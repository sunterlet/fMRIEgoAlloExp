#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Logging Module for fMRI Navigation Experiments
Provides consistent file saving behavior across all experiment types.
"""

import os
import csv
import datetime
from typing import List, Dict, Any

class UnifiedLogger:
    """Unified logging class for consistent data saving across experiments."""
    
    def __init__(self, participant_id: str, experiment_type: str, mode: str = 'practice'):
        """
        Initialize the unified logger.
        
        Args:
            participant_id: Participant ID (e.g., 'test', 'TS263')
            experiment_type: Type of experiment ('one_target', 'multi_arena', 'snake')
            mode: Experiment mode ('practice' or 'fmri')
        """
        self.participant_id = participant_id
        self.experiment_type = experiment_type
        self.mode = mode
        
        # Set up results directory
        self._setup_results_directory()
        
        # Set up filenames
        self._setup_filenames()
    
    def _setup_results_directory(self):
        """Set up the results directory using centralized approach."""
        centralized_results_dir = os.getenv('CENTRALIZED_RESULTS_DIR')
        if centralized_results_dir and os.path.exists(centralized_results_dir):
            self.results_dir = os.path.join(centralized_results_dir, self.participant_id)
            print(f"Using centralized results directory: {self.results_dir}")
        else:
            self.results_dir = os.path.join(os.path.dirname(__file__), "results")
            print(f"Using local results directory: {self.results_dir}")
        
        # Ensure directory exists
        os.makedirs(self.results_dir, exist_ok=True)
    
    def _setup_filenames(self):
        """Set up filenames based on experiment type and mode."""
        if self.mode == 'fmri':
            # fMRI mode: trial-specific files
            if self.experiment_type == 'one_target':
                self.continuous_filename = os.path.join(self.results_dir, f"{self.participant_id}_one_target_run_continuous.csv")
                self.discrete_filename = os.path.join(self.results_dir, f"{self.participant_id}_one_target_run_discrete.csv")
            elif self.experiment_type == 'multi_arena':
                self.continuous_filename = os.path.join(self.results_dir, f"{self.participant_id}_multi_arena_trial{getattr(self, 'current_trial', 1)}_continuous.csv")
                self.discrete_filename = os.path.join(self.results_dir, f"{self.participant_id}_multi_arena_trial{getattr(self, 'current_trial', 1)}_discrete.csv")
            elif self.experiment_type == 'snake':
                self.continuous_filename = os.path.join(self.results_dir, f"{self.participant_id}_snake_run{getattr(self, 'run_number', 1)}_continuous.csv")
                self.discrete_filename = os.path.join(self.results_dir, f"{self.participant_id}_snake_run{getattr(self, 'run_number', 1)}_discrete.csv")
        else:
            # Practice mode: unified single files
            self.continuous_filename = os.path.join(self.results_dir, f"{self.participant_id}_{self.experiment_type}_practice_continuous_log.csv")
            self.discrete_filename = os.path.join(self.results_dir, f"{self.participant_id}_{self.experiment_type}_practice_discrete_log.csv")
    
    def save_discrete_log(self, logs: List[Dict[str, Any]], fieldnames: List[str] = None):
        """
        Save discrete log data to CSV file.
        
        Args:
            logs: List of discrete log entries
            fieldnames: Column names for the CSV (if None, will be inferred from first log entry)
        """
        if not logs:
            return
        
        # Use provided fieldnames or infer from first log entry
        if fieldnames is None:
            fieldnames = list(logs[0].keys())
        
        # For practice mode, delete previous file to ensure clean start
        if self.mode == 'practice' and os.path.exists(self.discrete_filename):
            try:
                os.remove(self.discrete_filename)
                print(f"Deleted previous discrete file: {self.discrete_filename}")
            except Exception as e:
                print(f"Warning: Could not delete previous discrete file {self.discrete_filename}: {e}")
        
        try:
            with open(self.discrete_filename, "w", newline="", encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for log in logs:
                    writer.writerow(log)
            print(f"Discrete log saved successfully to: {self.discrete_filename}")
        except Exception as e:
            print(f"Error saving discrete log: {e}")
            self._save_backup_file(logs, fieldnames, self.discrete_filename, "discrete")
    
    def save_continuous_log(self, logs: List[Dict[str, Any]], fieldnames: List[str] = None):
        """
        Save continuous log data to CSV file.
        
        Args:
            logs: List of continuous log entries
            fieldnames: Column names for the CSV (if None, will be inferred from first log entry)
        """
        if not logs:
            return
        
        # Use provided fieldnames or infer from first log entry
        if fieldnames is None:
            fieldnames = list(logs[0].keys())
        
        # For practice mode, delete previous file to ensure clean start
        if self.mode == 'practice' and os.path.exists(self.continuous_filename):
            try:
                os.remove(self.continuous_filename)
                print(f"Deleted previous continuous file: {self.continuous_filename}")
            except Exception as e:
                print(f"Warning: Could not delete previous continuous file {self.continuous_filename}: {e}")
        
        try:
            with open(self.continuous_filename, "w", newline="", encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in logs:
                    # Only write fields that exist in the row
                    filtered_row = {k: v for k, v in row.items() if k in fieldnames}
                    writer.writerow(filtered_row)
            print(f"Continuous log saved successfully to: {self.continuous_filename}")
        except Exception as e:
            print(f"Error saving continuous log: {e}")
            self._save_backup_file(logs, fieldnames, self.continuous_filename, "continuous")
    
    def append_continuous_log(self, log_entry: Dict[str, Any]):
        """
        Append a single continuous log entry to the file.
        Used for real-time logging during experiments.
        
        Args:
            log_entry: Single log entry to append
        """
        try:
            # Determine fieldnames from the log entry
            fieldnames = list(log_entry.keys())
            
            # Check if file exists to determine if we need to write header
            file_exists = os.path.exists(self.continuous_filename)
            
            with open(self.continuous_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(log_entry)
        except Exception as e:
            print(f"Error appending continuous log entry: {e}")
    
    def _save_backup_file(self, logs: List[Dict[str, Any]], fieldnames: List[str], original_filename: str, log_type: str):
        """Save a backup file with timestamp if original save fails."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = original_filename.replace('.csv', f'_backup_{timestamp}.csv')
        
        try:
            with open(backup_filename, "w", newline="", encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for log in logs:
                    if log_type == "continuous":
                        # Filter fields for continuous logs
                        filtered_log = {k: v for k, v in log.items() if k in fieldnames}
                        writer.writerow(filtered_log)
                    else:
                        writer.writerow(log)
            print(f"{log_type.capitalize()} log saved as backup to: {backup_filename}")
        except Exception as backup_e:
            print(f"Failed to save backup file: {backup_e}")
    
    def get_filenames(self):
        """Get the current filenames for debugging purposes."""
        return {
            'continuous': self.continuous_filename,
            'discrete': self.discrete_filename
        }

