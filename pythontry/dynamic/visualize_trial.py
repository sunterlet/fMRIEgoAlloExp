import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
import sys
import os

# Arena parameters (in meters)
ARENA_DIAMETER = 3.3
ARENA_RADIUS = ARENA_DIAMETER / 2.0
TARGET_RADIUS = 0.1

def visualize_trial(log_file):
    print(f"Reading log file: {log_file}")
    
    # Read the continuous log file
    df = pd.read_csv(log_file)
    print(f"Found {len(df)} data points")
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Draw arena border
    arena_circle = Circle((0, 0), ARENA_RADIUS, fill=False, color='black', linewidth=2)
    ax.add_patch(arena_circle)
    
    # Plot trajectory for each phase
    phases = df['phase'].unique()
    print(f"Phases found: {phases}")
    colors = {'exploration': 'blue', 'annotation': 'green', 'feedback': 'red'}
    
    for phase in phases:
        phase_data = df[df['phase'] == phase]
        print(f"Plotting {len(phase_data)} points for {phase} phase")
        ax.plot(phase_data['x'], phase_data['y'], 
                color=colors[phase], 
                alpha=0.5, 
                label=f'{phase} trajectory')
    
    # Plot target placement
    target_placed = df[df['event'] == 'target_placed']
    if not target_placed.empty:
        target_pos = (target_placed.iloc[0]['x'], target_placed.iloc[0]['y'])
        print(f"Target placed at: {target_pos}")
        target_circle = Circle(target_pos, TARGET_RADIUS, 
                              color='red', alpha=0.3, 
                              label='Target area')
        ax.add_patch(target_circle)
        ax.plot(target_pos[0], target_pos[1], 'rx', 
                markersize=10, label='Target center')
    
    # Plot returned_to_target events
    returned_events = df[df['event'] == 'returned_to_target']
    if not returned_events.empty:
        print(f"Found {len(returned_events)} returned_to_target events")
        ax.plot(returned_events['x'], returned_events['y'], 
                'go', markersize=8, 
                label='Returned to target')
    
    # Plot started_moving event
    started_moving = df[df['event'] == 'started moving']
    if not started_moving.empty:
        print(f"Started moving at: ({started_moving.iloc[0]['x']}, {started_moving.iloc[0]['y']})")
        ax.plot(started_moving['x'], started_moving['y'], 
                'bs', markersize=8, 
                label='Started moving')
    
    # Set plot limits and labels
    ax.set_xlim(-ARENA_RADIUS, ARENA_RADIUS)
    ax.set_ylim(-ARENA_RADIUS, ARENA_RADIUS)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlabel('X position (meters)')
    ax.set_ylabel('Y position (meters)')
    ax.set_title('Trial Visualization')
    
    # Add legend
    ax.legend()
    
    # Save the plot
    output_file = os.path.join(os.path.dirname(log_file), 
                              os.path.basename(log_file).replace('_continuous_log.csv', '_visualization.png'))
    plt.savefig(output_file)
    print(f"Visualization saved to: {output_file}")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualize_trial.py <continuous_log_file>")
        sys.exit(1)
    
    log_file = sys.argv[1]
    visualize_trial(log_file) 