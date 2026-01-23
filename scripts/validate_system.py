#!/usr/bin/env python3
"""
P3IF Comprehensive System Validation Script

Validates all components by running actual tests and checking system state.
"""
import subprocess
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timezone

# Add 'src' to pythonpath so we can import internal modules if needed
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from p3if.utils.logging import get_logger

logger = get_logger("validate_system")

def run_command(cmd, cwd=None):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or str(Path(__file__).parent.parent))
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, '', str(e)

def validate_test_results():
    """Run pytest and validate results"""
    print('🔍 EXECUTING TEST SUITE...')
    
    # Run all tests
    code, stdout, stderr = run_command('python -m pytest tests/ --tb=short -q')
    
    # Parse results from the last line, e.g. "255 passed in 2.34s"
    # or "255 passed, 1 failed in 2.34s"
    
    lines = stdout.strip().split('\n')
    summary_line = lines[-1] if lines else ""
    
    passed = 0
    failed = 0
    skipped = 0
    
    # Extract numbers using regex
    pass_match = re.search(r'(\d+) passed', summary_line)
    fail_match = re.search(r'(\d+) failed', summary_line)
    skip_match = re.search(r'(\d+) skipped', summary_line)
    
    if pass_match:
        passed = int(pass_match.group(1))
    if fail_match:
        failed = int(fail_match.group(1))
    if skip_match:
        skipped = int(skip_match.group(1))
        
    total = passed + failed + skipped
    
    results = {
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'total': total,
        'pass_rate': f"{(passed/total*100):.1f}%" if total > 0 else "0%"
    }
    
    if code != 0 or failed > 0:
        print(f'❌ Test execution failed: {failed} failed, {passed} passed')
        return False, results
        
    print(f'✅ Tests passed: {passed} passed, {skipped} skipped')
    return True, results

def validate_coverage():
    """Run coverage check"""
    print('🔍 CHECKING COVERAGE...')
    
    # Run coverage on core modules
    code, stdout, stderr = run_command('python -m pytest --cov=p3if.core --cov-report=term-missing tests/unit/test_models.py -q')
    
    if code != 0:
        print('❌ Coverage check failed execution')
        return False, {}
        
    # Extract total coverage from output
    # TOTAL     123    12    90%
    match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', stdout)
    
    if match:
        coverage_percent = int(match.group(1))
        print(f'✅ Coverage report generated: {coverage_percent}%')
        return True, {'coverage': f"{coverage_percent}%"}
    
    print('⚠️  Could not parse coverage percentage')
    return False, {}

def validate_core_functionality():
    """Validate core P3IF functionality works via integration test"""
    print('🔍 VALIDATING CORE FUNCTIONALITY...')
    
    # Create a simple test script that uses the actual library
    test_script = '''
import sys
import os
sys.path.insert(0, os.path.abspath("src"))

try:
    from p3if.core.models import Property, Process, Perspective
    from p3if.core.framework import P3IFFramework
    
    # Test pattern creation with required fields
    prop = Property(name="Test Property", description="Description", domain="test")
    proc = Process(name="Test Process", description="Description", domain="test")  
    persp = Perspective(name="Test Perspective", description="Description", domain="test", viewpoint="test")
    
    # Test framework
    framework = P3IFFramework()
    framework.add_pattern(prop)
    framework.add_pattern(proc)
    framework.add_pattern(persp)
    
    patterns = framework.get_pattern_collection().all_patterns()
    if len(patterns) == 3:
        print("SUCCESS_CORE_VALIDATION")
    else:
        print(f"ERROR: Expected 3 patterns, got {len(patterns)}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
'''
    
    # Write test script
    tmp_path = Path('/tmp/core_test.py')
    with open(tmp_path, 'w') as f:
        f.write(test_script)
    
    code, stdout, stderr = run_command(f'python {tmp_path}')
    
    if code == 0 and 'SUCCESS_CORE_VALIDATION' in stdout:
        print('✅ Core functionality validated (Integration Test)')
        return True, {}
    else:
        print('❌ Core functionality failed')
        print('STDOUT:', stdout)
        print('STDERR:', stderr)
        return False, {}

def generate_comprehensive_report():
    """Generate the final comprehensive validation report"""
    print('\n' + '='*70)
    print('🎯 P3IF COMPREHENSIVE SYSTEM VALIDATION REPORT')
    print('='*70)
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')
    print()
    
    # Run all validations
    validations = [
        ('Test Suite', validate_test_results()),
        ('Code Coverage', validate_coverage()),
        ('Core Integration', validate_core_functionality()),
    ]
    
    validation_results = {}
    all_passed = True
    
    print('\nVALIDATION RESULTS:')
    print('-' * 40)
    
    for name, (passed, details) in validations:
        status = '✅ PASSED' if passed else '❌ FAILED'
        print(f'{name:25} {status}')
        validation_results[name.lower().replace(' ', '_')] = {
            'status': 'passed' if passed else 'failed',
            'details': details
        }
        if not passed:
            all_passed = False
    
    overall_status = '✅ SYSTEM FULLY VALIDATED' if all_passed else '⚠️  ISSUES DETECTED'
    print(f'\nOVERALL SYSTEM STATUS: {overall_status}')
    
    # Save detailed results
    report_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'validation_results': validation_results,
        'overall_status': 'success' if all_passed else 'failure',
    }
    
    report_path = Path('/tmp/p3if_validation_report.json')
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f'\n📄 Detailed report saved to: {report_path}')
    
    return all_passed

if __name__ == '__main__':
    success = generate_comprehensive_report()
    sys.exit(0 if success else 1)
