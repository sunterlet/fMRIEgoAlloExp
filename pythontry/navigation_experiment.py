from psychopy import visual, core, event, sound, gui, data
import numpy as np
import math
import os
import json
import csv
from datetime import datetime

# ---------------------------
# Configuration parameters
# ---------------------------
# Arena parameters (in meters)
ARENA_DIAMETER = 3.3                # meters
ARENA_RADIUS = ARENA_DIAMETER / 2.0   # 1.65 m
BORDER_THRESHOLD = 0.1              # threshold from border in meters

# Target parameters
TARGET_RADIUS = 0.1                 # reduced target radius in meters
DEFAULT_TARGET_COUNT = 3            # number of targets per trial

# Movement settings
MOVE_SPEED = 1.0                    # meters per second
ROTATE_SPEED = 90.0                 # degrees per second

# Scale factor: pixels per meter
SCALE = 200                         # 1 meter = 200 pixels

# Window size
WIN_WIDTH = 1000
WIN_HEIGHT = 800
CENTER_SCREEN = (WIN_WIDTH // 2, WIN_HEIGHT // 2)

# Colors
BACKGROUND_COLOR = (3, 3, 1)        # Background: near-black
AVATAR_COLOR = (255, 67, 101)       # Avatar: Folly
BORDER_COLOR = (255, 255, 243)      # Arena border: Ivory
TARGET_COLOR = (0, 217, 192)        # Targets and thermometer: Turquoise
CLOCK_COLOR = (183, 173, 153)       # Clock rotation, Annotation and Feedback avatar: Khaki
WHITE = (255, 255, 255)
DEBUG_COLOR = (50, 50, 255)

# Experiment parameters
TRAINING_SESSIONS = 3
DARK_TRAINING_TRIALS = 2
TEST_TRIALS = 5

# ---------------------------
# Predefined target positions
# ---------------------------
PREDEFINED_TARGETS = {
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

class NavigationExperiment:
    def __init__(self):
        # Create a dialog to get participant info
        self.expInfo = {
            'participant': '',
            'session': '001',
        }
        self.dlg = gui.DlgFromDict(dictionary=self.expInfo, title='Navigation Experiment')
        if not self.dlg.OK:
            core.quit()
        
        # Setup the window
        self.win = visual.Window(
            size=[WIN_WIDTH, WIN_HEIGHT],
            fullscr=False,
            color=BACKGROUND_COLOR,
            units='pix'
        )
        
        # Setup sounds
        self.sounds_dir = "/Volumes/ramot/sunt/Navigation/fMRI/sounds/"
        self.target_sound = sound.Sound(os.path.join(self.sounds_dir, "target.wav"))
        self.beep_sound = sound.Sound(os.path.join(self.sounds_dir, "beep.wav"))
        
        # Setup logging
        self.results_dir = "/Volumes/ramot/sunt/Navigation/fMRI/pythontry/results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.discrete_filename = os.path.join(
            self.results_dir, 
            f"{self.expInfo['participant']}_{timestamp}_discrete_log.csv"
        )
        self.continuous_filename = os.path.join(
            self.results_dir, 
            f"{self.expInfo['participant']}_{timestamp}_continuous_log.csv"
        )
        
        # Initialize experiment variables
        self.all_discrete_logs = []
        self.all_continuous_logs = []
        self.training_trial = 1
        self.dark_training_trial = 1
        self.test_trial = 1
        
        # Create visual elements
        self._create_visual_elements()
    
    def _create_visual_elements(self):
        """Create all visual elements used in the experiment"""
        # Arena border
        self.arena = visual.Circle(
            win=self.win,
            radius=ARENA_RADIUS * SCALE,
            edges=128,
            lineColor=BORDER_COLOR,
            lineWidth=2,
            fillColor=None,
            pos=(0, 0)
        )
        
        # Avatar (triangle)
        self.avatar = visual.ShapeStim(
            win=self.win,
            vertices=[[0, 30], [-17, -20], [17, -20]],  # Triangle shape
            fillColor=AVATAR_COLOR,
            lineColor=None,
            pos=(0, 0)
        )
        
        # Target
        self.target = visual.Circle(
            win=self.win,
            radius=TARGET_RADIUS * SCALE,
            edges=32,
            lineColor=TARGET_COLOR,
            fillColor=TARGET_COLOR,
            pos=(0, 0)
        )
        
        # Thermometer
        self.thermometer = visual.Rect(
            win=self.win,
            width=ARENA_DIAMETER * SCALE,
            height=20,
            lineColor=WHITE,
            fillColor=TARGET_COLOR,
            pos=(-WIN_WIDTH/2 + 50 + (ARENA_DIAMETER * SCALE)/2, WIN_HEIGHT/2 - 30)
        )
        
        # Clock
        self.clock = visual.Circle(
            win=self.win,
            radius=50,
            edges=128,
            lineColor=WHITE,
            fillColor=None,
            pos=(WIN_WIDTH/2 - 100, WIN_HEIGHT/2 - 75)
        )
        self.clock_hand = visual.Line(
            win=self.win,
            start=(WIN_WIDTH/2 - 100, WIN_HEIGHT/2 - 75),
            end=(WIN_WIDTH/2 - 100, WIN_HEIGHT/2 - 125),
            lineColor=CLOCK_COLOR,
            lineWidth=4
        )
        
        # Text elements
        self.instruction_text = visual.TextStim(
            win=self.win,
            text='',
            color=WHITE,
            height=20,
            pos=(0, WIN_HEIGHT/2 - 50)
        )
        
        self.counter_text = visual.TextStim(
            win=self.win,
            text='',
            color=WHITE,
            height=24,
            pos=(WIN_WIDTH/2 - 20, -WIN_HEIGHT/2 + 20)
        )
    
    def to_screen_coords(self, pos):
        """Convert arena coordinates (in meters) to screen coordinates (in pixels)"""
        x, y = pos
        screen_x = x * SCALE
        screen_y = -y * SCALE  # Invert y-axis to match screen coordinates
        return (screen_x, screen_y)
    
    def distance(self, a, b):
        """Euclidean distance between two points"""
        return math.hypot(a[0] - b[0], a[1] - b[1])
    
    def run_trial(self, is_training, trial_info):
        """Run a single trial of the experiment"""
        # Initialize trial variables
        player_pos = [0.0, 0.0]
        player_angle = 0.0
        phase = "exploration"
        current_target_positions = PREDEFINED_TARGETS[trial_info].copy()
        continuous_log = []
        encountered_goal = None
        
        # Trial loop
        trial_clock = core.Clock()
        exploration_start_time = trial_clock.getTime()
        annotation_start_time = None
        
        while True:
            # Handle events
            for key in event.getKeys():
                if key == 'escape':
                    self.win.close()
                    core.quit()
                elif key == 'return':
                    if phase == "exploration":
                        phase = "annotation"
                        annotation_start_time = trial_clock.getTime()
                    elif phase == "annotation":
                        phase = "feedback"
                    elif phase == "feedback":
                        return self._finalize_trial(
                            trial_info, is_training, 
                            trial_clock.getTime() - exploration_start_time,
                            annotation_start_time and trial_clock.getTime() - annotation_start_time,
                            encountered_goal,
                            continuous_log
                        )
            
            # Update player position and angle based on key presses
            keys = event.getKeys(keyList=['up', 'down', 'left', 'right'])
            dt = 1/60.0  # Assuming 60Hz refresh rate
            
            if 'up' in keys:
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] + dx
                new_y = player_pos[1] + dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
            
            if 'down' in keys:
                rad = math.radians(player_angle)
                dx = MOVE_SPEED * dt * math.sin(rad)
                dy = MOVE_SPEED * dt * math.cos(rad)
                new_x = player_pos[0] - dx
                new_y = player_pos[1] - dy
                if math.hypot(new_x, new_y) <= ARENA_RADIUS:
                    player_pos[0] = new_x
                    player_pos[1] = new_y
            
            if 'left' in keys:
                player_angle -= ROTATE_SPEED * dt
            
            if 'right' in keys:
                player_angle += ROTATE_SPEED * dt
            
            # Log position
            if phase in ["exploration", "annotation"]:
                continuous_log.append({
                    "trial_info": trial_info,
                    "phase": phase,
                    "time": trial_clock.getTime(),
                    "x": player_pos[0],
                    "y": player_pos[1]
                })
            
            # Check for target collision
            for pos in current_target_positions:
                if self.distance(player_pos, pos) <= TARGET_RADIUS:
                    if encountered_goal is None:
                        encountered_goal = pos
                        self.target_sound.play()
                    current_target_positions = [pos]
                    break
            
            # Draw everything
            self._draw_trial(phase, player_pos, player_angle, current_target_positions, trial_info)
            
            # Flip the screen
            self.win.flip()
    
    def _draw_trial(self, phase, player_pos, player_angle, current_target_positions, trial_info):
        """Draw all elements for the current trial phase"""
        # Clear the screen
        self.win.fill(BACKGROUND_COLOR)
        
        # Draw arena
        self.arena.draw()
        
        if phase == "exploration":
            # Draw targets if in training mode
            if "training" in trial_info:
                for pos in current_target_positions:
                    screen_pos = self.to_screen_coords(pos)
                    self.target.pos = screen_pos
                    self.target.draw()
            
            # Draw avatar
            self.avatar.pos = self.to_screen_coords(player_pos)
            self.avatar.ori = player_angle
            self.avatar.draw()
            
        elif phase == "annotation":
            # Draw instruction
            self.instruction_text.text = "Navigate to the location of the target, and press Enter to finalize your decision"
            self.instruction_text.draw()
            
            # Draw annotation avatar in Khaki
            self.avatar.fillColor = CLOCK_COLOR
            self.avatar.pos = self.to_screen_coords(player_pos)
            self.avatar.ori = player_angle
            self.avatar.draw()
            self.avatar.fillColor = AVATAR_COLOR  # Reset color
            
        elif phase == "feedback":
            # Draw target and annotation position
            if current_target_positions:
                screen_pos = self.to_screen_coords(current_target_positions[0])
                self.target.pos = screen_pos
                self.target.draw()
            
            # Draw feedback avatar in Khaki
            self.avatar.fillColor = CLOCK_COLOR
            self.avatar.pos = self.to_screen_coords(player_pos)
            self.avatar.ori = player_angle
            self.avatar.draw()
            self.avatar.fillColor = AVATAR_COLOR  # Reset color
        
        # Draw trial counter
        if trial_info.startswith("training"):
            total_trials = TRAINING_SESSIONS
        elif trial_info.startswith("dark_training"):
            total_trials = DARK_TRAINING_TRIALS
        elif trial_info.startswith("test"):
            total_trials = TEST_TRIALS
        else:
            total_trials = "?"
        
        current_trial = trial_info.split()[1]
        self.counter_text.text = f"{current_trial}/{total_trials}"
        self.counter_text.draw()
    
    def _finalize_trial(self, trial_info, is_training, exploration_time, annotation_time, encountered_goal, continuous_log):
        """Finalize trial data and return logs"""
        error_distance = None
        if encountered_goal is not None:
            error_distance = self.distance(encountered_goal, [0, 0])  # Assuming annotation is at origin
        
        discrete_log = {
            "trial_info": trial_info,
            "trial_type": "training" if is_training else "test",
            "exploration_time": exploration_time,
            "annotation_time": annotation_time,
            "encountered_goal": json.dumps(encountered_goal) if encountered_goal else None,
            "error_distance": error_distance
        }
        
        return discrete_log, continuous_log
    
    def run_experiment(self):
        """Run the full experiment"""
        # Show instructions
        self._show_instructions()
        
        # Training block
        print("Starting Training Block")
        for session in range(1, TRAINING_SESSIONS + 1):
            trial_info = f"training {self.training_trial}"
            print(f"Training Session {session} ({trial_info})")
            discrete_log, continuous_log = self.run_trial(True, trial_info)
            self.all_discrete_logs.append(discrete_log)
            self.all_continuous_logs.extend(continuous_log)
            self.training_trial += 1
            self._save_logs()
        
        # Dark training block
        print("Starting Dark Training Block")
        for d in range(1, DARK_TRAINING_TRIALS + 1):
            trial_info = f"dark_training {self.dark_training_trial}"
            print(f"Dark Training Trial {d} ({trial_info})")
            discrete_log, continuous_log = self.run_trial(False, trial_info)
            self.all_discrete_logs.append(discrete_log)
            self.all_continuous_logs.extend(continuous_log)
            self.dark_training_trial += 1
            self._save_logs()
        
        # Test block
        print("Starting Test Block")
        for t in range(1, TEST_TRIALS + 1):
            trial_info = f"test {self.test_trial}"
            print(f"Test Trial {t} ({trial_info})")
            discrete_log, continuous_log = self.run_trial(False, trial_info)
            self.all_discrete_logs.append(discrete_log)
            self.all_continuous_logs.extend(continuous_log)
            self.test_trial += 1
            self._save_logs()
        
        # Show completion message
        self.instruction_text.text = "Experiment complete. Press Escape to exit."
        self.instruction_text.draw()
        self.win.flip()
        
        while 'escape' not in event.getKeys():
            core.wait(0.1)
    
    def _show_instructions(self):
        """Show experiment instructions"""
        instructions = [
            "Welcome to the Navigation Experiment!",
            "In this experiment, you will navigate through a virtual arena.",
            "Use the arrow keys to move:",
            "- Up/Down: Move forward/backward",
            "- Left/Right: Rotate",
            "Press Enter to continue...",
            "Press Escape at any time to quit."
        ]
        
        for instruction in instructions:
            self.instruction_text.text = instruction
            self.instruction_text.draw()
            self.win.flip()
            
            while 'return' not in event.getKeys():
                if 'escape' in event.getKeys():
                    self.win.close()
                    core.quit()
                core.wait(0.1)
    
    def _save_logs(self):
        """Save both discrete and continuous logs to CSV files"""
        # Save discrete logs
        with open(self.discrete_filename, 'w', newline='') as csvfile:
            fieldnames = [
                'trial_info', 'trial_type', 'exploration_time', 
                'annotation_time', 'encountered_goal', 'error_distance'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for log in self.all_discrete_logs:
                writer.writerow(log)
        
        # Save continuous logs
        with open(self.continuous_filename, 'w', newline='') as csvfile:
            fieldnames = ['trial_info', 'phase', 'time', 'x', 'y']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.all_continuous_logs:
                writer.writerow(row)

if __name__ == "__main__":
    experiment = NavigationExperiment()
    experiment.run_experiment()
    experiment.win.close()
    core.quit() 