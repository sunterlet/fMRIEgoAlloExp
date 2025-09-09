function [results, exit_early] = PTSODfuncICONSheb_fMRI_Test_Trigger(filesList, trials, saveDir, SubID, day, trialType, screenNumber, scanning, com, TR)
% fMRI Test version with trigger functionality - includes fixation crosses for fMRI scanning
%
% STANDARDIZED FIXATION CROSS FORMAT:
% - Cross size: 200 pixels (standard text size)
% - Cross color: BLACK [0 0 0] on WHITE background [255 255 255]
% - Uses DrawFormattedText for consistent rendering
% - Note: Exploration experiments use WHITE cross on BLACK background with same dimensions
%
% saveDir: directory to save trial data
% SubID: subject ID for filename
% day: day number for filename  
% trialType: 'fMRI_example', 'fMRI_test' for filename
% scanning: boolean for fMRI scanning mode
% com: serial port for trigger
% TR: repetition time in seconds

    clear results;

    % Set default values for trigger parameters
    if nargin < 8 || isempty(scanning)
        scanning = false;
    end
    if nargin < 9 || isempty(com)
        com = 'COM4';
    end
    if nargin < 10 || isempty(TR)
        TR = 2.01;
    end

    % Initialize continuous logging arrays
    all_continuous_logs = {};
    all_discrete_logs = {};
    
    % Initialize trial start time
    trial_start_time = GetSecs();

    % Initialize Psychtoolbox
    PsychDefaultSetup(2);
    Screen('Preference', 'SkipSyncTests', 2);
    Screen('Preference', 'SuppressAllWarnings', 1);
    Screen('Preference', 'VisualDebuglevel', 3);
    Screen('Preference', 'VBLTimestampingMode', -20);
    Screen('Preference', 'TextEncodingLocale', 'UTF-16');

    % Initialize trigger if scanning
    if scanning
        s = serial(com, 'BaudRate', 9600);
        fopen(s);
        sync = 0;
    end

    % Use provided screen number or default to max screen
    if nargin < 7 || isempty(screenNumber)
        screens = Screen('Screens');
        screenNumber = max(screens);
    end
    
    white = WhiteIndex(screenNumber);
    black = BlackIndex(screenNumber);

    [window, ~] = PsychImaging('OpenWindow', screenNumber, white);
    if scanning
        HideCursor(window);
    else
        ShowCursor('Arrow', window);
    end
    Screen('BlendFunction', window, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    [screenX, screenY] = Screen('WindowSize', window);
    xCenter = screenX/2;
    yCenter = screenY/2;
    xCenter_right = 3 * (screenX/4);

    if length(filesList) == trials
        example = 0;
    else
        example = 1;
    end
    if example
        results = cell(1, 13);  % For examples, we only have 1 trial
        results(1,1:2) = filesList;
        maxDuration = 10 * 60;
    else
        rng('shuffle');
        randomIndices = randperm(trials);
        randomized_fileNames = filesList(randomIndices,:);
        results = cell(length(randomized_fileNames), 13);
        results(:,1:2) = randomized_fileNames;
        maxDuration = ((trials/2)*45 + (trials/2)*30 + (trials/2)*30) * 2;
    end
    countdownDuration = maxDuration;
    countdownStartTime = GetSecs();

    % Movement parameters
    SCALE = screenY / 3;
    MOVE_SPEED   = 1.0 * SCALE;
    ROTATE_SPEED = 70.0;
    BORDER_PADDING = 5;
    avatar.size  = 30;

    % Set up portable paths
    [~, ~, stimuliPath, ~] = setupPTSOD();

    icon_path = fullfile(stimuliPath, 'white_png');

    % Define the exit key for the experiment (only 'ESC' key will exit)
    escKey = KbName('ESCAPE'); % 'ESC' key is the only way to exit the experiment
    
    % Define unified fixation cross parameters
    crossSize = 20;
    crossThickness = 3;
    crossX = xCenter;
    crossY = yCenter;
    
    % Define unified text parameters
    textSize = 24;

    % Helper function to get current time string
    function timeStr = getCurrentTimeString()
        timeStr = datestr(now, 'HH:MM:SS.FFF');
    end

    % Helper function to add continuous log entry
    function addContinuousLogEntry(trial_time, trial_num, condition_type, phase, event, x, y, rotation_angle)
        entry = struct();
        entry.RealTime = getCurrentTimeString();
        entry.trial_time = round(trial_time, 3);
        entry.trial = trial_num;
        entry.condition_type = condition_type;
        entry.phase = phase;
        entry.event = event;
        entry.x = round(x, 3);
        entry.y = round(y, 3);
        entry.rotation_angle = round(rotation_angle, 3);
        all_continuous_logs{end+1} = entry;
    end

    % Helper function to save continuous log
    function saveContinuousLog(filename)
        if isempty(all_continuous_logs)
            return;
        end
        
        % Ensure the save directory exists
        [save_dir, ~, ~] = fileparts(filename);
        if ~exist(save_dir, 'dir')
            mkdir(save_dir);
        end
        
        % Define fieldnames
        fieldnames = {'RealTime', 'trial_time', 'trial', 'condition_type', 'phase', 'event', 'x', 'y', 'rotation_angle'};
        
        try
            fid = fopen(filename, 'w');
            if fid == -1
                error('Could not open file for writing');
            end
            
            % Write header
            fprintf(fid, '%s', strjoin(fieldnames, ','));
            fprintf(fid, '\n');
            
            % Write data
            for i = 1:length(all_continuous_logs)
                entry = all_continuous_logs{i};
                values = {};
                for j = 1:length(fieldnames)
                    field = fieldnames{j};
                    if isfield(entry, field)
                        if ischar(entry.(field))
                            values{j} = entry.(field);
                        else
                            values{j} = num2str(entry.(field));
                        end
                    else
                        values{j} = '';
                    end
                end
                fprintf(fid, '%s', strjoin(values, ','));
                fprintf(fid, '\n');
            end
            
            fclose(fid);
            fprintf('Continuous log saved successfully to: %s\n', filename);
        catch ME
            fprintf('Error saving continuous log: %s\n', ME.message);
            if fid ~= -1
                fclose(fid);
            end
        end
    end

    % Helper function to save discrete log
    function saveDiscreteLog(results, filename)
        if isempty(results)
            return;
        end
        
        % Ensure the save directory exists
        [save_dir, ~, ~] = fileparts(filename);
        if ~exist(save_dir, 'dir')
            mkdir(save_dir);
        end
        
        % Define fieldnames for discrete data
        fieldnames = {'trial', 'condition_type', 'memory', 'selected_angle', 'selected_distance', 'correct_angle', 'correct_distance', 'error_angle', 'error_distance', 'reaction_time', 'trial_number', 'final_x', 'final_y'};
        
        try
            fid = fopen(filename, 'w');
            if fid == -1
                error('Could not open file for writing');
            end
            
            % Write header
            fprintf(fid, '%s', strjoin(fieldnames, ','));
            fprintf(fid, '\n');
            
            % Write data
            for i = 1:size(results, 1)
                row = results(i, :);
                values = {};
                
                % trial (trial number)
                values{1} = num2str(i);
                
                % condition_type
                values{2} = 'test';
                
                % memory (0 or 1)
                if iscell(row{2})
                    values{3} = num2str(row{2});
                else
                    values{3} = num2str(row{2});
                end
                
                % selected_angle
                if iscell(row{3})
                    values{4} = num2str(row{3});
                else
                    values{4} = num2str(row{3});
                end
                
                % selected_distance
                if iscell(row{4})
                    values{5} = num2str(row{4});
                else
                    values{5} = num2str(row{4});
                end
                
                % correct_angle
                if iscell(row{5})
                    values{6} = num2str(row{5});
                else
                    values{6} = num2str(row{5});
                end
                
                % correct_distance
                if iscell(row{6})
                    values{7} = num2str(row{6});
                else
                    values{7} = num2str(row{6});
                end
                
                % error_angle
                if iscell(row{7})
                    values{8} = num2str(row{7});
                else
                    values{8} = num2str(row{7});
                end
                
                % error_distance
                if iscell(row{8})
                    values{9} = num2str(row{8});
                else
                    values{9} = num2str(row{8});
                end
                
                % reaction_time
                if iscell(row{9})
                    values{10} = num2str(row{9});
                else
                    values{10} = num2str(row{9});
                end
                
                % trial_number
                if iscell(row{11})
                    values{11} = num2str(row{11});
                else
                    values{11} = num2str(row{11});
                end
                
                % final_x
                if iscell(row{12})
                    values{12} = num2str(row{12});
                else
                    values{12} = num2str(row{12});
                end
                
                % final_y
                if iscell(row{13})
                    values{13} = num2str(row{13});
                else
                    values{13} = num2str(row{13});
                end
                
                fprintf(fid, '%s', strjoin(values, ','));
                fprintf(fid, '\n');
            end
            
            fclose(fid);
            fprintf('Discrete log saved successfully to: %s\n', filename);
        catch ME
            fprintf('Error saving discrete log: %s\n', ME.message);
            if fid ~= -1
                fclose(fid);
            end
        end
    end

    % Wait for trigger before starting trials (only for test trials, not examples)
    if scanning && ~example
        % Draw standardized fixation cross (BLACK cross on WHITE background)
        % STANDARDIZED FORMAT: 200px text size, BLACK cross on WHITE background
        Screen('TextSize', window, 200);
        DrawFormattedText(window, '+', 'center', 'center', [0 0 0]);
        Screen('Flip', window);
        
        fprintf('Waiting for scanner trigger before test trials...\n');
        % wait for scanner trigger
        while scanning
            sync=sync+1;
            if strcmpi(s.PinStatus.DataSetReady, 'off')
                while(strcmpi(s.PinStatus.DataSetReady, 'off'))
            %         disp('no trig');
                end 
            elseif strcmpi(s.PinStatus.DataSetReady, 'on')
                while(strcmpi(s.PinStatus.DataSetReady, 'on'))
            %         disp('no trig');
                end
            end
            %  fread(s,s.BytesAvailable);
           % disp(sync);
            if sync>0 , break; end
        end
        
        disp('Trigger was given');
        
        % Update trial start time for the first trial (before initial fixation)
        trial_start_time = GetSecs();
        
        % Log trigger received event
        addContinuousLogEntry(0.0, 1, 'test', 'trigger', 'trigger_received', 0.0, 0.0, 0.0);
        
        % Show fixation cross for 8 TRs (Dummy) after trigger
        fprintf('Showing fixation cross for 8 TRs (Dummy)...\n');
        dummyStart = GetSecs();
        
        % Log fixation start event
        addContinuousLogEntry(GetSecs() - trial_start_time, 1, 'test', 'fixation', 'fixation_start', 0.0, 0.0, 0.0);
        
        while GetSecs() - dummyStart < (8 * TR)
            % Draw white background
            Screen('FillRect', window, white);
            
            % Draw fixation cross (black cross on white background)
            Screen('TextSize', window, 100);
            DrawFormattedText(window, '+', 'center', 'center', [0 0 0]);
            
            Screen('Flip', window);
            
            % Check for 'K' key to skip dummy
            [keyIsDown, ~, keyCode] = KbCheck;
            if keyIsDown && (keyCode(KbName('K')) || keyCode(KbName('k')))
                fprintf('Dummy skipped by ''K'' key press\n');
                % Log fixation skipped event
                addContinuousLogEntry(GetSecs() - trial_start_time, 1, 'test', 'fixation', 'fixation_skipped', 0.0, 0.0, 0.0);
                break;
            end
        end
        
        % Log fixation end event (normal completion)
        addContinuousLogEntry(GetSecs() - trial_start_time, 1, 'test', 'fixation', 'fixation_end', 0.0, 0.0, 0.0);
    else
        % For non-scanning mode or example trials, set trial start time here
        trial_start_time = GetSecs();
    end

    for f = 1:size(results,1)
        trialText = sprintf('%d/%d', f, trials);
        if ~example
            mainImgFile = randomized_fileNames{f,1}; memory = randomized_fileNames{f,2};
        else
            mainImgFile = filesList{f,1};      memory = filesList{f,2};
        end
        
        % Set trial start time at the beginning of each trial (only for trials after the first)
        if f > 1
            trial_start_time = GetSecs();
        end
        if memory
            ImgTxt_dir = fullfile(stimuliPath, 'memory_screens_HE');
        else
            ImgTxt_dir = fullfile(stimuliPath, 'nomemory_screens_HE');
        end
        % Load & resize main image
        mainImg = imread(fullfile(ImgTxt_dir, mainImgFile));
        [ih,iw,~] = size(mainImg);
        sf = min(screenX/iw, screenY/ih);
        resized = imresize(mainImg, round([ih,iw]*sf));
        mainImgTexture = Screen('MakeTexture', window, resized);
        rect = Screen('Rect', mainImgTexture);
        mainImgRect = CenterRectOnPoint(rect, screenX/2, screenY/2);
        % Load text info & objects
        [~,bn] = fileparts(mainImgFile);
        fid = fopen(fullfile(ImgTxt_dir, [bn '.txt']), 'r');
        data = textscan(fid, '%s %s %s %d %d %d'); fclose(fid);
        object1 = data{1}{1}; object2 = data{2}{1}; object3 = data{3}{1};
        correctAngle = double(data{4});
        d12 = round(double(single(data{5}))/2);
        d13 = round(double(single(data{6}))/2);
        lineLength = 160;
        correctRelDist = lineLength*(d13/d12);
        % Prepare object textures & positions
        objImgs = {object1,object2,object3};
        objTex = cell(1,3); objRect = cell(1,3);
        for i=1:3
            img = imread(fullfile(icon_path,[objImgs{i} '.png']));
            objTex{i} = Screen('MakeTexture', window, img);
            switch i
                case 1, pos = [xCenter_right, yCenter];
                case 2, pos = [xCenter_right, yCenter-lineLength];
                case 3
                    ang = deg2rad(correctAngle);
                    pos = [xCenter_right+correctRelDist*sin(ang), yCenter-correctRelDist*cos(ang)];
            end
            objRect{i} = CenterRectOnPoint([0 0 75 75], pos(1), pos(2));
        end
        % Memory display dynamic
        skiptime = 0;
        if memory
            % Log memory phase start
            addContinuousLogEntry(GetSecs() - trial_start_time, f, 'test', 'memory', 'memory_start', 0.0, 0.0, 0.0);
            
            % Show image and timer simultaneously (no initial delay)
            % Convert 30 seconds to TRs: 30/2.01 = 14.93 TRs, use 15 TRs
            memoryTRs = 15;  % 15 TRs = 30.15 seconds
            
            startMem = GetSecs();
            while GetSecs() - startMem < (memoryTRs * TR)
                remT = (memoryTRs * TR) - (GetSecs() - startMem);
                % redraw image and continue covering right half
                Screen('DrawTexture', window, mainImgTexture, [], mainImgRect);
                Screen('FillRect', window, white, [screenX/2 0 screenX screenY]);
                % draw timer in top-left corner
                timerStr = sprintf('%.0f', remT);
                Screen('TextSize', window, textSize);
                DrawFormattedText(window, timerStr, 50, 50, black);
                % Draw progress indicator (non-example trials only, and not overlapping timer)
                if ~example
                    DrawFormattedText(window, trialText, screenX - 150, 50, black);
                end
                Screen('Flip', window);
                % Check for ESCAPE or E key to exit, or K key to skip timer
                [keyIsDown, ~, keyCode] = KbCheck;
                if keyIsDown && (keyCode(escKey))
                    exit_early = true; 
                    sca; 
                    return;
                end
                % Add K key functionality to skip timer for debugging
                if keyIsDown && (keyCode(KbName('K')) || keyCode(KbName('k')))
                    % Log memory phase skipped
                    addContinuousLogEntry(GetSecs() - trial_start_time, f, 'test', 'memory', 'memory_skipped', 0.0, 0.0, 0.0);
                    break;  % Skip the timer
                end
            end

            % Log memory phase end
            addContinuousLogEntry(GetSecs() - trial_start_time, f, 'test', 'memory', 'memory_end', 0.0, 0.0, 0.0);

            % Now reveal the right half (object side) and avatar immediately after memory
            Screen('DrawTexture', window, mainImgTexture, [], mainImgRect);
            % Immediately cover the left half 
            Screen('FillRect', window, white, [0 0 screenX/2 screenY]);
            % Draw progress indicator (non-example trials only)
            if ~example
                DrawFormattedText(window, trialText, screenX - 150, 50, black);
            end
            Screen('Flip', window);
        end

        % Navigation setup
        avatar.x = xCenter_right; avatar.y=yCenter; avatar.angle=0;
        KbReleaseWait;
        
        startNav=GetSecs(); prevSix=false;
        
        % Log navigation phase start
        addContinuousLogEntry(GetSecs() - trial_start_time, f, 'test', 'navigation', 'navigation_start', avatar.x, avatar.y, avatar.angle);
        
        % Set trial timer to 17 TRs (34.17 seconds)
        trialTRs = 17;  % 17 TRs = 34.17 seconds
        trialEndTime = startNav + (trialTRs * TR);
        
        while true
            t=GetSecs(); dt=t-startNav; startNav=t;
            [~,~,kc]=KbCheck;
            if kc(KbName('7&')), avatar.angle = avatar.angle - ROTATE_SPEED*dt; end
            if kc(KbName('0)')), avatar.angle = avatar.angle + ROTATE_SPEED*dt; end
            rad=deg2rad(avatar.angle);
            vx=sin(rad)*MOVE_SPEED*dt; vy=-cos(rad)*MOVE_SPEED*dt;
            if kc(KbName('8*')), avatar.x=avatar.x+vx; avatar.y=avatar.y+vy; end
            if kc(KbName('9(')), avatar.x=avatar.x-vx; avatar.y=avatar.y-vy; end
            avatar.x=min(max(avatar.x,BORDER_PADDING),screenX-BORDER_PADDING);
            avatar.y=min(max(avatar.y,BORDER_PADDING),screenY-BORDER_PADDING);
            
            % Log continuous navigation data
            current_trial_time = GetSecs() - trial_start_time;
            addContinuousLogEntry(current_trial_time, f, 'test', 'navigation', '', avatar.x, avatar.y, avatar.angle);
            % draw
            Screen('FillRect',window,white);
            Screen('DrawTexture',window,mainImgTexture,[],mainImgRect);
            for i=1:2, Screen('DrawTexture',window,objTex{i},[],objRect{i}); end
            tip=[avatar.x+avatar.size*sin(rad), avatar.y+avatar.size*-cos(rad)];
            bmx=avatar.x-(avatar.size/1.5)*sin(rad);
            bmy=avatar.y-(avatar.size/1.5)*-cos(rad);
            lp=[bmx+(avatar.size/2)*sin(rad+pi/2), bmy+(avatar.size/2)*-cos(rad+pi/2)];
            rp=[bmx+(avatar.size/2)*sin(rad-pi/2), bmy+(avatar.size/2)*-cos(rad-pi/2)];
            Screen('FillPoly',window,black,[tip;lp;rp]);
            % Hide left half of the screen in memory condition during navigation
            if memory
                Screen('FillRect', window, white, [0 0 screenX/2 screenY]);
            end
            % Draw progress indicator (non-example trials only)
            if ~example
                Screen('TextSize', window, textSize);
                DrawFormattedText(window, trialText, screenX - 150, 50, black);
            end
            
            % Draw trial timer in top-left corner
            remainingTime = trialEndTime - GetSecs();
            if remainingTime > 0
                timerStr = sprintf('%.0f', remainingTime);
                Screen('TextSize', window, textSize);
                DrawFormattedText(window, timerStr, 50, 50, black);
            end
            
            Screen('Flip',window);
            
            % Check if trial time has expired
            if GetSecs() >= trialEndTime
                fprintf('Trial %d: Time limit reached (17 TRs)\n', f);
                % Log trial timeout
                addContinuousLogEntry(GetSecs() - trial_start_time, f, 'test', 'navigation', 'trial_timeout', avatar.x, avatar.y, avatar.angle);
                break;
            end
            
            cs = kc(KbName('1!')) || kc(KbName('Return'));
            if cs && ~prevSix
                reactionTime=GetSecs()-countdownStartTime;
                % Log trial completion
                addContinuousLogEntry(GetSecs() - trial_start_time, f, 'test', 'navigation', 'trial_completed', avatar.x, avatar.y, avatar.angle);
                % If this is an example trial, show the target (object 3) in its real location
                if example
                    KbReleaseWait; % Wait for all keys to be released before feedback
                    feedbackShown = false;
                    while ~feedbackShown
                        % Draw everything as in the last navigation frame
                        Screen('FillRect',window,white);
                        Screen('DrawTexture',window,mainImgTexture,[],mainImgRect);
                        for i=1:2, Screen('DrawTexture',window,objTex{i},[],objRect{i}); end
                        % Draw the target (object 3) in its real location UNDERNEATH the avatar
                        Screen('DrawTexture',window,objTex{3},[],objRect{3});
                        % Draw avatar on top so it's visible even if on object3 location
                        tip=[avatar.x+avatar.size*sin(rad), avatar.y+avatar.size*-cos(rad)];
                        bmx=avatar.x-(avatar.size/1.5)*sin(rad);
                        bmy=avatar.y-(avatar.size/1.5)*-cos(rad);
                        lp=[bmx+(avatar.size/2)*sin(rad+pi/2), bmy+(avatar.size/2)*-cos(rad+pi/2)];
                        rp=[bmx+(avatar.size/2)*sin(rad-pi/2), bmy+(avatar.size/2)*-cos(rad-pi/2)];
                        Screen('FillPoly',window,black,[tip;lp;rp]);
                        if memory
                            Screen('FillRect', window, white, [0 0 screenX/2 screenY]);
                        end
                        Screen('Flip',window);
                        % Wait for 6 or 6^ key press
                        [keyIsDown, ~, keyCode] = KbCheck;
                        if keyIsDown && (keyCode(KbName('1!')) || keyCode(KbName('Return')))
                            feedbackShown = true;
                        end
                        if keyIsDown && keyCode(escKey)
                            exit_early = true; 
                            sca; 
                            return;
                        end
                    end
                end
                break;
            end
            prevSix=cs;
            if kc(escKey)
                exit_early = true; 
                sca; 
                return; 
            end
        end
        
        % Calculate when the current TR ends and when the next TR starts
        currentTime = GetSecs();
        trialStartTime = startNav; % Calculate when trial started
        elapsedTRs = floor((currentTime - trialStartTime) / TR);
        nextTRStart = trialStartTime + ((elapsedTRs + 1) * TR);
        
        % Wait until the next TR boundary before starting fixation
        if currentTime < nextTRStart
            waitTime = nextTRStart - currentTime;
            fprintf('Trial %d completed early. Waiting %.2f seconds for TR alignment...\n', f, waitTime);
            
            % Log TR alignment fixation start
            addContinuousLogEntry(GetSecs() - trial_start_time, f, 'test', 'fixation', 'tr_alignment_fixation_start', 0.0, 0.0, 0.0);
            
            % Show fixation cross while waiting for next TR boundary
            while GetSecs() < nextTRStart
                % Draw white background
                Screen('FillRect', window, white);
                % Draw standardized fixation cross (BLACK cross on WHITE background)
                % STANDARDIZED FORMAT: 200px text size, BLACK cross on WHITE background
                Screen('TextSize', window, 200);
                DrawFormattedText(window, '+', 'center', 'center', [0 0 0]);
                
                Screen('Flip', window);
                
                % Check for ESC key to exit
                [keyIsDown, ~, keyCode] = KbCheck;
                if keyIsDown && keyCode(escKey)
                    exit_early = true; 
                    sca; 
                    return; 
                end
            end
            
            % Log TR alignment fixation end
            addContinuousLogEntry(GetSecs() - trial_start_time, f, 'test', 'fixation', 'tr_alignment_fixation_end', 0.0, 0.0, 0.0);
        end

        % compute results
        dx=avatar.x-xCenter_right; dy=yCenter-avatar.y;
        selAngle=mod(atan2d(dx,dy),360);
        phi=abs(mod(selAngle-correctAngle,360));
        errorAngle=min(phi,360-phi);
        selDistPx=sqrt(dx^2+dy^2);
        errorRelDist=round(correctRelDist - selDistPx);
        results(f,3:13)={selAngle,selDistPx,correctAngle,correctRelDist,errorAngle,errorRelDist,reactionTime,skiptime,f,avatar.x,avatar.y};
        
        % Note: Discrete data will be saved as CSV at the end of all trials
        
        % Add 4 TR fixation screen after each trial (including last trial)
        % Log inter-trial fixation start
        addContinuousLogEntry(GetSecs() - trial_start_time, f+1, 'test', 'fixation', 'inter_trial_fixation_start', 0.0, 0.0, 0.0);
        
        fixationStart = GetSecs();
        while GetSecs() - fixationStart < (4 * TR)
            % Draw white background
            Screen('FillRect', window, white);
            % Draw standardized fixation cross (BLACK cross on WHITE background)
            % STANDARDIZED FORMAT: 200px text size, BLACK cross on WHITE background
            Screen('TextSize', window, 200);
            DrawFormattedText(window, '+', 'center', 'center', [0 0 0]);
            
            Screen('Flip', window);
            
            % Check for 'K' key to skip fixation
            [keyIsDown, ~, keyCode] = KbCheck;
            if keyIsDown && (keyCode(KbName('K')) || keyCode(KbName('k')))
                fprintf('Fixation skipped by ''K'' key press\n');
                % Log inter-trial fixation skipped
                addContinuousLogEntry(GetSecs() - trial_start_time, f+1, 'test', 'fixation', 'inter_trial_fixation_skipped', 0.0, 0.0, 0.0);
                break;
            end
        end
        
        % Log inter-trial fixation end (normal completion)
        addContinuousLogEntry(GetSecs() - trial_start_time, f+1, 'test', 'fixation', 'inter_trial_fixation_end', 0.0, 0.0, 0.0);
    end
    
    % Save continuous log
    if nargin >= 4  % Only save if saveDir is provided
        % Check if we should use centralized results directory
        centralized_results_dir = getenv('CENTRALIZED_RESULTS_DIR');
        if ~isempty(centralized_results_dir) && exist(centralized_results_dir, 'dir')
            % Use centralized results directory with SubID subfolder
            continuous_save_dir = fullfile(centralized_results_dir, SubID);
        else
            % Fall back to the provided saveDir
            continuous_save_dir = saveDir;
        end
        
        % Use new filename format for fMRI sessions
        if strcmp(trialType, 'fMRI_example') || strcmp(trialType, 'fMRI_test')
            continuousFilename = fullfile(continuous_save_dir, sprintf('%s_PTSOD_run%d_fMRI_continuous.csv', SubID, day));
        else
            % Keep old format for other trial types
            continuousFilename = fullfile(continuous_save_dir, sprintf('%s_PTSOD_day%d_%s_continuous.csv', SubID, day, trialType));
        end
        
        % Ensure the save directory exists
        [continuous_dir, ~, ~] = fileparts(continuousFilename);
        if ~exist(continuous_dir, 'dir')
            mkdir(continuous_dir);
        end
        
        saveContinuousLog(continuousFilename);
        
        % Save discrete log as CSV
        if strcmp(trialType, 'fMRI_example') || strcmp(trialType, 'fMRI_test')
            discreteFilename = fullfile(continuous_save_dir, sprintf('%s_PTSOD_run%d_fMRI_discrete.csv', SubID, day));
        else
            % Keep old format for other trial types
            discreteFilename = fullfile(continuous_save_dir, sprintf('%s_PTSOD_day%d_%s_discrete.csv', SubID, day, trialType));
        end
        
        saveDiscreteLog(results, discreteFilename);
    end
    
    % Close trigger connection
    if scanning
        fclose(s);
        delete(s);
    end
    
    sca;
    if ~exist('exit_early','var')
        exit_early = false;
    end
end 