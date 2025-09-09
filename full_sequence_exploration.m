%% Egocentric Allocentric Translation - fMRI Sequence (PORTABLE VERSION)




%% Setting up enviroment   
      
% Clear the workspace and the screen 
sca;      
 close all;          
 clc; clear;            

% Set up portable PTSOD paths from fMRI directory
try
    % Add PTSOD Code directory to path
    ptsodCodePath = fullfile(pwd, 'PTSOD', 'Code');
    if exist(ptsodCodePath, 'dir')
        addpath(ptsodCodePath);
        fprintf('PTSOD Code added to path: %s\n', ptsodCodePath);
    else
        error('PTSOD Code directory not found at: %s', ptsodCodePath);
    end
    
    % Set up PTSOD paths
    [projectRoot, ~, ~, ~] = setupPTSOD();
    fprintf('PTSOD running from: %s\n', projectRoot);
catch ME
    fprintf('PTSOD Setup Error: %s\n', ME.message);
    fprintf('Please ensure the PTSOD project is in the current directory.\n');
    fprintf('Expected structure: fMRI/PTSOD/Code/\n');
    return;
end

%% Screen Selection
fprintf('\n=== Screen Selection ===\n');

% Get available screens
screens = Screen('Screens');
numScreens = length(screens);

fprintf('Available screens: %s\n', mat2str(screens));
fprintf('Number of screens: %d\n', numScreens);

if numScreens > 1
    fprintf('\nMultiple screens detected. Please choose:\n');
    for i = 1:numScreens
        fprintf('%d. Screen %d', i, screens(i));
        if screens(i) == 0
            fprintf(' (current screen)');
        elseif screens(i) == max(screens)
            fprintf(' (external display)');
        end
        fprintf('\n');
    end
    
    choice = input(sprintf('\nSelect screen number (1-%d): ', numScreens));
    if choice >= 1 && choice <= numScreens
        selectedScreen = screens(choice);
        fprintf('Selected screen: %d\n', selectedScreen);
    else
        fprintf('Invalid choice, using screen 0 (current screen)\n');
        selectedScreen = 0;
    end
else
    fprintf('Only one screen available, using screen 0\n');
    selectedScreen = 0;
end

SubID = 'TS263';
day = 1;

%% PTSOD - PORTABLE VERSION

fprintf('\n=== Starting PTSOD Experiment ===\n');

% Outside of the magnet practice
fprintf('Running practice session...\n');
PTSODfunc_SplitDays_fMRI_New(SubID, day, 'practice', selectedScreen);

%%
% fMRI
fprintf('Running fMRI session...\n');
PTSODfunc_SplitDays_fMRI_New(SubID, day, 'fMRI', selectedScreen);

fprintf('PTSOD Experiment completed.\n');

%% One target block design

fprintf('\n=== Starting One Target Block Design ===\n');

% Add the exploration directory to MATLAB path
addpath('exploration');

% Practice session
run_snake_game('practice', SubID);
run_one_target('practice', SubID);

%%
% fMRI runs

total_trials = 4;  % Total number of trials in sequence
trial_counter = 1;

% Run snake game (trial 1)
run_snake_game('fmri', SubID, 1, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Run one target experiment (trial 2)
run_one_target('fmri', SubID, 1, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Run snake game (trial 3)
run_snake_game('fmri', SubID, 2, trial_counter, total_trials);
trial_counter = trial_counter + 1;

% Run one target experiment (trial 4)
run_one_target('fmri', SubID, 2, trial_counter, total_trials);

%% Full arena block design

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
run_multi_arena('practice', SubID, 1, 1, 1, 'thank_you', 'none', 1);

%% fMRI runs - Block Design
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