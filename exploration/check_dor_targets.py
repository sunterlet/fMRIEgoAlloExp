#!/usr/bin/env python3
"""
Check all Dor arenas and identify overlapping targets with our new arenas.
"""

import os

# Dor's arena directories
DOR_ARENAS = [
    "Antarctica", "City", "Desert", "Farm", "Forest", "Jungle", 
    "Kitchen", "Office", "Park", "Sky", "Space", "Training", "Underwater"
]

# Our updated arena targets
OUR_TARGETS = {
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

def get_dor_targets():
    """Get all targets from Dor's arenas."""
    dor_base_path = r"Z:\sunt\Navigation\SoundNavigation\Sounds\Dor"
    dor_targets = {}
    
    for arena in DOR_ARENAS:
        arena_path = os.path.join(dor_base_path, arena)
        if os.path.exists(arena_path):
            targets = []
            for file in os.listdir(arena_path):
                if file.endswith('.wav'):
                    target_name = file[:-4]  # Remove .wav extension
                    targets.append(target_name)
            dor_targets[arena] = targets
            print(f"{arena}: {targets}")
        else:
            print(f"Warning: {arena} directory not found")
    
    return dor_targets

def find_overlaps():
    """Find overlapping targets between Dor and our arenas."""
    dor_targets = get_dor_targets()
    
    # Flatten all Dor targets
    all_dor_targets = []
    for arena, targets in dor_targets.items():
        all_dor_targets.extend(targets)
    
    print(f"\nAll Dor targets: {all_dor_targets}")
    
    # Find overlaps
    overlaps = {}
    for our_arena, our_target_list in OUR_TARGETS.items():
        arena_overlaps = []
        for target in our_target_list:
            if target in all_dor_targets:
                arena_overlaps.append(target)
        if arena_overlaps:
            overlaps[our_arena] = arena_overlaps
    
    return overlaps, all_dor_targets

def main():
    """Main function to check for overlaps."""
    print("Checking Dor arenas for target overlaps...")
    print("="*60)
    
    overlaps, all_dor_targets = find_overlaps()
    
    print(f"\n{'='*60}")
    print("OVERLAP ANALYSIS")
    print("="*60)
    
    if overlaps:
        print("\nOVERLAPPING TARGETS FOUND:")
        for arena, overlap_targets in overlaps.items():
            print(f"\n{arena.upper()} Arena:")
            for target in overlap_targets:
                print(f"  - {target}")
    else:
        print("\nNo overlapping targets found!")
    
    print(f"\nTotal Dor targets: {len(all_dor_targets)}")
    print(f"Total our targets: {sum(len(targets) for targets in OUR_TARGETS.values())}")
    print("="*60)

if __name__ == "__main__":
    main() 