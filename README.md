
# MakUrSpace Mission Control

This project serves as a template for quickly launching a Flask web application. It includes a PostgreSQL database, a basic single page application (SPA) frontend, and a Mainsail instance for 3D printer management. It is designed to be deployed via Docker Compose. The existing docker-compose setup is intended for development and production environments, but will need to be modified for deployment to your production server.

## Getting Started

These instructions will get your copy of the project up and running on your local machine for development and testing purposes.

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
python3 -m venv venv
```

4. Activate the virtual environment:
   - On macOS/Linux:
   ```sh
   source venv/bin/activate
   ```
   - On Windows:
   ```sh
   .\venv\Scripts\Activate
   ```

5. Install the required packages:
```sh
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

6. Create a `.env` file in the root directory and add the following environment variables:
```sh
POSTGRES_DB=webdb
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
DATABASE_DOMAIN=db
SECRET_KEY=supersecretkey
WEB_DOMAIN=missioncontrol.local
MAINSAIL_DOMAIN=mainsail.local
MAINSAIL_PORT=5556
OCTOPRINT_DOMAIN=octoprint.local
OCTOPRINT_PORT=5557
TRAEFIK_DOMAIN=traefik.local
```

### Running the Project

To run the project on your local development machine, you will use a mix of Flask and Docker Compose. 

First, you will need to start the database and Mainsail containers:

```sh
docker-compose build
docker-compose up -d # to run in detached mode
docker-compose down
docker-compose down -v # to remove volumes

docker-compose logs -f # to view logs
docker-compose up --build -d # to rebuild and run in detached mode
```

Then, you will need to set the Flask environment variables and run the Flask application:

```sh
export FLASK_ENV=development  # or set FLASK_ENV=development on Windows
flask run
flask run --reload # to reload on file changes
```

Your app should now be running on [http://localhost:5000](http://localhost:5000).

## Deployment (Raspberry Pi)

### Prerequisites

- [Raspberry Pi OS](https://www.raspberrypi.org/software/)
- [Docker](https://docs.docker.com/engine/install/debian/)

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
./scripts/raspberry_pi_setup.sh
```

4. Reboot the Raspberry Pi:
```sh
sudo reboot
```

### Deploying the Project

1. Use docker-compose to build and run the containers:
```sh
docker-compose -f docker-compose.yml -f docker-compose.embed.yml build
docker-compose -f docker-compose.yml -f docker-compose.embed.yml up -d
```

2. Use docker-compose to stop the containers:
```sh
docker-compose -f docker-compose.yml -f docker-compose.embed.yml down

# To remove volumes:
docker-compose -f docker-compose.yml -f docker-compose.embed.yml down -v
```

3. Use docker-compose to view logs:
```sh
docker-compose -f docker-compose.yml -f docker-compose.embed.yml logs -f
```

## CI/CD Process

Continuous Integration and Continuous Deployment (CI/CD) is set up to streamline the process of integrating changes from multiple contributors and deploying to production. It is currently hosted via Nate3D's Gitea server and backed by a Drone.io CI/CD server. The CI/CD process is as follows:

### Continuous Integration

- `.drone.yml` defines the CI pipeline.
- Pushes or merges to master automatically trigger the CI pipeline.
- The CI pipeline runs the docker-compose file to build the application and deploy the image to a private Docker registry.

### Continuous Deployment

- `.drone.yml` defines the CD pipeline.
- After building successfully, changes in the master branch are automatically deployed to the production server.

## Contributing

Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

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
