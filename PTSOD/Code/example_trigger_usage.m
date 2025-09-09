%% Example: Using PTSOD with Trigger Functionality
% This script demonstrates how to use the updated PTSODfunc_SplitDays_fMRI_New
% function with scanner trigger functionality

clear; clc;

%% Example 1: Practice Session (No Trigger)
fprintf('=== Example 1: Practice Session ===\n');
fprintf('Running practice session without trigger functionality...\n');

% Practice session parameters
SubID = 'TS263';
day = 1;
sessionType = 'practice';
screenNumber = 0;  % Use default screen

% Run practice session (no trigger needed)
try
    [dataTable, filename] = PTSODfunc_SplitDays_fMRI_New(SubID, day, sessionType, screenNumber);
    
    % Check if the experiment actually completed or exited early
    if ~isempty(filename)
        fprintf('Practice session completed successfully!\n');
        fprintf('Data saved to: %s\n', filename);
    else
        fprintf('Practice session exited early, partial data was saved.\n');
    end
catch ME
    fprintf('Error in practice session: %s\n', ME.message);
end

%% Example 2: fMRI Session with Trigger
fprintf('\n=== Example 2: fMRI Session with Trigger ===\n');
fprintf('Running fMRI session with trigger functionality...\n');

% fMRI session parameters
SubID = 'TS263';
day = 1;
sessionType = 'fMRI';
screenNumber = 0;  % Use default screen
scanning = true;   % Enable trigger functionality
com = 'COM1';      % Serial port for trigger
TR = 2;           % TR in seconds

% Run fMRI session with trigger
try
    [dataTable, filename] = PTSODfunc_SplitDays_fMRI_New(SubID, day, sessionType, screenNumber, scanning, com, TR);
    
    % Check if the experiment actually completed or exited early
    if ~isempty(filename)
        fprintf('fMRI session completed successfully!\n');
        fprintf('Data saved to: %s\n', filename);
    else
        fprintf('fMRI session exited early, partial data was saved.\n');
    end
catch ME
    fprintf('Error in fMRI session: %s\n', ME.message);
end

%% Example 3: fMRI Session without Trigger (for testing)
fprintf('\n=== Example 3: fMRI Session without Trigger ===\n');
fprintf('Running fMRI session without trigger (for testing)...\n');

% fMRI session parameters (no trigger)
SubID = 'TS263';
day = 1;
sessionType = 'fMRI';
screenNumber = 0;  % Use default screen
scanning = false;  % Disable trigger functionality
com = 'COM1';      % Serial port (not used when scanning=false)
TR = 2;           % TR in seconds

% Run fMRI session without trigger
try
    [dataTable, filename] = PTSODfunc_SplitDays_fMRI_New(SubID, day, sessionType, screenNumber, scanning, com, TR);
    
    % Check if the experiment actually completed or exited early
    if ~isempty(filename)
        fprintf('fMRI session (no trigger) completed successfully!\n');
        fprintf('Data saved to: %s\n', filename);
    else
        fprintf('fMRI session (no trigger) exited early, partial data was saved.\n');
    end
catch ME
    fprintf('Error in fMRI session (no trigger): %s\n', ME.message);
end

fprintf('\n=== All examples completed ===\n'); 