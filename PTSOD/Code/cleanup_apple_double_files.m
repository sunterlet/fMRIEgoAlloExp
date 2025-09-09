function cleanup_apple_double_files()
%% CLEANUP_APPLE_DOUBLE_FILES
% This function removes AppleDouble metadata files (._*) that are created
% when copying files from macOS to Windows. These files cause errors in
% the PTSOD experiment.
%
% Usage: cleanup_apple_double_files()
%
% The function will:
% 1. Find all ._* files in the PTSOD directories
% 2. Display them for review
% 3. Optionally delete them (with confirmation)

fprintf('=== AppleDouble File Cleanup Utility ===\n\n');

% Get the current directory and setup PTSOD paths
currentDir = pwd;
[projectRoot, ~, stimuliPath, instructionsPath] = setupPTSOD();

fprintf('Project Root: %s\n', projectRoot);
fprintf('Stimuli Path: %s\n', stimuliPath);
fprintf('Instructions Path: %s\n\n', instructionsPath);

% Directories to check for ._* files
directories_to_check = {
    fullfile(stimuliPath, 'nomemory_screens');
    fullfile(stimuliPath, 'memory_screens');
    fullfile(stimuliPath, 'nomemory_screens_HE');
    fullfile(stimuliPath, 'memory_screens_HE');
    fullfile(stimuliPath, 'white_png');
    fullfile(instructionsPath, 'instructions_practice_fmri1');
    fullfile(instructionsPath, 'instructions_practice_fmri');
};

% Find all ._* files
all_apple_double_files = {};
total_count = 0;

fprintf('Searching for AppleDouble metadata files...\n');

for i = 1:length(directories_to_check)
    dir_path = directories_to_check{i};
    if exist(dir_path, 'dir')
        % Find all ._* files in this directory
        files = dir(fullfile(dir_path, '._*'));
        if ~isempty(files)
            fprintf('Found %d ._* files in: %s\n', length(files), dir_path);
            for j = 1:length(files)
                file_path = fullfile(dir_path, files(j).name);
                all_apple_double_files{end+1} = file_path;
                total_count = total_count + 1;
            end
        end
    else
        fprintf('Directory not found: %s\n', dir_path);
    end
end

fprintf('\nTotal AppleDouble files found: %d\n\n', total_count);

if total_count == 0
    fprintf('✅ No AppleDouble files found. Your PTSOD experiment should work correctly.\n');
    return;
end

% Display all found files
fprintf('AppleDouble files found:\n');
for i = 1:length(all_apple_double_files)
    fprintf('  %s\n', all_apple_double_files{i});
end

% Ask user if they want to delete these files
fprintf('\nThese files are causing errors in your PTSOD experiment.\n');
fprintf('They can be safely deleted as they are just metadata files.\n\n');

response = input('Do you want to delete these files? (y/n): ', 's');

if strcmpi(response, 'y') || strcmpi(response, 'yes')
    fprintf('\nDeleting AppleDouble files...\n');
    deleted_count = 0;
    
    for i = 1:length(all_apple_double_files)
        try
            delete(all_apple_double_files{i});
            fprintf('  Deleted: %s\n', all_apple_double_files{i});
            deleted_count = deleted_count + 1;
        catch ME
            fprintf('  Error deleting %s: %s\n', all_apple_double_files{i}, ME.message);
        end
    end
    
    fprintf('\n✅ Successfully deleted %d out of %d AppleDouble files.\n', deleted_count, total_count);
    fprintf('Your PTSOD experiment should now work correctly.\n');
    
else
    fprintf('\nNo files were deleted.\n');
    fprintf('You can run this function again later to clean up the files.\n');
    fprintf('Note: The PTSOD experiment may continue to have errors until these files are removed.\n');
end

fprintf('\n=== Cleanup Complete ===\n');

end
