"""
Core Package

Contains the core framework and models for the P3IF system.
"""

# Import main modules for easier access
from core.framework import P3IFFramework
from core.models import Property, Process, Perspective, Relationship

# For backward compatibility with p3if.core imports
try:
    import sys
    sys.modules['p3if.core'] = sys.modules[__name__]
    sys.modules['p3if.core.framework'] = sys.modules['core.framework']
    sys.modules['p3if.core.models'] = sys.modules['core.models']
except Exception:
    pass

__all__ = [
    'Property',
    'Process',
    'Perspective',
    'Relationship',
    'BasePattern',
    'P3IFFramework'
] 