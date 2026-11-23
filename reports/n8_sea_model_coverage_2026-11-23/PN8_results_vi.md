# P-N8: kết quả, SEA trên phép thử khối đích cố định (Study 7)

> **Luật:** [PN8_rules_vi.md](PN8_rules_vi.md) v1, khóa ở `49558ae` (push 2026-11-23T07:40:54Z).
>
> **Code:** đóng băng ở `9e902ed` (push 2026-11-23T08:47:52Z). Gồm 23 file và 374 mã băm phụ thuộc; trong đó 152 là các file tracked của bản clone SEA ở `bfb507b`, kể cả checkpoint.
>
> **Lượt chính** (UTC, 23/11):
>
> - A1 08:49:04–10:18:45; A2 10:18:46–11:22:28; A3 11:22:30–12:53:05; A4 12:53:07–14:18:27;
> - B 14:18:28–15:34:29;
> - sau đó là PC và GES trên 60 hệ tuyến tính.
>
> **Đọc:** bằng code đã đóng băng (`analyze8.py`), sau khi kiểm hoàn tất đạt. Kiểm lại bằng một script độc lập, viết trước khi đọc output chính.
>
> **Phạm vi:**
>
> - một model (SEA), một checkpoint (FCI synthetic), code đã phát hành;
> - phần A: 120 hệ tổng hợp held-out mới. Phần B: input của Study 4 được dùng lại, **không phải dữ liệu held-out mới**;
> - sáu giả thuyết là một family Holm riêng;
> - cờ: G3 PASS, G4 không có cờ. Nhánh đệm xen (IL) không chạy, vì G3 không gắn nhãn POSITION_SENSITIVE.

## 0. Tóm tắt

| ID | Phần | Contrast | Ước lượng [CI 95%] | t (df) | p một phía | Holm (hạng, ngưỡng) | Label | Size |
|---|---|---|---|---|---|---|---|---|
| P8-1 | A, 120 hệ | Δ, A20 (Gauss) | +5.84 [+5.06, +6.61] cặp | 15.12 (44.7) | 1.7 × 10⁻¹⁹ | 1, 0.0083 | **CONFIRMED** | LARGE |
| P8-1S | A, 120 hệ | Δ, S20 (có cấu trúc) | +4.50 [+3.86, +5.13] cặp | 14.19 (49.1) | 2.7 × 10⁻¹⁹ | 2, 0.0100 | **CONFIRMED** | LARGE |
| P8-2 | A, 120 hệ | H = F1(k0) − F1(A20) | +0.049 [+0.035, +0.063] | 6.89 (89.1) | 3.8 × 10⁻¹⁰ | 4, 0.0167 | **CONFIRMED** | UNCLEAR |
| P8-3 | A, 60 hệ tuyến tính | H_SEA − max(H_PC, H_GES) | +0.065 [+0.041, +0.088] | 5.57 (47.8) | 5.7 × 10⁻⁷ | 5, 0.0250 | **CONFIRMED** | UNCLEAR |
| P8-4S | B, Sachs | Δ, đệm Gauss k = 20 | +0.18 [−0.07, +0.42] cặp | 1.51 (19) | 0.074 | 6, 0.0500 | **NOT_CONFIRMED** | SMALL |
| P8-4W | B, Wine | Δ, đệm Gauss k = 20 | +5.88 [+4.82, +6.93] cặp | 11.60 (19) | 2.3 × 10⁻¹⁰ | 3, 0.0125 | **CONFIRMED** | LARGE |

**Cách tính:**

- Phần A dùng t phân tầng: trọng số bằng nhau cho 8 ô (4 ô ở P8-3), df Welch–Satterthwaite. Phần B dùng t có df = 19. Đây là xấp xỉ, vì Δ là trung bình của các số đếm.
- Biên là 1 cặp cho Δ và 0.05 cho H.
- CI và Size là mô tả. Chúng không được Holm bảo vệ và không phải phép kiểm tương đương.

**Câu đọc** (theo "Cách đọc" ở §4 của luật):

- **P8-1:** "Trên 120 hệ tổng hợp held-out mới, sau khi thêm 20 cột Gauss độc lập, skeleton khối đích của SEA nằm xa các output k0 ở seed khác hơn so với output k0 cùng seed. Theo flips, mức chênh trung bình là 5.84 cặp (CI 95% 5.06–6.61; trung bình đều theo 8 ô). CI nằm trọn trên biên 1 cặp."
- **P8-1S:** cùng câu, với 20 cột có cấu trúc: 4.50 cặp (3.86–5.13), CI nằm trọn trên biên.
- **P8-2:** "Khi thêm 20 cột Gauss, F1 skeleton khối đích giảm ở mức dấu, trung bình 0.049 (0.035–0.063)." Kết quả không xác lập được rằng mức giảm vượt biên 0.05. Nó cũng không xác lập được rằng mức giảm nằm trong biên.
- **P8-3:** "Trên 60 hệ tuyến tính, khi thêm 20 cột Gauss, F1 của SEA giảm nhiều hơn mức giảm lớn hơn trong hai đối chứng PC và GES, ở mức dấu: 0.065 (0.041–0.088)." Kết quả không xác lập được rằng mức chênh vượt 0.05.
- **P8-4W:** "Trên bảng Wine, output khối đích sau khi thêm đệm nằm xa các output k0 tham chiếu hơn output k0 cùng seed: 5.88 cặp (4.82–6.93) trên 55 cặp." Cả 20 lần sinh đều dương.
- **P8-4S:** "Trên bảng Sachs, giả thuyết không được xác nhận: 0.18 cặp (−0.07 đến 0.42)." CI nằm trong ±1 cặp (SMALL). Đây không phải phép kiểm tương đương, nên không thể viết rằng SEA ổn định trên Sachs.

**Suy luận từ Δ dương** (chỉ đúng một chiều):

- Với một input cố định, nếu phân phối skeleton khối đích qua seed không đổi khi thêm đệm thì E[Δ] = 0 (luật §0, §3). Vì vậy, Δ dương được xác nhận ở P8-1, P8-1S và P8-4W cho phép kết luận rằng thêm đệm đã làm đổi phân phối skeleton khối đích qua seed, có điều kiện trên input.
- Ở phần A, kết luận dựa trên trung bình đều theo ô. Nó không xác nhận thay đổi cho từng ô hay từng hệ, và không phải phép kiểm phân phối đồ thị sau khi gộp tất cả các hệ.
- Chiều ngược lại không đúng. Ở Sachs, việc không xác nhận Δ > 0 không cho thấy phân phối skeleton không đổi.

## 1. Tính toàn vẹn

- **Cổng đóng băng:** đạt ở `precheck` và ở đầu, cuối cả năm lượt (`pn8_start_*`, `pn8_end_*`).
  - Mọi header đều ghi `9e902ed` và `origin/docs/n1-pilot`, với danh sách vấn đề rỗng.
  - Sau lượt cuối, agent chạy thêm cổng hai lần: `post_runs_check` lúc 15:42:23Z, trước kiểm hoàn tất; và `pre_commit_results_check` lúc 15:50:48Z, trước khi commit báo cáo này. Cả hai đều đạt. Mỗi lần chỉ đọc và ghi thêm một header; quy trình không yêu cầu hai lần chạy này.
- **Kiểm hoàn tất** ([`checks/pn8_completeness.json`](checks/pn8_completeness.json)) đạt, 0 vấn đề:
  - A1–A4 mỗi lượt 212/212 job `ok`; B 242/242; tổng 1090 job;
  - mỗi job dự kiến có đúng một bản ghi `ok`, với seed và số input đúng;
  - mã băm input sinh lại khớp. Ở phần B, mã băm khớp `inputs5.json` của Study 4;
  - adapter đạt; các lần chạy lại trùng từng bit;
  - khối đích trùng từng bit giữa k0, A20 và S20;
  - chỉ có một commit đóng băng;
  - PC và GES: 120/120 output mỗi thuật toán.
- **Ngân sách** (§8 của luật):

  | Lượt | Thời gian | Mốc dừng |
  |---|---|---|
  | A1 | 1.49 h | 2.1 h |
  | A2 | 1.06 h | 2.1 h |
  | A3 | 1.51 h | 3.0 h |
  | A4 | 1.42 h | 3.0 h |
  | B | 1.27 h | 2.5 h |

  - Tổng 6.75 h, so với ước tính 9.3 h của G5. Không lượt nào chạm mốc dừng.
  - Thời gian trung bình mỗi tiến trình là 19.3 s ở D = 10 và 40.6 s ở D = 40, thấp hơn trung bình đo ở DEV (26.5 s và 65.2 s).
  - Bộ nhớ đỉnh 1.66 GB.
- **Kiểm lại độc lập** ([`posthoc/recheck_pn8.py`](posthoc/recheck_pn8.py); output ở [`posthoc/recheck_output.txt`](posthoc/recheck_output.txt)):
  - Script không import code phân tích của Study 7 (`common8`, `stats8`, `analyze8`) hay thống kê đã đóng băng. Từ file `.npz` thô, nó tự dựng lại skeleton, Δ, H, F1, t phân tầng, t ghép cặp, Holm và Size. Seed được tính lại theo công thức ở §2 của luật. Code đóng băng duy nhất nó dùng là bộ sinh khối đích của P-N1, để sinh lại đồ thị thật.
  - Kết quả khớp hoàn toàn với `pn8_reading.json` ở cả hai cách đọc skeleton: sai khác lớn nhất 0.0 trên ước lượng, SE, p và hai đầu CI; không lệch Label, Size hay hạng Holm.
  - Script ở commit `86d39fe` (08:50:12Z), trước khi lượt A1 xong, và trước lần đọc lúc 15:43:03Z. Commit này **chỉ là commit cục bộ**: trước khi push, thời điểm của nó chưa có bằng chứng bên ngoài.
- **Quy trình:** agent không đọc kết quả giữa các lượt. File luật và snapshot code không đổi trong suốt các lượt; cổng đóng băng cuối mỗi lượt kiểm điều này.

## 2. Mô tả (không thuộc bộ Holm)

Các số dưới đây lấy từ `pn8_reading.json`, theo các số đo mô tả ở §3 của luật. Riêng các cột đếm dấu (+/0/−) và khoảng giá trị là đếm thêm, không được ghi trước trong §3.

**Phần A, theo ô** (cách đọc NATIVE; trung bình trên 15 hệ; 45 cặp đích khi d_T = 10, 190 cặp khi d_T = 20):

| Ô | d_T, e_T, họ | F1 ở k0 | Số cạnh k0 → A20 → S20 | flips chỉ do seed | flips cùng seed, A20 | Δ A20 | Δ S20 | H, A20 | H, S20 | ΔTP; ΔFP, A20 |
|---|---|---|---|---|---|---|---|---|---|---|
| c0 | 10, 1, lin | 0.823 | 11.3 → 8.7 → 9.4 | 1.57 | 4.20 | 2.60 | 1.90 | 0.036 | 0.065 | −1.27; −1.33 |
| c1 | 10, 1, rff | 0.701 | 9.9 → 8.7 → 9.5 | 1.03 | 1.60 | 0.87 | 0.93 | 0.019 | −0.005 | −0.67; −0.53 |
| c2 | 10, 2, lin | 0.633 | 22.4 → 10.3 → 16.3 | 6.75 | 15.67 | 9.07 | 7.47 | 0.205 | 0.118 | −7.00; −5.07 |
| c3 | 10, 2, rff | 0.622 | 16.7 → 12.7 → 14.5 | 2.07 | 5.53 | 3.37 | 2.27 | 0.047 | 0.030 | −2.07; −1.87 |
| c4 | 20, 1, lin | 0.630 | 26.1 → 19.5 → 23.7 | 6.22 | 13.47 | 7.53 | 5.33 | 0.003 | 0.045 | −1.93; −4.73 |
| c5 | 20, 1, rff | 0.715 | 20.6 → 19.0 → 21.0 | 2.75 | 5.47 | 2.63 | 1.33 | 0.018 | −0.006 | −0.87; −0.73 |
| c6 | 20, 2, lin | 0.411 | 48.8 → 35.9 → 43.3 | 17.73 | 36.80 | 17.47 | 15.07 | 0.048 | 0.088 | −4.73; −8.20 |
| c7 | 20, 2, rff | 0.583 | 34.5 → 32.5 → 34.2 | 6.58 | 9.80 | 3.17 | 1.67 | 0.017 | 0.015 | −1.27; −0.80 |
| Trung bình đều | | 0.640 | 23.8 → 18.4 → 21.5 | 5.59 | 11.57 | 5.84 | 4.50 | 0.049 | 0.044 | −2.48; −2.91 |

Δp (trung bình |P − P(k0)| trên các cặp có thứ tự) là 0.089 với A20 và 0.067 với S20, so với 0.027 khi chỉ đổi seed.

**Phần A, đếm dấu và đối chứng cổ điển** (đối chứng cổ điển chỉ có trên các ô tuyến tính):

| Ô | Δ A20 +/0/− | Δ S20 +/0/− | H +/0/− | H nhỏ nhất, lớn nhất | H_PC | H_GES | flips PC; GES | H_SEA − max(H_PC, H_GES) |
|---|---|---|---|---|---|---|---|---|
| c0 | 13/1/1 | 12/1/2 | 9/1/5 | −0.094, +0.255 | −0.008 | +0.008 | 0.13; 0.40 | +0.023 |
| c1 | 9/4/2 | 8/6/1 | 9/3/3 | −0.200, +0.153 | | | | |
| c2 | 15/0/0 | 15/0/0 | 15/0/0 | +0.037, +0.385 | 0.000 | +0.008 | 0.00; 1.20 | +0.193 |
| c3 | 12/2/1 | 12/2/1 | 11/1/3 | −0.099, +0.161 | | | | |
| c4 | 14/1/0 | 13/1/1 | 8/0/7 | −0.073, +0.097 | 0.000 | +0.001 | 0.00; 0.40 | −0.002 |
| c5 | 13/1/1 | 11/2/2 | 8/0/7 | −0.060, +0.114 | | | | |
| c6 | 15/0/0 | 15/0/0 | 9/0/6 | −0.092, +0.206 | +0.003 | −0.001 | 0.13; 0.40 | +0.044 |
| c7 | 13/0/2 | 11/0/4 | 11/0/4 | −0.074, +0.126 | | | | |
| Tổng số hệ | 104/9/7 | 97/12/11 | 80/5/35 | | | | | 38/1/21 (60 hệ) |

**Phần B** (55 cặp mỗi bảng, 20 lần sinh; trung bình [nhỏ nhất, lớn nhất]):

| Số đo | Sachs | Wine |
|---|---|---|
| Số cạnh của SEA, k0 → đệm | 4.85 → 4.50 | 20.85 → 14.00 |
| flips chỉ do seed (trung bình 4 seed tham chiếu) | 0.28 [0, 1.25] | 3.16 [0.5, 5.0] |
| flips cùng seed, k0 → đệm | 0.55 [0, 2] | 8.85 [6, 12] |
| Δ; +/0/− | +0.18 [−1, +1]; 6/12/2 | +5.88 [+2, +11]; 20/0/0 |
| flips PC; GES (Study 4) | 0.15; 0.05 | 0.00; 0.10 |
| Contrast kiểu C11: flips cùng seed − max(PC, GES); +/0/− | +0.35 [−1, +1]; 9/9/2 | +8.75 [+6, +12]; 20/0/0 |
| Δp, đệm so với k0 cùng seed; Δp chỉ do seed | 0.012; 0.011 | 0.090; 0.041 |

**Cách đọc phụ** (cạnh khi 1 − P(không cạnh) > 0.5; phân tích độ nhạy định trước, không Holm):

| ID | Ước lượng [CI 95%] | p một phía (không hiệu chỉnh) | Size |
|---|---|---|---|
| P8-1 | +12.63 [+10.03, +15.24] | 6.0 × 10⁻⁹ | LARGE |
| P8-1S | +7.02 [+5.31, +8.73] | 4.4 × 10⁻⁸ | LARGE |
| P8-2 | +0.034 [+0.022, +0.045] | 5.7 × 10⁻⁸ | SMALL |
| P8-3 | +0.031 [+0.010, +0.053] | 2.8 × 10⁻³ | UNCLEAR |
| P8-4S | +0.05 [−0.05, +0.15] | 0.165 | SMALL |
| P8-4W | +4.38 [+3.61, +5.14] | 1.4 × 10⁻¹⁰ | LARGE |

**Đọc bảng.** Các số liệu là fact đã đo. Mọi giải thích đều được đánh dấu là suy luận.

1. **Thêm đệm chủ yếu làm SEA bỏ cạnh** (fact, mô tả).
   - Với A20, số cạnh khối đích giảm ở cả 8 ô. Xét từng hệ: 97/120 hệ giảm, 10 hệ không đổi, 13 hệ tăng. Ở Wine, số cạnh giảm từ 20.85 xuống 14.0.
   - Cả cạnh đúng lẫn cạnh sai đều giảm: ΔTP −2.48, ΔFP −2.91 (trung bình đều theo ô).
   - Đệm có cấu trúc làm mất ít cạnh hơn đệm Gauss: còn 21.5 cạnh, so với 18.4.
2. **Mức hại rất không đều giữa các ô** (fact; phép tính phụ là post hoc).
   - Ở ô c2 (d_T = 10, e_T = 2, tuyến tính), cả 15/15 hệ có H > 0; trung bình 0.205, và số cạnh giảm từ 22.4 xuống 10.3.
   - Bảy ô còn lại có H trung bình từ 0.003 đến 0.048. Trung bình đều của bảy ô này là 0.027 (phép tính post hoc, không kiểm).
   - Trên cả 120 hệ: 80 hệ dương, 5 bằng 0, 35 âm.
   - Vì vậy, P8-2 là kết luận về dấu của trung bình đều theo ô. Không viết "SEA mất khoảng 0.05 F1" như một mức chung.
3. **Biến động do seed lớn** (fact).
   - Chỉ đổi seed ở k0, skeleton đổi trung bình 5.59 cặp ở phần A (17.7 ở c6), 3.16 ở Wine và 0.28 ở Sachs.
   - Flips cùng seed sau khi thêm đệm là 11.57 ở phần A và 8.85 ở Wine. Khi D khác nhau, cùng một seed không giữ được các tập con biến, nên số này gộp cả biến động lịch suy luận. Δ mới là contrast để đọc.
   - Ở Wine, contrast kiểu C11 (dựa trên flips cùng seed) là 8.75, lớn hơn Δ (5.88). PC và GES là thuật toán tất định, nên contrast này không trừ đi phần do seed. Theo luật, contrast này chỉ là mô tả.
4. **Cách đọc phụ** (fact; phân tích độ nhạy).
   - Cả sáu contrast cùng chiều với cách đọc chính.
   - Δ ở phần A lớn hơn (12.6 so với 5.8), chủ yếu do c2 và c6. Ở hai ô này, output k0 theo cách đọc phụ dày hơn nhiều; ví dụ ở c6 là 111 cạnh trên 190 cặp, so với 48.8 ở cách đọc chính.
   - Mức hại nhỏ hơn: CI của P8-2 là [0.022, 0.045], nằm trong biên 0.05 (SMALL); P8-3 còn 0.031 (UNCLEAR).
   - Các ước lượng cùng dấu ở hai cách đọc skeleton đã thử, còn độ lớn của mức hại khác nhau giữa hai cách đọc. Nhận xét này không mở rộng sang mọi decoder.
5. **Sachs** (fact).
   - Ở k0, SEA chỉ có 4–5 cạnh trên 55 cặp. Cả skeleton lẫn xác suất cạnh đều đổi ở mức gần với biến động do seed: Δp 0.012, so với 0.011.
   - Skeleton thưa chỉ có ít cạnh để bỏ thêm, nhưng vẫn còn khoảng 50 cặp có thể thêm cạnh. Vì vậy, không suy ra rằng phép thử ở Sachs thiếu chỗ để phát hiện thay đổi nói chung. Không gọi kết quả này là ổn định.
6. **S20 so với A20, đặt cạnh bước 1** (suy luận post hoc, chưa kiểm).
   - Ở bước 1 (hệ phát triển, chỉ đo phía input), đệm có cấu trúc làm độ phủ cặp đích giảm nhiều hơn đệm Gauss: còn 0.22 lần mức ở k0, so với 0.44 lần.
   - Ở lượt chính, S20 lại làm output đổi ít hơn A20: Δ 4.50 so với 5.84; mất 2.3 cạnh so với 5.4.
   - Thứ tự quan sát không phù hợp với cách giải thích đơn giản rằng độ phủ càng giảm thì Δ càng tăng. Điều này chưa loại trừ vai trò của độ phủ, hay tương tác của độ phủ với các yếu tố khác.
   - Đây là đọc chéo giữa một pilot exploratory và kết quả chính, không phải một phép kiểm. Kênh gây ra thay đổi vẫn chưa được xác định (§0 của luật).
7. **Đối chứng cổ điển** (fact).
   - Trên hệ tuyến tính, PC và GES gần như không đổi: flips 0.07 với PC và 0.60 với GES; H_PC −0.001, H_GES +0.004.
   - Vì vậy, trên các ô tuyến tính, contrast của P8-3 gần bằng H của SEA; 38/60 hệ có contrast dương.

## 3. Điều không được viết

- Không viết rằng SEA ổn định trên Sachs, hay "ổn định trong biên" ở bất kỳ contrast nào có Size SMALL.
- Không chỉ ra kênh gây thay đổi (phân bổ lô, thống kê toàn cục hay aggregator). Không viết rằng nguyên nhân nằm ở thiết kế tổng hợp trên tập con nói chung.
- Không mở rộng kết quả sang mọi model tổng hợp trên tập con, sang checkpoint khác, hay sang k = 40.
- Không so sánh SEA với AVICI, CDFM hay FoundCause như một phép kiểm, và không xếp hạng các model.
- Không viết rằng SEA mất ít nhất 0.05 F1, hay mất khoảng 0.05 F1 như một mức chung.
- Không viết về độ chính xác của SEA trên bảng thật.
- Không viết rằng toàn bộ điều kiện thử nằm trong phân phối huấn luyện của SEA; điều này chưa được xác lập. Cụ thể: RFF không có trong các cơ chế huấn luyện; số biến sau khi thêm đệm (D = 30 và 40 ở phần A; 31 ở phần B) nằm giữa các kích thước đã công bố N = 10, 20, 100 nhưng không trùng; mỗi tập huấn luyện có 1000N hàng, còn ở đây n = 500, bằng kích thước lô.
- Không viết rằng phần B là dữ liệu held-out mới.
- Không viết rằng CI hay Size được Holm bảo vệ, hay rằng cách đọc phụ là một xác nhận.
- Không viết rằng Δ đo độ ổn định sau khi loại nhiễu seed.

## 4. Cập nhật đã duyệt (user, 23/11; chi tiết ở §6)

**Sổ claim, C16:** claim riêng cho Study 7. Không nhập vào C1 (ba model, dữ liệu tổng hợp) hay C11 (bảng thật).

- **Câu (user duyệt):** "Với một checkpoint SEA tổng hợp các ước lượng FCI trên tập con biến, trên 120 hệ tổng hợp mới, việc thêm một khối 20 biến độc lập với khối đích — Gauss hoặc có cấu trúc nội bộ — làm tăng khoảng cách trung bình từ skeleton đích tới các output k0 tham chiếu. Với đệm Gauss, F1 skeleton giảm trung bình; trên các hệ tuyến tính, mức giảm vượt đối chứng PC/GES theo contrast đã khóa. Hai kết luận F1 được xác nhận về dấu, chưa xác lập vượt biên thực tiễn 0,05. Trên hai bảng thật cố định, kết quả về khoảng cách được xác nhận ở Wine, nhưng không được xác nhận ở Sachs."
- **Trạng thái từng giả thuyết** (Holm 0.05 trên sáu giả thuyết, family riêng):
  - P8-1 (Δ, A20): CONFIRMED, LARGE;
  - P8-1S (Δ, S20): CONFIRMED, LARGE;
  - P8-2 (F1, A20): CONFIRMED, UNCLEAR;
  - P8-3 (F1 so với PC/GES, A20, hệ tuyến tính): CONFIRMED, UNCLEAR;
  - P8-4W (Δ, Wine): CONFIRMED, LARGE;
  - P8-4S (Δ, Sachs): NOT_CONFIRMED, SMALL.
- **Giới hạn đi kèm:**
  - hai kết luận về F1 (P8-2, P8-3) chỉ áp dụng cho đệm Gauss A20. Với đệm có cấu trúc, giả thuyết được xác nhận duy nhất là về Δ (P8-1S); mức giảm F1 ở S20 chỉ là mô tả;
  - một model và một checkpoint;
  - dữ liệu tổng hợp sinh bằng simulator của AVICI;
  - không xác lập rằng toàn bộ điều kiện thử nằm trong phân phối huấn luyện của SEA. Cụ thể: RFF không có trong các cơ chế huấn luyện; mỗi tập huấn luyện có N = 10, 20 hoặc 100 biến và 1000N hàng, còn ở đây mỗi input có n = 500 hàng (bằng kích thước lô) và, sau khi thêm đệm, D = 30 hoặc 40 biến ở phần A, 31 ở phần B;
  - độ lớn mức hại là UNCLEAR, giảm xuống SMALL ở cách đọc phụ, và tập trung ở ô c2;
  - Δ chỉ đọc được một chiều; kết quả trung bình ở phần A không xác nhận thay đổi cho từng hệ;
  - kênh gây thay đổi chưa xác định;
  - phần B dùng lại input của Study 4.

**Bản thảo** (nhánh riêng):

- mục Study 7 với bảng riêng: sáu hàng, hai cột Label và Size;
- sự không đồng đều giữa các ô nằm trong văn bản chính: ô c2 đóng góp khoảng 52% mức giảm F1 trung bình; bảy ô còn lại trung bình 0.0269. Đây là mô tả hậu nghiệm;
- bảng theo ô và cách đọc phụ ở phụ lục;
- pattern của ô c2 và của độ phủ đưa vào phần thảo luận; không mở thêm lượt thí nghiệm;
- tóm tắt: thêm câu của user về Study 7, không ghi số giả thuyết đạt;
- tiêu đề không đếm số model. Câu mở đầu không mô tả cả bốn model như cùng dự đoán đồ thị trực tiếp từ toàn bảng. Kết quả Study 1 giữ phạm vi ba checkpoint ban đầu.

**Push:** `86d39fe`, `bb4658e` và commit đính chính này (user duyệt).

## 5. File

- [`checks/pn8_completeness.json`](checks/pn8_completeness.json), [`checks/pn8_reading.json`](checks/pn8_reading.json), [`checks/pn8_run_header.json`](checks/pn8_run_header.json): bản sao trùng từng byte của các file trong `artifacts/n8_runs/pn8_out/`.
- [`posthoc/recheck_pn8.py`](posthoc/recheck_pn8.py) và [`posthoc/recheck_output.txt`](posthoc/recheck_output.txt).
- Output thô (`.npz`) và log nằm trong `artifacts/n8_runs/pn8_out/`, không đưa vào git.

## 6. Sau review của user (23/11)

- **User kiểm lại:**
  - tính lại Δ từ output `.npz`, tính lại các phép kiểm từ số liệu theo hệ và kiểm hạng Holm: khớp, sai khác số học tối đa khoảng 1.4 × 10⁻¹⁴;
  - các log có đủ 1090 job `ok`; ba file kiểm trong `checks/` trùng từng byte với bản trong `artifacts/`.
- **Quyết định:**
  - đưa Study 7 vào bài và thêm C16 riêng, với câu ở §4;
  - kết quả bổ sung bằng chứng cho một pipeline tổng hợp trên tập con; chưa xác định thêm cơ chế;
  - đóng phần mở rộng SEA tại đây. Pattern của ô c2 và của độ phủ đưa vào phần thảo luận; chưa mở thêm lượt thí nghiệm;
  - push `86d39fe`, `bb4658e` cùng commit đính chính này. Giữ lưu ý ở §1: thời điểm tạo script kiểm lại là thời điểm của một commit cục bộ, chưa có bằng chứng thời gian bên ngoài.
- **Đính chính câu chữ trong commit này** (so với `bb4658e`):
  - §0: suy luận từ Δ dương nói về phân phối skeleton qua seed, có điều kiện trên input. Kết quả trung bình ở phần A không xác nhận thay đổi cho từng hệ, và không phải phép kiểm phân phối đồ thị sau khi gộp tất cả các hệ;
  - §0, câu đọc của P8-3: ghi rõ đệm Gauss;
  - §2 mục 4: "dấu không phụ thuộc cách đọc skeleton" đổi thành "các ước lượng cùng dấu ở hai cách đọc skeleton đã thử"; không mở rộng sang mọi decoder;
  - §2 mục 5: bỏ suy luận "ít chỗ để phát hiện thay đổi". Skeleton thưa chỉ có ít cạnh để bỏ thêm, nhưng vẫn có nhiều cặp để thêm cạnh;
  - §2 mục 6: câu về độ phủ đổi thành "Thứ tự quan sát không phù hợp với cách giải thích đơn giản rằng độ phủ càng giảm thì Δ càng tăng", kèm ghi chú rằng vai trò của độ phủ, hay tương tác với các yếu tố khác, chưa bị loại trừ;
  - giới hạn của C16, và để thống nhất là gạch đầu dòng tương ứng ở §3: "không in-distribution" đổi thành "không xác lập rằng toàn bộ điều kiện thử nằm trong phân phối huấn luyện của SEA", kèm RFF và khác biệt về số hàng và số biến;
  - §4: câu C16 của user; hai kết luận F1 chỉ áp dụng cho đệm Gauss A20; với đệm có cấu trúc, chỉ giả thuyết về Δ được xác nhận.

- **Đính chính số sau khi push** (agent phát hiện ngày 23/11, khi kiểm có đích từng ước lượng và CI so với `pn8_reading.json` trước khi đưa vào bản thảo; chờ user duyệt push):
  - CI của P8-1 là [+5.06, +6.61], không phải [+5.06, +6.62] (§0, bảng và câu đọc). Cận trên là 6.61499…; bản trước đã làm tròn hai lần từ bản in ba chữ số (6.615);
  - CI của P8-4S ở cách đọc phụ là [−0.05, +0.15], không phải [−0.06, +0.16] (§2). Hai đầu là −0.0547 và +0.1547, cùng lỗi làm tròn hai lần;
  - nhãn và Size không đổi: cận dưới 5.06 vẫn trên biên 1 cặp, và [−0.05, +0.15] vẫn nằm trong ±1 cặp. Các bảng mô tả ở §2 đã được so từng ô với `pn8_reading.json`: không có lệch khác.
