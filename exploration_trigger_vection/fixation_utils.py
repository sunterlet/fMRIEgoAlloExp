#!/usr/bin/env python3
"""
Utility functions for displaying fixation cross images in fMRI experiments.
Provides consistent fixation cross display across all experiment scripts.
"""

import pygame
import os
import time
from datetime import datetime

def load_fixation_images():
    """Load fixation cross images from the same directory as this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define image paths
    black_on_white_path = os.path.join(script_dir, "fixation_cross_black_on_white.png")
    white_on_black_path = os.path.join(script_dir, "fixation_cross_white_on_black.png")
    
    # Load images
    try:
        black_on_white = pygame.image.load(black_on_white_path)
        white_on_black = pygame.image.load(white_on_black_path)
        return black_on_white, white_on_black
    except pygame.error as e:
        print(f"Warning: Could not load fixation cross images: {e}")
        print(f"Looking for images at:")
        print(f"  - {black_on_white_path}")
        print(f"  - {white_on_black_path}")
        return None, None

def show_fixation_image(screen, game_surface, offset_x, offset_y, duration, 
                       fixation_type="white_on_black", continuous_log=None, 
                       trial_counter=None, trial_info=None, background_color=(3, 3, 1)):
    """
    Display a fixation cross image for the specified duration.
    
    Args:
        screen: Pygame screen surface
        game_surface: Pygame game surface
        offset_x, offset_y: Screen offset for centering
        duration: Duration to display fixation (seconds)
        fixation_type: "white_on_black" or "black_on_white"
        continuous_log: List to append log entries to
        trial_counter: Trial counter for logging
        trial_info: Trial information for logging
        background_color: Background color tuple (R, G, B)
    """
    
    # Load fixation images
    black_on_white, white_on_black = load_fixation_images()
    
    if black_on_white is None or white_on_black is None:
        # Fallback to text-based fixation cross
        print("Using fallback text-based fixation cross")
        return show_fixation_text_fallback(screen, game_surface, offset_x, offset_y, 
                                         duration, continuous_log, trial_counter, trial_info, background_color)
    
    # Select the appropriate image
    if fixation_type == "black_on_white":
        fixation_image = black_on_white
    else:  # default to white_on_black
        fixation_image = white_on_black
    
    # Scale image to fit screen dimensions
    screen_width, screen_height = screen.get_size()
    fixation_image = pygame.transform.scale(fixation_image, (screen_width, screen_height))
    
    # Log fixation start event if continuous_log is provided
    if continuous_log is not None:
        fixation_start_time = time.time()
        entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": 0.0,  # Fixation is before trial starts
            "trial": str(trial_counter) if trial_counter is not None else "fixation",
            "phase": "fixation",
            "event": "fixation_start",
            "x": 0.0,  # No position during fixation
            "y": 0.0,
            "rotation_angle": 0.0,
            "score": 0,
            "target_x": 0.0,
            "target_y": 0.0
        }
        # Add trial-specific fields if available
        if trial_info:
            if "condition_type" in entry:
                entry["condition_type"] = trial_info.split()[0] if " " in trial_info else "fixation"
            if "RoundName" in entry:
                entry["RoundName"] = trial_info
            if "visibility" in entry:
                entry["visibility"] = "none"
        
        continuous_log.append(entry)
    
    # Display fixation image for specified duration
    start_time = time.time()
    while time.time() - start_time < duration:
        # Blit the fixation image directly to screen (full screen)
        screen.blit(fixation_image, (0, 0))
        pygame.display.flip()
        
        # Check for ESC key to exit or K key to skip fixation
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                elif event.key == pygame.K_k:
                    print("Fixation skipped by pressing K key")
                    return
    
    # Log fixation end event if continuous_log is provided
    if continuous_log is not None:
        fixation_end_entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": duration,
            "trial": str(trial_counter) if trial_counter is not None else "fixation",
            "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0,
            "y": 0.0,
            "rotation_angle": 0.0,
            "score": 0,
            "target_x": 0.0,
            "target_y": 0.0
        }
        # Add trial-specific fields if available
        if trial_info:
            if "condition_type" in entry:
                entry["condition_type"] = trial_info.split()[0] if " " in trial_info else "fixation"
            if "RoundName" in entry:
                entry["RoundName"] = trial_info
            if "visibility" in entry:
                entry["visibility"] = "none"
        
        continuous_log.append(fixation_end_entry)

def show_fixation_text_fallback(screen, game_surface, offset_x, offset_y, duration,
                               continuous_log=None, trial_counter=None, trial_info=None, 
                               background_color=(3, 3, 1)):
    """
    Fallback function to display text-based fixation cross if images are not available.
    This maintains the original behavior as a backup.
    """
    WHITE = (255, 255, 255)
    CENTER_SCREEN = (500, 400)  # Center of 1000x800 surface
    
    # Log fixation start event if continuous_log is provided
    if continuous_log is not None:
        fixation_start_time = time.time()
        entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": 0.0,  # Fixation is before trial starts
            "trial": str(trial_counter) if trial_counter is not None else "fixation",
            "phase": "fixation",
            "event": "fixation_start",
            "x": 0.0,  # No position during fixation
            "y": 0.0,
            "rotation_angle": 0.0,
            "score": 0,
            "target_x": 0.0,
            "target_y": 0.0
        }
        # Add trial-specific fields if available
        if trial_info:
            if "condition_type" in entry:
                entry["condition_type"] = trial_info.split()[0] if " " in trial_info else "fixation"
            if "RoundName" in entry:
                entry["RoundName"] = trial_info
            if "visibility" in entry:
                entry["visibility"] = "none"
        
        continuous_log.append(entry)
    
    # Display text-based fixation cross
    start_time = time.time()
    while time.time() - start_time < duration:
        screen.fill(background_color)
        game_surface.fill(background_color)
        
        # Draw fixation cross using standardized format (200px text size equivalent)
        font = pygame.font.SysFont("Arial", 200)
        fixation_text = font.render('+', True, WHITE)
        text_rect = fixation_text.get_rect(center=CENTER_SCREEN)
        
        game_surface.blit(fixation_text, text_rect)
        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()
        
        # Check for ESC key to exit or K key to skip fixation
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                elif event.key == pygame.K_k:
                    print("Fixation skipped by pressing K key")
                    return
    
    # Log fixation end event if continuous_log is provided
    if continuous_log is not None:
        fixation_end_entry = {
            "RealTime": datetime.now().strftime('%H:%M:%S.%f')[:-3],
            "trial_time": duration,
            "trial": str(trial_counter) if trial_counter is not None else "fixation",
            "phase": "fixation",
            "event": "fixation_end",
            "x": 0.0,
            "y": 0.0,
            "rotation_angle": 0.0,
            "score": 0,
            "target_x": 0.0,
            "target_y": 0.0
        }
        # Add trial-specific fields if available
        if trial_info:
            if "condition_type" in entry:
                entry["condition_type"] = trial_info.split()[0] if " " in trial_info else "fixation"
            if "RoundName" in entry:
                entry["RoundName"] = trial_info
            if "visibility" in entry:
                entry["visibility"] = "none"
        
        continuous_log.append(fixation_end_entry)
