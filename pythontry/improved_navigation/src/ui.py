import pygame
import numpy as np
from typing import Tuple, Optional
from .config import config
from .models import Vector2D
from .game_objects import Player, Target, GameState

class Renderer:
    def __init__(self):
        self.screen = pygame.display.set_mode((config.WIN_WIDTH, config.WIN_HEIGHT))
        pygame.display.set_caption("Navigation Experiment")
        self.center = (config.WIN_WIDTH // 2, config.WIN_HEIGHT // 2)
        self.font = pygame.font.SysFont("Arial", 20)

    def draw_player(self, player: Player, color: Tuple[int, int, int]) -> None:
        """Draw the player avatar as a triangle."""
        tip_length = 30
        base_length = 20
        half_width = 17

        screen_pos = player.position.to_screen_coords(self.center, config.SCALE)
        rad = np.radians(player.angle)
        
        # Calculate triangle points
        tip = (
            screen_pos[0] + int(tip_length * np.sin(rad)),
            screen_pos[1] - int(tip_length * np.cos(rad))
        )
        base_center = (
            screen_pos[0] - int(base_length * np.sin(rad)),
            screen_pos[1] + int(base_length * np.cos(rad))
        )
        left = (
            base_center[0] + int(half_width * np.sin(rad + np.pi/2)),
            base_center[1] - int(half_width * np.cos(rad + np.pi/2))
        )
        right = (
            base_center[0] + int(half_width * np.sin(rad - np.pi/2)),
            base_center[1] - int(half_width * np.cos(rad - np.pi/2))
        )
        
        pygame.draw.polygon(self.screen, color, [tip, left, right])

    def draw_arena(self) -> None:
        """Draw the arena border."""
        pygame.draw.circle(
            self.screen,
            config.BORDER_COLOR,
            self.center,
            int(config.ARENA_RADIUS * config.SCALE),
            2
        )

    def draw_target(self, target: Target) -> None:
        """Draw a target."""
        screen_pos = target.position.to_screen_coords(self.center, config.SCALE)
        pygame.draw.circle(
            self.screen,
            config.TARGET_COLOR,
            screen_pos,
            int(target.radius * config.SCALE)
        )

    def draw_thermometer(self, distance: float) -> None:
        """Draw movement distance indicator."""
        bar_x, bar_y = 50, 30
        max_bar_width = int(config.ARENA_DIAMETER * config.SCALE)
        bar_height = 20
        accumulation_factor = 200
        bar_width = min(max_bar_width, int(distance * accumulation_factor))
        
        label = self.font.render("Forward/Backward Movement", True, config.WHITE)
        self.screen.blit(label, (bar_x, bar_y - 25))
        
        pygame.draw.rect(self.screen, config.WHITE, (bar_x, bar_y, max_bar_width, bar_height), 2)
        pygame.draw.rect(self.screen, config.TARGET_COLOR, (bar_x, bar_y, bar_width, bar_height))

    def draw_clock(self, angle: float) -> None:
        """Draw rotation angle indicator."""
        dial_center = (config.WIN_WIDTH - 100, 75)
        dial_radius = 50

        label = self.font.render("Rotation Angle", True, config.WHITE)
        label_rect = label.get_rect(center=(dial_center[0], dial_center[1] - dial_radius - 15))
        self.screen.blit(label, label_rect)

        pygame.draw.circle(self.screen, config.WHITE, dial_center, dial_radius, 2)
        rad = np.radians(angle)
        end_pos = (
            dial_center[0] + int(dial_radius * np.sin(rad)),
            dial_center[1] - int(dial_radius * np.cos(rad))
        )
        pygame.draw.line(self.screen, config.CLOCK_COLOR, dial_center, end_pos, 4)
        
        angle_text = self.font.render(f"{angle:.1f}°", True, config.WHITE)
        self.screen.blit(angle_text, (dial_center[0] - 20, dial_center[1] - 10))

    def draw_trial_counter(self, current: int, total: int) -> None:
        """Draw trial progress counter."""
        text = f"{current}/{total}"
        counter = self.font.render(text, True, config.WHITE)
        rect = counter.get_rect()
        rect.bottomright = (config.WIN_WIDTH - 20, config.WIN_HEIGHT - 20)
        self.screen.blit(counter, rect)

    def render_game_state(self, state: GameState, show_debug: bool = False) -> None:
        """Main render function for the game state."""
        self.screen.fill(config.BACKGROUND_COLOR)
        
        if state.current_phase == "exploration":
            self.draw_arena()
            self.draw_player(state.player, config.AVATAR_COLOR)
            if show_debug:
                for target in state.targets:
                    self.draw_target(target)
                    
        elif state.current_phase == "annotation":
            self.draw_arena()
            if state.annotation_marker:
                self.draw_player(state.annotation_marker, config.CLOCK_COLOR)
            instruction = self.font.render(
                "Navigate to the location of the target, and press Enter to finalize your decision",
                True, config.WHITE
            )
            self.screen.blit(instruction, (20, 20))
            
        elif state.current_phase == "feedback":
            self.draw_arena()
            if state.encountered_target:
                self.draw_target(state.encountered_target)
            if state.annotation_marker:
                self.draw_player(state.annotation_marker, config.CLOCK_COLOR)
                
        pygame.display.flip() 