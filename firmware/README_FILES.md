# Chức năng các file trong firmware

Tài liệu này mô tả cấu trúc `firmware/` theo hiện trạng ngày 02/11/2026. Quy trình build, nạp code/model và xử lý lỗi nằm trong [README.md](README.md).

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
│   ├── idf_component.yml
│   ├── include/
│   │   ├── audio_processor.h
│   │   ├── audio_recorder.h
│   │   ├── ics43434.h
│   │   ├── mel_extractor.h
│   │   └── spectrogram_resize.h
│   └── src/
│       ├── main.cpp
│       ├── firmware.cpp
│       ├── audio_processor.cpp
│       ├── audio_recorder.cpp
│       ├── ics43434.cpp
│       ├── mel_extractor.cpp
│       └── spectrogram_resize.cpp
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

Header nằm trong `main/include/`, phần cài đặt C++ nằm trong `main/src/`. CMake và manifest vẫn ở `main/`. Việc sắp xếp thư mục chỉ thay đổi đường dẫn build, giữ nguyên nội dung và logic các file C++/header.

### `main/src/main.cpp`

Đây là file chứa `app_main()` đang được CMake chọn để build. Luồng trong mã nguồn hiện tại:

1. Kiểm tra PSRAM, nạp model nhúng trong flash và kiểm tra tensor input/output.
2. Khởi tạo micro ICS-43434 ở 16 kHz với BCLK GPIO3, WS GPIO2 và DIN GPIO1, nhận kênh trái.
3. Thu âm 5 giây bằng `AudioRecorder`.
4. Phát hiện đỉnh và cắt các đoạn âm thanh bằng `AudioProcessor`.
5. Tính Mel-Spectrogram cho từng đoạn, chuẩn hóa về `[0, 1]` và resize thành `128 × 128`.
6. Lượng tử hóa input INT8 theo exponent của model, gọi `model->run()` và đọc hai điểm số đầu ra.
7. In dự đoán `XANH` (class 0) hoặc `CHIN` (class 1), giải phóng bộ nhớ xử lý rồi chờ.

Mô tả này dựa trên mã nguồn; kết quả test model trên board ngày 31/10/2026 trong [README.md](README.md) thuộc bản kiểm thử trước, chưa xác nhận luồng thu âm và suy luận hiện tại.

### `main/src/firmware.cpp`

Giữ bản code kiểm thử model: kiểm tra PSRAM/tensor, gọi `model->test()`, in cấu trúc model rồi chờ. File này **không nằm trong danh sách `SRCS` hiện tại**, nên không được biên dịch cùng `main.cpp`.

### Các cặp header và source

| Header trong `main/include/` | Source trong `main/src/` | Chức năng |
| --- | --- | --- |
| `ics43434.h` | `ics43434.cpp` | Driver I2S thu PCM mono 24 bit trong `int32_t`, cấu hình chân/kênh và quản lý tài nguyên micro |
| `audio_recorder.h` | `audio_recorder.cpp` | Thu âm 5 giây ở 16 kHz vào buffer PCM `int16_t` |
| `audio_processor.h` | `audio_processor.cpp` | Phát hiện đỉnh, quản lý tối đa 32 đoạn cắt dài 0,24 giây |
| `mel_extractor.h` | `mel_extractor.cpp` | Tạo Mel-Spectrogram: FFT 2048, hop 256, 128 dải Mel, miền 50–2000 Hz, tối đa 32 frame |
| `spectrogram_resize.h` | `spectrogram_resize.cpp` | Resize spectrogram sang kích thước đầu ra do phía gọi truyền vào |

Xem mục 6 trong [README.md](README.md) để biết API micro và ví dụ kiểm tra riêng.

### `main/CMakeLists.txt`

Cấu hình riêng cho component ứng dụng `main`:

- `SRCS`: chọn sáu file `src/main.cpp`, `src/ics43434.cpp`, `src/audio_recorder.cpp`, `src/audio_processor.cpp`, `src/mel_extractor.cpp` và `src/spectrogram_resize.cpp` để biên dịch; không chọn `src/firmware.cpp`.
- `INCLUDE_DIRS "include"`: thêm `main/include/` vào đường dẫn tìm header. Vì vậy source trong `src/` vẫn dùng `#include "ics43434.h"`, không cần đổi thành đường dẫn tương đối.
- `REQUIRES esp-dl esp_driver_i2s esp_driver_gpio`: khai báo phụ thuộc ESP-DL và driver I2S/GPIO.
- `target_add_binary_data(...)`: nhúng `models/durian_student_pruned.espdl` dưới dạng dữ liệu nhị phân vào component.

Nhờ bước nhúng này, linker tạo được symbol mà `main/src/main.cpp` sử dụng. Nếu đổi tên model, cần cập nhật cả đường dẫn tại đây và tên symbol trong C++.

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

Các thư viện có thể cung cấp nhiều chức năng hơn ứng dụng đang sử dụng. Luồng thu âm và xử lý Mel nằm trong code ứng dụng; việc có thư viện JPEG trong dependency không đồng nghĩa ứng dụng đang xử lý ảnh.

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
| Sửa luồng chạy, thêm thu âm hoặc gọi suy luận | `main/src/main.cpp` và các module trong `main/src/`, `main/include/` |
| Thêm source vào build, nhúng model với tên khác | `main/CMakeLists.txt` |
| Thay trọng số/model | Export lại ngoài firmware, copy `.espdl` vào `models/`, rồi build/flash |
| Đổi target, PSRAM, flash, phân vùng hoặc mức log | Cấu hình qua `idf.py menuconfig`; kết quả nằm ở `sdkconfig` |
| Giữ cấu hình mặc định cho lần tạo project mới | `sdkconfig.defaults` |
| Thêm hoặc đổi yêu cầu phiên bản thư viện | `main/idf_component.yml` |
| Xem nguyên nhân build lỗi | `build/log/` và output lệnh `idf.py` |
| Phân tích lỗi runtime hoặc mức sử dụng bộ nhớ | Log board, `build/firmware.elf`, `build/firmware.map` |

Khi thêm source mới vào `main/src/`, đặt header tương ứng trong `main/include/` và cập nhật danh sách `SRCS` trong `main/CMakeLists.txt`. Xem [README.md](README.md) để thực hiện đúng quy trình build và nạp sau khi sửa.
