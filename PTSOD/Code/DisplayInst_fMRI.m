function [Instructions] = DisplayInst_fMRI(inst,screenNumber)
    
    % Clear the workspace and the screen
%     sca;
    
    % Initialize Psychtoolbox
    PsychDefaultSetup(2);
    
    % Skip sync checks for Psychtoolbox
    Screen('Preference', 'SkipSyncTests', 2);
    Screen('Preference', 'SuppressAllWarnings', 1);
    Screen('Preference', 'VisualDebuglevel', 3);
    Screen('Preference', 'VBLTimestampingMode', -20);


    % Open a Psychtoolbox window on the selected screen
    % Use black background for final instruction
    if strcmp(inst, '9.png')
        [window, windowRect] = PsychImaging('OpenWindow', screenNumber, [0 0 0]);
    else
        [window, windowRect] = PsychImaging('OpenWindow', screenNumber, [1 1 1]);
    end
    
    % Get the center coordinates of the window
    [xCenter, yCenter] = RectCenter(windowRect);
    
    % Get the size of the window
    windowWidth = RectWidth(windowRect);
    windowHeight = RectHeight(windowRect);

    % Set up portable paths
    [~, ~, ~, instructionsPath] = setupPTSOD();

    % Set the path to the folder containing the image
    % Use exploration instructions for final instruction
    if strcmp(inst, '9.png')
        Inst_path = fullfile(pwd, 'exploration', 'Instructions-he');
    else
        Inst_path = fullfile(instructionsPath, 'instructions_practice_fmri1');
    end
    
    % Check the type of 'inst' to determine if it's a single image name or a cell array
    if ischar(inst)
        % Single image name
        imageNames = {inst};
    elseif iscell(inst)
        % List of image names
        imageNames = inst;
    else
        error('Invalid input. Expected a single image name or a cell array of image names.');
    end
    
    % Loop over the image names
    for i = 1:numel(imageNames)
        % Get the current image name
        currentImage = imageNames{i};
        
        % Full path to the image
        image_path = fullfile(Inst_path, sprintf(currentImage));
        
        % Set the key code for the 1! key and Enter key
        oneKeyCode = KbName('1!');
        enterKeyCode = KbName('Return');
        escKey = KbName('ESCAPE'); % 'ESC' key is the only way to exit the instructions
        
        % Load the image
        image = imread(image_path);
        
        % Calculate the scale factor to fit the image within the window while maintaining aspect ratio
        % Use the smaller scale factor to ensure the image fits completely within the window
        % Apply smaller scale factor only to 9.png (final instruction), keep PTSOD instructions original size
        if strcmp(currentImage, '9.png')
            scaleFactor = min(windowWidth / size(image, 2), windowHeight / size(image, 1)) * 0.5;
        else
            scaleFactor = min(windowWidth / size(image, 2), windowHeight / size(image, 1));
        end
        scaledWidth = round(scaleFactor * size(image, 2));
        scaledHeight = round(scaleFactor * size(image, 1));
        
        % Resize the image maintaining original aspect ratio
        scaledImage = imresize(image, [scaledHeight, scaledWidth], 'bicubic');
        
        % Create a texture from the scaled image
        imageTexture = Screen('MakeTexture', window, scaledImage);
        
        % Calculate the destination rectangle for centering the image
        destRect = CenterRectOnPoint([0 0 scaledWidth scaledHeight], xCenter, yCenter);
        
        % Loop until the space bar is pressed
        while true
            % Draw the image on the screen
            Screen('DrawTexture', window, imageTexture, [], destRect);
            
            % Flip the screen to display the image and instructions
            Screen('Flip', window);

            % Wait 
            WaitSecs(0.15);
            
            % Check for key press
            [keyIsDown, ~, keyCode] = KbCheck;
            if keyIsDown && keyCode(escKey)
                sca;
                Instructions = -1;
                return;
            end
            if keyIsDown && (keyCode(oneKeyCode) || keyCode(enterKeyCode)) && strcmp(currentImage, '9-summary.png')
                % Clear screen immediately
                Screen('FillRect', window, [0 0 0]);
                Screen('Flip', window);
                Instructions = 0;
                break;
            elseif keyIsDown && (keyCode(oneKeyCode) || keyCode(enterKeyCode)) && strcmp(currentImage, '9.png')
                % Clear screen immediately and close window for final instruction
                Screen('FillRect', window, [0 0 0]);
                Screen('Flip', window);
                sca;
                Instructions = 1;
                break;
            elseif keyIsDown && (keyCode(oneKeyCode) || keyCode(enterKeyCode)) && ~strcmp(currentImage, '9-summary.png') && ~strcmp(currentImage, '99-thank-you.png') && ~strcmp(currentImage, '9.png')
                % Clear screen immediately
                Screen('FillRect', window, [0 0 0]);
                Screen('Flip', window);
                Instructions = 1;
                break;
            elseif keyIsDown && (keyCode(oneKeyCode) || keyCode(enterKeyCode)) && strcmp(currentImage, '99-thank-you.png')
                % Clear screen immediately
                Screen('FillRect', window, [0 0 0]);
                Screen('Flip', window);
                Instructions = 1;
                % Open a URL (change 'https://example.com' to the desired URL)
%                 web('https://docs.google.com/forms/d/e/1FAIpQLSdszFrji9oZznIUoonhcw0P3xyQq97wgd--qyYdJaFW5ffJkA/viewform?usp=sf_link', '-browser');
                break;
            end
        end
        
        % Release the texture
        Screen('Close', imageTexture);
    end
    
    if strcmp(currentImage, '99-thank-you.png')
        % Clear the screen
        Screen('Flip', window);
        
        % Close the window and release resources
        sca;
    end
end 