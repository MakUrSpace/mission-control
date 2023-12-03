#!/bin/bash

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

# Function to create alias hostname script
create_alias_script() {
    echo "Creating alias hostname script"

    cat > publish_alias.sh <<EOF
#!/bin/bash
IP_ADDRESS=\$(hostname -I | cut -d' ' -f1)

if [ -z "\$IP_ADDRESS" ]; then
    echo "Error: IP address not found."
    exit 1
fi

# Kill previous instances to avoid duplicates
kill \$(pgrep -f avahi-publish) 2>/dev/null

# Publish alias hostnames
avahi-publish -a mainsail.local -R \$IP_ADDRESS >/dev/null 2>&1 &
avahi-publish -a missioncontrol.local -R \$IP_ADDRESS >/dev/null 2>&1 &
avahi-publish -a octoprint.local -R \$IP_ADDRESS >/dev/null 2>&1 &
avahi-publish -a traefik.local -R \$IP_ADDRESS >/dev/null 2>&1 &
EOF

    chmod +x publish_alias.sh
}

# Function to create .env file with default environment variables
create_env_file() {
    echo "Creating .env file with default environment variables"

    cat > .env <<EOF
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
EOF
}

# Create the .env file
create_env_file

# Create and setup the alias hostname script
create_alias_script

# Add the alias hostname script to crontab for startup execution
echo "Adding alias hostname script to crontab for startup execution"
CRON_JOB="@reboot $(pwd)/publish_alias.sh"
(crontab -l 2>/dev/null | grep -v "$(pwd)/publish_alias.sh"; echo "$CRON_JOB") | crontab -

# Run the alias hostname script
echo "Running alias hostname script"
./publish_alias.sh

echo "Raspberry Pi setup completed."
