function [dataTable, filename] = combinePartialData(result_path, SubID, day_or_run, overallTime, sessionType, isComplete)
    % Helper function to combine partial data when exiting early
    % sessionType: 'practice' or 'fMRI' to create proper session-specific filenames
    % isComplete: true if session completed normally, false if exited early (default: false)
    % day_or_run: can be either day number or run number depending on the calling function
    % result_path: should already point to the SubID subfolder in the centralized results directory
    
    if nargin < 6
        isComplete = false;  % Default to incomplete (early exit)
    end
    
    % Use the provided result_path (which should already be the centralized results directory)
    % Create SubID subfolder within the centralized results directory
    save_path = fullfile(result_path, SubID);
    fprintf('Using results directory: %s\n', save_path);
    
    % Ensure the SubID subfolder exists
    if ~exist(save_path, 'dir')
        mkdir(save_path);
        fprintf('Created SubID subfolder: %s\n', save_path);
    end
    
    % Load and combine trial data for the specific session type
    if nargin >= 5 && ~isempty(sessionType)
        if strcmp(sessionType, 'fMRI')
            % For fMRI sessions, look for both old and new trial filename formats
            old_pattern = sprintf('%s_PTSOD_day%d_%s_*.mat', SubID, day_or_run, sessionType);
            new_pattern = sprintf('%s_PTSOD_run%d_fMRI_*.mat', SubID, day_or_run);
            
            % Search for both patterns in the save_path
            old_trial_files = dir(fullfile(save_path, old_pattern));
            new_trial_files = dir(fullfile(save_path, new_pattern));
            
            % Combine both sets of files
            allTrialFiles = [old_trial_files; new_trial_files];
            
            if isComplete
                fprintf('Loading complete %s session data for %s, Run %d\n', sessionType, SubID, day_or_run);
            else
                fprintf('Loading partial %s session data for %s, Run %d\n', sessionType, SubID, day_or_run);
            end
        else
            % For non-fMRI sessions, use the old pattern
            allTrialFiles = dir(fullfile(save_path, sprintf('%s_PTSOD_day%d_%s_*.mat', SubID, day_or_run, sessionType)));
            if isComplete
                fprintf('Loading complete %s session data for %s, Day/Run %d\n', sessionType, SubID, day_or_run);
            else
                fprintf('Loading partial %s session data for %s, Day/Run %d\n', sessionType, SubID, day_or_run);
            end
        end
    else
        % Fallback to old behavior if sessionType not provided
        allTrialFiles = dir(fullfile(save_path, sprintf('%s_PTSOD_day%d_*.mat', SubID, day_or_run)));
        if isComplete
            fprintf('Loading complete data for %s, Day/Run %d (session type not specified)\n', SubID, day_or_run);
        else
            fprintf('Loading partial data for %s, Day/Run %d (session type not specified)\n', SubID, day_or_run);
        end
    end
    
    if isempty(allTrialFiles)
        % No trial files found, create empty table
        dataTable = table();
        filename = '';
        fprintf('PTSOD run %d exited early, partial data was saved.\n', day_or_run);
        return;
    end
    
    % Initialize combined data
    combinedData = {};
    
    % Load each trial file and extract data
    for i = 1:length(allTrialFiles)
        trialFile = fullfile(save_path, allTrialFiles(i).name);
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
        end
    end
    
    % Create final data table
    headers = {'arena','numObjects', 'level', 'memory', 'angle', 'relDist', 'correctAngle', 'correctRelDist', 'errorAngle', 'errorRelDist', 'reactionTime', 'skiptime', 'overallTime', 'order','xMouse','yMouse'};
    
    if ~isempty(combinedData)
        dataTable = cell2table(combinedData, 'VariableNames', headers);
    else
        dataTable = table();
    end
    
    % Save combined data with proper session-specific filename
    if nargin >= 5 && ~isempty(sessionType)
        % Use session-specific filename with new format
        if strcmp(sessionType, 'fMRI')
            % For fMRI sessions, use the new format: SubID_PTSOD_run{run}_fMRI.mat
            if isComplete
                % Complete session - check for existing file and add suffix if needed
                base_filename = sprintf('%s_PTSOD_run%d_fMRI.mat', SubID, day_or_run);
                filename = fullfile(save_path, base_filename);
                suffix = 0;
                while exist(filename, 'file')
                    suffix = suffix + 1;
                    filename = fullfile(save_path, sprintf('%s_PTSOD_run%d_fMRI_%d.mat', SubID, day_or_run, suffix));
                end
                if suffix > 0
                    fprintf('File %s already exists, saving as: %s\n', base_filename, getFilenameFromPath(filename));
                end
            else
                % Incomplete session - add "incomplete" suffix
                suffix = 0;
                filename = fullfile(save_path, sprintf('%s_PTSOD_run%d_fMRI_incomplete.mat', SubID, day_or_run));
                while exist(filename, 'file')
                    suffix = suffix + 1;
                    filename = fullfile(save_path, sprintf('%s_PTSOD_run%d_fMRI_incomplete_%d.mat', SubID, day_or_run, suffix));
                end
            end
        else
            % For practice sessions, keep the old format for compatibility
            if isComplete
                % Complete session - check for existing file and add suffix if needed
                base_filename = sprintf('%s_PTSOD_day%d_%s.mat', SubID, day_or_run, sessionType);
                filename = fullfile(save_path, base_filename);
                suffix = 0;
                while exist(filename, 'file')
                    suffix = suffix + 1;
                    filename = fullfile(save_path, sprintf('%s_PTSOD_day%d_%s_%d.mat', SubID, day_or_run, sessionType, suffix));
                end
                if suffix > 0
                    fprintf('File %s already exists, saving as: %s\n', base_filename, getFilenameFromPath(filename));
                end
            else
                % Incomplete session - add "incomplete" suffix
                suffix = 0;
                filename = fullfile(save_path, sprintf('%s_PTSOD_day%d_%s_incomplete.mat', SubID, day_or_run, sessionType));
                while exist(filename, 'file')
                    suffix = suffix + 1;
                    filename = fullfile(save_path, sprintf('%s_PTSOD_day%d_%s_incomplete_%d.mat', SubID, day_or_run, sessionType, suffix));
                end
            end
        end
    else
        % Fallback to old behavior
        if isComplete
            % Complete session - check for existing file and add suffix if needed
            base_filename = sprintf('%s_PTSOD_day%d.mat', SubID, day_or_run);
            filename = fullfile(save_path, base_filename);
            suffix = 0;
            while exist(filename, 'file')
                suffix = suffix + 1;
                filename = fullfile(save_path, sprintf('%s_PTSOD_day%d_%d.mat', SubID, day_or_run, suffix));
            end
            if suffix > 0
                fprintf('File %s already exists, saving as: %s\n', base_filename, getFilenameFromPath(filename));
            end
        else
            % Incomplete session - add "incomplete" suffix
            suffix = 0;
            filename = fullfile(save_path, sprintf('%s_PTSOD_day%d_incomplete.mat', SubID, day_or_run));
            while exist(filename, 'file')
                suffix = suffix + 1;
                filename = fullfile(save_path, sprintf('%s_PTSOD_day%d_incomplete_%d.mat', SubID, day_or_run, suffix));
            end
        end
    end
    
    % Ensure the save directory exists
    [save_dir, ~, ~] = fileparts(filename);
    if ~exist(save_dir, 'dir')
        mkdir(save_dir);
        fprintf('Created directory: %s\n', save_dir);
    end
    
    save(filename, 'dataTable');
    
    % Clean up individual trial files
    fprintf('Deleting individual trial files...\n');
    for i = 1:length(allTrialFiles)
        delete(fullfile(save_path, allTrialFiles(i).name));
        fprintf('Deleted: %s\n', allTrialFiles(i).name);
    end
    
    if isComplete
        fprintf('Complete session data saved to: %s\n', filename);
    else
        fprintf('Partial session data saved to: %s\n', filename);
    end
end

function filename_only = getFilenameFromPath(full_path)
    % Helper function to extract just the filename from a full path
    [~, name, ext] = fileparts(full_path);
    filename_only = [name, ext];
end 