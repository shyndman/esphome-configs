#pragma once

#include <algorithm>
#include <cmath>

#ifndef THERMOSTAT_MIN_TEMP
#define THERMOSTAT_MIN_TEMP 16.0f
#endif

#ifndef THERMOSTAT_MAX_TEMP
#define THERMOSTAT_MAX_TEMP 30.0f
#endif

#ifndef THERMOSTAT_TEMP_STEP
#define THERMOSTAT_TEMP_STEP 0.2f
#endif

#ifndef THERMOSTAT_IDEAL_TEMP
#define THERMOSTAT_IDEAL_TEMP 21.0f
#endif

#ifndef THERMOSTAT_HEAT_OVERRUN
#define THERMOSTAT_HEAT_OVERRUN 0.3f
#endif

#ifndef THERMOSTAT_COOL_OVERRUN
#define THERMOSTAT_COOL_OVERRUN 0.3f
#endif

namespace thermostat::slider {

struct SliderState {
  int track_y;
  int track_height;
  int label_y;
  float setpoint;
};

constexpr float kTempMin = THERMOSTAT_MIN_TEMP;
constexpr float kTempMax = THERMOSTAT_MAX_TEMP;
constexpr float kTempStep = THERMOSTAT_TEMP_STEP;
constexpr float kIdealTemp = THERMOSTAT_IDEAL_TEMP;
constexpr float kHeatOverrun = THERMOSTAT_HEAT_OVERRUN;
constexpr float kCoolOverrun = THERMOSTAT_COOL_OVERRUN;

// Geometry tuned so 21 °C remains near the legacy visual position while
// extending the range to 16–30 °C.
constexpr float kTrackTopY = 120.0f;   // smaller y == hotter
constexpr float kIdealLabelY = 255.0f; // legacy position for 21 °C

constexpr float kSlope = (kIdealLabelY - kTrackTopY) / (kIdealTemp - kTempMax);
constexpr float kIntercept = kTrackTopY - (kSlope * kTempMax);

constexpr int kTrackMinY = static_cast<int>(kTrackTopY + 0.5f);
constexpr int kTrackMaxY = static_cast<int>((kSlope * kTempMin + kIntercept) + 0.5f);

inline float clamp_temperature(float temperature) {
  return std::clamp(temperature, kTempMin, kTempMax);
}

inline float round_to_step(float temperature) {
  return std::round(temperature / kTempStep) * kTempStep;
}

inline int clamp_track_y(int sample_y) {
  return std::clamp(sample_y, kTrackMinY, kTrackMaxY);
}

inline float temperature_from_y(int track_y) {
  float raw_temp = (static_cast<float>(track_y) - kIntercept) / kSlope;
  return clamp_temperature(round_to_step(raw_temp));
}

inline int track_y_from_temperature(float temperature) {
  float clamped_temp = clamp_temperature(temperature);
  float raw_y = (kSlope * clamped_temp) + kIntercept;
  int y = static_cast<int>(std::round(raw_y));
  return clamp_track_y(y);
}

inline int compute_label_y(int track_y) {
  return std::max(50, track_y - 69);
}

inline int compute_track_height(int track_y) {
  return std::max(0, 480 - track_y);
}

inline SliderState compute_state_from_y(int sample_y) {
  SliderState state{};
  state.track_y = clamp_track_y(sample_y);
  state.setpoint = temperature_from_y(state.track_y);
  state.track_y = track_y_from_temperature(state.setpoint);
  state.track_height = compute_track_height(state.track_y);
  state.label_y = compute_label_y(state.track_y);
  return state;
}

inline SliderState compute_state_from_temperature(float temperature) {
  SliderState state{};
  state.setpoint = clamp_temperature(round_to_step(temperature));
  state.track_y = track_y_from_temperature(state.setpoint);
  state.track_height = compute_track_height(state.track_y);
  state.label_y = compute_label_y(state.track_y);
  return state;
}

inline float clamp_cooling(float candidate, float heating_setpoint) {
  float adjusted = clamp_temperature(candidate);
  const float min_gap = kTempStep + kHeatOverrun;
  float min_limit = std::ceil((heating_setpoint + min_gap) / kTempStep) * kTempStep;
  if (min_limit > kTempMax) {
    min_limit = kTempMax;
  }
  float rounded = round_to_step(adjusted);
  if (rounded < min_limit) {
    rounded = min_limit;
  }
  return clamp_temperature(rounded);
}

inline float clamp_heating(float candidate, float cooling_setpoint) {
  float adjusted = clamp_temperature(candidate);
  float limit = cooling_setpoint - (kTempStep + kCoolOverrun);
  float stepped_limit = std::floor(limit / kTempStep) * kTempStep;
  if (stepped_limit < kTempMin) {
    stepped_limit = kTempMin;
  }
  if (adjusted > cooling_setpoint) {
    adjusted = cooling_setpoint;
  }
  if (adjusted > stepped_limit) {
    adjusted = stepped_limit;
  }
  return clamp_temperature(round_to_step(adjusted));
}

inline int track_min_y() { return kTrackMinY; }
inline int track_max_y() { return kTrackMaxY; }

// Backwards-compatible alias.
inline SliderState compute_state(int sample_y) {
  return compute_state_from_y(sample_y);
}

}  // namespace thermostat::slider
