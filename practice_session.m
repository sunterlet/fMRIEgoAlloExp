%% Practice Sessions - Egocentric Allocentric Translation fMRI Experiment
% This file runs all practice sessions outside the magnet

%% Setup Environment
sca; close all; clc; clear;

%% Screen Selection
% selectedScreen = select_screen(); 
selectedScreen = 1;
%% Participant Information
SubID = 'IT574';

%% Setup Centralized Results Directory
% Set centralized results directory to ensure all data is saved in one location
% Path structure: Results/SubID/fMRI/Behavior/Practice/
base_results_dir = fullfile(pwd, 'Results', SubID, 'fMRI', 'Behavior', 'Practice');
centralized_results_dir = base_results_dir;
setenv('CENTRALIZED_RESULTS_DIR', centralized_results_dir);
fprintf('\n=== Setting Centralized Results Directory ===\n');
fprintf('Centralized results directory: %s\n', centralized_results_dir);

% Create the full directory structure if it doesn't exist
if ~exist(centralized_results_dir, 'dir')
    mkdir(centralized_results_dir);
    fprintf('Created practice results directory: %s\n', centralized_results_dir);
else
    fprintf('Practice results directory already exists: %s\n', centralized_results_dir);
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

fprintf('Path setup completed.\n');

%% Snake Practice
fprintf('\n--- Snake Practice ---\n');
run_snake_game('practice', SubID, [], [], [], selectedScreen);

%% PTSOD Practice
fprintf('\n=== PTSOD Practice Session ===\n');
PTSODfunc_SplitDays_fMRI_New(SubID, 1, 'practice', 2);

%% One Target Practice
fprintf('\n--- One Target Practice ---\n');
run_one_target('practice', SubID, [], [], [], selectedScreen);

%% Multi-Arena Practice
fprintf('\n--- Multi-Arena Practice ---\n');
practice_conditions = {'full', 'limited', 'none'};

for j = 1:length(practice_conditions)
    visibility = practice_conditions{j};
    fprintf('\n--- Practice Condition %d: %s visibility ---\n', j, visibility);
    % Run only 1 arena per condition (handled internally by run_multi_arena)
    run_multi_arena('practice', SubID, j, j, length(practice_conditions), visibility, selectedScreen);
end

% Thank you screen
fprintf('\n--- Practice Complete ---\n');
run_multi_arena('practice', SubID, 1, 1, 1, 'thank_you', selectedScreen);

fprintf('\n=== ALL PRACTICE SESSIONS COMPLETED ===\n');

%% Optional: Additional Individual Practice
% If participant needs extra practice, uncomment and run one of these commands:

% ONE TARGET INDIVIDUAL PRACTICE
% Options for condition: 'training', 'dark_training', 'test'
% Syntax: practice_one_target_individual(SubID, condition, num_trials)
% Examples:
% practice_one_target_individual(SubID, 'training', 2);      % 2 training trials
% practice_one_target_individual(SubID, 'dark_training', 1); % 1 dark training trial
% practice_one_target_individual(SubID, 'test', 1);          % 1 test trial

% MULTI-ARENA INDIVIDUAL PRACTICE  
% Options for visibility: 'full', 'limited', 'none'
% Available arenas: full (beach), limited (ranch), none (school, library)
% Syntax: practice_multi_arena_individual(SubID, visibility, num_arenas)
% Examples:
% practice_multi_arena_individual(SubID, 'full', 1);    % 1 full visibility arena (beach)
% practice_multi_arena_individual(SubID, 'limited', 1); % 1 limited visibility arena (ranch)
% practice_multi_arena_individual(SubID, 'none', 1);    % 1 no visibility arena (school)
% practice_multi_arena_individual(SubID, 'none', 2);    % 2 no visibility arenas (school, library)