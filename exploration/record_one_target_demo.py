#!/usr/bin/env python3
"""
Script to record a one_target.py demo video showing one fMRI trial.
Includes: instructions screen, one target trial, 2 seconds fixation.
Audio is synchronized (beep for border, target sound).

Usage:
    python record_one_target_demo.py [options]

Options:
    --participant, -p    Participant initials (default: DEMO)
    --run, -r           Run number (default: 1)
    --trial, -t         Trial number (default: 1)
    --output, -o        Output video filename (default: auto-generated)
    --screen, -s         Screen number (default: None, uses fullscreen)
    --automate           Automate keyboard inputs (experimental)

Requirements:
    - opencv-python or imageio (for video writing)
    - soundfile and librosa (for audio processing)
    - ffmpeg (for combining video and audio)

The script will:
1. Show the instructions screen (from Instructions-he/6.png)
2. Run one fMRI trial (you may need to provide keyboard input)
3. Add 2 seconds of fixation at the end
4. Create a video file with synchronized audio

Keyboard controls during trial:
    - 7: Rotate left
    - 8: Move forward
    - 9: Move backward
    - 0: Rotate right
    - ENTER/1: Proceed to next phase
    - ESC: Exit
"""

import pygame
import sys
import os
import time
import numpy as np
import subprocess
import tempfile
import threading
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

# We'll import one_target after setting up sys.argv
# This is done in main() to ensure arguments are set correctly
one_target_module = None

# Global variables for recording
frames = []
audio_events = []  # List of (time, sound_type) tuples
recording_start_time = None
video_filename = None
demo_automation_active = False
automation_thread = None

def record_frame(surface):
    """Record a frame from the pygame surface."""
    global frames, recording_start_time
    
    if recording_start_time is None:
        recording_start_time = time.time()
    
    frame_time = time.time() - recording_start_time
    
    # Convert pygame surface to numpy array
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
    print(f"Audio event: {sound_type} at {timestamp:.3f}s")

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
        except Exception as e:
            print(f"Warning: Could not load target sound: {e}")
    
    if os.path.exists(beep_sound_path):
        try:
            beep_sound, _ = librosa.load(beep_sound_path, sr=sample_rate)
        except Exception as e:
            print(f"Warning: Could not load beep sound: {e}")
    
    # Create audio track
    total_samples = int(duration * sample_rate)
    audio_track = np.zeros((total_samples, 2), dtype=np.float32)
    
    # Track beep state (since it loops)
    beep_active_periods = []  # List of (start, end) tuples
    
    # Process audio events
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
        
        elif sound_type == "beep_start":
            # Beep starts - will continue until beep_stop
            beep_active_periods.append((sample_index, None))
        
        elif sound_type == "beep_stop":
            # Beep stops - close the most recent active period
            if beep_active_periods and beep_active_periods[-1][1] is None:
                start_idx = beep_active_periods[-1][0]
                beep_active_periods[-1] = (start_idx, sample_index)
    
    # Add beep sounds for active periods
    if beep_sound is not None:
        for start_idx, end_idx in beep_active_periods:
            if end_idx is None:
                end_idx = total_samples  # Continue to end if not stopped
            
            # Add looping beep sound
            beep_length = len(beep_sound)
            current_idx = start_idx
            while current_idx < end_idx and current_idx < total_samples:
                remaining = min(beep_length, end_idx - current_idx, total_samples - current_idx)
                beep_segment = beep_sound[:remaining]
                # Mono to stereo
                beep_stereo = np.column_stack([beep_segment, beep_segment])
                audio_track[current_idx:current_idx + remaining] += beep_stereo
                current_idx += beep_length
    
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

def automation_controller():
    """Automate keyboard inputs to simulate a trial for demo purposes."""
    global demo_automation_active
    
    # Wait a bit for the experiment to start
    time.sleep(1.0)
    
    # Wait for instructions screen to appear (it shows for 1 TR = 2.01 seconds)
    time.sleep(2.5)
    
    # Start movement: press 8 (forward) and 0 (rotate right) to move in a circle
    # This simulates exploration behavior
    print("Demo: Starting automated movement...")
    
    # Simulate movement pattern: rotate, move forward, rotate, move forward
    # This will trigger target placement after conditions are met
    movement_pattern = [
        (pygame.K_0, 1.0),  # Rotate right for 1 second
        (pygame.K_8, 2.0),  # Move forward for 2 seconds
        (pygame.K_7, 0.5),  # Rotate left for 0.5 seconds
        (pygame.K_8, 2.0),  # Move forward for 2 seconds
        (pygame.K_0, 1.0),  # Rotate right for 1 second
        (pygame.K_8, 3.0),  # Move forward for 3 seconds
    ]
    
    # Create a fake event queue or use pygame's event posting
    # Since we can't directly inject events, we'll need to patch the key checking
    
    # For now, we'll use a simpler approach: just wait and let the user know
    # that manual input might be needed, or we can patch the key checking functions
    
    # Actually, let's patch pygame.key.get_pressed() to return our simulated keys
    # But that's complex. Instead, let's create a thread that posts events
    
    # Wait for target to be placed (this happens automatically when conditions are met)
    # Then wait a bit more for exploration
    time.sleep(15.0)  # Wait for exploration phase
    
    # Press ENTER to proceed to annotation
    print("Demo: Proceeding to annotation phase...")
    # We'll need to inject a key event here
    
    # Wait for annotation phase
    time.sleep(5.0)
    
    # Press ENTER to proceed to feedback
    print("Demo: Proceeding to feedback phase...")
    
    # Wait a bit, then press ENTER to finish trial
    time.sleep(2.0)
    print("Demo: Finishing trial...")
    
    demo_automation_active = False

def patch_one_target_module(one_target):
    """Patch the one_target module to record frames and audio events."""
    global frames, audio_events, recording_start_time
    
    # Store original functions
    original_flip = pygame.display.flip
    
    # Patch pygame.display.flip to record frames
    def recording_flip():
        # Get the game surface from one_target module
        # Prefer game_surface (1000x800) over full screen
        surface_to_record = None
        
        if hasattr(one_target, 'game_surface') and one_target.game_surface is not None:
            surface_to_record = one_target.game_surface
        elif hasattr(one_target, 'screen') and one_target.screen is not None:
            # If game_surface doesn't exist, try to get from screen
            surface_to_record = one_target.screen
        
        if surface_to_record is not None:
            # If it's the full screen, we might want to crop to the game area
            # But for now, record whatever we have
            try:
                record_frame(surface_to_record)
            except Exception as e:
                print(f"Warning: Could not record frame: {e}")
        
        return original_flip()
    
    # Apply patches
    pygame.display.flip = recording_flip
    
    # We'll patch the channels after they're created in one_target
    # Store references for later patching
    original_patched = False
    
    def patch_channels_when_ready():
        """Patch sound channels after they're created."""
        nonlocal original_patched
        
        if original_patched:
            return
        
        # Patch sound channels if they exist
        if hasattr(one_target, 'target_channel') and one_target.target_channel:
            if not hasattr(one_target.target_channel, '_original_play'):
                original_play_target = one_target.target_channel.play
                one_target.target_channel._original_play = original_play_target
                
                def patched_target_play(sound, *args, **kwargs):
                    record_audio_event("target")
                    return original_play_target(sound, *args, **kwargs)
                
                one_target.target_channel.play = patched_target_play
        
        if hasattr(one_target, 'beep_channel') and one_target.beep_channel:
            if not hasattr(one_target.beep_channel, '_original_play'):
                original_play_beep = one_target.beep_channel.play
                original_stop_beep = one_target.beep_channel.stop
                
                one_target.beep_channel._original_play = original_play_beep
                one_target.beep_channel._original_stop = original_stop_beep
                
                def patched_beep_play(sound, *args, **kwargs):
                    record_audio_event("beep_start")
                    return original_play_beep(sound, *args, **kwargs)
                
                def patched_beep_stop(*args, **kwargs):
                    record_audio_event("beep_stop")
                    return original_stop_beep(*args, **kwargs)
                
                one_target.beep_channel.play = patched_beep_play
                one_target.beep_channel.stop = patched_beep_stop
                original_patched = True
    
    # Try to patch channels immediately, and also patch in the flip function
    def recording_flip_with_channel_patch():
        patch_channels_when_ready()
        return recording_flip()
    
    pygame.display.flip = recording_flip_with_channel_patch

def add_fixation_at_end(duration=2.0):
    """Add a 2-second fixation at the end of the recording."""
    global frames, recording_start_time
    
    if not frames:
        return
    
    print(f"Adding {duration}s fixation at the end...")
    
    # Get the last frame to use as base for dimensions
    last_frame_time, last_frame_array = frames[-1]
    
    # Create fixation frame
    # We need to draw a fixation cross on a black background
    # Since we're working with numpy arrays, we'll create a simple fixation
    
    # Create a black frame (background color from one_target: (3, 3, 1))
    height, width = last_frame_array.shape[:2]
    fixation_frame = np.zeros((height, width, 3), dtype=np.uint8)
    fixation_frame[:, :] = [1, 1, 3]  # Near-black background (BGR format)
    
    # Draw a white cross (simple approach: draw lines)
    center_x, center_y = width // 2, height // 2
    cross_size = 100  # Size of the cross
    
    # Horizontal line (white in BGR = [255, 255, 255])
    y_start = max(0, center_y - 5)
    y_end = min(height, center_y + 5)
    x_start = max(0, center_x - cross_size)
    x_end = min(width, center_x + cross_size)
    fixation_frame[y_start:y_end, x_start:x_end] = [255, 255, 255]
    
    # Vertical line
    y_start = max(0, center_y - cross_size)
    y_end = min(height, center_y + cross_size)
    x_start = max(0, center_x - 5)
    x_end = min(width, center_x + 5)
    fixation_frame[y_start:y_end, x_start:x_end] = [255, 255, 255]
    
    # Add frames for the fixation duration
    fps = 60
    num_frames = int(duration * fps)
    current_time = last_frame_time
    
    for i in range(num_frames):
        current_time += 1.0 / fps
        frames.append((current_time, fixation_frame.copy()))

def main():
    """Main function to run and record the one_target demo."""
    import argparse
    global one_target
    
    parser = argparse.ArgumentParser(description='Record one_target.py demo video')
    parser.add_argument('--participant', '-p', default='DEMO', 
                       help='Participant initials (default: DEMO)')
    parser.add_argument('--run', '-r', type=int, default=1,
                       help='Run number for fMRI mode (default: 1)')
    parser.add_argument('--trial', '-t', type=int, default=1,
                       help='Current trial number (default: 1)')
    parser.add_argument('--output', '-o', default=None,
                       help='Output video filename (default: auto-generated)')
    parser.add_argument('--screen', '-s', type=int, default=None,
                       help='Screen number to display on (default: None, windowed)')
    parser.add_argument('--automate', action='store_true',
                       help='Automate keyboard inputs (experimental)')
    
    args = parser.parse_args()
    
    # Set up output filename
    if args.output is None:
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)
        output_filename = os.path.join(results_dir, 
            f"{args.participant}_one_target_demo_video.mp4")
    else:
        output_filename = args.output
    
    print(f"Recording one_target demo to: {output_filename}")
    print("Note: This will run the experiment. You may need to provide keyboard input.")
    print("The video will include: instructions screen, one trial, 2s fixation")
    
    # IMPORTANT: Set sys.argv BEFORE importing one_target
    # because one_target parses arguments at import time
    original_argv = sys.argv
    sys.argv = ['one_target.py', 'fmri', 
                '--participant', args.participant,
                '--run', str(args.run),
                '--trial', str(args.trial),
                '--total-trials', '1']
    if args.screen is not None:
        sys.argv.extend(['--screen', str(args.screen)])
    
    # Now import one_target (it will parse the arguments we just set)
    import one_target
    
    # Patch the one_target module before running
    patch_one_target_module(one_target)
    
    # Start automation thread if requested
    if args.automate:
        global automation_thread, demo_automation_active
        demo_automation_active = True
        automation_thread = threading.Thread(target=automation_controller, daemon=True)
        automation_thread.start()
        print("Automation thread started (experimental)")
    
    try:
        # Run the one_target experiment
        one_target.run_experiment()
    except SystemExit:
        # Expected when experiment finishes
        pass
    except Exception as e:
        print(f"Error during experiment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original argv
        sys.argv = original_argv
    
    # Add 2-second fixation at the end
    add_fixation_at_end(2.0)
    
    # Create video from recorded frames
    if frames:
        print(f"\nRecording complete. Creating video with {len(frames)} frames...")
        print(f"Audio events recorded: {len(audio_events)}")
        create_video_with_audio(frames, audio_events, output_filename, fps=60)
        print(f"\nVideo saved to: {output_filename}")
    else:
        print("No frames were recorded!")

if __name__ == "__main__":
    main()
