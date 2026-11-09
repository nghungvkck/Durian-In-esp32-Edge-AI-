# Lịch sử và dọn thư mục FreeCAD

Tài liệu khôi phục hiện trạng: [README.md](README.md). File này chỉ giúp tra lại nguồn cũ; không phải danh sách lệnh cần chạy.

## Cập nhật06/11/2026 — đi dây, gom dây và kiểm kê trên đĩa

- Theo người dùng: ESP32-S3 Super Mini dùng nguyên hình C3 đại diện; SD breakout chỉ nhận3V3. Theo `firmware/README.md` mục7: SD13/12/11/10, I2S4/5/6, nút1/2/3. Pad vật lý chưa đối chiếu bo thật.
- Mốc đi dây đầu:55 objects/21 dây, hash36d34f9a6e62a5b85c42726c2315226e1231748b855d3d012b69bdaeeb1e3cdd;693,57 mm không áp dụng mốc này, tổng mốc đầu567,53 mm, vùng chung3,2 mm. Bằng chứng `CAD_DIR/Wiring_2026-11-06/`.
- Mốc gom gọn:55 objects/21 dây, hash`39f39e587e6e562525fdf9370f45cbdf2783d0e3523c8590d6a385d9aaf9cb29`; tổng693,57 mm, hở dây–vỏ/gờ tối thiểu0,242 mm, vùng chung cùng pad1,1 mm.23 BRep đọc lại valid/một solid,33 BRep nguồn giữ nguyên. Bằng chứng `CAD_DIR/Wiring_Tidy_2026-11-06/`.
- Khi dọn theo yêu cầu, tên file chính trên đĩa có hash`7ffc4262b453c2585239551817bba8d1cc305e709a64e4abfb961d7eeb396e66`,43 objects, không có dây/vít, có TPU/preview/LED/R/C. ZIP/XML/BRep/Placement khác bản đã kiểm chứng. Không đo lại bằng kernel, không coi báo cáo cũ xác nhận file43 objects, không tự khôi phục.
- Bản gom gọn còn nguyên tại `CAD_DIR/D36_Printed_Retention_35x25x6.20261106-103437.FCBak`, hash khớp báo cáo. README chính ghi rõ cần chốt bản làm việc trước khi tiếp tục CAD.

## Dọn ngày06/11/2026

- Người dùng yêu cầu cập nhật Markdown và xóa file không cần trong `freecad_control`; đã xóa đúng57 file:15 script dùng một lần +2 ảnh thử +2 JSON trung gian +19 cặp request/response thành công.
- Đã nén đủ57 file cùng snapshot ba Markdown và `resume_latest.py` trước dọn; kiểm tra CRC ZIP và SHA-256 từng file trước xóa. ZIP: [session_cleanup.zip](archive/cleanup_2026-11-06/session_cleanup.zip); [manifest](archive/cleanup_2026-11-06/cleanup_manifest.json) ghi nguồn, hash, kích thước, lý do và audit CAD.
- Xóa từng request đã có response thành công trước, response sau. Giữ16 cặp lỗi/kiểm chứng thất bại và request bị ngắt; không phát lại request hoặc chạy script cũ.
- Giữ các cầu nối/macro/send/status, script inspect/resume, `.gitignore`, toàn bộ archive cũ và mọi dữ liệu ngoài `freecad_control`. Không sửa CAD/backup/STL/firmware, không commit/push.
- README được hợp nhất: phân biệt file43 objects hiện trên đĩa với backup55 objects, hướng dẫn tiếp tục, trạng thái21 dây, kiểm chứng và cách tra script đã lưu ZIP.

## Dọn ngày 03/11/2026

- ZIP: `archive/cleanup_2026-11-03/session_cleanup.zip`.
- Manifest: `archive/cleanup_2026-11-03/cleanup_manifest.json`, ghi đường dẫn gốc tương đối với repo, kích thước, SHA-256, lý do và cách xử lý từng file.
- ZIP có bản README trước khi hợp nhất, bản `resume_latest.py` trước khi sửa câu trạng thái xuất STL, script dùng một lần, ảnh restart và các request/response thành công được đề xuất dọn.
- Đã kiểm tra CRC và SHA-256 từng mục ZIP. **Đã xóa đúng 155 file trong `freecad_control` sau khi người dùng chấp thuận**, theo [CLEANUP_PLAN.md](CLEANUP_PLAN.md). Request được xóa trước response để cầu nối không thực thi lại. Lần từ chối tự động trước đó đã được giải quyết bằng sự chấp thuận rõ phạm vi của người dùng.
- Giữ CAD, backup, STL, báo cáo trong `3D`, ba cầu nối, status, request lỗi và request bị ngắt. Không đổi `.gitignore`, firmware hoặc commit/push.

Muốn tra lịch sử, liệt kê/đọc ZIP; nếu cần giải nén thì dùng thư mục tạm riêng. Không giải nén vào inbox, không chạy lại code cũ trên CAD hiện hành. Có thể khôi phục file rời từ đúng mục ZIP sau khi kiểm tra hash trong manifest.

## Các mốc thiết kế trước khi đi dây

| Mốc | Ý nghĩa lịch sử |
|---|---|
| Khay/chèn TPU, thân136 | Đã bỏ toàn bộ TPU, hốc chèn và khe gài; không phục hồi theo các README cũ |
| Khung chỉ 6 objects | Sau đó phục hồi 25 phần linh kiện, không phải hiện trạng hiện nay |
| Vít M2 lệch cạnh | Thay bằng M3 ở X0/Z18, xóa cả lỗ/trụ M2 |
| Thân146 / ba M3 | Giữ công tắc đáy, dịch cụm phía trên Z+10 |
| Gia cố gờ hai nửa | Bản hình học hiện hành, số liệu tại `Reinforced_Frame/validation.json` |
| Xuất STL03/11 | Hai vỏ D36, không xuất linh kiện hoặc vít kim loại |

Các hash lịch sử và mô tả đầy đủ nằm trong README gốc được lưu trong ZIP và báo cáo từng mốc. `CAD_DIR` theo định nghĩa tại README bàn giao. Không gọi hash đó là hash file hiện tại; README bàn giao ghi riêng hash CAD đang lưu và hash nguồn xuất STL.

## Các bản cũ còn giữ nguyên

- D36 nền: `3D/Enclosure_Compact_Layout_D36/Compact_Layout_D36.FCStd`, mở bằng `resume_compact_d36.py` khi được yêu cầu.
- D36 `Trial_Minimal_Pads/`, `Trial_Battery_Tray/`, `Trial_AntiRattle_Battery_35x25x6/`: phương án thử đã bị thay thế, không tiếp tục thay bản chính.
- D40: mở bằng `resume_compact_layout.py` khi cần tham khảo.
- D50: mở bằng `resume_d50.py`. Front cuối ở `3D/Enclosure_USB_Near_Wall_D50/Print_2026-11-02_Front_No_Ribs/Front_half_no_ribs.stl`; Rear ở `Print_2026-11-02_Final/Rear_half.stl` cùng thư mục D50. ZIP hai nửa trong `Final` vẫn chứa front trước khi bỏ tám thanh.
- D50 có nháp 33 tuyến dây còn xuyên nhựa, không coi là đã lắp được. Bản vẽ D50 chỉ làm khi được yêu cầu; đọc `Technical_Drawing/README.md`, giữ 3D, TEXT_SCALE1.4 và đủ bốn tờ A3.
- Archive02/11: `3D/Enclosure_Compact_Layout_D36/History_2026-11-02/Session_work_archive.zip`, có README/manifest để tra nguồn.
