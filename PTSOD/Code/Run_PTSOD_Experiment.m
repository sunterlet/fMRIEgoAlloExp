%% PTSOD Experiment Runner
% This script provides a simple interface to run the PTSOD experiment
% for both practice (outside magnet) and fMRI (inside magnet) sessions
% 
% PORTABLE VERSION - Can run from any computer

clear; clc;

% Set up portable paths
try
    [projectRoot, ~, ~, ~] = setupPTSOD();
    fprintf('Running PTSOD from: %s\n\n', projectRoot);
catch ME
    fprintf('Setup Error: %s\n', ME.message);
    fprintf('Please ensure you are running this script from within the PTSOD project directory.\n');
    return;
end

fprintf('=== PTSOD Experiment Runner ===\n\n');

% Get subject information
SubID = input('Enter Subject ID (e.g., TS263): ', 's');
day = input('Enter Day (1 or 2): ');
sessionType = input('Enter Session Type (practice or fMRI): ', 's');

% Validate inputs
if ~ismember(day, [1, 2])
    error('Day must be 1 or 2');
end

if ~ismember(sessionType, {'practice', 'fMRI'})
    error('Session type must be "practice" or "fMRI"');
end

fprintf('\n=== Session Summary ===\n');
fprintf('Subject ID: %s\n', SubID);
fprintf('Day: %d\n', day);
fprintf('Session Type: %s\n', sessionType);

if strcmp(sessionType, 'practice')
    fprintf('\nThis will run the PRACTICE session (outside magnet):\n');
    fprintf('- All 3 examples (2 no-memory, 1 memory)\n');
    fprintf('- No fixation crosses\n');
    fprintf('- Full instructions\n');
else
    fprintf('\nThis will run the fMRI session (inside magnet):\n');
    fprintf('- 1 no-memory example\n');
    fprintf('- All test trials for Day %d\n', day);
    fprintf('- Fixation crosses included\n');
    fprintf('- Brief instructions only\n');
end

% Confirm before starting
confirm = input('\nProceed with experiment? (y/n): ', 's');
if ~strcmpi(confirm, 'y')
    fprintf('Experiment cancelled.\n');
    return;
end

fprintf('\nStarting experiment...\n');
fprintf('Press E key at any time to exit early.\n\n');

% Run the experiment
try
    [dataTable, filename] = PTSODfunc_SplitDays_fMRI_New(SubID, day, sessionType);
    
    % Check if the experiment actually completed or exited early
    if ~isempty(filename)
        fprintf('\n=== Experiment Completed ===\n');
        fprintf('Data saved to: %s\n', filename);
        fprintf('Number of trials completed: %d\n', height(dataTable));
    else
        fprintf('\n=== Experiment Exited Early ===\n');
        fprintf('Partial data was saved to the results folder.\n');
    end
    
catch ME
    fprintf('\n=== Error Occurred ===\n');
    fprintf('Error: %s\n', ME.message);
    fprintf('Check the Results folder for any partial data.\n');
end 