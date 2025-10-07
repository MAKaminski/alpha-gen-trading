#!/usr/bin/env python3
"""Test runner script for VS Code launch configuration."""

import sys
import subprocess
import os

def main():
    print("=== Test Runner Starting ===")
    
    # Get project root (parent of scripts/)
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    
    # Set up environment
    os.environ['PYTHONPATH'] = f"{project_root}/src:{project_root}"
    # Use mock data for tests to avoid OAuth issues
    os.environ['ALPHAGEN_USE_MOCK_DATA'] = 'true'
    
    # Use system Python 3.11
    python_cmd = "/opt/homebrew/bin/python3.11"
    
    # Check if Python 3.11 exists
    if not os.path.exists(python_cmd):
        print(f"ERROR: Python 3.11 not found at {python_cmd}")
        sys.exit(1)
    
    # Run pytest with all the arguments
    cmd = [
        python_cmd, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=src/alphagen",
        "--cov-report=term-missing",
        "--cov-fail-under=30",
        "--timeout=300"  # 5 minute timeout for full test suite
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
