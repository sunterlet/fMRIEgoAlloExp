# fMRI Navigation Experiment - Virtual Environment Guide

This guide explains how to use the "Sun-Navigation" virtual environment for your fMRI experiments.

## 🎯 Why Virtual Environment?

Using a virtual environment ensures that:
- ✅ Your experiments don't interfere with other users' Python packages
- ✅ You have consistent, isolated dependencies
- ✅ Easy to reproduce the exact environment on different machines
- ✅ Safe to experiment with different package versions

## 🚀 Quick Setup

### Option 1: Automatic Setup (Recommended)
```bash
# Double-click this file or run from command line:
install_dependencies.bat
```

This will:
1. Create a virtual environment called "Sun-Navigation"
2. Install all required dependencies
3. Create a convenient activation script

### Option 2: Manual Setup
```bash
# Create virtual environment
python -m venv Sun-Navigation

# Activate virtual environment
Sun-Navigation\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

## 📁 File Structure After Setup

```
exploration/
├── Sun-Navigation/              # Virtual environment folder
│   ├── Scripts/
│   │   ├── activate.bat         # Activation script
│   │   ├── python.exe           # Python interpreter
│   │   └── pip.exe              # Package installer
│   └── Lib/site-packages/       # Installed packages
├── run_experiments.bat          # Easy activation script
├── install_dependencies.bat     # Setup script
├── requirements.txt             # Package list
├── snake.py                     # Main experiment
├── one_target.py                # One target experiment
├── multi_arena.py               # Multi-arena experiment
└── trigger_utils.py             # Trigger functionality
```

## 🔧 Using the Virtual Environment

### Activating the Environment

**Option 1: Easy activation (recommended)**
```bash
# Double-click this file:
run_experiments.bat
```

**Option 2: Manual activation**
```bash
Sun-Navigation\Scripts\activate.bat
```

**Option 3: PowerShell activation**
```powershell
Sun-Navigation\Scripts\Activate.ps1
```

### Deactivating the Environment
```bash
deactivate
```

## 🧪 Running Experiments

Once the virtual environment is activated:

### Test Trigger Functionality
```bash
python test_trigger.py
```

### Run Practice Experiments
```bash
# Snake game practice
python snake.py practice

# One target practice
python one_target.py practice

# Multi-arena practice
python multi_arena.py practice
```

### Run fMRI Experiments
```bash
# Snake fMRI mode
python snake.py fmri --participant TEST --run 1 --trial 1 --total-trials 4 --scanning --com com4 --tr 2.0

# One target fMRI mode
python one_target.py fmri --participant TEST --run 1 --trial 1 --total-trials 4 --scanning --com com4 --tr 2.0

# Multi-arena fMRI mode
python multi_arena.py fmri --participant TEST --run 1 --trial 1 --total-trials 4 --scanning --com com4 --tr 2.0
```

## 🔍 Verifying the Environment

### Check if Virtual Environment is Active
```bash
# Should show the virtual environment path
echo %VIRTUAL_ENV%
```

### List Installed Packages
```bash
pip list
```

### Check Python Location
```bash
where python
# Should point to Sun-Navigation\Scripts\python.exe
```

## 🛠️ Troubleshooting

### Common Issues

1. **"python is not recognized"**
   - Make sure Python is installed and in PATH
   - Try running: `python --version`

2. **"venv module not found"**
   - Upgrade Python to 3.8+ which includes venv
   - Or install venv: `pip install virtualenv`

3. **"Permission denied"**
   - Run as administrator
   - Or use: `pip install --user package_name`

4. **"Virtual environment not activated"**
   - Make sure you see `(Sun-Navigation)` in your command prompt
   - Run: `Sun-Navigation\Scripts\activate.bat`

### Recreating the Environment

If something goes wrong, you can recreate the environment:

```bash
# Remove old environment
rmdir /s Sun-Navigation

# Run setup again
install_dependencies.bat
```

## 📋 Package List

The virtual environment includes:

**Core Dependencies:**
- `pygame>=2.5.0` - Game interface
- `pyserial>=3.5` - Serial communication for triggers
- `numpy>=1.21.0` - Numerical computing
- `pandas>=1.3.0` - Data analysis
- `matplotlib>=3.5.0` - Plotting

**Optional Dependencies:**
- `seaborn>=0.11.0` - Advanced plotting
- `scipy>=1.7.0` - Scientific computing
- `scikit-learn>=1.0.0` - Machine learning
- `pytest>=6.0.0` - Testing framework

## 🔄 Updating Dependencies

To update packages in the virtual environment:

```bash
# Activate environment
Sun-Navigation\Scripts\activate.bat

# Update specific package
pip install --upgrade package_name

# Update all packages
pip install --upgrade -r requirements.txt
```

## 🗑️ Removing the Environment

To completely remove the virtual environment:

```bash
# Deactivate first
deactivate

# Remove the folder
rmdir /s Sun-Navigation
```

## 💡 Tips

1. **Always activate the environment** before running experiments
2. **Keep the environment folder** - don't delete it accidentally
3. **Use `run_experiments.bat`** for easy access
4. **Check the command prompt** - you should see `(Sun-Navigation)` when active
5. **Backup the environment** if you need to recreate it elsewhere

## 🆘 Support

If you encounter issues:
1. Check that the virtual environment is activated
2. Verify Python version (3.8+)
3. Try recreating the environment
4. Check the troubleshooting section above 