"""
P3IF: Properties, Processes, and Perspectives Inter-Framework

A sophisticated meta-framework for integrating, analyzing, and visualizing
complex data relationships across multiple domains.
"""

__version__ = "2.0.0"

from .core import P3IFFramework, P3IFCore
from .core.models import Property, Process, Perspective, Relationship

__all__ = [
    'P3IFFramework',
    'P3IFCore',
    'Property',
    'Process',
    'Perspective',
    'Relationship',
]





