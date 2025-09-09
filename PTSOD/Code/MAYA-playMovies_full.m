function playMovies_full(subID,group,session,runNum,movieNum,scanning,eyetracking,TR,com,screenid)
commandwindow % to make the pointer go back to command window

if ~isa(subID,'char')
    error('subID must be a char')
end

% set path
codesFolder=pwd;
cd ..
path=pwd;
cd(codesFolder)
moviePath=fullfile(path,'Movies');
cuePath=fullfile(path,'Images');
    
% set movies
if group==1
    movieNames={'Kupa16_720','Hazarot1_720','Kupa1_720'};
    cueNames={'Kupa16','Hazarot1','Kupa1'};
    MovieLength=[302,306,301];
elseif group==2
    movieNames={'Hazarot1_720','Kupa16_720','Kupa1_720'};
    cueNames={'Hazarot1','Kupa16','Kupa1'};
    MovieLength=[306,302,301];
else
    error('group must be 1 or 2')
end

currentMovie=string(movieNames(movieNum));
currentCue=string(cueNames(movieNum));

% set experiment parameters
fixTime=TR*4;
introTime=10;
cueTime=2*TR;
movieTRs=ceil(MovieLength(movieNum)/TR);
finishScreen=movieTRs*TR-MovieLength(movieNum)+TR; % number of secs to add to gray finish screen the scan will end in round TRs

scanLength=fixTime+cueTime+MovieLength(movieNum)+finishScreen;
scanLengthTR=scanLength/TR; % This parameter is not used, it's just to make sure what is the actual scan lenght

% set stimuli files
movieFile=fullfile(moviePath,char(compose('%s.mp4',currentMovie)));
cueFile=fullfile(cuePath,append(currentCue,'.jpg'));
introFile=fullfile(cuePath,'movieIntro.jpg');

% set sub filename for edf folder name
sub_resultsPath=fullfile(path,'Results',subID);
if ~exist(sub_resultsPath,'dir')
    mkdir(sub_resultsPath)
end
sub_fileName=append(subID,'_group',string(group),'_session',string(session),'_movieRun',string(runNum),'_',currentCue);


% set log file
log = struct;
logFileName = append(sub_fileName,'_',char(datetime('now','Format','ddMMyyyy_HHmm')),'.mat');

% EYELINK EDF folder
sub_run_results_folder=fullfile(sub_resultsPath,sub_fileName);
if ~exist(sub_run_results_folder,'dir')
    mkdir(sub_run_results_folder)
end

disp(append('results will be saved in path: ',sub_run_results_folder))
disp(append('name of current log file: ',logFileName))

%% PTB initialization
% Avoid Psychotoolbox synchronization test and warnings
PsychDefaultSetup(2);
Screen('Preference', 'SkipSyncTests', 2);
Screen('Preference', 'SuppressAllWarnings', 1);
Screen('Preference', 'VisualDebuglevel', 3);
Screen('Preference', 'VBLTimestampingMode', -1);

% Define black and white
white = WhiteIndex(screenid);
gray = white / 2;


% resolution
x=1920;
y=1200;
[w,h]=Screen('WindowSize',screenid);
left=(w/2)-(x/2);
right=left+x;
top=(h/2)-(y/2);
bottom=top+y;
winSize=[left top right bottom];

[window,~] = PsychImaging('OpenWindow', screenid, gray, winSize);  

Screen('BlendFunction', window, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');

% define keys
DeviceNum=(-1); % listen to all keyboards
KbName('UnifyKeyNames')
esc=KbName('ESCAPE');  
right=KbName('RightArrow');

KeyList=zeros(1,256);
KeyList([esc,right])=1;

% Create keyboard listening queue
KbQueueCreate(DeviceNum,KeyList)

%% equipment initiation
% TRIGGER init
if scanning
    s=serial(com,'BaudRate',9600);
    fopen(s)
    sync=0;
end


% EYELINK init
if eyetracking
    % shut previous session
    if Eyelink('IsConnected') == 1
        Eyelink('Shutdown');
    end
    % initialize connection
    if (Eyelink('initialize') ~= 0)
        error('could not initialize connection to Eyelink')
    end
        % choose types of data to be recorded
        status_sampleData = Eyelink('command','link_sample_data = LEFT,RIGHT,GAZE,AREA,GAZERES,HREF,PUPIL,STATUS,INPUT');
        % define what types of events will be written to the .edf file
        status_eventFilter = Eyelink('command', 'link_event_filter = LEFT,RIGHT,FIXATION,BLINK,SACCADE,BUTTON,MESSAGE');
end    

% start listening to the keyboard
% KbQueueStart(DeviceNum);
    
%% intro presentation if it is the first run of session
if runNum==1
    cueImage=imread(introFile);
    imageTexture=Screen('MakeTexture',window,cueImage);
    Screen('DrawTexture',window,imageTexture,[],[],0);
    [onTime]=Screen('Flip',window);

    [~, ~]=waitOrPress_new(onTime,introTime,window,gray,scanning,DeviceNum);    
end

%% Run
% keyboard setup
LoadPsychHID;

if scanning
   HideCursor(window)
end

% open an eyetracking recording file
if eyetracking
    edffilename = append(subID(1:2),subID(end-1:end),'r',num2str(runNum),'m',num2str(movieNum),'.edf');        
    status_openFile = Eyelink('OpenFile',edffilename);
end

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

% start recording eye movements and save timestamp
if eyetracking
    status_start = Eyelink('startrecording'); %start recording eye position
    status_stratTime = Eyelink('Message', 'StartTime');
end

% Any other message to be save in eyelink file as follows:
if eyetracking
	status_response = Eyelink('Message', ['run_',num2str(runNum),'_response']);
end    

%% fixation to be removed in analysis
Screen('TextSize',window, 100);
DrawFormattedText(window,'+','center','center',[0 0 0]);
[tStartDummy]=Screen('Flip',window);

disp('Dummy fixation')

[~, ~]=waitOrPress_new(tStartDummy,fixTime,window,gray,scanning,DeviceNum);  

tEndDummy=GetSecs;

%% present cue for movie
cueImage=imread(cueFile);
imageTexture=Screen('MakeTexture',window,cueImage);
Screen('DrawTexture',window,imageTexture,[],[],0);
[tStartCue]=Screen('Flip',window);
disp('START cue')

[~, ~]=waitOrPress_new(tStartCue,cueTime,window,gray,scanning,DeviceNum);

%% present movie
movie = Screen('OpenMovie',window, movieFile);
Screen('PlayMovie', movie, 1);
tStartMovie=GetSecs;

disp(append('START movie ',currentCue))

% Playback loop: Runs until end of movie or esc key:
while 1        
          [keyIsDown, ~, keyCode] = KbCheck;
            if (keyIsDown==1 && keyCode(esc))
                % Set the abort-demo flag.
                sca
                % Close trigger port
                if scanning
                    fclose(s);
                    delete(s);
                end                    
                error('esc key was pressed')
                
            elseif (keyIsDown==1 && keyCode(right))
                Screen('Fillrect',window,gray);
                Screen('Flip',window);
                break;
            end
        % Wait for next movie frame, retrieve texture handle to it
        tex = Screen('GetMovieImage', window, movie);
        
        % Valid texture returned? A negative value means end of movie reached:
        if tex<=0
            % We're done, break out of loop:
            break;
        end         
        % Draw the new texture immediately to screen:
        Screen('DrawTexture', window, tex);
        
        % Update display:
        Screen('Flip', window);
        
        % Release texture:
        Screen('Close', tex);
end

Screen('PlayMovie', movie, 0);
tEndMovie = GetSecs;
Screen('CloseMovie', movie);   

disp('END movie')

Screen('Fillrect',window,gray);
Screen('Flip',window);
WaitSecs(finishScreen);
tEndRun = GetSecs;

%% finishing steps
sca
if scanning
   ShowCursor(window);
end

% save log file parameters
log.tStartDummy = tStartDummy;
log.tEndDummy = tEndDummy;
log.tStartCue = tStartCue-tEndDummy; % this should be the time of the first TR of the scan from the beginning of the experimet (that we are looking at, after 4TR removal)
log.tStartMovie = tStartMovie-tEndDummy; % the time of the movie started after the beginning of the experiment (without dummy)
log.tEndMovie = tEndMovie-tEndDummy;
log.tEndRun = tEndRun-tEndDummy;

save(fullfile(sub_run_results_folder,logFileName),'log')

%close eyelink file and save edf locally, then shut down eyetracker connection
if eyetracking
    cd(sub_run_results_folder)
    addpath(genpath(codesFolder))    
    saveEDF(edffilename);
    Eyelink('Shutdown');
    cd(codesFolder)
end

% Close trigger port
if scanning
    fclose(s);
    delete(s);
end

end

