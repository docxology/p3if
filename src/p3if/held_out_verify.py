"""Verify frozen held-out cases through the P3IF audit and transition APIs.

The comparison checks ordered and reversed transitions against a declarative
key. Citation verification reads the original transport, before canonicalization.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any

from .interchange import Interchange, InterchangeRelationship, load_interchange
from .interchange_audit import audit_interchange
from .interchange_transition import Coordinate, transition_interchange

_JSON = dict[str, Any]
_KINDS = {
    "framework": "framework",
    "property": "properties",
    "process": "processes",
    "perspective": "perspectives",
    "relationship": "relationships",
}
_WHITESPACE = re.compile(r"[ \t\r\n]*")
_DECODER = json.JSONDecoder()


def _digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _position(text: str, index: int) -> int:
    match = _WHITESPACE.match(text, index)
    assert match is not None
    return match.end()


def _source_values(text: str) -> dict[str, tuple[int, int, str]]:
    """Locate top-level framework and array item values in a validated snapshot."""
    index = _position(text, 0) + 1
    values: dict[str, tuple[int, int, str]] = {}
    while text[index := _position(text, index)] != "}":
        name, key_end = _DECODER.raw_decode(text, index)
        start = _position(text, _position(text, key_end) + 1)
        if name in _KINDS.values() and name != "framework":
            index = _position(text, start + 1)
            ordinal = 0
            while text[index] != "]":
                record, end = _DECODER.raw_decode(text, index)
                values[f"/{name}/{ordinal}"] = (index, end, record["id"])
                index = _position(text, end)
                if text[index] == ",":
                    index = _position(text, index + 1)
                ordinal += 1
            end = index + 1
        else:
            record, end = _DECODER.raw_decode(text, start)
            if name == "framework":
                values["/framework"] = (start, end, record["id"])
        index = _position(text, end)
        if text[index] == ",":
            index += 1
    return values


def _citation_ok(
    span: _JSON,
    key: tuple[str, str],
    raw: bytes,
    text: str,
    values: dict[str, tuple[int, int, str]],
) -> bool:
    pointer = span["pointer"]
    collection = _KINDS[key[0]]
    located = values.get(pointer)
    if located is None or pointer.split("/")[1] != collection or located[2] != key[1]:
        return False
    start, end, _ = located
    start_byte = len(text[:start].encode())
    quote = text[start:end].encode()
    end_byte = start_byte + len(quote)
    return (
        span["source_sha256"] == _digest(raw)
        and (span["start_char"], span["end_char"]) == (start, end)
        and (span["start_byte"], span["end_byte"]) == (start_byte, end_byte)
        and raw[start_byte:end_byte] == quote
        and span["quote_sha256"] == _digest(quote)
    )


def _score_state(record: InterchangeRelationship, name: str) -> str:
    if name not in record.model_fields_set:
        return "omitted"
    value = getattr(record, name)
    if value is None:
        return "explicit_null"
    return "reported_zero" if value == 0 else "reported_nonzero"


def _side(
    coordinate: Coordinate | None, relationship: InterchangeRelationship | None
) -> _JSON | None:
    if coordinate is None:
        return None
    return {
        "coordinate": list(coordinate),
        "scores": (
            {name: _score_state(relationship, name) for name in ("strength", "confidence")}
            if relationship is not None
            else None
        ),
    }


def _events(before: Interchange, after: Interchange) -> tuple[_JSON, list[_JSON]]:
    transition = transition_interchange(before, after)
    first, second = ({row.id: row for row in side.relationships} for side in (before, after))
    rows = []
    for event in transition.events:
        relationship = event.kind == "relationship"
        rows.append(
            {
                "kind": event.kind,
                "id": event.id,
                "change": event.change,
                "fields": list(event.fields),
                "rewired": event.rewired,
                "before": _side(event.before, first.get(event.id) if relationship else None),
                "after": _side(event.after, second.get(event.id) if relationship else None),
            }
        )
    return transition.model_dump(mode="json", exclude={"events"}), rows


def _reverse(event: _JSON) -> _JSON:
    return {
        **event,
        "before": event["after"],
        "after": event["before"],
        "change": {"added": "removed", "removed": "added", "modified": "modified"}[event["change"]],
    }


def _event_key(event: _JSON) -> tuple[str, str]:
    return str(event["kind"]), str(event["id"])


def _counts(events: list[_JSON], kind: str) -> _JSON:
    selected = [event for event in events if event["kind"] == kind]
    counts = Counter(event["change"] for event in selected)
    return {
        "kind": kind,
        **{change: counts[change] for change in ("added", "removed", "modified")},
        "rewired": sum(event["rewired"] for event in selected),
    }


def _evidence(case: _JSON, sources: tuple[bytes, bytes]) -> tuple[bool, int, int]:
    expected = {_event_key(row): row for row in case["expected"]["events"]}
    rows = {_event_key(row): row for row in case["citations"]}
    if rows.keys() != expected.keys() or len(rows) != len(case["citations"]):
        return False, 0, 0
    passed = True
    present, absent = 0, 0
    for name, raw in zip(("before", "after"), sources):
        text = raw.decode()
        values = _source_values(text)
        for key, citation in rows.items():
            span = citation[name]
            if expected[key][name] is None:
                absent += 1
                passed &= span is None
            else:
                present += 1
                passed &= span is not None and _citation_ok(span, key, raw, text, values)
    return passed, present, absent


def _verify_case(case: _JSON, sources: tuple[bytes, bytes]) -> _JSON:
    first, second = sources
    before, after = load_interchange(first), load_interchange(second)
    audit = audit_interchange(first, second)
    transition, events = _events(before, after)
    reverse, reverse_events = _events(after, before)
    expected = sorted(case["expected"]["events"], key=_event_key)
    axes = {
        axis: sorted({row.id for model in (before, after) for row in getattr(model, axis)})
        for axis in ("properties", "processes", "perspectives")
    }
    source_ok, present, absent = _evidence(case, sources)
    framework_fields: list[str] = next(
        (event["fields"] for event in expected if event["kind"] == "framework"), []
    )
    checks = {
        "framework_fields": list(audit.framework_fields) == framework_fields,
        "framework_identity": (
            audit.framework_id
            == transition["framework_id"]
            == reverse["framework_id"]
            == before.framework.id
            == after.framework.id
        ),
        "classification": audit.classification == case["expected"]["classification"],
        "source_hashes": (
            audit.before.source_sha256 == case["before_sha256"]
            and audit.after.source_sha256 == case["after_sha256"]
        ),
        "canonical_hashes": (
            transition["before_sha256"]
            == reverse["after_sha256"]
            == audit.before.analysis.semantic_sha256
            and transition["after_sha256"]
            == reverse["before_sha256"]
            == audit.after.analysis.semantic_sha256
        ),
        "axes": transition["axes"] == reverse["axes"] == axes,
        "audit_counts": (
            [item.model_dump() for item in audit.changes]
            == [_counts(expected, kind) for kind in _KINDS]
        ),
        "forward_events": sorted(events, key=_event_key) == expected,
        "reverse_events": sorted(reverse_events, key=_event_key)
        == [_reverse(event) for event in expected],
        "citation_spans": source_ok,
    }
    return {
        "case_id": case["case_id"],
        "domain": case["domain"],
        "intervention": case["intervention"],
        "classification": audit.classification,
        "events": len(events),
        "present_spans": present,
        "absent_sides": absent,
        "checks": checks,
        "passed": all(checks.values()),
    }


def verify_cases(case_dir: Path, registered_manifest: Path) -> _JSON:
    """Evaluate every case against its immutable registration.

    Args:
        case_dir: Generated input directory, including a copy of the manifest.
        registered_manifest: Frozen answer and source digest inventory.

    Returns:
        One deterministic receipt with all case outcomes and evidence counts.

    Raises:
        ValueError: A manifest, case identity, or exact source digest drifted.
    """
    frozen = registered_manifest.read_bytes()
    if frozen != (case_dir / "case-manifest.json").read_bytes():
        raise ValueError("Generated manifest differs from the registered manifest.")
    manifest = json.loads(frozen)
    cases = manifest["cases"]
    if manifest["schema_version"] != "p3if.held-out-case-manifest.v1" or [
        case["case_id"] for case in cases
    ] != [f"H{index:02d}" for index in range(1, 17)]:
        raise ValueError("Unexpected held-out case inventory.")
    inputs = []
    for case in cases:
        case_id = case["case_id"]
        first = (case_dir / case_id / "before.json").read_bytes()
        second = (case_dir / case_id / "after.json").read_bytes()
        if (_digest(first), _digest(second)) != (case["before_sha256"], case["after_sha256"]):
            raise ValueError(f"Exact source digest mismatch for {case_id}.")
        inputs.append((first, second))
    rows = [_verify_case(case, pair) for case, pair in zip(cases, inputs)]
    return {
        "schema_version": "p3if.held-out-conformance.v1",
        "manifest_sha256": _digest(frozen),
        "cases": rows,
        "passed": sum(row["passed"] for row in rows),
        "events": sum(row["events"] for row in rows),
        "present_spans": sum(row["present_spans"] for row in rows),
        "absent_sides": sum(row["absent_sides"] for row in rows),
    }
