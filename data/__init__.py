"""
Data Package

Contains data generators, importers, exporters, and domain definitions.
"""

# Import main modules for easier access
from data.synthetic import SyntheticDataGenerator
from data.domains import DomainManager
from data.importers import import_from_json as DataImporter 
from data.exporters import DataExporter

# For backward compatibility with p3if.data imports
try:
    import sys
    sys.modules['p3if.data'] = sys.modules[__name__]
    sys.modules['p3if.data.synthetic'] = sys.modules['data.synthetic']
    sys.modules['p3if.data.domains'] = sys.modules['data.domains']
    sys.modules['p3if.data.importers'] = sys.modules['data.importers']
    sys.modules['p3if.data.exporters'] = sys.modules['data.exporters']
    # Also make sure DataExporter can be imported from data.exporters
    from data.exporters import DataExporter as DE
    sys.modules['p3if.data.exporters'].DataExporter = DE
except Exception:
    pass

__all__ = [
    'SyntheticDataGenerator',
    'DomainManager',
    'DataImporter',
    'DataExporter'
] 