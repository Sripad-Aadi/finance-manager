"""Initialize the database with tables"""
from app import create_app, db

app = create_app()

with app.app_context():
    # Create all tables based on the models
    db.create_all()
    print("Database tables created successfully!")
