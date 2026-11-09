# Duration Edge AI — Phân loại sầu riêng xanh / chín bằng âm thanh

Dự án nghiên cứu của **Nguyễn Văn Hưng**, xây dựng hệ thống phân loại âm thanh gõ vào sầu riêng bằng CNN và triển khai suy luận trên **ESP32-S3**. Luồng phát triển gồm xử lý dữ liệu, huấn luyện Teacher, Knowledge Distillation sang Student, pruning, lượng tử hóa INT8 và tích hợp phần cứng cùng vỏ thiết bị.

Cập nhật tổng quan: **09/11/2026**. Tài liệu này mô tả mã nguồn và các kết quả đã ghi nhận; kết quả kiểm thử model riêng không thay thế kiểm thử toàn bộ thiết bị.

## 1. Trạng thái hiện tại

| Hạng mục | Hiện trạng |
| --- | --- |
| Xử lý dữ liệu Python | Có module đọc âm thanh, làm mịn, tìm đỉnh, cắt đoạn, Mel và thống kê |
| Huấn luyện | Có luồng Teacher → Student → pruning và fine-tune; dùng dữ liệu đã chia và lưu trên đĩa |
| Triển khai model | Xuất trực tiếp `.espdl` INT8 bằng `esp_ppq`; nhúng model vào firmware C++ dùng ESP-DL |
| Board đang cấu hình | ESP32-S3 N16R8: Flash 16 MB, Octal PSRAM 8 MB ở 40 MHz; phân vùng app factory vẫn 1500 KiB |
| Chế độ build hiện tại | `FIRMWARE_MODEL_TEST ON`, chạy WAV nhúng, không khởi tạo micro, SD, nút hoặc LED |
| WAV test mới | `firmware/test/20260717_172242.wav`, mono PCM16 16 kHz, 118784 mẫu, 7,424 giây; đã kiểm tra có tín hiệu biến thiên |
| Kiểm thử trên board | Bản kiểm thử model cũ đã báo `Model test PASSED` trên board Quad PSRAM 2 MB. WAV mới đã suy luận thành công trên N16R8: 5 đoạn, trung bình 343,5638 ms/đoạn, kết quả XANH (4/5 phiếu). WAV cũ không có đỉnh vì toàn bộ mẫu bằng -1 |
| Thu âm / SD / nút / LED | Đã có code ứng dụng chính, chưa có xác nhận kiểm thử đầy đủ trên board trong tài liệu bàn giao |
| Backend | FastAPI phân tích âm thanh và trả waveform, đỉnh, đoạn cắt, Mel, thống kê |
| Frontend | React + TypeScript + Vite + Tailwind; `App.tsx` hiện chỉ hiển thị trang kiểm tra Tailwind, chưa nối API |
| CAD | Có thiết kế vỏ và bố trí linh kiện; file chính trên đĩa khác backup 21 dây đã kiểm chứng. Đọc tài liệu CAD trước khi tiếp tục |

## 2. Luồng hệ thống

```text
Âm thanh gõ → tìm đỉnh → cắt đoạn → Mel-Spectrogram → dữ liệu 128×128
                                                       │
                                                       ▼
                                      Teacher MelCNN → Student MelStudent
                                                       │
                                                       ▼
                                             Pruning → Fine-tune
                                                       │
                                                       ▼
                                      esp_ppq → .espdl INT8 → ESP32-S3
```

Backend phục vụ quan sát và phân tích dữ liệu trên máy tính. Firmware chạy pipeline xử lý và model tại thiết bị; backend hiện chưa cung cấp API dự đoán nhãn bằng CNN.

## 3. Cấu trúc dự án

```text
Duration_edge_ai/
├── config/                     # Cấu hình xử lý dữ liệu và huấn luyện
├── src/
│   ├── processing_data/        # Đọc âm thanh, tìm đỉnh, cắt đoạn và tạo Mel
│   └── data_enrichment/        # Làm giàu dữ liệu
├── models/                     # Mô hình Teacher CNN
│   ├── cnn.py                  # Kiến trúc MelCNN, hàm loss và optimizer
│   ├── load_Data.py            # Nạp, chuẩn hóa, chia và làm giàu dữ liệu
│   ├── DataLoader.py           # Tạo các batch train/validation/test
│   ├── main.py                 # Điều phối huấn luyện và lưu Teacher
│   └── evaluate.py             # Đánh giá mô hình và ma trận nhầm lẫn
├── Knowledge_Distillation/     # Chưng cất kiến thức từ Teacher sang Student
│   ├── cnn_student.py          # Kiến trúc MelStudent
│   ├── loss_optimizer.py       # Loss chưng cất và cấu hình optimizer
│   ├── train_student.py        # Vòng lặp huấn luyện và lưu Student tốt nhất
│   └── main.py                 # Nạp Teacher, huấn luyện và đánh giá Student
├── Pruning_Model/              # Cắt tỉa và lượng tử hóa mô hình
│   ├── cnn_pruned.py           # Cắt channel Conv theo độ lớn L1
│   ├── fine_tuning_model.py    # Fine-tune mô hình sau cắt tỉa
│   ├── main.py                 # Điều phối pruning, fine-tune và đánh giá
│   └── quantize_pruned.py      # Lượng tử hóa INT8, xuất model ESP-DL
├── data/
│   ├── raw_data/               # Âm thanh gốc
│   ├── processed/              # Đặc trưng Mel đã xử lý
│   └── data_train/             # Các tập train/validation/test và ánh xạ nhãn
├── pth/                        # Trọng số mô hình PyTorch
├── espdl/                      # Model đã export cho ESP-DL
├── firmware/
│   ├── main/                   # Code C++ thu âm, xử lý và suy luận
│   ├── models/                 # Model nhúng vào firmware
│   ├── test/                   # Chương trình test và WAV mẫu
│   ├── README.md               # Hướng dẫn build, flash và phần cứng
│   └── README_FILES.md         # Giải thích chi tiết các file firmware
├── backend/                    # API phân tích âm thanh bằng FastAPI
├── ui/                         # Giao diện web React
├── notebook/                   # Notebook và kết quả thử nghiệm
├── 3D/                         # Thiết kế vỏ, linh kiện, STL và các phiên bản CAD
├── freecad_control/            # Công cụ FreeCAD và tài liệu bàn giao CAD
├── Beamer/                     # Thư mục dành cho trình chiếu
├── docs/                       # Tài liệu bổ sung
├── logs/                       # Log phát triển
├── nguyen_van_hung.docx         # Báo cáo Word
├── nguyen_van_hung.pdf          # Báo cáo PDF
└── README.md                   # Tổng quan dự án
```

Chi tiết firmware xem [firmware/README_FILES.md](firmware/README_FILES.md). Khi tiếp tục CAD, đọc [freecad_control/README.md](freecad_control/README.md) để chọn đúng bản làm việc.

## 4. Xử lý âm thanh và mô hình

Các tham số Python nằm trong [config/config_processing_data.py](config/config_processing_data.py); firmware có các hằng tương ứng trong các module C++.

| Tham số | Giá trị |
| --- | --- |
| Tần số lấy mẫu | 16000 Hz, mono |
| Ngưỡng tìm đỉnh | 0,15 × biên độ cực đại |
| Khoảng cách đỉnh tối thiểu | 0,3 giây |
| Đoạn cắt | 0,24 giây, lấy 0,145 giây trước đỉnh |
| Mel | 128 dải, FFT 2048, hop 256, miền 50–2000 Hz |
| Input dùng khi export | `[1, 1, 128, 128]` |
| Output | Hai điểm số cho hai lớp |

Pipeline Python trong [src/processing_data/pipeline.py](src/processing_data/pipeline.py) dùng làm mịn rồi `scipy.signal.find_peaks`. Firmware tìm cực đại cục bộ trên trị tuyệt đối PCM theo cửa sổ lõi 4 giây, có ngữ cảnh 0,24 giây hai phía; chỉ bỏ phiếu cho đỉnh thuộc lõi và lọc khoảng cách qua biên. Hai cách tìm đỉnh chưa được xác nhận tương đương.

Teacher trong [models/cnn.py](models/cnn.py) có bốn block Conv/BatchNorm/ReLU/MaxPool với số kênh 32/64/128/256 và classifier 512 → 256 → 2. Student trong [Knowledge_Distillation/cnn_student.py](Knowledge_Distillation/cnn_student.py) dùng số kênh 24/48/96/192, global average pooling và classifier 128 → 2. Script pruning cắt channel theo độ lớn L1, mặc định 20% mỗi lớp Conv, rồi fine-tune.

Cấu hình học nằm trong [config/config_model_cnn.py](config/config_model_cnn.py). Luồng chuẩn bị dữ liệu chia train/validation/test theo tỷ lệ 70/15/15 trước augmentation; chỉ tăng cường tập train. Các đoạn từ cùng bản thu vẫn cần được kiểm soát khi đánh giá để tránh việc chúng xuất hiện ở nhiều tập.

### Các điểm cần đối chiếu trước khi kết luận chất lượng model

- **Ánh xạ nhãn:** firmware hiện gán `0=XANH`, `1=CHÍN`. Code chuẩn bị dữ liệu dùng `LabelEncoder`, thường sắp thứ tự `chin`, `xanh`. Cần đối chiếu `data/data_train/classes.npy` của đúng checkpoint đã export; chưa xác nhận mapping của model nhúng hiện tại.
- **Chuẩn hóa:** code nạp dữ liệu Python hiện dùng min/max toàn bộ dữ liệu nạp, còn firmware đổi Mel theo `clamp((dB + 80) / 80, 0, 1)`. Cần kiểm tra lại với quy trình tạo bộ calibration/checkpoint thực tế.
- **Điểm INT8:** là điểm số model, không phải xác suất. Firmware lấy lớp có điểm cao hơn cho từng đoạn, rồi bỏ phiếu đa số. Không có đỉnh hoặc phiếu hòa thì không trả nhãn.
- **Kết quả đánh giá:** cần gắn accuracy/F1 với checkpoint, tập test và mapping cụ thể. README này không coi các con số 94–98% trong tài liệu lịch sử là chất lượng đã xác nhận của firmware hiện tại.

## 5. Chạy xử lý và huấn luyện trên máy tính

Chạy các lệnh từ gốc dự án. Môi trường đã dùng có tên Conda `Duration`; tùy máy cần chuẩn bị môi trường tương ứng. Nhóm thư viện chính gồm `numpy`, `scipy`, `librosa`, `torch`, `scikit-learn`, `scikit-image`, `matplotlib`, `seaborn`; export ESP-DL cần thêm `esp_ppq`. Dự án chưa có file requirements khóa phiên bản chung.

```bash
conda activate Duration
python -m src.processing_data.pipeline
```

Điểm chạy pipeline trên hiện thử file đầu tiên trong `data/raw_data/dau_nhua/v1c1`; nếu cần xử lý một file cụ thể, gọi `Pipeline().analyze_file(filepath)` từ Python. Notebook hỗ trợ các bước thử nghiệm và tạo Mel. Kiểm tra đường dẫn trong cấu hình trước khi xử lý dữ liệu.

Teacher đọc Mel từ `data/processed/data_lan7_no_smooth/{xanh,chin}`, chuẩn bị dữ liệu và lưu checkpoint. Các bước tiếp theo dùng bộ dữ liệu đã lưu:

```bash
python -m models.main
python -m Knowledge_Distillation.main
python -m Pruning_Model.main
```

| Bước | Checkpoint đầu ra mặc định |
| --- | --- |
| Teacher | `pth/best_model.pth` |
| Student KD | `pth/model_Student.pth` |
| Pruning + fine-tune | `pth/best_pruned_student.pth` |

Chỉ đánh giá Teacher với dữ liệu test đã lưu, không chia lại dữ liệu:

```bash
python -m models.main --evaluate --model-path pth/best_model.pth
```

## 6. Xuất model và chạy firmware

Hướng dẫn đầy đủ về môi trường ESP-IDF, cấu hình, lỗi và nạp model nằm trong [firmware/README.md](firmware/README.md). Bản đồ chức năng C++ nằm trong [firmware/README_FILES.md](firmware/README_FILES.md).

### Export INT8

[Pruning_Model/quantize_pruned.py](Pruning_Model/quantize_pruned.py) đọc checkpoint đã pruning và `data/data_train/X_train.npy` dạng `[N, 1, 128, 128]`, chạy calibration trên CPU cho ESP32-S3 (`w8a8`, batch 8, tối đa 32 bước), có export giá trị test.

```bash
python Pruning_Model/quantize_pruned.py
cp espdl/durian_student_pruned.espdl firmware/models/durian_student_pruned.espdl
sha256sum espdl/durian_student_pruned.espdl firmware/models/durian_student_pruned.espdl
```

Model trong `firmware/models/` được nhúng vào `firmware.bin` và flash cùng code. Chỉ thay bản ở `espdl/` chưa đổi model trên board; không flash trực tiếp checkpoint `.pth`.

### Build và flash

Công cụ đã dùng: ESP-IDF 5.3.6, target `esp32s3`; dependency lock ghi ESP-DL 3.3.14. Manifest hiện khai báo ESP-DL `"*"`, nên cần lưu ý phiên bản khi resolve lại dependency.

Ví dụ môi trường trên máy hiện tại, bắt đầu từ gốc dự án:

```bash
conda activate Duration
export IDF_PYTHON_ENV_PATH=/home/nghung/.espressif/python_env/idf5.3_py3.10_env
source /home/nghung/esp-idf/export.sh
cd firmware
idf.py reconfigure
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

Thay đường dẫn môi trường và cổng theo máy. Thoát monitor bằng `Ctrl+]`. Khi build phải kiểm tra firmware có vừa phân vùng factory 1500 KiB; Flash 16 MB không tự làm phân vùng app lớn lên. Cấu hình Octal hiện tại dành cho N16R8, khác board Quad cũ.

### Hai chế độ ứng dụng

Chọn trong [firmware/main/CMakeLists.txt](firmware/main/CMakeLists.txt):

| Giá trị | Điểm vào và hoạt động |
| --- | --- |
| `FIRMWARE_MODEL_TEST ON` | `test/model_only.cpp`: đọc `20260717_172242.wav` nhúng trong flash, chạy pipeline chung, in cấu trúc model, tensor, đỉnh, thời gian, điểm số và kết quả |
| `FIRMWARE_MODEL_TEST OFF` | `main/src/main.cpp`: thu micro ICS-43434 xuống SD theo nút bấm, suy luận file hoàn tất gần nhất, hiển thị trạng thái bằng LED |

Sau khi đổi chế độ hoặc WAV, reconfigure/build/flash lại. Bản test chạy một lần sau reset. File WAV mới đã kiểm tra trên máy có biên độ từ -31341 đến 31222 và có cực đại cục bộ ở cả hai cửa sổ; log board đã xác nhận pipeline trả kết quả XANH; độ chính xác nhãn vẫn cần kiểm chứng với nhãn thực và mapping.

### Chỉ số triển khai thực tế — 09/11/2026

Nguồn: [log suy luận đầy đủ](firmware/build/log/idf_py_stdout_output_20020) và [log build/flash](firmware/build/log/idf_py_stdout_output_76056). Đo ở chế độ WAV nhúng `FIRMWARE_MODEL_TEST ON`, ESP32-S3 CPU **160 MHz**, Flash DIO **16 MB**, Octal PSRAM **8 MB / 40 MHz**, ESP-IDF **5.3.6**. Đây là một lượt chạy WAV với 5 đoạn cắt, chưa phải benchmark trên nhiều file hoặc nhiều phiên chạy.

| Nhóm | Chỉ số | Kết quả / phạm vi |
| --- | --- | --- |
| Đầu vào | WAV | `20260717_172242.wav`, mono PCM16 16 kHz, 118784 mẫu, 7,424 giây; file 237612 byte |
| Đầu vào | Số đoạn suy luận | 5 đỉnh: 3 ở cửa sổ đầu, 2 ở cửa sổ sau; mỗi đoạn 3840 mẫu (0,24 giây) |
| Inference latency | Trung bình chạy model | **343,5638 ms/đoạn**, trung bình 5 lần gọi `model->run()` |
| Inference latency | Nhỏ nhất / lớn nhất | **343,304 / 344,445 ms/đoạn** |
| Inference latency | Từng lần chạy | 344,445; 343,353; 343,325; 343,304; 343,392 ms |
| Pipeline | Xử lý WAV tới kết quả | Khoảng **5,62 giây**, ước lượng từ timestamp log WAV 1364 ms tới kết quả 6984 ms; gồm nạp model, tiền xử lý, suy luận và log, không tính thời gian boot |
| Tiền xử lý | Tạo Mel | Khoảng **650–660 ms/đoạn**, suy ra từ khoảng giữa log cửa sổ/đỉnh trước và log Mel; chưa đo riêng bằng timer nên không coi là số đo chính xác của hàm Mel |
| Memory usage | PSRAM được nhận | **8 MB**, `SPI SRAM memory test OK` |
| Memory usage | PSRAM trống trước nạp model | **8385720 byte**; khối trống liên tục lớn nhất **8257536 byte** |
| Memory usage | RAM/PSRAM dùng khi suy luận | **Chưa đo** mức dùng thực tế và mức đỉnh; số PSRAM trống trước nạp model không đại diện bộ nhớ tiêu thụ của model |
| Flash usage | Firmware ứng dụng | **1510144 byte = 1474,75 KiB** (`0x170b00`), gồm code, model và WAV test |
| Flash usage | Phân vùng app factory | **1536000 byte = 1500 KiB** (`0x177000`) |
| Flash usage | Phân vùng app còn trống | **25856 byte = 25,25 KiB**, công cụ build báo 2% trống; đây là phần trống của phân vùng app, không phải toàn Flash 16 MB |
| Hardware deployment | Kết quả chạy thực tế | Đã build, flash và suy luận WAV nhúng thành công trên ESP32-S3; **4 phiếu XANH, 1 phiếu CHÍN**, `FINAL RESULT: XANH (class 0)` |
| Chất lượng phân loại | Accuracy/F1 trên board | **Chưa xác định**; cần nhãn thực, đối chiếu mapping và tập kiểm thử độc lập. Tỷ lệ phiếu 4/5 không phải accuracy hoặc xác suất 80% |

Tensor trong log ESP-DL: input INT8 `[1, 128, 128, 1]` (NHWC), output INT8 `[1, 2]`. Điểm của 5 đoạn lần lượt là `(8, -11)`, `(6, -9)`, `(13, -16)`, `(-5, 1)`, `(19, -22)`; nhãn trên dùng mapping firmware hiện tại `0=XANH`, `1=CHÍN`.

Model đã qua chưng cất kiến thức, pruning và INT8; các số trên ghi nhận hiệu năng hiện tại, chưa xác nhận pipeline đã tối ưu. Chưa có phép đo điện năng hoặc kết quả CPU 240 MHz. WAV test chiếm Flash và sẽ không được nhúng khi chọn ứng dụng chính (`OFF`). Log còn cảnh báo căn địa chỉ model 16 byte; phiên chạy vẫn hoàn tất. Monitor có báo mất kết nối USB sau phiên chạy, không có bằng chứng crash ứng dụng trong log suy luận đầy đủ. Log monitor mới hơn `idf_py_stdout_output_76241` chỉ lưu một phần nên không dùng để tính trung bình hoặc kết luận kết quả cuối.

### GPIO của ứng dụng thu âm

| Thành phần | Tín hiệu / GPIO |
| --- | --- |
| microSD SPI | CS13 / SCK12 / MOSI11 / MISO10 |
| ICS-43434 | SD4 / SCK5 / WS6; L/R nối GND |
| Nút 1 / 2 / 3 | CHÍN GPIO1 / XANH GPIO2 / suy luận GPIO3 |
| LED | GPIO7 |

Nút active-low với pull-up nội, LED active-high. Bấm nút nhãn để thu, bấm lại chính nút đó để dừng. Nút 3 suy luận WAV gần nhất khi nghỉ. WAV mono PCM16 16 kHz được ghi vào `/sdcard/CHIN/` hoặc `/sdcard/XANH/`; file chỉ chuyển từ `.TMP` sang `.WAV` sau khi hoàn tất thành công. Tên thư mục là nhãn lúc thu.

LED sáng liên tục khi thu, nháy 0,5 giây khi suy luận; một nháy ngắn lặp lại là XANH, hai nháy là CHÍN, nháy nhanh là lỗi. Chi tiết thao tác, dây và các giới hạn nằm trong README firmware.

## 7. Backend và giao diện web

Backend dùng FastAPI và pipeline Python. Chuẩn bị thêm các gói `fastapi`, `uvicorn`, `python-multipart` trong môi trường có thư viện xử lý âm thanh. Từ gốc dự án:

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs tại `http://127.0.0.1:8000/docs`.

| Endpoint | Chức năng |
| --- | --- |
| `GET /health` | Kiểm tra dịch vụ |
| `POST /api/analyze` | Upload âm thanh, nhận waveform, đỉnh và thống kê đoạn cắt |
| `GET /api/segment/{stored_name}/{segment_index}` | Lấy waveform, Mel và thống kê của một đoạn |

API nhận WAV/MP3/M4A/FLAC/OGG, giới hạn file 50 MB; file upload lưu tại `backend/data/uploads/`. Khả năng giải mã từng định dạng phụ thuộc môi trường âm thanh cài trên máy.

Chạy frontend ở terminal khác, bắt đầu từ gốc dự án:

```bash
cd ui
npm install
npm run dev
```

Frontend hiện là khung kiểm tra giao diện, chưa tích hợp các endpoint trên. `docker-compose.yml` đang trống, chưa có quy trình chạy toàn hệ thống bằng Compose.

## 8. CAD và tài liệu thiết kế

Đọc [freecad_control/README.md](freecad_control/README.md) trước khi tiếp tục FreeCAD. Tài liệu này tự chứa bản chính, backup, cách kết nối, yêu cầu thiết kế và các vấn đề chưa xác nhận; các bản CAD/STL nằm trong `3D/`.

Theo bàn giao 06/11/2026, file `D36_Printed_Retention_35x25x6.FCStd` hiện trên đĩa có 43 objects, khác backup 55 objects với 21 dây đã kiểm chứng. Thông số vỏ Ø36×146 mm và kết quả kiểm tra đi dây thuộc bản backup đã xác nhận; không suy rộng sang file chính hiện tại. Cần chốt bản làm việc trước khi tiếp tục sửa CAD, không tự khôi phục hoặc chạy lại script lịch sử.

Lịch sử thiết kế và dọn thư mục ở [freecad_control/HISTORY.md](freecad_control/HISTORY.md) và [freecad_control/CLEANUP_PLAN.md](freecad_control/CLEANUP_PLAN.md). File [docs/PROJECT_OVERVIEW_BEFORE_CAD.md](docs/PROJECT_OVERVIEW_BEFORE_CAD.md) là bản tổng quan lịch sử trước CAD, có thể khác cấu trúc và trạng thái hiện nay.

## 9. Các việc cần xác nhận tiếp

- Đo thêm RAM/PSRAM ở các mốc nạp model và xử lý, mức đỉnh bộ nhớ, cùng thời gian từng bước bằng timer; lặp lại benchmark trên nhiều WAV có nhãn.
- Đối chiếu mapping nhãn, chuẩn hóa và Mel giữa dữ liệu huấn luyện/calibration với firmware.
- Đánh giá model INT8 trên tập test độc lập; ghi checkpoint, dữ liệu và cấu hình đi kèm kết quả.
- Kiểm thử thu âm, chất lượng WAV, microSD, nút, LED và suy luận sau reboot trên board thực.
- Xác nhận bản CAD tiếp tục sử dụng, thông số linh kiện thực và khả năng lắp/in trước khi hoàn thiện vỏ.
