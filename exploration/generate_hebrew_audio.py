#!/usr/bin/env python3
"""
Hebrew TTS Audio Generator using Edge TTS
Generates MP3 audio files for Hebrew words from Final111_New_Arenas.csv
Uses Edge TTS with female Hebrew voice
Plays each sound for validation and allows regeneration with context
Supports custom sentences for problematic words
ONLY PROCESSES PROBLEMATIC WORDS - skips verified words
"""

import os
import csv
import time
import asyncio
import edge_tts
import subprocess
import pygame
from pathlib import Path

# Edge TTS Hebrew female voice
HEBREW_VOICE = "he-IL-HilaNeural"

# Custom sentences for problematic words - multiple variations to try
CUSTOM_SENTENCES = {
    "shell": [
        "צדף נמצא על החוף",  # A shell is on the beach - word at beginning
        "אני אוסף צדף יפה",  # I collect a beautiful shell - word in middle  
        "החוף מלא בצדף"  # The beach is full of shells - word at end
    ],
    "barrow": [  # Changed from "shed" to "barrow"
        "מריצה נמצאת בחווה",  # A barrow is in the ranch - word at beginning
        "החווה יש לה מריצה",  # The ranch has a barrow - word at end
        "אני משתמש במריצה"  # I use the barrow - word at end
    ],
    "tractor": [  # Changed from "gate" to "tractor"
        "טרקטור נכנס לחווה",  # A tractor enters the ranch - word at beginning
        "החווה יש לה טרקטור",  # The ranch has a tractor - word at end
        "אני נוהג בטרקטור"  # I drive the tractor - word at end
    ],
    "playground": [
        "הילדים משחקים במגרש משחקים",  # Children play in the playground
        "המגרש משחקים מלא בילדים",  # The playground is full of children
        "אני הולך למגרש משחקים"  # I go to the playground
    ],
    "treadmill": [
        "הליכון נמצא בחדר כושר",  # The treadmill is in the gym - word at beginning
        "החדר כושר יש לו הליכון",  # The gym has a treadmill - word at end
        "אני משתמש בהליכון"  # I use the treadmill - word at end
    ]
}

# Only process these problematic words - skip all others
PROBLEMATIC_WORDS = {
    "shell": "beach",
    "barrow": "ranch",  # Changed from "shed" to "barrow"
    "tractor": "ranch",  # Changed from "gate" to "tractor"
    "playground": "school",
    "treadmill": "gym"
}

def init_pygame():
    """Initialize pygame mixer for audio playback."""
    try:
        pygame.mixer.init()
        print("✓ Pygame mixer initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize pygame mixer: {e}")
        return False

def play_audio_file(file_path):
    """Play a single audio file."""
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        return True
        
    except Exception as e:
        print(f"✗ Error playing audio: {e}")
        return False

def load_arena_data():
    """Load arena data from CSV file."""
    arenas = {}
    arena_file = os.path.join(os.path.dirname(__file__), "Final111_New_Arenas.csv")
    
    if not os.path.exists(arena_file):
        print(f"Error: Arena file not found: {arena_file}")
        return {}
    
    with open(arena_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            if len(row) >= 5:
                theme, target_name, coords, hebrew_name, hebrew_theme = row
                if theme not in arenas:
                    arenas[theme] = {}
                arenas[theme][target_name] = hebrew_name
    
    return arenas

async def generate_hebrew_audio_edge_tts(hebrew_text, output_path, use_context=False, custom_sentence=None):
    """Generate Hebrew TTS audio file using Edge TTS."""
    try:
        if custom_sentence:
            print(f"  Generating with custom sentence: '{custom_sentence}'")
            text_to_speak = custom_sentence
        elif use_context:
            # Create a sentence with context for better pronunciation
            context_text = f"זה {hebrew_text}"
            print(f"  Generating with context: '{context_text}'")
            text_to_speak = context_text
        else:
            print(f"  Generating: {hebrew_text}")
            text_to_speak = hebrew_text
        
        # Create Edge TTS communicate object
        communicate = edge_tts.Communicate(text_to_speak, HEBREW_VOICE)
        
        # Generate the audio file
        await communicate.save(output_path)
        
        # Verify file was created and has reasonable size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 1000:  # Should be larger than placeholder files
                print(f"✓ Generated: {output_path} ({file_size} bytes)")
                return True
            else:
                print(f"✗ Generated file too small: {output_path} ({file_size} bytes)")
                return False
        else:
            print(f"✗ Failed to create file: {output_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error generating audio for '{hebrew_text}': {e}")
        return False

def check_edge_tts_installation():
    """Check if edge-tts is installed and working."""
    try:
        import edge_tts
        print("✓ Edge TTS is available")
        return True
    except ImportError:
        print("✗ Edge TTS not found. Installing...")
        try:
            subprocess.check_call(["pip", "install", "edge-tts"])
            print("✓ Edge TTS installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install Edge TTS")
            return False

async def validate_audio(file_path, target_name, hebrew_name):
    """Play audio and ask for validation."""
    print(f"\n🎵 Playing audio for '{target_name}' -> '{hebrew_name}'")
    
    # Play the audio
    if not play_audio_file(file_path):
        print("⚠️  Could not play audio file")
        return False
    
    # Ask for validation
    while True:
        user_input = input("\nIs the pronunciation correct? (y=yes, n=no, r=replay, s=skip): ").strip().lower()
        
        if user_input == 'y' or user_input == 'yes':
            print("✓ Pronunciation accepted")
            return True
        elif user_input == 'n' or user_input == 'no':
            print("✗ Pronunciation needs improvement")
            return False
        elif user_input == 'r' or user_input == 'replay':
            print("🔄 Replaying audio...")
            play_audio_file(file_path)
            continue
        elif user_input == 's' or user_input == 'skip':
            print("⏭️  Skipping this file")
            return 'skip'
        else:
            print("Invalid input. Please enter: y (yes), n (no), r (replay), or s (skip)")

async def main():
    """Main function to generate Hebrew audio files using Edge TTS."""
    print("Hebrew TTS Audio Generator using Edge TTS")
    print("=" * 60)
    print("ONLY PROCESSING PROBLEMATIC WORDS - skipping verified words")
    print("=" * 60)
    
    # Initialize pygame for audio playback
    if not init_pygame():
        print("Cannot proceed without pygame. Exiting.")
        return
    
    # Check Edge TTS installation
    if not check_edge_tts_installation():
        print("Cannot proceed without Edge TTS. Exiting.")
        return
    
    # Load arena data
    arenas = load_arena_data()
    if not arenas:
        print("Failed to load arena data. Exiting.")
        return
    
    # Create sounds directory structure
    sounds_dir = os.path.join(os.path.dirname(__file__), "sounds", "arenas")
    
    total_generated = 0
    total_failed = 0
    total_skipped = 0
    
    print(f"\n🎯 Processing ONLY these problematic words:")
    for word, arena in PROBLEMATIC_WORDS.items():
        print(f"  - {word} ({arena})")
    
    # Process only problematic words
    for target_name_lower, arena_name in PROBLEMATIC_WORDS.items():
        if arena_name not in arenas:
            print(f"⚠️  Arena '{arena_name}' not found in CSV data")
            continue
            
        # Find the Hebrew name for this target
        hebrew_name = None
        for target, hebrew in arenas[arena_name].items():
            if target.lower() == target_name_lower:
                hebrew_name = hebrew
                break
        
        if not hebrew_name:
            print(f"⚠️  Hebrew name not found for '{target_name_lower}' in '{arena_name}'")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing PROBLEMATIC word: '{target_name_lower}' -> '{hebrew_name}'")
        print(f"Arena: {arena_name}")
        print(f"{'='*60}")
        
        # Create arena directory if it doesn't exist
        arena_dir = os.path.join(sounds_dir, arena_name)
        os.makedirs(arena_dir, exist_ok=True)
        
        output_filename = f"{target_name_lower}.mp3"
        output_path = os.path.join(arena_dir, output_filename)
        
        # Check if we have a custom sentence for this word
        custom_sentences = CUSTOM_SENTENCES.get(target_name_lower)
        
        if not custom_sentences:
            print(f"⚠️  No custom sentences defined for '{target_name_lower}'")
            continue

        print(f"\n🔄 Trying different variations for '{target_name_lower}'...")
        for i, sentence in enumerate(custom_sentences):
            print(f"  Attempt {i+1}: '{sentence}'")
            success = await generate_hebrew_audio_edge_tts(hebrew_name, output_path, use_context=False, custom_sentence=sentence)
            
            if success:
                # Validate the audio
                validation_result = await validate_audio(output_path, target_name_lower, hebrew_name)
                
                if validation_result == 'skip':
                    total_skipped += 1
                    break # Move to next problematic word
                elif not validation_result:
                    print(f"⚠️  Variation '{sentence}' failed for '{target_name_lower}' - trying next...")
                    continue
                else: # validation_result is True
                    total_generated += 1
                    print(f"✓ Successfully generated for '{target_name_lower}' with variation '{sentence}'")
                    break # Found a working variation, move to next problematic word
            else:
                print(f"✗ Failed to generate audio for '{target_name_lower}' with variation '{sentence}'")
                total_failed += 1
                
        # If no variation worked, keep the original hebrew_name
        if total_generated == 0:
            print(f"⚠️  All variations failed for '{target_name_lower}' - keeping original: '{hebrew_name}'")
            total_generated += 1 # Count the original as a successful generation
                
        # Add small delay to avoid overwhelming the service
        await asyncio.sleep(0.5)
    
    # Cleanup
    pygame.mixer.quit()
    
    print(f"\n" + "=" * 60)
    print(f"PROBLEMATIC WORDS PROCESSING COMPLETE!")
    print(f"Successfully generated: {total_generated} files")
    print(f"Failed to generate: {total_failed} files")
    print(f"Skipped: {total_skipped} files")
    
    if total_failed > 0:
        print(f"\nNote: Some files failed to generate. This might be due to:")
        print(f"- Network connectivity issues")
        print(f"- Edge TTS service limitations")
        print(f"- Invalid Hebrew text")
        print(f"\nYou may need to manually create these files or retry later.")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 