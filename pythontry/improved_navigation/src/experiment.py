import pygame
import time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

from .config import config
from .models import Vector2D, TrialData, ContinuousData
from .game_objects import GameState, Target
from .ui import Renderer
from .logging import DataLogger

class Experiment:
    def __init__(self, player_initials: str):
        pygame.init()
        pygame.mixer.init()
        
        self.clock = pygame.time.Clock()
        self.renderer = Renderer()
        self.logger = DataLogger(player_initials)
        
        # Load sounds
        try:
            self.target_sound = pygame.mixer.Sound(str(config.TARGET_SOUND_PATH))
            self.beep_sound = pygame.mixer.Sound(str(config.BEEP_SOUND_PATH))
        except Exception as e:
            print(f"Error loading sounds: {e}")
            self.target_sound = None
            self.beep_sound = None
        self.beep_channel = None

        # Predefined target positions
        self.target_positions = {
            "training 1": [(-0.5, -1.0), (0.3, 0.8), (-1.0, 0.2)],
            "training 2": [(0.7, -0.8), (-0.4, 0.9), (0.3, -1.2)],
            "training 3": [(-0.8, -0.5), (0.5, 0.5), (0.2, -1.0)],
            "dark_training 1": [(-0.6, -0.9), (0.4, 0.7), (-0.9, 0.1)],
            "dark_training 2": [(0.2, -1.0), (-0.3, 0.8), (0.7, -0.6)],
            "test 1": [(0.5, 1.0), (-0.8, -0.2), (0.7, -0.7)],
            "test 2": [(-0.3, 0.7), (0.8, 0.2), (-0.9, -0.9)],
            "test 3": [(0.4, -0.4), (-0.6, 0.8), (0.2, 1.0)],
            "test 4": [(0.9, -0.3), (-0.4, -1.0), (1.0, 0.8)],
            "test 5": [(-0.2, -0.8), (0.5, 0.6), (-0.7, 1.2)]
        }

    def show_instruction(self, image_path: Path) -> None:
        """Display an instruction image and wait for Enter key."""
        try:
            instruction_image = pygame.image.load(str(image_path))
            self.renderer.screen.blit(instruction_image, (0, 0))
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return False
                        elif event.key == pygame.K_RETURN:
                            waiting = False
                self.clock.tick(60)
            return True
            
        except pygame.error as e:
            print(f"Error loading instruction image {image_path}: {e}")
            return False

    def run_practice(self) -> bool:
        """Run the practice game until score reaches 5."""
        game_state = GameState()
        score = 0
        
        while score < 5:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
            
            keys = pygame.key.get_pressed()
            game_state.update(dt, keys)
            
            # Check if player reached target
            if game_state.encountered_target:
                score += 1
                game_state.targets = []  # Remove target
                # Generate new target at random position
                angle = np.random.uniform(0, 2 * np.pi)
                r = config.ARENA_RADIUS * np.sqrt(np.random.uniform(0, 1))
                pos = Vector2D(r * np.cos(angle), r * np.sin(angle))
                game_state.targets.append(Target(pos))
                game_state.encountered_target = None
            
            self.renderer.render_game_state(game_state, show_debug=True)
            
        return True

    def run_trial(self, trial_info: str, is_training: bool = False) -> Tuple[TrialData, List[ContinuousData]]:
        """Run a single trial of the experiment."""
        game_state = GameState()
        
        # Set up targets
        if trial_info in self.target_positions:
            positions = self.target_positions[trial_info]
            game_state.targets = [
                Target(Vector2D(x, y)) for x, y in positions
            ]
        
        trial_start_time = time.time()
        continuous_logs = []
        
        while True:
            dt = self.clock.tick(60) / 1000.0
            current_time = time.time() - trial_start_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None, None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return None, None
                    if event.key == pygame.K_RETURN:
                        if game_state.current_phase == "exploration":
                            game_state.current_phase = "annotation"
                        elif game_state.current_phase == "annotation":
                            game_state.current_phase = "feedback"
                        elif game_state.current_phase == "feedback":
                            # Calculate trial data
                            trial_data = TrialData(
                                trial_info=trial_info,
                                trial_type="training" if is_training else "test",
                                exploration_time=current_time,
                                annotation_time=time.time() - trial_start_time - current_time,
                                encountered_goal=game_state.encountered_target.position if game_state.encountered_target else None,
                                annotation=game_state.annotation_marker.position if game_state.annotation_marker else Vector2D(0, 0),
                                error_distance=None  # Calculate based on positions
                            )
                            return trial_data, continuous_logs
            
            keys = pygame.key.get_pressed()
            game_state.update(dt, keys)
            
            # Log continuous data
            if game_state.current_phase in ["exploration", "annotation"]:
                log_entry = ContinuousData(
                    trial_info=trial_info,
                    phase=game_state.current_phase,
                    time=current_time,
                    position=game_state.player.position if game_state.current_phase == "exploration" 
                            else game_state.annotation_marker.position
                )
                continuous_logs.append(log_entry)
            
            # Handle border sound
            if game_state.arena.is_near_border(game_state.player.position):
                if self.beep_sound and (not self.beep_channel or not self.beep_channel.get_busy()):
                    self.beep_channel = self.beep_sound.play(loops=-1)
            else:
                if self.beep_channel:
                    self.beep_channel.stop()
                    self.beep_channel = None
            
            # Handle target collision sound
            if game_state.encountered_target and self.target_sound:
                self.target_sound.play()
            
            self.renderer.render_game_state(game_state, show_debug=is_training)
            
        return None, None

    def run(self) -> None:
        """Run the full experiment."""
        # Show welcome screen
        if not self.show_instruction(config.INSTRUCTIONS_DIR / "1.png"):
            return
            
        # Show practice instructions and run practice
        if not self.show_instruction(config.INSTRUCTIONS_DIR / "2.png"):
            return
        if not self.run_practice():
            return
            
        # Training block
        if not self.show_instruction(config.INSTRUCTIONS_DIR / "3.png"):
            return
        for i in range(1, config.TRAINING_SESSIONS + 1):
            trial_info = f"training {i}"
            trial_data, continuous_data = self.run_trial(trial_info, is_training=True)
            if trial_data is None:
                return
            self.logger.add_discrete_log(trial_data)
            for log in continuous_data:
                self.logger.add_continuous_log(log)
                
        # Dark training block
        if not self.show_instruction(config.INSTRUCTIONS_DIR / "4.png"):
            return
        for i in range(1, config.DARK_TRAINING_TRIALS + 1):
            trial_info = f"dark_training {i}"
            trial_data, continuous_data = self.run_trial(trial_info, is_training=False)
            if trial_data is None:
                return
            self.logger.add_discrete_log(trial_data)
            for log in continuous_data:
                self.logger.add_continuous_log(log)
                
        # Test block
        if not self.show_instruction(config.INSTRUCTIONS_DIR / "5.png"):
            return
        for i in range(1, config.TEST_TRIALS + 1):
            trial_info = f"test {i}"
            trial_data, continuous_data = self.run_trial(trial_info, is_training=False)
            if trial_data is None:
                return
            self.logger.add_discrete_log(trial_data)
            for log in continuous_data:
                self.logger.add_continuous_log(log)
                
        # Show completion screen
        self.show_instruction(config.INSTRUCTIONS_DIR / "6.png")
        
        pygame.quit() 