#!/bin/bash
# Setup script for hardware inventory system

echo "Hardware Inventory Setup"
echo "========================"

# Parse arguments
AUTO_YES=false
while getopts "y" opt; do
    case $opt in
        y)
            AUTO_YES=true
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            echo "Usage: $0 [-y]"
            echo "  -y  Automatically answer yes to all prompts"
            exit 1
            ;;
    esac
done

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check for pip3
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Install Flask if not already installed
echo "Checking for Flask..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing Flask..."
    pip3 install flask
else
    echo "Flask is already installed."
fi

# Initialize database
echo "Initializing database..."
cd src && python3 inventory_manager.py list > /dev/null 2>&1 && cd ..
echo "Database initialized at: data/hardware_inventory.db"

# Test hardware detection script
echo ""
echo "Testing hardware detection script..."
echo "Running without sudo (limited info):"
scripts/detect_hardware.sh 2>/dev/null | head -10
echo "..."
echo ""

# Offer to scan local system
if [ "$AUTO_YES" = true ]; then
    REPLY="y"
    echo "Auto-scanning local system (-y flag provided)..."
else
    read -p "Would you like to scan this system now? (y/n) " -n 1 -r
    echo
fi

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Scanning local system..."
    cd src
    if [ "$EUID" -eq 0 ]; then
        python3 inventory_manager.py scan
    else
        echo "Note: Running without root access. Some hardware details may be limited."
        echo "For full details, run: sudo python3 inventory_manager.py scan"
        python3 inventory_manager.py scan
    fi
    cd ..
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the web interface:"
echo "  cd src && python3 web_interface.py"
echo ""
echo "Then open: http://localhost:5000"
echo ""
echo "To scan systems:"
echo "  Local:  cd src && sudo python3 inventory_manager.py scan"
echo "  Remote: cd src && python3 inventory_manager.py scan --hostname <hostname>"
echo ""
echo "To add spare parts:"
echo "  cd src && python3 inventory_manager.py add-spare --type <type> --manufacturer <mfr> --model <model>"
