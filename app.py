#!/usr/bin/env python3
"""
Main application entry point for Sky Readers Haven
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from backend.app import create_app, db

# Determine configuration
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)