function selectedScreen = select_screen()
%% Screen Selection Function
% This function handles screen selection with visual identification
% Returns: selectedScreen - the chosen screen number

% Initialize Psychtoolbox
PsychDefaultSetup(2);
Screen('Preference', 'SkipSyncTests', 2);
Screen('Preference', 'SuppressAllWarnings', 1);
Screen('Preference', 'VisualDebuglevel', 3);
Screen('Preference', 'VBLTimestampingMode', -20);
Screen('Preference', 'TextEncodingLocale', 'UTF-16');

fprintf('\n=== Screen Selection ===\n');
screens = Screen('Screens');
numScreens = length(screens);

fprintf('Available screens: %s\n', mat2str(screens));
fprintf('Number of screens: %d\n', numScreens);

% Display test pattern on each screen for identification
fprintf('\n=== Displaying Test Patterns ===\n');
fprintf('A test pattern will be shown on each screen for 3 seconds.\n');
fprintf('Look at each screen to identify which one you want to use.\n\n');

for i = 1:numScreens
    screenNum = screens(i);
    fprintf('Showing test pattern on Screen %d...\n', screenNum);
    
    try
        % Open window on this screen
        [window, rect] = Screen('OpenWindow', screenNum, [128 128 128]);
        
        % Get screen dimensions
        [width, height] = Screen('WindowSize', window);
        
        % Create test pattern
        Screen('TextSize', window, 48);
        Screen('TextFont', window, 'Arial');
        Screen('TextColor', window, [255 255 255]);
        
        % Draw screen identification text
        DrawFormattedText(window, sprintf('SCREEN %d\n\nResolution: %dx%d\n\nThis is a test pattern\n\nPress any key to continue', ...
            screenNum, width, height), 'center', 'center');
        
        % Draw a colored border
        borderColor = [255 0 0]; % Red for screen 0, different colors for others
        if screenNum == 0
            borderColor = [255 0 0]; % Red
        elseif screenNum == max(screens)
            borderColor = [0 255 0]; % Green
        else
            borderColor = [0 0 255]; % Blue
        end
        
        Screen('FrameRect', window, borderColor, rect, 10);
        
        % Show the pattern
        Screen('Flip', window);
        
        % Wait for 3 seconds or key press
        WaitSecs(3);
        
        % Close window
        Screen('Close', window);
        
    catch ME
        fprintf('  Error displaying on Screen %d: %s\n', screenNum, ME.message);
    end
end

fprintf('\nTest patterns completed.\n');

% Get detailed information about each screen
for i = 1:numScreens
    screenNum = screens(i);
    fprintf('\n--- Screen %d ---\n', screenNum);
    
    % Get screen resolution
    try
        [width, height] = Screen('WindowSize', screenNum);
        fprintf('  Resolution: %dx%d\n', width, height);
    catch
        fprintf('  Resolution: Unable to determine\n');
    end
    
    % Get screen properties
    try
        rect = Screen('Rect', screenNum);
        fprintf('  Rect: [%d %d %d %d]\n', rect(1), rect(2), rect(3), rect(4));
    catch
        fprintf('  Rect: Unable to determine\n');
    end
    
    % Get refresh rate
    try
        refreshRate = Screen('NominalFrameRate', screenNum);
        if refreshRate > 0
            fprintf('  Refresh Rate: %.1f Hz\n', refreshRate);
        else
            fprintf('  Refresh Rate: Unknown\n');
        end
    catch
        fprintf('  Refresh Rate: Unable to determine\n');
    end
    
    % Get screen position information
    try
        [x, y] = Screen('WindowSize', screenNum);
        fprintf('  Position: [%d, %d]\n', x, y);
    catch
        fprintf('  Position: Unable to determine\n');
    end
end

if numScreens > 1
    fprintf('\nMultiple screens detected. Please choose:\n');
    fprintf('Note: Screen 0 may span multiple displays in some configurations.\n');
    for i = 1:numScreens
        fprintf('%d. Screen %d', i, screens(i));
        fprintf('\n');
    end
    
    choice = input(sprintf('\nSelect screen number (1-%d): ', numScreens));
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

end 