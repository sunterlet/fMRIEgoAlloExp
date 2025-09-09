function waitForTrigger(s, scanning)
% WAIT FOR TRIGGER - Waits for scanner trigger signal
% 
% This function waits for the scanner trigger signal before proceeding
% 
% Inputs:
%   s        - serial port object
%   scanning - boolean indicating if scanning mode is active

if scanning
    sync = 0;
    
    % Wait for scanner trigger
    while scanning
        sync = sync + 1;
        
        % Check if DataSetReady pin is off
        if strcmpi(s.PinStatus.DataSetReady, 'off')
            while(strcmpi(s.PinStatus.DataSetReady, 'off'))
                % Wait for pin to go high
                % disp('no trig');
            end 
        % Check if DataSetReady pin is on
        elseif strcmpi(s.PinStatus.DataSetReady, 'on')
            while(strcmpi(s.PinStatus.DataSetReady, 'on'))
                % Wait for pin to go low
                % disp('no trig');
            end
        end
        
        % Optional: read available bytes
        % fread(s, s.BytesAvailable);
        
        % Optional: display sync counter
        % disp(sync);
        
        % Break after first trigger
        if sync > 0
            break;
        end
    end
end

end 