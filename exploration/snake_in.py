#!/usr/bin/env python3
"""
Wrapper script for running snake game in fMRI mode (inside magnet).
This script can be called from MATLAB for block design experiments.
"""

import sys
import os
import subprocess

def run_fmri_session(participant_id="TEST", run_number=1, trial_number=1, total_trials=1, screen_number=None):
    """
    Run the snake game in fMRI mode.
    
    Args:
        participant_id (str): Participant initials/ID
        run_number (int): Run number for the block design
        trial_number (int): Current trial number in sequence
        total_trials (int): Total number of trials in sequence
        screen_number (int, optional): Screen number to display on
    """
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        snake_script = os.path.join(script_dir, "snake.py")
        
        # Build command with optional screen parameter
        cmd = [sys.executable, snake_script, "fmri", "--participant", participant_id, "--run", str(run_number), "--trial", str(trial_number), "--total-trials", str(total_trials)]
        
        if screen_number is not None:
            cmd.extend(["--screen", str(screen_number)])
        
        print(f"Running snake fMRI session for participant: {participant_id}, run: {run_number}")
        if screen_number is not None:
            print(f"Display will be on screen: {screen_number}")
        print(f"Command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(cmd, check=True)
        
        print(f"Snake fMRI run {run_number} completed successfully.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running snake fMRI session: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Get participant ID, run number, trial number, total trials, and screen number from command line arguments
    participant_id = sys.argv[1] if len(sys.argv) > 1 else "TEST"
    run_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    trial_number = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    total_trials = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    screen_number = int(sys.argv[5]) if len(sys.argv) > 5 else None
    
    success = run_fmri_session(participant_id, run_number, trial_number, total_trials, screen_number)
    sys.exit(0 if success else 1) 