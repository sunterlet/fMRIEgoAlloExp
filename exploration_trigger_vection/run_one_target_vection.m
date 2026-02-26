function run_one_target_vection(mode, participant_id, run_number, trial_number, total_trials, screen_number)
%RUN_ONE_TARGET_VECTION Run the one_target vection experiment in practice or fMRI mode
%
%   run_one_target_vection('practice', participant_id, screen_number) - Run practice session outside magnet
%   run_one_target_vection('fmri', participant_id, run_number, trial_number, total_trials, screen_number) - Run fMRI session inside magnet
%
%   Parameters:
%       mode: 'practice' or 'fmri'
%       participant_id: Participant initials (e.g., 'TS263')
%       run_number: Run number for fMRI mode (ignored for practice)
%       trial_number: Current trial number in sequence (ignored for practice)
%       total_trials: Total number of trials in sequence (ignored for practice)
%       screen_number: Screen number to display on (optional)
%
%   Examples:
%       run_one_target_vection('practice', 'TS263')                    % Practice session
%       run_one_target_vection('practice', 'TS263', [], [], [], 0)    % Practice session on screen 0
%       run_one_target_vection('fmri', 'TS263', 1, 1, 4)             % fMRI run 1, trial 1 of 4
%       run_one_target_vection('fmri', 'TS263', 1, 1, 4, 0)         % fMRI run 1, trial 1 of 4 on screen 0

    % Directory containing this .m file (so we always run from fMRI/exploration_trigger_vection regardless of pwd)
    vection_dir = fileparts(which('run_one_target_vection'));
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
            if nargin < 6
                screen_number = [];
            end
            
            fprintf('Running one_target vection practice session for participant: %s\n', participant_id);
            
            if isempty(screen_number)
                cmd = sprintf('%s one_target_out_vection.py %s', python_cmd, participant_id);
            else
                cmd = sprintf('%s one_target_out_vection.py %s %d', python_cmd, participant_id, screen_number);
            end
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('One target vection practice session completed successfully.\n');
            else
                error('One target vection practice session failed: %s', result);
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
            if nargin < 6
                screen_number = [];
            end
            
            fprintf('Running one_target vection fMRI session for participant: %s, run: %d, trial: %d/%d\n', participant_id, run_number, trial_number, total_trials);
            
            if isempty(screen_number)
                cmd = sprintf('%s one_target_in_vection.py %s %d %d %d', python_cmd, participant_id, run_number, trial_number, total_trials);
            else
                cmd = sprintf('%s one_target_in_vection.py %s %d %d %d %d', python_cmd, participant_id, run_number, trial_number, total_trials, screen_number);
            end
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('One target vection fMRI run %d completed successfully.\n', run_number);
            else
                error('One target vection fMRI session failed: %s', result);
            end
            
        else
            error('Invalid mode. Use ''practice'' or ''fmri''');
        end
        
    catch ME
        cd(current_dir);
        rethrow(ME);
    end
    
    cd(current_dir);
end
