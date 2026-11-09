"""Project P3IF changes onto stable coordinates shared by two snapshots.

The report preserves the caller's snapshot order and each declared endpoint.
Missing endpoints stay null. The report carries no timestamps or implied
relationships and does not materialize the Cartesian product of the axes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal

from pydantic import BaseModel, ConfigDict

from .interchange import Nullable
from .interchange_analysis import compare_interchange

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .interchange import Interchange, InterchangeRelationship
    from .interchange_analysis import ChangeKind, InterchangeChangeGroup

TransitionKind = Literal["framework", "property", "process", "perspective", "relationship"]
TransitionChange = Literal["added", "removed", "modified"]
Coordinate = tuple[Nullable[str], Nullable[str], Nullable[str]]

_REPORT_CONFIG = ConfigDict(extra="forbid", frozen=True, strict=True)


class TransitionAxes(BaseModel):
    """Sorted unions of the identities declared on each axis."""

    model_config: ClassVar[ConfigDict] = _REPORT_CONFIG

    properties: tuple[str, ...]
    processes: tuple[str, ...]
    perspectives: tuple[str, ...]


class TransitionEvent(BaseModel):
    """One stable identity change and its declared coordinate at each stage."""

    model_config: ClassVar[ConfigDict] = _REPORT_CONFIG

    kind: TransitionKind
    id: str
    change: TransitionChange
    fields: tuple[str, ...]
    rewired: bool
    before: Nullable[Coordinate]
    after: Nullable[Coordinate]


class InterchangeTransition(BaseModel):
    """Ordered snapshot identities and their sparse coordinate changes."""

    model_config: ClassVar[ConfigDict] = _REPORT_CONFIG

    framework_id: str
    before_sha256: str
    after_sha256: str
    axes: TransitionAxes
    events: tuple[TransitionEvent, ...]


def _coordinate(
    kind: ChangeKind, identity: str, relationships: Mapping[str, InterchangeRelationship]
) -> Coordinate:
    if kind == "relationship":
        return relationships[identity].endpoints()
    return (
        identity if kind == "property" else None,
        identity if kind == "process" else None,
        identity if kind == "perspective" else None,
    )


def _group_events(
    group: InterchangeChangeGroup,
    before: Mapping[str, InterchangeRelationship],
    after: Mapping[str, InterchangeRelationship],
) -> list[TransitionEvent]:
    added = set(group.added)
    removed = set(group.removed)
    modified = {entry.id: entry for entry in group.modified}
    events: list[TransitionEvent] = []
    for identity in sorted(added | removed | modified.keys()):
        operation: TransitionChange
        if identity in added:
            operation = "added"
        elif identity in removed:
            operation = "removed"
        else:
            operation = "modified"
        modification = modified.get(identity)
        events.append(
            TransitionEvent(
                kind=group.kind,
                id=identity,
                change=operation,
                fields=modification.fields if modification is not None else (),
                rewired=modification is not None and modification.rewired,
                before=None if operation == "added" else _coordinate(group.kind, identity, before),
                after=None if operation == "removed" else _coordinate(group.kind, identity, after),
            )
        )
    return events


def transition_interchange(before: Interchange, after: Interchange) -> InterchangeTransition:
    """Describe the declared coordinate changes between two P3IF snapshots.

    Args:
        before: The snapshot to display at the first stage.
        after: The snapshot to display at the second stage.

    Returns:
        Both canonical hashes, shared axis identities, and deterministic change
        events. Event ordering is by kind and then stable ID. A whole null
        coordinate means that the record is absent on that side.

    Raises:
        InterchangeError: The snapshots have different framework identities.
    """
    comparison = compare_interchange(before, after)
    axes = TransitionAxes(
        properties=tuple(sorted({item.id for item in (*before.properties, *after.properties)})),
        processes=tuple(sorted({item.id for item in (*before.processes, *after.processes)})),
        perspectives=tuple(
            sorted({item.id for item in (*before.perspectives, *after.perspectives)})
        ),
    )
    events: list[TransitionEvent] = []
    if comparison.framework_fields:
        events.append(
            TransitionEvent(
                kind="framework",
                id=comparison.framework_id,
                change="modified",
                fields=comparison.framework_fields,
                rewired=False,
                before=(None, None, None),
                after=(None, None, None),
            )
        )
    earlier_links = {item.id: item for item in before.relationships}
    later_links = {item.id: item for item in after.relationships}
    for group in comparison.groups:
        events.extend(_group_events(group, earlier_links, later_links))
    return InterchangeTransition(
        framework_id=comparison.framework_id,
        before_sha256=comparison.before_sha256,
        after_sha256=comparison.after_sha256,
        axes=axes,
        events=tuple(events),
    )
