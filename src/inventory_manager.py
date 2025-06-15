#!/usr/bin/env python3
"""
Hardware Inventory Manager
Processes hardware detection data and manages the SQLite database
"""

import json
import sqlite3
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import argparse


class HardwareInventory:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'data', 'hardware_inventory.db')
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema if needed"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Read and execute schema
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema_path = os.path.join(base_dir, 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                self.conn.executescript(f.read())
        self.conn.commit()
    
    def scan_local_system(self) -> Dict:
        """Run hardware detection script on local system"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(base_dir, 'scripts', 'detect_hardware.sh')
        try:
            # Try with sudo first (non-interactive), fall back to regular user
            result = subprocess.run(['sudo', '-n', script_path], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                # If sudo fails, try without
                result = subprocess.run([script_path], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON output: {e}")
                    print(f"Output was: {result.stdout[:200]}...")
                    return None
            else:
                print(f"Error running detection script: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error scanning system: {e}")
            return None
    
    def scan_remote_system(self, hostname: str) -> Dict:
        """Run hardware detection script on remote system via SSH"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(base_dir, 'scripts', 'detect_hardware.sh')
        try:
            # Copy script to remote system
            scp_result = subprocess.run(
                ['scp', script_path, f'{hostname}:/tmp/detect_hardware.sh'],
                capture_output=True, text=True
            )
            
            if scp_result.returncode == 0:
                # Run script on remote system
                ssh_result = subprocess.run(
                    ['ssh', hostname, 'sudo /tmp/detect_hardware.sh'],
                    capture_output=True, text=True
                )
                
                if ssh_result.returncode == 0:
                    return json.loads(ssh_result.stdout)
                else:
                    print(f"Error running remote detection: {ssh_result.stderr}")
                    return None
            else:
                print(f"Error copying script: {scp_result.stderr}")
                return None
        except Exception as e:
            print(f"Error scanning remote system: {e}")
            return None
    
    def update_system(self, data: Dict):
        """Update or insert system and component data"""
        cursor = self.conn.cursor()
        
        # Update or insert system record
        system_data = data.get('system', {})
        
        # First check if system exists
        cursor.execute("SELECT id FROM systems WHERE hostname = ?", (data['hostname'],))
        existing_system = cursor.fetchone()
        
        if existing_system:
            system_id = existing_system[0]
            cursor.execute("""
                UPDATE systems 
                SET manufacturer = ?, model = ?, serial_number = ?, 
                    uuid = ?, last_scan = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                system_data.get('manufacturer', ''),
                system_data.get('product', ''),
                system_data.get('serial', ''),
                system_data.get('uuid', ''),
                data['detection_date'],
                system_id
            ))
        else:
            cursor.execute("""
                INSERT INTO systems 
                (hostname, manufacturer, model, serial_number, uuid, last_scan)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data['hostname'],
                system_data.get('manufacturer', ''),
                system_data.get('product', ''),
                system_data.get('serial', ''),
                system_data.get('uuid', ''),
                data['detection_date']
            ))
            system_id = cursor.lastrowid
        
        # Don't clear components - we'll update them in place
        # Just remove old system component links
        cursor.execute("DELETE FROM system_components WHERE system_id = ?", (system_id,))
        
        # Process CPU
        cpu_data = data.get('cpu', {})
        if cpu_data.get('model'):
            component_id = self._add_or_update_component(
                cursor, 'cpu', '', cpu_data['model'], '',
                json.dumps(cpu_data), 'installed', data['hostname']
            )
            self._link_component_to_system(cursor, system_id, component_id)
        
        # Process Memory
        memory_data = data.get('memory', {})
        for slot in memory_data.get('slots', []):
            if slot.get('size') and 'No Module' not in slot.get('size', ''):
                specs = {
                    'slot': slot.get('slot'),
                    'size': slot.get('size'),
                    'speed': slot.get('speed'),
                    'type': slot.get('type')
                }
                component_id = self._add_or_update_component(
                    cursor, 'memory',
                    slot.get('manufacturer', ''),
                    f"{slot.get('type', 'Memory')} {slot.get('size', '')}",
                    slot.get('part_number', ''),
                    json.dumps(specs), 'installed', data['hostname']
                )
                self._link_component_to_system(cursor, system_id, component_id)
        
        # Process Storage
        for disk in data.get('storage', []):
            if disk.get('model'):
                specs = {
                    'device': disk.get('device'),
                    'size': disk.get('size'),
                    'type': disk.get('type')
                }
                component_id = self._add_or_update_component(
                    cursor, 'storage', '',
                    disk['model'],
                    disk.get('serial', ''),
                    json.dumps(specs), 'installed', data['hostname']
                )
                self._link_component_to_system(cursor, system_id, component_id)
        
        # Process GPU
        for gpu in data.get('gpu', []):
            if gpu.get('device'):
                component_id = self._add_or_update_component(
                    cursor, 'gpu', '',
                    gpu['device'], '',
                    json.dumps(gpu), 'installed', data['hostname']
                )
                self._link_component_to_system(cursor, system_id, component_id)
        
        # Process Motherboard
        mb_data = data.get('motherboard', {})
        if mb_data.get('product'):
            component_id = self._add_or_update_component(
                cursor, 'motherboard',
                mb_data.get('manufacturer', ''),
                mb_data.get('product', ''),
                mb_data.get('serial', ''),
                json.dumps(mb_data), 'installed', data['hostname']
            )
            self._link_component_to_system(cursor, system_id, component_id)
        
        self.conn.commit()
    
    def _add_or_update_component(self, cursor, comp_type: str, manufacturer: str,
                                 model: str, serial: str, specs: str,
                                 status: str, location: str) -> int:
        """Add or update a component record"""
        # Try to find existing component by serial number (if provided)
        if serial:
            cursor.execute(
                "SELECT id FROM components WHERE serial_number = ? AND component_type = ?",
                (serial, comp_type)
            )
            existing = cursor.fetchone()
        else:
            # For components without serial, match by type, model, and location
            # This prevents duplicates when rescanning the same system
            cursor.execute(
                "SELECT id FROM components WHERE model = ? AND component_type = ? AND location = ?",
                (model, comp_type, location)
            )
            existing = cursor.fetchone()
        
        if existing:
            # Update existing component
            cursor.execute("""
                UPDATE components 
                SET manufacturer = ?, model = ?, specifications = ?,
                    status = ?, location = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (manufacturer, model, specs, status, location, existing[0]))
            return existing[0]
        else:
            # Insert new component
            cursor.execute("""
                INSERT INTO components 
                (component_type, manufacturer, model, serial_number, 
                 specifications, status, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (comp_type, manufacturer, model, serial, specs, status, location))
            return cursor.lastrowid
    
    def _link_component_to_system(self, cursor, system_id: int, component_id: int):
        """Create link between system and component"""
        cursor.execute("""
            INSERT INTO system_components (system_id, component_id)
            VALUES (?, ?)
        """, (system_id, component_id))
    
    def add_spare_component(self, comp_type: str, manufacturer: str, 
                           model: str, serial: str = '', 
                           location: str = '', notes: str = ''):
        """Manually add a spare component"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO components 
            (component_type, manufacturer, model, serial_number, 
             status, location, notes)
            VALUES (?, ?, ?, ?, 'spare', ?, ?)
        """, (comp_type, manufacturer, model, serial, location, notes))
        self.conn.commit()
        return cursor.lastrowid
    
    def list_all_components(self, comp_type: Optional[str] = None,
                           status: Optional[str] = None) -> List[Dict]:
        """List all components with optional filters"""
        cursor = self.conn.cursor()
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
        return [dict(row) for row in cursor.fetchall()]
    
    def list_systems(self) -> List[Dict]:
        """List all systems"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.*, 
                   COUNT(sc.component_id) as component_count
            FROM systems s
            LEFT JOIN system_components sc ON s.id = sc.system_id
            GROUP BY s.id
            ORDER BY s.hostname
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_system_details(self, hostname: str) -> Dict:
        """Get detailed system information including components"""
        cursor = self.conn.cursor()
        
        # Get system info
        cursor.execute("SELECT * FROM systems WHERE hostname = ?", (hostname,))
        system = cursor.fetchone()
        if not system:
            return None
        
        result = dict(system)
        
        # Get components
        cursor.execute("""
            SELECT c.* 
            FROM components c
            JOIN system_components sc ON c.id = sc.component_id
            JOIN systems s ON sc.system_id = s.id
            WHERE s.hostname = ?
            ORDER BY c.component_type
        """, (hostname,))
        
        result['components'] = [dict(row) for row in cursor.fetchall()]
        return result
    
    def delete_component(self, component_id: int) -> bool:
        """Delete a component and its associations"""
        cursor = self.conn.cursor()
        try:
            # First remove any system associations
            cursor.execute("DELETE FROM system_components WHERE component_id = ?", (component_id,))
            # Then delete the component
            cursor.execute("DELETE FROM components WHERE id = ?", (component_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting component: {e}")
            return False
    
    def delete_system(self, system_id: int) -> bool:
        """Delete a system and its component associations"""
        cursor = self.conn.cursor()
        try:
            # Get the hostname for updating components
            cursor.execute("SELECT hostname FROM systems WHERE id = ?", (system_id,))
            system = cursor.fetchone()
            if not system:
                return False
            
            hostname = system[0]
            
            # Update components to mark them as spare
            cursor.execute("""
                UPDATE components 
                SET status = 'spare', location = NULL 
                WHERE location = ?
            """, (hostname,))
            
            # Remove all component associations
            cursor.execute("DELETE FROM system_components WHERE system_id = ?", (system_id,))
            
            # Then delete the system
            cursor.execute("DELETE FROM systems WHERE id = ?", (system_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting system: {e}")
            return False
    
    def get_system_id_by_hostname(self, hostname: str) -> Optional[int]:
        """Get system ID by hostname"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM systems WHERE hostname = ?", (hostname,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='Hardware Inventory Manager')
    parser.add_argument('action', choices=['scan', 'add-spare', 'list', 'show'],
                       help='Action to perform')
    parser.add_argument('--hostname', help='Hostname for remote scan or show')
    parser.add_argument('--type', help='Component type (for add-spare/list)')
    parser.add_argument('--manufacturer', help='Manufacturer (for add-spare)')
    parser.add_argument('--model', help='Model (for add-spare)')
    parser.add_argument('--serial', help='Serial number (for add-spare)')
    parser.add_argument('--location', help='Location (for add-spare)')
    parser.add_argument('--notes', help='Notes (for add-spare)')
    parser.add_argument('--status', help='Status filter (for list)')
    parser.add_argument('--db', default=None,
                       help='Database file path (default: data/hardware_inventory.db)')
    
    args = parser.parse_args()
    
    inventory = HardwareInventory(args.db)
    
    try:
        if args.action == 'scan':
            if args.hostname:
                print(f"Scanning remote system: {args.hostname}")
                data = inventory.scan_remote_system(args.hostname)
            else:
                print("Scanning local system...")
                data = inventory.scan_local_system()
            
            if data:
                inventory.update_system(data)
                print(f"Successfully updated inventory for {data['hostname']}")
            else:
                print("Scan failed")
                sys.exit(1)
        
        elif args.action == 'add-spare':
            if not all([args.type, args.manufacturer, args.model]):
                print("Error: --type, --manufacturer, and --model are required")
                sys.exit(1)
            
            comp_id = inventory.add_spare_component(
                args.type, args.manufacturer, args.model,
                args.serial or '', args.location or '', args.notes or ''
            )
            print(f"Added spare component with ID: {comp_id}")
        
        elif args.action == 'list':
            components = inventory.list_all_components(args.type, args.status)
            
            if not components:
                print("No components found")
            else:
                # Group by type
                by_type = {}
                for comp in components:
                    comp_type = comp['component_type']
                    if comp_type not in by_type:
                        by_type[comp_type] = []
                    by_type[comp_type].append(comp)
                
                for comp_type, items in sorted(by_type.items()):
                    print(f"\n{comp_type.upper()}:")
                    print("-" * 80)
                    for item in items:
                        status = f"[{item['status']}]"
                        location = f"@ {item['location']}" if item['location'] else ""
                        print(f"  {status:12} {item['manufacturer']:20} {item['model']:40} {location}")
                        if item['serial_number']:
                            print(f"               Serial: {item['serial_number']}")
        
        elif args.action == 'show':
            if args.hostname:
                details = inventory.get_system_details(args.hostname)
                if details:
                    print(f"\nSystem: {details['hostname']}")
                    print(f"Manufacturer: {details['manufacturer']}")
                    print(f"Model: {details['model']}")
                    print(f"Serial: {details['serial_number']}")
                    print(f"Last Scan: {details['last_scan']}")
                    print("\nComponents:")
                    
                    for comp in details['components']:
                        print(f"\n  {comp['component_type'].upper()}:")
                        print(f"    Model: {comp['model']}")
                        if comp['manufacturer']:
                            print(f"    Manufacturer: {comp['manufacturer']}")
                        if comp['serial_number']:
                            print(f"    Serial: {comp['serial_number']}")
                else:
                    print(f"System {args.hostname} not found")
            else:
                # List all systems
                systems = inventory.list_systems()
                print("\nSystems:")
                print("-" * 60)
                for sys in systems:
                    print(f"{sys['hostname']:20} {sys['manufacturer']:15} {sys['model']:20} "
                          f"({sys['component_count']} components)")
    
    finally:
        inventory.close()


if __name__ == '__main__':
    main()
