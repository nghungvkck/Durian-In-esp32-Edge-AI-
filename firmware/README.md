# Nạp firmware và model lên ESP32-S3

Tài liệu ghi lại cấu hình đã chạy thành công, quy trình nạp và các lỗi đã xử lý ngày 31/10/2026.

## 1. Phần cứng và kết quả đã xác nhận

Đã đọc trực tiếp thông tin board qua `/dev/ttyACM0` bằng esptool:

```text
Chip is ESP32-S3 (QFN56) (revision v0.2)
Embedded Flash 4MB (XMC)
Embedded PSRAM 2MB (AP_3v3)
USB mode: USB-Serial/JTAG
```

Cấu hình firmware hiện tại:

- ESP-IDF 5.3.6, target `esp32s3`.
- PSRAM Quad, 40 MHz, khởi tạo và kiểm tra bộ nhớ lúc boot, đưa vào heap.
- Flash trong image header: 2 MB; flash vật lý: 4 MB. Firmware hiện dùng được trong phạm vi 2 MB.
- Bảng phân vùng `partitions_singleapp_large.csv`, phân vùng `factory` bắt đầu tại `0x10000`, dung lượng 1500 KiB (`0x177000`).
- ESP-DL đã resolve phiên bản 3.3.14 trong lần build thành công. `main/idf_component.yml` hiện khai báo `"*"`, nên phiên bản có thể thay đổi khi resolve lại dependency.

Sau khi bật PSRAM, build và nạp lên board, log xác nhận:

```text
esp_psram: Found 2MB PSRAM device
esp_psram: Speed: 40MHz
esp_psram: SPI SRAM memory test OK
esp_psram: Adding pool of 2048K of PSRAM memory to heap allocator
DURIAN_AI: PSRAM free: 2094528 bytes, largest block: 2064384 bytes
DURIAN_AI: Model loaded
dl::Model: Test Pass!
DURIAN_AI: Model test PASSED
```

Đây là bài test với dữ liệu kiểm thử được nhúng trong model khi export. Firmware hiện chưa thu âm micro hoặc chạy phân loại âm thanh trực tiếp; `app_main()` nạp model, chạy `model->test()`, in cấu trúc rồi chờ.

## 2. Các file chính và cách model được nạp

| File | Vai trò |
| --- | --- |
| `../Pruning_Model/quantize_pruned.py` | Chuyển checkpoint PyTorch đã pruning sang model ESP-DL INT8 |
| `../pth/best_pruned_student.pth` | Trọng số đầu vào cho quantization |
| `../data/data_train/X_train.npy` | Dữ liệu calibration, dạng `[N, 1, 128, 128]` |
| `../espdl/durian_student_pruned.espdl` | Model đầu ra của script quantization |
| `models/durian_student_pruned.espdl` | Bản model thực sự được firmware nhúng vào binary |
| `main/CMakeLists.txt` | Khai báo source và nhúng model |
| `main/firmware.cpp` | Nạp và kiểm thử model trên board |
| `sdkconfig` | Cấu hình đang dùng cho build hiện tại |
| `sdkconfig.defaults` | Cấu hình mặc định PSRAM và phân vùng app cho lần tạo cấu hình mới |

**Model được nhúng vào `firmware.bin`, rồi nạp cùng code bằng `idf.py flash`. Không cần nạp riêng file `.pth` hoặc `.espdl` bằng một lệnh flash khác.**

Khi có model mới, phải copy sang `firmware/models/` rồi build và flash lại. Chỉ cập nhật file trong thư mục `espdl/` sẽ chưa thay đổi model trên board.

## 3. Quy trình cụ thể

### Bước 1 — Chuẩn bị model

Nếu chỉ nạp lại code và model đã có tại `firmware/models/durian_student_pruned.espdl`, có thể bỏ qua bước quantization và copy.

Nếu cần tạo model mới, chạy từ thư mục gốc dự án trong môi trường có `torch`, `numpy` và `esp_ppq`:

```bash
cd /mnt/d/Hoc_tap_Sinh_Vien/Kien_thu_AI/Project/Duration_edge_ai
conda activate Duration
python Pruning_Model/quantize_pruned.py
```

Script dùng CPU, target ESP32-S3, lượng tử hóa `w8a8`, calibration batch 8 và tối đa 32 bước. Script bật `export_test_values=True` để phục vụ `model->test()` trên board.

Khi script báo export thành công, copy model sang thư mục firmware:

```bash
cp espdl/durian_student_pruned.espdl firmware/models/durian_student_pruned.espdl
sha256sum espdl/durian_student_pruned.espdl firmware/models/durian_student_pruned.espdl
```

Hai mã SHA256 phải giống nhau. Giữ tên `durian_student_pruned.espdl` để khớp CMake và symbol trong C++.

### Bước 2 — Mở môi trường ESP-IDF

Các đường dẫn bên dưới là môi trường đã dùng thành công trên máy hiện tại:

```bash
cd /mnt/d/Hoc_tap_Sinh_Vien/Kien_thu_AI/Project/Duration_edge_ai/firmware
conda activate Duration
export IDF_PYTHON_ENV_PATH=/home/nghung/.espressif/python_env/idf5.3_py3.10_env
source /home/nghung/esp-idf/export.sh
idf.py --version
```

Máy khác cần thay đường dẫn môi trường Python và ESP-IDF tương ứng. Dùng cùng môi trường Python cho các lần configure/build của một thư mục `build`.

### Bước 3 — Kiểm tra target và cấu hình bộ nhớ

Project hiện đã cấu hình target `esp32s3`; không cần chạy `set-target` mỗi lần nạp. Với một bản checkout mới chưa có cấu hình, chạy:

```bash
idf.py set-target esp32s3
```

Các thiết lập cần có trong `sdkconfig`:

```text
CONFIG_IDF_TARGET="esp32s3"
CONFIG_SPIRAM=y
CONFIG_SPIRAM_MODE_QUAD=y
CONFIG_SPIRAM_TYPE_AUTO=y
CONFIG_SPIRAM_SPEED_40M=y
CONFIG_SPIRAM_BOOT_INIT=y
CONFIG_SPIRAM_USE_MALLOC=y
CONFIG_SPIRAM_MEMTEST=y
CONFIG_PARTITION_TABLE_SINGLE_APP_LARGE=y
CONFIG_PARTITION_TABLE_FILENAME="partitions_singleapp_large.csv"
```

`sdkconfig.defaults` đã lưu các thiết lập PSRAM và phân vùng app. File này cung cấp giá trị mặc định khi tạo cấu hình; không tự ghi đè các giá trị đã có trong `sdkconfig`. Nếu cấu hình cũ vẫn tắt PSRAM, mở `idf.py menuconfig`, bật trong `Component config → ESP PSRAM`, chọn Quad, 40 MHz và cho phép cấp phát qua malloc; chọn phân vùng single factory app lớn trong `Partition Table`.

Trong `main/firmware.cpp`, model được tạo với `max_internal_size = 0`:

```cpp
dl::Model *model = new dl::Model(
    reinterpret_cast<const char *>(model_espdl),
    fbs::MODEL_LOCATION_IN_FLASH_RODATA,
    0
);
```

Với `CONFIG_SPIRAM=y`, bộ quản lý bộ nhớ Greedy của phiên bản ESP-DL hiện tại đặt vùng tensor vào PSRAM khi giới hạn RAM nội bằng 0. Code cũng kiểm tra PSRAM và tensor input/output trước khi gọi `test()`.

### Bước 4 — Build

```bash
idf.py build
```

Chỉ tiếp tục khi có `Project build complete` và kiểm tra dung lượng phân vùng không báo lỗi. Bản đã kiểm chứng có `firmware.bin` dung lượng `0x137b80` byte, phân vùng app còn khoảng 17%; con số sẽ thay đổi khi sửa code/model.

Đổi cấu hình PSRAM có thể khiến ESP-IDF biên dịch lại toàn bộ, mất nhiều thời gian hơn build thông thường.

### Bước 5 — Kết nối board và nạp

Kết nối board với máy; trong môi trường Linux/WSL đang chạy ESP-IDF phải nhìn thấy cổng USB:

```bash
ls -l /dev/ttyACM0
```

Đóng monitor hoặc chương trình khác đang giữ cổng, rồi chạy:

```bash
idf.py -p /dev/ttyACM0 flash monitor
```

Lệnh này nạp bootloader, bảng phân vùng và firmware chứa model, sau đó mở log. Thay tên cổng nếu board được nhận ở cổng khác. Thoát monitor bằng `Ctrl+]`.

### Bước 6 — Xác nhận trên board

Log phải có các dòng:

```text
Found 2MB PSRAM device
SPI SRAM memory test OK
PSRAM free: ...
Model loaded
Model test PASSED
```

Nếu chưa có `Model test PASSED`, lưu log từ lúc boot đến lỗi để chẩn đoán. Build thành công chưa đủ để xác nhận model chạy được trên phần cứng.

### Các lần cập nhật tiếp theo

- Chỉ sửa C++: `idf.py build`, rồi `idf.py -p /dev/ttyACM0 flash monitor`.
- Thay model: export `.espdl`, copy sang `firmware/models/`, rồi build và flash như trên.
- Không cần `fullclean` mỗi lần cập nhật. CMake đã theo dõi file model qua `target_add_binary_data`.

## 4. Lỗi đã gặp và cách xử lý

### 4.1. Linker không tìm thấy model nhúng

```text
undefined reference to `_binary_durian_student_pruned_espdl_start'
```

Nguyên nhân: C++ đã khai báo symbol nhưng `main/CMakeLists.txt` chưa nhúng file model. Đã thêm sau `idf_component_register(...)`:

```cmake
target_add_binary_data(${COMPONENT_LIB}
    "${CMAKE_CURRENT_LIST_DIR}/../models/durian_student_pruned.espdl"
    BINARY
)
```

Symbol tương ứng trong C++:

```cpp
extern const uint8_t model_espdl[] asm("_binary_durian_student_pruned_espdl_start");
```

### 4.2. Phân vùng app quá nhỏ

```text
app partition is too small for binary firmware.bin
factory ... size 0x100000 (overflow 0x35660)
```

Nguyên nhân: firmware kèm model vượt phân vùng app mặc định 1 MiB. Đã chuyển sang `CONFIG_PARTITION_TABLE_SINGLE_APP_LARGE=y`, dùng phân vùng factory 1500 KiB. Sau khi đổi phải flash lại bảng phân vùng bằng `idf.py flash`.

### 4.3. Thiếu RAM nội, sau đó crash khi test model

```text
Input cap=0x804 can not callocate with MALLOC_CAP_SIMD
Failed to alloc 396.00KB internal RAM, largest available internal RAM block size 128.00KB
MemoryManagerGreedy: root_alloc failed
Guru Meditation Error: ... LoadProhibited
EXCVADDR: 0x00000004
```

Nguyên nhân: PSRAM bị tắt (`# CONFIG_SPIRAM is not set`), nên ESP-DL cố cấp phát vùng tensor 396 KiB trong RAM nội. Vùng liên tục lớn nhất còn lại chỉ 128 KiB. Code cũ vẫn in `Model loaded` và gọi `model->test()` sau khi cấp phát thất bại, dẫn tới truy cập con trỏ null.

Cách sửa đã kiểm chứng:

1. Đọc thông tin chip và xác nhận có PSRAM tích hợp 2 MB.
2. Bật Quad PSRAM 40 MHz, khởi tạo lúc boot, kiểm tra bộ nhớ và thêm vào heap.
3. Dùng `max_internal_size = 0` để vùng tensor được cấp phát trong PSRAM.
4. Kiểm tra PSRAM và tensor input/output trước khi chạy test; nếu thất bại thì ghi lỗi và dừng khởi tạo.
5. Build, flash lại và xác nhận `Model test PASSED` trên board.

Dung lượng file model trong flash khác với RAM cần lúc chạy: model INT8 nhỏ vẫn cần RAM cho các tensor trung gian.

### 4.4. Môi trường Python không khớp với build cũ

```text
idf5.3_py3.12_env ... currently active
project was configured with ... idf5.3_py3.10_env
```

Đã xử lý bằng cách đặt `IDF_PYTHON_ENV_PATH` về môi trường Python 3.10 ở bước 2 trước khi source ESP-IDF và build. Nếu chủ động chuyển môi trường Python, cần tạo lại build bằng `idf.py fullclean` rồi `idf.py build`; kiểm tra lại cấu hình trước khi flash.

## 5. Cảnh báo còn tồn tại

```text
The address of fbs model in flash is not aligned with 16 bytes.
```

Cảnh báo căn địa chỉ model này vẫn xuất hiện trong bản đã test thành công; chưa xử lý trong lần sửa PSRAM. Đây không phải nguyên nhân lỗi cấp phát 396 KiB nói trên.

```text
Detected size(4096k) larger than the size in the binary image header(2048k).
```

Flash vật lý 4 MB nhưng image đang cấu hình 2 MB. Bản hiện tại vừa trong 2 MB và đã chạy test thành công; chưa đổi cấu hình để sử dụng toàn bộ 4 MB.
