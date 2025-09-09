%% Calculate Trial Timer in TRs
% Calculate how many TRs correspond to 35 seconds for the trial timer

clear all; clc;

%% Parameters
TR = 2.01;  % Repetition Time in seconds
trialTimer = 35;  % Trial timer in seconds

%% Calculate
numTRs = trialTimer / TR;

fprintf('=== Trial Timer Calculation ===\n');
fprintf('TR: %.2f seconds\n', TR);
fprintf('Trial Timer: %.0f seconds\n', trialTimer);
fprintf('Number of TRs: %.2f\n', numTRs);
fprintf('Rounded to nearest TR: %.0f TRs\n', round(numTRs));

%% Additional calculations
fprintf('\n=== Additional Information ===\n');
fprintf('35 seconds = %.1f TRs\n', numTRs);
fprintf('17 TRs = %.1f seconds\n', 17 * TR);
fprintf('18 TRs = %.1f seconds\n', 18 * TR);

%% For fMRI timing precision
fprintf('\n=== fMRI Timing Considerations ===\n');
fprintf('For precise fMRI timing, you might want to use:\n');
fprintf('  - 17 TRs = %.1f seconds (slightly under 35s)\n', 17 * TR);
fprintf('  - 18 TRs = %.1f seconds (slightly over 35s)\n', 18 * TR);

if numTRs > 17 && numTRs < 18
    fprintf('\nRecommendation: Use 17 TRs (%.1f seconds) to stay under 35s\n', 17 * TR);
else
    fprintf('\nRecommendation: Use %.0f TRs\n', round(numTRs));
end 