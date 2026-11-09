# Chức năng các file trong firmware

**Cấu hình board mới N16R8:** `sdkconfig` và `sdkconfig.defaults` đã chuyển
sang Octal PSRAM (8 MB, 40 MHz, auto-detect) và Flash 16 MB. Log ngày
09/11/2026 đã xác nhận build/flash, PSRAM memory test OK và chạy WAV test; mô tả Quad PSRAM 2 MB/Flash 4 MB bên dưới thuộc
board trước. Bảng phân vùng factory vẫn 1500 KiB. Xem đầu README.md.

**Cập nhật 07/11/2026:** CMake hiện chọn `test/model_only.cpp` bằng
`set(FIRMWARE_MODEL_TEST ON)`. File này đọc WAV nhúng
`test/20260717_172242.wav` qua `fmemopen`, gọi `infer_wav` trong pipeline
chính với log chi tiết và in kết quả; không khởi tạo các ngoại vi ứng dụng.
Pipeline dùng chung các module xử lý âm thanh, Mel và resize đã có.
Đổi biến trên thành `OFF` để chọn lại `main/src/main.cpp` và bỏ nhúng WAV test.
API theo đường dẫn file của ứng dụng chính vẫn giữ nguyên.
Chế độ WAV test đã chạy trên board theo log 09/11/2026. Các mô tả chọn source bên dưới
là của chế độ ứng dụng chính (`OFF`).

Cập nhật 09/11/2026: đã đổi đường dẫn nhúng, symbol linker và tên log sang
`20260717_172242.wav` (mono PCM16 16 kHz, 118784 mẫu, 7,424 giây).
Đã chạy WAV này trên N16R8: 5 đoạn, trung bình model **343,5638 ms/đoạn**,
4 phiếu XANH / 1 phiếu CHÍN, kết quả XANH theo mapping hiện tại. Firmware
1474,75 KiB, phân vùng app còn 25,25 KiB. PSRAM 8 MB đã nhận và test OK;
chưa đo RAM/PSRAM tiêu thụ khi suy luận. Bảng số liệu, điều kiện đo và log
nguồn nằm ở mục “Chỉ số triển khai thực tế” trong [README.md](README.md).

Tài liệu này mô tả cấu trúc `firmware/` theo cập nhật ngày 05/11/2026 (chưa build/chạy trên board). Quy trình build, nạp code/model và xử lý lỗi nằm trong [README.md](README.md).

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
│   │   ├── wav_file.h
│   │   ├── inference_pipeline.h
│   │   ├── audio_processor.h
│   │   ├── audio_recorder.h
│   │   ├── ics43434.h
│   │   ├── mel_extractor.h
│   │   └── spectrogram_resize.h
│   └── src/
│       ├── inference_pipeline.cpp
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

Đây là điểm vào CMake chọn để build. Khởi tạo GPIO, task LED, microSD SPI và bộ đệm thu âm, tìm WAV mới nhất trong `CHIN/` và `XANH/`, rồi chờ nút:

1. Nút 1 GPIO1 thu/dừng nhãn CHÍN; nút 2 GPIO2 thu/dừng nhãn XANH. Khi đang thu chỉ chính nút đã bắt đầu có thể dừng; bỏ qua nút còn lại và Play.
2. Micro dùng SD GPIO4, SCK GPIO5, WS GPIO6; chỉ bật trong lúc thu. Ghi WAV liên tục xuống SD (CS13/SCK12/MOSI11/MISO10), hoàn tất `.TMP` → `.WAV` khi dừng thành công.
3. Nút 3 GPIO3 gọi `infer_latest_wav()` cho WAV hoàn tất gần nhất.
4. LED đơn GPIO7: sáng khi thu, nháy chậm khi xử lý, 1 nháy=XANH, 2 nháy=CHÍN, nháy nhanh=lỗi. Task LED hoạt động độc lập.

Giả định nút active-low, LED active-high. Xem mục 7 [README.md](README.md) để biết cách đấu, định dạng file và quy ước thao tác. Code cập nhật chưa được build/flash theo yêu cầu.

### `main/src/inference_pipeline.cpp` và `main/include/inference_pipeline.h`

`infer_latest_wav(path, prediction)` nạp model và kiểm tra tensor, đọc WAV theo lõi 4 giây với ngữ cảnh 0,24 giây hai phía, rồi dùng AudioProcessor → MelExtractor → resize 128 × 128 → lượng tử hóa INT8 → ESP-DL. Ngưỡng đỉnh tính riêng từng cửa sổ; không nạp toàn bộ bản thu vào RAM. Chỉ tính phiếu cho đỉnh thuộc lõi, lọc khoảng cách đỉnh qua biên. Đa số phiếu cho kết quả 0=XANH hoặc 1=CHÍN; không có đỉnh/phiếu hòa trả lỗi. Bộ nhớ model và xử lý được giải phóng sau mỗi lần chạy.

### `main/include/wav_file.h`

Hàm inline ghi/đọc header 44 byte của định dạng ứng dụng: WAV mono PCM16 little-endian 16 kHz. Kiểm tra định dạng và độ dài thực của file trước suy luận. Không hỗ trợ WAV có chunk mở rộng hoặc định dạng tùy ý từ bên ngoài.

### `main/src/firmware.cpp`

Giữ bản code kiểm thử model: kiểm tra PSRAM/tensor, gọi `model->test()`, in cấu trúc model rồi chờ. File này **không nằm trong danh sách `SRCS` hiện tại**, nên không được biên dịch cùng `main.cpp`.

### Các cặp header và source

| Header trong `main/include/` | Source trong `main/src/` | Chức năng |
| --- | --- | --- |
| `ics43434.h` | `ics43434.cpp` | Driver I2S thu PCM mono 24 bit trong `int32_t`, cấu hình chân/kênh và quản lý tài nguyên micro |
| `audio_recorder.h` | `audio_recorder.cpp` | Hai task thu PCM16 16 kHz và ghi WAV liên tục; queue 16 × 1024 mẫu, stop drain và hoàn tất header |
| `audio_processor.h` | `audio_processor.cpp` | Phát hiện đỉnh, quản lý tối đa 32 đoạn cắt dài 0,24 giây |
| `mel_extractor.h` | `mel_extractor.cpp` | Tạo Mel-Spectrogram: FFT 2048, hop 256, 128 dải Mel, miền 50–2000 Hz, tối đa 32 frame |
| `spectrogram_resize.h` | `spectrogram_resize.cpp` | Resize spectrogram sang kích thước đầu ra do phía gọi truyền vào |

Xem mục 6 trong [README.md](README.md) để biết API micro và ví dụ kiểm tra riêng.

### `main/CMakeLists.txt`

Cấu hình riêng cho component ứng dụng `main`:

- `SRCS`: chọn bảy file `src/main.cpp`, `src/inference_pipeline.cpp`, `src/ics43434.cpp`, `src/audio_recorder.cpp`, `src/audio_processor.cpp`, `src/mel_extractor.cpp` và `src/spectrogram_resize.cpp` để biên dịch; không chọn `src/firmware.cpp`.
- `INCLUDE_DIRS "include"`: thêm `main/include/` vào đường dẫn tìm header. Vì vậy source trong `src/` vẫn dùng `#include "ics43434.h"`, không cần đổi thành đường dẫn tương đối.
- `REQUIRES esp-dl esp_driver_i2s esp_driver_gpio esp_driver_spi esp_driver_sdspi sdmmc fatfs`: khai báo ESP-DL, driver I2S/GPIO/SPI và filesystem microSD.
- `target_add_binary_data(...)`: nhúng `models/durian_student_pruned.espdl` dưới dạng dữ liệu nhị phân vào component.

Nhờ bước nhúng này, linker tạo được symbol mà `main/src/inference_pipeline.cpp` sử dụng. Nếu đổi tên model, cần cập nhật cả đường dẫn tại đây và tên symbol trong C++.

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
