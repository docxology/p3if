"""Versioned, data-only P3IF interchange independent of the graph runtime.

The wire contract keeps declared identities, axis attributes, partial links,
and optional metrics. Graph validation applies to relationship endpoints.
Other pattern references remain declarations that can refer outside a file.
"""

# Python 3.9 resolves the alias through typing.Optional.
# ruff: noqa: UP045

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime  # noqa: TC003 - Pydantic resolves this at runtime.
from typing import TYPE_CHECKING, Annotated, ClassVar, Literal, TypeVar, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    StringConstraints,
    ValidationError,
    model_validator,
)

# Pydantic resolves the runtime alias on all supported Python versions.
if TYPE_CHECKING and sys.version_info >= (3, 10):
    from typing import TypeAlias

    _T = TypeVar("_T")
    Nullable: TypeAlias = _T | None  # noqa: UP040 - The file must parse on Python 3.9.
else:
    from typing import Optional as Nullable  # pyright: ignore[reportUnreachable]

FORMAT = "p3if.interchange"
VERSION = 1
SCHEMA_ID = "https://github.com/docxology/p3if/blob/main/schemas/p3if-interchange-v1.schema.json"
MAX_BYTES = 4 * 1024 * 1024
MAX_AXIS_ITEMS = 10_000
MAX_RELATIONSHIPS = 20_000
MAX_DEPTH = 48
MAX_JSON_VALUES = 150_000
_MAX_INTEGER_DIGITS = 128

Identity = Annotated[str, StringConstraints(min_length=1, max_length=256, pattern=r"\S")]
Name = Annotated[str, StringConstraints(min_length=1, max_length=200, pattern=r"\S")]
Description = Annotated[str, StringConstraints(min_length=1, max_length=2000, pattern=r"\S")]
Domain = Annotated[str, StringConstraints(min_length=1, max_length=100, pattern=r"\S")]
Score = Annotated[float, Field(ge=0, le=1)]
JSONMap = dict[str, JsonValue]


class InterchangeError(ValueError):
    """A malformed, oversized, or inconsistent P3IF interchange document."""

    def __init__(self, message: str) -> None:
        """Record a diagnostic that excludes untrusted JSON values."""
        super().__init__(message)


class _WireModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid", frozen=True, strict=True, allow_inf_nan=False
    )


class FrameworkIdentity(_WireModel):
    """Producer-declared framework identity and optional descriptive metadata."""

    id: Identity
    name: Name
    description: Nullable[Description] = None
    metadata: Nullable[JSONMap] = None


class _Pattern(_WireModel):
    id: Identity
    name: Name
    description: Nullable[Description] = None
    domain: Domain
    tags: Nullable[tuple[str, ...]] = None
    metadata: Nullable[JSONMap] = None
    created_at: Nullable[datetime] = None
    updated_at: Nullable[datetime] = None
    version: Nullable[str] = None
    parent_id: Nullable[Identity] = None
    validation_status: Nullable[str] = None
    quality_score: Nullable[Score] = None
    references: Nullable[tuple[str, ...]] = None
    related_patterns: Nullable[tuple[Identity, ...]] = None


class InterchangeProperty(_Pattern):
    """A retained property, including measurement and value declarations."""

    type: Nullable[Literal["property"]] = None
    data_type: Nullable[str] = None
    unit: Nullable[str] = None
    range_min: Nullable[float] = None
    range_max: Nullable[float] = None
    allowed_values: Nullable[tuple[str, ...]] = None
    category: Nullable[str] = None
    priority: Nullable[Literal["low", "medium", "high", "critical"]] = None

    @model_validator(mode="after")
    def ordered_range(self) -> InterchangeProperty:
        """Require ordered bounds when both measurement endpoints are declared."""
        if (
            self.range_min is not None
            and self.range_max is not None
            and self.range_min > self.range_max
        ):
            message = "property range_min exceeds range_max"
            raise InterchangeError(message)
        return self


class InterchangeProcess(_Pattern):
    """A retained process whose steps and dependencies are descriptive data."""

    type: Nullable[Literal["process"]] = None
    steps: Nullable[tuple[JSONMap, ...]] = None
    inputs: Nullable[tuple[str, ...]] = None
    outputs: Nullable[tuple[str, ...]] = None
    duration: Nullable[str] = None
    complexity: Nullable[Literal["low", "medium", "high"]] = None
    automation_level: Nullable[Literal["manual", "semi-automated", "fully-automated"]] = None
    prerequisites: Nullable[tuple[str, ...]] = None
    dependencies: Nullable[tuple[str, ...]] = None


class InterchangePerspective(_Pattern):
    """A retained perspective, including the producer's stakeholder context."""

    type: Nullable[Literal["perspective"]] = None
    viewpoint: Nullable[Annotated[str, StringConstraints(max_length=100)]] = None
    concerns: Nullable[tuple[str, ...]] = None
    constraints: Nullable[tuple[str, ...]] = None
    scope: Nullable[Literal["general", "specific", "detailed"]] = None
    bias_factor: Nullable[Score] = None
    stakeholder_type: Nullable[str] = None
    expertise_level: Nullable[Literal["novice", "intermediate", "expert"]] = None


_AXIS_FIELDS = ("property_id", "process_id", "perspective_id")
_MIN_RELATIONSHIP_AXES = 2


class InterchangeRelationship(_WireModel):
    """A link joining two or three retained axes with optional reported scores."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "anyOf": [
                {
                    "required": [left, right],
                    "properties": {left: {"type": "string"}, right: {"type": "string"}},
                }
                for left, right in (
                    ("property_id", "process_id"),
                    ("property_id", "perspective_id"),
                    ("process_id", "perspective_id"),
                )
            ],
        }
    )

    id: Identity
    property_id: Nullable[Identity] = None
    process_id: Nullable[Identity] = None
    perspective_id: Nullable[Identity] = None
    strength: Nullable[Score] = None
    confidence: Nullable[Score] = None
    bidirectional: Nullable[bool] = None
    relationship_type: Nullable[
        Literal["general", "causal", "dependency", "composition", "aggregation", "specialization"]
    ] = None
    direction: Nullable[str] = None
    temporal_context: Nullable[str] = None
    validity_period: Nullable[dict[str, datetime]] = None
    evidence_sources: Nullable[tuple[str, ...]] = None
    validation_method: Nullable[str] = None
    assumptions: Nullable[tuple[str, ...]] = None
    metadata: Nullable[JSONMap] = None
    created_at: Nullable[datetime] = None
    updated_at: Nullable[datetime] = None
    status: Nullable[str] = None
    quality_score: Nullable[Score] = None

    @model_validator(mode="after")
    def connected_axes(self) -> InterchangeRelationship:
        """Require at least two explicitly connected dimensions."""
        if sum(value is not None for value in self.endpoints()) < _MIN_RELATIONSHIP_AXES:
            message = "a relationship must connect at least two dimensions"
            raise InterchangeError(message)
        return self

    def endpoints(self) -> tuple[Nullable[str], Nullable[str], Nullable[str]]:
        """Return property, process, and perspective IDs in axis order."""
        return self.property_id, self.process_id, self.perspective_id


class Interchange(_WireModel):
    """The closed version-one envelope for a complete declared graph."""

    format: Literal["p3if.interchange"]
    version: int = Field(ge=VERSION, le=VERSION, json_schema_extra={"const": VERSION})
    framework: FrameworkIdentity
    properties: tuple[InterchangeProperty, ...] = Field(max_length=MAX_AXIS_ITEMS)
    processes: tuple[InterchangeProcess, ...] = Field(max_length=MAX_AXIS_ITEMS)
    perspectives: tuple[InterchangePerspective, ...] = Field(max_length=MAX_AXIS_ITEMS)
    relationships: tuple[InterchangeRelationship, ...] = Field(max_length=MAX_RELATIONSHIPS)

    @model_validator(mode="after")
    def closed_graph(self) -> Interchange:
        """Validate stable identities and local, axis-correct relationship endpoints."""
        axis_for_id: dict[str, str] = {}
        for axis, patterns in (
            ("property_id", self.properties),
            ("process_id", self.processes),
            ("perspective_id", self.perspectives),
        ):
            for pattern in patterns:
                if pattern.id in axis_for_id:
                    message = "duplicate pattern identity across the declared axes"
                    raise InterchangeError(message)
                axis_for_id[pattern.id] = axis

        seen_relationships: set[str] = set()
        for relationship in self.relationships:
            if relationship.id in seen_relationships:
                message = "duplicate relationship identity"
                raise InterchangeError(message)
            seen_relationships.add(relationship.id)
            endpoints = relationship.endpoints()
            for index, axis in enumerate(_AXIS_FIELDS):
                endpoint = endpoints[index]
                if endpoint is not None and axis_for_id.get(endpoint) != axis:
                    message = f"relationship {axis} is absent or belongs to a different axis"
                    raise InterchangeError(message)
        return self


def _unique_object(pairs: list[tuple[str, JsonValue]]) -> JSONMap:
    result: JSONMap = {}
    for key, value in pairs:
        if key in result:
            message = "JSON object contains a duplicate member"
            raise InterchangeError(message)
        result[key] = value
    return result


def _finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        message = "JSON numbers must be finite"
        raise InterchangeError(message)
    return value


def _bounded_integer(token: str) -> int:
    if len(token.removeprefix("-")) > _MAX_INTEGER_DIGITS:
        message = "JSON integer exceeds the supported precision"
        raise InterchangeError(message)
    return int(token)


def _reject_constant(token: str) -> float:
    message = f"invalid JSON number {token}"
    raise InterchangeError(message)


def _valid_string(value: str) -> None:
    if any("\ud800" <= character <= "\udfff" for character in value):
        message = "JSON strings must contain valid Unicode scalar values"
        raise InterchangeError(message)


def _check_structure(root: JSONMap) -> None:
    pending: list[tuple[JsonValue, int]] = [(root, 1)]
    count = 0
    while pending:
        value, depth = pending.pop()
        count += 1
        if count > MAX_JSON_VALUES or depth > MAX_DEPTH:
            message = "JSON structure exceeds the interchange limits"
            raise InterchangeError(message)
        if isinstance(value, (dict, list)) and count + len(pending) + len(value) > MAX_JSON_VALUES:
            message = "JSON structure exceeds the interchange limits"
            raise InterchangeError(message)
        if isinstance(value, dict):
            for key, child in value.items():
                _valid_string(key)
                pending.append((child, depth + 1))
        elif isinstance(value, list):
            pending.extend((child, depth + 1) for child in value)
        elif isinstance(value, str):
            _valid_string(value)


def decode_json(data: object) -> JSONMap:
    """Decode one strict, bounded UTF-8 JSON object.

    Args:
        data: Complete JSON bytes to validate.

    Returns:
        A data-only JSON object with its original keys and values.

    Raises:
        InterchangeError: The input exceeds a limit or is not strict UTF-8 JSON.
    """
    if not isinstance(data, bytes) or not 0 < len(data) <= MAX_BYTES:
        message = f"expected 1 to {MAX_BYTES} bytes of UTF-8 JSON"
        raise InterchangeError(message)
    try:
        document = cast(
            "object",
            json.loads(
                data.decode("utf-8"),
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
                parse_float=_finite_float,
                parse_int=_bounded_integer,
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        message = "expected a well-formed UTF-8 JSON object"
        raise InterchangeError(message) from error
    if not isinstance(document, dict):
        message = "expected a JSON object at the document root"
        raise InterchangeError(message)
    checked = cast("JSONMap", document)
    _check_structure(checked)
    return checked


def load_interchange(data: bytes) -> Interchange:
    """Validate the complete P3IF wire contract and its reference graph.

    Args:
        data: Untrusted UTF-8 JSON document bytes.

    Returns:
        A validated P3IF interchange document.

    Raises:
        InterchangeError: The wire contract or reference graph is invalid.
    """
    _ = decode_json(data)
    try:
        return Interchange.model_validate_json(data)
    except ValidationError as error:
        issue = error.errors(include_input=False, include_url=False)[0]
        path = ".".join(str(part) for part in issue["loc"]) or "document"
        message = f"invalid P3IF interchange at {path}: {issue['msg']}"
        raise InterchangeError(message) from error


def canonical_bytes(model: Interchange) -> bytes:
    """Serialize deterministic UTF-8 JSON with optional fields left as declared.

    Args:
        model: A validated P3IF interchange document.

    Returns:
        Compact sorted JSON terminated by one line feed.

    Raises:
        InterchangeError: The model no longer has a valid or bounded wire form.
    """
    try:
        ordered = model.model_copy(
            update={
                "properties": tuple(sorted(model.properties, key=lambda item: item.id)),
                "processes": tuple(sorted(model.processes, key=lambda item: item.id)),
                "perspectives": tuple(sorted(model.perspectives, key=lambda item: item.id)),
                "relationships": tuple(sorted(model.relationships, key=lambda item: item.id)),
            }
        )
        payload = ordered.model_dump(mode="json", exclude_unset=True)
        data = (
            json.dumps(
                payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as error:
        message = "the interchange document could not be encoded as strict JSON"
        raise InterchangeError(message) from error
    _ = load_interchange(data)
    return data


def interchange_sha256(model: Interchange) -> str:
    """Hash the canonical interchange document, including optional declared data."""
    return hashlib.sha256(canonical_bytes(model)).hexdigest()


def interchange_schema() -> JSONMap:
    """Return the version-one JSON Schema with its published identity."""
    schema = cast("JSONMap", Interchange.model_json_schema())
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        **schema,
    }
