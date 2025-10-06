#!/usr/bin/env python3
"""
Railway startup script for Alpha-Gen backend.
This script handles Railway-specific configuration and starts the FastAPI server.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set environment variables for Railway
os.environ.setdefault("PYTHONPATH", str(src_path))
os.environ.setdefault("PYTHONUNBUFFERED", "1")

def main():
    """Start the FastAPI server for Railway deployment."""
    # Get port from Railway environment variable
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting Alpha-Gen API server on {host}:{port}")
    print(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    
    # Import and run the FastAPI app
    from backend.main import app
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
