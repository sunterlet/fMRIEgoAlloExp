# fMRI Experiment Organization

## File Structure

The fMRI experiment has been split into separate files for better organization:

### Main Files
- **`practice_sessions.m`** - Runs all practice sessions (outside magnet)
- **`fmri_sessions.m`** - Runs all fMRI sessions (inside magnet)
- **`run_full_experiment.m`** - Master file to run both sessions
- **`full_sequence_exploration.m`** - Original combined file (kept for reference)

## Session Breakdown

### Practice Sessions (`practice_sessions.m`)
**Location**: Outside the magnet
**Components**:
1. PTSOD practice session
2. One target practice (snake game + one target)
3. Multi-arena practice (3 conditions: full, limited, none visibility)

### fMRI Sessions (`fmri_sessions.m`)
**Location**: Inside the magnet
**Components**:
1. PTSOD fMRI session
2. One target run design (12 trials: 6 Snake + 6 One Target, intertwined)
3. Full arena run design (12 trials: 6 Snake + 6 Multi-Arena, intertwined)

## Arena Assignments

### Practice Arenas (Outside Magnet)
- `garden`, `beach`, `village`, `ranch`, `zoo`, `school`

### fMRI Arenas (Inside Magnet)
- `hospital`, `bookstore`, `gym`, `museum`, `airport`, `market`

## Usage

### Run Practice Only
```matlab
practice_sessions
```

### Run fMRI Only
```matlab
fmri_sessions
```

### Run Both Sessions
```matlab
run_full_experiment
```

## Run Design Summary

### One Target Run Design (12 trials)
- 6 Snake trials + 6 One Target trials, intertwined
- Trials run continuously to eliminate timing gaps
- Each trial type is randomized by its individual script

### Full Arena Run Design (12 trials)
- 6 Snake trials + 6 Multi-Arena trials, intertwined
- Trials run continuously to eliminate timing gaps
- Each trial type is randomized by its individual script

## Data Output
All results are saved in `exploration/results/` 