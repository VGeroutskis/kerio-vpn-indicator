#!/bin/bash

# Kerio VPN Indicator Installation Script

set -e

echo "==================================="
echo "Kerio VPN Indicator Installation"
echo "==================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Error: Please do not run this script as root."
    echo "The script will ask for sudo password when needed."
    exit 1
fi

# Check if Kerio VPN Client is installed
if ! systemctl list-unit-files | grep -q kerio-kvc.service; then
    echo "Warning: Kerio VPN Client (kerio-kvc.service) not found."
    echo "Please install Kerio Control VPN Client first."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for required dependencies
echo "Checking dependencies..."
MISSING_DEPS=()

# Check Python 3
if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi

# Check for GTK and AppIndicator libraries
if ! python3 -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('AppIndicator3', '0.1')" 2>/dev/null; then
    echo "Missing GTK3 or AppIndicator3 libraries."
    echo ""
    echo "Please install the required packages:"
    echo ""
    echo "Ubuntu/Debian/Mint:"
    echo "  sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1"
    echo ""
    echo "Fedora/RHEL:"
    echo "  sudo dnf install python3-gobject gtk3 libappindicator-gtk3"
    echo ""
    echo "Arch/Manjaro:"
    echo "  sudo pacman -S python-gobject gtk3 libappindicator-gtk3"
    echo ""
    echo "openSUSE:"
    echo "  sudo zypper install python3-gobject-Gdk typelib-1_0-Gtk-3_0 typelib-1_0-AppIndicator3-0_1"
    echo ""
    exit 1
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "Error: Missing dependencies: ${MISSING_DEPS[*]}"
    exit 1
fi

echo "All dependencies satisfied."
echo ""

# Install the indicator script
echo "Installing kerio-vpn-indicator..."
sudo cp kerio-vpn-indicator.py /usr/local/bin/kerio-vpn-indicator
sudo chmod +x /usr/local/bin/kerio-vpn-indicator
echo "✓ Installed to /usr/local/bin/kerio-vpn-indicator"

# Install the config editor
echo "Installing kerio-config-editor..."
sudo cp kerio-config-editor.py /usr/local/bin/kerio-config-editor
sudo chmod +x /usr/local/bin/kerio-config-editor
echo "✓ Installed to /usr/local/bin/kerio-config-editor"

# Install desktop files
echo "Installing desktop files..."
sudo cp kerio-config-editor.desktop /usr/share/applications/
echo "✓ Installed settings application menu entry"

# Install desktop file for autostart
echo "Installing autostart entry..."
mkdir -p ~/.config/autostart
cp kerio-vpn-indicator.desktop ~/.config/autostart/
echo "✓ Installed autostart entry"

# Install sudoers rules if they exist
if [ -f "kerio-vpn-sudoers" ]; then
    echo "Installing sudoers rules for passwordless operation..."
    sudo visudo -c -f kerio-vpn-sudoers
    if [ $? -eq 0 ]; then
        sudo cp kerio-vpn-sudoers /etc/sudoers.d/kerio-vpn
        sudo chmod 440 /etc/sudoers.d/kerio-vpn
        echo "✓ Installed sudoers rules"
    else
        echo "Warning: sudoers file has syntax errors. Skipping."
    fi
fi

echo ""
echo "==================================="
echo "Installation Complete!"
echo "==================================="
echo ""
echo "The indicator will start automatically on next login."
echo "To start it now, run:"
echo "  kerio-vpn-indicator &"
echo ""
echo "Or log out and log back in."
echo ""
