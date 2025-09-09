# Online Exploration Experiment

This is a web-based version of the Exploration Experiment, designed to run in a web browser. The experiment consists of three phases: training, dark training, and test phases, where participants navigate through a virtual environment to find targets.

## Requirements

- Python 3.7 or higher
- Flask
- Flask-SocketIO
- Modern web browser with JavaScript enabled

## Installation

1. Clone this repository or download the files
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Experiment

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Follow the on-screen instructions to complete the experiment.

## Experiment Structure

1. **Welcome Screen**: Introduction to the experiment
2. **Practice Game**: Collect 15 targets to familiarize with controls
3. **Training Phase**: 3 trials with visible targets
4. **Dark Training Phase**: 2 trials with hidden targets and visible border
5. **Test Phase**: 5 trials with hidden targets and no border

## Controls

- Up/Down Arrow Keys: Move forward/backward
- Left/Right Arrow Keys: Rotate left/right
- Enter Key: Progress through phases
- K Key: Show debug information (if enabled)

## Data Collection

The experiment automatically saves two types of data:
1. Discrete logs: Trial completion data
2. Continuous logs: Player movement data

Data is saved in the `results` directory with the format:
- `{initials}_discrete_log.csv`
- `{initials}_continuous_log.csv`

## Development

The experiment is built using:
- Backend: Flask with Flask-SocketIO
- Frontend: HTML5 Canvas with JavaScript
- Real-time communication: WebSocket

## License

[Your License Here]


