# Hardware Inventory System

A lightweight, web-based hardware inventory system for tracking computer components across Linux systems. Features automated hardware detection, component tracking, and a simple web interface.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🔍 **Automated Hardware Detection**: Scans Linux systems to detect CPU, RAM, GPU, storage, and motherboard
- 📦 **Component Tracking**: Track both installed components and spare parts
- 🌐 **Web Interface**: Simple, clean web UI for viewing and managing inventory
- 🚀 **One-Line Remote Scanning**: Easy system scanning with `curl | bash`
- 💾 **SQLite Database**: Lightweight, file-based storage
- 🔄 **Idempotent Operations**: Repeated scans won't create duplicates
- 🔧 **No Agent Required**: Scans systems without installing software

## Screenshots

The web interface provides an easy way to view and manage your hardware inventory:
- Dashboard with component statistics
- System list with component counts
- Detailed component views
- Spare parts tracking

## Quick Start

### One-Line Scanner

From any Linux system, run:

```bash
# Basic scan
curl http://your-server:5000/scan_system | bash

# Full scan with sudo (recommended for complete details)
curl http://your-server:5000/scan_system | sudo bash
```

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/hardware-inventory.git
cd hardware-inventory
```

2. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

3. **Run setup:**
```bash
./setup.sh -y  # -y flag for automatic setup
```

4. **Start the web interface:**
```bash
cd src && python3 web_interface.py
```

5. **Open your browser to:** http://localhost:5000

### Systemd Service Installation

For production use, install as a systemd service:

```bash
sudo ./install.sh --path /opt/hardware-inventory
sudo systemctl start hardware-inventory
sudo systemctl enable hardware-inventory
```

## Usage

### Command Line Interface

**Scan local system:**
```bash
cd src && sudo python3 inventory_manager.py scan
```

**Scan remote system (requires SSH keys):**
```bash
cd src && python3 inventory_manager.py scan --hostname remote-server
```

**Add spare component:**
```bash
cd src && python3 inventory_manager.py add-spare \
  --type gpu \
  --manufacturer "NVIDIA" \
  --model "GeForce RTX 3080" \
  --location "Shelf A"
```

**List all components:**
```bash
cd src && python3 inventory_manager.py list
```

### Web Interface Features

- **Dashboard**: Overview of all components and systems
- **Systems**: List of scanned computers with their components
- **Components**: All components with filtering by type and status
- **Add Component**: Manually add spare parts
- **Edit/Delete**: Edit component details or delete components/systems
- **Scan Systems**: Instructions and one-liner commands for scanning

## What Gets Detected

| Component | Details Collected | Requires Sudo |
|-----------|------------------|---------------|
| CPU | Model, cores, threads, sockets | No |
| Memory | Total capacity, DIMM details | Yes (for DIMM info) |
| Storage | Model, size, serial, type (SSD/HDD) | No |
| GPU | Graphics card model | No |
| Motherboard | Manufacturer, model, serial | Yes |
| System | Manufacturer, model, UUID | Yes |

## Project Structure

```
hardware-inventory/
├── src/                    # Python source files
│   ├── inventory_manager.py
│   └── web_interface.py
├── scripts/                # Shell scripts
│   └── detect_hardware.sh
├── templates/              # HTML templates
├── static/                 # Static files (CSS, images)
├── systemd/                # Systemd service files
├── data/                   # Database storage (created on setup)
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── install.sh             # Installation script
└── schema.sql             # Database schema
```

## Requirements

- Linux-based systems (for hardware detection)
- Python 3.6+
- Flask 2.0+
- Standard Linux tools: `lscpu`, `lsblk`, `lspci`
- Optional: `dmidecode` for complete hardware details (requires sudo)

## Security Considerations

- The web interface binds to all interfaces by default (0.0.0.0:5000)
- No authentication is included - add a reverse proxy with auth for production
- The systemd service includes security hardening options
- Remote scanning requires SSH key authentication

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Background pattern by [Ai18io81](https://www.dreamstime.com/ai18io81_info) via [Dreamstime](https://www.dreamstime.com/)
- Built with Flask, SQLite, and various Linux hardware detection tools

## Troubleshooting

### Common Issues

**Missing dmidecode:** Install with your package manager:
- Debian/Ubuntu: `sudo apt-get install dmidecode`
- RHEL/CentOS: `sudo yum install dmidecode`
- Fedora: `sudo dnf install dmidecode`

**Permission denied:** Ensure scripts are executable:
```bash
chmod +x setup.sh scripts/detect_hardware.sh
```

**Database errors:** Check data directory permissions:
```bash
mkdir -p data
chmod 755 data
```

## Roadmap

- [ ] Add authentication system
- [ ] Implement proper memory DIMM detection
- [ ] Add CSV/Excel export functionality
- [ ] Create REST API documentation
- [ ] Add support for Windows/macOS systems
- [ ] Implement email notifications for changes
- [ ] Add barcode/QR code support for physical tracking
