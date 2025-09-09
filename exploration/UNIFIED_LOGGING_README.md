# Unified Logging System for fMRI Navigation Experiments

## Overview

This document describes the unified logging system that standardizes data saving across all experiment types (one_target, multi_arena, snake) to eliminate the need for post-processing file combination.

## Problem Solved

**Before:** Multi-arena practice created separate files for each arena/condition that needed to be combined using `combine_logs.py` after all practice sessions.

**After:** All experiments now use a unified approach that creates single consolidated files from the start.

## File Organization

### Practice Mode (Unified Approach)
All experiments now follow the same pattern:

```
Results/
└── SubID/
    ├── SubID_one_target_practice_continuous_log.csv
    ├── SubID_one_target_practice_discrete_log.csv
    ├── SubID_multi_arena_practice_continuous_log.csv
    ├── SubID_multi_arena_practice_discrete_log.csv
    ├── SubID_snake_practice_continuous_log.csv
    └── SubID_snake_practice_discrete_log.csv
```

### fMRI Mode (Trial-Specific)
For fMRI runs, files remain trial-specific as needed:

```
Results/
└── SubID/
    ├── SubID_one_target_run_continuous.csv
    ├── SubID_one_target_run_discrete.csv
    ├── SubID_multi_arena_trial1_continuous.csv
    ├── SubID_multi_arena_trial1_discrete.csv
    ├── SubID_snake_run1_continuous.csv
    └── SubID_snake_run1_discrete.csv
```

## Key Changes

### 1. Multi-Arena Practice (`multi_arena.py`)
- **Removed:** Arena-specific suffixes (`_1`, `_2`, `_3`)
- **Removed:** Environment variable `ARENA_LOG_SUFFIX`
- **Added:** Unified file naming for practice mode
- **Added:** Automatic file cleanup for practice mode

### 2. Practice Sessions (`practice_sessions.m`)
- **Removed:** Call to `combine_logs.py` script
- **Simplified:** No post-processing required

### 3. Unified Logging Module (`unified_logging.py`)
- **New:** Centralized logging class for consistent behavior
- **Features:** Automatic file management, error handling, backup creation
- **Benefits:** Consistent API across all experiment types

## Benefits

1. **Simplified Workflow:** No need for post-processing file combination
2. **Consistent Behavior:** All experiments follow the same logging pattern
3. **Reduced Complexity:** Eliminates the need for `combine_logs.py`
4. **Better Error Handling:** Centralized error handling and backup creation
5. **Easier Maintenance:** Single logging system to maintain

## Usage

### For Existing Experiments
The changes are backward-compatible. Existing experiments will continue to work with the new unified approach.

### For New Experiments
Use the `UnifiedLogger` class for consistent behavior:

```python
from unified_logging import UnifiedLogger

# Initialize logger
logger = UnifiedLogger(participant_id='test', experiment_type='multi_arena', mode='practice')

# Save data
logger.save_discrete_log(discrete_logs)
logger.save_continuous_log(continuous_logs)

# Real-time logging
logger.append_continuous_log(log_entry)
```

## Migration Notes

- The `combine_logs.py` script is no longer needed for practice sessions
- All practice data is now saved to single consolidated files
- fMRI mode behavior remains unchanged
- Existing data files are not affected by these changes

## File Naming Convention

Following the user's preference for log file names without run numbers or timestamps:

- `SubID_one_target_practice_continuous_log.csv`
- `SubID_one_target_practice_discrete_log.csv`
- `SubID_multi_arena_practice_continuous_log.csv`
- `SubID_multi_arena_practice_discrete_log.csv`
- `SubID_snake_practice_continuous_log.csv`
- `SubID_snake_practice_discrete_log.csv`

