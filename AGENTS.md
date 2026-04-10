# Repository Guidelines
## Project Overview
This repository is an ESPHome configuration monorepo for Home Assistant-connected ESP32/ESP8266 devices (lighting, presence, plugs, displays, thermostat control, utility sensors). Top-level `*.esp.yaml` files are deployable device entrypoints; shared behavior is composed from `packages/`.

## Architecture & Data Flow
- **Composition model:** Device files include reusable package modules via `packages:` + `!include` (example: `thermostat-controller.esp.yaml`, `packages/device-base.esp.yaml`).
- **Shared base layer:** `packages/device-base.esp.yaml` centralizes Wi-Fi, API, OTA, logging, time sync, diagnostics, and static IP wiring via `packages/device-ip-map.esp.yaml`.
- **Thermostat stack (package-driven):**
  - Controller/brain: `thermostat-controller.esp.yaml`
  - Shared defaults: `packages/thermostat/defaults.esp.yaml`
- **Data flow pattern:**
  1. Home Assistant entities feed ESPHome sensors/text/binary sensors (`platform: homeassistant`).
  2. `on_value`/`on_state` handlers update globals and UI state (LVGL widgets/scripts).
  3. User interactions or automation scripts write back to HA via `homeassistant.service` (for example `climate.set_temperature`).
  4. Controller computes final relay states and drives GPIO outputs (`thermostat-controller.esp.yaml`).

## Key Directories
- `./` — deployable device configs (`*.esp.yaml`)
- `packages/` — reusable modules (hardware bases, feature packs, effects)
- `include/` — C++ helpers and partition CSVs included by ESPHome
- `assets/` — icons, animation frames, fonts
- `scripts/` — asset generation and repo sync helpers
- `scratch/` — prototype/safe experimentation configs
- `archive/` — retired configs
- `support/` — auxiliary firmware/sketches
- `docs/` — design notes and hardware references

## Development Commands
- After making any change, always run `esphome config <device>.esp.yaml` and `esphome build <device>.esp.yaml` locally to ensure the configuration still validates and compiles before moving on.
- Validate config: `esphome config <device>.esp.yaml`
- Compile firmware: `esphome compile <device>.esp.yaml`
- Flash over USB: `esphome upload --device /dev/ttyUSB0 <device>.esp.yaml`
- Flash OTA: `esphome upload <device>.esp.yaml`
- Stream logs: `esphome logs <device>.esp.yaml`
- Clean build artifacts: `esphome clean <device>.esp.yaml`

Useful helpers:
- Generate fan frames: `./scripts/generate-fan-animation-frames.sh`
- Create sliding text GIF: `uv run scripts/create_sliding_text_gif.py --help`
- Measure rendered text: `uv run scripts/measure_string.py --help`

## Code Conventions & Common Patterns
- **Formatting:** YAML uses two-space indentation; prefer explicit sections over anchors for readability.
- **Naming:**
  - Device/package filenames: kebab-case (`office-ring-light.esp.yaml`)
  - Substitutions: snake_case (`friendly_name`, `name`, `ip_<device_name>`)
  - IDs: lowercase_with_underscores (`cooling_setpoint_temp`)
- **New config checklist:** when adding a new deployable config, add its `ip_<device_name>` substitution to `packages/device-ip-map.esp.yaml` before validating or building.
- **Reuse/composition:** build features as packages, parameterize with `substitutions`, and include from device entrypoints.
- **State management pattern:**
  - transient runtime state in `globals`
  - business/UI transitions in `script` blocks (`mode: restart` / `single`)
  - event triggers in `on_value`, `on_state`, `on_press`, `interval`
- **Error/fallback handling in lambdas:** guard invalid inputs (`std::isnan`, null checks), early-return on bad state, and emit targeted logs (`ESP_LOGD/W/I`, `logger.log`).
- **Async/event model:** event-driven automations, not async/await. Timing via `delay`, `interval`, and component callbacks.
- **Dependency injection style:** use substitutions and package includes rather than framework DI.
- **Secrets:** always reference sensitive values with `!secret`; keep secrets only in `secrets.yaml`.

## Important Files
- `packages/device-base.esp.yaml` — base stack used by most devices
- `packages/device-ip-map.esp.yaml` — centralized static IP substitution map
- `thermostat-controller.esp.yaml` — thermostat climate control + relay orchestration
- `packages/thermostat/defaults.esp.yaml` — shared thermostat substitutions and defaults
- `include/thermostat_slider_state.h` — setpoint/slider math
- `include/thermostat_ui_animation.h` — LVGL color animation helper
- `scratch-device.esp.yaml` — safe staging area for risky experiments

## Runtime/Tooling Preferences
- Primary runtime/toolchain: **ESPHome CLI** (PlatformIO/ESP-IDF configured per device/package).
- Python helper scripts are first-class tooling; several are `uv` scripts (`#!/usr/bin/env -S uv run --script`).
- No Node/Bun package manager workflow is defined in this repo.
- Local `.venv/` is used for tooling dependencies; repo ignores `.venv`, `.esphome/`, `build/`, and `secrets.yaml`.

## Testing & QA
- No formal unit-test framework or CI pipeline is defined in-repo.
- QA is command-driven and hardware-observed:
  1. `esphome config <device>.esp.yaml` for every change.
  2. `esphome compile <device>.esp.yaml` when touching shared packages/platform settings.
  3. `esphome logs <device>.esp.yaml` to verify boot/runtime behavior after deploy.
- Use `scratch/` or `scratch-device.esp.yaml` for high-risk iteration before touching production device configs.
- For UI/sensor changes, capture short runtime logs (and screenshots when visual behavior changes) as evidence.
