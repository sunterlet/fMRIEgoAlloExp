function run_multi_arena(mode, participant_id, run_number, trial_number, total_trials, visibility, screen_number)
%RUN_MULTI_ARENA Run multi-arena experiment from MATLAB
%
%   run_multi_arena(mode, participant_id, run_number, trial_number, total_trials, visibility, screen_number)
%
%   Parameters:
%       mode: 'practice' or 'fmri'
%           if mode == 'practice'
%               preassign the arenas to the conditions: 
%               full visibility (training)  - Assigned arenas: garden, beach
%               limited visibility (dark_training) - Assigned arenas: village, ranch
%               none visibility (test) - Assigned arenas: zoo, school
%               
%               show the relevant instruction once, and run the assigned arenas.
%               Each arena will display "זירה 1 מתוך 2" or "זירה 2 מתוך 2" in the intro screen.
%               
%           if mode == 'fmri' 
%               fmri_arenas = {'hospital', 'bookstore', 'gym', 'museum', 'airport', 'market'};
%               run one arena per run with the relevant fMRI features (not in a loop as the snake block should come after) 
%
%       participant_id: Participant initials (e.g., 'TS263')
%       run_number: Run number for fMRI mode (ignored for practice)
%       trial_number: Current trial number in sequence (ignored for practice)
%       total_trials: Total number of trials in sequence (ignored for practice)
%       visibility: 'full', 'limited', or 'none' (visibility mode for practice)
%       screen_number: Screen number to display on (optional, default: None)
%
%   Examples:
%       run_multi_arena('practice', 'TS263', 1, 1, 1, 'full')                    % Practice session (default screen)
%       run_multi_arena('practice', 'TS263', 1, 1, 1, 'full', 0)               % Practice session on screen 0
%       run_multi_arena('fmri', 'TS263', 1, 3, 4, 'none')                      % fMRI run 1, trial 3 of 4 (default screen)
%       run_multi_arena('fmri', 'TS263', 1, 3, 4, 'none', 0)                  % fMRI run 1, trial 3 of 4 on screen 0

    % Get the current directory and navigate to exploration
    current_dir = pwd;
    exploration_dir = fullfile(current_dir, 'exploration');

    if ~exist(exploration_dir, 'dir')
        error('exploration directory not found');
    end

    % Change to exploration directory
    cd(exploration_dir);

    % Function to find Python executable
    function python_cmd = find_python()
        % Try different Python commands
        python_commands = {'python3', 'python', 'py'};
        
        for cmd = python_commands
            [status, ~] = system(sprintf('%s --version', cmd{1}));
            if status == 0
                python_cmd = cmd{1};
                return;
            end
        end
        
        % If still no Python found, provide helpful error
        error(['Python not found! Please install Python 3.8+ from https://www.python.org/downloads/\n' ...
               'Make sure to check "Add Python to PATH" during installation.\n' ...
               'After installation, restart MATLAB and try again.\n' ...
               'Alternatively, you can install Python using: winget install Python.Python.3.11']);
    end
    
    try
        % Find Python executable
        python_cmd = find_python();
        fprintf('Using Python command: %s\n', python_cmd);
        
        % Set default screen number if not provided
        if nargin < 7
            screen_number = [];
        end
        
        if strcmp(mode, 'practice')
            % Practice mode - handle arena assignments internally
            
            % Special case: Show thank you screen
            if strcmp(visibility, 'thank_you')
                fprintf('Showing thank you screen for participant: %s\n', participant_id);
                if nargin < 7 || isempty(screen_number)
                    cmd = sprintf('%s multi_arena.py practice --participant %s --arena thank_you --visibility none --num-trials 1', python_cmd, participant_id);
                else
                    cmd = sprintf('%s multi_arena.py practice --participant %s --arena thank_you --visibility none --num-trials 1 --screen %d', python_cmd, participant_id, screen_number);
                end
                [status, result] = system(cmd);
                if status ~= 0
                    error('Failed to show thank you screen: %s', result);
                end
                return;
            end
            
            fprintf('Running multi_arena practice session for participant: %s, visibility: %s\n', participant_id, visibility);
            
            % Define arena assignments for each visibility condition
            if strcmp(visibility, 'full')
                assigned_arenas = {'garden', 'beach'};
                fprintf('  Full visibility (training) - Assigned arenas: %s\n', strjoin(assigned_arenas, ', '));
            elseif strcmp(visibility, 'limited')
                assigned_arenas = {'village', 'ranch'};
                fprintf('  Limited visibility (dark_training) - Assigned arenas: %s\n', strjoin(assigned_arenas, ', '));
            elseif strcmp(visibility, 'none')
                assigned_arenas = {'zoo', 'school'};
                fprintf('  No visibility (test) - Assigned arenas: %s\n', strjoin(assigned_arenas, ', '));
            else
                error('Invalid visibility mode. Use ''full'', ''limited'', ''none'', or ''thank_you''');
            end
            
            % Show instructions once for this condition
            fprintf('  Showing instructions for %s visibility...\n', visibility);
            if nargin < 7 || isempty(screen_number)
                cmd_instructions = sprintf('%s multi_arena.py practice --participant %s --arena instructions --visibility %s --num-trials 1', python_cmd, participant_id, visibility);
            else
                cmd_instructions = sprintf('%s multi_arena.py practice --participant %s --arena instructions --visibility %s --num-trials 1 --screen %d', python_cmd, participant_id, visibility, screen_number);
            end
            [status, result] = system(cmd_instructions);
            if status ~= 0
                error('Failed to show instructions: %s', result);
            end
            
            % Store arena-specific log files for later combination
            arena_continuous_files = {};
            arena_discrete_files = {};
            
            % Run each assigned arena
            for i = 1:length(assigned_arenas)
                arena_name = assigned_arenas{i};
                fprintf('    Running arena: %s (arena %d of %d)\n', arena_name, i, length(assigned_arenas));
                
                % Set environment variable to use arena-specific filenames (only arena name, no visibility)
                arena_suffix = sprintf('_%s', arena_name);
                setenv('ARENA_LOG_SUFFIX', arena_suffix);
                
                % Construct command for practice mode (1 trial per arena)
                if nargin < 7 || isempty(screen_number)
                    cmd = sprintf('%s multi_arena.py practice --participant %s --arena %s --visibility %s --num-trials 1 --arena-number %d --arenas-per-condition %d', python_cmd, participant_id, arena_name, visibility, i, length(assigned_arenas));
                else
                    cmd = sprintf('%s multi_arena.py practice --participant %s --arena %s --visibility %s --num-trials 1 --arena-number %d --arenas-per-condition %d --screen %d', python_cmd, participant_id, arena_name, visibility, i, length(assigned_arenas), screen_number);
                end
                
                % Run the command
                [status, result] = system(cmd);
                
                if status ~= 0
                    error('Multi-arena practice session failed for arena %s: %s', arena_name, result);
                end
                
                % Store the generated log file names for later combination
                results_dir = fullfile(exploration_dir, 'results');
                arena_continuous_files{i} = fullfile(results_dir, sprintf('%s_multi_arena_practice_continuous_log%s.csv', participant_id, arena_suffix));
                arena_discrete_files{i} = fullfile(results_dir, sprintf('%s_multi_arena_practice_discrete_log%s.csv', participant_id, arena_suffix));
            end
            
            % Combine all arena-specific log files into single files
            fprintf('  Combining log files for %s visibility condition...\n', visibility);
            combine_arena_logs(participant_id, visibility, arena_continuous_files, arena_discrete_files, results_dir);
            
            fprintf('Multi-arena practice session completed successfully.\n');
            
        elseif strcmp(mode, 'fmri')
            % fMRI mode - use predefined fMRI arenas
            fmri_arenas = {'hospital', 'bookstore', 'gym', 'museum', 'airport', 'market'};
            
            if run_number > length(fmri_arenas)
                error('Run number %d exceeds available fMRI arenas (%d)', run_number, length(fmri_arenas));
            end
            
            arena_name = fmri_arenas{run_number};
            fprintf('Running multi_arena fMRI session for participant: %s, run: %d, trial: %d/%d, arena: %s\n', ...
                participant_id, run_number, trial_number, total_trials, arena_name);
            
            % Construct command for fMRI mode without scanning parameter (handled at MATLAB level)
            if nargin < 7 || isempty(screen_number)
                cmd = sprintf('%s multi_arena.py fmri --participant %s --run %d --trial %d --total-trials %d --arena %s --visibility none --num-trials 1 --arena-number 1 --arenas-per-condition 1', ...
                    python_cmd, participant_id, run_number, trial_number, total_trials, arena_name);
            else
                cmd = sprintf('%s multi_arena.py fmri --participant %s --run %d --trial %d --total-trials %d --arena %s --visibility none --num-trials 1 --arena-number 1 --arenas-per-condition 1 --screen %d', ...
                    python_cmd, participant_id, run_number, trial_number, total_trials, arena_name, screen_number);
            end
            
            % Run the command
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Multi-arena fMRI session completed successfully.\n');
            else
                error('Multi-arena fMRI session failed: %s', result);
            end
            
        else
            error('Invalid mode. Use ''practice'' or ''fmri''');
        end
        
    catch ME
        % Return to original directory before re-throwing error
        cd(current_dir);
        rethrow(ME);
    end
    
    % Return to original directory
    cd(current_dir);
end

function combine_arena_logs(participant_id, visibility, continuous_files, discrete_files, results_dir)
    % Combine arena-specific log files into single files
    
    % Combine continuous logs
    combined_continuous = [];
    for i = 1:length(continuous_files)
        if exist(continuous_files{i}, 'file')
            try
                % Read the arena-specific continuous log with UTF-8 encoding
                arena_data = readtable(continuous_files{i}, 'Delimiter', ',', 'TextType', 'string', 'Encoding', 'UTF-8');
                
                % Add RoundName column if it doesn't exist
                if ~ismember('RoundName', arena_data.Properties.VariableNames)
                    % Extract arena name from filename
                    % Filename format: TEST_multi_arena_practice_continuous_log_garden.csv
                    [~, filename] = fileparts(continuous_files{i});
                    parts = split(filename, '_');
                    
                    % Find the arena name - it's the last part after 'log'
                    arena_name = '';
                    for j = 1:length(parts)
                        if strcmp(parts{j}, 'log')
                            if j < length(parts)
                                arena_name = parts{j+1};
                            end
                            break;
                        end
                    end
                    
                    % If we couldn't find it, use the last part as fallback
                    if isempty(arena_name) && ~isempty(parts)
                        arena_name = parts{end};
                    end
                    
                    % Create RoundName column
                    arena_data.RoundName = repmat(arena_name, height(arena_data), 1);
                end
                
                % Update trial number to reflect the order of this arena (i)
                arena_data.trial = repmat(i, height(arena_data), 1);
                
                combined_continuous = [combined_continuous; arena_data];
                
                % Delete the arena-specific file after reading
                delete(continuous_files{i});
                
            catch ME
                fprintf('Warning: Could not read continuous log file %s: %s\n', continuous_files{i}, ME.message);
            end
        end
    end
    
    % Combine discrete logs
    combined_discrete = [];
    for i = 1:length(discrete_files)
        if exist(discrete_files{i}, 'file')
            try
                % Read the arena-specific discrete log with UTF-8 encoding
                arena_data = readtable(discrete_files{i}, 'Delimiter', ',', 'TextType', 'string', 'Encoding', 'UTF-8');
                
                % Update trial number to reflect the order of this arena (i)
                if ismember('trial', arena_data.Properties.VariableNames)
                    arena_data.trial = repmat(i, height(arena_data), 1);
                end
                
                combined_discrete = [combined_discrete; arena_data];
                
                % Delete the arena-specific file after reading
                delete(discrete_files{i});
                
            catch ME
                fprintf('Warning: Could not read discrete log file %s: %s\n', discrete_files{i}, ME.message);
            end
        end
    end
    
    % Save combined files with UTF-8 encoding and reordered columns
    if ~isempty(combined_continuous)
        combined_continuous_filename = fullfile(results_dir, sprintf('%s_multi_arena_practice_continuous_log.csv', participant_id));
        
        % Reorder columns as requested: RealTime, trial_time, trial, RoundName, visibility, phase, event, x, y, rotation_angle
        desired_order = {'RealTime', 'trial_time', 'trial', 'RoundName', 'visibility', 'phase', 'event', 'x', 'y', 'rotation_angle'};
        
        % Check which columns exist and reorder them
        existing_columns = combined_continuous.Properties.VariableNames;
        final_order = {};
        
        for col = desired_order
            if ismember(col{1}, existing_columns)
                final_order{end+1} = col{1};
            end
        end
        
        % Add any remaining columns that weren't in the desired order
        for col = existing_columns
            if ~ismember(col{1}, final_order)
                final_order{end+1} = col{1};
            end
        end
        
        % Reorder the table
        combined_continuous = combined_continuous(:, final_order);
        
        writetable(combined_continuous, combined_continuous_filename, 'Delimiter', ',', 'Encoding', 'UTF-8');
        fprintf('    Combined continuous log saved: %s\n', combined_continuous_filename);
    end
    
    if ~isempty(combined_discrete)
        combined_discrete_filename = fullfile(results_dir, sprintf('%s_multi_arena_practice_discrete_log.csv', participant_id));
        writetable(combined_discrete, combined_discrete_filename, 'Delimiter', ',', 'Encoding', 'UTF-8');
        fprintf('    Combined discrete log saved: %s\n', combined_discrete_filename);
    end
end 