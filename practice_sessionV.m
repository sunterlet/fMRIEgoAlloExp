%% Practice Sessions - Egocentric Allocentric Translation fMRI Experiment
% This file runs all practice sessions outside the magnet

%% Setup Environment
sca; close all; clc; clear;

%% Screen Selection
% selectedScreen = select_screen(); 
selectedScreen = 1;
%% Participant Information
SubID = 'tst';

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

% Add exploration_trigger_vection directory to path (vection tasks)
vectionPath = fullfile(pwd, 'exploration_trigger_vection');
if exist(vectionPath, 'dir')
    addpath(vectionPath);
    fprintf('✓ Exploration trigger vection added to path: %s\n', vectionPath);
else
    fprintf('⚠ Exploration trigger vection directory not found at: %s\n', vectionPath);
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

%% Vection Practice (wrappers in exploration_trigger_vection/)
% Snake: snake-ins.png, 90 s, minimap 30 s then auto-hide
% One target: OT-ins.png, 3 trials, trial intro (זירה X/3), trial 1 minimap on
% Multi target: FA-ins.png, 3 trials (garden, zoo, beach), minimap togglable with B

%% Snake Vection Practice
fprintf('\n--- Snake Vection Practice ---\n');
run_snake_vection('practice', SubID, [], [], [], selectedScreen);

%% PTSOD Practice
fprintf('\n=== PTSOD Practice Session ===\n');
PTSODfunc_SplitDays_fMRI_New(SubID, 1, 'practice', 2);

%% One Target Vection Practice
fprintf('\n--- One Target Vection Practice ---\n');
run_one_target_vection('practice', SubID, [], [], [], selectedScreen);

%% Multi-Arena Vection Practice
fprintf('\n--- Multi-Arena Vection Practice ---\n');
run_multi_target_vection('practice', SubID, selectedScreen);

fprintf('\n--- Practice Complete ---\n');

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