#!/usr/bin/env python3
"""
Test script to verify the terminal menu displays correctly
"""

import subprocess
import sys
import time
from pathlib import Path

def test_terminal_menu():
    """Test that the terminal displays the numbered menu correctly."""

    terminal_script = Path(__file__).parent / "interactive_terminal.sh"

    if not terminal_script.exists():
        print("❌ Terminal script not found")
        return False

    print("🧪 Testing terminal menu display...")

    try:
        # Run the terminal script and capture the first few lines of output
        process = subprocess.Popen(
            [str(terminal_script), "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )

        stdout, stderr = process.communicate(timeout=10)

        print("✅ Terminal help output:")
        print("=" * 50)
        print(stdout)
        print("=" * 50)

        # Check if the numbered menu is present in the help
        expected_lines = [
            "1) Setup Environment",
            "2) Run All Tests",
            "3) Run All Examples",
            "4) Generate Visualizations",
            "5) Show System Status",
            "6) Help & Information",
            "0) Exit"
        ]

        success = True
        for expected_line in expected_lines:
            if expected_line in stdout:
                print(f"✅ Found: {expected_line}")
            else:
                print(f"❌ Missing: {expected_line}")
                success = False

        if success:
            print("🎉 Terminal menu test PASSED!")
        else:
            print("⚠️  Terminal menu test had some issues")

        return success

    except subprocess.TimeoutExpired:
        print("❌ Terminal script timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ Error running terminal: {e}")
        return False

if __name__ == "__main__":
    success = test_terminal_menu()
    sys.exit(0 if success else 1)
