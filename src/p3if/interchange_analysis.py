"""Sparse analysis and stable-identity comparisons for P3IF interchange.

Coverage counts only explicitly declared coordinates. A triple contributes to
its three axes and the triple space, with no implied pair declarations.
Comparison keeps field-presence changes, including omitted and explicit null.
"""

from __future__ import annotations

import json
from math import prod
from typing import TYPE_CHECKING, ClassVar, Final, Literal, cast

from pydantic import BaseModel, ConfigDict

from .interchange import (
    Interchange,
    InterchangeError,
    InterchangeRelationship,
    JSONMap,
    interchange_sha256,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

Axis = Literal["property", "process", "perspective"]
ChangeKind = Literal["property", "process", "perspective", "relationship"]
Metric = Literal["strength", "confidence"]

_AXES: Final[tuple[Axis, ...]] = ("property", "process", "perspective")
_SPACES: Final[tuple[tuple[Axis, ...], ...]] = (
    ("property", "process"),
    ("property", "perspective"),
    ("process", "perspective"),
    _AXES,
)
_CHANGE_KINDS: Final[tuple[ChangeKind, ...]] = (*_AXES, "relationship")


class _Report(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True, strict=True)


class AxisCoverage(_Report):
    """One declared dimension and its explicit participation in links."""

    axis: Axis
    total: int
    linked: int
    unlinked: int


class CoordinateCoverage(_Report):
    """Exact declared coordinates over one pair or triple denominator."""

    axes: tuple[Axis, ...]
    relationships: int
    observed: int
    possible: int
    unobserved: int


class MetricCoverage(_Report):
    """Field presence and reported values for one relationship measurement."""

    omitted: int
    null: int
    missing: int
    zero: int
    nonzero: int
    reported: int


class InterchangeAnalysis(_Report):
    """Coverage over a single validated, content-identified P3IF graph."""

    framework_id: str
    semantic_sha256: str
    axes: tuple[AxisCoverage, ...]
    spaces: tuple[CoordinateCoverage, ...]
    strength: MetricCoverage
    confidence: MetricCoverage
    relationship_count: int


class InterchangeModification(_Report):
    """Changed wire fields on one retained identity and its rewire status."""

    id: str
    fields: tuple[str, ...]
    rewired: bool


class InterchangeChangeGroup(_Report):
    """Added, removed, and modified IDs in one dimension or relationship set."""

    kind: ChangeKind
    before_total: int
    after_total: int
    added: tuple[str, ...]
    removed: tuple[str, ...]
    modified: tuple[InterchangeModification, ...]


class InterchangeComparison(_Report):
    """Deterministic changes between two snapshots of the same framework."""

    framework_id: str
    before_sha256: str
    after_sha256: str
    framework_fields: tuple[str, ...]
    groups: tuple[InterchangeChangeGroup, ...]


def _metric_coverage(
    relationships: tuple[InterchangeRelationship, ...], metric: Metric
) -> MetricCoverage:
    omitted = null = zero = nonzero = 0
    for relationship in relationships:
        value = relationship.strength if metric == "strength" else relationship.confidence
        if metric not in relationship.model_fields_set:
            omitted += 1
        elif value is None:
            null += 1
        elif value == 0:
            zero += 1
        else:
            nonzero += 1
    return MetricCoverage(
        omitted=omitted,
        null=null,
        missing=omitted + null,
        zero=zero,
        nonzero=nonzero,
        reported=zero + nonzero,
    )


def analyze_interchange(model: Interchange) -> InterchangeAnalysis:
    """Count sparse links, coordinate coverage, and metric availability.

    Args:
        model: One validated P3IF interchange snapshot.

    Returns:
        A deterministic report with axis participation, exact pair and triple
        coverage, and score availability. Denominators are calculated from axis
        cardinalities without materializing the product.
    """
    identity = interchange_sha256(model)
    sizes: dict[Axis, int] = {
        "property": len(model.properties),
        "process": len(model.processes),
        "perspective": len(model.perspectives),
    }
    linked: dict[Axis, set[str]] = {axis: set() for axis in _AXES}
    coordinates: dict[tuple[Axis, ...], set[tuple[str, ...]]] = {space: set() for space in _SPACES}
    relations: dict[tuple[Axis, ...], int] = dict.fromkeys(_SPACES, 0)
    for relationship in model.relationships:
        axes: list[Axis] = []
        point: list[str] = []
        for index, endpoint in enumerate(relationship.endpoints()):
            if endpoint is not None:
                axis = _AXES[index]
                linked[axis].add(endpoint)
                axes.append(axis)
                point.append(endpoint)
        space = tuple(axes)
        coordinates[space].add(tuple(point))
        relations[space] += 1

    coverage: list[CoordinateCoverage] = []
    for space in _SPACES:
        possible = prod(sizes[axis] for axis in space)
        observed = len(coordinates[space])
        coverage.append(
            CoordinateCoverage(
                axes=space,
                relationships=relations[space],
                observed=observed,
                possible=possible,
                unobserved=possible - observed,
            )
        )

    return InterchangeAnalysis(
        framework_id=model.framework.id,
        semantic_sha256=identity,
        axes=tuple(
            AxisCoverage(
                axis=axis,
                total=sizes[axis],
                linked=len(linked[axis]),
                unlinked=sizes[axis] - len(linked[axis]),
            )
            for axis in _AXES
        ),
        spaces=tuple(coverage),
        strength=_metric_coverage(model.relationships, "strength"),
        confidence=_metric_coverage(model.relationships, "confidence"),
        relationship_count=len(model.relationships),
    )


def _changed_fields(before: BaseModel, after: BaseModel) -> tuple[str, ...]:
    left = cast("JSONMap", before.model_dump(mode="json", exclude_unset=True))
    right = cast("JSONMap", after.model_dump(mode="json", exclude_unset=True))
    # Python treats JSON booleans and numbers as equal. Compare their actual
    # encoded form so a type change in nested metadata survives the diff.
    return tuple(
        field
        for field in sorted(left.keys() | right.keys())
        if field not in left
        or field not in right
        or json.dumps(left[field], sort_keys=True) != json.dumps(right[field], sort_keys=True)
    )


def _collections(model: Interchange) -> dict[ChangeKind, Mapping[str, BaseModel]]:
    return {
        "property": {item.id: item for item in model.properties},
        "process": {item.id: item for item in model.processes},
        "perspective": {item.id: item for item in model.perspectives},
        "relationship": {item.id: item for item in model.relationships},
    }


def _compare_group(
    kind: ChangeKind, before: Mapping[str, BaseModel], after: Mapping[str, BaseModel]
) -> InterchangeChangeGroup:
    modified: list[InterchangeModification] = []
    for identity in sorted(before.keys() & after.keys()):
        left, right = before[identity], after[identity]
        if fields := _changed_fields(left, right):
            rewired = (
                isinstance(left, InterchangeRelationship)
                and isinstance(right, InterchangeRelationship)
                and left.endpoints() != right.endpoints()
            )
            modified.append(InterchangeModification(id=identity, fields=fields, rewired=rewired))
    return InterchangeChangeGroup(
        kind=kind,
        before_total=len(before),
        after_total=len(after),
        added=tuple(sorted(after.keys() - before.keys())),
        removed=tuple(sorted(before.keys() - after.keys())),
        modified=tuple(modified),
    )


def compare_interchange(before: Interchange, after: Interchange) -> InterchangeComparison:
    """Compare canonical P3IF snapshots by exact stable identities.

    Args:
        before: The earlier declared snapshot.
        after: The later declared snapshot with the same framework ID.

    Returns:
        Both canonical hashes, changed framework fields, and exact member and
        relationship changes. Rewiring means that a retained relationship ID
        has different endpoint IDs.

    Raises:
        InterchangeError: The snapshots belong to different frameworks.
    """
    if before.framework.id != after.framework.id:
        message = "P3IF comparison requires matching framework IDs"
        raise InterchangeError(message)
    before_sha256 = interchange_sha256(before)
    after_sha256 = interchange_sha256(after)
    left, right = _collections(before), _collections(after)
    return InterchangeComparison(
        framework_id=before.framework.id,
        before_sha256=before_sha256,
        after_sha256=after_sha256,
        framework_fields=_changed_fields(before.framework, after.framework),
        groups=tuple(_compare_group(kind, left[kind], right[kind]) for kind in _CHANGE_KINDS),
    )
