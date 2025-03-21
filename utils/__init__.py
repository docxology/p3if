"""
Utils Package

Contains utility functions and classes for the P3IF framework.
"""

# Import main utility modules
from utils.config import Config
from utils.storage import StorageInterface as StorageManager

# For backward compatibility with p3if.utils imports
try:
    import sys
    sys.modules['p3if.utils'] = sys.modules[__name__]
    sys.modules['p3if.utils.config'] = sys.modules['utils.config']
    sys.modules['p3if.utils.storage'] = sys.modules['utils.storage']
except Exception:
    pass

from utils.json import P3IFEncoder, convert_to_serializable, dumps, dump, loads, load

__all__ = [
    'P3IFEncoder',
    'convert_to_serializable',
    'dumps',
    'dump',
    'loads',
    'load'
] 