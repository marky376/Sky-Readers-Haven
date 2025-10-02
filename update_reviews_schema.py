#!/usr/bin/env python3
"""
Update reviews table schema and create review_votes table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import create_app, db
from sqlalchemy import inspect, text

app = create_app('development')

with app.app_context():
    inspector = inspect(db.engine)
    
    print("Checking reviews table schema...")
    
    # Check if title column exists
    reviews_columns = [col['name'] for col in inspector.get_columns('reviews')]
    
    if 'title' not in reviews_columns:
        print("Adding new columns to reviews table...")
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE reviews ADD COLUMN title VARCHAR(200)"))
            conn.execute(text("ALTER TABLE reviews ADD COLUMN verified_purchase BOOLEAN DEFAULT 0 NOT NULL"))
            conn.execute(text("ALTER TABLE reviews ADD COLUMN helpful_count INTEGER DEFAULT 0 NOT NULL"))
            conn.execute(text("ALTER TABLE reviews ADD COLUMN unhelpful_count INTEGER DEFAULT 0 NOT NULL"))
            conn.execute(text("ALTER TABLE reviews ADD COLUMN status VARCHAR(20) DEFAULT 'pending' NOT NULL"))
            conn.execute(text("ALTER TABLE reviews ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"))
            conn.commit()
        print("✓ Reviews table updated successfully")
    else:
        print("✓ Reviews table already has new columns")
    
    # Check if review_votes table exists
    tables = inspector.get_table_names()
    
    if 'review_votes' not in tables:
        print("Creating review_votes table...")
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE review_votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    review_id INTEGER NOT NULL,
                    is_helpful BOOLEAN NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE,
                    UNIQUE (user_id, review_id)
                )
            """))
            conn.commit()
        print("✓ review_votes table created successfully")
    else:
        print("✓ review_votes table already exists")
    
    # Mark existing reviews as approved
    from backend.models import Review
    pending_reviews = Review.query.filter_by(status='pending').all()
    if pending_reviews:
        print(f"\nMarking {len(pending_reviews)} existing reviews as approved...")
        for review in pending_reviews:
            review.status = 'approved'
        db.session.commit()
        print("✓ Existing reviews approved")
    
    print("\n✅ Database schema update complete!")
    print("\nReview system ready with:")
    print("  - Review titles")
    print("  - Verified purchase badges")
    print("  - Helpful/unhelpful voting")
    print("  - Review moderation (pending/approved/rejected)")
    print("  - Updated timestamps")
