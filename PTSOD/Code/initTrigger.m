function [s, sync] = initTrigger(scanning, com)
% INIT TRIGGER - Initialize scanner trigger connection
% 
% This function initializes the serial connection for scanner trigger handling
% 
% Inputs:
%   scanning - boolean indicating if scanning mode is active
%   com      - serial port identifier (e.g., 'COM1')
% 
% Outputs:
%   s        - serial port object (empty if not scanning)
%   sync     - trigger counter (0 if not scanning)

% Initialize variables
s = [];
sync = 0;

%% TRIGGER INITIALIZATION
if scanning
    % Initialize serial connection for trigger
    s = serial(com, 'BaudRate', 9600);
    fopen(s);
    sync = 0;
end

end 