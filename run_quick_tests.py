#!/usr/bin/env python3
"""Quick test runner script for VS Code launch configuration - Unit tests only."""

import sys
import subprocess
import os

def main():
    print("=== Quick Test Runner Starting (Unit Tests Only) ===")
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
    
    # Run pytest with unit tests only (much faster)
    # Exclude integration and E2E tests that might hang
    cmd = [
        python_cmd, "-m", "pytest",
        "tests/unit/",
        "-v",
        "--tb=short",
        "--maxfail=5",
        "-x",  # Stop on first failure
        "--ignore=tests/integration/",  # Skip integration tests
        "--ignore=tests/e2e/",  # Skip E2E tests
        "-m", "not slow"  # Skip any tests marked as slow
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
