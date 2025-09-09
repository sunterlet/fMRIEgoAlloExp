#!/usr/bin/env python3
"""
Hebrew Audio Player for Validation
Plays all generated Hebrew audio files so you can validate their quality
"""

import os
import time
import pygame
from pathlib import Path

def init_pygame():
    """Initialize pygame mixer for audio playback."""
    try:
        pygame.mixer.init()
        print("✓ Pygame mixer initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize pygame mixer: {e}")
        return False

def get_all_audio_files():
    """Get all MP3 files from the arenas directory."""
    sounds_dir = Path(__file__).parent / "sounds" / "arenas"
    audio_files = []
    
    if not sounds_dir.exists():
        print(f"Error: Sounds directory not found: {sounds_dir}")
        return []
    
    for arena_dir in sounds_dir.iterdir():
        if arena_dir.is_dir():
            arena_name = arena_dir.name
            for audio_file in arena_dir.glob("*.mp3"):
                audio_files.append((arena_name, audio_file.name, str(audio_file)))
    
    # Sort by arena name, then by filename
    audio_files.sort(key=lambda x: (x[0], x[1]))
    return audio_files

def play_audio_file(file_path, arena_name, filename):
    """Play a single audio file."""
    try:
        print(f"\n🎵 Playing: {arena_name}/{filename}")
        print(f"   File: {file_path}")
        
        # Load and play the audio
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        return True
        
    except Exception as e:
        print(f"✗ Error playing {filename}: {e}")
        return False

def main():
    """Main function to play all Hebrew audio files."""
    print("Hebrew Audio Player for Validation")
    print("=" * 50)
    
    # Initialize pygame
    if not init_pygame():
        print("Cannot proceed without pygame. Exiting.")
        return
    
    # Get all audio files
    audio_files = get_all_audio_files()
    if not audio_files:
        print("No audio files found. Exiting.")
        return
    
    print(f"Found {len(audio_files)} audio files to play")
    print("\nControls:")
    print("- Press Enter to play next file")
    print("- Type 'q' to quit")
    print("- Type 's' to skip current file")
    print("- Type 'r' to replay current file")
    print("- Type 'f' to add current file to fix list")
    
    # Initialize fix list
    fix_list = []
    current_index = 0
    
    while current_index < len(audio_files):
        arena_name, filename, file_path = audio_files[current_index]
        
        print(f"\n{'='*60}")
        print(f"File {current_index + 1} of {len(audio_files)}")
        print(f"Arena: {arena_name}")
        print(f"File: {filename}")
        print(f"Path: {file_path}")
        print(f"{'='*60}")
        
        # Play the audio
        success = play_audio_file(file_path, arena_name, filename)
        
        if not success:
            print(f"⚠️  Failed to play {filename} - adding to fix list")
            fix_list.append(f"{arena_name}/{filename}")
        
        # Get user input
        while True:
            user_input = input("\nAction (Enter=next, q=quit, s=skip, r=replay, f=fix): ").strip().lower()
            
            if user_input == 'q':
                print("Quitting...")
                break
            elif user_input == 's':
                print(f"Skipping {filename}")
                break
            elif user_input == 'r':
                print(f"Replaying {filename}")
                play_audio_file(file_path, arena_name, filename)
                continue
            elif user_input == 'f':
                fix_list.append(f"{arena_name}/{filename}")
                print(f"Added {filename} to fix list")
                break
            elif user_input == '' or user_input == 'n':
                print(f"Moving to next file...")
                break
            else:
                print("Invalid input. Please try again.")
        
        if user_input == 'q':
            break
            
        current_index += 1
    
    # Save fix list if any files were marked
    if fix_list:
        fix_list_file = "hebrew_audio_fix_list.txt"
        with open(fix_list_file, 'w', encoding='utf-8') as f:
            f.write("Hebrew Audio Files Needing Fixes\n")
            f.write("=" * 40 + "\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for file_path in fix_list:
                f.write(f"{file_path}\n")
        
        print(f"\n📝 Fix list saved to: {fix_list_file}")
        print(f"Files needing fixes: {len(fix_list)}")
        print("\nFiles in fix list:")
        for file_path in fix_list:
            print(f"  - {file_path}")
    else:
        print("\n🎉 All audio files passed validation!")
    
    # Cleanup
    pygame.mixer.quit()
    print("\nAudio player closed.")

if __name__ == "__main__":
    main()
