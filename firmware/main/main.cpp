#include <cstdint>
#include <cmath>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_log.h"
#include "esp_err.h"
#include "driver/gpio.h"

#include "ics43434.h"
#include "audio_recorder.h"
#include "audio_processor.h"

static const char *TAG = "MAIN";

extern "C" void app_main(void)
{
    Ics43434 mic;
    AudioRecorder recorder;
    AudioProcessor processor;

    // 1. Khoi tao microphone
    Ics43434::Config config{};
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

    // 2. Khoi tao bo ghi am
    err = recorder.init();

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Recorder initialization failed: %s",
                 esp_err_to_name(err));
        return;
    }

    // 3. Ghi am 5 giay
    ESP_LOGI(TAG, "Recording %u seconds...",
             static_cast<unsigned>(AudioRecorder::RECORD_SECONDS));

    err = recorder.record(mic);

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Recording failed: %s",
                 esp_err_to_name(err));
        return;
    }

    ESP_LOGI(TAG, "Recording completed");
    ESP_LOGI(TAG, "Sample count: %u",
             static_cast<unsigned>(recorder.sample_count()));
    ESP_LOGI(TAG, "Audio size: %u bytes",
             static_cast<unsigned>(recorder.byte_size()));

    // 4. Phat hien peak va cat audio
    err = processor.process(
        recorder.data(),
        recorder.sample_count()
    );

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Audio processing failed: %s",
                 esp_err_to_name(err));
        return;
    }

    const size_t count = processor.peak_count();

    ESP_LOGI(TAG, "Detected peaks: %u",
             static_cast<unsigned>(count));

    // 5. Kiem tra cac doan audio da cat
    for (size_t i = 0; i < count; i++) {
        const int16_t *crop = processor.crop_data(i);
        const size_t samples = processor.crop_sample_count(i);

        if (crop == nullptr || samples == 0) {
            ESP_LOGW(TAG, "Crop %u is empty",
                     static_cast<unsigned>(i));
            continue;
        }

        int16_t min_value = crop[0];
        int16_t max_value = crop[0];
        double sum_squares = 0.0;

        for (size_t j = 0; j < samples; j++) {
            const int16_t value = crop[j];

            if (value < min_value) {
                min_value = value;
            }

            if (value > max_value) {
                max_value = value;
            }

            sum_squares +=
                static_cast<double>(value) * value;
        }

        const double rms = std::sqrt(
            sum_squares / static_cast<double>(samples)
        );

        ESP_LOGI(
            TAG,
            "Crop %u | peak=%u | start=%u | samples=%u",
            static_cast<unsigned>(i),
            static_cast<unsigned>(processor.peak_index(i)),
            static_cast<unsigned>(processor.crop_start_index(i)),
            static_cast<unsigned>(samples)
        );

        ESP_LOGI(
            TAG,
            "Crop %u | min=%d | max=%d | RMS=%.2f",
            static_cast<unsigned>(i),
            static_cast<int>(min_value),
            static_cast<int>(max_value),
            rms
        );
    }

    ESP_LOGI(TAG, "Audio processing completed");
}