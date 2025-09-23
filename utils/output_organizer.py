#!/usr/bin/env python3
"""
Output Organization Utility for P3IF Visualizations and Animations

This module provides a comprehensive system for organizing all visualization outputs
into a consistent directory structure under the main output folder.
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
import logging
from dataclasses import dataclass, field


@dataclass
class OutputDirectoryStructure:
    """Defines the standard output directory structure for P3IF."""
    base_name: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))

    def get_base_path(self, root_output_dir: Union[str, Path]) -> Path:
        """Get the base output path for this structure."""
        root_path = Path(root_output_dir)
        return root_path / f"{self.base_name}_{self.timestamp}"

    def get_subdirs(self) -> Dict[str, str]:
        """Get the standard subdirectory structure."""
        return {
            "visualizations": "Interactive visualizations (HTML files)",
            "images": "Static images and charts (PNG, SVG, etc.)",
            "animations": "Animation files and sequences",
            "data": "Data files and JSON exports",
            "reports": "Analysis reports and summaries",
            "logs": "Log files and debugging information",
            "assets": "Static assets (CSS, JS, fonts)",
            "config": "Configuration files and settings",
            "metadata": "Metadata and version information"
        }


class OutputOrganizer:
    """Manages the organization of P3IF visualization outputs."""

    def __init__(self, root_output_dir: Union[str, Path] = None):
        """
        Initialize the output organizer.

        Args:
            root_output_dir: Root output directory (defaults to project_root/output)
        """
        if root_output_dir is None:
            # Default to project root output directory
            project_root = Path(__file__).parent.parent
            root_output_dir = project_root / "output"

        self.root_output_dir = Path(root_output_dir)
        self.logger = logging.getLogger(__name__)

        # Ensure root output directory exists
        self.root_output_dir.mkdir(parents=True, exist_ok=True)

        # Create main output directory for current session
        self.current_session = OutputDirectoryStructure("p3if_output")
        self.current_base_path = self.current_session.get_base_path(self.root_output_dir)

    def create_session_structure(self, session_name: Optional[str] = None) -> Path:
        """
        Create a new output session with organized subdirectories.

        Args:
            session_name: Optional custom session name

        Returns:
            Path to the session base directory
        """
        if session_name:
            self.current_session = OutputDirectoryStructure(session_name)
            self.current_base_path = self.current_session.get_base_path(self.root_output_dir)

        # Create all standard subdirectories
        subdirs = self.current_session.get_subdirs()
        for subdir_name, description in subdirs.items():
            subdir_path = self.current_base_path / subdir_name
            subdir_path.mkdir(parents=True, exist_ok=True)

            # Create a README file explaining the directory
            readme_path = subdir_path / "README.md"
            if not readme_path.exists():
                readme_path.write_text(f"# {subdir_name.title()} Directory\n\n{description}\n")

        # Create session metadata
        self._create_session_metadata()

        self.logger.info(f"Created output session structure at: {self.current_base_path}")
        return self.current_base_path

    def _create_session_metadata(self):
        """Create metadata file for the current session."""
        metadata = {
            "session_name": self.current_session.base_name,
            "timestamp": self.current_session.timestamp,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "structure_version": "2.0",
            "subdirectories": self.current_session.get_subdirs()
        }

        metadata_path = self.current_base_path / "session_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

    def get_visualization_path(self, visualization_type: str, filename: str) -> Path:
        """
        Get the appropriate path for a visualization file.

        Args:
            visualization_type: Type of visualization (e.g., "3d_cube", "network_graph")
            filename: Name of the file

        Returns:
            Path to the organized location for the file
        """
        # Create visualization subdirectory if it doesn't exist
        viz_dir = self.current_base_path / "visualizations" / visualization_type
        viz_dir.mkdir(parents=True, exist_ok=True)

        return viz_dir / filename

    def get_image_path(self, category: str, filename: str) -> Path:
        """
        Get the appropriate path for an image file.

        Args:
            category: Category of image (e.g., "overview", "domain", "comparison")
            filename: Name of the image file

        Returns:
            Path to the organized location for the image
        """
        # Create category subdirectory if it doesn't exist
        img_dir = self.current_base_path / "images" / category
        img_dir.mkdir(parents=True, exist_ok=True)

        return img_dir / filename

    def get_animation_path(self, animation_type: str, filename: str) -> Path:
        """
        Get the appropriate path for an animation file.

        Args:
            animation_type: Type of animation (e.g., "rotation", "transition", "sequence")
            filename: Name of the animation file

        Returns:
            Path to the organized location for the animation
        """
        # Create animation subdirectory if it doesn't exist
        anim_dir = self.current_base_path / "animations" / animation_type
        anim_dir.mkdir(parents=True, exist_ok=True)

        return anim_dir / filename

    def get_data_path(self, data_type: str, filename: str) -> Path:
        """
        Get the appropriate path for a data file.

        Args:
            data_type: Type of data (e.g., "patterns", "relationships", "metrics")
            filename: Name of the data file

        Returns:
            Path to the organized location for the data file
        """
        # Create data subdirectory if it doesn't exist
        data_dir = self.current_base_path / "data" / data_type
        data_dir.mkdir(parents=True, exist_ok=True)

        return data_dir / filename

    def get_asset_path(self, asset_type: str, filename: str) -> Path:
        """
        Get the appropriate path for an asset file.

        Args:
            asset_type: Type of asset (e.g., "css", "js", "fonts")
            filename: Name of the asset file

        Returns:
            Path to the organized location for the asset file
        """
        # Create asset subdirectory if it doesn't exist
        asset_dir = self.current_base_path / "assets" / asset_type
        asset_dir.mkdir(parents=True, exist_ok=True)

        return asset_dir / filename

    def organize_existing_files(self, source_dir: Union[str, Path], copy_files: bool = True):
        """
        Organize existing visualization files from a source directory.

        Args:
            source_dir: Source directory containing files to organize
            copy_files: Whether to copy files (True) or move them (False)
        """
        source_path = Path(source_dir)

        if not source_path.exists():
            self.logger.warning(f"Source directory does not exist: {source_path}")
            return

        # Define file type mappings
        file_type_mappings = {
            ".html": ("visualizations", "interactive"),
            ".png": ("images", "static"),
            ".svg": ("images", "vector"),
            ".json": ("data", "json"),
            ".css": ("assets", "css"),
            ".js": ("assets", "js"),
            ".log": ("logs", "logs"),
            ".md": ("reports", "documentation")
        }

        # Process files
        for file_path in source_path.rglob("*"):
            if file_path.is_file():
                extension = file_path.suffix.lower()

                if extension in file_type_mappings:
                    category, subcategory = file_type_mappings[extension]

                    if category == "visualizations" and "cube" in file_path.name:
                        subcategory = "3d_cube"
                    elif category == "visualizations" and "graph" in file_path.name:
                        subcategory = "network_graph"

                    target_path = self._get_organized_path(category, subcategory, file_path.name)

                    if copy_files:
                        shutil.copy2(file_path, target_path)
                    else:
                        shutil.move(str(file_path), str(target_path))

                    self.logger.info(f"{'Copied' if copy_files else 'Moved'} {file_path} -> {target_path}")

    def _get_organized_path(self, category: str, subcategory: str, filename: str) -> Path:
        """Get the organized path for a file."""
        if category == "visualizations":
            return self.current_base_path / "visualizations" / subcategory / filename
        elif category == "images":
            return self.current_base_path / "images" / subcategory / filename
        elif category == "data":
            return self.current_base_path / "data" / subcategory / filename
        elif category == "assets":
            return self.current_base_path / "assets" / subcategory / filename
        else:
            return self.current_base_path / category / filename

    def create_output_index(self) -> Path:
        """
        Create an index file listing all output files in the current session.

        Returns:
            Path to the created index file
        """
        index_data = {
            "session_info": {
                "name": self.current_session.base_name,
                "timestamp": self.current_session.timestamp,
                "base_path": str(self.current_base_path),
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            "directory_structure": self.current_session.get_subdirs(),
            "files_by_category": self._catalog_files()
        }

        index_path = self.current_base_path / "output_index.json"
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)

        self.logger.info(f"Created output index at: {index_path}")
        return index_path

    def _catalog_files(self) -> Dict[str, List[str]]:
        """Catalog all files in the output structure."""
        catalog = {}

        for subdir_name in self.current_session.get_subdirs().keys():
            subdir_path = self.current_base_path / subdir_name
            if subdir_path.exists():
                files = []
                for file_path in subdir_path.rglob("*"):
                    if file_path.is_file():
                        files.append(str(file_path.relative_to(self.current_base_path)))
                catalog[subdir_name] = sorted(files)

        return catalog

    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        return {
            "session_name": self.current_session.base_name,
            "base_path": str(self.current_base_path),
            "timestamp": self.current_session.timestamp,
            "subdirectories": list(self.current_session.get_subdirs().keys()),
            "total_size": self._calculate_directory_size(self.current_base_path),
            "file_counts": self._count_files_by_type()
        }

    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate the total size of a directory in bytes."""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    def _count_files_by_type(self) -> Dict[str, int]:
        """Count files by type/extension."""
        counts = {}

        for file_path in self.current_base_path.rglob("*"):
            if file_path.is_file():
                extension = file_path.suffix.lower() or "no_extension"
                counts[extension] = counts.get(extension, 0) + 1

        return counts

    def cleanup_old_sessions(self, keep_last_n: int = 5):
        """
        Clean up old output sessions, keeping only the most recent N.

        Args:
            keep_last_n: Number of recent sessions to keep
        """
        # Get all session directories
        session_dirs = []
        for item in self.root_output_dir.iterdir():
            if item.is_dir() and item.name.startswith("p3if_output_"):
                try:
                    # Extract timestamp from directory name
                    timestamp_str = item.name.split("_")[-1]
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    session_dirs.append((item, timestamp))
                except (ValueError, IndexError):
                    continue

        # Sort by timestamp (newest first)
        session_dirs.sort(key=lambda x: x[1], reverse=True)

        # Remove old sessions
        sessions_to_remove = session_dirs[keep_last_n:]
        for session_dir, _ in sessions_to_remove:
            shutil.rmtree(session_dir)
            self.logger.info(f"Removed old session: {session_dir}")

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available output sessions."""
        sessions = []

        for item in self.root_output_dir.iterdir():
            if item.is_dir() and item.name.startswith("p3if_output_"):
                try:
                    # Extract timestamp from directory name
                    timestamp_str = item.name.split("_")[-1]
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                    sessions.append({
                        "name": item.name,
                        "path": str(item),
                        "timestamp": timestamp.isoformat(),
                        "size": self._calculate_directory_size(item)
                    })
                except (ValueError, IndexError):
                    continue

        return sorted(sessions, key=lambda x: x['timestamp'], reverse=True)


# Global output organizer instance
_default_organizer = None

def get_output_organizer(root_output_dir: Union[str, Path] = None) -> OutputOrganizer:
    """Get the global output organizer instance."""
    global _default_organizer
    if _default_organizer is None:
        _default_organizer = OutputOrganizer(root_output_dir)
    return _default_organizer

def organize_visualization_output(visualization_type: str,
                                filename: str,
                                content: Any,
                                root_output_dir: Union[str, Path] = None) -> Path:
    """
    Convenience function to organize a visualization output.

    Args:
        visualization_type: Type of visualization
        filename: Output filename
        content: Content to write to the file
        root_output_dir: Root output directory

    Returns:
        Path to the organized output file
    """
    organizer = get_output_organizer(root_output_dir)
    output_path = organizer.get_visualization_path(visualization_type, filename)

    # Write content to file
    if isinstance(content, str):
        output_path.write_text(content)
    elif isinstance(content, (dict, list)):
        output_path.write_text(json.dumps(content, indent=2))
    else:
        # For binary content
        output_path.write_bytes(content)

    return output_path

def organize_animation_output(animation_type: str,
                            filename: str,
                            content: Any,
                            root_output_dir: Union[str, Path] = None) -> Path:
    """
    Convenience function to organize an animation output.

    Args:
        animation_type: Type of animation
        filename: Output filename
        content: Content to write to the file
        root_output_dir: Root output directory

    Returns:
        Path to the organized output file
    """
    organizer = get_output_organizer(root_output_dir)
    output_path = organizer.get_animation_path(animation_type, filename)

    # Write content to file
    if isinstance(content, str):
        output_path.write_text(content)
    elif isinstance(content, (dict, list)):
        output_path.write_text(json.dumps(content, indent=2))
    else:
        # For binary content
        output_path.write_bytes(content)

    return output_path

def create_standard_output_structure(root_output_dir: Union[str, Path] = None) -> Path:
    """
    Create a standard output structure for P3IF visualizations.

    Args:
        root_output_dir: Root output directory

    Returns:
        Path to the created output base directory
    """
    organizer = get_output_organizer(root_output_dir)
    return organizer.create_session_structure()
