"""
Analysis Package

Contains analysis tools for the P3IF framework, including basic analysis,
meta-analysis, report generation, and network analysis.
"""

# Import main analysis modules
from analysis.basic import BasicAnalyzer
from analysis.meta import MetaAnalyzer
from analysis.report import AnalysisReport as ReportGenerator
from analysis.network import NetworkAnalyzer

# For backward compatibility with p3if.analysis imports
try:
    import sys
    sys.modules['p3if.analysis'] = sys.modules[__name__]
    sys.modules['p3if.analysis.basic'] = sys.modules['analysis.basic']
    sys.modules['p3if.analysis.meta'] = sys.modules['analysis.meta']
    sys.modules['p3if.analysis.report'] = sys.modules['analysis.report']
    sys.modules['p3if.analysis.network'] = sys.modules['analysis.network']
    # Also add the class alias for ReportGenerator
    from analysis.report import AnalysisReport
    sys.modules['p3if.analysis.report'].ReportGenerator = AnalysisReport
except Exception:
    pass

__all__ = [
    'BasicAnalyzer',
    'NetworkAnalyzer',
    'MetaAnalyzer',
    'ReportGenerator'
] 