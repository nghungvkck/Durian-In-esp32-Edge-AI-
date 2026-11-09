#include <atomic>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <dirent.h>
#include <initializer_list>
#include <sys/stat.h>
#include <unistd.h>

#include "driver/gpio.h"
#include "driver/spi_common.h"
#include "driver/sdspi_host.h"
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "audio_recorder.h"
#include "inference_pipeline.h"
#include "wav_file.h"

static const char *TAG = "DURIAN_AI";
constexpr gpio_num_t BUTTONS[] = {GPIO_NUM_1, GPIO_NUM_2, GPIO_NUM_3};
constexpr gpio_num_t LED = GPIO_NUM_7;
constexpr bool LED_ACTIVE_HIGH = true; // LED anode through resistor to GPIO7, cathode to GND.
constexpr bool BUTTON_ACTIVE_LOW = true; // Buttons connect their GPIO to GND when pressed.

// LED state is owned by a separate task so inference and SD writes cannot freeze it.
enum class LedMode { Idle, Recording, Processing, Green, Ripe, Error };
static std::atomic<LedMode> led_mode{LedMode::Idle};
static void led_task(void *) {
    LedMode previous = LedMode::Idle;
    unsigned tick = 0;
    while (true) {
        const LedMode mode = led_mode.load();
        if (mode != previous) { tick = 0; previous = mode; }
        bool on = false;
        switch (mode) {
        case LedMode::Idle: break;
        case LedMode::Recording: on = true; break;
        case LedMode::Processing: on = tick % 10 < 5; break;
        case LedMode::Green: on = tick % 30 < 3; break; // One flash per 3 seconds.
        case LedMode::Ripe: on = tick % 30 < 3 || (tick % 30 >= 6 && tick % 30 < 9); break;
        case LedMode::Error: on = tick % 2 == 0; break;
        }
        gpio_set_level(LED, on == LED_ACTIVE_HIGH);
        tick = (tick + 1) % 30;
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

class Button {
public:
    void reset(gpio_num_t pin) {
        pin_ = pin;
        raw_ = stable_ = pressed();
        changed_ = xTaskGetTickCount();
    }
    bool poll() {
        const bool down = pressed();
        const TickType_t now = xTaskGetTickCount();
        if (down != raw_) { raw_ = down; changed_ = now; }
        if (stable_ != raw_ && now - changed_ >= pdMS_TO_TICKS(40)) {
            stable_ = raw_;
            return stable_; // Only the debounced press edge, never autorepeat.
        }
        return false;
    }
private:
    bool pressed() const { return gpio_get_level(pin_) == (BUTTON_ACTIVE_LOW ? 0 : 1); }
    gpio_num_t pin_ = GPIO_NUM_NC;
    bool raw_ = false, stable_ = false;
    TickType_t changed_ = 0;
};

static esp_err_t mount_sd() {
    sdmmc_host_t host = SDSPI_HOST_DEFAULT();
    spi_bus_config_t bus = {};
    bus.mosi_io_num = GPIO_NUM_11;
    bus.miso_io_num = GPIO_NUM_10;
    bus.sclk_io_num = GPIO_NUM_12;
    bus.quadwp_io_num = bus.quadhd_io_num = -1;
    bus.max_transfer_sz = 4096;
    esp_err_t err = spi_bus_initialize(static_cast<spi_host_device_t>(host.slot), &bus, SDSPI_DEFAULT_DMA);
    if (err != ESP_OK) return err;
    sdspi_device_config_t device = SDSPI_DEVICE_CONFIG_DEFAULT();
    device.host_id = static_cast<spi_host_device_t>(host.slot);
    device.gpio_cs = GPIO_NUM_13;
    esp_vfs_fat_sdmmc_mount_config_t config = {};
    config.format_if_mount_failed = false;
    config.max_files = 5;
    config.allocation_unit_size = 16 * 1024;
    sdmmc_card_t *card = nullptr;
    err = esp_vfs_fat_sdspi_mount("/sdcard", &host, &device, &config, &card);
    if (err != ESP_OK) {
        spi_bus_free(device.host_id);
        return err;
    }
    for (const char *folder : {"/sdcard/CHIN", "/sdcard/XANH"}) {
        if (mkdir(folder, 0775) != 0 && errno != EEXIST) return ESP_FAIL;
        struct stat st{};
        if (stat(folder, &st) != 0 || !S_ISDIR(st.st_mode)) return ESP_FAIL;
    }
    return ESP_OK;
}

// Eight-digit monotonic IDs work with FAT short names; no RTC or long-name option needed.
// TMP files reserve IDs too, but only finalized valid WAV files can be inferred.
static esp_err_t scan_recordings(uint32_t &highest, char *latest, size_t capacity) {
    highest = 0;
    uint32_t latest_id = 0;
    latest[0] = 0;
    for (const char *label : {"CHIN", "XANH"}) {
        char folder[32];
        snprintf(folder, sizeof(folder), "/sdcard/%s", label);
        DIR *dir = opendir(folder);
        if (!dir) return ESP_FAIL;
        while (dirent *entry = readdir(dir)) {
            const char *name = entry->d_name;
            if (strlen(name) != 12 || name[8] != '.') continue;
            uint32_t id = 0;
            bool digits = true;
            for (unsigned i = 0; i < 8; ++i) {
                if (name[i] < '0' || name[i] > '9') { digits = false; break; }
                id = id * 10 + unsigned(name[i] - '0');
            }
            if (!digits || (strcmp(name + 9, "WAV") && strcmp(name + 9, "TMP"))) continue;
            if (id > highest) highest = id;
            if (strcmp(name + 9, "WAV") || id <= latest_id) continue;
            char path[64];
            snprintf(path, sizeof(path), "%s/%.12s", folder, name);
            FILE *file = fopen(path, "rb");
            uint32_t samples = 0;
            const bool valid = file && wav::read_header(file, samples);
            if (file) fclose(file);
            if (valid) {
                latest_id = id;
                snprintf(latest, capacity, "%s", path);
            }
        }
        closedir(dir);
    }
    return ESP_OK;
}

extern "C" void app_main(void) {
    gpio_config_t led_config = {};
    led_config.pin_bit_mask = 1ULL << LED;
    led_config.mode = GPIO_MODE_OUTPUT;
    ESP_ERROR_CHECK(gpio_config(&led_config));
    gpio_set_level(LED, !LED_ACTIVE_HIGH);
    gpio_config_t buttons_config = {};
    buttons_config.pin_bit_mask = (1ULL << BUTTONS[0]) | (1ULL << BUTTONS[1]) | (1ULL << BUTTONS[2]);
    buttons_config.mode = GPIO_MODE_INPUT;
    buttons_config.pull_up_en = BUTTON_ACTIVE_LOW ? GPIO_PULLUP_ENABLE : GPIO_PULLUP_DISABLE;
    buttons_config.pull_down_en = BUTTON_ACTIVE_LOW ? GPIO_PULLDOWN_DISABLE : GPIO_PULLDOWN_ENABLE;
    ESP_ERROR_CHECK(gpio_config(&buttons_config));
    ESP_ERROR_CHECK(xTaskCreate(led_task, "status_led", 2048, nullptr, 2, nullptr) == pdPASS ? ESP_OK : ESP_ERR_NO_MEM);
    Button buttons[3];
    for (unsigned i = 0; i < 3; ++i) buttons[i].reset(BUTTONS[i]);

    AudioRecorder recorder;
    esp_err_t err = heap_caps_get_free_size(MALLOC_CAP_SPIRAM) ? mount_sd() : ESP_ERR_NO_MEM;
    if (err == ESP_OK) err = recorder.init();
    uint32_t highest = 0;
    char latest[64] = {};
    if (err == ESP_OK) err = scan_recordings(highest, latest, sizeof(latest));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Initialization failed: %s; check PSRAM/SD and restart", esp_err_to_name(err));
        led_mode.store(LedMode::Error);
        while (true) vTaskDelay(pdMS_TO_TICKS(1000));
    }
    ESP_LOGI(TAG, "Ready. Button 1=CHIN, 2=XANH, 3=infer latest: %s", latest);
    Ics43434 mic;
    int recording_button = -1;
    char temporary[64] = {}, destination[64] = {};
    while (true) {
        bool press[3];
        for (unsigned i = 0; i < 3; ++i) press[i] = buttons[i].poll();
        if (recorder.is_recording()) {
            // Ignore the other label and Play entirely while recording.
            if (press[recording_button] || recorder.error() != ESP_OK) {
                err = recorder.stop(); // Drain queued PCM, finalize header, close file.
                const esp_err_t mic_err = mic.end();
                if (err == ESP_OK && mic_err != ESP_OK) err = mic_err;
                if (err == ESP_OK && rename(temporary, destination) != 0) err = ESP_FAIL;
                if (err == ESP_OK) {
                    snprintf(latest, sizeof(latest), "%s", destination);
                    ESP_LOGI(TAG, "Saved %s", latest);
                    led_mode.store(LedMode::Idle);
                } else {
                    ESP_LOGE(TAG, "Recording failed: %s; unfinished file: %s", esp_err_to_name(err), temporary);
                    led_mode.store(LedMode::Error);
                }
                recording_button = -1;
            }
        } else if ((press[0] || press[1]) && !(press[0] && press[1]) && !press[2]) {
            const int button = press[0] ? 0 : 1;
            const char *label = button == 0 ? "CHIN" : "XANH";
            if (highest >= 99999999) {
                ESP_LOGE(TAG, "Recording ID space exhausted");
                led_mode.store(LedMode::Error);
            } else {
                ++highest;
                snprintf(temporary, sizeof(temporary), "/sdcard/%s/%08lu.TMP", label, static_cast<unsigned long>(highest));
                snprintf(destination, sizeof(destination), "/sdcard/%s/%08lu.WAV", label, static_cast<unsigned long>(highest));
                Ics43434::Config config;
                config.bclk = GPIO_NUM_5;
                config.ws = GPIO_NUM_6;
                config.din = GPIO_NUM_4;
                config.sample_rate_hz = AudioRecorder::SAMPLE_RATE_HZ;
                config.right_channel = false;
                err = mic.begin(config);
                if (err == ESP_OK) err = recorder.start(mic, temporary);
                if (err == ESP_OK) {
                    recording_button = button;
                    led_mode.store(LedMode::Recording);
                    ESP_LOGI(TAG, "Recording %s; press button %d again to stop", label, button + 1);
                } else {
                    (void)mic.end();
                    ESP_LOGE(TAG, "Start failed: %s", esp_err_to_name(err));
                    led_mode.store(LedMode::Error);
                }
            }
        } else if (press[2] && !press[0] && !press[1]) {
            if (!latest[0]) {
                ESP_LOGW(TAG, "No finalized recording available");
                led_mode.store(LedMode::Error);
            } else {
                led_mode.store(LedMode::Processing);
                ESP_LOGI(TAG, "Inferring %s", latest);
                int prediction = -1;
                err = infer_latest_wav(latest, prediction);
                if (err == ESP_OK) {
                    ESP_LOGI(TAG, "Result: %s", prediction == 1 ? "CHIN" : "XANH");
                    led_mode.store(prediction == 1 ? LedMode::Ripe : LedMode::Green);
                } else {
                    ESP_LOGE(TAG, "Inference failed: %s", esp_err_to_name(err));
                    led_mode.store(LedMode::Error);
                }
            }
            // Discard presses during inference; held buttons must be released first.
            for (unsigned i = 0; i < 3; ++i) buttons[i].reset(BUTTONS[i]);
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
