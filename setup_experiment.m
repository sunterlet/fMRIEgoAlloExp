%% Setup Script for fMRI Navigation Experiment
% This script sets up the experiment environment on a new computer
% Run this before running fmri_session.m

fprintf('=== fMRI Navigation Experiment Setup ===\n\n');

%% Check MATLAB Version
matlab_version = version('-release');
fprintf('MATLAB Version: %s\n', matlab_version);

% Check if Psychtoolbox is installed
try
    PsychtoolboxVersion;
    fprintf('✓ Psychtoolbox is installed\n');
catch
    fprintf('⚠ WARNING: Psychtoolbox not found!\n');
    fprintf('Please install Psychtoolbox from: http://psychtoolbox.org/\n');
    fprintf('Or run: DownloadPsychtoolbox() in MATLAB\n\n');
end

%% Check Python Installation
fprintf('\n=== Checking Python Installation ===\n');

% Try to detect Python
python_commands = {'python3', 'python', 'py'};
python_found = false;
python_cmd = '';

for i = 1:length(python_commands)
    try
        [status, result] = system(sprintf('%s --version', python_commands{i}));
        if status == 0
            python_cmd = python_commands{i};
            python_found = true;
            fprintf('✓ Python found: %s\n', result);
            break;
        end
    catch
        continue;
    end
end

if ~python_found
    fprintf('⚠ WARNING: Python not found!\n');
    fprintf('Please install Python 3.8+ from: https://python.org/\n');
    fprintf('Make sure to check "Add Python to PATH" during installation\n\n');
else
    % Check if required packages are installed
    fprintf('\n=== Checking Python Dependencies ===\n');
    
    required_packages = {'pygame', 'numpy', 'pandas', 'matplotlib'};
    missing_packages = {};
    
    for i = 1:length(required_packages)
        try
            [status, ~] = system(sprintf('%s -c "import %s"' , python_cmd, required_packages{i}));
            if status == 0
                fprintf('✓ %s is installed\n', required_packages{i});
            else
                fprintf('✗ %s is missing\n', required_packages{i});
                missing_packages{end+1} = required_packages{i};
            end
        catch
            fprintf('✗ %s is missing\n', required_packages{i});
            missing_packages{end+1} = required_packages{i};
        end
    end
    
    if ~isempty(missing_packages)
        fprintf('\n⚠ Missing Python packages detected!\n');
        fprintf('To install missing packages, run:\n');
        fprintf('  %s -m pip install -r requirements.txt\n\n', python_cmd);
    else
        fprintf('\n✓ All Python dependencies are installed!\n');
    end
end

%% Check Required Directories
fprintf('\n=== Checking Required Directories ===\n');

required_dirs = {
    'exploration', 'PTSOD', 'arenas_new_icons', 'sounds', ...
    'exploration/sounds', 'exploration/Instructions-he', ...
    'PTSOD/Code', 'PTSOD/Instructions_HE', 'PTSOD/Stimuli'
};

all_dirs_exist = true;
for i = 1:length(required_dirs)
    if exist(required_dirs{i}, 'dir')
        fprintf('✓ %s\n', required_dirs{i});
    else
        fprintf('✗ %s (MISSING!)\n', required_dirs{i});
        all_dirs_exist = false;
    end
end

if ~all_dirs_exist
    fprintf('\n⚠ WARNING: Some required directories are missing!\n');
    fprintf('Please ensure you have downloaded the complete repository.\n\n');
end

%% Check Required Files
fprintf('\n=== Checking Required Files ===\n');

required_files = {
    'fmri_session.m', 'select_screen.m', 'combine_session_data.m', ...
    'exploration/run_snake_game.m', 'exploration/one_target_run.m', ...
    'exploration/full_arena_run.m', 'exploration/trigger_manager.m', ...
    'exploration/snake.py', 'exploration/one_target.py', 'exploration/multi_arena.py', ...
    'requirements.txt'
};

all_files_exist = true;
for i = 1:length(required_files)
    if exist(required_files{i}, 'file')
        fprintf('✓ %s\n', required_files{i});
    else
        fprintf('✗ %s (MISSING!)\n', required_files{i});
        all_files_exist = false;
    end
end

if ~all_files_exist
    fprintf('\n⚠ WARNING: Some required files are missing!\n');
    fprintf('Please ensure you have downloaded the complete repository.\n\n');
end

%% Create Results Directory
fprintf('\n=== Setting up Results Directory ===\n');

results_dir = fullfile(pwd, 'Results');
if ~exist(results_dir, 'dir')
    mkdir(results_dir);
    fprintf('✓ Created Results directory: %s\n', results_dir);
else
    fprintf('✓ Results directory already exists: %s\n', results_dir);
end

%% Test Screen Selection
fprintf('\n=== Testing Screen Selection ===\n');
fprintf('This will open a test pattern to help you select the correct screen.\n');
fprintf('Press any key to continue or ESC to skip...\n');

try
    % Test if we can initialize Psychtoolbox
    Screen('Preference', 'SkipSyncTests', 1);  % Skip sync tests for setup
    screens = Screen('Screens');
    fprintf('✓ Found %d screen(s)\n', length(screens));
    
    % Ask if user wants to test screen selection
    response = input('Test screen selection? (y/n): ', 's');
    if strcmpi(response, 'y') || strcmpi(response, 'yes')
        selectedScreen = select_screen();
        fprintf('✓ Screen selection test completed\n');
    else
        fprintf('Skipped screen selection test\n');
    end
catch ME
    fprintf('⚠ Screen selection test failed: %s\n', ME.message);
    fprintf('This might be due to display issues or missing Psychtoolbox\n');
end

%% Summary
fprintf('\n=== Setup Summary ===\n');

if python_found && all_dirs_exist && all_files_exist
    fprintf('✓ Setup completed successfully!\n');
    fprintf('You can now run: fmri_session\n\n');
else
    fprintf('⚠ Setup completed with warnings.\n');
    fprintf('Please address the issues above before running the experiment.\n\n');
end

fprintf('Next steps:\n');
fprintf('1. If Python packages are missing, run: %s -m pip install -r requirements.txt\n', python_cmd);
fprintf('2. If Psychtoolbox is missing, install it from: http://psychtoolbox.org/\n');
fprintf('3. Run the experiment: fmri_session\n\n');

fprintf('For detailed installation instructions, see: README_INSTALLATION.md\n');
