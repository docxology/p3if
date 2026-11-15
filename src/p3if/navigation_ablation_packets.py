"""Prepare matched reviewer packets for the P3IF source navigation ablation.

Both arms receive the same audit and transition report, original source bytes,
questions, lookup data and instrumented reader. Only the per-event source
pointer array varies. Session folders carry no condition labels. The separate
coordinator manifest records the assignments and hashes every delivered file.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files as resource_files
from pathlib import Path

from p3if.citation_effort_packets import (
    CASE_SCHEMA,
    _INSTRUCTIONS,
    _questions,
    _report_with_pointers,
)
from p3if.held_out_reviewer_packets import (
    SESSIONS,
    Object,
    _digest,
    _name_lookup,
    _object,
    _write,
    assignment_rows as _prior_assignments,
)

CASE_IDS = tuple(f"A{number:02d}" for number in range(1, 17))
PACKET_SCHEMA = "p3if.navigation-ablation-packets.v1"
_SIDES = ("before", "after")
_DOMAINS = ("ScienceResearch",) * 8 + ("MathEducation",) * 8
_CONDITIONS = {"p3if": "navigation", "diff": "no_navigation"}


@dataclass(frozen=True)
class _CaseMaterials:
    sources: tuple[bytes, bytes]
    lookup: Object
    questions: list[Object]
    reports: dict[str, Object]


def assignment_rows() -> list[Object]:
    """Return the four counterbalanced schedules in delivery order.

    Returns:
        Coordinator rows with session, period, case ID, condition, and folder.
        Each case has the same period and position in both conditions.
    """
    rows = []
    for row in _prior_assignments():
        case_id = f"A{row['case_id'][1:]}"
        rows.append(
            {
                **row,
                "case_id": case_id,
                "condition": _CONDITIONS[row["condition"]],
                "folder": f"{row['session']}/{row['period']}/{case_id}",
            }
        )
    return rows


def _materials(case_dir: Path, frozen: bytes) -> dict[str, _CaseMaterials]:
    if (case_dir / "case-manifest.json").read_bytes() != frozen:
        raise ValueError("Generated case manifest differs from the frozen manifest.")
    manifest = _object(frozen)
    if manifest["schema_version"] != CASE_SCHEMA:
        raise ValueError("Unsupported frozen citation case manifest.")
    cases = manifest["cases"]
    if (
        tuple(row["case_id"] for row in cases) != CASE_IDS
        or tuple(row["domain"] for row in cases) != _DOMAINS
    ):
        raise ValueError("Unexpected frozen navigation ablation case inventory.")

    materials = {}
    for case in cases:
        case_id = case["case_id"]
        before = (case_dir / case_id / "before.json").read_bytes()
        after = (case_dir / case_id / "after.json").read_bytes()
        if (_digest(before), _digest(after)) != (case["before_sha256"], case["after_sha256"]):
            raise ValueError(f"Exact source digest mismatch for {case_id}.")
        report = _report_with_pointers(before, after)
        without_pointers = {
            **report,
            "changes": {**report["changes"], "source_pointers": []},
        }
        materials[case_id] = _CaseMaterials(
            sources=(before, after),
            lookup=_name_lookup(before, after),
            questions=_questions(case),
            reports={"navigation": report, "no_navigation": without_pointers},
        )
    return materials


def _reader_source() -> bytes:
    # Preserve the historical packet reader bytes, including the case ID guard
    # in its archived packets. Specialize only the guard for this study.
    source = resource_files("p3if").joinpath("citation_review_tool.py").read_bytes()
    prior_guard = rb're.compile(r"C[0-9]{2}\Z")'
    ablation_guard = rb're.compile(r"A[0-9]{2}\Z")'
    if source.count(prior_guard) != 1:
        raise ValueError("The bundled review reader has an unexpected case ID guard.")
    return source.replace(prior_guard, ablation_guard)


def prepare_packets(case_dir: Path, frozen_manifest: Path, output_dir: Path) -> None:
    """Write four masked session folders and their coordinator manifest.

    Args:
        case_dir: Generated case pairs with their case manifest.
        frozen_manifest: Preregistered byte-exact case manifest.
        output_dir: New directory for the four sessions and coordinator manifest.

    Raises:
        ValueError: The frozen manifest, source, or bundled reader differs.
        OSError: An input cannot be read or the output cannot be created.
    """
    frozen = frozen_manifest.read_bytes()
    materials = _materials(case_dir, frozen)
    assignments = assignment_rows()
    reader = _reader_source()
    instructions = _INSTRUCTIONS.replace("C01", "A01").encode("utf-8")
    output_dir.mkdir()
    for session in SESSIONS:
        session_root = output_dir / session
        session_root.mkdir()
        (session_root / "instructions.md").write_bytes(instructions)
        (session_root / "review.py").write_bytes(reader)
        schedule = []
        for row in assignments:
            if row["session"] != session:
                continue
            case_id = row["case_id"]
            item = materials[case_id]
            destination = output_dir / row["folder"]
            destination.mkdir(parents=True)
            for side, raw in zip(_SIDES, item.sources):
                (destination / f"{side}.json").write_bytes(raw)
            _write(destination / "lookup.json", item.lookup)
            _write(destination / "questions.json", item.questions)
            _write(destination / "report.json", item.reports[row["condition"]])
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
