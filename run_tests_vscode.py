#!/usr/bin/env python3
"""
VS Code compatible test runner with detailed error logging
"""
import sys
import os
import subprocess
import traceback
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_vscode.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def log_system_info():
    """Log detailed system information"""
    logger.info("=== SYSTEM INFO ===")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    logger.info(f"ALPHAGEN_USE_MOCK_DATA: {os.environ.get('ALPHAGEN_USE_MOCK_DATA')}")
    
    # Check if paths exist
    src_path = os.path.join(os.getcwd(), 'src')
    logger.info(f"src directory exists: {os.path.exists(src_path)}")
    logger.info(f"src directory contents: {os.listdir(src_path) if os.path.exists(src_path) else 'N/A'}")
    
    # Check Python executable
    logger.info(f"Python executable exists: {os.path.exists(sys.executable)}")
    logger.info(f"Python executable is file: {os.path.isfile(sys.executable)}")
    logger.info(f"Python executable is symlink: {os.path.islink(sys.executable)}")
    
    if os.path.islink(sys.executable):
        try:
            real_path = os.readlink(sys.executable)
            logger.info(f"Python executable real path: {real_path}")
            logger.info(f"Real path exists: {os.path.exists(real_path)}")
        except Exception as e:
            logger.error(f"Error reading symlink: {e}")

def main():
    try:
        logger.info("Starting VS Code test runner")
        
        # Set up environment FIRST
        os.environ['PYTHONPATH'] = f"{os.getcwd()}/src:{os.getcwd()}"
        os.environ['ALPHAGEN_USE_MOCK_DATA'] = 'true'
        
        # Clean up sys.path to remove empty strings and non-existent paths
        sys.path = [p for p in sys.path if p and os.path.exists(p)]
        sys.path.insert(0, f"{os.getcwd()}/src")
        sys.path.insert(0, os.getcwd())
        
        logger.info("Environment set up complete")
        
        # Log system info
        log_system_info()
        
        # Try to import alphagen first
        logger.info("Attempting to import alphagen...")
        try:
            import alphagen
            logger.info("✓ Successfully imported alphagen")
        except Exception as e:
            logger.error(f"✗ Failed to import alphagen: {e}")
            logger.error(f"Import traceback: {traceback.format_exc()}")
            return 1
        
        # Run a simple test
        logger.info("Running test...")
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/unit/test_oauth_token.py::TestOAuthTokenHandling::test_token_validation_success', 
            '-v', '--tb=short'
        ], cwd=os.getcwd(), capture_output=True, text=True)
        
        logger.info(f"Test completed with exit code: {result.returncode}")
        logger.info(f"Test stdout: {result.stdout}")
        if result.stderr:
            logger.info(f"Test stderr: {result.stderr}")
        
        return result.returncode
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    logger.info(f"Exiting with code: {exit_code}")
    sys.exit(exit_code)
