import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle
import seaborn as sns
from datetime import datetime
import os

# Set style for better plots
plt.style.use('default')
sns.set_palette("husl")

# Arena parameters (in meters)
ARENA_DIAMETER = 3.3
ARENA_RADIUS = ARENA_DIAMETER / 2.0
TARGET_RADIUS = 0.1

def load_and_analyze_data(csv_file):
    """Load and analyze the trial data."""
    print(f"Loading data from: {csv_file}")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} data points")
    
    # Convert trial_time to numeric, handling any non-numeric values
    df['trial_time'] = pd.to_numeric(df['trial_time'], errors='coerce')
    
    # Basic statistics
    print(f"\nData Summary:")
    print(f"Phases: {df['phase'].unique()}")
    print(f"Events: {df['event'].dropna().unique()}")
    print(f"Trial duration: {df['trial_time'].max():.2f} seconds")
    
    return df

def create_comprehensive_visualization(df, output_dir="."):
    """Create a comprehensive visualization of the trial."""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Main trajectory plot
    ax1 = plt.subplot(2, 3, 1)
    plot_trajectory(ax1, df, "Complete Trial Trajectory")
    
    # 2. Exploration phase only
    ax2 = plt.subplot(2, 3, 2)
    exploration_data = df[df['phase'] == 'exploration']
    plot_trajectory(ax2, exploration_data, "Exploration Phase")
    
    # 3. Annotation phase only
    ax3 = plt.subplot(2, 3, 3)
    annotation_data = df[df['phase'] == 'annotation']
    plot_trajectory(ax3, annotation_data, "Annotation Phase")
    
    # 4. Time series of position
    ax4 = plt.subplot(2, 3, 4)
    plot_position_time_series(ax4, df)
    
    # 5. Rotation angle over time
    ax5 = plt.subplot(2, 3, 5)
    plot_rotation_time_series(ax5, df)
    
    # 6. Speed analysis
    ax6 = plt.subplot(2, 3, 6)
    plot_speed_analysis(ax6, df)
    
    plt.tight_layout()
    
    # Save the comprehensive plot
    output_file = os.path.join(output_dir, "trial_comprehensive_analysis.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Comprehensive analysis saved to: {output_file}")
    
    # Create separate detailed plots
    create_detailed_trajectory_plot(df, output_dir)
    create_time_analysis_plots(df, output_dir)
    
    plt.show()

def plot_trajectory(ax, df, title):
    """Plot trajectory with arena, target, and key events."""
    
    # Draw arena border
    arena_circle = Circle((0, 0), ARENA_RADIUS, fill=False, color='black', linewidth=2, alpha=0.7)
    ax.add_patch(arena_circle)
    
    # Plot trajectory for each phase
    phases = df['phase'].unique()
    colors = {
        'fixation': 'gray',
        'exploration': 'blue', 
        'annotation': 'green', 
        'feedback': 'red'
    }
    
    for phase in phases:
        if phase in colors:
            phase_data = df[df['phase'] == phase]
            if len(phase_data) > 0:
                ax.plot(phase_data['x'], phase_data['y'], 
                       color=colors[phase], alpha=0.6, linewidth=1.5,
                       label=f'{phase} trajectory')
    
    # Plot key events
    plot_key_events(ax, df)
    
    # Set plot properties
    ax.set_xlim(-ARENA_RADIUS-0.1, ARENA_RADIUS+0.1)
    ax.set_ylim(-ARENA_RADIUS-0.1, ARENA_RADIUS+0.1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X position (meters)')
    ax.set_ylabel('Y position (meters)')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)

def plot_key_events(ax, df):
    """Plot key events on the trajectory."""
    
    # Target placement
    target_placed = df[df['event'] == 'target_placed']
    if not target_placed.empty:
        target_pos = (target_placed.iloc[0]['x'], target_placed.iloc[0]['y'])
        target_circle = Circle(target_pos, TARGET_RADIUS, 
                              color='red', alpha=0.4, linewidth=2,
                              label='Target area')
        ax.add_patch(target_circle)
        ax.plot(target_pos[0], target_pos[1], 'rx', 
                markersize=10, markeredgewidth=2, label='Target center')
    
    # Target annotation
    target_annotated = df[df['event'] == 'target_annotated']
    if not target_annotated.empty:
        annotation_pos = (target_annotated.iloc[0]['x'], target_annotated.iloc[0]['y'])
        ax.plot(annotation_pos[0], annotation_pos[1], 'go', 
                markersize=12, markeredgewidth=2, label='Annotation')
    
    # Started moving
    started_moving = df[df['event'] == 'started moving']
    if not started_moving.empty:
        start_pos = (started_moving.iloc[0]['x'], started_moving.iloc[0]['y'])
        ax.plot(start_pos[0], start_pos[1], 'bs', 
                markersize=10, markeredgewidth=2, label='Started moving')

def plot_position_time_series(ax, df):
    """Plot X and Y position over time."""
    
    # Plot position over time
    ax.plot(df['trial_time'], df['x'], 'b-', alpha=0.7, label='X position', linewidth=1.5)
    ax.plot(df['trial_time'], df['y'], 'r-', alpha=0.7, label='Y position', linewidth=1.5)
    
    # Add phase boundaries
    phases = df['phase'].unique()
    colors = {'fixation': 'gray', 'exploration': 'blue', 'annotation': 'green', 'feedback': 'red'}
    
    for phase in phases:
        if phase in colors:
            phase_data = df[df['phase'] == phase]
            if len(phase_data) > 0:
                start_time = phase_data['trial_time'].min()
                end_time = phase_data['trial_time'].max()
                ax.axvspan(start_time, end_time, alpha=0.2, color=colors[phase], label=f'{phase} phase')
    
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Position (meters)')
    ax.set_title('Position Over Time', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

def plot_rotation_time_series(ax, df):
    """Plot rotation angle over time."""
    
    ax.plot(df['trial_time'], df['rotation_angle'], 'purple', alpha=0.7, linewidth=1.5)
    
    # Add phase boundaries
    phases = df['phase'].unique()
    colors = {'fixation': 'gray', 'exploration': 'blue', 'annotation': 'green', 'feedback': 'red'}
    
    for phase in phases:
        if phase in colors:
            phase_data = df[df['phase'] == phase]
            if len(phase_data) > 0:
                start_time = phase_data['trial_time'].min()
                end_time = phase_data['trial_time'].max()
                ax.axvspan(start_time, end_time, alpha=0.2, color=colors[phase])
    
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Rotation Angle (degrees)')
    ax.set_title('Rotation Over Time', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

def plot_speed_analysis(ax, df):
    """Plot movement speed over time."""
    
    # Calculate speed (distance between consecutive points)
    df_copy = df.copy()
    df_copy['dx'] = df_copy['x'].diff()
    df_copy['dy'] = df_copy['y'].diff()
    df_copy['speed'] = np.sqrt(df_copy['dx']**2 + df_copy['dy']**2) / df_copy['trial_time'].diff()
    
    # Remove infinite and NaN values
    df_copy = df_copy.dropna(subset=['speed'])
    df_copy = df_copy[np.isfinite(df_copy['speed'])]
    
    if len(df_copy) > 0:
        ax.plot(df_copy['trial_time'], df_copy['speed'], 'orange', alpha=0.7, linewidth=1.5)
        
        # Add phase boundaries
        phases = df['phase'].unique()
        colors = {'fixation': 'gray', 'exploration': 'blue', 'annotation': 'green', 'feedback': 'red'}
        
        for phase in phases:
            if phase in colors:
                phase_data = df[df['phase'] == phase]
                if len(phase_data) > 0:
                    start_time = phase_data['trial_time'].min()
                    end_time = phase_data['trial_time'].max()
                    ax.axvspan(start_time, end_time, alpha=0.2, color=colors[phase])
    
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Speed (m/s)')
    ax.set_title('Movement Speed Over Time', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

def create_detailed_trajectory_plot(df, output_dir):
    """Create a detailed trajectory plot with annotations."""
    
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Draw arena
    arena_circle = Circle((0, 0), ARENA_RADIUS, fill=False, color='black', linewidth=3)
    ax.add_patch(arena_circle)
    
    # Plot exploration trajectory
    exploration_data = df[df['phase'] == 'exploration']
    if len(exploration_data) > 0:
        ax.plot(exploration_data['x'], exploration_data['y'], 
               color='blue', alpha=0.8, linewidth=2, label='Exploration')
    
    # Plot annotation trajectory
    annotation_data = df[df['phase'] == 'annotation']
    if len(annotation_data) > 0:
        ax.plot(annotation_data['x'], annotation_data['y'], 
               color='green', alpha=0.8, linewidth=2, label='Annotation')
    
    # Plot key events
    plot_key_events(ax, df)
    
    # Add statistics text
    stats_text = f"""
    Trial Statistics:
    - Total duration: {df['trial_time'].max():.2f}s
    - Exploration time: {exploration_data['trial_time'].max() - exploration_data['trial_time'].min():.2f}s
    - Annotation time: {annotation_data['trial_time'].max() - annotation_data['trial_time'].min():.2f}s
    - Total distance: {calculate_total_distance(df):.2f}m
    """
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_xlim(-ARENA_RADIUS-0.1, ARENA_RADIUS+0.1)
    ax.set_ylim(-ARENA_RADIUS-0.1, ARENA_RADIUS+0.1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X position (meters)')
    ax.set_ylabel('Y position (meters)')
    ax.set_title('Detailed Trial Trajectory Analysis', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    
    output_file = os.path.join(output_dir, "detailed_trajectory.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Detailed trajectory saved to: {output_file}")
    plt.show()

def create_time_analysis_plots(df, output_dir):
    """Create time-based analysis plots."""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Position heatmap
    ax1.hexbin(df['x'], df['y'], gridsize=20, cmap='Blues', alpha=0.7)
    arena_circle = Circle((0, 0), ARENA_RADIUS, fill=False, color='black', linewidth=2)
    ax1.add_patch(arena_circle)
    ax1.set_xlim(-ARENA_RADIUS, ARENA_RADIUS)
    ax1.set_ylim(-ARENA_RADIUS, ARENA_RADIUS)
    ax1.set_aspect('equal')
    ax1.set_title('Position Heatmap', fontweight='bold')
    ax1.set_xlabel('X position (meters)')
    ax1.set_ylabel('Y position (meters)')
    
    # 2. Time spent in each phase
    phase_counts = df['phase'].value_counts()
    ax2.pie(phase_counts.values, labels=phase_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Time Distribution by Phase', fontweight='bold')
    
    # 3. Movement patterns
    df_copy = df.copy()
    df_copy['dx'] = df_copy['x'].diff()
    df_copy['dy'] = df_copy['y'].diff()
    df_copy['distance'] = np.sqrt(df_copy['dx']**2 + df_copy['dy']**2)
    
    # Remove NaN values
    df_copy = df_copy.dropna(subset=['distance'])
    
    if len(df_copy) > 0:
        ax3.hist(df_copy['distance'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax3.set_xlabel('Distance between consecutive points (meters)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Movement Distance Distribution', fontweight='bold')
        ax3.grid(True, alpha=0.3)
    
    # 4. Rotation angle distribution
    ax4.hist(df['rotation_angle'], bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
    ax4.set_xlabel('Rotation Angle (degrees)')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Rotation Angle Distribution', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, "time_analysis.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Time analysis saved to: {output_file}")
    plt.show()

def calculate_total_distance(df):
    """Calculate total distance traveled."""
    df_copy = df.copy()
    df_copy['dx'] = df_copy['x'].diff()
    df_copy['dy'] = df_copy['y'].diff()
    df_copy['distance'] = np.sqrt(df_copy['dx']**2 + df_copy['dy']**2)
    return df_copy['distance'].sum()

def print_trial_summary(df):
    """Print a comprehensive summary of the trial."""
    
    print("\n" + "="*60)
    print("TRIAL SUMMARY")
    print("="*60)
    
    # Basic trial info
    print(f"Trial duration: {df['trial_time'].max():.2f} seconds")
    print(f"Total data points: {len(df)}")
    
    # Phase analysis
    print(f"\nPhase Analysis:")
    for phase in df['phase'].unique():
        phase_data = df[df['phase'] == phase]
        duration = phase_data['trial_time'].max() - phase_data['trial_time'].min()
        print(f"  {phase}: {duration:.2f}s ({len(phase_data)} points)")
    
    # Key events
    print(f"\nKey Events:")
    events = df['event'].dropna().unique()
    for event in events:
        event_data = df[df['event'] == event]
        if len(event_data) > 0:
            time = event_data.iloc[0]['trial_time']
            pos = (event_data.iloc[0]['x'], event_data.iloc[0]['y'])
            print(f"  {event}: {time:.2f}s at position ({pos[0]:.3f}, {pos[1]:.3f})")
    
    # Movement statistics
    total_distance = calculate_total_distance(df)
    print(f"\nMovement Statistics:")
    print(f"  Total distance traveled: {total_distance:.2f} meters")
    print(f"  Average speed: {total_distance/df['trial_time'].max():.3f} m/s")
    
    # Position statistics
    print(f"\nPosition Statistics:")
    print(f"  X range: [{df['x'].min():.3f}, {df['x'].max():.3f}] meters")
    print(f"  Y range: [{df['y'].min():.3f}, {df['y'].max():.3f}] meters")
    print(f"  Distance from center: {np.sqrt(df['x']**2 + df['y']**2).max():.3f} meters")
    
    # Rotation statistics
    print(f"\nRotation Statistics:")
    print(f"  Rotation range: [{df['rotation_angle'].min():.1f}, {df['rotation_angle'].max():.1f}] degrees")
    print(f"  Total rotation: {abs(df['rotation_angle'].diff()).sum():.1f} degrees")

def main():
    """Main function to run the visualization."""
    
    # File path
    csv_file = "Results/test/test_OT_ot2_continuous.csv"
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found!")
        return
    
    # Load and analyze data
    df = load_and_analyze_data(csv_file)
    
    # Print summary
    print_trial_summary(df)
    
    # Create visualizations
    create_comprehensive_visualization(df)
    
    print("\nVisualization complete!")

if __name__ == "__main__":
    main()
