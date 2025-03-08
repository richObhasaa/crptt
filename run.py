#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys
from setup import setup_environment

def check_dependencies():
    """
    Checks if required dependencies are installed
    
    Returns:
        bool: True if all dependencies are installed, False otherwise
    """
    try:
        import streamlit
        import pandas
        import numpy
        import plotly
        import requests
        import dotenv
        return True
    except ImportError as e:
        print(f"Missing dependency: {e.name}")
        return False

def install_dependencies():
    """
    Installs required dependencies
    
    Returns:
        bool: True if installation successful, False otherwise
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def run_app(debug=False):
    """
    Runs the Streamlit application
    
    Args:
        debug (bool): Whether to run in debug mode
    """
    # Create command
    command = ["streamlit", "run", "app.py"]
    
    # Add debug flag if needed
    if debug:
        os.environ["DEBUG"] = "1"
        command.append("--logger.level=debug")
    
    # Run the app
    subprocess.call(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Crypto Market Cap Analysis & Prediction application.")
    parser.add_argument("--setup", action="store_true", help="Run setup before starting the app")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies only")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    
    args = parser.parse_args()
    
    # Check dependencies if requested
    if args.check_deps:
        if check_dependencies():
            print("All dependencies are installed.")
            sys.exit(0)
        else:
            print("Some dependencies are missing. Run with --install-deps to install them.")
            sys.exit(1)
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing dependencies...")
        if install_dependencies():
            print("Dependencies installed successfully.")
        else:
            print("Failed to install dependencies.")
            sys.exit(1)
    
    # Run setup if requested
    if args.setup:
        print("Running setup...")
        setup_environment()
    
    # Run the app
    run_app(debug=args.debug)