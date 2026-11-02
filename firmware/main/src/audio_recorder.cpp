#include "audio_recorder.h"
#include <algorithm>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "AUDIO_RECORDER";

AudioRecorder::~AudioRecorder() {
    clear();
}

esp_err_t AudioRecorder::init() {
    if (buffer_ != nullptr) {
        return ESP_OK;
    }

    const size_t bytes = TOTAL_SAMPLES * sizeof(int16_t);
    buffer_ = static_cast<int16_t *>(
        heap_caps_malloc(
            bytes,
            MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT
        )
    );

    if (buffer_ == nullptr) {
        ESP_LOGE(TAG, "Cannot allocate audio buffer in PSRAM");
        return ESP_ERR_NO_MEM;
    }

    samples_recorded_ = 0;
    ESP_LOGI(TAG, "Audio buffer allocated: %u bytes",
             static_cast<unsigned>(bytes));

    return ESP_OK;
}

esp_err_t AudioRecorder::record(Ics43434 &mic) {
    if (buffer_ == nullptr) {
        ESP_LOGE(TAG, "Call init() before record()");
        return ESP_ERR_INVALID_STATE;
    }

    constexpr size_t CHUNK_SIZE = 256;
    int32_t input[CHUNK_SIZE];

    samples_recorded_ = 0;

    while (samples_recorded_ < TOTAL_SAMPLES) {
        const size_t remaining = TOTAL_SAMPLES - samples_recorded_;
        const size_t requested = std::min(remaining, CHUNK_SIZE);

        size_t received = 0;

        esp_err_t err = mic.read(
            input,
            requested,
            received,
            1000
        );

        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Microphone read failed: %s",
                     esp_err_to_name(err));
            samples_recorded_ = 0;
            return err;
        }

        if (received == 0) {
            ESP_LOGE(TAG, "No samples received");
            samples_recorded_ = 0;
            return ESP_FAIL;
        }

        for (size_t i = 0; i < received; i++) {
            int32_t sample = input[i] / 256;

            sample = std::max<int32_t>(sample, -32768);
            sample = std::min<int32_t>(sample, 32767);

            buffer_[samples_recorded_ + i] =
                static_cast<int16_t>(sample);
        }

        samples_recorded_ += received;
    }

    ESP_LOGI(TAG, "Recorded %u samples",
             static_cast<unsigned>(samples_recorded_));

    return ESP_OK;
}

const int16_t *AudioRecorder::data() const {
    return buffer_;
}

size_t AudioRecorder::sample_count() const {
    return samples_recorded_;
}

size_t AudioRecorder::byte_size() const {
    return samples_recorded_ * sizeof(int16_t);
}

void AudioRecorder::clear() {
    if (buffer_ != nullptr) {
        heap_caps_free(buffer_);
        buffer_ = nullptr;
    }

    samples_recorded_ = 0;
}

bool AudioRecorder::is_ready() const {
    return buffer_ != nullptr;
}