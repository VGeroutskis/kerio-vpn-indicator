#!/bin/bash
# Update Kerio VPN Indicator

echo "Updating Kerio VPN Indicator..."

# Pull latest changes
git pull

# Stop running indicator
echo "Stopping running indicator..."
pkill -f kerio-vpn-indicator

# Copy files
sudo cp kerio-vpn-indicator.py /usr/local/bin/kerio-vpn-indicator
sudo cp kerio-config-editor.py /usr/local/bin/kerio-config-editor

# Set permissions
sudo chmod +x /usr/local/bin/kerio-vpn-indicator
sudo chmod +x /usr/local/bin/kerio-config-editor

# Restart indicator
echo "Restarting indicator..."
nohup kerio-vpn-indicator > /dev/null 2>&1 &

echo "Update complete!"
