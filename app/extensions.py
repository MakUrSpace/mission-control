"""Extensions module. Each extension is initialized in the app factory located in __init__.py."""
import eventlet
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

eventlet.monkey_patch()

db = SQLAlchemy()
migrate = Migrate()
