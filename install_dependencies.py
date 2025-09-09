#!/usr/bin/env python3
"""
Installation script for fMRI Navigation Experiment
This script installs all required Python dependencies
"""

import sys
import subprocess
import os
import platform

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected.")
        print("This experiment requires Python 3.8 or higher.")
        print("Please download and install Python from: https://python.org/")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected.")
        return True

def install_requirements():
    """Install requirements from requirements.txt"""
    print("\n=== Installing Python Dependencies ===")
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        print("Please ensure you're running this script from the experiment directory.")
        return False
    
    try:
        # Install requirements
        print("Installing packages from requirements.txt...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True, capture_output=True, text=True)
        
        print("✅ All dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ pip not found! Please ensure Python is properly installed.")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    print("\n=== Testing Package Imports ===")
    
    required_packages = [
        'pygame', 'numpy', 'pandas', 'matplotlib'
    ]
    
    all_imports_successful = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ {package} import failed: {e}")
            all_imports_successful = False
    
    return all_imports_successful

def check_matlab_requirements():
    """Check if MATLAB requirements are met"""
    print("\n=== MATLAB Requirements Check ===")
    print("Please ensure the following are installed in MATLAB:")
    print("1. MATLAB R2018b or later")
    print("2. Psychtoolbox (http://psychtoolbox.org/)")
    print("3. Statistics and Machine Learning Toolbox")
    print("\nTo install Psychtoolbox in MATLAB, run:")
    print("  DownloadPsychtoolbox()")
    print("\nTo test your MATLAB setup, run:")
    print("  setup_experiment")

def main():
    """Main installation function"""
    print("=== fMRI Navigation Experiment - Dependency Installer ===")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python executable: {sys.executable}")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Installation failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n⚠️  Some packages failed to import.")
        print("You may need to restart your terminal/IDE and try again.")
        sys.exit(1)
    
    # Check MATLAB requirements
    check_matlab_requirements()
    
    print("\n✅ Installation completed successfully!")
    print("\nNext steps:")
    print("1. Open MATLAB")
    print("2. Navigate to the experiment directory")
    print("3. Run: setup_experiment")
    print("4. Run: fmri_session")

if __name__ == "__main__":
    main()
