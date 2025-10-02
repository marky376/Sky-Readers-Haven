#!/usr/bin/env python3
"""Create demo user for Sky Readers Haven"""

from backend.app import create_app, db
from backend.models import User

# Create app instance
app = create_app()

def create_demo_user():
    with app.app_context():
        # Check if demo user exists
        demo = User.query.filter_by(username='demo').first()
        
        if demo:
            print("✓ Demo user already exists")
            print(f"  Username: {demo.username}")
            print(f"  Email: {demo.email}")
            
            # Update password to 'demo123'
            demo.set_password('demo123')
            db.session.commit()
            print("✓ Password updated to 'demo123'")
        else:
            # Create demo user
            demo = User(
                username='demo',
                email='demo@skyreadershaven.com'
            )
            demo.set_password('demo123')
            
            db.session.add(demo)
            db.session.commit()
            
            print("✓ Demo user created successfully!")
            print(f"  Username: demo")
            print(f"  Password: demo123")
            print(f"  Email: demo@skyreadershaven.com")

if __name__ == '__main__':
    create_demo_user()
