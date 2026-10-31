# Chức năng các file trong firmware

Tài liệu này mô tả cấu trúc `firmware/` theo hiện trạng ngày 31/10/2026. Quy trình build, nạp code/model và xử lý lỗi nằm trong [README.md](README.md).

## 1. Sơ đồ thư mục

```text
firmware/
├── CMakeLists.txt
├── README.md
├── README_FILES.md
├── sdkconfig
├── sdkconfig.defaults
├── dependencies.lock
├── main/
│   ├── CMakeLists.txt
│   ├── firmware.cpp
│   ├── ics43434.h
│   ├── ics43434.cpp
│   └── idf_component.yml
├── models/
│   └── durian_student_pruned.espdl
├── managed_components/
│   ├── espressif__esp-dl/
│   ├── espressif__dl_fft/
│   └── espressif__esp_new_jpeg/
└── build/
    ├── firmware.bin
    ├── firmware.elf
    ├── firmware.map
    ├── bootloader/
    ├── partition_table/
    └── ...
```

## 2. Các file ở thư mục gốc

### `CMakeLists.txt`

File cấu hình build cấp dự án. File này chọn phiên bản CMake tối thiểu, nạp hệ thống build của ESP-IDF qua biến môi trường `IDF_PATH`, và đặt tên project là `firmware`.

Tên project cũng được dùng cho các file đầu ra `firmware.bin`, `firmware.elf` và `firmware.map`.

### `sdkconfig`

Chứa toàn bộ cấu hình đang có hiệu lực cho lần build hiện tại, như target ESP32-S3, flash, PSRAM, FreeRTOS, log và bảng phân vùng.

Các cấu hình quan trọng hiện nay:

- PSRAM Quad 40 MHz, khởi tạo và kiểm tra lúc boot, cho phép cấp phát qua heap.
- Flash trong image header là 2 MB, trong khi flash vật lý của board là 4 MB.
- Phân vùng app `factory` 1500 KiB để chứa firmware kèm model.

Thông thường dùng `idf.py menuconfig` để thay đổi cấu hình. CMake/ESP-IDF sẽ đọc file này khi build và sinh header cấu hình cho C/C++.

### `sdkconfig.defaults`

Lưu các giá trị mặc định cần thiết của dự án: bật PSRAM và dùng phân vùng app lớn. Giúp tái tạo cấu hình khi chưa có `sdkconfig`.

File này chỉ chứa các thiết lập dự án cần giữ, trong khi `sdkconfig` chứa cấu hình đầy đủ. Giá trị mặc định không tự ghi đè một giá trị đã được thiết lập trong `sdkconfig`.

### `dependencies.lock`

Do ESP-IDF Component Manager quản lý, ghi lại các phiên bản thư viện đã resolve, nguồn tải và mã kiểm tra của chúng. Nhờ đó các lần build có thể dùng lại bộ dependency đã chọn.

Bản hiện tại ghi ESP-DL 3.3.14, `dl_fft` 0.8.0, `esp_new_jpeg` 1.0.2 và ESP-IDF 5.3.6. Khai báo yêu cầu thư viện ở `main/idf_component.yml`; không cần sửa tay file lock trong quy trình build thông thường.

### `README.md` và `README_FILES.md`

- [README.md](README.md): thông tin board, quy trình quantize/copy model/build/flash, kết quả chạy và các lỗi đã gặp.
- [README_FILES.md](README_FILES.md): bản đồ chức năng các file và thư mục, tức tài liệu đang đọc.

## 3. Thư mục `main/` — code ứng dụng

### `main/firmware.cpp`

Code ứng dụng chính chạy trên ESP32-S3. Hàm `app_main()` là điểm bắt đầu của ứng dụng sau khi ESP-IDF khởi tạo hệ thống.

Luồng hiện tại:

1. In log khởi động và dung lượng PSRAM còn trống.
2. Dừng khởi tạo model nếu không có PSRAM khả dụng.
3. Dùng symbol `_binary_durian_student_pruned_espdl_start` để lấy địa chỉ model đã nhúng trong flash.
4. Tạo `dl::Model` với `MODEL_LOCATION_IN_FLASH_RODATA` và `max_internal_size = 0`; khi PSRAM được bật, ESP-DL cấp phát vùng tensor vào PSRAM.
5. Kiểm tra tensor input/output đã tồn tại và có bộ nhớ trước khi chạy test.
6. Gọi `model->test()` với dữ liệu kiểm thử đã export kèm model và in kết quả PASS/FAIL.
7. In cấu trúc các lớp bằng `model->print()`, rồi chờ trong vòng lặp có `vTaskDelay()`.

File này hiện chưa đọc micro, tính Mel-Spectrogram hoặc phân loại âm thanh thu trực tiếp. Đó là các chức năng cần bổ sung khi triển khai luồng suy luận thực tế.

### `main/ics43434.h` và `main/ics43434.cpp`

Class `Ics43434` dùng driver I2S standard của ESP-IDF 5.3 để thu âm mono từ ICS-43434. Header khai báo cấu hình chân, tần số lấy mẫu và API `begin()`, `read()`, `end()`, `is_started()`, `to_float()`; file `.cpp` chứa phần cài đặt và quản lý tài nguyên I2S/DMA.

Mặc định 16 kHz, dữ liệu PCM 24 bit có dấu lưu trong `int32_t`. Chân BCLK/WS/DIN phải truyền qua `Config`. Class chưa được gọi trong `firmware.cpp`, chưa tạo Mel hoặc chạy phân loại, và chưa xác nhận bằng micro thật. Xem mục 6 trong [README.md](README.md) để nối dây và xem ví dụ gọi.

### `main/CMakeLists.txt`

Cấu hình riêng cho component ứng dụng `main`:

- `SRCS "firmware.cpp" "ics43434.cpp"`: chọn file nguồn để biên dịch.
- `INCLUDE_DIRS "."`: thêm thư mục hiện tại vào đường dẫn tìm header.
- `REQUIRES esp-dl esp_driver_i2s esp_driver_gpio`: khai báo phụ thuộc ESP-DL và driver I2S/GPIO.
- `target_add_binary_data(...)`: nhúng `models/durian_student_pruned.espdl` dưới dạng dữ liệu nhị phân vào component.

Nhờ bước nhúng này, linker tạo được symbol mà `firmware.cpp` sử dụng. Nếu đổi tên model, cần cập nhật cả đường dẫn tại đây và tên symbol trong C++.

### `main/idf_component.yml`

Manifest khai báo thư viện cần tải từ ESP Component Registry. Hiện có:

```yaml
dependencies:
  espressif/esp-dl: "*"
```

`"*"` cho phép Component Manager lựa chọn phiên bản phù hợp khi resolve. Phiên bản đã chọn được ghi trong `dependencies.lock`, còn mã thư viện được đưa vào `managed_components/`.

## 4. Thư mục `models/` — model dùng trên board

### `models/durian_student_pruned.espdl`

Model ESP-DL INT8 đã chuyển từ checkpoint PyTorch sau pruning. Đây là bản model được build thực sự vào firmware.

Nguồn tạo model nằm ngoài thư mục firmware:

```text
pth/best_pruned_student.pth
    → Pruning_Model/quantize_pruned.py
    → espdl/durian_student_pruned.espdl
    → copy sang firmware/models/durian_student_pruned.espdl
```

Model được nhúng vào `firmware.bin` và flash cùng code. Khi thay model, cập nhật file trong `models/`, build và flash lại; không nạp file `.pth` trực tiếp lên ESP32.

## 5. Thư mục `managed_components/` — thư viện được quản lý

| Thư mục | Chức năng |
| --- | --- |
| `espressif__esp-dl/` | Runtime suy luận: đọc model `.espdl`, quản lý tensor/bộ nhớ, thực thi các toán tử như Conv, Pool và Gemm, kiểm thử model |
| `espressif__dl_fft/` | Thư viện phép biến đổi FFT, là dependency của ESP-DL |
| `espressif__esp_new_jpeg/` | Thư viện xử lý JPEG, được kéo theo dependency của ESP-DL |

Các thư viện có thể cung cấp nhiều chức năng hơn ứng dụng đang sử dụng. Có thư viện FFT/JPEG trong dependency không đồng nghĩa firmware hiện đã có luồng thu âm hoặc xử lý ảnh.

Thư mục này do Component Manager tải và quản lý. Trong quy trình phát triển thông thường, chỉnh code ứng dụng trong `main/`, khai báo dependency ở manifest và để công cụ quản lý thư viện này.

## 6. Thư mục `build/` — kết quả tự sinh

Đây là đầu ra của CMake, Ninja và ESP-IDF. Không phải nơi sửa code nguồn; các file có thể được tạo lại khi configure/build.

| File/thư mục | Chức năng |
| --- | --- |
| `firmware.bin` | Image ứng dụng chứa code và model nhúng, được ghi vào phân vùng `factory` |
| `firmware.elf` | Chương trình đã link có symbol phục vụ debug và giải mã địa chỉ lỗi/backtrace |
| `firmware.map` | Bản đồ linker: vị trí, kích thước các section và symbol; dùng phân tích flash/RAM |
| `bootloader/bootloader.bin` | Bootloader chọn phân vùng ứng dụng và khởi động firmware |
| `partition_table/partition-table.bin` | Bảng phân vùng nhị phân, mô tả vị trí/kích thước NVS, PHY và app trong flash |
| `durian_student_pruned.espdl.S` | Assembly tự sinh để đưa byte của model vào binary và tạo symbol truy cập |
| `esp-idf/` | Object và thư viện trung gian của các component, cùng dữ liệu phục vụ link |
| `config/` | Cấu hình sinh từ `sdkconfig`, gồm header `sdkconfig.h` và các định dạng cho công cụ build |
| `CMakeCache.txt`, `CMakeFiles/` | Cache và dữ liệu nội bộ của CMake, gồm thông tin công cụ và đường dẫn môi trường |
| `build.ninja`, `cmake_install.cmake` | Các chỉ dẫn build/install tự sinh từ CMake |
| `compile_commands.json` | Các lệnh biên dịch từng file nguồn; hữu ích cho IDE và công cụ phân tích code |
| `flash_args`, `flasher_args.json` và các file `*flash*args*` | Các tham số flash: file binary, offset và thiết lập flash cho esptool/ESP-IDF |
| `project_description.json` | Metadata về project, component và file đầu ra cho các công cụ ESP-IDF |
| `project_elf_src_esp32s3.c` | File nguồn phụ trợ do hệ thống build sinh cho executable của project |
| `log/` | Log stdout/stderr của các lệnh ESP-IDF, hữu ích khi build hoặc flash thất bại |
| `gdbinit` | Thiết lập hỗ trợ GDB debug |
| `bootloader-prefix/` | Dữ liệu điều phối việc build bootloader như một project phụ |
| `config.env`, `kconfigs*.in`, `ldgen_libraries*` | Dữ liệu trung gian cho cấu hình Kconfig và sinh linker script |
| `x509_crt_bundle.S` | Dữ liệu chứng chỉ được sinh trong quá trình build theo cấu hình ESP-IDF |
| `component_manager_run_counter.*`, `components_with_manifests_list.temp.overrides` | Dữ liệu nội bộ phục vụ Component Manager trong quá trình cấu hình/build |

Tại bản build đã kiểm chứng, `idf.py flash` dùng các offset:

```text
0x00000000 → build/bootloader/bootloader.bin
0x00008000 → build/partition_table/partition-table.bin
0x00010000 → build/firmware.bin  (đã chứa model)
```

Các offset này thuộc cấu hình hiện tại. Dùng `idf.py flash` để công cụ lấy đúng tham số của bản build, thay vì tự ghi nhớ offset cho những cấu hình khác.

## 7. Muốn thay đổi chức năng thì sửa file nào?

| Việc cần làm | File/thư mục liên quan |
| --- | --- |
| Sửa luồng chạy, thêm thu âm hoặc gọi suy luận | `main/firmware.cpp`, hoặc thêm source/header mới vào `main/` |
| Thêm source vào build, nhúng model với tên khác | `main/CMakeLists.txt` |
| Thay trọng số/model | Export lại ngoài firmware, copy `.espdl` vào `models/`, rồi build/flash |
| Đổi target, PSRAM, flash, phân vùng hoặc mức log | Cấu hình qua `idf.py menuconfig`; kết quả nằm ở `sdkconfig` |
| Giữ cấu hình mặc định cho lần tạo project mới | `sdkconfig.defaults` |
| Thêm hoặc đổi yêu cầu phiên bản thư viện | `main/idf_component.yml` |
| Xem nguyên nhân build lỗi | `build/log/` và output lệnh `idf.py` |
| Phân tích lỗi runtime hoặc mức sử dụng bộ nhớ | Log board, `build/firmware.elf`, `build/firmware.map` |

Khi thêm source mới vào `main/`, nhớ cập nhật danh sách `SRCS` trong `main/CMakeLists.txt`. Xem [README.md](README.md) để thực hiện đúng quy trình build và nạp sau khi sửa.
