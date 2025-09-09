import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
import os

# Arena parameters (in meters)
ARENA_DIAMETER = 3.3
ARENA_RADIUS = ARENA_DIAMETER / 2.0
TARGET_RADIUS = 0.1

def visualize_exploration_annotation_trajectories(csv_file):
    """Create a focused visualization of exploration and annotation trajectories."""
    
    print(f"Analyzing trial data from: {csv_file}")
    
    # Load data
    df = pd.read_csv(csv_file)
    df['trial_time'] = pd.to_numeric(df['trial_time'], errors='coerce')
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: Exploration trajectory
    plot_exploration_trajectory(ax1, df)
    
    # Plot 2: Annotation trajectory
    plot_annotation_trajectory(ax2, df)
    
    plt.tight_layout()
    
    # Save plot
    output_file = "exploration_annotation_trajectories.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Trajectory visualization saved to: {output_file}")
    
    plt.show()
    
    # Print key statistics
    print_trajectory_statistics(df)

def plot_exploration_trajectory(ax, df):
    """Plot exploration phase trajectory."""
    
    # Filter exploration data
    exploration_data = df[df['phase'] == 'exploration']
    
    if len(exploration_data) == 0:
        ax.text(0.5, 0.5, 'No exploration data', ha='center', va='center', transform=ax.transAxes)
        return
    
    # Draw arena
    arena_circle = Circle((0, 0), ARENA_RADIUS, fill=False, color='black', linewidth=2)
    ax.add_patch(arena_circle)
    
    # Plot trajectory
    ax.plot(exploration_data['x'], exploration_data['y'], 
           color='blue', alpha=0.7, linewidth=2, label='Exploration path')
    
    # Plot key events
    plot_exploration_events(ax, exploration_data)
    
    # Add statistics
    duration = exploration_data['trial_time'].max() - exploration_data['trial_time'].min()
    distance = calculate_path_distance(exploration_data)
    
    stats_text = f"""Exploration Phase:
Duration: {duration:.2f}s
Distance: {distance:.2f}m
Points: {len(exploration_data)}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Set plot properties
    ax.set_xlim(-ARENA_RADIUS-0.1, ARENA_RADIUS+0.1)
    ax.set_ylim(-ARENA_RADIUS-0.1, ARENA_RADIUS+0.1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X position (meters)')
    ax.set_ylabel('Y position (meters)')
    ax.set_title('Exploration Trajectory', fontsize=14, fontweight='bold')
    ax.legend()

def plot_annotation_trajectory(ax, df):
    """Plot annotation phase trajectory."""
    
    # Filter annotation data
    annotation_data = df[df['phase'] == 'annotation']
    
    if len(annotation_data) == 0:
        ax.text(0.5, 0.5, 'No annotation data', ha='center', va='center', transform=ax.transAxes)
        return
    
    # Draw arena
    arena_circle = Circle((0, 0), ARENA_RADIUS, fill=False, color='black', linewidth=2)
    ax.add_patch(arena_circle)
    
    # Plot trajectory
    ax.plot(annotation_data['x'], annotation_data['y'], 
           color='green', alpha=0.7, linewidth=2, label='Annotation path')
    
    # Plot key events
    plot_annotation_events(ax, annotation_data)
    
    # Add statistics
    duration = annotation_data['trial_time'].max() - annotation_data['trial_time'].min()
    distance = calculate_path_distance(annotation_data)
    
    stats_text = f"""Annotation Phase:
Duration: {duration:.2f}s
Distance: {distance:.2f}m
Points: {len(annotation_data)}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # Set plot properties
    ax.set_xlim(-ARENA_RADIUS-0.1, ARENA_RADIUS+0.1)
    ax.set_ylim(-ARENA_RADIUS-0.1, ARENA_RADIUS+0.1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X position (meters)')
    ax.set_ylabel('Y position (meters)')
    ax.set_title('Annotation Trajectory', fontsize=14, fontweight='bold')
    ax.legend()

def plot_exploration_events(ax, exploration_data):
    """Plot key events during exploration."""
    
    # Target placement
    target_placed = exploration_data[exploration_data['event'] == 'target_placed']
    if not target_placed.empty:
        target_pos = (target_placed.iloc[0]['x'], target_placed.iloc[0]['y'])
        target_circle = Circle(target_pos, TARGET_RADIUS, 
                              color='red', alpha=0.4, linewidth=2)
        ax.add_patch(target_circle)
        ax.plot(target_pos[0], target_pos[1], 'rx', 
                markersize=12, markeredgewidth=2, label='Target placed')
    
    # Started moving
    started_moving = exploration_data[exploration_data['event'] == 'started moving']
    if not started_moving.empty:
        start_pos = (started_moving.iloc[0]['x'], started_moving.iloc[0]['y'])
        ax.plot(start_pos[0], start_pos[1], 'bs', 
                markersize=10, markeredgewidth=2, label='Started moving')

def plot_annotation_events(ax, annotation_data):
    """Plot key events during annotation."""
    
    # Target annotation
    target_annotated = annotation_data[annotation_data['event'] == 'target_annotated']
    if not target_annotated.empty:
        annotation_pos = (target_annotated.iloc[0]['x'], target_annotated.iloc[0]['y'])
        ax.plot(annotation_pos[0], annotation_pos[1], 'go', 
                markersize=12, markeredgewidth=2, label='Target annotated')

def calculate_path_distance(data):
    """Calculate total distance traveled along a path."""
    if len(data) < 2:
        return 0.0
    
    dx = data['x'].diff()
    dy = data['y'].diff()
    distance = np.sqrt(dx**2 + dy**2)
    return distance.sum()

def print_trajectory_statistics(df):
    """Print detailed statistics about the trajectories."""
    
    print("\n" + "="*60)
    print("TRAJECTORY ANALYSIS")
    print("="*60)
    
    # Exploration statistics
    exploration_data = df[df['phase'] == 'exploration']
    if len(exploration_data) > 0:
        print(f"\nEXPLORATION PHASE:")
        print(f"  Duration: {exploration_data['trial_time'].max() - exploration_data['trial_time'].min():.2f} seconds")
        print(f"  Data points: {len(exploration_data)}")
        print(f"  Distance traveled: {calculate_path_distance(exploration_data):.2f} meters")
        print(f"  Average speed: {calculate_path_distance(exploration_data)/(exploration_data['trial_time'].max() - exploration_data['trial_time'].min()):.3f} m/s")
        print(f"  Position range: X[{exploration_data['x'].min():.3f}, {exploration_data['x'].max():.3f}], Y[{exploration_data['y'].min():.3f}, {exploration_data['y'].max():.3f}]")
        
        # Target placement
        target_placed = exploration_data[exploration_data['event'] == 'target_placed']
        if not target_placed.empty:
            target_pos = (target_placed.iloc[0]['x'], target_placed.iloc[0]['y'])
            print(f"  Target placed at: ({target_pos[0]:.3f}, {target_pos[1]:.3f}) at {target_placed.iloc[0]['trial_time']:.2f}s")
    
    # Annotation statistics
    annotation_data = df[df['phase'] == 'annotation']
    if len(annotation_data) > 0:
        print(f"\nANNOTATION PHASE:")
        print(f"  Duration: {annotation_data['trial_time'].max() - annotation_data['trial_time'].min():.2f} seconds")
        print(f"  Data points: {len(annotation_data)}")
        print(f"  Distance traveled: {calculate_path_distance(annotation_data):.2f} meters")
        print(f"  Average speed: {calculate_path_distance(annotation_data)/(annotation_data['trial_time'].max() - annotation_data['trial_time'].min()):.3f} m/s")
        print(f"  Position range: X[{annotation_data['x'].min():.3f}, {annotation_data['x'].max():.3f}], Y[{annotation_data['y'].min():.3f}, {annotation_data['y'].max():.3f}]")
        
        # Target annotation
        target_annotated = annotation_data[annotation_data['event'] == 'target_annotated']
        if not target_annotated.empty:
            annotation_pos = (target_annotated.iloc[0]['x'], target_annotated.iloc[0]['y'])
            print(f"  Target annotated at: ({annotation_pos[0]:.3f}, {annotation_pos[1]:.3f}) at {target_annotated.iloc[0]['trial_time']:.2f}s")
    
    # Calculate error if both target placement and annotation exist
    target_placed = df[df['event'] == 'target_placed']
    target_annotated = df[df['event'] == 'target_annotated']
    
    if not target_placed.empty and not target_annotated.empty:
        target_pos = (target_placed.iloc[0]['x'], target_placed.iloc[0]['y'])
        annotation_pos = (target_annotated.iloc[0]['x'], target_annotated.iloc[0]['y'])
        error_distance = np.sqrt((target_pos[0] - annotation_pos[0])**2 + (target_pos[1] - annotation_pos[1])**2)
        print(f"\nPERFORMANCE METRICS:")
        print(f"  Target placement: ({target_pos[0]:.3f}, {target_pos[1]:.3f})")
        print(f"  Target annotation: ({annotation_pos[0]:.3f}, {annotation_pos[1]:.3f})")
        print(f"  Error distance: {error_distance:.3f} meters")

def main():
    """Main function."""
    
    csv_file = "Results/test/test_OT_ot2_continuous.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found!")
        return
    
    visualize_exploration_annotation_trajectories(csv_file)

if __name__ == "__main__":
    main()
