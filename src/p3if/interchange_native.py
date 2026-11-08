"""Convert native frameworks and older JSON exports to the versioned interchange."""

import json
from typing import Any

from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticSerializationError

from p3if.core.framework import P3IFFramework
from p3if.core.models import BasePattern, Perspective, Process, Property, Relationship
from p3if.interchange import (
    FORMAT,
    VERSION,
    FrameworkIdentity,
    Interchange,
    InterchangeError,
    canonical_bytes,
    decode_json,
    load_interchange,
)

_GROUPS = {"property": "properties", "process": "processes", "perspective": "perspectives"}
_MODELS: dict[str, type[BasePattern]] = {
    "properties": Property,
    "processes": Process,
    "perspectives": Perspective,
}


def _wire(framework: FrameworkIdentity, groups: dict[str, list[dict[str, Any]]]) -> Interchange:
    try:
        data = json.dumps(
            {
                "format": FORMAT,
                "version": VERSION,
                "framework": framework.model_dump(mode="json", exclude_unset=True),
                **groups,
            },
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (ValueError, TypeError, RecursionError) as error:
        raise InterchangeError("Framework fields must be bounded JSON data.") from error
    return load_interchange(data)


def _native_fields(model: BaseModel, identity: str) -> dict[str, Any]:
    mutated = {
        name
        for name, field in type(model).model_fields.items()
        if field.default_factory in (dict, list) and getattr(model, name)
    }
    included = model.model_fields_set | mutated
    try:
        return {**model.model_dump(mode="json", include=included), "id": identity}
    except (PydanticSerializationError, TypeError, RecursionError) as error:
        raise InterchangeError("Native fields must be representable as JSON data.") from error


def interchange_from_framework(
    framework: P3IFFramework, identity: FrameworkIdentity
) -> Interchange:
    """Export a native framework with stable IDs and its explicitly supplied identity.

    Args:
        framework: Native patterns and relationships to export.
        identity: Stable framework identity and any declared metadata.

    Returns:
        A validated interchange snapshot with explicit fields and no generated scores.

    Raises:
        InterchangeError: The native data does not satisfy the versioned contract.
    """
    patterns, relationships = framework.snapshot_models()
    groups: dict[str, list[dict[str, Any]]] = {name: [] for name in _MODELS}
    for pattern in patterns:
        groups[_GROUPS[pattern.type.value]].append(_native_fields(pattern, pattern.id))
    groups["relationships"] = [_native_fields(item, item.id) for item in relationships]
    return _wire(identity, groups)


def framework_from_interchange(interchange: Interchange) -> P3IFFramework:
    """Materialize a wire snapshot that can round-trip through native P3IF models.

    Args:
        interchange: The validated interchange data.

    Returns:
        A new framework with detached models and no external storage backend.

    Raises:
        InterchangeError: Native P3IF requires missing data or would alter the snapshot.
    """
    try:
        patterns = [
            _MODELS[group].model_validate(item.model_dump(mode="json", exclude_unset=True))
            for group, entries in (
                ("properties", interchange.properties),
                ("processes", interchange.processes),
                ("perspectives", interchange.perspectives),
            )
            for item in entries
        ]
        relationships = [
            Relationship.model_validate(item.model_dump(mode="json", exclude_unset=True))
            for item in interchange.relationships
        ]
    except (ValidationError, TypeError) as error:
        raise InterchangeError(
            "Native P3IF cannot represent this snapshot. Check required native fields "
            "such as pattern descriptions and perspective viewpoints."
        ) from error
    framework = P3IFFramework()
    for pattern in patterns:
        framework.add_pattern(pattern)
    for relationship in relationships:
        framework.add_relationship(relationship)
    roundtrip = interchange_from_framework(framework, interchange.framework)
    if canonical_bytes(roundtrip) != canonical_bytes(interchange):
        raise InterchangeError("Native P3IF normalization would change this snapshot.")
    return framework


def _legacy_entries(value: object, group: str, *, keyed: bool = False) -> list[dict[str, Any]]:
    if keyed and isinstance(value, dict):
        for identity, entry in value.items():
            if not isinstance(entry, dict) or entry.get("id") != identity:
                raise InterchangeError(f"Legacy {group} map keys must match their explicit IDs.")
        return list(value.values())
    if keyed or not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise InterchangeError(f"Legacy {group} must contain JSON objects in its declared format.")
    return value


def _domain_groups(raw: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    domain, version, patterns = raw["domain"], raw["version"], raw["patterns"]
    if not isinstance(domain, str) or not domain.strip():
        raise InterchangeError("Legacy domain export requires a declared domain name.")
    if not isinstance(version, str) or not version.strip():
        raise InterchangeError("Legacy domain export requires a declared domain version.")
    if not isinstance(patterns, dict) or patterns.keys() != _MODELS.keys():
        raise InterchangeError("Legacy domain export requires the three named pattern groups.")
    groups = {name: _legacy_entries(patterns[name], name) for name in _MODELS}
    for kind, name in _GROUPS.items():
        items = groups[name]
        if raw[name] != [item.get("name") for item in items]:
            raise InterchangeError(f"Legacy domain {name} names must match their pattern list.")
        if any(item.get("type") != kind or item.get("domain") != domain for item in items):
            raise InterchangeError(
                f"Legacy domain {name} must match their declared type and domain."
            )
    groups["relationships"] = _legacy_entries(raw["relationships"], "relationships")
    return groups


def migrate_legacy(data: bytes, identity: FrameworkIdentity) -> Interchange:
    """Migrate a recognized legacy export without inferring missing source fields.

    Args:
        data: Exact UTF-8 bytes of a grouped, flat, ID-keyed, or domain-library export.
        identity: Stable identity assigned to the resulting versioned framework.

    Returns:
        A validated interchange snapshot, including any legacy export metadata.

    Raises:
        InterchangeError: The format is unsupported or its data is invalid.
    """
    raw = decode_json(data)
    if not isinstance(raw, dict):
        raise InterchangeError("A legacy P3IF export must be a JSON object.")
    grouped = {*_MODELS, "relationships"}
    flat = {"patterns", "relationships"}
    domain = grouped | {"patterns", "domain", "version"}
    metadata_fields = {"framework_metadata", "metadata"}
    fields = raw.keys() - metadata_fields
    if fields in (domain, domain | {"description"}):
        groups = _domain_groups(raw)
        metadata_fields |= {"domain", "version", "description"}
    elif fields == grouped:
        groups = {name: _legacy_entries(raw[name], name) for name in grouped}
    elif fields == flat:
        keyed = isinstance(raw["patterns"], dict)
        groups = {name: [] for name in _MODELS}
        for pattern in _legacy_entries(raw["patterns"], "patterns", keyed=keyed):
            kind = pattern.get("type")
            if not isinstance(kind, str) or kind not in _GROUPS:
                raise InterchangeError("Legacy patterns require a recognized explicit type.")
            groups[_GROUPS[kind]].append(pattern)
        groups["relationships"] = _legacy_entries(
            raw["relationships"], "relationships", keyed=keyed
        )
    else:
        raise InterchangeError("Expected a grouped, flat, ID-keyed, or domain-library P3IF export.")
    legacy_metadata = {name: raw[name] for name in metadata_fields if name in raw}
    if legacy_metadata:
        metadata = dict(identity.metadata or {})
        if "legacy_export" in metadata:
            raise InterchangeError("Framework metadata already contains a legacy_export entry.")
        metadata["legacy_export"] = legacy_metadata
        identity = FrameworkIdentity.model_validate(
            {**identity.model_dump(exclude_unset=True), "metadata": metadata}
        )
    return _wire(identity, groups)
