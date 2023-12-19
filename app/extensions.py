"""Extensions module. Each extension is initialized in the app factory located in __init__.py."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
