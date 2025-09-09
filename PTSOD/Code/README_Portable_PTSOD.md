# PTSOD Experiment - Portable Version

This is the portable version of the PTSOD (Point-to-Same-Object-Direction) experiment that can run from any computer without requiring specific hard-coded paths.

## 🚀 Quick Start

1. **Copy the entire PTSOD folder** to any computer with MATLAB installed
2. **Navigate to the Code directory** in MATLAB
3. **Run the experiment**:
   ```matlab
   Run_PTSOD_Experiment
   ```

## 📁 Project Structure

The portable version automatically detects the project structure:

```
PTSOD/
├── Code/                    # MATLAB functions and scripts
│   ├── setupPTSOD.m        # Portable setup function
│   ├── Run_PTSOD_Experiment.m  # Main experiment runner
│   └── [other .m files]    # Experiment functions
├── Stimuli/                # Experiment stimuli
│   ├── nomemory_screens/   # No-memory trial images
│   ├── memory_screens/     # Memory trial images
│   ├── nomemory_screens_HE/ # Hebrew no-memory screens
│   ├── memory_screens_HE/   # Hebrew memory screens
│   └── white_png/          # Object icons
├── Instructions_HE/         # Hebrew instruction images
│   └── instructions_practice_fmri1/
└── Results/                # Output data (created automatically)
```

## 🔧 How Portability Works

### Automatic Path Detection
The `setupPTSOD()` function automatically:
- Finds the project root by looking for key directories (`Stimuli` and `Instructions_HE`)
- Sets up all necessary paths relative to the project root
- Adds the Code directory to MATLAB's path
- Creates the Results directory if it doesn't exist

### No Hard-coded Paths
All hard-coded paths like `Z:\sunt\Navigation\fMRI\PTSOD` have been replaced with:
- Relative paths using `fullfile()`
- Automatic path detection via `setupPTSOD()`
- Cross-platform compatibility

## 📋 Requirements

- **MATLAB** (R2016b or later recommended)
- **Psychtoolbox** for stimulus presentation
- **Image Processing Toolbox** for image handling

## 🎯 Running the Experiment

### Method 1: Interactive Runner (Recommended)
```matlab
% Navigate to the Code directory
cd('path/to/PTSOD/Code');

% Run the experiment
Run_PTSOD_Experiment
```

### Method 2: Direct Function Call
```matlab
% Navigate to the Code directory
cd('path/to/PTSOD/Code');

% Run specific session
[dataTable, filename] = PTSODfunc_SplitDays_fMRI_New('TS263', 1, 'practice');
```

## 📊 Experiment Parameters

- **Subject ID**: Initials + 3 digits (e.g., 'TS263')
- **Day**: 1 or 2
- **Session Type**: 'practice' (outside magnet) or 'fMRI' (inside magnet)

## 🔄 Session Types

### Practice Session (Outside Magnet)
- All 3 examples (2 no-memory, 1 memory)
- No fixation crosses
- Full instructions
- 30-second memory period

### fMRI Session (Inside Magnet)
- 1 no-memory example
- All test trials for the specified day
- Fixation crosses included
- Brief instructions only
- 30-second memory period

## 📁 Data Output

Results are automatically saved to the `Results/` directory with the format:
- `PTSOD_[SubID]_Day[day]_[sessionType]_[timestamp].mat`

## 🛠️ Troubleshooting

### "Could not find PTSOD project root"
- Ensure you're running from within the PTSOD project directory
- Check that `Stimuli` and `Instructions_HE` directories exist
- Verify the project structure is intact

### Missing files or directories
- Ensure all required directories exist:
  - `Stimuli/nomemory_screens/`
  - `Stimuli/memory_screens/`
  - `Stimuli/nomemory_screens_HE/`
  - `Stimuli/memory_screens_HE/`
  - `Stimuli/white_png/`
  - `Instructions_HE/instructions_practice_fmri1/`

### Psychtoolbox errors
- Install Psychtoolbox if not already installed
- Ensure proper display setup for your system

## 🔧 Customization

### Adding New Stimuli
1. Place new images in the appropriate `Stimuli` subdirectory
2. Update the file loading logic if needed
3. The portable system will automatically detect the new files

### Modifying Instructions
1. Replace instruction images in `Instructions_HE/instructions_practice_fmri1/`
2. Maintain the same naming convention
3. Update the instruction sequence if needed

## 📝 Version History

### Portable Version (Current)
- ✅ Automatic path detection
- ✅ Cross-platform compatibility
- ✅ No hard-coded paths
- ✅ Self-contained setup

### Previous Version
- ❌ Hard-coded paths (`Z:\sunt\Navigation\fMRI\PTSOD`)
- ❌ Required specific directory structure
- ❌ Not portable between computers

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all required directories and files exist
3. Ensure MATLAB and Psychtoolbox are properly installed
4. Check that you're running from the correct directory

## 📄 License

This code is part of the PTSOD experiment system. Please ensure proper attribution when using or modifying this code. 