#include "audio_recorder.h"
#include <algorithm>
#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "AUDIO_RECORDER";

AudioRecorder::~AudioRecorder() {
    clear();
}

esp_err_t AudioRecorder::init() {
    if (initialized_) { return ESP_OK;}

    constexpr size_t buffer_bytes = BUFFER_COUNT * CHUNK_SAMPLES * sizeof(int16_t);                          // tinh so byte can thiet
    // cap phat bo nho psram
    // neu ko cap phat duoc thi buffer_ trả về nullptr 
    buffer_ = static_cast<int16_t *>(heap_caps_malloc(buffer_bytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));  
    if (buffer_ == nullptr){
        ESP_LOGE(TAG, "Failed to allocate buffer");
        return ESP_ERR_NO_MEM;
    }

    free_buffers_ = xQueueCreate(BUFFER_COUNT, sizeof(int16_t *));   // queue luu cac con tro dang ranh
    ready_buffers_ = xQueueCreate(BUFFER_COUNT, sizeof(AudioChunk)); // queue luu cac chunk da san sang de ghi vao file
    if (free_buffers_ == nullptr || ready_buffers_ == nullptr) {     // neu 1 trong 2 queue ko tao duoc thi xoa queue con lai va giai phong bo nho buffer_
        if (free_buffers_ != nullptr) {
            vQueueDelete(free_buffers_);
            free_buffers_ = nullptr;
        }
        if (ready_buffers_ != nullptr) {
            vQueueDelete(ready_buffers_);
            ready_buffers_ = nullptr;
        }

        heap_caps_free(buffer_);
        buffer_ = nullptr;
        ESP_LOGE(TAG, "Failed to create queues");
        return ESP_ERR_NO_MEM;
    }

    for (size_t i = 0; i < BUFFER_COUNT; i++) {                     // dua cac chunk vao queue free_buffers_ de san sang su dung
        int16_t *chunk = buffer_ + i * CHUNK_SAMPLES;               // tinh dia chi cua chunk thu i
        xQueueSend(free_buffers_, &chunk, 0);                       // dua con tro chunk vao queue free_buffers_
    }

    samples_recorded_ = 0;
    initialized_ = true;

    ESP_LOGI(TAG, "AudioRecorder initialized with buffer size %u bytes", static_cast<unsigned>(buffer_bytes));
    return ESP_OK;
}

esp_err_t AudioRecorder::start(Ics43434 &mic, const char *file_path) {
    if (!initialized_) {
        ESP_LOGE(TAG, "Call init() before start()");
        return ESP_ERR_INVALID_STATE;
    }

    if (file_ != nullptr){
        ESP_LOGE(TAG, "Recording already in progress");
        return ESP_ERR_INVALID_STATE;
    }

    if (!mic.is_started()){
        ESP_LOGE(TAG, "Microphone not started");
        return ESP_ERR_INVALID_STATE;   
    }

    if (file_path == nullptr) {
        ESP_LOGE(TAG, "Invalid filename");
        return ESP_ERR_INVALID_ARG;
    }

    if (file_ != nullptr) {
        ESP_LOGE(TAG, "Recording already in progress");
        return ESP_ERR_INVALID_STATE;
    }   
}

// esp_err_t AudioRecorder::record(Ics43434 &mic) {
//     if (buffer_ == nullptr) {
//         ESP_LOGE(TAG, "Call init() before record()");
//         return ESP_ERR_INVALID_STATE;
//     }

//     constexpr size_t CHUNK_SIZE = 256;
//     int32_t input[CHUNK_SIZE];

//     samples_recorded_ = 0;

//     while (samples_recorded_ < TOTAL_SAMPLES) {
//         const size_t remaining = TOTAL_SAMPLES - samples_recorded_;
//         const size_t requested = std::min(remaining, CHUNK_SIZE);

//         size_t received = 0;

//         esp_err_t err = mic.read(
//             input,
//             requested,
//             received,
//             1000
//         );

//         if (err != ESP_OK) {
//             ESP_LOGE(TAG, "Microphone read failed: %s",
//                      esp_err_to_name(err));
//             samples_recorded_ = 0;
//             return err;
//         }

//         if (received == 0) {
//             ESP_LOGE(TAG, "No samples received");
//             samples_recorded_ = 0;
//             return ESP_FAIL;
//         }

//         for (size_t i = 0; i < received; i++) {
//             int32_t sample = input[i] / 256;

//             sample = std::max<int32_t>(sample, -32768);
//             sample = std::min<int32_t>(sample, 32767);

//             buffer_[samples_recorded_ + i] =
//                 static_cast<int16_t>(sample);
//         }

//         samples_recorded_ += received;
//     }

//     ESP_LOGI(TAG, "Recorded %u samples",
//              static_cast<unsigned>(samples_recorded_));

//     return ESP_OK;
// }

// const int16_t *AudioRecorder::data() const {
//     return buffer_;
// }

// size_t AudioRecorder::sample_count() const {
//     return samples_recorded_;
// }

// size_t AudioRecorder::byte_size() const {
//     return samples_recorded_ * sizeof(int16_t);
// }

// void AudioRecorder::clear() {
//     if (buffer_ != nullptr) {
//         heap_caps_free(buffer_);
//         buffer_ = nullptr;
//     }

//     samples_recorded_ = 0;
// }

// bool AudioRecorder::is_ready() const {
//     return buffer_ != nullptr;
// }
