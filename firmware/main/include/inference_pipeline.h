#pragma once
#include "esp_err.h"
#include <cstdio>
// Returns class 0 (XANH) or 1 (CHIN); tie/no crops is an error.
esp_err_t infer_latest_wav(const char *path, int &prediction);
// Same pipeline for an open, seekable WAV stream (e.g. fmemopen).
// Caller owns the stream. verbose prints model structure and processing stages.
esp_err_t infer_wav(FILE *file, int &prediction, bool verbose = false);
