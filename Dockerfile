# Use an official Python runtime as a base image
FROM python:3.9-slim

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the environment variables
ENV FLASK_APP=app/__init__.py

# Set the working directory
WORKDIR /app

# Copy the application folder(s) into the container
COPY ./app /app/app
COPY ./migrations /app/migrations
COPY ./scripts /app/scripts
COPY ./requirements.txt /app/requirements.txt

# Install the required packages
RUN pip install --upgrade pip wheel
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Expose the port the app runs on
EXPOSE 80

# Copy the entrypoint script into the container
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Ensure the script is executable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint to run the script
ENTRYPOINT ["entrypoint.sh"]
CMD ["gunicorn", "app:create_app()", "--bind", "0.0.0.0:80"]