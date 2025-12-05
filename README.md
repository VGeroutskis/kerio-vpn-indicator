# Kerio VPN System Tray Indicator

A universal system tray indicator for **Kerio Control VPN Client** that works across all major Linux desktop environments.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)

## Features

✅ **Universal Desktop Environment Support**
- XFCE, MATE, Cinnamon, LXDE, LXQt
- GNOME (via AppIndicator fallback)
- KDE Plasma (via system tray)
- Any DE with system tray support

✅ **VPN Management**
- One-click connect/disconnect
- Real-time connection status
- Connection duration timer
- VPN IP address display
- Server information
- **Graphical settings editor** for server, username, password, port

✅ **Smart Features**
- Auto-reconnect on disconnect (configurable)
- Desktop notifications
- Quick IP copy to clipboard
- Service log viewer
- Passwordless operation (optional)

✅ **Lightweight**
- Python-based (~350 lines)
- Minimal dependencies
- Low resource usage
- Auto-start on login

## Screenshots

*System tray indicator showing VPN status*

## Supported Desktop Environments

| Desktop Environment | Status | Notes |
|---------------------|--------|-------|
| XFCE | ✅ Native | Full AppIndicator support |
| MATE | ✅ Native | Full AppIndicator support |
| Cinnamon | ✅ Native | Full AppIndicator support |
| LXDE | ✅ Native | System tray support |
| LXQt | ✅ Native | System tray support |
| GNOME | ✅ Fallback | Requires AppIndicator extension |
| KDE Plasma | ✅ Native | System tray support |
| Budgie | ✅ Native | AppIndicator support |
| Pantheon | ✅ Native | AppIndicator support |

## Prerequisites

### 1. Kerio Control VPN Client

You must have Kerio Control VPN Client installed. See the [installation guide below](#installing-kerio-control-vpn-client).

### 2. System Dependencies

**Ubuntu / Debian / Linux Mint / Pop!_OS:**
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

**Fedora / RHEL / CentOS / Rocky Linux / AlmaLinux:**
```bash
sudo dnf install python3-gobject gtk3 libappindicator-gtk3
```

**Arch Linux / Manjaro / EndeavourOS:**
```bash
sudo pacman -S python-gobject gtk3 libappindicator-gtk3
```

**openSUSE / SUSE Linux Enterprise:**
```bash
sudo zypper install python3-gobject-Gdk typelib-1_0-Gtk-3_0 typelib-1_0-AppIndicator3-0_1
```

**For GNOME users:** Install the AppIndicator extension:
```bash
# GNOME 45+ (Ubuntu 24.04+, Fedora 40+)
gnome-extensions install appindicatorsupport@rgcjonas.gmail.com
gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com
```

Or install via GNOME Extensions website: [AppIndicator Support](https://extensions.gnome.org/extension/615/appindicator-support/)

## Installation

### Quick Install

```bash
git clone https://github.com/VGeroutskis/kerio-vpn-indicator.git
cd kerio-vpn-indicator
./install.sh
```

The indicator will:
- Install to `/usr/local/bin/kerio-vpn-indicator`
- Add autostart entry for your desktop environment
- Optionally set up passwordless VPN control

### Manual Installation

1. Copy the script:
```bash
sudo cp kerio-vpn-indicator.py /usr/local/bin/kerio-vpn-indicator
sudo chmod +x /usr/local/bin/kerio-vpn-indicator
```

2. Add autostart entry:
```bash
mkdir -p ~/.config/autostart
cp kerio-vpn-indicator.desktop ~/.config/autostart/
```

3. Set up passwordless operation (optional):
```bash
sudo visudo -c -f kerio-vpn-sudoers
sudo cp kerio-vpn-sudoers /etc/sudoers.d/kerio-vpn
sudo chmod 440 /etc/sudoers.d/kerio-vpn
```

4. Start the indicator:
```bash
kerio-vpn-indicator &
```

Or log out and log back in for autostart.

## Usage

### Starting the Indicator

The indicator starts automatically on login. To start it manually:

```bash
kerio-vpn-indicator &
```

### Features

**Left-click** on the system tray icon to open the menu:

- **VPN Status** - Shows current connection state
- **Connection Info** - IP address, server, and duration
- **Connect/Disconnect** - Toggle VPN connection
- **Reconnect** - Force reconnection
- **Auto-reconnect** - Enable/disable automatic reconnection (up to 3 attempts)
- **Copy IP Address** - Copy your VPN IP to clipboard
- **View Logs** - Open service logs in terminal
- **Settings** - Edit VPN connection settings (server, port, credentials)
- **Quit** - Close the indicator

### VPN Settings Editor

Click **Settings...** in the menu or run `kerio-config-editor` to open the graphical settings editor:

- Edit server address, port, username, and password
- Test connection with one click
- Auto-save and apply changes
- Password visibility toggle
- Load current settings from config file

### Keyboard Shortcuts

The indicator is designed for mouse interaction, but you can control the VPN via terminal:

```bash
# Connect
sudo systemctl start kerio-kvc.service

# Disconnect
sudo systemctl stop kerio-kvc.service

# Status
systemctl status kerio-kvc.service
```

## Installing Kerio Control VPN Client

Before using the indicator, you need to install Kerio Control VPN Client.

### Download Kerio VPN Client

Download the DEB package from the official Kerio Control VPN resources page:

**Download Link**: [Kerio Control VPN Client](https://gfi.ai/products-and-solutions/network-security-solutions/keriocontrol/resources/vpn)

**Note**: Kerio officially provides only **.deb** packages for Linux. For other distributions, you'll need to convert the package or extract it manually.

### Installation by Distribution

#### Ubuntu / Debian / Linux Mint / Pop!_OS / Zorin OS

```bash
# Download the DEB package (replace with actual version)
wget https://cdn.kerio.com/dwn/control/control-<version>/kerio-control-vpnclient-<version>-linux-amd64.deb

# Install the package
sudo apt install ./kerio-control-vpnclient-<version>-linux-amd64.deb
```

#### Fedora / RHEL / CentOS / Rocky Linux / AlmaLinux

Convert the DEB package using `alien`:

```bash
sudo dnf install alien
wget https://cdn.kerio.com/dwn/control/control-<version>/kerio-control-vpnclient-<version>-linux-amd64.deb
sudo alien -r kerio-control-vpnclient-<version>-linux-amd64.deb
sudo dnf install kerio-control-vpnclient-<version>-1.x86_64.rpm
```

#### Arch Linux / Manjaro / EndeavourOS

```bash
# Using debtap
yay -S debtap
sudo debtap -u
wget https://cdn.kerio.com/dwn/control/control-<version>/kerio-control-vpnclient-<version>-linux-amd64.deb
debtap kerio-control-vpnclient-<version>-linux-amd64.deb
sudo pacman -U kerio-control-vpnclient-<version>-1-x86_64.pkg.tar.zst
```

#### Generic Linux (Manual Extraction)

```bash
# Download and extract
wget https://cdn.kerio.com/dwn/control/control-<version>/kerio-control-vpnclient-<version>-linux-amd64.deb
ar x kerio-control-vpnclient-<version>-linux-amd64.deb
tar xf data.tar.xz

# Install files
sudo cp -r usr /
sudo cp -r etc /
sudo systemctl daemon-reload
```

### Configure Kerio VPN

Edit `/etc/kerio-kvc.conf`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<config>
  <connections>
    <connection type="persistent">
      <server>vpn.example.com</server>
      <port>4090</port>
      <username>your_username</username>
      <password>your_password</password>
      <active>yes</active>
      <description>My VPN Connection</description>
    </connection>
  </connections>
</config>
```

## Troubleshooting

### Indicator doesn't appear in system tray

**GNOME users**: Install the AppIndicator extension:
```bash
gnome-extensions install appindicatorsupport@rgcjonas.gmail.com
gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com
```

**Other DEs**: Check if `gir1.2-appindicator3-0.1` is installed.

### Password prompts when connecting

Install the sudoers rules:
```bash
cd kerio-vpn-indicator
sudo cp kerio-vpn-sudoers /etc/sudoers.d/kerio-vpn
sudo chmod 440 /etc/sudoers.d/kerio-vpn
```

### VPN connects but indicator shows disconnected

The indicator checks for the `kvnet` network interface. Verify:
```bash
ip addr show kvnet
```

If your interface has a different name, edit `/usr/local/bin/kerio-vpn-indicator` and change `kvnet` to your interface name.

### Connection logs

View Kerio VPN logs:
```bash
journalctl -u kerio-kvc.service -f
```

Or use the "View Logs" menu option in the indicator.

## Uninstallation

```bash
cd kerio-vpn-indicator
./uninstall.sh
```

Or manually:
```bash
# Stop the indicator
pkill -f kerio-vpn-indicator

# Remove files
sudo rm /usr/local/bin/kerio-vpn-indicator
rm ~/.config/autostart/kerio-vpn-indicator.desktop
sudo rm /etc/sudoers.d/kerio-vpn  # Optional
```

## Comparison with GNOME Extension

| Feature | System Tray Indicator | GNOME Extension |
|---------|----------------------|-----------------|
| Desktop Environments | All (XFCE, MATE, etc.) | GNOME only |
| Installation | Simple Python script | GNOME Shell extension |
| Dependencies | Minimal | GNOME Shell API |
| Updates | No GNOME version issues | Must match GNOME version |
| Performance | Lightweight | Integrated with Shell |

**Use the indicator if:**
- You use XFCE, MATE, Cinnamon, or other non-GNOME DEs
- You want a simpler, more portable solution
- You frequently switch desktop environments

**Use the GNOME extension if:**
- You use GNOME Shell exclusively
- You prefer native Shell integration
- You want panel button instead of system tray icon

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Kerio VPN GNOME Extension](https://github.com/VGeroutskis/kerio-vpn-extension) - Native GNOME Shell extension

## Author

**Vasilis Geroutskis**

## Acknowledgments

- Kerio Technologies for the VPN client
- The GTK and AppIndicator communities
