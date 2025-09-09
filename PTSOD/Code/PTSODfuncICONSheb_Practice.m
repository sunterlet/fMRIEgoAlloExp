function [results, exit_early] = PTSODfuncICONSheb_Practice(filesList,trials, saveDir, SubID, day, trialType, screenNumber)
% Practice version for outside the magnet - no fixation crosses
% saveDir: directory to save trial data
% SubID: subject ID for filename
% day: day number for filename  
% trialType: 'practice_example1', 'practice_example2', 'practice_example3' for filename

    clear results;

    % Initialize Psychtoolbox
    PsychDefaultSetup(2);
    Screen('Preference', 'SkipSyncTests', 2);
    Screen('Preference', 'SuppressAllWarnings', 1);
    Screen('Preference', 'VisualDebuglevel', 3);
    Screen('Preference', 'VBLTimestampingMode', -20);
    Screen('Preference', 'TextEncodingLocale', 'UTF-16');

    % Use provided screen number or default to max screen
    if nargin < 7 || isempty(screenNumber)
        screens = Screen('Screens');
        screenNumber = max(screens);
    end

    white = WhiteIndex(screenNumber);
    black = BlackIndex(screenNumber);

    [window, ~] = PsychImaging('OpenWindow', screenNumber, white);
    HideCursor(window);
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
    
    % Define unified text parameters
    textSize = 24;

    for f = 1:size(results,1)
        trialText = sprintf('%d/%d', f, trials);
        if ~example
            mainImgFile = randomized_fileNames{f,1}; memory = randomized_fileNames{f,2};
        else
            mainImgFile = filesList{f,1};      memory = filesList{f,2};
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
            % Show image and timer simultaneously (no initial delay)
            startMem = GetSecs();
            while GetSecs() - startMem < 30  % Changed from 45 to 30 seconds
                remT = 30 - (GetSecs() - startMem);  % Changed from 45 to 30 seconds
                % redraw image and continue covering right half
                Screen('DrawTexture', window, mainImgTexture, [], mainImgRect);
                Screen('FillRect', window, white, [screenX/2 0 screenX screenY]);
                % draw timer in top-left corner (for all trials during memory phase)
                timerStr = sprintf('%.0f', remT);  % Changed from '%.0f:%02.0f' to '%.0f'
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
                    exit_early = true; sca; return;
                end
                % Add K key functionality to skip timer for debugging
                if keyIsDown && (keyCode(KbName('K')) || keyCode(KbName('k')))
                    break;  % Skip the timer
                end
            end
            % Do NOT reveal the right half yet; wait until after fixation cross
            
            % NO fixation cross for practice - immediately reveal the right half
            Screen('DrawTexture', window, mainImgTexture, [], mainImgRect);
            % Immediately cover the left half with white to prevent it from being visible
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
            Screen('Flip',window);
            cs = kc(KbName('1!')) || kc(KbName('Return'));
            if cs && ~prevSix
                reactionTime=GetSecs()-countdownStartTime;
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
                            exit_early = true; sca; return;
                        end
                    end
                end
                break;
            end
            prevSix=cs;
            if kc(escKey), exit_early = true; sca; return; end
            if kc(escKey), exit_early = true; sca; return; end
        end
        % compute results
        dx=avatar.x-xCenter_right; dy=yCenter-avatar.y;
        selAngle=mod(atan2d(dx,dy),360);
        phi=abs(mod(selAngle-correctAngle,360));
        errorAngle=min(phi,360-phi);
        selDistPx=sqrt(dx^2+dy^2);
        errorRelDist=round(correctRelDist - selDistPx);
        results(f,3:13)={selAngle,selDistPx,correctAngle,correctRelDist,errorAngle,errorRelDist,reactionTime,skiptime,f,avatar.x,avatar.y};
        
        % Save this trial's data immediately
        if nargin >= 4  % Only save if saveDir is provided
            trialData = results(f,:);
            
            % Check if we should use centralized results directory
            centralized_results_dir = getenv('CENTRALIZED_RESULTS_DIR');
            if ~isempty(centralized_results_dir) && exist(centralized_results_dir, 'dir')
                % Use centralized results directory with SubID subfolder
                trial_save_dir = fullfile(centralized_results_dir, SubID);
            else
                % Fall back to the provided saveDir
                trial_save_dir = saveDir;
            end
            
            % Keep existing format for practice sessions
            trialFilename = fullfile(trial_save_dir, sprintf('%s_PTSOD_day%d_%s_trial%d.mat', SubID, day, trialType, f));
            
            % Ensure the save directory exists
            [trial_dir, ~, ~] = fileparts(trialFilename);
            if ~exist(trial_dir, 'dir')
                mkdir(trial_dir);
            end
            
            save(trialFilename, 'trialData');
        end
        
        % NO fixation cross after practice trials - just a brief pause
        WaitSecs(1);
    end
    sca;
    if ~exist('exit_early','var')
        exit_early = false;
    end
end 