# FreeCAD — bàn giao để tiếp tục công việc

**Cập nhật 30/10/2026, Asia/Bangkok. Chỉ cần đọc file này để khôi phục ngữ cảnh CAD.**

Người dùng đã xác nhận **bản 3D cuối có hai khung Type-C là chuẩn**, sau đó yêu cầu hoàn thiện bản vẽ kỹ thuật. Bộ bản vẽ mới nhất là **Rev C, 4 tờ A3**, đã hoàn thành. Không có yêu cầu sửa CAD nào còn đang thực hiện. Tiếp tục theo yêu cầu mới; không tự bắt đầu các việc chưa chốt bên dưới.

## 1. Quy tắc phạm vi — phải giữ ở mọi phiên sau

**Người dùng yêu cầu: chỉ sửa đúng file/phần được chỉ định.**

- Yêu cầu sửa một phần 3D: chỉ sửa phần đó trong FCStd được chỉ định. Không tự cập nhật bản vẽ, STL, STEP, ảnh, JSON, README hay các phần 3D khác.
- Yêu cầu sửa bản vẽ kỹ thuật: chỉ cập nhật bộ bản vẽ; giữ nguyên file 3D nguồn và các file xuất 3D.
- Yêu cầu sửa README này: chỉ sửa `freecad_control/README.md`. Lần cập nhật hiện tại thuộc trường hợp này.
- Việc “đồng bộ tất cả file” **không còn là quy trình tự động**. Chỉ xuất/cập nhật thêm khi người dùng yêu cầu; các hướng dẫn cũ trong README lịch sử không mở rộng phạm vi.
- Không tự sửa `.gitignore`, hoàn tác thay đổi ngoài phạm vi, commit, push hoặc xóa bản CAD lịch sử.
- Người dùng muốn thao tác trực tiếp trong FreeCAD khi yêu cầu chỉnh CAD. Không dừng ở hướng dẫn tự vẽ. Không hỏi lại các lựa chọn đã chốt về micro, SD, nút, hai lỗ trên hoặc khung Type-C.

Mọi lệnh shell phải có tiền tố **`rtk`**, theo `/home/nghung/.codex/RTK.md`. Ví dụ `rtk proxy python3 ...`, `rtk git status`, `rtk rg ...`.

## 2. Hai tài liệu hiện tại và tình trạng file xuất

Mọi đường dẫn tương đối trong tài liệu này tính từ **gốc dự án**.

### Bản 3D chính duy nhất

```text
3D/Enclosure_USB_Near_Wall_D50/Enclosure_USB_Near_Wall_D50.FCStd
```

Đây là cụm đầy đủ, **44 đối tượng**, được cập nhật tại cùng đường dẫn sau lần thêm khung Type-C. Không có bản chính mới mang tên khác. Tìm document bằng `FileName`, không dựa vào tên tab vì FreeCAD có thể thêm hậu tố.

Mốc của bản 3D đã được người dùng chốt:

| Kiểm tra | Giá trị |
|---|---|
| Vỏ | Ø50 × cao 201 mm |
| `Rear_half` | BRep hợp lệ, 1 solid, **84825,115296 mm³** |
| `Front_half` | BRep hợp lệ, 1 solid, **71811,003421 mm³** |
| Linh kiện/dây tham chiếu | 42 đối tượng còn lại giữ nguyên trong lần thêm khung Type-C |
| SHA-256 FCStd đã chốt | `15e05ccf3de00d02bb7c4a52d04653c55a4297b78dbb221761041e18c6e42a40` |

SHA này nhận diện mốc bàn giao, không phải điều kiện buộc mọi lần sửa được người dùng cho phép sau này phải giữ nguyên. Không hoàn tác sửa đổi mới chỉ vì hash khác.

### Bộ bản vẽ kỹ thuật mới nhất

Thư mục:

```text
3D/Enclosure_USB_Near_Wall_D50/Technical_Drawing/
```

| File | Nội dung |
|---|---|
| `Ban_ve_ky_thuat_Vo_tru_D50.pdf` | **Rev C, 4 tờ A3 ngang**, chữ và nét vector |
| `Ban_ve_ky_thuat_Vo_tru_D50.FCStd` | Tài liệu bản vẽ riêng, **4 trang TechDraw**; 2 shape nguồn sao chép ẩn để đối chiếu |
| `01_Tong_the.svg` | Hình chiếu, mặt cắt X0, mặt đỉnh và trục đo |
| `02_Hai_nua_vo.svg` | Phía trong hai nửa, lỗ ghép, giá gá |
| `03_Chi_tiet.svg` | Đỉnh, khe 20×3, đáy cần gạt và lỗ âm |
| `04_Khung_TypeC.svg` | Biên dạng/cắt khung Type-C, hốc đầu cáp, tọa độ hai cổng |
| `preview_01.png` … `preview_04.png` | Ảnh xem trước |
| `geometry_metadata.json` | Nguồn 3D, SHA-256, Rev C, kích thước cổng và thể tích hiện tại |
| `drawing_verification.json` | PDF 4 trang, TechDraw 4 trang, 3D nguồn không đổi, không sửa ngoài thư mục bản vẽ |

Chữ và số đã tăng **40%** theo yêu cầu; số kích thước cao **3,92 mm**. Tỷ lệ ghi theo từng hình, đơn vị mm, in ở 100% kích thước trang. Hình chiếu bố trí độc lập theo nhãn. Các kích thước là **danh nghĩa, chưa có dung sai chế tạo**. Kích thước/chú thích SVG tĩnh, không tự liên kết tham số khi CAD đổi. Hai shape ẩn trong FCStd bản vẽ chỉ là bản sao đối chiếu, **không dùng tài liệu bản vẽ làm cụm 3D để sửa**.

Hình chiếu/mặt cắt lấy từ BRep bản đã chốt; các nét chia mặt trụ thừa được lọc khi dựng bản vẽ. Biên dạng cửa Type-C phóng to dựng theo kích thước đặc trưng đã kiểm chứng của CAD, bỏ nét ghép của các trụ bo góc. Chưa ghi đủ mọi kích thước giá/rãnh nội bộ để dựng lại toàn bộ vỏ chỉ bằng PDF; khi cần chế tạo dùng kèm FCStd nguồn hiện tại.

### Những file chưa theo kịp lần thêm khung Type-C

**STL, STEP, ảnh 3D và `validation.json` trong thư mục CAD vẫn là bản xuất trước khi thêm khung Type-C.** Người dùng đã giới hạn lần sửa đó chỉ vào FCStd, nên không được xuất lại các file này. Lần hoàn thiện bản vẽ sau đó chỉ cập nhật `Technical_Drawing/`.

- Không coi `STL/Rear_half.stl`, `STL/Front_half.stl`, `Two_shell_halves.step` hiện có là bản cuối đã có khung Type-C.
- `validation.json` cũ ghi Rear **84187,632** / Front **71752,203 mm³**, STL **11848 / 11120** tam giác. Đây là mốc **trước khung Type-C**, không phải thể tích/STL hiện tại.
- `usb_before.png`, `usb_after.png`, `usb_inside_full.png`, `usb_fit.json` và các ảnh xuất 3D cũ cũng có thể chưa có khung Type-C. Dùng viewport FCStd hoặc bản vẽ Rev C để xem trạng thái cuối.
- `wire_netlist.json` vẫn mô tả các tuyến dây hiện có vì lần thêm khung không đổi dây. `button_module_spec.json` vẫn chứa các giả định phần cứng nút.
- README trong thư mục CAD có thể còn mô tả trước khung Type-C; **file bàn giao này và `Technical_Drawing/geometry_metadata.json` là căn cứ hiện tại**.

Chỉ khi người dùng yêu cầu giao file in/xuất 3D mới kiểm tra và xuất lại đúng phạm vi đó.

## 3. Mở lại để làm việc

Workspace WSL:

```text
/mnt/d/Hoc_tap_Sinh_Vien/Kien_thu_AI/Project/Duration_edge_ai
```

Thư mục Windows tương ứng:

```text
D:Hoc_tap_Sinh_VienKien_thu_AIProjectDuration_edge_ai
```

FreeCAD đã dùng: **1.1.4**, executable `C:Program FilesFreeCAD 1.1inFreeCAD.exe`. Không có FreeCAD MCP riêng; cầu nối là macro Qt timer đọc/ghi file chung Windows–WSL.

Khi có yêu cầu tiếp tục CAD, từ gốc dự án chạy lần lượt:

```bash
rtk proxy python3 freecad_control/send.py freecad_control/inspect_connection.py
rtk proxy python3 freecad_control/send.py freecad_control/resume_latest.py --timeout 60
```

`resume_latest.py` tìm/mở đúng FCStd theo đường dẫn, hiện linh kiện cùng nửa sau, ẩn nửa trước và khối thử cáp, kiểm tra sơ bộ. **Không sửa hình học hoặc tự lưu FCStd.** Kết quả đúng có `[50,201]`, SD dọc, micro đứng trên ESP, PCB nút Z130–166, hai lỗ trên theo Y/X0, hai mặt USB ở X−23; thể tích xem bảng mục 2. Đây không phải kiểm chứng bộ STL hiện có.

Để xem mặt trước đóng vỏ, hai lỗ ở giữa:

```bash
rtk proxy python3 freecad_control/send.py freecad_control/show_center_holes.py --timeout 60
```

Lệnh này cũng chỉ đổi hiển thị. Muốn xem bên trong trở lại, chạy `resume_latest.py`.

Muốn **chỉ xem bản vẽ đã lưu**, mở PDF hoặc dùng File → Open trong FreeCAD với đường dẫn FCStd ở mục 2. **Không chạy công cụ tạo lại/lưu bản vẽ chỉ để xem.**

Lưu ý hiển thị:

- Chuyển thật sang đúng cửa sổ MDI của document theo `FileName`; `App.setActiveDocument()` đơn thuần có lúc chưa chuyển tab nhìn thấy.
- Không nhầm tab `ICS43434_Module_13mm` (micro rời), cụm lịch sử hoặc FCStd bản vẽ với cụm 3D chính.
- Hai nửa vỏ hiện dùng `DisplayMode='Shaded'` để ẩn các nét chia mặt thừa. Nửa sau không refine toàn bộ được vì OCC báo `Bnd_Box is void`. **Đó là đường chia mặt CAD, không phải tất cả đều là gờ nhựa; không tự cắt bỏ thân/giá theo các đường đó.**
- Sau khi đổi shape/visibility, cần để viewport cập nhật và dùng `fitAll()` trước khi chụp. Khi đặt camera cận, đặt khoảng cắt phù hợp (đã dùng near=1, far=1000); ảnh trắng không chứng minh mô hình mất.
- Không đóng document khác hoặc lưu đè khi chưa hiểu sửa đổi chưa lưu của người dùng. `saveCopy()` có thể để document còn dấu thay đổi trong GUI dù bản sao đã được thay đúng vào file đích; kiểm tra nội dung trước khi tự lưu thêm.

Nếu mất kết nối/heartbeat:

1. `connected:true` trong status cũ không đủ. `send.py` yêu cầu heartbeat mới trong vòng 10 giây.
2. Một script CAD chạy lâu có thể chặn timer, hoặc vừa trả kết quả nhưng timer chưa kịp cập nhật. Kiểm tra lệnh đang chạy, UUID/phản hồi và heartbeat trước khi kết luận ứng dụng đã đóng.
3. Nếu macro thực sự ngừng, chạy lại macro trong FreeCAD đang mở:

   ```text
   D:Hoc_tap_Sinh_VienKien_thu_AIProjectDuration_edge_aireecad_controlConnect.FCMacro
   ```

4. Nếu ứng dụng đã đóng, mở FreeCAD và macro trên. Mở GUI qua PowerShell `Start-Process` cần quyền phù hợp của phiên; không giả định quyền từ phiên trước. Ưu tiên giữ phiên có sửa đổi chưa lưu.

## 4. Hình học đã chốt — không hỏi lại hoặc tự bố trí lại

Z hướng lên, đáy có cần gạt tại Z0, đỉnh Z201. Hai nửa chia dọc tại Y0; phía trước là +Y. Linh kiện giữ tỷ lệ 1:1.

| Hạng mục | Trạng thái cuối (mm) |
|---|---|
| Vỏ | Ø50 × 201; khoang chính Ø44 dưới Z168; vách chính 3, đáy 3 |
| Đỉnh | Vùng Z168–201 đặc ngoài khe tâm và hai lỗ; đoạn thêm Z171–201 cao 30 |
| Khe đỉnh | Chữ nhật **X20 × Y3**, tâm X0/Y0; khối cắt Z3–202, trên vật thể tới Z201; thông xuống khoang, **giữ đáy Z0–3 phía cần gạt** |
| Hai lỗ trên | Ø4 xuyên **trước–sau theo Y**, X0, Z176/Z196, cách tâm 20; không ren/hốc đầu vít/hốc đai ốc |
| Ốc ghép thân | 3 hàng mỗi bên, tổng 6 vị trí; X±21, Z14/97/166; đã bỏ hàng Z43/127 |
| Lỗ ghép | Nửa trước Ø3,4/bậc Ø6,4; nửa sau pilot Ø2,6; chưa chọn bộ vít thật |
| Pin | Tham chiếu 30×33×8; Z6–39 |
| SD | Dựng dọc, rộng 24 × cao 44,748 × dày 4; Z47–91,748; header trên |
| IP5306 | Kích thước bao 26×20×4; Z100–120; đã dịch **X−10** so với bố trí giữa cũ |
| ESP32-C3 | Sau xoay bo, bao 24×17,803×4,2; Z131–148,803; đã dịch **X−11** so với bố trí giữa cũ |
| Hai cổng USB | Cùng hướng −X, mặt đầu X−23; cùng tâm Y−5,5; sạc Z110, ESP Z139,9016; cách tâm 29,9016 |
| Khoảng lùi USB | Tại đường tâm so mặt trụ ngoài khoảng **1,387 mm**; trước khi dịch bo là 11–12 mm |
| Giá IP/ESP | Giá sau đã dời/nối vào thành cong; bỏ ngón ép trước tại vị trí bo cũ; hốc né mép PCB có vùng vách còn khoảng **1,2 mm** |
| Micro ICS-43434 | **Dựng đứng phía trên ESP**, PCB Ø13 tạm dày 1,6; tâm (0,−19,8,159); Z≈152,5–165,5; cách ESP phía dưới ≈3,719 |
| Đường âm | Thành **sau −Y**, tâm X0/Z159; 1 lỗ Ø1,2 + 6 lỗ Ø0,9 trên vòng tâm Ø2,4, đều 60° |
| Công tắc | Chìm ở đáy; tâm X0/Y16; bích Z3–3,8, thân Z3,8–11,3; nút tới Z0 |
| Hốc công tắc | Ngoài 24,2×10,2; cửa trong 13,4×6,4; hai pilot Ø1,6 tại X±9,5/Y16 |
| PCB ba nút | X±7,5 / Y17,2–18,8 / Z130–166; sát dưới vùng đặc, hở 2 |
| Lỗ bấm | 3×Ø4,6, X0, Z140/148/156; đầu nút nhô danh nghĩa 0,5 |
| Giá nút | Hai trụ Ø6,8/pilot Ø2 tại X0/Z133,163; thanh dẫn/chặn liền nửa trước; không đổi trong lần thêm Type-C |

Các thành phần xếp từ dưới lên: pin → SD → IP5306 → ESP32-C3 → micro. Mặt IC micro hướng +Y; mặt PCB có đường âm hướng −Y. Có giá micro, hai vít M2 tham chiếu, đệm cách điện và đệm âm mềm. Đệm mềm không được nhập vào nhựa in. BOOT/RESET ESP cần mở nửa trước; hai ống dẫn dụng cụ cũ đã bỏ.

### Hai khung Type-C cuối cùng

Người dùng xác nhận “bao nhựa” là **khung nhựa gắn với vỏ, ôm riêng từng cổng**, không phải đổi mô hình đầu nhựa dây cáp. Khung liền hai nửa vỏ, đã chừa mép ghép để hai nửa không chồng nhau. Hai vị trí cùng biên dạng:

| Đặc trưng | Kích thước |
|---|---|
| Cửa trong dạng con nhộng | **Z10,8 × Y5,2**, hai đầu R2,6 |
| Hốc đầu nhựa cáp | **Z13,2 × Y9,2**, bo góc R0,6 |
| Bậc cuối hốc đầu cáp | X−23,4; mặt đầu cổng tham chiếu X−23 |
| Bao phôi khung ngoài | Z16,8 × Y12,8, R2,4; được giao với mặt trụ Ø50 |

Không hiểu bao phôi là tấm nhựa phẳng nhô ra tại X−25,4: biên ngoài đã cắt theo mặt trụ, **kích thước vỏ vẫn Ø50**. Giữ nguyên vị trí/kích thước các bo, dây và 42 đối tượng tham chiếu trong lần thêm khung. Đã kiểm tra một solid hợp lệ mỗi nửa, khung không cấn các tham chiếu đã xét, đầu cáp danh nghĩa vẫn đi vào được và hai nửa không chồng lấn vượt ngưỡng.

## 5. Công cụ nào được dùng cho việc gì

| Công cụ | Vai trò / giới hạn |
|---|---|
| `Connect.FCMacro`, `send.py` | Cầu nối; file runtime trong `inbox/`, `outbox/`, `status.json` |
| `inspect_connection.py` | Đọc phiên bản và danh sách document |
| `resume_latest.py` | Mở/hiện cụm đúng đường dẫn, kiểm tra sơ bộ; không lưu CAD |
| `show_center_holes.py` | Hiện mặt trước; không xuất ảnh hoặc lưu CAD |
| `show_center_slot.py` | **Có ghi đè ảnh** `center_slot_top.png`; không tự chạy nếu chỉ được xem/sửa file khác |
| `show_usb_revision.py` | **Có ghi ảnh và `usb_fit.json`**, dựa bố trí trước khung; không dùng để xem đơn thuần hoặc làm báo cáo cuối |
| `validate_latest.py` | Kiểm tra chỉ đọc, nhưng mặc định đọc **STL đang có trên đĩa**; độ kín STL không chứng minh STL trùng FCStd hiện tại. Chưa phải bộ kiểm tra chuyên biệt hoàn chỉnh cho khung Type-C cuối |
| `export_center_holes.py` | **Ghi FCStd/STL/STEP/ảnh/JSON**; không chạy trừ khi người dùng cho phép xuất đúng các file này |
| `prepare_drawing_sources.py`, `prepare_section_details.py`, `render_technical_drawing.py`, `open_technical_drawing.py` trong `freecad_control/` | Quy trình **cũ 3 tờ / Rev B**; không dùng để cập nhật bộ 4 tờ cuối |
| `reduce_seam_screws.py`, `create_center_slot.py`, `move_usb_near_wall.py`, `refine_usb_revision.py` | Script sửa theo lịch sử; không chạy lại để mở phiên hoặc dựng lại bản đã chốt |

Các script tạm đã dùng để thêm khung Type-C nằm trong `/tmp` của phiên trước và **không phải phụ thuộc cần giữ để mở/sửa CAD**. FCStd tự chứa đầy đủ shape. Khi cần sửa tiếp, viết script tự đủ imports/biến trên các shape hiện tại; không tìm/chạy lại chuỗi dựng lịch sử.

### Chỉ khi được yêu cầu cập nhật bản vẽ

Nguồn 3D phải đang mở đúng đường dẫn. Dùng **ba công cụ trong chính `Technical_Drawing/`**, lần lượt:

```bash
rtk proxy python3 freecad_control/send.py 3D/Enclosure_USB_Near_Wall_D50/Technical_Drawing/prepare_final_drawing.py --timeout 180
rtk proxy python3 3D/Enclosure_USB_Near_Wall_D50/Technical_Drawing/render_final_drawing.py
rtk proxy python3 freecad_control/send.py 3D/Enclosure_USB_Near_Wall_D50/Technical_Drawing/open_final_drawing.py --timeout 120
```

- Lệnh 1 chạy trong FreeCAD Windows, chỉ đọc hình học nguồn và ghi nguồn bản vẽ/metadata.
- Lệnh 2 chạy bằng Python cục bộ có **PyQt5**, tạo 4 SVG, PDF và ảnh xem trước; giữ `TEXT_SCALE=1.4`.
- Lệnh 3 cập nhật 4 trang TechDraw và hai shape đối chiếu **trong tài liệu bản vẽ**, kiểm tra SHA nguồn không đổi và lưu riêng FCStd bản vẽ. Đây là lệnh ghi, không chỉ mở để xem.
- Sau khi tạo lại: rà cả bốn ảnh, PDF/TechDraw đều 4 trang, chữ không chồng, biên dạng không mất nét bao. Các nét chia mặt trụ có thể trùng nét cấu tạo ở độ sâu khác; không lọc mù toàn bộ nét và làm mất đường bao hoặc giá bên trong.
- Chỉ sửa bộ bản vẽ; không tiện tay xuất lại STL/STEP hoặc lưu 3D nguồn.

## 6. Cách sửa CAD an toàn và giữ đúng phạm vi

Script gửi qua cầu nối chạy **trong Python FreeCAD Windows**, có `App`, `Gui`; tự import `Part`, `Mesh` khi cần. Không chạy script CAD bằng Python Linux trực tiếp.

```bash
rtk proxy python3 freecad_control/send.py /tmp/TEN_SCRIPT_TU_DU.py --timeout 120
```

Đường dẫn script đầu vào được `send.py` đọc ở WSL rồi gửi nội dung, nên script tạm `/tmp/...` dùng được. Bên trong script CAD phải dùng đường dẫn Windows khi đọc/ghi dự án. Trả kết quả JSON qua biến `result`.

Các đối tượng ổn định:

```text
Rear_half, Front_half, Battery, MicroSD, IP5306, ESP32_C3, SW1
Mic_PCB, Mic_ICS43434, Mic_Pads, Mic_Passives, Mic_Acoustic_Gasket
Key_PCB, Key_Mount_Rings, Key_Pads
Key_Case_1..3, Key_Body_1..3, Key_Stem_1..3, Key_Leads_1..3
Key_Screw_55, Key_Screw_85
Charge_plug_envelope, Code_plug_envelope
```

Hai tên vít `Key_Screw_55/85` là tên lịch sử; vị trí thật Z133/163. Không suy tọa độ từ tên.

Trình tự cho một yêu cầu sửa mới:

1. Xác định đúng phạm vi và đúng `FileName`; giữ sửa đổi chưa lưu. Không dựng lại từ đầu.
2. Ghi nhận trạng thái các phần ngoài phạm vi (shape/placement hoặc hash file khi phù hợp).
3. Sửa đúng vùng yêu cầu bằng script tự chứa. Không phụ thuộc biến `doc`, `rear`, `OUT` hoặc hàm còn sót trong namespace phiên trước.
4. Kiểm tra phù hợp thay đổi: BRep hợp lệ, số solid, BoundBox, thể tích đủ thân; giao thoa/đường cắm cáp/đường âm nếu liên quan. Xem viewport thật.
5. Chỉ lưu file được phép; không tự xuất các định dạng khác hoặc cập nhật tài liệu. Khi cần chỉ thay một FCStd, đã dùng `saveCopy()` ra file tạm rồi thay đúng file đích để không xoay/ghi đè các backup khác; không để lại file tạm trong dự án.
6. Đối chiếu các phần/file ngoài phạm vi không đổi, mở đúng tab cho người dùng.

Lỗi hình học đã gặp:

- `isValid()` và “1 solid” chưa đủ: từng có lỗi fuse làm mất thân, chỉ còn giá ≈444 mm³. Luôn kiểm tra kích thước/thể tích, không bỏ assertion để ép xuất.
- `removeSplitter()` trên nửa sau có thể báo **`Bnd_Box is void`** dù shape ban đầu hợp lệ. Không sửa toàn bộ hình học chỉ để xóa nét. Bản cuối giữ shape hợp lệ và dùng Shaded; bản vẽ xử lý nét riêng trên dữ liệu bản vẽ.
- Boolean của các shape gần trùng nhau có thể tạo kết quả rỗng hoặc topology suy biến. Khi tính thể tích giao/hiệu, kiểm tra `isNull()`/`Solids` trước; đọc lỗi để phân biệt lỗi phép kiểm tra với giao thoa thật. Không nâng ngưỡng hoặc bỏ kiểm tra để ép đạt.
- Khi dịch đối tượng, cộng độ dịch vào placement đang có; không gán placement mới làm bo về gốc. Không thu nhỏ bo để vừa vỏ.

### Hàng đợi và timeout

Macro chạy trên GUI thread; không thêm vòng chờ chặn GUI. **Timeout không hủy lệnh**: lệnh có thể đang chạy hoặc vẫn chờ trong hàng đợi. Xác định UUID và đọc phản hồi tương ứng trước khi gửi lại lệnh tạo/sửa hình.

**Không xóa riêng `outbox/` khi vẫn giữ `inbox/` và macro đang chạy.** Yêu cầu không còn phản hồi cùng UUID có thể bị coi là chưa xử lý và chạy lại. Không xóa hàng đợi để “reset” một script timeout.

## 7. Điện và các việc chưa chốt

Đây là thông tin bàn giao, **không phải yêu cầu tự triển khai**.

| Phần | Trạng thái |
|---|---|
| Nguồn | Pin 3,7 V/800 mAh → IP5306; OUT+ qua SW1 tới ESP 5V/VBUS và SD VCC; GND chung |
| Sạc | Người dùng xác nhận USB-C; chưa chốt dòng sạc và đo bo/cáp thật |
| SD | Xác nhận module VCC/5 V có ổn áp; mức logic 3,3 V vẫn cần xác nhận |
| Dây | 11 tuyến nguồn/GND/SPI tham chiếu; tọa độ/chiều dài ở `wire_netlist.json` trong thư mục CAD chính |
| SPI đề xuất | SCK GPIO4, MOSI GPIO6, MISO GPIO5, CS GPIO7 |
| Nạp code | USB-OFF trước khi nối PC; rút USB trước khi RUN, cách ly thủ công |
| Micro I²S | Chưa thêm dây, chưa chốt GPIO/firmware; không báo đã đấu xong |
| Ba nút | Mới là cơ khí; chưa đi dây/chốt GPIO/chức năng. PCB 36×15, các số còn lại như dày PCB 1,6, switch 6×6, bước 8, lỗ PCB Ø3,2 cách 30, tổng dày 8,3 là giả định |
| Micro | Ø13 theo ảnh; PCB dày 1,6, pad và lỗ âm giữa bo còn là giả định |
| Công tắc | Vỏ tham chiếu 12,6×6×7,5; bích 23, hai vít cách 19; chưa chọn mã thật |
| Chế tạo | Chưa chốt vật liệu/dung sai/co ngót/vít/độ nén đệm, chưa in/lắp/thử điện/lực/rung/âm học |

`firmware/sdkconfig` tại lần bàn giao vẫn **`CONFIG_IDF_TARGET="esp32s3"`**, trong khi CAD dùng **ESP32-C3 SuperMini**. Chưa chuyển/nạp firmware C3; không flash binary S3 sang C3. Hình học đỉnh đặc không tự đặt infill; khi được yêu cầu chuẩn bị in phải cấu hình vùng đỉnh phù hợp trong slicer.

## 8. File cục bộ và lịch sử

- `3D/` và `freecad_control/` bị `.gitignore` bỏ qua, hiện tồn tại cục bộ trên máy này. Clone Git mới không tự có CAD/cầu nối; giữ/sao lưu hai thư mục khi chuyển máy.
- Các bản `Enclosure_Center_Slot_D50`, `Enclosure_Three_Seam_Screws_D50`, `Enclosure_Center_Holes_D50` là mốc trước. Các bản Face/Mount_Holes khoan theo X là cách hiểu đã bị sửa, không dùng tiếp.
- Các bản SD ngang, micro ngang (`Enclosure_With_ICS43434`), các cụm clamshell cũ và module micro/nút riêng đều là lịch sử/tham chiếu. Không mở mặc định hoặc dựng lại thay cho bản chính.
- Đã dọn `freecad_control/` ngày 29/10/2026, xóa 86 file thử/tạm và `iterations/`; không cần phục hồi chuỗi đó để sửa FCStd hiện tại. Không tự dọn tiếp các bản trong `3D/`.
- Có các thay đổi Git ngoài CAD từ trước; kiểm tra trạng thái mới khi thực sự cần, không hoàn tác chúng theo README này.
- Dự án dùng tiếng gõ trái cây để phân loại độ chín; AI ở `src/`, `models/`, `notebook/`, `ONNX/`, firmware ở `firmware/`. Không cần đọc README gốc hoặc lịch sử chat để tiếp tục CAD.

**Điểm bắt đầu phiên sau:** đọc tài liệu này → tuân thủ phạm vi người dùng yêu cầu → khi cần thao tác CAD, kiểm tra kết nối và mở đúng FCStd ở mục 3 → làm trên trạng thái cuối đã có, không chạy lại script dựng lịch sử.
