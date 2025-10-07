#!/usr/bin/env python3
"""Application runner script for VS Code launch configuration."""

import sys
import subprocess
import os

def main():
    print("=== App Runner Starting ===")
    
    # Get project root (parent of scripts/)
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    
    # Set up environment
    os.environ['PYTHONPATH'] = f"{project_root}:{project_root}/src"
    
    # Use Python 3.11 specifically
    python_cmd = "/opt/homebrew/bin/python3.11"
    
    # Check if Python 3.11 exists
    if not os.path.exists(python_cmd):
        print(f"ERROR: Python 3.11 not found at {python_cmd}")
        sys.exit(1)
    
    # Run the application with debug argument
    cmd = [
        python_cmd, "-m", "src.alphagen",
        "debug"
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
