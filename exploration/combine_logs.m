% Script to combine all multi-arena log files
clear; clc;

% Add the practice_sessions.m file to path to access the function
addpath('.');

% Set parameters
participant_id = 'test';
results_dir = 'U:\sunt\Navigation\fMRI\Results';

fprintf('Combining multi-arena log files for participant: %s\n', participant_id);
fprintf('Results directory: %s\n', results_dir);

% Run the combination function
combine_all_multi_arena_logs(participant_id, results_dir);

fprintf('Combination complete!\n');
