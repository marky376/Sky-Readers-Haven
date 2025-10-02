#!/usr/bin/env python3
from backend.app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Current tables in database:")
    for table in tables:
        print(f"  - {table}")
    
    print("\nModels defined in code:")
    for table in db.Model.metadata.tables:
        print(f"  - {table}")
