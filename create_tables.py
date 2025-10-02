#!/usr/bin/env python3
"""Script to create missing database tables"""
from backend.app import create_app, db

app = create_app()
with app.app_context():
    print("Creating all missing tables...")
    db.create_all()
    print("✓ Database tables created successfully!")
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\nCurrent tables in database ({len(tables)}):")
    for table in sorted(tables):
        print(f"  ✓ {table}")
