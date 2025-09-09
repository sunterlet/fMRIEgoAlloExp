#!/usr/bin/env python3
"""
Wrapper script for running snake game in fMRI mode using virtual environment.
This script can be called from MATLAB for block design experiments.
Uses the Sun-Navigation virtual environment for isolated dependencies.
"""

import sys
import os
import subprocess

def get_venv_python():
    """Get the Python executable from the virtual environment."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, "Sun-Navigation", "Scripts", "python.exe")
    
    if os.path.exists(venv_python):
        return venv_python
    else:
        print(f"Warning: Virtual environment not found at {venv_python}")
        print("Falling back to system Python")
        return sys.executable

def run_fmri_session(participant_id="TEST", run_number=1, trial_number=1, total_trials=1):
    """
    Run the snake game in fMRI mode using virtual environment.
    
    Args:
        participant_id (str): Participant initials/ID
        run_number (int): Run number for the block design
        trial_number (int): Current trial number in sequence
        total_trials (int): Total number of trials in sequence
    """
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        snake_script = os.path.join(script_dir, "snake.py")
        
        # Use virtual environment Python if available
        python_executable = get_venv_python()
        
        # Run the snake script in fMRI mode with trigger functionality
        cmd = [python_executable, snake_script, "fmri", "--participant", participant_id, "--run", str(run_number), "--trial", str(trial_number), "--total-trials", str(total_trials), "--scanning", "--com", "com4", "--tr", "2.0"]
        
        print(f"Running snake fMRI session for participant: {participant_id}, run: {run_number}")
        print(f"Using Python: {python_executable}")
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
    # Get participant ID, run number, trial number, and total trials from command line arguments
    participant_id = sys.argv[1] if len(sys.argv) > 1 else "TEST"
    run_number = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    trial_number = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    total_trials = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    
    success = run_fmri_session(participant_id, run_number, trial_number, total_trials)
    sys.exit(0 if success else 1) 