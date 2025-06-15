# Contributing to Hardware Inventory System

Thank you for your interest in contributing to the Hardware Inventory System! This document provides guidelines and information for contributors.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Linux-based system (for hardware detection)
- Git
- Basic understanding of Flask and SQLite

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/hardware-inventory.git
   cd hardware-inventory
   ```

2. **Set up the development environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   ```bash
   ./setup.sh -y
   ```

4. **Run the development server:**
   ```bash
   cd src && python3 web_interface.py
   ```

## Contributing Guidelines

### Reporting Issues

- Use the GitHub issue tracker
- Include system information (OS, Python version)
- Provide clear reproduction steps
- Include relevant logs or error messages

### Submitting Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clear, commented code
   - Follow PEP 8 style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   # Run basic functionality tests
   cd src && python3 inventory_manager.py scan
   cd src && python3 web_interface.py
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: Brief description of your change"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use clear, descriptive commit messages:
- `Add: New feature description`
- `Fix: Bug fix description`
- `Update: Change description`
- `Remove: Removal description`
- `Docs: Documentation changes`

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Comment complex logic

### Testing

- Test on multiple Linux distributions when possible
- Verify hardware detection works with and without sudo
- Test web interface functionality
- Ensure database operations are idempotent

## Project Structure

```
hardware-inventory/
├── src/                    # Python source files
│   ├── inventory_manager.py    # Core inventory management
│   └── web_interface.py        # Flask web application
├── scripts/                # Shell scripts
│   └── detect_hardware.sh     # Hardware detection script
├── templates/              # HTML templates
├── static/                 # Static files (CSS, images)
├── systemd/                # Systemd service files
├── data/                   # Database storage (created on setup)
├── tests/                  # Test files (future)
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── install.sh             # Installation script
├── schema.sql             # Database schema
├── README.md              # Main documentation
├── CHANGELOG.md           # Version history
├── CONTRIBUTING.md        # This file
└── LICENSE                # MIT license
```

## Development Priorities

### High Priority
- Add authentication system
- Implement proper memory DIMM detection
- Add CSV/Excel export functionality
- Create comprehensive test suite

### Medium Priority
- REST API documentation
- Support for Windows/macOS systems
- Email notifications for changes
- Barcode/QR code support

### Low Priority
- Performance optimizations
- Additional hardware component types
- Advanced reporting features

## Questions?

Feel free to:
- Open an issue for discussion
- Contact the maintainers
- Check existing documentation

Thank you for contributing!
