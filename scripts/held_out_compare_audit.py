"""Compare each public P3IF audit against the independent raw-source reference.

Generate the reference and source check with ``held_out_source_check.py`` and
the conformance receipt with ``held_out_verify.py``. Run this command after
public registration with the frozen case directory and exact commit ID.
"""

import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import sys

from p3if.cli import main as audit_cli


def digest(raw):
    return sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def first_difference(left, right, path=""):
    if left.__class__ is not right.__class__:
        return path
    if isinstance(left, dict):
        if left.keys() != right.keys():
            return f"{path}/(fields)"
        for key in sorted(left):
            if (found := first_difference(left[key], right[key], f"{path}/{key}")) is not None:
                return found
    elif isinstance(left, list):
        if len(left) != len(right):
            return f"{path}/(length)"
        for index, (first, second) in enumerate(zip(left, right)):
            if (found := first_difference(first, second, f"{path}/{index}")) is not None:
                return found
    elif left != right:
        return path
    return None


def compare(
    case_dir,
    reference_path,
    source_check_path,
    conformance_path,
    registration_commit,
    output,
):
    require(
        re.fullmatch("[0-9a-f]{40}", registration_commit),
        "Need exact public registration commit",
    )
    manifest_bytes = (case_dir / "case-manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    reference_bytes = reference_path.read_bytes()
    reference = json.loads(reference_bytes)
    source_check_bytes = source_check_path.read_bytes()
    source_check = json.loads(source_check_bytes)
    conformance_bytes = conformance_path.read_bytes()
    conformance = json.loads(conformance_bytes)
    registered_digest = digest(manifest_bytes)
    require(
        reference["case_manifest_sha256"]
        == source_check["case_manifest_sha256"]
        == conformance["manifest_sha256"]
        == registered_digest,
        "Claimed registration inputs disagree",
    )
    identities = [case["case_id"] for case in manifest["cases"]]
    require(
        identities == [f"H{number:02d}" for number in range(1, 17)],
        "Wrong case inventory",
    )
    require(
        identities
        == [case["case_id"] for case in source_check["cases"]]
        == [case["case_id"] for case in conformance["cases"]]
        == sorted(reference["cases"]),
        "Result case inventories disagree",
    )
    inventory = {}
    for case in manifest["cases"]:
        identity = case["case_id"]
        files = [
            (case_dir / identity / f"{name}.json").resolve(strict=True)
            for name in ("before", "after")
        ]
        for name, file in zip(("before", "after"), files):
            require(
                digest(file.read_bytes())
                == reference["cases"][identity][name]["source_sha256"]
                == case[f"{name}_sha256"],
                f"Invalid frozen input: {identity} {name}",
            )
        inventory[identity] = files
    rows = []
    for source_row, run_row in zip(source_check["cases"], conformance["cases"]):
        identity = source_row["case_id"]
        require(
            all(
                run_row[name] == source_row[name]
                for name in (
                    "case_id",
                    "domain",
                    "intervention",
                    "classification",
                    "events",
                    "absent_sides",
                )
            ),
            f"Reported event/layout mismatch: {identity}",
        )
        require(
            run_row["passed"] and run_row["present_spans"] == source_row["exact_spans"],
            f"Registered conformance failed: {identity}",
        )
        buffer = io.BytesIO()
        output_stream = io.TextIOWrapper(buffer, encoding="utf-8")
        with redirect_stdout(output_stream):
            status = audit_cli(["audit", *map(str, inventory[identity])])
        require(status == 0, f"Audit CLI failed: {identity} ({status})")
        output_stream.flush()
        raw_audit = buffer.getvalue()
        output_stream.close()
        actual = json.loads(raw_audit)
        mismatch = first_difference(reference["cases"][identity], actual)
        rows.append(
            {
                "case_id": identity,
                "passed": mismatch is None,
                "mismatch_path": mismatch,
                "sha256": digest(raw_audit),
            }
        )
    result = {
        "schema_version": "p3if.held-out-independent-audit-comparison.v1",
        "registration_commit": registration_commit,
        "case_manifest_sha256": registered_digest,
        "source_check_sha256": digest(source_check_bytes),
        "raw_audit_reference_sha256": digest(reference_bytes),
        "conformance_sha256": digest(conformance_bytes),
        "passed": sum(row["passed"] for row in rows),
        "cases": rows,
    }
    with output.open("x", encoding="utf-8") as stream:
        stream.write(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
        )
    print(
        f"Matched complete P3IF audit output against independent JSON for {result['passed']}/{len(rows)} cases"
    )
    return result["passed"] == len(rows)


def main():
    """Write the complete independent comparison receipt after registration."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("case_dir", "reference", "source_check", "conformance"):
        parser.add_argument(name, type=Path)
    parser.add_argument("registration_commit")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not compare(
        args.case_dir,
        args.reference,
        args.source_check,
        args.conformance,
        args.registration_commit,
        args.output,
    ):
        sys.exit(1)


if __name__ == "__main__":
    main()
