#!/usr/bin/env python3
"""
Create wishlist table in database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import create_app, db
from sqlalchemy import inspect, text

app = create_app('development')

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("Checking wishlist table...")
    
    if 'wishlists' not in tables:
        print("Creating wishlists table...")
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE wishlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    notes VARCHAR(500),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                    UNIQUE (user_id, book_id)
                )
            """))
            conn.commit()
        print("✓ wishlists table created successfully")
    else:
        print("✓ wishlists table already exists")
    
    print("\n✅ Database ready!")
    print("Wishlist system features:")
    print("  - Add/remove books from wishlist")
    print("  - Optional personal notes per book")
    print("  - Unique constraint (one book per user)")
    print("  - Cascade delete on user/book deletion")
