function run_snake_game(mode, participant_id, run_number, trial_number, total_trials, screen_number)
%RUN_SNAKE_GAME Run the snake game in practice, fMRI, or anatomical mode
%
%   run_snake_game('practice', participant_id, screen_number) - Run practice session outside magnet
%   run_snake_game('fmri', participant_id, run_number, trial_number, total_trials, screen_number) - Run fMRI session inside magnet
%   run_snake_game('anatomical', participant_id, screen_number) - Run endless game during anatomical scan
%
%   Parameters:
%       mode: 'practice', 'fmri', or 'anatomical'
%       participant_id: Participant initials (e.g., 'TS263')
%       run_number: Run number for fMRI mode (ignored for practice and anatomical)
%       trial_number: Current trial number in sequence (ignored for practice and anatomical)
%       total_trials: Total number of trials in sequence (ignored for practice and anatomical)
%       screen_number: Screen number to display on (optional, default: None)
%
%   Examples:
%       run_snake_game('practice', 'TS263')                    % Practice session (default screen)
%       run_snake_game('practice', 'TS263', [], [], [], 0)    % Practice session on screen 0
%       run_snake_game('fmri', 'TS263', 1, 2, 4)             % fMRI run 1, trial 2 of 4 (default screen)
%       run_snake_game('fmri', 'TS263', 1, 2, 4, 0)         % fMRI run 1, trial 2 of 4 on screen 0
%       run_snake_game('anatomical', 'TS263')                 % Anatomical scan mode (default screen)
%       run_snake_game('anatomical', 'TS263', [], [], [], 0)  % Anatomical scan mode on screen 0

    % Get the current directory (should be the fMRI experiment directory)
    current_dir = pwd;
    
    % Path to the exploration experiment directory
    exploration_dir = fullfile(current_dir, 'exploration');
    
    if ~exist(exploration_dir, 'dir')
        error('Exploration experiment directory not found: %s', exploration_dir);
    end

    % Change to the exploration experiment directory
    cd(exploration_dir);
    
    % Function to find Python executable (Windows-specific)
    function python_cmd = find_python()
        % Try different Python commands for Windows
        python_commands = {'py', 'python', 'python3'};
        
        for i = 1:length(python_commands)
            try
                [status, ~] = system(sprintf('%s --version', python_commands{i}));
                if status == 0
                    python_cmd = python_commands{i};
                    return;
                end
            catch
                % Continue to next command
            end
        end
        
        % If no Python found, try to find Python in common Windows installation paths
        common_paths = {
            'C:\Python*\python.exe',
            'C:\Program Files\Python*\python.exe',
            'C:\Program Files (x86)\Python*\python.exe',
            '%LOCALAPPDATA%\Programs\Python\Python*\python.exe'
        };
        
        % Try to find Python in common paths
        for i = 1:length(common_paths)
            % Expand environment variables
            path = strrep(common_paths{i}, '%LOCALAPPDATA%', getenv('LOCALAPPDATA'));
            % Use dir to find matching paths
            files = dir(path);
            if ~isempty(files)
                for j = 1:length(files)
                    full_path = fullfile(files(j).folder, files(j).name);
                    try
                        [status, ~] = system(sprintf('"%s" --version', full_path));
                        if status == 0
                            python_cmd = sprintf('"%s"', full_path);
                            return;
                        end
                    catch
                        % Continue to next file
                    end
                end
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
        
        if strcmp(mode, 'practice')
            % Run practice session
            if nargin < 2
                participant_id = 'TEST';
            end
            if nargin < 3
                screen_number = 0; % Default screen for practice
            end
            
            fprintf('Running snake practice session for participant: %s, screen: %d\n', participant_id, screen_number);
            
            % Run the practice script
            cmd = sprintf('%s snake_out.py %s %d', python_cmd, participant_id, screen_number);
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Snake practice session completed successfully.\n');
            else
                error('Snake practice session failed: %s', result);
            end
            
        elseif strcmp(mode, 'fmri')
            % Run fMRI session
            if nargin < 2
                participant_id = 'TEST';
            end
            if nargin < 3
                run_number = 1;
            end
            if nargin < 4
                trial_number = 1;
            end
            if nargin < 5
                total_trials = 1;
            end
            if nargin < 6
                screen_number = 0; % Default screen for fMRI
            end
            
            fprintf('Running snake fMRI session for participant: %s, run: %d, trial: %d/%d, screen: %d\n', participant_id, run_number, trial_number, total_trials, screen_number);
            
            % Run the fMRI script without scanning parameter (handled at MATLAB level)
            cmd = sprintf('%s snake_in.py %s %d %d %d %d', python_cmd, participant_id, run_number, trial_number, total_trials, screen_number);
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Snake fMRI run %d completed successfully.\n', run_number);
            else
                error('Snake fMRI session failed: %s', result);
            end
            
        elseif strcmp(mode, 'anatomical')
            % Run anatomical scan mode (endless gameplay)
            if nargin < 2
                participant_id = 'TEST';
            end
            if nargin < 6
                screen_number = 0; % Default screen for anatomical
            end
            
            fprintf('Running snake anatomical scan mode for participant: %s, screen: %d\n', participant_id, screen_number);
            
            % Run the anatomical script (endless gameplay)
            cmd = sprintf('%s snake.py anatomical --participant %s --screen %d', python_cmd, participant_id, screen_number);
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Snake anatomical scan mode completed successfully.\n');
            else
                error('Snake anatomical scan mode failed: %s', result);
            end
            
        else
            error('Invalid mode. Use ''practice'', ''fmri'', or ''anatomical''');
        end
        
    catch ME
        % Return to original directory before re-throwing error
        cd(current_dir);
        rethrow(ME);
    end
    
    % Return to original directory
    cd(current_dir);
end 