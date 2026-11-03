# FreeCAD — bàn giao hiện tại

Cập nhật **03/11/2026, Asia/Bangkok**. Đây là tài liệu khôi phục ngữ cảnh CAD chính, tự chứa đường dẫn bản đang làm, yêu cầu đã chốt, kết nối và phần chưa hoàn thành. Chỉ đọc README của bản CAD khi cần chi tiết; không cần README gốc dự án.

### Thay đổi mới: vít âm và đai ốc

**Đã xuất STL D36 ngày03/11/2026 theo yêu cầu:** trong thư mục bản CAD `Print_2026-11-03/`, hai file `D36_Front_half_2026-11-03.stl` và `D36_Rear_half_2026-11-03.stl`. Chỉ xuất hai vỏ đã gia cố, không xuất vít/đai ốc/linh kiện. STL binary, tọa độ lắp, dùng mm khi import, chưa đặt hướng in. Đã đọc lại hai STL closed solid, X36/Z146; thể tích lệch BRep dưới0,12%. Có `validation.json` và README trong thư mục xuất. Nguồn CAD hash `30ffa569b3b1985c07a908fed7001bee70d0980014a19a7e67fb60a15af345c7` giữ nguyên; không sửa CAD trong lần xuất. Những ghi chú “chưa xuất STL D36” bên dưới là lịch sử. Chưa slicer/G-code/profile/in thử.

**Mới nhất — gia cố gờ sẵn ở cả hai nửa:** người dùng xác nhận gia cố các gờ hiện có, không thêm bốn thanh pin mới vào nửa trước. Nửa sau: hai thanh đỡ pin tăng bề dày lưng từ0,8 lên1,6 mm (mặt đỡ pin Y−4,624074 giữ nguyên, thêm về lưng), bề rộng theo Z từ4 lên5,2 mm; hai thanh chặn đầu tăng từ0,8 lên1,6 mm về phía ngoài pin. Chân thanh kéo ra cả hai cạnh, cắt theo trụ R16,8 để nhập vào vách. Nửa trước: mở rộng chân gờ SD/bo nút/ESP ra vách; nửa sau gia cố chân IP5306 và phần đế dưới ngàm micro một đầu. Không thêm ngàm bên/trên micro, không thêm TPU hoặc hốc cũ. Giữ nguyên mặt hướng linh kiện, kích thước/placement 25 phần linh kiện và sáu phần vít.

Đã lưu và đọc lại BRep: hai vỏ valid/mỗi nửa một solid, X36/Z146, giao thể tích hai nửa0. Phần thêm có khoảng hở với linh kiện tối thiểu trên0,19 mm (kiểm tra hộp bao loại trừ hoặc khoảng cách hình học cục bộ), không cấn. 31 objects ngoài vỏ giữ nguyên payload hình học/placement trong sai số số học. Front/Rear hiện **29340,783389 / 30828,065379 mm³**; tổng33 objects. Chưa thử in/lắp, lực giữ/độ bền/đường lắp. Backup/validation/ảnh trong `Reinforced_Frame/`: `D36_before_reinforcing_frame.FCStd`, `validation.json`, `reinforced_frame.png`. Hash hiện hành `30ffa569b3b1985c07a908fed7001bee70d0980014a19a7e67fb60a15af345c7`. Các hash/thể tích bên dưới là mốc trước gia cố.

**BẢN HIỆN HÀNH — ba vít M3 thẳng hàng, vỏ Ø36×146 mm:** theo yêu cầu mới, bỏ vít M2 lệch cạnh và dùng `Screw_M3_Lower`/`Nut_M3_Lower`, giống hai bộ cũ (M3×30, đầu Ø5,5×3, đai ốc AF5,5×2,4). Cả ba tâm X0; Z18/121/141. Lỗ xuyên mới Ø4, hốc đầu Ø6,2/mặt tựa Y13, hốc đai ốc AF5,9/mặt tựa Y−14,1. Đã bỏ cả lỗ/trụ M2 bên cạnh, không để lỗ thừa.

Kéo dài thân **10 mm tại Z13**, thành Z0…146; thêm đoạn thành trụ và hai trụ siết bán kính 4,5 mm quanh vít dưới, gặp tại Y0. Giữ nguyên công tắc `SW1`/`SW1_Terminals` và cửa đáy. Pin, bo, micro, nút bấm, gờ/cửa phía trên và hai bộ vít cũ **dịch +10 mm theo Z**, không đổi kích thước hoặc xoay; đây là thay đổi placement được thực hiện để chừa chỗ cho vít giữa thân. Khoảng cách tương đối cụm linh kiện phía trên giữ nguyên. Pin nay Z26,5…61,5; SD bắt đầu Z25. Không còn TPU/preview/R/C rời/LED như các bản đã loại.

Đã lưu và đọc lại BRep: hai vỏ hợp lệ/mỗi nửa một solid, X36/Z146, không giao thể tích nhau. Hai chi tiết vít mới hợp lệ; trụ/vít mới không giao linh kiện gần đó. Trụ cách thân công tắc 2,2 mm, chân công tắc khoảng 1,562 mm; ngàm/trụ phía trước cách microSD khoảng 2,995 mm. Front/Rear hiện **29107,368581 / 29796,112526 mm³**. Có 33 objects: 25 phần linh kiện + hai vỏ + sáu phần kim loại. Chưa kiểm chứng lực siết/độ bền/dung sai in; dây cần tính thêm khoảng dài mới, chưa có mô hình dây.

Hash hiện hành `619f3dc734b3df2f37cabc75dc37719e4f66d8b9e6139f34a8b639c7d3f8e8f7`. Backup/validation/ảnh tại `Centered_Lower_M3/`: `D36_before_centering_lower_M3.FCStd`, `validation.json`, `three_aligned_M3.png`. `resume_latest.py` kiểm tra chiều dài146 và hiện ba bộ M3. **Tất cả các đoạn mô tả M2, chiều dài136, tọa độ linh kiện và hash trước mốc này ở dưới là lịch sử; không chạy lại các script chỉnh sửa cũ trên bản146.**

**Mới nhất — thêm một vít thân dưới:** có thêm `Screw_M2_Lower` + `Nut_M2_Lower`, tâm X14/Z8,5 mm, trục Y, lệch cạnh gần đầu công tắc để tránh pin/microSD/công tắc. Mô hình M2×14, đầu Ø3,8×2; đai ốc AF4×1,6. Lỗ mới Ø2,4; hốc đầu Ø4,4, mặt tựa Y6/đỉnh đầu Y8; hốc lục giác AF4,4, mặt tựa Y−6/đai ốc ngoài Y−7,6, mũi vít Y−8. Hai trụ đỡ liền vỏ ở X11,8…18, Z5,3…12,7, cắt theo trụ ngoài Ø36 và gặp nhau tại Y0, tạo mặt tựa siết. Đầu vít/đai ốc nằm trong bao Ø36; hai bộ M3 cũ giữ nguyên. Tổng **33 objects** (25 linh kiện, hai vỏ, sáu phần vít/đai ốc).

Đã kiểm tra và đọc lại BRep: hai vỏ và hai phần kim loại mới valid/mỗi shape một solid; X36/Z136 giữ nguyên; hai vỏ không giao thể tích, phần thêm và vít mới không giao linh kiện. 29 objects ngoài vỏ cũ giữ nguyên BRep/placement trong dung sai số học. Front/Rear hiện **27468,523031 / 28130,064493 mm³**. Chưa thử lực siết/độ bền/dung sai thực; không khẳng định đã đạt độ chắc thực tế. Backup, validation, ảnh tại `Lower_Screw/`; backup `D36_before_lower_screw.FCStd`. Hash hiện hành `bee2ff22cb01aa04f679200bfce8ebc85b09d84d4877cbd65f36121131497469`. `resume_latest.py` hiện cả vít dưới. Các trạng thái/hash bên dưới là lịch sử.

**Mới nhất — đơn giản hóa các hốc/bậc nhỏ trên gờ:** đã lấp 8 hốc chèn TPU của SD/IP5306/ESP32/bo nút và 2 khe chữ nhật gài TPU trên thanh đỡ pin (Z22–26, Z44–48). Không thêm lại TPU. Giữ các gờ đỡ lớn, ngàm micro một đầu, lỗ/cửa vỏ, 25 phần linh kiện và 4 phần vít/đai ốc đúng vị trí. Hai vỏ hợp lệ/mỗi nửa một solid, X36/Z136 và giao thể tích hai nửa 0. Front/Rear mới: **27343,764920 / 28013,129980 mm³**. Phần bù không giao thể tích linh kiện; không chứng nhận lực giữ sau bỏ chèn mềm. `removeSplitter()` thử trên kết quả nhưng không hợp lệ nên không áp dụng; dùng Shaded để ẩn đường chia mặt dư, không gọi đó là đã xóa hết cạnh hình học.

Đã lưu; hash hiện hành `bb83f0192886a09299253ac236a74d0128066ab66a06e7513efc025a00125253`. Backup và kiểm chứng trong `Simplified_Holder_Steps/D36_before_simplifying_holder_steps.FCStd`, `Simplified_Holder_Steps/validation.json`. Đọc lại BRep sau sửa hợp lệ, 29 objects ngoài vỏ giữ nguyên hình học/placement. Các số liệu/hash bên dưới là mốc trước đơn giản hóa.

**Hiện trạng mới nhất — thêm lại linh kiện được chọn:** người dùng yêu cầu thêm ESP32-C3, mạch sạc IP5306, pin 35×25×6, ba nút bấm (cả PCB/phần thân/chân), micro ICS43434 (PCB/IC/pads/passives), mạch đọc microSD và công tắc gạt/chân. Đã phục hồi đúng 25 objects từ `Shells_Only/D36_before_removing_components.FCStd`, giữ nguyên hình học/placement; file hiện có **31 objects** gồm 6 vỏ/vít/đai ốc và 25 phần linh kiện. Đã lưu, đối chiếu BRep/placement của tất cả với nguồn và đọc lại BRep hai vỏ/bốn chi tiết vít. Không có TPU vàng/cam, R/C rời, LED, đệm micro hoặc link xem tách. Vỏ vẫn ghép kín, vít ở vị trí siết; linh kiện có Visibility=True bên trong vỏ đặc, muốn xem nội thất có thể tạm ẩn một nửa vỏ khi được yêu cầu. `resume_latest.py` đã cập nhật bộ linh kiện này.

**Hash hiện hành:** `2bc4723989299fdd2c23402208f817c70cc99e7867ae74b3ce98b5318b2d56b9`. Báo cáo `Selected_Components/validation.json`; backup trước phục hồi `Selected_Components/D36_before_restoring_components.FCStd`. Các mốc “chỉ 6 objects” hoặc “ẩn linh kiện” bên dưới đã được thay thế; không dùng làm trạng thái hiện tại.

**Yêu cầu mới nhất — đã xóa hẳn phần thừa:** file CAD hiện tại chỉ còn **6 objects**: `Front_half`, `Rear_half`, `Screw_M3_1/2`, `Nut_M3_1/2`, ở tọa độ lắp kín. Đã xóa 45 objects: toàn bộ bo/pin/micro/trở/tụ/LED/công tắc, TPU vàng/cam và mọi link `Preview_*`; không chỉ ẩn nữa. Giữ nguyên hình học và placement của hai vỏ + bộ vít. Các gờ đã nhập liền trong vỏ vẫn giữ nguyên, không khoét bỏ thêm. `resume_latest.py` đã bỏ kiểm tra pin/micro và mở đúng bản khung lắp. Không chạy các script build/validate cũ đòi linh kiện hoặc preview.

**Hash hiện tại:** `c8f3a7a0ce3f2f3cf0dcebbbe61b69571a4a953ed910a48e742444edeb2ce042`. Đã đọc lại BRep 6 objects: hợp lệ/mỗi shape một solid, payload và placement trùng trước xóa. Báo cáo `Shells_Only/validation.json`; backup đầy đủ trước xóa `Shells_Only/D36_before_removing_components.FCStd` trong thư mục bản CAD. Các bản CAD thử/backup cũ trên đĩa là lịch sử, chưa xóa thư mục. Những mô tả linh kiện/TPU/preview bên dưới chỉ còn là ngữ cảnh trước khi dọn, không phải object còn trong file đang làm.

Đã lưu chế độ xem: hash hiện tại `9dd43fd3ca4a54ffb6284ba711f975aa85fc52bf76e002d2c37e417bf7eb44ed`. `Assembled_View/validation.json` đối chiếu 55 payload BRep (cả payload link), chỉ thay đổi cờ OCC Checked ở TPU, không đổi dữ liệu hình học; placement giữ nguyên, đúng 6 object được hiện. Backup `Assembled_View/D36_before_clean_assembled_view.FCStd`; ảnh `Assembled_View/assembled.png`. Các hash bên dưới là các mốc trước khi lưu chế độ xem mới.

Người dùng yêu cầu giữ nguyên hai lỗ Ø4 tại X0/Z111 và Z131, thêm đầu vít âm nửa trước và hốc đai ốc lục giác nửa sau. Mô hình chọn hai bộ M3 × 30, đầu Ø5,5 × 3, đai ốc AF5,5 × 2,4; hốc đầu Ø6,2/mặt tựa Y13, hốc đai ốc AF5,9/mặt tựa Y−14,1. Đây là ngoại lệ mới cho vít ghép vỏ kim loại; các chi tiết giữ linh kiện vẫn chỉ in 3D. Hốc chống xoay đai ốc, chưa giữ chống rơi trước khi bắt vít. Chưa thử dung sai, lực siết hoặc độ bền thực.

Xem `Printed_Retention_35x25x6/Recessed_Fasteners/README.md`, backup và `validation.json` trong cùng thư mục. Các bảng thể tích, số object và hash ở bên dưới là **mốc trước sửa vít**, không dùng làm giá trị mới. `Screw_M3_1/2`, `Nut_M3_1/2` là mô hình kim loại tham chiếu không xuất in; `Preview_Screw_*`/`Preview_Nut_*` chỉ để xem. `resume_latest.py` đã bao gồm các link mới.

**Đã lưu và đọc lại BRep sau khi khởi động lại FreeCAD:** 51 objects; Front / Rear lần lượt 27333,204889 / 27993,369980 mm³, hợp lệ/mỗi nửa một solid, kích thước X36/Z136 giữ nguyên. Hai vít và hai đai ốc hợp lệ/mỗi shape một solid; kiểm tra trước lưu không giao thể tích với vỏ hoặc linh kiện. 37 shape tham chiếu (33 linh kiện + 4 trạng thái TPU) giữ placement và dữ liệu hình học; khi lưu chỉ có sai số số thực tối đa 2,23e−16 và cờ OCC Checked của vài shape. Hash CAD hiện tại: `3c87ee038f4f9b5eae777aa50bce0a2f4947532d3290d6675086774980ce3424`. Ảnh: `Recessed_Fasteners/fasteners.png`.

Phiên trước bị treo trong `finish_recessed_fasteners.py` do Boolean đối chiếu hình giống nhau; **không chạy lại script đó**. Đã khởi động lại đúng bản trên đĩa, dựng/lưu lại và kiểm tra bằng `validate_saved_fasteners.py` (đọc BRep, optimal bounds, token hình học và placement, không Boolean đối chiếu toàn linh kiện). Request bị ngắt đã chuyển sang `easy_insert_session/interrupted_requests/5b496b93493148eba884d5f52b136a9d.json`, không phát lại. Cầu nối hiện đã hoạt động lại. `restart_current.FCMacro` mở đúng D36 trước khi nối cầu; không cần chạy lại khi đã kết nối.

## 1. Bản CAD đang tiếp tục

**Chỉ tiếp tục:**

```text
3D/Enclosure_Compact_Layout_D36/Printed_Retention_35x25x6/D36_Printed_Retention_35x25x6.FCStd
```

Dùng `freecad_control/resume_latest.py`. Script trỏ đúng bản này, chọn document theo FileName, kiểm tra hai nửa vỏ và bộ vít; chỉ mở/hiện, không đổi hình học hoặc lưu. Không mở bản nền pin cũ bằng `resume_compact_d36.py` để tiếp tục thay cho bản mới; không dựng lại từ script lịch sử.

| Mục | Trạng thái hiện tại |
|---|---|
| Vỏ | Ø36 × 146 mm; vách 2 mm, đáy 3 mm; khoang Ø32, hai nửa chia theo Y0 |
| Trục | +Y là trước; Z dọc thân |
| Pin mới | **35 × 25 × 6 mm**: dài 35 theo Z, ngang 25 theo X, dày 6 theo Y; giữ tâm pin cũ |
| Bao pin | X±12,5; Y−3,824074…2,175926; Z26,5…61,5 mm |
| Micro | PCB Ø13, dày 1,6 mm; IC mô hình cao 2 mm theo Y, không phải nâng vị trí Z |
| Linh kiện | 25 phần mô hình được chọn; công tắc giữ đáy, các phần khác dịch Z+10 ở mốc146 |
| Vỏ để sửa/xuất sau này | `Front_half`, `Rear_half`, ở tọa độ ghép |
| Thể tích Front / Rear | 29340,783389 / 30828,065379 mm³ |
| Giữ linh kiện | Chỉ chi tiết in 3D; gờ/chặn cứng và khay/chèn TPU cũng in 3D; không keo, mút hoặc băng dính |
| Vật liệu | Vỏ/gờ nhựa cứng chưa chọn mác/profile; ba bộ vít/đai ốc kim loại; đã bỏ toàn bộ TPU |
| Document đã lưu | 33 objects: hai vỏ, sáu phần vít/đai ốc, 25 phần linh kiện; không có preview |

IC micro 2 mm là kích thước mô hình theo yêu cầu người dùng, không phải xác nhận kích thước vật thật từ datasheet. Không tự sửa kích thước linh kiện khác để ép vừa.

## 2. Các yêu cầu giữ đã chốt

- **Pin:** bỏ khay cứng rời và hai mỏ nửa trước che mặt bo SD. Nửa sau có đỡ lưng/cạnh/chặn đầu. Khay TPU một chi tiết liên tục gồm hai vòng kín ôm pin, hai chân đàn hồi đầu mũi tên gài qua khe trên thanh đỡ lưng nửa sau. Không dùng bo SD làm mặt ép pin. Lực gài/nhả, độ bền chân và lực giữ chưa thử.
- **SD:** chỉ còn **hai giá góc đối diện**. Hai gờ lớn đã bỏ thực tế từng giữ pin bên dưới, không phải thêm hai giá SD. Không tự thêm lại chúng. Hình bao khay TPU đã lắp cách SD khoảng 1,7 mm theo báo cáo lần sửa SD.
- **Micro:** chỉ giữ **một đầu dưới** bằng một ngàm chữ U rộng 4 mm. Đã bỏ hai gờ cạnh, chặn trên và hai miếng chèn TPU riêng của micro. Không tự thêm lại các gờ này. Khoảng cách ngàm–PCB nhỏ nhất khoảng 0,2278 mm, ngàm–IC khoảng 3,2524 mm theo báo cáo lần sửa micro; lực giữ/chống xoay chưa thử.
- Các bo còn lại dùng gờ/chặn và **8 miếng chèn TPU** trong hốc: SD, IP5306, ESP32, bo nút. Không còn 10 miếng như mốc trước khi sửa micro.
- Người dùng ưu tiên đơn giản, ít gờ và in nhanh, đồng thời muốn cầm/gõ không lung lay hoặc phát tiếng. **Đây là mục tiêu, chưa phải kết quả thử nghiệm đã đạt.** Không tự dùng lại keo/mút của các phương án đã loại.

## 3. Phân biệt hình để in và hình xem

| Object | Vai trò |
|---|---|
| `Front_half`, `Rear_half` | Hai nửa nhựa cứng, ở tọa độ ghép |
| `TPU_Battery_Print` | Khay TPU ở trạng thái tự do, có phần dư danh nghĩa 0,15 mm tại mặt giữ |
| `TPU_Board_Print` | 8 miếng chèn TPU đã trải phẳng, dày tự do 0,95 mm |
| `TPU_Battery_Installed`, `TPU_Board_Installed` | Hình bao danh nghĩa khi lắp, không xuất lặp để in |
| `Preview_Rear_Separated`, `Preview_Front_Separated` | Hai link xem vỏ tách rời; không xuất |
| `Preview_TPU_Rear`, `Preview_TPU_Front` | Hình preview TPU tách rời; không xuất |
| `Battery` và mô hình linh kiện | Chỉ tham chiếu, không xuất làm chi tiết in |

TPU tự do có phần dư/giao hình học có chủ đích với vị trí linh kiện danh nghĩa. Trạng thái Installed chỉ biểu diễn hình bao tiếp xúc, không phải mô phỏng biến dạng hoặc đo lực ép. Chưa chọn độ cứng TPU, chưa chứng nhận lực lên túi pin hoặc khả năng in các chèn nhỏ.

Xem lắp kín: ẩn toàn bộ `Preview_*` và `TPU_*_Print`, hiện hai source halves, linh kiện và `TPU_*_Installed`. Tọa độ source là vị trí lắp chuẩn. Không đổi placement source để tạo ảnh tách rời.

## 4. Kiểm chứng và file bằng chứng

Thư mục bản hiện tại, gọi tắt là `Printed_Retention_35x25x6/`, có:

- `README.md`, `validation.json`: mô tả và báo cáo tổng hợp qua các mốc; đọc kèm mục hash bên dưới vì file đã được lưu lại sau lần kiểm chứng micro.
- `Micro_Single_End/validation.json`, `micro_single_end.png`: bằng chứng mới nhất về ngàm micro một đầu.
- `Micro_Single_End/D36_before_single_mic_holder.FCStd`: backup ngay trước sửa micro.
- `SD_Simplification/validation.json`, `before_view.png`, `after_view.png`: mốc bỏ hai mỏ che SD; hình SD vẫn đúng, hash/thể tích tại đó là mốc trước sửa micro.
- `SD_Simplification/D36_before_SD_simplification.FCStd`: backup trước sửa SD.
- `printed_retention.png`: ảnh trước hai lần bớt gờ, **không phải ảnh hình học mới nhất**.

**SHA-256 file CAD hiện trên đĩa, đối chiếu 03/11/2026:**

```text
349c2d71d5c2dbf4118c3a814c9b8fc557363a5af1dc74f31185ab2cc72a9f88
```

Hash trong báo cáo lần sửa micro là `95bbb6c34e87768e8bd8fb221eaff9276b615f4fd7f7b5ee2d960ff9f8321e07`; không dùng nó làm hash file hiện tại. Lần rà soát tài liệu này không sửa CAD hoặc các JSON đó. Toàn bộ payload BRep và thuộc tính document của CAD hiện tại trùng với `D36_Printed_Retention_35x25x6.20261102-192014.FCBak` đi kèm; hash FCBak cũng khác mốc báo cáo micro, nên không chỉ dựa vào so sánh backup để suy ra lịch sử lưu.

Đã **đọc trực tiếp BRep trên đĩa qua FreeCAD Windows ngày 03/11**: hai nửa hợp lệ, mỗi nửa một solid, giao thể tích 0; X36/Z136 và thể tích khớp bảng trên. Pin XYZ25/6/35; PCB micro dày 1,6, IC cao 2 mm. Hai trạng thái khay TPU hợp lệ/mỗi shape một solid; hai bộ chèn TPU hợp lệ/mỗi bộ 8 solids. Đây là kiểm tra đọc, không sửa/lưu document hoặc đổi viewport. Các khoảng hở chi tiết và việc giữ nguyên 33 linh kiện ở trên được dẫn từ báo cáo lần sửa tương ứng, không phải đo lại đầy đủ hôm nay.

Hash hoặc ZIP mở được không đủ chứng minh hình học. Khi sửa/lưu tiếp phải kiểm tra lại BRep, vị trí và các giao thoa liên quan; không coi kết quả static là chứng nhận lực giữ hoặc độ ồn thực tế.

## 5. Những việc chưa hoàn thành

- Ngàm/mối ghép hai nửa vỏ chưa hoàn thiện; độ rơ của vỏ chưa kiểm chứng.
- Chưa in/lắp thử, chưa thử cầm/lắc/gõ, lực giữ/nhả, chống xoay micro, độ bền chân gài TPU, độ dày/độ cứng chèn hoặc lực lên pin.
- D36 chưa có tuyến dây; không mang nguyên dây D50 sang. R/C, dây và chân LED cần cách điện/giữ cơ khí phù hợp yêu cầu chỉ in 3D; chưa xác nhận hết tiếng do dây hoặc công tắc/LED.
- Chưa kiểm tra đầy đủ đầu cáp, tháo SD, anten ESP32, nhiệt, đệm âm, đường lắp và dung sai thực. Cửa USB/nút/LED/micro vẫn là cấu hình thử.
- **Đã xuất hai STL D36 trong `Print_2026-11-03/`**; chưa G-code, profile máy/vật liệu/hướng in/support hoặc chạy slicer. Ước lượng trao đổi **4–7 giờ cả bộ** từ mốc cũ không áp dụng làm thời gian slicer cho bản146/gờ gia cố mới.

Không tự triển khai dây/firmware, xuất in hoặc hoàn thiện các mục trên khi chưa được yêu cầu. Lần cập nhật tài liệu này chỉ sửa Markdown trong `freecad_control`, không thay hình học.

## 6. Kết nối FreeCAD Windows

Mọi lệnh shell có tiền tố `rtk` theo `/home/nghung/.codex/RTK.md`. **Không chạy CAD bằng Python Linux.** Cầu nối sử dụng: `freecad_control/easy_insert_session/`.

```bash
rtk proxy python3 freecad_control/easy_insert_session/send.py freecad_control/inspect_connection.py
rtk proxy python3 freecad_control/easy_insert_session/send.py freecad_control/resume_latest.py --timeout 60
```

`send.py` chỉ nhận khi heartbeat dưới 10 giây. Luôn kiểm tra trạng thái mới; không suy đoán phiên hiện tại từ PID/log hoặc thông tin phiên cũ. Giữ cả ba cầu nối gốc, `easy_insert_session`, `open_tray_session` và inbox/outbox của chúng; không tự đổi cầu nối hoặc đóng/lưu document khác.

Nếu mất kết nối, chạy macro trong đúng phiên FreeCAD Windows:

```text
D:\Hoc_tap_Sinh_Vien\Kien_thu_AI\Project\Duration_edge_ai\freecad_control\easy_insert_session\Connect.FCMacro
```

Sau kết nối vẫn chạy `resume_latest.py`: macro có thể mở D50 nếu chưa có document. FreeCAD quan sát: 1.1.4; chương trình `C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe`.

**Timeout không hủy request.** Theo dõi đúng UUID trong inbox/outbox trước khi gửi lại; không chạy trùng lệnh. Script sửa mới phải tự chứa imports/biến, không phụ thuộc globals phiên trước. Tránh Boolean toàn bộ assembly gần giống nhau hoặc lấy mẫu nặng trong GUI; ưu tiên kiểm tra cục bộ, dùng báo cáo có sẵn.

## 7. Các bản cũ và file in D50

| Bản | Vai trò và lệnh mở |
|---|---|
| D36 pin mới, `Printed_Retention_35x25x6/` | Bản đang phát triển; **`resume_latest.py`** |
| D36 nền `Compact_Layout_D36.FCStd` | Mốc 23 cụm giá/pin cũ, giữ lịch sử; `resume_compact_d36.py` |
| D36 `Trial_Minimal_Pads/` | Thử kê/dán đã bỏ; không tiếp tục hoặc phục hồi keo |
| D36 `Trial_Battery_Tray/` | Thử khay cứng rời đã thay thế |
| D36 `Trial_AntiRattle_Battery_35x25x6/` | Phương án mút/keo đã bị loại; không tiếp tục |
| D40 Ø40 × 136 | Bố trí tham khảo; `resume_compact_layout.py` |
| D50 Ø50 × 201 | Bản cũ đã có STL; `resume_d50.py` |

Các bản nền/D40/D50 giữ nguyên. D36 nền hash `49549ee09ea2b058d56a3db4cff2dbe2cc842359dfaaeab47dec5d9e3b09c498`; D40 `29c446de8c4d00ce937945e86075882f413ff5f981203fb38a22d5951fba8846`; D50 `cdf62dd5dd87bdf6eeec679989cedda4f531a9f0fe1f7feaa2a1dd9042abaf82` là các mốc đã ghi trước đây, không đo lại trong lần cập nhật này. Các số giảm nhựa 20,27%/75,66% thuộc riêng giá giữ ở mốc cũ; không áp dụng cho toàn vỏ hoặc thời gian in hiện tại.

**`Front_half_no_ribs.stl` cạnh `test.py` là D50, không phải D36.** Bộ D50 cuối đã giao:

- Front: `3D/Enclosure_USB_Near_Wall_D50/Print_2026-11-02_Front_No_Ribs/Front_half_no_ribs.stl`.
- Rear: `3D/Enclosure_USB_Near_Wall_D50/Print_2026-11-02_Final/Rear_half.stl`.
- ZIP front cùng thư mục No_Ribs. ZIP hai nửa trong Final còn chứa front trước khi cắt bỏ tám thanh.
- `Print_2026-11-02/`, STEP/STL cũ và bản vẽ Rev C không phải nguồn mới nhất; giữ làm lịch sử.

D50 còn nháp 33 tuyến dây có đoạn xuyên nhựa, không coi đã lắp được; đọc WIRING D50 nếu được yêu cầu điện. Firmware vẫn mốc S3/PSRAM chưa khớp C3; không tự sửa/build/flash khi làm CAD. Bản vẽ D50 chỉ làm khi được yêu cầu: đọc `Technical_Drawing/README.md`, giữ 3D, TEXT_SCALE 1.4 và đủ bốn tờ A3.

## 8. Quy tắc sửa và bàn giao

Chỉ sửa phần được yêu cầu, giữ kích thước/placement linh kiện và phần ngoài phạm vi. Sao lưu trước khi sửa. Trước lưu kiểm tra valid, số solid, bao bằng `optimalBoundingBox(False,False)`, giao thoa liên quan và viewport; sau lưu đọc lại BRep. IP5306 có dạng mặt: riêng `common.Volume == 0` không chứng minh hết cấn, phải xét khoảng cách/diện tích giao.

Dùng Shaded để không nhầm đường chia mặt Boolean với gờ nhựa. `removeSplitter()` từng tạo shape lỗi; chỉ dùng khi kết quả vẫn hợp lệ. Camera có animation, chờ ổn định trước chụp; import `from pivy import coin` trước khi thao tác camera node.

Khi chốt thay đổi CAD, cập nhật README bàn giao này và README đúng bản CAD. Không tự sửa `.gitignore`, commit/push, xóa backup hoặc lịch sử. Các script build/simplify một lần trong thư mục bản CAD mô tả từng mốc, có thể chặn trạng thái hoặc phụ thuộc lịch sử; không chạy lại để dựng CAD đã có.

Archive dọn ngày 02/11 nằm tại:

```text
3D/Enclosure_Compact_Layout_D36/History_2026-11-02/Session_work_archive.zip
```

Đọc README/`cleanup_manifest.json` trong thư mục lịch sử để tra đường dẫn gốc/hash; không cần giải nén để mở CAD hiện tại. Không chạy lại request lịch sử. Chỉ dọn inbox/outbox khi response hợp lệ đã có, xóa request trước rồi response, luôn giữ request đang chạy. Không tự dọn trong việc cập nhật tài liệu.
