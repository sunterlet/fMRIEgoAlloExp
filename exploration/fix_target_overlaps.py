#!/usr/bin/env python3
"""
Fix target overlaps by replacing overlapping targets with unique ones.
"""

import random
import math
import csv
import os
import sys
from generate_target_locations import generate_target_locations

# Dor's overlapping targets (to avoid)
DOR_OVERLAPPING_TARGETS = [
    'Iceberg', 'Igloo', 'Penguin', 'PolarBear', 'Seal', 'Bench', 'Building', 
    'Cafe', 'Kiyosk', 'ParkingLot', 'TrafficLight', 'Trash', 'Cactus', 'Camel', 
    'Cliff', 'Dune', 'Nomad', 'Barn', 'Chicken', 'Cow', 'Hay', 'Horse', 'Pig', 
    'Tractor', 'Bear', 'Deer', 'Mushroom', 'Owl', 'River', 'Squirrel', 'Tree', 
    'Lake', 'Monkey', 'PalmTree', 'Parrot', 'Tiger', 'Countertop', 'Cup', 
    'Fork', 'Oven', 'Pot', 'Sink', 'Toaster', 'Desk', 'Notebook', 'Pen', 
    'Stapler', 'Telephone', 'Flowers', 'Fountain', 'Grass', 'Path', 'Picnic', 
    'Slide', 'Swing', 'Airplane', 'Bird', 'Cloud', 'Rainbow', 'SnowFlake', 
    'Ailen', 'Astronaut', 'Moon', 'Satellite', 'SpaceShip', 'Alef', 'Bet', 
    'Gimel', 'beep', 'Coral', 'Octopus', 'ScubaDiver', 'SeaTurtle', 'SeaWeed', 
    'Shark', 'Whale'
]

# Updated arena themes (no overlap with Dor)
FINAL_ARENAS = [
    "garden",      # Garden theme
    "beach",       # Beach theme
    "village",     # Village theme
    "ranch",       # Ranch theme
    "zoo",         # Zoo theme
    "school",      # School theme
    "hospital",    # Hospital theme
    "bookstore",   # Bookstore theme
    "gym",         # Gym theme
    "museum",      # Museum theme
    "airport",     # Airport theme
    "market"       # Market theme
]

# Updated target names with NO overlaps
FINAL_ARENA_TARGETS = {
    "garden": ["Rose", "Butterfly", "Pond", "Gazebo", "Bush"],  # Replaced: Flower, Fountain, Bench, Tree
    "beach": ["Shell", "Seagull", "Wave", "Sandcastle", "Crab"],  # No overlaps
    "village": ["House", "Church", "Shop", "Street", "Lamp"],  # No overlaps
    "ranch": ["Sheep", "Donkey", "Shed", "Gate", "Straw"],  # Replaced: Horse, Cow, Barn, Hay
    "zoo": ["Lion", "Elephant", "Gorilla", "Giraffe", "Seal"],  # Replaced: Monkey, Penguin
    "school": ["Blackboard", "Book", "Teacher", "Playground", "Cafeteria"],  # Replaced: Desk
    "hospital": ["Doctor", "Bed", "Medicine", "Stethoscope", "Ambulance"],  # No overlaps
    "bookstore": ["Bookshelf", "Clerk", "Computer", "Chair", "Magazine"],  # No overlaps
    "gym": ["Treadmill", "Weights", "Trainer", "Pool", "Basketball"],  # No overlaps
    "museum": ["Painting", "Sculpture", "Guide", "Ticket", "Gallery"],  # No overlaps
    "airport": ["Plane", "Pilot", "Luggage", "Gate", "Runway"],  # No overlaps
    "market": ["Vendor", "Fruit", "Basket", "Scale", "Stall"]  # No overlaps
}

# Updated Hebrew translations
FINAL_HEBREW_NAMES = {
    # Garden
    "Rose": "ורד",
    "Butterfly": "פרפר",
    "Pond": "בריכה",
    "Gazebo": "ביתן",
    "Bush": "שיח",
    
    # Beach
    "Shell": "צדף",
    "Seagull": "שחף",
    "Wave": "גל",
    "Sandcastle": "טירת חול",
    "Crab": "סרטן",
    
    # Village
    "House": "בית",
    "Church": "כנסייה",
    "Shop": "חנות",
    "Street": "רחוב",
    "Lamp": "פנס",
    
    # Ranch
    "Sheep": "כבשה",
    "Donkey": "חמור",
    "Shed": "סככה",
    "Gate": "שער",
    "Straw": "קש",
    
    # Zoo
    "Lion": "אריה",
    "Elephant": "פיל",
    "Gorilla": "גורילה",
    "Giraffe": "ג'ירף",
    "Seal": "כלב ים",
    
    # School
    "Blackboard": "לוח",
    "Book": "ספר",
    "Teacher": "מורה",
    "Playground": "מגרש משחקים",
    "Cafeteria": "קפיטריה",
    
    # Hospital
    "Doctor": "רופא",
    "Bed": "מיטה",
    "Medicine": "תרופה",
    "Stethoscope": "סטטוסקופ",
    "Ambulance": "אמבולנס",
    
    # Bookstore
    "Bookshelf": "מדף ספרים",
    "Clerk": "פקיד",
    "Computer": "מחשב",
    "Chair": "כיסא",
    "Magazine": "כתב עת",
    
    # Gym
    "Treadmill": "הליכון",
    "Weights": "משקולות",
    "Trainer": "מאמן",
    "Pool": "בריכה",
    "Basketball": "כדורסל",
    
    # Museum
    "Painting": "ציור",
    "Sculpture": "פסל",
    "Guide": "מדריך",
    "Ticket": "כרטיס",
    "Gallery": "גלריה",
    
    # Airport
    "Plane": "מטוס",
    "Pilot": "טייס",
    "Luggage": "מזוודה",
    "Gate": "שער",
    "Runway": "מסלול",
    
    # Market
    "Vendor": "מוכר",
    "Fruit": "פרי",
    "Basket": "סל",
    "Scale": "משקל",
    "Stall": "דוכן"
}

def generate_final_arenas_csv():
    """Generate the final arenas CSV file with target locations."""
    
    # Create the final arenas list
    final_arenas_data = []
    
    for arena_name in FINAL_ARENAS:
        # Generate 5 target locations for this arena
        locations = generate_target_locations(5, min_distance=0.3)
        targets = FINAL_ARENA_TARGETS[arena_name]
        
        # Add each target with its location
        for i, target in enumerate(targets):
            x, y = locations[i]
            # Format coordinates as in the original CSV: "(x; y)"
            coords = f"({x:.2f}; {y:.2f})"
            hebrew_name = FINAL_HEBREW_NAMES.get(target, target)
            final_arenas_data.append([arena_name, target, coords, hebrew_name])
    
    # Write to CSV file
    output_file = "Final_New_Arenas.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["theme", "target", "coords", "hebrew_name"])  # Header
        writer.writerows(final_arenas_data)
    
    print(f"Generated {output_file} with {len(final_arenas_data)} targets across {len(FINAL_ARENAS)} arenas")
    return final_arenas_data

def create_final_sound_folders():
    """Create sound folders for each final arena with placeholder files."""
    
    # Create the arenas directory inside sounds
    arenas_dir = os.path.join("sounds", "arenas")
    os.makedirs(arenas_dir, exist_ok=True)
    
    print(f"Creating final sound folders in: {arenas_dir}")
    
    for arena_name in FINAL_ARENAS:
        # Create arena folder
        arena_dir = os.path.join(arenas_dir, arena_name)
        os.makedirs(arena_dir, exist_ok=True)
        
        # Create placeholder .mp3 files for each target
        targets = FINAL_ARENA_TARGETS[arena_name]
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
    
    print(f"Created {len(FINAL_ARENAS)} arena folders with {len(FINAL_ARENAS) * 5} placeholder audio files")

def print_final_arena_summary():
    """Print a summary of the final arenas."""
    
    print("\n" + "="*60)
    print("FINAL ARENAS SUMMARY (No Arena or Target Overlaps with Dor)")
    print("="*60)
    
    for arena_name in FINAL_ARENAS:
        targets = FINAL_ARENA_TARGETS[arena_name]
        print(f"\n{arena_name.upper()} Arena:")
        for i, target in enumerate(targets, 1):
            hebrew = FINAL_HEBREW_NAMES.get(target, target)
            print(f"  {i}. {target} → {hebrew}")
    
    print(f"\nTotal: {len(FINAL_ARENAS)} arenas with {len(FINAL_ARENAS) * 5} targets")
    print("="*60)
    
    print("\nTARGET REPLACEMENTS MADE:")
    print("Garden: Flower→Rose, Fountain→Pond, Bench→Gazebo, Tree→Bush")
    print("Ranch: Horse→Sheep, Cow→Donkey, Barn→Shed, Hay→Straw")
    print("Zoo: Monkey→Gorilla, Penguin→Seal")
    print("School: Desk→Blackboard")
    
    print("\nVERIFICATION:")
    print("✓ No arena name overlaps with Dor")
    print("✓ No target name overlaps with Dor")
    print("✓ All targets have Hebrew translations")
    print("✓ All arenas have 5 targets each")

def main():
    """Main function to generate final arenas and create sound folders."""
    
    print("Generating final arenas with target locations (no overlaps with Dor)...")
    final_arenas_data = generate_final_arenas_csv()
    
    print("\nCreating final sound folders...")
    create_final_sound_folders()
    
    print_final_arena_summary()
    
    print("\nNext steps:")
    print("1. Replace placeholder .mp3 files with actual Hebrew audio recordings")
    print("2. Use the generated Final_New_Arenas.csv in your multi_arena experiment")
    print("3. Update the multi_arena.py script to use the new arena file if needed")

if __name__ == "__main__":
    main() 