"""
Update database to add is_admin field to users table
"""
from backend.app import create_app, db
from backend.models import User
from sqlalchemy import inspect

def update_database():
    app = create_app('development')
    
    with app.app_context():
        # Check if is_admin column exists
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column to users table...")
            # Add the column using raw SQL
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL'))
                conn.commit()
            print("✓ Column added successfully!")
        else:
            print("✓ is_admin column already exists")
        
        # Check if we have any users
        user_count = User.query.count()
        print(f"\nTotal users in database: {user_count}")
        
        if user_count > 0:
            # Make first user an admin if no admins exist
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count == 0:
                first_user = User.query.first()
                first_user.is_admin = True
                db.session.commit()
                print(f"✓ Made '{first_user.username}' an admin")
            else:
                print(f"✓ Already have {admin_count} admin(s)")
        
        print("\n✅ Database update complete!")
        print("\nAdmin users:")
        admins = User.query.filter_by(is_admin=True).all()
        for admin in admins:
            print(f"  - {admin.username} ({admin.email})")

if __name__ == '__main__':
    update_database()
