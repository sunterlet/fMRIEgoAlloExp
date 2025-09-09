#!/usr/bin/env python3
"""
Script to combine all multi-arena log files into single files
"""

import pandas as pd
import os
import glob
import time

def combine_all_multi_arena_logs(participant_id, results_dir):
    """Combine all multi-arena log files into single files."""
    
    subid_dir = os.path.join(results_dir, participant_id)
    if not os.path.exists(subid_dir):
        print(f"Warning: SubID directory not found: {subid_dir}")
        return
    
    # Find all multi-arena continuous log files
    continuous_pattern = os.path.join(subid_dir, f"{participant_id}_multi_arena_practice_continuous_log_*.csv")
    continuous_files = glob.glob(continuous_pattern)
    
    # Find all multi-arena discrete log files
    discrete_pattern = os.path.join(subid_dir, f"{participant_id}_multi_arena_practice_discrete_log_*.csv")
    discrete_files = glob.glob(discrete_pattern)
    
    # Sort files by creation time to preserve temporal order
    continuous_files.sort(key=lambda x: os.path.getctime(x))
    discrete_files.sort(key=lambda x: os.path.getctime(x))
    
    if not continuous_files and not discrete_files:
        print("No multi-arena log files found to combine.")
        return
    
    print(f"Found {len(continuous_files)} continuous log files and {len(discrete_files)} discrete log files to combine.")
    print("Files will be combined in temporal order (by creation time):")
    for i, file_path in enumerate(continuous_files, 1):
        filename = os.path.basename(file_path)
        creation_time = os.path.getctime(file_path)
        print(f"  {i}. {filename} (created: {time.ctime(creation_time)})")
    
    # Combine continuous logs
    combined_continuous = []
    for file_path in continuous_files:
        try:
            # Read the arena-specific continuous log with UTF-8 encoding
            arena_data = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # Add RoundName column if it doesn't exist
            if 'RoundName' not in arena_data.columns:
                # Extract arena name from filename
                filename = os.path.basename(file_path)
                parts = filename.split('_')
                
                # Find the arena name - it's the last part after 'log'
                arena_name = ''
                for i, part in enumerate(parts):
                    if part == 'log':
                        if i + 1 < len(parts):
                            arena_name = parts[i + 1].replace('.csv', '')
                        break
                
                # If we couldn't find it, use the last part as fallback
                if not arena_name and parts:
                    arena_name = parts[-1].replace('.csv', '')
                
                # Create RoundName column
                arena_data['RoundName'] = arena_name
            
            combined_continuous.append(arena_data)
            print(f"  Added: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Warning: Could not read continuous log file {file_path}: {e}")
    
    # Combine discrete logs
    combined_discrete = []
    for file_path in discrete_files:
        try:
            # Read the arena-specific discrete log with UTF-8 encoding
            arena_data = pd.read_csv(file_path, encoding='utf-8-sig')
            combined_discrete.append(arena_data)
            print(f"  Added: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"Warning: Could not read discrete log file {file_path}: {e}")
    
    # Save combined files with UTF-8 encoding
    if combined_continuous:
        combined_continuous_df = pd.concat(combined_continuous, ignore_index=True)
        combined_continuous_filename = os.path.join(subid_dir, f"{participant_id}_multi_arena_practice_continuous_log.csv")
        
        # Columns are already in correct order from multi_arena.py: RealTime, trial_time, trial, RoundName, visibility, phase, event, x, y, rotation_angle
        combined_continuous_df.to_csv(combined_continuous_filename, index=False, encoding='utf-8-sig')
        print(f"[OK] Combined continuous log saved: {combined_continuous_filename}")
    
    if combined_discrete:
        combined_discrete_df = pd.concat(combined_discrete, ignore_index=True)
        combined_discrete_filename = os.path.join(subid_dir, f"{participant_id}_multi_arena_practice_discrete_log.csv")
        combined_discrete_df.to_csv(combined_discrete_filename, index=False, encoding='utf-8-sig')
        print(f"[OK] Combined discrete log saved: {combined_discrete_filename}")
    
    # Delete individual arena files after successful combination
    if combined_continuous and combined_discrete:
        print("\nDeleting individual arena files...")
        for file_path in continuous_files:
            os.remove(file_path)
            print(f"  Deleted: {os.path.basename(file_path)}")
        for file_path in discrete_files:
            os.remove(file_path)
            print(f"  Deleted: {os.path.basename(file_path)}")
        print("[OK] All individual arena files deleted.")

if __name__ == "__main__":
    # Set parameters
    participant_id = 'test'
    results_dir = r'U:\sunt\Navigation\fMRI\Results'
    
    print(f"Combining multi-arena log files for participant: {participant_id}")
    print(f"Results directory: {results_dir}")
    
    # Run the combination function
    combine_all_multi_arena_logs(participant_id, results_dir)
    
    print("Combination complete!")
