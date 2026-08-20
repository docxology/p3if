"""
Tests for asynchronous pattern and relationship storage and framework operations (A2).
"""
import pytest
import asyncio
from p3if.core.framework import P3IFFramework
from p3if.core.models import Property, Process, Perspective, Relationship
from p3if.utils.storage import JSONStorage, SQLiteStorage


@pytest.fixture
def tmp_json_storage(tmp_path):
    storage_file = tmp_path / "async_storage.json"
    return JSONStorage(storage_file)


@pytest.fixture
def tmp_sqlite_storage(tmp_path):
    storage_file = tmp_path / "async_storage.db"
    return SQLiteStorage(storage_file)


@pytest.mark.asyncio
async def test_json_storage_async_pattern_operations(tmp_json_storage):
    """Test asynchronous pattern save, get, and delete in JSONStorage."""
    prop = Property(name="Async Prop", domain="tech", description="Async test property")

    await tmp_json_storage.save_pattern_async(prop)
    retrieved = await tmp_json_storage.get_pattern_async(prop.id)
    assert retrieved is not None
    assert retrieved.name == "Async Prop"

    patterns = await tmp_json_storage.get_patterns_by_type_async("property")
    assert len(patterns) == 1
    assert patterns[0].id == prop.id

    deleted = await tmp_json_storage.delete_pattern_async(prop.id)
    assert deleted is True

    retrieved_after_delete = await tmp_json_storage.get_pattern_async(prop.id)
    assert retrieved_after_delete is None


@pytest.mark.asyncio
async def test_json_storage_async_relationship_operations(tmp_json_storage):
    """Test asynchronous relationship save, get, and delete in JSONStorage."""
    prop = Property(name="Prop1", domain="test", description="P1")
    proc = Process(name="Proc1", domain="test", description="Pr1")
    rel = Relationship(property_id=prop.id, process_id=proc.id, strength=0.8, confidence=0.9)

    await tmp_json_storage.save_relationship_async(rel)
    retrieved = await tmp_json_storage.get_relationship_async(rel.id)
    assert retrieved is not None
    assert retrieved.strength == 0.8

    deleted = await tmp_json_storage.delete_relationship_async(rel.id)
    assert deleted is True

    cleared = await tmp_json_storage.get_relationship_async(rel.id)
    assert cleared is None


@pytest.mark.asyncio
async def test_sqlite_storage_async_operations(tmp_sqlite_storage):
    """Test asynchronous pattern and relationship operations in SQLiteStorage."""
    persp = Perspective(
        name="Stakeholder", domain="biz", viewpoint="business", description="Biz perspective"
    )
    await tmp_sqlite_storage.save_pattern_async(persp)

    retrieved = await tmp_sqlite_storage.get_pattern_async(persp.id)
    assert retrieved is not None
    assert retrieved.name == "Stakeholder"

    patterns = await tmp_sqlite_storage.get_patterns_by_type_async("perspective")
    assert len(patterns) == 1

    await tmp_sqlite_storage.clear_async()
    assert await tmp_sqlite_storage.get_pattern_async(persp.id) is None


@pytest.mark.asyncio
async def test_framework_async_methods():
    """Test P3IFFramework asynchronous add_pattern_async and add_relationship_async."""
    fw = P3IFFramework()
    prop = Property(name="Async Core Prop", domain="general", description="Testing async framework")
    proc = Process(name="Async Core Proc", domain="general", description="Testing async process")

    # Add concurrently using asyncio.gather
    p1_id, p2_id = await asyncio.gather(
        fw.add_pattern_async(prop),
        fw.add_pattern_async(proc),
    )

    assert p1_id == prop.id
    assert p2_id == proc.id
    assert len(fw.get_patterns_by_domain("general")) == 2

    rel = Relationship(property_id=p1_id, process_id=p2_id, strength=0.85, confidence=0.95)
    rel_id = await fw.add_relationship_async(rel)

    assert rel_id == rel.id
    assert len(fw.get_relationships_by_pattern(p1_id)) == 1
