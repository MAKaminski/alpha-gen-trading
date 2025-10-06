#!/usr/bin/env python3
"""Validate directory structure compliance."""

import os
import sys
from pathlib import Path


# Allowed files at root level
ALLOWED_ROOT_FILES = {
    'pyproject.toml',
    'pytest.ini', 
    'README.md',
    '.gitignore',
    '.pre-commit-config.yaml',
    'DIRECTORY_STRUCTURE.md'  # This file itself
}

# Required directories
REQUIRED_DIRECTORIES = {
    'src',
    'tests', 
    'scripts',
    'config',
    'docs',
    'deploy',
    'data',
    'charts',
    'examples',
    '.github'
}

# Required script subdirectories
REQUIRED_SCRIPT_DIRS = {
    'scripts/setup',
    'scripts/debug', 
    'scripts/testing'
}

# Required doc subdirectories
REQUIRED_DOC_DIRS = {
    'docs/setup',
    'docs/architecture'
}


def check_root_files():
    """Check that only allowed files exist at root level."""
    root = Path('.')
    violations = []
    
    for item in root.iterdir():
        if item.is_file() and item.name not in ALLOWED_ROOT_FILES:
            violations.append(f"❌ Unauthorized file at root: {item.name}")
    
    return violations


def check_required_directories():
    """Check that required directories exist."""
    violations = []
    
    for dir_path in REQUIRED_DIRECTORIES:
        if not Path(dir_path).exists():
            violations.append(f"❌ Missing required directory: {dir_path}")
    
    return violations


def check_script_structure():
    """Check script directory structure."""
    violations = []
    
    for dir_path in REQUIRED_SCRIPT_DIRS:
        if not Path(dir_path).exists():
            violations.append(f"❌ Missing required script directory: {dir_path}")
    
    # Check for loose files in scripts directory
    scripts_dir = Path('scripts')
    if scripts_dir.exists():
        for item in scripts_dir.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                violations.append(f"❌ Loose file in scripts directory: {item}")
    
    return violations


def check_doc_structure():
    """Check documentation directory structure."""
    violations = []
    
    for dir_path in REQUIRED_DOC_DIRS:
        if not Path(dir_path).exists():
            violations.append(f"❌ Missing required doc directory: {dir_path}")
    
    return violations


def main():
    """Main validation function."""
    print("🔍 Validating directory structure...")
    
    all_violations = []
    all_violations.extend(check_root_files())
    all_violations.extend(check_required_directories())
    all_violations.extend(check_script_structure())
    all_violations.extend(check_doc_structure())
    
    if all_violations:
        print("\n❌ Directory structure violations found:")
        for violation in all_violations:
            print(f"  {violation}")
        
        print("\n📋 To fix these issues:")
        print("  1. Move files to appropriate subdirectories")
        print("  2. Create missing directories")
        print("  3. See DIRECTORY_STRUCTURE.md for guidance")
        
        return 1
    else:
        print("✅ Directory structure is compliant!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
