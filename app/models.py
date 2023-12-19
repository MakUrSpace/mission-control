"""models.py"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()
migrate = Migrate()


class BaseModel(db.Model):
    """BaseModel to be inherited by all models.

    Args:
        db (Model): Model class from SQLAlchemy, acting as a base.
    """

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    last_modified = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class About(BaseModel):
    """About model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "about"
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)


class Site(BaseModel):
    """Site model to represent a website.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "site"
    title = db.Column(db.String(50), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    logo = db.Column(db.String(250), nullable=False)
    contact_id = db.Column(
        db.Integer, db.ForeignKey("contact.id", name="fk_contact_id"), nullable=False
    )
    contact = db.relationship(
        "Contact", backref="site", lazy=True, foreign_keys=[contact_id]
    )
    about_id = db.Column(
        db.Integer, db.ForeignKey("about.id", name="fk_about_id"), nullable=True
    )
    about = db.relationship("About", backref="site", lazy=True, uselist=False)
    services = db.relationship("Service", backref="site", lazy=True)


class Contact(BaseModel):
    """Contact model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "contact"
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    linkedin = db.Column(db.String(250), nullable=True)
    github = db.Column(db.String(250), nullable=True)
    facebook = db.Column(db.String(250), nullable=True)
    twitter = db.Column(db.String(250), nullable=True)
    instagram = db.Column(db.String(250), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", name="fk_user_id"), nullable=True
    )


class User(UserMixin, BaseModel):
    """User model.

    Args:
        UserMixin : Mixin for implementing Flask-Login user management.
        BaseModel : Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "user"
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    last_failed_login = db.Column(db.DateTime)
    failed_login_count = db.Column(db.Integer, default=0)
    contacts = db.relationship("Contact", backref="user", lazy=True)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id


class Service(BaseModel):
    """Service model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "service"
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    logo = db.Column(db.String(250), nullable=False)
    documentation_url = db.Column(db.String(250), nullable=True)
    is_running = db.Column(db.Boolean, default=False)
    docker_container_id = db.Column(db.String(250), nullable=True)
    docker_image = db.Column(db.String(250), nullable=False)
    docker_volumes = db.relationship("DockerVolume", backref="service", lazy=True)
    docker_ports = db.relationship("DockerPort", backref="service", lazy=True)
    docker_devices = db.relationship("DockerDevice", backref="service", lazy=True)
    docker_labels = db.relationship("DockerLabel", backref="service", lazy=True)
    docker_healthcheck = db.relationship(
        "DockerHealthcheck", backref="service", lazy=True, uselist=False
    )
    environment_vars = db.relationship("EnvironmentVar", backref="service", lazy=True)
    site_id = db.Column(
        db.Integer, db.ForeignKey("site.id", name="fk_site_id"), nullable=False
    )

    @property
    def url(self):
        # Get the domain and port from the service environment variables
        domain = None
        port = None
        for domain_var in self.environment_vars:
            if domain_var.key.endswith('_DOMAIN'):
                domain = domain_var.value
            elif domain_var.key.endswith('_PORT'):
                port = domain_var.value

        if domain and port:
            return f'http://{domain}:{port}'
        if domain:
            return f'http://{domain}'
        return None

    def get_container(self):
        if self.docker_container_id:
            return current_app.docker_manager.get_container(self.docker_container_id)

    def start(self):
        """Start the service."""
        if self.is_running:
            print("Service is already running.")
            return True

        container = current_app.docker_manager.start_service(self)
        if container:
            self.docker_container_id = container.id
            self.is_running = True
            db.session.commit()
            return True
        return False

    def stop(self):
        """Stop the service."""
        if not self.is_running:
            print("Service is not running.")
            return False

        if current_app.docker_manager.stop_service(self):
            self.docker_container_id = None
            self.is_running = False
            db.session.commit()
            return True
        return False

    def restart(self):
        """Restart the service."""
        container = current_app.docker_manager.restart_service(self)
        if container:
            self.docker_container_id = container.id
            self.is_running = True
            db.session.commit()
            return True
        return False

class EnvironmentVar(BaseModel):
    """EnvironmentVar model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "environment_var"
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )


class DockerVolume(BaseModel):
    """Volume model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_volume"
    container_path = db.Column(db.String(250), nullable=False)
    host_path = db.Column(db.String(250), nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )


class DockerPort(BaseModel):
    """Port model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_port"
    container_port = db.Column(db.Integer, nullable=False)
    host_port = db.Column(db.Integer, nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )


class DockerDevice(BaseModel):
    """Device model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_device"
    container_path = db.Column(db.String(250), nullable=False)
    host_path = db.Column(db.String(250), nullable=False)
    cgroup_permissions = db.Column(db.String(25), nullable=False, default="r")
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )


class DockerLabel(BaseModel):
    """Label model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_label"
    key = db.Column(db.String(60), nullable=False)
    value = db.Column(db.String(60), nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=False
    )


class DockerHealthcheck(BaseModel):
    """Healthcheck model.

    Args:
        BaseModel: Custom base model to provide additional standardized functionality.
    """

    __tablename__ = "docker_healthcheck"
    test = db.Column(db.String(250), nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    timeout = db.Column(db.Integer, nullable=False)
    retries = db.Column(db.Integer, nullable=False)
    start_period = db.Column(db.Integer, nullable=False)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", name="fk_service_id"), nullable=True
    )
