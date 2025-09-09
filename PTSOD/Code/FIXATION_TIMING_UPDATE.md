# PTSOD fMRI Fixation Timing Update

## Overview
This document describes the updates made to ensure proper fixation timing in PTSOD fMRI runs according to the specified requirements.

## Required Fixation Timing
1. **8 TR fixation before the first trial** (after trigger)
2. **TR alignment + 4 TR fixation after each trial**
3. **4 TR fixation after the last trial** and before the thank you screen

## Changes Made

### 1. PTSODfuncICONSheb_fMRI_Test_Trigger.m

#### Initial 8 TR Fixation (Dummy)
- **Location**: After trigger received, before first trial
- **Duration**: Exactly 8 TRs (8 × 2.01s = 16.08s)
- **Fixation Cross**: Standardized 200px BLACK cross on WHITE background
- **Logging**: Continuous logging of fixation start/end events
- **Skip Option**: 'K' key to skip (for debugging)

#### TR Alignment Fixation
- **Location**: After each trial completion, before next TR boundary
- **Duration**: Variable (calculated to align with next TR)
- **Purpose**: Ensures proper fMRI data synchronization
- **Fixation Cross**: Standardized 200px BLACK cross on WHITE background
- **Logging**: Continuous logging of TR alignment events

#### Inter-Trial Fixation
- **Location**: After each trial (including last trial)
- **Duration**: Exactly 4 TRs (4 × 2.01s = 8.04s)
- **Fixation Cross**: Standardized 200px BLACK cross on WHITE background
- **Logging**: Continuous logging of inter-trial fixation events
- **Skip Option**: 'K' key to skip (for debugging)

### 2. PTSODfunc_SplitRuns_fMRI_New.m

#### Removed Final Fixation
- **Previous**: Had separate 4 TR final fixation before thank you screen
- **Current**: Final fixation now handled within trial function after last trial
- **Reason**: Avoids duplicate fixation and ensures consistent timing

## Standardized Fixation Cross Format

### Visual Specifications
- **Cross Size**: 200 pixels (standard text size equivalent)
- **Cross Color**: BLACK [0 0 0] on WHITE background [255 255 255]
- **Rendering**: Uses `DrawFormattedText` for consistent appearance
- **Position**: Center of screen

### Note on Color Scheme
- **PTSOD**: BLACK cross on WHITE background
- **Exploration Experiments**: WHITE cross on BLACK background
- **Dimensions**: Same (200px) for consistency across experiments

## Timing Precision

### TR Value
- **TR**: 2.01 seconds (hardcoded constant)
- **Alignment**: Within 0.1 TR (≈0.2 seconds) for proper scanner synchronization

### Fixation Durations
- **Initial Dummy**: 8 TRs = 16.08 seconds
- **Inter-Trial**: 4 TRs = 8.04 seconds
- **TR Alignment**: Variable (calculated for precise alignment)

## Logging and Data Collection

### Continuous Log Events
- `fixation_start`: Beginning of each fixation period
- `fixation_end`: Normal completion of fixation
- `fixation_skipped`: When 'K' key is pressed to skip
- `tr_alignment_fixation_start`: Beginning of TR alignment
- `tr_alignment_fixation_end`: End of TR alignment
- `inter_trial_fixation_start`: Beginning of inter-trial fixation
- `inter_trial_fixation_end`: End of inter-trial fixation

### Log Fields
- `RealTime`: Timestamp in HH:MM:SS.FFF format
- `trial_time`: Time since trial start
- `trial`: Trial number
- `condition_type`: 'test' for fMRI trials
- `phase`: 'fixation' for all fixation events
- `event`: Specific fixation event type
- `x`, `y`, `rotation_angle`: Position data (0.0 during fixation)

## Implementation Details

### Key Functions
- **Main Function**: `PTSODfuncICONSheb_fMRI_Test_Trigger()`
- **Screen Management**: Uses Psychtoolbox for precise timing
- **Key Handling**: ESC key to exit, 'K' key to skip fixation
- **Trigger Handling**: Serial port communication for scanner synchronization

### Error Handling
- **Graceful Exit**: ESC key allows experimenter to exit early
- **Data Preservation**: Partial data is saved if experiment exits early
- **Logging Continuity**: All events are logged even if skipped

## Usage Notes

### For Experimenters
- **Initial Setup**: Ensure proper COM port configuration
- **Skip Options**: Use 'K' key to skip fixation if needed for debugging
- **Exit Option**: Use ESC key to exit experiment early if necessary

### For Participants
- **Fixation Display**: Consistent visual appearance across all fixation periods
- **Timing**: Precise synchronization with scanner TR
- **Duration**: Predictable timing for experimental design

## Testing and Validation

### Test Scripts Available
- `test_PTSODfuncICONSheb_fMRI_Test_Trigger.m`: Comprehensive testing
- `simple_test_PTSOD.m`: Quick verification

### Validation Points
- **Timing Accuracy**: Verify TR alignment precision
- **Visual Consistency**: Ensure fixation cross appearance
- **Logging Completeness**: Check all events are recorded
- **Skip Functionality**: Test 'K' key skip option

## Compatibility

### MATLAB Version
- **Minimum**: MATLAB R2018b or later
- **Toolboxes**: Psychtoolbox 3.0.18 or later
- **Platform**: Windows, macOS, Linux

### Hardware Requirements
- **Display**: Any screen supported by Psychtoolbox
- **Serial Port**: For scanner trigger functionality
- **Performance**: Sufficient for 60Hz refresh rate

## Future Considerations

### Potential Enhancements
- **Configurable TR**: Allow TR value to be set via parameter
- **Flexible Timing**: Make fixation durations configurable
- **Advanced Logging**: Additional metadata for analysis
- **Visual Customization**: Options for different fixation cross styles

### Maintenance Notes
- **Code Structure**: Well-documented and modular design
- **Error Handling**: Comprehensive error checking and recovery
- **Logging**: Detailed event tracking for debugging and analysis
- **Standards**: Follows established coding conventions
