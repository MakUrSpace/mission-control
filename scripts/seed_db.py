"""Seed the database with some initial data."""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import db, create_app
from app.models import (
    Site,
    Contact,
    User,
    About,
    Service,
    EnvironmentVar,
)
from app.models.service import (
    ServiceType,
    DockerPort,
    DockerLabel,
    DockerVolume,
    # DockerDevice,
    DockerHealthcheck,
)

# Create app context
# NOTE: This must be done before reading environment variables
app = create_app()

# Read environment variables
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "admin"

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Add new User
    user = User(
        username="admin",
        password=ADMIN_PASSWORD,
        is_admin=True,
    )

    # Add new Site
    site = Site(
        title="Mission Control",
        subtitle="A MakUrSpace Project",
        url="https://mc.nate3d.com",
        logo="img/logo.png",
    )

    # Add new Contact
    contact = Contact(name="MakUrSpace LLC", email="hello@makurspace.com")

    # Assign Contact to Site
    site.contact = contact
    # Assign Contact to User
    user.contact = contact

    # Add Octoprint service
    # Optional device mapping for webcam
    # devices = [DockerDevice(host_path="/dev/video0", container_path="/dev/video0")]
    devices = []

    SERVICE_NAME = "Octoprint"
    octoprint = Service(
        name=SERVICE_NAME,
        type=ServiceType.DOCKER,
        is_daemon=False,
        description="Octoprint is a web interface for managing 3D printers.",
        logo="img/services/octoprint.png",
        documentation_url="https://docs.octoprint.org/en/master/",
        docker_image="octoprint/octoprint",
        docker_image_tag="latest",
        docker_ports=[
            DockerPort(
                container_port=5000, host_port=os.environ.get("OCTOPRINT_PORT", 5557)
            ),
        ],
        docker_volumes=[
            DockerVolume(
                container_path="/octoprint",
                host_path="data/octoprint",
            ),
        ],
        docker_labels=[
            DockerLabel(key="traefik.enable", value="true"),
            DockerLabel(key=f"traefik.http.routers.{SERVICE_NAME}.rule",
                        value=f"Host(`{os.environ.get('OCTOPRINT_DOMAIN', 'localhost')}`)"),
            DockerLabel(key=f"traefik.http.routers.{SERVICE_NAME}.entrypoints", value="web"),
        ],
        docker_devices=devices,
        docker_healthcheck=DockerHealthcheck(
            test="curl --fail http://localhost:80 || exit 1",
            interval=30,
            timeout=10,
            retries=3,
            start_period=15,
        ),
    )

    octoprint.environment_vars = [
        EnvironmentVar(
            key="OCTOPRINT_DOMAIN",
            value=os.environ.get("OCTOPRINT_DOMAIN", "localhost"),
        ),
        EnvironmentVar(
            key="OCTOPRINT_PORT",
            value=os.environ.get("OCTOPRINT_PORT", "5557"),
        ),
    ]
    site.services.append(octoprint)

    # Add Mainsail service
    SERVICE_NAME = "Mainsail"
    mainsail = Service(
        name=SERVICE_NAME,
        type=ServiceType.DOCKER,
        is_daemon=False,
        description="Mainsail is a web interface for managing 3D printers.",
        logo="img/services/mainsail.png",
        documentation_url="https://docs.mainsail.xyz/",
        docker_image="ghcr.io/mainsail-crew/mainsail",
        docker_image_tag="latest",
        docker_ports=[
            DockerPort(
                container_port=80, host_port=os.environ.get("MAINSAIL_PORT", 5556)
            ),
        ],
        docker_volumes=[
            DockerVolume(
                container_path="/usr/share/nginx/html/config.json",
                host_path="data/mainsail/config.json",
            ),
        ],
        docker_labels=[
            DockerLabel(key="traefik.enable", value="true"),
            DockerLabel(key=f"traefik.http.routers.{SERVICE_NAME}.rule",
                        value=f"Host(`{os.environ.get('MAINSAIL_DOMAIN', 'localhost')}`)"),
            DockerLabel(key=f"traefik.http.routers.{SERVICE_NAME}.entrypoints", value="web"),
        ],
        docker_healthcheck=DockerHealthcheck(
            test="curl --fail http://localhost:80 || exit 1",
            interval=30,
            timeout=10,
            retries=3,
            start_period=15,
        ),
    )
    mainsail.environment_vars = [
        EnvironmentVar(
            key="MAINSAIL_DOMAIN",
            value=os.environ.get("MAINSAIL_DOMAIN", "localhost"),
        ),
        EnvironmentVar(
            key="MAINSAIL_PORT",
            value=os.environ.get("MAINSAIL_PORT", "5556"),
        ),
    ]
    site.services.append(mainsail)

    # Add CNCJS service
    SERVICE_NAME = "CNCJS"
    cncjs = Service(
        name=SERVICE_NAME,
        type=ServiceType.DOCKER,
        is_daemon=False,
        description=(
            "A full-featured web interface for CNC controllers "
            "running Grbl, Marlin, Smoothieware, or TinyG."
        ),
        logo="img/services/cncjs.png",
        documentation_url="https://github.com/cncjs/cncjs/wiki/",
        docker_image="cncjs/cncjs",
        docker_image_tag="latest",
        docker_ports=[
            DockerPort(
                container_port=8000, host_port=os.environ.get("CNCJS_PORT", 5558)
            ),
        ],
        docker_volumes=[
            DockerVolume(
                container_path="/cncjs",
                host_path="data/cncjs",
            ),
        ],
        docker_labels=[
            DockerLabel(key="traefik.enable", value="true"),
            DockerLabel(key=f"traefik.http.routers.{SERVICE_NAME}.rule", 
                        value=f"Host(`{os.environ.get('CNCJS_DOMAIN', 'localhost')}`)"),
            DockerLabel(key=f"traefik.http.routers.{SERVICE_NAME}.entrypoints", value="web"),
        ],
        docker_healthcheck=DockerHealthcheck(
            test="curl --fail http://localhost:8000 || exit 1",
            interval=30,
            timeout=10,
            retries=3,
            start_period=15,
        ),
    )
    cncjs.environment_vars = [
        EnvironmentVar(
            key="CNCJS_DOMAIN",
            value=os.environ.get("CNCJS_DOMAIN", "localhost"),
        ),
        EnvironmentVar(
            key="CNCJS_PORT",
            value=os.environ.get("CNCJS_PORT", "5558"),
        ),
    ]
    site.services.append(cncjs)

    # Add Traefik daemon service
    SERVICE_NAME = "Traefik"
    traefik = Service(
        name=SERVICE_NAME,
        type=ServiceType.WEB_PROXY,
        is_daemon=True,
        description="Traefik is a modern HTTP reverse proxy and load balancer.",
        logo="img/services/traefik.png",
        documentation_url="https://doc.traefik.io/traefik/",
        docker_image="traefik",
        docker_image_tag="latest",
    )
    site.services.append(traefik)

    db.session.add(site)
    db.session.add(user)
    db.session.commit()  # Commit to get the ID for the site

    # Add new About section
    about = About(
        title="Welcome to Mission Control",
        description=(
            "Welcome to the demo for Mission Control.;"
            "This is a project intended to be shared and used to grow maker communities."
        ),
    )
    db.session.add(about)
    site.about = about

    # Commit all changes
    db.session.commit()
