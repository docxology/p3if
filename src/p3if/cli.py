"""Offline commands for producing, checking, and inspecting P3IF interchange."""

import argparse
import json
import logging
import os
import stat
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Optional, Sequence

from pydantic import ValidationError

from p3if import __version__
from p3if.interchange import (
    MAX_BYTES,
    FrameworkIdentity,
    Interchange,
    InterchangeError,
    canonical_bytes,
    interchange_schema,
    interchange_sha256,
    load_interchange,
)
from p3if.interchange_native import (
    framework_from_interchange,
    migrate_legacy,
)


def _read(source: str) -> bytes:
    if source == "-":
        return sys.stdin.buffer.read(MAX_BYTES + 1)
    fd = os.open(source, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise InterchangeError("Read interchange from a regular file or standard input.")
        return stream.read(MAX_BYTES + 1)


def _write(data: bytes, destination: str) -> None:
    if destination == "-":
        sys.stdout.buffer.write(data)
        return
    target = Path(destination)
    stream = NamedTemporaryFile(dir=target.parent, prefix=".p3if-", delete=False)
    temporary = Path(stream.name)
    try:
        with stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
    finally:
        temporary.unlink()


def _json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _native_roundtrip(document: Interchange) -> None:
    # P3IF installs a console logger at import time. Keep its existing library behavior
    # and reserve CLI stdout for the machine-readable document during this command.
    stdout = sys.stdout
    handlers = [
        handler
        for handler in logging.getLogger().handlers
        if isinstance(handler, logging.StreamHandler) and handler.stream is stdout
    ]
    try:
        for handler in handlers:
            handler.setStream(sys.stderr)
        with redirect_stdout(sys.stderr):
            framework_from_interchange(document)
    finally:
        for handler in handlers:
            handler.setStream(stdout)


def inspect_interchange(document: Interchange) -> dict[str, Any]:
    """Summarize declared P3IF axes, link coverage, and explicitly reported metrics.

    Args:
        document: A validated interchange snapshot.

    Returns:
        Declared counts, cardinalities, and the canonical identity as JSON-ready data.
    """
    counts = {
        "properties": len(document.properties),
        "processes": len(document.processes),
        "perspectives": len(document.perspectives),
    }
    linked: tuple[set[str], set[str], set[str]] = (set(), set(), set())
    triples: set[tuple[str, str, str]] = set()
    pair_count = 0
    strength_count = 0
    confidence_count = 0
    for relation in document.relationships:
        property_id, process_id, perspective_id = relation.endpoints()
        for ids, identity in zip(linked, (property_id, process_id, perspective_id)):
            if identity is not None:
                ids.add(identity)
        if property_id is not None and process_id is not None and perspective_id is not None:
            triples.add((property_id, process_id, perspective_id))
        else:
            pair_count += 1
        strength_count += relation.strength is not None
        confidence_count += relation.confidence is not None
    return {
        "format": document.format,
        "version": document.version,
        "framework": document.framework.model_dump(mode="json", exclude_unset=True),
        "sha256": interchange_sha256(document),
        "axes": counts,
        "unlinked_axes": {key: counts[key] - len(ids) for key, ids in zip(counts, linked)},
        "domains": sorted(
            {item.domain for item in document.properties}
            | {item.domain for item in document.processes}
            | {item.domain for item in document.perspectives}
        ),
        "relationships": {
            "pairs": pair_count,
            "triples": len(document.relationships) - pair_count,
            "explicit_strength": strength_count,
            "explicit_confidence": confidence_count,
        },
        "coordinate_space": {
            "possible_triples": counts["properties"] * counts["processes"] * counts["perspectives"],
            "linked_triples": len(triples),
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="p3if", description="P3IF versioned interchange tools", allow_abbrev=False
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("validate", "Validate the schema and typed relationship graph."),
        ("inspect", "Summarize the declared graph and its content identity."),
        ("canonicalize", "Write stable, sorted interchange JSON."),
        ("migrate", "Convert a recognized legacy P3IF JSON export."),
        ("roundtrip", "Verify exact native framework materialization and re-export."),
        ("schema", "Write the public version-one JSON Schema."),
    ):
        command = commands.add_parser(name, help=help_text, allow_abbrev=False)
        if name != "schema":
            command.add_argument("input", help="Local JSON file or - for standard input")
        if name != "validate":
            command.add_argument("-o", "--output", default="-", help="New file or - for stdout")
        if name == "migrate":
            command.add_argument("--id", required=True, help="Stable identity for the framework")
            command.add_argument("--name", required=True, help="Display name for the framework")
            command.add_argument("--description", help="Optional description of the framework")
    return parser


def _run(options: argparse.Namespace) -> None:
    command = options.command
    if command == "schema":
        _write(_json(interchange_schema()), options.output)
        return
    raw = _read(options.input)
    if command == "migrate":
        identity = FrameworkIdentity(id=options.id, name=options.name)
        if options.description is not None:
            identity = FrameworkIdentity(
                id=identity.id, name=identity.name, description=options.description
            )
        _write(canonical_bytes(migrate_legacy(raw, identity)), options.output)
        return
    interchange = load_interchange(raw)
    if command == "validate":
        _write(_json({"valid": True, "sha256": interchange_sha256(interchange)}), "-")
    elif command == "inspect":
        _write(_json(inspect_interchange(interchange)), options.output)
    elif command == "roundtrip":
        _native_roundtrip(interchange)
        _write(canonical_bytes(interchange), options.output)
    else:
        _write(canonical_bytes(interchange), options.output)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the command-line entry point.

    Args:
        argv: Arguments after the program name, or the process arguments when omitted.

    Returns:
        Zero on success and two on invalid input or an I/O failure.
    """
    options = _parser().parse_args(argv)
    try:
        _run(options)
    except (InterchangeError, OSError, ValidationError) as error:
        print(f"p3if: {error}", file=sys.stderr)
        return 2
    return 0
