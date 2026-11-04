"""
Tests for High-Performance Compositional Indexing Engine (p3if.core.indexing).
"""
import pytest
from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective, Relationship
from p3if.core.indexing import CompositionalIndex, QueryPredicate


@pytest.fixture
def populated_index():
    """Create and return an indexed set of cross-domain patterns."""
    index = CompositionalIndex()

    p1 = Property(name="Security", domain="cyber", tags=["core", "defense"], description="Sec")
    p2 = Property(
        name="Privacy", domain="healthcare", tags=["core", "compliance"], description="Priv"
    )
    proc1 = Process(name="Authentication", domain="cyber", tags=["defense"], description="Auth")
    proc2 = Process(name="Diagnosis", domain="healthcare", tags=["clinical"], description="Diag")
    persp1 = Perspective(
        name="Auditor", domain="cyber", viewpoint="sec_ops", tags=["core"], description="Aud"
    )
    persp2 = Perspective(
        name="Doctor", domain="healthcare", viewpoint="clinical", tags=["care"], description="Doc"
    )

    for p in [p1, p2, proc1, proc2, persp1, persp2]:
        index.index_pattern(p)

    rel1 = Relationship(property_id=p1.id, process_id=proc1.id, strength=0.9, confidence=0.95)
    rel2 = Relationship(property_id=p2.id, process_id=proc2.id, strength=0.8, confidence=0.85)
    rel_cross = Relationship(property_id=p1.id, process_id=proc2.id, strength=0.6, confidence=0.7)

    for r in [rel1, rel2, rel_cross]:
        index.index_relationship(r)

    return index, [p1, p2, proc1, proc2, persp1, persp2]


def test_compositional_index_query_conjunction(populated_index):
    """Test AND conjunction across multiple dimensions."""
    index, patterns = populated_index

    # Query: domain=cyber AND tags=core
    results = index.query(domains=["cyber"], tags=["core"], operator="AND")
    ids = {p.id for p in results}
    assert ids == {patterns[0].id, patterns[4].id}  # Security and Auditor

    # Query: type=property AND domain=cyber
    prop_cyber = index.query(types=["property"], domains=["cyber"], operator="AND")
    assert len(prop_cyber) == 1
    assert prop_cyber[0].name == "Security"


def test_compositional_index_query_disjunction(populated_index):
    """Test OR disjunction across multiple dimensions."""
    index, patterns = populated_index

    results = index.query(domains=["cyber", "healthcare"], types=["process"], operator="OR")
    # All patterns in cyber OR healthcare OR process (covers all 6)
    assert len(results) == 6


def test_compositional_index_connected_patterns(populated_index):
    """Test fast lookup of connected patterns."""
    index, patterns = populated_index
    p1 = patterns[0]  # Security

    connected = index.find_connected_patterns(p1.id)
    connected_names = {p.name for p in connected}
    assert "Authentication" in connected_names
    assert "Diagnosis" in connected_names


def test_compositional_index_cross_domain_density(populated_index):
    """Test O(1) computation of cross-domain connection density."""
    index, _ = populated_index
    density = index.get_domain_cross_product_density("cyber", "healthcare")
    # 1 cross-domain link between 3 cyber and 3 healthcare patterns: 1 / 9
    assert density == pytest.approx(1.0 / 9.0)


def test_compositional_index_build_from_framework():
    """Test populating index from P3IFFramework."""
    fw = P3IFFramework()
    p = Property(name="Performance", domain="infra", description="Speed")
    proc = Process(name="Caching", domain="infra", description="Cache")
    fw.add_pattern(p)
    fw.add_pattern(proc)
    rel = Relationship(property_id=p.id, process_id=proc.id, strength=0.9, confidence=0.9)
    fw.add_relationship(rel)

    index = CompositionalIndex().build_from_framework(fw)
    assert len(index) == 2
    assert len(index.query(domains=["infra"])) == 2
    assert len(index.find_connected_patterns(p.id)) == 1


def test_query_predicate():
    """Test atomic QueryPredicate matching logic."""
    prop = Property(name="AuditLog", domain="security", priority="high", description="Logs")

    pred_eq = QueryPredicate("domain", "security", operator="eq")
    assert pred_eq.matches(prop) is True

    pred_neq = QueryPredicate("domain", "healthcare", operator="eq")
    assert pred_neq.matches(prop) is False

    pred_in = QueryPredicate("priority", ["high", "critical"], operator="in")
    assert pred_in.matches(prop) is True
