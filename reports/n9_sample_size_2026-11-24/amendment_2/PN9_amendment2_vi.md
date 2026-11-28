# P-N9, sửa đổi 2: job SEA quá giờ khi máy ngủ (28/11/2026)

**Trạng thái.** User duyệt ngày 28/11/2026, trước khi chạy tiếp SEA. Sửa đổi được viết sau khi khóa luật v1 (5146c74), đóng băng code (044aa71) và sửa đổi 1, trước khi đọc bất kỳ giá trị nào của §3. Quyết định chỉ dựa trên log của runner, header kiểm đóng băng và log hệ thống của Windows; không xem chỉ số nào.

**Phạm vi.** Không đổi thành phần, phép kiểm, nhãn, ngưỡng hay code đã đóng băng. Chỉ xử lý một bản ghi lỗi của SEA R3 do máy ngủ, và mở rộng phép kiểm hoàn tất của sửa đổi 1 cho đúng bản ghi đó. `PN9_rules_vi.md` vẫn chưa sửa được khi còn lượt chính, nên mục §10 trỏ tới sửa đổi 1 và 2 sẽ viết sau khi mọi lượt chính xong.

## 1. Sự kiện

- FoundCause R1–R4 và SEA R1–R2 xong; mọi bản ghi `ok`; mọi header kiểm đóng băng đạt.
- SEA R3 bắt đầu lúc 03:30:37 ngày 28/11. 709 job đầu xong và `ok`.
- Job `PN9-c6-r8__n5000__A20__s740983` bắt đầu khoảng 07:34. Máy vào chế độ ngủ lúc 07:35:28 và thức dậy lúc 14:04:44 (log hệ thống: Kernel-Power 42, "Sleep Reason: Application API"; Power-Troubleshooter 1). User xác nhận đã cho máy ngủ.
- Giới hạn 3600 s của mỗi job SEA tính cả thời gian ngủ. Khi máy thức dậy, runner ghi `error: exit timeout` với `wall_total_s` = 23409,8, tức 6 giờ 29 phút ngủ cộng khoảng một phút chạy, rồi dừng như §8 quy định. Không có output nào được lưu cho job này; thư mục làm việc của nó bị runner xóa khi chạy lại.
- Hai lần ngủ khác, cũng do user, rơi vào lượt chính nhưng không gây lỗi: 12:43–13:15 ngày 27/11 (một job FoundCause R4 dài 2161 s) và 18:05–19:02 ngày 27/11 (một job SEA R1 dài 3440,5 s; R1 xong trong 5,98 h, dưới mốc 6,3 h). Model là tất định, nên tạm dừng do ngủ không làm đổi output.

## 2. Vì sao cần sửa đổi

- §8: một job lỗi thì dừng và báo user. Lỗi ở đây do máy ngủ, không do SEA; §1 đã định trước rằng runner chạy tiếp được sau khi bị gián đoạn.
- §7 không cho phép bản ghi lỗi. Nếu giữ nguyên, bản ghi này chặn việc đọc cả 11 thành phần, kể cả S1, S2s và S2t.

## 3. Quyết định

1. **SEA R3.** Mở một phiên mới, tức một header bắt đầu mới của `verify_freeze9.py`, rồi chạy runner đã đóng băng. Runner chạy lại job bị quá giờ trong một tiến trình mới với đúng seed đã ghi trước, rồi các job còn lại và hai job chạy lại cuối lượt. Bản ghi lỗi giữ nguyên trong log.
2. **SEA R4.** Chạy như thường sau R3.
3. **Mọi lý do dừng khác** ở §8, kể cả chạm mốc, giữ nguyên: dừng, báo user. Sửa đổi này không cho phép mở thêm phiên nào khác.
4. **Kiểm hoàn tất.** `completeness9b.py` thay cho `completeness9a.py` của sửa đổi 1, vốn chưa chạy trên output thật. Script mới làm đúng như `completeness9a.py`, với hai thay đổi:
   - danh sách được chấp nhận gồm các lần dừng ở mốc của GES trong `amendment_1/allowed_stops9.json` và bản ghi lỗi trong `allowed_errors9.json` (model, lượt, key, trạng thái, `wall_total_s`). Bản ghi lỗi chỉ được chấp nhận khi là `error: exit timeout` của SEA R3;
   - job có bản ghi trong danh sách còn phải đạt các kiểm riêng của SEA: seed khớp kế hoạch, `layout_ok` đúng, `auc_ok` không sai.
5. `analyze9.py`, mọi code đã đóng băng và `posthoc_recheck/recheck9.py` không đổi.

## 4. File trong thư mục này

- `run_sea_amend2.py`: chạy các phiên của bước 1–2, ghi `pn9_out/sea_amend2_sessions.jsonl` và `pn9_out/sea_amend2_console.log`. Không tính hay in chỉ số nào.
- `allowed_errors9.json`: bản ghi lỗi được chấp nhận.
- `completeness9b.py` và bài test `test_completeness9b.py`, kết quả ở `test_completeness9b.json`.

## 5. Nhật ký (append-only)

- **28/11/2026.** User xác nhận đã cho máy ngủ và duyệt việc chạy tiếp trong phiên mới. Commit và push trước khi mở phiên mới của SEA R3.
- **28/11/2026, 14:17.** `completeness9b.py` qua bài test `test_completeness9b.py` trên dữ liệu tổng hợp với input giả và đường dẫn chuyển hướng; không đọc output nào của P-N9. Kết quả ở `test_completeness9b.json`: 21/21 tình huống đạt. Cả 5 tình huống phải đạt đều đạt, kể cả tình huống thật (một lần dừng của GES R1 cộng một lần quá giờ của SEA R3); cả 16 tình huống có lỗi cài sẵn đều bị bắt. Lần chạy đầu của bài test dừng vì một lỗi chỉ số trong chính bài test (tình huống hai lần quá giờ); đã sửa chỉ số, không đổi `completeness9b.py`. SHA-256:
  - `completeness9b.py`: `cee1dbbeb6b11385bf03ad9b1ebb04006054046f38e5deae02c2b6103de8841b`;
  - `test_completeness9b.py`: `90c87510d5bbf8c5cd59814285cd9bcfba7b84f86e6785f9b0373af3a9fc0e30`;
  - `run_sea_amend2.py`: `99e50e4ec54234d149e6c4c1df93b716907e8ba1cfecd817411b7ea5895b1546`.
- **28/11/2026.** Commit cùng script kiểm lại độc lập `posthoc_recheck/recheck9.py`, viết và test ngày 27/11 trước khi đọc output nào (6/6 tình huống tổng hợp khớp với `analyze9.py`, 29/29 lỗi cài sẵn bị bắt; `posthoc_recheck/test_recheck9.json`). SHA-256 của `recheck9.py`: `8efbf308cb3ee6e574d21575239b172252bbfe373edf18cd5908aa12c5885a51`.
