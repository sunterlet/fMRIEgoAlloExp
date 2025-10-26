function [dataTable,filename] = PTSODfunc_SplitRuns_fMRI_New(SubID, run, sessionType, screenNumber, scanning, com, TR)
%% RUN: 
% PTSODfunc_SplitRuns_fMRI_New(SubID, day, sessionType, screenNumber, scanning, com, TR) 
% - SubID: initials and 3 last ID digits (example: 'TS263')
% - day: 1 or 2
% - sessionType: 'practice' for outside magnet, 'fMRI' for inside magnet
% - screenNumber: screen number to use for display (optional)
% - scanning: boolean for fMRI scanning mode (optional, default false)
% - com: serial port for trigger (optional, default 'COM1')
% - TR: repetition time in seconds (optional, default 2)
% 
% STANDARDIZED FIXATION CROSS FORMAT:
% - Cross size: 200 pixels (standard text size)
% - Cross color: BLACK [0 0 0] on WHITE background [255 255 255]
% - Uses DrawFormattedText for consistent rendering
% - Note: Exploration experiments use WHITE cross on BLACK background with same dimensions
% 
% PORTABLE VERSION - Can run from any computer

    %% PTSOD fMRI Experiment - New Version
                         
    %% Setting up environment   
          
    % Clear the workspace and the screen 
    sca;
    
    % Initialize Psychtoolbox with synchronization preferences to prevent errors
    PsychDefaultSetup(2);
    Screen('Preference', 'SkipSyncTests', 1);
    Screen('Preference', 'SuppressAllWarnings', 1);
    
    % Initialize Psychtoolbox functions
    InitializePsychSound;
    KbName('UnifyKeyNames');      
    
    % Set up portable paths
    [projectRoot, result_path, stimuliPath, instructionsPath] = setupPTSOD();

    % Set up paths relative to the project root
    directory_nomemory = fullfile(stimuliPath, 'nomemory_screens');
    directory_memory   = fullfile(stimuliPath, 'memory_screens');
    
    %% Setting lists and variables
    
    % Set results list
    examples = 3;  
    trials = 8;  % 8 trials per run (4 memory + 4 no-memory)
    
    % Get the list of files in the directory
    files_nomemory = dir(fullfile(directory_nomemory, '*.png'));
    files_memory = dir(fullfile(directory_memory, '*.png'));
    
    % Extract only the file names and filter out AppleDouble metadata files (._*)
    fileNames_nomemory = {files_nomemory(~[files_nomemory.isdir]).name}';
    fileNames_memory = {files_memory(~[files_memory.isdir]).name}';
    
    % Filter out AppleDouble metadata files (files starting with "._")
    fileNames_nomemory = fileNames_nomemory(~startsWith(fileNames_nomemory, '._'));
    fileNames_memory = fileNames_memory(~startsWith(fileNames_memory, '._'));
    
    % Create a list with names and memory info (nomemory = 0, memory = 1)
    fileNames_nomemory_dir = fileNames_nomemory;
    fileNames_nomemory_dir(:,2) = {0};
    
    fileNames_memory_dir = fileNames_memory;
    fileNames_memory_dir(:,2) = {1};
    
    fileNames_dir_all = [fileNames_nomemory_dir;fileNames_memory_dir];
    examples_dir = contains(fileNames_dir_all(:,1),'example');
    
    fileNames_dir_test = fileNames_dir_all(~examples_dir,:);
    fileNames_dir_examples = fileNames_dir_all(examples_dir,:);
    
    %% Instructions and examples
    
    % Get the instruction file names and filter out AppleDouble metadata files
    files_inst = dir( fullfile(instructionsPath, 'instructions_practice_fmri1', '*.png'));
    files_inst = {files_inst(~[files_inst.isdir]).name}';
    % Filter out AppleDouble metadata files from instructions
    files_inst = files_inst(~startsWith(files_inst, '._'));
    Instructions = 1;    
    
    tic;
    
    if strcmp(sessionType, 'practice')
        %% PRACTICE SESSION (Outside Magnet)
        fprintf('Starting PRACTICE session for %s, Run %d\n', SubID, run);
        
        while Instructions == 1 
         
            % General instructions & no memory instructions
            Instructions = DisplayInst_fMRI(files_inst(1:6), screenNumber);
            if Instructions == -1
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
                return;
            end
            
            % no memory example
            [nomemory_example1, exit_early] = PTSODfuncICONSheb_Practice(fileNames_dir_examples(1,:), trials, result_path, SubID, run, 'practice_example1', screenNumber);
            if exit_early
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
                return;
            end
            
            % second nomemory example
            Instructions = DisplayInst_fMRI(files_inst(7), screenNumber);
            if Instructions == -1
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
                return;
            end
            
            [nomemory_example2, exit_early] = PTSODfuncICONSheb_Practice(fileNames_dir_examples(2,:), trials, result_path, SubID, run, 'practice_example2', screenNumber);
            if exit_early
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
                return;
            end
            
            % Memory instructions 
            Instructions = DisplayInst_fMRI(files_inst(8), screenNumber);
            if Instructions == -1
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
                return;
            end
            
            % memory example
            [memory_example, exit_early] = PTSODfuncICONSheb_Practice(fileNames_dir_examples(3,:), trials, result_path, SubID, run, 'practice_example3', screenNumber);
            if exit_early
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
                return;
            end
            
            % Break after memory example (no final instructions in practice)
            break;
        end
        
        %% Thank you screen for practice
        DisplayInst_fMRI(files_inst(11), screenNumber);
        overallTime = toc;
        sca;
        
    elseif strcmp(sessionType, 'fMRI')
        %% fMRI SESSION (Inside Magnet)
        fprintf('Starting fMRI session for %s, Run %d\n', SubID, run);
        
        % Brief instructions before fMRI session
        Instructions = DisplayInst_fMRI(files_inst(9), screenNumber);
        if Instructions == -1
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
            return;
        end
        
        % Run one no-memory example in fMRI (NO fixation point after example) - ONLY for run 1
        if run == 1
            [fMRI_example, exit_early] = PTSODfuncICONSheb_fMRI_Test_Trigger(fileNames_dir_examples(1,:), trials, result_path, SubID, run, 'fMRI_example', screenNumber, false, com, TR);
            if exit_early
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
                return;
            end

            % Brief instructions after fMRI example
            Instructions = DisplayInst_fMRI(files_inst(10), screenNumber);
            if Instructions == -1
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
                return;
            end
        else
            fprintf('Skipping example trial for run %d (instructions and 8 test trials only)\n', run);
        end
        
        %% EXP - Test trials (with trigger functionality)
        % Separate memory and no-memory trials
        memory_trials = fileNames_dir_test([fileNames_dir_test{:,2}] == 1, :);
        nomemory_trials = fileNames_dir_test([fileNames_dir_test{:,2}] == 0, :);
        
        fprintf('Total memory trials available: %d\n', size(memory_trials,1));
        fprintf('Total no-memory trials available: %d\n', size(nomemory_trials,1));
        
        if run == 1
            % For run 1, take first 4 memory and first 4 no-memory trials
            test_trials = [memory_trials(1:4, :); nomemory_trials(1:4, :)];
        else
            % For run 2, take remaining memory and no-memory trials (no overlap)
            test_trials = [memory_trials(5:8, :); nomemory_trials(5:8, :)];
        end
        
        fprintf('Running %d test trials for Run %d (4 memory + 4 no-memory)\n', size(test_trials,1), run);
        
        % Only enable scanning (trigger) for test trials inside the scanner
        [trial_data, exit_early] = PTSODfuncICONSheb_fMRI_Test_Trigger(test_trials, size(test_trials,1), result_path, SubID, run, 'fMRI_test', screenNumber, scanning, com, TR);
        if exit_early
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, false);
            return;
        end
        
        %% Note: TR alignment and inter-trial fixation handled by PTSODfuncICONSheb_fMRI_Test_Trigger
        fprintf('TR alignment and inter-trial fixation already handled by trial function.\n');
        fprintf('Final 4 TR fixation also handled by trial function after last trial.\n');
        
        %% Thank you screen for fMRI
        DisplayInst_fMRI(files_inst(11), screenNumber);
        overallTime = toc;
        sca;

    end
    
    % Combine all data at the end
    [dataTable, filename] = combinePartialData(result_path, SubID, run, toc, sessionType, true);
    
    % Clean up screen
    sca;
    
end 