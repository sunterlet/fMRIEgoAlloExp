function trigger_manager(mode, com_port, TR)
%TRIGGER_MANAGER Manage fMRI triggers at the MATLAB level
%
%   trigger_manager('init', com_port, TR) - Initialize trigger connection
%   trigger_manager('wait') - Wait for trigger
%   trigger_manager('close') - Close trigger connection
%
%   Parameters:
%       mode: 'init', 'wait', or 'close'
%       com_port: Serial port for trigger (e.g., 'com4')
%       TR: TR in seconds (e.g., 2.01)
%
%   Examples:
%       trigger_manager('init', 'com4', 2.01)
%       trigger_manager('wait')
%       trigger_manager('close')

    persistent serial_obj
    
    switch mode
        case 'init'
            % Initialize serial connection for trigger
            try
                serial_obj = serial(com_port, 'BaudRate', 9600, 'DataBits', 8, ...
                    'Parity', 'none', 'StopBits', 1, 'Terminator', 'LF');
                fopen(serial_obj);
                fprintf('Trigger initialized on %s with TR = %.2f seconds\n', com_port, TR);
            catch ME
                error('Failed to initialize trigger on %s: %s', com_port, ME.message);
            end
            
        case 'wait'
            % Wait for trigger using pin status detection (like PTSOD function)
            if isempty(serial_obj) || ~isvalid(serial_obj)
                error('Trigger not initialized. Call trigger_manager(''init'', com_port, TR) first.');
            end
            
            fprintf('Waiting for scanner trigger...\n');
            fprintf('CRITICAL: Experiment will NOT continue without trigger!\n');
            sync = 0;
            
            try
                % Wait for trigger using pin status detection
                while sync == 0
                    if strcmpi(serial_obj.PinStatus.DataSetReady, 'off')
                        while(strcmpi(serial_obj.PinStatus.DataSetReady, 'off'))
                            % Wait for pin to go high
                        end 
                    elseif strcmpi(serial_obj.PinStatus.DataSetReady, 'on')
                        while(strcmpi(serial_obj.PinStatus.DataSetReady, 'on'))
                            % Wait for pin to go low
                        end
                    end
                    sync = sync + 1;
                    if sync > 0
                        break;
                    end
                end
                
                fprintf('Trigger received! Experiment can proceed.\n');
                
            catch ME
                error('CRITICAL ERROR: Failed to receive trigger. Experiment cannot continue without trigger: %s', ME.message);
            end
            
        case 'close'
            % Close trigger connection
            if ~isempty(serial_obj) && isvalid(serial_obj)
                try
                    fclose(serial_obj);
                    delete(serial_obj);
                    clear serial_obj;
                    fprintf('Trigger connection closed.\n');
                catch ME
                    warning('Error closing trigger connection: %s', ME.message);
                end
            end
            
        otherwise
            error('Invalid mode. Use ''init'', ''wait'', or ''close''');
    end
end 