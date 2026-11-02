#pragma once

#include <cstddef>
#include <cstdint>

#include "driver/gpio.h"
#include "driver/i2s_std.h"
#include "esp_err.h"

// create class ics43434
// Owns one I2S RX channel. Use from a single task; do not copy or move.
class Ics43434 {
public:
    struct Config {
        gpio_num_t bclk = GPIO_NUM_NC; // Microphone SCK/BCLK, NC == null
        gpio_num_t ws = GPIO_NUM_NC;   // Microphone WS/LRCLK
        gpio_num_t din = GPIO_NUM_NC;  // Microphone SD -> ESP32 input
        uint32_t sample_rate_hz = 16000;  // Sample_Rate , Nyqusits = 8000hz
        bool right_channel = false;   // false: LR -> GND; true: LR -> 3V3
    };

    Ics43434() = default;    
    ~Ics43434();

    Ics43434(const Ics43434 &) = delete;                 // Cấm tạo đối tượng mới bằng cách sao chép đối tượng cũ
    Ics43434 &operator=(const Ics43434 &) = delete;      // Cấm gán 1 đối tượng bằng đối tượng khác
    Ics43434(Ics43434 &&) = delete;                      // Cấm chuyển tài nguyên từ đối tượng này sang đối tượng khác
    Ics43434 &operator=(Ics43434 &&) = delete;           // Cấm chuyển tài nguyên giữa 2 đối tượng public

    // Allocates/enables I2S and discards 200 ms of startup audio.
    // Does not detect whether a physical microphone is connected.
    // Các hàm public, Header khai báo 4 thành phần chính
    esp_err_t begin(const Config &config);          // Hàm khởi tạo microphone
    esp_err_t end();                                // Hàm dừng
    bool is_started() const { return running_; }    // Hàm kiểm tra trạng thái

    // Blocking read; capacity and samples_read are SAMPLE counts, not bytes.
    // Output: signed 24-bit PCM in int32_t [-8388608, 8388607].
    // On timeout, samples_read may be nonzero: those samples are valid.
    // timeout_ms uses milliseconds, not FreeRTOS ticks.
    esp_err_t read(int32_t *samples, size_t capacity, size_t &samples_read,
                   uint32_t timeout_ms = 1000);

    // Convert one returned PCM sample to approximately [-1, 1).
    static float to_float(int32_t sample) { return sample / 8388608.0f; }  // chuyển mẫu âm thành PCM 24-bit sang thành số thực [-1,1)

private:
    i2s_chan_handle_t rx_ = nullptr;
    bool running_ = false;
};
