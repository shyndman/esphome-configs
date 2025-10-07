# Repository Guidelines

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
