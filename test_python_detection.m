%% Test Python Detection for fMRI Navigation Experiments
% This script tests if the Python detection works correctly

fprintf('=== Testing Python Detection ===\n');

% Test the find_python function from run_snake_game
try
    % Add the exploration directory to path
    addpath('exploration');
    
    % Test the find_python function
    python_cmd = find_python();
    fprintf('✓ Python command found: %s\n', python_cmd);
    
    % Test if the command actually works
    [status, result] = system(sprintf('%s --version', python_cmd));
    if status == 0
        fprintf('✓ Python command works: %s', result);
    else
        fprintf('✗ Python command failed: %s', result);
    end
    
    % Test if pygame is available
    [status, result] = system(sprintf('%s -c "import pygame; print(''pygame OK'')"', python_cmd));
    if status == 0
        fprintf('✓ pygame is available\n');
    else
        fprintf('✗ pygame not available: %s', result);
    end
    
    fprintf('\n=== Python Detection Test Complete ===\n');
    
catch ME
    fprintf('✗ Error in Python detection: %s\n', ME.message);
end 