#pragma once

#include <cstddef>
#include <cstdint>

#include "esp_err.h"
#include "ics43434.h"

class AudioRecorder {
public:
    static constexpr uint32_t SAMPLE_RATE_HZ = 16000;
    static constexpr uint32_t RECORD_SECONDS = 5;
    static constexpr size_t TOTAL_SAMPLES =
        SAMPLE_RATE_HZ * RECORD_SECONDS;

    AudioRecorder() = default;
    ~AudioRecorder();

    AudioRecorder(const AudioRecorder &) = delete;
    AudioRecorder &operator=(const AudioRecorder &) = delete;

    esp_err_t init();
    esp_err_t record(Ics43434 &mic);

    const int16_t *data() const;
    size_t sample_count() const;
    size_t byte_size() const;

    void clear();
    bool is_ready() const;

private:
    int16_t *buffer_ = nullptr;
    size_t samples_recorded_ = 0;
};