function run_snake_vection(mode, participant_id, run_number, trial_number, total_trials, screen_number)
%RUN_SNAKE_VECTION Run the snake vection game in practice, fMRI, or shimming mode
%
%   run_snake_vection('practice', participant_id, screen_number) - Run practice session outside magnet
%   run_snake_vection('fmri', participant_id, run_number, trial_number, total_trials, screen_number) - Run fMRI session inside magnet
%   run_snake_vection('shimming', participant_id, screen_number) - Run endless game during shimming scan
%
%   Parameters:
%       mode: 'practice', 'fmri', or 'shimming'
%       participant_id: Participant initials (e.g., 'TS263')
%       run_number: Run number for fMRI mode (ignored for practice and shimming)
%       trial_number: Current trial number in sequence (ignored for practice and shimming)
%       total_trials: Total number of trials in sequence (ignored for practice and shimming)
%       screen_number: Screen number to display on (optional, default: 0)
%
%   Examples:
%       run_snake_vection('practice', 'TS263')                    % Practice session (default screen)
%       run_snake_vection('practice', 'TS263', [], [], [], 0)    % Practice session on screen 0
%       run_snake_vection('fmri', 'TS263', 1, 2, 4)             % fMRI run 1, trial 2 of 4 (default screen)
%       run_snake_vection('fmri', 'TS263', 1, 2, 4, 0)         % fMRI run 1, trial 2 of 4 on screen 0
%       run_snake_vection('shimming', 'TS263')                 % Shimming scan mode (default screen)

    current_dir = pwd;  % Save so we can restore after cd(vection_dir) and in catch
    % Directory containing this .m file (so we always run from fMRI/exploration_trigger_vection regardless of pwd)
    vection_dir = fileparts(which('run_snake_vection'));
    if isempty(vection_dir)
        vection_dir = fullfile(pwd, 'exploration_trigger_vection');
    end
    if ~exist(vection_dir, 'dir')
        error('Exploration trigger vection directory not found: %s', vection_dir);
    end

    cd(vection_dir);
    
    % Function to find Python executable
    function python_cmd = find_python()
        python_commands = {'py', 'python', 'python3'};
        
        for i = 1:length(python_commands)
            try
                [status, ~] = system(sprintf('%s --version', python_commands{i}));
                if status == 0
                    python_cmd = python_commands{i};
                    return;
                end
            catch
            end
        end
        
        common_paths = {
            'C:\Python*\python.exe',
            'C:\Program Files\Python*\python.exe',
            'C:\Program Files (x86)\Python*\python.exe',
            '%LOCALAPPDATA%\Programs\Python\Python*\python.exe'
        };
        
        for i = 1:length(common_paths)
            path = strrep(common_paths{i}, '%LOCALAPPDATA%', getenv('LOCALAPPDATA'));
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
                    end
                end
            end
        end
        
        error(['Python not found! Please install Python 3.8+ from https://www.python.org/downloads/\n' ...
               'Make sure to check "Add Python to PATH" during installation.']);
    end
    
    try
        python_cmd = find_python();
        fprintf('Using Python command: %s\n', python_cmd);
        
        if strcmp(mode, 'practice')
            if nargin < 2
                participant_id = 'TEST';
            end
            if nargin < 6 || isempty(screen_number)
                screen_number = 0;
            end
            
            fprintf('Running snake vection practice session for participant: %s, screen: %d\n', participant_id, screen_number);
            
            if screen_number == 0
                cmd = sprintf('%s snake_out_vection.py %s', python_cmd, participant_id);
            else
                cmd = sprintf('%s snake_out_vection.py %s %d', python_cmd, participant_id, screen_number);
            end
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Snake vection practice session completed successfully.\n');
            else
                error('Snake vection practice session failed: %s', result);
            end
            
        elseif strcmp(mode, 'fmri')
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
            if nargin < 6 || isempty(screen_number)
                screen_number = 0;
            end
            
            fprintf('Running snake vection fMRI session for participant: %s, run: %d, trial: %d/%d, screen: %d\n', participant_id, run_number, trial_number, total_trials, screen_number);
            
            cmd = sprintf('%s snake_in_vection.py %s %d %d %d %d', python_cmd, participant_id, run_number, trial_number, total_trials, screen_number);
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Snake vection fMRI run %d completed successfully.\n', run_number);
            else
                error('Snake vection fMRI session failed: %s', result);
            end
            
        elseif strcmp(mode, 'shimming')
            if nargin < 2
                participant_id = 'TEST';
            end
            if nargin < 6 || isempty(screen_number)
                screen_number = 0;
            end
            
            fprintf('Running snake vection shimming scan mode for participant: %s, screen: %d\n', participant_id, screen_number);
            
            cmd = sprintf('%s snake_vection.py shimming --participant %s --screen %d', python_cmd, participant_id, screen_number);
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Snake vection shimming scan mode completed successfully.\n');
            else
                error('Snake vection shimming scan mode failed: %s', result);
            end
            
        else
            error('Invalid mode. Use ''practice'', ''fmri'', or ''shimming''');
        end
        
    catch ME
        cd(current_dir);
        rethrow(ME);
    end
    
    cd(current_dir);
end
