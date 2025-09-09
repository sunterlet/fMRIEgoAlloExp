#!/usr/bin/env python3
"""
Setup script for the exploration experiment.
This script checks dependencies and sets up the environment.
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("ERROR: Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package):
    """Check if a package is installed."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def setup_environment():
    """Set up the experiment environment."""
    print("Setting up exploration experiment environment...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check and install pygame
    if not check_package("pygame"):
        print("Installing pygame...")
        if install_package("pygame"):
            print("✓ pygame installed successfully")
        else:
            print("✗ Failed to install pygame")
            print("Try: pip install pygame --user")
            return False
    else:
        print("✓ pygame already installed")
    
    # Check required directories
    required_dirs = ["sounds", "Instructions-he", "results"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"✗ Missing directory: {dir_name}")
            return False
        else:
            print(f"✓ Directory found: {dir_name}")
    
    # Check required files
    required_files = [
        "sounds/beep.wav",
        "sounds/target.wav",
        "Instructions-he/1.png",
        "Instructions-he/2.png",
        "Instructions-he/3.png",
        "Instructions-he/4.png", 
        "Instructions-he/5.png",
        "Instructions-he/6.png",
        "Instructions-he/10.png"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"✗ Missing file: {file_path}")
            return False
        else:
            print(f"✓ File found: {file_path}")
    
    print("=" * 50)
    print("✓ Environment setup complete!")
    print("\nYou can now run:")
    print("  python one_target.py practice --participant TEST")
    print("  python one_target.py fmri --participant TEST --run 1")
    return True

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1) 