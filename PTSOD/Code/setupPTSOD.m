function [projectRoot, resultPath, stimuliPath, instructionsPath] = setupPTSOD()
%% SETUP PTSOD - Portable Setup Function
% This function automatically detects the project root and sets up all
% necessary paths for the PTSOD experiment to run from any computer.
%
% Returns:
%   projectRoot - The root directory of the PTSOD project
%   resultPath - Path to the Results directory
%   stimuliPath - Path to the Stimuli directory
%   instructionsPath - Path to the Instructions directory

% Get the directory of the current function
currentDir = fileparts(mfilename('fullpath'));

% Check if we're already in the PTSOD project structure
if exist(fullfile(currentDir, '..', 'Stimuli'), 'dir')
    % We're in the Code subdirectory of PTSOD
    projectRoot = fullfile(currentDir, '..');
elseif exist(fullfile(currentDir, 'Stimuli'), 'dir')
    % We're in the PTSOD root directory
    projectRoot = currentDir;
else
    % Try to find the project root by looking for key directories
    projectRoot = findProjectRoot(currentDir);
end

% Validate that we found the correct project root
if isempty(projectRoot) || ~exist(fullfile(projectRoot, 'Stimuli'), 'dir')
    error('Could not find PTSOD project root. Please ensure you are running from within the PTSOD project directory.');
end

% Set up all the necessary paths
% Check if centralized results directory is set
centralized_results_dir = getenv('CENTRALIZED_RESULTS_DIR');
if ~isempty(centralized_results_dir) && exist(centralized_results_dir, 'dir')
    % Use centralized results directory
    resultPath = centralized_results_dir;
    fprintf('Using centralized results directory: %s\n', resultPath);
else
    % Fall back to local PTSOD Results directory
    resultPath = fullfile(projectRoot, 'Results');
    fprintf('Using local PTSOD Results directory: %s\n', resultPath);
end

stimuliPath = fullfile(projectRoot, 'Stimuli');
instructionsPath = fullfile(projectRoot, 'Instructions_HE');

% Add the Code directory to the MATLAB path
codePath = fullfile(projectRoot, 'Code');
if ~exist(codePath, 'dir')
    error('Code directory not found at: %s', codePath);
end

% Add to path if not already there
if ~contains(path, codePath)
    addpath(codePath);
end

% Create Results directory if it doesn't exist
if ~exist(resultPath, 'dir')
    mkdir(resultPath);
    fprintf('Created Results directory: %s\n', resultPath);
end

fprintf('PTSOD Setup Complete:\n');
fprintf('  Project Root: %s\n', projectRoot);
fprintf('  Results Path: %s\n', resultPath);
fprintf('  Stimuli Path: %s\n', stimuliPath);
fprintf('  Instructions Path: %s\n', instructionsPath);

end

function projectRoot = findProjectRoot(startDir)
%% Helper function to find the project root by looking for key directories
% Recursively searches upward from startDir to find a directory containing
% both 'Stimuli' and 'Instructions_HE' subdirectories

currentDir = startDir;
maxLevels = 10; % Prevent infinite loops
level = 0;

while level < maxLevels
    % Check if this directory contains the key project directories
    if exist(fullfile(currentDir, 'Stimuli'), 'dir') && ...
       exist(fullfile(currentDir, 'Instructions_HE'), 'dir')
        projectRoot = currentDir;
        return;
    end
    
    % Go up one directory level
    parentDir = fileparts(currentDir);
    if strcmp(parentDir, currentDir)
        % We've reached the root of the filesystem
        break;
    end
    currentDir = parentDir;
    level = level + 1;
end

projectRoot = [];
end 