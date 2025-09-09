# Navigation Experiment

A spatial navigation and memory experiment implemented in Python using Pygame.

## Overview

This experiment tests participants' ability to navigate in a virtual arena and remember target locations under different visibility conditions:
- Training: Full visibility of arena and targets
- Dark Training: Limited visibility (only see borders)
- Test: Minimal visibility

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
improved_navigation/
├── src/
│   ├── __init__.py
│   ├── config.py        # Configuration settings
│   ├── models.py        # Data models
│   ├── game_objects.py  # Game entities
│   ├── ui.py           # Rendering
│   ├── logging.py      # Data collection
│   ├── experiment.py   # Experiment logic
│   └── main.py         # Entry point
├── data/               # Experiment data
├── sounds/             # Sound effects
├── instructions/       # Instruction images
├── tests/             # Test files
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## Usage

1. Ensure all required sound files are in the `sounds/` directory:
   - `target.wav`
   - `beep.wav`

2. Ensure all instruction images (1.png through 6.png) are in the `instructions/` directory

3. Run the experiment:
```bash
python -m improved_navigation.src.main
```

4. Enter your initials when prompted

5. Follow the on-screen instructions

## Data Collection

The experiment collects two types of data:
1. Discrete logs (per trial):
   - Trial information
   - Exploration/annotation times
   - Target encounters
   - Error distances

2. Continuous logs:
   - Moment-to-moment positions
   - Phase information
   - Timestamps

Data is saved in CSV format in the `data/` directory.

## Controls

- Arrow keys:
  - Up/Down: Move forward/backward
  - Left/Right: Rotate
- Enter: Progress through phases
- Escape: Exit experiment
- K: Show debug information (during training) 