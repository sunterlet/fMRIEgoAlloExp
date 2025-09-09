#!/usr/bin/env python3
"""
Enhanced Install Dependencies for fMRI Navigation Experiments
This script checks for Python installation and installs all required packages.
"""

import subprocess
import sys
import os
import platform

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required for fMRI experiments")
        print("Please install Python 3.8 or higher from https://www.python.org/downloads/")
        return False
    
    print("✅ Python version is compatible")
    return True

def check_pip():
    """Check if pip is available."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        print("Please install pip or upgrade Python")
        return False

def install_package(package):
    """Install a single package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("=== Enhanced fMRI Navigation Experiment - Dependency Installer ===\n")
    
    # Check system info
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Check Python version
    if not check_python_version():
        print("\n=== Python Installation Required ===")
        print("Please install Python 3.8+ from: https://www.python.org/downloads/")
        print("After installing Python, run this script again.")
        return False
    
    # Check pip
    if not check_pip():
        print("\n=== pip Installation Required ===")
        print("Please install pip or upgrade your Python installation.")
        return False
    
    print("\n=== Installing Dependencies ===")
    
    # Core dependencies (required)
    core_dependencies = [
        "pygame>=2.5.0",
        "pyserial>=3.5",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0"
    ]
    
    # Optional dependencies
    optional_dependencies = [
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "pytest>=6.0.0"
    ]
    
    print("Installing core dependencies...")
    core_success = True
    for package in core_dependencies:
        if not install_package(package):
            core_success = False
    
    print("\nInstalling optional dependencies...")
    optional_success = True
    for package in optional_dependencies:
        if not install_package(package):
            optional_success = False
    
    print("\n=== Installation Summary ===")
    if core_success:
        print("✅ All core dependencies installed successfully!")
        print("✅ fMRI experiments should now work properly")
    else:
        print("❌ Some core dependencies failed to install")
        print("❌ fMRI experiments may not work properly")
    
    if optional_success:
        print("✅ All optional dependencies installed successfully!")
    else:
        print("⚠️  Some optional dependencies failed to install")
        print("⚠️  Advanced features may not be available")
    
    print("\n=== Next Steps ===")
    print("1. Test the trigger functionality: python test_trigger.py")
    print("2. Run a practice experiment: python snake.py practice")
    print("3. For fMRI mode, ensure serial port is connected")
    
    return core_success

if __name__ == "__main__":
    main() 