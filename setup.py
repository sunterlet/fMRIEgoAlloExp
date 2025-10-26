#!/usr/bin/env python3
"""
Quick setup script for fMRI dependencies
"""
import subprocess
import sys
import os

print("="*80)
print("fMRI Session Dependencies - Quick Setup")
print("="*80)

# Check Python version
print(f"\nPython version: {sys.version}")
if sys.version_info < (3, 8):
    print("[WARN] Python 3.8+ is recommended")

# Install Python dependencies
print("\nInstalling Python dependencies...")
requirements = os.path.join(os.path.dirname(__file__), 'exploration', 'requirements.txt')
if os.path.exists(requirements):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements])
        print("[OK] Python dependencies installed successfully")
    except Exception as e:
        print(f"[ERROR] Error installing dependencies: {e}")
        print("  Try manually: pip install -r exploration/requirements.txt")
else:
    print("[WARN] requirements.txt not found")

print("\n" + "="*80)
print("Setup complete!")
print("="*80)
print("\nNext steps:")
print("1. Install MATLAB with Psychtoolbox-3")
print("2. Install Instrument Control Toolbox (for fMRI trigger)")
print("3. Run fmri_session.m in MATLAB")
print("\nFor more information, see README.md")
