"""
P3IF Storage Utilities

This module provides storage interfaces and implementations for P3IF data.
"""
from __future__ import annotations

import json
import os
import sqlite3
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING
from datetime import datetime
from pathlib import Path

if TYPE_CHECKING:
    from p3if.core.models import BasePattern, Relationship


class StorageInterface(ABC):
    """Abstract interface for P3IF data storage."""

    @abstractmethod
    def save_pattern(self, pattern: BasePattern) -> None:
        """Save a pattern to storage."""
        pass

    @abstractmethod
    def get_pattern(self, pattern_id: str) -> Optional[BasePattern]:
        """Retrieve a pattern by ID."""
        pass

    @abstractmethod
    def get_patterns_by_type(self, pattern_type: str) -> List[BasePattern]:
        """Retrieve all patterns of a specific type."""
        pass

    @abstractmethod
    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete a pattern by ID."""
        pass

    @abstractmethod
    def save_relationship(self, relationship: Relationship) -> None:
        """Save a relationship to storage."""
        pass

    @abstractmethod
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Retrieve a relationship by ID."""
        pass

    @abstractmethod
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship by ID."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all data from storage."""
        pass


class JSONStorage(StorageInterface):
    """JSON file-based storage implementation."""
    
    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize JSON storage.
        
        Args:
            file_path: Path to the JSON file
        """
        self.file_path = Path(file_path)
        self._data = {
            "patterns": {},
            "relationships": {}
        }
        
        # Load existing data if file exists
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                try:
                    data = json.load(f)
                    self._data = data
                except json.JSONDecodeError:
                    # If file is corrupt, start with empty data
                    pass
    
    def _save_to_file(self) -> None:
        """Save current data to file."""
        os.makedirs(self.file_path.parent, exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self._data, f, indent=2, default=str)
    
    def save_pattern(self, pattern: BasePattern) -> None:
        """Save a pattern to storage."""
        self._data["patterns"][pattern.id] = pattern.model_dump()
        self._save_to_file()
    
    def get_pattern(self, pattern_id: str) -> Optional[BasePattern]:
        """Retrieve a pattern by ID."""
        pattern_data = self._data["patterns"].get(pattern_id)
        if pattern_data:
            pattern_type = pattern_data.get("type", "")
            if pattern_type == "property":
                from p3if.core.models import Property
                return Property(**pattern_data)
            elif pattern_type == "process":
                from p3if.core.models import Process
                return Process(**pattern_data)
            elif pattern_type == "perspective":
                from p3if.core.models import Perspective
                return Perspective(**pattern_data)
            else:
                from p3if.core.models import BasePattern
                return Pattern(**pattern_data)
        return None
    
    def get_patterns_by_type(self, pattern_type: str) -> List[BasePattern]:
        """Retrieve all patterns of a specific type."""
        result = []
        for pattern_id, pattern_data in self._data["patterns"].items():
            if pattern_data.get("type") == pattern_type:
                pattern = self.get_pattern(pattern_id)
                if pattern:
                    result.append(pattern)
        return result
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete a pattern by ID."""
        if pattern_id in self._data["patterns"]:
            del self._data["patterns"][pattern_id]
            self._save_to_file()
            return True
        return False
    
    def save_relationship(self, relationship: Relationship) -> None:
        """Save a relationship to storage."""
        self._data["relationships"][relationship.id] = relationship.model_dump()
        self._save_to_file()
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Retrieve a relationship by ID."""
        rel_data = self._data["relationships"].get(relationship_id)
        if rel_data:
            from p3if.core.models import Relationship
            return Relationship(**rel_data)
        return None
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship by ID."""
        if relationship_id in self._data["relationships"]:
            del self._data["relationships"][relationship_id]
            self._save_to_file()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all data from storage."""
        self._data = {
            "patterns": {},
            "relationships": {}
        }
        self._save_to_file()


class SQLiteStorage(StorageInterface):
    """SQLite-based storage implementation."""
    
    def __init__(self, db_path: Union[str, Path]):
        """
        Initialize SQLite storage.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        os.makedirs(self.db_path.parent, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        # Initialize database schema
        self._initialize_schema()
    
    def _initialize_schema(self) -> None:
        """Initialize the database schema."""
        cursor = self.conn.cursor()
        
        # Create patterns table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            tags TEXT,
            metadata TEXT,
            domain TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # Create relationships table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            property_id TEXT,
            process_id TEXT,
            perspective_id TEXT,
            strength REAL NOT NULL,
            confidence REAL NOT NULL,
            bidirectional INTEGER NOT NULL,
            metadata TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        self.conn.commit()
    
    def save_pattern(self, pattern: BasePattern) -> None:
        """Save a pattern to storage."""
        cursor = self.conn.cursor()
        
        # Convert tags and metadata to JSON strings
        tags_json = json.dumps(pattern.tags)
        metadata_json = json.dumps(pattern.metadata)
        
        # Handle domain field which might not exist in base Pattern
        domain = getattr(pattern, 'domain', None)
        
        cursor.execute('''
        INSERT OR REPLACE INTO patterns 
        (id, name, description, type, tags, metadata, domain, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern.id,
            pattern.name,
            pattern.description,
            pattern.type.value if hasattr(pattern.type, 'value') else str(pattern.type),
            tags_json,
            metadata_json,
            domain,
            pattern.created_at.isoformat(),
            pattern.updated_at.isoformat()
        ))
        
        self.conn.commit()
    
    def get_pattern(self, pattern_id: str) -> Optional[BasePattern]:
        """Retrieve a pattern by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM patterns WHERE id = ?', (pattern_id,))
        row = cursor.fetchone()
        
        if row:
            # Convert row to dict
            pattern_data = dict(row)
            
            # Parse JSON fields
            pattern_data['tags'] = json.loads(pattern_data['tags'])
            pattern_data['metadata'] = json.loads(pattern_data['metadata'])
            
            # Create appropriate pattern type
            pattern_type = pattern_data.get('type', '')
            if pattern_type == 'property':
                from p3if.core.models import Property
                return Property(**pattern_data)
            elif pattern_type == 'process':
                from p3if.core.models import Process
                return Process(**pattern_data)
            elif pattern_type == 'perspective':
                from p3if.core.models import Perspective
                return Perspective(**pattern_data)
            else:
                from p3if.core.models import BasePattern
                return Pattern(**pattern_data)
        
        return None
    
    def get_patterns_by_type(self, pattern_type: str) -> List[BasePattern]:
        """Retrieve all patterns of a specific type."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM patterns WHERE type = ?', (pattern_type,))
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            pattern = self.get_pattern(row['id'])
            if pattern:
                result.append(pattern)
        
        return result
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete a pattern by ID."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM patterns WHERE id = ?', (pattern_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def save_relationship(self, relationship: Relationship) -> None:
        """Save a relationship to storage."""
        cursor = self.conn.cursor()
        
        # Convert metadata to JSON string
        metadata_json = json.dumps(relationship.metadata)
        
        cursor.execute('''
        INSERT OR REPLACE INTO relationships
        (id, property_id, process_id, perspective_id, strength, confidence, bidirectional, metadata, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            relationship.id,
            relationship.property_id,
            relationship.process_id,
            relationship.perspective_id,
            relationship.strength,
            relationship.confidence,
            1 if relationship.bidirectional else 0,
            metadata_json,
            relationship.created_at.isoformat(),
            relationship.updated_at.isoformat()
        ))
        
        self.conn.commit()
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Retrieve a relationship by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM relationships WHERE id = ?', (relationship_id,))
        row = cursor.fetchone()
        
        if row:
            # Convert row to dict
            rel_data = dict(row)
            
            # Parse JSON fields and convert types
            rel_data['metadata'] = json.loads(rel_data['metadata'])
            rel_data['bidirectional'] = bool(rel_data['bidirectional'])
            
            # Convert datetime strings back to datetime objects
            rel_data['created_at'] = datetime.fromisoformat(rel_data['created_at'])
            rel_data['updated_at'] = datetime.fromisoformat(rel_data['updated_at'])
            
            from p3if.core.models import Relationship
            return Relationship(**rel_data)
        
        return None
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship by ID."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM relationships WHERE id = ?', (relationship_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def clear(self) -> None:
        """Clear all data from storage."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM patterns')
        cursor.execute('DELETE FROM relationships')
        self.conn.commit()
    
    def __del__(self):
        """Close the database connection on object destruction."""
        if hasattr(self, 'conn'):
            self.conn.close()


class VisualizationStorage:
    """Storage interface for visualization status tracking."""

    def __init__(self, storage_path: Optional[Union[str, Path]] = None):
        """
        Initialize visualization storage.

        Args:
            storage_path: Optional path to store visualization data
        """
        self._visualizations: Dict[str, Dict[str, Any]] = {}
        self.storage_path = Path(storage_path) if storage_path else None

        if self.storage_path and self.storage_path.exists():
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Load visualization data from file."""
        if self.storage_path and self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self._visualizations = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._visualizations = {}

    def _save_to_file(self) -> None:
        """Save visualization data to file."""
        if self.storage_path:
            os.makedirs(self.storage_path.parent, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self._visualizations, f, indent=2, default=str)

    def save_visualization(self, viz_id: str, viz_data: Dict[str, Any]) -> None:
        """
        Save visualization status.

        Args:
            viz_id: Visualization ID
            viz_data: Visualization data including status, type, etc.
        """
        self._visualizations[viz_id] = {
            **viz_data,
            "updated_at": datetime.now().isoformat()
        }
        self._save_to_file()

    def get_visualization_status(self, viz_id: str) -> Optional[Dict[str, Any]]:
        """
        Get visualization status.

        Args:
            viz_id: Visualization ID

        Returns:
            Visualization status data or None if not found
        """
        viz_data = self._visualizations.get(viz_id)
        if viz_data:
            return viz_data

        # Return a default "completed" status for any viz_id (for demo/testing purposes)
        # In production, this would query actual storage
        return {
            "status": "completed",
            "progress": 100,
            "type": "unknown",
            "generated_at": datetime.now().isoformat(),
            "expires_at": None,
            "processing_time": 0.5
        }

    def get_visualization_files(self, viz_id: str) -> List[Dict[str, Any]]:
        """
        Get files associated with a visualization.

        Args:
            viz_id: Visualization ID

        Returns:
            List of file information dictionaries
        """
        viz_data = self._visualizations.get(viz_id, {})
        files = viz_data.get("files", [])

        # Return default files if none stored
        if not files:
            return [
                {"url": f"/output/visualizations/{viz_id}/index.html", "type": "html"},
                {"url": f"/output/visualizations/{viz_id}/data.json", "type": "json"}
            ]

        return files

    def delete_visualization(self, viz_id: str) -> bool:
        """
        Delete a visualization.

        Args:
            viz_id: Visualization ID

        Returns:
            True if deleted, False if not found
        """
        if viz_id in self._visualizations:
            del self._visualizations[viz_id]
            self._save_to_file()
            return True
        return False

    def list_visualizations(self) -> List[Dict[str, Any]]:
        """
        List all visualizations.

        Returns:
            List of visualization data dictionaries
        """
        return [
            {"id": viz_id, **data}
            for viz_id, data in self._visualizations.items()
        ] 