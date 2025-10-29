#!/bin/bash
# UniFi Network Pro - Installation Script for Home Assistant
# This script automates the installation process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Detect Home Assistant config directory
detect_ha_config() {
    if [ -d "/config" ]; then
        echo "/config"
    elif [ -d "/usr/share/hassio/homeassistant" ]; then
        echo "/usr/share/hassio/homeassistant"
    elif [ -d "$HOME/.homeassistant" ]; then
        echo "$HOME/.homeassistant"
    else
        return 1
    fi
}

# Main installation
main() {
    print_header "UniFi Network Pro Installer"

    echo -e "\nThis script will install the UniFi Network Pro integration"
    echo -e "for Home Assistant.\n"

    # Detect or ask for HA config directory
    print_info "Detecting Home Assistant configuration directory..."
    HA_CONFIG=$(detect_ha_config)

    if [ -z "$HA_CONFIG" ]; then
        print_warning "Could not auto-detect Home Assistant config directory"
        read -p "Enter your Home Assistant config path: " HA_CONFIG
    else
        print_success "Found Home Assistant at: $HA_CONFIG"
        read -p "Is this correct? (y/n): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            read -p "Enter your Home Assistant config path: " HA_CONFIG
        fi
    fi

    # Validate config directory
    if [ ! -d "$HA_CONFIG" ]; then
        print_error "Directory $HA_CONFIG does not exist"
        exit 1
    fi

    # Check if configuration.yaml exists
    if [ ! -f "$HA_CONFIG/configuration.yaml" ]; then
        print_error "No configuration.yaml found in $HA_CONFIG"
        print_error "This doesn't appear to be a valid Home Assistant config directory"
        exit 1
    fi

    print_success "Valid Home Assistant directory confirmed"

    # Create custom_components directory if needed
    print_info "Checking for custom_components directory..."
    CUSTOM_DIR="$HA_CONFIG/custom_components"

    if [ ! -d "$CUSTOM_DIR" ]; then
        print_info "Creating custom_components directory..."
        mkdir -p "$CUSTOM_DIR"
        print_success "Created $CUSTOM_DIR"
    else
        print_success "custom_components directory exists"
    fi

    # Check if integration already exists
    INTEGRATION_DIR="$CUSTOM_DIR/unifi_network_pro"

    if [ -d "$INTEGRATION_DIR" ]; then
        print_warning "UniFi Network Pro integration already exists"
        read -p "Do you want to overwrite it? (y/n): " overwrite
        if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
            print_info "Installation cancelled"
            exit 0
        fi
        print_info "Backing up existing installation..."
        mv "$INTEGRATION_DIR" "$INTEGRATION_DIR.backup.$(date +%s)"
        print_success "Backup created"
    fi

    # Get script directory (where this install.sh is located)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SOURCE_DIR="$SCRIPT_DIR/custom_components/unifi_network_pro"

    # Verify source files exist
    if [ ! -d "$SOURCE_DIR" ]; then
        print_error "Source files not found at $SOURCE_DIR"
        print_error "Make sure you're running this script from the integration directory"
        exit 1
    fi

    # Copy integration files
    print_info "Installing UniFi Network Pro integration..."
    cp -r "$SOURCE_DIR" "$CUSTOM_DIR/"

    # Verify installation
    if [ -f "$INTEGRATION_DIR/manifest.json" ]; then
        print_success "Integration files copied successfully"
    else
        print_error "Installation failed - manifest.json not found"
        exit 1
    fi

    # Set proper permissions
    print_info "Setting permissions..."
    chmod -R 755 "$INTEGRATION_DIR"
    print_success "Permissions set"

    # Check if running in Docker
    if [ -f "/.dockerenv" ]; then
        print_info "Running in Docker container"
        # Try to set ownership to homeassistant user
        if id "homeassistant" &>/dev/null; then
            chown -R homeassistant:homeassistant "$INTEGRATION_DIR"
            print_success "Ownership set to homeassistant user"
        fi
    fi

    # Installation complete
    print_header "Installation Complete!"

    echo -e "\n${GREEN}✓ UniFi Network Pro has been installed successfully!${NC}\n"

    print_info "Integration location: $INTEGRATION_DIR"
    print_info "Files installed:"
    ls -1 "$INTEGRATION_DIR" | sed 's/^/  - /'

    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo "1. Restart Home Assistant"
    echo "2. Go to Settings → Devices & Services"
    echo "3. Click '+ ADD INTEGRATION'"
    echo "4. Search for 'UniFi Network Pro'"
    echo "5. Follow the setup wizard"

    echo -e "\n${BLUE}Configuration Requirements:${NC}"
    echo "- UDM Pro Max IP address or hostname"
    echo "- UniFi controller admin username"
    echo "- UniFi controller admin password"
    echo "- Site ID (usually 'default')"

    echo -e "\n${BLUE}Documentation:${NC}"
    echo "- Quick Start: $SCRIPT_DIR/QUICKSTART.md"
    echo "- Full Guide: $SCRIPT_DIR/INSTALLATION.md"
    echo "- Troubleshooting: $SCRIPT_DIR/TROUBLESHOOTING.md"

    echo -e "\n${BLUE}Example Configurations:${NC}"
    echo "- Dashboards: $SCRIPT_DIR/examples/"
    echo "- Automations: $SCRIPT_DIR/examples/automations.yaml"

    # Ask about restarting HA
    echo -e "\n"
    read -p "Would you like help restarting Home Assistant? (y/n): " restart_help

    if [ "$restart_help" = "y" ] || [ "$restart_help" = "Y" ]; then
        echo -e "\n${BLUE}Restart Methods:${NC}"
        echo "1. UI: Settings → System → Restart"
        echo "2. CLI: ha core restart"
        echo "3. Docker: docker restart homeassistant"
        echo "4. Supervisor: systemctl restart home-assistant@homeassistant"
    fi

    print_success "Thank you for using UniFi Network Pro!"
}

# Run main function
main "$@"
