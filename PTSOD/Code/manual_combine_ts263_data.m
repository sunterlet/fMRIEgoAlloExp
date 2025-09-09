function manual_combine_ts263_data()
%% MANUAL_COMBINE_TS263_DATA
% This function manually combines the existing TS263 trial files that weren't
% automatically combined by combinePartialData.m
%
% Usage: manual_combine_ts263_data()

fprintf('=== Manual TS263 Data Combination ===\n\n');

% Get the centralized results directory
centralized_results_dir = getenv('CENTRALIZED_RESULTS_DIR');
if isempty(centralized_results_dir) || ~exist(centralized_results_dir, 'dir')
    fprintf('❌ CENTRALIZED_RESULTS_DIR not set or directory not found.\n');
    fprintf('Please run fmri_sessions1.m first to set up the environment.\n');
    return;
end

% Define the TS263 subfolder path
ts263_path = fullfile(centralized_results_dir, 'TS263');
if ~exist(ts263_path, 'dir')
    fprintf('❌ TS263 directory not found at: %s\n', ts263_path);
    return;
end

fprintf('Found TS263 directory: %s\n', ts263_path);

% Look for fMRI trial files
fprintf('\nSearching for fMRI trial files...\n');
trial_files = dir(fullfile(ts263_path, 'TS263_PTSOD_run1_fMRI_trial*.mat'));

if isempty(trial_files)
    fprintf('❌ No fMRI trial files found.\n');
    return;
end

fprintf('Found %d trial files:\n', length(trial_files));
for i = 1:length(trial_files)
    fprintf('  %s\n', trial_files(i).name);
end

% Initialize combined data
combinedData = {};
overallTime = 0; % We don't have this info, so set to 0

fprintf('\nLoading and combining trial data...\n');

% Load each trial file and extract data
for i = 1:length(trial_files)
    trialFile = fullfile(ts263_path, trial_files(i).name);
    try
        loadedData = load(trialFile);
        
        if isfield(loadedData, 'trialData')
            % Extract the trial data
            trialRow = loadedData.trialData;
            
            % Parse arena name to get numObjects and level
            arenaName = trialRow{1};
            numbers = regexp(arenaName, '\d+', 'match');
            numbers = cellfun(@str2double, numbers);
            num_objects = numbers(1);
            if length(numbers) == 1
                level = 0;
            else
                level = numbers(2);
            end
            
            % Extract numeric values from cells
            angle = trialRow{3};
            relDist = trialRow{4};
            correctAngle = trialRow{5};
            correctRelDist = trialRow{6};
            errorAngle = trialRow{7};
            errorRelDist = trialRow{8};
            reactionTime = trialRow{9};
            skiptime = trialRow{10};
            order = trialRow{11};
            xMouse = trialRow{12};
            yMouse = trialRow{13};
            
            % If any values are cell arrays, extract the numeric value
            if iscell(angle), angle = angle{1}; end
            if iscell(relDist), relDist = relDist{1}; end
            if iscell(correctAngle), correctAngle = correctAngle{1}; end
            if iscell(correctRelDist), correctRelDist = correctRelDist{1}; end
            if iscell(errorAngle), errorAngle = errorAngle{1}; end
            if iscell(errorRelDist), errorRelDist = errorRelDist{1}; end
            if iscell(reactionTime), reactionTime = reactionTime{1}; end
            if iscell(skiptime), skiptime = skiptime{1}; end
            if iscell(order), order = order{1}; end
            if iscell(xMouse), xMouse = xMouse{1}; end
            if iscell(yMouse), yMouse = yMouse{1}; end
            
            % Create row data
            rowData = {arenaName, num_objects, level, trialRow{2}, angle, relDist, correctAngle, correctRelDist, errorAngle, errorRelDist, reactionTime, skiptime, overallTime, order, xMouse, yMouse};
            combinedData = [combinedData; rowData];
            
            fprintf('  ✓ Loaded trial %d: %s\n', i, arenaName);
        else
            fprintf('  ⚠ Trial %d: No trialData field found\n', i);
        end
    catch ME
        fprintf('  ❌ Error loading trial %d: %s\n', i, ME.message);
    end
end

if isempty(combinedData)
    fprintf('\n❌ No valid trial data found to combine.\n');
    return;
end

% Create final data table
headers = {'arena','numObjects', 'level', 'memory', 'angle', 'relDist', 'correctAngle', 'correctRelDist', 'errorAngle', 'errorRelDist', 'reactionTime', 'skiptime', 'overallTime', 'order','xMouse','yMouse'};
dataTable = cell2table(combinedData, 'VariableNames', headers);

% Save combined data
filename = fullfile(ts263_path, 'TS263_PTSOD_run1_fMRI.mat');
save(filename, 'dataTable');
fprintf('\n✅ Combined data saved to: %s\n', filename);
fprintf('Data table contains %d trials\n', height(dataTable));

% Ask user if they want to delete the individual trial files
fprintf('\nIndividual trial files can now be safely deleted.\n');
response = input('Do you want to delete the individual trial files? (y/n): ', 's');

if strcmpi(response, 'y') || strcmpi(response, 'yes')
    fprintf('\nDeleting individual trial files...\n');
    deleted_count = 0;
    
    for i = 1:length(trial_files)
        try
            delete(fullfile(ts263_path, trial_files(i).name));
            fprintf('  Deleted: %s\n', trial_files(i).name);
            deleted_count = deleted_count + 1;
        catch ME
            fprintf('  Error deleting %s: %s\n', trial_files(i).name, ME.message);
        end
    end
    
    fprintf('\n✅ Successfully deleted %d out of %d trial files.\n', deleted_count, length(trial_files));
    fprintf('Data combination and cleanup complete!\n');
else
    fprintf('\nIndividual trial files were not deleted.\n');
    fprintf('You can delete them manually later if needed.\n');
end

fprintf('\n=== Manual Combination Complete ===\n');

end
