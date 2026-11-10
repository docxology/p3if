"""Build the frozen inputs and independent intervention key for the reviewer pilot.

The source fixtures are pinned by byte digest. Each intervention edits a single
declared relationship. The expected answers follow the intervention specification
and the raw before/after record fields, without using the tools under comparison.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

from .interchange import FrameworkIdentity, canonical_bytes, load_interchange
from .interchange_native import migrate_legacy

_AXES = ("property_id", "process_id", "perspective_id")
_SCORES = ("strength", "confidence")
Object = dict[str, Any]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)


def _encode(document: Object, *, compact: bool = False) -> bytes:
    if compact:
        return canonical_bytes(load_interchange(_encode(document)))
    return (_pretty(document) + "\n").encode("utf-8")


def _baseline(fixtures: Path, domain: Object) -> Object:
    path = fixtures / domain["fixture"]
    source = path.read_bytes()
    if _sha(source) != domain["fixture_sha256"]:
        raise ValueError(f"The shipped fixture differs from the frozen source: {path}")
    model = migrate_legacy(source, FrameworkIdentity(**domain["framework"]))
    baseline: Object = json.loads(canonical_bytes(model))
    return baseline


def _score(record: Object, key: str) -> str:
    if key not in record:
        return "omitted"
    value = record[key]
    if value is None:
        return "explicit_null"
    return "reported_zero" if value == 0 else "reported_nonzero"


def _side(record: Optional[Object]) -> Optional[Object]:
    if record is None:
        return None
    return {
        "endpoints": [record.get(axis) for axis in _AXES],
        "scores": {key: _score(record, key) for key in _SCORES},
    }


def _citation(data: bytes, document: Object, record: Optional[Object]) -> Optional[Object]:
    if record is None:
        return None
    index = next(i for i, row in enumerate(document["relationships"]) if row["id"] == record["id"])
    fragment = _pretty(record).replace("\n", "\n    ")
    text = data.decode("utf-8")
    if text.count(fragment) != 1 or json.loads(fragment) != document["relationships"][index]:
        raise ValueError("The evidence relationship does not have a unique exact source span.")
    start = text.index(fragment)
    raw = fragment.encode("utf-8")
    start_byte = len(text[:start].encode("utf-8"))
    return {
        "source_sha256": _sha(data),
        "pointer": f"/relationships/{index}",
        "start_char": start,
        "end_char": start + len(fragment),
        "start_byte": start_byte,
        "end_byte": start_byte + len(raw),
        "quote_sha256": _sha(raw),
    }


def _apply(document: Object, intervention: Object) -> tuple[Optional[Object], Optional[Object]]:
    operation = intervention["change"]
    identity = intervention["id"]
    rows = document["relationships"]
    earlier = next((row for row in rows if row["id"] == identity), None)
    if operation == "added":
        later = intervention["set"]
        if (
            earlier is not None
            or later["id"] != identity
            or any(all(row.get(key) == later.get(key) for key in _AXES) for row in rows)
        ):
            raise ValueError(f"The added relationship would reuse an ID or coordinate: {identity}")
        rows.append(later)
        rows.sort(key=lambda row: row["id"])
        return None, later
    if earlier is None:
        raise ValueError(f"The frozen relationship is missing: {identity}")
    index = rows.index(earlier)
    if operation == "removed":
        del rows[index]
        return earlier, None
    if operation != "modified":
        raise ValueError(f"Unknown relationship operation: {operation}")
    set_fields = intervention["set"]
    omitted = intervention["omit"]
    if any(key not in earlier or key in set_fields for key in omitted) or any(
        key in earlier and earlier[key] == value for key, value in set_fields.items()
    ):
        raise ValueError(f"The frozen intervention contains a no-op field: {identity}")
    later = {key: value for key, value in earlier.items() if key not in omitted}
    later.update(set_fields)
    rows[index] = later
    return earlier, later


def _case(before: Object, case: Object) -> tuple[bytes, bytes, Object]:
    after = deepcopy(before)
    before_bytes = _encode(before)
    scenario = case["intervention"]
    expected: Object = {"case_id": case["case_id"], "classification": scenario, "events": []}
    earlier = later = None
    if scenario in {"identical_bytes", "encoding_only"}:
        after_bytes = (
            before_bytes if scenario == "identical_bytes" else _encode(after, compact=True)
        )
        if scenario == "encoding_only" and after_bytes == before_bytes:
            raise ValueError("The encoding control needs two different byte streams.")
    else:
        intervention = case["relationship"]
        earlier, later = _apply(after, intervention)
        after_bytes = _encode(after)
        _ = load_interchange(after_bytes)
        operation = intervention["change"]
        fields = (
            sorted([*intervention["set"], *intervention["omit"]]) if operation == "modified" else []
        )
        expected.update(
            classification="declared_change",
            events=[
                {
                    "id": intervention["id"],
                    "change": operation,
                    "fields": fields,
                    "before": _side(earlier),
                    "after": _side(later),
                }
            ],
        )
    return (
        before_bytes,
        after_bytes,
        {
            "case_id": case["case_id"],
            "domain": case["domain"],
            "intervention": scenario,
            "before_sha256": _sha(before_bytes),
            "after_sha256": _sha(after_bytes),
            "expected": expected,
            "citations": {
                "before": _citation(before_bytes, before, earlier),
                "after": _citation(after_bytes, after, later),
            },
        },
    )


def build_cases(fixtures: Path, specification: Path, output_dir: Path) -> None:
    """Generate case snapshots and a frozen answer and provenance manifest.

    Args:
        fixtures: Directory containing the shipped domain fixtures.
        specification: The preregistered JSON intervention specifications.
        output_dir: New output directory to create.

    Raises:
        ValueError: A pinned fixture, intervention, or panel allocation drifted.
        OSError: An input could not be read or the outputs could not be created.
    """
    spec_bytes = specification.read_bytes()
    spec = json.loads(spec_bytes)
    if spec["schema_version"] != "p3if.reviewer-case-spec.v1":
        raise ValueError("Unknown case specification version.")
    baselines = {name: _baseline(fixtures, domain) for name, domain in spec["domains"].items()}
    ids = [case["case_id"] for case in spec["cases"]]
    allocated = [identity for panel in spec["panels"].values() for identity in panel]
    if len(set(ids)) != len(ids) or sorted(ids) != sorted(allocated):
        raise ValueError("Each case must occur in exactly one panel.")
    cases = [_case(baselines[case["domain"]], case) for case in spec["cases"]]
    manifest = {
        "schema_version": "p3if.reviewer-case-manifest.v1",
        "specification_sha256": _sha(spec_bytes),
        "domains": spec["domains"],
        "panels": spec["panels"],
        "cases": [row for _, _, row in cases],
    }
    output_dir.mkdir()
    for before, after, row in cases:
        folder = output_dir / row["case_id"]
        folder.mkdir()
        (folder / "before.json").write_bytes(before)
        (folder / "after.json").write_bytes(after)
    (output_dir / "case-manifest.json").write_bytes((_pretty(manifest) + "\n").encode("utf-8"))
