#!/usr/bin/env python3
"""
Wrapper script to run multi_arena.py in fMRI mode.
Usage: python multi_arena_in.py [participant_id] [run_number] [trial_number] [total_trials] [arena_name] [screen_number]
"""

import sys
import subprocess
import os

def main():
    # Get parameters from command line
    if len(sys.argv) < 5:
        print("Usage: python multi_arena_in.py [participant_id] [run_number] [trial_number] [total_trials] [arena_name] [screen_number]")
        print("Example: python multi_arena_in.py TS263 1 3 4 arena1 0")
        sys.exit(1)
    
    participant_id = sys.argv[1]
    run_number = sys.argv[2]
    trial_number = sys.argv[3]
    total_trials = sys.argv[4]
    
    # Get arena name from command line or use default
    if len(sys.argv) > 5:
        arena_name = sys.argv[5]
    else:
        arena_name = "arena1"
    
    # Get screen number from command line or use default
    if len(sys.argv) > 6:
        screen_number = sys.argv[6]
    else:
        screen_number = None
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the command with trigger functionality
    cmd = [
        sys.executable,
        os.path.join(script_dir, "multi_arena.py"),
        "fmri",
        "--participant", participant_id,
        "--run", run_number,
        "--trial", trial_number,
        "--total-trials", total_trials,
        "--arena", arena_name,
    ]
    
    # Add screen parameter if provided
    if screen_number is not None:
        cmd.extend(["--screen", screen_number])
    
    if scanning:
        cmd.extend(["--scanning", "--com", "com4", "--tr", "2.01"])
    
    print(f"Running multi_arena fMRI session for participant: {participant_id}, run: {run_number}, trial: {trial_number}/{total_trials}, arena: {arena_name}")
    if screen_number is not None:
        print(f"Display will be on screen: {screen_number}")
    print(f"Command: {' '.join(cmd)}")
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True)
        print("Multi-arena fMRI session completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running multi_arena fMRI session: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 