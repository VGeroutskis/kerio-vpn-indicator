#!/bin/bash
# Update Kerio VPN Indicator

echo "Updating Kerio VPN Indicator..."

# Pull latest changes
git pull

# Copy files
sudo cp kerio-vpn-indicator.py /usr/local/bin/kerio-vpn-indicator
sudo cp kerio-config-editor.py /usr/local/bin/kerio-config-editor

# Set permissions
sudo chmod +x /usr/local/bin/kerio-vpn-indicator
sudo chmod +x /usr/local/bin/kerio-config-editor

echo "Update complete! Restart the indicator if it's running."
