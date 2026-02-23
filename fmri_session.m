%% fMRI Sessions - Egocentric Allocentric Translation fMRI Experiment
% This file runs all fMRI sessions inside the magnet

% Sequence Order
    
    % Shimming and setup + snake practice 

    % Rest X 2
    
    %  8 trial PTSOD
    
    % One target block design (6 snake_vection + 6 one_target_vection, 3D first-person)
        % Snake vection
        % One target vection
        % Snake vection ... 
        
    % Movie 1 - The Shinning
    
    % Full arena block desing (6 snake 6 full arena)

        % Snake
        % Full arena
        % Snake ... 

    %  8 trial PTSOD
    
    % Movie 2 - Mission Impossible 
    
    % Anatomy


%% Setup Environment
sca; close all; clc; clear; 
commandwindow

%% ========== EXPERIMENT CONFIGURATION - CHANGE THESE SETTINGS ==========
% Participant Information
SubID = 'test';          

% Scanning Mode
scanning = false;         % true = fMRI scanning mode | false = testing mode
com = 'com4';            % Serial port for scanner trigger
TR = 2.01;               % TR in seconds
%% ======================================================================

% Fix random number generator to prevent conflicts with Psychtoolbox
% This resolves the "legacy generator" error when using rng('shuffle')
fprintf('Initializing random number generator...\n');
try
    rng('default');  % Reset to default modern generator
    rng('shuffle');  % Seed with current time
    fprintf('✓ Random number generator initialized successfully\n');
catch ME
    fprintf('Warning: Could not initialize random number generator: %s\n', ME.message);
    fprintf('This may cause issues with trial randomization\n');
end

% Screen Selection - Hardcoded for consistency with Python
% MATLAB/Psychtoolbox uses screen 2, Python uses screen 1
selectedScreen = 2; %select_screen(); %2;

%% Setup Centralized Results Directory
fprintf('\n=== Setting up Centralized Results Directory ===\n');

% Create centralized results directory
centralized_results_dir = fullfile(pwd, 'Results');
if ~exist(centralized_results_dir, 'dir')
    mkdir(centralized_results_dir);
    fprintf('✓ Created centralized Results directory: %s\n', centralized_results_dir);
else
    fprintf('✓ Centralized Results directory already exists: %s\n', centralized_results_dir);
end

% Set environment variable for Python scripts to use centralized results directory
setenv('CENTRALIZED_RESULTS_DIR', centralized_results_dir);
fprintf('✓ Set CENTRALIZED_RESULTS_DIR environment variable\n');

% Create SubID subfolder in Results directory
subid_dir = fullfile(centralized_results_dir, SubID);
if ~exist(subid_dir, 'dir')
    mkdir(subid_dir);
    fprintf('✓ Created SubID subfolder: %s\n', subid_dir);
else
    fprintf('✓ SubID subfolder already exists: %s\n', subid_dir);
end

%% Display Configuration Summary
fprintf('\n=== Trigger Configuration ===\n');
fprintf('Subject ID: %s\n', SubID);
fprintf('Scanning mode: %s\n', mat2str(scanning));
if ~scanning
    fprintf('TESTING MODE: No trigger handling (press any key to start blocks)\n');
end
fprintf('Serial port: %s\n', com);
fprintf('TR: %.2f seconds\n', TR);

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

% Add exploration_trigger directory to path (run_snake_game for shimming, etc.)
explorationPath = fullfile(pwd, 'exploration_trigger');
if exist(explorationPath, 'dir')
    addpath(explorationPath);
    fprintf('✓ Exploration trigger added to path: %s\n', explorationPath);
else
    fprintf('⚠ Exploration trigger directory not found at: %s\n', explorationPath);
end

% Add exploration_trigger_vection first in path (primary vection tasks - one_target_run, full_arena_run)
explorationVectionPath = fullfile(pwd, 'exploration_trigger_vection');
if exist(explorationVectionPath, 'dir')
    addpath(explorationVectionPath, '-begin');  % Prepend so vection run scripts take precedence
    fprintf('✓ Exploration vection experiment added to path: %s\n', explorationVectionPath);
else
    fprintf('⚠ Exploration vection directory not found at: %s\n', explorationVectionPath);
end

% Add trigger_manager function to path
triggerManagerPath = fullfile(pwd, 'exploration_trigger');
if exist(triggerManagerPath, 'dir')
    addpath(triggerManagerPath);
    fprintf('✓ Trigger manager added to path: %s\n', triggerManagerPath);
else
    fprintf('⚠ Trigger manager directory not found at: %s\n', triggerManagerPath);
end

% Add run_snake_game function to path
snakeGamePath = fullfile(pwd, 'exploration_trigger');
if exist(snakeGamePath, 'dir')
    addpath(snakeGamePath);
    fprintf('✓ Snake game functions added to path: %s\n', snakeGamePath);
else
    fprintf('⚠ Snake game functions directory not found at: %s\n', snakeGamePath);
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

%% Practice snake
commandwindow
fprintf('\n=== Snake Practice ===\n');
fprintf('Participants will play endless snake game during shimming and setting...\n');
fprintf('The game will run continuously until manually terminated.\n');
fprintf('Press ESC key in the game window to exit when shimming is complete.\n\n');

% Run endless snake game during shimming
try
    % Use the run_snake_game function for consistency
    run_snake_game('shimming', SubID, [], [], [], selectedScreen);
    
    fprintf('✓ snake practice completed successfully!\n');
catch ME
    fprintf('Error in snake practice: %s\n', ME.message);
end

%% PTSOD fMRI Run 1
commandwindow
fprintf('\n=== PTSOD fMRI Run 1 ===\n');
run = 1;

% Ensure random number generator is properly initialized before PTSOD
fprintf('Ensuring random number generator is ready for PTSOD...\n');
try
    rng('default');  % Reset to default modern generator
    rng('shuffle');  % Seed with current time
    fprintf('✓ Random number generator ready for PTSOD\n');
catch ME
    fprintf('Warning: Could not reinitialize random number generator: %s\n', ME.message);
end

% Run fMRI
try
    [dataTable, filename] = PTSODfunc_SplitRuns_fMRI_New(SubID, run, 'fMRI', selectedScreen, scanning, com, TR);
    % Check if the experiment actually completed or exited early
    if ~isempty(filename)
        % Check if filename contains "incomplete" to determine if run ended early
        if contains(filename, 'incomplete')
            fprintf('PTSOD fMRI run 1 exited early, partial data was saved.\n');
            fprintf('Data saved to: %s\n', filename);
        else
            fprintf('PTSOD fMRI run 1 completed successfully!\n');
            fprintf('Data saved to: %s\n', filename);
        end
    else
        fprintf('PTSOD fMRI run 1 exited early, no data was saved.\n');
    end
catch ME
    fprintf('Error in PTSOD fMRI run 1: %s\n', ME.message);
end

%% One Target Run Design (6 snake_vection + 6 one_target_vection)
commandwindow
fprintf('\n=== One Target Run Design (Vection - 3D first-person) ===\n');
fprintf('Note: Trigger waiting is handled by Python scripts for each trial.\n');
fprintf('Starting One Target Run (snake_vection + one_target_vection)...\n');

vection = true;  % Use 3D vection scripts: snake_vection.py, one_target_vection.py
one_target_run(SubID, selectedScreen, scanning, com, TR, vection);

%% Full Arena Run 1 (Vection - 3D first-person: snake_vection + multi_arena_vection)
commandwindow
fprintf('\n--- Full Arena Run 1 (Vection) ---\n');
% Arena assignments (for reference - handled internally by the wrapper)
practice_arenas = {'garden', 'beach', 'village', 'ranch', 'zoo', 'school'};
fmri_arenas = {'hospital', 'library', 'gym', 'museum', 'airport', 'market'};
fprintf('Note: Trigger waiting is handled by Python scripts for each trial.\n');
fprintf('Starting Full Arena Run 1 (snake_vection + multi_arena_vection)...\n');

vection = true;  % Use 3D vection scripts: snake_vection.py, multi_arena_vection.py
full_arena_run(SubID, 1, selectedScreen, scanning, com, TR, vection);

%% Movie 1 - The Shining
commandwindow
fprintf('\n=== Movie 1 - The Shining ===\n');
fprintf('Playing The Shining...\n');

try
    log1 = PlayMovie_Scaled(SubID, 'TheShining.mp4', scanning, selectedScreen);
    % Only print success if not aborted
    if ~isfield(log1, 'aborted') || ~log1.aborted
        fprintf('\n✓ Movie 1 completed successfully!\n');
    end
catch ME
    fprintf('Error playing Movie 1: %s\n', ME.message);
end

%% Full Arena Run 2 (Vection - 3D first-person: snake_vection + multi_arena_vection)
commandwindow
fprintf('\n--- Full Arena Run 2 (Vection) ---\n');
fprintf('Note: Trigger waiting is handled by Python scripts for each trial.\n');
fprintf('Starting Full Arena Run 2 (snake_vection + multi_arena_vection)...\n');

vection = true;  % Use 3D vection scripts: snake_vection.py, multi_arena_vection.py
full_arena_run(SubID, 2, selectedScreen, scanning, com, TR, vection);

%% PTSOD fMRI Run 2
commandwindow
fprintf('\n=== PTSOD fMRI Run 2 ===\n');
run = 2;

% Ensure random number generator is properly initialized before PTSOD
fprintf('Ensuring random number generator is ready for PTSOD...\n');
try
    rng('default');  % Reset to default modern generator
    rng('shuffle');  % Seed with current time
    fprintf('✓ Random number generator ready for PTSOD\n');
catch ME
    fprintf('Warning: Could not reinitialize random number generator: %s\n', ME.message);
end

% Run fMRI
try
    [dataTable, filename] = PTSODfunc_SplitRuns_fMRI_New(SubID, run, 'fMRI', selectedScreen, scanning, com, TR);
    
    % Check if the experiment actually completed or exited early
    if ~isempty(filename)
        fprintf('PTSOD fMRI run 2 completed successfully!\n');
        fprintf('Data saved to: %s\n', filename);
    else
        fprintf('PTSOD fMRI run 2 exited early, partial data was saved.\n');
    end
catch ME
    fprintf('Error in PTSOD fMRI run 2: %s\n', ME.message);
end

%% Movie 2 - Mission Impossible
commandwindow
fprintf('\n=== Movie 2 - Mission Impossible ===\n');
fprintf('Playing Mission Impossible ...\n');

try
    log2 = PlayMovie_Scaled(SubID, 'MissionImpossible.mp4', scanning, selectedScreen);
    % Only print success if not aborted
    if ~isfield(log2, 'aborted') || ~log2.aborted
        fprintf('\n✓ Movie 2 completed successfully!\n');
    end
catch ME
    fprintf('Error playing Movie 2: %s\n', ME.message);
end

%% Close trigger
commandwindow
fprintf('Note: Trigger connections are closed by individual Python scripts.\n');

%% Data Combination
commandwindow
% Call the external combine_session_data function to combine all trial data
% into single files per run type after the session is complete
fprintf('\n=== COMBINING SESSION DATA ===\n');
fprintf('Calling external combine_session_data function...\n');

try
    combine_session_data(SubID);
    fprintf('✓ Data combination completed successfully!\n');
catch ME
    fprintf('Error in data combination: %s\n', ME.message);
    fprintf('You can run combine_session_data manually later.\n');
end

% To run the combination function manually, use:
% combine_session_data('test');  % Replace 'test' with actual participant ID
