# Trigger Functions - Extracted from MAYA-playMovies_full.m

This directory contains trigger handling functions extracted from the `MAYA-playMovies_full.m` script for fMRI experiments.

## Files

### Core Trigger Functions

1. **`initTrigger.m`** - Initialize scanner trigger connection
   - **Inputs**: `scanning` (boolean), `com` (serial port string)
   - **Outputs**: `s` (serial object), `sync` (trigger counter)
   - **Purpose**: Sets up serial connection for scanner trigger detection

2. **`waitForTrigger.m`** - Wait for scanner trigger signal
   - **Inputs**: `s` (serial object), `scanning` (boolean)
   - **Purpose**: Waits for the scanner trigger signal before proceeding with experiment

3. **`closeTrigger.m`** - Close trigger connection
   - **Inputs**: `s` (serial object), `scanning` (boolean)
   - **Purpose**: Properly closes the serial port connection

### Example Usage

4. **`triggerExample.m`** - Example implementation
   - Demonstrates how to use the trigger functions in a complete experiment
   - Includes error handling and cleanup

## Usage Pattern

```matlab
% 1. Initialize trigger
[s, sync] = initTrigger(scanning, com);

% 2. Wait for trigger
waitForTrigger(s, scanning);

% 3. Run your experiment
% ... your experimental code here ...

% 4. Clean up
closeTrigger(s, scanning);
```

## Key Features

- **Modular Design**: Each function handles a specific aspect of trigger management
- **Error Handling**: Proper cleanup in case of errors
- **Flexible**: Can be used with or without scanning mode
- **Reusable**: Can be integrated into any fMRI experiment

## Dependencies

- MATLAB's Instrument Control Toolbox (for serial communication)
- PsychToolbox (for screen management in scanning mode)

## Notes

- The trigger detection uses the `DataSetReady` pin status
- Baud rate is set to 9600
- Functions are designed to work with fMRI scanner triggers
- All functions include proper documentation and error handling

## Integration with Original Script

These functions extract the trigger handling logic from the original `MAYA-playMovies_full.m` script:

- **Lines 108-112**: Trigger initialization
- **Lines 158-175**: Wait for trigger loop
- **Lines 290-294**: Trigger cleanup

The extracted functions maintain the same functionality while providing better modularity and reusability. 