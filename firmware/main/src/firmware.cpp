#include <cstdio>  
#include <cstdint>
#include "freertos/FreeRTOS.h"    // Hệ diều hành quán lý thời gian thực FreeRTOS
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_heap_caps.h" // Kiểm tra bộ nhớ theo thuộc tiếng
#include "dl_model_base.hpp"  // lớp cơ sở của mô hình ESP-DL

extern const uint8_t model_espdl[] asm("_binary_durian_student_pruned_espdl_start");   // Khai bao model
static const char *TAG = "DURIAN_AI";

extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "Starting Durian Edge AI...");

    const size_t psram_free = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);              // Kiểm tra bộ nhớ PSRam
    ESP_LOGI(TAG, "PSRAM free: %u bytes, largest block: %u bytes",
             static_cast<unsigned>(psram_free),
             static_cast<unsigned>(heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM)));
    if (psram_free == 0) {
        ESP_LOGE(TAG, "PSRAM unavailable; skipping model initialization.");
        return;
    }

    dl::Model *model = new dl::Model(
        reinterpret_cast<const char *>(model_espdl),
        fbs::MODEL_LOCATION_IN_FLASH_RODATA,
        0 // With CONFIG_SPIRAM enabled, allocate the tensor arena in PSRAM.
    );

    const auto &inputs = model->get_inputs();
    const auto &outputs = model->get_outputs();
    if (inputs.empty() || outputs.empty()) {
        ESP_LOGE(TAG, "Model initialization failed: no input/output tensors.");
        delete model;
        return;
    }
    for (const auto &entry : inputs) {
        if (!entry.second || !entry.second->get_element_ptr()) {
            ESP_LOGE(TAG, "Model input allocation failed: %s", entry.first.c_str());
            delete model;
            return;
        }
    }
    for (const auto &entry : outputs) {
        if (!entry.second || !entry.second->get_element_ptr()) {
            ESP_LOGE(TAG, "Model output allocation failed: %s", entry.first.c_str());
            delete model;
            return;
        }
    }

    ESP_LOGI(TAG, "Model loaded");

    esp_err_t result = model->test();

    if (result == ESP_OK) {
        ESP_LOGI(TAG, "Model test PASSED");
    } else {
        ESP_LOGE(TAG, "Model test FAILED: %s", esp_err_to_name(result));
    }

    model->print();

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
