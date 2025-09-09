from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create data directory if it doesn't exist
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/api/save_trial', methods=['POST'])
def save_trial():
    try:
        data = request.json
        participant_id = data.get('participant_id')
        
        if not participant_id:
            return jsonify({'error': 'Missing participant_id'}), 400
            
        # Create a filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{DATA_DIR}/{participant_id}_{timestamp}.json"
        
        # Save the data
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 