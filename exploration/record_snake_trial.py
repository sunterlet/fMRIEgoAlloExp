#!/usr/bin/env python3
"""
Script to record a snake game trial as a video with audio.
This script runs the snake game and records it to a video file.
"""

import pygame
import sys
import os
import time
import numpy as np
import subprocess
import tempfile
from pathlib import Path

# Try to import opencv for video writing
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("Warning: opencv-python not installed. Will use imageio instead.")
    try:
        import imageio
        HAS_IMAGEIO = True
    except ImportError:
        HAS_IMAGEIO = False
        print("Error: Neither opencv-python nor imageio is available.")
        print("Please install one of them: pip install opencv-python or pip install imageio")
        sys.exit(1)

# Import the snake game module
import snake

# Global variables for recording
frames = []
audio_events = []  # List of (time, sound_type) tuples
recording_start_time = None
video_filename = None

def record_frame(surface, offset_x, offset_y, screen_width, screen_height):
    """Record a frame from the pygame surface."""
    global frames, recording_start_time
    
    if recording_start_time is None:
        recording_start_time = time.time()
    
    # Capture the game surface area from the screen
    # We need to capture the centered game area
    frame_time = time.time() - recording_start_time
    
    # Convert pygame surface to numpy array
    # Get the game surface (1000x800)
    frame_array = pygame.surfarray.array3d(surface)
    # Convert from (width, height, 3) to (height, width, 3) and RGB to BGR for OpenCV
    frame_array = np.transpose(frame_array, (1, 0, 2))
    frame_array = frame_array[:, :, ::-1]  # RGB to BGR
    
    frames.append((frame_time, frame_array))

def record_audio_event(sound_type, timestamp=None):
    """Record when an audio event occurs."""
    global audio_events, recording_start_time
    
    if recording_start_time is None:
        recording_start_time = time.time()
    
    if timestamp is None:
        timestamp = time.time() - recording_start_time
    
    audio_events.append((timestamp, sound_type))

def create_video_with_audio(frames, audio_events, output_path, fps=60):
    """Create a video file with audio from frames and audio events."""
    global video_filename
    
    if not frames:
        print("No frames to record!")
        return None
    
    print(f"Creating video with {len(frames)} frames...")
    
    # Get frame dimensions
    height, width = frames[0][1].shape[:2]
    
    # Create temporary directory for intermediate files
    temp_dir = tempfile.mkdtemp()
    temp_video = os.path.join(temp_dir, "video.mp4")
    temp_audio = os.path.join(temp_dir, "audio.wav")
    
    try:
        if HAS_OPENCV:
            # Use OpenCV to write video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
            
            for frame_time, frame_array in frames:
                out.write(frame_array.astype(np.uint8))
            
            out.release()
        elif HAS_IMAGEIO:
            # Use imageio to write video
            frame_arrays = [frame[1].astype(np.uint8) for frame in frames]
            imageio.mimsave(temp_video, frame_arrays, fps=fps, codec='libx264')
        
        print("Video file created. Adding audio...")
        
        # Create audio file with target and beep sounds
        create_audio_track(audio_events, temp_audio, len(frames) / fps)
        
        # Combine video and audio using ffmpeg
        final_output = output_path
        if os.path.exists(final_output):
            os.remove(final_output)
        
        # Use ffmpeg to combine video and audio
        cmd = [
            'ffmpeg', '-y',
            '-i', temp_video,
            '-i', temp_audio,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            final_output
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: ffmpeg error: {result.stderr}")
            # If ffmpeg fails, just copy the video without audio
            import shutil
            shutil.copy(temp_video, final_output)
            print("Video created without audio (ffmpeg not available or failed)")
        else:
            print(f"Video with audio created: {final_output}")
        
        video_filename = final_output
        return final_output
        
    except Exception as e:
        print(f"Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass

def create_audio_track(audio_events, output_path, duration):
    """Create an audio track with target and beep sounds at specified times."""
    try:
        import soundfile as sf
        import librosa
    except ImportError:
        print("Warning: soundfile or librosa not available. Creating silent audio track.")
        # Create a silent audio track
        sample_rate = 44100
        samples = int(duration * sample_rate)
        audio_data = np.zeros((samples, 2), dtype=np.float32)
        try:
            import soundfile as sf
            sf.write(output_path, audio_data, sample_rate)
        except:
            # Fallback: use a simple WAV writer
            create_silent_wav(output_path, duration, sample_rate)
        return
    
    sample_rate = 44100
    
    # Load sound files
    target_sound_path = os.path.join(os.path.dirname(__file__), "sounds", "target.wav")
    beep_sound_path = os.path.join(os.path.dirname(__file__), "sounds", "beep.wav")
    
    target_sound = None
    beep_sound = None
    
    if os.path.exists(target_sound_path):
        try:
            target_sound, _ = librosa.load(target_sound_path, sr=sample_rate)
        except:
            pass
    
    if os.path.exists(beep_sound_path):
        try:
            beep_sound, _ = librosa.load(beep_sound_path, sr=sample_rate)
        except:
            pass
    
    # Create audio track
    total_samples = int(duration * sample_rate)
    audio_track = np.zeros((total_samples, 2), dtype=np.float32)
    
    # Add sounds at specified times
    for event_time, sound_type in audio_events:
        sample_index = int(event_time * sample_rate)
        
        if sound_type == "target" and target_sound is not None:
            sound_length = len(target_sound)
            end_index = min(sample_index + sound_length, total_samples)
            if end_index > sample_index:
                available_length = end_index - sample_index
                if available_length <= len(target_sound):
                    # Mono to stereo
                    sound_stereo = np.column_stack([target_sound[:available_length], 
                                                    target_sound[:available_length]])
                    audio_track[sample_index:end_index] += sound_stereo
        
        elif sound_type == "beep" and beep_sound is not None:
            # Beep is looped, so we'll add it for a short duration
            beep_duration = 0.1  # 100ms
            beep_samples = int(beep_duration * sample_rate)
            end_index = min(sample_index + beep_samples, total_samples)
            if end_index > sample_index:
                available_length = end_index - sample_index
                beep_segment = beep_sound[:min(available_length, len(beep_sound))]
                # Mono to stereo
                beep_stereo = np.column_stack([beep_segment, beep_segment])
                audio_track[sample_index:end_index] += beep_stereo
    
    # Normalize audio
    max_val = np.max(np.abs(audio_track))
    if max_val > 0:
        audio_track = audio_track / max_val * 0.8  # Scale to 80% to avoid clipping
    
    # Write audio file
    try:
        sf.write(output_path, audio_track, sample_rate)
    except Exception as e:
        print(f"Error writing audio: {e}")
        create_silent_wav(output_path, duration, sample_rate)

def create_silent_wav(output_path, duration, sample_rate):
    """Create a silent WAV file as fallback."""
    import wave
    import struct
    
    total_samples = int(duration * sample_rate)
    
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Write silent frames
        silent_frame = struct.pack('<hh', 0, 0)  # Two 16-bit samples (silence)
        for _ in range(total_samples):
            wav_file.writeframes(silent_frame)

def patch_snake_module():
    """Patch the snake module to record frames and audio events."""
    global frames, audio_events, recording_start_time
    
    # Store original functions
    original_flip = pygame.display.flip
    original_play_target = None
    original_play_beep = None
    
    # Patch pygame.display.flip to record frames
    def recording_flip():
        # Get the current display surface
        screen = pygame.display.get_surface()
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        
        # Get game surface from snake module
        if hasattr(snake, 'game_surface'):
            record_frame(snake.game_surface, snake.offset_x, snake.offset_y, 
                        screen_width, screen_height)
        
        return original_flip()
    
    # Patch sound playing functions
    def patched_target_play(*args, **kwargs):
        record_audio_event("target")
        if original_play_target:
            return original_play_target(*args, **kwargs)
    
    def patched_beep_play(*args, **kwargs):
        record_audio_event("beep")
        if original_play_beep:
            return original_play_beep(*args, **kwargs)
    
    # Apply patches
    pygame.display.flip = recording_flip
    
    # Patch sound channels if they exist
    if hasattr(snake, 'target_channel') and snake.target_channel:
        original_play_target = snake.target_channel.play
        snake.target_channel.play = lambda sound, *args, **kwargs: (
            record_audio_event("target"),
            original_play_target(sound, *args, **kwargs)
        )
    
    if hasattr(snake, 'beep_channel') and snake.beep_channel:
        original_play_beep = snake.beep_channel.play
        snake.beep_channel.play = lambda sound, *args, **kwargs: (
            record_audio_event("beep"),
            original_play_beep(sound, *args, **kwargs)
        )

def main():
    """Main function to run and record the snake trial."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Record snake game trial as video')
    parser.add_argument('--participant', '-p', default='TEST', 
                       help='Participant initials (default: TEST)')
    parser.add_argument('--run', '-r', type=int, default=1,
                       help='Run number for fMRI mode (default: 1)')
    parser.add_argument('--trial', '-t', type=int, default=1,
                       help='Current trial number (default: 1)')
    parser.add_argument('--output', '-o', default=None,
                       help='Output video filename (default: auto-generated)')
    parser.add_argument('--screen', '-s', type=int, default=None,
                       help='Screen number to display on')
    
    args = parser.parse_args()
    
    # Set up output filename
    if args.output is None:
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)
        output_filename = os.path.join(results_dir, 
            f"{args.participant}_snake_trial{args.trial}_video.mp4")
    else:
        output_filename = args.output
    
    print(f"Recording snake trial to: {output_filename}")
    
    # Patch the snake module before running
    patch_snake_module()
    
    # Modify sys.argv to pass arguments to snake.py
    original_argv = sys.argv
    sys.argv = ['snake.py', 'fmri', 
                '--participant', args.participant,
                '--run', str(args.run),
                '--trial', str(args.trial),
                '--total-trials', '1']
    if args.screen is not None:
        sys.argv.extend(['--screen', str(args.screen)])
    
    try:
        # Run the snake game
        snake.run_practice_game()
    finally:
        sys.argv = original_argv
    
    # Create video from recorded frames
    if frames:
        print(f"\nRecording complete. Creating video with {len(frames)} frames...")
        create_video_with_audio(frames, audio_events, output_filename, fps=60)
        print(f"\nVideo saved to: {output_filename}")
    else:
        print("No frames were recorded!")

if __name__ == "__main__":
    main()
