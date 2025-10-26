# fMRI Session Dependencies

This folder contains all dependencies required to run `fmri_session.m`.

## Directory Structure

- **Root MATLAB Scripts**: `select_screen.m`, `fmri_session.m`
- **exploration/**: Navigation experiment scripts (MATLAB + Python)
  - MATLAB wrappers: `run_snake_game.m`, `one_target_run.m`, `full_arena_run.m`, `trigger_manager.m`
  - Python scripts: `snake.py`, `one_target.py`, `multi_arena.py`, and wrapper scripts
  - `arena_configs/`: 12 arena configuration JSON files
  - `sounds/`: Sound effects and Hebrew audio for all 12 arenas (~65 files)
  - `Instructions-he/`: Navigation instruction images (12 files)
- **PTSOD/**: PTSOD (Perspective Taking and Spatial Orientation Distance) experiment
  - `Code/`: 6 MATLAB scripts for PTSOD experiment
  - `Stimuli/`: Memory and no-memory screen images, object icons (~200+ files)
  - `Instructions_HE/`: PTSOD instruction images (11 files)
- **arenas_new_icons/**: 17 themed icon sets (~3,400 files)
- **sounds/**: Root-level sound files

## Required Software

### MATLAB
- **MATLAB** (R2019b or later recommended)
- **Psychtoolbox-3** (http://psychtoolbox.org/)
- **Instrument Control Toolbox** (for fMRI trigger via serial port)

### Python
- **Python 3.8+**
- Install dependencies: `pip install -r exploration/requirements.txt`

Required Python packages:
- pygame==2.5.2
- pandas>=1.3.0
- matplotlib>=3.4.0
- seaborn>=0.11.0
- pyserial>=3.5
- edge-tts>=6.1.9
- librosa>=0.10.0
- soundfile>=0.12.0
- numpy>=1.21.0

## Hardware Requirements

- **Serial Port**: COM4 (9600 baud) for fMRI trigger (when scanning mode enabled)
- **Multiple Displays**: For screen selection functionality
- **Audio Output**: For sound playback

## Usage

1. Copy this entire `FMRI_dep` folder to your target computer
2. Install MATLAB with Psychtoolbox-3
3. Install Python 3.8+ and required packages
4. Add the folder to MATLAB path or `cd` into it
5. Run `fmri_session.m`

## File Statistics

- Total MATLAB scripts: 22
- Total Python scripts: 11
- Arena configurations: 12 JSON files
- Sound files: ~67 files
- Image files: ~3,600+ files
- Total files: ~3,700+

## Environment Variables

The scripts automatically set:
- `CENTRALIZED_RESULTS_DIR`: Points to Results directory for data storage
- `TRIGGER_RECEIVED_TIME`: For trigger timing communication

## Notes

- Results are saved to `Results/<SubID>/` directory (created automatically)
- All paths are portable and use `pwd` for current directory reference
- Python scripts are called via system commands from MATLAB
- Supports both scanning mode (with triggers) and testing mode (without triggers)

## Generated

This dependency package was automatically generated.
Date: 1761476997.132903

For questions, refer to the original project documentation.
