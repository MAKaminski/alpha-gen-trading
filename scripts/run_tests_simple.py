#!/usr/bin/env python3
"""Simple test runner for local debugging."""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent  # Go up one level from scripts/
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ['ALPHAGEN_USE_MOCK_DATA'] = 'true'
os.environ['PYTHONPATH'] = f"{project_root}/src:{project_root}"

# Import pytest and run
import pytest

if __name__ == "__main__":
    # Run pytest with arguments
    args = [
        "tests/",
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure for faster debugging
    ]
    
    # Add any command line arguments
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    
    print(f"Running pytest with args: {args}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"Python path: {sys.path[:3]}")
    print("-" * 50)
    
    sys.exit(pytest.main(args))

