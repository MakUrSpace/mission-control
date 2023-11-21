"""__init__.py"""
import os
import sass
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_login import LoginManager
from .admin import admin
from .models import db, migrate, User
from .routes import bp as main_bp

# Initialize default environment variables
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_APP', 'app')

# Initialize dotenv settings
if os.environ.get('FLASK_ENV') == 'development':
    load_dotenv(find_dotenv())

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "main.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def format_datetime(value, date_format="%b %Y"):
    """HTML filter to format a datetime object.

    Args:
        value (str): Datetime in string format.
        format (str, optional): Defaults to '%b %Y'.

    Returns:
        datetime: Datetime object.
    """
    if value is None:
        return ""
    return value.strftime(date_format)


def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Compile SASS to CSS
    os.makedirs('app/static/css', exist_ok=True)
    css = sass.compile(filename='app/static/sass/custom.scss', output_style='compressed')
    with open('app/static/css/custom.css', 'w', encoding='utf8') as f:
        f.write(css)

    # Configure app settings
    app.config["DEBUG"] = os.environ.get("FLASK_ENV") == "development"
    app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV")
    app.config["FLASK_APP"] = os.environ.get("FLASK_APP")
    app.config["MAINSAIL_URL"] = os.environ.get("MAINSAIL_URL")
    app.config["OCTOPRINT_URL"] = os.environ.get("OCTOPRINT_URL")
    
    # Configure development settings
    if app.config["DEBUG"]:
        app.config["TEMPLATES_AUTO_RELOAD"] = True
        app.config["SQLALCHEMY_ECHO"] = False

    # Configure CSRF protection
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "SUPERSECRETKEY")

    # Register app blueprints (routes)
    app.register_blueprint(main_bp)

    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    # Register Jinja2 filters
    app.jinja_env.filters["datetime"] = format_datetime

    # Initialize Flask-Login
    login_manager.init_app(app)
    admin.init_app(app)

    return app
