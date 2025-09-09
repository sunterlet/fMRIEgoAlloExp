#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Wrapper Timing Script
Tests the timing gaps in wrapper scripts by running just one trial of each type.
This will help verify that the wrapper approach eliminates timing issues.

Usage: python test_wrapper_timing.py --participant PARTICIPANT_ID --run RUN_NUMBER
"""

import subprocess
import sys
import os
import time
import argparse
from datetime import datetime

# Constants
TR = 2.01  # TR in seconds
TOTAL_TRIALS = 2  # 1 snake + 1 one_target trial

def run_trial(trial_number, trial_type, participant_id, run_number):
    """Run a single trial and return timing information."""
    
    print(f"\n{'='*60}")
    print(f"TRIAL {trial_number}/{TOTAL_TRIALS}: {trial_type.upper()}")
    print(f"{'='*60}")
    
    trial_start_time = time.time()
    
    # Determine which script to run
    if trial_type == "snake":
        script_name = "snake.py"
    elif trial_type == "one_target":
        script_name = "one_target.py"
    else:
        raise ValueError(f"Unknown trial type: {trial_type}")
    
    # Construct command
    cmd = [
        sys.executable,
        script_name,
        "fmri",
        "--participant", participant_id,
        "--run", str(run_number),
        "--trial", str(trial_number),
        "--total-trials", str(TOTAL_TRIALS)
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Trial start time: {datetime.fromtimestamp(trial_start_time).strftime('%H:%M:%S.%f')[:-3]}")
    
    try:
        # Run the trial
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        trial_end_time = time.time()
        trial_duration = trial_end_time - trial_start_time
        
        print(f"Trial end time: {datetime.fromtimestamp(trial_end_time).strftime('%H:%M:%S.%f')[:-3]}")
        print(f"Trial duration: {trial_duration:.3f}s ({trial_duration/TR:.2f} TRs)")
        
        if result.returncode != 0:
            print(f"WARNING: {trial_type} trial returned error code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        
        return {
            'trial_number': trial_number,
            'trial_type': trial_type,
            'start_time': trial_start_time,
            'end_time': trial_end_time,
            'duration': trial_duration,
            'return_code': result.returncode
        }
        
    except Exception as e:
        print(f"ERROR running {trial_type} trial: {e}")
        trial_end_time = time.time()
        trial_duration = trial_end_time - trial_start_time
        
        return {
            'trial_number': trial_number,
            'trial_type': trial_type,
            'start_time': trial_start_time,
            'end_time': trial_end_time,
            'duration': trial_duration,
            'return_code': -1,
            'error': str(e)
        }

def test_wrapper_timing(participant_id, run_number):
    """Test timing with just one trial of each type."""
    
    print(f"\n{'='*80}")
    print(f"WRAPPER TIMING TEST")
    print(f"Participant: {participant_id}")
    print(f"Run: {run_number}")
    print(f"Total Trials: {TOTAL_TRIALS}")
    print(f"TR: {TR} seconds")
    print(f"Note: Trial durations are randomized by individual scripts")
    print(f"{'='*80}")
    
    # Initialize timing variables
    block_start_time = time.time()
    trial_results = []
    
    print(f"Block start time: {datetime.fromtimestamp(block_start_time).strftime('%H:%M:%S.%f')[:-3]}")
    
    # Define trial sequence (just one of each type)
    trial_sequence = [
        ("snake", 1),      # Trial 1: Snake
        ("one_target", 2)  # Trial 2: One Target
    ]
    
    # Run all trials
    for trial_type, trial_number in trial_sequence:
        result = run_trial(trial_number, trial_type, participant_id, run_number)
        trial_results.append(result)
        
        # Small delay to ensure proper separation between trials
        time.sleep(0.1)
    
    # Calculate block timing
    block_end_time = time.time()
    block_duration = block_end_time - block_start_time
    
    print(f"\n{'='*80}")
    print(f"WRAPPER TIMING TEST COMPLETE")
    print(f"{'='*80}")
    
    # Overall timing
    print(f"Block start: {datetime.fromtimestamp(block_start_time).strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Block end: {datetime.fromtimestamp(block_end_time).strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Block duration: {block_duration:.3f} seconds ({block_duration/TR:.2f} TRs)")
    
    # Trial-by-trial analysis
    print(f"\nTRIAL TIMINGS:")
    total_trial_time = 0
    for result in trial_results:
        print(f"  Trial {result['trial_number']} ({result['trial_type']}): {result['duration']:.3f}s ({result['duration']/TR:.2f} TRs)")
        total_trial_time += result['duration']
    
    print(f"Total trial time: {total_trial_time:.3f}s ({total_trial_time/TR:.2f} TRs)")
    
    # Gap analysis
    print(f"\nGAP ANALYSIS:")
    if len(trial_results) > 1:
        gap = trial_results[1]['start_time'] - trial_results[0]['end_time']
        if gap > 0.1:  # More than 100ms gap
            print(f"  WARNING: Gap between Trial {trial_results[0]['trial_number']} and Trial {trial_results[1]['trial_number']}: {gap:.3f}s ({gap/TR:.2f} TRs)")
        else:
            print(f"  OK: Gap between Trial {trial_results[0]['trial_number']} and Trial {trial_results[1]['trial_number']}: {gap:.3f}s ({gap/TR:.2f} TRs)")
    
    # Overhead analysis
    overhead = block_duration - total_trial_time
    print(f"Overhead (non-trial time): {overhead:.3f}s ({overhead/TR:.2f} TRs)")
    
    if overhead > 1.0:  # More than 1 second overhead
        print(f"  WARNING: High overhead detected!")
    else:
        print(f"  OK: Overhead is reasonable.")
    
    # Overall timing analysis
    print(f"\nOVERALL TIMING ANALYSIS:")
    actual_total_trs = block_duration / TR
    print(f"Actual total TRs: {actual_total_trs:.2f}")
    print(f"Block duration: {block_duration:.3f} seconds")
    print(f"Average trial duration: {total_trial_time/TOTAL_TRIALS:.3f} seconds")
    print(f"Average trial duration in TRs: {(total_trial_time/TOTAL_TRIALS)/TR:.2f} TRs")
    
    # Save detailed timing log
    log_filename = f"wrapper_timing_test_log_{participant_id}_run{run_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    save_timing_log(log_filename, block_start_time, trial_results)
    print(f"\nDetailed timing log saved to: {log_filename}")
    
    print(f"\n{'='*80}")
    print(f"WRAPPER TIMING TEST COMPLETE")
    print(f"{'='*80}")

def save_timing_log(filename, block_start_time, trial_results):
    """Save detailed timing log to CSV file."""
    
    import csv
    
    # Use centralized results directory if available, otherwise use local results directory
    centralized_results_dir = os.getenv('CENTRALIZED_RESULTS_DIR')
    if centralized_results_dir and os.path.exists(centralized_results_dir):
        # Create full path in centralized directory
        full_filename = os.path.join(centralized_results_dir, os.path.basename(filename))
        print(f"Using centralized results directory: {centralized_results_dir}")
    else:
        # Fall back to local results directory
        full_filename = filename
        print(f"Using local results directory: {os.path.dirname(filename)}")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(full_filename), exist_ok=True)
    
    with open(full_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Trial', 'Type', 'Start Time', 'End Time', 'Duration (s)', 'Duration (TRs)', 'Return Code'])
        
        # Write trial results
        for result in trial_results:
            writer.writerow([
                result['trial_number'],
                result['trial_type'],
                datetime.fromtimestamp(result['start_time']).strftime('%H:%M:%S.%f')[:-3],
                datetime.fromtimestamp(result['end_time']).strftime('%H:%M:%S.%f')[:-3],
                f"{result['duration']:.3f}",
                f"{result['duration']/TR:.2f}",
                result['return_code']
            ])
        
        # Write gap analysis
        if len(trial_results) > 1:
            writer.writerow([])  # Empty row
            writer.writerow(['GAP ANALYSIS'])
            writer.writerow(['Trial 1', 'Trial 2', 'Gap (s)', 'Gap (TRs)'])
            
            gap = trial_results[1]['start_time'] - trial_results[0]['end_time']
            writer.writerow([
                f"{trial_results[0]['trial_number']} ({trial_results[0]['trial_type']})",
                f"{trial_results[1]['trial_number']} ({trial_results[1]['trial_type']})",
                f"{gap:.3f}",
                f"{gap/TR:.2f}"
            ])

def main():
    """Main function to parse arguments and run the test."""
    
    parser = argparse.ArgumentParser(description='Wrapper Timing Test')
    parser.add_argument('--participant', '-p', required=True,
                       help='Participant ID')
    parser.add_argument('--run', '-r', type=int, required=True,
                       help='Run number')
    
    args = parser.parse_args()
    
    # Change to the exploration directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run the test
    test_wrapper_timing(args.participant, args.run)

if __name__ == "__main__":
    main() 