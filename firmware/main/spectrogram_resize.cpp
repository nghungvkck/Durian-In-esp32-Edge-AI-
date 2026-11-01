#include "spectrogram_resize.h"
#include <cmath>

esp_err_t resize_spectrogram(
    const float *input,
    size_t input_height,
    size_t input_width,
    float *output,
    size_t output_height,
    size_t output_width,
    size_t output_capacity
) {
    if (!input || !output ||
        input_height == 0 || input_width == 0 ||
        output_height == 0 || output_width == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    if (output_height > SIZE_MAX / output_width ||
        output_capacity < output_height * output_width) {
        return ESP_ERR_INVALID_SIZE;
    }

    for (size_t y = 0; y < output_height; y++) {
        float src_y = (y + 0.5f) * input_height / output_height - 0.5f;
        src_y = fmaxf(0.0f, fminf(src_y, input_height - 1.0f));

        size_t y0 = static_cast<size_t>(src_y);
        size_t y1 = (y0 + 1 < input_height) ? y0 + 1 : y0;
        float dy = src_y - y0;

        for (size_t x = 0; x < output_width; x++) {
            float src_x = (x + 0.5f) * input_width / output_width - 0.5f;
            src_x = fmaxf(0.0f, fminf(src_x, input_width - 1.0f));

            size_t x0 = static_cast<size_t>(src_x);
            size_t x1 = (x0 + 1 < input_width) ? x0 + 1 : x0;
            float dx = src_x - x0;

            float top = input[y0 * input_width + x0] * (1.0f - dx)
                      + input[y0 * input_width + x1] * dx;

            float bottom = input[y1 * input_width + x0] * (1.0f - dx)
                         + input[y1 * input_width + x1] * dx;

            output[y * output_width + x] = top * (1.0f - dy)
                                         + bottom * dy;
        }
    }

    return ESP_OK;
}