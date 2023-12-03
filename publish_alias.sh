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
