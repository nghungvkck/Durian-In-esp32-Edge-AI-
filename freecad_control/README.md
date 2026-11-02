# FreeCAD — bàn giao cho phiên tiếp theo

Cập nhật **02/11/2026, Asia/Bangkok**. Đọc file này trước khi tiếp tục CAD. File tự chứa trạng thái cuối, đường dẫn file in, cách kết nối và việc còn dở; không cần đọc README gốc dự án. Khi sửa chi tiết, đọc thêm `3D/Enclosure_USB_Near_Wall_D50/DESIGN_NOTES.md`, nhưng ưu tiên các chốt mới trong tài liệu này hơn lịch sử.

## Chốt mới nhất — giản lược giá PCB ba nút (02/11/2026)

Theo yêu cầu mới, **giá PCB ba nút chỉ còn hai thanh ngang trên/dưới và ba lỗ cho đầu nút nhô ra**. Đã bỏ hai trụ tròn tại Z133/163, hai thanh dẫn dọc và toàn bộ gờ nhỏ của giá nút. Giữ nguyên hai thanh ngang nối thành tại Z128,7–129,7 và Z166,3–167,3; ba lỗ Ø4,6 ở X0/Z140,148,156 cùng hốc né thân nút phía trong. Không còn gờ kẹp bên riêng cho PCB nút; đây là ngoại lệ mới đối với yêu cầu giữ gờ linh kiện ở mục 3. Chưa thử giữ/lắp bo thực tế.

Đã lưu bản chính `3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd`, SHA-256 `718f4e5f86de5c4ae2f2d962ae061e29d907d7df437ade1af9e2fd6c8e702ce3`. Nửa trước hợp lệ, một solid, thể tích **72716,831590 mm³**; nửa sau giữ nguyên **86600,815315 mm³**; hai nửa giao thể tích **0 mm³**. Bao ngoài Ø50 × 201 giữ nguyên. Toàn bộ 76 đối tượng có Shape ngoài nửa trước giữ nguyên BRep/placement, tổng vẫn 80 objects; không sửa PCB, nút, LED, dây hoặc linh kiện khác. Kiểm tra cụm nút không giao thể tích với nhựa; vùng bỏ giá không còn nhựa nhô vào khoang.

Backup `Enclosure_USB_Near_Wall_D50_before_simple_key_support.FCStd`, báo cáo `simple_key_support_validation.json`, ảnh `simple_key_support_inside.png` trong thư mục CAD. Đã kiểm tra ảnh và để GUI xem cận mặt trong nửa trước. `removeSplitter()` tạo ứng viên không hợp lệ nên đã loại bỏ, giữ kết quả Boolean hợp lệ; đường chia mặt khi xem Flat Lines không phải gờ nhựa, dùng Shaded.

**Bộ STL/ZIP và nguồn hai vỏ trong `Print_2026-11-02/` vẫn thuộc bản trước thay đổi giá nút này**, chưa xuất lại. Không gửi nửa trước trong bộ đó nếu cần đúng sửa đổi mới. Các mục bên dưới ghi lại mốc xuất in và trạng thái dây; không dùng các thể tích/hash lịch sử thay cho mốc mới này. Không có yêu cầu tiếp tục nối dây hoặc firmware.

## 1. Bộ xuất in trước lần giản lược giá nút

Trước khi giản lược giá nút, người dùng đã yêu cầu **dừng nối dây, xuất riêng hai nửa vỏ để đi in**. Hai STL đã xuất, kiểm tra và đóng gói cho mốc đó. Sau đó đã sửa và lưu giá nút theo phần đầu tài liệu; **chưa xuất lại STL cho thay đổi mới**. Không tự tiếp tục CAD, nối dây hoặc firmware khi chưa có yêu cầu mới.

Thư mục file in, tính từ gốc dự án:

```text
3D/Enclosure_USB_Near_Wall_D50/Print_2026-11-02/
```

| Tệp | Dùng để làm gì |
|---|---|
| `Hai_vo_LED3mm_STL.zip` | Gói in mốc trước giản lược giá nút: hai STL, hướng dẫn và báo cáo kiểm tra |
| `Rear_half.stl` | Nửa vỏ sau; in 1 chiếc |
| `Front_half_LED3mm.stl` | Nửa vỏ trước, có lỗ/ngàm giữ LED đơn Ø3 mm; in 1 chiếc |
| `README.md` | Hướng dẫn nhập slicer và những thông số chưa chốt |
| `export_validation.json` | Hash, nguồn xuất, kích thước và kết quả kiểm tra mesh |
| `Print_source_LED3mm.FCStd` | **Nguồn hai shape đúng với bộ STL đã xuất**; chỉ có hai nửa vỏ, không phải toàn bộ assembly |

Đơn vị **mm**, tỷ lệ **100% (1:1)**. Bao vỏ ghép Ø50 × 201 mm. Chỉ xuất nhựa vỏ, không chứa pin, bo, dây hoặc linh kiện phụ. Mỗi STL kín, cạnh manifold, hướng mặt nhất quán, một thành phần liên thông, không có tam giác suy biến. Đã đối chiếu thể tích mesh với BRep. **Đây là kiểm tra file, chưa phải xác nhận in/lắp thực tế.** Chưa tạo G-code, chọn profile máy, vật liệu, hướng in hoặc support.

Đỉnh Z168–201 là vùng đặc của hình học; infill do slicer quyết định. Khi chuẩn bị in FDM cần đặt modifier thích hợp nếu muốn vùng này đặc 100%. Chưa xác nhận dung sai, lực gài/nhả, độ bền gờ/ngàm/lẫy hoặc kích thước linh kiện thật. Không tự xuất lại STL, sửa hình học hoặc thay bộ file in đã chốt nếu chưa được yêu cầu.

## 2. Chọn đúng nguồn CAD — cần đọc trước khi mở hoặc lưu

Mọi đường dẫn CAD trong các phần dưới tính từ `3D/Enclosure_USB_Near_Wall_D50/`.

- Assembly làm việc vẫn mang tên `Enclosure_USB_Near_Wall_D50.FCStd`, nhưng **file này đã được lưu tiếp trong lúc làm việc; không mặc định nội dung trên đĩa giống mốc xuất in hoặc báo cáo cũ**.
- Lúc xuất STL, file chính trên đĩa có hash `1330f1d286a0f51a96c123c7ec43038625d501d13b4a8af6032e26f475cebf7c`, Document.xml không có LED. Hai shape trong GUI vẫn đúng mốc LED; đã đối chiếu hash BRep và lưu nguồn hai vỏ riêng để bảo toàn kết quả in.
- Mốc trước sửa giá nút, hash file chính từng là `2dd980ffe8ca6b697d09aa23c8cb939d78fd66c59996d59186c01be94fc47eb7`, có **80 objects**, có `Status_LED_3mm` và `Complete_Wiring`. Sau sửa giá nút đã lưu hash `718f4e5f86de5c4ae2f2d962ae061e29d907d7df437ade1af9e2fd6c8e702ce3`; kiểm tra tính toàn vẹn FCStd và hash trên đĩa khớp báo cáo. Hệ dây nháp vẫn được giữ nguyên; không coi lần kiểm tra giá nút là xác nhận toàn bộ hệ dây.
- `complete_wiring_validation.json` còn ghi `saved: false`: đó là trạng thái lần thao tác của agent dừng trước bước lưu cuối, **không còn đủ để kết luận file chính hiện không chứa dây**. Không sửa báo cáo lịch sử thành một lần kiểm tra chưa thực hiện.
- **Muốn dùng đúng hai vỏ đã xuất in:** dùng `Print_2026-11-02/Print_source_LED3mm.FCStd` và `export_validation.json` cùng thư mục. Không lấy assembly đang thay đổi để thay thế bộ in đã chốt.
- **Muốn sửa tiếp toàn bộ assembly:** kiểm tra heartbeat, đúng document/FileName và trạng thái hiện tại trước; đối chiếu hai nửa với nguồn in nếu thay đổi có liên quan. Dùng `resume_latest.py` để mở/hiện đúng assembly, nhưng script này không chứng minh assembly giống nguồn STL.
- Không tự lưu đè document đang mở, hoàn tác file chính về backup, đóng các phiên khác hoặc dựng lại CAD từ đầu. Hash là mốc đối chiếu, không phải lý do tự hoàn tác khi người dùng đã lưu tiếp.

SHA-256 nguồn hai vỏ in riêng đã kiểm tra:

```text
f1ca701454b961abe9d44eebf1b900aec12956cf3ddaccfc7a943da0902b56ce
```

BRep của hai vỏ đã xuất: mỗi nửa hợp lệ, một solid; Rear **86600,815315 mm³**, Front **73281,150269 mm³**. Giao thể tích khi đóng ở mốc LED **0 mm³**. Không áp dụng kết luận này cho một assembly mới chưa đối chiếu.

## 3. Cấu hình cơ khí đã chốt và phải giữ

**Giữ gờ giữ linh kiện trực tiếp trên khung, gân ngang nối thành trụ và sáu lẫy ghép vỏ; riêng giá PCB nút chỉ giữ hai thanh ngang theo chốt mới.** Không dùng cách chặn linh kiện nhờ đóng nắp.

- Pin, SD, IP5306, ESP32-C3, micro và công tắc giữ gờ/bệ trên chính khung, hai điểm mỗi cụm. Gờ chỉ chồng mép trống, tránh IC/pad/chân hàn. PCB nút đã bỏ trụ, thanh dẫn dọc và gờ bên; không tự khôi phục.
- Phương án `easy_insert` đã bỏ: mười thanh chặn trên nửa trước, cửa dẫn/rãnh và bốn lẫy linh kiện mới của phương án đó đã hoàn tác. Không đưa lại phương án này để “dễ lắp”; không áp dụng 22 kiểm tra đường lắp hoặc trình tự luồn PCB nút lên 100 mm của nó cho bản hiện tại.
- Giữ gân ngang 13 tầng/26 nhánh tới thành cong; sáu lẫy ghép tại X±21/Z14,97,166. Lỗ vít ghép cũ và pilot giữ linh kiện đã lấp.
- LED đơn Ø3 mm ở **mặt trước +Y, tâm X0/Z123**, dưới nút thấp nhất 17 mm. Lỗ Ø3,3; bệ Ø6,8 có bậc chặn và hai ngàm giữ liền nửa trước. Ngàm dày 0,8, tự do 8,4 mm, chân Z114,8–116; không cần nửa sau để giữ LED.
- LED/vành/chân là kích thước danh nghĩa: vành Ø3,8 dày 0,6, bước chân 2,54, đầu LED Y25,05. Chưa có mã LED thật; màu xanh chỉ dùng nhận diện trong CAD.
- Lần nối dây giữ nguyên hai nửa vỏ và 29 tham chiếu linh kiện; chỉ sửa 11 tuyến dây cũ và thêm dây/linh kiện phụ. Không tự bố trí lại linh kiện.

Đơn vị mm; Z hướng lên, mặt ghép Y0, +Y là trước:

| Hạng mục | Bố trí cần giữ |
|---|---|
| Vỏ | Ø50 × 201; khoang chính Ø44 dưới Z168; đáy Z0–3 |
| Đỉnh | Đặc Z168–201; khe X20 × Y3 thông xuống khoang, giữ đáy; lỗ Ø4 theo Y tại X0/Z176,196 |
| Pin | X/Y/Z = 28/8/38, Z6–44; lòng khay 29,4, hở cạnh 0,7; gờ rộng Z5, chồng mép 2, hở mặt 0,4 |
| SD | Dọc, rộng 24, Z47–91,748, header trên |
| IP5306 / ESP32-C3 | IP Z100–120; ESP Z131–148,803; USB hướng −X, đầu X−23, tâm Y−5,5/Z110 và 139,9016 |
| Micro | Dựng đứng, tâm (0,−19,8,159); đường âm ra sau −Y; đệm mềm riêng, không nhập vào nhựa |
| Nút / công tắc | PCB ba nút Z130–166 phía trước; tâm ba lỗ Ø4,6 tại X0/Z140,148,156; hai thanh ngang Z128,7–129,7 và Z166,3–167,3; công tắc ở đáy |

ESP giữ mép bên trống, tránh hàng pad hai đầu: gờ X−21,7/Z133,75–134,95 và X1/Z144,5–145,7. Micro giữ hai cạnh; công tắc giữ tai bích. Nút không còn hai gờ đối góc. Vùng tránh IC/pad/chân hàn 0,5 mm và USB kim loại 0,35 mm, xét hai mặt bo. IP5306 có mô hình dạng mặt rời. Chi tiết xem `DESIGN_NOTES.md` và `component_clearances.json` trong thư mục CAD.

## 4. Hệ dây đã dừng — không tự tiếp tục

Kế hoạch có **33 dây, 5 linh kiện phụ**, thêm hai chân công tắc danh nghĩa, nhóm `Complete_Wiring`. 11 tuyến cũ sửa đầu nối + 22 dây mới. Bản nháp đã tạo trong GUI có 70 đối tượng mô hình, tổng 80 objects khi tính nhóm/phụ trợ. Bản chính đã lưu sau sửa giá nút vẫn có hệ dây này; lần sửa chỉ xác nhận giữ nguyên BRep/placement ngoài nửa trước, chưa kiểm tra lại toàn bộ va chạm dây.

| Dữ liệu | Trạng thái |
|---|---|
| `complete_wiring_plan.json` | 33 tuyến, đầu chân, GPIO và linh kiện phụ dự kiến |
| `wire_netlist.json` | Vẫn là **11 tuyến cũ**, không phải danh sách 33 tuyến |
| `wire_netlist_before_complete_wiring.json` | Bản sao danh sách 11 tuyến trước thao tác |
| `electrical_connectivity_audit.json` | Đủ 33 quan hệ kết nối logic, không trùng GPIO, không nối tắt trực tiếp nguồn/tín hiệu, không nối vòng qua điện trở LED |
| `complete_wiring_validation.json` | Báo cáo nháp, có kiểm tra va chạm lưới và giới hạn; `saved:false` là trạng thái lần agent dừng |
| `complete_wiring_overview.png` | Ảnh tổng quan dây, ẩn hai nửa vỏ |
| `complete_wiring_detail.png` | **Chưa được tạo**; không dẫn file này làm bằng chứng |
| `WIRING.md` | Mô tả sơ đồ tham chiếu và giả định, đã đánh dấu nháp dừng |

Kiểm tra lưới bề mặt vỏ (độ lệch tessellation 0,2 mm) phát hiện **6 đoạn thuộc 5 dây xuyên/chạm nhựa**, chưa sửa: `MIC_3V3` đoạn 3 và 4; `KEY1_signal`, `KEY2_signal`, `KEY3_signal`, `KEY1_GND` đoạn 4. Đây không phải bản đi dây đã xác nhận lắp được. Chưa kiểm tra đầy đủ va chạm giữa các dây, bán kính uốn, độ chùng mở nắp hoặc giữ/cách điện linh kiện phụ.

Danh sách `terminal_gaps` chỉ là khoảng cách từ điểm tới hình học; điểm nằm trong solid hoặc giữa lỗ pad vẫn có thể trả khoảng cách dương. Không dùng nó riêng lẻ để kết luận hở điện, cũng không coi khối cách điện chạm nhau trong CAD là nối điện thật. Pinout module, cực LED, tiếp điểm nút/công tắc và thông mạch phần cứng chưa xác minh.

GPIO tham chiếu: SD SCK4/MISO5/MOSI6/CS7; micro BCLK3/WS2/DATA1, VDD3V3, GND/LR nối GND; nút dưới/giữa/trên GPIO0/20/21; LED GPIO10 qua 1 kΩ, cathode GND. Phụ trợ: R_KEY3 1 kΩ nối tiếp GPIO21, R_GPIO2_PU 10 kΩ, R_MIC_SD_PD 100 kΩ, C_MIC 100 nF. Nút nối trực tiếp chân công tắc tham chiếu, không gán chức năng giả cho bốn pad connector trên PCB nút. GPIO8/9 chưa dùng; GPIO20/21 cần nhả UART0, nút cần input pull-up trong firmware C3.

**Firmware chưa khớp CAD:** `firmware/sdkconfig` vẫn nhắm `esp32s3`; `main.cpp` đã có pipeline thu âm/xử lý/inference, BCLK3/WS2/DIN1, yêu cầu PSRAM và dừng khi không có. Chưa chuyển/nạp C3 hoặc triển khai SD/nút/LED cho cấu hình CAD. Không flash binary S3 sang C3. Mức logic SD 3,3 V, dòng sạc, tự tắt tải thấp IP5306, tải ổn áp, bảo vệ pin và chống cấp ngược USB chưa xác nhận. Chế độ đã chốt: tắt SW1 trước khi nối USB nạp, rút USB trước khi RUN. Không tự triển khai điện/firmware trong việc CAD.

## 5. Kết nối FreeCAD Windows khi có yêu cầu mới

Chạy từ gốc dự án. Mọi lệnh shell có tiền tố `rtk` theo `/home/nghung/.codex/RTK.md`. **Không chạy CAD bằng Python Linux.** Không cần kết nối hoặc mở CAD chỉ để lấy bộ STL đã xuất.

```bash
rtk proxy python3 freecad_control/easy_insert_session/send.py freecad_control/inspect_connection.py
rtk proxy python3 freecad_control/easy_insert_session/send.py freecad_control/resume_latest.py --timeout 60
```

Đọc mục 2 trước: `resume_latest.py` mở đúng assembly theo **FileName**, chuyển tab, kiểm tra bố trí và hiện toàn bộ nửa sau/linh kiện, ẩn nửa trước; không sửa hình học hoặc lưu. Nó không đối chiếu assembly với bộ STL đã chốt. Không dùng bản micro nằm ngang cũ hoặc chạy script thử lịch sử để dựng lại trạng thái.

Cầu nối đang dùng là `easy_insert_session`; tên không có nghĩa phương án cơ khí `easy_insert` còn áp dụng. `send.py` chỉ nhận khi heartbeat mới dưới 10 giây. Nếu mất kết nối, chạy macro trong đúng phiên FreeCAD:

```text
D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\freecad_control\easy_insert_session\Connect.FCMacro
```

FreeCAD 1.1.4: `C:\Program Files\FreeCAD 1.1\bin\FreeCAD.exe`. Khi dọn thư mục, cả ba cầu nối đều có heartbeat mới: `easy_insert_session` PID156496, gốc PID23396, `open_tray_session` PID131024. Đây chỉ là mốc quan sát; kiểm tra heartbeat thực tế ở lần tiếp tục. Giữ cả ba bộ cầu nối vì các phiên vẫn hoạt động; không tự đóng/lưu phiên khác, dùng cầu nối gốc hoặc đổi sang `open_tray_session/`. PID210936 từng có sửa chưa lưu; không suy luận trạng thái hiện tại từ PID lịch sử.

**Timeout không hủy lệnh.** Theo dõi đúng UUID/outbox trước khi gửi lại. Script mới phải đủ imports/biến, không phụ thuộc globals phiên trước. Script lịch sử `check_wiring_geometry.py` lấy mẫu trực tiếp quá chậm, đã dừng ở checkpoint và nay đã xóa; không dựng lại để chạy lại. Kết quả thay thế đã có ở `complete_wiring_validation.json` trong thư mục CAD, tính từ mesh do Windows FreeCAD xuất. File tiến độ phần đã kiểm tra vẫn giữ ngoài phạm vi dọn thư mục này.

## 6. Quy tắc sửa tiếp và tài liệu lịch sử

1. Chỉ sửa phần được yêu cầu; giữ shape/placement ngoài phạm vi. Trước khi lưu, kiểm tra BRep, số solid, kích thước, giao thoa liên quan và viewport. Khi người dùng chốt thay đổi, cập nhật README này cùng README CAD tương ứng. Không tự sửa `.gitignore`, commit/push hoặc xóa lịch sử CAD.
2. Không Boolean toàn bộ các cụm nhập phức tạp gần giống nhau hoặc lặp nhiều lần; từng làm treo GUI. Ưu tiên kiểm tra cục bộ. Với IP5306 dạng mặt, `common.Volume == 0` không đủ để kết luận hết cấn; xét diện tích giao/khoảng cách.
3. Dùng `optimalBoundingBox(False,False)` để kiểm tra bao. BoundBox nhanh của spline đã cắt có thể rộng giả. `removeSplitter()` trên nửa sau từng báo `Bnd_Box is void`. Vỏ dùng Shaded; nét chia mặt không phải gờ nhựa. Camera có animation; chờ ổn định hoặc đặt camera đầy đủ khi chụp. Import `from pivy import coin` trước `getCameraNode()` ở phiên mới.
4. Giữ backup/bằng chứng cuối/cầu nối. Các script tạo/sửa/xuất dùng một lần trong `freecad_control/` đã xóa sau khi hoàn tất; không cần chúng để mở bản chính. Nếu dọn log, chỉ xóa request đã có phản hồi hợp lệ, inbox trước rồi outbox; phản hồi lẻ được xóa khi không còn request tương ứng. Giữ request đang chạy. `3D/` và `freecad_control/` là dữ liệu cục bộ bị Git bỏ qua.
5. `status_led_validation.json`, `status_led_front.png`, `status_led_socket.png` là mốc LED trước nối dây. `restored_frame_lips_*` là mốc khôi phục gờ trước LED. Các mốc `easy_insert_*`, `frame_ribs_*`, `shell_snaps_*`, `screwless_*`, FCStd/FCBak khác là lịch sử; không lấy chúng thay bộ in hiện tại.
6. Bản vẽ Rev C bốn tờ A3 trong `Technical_Drawing/`, STL/STEP lịch sử ngoài `Print_2026-11-02/` chưa đồng bộ với bộ vỏ LED đã xuất. Không tự xuất lại. Chỉ khi người dùng yêu cầu bản vẽ: giữ 3D; chạy `prepare_final_drawing.py` qua cầu nối → `render_final_drawing.py` bằng Python có PyQt5 → `open_final_drawing.py` qua cầu nối. Giữ `TEXT_SCALE=1.4`, kiểm tra đủ bốn trang A3.

## 7. Dọn thư mục `freecad_control` — 02/11/2026

Theo yêu cầu, chỉ cập nhật/xóa bên trong `freecad_control/`; không sửa CAD, STL, backup, ảnh hay báo cáo trong `3D/`. Thư mục này chỉ có một file Markdown là `README.md`; đã sửa các mô tả cũ về gờ nút, hash bản chính và trạng thái bộ in để khớp lần giản lược mới.

Đã xóa **26 script dùng một lần**, **82 cặp request/response đã xử lý** và **31 response lẻ hợp lệ** — tổng **221 file**. Nhóm script đã bỏ gồm thử/tạo/sửa LED, đi dây, kiểm tra/xuất mesh/STL và giản lược giá nút; kết quả CAD và bằng chứng cuối vẫn nằm trong thư mục CAD. Khi dọn không có request chưa có phản hồi. Không xóa thư mục cầu nối hoặc `inbox/`, `outbox/` đang được các macro dùng.

Các file vận hành giữ lại:

| Đường dẫn trong `freecad_control/` | Vai trò |
|---|---|
| `README.md` | Bàn giao hiện trạng và cách tiếp tục |
| `resume_latest.py` | Mở/hiện đúng assembly; không sửa hình học hoặc lưu |
| `inspect_connection.py` | Xem phiên bản và danh sách document qua cầu nối |
| `easy_insert_session/{Connect.FCMacro,send.py,status.json,inbox/,outbox/}` | Cầu nối dùng cho bản chính |
| `{Connect.FCMacro,send.py,status.json,inbox/,outbox/}` | Cầu nối gốc, giữ để không ảnh hưởng phiên khác |
| `open_tray_session/{Connect.FCMacro,send.py,status.json,inbox/,outbox/}` | Cầu nối phiên cũ còn heartbeat |
| `.gitignore` | Giữ nguyên |

Không commit/push. Khi cần sửa tiếp, đọc tài liệu này rồi dùng bản chính đã lưu; không chạy lại request lịch sử hoặc dựng lại CAD từ các bước cũ.
