# Exploration Experiment

This folder contains an exploration version of the experiment that can be run on any computer.

## Requirements

- Python 3.7 or higher
- pygame library

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Experiments

### Main Experiment (`one_target.py`)

This is the main exploration experiment with MRI-compatible controls:

```bash
python one_target.py
```

**Features:**
- Full experiment with training, dark training, and test trials
- MRI-compatible number key controls (1-4)
- Automatic data logging
- Debug mode available

**Controls:**
- **Number Keys**: 
  - `1`: Rotate left
  - `2`: Move forward
  - `3`: Move backward  
  - `4`: Rotate right
  - `6`: Confirm decisions and proceed through phases
- **Arrow Keys**: Alternative controls (UP/DOWN for movement, LEFT/RIGHT for rotation)
- **Escape**: Exit the experiment
- **K**: Show debug information (when in debug mode)

### Practice Game (`snake.py`)

A simple practice game to familiarize with the controls:

```bash
python snake.py
```

**Features:**
- Simple target collection game
- Score-based gameplay (reach score of 5 to complete)
- Same visual style as main experiment
- Good for learning the controls

**Controls:**
- **Arrow Keys**: 
  - `UP/DOWN`: Move forward/backward
  - `LEFT/RIGHT`: Rotate
- **Number Key `6`**: Exit the practice game
- **Escape**: Exit the game

## Output

The main experiment (`one_target.py`) will create log files in the `results/` folder:
- `{initials}_discrete_log.csv`: Summary data for each trial
- `{initials}_continuous_log.csv`: Detailed movement and event data

## File Structure

```
exploration/
├── one_target.py                    # Main experiment script
├── snake.py                         # Practice game
├── practice_game_v2.py              # Alternative practice game
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── Instructions/                   # Instruction images
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   ├── 4.png
│   ├── 5.png
│   └── 6.png
├── sounds/                         # Audio files
│   ├── target.wav
│   └── beep.wav
└── results/                        # Output directory (created automatically)
```

## Experiment Flow

### Main Experiment (`one_target.py`)
1. **Welcome** - Introduction screen
2. **Training Block** - 3 training trials with full visibility
3. **Dark Training Block** - 3 trials with limited visibility
4. **Test Block** - 5 test trials with limited visibility
5. **Completion** - Final instructions

### Practice Game (`snake.py`)
- Simple target collection in the same arena
- Reach a score of 5 to complete
- No data logging

## Notes

- The experiment runs in fullscreen mode
- All file paths are relative, so the folder can be moved to any location
- Debug mode is enabled when participant initials are '111'
- MRI-compatible controls use number keys 1-4 for movement and 6 for confirmation
- Arrow keys are available as alternative controls 