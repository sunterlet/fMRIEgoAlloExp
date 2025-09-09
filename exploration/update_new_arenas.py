#!/usr/bin/env python3
"""
Update new arenas to replace overlapping ones with unique themes.
Replace: forest, city, farm, office/library with new unique themes.
"""

import random
import math
import csv
import os
import sys
from generate_target_locations import generate_target_locations

# Dor's existing arenas (to avoid overlap)
DOR_ARENAS = [
    "Antarctica", "City", "Desert", "Farm", "Forest", "Jungle", 
    "Kitchen", "Office", "Park", "Sky", "Space", "Training", "Underwater"
]

# Updated arena themes (replacing overlapping ones)
UPDATED_ARENAS = [
    "garden",      # Garden theme (replaces forest)
    "beach",       # Beach theme (kept - unique)
    "village",     # Village theme (replaces city)
    "ranch",       # Ranch theme (replaces farm)
    "zoo",         # Zoo theme (kept - unique)
    "school",      # School theme (kept - unique)
    "hospital",    # Hospital theme (kept - unique)
    "bookstore",   # Bookstore theme (replaces library/office)
    "gym",         # Gym theme (kept - unique)
    "museum",      # Museum theme (kept - unique)
    "airport",     # Airport theme (kept - unique)
    "market"       # Market theme (kept - unique)
]

# Updated target names for each arena (5 targets per arena)
UPDATED_ARENA_TARGETS = {
    "garden": ["Flower", "Butterfly", "Fountain", "Bench", "Tree"],
    "beach": ["Shell", "Seagull", "Wave", "Sandcastle", "Crab"],
    "village": ["House", "Church", "Shop", "Street", "Lamp"],
    "ranch": ["Horse", "Cow", "Barn", "Fence", "Hay"],
    "zoo": ["Lion", "Elephant", "Monkey", "Giraffe", "Penguin"],
    "school": ["Desk", "Book", "Teacher", "Playground", "Cafeteria"],
    "hospital": ["Doctor", "Bed", "Medicine", "Stethoscope", "Ambulance"],
    "bookstore": ["Bookshelf", "Clerk", "Computer", "Chair", "Magazine"],
    "gym": ["Treadmill", "Weights", "Trainer", "Pool", "Basketball"],
    "museum": ["Painting", "Sculpture", "Guide", "Ticket", "Gallery"],
    "airport": ["Plane", "Pilot", "Luggage", "Gate", "Runway"],
    "market": ["Vendor", "Fruit", "Basket", "Scale", "Stall"]
}

# Updated Hebrew translations
UPDATED_HEBREW_NAMES = {
    # Garden
    "Flower": "פרח",
    "Butterfly": "פרפר",
    "Fountain": "מזרקה",
    "Bench": "ספסל",
    "Tree": "עץ",
    
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
    "Horse": "סוס",
    "Cow": "פרה",
    "Barn": "אסם",
    "Fence": "גדר",
    "Hay": "חציר",
    
    # Zoo
    "Lion": "אריה",
    "Elephant": "פיל",
    "Monkey": "קוף",
    "Giraffe": "ג'ירף",
    "Penguin": "פינגווין",
    
    # School
    "Desk": "שולחן כתיבה",
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

def generate_updated_arenas_csv():
    """Generate the updated arenas CSV file with target locations."""
    
    # Create the updated arenas list
    updated_arenas_data = []
    
    for arena_name in UPDATED_ARENAS:
        # Generate 5 target locations for this arena
        locations = generate_target_locations(5, min_distance=0.3)
        targets = UPDATED_ARENA_TARGETS[arena_name]
        
        # Add each target with its location
        for i, target in enumerate(targets):
            x, y = locations[i]
            # Format coordinates as in the original CSV: "(x; y)"
            coords = f"({x:.2f}; {y:.2f})"
            hebrew_name = UPDATED_HEBREW_NAMES.get(target, target)
            updated_arenas_data.append([arena_name, target, coords, hebrew_name])
    
    # Write to CSV file
    output_file = "Updated_New_Arenas.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["theme", "target", "coords", "hebrew_name"])  # Header
        writer.writerows(updated_arenas_data)
    
    print(f"Generated {output_file} with {len(updated_arenas_data)} targets across {len(UPDATED_ARENAS)} arenas")
    return updated_arenas_data

def create_updated_sound_folders():
    """Create sound folders for each updated arena with placeholder files."""
    
    # Create the arenas directory inside sounds
    arenas_dir = os.path.join("sounds", "arenas")
    os.makedirs(arenas_dir, exist_ok=True)
    
    print(f"Creating updated sound folders in: {arenas_dir}")
    
    for arena_name in UPDATED_ARENAS:
        # Create arena folder
        arena_dir = os.path.join(arenas_dir, arena_name)
        os.makedirs(arena_dir, exist_ok=True)
        
        # Create placeholder .mp3 files for each target
        targets = UPDATED_ARENA_TARGETS[arena_name]
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
    
    print(f"Created {len(UPDATED_ARENAS)} arena folders with {len(UPDATED_ARENAS) * 5} placeholder audio files")

def print_updated_arena_summary():
    """Print a summary of the updated arenas."""
    
    print("\n" + "="*60)
    print("UPDATED ARENAS SUMMARY (No Overlap with Dor)")
    print("="*60)
    
    for arena_name in UPDATED_ARENAS:
        targets = UPDATED_ARENA_TARGETS[arena_name]
        print(f"\n{arena_name.upper()} Arena:")
        for i, target in enumerate(targets, 1):
            hebrew = UPDATED_HEBREW_NAMES.get(target, target)
            print(f"  {i}. {target} → {hebrew}")
    
    print(f"\nTotal: {len(UPDATED_ARENAS)} arenas with {len(UPDATED_ARENAS) * 5} targets")
    print("="*60)
    
    print("\nREPLACEMENTS MADE:")
    print("- forest → garden")
    print("- city → village") 
    print("- farm → ranch")
    print("- library/office → bookstore")
    print("\nUNIQUE ARENAS (kept):")
    print("- beach, zoo, school, hospital, gym, museum, airport, market")

def main():
    """Main function to generate updated arenas and create sound folders."""
    
    print("Generating updated arenas with target locations (no overlap with Dor)...")
    updated_arenas_data = generate_updated_arenas_csv()
    
    print("\nCreating updated sound folders...")
    create_updated_sound_folders()
    
    print_updated_arena_summary()
    
    print("\nNext steps:")
    print("1. Replace placeholder .mp3 files with actual Hebrew audio recordings")
    print("2. Use the generated Updated_New_Arenas.csv in your multi_arena experiment")
    print("3. Update the multi_arena.py script to use the new arena file if needed")

if __name__ == "__main__":
    main() 