idf_component_register(
    SRCS "firmware.cpp" "ics43434.cpp"
    INCLUDE_DIRS "."
    REQUIRES esp-dl esp_driver_i2s esp_driver_gpio
)

target_add_binary_data(${COMPONENT_LIB}
    "${CMAKE_CURRENT_LIST_DIR}/../models/durian_student_pruned.espdl"
    BINARY
)
