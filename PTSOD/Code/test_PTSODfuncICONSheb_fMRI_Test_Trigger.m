%% Test Script for PTSODfuncICONSheb_fMRI_Test_Trigger
% This script tests the PTSOD fMRI experiment function with various configurations
% Author: Test Script
% Date: 2024

clear all; close all; clc;

fprintf('=== PTSOD fMRI Test Script ===\n\n');

%% Test Configuration
% Set up test parameters
testConfig = struct();
testConfig.SubID = 'TEST001';
testConfig.day = 1;
testConfig.saveDir = fullfile(pwd, 'test_results');
testConfig.screenNumber = [];  % Will use default
testConfig.scanning = true;    % Test WITH fMRI trigger
testConfig.com = 'COM4';       % Default COM port
testConfig.TR = 2.01;          % Default TR

% Create test results directory
if ~exist(testConfig.saveDir, 'dir')
    mkdir(testConfig.saveDir);
    fprintf('Created test results directory: %s\n', testConfig.saveDir);
end

%% Test 1: Example Trial with Trigger (Single Trial)
fprintf('--- Test 1: Example Trial with Trigger ---\n');
try
    % Create example trial data
    exampleFiles = {'archive_scissors_notebook_5_lvlexample.png', true};
    
    fprintf('Running example trial with trigger enabled...\n');
    fprintf('Note: Example trials do not wait for trigger (only test trials do)\n');
    [results_example, exit_early_example] = PTSODfuncICONSheb_fMRI_Test_Trigger(...
        exampleFiles, 1, testConfig.saveDir, testConfig.SubID, ...
        testConfig.day, 'fMRI_example', testConfig.screenNumber, ...
        testConfig.scanning, testConfig.com, testConfig.TR);
    
    if exit_early_example
        fprintf('Example trial exited early.\n');
    else
        fprintf('Example trial completed successfully.\n');
        fprintf('Results structure size: %dx%d\n', size(results_example));
    end
    
catch ME
    fprintf('ERROR in example trial: %s\n', ME.message);
end

fprintf('\n');

%% Test 2: Test Trials with Trigger (Multiple Trials)
fprintf('--- Test 2: Test Trials with Trigger ---\n');
try
    % Create test trial data with multiple trials
    testFiles = {
        'toilet_lightbulb_faucet_7_lvl1.png', true;
        'table_bed_sofa_3_lvl2.png', false;
        'sword_gun_shield_5_lvl1.png', true;
        'socks_shirt_shorts_3_lvl1.png', false
    };
    numTrials = size(testFiles, 1);
    
    fprintf('Running %d test trials with trigger enabled...\n', numTrials);
    fprintf('IMPORTANT: This will wait for a scanner trigger before starting!\n');
    fprintf('The experiment will show a fixation cross and wait for trigger.\n');
    fprintf('If no trigger is received, press ''E'' to exit early.\n\n');
    
    [results_test, exit_early_test] = PTSODfuncICONSheb_fMRI_Test_Trigger(...
        testFiles, numTrials, testConfig.saveDir, testConfig.SubID, ...
        testConfig.day, 'fMRI_test', testConfig.screenNumber, ...
        testConfig.scanning, testConfig.com, testConfig.TR);
    
    if exit_early_test
        fprintf('Test trials exited early.\n');
    else
        fprintf('Test trials completed successfully!\n');
        fprintf('Results structure size: %dx%d\n', size(results_test));
        
        % Display some basic statistics
        if ~isempty(results_test) && size(results_test, 1) > 0
            fprintf('Sample results from first trial:\n');
            fprintf('  Selected Angle: %.2f°\n', results_test{1, 3});
            fprintf('  Selected Distance: %.2f pixels\n', results_test{1, 4});
            fprintf('  Correct Angle: %.2f°\n', results_test{1, 5});
            fprintf('  Correct Distance: %.2f pixels\n', results_test{1, 6});
            fprintf('  Angle Error: %.2f°\n', results_test{1, 7});
            fprintf('  Distance Error: %.2f pixels\n', results_test{1, 8});
            fprintf('  Reaction Time: %.2f seconds\n', results_test{1, 9});
        end
    end
    
catch ME
    fprintf('ERROR in test trials: %s\n', ME.message);
end

fprintf('\n');

%% Test 3: Single Trial with Trigger
fprintf('--- Test 3: Single Trial with Trigger ---\n');
try
    % Test with a single trial and trigger enabled
    fprintf('Running single trial with trigger enabled...\n');
    fprintf('This will wait for a scanner trigger before starting.\n');
    fprintf('If no trigger is received, press ''E'' to exit early.\n\n');
    
    % Use a single test trial for scanning mode test
    scanFiles = {'printer_telephone_laptop_7_lvl2.png', true};
    
    [results_scan, exit_early_scan] = PTSODfuncICONSheb_fMRI_Test_Trigger(...
        scanFiles, 1, testConfig.saveDir, testConfig.SubID, ...
        testConfig.day, 'fMRI_single_test', testConfig.screenNumber, ...
        testConfig.scanning, testConfig.com, testConfig.TR);
    
    if exit_early_scan
        fprintf('Single trial test exited early.\n');
    else
        fprintf('Single trial test completed successfully!\n');
    end
    
catch ME
    fprintf('ERROR in single trial test: %s\n', ME.message);
end

fprintf('\n');

%% Test 4: Trigger Configuration Test
fprintf('--- Test 4: Trigger Configuration Test ---\n');
try
    % Test with different trigger configurations
    fprintf('Testing trigger with different COM port...\n');
    fprintf('Using COM3 instead of COM4...\n');
    
    % Test with different COM port
    testConfig.com = 'COM3';
    
    [results_com3, exit_early_com3] = PTSODfuncICONSheb_fMRI_Test_Trigger(...
        exampleFiles, 1, testConfig.saveDir, testConfig.SubID, ...
        testConfig.day, 'fMRI_com3_test', testConfig.screenNumber, ...
        testConfig.scanning, testConfig.com, testConfig.TR);
    
    if exit_early_com3
        fprintf('COM3 test exited early.\n');
    else
        fprintf('COM3 test completed successfully.\n');
    end
    
catch ME
    fprintf('ERROR in COM3 test: %s\n', ME.message);
    fprintf('This is expected if COM3 is not available.\n');
end

fprintf('\n');

%% Summary
fprintf('=== Trigger Test Summary ===\n');
fprintf('Test results directory: %s\n', testConfig.saveDir);
fprintf('Check the directory for saved trial data files.\n');
fprintf('All tests were run with scanning = true (trigger enabled).\n');
fprintf('Remember: Test trials will wait for scanner trigger before starting.\n');
fprintf('Test script completed.\n\n');

%% Helper function to display results structure
function displayResultsInfo(results, trialName)
    if ~isempty(results)
        fprintf('%s Results:\n', trialName);
        fprintf('  Number of trials: %d\n', size(results, 1));
        fprintf('  Number of columns: %d\n', size(results, 2));
        
        % Display column headers (based on the function's output structure)
        headers = {'File1', 'File2', 'SelAngle', 'SelDist', 'CorrAngle', ...
                  'CorrDist', 'AngleError', 'DistError', 'ReactionTime', ...
                  'SkipTime', 'TrialNum', 'AvatarX', 'AvatarY'};
        
        fprintf('  Column structure:\n');
        for i = 1:min(length(headers), size(results, 2))
            fprintf('    %d: %s\n', i, headers{i});
        end
    else
        fprintf('%s: No results available\n', trialName);
    end
end 