#!/usr/bin/env python3
"""
Kerio VPN Configuration Editor
GUI tool to edit /etc/kerio-kvc.conf settings
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import xml.etree.ElementTree as ET
import html
import subprocess
import os
import sys

class KerioConfigEditor(Gtk.Window):
    def __init__(self):
        super().__init__(title="Kerio VPN Configuration")
        self.set_default_size(500, 400)
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        self.config_file = '/etc/kerio-kvc.conf'
        
        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)
        
        # Header
        header = Gtk.Label()
        header.set_markup("<big><b>Kerio VPN Connection Settings</b></big>")
        header.set_margin_bottom(10)
        vbox.pack_start(header, False, False, 0)
        
        # Form grid
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_start(20)
        grid.set_margin_end(20)
        vbox.pack_start(grid, True, True, 0)
        
        # Server
        label = Gtk.Label(label="VPN Server:", xalign=0)
        grid.attach(label, 0, 0, 1, 1)
        self.server_entry = Gtk.Entry()
        self.server_entry.set_placeholder_text("vpn.example.com or IP address")
        self.server_entry.set_hexpand(True)
        grid.attach(self.server_entry, 1, 0, 1, 1)
        
        # Port
        label = Gtk.Label(label="Port:", xalign=0)
        grid.attach(label, 0, 1, 1, 1)
        self.port_entry = Gtk.Entry()
        self.port_entry.set_placeholder_text("4090")
        self.port_entry.set_max_length(5)
        self.port_entry.set_width_chars(10)
        grid.attach(self.port_entry, 1, 1, 1, 1)
        
        # Username
        label = Gtk.Label(label="Username:", xalign=0)
        grid.attach(label, 0, 2, 1, 1)
        self.username_entry = Gtk.Entry()
        self.username_entry.set_placeholder_text("your_username")
        grid.attach(self.username_entry, 1, 2, 1, 1)
        
        # Password
        label = Gtk.Label(label="Password:", xalign=0)
        grid.attach(label, 0, 3, 1, 1)
        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("your_password")
        self.password_entry.set_visibility(False)
        self.password_entry.set_invisible_char('●')
        grid.attach(self.password_entry, 1, 3, 1, 1)
        
        # Show password checkbox
        self.show_password = Gtk.CheckButton(label="Show password")
        self.show_password.connect("toggled", self.on_show_password_toggled)
        grid.attach(self.show_password, 1, 4, 1, 1)
        
        # Description
        label = Gtk.Label(label="Description:", xalign=0)
        grid.attach(label, 0, 5, 1, 1)
        self.description_entry = Gtk.Entry()
        self.description_entry.set_placeholder_text("My VPN Connection")
        grid.attach(self.description_entry, 1, 5, 1, 1)
        
        # Auto-connect
        self.autoconnect_check = Gtk.CheckButton(label="Connect automatically on service start")
        self.autoconnect_check.set_active(True)
        grid.attach(self.autoconnect_check, 0, 6, 2, 1)
        
        # Status label
        self.status_label = Gtk.Label(label="")
        self.status_label.set_margin_top(10)
        vbox.pack_start(self.status_label, False, False, 0)
        
        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_margin_top(10)
        vbox.pack_start(button_box, False, False, 0)
        
        # Load button
        load_button = Gtk.Button(label="Load Current Settings")
        load_button.connect("clicked", self.on_load_clicked)
        button_box.pack_start(load_button, True, True, 0)
        
        # Save button
        save_button = Gtk.Button(label="Save & Apply")
        save_button.get_style_context().add_class("suggested-action")
        save_button.connect("clicked", self.on_save_clicked)
        button_box.pack_start(save_button, True, True, 0)
        
        # Test connection button
        test_button = Gtk.Button(label="Test Connection")
        test_button.connect("clicked", self.on_test_clicked)
        button_box.pack_start(test_button, True, True, 0)
        
        # Close button
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", lambda w: self.destroy())
        button_box.pack_start(close_button, True, True, 0)
        
        # Load current config after window is shown
        self.connect("realize", lambda w: GLib.timeout_add(100, self.load_config))
        
    def on_show_password_toggled(self, widget):
        """Toggle password visibility"""
        self.password_entry.set_visibility(widget.get_active())
    
    def decode_html_entities(self, text):
        """Decode HTML entities like &#33; -> !"""
        if not text:
            return text
        return html.unescape(text)
    
    def encode_html_entities(self, text):
        """Encode special characters as HTML entities"""
        if not text:
            return text
        
        # Characters that need encoding
        # Note: We don't encode & and # since we use them in the entity format &#XX;
        special_chars = {
            '!': '&#33;', '"': '&#34;', '$': '&#36;',
            '%': '&#37;', "'": '&#39;', '<': '&#60;',
            '>': '&#62;', '@': '&#64;', '\\': '&#92;'
        }
        
        result = []
        for char in text:
            if char in special_chars:
                result.append(special_chars[char])
            else:
                result.append(char)
        return ''.join(result)
    
    def load_config(self):
        """Load configuration from /etc/kerio-kvc.conf"""
        try:
            # Read config file with sudo
            result = subprocess.run(
                ['sudo', 'cat', self.config_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.show_status("Configuration file not found. Please fill in the settings.", "warning")
                return False
            
            # Parse XML from string
            root = ET.fromstring(result.stdout)
            
            connection = root.find('.//connection[@type="persistent"]')
            if connection is not None:
                # Load values
                server = connection.find('server')
                if server is not None and server.text:
                    server_text = self.decode_html_entities(server.text)
                    # Check if port is included in server (format: server:port)
                    if ':' in server_text:
                        server_parts = server_text.rsplit(':', 1)
                        self.server_entry.set_text(server_parts[0])
                        self.port_entry.set_text(server_parts[1])
                    else:
                        self.server_entry.set_text(server_text)
                
                # Check for separate port element
                port = connection.find('port')
                if port is not None and port.text:
                    self.port_entry.set_text(port.text)
                
                username = connection.find('username')
                if username is not None and username.text:
                    self.username_entry.set_text(self.decode_html_entities(username.text))
                
                password = connection.find('password')
                if password is not None and password.text:
                    self.password_entry.set_text(self.decode_html_entities(password.text))
                
                description = connection.find('description')
                if description is not None and description.text:
                    self.description_entry.set_text(self.decode_html_entities(description.text))
                
                # Handle both 'yes'/'no' and '1'/'0' for active
                active = connection.find('active')
                if active is not None and active.text:
                    active_value = active.text.strip().lower()
                    self.autoconnect_check.set_active(active_value in ['yes', '1', 'true'])
                
                self.show_status("Configuration loaded successfully", "success")
            else:
                self.show_status("No persistent connection found in config", "warning")
                
        except Exception as e:
            self.show_status(f"Error loading config: {e}", "error")
            return False
        
        return False  # Don't repeat the timeout
    
    def save_config(self):
        """Save configuration to /etc/kerio-kvc.conf"""
        # Validate inputs
        server = self.server_entry.get_text().strip()
        port = self.port_entry.get_text().strip()
        username = self.username_entry.get_text().strip()
        password = self.password_entry.get_text()
        
        if not server:
            self.show_status("Server is required", "error")
            return False
        
        if not port:
            port = "4090"
        
        if not username:
            self.show_status("Username is required", "error")
            return False
        
        if not password:
            self.show_status("Password is required", "error")
            return False
        
        # Build XML manually to avoid double-encoding
        xml_lines = ['<config>', '  <connections>', '    <connection type="persistent">']
        
        xml_lines.append(f'      <server>{self.encode_html_entities(server)}:{port}</server>')
        xml_lines.append(f'      <username>{self.encode_html_entities(username)}</username>')
        xml_lines.append(f'      <password>{self.encode_html_entities(password)}</password>')
        
        # Get server fingerprint using openssl
        fingerprint = None
        try:
            # First try to preserve existing fingerprint
            result = subprocess.run(['sudo', 'cat', self.config_file], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                root = ET.fromstring(result.stdout)
                connection = root.find('.//connection[@type="persistent"]')
                if connection is not None:
                    fp_elem = connection.find('fingerprint')
                    if fp_elem is not None and fp_elem.text:
                        fingerprint = fp_elem.text
        except:
            pass
        
        # If no existing fingerprint, try to get it from the server
        if not fingerprint:
            try:
                print(f"Getting fingerprint from {server}:{port}...")
                # Get the server certificate and calculate fingerprint
                # Use echo to close stdin immediately
                result = subprocess.run(
                    f'echo | openssl s_client -connect {server}:{port} -showcerts 2>/dev/null',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.stdout:
                    # Extract the certificate - openssl outputs to stdout
                    cert_lines = []
                    in_cert = False
                    for line in result.stdout.split('\n'):
                        if '-----BEGIN CERTIFICATE-----' in line:
                            in_cert = True
                            cert_lines = [line]
                        elif in_cert:
                            cert_lines.append(line)
                            if '-----END CERTIFICATE-----' in line:
                                break
                    
                    if cert_lines:
                        cert_text = '\n'.join(cert_lines)
                        # Calculate SHA1 fingerprint
                        result = subprocess.run(
                            ['openssl', 'x509', '-noout', '-fingerprint', '-sha1'],
                            input=cert_text,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        if result.returncode == 0 and result.stdout:
                            # Extract fingerprint from output like "SHA1 Fingerprint=XX:XX:XX:..."
                            for line in result.stdout.split('\n'):
                                if 'Fingerprint=' in line:
                                    fingerprint = line.split('=')[1].strip()
                                    print(f"Got fingerprint: {fingerprint}")
                                    break
            except Exception as e:
                print(f"Could not get fingerprint: {e}")
                # Continue without fingerprint - Kerio will handle it
        
        if fingerprint:
            xml_lines.append(f'      <fingerprint>{fingerprint}</fingerprint>')
        
        xml_lines.append(f'      <active>{"1" if self.autoconnect_check.get_active() else "0"}</active>')
        
        description = self.description_entry.get_text().strip()
        if description:
            xml_lines.append(f'      <description>{self.encode_html_entities(description)}</description>')
        
        xml_lines.extend(['    </connection>', '  </connections>', '</config>'])
        
        xml_content = '\n'.join(xml_lines) + '\n'
        
        # Write to temporary file
        temp_file = '/tmp/kerio-kvc.conf.tmp'
        try:
            with open(temp_file, 'w') as f:
                f.write(xml_content)
            
            # Move to final location with sudo
            result = subprocess.run(
                ['sudo', 'mv', temp_file, self.config_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.show_status(f"Error saving config: {result.stderr}", "error")
                return False
            
            # Set proper permissions
            subprocess.run(['sudo', 'chmod', '600', self.config_file], timeout=5)
            
            self.show_status("Configuration saved successfully", "success")
            return True
            
        except Exception as e:
            self.show_status(f"Error saving config: {e}", "error")
            return False
    
    def restart_service(self):
        """Restart Kerio VPN service"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', 'kerio-kvc.service'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.show_status("VPN service restarted successfully", "success")
                return True
            else:
                self.show_status(f"Error restarting service: {result.stderr}", "error")
                return False
                
        except Exception as e:
            self.show_status(f"Error restarting service: {e}", "error")
            return False
    
    def show_status(self, message, status_type="info"):
        """Show status message with color"""
        if status_type == "success":
            markup = f'<span foreground="green">✓ {message}</span>'
        elif status_type == "error":
            markup = f'<span foreground="red">✗ {message}</span>'
        elif status_type == "warning":
            markup = f'<span foreground="orange">⚠ {message}</span>'
        else:
            markup = message
        
        self.status_label.set_markup(markup)
    
    def on_load_clicked(self, widget):
        """Load button clicked"""
        self.load_config()
    
    def on_save_clicked(self, widget):
        """Save button clicked"""
        if self.save_config():
            # Ask if user wants to restart service
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Restart VPN Service?"
            )
            dialog.format_secondary_text(
                "Configuration saved. Do you want to restart the VPN service now to apply changes?"
            )
            
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                self.restart_service()
    
    def on_test_clicked(self, widget):
        """Test connection button clicked"""
        print("Test connection button clicked")
        
        # Save first
        if not self.save_config():
            print("Config save failed, aborting test")
            return
        
        print("Config saved, restarting service...")
        self.show_status("Restarting VPN service...", "info")
        
        # Try to restart service
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', 'kerio-kvc.service'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"Service restart failed: {result.stderr}")
                self.show_status(f"Failed to restart service: {result.stderr}", "error")
                return
            
            print("Service restarted successfully, starting connection check...")
            self.show_status("Testing connection...", "info")
            
            # Initialize test counters
            self.test_check_count = 0
            self.test_max_attempts = 10
            
            # Start checking connection status
            GLib.timeout_add_seconds(2, self.check_connection_status)
            
        except subprocess.TimeoutExpired:
            print("Service restart timeout")
            self.show_status("Service restart timeout", "error")
        except Exception as e:
            print(f"Service restart error: {e}")
            self.show_status(f"Connection test failed: {e}", "error")
    
    def check_connection_status(self):
        """Check if VPN connected successfully - returns True to continue, False to stop"""
        self.test_check_count += 1
        print(f"\nConnection check attempt {self.test_check_count}/{self.test_max_attempts}")
        
        try:
            # Step 1: Check if service is running
            print("  Checking service status...")
            result = subprocess.run(
                ['systemctl', 'is-active', 'kerio-kvc.service'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            service_status = result.stdout.strip()
            print(f"  Service status: {service_status} (returncode={result.returncode})")
            
            if result.returncode != 0:
                print(f"  Service not active")
                self.show_status("Service not active - check credentials and server", "error")
                return False  # Stop checking
            
            # Step 2: Check if interface exists and is up
            print("  Checking interface kvnet...")
            result = subprocess.run(
                ['ip', 'addr', 'show', 'kvnet'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print(f"  Interface kvnet not found")
                if self.test_check_count < self.test_max_attempts:
                    self.show_status(f"Waiting for interface... ({self.test_check_count}/{self.test_max_attempts})", "info")
                    return True  # Continue checking
                else:
                    self.show_status("Timeout - VPN interface not created", "error")
                    return False  # Stop checking
            
            # Step 3: Extract IP address
            print("  Interface found, looking for IP address...")
            ip_found = None
            for line in result.stdout.split('\n'):
                if 'inet ' in line and 'inet6' not in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip_found = parts[1].split('/')[0]
                        print(f"  Found IP: {ip_found}")
                        break
            
            if ip_found:
                print(f"  SUCCESS! VPN connected with IP {ip_found}")
                self.show_status(f"✓ Connection successful! VPN IP: {ip_found}", "success")
                return False  # Stop checking
            else:
                print(f"  No IP address assigned yet")
                if self.test_check_count < self.test_max_attempts:
                    self.show_status(f"Connecting... ({self.test_check_count}/{self.test_max_attempts})", "info")
                    return True  # Continue checking
                else:
                    print(f"  TIMEOUT - No IP after {self.test_max_attempts} attempts")
                    self.show_status("Timeout - VPN did not get IP address", "error")
                    return False  # Stop checking
                
        except subprocess.TimeoutExpired:
            print(f"  Command timeout")
            self.show_status("Check timeout - command took too long", "error")
            return False  # Stop checking
        except Exception as e:
            print(f"  Error during check: {e}")
            self.show_status(f"Error checking status: {e}", "error")
            return False  # Stop checking

def main():
    # Check if running in terminal
    if not os.isatty(0):
        # Not in terminal, might need pkexec for sudo
        pass
    
    win = KerioConfigEditor()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
