"""
P3IF Core Framework - Enhanced Version

This module contains the enhanced main P3IF framework class with improved
performance, validation, and analysis capabilities.
"""
from typing import Dict, List, Optional, Union, Any, Tuple, Set, Iterator
import json
import logging
import asyncio
import os
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter
from dataclasses import dataclass
import sys
import hashlib
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor

# Add the project root to the path if this module is run directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from core.models import (
    Property, Process, Perspective, Relationship, BasePattern,
    PatternType, PatternCollection, RelationshipAnalysis, MetadataMixin
)
from utils.storage import StorageInterface
from utils.config import Config
from utils.performance import (
    get_performance_monitor, get_cache, performance_timer,
    cached, memoize, performance_context, LRUCache
)


@dataclass
class FrameworkMetrics:
    """Framework performance and usage metrics."""
    total_patterns: int
    total_relationships: int
    average_relationship_strength: float
    average_confidence: float
    domain_count: int
    pattern_types_count: Dict[str, int]
    relationship_types_count: Dict[str, int]
    orphaned_patterns: int
    deprecated_patterns: int
    validation_issues: int


class P3IFFramework(MetadataMixin):
    """
    Enhanced P3IF framework class with improved performance, validation, and analysis.

    This class provides comprehensive functionality for working with P3IF data:
    - Advanced pattern and relationship management
    - Performance-optimized operations with caching
    - Comprehensive validation and quality checks
    - Advanced analysis and metrics
    - Concurrent processing support
    - Enhanced import/export capabilities
    """

    def __init__(self, storage_backend: Optional[StorageInterface] = None,
                 config: Optional[Config] = None):
        """
        Initialize an enhanced P3IF framework instance.
        
        Args:
            storage_backend: Optional storage backend implementation
            config: Optional configuration object
        """
        self.logger = logging.getLogger(__name__)
        self._storage = storage_backend
        self._config = config or Config()
        
        # Core data structures with thread safety
        self._lock = threading.RLock()
        self._patterns: Dict[str, BasePattern] = {}
        self._relationships: Dict[str, Relationship] = {}
        
        # Enhanced indexing for performance
        self._pattern_index: Dict[str, Dict[str, List[str]]] = {
            'domain': defaultdict(list),
            'type': defaultdict(list),
            'tags': defaultdict(list),
            'status': defaultdict(list)
        }
        self._relationship_index: Dict[str, Dict[str, List[str]]] = {
            'property': defaultdict(list),
            'process': defaultdict(list),
            'perspective': defaultdict(list),
            'type': defaultdict(list),
            'status': defaultdict(list)
        }

        # Enhanced caching with performance monitoring
        self._metrics_cache: Optional[FrameworkMetrics] = None
        self._metrics_cache_time: Optional[datetime] = None
        self._cache_timeout = 300  # 5 minutes

        # Performance monitoring and optimization
        self._performance_monitor = get_performance_monitor()
        self._local_cache = LRUCache(max_size=500, default_ttl=600)  # 10 minutes
        self._query_cache = LRUCache(max_size=200, default_ttl=300)   # 5 minutes

        # Batch operations for performance
        self._batch_operations: List[Callable] = []
        self._batch_mode = False
        self._batch_size_threshold = 100

        # Thread pool for concurrent operations (optimized)
        self._executor = ThreadPoolExecutor(
            max_workers=min(8, (os.cpu_count() or 4) * 2),
            thread_name_prefix="p3if"
        )

        # Initialize metadata
        self.metadata = {
            'created_at': datetime.now(timezone.utc),
            'version': '2.0.0',
            'framework_type': 'enhanced_p3if'
        }

    def _update_indexes(self, pattern: Optional[BasePattern] = None,
                       relationship: Optional[Relationship] = None) -> None:
        """Update internal indexes for fast lookups."""
        with self._lock:
            if pattern:
                # Update pattern indexes
                if pattern.domain:
                    self._pattern_index['domain'][pattern.domain].append(pattern.id)
                self._pattern_index['type'][pattern.type.value].append(pattern.id)
                self._pattern_index['status'][pattern.validation_status].append(pattern.id)

                for tag in pattern.tags:
                    self._pattern_index['tags'][tag].append(pattern.id)

            if relationship:
                # Update relationship indexes
                if relationship.property_id:
                    self._relationship_index['property'][relationship.property_id].append(relationship.id)
                if relationship.process_id:
                    self._relationship_index['process'][relationship.process_id].append(relationship.id)
                if relationship.perspective_id:
                    self._relationship_index['perspective'][relationship.perspective_id].append(relationship.id)

                self._relationship_index['type'][relationship.relationship_type].append(relationship.id)
                self._relationship_index['status'][relationship.status].append(relationship.id)
    
    def add_pattern(self, pattern: BasePattern) -> str:
        """
        Add a pattern to the framework with validation and indexing.
        
        Args:
            pattern: The pattern to add
            
        Returns:
            The ID of the added pattern

        Raises:
            ValueError: If pattern validation fails or duplicate ID exists
        """
        with self._lock:
            # Validate pattern
            if pattern.id in self._patterns:
                raise ValueError(f"Pattern with ID {pattern.id} already exists")

            # Additional validation
            if pattern.is_deprecated():
                self.logger.warning(f"Adding deprecated pattern: {pattern.name}")

            # Add pattern
        self._patterns[pattern.id] = pattern

        # Update indexes
        self._update_indexes(pattern=pattern)

            # Persist if storage is available
        if self._storage:
            self._storage.save_pattern(pattern)

            # Invalidate cache
            self._invalidate_metrics_cache()

            self.logger.info(f"Added pattern: {pattern.name} ({pattern.id})")
        return pattern.id
        
    def get_pattern(self, pattern_id: str) -> Optional[BasePattern]:
        """
        Retrieve a pattern by ID with fast lookup.
        
        Args:
            pattern_id: The ID of the pattern to retrieve
            
        Returns:
            The pattern, or None if not found
        """
        with self._lock:
            return self._patterns.get(pattern_id)
    
    def get_patterns_by_type(self, pattern_type: Union[str, PatternType]) -> List[BasePattern]:
        """
        Retrieve all patterns of a specific type using indexing.
        
        Args:
            pattern_type: The type of patterns to retrieve
            
        Returns:
            A list of patterns of the specified type
        """
        with self._lock:
            if isinstance(pattern_type, PatternType):
                pattern_type = pattern_type.value

            pattern_ids = self._pattern_index['type'].get(pattern_type, [])
            return [self._patterns[pid] for pid in pattern_ids if pid in self._patterns]

    def get_patterns_by_domain(self, domain: str) -> List[BasePattern]:
        """
        Retrieve all patterns in a specific domain.

        Args:
            domain: Domain name

        Returns:
            List of patterns in the domain
        """
        with self._lock:
            pattern_ids = self._pattern_index['domain'].get(domain, [])
            return [self._patterns[pid] for pid in pattern_ids if pid in self._patterns]

    def get_patterns_by_tag(self, tag: str) -> List[BasePattern]:
        """
        Retrieve all patterns with a specific tag.

        Args:
            tag: Tag name

        Returns:
            List of patterns with the tag
        """
        with self._lock:
            pattern_ids = self._pattern_index['tags'].get(tag.lower(), [])
            return [self._patterns[pid] for pid in pattern_ids if pid in self._patterns]

    def search_patterns(self, query: str, limit: int = 50) -> List[BasePattern]:
        """
        Search patterns by name, description, or tags.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching patterns
        """
        with self._lock:
            query_lower = query.lower()
            results = []

            for pattern in self._patterns.values():
                # Search in name, description, and tags
                searchable_text = f"{pattern.name} {pattern.description or ''} {' '.join(pattern.tags)}".lower()

                if query_lower in searchable_text:
                    results.append(pattern)
                    if len(results) >= limit:
                        break

            return results
    
    def add_relationship(self, relationship: Relationship) -> str:
        """
        Add a relationship with comprehensive validation and indexing.
        
        Args:
            relationship: The relationship to add
            
        Returns:
            The ID of the added relationship

        Raises:
            ValueError: If relationship validation fails
        """
        with self._lock:
            # Validate relationship
            if relationship.id in self._relationships:
                raise ValueError(f"Relationship with ID {relationship.id} already exists")

            # Check that connected patterns exist
            for pattern_id in relationship.get_connected_patterns():
                if pattern_id not in self._patterns:
                    raise ValueError(f"Referenced pattern {pattern_id} does not exist")

            # Add relationship
        self._relationships[relationship.id] = relationship

        # Update indexes
        self._update_indexes(relationship=relationship)

        # Persist if storage is available
        if self._storage:
            self._storage.save_relationship(relationship)

        # Invalidate cache
        self._invalidate_metrics_cache()

        self.logger.info(f"Added relationship: {relationship.id}")
        return relationship.id
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Retrieve a relationship by ID.
        
        Args:
            relationship_id: The ID of the relationship to retrieve
            
        Returns:
            The relationship, or None if not found
        """
        with self._lock:
            return self._relationships.get(relationship_id)

    def get_relationships_by_pattern(self, pattern_id: str) -> List[Relationship]:
        """
        Get all relationships involving a specific pattern.

        Args:
            pattern_id: ID of the pattern

        Returns:
            List of relationships involving the pattern
        """
        with self._lock:
            relationship_ids = (
                self._relationship_index['property'].get(pattern_id, []) +
                self._relationship_index['process'].get(pattern_id, []) +
                self._relationship_index['perspective'].get(pattern_id, [])
            )
            return [self._relationships[rid] for rid in relationship_ids if rid in self._relationships]

    def get_relationships_by_type(self, relationship_type: str) -> List[Relationship]:
        """
        Get all relationships of a specific type.

        Args:
            relationship_type: Type of relationship

        Returns:
            List of relationships of the specified type
        """
        with self._lock:
            relationship_ids = self._relationship_index['type'].get(relationship_type, [])
            return [self._relationships[rid] for rid in relationship_ids if rid in self._relationships]

    def remove_pattern(self, pattern_id: str) -> bool:
        """
        Remove a pattern and all its relationships.

        Args:
            pattern_id: ID of the pattern to remove

        Returns:
            True if pattern was removed, False if not found
        """
        with self._lock:
            if pattern_id not in self._patterns:
                return False

            pattern = self._patterns[pattern_id]

            # Remove all relationships involving this pattern
            relationships_to_remove = self.get_relationships_by_pattern(pattern_id)
            for relationship in relationships_to_remove:
                del self._relationships[relationship.id]

            # Remove from patterns
            del self._patterns[pattern_id]

            # Update indexes (rebuild for simplicity)
            self._rebuild_indexes()

            # Persist changes
            if self._storage:
                self._storage.delete_pattern(pattern_id)
                for relationship in relationships_to_remove:
                    self._storage.delete_relationship(relationship.id)

            # Invalidate cache
            self._invalidate_metrics_cache()

            self.logger.info(f"Removed pattern: {pattern.name} ({pattern_id})")
            return True

    def remove_relationship(self, relationship_id: str) -> bool:
        """
        Remove a relationship.

        Args:
            relationship_id: ID of the relationship to remove

        Returns:
            True if relationship was removed, False if not found
        """
        with self._lock:
            if relationship_id not in self._relationships:
                return False

            del self._relationships[relationship_id]

            # Update indexes (rebuild for simplicity)
            self._rebuild_indexes()

            # Persist changes
            if self._storage:
                self._storage.delete_relationship(relationship_id)

            # Invalidate cache
            self._invalidate_metrics_cache()

            self.logger.info(f"Removed relationship: {relationship_id}")
            return True
    
    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes from current data."""
        # Clear existing indexes
        for index in self._pattern_index.values():
            index.clear()
        for index in self._relationship_index.values():
            index.clear()

        # Rebuild pattern indexes
        for pattern in self._patterns.values():
            self._update_indexes(pattern=pattern)

        # Rebuild relationship indexes
        for relationship in self._relationships.values():
            self._update_indexes(relationship=relationship)

    def _invalidate_metrics_cache(self) -> None:
        """Invalidate the metrics cache."""
        self._metrics_cache = None
        self._metrics_cache_time = None
        self._local_cache.clear()

    def _validate_framework_quick(self) -> int:
        """Quick validation for basic framework issues."""
        issues = 0

        # Check for relationships referencing non-existent patterns
        for relationship in self._relationships.values():
            connected_patterns = relationship.get_connected_patterns()
            for pattern_id in connected_patterns:
                if pattern_id and pattern_id not in self._patterns:
                    issues += 1

        # Check for patterns with missing required fields
        for pattern in self._patterns.values():
            if not pattern.name or not pattern.domain:
                issues += 1

        return issues

    @performance_timer("add_pattern_batch")
    def add_patterns_batch(self, patterns: List[BasePattern]) -> Dict[str, Any]:
        """
        Add multiple patterns in a batch for better performance.

        Args:
            patterns: List of patterns to add

        Returns:
            Dictionary with batch operation results
        """
        successful = 0
        failed = 0
        errors = []

        with self._lock:
            for pattern in patterns:
                try:
                    self.add_pattern(pattern)
                    successful += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"Pattern {pattern.name}: {str(e)}")

        return {
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'total': len(patterns)
        }

    @performance_timer("add_relationship_batch")
    def add_relationships_batch(self, relationships: List[Relationship]) -> Dict[str, Any]:
        """
        Add multiple relationships in a batch for better performance.

        Args:
            relationships: List of relationships to add

        Returns:
            Dictionary with batch operation results
        """
        successful = 0
        failed = 0
        errors = []

        with self._lock:
            for relationship in relationships:
                try:
                    self.add_relationship(relationship)
                    successful += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"Relationship {relationship.id}: {str(e)}")

        return {
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'total': len(relationships)
        }

    @cached
    def get_patterns_by_domain_optimized(self, domain: str) -> List[BasePattern]:
        """Get patterns by domain with caching."""
        return self.get_patterns_by_domain(domain)

    @cached
    def get_patterns_by_type_optimized(self, pattern_type: str) -> List[BasePattern]:
        """Get patterns by type with caching."""
        return self.get_patterns_by_type(pattern_type)

    @memoize
    def search_patterns_optimized(self, query: str, limit: int = 100) -> List[BasePattern]:
        """Search patterns with memoization."""
        return self.search_patterns(query)[:limit]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the framework."""
        return {
            'cache_stats': {
                'local_cache': self._local_cache.stats(),
                'query_cache': self._query_cache.stats()
            },
            'index_stats': {
                'pattern_index_size': sum(len(ids) for ids in self._pattern_index.get('domain', {}).values()),
                'relationship_index_size': sum(len(ids) for ids in self._relationship_index.get('property', {}).values())
            },
            'memory_usage': len(self._patterns) + len(self._relationships)
        }

    # Enhanced get_metrics method with performance optimizations
    def get_metrics(self, force_refresh: bool = False) -> FrameworkMetrics:
        """
        Get comprehensive framework metrics with enhanced caching.

        Args:
            force_refresh: Force refresh of cached metrics

        Returns:
            FrameworkMetrics object
        """
        with self._lock:
            now = datetime.now(timezone.utc)

            # Check cache validity
            if (not force_refresh and self._metrics_cache and
                self._metrics_cache_time and
                (now - self._metrics_cache_time).seconds < self._cache_timeout):
                return self._metrics_cache

            # Try local cache first
            cache_key = f"metrics_{len(self._patterns)}_{len(self._relationships)}"
            cached_metrics = self._local_cache.get(cache_key)
            if cached_metrics and not force_refresh:
                self._metrics_cache = cached_metrics
                self._metrics_cache_time = now
                return cached_metrics

        # Calculate metrics with performance monitoring
        with performance_context("metrics_calculation"):
            metrics = self._calculate_metrics_internal()

        # Cache the result
        with self._lock:
            self._metrics_cache = metrics
            self._metrics_cache_time = now
            self._local_cache.put(cache_key, metrics)

        return metrics

    def _calculate_metrics_internal(self) -> FrameworkMetrics:
        """Internal method to calculate metrics efficiently."""
        total_patterns = len(self._patterns)
        total_relationships = len(self._relationships)

        # Use indexes for faster counting
        pattern_types_count = Counter()
        for pattern_ids in self._pattern_index.get('type', {}).values():
            pattern_type = pattern_ids[0].split('_')[0] if pattern_ids else 'unknown'
            pattern_types_count[pattern_type] += len(pattern_ids)

        # Domain count using index
        domain_count = len(self._pattern_index.get('domain', {}))

        # Relationship metrics with batch processing
        if total_relationships > 0:
            strengths = []
            confidences = []
            relationship_types_count = Counter()

            # Process in batches for better memory efficiency
            batch_size = 1000
            for i in range(0, total_relationships, batch_size):
                batch_relationships = list(self._relationships.values())[i:i+batch_size]

                for rel in batch_relationships:
                    strengths.append(rel.strength)
                    confidences.append(rel.confidence)
                    relationship_types_count[rel.relationship_type] += 1

            avg_strength = sum(strengths) / len(strengths) if strengths else 0.0
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        else:
            avg_strength = 0.0
            avg_confidence = 0.0
            relationship_types_count = Counter()

        # Orphaned patterns using set operations for efficiency
        all_pattern_ids = set(self._patterns.keys())
        connected_pattern_ids = set()

        # Use relationship index for faster lookup
        for pattern_id in all_pattern_ids:
            if pattern_id in self._pattern_relationships:
                connected_pattern_ids.add(pattern_id)

        orphaned_patterns = len(all_pattern_ids - connected_pattern_ids)

        # Deprecated patterns with batch processing
        deprecated_patterns = 0
        for i in range(0, total_patterns, batch_size):
            batch_patterns = list(self._patterns.values())[i:i+batch_size]
            deprecated_patterns += sum(1 for p in batch_patterns if p.is_deprecated())

        # Validation issues (simplified)
        validation_issues = self._validate_framework_quick()

        return FrameworkMetrics(
            total_patterns=total_patterns,
            total_relationships=total_relationships,
            average_relationship_strength=avg_strength,
            average_confidence=avg_confidence,
            domain_count=domain_count,
            pattern_types_count=dict(pattern_types_count),
            relationship_types_count=dict(relationship_types_count),
            orphaned_patterns=orphaned_patterns,
            deprecated_patterns=deprecated_patterns,
            validation_issues=validation_issues
        )

    def get_pattern_collection(self) -> PatternCollection:
        """
        Get all patterns as a PatternCollection.

        Returns:
            PatternCollection with all patterns organized by type
        """
        with self._lock:
            properties = [p for p in self._patterns.values() if isinstance(p, Property)]
            processes = [p for p in self._patterns.values() if isinstance(p, Process)]
            perspectives = [p for p in self._patterns.values() if isinstance(p, Perspective)]

            return PatternCollection(
                properties=properties,
                processes=processes,
                perspectives=perspectives
            )

    def export_to_json(self, file_path: Optional[str] = None,
                      include_metadata: bool = True) -> Optional[str]:
        """
        Export the framework data to JSON with enhanced metadata.
        
        Args:
            file_path: Optional path to write the JSON to
            include_metadata: Include export metadata
            
        Returns:
            If file_path is None, returns the JSON string
        """
        with self._lock:
            data = {
                "patterns": [p.dict(by_alias=True) for p in self._patterns.values()],
                "relationships": [r.dict(by_alias=True) for r in self._relationships.values()],
                "framework_metadata": {
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "framework_version": "2.0.0",
                    "total_patterns": len(self._patterns),
                    "total_relationships": len(self._relationships),
                    "exporter": "p3if-enhanced"
                } if include_metadata else None
            }

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Exported framework to {file_path}")
                return None
            else:
                return json.dumps(data, indent=2, ensure_ascii=False)
    
    def import_from_json(self, json_data: Union[str, Path, Dict],
                        validate: bool = True) -> Dict[str, int]:
        """
        Import framework data from JSON with enhanced validation.
        
        Args:
            json_data: JSON string, file path, or dict
            validate: Whether to validate imported data

        Returns:
            Dictionary with import statistics
        """
        with self._lock:
            # Load data from various sources
            if isinstance(json_data, str) and Path(json_data).exists():
                with open(json_data, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif isinstance(json_data, str):
                data = json.loads(json_data)
            elif isinstance(json_data, Path):
                with open(json_data, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif isinstance(json_data, dict):
                data = json_data
            else:
                raise ValueError("Invalid JSON data format")

            # Import patterns
            patterns_imported = 0
            relationships_imported = 0

            # Import patterns first
            for pattern_data in data.get("patterns", []):
                try:
                    # Determine pattern type and class
                    pattern_type = pattern_data.get("type")
                    if pattern_type == "property":
                        pattern = Property(**pattern_data)
                    elif pattern_type == "process":
                        pattern = Process(**pattern_data)
                    elif pattern_type == "perspective":
                        pattern = Perspective(**pattern_data)
                    else:
                        self.logger.warning(f"Unknown pattern type: {pattern_type}")
                        continue

                    # Add pattern (this will handle validation and indexing)
                    self.add_pattern(pattern)
                    patterns_imported += 1

                except Exception as e:
                    self.logger.error(f"Failed to import pattern: {e}")
                    if validate:
                        raise

            # Import relationships
            for rel_data in data.get("relationships", []):
                try:
                    relationship = Relationship(**rel_data)
                    self.add_relationship(relationship)
                    relationships_imported += 1

                except Exception as e:
                    self.logger.error(f"Failed to import relationship: {e}")
                    if validate:
                        raise

            # Rebuild indexes to ensure consistency
            self._rebuild_indexes()

            # Invalidate cache
            self._invalidate_metrics_cache()

            self.logger.info(f"Imported {patterns_imported} patterns and {relationships_imported} relationships")

            return {
                "patterns_imported": patterns_imported,
                "relationships_imported": relationships_imported
            }

    def hot_swap_dimension(self, old_dimension: Union[str, PatternType],
                          new_dimension: Union[str, PatternType]) -> int:
        """
        Hot-swap one dimension with another across all relationships.
        
        Args:
            old_dimension: The dimension to replace
            new_dimension: The dimension to use as replacement

        Returns:
            Number of relationships modified
        """
        with self._lock:
            if isinstance(old_dimension, PatternType):
                old_dimension = old_dimension.value
            if isinstance(new_dimension, PatternType):
                new_dimension = new_dimension.value

            if old_dimension not in ['property', 'process', 'perspective']:
                raise ValueError(f"Invalid dimension: {old_dimension}")
            if new_dimension not in ['property', 'process', 'perspective']:
                raise ValueError(f"Invalid dimension: {new_dimension}")

            modified_count = 0
            old_attr = f"{old_dimension}_id"
            new_attr = f"{new_dimension}_id"
            
            for relationship in self._relationships.values():
                if (hasattr(relationship, old_attr) and
                    hasattr(relationship, new_attr) and
                    getattr(relationship, old_attr)):

                    old_value = getattr(relationship, old_attr)
                    setattr(relationship, new_attr, old_value)
                    setattr(relationship, old_attr, None)
                    relationship.updated_at = datetime.now(timezone.utc)
                    modified_count += 1

            if modified_count > 0:
                # Rebuild indexes after changes
                self._rebuild_indexes()
                self._invalidate_metrics_cache()

            self.logger.info(f"Hot-swapped {modified_count} relationships from {old_dimension} to {new_dimension}")
            return modified_count

    def multiplex_frameworks(self, external_framework: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        """
        Integrate patterns from an external framework with advanced conflict resolution.
        
        Args:
            external_framework: Dictionary containing patterns to integrate

        Returns:
            Dictionary with integration statistics
        """
        with self._lock:
            integrated = {"properties": 0, "processes": 0, "perspectives": 0}
            skipped = {"properties": 0, "processes": 0, "perspectives": 0}

        for dimension, items in external_framework.items():
            if dimension not in ['property', 'process', 'perspective']:
                self.logger.warning(f"Skipping unknown dimension: {dimension}")
                continue

            dimension_class = {
                'property': Property,
                'process': Process,
                'perspective': Perspective
            }[dimension]

            for item_data in items:
                    try:
                        # Check if item already exists (by name and domain)
                        existing_items = [
                            p for p in self._patterns.values()
                            if (p.type.value == dimension and
                                p.name == item_data.get("name") and
                                p.domain == item_data.get("domain"))
                        ]

                        if existing_items:
                            # Pattern exists - update it
                            existing = existing_items[0]
                            # Update fields while preserving ID and timestamps
                            for key, value in item_data.items():
                                if key not in ['id', 'created_at'] and hasattr(existing, key):
                                    setattr(existing, key, value)
                            existing.updated_at = datetime.now(timezone.utc)
                            skipped[dimension] += 1
                        else:
                            # Create new pattern
                            pattern = dimension_class(**item_data)
                            self.add_pattern(pattern)
                            integrated[dimension] += 1

                    except Exception as e:
                        self.logger.error(f"Failed to integrate {dimension} item: {e}")
                        continue

            # Rebuild indexes and invalidate cache
            self._rebuild_indexes()
            self._invalidate_metrics_cache()

            self.logger.info(f"Integrated {integrated} new patterns, updated {skipped} existing patterns")
            return {"integrated": integrated, "skipped": skipped}
    
    def clear(self) -> None:
        """Clear all patterns and relationships with proper cleanup."""
        with self._lock:
            self._patterns.clear()
            self._relationships.clear()

            # Clear indexes
            for index in self._pattern_index.values():
                index.clear()
            for index in self._relationship_index.values():
                index.clear()

            # Clear caches
            self._invalidate_metrics_cache()

            # Clear storage
            if self._storage:
                self._storage.clear()

            self.logger.info("Framework cleared")
            
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive summary statistics for the framework.

        Returns:
            Dictionary containing detailed statistics
        """
        metrics = self.get_metrics()

        with self._lock:
            # Domain analysis
            domain_stats = defaultdict(int)
            for pattern in self._patterns.values():
                if pattern.domain:
                    domain_stats[pattern.domain] += 1

            # Tag analysis
            all_tags = Counter()
            for pattern in self._patterns.values():
                all_tags.update(pattern.tags)

            # Relationship analysis
            bidirectional_count = sum(1 for r in self._relationships.values() if r.bidirectional)
            unidirectional_count = len(self._relationships) - bidirectional_count

            # Quality metrics
            quality_scores = [p.quality_score for p in self._patterns.values()]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

            return {
                "overview": {
                    "total_patterns": metrics.total_patterns,
                    "total_relationships": metrics.total_relationships,
                    "domains": metrics.domain_count,
                    "avg_relationship_strength": metrics.average_relationship_strength,
                    "avg_confidence": metrics.average_confidence
                },
                "patterns": {
                    "by_type": metrics.pattern_types_count,
                    "orphaned": metrics.orphaned_patterns,
                    "deprecated": metrics.deprecated_patterns,
                    "avg_quality_score": avg_quality
                },
                "relationships": {
                    "by_type": metrics.relationship_types_count,
                    "bidirectional": bidirectional_count,
                    "unidirectional": unidirectional_count
                },
                "domains": dict(domain_stats),
                "tags": dict(all_tags.most_common(20)),  # Top 20 tags
                "validation": {
                    "issues": metrics.validation_issues
                }
            }

    def validate_framework(self) -> Dict[str, Any]:
        """
        Validate the framework for consistency and quality issues.
        
        Returns:
            Dictionary containing validation results
        """
        with self._lock:
            issues = []
            warnings = []

            # Check for orphaned patterns
            all_pattern_ids = set(self._patterns.keys())
            connected_pattern_ids = set()
            for relationship in self._relationships.values():
                connected_pattern_ids.update(relationship.get_connected_patterns())

            orphaned = all_pattern_ids - connected_pattern_ids
            if orphaned:
                issues.append(f"Found {len(orphaned)} orphaned patterns")

            # Check for patterns with no relationships
            isolated_patterns = [
                pid for pid in all_pattern_ids
                if not self.get_relationships_by_pattern(pid)
            ]
            if isolated_patterns:
                warnings.append(f"Found {len(isolated_patterns)} patterns with no relationships")

            # Check for deprecated patterns
            deprecated = [p for p in self._patterns.values() if p.is_deprecated()]
            if deprecated:
                warnings.append(f"Found {len(deprecated)} deprecated patterns")

            # Check relationship validity
            invalid_relationships = []
            for relationship in self._relationships.values():
                connected = relationship.get_connected_patterns()
                if not connected:
                    invalid_relationships.append(relationship.id)

            if invalid_relationships:
                issues.append(f"Found {len(invalid_relationships)} relationships with no connections")

            # Check for circular relationships (simplified)
            # This would need more sophisticated logic for complex cases
        
        return {
                "valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "statistics": {
                    "orphaned_patterns": len(orphaned),
                    "isolated_patterns": len(isolated_patterns),
                    "deprecated_patterns": len(deprecated),
                    "invalid_relationships": len(invalid_relationships)
                }
            }

    def __len__(self) -> int:
        """Return the total number of patterns in the framework."""
        return len(self._patterns)

    def __contains__(self, pattern_id: str) -> bool:
        """Check if a pattern exists in the framework."""
        return pattern_id in self._patterns

    def __iter__(self) -> Iterator[BasePattern]:
        """Iterate over all patterns in the framework."""
        return iter(self._patterns.values())

    def __del__(self):
        """Cleanup when framework is destroyed."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)
    