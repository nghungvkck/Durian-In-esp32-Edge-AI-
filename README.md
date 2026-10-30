# Duration Edge AI — bàn giao phiên làm việc

**Tài liệu bàn giao FreeCAD chính nằm tại [freecad_control/README.md](freecad_control/README.md). Phiên sau chỉ cần đọc file đó để tiếp tục CAD.**

**Cập nhật: 29/10/2026, Asia/Bangkok.** Công việc gần nhất là thiết kế vỏ và thao tác trực tiếp trên FreeCAD Windows. Đọc tài liệu này trước khi tiếp tục; không yêu cầu người dùng kể lại các lựa chọn đã chốt.

## 1. Vào việc ngay ở phiên sau

1. Đọc `/home/nghung/.codex/RTK.md`: **mọi lệnh shell phải có tiền tố `rtk`**.
2. Đọc README này và [README bản CAD hiện tại](3D/Enclosure_Upright_ICS43434/README.md).
3. Từ thư mục gốc dự án, chạy:

   ```bash
   rtk proxy python3 freecad_control/send.py freecad_control/inspect_connection.py
   rtk proxy python3 freecad_control/send.py freecad_control/resume_latest.py --timeout 60
   ```

4. Tiếp tục yêu cầu mới trên cụm lắp vừa mở. **Không dựng lại từ đầu, không mặc định mở module micro riêng hoặc các bản vỏ cũ.**

`resume_latest.py` tự tìm/mở file đã chốt theo đường dẫn, không phụ thuộc tên document hoặc biến Python của phiên trước. Nó hiện linh kiện cùng nửa vỏ sau, ẩn nửa trước và các khối thử đầu cáp. Nó kiểm tra sơ bộ vỏ còn nguyên và micro đứng trên ESP32; chỉ chỉnh hiển thị, không sửa hình học hay tự lưu file.

Nếu heartbeat mất/cũ, xem mục 4. Chữ `connected: true` trong file status cũ không chứng minh ứng dụng còn kết nối.

## 2. Bản CAD hiện tại được chấp nhận

**File chính duy nhất để tiếp tục:**

```text
3D/Enclosure_Upright_ICS43434/Enclosure_Upright_ICS43434.FCStd
```

| File trong thư mục trên | Ý nghĩa |
|---|---|
| `Enclosure_Upright_ICS43434.FCStd` | Cụm lắp đầy đủ, linh kiện nằm trong vỏ |
| `STL/Rear_half.stl`, `STL/Front_half.stl` | Đúng hai mảnh vỏ để in |
| `Two_shell_halves.step` | Hai nửa ở vị trí lắp thực |
| `ICS43434_upright_reference.step` | Micro đứng tại vị trí lắp; không phải phần in |
| `upright_mic_above_esp.png`, `rear_sound_holes.png` | Ảnh bố trí và lỗ âm |
| `validation.json` | Kiểm tra hình học, thể tích, STL và đường âm |

Document cũ có tên `Upright_ICS43434_Assembly`; khi mở lại có thể đổi tên/thêm hậu tố. Tìm bằng `FileName`, không giả định tên cũ luôn tồn tại.

**Lỗi giao tiếp cần tránh:** người dùng từng nhìn tab `ICS43434_Module_13mm` (chỉ chứa micro riêng) và tưởng micro chưa được đặt trong vỏ. Khi trình bày kết quả phải chuyển thật sang tab cụm lắp đầy đủ, mở/ẩn nửa trước để thấy micro trong vỏ.

## 3. Yêu cầu đã chốt

- Vỏ **trụ tròn Ø64 × cao 150 mm**, gồm **hai nửa tách dọc thân**; ghép lại mới thành trụ. Đỉnh/đáy liền hai nửa, không có nắp in rời.
- Linh kiện **dựng đứng, xếp từ dưới lên**: pin → module SD → IP5306 → ESP32-C3 → micro ICS-43434.
- ESP32-C3 đã xoay 90° trong mặt phẳng bo, cùng kiểu nằm với IP5306; hai cổng USB cùng hướng ra một phía hông.
- Công tắc **chìm ở mặt đáy**, nút gạt danh nghĩa không nhô dưới đáy; không còn đặt ở giữa thân.
- Micro **dựng đứng song song ESP32, phía trên ESP32**. Bố trí micro nằm ngang/úp xuống trước đó đã bị thay thế.
- Micro gần thành sau cho đường âm ngắn: mặt IC hướng +Y về mặt mở, mặt PCB có lỗ âm hướng -Y ra thành sau. Lỗ âm ở **thành sau**, không ở đỉnh.
- Có giá/gối/chặn giữ các bo và pin. Micro có giá, hai trụ vít M2 giữ mép, đệm cách điện và vòng đệm âm mềm. Đệm mềm không xuất chung với STL nhựa cứng.
- Người dùng muốn trợ lý **thao tác trực tiếp trong FreeCAD**, không chỉ hướng dẫn tự vẽ. Tiếp tục theo yêu cầu mới, không hỏi lại các lựa chọn đã chốt này.

### Tọa độ và kích thước (mm)

Z hướng lên; hai nửa chia tại Y=0; mặt linh kiện hướng +Y, phía trước mở để lắp. STEP gốc giữ tỷ lệ 1:1.

| Hạng mục | Giá trị |
|---|---|
| Vỏ | Ngoài Ø64, trong Ø58, vách 3, đáy 3, trần Z147–150 |
| Pin | Người dùng cung cấp **30 × 33 × 8**, dựng rộng 30/cao 33/dày 8; Z6–39 |
| SD | Bao ngoài 44,748 × cao 24 × dày 4; Z47–71 |
| IP5306 | 26 × cao 20 × dày 4; Z79–99 |
| ESP32-C3 sau xoay | Rộng 24 × cao 17,803 × dày 4,2; Z110–127,803 |
| Micro | Ø13 theo ảnh; PCB tạm dày 1,6; tâm (0, -26,8, 138); Z131,5–144,5 |
| USB sạc | IP5306, tâm khoảng (-13, -5,5, 89), hướng -X |
| USB code | ESP32, tâm khoảng (-12, -5,5, 118,902), hướng -X |
| Hốc đầu cáp | 15 × 12; kiểm tra khối đầu nhựa 12 × 8, dài 20 |
| Công tắc đáy | Tâm X0/Y16; bích Z3–3,8, thân Z3,8–11,3, nút tới Z0 |
| Lỗ âm | Tâm thành sau X0/Z138; 1 lỗ Ø1,2 + 6 lỗ Ø0,9, vòng bán kính 1,2 |

Linh kiện gốc nằm trong `3D/`: STEP ESP32, STEP SD, STEP IP5306; pin gốc là SLDPRT chưa chuyển đổi. Mô hình pin và micro là tham chiếu theo kích thước/ảnh, không phải toàn bộ hình học đã đo.

## 4. Kết nối FreeCAD từ Codex/WSL

### Đường dẫn

- Workspace WSL: `/mnt/d/Hoc_tap_Sinh_Vien/Kien_thu_AI/Project/Duration_edge_ai`
- Cùng thư mục trên Windows: `D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai`
- FreeCAD đã dùng: **1.1.4**, executable `C:\Program Files\FreeCAD 1.1\bin\FreeCAD.exe`.
- Không có FreeCAD MCP riêng. Cầu nối là macro Qt timer đọc/ghi file chung Windows–WSL, không mở cổng mạng.

### Còn ứng dụng và macro đang chạy

Chạy hai lệnh ở mục 1. `send.py` kiểm tra heartbeat trong vòng 10 giây trước khi gửi. Trong lúc một script CAD chạy lâu, heartbeat có thể ngừng tạm thời; kiểm tra thao tác đang chạy trước khi gửi thêm.

### FreeCAD đã đóng hoặc mất macro

Mở FreeCAD và chạy macro từ menu Macro:

```text
D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\freecad_control\Connect.FCMacro
```

Nếu cần mở bằng terminal, dùng Windows PowerShell `Start-Process` với executable và macro trên. Mở GUI Windows cần quyền thực thi phù hợp của phiên; không giả định quyền từ phiên trước còn hiệu lực. Nếu ứng dụng đã mở với file chưa lưu, ưu tiên chạy macro trong ứng dụng đó, không đóng lại làm mất sửa đổi.

Sau khi macro chạy, dùng `resume_latest.py`. Nếu di chuyển dự án, sửa đường dẫn Windows trong `Connect.FCMacro` và `resume_latest.py`.

### Gửi script chỉnh sửa

```bash
rtk proxy python3 freecad_control/send.py freecad_control/TEN_SCRIPT.py --timeout 120
```

- Script chạy **trong Python của FreeCAD Windows**, có sẵn `App`, `Gui`; tự import `Part`, `Mesh`... Không chạy script FreeCAD bằng Python Linux trực tiếp.
- Trả kết quả bằng `result` serialize được JSON. Thành công: `ok: true`; lỗi: traceback trong phản hồi `outbox`.
- Macro chạy trên GUI thread: không thêm vòng chờ chặn GUI.
- `inbox/*.json`: yêu cầu; `outbox/*.json`: phản hồi cùng UUID. `send.py` đã ghi file tạm/đổi tên nguyên tử.
- **Timeout không có nghĩa lệnh bị hủy.** Lệnh có thể còn chạy/chờ; kiểm tra phản hồi đúng UUID trước khi gửi lại thao tác tạo/sửa hình.
- Namespace có thể giữ biến, nhưng **script mới phải tự đủ imports/biến**, không phụ thuộc `doc`, `rear`, `OUT`, `view` của phiên trước.

## 5. Nguồn thiết kế và kiểm tra

Ưu tiên sửa **FCStd cuối đã lưu**, rồi xuất lại file liên quan. Không chạy chuỗi script thử cũ để khôi phục phiên.

| Script | Vai trò |
|---|---|
| `freecad_control/resume_latest.py` | Lệnh vào việc cho phiên mới, độc lập biến phiên trước |
| `freecad_control/inspect_connection.py` | Xem version/documents đang kết nối |
| `freecad_control/stand_microphone_upright.py` | Nguồn bố trí cuối, phụ thuộc document nền và module |
| `freecad_control/repair_upright_rear.py` | Ghi lại sửa boolean thân sau; không tự chạy lại trên bản cuối |
| `freecad_control/build_side_usb_bottom_switch.py` | Nguồn bản trước: USB hông, công tắc đáy |
| `freecad_control/iterations/`, các `finish_*`, `repair_*` khác | Lịch sử thử/sửa, có thể phụ thuộc biến sống trong phiên cũ |

Nếu thật sự cần dựng lại toàn bộ, đọc phụ thuộc trước: `stand_microphone_upright.py` cần document `Side_USB_Bottom_Switch` và module riêng `ICS43434_Module_13mm`. Các chỉnh sửa nguồn sau lần xuất cuối chưa được kiểm chứng bằng một lần dựng mới hoàn toàn; FCStd/STL đã kiểm tra là bản giao chính.

### Kiểm tra đã làm

- Hai nửa BRep hợp lệ, mỗi nửa một solid; hai STL kín.
- Không phát hiện giao thoa vượt ngưỡng 0,02 mm³ trong các cặp đã kiểm tra; bảy lỗ âm thông.
- Thể tích cuối: **Rear_half ≈ 73.775,965 mm³**, **Front_half ≈ 54.799,983 mm³**.
- STEP IP5306 ban đầu là các mặt triangulated; đã khâu thành solid để kiểm tra.
- Chưa in/lắp, thử điện, thử lực/rung hoặc đo đáp tuyến âm.

### Lỗi từng gặp, cần tránh

- Cắt trùng mặt nắp cũ tại Z137 từng tạo mặt độ dày bằng 0; fuse giá micro làm **mất cả thân sau**, chỉ còn giá khoảng **444 mm³**, dù vẫn “valid / 1 solid”. Đã sửa bằng giữ phần dưới tới Z136,8, fuse từng bước và kiểm tra thể tích. **Luôn kiểm tra BoundBox/thể tích còn nguyên vỏ, không chỉ `isValid()` và số solid.**
- Khi tạo bản tách lớp, cộng độ dịch vào placement hiện có; không gán đè làm bo về gốc.
- Sau xuất STEP/đổi tab, kiểm tra visibility và cửa sổ thực đang hiện. Nửa trước ẩn thì nửa sau phải hiện. Khối đầu cáp chỉ là vùng kiểm tra, không phải phần in.
- Sửa hình học xong phải cập nhật đồng bộ FCStd, STL, STEP, ảnh và `validation.json`; không trộn nửa vỏ khác phiên bản.

## 6. Điện và những việc chưa chốt

| Phần | Trạng thái |
|---|---|
| IP5306 | Người dùng xác nhận cổng sạc USB-C |
| SD | Người dùng xác nhận VCC/5 V có ổn áp; vẫn cần xác nhận mức logic 3,3 V |
| Pin | 3,7 V / 800 mAh; kích thước 30 × 33 × 8 người dùng cung cấp |
| Dây hiện có | 11 tuyến nguồn/GND/SPI tham chiếu, giữ trong cụm cuối |
| SPI đề xuất | SCK→GPIO4, MOSI→GPIO6, MISO→GPIO5, CS→GPIO7 |
| Nguồn | Pin→IP5306; OUT+ qua SW1 tới ESP 5V/VBUS và SD VCC; GND chung |
| Nạp code | **USB-OFF trước khi nối PC**, rút USB trước khi RUN; cách ly thủ công |
| I²S micro | **Chưa thêm dây, chưa chốt chân/firmware**; không báo đã đấu xong |
| Pad IP/SD | Đầu dây CAD là vùng danh nghĩa; cần ảnh rõ hai mặt/chữ pad hoặc schematic thật để chốt |
| Micro | Ø13 theo ảnh; PCB 1,6, vị trí pad và lỗ âm giữa bo còn là giả định |
| Công tắc | Vỏ tham chiếu 12,6 × 6 × 7,5; bích 23, hai vít cách 19; chưa chọn mã thực |
| Phần cứng khác | Chưa chốt dòng sạc pin, độ nén đệm, đầu cáp thực, lực giữ và chiều dài vít micro |

`firmware/sdkconfig` vẫn target **esp32s3**; `firmware/main/firmware.c` dùng LED GPIO48. CAD hiện dùng **ESP32-C3 SuperMini**. Chưa sửa/nạp firmware C3; không flash nhầm binary S3 vào C3.

Danh sách việc còn lại là thông tin bàn giao, không phải yêu cầu tự bắt đầu tất cả. Tiếp tục theo yêu cầu mới của người dùng.

## 7. File cục bộ và Git

- `3D/` và `freecad_control/` bị `.gitignore` bỏ qua, tồn tại **cục bộ trên máy này**; clone Git mới không tự có CAD/cầu nối. Giữ/sao lưu hai thư mục khi chuyển máy. Không tự sửa `.gitignore`, commit hoặc push.
- Cuối phiên thấy `.gitignore`, `models/DataLoader.py` có sửa đổi và `src/processing_data/smooth_plot.py` bị xóa. Không hoàn tác chúng theo README này; xem `git status` mới và giữ thay đổi ngoài phạm vi.
- `Enclosure_Cylinder*`, `Enclosure_Vertical_Clamshell`, `Enclosure_Wired_Clamshell`, `Enclosure_Side_USB_Bottom_Switch`, `Enclosure_With_ICS43434` là lịch sử. Đặc biệt `Enclosure_With_ICS43434` đặt micro ngang, **không phải bố trí cuối**.
- Khi có yêu cầu mới được chốt, cập nhật README này và README bản CAD mới.

## 8. Phần AI của dự án

Dự án gốc phân loại độ chín trái cây bằng âm thanh gõ: xử lý dữ liệu ở `src/`, mô hình ở `models/` và `notebook/`, xuất ở `ONNX/`, firmware ở `firmware/`.

README cũ được giữ tại [docs/PROJECT_OVERVIEW_BEFORE_CAD.md](docs/PROJECT_OVERVIEW_BEFORE_CAD.md). Các kết quả accuracy và target S3 trong tài liệu đó là nội dung trước đây, chưa kiểm chứng lại trong phiên CAD.
