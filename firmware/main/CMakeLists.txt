idf_component_register(
    SRCS "firmware.cpp"
    INCLUDE_DIRS "."
    REQUIRES esp-dl
)

target_add_binary_data(${COMPONENT_LIB}
    "${CMAKE_CURRENT_LIST_DIR}/../models/durian_student_pruned.espdl"
    BINARY
)
