# P-N9, sửa đổi 1: lần dừng ở mốc của GES R1 (26/11/2026)

**Trạng thái.** User duyệt ngày 26/11/2026, trước khi chạy tiếp GES. Sửa đổi được viết sau khi khóa luật v1 (5146c74) và đóng băng code (044aa71), trước khi đọc bất kỳ giá trị nào của §3. Quyết định chỉ dựa trên thời gian chạy, trạng thái job và header kiểm đóng băng; không xem chỉ số nào.

**Phạm vi.** Không đổi thành phần, phép kiểm, nhãn, ngưỡng hay code đã đóng băng. Chỉ đổi cách xử lý lần dừng ở mốc của GES (§8) và, tương ứng, phép kiểm hoàn tất (§7) cho đúng các lần dừng đó.

**Vì sao là file riêng.** `PN9_rules_vi.md` nằm trong danh sách file được kiểm mã băm ở đầu và cuối mỗi lượt chính, nên không sửa được khi các lượt chính còn chạy. Sau khi mọi lượt chính xong, nhật ký §10 sẽ có một mục trỏ tới file này.

## 1. Sự kiện

- Các lượt ngắn chạy từ 12:42 ngày 25/11 đến 03:18 ngày 26/11. AVICI R1–R4, CDFM R1–R4, PC R1 và R3 xong. Mọi bản ghi đều `ok`, và mọi header kiểm đóng băng đều đạt, cùng commit 044aa71.
- GES R1 dừng ở mốc 0,1 h (360 s). Bản ghi `budget_stop` đứng trước job `PN9-c2-r14__n4000__k0`, với `elapsed_s` = 373,3.
  - 418/422 job đã xong và `ok`.
  - Còn 4 job: 2 job chính (`PN9-c2-r14__n4000__k0` và `PN9-c2-r14__n4000__A20`) và 2 job chạy lại cuối lượt.
  - GES R3 chưa chạy.
- Nguyên nhân chỉ là thời gian. Tổng thời gian tính của 418 job là 367 s. Một lần gọi ở hệ `PN9-c2-r14` (n = 1000, A20, D = 30) mất 111 s; mọi lần gọi khác đều không quá 16 s.
- Mốc 0,1 h bằng 1,5 lần ước tính G4 (0,06 h). Ước tính này chỉ dựa trên 4 hệ DEV. Log held-out của Study 1 đã có những lần gọi GES chậm như vậy (lâu nhất 113,3 s, 95% số lần gọi dưới 10,4 s), nhưng không được dùng khi đặt mốc.
- Output của GES là tất định và được lưu riêng từng job bằng cách ghi nguyên tử, nên lần dừng không ảnh hưởng output nào đã lưu.

## 2. Vì sao cần sửa đổi

- §8 ghi: "Vượt mốc → dừng, báo user." Luật không nói xử lý tiếp thế nào; user quyết định.
- §7 không cho phép bản ghi `budget_stop`. `completeness9.py` (đã đóng băng) vì vậy báo lỗi, mà `analyze9.py` chỉ đọc khi kiểm hoàn tất đạt.
- Nếu giữ nguyên, một bản ghi về thời gian của GES sẽ chặn việc đọc cả 11 thành phần. Trong khi đó GES chỉ để mô tả và không thuộc thành phần Holm nào.
- Phương án dự phòng của GES ở §6.1 không áp ở đây. Phương án đó (bỏ các mức trên 2000 nếu một lần gọi mất hơn 60 s) là luật của cổng DEV, áp trước các lượt chính. Hơn nữa, lần gọi chậm xảy ra ở n = 1000.

## 3. Quyết định

1. **GES R1.** Mở một phiên mới, tức là ghi một header bắt đầu mới bằng `verify_freeze9.py`; đồng hồ của mốc bắt đầu lại. Sau đó chạy runner đã đóng băng. Runner bỏ qua các job đã xong có output khớp mã băm input, và chạy 4 job còn lại. Bản ghi `budget_stop` giữ nguyên trong log.
2. **GES R3.** Chạy như thường. Nếu một phiên chạm mốc (0,5 h), mở phiên mới như ở bước 1, và cứ thế.
3. **Trần thời gian.** Tổng thời gian các lượt chính của GES không quá 1,8 h, tức 1,5 lần ước tính 1,2 h của GES ở §8.
   - Tổng này cộng mọi phiên của R1 và R3. Mỗi phiên tính từ header bắt đầu đến lúc runner kết thúc; phiên đầu của R1 tính 373,3 s.
   - Chỉ mở phiên mới khi tổng đến lúc đó còn dưới 1,8 h. Nếu không, dừng và báo user.
   - Phiên cuối có thể vượt trần, nhiều nhất bằng mốc của phiên đó cộng một job.
4. **Các lý do dừng khác** ở §8 (job lỗi, chạy lại không trùng từng bit, kiểm đóng băng không đạt) giữ nguyên: dừng, báo user.
5. **Chỉ áp cho GES.** Nếu một lượt của model khác chạm mốc, user quyết định lúc đó.
6. **Kiểm hoàn tất.** `completeness9.py` chạy không đổi, và output của nó được lưu thành `checks/pn9_completeness_frozen.json`. Sau đó script mới `completeness9a.py` ghi `checks/pn9_completeness.json`, là file `analyze9.py` đọc. Script này chỉ ghi `ok = true` khi đủ cả bốn điều kiện:
   1. Mọi bản ghi `budget_stop` trong log của mọi model và mọi lượt đều là của GES R1 hoặc R3 và có trong `allowed_stops9.json` (model, lượt, key, `elapsed_s`). Ngược lại, mọi lần dừng trong danh sách đều có trong log.
   2. Job của mỗi lần dừng trong danh sách có đúng một bản ghi khác, `ok`, có output, và đạt các kiểm của §7 như mọi job khác: mức n khớp kế hoạch; mã băm input khớp input sinh lại; nếu là job chạy lại thì output trùng từng bit với bản gốc.
   3. Với mỗi lượt có lần dừng, số header bắt đầu đạt bằng 1 cộng số lần dừng của lượt đó trong danh sách. Header bắt đầu và header kết thúc cuối cùng đều đạt, như ở `completeness9.py`.
   4. Các lỗi `completeness9.py` báo đúng là các lỗi do những lần dừng trong danh sách gây ra: mỗi lượt có lần dừng một dòng `non-ok records`, mỗi job dừng một dòng `has 2 records or no output`. Có lỗi nào khác thì `ok = false`.

   `allowed_stops9.json` hiện chỉ có lần dừng ở §1. Nếu GES chạm mốc lần nữa theo bước 2, lần dừng đó được thêm vào danh sách và vào nhật ký dưới đây, kèm thời gian; không thêm gì khác.
7. `analyze9.py` và mọi code đã đóng băng không đổi.

## 4. File trong thư mục này

- `run_ges_amend1.py`: chạy các phiên của bước 1–3, kể cả trần ở bước 3. Script ghi `pn9_out/ges_amend1_sessions.jsonl` và `pn9_out/ges_amend1_console.log`, và không tính hay in chỉ số nào.
- `allowed_stops9.json`: danh sách lần dừng được chấp nhận.
- `completeness9a.py`: sẽ thêm sau, trước khi chạy bất kỳ kiểm hoàn tất nào. Mã băm SHA-256 của nó sẽ ghi vào nhật ký dưới đây khi commit.

## 5. Nhật ký (append-only)

- **26/11/2026.** User duyệt sửa đổi. Commit và push trước khi mở phiên mới của GES R1.
- **26/11/2026, 07:16–07:43.** GES chạy theo bước 1–3 bằng `run_ges_amend1.py`:
  - GES R1: phiên mới 17,3 s; 4 job còn lại `ok`; header kết thúc đạt.
  - GES R3: một phiên 1547,4 s, dưới mốc 1800 s; 422/422 job `ok`; header kết thúc đạt.
  - Tổng thời gian GES là 1938,0 s, dưới trần 6480 s. Không có lần dừng mới, nên `allowed_stops9.json` không đổi.
  - Mọi header kiểm đóng băng của GES đều đạt, cùng commit đóng băng 044aa71.
- **26/11/2026, 07:47.** Thêm `completeness9a.py` và bài test `test_completeness9a.py`:
  - SHA-256 của `completeness9a.py`: `bee2b5c7d345db200c0f9dcff38daf35eade1937014c38423d30f64ae233ae6e`.
  - SHA-256 của `test_completeness9a.py`: `2ab0123a5a3f9ddcff588740479835acbf7b86e8b1db2197ac706d191f9f87f5`.
  - Bài test dùng dữ liệu tổng hợp với input giả và đường dẫn chuyển hướng, như phần kiểm hoàn tất của `selftest9.py`; không đọc output nào của P-N9. Kết quả ở `test_completeness9a.json`: 15/15 tình huống đạt. Cả 4 tình huống phải đạt đều đạt, và cả 11 tình huống có lỗi cài sẵn đều bị bắt.
  - Chưa chạy kiểm hoàn tất trên output thật. Kiểm đóng băng ngay sau bài test (`pn9_precheck`, 07:47) đạt.
