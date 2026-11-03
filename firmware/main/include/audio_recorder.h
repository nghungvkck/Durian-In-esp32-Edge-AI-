#pragma once

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include "driver/gpio.h"
#include "esp_err.h"
#include "ics43434.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

class AudioRecorder {
public:
    // MicroSD SPI pins.
    static constexpr gpio_num_t SD_MISO_PIN = GPIO_NUM_4;
    static constexpr gpio_num_t SD_MOSI_PIN = GPIO_NUM_5;
    static constexpr gpio_num_t SD_SCK_PIN = GPIO_NUM_6;
    static constexpr gpio_num_t SD_CS_PIN = GPIO_NUM_7;

    static constexpr uint32_t SAMPLE_RATE_HZ = 16000;      // Sample rate in Hz

    AudioRecorder() = default;
    ~AudioRecorder();

    AudioRecorder(const AudioRecorder &) = delete;
    AudioRecorder &operator=(const AudioRecorder &) = delete;

    esp_err_t init();  // Initializes the audio recorder and allocates buffer in PSRAM.
    esp_err_t start(Ics43434 &mic, const char *file_path);
    esp_err_t stop();  // Stops recording audio from the microphone.
    bool is_recording() const;

private:
    static constexpr size_t CHUNK_SAMPLES = 1024;
    static constexpr size_t BUFFER_COUNT = 8;
    FILE *file_ = nullptr;

    struct AudioChunk {
        int16_t *data;
        size_t sample_count;
    };

    int16_t *buffer_ = nullptr;
    size_t samples_recorded_ = 0;
    QueueHandle_t free_buffers_ = nullptr;
    QueueHandle_t ready_buffers_ = nullptr;
    bool initialized_ = false;
};
