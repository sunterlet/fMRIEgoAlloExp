#!/usr/bin/env python3
"""
Generate new arenas with target locations and create sound folders.
This script creates 12 new arenas with 5 targets each, using the target location
generation function from generate_target_locations.py
"""

import random
import math
import csv
import os
import sys
from generate_target_locations import generate_target_locations

# New arena themes (not in the original Arenas.csv)
NEW_ARENAS = [
    "forest",      # Forest theme
    "beach",       # Beach theme
    "city",        # City theme
    "farm",        # Farm theme
    "zoo",         # Zoo theme
    "school",      # School theme
    "hospital",    # Hospital theme
    "library",     # Library theme
    "gym",         # Gym theme
    "museum",      # Museum theme
    "airport",     # Airport theme
    "market"       # Market theme
]

# Target names for each arena (5 targets per arena)
ARENA_TARGETS = {
    "forest": ["Tree", "Mushroom", "Squirrel", "Stream", "Rock"],
    "beach": ["Shell", "Seagull", "Wave", "Sandcastle", "Crab"],
    "city": ["Building", "Car", "Streetlight", "Bench", "Fountain"],
    "farm": ["Barn", "Tractor", "Chicken", "Corn", "Fence"],
    "zoo": ["Lion", "Elephant", "Monkey", "Giraffe", "Penguin"],
    "school": ["Desk", "Book", "Teacher", "Playground", "Cafeteria"],
    "hospital": ["Doctor", "Bed", "Medicine", "Stethoscope", "Ambulance"],
    "library": ["Bookshelf", "Librarian", "Computer", "Chair", "Magazine"],
    "gym": ["Treadmill", "Weights", "Trainer", "Pool", "Basketball"],
    "museum": ["Painting", "Sculpture", "Guide", "Ticket", "Gallery"],
    "airport": ["Plane", "Pilot", "Luggage", "Gate", "Runway"],
    "market": ["Vendor", "Fruit", "Basket", "Scale", "Stall"]
}

def generate_new_arenas_csv():
    """Generate the new arenas CSV file with target locations."""
    
    # Create the new arenas list
    new_arenas_data = []
    
    for arena_name in NEW_ARENAS:
        # Generate 5 target locations for this arena
        locations = generate_target_locations(5, min_distance=0.3)
        targets = ARENA_TARGETS[arena_name]
        
        # Add each target with its location
        for i, target in enumerate(targets):
            x, y = locations[i]
            # Format coordinates as in the original CSV: "(x; y)"
            coords = f"({x:.2f}; {y:.2f})"
            new_arenas_data.append([arena_name, target, coords])
    
    # Write to CSV file
    output_file = "New_Arenas.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["theme", "target", "coords"])  # Header
        writer.writerows(new_arenas_data)
    
    print(f"Generated {output_file} with {len(new_arenas_data)} targets across {len(NEW_ARENAS)} arenas")
    return new_arenas_data

def create_sound_folders():
    """Create sound folders for each arena with placeholder files."""
    
    # Create the arenas directory inside sounds
    arenas_dir = os.path.join("sounds", "arenas")
    os.makedirs(arenas_dir, exist_ok=True)
    
    print(f"Creating sound folders in: {arenas_dir}")
    
    for arena_name in NEW_ARENAS:
        # Create arena folder
        arena_dir = os.path.join(arenas_dir, arena_name)
        os.makedirs(arena_dir, exist_ok=True)
        
        # Create placeholder .mp3 files for each target
        targets = ARENA_TARGETS[arena_name]
        for target in targets:
            # Create a placeholder file (you'll need to replace these with actual Hebrew audio)
            placeholder_file = os.path.join(arena_dir, f"{target.lower()}.mp3")
            
            # Create an empty file as placeholder
            with open(placeholder_file, 'w') as f:
                f.write("# Placeholder for Hebrew audio file\n")
                f.write(f"# Target: {target}\n")
                f.write(f"# Arena: {arena_name}\n")
                f.write("# Replace this file with actual .mp3 audio of Hebrew pronunciation\n")
            
            print(f"  Created placeholder: {placeholder_file}")
    
    print(f"Created {len(NEW_ARENAS)} arena folders with {len(NEW_ARENAS) * 5} placeholder audio files")

def print_arena_summary():
    """Print a summary of the generated arenas."""
    
    print("\n" + "="*60)
    print("NEW ARENAS SUMMARY")
    print("="*60)
    
    for arena_name in NEW_ARENAS:
        targets = ARENA_TARGETS[arena_name]
        print(f"\n{arena_name.upper()} Arena:")
        for i, target in enumerate(targets, 1):
            print(f"  {i}. {target}")
    
    print(f"\nTotal: {len(NEW_ARENAS)} arenas with {len(NEW_ARENAS) * 5} targets")
    print("="*60)

def main():
    """Main function to generate new arenas and create sound folders."""
    
    print("Generating new arenas with target locations...")
    new_arenas_data = generate_new_arenas_csv()
    
    print("\nCreating sound folders...")
    create_sound_folders()
    
    print_arena_summary()
    
    print("\nNext steps:")
    print("1. Replace placeholder .mp3 files with actual Hebrew audio recordings")
    print("2. Use the generated New_Arenas.csv in your multi_arena experiment")
    print("3. Update the multi_arena.py script to use the new arena file if needed")

if __name__ == "__main__":
    main() 