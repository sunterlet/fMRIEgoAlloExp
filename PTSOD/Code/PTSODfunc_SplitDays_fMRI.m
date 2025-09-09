function [dataTable,filename] = PTSODfunc_SplitDays_fMRI(SubID, day)
%% RUN: 
% cd E:\Sun\Navigation\DesktopTasks\PTSOD\Code
% PTSODfunc_SplitDays(SubID, day) - SubID - initials and 3 last ID digits (example: 'TS263'), day: 1 or 2.
    %% PTSOD Desktop Experiment
                         
    %% Setting up enviroment   
          
    % Clear the workspace and the screen 
    sca;      
%      close all;          
%      clc; clear;            
    
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
    
    % Extract only the file names
    fileNames_nomemory = {files_nomemory(~[files_nomemory.isdir]).name}';
    fileNames_memory = {files_memory(~[files_memory.isdir]).name}';
    
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
    
    % Get the instruction file names
    files_inst = dir(fullfile(scriptDir, 'Instructions_HE', '*.png'));
    files_inst = {files_inst(~[files_inst.isdir]).name}';
    Instructions = 1;    
    
    tic;
    while Instructions == 1 
     
        % General instructions & no memory instructions
        Instructions = DisplayInst_fMRI(files_inst(1:6),2);
        if Instructions == -1
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
        
        % no memory example
        [nomemory_example1, exit_early] = PTSODfuncICONSheb_fMRI(fileNames_dir_examples(1,:), trials, result_path, SubID, day, 'example1');
        if exit_early
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
        
        % second nomemory example
        Instructions = DisplayInst_fMRI(files_inst(7),2);
        if Instructions == -1
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
        
        [nomemory_example2, exit_early] = PTSODfuncICONSheb_fMRI(fileNames_dir_examples(2,:), trials, result_path, SubID, day, 'example2');
        if exit_early
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
        
        % Memory instructions 
        Instructions = DisplayInst_fMRI(files_inst(8),2);
        if Instructions == -1
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
        
        % memory example
        [memory_example, exit_early] = PTSODfuncICONSheb_fMRI(fileNames_dir_examples(3,:), trials, result_path, SubID, day, 'example3');
        if exit_early
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
        
        % Final instructions 
        Instructions = DisplayInst_fMRI(files_inst(9),2);
        if Instructions == -1
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
        if Instructions == 0
            break;
        end
    end
    
    %% EXP
    
     if day == 1
        [test_results, exit_early] = PTSODfuncICONSheb_fMRI(fileNames_dir_test(1:2:end,:), trials, result_path, SubID, day, 'test');
        if exit_early
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
    elseif day == 2
        [test_results, exit_early] = PTSODfuncICONSheb_fMRI(fileNames_dir_test(2:2:end,:), trials, result_path, SubID, day, 'test');
        if exit_early
            % Combine any partial data and exit
            [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
            return;
        end
    end

    %% Thank you screen
    
    DisplayInst_fMRI(files_inst(10),2);
    if Instructions == -1
        % Combine any partial data and exit
        [dataTable, filename] = combinePartialData(result_path, SubID, day, toc);
        return;
    end
    overallTime = toc;
    sca
    
    %% Combine all saved trial data
    
    % Load and combine all trial data
    allTrialFiles = dir(fullfile(result_path, sprintf('%s_PTSOD_day%d_*.mat', SubID, day)));
    
    if isempty(allTrialFiles)
        % No trial files found, create empty table
        dataTable = table();
        filename = '';
        return;
    end
    
    % Initialize combined data
    combinedData = {};
    
    % Load each trial file and extract data
    for i = 1:length(allTrialFiles)
        trialFile = fullfile(result_path, allTrialFiles(i).name);
        loadedData = load(trialFile);
        
        if isfield(loadedData, 'trialData')
            % Extract the trial data
            trialRow = loadedData.trialData;
            
            % Parse arena name to get numObjects and level
            arenaName = trialRow{1};
            numbers = regexp(arenaName, '\d+', 'match');
            numbers = cellfun(@str2double, numbers);
            num_objects = numbers(1);
            if length(numbers) == 1
                level = 0;
            else
                level = numbers(2);
            end
            
            % Convert string values to numeric
            angle = str2double(trialRow{3});
            relDist = str2double(trialRow{4});
            correctAngle = str2double(trialRow{5});
            correctRelDist = str2double(trialRow{6});
            errorAngle = str2double(trialRow{7});
            errorRelDist = str2double(trialRow{8});
            reactionTime = str2double(trialRow{9});
            skiptime = str2double(trialRow{10});
            order = str2double(trialRow{11});
            xMouse = str2double(trialRow{12});
            yMouse = str2double(trialRow{13});
            
            % Create row data
            rowData = {arenaName, num_objects, level, trialRow{2}, angle, relDist, correctAngle, correctRelDist, errorAngle, errorRelDist, reactionTime, skiptime, overallTime, order, xMouse, yMouse};
            combinedData = [combinedData; rowData];
        end
    end
    
    % Create final data table
    headers = {'arena','numObjects', 'level', 'memory', 'angle', 'relDist', 'correctAngle', 'correctRelDist', 'errorAngle', 'errorRelDist', 'reactionTime', 'skiptime', 'overallTime', 'order','xMouse','yMouse'};
    
    if ~isempty(combinedData)
        dataTable = cell2table(combinedData, 'VariableNames', headers);
    else
        dataTable = table();
    end
    
    % Save combined data
    suffix = 0;
    filename = fullfile(result_path, [SubID '_PTSOD_day' num2str(day) '.mat']);
    while exist(filename, 'file')
        suffix = suffix + 1;
        filename = fullfile(result_path, [SubID '_PTSOD_day' num2str(day) '_' num2str(suffix) '.mat']);
    end
    save(filename, 'dataTable');
    
end