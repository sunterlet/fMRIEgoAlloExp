% Add paths for portable experiment
% Run this script before using run_one_target function

% Get current directory
current_dir = pwd;

% Add exploration directory to path
exploration_dir = fullfile(current_dir, 'exploration');
if exist(exploration_dir, 'dir')
    addpath(exploration_dir);
    fprintf('Added to path: %s\n', exploration_dir);
else
    error('Exploration experiment directory not found: %s', exploration_dir);
end

fprintf('Paths added successfully. You can now use run_one_target function.\n'); 