# TR Alignment for fMRI Python Scripts

This document describes the TR (Repetition Time) alignment changes made to the Python scripts to match the timing structure of the MATLAB PTSOD function.

## Overview

The Python scripts (snake.py, one_target.py, multi_arena.py) have been modified to align with TR boundaries, similar to how the MATLAB `PTSODfuncICONSheb_fMRI_Test_Trigger.m` function works.

## Key Changes

### 1. Trigger Utilities (`trigger_utils.py`)

- Added `TR` parameter to `TriggerManager` class (default: 2.01 seconds)
- Added `show_fixation_for_TRs(num_TRs, skip_key='k')` method to show fixation for specified number of TRs
- Added `wait_for_next_TR_boundary(current_time, trial_start_time)` method to wait until next TR boundary
- Both methods include 'K' key functionality to skip fixation for debugging

### 2. Snake Game (`snake.py`)

- **Trial Duration**: Changed from random 9-14 seconds to 5-7 TRs (10.05-14.07 seconds)
- **TR Alignment**: ❌ **REMOVED** - No TR alignment needed since trials are already TR-aligned
- **Initial Fixation**: 8 TRs for first trial, 4 TRs for subsequent trials
- **Final Fixation**: No thank you screen (handled by final one_target trial)
- **Trigger Integration**: Proper trigger initialization and cleanup for fMRI mode

### 3. One Target Experiment (`one_target.py`)

- **Exploration Duration**: Changed from 120 seconds to 60 TRs (120.6 seconds) for fMRI mode
- **TR Alignment**: ✅ **ADDED** - Wait for next TR boundary after trial completion (participant can end annotation early)
- **Initial Fixation**: 8 TRs for first trial, 4 TRs for subsequent trials
- **Final Fixation**: 4 TRs + thank you screen only for final trial (trial 12)
- **Trigger Integration**: Proper trigger initialization and cleanup for fMRI mode

### 4. Multi-Arena Experiment (`multi_arena.py`)

- **Exploration Duration**: Changed from 120 seconds to 60 TRs (120.6 seconds) for fMRI mode
- **TR Alignment**: Added wait for next TR boundary after trial completion
- **Initial Fixation**: 8 TRs for first trial, 4 TRs for subsequent trials
- **Final Fixation**: 4 TRs + thank you screen only for final trial (trial 12)
- **Trigger Integration**: Proper trigger initialization and cleanup for fMRI mode

### 5. Wrapper Scripts

- Updated `snake_in.py`, `one_target_in.py`, `multi_arena_in.py` to pass TR=2.01 seconds
- Maintained backward compatibility with existing MATLAB wrapper functions

## TR Alignment Process

**Important Logic Update**: TR alignment is only needed when participants can end trials early.

1. **Snake Trials**: ❌ No TR alignment needed - duration is exact multiple of TRs (5-7 TRs)
2. **One Target Trials**: ✅ TR alignment needed - participants can end **feedback phase** early (corrected)
3. **Multi-Arena Trials**: ✅ TR alignment needed - participants can end exploration early
4. **Timing Reference**: Uses trigger time (not trial start time) to avoid fixation timing mismatch
5. **Skip Functionality**: 'K' key can skip fixation periods for debugging

## Key Fixes Applied

### Issue #1: Snake TR Alignment Logic Error
**Problem**: Snake trials showed fixation despite being TR-aligned due to timing reference mismatch.
**Root Cause**: TR calculation used `trial_start_time` but fixation occurred before trial start.
**Solution**: Removed unnecessary TR alignment logic from snake.py entirely.

### Issue #2: One Target TR Alignment Location Error  
**Problem**: TR alignment occurred after annotation phase instead of feedback phase.
**Root Cause**: Participants can end annotation phase early, but trial continues to feedback phase.
**Solution**: Moved TR alignment to after feedback phase when `trial_done = True`.

## Timing Structure

### Snake Game
- **Practice Mode**: 60 seconds (unchanged)
- **fMRI Mode**: 5-7 TRs (10.05-14.07 seconds) + variable fixation (8 TRs for trial 1, 4 TRs for trials 2+)

### One Target Experiment
- **Practice Mode**: 120 seconds (unchanged)
- **fMRI Mode**: 60 TRs (120.6 seconds) + variable fixation (8 TRs for trial 1, 4 TRs for trials 2+, final 4 TRs + thank you for trial 12)

### Multi-Arena Experiment
- **Practice Mode**: 120 seconds (unchanged)
- **fMRI Mode**: 60 TRs (120.6 seconds) + variable fixation (8 TRs for trial 1, 4 TRs for trials 2+, final 4 TRs + thank you for trial 12)

## Usage

The scripts work exactly as before, but now include TR alignment when `--scanning` flag is used:

```bash
# fMRI mode with TR alignment
python snake.py fmri --participant TS263 --run 1 --trial 1 --total-trials 4 --scanning --tr 2.01

# Practice mode (no TR alignment)
python snake.py practice --participant TS263
```

## MATLAB Integration

The MATLAB wrapper functions (`run_snake_game.m`, `run_one_target.m`, `run_multi_arena.m`) work unchanged - they automatically pass the scanning parameter which enables TR alignment.

## Debugging

- Press 'K' to skip fixation periods during fMRI sessions
- Press 'ESC' to exit at any time
- TR alignment only occurs when `--scanning` flag is used

## Compatibility

- All existing functionality is preserved
- Practice mode timing unchanged
- fMRI mode now includes TR alignment
- Backward compatible with existing MATLAB scripts 