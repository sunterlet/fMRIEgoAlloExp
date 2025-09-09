# PTSOD fMRI Experiment - New System (PORTABLE VERSION)

This document describes the new PTSOD experiment system that separates practice sessions (outside magnet) from fMRI sessions (inside magnet). 

**This is now a PORTABLE version that can run from any computer without hard-coded paths.**

## Overview

The new system consists of two separate session types:

1. **Practice Session** (`sessionType = 'practice'`): Run outside the magnet
   - All 3 examples (2 no-memory, 1 memory)
   - No fixation crosses
   - Full instructions
   - Participants learn the task

2. **fMRI Session** (`sessionType = 'fMRI'`): Run inside the magnet
   - 1 no-memory example (refresher)
   - All test trials for the specific day
   - Fixation crosses included
   - Brief instructions only

## Files Created

### New Functions
- `PTSODfuncICONSheb_Practice.m` - Practice version (no fixation crosses)
- `PTSODfuncICONSheb_fMRI_Test.m` - fMRI version (with fixation crosses)
- `PTSODfunc_SplitDays_fMRI_New.m` - Main script that handles both session types
- `Run_PTSOD_Experiment.m` - Simple interface to run the experiment

### Data Files
- Practice data: `SubID_PTSOD_dayX_practice.mat`
- fMRI data: `SubID_PTSOD_dayX_fMRI.mat`
- Individual trial files: `SubID_PTSOD_dayX_sessionType_trialN.mat`

## How to Run the Experiment

### Option 1: Use the Simple Interface (PORTABLE)
```matlab
% Navigate to the Code directory (any location)
cd('path/to/PTSOD/Code')

% Run the experiment runner
Run_PTSOD_Experiment
```

The script will prompt you for:
- Subject ID (e.g., 'TS263')
- Day (1 or 2)
- Session Type ('practice' or 'fMRI')

### Option 2: Direct Function Call (PORTABLE)
```matlab
% Navigate to the Code directory (any location)
cd('path/to/PTSOD/Code')

% For practice session (outside magnet)
[dataTable, filename] = PTSODfunc_SplitDays_fMRI_New('TS263', 1, 'practice');

% For fMRI session (inside magnet)
[dataTable, filename] = PTSODfunc_SplitDays_fMRI_New('TS263', 1, 'fMRI');
```

## Session Flow

### Practice Session (Outside Magnet)
1. General instructions (slides 1-6)
2. No-memory example 1
3. No-memory instructions (slide 7)
4. No-memory example 2
5. Memory instructions (slide 8)
6. Memory example
7. Final instructions (slide 9)
8. Thank you screen (slide 10)

### fMRI Session (Inside Magnet)
1. Brief instructions (slide 9)
2. No-memory example (refresher)
3. Test trials (Day 1: odd trials, Day 2: even trials)
4. Thank you screen (slide 10)

## Key Differences

| Feature | Practice Session | fMRI Session |
|---------|------------------|--------------|
| Fixation Crosses | ❌ No | ✅ Yes (6s each) |
| Examples | 3 (2 no-memory, 1 memory) | 1 (no-memory only) |
| Instructions | Full | Brief |
| Test Trials | ❌ No | ✅ Yes |
| Memory Timer | 30s | 30s |
| Exit Key | E | E |

## Data Structure

Both session types save data in the same format:
- `arena`: Arena name
- `numObjects`: Number of objects in arena
- `level`: Difficulty level
- `memory`: Memory condition (0/1)
- `angle`: Selected angle
- `relDist`: Selected relative distance
- `correctAngle`: Correct angle
- `correctRelDist`: Correct relative distance
- `errorAngle`: Angular error
- `errorRelDist`: Distance error
- `reactionTime`: Response time
- `skiptime`: Skipped time
- `overallTime`: Total session time
- `order`: Trial order
- `xMouse`, `yMouse`: Final avatar position

## Portable Setup

### Automatic Path Detection
The portable version automatically:
- Detects the project root directory
- Sets up all necessary paths
- Adds the Code directory to MATLAB's path
- Creates the Results directory if needed

### Testing Portability
Run the test script to verify everything works:
```matlab
testPortability
```

### Troubleshooting

### Common Issues
1. **Screen not found**: Check `screenNumber` in the functions
2. **Path errors**: The portable version should handle this automatically
3. **Early exit**: Press 'E' key to exit at any time
4. **Data not saved**: Check the Results folder permissions

### Recovery
If the experiment exits early, partial data will be saved. Use the `combinePartialData` function to recover:
```matlab
[dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
```

## Notes

- The practice session is designed to be run once per participant to learn the task
- The fMRI session should be run twice (Day 1 and Day 2) with different trial sets
- All timing is optimized for fMRI scanning
- The system automatically handles trial randomization and data saving 