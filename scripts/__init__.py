#!/usr/bin/env python3
"""
Scripts Package

Contains executable scripts for the P3IF framework.
"""

__version__ = '0.1.0'

# For backward compatibility with p3if.scripts imports
try:
    import sys
    sys.modules['p3if.scripts'] = sys.modules[__name__]
    sys.modules['p3if.scripts.ensure_website_references'] = sys.modules['scripts.ensure_website_references']
    sys.modules['p3if.scripts.fix_visualization_paths'] = sys.modules['scripts.fix_visualization_paths']
except Exception:
    pass 