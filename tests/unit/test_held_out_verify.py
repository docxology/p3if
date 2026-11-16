"""Test the complete frozen case replay and its source binding."""

from pathlib import Path

import pytest

from p3if.held_out_cases import build_cases
from p3if.held_out_verify import verify_cases

_ROOT = Path(__file__).resolve().parents[2]
_DOCS = _ROOT / "docs/manuscript"


def test_held_out_verify_requires_exact_sources(tmp_path: Path) -> None:
    cases = tmp_path / "cases"
    build_cases(
        _ROOT / "data/domains",
        _DOCS / "held-out-case-spec.json",
        cases,
    )
    manifest = _DOCS / "held-out-case-manifest.json"
    receipt = verify_cases(cases, manifest)
    assert (receipt["passed"], receipt["events"]) == (16, 48)
    assert (receipt["present_spans"], receipt["absent_sides"]) == (78, 18)

    changed = cases / "H16" / "after.json"
    changed.write_bytes(changed.read_bytes() + b" ")
    with pytest.raises(ValueError, match="Exact source digest mismatch for H16"):
        verify_cases(cases, manifest)
