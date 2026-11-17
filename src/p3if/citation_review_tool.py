"""Inspect and cite exact snapshot bytes in one masked reviewer packet.

The packet generator copies this standard-library-only module as `review.py`.
Every parsed operation logs its result and timings without recording snippets,
queries, or answer content. Submissions preserve the original stdin bytes.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, UTC
from hashlib import sha256
from pathlib import Path
from time import monotonic_ns
from typing import Any
import json
import os
import re
import sys

KINDS = {
    "framework": "framework",
    "property": "properties",
    "process": "processes",
    "perspective": "perspectives",
    "relationship": "relationships",
}
ACTION_SCHEMA = "p3if.citation-review-action.v1"
_SOURCE_SIDES = ("before", "after")
_OPEN_RESOURCES = (*_SOURCE_SIDES, "lookup", "report", "questions")
_DECODER = json.JSONDecoder()
_WHITESPACE = re.compile(r"[ \t\r\n]*")
_CASE_ID = re.compile(r"C[0-9]{2}\Z")


@dataclass(frozen=True)
class RecordSpan:
    """A direct declaration located in the original decoded snapshot."""

    kind: str
    identity: str
    name: str | None
    start: int
    end: int


def _skip(text: str, index: int) -> int:
    match = _WHITESPACE.match(text, index)
    assert match is not None
    return match.end()


def _span(kind: str, value: dict[str, Any], start: int, end: int) -> RecordSpan:
    return RecordSpan(kind, value["id"], value.get("name"), start, end)


def record_spans(text: str) -> dict[str, RecordSpan]:
    """Return pointers and codepoint spans for direct interchange declarations.

    Args:
        text: Exact decoded text of a valid interchange object.

    Returns:
        Framework and direct collection records indexed by JSON pointer.

    Raises:
        ValueError: The snapshot does not contain a valid top-level declaration.
    """
    collections = {name: kind for kind, name in KINDS.items() if kind != "framework"}
    first = _skip(text, 0)
    if text[first : first + 1] != "{":
        raise ValueError("Expected an interchange object.")
    index = _skip(text, first + 1)
    spans = {}
    while text[index] != "}":
        name, key_end = _DECODER.raw_decode(text, index)
        start = _skip(text, _skip(text, key_end) + 1)
        if name in collections:
            index = _skip(text, start + 1)
            ordinal = 0
            while text[index] != "]":
                record, end = _DECODER.raw_decode(text, index)
                spans[f"/{name}/{ordinal}"] = _span(collections[name], record, index, end)
                ordinal += 1
                index = _skip(text, end)
                if text[index] == ",":
                    index = _skip(text, index + 1)
            end = index + 1
        else:
            record, end = _DECODER.raw_decode(text, start)
            if name == "framework":
                spans["/framework"] = _span("framework", record, start, end)
        index = _skip(text, end)
        if text[index] == ",":
            index = _skip(text, index + 1)
    return spans


def _case_folder(root: Path, case_id: str) -> Path:
    if not _CASE_ID.fullmatch(case_id):
        raise ValueError("Use a case ID from your schedule.")
    schedule = json.loads((root / "schedule.json").read_bytes())
    entry = next((row for row in schedule if row["case_id"] == case_id), None)
    if entry is None or entry["period"] not in (1, 2):
        raise ValueError("Use a case ID from your schedule.")
    relative = f"{entry['period']}/{case_id}"
    if entry["folder"] != relative:
        raise ValueError("Use a case ID from your schedule.")
    folder = root / relative
    if folder.resolve() != folder:
        raise ValueError("The scheduled folder must be inside your packet.")
    return folder


def _packet_file(folder: Path, name: str) -> bytes:
    path = folder / name
    if path.resolve() != path:
        raise ValueError("Expected a file inside the packet.")
    return path.read_bytes()


def _json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def _matches_source(text: str, literal: str) -> list[dict[str, Any]]:
    if not literal:
        raise ValueError("A search requires nonempty literal text.")
    matches: list[dict[str, Any]] = []
    index = text.find(literal)
    while index != -1 and len(matches) < 20:
        left = max(0, index - 48)
        right = min(len(text), index + len(literal) + 48)
        matches.append({"match_char": index, "context": text[left:right]})
        index = text.find(literal, index + len(literal))
    return matches


def _members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("The submission contains duplicate JSON member names.")
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("Use only standard JSON values in a submission.")


def _submit(case_id: str, output: Path) -> tuple[bytes, str]:
    raw = sys.stdin.buffer.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("The one-case submission exceeds 1 MB.")
    value = json.loads(raw, object_pairs_hook=_members, parse_constant=_reject_constant)
    if (
        not isinstance(value, dict)
        or set(value) != {"case_id", "citations"}
        or value["case_id"] != case_id
        or not isinstance(value["citations"], list)
    ):
        raise ValueError("Submit one object with the selected case_id and a citations array.")
    with (output / f"{case_id}.json").open("xb") as stream:
        stream.write(raw)
    digest = sha256(raw).hexdigest()
    return _json({"case_id": case_id, "answer_sha256": digest}), digest


def _command(args: argparse.Namespace, root: Path) -> tuple[bytes, int | None]:
    if args.action == "schedule":
        return _packet_file(root, "schedule.json"), None
    folder = _case_folder(root, args.case_id)
    if args.action == "start":
        return _json({"case_id": args.case_id, "started": True}), None
    if args.action == "open":
        return _packet_file(folder, f"{args.resource}.json"), None

    source = _packet_file(folder, f"{args.side}.json")
    text = source.decode("utf-8")
    if args.action == "search":
        matches = _matches_source(text, args.literal)
        return _json(matches), len(matches)

    spans = record_spans(text)
    if args.action == "find":
        records = [
            {"id": span.identity, "name": span.name, "pointer": pointer}
            for pointer, span in spans.items()
            if span.kind == args.kind
            and (args.contains in span.identity or args.contains in (span.name or ""))
        ]
        return _json(records), len(records)

    span = spans.get(args.pointer)
    if span is None:
        raise ValueError("The pointer does not identify a direct declaration on this side.")
    quote = text[span.start : span.end].encode("utf-8")
    start_byte = len(text[: span.start].encode("utf-8"))
    return (
        _json(
            {
                "source_sha256": sha256(source).hexdigest(),
                "pointer": args.pointer,
                "start_char": span.start,
                "end_char": span.end,
                "start_byte": start_byte,
                "end_byte": start_byte + len(quote),
                "quote_sha256": sha256(quote).hexdigest(),
            }
        ),
        1,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Assigned output directory")
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("schedule", help="Read the assigned case order")
    for action in ("start", "open", "find", "search", "cite", "submit"):
        command = actions.add_parser(action)
        command.add_argument("case_id")
        if action == "open":
            command.add_argument("resource", choices=_OPEN_RESOURCES)
        if action in {"find", "search", "cite"}:
            command.add_argument("side", choices=_SOURCE_SIDES)
        if action == "find":
            command.add_argument("kind", choices=KINDS)
            command.add_argument("--contains", default="")
        elif action == "search":
            command.add_argument("literal")
        elif action == "cite":
            command.add_argument("pointer")
    return parser


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _append(output: Path, row: dict[str, Any]) -> None:
    data = (json.dumps(row, sort_keys=True) + "\n").encode()
    descriptor = os.open(output / "actions.jsonl", os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        if os.write(descriptor, data) != len(data):
            raise OSError("Incomplete action log write.")
    finally:
        os.close(descriptor)


def main() -> None:
    """Run one reviewer action and append its measured outcome."""
    parser = _parser()
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    output = args.output.resolve()
    if not output.is_dir() or output.is_relative_to(root):
        parser.error("Use the assigned existing output directory outside the packet.")

    case_id = getattr(args, "case_id", None)
    row = {
        "schema_version": ACTION_SCHEMA,
        "case_id": case_id if case_id is None or _CASE_ID.fullmatch(case_id) else None,
        "action": args.action,
        "resource": getattr(args, "resource", None),
        "side": getattr(args, "side", None),
        "started_at_utc": _utc_now(),
        "started_monotonic_ns": monotonic_ns(),
        "status": "error",
        "hits": None,
        "response_bytes": None,
        "answer_sha256": None,
    }
    try:
        if args.action == "submit":
            _case_folder(root, args.case_id)
            response, digest = _submit(args.case_id, output)
            row["answer_sha256"] = digest
            hits = None
        else:
            response, hits = _command(args, root)
        row.update(status="no_hits" if hits == 0 else "ok", hits=hits, response_bytes=len(response))
    except (IndexError, KeyError, OSError, TypeError, ValueError) as error:
        parser.error(str(error))
    finally:
        row.update(finished_at_utc=_utc_now(), finished_monotonic_ns=monotonic_ns())
        _append(output, row)
    sys.stdout.buffer.write(response)


if __name__ == "__main__":
    main()
