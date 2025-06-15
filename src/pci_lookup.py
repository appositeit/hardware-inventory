#!/usr/bin/env python3
"""
PCI ID Lookup Utility for Hardware Inventory
Provides manufacturer and device name resolution from PCI vendor/device IDs
"""

import re
import os
import subprocess
from typing import Dict, Optional, Tuple


class PCIIDLookup:
    """PCI ID database lookup utility"""
    
    def __init__(self):
        self.vendors = {}
        self.devices = {}
        self.pci_ids_paths = [
            '/usr/share/hwdata/pci.ids',
            '/usr/share/misc/pci.ids', 
            '/usr/local/share/pci.ids',
            '/var/lib/usbutils/pci.ids'
        ]
        self._load_pci_ids()
    
    def _load_pci_ids(self):
        """Load PCI IDs from system database file"""
        pci_ids_file = None
        
        # Find the pci.ids file
        for path in self.pci_ids_paths:
            if os.path.exists(path):
                pci_ids_file = path
                break
        
        if not pci_ids_file:
            print("Warning: No pci.ids file found. Manufacturer detection will be limited.")
            return
        
        try:
            with open(pci_ids_file, 'r', encoding='utf-8', errors='ignore') as f:
                current_vendor_id = None
                
                for line in f:
                    line = line.rstrip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Vendor line (no leading tab)
                    if not line.startswith('\t') and ' ' in line:
                        parts = line.split(' ', 1)
                        if len(parts) == 2 and len(parts[0]) == 4:
                            try:
                                vendor_id = parts[0].lower()
                                vendor_name = parts[1]
                                self.vendors[vendor_id] = vendor_name
                                current_vendor_id = vendor_id
                            except ValueError:
                                continue
                    
                    # Device line (one leading tab)
                    elif line.startswith('\t') and not line.startswith('\t\t') and current_vendor_id:
                        device_line = line[1:]  # Remove leading tab
                        if ' ' in device_line:
                            parts = device_line.split(' ', 1)
                            if len(parts) == 2 and len(parts[0]) == 4:
                                try:
                                    device_id = parts[0].lower()
                                    device_name = parts[1]
                                    device_key = f"{current_vendor_id}:{device_id}"
                                    self.devices[device_key] = device_name
                                except ValueError:
                                    continue
                                    
        except Exception as e:
            print(f"Warning: Error loading pci.ids file: {e}")
    
    def get_vendor_name(self, vendor_id: str) -> Optional[str]:
        """Get vendor name from vendor ID (4-digit hex)"""
        if not vendor_id:
            return None
        
        # Normalize to lowercase 4-digit hex
        vendor_id = vendor_id.lower().zfill(4)
        return self.vendors.get(vendor_id)
    
    def get_device_name(self, vendor_id: str, device_id: str) -> Optional[str]:
        """Get device name from vendor and device IDs"""
        if not vendor_id or not device_id:
            return None
        
        # Normalize to lowercase 4-digit hex
        vendor_id = vendor_id.lower().zfill(4)
        device_id = device_id.lower().zfill(4)
        device_key = f"{vendor_id}:{device_id}"
        return self.devices.get(device_key)
    
    def lookup_pci_device(self, vendor_id: str, device_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Get both vendor and device names"""
        vendor_name = self.get_vendor_name(vendor_id)
        device_name = self.get_device_name(vendor_id, device_id)
        return vendor_name, device_name


def parse_lspci_vendor_ids() -> Dict[str, str]:
    """
    Parse lspci -nn output to extract vendor/device IDs and manufacturers
    Returns dict mapping PCI addresses to manufacturer names
    """
    manufacturers = {}
    
    try:
        # Run lspci -nn to get vendor/device IDs with names
        result = subprocess.run(['lspci', '-nn'], capture_output=True, text=True)
        if result.returncode != 0:
            return manufacturers
        
        # Pattern to match lspci -nn output: 
        # 01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GA106 [10de:2504] (rev a1)
        pattern = r'^([0-9a-f]{2}:[0-9a-f]{2}\.[0-9a-f])\s+.*?:\s+([^[]+)\s+.*?\[([0-9a-f]{4}):([0-9a-f]{4})\]'
        
        for line in result.stdout.split('\n'):
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                pci_addr, manufacturer, vendor_id, device_id = match.groups()
                # Clean up manufacturer name
                manufacturer = manufacturer.strip()
                # Remove common suffixes to get cleaner manufacturer names
                manufacturer = re.sub(r'\s+(Inc\.|Corporation|Co\.,?\s*Ltd\.?|Ltd\.?|Corp\.?)$', '', manufacturer)
                manufacturers[f"{vendor_id.lower()}:{device_id.lower()}"] = manufacturer
        
    except Exception as e:
        print(f"Warning: Error parsing lspci output: {e}")
    
    return manufacturers


def extract_vendor_id_from_device_string(device_string: str) -> Optional[str]:
    """
    Extract vendor ID from device strings that might contain PCI IDs
    Examples: 
    - "GA106 [GeForce RTX 3060 Lite Hash Rate]" -> None (no ID visible)
    - Various GPU model strings -> attempt to extract
    """
    # Look for PCI ID patterns in device strings
    pci_pattern = r'\[([0-9a-f]{4}):([0-9a-f]{4})\]'
    match = re.search(pci_pattern, device_string, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    
    return None


def enhance_manufacturer_detection(component_data: dict, lookup: PCIIDLookup) -> str:
    """
    Enhance manufacturer detection for a component
    Returns the best manufacturer name found
    """
    component_type = component_data.get('component_type', '')
    current_manufacturer = component_data.get('manufacturer', '').strip()
    device_model = component_data.get('model', '')
    
    # If we already have a good manufacturer, keep it
    if current_manufacturer and len(current_manufacturer) > 2:
        return current_manufacturer
    
    # Try to extract vendor ID from model string for PCI devices
    vendor_id = extract_vendor_id_from_device_string(device_model)
    if vendor_id:
        vendor_name = lookup.get_vendor_name(vendor_id)
        if vendor_name:
            return vendor_name
    
    # For GPUs, try common manufacturer detection from model string
    if component_type == 'gpu':
        model_lower = device_model.lower()
        if 'nvidia' in model_lower or 'geforce' in model_lower or 'quadro' in model_lower or 'tesla' in model_lower:
            return 'NVIDIA Corporation'
        elif 'amd' in model_lower or 'radeon' in model_lower or 'ati' in model_lower:
            return 'Advanced Micro Devices, Inc.'
        elif 'intel' in model_lower:
            return 'Intel Corporation'
    
    # For storage, try common manufacturer detection
    elif component_type == 'storage':
        model_lower = device_model.lower()
        if 'samsung' in model_lower:
            return 'Samsung Electronics Co Ltd'
        elif 'western digital' in model_lower or 'wd' in model_lower:
            return 'Western Digital'
        elif 'seagate' in model_lower:
            return 'Seagate Technology'
        elif 'toshiba' in model_lower:
            return 'Toshiba'
        elif 'intel' in model_lower:
            return 'Intel Corporation'
        elif 'crucial' in model_lower or 'micron' in model_lower:
            return 'Micron Technology'
        elif 'kingston' in model_lower:
            return 'Kingston Technology'
    
    # For CPUs, extract manufacturer from model
    elif component_type == 'cpu':
        model_lower = device_model.lower()
        if 'intel' in model_lower:
            return 'Intel Corporation'
        elif 'amd' in model_lower:
            return 'Advanced Micro Devices, Inc.'
        elif 'arm' in model_lower:
            return 'ARM'
    
    return current_manufacturer


if __name__ == '__main__':
    # Test the PCI ID lookup functionality
    lookup = PCIIDLookup()
    
    print("PCI ID Lookup Test")
    print("=" * 50)
    print(f"Loaded {len(lookup.vendors)} vendors and {len(lookup.devices)} devices")
    
    # Test some common vendor IDs
    test_vendors = ['8086', '10de', '1002', '1022', '10ec', '144d']
    for vendor_id in test_vendors:
        vendor_name = lookup.get_vendor_name(vendor_id)
        print(f"Vendor {vendor_id}: {vendor_name}")
    
    print("\nLSPCI Parsing Test")
    print("=" * 50)
    manufacturers = parse_lspci_vendor_ids()
    for device_id, manufacturer in list(manufacturers.items())[:5]:
        print(f"Device {device_id}: {manufacturer}")
