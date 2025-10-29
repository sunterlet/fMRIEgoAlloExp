%% Full Arena Run 1 (2 snake + 2 multi_arena trials)
fprintf('\n--- Full Arena Run 1 (Run 1, 4 trials total) ---\n');
fprintf('This will run 2 snake trials and 2 multi_arena trials as a single process\n');

% Arena assignments (for reference - handled internally by the wrapper)
practice_arenas = {'garden', 'beach', 'village', 'ranch', 'zoo', 'school'};
fmri_arenas = {'hospital', 'bookstore', 'gym', 'museum', 'airport', 'market'};

% Initialize trigger if scanning is enabled
if scanning
    fprintf('Initializing trigger for Full Arena Run 1...\n');
    s=serial('com4','BaudRate',9600);
    fopen(s)
    sync=0;
end

% Wait for trigger before starting block
fprintf('Waiting for scanner trigger before Full Arena Run 1...\n');
trigger_received_time = [];
while scanning    % Middle Trigger
    sync=sync+1;
    if strcmpi(s.PinStatus.DataSetReady, 'off')
        while(strcmpi(s.PinStatus.DataSetReady, 'off'))

        end 
    elseif strcmpi(s.PinStatus.DataSetReady, 'on')
        while(strcmpi(s.PinStatus.DataSetReady, 'on'))

        end
    end
    disp(sync);
    if sync>0 
        trigger_received_time = GetSecs();
        break; 
    end
end
fprintf('Trigger received! Starting Full Arena Run 1...\n');

% Log trigger received event if scanning is enabled
if scanning && ~isempty(trigger_received_time)
    fprintf('Logging trigger received event at time: %.3f\n', trigger_received_time);
    % Set environment variable for Python scripts to know trigger time
    setenv('TRIGGER_RECEIVED_TIME', num2str(trigger_received_time));
end

full_arena_run(SubID, 1, selectedScreen);

% Close trigger after block completion
if scanning
    fclose(s);
    delete(s);
end

%% Full Arena Run 2 (2 snake + 2 multi_arena trials)
fprintf('\n--- Full Arena Run 2 (Run 2, 4 trials total) ---\n');
fprintf('This will run 2 snake trials and 2 multi_arena trials as a single process\n');
fprintf('to eliminate timing gaps between trials.\n');

% Initialize trigger if scanning is enabled
if scanning
    fprintf('Initializing trigger for Full Arena Run 2...\n');
    s=serial('com4','BaudRate',9600);
    fopen(s)
    sync=0;
end

% Wait for trigger before starting block
fprintf('Waiting for scanner trigger before Full Arena Run 2...\n');
trigger_received_time = [];
while scanning    % Middle Trigger
    sync=sync+1;
    if strcmpi(s.PinStatus.DataSetReady, 'off')
        while(strcmpi(s.PinStatus.DataSetReady, 'off'))

        end 
    elseif strcmpi(s.PinStatus.DataSetReady, 'on')
        while(strcmpi(s.PinStatus.DataSetReady, 'on'))

        end
    end
    disp(sync);
    if sync>0 
        trigger_received_time = GetSecs();
        break; 
    end
end
fprintf('Trigger received! Starting Full Arena Run 2...\n');

% Log trigger received event if scanning is enabled
if scanning && ~isempty(trigger_received_time)
    fprintf('Logging trigger received event at time: %.3f\n', trigger_received_time);
    % Set environment variable for Python scripts to know trigger time
    setenv('TRIGGER_RECEIVED_TIME', num2str(trigger_received_time));
end

full_arena_run(SubID, 2, selectedScreen);

% Close trigger after block completion
if scanning
    fclose(s);
    delete(s);
end