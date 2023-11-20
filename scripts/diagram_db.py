"""diagram_db.py - Generate an ER diagram from the SQLAlchemy db instance."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from eralchemy2 import render_er
from app import db, create_app

# Generate intermediate markdown file
app = create_app()
with app.app_context():
    render_er(db.metadata, 'db_model.pdf')
