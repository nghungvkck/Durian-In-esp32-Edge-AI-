# ON: WAV test in flash; OFF: normal recording application (src/main.cpp).
set(FIRMWARE_MODEL_TEST ON)

set(app_sources
    "src/inference_pipeline.cpp" "src/audio_processor.cpp"
    "src/mel_extractor.cpp" "src/spectrogram_resize.cpp"
)
if(FIRMWARE_MODEL_TEST)
    list(APPEND app_sources "../test/model_only.cpp")
else()
    list(APPEND app_sources "src/main.cpp" "src/ics43434.cpp" "src/audio_recorder.cpp")
endif()

idf_component_register(
    SRCS ${app_sources}
    INCLUDE_DIRS "include"
    REQUIRES esp-dl esp_timer esp_driver_i2s esp_driver_gpio esp_driver_spi esp_driver_sdspi sdmmc fatfs
)

target_add_binary_data(${COMPONENT_LIB}
    "${CMAKE_CURRENT_LIST_DIR}/../models/durian_student_pruned.espdl"
    BINARY
)

if(FIRMWARE_MODEL_TEST)
    target_add_binary_data(${COMPONENT_LIB}
        "${CMAKE_CURRENT_LIST_DIR}/../test/20260717_172242.wav"
        BINARY
    )
endif()
