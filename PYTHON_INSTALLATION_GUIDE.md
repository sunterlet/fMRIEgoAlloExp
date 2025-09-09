# Python Installation Guide for fMRI Navigation Experiments (Windows)

## Problem
The MATLAB functions `run_snake_game`, `run_one_target`, and `run_multi_arena` require Python to run the underlying experiment scripts. If you see the error:
```
'python' is not recognized as an internal or external command
```
This means Python is not installed or not in your system PATH.

## Solution: Install Python on Windows

### Step 1: Download Python
1. Go to https://www.python.org/downloads/
2. Click "Download Python" (latest version, 3.8 or higher)
3. Download the Windows installer

### Step 2: Install Python
1. Run the downloaded installer
2. **IMPORTANT**: Check the box "Add Python to PATH" during installation
3. Click "Install Now"
4. Wait for installation to complete

### Step 3: Verify Installation
1. Open a new PowerShell window
2. Run: `py --version`
3. You should see something like: `Python 3.13.5`

### Step 4: Install Dependencies
1. Navigate to your fMRI experiment directory
2. Run the dependency installer:
   ```powershell
   .\install_dependencies_enhanced.bat
   ```
   
   Or manually install dependencies:
   ```powershell
   py -m pip install pygame pandas matplotlib seaborn pyserial
   ```

### Step 5: Test the Setup
1. Restart MATLAB
2. Run the test script:
   ```matlab
   test_python_detection
   ```
3. Run your practice sessions:
   ```matlab
   practice_sessions
   ```

## How It Works

The MATLAB functions now use intelligent Python detection:

1. **Primary**: Tries `py` command (Windows Python launcher)
2. **Fallback**: Tries `python` command
3. **Fallback**: Tries `python3` command
4. **Fallback**: Searches common Windows installation paths
5. **Error**: Provides helpful installation instructions

## Updated MATLAB Functions

The MATLAB functions have been optimized for Windows:

- `exploration/run_snake_game.m` - Updated with Windows-specific Python detection
- `exploration/run_one_target.m` - Updated with Windows-specific Python detection  
- `exploration/run_multi_arena.m` - Updated with Windows-specific Python detection

## File Structure
```
fMRI/
├── exploration/
│   ├── run_snake_game.m      # Updated with Windows Python detection
│   ├── run_one_target.m      # Updated with Windows Python detection  
│   ├── run_multi_arena.m     # Updated with Windows Python detection
│   ├── snake_out.py          # Python script for snake practice
│   ├── one_target_out.py     # Python script for one-target practice
│   ├── multi_arena.py        # Python script for multi-arena experiments
│   └── requirements.txt      # Python dependencies
├── install_dependencies_enhanced.bat    # Enhanced installer
├── install_dependencies_VENV.bat        # Virtual environment installer
├── test_python_detection.m              # Test script
└── PYTHON_INSTALLATION_GUIDE.md        # This guide
```

## Troubleshooting

### Python not found after installation
- Restart your computer
- Make sure "Add Python to PATH" was checked during installation
- Try running `py --version` in a new terminal window

### Permission errors during installation
- Run PowerShell as Administrator
- Or use the virtual environment approach

### Dependencies fail to install
- Check your internet connection
- Try running: `py -m pip install --upgrade pip`
- Then install dependencies: `py -m pip install pygame pandas matplotlib seaborn pyserial`

### MATLAB still can't find Python
- Run the test script: `test_python_detection`
- Check the output to see which Python command is being used
- Make sure MATLAB is restarted after Python installation

## Support
If you continue to have issues:
1. Check that Python is properly installed: `py --version`
2. Verify dependencies are installed: `py -c "import pygame; print('pygame OK')"`
3. Run the test script: `test_python_detection`
4. Check the MATLAB error messages for specific Python script errors 