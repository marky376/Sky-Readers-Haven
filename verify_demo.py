#!/usr/bin/env python3
from backend.app import create_app, db
from backend.models import User

app = create_app()

with app.app_context():
    demo = User.query.filter_by(username='demo').first()
    print(f'Username: {demo.username}')
    print(f'Email: {demo.email}')
    print(f'Password check for "demo123": {demo.check_password("demo123")}')
