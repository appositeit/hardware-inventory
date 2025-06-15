#!/usr/bin/env python3
"""
Basic tests for Hardware Inventory System

Run with: python3 test_basic.py
"""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_database_schema():
    """Test that database schema can be created"""
    print("Testing database schema creation...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # Read schema
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Create database
        conn = sqlite3.connect(db_path)
        conn.executescript(schema)
        conn.close()
        
        # Verify tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        expected_tables = ['systems', 'components']
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"
        
        print("✅ Database schema test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_hardware_detection_script():
    """Test that hardware detection script exists and is executable"""
    print("Testing hardware detection script...")
    
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'detect_hardware.sh')
    
    try:
        # Check if script exists
        assert os.path.exists(script_path), f"Script not found: {script_path}"
        
        # Check if script is executable
        assert os.access(script_path, os.X_OK), f"Script not executable: {script_path}"
        
        print("✅ Hardware detection script test passed")
        return True
        
    except Exception as e:
        print(f"❌ Hardware detection script test failed: {e}")
        return False

def test_imports():
    """Test that main modules can be imported"""
    print("Testing module imports...")
    
    try:
        import inventory_manager
        print("  ✅ inventory_manager imported successfully")
        
        import web_interface
        print("  ✅ web_interface imported successfully")
        
        print("✅ Module import test passed")
        return True
        
    except Exception as e:
        print(f"❌ Module import test failed: {e}")
        return False

def test_requirements():
    """Test that required files exist"""
    print("Testing required files...")
    
    base_path = os.path.join(os.path.dirname(__file__), '..')
    required_files = [
        'README.md',
        'LICENSE',
        'requirements.txt',
        'schema.sql',
        'setup.sh',
        'install.sh',
        '.gitignore'
    ]
    
    try:
        for file in required_files:
            file_path = os.path.join(base_path, file)
            assert os.path.exists(file_path), f"Required file not found: {file}"
        
        print("✅ Required files test passed")
        return True
        
    except Exception as e:
        print(f"❌ Required files test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Hardware Inventory System Tests")
    print("=" * 50)
    
    tests = [
        test_requirements,
        test_database_schema,
        test_hardware_detection_script,
        test_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
