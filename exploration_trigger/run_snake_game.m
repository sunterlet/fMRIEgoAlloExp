function run_snake_game(mode, participant_id, run_number, trial_number, total_trials, screen_number)
%RUN_SNAKE_GAME Run the snake game in practice, fMRI, or shimming mode
%
%   run_snake_game('practice', participant_id, screen_number) - Run practice session outside magnet
%   run_snake_game('fmri', participant_id, run_number, trial_number, total_trials, screen_number) - Run fMRI session inside magnet
%   run_snake_game('shimming', participant_id, screen_number) - Run endless game during scan shimming
%
%   Parameters:
%       mode: 'practice', 'fmri', or 'shimming'
%       participant_id: Participant initials (e.g., 'TS263')
%       run_number: Run number for fMRI mode (ignored for practice and shimming)
%       trial_number: Current trial number in sequence (ignored for practice and shimming)
%       total_trials: Total number of trials in sequence (ignored for practice and shimming)
%       screen_number: Screen number to display on (optional, default: None)
%                      If not provided, will use the screen selected in fMRI_session.m
%
%   Examples:
%       run_snake_game('practice', 'TS263')                    % Practice session (default screen)
%       run_snake_game('practice', 'TS263', [], [], [], 0)    % Practice session on screen 0
%       run_snake_game('fmri', 'TS263', 1, 2, 4)             % fMRI run 1, trial 2 of 4 (default screen)
%       run_snake_game('fmri', 'TS263', 1, 2, 4, 0)         % fMRI run 1, trial 2 of 4 on screen 0
%       run_snake_game('shimming', 'TS263')                 % Shimming mode (uses selectedScreen from fMRI_session.m)
%       run_snake_game('shimming', 'TS263', [], [], [], 0)  % Shimming mode on screen 0

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
            if nargin < 6
                screen_number = 2; % Default: Use MATLAB Screen 2
            end
            
            % Convert MATLAB screen numbering to Python screen numbering
            % Using Python screen 0 for all monitors
            python_screen = 0;
            
            fprintf('Running snake practice session for participant: %s, MATLAB screen: %d, Python screen: %d\n', ...
                participant_id, screen_number, python_screen);
            
            % Run the practice script
            cmd = sprintf('%s snake_out.py %s %d', python_cmd, participant_id, python_screen);
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
                screen_number = 2; % Default: Use MATLAB Screen 2
            end
            
            % Convert MATLAB screen numbering to Python screen numbering
            % Using Python screen 0 for all monitors
            python_screen = 0;
            
            fprintf('Running snake fMRI session for participant: %s, run: %d, trial: %d/%d, MATLAB screen: %d, Python screen: %d\n', ...
                participant_id, run_number, trial_number, total_trials, screen_number, python_screen);
            
            % Run the fMRI script without scanning parameter (handled at MATLAB level)
            cmd = sprintf('%s snake_in.py %s %d %d %d %d', python_cmd, participant_id, run_number, trial_number, total_trials, python_screen);
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Snake fMRI run %d completed successfully.\n', run_number);
            else
                error('Snake fMRI session failed: %s', result);
            end
            
        elseif strcmp(mode, 'shimming')
            % Run shimming mode (endless gameplay during scan shimming)
            if nargin < 2
                participant_id = 'TEST';
            end
            if nargin < 6
                % Try to get selectedScreen from the main fMRI session
                try
                    % Check if selectedScreen variable exists in the base workspace
                    if evalin('base', 'exist(''selectedScreen'', ''var'')')
                        screen_number = evalin('base', 'selectedScreen');
                        fprintf('Using selectedScreen from fMRI_session.m: %d\n', screen_number);
                    else
                        screen_number = 0; % Default screen for shimming
                        fprintf('No selectedScreen found in base workspace, using default screen 0\n');
                    end
                catch
                        screen_number = 0; % Default screen for shimming
                    fprintf('Could not access selectedScreen from base workspace, using default screen 0\n');
                end
            end
            
            fprintf('Running snake shimming mode for participant: %s, MATLAB screen: %d\n', participant_id, screen_number);
            
            % Convert MATLAB screen numbering to Python screen numbering
            % Using Python screen 0 for all monitors
            python_screen = 0;
            fprintf('Using Python screen 0 (primary monitor)\n');
            
            % Verify screen selection if provided
            if ~isempty(python_screen)
                try
                    % Initialize Psychtoolbox to verify screen exists
                    Screen('Preference', 'SkipSyncTests', 1);  % Skip sync tests for faster startup
                    screen_info = Screen('Screens');
                    if screen_number > max(screen_info)
                        warning('MATLAB Screen %d not found. Available screens: %s. Using default screen.', ...
                                screen_number, mat2str(screen_info));
                        python_screen = 0;
                    else
                        fprintf('✓ MATLAB Screen %d verified and available for shimming\n', screen_number);
                        fprintf('✓ Will use Python screen %d\n', python_screen);
                    end
                catch ME
                    warning('Could not verify screen selection: %s. Using default Python screen 0.', ME.message);
                    python_screen = 0;
                end
            end
            
            % Run the shimming script (endless gameplay)
            cmd = sprintf('%s snake.py shimming --participant %s --screen %d', python_cmd, participant_id, python_screen);
            
            % Run the Python script
            fprintf('Executing command: %s\n', cmd);
            fprintf('Starting snake shimming game...\n');
            
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('✓ Snake shimming mode completed successfully.\n');
                if ~isempty(result)
                    fprintf('Python output:\n%s\n', result);
                end
            else
                fprintf('✗ Snake shimming mode failed with status: %d\n', status);
                if ~isempty(result)
                    fprintf('Error output:\n%s\n', result);
                end
                error('Snake shimming mode failed: %s', result);
            end
            
        else
            error('Invalid mode. Use ''practice'', ''fmri'', or ''shimming''');
        end
        
    catch ME
        % Return to original directory before re-throwing error
        cd(current_dir);
        rethrow(ME);
    end
    
    % Return to original directory
    cd(current_dir);
end 