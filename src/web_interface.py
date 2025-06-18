#!/usr/bin/env python3
"""
Simple Flask web interface for hardware inventory
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, Response, make_response
import sqlite3
import json
from datetime import datetime
import os
import socket
import subprocess

# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'templates'))

# Default database path
default_db = os.path.join(BASE_DIR, 'data', 'hardware_inventory.db')
app.config['DATABASE'] = os.environ.get('INVENTORY_DB', default_db)


def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


@app.route('/')
def index():
    """Main dashboard"""
    db = get_db()
    
    # Get component counts by type and status
    cursor = db.cursor()
    cursor.execute("""
        SELECT component_type, status, COUNT(*) as count
        FROM components
        GROUP BY component_type, status
        ORDER BY component_type, status
    """)
    
    stats = {}
    for row in cursor.fetchall():
        comp_type = row['component_type']
        if comp_type not in stats:
            stats[comp_type] = {'installed': 0, 'spare': 0, 'retired': 0}
        stats[comp_type][row['status']] = row['count']
    
    # Get system count
    cursor.execute("SELECT COUNT(*) as count FROM systems")
    system_count = cursor.fetchone()['count']
    
    db.close()
    
    return render_template('index.html', stats=stats, system_count=system_count)


@app.route('/systems')
def systems():
    """List all systems"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT s.*, 
               COUNT(sc.component_id) as component_count
        FROM systems s
        LEFT JOIN system_components sc ON s.id = sc.system_id
        GROUP BY s.id
        ORDER BY s.hostname
    """)
    systems = cursor.fetchall()
    db.close()
    
    return render_template('systems.html', systems=systems)


@app.route('/system/<hostname>')
def system_detail(hostname):
    """Show system details"""
    db = get_db()
    cursor = db.cursor()
    
    # Get system info
    cursor.execute("SELECT * FROM systems WHERE hostname = ?", (hostname,))
    system = cursor.fetchone()
    
    if not system:
        db.close()
        return "System not found", 404
    
    # Get components
    cursor.execute("""
        SELECT c.* 
        FROM components c
        JOIN system_components sc ON c.id = sc.component_id
        JOIN systems s ON sc.system_id = s.id
        WHERE s.hostname = ?
        ORDER BY c.component_type
    """, (hostname,))
    
    components = cursor.fetchall()
    db.close()
    
    # Parse component specifications
    parsed_components = []
    for comp in components:
        comp_dict = dict(comp)
        if comp_dict['specifications']:
            try:
                comp_dict['specs'] = json.loads(comp_dict['specifications'])
            except:
                comp_dict['specs'] = {}
        parsed_components.append(comp_dict)
    
    return render_template('system_detail.html', system=system, components=parsed_components)


@app.route('/components')
def components():
    """List all components"""
    comp_type = request.args.get('type')
    status = request.args.get('status')
    
    db = get_db()
    cursor = db.cursor()
    
    query = "SELECT * FROM components WHERE 1=1"
    params = []
    
    if comp_type:
        query += " AND component_type = ?"
        params.append(comp_type)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY component_type, manufacturer, model"
    
    cursor.execute(query, params)
    components = cursor.fetchall()
    db.close()
    
    return render_template('components.html', components=components, 
                          filter_type=comp_type, filter_status=status)


@app.route('/component/add', methods=['GET', 'POST'])
def add_component():
    """Add a spare component"""
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO components 
            (component_type, manufacturer, model, serial_number, 
             status, location, notes)
            VALUES (?, ?, ?, ?, 'spare', ?, ?)
        """, (
            request.form['type'],
            request.form['manufacturer'],
            request.form['model'],
            request.form.get('serial', ''),
            request.form.get('location', ''),
            request.form.get('notes', '')
        ))
        
        db.commit()
        db.close()
        
        return redirect(url_for('components'))
    
    return render_template('add_component.html')


@app.route('/component/<int:comp_id>/edit', methods=['GET', 'POST'])
def edit_component(comp_id):
    """Edit a component"""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        cursor.execute("""
            UPDATE components 
            SET manufacturer = ?, model = ?, serial_number = ?,
                status = ?, location = ?, notes = ?
            WHERE id = ?
        """, (
            request.form['manufacturer'],
            request.form['model'],
            request.form.get('serial', ''),
            request.form['status'],
            request.form.get('location', ''),
            request.form.get('notes', ''),
            comp_id
        ))
        
        db.commit()
        db.close()
        
        return redirect(url_for('components'))
    
    cursor.execute("SELECT * FROM components WHERE id = ?", (comp_id,))
    component = cursor.fetchone()
    db.close()
    
    if not component:
        return "Component not found", 404
    
    return render_template('edit_component.html', component=component)


@app.route('/component/<int:comp_id>/delete', methods=['POST'])
def delete_component(comp_id):
    """Delete a component"""
    from inventory_manager import HardwareInventory
    
    inventory = HardwareInventory(app.config['DATABASE'])
    success = inventory.delete_component(comp_id)
    inventory.close()
    
    if success:
        return jsonify({'status': 'success', 'message': 'Component deleted'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to delete component'}), 500


@app.route('/system/<hostname>/delete', methods=['POST'])
def delete_system(hostname):
    """Delete a system"""
    from inventory_manager import HardwareInventory
    
    inventory = HardwareInventory(app.config['DATABASE'])
    system_id = inventory.get_system_id_by_hostname(hostname)
    
    if system_id:
        success = inventory.delete_system(system_id)
        inventory.close()
        
        if success:
            return jsonify({'status': 'success', 'message': 'System deleted'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete system'}), 500
    else:
        inventory.close()
        return jsonify({'status': 'error', 'message': 'System not found'}), 404


@app.route('/scan-help')
def scan_help():
    """Show help for scanning systems"""
    import socket
    # Get the server's hostname and IP
    hostname = socket.gethostname()
    try:
        # Try to get the primary IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        server_ip = s.getsockname()[0]
        s.close()
    except:
        server_ip = "nara"
    
    # Get current port from environment or use default
    port = os.environ.get('INVENTORY_PORT', '5101')
    server_url = f"http://{server_ip}:{port}"
    
    return render_template('scan_help.html', 
                          server_url=server_url,
                          hostname=hostname,
                          server_ip=server_ip)


@app.route('/credits')
def credits():
    """Show credits page"""
    return render_template('credits.html')


@app.route('/scan_system')
def scan_system():
    """Return a bash script that can be piped to bash for easy scanning"""
    # Get server URL
    hostname = socket.gethostname()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        server_ip = s.getsockname()[0]
        s.close()
    except:
        server_ip = hostname
    
    # Get current port from environment or use default
    port = os.environ.get('INVENTORY_PORT', '5101')
    server_url = f"http://{server_ip}:{port}"
    
    # Generate the bash script
    script = f'''#!/bin/bash
# Hardware Inventory Scanner
# Auto-generated script from {server_url}

SERVER_URL="{server_url}"
TEMP_DIR="/tmp/hardware_inventory_$$"

echo "Hardware Inventory Scanner"
echo "========================="
echo "Server: $SERVER_URL"
echo ""

# Check for required commands
MISSING_CMDS=""
for cmd in lscpu lsblk lspci; do
    if ! command -v $cmd >/dev/null 2>&1; then
        MISSING_CMDS="$MISSING_CMDS $cmd"
    fi
done

if [ -n "$MISSING_CMDS" ]; then
    echo "WARNING: Missing required commands:$MISSING_CMDS"
    echo "Some hardware information may be incomplete."
    echo ""
fi

# Check for dmidecode (optional but recommended)
if ! command -v dmidecode >/dev/null 2>&1; then
    echo "NOTE: dmidecode is not installed."
    echo "Install it for complete hardware information:"
    if [ -f /etc/debian_version ]; then
        echo "  sudo apt-get install dmidecode"
    elif [ -f /etc/redhat-release ]; then
        echo "  sudo yum install dmidecode"
    else
        echo "  Please install dmidecode using your package manager"
    fi
    echo ""
fi

# Create temp directory
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Download detection script
echo "Downloading detection script..."
if command -v wget >/dev/null 2>&1; then
    wget -q "$SERVER_URL/static/detect_hardware.sh" -O detect_hardware.sh
elif command -v curl >/dev/null 2>&1; then
    curl -s "$SERVER_URL/static/detect_hardware.sh" -o detect_hardware.sh
else
    echo "ERROR: Neither wget nor curl is available. Cannot download detection script."
    exit 1
fi

if [ ! -f detect_hardware.sh ]; then
    echo "ERROR: Failed to download detection script"
    exit 1
fi

chmod +x detect_hardware.sh

# Run detection
echo "Scanning hardware..."
if [ "$EUID" -eq 0 ]; then
    ./detect_hardware.sh > hardware_data.json 2>/dev/null
else
    echo "Running without sudo - some information may be limited."
    echo "For complete details, run: curl $SERVER_URL/scan_system | sudo bash"
    ./detect_hardware.sh > hardware_data.json 2>/dev/null
fi

# Verify JSON
if ! python3 -m json.tool < hardware_data.json >/dev/null 2>&1; then
    echo "ERROR: Hardware detection failed to produce valid JSON"
    cat hardware_data.json
    exit 1
fi

# Upload results
echo "Uploading results to inventory server..."
if command -v curl >/dev/null 2>&1; then
    RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \\
        -d @hardware_data.json \\
        "$SERVER_URL/api/upload_scan")
    echo "Server response: $RESPONSE"
elif command -v wget >/dev/null 2>&1; then
    RESPONSE=$(wget -q -O - --post-file=hardware_data.json \\
        --header="Content-Type: application/json" \\
        "$SERVER_URL/api/upload_scan")
    echo "Server response: $RESPONSE"
else
    echo "ERROR: Cannot upload results (no curl or wget)"
    echo "Manual upload required. Hardware data saved to: $TEMP_DIR/hardware_data.json"
    exit 1
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "Scan complete!"
echo "View results at: $SERVER_URL"
'''
    
    response = make_response(script)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = 'inline; filename="scan_system.sh"'
    return response


@app.route('/api/upload_scan', methods=['POST'])
def api_upload_scan():
    """API endpoint to receive scan results"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Import the inventory manager
        from inventory_manager import HardwareInventory
        
        # Process the scan data
        inventory = HardwareInventory(app.config['DATABASE'])
        inventory.update_system(data)
        inventory.close()
        
        return jsonify({
            'status': 'success', 
            'message': f'Successfully updated inventory for {data.get("hostname", "unknown")}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/scan/<hostname>', methods=['POST'])
def api_scan_system(hostname):
    """API endpoint to trigger system scan"""
    # This would integrate with the inventory_manager.py script
    # For now, return a placeholder
    return jsonify({'status': 'success', 'message': f'Scan of {hostname} queued'})


if __name__ == '__main__':
    import argparse
    
    # Create templates directory
    os.makedirs(os.path.join(BASE_DIR, 'templates'), exist_ok=True)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Hardware Inventory Web Interface')
    parser.add_argument('--host', default=os.environ.get('INVENTORY_HOST', '0.0.0.0'),
                        help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=int(os.environ.get('INVENTORY_PORT', 5101)),
                        help='Port to bind to (default: 5101)')
    parser.add_argument('--debug', action='store_true', 
                        default=os.environ.get('INVENTORY_DEBUG', 'false').lower() == 'true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"Starting Hardware Inventory Web Interface on {args.host}:{args.port}")
    print(f"Debug mode: {args.debug}")
    print(f"Database: {app.config['DATABASE']}")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
