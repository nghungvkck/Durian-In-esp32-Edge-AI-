#include "ics43434.h"

#include <limits>

Ics43434::~Ics43434()
{
    (void)end();
}

esp_err_t Ics43434::begin(const Config &config)
{
    if (rx_ != nullptr) {
        return ESP_ERR_INVALID_STATE;
    }
    // ICS-43434 supports low-power and high-performance sample-rate bands.
    const bool valid_rate =
        (config.sample_rate_hz >= 6250 && config.sample_rate_hz <= 18750) ||
        (config.sample_rate_hz >= 23000 && config.sample_rate_hz <= 51600);
    if (!valid_rate || !GPIO_IS_VALID_OUTPUT_GPIO(config.bclk) ||
        !GPIO_IS_VALID_OUTPUT_GPIO(config.ws) || !GPIO_IS_VALID_GPIO(config.din) ||
        config.bclk == config.ws || config.bclk == config.din || config.ws == config.din) {
        return ESP_ERR_INVALID_ARG;
    }

    i2s_chan_config_t channel = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    channel.dma_desc_num = 6;
    channel.dma_frame_num = 256;
    esp_err_t err = i2s_new_channel(&channel, nullptr, &rx_);
    if (err != ESP_OK) {
        return err;
    }

    i2s_std_config_t standard = {};
    standard.clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(config.sample_rate_hz);
    // Two 32-bit slots generate the 64 BCLK cycles/frame required by the mic.
    // Receive only the selected slot; the microphone's 24 bits occupy bits 31:8.
    standard.slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(
        I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO);
    standard.slot_cfg.slot_mask = config.right_channel ? I2S_STD_SLOT_RIGHT : I2S_STD_SLOT_LEFT;
    standard.gpio_cfg.mclk = I2S_GPIO_UNUSED;
    standard.gpio_cfg.bclk = config.bclk;
    standard.gpio_cfg.ws = config.ws;
    standard.gpio_cfg.dout = I2S_GPIO_UNUSED;
    standard.gpio_cfg.din = config.din;

    err = i2s_channel_init_std_mode(rx_, &standard);
    if (err == ESP_OK) {
        err = i2s_channel_enable(rx_);
    }
    if (err != ESP_OK) {
        (void)end();
        return err;
    }
    running_ = true;

    // Drain startup data rather than sleeping and leaving it queued in DMA.
    int32_t discard[128];
    size_t remaining = config.sample_rate_hz / 5;
    while (remaining > 0) {
        size_t received = 0;
        const size_t count = remaining < 128 ? remaining : 128;
        err = read(discard, count, received, 1000);
        if (err != ESP_OK || received == 0) {
            (void)end();
            return err != ESP_OK ? err : ESP_FAIL;
        }
        remaining -= received;
    }
    return ESP_OK;
}

esp_err_t Ics43434::read(int32_t *samples, size_t capacity, size_t &samples_read,
                       uint32_t timeout_ms)
{
    samples_read = 0;
    if (!running_) {
        return ESP_ERR_INVALID_STATE;
    }
    if (samples == nullptr || capacity == 0 ||
        capacity > std::numeric_limits<size_t>::max() / sizeof(*samples)) {
        return ESP_ERR_INVALID_ARG;
    }

    size_t bytes_read = 0;
    const esp_err_t err = i2s_channel_read(rx_, samples, capacity * sizeof(*samples),
                                         &bytes_read, timeout_ms);
    samples_read = bytes_read / sizeof(*samples);
    for (size_t i = 0; i < samples_read; ++i) {
        // ESP32 GCC uses arithmetic right shift: preserve the signed PCM value,
        // remove the last 8 bits (the mic releases SD after its 24 data bits).
        samples[i] >>= 8;
    }
    return err;
}

esp_err_t Ics43434::end()
{
    if (rx_ == nullptr) {
        return ESP_OK;
    }
    if (running_) {
        const esp_err_t err = i2s_channel_disable(rx_);
        if (err != ESP_OK) {
            return err;
        }
        running_ = false;
    }
    const esp_err_t err = i2s_del_channel(rx_);
    if (err == ESP_OK) {
        rx_ = nullptr;
    }
    return err;
}
