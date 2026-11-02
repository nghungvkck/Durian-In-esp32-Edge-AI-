#pragma once

#include <cstddef>
#include "esp_err.h"

esp_err_t resize_spectrogram(
    const float *input,
    size_t input_height,
    size_t input_width,
    float *output,
    size_t output_height,
    size_t output_width,
    size_t output_capacity
);