#pragma once

#include <cstddef>
#include <cstdint>

#include "esp_err.h"

class AudioProcessor {
public:
    static constexpr uint32_t SAMPLE_RATE_HZ = 16000;
    static constexpr float PEAK_THRESHOLD_RATIO = 0.15f;
    static constexpr float MIN_PEAK_DISTANCE_SEC = 0.3f;
    static constexpr float PRE_PEAK_SEC = 0.145f;
    static constexpr float CROP_DURATION_SEC = 0.24f;

    static constexpr size_t MIN_PEAK_DISTANCE_SAMPLES =
        static_cast<size_t>(SAMPLE_RATE_HZ * MIN_PEAK_DISTANCE_SEC);

    static constexpr size_t PRE_PEAK_SAMPLES =
        static_cast<size_t>(SAMPLE_RATE_HZ * PRE_PEAK_SEC);

    static constexpr size_t CROP_SAMPLES =
        static_cast<size_t>(SAMPLE_RATE_HZ * CROP_DURATION_SEC);

    static constexpr size_t MAX_PEAKS = 32;

    struct CropInfo {
        size_t peak_index;
        size_t start_index;
        size_t sample_count;
    };

    AudioProcessor() = default;
    ~AudioProcessor();

    AudioProcessor(const AudioProcessor &) = delete;
    AudioProcessor &operator=(const AudioProcessor &) = delete;

    esp_err_t process(const int16_t *audio, size_t sample_count);

    size_t peak_count() const;
    size_t crop_sample_count(size_t index) const;
    size_t crop_start_index(size_t index) const;
    size_t peak_index(size_t index) const;

    const int16_t *crop_data(size_t index) const;

    void clear();

private:
    CropInfo crops_[MAX_PEAKS] = {};
    size_t peak_count_ = 0;
    int16_t *crop_buffer_ = nullptr;

    esp_err_t detect_peaks(const int16_t *audio, size_t sample_count);
    esp_err_t crop_audio(const int16_t *audio, size_t sample_count);
};