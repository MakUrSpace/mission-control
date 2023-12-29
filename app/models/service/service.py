"""Service component model."""
import importlib
import logging
from enum import Enum, auto
from flask import current_app as app
from app.extensions import db
from app.models.base_model import BaseModel

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Service type enum."""

    DOCKER = auto()
    INFO = auto()
    MARKETING = auto()
    WEB_PROXY = auto()


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
    is_disabled = db.Column(db.Boolean, default=False)
    is_daemon = db.Column(db.Boolean, default=False)
    type = db.Column(db.Enum(ServiceType), nullable=False, default=ServiceType.DOCKER)
    docker_container_id = db.Column(db.String(250), nullable=True)
    docker_image = db.Column(db.String(250), nullable=False)
    docker_image_tag = db.Column(db.String(250), nullable=False)
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
    def url(self) -> str:
        # Get the domain and port from the service environment variables
        domain = None
        port = None
        for domain_var in self.environment_vars:
            if domain_var.key.endswith("_DOMAIN"):
                domain = domain_var.value
            elif domain_var.key.endswith("_PORT"):
                port = domain_var.value

        if domain and port:
            return f"http://{domain}:{port}"
        if domain:
            return f"http://{domain}"
        return None

    @classmethod
    def handle_docker_event(cls, this_app, container, status) -> None:
        """Handle a Docker event."""
        with this_app.app_context():
            if status == "start":
                # Get the image and tag from the container
                image, tag = container.image.tags[0].split(":")
                service = cls.query.filter_by(
                    docker_image=image, docker_image_tag=tag
                ).first()

                if service:
                    service.update_state(True, container.id)

                    # Emit a socketio event to notify clients
                    socket_events = importlib.import_module("app.socket_events")
                    socket_events.emit_service_status(service, status)
            elif status in ("die", "destroy"):
                service = cls.query.filter_by(docker_container_id=container.id).first()
                if service:
                    service.update_state(False, None)

                    # Emit a socketio event to notify clients
                    socket_events = importlib.import_module("app.socket_events")
                    socket_events.emit_service_status(service, status)

    def start(self) -> bool:
        """Start the service."""
        if self.is_running:
            logger.info("Service %s is already running", self.id)
            return True, None

        container = app.docker_manager.start_service(self)
        if container:
            self.docker_container_id = container.id
            self.is_running = True
            db.session.commit()
            return True, None
        return False

    def stop(self) -> bool:
        """Stop the service."""
        if not self.is_running:
            print("Service is not running.")
            return False

        result = app.docker_manager.stop_service(self)
        if result:
            self.docker_container_id = None
            self.is_running = False
            db.session.commit()
            return True, None
        return False

    def restart(self) -> bool:
        """Restart the service."""
        container = app.docker_manager.restart_service(self)
        if container:
            self.docker_container_id = container.id
            self.is_running = True
            db.session.commit()
            return True, None
        return False

    def update_state(self, is_running, container_id) -> bool:
        """Update the service state."""
        try:
            self.is_running = is_running
            self.docker_container_id = None if not is_running else container_id
            db.session.commit()
        except Exception as e:
            logger.error("Error updating service state: %s", e)
            return False
        return True
