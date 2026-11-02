#pragma once

#include <cstddef>
#include <cstdint>

#include "esp_err.h"

class MelExtractor {
public:
    static constexpr size_t N_FFT = 2048;
    static constexpr size_t HOP_LENGTH = 256;   
    static constexpr size_t N_MELS = 128;

    static constexpr float FMIN = 50.0f;
    static constexpr float FMAX = 2000.0f;

    static constexpr size_t MAX_FRAMES = 32;

    static constexpr size_t MEL_SIZE = N_MELS * MAX_FRAMES;

    esp_err_t extract(
        const int16_t *audio,
        size_t sample_count,
        float *output,
        size_t output_capacity,
        size_t &n_frames
    );

private:
    void fft(float *real, float *imag);
    float hz_to_mel(float hz);
    float mel_to_hz(float mel);
};