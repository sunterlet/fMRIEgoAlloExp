from pathlib import Path
from pydantic import BaseModel
from typing import Tuple

class ExperimentConfig(BaseModel):
    # Arena parameters (in meters)
    ARENA_DIAMETER: float = 3.3
    ARENA_RADIUS: float = ARENA_DIAMETER / 2.0
    BORDER_THRESHOLD: float = 0.1

    # Target parameters
    TARGET_RADIUS: float = 0.1
    DEFAULT_TARGET_COUNT: int = 3

    # Movement settings
    MOVE_SPEED: float = 1.0  # meters per second
    ROTATE_SPEED: float = 90.0  # degrees per second

    # Display settings
    SCALE: int = 200  # pixels per meter
    WIN_WIDTH: int = 1000
    WIN_HEIGHT: int = 800
    
    # Colors (R, G, B)
    BACKGROUND_COLOR: Tuple[int, int, int] = (3, 3, 1)
    AVATAR_COLOR: Tuple[int, int, int] = (255, 67, 101)
    BORDER_COLOR: Tuple[int, int, int] = (255, 255, 243)
    TARGET_COLOR: Tuple[int, int, int] = (0, 217, 192)
    CLOCK_COLOR: Tuple[int, int, int] = (183, 173, 153)
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    DEBUG_COLOR: Tuple[int, int, int] = (50, 50, 255)

    # Trial counts
    TRAINING_SESSIONS: int = 3
    DARK_TRAINING_TRIALS: int = 2
    TEST_TRIALS: int = 5

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    SOUNDS_DIR: Path = BASE_DIR / "sounds"
    INSTRUCTIONS_DIR: Path = BASE_DIR / "instructions"
    DATA_DIR: Path = BASE_DIR / "data"

    # Sound files
    TARGET_SOUND_PATH: Path = SOUNDS_DIR / "target.wav"
    BEEP_SOUND_PATH: Path = SOUNDS_DIR / "beep.wav"

config = ExperimentConfig() 