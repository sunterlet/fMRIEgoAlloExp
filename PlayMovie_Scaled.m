function log = PlayMovie_Scaled(participant_id, movieFile, scanning, screenNumber)
% PlayMovie_Scaled - Movie player with 75% scaling based on Ido's version
% 
% Usage: PlayMovie_Scaled(participant_id, movieFile, scanning, screenNumber)
%
% Required:
%   participant_id - Participant identifier (string or number)
%   movieFile      - Name of movie file (will look in C:\Users\fmriuser\Desktop\Sun\movies)
%   scanning       - true/false, enable scanning mode with trigger
%   screenNumber   - Screen number to use
%
% Examples:
%   PlayMovie_Scaled('P01', 'movie.mp4', true, 2)
%   PlayMovie_Scaled('P01', 'movie.mp4', false, 1)

% PTB Settings
close all; 
sca
commandwindow

%% Basic parameters
TR = 2.01;
dummyDuration = 4 * TR;
fixationDuration = 4 * TR;
moviePath = 'C:\Users\fmriuser\Desktop\Sun\movies';
fixationCrossPath = 'C:\Users\fmriuser\Desktop\Sun\fixation_cross_white_on_black.png';

first_line_code = GetSecs;

%% PTB Initialization
% Avoid Psychotoolbox synchronization test and warnings
Screen('Preference', 'SkipSyncTests', 1);
Screen('Preference', 'SuppressAllWarnings', 1);
Screen('Preference', 'VisualDebuglevel', 0);
Screen('Preference', 'Verbosity', 2);
Screen('Preference', 'SyncTestSettings', 0.002); 
PsychDefaultSetup(2);
Priority(1);
Screen('Preference', 'TextAlphaBlending', 1);
Screen('Preference', 'TextAntiAliasing', 2);
Screen('Preference', 'TextRenderer', 1);

% Define colors
red = [1 0 0];
white = WhiteIndex(screenNumber);
black = BlackIndex(screenNumber);

% Load keyboard handling
LoadPsychHID;

% Set window size
windowSize = setPTBResolution(1920, 1200, screenNumber);
[window, ~] = PsychImaging('OpenWindow', screenNumber, black, windowSize, [], [], [], 4);
Screen('BlendFunction', window, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

% Set text style
Screen('TextFont', window, 'Arial');
Screen('TextSize', window, 70);
Screen('TextColor', window, white);
Screen('TextStyle', window, 1);

%% Initialize scanning if needed
if scanning
    try
        s = serial('COM4', 'BaudRate', 9600);
        fopen(s);
        sync = 0;
        HideCursor(window);
    catch
        warning('Could not initialize serial connection for scanning. Continuing without scanning mode.');
        scanning = false;
    end
end

%% Prepare log structure
log = struct;
externalSoundtrack = false;

%% Load fixation cross image
fixationCross = imread(fixationCrossPath);
fixationTexture = Screen('MakeTexture', window, fixationCross);

%% Open movie
Screen(window, 'TextSize', 200);
movieName = fullfile(moviePath, movieFile);
movie_num = Screen('OpenMovie', window, movieName);

% Get screen dimensions
[screenWidth, screenHeight] = Screen('WindowSize', window);

% Get movie dimensions by briefly starting playback
Screen('PlayMovie', movie_num, 1, 0, 0);
WaitSecs(0.1);
tex_temp = Screen('GetMovieImage', window, movie_num, 1);
if tex_temp > 0
    [movieWidth, movieHeight] = Screen('WindowSize', tex_temp);
    Screen('Close', tex_temp);
else
    error('Could not get movie dimensions');
end
Screen('PlayMovie', movie_num, 0);
Screen('SetMovieTimeIndex', movie_num, 0);

% Calculate destination rectangle for 75% scaling with aspect ratio preserved
scaleFactor = 0.75;
scaledWidth = movieWidth * scaleFactor;
scaledHeight = movieHeight * scaleFactor;

% Center the scaled movie on screen
dstRect = CenterRectOnPointd([0 0 scaledWidth scaledHeight], ...
                              screenWidth/2, screenHeight/2);

log.movieDimensions = [movieWidth, movieHeight];
log.scaledDimensions = [scaledWidth, scaledHeight];
log.dstRect = dstRect;

%% Wait for scanner trigger if in scanning mode
if scanning
    % Show fixation cross while waiting for trigger
    Screen('DrawTexture', window, fixationTexture, [], [], 0);
    waiting_for_trigger = Screen('Flip', window);
    log.waiting_for_trigger = waiting_for_trigger;
    
    disp('Waiting for trigger...');
    while scanning
        sync = sync + 1;
        if strcmpi(s.PinStatus.DataSetReady, 'off')
            while strcmpi(s.PinStatus.DataSetReady, 'off')
                % Wait for trigger
            end 
        elseif strcmpi(s.PinStatus.DataSetReady, 'on')
            while strcmpi(s.PinStatus.DataSetReady, 'on')
                % Wait for trigger
            end
        end
        if sync > 0
            break;
        end
    end
    disp('Trigger received');
    time_mri_trigger = GetSecs;
    log.MRI_trigger = time_mri_trigger;
end

%% Dummy scan fixation (4 TRs)
Screen('DrawTexture', window, fixationTexture, [], [], 0);
first_fixation = Screen('Flip', window);
log.start_dummy_fixation = first_fixation;
WaitSecs(dummyDuration);
end_dummy_fixation = GetSecs;
log.end_dummy_fixation = end_dummy_fixation;
disp('Dummy fixation completed');

%% Initiation fixation (4 TRs)
Screen('DrawTexture', window, fixationTexture, [], [], 0);
start_init_fixation = Screen('Flip', window);
log.start_init_fixation = start_init_fixation;
WaitSecs(fixationDuration);
end_init_fixation = GetSecs;
log.end_init_fixation = end_init_fixation;
disp('Initiation fixation completed');

%% Play movie
if externalSoundtrack
    Screen('PlayMovie', movie_num, 1, 0, 0);
    tStartMovie = GetSecs;
    PsychPortAudio('Start', pahandle, 1, 0, 1, inf, 0);
else
    Screen('PlayMovie', movie_num, 1, 0, 1);
    tStartMovie = GetSecs;
end
log.tStartMovie = tStartMovie;
disp('Movie started');

% Movie playback loop with Escape key detection
escapePressed = false;
KbName('UnifyKeyNames');
escapeKey = KbName('ESCAPE');

while true
    % Check for Escape key
    [keyIsDown, ~, keyCode] = KbCheck;
    if keyIsDown && keyCode(escapeKey)
        escapePressed = true;
        break;
    end
    
    tex = Screen('GetMovieImage', window, movie_num);
    if tex <= 0
        break;
    end
    % Draw movie at 75% scale, centered
    Screen('DrawTexture', window, tex, [], dstRect);
    Screen('Flip', window);
    Screen('Close', tex);
end

% Stop playback
Screen('PlayMovie', movie_num, 0);
tEndMovie = GetSecs;
log.tEndMovie = tEndMovie;

% Close movie
Screen('CloseMovie', movie_num);

% Close soundtrack if used
if externalSoundtrack
    PsychPortAudio('Stop', pahandle, 0);
    PsychPortAudio('Close');
end

% If Escape was pressed, cleanup and exit immediately
if escapePressed
    fprintf('\nRun aborted by user (Escape pressed)\n');
    log.aborted = true;
    log.abort_time = tEndMovie;
    log.Total_Duration = tEndMovie - first_line_code;
    
    if scanning
        fclose(s);
        delete(s);
        ShowCursor(window);
    end
    
    % Save log file
    savingPath = fullfile('C:\Users\fmriuser\Desktop\Sun\Results', num2str(participant_id), 'movies');
    if ~exist(savingPath, 'dir')
        mkdir(savingPath);
    end
    
    % Extract movie name without extension
    [~, movieName_noext, ~] = fileparts(movieFile);
    logFileName = [num2str(participant_id), '_', movieName_noext, '_log_ABORTED.mat'];
    
    save(fullfile(savingPath, logFileName), 'log');
    
    Screen('CloseAll');
    ShowCursor;
    return;
end

fprintf('\nMovie ended\n');

%% End fixation (4 TRs)
Screen('DrawTexture', window, fixationTexture, [], [], 0);
tStartEndFixation = Screen('Flip', window);
log.tStartEndFixation = tStartEndFixation;
WaitSecs(fixationDuration);
tEndFixation = GetSecs;
log.tEndFixation = tEndFixation;

%% Save log and cleanup
log.Total_Duration = tEndFixation - first_line_code;

if scanning
    fclose(s);
    delete(s);
    ShowCursor(window);
end

% Save log file
savingPath = fullfile('C:\Users\fmriuser\Desktop\Sun\Results', num2str(participant_id), 'movies');
if ~exist(savingPath, 'dir')
    mkdir(savingPath);
end

% Extract movie name without extension
[~, movieName_noext, ~] = fileparts(movieFile);
logFileName = [num2str(participant_id), '_', movieName_noext, '_log.mat'];

save(fullfile(savingPath, logFileName), 'log');

Screen('CloseAll');
ShowCursor;

end

%% Helper function
function windowSize = setPTBResolution(x, y, screenid)
[w, h] = Screen('WindowSize', screenid);
left = (w/2) - (x/2);
right = left + x;
top = (h/2) - (y/2);
bottom = top + y;
windowSize = [left top right bottom];
end

