#!/bin/bash

# Constants
CURRENT_USER=${SUDO_USER:-$(whoami)}

# Logging functions
info() {
    echo -e "\033[32m[INFO]\033[0m $1"
}

warn() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# Check if we are running as root
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root."
    error "Run 'sudo !!' to re-run this command as root."
    exit 1
fi

# Check if we are running in headless mode
headless_mode=0
force_mode=0
logout_required=0
venv_need_activate=0

# Check for --headless argument
for arg in "$@"; do
    case $arg in
    --headless)
        headless_mode=1
        warn "Headless mode: Skipping interactive prompts."
        ;;
    -f | --force)
        force_mode=1
        warn "Force mode: Forcing all actions."
        ;;
    --uninstall)
        uninstall
        exit 0
        ;;
    esac
done

# Check if docker is installed
if ! dpkg -s docker-ce docker-ce-cli containerd.io >/dev/null 2>&1 || [ $force_mode -eq 1 ]; then
    info "Installing Docker..."
    curl -fsSL https://get.docker.com -o install-docker.sh
    sh install-docker.sh || {
        error "Failed to install Docker"
        exit 1
    }
else
    info "Docker already installed."
    export DOCKER_GID=$(stat -c '%g' /var/run/docker.sock)
fi

# Check if required python packages are installed
if ! dpkg -s python3 python3-pip >/dev/null 2>&1 || [ $force_mode -eq 1 ]; then
    info "Installing Python 3 and pip..."
    apt-get update
    apt-get install -y python3 python3-pip || {
        error "Failed to install Python 3 and pip"
        exit 1
    }
else
    info "Python 3 and pip already installed."
fi

# Check if Avahi is installed
if ! dpkg -s avahi-daemon avahi-utils >/dev/null 2>&1 || [ $force_mode -eq 1 ]; then
    info "Installing Avahi..."
    apt-get update
    apt-get install -y avahi-daemon avahi-utils || {
        error "Failed to install Avahi"
        exit 1
    }
else
    info "Avahi already installed."
fi

# Check if Avahi service is enabled and running
if ! systemctl is-active --quiet avahi-daemon || [ $force_mode -eq 1 ]; then
    info "Enabling and starting Avahi service"
    systemctl enable avahi-daemon
    systemctl start avahi-daemon
    info "Avahi service enabled and started."
else
    info "Avahi service is already running."
fi

# Path for the alias hostname script
ALIAS_SCRIPT_PATH="/usr/local/bin/publish_alias.sh"

# Function to create alias hostname script
create_alias_script() {
    if [ -f "${ALIAS_SCRIPT_PATH}" ] && [ -x "${ALIAS_SCRIPT_PATH}" ]; then
        if [ $force_mode -eq 1 ]; then
            info "Force mode: Forcing creation of alias hostname script."
        else
            if [ $headless_mode -eq 1 ]; then
                info "Headless mode: Alias hostname script already exists, skipping creation."
                return
            fi

            info "Alias hostname script already exists."
            echo -ne "\033[32m[INFO]\033[0m Do you want to overwrite it? (y/N): "
            read confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                info "Aborting alias hostname script creation."
                return
            fi
        fi
    else
        info "Alias hostname script does not exist or is not executable. Creating script."
    fi

    info "Creating alias hostname script at ${ALIAS_SCRIPT_PATH}"
    tee "${ALIAS_SCRIPT_PATH}" >/dev/null <<'EOF'
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
avahi-publish -a cncjs.local -R $IP_ADDRESS >/dev/null 2>&1 &
EOF

    chmod +x "${ALIAS_SCRIPT_PATH}"
}

# Function to create systemd service file for the script
create_systemd_service() {
    local service_path="/etc/systemd/system/publish-alias.service"

    if [ -f "${service_path}" ]; then
        if [ $force_mode -eq 1 ]; then
            info "Force mode: Forcing creation of systemd service."
        else
            if [ -f "${service_path}" ]; then
                if [ $headless_mode -eq 1 ]; then
                    info "Headless mode: Systemd service for publish_alias.sh already exists, skipping creation."
                    return
                fi

                info "Publish-alias systemd service already exists."
                echo -ne "\033[32m[INFO]\033[0m Do you want to overwrite it? (y/N): "
                read confirm
                if [[ ! $confirm =~ ^[Yy]$ ]]; then
                    info "Aborting systemd service creation."
                    return
                fi
            fi
        fi
    else
        info "Systemd service for publish_alias.sh does not exist. Creating service."
    fi

    info "Creating systemd service for publish_alias.sh"

    tee "${service_path}" >/dev/null <<EOF
[Unit]
Description=Publish Alias Hostnames
After=network-online.target avahi-daemon.service
Wants=network-online.target avahi-daemon.service

[Service]
Type=oneshot
ExecStart=${ALIAS_SCRIPT_PATH}
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

    # Reload the systemd manager configuration
    systemctl daemon-reload

    # Enable the service
    systemctl enable publish-alias.service

    # Start the service
    systemctl start publish-alias.service
}

# Function to create .env file with default environment variables
create_env_file() {
    if [ -f ".env" ]; then
        if [ $force_mode -eq 1 ]; then
            info "Force mode: Forcing creation of .env file."
        else
            if [ $headless_mode -eq 1 ]; then
                info "Headless mode: .env file already exists, skipping creation."
                return
            fi

            info ".env file already exists."
            echo -ne "\033[32m[INFO]\033[0m Do you want to overwrite it? (y/N): "
            read confirm
            if [[ ! $confirm =~ ^[Yy]$ ]]; then
                info "Aborting .env file creation."
                return
            fi
        fi
    else
        info ".env file does not exist. Creating file."
    fi

    info "Creating .env file with default environment variables"

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

    chown $CURRENT_USER:$CURRENT_USER .env

    echo -e "\033[1;33m.env file created/overwritten.\033[0m"
    echo -e "\033[1;32mIMPORTANT:\033[0m Please modify the following variables to unique values of your choosing:"
    echo -e "\033[1;34mPOSTGRES_USER\033[0m"
    echo -e "\033[1;34mPOSTGRES_PASSWORD\033[0m"
    echo -e "\033[1;34mSECRET_KEY\033[0m"
    echo -e "\033[1;34mADMIN_PASSWORD\033[0m"
}

# Function to add the current user to the docker group
add_user_to_docker_group() {
    # Check if the docker group exists
    if getent group docker >/dev/null; then
        info "Docker group exists."

        # Check if the user is not already in the docker group
        if ! groups $CURRENT_USER | grep -q '\bdocker\b'; then
            info "Adding $CURRENT_USER to the docker group."
            sudo usermod -aG docker $CURRENT_USER

            info "User $CURRENT_USER has been added to the docker group."
            info "Please log out and back in for this to take effect."
            logout_required=1
        else
            info "User $CURRENT_USER is already a member of the docker group."
        fi
    else
        info "Docker group does not exist."
    fi
}

# Function to setup venv and install required python packages
setup_venv() {
    # Check if venv is installed
    if ! dpkg -s python3-venv >/dev/null 2>&1; then
        info "Installing python3-venv..."
        apt-get update
        apt-get install -y python3-venv || {
            info "Failed to install python3-venv"
            exit 1
        }
    else
        info "python3-venv already installed."
    fi

    # Check if .venv exists
    if [ ! -d ".venv" ]; then
        info "Creating venv..."
        python3 -m venv .venv || {
            info "Failed to create .venv"
            exit 1
        }
    else
        info ".venv already exists."
    fi

    chown -R $CURRENT_USER:$CURRENT_USER .venv

    # Check if the virtual environment is already active
    if [ -z "$VIRTUAL_ENV" ]; then
        warn "Please activate the virtual environment with 'source .venv/bin/activate' before proceeding."
        venv_need_activate=1
        return 1
    fi

    # Check if requirements are already satisfied
    if ! pip3 freeze | grep -f requirements.txt >/dev/null 2>&1; then
        info "Installing required python packages..."
        pip3 install -r requirements.txt || {
            info "Failed to install required python packages"
            exit 1
        }
    else
        info "Required python packages are already installed."
    fi
}

uninstall() {
    info "Uninstalling Raspberry Pi setup for MakUrSpace Mission Control..."
    # Remove the alias hostname script
    if [ -f "${ALIAS_SCRIPT_PATH}" ]; then
        info "Removing alias hostname script..."
        rm -f "${ALIAS_SCRIPT_PATH}"
    else
        warn "Alias hostname script not found at ${ALIAS_SCRIPT_PATH}."
    fi

    # Disable and remove the systemd service
    local service_path="/etc/systemd/system/publish-alias.service"
    if [ -f "${service_path}" ]; then
        info "Removing systemd service for publish_alias.sh..."
        systemctl stop publish-alias.service
        systemctl disable publish-alias.service
        rm -f "${service_path}"
        systemctl daemon-reload
    fi

    # Remove .env file
    if [ -f ".env" ]; then
        info "Removing .env file..."
        rm -f ".env"
    else
        warn ".env file not found."
    fi

    # Remove the virtual environment directory
    if [ -d ".venv" ]; then
        info "Removing virtual environment..."
        rm -rf ".venv"
    else
        warn ".venv directory not found."
    fi

    info "Uninstallation completed."

    warn "System packages were not removed. Please remove them manually if required:"
    warn "Docker: docker-ce docker-ce-cli containerd.io"
    warn "Python: python3 python3-pip"
    warn "Avahi: avahi-daemon avahi-utils"
    warn "$ sudo apt-get remove -y <package_name>"
}

# Add the current user to the docker group
add_user_to_docker_group

# Setup venv and install required python packages
setup_venv

# Create the .env file
create_env_file

# Create and setup the alias hostname script
create_alias_script

# Create and setup the systemd service
create_systemd_service

info "###############################################"
info "MakUrSpace Mission Control: Raspberry Pi setup complete"
info "###############################################"

if [ $logout_required -eq 1 ]; then
    echo -e "\033[1;32mIMPORTANT:\033[0m Please log out and back in for the changes to take effect."
fi

if [ $venv_need_activate -eq 1 ]; then
    echo -e "\033[1;33mIMPORTANT:\033[0m Please activate the virtual environment with 'source .venv/bin/activate' before proceeding."
fi
