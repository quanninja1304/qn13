# P-N9 (Study 8): chọn các mức n và số hệ (phân tích thiết kế, chưa khóa)

> **Trạng thái:** phân tích thiết kế, viết trước bản nháp rules. Chưa có quy tắc nào được khóa, và chưa chạy model nào cho P-N9.
>
> **Nguồn số liệu:**
>
> - output đã lưu của Study 1 (held-out, n = 500) và Study 7 (n = 500);
> - log thời gian chạy của hai study đó;
> - code, config và bài gốc của các model.
>
> **File:**
>
> - Script: [design/pn9_n_grid_design.py](design/pn9_n_grid_design.py). Output đầy đủ ở [design/pn9_n_grid_design_output.txt](design/pn9_n_grid_design_output.txt).
> - Sơ đồ: [design/pn9_n_grid_diagram.py](design/pn9_n_grid_diagram.py). Ảnh lưu ngoài repo, tại `artifacts/n9_runs/design/pn9_n_grid.png`.
>
> **Nhãn:** *sự kiện* là điều đã kiểm trong nguồn hoặc code; *suy luận* là điều tính ra từ sự kiện nhưng chưa đo.

## 1. Câu hỏi và figure cần có

**Câu hỏi.** Hiện tượng có còn không khi n khớp với chế độ huấn luyện của từng model? Trong khoảng huấn luyện, hiện tượng có giảm khi n tăng không? Ở đây "hiện tượng" gồm:

- F1 mất đi khi thêm 20 cột Gaussian độc lập, H = F1(k = 0) − F1(k = 20);
- Δ của SEA.

**Figure chính (đề xuất):**

- Bốn panel nhỏ: AVICI, CDFM, FoundCause, SEA.
- Trục x là n theo thang log. Trục y là H, cùng đơn vị F1 và dùng chung cho cả bốn panel.
- Mỗi mức n là một điểm có CI 95%. Điểm đặc nếu n nằm trong chế độ huấn luyện của model, rỗng nếu nằm ngoài. Dải nền đánh dấu chế độ huấn luyện.
- n = 500 được đánh dấu để nối với Studies 1–7.

**Figure phụ:**

- H trên hệ tuyến tính, cạnh PC và GES;
- flips;
- Δ của SEA.

Δ có đơn vị khác H (số cặp), nên đặt ở hình riêng; không dùng hai trục y.

## 2. Ràng buộc theo model

| Model | Chế độ huấn luyện (sự kiện) | Ràng buộc về code hoặc phần cứng | Hệ quả cho các mức n |
|---|---|---|---|
| AVICI `scm-v0` | Mỗi ví dụ huấn luyện có 200 dòng: 150 quan sát + 50 can thiệp, hoặc 200 dòng quan sát với xác suất 0,5 (`kwargs.json` của checkpoint, `data.py`, `data_jax.py`) | **Attention:** đầy đủ theo trục dòng, 8 đầu (`kwargs.json`). **RAM máy:** 7,8 GB. **Bộ nhớ (suy luận):** logits attention của một lớp với D = 40 cột chiếm khoảng 40 × 8 × n² × 4 byte, tức 0,32 GB ở n = 500, 1,3 GB ở 1000 và 5,1 GB ở 2000 | n = 2000 gần như không chạy được trên máy này. n = 1000 phải kiểm ở DEV |
| CDFM | "sample size … drawn uniformly from … [50,4096]" (§5.4). Benchmark của bài dùng N ∈ {500, 1000, 2000, 3000, 4000} (§6.2) | **Kiến trúc:** code dùng `InducedSelfAttentionBlock` và `scaled_dot_product_attention`. **Chi phí (suy luận):** gần tuyến tính theo n | Lên được tới 4000 mà vẫn ở trong khoảng huấn luyện |
| FoundCause | "N∈[100,599] observations" (§2) | Mỗi lượt chạy dùng ceil(0,9 · min(n, 5000)) dòng (README, code) | n ∈ [112, 665] cho 100–599 dòng mỗi lượt. Không vượt 665 được mà vẫn ở trong khoảng |
| SEA | **Dữ liệu huấn luyện:** "1000N points" với N ∈ {10, 20, 100} (§4.1), tức 10.000–100.000 dòng. **Batch:** b = 500 dòng (§3.3), lấy ngẫu nhiên, với giả định "b≪M" (§3.1) | **Code:** `np.random.choice(n, 500, replace=False)`. **Hệ quả của code:** n < 500 thì báo lỗi; ở n = 500, mọi batch chứa đúng cùng 500 dòng | Không xuống dưới 500 được. Chỉ n ≥ 10.000 mới nằm trong khoảng cỡ dữ liệu lúc huấn luyện |
| PC, GES | Không áp dụng | Ở n = 500, trên 40 hệ tuyến tính của Study 1: PC không đổi cặp nào (flips = 0, H = 0); GES đổi trung bình 1,5 cặp (H = 0,009) | Làm mốc tham chiếu ở mọi mức n |

## 3. Bao nhiêu mức n là đủ

- **Thang log.** Dùng chuỗi 1–2–5 (100, 200, 500, 1000, 2000, 5000, …) để các điểm cách đều nhau trên trục log của figure.
- **Độ rộng khoảng n quan trọng hơn số mức n.** Đặt x = log₂ n và Sxx = Σ(x − x̄)². Với CDFM:
  - 2 mức {500, 4000}: Sxx = 4,50;
  - 4 mức {500, 1000, 2000, 4000}: Sxx = 5,00;
  - 6 mức {100, 200, 500, 1000, 2000, 4000}: Sxx = 20,21.

  Thêm hai mức ở giữa chỉ tăng Sxx khoảng 11%. Nới khoảng xuống tới 100 tăng Sxx khoảng 4 lần, nên SE của độ dốc giảm một nửa.
- **Các mức ở giữa phục vụ figure.**
  - Hai điểm chỉ cho một đoạn thẳng.
  - Cần ít nhất 3 điểm để thấy hình dạng: đơn điệu, chữ U hay bậc thang.
  - 4–6 điểm trên trục log là đủ; trên 6 điểm thì gần như không thêm thông tin.
- **Mỗi model phải có n = 500**, để nối với Studies 1–7.
- **Phải phủ chế độ huấn luyện.** Mỗi lưới phải phủ chế độ huấn luyện của chính model đó. Điểm nằm ngoài chế độ huấn luyện chỉ dùng để mô tả và được vẽ rỗng.
- **Điểm chung giữa các model:** 200, 500, 1000 và 2000. Các điểm này cho phép so sánh các model ở cùng n, trên cùng hệ.

## 4. Bao nhiêu hệ là đủ

**Nửa độ rộng CI 95%** của trung bình cân bằng theo ô, tính bằng 1,96 · SD trong ô / √N, với SD lấy từ output đã lưu ở n = 500:

| Đại lượng | N = 24 | N = 40 | N = 80 | N = 120 |
|---|---|---|---|---|
| AVICI H | 0,036 | 0,028 | 0,020 | 0,016 |
| CDFM H | 0,031 | 0,024 | 0,017 | 0,014 |
| FoundCause H | 0,038 | 0,029 | 0,021 | 0,017 |
| SEA H | 0,031 | 0,024 | 0,017 | 0,014 |
| SEA Δ (cặp) | 1,69 | 1,31 | 0,93 | 0,76 |

Với N = 80, CI của H ở mỗi mức n vào khoảng ±0,02. Khoảng này hẹp hơn nhiều so với hiệu ứng đo được ở n = 500 (0,049–0,093), nên figure đọc được. N = 24 (cỡ FoundCause ở Study 1) cho CI khoảng ±0,03–0,04.

**Power.** Mức α một phía là 0,05/8 (Holm, trường hợp xấu nhất cho họ 8 giả thuyết). ρ là tương quan của hiệu ứng theo từng hệ giữa các mức n. Bảng dưới là các con số chính ở N = 80, trình bày theo ρ = 0 / ρ = 0,5:

| Phép kiểm | Kịch bản | Power |
|---|---|---|
| CDFM, xu hướng trên 100–4000 | SHRINKS nếu hiệu ứng mất hẳn trên khoảng | 0,81 / 0,99 |
| | STABLE nếu độ dốc bằng 0 | 0,98 / 1,00 |
| FoundCause, xu hướng trên 125–500 | SHRINKS | 0,67 / 0,95 |
| | STABLE | 0,64 / 0,98 (với N = 40: 0,00 / 0,64) |
| AVICI, xu hướng trên 100–1000 | SHRINKS | 0,13 / 0,29 |
| AVICI, H(500) − H(200), hai phía | \|d\| = 0,05 | 0,79 / 0,99 |
| | \|d\| = 0,03 | 0,27 / 0,60 |
| SEA, xu hướng của Δ trên 500–20.000 | SHRINKS | 1,00 |
| | STABLE | 0,00 / 0,00; chỉ đạt 0,77 khi ρ = 0,8, và 0,96 khi thêm N = 120 |
| Hiện tượng còn ở một mức n | nếu hiệu ứng bằng giá trị ở n = 500 | AVICI 0,96; CDFM, FoundCause và Δ của SEA 1,00 |

Hai hệ quả:

- **Không dùng nhãn xu hướng cho AVICI.** Hiệu ứng của AVICI (0,068) chỉ lớn hơn margin 0,05 một chút trên một khoảng 3,3 lần gấp đôi. Vì vậy AVICI dùng hai giả thuyết khác (mục 5).
- **FoundCause cần N = 80.** Với N = 40, nhãn STABLE không thể đạt được ở ρ = 0.

**ρ chưa biết.** Có vài proxy, đều đo ở cùng n = 500 nhưng giữa các điều kiện khác nhau:

| Model | Hai điều kiện so sánh | Tương quan |
|---|---|---|
| CDFM | A10 và A20 | 0,55 |
| CDFM | A20 và A30 | 0,62 |
| CDFM | A20 và B20 | 0,29 |
| AVICI | A20 và B20 | 0,39 |
| FoundCause | A20 và B20 | 0,02 |
| SEA (Δ) | A20 và S20 | 0,92 |

Kế hoạch dùng ρ = 0 cho an toàn, và đo ρ trên hệ DEV (mục 9).

## 5. Lưới đề xuất

**Các mức n và vai trò của từng mức:**

| Model | Các mức n | Trong chế độ huấn luyện | Giả thuyết confirmatory | Mô tả |
|---|---|---|---|---|
| AVICI | 100, 200, 500, 1000 | 200 | **A1:** hiện tượng còn ở n = 200. **A2:** H(500) − H(200), kiểm hai phía | 100 và 1000, dùng để xem hình dạng quanh n huấn luyện |
| CDFM | 100, 200, 500, 1000, 2000, 4000 | tất cả | **C1:** hiện tượng còn ở n = 4000. **C2:** xu hướng trên 100–4000 | các mức còn lại trên figure |
| FoundCause | 125, 200, 500 | tất cả | **F1:** xu hướng trên 125–500 | n = 500 lặp lại Study 1 |
| SEA | 500, 1000, 2000, 5000, 20.000 | 20.000 | **S1:** Δ còn ở n = 20.000. **S2:** xu hướng của Δ trên 500–20.000 | H của SEA ở mọi mức n |
| PC, GES | 100, 125, 200, 500, 1000, 2000, 4000 | — | — | mốc tham chiếu. PC chạy thêm ở 5000 và 20.000; GES ở 5000 và 20.000 chỉ chạy nếu DEV cho thấy thời gian chấp nhận được |

**Cách đọc hình dạng của AVICI quanh n huấn luyện:**

- **Chữ U**, tức H thấp nhất ở n = 200: ủng hộ giải thích "n lệch khỏi lúc huấn luyện".
- **Giảm đơn điệu theo n:** ủng hộ giải thích do mẫu hữu hạn.
- **Phẳng:** hiện tượng mang tính hệ thống.

**Họ giả thuyết.** Có 7 giả thuyết confirmatory, cộng một chỗ trống, và dùng Holm 0,05.

**Margin cho nhãn xu hướng.** Tổng thay đổi trên toàn khoảng n của model bằng margin thực hành đã dùng ở các study trước: 0,05 F1, hoặc 1 cặp cho Δ. Chia cho số lần gấp đôi trong khoảng, ta được:

- CDFM: 0,0094 mỗi lần gấp đôi;
- FoundCause: 0,025 mỗi lần gấp đôi;
- SEA: 0,19 cặp mỗi lần gấp đôi.

**Dữ liệu:**

- 80 hệ held-out mới, 10 hệ mỗi ô, theo 8 ô như Study 1.
- Cùng một bộ hệ dùng cho mọi model.
- Mỗi hệ được sinh một lần với 20.000 dòng; mỗi mức n nhỏ hơn lấy n dòng đầu.
- Padding Gaussian, k = 20, được sinh và cắt theo cùng cách.
- Ở mỗi mức n, khối đích giống hệt từng bit giữa input k = 0 và k = 20.

## 6. Chi phí máy (ước lượng)

Thời gian mỗi lần gọi ở n = 500 lấy từ log. Ví dụ:

- AVICI: 2,0–8,0 giây;
- CDFM: 2,5–9,1 giây;
- FoundCause: 157–436 giây;
- SEA: trung vị 17,6 giây.

Hệ số co giãn theo n là giả định và sẽ được đo ở DEV:

- AVICI: một nửa tuyến tính, một nửa bậc hai theo n;
- CDFM và GES: tuyến tính theo n;
- FoundCause: lấy cận trên là thời gian ở n = 500;
- SEA: không đổi theo n, vì FCI luôn chạy trên batch 500 dòng.

| Model | Các mức n | Phút mỗi hệ | Giờ cho N = 80 |
|---|---|---|---|
| AVICI | 100, 200, 500, 1000 | 0,7 | 1,0 |
| CDFM | 100–4000 (6 mức) | 3,0 | 4,0 |
| FoundCause | 125, 200, 500 | ≤ 29,6 | ≤ 39,4 |
| GES | 100–4000 (7 mức) | 1,2 | 1,6 |
| SEA | 500–20.000 (5 mức), 7 lần gọi mỗi mức (k = 0 ở 5 seed, padding Gaussian và structured ở seed a) | 10,8 | 14,4 (12,3 nếu chỉ dùng Gaussian) |
| PC | mọi mức | không đáng kể | — |

Tổng khoảng 60 giờ chạy tuần tự, cộng thêm DEV gate. Các model không bao giờ chạy song song.

## 7. Sơ đồ

Ảnh `artifacts/n9_runs/design/pn9_n_grid.png` đặt các mức n của từng model trên trục log, cạnh dải chế độ huấn luyện của chính model đó.

- Điểm đặc: n nằm trong chế độ huấn luyện. Điểm rỗng: n nằm ngoài.
- Vòng đen: mức n có kiểm định confirmatory tại một n, gồm AVICI ở 200 và 500, CDFM ở 4000, SEA ở 20.000.
- Đường gạch: n = 500 của Studies 1–7.

## 8. Điểm cần quyết

1. **Số hệ.** Dùng N = 80 cho cả bốn model? FoundCause chiếm khoảng hai phần ba thời gian máy. Hay dùng N = 120 cho FoundCause, để STABLE đạt power 0,91 ở ρ = 0 (thêm khoảng 20 giờ)?
2. **Giả thuyết thứ 8.** Ba lựa chọn:
   - H của SEA ở n = 20.000 (theo dấu);
   - hiện tượng còn ở n = 125 với FoundCause;
   - bỏ, giữ họ 7 giả thuyết.
3. **Structured padding.** Chỉ dùng Gaussian (đề xuất), hay thêm structured cho SEA như Study 7 (đã tính trong ước lượng 14,4 giờ)?
4. **AVICI ở 100 và 1000.** Có giữ hai mức mô tả này không? Chi phí khoảng 1 giờ.
5. **Quy tắc tăng N theo ρ đo ở DEV.** Ví dụ: nếu ρ ước lượng nhỏ hơn 0,3, tăng N lên 120 cho các model có giả thuyết xu hướng. Quy tắc này phải khóa trước khi chạy DEV.

## 9. Những gì sẽ đo ở DEV gate

- **Thời gian và RAM:**
  - AVICI ở n = 1000;
  - CDFM ở n = 4000;
  - FoundCause ở n = 125 và 200;
  - GES ở n = 4000 (và 20.000 nếu dùng);
  - SEA ở n = 20.000.
- **ρ giữa các mức n,** chỉ dùng để đặt N theo quy tắc đã khóa.
- **Tính lồng nhau của dữ liệu:**
  - n dòng đầu giống hệt nhau giữa các mức n;
  - khối đích giống hệt từng bit giữa input k = 0 và k = 20.
