#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root"
    exit 1
fi

# Check if we are running in headless mode
headless_mode=0
force_mode=0

# Check for --headless argument
for arg in "$@"
do
    case $arg in
        --headless)
            headless_mode=1
            ;;
        -f|--force)
            force_mode=1
            ;;
    esac
done

# Check if Avahi is installed
if ! dpkg -s avahi-daemon avahi-utils >/dev/null 2>&1 || [ $force_mode -eq 1 ]; then
    echo "Installing Avahi..."
    sudo apt-get update
    sudo apt-get install -y avahi-daemon avahi-utils || { echo "Failed to install Avahi"; exit 1; }
else
    echo "Avahi already installed."
fi

# Check if Avahi service is enabled and running
if ! systemctl is-active --quiet avahi-daemon || [ $force_mode -eq 1 ]; then
    echo "Enabling and starting Avahi service"
    sudo systemctl enable avahi-daemon
    sudo systemctl start avahi-daemon
    echo "Avahi service enabled and started."
else
    echo "Avahi service is already running."
fi

# Path for the alias hostname script
ALIAS_SCRIPT_PATH="/usr/local/bin/publish_alias.sh"

# Function to create alias hostname script
create_alias_script() {
    if [ -f "${ALIAS_SCRIPT_PATH}" ] && [ -x "${ALIAS_SCRIPT_PATH}" ]; then
        if [ $force_mode -eq 1 ]; then
            echo "Force mode: Forcing creation of alias hostname script."
        else
            if [ $headless_mode -eq 1 ]; then
                echo "Headless mode: Alias hostname script already exists, skipping creation."
                return
            fi

            read -p "Alias hostname script already exists. Do you want to overwrite it? (y/N): " confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                echo "Aborting alias hostname script creation."
                return
            fi
        fi
    else
        echo "Alias hostname script does not exist or is not executable. Creating script."
    fi

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
    local service_path="/etc/systemd/system/publish-alias.service"

    if [ -f "${service_path}" ]; then
        if [ $force_mode -eq 1 ]; then
            echo "Force mode: Forcing creation of systemd service."
        else
            if [ -f "${service_path}" ]; then
                if [ $headless_mode -eq 1 ]; then
                    echo "Headless mode: Systemd service for publish_alias.sh already exists, skipping creation."
                    return
                fi

                read -p "Systemd service for publish_alias.sh already exists. Do you want to overwrite it? (y/N): " confirm
                if [[ ! $confirm =~ ^[Yy]$ ]]; then
                    echo "Aborting systemd service creation."
                    return
                fi
            fi
        fi
    else
        echo "Systemd service for publish_alias.sh does not exist. Creating service."
    fi

    echo "Creating systemd service for publish_alias.sh"

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
    if [ -f ".env" ]; then
        if [ $force_mode -eq 1 ]; then
            echo "Force mode: Forcing creation of .env file."
        else
            if [ $headless_mode -eq 1 ]; then
                echo "Headless mode: .env file already exists, skipping creation."
                return
            fi

            read -p ".env file already exists. Do you want to overwrite it? (y/N): " confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                echo "Aborting .env file creation."
                return
            fi
        fi
    else
        echo ".env file does not exist. Creating file."
    fi

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
    echo -e "\033[1;33m.env file created/overwritten.\033[0m"
    echo -e "\033[1;32mIMPORTANT:\033[0m Please modify the following variables to unique values of your choosing:"
    echo -e "\033[1;34mPOSTGRES_USER\033[0m"
    echo -e "\033[1;34mPOSTGRES_PASSWORD\033[0m"
    echo -e "\033[1;34mSECRET_KEY\033[0m"
    echo -e "\033[1;34mADMIN_PASSWORD\033[0m"
}

# Create the .env file
create_env_file

# Create and setup the alias hostname script
create_alias_script

# Create and setup the systemd service
create_systemd_service

echo "Raspberry Pi setup completed."
