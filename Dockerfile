# --- Build Stage for libsass ---
# Use a base image with build tools installed
FROM python:3.11-slim-bullseye as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsass-dev \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and wheel
RUN pip install --upgrade pip wheel

# Build libsass
RUN pip wheel libsass --wheel-dir=/wheels

# --- Final Stage ---
# Use an official Python runtime as a base image
FROM python:3.11-slim-bullseye as final

# Set the environment variables
ENV FLASK_APP=app/__init__.py

# Set the working directory
WORKDIR /

# Create a non-root user for security and add them to the docker group
ARG DOCKER_GID=999
RUN groupadd -r musAdmin && \
    groupadd -g ${DOCKER_GID} docker && \
    useradd -l -r -g musAdmin musAdmin && \
    usermod -aG docker musAdmin

# Copy the pre-built libsass wheel from the builder stage
COPY --from=builder --chown=musAdmin:musAdmin /wheels /wheels

# Copy the application files
COPY --chown=musAdmin:musAdmin ./app /app
COPY --chown=musAdmin:musAdmin ./migrations /migrations
COPY --chown=musAdmin:musAdmin ./scripts /scripts
COPY --chown=musAdmin:musAdmin ./requirements.txt /requirements.txt

# Install libsass using the pre-built wheel and other Python dependencies
RUN pip install --upgrade pip wheel \
    && pip install --no-cache-dir --find-links=/wheels libsass \
    && pip install --no-cache-dir --trusted-host pypi.python.org -r /requirements.txt \
    && rm -rf /wheels

# Expose the port the app runs on
EXPOSE 80

# Copy the entrypoint script into the container and make it executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Run the entrypoint script as the container's entrypoint (as root)
ENTRYPOINT ["entrypoint.sh"]

# Set the user and run the app
USER musAdmin
CMD ["gunicorn", "-k", "eventlet", "app:create_app()", "--bind", "0.0.0.0:80"]