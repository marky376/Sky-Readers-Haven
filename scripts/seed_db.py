#!/usr/bin/env python3
"""Seed the database with sample data for Sky Readers Haven."""
import os
import datetime
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app, db
from backend.models import Author, Category, Book, User

app = create_app(os.getenv('FLASK_CONFIG', 'development'))

def seed():
    with app.app_context():
        db.create_all()

        # create a demo user
        if not User.query.filter_by(username='demo').first():
            demo = User(username='demo', email='demo@example.com')
            demo.set_password('password')
            db.session.add(demo)

        # categories
        categories = ['Fiction','Science Fiction','Thriller','Horror','Biography','Self Help']
        cat_objs = {}
        for c in categories:
            obj = Category.query.filter_by(name=c).first()
            if not obj:
                obj = Category(name=c)
                db.session.add(obj)
            cat_objs[c] = obj

        # authors and books
        a1 = Author.query.filter_by(name='Paulo Coelho').first() or Author(name='Paulo Coelho')
        a2 = Author.query.filter_by(name='F. Scott Fitzgerald').first() or Author(name='F. Scott Fitzgerald')
        db.session.add_all([a1,a2])

        b1 = Book(title='The Alchemist', description='A fable about following your dream.', published_date=datetime.date(1988,1,1), author=a1, category=cat_objs['Fiction'])
        b2 = Book(title='The Great Gatsby', description='A classic novel of the Jazz Age.', published_date=datetime.date(1925,4,10), author=a2, category=cat_objs['Fiction'])
        db.session.add_all([b1,b2])

        db.session.commit()
        print('Database seeded successfully')

if __name__ == '__main__':
    seed()
