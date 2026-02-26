#!/usr/bin/env python3
"""
Vection experiment (Pygame): first-person movement in darkness with a floor dot grid.
Optic flow is driven by keyboard (no landmarks).

Controls:
  6 - rotate left
  7 - move forward
  8 - move backward
  9 - rotate right
  Escape - quit
"""

import math
import pygame

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
EYE_HEIGHT = 1.6
MOVE_SPEED = 2.0
TURN_SPEED = 1.2  # rad/s
GRID_EXTENT = 60
GRID_SPACING = 1.5
DOT_COLOR = (217, 217, 230)   # RGB 0–255 (alpha set separately)
DOT_ALPHA = 165              # max opacity 0–255 (less transparent)
BACKGROUND_COLOR = (5, 5, 8)
FOV_DEG = 70
DOT_RADIUS_PX = 3
Z_NEAR = 0.5   # don't draw dots closer than this (avoid div by zero / huge projection)
Z_FAR = 14     # don't draw dots beyond this depth (shallower, no horizon)
DOTS_VISIBLE_RADIUS = 16    # only show dots within this horizontal distance (nearby only)
FADE_IN_SPEED = 5.0   # fade-in per second when movement starts

# Debug minimap (top-down view)
MINIMAP_SIZE = 180
MINIMAP_MARGIN = 12
MINIMAP_WORLD_RADIUS = 30   # world units visible around avatar
MINIMAP_BG_COLOR = (3, 3, 1, 255)  # Same near-black as fullscreen task background
MINIMAP_GRID_COLOR = (80, 80, 90, 100)
# Match exploration_trigger/snake.py avatar (Folly)
MINIMAP_AVATAR_COLOR = (255, 67, 101)
MINIMAP_AVATAR_HEADING_COLOR = (200, 50, 80)


def make_floor_dots(extent: float, spacing: float) -> list:
    """List of (x, y, z) for grid on y=0."""
    points = []
    x = -extent
    while x <= extent:
        z = -extent
        while z <= extent:
            points.append((x, 0.0, z))
            z += spacing
        x += spacing
    return points


def world_to_camera(wx: float, wy: float, wz: float,
                    px: float, py: float, pz: float, yaw: float) -> tuple:
    """Convert world (wx,wy,wz) to camera-space (cx, cy, cz). Same axes as movement forward."""
    dx, dy, dz = wx - px, wy - py, wz - pz
    c, s = math.cos(yaw), math.sin(yaw)
    # Forward (where we look / move with 7) = (-s, 0, -c). Right = (c, 0, -s). Up = (0,1,0).
    # Camera-space: x = right, y = up, z = forward (depth, positive = in front).
    cx = dx * c - dz * s   # V · right
    cy = dy                # V · up
    cz = -dx * s - dz * c  # V · forward (depth)
    return cx, cy, cz


def project_to_screen(cx: float, cy: float, cz: float,
                      width: int, height: int, fov_deg: float):
    """Perspective project camera-space (cx,cy,cz) to screen (sx, sy). Returns None if behind or too far."""
    if cz <= Z_NEAR or cz > Z_FAR:
        return None
    fov_rad = math.radians(fov_deg)
    scale = (height / 2.0) / math.tan(fov_rad / 2.0)
    sx = width / 2.0 + (cx / cz) * scale
    sy = height / 2.0 - (cy / cz) * scale
    return sx, sy


def world_to_minimap(wx: float, wz: float, px: float, pz: float,
                     map_size: int, world_radius: float) -> tuple:
    """Convert world (x,z) to minimap pixel (mx, my). Top-down: +x right, +z down on screen."""
    scale = map_size / (2 * world_radius)
    mx = map_size / 2.0 + (wx - px) * scale
    my = map_size / 2.0 + (wz - pz) * scale  # +z down (world -z = forward at yaw=0)
    return mx, my


def draw_minimap(screen: pygame.Surface, px: float, pz: float, yaw: float, dots: list):
    """Draw debug top-down minimap with avatar and floor grid context."""
    w, h = screen.get_size()
    map_size = MINIMAP_SIZE
    radius = MINIMAP_WORLD_RADIUS
    # Top-right corner
    mx = w - map_size - MINIMAP_MARGIN
    my = MINIMAP_MARGIN

    layer = pygame.Surface((map_size, map_size), pygame.SRCALPHA)
    layer.fill(MINIMAP_BG_COLOR)

    # Draw floor dots (sparse sample for context)
    for (wx, _wy, wz) in dots:
        if abs(wx - px) > radius or abs(wz - pz) > radius:
            continue
        mmx, mmy = world_to_minimap(wx, wz, px, pz, map_size, radius)
        if 0 <= mmx < map_size and 0 <= mmy < map_size:
            pygame.draw.circle(layer, MINIMAP_GRID_COLOR, (int(mmx), int(mmy)), 1)

    # Avatar: triangle pointing in facing direction
    cx, cy = map_size / 2.0, map_size / 2.0  # avatar at center (we're always centered)
    tip_len = 10
    base_len = 6
    # Forward direction in world: (-sin(yaw), -cos(yaw))
    fx, fz = -math.sin(yaw), -math.cos(yaw)
    # Right direction: (cos(yaw), -sin(yaw))
    rx, rz = math.cos(yaw), -math.sin(yaw)
    # Triangle: tip at front, base at back
    tip_x = cx + fx * tip_len
    tip_y = cy + fz * tip_len
    base_left_x = cx - fx * base_len - rx * base_len
    base_left_y = cy - fz * base_len - rz * base_len
    base_right_x = cx - fx * base_len + rx * base_len
    base_right_y = cy - fz * base_len + rz * base_len
    pygame.draw.polygon(layer, MINIMAP_AVATAR_COLOR, [
        (tip_x, tip_y), (base_left_x, base_left_y), (base_right_x, base_right_y)
    ])
    pygame.draw.polygon(layer, MINIMAP_AVATAR_HEADING_COLOR, [
        (tip_x, tip_y), (base_left_x, base_left_y), (base_right_x, base_right_y)
    ], 1)

    screen.blit(layer, (mx, my))


def main():
    pygame.init()
    width, height = 1280, 720
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Vection — 6: left | 7: forward | 8: back | 9: right")

    dots = make_floor_dots(GRID_EXTENT, GRID_SPACING)
    # Camera: position (x, y, z), yaw (0 = looking along -Z)
    px, py, pz = 0.0, EYE_HEIGHT, 0.0
    yaw = 0.0
    keys_held = set()
    clock = pygame.time.Clock()
    running = True
    fade_factor = 0.0  # 0 = no dots, 1 = full visibility; fades in/out with movement

    while running:
        dt = clock.tick(60) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                else:
                    keys_held.add(e.key)
            elif e.type == pygame.KEYUP:
                keys_held.discard(e.key)

        # Movement: forward = direction we look; same as view so heading and motion align.
        forward_x = -math.sin(yaw)
        forward_z = -math.cos(yaw)
        # 7 = forward, 8 = backward (along viewing direction)
        if pygame.K_7 in keys_held or pygame.K_KP7 in keys_held:
            px += forward_x * MOVE_SPEED * dt
            pz += forward_z * MOVE_SPEED * dt
        if pygame.K_8 in keys_held or pygame.K_KP8 in keys_held:
            px -= forward_x * MOVE_SPEED * dt
            pz -= forward_z * MOVE_SPEED * dt
        # 6 = rotate left, 9 = rotate right
        if pygame.K_6 in keys_held or pygame.K_KP6 in keys_held:
            yaw += TURN_SPEED * dt
        if pygame.K_9 in keys_held or pygame.K_KP9 in keys_held:
            yaw -= TURN_SPEED * dt

        screen.fill(BACKGROUND_COLOR)

        moving = (
            pygame.K_6 in keys_held or pygame.K_KP6 in keys_held
            or pygame.K_7 in keys_held or pygame.K_KP7 in keys_held
            or pygame.K_8 in keys_held or pygame.K_KP8 in keys_held
            or pygame.K_9 in keys_held or pygame.K_KP9 in keys_held
        )
        # Fade in when moving; once visible, stay visible (no fade-out between movements)
        if moving:
            fade_factor = min(1.0, fade_factor + FADE_IN_SPEED * dt)

        if fade_factor > 0.01:
            w, h = screen.get_size()
            alpha = int(DOT_ALPHA * fade_factor)
            dot_color_rgba = (*DOT_COLOR, alpha)
            layer = pygame.Surface((w, h), pygame.SRCALPHA)
            radius_sq = DOTS_VISIBLE_RADIUS * DOTS_VISIBLE_RADIUS
            for (wx, wy, wz) in dots:
                dist_sq = (wx - px) * (wx - px) + (wz - pz) * (wz - pz)
                if dist_sq > radius_sq:
                    continue
                cx, cy, cz = world_to_camera(wx, wy, wz, px, py, pz, yaw)
                pt = project_to_screen(cx, cy, cz, w, h, FOV_DEG)
                if pt is not None:
                    sx, sy = int(pt[0]), int(pt[1])
                    if 0 <= sx < w and 0 <= sy < h:
                        pygame.draw.circle(layer, dot_color_rgba, (sx, sy), DOT_RADIUS_PX)
            screen.blit(layer, (0, 0))

        draw_minimap(screen, px, pz, yaw, dots)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
