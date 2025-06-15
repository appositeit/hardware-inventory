# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Hardware Inventory System
- Web-based interface for hardware inventory management
- Automated hardware detection for Linux systems
- Support for CPU, memory, storage, GPU, and motherboard detection
- One-line remote scanning with `curl | bash`
- Component tracking for both installed and spare parts
- SQLite database backend
- Systemd service integration
- Security hardening options for production deployment
- RESTful API endpoints
- Bootstrap-based responsive web interface

### Features
- 🔍 Automated hardware detection without agents
- 📦 Component and spare parts tracking
- 🌐 Clean, responsive web interface
- 🚀 One-line system scanning
- 💾 Lightweight SQLite storage
- 🔄 Idempotent scan operations
- 🔧 No software installation required on target systems

### Security
- Systemd security hardening
- Limited file system access
- Non-privileged execution mode
- Temporary directory isolation

## [1.0.0] - 2025-06-15

### Added
- Initial project structure
- Core hardware detection functionality
- Web interface implementation
- Database schema and management
- Installation and setup scripts
- Comprehensive documentation
- MIT license
