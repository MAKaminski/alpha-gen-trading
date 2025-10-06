#!/usr/bin/env python3
"""Development environment setup script for Alpha-Gen."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Set up the development environment."""
    print("🚀 Setting up Alpha-Gen development environment...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Create virtual environment
    if not Path(".venv").exists():
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        activate_cmd = ".venv\\Scripts\\activate"
        pip_cmd = ".venv\\Scripts\\pip"
    else:
        activate_cmd = "source .venv/bin/activate"
        pip_cmd = ".venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        sys.exit(1)
    
    if not run_command(f"{pip_cmd} install -e .[dev,test]", "Installing dependencies"):
        sys.exit(1)
    
    # Install pre-commit hooks
    if not run_command(f"{activate_cmd} && pre-commit install", "Installing pre-commit hooks"):
        print("⚠️  Pre-commit installation failed, but continuing...")
    
    # Create necessary directories
    directories = ["data", "charts", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Copy environment template
    env_example = Path("config/.env.example")
    env_file = Path("config/.env")
    
    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created config/.env from template")
        print("⚠️  Please edit config/.env with your API keys")
    
    # Run structure validation
    if not run_command(f"{activate_cmd} && python scripts/testing/check_structure.py", "Validating directory structure"):
        print("⚠️  Directory structure validation failed")
    
    # Run tests
    if not run_command(f"{activate_cmd} && pytest tests/unit -v", "Running unit tests"):
        print("⚠️  Some tests failed, but setup completed")
    
    print("\n🎉 Development environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Edit config/.env with your API keys")
    print("2. Run: python scripts/setup/setup_schwab_oauth.py")
    print("3. Run: python scripts/debug/debug_cli.py run")
    print("\n📚 Documentation:")
    print("- Setup guide: docs/setup/REAL_DATA_SETUP.md")
    print("- Architecture: docs/architecture.md")
    print("- Git workflow: docs/GIT_WORKFLOW.md")


if __name__ == "__main__":
    main()
