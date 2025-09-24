#!/usr/bin/env python3
"""
P3IF Test Runner (Legacy Wrapper)

This is a legacy wrapper that redirects to the comprehensive test runner.
For full functionality, use run_tests.py instead.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main function - redirect to comprehensive test runner."""
    print("P3IF Test Runner (Legacy)")
    print("=========================")
    print("⚠️  This is a legacy wrapper. For comprehensive testing with:")
    print("   - Detailed logging and validation")
    print("   - Coverage reporting")
    print("   - Output confirmation")
    print("   - Better error reporting")
    print()
    print("Please use: python run_tests.py")
    print()
    print("Redirecting to comprehensive test runner...")
    print()

    # Import and run the comprehensive test runner
    try:
        from run_tests import main as comprehensive_main
        return comprehensive_main()
    except ImportError as e:
        print(f"❌ Failed to import comprehensive test runner: {e}")
        print("Please ensure run_tests.py exists and dependencies are installed.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
