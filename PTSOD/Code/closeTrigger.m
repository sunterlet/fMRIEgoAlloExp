function closeTrigger(s, scanning)
% CLOSE TRIGGER - Closes the trigger serial connection
% 
% This function properly closes the serial port connection used for triggers
% 
% Inputs:
%   s        - serial port object
%   scanning - boolean indicating if scanning mode is active

if scanning
    % Close trigger port
    fclose(s);
    delete(s);
end

end 