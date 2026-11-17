"""Build the frozen snapshot pairs and exact citation key from pinned fixtures."""

from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from .held_out_cases import _COLLECTIONS, _apply_edits, _encode, _event, _record
from .held_out_verify import _source_values
from .interchange import load_interchange
from .reviewer_study_cases import _baseline, _sha

SPEC_SCHEMA = "p3if.citation-case-spec.v1"
NAVIGATION_SPEC_SCHEMA = "p3if.navigation-case-spec.v1"
MANIFEST_SCHEMA = "p3if.citation-case-manifest.v1"
_CASE_PREFIXES = {SPEC_SCHEMA: "C", NAVIGATION_SPEC_SCHEMA: "A"}
_KINDS = {"framework", *_COLLECTIONS}
_ENCODINGS = {"pretty", "compact", "ascii", "crlf"}
Object = dict[str, Any]


def _transport(document: Object, encoding: str) -> bytes:
    if encoding not in _ENCODINGS:
        raise ValueError(f"Unsupported citation case encoding: {encoding}")
    if encoding == "compact":
        return (
            json.dumps(
                document, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
            )
            + "\n"
        ).encode("utf-8")
    raw = _encode(document, ascii_only=encoding == "ascii")
    return raw.replace(b"\n", b"\r\n") if encoding == "crlf" else raw


def _span(
    document: Object,
    text: str,
    spans: dict[str, tuple[int, int, str]],
    source_sha256: str,
    kind: str,
    identity: str,
) -> Object | None:
    index, row = _record(document, kind, identity)
    if row is None:
        return None
    pointer = "/framework" if kind == "framework" else f"/{_COLLECTIONS[kind]}/{index}"
    start, end, located_identity = spans[pointer]
    if located_identity != identity:
        raise ValueError(f"The original source token at {pointer} has a different identity.")
    quoted = text[start:end].encode("utf-8")
    start_byte = len(text[:start].encode("utf-8"))
    return {
        "source_sha256": source_sha256,
        "pointer": pointer,
        "start_char": start,
        "end_char": end,
        "start_byte": start_byte,
        "end_byte": start_byte + len(quoted),
        "quote_sha256": _sha(quoted),
    }


def _questions(spec: Object) -> list[Object]:
    questions: list[Object] = spec["questions"]
    if not questions or any(
        set(item) != {"kind", "id"} or item["kind"] not in _KINDS for item in questions
    ):
        raise ValueError("Each citation case needs at least one stable identity question.")
    keys = {(item["kind"], item["id"]) for item in questions}
    if len(questions) != len(keys):
        raise ValueError("A citation case cannot repeat a question.")
    return questions


def _case(baseline: Object, context: str, spec: Object) -> tuple[bytes, bytes, Object]:
    before = deepcopy(baseline)
    if "description" in before["framework"]:
        raise ValueError("The citation context would replace a fixture declaration.")
    before["framework"]["description"] = context
    _apply_edits(before, spec["seed_edits"])
    after = deepcopy(before)
    edits = spec["edits"]
    _apply_edits(after, edits)
    reverse = spec["reverse_after"]
    if len(set(reverse)) != len(reverse) or any(
        key not in _COLLECTIONS.values() for key in reverse
    ):
        raise ValueError("Only distinct record collections may be reversed.")
    for collection in reverse:
        after[collection].reverse()

    before_raw = _transport(before, spec["before_encoding"])
    after_raw = _transport(after, spec["after_encoding"])
    _ = load_interchange(before_raw), load_interchange(after_raw)
    classification = "declared_change" if edits else "encoding_only"
    if before_raw == after_raw:
        if edits:
            raise ValueError("A declared intervention produced identical source bytes.")
        classification = "identical_bytes"

    events = [
        _event(
            edit,
            _record(before, edit["kind"], edit["id"])[1],
            _record(after, edit["kind"], edit["id"])[1],
        )
        for edit in sorted(edits, key=lambda item: (item["kind"], item["id"]))
    ]
    before_text, after_text = before_raw.decode("utf-8"), after_raw.decode("utf-8")
    before_spans, after_spans = _source_values(before_text), _source_values(after_text)
    before_hash, after_hash = _sha(before_raw), _sha(after_raw)
    questions = _questions(spec)
    citations = []
    for question in questions:
        kind, identity = question["kind"], question["id"]
        left = _span(before, before_text, before_spans, before_hash, kind, identity)
        right = _span(after, after_text, after_spans, after_hash, kind, identity)
        if left is None and right is None:
            raise ValueError(f"Citation question {kind} {identity} is absent from both snapshots.")
        citations.append({**question, "before": left, "after": right})

    case_id = spec["case_id"]
    return (
        before_raw,
        after_raw,
        {
            "case_id": case_id,
            "domain": spec["domain"],
            "intervention": spec["intervention"],
            "before_sha256": before_hash,
            "after_sha256": after_hash,
            "questions": questions,
            "citations": citations,
            "expected": {"case_id": case_id, "classification": classification, "events": events},
        },
    )


def build_cases(fixtures: Path, specification: Path, output_dir: Path) -> None:
    """Write original before/after transports and their exact frozen citation manifest.

    The lexical span scanner reads original JSON tokens independently of both
    analytical arms and resolves only declarations at their actual pointers.

    Args:
        fixtures: Directory containing the shipped legacy domain fixtures.
        specification: Citation study or source navigation ablation specification.
        output_dir: New directory for the original transports and manifest.

    Raises:
        ValueError: The specification or a pinned fixture fails validation.
        OSError: An input cannot be read or an output cannot be written.
    """
    raw_spec = specification.read_bytes()
    spec = json.loads(raw_spec)
    prefix = _CASE_PREFIXES.get(spec["schema_version"])
    if prefix is None:
        raise ValueError("Unknown citation case specification version.")
    identities = [f"{prefix}{index:02d}" for index in range(1, 17)]
    rows = spec["cases"]
    if [case["case_id"] for case in rows] != identities or Counter(
        case["domain"] for case in rows
    ) != {"ScienceResearch": 8, "MathEducation": 8}:
        raise ValueError("The citation corpus needs all sixteen ordered and balanced case IDs.")
    baselines = {name: _baseline(fixtures, domain) for name, domain in spec["domains"].items()}
    cases = [
        _case(
            baselines[case["domain"]],
            spec["context_template"].format(case_id=case["case_id"]),
            case,
        )
        for case in rows
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
