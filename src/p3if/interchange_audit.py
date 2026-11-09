"""Produce a deterministic audit of two exact, ordered P3IF interchange files.

The report separates byte-level changes, semantic changes, and structural
measurements. Its signed deltas describe the supplied declarations. They do
not measure causal effects, evidence quality, or reviewer authority.
"""

from __future__ import annotations

from hashlib import sha256
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict

from .interchange import InterchangeError, load_interchange
from .interchange_analysis import (
    Axis,
    AxisCoverage,
    CoordinateCoverage,
    InterchangeAnalysis,
    MetricCoverage,
    analyze_interchange,
    compare_interchange,
)

_AUDIT_CONFIG = ConfigDict(extra="forbid", frozen=True, strict=True)
AuditClassification = Literal["identical_bytes", "encoding_only", "declared_change"]
AuditKind = Literal["framework", "property", "process", "perspective", "relationship"]


class _AuditModel(BaseModel):
    model_config: ClassVar[ConfigDict] = _AUDIT_CONFIG


class AuditSnapshot(_AuditModel):
    """Exact transport identity and analytical description of one input."""

    source_sha256: str
    source_bytes: int
    analysis: InterchangeAnalysis


class AxisDelta(_AuditModel):
    """Signed after-minus-before changes in axis participation."""

    axis: Axis
    total: int
    linked: int
    unlinked: int


class CoordinateDelta(_AuditModel):
    """Signed changes in one exact pair or triple coordinate space."""

    axes: tuple[Axis, ...]
    relationships: int
    observed: int
    possible: int
    unobserved: int


class MetricDelta(_AuditModel):
    """Signed changes in one relationship score's presence and value categories."""

    omitted: int
    null: int
    missing: int
    zero: int
    nonzero: int
    reported: int


class ChangeCounts(_AuditModel):
    """Stable-ID changes for one declaration kind."""

    kind: AuditKind
    added: int = 0
    removed: int = 0
    modified: int = 0
    rewired: int = 0


class InterchangeAudit(_AuditModel):
    """A versioned reproducibility receipt for an ordered snapshot comparison."""

    method: Literal["p3if.snapshot-audit.v1"] = "p3if.snapshot-audit.v1"
    framework_id: str
    classification: AuditClassification
    before: AuditSnapshot
    after: AuditSnapshot
    framework_fields: tuple[str, ...]
    changes: tuple[ChangeCounts, ...]
    axes: tuple[AxisDelta, ...]
    coordinates: tuple[CoordinateDelta, ...]
    strength: MetricDelta
    confidence: MetricDelta
    relationship_delta: int


def _axis_delta(left: AxisCoverage, right: AxisCoverage) -> AxisDelta:
    return AxisDelta(
        axis=left.axis,
        total=right.total - left.total,
        linked=right.linked - left.linked,
        unlinked=right.unlinked - left.unlinked,
    )


def _coordinate_delta(left: CoordinateCoverage, right: CoordinateCoverage) -> CoordinateDelta:
    return CoordinateDelta(
        axes=left.axes,
        relationships=right.relationships - left.relationships,
        observed=right.observed - left.observed,
        possible=right.possible - left.possible,
        unobserved=right.unobserved - left.unobserved,
    )


def _metric_delta(before: MetricCoverage, after: MetricCoverage) -> MetricDelta:
    return MetricDelta(
        omitted=after.omitted - before.omitted,
        null=after.null - before.null,
        missing=after.missing - before.missing,
        zero=after.zero - before.zero,
        nonzero=after.nonzero - before.nonzero,
        reported=after.reported - before.reported,
    )


def audit_interchange(before: bytes, after: bytes) -> InterchangeAudit:
    """Audit exact input bytes and describe reproducible structural changes.

    Args:
        before: Exact UTF-8 bytes of the first v1 interchange.
        after: Exact UTF-8 bytes of the second v1 interchange.

    Returns:
        A deterministic receipt with both byte and semantic identities, analyses,
        change counts, and signed after-minus-before deltas.

    Raises:
        InterchangeError: An input is invalid or framework IDs differ.
    """
    first = load_interchange(before)
    same_bytes = before == after
    second = first if same_bytes else load_interchange(after)
    if first.framework.id != second.framework.id:
        message = "P3IF audit requires matching framework IDs"
        raise InterchangeError(message)

    earlier = analyze_interchange(first)
    later = earlier if same_bytes else analyze_interchange(second)
    classification: AuditClassification
    framework_fields: tuple[str, ...] = ()
    changes: tuple[ChangeCounts, ...]
    if earlier.semantic_sha256 != later.semantic_sha256:
        classification = "declared_change"
        delta = compare_interchange(first, second)
        framework_fields = delta.framework_fields
        changes = (
            ChangeCounts(kind="framework", modified=int(bool(framework_fields))),
            *(
                ChangeCounts(
                    kind=group.kind,
                    added=len(group.added),
                    removed=len(group.removed),
                    modified=len(group.modified),
                    rewired=sum(item.rewired for item in group.modified),
                )
                for group in delta.groups
            ),
        )
    else:
        classification = "identical_bytes" if same_bytes else "encoding_only"
        changes = (
            ChangeCounts(kind="framework"),
            ChangeCounts(kind="property"),
            ChangeCounts(kind="process"),
            ChangeCounts(kind="perspective"),
            ChangeCounts(kind="relationship"),
        )

    before_source = sha256(before).hexdigest()
    return InterchangeAudit(
        framework_id=first.framework.id,
        classification=classification,
        before=AuditSnapshot(
            source_sha256=before_source, source_bytes=len(before), analysis=earlier
        ),
        after=AuditSnapshot(
            source_sha256=before_source if same_bytes else sha256(after).hexdigest(),
            source_bytes=len(after),
            analysis=later,
        ),
        framework_fields=framework_fields,
        changes=changes,
        axes=tuple(map(_axis_delta, earlier.axes, later.axes)),
        coordinates=tuple(map(_coordinate_delta, earlier.spaces, later.spaces)),
        strength=_metric_delta(earlier.strength, later.strength),
        confidence=_metric_delta(earlier.confidence, later.confidence),
        relationship_delta=later.relationship_count - earlier.relationship_count,
    )
