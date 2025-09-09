from typing import List, Optional
import numpy as np
import pygame
from .models import Vector2D
from .config import config

class Player:
    def __init__(self, position: Vector2D = Vector2D(0.0, 0.0), angle: float = 0.0):
        self.position = position
        self.angle = angle
        self.move_speed = config.MOVE_SPEED
        self.rotate_speed = config.ROTATE_SPEED

    def move(self, direction: float, dt: float, arena_radius: float) -> bool:
        """Move the player in the current direction.
        Returns True if movement was possible, False if blocked by arena boundary."""
        rad = np.radians(self.angle)
        movement = Vector2D(
            np.sin(rad) * self.move_speed * dt * direction,
            np.cos(rad) * self.move_speed * dt * direction
        )
        new_pos = self.position + movement
        
        if new_pos.magnitude() <= arena_radius:
            self.position = new_pos
            return True
        return False

    def rotate(self, direction: float, dt: float) -> None:
        """Rotate the player. direction: 1 for right, -1 for left."""
        self.angle += self.rotate_speed * dt * direction
        self.angle %= 360.0

class Target:
    def __init__(self, position: Vector2D):
        self.position = position
        self.radius = config.TARGET_RADIUS

    def check_collision(self, point: Vector2D) -> bool:
        """Check if a point is within the target's radius."""
        return (point - self.position).magnitude() <= self.radius

class Arena:
    def __init__(self):
        self.radius = config.ARENA_RADIUS
        self.border_threshold = config.BORDER_THRESHOLD
        
    def is_near_border(self, position: Vector2D) -> bool:
        """Check if a position is near the arena border."""
        return position.magnitude() >= (self.radius - self.border_threshold)

    def contains_point(self, position: Vector2D) -> bool:
        """Check if a position is within the arena."""
        return position.magnitude() <= self.radius

class GameState:
    def __init__(self):
        self.player = Player()
        self.arena = Arena()
        self.targets: List[Target] = []
        self.current_phase = "exploration"
        self.annotation_marker: Optional[Player] = None
        self.encountered_target: Optional[Target] = None
        self.start_time = pygame.time.get_ticks()
        
    def update(self, dt: float, keys: List[bool]) -> None:
        """Update game state based on input."""
        if self.current_phase == "exploration":
            if keys[pygame.K_UP]:
                self.player.move(1, dt, self.arena.radius)
            if keys[pygame.K_DOWN]:
                self.player.move(-1, dt, self.arena.radius)
            if keys[pygame.K_LEFT]:
                self.player.rotate(-1, dt)
            if keys[pygame.K_RIGHT]:
                self.player.rotate(1, dt)
            
            # Check target collisions
            for target in self.targets:
                if target.check_collision(self.player.position):
                    self.encountered_target = target
                    self.targets = [target]  # Keep only the encountered target
                    
        elif self.current_phase == "annotation":
            if not self.annotation_marker:
                self.annotation_marker = Player()
            
            if keys[pygame.K_UP]:
                self.annotation_marker.move(1, dt, self.arena.radius)
            if keys[pygame.K_DOWN]:
                self.annotation_marker.move(-1, dt, self.arena.radius)
            if keys[pygame.K_LEFT]:
                self.annotation_marker.rotate(-1, dt)
            if keys[pygame.K_RIGHT]:
                self.annotation_marker.rotate(1, dt) 