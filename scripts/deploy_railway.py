#!/usr/bin/env python3
"""
Railway deployment helper script.
This script helps prepare and deploy the Alpha-Gen backend to Railway.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_railway_cli():
    """Check if Railway CLI is installed."""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not installed")
        return False

def check_railway_auth():
    """Check if Railway is authenticated."""
    try:
        result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway authenticated as: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway not authenticated")
            print("Please run: railway login")
            return False
    except Exception as e:
        print(f"❌ Error checking Railway auth: {e}")
        return False

def install_railway_cli():
    """Install Railway CLI."""
    print("Installing Railway CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Railway CLI: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = [
        'SCHWAB_CLIENT_ID',
        'SCHWAB_CLIENT_SECRET',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your Railway project dashboard.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_dockerfile():
    """Check if Dockerfile exists and is valid."""
    dockerfile_path = Path("deploy/Dockerfile")
    if not dockerfile_path.exists():
        print("❌ Dockerfile not found at deploy/Dockerfile")
        return False
    
    print("✅ Dockerfile found")
    return True

def check_railway_config():
    """Check if railway.json exists."""
    config_path = Path("railway.json")
    if not config_path.exists():
        print("❌ railway.json not found")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        print("✅ railway.json is valid")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ railway.json is invalid: {e}")
        return False

def deploy_to_railway():
    """Deploy to Railway."""
    print("Deploying to Railway...")
    try:
        subprocess.run(['railway', 'up'], check=True)
        print("✅ Deployment successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False

def main():
    """Main deployment function."""
    print("🚀 Alpha-Gen Railway Deployment Helper")
    print("=" * 50)
    
    # Check prerequisites
    if not check_railway_cli():
        if not install_railway_cli():
            print("Please install Railway CLI manually: npm install -g @railway/cli")
            return False
    
    if not check_railway_auth():
        print("\n🔐 Railway Authentication Required")
        print("Please run: railway login")
        print("This will open a browser window for authentication.")
        return False
    
    if not check_dockerfile():
        return False
    
    if not check_railway_config():
        return False
    
    # Check environment variables (optional for this script)
    print("\n📋 Environment Variables Check:")
    check_environment_variables()
    
    print("\n🚀 Ready to deploy!")
    print("Make sure you have:")
    print("1. Logged into Railway: railway login")
    print("2. Linked your project: railway link")
    print("3. Set environment variables in Railway dashboard")
    
    response = input("\nDeploy now? (y/N): ").lower().strip()
    if response == 'y':
        return deploy_to_railway()
    else:
        print("Deployment cancelled. Run this script again when ready.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
