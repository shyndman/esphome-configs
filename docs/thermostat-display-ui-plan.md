# Thermostat Display UI Modernization Plan

## Goals
- Enable editing for both cooling and heating setpoints via the existing slider.
- Support fan mode toggling with the current button behaviour.
- Preserve the established layout; focus on interaction, animation, and data integrity.

## Interaction Overview
- **Active target selection:** Tap either temperature label to make it active. Only one target is editable at a time.
- **Initial state:** Heating setpoint is active after boot or data reload. Cooling remains passive until selected.
- **Dragging:** Touch-and-drag behaviour mirrors the current slider experience. Dragging updates the active setpoint preview immediately but only applies changes when the user releases the screen.
- **Fan button:** Existing toggle and visual feedback remain unchanged.

## Visual & Animation Requirements
- **Neutral transition style:** Introduce `transition_neutral_color` (#303030) for intermediary fades.
- **Color sources:** Use `warming_color` for heating and `cooling_color` for cooling. No alternative palettes.
- **Animation cadence:** Total duration 120 ms (ease-in-out). Stage 1 (0–60 ms) transitions the track and labels to the neutral style; Stage 2 (60–120 ms) transitions from neutral to the target accent. Stage boundaries align across all affected widgets.
- **Track height:** Animates continuously over the full 120 ms, syncing with color changes.
- **Inactive label:** Animates toward its existing gray (`#292929`) whenever it loses focus. No animation when tapping the already-active label.
- **Track representation:** Only the active setpoint drives the slider geometry. The inactive setpoint remains a static label.

## Temperature Handling
- **Display format:** Round to nearest whole degree before showing text. Internal math uses 0.2 °C increments.
- **Slider mapping:** Expand range to cover 16–30 °C while keeping 21 °C near its current visual position (“ideal”). Adjust the mapping function accordingly.
- **Setpoint ordering:** Prevent heating from exceeding cooling and vice versa. Clamp edits using controller overruns.
  - Cooling upper bound: `ceil((heating + 0.2 + heat_overrun) / 0.2) * 0.2`.
  - Heating lower bound: `floor((cooling - 0.2 - cool_overrun) / 0.2) * 0.2`.
- **Overrun sharing:** Extract shared constants for `heat_overrun` and `cool_overrun` so both the controller and UI consume the same values.

## Data Flow & State Management
- Maintain globals for both setpoints, current track geometry, drag state, active target, and animation progression.
- Update the inactive label when Home Assistant pushes a new value but keep the slider parked on the active target until it changes.
- On load, populate both setpoints, then immediately align the slider visuals with the heating target.
- Continue to debounce climate updates via `apply_cooling_setpoint` et al., extending logic to handle the active target generically.

## Implementation Steps
1. **Shared constants:** Introduce a common include/substitution for temperature bounds and overruns; refactor controller and UI to reference it.
2. **Globals & helpers:** Replace single-setpoint globals with active-target metadata and extend `thermostat::slider` helpers to support 16–30 °C with 0.2 °C steps plus whole-degree display helpers.
3. **Touch handling:** Generalize drag/tap logic to swap between heating and cooling. Ensure clamps respect the overrun formulas and 0.2 °C increments.
4. **Animation wiring:** Define LVGL animation timelines for the 120 ms dual-stage color changes and synchronized track height updates. Add the `transition_neutral_color` style.
5. **Fan mode visuals:** Keep existing button refresh logic; adjust only if shared styles require updates.
6. **Home Assistant syncing:** Update `on_value` handlers so inactive targets refresh labels without disturbing the active slider, and active targets snap immediately.
7. **Testing:** Run `esphome config thermostat-display.esp.yaml` and verify animation/touch behaviour on hardware or simulator, ensuring setpoint limits hold and no cross-over occurs.

## Open Questions / Follow-ups
- Revisit inactive-target visualization (ghost track, dual markers) after the base interaction feels right.
- Consider persisting the last-active target if user feedback suggests it.
- Assess whether we need a dedicated easing constant for reuse across animations.
