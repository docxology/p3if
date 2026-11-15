"""Generate matched, condition-masked citation review packets.

Each pair has common original bytes, name lookups, questions, and an identical
instrumented review tool. The audited workflow also exposes source pointers
for its observed events. A coordinator-only inventory binds the packet bytes
and assignments without placing either the key or allocation in a packet.
"""

from __future__ import annotations

from pathlib import Path

from . import citation_review_tool
from .held_out_reviewer_packets import (
    SESSIONS,
    Object,
    _audited_report,
    _digest,
    _name_lookup,
    _object,
    _write,
    assignment_rows as _prior_assignments,
    stable_id_diff,
)

CASE_IDS = tuple(f"C{number:02d}" for number in range(1, 17))
CASE_SCHEMA = "p3if.citation-case-manifest.v1"
PACKET_SCHEMA = "p3if.citation-effort-packets.v1"
_SIDES = ("before", "after")
_HOLDOUT_DOMAIN = ("ScienceResearch",) * 8 + ("MathEducation",) * 8

_INSTRUCTIONS = """# Exact citation review

Use the assigned review tool for every case-material read and for submission.
Read the schedule, process its cases in order, and run `start` when you begin
each case. Complete the case before starting the next. Use only this packet
folder and your assigned output. Do not read the repository, study materials,
other packets, or external sources. Do not derive another full comparison or
automatically fill answers. You may paste exact fields from a chosen citation.

Run `python -I -B /path/to/your/review.py --output /path/to/your/output ACTION`.
The runner only needs the Python standard library. Replace `ACTION` with one
of these commands, using your own scheduled case ID and selected side/pointer.

- `schedule` prints the case order and folders.
- `start C01` marks when you begin reviewing C01.
- `open C01 questions` lists the declarations to cite by kind and stable ID.
- `open C01 report` prints the comparison from before to after. Where a field
  value is wrapped as `{"value": null}`, the source declares null. An empty
  wrapper indicates omission. If listed, source pointers identify an event's
  direct declaration on each side, and a null pointer describes absence.
- `open C01 lookup` prints names separately for the two sides.
- `open C01 before` and `open C01 after` print the original snapshot bytes.
- `find C01 before property --contains "partial ID or name"` lists matching
  direct declarations as pointer, ID, and name. The filter is literal and
  case-sensitive. Omit it to list the requested kind on that side.
- `search C01 before "literal text"` shows up to 20 raw text matches. Matches
  can come from quoted strings or metadata as well as actual declarations.
- `cite C01 before /properties/0` prints the original snapshot hash, pointer,
  half-open codepoint and UTF-8 byte ranges, and exact quotation hash.
- `submit C01` reads one manually composed case JSON object from standard
  input. Use the returned receipt to confirm submission. It preserves your
  input bytes and accepts one submission per case.

Open the questions and report for each case. Find or confirm the precise record
identity on each side. When an identity is absent, confirm that by a source
lookup or explicit evidence from the report. A real declaration writes a full
exact location. For a present side use `cite` for the selected pointer and
check its identity before submission. When confirming a missing side via
`find`, use the stable ID and compare any hits against the exact identity.

For a case, write a JSON object with keys `case_id` and `citations`. For every
question, write one citations entry with exactly `kind`, `id`, `before`, and
`after`. A present side contains exactly the object from `cite`. An absent side
is JSON null. Keep the directions and side names as displayed. A shifted
pointer can represent the same identity in the two snapshots. Nested strings
that contain an ID are not that direct declaration. Names can be duplicated,
so use the exact stable ID and kind.

The review action log is written by the tool. Do not edit it, the packet, or
submitted responses. If you discover a failed tool invocation, correct it
before submitting. Complete and submit each assigned case once.
"""


def assignment_rows() -> list[Object]:
    """Return fixed paired assignments with equal case position across arms.

    Returns:
        Ordered assignments for each session, period, case, and condition.
    """
    rows = []
    for row in _prior_assignments():
        case_id = f"C{row['case_id'][1:]}"
        rows.append(
            {**row, "case_id": case_id, "folder": f"{row['session']}/{row['period']}/{case_id}"}
        )
    return rows


def _pointer_index(source: bytes) -> dict[tuple[str, str], str]:
    return {
        (record.kind, record.identity): pointer
        for pointer, record in citation_review_tool.record_spans(source.decode("utf-8")).items()
    }


def _report_with_pointers(before: bytes, after: bytes) -> Object:
    report = _audited_report(before, after)
    indexes = {side: _pointer_index(raw) for side, raw in zip(_SIDES, (before, after))}
    pointers = []
    for event in report["changes"]["events"]:
        kind, identity = event["kind"], event["id"]
        pointers.append(
            {
                "kind": kind,
                "id": identity,
                **{side: indexes[side].get((kind, identity)) for side in _SIDES},
            }
        )
    report["changes"]["source_pointers"] = pointers
    return report


def _questions(case: Object) -> list[Object]:
    questions = case["questions"]
    if not isinstance(questions, list) or not questions:
        raise ValueError("Expected nonempty citation questions.")
    seen = set()
    for question in questions:
        if (
            not isinstance(question, dict)
            or set(question) != {"kind", "id"}
            or question["kind"] not in citation_review_tool.KINDS
            or not isinstance(question["id"], str)
            or not question["id"]
        ):
            raise ValueError("Each citation question requires only a valid kind and stable ID.")
        seen.add((question["kind"], question["id"]))
    if len(seen) != len(questions):
        raise ValueError("Repeated citation question identity.")
    return [{"kind": question["kind"], "id": question["id"]} for question in questions]


def _materials(case_dir: Path, frozen: bytes) -> dict[str, Object]:
    if (case_dir / "case-manifest.json").read_bytes() != frozen:
        raise ValueError("Generated case manifest differs from the frozen manifest.")
    manifest = _object(frozen)
    if manifest["schema_version"] != CASE_SCHEMA:
        raise ValueError("Unsupported frozen citation case manifest.")
    cases = manifest["cases"]
    if (
        tuple(row["case_id"] for row in cases) != CASE_IDS
        or tuple(row["domain"] for row in cases) != _HOLDOUT_DOMAIN
    ):
        raise ValueError("Unexpected frozen citation case inventory.")

    materials = {}
    for case in cases:
        case_id = case["case_id"]
        first, second = ((case_dir / case_id / f"{side}.json").read_bytes() for side in _SIDES)
        if (_digest(first), _digest(second)) != (case["before_sha256"], case["after_sha256"]):
            raise ValueError(f"Exact source digest mismatch for {case_id}.")
        materials[case_id] = {
            "sources": (first, second),
            "lookup": _name_lookup(first, second),
            "questions": _questions(case),
            "p3if": _report_with_pointers(first, second),
            "diff": stable_id_diff(first, second),
        }
    return materials


def prepare_packets(case_dir: Path, frozen_manifest: Path, output_dir: Path) -> None:
    """Write four review folders and a coordinator-only digest inventory.

    Args:
        case_dir: Directory containing all generated cases and their manifest.
        frozen_manifest: Preregistered citation case manifest.
        output_dir: New directory in which to write the packets and inventory.

    Raises:
        ValueError: The manifest, question inventory, or source digest differs.
        OSError: An input is unavailable or an output cannot be created.
    """
    frozen = frozen_manifest.read_bytes()
    materials = _materials(case_dir, frozen)
    assignments = assignment_rows()
    helper = Path(citation_review_tool.__file__).read_bytes()
    output_dir.mkdir()
    for session in SESSIONS:
        session_root = output_dir / session
        session_root.mkdir()
        (session_root / "instructions.md").write_bytes(_INSTRUCTIONS.encode("utf-8"))
        (session_root / "review.py").write_bytes(helper)
        schedule = []
        for row in assignments:
            if row["session"] != session:
                continue
            case_id = row["case_id"]
            item = materials[case_id]
            destination = output_dir / row["folder"]
            destination.mkdir(parents=True)
            for side, raw in zip(_SIDES, item["sources"]):
                (destination / f"{side}.json").write_bytes(raw)
            _write(destination / "lookup.json", item["lookup"])
            _write(destination / "questions.json", item["questions"])
            _write(destination / "report.json", item[row["condition"]])
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
            "case_manifest_sha256": _digest(frozen),
            "assignments": assignments,
            "files": files,
        },
    )
