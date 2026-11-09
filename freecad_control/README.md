# FreeCAD — bàn giao D36 và trạng thái trên đĩa

Cập nhật **06/11/2026, Asia/Bangkok**. Đường dẫn tương đối tính từ gốc dự án `Duration_edge_ai`. Đây là tài liệu đọc trước khi tiếp tục CAD; không cần đọc README gốc dự án.

## 1. Chênh lệch cần biết trước khi tiếp tục

**File CAD chính trên đĩa hiện khác bản 21 dây đã kiểm chứng.** Lần dọn tài liệu này chỉ đọc ZIP/XML/SHA-256, không mở hay sửa/lưu CAD và không khôi phục bản nào.

| Bản | Trạng thái quan sát được |
|---|---|
| `CAD_DIR/D36_Printed_Retention_35x25x6.FCStd` | XML có **43 objects**, không có `Wire_*`, không có group dây hoặc sáu phần vít/đai ốc; có các objects TPU, preview tách, LED và R/C |
| `CAD_DIR/D36_Printed_Retention_35x25x6.20261106-103437.FCBak` | Hash khớp **bản 55 objects, 21 dây đã gom gọn** được kiểm chứng trước đó |

`CAD_DIR` là:

```text
3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6
```

SHA-256 file chính hiện trên đĩa:

```text
7ffc4262b453c2585239551817bba8d1cc305e709a64e4abfb961d7eeb396e66
```

SHA-256 backup 21 dây đã kiểm chứng:

```text
39f39e587e6e562525fdf9370f45cbdf2783d0e3523c8590d6a385d9aaf9cb29
```

ZIP/XML cho thấy cả hình học lưu và nhiều Placement của 43 objects hiện tại khác backup; không coi là chỉ đổi viewport. Nhãn pin trong file hiện tại ghi38×28×8 mm, nhưng lần này không dùng kernel để đo/xác nhận kích thước. Báo cáo valid, Ø36×146 và khoảng hở của bản55 objects **không xác nhận hình học file43 objects hiện tại**. Chưa xác định nguyên nhân file thay đổi; không suy ra nội dung GUI từ file trên đĩa hoặc heartbeat.

**Không chạy script sửa lịch sử, không ghi đè hoặc tự phục hồi CAD.** Trước khi tiếp tục sửa, cần chốt bản làm việc với người dùng. `resume_latest.py` vẫn trỏ tên file chính, không tự chọn backup; chưa dùng nó để tiếp tục bản55 objects khi file chính còn khác biệt. Mọi CAD/backup/STL/báo cáo trong `3D` được giữ nguyên.

Đối chiếu chi tiết tên object/Placement/hash và các objects thêm/bớt nằm trong [manifest dọn06/11](archive/cleanup_2026-11-06/cleanup_manifest.json), mục `cad_disk_audit`.

## 2. Thiết kế đã chốt và bản 21 dây được kiểm chứng

Mục này mô tả **backup55 objects có hash ở trên**, không phải kết quả đo mới cho file43 objects.

| Mục | Trạng thái đã chốt |
|---|---|
| Vỏ | Ø36×146 mm, Z0…146; vách danh nghĩa2 mm, đáy3 mm, khoangØ32 |
| Trục | +Y là trước; Z dọc thân; hai nửa chia tại Y0 |
| Objects | Hai vỏ +6 phần vít/đai ốc +25 phần linh kiện +group +21 dây =55 |
| Vít | Ba bộ M3×30, trụcY, X0, tại Z18/121/141; lỗØ4; hốc đầuØ6,2, tựaY13; hốc đai ốcAF5,9, tựaY−14,1 |
| Pin |35 theoZ ×25 theoX ×6 theoY; X±12,5; Y−3,824074…2,175926; Z26,5…61,5 |
| ESP | ESP32-S3 Super Mini, dùng nguyên hình/vị trí C3 theo người dùng; tên nội bộ `ESP32_C3`, Label và `BoardIdentity` ghi S3/proxy |
| Micro | PCBØ13×1,6 mm, IC mô hình cao2 mm theoY; một ngàmU dưới rộng4 mm |
| Đã bỏ | TPU/hốc TPU, preview tách, vít/lỗ/trụ M2 lệch cạnh, R/C rời, LED rời và đệm micro |

Thân đã tăng10 mm tại Z13; giữ công tắc/chân/cửa đáy, dịch cụm phía trên Z+10. Không dùng tọa độ bản136 mm cho bản146 mm. Trụ vít dưới R4,5 gặp tại Y0.

Gờ đã gia cố: lưng thanh pin nửa sau0,8→1,6 mm, bề rộngZ4→5,2 mm; chặn đầu tăng0,8→1,6 mm về phía ngoài pin, mặt đỡY−4,624074 giữ nguyên. Chân mở về hai vách, cắtR16,8. Mở chân gờ SD/ESP/bo nút ở nửa trước, IP5306/đế ngàm micro ở nửa sau. Không thêm khung pin đối xứng nửa trước hoặc ngàm micro bên/trên.

Yêu cầu giữ: SD chỉ hai giá góc đối diện, không làm mặt ép pin; micro giữ một đầu; giữ bằng chi tiết in, không tự thêm keo/mút/băng dính. Vật liệu nhựa cứng và profile in chưa chọn. Không đổi kích thước linh kiện để ép vừa. IC micro cao2 mm là yêu cầu mô hình, chưa xác nhận theo vật thật.

## 3. Sơ đồ dây và kiểm chứng của bản gom gọn

Nguồn GPIO: `firmware/README.md` mục7 ngày05/11; bảng ví dụ micro ở mục6 là mốc cũ.

| Cụm | Nối logic |
|---|---|
| SD3V3, theo người dùng | CS/SCK/MOSI/MISO→GPIO13/12/11/10; VCC→ESP3V3, GND chung |
| ICS43434 | SD/SCK/WS→GPIO4/5/6; VDD→ESP3V3, GND chung; L/R→GND |
| Ba nút | CHÍN/XANH/suy luận→GPIO1/2/3, nhấn kéo xuốngGND, pull-up nội theo firmware |
| Nguồn | Pin→IP5306 B+/B−; IP5V→công tắc→ESP5V; IPGND→ESPGND |
| LED | GPIO7 dành cho LED theo firmware; bản55 objects không có LED rời nên không thêm dây LED |

21 dây đã gom: SPI chạy thành dải; micro dùng hành lang chung và tách nhánh quanh mép; nút chạy theo mép PCB; dây nguồn chạy lớp dưới với các đoạn song song. Dây nguồn5V/pin Ø ngoài0,90 mm, dây khác0,65 mm; tổng tâm dây bo góc **693,57 mm**, chưa có dư hàn/mở vỏ.

Báo cáo `CAD_DIR/Wiring_Tidy_2026-11-06/validation.json` xác nhận tại mốc hash `39f39e587e6e562525fdf9370f45cbdf2783d0e3523c8590d6a385d9aaf9cb29`:

- 21 dây và hai vỏ đọc lại từ BRep: valid, mỗi shape một solid; vỏØ36×146.
- Kiểm tra từng dây với33 objects ban đầu và mọi cặp dây: không phát hiện giao thoa ngoài vùng tiếp điểm. IP5306 dạng mặt được xét diện tích giao, không chỉ thể tích.
- Vùng tiếp điểm với đúng linh kiện: bán kính1,3 mm; dây cùng net/cùng pad được chung vùng1,1 mm. Hở dây–vỏ/gờ nhỏ nhất khoảng0,242 mm.
- 33 BRep cơ khí/linh kiện trùng byte với backup trước gom; vertices/edges/faces/volume/Placement đối chiếu đạt.

**Pad vật lý vẫn là tham chiếu**, chưa đối chiếu thứ tự chân S3 thật, đầu cực pin, IP5306, công tắc và các module. Hình SD đang có cũng chỉ đại diện breakout3V3. Không dùng thứ tự pad trong mô hình làm hướng dẫn hàn vật thật.

Chưa xác nhận: vòng chùng/đường mở vỏ, phần dư hàn, kẹp giữ/chống rung/cách điện, AWG/vật liệu/bán kính uốn dây, ngân sách dòng3V3, tự tắt IP5306, cách ly USB, anten, nhiệt, âm học, đường tháo SD và lắp thực. Chưa build/flash firmware. Chưa kiểm tra in/lực giữ/độ bền và cầm/lắc/gõ không phát tiếng.

## 4. Bằng chứng và STL giữ nguyên

| Thư mục trong CAD_DIR | Vai trò |
|---|---|
| `Wiring_Tidy_2026-11-06/` | Bản tuyến gom gọn: README, routes trước/sau, validation, ảnh và BRep đọc lại; backup trước gom `D36_before_tidy.FCStd` có hash36d34f… |
| `Wiring_2026-11-06/` | Mốc đi dây đầu đã thay tuyến; dài567,53 mm, vùng chung3,2 mm; backup trước đi dây có hash9c08bf… |
| `Reinforced_Frame/` | Gia cố gờ, validation/ảnh/backup; thể tích Front/Rear29340,783389 /30828,065379 mm³ |
| `Centered_Lower_M3/` | Thân146 và ba vít thẳng hàng |
| `Print_2026-11-03/` | Hai STL vỏ D36 và validation xuất |
| Các thư mục khác | Lịch sử giữ nguyên; không dùng thay bản đã chốt |

STL03/11 chỉ gồm hai vỏ, không vít/linh kiện/dây. Binary, import theo mm, tọa độ lắp chưa xoay hướng in; linear0,05 mm, angular0,15 rad. Báo cáo xuất ghi mesh closed solid, X36/Z146, lệch thể tích BRep dưới0,12%.

| File trong `Print_2026-11-03/` | SHA-256 |
|---|---|
| `D36_Front_half_2026-11-03.stl` | `a22ef03c5108e645dceb502ebabb76d9f4aacc86228a0269e32caa72df422ae4` |
| `D36_Rear_half_2026-11-03.stl` | `fb28b9829afbdebd1c7371fa1708fe5e101627fd5579744606966499e0edb812` |

Hash nguồn STL là `30ffa569b3b1985c07a908fed7001bee70d0980014a19a7e67fb60a15af345c7`; không gán hash đó cho CAD hiện tại. Bản trước đi dây hash `9c08bf20382902c3c63c73057a5198aed6180d2e375f15898e6718bc947cc806`. Chưa slicer/G-code/profile/hướng in/support/in thử; không dùng ước lượng thời gian in cũ. `Front_half_no_ribs.stl` ở gốc dự án là D50.

## 5. Kết nối FreeCAD và tiếp tục

Giữ ba cầu nối: gốc `freecad_control`, `easy_insert_session`, `open_tray_session`. D36 dùng `easy_insert_session`; heartbeat phải dưới10 giây. `connected: true` cũ không chứng minh còn kết nối. FreeCAD Windows đã quan sát1.1.4, executable `C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe`.

Lệnh kiểm tra kết nối chỉ đọc:

```bash
rtk proxy python3 freecad_control/easy_insert_session/send.py freecad_control/inspect_connection.py
```

Sau khi đã chốt/giải quyết chênh lệch bản chính ở mục1 mới dùng quy trình mở thông thường:

```bash
rtk proxy python3 freecad_control/easy_insert_session/send.py freecad_control/resume_latest.py --timeout 60
```

`resume_latest.py` tìm theo FileName, kiểm tra hai vỏ valid/một solid, X36/Z146 rồi thay visibility/viewport; không đổi hình học hay lưu. Với file hiện tại khác bản đã chốt, không coi lệnh này là phục hồi backup hoặc xác nhận đủ21 dây.

Nếu cần kết nối lại sau khi chốt bản làm việc, macro Windows là `D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\freecad_control\restart_current.FCMacro`. Macro mở tên file chính trước khi nối; không tự dùng khi file chính đang có chênh lệch. `easy_insert_session/Connect.FCMacro` riêng có thể mở D50 nếu không có document. Không chạy lại macro nếu cầu nối đang hoạt động, không đóng/lưu document khác, nhất là cửa sổ `D36_AntiRattle_Battery_35x25x6` đã từng có thay đổi chưa lưu.

## 6. Quy tắc vận hành và sửa CAD

- Shell luôn tiền tố `rtk`. Python Linux chỉ gửi script/đọc ZIP/XML; mã CAD chạy trong FreeCAD Windows.
- Timeout không hủy request. Kiểm tra UUID inbox/outbox trước gửi lại; request đã có response không được phát lại.
- Giữ request lỗi/bị ngắt/chưa hoàn tất. Request ngắt `easy_insert_session/interrupted_requests/5b496b93493148eba884d5f52b136a9d.json` chỉ để tra cứu; không chuyển vào inbox.
- Chỉ xóa cặp request thành công sau kiểm tra response/hash; request trước, response sau. Không đưa request đã hoàn tất trong ZIP về inbox.
- Script CAD mới phải tự chứa imports/biến, không phụ thuộc globals phiên cũ. Các script lịch sử có thể phụ thuộc phiên cũ; không chạy lại.
- Trước sửa phải backup; chỉ sửa phần được yêu cầu. Trước lưu kiểm tra valid/số solid, `optimalBoundingBox(False, False)`, giao thoa liên quan và viewport; sau lưu đọc lại BRep và hash.
- Không Boolean đối chiếu toàn assembly gần giống nhau vì từng treo. `common.Volume == 0` không đủ với IP5306 dạng mặt. `removeSplitter()` chỉ dùng khi kết quả hợp lệ.
- Dùng Shaded để phân biệt cạnh chia mặt với gờ; Shaded không xóa cạnh. Đợi camera ổn định trước chụp; dùng `from pivy import coin` khi thao tác camera node.
- Chỉ tài liệu/dọn thư mục thì không sửa/lưu CAD, không xuất lại STL, không build/flash firmware. Không sửa `.gitignore`, commit/push hoặc các phần firmware/Word/repo blog.

## 7. Thư mục đã dọn, file còn giữ và khôi phục

Đã dọn **57 file ngày06/11** theo yêu cầu:15 script dùng một lần,2 ảnh thử,2 JSON trung gian và19 cặp request/response thành công. ZIP được kiểm tra CRC và SHA-256 từng file trước xóa. Giữ16 cặp lỗi/kiểm chứng thất bại và một request bị ngắt; không có request thiếu response trong danh sách kiểm kê lúc dọn.

- [CLEANUP_PLAN.md](CLEANUP_PLAN.md): danh sách dọn06/11 và mốc155 file ngày03/11.
- [HISTORY.md](HISTORY.md): các mốc thiết kế, chênh lệch file hiện tại và lịch sử dọn.
- [ZIP06/11](archive/cleanup_2026-11-06/session_cleanup.zip), [manifest06/11](archive/cleanup_2026-11-06/cleanup_manifest.json):57 file đã xóa +snapshot ba Markdown và `resume_latest.py` trước dọn; đường dẫn gốc/hash/kích thước và audit CAD.
- ZIP03/11 và manifest giữ nguyên trong `archive/cleanup_2026-11-03/`.

File vận hành giữ ở gốc: `Connect.FCMacro`, `send.py`, `inspect_connection.py`, `resume_latest.py`, `restart_current.FCMacro`. Giữ `resume_compact_d36.py`, `resume_compact_layout.py`, `resume_d50.py` để mở bản cũ khi người dùng yêu cầu, và toàn bộ macro/send/status của ba cầu nối.

Các script wiring/inspect/debug mà README trong `3D` còn liệt kê **đã chuyển vào ZIP06/11**, không còn bản rời trong `freecad_control`. Muốn tra cứu, đọc ZIP hoặc giải nén vào thư mục tạm riêng rồi đối chiếu manifest; không giải nén vào inbox, không chạy lại trên CAD hiện hành. Không xóa CAD/backup/STL/báo cáo hoặc lịch sử ngoài phạm vi `freecad_control`.
