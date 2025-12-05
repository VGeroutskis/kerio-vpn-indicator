#!/usr/bin/env python3
"""
Kerio VPN System Tray Indicator
A universal system tray application for Kerio Control VPN
Works on: XFCE, MATE, Cinnamon, LXDE, LXQt, and GNOME (fallback)
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
import subprocess
import os
import signal
import sys
import time
from datetime import datetime
import xml.etree.ElementTree as ET
import html

class KerioVPNIndicator:
    def __init__(self):
        self.app_id = 'kerio-vpn-indicator'
        
        # Create indicator
        self.indicator = AppIndicator3.Indicator.new(
            self.app_id,
            'network-offline',
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # State variables
        self.is_connected = False
        self.connection_start_time = None
        self.vpn_ip = None
        self.vpn_server = None
        self.auto_reconnect_enabled = True
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        self.manual_disconnect = False  # Track manual disconnects
        
        # Load config
        self.config_file = '/etc/kerio-kvc.conf'
        self.load_config()
        
        # Create menu
        self.menu = Gtk.Menu()
        self.build_menu()
        self.indicator.set_menu(self.menu)
        
        # Start monitoring
        GLib.timeout_add_seconds(2, self.update_status)
        
    def load_config(self):
        """Load VPN server info from Kerio config"""
        try:
            if os.path.exists(self.config_file):
                tree = ET.parse(self.config_file)
                root = tree.getroot()
                
                connection = root.find('.//connection[@type="persistent"]')
                if connection is not None:
                    server = connection.find('server')
                    port = connection.find('port')
                    
                    if server is not None and server.text:
                        self.vpn_server = html.unescape(server.text)
                        if port is not None and port.text:
                            self.vpn_server += f":{port.text}"
        except Exception as e:
            print(f"Error loading config: {e}")
            self.vpn_server = "Unknown"
    
    def build_menu(self):
        """Build the indicator menu"""
        # Status item
        self.status_item = Gtk.MenuItem(label="VPN: Disconnected")
        self.status_item.set_sensitive(False)
        self.menu.append(self.status_item)
        
        # Connection info item
        self.info_item = Gtk.MenuItem(label="No connection info")
        self.info_item.set_sensitive(False)
        self.menu.append(self.info_item)
        
        # Separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Connect/Disconnect
        self.connect_item = Gtk.MenuItem(label="Connect")
        self.connect_item.connect('activate', self.on_toggle_connection)
        self.menu.append(self.connect_item)
        
        # Reconnect
        self.reconnect_item = Gtk.MenuItem(label="Reconnect")
        self.reconnect_item.connect('activate', self.on_reconnect)
        self.reconnect_item.set_sensitive(False)
        self.menu.append(self.reconnect_item)
        
        # Separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Auto-reconnect toggle
        self.auto_reconnect_item = Gtk.CheckMenuItem(label="Auto-reconnect")
        self.auto_reconnect_item.set_active(True)
        self.auto_reconnect_item.connect('toggled', self.on_auto_reconnect_toggled)
        self.menu.append(self.auto_reconnect_item)
        
        # Separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Copy IP
        self.copy_ip_item = Gtk.MenuItem(label="Copy IP Address")
        self.copy_ip_item.connect('activate', self.on_copy_ip)
        self.copy_ip_item.set_sensitive(False)
        self.menu.append(self.copy_ip_item)
        
        # View logs
        logs_item = Gtk.MenuItem(label="View Logs")
        logs_item.connect('activate', self.on_view_logs)
        self.menu.append(logs_item)
        
        # Settings
        settings_item = Gtk.MenuItem(label="Settings...")
        settings_item.connect('activate', self.on_settings)
        self.menu.append(settings_item)
        
        # Separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect('activate', self.on_quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
    
    def update_menu(self):
        """Update menu items based on connection state"""
        if self.is_connected:
            self.status_item.set_label("VPN: Connected ✓")
            self.connect_item.set_label("Disconnect")
            self.reconnect_item.set_sensitive(True)
            self.copy_ip_item.set_sensitive(True)
            self.indicator.set_icon('network-transmit-receive')
            
            # Update connection info
            info_parts = []
            if self.vpn_ip:
                info_parts.append(f"IP: {self.vpn_ip}")
            if self.vpn_server:
                info_parts.append(f"Server: {self.vpn_server}")
            if self.connection_start_time:
                duration = self.get_connection_duration()
                info_parts.append(f"Duration: {duration}")
            
            self.info_item.set_label(" | ".join(info_parts) if info_parts else "Connected")
        else:
            self.status_item.set_label("VPN: Disconnected")
            self.connect_item.set_label("Connect")
            self.reconnect_item.set_sensitive(False)
            self.copy_ip_item.set_sensitive(False)
            self.indicator.set_icon('network-offline')
            self.info_item.set_label("Not connected")
            self.connection_start_time = None
            self.vpn_ip = None
    
    def get_connection_duration(self):
        """Get formatted connection duration"""
        if not self.connection_start_time:
            return "00:00:00"
        
        duration = int(time.time() - self.connection_start_time)
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def update_status(self):
        """Check VPN status and update indicator"""
        was_connected = self.is_connected
        
        # Check service status
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', 'kerio-kvc.service'],
                capture_output=True,
                text=True,
                timeout=5
            )
            service_active = result.returncode == 0
        except:
            service_active = False
        
        # Check network interface
        interface_up = False
        vpn_ip = None
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show', 'kvnet'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                interface_up = True
                # Extract IP address
                for line in result.stdout.split('\n'):
                    if 'inet ' in line:
                        vpn_ip = line.strip().split()[1].split('/')[0]
                        break
        except:
            pass
        
        # Update connection state
        self.is_connected = service_active and interface_up
        
        if self.is_connected:
            self.vpn_ip = vpn_ip
            if not was_connected:
                self.connection_start_time = time.time()
                self.reconnect_attempts = 0
                self.manual_disconnect = False  # Reset manual disconnect flag
                self.show_notification("Kerio VPN Connected", 
                                     f"VPN connection established\nIP: {vpn_ip}")
        else:
            if was_connected:
                self.show_notification("Kerio VPN Disconnected", 
                                     "VPN connection lost")
                
                # Auto-reconnect logic - only if not manually disconnected
                if (self.auto_reconnect_enabled and 
                    not self.manual_disconnect and 
                    self.reconnect_attempts < self.max_reconnect_attempts):
                    self.reconnect_attempts += 1
                    GLib.timeout_add_seconds(3, self.auto_reconnect)
        
        self.update_menu()
        return True  # Keep the timeout running
    
    def auto_reconnect(self):
        """Attempt to reconnect automatically"""
        print(f"Auto-reconnect attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        self.show_notification("Kerio VPN", 
                             f"Auto-reconnecting... (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        self.connect_vpn()
        return False  # Don't repeat this timeout
    
    def connect_vpn(self):
        """Start VPN connection"""
        try:
            self.manual_disconnect = False  # Clear manual disconnect flag when connecting
            subprocess.run(
                ['sudo', 'systemctl', 'start', 'kerio-kvc.service'],
                check=True,
                timeout=10
            )
            return True
        except Exception as e:
            self.show_notification("Kerio VPN Error", f"Failed to start VPN: {e}")
            return False
    
    def disconnect_vpn(self):
        """Stop VPN connection"""
        try:
            self.manual_disconnect = True  # Set flag to prevent auto-reconnect
            subprocess.run(
                ['sudo', 'systemctl', 'stop', 'kerio-kvc.service'],
                check=True,
                timeout=10
            )
            return True
        except Exception as e:
            self.show_notification("Kerio VPN Error", f"Failed to stop VPN: {e}")
            return False
    
    def show_notification(self, title, message):
        """Show desktop notification"""
        try:
            subprocess.run(
                ['notify-send', '-i', 'network-vpn', title, message],
                timeout=5
            )
        except:
            pass
    
    def on_toggle_connection(self, widget):
        """Handle connect/disconnect action"""
        if self.is_connected:
            self.disconnect_vpn()
        else:
            self.connect_vpn()
    
    def on_reconnect(self, widget):
        """Handle reconnect action"""
        self.manual_disconnect = False  # Clear flag for reconnect
        self.disconnect_vpn()
        GLib.timeout_add_seconds(2, lambda: self.connect_vpn())
    
    def on_auto_reconnect_toggled(self, widget):
        """Handle auto-reconnect toggle"""
        self.auto_reconnect_enabled = widget.get_active()
        if self.auto_reconnect_enabled:
            self.reconnect_attempts = 0
    
    def on_copy_ip(self, widget):
        """Copy VPN IP to clipboard"""
        if self.vpn_ip:
            try:
                clipboard = Gtk.Clipboard.get(Gtk.gdk.SELECTION_CLIPBOARD)
                clipboard.set_text(self.vpn_ip, -1)
                clipboard.store()
                self.show_notification("Kerio VPN", f"IP address copied: {self.vpn_ip}")
            except:
                pass
    
    def on_view_logs(self, widget):
        """Open logs in terminal"""
        try:
            subprocess.Popen(
                ['gnome-terminal', '--', 'bash', '-c', 
                 'journalctl -u kerio-kvc.service -f; exec bash']
            )
        except:
            try:
                subprocess.Popen(
                    ['xfce4-terminal', '-e', 
                     'bash -c "journalctl -u kerio-kvc.service -f; exec bash"']
                )
            except:
                try:
                    subprocess.Popen(
                        ['xterm', '-e', 
                         'bash -c "journalctl -u kerio-kvc.service -f; exec bash"']
                    )
                except:
                    pass
    
    def on_settings(self, widget):
        """Open settings editor"""
        try:
            subprocess.Popen(['kerio-config-editor'])
        except Exception as e:
            self.show_notification("Error", f"Could not open settings: {e}")
    
    def on_quit(self, widget):
        """Quit the indicator"""
        Gtk.main_quit()

def main():
    # Handle signals
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Create indicator
    indicator = KerioVPNIndicator()
    
    # Run GTK main loop
    Gtk.main()

if __name__ == '__main__':
    main()
