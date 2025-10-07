#!/usr/bin/env python3
"""Fast test runner script - only runs a few key tests for quick feedback."""

import sys
import subprocess
import os

def main():
    print("=== Fast Test Runner Starting (Key Tests Only) ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    
    # Set up environment
    os.environ['PYTHONPATH'] = f"{os.getcwd()}:{os.getcwd()}/src"
    
    # Use Python 3.11 specifically
    python_cmd = "/opt/homebrew/bin/python3.11"
    
    # Check if Python 3.11 exists
    if not os.path.exists(python_cmd):
        print(f"ERROR: Python 3.11 not found at {python_cmd}")
        sys.exit(1)
    
    # Run only a few key tests for quick feedback
    cmd = [
        python_cmd, "-m", "pytest",
        "tests/unit/test_app_simple.py",  # Just the app tests
        "tests/unit/test_events.py",      # Just the events tests
        "tests/unit/test_storage_simple.py",  # Just the storage tests
        "-v",
        "--tb=short",
        "--maxfail=3",
        "-x"  # Stop on first failure
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print("-" * 50)
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=False)
        print(f"Command completed with exit code: {result.returncode}")
        sys.exit(result.returncode)
    except Exception as e:
        print(f"ERROR running command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
