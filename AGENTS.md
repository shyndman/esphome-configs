# Repository Guidelines

> Heads-up: if you notice in-progress edits when you hop in, it usually means I'm working on the repo at the same time—feel free to coordinate rather than undoing the changes.

## Project Structure & Module Organization
- Root `*.esp.yaml` files define deployed devices; include `packages/device-base.esp.yaml` plus hardware modules such as `packages/esp32-base.esp.yaml` or `packages/mm-wave-presence-compact.esp.yaml`.
- Shared building blocks live in `packages/`; update `packages/device-ip-map.esp.yaml` when reserving static addresses, and keep lighting effects under `packages/light-effects/`.
- Use `scratch/` for prototypes, `archive/` for retired configs, `assets/` for media, and `include/` for partition CSVs; `support/` holds helper sketches referenced by device configs.

## Build, Test & Development Commands
- `esphome config thermostat-display.esp.yaml` validates syntax, secrets, and substitutions without contacting hardware.
- `esphome compile <device>.esp.yaml` builds firmware into `build/<device>/`; share the `.bin` from that directory when collaborating.
- `esphome upload --device /dev/ttyUSB0 <device>.esp.yaml` flashes via USB, while `esphome upload <device>.esp.yaml` performs OTA once trusted.
- `esphome logs <device>.esp.yaml` tails runtime output, and `esphome clean <device>.esp.yaml` clears cached builds.

## Coding Style & Naming Conventions
- Indent YAML with two spaces and prefer explicit sections over anchors to keep diffs readable.
- Device and package filenames use kebab-case (`office-ring-light.esp.yaml`); substitutions stay snake_case, and IDs follow ESPHome’s lowercase_with_underscores style.
- Reference secrets via `!secret` and store sensitive values only in `secrets.yaml`.

## Testing Guidelines
- Run `esphome config` before every commit and add `esphome compile` when touching shared packages or platform settings.
- Trial risky work inside `scratch-device.esp.yaml` to isolate OTA devices from regressions.
- Capture a short `esphome logs` session for new sensors or displays to confirm components boot and memory usage fits the selected partition.

## Commit & Pull Request Guidelines
- Follow the existing history: concise, imperative commit subjects such as “Remove computationally expensive Bluetooth tracking.”
- Keep each commit focused; include relevant CLI output in the body when validation or logs motivated the change.
- Pull requests should name the affected device(s), list touched packages, and call out new secrets or IP assignments; attach screenshots or logs when altering UI or presence sensors.

## Security & Configuration Tips
- Keep secrets out of version control; provide `.example` placeholders under `support/` when guidance is required.
- Select the correct partition CSV from `include/` before enabling large assets or PSRAM-heavy features.
- Store source animations or icons in `assets/` and note the generator script (`scripts/create_sliding_text_gif.py`) so others can reproduce them.

## Thermostat Display Stack
- `thermostat-display.esp.yaml` is the deployed LVGL touchscreen on the LilyGO T-Panel S3; it pulls in `packages/thermostat/display-ui.esp.yaml`, which composes shared defaults, assets, runtime scripts, data sources, and the LVGL layout under `packages/thermostat/ui/`.
- `thermostat-display-desktop.esp.yaml` runs the same UI against SDL display/touch backends for fast iteration on a desktop; it overrides the idle timeout, disables antiburn, and swaps the time source to `host`.
- Runtime behaviour (animations, slider math, HA service calls) lives in `packages/thermostat/ui/runtime.esp.yaml` with helpers in `include/thermostat_slider_state.h` and `include/thermostat_ui_animation.h`; the LVGL widget tree is defined in `packages/thermostat/ui/layout.esp.yaml`.
- Home Assistant entities feed the UI through `packages/thermostat/ui/data-sources.esp.yaml`; the matching climate brain is `thermostat-controller.esp.yaml`, which exposes `climate.thermostat_climate_ctrl_climate_control` and the sensors the display expects.
- For changes, run `esphome config thermostat-display.esp.yaml` (and the desktop variant when tweaking UI) before committing; capture `esphome logs` once on hardware to verify memory and antiburn behaviour.
