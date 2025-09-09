#!/usr/bin/env python3
"""
Visualize arenas with target locations.
Shows each arena as a 2D plot with target positions and Hebrew labels.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import csv
import re
import numpy as np
from matplotlib.patches import Circle
import os

# Set up Hebrew font support
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']

def parse_coordinates(coord_str):
    """Parse coordinate string like '(0.65; 0.06)' to (x, y)."""
    match = re.search(r'\(([^;]+);\s*([^)]+)\)', coord_str)
    if match:
        x = float(match.group(1))
        y = float(match.group(2))
        return x, y
    return None, None

def load_arena_data(csv_file="Final_New_Arenas.csv"):
    """Load arena data from CSV file."""
    arenas = {}
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                arena = row['theme']
                target = row['target']
                coords = row['coords']
                hebrew = row['hebrew_name']
                
                if arena not in arenas:
                    arenas[arena] = []
                
                x, y = parse_coordinates(coords)
                if x is not None and y is not None:
                    arenas[arena].append({
                        'target': target,
                        'hebrew': hebrew,
                        'x': x,
                        'y': y
                    })
        
        print(f"Loaded {len(arenas)} arenas with {sum(len(t) for t in arenas.values())} targets")
        return arenas
    except FileNotFoundError:
        print(f"Error: {csv_file} not found")
        return {}

def create_arena_visualization(arena_name, targets, figsize=(10, 8)):
    """Create a visualization for a single arena."""
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # Set up the arena boundaries (3.3m diameter circle)
    arena_radius = 1.65  # 3.3m diameter = 1.65m radius
    ax.set_xlim(-arena_radius, arena_radius)
    ax.set_ylim(-arena_radius, arena_radius)
    
    # Create arena background (circle)
    arena_circle = patches.Circle((0, 0), arena_radius, 
                                 linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax.add_patch(arena_circle)
    
    # Add arena title
    ax.set_title(f'{arena_name.upper()} Arena (3.3m diameter)', fontsize=16, fontweight='bold', pad=20)
    
    # Plot targets
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']  # Colorful palette
    target_radius = 0.1
    
    for i, target_info in enumerate(targets):
        x, y = target_info['x'], target_info['y']
        target = target_info['target']
        color = colors[i % len(colors)]
        
        # Draw target circle
        target_circle = Circle((x, y), target_radius, color=color, alpha=0.8, linewidth=2, edgecolor='black')
        ax.add_patch(target_circle)
        
        # Add target label (English only)
        ax.text(x, y + target_radius + 0.05, target, 
                ha='center', va='bottom', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # Add target number
        ax.text(x, y, str(i+1), ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Add legend
    legend_elements = [patches.Patch(color=colors[i], label=f'Target {i+1}') 
                      for i in range(min(5, len(targets)))]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
    
    # Add coordinate info
    ax.text(0.02, 0.98, f'Targets: {len(targets)}', transform=ax.transAxes, 
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
    
    return fig, ax

def create_all_arenas_overview(arenas, figsize=(20, 15)):
    """Create an overview of all arenas in a grid layout."""
    
    n_arenas = len(arenas)
    cols = 4
    rows = (n_arenas + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    if rows == 1:
        axes = axes.reshape(1, -1)
    
    arena_names = list(arenas.keys())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    for i, arena_name in enumerate(arena_names):
        row = i // cols
        col = i % cols
        ax = axes[row, col]
        
        targets = arenas[arena_name]
        
        # Set up the arena (3.3m diameter circle)
        arena_radius = 1.65
        ax.set_xlim(-arena_radius, arena_radius)
        ax.set_ylim(-arena_radius, arena_radius)
        
        # Create arena background (circle)
        arena_circle = patches.Circle((0, 0), arena_radius, 
                                     linewidth=1, edgecolor='black', facecolor='lightgray', alpha=0.3)
        ax.add_patch(arena_circle)
        
        # Add arena title
        ax.set_title(f'{arena_name.upper()}', fontsize=12, fontweight='bold')
        
        # Plot targets
        target_radius = 0.08
        for j, target_info in enumerate(targets):
            x, y = target_info['x'], target_info['y']
            color = colors[j % len(colors)]
            
            # Draw target circle
            target_circle = Circle((x, y), target_radius, color=color, alpha=0.8, linewidth=1, edgecolor='black')
            ax.add_patch(target_circle)
            
            # Add target number
            ax.text(x, y, str(j+1), ha='center', va='center', fontsize=10, fontweight='bold', color='white')
        
        ax.grid(True, alpha=0.2)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
    
    # Hide empty subplots
    for i in range(n_arenas, rows * cols):
        row = i // cols
        col = i % cols
        axes[row, col].set_visible(False)
    
    plt.suptitle('All Arenas Overview (3.3m diameter circles)', fontsize=20, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    return fig, axes

def save_visualizations(arenas, output_dir="arena_visualizations"):
    """Save individual arena visualizations and overview."""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save individual arena plots
    for arena_name, targets in arenas.items():
        fig, ax = create_arena_visualization(arena_name, targets)
        filename = os.path.join(output_dir, f"{arena_name}_arena.png")
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved: {filename}")
    
    # Save overview
    fig, axes = create_all_arenas_overview(arenas)
    overview_filename = os.path.join(output_dir, "all_arenas_overview.png")
    fig.savefig(overview_filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {overview_filename}")

def main():
    """Main function to create arena visualizations."""
    
    print("Arena Visualization Generator")
    print("="*50)
    
    # Load arena data
    arenas = load_arena_data()
    if not arenas:
        return
    
    print(f"\nCreating visualizations for {len(arenas)} arenas...")
    
    # Create and save visualizations
    save_visualizations(arenas)
    
    print(f"\n{'='*50}")
    print("🎉 Visualization complete!")
    print(f"{'='*50}")
    print("\nGenerated files:")
    print("  Individual arena plots: arena_visualizations/<arena>_arena.png")
    print("  Overview plot: arena_visualizations/all_arenas_overview.png")
    
    # Show a sample visualization
    print("\nShowing sample visualization (Garden arena)...")
    if 'garden' in arenas:
        fig, ax = create_arena_visualization('garden', arenas['garden'])
        plt.show()
    
    print("\nNext steps:")
    print("1. Review individual arena plots")
    print("2. Check target spacing and distribution")
    print("3. Verify Hebrew labels are readable")
    print("4. Use overview for experiment planning")

if __name__ == "__main__":
    main() 