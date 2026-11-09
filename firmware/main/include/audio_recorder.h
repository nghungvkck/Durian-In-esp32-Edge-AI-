#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include "ics43434.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"

// The control task owns start/stop. Only the capture task reads the microphone;
// only the writer task writes PCM. stop() joins both before closing the WAV.
class AudioRecorder {
public:
    static constexpr uint32_t SAMPLE_RATE_HZ = 16000;
    AudioRecorder() = default;
    ~AudioRecorder();
    AudioRecorder(const AudioRecorder &) = delete;
    AudioRecorder &operator=(const AudioRecorder &) = delete;
    esp_err_t init();
    esp_err_t start(Ics43434 &mic, const char *file_path);
    esp_err_t stop();
    bool is_recording() const { return active_; }
    esp_err_t error() const { return error_.load(); }

private:
    static constexpr size_t CHUNK_SAMPLES = 1024;
    static constexpr size_t BUFFER_COUNT = 16; // About one second of SD latency.
    struct AudioChunk { int16_t *data; size_t sample_count; };
    static void capture_task(void *context);
    static void writer_task(void *context);
    void set_error(esp_err_t error);
    void clear();
    Ics43434 *mic_ = nullptr;
    FILE *file_ = nullptr;
    int16_t *buffer_ = nullptr;
    size_t samples_recorded_ = 0;
    QueueHandle_t free_buffers_ = nullptr;
    QueueHandle_t ready_buffers_ = nullptr;
    SemaphoreHandle_t capture_done_ = nullptr;
    SemaphoreHandle_t writer_done_ = nullptr;
    std::atomic<bool> stop_requested_{false};
    std::atomic<esp_err_t> error_{ESP_OK};
    bool active_ = false;
};
