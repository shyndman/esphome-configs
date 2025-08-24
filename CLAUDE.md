# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an ESPHome configuration repository for managing IoT devices in a home automation setup. The codebase consists of YAML configuration files that define device behavior for ESP32/ESP8266 microcontrollers integrated with Home Assistant.

## Architecture and Structure

### Core Configuration Pattern
- **Device Files**: Individual `.esp.yaml` files define specific devices (e.g., `bedside-lamp.esp.yaml`, `thermostat-display.esp.yaml`)
- **Packages System**: Reusable configuration components in `/packages/` directory that are included using `!include`
- **Base Configuration**: `packages/device-base.esp.yaml` provides common functionality (WiFi, API, OTA, logging, sensors)
- **IP Management**: `packages/device-ip-map.esp.yaml` centrally manages static IP assignments using substitutions
- **Secrets**: `secrets.yaml` contains WiFi credentials and other sensitive data (excluded from version control)

### Key Packages
- `device-base.esp.yaml` - Essential services and sensors for all devices
- `athom-*.esp.yaml` - Hardware-specific configs for Athom smart devices
- `mm-wave-presence.esp.yaml` - Millimeter wave presence detection
- `ble-beacon-tracker.esp.yaml` - Bluetooth beacon tracking
- Hardware-specific packages for ESP32C3, ESP32S3 variants

### Directory Structure
- `/packages/` - Reusable configuration modules
- `/scratch/` - Development and testing configurations
- `/archive/` - Deprecated configurations
- `/assets/` - Images and media files
- `/include/` - Partition tables and other includes
- `/support/` - Arduino code for supporting hardware (timer MCU)

## Common Development Tasks

### Adding New Devices
1. Create new `.esp.yaml` file with appropriate naming
2. Include relevant packages (always include `device-base.esp.yaml`)
3. Add static IP to `packages/device-ip-map.esp.yaml`
4. Define substitutions for `friendly_name` and `name`

### ESPHome Commands
- Validate configuration: `esphome config <device>.esp.yaml`
- Compile firmware: `esphome compile <device>.esp.yaml` 
- Upload to device: `esphome upload <device>.esp.yaml`
- Monitor logs: `esphome logs <device>.esp.yaml`
- Clean build files: `esphome clean <device>.esp.yaml`

### Package Development
- Create reusable components in `/packages/` directory
- Use substitutions for configurable parameters
- Follow existing naming patterns (`.esp.yaml` extension)
- Test with scratch devices before deploying

## Configuration Conventions

### Naming
- Device files: `<device-name>.esp.yaml` (kebab-case)
- Package files: `<component-name>.esp.yaml` 
- Substitution variables: `friendly_name` and `name` are standard
- IP substitutions: `ip_<device_name_with_underscores>`

### IP Address Scheme
- Base network: 192.168.85.x and 192.168.86.x
- Thermostat devices: .26-.27
- Lighting: .28, .43-.48
- Smart plugs: .60-.63
- Utility devices: .220, .228
- Presence sensors: .04, .229-.232
- Sensor suites: .10-.21
- Scratch/development: .05-.08

### Hardware Platforms
- ESP32-S3 devices often require PSRAM configuration
- Custom partition tables available in `/include/`
- Platform-specific settings handled via packages

## Testing and Validation
- Use `scratch-device.esp.yaml` for development and testing
- Validate configurations before deployment: `esphome config`
- Monitor device logs during development: `esphome logs`
- Test OTA updates before deploying to production devices