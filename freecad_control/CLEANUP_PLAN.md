# Dọn thư mục FreeCAD — cập nhật06/11/2026

## Đã thực hiện ngày06/11

**Đã xóa đúng57 file, chỉ trong `freecad_control`, theo yêu cầu người dùng.** Gồm19 file dùng một lần (15 script,2 ảnh,2 JSON) và19 cặp request/response thành công (38 JSON). Mốc03/11 đã xóa155 file được giữ nguyên ở phần lịch sử bên dưới.

Bản sao đầy đủ tại [ZIP06/11](archive/cleanup_2026-11-06/session_cleanup.zip); danh sách nguồn/SHA-256/kích thước/lý do và audit CAD tại [manifest06/11](archive/cleanup_2026-11-06/cleanup_manifest.json). ZIP có thêm snapshot ba Markdown và `resume_latest.py` trước dọn, tổng61 file được kiểm tra hash, cùng manifest trước xóa. Đã kiểm tra CRC và mọi SHA-256 trước khi xóa; request trước, response sau.

Giữ16 cặp lỗi/kiểm chứng thất bại, request ngắt, cầu nối/macro/send/status, scripts resume/inspect, `.gitignore`, archive cũ. Không xóa CAD/STL/backup/báo cáo trong `3D`, firmware hoặc Word. Muốn phục hồi chỉ giải nén vào thư mục tạm và kiểm tra manifest; không đưa request hoàn tất trở lại inbox và không chạy lại code lịch sử trên CAD hiện hành.

### 19 file dùng một lần đã xóa

- `freecad_control/build_d36_wiring.py`
- `freecad_control/build_tidy_d36_wiring.py`
- `freecad_control/capture_d36_wiring.py`
- `freecad_control/capture_tidy_d36_wiring.py`
- `freecad_control/debug_wiring_validation.py`
- `freecad_control/export_wiring_obstacles.py`
- `freecad_control/inspect_wiring.py`
- `freecad_control/inspect_wiring_ports.py`
- `freecad_control/plan_d36_wiring.py`
- `freecad_control/plan_tidy_d36_wiring.py`
- `freecad_control/save_d36_wiring.py`
- `freecad_control/save_tidy_d36_wiring.py`
- `freecad_control/verify_saved_d36_wiring.py`
- `freecad_control/verify_saved_tidy_d36_wiring.py`
- `freecad_control/view_tidy_d36_wiring.py`
- `freecad_control/wiring_before.png`
- `freecad_control/wiring_ports.png`
- `freecad_control/wiring_inspection.json`
- `freecad_control/wiring_obstacles.json`

### 19 cặp thành công đã xóa

Mỗi UUID tương ứng `easy_insert_session/inbox/<UUID>.json` và `easy_insert_session/outbox/<UUID>.json` trong `freecad_control`. Response có `ok: true`; các response lỗi hoặc kết quả `validation_failed` được giữ lại.

- `04a2077bd3e14d8b88b725a50c61afdc`
- `07a650f02e2d4e1491ba9e4d04a7f4f2`
- `1ca9898a1cca42ddbfd5972b4b3c058e`
- `1eb3e943a6444247a45093d7ba98b82d`
- `3beb0a343c454ce8b070d92005525c51`
- `479e602d07fb42ed910d7d03b7eb9e64`
- `57720239cdec4740b2584c8cf84a43de`
- `57806f4ffa9f42cf9dac11e7a50aa19c`
- `622dfeeb321a42e08693da9c777c79ac`
- `6c020ddba17d4d09b3a8facc2c1ced1f`
- `9259bb2a58a047ef89f84ff468262066`
- `930fb903c61f4af7ac591a4cb4930e82`
- `a6ec5c0afffb4cfe8905b28b74c56112`
- `a87cf521b3534e04993e9bbfd2e4746b`
- `b5595ea91c76479381dc1708699bf736`
- `c17b5dd9177d4b44af99b0aa02d8eec6`
- `c8d0d280d0c545ff903411a968adc7cd`
- `d69b3e4270aa4971bf32979c0ee7055a`
- `f5321b218027482c8555e9df8e59520c`

## Lịch sử dọn03/11

### Danh sách đã thực hiện —03/11/2026

**Trạng thái: đã xóa đúng 155 file sau khi người dùng đồng ý, chỉ trong thư mục `freecad_control`.** Không xóa file ngoài thư mục này.

Đã xóa đúng 155 file: 25 script/ảnh dùng một lần và 65 cặp request/response đã trả về `ok: true` (130 JSON).

Tất cả đã lưu ở `archive/cleanup_2026-11-03/session_cleanup.zip`; đường dẫn gốc, SHA-256 và kích thước ở `cleanup_manifest.json`. Các bản rời trong danh sách đã xóa; bản sao đầy đủ còn trong ZIP.

Không xóa CAD, STL, backup, báo cáo trong `3D`, các cầu nối, status, request lỗi/bị ngắt, script mở bản hiện tại/bản cũ, firmware hoặc tài liệu Word.

Việc xóa làm mất bản rời tại đường dẫn cũ; nếu cần lại phải khôi phục từ ZIP. Không đưa request đã hoàn tất trở lại inbox đang hoạt động.

## 25 script/ảnh đã xóa

- `freecad_control/add_lower_screw.py`
- `freecad_control/add_recessed_fasteners.py`
- `freecad_control/capture_centered_m3.py`
- `freecad_control/capture_clean_assembly.py`
- `freecad_control/capture_fasteners.py`
- `freecad_control/capture_lower_screw.py`
- `freecad_control/capture_reinforced_frame.py`
- `freecad_control/center_lower_m3.py`
- `freecad_control/export_shells_2026_11_03.py`
- `freecad_control/finalize_simplified_holders.py`
- `freecad_control/finish_recessed_fasteners.py`
- `freecad_control/inspect_fastener_holes.py`
- `freecad_control/inspect_frame_bars.py`
- `freecad_control/inspect_lower_screw.py`
- `freecad_control/inspect_shell_steps.py`
- `freecad_control/keep_shells_only.py`
- `freecad_control/reinforce_frame_bars.py`
- `freecad_control/restore_selected_components.py`
- `freecad_control/save_fastener_view.py`
- `freecad_control/show_clean_assembly.py`
- `freecad_control/show_lower_screw.py`
- `freecad_control/simplify_holder_steps.py`
- `freecad_control/validate_clean_view.py`
- `freecad_control/validate_saved_fasteners.py`
- `freecad_control/restart_screen.png`

## 65 cặp request/response thành công

Mỗi UUID dưới đây tương ứng hai file: `freecad_control/easy_insert_session/inbox/<UUID>.json` và `freecad_control/easy_insert_session/outbox/<UUID>.json`. Đã kiểm tra lại response và hash, xóa request trước, response sau.

- `0c1e06f5550d4b658a1d0db5e1ee2df0`
- `1024555d01e2417d92502b2756e981de`
- `1130db805d504bada7ecadd58f0c9d67`
- `225374390cbc489f872f8771cd475ba0`
- `238664b748c44a7792d3e2acc9722e02`
- `2a2c4216c3b740f6960467af1edf71ab`
- `2a47991e25ba471481ace5d08a563934`
- `2bedc22a311240509a6350879093aed3`
- `2daaa7d89260475998004c8d02559029`
- `2dfa841c1e7d41649295909e41ecc313`
- `2e7465411f4f4b00a327a77dfadf8301`
- `2f95ca606e954e0e908d97e9cbeb3d7f`
- `34e546ba9db74638aa6bbe68f33aea8e`
- `3aa23a7edfc14cabbee93fc8ab0668d0`
- `4231a0f907eb4c6fa472ca4e99419ad1`
- `427c6e41bc1348ab8113f1fdb8ff8fb1`
- `4773a457430d4a17a18add002d721723`
- `48bceefdcf374cb6b55fedf1993f4e5a`
- `4a4b3d521fd3494b8d3267ad909d04ca`
- `4ae50d85b0164549b6010ecd170e3191`
- `4c3a00bf6b2041f29fbd79470dbfb3e7`
- `4fb9dc31022047738863429d233dc806`
- `5137ac12f14e48be9c3beb06f9c835d0`
- `61aade79062b469cade898ef47db7b13`
- `68347828d59446d985e833971c04d38d`
- `6a33593a14a541639e646c442c9c504f`
- `6cd603c693a14879b073b46ce999aaa1`
- `6d6def125551496d8bfb424776a40253`
- `72e19b5551dd40f6b6122767aafc59fd`
- `74aa729ad34d474da32820a7467c017e`
- `74c5bf26ad2248ebb26c6afffc708dec`
- `7738060948204c6d94bf6bb267602f6c`
- `789b87c5d9c04a50814298165cf5137c`
- `81e9f656b9434234b70295b96aa0aa54`
- `84e193d12d2b496eaa89bd2fecdb1ffc`
- `8c4450d3e5774b33966fde794bdd9698`
- `8d74895b14544be492ae0eebbe114af6`
- `8ee2095c611c48f8b7bd7822e47a455c`
- `94a61e9f8219474e842ffd6e18795895`
- `969765ecfc3841d897ad5a7852af5d14`
- `9dd4b5bde836414582b0a00b29893b8c`
- `9ed9001bc8ff406e8fd79fd47c85de3f`
- `a464fa45223149c9a8768c0fa0740f26`
- `a8c7401e72db4126a46b3516dbc24b73`
- `ab85e37987e243e7ac275a8d39e73974`
- `ae1e4798abc7468782c317e2da288940`
- `b2a946184b3844918e830005e55a5224`
- `b42911768195451a97cb6643f8b45965`
- `bafbf98b7cfb44948a48d5083a36343e`
- `bd17b5ff221148caae1789fd1fb694ba`
- `bdf89568af1a438c9828afc0c9c88183`
- `c03d47459ca54ddfbaec3facddb4b4fd`
- `c1e5b67ae7884ca397f218438b9e09ed`
- `c3152b683fd540d0a29114752c77e635`
- `c752c73f07ff4f69a22b812da9d0b96a`
- `cda8724ec2684508aec2087aedbaa4d5`
- `ce7535513e904df6bf64186d5ddd4ee5`
- `d5b027de5ac14cb69d9aaf19ffa7d0e0`
- `e0e92ee6a1274da5b66a393945eb5ea3`
- `e19488ca5d824d83afcce959d79c316a`
- `e34cc48681d04b998973e0024e637fd3`
- `e544bffe81bd48aab564db9bd940b2d6`
- `e55be620520a4dfdba9b6902d6be0c14`
- `edb1b5557aea4b73bf0e17e7cc291715`
- `ff94ffa86a44462eb9e42d090ab4c19c`
