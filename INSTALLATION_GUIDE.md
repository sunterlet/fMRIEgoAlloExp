# Installation Guide - fMRI Navigation Experiment

This guide will help you set up the fMRI Navigation Experiment on a new computer.

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/fMRI-Navigation-Experiment.git
   cd fMRI-Navigation-Experiment
   ```

2. **Install Python dependencies:**
   ```bash
   python install_dependencies.py
   ```

3. **Set up MATLAB environment:**
   - Open MATLAB
   - Navigate to the experiment directory
   - Run: `setup_experiment`

4. **Run the experiment:**
   ```matlab
   fmri_session
   ```

### Option 2: Manual Setup

If the automated setup doesn't work, follow the manual steps below.

## Prerequisites

### 1. MATLAB Requirements

- **MATLAB R2018b or later**
- **Psychtoolbox** - Download from [psychtoolbox.org](http://psychtoolbox.org/)
- **Statistics and Machine Learning Toolbox** (for data processing)

#### Installing Psychtoolbox in MATLAB:
```matlab
% In MATLAB command window:
DownloadPsychtoolbox()
```

### 2. Python Requirements

- **Python 3.8 or later** - Download from [python.org](https://python.org/)
- **Required packages** (installed automatically):
  - pygame >= 2.5.0
  - numpy >= 1.21.0
  - pandas >= 1.3.0
  - matplotlib >= 3.5.0

#### Installing Python Dependencies:
```bash
pip install -r requirements.txt
```

## Detailed Installation Steps

### Step 1: Download the Repository

```bash
git clone https://github.com/yourusername/fMRI-Navigation-Experiment.git
cd fMRI-Navigation-Experiment
```

### Step 2: Install Python Dependencies

#### Windows:
```cmd
python install_dependencies.py
```

#### macOS/Linux:
```bash
python3 install_dependencies.py
```

#### Manual Installation:
```bash
pip install -r requirements.txt
```

### Step 3: Set up MATLAB Environment

1. **Open MATLAB**
2. **Navigate to the experiment directory:**
   ```matlab
   cd /path/to/fMRI-Navigation-Experiment
   ```
3. **Run the setup script:**
   ```matlab
   setup_experiment
   ```

### Step 4: Test the Installation

1. **Test Python setup:**
   ```bash
   python -c "import pygame, numpy, pandas, matplotlib; print('All packages imported successfully!')"
   ```

2. **Test MATLAB setup:**
   ```matlab
   setup_experiment  % Should complete without errors
   ```

3. **Test screen selection:**
   ```matlab
   selectedScreen = select_screen();  % Should open test pattern
   ```

## Configuration

### fMRI Settings

Edit `fmri_session.m` to configure your setup:

```matlab
% Scanning Parameters 
scanning = false;   % Set to true for actual fMRI scanning
com = 'com4';       % Serial port for trigger (Windows) or '/dev/ttyUSB0' (Linux/macOS)
TR = 2.01;          % TR in seconds

% Participant Information
SubID = 'test';     % Change to actual participant ID
```

### Screen Configuration

The experiment will automatically detect available screens and let you choose the correct one. For multiple monitor setups:

- **Primary monitor**: Usually screen 0
- **Secondary monitor**: Usually screen 1
- **Projector**: Usually the highest numbered screen

## Troubleshooting

### Common Issues

#### 1. Python Not Found
**Error:** `python: command not found`

**Solution:**
- Ensure Python is installed and added to PATH
- Try `python3` instead of `python`
- On Windows, try `py` instead of `python`

#### 2. Psychtoolbox Not Found
**Error:** `Undefined function 'Screen'`

**Solution:**
```matlab
% Install Psychtoolbox
DownloadPsychtoolbox()

% Or add to path manually
addpath(genpath('/path/to/Psychtoolbox'))
```

#### 3. Screen Selection Issues
**Error:** Screen selection fails or shows wrong display

**Solution:**
- Check display settings in your OS
- Ensure the target display is enabled
- Try different screen numbers (0, 1, 2, etc.)

#### 4. Serial Port Issues
**Error:** Cannot open serial port

**Solution:**
- Check the correct COM port (Windows) or device path (Linux/macOS)
- Ensure the port is not in use by another application
- For testing, set `scanning = false`

#### 5. Missing Dependencies
**Error:** Import errors in Python

**Solution:**
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt

# Or install individually
pip install pygame numpy pandas matplotlib
```

### Platform-Specific Issues

#### Windows
- Ensure Visual C++ Redistributable is installed
- Check that Python is added to PATH during installation
- Use `py` command instead of `python` if needed

#### macOS
- You may need to install Xcode command line tools:
  ```bash
  xcode-select --install
  ```
- Use `python3` instead of `python`

#### Linux
- Install development packages:
  ```bash
  sudo apt-get install python3-dev python3-pip
  ```
- For pygame, you may need:
  ```bash
  sudo apt-get install python3-pygame
  ```

## Testing the Installation

### 1. Run Setup Script
```matlab
setup_experiment
```

This should complete without errors and show:
- ✅ Python found and working
- ✅ All required packages installed
- ✅ All directories present
- ✅ All required files present

### 2. Test Individual Components

#### Test Snake Game:
```matlab
run_snake_game('test', 'test_subject', [], [], [], 0);
```

#### Test Screen Selection:
```matlab
selectedScreen = select_screen();
```

#### Test Python Integration:
```matlab
% This should work without errors
system('python -c "import pygame; print(''Python integration working!'')"');
```

### 3. Run Full Experiment (Test Mode)
```matlab
% Set to test mode (no fMRI trigger)
scanning = false;
fmri_session
```

## Getting Help

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Run the setup script:** `setup_experiment`
3. **Check MATLAB command window for error messages**
4. **Verify all prerequisites are installed**
5. **Check the individual README files in subdirectories**

## File Structure Verification

After installation, your directory should contain:

```
fMRI-Navigation-Experiment/
├── fmri_session.m              # Main experiment script
├── setup_experiment.m          # Setup script
├── install_dependencies.py     # Python dependency installer
├── requirements.txt            # Python dependencies
├── README.md                   # Main documentation
├── INSTALLATION_GUIDE.md       # This file
├── exploration/                # Main experiment code
├── PTSOD/                      # PTSOD task
├── arenas_new_icons/           # Arena assets
├── sounds/                     # Audio files
└── Results/                    # Output directory (created automatically)
```

## Next Steps

Once installation is complete:

1. **Read the main README.md** for experiment details
2. **Run a test session** with `scanning = false`
3. **Configure for your specific setup** (screen, serial port, etc.)
4. **Run the actual experiment** with `scanning = true`

## Support

For additional help:
- Check the troubleshooting section above
- Review error messages in MATLAB command window
- Ensure all prerequisites are properly installed
- Verify file permissions and paths
