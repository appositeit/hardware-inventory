# Hardware Inventory API Documentation

The Hardware Inventory system provides both a web interface and REST API endpoints for managing hardware inventory data.

## Base URL

The service runs on the configured host and port (default: `http://localhost:5101`)

## Authentication

Currently, no authentication is required. **Note:** This should be addressed for production deployments.

## Content Types

- Request: `application/json`
- Response: `application/json`

## API Endpoints

### System Management

#### Upload System Scan
Upload hardware scan results for a system.

**Endpoint:** `POST /api/upload_scan`

**Request Body:**
```json
{
  "hostname": "server01",
  "manufacturer": "Dell Inc.",
  "model": "PowerEdge R740",
  "uuid": "4C4C4544-0051-4410-8033-C6C04F564831",
  "cpu": {
    "model": "Intel(R) Xeon(R) Silver 4214 CPU @ 2.20GHz",
    "cores": 12,
    "threads": 24,
    "sockets": 2
  },
  "memory": {
    "total_gb": 64,
    "dimms": [
      {
        "size_gb": 16,
        "speed": "2933 MHz",
        "manufacturer": "Samsung",
        "part_number": "M393A2G40DB0-CVF"
      }
    ]
  },
  "storage": [
    {
      "device": "/dev/sda",
      "model": "PERC H730P",
      "size": "1.8T",
      "type": "HDD",
      "serial": "6282DE52000040050025384200000000"
    }
  ],
  "gpu": [
    {
      "model": "Matrox Electronics Systems Ltd. G200eR2",
      "driver": "mgag200"
    }
  ],
  "network": [
    {
      "interface": "eno1",
      "mac": "90:b1:1c:1e:2f:3d",
      "driver": "ixgbe"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully updated inventory for server01"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error description"
}
```

#### Trigger System Scan
Trigger a remote scan of a system (future implementation).

**Endpoint:** `POST /api/scan/{hostname}`

**Response:**
```json
{
  "status": "success",
  "message": "Scan of hostname queued"
}
```

### Component Management

#### Delete Component
Delete a component from the inventory.

**Endpoint:** `POST /component/{component_id}/delete`

**Response:**
```json
{
  "status": "success",
  "message": "Component deleted"
}
```

#### Delete System
Delete a system and all its components.

**Endpoint:** `POST /system/{hostname}/delete`

**Response:**
```json
{
  "status": "success",
  "message": "System deleted"
}
```

### Utility Endpoints

#### Get Scan Script
Returns a bash script that can be piped to bash for easy system scanning.

**Endpoint:** `GET /scan_system`

**Response:** Bash script (Content-Type: text/plain)

Example usage:
```bash
curl http://server:5101/scan_system | bash
curl http://server:5101/scan_system | sudo bash  # For complete hardware info
```

## Data Models

### System Object
```json
{
  "id": 1,
  "hostname": "server01",
  "manufacturer": "Dell Inc.",
  "model": "PowerEdge R740",
  "serial_number": "ABC123",
  "uuid": "4C4C4544-0051-4410-8033-C6C04F564831",
  "last_scan": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T09:00:00Z"
}
```

### Component Object
```json
{
  "id": 1,
  "component_type": "cpu",
  "manufacturer": "Intel",
  "model": "Xeon Silver 4214",
  "serial_number": "N/A",
  "specifications": "{\"cores\": 12, \"threads\": 24}",
  "status": "installed",
  "location": "server01",
  "notes": "Primary CPU",
  "created_at": "2024-01-01T09:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Component Types
- `cpu` - Central Processing Unit
- `memory` - RAM modules
- `storage` - Hard drives, SSDs
- `gpu` - Graphics cards
- `motherboard` - Main board
- `network` - Network interfaces
- `other` - Miscellaneous components

### Component Status
- `installed` - Currently installed in a system
- `spare` - Available spare component
- `retired` - Decommissioned component

## Error Codes

| HTTP Status | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid data |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

## Examples

### Scan and Upload System Data

1. **Generate scan script:**
   ```bash
   curl http://inventory-server:5101/scan_system > scan.sh
   chmod +x scan.sh
   ```

2. **Run scan on target system:**
   ```bash
   ./scan.sh
   # or with sudo for complete info
   sudo ./scan.sh
   ```

3. **One-liner remote scan:**
   ```bash
   curl http://inventory-server:5101/scan_system | sudo bash
   ```

### Manual Component Management

1. **Add a spare component via web interface:**
   - Navigate to `/component/add`
   - Fill in component details
   - Submit form

2. **Delete a component via API:**
   ```bash
   curl -X POST http://inventory-server:5101/component/123/delete
   ```

3. **Delete a system via API:**
   ```bash
   curl -X POST http://inventory-server:5101/system/server01/delete
   ```

## Security Considerations

- **No Authentication:** The current implementation has no authentication
- **Network Exposure:** Service binds to 0.0.0.0 by default
- **Data Validation:** Limited input validation is performed
- **CSRF Protection:** No CSRF protection implemented

For production deployments, consider:
- Adding authentication (OAuth2, API keys, etc.)
- Implementing HTTPS
- Adding rate limiting
- Input validation and sanitisation
- Reverse proxy with authentication
- Network access controls

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting for production use.

## Pagination

The web interface handles pagination automatically. API endpoints currently return all results without pagination.

## Versioning

The current API is version 1 (implicit). Future versions should use URL versioning (e.g., `/api/v2/`).
