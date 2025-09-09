# Exploration Experiment Suite - Practice and fMRI Modes

This document describes how to use the modified `one_target.py`, `snake.py`, and `multi_arena.py` scripts and their wrapper scripts for running experiments both outside the magnet (practice) and inside the magnet (fMRI).

## Overview

The experiments have been modified to support two modes:
1. **Practice Mode** (`practice`): Full sequence outside the magnet
2. **fMRI Mode** (`fmri`): Single trial inside the magnet for block design

### Available Experiments:
- **One Target Experiment**: Navigation and memory task
- **Snake Game**: Motor control and target acquisition task
- **Multi-Arena Experiment**: Spatial memory and annotation task

## Files

### One Target Experiment
- `one_target.py` - Main experiment script (modified to support both modes)
- `one_target_out.py` - Wrapper for practice mode
- `one_target_in.py` - Wrapper for fMRI mode  
- `run_one_target.m` - MATLAB function to call the scripts

### Snake Game
- `snake.py` - Main game script (modified to support both modes)
- `snake_out.py` - Wrapper for practice mode
- `snake_in.py` - Wrapper for fMRI mode  
- `run_snake_game.m` - MATLAB function to call the scripts

### Multi-Arena Experiment
- `multi_arena.py` - Main experiment script (modified to support both modes)
- `multi_arena_out.py` - Wrapper for practice mode
- `multi_arena_in.py` - Wrapper for fMRI mode  
- `run_multi_arena.m` - MATLAB function to call the scripts

### Block Design Sequences
- `full_sequence_exploration.m` - One Target + Snake block design
- `full_sequence_snake_multi_arena.m` - Snake + Multi-Arena block design

### Setup and Documentation
- `setup.py` - Setup script to check dependencies and environment
- `requirements.txt` - Python package requirements
- `README_one_target.md` - This documentation

## Usage

### One Target Experiment

#### Direct Python Usage
```bash
# Practice Mode (Outside Magnet)
python one_target.py practice --participant TS263

# fMRI Mode (Inside Magnet)
python one_target.py fmri --participant TS263 --run 1
```

#### Using Wrapper Scripts
```bash
# Practice Mode
python one_target_out.py TS263

# fMRI Mode
python one_target_in.py TS263 1
```

#### Using MATLAB Function
```matlab
% Practice Mode
run_one_target('practice', 'TS263')

% fMRI Mode (with trial counter)
run_one_target('fmri', 'TS263', 1, 1, 4)  % Trial 1 of 4
run_one_target('fmri', 'TS263', 2, 3, 4)  % Trial 3 of 4
```

### Snake Game

#### Direct Python Usage
```bash
# Practice Mode (Outside Magnet)
python snake.py practice --participant TS263

# fMRI Mode (Inside Magnet)
python snake.py fmri --participant TS263 --run 1
```

#### Using Wrapper Scripts
```bash
# Practice Mode
python snake_out.py TS263

# fMRI Mode
python snake_in.py TS263 1
```

#### Using MATLAB Function
```matlab
% Practice Mode
run_snake_game('practice', 'TS263')

% fMRI Mode (with trial counter)
run_snake_game('fmri', 'TS263', 1, 2, 4)  % Trial 2 of 4
run_snake_game('fmri', 'TS263', 2, 4, 4)  % Trial 4 of 4
```

### Multi-Arena Experiment

#### Direct Python Usage
```bash
# Practice Mode (Outside Magnet)
python multi_arena.py practice --participant TS263 --arena arena1

# fMRI Mode (Inside Magnet)
python multi_arena.py fmri --participant TS263 --run 1 --arena arena1
```

#### Using Wrapper Scripts
```bash
# Practice Mode
python multi_arena_out.py TS263 arena1

# fMRI Mode
python multi_arena_in.py TS263 1 3 4 arena1
```

#### Using MATLAB Function
```matlab
% Practice Mode
run_multi_arena('practice', 'TS263', 1, 1, 1, 'arena1')

% fMRI Mode (with trial counter)
run_multi_arena('fmri', 'TS263', 1, 3, 4, 'arena1')  % Trial 3 of 4
run_multi_arena('fmri', 'TS263', 2, 5, 6, 'arena2')  % Trial 5 of 6
```

## Trial Structure

### One Target Experiment

#### Practice Mode
- **Training trials**: 3 trials with full visibility
- **Dark training trials**: 2 trials with limited visibility
- **Test trials**: 3 trials with limited visibility
- **Instructions**: Uses images 3.png, 4.png, 5.png from Instructions-he/
- **End instruction**: Shows image 10.png at completion
- **Key controls**: 1/4 (rotation), 2/3 (forward/backward), 6 (enter)

#### fMRI Mode
- **Test trial**: 1 trial with limited visibility
- **Instructions**: Uses image 6.png for 6 seconds
- **Fixation**: 6-second fixation cross before and after trial
- **Progress indicator**: Shows current trial number in sequence (e.g., "1/4")
- **Block design**: Designed to run as part of a larger fMRI sequence
- **Key controls**: 1/4 (rotation), 2/3 (forward/backward), 6 (enter)

### Snake Game

#### Practice Mode
- **Target score**: 7 points
- **Instructions**: Uses image 1.png (wait for key press)
- **Gameplay**: Standard snake game with full visibility
- **End instruction**: Shows image 10.png at completion
- **Key controls**: 1/4 (rotation), 2/3 (forward/backward), 6 (enter)

#### fMRI Mode
- **Target score**: 3 points
- **Instructions**: Uses image 2.png for 6 seconds
- **Fixation**: 6-second fixation cross before and after game
- **Progress indicator**: Shows current trial number in sequence (e.g., "2/4")
- **Block design**: Designed to run as part of a larger fMRI sequence
- **Key controls**: 1/4 (rotation), 2/3 (forward/backward), 6 (enter)

### Multi-Arena Experiment

#### Practice Mode
- **Training trial**: 1 trial with full visibility
- **Dark training trials**: 2 trials with limited visibility
- **Test trials**: 3 trials with limited visibility
- **Instructions**: Uses image 7.png (wait for key press)
- **End instruction**: Shows image 10.png at completion
- **Key controls**: 1/4 (rotation), 2/3 (forward/backward), 6 (enter)

#### fMRI Mode
- **Test trial**: 1 trial with limited visibility
- **Instructions**: Uses image 8.png for 6 seconds
- **Fixation**: 6-second fixation cross before and after experiment
- **Progress indicator**: Shows current trial number in sequence (e.g., "3/6")
- **Block design**: Designed to run as part of a larger fMRI sequence
- **Key controls**: 1/4 (rotation), 2/3 (forward/backward), 6 (enter)

## Output Files

### One Target Experiment

#### Practice Mode
- `{participant}_practice_discrete_log.csv`
- `{participant}_practice_continuous_log.csv`

#### fMRI Mode
- `{participant}_run{number}_discrete_log.csv`
- `{participant}_run{number}_continuous_log.csv`

### Snake Game
- No output files (game only tracks score internally)

### Multi-Arena Experiment

#### Practice Mode
- `{participant}_multi_arena_practice_continuous_log.csv`
- `{participant}_multi_arena_practice_discrete_log.csv`

#### fMRI Mode
- `{participant}_multi_arena_run{number}_continuous_log.csv`
- `{participant}_multi_arena_run{number}_discrete_log.csv`

## Integration with Block Design Sequences

### full_sequence_exploration.m (One Target + Snake)

Add the following to your MATLAB sequence:

```matlab
% Practice sessions (outside magnet)
run_snake_game('practice', SubID);
run_one_target('practice', SubID);

% fMRI runs (inside magnet) - integrate with block design
total_trials = 4;  % Total number of trials in sequence
trial_counter = 1;

% Run one target experiment (trial 1)
run_one_target('fmri', SubID, 1, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Run snake game (trial 2)
run_snake_game('fmri', SubID, 1, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Run one target experiment (trial 3)
run_one_target('fmri', SubID, 2, trial_counter, total_trials);
trial_counter = trial_counter + 1;
```

### full_sequence_snake_multi_arena.m (Snake + Multi-Arena)

This sequence runs a 6-block design alternating between snake and multi-arena tasks:

```matlab
% Practice sessions (outside magnet)
run_snake_game('practice', SubID);
run_multi_arena('practice', SubID, 1, 1, 1, 'arena1');

% fMRI runs (inside magnet) - 6 blocks total
total_trials = 6;
trial_counter = 1;

% Block 1: Snake
run_snake_game('fmri', SubID, 1, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Block 2: Multi-Arena
run_multi_arena('fmri', SubID, 1, trial_counter, total_trials, 'arena1');
trial_counter = trial_counter + 1;

% Block 3: Snake
run_snake_game('fmri', SubID, 2, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Block 4: Multi-Arena
run_multi_arena('fmri', SubID, 2, trial_counter, total_trials, 'arena2');
trial_counter = trial_counter + 1;

% Block 5: Snake
run_snake_game('fmri', SubID, 3, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Block 6: Multi-Arena
run_multi_arena('fmri', SubID, 3, trial_counter, total_trials, 'arena3');

% Run snake game (trial 4)
run_snake_game('fmri', SubID, 2, trial_counter, total_trials);
```

## Command Line Arguments

### one_target.py
- `mode`: Required. Either 'practice' or 'fmri'
- `--participant, -p`: Participant ID (default: 'TEST')
- `--run, -r`: Run number for fMRI mode (default: 1)
- `--trial, -t`: Current trial number in sequence (default: 1)
- `--total-trials, -tt`: Total number of trials in sequence (default: 1)

### one_target_out.py
- `participant_id`: Participant ID (default: 'TEST')

### one_target_in.py
- `participant_id`: Participant ID (default: 'TEST')
- `run_number`: Run number (default: 1)
- `trial_number`: Current trial number in sequence (default: 1)
- `total_trials`: Total number of trials in sequence (default: 1)

### snake.py
- `mode`: Required. Either 'practice' or 'fmri'
- `--participant, -p`: Participant ID (default: 'TEST')
- `--run, -r`: Run number for fMRI mode (default: 1)
- `--trial, -t`: Current trial number in sequence (default: 1)
- `--total-trials, -tt`: Total number of trials in sequence (default: 1)

### snake_out.py
- `participant_id`: Participant ID (default: 'TEST')

### snake_in.py
- `participant_id`: Participant ID (default: 'TEST')
- `run_number`: Run number (default: 1)
- `trial_number`: Current trial number in sequence (default: 1)
- `total_trials`: Total number of trials in sequence (default: 1)

## Portability

The experiment is designed to be fully portable and explorable:

### Quick Setup
```bash
# Run setup script to check environment
python setup.py

# Install dependencies if needed
pip install pygame
```

### Requirements
- Python 3.7 or higher
- pygame package
- All files in the exploration directory

### Cross-Platform Compatibility
- Works on Windows, Mac, and Linux
- Uses relative paths for all files
- No external dependencies or internet connections required
- Automatic directory creation and error handling

## Notes

- The experiment uses Hebrew instructions from the `Instructions-he/` directory
- fMRI mode includes automatic fixation crosses (6 seconds each)
- All modes support the same control scheme (number keys 1-4 for movement, 6 for progression)
- Debug mode is available when participant ID is '111'
- Results are automatically saved after each trial/run
- All scripts are self-contained and portable 