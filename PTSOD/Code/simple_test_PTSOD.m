%% Simple Test Script for PTSODfuncICONSheb_fMRI_Test_Trigger
% Quick test to verify the function works correctly
% Run this script to test the PTSOD experiment function

clear all; close all; clc;

fprintf('=== Simple PTSOD Test ===\n\n');

%% Test Setup
% Create a simple test with one example trial
testFiles = {'archive_scissors_notebook_5_lvlexample.png', true};

% Test parameters
saveDir = fullfile(pwd, 'test_results');
SubID = 'TEST001';
day = 1;
trialType = 'fMRI_example';
scanning = false;  % No fMRI trigger for simple test

% Create results directory
if ~exist(saveDir, 'dir')
    mkdir(saveDir);
    fprintf('Created test results directory: %s\n', saveDir);
end

%% Run Test
fprintf('Starting PTSOD test...\n');
fprintf('Instructions:\n');
fprintf('- Use arrow keys (1,2,3,4) to navigate\n');
fprintf('- Press 6 to complete the trial\n');
fprintf('- Press E to exit early\n');
fprintf('- Press K to skip timers/fixation\n\n');

try
    [results, exit_early] = PTSODfuncICONSheb_fMRI_Test_Trigger(...
        testFiles, 1, saveDir, SubID, day, trialType, [], scanning);
    
    if exit_early
        fprintf('Test exited early.\n');
    else
        fprintf('Test completed successfully!\n');
        
        % Display results
        if ~isempty(results)
            fprintf('\nResults:\n');
            fprintf('Selected Angle: %.2f°\n', results{1, 3});
            fprintf('Selected Distance: %.2f pixels\n', results{1, 4});
            fprintf('Correct Angle: %.2f°\n', results{1, 5});
            fprintf('Correct Distance: %.2f pixels\n', results{1, 6});
            fprintf('Angle Error: %.2f°\n', results{1, 7});
            fprintf('Distance Error: %.2f pixels\n', results{1, 8});
            fprintf('Reaction Time: %.2f seconds\n', results{1, 9});
        end
    end
    
catch ME
    fprintf('ERROR: %s\n', ME.message);
    fprintf('Stack trace:\n');
    for i = 1:length(ME.stack)
        fprintf('  %s (line %d)\n', ME.stack(i).name, ME.stack(i).line);
    end
end

fprintf('\nTest completed. Check %s for saved data files.\n', saveDir); 