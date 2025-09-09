import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from .models import TrialData, ContinuousData, Vector2D
from .config import config

class DataLogger:
    def __init__(self, player_initials: str):
        self.player_initials = player_initials
        self.discrete_logs: List[TrialData] = []
        self.continuous_logs: List[ContinuousData] = []
        
        # Ensure data directory exists
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Set up file paths
        self.discrete_file = config.DATA_DIR / f"{player_initials}_discrete_log.csv"
        self.continuous_file = config.DATA_DIR / f"{player_initials}_continuous_log.csv"

    def add_discrete_log(self, trial_data: TrialData) -> None:
        """Add a discrete trial data point and save to file."""
        self.discrete_logs.append(trial_data)
        self._save_discrete_logs()

    def add_continuous_log(self, continuous_data: ContinuousData) -> None:
        """Add a continuous data point and save to file."""
        self.continuous_logs.append(continuous_data)
        self._save_continuous_logs()

    def _save_discrete_logs(self) -> None:
        """Save discrete logs to CSV file."""
        with open(self.discrete_file, "w", newline="") as csvfile:
            fieldnames = [
                "trial_info",
                "trial_type",
                "exploration_time",
                "annotation_time",
                "encountered_goal",
                "annotation",
                "error_distance"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for log in self.discrete_logs:
                row = {
                    "trial_info": log.trial_info,
                    "trial_type": log.trial_type,
                    "exploration_time": log.exploration_time,
                    "annotation_time": log.annotation_time,
                    "encountered_goal": json.dumps([
                        log.encountered_goal.x,
                        log.encountered_goal.y
                    ]) if log.encountered_goal else None,
                    "annotation": json.dumps([
                        log.annotation.x,
                        log.annotation.y
                    ]),
                    "error_distance": log.error_distance
                }
                writer.writerow(row)

    def _save_continuous_logs(self) -> None:
        """Save continuous logs to CSV file."""
        with open(self.continuous_file, "w", newline="") as csvfile:
            fieldnames = ["trial_info", "phase", "time", "x", "y"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for log in self.continuous_logs:
                row = {
                    "trial_info": log.trial_info,
                    "phase": log.phase,
                    "time": log.time,
                    "x": log.position.x,
                    "y": log.position.y
                }
                writer.writerow(row)

    def load_logs(self) -> None:
        """Load existing logs from files if they exist."""
        if self.discrete_file.exists():
            self.discrete_logs = []
            with open(self.discrete_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    encountered_goal = json.loads(row["encountered_goal"]) if row["encountered_goal"] else None
                    annotation = json.loads(row["annotation"])
                    
                    trial_data = TrialData(
                        trial_info=row["trial_info"],
                        trial_type=row["trial_type"],
                        exploration_time=float(row["exploration_time"]),
                        annotation_time=float(row["annotation_time"]),
                        encountered_goal=Vector2D(encountered_goal[0], encountered_goal[1]) if encountered_goal else None,
                        annotation=Vector2D(annotation[0], annotation[1]),
                        error_distance=float(row["error_distance"]) if row["error_distance"] else None
                    )
                    self.discrete_logs.append(trial_data)
                    
        if self.continuous_file.exists():
            self.continuous_logs = []
            with open(self.continuous_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    continuous_data = ContinuousData(
                        trial_info=row["trial_info"],
                        phase=row["phase"],
                        time=float(row["time"]),
                        position=Vector2D(float(row["x"]), float(row["y"]))
                    )
                    self.continuous_logs.append(continuous_data) 