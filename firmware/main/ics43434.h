#pragma once

#include <cstddef>
#include <cstdint>

#include "driver/gpio.h"
#include "driver/i2s_std.h"
#include "esp_err.h"

// Owns one I2S RX channel. Use from a single task; do not copy or move.
class Ics43434 {
public:
    struct Config {
        gpio_num_t bclk = GPIO_NUM_NC; // Microphone SCK/BCLK
        gpio_num_t ws = GPIO_NUM_NC;   // Microphone WS/LRCLK
        gpio_num_t din = GPIO_NUM_NC;  // Microphone SD -> ESP32 input
        uint32_t sample_rate_hz = 16000;
        bool right_channel = false;   // false: LR -> GND; true: LR -> 3V3
    };

    Ics43434() = default;
    ~Ics43434();
    Ics43434(const Ics43434 &) = delete;
    Ics43434 &operator=(const Ics43434 &) = delete;
    Ics43434(Ics43434 &&) = delete;
    Ics43434 &operator=(Ics43434 &&) = delete;

    // Allocates/enables I2S and discards 200 ms of startup audio.
    // Does not detect whether a physical microphone is connected.
    esp_err_t begin(const Config &config);
    esp_err_t end();
    bool is_started() const { return running_; }

    // Blocking read; capacity and samples_read are SAMPLE counts, not bytes.
    // Output: signed 24-bit PCM in int32_t [-8388608, 8388607].
    // On timeout, samples_read may be nonzero: those samples are valid.
    // timeout_ms uses milliseconds, not FreeRTOS ticks.
    esp_err_t read(int32_t *samples, size_t capacity, size_t &samples_read,
                   uint32_t timeout_ms = 1000);

    // Convert one returned PCM sample to approximately [-1, 1).
    static float to_float(int32_t sample) { return sample / 8388608.0f; }

private:
    i2s_chan_handle_t rx_ = nullptr;
    bool running_ = false;
};
