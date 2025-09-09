# fMRI Navigation Experiment

A comprehensive fMRI experiment system for studying egocentric and allocentric navigation using snake games and arena-based tasks.

## Overview

This experiment consists of multiple components:
- **Anatomical Scan**: Endless snake game during anatomical scanning
- **PTSOD Tasks**: Two runs of the PTSOD (Pointing to Self-Other Direction) task
- **One Target Run**: 6 snake trials + 6 one-target arena trials
- **Full Arena Run**: 6 snake trials + 6 multi-arena trials

## Quick Start

### Prerequisites

1. **MATLAB R2018b+** (with Psychtoolbox)
2. **Python 3.8+** with required packages
3. **Serial port connection** (for fMRI trigger functionality - handled by MATLAB)

### Installation

#### Option 1: Automated Setup (Recommended)

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

#### Option 2: Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/fMRI-Navigation-Experiment.git
   cd fMRI-Navigation-Experiment
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install MATLAB dependencies:**
   - Ensure Psychtoolbox is installed: `DownloadPsychtoolbox()` in MATLAB
   - Add all required paths (handled automatically by `fmri_session.m`)

**For detailed installation instructions, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**

### Running the Experiment

1. **Start MATLAB and navigate to the project directory**

2. **Run the main experiment:**
   ```matlab
   fmri_session
   ```

3. **Follow the on-screen prompts:**
   - Select your display screen
   - The experiment will run automatically through all phases

## File Structure

```
fMRI/
├── fmri_session.m              # Main experiment script
├── select_screen.m             # Screen selection utility
├── combine_session_data.m      # Data combination function
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
│
├── exploration/               # Main experiment code
│   ├── run_snake_game.m       # Snake game wrapper
│   ├── one_target_run.m       # One target experiment
│   ├── full_arena_run.m       # Full arena experiment
│   ├── trigger_manager.m      # Trigger management
│   ├── snake.py              # Snake game implementation
│   ├── one_target.py         # One target task
│   ├── multi_arena.py        # Multi-arena task
│   ├── sounds/               # Audio files
│   ├── Instructions-he/      # Hebrew instruction images
│   └── arena_visualizations/ # Arena images
│
├── PTSOD/                    # PTSOD task
│   ├── Code/                 # PTSOD MATLAB functions
│   ├── Instructions_HE/      # Hebrew instructions
│   └── Stimuli/             # Task stimuli
│
├── arenas_new_icons/         # Arena icon assets
├── sounds/                   # Global sound files
└── Results/                  # Output directory (created automatically)
```

## Configuration

### fMRI Settings

Edit `fmri_session.m` to configure:

```matlab
% Scanning Parameters 
scanning = false;   % Set to true for actual fMRI
com = 'com4';       % Serial port for trigger
TR = 2.01;          % TR in seconds
```

### Participant Information

```matlab
SubID = 'test';     % Change to actual participant ID
```

## Experiment Phases

### 1. Anatomical Scan Snake Practice
- Endless snake game during anatomical scanning
- Press ESC to exit when scan is complete

### 2. PTSOD fMRI Run 1
- 8-trial PTSOD task
- Uses Hebrew instructions and stimuli

### 3. One Target Run Design
- 6 snake trials + 6 one-target arena trials
- Intertwined design to eliminate timing gaps

### 4. Full Arena Run Design  
- 6 snake trials + 6 multi-arena trials
- Uses 6 different fMRI arenas

### 5. PTSOD fMRI Run 2
- Second 8-trial PTSOD task

### 6. Final Instructions
- Completion screen with black background

## Data Output

All data is saved in the `Results/` directory with the following structure:

```
Results/
└── [SubID]/
    ├── [SubID]_anatomical_snake_continuous.csv
    ├── [SubID]_anatomical_snake_discrete.csv
    ├── [SubID]_OT_ot_continuous.csv
    ├── [SubID]_OT_ot_discrete.csv
    ├── [SubID]_OT_snake_continuous.csv
    ├── [SubID]_OT_snake_discrete.csv
    ├── [SubID]_FA_fa_continuous.csv
    ├── [SubID]_FA_fa_discrete.csv
    ├── [SubID]_FA_snake_continuous.csv
    └── [SubID]_FA_snake_discrete.csv
```

Where:
- `OT` = One Target Run
- `FA` = Full Arena Run
- `ot` = One Target trials
- `fa` = Full Arena trials
- `snake` = Snake game trials

### Data Combination

The `combine_session_data()` function automatically combines individual trial files into single files per run type. This is called automatically at the end of `fmri_session.m`.

## Arena Assignments

### Practice Arenas (used in practice sessions)
- garden, beach, village, ranch, zoo, school

### fMRI Arenas (used in actual fMRI runs)
- hospital, bookstore, gym, museum, airport, market

## Troubleshooting

### Common Issues

1. **Screen Selection Problems**
   - The `select_screen()` function will display test patterns
   - Choose the correct screen for your setup

2. **Serial Port Issues**
   - Check that `com` variable matches your system
   - For testing, set `scanning = false`

3. **Python Dependencies**
   - Run `pip install -r requirements.txt`
   - Ensure Python 3.8+ is installed

4. **MATLAB Path Issues**
   - All paths are added automatically by `fmri_session.m`
   - Check that all directories exist

### Testing Mode

For testing without fMRI scanner:
```matlab
scanning = false;  % Disables trigger functionality
```

## Development

### Adding New Arenas

1. Add arena images to `arenas_new_icons/`
2. Update arena lists in `fmri_session.m`
3. Add corresponding sounds to `exploration/sounds/arenas/`

### Modifying Tasks

- Snake game: Edit `exploration/snake.py`
- One target: Edit `exploration/one_target.py`  
- Multi-arena: Edit `exploration/multi_arena.py`

## Requirements

### MATLAB
- MATLAB R2018b or later
- Psychtoolbox
- Statistics and Machine Learning Toolbox (for data processing)

### Python
- Python 3.8 or later
- pygame >= 2.5.0
- numpy >= 1.21.0
- pandas >= 1.3.0
- matplotlib >= 3.5.0

### Hardware
- Serial port connection (for fMRI triggers - handled by MATLAB)
- Multiple displays (recommended)
- Audio output capability

## License

[Add your license information here]

## Citation

[Add citation information here]

## Support

For technical support or questions about the experiment:
1. Check the troubleshooting section above
2. Review the individual README files in subdirectories
3. [Add contact information]

## Version History

- v1.0: Initial release with complete fMRI experiment pipeline
