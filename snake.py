import argparse
import os
import random

# ---------------------------
# Parse command line arguments
# ---------------------------
parser = argparse.ArgumentParser(description='Snake Practice Game')
parser.add_argument('mode', choices=['practice', 'fmri', 'anatomical'], 
                   help='Run mode: practice (outside magnet), fmri (inside magnet), or anatomical (during anatomical scan)')
parser.add_argument('--participant', '-p', default='TEST', 
                   help='Participant initials (default: TEST)')
parser.add_argument('--run', '-r', type=int, default=1,
                   help='Run number for fMRI mode (default: 1)')
parser.add_argument('--trial', '-t', type=int, default=1,
                   help='Current trial number in sequence (default: 1)')
parser.add_argument('--total-trials', '-tt', type=int, default=1,
                   help='Total number of trials in sequence (default: 1)')
parser.add_argument('--screen', '-s', type=int, default=None,
                   help='Screen number to display on (default: None, uses fullscreen)')
args = parser.parse_args()

MODE = args.mode
player_initials = args.participant
run_number = args.run
current_trial = args.trial
total_trials = args.total_trials
screen_number = args.screen
TR = 2.01  # Fixed TR for fMRI experiments

# ---------------------------
# Set up logging files
# ---------------------------
# Use centralized results directory if available, otherwise use local results directory
centralized_results_dir = os.getenv('CENTRALIZED_RESULTS_DIR')
if centralized_results_dir and os.path.exists(centralized_results_dir):
    # Create SubID subfolder in centralized directory
    results_dir = os.path.join(centralized_results_dir, player_initials)
    print(f"Using centralized results directory: {results_dir}")
else:
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    print(f"Using local results directory: {results_dir}")

if MODE == 'fmri':
    # Determine run context based on run_number
    # Run 1 = One Target Run, Run 2 = Full Arena Run
    if run_number == 1:
        run_context = "OT"
    elif run_number == 2:
        run_context = "FA"
    else:
        # Fallback for any other run numbers
        run_context = f"run{run_number}"
    continuous_filename = os.path.join(results_dir, f"{player_initials}_{run_context}_snake{current_trial}_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_{run_context}_snake{current_trial}_discrete.csv")
elif MODE == 'anatomical':
    # Anatomical mode: use special naming for anatomical scan period
    continuous_filename = os.path.join(results_dir, f"{player_initials}_anatomical_snake_continuous.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_anatomical_snake_discrete.csv")
else:
    continuous_filename = os.path.join(results_dir, f"{player_initials}_snake_practice_continuous_log.csv")
    discrete_filename = os.path.join(results_dir, f"{player_initials}_snake_practice_discrete_log.csv")

# Ensure results directory exists
os.makedirs(results_dir, exist_ok=True)

# Set trial duration based on mode
if MODE == 'fmri':
    # fMRI mode: Use random TR-aligned durations (10-15 seconds)
    # Convert to TRs: 10-15 seconds = 5-7.5 TRs, use 5-7 TRs
    TRIAL_TRs = random.randint(5, 7)  # 5-7 TRs = 10.05-14.07 seconds
    TRIAL_DURATION = TRIAL_TRs * TR
elif MODE == 'anatomical':
    # Anatomical mode: No time limit (endless gameplay)
    TRIAL_DURATION = None
else:
    # Practice mode: Fixed 1 minute duration
    TRIAL_DURATION = 60.0  # 1 minute = 60 seconds
