#!/usr/bin/env python
"""
Run script for Sky Readers Haven application
"""
from backend.app import create_app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
