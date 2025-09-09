%% Practice Sessions - Egocentric Allocentric Translation fMRI Experiment
% This file runs all practice sessions outside the magnet

%% Setup Environment
sca; close all; clc; clear;

%% Screen Selection
selectedScreen = select_screen(); 
% selectedScreen = 1;
%% Participant Information
SubID = 'WM347';

%% Setup Centralized Results Directory
% Set centralized results directory to ensure all data is saved in one location
centralized_results_dir = fullfile(pwd, 'Results');
setenv('CENTRALIZED_RESULTS_DIR', centralized_results_dir);
fprintf('\n=== Setting Centralized Results Directory ===\n');
fprintf('Centralized results directory: %s\n', centralized_results_dir);

% Create the Results directory if it doesn't exist
if ~exist(centralized_results_dir, 'dir')
    mkdir(centralized_results_dir);
    fprintf('Created Results directory: %s\n', centralized_results_dir);
end

% Create SubID subfolder in Results directory
subid_dir = fullfile(centralized_results_dir, SubID);
if ~exist(subid_dir, 'dir')
    mkdir(subid_dir);
    fprintf('Created SubID subfolder: %s\n', subid_dir);
end

%% Add Relevant Paths
fprintf('\n=== Adding Relevant Paths ===\n');

% Add PTSOD Code directory to path
ptsodCodePath = fullfile(pwd, 'PTSOD', 'Code');
if exist(ptsodCodePath, 'dir')
    addpath(ptsodCodePath);
    fprintf('✓ PTSOD Code added to path: %s\n', ptsodCodePath);
else
    fprintf('⚠ PTSOD Code directory not found at: %s\n', ptsodCodePath);
end

% Add exploration directory to path
explorationPath = fullfile(pwd, 'exploration');
if exist(explorationPath, 'dir')
    addpath(explorationPath);
    fprintf('✓ Exploration experiment added to path: %s\n', explorationPath);
else
    fprintf('⚠ Exploration experiment directory not found at: %s\n', explorationPath);
end

% Add sounds directory to path
soundsPath = fullfile(pwd, 'sounds');
if exist(soundsPath, 'dir')
    addpath(soundsPath);
    fprintf('✓ Sounds directory added to path: %s\n', soundsPath);
else
    fprintf('⚠ Sounds directory not found at: %s\n', soundsPath);
end

% Add arenas_new_icons directory to path
iconsPath = fullfile(pwd, 'arenas_new_icons');
if exist(iconsPath, 'dir')
    addpath(genpath(iconsPath));
    fprintf('✓ Arena icons added to path: %s\n', iconsPath);
else
    fprintf('⚠ Arena icons directory not found at: %s\n', iconsPath);
end

fprintf('Path setup completed.\n');

%% PTSOD Practice
fprintf('\n=== PTSOD Practice Session ===\n');
PTSODfunc_SplitDays_fMRI_New(SubID, 1, 'practice', selectedScreen);

%% Navigation Practice Sessions
fprintf('\n=== Navigation Practice Sessions ===\n');

% Snake Practice
fprintf('\n--- Snake Practice ---\n');
run_snake_game('practice', SubID);

% One Target Practice
fprintf('\n--- One Target Practice ---\n');
run_one_target('practice', SubID);

% Multi-Arena Practice
fprintf('\n--- Multi-Arena Practice ---\n');
practice_conditions = {'full', 'limited', 'none'};

for j = 1:length(practice_conditions)
    visibility = practice_conditions{j};
    fprintf('\n--- Practice Condition %d: %s visibility ---\n', j, visibility);
    run_multi_arena('practice', SubID, j, j, length(practice_conditions), visibility);
end

% Thank you screen
fprintf('\n--- Practice Complete ---\n');
run_multi_arena('practice', SubID, 1, 1, 1, 'thank_you');

fprintf('\n=== ALL PRACTICE SESSIONS COMPLETED ===\n'); 