function triggerExample()
% TRIGGER EXAMPLE - Example usage of extracted trigger functions
% 
% This example demonstrates how to use the extracted trigger handling
% functions from MAYA-playMovies_full.m

% Example parameters
scanning = true;  % Set to true for scanning mode
com = 'COM1';     % Serial port identifier
subID = 'test01';
group = 1;
session = 1;
runNum = 1;
movieNum = 1;
eyetracking = false;
TR = 2;           % TR in seconds
screenid = 0;     % Screen ID for PTB

try
    %% Initialize trigger
    [s, sync] = initTrigger(scanning, com);
    
    %% PTB initialization (if needed)
    if scanning
        % Initialize PsychToolbox
        PsychDefaultSetup(2);
        Screen('Preference', 'SkipSyncTests', 2);
        Screen('Preference', 'SuppressAllWarnings', 1);
        
        % Open window
        [window, ~] = Screen('OpenWindow', 0, [128 128 128]);
        HideCursor(window);
    end
    
    %% Wait for scanner trigger
    disp('Waiting for scanner trigger...');
    waitForTrigger(s, scanning);
    disp('Trigger received! Starting experiment...');
    
    %% Your experiment code here
    % This is where you would put your experimental stimuli presentation
    % For example:
    % - Present fixation cross
    % - Show cues
    % - Play movies
    % - Record responses
    
    %% Example: Simple fixation period
    if scanning
        % Draw fixation cross using standardized format (200px text size)
        Screen('TextSize', window, 200);
        DrawFormattedText(window, '+', 'center', 'center', [0 0 0]);
        Screen('Flip', window);
        
        % Wait for 4 TRs (fixation period)
        WaitSecs(TR * 4);
    end
    
    %% Clean up
    if scanning
        ShowCursor(window);
        Screen('CloseAll');
    end
    
    %% Close trigger connection
    closeTrigger(s, scanning);
    
    disp('Experiment completed successfully!');
    
catch ME
    %% Error handling
    disp(['Error: ' ME.message]);
    
    % Clean up on error
    if scanning
        ShowCursor(window);
        Screen('CloseAll');
    end
    
    % Close trigger connection
    closeTrigger(s, scanning);
    
    % Re-throw the error
    rethrow(ME);
end

end 