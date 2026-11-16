"""Prepare condition-masked packets for the registered held-out reviewer comparison.

Each assignment includes the same original snapshots and name lookup in both
workflows. A coordinator-only manifest binds every delivered byte and discloses
the assignments. Deliver only one session folder to each reviewer.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

Object = dict[str, Any]

PACKET_SCHEMA = "p3if.held-out-reviewer-packets.v1"
CASE_IDS = tuple(f"H{number:02d}" for number in range(1, 17))
SESSIONS = ("S1", "S2", "S3", "S4")
_CASE_SCHEMA = "p3if.held-out-case-manifest.v1"
_SIDES = ("before", "after")
_COLLECTIONS = {
    "property": "properties",
    "process": "processes",
    "perspective": "perspectives",
    "relationship": "relationships",
}
_PANELS = {
    "A": ("H01", "H10", "H04", "H15"),
    "B": ("H03", "H13", "H06", "H16"),
    "C": ("H09", "H02", "H12", "H07"),
    "D": ("H11", "H05", "H14", "H08"),
}
_DESIGN = {
    "S1": (("A", "p3if"), ("B", "diff")),
    "S2": (("C", "diff"), ("D", "p3if")),
    "S3": (("A", "diff"), ("B", "p3if")),
    "S4": (("C", "p3if"), ("D", "diff")),
}
_INSTRUCTIONS = """# Snapshot review

Work through `schedule.json` in order. For each case, inspect `report.json` and use
`before.json`, `after.json`, and `lookup.json` to verify individual details. The
comparison runs from before to after. The lookup gives names separately for the
two sides. Under `source_sha256` the digests identify exact input bytes.
A report may separately describe canonical snapshot identity or include field
values. Where a field value is wrapped as `{"value": null}`, the source declares
null. An empty wrapper indicates an omitted field.

Use only the files in this session folder. Do not read the project repository,
study documentation, other sessions, or the answer key. Do not build another
full diff or audit, call a comparison tool, or delegate the review. You may
filter the supplied report, lookup, or a single original snapshot by record ID
to verify details. Use your own reading to compose the answers. Give one answer
per case as a JSON array in the scheduled order.

Each answer has keys `case_id`, `classification`, and `events`. Use
`identical_bytes` for exact matches, `encoding_only` for different bytes with
unchanged declarations, and `declared_change` when declarations differ.
Reordering the top-level named record collections does not change a declaration.
For the first two classifications use `events: []`.

Give every changed stable identity once per kind. Each event has keys `kind`,
`id`, `change`, `fields`, `rewired`, `before`, and `after`. Kinds are
`framework`, `property`, `process`, `perspective`, and `relationship`. Operations
are `added`, `removed`, and `modified`. Use `fields: []` for additions and
removals. Otherwise list changed top-level fields, including transitions between
an omitted field and a declared null. Changes in type or order inside a nested
field count as a change to that field.

For a present side return an object with `coordinate` and `scores`. The
coordinate array orders property, process, then perspective stable IDs. A
relationship uses its endpoints and has null where an endpoint is missing.
A property, process, or perspective uses its own ID in its axis and nulls in
the others. A framework uses three nulls. The entire side is null for an
absent record. Use `rewired: true` only for a retained relationship whose
endpoint coordinate actually changes.

Relationship scores are an object with keys `strength` and `confidence`. For
each score report `omitted`, `explicit_null`, `reported_zero`, or
`reported_nonzero`, according to the original declaration on that side.
For any other present record, use `scores: null`.
"""


def assignment_rows() -> list[Object]:
    """Return the four fixed session schedules in delivery order."""
    return [
        {
            "session": session,
            "period": period,
            "case_id": case_id,
            "condition": condition,
            "folder": f"{session}/{period}/{case_id}",
        }
        for session in SESSIONS
        for period, (panel, condition) in enumerate(_DESIGN[session], start=1)
        for case_id in _PANELS[panel]
    ]


def _digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _write(path: Path, data: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        )
        stream.write("\n")


def _object_members(pairs: list[tuple[str, Any]]) -> Object:
    members = dict(pairs)
    if len(members) != len(pairs):
        raise ValueError("Duplicate JSON object member.")
    return members


def _reject_constant(token: str) -> None:
    raise ValueError(f"Unexpected non-JSON numeric constant: {token}")


def _object(raw: bytes) -> Object:
    value = json.loads(raw, object_pairs_hook=_object_members, parse_constant=_reject_constant)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object.")
    return value


def _declarations(document: Object) -> dict[tuple[str, str], Object]:
    framework = document["framework"]
    records = {("framework", framework["id"]): framework}
    for kind, collection in _COLLECTIONS.items():
        for record in document[collection]:
            key = (kind, record["id"])
            if key in records:
                raise ValueError(f"Duplicate {kind} stable ID.")
            records[key] = record
    return records


def _value_key(value: Any) -> str:
    # Preserve primitive types and array order while ignoring object key order.
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _member(record: Object, field: str) -> Object:
    return {"value": record[field]} if field in record else {}


def _stable_id_changes(before: Object, after: Object) -> list[Object]:
    left, right = _declarations(before), _declarations(after)
    events: list[Object] = []
    for key in sorted(left.keys() | right.keys()):
        kind, identity = key
        event: Object = {"kind": kind, "id": identity}
        if key not in left:
            events.append({**event, "change": "added", "after": right[key]})
        elif key not in right:
            events.append({**event, "change": "removed", "before": left[key]})
        else:
            earlier, later = left[key], right[key]
            fields = {}
            for field in sorted(earlier.keys() | later.keys()):
                first, second = _member(earlier, field), _member(later, field)
                if _value_key(first) != _value_key(second):
                    fields[field] = {"before": first, "after": second}
            if fields:
                events.append({**event, "change": "modified", "fields": fields})
    return events


def stable_id_diff(before: bytes, after: bytes) -> Object:
    """Compare wire declarations by stable ID using Python's standard library.

    Args:
        before: Exact bytes of the first frozen interchange snapshot.
        after: Exact bytes of the second frozen interchange snapshot.

    Returns:
        Transport digests, case classification, and field-level changed records.
        Collection ordering and JSON escape spelling do not affect declarations.
    """
    earlier, later = _object(before), _object(after)
    events = _stable_id_changes(earlier, later)
    classification = "declared_change" if events else "encoding_only"
    if before == after:
        classification = "identical_bytes"
    return {
        "source_sha256": {"before": _digest(before), "after": _digest(after)},
        "summary": {"classification": classification},
        "changes": {"events": events},
    }


def _audited_report(before: bytes, after: bytes) -> Object:
    # Keep the standard-library comparator independent of the audited workflow.
    from .interchange import load_interchange
    from .interchange_audit import audit_interchange
    from .interchange_transition import transition_interchange

    summary = audit_interchange(before, after).model_dump(mode="json", exclude={"method"})
    changes = transition_interchange(load_interchange(before), load_interchange(after)).model_dump(
        mode="json"
    )
    changes["canonical_sha256"] = {
        "before": changes.pop("before_sha256"),
        "after": changes.pop("after_sha256"),
    }
    return {
        "source_sha256": {"before": _digest(before), "after": _digest(after)},
        "summary": summary,
        "changes": changes,
    }


def _name_lookup(before: bytes, after: bytes) -> Object:
    return {
        side: {
            kind: {row["id"]: row["name"] for row in document[collection]}
            for kind, collection in _COLLECTIONS.items()
            if kind != "relationship"
        }
        for side, document in zip(_SIDES, (_object(before), _object(after)))
    }


def _source_pairs(case_dir: Path, frozen_raw: bytes) -> dict[str, tuple[bytes, bytes]]:
    if (case_dir / "case-manifest.json").read_bytes() != frozen_raw:
        raise ValueError("Generated case manifest differs from the frozen manifest.")
    manifest = _object(frozen_raw)
    if manifest["schema_version"] != _CASE_SCHEMA:
        raise ValueError("Unsupported frozen case manifest.")
    cases = manifest["cases"]
    if tuple(row["case_id"] for row in cases) != CASE_IDS:
        raise ValueError("Unexpected frozen case inventory.")
    pairs = {}
    for row in cases:
        case_id = row["case_id"]
        before = (case_dir / case_id / "before.json").read_bytes()
        after = (case_dir / case_id / "after.json").read_bytes()
        if (_digest(before), _digest(after)) != (row["before_sha256"], row["after_sha256"]):
            raise ValueError(f"Exact source digest mismatch for {case_id}.")
        pairs[case_id] = (before, after)
    return pairs


def prepare_packets(case_dir: Path, frozen_manifest: Path, output_dir: Path) -> None:
    """Generate four isolated reviewer folders and their coordinator manifest.

    Args:
        case_dir: Frozen case generator output directory.
        frozen_manifest: Checked public held-out case manifest.
        output_dir: New directory for packets and their complete digest inventory.

    Raises:
        ValueError: The case inventory or an exact source digest differs.
        OSError: An input could not be read or the output could not be created.
    """
    frozen_raw = frozen_manifest.read_bytes()
    pairs = _source_pairs(case_dir, frozen_raw)
    assignments = assignment_rows()
    output_dir.mkdir()
    for session in SESSIONS:
        session_root = output_dir / session
        session_root.mkdir()
        (session_root / "instructions.md").write_bytes(_INSTRUCTIONS.encode("utf-8"))
        schedule = []
        for row in assignments:
            if row["session"] != session:
                continue
            case_id = row["case_id"]
            before, after = pairs[case_id]
            destination = output_dir / row["folder"]
            destination.mkdir(parents=True)
            for side, raw in zip(_SIDES, (before, after)):
                (destination / f"{side}.json").write_bytes(raw)
            _write(destination / "lookup.json", _name_lookup(before, after))
            report = _audited_report if row["condition"] == "p3if" else stable_id_diff
            _write(destination / "report.json", report(before, after))
            schedule.append(
                {
                    "period": row["period"],
                    "case_id": case_id,
                    "folder": destination.relative_to(session_root).as_posix(),
                }
            )
        _write(session_root / "schedule.json", schedule)

    files = {
        path.relative_to(output_dir).as_posix(): _digest(path.read_bytes())
        for path in sorted(output_dir.rglob("*"))
        if path.is_file()
    }
    _write(
        output_dir / "packet-manifest.json",
        {
            "schema_version": PACKET_SCHEMA,
            "case_manifest_sha256": _digest(frozen_raw),
            "assignments": assignments,
            "files": files,
        },
    )
