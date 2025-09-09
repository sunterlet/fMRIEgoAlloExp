# Trigger Functionality for fMRI Experiments

This document describes the trigger functionality that has been added to the Python scripts for fMRI experiments.

## Overview

The trigger functionality allows the Python scripts to synchronize with fMRI scanner triggers, ensuring precise timing for experimental stimuli presentation.

## Files Added/Modified

### New Files
- `trigger_utils.py` - Python equivalent of MATLAB trigger functions
- `test_trigger.py` - Test script for trigger functionality
- `README_TRIGGER.md` - This documentation file

### Modified Files
- `snake.py` - Added trigger functionality
- `one_target.py` - Added trigger functionality  
- `multi_arena.py` - Added trigger functionality
- `snake_in.py` - Updated to use trigger functionality
- `one_target_in.py` - Updated to use trigger functionality
- `multi_arena_in.py` - Updated to use trigger functionality
- `requirements.txt` - Added pyserial dependency
- `fmri_sessions.m` - Updated to use trigger functionality

## Trigger Functionality

### TriggerManager Class

The `TriggerManager` class provides the following methods:

- `__init__(scanning, com, baud_rate)` - Initialize trigger manager
- `init_trigger()` - Initialize serial connection for trigger
- `wait_for_trigger()` - Wait for scanner trigger signal
- `close_trigger()` - Close trigger connection

### Command Line Arguments

The Python scripts now accept the following additional arguments:

- `--scanning` - Enable trigger functionality for fMRI scanning
- `--com` - Serial port for trigger (if empty or not specified, defaults to com4)
- `--tr` - TR in seconds (default: 2.0)

### Example Usage

```bash
# Run snake game with trigger functionality
python snake.py fmri --participant TS263 --run 1 --trial 1 --total-trials 4 --scanning --com com4 --tr 2.0

# Run one target experiment with trigger functionality
python one_target.py fmri --participant TS263 --run 1 --trial 1 --total-trials 4 --scanning --com com4 --tr 2.0

# Run multi-arena experiment with trigger functionality
python multi_arena.py fmri --participant TS263 --run 1 --trial 1 --total-trials 4 --arena hospital --scanning --com com4 --tr 2.0
```

## Integration with MATLAB

The MATLAB wrapper functions (`run_snake_game.m`, `run_one_target.m`, `run_multi_arena.m`) now call the Python scripts with trigger functionality enabled.

### fMRI Sessions

The `fmri_sessions.m` file has been updated to use trigger functionality:

```matlab
% fMRI session parameters with trigger functionality
scanning = true;   % Enable trigger functionality
com = 'com4';      % Serial port for trigger
TR = 2;           % TR in seconds

% Run fMRI session with trigger
[dataTable, filename] = PTSODfunc_SplitDays_fMRI_New(SubID, day, 'fMRI', selectedScreen, scanning, com, TR);
```

## Testing

Use the test script to verify trigger functionality:

```bash
python test_trigger.py
```

This will test both scanning disabled and enabled modes.

## Dependencies

The trigger functionality requires the `pyserial` library:

```bash
pip install pyserial>=3.5
```

## Error Handling

The trigger functionality includes comprehensive error handling:

- If trigger initialization fails, the experiment exits with error
- If trigger wait fails, the experiment exits with error
- All errors are logged with appropriate messages
- When scanning is enabled, trigger reception is mandatory

## Configuration

### Serial Port

The default serial port is `com4` when the `--com` parameter is empty or not specified. This can be changed by explicitly providing the `--com` parameter.

### Baud Rate

The default baud rate is 9600. This can be modified in the `TriggerManager` class.

### Timeout

The trigger wait has a 30-second timeout to prevent infinite waiting.

## Notes

- The trigger functionality is only active when `--scanning` is specified
- In practice mode, trigger functionality is disabled
- The trigger functionality is compatible with the existing MATLAB trigger functions
- When scanning is enabled, trigger reception is mandatory - experiments will exit if trigger is not received
- All experiments can run without trigger functionality for testing purposes (when scanning is disabled) 