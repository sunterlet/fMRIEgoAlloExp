%% fMRI Experiment Time Calculation
% This script calculates the total time for the fMRI experiment
% Based on specifications provided

fprintf('=== fMRI EXPERIMENT TIME CALCULATION ===\n\n');

%% 1. Anatomy Scan
anatomy_time = 12.5; % Average of 10-15 minutes
fprintf('1. Anatomy Scan: %.1f minutes\n', anatomy_time);

%% 2. Rest Scans (2 x 8 minutes)
rest_time = 2 * 8;
fprintf('2. Rest Scans (2 x 8 min): %.0f minutes\n', rest_time);

%% 3. PTSOD Task
fprintf('\n3. PTSOD Task:\n');

% Memory trials: 6 trials
memory_trials = 6;
memory_memorization = 30; % seconds
memory_navigation = 35; % seconds
memory_fixation = 8; % seconds
memory_total_per_trial = memory_memorization + memory_navigation + memory_fixation;
memory_total_time = memory_trials * memory_total_per_trial / 60; % convert to minutes

fprintf('   - Memory trials: %d trials\n', memory_trials);
fprintf('     * Memorization: %d seconds\n', memory_memorization);
fprintf('     * Navigation: %d seconds\n', memory_navigation);
fprintf('     * Fixation: %d seconds\n', memory_fixation);
fprintf('     * Total per trial: %d seconds\n', memory_total_per_trial);
fprintf('     * Total memory time: %.1f minutes\n', memory_total_time);

% No memory trials: 6 trials
no_memory_trials = 6;
no_memory_navigation = 35; % seconds
no_memory_fixation = 8; % seconds
no_memory_total_per_trial = no_memory_navigation + no_memory_fixation;
no_memory_total_time = no_memory_trials * no_memory_total_per_trial / 60; % convert to minutes

fprintf('   - No memory trials: %d trials\n', no_memory_trials);
fprintf('     * Navigation: %d seconds\n', no_memory_navigation);
fprintf('     * Fixation: %d seconds\n', no_memory_fixation);
fprintf('     * Total per trial: %d seconds\n', no_memory_total_per_trial);
fprintf('     * Total no memory time: %.1f minutes\n', no_memory_total_time);

ptsod_total_time = memory_total_time + no_memory_total_time;
fprintf('   - PTSOD Total Time: %.1f minutes\n', ptsod_total_time);

%% 4. One Target - Snake Block Design
fprintf('\n4. One Target - Snake Block Design:\n');

% Updated structure: Snake - One Target - Snake - One Target - ... (intertwined)
% Total: 12 trials (6 snake + 6 one target, alternating)

% One Target: 6 trials
one_target_trials = 6;
one_target_exploration_min = 8; % seconds
one_target_exploration_max = 13; % seconds
one_target_exploration_avg = (one_target_exploration_min + one_target_exploration_max) / 2;
one_target_navigation = 15; % seconds
one_target_fixation = 8; % seconds
one_target_total_per_trial = one_target_exploration_avg + one_target_navigation + one_target_fixation;
one_target_total_time = one_target_trials * one_target_total_per_trial / 60; % convert to minutes

fprintf('   - One Target: %d trials\n', one_target_trials);
fprintf('     * Exploration: %.1f seconds (avg of %d-%d)\n', one_target_exploration_avg, one_target_exploration_min, one_target_exploration_max);
fprintf('     * Navigation: %d seconds\n', one_target_navigation);
fprintf('     * Fixation: %d seconds\n', one_target_fixation);
fprintf('     * Total per trial: %.1f seconds\n', one_target_total_per_trial);
fprintf('     * Total one target time: %.1f minutes\n', one_target_total_time);

% Snake: 6 trials
snake_trials = 6;
snake_time_min = 10; % seconds
snake_time_max = 15; % seconds
snake_time_avg = (snake_time_min + snake_time_max) / 2;
snake_total_time = snake_trials * snake_time_avg / 60; % convert to minutes

fprintf('   - Snake: %d trials\n', snake_trials);
fprintf('     * Time per trial: %.1f seconds (avg of %d-%d)\n', snake_time_avg, snake_time_min, snake_time_max);
fprintf('     * Total snake time: %.1f minutes\n', snake_total_time);

one_target_snake_total = one_target_total_time + snake_total_time;
fprintf('   - One Target-Snake Total Time: %.1f minutes\n', one_target_snake_total);

%% 5. Full Arena - Snake Block Design
fprintf('\n5. Full Arena - Snake Block Design:\n');

% Updated structure: Snake - Multi-Arena - Snake - Multi-Arena - ... (intertwined)
% Total: 12 trials (6 snake + 6 multi-arena, alternating)

% Full Arena: 6 trials
full_arena_trials = 6;
full_arena_exploration = 2 * 60; % 2 minutes in seconds
full_arena_navigation = 1 * 60; % 1 minute in seconds
full_arena_fixation = 8; % seconds
full_arena_total_per_trial = full_arena_exploration + full_arena_navigation + full_arena_fixation;
full_arena_total_time = full_arena_trials * full_arena_total_per_trial / 60; % convert to minutes

fprintf('   - Full Arena: %d trials\n', full_arena_trials);
fprintf('     * Exploration: %d minutes\n', full_arena_exploration/60);
fprintf('     * Navigation: %d minute\n', full_arena_navigation/60);
fprintf('     * Fixation: %d seconds\n', full_arena_fixation);
fprintf('     * Total per trial: %.1f minutes\n', full_arena_total_per_trial/60);
fprintf('     * Total full arena time: %.1f minutes\n', full_arena_total_time);

% Snake: 6 trials (same as above)
snake_trials_full = 6;
snake_total_time_full = snake_trials_full * snake_time_avg / 60; % convert to minutes

fprintf('   - Snake: %d trials\n', snake_trials_full);
fprintf('     * Time per trial: %.1f seconds (avg of %d-%d)\n', snake_time_avg, snake_time_min, snake_time_max);
fprintf('     * Total snake time: %.1f minutes\n', snake_total_time_full);

full_arena_snake_total = full_arena_total_time + snake_total_time_full;
fprintf('   - Full Arena-Snake Total Time: %.1f minutes\n', full_arena_snake_total);

%% 6. Total Time Calculation
fprintf('\n=== TOTAL TIME CALCULATION ===\n');

total_time = anatomy_time + rest_time + ptsod_total_time + one_target_snake_total + full_arena_snake_total;

fprintf('1. Anatomy Scan: %.1f minutes\n', anatomy_time);
fprintf('2. Rest Scans: %.0f minutes\n', rest_time);
fprintf('3. PTSOD Task: %.1f minutes\n', ptsod_total_time);
fprintf('4. One Target-Snake: %.1f minutes\n', one_target_snake_total);
fprintf('5. Full Arena-Snake: %.1f minutes\n', full_arena_snake_total);
fprintf('\nTOTAL EXPERIMENT TIME: %.1f minutes (%.1f hours)\n', total_time, total_time/60);

%% 7. Detailed Breakdown
fprintf('\n=== DETAILED BREAKDOWN ===\n');

% PTSOD breakdown
fprintf('PTSOD Breakdown:\n');
fprintf('  - Memory trials: %.1f minutes\n', memory_total_time);
fprintf('  - No memory trials: %.1f minutes\n', no_memory_total_time);
fprintf('  - PTSOD Total: %.1f minutes\n', ptsod_total_time);

% One Target breakdown
fprintf('One Target Breakdown:\n');
fprintf('  - One Target trials: %.1f minutes\n', one_target_total_time);
fprintf('  - Snake trials: %.1f minutes\n', snake_total_time);
fprintf('  - One Target-Snake Total: %.1f minutes\n', one_target_snake_total);

% Full Arena breakdown
fprintf('Full Arena Breakdown:\n');
fprintf('  - Full Arena trials: %.1f minutes\n', full_arena_total_time);
fprintf('  - Snake trials: %.1f minutes\n', snake_total_time_full);
fprintf('  - Full Arena-Snake Total: %.1f minutes\n', full_arena_snake_total);

fprintf('\n=== SUMMARY ===\n');
fprintf('Total fMRI experiment time: %.1f minutes (%.1f hours)\n', total_time, total_time/60);
fprintf('This includes all tasks, rest periods, and anatomical scan.\n'); 