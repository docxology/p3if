#!/usr/bin/env python3
"""
P3IF Documentation Validation Script

Validates that all documentation accurately reflects the current implementation
and capabilities of the P3IF system.
"""
import os
import sys
import logging
from pathlib import Path
import subprocess
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentationValidator:
    """Validates P3IF documentation accuracy."""
    
    def __init__(self):
        self.project_root = project_root
        self.docs_dir = self.project_root / "docs"
        self.scripts_dir = self.project_root / "scripts"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
    
    def validate_script_existence(self):
        """Validate that documented scripts actually exist."""
        logger.info("🔍 Validating script existence...")
        
        documented_scripts = [
            "generate_final_visualizations.py",
            "run_multidomain_portal.py", 
            "benchmark_performance.py",
            "update_domain_files.py",
            "test_3d_cube_with_domains.py",
            "view_p3if_website.py"
        ]
        
        for script in documented_scripts:
            script_path = self.scripts_dir / script
            test_result = {
                "test": f"Script exists: {script}",
                "status": "PASS" if script_path.exists() else "FAIL",
                "details": f"Path: {script_path}"
            }
            self.validation_results["tests"].append(test_result)
            
            if test_result["status"] == "PASS":
                self.validation_results["summary"]["passed"] += 1
                logger.info(f"✅ {script} exists")
            else:
                self.validation_results["summary"]["failed"] += 1
                logger.error(f"❌ {script} missing")
    
    def validate_visualization_generation(self):
        """Validate that visualization generation works as documented."""
        logger.info("🎨 Validating visualization generation...")
        
        try:
            # Run the main visualization script
            result = subprocess.run([
                sys.executable, 
                str(self.scripts_dir / "generate_final_visualizations.py")
            ], capture_output=True, text=True, timeout=300)
            
            test_result = {
                "test": "Visualization generation execution",
                "status": "PASS" if result.returncode == 0 else "FAIL",
                "details": f"Return code: {result.returncode}"
            }
            
            if result.returncode != 0:
                test_result["error"] = result.stderr
            
            self.validation_results["tests"].append(test_result)
            
            if test_result["status"] == "PASS":
                self.validation_results["summary"]["passed"] += 1
                logger.info("✅ Visualization generation successful")
                
                # Validate expected output files
                self._validate_output_files()
            else:
                self.validation_results["summary"]["failed"] += 1
                logger.error(f"❌ Visualization generation failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            test_result = {
                "test": "Visualization generation execution",
                "status": "FAIL",
                "details": "Timeout after 300 seconds"
            }
            self.validation_results["tests"].append(test_result)
            self.validation_results["summary"]["failed"] += 1
            logger.error("❌ Visualization generation timed out")
    
    def _validate_output_files(self):
        """Validate that expected output files are generated."""
        logger.info("📁 Validating output file structure...")
        
        # Find the latest output directory
        output_dir = self.project_root / "output"
        if not output_dir.exists():
            test_result = {
                "test": "Output directory exists",
                "status": "FAIL",
                "details": "No output directory found"
            }
            self.validation_results["tests"].append(test_result)
            self.validation_results["summary"]["failed"] += 1
            return
        
        # Get the most recent session directory
        session_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("p3if_output_")]
        if not session_dirs:
            test_result = {
                "test": "Session directory exists",
                "status": "FAIL", 
                "details": "No session directories found"
            }
            self.validation_results["tests"].append(test_result)
            self.validation_results["summary"]["failed"] += 1
            return
        
        latest_session = max(session_dirs, key=lambda x: x.name)
        
        # Expected files as documented
        expected_files = [
            "visualizations/networks/small_network.png",
            "visualizations/networks/large_network.png", 
            "visualizations/statistics/pattern_statistics.png",
            "animations/framework/p3if_components.gif",
            "reports/visualization_report.md",
            "session_metadata.json"
        ]
        
        for expected_file in expected_files:
            file_path = latest_session / expected_file
            test_result = {
                "test": f"Output file exists: {expected_file}",
                "status": "PASS" if file_path.exists() else "FAIL",
                "details": f"Path: {file_path}"
            }
            self.validation_results["tests"].append(test_result)
            
            if test_result["status"] == "PASS":
                self.validation_results["summary"]["passed"] += 1
                logger.info(f"✅ {expected_file} exists")
            else:
                self.validation_results["summary"]["failed"] += 1
                logger.error(f"❌ {expected_file} missing")
    
    def validate_core_modules(self):
        """Validate that core modules can be imported."""
        logger.info("🔧 Validating core module imports...")
        
        core_modules = [
            "core.framework",
            "core.models", 
            "visualization.interactive",
            "utils.output_organizer",
            "utils.performance",
            "data.synthetic"
        ]
        
        for module in core_modules:
            try:
                __import__(module)
                test_result = {
                    "test": f"Import module: {module}",
                    "status": "PASS",
                    "details": "Successfully imported"
                }
                self.validation_results["summary"]["passed"] += 1
                logger.info(f"✅ {module} imported successfully")
            except ImportError as e:
                test_result = {
                    "test": f"Import module: {module}",
                    "status": "FAIL",
                    "details": f"Import error: {str(e)}"
                }
                self.validation_results["summary"]["failed"] += 1
                logger.error(f"❌ {module} import failed: {e}")
            
            self.validation_results["tests"].append(test_result)
    
    def validate_documentation_files(self):
        """Validate that all documented files exist."""
        logger.info("📚 Validating documentation files...")
        
        expected_docs = [
            "README.md",
            "concepts/P3IF.md",
            "concepts/CategoryTheory_P3IF.md", 
            "concepts/CognitiveSecurity_P3IF.md",
            "concepts/domain_integration.md",
            "api/README.md",
            "visualization/README.md",
            "visualization/technical_documentation.md",
            "examples/README.md",
            "diagrams/process-flows.md",
            "diagrams/system-architecture.md"
        ]
        
        for doc_file in expected_docs:
            file_path = self.docs_dir / doc_file
            test_result = {
                "test": f"Documentation file exists: {doc_file}",
                "status": "PASS" if file_path.exists() else "FAIL",
                "details": f"Path: {file_path}"
            }
            self.validation_results["tests"].append(test_result)
            
            if test_result["status"] == "PASS":
                self.validation_results["summary"]["passed"] += 1
                logger.info(f"✅ {doc_file} exists")
            else:
                self.validation_results["summary"]["failed"] += 1
                logger.error(f"❌ {doc_file} missing")
    
    def generate_report(self):
        """Generate validation report."""
        self.validation_results["summary"]["total"] = (
            self.validation_results["summary"]["passed"] + 
            self.validation_results["summary"]["failed"]
        )
        
        # Save detailed results
        report_path = self.project_root / "validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        # Print summary
        summary = self.validation_results["summary"]
        logger.info("\n" + "="*60)
        logger.info("📋 DOCUMENTATION VALIDATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total Tests: {summary['total']}")
        logger.info(f"Passed: {summary['passed']}")
        logger.info(f"Failed: {summary['failed']}")
        
        if summary['failed'] == 0:
            logger.info("🎉 ALL DOCUMENTATION VALIDATION TESTS PASSED!")
        else:
            logger.warning(f"⚠️  {summary['failed']} tests failed")
        
        logger.info(f"📄 Detailed report saved to: {report_path}")
        
        return summary['failed'] == 0
    
    def run_validation(self):
        """Run all validation tests."""
        logger.info("🚀 Starting P3IF documentation validation...")
        
        self.validate_documentation_files()
        self.validate_script_existence()
        self.validate_core_modules()
        self.validate_visualization_generation()
        
        return self.generate_report()


def main():
    """Main function."""
    validator = DocumentationValidator()
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
