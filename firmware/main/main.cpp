#include <cstdio>
#include <cstdint>
#include <algorithm>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "audio_recorder.h"
#include "ics43434.h"

static const char *TAG = "MAIN";

extern "C" void app_main(void) {
    Ics43434 mic;

    Ics43434::Config config;
    config.bclk = GPIO_NUM_3;
    config.ws = GPIO_NUM_2;
    config.din = GPIO_NUM_1;
    config.sample_rate_hz = 16000;
    config.right_channel = false;

    esp_err_t err = mic.begin(config);

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Microphone initialization failed: %s",
                 esp_err_to_name(err));
        return;
    }

    ESP_LOGI(TAG, "ICS-43434 initialized");

    AudioRecorder recorder;

    err = recorder.init();

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Audio recorder initialization failed: %s",
                 esp_err_to_name(err));
        mic.end();
        return;
    }

    ESP_LOGI(TAG, "Recording 5 seconds...");
    err = recorder.record(mic);

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Recording failed: %s",
                 esp_err_to_name(err));
        recorder.clear();
        mic.end();
        return;
    }

    const int16_t *pcm = recorder.data();
    const size_t count = recorder.sample_count();

    int16_t min_value = pcm[0];
    int16_t max_value = pcm[0];
    double sum_squares = 0.0;

    for (size_t i = 0; i < count; i++) {
        min_value = std::min(min_value, pcm[i]);
        max_value = std::max(max_value, pcm[i]);
        sum_squares += static_cast<double>(pcm[i]) * pcm[i];
    }

    const double rms = (count > 0)
        ? __builtin_sqrt(sum_squares / count)
        : 0.0;

    ESP_LOGI(TAG, "Recording completed");
    ESP_LOGI(TAG, "Sample count: %u",
             static_cast<unsigned>(count));
    ESP_LOGI(TAG, "Audio size: %u bytes",
             static_cast<unsigned>(recorder.byte_size()));
    ESP_LOGI(TAG, "Min: %d | Max: %d",
             min_value, max_value);
    ESP_LOGI(TAG, "RMS: %.2f", rms);

    ESP_LOGI(TAG, "Audio is stored in PSRAM");

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}