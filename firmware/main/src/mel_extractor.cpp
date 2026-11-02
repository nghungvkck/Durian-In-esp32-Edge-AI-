#include "mel_extractor.h"

#include <cmath>
#include <cstring>
#include <algorithm>

#include "esp_heap_caps.h"

namespace {
constexpr float PI = 3.14159265358979323846f;
constexpr float EPSILON = 1.0e-10f;
constexpr float SAMPLE_RATE = 16000.0f;
}

float MelExtractor::hz_to_mel(float hz) {
    constexpr float MIN_LOG_HZ = 1000.0f;
    constexpr float MIN_LOG_MEL = 15.0f;
    constexpr float LOGSTEP = 0.06875177742094912f;

    if (hz < MIN_LOG_HZ) {
        return hz * (3.0f / 200.0f);
    }

    return MIN_LOG_MEL + std::log(hz / MIN_LOG_HZ) / LOGSTEP;
}

float MelExtractor::mel_to_hz(float mel) {
    constexpr float MIN_LOG_HZ = 1000.0f;
    constexpr float MIN_LOG_MEL = 15.0f;
    constexpr float LOGSTEP = 0.06875177742094912f;

    if (mel < MIN_LOG_MEL) {
        return mel * (200.0f / 3.0f);
    }

    return MIN_LOG_HZ * std::exp(LOGSTEP * (mel - MIN_LOG_MEL));
}

void MelExtractor::fft(float *real, float *imag) {
    size_t j = 0;

    for (size_t i = 1; i < N_FFT; i++) {
        size_t bit = N_FFT >> 1;

        while (j & bit) {
            j ^= bit;
            bit >>= 1;
        }

        j ^= bit;

        if (i < j) {
            std::swap(real[i], real[j]);
            std::swap(imag[i], imag[j]);
        }
    }

    for (size_t len = 2; len <= N_FFT; len <<= 1) {
        const float angle = -2.0f * PI / static_cast<float>(len);
        const float wlen_real = std::cos(angle);
        const float wlen_imag = std::sin(angle);

        for (size_t i = 0; i < N_FFT; i += len) {
            float w_real = 1.0f;
            float w_imag = 0.0f;

            for (size_t k = 0; k < len / 2; k++) {
                const size_t u = i + k;
                const size_t v = u + len / 2;

                const float v_real =
                    real[v] * w_real - imag[v] * w_imag;

                const float v_imag =
                    real[v] * w_imag + imag[v] * w_real;

                real[v] = real[u] - v_real;
                imag[v] = imag[u] - v_imag;

                real[u] += v_real;
                imag[u] += v_imag;

                const float next_w_real =
                    w_real * wlen_real - w_imag * wlen_imag;

                w_imag =
                    w_real * wlen_imag + w_imag * wlen_real;

                w_real = next_w_real;
            }
        }
    }
}

esp_err_t MelExtractor::extract(
    const int16_t *audio,
    size_t sample_count,
    float *output,
    size_t output_capacity,
    size_t &n_frames
) {
    n_frames = 0;

    if (audio == nullptr || output == nullptr || sample_count == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    n_frames = 1 + sample_count / HOP_LENGTH;

    if (n_frames > MAX_FRAMES ||
        output_capacity < N_MELS * n_frames) {
        n_frames = 0;
        return ESP_ERR_INVALID_SIZE;
    }

    float *real = static_cast<float *>(
        heap_caps_malloc(N_FFT * sizeof(float),
                         MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT)
    );

    float *imag = static_cast<float *>(
        heap_caps_malloc(N_FFT * sizeof(float),
                         MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT)
    );

    float *power = static_cast<float *>(
        heap_caps_malloc((N_FFT / 2 + 1) * sizeof(float),
                         MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT)
    );

    float *filters = static_cast<float *>(
        heap_caps_calloc(
            N_MELS * (N_FFT / 2 + 1),
            sizeof(float),
            MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT
        )
    );

    if (!real || !imag || !power || !filters) {
        if (real) heap_caps_free(real);
        if (imag) heap_caps_free(imag);
        if (power) heap_caps_free(power);
        if (filters) heap_caps_free(filters);

        n_frames = 0;
        return ESP_ERR_NO_MEM;
    }

    const size_t n_bins = N_FFT / 2 + 1;

    const float mel_min = hz_to_mel(FMIN);
    const float mel_max = hz_to_mel(FMAX);

    float mel_points[N_MELS + 2];
    size_t bin_points[N_MELS + 2];

    for (size_t i = 0; i < N_MELS + 2; i++) {
        const float mel = mel_min +
            (mel_max - mel_min) * i / (N_MELS + 1);

        mel_points[i] = mel_to_hz(mel);

        bin_points[i] = static_cast<size_t>(
            std::floor((N_FFT + 1) * mel_points[i] / SAMPLE_RATE)
        );

        if (bin_points[i] >= n_bins) {
            bin_points[i] = n_bins - 1;
        }
    }

    for (size_t m = 0; m < N_MELS; m++) {
        const size_t left = bin_points[m];
        const size_t center = bin_points[m + 1];
        const size_t right = bin_points[m + 2];

        for (size_t k = left; k < center; k++) {
            if (center > left) {
                filters[m * n_bins + k] =
                    static_cast<float>(k - left) / (center - left);
            }
        }

        for (size_t k = center; k < right; k++) {
            if (right > center) {
                filters[m * n_bins + k] =
                    static_cast<float>(right - k) / (right - center);
            }
        }
    }

    float global_max = 0.0f;

    for (size_t frame = 0; frame < n_frames; frame++) {
        const int64_t frame_start =
            static_cast<int64_t>(frame * HOP_LENGTH) -
            static_cast<int64_t>(N_FFT / 2);

        for (size_t i = 0; i < N_FFT; i++) {
            const int64_t index = frame_start + i;

            float sample = 0.0f;

            if (index >= 0 &&
                static_cast<size_t>(index) < sample_count) {
                sample = static_cast<float>(audio[index]) / 32768.0f;
            }

            const float hann =
                0.5f - 0.5f * std::cos(
                    2.0f * PI * i / N_FFT
                );

            real[i] = sample * hann;
            imag[i] = 0.0f;
        }

        fft(real, imag);

        for (size_t k = 0; k < n_bins; k++) {
            power[k] =
                real[k] * real[k] + imag[k] * imag[k];
        }

        for (size_t m = 0; m < N_MELS; m++) {
            float energy = 0.0f;

            for (size_t k = 0; k < n_bins; k++) {
                energy += power[k] * filters[m * n_bins + k];
            }

            output[m * n_frames + frame] = energy;

            if (energy > global_max) {
                global_max = energy;
            }
        }
    }

    const float reference = std::max(global_max, EPSILON);
    const float min_db = 10.0f * std::log10(reference) - 80.0f;

    for (size_t i = 0; i < N_MELS * n_frames; i++) {
        const float energy = std::max(output[i], EPSILON);
        float db = 10.0f * std::log10(energy);

        db = std::max(db, min_db);
        output[i] = db - 10.0f * std::log10(reference);
    }

    heap_caps_free(real);
    heap_caps_free(imag);
    heap_caps_free(power);
    heap_caps_free(filters);

    return ESP_OK;
}