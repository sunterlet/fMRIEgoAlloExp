function one_target_run(participant_id, screen_number)
%ONE_TARGET_RUN Run the One Target Run (6 snake + 6 one_target trials)
%
%   one_target_run(participant_id, screen_number) - Run One Target Run
%
%   Parameters:
%       participant_id: Participant ID (e.g., 'TS263')
%       screen_number: Screen number to display on (optional, default: None)
%
%   Terminology:
%   - This is a SINGLE RUN containing 12 trials (6 snake + 6 one_target)
%   - Each trial is numbered 1-12 within this run
%   - Run number 1 = One Target Run (first run in fMRI session)
%
%   Examples:
%       one_target_run('TS263')           % One Target Run (default screen)
%       one_target_run('TS263', 0)       % One Target Run on screen 0

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
        
        % Validate inputs
        if nargin < 1
            participant_id = 'TEST';
        end
        if nargin < 2
            screen_number = [];
        end
        
        fprintf('Running One Target Run for participant: %s\n', participant_id);
        if ~isempty(screen_number)
            fprintf('Display will be on screen: %d\n', screen_number);
        else
            fprintf('Display will use default screen behavior\n');
        end
        fprintf('This will run 6 snake trials and 6 one_target trials (intertwined)\n');
        
        % Build command with optional screen parameter
        if ~isempty(screen_number)
            cmd = sprintf('%s one_target_run.py --participant %s --run 1 --screen %d', python_cmd, participant_id, screen_number);
        else
            cmd = sprintf('%s one_target_run.py --participant %s --run 1', python_cmd, participant_id);
        end
        [status, result] = system(cmd);
        
        if status == 0
            fprintf('One Target Run completed successfully.\n');
        else
            error('One Target Run failed: %s', result);
        end
        
    catch ME
        % Return to original directory before re-throwing error
        cd(current_dir);
        rethrow(ME);
    end
    
    % Return to original directory
    cd(current_dir);
end 