"""__init__.py"""
import importlib
import os
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_login import LoginManager
from .admin import admin
from .models import db, migrate, User
from .routes import bp as main_bp

# Initialize default environment variables
os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("FLASK_APP", "app")

# Initialize dotenv settings
if os.environ.get("FLASK_ENV") == "development":
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

    # Configure app settings
    app.config["DEBUG"] = os.environ.get("FLASK_ENV") == "development"
    app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV")
    app.config["FLASK_APP"] = os.environ.get("FLASK_APP")

    if app.config["DEBUG"]:
        # Configure logging
        logging = importlib.import_module("logging")
        logging.basicConfig(level=logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)

    try:
        print("Registering SASS bundle...")
        app.config["LIBSASS_AVAILABLE"] = importlib.util.find_spec("sass") is not None
        print(f"Is Libsass available? {app.config['LIBSASS_AVAILABLE']}")
        flask_assets = importlib.import_module("flask_assets")

        environment = flask_assets.Environment
        bundle = flask_assets.Bundle

        assets = environment(app)
        assets.debug = app.config["DEBUG"]

        scss_bundle = bundle(
            "sass/custom.scss",
            filters="libsass",
            output="css/custom.css",
        )
        assets.register("scss_all", scss_bundle)
        assets.init_app(app)
        print("Registered SASS bundle.")
    except ImportError:
        print("WARNING: libsass not installed. Skipping SASS compilation.")
                
    # Fetching individual components from environment variables
    if "SQLALCHEMY_DATABASE_URI" not in os.environ:
        db_user = os.environ.get("POSTGRES_USER", "pgadm")
        db_password = os.environ.get("POSTGRES_PASSWORD", "lolnope")
        db_name = os.environ.get("POSTGRES_DB", "webdb")
        db_host = os.environ.get("DATABASE_DOMAIN", "db")
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
            "SQLALCHEMY_DATABASE_URI"
        )

    # Configure domains with ports if the ports are provided
    mainsail_domain = os.environ.get("MAINSAIL_DOMAIN")
    mainsail_port = os.environ.get("MAINSAIL_PORT")
    mainsail_url = (
        f"http://{mainsail_domain}"
        if not mainsail_port
        else f"http://{mainsail_domain}:{mainsail_port}"
    )
    app.config["MAINSAIL_URL"] = mainsail_url

    octoprint_domain = os.environ.get("OCTOPRINT_DOMAIN")
    octoprint_port = os.environ.get("OCTOPRINT_PORT")
    octoprint_url = (
        f"http://{octoprint_domain}"
        if not octoprint_port
        else f"http://{octoprint_domain}:{octoprint_port}"
    )
    app.config["OCTOPRINT_URL"] = octoprint_url

    # Configure development settings
    if app.config["DEBUG"]:
        app.config["TEMPLATES_AUTO_RELOAD"] = True
        app.config["SQLALCHEMY_ECHO"] = False

    # Configure CSRF protection
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "SUPERSECRETKEY")

    # Register app blueprints (routes)
    app.register_blueprint(main_bp)

    # Configure database
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
