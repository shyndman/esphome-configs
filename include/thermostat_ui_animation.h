#pragma once

#include <cstdint>

#include "lvgl.h"

namespace thermostat::ui {

namespace {

struct ColorAnimRequest {
  lv_obj_t *obj;
  lv_color_t from;
  lv_color_t to;
  bool is_text;
  lv_part_t part;
  uint16_t duration_ms;
  ColorAnimRequest *next;
};

inline void start_color_animation(ColorAnimRequest *request);

inline void color_anim_ready_cb(lv_anim_t *anim) {
  auto *request = static_cast<ColorAnimRequest *>(lv_anim_get_user_data(anim));
  if (!request) {
    return;
  }

  if (request->is_text) {
    lv_obj_set_style_text_color(request->obj, request->to, request->part);
  } else {
    lv_obj_set_style_bg_color(request->obj, request->to, request->part);
  }

  auto *next = request->next;
  delete request;
  if (next != nullptr) {
    start_color_animation(next);
  }
}

inline void start_color_animation(ColorAnimRequest *request) {
  if (request == nullptr) {
    return;
  }

  if (request->is_text) {
    lv_obj_set_style_text_color(request->obj, request->from, request->part);
  } else {
    lv_obj_set_style_bg_color(request->obj, request->from, request->part);
  }

  lv_anim_t anim;
  lv_anim_init(&anim);
  lv_anim_set_var(&anim, request);
  lv_anim_set_user_data(&anim, request);
  lv_anim_set_values(&anim, 0, 255);
  lv_anim_set_time(&anim, request->duration_ms);
  lv_anim_set_path_cb(&anim, lv_anim_path_ease_in_out);

  lv_anim_set_exec_cb(&anim, [](void *var, int32_t value) {
    auto *req = static_cast<ColorAnimRequest *>(var);
    if (req == nullptr) {
      return;
    }
    lv_color_t mixed = lv_color_mix(req->to, req->from, static_cast<uint8_t>(value));
    if (req->is_text) {
      lv_obj_set_style_text_color(req->obj, mixed, req->part);
    } else {
      lv_obj_set_style_bg_color(req->obj, mixed, req->part);
    }
  });

  lv_anim_set_ready_cb(&anim, color_anim_ready_cb);
  lv_anim_start(&anim);
}

inline ColorAnimRequest *make_color_request(lv_obj_t *obj, uint32_t from_hex,
                                            uint32_t to_hex, uint16_t duration_ms,
                                            bool is_text, lv_part_t part) {
  auto *request = new ColorAnimRequest{
      obj,
      lv_color_hex(from_hex),
      lv_color_hex(to_hex),
      is_text,
      part,
      duration_ms,
      nullptr,
  };
  return request;
}

}  // namespace

inline void animate_two_stage_color(lv_obj_t *obj, uint32_t start_color, uint32_t mid_color,
                                    uint32_t end_color, uint16_t stage_duration_ms,
                                    bool is_text, lv_part_t part = LV_PART_MAIN) {
  auto *stage2 = make_color_request(obj, mid_color, end_color, stage_duration_ms, is_text, part);
  auto *stage1 = make_color_request(obj, start_color, mid_color, stage_duration_ms, is_text, part);
  stage1->next = stage2;
  start_color_animation(stage1);
}

}  // namespace thermostat::ui
