"""
Unified sound paths for exploration_trigger_vection tasks.
All Python tasks that use beep.wav and target.wav load them from exploration_trigger_vection/sounds/.
"""
import os

# Canonical sounds directory: same directory as this script
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(_SCRIPT_DIR, "sounds")
BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")
TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
