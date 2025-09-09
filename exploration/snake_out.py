#!/usr/bin/env python3
"""
Wrapper script for running snake game in practice mode (outside magnet).
This script can be called from MATLAB.
"""

import sys
import os
import subprocess

def run_practice_session(participant_id="TEST", screen_number=None):
    """
    Run the snake game in practice mode.
    
    Args:
        participant_id (str): Participant initials/ID
        screen_number (int, optional): Screen number to display on
    """
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        snake_script = os.path.join(script_dir, "snake.py")
        
        # Build command with optional screen parameter
        cmd = [sys.executable, snake_script, "practice", "--participant", participant_id]
        
        if screen_number is not None:
            cmd.extend(["--screen", str(screen_number)])
        
        print(f"Running snake practice session for participant: {participant_id}")
        if screen_number is not None:
            print(f"Display will be on screen: {screen_number}")
        print(f"Command: {' '.join(cmd)}")
        
        # Run the command
        result = subprocess.run(cmd, check=True)
        
        print("Snake practice session completed successfully.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running snake practice session: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Get participant ID and screen number from command line arguments if provided
    participant_id = sys.argv[1] if len(sys.argv) > 1 else "TEST"
    screen_number = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    success = run_practice_session(participant_id, screen_number)
    sys.exit(0 if success else 1) 