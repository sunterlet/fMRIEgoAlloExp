% Full Sequence for Snake and Multi-Arena Block Design
% This script runs a complete fMRI experiment with snake and multi-arena tasks
% in a block design format using the new arenas from Final_New_Arenas.csv

clear all;
close all;

% Add path to exploration experiment functions
addpath('exploration');

% Participant information
SubID = input('Enter participant ID (e.g., TS263): ', 's');

% Define arena assignments
% Practice arenas (outside magnet) - different from fMRI arenas
practice_arenas = {'garden', 'beach', 'village', 'ranch', 'zoo', 'school'};

% fMRI arenas (inside magnet) - different from practice arenas
fmri_arenas = {'hospital', 'bookstore', 'gym', 'museum', 'airport', 'market'};

fprintf('\n=== ARENA ASSIGNMENTS ===\n');
fprintf('Practice Arenas: %s\n', strjoin(practice_arenas, ', '));
fprintf('fMRI Arenas: %s\n', strjoin(fmri_arenas, ', '));

% Practice sessions (outside magnet)
fprintf('\n=== PRACTICE SESSIONS (Outside Magnet) ===\n');

% Practice snake game
fprintf('\n--- Snake Practice ---\n');
run_snake_game('practice', SubID, 1, 1, 1);

% Practice multi-arena (using practice arenas)
fprintf('\n--- Multi-Arena Practice ---\n');

% Run practice conditions with simplified function calls
practice_conditions = {'full', 'limited', 'none'};

for j = 1:length(practice_conditions)
    visibility = practice_conditions{j};
    
    fprintf('\n--- Practice Condition %d: %s visibility ---\n', j, visibility);
    
    % Run the condition (instructions shown once, then assigned arenas)
    run_multi_arena('practice', SubID, j, j, length(practice_conditions), visibility);
end

% Show thank you screen after all practice trials are complete
fprintf('\n--- Practice Complete ---\n');
fprintf('Showing thank you screen...\n');
% Call the Python script directly for thank you screen
system(sprintf('python multi_arena.py practice --participant %s --arena thank_you --visibility none --num-trials 1', SubID));

% Wait for user confirmation before fMRI sessions
fprintf('\nPractice sessions completed.\n');
fprintf('Press Enter when ready to start fMRI sessions...\n');
pause;

% fMRI runs - Block Design
fprintf('\n=== fMRI SESSIONS (Inside Magnet) ===\n');

% Define the block sequence
total_trials = 6;  % Total number of trials in sequence
trial_counter = 1;

% Block 1: Snake
fprintf('\n--- Block 1: Snake ---\n');
run_snake_game('fmri', SubID, 1, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Block 2: Multi-Arena (Run 1)
fprintf('\n--- Block 2: Multi-Arena (Run 1) ---\n');
fprintf('  Running: 1 test trial (no visibility)\n');
run_multi_arena('fmri', SubID, 1, trial_counter, total_trials, 'none');
trial_counter = trial_counter + 1;

% Block 3: Snake
fprintf('\n--- Block 3: Snake ---\n');
run_snake_game('fmri', SubID, 2, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Block 4: Multi-Arena (Run 2)
fprintf('\n--- Block 4: Multi-Arena (Run 2) ---\n');
fprintf('  Running: 1 test trial (no visibility)\n');
run_multi_arena('fmri', SubID, 2, trial_counter, total_trials, 'none');
trial_counter = trial_counter + 1;

% Block 5: Snake
fprintf('\n--- Block 5: Snake ---\n');
run_snake_game('fmri', SubID, 3, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Block 6: Multi-Arena (Run 3)
fprintf('\n--- Block 6: Multi-Arena (Run 3) ---\n');
fprintf('  Running: 1 test trial (no visibility)\n');
run_multi_arena('fmri', SubID, 3, trial_counter, total_trials, 'none');

fprintf('\n=== EXPERIMENT COMPLETED ===\n');
fprintf('All fMRI sessions completed successfully.\n');
fprintf('Data saved in exploration/results/\n');

% Summary of arena usage
fprintf('\n=== ARENA USAGE SUMMARY ===\n');
fprintf('Practice Conditions:\n');
fprintf('  Full visibility: garden, beach\n');
fprintf('  Limited visibility: village, ranch\n');
fprintf('  No visibility: zoo, school\n');
fprintf('\nfMRI Arenas Used:\n');
fmri_arenas = {'hospital', 'bookstore', 'gym', 'museum', 'airport', 'market'};
for i = 1:3
    fprintf('  %d. %s (Block %d)\n', i, fmri_arenas{i}, 2*i);
end
fprintf('\nRemaining fMRI arenas available: %s\n', strjoin(fmri_arenas(4:end), ', ')); 