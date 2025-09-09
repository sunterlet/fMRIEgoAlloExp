#!/usr/bin/env python
"""
PsychoPy Conversion of Exploration Experiment
Originally implemented in pygame

Key changes:
• Uses a single PsychoPy window with units set to "cm".
• A proper monitor profile is defined (using a Monitor object) so that pixel‐to‐cm conversions work.
• Drawing of arena, avatar, targets, thermometer, and clock are done via PsychoPy’s visual stimuli.
• Events are handled with psychopy.event.getKeys.
• Sound playback is done via psychopy.sound.Sound.
• Data logging uses PsychoPy’s ExperimentHandler.
• The code is split into modular functions for instructions, trial handling, etc.
"""

import os, math, random, json, time
from psychopy import visual, event, core, data, sound, monitors

# ---------------------------
# Experiment Configuration (converted to cm)
# ---------------------------
# Arena parameters (converted from meters to centimeters)
ARENA_DIAMETER = 330              # 3.3 m --> 330 cm
ARENA_RADIUS = ARENA_DIAMETER / 2   # 165 cm
BORDER_THRESHOLD = 10             # 0.1 m --> 10 cm

# Target parameters
TARGET_RADIUS = 10                # 0.1 m --> 10 cm
DEFAULT_TARGET_COUNT = 3          # number of targets per trial

# Movement settings
MOVE_SPEED = 100                  # 1 m/s --> 100 cm/s
ROTATE_SPEED = 90                 # degrees per second

# Window size in centimeters (rough equivalent to original design)
WIN_WIDTH_CM = 33
WIN_HEIGHT_CM = 26.4

# ---------------------------
# Color Palette (using rgb255 values)
# ---------------------------
BACKGROUND_COLOR = (3, 3, 1)        # near-black
AVATAR_COLOR = (255, 67, 101)       # Folly
BORDER_COLOR = (255, 255, 243)      # Ivory
TARGET_COLOR = (0, 217, 192)        # Turquoise
CLOCK_COLOR = (183, 173, 153)       # Khaki
WHITE = (255, 255, 255)
DEBUG_COLOR = (50, 50, 255)

# ---------------------------
# Sound & Instruction Paths
# ---------------------------
SOUNDS_DIR = "sounds"
TARGET_SOUND_PATH = os.path.join(SOUNDS_DIR, "target.wav")
BEEP_SOUND_PATH = os.path.join(SOUNDS_DIR, "beep.wav")
INSTRUCTIONS_DIR = "Instructions"

# ---------------------------
# Experiment Parameters
# ---------------------------
TRAINING_SESSIONS = 3
DARK_TRAINING_TRIALS = 2
TEST_TRIALS = 5

# Predefined target positions (converted from meters to centimeters)
PREDEFINED_TARGETS = {
    "training 1": [(-50, -100), (30, 80), (-100, 20)],
    "training 2": [(70, -80), (-40, 90), (30, -120)],
    "training 3": [(-80, -50), (50, 50), (20, -100)],
    "dark_training 1": [(-60, -90), (40, 70), (-90, 10)],
    "dark_training 2": [(20, -100), (-30, 80), (70, -60)],
    "test 1": [(50, 100), (-80, -20), (70, -70)],
    "test 2": [(-30, 70), (80, 20), (-90, -90)],
    "test 3": [(40, -40), (-60, 80), (20, 100)],
    "test 4": [(90, -30), (-40, -100), (100, 80)],
    "test 5": [(-20, -80), (50, 60), (-70, 120)]
}

# ---------------------------
# Global Initialization: Monitor, Window, Clock, Sounds, and Data Handler
# ---------------------------
# Create a monitor specification (update these values as needed for your setup)
myMonitor = monitors.Monitor('testMonitor')
myMonitor.setWidth(34)            # Physical width in cm
myMonitor.setSizePix([1280, 720])   # Screen resolution in pixels

# Create a PsychoPy window using the defined monitor.
win = visual.Window(
    size=(1000, 800),          # window size in pixels
    monitor=myMonitor,         # use our monitor object
    units="cm",
    color=BACKGROUND_COLOR,
    colorSpace='rgb255',
    fullscr=False
)
win.setMouseVisible(False)

# Global clock
global_clock = core.Clock()

# Load sounds using PsychoPy's sound module
try:
    beep_sound = sound.Sound(BEEP_SOUND_PATH, secs=0.5, stereo=True, loops=-1)
except Exception as e:
    print("Error loading beep sound:", e)
    beep_sound = None
try:
    target_sound = sound.Sound(TARGET_SOUND_PATH)
except Exception as e:
    print("Error loading target sound:", e)
    target_sound = None

# Create an ExperimentHandler for discrete logs
exp = data.ExperimentHandler(name="ExplorationExperiment", dataFileName="discrete_log")

# Continuous logs
continuous_logs = []


# ---------------------------
# Helper Functions for Drawing Stimuli
# ---------------------------
def draw_arena():
    """Draw the arena border as a circle at the center (0,0)."""
    arena = visual.Circle(
        win=win,
        radius=ARENA_RADIUS,
        edges=128,
        lineColor=BORDER_COLOR,
        lineWidth=0.5,
        fillColor=None,
        units="cm",
        pos=(0, 0)
    )
    arena.draw()

def draw_avatar(pos, angle, color=AVATAR_COLOR):
    """
    Draw an elongated triangle representing the player.
    'pos' is a tuple (x, y) in cm.
    'angle' is in degrees, with 0° defined as pointing upward.
    """
    tip_length = 3  # in cm
    base_length = 2
    half_width = 2.5
    angle_rad = math.radians(angle - 90)  # adjust so that 0° points upward
    tip = (pos[0] + tip_length * math.cos(angle_rad),
           pos[1] + tip_length * math.sin(angle_rad))
    base_center = (pos[0] - base_length * math.cos(angle_rad),
                   pos[1] - base_length * math.sin(angle_rad))
    left = (base_center[0] + half_width * math.cos(angle_rad + math.pi/2),
            base_center[1] + half_width * math.sin(angle_rad + math.pi/2))
    right = (base_center[0] + half_width * math.cos(angle_rad - math.pi/2),
             base_center[1] + half_width * math.sin(angle_rad - math.pi/2))
    vertices = [tip, left, right]
    avatar = visual.ShapeStim(
        win=win,
        vertices=vertices,
        fillColor=color,
        lineColor=color,
        closeShape=True,
        units="cm"
    )
    avatar.draw()

def draw_goal(pos, radius=1):
    """Draw the goal/target as a filled circle."""
    goal = visual.Circle(
        win=win,
        radius=radius,
        edges=64,
        fillColor=TARGET_COLOR,
        lineColor=TARGET_COLOR,
        units="cm",
        pos=pos
    )
    goal.draw()

def draw_text(message, pos, color=WHITE, height=1.5):
    """Draw a text message on the screen."""
    txt = visual.TextStim(win=win, text=message, pos=pos, color=color, height=height, units="cm", colorSpace='rgb255')
    txt.draw()

def draw_thermometer(distance_moved):
    """
    Draw a horizontal bar (thermometer) at the top-left showing distance moved.
    """
    bar_x = -WIN_WIDTH_CM/2 + 2
    bar_y = WIN_HEIGHT_CM/2 - 2
    max_bar_width = ARENA_DIAMETER  # in cm
    bar_height = 1.5
    accumulation_factor = 1  # adjustable factor
    bar_width = min(max_bar_width, distance_moved * accumulation_factor)
    
    rect_border = visual.Rect(
        win=win,
        width=max_bar_width,
        height=bar_height,
        lineColor=WHITE,
        fillColor=None,
        pos=(bar_x + max_bar_width/2, bar_y),
        units="cm"
    )
    rect_border.draw()
    
    rect_fill = visual.Rect(
        win=win,
        width=bar_width,
        height=bar_height,
        fillColor=TARGET_COLOR,
        lineColor=TARGET_COLOR,
        pos=(bar_x + bar_width/2, bar_y),
        units="cm"
    )
    rect_fill.draw()
    
    draw_text("Forward/Backward Movement", (bar_x, bar_y + 2), height=1.2)

def draw_clock(angle_rotated):
    """
    Draw a clock-like dial at the top-right showing rotation angle.
    """
    dial_center = (WIN_WIDTH_CM/2 - 4, WIN_HEIGHT_CM/2 - 4)
    dial_radius = 3
    dial = visual.Circle(
        win=win,
        radius=dial_radius,
        edges=64,
        lineColor=WHITE,
        fillColor=None,
        pos=dial_center,
        units="cm"
    )
    dial.draw()
    
    rad = math.radians(angle_rotated)
    end_x = dial_center[0] + dial_radius * math.sin(rad)
    end_y = dial_center[1] + dial_radius * math.cos(rad)
    hand = visual.ShapeStim(
        win=win,
        vertices=[dial_center, (end_x, end_y)],
        lineColor=CLOCK_COLOR,
        lineWidth=3,
        closeShape=False,
        units="cm"
    )
    hand.draw()
    
    draw_text(f"{angle_rotated:.1f}°", (dial_center[0], dial_center[1]-dial_radius-1), height=1.2)

# ---------------------------
# Instruction Display
# ---------------------------
def show_image(image_path):
    """
    Display an instruction image (sized for the window) and wait for a key press.
    """
    instr = visual.ImageStim(win=win, image=image_path, pos=(0, 0),
                             size=(WIN_WIDTH_CM, WIN_HEIGHT_CM), units="cm")
    instr.draw()
    win.flip()
    keys = event.waitKeys(keyList=['return', 'escape'])
    if 'escape' in keys:
        win.close()
        core.quit()

# ---------------------------
# Practice Game
# ---------------------------
def run_practice_game():
    """Runs the practice game where the participant collects goals."""
    score = 0
    avatar_pos = [0, 0]
    avatar_angle = 0
    avatar_speed = 3   # cm per frame
    rotation_speed = 3 # degrees per frame
    goal_radius = 1    # in cm
    
    def random_position_in_arena():
        angle = random.uniform(0, 2 * math.pi)
        r = ARENA_RADIUS * math.sqrt(random.uniform(0, 1))
        return (r * math.cos(angle), r * math.sin(angle))
    
    goal_pos = random_position_in_arena()
    score_text = visual.TextStim(win=win, text=f"Score: {score}", pos=(-WIN_WIDTH_CM/2 + 3, WIN_HEIGHT_CM/2 - 3),
                                 height=1.5, units="cm", color=WHITE, colorSpace='rgb255')
    
    practice_clock = core.Clock()
    running = True
    while running:
        dt = practice_clock.getTime()
        practice_clock.reset()
        keys = event.getKeys(keyList=['up', 'down', 'left', 'right', 'return', 'escape'])
        if 'escape' in keys:
            win.close()
            core.quit()
        if 'return' in keys:
            break
        
        if 'up' in keys:
            rad = math.radians(avatar_angle)
            avatar_pos[0] += avatar_speed * math.cos(rad)
            avatar_pos[1] += avatar_speed * math.sin(rad)
        if 'down' in keys:
            rad = math.radians(avatar_angle)
            avatar_pos[0] -= avatar_speed * math.cos(rad)
            avatar_pos[1] -= avatar_speed * math.sin(rad)
        if 'left' in keys:
            avatar_angle = (avatar_angle - rotation_speed) % 360
        if 'right' in keys:
            avatar_angle = (avatar_angle + rotation_speed) % 360
        
        # Check if avatar’s tip reached the goal
        tip_length = 3
        rad = math.radians(avatar_angle - 90)
        tip_x = avatar_pos[0] + tip_length * math.cos(rad)
        tip_y = avatar_pos[1] + tip_length * math.sin(rad)
        distance_to_goal = math.hypot(tip_x - goal_pos[0], tip_y - goal_pos[1])
        if distance_to_goal < (goal_radius + 0.5):
            score += 1
            goal_pos = random_position_in_arena()

        win.flip()
        draw_arena()
        draw_goal(goal_pos, radius=goal_radius)
        draw_avatar(avatar_pos, avatar_angle)
        score_text.text = f"Score: {score}"
        score_text.draw()
        win.flip()
        
        if score >= 5:
            running = False
        core.wait(0.02)

# ---------------------------
# Trial Function (Training, Dark Training, Test)
# ---------------------------
def run_trial(is_training, trial_info, display_on_border=False):
    """
    Runs a single trial with phases: exploration, annotation, and feedback.
    Returns discrete log info and appends continuous log entries globally.
    """
    if trial_info in PREDEFINED_TARGETS:
        current_targets = PREDEFINED_TARGETS[trial_info].copy()
    else:
        current_targets = []
    
    phase = "exploration"
    player_pos = [0.0, 0.0]
    player_angle = 0.0
    annotation_marker_pos = [0.0, 0.0]
    annotation_marker_angle = 0.0
    target_was_inside = False
    encountered_goal = None
    trial_clock = core.Clock()
    exploration_start_time = trial_clock.getTime()
    annotation_start_time = None
    local_continuous_log = []
    started_moving = False

    trial_running = True
    while trial_running:
        dt = trial_clock.getTime()
        trial_clock.reset()
        t = core.getTime()
        if phase in ["exploration", "annotation"]:
            if phase == "exploration":
                log_entry = {"trial_info": trial_info, "phase": "exploration", "time": t,
                             "x": player_pos[0], "y": player_pos[1]}
            else:
                log_entry = {"trial_info": trial_info, "phase": "annotation", "time": t,
                             "x": annotation_marker_pos[0], "y": annotation_marker_pos[1]}
            local_continuous_log.append(log_entry)
        
        theseKeys = event.getKeys(keyList=['up', 'down', 'left', 'right', 'return', 'escape', 'k'])
        if 'escape' in theseKeys:
            win.close()
            core.quit()
        if 'return' in theseKeys:
            if phase == "exploration":
                exploration_duration = core.getTime() - exploration_start_time
                phase = "annotation"
                annotation_start_time = core.getTime()
                annotation_marker_pos = [0.0, 0.0]
                annotation_marker_angle = 0.0
                if beep_sound is not None:
                    beep_sound.stop()
            elif phase == "annotation":
                annotation_duration = core.getTime() - annotation_start_time
                phase = "feedback"
            elif phase == "feedback":
                trial_running = False
        
        if phase == "exploration":
            if 'up' in theseKeys:
                rad = math.radians(player_angle)
                player_pos[0] += MOVE_SPEED * dt * math.cos(rad)
                player_pos[1] += MOVE_SPEED * dt * math.sin(rad)
            if 'down' in theseKeys:
                rad = math.radians(player_angle)
                player_pos[0] -= MOVE_SPEED * dt * math.cos(rad)
                player_pos[1] -= MOVE_SPEED * dt * math.sin(rad)
            if 'left' in theseKeys:
                player_angle = (player_angle - ROTATE_SPEED * dt) % 360
            if 'right' in theseKeys:
                player_angle = (player_angle + ROTATE_SPEED * dt) % 360
            
            dist_from_center = math.hypot(player_pos[0], player_pos[1])
            if dist_from_center >= (ARENA_RADIUS - BORDER_THRESHOLD):
                if beep_sound is not None:
                    beep_sound.play()
            else:
                if beep_sound is not None:
                    beep_sound.stop()
            
            is_inside_target = False
            encountered = None
            for pos in current_targets:
                if math.hypot(player_pos[0] - pos[0], player_pos[1] - pos[1]) <= TARGET_RADIUS:
                    is_inside_target = True
                    encountered = pos
                    break
            if not target_was_inside and is_inside_target:
                if target_sound is not None:
                    target_sound.play()
                if encountered_goal is None:
                    encountered_goal = encountered
                current_targets = [encountered]
            target_was_inside = is_inside_target
        elif phase == "annotation":
            if 'up' in theseKeys:
                rad = math.radians(annotation_marker_angle)
                annotation_marker_pos[0] += MOVE_SPEED * dt * math.cos(rad)
                annotation_marker_pos[1] += MOVE_SPEED * dt * math.sin(rad)
            if 'down' in theseKeys:
                rad = math.radians(annotation_marker_angle)
                annotation_marker_pos[0] -= MOVE_SPEED * dt * math.cos(rad)
                annotation_marker_pos[1] -= MOVE_SPEED * dt * math.sin(rad)
            if 'left' in theseKeys:
                annotation_marker_angle = (annotation_marker_angle - ROTATE_SPEED * dt) % 360
            if 'right' in theseKeys:
                annotation_marker_angle = (annotation_marker_angle + ROTATE_SPEED * dt) % 360
        
        win.flip()
        draw_arena()
        if phase == "exploration":
            if is_training:
                draw_avatar(player_pos, player_angle)
                if 'up' in theseKeys or 'down' in theseKeys:
                    moved_distance = math.hypot(player_pos[0], player_pos[1])
                    draw_thermometer(moved_distance)
                if 'left' in theseKeys or 'right' in theseKeys:
                    draw_clock(ROTATE_SPEED * dt)
            else:
                if not started_moving:
                    if any(k in theseKeys for k in ['up', 'down', 'left', 'right']):
                        started_moving = True
                    draw_avatar([0, 0], 0)
                else:
                    draw_avatar(player_pos, player_angle)
            if 'k' in theseKeys:
                for pos in current_targets:
                    debug_circle = visual.Circle(
                        win=win, radius=TARGET_RADIUS, edges=64,
                        lineColor=DEBUG_COLOR, fillColor=None,
                        pos=pos, units="cm"
                    )
                    debug_circle.draw()
        elif phase == "annotation":
            draw_text("Navigate to the target location, then press Enter", (-WIN_WIDTH_CM/2 + 3, WIN_HEIGHT_CM/2 - 4))
            draw_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
        elif phase == "feedback":
            if current_targets:
                draw_goal(current_targets[0], radius=TARGET_RADIUS)
            draw_avatar(annotation_marker_pos, annotation_marker_angle, color=CLOCK_COLOR)
        
        parts = trial_info.split()
        if parts[0] == "training":
            total_trials = TRAINING_SESSIONS
        elif parts[0] == "dark_training":
            total_trials = DARK_TRAINING_TRIALS
        elif parts[0] == "test":
            total_trials = TEST_TRIALS
        else:
            total_trials = "?"
        counter_text = f"{parts[1]}/{total_trials}"
        draw_text(counter_text, (WIN_WIDTH_CM/2 - 3, -WIN_HEIGHT_CM/2 + 2))
        
        win.flip()
        core.wait(0.02)

    exploration_time = t if exploration_start_time is not None else 0
    annotation_time = t - exploration_time if annotation_start_time is not None else 0
    error_distance = None
    if encountered_goal is not None:
        error_distance = math.hypot(encountered_goal[0] - annotation_marker_pos[0],
                                    encountered_goal[1] - annotation_marker_pos[1])
    
    discrete_log = {
        "trial_info": trial_info,
        "trial_type": "training" if is_training else "test",
        "exploration_time": exploration_time,
        "annotation_time": annotation_time,
        "encountered_goal": encountered_goal,
        "annotation": annotation_marker_pos,
        "error_distance": error_distance
    }
    
    exp.addData('trial_info', trial_info)
    exp.addData('trial_type', discrete_log["trial_type"])
    exp.addData('exploration_time', exploration_time)
    exp.addData('annotation_time', annotation_time)
    exp.addData('encountered_goal', json.dumps(encountered_goal))
    exp.addData('annotation', json.dumps(annotation_marker_pos))
    exp.addData('error_distance', error_distance)
    exp.nextEntry()
    
    continuous_logs.extend(local_continuous_log)
    
    return discrete_log

# ---------------------------
# Main Experiment Loop
# ---------------------------
def run_experiment():
    training_trial = 1
    dark_training_trial = 1
    test_trial = 1

    show_image(os.path.join(INSTRUCTIONS_DIR, "1.png"))
    show_image(os.path.join(INSTRUCTIONS_DIR, "2.png"))
    run_practice_game()
    show_image(os.path.join(INSTRUCTIONS_DIR, "3.png"))

    print("Starting Training Block")
    for session in range(1, TRAINING_SESSIONS + 1):
        trial_info = f"training {training_trial}"
        print(f"Training Session {session} ({trial_info})")
        run_trial(is_training=True, trial_info=trial_info)
        training_trial += 1
    
    show_image(os.path.join(INSTRUCTIONS_DIR, "4.png"))
    print("Starting Dark Training Block")
    for d in range(1, DARK_TRAINING_TRIALS + 1):
        trial_info = f"dark_training {dark_training_trial}"
        print(f"Dark Training Trial {d} ({trial_info})")
        run_trial(is_training=False, trial_info=trial_info, display_on_border=True)
        dark_training_trial += 1
    
    show_image(os.path.join(INSTRUCTIONS_DIR, "5.png"))
    print("Starting Test Block")
    for t in range(1, TEST_TRIALS + 1):
        trial_info = f"test {test_trial}"
        print(f"Test Trial {t} ({trial_info})")
        run_trial(is_training=False, trial_info=trial_info, display_on_border=False)
        test_trial += 1
    
    show_image(os.path.join(INSTRUCTIONS_DIR, "6.png"))
    draw_text("Experiment complete. Press Escape to exit.", (0, 0))
    win.flip()
    while True:
        keys = event.waitKeys(keyList=['escape'])
        if 'escape' in keys:
            break

if __name__ == '__main__':
    run_experiment()
    exp.saveAsWideText("discrete_log.csv", delim=",")
    # Optionally, save continuous_logs to a CSV file here if needed.
    win.close()
    core.quit()
