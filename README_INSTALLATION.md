# fMRI Navigation Experiment - Installation Guide

This guide explains how to install all dependencies for the fMRI navigation experiments.

## Quick Installation

### Option 1: Using the batch file (Windows)
```bash
# Double-click the file or run from command line:
install_dependencies.bat
```

### Option 2: Using the Python script
```bash
python install_dependencies.py
```

### Option 3: Using pip directly
```bash
pip install -r requirements.txt
```

## Manual Installation

If you prefer to install dependencies manually, here are the core packages you need:

### Core Dependencies (Required)
```bash
pip install pygame>=2.5.0
pip install pyserial>=3.5
pip install numpy>=1.21.0
pip install pandas>=1.3.0
pip install matplotlib>=3.5.0
```

### Optional Dependencies
```bash
pip install seaborn>=0.11.0
pip install scipy>=1.7.0
pip install scikit-learn>=1.0.0
pip install pytest>=6.0.0
```

## Verification

After installation, test that everything works:

1. **Test trigger functionality:**
   ```bash
   python test_trigger.py
   ```

2. **Test a practice experiment:**
   ```bash
   python snake.py practice
   ```

3. **Test fMRI mode (requires serial port):**
   ```bash
   python snake.py fmri --participant TEST --run 1 --trial 1 --total-trials 4 --scanning --com com4 --tr 2.0
   ```

## Troubleshooting

### Common Issues

1. **"No module named 'serial'"**
   - Solution: `pip install pyserial`

2. **"No module named 'pygame'"**
   - Solution: `pip install pygame`

3. **Serial port not found**
   - This is normal if no physical serial port is connected
   - For testing, you can disable scanning mode

4. **Permission errors**
   - Try: `pip install --user package_name`
   - Or run as administrator

### Python Version
- Recommended: Python 3.8 or higher
- Tested with: Python 3.10

## File Structure

```
exploration/
├── requirements.txt              # List of all dependencies
├── install_dependencies.py      # Python installation script
├── install_dependencies.bat     # Windows batch installer
├── README_INSTALLATION.md      # This file
├── test_trigger.py             # Test trigger functionality
├── snake.py                    # Main snake experiment
├── one_target.py               # One target experiment
├── multi_arena.py              # Multi-arena experiment
└── trigger_utils.py            # Trigger functionality
```

## Next Steps

After successful installation:

1. **For Practice Mode:** Run experiments without scanner triggers
2. **For fMRI Mode:** Ensure serial port connection to scanner
3. **For Development:** Use the test scripts to verify functionality

## Support

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Verify Python version compatibility
3. Test with practice mode first
4. Check serial port configuration for fMRI mode 