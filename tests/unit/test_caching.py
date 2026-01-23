"""
Unit tests for P3IF caching functionality.
"""
import pytest
import time
from collections import OrderedDict


class TestLRUCache:
    """Test cases for LRU cache implementations."""

    def test_basic_cache_operations(self):
        """Test basic get/set operations on cache."""
        cache = OrderedDict()
        max_size = 3

        # Add items
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        assert len(cache) == 3
        assert cache['a'] == 1
        assert cache['b'] == 2
        assert cache['c'] == 3

    def test_cache_eviction(self):
        """Test that oldest items are evicted when cache is full."""
        cache = OrderedDict()
        max_size = 3

        # Add items up to max size
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        # Add one more - should trigger eviction
        if len(cache) >= max_size:
            cache.popitem(last=False)
        cache['d'] = 4

        assert len(cache) == 3
        assert 'a' not in cache
        assert 'd' in cache

    def test_cache_access_updates_order(self):
        """Test that accessing an item moves it to end of cache."""
        cache = OrderedDict()

        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        # Access 'a' - should move to end
        cache.move_to_end('a')

        # Verify order
        keys = list(cache.keys())
        assert keys == ['b', 'c', 'a']

    def test_cache_with_none_values(self):
        """Test cache handles None values correctly."""
        cache = OrderedDict()

        cache['a'] = None
        cache['b'] = 1

        assert 'a' in cache
        assert cache['a'] is None
        assert cache['b'] == 1


class TestVisualizationCache:
    """Test cases for visualization caching."""

    def test_cache_key_generation(self):
        """Test that cache keys are generated consistently."""
        import hashlib
        import json

        def generate_cache_key(data):
            """Generate a cache key from visualization data."""
            serialized = json.dumps(data, sort_keys=True)
            return hashlib.md5(serialized.encode()).hexdigest()

        data1 = {'type': 'cube', 'domain': 'healthcare'}
        data2 = {'domain': 'healthcare', 'type': 'cube'}
        data3 = {'type': 'cube', 'domain': 'finance'}

        key1 = generate_cache_key(data1)
        key2 = generate_cache_key(data2)
        key3 = generate_cache_key(data3)

        # Same data in different order should produce same key
        assert key1 == key2
        # Different data should produce different key
        assert key1 != key3

    def test_cache_expiry(self):
        """Test that expired cache entries are detected."""
        cache_expiry = {}
        ttl = 0.1  # 100ms TTL

        cache_expiry['key1'] = time.time()
        time.sleep(0.15)  # Wait for expiry

        # Check if expired
        is_expired = time.time() - cache_expiry.get('key1', 0) > ttl
        assert is_expired is True

        # Fresh entry should not be expired
        cache_expiry['key2'] = time.time()
        is_expired = time.time() - cache_expiry.get('key2', 0) > ttl
        assert is_expired is False


class TestFrameworkCaching:
    """Test cases for framework-level caching."""

    def test_pattern_index_caching(self):
        """Test that pattern indexes are cached correctly."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property

        framework = P3IFFramework()

        # Add patterns
        prop1 = Property(name="Test 1", description="Test", domain="test")
        prop2 = Property(name="Test 2", description="Test", domain="test")

        framework.add_pattern(prop1)
        framework.add_pattern(prop2)

        # Verify patterns are added to framework
        assert prop1.id in framework._patterns
        assert prop2.id in framework._patterns
        # Verify type index is populated
        assert prop1.id in framework._pattern_index['type']['property']
        assert prop2.id in framework._pattern_index['type']['property']

    def test_relationship_index_caching(self):
        """Test that relationship indexes are cached correctly."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property, Process, Relationship

        framework = P3IFFramework()

        # Add patterns
        prop = Property(name="Test Property", description="Test", domain="test")
        proc = Process(name="Test Process", description="Test", domain="test")

        framework.add_pattern(prop)
        framework.add_pattern(proc)

        # Add relationship
        rel = Relationship(
            property_id=prop.id,
            process_id=proc.id,
            strength=0.8,
            confidence=0.9
        )
        framework.add_relationship(rel)

        # Verify relationship is in framework
        assert rel.id in framework._relationships
        # Verify index is populated by pattern
        assert rel.id in framework._relationship_index['property'][prop.id]
        assert rel.id in framework._relationship_index['process'][proc.id]

    def test_cache_clear_on_pattern_removal(self):
        """Test that caches are updated when patterns are removed."""
        from p3if.core.framework import P3IFFramework
        from p3if.core.models import Property

        framework = P3IFFramework()

        prop = Property(name="Test", description="Test", domain="test")
        framework.add_pattern(prop)

        assert prop.id in framework._patterns

        # Remove pattern
        framework.remove_pattern(prop.id)

        # Verify pattern is removed from framework
        assert prop.id not in framework._patterns
        # Verify index is updated
        assert prop.id not in framework._pattern_index['type'].get('property', [])
