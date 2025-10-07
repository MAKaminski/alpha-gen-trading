#!/usr/bin/env python3
"""
Wrapper to run pytest with cleaned sys.path
"""
import sys
import os

# CRITICAL: Clean sys.path FIRST before any other imports
sys.path = [p for p in sys.path if p and os.path.exists(p)]

# Now set up environment
workspace = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(workspace, 'src'))
sys.path.insert(0, workspace)

os.environ['PYTHONPATH'] = f"{workspace}/src:{workspace}"
os.environ['ALPHAGEN_USE_MOCK_DATA'] = 'true'

# Now import and run pytest
import pytest

# Run all tests
sys.exit(pytest.main([
    'tests',
    '-v'
]))

