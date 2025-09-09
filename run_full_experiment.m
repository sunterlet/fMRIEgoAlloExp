%% Full fMRI Experiment - Egocentric Allocentric Translation
% Master file to run both practice and fMRI sessions

fprintf('=== Egocentric Allocentric Translation fMRI Experiment ===\n');
fprintf('This script will run both practice and fMRI sessions.\n\n');

% Ask user which sessions to run
fprintf('Select sessions to run:\n');
fprintf('1. Practice sessions only (outside magnet)\n');
fprintf('2. fMRI sessions only (inside magnet)\n');
fprintf('3. Both practice and fMRI sessions\n');
fprintf('4. Exit\n');

choice = input('\nEnter your choice (1-4): ');

switch choice
    case 1
        fprintf('\nRunning practice sessions...\n');
        practice_sessions;
        
    case 2
        fprintf('\nRunning fMRI sessions...\n');
        fmri_sessions;
        
    case 3
        fprintf('\nRunning both practice and fMRI sessions...\n');
        fprintf('\n=== PRACTICE SESSIONS ===\n');
        practice_sessions;
        
        fprintf('\n=== fMRI SESSIONS ===\n');
        fmri_sessions;
        
    case 4
        fprintf('Exiting...\n');
        return;
        
    otherwise
        fprintf('Invalid choice. Exiting...\n');
        return;
end

fprintf('\n=== EXPERIMENT COMPLETED ===\n'); 