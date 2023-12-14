
# MakUrSpace Mission Control

This project serves as a template for quickly launching a Flask web application.
It includes a PostgreSQL database, a basic single page application (SPA)
frontend, and a Mainsail instance for 3D printer management. It is designed to
be deployed via Docker Compose. The existing docker compose setup is intended for
development and production environments, but will need to be modified for
deployment to your production server.

## Table of Contents
- [MakUrSpace Mission Control](#makurspace-mission-control)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Setting Up the Development Environment](#setting-up-the-development-environment)
      - [Using VSCode and Python Virtual Environments](#using-vscode-and-python-virtual-environments)
    - [Running the Project](#running-the-project)
  - [Deployment (Raspberry Pi)](#deployment-raspberry-pi)
    - [Prerequisites](#prerequisites-1)
    - [Setting Up the Raspberry Pi](#setting-up-the-raspberry-pi)
    - [Deploying the Project](#deploying-the-project)
  - [CI/CD Process](#cicd-process)
    - [Continuous Integration](#continuous-integration)
    - [Continuous Deployment](#continuous-deployment)
  - [Contributing](#contributing)
    - [Updating Database Migrations](#updating-database-migrations)
    - [Using Migrations](#using-migrations)
  - [License](#license)


## Getting Started

These instructions will get your copy of the project up and running on your
local machine for development and testing purposes.

### Prerequisites

What things you need to install the software:

- [Python 3.x](https://www.python.org/downloads/)
- [VSCode](https://code.visualstudio.com/download)
- [Git](https://git-scm.com/downloads)

### Setting Up the Development Environment

#### Using VSCode and Python Virtual Environments

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
following environment variables. 

   > **Note:** The `.env` file is ignored by git and should not be committed. 
   > These values are for development purposes only and may be edited freely.

   ```sh
   FLASK_APP=app/__init__.py # Flask application entry point
   POSTGRES_DB=webdb # Postgres database name
   POSTGRES_USER=admin # Postgres username
   POSTGRES_PASSWORD=password # Postgres password
   DATABASE_DOMAIN=localhost # Postgres domain
   SECRET_KEY=supersecretkey # Flask property for Cross-Site Request Forgery (CSRF) Protection, session management, etc.
   WEB_DOMAIN=localhost # Flask web app FQDN
   MAINSAIL_DOMAIN=localhost # Mainsail FQDN
   MAINSAIL_PORT=5556 # Not used when running with docker-compose.embed.yml
   OCTOPRINT_DOMAIN=localhost # Octoprint FQDN
   OCTOPRINT_PORT=5557 # Not used when running with docker-compose.embed.yml
   ADMIN_PASSWORD=admin # Admin password for the web app
   ```

   > **Additional Notes:**
   >- The `SECRET_KEY` value should be a random string of characters.
   >- The `DATABASE_DOMAIN` will be localhost when running locally, but will be the container name when running in Docker (or network alias).
   >- The `WEB_DOMAIN` will be localhost when running locally, but will be __missioncontrol.local__ name when running with docker-compose.embed.yml.
   >- The `MAINSAIL_DOMAIN` will be localhost when running locally, but will be __mainsail.local__ name when running with docker-compose.embed.yml.
   >- The `OCTOPRINT_DOMAIN` will be localhost when running locally, but will be __octoprint.local__ name when running with docker-compose.embed.yml.
   >- The `*_PORT` values are the ports that the containers will be exposed on. These values are only used when running locally.

### Running the Project

To run the project on your local development machine, you will use a mix
of Flask and Docker Compose.

First, you will need to start the database and Mainsail containers:

```sh
docker compose up --build -d
```

>_Some useful docker compose commands:_
   >    ```sh
   >    docker compose build # to build the containers
   >    docker compose up -d # to run the built containers in detached mode
   >    docker compose down # to stop the containers
   >    docker compose down -v # to stop the containers and remove volumes
   >
   >    docker compose logs -f # to follow the logs
   >    docker compose up --build -d # to rebuild and run in detached mode
   >    ```
   >   **Note:** Docker compose automatically applies the docker-compose.override.yml file if it exists. This is equivalent to running `docker compose -f docker-compose.yml -f docker-compose.override.yml up -d`.

Then, you will need to set the Flask environment variables and run the Flask application:

Mac/Linux:

```sh
export FLASK_ENV=development
flask run
flask run --reload # to reload on file changes
```

Windows(PowerShell):

```powershell
$env:FLASK_ENV="development"
flask run
flask run --reload # to reload on file changes
```

Windows(cmd):

```cmd
set FLASK_ENV=development
flask run
flask run --reload # to reload on file changes
```

Your app should now be running on [http://localhost:5000](http://localhost:5000).

## Deployment (Raspberry Pi)

### Prerequisites

- [Raspberry Pi OS](https://www.raspberrypi.org/software/)
- [Docker (Raspberry Pi arm64)](https://docs.docker.com/engine/install/debian/)
- [Docker (Raspberry Pi armhf)](https://docs.docker.com/engine/install/raspberry-pi-os/)

### Setting Up the Raspberry Pi

1. Install the required packages:

   ```sh
   sudo apt-get update
   sudo apt-get install -y git python3 python3-pip
   ```

2. Clone the repository to your local machine:

   ```sh
   git clone git@github.com:MakUrSpace/mission-control.git
   ```

3. Run the setup script. This will setup the .env file and setup mDNS for mission-control:

   ```sh
   cd mission-control
   sudo ./scripts/raspberry_pi_setup.sh
   ```

4. Reboot the Raspberry Pi:

   ```sh
   sudo reboot
   ```

### Building and Running the Project

A convenience script is provided to build and run the project:

```sh
Usage: ./docker_manager {start|stop|destroy|status|logs} 
```

## CI/CD Process

Continuous Integration and Continuous Deployment (CI/CD) is set up to streamline
the process of integrating changes from multiple contributors and deploying to
production. It is currently hosted via Nate3D's Gitea server and backed by a
Drone.io CI/CD server. The CI/CD process is as follows:

### Continuous Integration

- `.drone.yml` defines the CI pipeline.
- Pushes or merges to master automatically trigger the CI pipeline.
- The CI pipeline runs the docker-compose file to build the application and
deploy the image to a private Docker registry.

### Continuous Deployment

- `.drone.yml` defines the CD pipeline.
- After building successfully, changes in the master branch are automatically
deployed to the production server.

## Contributing

Contributions are what make the open-source community an amazing place to learn,
inspire, and create. Any contributions you make are **greatly appreciated**.

### Updating Database Migrations

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

### Using Migrations

To apply migrations to your local database:

```sh
flask db upgrade
```

To rollback a migration:

```sh
flask db downgrade
```

## License

TBD
