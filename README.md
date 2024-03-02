
# 1. MakUrSpace Mission Control

Mission Control is the gateway to YOUR makerspace.

It provides a single point of access to all of your makerspace tools and services.
It is intended to be run on a Raspberry Pi and is designed to be easy to set up
and use. Mission Control puts you in control of YOUR makerspace by providing an
out-of-the-box experience for accessing your makerspace tools and services.

Mission Control is built with Flask and Docker Compose. It is designed to be
modular and extensible. It is currently configured to work with the following services:

- [Mainsail](https://docs.mainsail.xyz/)
- [Octoprint](https://octoprint.org/)
- [CNCJS](https://cnc.js.org/)
- [Traefik](https://doc.traefik.io/traefik/)
- [Postgres](https://www.postgresql.org/)

> Want to see another service here? Open an issue and let us know!

## 1.1. Table of Contents

- [1. MakUrSpace Mission Control](#1-makurspace-mission-control)
  - [1.1. Table of Contents](#11-table-of-contents)
  - [1.2. Getting Started](#12-getting-started)
    - [1.2.1. Prerequisites](#121-prerequisites)
    - [1.2.2. Setting Up the Development Environment](#122-setting-up-the-development-environment)
      - [1.2.2.1. Using VSCode and Python Virtual Environments](#1221-using-vscode-and-python-virtual-environments)
    - [1.2.3. Running the Project](#123-running-the-project)
    - [1.2.4. Upgrading Project](#124-upgrading-project)
  - [1.3. Deployment (Raspberry Pi)](#13-deployment-raspberry-pi)
    - [1.3.1. Prerequisites](#131-prerequisites)
    - [1.3.2. Setting Up the Raspberry Pi](#132-setting-up-the-raspberry-pi)
    - [1.3.3. Building and Running the Project](#133-building-and-running-the-project)
    - [1.3.4. Accessing Your MissionControl Toolkit](#134-accessing-your-missioncontrol-toolkit)
    - [1.3.5. Upgrading Project](#135-upgrading-project)
  - [1.4. CI/CD Process](#14-cicd-process)
    - [1.4.1. Continuous Integration](#141-continuous-integration)
    - [1.4.2. Continuous Deployment](#142-continuous-deployment)
  - [1.5. Contributing](#15-contributing)
    - [1.5.1. Updating Database Migrations](#151-updating-database-migrations)
    - [1.5.2. Using Migrations](#152-using-migrations)
  - [1.6. License](#16-license)

## 1.2. Getting Started

These instructions will get your copy of the project up and running on your
local machine for development and testing purposes.

### 1.2.1. Prerequisites

What things you need to install the software:

- [Python 3.x](https://www.python.org/downloads/)
- [VSCode](https://code.visualstudio.com/download)
- [Git](https://git-scm.com/downloads)

### 1.2.2. Setting Up the Development Environment

#### 1.2.2.1. Using VSCode and Python Virtual Environments

1. Clone the repository to your local machine:

   ```sh
   git clone git@github.com:MakUrSpace/mission-control.git
   ```

2. Open the cloned directory in VSCode.

3. Create a virtual environment:

   ```sh
   python3 -m venv .venv
   ```

4. Activate the virtual environment:
   - On macOS/Linux:

     ```sh
     source .venv/bin/activate
     ```

   - On Windows (PowerShell):

      ```powershell
      .venv\Scripts\Activate.ps1
      ```

   - On Windows (cmd):

      ```cmd
      .venv\Scripts\activate
      ```

5. Install the required packages:

   ```sh
   pip install -r requirements.txt
   pip install -r requirements_dev.txt
   ```

6. Create a `.env` file in the workspace root directory and add the
following environment variables. (Copy & Paste the following)

   > **Note:** The `.env` file is ignored by git and should not be committed.
   > These values are for development purposes only and may be edited freely.

   > **IMPORTANT:** The same variables are used for container creation as well as for access to the same.
   > If you need to change any after creating the container, simply destroy and re-create the containers after updating .env.

   ```sh
   # Flask application entry point
   FLASK_APP=app/__init__.py

   # Postgres database name
   POSTGRES_DB=webdb

   # Postgres username
   POSTGRES_USER=admin

   # Postgres password
   POSTGRES_PASSWORD=password

   # Postgres domain
   DATABASE_DOMAIN=localhost

   # Flask property for Cross-Site Request Forgery (CSRF) 
   # Protection, session management, etc.
   SECRET_KEY=supersecretkey

   # Flask web app FQDN
   WEB_DOMAIN=localhost

   # Mainsail FQDN
   MAINSAIL_DOMAIN=localhost

   # Mainsail port
   MAINSAIL_PORT=5556

   # Octoprint FQDN
   OCTOPRINT_DOMAIN=localhost

   # Octoprint port
   OCTOPRINT_PORT=5557

   # CNCJS FQDN
   CNCJS_DOMAIN=localhost

   # CNCJS port
   CNCJS_PORT=5558

   # Traefik FQDN (not used when running locally; see Raspberry Pi setup)
   TRAEFIK_DOMAIN=localhost

   # Admin password for the web app
   ADMIN_PASSWORD=admin

   # Docker Compose file(s) to use when running locally
   COMPOSE_FILE=docker_compose/docker-compose.yml:docker_compose/docker-compose.override.yml

   # Docker group ID (used when running locally)
   DOCKER_GID=999 # Run `getent group docker` to get the GID value

   ```

   > **Additional Notes:**
   >- The `SECRET_KEY` value should be a random string of characters.
   >- The `DATABASE_DOMAIN` will be localhost when running locally, but will be
   > the container name when running in Docker (or network alias).
   >- The `WEB_DOMAIN` will be localhost when running locally, but will be
   > **missioncontrol.local** name when running with docker-compose.embed.yml.
   >- The `MAINSAIL_DOMAIN` will be localhost when running locally, but will be
   > **mainsail.local** name when running with docker-compose.embed.yml.
   >- The `OCTOPRINT_DOMAIN` will be localhost when running locally, but will be
   > **octoprint.local** name when running with docker-compose.embed.yml.
   >- The `CNCJS_DOMAIN` will be localhost when running locally, but will be
   > **cncjs.local** name when running with docker-compose.embed.yml.
   >- The `*_PORT` values are the ports that the containers will be exposed on.
   > **These ports are only used when running locally.**
   >- The `TRAEFIK_DOMAIN` is not used when running locally. It is used to route
   >traffic to the appropriate container when running with docker-compose.embed.yml.
   >- The `ADMIN_PASSWORD` value is the password for the admin user.
   >- The `COMPOSE_FILE` value is a colon-separated list of docker-compose files.
   > _If on Windows, use semicolons instead of colons._
   >- The `DOCKER_GID` value is the group ID of the docker group. This is used to access the docker socket when running locally. This will need to match the group ID of the docker group on your local machine. Run `getent group docker` to get the GID value.

### 1.2.3. Running the Project

To run the project on your local development machine, you will use a mix
of Flask and Docker Compose.

First, you will need to start the database and other services:

```sh
docker compose up --build -d
```

Then, you will need to apply the database migrations:

```sh
flask db upgrade
```

Then, you will need to seed the database:

```sh
python3 scripts/seed_db.py
```

Then, simply run the Flask application with the provided development wrapper:

```sh
python3 run.py
```

Your app should now be running on [http://localhost:5000](http://localhost:5000).

### 1.2.4. Upgrading Project

To upgrade the project to the latest version:

1. Pull the latest changes from the repository:

   ```sh
   git pull
   ```

2. Stop the running containers and destroy the volumes:

   ```sh
   docker compose down -v
   ```

   >**Note:** This will destroy the database and all data stored in it.

3. Check the `.env` file for any new environment variables and add them.
4. Rebuild and run the containers:

   ```sh
   docker compose up --build -d
   ```

5. Apply any database migrations:

   ```sh
   flask db upgrade
   ```

6. Re-seed the database:

   ```sh
   python3 scripts/seed_db.py
   ```

7. Run the Flask application:

   ```sh
   python3 run.py
   ```

You should now be able to access the application at
[http://localhost:5000](http://localhost:5000).

## 1.3. Deployment (Raspberry Pi)

### 1.3.1. Prerequisites

   > **Note:** The following instructions are for a Raspberry Pi running
   > Raspberry Pi OS.
   >
   > **Docker will be installed by running the `raspberry_pi_setup.sh` script.
   > Links below are for reference only.**

- [Raspberry Pi OS](https://www.raspberrypi.org/software/)
- [Docker (Raspberry Pi arm64)](https://docs.docker.com/engine/install/debian/)
- [Docker (Raspberry Pi armhf)](https://docs.docker.com/engine/install/raspberry-pi-os/)

### 1.3.2. Setting Up the Raspberry Pi

1. Clone the repository to your local machine:

   ```sh
   git clone git@github.com:MakUrSpace/mission-control.git
   ```

2. Run the setup script. It must be run with sudo:

   ```sh
   cd mission-control
   sudo ./scripts/raspberry_pi_setup.sh
   ```

   >**It is safe to run the setup script multiple times**
   >The script will attempt to install the Python packages defined in
   >`requirements.txt`. The dev packages are not installed, see
   >[Installing Dev Dependencies on Raspberry Pi](#installing-dev-dependencies-on-raspberry-pi)
   for details.

3. Reboot the Raspberry Pi(optional, but recommended):

   ```sh
   sudo reboot
   ```

### 1.3.3. Building and Running the Project

A convenience script is provided to build and run the project:

```sh
./docker_manager <command>

Commands:
    start | up      (Re)start (and build) the Docker containers
    stop | down     Stop the Docker containers
    status | ps     Show the status of the Docker containers
    destroy | rm    Destroy the Docker containers
    purge | bye     Purge the Docker containers and images
    logs | log      Show docker logs
    help            Show this help message
```

### 1.3.4. Accessing Your MissionControl Toolkit

Once the project is running, you can access the
following **_MakUrSpace_ Mission Control** services:

- [MissionControl Web App](http://missioncontrol.local)
  - MissionControl Web App is a single page application (SPA) that provides
    access to the other services. It is built with Flask and simple HTML/SCSS.
    >This is **your** maker dashboard.
- [Mainsail](http://mainsail.local)
  - Mainsail is a modern, responsive web interface for klipper open-source 3D
    printer firmware. Read more about it [here](https://docs.mainsail.xyz/)
    >This is **your** 3D printer dashboard for your Klipper-powered 3D makerspace.
- [Octoprint](http://octoprint.local)
  - Octoprint is an extremely powerful application for managing 3D printers with
    a responsive and extensive web app.
    Read more about it [here](https://octoprint.org/)
    >This is **your** 3D printer dashboard for your Marlin-powered 3D makerspace.
- [Traefik Dashboard](http://traefik.local)
  - Traefik is a reverse proxy that routes traffic to the appropriate service
    based on the domain name.
    MissionControl pairs this with the power of mDNS to provide a seamless
    experience for your makerspace.
    >This is **your** Mission Control central switchboard.

### 1.3.5. Upgrading Project

To upgrade the project to the latest version:

1. Pull the latest changes from the repository:

   ```sh
   git pull
   ```

2. Stop the running app and destroy the app volumes:

   ```sh
   ./docker_manager destroy
   ```

   >**Note:** This will destroy the database and all data stored in it.

3. Re-run the setup script with headless+force mode:

   ```sh
   sudo ./scripts/raspberry_pi_setup.sh --headless -f
   ```

4. Rebuild and run the app:

   ```sh
   ./docker_manager start
   ```

You should now be able to access the application at
[http://missioncontrol.local](http://missioncontrol.local).

## 1.4. CI/CD Process

Continuous Integration and Continuous Deployment (CI/CD) is set up to streamline
the process of integrating changes from multiple contributors and deploying to
production. It is currently hosted via Nate3D's Gitea server and backed by a
Drone.io CI/CD server. The CI/CD process is as follows:

### 1.4.1. Continuous Integration

- `.drone.yml` defines the CI pipeline.
- Pushes or merges to master automatically trigger the CI pipeline.
- The CI pipeline runs the docker-compose file to build the application and
deploy the image to a private Docker registry.

### 1.4.2. Continuous Deployment

- `.drone.yml` defines the CD pipeline.
- After building successfully, changes in the master branch are automatically
deployed to the production server.

## 1.5. Contributing

Contributions are what make the open-source community an amazing place to learn,
inspire, and create. Any contributions you make are **greatly appreciated**.

### 1.5.1. Updating Database Migrations

When contributing changes to the database models:

1. Generate a new migration file after modifying models:

   ```sh
   flask db migrate -m "Add or modify fields"
   ```

2. Review the generated migration file to ensure accuracy.

3. Apply the migration to the database:

   ```sh
   flask db upgrade
   ```

4. Commit the migration file along with your model changes.

### 1.5.2. Using Migrations

To apply migrations to your local database:

```sh
flask db upgrade
```

To rollback a migration:

```sh
flask db downgrade
```

## 1.6. License

TBD
