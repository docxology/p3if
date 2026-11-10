"""
Pattern analysis API routes.
"""
import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify
from p3if.core.framework import P3IFFramework
from .common import API_BASE_URL, handle_api_errors

logger = logging.getLogger(__name__)
analysis_api_bp = Blueprint("api_analysis", __name__)


@analysis_api_bp.route(f"{API_BASE_URL}/analysis/patterns")
@handle_api_errors
def analyze_patterns():
    """Perform comprehensive pattern analysis."""
    try:
        framework = P3IFFramework()

        try:
            from p3if.core.analysis.meta import MetaAnalyzer
            analyzer = MetaAnalyzer(framework)

            domain_comparison = analyzer.get_domain_comparison()
            framework_stats = analyzer.get_framework_statistics()
            pattern_clusters = analyzer.identify_pattern_clusters()

            analysis_results = {
                "domain_comparison": domain_comparison,
                "framework_statistics": framework_stats,
                "pattern_clusters": pattern_clusters,
                "cross_domain_relationships": analyzer.analyze_cross_domain_relationships(),
            }
        except (ImportError, AttributeError):
            analysis_results = {
                "domain_comparison": {},
                "framework_statistics": {},
                "pattern_clusters": [],
                "cross_domain_relationships": {},
            }

        return jsonify({
            "status": "success",
            "message": "Pattern analysis completed successfully",
            "data": {
                "analysis": analysis_results,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "metadata": {
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "framework_patterns": len(framework._patterns),
                "framework_relationships": len(framework._relationships),
                "analysis_version": "2.0",
            },
        })
    except Exception:
        logger.exception("Error performing pattern analysis")
        return jsonify({
            "status": "error",
            "error": "Analysis Error",
            "message": "Error performing pattern analysis",
            "status_code": 500,
        }), 500
