%% Test Simple Screen Selection
% This script demonstrates the simplified screen selection in full_sequence_exploration.m

clear; clc;

fprintf('=== Testing Simple Screen Selection ===\n\n');

% Simulate the screen selection from full_sequence_exploration.m
fprintf('=== Screen Selection ===\n');

% Get available screens
screens = Screen('Screens');
numScreens = length(screens);

fprintf('Available screens: %s\n', mat2str(screens));
fprintf('Number of screens: %d\n', numScreens);

if numScreens > 1
    fprintf('\nMultiple screens detected. Please choose:\n');
    for i = 1:numScreens
        fprintf('%d. Screen %d', i, screens(i));
        if screens(i) == 0
            fprintf(' (current screen)');
        elseif screens(i) == max(screens)
            fprintf(' (external display)');
        end
        fprintf('\n');
    end
    
    choice = input('\nSelect screen number (1-%d): ', numScreens);
    if choice >= 1 && choice <= numScreens
        selectedScreen = screens(choice);
        fprintf('Selected screen: %d\n', selectedScreen);
    else
        fprintf('Invalid choice, using screen 0 (current screen)\n');
        selectedScreen = 0;
    end
else
    fprintf('Only one screen available, using screen 0\n');
    selectedScreen = 0;
end

% Validate screen selection
try
    [window, windowRect] = Screen('OpenWindow', selectedScreen, [1 1 1], [0 0 100 100]);
    Screen('Close', window);
    fprintf('✅ Screen %d is valid and accessible\n', selectedScreen);
catch ME
    fprintf('❌ Error accessing screen %d: %s\n', selectedScreen, ME.message);
    fprintf('Falling back to screen 0...\n');
    selectedScreen = 0;
end

fprintf('=== Screen Selection Complete ===\n\n');

% Test that the screen number can be passed to PTSOD functions
fprintf('=== Testing Function Integration ===\n');
fprintf('The selected screen (%d) would be passed to:\n', selectedScreen);
fprintf('- PTSODfunc_SplitDays_fMRI_New(SubID, day, ''practice'', %d)\n', selectedScreen);
fprintf('- PTSODfunc_SplitDays_fMRI_New(SubID, day, ''fMRI'', %d)\n', selectedScreen);
fprintf('- DisplayInst_fMRI(instructions, %d)\n', selectedScreen);
fprintf('- PTSODfuncICONSheb_Practice(..., %d)\n', selectedScreen);
fprintf('- PTSODfuncICONSheb_fMRI_Test(..., %d)\n', selectedScreen);

fprintf('\n✅ Simple screen selection test completed!\n');
fprintf('You can now run full_sequence_exploration.m and it will ask for screen selection once.\n'); 