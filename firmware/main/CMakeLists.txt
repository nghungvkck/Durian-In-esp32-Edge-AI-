idf_component_register(
    SRCS "main.cpp" "ics43434.cpp" "audio_recorder.cpp" "audio_processor.cpp"
    INCLUDE_DIRS "."
    REQUIRES esp-dl esp_driver_i2s esp_driver_gpio
)

target_add_binary_data(${COMPONENT_LIB}
    "${CMAKE_CURRENT_LIST_DIR}/../models/durian_student_pruned.espdl"
    BINARY
)
