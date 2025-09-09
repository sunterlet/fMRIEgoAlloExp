# Trigger Handling Modification Summary

## Overview
Modified the fMRI experiment system to handle triggers at the MATLAB level instead of within the Python experiments. This provides better control over block design timing and simplifies the Python experiments.

## Changes Made

### 1. MATLAB Level Changes

#### New Files Created:
- `exploration/trigger_manager.m` - MATLAB trigger management function

#### Modified Files:
- `fmri_sessions.m` - Added trigger initialization, waiting, and closing for each block design
- `exploration/run_snake_game.m` - Removed scanning parameter
- `exploration/run_one_target.m` - Removed scanning parameter  
- `exploration/run_multi_arena.m` - Removed scanning parameter

### 2. Python Level Changes

#### Modified Files:
- `exploration/snake.py` - Removed trigger handling code
- `exploration/one_target.py` - Removed trigger handling code
- `exploration/multi_arena.py` - Removed trigger handling code
- `exploration/snake_in.py` - Removed scanning parameter
- `exploration/one_target_in.py` - Removed scanning parameter

### 3. Key Changes

#### Trigger Management:
- **Before**: Each Python experiment handled its own trigger initialization, waiting, and closing
- **After**: MATLAB manages triggers at the block design level

#### Block Design Flow:
1. MATLAB initializes trigger before each block (One Target or Full Arena)
2. MATLAB waits for trigger to start the block
3. Python experiments run without trigger handling
4. MATLAB closes trigger after block completion

#### Function Signatures:
- **Before**: `run_snake_game('fmri', SubID, i, trial_counter, total_trials, scanning)`
- **After**: `run_snake_game('fmri', SubID, i, trial_counter, total_trials)`

### 4. Benefits

1. **Centralized Control**: All trigger handling is managed at the MATLAB level
2. **Simplified Python Code**: Python experiments focus on gameplay, not trigger management
3. **Better Block Design**: Triggers are synchronized with block boundaries, not individual trials
4. **Easier Debugging**: Trigger issues can be isolated to MATLAB code
5. **Consistent Timing**: All experiments use the same TR (2.01 seconds)

### 5. Usage

#### Running fMRI Sessions:
```matlab
% In fmri_sessions.m
scanning = true;  % Enable trigger functionality
com = 'com4';    % Serial port
TR = 2.01;       % TR in seconds

% Triggers are automatically handled for each block design
```

#### Python Experiments:
- No longer need `--scanning`, `--com`, or `--tr` parameters
- Run normally without trigger handling
- Focus on gameplay and data collection

### 6. File Structure

```
fMRI/
├── fmri_sessions.m                    # Main fMRI session runner
├── exploration/
│   ├── trigger_manager.m              # NEW: MATLAB trigger handler
│   ├── run_snake_game.m              # Modified: No scanning parameter
│   ├── run_one_target.m              # Modified: No scanning parameter
│   ├── run_multi_arena.m             # Modified: No scanning parameter
│   ├── snake.py                      # Modified: No trigger handling
│   ├── one_target.py                 # Modified: No trigger handling
│   ├── multi_arena.py                # Modified: No trigger handling
│   ├── snake_in.py                   # Modified: No scanning parameter
│   └── one_target_in.py              # Modified: No scanning parameter
```

## Testing

To test the modified system:

1. **Practice Mode**: Run experiments outside magnet (no triggers)
2. **fMRI Mode**: Run with `scanning = true` to enable trigger handling
3. **Block Design**: Verify triggers work at block boundaries, not individual trials

## Notes

- All Python experiments now use fixed TR = 2.01 seconds
- Trigger handling is completely removed from Python code
- MATLAB manages all trigger initialization, waiting, and cleanup
- Block designs are properly synchronized with triggers
- **NEW**: Improved trigger detection using pin status (like PTSOD function)
- **NEW**: Added 4 TR dummy scan after trigger reception
- **NEW**: Added error handling for trigger operations
- **NEW**: Added Psychtoolbox initialization and screen setup
- **NEW**: **MANDATORY TRIGGER**: Experiment will NOT continue without receiving a trigger
- **NEW**: **TIMING UPDATES**: Instructions shown for 1 TR, fixation for 4 TRs after each trial
- **NEW**: **TR ALIGNMENT**: Trial endings are now aligned to TR boundaries with proper waiting
- **FIXED**: **MODE VARIABLE ERROR**: Fixed NameError in one_target.py where MODE was accessed before definition
- **NEW**: **TESTING MODE**: Added ability to test fMRI sessions outside scanner with `scanning = false` (keeps all fMRI functionality except trigger handling)
- **OPTIMIZED**: **TIMING**: Moved dummy scan from MATLAB to Python for seamless timing between trigger reception and experiment start
- **CLEANED UP**: **REMOVED PSYCHTOOLBOX**: Removed unnecessary Psychtoolbox initialization from MATLAB since all display is now handled in Python
- **STANDARDIZED**: **FIXATION CROSS**: Unified fixation cross format across all Python scripts (drawn lines instead of text characters)
- **CORRECTED**: **FIXATION FLOW**: Simplified to 4 TRs fixation at start of each trial, TR alignment (fixation until end of current TR) at end of each trial 