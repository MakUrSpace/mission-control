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
    About
)

app = create_app()
with app.app_context():
    # Clear existing data
    Project.query.delete()
    Site.query.delete()
    TimelineSubsection.query.delete()
    TimelineSection.query.delete()
    Timeline.query.delete()
    User.query.delete()
    Contact.query.delete()

    # Add new User
    user = User(
        username="admin",
        password="admin",
        is_admin=True,
    )

    # Add new Site
    site = Site(
        title="Nate Brandeburg",
        subtitle="Senior Software Engineering Lead",
        url="https://wip.nate3d.com",
        logo="static/img/logo.png",
    )

    # Add new Contact
    contact = Contact(
        name="Nate Brandeburg",
        email="me@nate3d.com",
        linkedin="https://www.linkedin.com/in/nate-brandeburg/",
        github="https://github.com/nate3D"
    )

    # Assign Contact to Site
    site.contact = contact
    # Assign Contact to User
    user.contact = contact
    db.session.add(site)
    db.session.add(user)
    db.session.commit()  # Commit to get the ID for the site

    # Add new About section
    about = About(
        title="Hello There!",
        description="I'm Nate Brandeburg, a Senior Software Engineering Lead at <a href=\"https://hello.whisker.com/\" target=\"_blank\" rel=\"noopener noreferrer\">Whisker</a>!;My passion is designing global software systems and my strength is empowering a team of incredible engineers to realize their full potential!;My current focus is on building a team of engineers to create a world-class cloud platform to unlock the value of our Litter-Robot and pet data."
    )
    db.session.add(about)
    site.about = about

    # Add new Timeline
    timeline = Timeline(title="Timeline")
    db.session.add(timeline)
    db.session.commit()  # Commit to get the ID for the timeline

    whisker = TimelineSection(title="Whisker", timeline_id=timeline.id)
    senior_software_engineering_lead = TimelineSubsection(
        title="Senior Software Engineering Lead",
        start_date=date(2023, 5, 1),
        end_date=None,
        details="Detail about the position.",
        timeline_section=whisker,
    )
    software_systems_engineer = TimelineSubsection(
        title="Software Systems Engineer",
        start_date=date(2022, 9, 1),
        end_date=date(2023, 5, 1),
        details="Built containerized software engineering toolkit using VSCode, Docker, AWS-CLI, and Python.;Over-the-air firmware update process refinement.;Cross-team coordination between firmware and cloud to successfully deploy OTA enhancements.;Guided team to begin following microservice design principles.",
        timeline_section=whisker,
    )
    db.session.add(whisker)

    the_seam = TimelineSection(title="The Seam", timeline_id=timeline.id)
    senior_solutions_architect = TimelineSubsection(
        title="Senior Solutions Architect",
        start_date=date(2021, 5, 1),
        end_date=date(2022, 9, 1),
        details="Architected a reusable DotNet 6 solution using onion architecture design patterns with robust separation of concerns.;Lead the effort to implement GraphQL into .NET Core web server applications.;Mentored junior developers in API, database, and architecture best practices.;Identified issues and optimized our SQL Server instances to fully utilize available system resources.;Implemented a change management process to move the team from Waterfall to Agile development methodologies.",
        timeline_section=the_seam,
    )
    db.session.add(the_seam)

    buckman_laboratories = TimelineSection(
        title="Buckman Laboratories", timeline_id=timeline.id
    )
    digital_innovation_engineer = TimelineSubsection(
        title="Digital Innovation Engineer",
        start_date=date(2019, 8, 1),
        end_date=date(2021, 5, 1),
        details="Rapidly designed and developed proof-of-concept available systems and applications to get new product ideas to market quickly on a global scale.;Utilized new technologies such as LoRaWAN for wireless communication of data at customer sites.;Implemented industry standard Industrial Internet-of-Things (IIoT) concepts in Microsoft Azure.;Took advantage of Microsoft's PowerApps platform to decrease turnaround time on delivering proof-of-concept mobile and web applications.;Coupled our cloud solutions with vendor systems via RESTful service APIs.;Worked closely with vendors to form partnerships and build a global supply chain.;Guided and trained interns to bolster their skills and improve their contributions to team efforts.",
        timeline_section=buckman_laboratories,
    )
    db.session.add(buckman_laboratories)

    ubiquisoft_technologies = TimelineSection(
        title="Ubiquisoft Technologies", timeline_id=timeline.id
    )
    software_development_advisor = TimelineSubsection(
        title="Software Development Advisor",
        start_date=date(2019, 4, 1),
        end_date=date(2019, 8, 1),
        details="Oversaw all development projects and met daily with all developers (Scrum Stand-up).;Advised developers on best-practices and technological tool use, especially using the IntelliJ family of products.;Investigated new technologies as to how they might streamline and augment our development workflow, leading to a migration to microservice architecture.;Guided junior developers to help them build skills and grow their development abilities.;Improved development throughput through the implementation of Scrum methodologies and modern development practices.;Offered recommendations to Ubiquisoft administration on potential new-hires based on their technical interview results.",
        timeline_section=ubiquisoft_technologies,
    )
    software_development_lead = TimelineSubsection(
        title="Software Development Lead & Certified Scrum Master",
        start_date=date(2018, 1, 1),
        end_date=date(2019, 4, 1),
        details="Led a team of junior developers, making a focused effort to leverage their unique strengths and help improve their areas for growth.;Led the final development stages for the Crew Planning Management System used by FedEx Air Operations.;Produced initial system designs and oversaw further refinement in addition to overseeing and contributing to implementation.;Obtained Certified Scrum Master from the Scrum Alliance - Utilized this training to begin shifting Ubiquisoft's development methodology from waterfall to Agile(Scrum).;Took part in an official Scrum Alliance training course and achieve a Certified Scrum Master designation.",
        timeline_section=ubiquisoft_technologies,
    )
    java_software_developer = TimelineSubsection(
        title="Java Software Developer",
        start_date=date(2016, 6, 1),
        end_date=date(2018, 1, 1),
        details="Built Java 8 enterprise applications on top of Oracle's Weblogic 12 application server.;Leveraged the Java Message Service to scale application interfaces with FedEx internal systems.;Interacted on a daily basis with system users to gather requirements, discuss feature requests, and answer any questions.;Introduced Postman as a way of streamlining our development and testing processes by utilizing Postman Runners and shared Workspace Collections.;Researched the up-and-coming microservice architecture design philosophy for a better understanding of how our applications could be modernized by moving to this new architecture concept.;Continued maintenance of Air Operations servers carried over from my previous role as Systems Administrator.",
        timeline_section=ubiquisoft_technologies,
    )
    systems_administrator = TimelineSubsection(
        title="Systems Administrator",
        start_date=date(2015, 1, 1),
        end_date=date(2016, 6, 1),
        details="Ran and maintained all thirty-five Air Operations servers hosted at the FedEx Air Operations Center, Memphis, TN.;Led a year long effort to move all thirty-five Air Operations server virtual machines to four new Cisco physical servers.;Continued management of virtual servers after migration in a RedHat 7 Hypervisor environment. SSH and X-11 forwarding used to maintain these servers as they were hosted within the FedEx Air Operations server farm.;Migrated all Air Operations personnel from RedHat desktop operating systems to Windows 7.;Provided on-site support to all Air Operations personnel as well as Ubiquisoft employees.;Remote support of different FedEx OpCos achieved using Windows Remote Desktop and shell SSH access using Putty and XMing.",
        timeline_section=ubiquisoft_technologies,
    )
    db.session.add(ubiquisoft_technologies)

    # Add new Project
    nate_web_project = Project(
        title="Nate3D.com",
        description="This website.",
    )
    
    # Assign timeline to site
    site.timeline = timeline
    
    # Assign projects to site
    site.projects.append(nate_web_project)

    db.session.commit()
