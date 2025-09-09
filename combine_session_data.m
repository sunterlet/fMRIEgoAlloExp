function combine_session_data(participant_id)

    % Data Combination Function
    % This function combines all trial data into single files per run type
    % Run this manually after the session is complete

    fprintf('\n=== COMBINING SESSION DATA ===\n');
    fprintf('Participant: %s\n', participant_id);
    
    % Get centralized results directory
    centralized_results_dir = fullfile(pwd, 'Results');
    subid_dir = fullfile(centralized_results_dir, participant_id);
    
    if ~exist(subid_dir, 'dir')
        fprintf('Error: Participant directory not found: %s\n', subid_dir);
        return;
    end
    
    fprintf('Results directory: %s\n', subid_dir);
    
    % Define run types and their patterns
    run_types = {
        'OT', 'OT', 'One Target Run';
        'FA', 'FA', 'Full Arena Run'
    };
    
    % Define trial types for each run
    trial_types = {
        'ot', 'ot', 'One Target trials';
        'snake', 'snake', 'Snake trials';
        'fa', 'fa', 'Full Arena trials'
    };
    
    for run_idx = 1:size(run_types, 1)
        run_code = run_types{run_idx, 1};
        run_pattern = run_types{run_idx, 2};
        run_name = run_types{run_idx, 3};
        
        fprintf('\n--- Processing %s ---\n', run_name);
        
        % Group files by trial type
        for trial_idx = 1:size(trial_types, 1)
            trial_code = trial_types{trial_idx, 1};
            trial_pattern = trial_types{trial_idx, 2};
            trial_name = trial_types{trial_idx, 3};
            
            % Find continuous files for this trial type
            continuous_pattern = sprintf('%s_%s_%s*continuous*.csv', participant_id, run_code, trial_pattern);
            continuous_files = dir(fullfile(subid_dir, continuous_pattern));
            
            % Find discrete files for this trial type
            discrete_pattern = sprintf('%s_%s_%s*discrete*.csv', participant_id, run_code, trial_pattern);
            discrete_files = dir(fullfile(subid_dir, discrete_pattern));
            
            if ~isempty(continuous_files) || ~isempty(discrete_files)
                fprintf('  Processing %s trials...\n', trial_name);
                
                % Combine continuous files
                if ~isempty(continuous_files)
                    fprintf('    Found %d continuous files\n', length(continuous_files));
                    combined_continuous = [];
                    
                    for file_idx = 1:length(continuous_files)
                        file_path = fullfile(continuous_files(file_idx).folder, continuous_files(file_idx).name);
                        try
                            % Read CSV file
                            data = readtable(file_path);
                            combined_continuous = [combined_continuous; data];
                            fprintf('      Added: %s\n', continuous_files(file_idx).name);
                        catch ME
                            fprintf('      Error reading %s: %s\n', continuous_files(file_idx).name, ME.message);
                        end
                    end
                    
                    % Save combined continuous file
                    if ~isempty(combined_continuous)
                        output_filename = fullfile(subid_dir, sprintf('%s_%s_%s_continuous.csv', participant_id, run_code, trial_code));
                        writetable(combined_continuous, output_filename);
                        fprintf('    Saved combined continuous: %s\n', output_filename);
                        
                        % Delete individual files
                        for file_idx = 1:length(continuous_files)
                            file_path = fullfile(continuous_files(file_idx).folder, continuous_files(file_idx).name);
                            delete(file_path);
                            fprintf('      Deleted: %s\n', continuous_files(file_idx).name);
                        end
                    end
                end
                
                % Combine discrete files
                if ~isempty(discrete_files)
                    fprintf('    Found %d discrete files\n', length(discrete_files));
                    combined_discrete = [];
                    
                    for file_idx = 1:length(discrete_files)
                        file_path = fullfile(discrete_files(file_idx).folder, discrete_files(file_idx).name);
                        try
                            % Read CSV file
                            data = readtable(file_path);
                            combined_discrete = [combined_discrete; data];
                            fprintf('      Added: %s\n', discrete_files(file_idx).name);
                        catch ME
                            fprintf('      Error reading %s: %s\n', discrete_files(file_idx).name, ME.message);
                        end
                    end
                    
                    % Save combined discrete file
                    if ~isempty(combined_discrete)
                        output_filename = fullfile(subid_dir, sprintf('%s_%s_%s_discrete.csv', participant_id, run_code, trial_code));
                        writetable(combined_discrete, output_filename);
                        fprintf('    Saved combined discrete: %s\n', output_filename);
                        
                        % Delete individual files
                        for file_idx = 1:length(discrete_files)
                            file_path = fullfile(discrete_files(file_idx).folder, discrete_files(file_idx).name);
                            delete(file_path);
                            fprintf('      Deleted: %s\n', discrete_files(file_idx).name);
                        end
                    end
                end
            end
        end
    end
    
    fprintf('\n=== DATA COMBINATION COMPLETE ===\n');
    fprintf('All trial data has been combined into single files per run type.\n');
    fprintf('Individual trial files have been deleted.\n');
end
