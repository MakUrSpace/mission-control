"""Service component model."""
import time
import logging
from flask import current_app as app
from app.extensions import db
from app.models.base_model import BaseModel

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
            container, error = app.docker_manager.get_container(self.docker_container_id)
            if container:
                return container
            logging.error("Error getting container %s: %s", self.docker_container_id, error)

            # If the container is not found, update the database
            self.docker_container_id = None
            self.is_running = False
            db.session.commit()
        return None

    def check_status(self):
        container = self.get_container()
        if container and container.status == 'running':
            if not self.is_running:
                self.is_running = True
        else:
            if self.is_running:
                self.is_running = False

    @classmethod
    def schedule_service_checks(cls, app):
        with app.app_context():
            while True:
                try:
                    for service in cls.query.all():
                        db.session.refresh(service)
                        service.check_status()
                    db.session.commit()
                except Exception as e:
                    logging.error("Error checking service status: %s", e)
                    db.session.rollback()
                time.sleep(5)

    def start(self):
        """Start the service."""
        if self.is_running:
            print("Service is already running.")
            return True

        container, error = app.docker_manager.start_service(self)
        if container:
            self.docker_container_id = container.id
            self.is_running = True
            db.session.commit()
            return True, None
        return False, error

    def stop(self):
        """Stop the service."""
        if not self.is_running:
            print("Service is not running.")
            return False

        result, error = app.docker_manager.stop_service(self)
        if result:
            self.docker_container_id = None
            self.is_running = False
            db.session.commit()
            return True, None
        return False, error

    def restart(self):
        """Restart the service."""
        container, error = app.docker_manager.restart_service(self)
        if container:
            self.docker_container_id = container.id
            self.is_running = True
            db.session.commit()
            return True, None
        return False, error
