function run_multi_target_vection(mode, participant_id, screen_number)
%RUN_MULTI_TARGET_VECTION Run the multi_target vection experiment
%
%   run_multi_target_vection('practice', participant_id, screen_number) - Run full practice sequence
%       (3 trials: training garden, beach, zoo + thank you)
%   run_multi_target_vection('fmri', participant_id, run_number, trial_number, total_trials, arena_name, screen_number)
%       - Run single fMRI trial (for use by fmri_session)
%
%   Practice: Runs one Python process with --practice-sequence (instructions, trial 1, 2, 3, thank you)
%
%   Examples:
%       run_multi_target_vection('practice', 'TS263', 0)
%       run_multi_target_vection('practice', 'TS263')  % default screen

    % Directory containing this .m file (so we always run from fMRI/exploration_trigger_vection regardless of pwd)
    vection_dir = fileparts(which('run_multi_target_vection'));
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
        
        if nargin < 2
            participant_id = 'TEST';
        end
        if nargin < 3
            screen_number = [];
        end
        
        if strcmp(mode, 'practice')
            % Run full practice sequence (3 trials + thank you)
            cmd = sprintf('%s multi_target_vection.py practice --participant %s --practice-sequence', python_cmd, participant_id);
            if ~isempty(screen_number)
                cmd = sprintf('%s --screen %d', cmd, screen_number);
            end
            
            fprintf('Running multi_target vection practice sequence (training, beach, zoo)\n');
            fprintf('Command: %s\n', cmd);
            
            [status, result] = system(cmd);
            
            if status == 0
                fprintf('Multi target vection practice completed successfully.\n');
            else
                error('Multi target vection practice failed: %s', result);
            end
        else
            % fMRI mode: typically invoked by multi_target_run.py, not this wrapper
            error('fMRI mode: use multi_target_run.py from exploration_trigger_vection');
        end
        
    catch ME
        cd(current_dir);
        rethrow(ME);
    end
    
    cd(current_dir);
end
