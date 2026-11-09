// Chạy WAV nhúng trong flash qua chính pipeline của ứng dụng main.
// Không khởi tạo micro, SD, GPIO, nút hoặc LED. Vẫn cần ESP32-S3 có PSRAM.
#include <cstdint>
#include <cstdio>
#include <memory>

#include "inference_pipeline.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

extern const uint8_t test_wav_start[] asm("_binary_20260717_172242_wav_start");
extern const uint8_t test_wav_end[] asm("_binary_20260717_172242_wav_end");

extern "C" void app_main(void)
{
    constexpr const char *TAG = "MODEL_ONLY";
    const size_t free_psram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "PSRAM free=%u bytes, largest block=%u bytes", unsigned(free_psram),
             unsigned(heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM)));
    if (free_psram == 0) {
        ESP_LOGE(TAG, "PSRAM unavailable. Enable PSRAM before loading the model.");
        return;
    }

    const size_t bytes = test_wav_end - test_wav_start;
    ESP_LOGI(TAG, "Test WAV: 20260717_172242.wav (%u bytes)", unsigned(bytes));
    // fmemopen nhận void*, nhưng chế độ rb chỉ đọc; không ghi vào flash rodata.
    std::unique_ptr<FILE, decltype(&fclose)> file(
        fmemopen(const_cast<uint8_t *>(test_wav_start), bytes, "rb"), fclose);
    if (!file) {
        ESP_LOGE(TAG, "Cannot open embedded WAV");
        return;
    }

    int prediction = -1;
    const esp_err_t err = infer_wav(file.get(), prediction, true);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "FINAL RESULT: %s (class %d)", prediction == 1 ? "CHIN" : "XANH", prediction);
    } else {
        ESP_LOGE(TAG, "WAV inference failed: %s (no prediction)", esp_err_to_name(err));
    }
    ESP_LOGI(TAG, "Done. Reset the board to run again.");
}
