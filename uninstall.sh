#!/bin/bash

# Kerio VPN Indicator Uninstallation Script

set -e

echo "==================================="
echo "Kerio VPN Indicator Uninstallation"
echo "==================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Error: Please do not run this script as root."
    echo "The script will ask for sudo password when needed."
    exit 1
fi

read -p "Are you sure you want to uninstall Kerio VPN Indicator? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Stop the indicator if running
echo "Stopping indicator..."
pkill -f kerio-vpn-indicator || true

# Remove the script
if [ -f "/usr/local/bin/kerio-vpn-indicator" ]; then
    echo "Removing kerio-vpn-indicator..."
    sudo rm /usr/local/bin/kerio-vpn-indicator
    echo "✓ Removed"
fi

# Remove autostart entry
if [ -f "$HOME/.config/autostart/kerio-vpn-indicator.desktop" ]; then
    echo "Removing autostart entry..."
    rm "$HOME/.config/autostart/kerio-vpn-indicator.desktop"
    echo "✓ Removed"
fi

# Ask about sudoers rules
if [ -f "/etc/sudoers.d/kerio-vpn" ]; then
    echo ""
    read -p "Remove sudoers rules? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm /etc/sudoers.d/kerio-vpn
        echo "✓ Removed sudoers rules"
    fi
fi

echo ""
echo "==================================="
echo "Uninstallation Complete!"
echo "==================================="
echo ""
