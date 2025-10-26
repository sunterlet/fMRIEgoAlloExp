%% fMRI Sessions - Egocentric Allocentric Translation fMRI Experiment
% This file runs all fMRI sessions inside the magnet

% Sequence Order
    
    % Shimming + snake practice (endless gameplay during anatomical scan)

    % Rest X 2
    
    %  8 trial PTSOD
    
    % One target block desing
        % Snake
        % One target arena
        % Snake ... 

    % Movie 1    
    
    % Full arena 

        % Snake
        % Full arena
        % Snake ... 

    %  8 trial PTSOD

    % Movie 2 

    % Anatomy

%% Setup Environment
sca; close all; clc; clear;

% Participant Information
SubID = 'test';

% Screen Selection
selectedScreen = select_screen();
% selectedScreen = 1;

%% Setup Centralized Results Directory
fprintf('\n=== Setting up Centralized Results Directory ===\n');

% Create centralized results directory
centralized_results_dir = fullfile(pwd, 'Results');
if ~exist(centralized_results_dir, 'dir')
    mkdir(centralized_results_dir);
    fprintf('✓ Created centralized Results directory: %s\n', centralized_results_dir);
else
    fprintf('✓ Centralized Results directory already exists: %s\n', centralized_results_dir);
end

% Set environment variable for Python scripts to use centralized results directory
setenv('CENTRALIZED_RESULTS_DIR', centralized_results_dir);
fprintf('✓ Set CENTRALIZED_RESULTS_DIR environment variable\n');

% Create SubID subfolder in Results directory
subid_dir = fullfile(centralized_results_dir, SubID);
if ~exist(subid_dir, 'dir')
    mkdir(subid_dir);
    fprintf('✓ Created SubID subfolder: %s\n', subid_dir);
else
    fprintf('✓ SubID subfolder already exists: %s\n', subid_dir);
end

%% Scanning Parameters 
scanning = false;   % Enable trigger functionality for all fMRI experiments
com = 'com4';      % Serial port for trigger
TR = 2.01;           % TR in seconds

fprintf('\n=== Trigger Configuration ===\n');
fprintf('Scanning mode: %s\n', mat2str(scanning));
if ~scanning
    fprintf('TESTING MODE: No trigger handling (press any key to start blocks)\n');
end
fprintf('Serial port: %s\n', com);
fprintf('TR: %d seconds\n', TR);

%% Add Relevant Paths
fprintf('\n=== Adding Relevant Paths ===\n');

% Add PTSOD Code directory to path
ptsodCodePath = fullfile(pwd, 'PTSOD', 'Code');
if exist(ptsodCodePath, 'dir')
    addpath(ptsodCodePath);
    fprintf('✓ PTSOD Code added to path: %s\n', ptsodCodePath);
else
    fprintf('⚠ PTSOD Code directory not found at: %s\n', ptsodCodePath);
end

% Add exploration directory to path
explorationPath = fullfile(pwd, 'exploration');
if exist(explorationPath, 'dir')
    addpath(explorationPath);
    fprintf('✓ Exploration experiment added to path: %s\n', explorationPath);
else
    fprintf('⚠ Exploration experiment directory not found at: %s\n', explorationPath);
end

% Add trigger_manager function to path
triggerManagerPath = fullfile(pwd, 'exploration');
if exist(triggerManagerPath, 'dir')
    addpath(triggerManagerPath);
    fprintf('✓ Trigger manager added to path: %s\n', triggerManagerPath);
else
    fprintf('⚠ Trigger manager directory not found at: %s\n', triggerManagerPath);
end

% Add run_snake_game function to path
snakeGamePath = fullfile(pwd, 'exploration');
if exist(snakeGamePath, 'dir')
    addpath(snakeGamePath);
    fprintf('✓ Snake game functions added to path: %s\n', snakeGamePath);
else
    fprintf('⚠ Snake game functions directory not found at: %s\n', snakeGamePath);
end

% Add sounds directory to path
soundsPath = fullfile(pwd, 'sounds');
if exist(soundsPath, 'dir')
    addpath(soundsPath);
    fprintf('✓ Sounds directory added to path: %s\n', soundsPath);
else
    fprintf('⚠ Sounds directory not found at: %s\n', soundsPath);
end

% Add arenas_new_icons directory to path
iconsPath = fullfile(pwd, 'arenas_new_icons');
if exist(iconsPath, 'dir')
    addpath(genpath(iconsPath));
    fprintf('✓ Arena icons added to path: %s\n', iconsPath);
else
    fprintf('⚠ Arena icons directory not found at: %s\n', iconsPath);
end

fprintf('Path setup completed.\n');

%% Anatomical Scan Snake Practice
fprintf('\n=== Anatomical Scan Snake Practice ===\n');
fprintf('Participants will play endless snake game during anatomical scan...\n');
fprintf('The game will run continuously until manually terminated.\n');
fprintf('Press ESC key in the game window to exit when anatomical scan is complete.\n\n');

% Run endless snake game for anatomical scan period
try
    fprintf('Game will start in 3 seconds...\n');
    pause(3);  % Give participant time to prepare
    
    % Use the run_snake_game function for consistency
    run_snake_game('anatomical', SubID, [], [], [], selectedScreen);
    
    fprintf('✓ Anatomical snake practice completed successfully!\n');
catch ME
    fprintf('Error in anatomical snake practice: %s\n', ME.message);
    fprintf('Continuing with experiment...\n');
end

%% PTSOD fMRI Run 1
fprintf('\n=== PTSOD fMRI Run 1 ===\n');
run = 1;

% Run fMRI
try
    [dataTable, filename] = PTSODfunc_SplitRuns_fMRI_New(SubID, run, 'fMRI', selectedScreen, scanning, com, TR);
    
    % Check if the experiment actually completed or exited early
    if ~isempty(filename)
        fprintf('PTSOD fMRI run 1 completed successfully!\n');
        fprintf('Data saved to: %s\n', filename);
    else
        fprintf('PTSOD fMRI run 1 exited early, partial data was saved.\n');
    end
catch ME
    fprintf('Error in PTSOD fMRI run 1: %s\n', ME.message);
end

%% One Target Run Design
fprintf('\n=== One Target Run Design ===\n');

% Initialize trigger if scanning is enabled
if scanning7
    fprintf('Initializing trigger for One Target Run Design...\n');
    s=serial('com4','BaudRate',9600);
    fopen(s)
    sync=0;
end

% Wait for trigger before starting block
fprintf('Waiting for scanner trigger before One Target Run Design...\n');
trigger_received_time = [];
while scanning    % Middle Trigger
    sync=sync+1;
    if strcmpi(s.PinStatus.DataSetReady, 'off')
        while(strcmpi(s.PinStatus.DataSetReady, 'off'))

        end 
    elseif strcmpi(s.PinStatus.DataSetReady, 'on')
        while(strcmpi(s.PinStatus.DataSetReady, 'on'))

        end
    end
    disp(sync);
    if sync>0 
        trigger_received_time = GetSecs();
        break; 
    end
end
fprintf('Trigger received! Starting One Target Run Design...\n');

% Log trigger received event if scanning is enabled
if scanning && ~isempty(trigger_received_time)
    fprintf('Logging trigger received event at time: %.3f\n', trigger_received_time);
    % Set environment variable for Python scripts to know trigger time
    setenv('TRIGGER_RECEIVED_TIME', num2str(trigger_received_time));
end

% Run the complete One Target Run (6 snake + 6 one_target trials intertwined)
fprintf('\n--- Running One Target Run (12 trials total) ---\n');
fprintf('This will run 6 snake trials and 6 one_target trials as a single process\n');
fprintf('to eliminate timing gaps between trials.\n');

one_target_run(SubID, selectedScreen);

% Close trigger after block completion
if scanning
    fclose(s);
    delete(s);
end

%% Full Arena Run Design
fprintf('\n=== Full Arena Run Design ===\n');

% Initialize trigger if scanning is enabled
if scanning
    fprintf('Initializing trigger for Full Arena Run Design...\n');
    s=serial('com4','BaudRate',9600);
    fopen(s)
    sync=0;
end

% Wait for trigger before starting block
fprintf('Waiting for scanner trigger before Full Arena Run Design...\n');
trigger_received_time = [];
while scanning    % Middle Trigger
    sync=sync+1;
    if strcmpi(s.PinStatus.DataSetReady, 'off')
        while(strcmpi(s.PinStatus.DataSetReady, 'off'))

        end 
    elseif strcmpi(s.PinStatus.DataSetReady, 'on')
        while(strcmpi(s.PinStatus.DataSetReady, 'on'))

        end
    end
    disp(sync);
    if sync>0 
        trigger_received_time = GetSecs();
        break; 
    end
end
fprintf('Trigger received! Starting Full Arena Run Design...\n');

% Log trigger received event if scanning is enabled
if scanning && ~isempty(trigger_received_time)
    fprintf('Logging trigger received event at time: %.3f\n', trigger_received_time);
    % Set environment variable for Python scripts to know trigger time
    setenv('TRIGGER_RECEIVED_TIME', num2str(trigger_received_time));
end

% Arena assignments (for reference - handled internally by the wrapper)
practice_arenas = {'garden', 'beach', 'village', 'ranch', 'zoo', 'school'};
fmri_arenas = {'hospital', 'bookstore', 'gym', 'museum', 'airport', 'market'};

fprintf(['f' ...
    'MRI Arenas: %s\n'], strjoin(fmri_arenas, ', '));

% Run the complete Full Arena Run (6 snake + 6 multi_arena trials intertwined)
fprintf('\n--- Running Full Arena Run (12 trials total) ---\n');
fprintf('This will run 6 snake trials and 6 multi_arena trials as a single process\n');
fprintf('to eliminate timing gaps between trials.\n');

full_arena_run(SubID, selectedScreen);

% Close trigger after block completion
if scanning
    fclose(s);
    delete(s);
end

%% PTSOD fMRI Run 2
fprintf('\n=== PTSOD fMRI Run 2 ===\n');
run = 2;

% Run fMRI
try
    [dataTable, filename] = PTSODfunc_SplitRuns_fMRI_New(SubID, run, 'fMRI', selectedScreen, scanning, com, TR);
    
    % Check if the experiment actually completed or exited early
    if ~isempty(filename)
        fprintf('PTSOD fMRI run 2 completed successfully!\n');
        fprintf('Data saved to: %s\n', filename);
    else
        fprintf('PTSOD fMRI run 2 exited early, partial data was saved.\n');
    end
catch ME
    fprintf('Error in PTSOD fMRI run 2: %s\n', ME.message);
end

%% Final Instruction Screen
fprintf('\n=== Final Instruction Screen ===\n');
fprintf('Showing final instruction with black background...\n');

% Add PTSOD Code directory to path if not already added
ptsodCodePath = fullfile(pwd, 'PTSOD', 'Code');
if exist(ptsodCodePath, 'dir')
    addpath(ptsodCodePath);
end

% Show final instruction screen with black background
try
    Instructions = DisplayInst_fMRI('9.png', selectedScreen);
    if Instructions == -1
        fprintf('Final instruction screen was exited early.\n');
    else
        fprintf('Final instruction screen completed successfully.\n');
    end
catch ME
    fprintf('Error showing final instruction screen: %s\n', ME.message);
end

%% Close trigger 
if scanning
    fprintf('Full Arena Run Design completed. Closing trigger...\n');
    trigger_manager('close');
else
    fprintf('Testing mode: Full Arena Run Design completed (no trigger to close).\n');
end

%% Summary
fprintf('\n=== fMRI EXPERIMENT COMPLETED ===\n');
fprintf('All data saved in centralized Results directory: %s\n', centralized_results_dir);

fprintf('\n=== ANATOMICAL SCAN DATA ===\n');
fprintf('Snake practice data during anatomical scan saved as:\n');
fprintf('  - %s_anatomical_snake_continuous.csv\n', SubID);
fprintf('  - %s_anatomical_snake_discrete.csv\n', SubID);

fprintf('\n=== ARENA USAGE SUMMARY ===\n');
fprintf('Multi-Arena run used 6 different arenas from the fMRI arena pool.\n');
fprintf('Used arenas: %s\n', strjoin(fmri_arenas(1:6), ', '));
fprintf('\nAll fMRI arenas have been used in this session.\n');

%% Cleanup
fprintf('fMRI session cleanup completed.\n');

%% Data Combination Function
% This function combines all trial data into single files per run type
% Run this manually after the session is complete
function combine_session_data(participant_id)
    fprintf('\n=== COMBINING SESSION DATA ===\n');
    fprintf('Participant: %s\n', participant_id);
    
    % Get centralized results directory
    centralized_results_dir = fullfile(pwd, 'Results');
    subid_dir = fullfile(centralized_results_dir, participant_id);
    
    if ~exist(subid_dir, 'dir')
        fprintf('Error: Participant directory not found: %s\n', subid_dir);
        return;
    end
    
    fprintf('Results directory: %s\n', subid_dir);
    
    % Define run types and their patterns
    run_types = {
        'OT', 'OT', 'One Target Run';
        'FA', 'FA', 'Full Arena Run'
    };
    
    % Define trial types for each run
    trial_types = {
        'ot', 'ot', 'One Target trials';
        'snake', 'snake', 'Snake trials';
        'fa', 'fa', 'Full Arena trials';
        'anatomical', 'anatomical', 'Anatomical scan snake trials'
    };
    
    % Process anatomical scan data first (standalone, not part of run types)
    fprintf('\n--- Processing Anatomical Scan Data ---\n');
    
    % Find anatomical snake files
    anatomical_continuous_pattern = sprintf('%s_anatomical_snake*continuous*.csv', participant_id);
    anatomical_continuous_files = dir(fullfile(subid_dir, anatomical_continuous_pattern));
    
    anatomical_discrete_pattern = sprintf('%s_anatomical_snake*discrete*.csv', participant_id);
    anatomical_discrete_files = dir(fullfile(subid_dir, anatomical_discrete_pattern));
    
    if ~isempty(anatomical_continuous_files) || ~isempty(anatomical_discrete_files)
        fprintf('  Processing anatomical snake trials...\n');
        
        % Combine anatomical continuous files
        if ~isempty(anatomical_continuous_files)
            fprintf('    Found %d anatomical continuous files\n', length(anatomical_continuous_files));
            combined_anatomical_continuous = [];
            
            for file_idx = 1:length(anatomical_continuous_files)
                file_path = fullfile(anatomical_continuous_files(file_idx).folder, anatomical_continuous_files(file_idx).name);
                try
                    % Read CSV file
                    data = readtable(file_path);
                    combined_anatomical_continuous = [combined_anatomical_continuous; data];
                    fprintf('      Added: %s\n', anatomical_continuous_files(file_idx).name);
                catch ME
                    fprintf('      Error reading %s: %s\n', anatomical_continuous_files(file_idx).name, ME.message);
                end
            end
            
            % Save combined anatomical continuous file
            if ~isempty(combined_anatomical_continuous)
                output_filename = fullfile(subid_dir, sprintf('%s_anatomical_snake_continuous.csv', participant_id));
                writetable(combined_anatomical_continuous, output_filename);
                fprintf('    Saved combined anatomical continuous: %s\n', output_filename);
                
                % Delete individual files
                for file_idx = 1:length(anatomical_continuous_files)
                    file_path = fullfile(anatomical_continuous_files(file_idx).folder, anatomical_continuous_files(file_idx).name);
                    delete(file_path);
                    fprintf('      Deleted: %s\n', anatomical_continuous_files(file_idx).name);
                end
            end
        end
        
        % Combine anatomical discrete files
        if ~isempty(anatomical_discrete_files)
            fprintf('    Found %d anatomical discrete files\n', length(anatomical_discrete_files));
            combined_anatomical_discrete = [];
            
            for file_idx = 1:length(anatomical_discrete_files)
                file_path = fullfile(anatomical_discrete_files(file_idx).folder, anatomical_discrete_files(file_idx).name);
                try
                    % Read CSV file
                    data = readtable(file_path);
                    combined_anatomical_discrete = [combined_anatomical_discrete; data];
                    fprintf('      Added: %s\n', anatomical_discrete_files(file_idx).name);
                catch ME
                    fprintf('      Error reading %s: %s\n', anatomical_discrete_files(file_idx).name, ME.message);
                end
            end
            
            % Save combined anatomical discrete file
            if ~isempty(combined_anatomical_discrete)
                output_filename = fullfile(subid_dir, sprintf('%s_anatomical_snake_discrete.csv', participant_id));
                writetable(combined_anatomical_discrete, output_filename);
                fprintf('    Saved combined anatomical discrete: %s\n', output_filename);
                
                % Delete individual files
                for file_idx = 1:length(anatomical_discrete_files)
                    file_path = fullfile(anatomical_discrete_files(file_idx).folder, anatomical_discrete_files(file_idx).name);
                    delete(file_path);
                    fprintf('      Deleted: %s\n', anatomical_discrete_files(file_idx).name);
                end
            end
        end
    end
    
    % Process regular run types
    for run_idx = 1:size(run_types, 1)
        run_code = run_types{run_idx, 1};
        run_pattern = run_types{run_idx, 2};
        run_name = run_types{run_idx, 3};
        
        fprintf('\n--- Processing %s ---\n', run_name);
        
        % Group files by trial type
        for trial_idx = 1:size(trial_types, 1)
            trial_code = trial_types{trial_idx, 1};
            trial_pattern = trial_types{trial_idx, 2};
            trial_name = trial_types{trial_idx, 3};
            
            % Find continuous files for this trial type
            continuous_pattern = sprintf('%s_%s_%s*continuous*.csv', participant_id, run_code, trial_pattern);
            continuous_files = dir(fullfile(subid_dir, continuous_pattern));
            
            % Find discrete files for this trial type
            discrete_pattern = sprintf('%s_%s_%s*discrete*.csv', participant_id, run_code, trial_pattern);
            discrete_files = dir(fullfile(subid_dir, discrete_pattern));
            
            if ~isempty(continuous_files) || ~isempty(discrete_files)
                fprintf('  Processing %s trials...\n', trial_name);
                
                % Combine continuous files
                if ~isempty(continuous_files)
                    fprintf('    Found %d continuous files\n', length(continuous_files));
                    combined_continuous = [];
                    
                    for file_idx = 1:length(continuous_files)
                        file_path = fullfile(continuous_files(file_idx).folder, continuous_files(file_idx).name);
                        try
                            % Read CSV file
                            data = readtable(file_path);
                            combined_continuous = [combined_continuous; data];
                            fprintf('      Added: %s\n', continuous_files(file_idx).name);
                        catch ME
                            fprintf('      Error reading %s: %s\n', continuous_files(file_idx).name, ME.message);
                        end
                    end
                    
                    % Save combined continuous file
                    if ~isempty(combined_continuous)
                        output_filename = fullfile(subid_dir, sprintf('%s_%s_%s_continuous.csv', participant_id, run_code, trial_code));
                        writetable(combined_continuous, output_filename);
                        fprintf('    Saved combined continuous: %s\n', output_filename);
                        
                        % Delete individual files
                        for file_idx = 1:length(continuous_files)
                            file_path = fullfile(continuous_files(file_idx).folder, continuous_files(file_idx).name);
                            delete(file_path);
                            fprintf('      Deleted: %s\n', continuous_files(file_idx).name);
                        end
                    end
                end
                
                % Combine discrete files
                if ~isempty(discrete_files)
                    fprintf('    Found %d discrete files\n', length(discrete_files));
                    combined_discrete = [];
                    
                    for file_idx = 1:length(discrete_files)
                        file_path = fullfile(discrete_files(file_idx).folder, discrete_files(file_idx).name);
                        try
                            % Read CSV file
                            data = readtable(file_path);
                            combined_discrete = [combined_discrete; data];
                            fprintf('      Added: %s\n', discrete_files(file_idx).name);
                        catch ME
                            fprintf('      Error reading %s: %s\n', discrete_files(file_idx).name, ME.message);
                        end
                    end
                    
                    % Save combined discrete file
                    if ~isempty(combined_discrete)
                        output_filename = fullfile(subid_dir, sprintf('%s_%s_%s_discrete.csv', participant_id, run_code, trial_code));
                        writetable(combined_discrete, output_filename);
                        fprintf('Saved combined discrete: %s\n', output_filename);
                        
                        % Delete individual files
                        for file_idx = 1:length(discrete_files)
                            file_path = fullfile(discrete_files(file_idx).folder, discrete_files(file_idx).name);
                            delete(file_path);
                            fprintf('      Deleted: %s\n', discrete_files(file_idx).name);
                        end
                    end
                end
            end
        end
    end
    
    fprintf('\n=== DATA COMBINATION COMPLETE ===\n');
    fprintf('All trial data has been combined into single files per run type.\n');
    fprintf('Anatomical scan data has been combined into separate files.\n');
    fprintf('Individual trial files have been deleted.\n');
end

% To run the combination function manually, uncomment and modify the line below:
combine_session_data('test');  % Replace 'test' with actual participant ID
