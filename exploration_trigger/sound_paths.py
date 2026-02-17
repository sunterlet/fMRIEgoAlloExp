"""
Unified sound paths for exploration_trigger tasks.
All Python tasks that use beep.wav and target.wav (snake, one_target; multi_arena uses beep + arena-specific sounds)
load them from exploration_trigger/sounds/.
"""
import os

# Canonical sounds directory: exploration_trigger/sounds
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(_SCRIPT_DIR, "sounds")
BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")
TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
