%% Test Portability Script
% This script tests that the portable PTSOD setup works correctly
% Run this script to verify all paths are properly detected

clear; clc;

fprintf('=== PTSOD Portability Test ===\n\n');

try
    % Test the setup function
    fprintf('Testing setupPTSOD()...\n');
    [projectRoot, resultPath, stimuliPath, instructionsPath] = setupPTSOD();
    
    fprintf('✅ Setup successful!\n\n');
    
    % Test that all required directories exist
    fprintf('Testing required directories...\n');
    
    requiredDirs = {
        fullfile(stimuliPath, 'nomemory_screens');
        fullfile(stimuliPath, 'memory_screens');
        fullfile(stimuliPath, 'nomemory_screens_HE');
        fullfile(stimuliPath, 'memory_screens_HE');
        fullfile(stimuliPath, 'white_png');
        fullfile(instructionsPath, 'instructions_practice_fmri1');
    };
    
    dirNames = {
        'Stimuli/nomemory_screens';
        'Stimuli/memory_screens';
        'Stimuli/nomemory_screens_HE';
        'Stimuli/memory_screens_HE';
        'Stimuli/white_png';
        'Instructions_HE/instructions_practice_fmri1';
    };
    
    allDirsExist = true;
    for i = 1:length(requiredDirs)
        if exist(requiredDirs{i}, 'dir')
            fprintf('✅ %s\n', dirNames{i});
        else
            fprintf('❌ %s (MISSING)\n', dirNames{i});
            allDirsExist = false;
        end
    end
    
    fprintf('\n');
    
    % Test that some key files exist
    fprintf('Testing key files...\n');
    
    % Check for PNG files in stimuli directories
    nomemoryFiles = dir(fullfile(stimuliPath, 'nomemory_screens', '*.png'));
    memoryFiles = dir(fullfile(stimuliPath, 'memory_screens', '*.png'));
    instructionFiles = dir(fullfile(instructionsPath, 'instructions_practice_fmri1', '*.png'));
    
    % Filter out AppleDouble metadata files (files starting with "._")
    nomemoryFiles = nomemoryFiles(~startsWith({nomemoryFiles.name}, '._'));
    memoryFiles = memoryFiles(~startsWith({memoryFiles.name}, '._'));
    instructionFiles = instructionFiles(~startsWith({instructionFiles.name}, '._'));
    
    if ~isempty(nomemoryFiles)
        fprintf('✅ nomemory_screens: %d PNG files found\n', length(nomemoryFiles));
    else
        fprintf('❌ nomemory_screens: No PNG files found\n');
    end
    
    if ~isempty(memoryFiles)
        fprintf('✅ memory_screens: %d PNG files found\n', length(memoryFiles));
    else
        fprintf('❌ memory_screens: No PNG files found\n');
    end
    
    if ~isempty(instructionFiles)
        fprintf('✅ instructions: %d PNG files found\n', length(instructionFiles));
    else
        fprintf('❌ instructions: No PNG files found\n');
    end
    
    fprintf('\n');
    
    % Test MATLAB path
    fprintf('Testing MATLAB path...\n');
    codePath = fullfile(projectRoot, 'Code');
    if contains(path, codePath)
        fprintf('✅ Code directory added to MATLAB path\n');
    else
        fprintf('❌ Code directory not in MATLAB path\n');
    end
    
    fprintf('\n');
    
    % Summary
    if allDirsExist
        fprintf('🎉 All tests passed! The PTSOD experiment is ready to run.\n');
        fprintf('\nTo start the experiment, run:\n');
        fprintf('  Run_PTSOD_Experiment\n');
    else
        fprintf('⚠️  Some directories are missing. Please check the project structure.\n');
        fprintf('Refer to README_Portable_PTSOD.md for the required directory structure.\n');
    end
    
catch ME
    fprintf('❌ Test failed with error: %s\n', ME.message);
    fprintf('Please ensure you are running this script from within the PTSOD project directory.\n');
end

fprintf('\n=== Test Complete ===\n'); 