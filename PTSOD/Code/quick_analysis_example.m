%% Quick Analysis of Example PTSOD Data
% Analyze the LB218_PTSOD_day1.csv file as an example

clear all; close all; clc;

%% Load the example data
fprintf('Loading example data...\n');
data = readtable('Z:\sunt\Navigation\Results_Experiment_computer\Results_Desktop_tasks\LB218\s1\LB218_PTSOD_day1.csv');

fprintf('Data loaded successfully!\n');
fprintf('Number of trials: %d\n', height(data));
fprintf('Columns: %s\n', strjoin(data.Properties.VariableNames, ', '));

%% Analyze reaction times
fprintf('\n=== Reaction Time Analysis ===\n');

% Extract reaction times and memory conditions
reactionTimes = data.reactionTime;
memoryConditions = data.memory;

% Remove any invalid data
validIdx = ~isnan(reactionTimes) & reactionTimes > 0;
reactionTimes = reactionTimes(validIdx);
memoryConditions = memoryConditions(validIdx);

fprintf('Valid trials: %d\n', length(reactionTimes));

% Separate memory and non-memory conditions
memoryTrials = reactionTimes(memoryConditions == 1);
nonMemoryTrials = reactionTimes(memoryConditions == 0);

fprintf('\nMemory trials: %d\n', length(memoryTrials));
fprintf('Non-memory trials: %d\n', length(nonMemoryTrials));

%% Calculate statistics
if ~isempty(memoryTrials)
    fprintf('\nMemory Condition:\n');
    fprintf('  Mean: %.2f seconds\n', mean(memoryTrials));
    fprintf('  Median: %.2f seconds\n', median(memoryTrials));
    fprintf('  Std: %.2f seconds\n', std(memoryTrials));
    fprintf('  Min: %.2f seconds\n', min(memoryTrials));
    fprintf('  Max: %.2f seconds\n', max(memoryTrials));
    fprintf('  75th percentile: %.2f seconds\n', prctile(memoryTrials, 75));
    fprintf('  90th percentile: %.2f seconds\n', prctile(memoryTrials, 90));
    fprintf('  95th percentile: %.2f seconds\n', prctile(memoryTrials, 95));
end

if ~isempty(nonMemoryTrials)
    fprintf('\nNon-Memory Condition:\n');
    fprintf('  Mean: %.2f seconds\n', mean(nonMemoryTrials));
    fprintf('  Median: %.2f seconds\n', median(nonMemoryTrials));
    fprintf('  Std: %.2f seconds\n', std(nonMemoryTrials));
    fprintf('  Min: %.2f seconds\n', min(nonMemoryTrials));
    fprintf('  Max: %.2f seconds\n', max(nonMemoryTrials));
    fprintf('  75th percentile: %.2f seconds\n', prctile(nonMemoryTrials, 75));
    fprintf('  90th percentile: %.2f seconds\n', prctile(nonMemoryTrials, 90));
    fprintf('  95th percentile: %.2f seconds\n', prctile(nonMemoryTrials, 95));
end

%% Statistical comparison
if ~isempty(memoryTrials) && ~isempty(nonMemoryTrials)
    [h, p] = ttest2(memoryTrials, nonMemoryTrials);
    fprintf('\nT-test (Memory vs Non-Memory):\n');
    fprintf('  p-value: %.4f\n', p);
    fprintf('  Significant difference: %s\n', logical2str(h));
end

%% Overall recommendations
overallMean = mean(reactionTimes);
overallStd = std(reactionTimes);
recommendedTimer = overallMean + 2*overallStd;

fprintf('\n=== Timer Recommendations ===\n');
fprintf('Overall mean: %.2f seconds\n', overallMean);
fprintf('Overall std: %.2f seconds\n', overallStd);
fprintf('Recommended timer (mean + 2*std): %.2f seconds\n', recommendedTimer);
fprintf('Recommended timer (95th percentile): %.2f seconds\n', prctile(reactionTimes, 95));

%% Create visualization
figure('Name', 'Example PTSOD Reaction Time Analysis', 'Position', [100, 100, 1000, 600]);

% Histogram
subplot(1, 2, 1);
if ~isempty(memoryTrials)
    histogram(memoryTrials, 10, 'FaceAlpha', 0.7, 'DisplayName', 'Memory');
    hold on;
end
if ~isempty(nonMemoryTrials)
    histogram(nonMemoryTrials, 10, 'FaceAlpha', 0.7, 'DisplayName', 'Non-Memory');
end
xlabel('Reaction Time (seconds)');
ylabel('Frequency');
title('Reaction Time Distribution');
legend('Location', 'best');
grid on;

% Box plot
subplot(1, 2, 2);
if ~isempty(memoryTrials) && ~isempty(nonMemoryTrials)
    boxplot([memoryTrials, nonMemoryTrials], 'Labels', {'Memory', 'Non-Memory'});
elseif ~isempty(memoryTrials)
    boxplot(memoryTrials, 'Labels', {'Memory'});
elseif ~isempty(nonMemoryTrials)
    boxplot(nonMemoryTrials, 'Labels', {'Non-Memory'});
end
ylabel('Reaction Time (seconds)');
title('Reaction Time Comparison');
grid on;

%% Helper function
function str = logical2str(logicalVal)
    if logicalVal
        str = 'Yes';
    else
        str = 'No';
    end
end 