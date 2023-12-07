#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    exit 1
fi

# Check if Avahi is installed
if ! dpkg -s avahi-daemon avahi-utils >/dev/null 2>&1; then
    echo "Installing Avahi..."
    sudo apt-get update
    sudo apt-get install -y avahi-daemon avahi-utils
else
    echo "Avahi already installed."
fi

# Enable and start Avahi service
echo "Enabling and starting Avahi service"
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
echo "Avahi service enabled and started."

# Path for the alias hostname script
ALIAS_SCRIPT_PATH="/usr/local/bin/publish_alias.sh"

# Function to create alias hostname script
create_alias_script() {
    echo "Creating alias hostname script at ${ALIAS_SCRIPT_PATH}"

    sudo tee "${ALIAS_SCRIPT_PATH}" >/dev/null <<'EOF'
#!/bin/bash
IP_ADDRESS=$(hostname -I | cut -d' ' -f1)

if [ -z "$IP_ADDRESS" ]; then
    echo "Error: IP address not found."
    exit 1
fi

# Kill previous instances to avoid duplicates
kill $(pgrep -f avahi-publish) 2>/dev/null

# Publish alias hostnames
avahi-publish -a mainsail.local -R $IP_ADDRESS >/dev/null 2>&1 &
avahi-publish -a missioncontrol.local -R $IP_ADDRESS >/dev/null 2>&1 &
avahi-publish -a octoprint.local -R $IP_ADDRESS >/dev/null 2>&1 &
avahi-publish -a traefik.local -R $IP_ADDRESS >/dev/null 2>&1 &
EOF

    sudo chmod +x "${ALIAS_SCRIPT_PATH}"
}

# Function to create systemd service file for the script
create_systemd_service() {
    echo "Creating systemd service for publish_alias.sh"

    local service_path="/etc/systemd/system/publish-alias.service"
    sudo tee "${service_path}" >/dev/null <<EOF
[Unit]
Description=Publish Alias Hostnames
After=avahi-daemon.service
Wants=avahi-daemon.service

[Service]
Type=oneshot
ExecStart=${ALIAS_SCRIPT_PATH}
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    # Reload the systemd manager configuration
    sudo systemctl daemon-reload

    # Enable the service
    sudo systemctl enable publish-alias.service

    # Start the service
    sudo systemctl start publish-alias.service
}

# Function to create .env file with default environment variables
create_env_file() {
    echo "Creating .env file with default environment variables"

    cat >.env <<EOF
# Environment variables for docker-compose
POSTGRES_DB=webdb
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
DATABASE_DOMAIN=db
SECRET_KEY=supersecretkey
WEB_DOMAIN=missioncontrol.local
MAINSAIL_DOMAIN=mainsail.local
OCTOPRINT_DOMAIN=octoprint.local
TRAEFIK_DOMAIN=traefik.local
ADMIN_PASSWORD=changeme!
EOF
}

# Create the .env file
create_env_file

# Create and setup the alias hostname script
create_alias_script

# Create and setup the systemd service
create_systemd_service

echo "Raspberry Pi setup completed."
