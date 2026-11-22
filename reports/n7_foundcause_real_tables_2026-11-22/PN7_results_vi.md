# P-N7: kết quả, FoundCause trên hai bảng thật (gap 4, C11 cho model thứ ba)

> **Luật:** [PN7_rules_vi.md](PN7_rules_vi.md) v1, khóa ở `7bc40f8` (push 2026-11-22T14:28:20Z).
>
> **Code:** đóng băng ở `82ef38c` (push 2026-11-22T15:04:15Z): 19 file, 219 mã băm phụ thuộc.
>
> **Lượt chính:**
>
> - Sachs: 15:05:30–17:32:41Z;
> - Wine: 17:32:43–19:46:45Z.
>
> **Đọc:** bằng code đã đóng băng (`analyze7.py --set PN7`), sau khi kiểm hoàn tất đạt.
>
> **Phạm vi:**
>
> - P7-1 kiểm độ bất ổn của **toàn bộ pipeline mặc định** của FoundCause, có điều kiện trên lịch suy luận base 42 của gói;
> - input là input của P-N5 được dùng lại, **không phải dữ liệu held-out mới**;
> - hai giả thuyết là một family Holm riêng, tách khỏi các family của P-N5 và P-N6;
> - đo độ bất ổn, không đo độ chính xác; không dùng đồ thị tham chiếu nào của Sachs.

## 0. Tóm tắt

| ID | Bảng | E_r[D_r], CI 95% | p một phía | Holm (hạng, ngưỡng) | Nhãn | +/0/− |
|---|---|---|---|---|---|---|
| P7-1W | Wine | +15.90 [+14.51, +17.29] | 6.0 × 10⁻¹⁶ | 1, 0.025 | **CONFIRMED** | 20/0/0 |
| P7-1S | Sachs | +0.05 [−0.23, +0.33] | 0.358 | 2, 0.05 | **NOT_CONFIRMED** | 4/13/3 |

Ở đây D_r = flips_FC,r − max(flips_PC,r, flips_GES,r), ở k = 20 với đệm Gauss, trên 20 lần sinh đệm của P-N5. t có df = 19 và là xấp xỉ, vì flips là số đếm rời rạc. CI và nhãn cỡ không được Holm bảo vệ.

**Câu được viết (theo §9 của luật):**

- **Wine:** "Trên 500 hàng đã chọn của bảng Wine, với tiền xử lý đã khóa và pipeline mặc định của FoundCause, thêm 20 cột Gauss độc lập làm skeleton trên khối thật đổi trạng thái trung bình 16.0 trong 55 cặp. Đối chứng cổ điển đổi nhiều hơn ở từng lần sinh đổi trung bình 0.10 cặp."
- **Sachs:** "Trên 500 hàng đã chọn của bảng Sachs, … đổi trạng thái trung bình 0.25 trong 55 cặp. Đối chứng cổ điển đổi nhiều hơn ở từng lần sinh đổi trung bình 0.20 cặp." Giả thuyết không được xác nhận.

## 1. Tính toàn vẹn

- **Cổng đóng băng:** đạt ở đầu và cuối cả hai lượt (`pn7_start_sachs`, `pn7_end_sachs`, `pn7_start_wine`, `pn7_end_wine`).
  - Mỗi header ghi `82ef38c`, nhánh remote, mã băm `SHA256SUMS` và `DEPS_SHA256.json`, `data_ok` và `checkpoint_ok`.
- **Kiểm hoàn tất** ([`checks/pn7_completeness.json`](checks/pn7_completeness.json)), `ok`, 0 vấn đề:
  - 54/54 job `ok`;
  - 54 input khớp mã băm của P-N5 (`inputs5.json`);
  - chỉ số hàng (450/500 ở mỗi lượt con) trùng giữa k0 và mọi input `k20_e0`, ở 40 input;
  - kiểm dòng mã về lịch trong nguồn gói đạt;
  - chạy lại k0 trùng từng bit ở cả hai bảng;
  - adapter ở base 42 lệch 0 so với API ở cả hai bảng (ngưỡng dừng 10⁻⁶).
- **Ngân sách:**
  - Sachs 8 827 s (2.45 giờ), Wine 8 039 s (2.23 giờ), đều dưới mốc dừng 3 giờ mỗi lượt;
  - trung vị mỗi lần gọi: 153 s ở D = 11, 338–341 s ở D = 31;
  - bộ nhớ đỉnh 2.27 GB (Wine), cao hơn mức 2.09 GB đo ở DEV7.
- **Kiểm lại độc lập** ([`posthoc/recheck_pn7.py`](posthoc/recheck_pn7.py), output ở [`posthoc/recheck_output.txt`](posthoc/recheck_output.txt)):
  - script được viết ngày 23/11, trước khi đọc bất kỳ output chính nào;
  - không import code đã đóng băng của P-N7, P-N5 hay P-N1. Nó dựng lại skeleton, flips, contrast, phép t và Holm từ file `.npz` thô;
  - kết quả khớp hoàn toàn với code đọc: 20 giá trị contrast mỗi bảng, trung bình, p, tham chiếu lịch, m0 và nhãn Holm.
- **Ghi chú quy trình:**
  - Lần chạy thử đầu tiên của script kiểm lại, trên output DEV7 (bảng thay thế `standin`), đã in giá trị flips, contrast và p của bảng thay thế. Cổng G7 chỉ cho kiểm cấu trúc trên DEV7.
  - Không yếu tố đã khóa nào và không lượt chạy nào phụ thuộc các giá trị này: code đã đóng băng và lượt chính đang chạy.
  - Chế độ dev của script sau đó được sửa để không in giá trị.

## 2. Mô tả (không thuộc bộ Holm)

| Số đo | Sachs | Wine |
|---|---|---|
| m0 của FoundCause (số cạnh skeleton ở k0, trên 55 cặp) | 7 | 8 |
| flips của FoundCause ở k = 20: trung bình [nhỏ nhất, lớn nhất] | 0.25 [0, 1] | 16.00 [11, 21] |
| max(flips PC, flips GES) theo lần sinh: trung bình [nhỏ nhất, lớn nhất] | 0.20 [0, 1] | 0.10 [0, 1] |
| Δm của FoundCause: trung bình [nhỏ nhất, lớn nhất] | +0.25 [0, +1] | +15.60 [+7, +21] |
| Δp của FoundCause: trung bình [nhỏ nhất, lớn nhất] | 0.0401 [0.0355, 0.0446] | 0.1357 [0.1243, 0.1546] |
| Tham chiếu lịch ở k0, base 1042 / 2042 / 3042 / 4042 | 0 / 0 / 0 / 0 (trung bình 0, lớn nhất 0) | 0 / 1 / 0 / 1 (trung bình 0.5, lớn nhất 1) |
| flips của AVICI trên cùng lần sinh (P-N5) | 2.85 [1, 4] | 5.40 [1, 16] |
| flips của CDFM trên cùng lần sinh (P-N5) | 1.50 [1, 4] | 11.00 [7, 16] |

**Đọc bảng (mô tả):**

- **Wine:**
  - flips gần như hoàn toàn đến từ cạnh được thêm vào. Δm trung bình +15.6 so với flips 16.0: số cạnh trên 55 cặp tăng từ 8 lên khoảng 24;
  - cả 20 lần sinh đều có D_r ≥ 11.
- **Sachs:**
  - xác suất cạnh có đổi (Δp trung bình 0.0401), nhưng skeleton hầu như không đổi;
  - CI của E_r[D_r] nằm trong ±1 cặp (nhãn cỡ SMALL). Đây là mô tả: không phải phép kiểm tương đương, không được Holm bảo vệ, và không chứng minh FoundCause ổn định trên bảng này.
- **Tham chiếu lịch:**
  - đổi cả lịch suy luận ở k0 làm đổi nhiều nhất 1 cặp ở Wine và 0 cặp ở Sachs;
  - theo luật, tham chiếu này đo biến động của toàn bộ lịch (mẫu con hàng, hoán vị cột, nhiễu tie-break). Nó không phải đối chứng riêng cho hoán vị cột, không phải ngưỡng, và không được lấy trừ khỏi flips.
- **AVICI và CDFM:** đặt cạnh để mô tả, không kiểm. Không có phép so sánh nào giữa các model.
- **Cột bị bỏ:** `sanitize` của FoundCause không bỏ cột nào ở mọi input (`dropped` rỗng, `n_duplicates` = 0).

## 3. Điều không được viết (theo §9 của luật)

- Không viết câu nào về độ chính xác, hay rằng FoundCause sai.
- Không viết "mọi model học sẵn đều bất ổn".
- Không kết luận cho k = 40, cho đệm có cấu trúc, hay cho biến có sẵn trong dữ liệu thật.
- Không viết rằng FoundCause bất ổn hơn hay kém hơn AVICI hoặc CDFM. Các số ở §2 chỉ là mô tả.
- Không viết rằng P7-1S không được xác nhận nghĩa là FoundCause ổn định trên Sachs.
- Không viết rằng độ bất ổn ở Wine là do thông tin trong cột thêm vào. P7-1 không tách phần đó khỏi thay đổi tính toán nội bộ khi D đổi, như hoán vị cột ở base cố định.
- Không viết rằng input là dữ liệu held-out mới.
- Không viết rằng kết quả về cơ chế ngưỡng của CDFM hay cách sửa R-L áp dụng cho FoundCause.
- Không viết rằng CI hay nhãn cỡ được Holm bảo vệ.

## 4. Đề xuất cập nhật (chờ user duyệt; chưa sửa)

**Sổ claim, C11.**

- Giữ riêng hai nguồn bằng chứng, mỗi nguồn với family Holm của nó:
  - P-N5: AVICI và CDFM, cả hai bảng, 4/4 CONFIRMED;
  - P-N7: FoundCause, Wine CONFIRMED, Sachs NOT_CONFIRMED.
- **Câu đề xuất:** "Trên hai bảng thật cố định, skeleton của AVICI và CDFM đổi nhiều hơn đối chứng cổ điển ở cả hai bảng (Study 4). Skeleton của FoundCause đổi nhiều hơn đối chứng cổ điển trên bảng Wine, không được xác nhận trên bảng Sachs (Study 6)."
- Không mở rộng C11 thành một claim chung cho cả ba model.

**Bản thảo (nhánh riêng, sau khi duyệt):**

- §7: thêm Study 6 (một bảng và đoạn đọc theo §9 của luật);
- tóm tắt, phần đóng góp, Bảng 1 và Phụ lục A: thêm hàng Study 6;
- có thể thêm cột FoundCause vào Hình 1c (mô tả).

## 5. File

- [`checks/pn7_completeness.json`](checks/pn7_completeness.json), [`checks/pn7_reading.json`](checks/pn7_reading.json), [`checks/pn7_run_header.json`](checks/pn7_run_header.json): bản sao từ `artifacts/n7_runs/pn7_out/`.
- [`posthoc/recheck_pn7.py`](posthoc/recheck_pn7.py) và [`posthoc/recheck_output.txt`](posthoc/recheck_output.txt).
- Output thô (`.npz`) và log nằm trong `artifacts/n7_runs/pn7_out/` (không đưa vào git).
