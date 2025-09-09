%% Analyze PTSOD Reaction Times
% This script analyzes reaction times from PTSOD experiment results
% to calculate average completion times for memory and non-memory conditions

clear all; close all; clc;

%% Setup
% Define the results directory
resultsDir = 'Z:\sunt\Navigation\Results_Experiment_computer\Results_Desktop_tasks';

% Initialize data storage
allReactionTimes = [];
allMemoryConditions = [];
allParticipants = {};
allSessions = {};

%% Find all PTSOD files
fprintf('Searching for PTSOD files...\n');

% Get all participant directories
participantDirs = dir(resultsDir);
participantDirs = participantDirs([participantDirs.isdir]);
participantDirs = participantDirs(~ismember({participantDirs.name}, {'.', '..', '.DS_Store'}));

totalFiles = 0;
processedFiles = 0;

for p = 1:length(participantDirs)
    participant = participantDirs(p).name;
    participantPath = fullfile(resultsDir, participant);
    
    % Check for s1 and s2 subdirectories
    for session = {'s1', 's2'}
        sessionPath = fullfile(participantPath, session{1});
        
        if exist(sessionPath, 'dir')
            % Look for PTSOD files
            files = dir(fullfile(sessionPath, '*PTSOD*.csv'));
            
            for f = 1:length(files)
                totalFiles = totalFiles + 1;
                filePath = fullfile(sessionPath, files(f).name);
                
                try
                    % Read the CSV file
                    fprintf('Processing: %s\n', filePath);
                    
                    % Read CSV data
                    data = readtable(filePath);
                    
                    % Extract reaction times and memory conditions
                    if ismember('reactionTime', data.Properties.VariableNames) && ...
                       ismember('memory', data.Properties.VariableNames)
                        
                        reactionTimes = data.reactionTime;
                        memoryConditions = data.memory;
                        
                        % Remove any invalid data (NaN, negative values)
                        validIdx = ~isnan(reactionTimes) & reactionTimes > 0;
                        reactionTimes = reactionTimes(validIdx);
                        memoryConditions = memoryConditions(validIdx);
                        
                        % Store data
                        allReactionTimes = [allReactionTimes; reactionTimes(:)];
                        allMemoryConditions = [allMemoryConditions; memoryConditions(:)];
                        
                        % Store participant and session info
                        numTrials = length(reactionTimes);
                        allParticipants = [allParticipants; repmat({participant}, numTrials, 1)];
                        allSessions = [allSessions; repmat(session, numTrials, 1)];
                        
                        processedFiles = processedFiles + 1;
                        
                        fprintf('  - Found %d valid trials\n', numTrials);
                    else
                        fprintf('  - Missing required columns (reactionTime or memory)\n');
                    end
                    
                catch ME
                    fprintf('  - Error reading file: %s\n', ME.message);
                end
            end
        end
    end
end

fprintf('\nProcessed %d out of %d files\n', processedFiles, totalFiles);

%% Analyze the data
if ~isempty(allReactionTimes)
    fprintf('\n=== Analysis Results ===\n');
    
    % Convert to arrays for easier analysis
    reactionTimes = allReactionTimes;  % Already numeric array
    memoryConditions = allMemoryConditions;  % Already numeric array
    
    % Separate memory and non-memory conditions
    memoryTrials = reactionTimes(memoryConditions == 1);
    nonMemoryTrials = reactionTimes(memoryConditions == 0);
    
    % Calculate statistics
    fprintf('Memory Condition (n = %d):\n', length(memoryTrials));
    fprintf('  Mean: %.2f seconds\n', mean(memoryTrials));
    fprintf('  Median: %.2f seconds\n', median(memoryTrials));
    fprintf('  Std: %.2f seconds\n', std(memoryTrials));
    fprintf('  Min: %.2f seconds\n', min(memoryTrials));
    fprintf('  Max: %.2f seconds\n', max(memoryTrials));
    
    fprintf('\nNon-Memory Condition (n = %d):\n', length(nonMemoryTrials));
    fprintf('  Mean: %.2f seconds\n', mean(nonMemoryTrials));
    fprintf('  Median: %.2f seconds\n', median(nonMemoryTrials));
    fprintf('  Std: %.2f seconds\n', std(nonMemoryTrials));
    fprintf('  Min: %.2f seconds\n', min(nonMemoryTrials));
    fprintf('  Max: %.2f seconds\n', max(nonMemoryTrials));
    
    % Statistical test
    [h, p] = ttest2(memoryTrials, nonMemoryTrials);
    fprintf('\nT-test (Memory vs Non-Memory):\n');
    fprintf('  p-value: %.4f\n', p);
    fprintf('  Significant difference: %s\n', logical2str(h));
    
    % Calculate percentiles for timer setting
    fprintf('\n=== Timer Recommendations ===\n');
    fprintf('For Memory trials:\n');
    fprintf('  75th percentile: %.2f seconds\n', prctile(memoryTrials, 75));
    fprintf('  90th percentile: %.2f seconds\n', prctile(memoryTrials, 90));
    fprintf('  95th percentile: %.2f seconds\n', prctile(memoryTrials, 95));
    
    fprintf('\nFor Non-Memory trials:\n');
    fprintf('  75th percentile: %.2f seconds\n', prctile(nonMemoryTrials, 75));
    fprintf('  90th percentile: %.2f seconds\n', prctile(nonMemoryTrials, 90));
    fprintf('  95th percentile: %.2f seconds\n', prctile(nonMemoryTrials, 95));
    
    % Overall recommendations
    overallMean = mean(reactionTimes);
    overallStd = std(reactionTimes);
    recommendedTimer = overallMean + 2*overallStd; % 2 standard deviations
    
    fprintf('\n=== Overall Recommendations ===\n');
    fprintf('Overall mean: %.2f seconds\n', overallMean);
    fprintf('Recommended timer (mean + 2*std): %.2f seconds\n', recommendedTimer);
    fprintf('Recommended timer (95th percentile): %.2f seconds\n', prctile(reactionTimes, 95));
    
    %% Create visualizations
    figure('Name', 'PTSOD Reaction Time Analysis', 'Position', [100, 100, 1200, 800]);
    
    % Histogram comparison
    subplot(2, 2, 1);
    histogram(memoryTrials, 20, 'FaceAlpha', 0.7, 'DisplayName', 'Memory');
    hold on;
    histogram(nonMemoryTrials, 20, 'FaceAlpha', 0.7, 'DisplayName', 'Non-Memory');
    xlabel('Reaction Time (seconds)');
    ylabel('Frequency');
    title('Reaction Time Distribution');
    legend('Location', 'best');
    grid on;
    
    % Box plot
    subplot(2, 2, 2);
    boxplot([memoryTrials, nonMemoryTrials], 'Labels', {'Memory', 'Non-Memory'});
    ylabel('Reaction Time (seconds)');
    title('Reaction Time Comparison');
    grid on;
    
    % Cumulative distribution
    subplot(2, 2, 3);
    [f1, x1] = ecdf(memoryTrials);
    [f2, x2] = ecdf(nonMemoryTrials);
    plot(x1, f1, 'LineWidth', 2, 'DisplayName', 'Memory');
    hold on;
    plot(x2, f2, 'LineWidth', 2, 'DisplayName', 'Non-Memory');
    xlabel('Reaction Time (seconds)');
    ylabel('Cumulative Probability');
    title('Cumulative Distribution');
    legend('Location', 'best');
    grid on;
    
    % Participant-level analysis
    subplot(2, 2, 4);
    uniqueParticipants = unique(allParticipants);
    participantMeans = zeros(length(uniqueParticipants), 2);
    
    for p = 1:length(uniqueParticipants)
        participant = uniqueParticipants{p};
        participantIdx = strcmp(allParticipants, participant);
        
        participantMemory = reactionTimes(participantIdx & memoryConditions == 1);
        participantNonMemory = reactionTimes(participantIdx & memoryConditions == 0);
        
        if ~isempty(participantMemory)
            participantMeans(p, 1) = mean(participantMemory);
        end
        if ~isempty(participantNonMemory)
            participantMeans(p, 2) = mean(participantNonMemory);
        end
    end
    
    % Remove participants with no data
    validIdx = any(participantMeans > 0, 2);
    participantMeans = participantMeans(validIdx, :);
    
    bar(participantMeans);
    xlabel('Participant');
    ylabel('Mean Reaction Time (seconds)');
    title('Participant-Level Analysis');
    legend('Memory', 'Non-Memory', 'Location', 'best');
    grid on;
    
    % Save results
    results = struct();
    results.memoryTrials = memoryTrials;
    results.nonMemoryTrials = nonMemoryTrials;
    results.memoryMean = mean(memoryTrials);
    results.nonMemoryMean = mean(nonMemoryTrials);
    results.recommendedTimer = recommendedTimer;
    results.recommendedTimer95 = prctile(reactionTimes, 95);
    
    save('PTSOD_reaction_time_analysis.mat', 'results');
    fprintf('\nResults saved to: PTSOD_reaction_time_analysis.mat\n');
    
else
    fprintf('No valid data found!\n');
end

%% Helper function
function str = logical2str(logicalVal)
    if logicalVal
        str = 'Yes';
    else
        str = 'No';
    end
end 