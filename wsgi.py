"""
WSGI entry point for production deployment.
Use with Gunicorn or other WSGI servers.

Example usage:
    gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
"""

import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app,db

# Create application instance
app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
