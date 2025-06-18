# Hardware Inventory

Project directory:
/home/jem/development/hardware_inventory/

## Project Rules

[[/home/jem/development/ai/prompts/project_maintenance_rules]]

[[/home/jem/development/nara_admin/prompts/restart]]

## About Hardware Inventory

A lightweight, web-based hardware inventory system for tracking computer components across Linux systems. Features automated hardware detection, component tracking, and a simple web interface.

* Automated Hardware Detection: Scans Linux systems to detect CPU, RAM, GPU, storage, and motherboard
* Component Tracking: Track both installed components and spare parts
* Web Interface: Simple, clean web UI for viewing and managing inventory
* One-Line Remote Scanning: Easy system scanning with `curl | bash`
* SQLite Database: Lightweight, file-based storage
* Idempotent Operations: Repeated scans won't create duplicates
* No Agent Required: Scans systems without installing software

# ToDo

Please set up Hardware Inventory as a proper project.

* Setup Hardware Inventory on nara- make sure the port that it uses is free before trying to start the service, there are a lot of running services already. This is partially configured- please check how far progressed this work is.
* Make a small helper script for adding entries to Hardware Inventory in bin/
* Scan the services in systemd and find what ports are in use. Create mappings in Hardware Inventory for each service in systemd. 

