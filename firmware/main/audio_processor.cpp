#include "audio_processor.h"

#include <cstdlib>
#include <cstring>
#include <limits>

#include "esp_heap_caps.h"

AudioProcessor::~AudioProcessor() {
    clear();
}

esp_err_t AudioProcessor::process(
    const int16_t *audio,
    size_t sample_count
) {
    if (audio == nullptr || sample_count < 3) {
        return ESP_ERR_INVALID_ARG;
    }

    clear();

    esp_err_t err = detect_peaks(audio, sample_count);
    if (err != ESP_OK) {
        clear();
        return err;
    }

    err = crop_audio(audio, sample_count);
    if (err != ESP_OK) {
        clear();
        return err;
    }

    return ESP_OK;
}

esp_err_t AudioProcessor::detect_peaks(
    const int16_t *audio,
    size_t sample_count
) {
    int32_t max_amplitude = 0;

    for (size_t i = 0; i < sample_count; i++) {
        int32_t amplitude = static_cast<int32_t>(audio[i]);

        if (amplitude < 0) {
            amplitude = -amplitude;
        }

        if (amplitude > max_amplitude) {
            max_amplitude = amplitude;
        }
    }

    if (max_amplitude == 0) {
        return ESP_OK;
    }

    const int32_t threshold = static_cast<int32_t>(
        max_amplitude * PEAK_THRESHOLD_RATIO
    );

    size_t last_peak = 0;
    int32_t last_peak_amplitude = 0;

    for (size_t i = 1; i + 1 < sample_count; i++) {
        int32_t current = static_cast<int32_t>(audio[i]);
        int32_t left = static_cast<int32_t>(audio[i - 1]);
        int32_t right = static_cast<int32_t>(audio[i + 1]);

        if (current < 0) {
            current = -current;
        }

        if (left < 0) {
            left = -left;
        }

        if (right < 0) {
            right = -right;
        }

        const bool is_peak =
            current >= threshold &&
            current > left &&
            current >= right;

        if (!is_peak) {
            continue;
        }

        if (peak_count_ == 0) {
            crops_[peak_count_].peak_index = i;
            last_peak = i;
            last_peak_amplitude = current;
            peak_count_++;
            continue;
        }

        if (i - last_peak < MIN_PEAK_DISTANCE_SAMPLES) {
            if (current > last_peak_amplitude) {
                crops_[peak_count_ - 1].peak_index = i;
                last_peak = i;
                last_peak_amplitude = current;
            }

            continue;
        }

        if (peak_count_ >= MAX_PEAKS) {
            break;
        }

        crops_[peak_count_].peak_index = i;
        last_peak = i;
        last_peak_amplitude = current;
        peak_count_++;
    }

    return ESP_OK;
}

esp_err_t AudioProcessor::crop_audio(
    const int16_t *audio,
    size_t sample_count
) {
    if (peak_count_ == 0) {
        return ESP_OK;
    }

    if (peak_count_ >
        std::numeric_limits<size_t>::max() / CROP_SAMPLES) {
        return ESP_ERR_INVALID_SIZE;
    }

    const size_t buffer_samples = peak_count_ * CROP_SAMPLES;
    const size_t buffer_bytes = buffer_samples * sizeof(int16_t);

    crop_buffer_ = static_cast<int16_t *>(
        heap_caps_malloc(
            buffer_bytes,
            MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT
        )
    );

    if (crop_buffer_ == nullptr) {
        return ESP_ERR_NO_MEM;
    }

    for (size_t i = 0; i < peak_count_; i++) {
        const size_t peak = crops_[i].peak_index;

        const size_t start =
            peak > PRE_PEAK_SAMPLES
                ? peak - PRE_PEAK_SAMPLES
                : 0;

        size_t end = start + CROP_SAMPLES;

        if (end > sample_count) {
            end = sample_count;
        }

        const size_t length = end - start;

        crops_[i].start_index = start;
        crops_[i].sample_count = length;

        int16_t *destination =
            crop_buffer_ + i * CROP_SAMPLES;

        std::memcpy(
            destination,
            audio + start,
            length * sizeof(int16_t)
        );
    }

    return ESP_OK;
}

size_t AudioProcessor::peak_count() const {
    return peak_count_;
}

size_t AudioProcessor::crop_sample_count(size_t index) const {
    if (index >= peak_count_) {
        return 0;
    }

    return crops_[index].sample_count;
}

size_t AudioProcessor::crop_start_index(size_t index) const {
    if (index >= peak_count_) {
        return 0;
    }

    return crops_[index].start_index;
}

size_t AudioProcessor::peak_index(size_t index) const {
    if (index >= peak_count_) {
        return 0;
    }

    return crops_[index].peak_index;
}

const int16_t *AudioProcessor::crop_data(size_t index) const {
    if (index >= peak_count_ || crop_buffer_ == nullptr) {
        return nullptr;
    }

    return crop_buffer_ + index * CROP_SAMPLES;
}

void AudioProcessor::clear() {
    if (crop_buffer_ != nullptr) {
        heap_caps_free(crop_buffer_);
        crop_buffer_ = nullptr;
    }

    peak_count_ = 0;
    std::memset(crops_, 0, sizeof(crops_));
}