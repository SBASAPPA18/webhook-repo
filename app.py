from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['webhook_database']
collection = db['github_events']

# Webhook endpoint to receive events
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    # Extract relevant data from the webhook payload
    action = data.get('action')
    author = data['sender']['login']
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
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

    # Store event data in MongoDB
    collection.insert_one(event_data)
    return jsonify({'status': 'success', 'data': event_data})


# Main route to display the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to retrieve the events from MongoDB
@app.route('/events', methods=['GET'])
def get_events():
    events = collection.find().sort('timestamp', -1)  # Get latest events
    event_list = []
    for event in events:
        event_list.append({
            'author': event['author'],
            'action': event['action'],
            'to_branch': event['to_branch'],
            'timestamp': event['timestamp']
        })
    return jsonify(event_list)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
