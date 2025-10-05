function PlayMovie(movieFile, varargin)
% PlayMovie - Portable movie player with PsychToolbox
% 
% Usage: PlayMovie(movieFile, 'param', value, ...)
%
% Required:
%   movieFile - Name of movie file (will look in movies/ subdirectory)
%
% Optional parameters:
%   'scanning'     - true/false, enable scanning mode with trigger (default: false)
%   'dummyDuration'- Duration of dummy scan in seconds (default: 4)
%   'TR'          - Repetition time for scanning (default: 2)
%   'externalSound'- true/false, use external soundtrack (default: false)
%   'soundFile'   - Name of external sound file in movies/ directory (if externalSound=true)
%
% Examples:
%   PlayMovie('movie.mp4')
%   PlayMovie('movie.mp4', 'scanning', true, 'dummyDuration', 6)
%   PlayMovie('movie.mp4', 'scanning', true, 'externalSound', true, 'soundFile', 'movie_audio.wav')

% Parse input arguments
p = inputParser;
addRequired(p, 'movieFile', @ischar);
addParameter(p, 'scanning', false, @islogical);
addParameter(p, 'dummyDuration', 4, @isnumeric);
addParameter(p, 'TR', 2, @isnumeric);
addParameter(p, 'externalSound', false, @islogical);
addParameter(p, 'soundFile', '', @ischar);

parse(p, movieFile, varargin{:});

% Extract parameters
scanning = p.Results.scanning;
dummyDuration = p.Results.dummyDuration;
TR = p.Results.TR;
externalSound = p.Results.externalSound;
soundFile = p.Results.soundFile;

% Fixed parameters
resolution = [1920 1200];
fullscreen = true;
eyetracking = false;

% Get current directory for portability
currentDir = pwd;
scriptDir = fileparts(mfilename('fullpath'));

% Initialize logging structure
log = struct;
log.scriptStart = GetSecs;

try
    % Clean up any existing windows and prepare environment
    close all;
    sca;
    commandwindow;
    HideCursor;
    
    % Initialize Psychtoolbox
    PsychDefaultSetup(2);
    Screen('Preference', 'SkipSyncTests', 2);
    Screen('Preference', 'SuppressAllWarnings', 1);
    Screen('Preference', 'VisualDebuglevel', 3);
    Screen('Preference', 'VBLTimestampingMode', -20);
    Screen('Preference', 'TextEncodingLocale', 'UTF-16');
    
    % Get screen information
    screens = Screen('Screens');
    if fullscreen
        screenNumber = max(screens);
    else
        screenNumber = min(screens);
    end
    
    % Set priority for timing accuracy
    Priority(1);
    
    % Set text preferences
    Screen('Preference', 'TextAlphaBlending', 1);
    Screen('Preference', 'TextAntiAliasing', 2);
    Screen('Preference', 'TextRenderer', 1);
    
    % Define colors (standardized fixation cross format)
    red = [1 0 0];
    grey = [0.651 0.651 0.651];
    white = [1 1 1];  % WHITE (255, 255, 255) for fixation cross
    black = [0 0 0];
    background_color = [3/255 3/255 1/255];  % BACKGROUND_COLOR (3, 3, 1) - near-black
    
    % Load PsychHID for keyboard input
    LoadPsychHID;
    
    % Set up window
    if fullscreen
        windowSize = [];
    else
        windowSize = setPTBResolution(resolution(1), resolution(2), screenNumber);
    end
    
    [windowPtr, ~] = PsychImaging('OpenWindow', screenNumber, background_color, windowSize, [], [], [], 4);
    Screen('BlendFunction', windowPtr, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    % Initialize scanning setup if needed
    if scanning
        try
            s = serial('COM4', 'BaudRate', 9600);
            fopen(s);
            sync = 0;
            log.scanningEnabled = true;
        catch
            warning('Could not initialize serial connection for scanning. Continuing without scanning mode.');
            scanning = false;
            log.scanningEnabled = false;
        end
    end
    
    % Eyetracking disabled as requested
    
    % Prepare movie file path (portable) - look in movies/ subdirectory
    moviesDir = fullfile(scriptDir, 'movies');
    moviePath = fullfile(moviesDir, movieFile);
    
    if ~isfile(moviePath)
        error('Movie file not found: %s\nExpected location: %s', movieFile, moviePath);
    end
    
    % Load and prepare movie
    movie = Screen('OpenMovie', windowPtr, moviePath);
    log.movieFile = moviePath;
    
    % Prepare external sound if needed
    if externalSound && ~isempty(soundFile)
        try
            InitializePsychSound(1);
            pahandle = PsychPortAudio('Open', [], [], 2, [], 2);
            PsychPortAudio('Volume', pahandle, 0.5);
            
            soundPath = fullfile(moviesDir, soundFile);
            
            [y, Fs] = audioread(soundPath);
            wavedata = y';
            nrchannels = size(wavedata, 1);
            if nrchannels < 2
                wavedata = [wavedata; wavedata];
            end
            bufferhandle = PsychPortAudio('CreateBuffer', pahandle, wavedata);
            PsychPortAudio('FillBuffer', pahandle, bufferhandle);
            log.externalSoundEnabled = true;
        catch
            warning('Could not load external sound file. Continuing without external sound.');
            externalSound = false;
            log.externalSoundEnabled = false;
        end
    end
    
    % Wait for scanning trigger if in scanning mode
    if scanning
        disp('Waiting for scanning trigger...');
        while scanning
            sync = sync + 1;
            if strcmpi(s.PinStatus.DataSetReady, 'off')
                while strcmpi(s.PinStatus.DataSetReady, 'off')
                    % Wait for trigger
                end
            elseif strcmpi(s.PinStatus.DataSetReady, 'on')
                while strcmpi(s.PinStatus.DataSetReady, 'on')
                    % Wait for trigger to end
                end
            end
            disp(sync);
            if sync > 0
                break;
            end
        end
        log.triggerReceived = GetSecs;
    end
    
    % Eyetracking disabled as requested
    
    % Dummy scan period (4 TRs) - standardized fixation cross format
    Screen(windowPtr, 'TextSize', 200);  % Cross size: 200 pixels (standard text size equivalent)
    DrawFormattedText(windowPtr, '+', 'center', 'center', white);  % WHITE cross on near-black background
    tStartDummy = Screen('Flip', windowPtr);
    dummyDuration = 4 * TR;
    tEndDummy = Screen('Flip', windowPtr, tStartDummy + dummyDuration);
    log.tStartDummy = tStartDummy;
    log.tEndDummy = tEndDummy;
    
    % Additional fixation period (4 TRs) - standardized fixation cross format
    DrawFormattedText(windowPtr, '+', 'center', 'center', white);  % WHITE cross on near-black background
    tStartFixation = Screen('Flip', windowPtr);
    fixationDuration = 4 * TR;
    tEndFixation = Screen('Flip', windowPtr, tStartFixation + fixationDuration);
    log.tStartFixation = tStartFixation;
    log.tEndFixation = tEndFixation;
    
    % Start movie playback
    if externalSound
        Screen('PlayMovie', movie, 1, 0, 0);
        tStartMovie = GetSecs;
        PsychPortAudio('Start', pahandle, 1, 0, 1, inf, 0);
    else
        Screen('PlayMovie', movie, 1, 0, 1);
        tStartMovie = GetSecs;
    end
    log.tStartMovie = tStartMovie;
    
    % Play movie loop
    while ~KbCheck
        tex = Screen('GetMovieImage', windowPtr, movie);
        if tex <= 0
            break;
        end
        Screen('DrawTexture', windowPtr, tex);
        Screen('Flip', windowPtr);
        Screen('Close', tex);
    end
    
    % Stop movie playback
    Screen('PlayMovie', movie, 0);
    tEndMovie = GetSecs;
    Screen('CloseMovie', movie);
    log.tEndMovie = tEndMovie;
    
    % Stop external sound if used
    if externalSound
        PsychPortAudio('Stop', pahandle, 0);
        PsychPortAudio('Close');
    end
    
    % Show end screen
    Screen(windowPtr, 'TextSize', 50);
    DrawFormattedText(windowPtr, 'Movie finished. Press any key to exit...', 'center', 'center', black);
    tEndScreen = Screen('Flip', windowPtr);
    log.tEndScreen = tEndScreen;
    
    % Wait for key press to exit
    KbWait;
    
    % Eyetracking disabled as requested
    
    % Clean up scanning
    if scanning
        try
            fclose(s);
            delete(s);
            log.scanningStopped = GetSecs;
        catch
            warning('Error closing serial connection.');
        end
    end
    
    % Save log file
    log.scriptEnd = GetSecs;
    log.duration = log.scriptEnd - log.scriptStart;
    
    % Save log to current directory
    logFile = fullfile(currentDir, sprintf('movie_log_%s.mat', datestr(now, 'yyyymmdd_HHMMSS')));
    save(logFile, 'log');
    fprintf('Log saved to: %s\n', logFile);
    
catch ME
    % Error handling and cleanup
    fprintf('Error occurred: %s\n', ME.message);
    
    % Clean up resources
    try
        Screen('CloseAll');
        ShowCursor;
        if exist('s', 'var') && scanning
            fclose(s);
            delete(s);
        end
        if exist('pahandle', 'var') && externalSound
            PsychPortAudio('Close');
        end
        % Eyetracking disabled as requested
    catch
        % Ignore cleanup errors
    end
    
    rethrow(ME);
end

% Final cleanup
Screen('CloseAll');
ShowCursor;
Priority(0);

fprintf('Movie playback completed successfully.\n');

end

% Helper function for setting PTB resolution (from existing codebase)
function windowSize = setPTBResolution(x, y, screenid)
[w, h] = Screen('WindowSize', screenid);
left = (w/2) - (x/2);
right = left + x;
top = (h/2) - (y/2);
bottom = top + y;
windowSize = [left top right bottom];
end
