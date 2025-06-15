#!/usr/bin/env python3
"""
Test script for PCI manufacturer detection functionality
"""

import os
import sys
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from pci_lookup import PCIIDLookup, enhance_manufacturer_detection, parse_lspci_vendor_ids
    print("✅ PCI lookup modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PCI lookup modules: {e}")
    sys.exit(1)

def test_pci_lookup():
    """Test PCI ID lookup functionality"""
    print("\n🧪 Testing PCI ID Lookup")
    print("=" * 50)
    
    lookup = PCIIDLookup()
    print(f"✅ Loaded {len(lookup.vendors)} vendors and {len(lookup.devices)} devices")
    
    # Test known vendor IDs
    test_cases = [
        ('8086', 'Intel Corporation'),
        ('10de', 'NVIDIA Corporation'), 
        ('1002', 'Advanced Micro Devices, Inc. [AMD/ATI]'),
        ('1022', 'Advanced Micro Devices, Inc. [AMD]'),
        ('10ec', 'Realtek Semiconductor Co., Ltd.'),
        ('144d', 'Samsung Electronics Co Ltd')
    ]
    
    passed = 0
    for vendor_id, expected in test_cases:
        result = lookup.get_vendor_name(vendor_id)
        if result and expected in result:
            print(f"✅ {vendor_id}: {result}")
            passed += 1
        else:
            print(f"❌ {vendor_id}: Expected '{expected}', got '{result}'")
    
    print(f"\n📊 PCI Lookup Tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_manufacturer_enhancement():
    """Test manufacturer enhancement functionality"""
    print("\n🧪 Testing Manufacturer Enhancement")
    print("=" * 50)
    
    lookup = PCIIDLookup()
    
    test_cases = [
        {
            'component_type': 'cpu',
            'manufacturer': '',
            'model': 'AMD Ryzen 5 3600 6-Core Processor',
            'expected': 'Advanced Micro Devices, Inc.'
        },
        {
            'component_type': 'gpu', 
            'manufacturer': '',
            'model': 'NVIDIA Corporation GA102 [GeForce RTX 3080 Lite Hash Rate]',
            'expected': 'NVIDIA Corporation'
        },
        {
            'component_type': 'storage',
            'manufacturer': '',
            'model': 'Samsung SSD 970 EVO Plus 500GB',
            'expected': 'Samsung Electronics Co Ltd'
        },
        {
            'component_type': 'storage',
            'manufacturer': '',
            'model': 'WDC WD40EZRZ-00GXCB0',
            'expected': 'Western Digital'
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        result = enhance_manufacturer_detection(test_case, lookup)
        expected = test_case['expected']
        
        if result and expected in result:
            print(f"✅ {test_case['component_type']}: '{test_case['model']}' → {result}")
            passed += 1
        else:
            print(f"❌ {test_case['component_type']}: Expected '{expected}', got '{result}'")
    
    print(f"\n📊 Enhancement Tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_lspci_parsing():
    """Test lspci parsing functionality"""
    print("\n🧪 Testing LSPCI Parsing")
    print("=" * 50)
    
    try:
        manufacturers = parse_lspci_vendor_ids()
        if manufacturers:
            print(f"✅ Parsed {len(manufacturers)} devices from lspci")
            # Show a few examples
            for device_id, manufacturer in list(manufacturers.items())[:3]:
                print(f"   {device_id}: {manufacturer}")
            return True
        else:
            print("❌ No devices parsed from lspci")
            return False
    except Exception as e:
        print(f"❌ Error parsing lspci: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Hardware Inventory Manufacturer Detection Tests")
    print("=" * 60)
    
    tests = [
        test_pci_lookup,
        test_manufacturer_enhancement,
        test_lspci_parsing
    ]
    
    passed_tests = 0
    for test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}")
    
    print(f"\n📊 Overall Results: {passed_tests}/{len(tests)} test suites passed")
    
    if passed_tests == len(tests):
        print("🎉 All tests passed! Manufacturer detection is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
