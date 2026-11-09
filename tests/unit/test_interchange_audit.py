"""Bind the public audit to exact bytes and independently stated controls."""

import json
from hashlib import sha256
from pathlib import Path

import pytest

from p3if.cli import main
from p3if.interchange import InterchangeError
from p3if.interchange_audit import audit_interchange

_EXAMPLE = Path(__file__).resolve().parents[2] / "examples/interchange/framework-v1.json"


def test_audit_distinguishes_identical_bytes_from_encoding_changes() -> None:
    """Keep exact byte identity separate from canonical graph identity."""
    source = _EXAMPLE.read_bytes()
    reordered = json.loads(source)
    reordered["relationships"].reverse()
    reformatted = json.dumps(reordered, sort_keys=True, ensure_ascii=False).encode()
    identical = audit_interchange(source, source)
    assert identical.classification == "identical_bytes"
    assert identical.before == identical.after

    audit = audit_interchange(source, reformatted)
    assert audit.classification == "encoding_only"
    assert audit.before.source_sha256 == sha256(source).hexdigest()
    assert audit.after.source_sha256 == sha256(reformatted).hexdigest()
    assert audit.before.source_sha256 != audit.after.source_sha256
    assert audit.before.analysis == audit.after.analysis
    assert not any(row.modified or row.added or row.removed or row.rewired for row in audit.changes)


def test_audit_tracks_signed_metric_and_coordinate_changes() -> None:
    """A rewire and an omitted score preserve the original sparse denominator rules."""
    source = _EXAMPLE.read_bytes()
    revised = json.loads(source)
    revised["processes"].append(
        {"id": "process.recheck", "name": "Recheck", "domain": "synthetic-archive"}
    )
    relationship = revised["relationships"][0]
    relationship["process_id"] = "process.recheck"
    del relationship["strength"]
    target = json.dumps(revised).encode()
    report = audit_interchange(source, target)
    assert report.classification == "declared_change"
    assert report.relationship_delta == 0
    changes = {row.kind: row for row in report.changes}
    assert changes["relationship"].modified == changes["relationship"].rewired == 1
    assert changes["process"].added == 1
    assert report.axes[1].total == 1
    assert report.coordinates[-1].possible == 2
    assert report.coordinates[-1].observed == 0
    assert report.strength.omitted == 1
    assert report.strength.zero == report.strength.reported == -1
    reverse = audit_interchange(target, source)
    assert reverse.before == report.after
    assert reverse.strength.zero == 1
    assert reverse.coordinates[-1].possible == -2


def test_audit_cli_writes_one_report_and_refuses_unrelated_frameworks(tmp_path: Path) -> None:
    """The same audit survives JSON export, while an invalid pair writes no report."""
    output = tmp_path / "audit.json"
    assert main(["audit", str(_EXAMPLE), str(_EXAMPLE), "-o", str(output)]) == 0
    assert json.loads(output.read_bytes()) == audit_interchange(
        _EXAMPLE.read_bytes(), _EXAMPLE.read_bytes()
    ).model_dump(mode="json")
    unrelated = _EXAMPLE.read_bytes().replace(b"synthetic.archive-example", b"unrelated")
    foreign = tmp_path / "foreign.json"
    foreign.write_bytes(unrelated)
    missing = tmp_path / "missing.json"
    with pytest.raises(InterchangeError, match="matching framework IDs"):
        audit_interchange(_EXAMPLE.read_bytes(), unrelated)
    assert main(["audit", str(_EXAMPLE), str(foreign), "-o", str(missing)]) == 2
    assert not missing.exists()
