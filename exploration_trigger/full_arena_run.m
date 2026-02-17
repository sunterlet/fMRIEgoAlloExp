function full_arena_run(participant_id, run_number, screen_number, scanning, com, TR)
%FULL_ARENA_RUN Run the Full Arena Run with run-based configuration
%
%   full_arena_run(participant_id, run_number, screen_number, scanning, com, TR) - Run Full Arena Run
%
%   Parameters:
%       participant_id: Participant ID (e.g., 'TS263')
%       run_number: Run number in fMRI session
%           - Run 1: 4 trials (2 snake + 2 multi_arena) - uses hospital, library
%           - Run 2: 4 trials (2 snake + 2 multi_arena) - uses gym, museum
%           - Other: 12 trials (6 snake + 6 multi_arena) - uses all 6 arenas
%       screen_number: Screen number to display on (optional, default: None)
%
%   Examples:
%       full_arena_run('TS263', 1)           % Full Arena Run 1 (default screen)
%       full_arena_run('TS263', 1, 0)       % Full Arena Run 1 on screen 0
%       full_arena_run('TS263', 2, 0)       % Full Arena Run 2 on screen 0

    % Get the current directory (should be the fMRI experiment directory)
    current_dir = pwd;
    
    % Path to the exploration_trigger experiment directory
    exploration_dir = fullfile(current_dir, 'exploration_trigger');
    
    if ~exist(exploration_dir, 'dir')
        error('Exploration experiment directory not found: %s', exploration_dir);
    end

    % Change to the exploration_trigger experiment directory
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
            run_number = 1;  % Default to run 1
        end
        if nargin < 3
            screen_number = [];
        end
        if nargin < 4
            % Try to get scanning from base workspace
            try
                if evalin('base', 'exist(''scanning'', ''var'')')
                    scanning = evalin('base', 'scanning');
                else
                    scanning = false;
                end
            catch
                scanning = false;
            end
        end
        if nargin < 5
            % Try to get com from base workspace
            try
                if evalin('base', 'exist(''com'', ''var'')')
                    com = evalin('base', 'com');
                else
                    com = 'com4';
                end
            catch
                com = 'com4';
            end
        end
        if nargin < 6
            % Try to get TR from base workspace
            try
                if evalin('base', 'exist(''TR'', ''var'')')
                    TR = evalin('base', 'TR');
                else
                    TR = 2.01;
                end
            catch
                TR = 2.01;
            end
        end
        
        fprintf('Running Full Arena Run for participant: %s\n', participant_id);
        fprintf('Run number: %d\n', run_number);
        if ~isempty(screen_number)
            fprintf('Display will be on screen: %d\n', screen_number);
        else
            fprintf('Display will use default screen behavior\n');
        end
        
        % Determine configuration based on run number
        if run_number == 1
            fprintf('This will run 2 snake trials and 2 multi_arena trials (intertwined)\n');
            fprintf('Arenas: hospital, library\n');
        elseif run_number == 2
            fprintf('This will run 2 snake trials and 2 multi_arena trials (intertwined)\n');
            fprintf('Arenas: gym, museum\n');
        else
            fprintf('This will run 6 snake trials and 6 multi_arena trials (intertwined)\n');
            fprintf('Arenas: hospital, library, gym, museum, airport, market\n');
        end
        
        % Build command with optional screen parameter
        % Python uses screen 0 (primary monitor)
        python_screen = 0;
        
        % Build command array for ProcessBuilder
        command = {python_cmd, 'full_arena_run.py', '--participant', participant_id, '--run', num2str(run_number), '--screen', num2str(python_screen)};
        
        % Add trigger parameters if scanning is enabled
        if scanning
            command{end+1} = '--scanning';
            command{end+1} = '--com';
            command{end+1} = com;
            command{end+1} = '--tr';
            command{end+1} = num2str(TR);
        end
        
        % Run the Python script
        cmd_str = sprintf('%s ', command{:});
        fprintf('Executing command: %s\n', cmd_str(1:end-1)); % Remove trailing space
        fprintf('Starting Full Arena Run...\n');
        fprintf('\n--- Python Output (real-time) ---\n');
        
        % Use Java ProcessBuilder for real-time output
        processBuilder = java.lang.ProcessBuilder(command);
        processBuilder.directory(java.io.File(exploration_dir)); % Set working directory
        processBuilder.redirectErrorStream(true); % Redirect error stream to output stream
        process = processBuilder.start();
        
        reader = java.io.BufferedReader(java.io.InputStreamReader(process.getInputStream()));
        
        % Read output line by line in real-time
        while isjava(process) && process.isAlive()
            if reader.ready()
                line = reader.readLine();
                if ~isempty(line)
                    fprintf('%s\n', char(line));
                end
            else
                pause(0.01); % Small pause to prevent busy-waiting
            end
        end
        
        % Read any remaining output
        while reader.ready()
            line = reader.readLine();
            if ~isempty(line)
                fprintf('%s\n', char(line));
            end
        end
        
        % Wait for process to complete and get exit code
        exit_code = process.waitFor();
        
        fprintf('\n--- End of Python Output ---\n');
        
        if exit_code == 0
            fprintf('✓ Full Arena Run completed successfully.\n');
        else
            fprintf('✗ Full Arena Run failed with exit code: %d\n', exit_code);
            error('Full Arena Run failed with exit code: %d', exit_code);
        end
        
    catch ME
        % Return to original directory before re-throwing error
        cd(current_dir);
        rethrow(ME);
    end
    
    % Return to original directory
    cd(current_dir);
end 