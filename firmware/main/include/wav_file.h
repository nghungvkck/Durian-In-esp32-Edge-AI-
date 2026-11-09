#pragma once

#include <cstdint>
#include <cstdio>
#include <cstring>

// Application WAV format: 44-byte RIFF header, mono PCM16 little endian, 16 kHz.
namespace wav {
constexpr uint32_t RATE = 16000;
constexpr long HEADER_BYTES = 44;
// Keep file offsets representable by ESP-IDF's signed 32-bit long/fseek.
constexpr uint32_t MAX_DATA_BYTES = 0x7fffff00;
inline void put16(uint8_t *p, uint16_t v) { p[0] = v; p[1] = v >> 8; }
inline void put32(uint8_t *p, uint32_t v) {
    for (unsigned i = 0; i < 4; ++i) p[i] = v >> (8 * i);
}
inline uint32_t get32(const uint8_t *p) {
    return uint32_t(p[0]) | (uint32_t(p[1]) << 8) |
           (uint32_t(p[2]) << 16) | (uint32_t(p[3]) << 24);
}
inline bool write_header(FILE *f, uint32_t bytes) {
    uint8_t h[44] = {};
    memcpy(h, "RIFF", 4); put32(h + 4, bytes + 36);
    memcpy(h + 8, "WAVEfmt ", 8); put32(h + 16, 16);
    put16(h + 20, 1); put16(h + 22, 1);
    put32(h + 24, RATE); put32(h + 28, RATE * 2);
    put16(h + 32, 2); put16(h + 34, 16);
    memcpy(h + 36, "data", 4); put32(h + 40, bytes);
    return fseek(f, 0, SEEK_SET) == 0 && fwrite(h, 1, sizeof(h), f) == sizeof(h);
}
inline bool read_header(FILE *f, uint32_t &samples) {
    uint8_t h[44];
    if (fseek(f, 0, SEEK_SET) != 0 || fread(h, 1, sizeof(h), f) != sizeof(h)) return false;
    if (memcmp(h, "RIFF", 4) || memcmp(h + 8, "WAVEfmt ", 8) ||
        get32(h + 16) != 16 || h[20] != 1 || h[21] != 0 ||
        h[22] != 1 || h[23] != 0 || get32(h + 24) != RATE ||
        get32(h + 28) != RATE * 2 || h[32] != 2 || h[33] != 0 ||
        h[34] != 16 || h[35] != 0 || memcmp(h + 36, "data", 4)) return false;
    const uint32_t bytes = get32(h + 40);
    if (!bytes || bytes > MAX_DATA_BYTES || bytes % 2 || get32(h + 4) != bytes + 36) return false;
    if (fseek(f, 0, SEEK_END) != 0 || ftell(f) != HEADER_BYTES + long(bytes)) return false;
    samples = bytes / 2;
    return fseek(f, HEADER_BYTES, SEEK_SET) == 0;
}
} // namespace wav
