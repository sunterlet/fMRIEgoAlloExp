#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Arena Run Wrapper Script
Runs 6 snake trials and 6 multi_arena trials (intertwined) as a single process
to eliminate timing gaps between trials.

Terminology:
- This is a SINGLE RUN containing 12 trials (6 snake + 6 multi_arena)
- Each trial is numbered 1-12 within this run
- Run number 2 = Full Arena Run (second run in fMRI session)

Usage: python full_arena_run.py --participant PARTICIPANT_ID --run RUN_NUMBER
Note: Run number should be 2 for Full Arena Run.
"""

import subprocess
import sys
import os
import time
import argparse
from datetime import datetime

# ---------------------------
# STANDARDIZED FIXATION CROSS FORMAT:
# - Cross size: 200 pixels (standard text size equivalent)
# - Cross color: WHITE (255, 255, 255) on BLACK background
# - Background: BACKGROUND_COLOR (3, 3, 1) - near-black
# - Position: Center of screen (CENTER_SCREEN)
# - Uses pygame.font for consistent rendering (equivalent to PTSOD's DrawFormattedText)
# 
# Note: PTSOD uses BLACK cross on WHITE background with same dimensions
# ---------------------------

# Constants
TR = 2.01  # TR in seconds
TOTAL_TRIALS = 12  # 6 snake + 6 multi_arena trials

def get_unique_filename(base_filename, participant_id):
    """Generate a unique filename by adding suffix if file exists."""
    # Use centralized results directory if available, otherwise use local results directory
    centralized_results_dir = os.getenv('CENTRALIZED_RESULTS_DIR')
    if centralized_results_dir and os.path.exists(centralized_results_dir):
        # Create SubID subfolder in centralized directory
        subid_dir = os.path.join(centralized_results_dir, participant_id)
        os.makedirs(subid_dir, exist_ok=True)
        
        # Create full path in centralized directory under SubID folder
        full_filename = os.path.join(subid_dir, os.path.basename(base_filename))
        print(f"Using centralized results directory: {subid_dir}")
    else:
        # Fall back to local results directory
        full_filename = base_filename
        print(f"Using local results directory: {os.path.dirname(base_filename)}")
    
    if not os.path.exists(full_filename):
        return full_filename
    
    # Split filename into name and extension
    name, ext = os.path.splitext(full_filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not os.path.exists(new_filename):
            return new_filename
        counter += 1

def run_trial(trial_number, trial_type, participant_id, run_number, arena_name=None, screen_number=None):
    """Run a single trial and return timing information."""
    
    print(f"\n{'='*60}")
    print(f"TRIAL {trial_number}/{TOTAL_TRIALS}: {trial_type.upper()}")
    print(f"{'='*60}")
    
    trial_start_time = time.time()
    
    # Determine which script to run
    if trial_type == "snake":
        script_name = "snake.py"
    elif trial_type == "multi_arena":
        script_name = "multi_arena.py"
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

    # Add screen argument if provided
    if screen_number is not None:
        cmd.extend(["--screen", str(screen_number)])

    # For multi_arena trials, specify the arena and visibility explicitly
    if trial_type == "multi_arena":
        if arena_name:
            cmd.extend(["--arena", arena_name])
        # Ensure no-visibility behavior in fMRI
        cmd.extend(["--visibility", "none", "--arena-number", "1", "--arenas-per-condition", "1"])
    
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

def run_full_arena_run(participant_id, run_number, screen_number=None):
    """Run the complete Full Arena Run (6 snake + 6 multi_arena trials)."""
    
    print(f"\n{'='*80}")
    print(f"FULL ARENA RUN STARTING")
    print(f"Participant: {participant_id}")
    print(f"Run: {run_number}")
    print(f"Total Trials: {TOTAL_TRIALS}")
    print(f"TR: {TR} seconds")
    if screen_number is not None:
        print(f"Display will be on screen: {screen_number}")
    print(f"Note: Trial durations are randomized by individual scripts")
    print(f"{'='*80}")
    
    block_start_time = time.time()
    
    # Define trial sequence (6 snake + 6 multi_arena, intertwined)
    trial_sequence = [
        "snake", "multi_arena", "snake", "multi_arena", "snake", "multi_arena",
        "snake", "multi_arena", "snake", "multi_arena", "snake", "multi_arena"
    ]
    
    trial_results = []
    # Predefine the six fMRI arenas to use across the six multi_arena trials
    fmri_arenas = ["hospital", "bookstore", "gym", "museum", "airport", "market"]
    next_multi_idx = 0

    
    # Run all trials
    for trial_number, trial_type in enumerate(trial_sequence, 1):
        arena_for_trial = None
        if trial_type == "multi_arena":
            # Cycle through the predefined fMRI arenas
            if next_multi_idx < len(fmri_arenas):
                arena_for_trial = fmri_arenas[next_multi_idx]
            else:
                # Safety fallback: wrap around if somehow exceeded
                arena_for_trial = fmri_arenas[next_multi_idx % len(fmri_arenas)]
            next_multi_idx += 1

        result = run_trial(trial_number, trial_type, participant_id, run_number, arena_for_trial, screen_number)
        trial_results.append(result)
        

        
        # Small delay between trials to ensure clean separation
        if trial_number < TOTAL_TRIALS:
            time.sleep(0.1)
    
    block_end_time = time.time()
    block_duration = block_end_time - block_start_time
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"RUN SUMMARY")
    print(f"{'='*80}")
    print(f"Block start time: {datetime.fromtimestamp(block_start_time).strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Block end time: {datetime.fromtimestamp(block_end_time).strftime('%H:%M:%S.%f')[:-3]}")
    print(f"Total block duration: {block_duration:.3f}s ({block_duration/TR:.2f} TRs)")
    
    print(f"\nTRIAL DURATIONS:")
    total_trial_time = 0
    for result in trial_results:
        print(f"  Trial {result['trial_number']} ({result['trial_type']}): {result['duration']:.3f}s ({result['duration']/TR:.2f} TRs)")
        total_trial_time += result['duration']
    
    print(f"Total trial time: {total_trial_time:.3f}s ({total_trial_time/TR:.2f} TRs)")
    
    # Gap analysis
    print(f"\nGAP ANALYSIS:")
    gaps = []
    for i in range(1, len(trial_results)):
        gap = trial_results[i]['start_time'] - trial_results[i-1]['end_time']
        gaps.append(gap)
        if gap > 0.1:  # More than 100ms gap
            print(f"  WARNING: Gap between Trial {trial_results[i-1]['trial_number']} and Trial {trial_results[i]['trial_number']}: {gap:.3f}s ({gap/TR:.2f} TRs)")
        else:
            print(f"  OK: Gap between Trial {trial_results[i-1]['trial_number']} and Trial {trial_results[i]['trial_number']}: {gap:.3f}s ({gap/TR:.2f} TRs)")
    
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
    
    # Save detailed timing log with unique filename
    base_log_filename = f"{participant_id}_full_arena_run_timing.csv"
    log_filename = get_unique_filename(base_log_filename, participant_id)
    save_timing_log(log_filename, block_start_time, trial_results)
    print(f"\nDetailed timing log saved to: {log_filename}")
    
    
    
    print(f"\n{'='*80}")
    print(f"FULL ARENA RUN COMPLETE")
    print(f"{'='*80}")
    
    # Add TR alignment fixation after the last trial, followed by 4 TRs before finish screen
    print(f"\n=== TR ALIGNMENT AND FINAL FIXATION ===")
    
    # Import pygame for the fixation display
    try:
        import pygame
        pygame.init()
        
        # Create a simple display for fixation
        if screen_number is not None:
            # Use specified screen number
            os.environ['DISPLAY'] = f':0.{screen_number}'
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            # Use default fullscreen behavior
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        
        # Calculate the offset to center the game area
        offset_x = (screen_width - 1000) // 2
        offset_y = (screen_height - 800) // 2
        
        # Create a surface for the game content
        game_surface = pygame.Surface((1000, 800))
        
        # Hide cursor for experiment
        pygame.mouse.set_visible(False)
        
        # Background color (same as multi_arena.py)
        BACKGROUND_COLOR = (3, 3, 1)  # near-black
        WHITE = (255, 255, 255)
        
        # 1. TR alignment fixation (if needed)
        current_time = time.time()
        trigger_received_time = os.getenv('TRIGGER_RECEIVED_TIME')
        
        if trigger_received_time:
            reference_time = float(trigger_received_time)
            elapsed_TRs = int((current_time - reference_time) / TR)
            next_TR_start = reference_time + ((elapsed_TRs + 1) * TR)
            
            # Check if we need TR alignment
            if current_time < next_TR_start:
                wait_time = next_TR_start - current_time
                print(f'TR alignment: Waiting {wait_time:.2f} seconds for TR alignment...')
                
                # Show TR alignment fixation
                start_time = time.time()
                while time.time() - start_time < wait_time:
                    screen.fill(BACKGROUND_COLOR)
                    game_surface.fill(BACKGROUND_COLOR)
                    
                    # Draw standardized fixation cross using standardized format (200px text size equivalent)
                    # Use font rendering for consistent appearance with PTSOD
                    font = pygame.font.SysFont("Arial", 200)
                    fixation_text = font.render('+', True, WHITE)
                    text_rect = fixation_text.get_rect(center=(500, 400))  # Center of 1000x800 surface
                    
                    game_surface.blit(fixation_text, text_rect)
                    screen.blit(game_surface, (offset_x, offset_y))
                    pygame.display.flip()
                    
                    # Check for ESC key to exit
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            break
                
                print(f"TR alignment fixation complete.")
            else:
                print(f'No TR alignment needed - already at TR boundary.')
        else:
            print(f'No trigger time available - skipping TR alignment.')
        
        # 2. 4 TRs final fixation before finish screen (no screen clearing between fixations)
        print(f'Showing 4 TRs final fixation before finish screen...')
        final_fixation_duration = 4 * TR
        
        start_time = time.time()
        while time.time() - start_time < final_fixation_duration:
            screen.fill(BACKGROUND_COLOR)
            game_surface.fill(BACKGROUND_COLOR)
            
            # Draw standardized fixation cross using standardized format (200px text size equivalent)
            # Use font rendering for consistent appearance with PTSOD
            font = pygame.font.SysFont("Arial", 200)
            fixation_text = font.render('+', True, WHITE)
            text_rect = fixation_text.get_rect(center=(500, 400))  # Center of 1000x800 surface
            
            game_surface.blit(fixation_text, text_rect)
            screen.blit(game_surface, (offset_x, offset_y))
            pygame.display.flip()
            
            # Check for ESC key to exit
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    break
        
        print(f"Final fixation complete.")
        pygame.quit()
        
    except ImportError:
        print("Warning: pygame not available, skipping fixation display")
    except Exception as e:
        print(f"Warning: Error during fixation display: {e}")
    
    print(f"\n=== FULL ARENA RUN FINISHED ===")

def save_timing_log(filename, block_start_time, trial_results):
    """Save detailed timing log to CSV file."""
    
    import csv
    
    # Ensure the directory exists (get_unique_filename already handles this)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', newline='') as csvfile:
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
            
            for i in range(1, len(trial_results)):
                gap = trial_results[i]['start_time'] - trial_results[i-1]['end_time']
                writer.writerow([
                    f"{trial_results[i-1]['trial_number']} ({trial_results[i-1]['trial_type']})",
                    f"{trial_results[i]['trial_number']} ({trial_results[i]['trial_type']})",
                    f"{gap:.3f}",
                    f"{gap/TR:.2f}"
                ])



def main():
    """Main function to parse arguments and run the block."""
    
    parser = argparse.ArgumentParser(description='Full Arena Block Wrapper')
    parser.add_argument('--participant', '-p', required=True,
                       help='Participant ID')
    parser.add_argument('--run', '-r', type=int, required=True,
                       help='Run number')
    parser.add_argument('--screen', '-s', type=int, default=None,
                       help='Screen number to display on (default: None, uses fullscreen)')
    
    args = parser.parse_args()
    
    # Change to the exploration directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run the block
    run_full_arena_run(args.participant, args.run, args.screen)

if __name__ == "__main__":
    main() 