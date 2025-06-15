-- SQLite schema for hardware inventory
-- Supports both installed components and spare parts

-- Main components table
CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_type VARCHAR(50) NOT NULL, -- cpu, gpu, memory, storage, motherboard
    manufacturer VARCHAR(100),
    model VARCHAR(200),
    serial_number VARCHAR(100),
    specifications TEXT, -- JSON field for detailed specs
    status VARCHAR(20) DEFAULT 'spare', -- installed, spare, retired
    location VARCHAR(100), -- hostname if installed, physical location if spare
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Systems table for complete computer records
CREATE TABLE IF NOT EXISTS systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname VARCHAR(100) UNIQUE NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(200),
    serial_number VARCHAR(100),
    uuid VARCHAR(100),
    last_scan TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link table for components currently installed in systems
CREATE TABLE IF NOT EXISTS system_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_id INTEGER,
    component_id INTEGER,
    installed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES systems(id),
    FOREIGN KEY (component_id) REFERENCES components(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_components_type ON components(component_type);
CREATE INDEX IF NOT EXISTS idx_components_status ON components(status);
CREATE INDEX IF NOT EXISTS idx_system_components_system ON system_components(system_id);
CREATE INDEX IF NOT EXISTS idx_system_components_component ON system_components(component_id);

-- Trigger to update the updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_components_timestamp 
AFTER UPDATE ON components
BEGIN
    UPDATE components SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_systems_timestamp 
AFTER UPDATE ON systems
BEGIN
    UPDATE systems SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
