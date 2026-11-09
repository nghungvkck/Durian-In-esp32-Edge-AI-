#include "inference_pipeline.h"
#include "wav_file.h"
#include "audio_processor.h"
#include "mel_extractor.h"
#include "spectrogram_resize.h"
#include "dl_model_base.hpp"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <memory>
#include <new>
#include <string>
#include "esp_timer.h"

static const char *TAG = "INFERENCE";
extern const uint8_t model_espdl[] asm("_binary_durian_student_pruned_espdl_start");

esp_err_t infer_latest_wav(const char *path, int &prediction) {
    prediction = -1;
    std::unique_ptr<FILE, decltype(&fclose)> file(fopen(path, "rb"), fclose);
    if (!file) return ESP_ERR_INVALID_ARG;
    return infer_wav(file.get(), prediction);
}

esp_err_t infer_wav(FILE *file, int &prediction, bool verbose) {
    prediction = -1;
    uint32_t total = 0;
    if (!file || !wav::read_header(file, total)) return ESP_ERR_INVALID_ARG;
    if (verbose) ESP_LOGI(TAG, "WAV: mono PCM16, %u Hz, %u samples, %.3f s",
                          unsigned(wav::RATE), unsigned(total), double(total) / wav::RATE);
    std::unique_ptr<dl::Model> model(new (std::nothrow) dl::Model(
        reinterpret_cast<const char *>(model_espdl), fbs::MODEL_LOCATION_IN_FLASH_RODATA, 0));
    if (!model) return ESP_ERR_NO_MEM;
    auto &inputs = model->get_inputs();
    auto &outputs = model->get_outputs();
    if (inputs.empty() || outputs.empty()) return ESP_FAIL;
    auto *input = inputs.begin()->second;
    auto *output = outputs.begin()->second;
    constexpr size_t SIZE = 128 * 128;
    if (!input || !output || !input->data || !output->data ||
        input->dtype != dl::DATA_TYPE_INT8 || output->dtype != dl::DATA_TYPE_INT8 ||
        input->get_bytes() != SIZE || output->get_bytes() != 2) return ESP_FAIL;
    if (verbose) {
        for (const auto *kind : {"INPUT", "OUTPUT"}) {
            const auto &tensors = kind[0] == 'I' ? inputs : outputs;
            for (const auto &entry : tensors) {
                if (!entry.second || !entry.second->data) return ESP_FAIL;
                std::string shape = "[";
                for (const int dim : entry.second->shape) {
                    if (shape.size() > 1) shape += ", ";
                    shape += std::to_string(dim);
                }
                shape += "]";
                ESP_LOGI(TAG, "%s %s: shape=%s dtype=%s", kind, entry.first.c_str(),
                         shape.c_str(), entry.second->get_dtype_string());
            }
        }
        ESP_LOGI(TAG, "=== MODEL STRUCTURE ===");
        model->print();
    }

    // Four-second cores with context on both sides. Infer only peaks inside
    // each core, avoiding duplicate votes and truncated crops at block edges.
    constexpr size_t CORE = 4 * wav::RATE;
    constexpr size_t HALO = AudioProcessor::CROP_SAMPLES;
    constexpr size_t CAPACITY = CORE + 2 * HALO;
    std::unique_ptr<int16_t, decltype(&free)> audio(static_cast<int16_t *>(
        heap_caps_malloc(CAPACITY * sizeof(int16_t), MALLOC_CAP_SPIRAM)), free);
    std::unique_ptr<float, decltype(&free)> mel(static_cast<float *>(
        heap_caps_malloc(MelExtractor::MEL_SIZE * sizeof(float), MALLOC_CAP_SPIRAM)), free);
    std::unique_ptr<float, decltype(&free)> resized(static_cast<float *>(
        heap_caps_malloc(SIZE * sizeof(float), MALLOC_CAP_SPIRAM)), free);
    if (!audio || !mel || !resized) return ESP_ERR_NO_MEM;
    MelExtractor extractor;
    size_t votes[2] = {};
    size_t last_peak = 0;
    bool have_peak = false;
    for (size_t core = 0; core < total; core += CORE) {
        const size_t begin = core > HALO ? core - HALO : 0;
        const size_t core_end = std::min<size_t>(core + CORE, total);
        const size_t end = std::min<size_t>(core_end + HALO, total);
        const size_t count = end - begin;
        if (fseek(file, wav::HEADER_BYTES + long(begin * 2), SEEK_SET) != 0 ||
            fread(audio.get(), sizeof(int16_t), count, file) != count) return ESP_FAIL;
        if (count < 3) continue;
        AudioProcessor processor;
        esp_err_t err = processor.process(audio.get(), count);
        if (err != ESP_OK) return err;
        if (verbose) ESP_LOGI(TAG, "Window %.3f..%.3f s: %u candidate peaks (threshold %.2f of peak)",
                             double(core) / wav::RATE, double(core_end) / wav::RATE,
                             unsigned(processor.peak_count()), double(AudioProcessor::PEAK_THRESHOLD_RATIO));
        for (size_t i = 0; i < processor.peak_count(); ++i) {
            const size_t peak = begin + processor.peak_index(i);
            if (peak < core || peak >= core_end ||
                (have_peak && peak - last_peak < AudioProcessor::MIN_PEAK_DISTANCE_SAMPLES)) continue;
            size_t frames = 0;
            err = extractor.extract(processor.crop_data(i), processor.crop_sample_count(i),
                                    mel.get(), MelExtractor::MEL_SIZE, frames);
            if (err != ESP_OK) return err;
            if (!frames || frames > MelExtractor::MAX_FRAMES) return ESP_FAIL;
            if (verbose) ESP_LOGI(TAG, "Crop: peak=%.3f s, %u samples -> Mel 128 x %u (FFT 2048, hop 256)",
                                 double(peak) / wav::RATE, unsigned(processor.crop_sample_count(i)), unsigned(frames));
            for (size_t j = 0; j < 128 * frames; ++j)
                mel.get()[j] = std::clamp((mel.get()[j] + 80.0f) / 80.0f, 0.0f, 1.0f);
            err = resize_spectrogram(mel.get(), 128, frames, resized.get(), 128, 128, SIZE);
            if (err != ESP_OK) return err;
            auto *data = static_cast<int8_t *>(input->data);
            for (size_t j = 0; j < SIZE; ++j) {
                if (!std::isfinite(resized.get()[j])) return ESP_FAIL;
                data[j] = dl::quantize<int8_t>(resized.get()[j], DL_RESCALE(input->exponent));
            }
            if (verbose) ESP_LOGI(TAG, "Normalize [-80,0] dB -> [0,1] -> resize 128x128 -> INT8 -> model");
            const int64_t started = esp_timer_get_time();
            model->run();
            if (verbose) ESP_LOGI(TAG, "Inference time: %.3f ms", (esp_timer_get_time() - started) / 1000.0);
            const auto *scores = static_cast<const int8_t *>(output->data);
            const int cls = scores[1] > scores[0] ? 1 : 0;
            ++votes[cls];
            last_peak = peak;
            have_peak = true;
            ESP_LOGI(TAG, "Peak %u: %s (scores %d, %d)", static_cast<unsigned>(peak),
                     cls ? "CHIN" : "XANH", int(scores[0]), int(scores[1]));
            vTaskDelay(1);
        }
        vTaskDelay(1);
    }
    ESP_LOGI(TAG, "Votes XANH=%u, CHIN=%u", unsigned(votes[0]), unsigned(votes[1]));
    if (votes[0] == votes[1]) {
        ESP_LOGW(TAG, "No peaks or tied votes: no prediction");
        return ESP_ERR_NOT_FOUND;
    }
    prediction = votes[1] > votes[0] ? 1 : 0;
    return ESP_OK;
}
