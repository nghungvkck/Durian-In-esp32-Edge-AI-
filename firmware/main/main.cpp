#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <algorithm>
#include <new>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_log.h"
#include "esp_err.h"
#include "esp_heap_caps.h"

#include "dl_model_base.hpp"
#include "ics43434.h"
#include "audio_recorder.h"
#include "audio_processor.h"
#include "mel_extractor.h"
#include "spectrogram_resize.h"

static const char *TAG = "DURIAN_AI";

extern const uint8_t model_espdl[] asm("_binary_durian_student_pruned_espdl_start");

extern "C" void app_main(void)
{
    ESP_LOGI(TAG, "Starting durian audio pipeline");

    const size_t psram_free = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "PSRAM free: %u bytes, largest block: %u bytes",
             static_cast<unsigned>(psram_free),
             static_cast<unsigned>(heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM)));

    if (psram_free == 0) {
        ESP_LOGE(TAG, "PSRAM unavailable");
        return;
    }

    // 1. Load the quantized ESP-DL model once.
    dl::Model *model = new (std::nothrow) dl::Model(
        reinterpret_cast<const char *>(model_espdl),
        fbs::MODEL_LOCATION_IN_FLASH_RODATA,
        0
    );

    if (!model) {
        ESP_LOGE(TAG, "Failed to allocate model object");
        return;
    }

    auto &inputs = model->get_inputs();
    auto &outputs = model->get_outputs();

    if (inputs.empty() || outputs.empty()) {
        ESP_LOGE(TAG, "Model has no input/output tensors");
        delete model;
        return;
    }

    dl::TensorBase *model_input = inputs.begin()->second;
    dl::TensorBase *model_output = outputs.begin()->second;

    if (!model_input || !model_input->data ||
        !model_output || !model_output->data) {
        ESP_LOGE(TAG, "Model input/output tensor data is unavailable");
        delete model;
        return;
    }

    constexpr size_t INPUT_SIZE = 128 * 128;
    if (model_input->get_bytes() != INPUT_SIZE) {
        ESP_LOGE(TAG, "Unexpected model input size: %d bytes",
                 model_input->get_bytes());
        model->print();
        delete model;
        return;
    }

    if (model_output->get_bytes() != 2) {
        ESP_LOGE(TAG, "Expected 2 INT8 output values, got %d bytes",
                 model_output->get_bytes());
        model->print();
        delete model;
        return;
    }

    ESP_LOGI(TAG, "Model loaded. Input bytes=%d, input exponent=%d, output exponent=%d",
             model_input->get_bytes(),
             model_input->get_exponent(),
             model_output->get_exponent());
    model->print();

    // 2. Initialize microphone.
    Ics43434 mic;
    Ics43434::Config mic_config{
        GPIO_NUM_3,
        GPIO_NUM_2,
        GPIO_NUM_1,
        16000,
        false
    };

    esp_err_t err = mic.begin(mic_config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Microphone initialization failed: %s", esp_err_to_name(err));
        delete model;
        return;
    }

    // 3. Initialize recorder and record audio.
    AudioRecorder recorder;
    err = recorder.init();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Recorder initialization failed: %s", esp_err_to_name(err));
        delete model;
        return;
    }

    ESP_LOGI(TAG, "Recording audio...");
    err = recorder.record(mic);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Recording failed: %s", esp_err_to_name(err));
        delete model;
        return;
    }

    ESP_LOGI(TAG, "Recorded %u samples",
             static_cast<unsigned>(recorder.sample_count()));

    // 4. Detect peaks and extract audio crops.
    AudioProcessor processor;
    processor.process(recorder.data(), recorder.sample_count());

    const size_t num_peaks = processor.peak_count();
    ESP_LOGI(TAG, "Detected peaks: %u", static_cast<unsigned>(num_peaks));

    if (num_peaks == 0) {
        ESP_LOGW(TAG, "No peaks detected");
        delete model;
        return;
    }

    // 5. Allocate Mel buffers in PSRAM.
    float *mel_output = static_cast<float *>(
        heap_caps_malloc(MelExtractor::MEL_SIZE * sizeof(float), MALLOC_CAP_SPIRAM)
    );

    constexpr size_t RESIZED_HEIGHT = 128;
    constexpr size_t RESIZED_WIDTH = 128;
    constexpr size_t RESIZED_SIZE = RESIZED_HEIGHT * RESIZED_WIDTH;

    float *resized_mel = static_cast<float *>(
        heap_caps_malloc(RESIZED_SIZE * sizeof(float), MALLOC_CAP_SPIRAM)
    );

    if (!mel_output || !resized_mel) {
        ESP_LOGE(TAG, "Failed to allocate Mel buffers");
        free(mel_output);
        free(resized_mel);
        delete model;
        return;
    }

    MelExtractor mel_extractor;
    size_t successful_crops = 0;

    // 6. Process every crop and run inference.
    for (size_t i = 0; i < num_peaks; i++) {
        const int16_t *crop = processor.crop_data(i);
        const size_t crop_samples = processor.crop_sample_count(i);

        if (!crop || crop_samples == 0) {
            ESP_LOGW(TAG, "Crop %u is empty", static_cast<unsigned>(i));
            vTaskDelay(1);
            continue;
        }

        ESP_LOGI(TAG, "Crop %u: %u samples",
                 static_cast<unsigned>(i),
                 static_cast<unsigned>(crop_samples));

        size_t n_frames = 0;
        err = mel_extractor.extract(
            crop,
            crop_samples,
            mel_output,
            MelExtractor::MEL_SIZE,
            n_frames
        );

        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Mel extraction failed for crop %u: %s",
                     static_cast<unsigned>(i), esp_err_to_name(err));
            vTaskDelay(1);
            continue;
        }

        if (n_frames == 0 || n_frames > MelExtractor::MAX_FRAMES) {
            ESP_LOGE(TAG, "Invalid Mel frame count: %u",
                     static_cast<unsigned>(n_frames));
            vTaskDelay(1);
            continue;
        }

        // Convert Mel dB values in [-80, 0] to [0, 1].
        for (size_t j = 0; j < 128 * n_frames; j++) {
            mel_output[j] = std::clamp((mel_output[j] + 80.0f) / 80.0f, 0.0f, 1.0f);
        }

        err = resize_spectrogram(
            mel_output,
            128,
            n_frames,
            resized_mel,
            RESIZED_HEIGHT,
            RESIZED_WIDTH,
            RESIZED_SIZE
        );

        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Mel resize failed for crop %u: %s",
                     static_cast<unsigned>(i), esp_err_to_name(err));
            vTaskDelay(1);
            continue;
        }

        bool valid_input = true;
        for (size_t j = 0; j < RESIZED_SIZE; j++) {
            if (!std::isfinite(resized_mel[j])) {
                ESP_LOGE(TAG, "Invalid Mel value at index %u", static_cast<unsigned>(j));
                valid_input = false;
                break;
            }
        }

        if (!valid_input) {
            vTaskDelay(1);   
            continue;
        }

        // Quantize float [0, 1] to the model's INT8 input using its exponent.
        int8_t *input_data = static_cast<int8_t *>(model_input->data);
        for (size_t j = 0; j < RESIZED_SIZE; j++) {
            input_data[j] = dl::quantize<int8_t>(
                resized_mel[j],
                DL_RESCALE(model_input->exponent)
            );
        }

        // Run the model. Output is two INT8 class scores (logits).
        model->run();

        const int8_t *output_data = static_cast<const int8_t *>(model_output->data);
        const float score0 = dl::dequantize(
            output_data[0],
            DL_SCALE(model_output->exponent)
        );
        const float score1 = dl::dequantize(
            output_data[1],
            DL_SCALE(model_output->exponent)
        );

        const int predicted_class = (score1 > score0) ? 1 : 0;
        const char *label = (predicted_class == 0) ? "XANH" : "CHIN";

        ESP_LOGI(TAG,
                 "Crop %u prediction: %s (class=%d), score0=%.5f, score1=%.5f",
                 static_cast<unsigned>(i), label, predicted_class, score0, score1);

        successful_crops++;
        vTaskDelay(1);
    }

    free(mel_output);
    free(resized_mel);

    ESP_LOGI(TAG, "Pipeline completed: %u/%u crops inferred",
             static_cast<unsigned>(successful_crops),
             static_cast<unsigned>(num_peaks));

    delete model;

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
