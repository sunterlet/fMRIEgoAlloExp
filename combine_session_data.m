function combine_session_data(participant_id)
%% COMBINE SESSION DATA
% This function combines all trial data into single files per run type
% Run this manually after the session is complete or call from fmri_session.m
%
% Input:
%   participant_id - String containing the participant ID (e.g., 'test')
%
% Output:
%   None - Creates combined CSV files in the Results directory

fprintf('\n=== COMBINING SESSION DATA ===\n');
fprintf('Participant: %s\n', participant_id);

% Get centralized results directory
centralized_results_dir = '/Volumes/ramot/sunt/Navigation/fMRI/Results';
subid_dir = fullfile(centralized_results_dir, participant_id, 'fMRI', 'Behavior', 'raw');
output_dir = fullfile(centralized_results_dir, participant_id, 'fMRI', 'Behavior');

if ~exist(subid_dir, 'dir')
    fprintf('Error: Participant directory not found: %s\n', subid_dir);
    return;
end

fprintf('Reading from directory: %s\n', subid_dir);
fprintf('Saving combined files to: %s\n', output_dir);

% Define run types and their patterns
run_types = {
    'OT', 'OT', 'One Target Run';
    'MT', 'MT*', 'Multi Target Run'
};

% Define trial types for discrete data grouping
trial_types = {
    'ot', 'ot', 'One Target trials';
    'snake', 'snake', 'Snake trials';
    'mt', 'mt', 'Multi Target trials'
};

% Process regular run types
for run_idx = 1:size(run_types, 1)
    run_code = run_types{run_idx, 1};
    run_pattern = run_types{run_idx, 2};
    run_name = run_types{run_idx, 3};
    
    fprintf('\n--- Processing %s ---\n', run_name);
    
    % Use more flexible pattern matching to catch all files
    % For OT: match {participant_id}_OT_*continuous*.csv
    % For MT: match {participant_id}_MT*_*continuous*.csv (handles MT, MT1, MT2, etc.)
    if strcmp(run_code, 'OT')
        continuous_pattern = sprintf('%s_OT_*continuous*.csv', participant_id);
        discrete_pattern = sprintf('%s_OT_*discrete*.csv', participant_id);
    else % MT
        % Match both MT and MT{number} patterns
        continuous_pattern = sprintf('%s_MT*continuous*.csv', participant_id);
        discrete_pattern = sprintf('%s_MT*discrete*.csv', participant_id);
    end
    
    continuous_files = dir(fullfile(subid_dir, continuous_pattern));
    discrete_files = dir(fullfile(subid_dir, discrete_pattern));
    
    fprintf('  Pattern used: %s\n', continuous_pattern);
    if ~isempty(continuous_files)
        fprintf('  Found %d continuous files matching pattern\n', length(continuous_files));
        [~, sort_idx] = sort([continuous_files.datenum]);
        continuous_files = continuous_files(sort_idx);
        % List all found files for debugging
        for f_idx = 1:length(continuous_files)
            fprintf('    - %s\n', continuous_files(f_idx).name);
        end
    else
        fprintf('  No continuous files found matching pattern: %s\n', continuous_pattern);
    end
    
    if ~isempty(discrete_files)
        [~, sort_idx] = sort([discrete_files.datenum]);
        discrete_files = discrete_files(sort_idx);
    end
    
    if isempty(continuous_files) && isempty(discrete_files)
        fprintf('  No files found for %s.\n', run_name);
        continue;
    end
    
    continuous_run_ids = cell(length(continuous_files), 1);
    for file_idx = 1:length(continuous_files)
        continuous_run_ids{file_idx} = extract_run_identifier(continuous_files(file_idx).name, participant_id, run_code);
    end
    
    discrete_run_ids = cell(length(discrete_files), 1);
    for file_idx = 1:length(discrete_files)
        discrete_run_ids{file_idx} = extract_run_identifier(discrete_files(file_idx).name, participant_id, run_code);
    end
    
    all_run_ids = [continuous_run_ids; discrete_run_ids];
    all_run_ids = all_run_ids(~cellfun(@isempty, all_run_ids));
    all_run_ids = unique(all_run_ids);
    
    for run_id_idx = 1:length(all_run_ids)
        run_identifier = all_run_ids{run_id_idx};
        fprintf('  Combining data for run %s...\n', run_identifier);
        
        % Combine continuous files for this run identifier
        continuous_indices = strcmp(continuous_run_ids, run_identifier);
        if any(continuous_indices)
            matching_continuous = continuous_files(continuous_indices);
            fprintf('    Found %d continuous files\n', length(matching_continuous));
            
            % Check for duplicate filenames (shouldn't happen, but safety check)
            file_names = {matching_continuous.name};
            [unique_names, unique_idx] = unique(file_names, 'stable');
            if length(unique_names) < length(file_names)
                fprintf('    Warning: Found duplicate filenames, using only unique files\n');
                matching_continuous = matching_continuous(unique_idx);
            end
            
            combined_continuous = [];
            
            for file_idx = 1:length(matching_continuous)
                file_path = fullfile(matching_continuous(file_idx).folder, matching_continuous(file_idx).name);
                try
                    % Read CSV file
                    % Use 'TreatAsEmpty' to handle empty cells properly and prevent row duplication
                    data = readtable(file_path, 'TreatAsEmpty', {''});
                    
                    % Extract trial type from filename and add as column
                    trial_type = extract_trial_type(matching_continuous(file_idx).name);
                    
                    % Remove existing trial_type column if it exists (to avoid conflicts with empty/mixed values)
                    % Use compatible method that works across MATLAB versions
                    if ismember('trial_type', data.Properties.VariableNames)
                        % Create new table without trial_type column
                        var_names = data.Properties.VariableNames;
                        var_names(strcmp(var_names, 'trial_type')) = [];
                        data = data(:, var_names);
                    end
                    
                    % Add trial_type column with consistent values
                    data.trial_type = repmat({trial_type}, height(data), 1);
                    
                    % Ensure all required columns exist (handle unified header structure)
                    % Add missing columns with appropriate empty values
                    required_columns = {'RealTime', 'trial_time', 'trial', 'trial_type', 'RoundName', 'condition_type', ...
                        'visibility', 'phase', 'event', 'x', 'y', 'rotation_angle', 'score', 'target_x', 'target_y'};
                    for col_idx = 1:length(required_columns)
                        col_name = required_columns{col_idx};
                        if ~ismember(col_name, data.Properties.VariableNames)
                            % Add missing column with appropriate empty values
                            % Use numeric NaN for numeric columns, empty string for text columns
                            if ismember(col_name, {'trial_time', 'x', 'y', 'rotation_angle', 'score', 'target_x', 'target_y'})
                                data.(col_name) = nan(height(data), 1);
                            else
                                data.(col_name) = repmat({''}, height(data), 1);
                            end
                        end
                    end
                    
                    % Normalize column types to prevent concatenation errors
                    % Convert text columns to cell arrays and numeric columns to numeric arrays
                    % Note: 'trial' can be numeric or text depending on the file, so handle both cases
                    text_columns = {'RealTime', 'trial_type', 'RoundName', 'condition_type', ...
                        'visibility', 'phase', 'event'};
                    numeric_columns = {'trial_time', 'x', 'y', 'rotation_angle', 'score', 'target_x', 'target_y'};
                    flexible_columns = {'trial'};  % Can be numeric or text - convert to cell for consistency
                    
                    % Convert text columns to cell arrays
                    for col_idx = 1:length(text_columns)
                        col_name = text_columns{col_idx};
                        if ismember(col_name, data.Properties.VariableNames)
                            % Convert to cell array if not already
                            if ~iscell(data.(col_name))
                                if isnumeric(data.(col_name))
                                    data.(col_name) = cellstr(string(data.(col_name)));
                                elseif isstring(data.(col_name))
                                    data.(col_name) = cellstr(data.(col_name));
                                elseif ischar(data.(col_name))
                                    data.(col_name) = cellstr(data.(col_name));
                                end
                            end
                        end
                    end
                    
                    % Convert flexible columns (like 'trial') to cell arrays for consistency
                    for col_idx = 1:length(flexible_columns)
                        col_name = flexible_columns{col_idx};
                        if ismember(col_name, data.Properties.VariableNames)
                            % Always convert to cell array for consistency
                            if ~iscell(data.(col_name))
                                if isnumeric(data.(col_name))
                                    data.(col_name) = cellstr(string(data.(col_name)));
                                elseif isstring(data.(col_name))
                                    data.(col_name) = cellstr(data.(col_name));
                                elseif ischar(data.(col_name))
                                    data.(col_name) = cellstr(data.(col_name));
                                end
                            end
                        end
                    end
                    
                    for col_idx = 1:length(numeric_columns)
                        col_name = numeric_columns{col_idx};
                        if ismember(col_name, data.Properties.VariableNames)
                            % Convert to numeric array if not already
                            if iscell(data.(col_name))
                                % Convert cell array to numeric, handling empty cells and non-numeric values
                                numeric_data = nan(height(data), 1);
                                for row_idx = 1:height(data)
                                    cell_val = data.(col_name){row_idx};
                                    if ~isempty(cell_val)
                                        if isnumeric(cell_val)
                                            numeric_data(row_idx) = cell_val;
                                        elseif ischar(cell_val) || isstring(cell_val)
                                            numeric_data(row_idx) = str2double(cell_val);
                                        end
                                    end
                                end
                                data.(col_name) = numeric_data;
                            elseif isstring(data.(col_name))
                                % Convert string array to numeric
                                numeric_data = nan(height(data), 1);
                                for row_idx = 1:height(data)
                                    str_val = data.(col_name)(row_idx);
                                    if ~isempty(str_val) && str_val ~= ""
                                        numeric_data(row_idx) = str2double(str_val);
                                    end
                                end
                                data.(col_name) = numeric_data;
                            elseif ischar(data.(col_name))
                                % Convert char array to numeric
                                data.(col_name) = str2double(data.(col_name));
                            end
                        end
                    end
                    
                    % If this is the first file, initialize combined_continuous with this data structure
                    if isempty(combined_continuous)
                        combined_continuous = data;
                    else
                        % Normalize existing combined_continuous to match data types
                        % Convert text columns to cell arrays
                        for col_idx = 1:length(text_columns)
                            col_name = text_columns{col_idx};
                            if ismember(col_name, combined_continuous.Properties.VariableNames)
                                if ~iscell(combined_continuous.(col_name))
                                    if isnumeric(combined_continuous.(col_name))
                                        combined_continuous.(col_name) = cellstr(string(combined_continuous.(col_name)));
                                    elseif isstring(combined_continuous.(col_name))
                                        combined_continuous.(col_name) = cellstr(combined_continuous.(col_name));
                                    elseif ischar(combined_continuous.(col_name))
                                        combined_continuous.(col_name) = cellstr(combined_continuous.(col_name));
                                    end
                                end
                            end
                        end
                        
                        % Convert flexible columns to cell arrays
                        for col_idx = 1:length(flexible_columns)
                            col_name = flexible_columns{col_idx};
                            if ismember(col_name, combined_continuous.Properties.VariableNames)
                                if ~iscell(combined_continuous.(col_name))
                                    if isnumeric(combined_continuous.(col_name))
                                        combined_continuous.(col_name) = cellstr(string(combined_continuous.(col_name)));
                                    elseif isstring(combined_continuous.(col_name))
                                        combined_continuous.(col_name) = cellstr(combined_continuous.(col_name));
                                    elseif ischar(combined_continuous.(col_name))
                                        combined_continuous.(col_name) = cellstr(combined_continuous.(col_name));
                                    end
                                end
                            end
                        end
                        for col_idx = 1:length(numeric_columns)
                            col_name = numeric_columns{col_idx};
                            if ismember(col_name, combined_continuous.Properties.VariableNames)
                                if iscell(combined_continuous.(col_name))
                                    numeric_data = nan(height(combined_continuous), 1);
                                    for row_idx = 1:height(combined_continuous)
                                        cell_val = combined_continuous.(col_name){row_idx};
                                        if ~isempty(cell_val)
                                            if isnumeric(cell_val)
                                                numeric_data(row_idx) = cell_val;
                                            elseif ischar(cell_val) || isstring(cell_val)
                                                numeric_data(row_idx) = str2double(cell_val);
                                            end
                                        end
                                    end
                                    combined_continuous.(col_name) = numeric_data;
                                elseif isstring(combined_continuous.(col_name))
                                    numeric_data = nan(height(combined_continuous), 1);
                                    for row_idx = 1:height(combined_continuous)
                                        str_val = combined_continuous.(col_name)(row_idx);
                                        if ~isempty(str_val) && str_val ~= ""
                                            numeric_data(row_idx) = str2double(str_val);
                                        end
                                    end
                                    combined_continuous.(col_name) = numeric_data;
                                elseif ischar(combined_continuous.(col_name))
                                    combined_continuous.(col_name) = str2double(combined_continuous.(col_name));
                                end
                            end
                        end
                        % Final check: ensure all common columns have matching types before concatenation
                        common_cols = intersect(combined_continuous.Properties.VariableNames, data.Properties.VariableNames);
                        for col_idx = 1:length(common_cols)
                            col_name = common_cols{col_idx};
                            if ismember(col_name, [text_columns, flexible_columns])
                                % Text/flexible columns should be cell arrays
                                if ~iscell(combined_continuous.(col_name)) && iscell(data.(col_name))
                                    combined_continuous.(col_name) = cellstr(string(combined_continuous.(col_name)));
                                elseif iscell(combined_continuous.(col_name)) && ~iscell(data.(col_name))
                                    if isnumeric(data.(col_name))
                                        data.(col_name) = cellstr(string(data.(col_name)));
                                    else
                                        data.(col_name) = cellstr(data.(col_name));
                                    end
                                end
                            elseif ismember(col_name, numeric_columns)
                                % Numeric columns should be numeric arrays
                                if iscell(combined_continuous.(col_name)) && ~iscell(data.(col_name))
                                    % combined_continuous has cell, data has numeric - convert combined_continuous
                                    numeric_data = nan(height(combined_continuous), 1);
                                    for row_idx = 1:height(combined_continuous)
                                        cell_val = combined_continuous.(col_name){row_idx};
                                        if ~isempty(cell_val)
                                            if isnumeric(cell_val)
                                                numeric_data(row_idx) = cell_val;
                                            elseif ischar(cell_val) || isstring(cell_val)
                                                numeric_data(row_idx) = str2double(cell_val);
                                            end
                                        end
                                    end
                                    combined_continuous.(col_name) = numeric_data;
                                elseif ~iscell(combined_continuous.(col_name)) && iscell(data.(col_name))
                                    % combined_continuous has numeric, data has cell - convert data
                                    numeric_data = nan(height(data), 1);
                                    for row_idx = 1:height(data)
                                        cell_val = data.(col_name){row_idx};
                                        if ~isempty(cell_val)
                                            if isnumeric(cell_val)
                                                numeric_data(row_idx) = cell_val;
                                            elseif ischar(cell_val) || isstring(cell_val)
                                                numeric_data(row_idx) = str2double(cell_val);
                                            end
                                        end
                                    end
                                    data.(col_name) = numeric_data;
                                end
                            end
                        end
                        
                        % Concatenate this file's data to the combined table
                        combined_continuous = [combined_continuous; data];
                    end
                    
                    % Log file addition with row count for debugging
                    fprintf('      Added: %s (%d rows)\n', matching_continuous(file_idx).name, height(data));
                catch ME
                    fprintf('      Error reading %s: %s\n', matching_continuous(file_idx).name, ME.message);
                    fprintf('      Error details: %s\n', getReport(ME, 'extended'));
                end
            end
            
            if ~isempty(combined_continuous)
                % Remove duplicate rows before sorting (safety check)
                % Use all columns to identify duplicates
                [~, unique_idx] = unique(combined_continuous, 'rows', 'stable');
                if length(unique_idx) < height(combined_continuous)
                    num_duplicates = height(combined_continuous) - length(unique_idx);
                    fprintf('    Warning: Found %d duplicate rows, removing them...\n', num_duplicates);
                    combined_continuous = combined_continuous(unique_idx, :);
                end
                
                % Sort by RealTime to ensure chronological order across all trials
                if ismember('RealTime', combined_continuous.Properties.VariableNames)
                    combined_continuous = sortrows(combined_continuous, 'RealTime');
                elseif ismember('trial_time', combined_continuous.Properties.VariableNames)
                    % Fallback to trial_time if RealTime not available
                    combined_continuous = sortrows(combined_continuous, 'trial_time');
                end
                
                % Ensure unified header structure with columns in consistent order
                unified_columns = {'RealTime', 'trial_time', 'trial', 'trial_type', 'RoundName', 'condition_type', ...
                    'visibility', 'phase', 'event', 'x', 'y', 'rotation_angle', 'score', 'target_x', 'target_y'};
                % Reorder columns to match unified structure
                % First, add any missing unified columns
                for col_idx = 1:length(unified_columns)
                    col_name = unified_columns{col_idx};
                    if ~ismember(col_name, combined_continuous.Properties.VariableNames)
                        if ismember(col_name, {'trial_time', 'x', 'y', 'rotation_angle', 'score', 'target_x', 'target_y'})
                            combined_continuous.(col_name) = nan(height(combined_continuous), 1);
                        else
                            combined_continuous.(col_name) = repmat({''}, height(combined_continuous), 1);
                        end
                    end
                end
                % Reorder: unified columns first, then any other columns
                other_columns = setdiff(combined_continuous.Properties.VariableNames, unified_columns, 'stable');
                combined_continuous = combined_continuous(:, [unified_columns, other_columns]);
                
                output_filename = fullfile(output_dir, sprintf('%s_%s_continuous.csv', participant_id, run_identifier));
                writetable(combined_continuous, output_filename);
                fprintf('    Saved combined continuous: %s (%d rows from %d files)\n', ...
                    output_filename, height(combined_continuous), length(matching_continuous));
            end
        end
        
        % Combine discrete files by trial type for this run identifier
        for trial_idx = 1:size(trial_types, 1)
            trial_code = trial_types{trial_idx, 1};
            trial_pattern = trial_types{trial_idx, 2};
            trial_name = trial_types{trial_idx, 3};
            
            discrete_trial_pattern = sprintf('%s_%s_%s*discrete*.csv', participant_id, run_pattern, trial_pattern);
            discrete_trial_files = dir(fullfile(subid_dir, discrete_trial_pattern));
            
            if isempty(discrete_trial_files)
                continue;
            end
            
            [~, sort_idx] = sort([discrete_trial_files.datenum]);
            discrete_trial_files = discrete_trial_files(sort_idx);
            
            discrete_trial_run_ids = cell(length(discrete_trial_files), 1);
            for file_idx = 1:length(discrete_trial_files)
                discrete_trial_run_ids{file_idx} = extract_run_identifier(discrete_trial_files(file_idx).name, participant_id, run_code);
            end
            
            discrete_indices = strcmp(discrete_trial_run_ids, run_identifier);
            if any(discrete_indices)
                matching_discrete = discrete_trial_files(discrete_indices);
                fprintf('    [%s - %s] Found %d discrete files\n', run_identifier, trial_name, length(matching_discrete));
                
                % Check for duplicate filenames (shouldn't happen, but safety check)
                file_names = {matching_discrete.name};
                [unique_names, unique_idx] = unique(file_names, 'stable');
                if length(unique_names) < length(file_names)
                    fprintf('    Warning: Found duplicate filenames, using only unique files\n');
                    matching_discrete = matching_discrete(unique_idx);
                end
                
                combined_discrete = [];
                processed_files = {};  % Track processed file paths to avoid duplicates
                
                for file_idx = 1:length(matching_discrete)
                    file_path = fullfile(matching_discrete(file_idx).folder, matching_discrete(file_idx).name);
                    
                    % Skip if this file was already processed
                    if ismember(file_path, processed_files)
                        fprintf('      Skipping duplicate file: %s\n', matching_discrete(file_idx).name);
                        continue;
                    end
                    processed_files{end+1} = file_path;
                    
                    try
                        % Read CSV file
                        data = readtable(file_path, 'TreatAsEmpty', {''});
                        combined_discrete = [combined_discrete; data];
                        fprintf('      Added: %s (%d rows)\n', matching_discrete(file_idx).name, height(data));
                    catch ME
                        fprintf('      Error reading %s: %s\n', matching_discrete(file_idx).name, ME.message);
                    end
                end
                
                if ~isempty(combined_discrete)
                    % Remove duplicate rows before saving (safety check)
                    % Convert to string representation for more reliable duplicate detection
                    original_height = height(combined_discrete);
                    [~, unique_idx] = unique(combined_discrete, 'rows', 'stable');
                    if length(unique_idx) < original_height
                        num_duplicates = original_height - length(unique_idx);
                        fprintf('    Warning: Found %d duplicate rows, removing them...\n', num_duplicates);
                        combined_discrete = combined_discrete(unique_idx, :);
                    end
                    
                    output_filename = fullfile(output_dir, sprintf('%s_%s_%s_discrete.csv', participant_id, run_identifier, trial_code));
                    writetable(combined_discrete, output_filename);
                    fprintf('    [%s - %s] Saved combined discrete: %s (%d rows from %d files)\n', ...
                        run_identifier, trial_name, output_filename, height(combined_discrete), length(matching_discrete));
                end
            end
        end
    end
end

fprintf('\n=== DATA COMBINATION COMPLETE ===\n');
fprintf('All trial data has been combined into single files per run.\n');
fprintf('Continuous logs from all trial types (ot, snake, mt) have been combined.\n');
fprintf('Raw individual trial files remain in their original location.\n');
fprintf('\nNote: Combined continuous files use unified header structure:\n');
fprintf('  RealTime, trial_time, trial, trial_type, RoundName, condition_type, visibility,\n');
fprintf('  phase, event, x, y, rotation_angle, score, target_x, target_y\n');
fprintf('  (trial_type: OT, MT, or SNAKE)\n');

end

function run_identifier = extract_run_identifier(file_name, participant_id, run_code)
% Helper to extract run identifier (e.g., MT1, OT) from filename.
% Handles multiple patterns:
%   - {participant_id}_OT_ot{trial}_continuous.csv -> OT
%   - {participant_id}_OT_snake{trial}_continuous.csv -> OT
%   - {participant_id}_MT{number}_mt{trial}_continuous.csv -> MT{number}
%   - {participant_id}_MT{number}_snake{trial}_continuous.csv -> MT{number}
%   - {participant_id}_MT_mt{trial}_continuous.csv -> MT
%   - {participant_id}_MT_snake{trial}_continuous.csv -> MT
% Falls back to the base run_code if no numeric suffix is present.

% Pattern 1: Match {participant_id}_{run_code}{number}_... (e.g., MT1, MT2)
pattern1 = sprintf('^%s_(%s\\d+)_', participant_id, run_code);
tokens1 = regexp(file_name, pattern1, 'tokens', 'once');

if ~isempty(tokens1) && ~isempty(tokens1{1})
    run_identifier = tokens1{1};
    return;
end

% Pattern 2: Match {participant_id}_{run_code}_... (e.g., OT, MT without number)
pattern2 = sprintf('^%s_(%s)_', participant_id, run_code);
tokens2 = regexp(file_name, pattern2, 'tokens', 'once');

if ~isempty(tokens2) && ~isempty(tokens2{1})
    run_identifier = tokens2{1};
    return;
end

% Fallback: return base run_code
run_identifier = run_code;
end

function trial_type = extract_trial_type(file_name)
% Helper to extract trial type (OT, MT, or SNAKE) from filename.
% Patterns:
%   - {participant_id}_OT_ot{trial}_continuous.csv -> OT
%   - {participant_id}_OT_snake{trial}_continuous.csv -> SNAKE
%   - {participant_id}_MT{number}_mt{trial}_continuous.csv -> MT
%   - {participant_id}_MT{number}_snake{trial}_continuous.csv -> SNAKE
%   - {participant_id}_MT_mt{trial}_continuous.csv -> MT
%   - {participant_id}_MT_snake{trial}_continuous.csv -> SNAKE

% Check for snake trials first (most specific)
if contains(file_name, '_snake')
    trial_type = 'SNAKE';
    return;
end

% Check for OT trials (one target)
if contains(file_name, '_ot') || contains(file_name, '_OT_ot')
    trial_type = 'OT';
    return;
end

% Check for MT trials (multi target)
if contains(file_name, '_mt') || contains(file_name, '_MT_mt')
    trial_type = 'MT';
    return;
end

% Fallback: try to infer from run context
if contains(file_name, '_OT_')
    trial_type = 'OT';
elseif contains(file_name, '_MT')
    trial_type = 'MT';
else
    % Default fallback
    trial_type = 'UNKNOWN';
end
end