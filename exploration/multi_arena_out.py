#!/usr/bin/env python3
"""
Wrapper script to run multi_arena.py in practice mode.
Usage: python multi_arena_out.py [participant_id] [arena_name] [screen_number]
"""

import sys
import subprocess
import os

def main():
    # Get participant ID from command line or input
    if len(sys.argv) > 1:
        participant_id = sys.argv[1]
    else:
        participant_id = input("Enter participant ID: ").strip()
    
    # Get arena name from command line or use default
    if len(sys.argv) > 2:
        arena_name = sys.argv[2]
    else:
        arena_name = "arena1"
    
    # Get screen number from command line or use default
    if len(sys.argv) > 3:
        screen_number = sys.argv[3]
    else:
        screen_number = None
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the command
    cmd = [
        sys.executable,
        os.path.join(script_dir, "multi_arena.py"),
        "practice",
        "--participant", participant_id,
        "--arena", arena_name
    ]
    
    # Add screen parameter if provided
    if screen_number is not None:
        cmd.extend(["--screen", screen_number])
    
    print(f"Running multi_arena practice session for participant: {participant_id}, arena: {arena_name}")
    if screen_number is not None:
        print(f"Display will be on screen: {screen_number}")
    print(f"Command: {' '.join(cmd)}")
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True)
        print("Multi-arena practice session completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running multi_arena practice session: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 