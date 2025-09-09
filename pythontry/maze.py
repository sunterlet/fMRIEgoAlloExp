from ursina import *

app = Ursina()

# Define the maze grid: 1 = wall, 0 = open space.
maze = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,0,0,1],
    [1,0,1,0,0,0,1,0,0,1],
    [1,0,1,0,1,0,1,0,0,1],
    [1,0,0,0,1,0,1,0,0,1],
    [1,0,1,0,0,0,1,0,0,1],
    [1,0,1,1,1,1,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1],
]

# Create maze walls: walls are 2 units tall so they appear full height.
walls = []
for z, row in enumerate(maze):
    for x, cell in enumerate(row):
        if cell == 1:
            wall = Entity(
                model='cube',
                collider='box',
                texture='white_cube',
                scale=(1, 2, 1),      # wall is 2 units tall
                position=(x, 1, z),    # center at y=1 (spanning 0 to 2)
                color=color.gray
            )
            walls.append(wall)

# Create the floor.
floor = Entity(
    model='quad',
    scale=(len(maze[0]), len(maze)),
    texture='white_cube',
    rotation_x=90,
    position=((len(maze[0]) - 1) / 2, 0, (len(maze) - 1) / 2),
    color=color.light_gray
)
# Remove collider from the floor so it won't interfere with movement.
floor.collider = None

# Create the player as a small red dot.
player = Entity(
    model='sphere',
    collider='box',
    scale=0.2,
    color=color.red,
)
# Place the player slightly above the floor.
player.position = (1, 0.1, 1)

# Set up the camera: parent it to the player and position at eye level.
camera.parent = player
camera.position = (0, 1.6, 0)  # human eye level relative to player
camera.rotation = (0, 0, 0)

# Arrow keys: up/down move forward/backward; left/right rotate.
def update():
    speed = 3 * time.dt          # movement speed
    rot_speed = 90 * time.dt     # rotation speed in degrees per second
    old_pos = player.position
    old_rot = player.rotation_y

    if held_keys['up arrow']:
        player.position += player.forward * speed
    if held_keys['down arrow']:
        player.position -= player.forward * speed
    if held_keys['left arrow']:
        player.rotation_y -= rot_speed
    if held_keys['right arrow']:
        player.rotation_y += rot_speed

    # Check collisions only with walls.
    hit_info = player.intersects()
    if hit_info.hit:
        player.position = old_pos
        player.rotation_y = old_rot

# Press Escape to exit the application.
def input(key):
    if key == 'escape':
        application.quit()

app.run()
