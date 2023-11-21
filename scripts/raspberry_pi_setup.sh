#!/bin/bash

# Update and install Avahi
sudo apt-get update
sudo apt-get install -y avahi-daemon

# Enable and start Avahi service
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon

# Function to create Avahi service file
create_avahi_service_file() {
    local service_name=$1
    local port=$2
    local file_path="/etc/avahi/services/${service_name}.service"

    echo "Creating Avahi service file for ${service_name}"

    sudo bash -c "cat > ${file_path}" <<EOF
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">${service_name} on %h</name>
  <service>
    <type>_http._tcp</type>
    <port>${port}</port>
  </service>
</service-group>
EOF
}

# Function to create .env file with default environment variables
create_env_file() {
    echo "Creating .env file with default environment variables"

    cat > .env <<EOF
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
EOF
}

# Create Avahi service files
create_avahi_service_file "missioncontrol" 80
create_avahi_service_file "mainsail" 80
create_avahi_service_file "octoprint" 80
create_avahi_service_file "traefik" 80

# Restart Avahi to apply changes
sudo systemctl restart avahi-daemon

# Create the .env file
create_env_file

echo "Raspberry Pi setup completed."
