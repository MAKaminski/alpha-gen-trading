"""
Main entry point for Alpha-Gen API server.
This file serves as the root-level main.py that Railway's Railpack can auto-detect.
"""

from backend.main import app

# Re-export the FastAPI app for Railway auto-detection
__all__ = ["app"]
