# 🥭 Duration Edge AI — Phân Loại Quả Xanh / Chín Trên Thiết Bị Nhúng

> **Dự án nghiên cứu sinh viên** — Xây dựng hệ thống phân loại âm thanh gõ vào trái cây (xanh / chín) chạy trực tiếp trên chip **ESP32-S3**, sử dụng mô hình AI nhẹ (CNN + Knowledge Distillation + Pruning).

---

## 🎯 Bài Toán

Khi gõ vào một trái cây, âm thanh phát ra sẽ khác nhau tùy theo độ chín:
- **Xanh** → âm thanh cao, vang, cứng
- **Chín** → âm thanh thấp, đục, mềm

Dự án này thu thập âm thanh → xử lý → trích xuất đặc trưng Mel-Spectrogram → đưa vào mô hình CNN để phân loại, và triển khai kết quả lên vi điều khiển **ESP32-S3**.

---

## 🏗️ Kiến Trúc Hệ Thống

```
[Âm thanh thô] 
      │
      ▼
[Xử lý tín hiệu]  ← src/processing_data/
  ├─ Load audio
  ├─ Làm mịn (Smooth)
  ├─ Phát hiện đỉnh (Peak Detection)
  ├─ Cắt đoạn âm thanh (Segmentation)
  └─ Trích xuất Mel-Spectrogram
      │
      ▼
[Huấn luyện mô hình]  ← models/ + notebook/
  ├─ Teacher: MelCNN (lớn, chính xác)
  ├─ Student: MelStudent (nhỏ, nhanh)
  └─ Pruning + Quantization (INT8)
      │
      ▼
[Xuất ONNX]  ← ONNX/
      │
      ▼
[Triển khai ESP32-S3]  ← firmware/
```

---

## 📁 Cấu Trúc Thư Mục

```
Duration_edge_ai/
│
├── 📂 config/                         # Các thông số cấu hình
│   ├── config_processing_data.py      # Cấu hình xử lý âm thanh (SR, Mel, Smooth...)
│   └── config_model_cnn.py            # Cấu hình mô hình CNN (augmentation...)
│
├── 📂 src/                            # Mã nguồn chính
│   └── processing_data/               # Pipeline xử lý dữ liệu âm thanh
│       ├── pipeline.py                # Điều phối toàn bộ pipeline
│       └── core/
│           ├── audio_loader.py        # Tải file âm thanh (wav, mp3, flac...)
│           ├── smoother.py            # Làm mịn tín hiệu
│           ├── peak_detector.py       # Phát hiện đỉnh âm thanh
│           ├── segmenter.py           # Cắt đoạn xung quanh đỉnh
│           └── features/
│               ├── mel.py             # Trích xuất Mel-Spectrogram
│               └── stats.py           # Thống kê tín hiệu
│
├── 📂 models/                         # Định nghĩa mô hình
│   ├── cnn.py                         # Teacher model: MelCNN (256 filter)
│   ├── load_Data.py                   # Load & augment dữ liệu cho training
│   └── DataLoader.py
│
├── 📂 ONNX/                           # Xuất mô hình sang ONNX
│   ├── export_onnx.py                 # Script xuất ONNX từ PyTorch
│   ├── test.py                        # Test mô hình ONNX
│   ├── model.onnx                     # Mô hình đã xuất
│   └── calib_data/                    # Dữ liệu calibration cho quantization
│
├── 📂 firmware/                       # Code cho ESP32-S3
│   ├── main/firmware.c                # Firmware C (ESP-IDF)
│   ├── CMakeLists.txt
│   ├── sdkconfig
│   └── build/                         # Build artifacts (firmware.bin, .elf...)
│
├── 📂 notebook/                       # Jupyter notebooks & model checkpoints
│   ├── eda.ipynb                      # Phân tích dữ liệu (EDA)
│   ├── processing_dataMel.ipynb       # Xử lý & tạo Mel-Spectrogram
│   ├── model_94/                      # Model đạt 94% accuracy
│   ├── model_98/                      # Model đạt 98% accuracy
│   └── *.png                          # Biểu đồ phân tích
│
├── 📂 ui/                             # Giao diện web (React + TypeScript)
│   └── src/App.tsx
│
├── 📂 data/                           # Dữ liệu (không commit lên git)
│   ├── raw_data/                      # Âm thanh thô
│   └── processed/                     # Mel-Spectrogram đã xử lý (.npy)
│
└── 📂 logs/                           # Log backend/frontend/firmware
```

---

## ⚙️ Pipeline Xử Lý Âm Thanh

Toàn bộ pipeline nằm trong [`src/processing_data/pipeline.py`](file:///mnt/d/Hoc_tap_Sinh_Vien/Kien_thu_AI/Project/Duration_edge_ai/src/processing_data/pipeline.py):

```
Bước 1: Load audio        → AudioLoader  (wav/mp3/flac...)
Bước 2: Làm mịn           → Smoother     (abs → Gaussian → Savitzky-Golay)
Bước 3: Phát hiện đỉnh    → PeakDetector (scipy.signal.find_peaks)
Bước 4: Cắt đoạn          → Segmenter    (0.24s mỗi đoạn, lấy 0.145s trước đỉnh)
Bước 5: Trích xuất Mel    → MelExtractor (128 mel bands, 50–2000 Hz)
```

### Giải thích từng bước

| Bước | Mô tả |
|------|--------|
| **Load** | Tải file âm thanh, tự động convert về mono |
| **Smooth** | Lấy giá trị tuyệt đối → giảm nhiễu Gaussian → làm mịn Savitzky-Golay → ra đường bao tín hiệu |
| **Peak Detection** | Tìm các đỉnh có biên độ ≥ 15% max, cách nhau ít nhất 0.3s |
| **Segmentation** | Cắt đoạn 240ms xung quanh mỗi đỉnh (lấy 145ms trước đỉnh) |
| **Mel-Spectrogram** | Chuyển đoạn âm thanh thành ảnh (128 × N_frames) dạng dB |

---

## 🧠 Mô Hình AI

### Teacher Model — `MelCNN`

```
Input [B, 1, 128, 128]
  → Conv2d(1→32) → BN → ReLU → MaxPool
  → Conv2d(32→64) → BN → ReLU → MaxPool
  → Conv2d(64→128) → BN → ReLU → MaxPool
  → Conv2d(128→256) → BN → ReLU → MaxPool
  → Flatten → Linear(16384→512) → Linear(512→256) → Linear(256→2)
Output [B, 2]  (logits cho: xanh / chín)
```

### Student Model — `MelStudent` (dành cho ESP32)

Mô hình nhỏ hơn, dùng **Knowledge Distillation** từ Teacher:

```
Input [B, 1, 128, 16]  ← time_frames rút ngắn
  → Conv2d(1→24) → ... → Conv2d(96→192)
  → AdaptiveAvgPool2d(1,1)
  → Linear(192→128) → Linear(128→2)
```

### Tối Ưu Hóa

| Phương pháp | Mô tả | Kết quả |
|---|---|---|
| **Knowledge Distillation** | Student học từ Teacher's soft labels | Giữ accuracy cao |
| **Pruning** | Cắt bỏ 20% filter ít quan trọng (1→19, 24→38...) | Giảm params |
| **INT8 Quantization** | Chuyển float32 → int8 | ÷4 bộ nhớ, nhanh hơn trên ESP32 |

**Kết quả đạt được:** 94–98% accuracy với mô hình rất nhỏ phù hợp ESP32-S3.

---

## 🔧 Cấu Hình

### `config/config_processing_data.py`

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `SAMPLE_RATE` | 16000 Hz | Tần số lấy mẫu |
| `PEAK_THRESHOLD_RATIO` | 0.15 | Ngưỡng phát hiện đỉnh = 15% × max |
| `PEAK_MIN_DISTANCE_SEC` | 0.3 s | Khoảng cách tối thiểu giữa 2 đỉnh |
| `SEGMENT_DURATION_SEC` | 0.24 s | Độ dài mỗi đoạn âm thanh |
| `MEL_N_MELS` | 128 | Số dải mel |
| `MEL_FMIN / FMAX` | 50–2000 Hz | Dải tần phân tích |

### `config/config_model_cnn.py`

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `N_MELS` | 128 | Kích thước ảnh mel |
| `NOISE_FACTOR` | 0.005 | Hệ số nhiễu augmentation |
| `SHIFT_MAX` | 10 | Dịch chuyển thời gian tối đa |
| `FACTOR_RANGE` | (0.8, 1.2) | Điều chỉnh độ sáng spectrogram |

---

## 🚀 Cách Chạy

### 1. Cài đặt môi trường Python

```bash
pip install librosa scipy numpy torch torchvision scikit-learn scikit-image onnx matplotlib seaborn
```

### 2. Xử lý dữ liệu âm thanh

```bash
# Test pipeline với 1 file
python src/processing_data/pipeline.py
```

### 3. Xuất mô hình sang ONNX

```bash
cd ONNX
python export_onnx.py
```

### 4. Build firmware ESP32-S3

```bash
cd firmware
idf.py build
idf.py flash
```

### 5. Chạy giao diện web (nếu cần)

```bash
cd ui
npm install
npm run dev
```

---

## 📊 Kết Quả

| Mô hình | Accuracy | Params | Kích thước |
|---|---|---|---|
| MelCNN (Teacher) | ~98% | ~2.1M | ~8 MB |
| MelStudent | ~96% | ~200K | ~800 KB |
| MelStudent Pruned | ~94–98% | ~130K | ~520 KB |
| MelStudent INT8 | ~94% | ~130K | ~130 KB ✅ |

> [!TIP]
> Mô hình INT8 đã được tối ưu để chạy được trên ESP32-S3 với RAM hạn chế (~512KB SRAM).

---

## 📦 Dữ Liệu

Dữ liệu âm thanh thô được tổ chức theo nhãn:

```
data/
├── raw_data/
│   └── dau_nhua/
│       ├── v1c1/    ← version 1, class 1
│       └── ...
└── processed/
    └── data_lan7_no_smooth/
        ├── xanh/    ← *.npy (Mel-Spectrogram)
        └── chin/    ← *.npy (Mel-Spectrogram)
```

---

## 🛠️ Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
|---|---|
| Xử lý âm thanh | `librosa`, `scipy` |
| Deep Learning | `PyTorch` |
| Model export | `ONNX`, `torch.onnx` |
| Phân tích dữ liệu | `numpy`, `pandas`, `matplotlib`, `seaborn` |
| Firmware | `C` + `ESP-IDF` (FreeRTOS) |
| Giao diện web | `React` + `TypeScript` + `Tailwind CSS` + `Vite` |

---

## 👤 Tác Giả

**Nguyễn Văn Hưng** — Sinh viên nghiên cứu AI nhúng

---

> [!NOTE]
> Đây là dự án nghiên cứu sinh viên, tập trung vào việc đưa mô hình AI nhẹ (TinyML) lên vi điều khiển ESP32-S3 để phân loại trái cây theo thời gian thực.

