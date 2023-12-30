# --- Build Stage ---
# Use a base image with build tools installed
FROM python:3.11-slim-bullseye as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and wheel
RUN pip install --upgrade pip wheel

# --- Final Stage ---
# Use an official Python runtime as a base image
FROM python:3.11-slim-bullseye as final

# Set the environment variables
ENV FLASK_APP=app/__init__.py

# Set the working directory
WORKDIR /mission-control

# Install curl and other necessary packages
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create new user and docker group
# Create a non-root user for security and add them to the docker group
ARG DOCKER_GID=999
RUN getent group docker || groupadd -g $DOCKER_GID docker && \
    useradd -m -G docker musAdmin

# Copy the application files
COPY --chown=musAdmin:musAdmin ./app app
COPY --chown=musAdmin:musAdmin ./migrations migrations
COPY --chown=musAdmin:musAdmin ./scripts scripts
COPY --chown=musAdmin:musAdmin ./requirements.txt requirements.txt

# Copy the entrypoint script to the container and make it executable
COPY --chown=musAdmin:musAdmin entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Switch to the non-root user
USER musAdmin

# Update PATH to include user's local bin directory
ENV PATH=/home/musAdmin/.local/bin:${PATH}

# Install Python dependencies
RUN pip install --upgrade pip wheel \
    && pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script as the container's entrypoint
ENTRYPOINT ["entrypoint.sh"]

# Run the app with gunicorn with eventlet support
CMD ["gunicorn", "-k", "eventlet", "app:create_app()", "--bind", "0.0.0.0:8000"]

