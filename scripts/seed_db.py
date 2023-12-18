"""Seed the database with some initial data."""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import db, create_app
from app.models import (
    DockerHealthcheck,
    DockerPort,
    DockerVolume,
    Site,
    Contact,
    User,
    About,
    Service,
    EnvironmentVar,
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
    octoprint = Service(
        name="Octoprint",
        description="Octoprint is a web interface for managing 3D printers.",
        logo="img/services/octoprint.png",
        documentation_url="https://docs.octoprint.org/en/master/",
        docker_image="octoprint/octoprint:latest",
        docker_ports=[
            DockerPort(
                container_port=5000, host_port=os.environ.get("OCTOPRINT_PORT", 5557)
            ),
        ],
        docker_volumes=[
            DockerVolume(volume_mapping="octoprint_volume:/octoprint"),
        ],
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
            value="localhost",
        ),
        EnvironmentVar(
            key="OCTOPRINT_PORT",
            value="5557",
        ),
    ]
    site.services.append(octoprint)

    # Add Mainsail service
    mainsail = Service(
        name="Mainsail",
        description="Mainsail is a web interface for managing 3D printers.",
        logo="img/services/mainsail.png",
        documentation_url="https://docs.mainsail.xyz/",
        docker_image="ghcr.io/mainsail-crew/mainsail:latest",
        docker_ports=[
            DockerPort(
                container_port=80, host_port=os.environ.get("MAINSAIL_PORT", 5556)
            ),
        ],
        docker_volumes=[
            DockerVolume(
                volume_mapping="data/mainsail/config.json:/usr/share/nginx/html/config.json"
            ),
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
            value="localhost",
        ),
        EnvironmentVar(
            key="MAINSAIL_PORT",
            value="5556",
        ),
    ]
    site.services.append(mainsail)

    # Add CNCJS service
    cncjs = Service(
        name="CNCJS",
        description=(
            "A full-featured web interface for CNC controllers "
            "running Grbl, Marlin, Smoothieware, or TinyG."
        ),
        logo="img/services/cncjs.png",
        documentation_url="https://github.com/cncjs/cncjs/wiki/",
        docker_image="cncjs/cncjs:latest",
        docker_ports=[
            DockerPort(
                container_port=8000, host_port=os.environ.get("CNCJS_PORT", 5555)
            ),
        ],
        docker_volumes=[
            DockerVolume(volume_mapping="cncjs_volume:/cncjs"),
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
            value="localhost",
        ),
        EnvironmentVar(
            key="CNCJS_PORT",
            value="5555",
        ),
    ]
    site.services.append(cncjs)

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
