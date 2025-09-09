function [dataTable,filename] = PTSODfunc_SplitDays_fMRI_New(SubID, day, sessionType, screenNumber, scanning, com, TR)
%% RUN: 
% PTSODfunc_SplitDays_fMRI_New(SubID, day, sessionType, screenNumber, scanning, com, TR) 
% - SubID: initials and 3 last ID digits (example: 'TS263')
% - day: 1 or 2
% - sessionType: 'practice' for outside magnet, 'fMRI' for inside magnet
% - screenNumber: screen number to use for display (optional)
% - scanning: boolean for fMRI scanning mode (optional, default false)
% - com: serial port for trigger (optional, default 'COM1')
% - TR: repetition time in seconds (optional, default 2)
% 
% PORTABLE VERSION - Can run from any computer

    %% PTSOD fMRI Experiment - New Version
                         
    %% Setting up environment   
          
    % Clear the workspace and the screen 
    sca;      
    
    % Set up portable paths
    [projectRoot, result_path, stimuliPath, instructionsPath] = setupPTSOD();

    % Set up paths relative to the project root
    directory_nomemory = fullfile(stimuliPath, 'nomemory_screens');
    directory_memory   = fullfile(stimuliPath, 'memory_screens');
    
    %% Setting lists and variables
    
    % Set results list
    examples = 3;  
    trials = 12;
    
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
        fprintf('Starting PRACTICE session for %s, Day %d\n', SubID, day);
        
        while Instructions == 1 
         
            % General instructions & no memory instructions
            Instructions = DisplayInst_fMRI(files_inst(1:6), screenNumber);
            if Instructions == -1
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
                return;
            end
            
            % no memory example
            [nomemory_example1, exit_early] = PTSODfuncICONSheb_Practice(fileNames_dir_examples(1,:), trials, result_path, SubID, day, 'practice_example1', screenNumber);
            if exit_early
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
                return;
            end
            
            % second nomemory example
            Instructions = DisplayInst_fMRI(files_inst(7), screenNumber);
            if Instructions == -1
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
                return;
            end
            
            [nomemory_example2, exit_early] = PTSODfuncICONSheb_Practice(fileNames_dir_examples(2,:), trials, result_path, SubID, day, 'practice_example2', screenNumber);
            if exit_early
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
                return;
            end
            
            % Memory instructions 
            Instructions = DisplayInst_fMRI(files_inst(8), screenNumber);
            if Instructions == -1
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
                return;
            end
            
            % memory example
            [memory_example, exit_early] = PTSODfuncICONSheb_Practice(fileNames_dir_examples(3,:), trials, result_path, SubID, day, 'practice_example3', screenNumber);
            if exit_early
                % Combine any partial data and exit
                [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
                return;
            end
            
            % Break after memory example (no final instructions in practice)
            break;
        end
        
        %% Thank you screen for practice
        DisplayInst_fMRI(files_inst(11), screenNumber);
        overallTime = toc;
        sca
        
    elseif strcmp(sessionType, 'fMRI')
        %% fMRI SESSION (Inside Magnet)
        fprintf('Starting fMRI session for %s, Day %d\n', SubID, day);
        
        % Brief instructions before fMRI session
        Instructions = DisplayInst_fMRI(files_inst(9), screenNumber);
        if Instructions == -1
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
            return;
        end
        
        % Run one no-memory example in fMRI (NO fixation point after example)
        [fMRI_example, exit_early] = PTSODfuncICONSheb_fMRI_Test_Trigger(fileNames_dir_examples(1,:), trials, result_path, SubID, day, 'fMRI_example', screenNumber, false, com, TR);
        if exit_early
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
            return;
        end

        % Brief instructions after fMRI example
        Instructions = DisplayInst_fMRI(files_inst(10), screenNumber);
        if Instructions == -1
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
            return;
        end
        
        %% EXP - Test trials (with trigger functionality)
        if day == 1
            test_trials = fileNames_dir_test(1:2:end,:); % Odd trials for day 1
        else
            test_trials = fileNames_dir_test(2:2:end,:); % Even trials for day 2
        end
        
        fprintf('Running %d test trials for Day %d\n', size(test_trials,1), day);
        
        % Only enable scanning (trigger) for test trials inside the scanner
        [trial_data, exit_early] = PTSODfuncICONSheb_fMRI_Test_Trigger(test_trials, size(test_trials,1), result_path, SubID, day, 'fMRI_test', screenNumber, scanning, com, TR);
        if exit_early
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, false);
            return;
        end
        
        %% Thank you screen for fMRI
        DisplayInst_fMRI(files_inst(11), screenNumber);
        overallTime = toc;
        sca

    end
    
    % Combine all data at the end
    [dataTable, filename] = combinePartialData(result_path, SubID, day, toc, sessionType, true);
    
end 