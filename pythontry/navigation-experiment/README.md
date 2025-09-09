# Navigation Experiment

This is a web-based navigation experiment converted from a Pygame implementation. It's designed to be run on the Prolific platform.

## Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python app.py
```

3. Serve the frontend:
   - You can use any static file server
   - For development, you can use Python's built-in server:
```bash
cd frontend
python -m http.server 8000
```

## Running the Experiment

1. Access the experiment through your web browser at `http://localhost:8000`
2. Enter a Prolific ID to start
3. Follow the on-screen instructions

## Data Collection

- Data is saved in the `backend/data` directory
- Each trial's data is saved as a JSON file with the format: `{participant_id}_{timestamp}.json`

## Deployment

For production deployment:

1. Set up a web server (e.g., Nginx) to serve the frontend
2. Deploy the Flask backend on a WSGI server (e.g., Gunicorn)
3. Configure the frontend to point to the production backend URL
4. Set up proper SSL certificates
5. Update the Prolific study URL to point to your production server

## Development

- Frontend code is in the `frontend` directory
- Backend code is in the `backend` directory
- The experiment logic is in `frontend/js/game.js`
- UI flow is handled in `frontend/js/main.js` 