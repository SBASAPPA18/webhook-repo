# webhook-repo

# GitHub Webhook Integration Project

## Overview

This project integrates GitHub actions with a Flask web application and MongoDB. It uses GitHub webhooks to capture events such as pushes, pull requests, and merges, stores these events in MongoDB, and displays them in a web interface.

## Repositories

- **`action-repo`**: GitHub repository to trigger GitHub actions and webhooks.
- **`webhook-repo`**: Repository containing the Flask app to handle webhooks and interact with MongoDB.

## Prerequisites

- Python 3.7 or higher
- MongoDB
- Ngrok
- Git

## Setup Instructions

### 1. Clone Repositories

git clone https://github.com/your-username/webhook-repo.git
cd webhook-repo

### 2. Create Virtual Environment

python -m venv venv

### 3. Activate Virtual Environment
venv\Scripts\activate

### Install Dependency
---
pip install Flask pymongo waitress


### Aplication Code
---
from flask import Flask, jsonify
from pymongo import MongoClient, DESCENDING

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']

@app.route('/events', methods=['GET'])
def get_events():
    events = db.github_events.find().sort('timestamp', DESCENDING)
    return jsonify([event for event in events])

if __name__ == '__main__':
    app.run(debug=True)

## Running Application
---
#### Start Application with Waitress

waitress-serve --listen=127.0.0.1:5000 app:app

## Access The Application
---
[link](http://127.0.0.1:5000/events
)

# Testing
[link](curl http://127.0.0.1:5000/events
)

# Setup MangoDB

Ensure that MongoDB is installed and running on your local machine. The default connection string used in the application is (mongodb://localhost:27017/.) Modify this string in app.py if your MongoDB instance is running elsewhere.


