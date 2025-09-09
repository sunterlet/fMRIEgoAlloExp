%% Setup fMRI Exploration Environment
% This script helps set up the fMRI directory for running exploration experiments
% including PTSOD and other experiments

clear; clc;

fprintf('=== fMRI Exploration Setup ===\n\n');

% Get current directory
currentDir = pwd;
fprintf('Current directory: %s\n', currentDir);

% Check if we're in the right location (fMRI directory)
if ~contains(currentDir, 'fMRI')
    fprintf('Warning: Current directory does not contain "fMRI".\n');
    fprintf('Expected to be in: \\isi.storwis.weizmann.ac.il\\labs\\ramot\\sunt\\Navigation\\fMRI\\\n\n');
end

% Check for PTSOD directory
ptsodPath = fullfile(currentDir, 'PTSOD');
if exist(ptsodPath, 'dir')
    fprintf('✅ PTSOD directory found: %s\n', ptsodPath);
    
    % Check PTSOD structure
    ptsodCodePath = fullfile(ptsodPath, 'Code');
    ptsodStimuliPath = fullfile(ptsodPath, 'Stimuli');
    ptsodInstructionsPath = fullfile(ptsodPath, 'Instructions_HE');
    
    if exist(ptsodCodePath, 'dir')
        fprintf('✅ PTSOD Code directory found\n');
    else
        fprintf('❌ PTSOD Code directory missing\n');
    end
    
    if exist(ptsodStimuliPath, 'dir')
        fprintf('✅ PTSOD Stimuli directory found\n');
    else
        fprintf('❌ PTSOD Stimuli directory missing\n');
    end
    
    if exist(ptsodInstructionsPath, 'dir')
        fprintf('✅ PTSOD Instructions directory found\n');
    else
        fprintf('❌ PTSOD Instructions directory missing\n');
    end
    
else
    fprintf('❌ PTSOD directory not found at: %s\n', ptsodPath);
    fprintf('Please ensure PTSOD is in the current directory.\n\n');
end

fprintf('\n=== Directory Structure Check ===\n');
fprintf('Expected structure:\n');
fprintf('fMRI/\n');
fprintf('├── PTSOD/\n');
fprintf('│   ├── Code/\n');
fprintf('│   ├── Stimuli/\n');
fprintf('│   └── Instructions_HE/\n');
fprintf('├── full_sequence_fMRI_exploration.m\n');
fprintf('└── [other experiments]\n\n');

% Test PTSOD setup
fprintf('=== Testing PTSOD Setup ===\n');
try
    % Add PTSOD Code to path
    if exist(ptsodCodePath, 'dir')
        addpath(ptsodCodePath);
        fprintf('✅ PTSOD Code added to MATLAB path\n');
        
        % Test setupPTSOD function
        [projectRoot, resultPath, stimuliPath, instructionsPath] = setupPTSOD();
        fprintf('✅ PTSOD setup successful\n');
        fprintf('  Project Root: %s\n', projectRoot);
        fprintf('  Results Path: %s\n', resultPath);
        fprintf('  Stimuli Path: %s\n', stimuliPath);
        fprintf('  Instructions Path: %s\n', instructionsPath);
        
    else
        fprintf('❌ Cannot test PTSOD setup - Code directory missing\n');
    end
    
catch ME
    fprintf('❌ PTSOD setup test failed: %s\n', ME.message);
end

fprintf('\n=== Setup Complete ===\n');
fprintf('To run the full sequence, use:\n');
fprintf('  full_sequence_fMRI_exploration\n\n');

fprintf('To test PTSOD only, use:\n');
fprintf('  cd PTSOD/Code\n');
fprintf('  testPortability\n'); 