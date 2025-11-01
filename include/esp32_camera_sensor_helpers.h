#pragma once

#include "esp_camera.h"

namespace espcam_helpers {

inline sensor_t *sensor() { return esp_camera_sensor_get(); }

inline void set_sharpness(int level) {
  if (auto *s = sensor(); s != nullptr && s->set_sharpness != nullptr) {
    s->set_sharpness(s, level);
  }
}

inline void set_denoise(bool enable) {
  if (auto *s = sensor(); s != nullptr && s->set_denoise != nullptr) {
    s->set_denoise(s, enable ? 1 : 0);
  }
}

inline void set_quality(int quality) {
  if (auto *s = sensor(); s != nullptr && s->set_quality != nullptr) {
    s->set_quality(s, quality);
  }
}

inline void set_raw_gma(bool enable) {
  if (auto *s = sensor(); s != nullptr && s->set_raw_gma != nullptr) {
    s->set_raw_gma(s, enable ? 1 : 0);
  }
}

inline void set_dcw(bool enable) {
  if (auto *s = sensor(); s != nullptr && s->set_dcw != nullptr) {
    s->set_dcw(s, enable ? 1 : 0);
  }
}

inline void set_awb_gain(bool enable) {
  if (auto *s = sensor(); s != nullptr && s->set_awb_gain != nullptr) {
    s->set_awb_gain(s, enable ? 1 : 0);
  }
}

}  // namespace espcam_helpers
