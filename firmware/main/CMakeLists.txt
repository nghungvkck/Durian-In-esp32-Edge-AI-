idf_component_register(
    SRCS 
    "src/main.cpp" "src/ics43434.cpp" "src/audio_recorder.cpp" 
    "src/audio_processor.cpp" "src/mel_extractor.cpp" "src/spectrogram_resize.cpp"
    INCLUDE_DIRS "include"
    REQUIRES esp-dl esp_driver_i2s esp_driver_gpio
)

target_add_binary_data(${COMPONENT_LIB}
    "${CMAKE_CURRENT_LIST_DIR}/../models/durian_student_pruned.espdl"
    BINARY
)
