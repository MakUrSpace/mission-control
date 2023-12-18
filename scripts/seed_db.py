"""Seed the database with some initial data."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import date
from app import db, create_app
from app.models import (
    Timeline,
    TimelineSection,
    TimelineSubsection,
    Project,
    Site,
    Contact,
    User,
    About,
    Service
)

# Create app context
# NOTE: This must be done before reading environment variables
app = create_app()

# Read environment variables
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "admin"

with app.app_context():
    # Clear existing data
    Project.query.delete()
    Site.query.delete()
    TimelineSubsection.query.delete()
    TimelineSection.query.delete()
    Timeline.query.delete()
    User.query.delete()
    Contact.query.delete()
    About.query.delete()
    Service.query.delete()

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
    contact = Contact(
        name="MakUrSpace LLC",
        email="hello@makurspace.com"
    )

    # Assign Contact to Site
    site.contact = contact
    # Assign Contact to User
    user.contact = contact

    # Add Octoprint service
    octoprint = Service(
        name="Octoprint",
        description="Octoprint is a web interface for managing 3D printers.",
        logo="img/services/octoprint.png",
    )
    site.services.append(octoprint)
    
    # Add Mainsail service
    mainsail = Service(
        name="Mainsail",
        description="Mainsail is a web interface for managing 3D printers.",
        logo="img/services/mainsail.png",
    )
    site.services.append(mainsail)

    # New Idea? service
    new_idea = Service(
        name="New Idea?",
        description="Have an idea for a new service? Let us know!",
        logo="img/services/idea.png",
    )
    site.services.append(new_idea)
    
    db.session.add(site)
    db.session.add(user)
    db.session.commit()  # Commit to get the ID for the site

    # Add new About section
    about = About(
        title="Welcome to Mission Control",
        description="Welcome to the demo for Mission Control.;This is a project intended to be shared and used to grow maker communities."
    )
    db.session.add(about)
    site.about = about

    # Add new Timeline
    timeline = Timeline(title="Timeline")
    db.session.add(timeline)
    db.session.commit()  # Commit to get the ID for the timeline

    mission_control = TimelineSection(title="Mission Control", timeline_id=timeline.id)
    core_functionality = TimelineSubsection(
        title="Core Functionality",
        start_date=date(2023, 9, 1),
        end_date=None,
        details="Customizable web app;Database-driven content;User authentication;Admin dashboard;REST API",
        timeline_section=mission_control,
    )
    first_expansion = TimelineSubsection(
        title="First Expansion",
        start_date=date(2023, 11, 1),
        end_date=None,
        details="Mainsail integration;Octoprint integration;3D printer management;3D printer monitoring;3D printer control",
        timeline_section=mission_control,
    )
    db.session.add(mission_control)

    # Add new Project
    nate_web_project = Project(
        title="Nate3D.com",
        description="The template for this project!",
    )

    # Assign timeline to site
    site.timeline = timeline
    
    # Assign projects to site
    site.projects.append(nate_web_project)

    db.session.commit()
