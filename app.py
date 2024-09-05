from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient, DESCENDING
from datetime import datetime
import logging
import pymongo

app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['webhook_database']
collection = db['github_events']

result = collection.insert_one({"test": "data"})
print(result.inserted_id)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
# Webhook endpoint to receive events
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    logging.debug(f"Received payload: {data}")
    
    # Extract relevant data from the webhook payload
    action = data.get('action')
    author = data['sender']['login']
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    event_data = None  # Initialize event_data

    if action == 'push':
        to_branch = data['ref'].split('/')[-1]
        request_id = data['head_commit']['id']
        event_data = {
            'request_id': request_id,
            'author': author,
            'action': 'PUSH',
            'from_branch': None,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    elif action == 'pull_request':
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        request_id = data['pull_request']['id']
        event_data = {
            'request_id': request_id,
            'author': author,
            'action': 'PULL_REQUEST',
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    elif action == 'merge':
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        request_id = data['pull_request']['id']
        event_data = {
            'request_id': request_id,
            'author': author,
            'action': 'MERGE',
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    else:
        return jsonify({'status': 'failure', 'message': f'Unsupported action: {action}'}), 400

    # Store event data in MongoDB if event_data is populated
    if event_data:
        collection.insert_one(event_data)
        return jsonify({'status': 'success', 'data': event_data})
    else:
        return jsonify({'status': 'failure', 'message': 'No valid event data'}), 400

# Main route to display the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to retrieve the events from MongoDB
@app.route('/events', methods=['GET'])
def get_events():
    events = db.github_events.find().sort('timestamp', DESCENDING)

    event_list = []
    for event in events:
        # Safely access fields, and provide a default value if the field is missing
        event_data = {
            'request_id': event.get('request_id', 'N/A'),
            'author': event.get('author', 'Unknown Author'),
            'action': event.get('action', 'No Action'),
            'to_branch': event.get('to_branch', 'Unknown Branch'),
            'timestamp': event.get('timestamp', 'Unknown Timestamp')
        }
        event_list.append(event_data)
    return jsonify(event_list)


if __name__ == '__main__':
    app.run(debug=True)
