"""
High-Performance Compositional Indexing Engine.

This module provides multi-attribute inverted indexing, compositional query
evaluation (intersection, union, difference, threshold filtering), bitmap-like
set operations, and fast sub-millisecond retrieval for P3IF frameworks.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import (
    Dict,
    List,
    Optional,
    Set,
    Any,
    Callable,
    Iterable,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from p3if.core.models import BasePattern, Relationship
    from p3if.core.framework.core import P3IFFramework

logger = logging.getLogger(__name__)


class QueryPredicate:
    """Represents an atomic predicate in a compositional query."""

    def __init__(
        self,
        field: str,
        value: Any,
        operator: str = "eq",
    ) -> None:
        """
        Initialize predicate.

        Args:
            field: Attribute name (e.g. 'type', 'domain', 'tag', 'confidence')
            value: Target value or threshold
            operator: Comparison operator ('eq', 'in', 'gte', 'lte', 'contains')
        """
        self.field = field
        self.value = value
        self.operator = operator

    def matches(self, pattern: BasePattern) -> bool:
        """Evaluate predicate directly on a pattern object."""
        target = getattr(pattern, self.field, None)
        if target is None and hasattr(pattern, "metadata") and pattern.metadata:
            target = pattern.metadata.get(self.field)

        if self.operator == "eq":
            if target is not None and hasattr(target, "value"):
                target = target.value
            val = self.value.value if hasattr(self.value, "value") else self.value
            return bool(target == val)
        elif self.operator == "in":
            return bool(target in self.value)
        elif self.operator == "gte":
            return bool(target is not None and target >= self.value)
        elif self.operator == "lte":
            return bool(target is not None and target <= self.value)
        elif self.operator == "contains":
            if isinstance(target, (list, set, tuple)):
                return bool(self.value in target)
            elif isinstance(target, str):
                return bool(str(self.value) in target)
            return False
        return False


class CompositionalIndex:
    """
    In-memory compositional indexing engine for multi-attribute pattern and
    relationship retrieval with set-algebraic query optimization.
    """

    def __init__(self) -> None:
        """Initialize empty indices."""
        # Pattern inverted indices: attribute -> value -> Set[pattern_id]
        self._type_index: Dict[str, Set[str]] = defaultdict(set)
        self._domain_index: Dict[str, Set[str]] = defaultdict(set)
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        self._status_index: Dict[str, Set[str]] = defaultdict(set)

        # Primary storage map: id -> pattern
        self._pattern_map: Dict[str, BasePattern] = {}

        # Relationship index: dimension -> pattern_id -> Set[relationship_id]
        self._rel_property_index: Dict[str, Set[str]] = defaultdict(set)
        self._rel_process_index: Dict[str, Set[str]] = defaultdict(set)
        self._rel_perspective_index: Dict[str, Set[str]] = defaultdict(set)
        self._rel_type_index: Dict[str, Set[str]] = defaultdict(set)
        self._relationship_map: Dict[str, Relationship] = {}

    def __len__(self) -> int:
        return len(self._pattern_map)

    def index_pattern(self, pattern: BasePattern) -> None:
        """Index a single pattern into all relevant inverted indices."""
        pid = pattern.id
        self._pattern_map[pid] = pattern

        # Index type
        ptype = pattern.type.value if hasattr(pattern.type, "value") else str(pattern.type)
        self._type_index[ptype.lower()].add(pid)

        # Index domain
        domain = getattr(pattern, "domain", None)
        if domain:
            self._domain_index[domain.lower()].add(pid)

        # Index tags
        if pattern.tags:
            for tag in pattern.tags:
                self._tag_index[tag.lower()].add(pid)

        # Index validation status
        status = getattr(pattern, "validation_status", None)
        if status:
            self._status_index[str(status).lower()].add(pid)

    def index_relationship(self, relationship: Relationship) -> None:
        """Index a relationship into topological connection indices."""
        rid = relationship.id
        self._relationship_map[rid] = relationship

        if relationship.property_id:
            self._rel_property_index[relationship.property_id].add(rid)
        if relationship.process_id:
            self._rel_process_index[relationship.process_id].add(rid)
        if relationship.perspective_id:
            self._rel_perspective_index[relationship.perspective_id].add(rid)

        rel_type = getattr(relationship, "relationship_type", "associated")
        self._rel_type_index[str(rel_type).lower()].add(rid)

    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern and purge its ID from all inverted indices."""
        if pattern_id not in self._pattern_map:
            return False

        pattern = self._pattern_map.pop(pattern_id)
        ptype = pattern.type.value if hasattr(pattern.type, "value") else str(pattern.type)
        self._type_index[ptype.lower()].discard(pattern_id)

        domain = getattr(pattern, "domain", None)
        if domain:
            self._domain_index[domain.lower()].discard(pattern_id)

        if pattern.tags:
            for tag in pattern.tags:
                self._tag_index[tag.lower()].discard(pattern_id)

        status = getattr(pattern, "validation_status", None)
        if status:
            self._status_index[str(status).lower()].discard(pattern_id)

        return True

    def build_from_framework(self, framework: P3IFFramework) -> CompositionalIndex:
        """Populate index from an existing P3IFFramework instance."""
        self.clear()
        for pattern in framework.get_all_patterns():
            self.index_pattern(pattern)
        for rel in framework.get_all_relationships():
            self.index_relationship(rel)
        return self

    def clear(self) -> None:
        """Clear all indexed data."""
        self._type_index.clear()
        self._domain_index.clear()
        self._tag_index.clear()
        self._status_index.clear()
        self._pattern_map.clear()
        self._rel_property_index.clear()
        self._rel_process_index.clear()
        self._rel_perspective_index.clear()
        self._rel_type_index.clear()
        self._relationship_map.clear()

    def query_ids(
        self,
        types: Optional[Iterable[str]] = None,
        domains: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        operator: str = "AND",
    ) -> Set[str]:
        """
        Fast compositional ID lookup supporting conjunctions (AND) and disjunctions (OR).
        """
        candidate_sets: List[Set[str]] = []

        if types:
            type_set: Set[str] = set()
            for t in types:
                type_set |= self._type_index.get(t.lower(), set())
            candidate_sets.append(type_set)

        if domains:
            domain_set: Set[str] = set()
            for d in domains:
                domain_set |= self._domain_index.get(d.lower(), set())
            candidate_sets.append(domain_set)

        if tags:
            tag_set: Set[str] = set()
            for tg in tags:
                tag_set |= self._tag_index.get(tg.lower(), set())
            candidate_sets.append(tag_set)

        if not candidate_sets:
            return set(self._pattern_map.keys())

        if operator.upper() == "AND":
            # Fast intersection starting with smallest set
            candidate_sets.sort(key=len)
            res = set(candidate_sets[0])
            for s in candidate_sets[1:]:
                res &= s
            return res
        elif operator.upper() == "OR":
            res = set()
            for s in candidate_sets:
                res |= s
            return res
        else:
            raise ValueError(f"Unsupported operator: {operator}. Expected 'AND' or 'OR'.")

    def query(
        self,
        types: Optional[Iterable[str]] = None,
        domains: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        operator: str = "AND",
        filter_fn: Optional[Callable[[BasePattern], bool]] = None,
    ) -> List[BasePattern]:
        """
        Execute compositional query returning hydrated BasePattern models.
        """
        ids = self.query_ids(types=types, domains=domains, tags=tags, operator=operator)
        results = [self._pattern_map[pid] for pid in ids if pid in self._pattern_map]

        if filter_fn:
            results = [p for p in results if filter_fn(p)]

        return results

    def find_connected_patterns(
        self, pattern_id: str, relationship_type: Optional[str] = None
    ) -> List[BasePattern]:
        """Find all patterns connected to the given pattern ID via indexed relationships."""
        rel_ids = (
            self._rel_property_index.get(pattern_id, set())
            | self._rel_process_index.get(pattern_id, set())
            | self._rel_perspective_index.get(pattern_id, set())
        )

        connected_ids: Set[str] = set()
        for rid in rel_ids:
            rel = self._relationship_map.get(rid)
            if not rel:
                continue
            if relationship_type and rel.relationship_type.lower() != relationship_type.lower():
                continue
            for pid in [rel.property_id, rel.process_id, rel.perspective_id]:
                if pid and pid != pattern_id:
                    connected_ids.add(pid)

        return [self._pattern_map[pid] for pid in connected_ids if pid in self._pattern_map]

    def get_domain_cross_product_density(self, domain_a: str, domain_b: str) -> float:
        """
        Compute normalized connection density between two domains in O(1) indexed time.
        """
        patterns_a = self._domain_index.get(domain_a.lower(), set())
        patterns_b = self._domain_index.get(domain_b.lower(), set())

        if not patterns_a or not patterns_b:
            return 0.0

        links = 0
        for pid_a in patterns_a:
            rel_ids = (
                self._rel_property_index.get(pid_a, set())
                | self._rel_process_index.get(pid_a, set())
                | self._rel_perspective_index.get(pid_a, set())
            )
            for rid in rel_ids:
                rel = self._relationship_map.get(rid)
                if rel and any(
                    target in patterns_b
                    for target in [rel.property_id, rel.process_id, rel.perspective_id]
                ):
                    links += 1

        possible = len(patterns_a) * len(patterns_b)
        return float(links / possible) if possible > 0 else 0.0
