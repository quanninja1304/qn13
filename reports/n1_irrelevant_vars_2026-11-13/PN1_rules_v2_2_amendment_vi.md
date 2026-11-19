# Luật đọc P-N1, bản sửa v2.2: held-out (19/11/2026)

> **Trạng thái:** user duyệt 19/11/2026; khóa khi commit chứa file này và `code/SHA256SUMS` được push. Chưa có output model nào trên hệ held-out tại thời điểm khóa: thư mục kết quả không có file `HELD-*` nào. Script phân tích `analyze_held.py` từ chối đọc khi thiếu output.
> **Phạm vi:** chỉ sửa phần held-out (v2 RN5, v2.1 A9). Mọi phần khác của [v2](PN1_reading_rules_vi.md) và [v2.1](PN1_rules_v2_1_amendment_vi.md) giữ nguyên, kể cả các biên 0.03 và 0.05, τ, decoder, bootstrap (2 000 lần, percentile 95%, seed 20261114).
> **Bối cảnh:** kết quả E2 ở [`PN1_E2_results_vi.md`](PN1_E2_results_vi.md). Lead và dấu đã ghi ở đó, theo quy tắc "mọi chữ ký đạt đều đi tiếp" đã ghi ở §4 của v2.1 trước khi xem số.

## 1. Cỡ held-out: 80 hệ lồng nhau, FoundCause giữ 24

**Lý do:** đây là thay đổi thiết kế dựa trên dữ liệu exploratory, làm trước khi mở held-out. Mô phỏng lấy mẫu phân tầng từ 80 hệ E2 (1 000 lần, đọc bằng đúng luật) cho thấy với 24 hệ, xác suất đạt luật **ngay cả khi hiệu ứng thật bằng ước lượng E2** là:

| Tiêu chí | 24 hệ | 80 hệ |
|---|---|---|
| AVICI M1 (cận trên < −0.03) | 0.55 | 0.98 |
| CDFM M2_FIXED, phần H | 0.08 | 0.51–0.54 |
| FoundCause B20, cận dưới > 0 | 0.80 | — |
| HARM ở A20 (ba model) | 0.81–0.97 | ≥ 0.92 |

Đây là ước lượng dưới phân phối thực nghiệm của E2, không phải power của quần thể thật. Nó có thể lạc quan vì lead được chọn từ chính E2. Sai số Monte Carlo khoảng ±0.016. Mã: `code/pn1/power_heldout.py`.

**Thiết kế:**
- Seed hệ held-out thứ r của ô c là `300000 + 1000·c + r`, đúng công thức của v2.1. v2.1 dùng r ∈ {0, 1, 2} (24 hệ); v2.2 dùng r ∈ {0, …, 9} (80 hệ). 24 hệ cũ là tập con của 80 hệ.
- Cả 80 seed được chốt trong `code/pn1_out/held_manifest.json` trước khi chạy: seed dùng thật, số cạnh thật, mã băm khối đích, mã băm mọi input. Không trùng seed với DEV, EXP, ORACLE; không hệ nào bị thay seed theo luật 0 cạnh.
- **Không đọc kết quả của 24 hệ đầu để quyết định có chạy tiếp hay không.** Runner chạy từng model trọn tập của nó.

| Thuật toán | Tập đọc chính | Điều kiện (luôn có k = 0) | Số job |
|---|---|---|---|
| AVICI | 80 hệ | A20, B20 | 240 |
| CDFM | 80 hệ | A5, A10, A20, A30, B20, C20 | 560 |
| FoundCause | 24 hệ (r ∈ {0, 1, 2}) | A20, B20 | 72 |
| PC, GES | 80 hệ | hợp các điều kiện trên | 560 mỗi thuật toán |

- AVICI và CDFM: đọc chính trên 80 hệ; 24 hệ con chỉ báo ở mức mô tả.
- FoundCause: so với PC/GES **trên đúng 24 hệ đó**, không dùng mốc trung bình trên 80 hệ.
- BEYOND_CLASSICAL chỉ trên hệ tuyến tính: 40 hệ (AVICI, CDFM), 12 hệ (FoundCause).

## 2. Không đổi

Biên 0.03 (M1, M2) và 0.05 (HARM, BEYOND_CLASSICAL, M3); τ đo trên DEV ở RN0; ba decoder; thống kê bootstrap; cách nối đệm sau khối đích; adapter và số luồng như E1/E2. Không nới biên vì tăng cỡ mẫu.

## 3. Luật đọc held-out

### 3.1 Phần chung, đọc cho mọi model

- **CHANGE tại A20:** ba nhãn A1 như E1, cùng τ và biên.
- **HARM tại A20:** H ≥ 0.05 và cận dưới CI > 0, cho H_NATIVE và H_FIXED.
- **BEYOND_CLASSICAL tại A20, hệ tuyến tính:** ước lượng = H_model − max(H_PC, H_GES); max tính lại trong từng lần bootstrap.
  - PASS: ước lượng ≥ 0.05 và cận dưới > 0.
  - CONTRARY: cận trên < 0.05.
  - INCONCLUSIVE: còn lại.

### 3.2 Lead của từng model (đóng băng)

**AVICI: M1, dấu −, H_NATIVE (= H_FIXED; một phép thử, không phải hai).** δ = H_A20 − H_B20, trung bình [CI].
- REPLICATED: cận trên < −0.03.
- NOT_REPLICATED: cận dưới > −0.03.
- INCONCLUSIVE: CI chứa −0.03.

**CDFM: M2, chỉ đọc chính ở H_FIXED.**
- Phần H, với ba hiệu H_A20 − H_B20, H_A20 − H_C20, H_B20 − H_C20:
  - PASS_H: cả ba CI nằm trọn trong [−0.03, +0.03].
  - CONTRARY_H: ít nhất một CI nằm trọn về một phía ngoài khoảng đó.
  - INCONCLUSIVE_H: còn lại.
- Phần Δp (kiểu A):
  - (i) cận dưới CI của median theo hệ của Δp_A(30) − Δp_A(5) > 0;
  - (ii) median Δp không giảm qua k = 5, 10, 20, 30.
- Tổng hợp:
  - **M2 PASS:** PASS_H, (i) và (ii).
  - **M2 CONTRARY:** CONTRARY_H, hoặc CI của contrast Δp nằm trọn dưới 0.
  - **M2 INCONCLUSIVE:** còn lại. Ghi rõ điều kiện nào không đạt. Một đoạn median giảm nhẹ mà không có bằng chứng thống kê ngược chiều thì chỉ báo là điều kiện đơn điệu không đạt, không gọi là bác bỏ pha loãng.
- M2 ở H_NATIVE chỉ báo ở mức mô tả, không thay thế lead kể cả khi thuận lợi hơn.
- Kể cả với 80 hệ, PASS_H chỉ khoảng 0.5 dưới phân phối E2. INCONCLUSIVE là kết quả đã được dự kiến, không phải bằng chứng trái chiều.

**Nhãn RN5 cho AVICI và CDFM:**
- **REPLICATED:** BEYOND_CLASSICAL PASS (cùng estimand với lead) và lead đạt (AVICI REPLICATED; CDFM M2 PASS).
- **NOT_REPLICATED:** BEYOND_CLASSICAL CONTRARY, hoặc lead NOT_REPLICATED/CONTRARY.
- **INCONCLUSIVE:** còn lại.

**FoundCause: không có lead** (UNEXPLAINED ở E2). Chỉ kiểm lại CHANGE, HARM và BEYOND_CLASSICAL tại A20.
- **Nhánh phụ B20, chọn sau khi xem E2.** Estimand NATIVE; δ = H_A20 − H_B20; giả thuyết là dấu dương.
  - SIGN_CONFIRMED: cận dưới > 0.
  - CONTRARY: cận trên < 0.
  - INCONCLUSIVE: CI chứa 0.
  - Báo thêm việc cận dưới có vượt 0.03 hay không.
- Nhánh này là phép kiểm độc lập trên dữ liệu mới cho một giả thuyết sinh ra từ E2. Nó không phải cách hạ biên M1 từ 0.03 xuống 0, không đổi nhãn UNEXPLAINED của E2, và không thay thế lead nếu AVICI hay CDFM không tái lập.

### 3.3 Mô tả (không phải nhãn)

Theo từng điều kiện: median Δp, Flips, H_NATIVE, H_FIXED, mốc PC/GES; thay đổi TP, FP, FN, precision, recall (NATIVE) so với k = 0; với CDFM thêm H_FROZEN; với AVICI, CDFM thêm toàn bộ phần chung trên 24 hệ con.

### 3.4 Quyết định dự án (v2.1 A9)

- **GO mechanism validation:** AVICI hoặc CDFM đạt REPLICATED. Tức là thiết kế can thiệp vào model để tách các giả thuyết ở §5 của báo cáo E2; chưa xây phương pháp.
- Còn lại: báo theo từng model; quyết định tiếp theo là của user.
- Kết luận theo từng model và estimand. Held-out không biến chúng thành một claim đã kiểm soát familywise; không dùng câu "ít nhất một model đạt" như kết luận đã kiểm soát.
- Số phép thử ở held-out:
  - lead: 2 (AVICI M1, CDFM M2);
  - nhánh phụ: 1 (FoundCause B20);
  - kiểm lại HARM và BEYOND_CLASSICAL: 6 + 6.

## 4. Đóng băng mã và bằng chứng thời gian

- **Snapshot nguồn** ở [`code/`](code/), kèm `code/SHA256SUMS`: code chạy, code phân tích (gồm `analyze_held.py`), YAML sinh dữ liệu, manifest seed, τ của RN0 (`rn0_*.json`), script power.
  - Đây là snapshot để đối chiếu, không chạy từ vị trí này: `common.py` tính đường dẫn theo vị trí file.
  - Code chạy thật nằm ở `artifacts/n1_runs/` (git-ignored). `verify_freeze.py` kiểm từng file ở đó có cùng SHA-256 với snapshot.
- **Cổng trước khi chạy** (`run_heldout.ps1` gọi `verify_freeze.py`). Runner dừng nếu:
  - mã băm lệch;
  - snapshot có thay đổi chưa commit;
  - commit sửa `SHA256SUMS` lần cuối chưa có trên remote.

  Mỗi lần chạy ghi `held_run_header.json`: commit đóng băng, HEAD, mã băm của `SHA256SUMS`.
- **Kiểm chéo khi đọc:** `analyze_held.py` so mã băm input của từng output với manifest, và seed dùng thật của từng hệ; lệch là từ chối đọc.
- **Kiểm tương đương trước khi đóng băng:** chạy `analyze_held.py --set EXP` trên 80 hệ exploratory tái tạo đúng **mọi** số E1/E2 tương ứng, kể cả CI: CHANGE, HARM, BEYOND_CLASSICAL, M1, ba hiệu M2, contrast Δp, H mô tả theo điều kiện. Các nhãn trên EXP ra đúng như dự kiến: AVICI REPLICATED, CDFM M2 PASS, FoundCause SIGN_CONFIRMED.
- **Bằng chứng phía GitHub:** sau khi push, lưu phản hồi của `GET /repos/{owner}/{repo}/activity` (thời điểm do máy chủ ghi) và `git ls-remote`.
  - Đây là bằng chứng nội dung đã công khai trước khi chạy, không chứng minh ai đã hay chưa xem dữ liệu.
  - API này chỉ giữ lịch sử có hạn, nên phản hồi được lưu lại ngay.
- `jobs.py` có thêm `HELD_PER_CELL`, `HELD_CONDS`, `held_systems` và nhánh `HELD`. Danh sách job của DEV, E1, E2 đã được kiểm là trùng hệt bản dùng cho E2. `common.py` không đổi.

## 5. Quyết định của user (19/11/2026)

1. Held-out 80/80/24 như §1: **duyệt**.
2. Ba nhánh cho M2 của CDFM gồm cả điều kiện Δp, và tiêu chí dấu cho FoundCause B20: **duyệt** (theo chỉnh lý của user).
3. Thứ tự: làm sạch lịch sử, push, đóng băng v2.2 và push, rồi mới chạy: **duyệt**.

## 6. Nhật ký thay đổi sau khóa (append-only)

- 19/11/2026: khóa. Chưa có output model nào trên hệ held-out.
