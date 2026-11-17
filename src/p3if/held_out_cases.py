"""Generate the registered P3IF interchange conformance corpus.

Snapshot edits and the expected event set come from the intervention spec.
The oracle reads only the declared edits and the raw records they affect.
The generator uses interchange loading to check the resulting snapshots and
uses neither the transition evaluator nor its comparison helper.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .interchange import load_interchange
from .reviewer_study_cases import _baseline, _score, _sha

SPEC_SCHEMA = "p3if.held-out-case-spec.v1"
MANIFEST_SCHEMA = "p3if.held-out-case-manifest.v1"
_AXIS_KEYS = ("property_id", "process_id", "perspective_id")
_AXIS_KINDS = ("property", "process", "perspective")
_COLLECTIONS = {
    "property": "properties",
    "process": "processes",
    "perspective": "perspectives",
    "relationship": "relationships",
}
_CASE_ID = re.compile(r"H[0-9]{2}\Z")
Object = dict[str, Any]


def _json(value: Any, *, ascii_only: bool = False) -> str:
    return json.dumps(value, ensure_ascii=ascii_only, sort_keys=True, indent=2, allow_nan=False)


def _encode(document: Object, *, ascii_only: bool = False) -> bytes:
    return (_json(document, ascii_only=ascii_only) + "\n").encode("utf-8")


def _record(document: Object, kind: str, identity: str) -> tuple[int | None, Object | None]:
    if kind == "framework":
        framework = document["framework"]
        if framework["id"] != identity:
            raise ValueError(f"Unexpected framework identity in edit: {identity}")
        return None, framework
    rows = document[_COLLECTIONS[kind]]
    return next(
        ((index, row) for index, row in enumerate(rows) if row["id"] == identity), (None, None)
    )


def _modified(earlier: Object, edit: Object) -> Object:
    added = edit.get("set", {})
    removed = edit.get("omit", [])
    if (
        not (added or removed)
        or "id" in added
        or "id" in removed
        or len(set(removed)) != len(removed)
        or any(key not in earlier or key in added for key in removed)
        or any(
            key in earlier and _json(earlier[key]) == _json(value) for key, value in added.items()
        )
    ):
        raise ValueError(f"Invalid or ineffective fields in edit: {edit['id']}")
    result = {key: value for key, value in earlier.items() if key not in removed}
    result.update(added)
    return result


def _apply(document: Object, edit: Object) -> None:
    kind, identity, operation = edit["kind"], edit["id"], edit["change"]
    index, earlier = _record(document, kind, identity)
    if operation == "added" and earlier is None:
        later = edit["set"]
        if later["id"] != identity or edit.get("omit"):
            raise ValueError(f"Invalid added record: {identity}")
        document[_COLLECTIONS[kind]].append(later)
    elif operation == "removed" and index is not None:
        if edit.get("set") or edit.get("omit"):
            raise ValueError(f"A removed record cannot also declare field changes: {identity}")
        del document[_COLLECTIONS[kind]][index]
    elif operation == "modified" and earlier is not None:
        later = _modified(earlier, edit)
        if kind == "framework":
            document["framework"] = later
        else:
            document[_COLLECTIONS[kind]][index] = later
    else:
        raise ValueError(f"Invalid {operation} edit for {kind} {identity}")


def _apply_edits(document: Object, edits: list[Object]) -> None:
    keys = {(edit["kind"], edit["id"]) for edit in edits}
    if len(keys) != len(edits):
        raise ValueError("Edit each record at most once per specification phase.")
    for edit in edits:
        _apply(document, edit)


def _side(kind: str, row: Object | None) -> Object | None:
    if row is None:
        return None
    if kind == "relationship":
        return {
            "coordinate": [row.get(key) for key in _AXIS_KEYS],
            "scores": {key: _score(row, key) for key in ("strength", "confidence")},
        }
    return {
        "coordinate": [row["id"] if kind == axis else None for axis in _AXIS_KINDS],
        "scores": None,
    }


def _event(edit: Object, earlier: Object | None, later: Object | None) -> Object:
    kind, operation = edit["kind"], edit["change"]
    left, right = _side(kind, earlier), _side(kind, later)
    fields = (
        sorted([*edit.get("set", {}), *edit.get("omit", [])]) if operation == "modified" else []
    )
    return {
        "kind": kind,
        "id": edit["id"],
        "change": operation,
        "fields": fields,
        "rewired": (
            kind == "relationship"
            and left is not None
            and right is not None
            and left["coordinate"] != right["coordinate"]
        ),
        "before": left,
        "after": right,
    }


def _citation(data: bytes, kind: str, found: tuple[int | None, Object | None]) -> Object | None:
    index, record = found
    if record is None:
        return None
    # All records cited by this corpus use this fixed pretty encoding. Compute
    # coordinates against that exact transport after applying array ordering.
    indent = "  " if kind == "framework" else "    "
    fragment = _json(record).replace("\n", "\n" + indent)
    text = data.decode("utf-8")
    if text.count(fragment) != 1:
        raise ValueError(f"Ambiguous source span for {kind} {record['id']}")
    start = text.index(fragment)
    start_byte = len(text[:start].encode("utf-8"))
    raw = fragment.encode("utf-8")
    return {
        "source_sha256": _sha(data),
        "pointer": "/framework" if kind == "framework" else f"/{_COLLECTIONS[kind]}/{index}",
        "start_char": start,
        "end_char": start + len(fragment),
        "start_byte": start_byte,
        "end_byte": start_byte + len(raw),
        "quote_sha256": _sha(raw),
    }


def _case(baseline: Object, context: str, spec: Object) -> tuple[bytes, bytes, Object]:
    before = deepcopy(baseline)
    if "description" in before["framework"]:
        raise ValueError("The case context would replace a fixture declaration.")
    before["framework"]["description"] = context
    _apply_edits(before, spec["seed_edits"])
    after = deepcopy(before)
    edits = spec["edits"]
    _apply_edits(after, edits)
    encoding = spec["after_encoding"]
    reversal = encoding["reverse"]
    if len(set(reversal)) != len(reversal) or any(
        key not in _COLLECTIONS.values() for key in reversal
    ):
        raise ValueError("Only distinct top-level record collections may be reversed.")
    for collection in reversal:
        after[collection].reverse()
    if edits and encoding["ascii"]:
        raise ValueError("The cited snapshots must use the corpus's UTF-8 encoding.")
    before_raw = _encode(before)
    after_raw = _encode(after, ascii_only=encoding["ascii"])
    if before_raw == after_raw:
        raise ValueError(
            "A held-out pair must have a declared intervention or a different encoding."
        )
    _ = load_interchange(before_raw), load_interchange(after_raw)
    events, citations = [], []
    for edit in sorted(edits, key=lambda item: (item["kind"], item["id"])):
        kind, identity = edit["kind"], edit["id"]
        earlier, later = _record(before, kind, identity), _record(after, kind, identity)
        events.append(_event(edit, earlier[1], later[1]))
        citations.append(
            {
                "kind": kind,
                "id": identity,
                "before": _citation(before_raw, kind, earlier),
                "after": _citation(after_raw, kind, later),
            }
        )
    return (
        before_raw,
        after_raw,
        {
            "case_id": spec["case_id"],
            "domain": spec["domain"],
            "intervention": spec["intervention"],
            "before_sha256": _sha(before_raw),
            "after_sha256": _sha(after_raw),
            "expected": {
                "case_id": spec["case_id"],
                "classification": "declared_change" if edits else "encoding_only",
                "events": events,
            },
            "citations": citations,
        },
    )


def build_cases(fixtures: Path, specification: Path, output_dir: Path) -> None:
    """Build exact before/after inputs with their declared event and span keys.

    Args:
        fixtures: Directory containing the shipped legacy domain fixtures.
        specification: Registered case intervention specification.
        output_dir: New output directory to create.

    Raises:
        ValueError: The spec or a pinned fixture fails validation.
        OSError: An input cannot be read or the outputs cannot be written.
    """
    raw_spec = specification.read_bytes()
    spec = json.loads(raw_spec)
    if spec["schema_version"] != SPEC_SCHEMA:
        raise ValueError("Unknown held-out case specification version.")
    baselines = {name: _baseline(fixtures, domain) for name, domain in spec["domains"].items()}
    ids = [case["case_id"] for case in spec["cases"]]
    if len(set(ids)) != len(ids) or any(not _CASE_ID.fullmatch(identity) for identity in ids):
        raise ValueError("Held-out case IDs must be distinct and match H00–H99.")
    cases = [
        _case(
            baselines[case["domain"]],
            spec["context_template"].format(case_id=case["case_id"]),
            case,
        )
        for case in spec["cases"]
    ]
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "specification_sha256": _sha(raw_spec),
        "domains": spec["domains"],
        "cases": [row for _, _, row in cases],
    }
    output_dir.mkdir()
    for before, after, row in cases:
        folder = output_dir / row["case_id"]
        folder.mkdir()
        (folder / "before.json").write_bytes(before)
        (folder / "after.json").write_bytes(after)
    (output_dir / "case-manifest.json").write_bytes(_encode(manifest))
