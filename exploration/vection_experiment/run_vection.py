#!/usr/bin/env python3
"""
Vection experiment: first-person movement in darkness with a floor dot grid.
Optic flow is driven by keyboard (no landmarks).

Controls:
  6 - rotate left
  7 - move forward
  8 - move backward
  9 - rotate right
  Escape - quit
"""

import math
import pyglet
from pyglet.math import Mat4, Vec3
from pyglet.graphics import Batch, Group
from pyglet.gl import GL_TRIANGLES, glClearColor

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
EYE_HEIGHT = 1.6
MOVE_SPEED = 2.0
TURN_SPEED = 1.2  # rad/s
GRID_EXTENT = 60   # half-size of floor grid (world units)
GRID_SPACING = 1.5
DOT_RADIUS = 0.08  # world-unit size of each dot (quad half-size)
DOT_COLOR = (0.85, 0.85, 0.9)
BACKGROUND_COLOR = (0.02, 0.02, 0.03)
Z_NEAR, Z_FAR = 0.1, 400.0
FOV_DEG = 70


def make_floor_dots(extent: float, spacing: float, radius: float, color: tuple) -> tuple:
    """Build vertex arrays for a grid of small quads (dots) on y=0. Each dot = 2 triangles."""
    positions = []
    colors = []
    x = -extent
    while x <= extent:
        z = -extent
        while z <= extent:
            # Quad corners: (x±r, 0, z±r) — two triangles
            r = radius
            # tri 1
            positions.extend((x - r, 0.0, z - r, x + r, 0.0, z - r, x + r, 0.0, z + r))
            colors.extend(color * 3)
            # tri 2
            positions.extend((x - r, 0.0, z - r, x + r, 0.0, z + r, x - r, 0.0, z + r))
            colors.extend(color * 3)
            z += spacing
        x += spacing
    n_vertices = len(positions) // 3
    return positions, colors, n_vertices


class VectionWindow(pyglet.window.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Camera state: position (x, y, z), yaw (radians, 0 = looking along -Z)
        self.pos = Vec3(0.0, EYE_HEIGHT, 0.0)
        self.yaw = 0.0

        # Floor dot grid (each dot = small quad = 2 triangles)
        positions, colors, n_vertices = make_floor_dots(
            GRID_EXTENT, GRID_SPACING, DOT_RADIUS, DOT_COLOR
        )
        self._batch = Batch()
        self._batch.add(
            n_vertices,
            GL_TRIANGLES,
            None,
            ("v3f", positions),
            ("c3f", colors),
        )

        # Key state for smooth motion
        self.keys = set()

        # Resize to set projection
        self._update_projection()

    def _update_projection(self):
        aspect = self.width / max(1, self.height)
        self.projection = Mat4.perspective_projection(
            aspect, Z_NEAR, Z_FAR, fov=FOV_DEG
        )

    def _forward_vector(self) -> Vec3:
        return Vec3(-math.sin(self.yaw), 0.0, -math.cos(self.yaw))

    def _view_matrix(self) -> Mat4:
        forward = self._forward_vector()
        target = self.pos + forward
        up = Vec3(0.0, 1.0, 0.0)
        return Mat4.look_at(self.pos, target, up)

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self._update_projection()
        return pyglet.event.EVENT_HANDLED

    def on_key_press(self, symbol: int, modifiers: int):
        self.keys.add(symbol)
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol: int, modifiers: int):
        self.keys.discard(symbol)

    def update(self, dt: float):
        forward = self._forward_vector()
        if pyglet.window.key.NUM_7 in self.keys or pyglet.window.key.NUM_ADD in self.keys:
            self.pos += forward * MOVE_SPEED * dt
        if pyglet.window.key.NUM_8 in self.keys or pyglet.window.key.NUM_SUBTRACT in self.keys:
            self.pos -= forward * MOVE_SPEED * dt
        if pyglet.window.key.NUM_6 in self.keys:
            self.yaw += TURN_SPEED * dt
        if pyglet.window.key.NUM_9 in self.keys:
            self.yaw -= TURN_SPEED * dt
        # Also support main keyboard 6,7,8,9 (no numlock assumption)
        if pyglet.window.key._6 in self.keys:
            self.yaw += TURN_SPEED * dt
        if pyglet.window.key._7 in self.keys:
            self.pos += forward * MOVE_SPEED * dt
        if pyglet.window.key._8 in self.keys:
            self.pos -= forward * MOVE_SPEED * dt
        if pyglet.window.key._9 in self.keys:
            self.yaw -= TURN_SPEED * dt

    def on_draw(self):
        r, g, b = BACKGROUND_COLOR
        glClearColor(r, g, b, 1.0)
        self.clear()
        self.view = self._view_matrix()
        self._batch.draw()


def main():
    window = VectionWindow(
        width=1280,
        height=720,
        caption="Vection experiment — 6: left | 7: forward | 8: back | 9: right",
        resizable=True,
    )
    pyglet.clock.schedule_interval(window.update, 1 / 60.0)
    pyglet.app.run()


if __name__ == "__main__":
    main()
