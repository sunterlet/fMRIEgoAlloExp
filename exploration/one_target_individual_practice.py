#!/usr/bin/env python3
"""
Individual One Target Practice Script
Allows running specific practice trials for participants who need extra training
"""

import sys
import os

# Check for required arguments
if len(sys.argv) < 4:
    print("Usage: one_target_individual_practice.py <participant_id> <condition> <trial_number>")
    print("Conditions: training, dark_training, test")
    sys.exit(1)

participant_id = sys.argv[1]
condition = sys.argv[2]
trial_number = int(sys.argv[3])

# Validate condition
valid_conditions = ['training', 'dark_training', 'test']
if condition not in valid_conditions:
    print(f"Error: Invalid condition '{condition}'. Must be one of: {', '.join(valid_conditions)}")
    sys.exit(1)

# Set environment variable to indicate individual practice mode
os.environ['ONE_TARGET_INDIVIDUAL_PRACTICE'] = 'true'
os.environ['ONE_TARGET_CONDITION'] = condition
os.environ['ONE_TARGET_TRIAL_NUM'] = str(trial_number)

# Import and run the one_target experiment
# This will run in practice mode but with custom condition
print(f"\nRunning individual One Target practice:")
print(f"  Participant: {participant_id}")
print(f"  Condition: {condition}")
print(f"  Trial: {trial_number}")
print("=" * 50)

# Construct command to run one_target.py in practice mode
# but with modified trial sequence
import subprocess

# Run the practice mode with special handling
cmd = [
    sys.executable,  # Use same Python interpreter
    'one_target_out.py',  # Use the practice wrapper
    participant_id
]

# Execute
result = subprocess.run(cmd, capture_output=False)
sys.exit(result.returncode)

