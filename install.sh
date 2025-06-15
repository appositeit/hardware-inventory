#!/bin/bash
# Installation script for Hardware Inventory System

set -e

echo "Hardware Inventory System Installer"
echo "==================================="
echo ""

# Default values
INSTALL_PATH="/opt/hardware-inventory"
PYTHON_BIN="/usr/bin/python3"
SERVICE_USER="$USER"
SERVICE_GROUP="$USER"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        --user)
            SERVICE_USER="$2"
            shift 2
            ;;
        --group)
            SERVICE_GROUP="$2"
            shift 2
            ;;
        --python)
            PYTHON_BIN="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --path PATH     Installation path (default: /opt/hardware-inventory)"
            echo "  --user USER     Service user (default: current user)"
            echo "  --group GROUP   Service group (default: current user)"
            echo "  --python PATH   Python binary path (default: /usr/bin/python3)"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Installation settings:"
echo "  Path: $INSTALL_PATH"
echo "  User: $SERVICE_USER"
echo "  Group: $SERVICE_GROUP"
echo "  Python: $PYTHON_BIN"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "Error: Python not found at $PYTHON_BIN"
    exit 1
fi

if ! "$PYTHON_BIN" -c "import flask" &> /dev/null; then
    echo "Error: Flask is not installed. Please install it with:"
    echo "  pip3 install flask"
    exit 1
fi

# Create installation directory
if [ "$INSTALL_PATH" != "$(pwd)" ]; then
    echo "Creating installation directory..."
    sudo mkdir -p "$INSTALL_PATH"
    sudo chown "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_PATH"
    
    echo "Copying files..."
    sudo cp -r . "$INSTALL_PATH/"
    sudo chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_PATH"
fi

# Create data directory
echo "Creating data directory..."
mkdir -p "$INSTALL_PATH/data"

# Create systemd service file
echo "Creating systemd service file..."
sed -e "s|%USER%|$SERVICE_USER|g" \
    -e "s|%GROUP%|$SERVICE_GROUP|g" \
    -e "s|%INSTALL_PATH%|$INSTALL_PATH|g" \
    -e "s|%PYTHON_BIN%|$PYTHON_BIN|g" \
    "$INSTALL_PATH/systemd/hardware-inventory.service.template" | \
    sudo tee /etc/systemd/system/hardware-inventory.service > /dev/null

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "Installation complete!"
echo ""
echo "To start the service:"
echo "  sudo systemctl start hardware-inventory"
echo "  sudo systemctl enable hardware-inventory  # To start on boot"
echo ""
echo "To check status:"
echo "  sudo systemctl status hardware-inventory"
echo ""
echo "Web interface will be available at:"
echo "  http://localhost:5000"
echo ""
echo "To scan systems, use:"
echo "  curl http://localhost:5000/scan_system | sudo bash"
