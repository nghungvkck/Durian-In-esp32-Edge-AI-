#include "audio_recorder.h"
#include "wav_file.h"
#include <algorithm>
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/task.h"

static const char *TAG = "AUDIO_RECORDER";

AudioRecorder::~AudioRecorder() { clear(); }

void AudioRecorder::clear() {
    if (active_) (void)stop();
    if (free_buffers_) vQueueDelete(free_buffers_);
    if (ready_buffers_) vQueueDelete(ready_buffers_);
    if (capture_done_) vSemaphoreDelete(capture_done_);
    if (writer_done_) vSemaphoreDelete(writer_done_);
    heap_caps_free(buffer_);
    free_buffers_ = nullptr;
    ready_buffers_ = nullptr;
    capture_done_ = writer_done_ = nullptr;
    buffer_ = nullptr;
}

esp_err_t AudioRecorder::init() {
    if (buffer_) return ESP_OK;
    buffer_ = static_cast<int16_t *>(heap_caps_malloc(
        BUFFER_COUNT * CHUNK_SAMPLES * sizeof(int16_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
    free_buffers_ = xQueueCreate(BUFFER_COUNT, sizeof(int16_t *));
    // One extra slot guarantees room for the end marker.
    ready_buffers_ = xQueueCreate(BUFFER_COUNT + 1, sizeof(AudioChunk));
    capture_done_ = xSemaphoreCreateBinary();
    writer_done_ = xSemaphoreCreateBinary();
    if (!buffer_ || !free_buffers_ || !ready_buffers_ || !capture_done_ || !writer_done_) {
        clear();
        return ESP_ERR_NO_MEM;
    }
    return ESP_OK;
}

void AudioRecorder::set_error(esp_err_t err) {
    esp_err_t expected = ESP_OK;
    error_.compare_exchange_strong(expected, err);
    stop_requested_.store(true);
}

esp_err_t AudioRecorder::start(Ics43434 &mic, const char *path) {
    if (!buffer_ || active_ || !mic.is_started()) return ESP_ERR_INVALID_STATE;
    if (!path) return ESP_ERR_INVALID_ARG;
    file_ = fopen(path, "wb");
    if (!file_) return ESP_FAIL;
    if (!wav::write_header(file_, 0)) {
        fclose(file_); file_ = nullptr;
        return ESP_FAIL;
    }
    xQueueReset(free_buffers_);
    xQueueReset(ready_buffers_);
    (void)xSemaphoreTake(capture_done_, 0);
    (void)xSemaphoreTake(writer_done_, 0);
    for (size_t i = 0; i < BUFFER_COUNT; ++i) {
        int16_t *chunk = buffer_ + i * CHUNK_SAMPLES;
        xQueueSend(free_buffers_, &chunk, 0);
    }
    samples_recorded_ = 0;
    mic_ = &mic;
    stop_requested_.store(false);
    error_.store(ESP_OK);
    if (xTaskCreate(writer_task, "sd_writer", 4096, this, 5, nullptr) != pdPASS) {
        fclose(file_); file_ = nullptr;
        return ESP_ERR_NO_MEM;
    }
    if (xTaskCreate(capture_task, "mic_capture", 6144, this, 6, nullptr) != pdPASS) {
        AudioChunk end{nullptr, 0};
        xQueueSend(ready_buffers_, &end, portMAX_DELAY);
        xSemaphoreTake(writer_done_, portMAX_DELAY);
        fclose(file_); file_ = nullptr;
        return ESP_ERR_NO_MEM;
    }
    active_ = true;
    return ESP_OK;
}

void AudioRecorder::capture_task(void *context) {
    auto &self = *static_cast<AudioRecorder *>(context);
    int32_t pcm[CHUNK_SAMPLES];
    while (!self.stop_requested_.load()) {
        int16_t *buffer = nullptr;
        // Fail explicitly rather than silently losing audio if the SD falls behind.
        if (xQueueReceive(self.free_buffers_, &buffer, pdMS_TO_TICKS(20)) != pdTRUE) {
            self.set_error(ESP_ERR_TIMEOUT);
            break;
        }
        size_t count = 0;
        esp_err_t err = self.mic_->read(pcm, CHUNK_SAMPLES, count, 200);
        if ((err != ESP_OK && err != ESP_ERR_TIMEOUT) || count == 0) {
            xQueueSend(self.free_buffers_, &buffer, 0);
            self.set_error(err == ESP_OK ? ESP_FAIL : err);
            break;
        }
        for (size_t i = 0; i < count; ++i)
            buffer[i] = static_cast<int16_t>(std::clamp<int32_t>(pcm[i] / 256, -32768, 32767));
        AudioChunk chunk{buffer, count};
        xQueueSend(self.ready_buffers_, &chunk, portMAX_DELAY);
    }
    AudioChunk end{nullptr, 0};
    xQueueSend(self.ready_buffers_, &end, portMAX_DELAY);
    xSemaphoreGive(self.capture_done_);
    vTaskDelete(nullptr);
}

void AudioRecorder::writer_task(void *context) {
    auto &self = *static_cast<AudioRecorder *>(context);
    size_t flushed_samples = 0;
    while (true) {
        AudioChunk chunk{};
        xQueueReceive(self.ready_buffers_, &chunk, portMAX_DELAY);
        if (!chunk.data) break;
        // On failure keep draining the queue so capture/stop can always finish.
        if (self.error_.load() == ESP_OK) {
            if (self.samples_recorded_ + chunk.sample_count > wav::MAX_DATA_BYTES / 2) {
                self.set_error(ESP_ERR_INVALID_SIZE);
            } else if (fwrite(chunk.data, sizeof(int16_t), chunk.sample_count, self.file_) != chunk.sample_count) {
                self.set_error(ESP_FAIL);
            } else {
                self.samples_recorded_ += chunk.sample_count;
                if (self.samples_recorded_ - flushed_samples >= SAMPLE_RATE_HZ) {
                    if (fflush(self.file_) != 0) self.set_error(ESP_FAIL);
                    flushed_samples = self.samples_recorded_;
                }
            }
        }
        xQueueSend(self.free_buffers_, &chunk.data, 0);
    }
    xSemaphoreGive(self.writer_done_);
    vTaskDelete(nullptr);
}

esp_err_t AudioRecorder::stop() {
    if (!active_) return ESP_ERR_INVALID_STATE;
    stop_requested_.store(true);
    xSemaphoreTake(capture_done_, portMAX_DELAY);
    xSemaphoreTake(writer_done_, portMAX_DELAY);
    if (samples_recorded_ == 0) set_error(ESP_ERR_INVALID_SIZE);
    if (!wav::write_header(file_, samples_recorded_ * sizeof(int16_t))) set_error(ESP_FAIL);
    if (fflush(file_) != 0) set_error(ESP_FAIL);
    if (fclose(file_) != 0) set_error(ESP_FAIL);
    file_ = nullptr;
    mic_ = nullptr;
    active_ = false;
    ESP_LOGI(TAG, "Stopped: %u samples, status=%s", static_cast<unsigned>(samples_recorded_),
             esp_err_to_name(error_.load()));
    return error_.load();
}
