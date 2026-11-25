# P-N9: hiện tượng theo cỡ mẫu n (luật v1, ĐÃ KHÓA; 25/11/2026)

> **Trạng thái:** v1 **ĐÃ KHÓA**.
>
> - User duyệt v0 ngày 25/11 và chấp nhận mặc định của cả sáu điểm mở ở §11. v1 = v0 cộng đúng các quyết định đó (§10).
> - Khóa bằng commit và push trước khi sinh bất kỳ input nào của P-N9, kể cả của tập phát triển.
> - Lúc khóa, chưa sinh input nào và chưa chạy model nào cho P-N9.
>
> **Cơ sở:**
>
> - phân tích thiết kế `PN9_n_grid_design_vi.md` (§1–§10);
> - quyết định của user ngày 24–25/11:
>   - thí nghiệm theo n cho cả bốn model, ở các mức n nằm trong hoặc khớp với chế độ huấn luyện của từng model;
>   - N = 120 hệ cho mọi model;
>   - STABLE định nghĩa theo từng mức n;
>   - giữ luật "hiện tượng còn" của Study 1;
>   - cổng DEV chỉ kiểm tính khả thi, với phương án dự phòng khóa trước.
>
> **Vai trò:**
>
> - trong bài, đây là Study 8, với bảng và hình riêng;
> - luật và nhãn của các study trước giữ nguyên;
> - câu hỏi: hiện tượng của bài có còn khi n khớp với chế độ huấn luyện của từng model không, và trong khoảng huấn luyện nó có giảm khi n tăng không?
>
> **Cam kết báo cáo:** nếu kiểm hoàn tất đạt, cả 11 thành phần ở §4 được báo cáo trong bài, kèm nhãn, bất kể chiều và độ lớn. Hình ở §4.4 được vẽ bằng code đọc đã đóng băng. Quyết định này không phụ thuộc kết quả.
>
> **Điểm mở:** đã quyết hết trước khi khóa, xem §11.

## 0. Câu hỏi và điều không thể kết luận

**Hai câu hỏi:**

- **(A) Model chạy ở n lệch khỏi chế độ huấn luyện.**
  - AVICI được huấn luyện trên các ví dụ 200 dòng, trong khi Studies 1–7 chạy ở n = 500.
  - SEA được huấn luyện trên dữ liệu 1000N dòng. Ở n = 500, mọi lô của SEA dùng đúng cùng 500 dòng.
  - Câu hỏi: hiện tượng có còn khi n khớp với chế độ huấn luyện không?
- **(B) Model mà n = 500 nằm trong khoảng huấn luyện**, tức CDFM và FoundCause. Câu hỏi: trong khoảng huấn luyện, hiện tượng có giảm khi n tăng không, hay nằm trong biên quanh mức ở n = 500?

**Chế độ huấn luyện** (sự kiện, kiểm ngày 24–25/11):

| Model | Chế độ huấn luyện | Nguồn |
|---|---|---|
| AVICI `scm-v0` | Mỗi ví dụ huấn luyện có 200 dòng: 150 quan sát + 50 can thiệp, hoặc 200 dòng quan sát với xác suất 0,5 | `kwargs.json` của checkpoint, `config/train/scm-v0.yaml`, `avici/data.py`, `avici/utils/data_jax.py` |
| CDFM | "The number of observed variables and sample size are drawn uniformly from [2,100] and [50,4096], respectively." | bài CDFM, §5.4 (arXiv 2607.11508, HTML) |
| FoundCause | "During training, we sample problems with D∈[2,50] variables and N∈[100,599] observations." Mỗi lượt chạy dùng ceil(0,9 · min(n, 5000)) dòng, nên n ∈ [112, 665] cho 100–599 dòng mỗi lượt | bài FoundCause, §2 (arXiv 2606.17516v2); README và code |
| SEA | **Dữ liệu huấn luyện:** "each with 1000N points", với N = 10, 20, 100 biến. **Lô:** "batches of size b=500", lấy "b≪M observations uniformly at random" | bài SEA, §4.1, §3.3, §3.1 (arXiv 2402.01929v3) |
| SEA (code) | `np.random.choice(n, 500, replace=False)`. Với n < 500 code báo lỗi; với n = 500, mọi lô có đúng cùng 500 dòng | `src/data/samplers.py` ở commit đã ghim của Study 7 |

**Không kết luận được:**

- **Nguyên nhân của thay đổi theo n.** Kết quả chỉ ràng buộc được các giải thích:
  - nếu hiện tượng còn ở n khớp huấn luyện, giải thích "n lệch" bị loại cho model đó, ở chế độ đã thử;
  - nếu hiện tượng giảm theo n, kết quả phù hợp với giải thích do mẫu hữu hạn nhưng không chứng minh giải thích ấy.
- **Cơ chế bên trong model.**
- **Mức n nằm ngoài chế độ huấn luyện.** Các mức này chỉ để mô tả (§2.3).
- **So sánh giữa các model.** Bài không xếp hạng model. Hơn nữa, cùng một n mang nghĩa khác nhau với từng model.
- **STABLE không có nghĩa là "không phụ thuộc n" hay "ổn định ở mọi n".** STABLE chỉ nói mọi mức đã thử nằm trong biên quanh mức ở n = 500 (§4).
- **Với SEA, Δ chỉ đọc được một chiều,** như Study 7 §0: phân phối output không đổi thì E[Δ] = 0, nhưng chiều ngược lại không đúng. Điều này áp dụng ở mọi n.
- **Khái quát** sang checkpoint khác, model khác, đệm có cấu trúc (không thử, §11 O2), hay dữ liệu thật.

## 1. Model và cách chạy

**Model, giữ nguyên như các study trước:**

| Model | Checkpoint, cấu hình, môi trường | Cách đọc skeleton |
|---|---|---|
| AVICI, CDFM, FoundCause | như Study 1 | NATIVE là cách đọc chính. AVICI: ngưỡng 0,5. CDFM: ngưỡng thích nghi NATIVE. FoundCause: 0,5 trên max(P_ij, P_ji), mức đồng thuận tối thiểu 0,5, lịch ensemble mặc định của gói (base 42), 10 lượt, temperature 1,0 |
| SEA | như Study 7 §1: commit `bfb507b0…`, checkpoint FCI, `config/aggregator_tf_fci.yaml`. Mỗi input chạy trong một tiến trình mới, với seed ghi trước | NATIVE |
| PC, GES | PC: Fisher-z, α = 0,05, bản stable. GES: BIC Gauss. Cả hai từ causal-learn, như Study 1. Chỉ chạy và chỉ đọc trên hệ tuyến tính | — |

**Đọc phụ (chỉ mô tả, không vào Holm):**

- FIXED và FROZEN của CDFM, như Study 1. FROZEN dùng ngưỡng mà CDFM chọn ở k0 cùng mức n;
- cách đọc 1 − P(không cạnh) > 0,5 của SEA, như Study 7.

**Code:**

- chỉ viết file mới;
- code đã đóng băng của Studies 1, 2 và 7 được gọi lại từ bản đóng băng và không bị sửa.

**Chạy:**

- tuần tự, mỗi lúc một model, không bao giờ song song;
- các lượt dài (FoundCause, SEA) do user chạy trong PowerShell của mình, không chạy trong phiên agent;
- runner chạy tiếp được sau khi bị gián đoạn: bỏ qua job đã có output hợp lệ với mã băm đúng;
- bật chống ngủ máy và tắt QuickEdit;
- cổng đóng băng chạy ở đầu và cuối mỗi lượt.

## 2. Dữ liệu và seed

### 2.1 Hệ

- **Ô:** 8 ô như Study 2 và Study 7: d_T ∈ {10, 20}, e_T ∈ {1, 2}, tuyến tính và RFF, đồ thị ER. Thứ tự ô như Study 2; các ô tuyến tính là 0, 2, 4, 6.
- **Số hệ:** 15 hệ mỗi ô, tổng **120 hệ** (r = 0, …, 14), trong đó có 60 hệ tuyến tính. Chỉ số hệ i = 15·c + r.
- **Seed của hệ:** s_i = 730000 + 1000·c + r. Base 730000 chưa dùng ở pha nào.
- **Khối đích:**
  - sinh bằng bộ sinh đã đóng băng của Study 1 (simulator AVICI, cấu hình ô như Study 1);
  - chỉ dữ liệu quan sát, sinh một lần cho mỗi hệ với **20 000 dòng**;
  - mọi tham số khác giữ nguyên.
- **Đệm:**
  - 20 cột Gauss độc lập, sinh một lần cho mỗi hệ với 20 000 dòng: rng = `np.random.default_rng(np.random.SeedSequence([s_i, 20261125, 9]))`, P = `rng.standard_normal((20000, 20))`;
  - đây là đệm Gauss (A20) của Study 1, viết trực tiếp, để không phụ thuộc chi tiết bên trong bộ sinh cũ.

### 2.2 Input ở mỗi mức n

- **Dữ liệu:** input ở mức n dùng **n dòng đầu** của khối đích và của đệm.
- **Chuẩn hóa:** mỗi cột được chuẩn hóa z trên đúng n dòng đó, như Study 1.
- **Hai loại input:**
  - **k0:** chỉ khối đích;
  - **A20:** [khối đích | đệm].
- **Tính chất được kiểm ở G1:** ở mỗi mức n, khối đích giống hệt từng bit giữa k0 và A20; các mức n lồng nhau.

### 2.3 Các mức n

| Model | Các mức n | Trong chế độ huấn luyện | Ngoài chế độ huấn luyện (chỉ mô tả) |
|---|---|---|---|
| AVICI | 100, 200, 500, 1000 | 200 | 100, 500, 1000 |
| CDFM | 100, 200, 500, 1000, 2000, 4000 | tất cả | — |
| FoundCause | 125, 200, 500 | tất cả | — |
| SEA | 500, 1000, 2000, 5000, 20 000 | 20 000 (cỡ dữ liệu huấn luyện là 10 000–100 000 dòng) | 500, 1000, 2000, 5000 |
| PC | 100, 125, 200, 500, 1000, 2000, 4000, 5000, 20 000 | — | — |
| GES | 100, 125, 200, 500, 1000, 2000, 4000 | — | — |

Ngoại lệ: các mức của AVICI và SEA nằm ngoài chế độ huấn luyện vẫn được dùng trong các thành phần A2 (n = 500 của AVICI) và S2 (§4).

### 2.4 Seed của SEA

Gọi ℓ = 0, …, 4 là chỉ số của mức n trong lưới của SEA.

- **Lượt chính của hệ i ở mức ℓ:** a_{i,ℓ} = 740000 + 10·i + ℓ, dùng chung cho k0 và A20.
- **Lượt tham chiếu ở k0:** b_{i,ℓ,m} = 750000 + 100·i + 10·ℓ + m, với m = 1, …, 4 (M = 4), như Study 7.

### 2.5 Tập phát triển

- **Hệ:** s = 720000 + 1000·c + r, với r = 0, 1, tức 16 hệ. Chỉ số i = 15·c + r như §2.1.
- **Seed của SEA:** cùng công thức như §2.4, cộng thêm 1 000 000.

### 2.6 Đơn vị độc lập

- Đơn vị độc lập là 120 hệ.
- Các mức n trong cùng một hệ được ghép cặp.
- Bốn seed tham chiếu của SEA được lấy trung bình trong mỗi đơn vị. Chúng không làm tăng cỡ mẫu.

## 3. Biến đo

- **Hại:** H_i(n) = F1(k0) − F1(A20), với F1 skeleton trên các cặp của khối đích so với đồ thị thật, cách đọc NATIVE. Đo cho AVICI, CDFM, FoundCause, PC, GES, và SEA ở seed a_{i,ℓ}. Hàm F1 là hàm đã đóng băng của Study 1.
- **Δ của SEA ở mức n:** Δ_i(n) = (1/4) Σ_m [flips(k0@b_{i,ℓ,m}, A20@a_{i,ℓ}) − flips(k0@b_{i,ℓ,m}, k0@a_{i,ℓ})], như Study 7 §3.
- **Tương phản với mức neo n = 500:**
  - D_i(n) = H_i(n) − H_i(500);
  - với SEA: D^Δ_i(n) = Δ_i(n) − Δ_i(500).
- **Độ dốc theo hệ:** β_i là hệ số góc OLS của H_i(n) theo log₂ n, trên mọi mức trong lưới của model; với SEA dùng Δ_i(n). Lưới của CDFM là 100–4000, của FoundCause là 125–500, của SEA là 500–20 000.
- **Mô tả** (không vào Holm):
  - flips;
  - F1(k0) và F1(A20) ở từng mức;
  - H − max(H_PC, H_GES) trên hệ tuyến tính;
  - H của SEA;
  - Δp;
  - các giá trị theo ô;
  - tương quan của H_i(n) giữa các mức (ρ̂). ρ̂ được báo sau khi đọc và không dùng cho quyết định nào.

## 4. Giả thuyết (một họ Holm riêng, 11 thành phần)

### 4.1 Biên

| Biên | Giá trị |
|---|---|
| m cho H | 0,05 |
| m cho Δ | 1 cặp |
| c cho độ dốc, CDFM | 0,05 / log₂(4000/100) = 0,0094 mỗi lần gấp đôi n |
| c cho độ dốc, FoundCause | 0,05 / log₂(500/125) = 0,025 mỗi lần gấp đôi n |
| c cho độ dốc, SEA | 1 / log₂(20000/500) = 0,188 cặp mỗi lần gấp đôi n |

Hai biên m là biên thực hành đã dùng ở Study 1 và Study 7. c bằng m chia cho số lần gấp đôi n trong khoảng của model, nên một độ dốc vượt −c nghĩa là tổng thay đổi trên cả khoảng lớn hơn m.

### 4.2 Các thành phần

| ID | Model | Đại lượng | H0 | Phép kiểm | Bác H0 thì |
|---|---|---|---|---|---|
| A1 | AVICI | H(200) | θ ≤ 0 | t phân tầng một phía | xét nhãn PERSISTS (§4.3) |
| A2d | AVICI | D(500) = H(500) − H(200) | D = 0 | t phân tầng hai phía | HIGHER nếu D̂ > 0, LOWER nếu D̂ < 0 |
| A2s | AVICI | như trên | \|D\| ≥ 0,05 | TOST: p là giá trị lớn hơn của hai p một phía | SIMILAR |
| C1 | CDFM | H(4000) | θ ≤ 0 | t phân tầng một phía | xét nhãn PERSISTS |
| C2s | CDFM | độ dốc β | β ≥ −c | t phân tầng một phía | SHRINKS |
| C2t | CDFM | D(n), n ∈ {100, 200, 1000, 2000, 4000} | có ít nhất một n với \|D(n)\| ≥ 0,05 | intersection–union các TOST: p là giá trị lớn nhất qua các mức và hai phía | STABLE |
| F1s | FoundCause | độ dốc β | β ≥ −c | t phân tầng một phía | SHRINKS |
| F1t | FoundCause | D(125), D(200) | có ít nhất một n với \|D(n)\| ≥ 0,05 | intersection–union các TOST | STABLE |
| S1 | SEA | Δ(20 000) | θ ≤ 0 | t phân tầng một phía | xét nhãn PERSISTS, biên 1 cặp |
| S2s | SEA | độ dốc β của Δ | β ≥ −c | t phân tầng một phía | SHRINKS |
| S2t | SEA | D^Δ(n), n ∈ {1000, 2000, 5000, 20 000} | có ít nhất một n với \|D^Δ(n)\| ≥ 1 cặp | intersection–union các TOST | STABLE |

**Phép kiểm:**

- t phân tầng như Study 2: 8 ô, trọng số bằng nhau (w_c = 1/8), SE² = Σ w_c² s_c² / n_c, df Welch–Satterthwaite. Mọi đại lượng (H, D, β, Δ) được tính theo từng hệ trước, rồi mới đưa vào phép kiểm.
- Holm ở mức familywise 0,05 trên đúng 11 p-value. Family này tách riêng khỏi các study khác.
- SE = 0 thì gán DEGENERATE, p = 1, không bác H0.

### 4.3 Nhãn

**A1, C1, S1:** cùng cấu trúc với luật "hiện tượng còn" của Study 1. Khác Study 1 ở một điểm: phần kiểm dấu dùng t phân tầng với Holm thay cho CI bootstrap 95%, vì P-N9 có một họ nhiều thành phần.

- **PERSISTS:** bác H0 ở ngưỡng Holm, và ước lượng ≥ m (0,05 cho H; 1 cặp cho Δ).
- **PRESENT_BELOW_MARGIN:** bác H0, nhưng ước lượng < m.
- **NOT_CONFIRMED:** không bác H0.

**A2 (AVICI):**

- A2d bác H0 → HIGHER hoặc LOWER, theo dấu của D̂.
- A2s bác H0 → SIMILAR.
- Bác cả hai → báo cả hai: hiệu nằm trong ±0,05, và có dấu.
- Không bác cái nào → UNCLEAR.

**C2, F1, S2 (xu hướng):**

- C2s, F1s hoặc S2s bác H0 → SHRINKS.
- C2t, F1t hoặc S2t bác H0 → STABLE.
- Bác cả hai, tức mọi mức nằm trong ±m quanh n = 500 nhưng tổng thay đổi trên cả khoảng vượt m → báo cả hai, không gộp thành một nhãn.
- Không bác cái nào → UNCLEAR. Một đường không đơn điệu, chẳng hạn chữ U, thường rơi vào trường hợp này; hình ở §4.4 cho thấy hình dạng.

**Size**, như Study 7 nhưng chỉ để mô tả, với CI 95% không điều chỉnh:

- áp cho ước lượng của A1, C1, S1 và cho D̂ của A2;
- SMALL khi CI nằm trong (−m, m); LARGE khi CI nằm trọn ngoài ±m; UNCLEAR trong các trường hợp còn lại.

**Vì sao không có GROWS:** không có dự đoán trước nào rằng hiện tượng tăng theo n trong khoảng huấn luyện. Nếu điều đó xảy ra, nó được báo như mô tả, qua CI của độ dốc. Bỏ GROWS giúp họ giả thuyết nhỏ hơn.

**Cách đọc:**

- STABLE nghĩa là mọi mức đã thử nằm trong biên quanh n = 500. STABLE không có nghĩa là "không phụ thuộc n".
- NOT_CONFIRMED và UNCLEAR không chứng minh rằng không có hiệu ứng.
- Mức n ngoài chế độ huấn luyện chỉ có nghĩa mô tả. Riêng A2 và S2 dùng chúng như một phần của phép so đã khóa.

### 4.4 Hình (khóa trước)

**Hình chính:**

- bốn panel: AVICI, CDFM, FoundCause, SEA;
- trục x: n theo thang log; trục y: H, dùng chung cho cả bốn panel;
- mỗi mức n là một điểm, kèm CI 95% của t phân tầng (mô tả, không điều chỉnh);
- điểm đặc khi n nằm trong chế độ huấn luyện, điểm rỗng khi nằm ngoài; dải nền đánh dấu chế độ huấn luyện;
- đường gạch tại n = 500.

**Hình phụ:**

- H trên hệ tuyến tính, cạnh PC và GES;
- flips;
- Δ của SEA theo n, trên một trục riêng (không dùng hai trục y).

Code vẽ hình là một phần của code đọc đã đóng băng.

## 5. Cỡ mẫu và power (phân tích kịch bản, không phải chứng minh)

**Giả định:** N = 120 (quyết định của user). Ngưỡng Holm xấu nhất là α = 0,05/11 cho mọi thành phần. SD trong ô lấy từ output đã lưu ở n = 500: Study 1 held-out cho AVICI, CDFM, FoundCause; Study 7 cho SEA. ρ là tương quan giữa các mức n, giả định đều (compound symmetry).

Script: [design/pn9_power_v0.py](design/pn9_power_v0.py). Output: [design/pn9_power_v0_output.txt](design/pn9_power_v0_output.txt).

Power theo kịch bản, trình bày theo ρ = 0 / ρ = 0,5:

| Thành phần | Kịch bản | Power |
|---|---|---|
| A1, C1, S1 | hiệu ứng thật bằng giá trị ở n = 500 | 0,99; 1,00; 1,00 |
| A2d | \|D\| = 0,05 | 0,93 / 1,00 |
| A2d | \|D\| = 0,03 | 0,40 / 0,80 |
| A2s | D = 0 | 0,91 / 1,00 |
| C2t STABLE | đường phẳng | 0,93 / 1,00 |
| C2s SHRINKS | hiệu ứng ở n = 500 giảm tuyến tính theo log₂ n về 0 trên khoảng | 0,94 / 1,00 |
| F1t STABLE | đường phẳng | 0,76 / 1,00 |
| F1s SHRINKS | như C2s | 0,84 / 0,99 |
| S2t STABLE | đường phẳng | 0,00 / 0,00; 0,61 nếu ρ = 0,8 |
| S2s SHRINKS | như C2s | 1,00 / 1,00 |

- Trong các kịch bản đã thử, không có trường hợp gán nhầm nhãn: khi đường phẳng, SHRINKS ra 0,00; khi đường giảm, STABLE ra 0,00.
- **S2t gần như không đạt được** trừ khi ρ cao. Nếu Δ của SEA thật sự không đổi theo n, nhãn xu hướng của SEA nhiều khả năng là UNCLEAR. Thành phần có thông tin của SEA là S1. Điều này được chấp nhận trước.
- ρ̂ đo được không được dùng để đổi N, biên hay giả thuyết.

## 6. Cổng trên tập phát triển (chỉ kiểm khả thi; tiêu chí ghi trước khi chạy)

Cổng chạy trên 16 hệ của §2.5. Cổng **không đọc** H, Δ, F1, flips hay bất kỳ đại lượng nào của §3 trên dữ liệu DEV.

- **G1, dữ liệu:**
  - các mức lồng nhau: n dòng đầu, trước chuẩn hóa, giống hệt từng bit giữa các mức;
  - ở mỗi mức n, khối đích giống hệt từng bit giữa k0 và A20 sau chuẩn hóa;
  - mã băm input khớp input sinh lại.

  Không đạt → dừng, sửa lỗi, chạy lại cổng.
- **G2, tính xác định:** với mỗi model, chạy lại một input trong tiến trình mới phải cho output trùng từng bit. Với SEA, chạy lại với cùng seed. Không đạt → dừng.
- **G3, bộ nhớ:** đo peak working set ở mức n lớn nhất trên input D = 40. Ngưỡng: 6,0 GB (máy có 7,8 GB RAM). Các mức đo:
  - AVICI ở n = 1000;
  - CDFM ở n = 4000;
  - SEA ở n = 20 000;
  - FoundCause ở n = 500;
  - GES ở n = 4000.

  Không đạt → áp phương án dự phòng ở §6.1.
- **G4, thời gian:** ước tính các lượt chính từ thời gian đo ở cổng. Nếu tổng vượt 1,5 lần ước tính ở §8 → báo user trước khi chạy.
- **G5, adapter:**
  - với SEA, như G1 của Study 7: nhãn `true` khớp đồ thị, và output không phụ thuộc file đồ thị;
  - với các model khác, như các kiểm adapter của Study 1.
- **G6, code đọc:** chạy trên output DEV ở chế độ chỉ kiểm cấu trúc, không in giá trị, như Study 7.

### 6.1 Phương án dự phòng (khóa trước)

Mọi thay đổi do phương án dự phòng được ghi vào nhật ký trước các lượt chính. Phương án dự phòng chỉ được bỏ mức n hoặc dời mức trên cùng theo đúng các quy tắc dưới đây; không được thêm hay sửa thành phần nào khác.

| Điều kiện | Xử lý |
|---|---|
| AVICI không đạt G3 ở n = 1000 | Bỏ mức 1000. Mức này chỉ để mô tả, nên không thành phần nào bị ảnh hưởng |
| CDFM không đạt G3 ở n = 4000 | Mức trên cùng thành 2000. C1 kiểm ở n = 2000; C2 tính trên {100, …, 2000}; c = 0,05 / log₂ 20 = 0,0116 |
| SEA không đạt G3 ở n = 20 000 | Dùng 10 000, vẫn nằm trong khoảng cỡ dữ liệu huấn luyện. S1 kiểm ở n = 10 000; S2 tính trên {500, 1000, 2000, 5000, 10 000}; c = 1 / log₂ 20 = 0,231 |
| GES không đạt G3 ở n = 4000, hoặc mất hơn 60 s mỗi lần gọi | Bỏ các mức GES trên 2000. GES chỉ để mô tả |
| G4 vượt mốc | Báo user. User quyết định trước các lượt chính, và quyết định được ghi vào nhật ký |

## 7. Kiểm hoàn tất trước khi đọc

**Số output phải có:**

| Model | Số output |
|---|---|
| AVICI | 120 × 4 × 2 = 960 |
| CDFM | 120 × 6 × 2 = 1440 |
| FoundCause | 120 × 3 × 2 = 720 |
| SEA | 120 × 5 × 6 = 3600 |
| PC | 60 × 9 × 2 = 1080 |
| GES | 60 × 7 × 2 = 840 |

Các con số này được điều chỉnh tương ứng nếu áp §6.1.

**Các kiểm:**

- Mỗi job có đúng một trạng thái kết thúc, không có `error` hay `budget_stop`. Seed và mức n ghi trong output khớp kế hoạch.
- Mã băm input khớp input sinh lại. Khối đích giống hệt từng bit giữa k0 và A20 ở mỗi mức.
- **Chạy lại từng bit:** cuối mỗi lượt, chạy lại k0 ở mức nhỏ nhất của hệ đầu tiên trong mỗi ô. Output phải trùng từng bit.
- **SEA:** kiểm adapter trên mọi output, như Study 7.
- **Mã băm:** code, checkpoint và phụ thuộc khớp bản đóng băng, kiểm ở đầu và cuối mỗi lượt.

## 8. Ngân sách và điều kiện dừng

**Thời gian mỗi lần gọi ở n = 500**, đo trên máy chạy (i3-1005G1, 2 nhân, RAM 7,8 GB, chỉ CPU):

| Model | Thời gian | Nguồn |
|---|---|---|
| AVICI | 2,0–8,0 s | log held-out của Study 1 |
| CDFM | 2,5–9,1 s | log held-out của Study 1 |
| FoundCause | 157–436 s | log held-out của Study 1 |
| GES | 0,2–5,7 s | log held-out của Study 1 |
| PC | ≤ 0,6 s | log held-out của Study 1 |
| SEA, mỗi tiến trình | 21–27 s ở D = 10–20; khoảng 43 s ở D = 30; 65 s ở D = 40 | cổng DEV của Study 7, `checks/gates8.json` |

**Giả định về tăng theo n**, sẽ đo lại ở G4:

- AVICI: một nửa tuyến tính, một nửa bậc hai;
- CDFM và GES: tuyến tính;
- FoundCause: lấy cận trên là thời gian ở n = 500;
- SEA: không đổi, vì FCI chạy trên lô 500 dòng;
- PC: không đáng kể.

**Ước tính với N = 120:**

| Model | Ước tính |
|---|---|
| AVICI | 1,4 h |
| CDFM | 6,0 h |
| FoundCause | ≤ 59 h |
| SEA (6 tiến trình mỗi hệ mỗi mức) | 29 h |
| GES | 1,2 h |
| PC | < 0,5 h |
| **Tổng** | **khoảng 97 h, chạy tuần tự** |
| Cổng DEV | thêm khoảng 4–5 h |

- **Sửa so với `PN9_n_grid_design_vi.md` §6:** tài liệu đó tính SEA bằng thời gian SEA tự ghi (17,6 s mỗi lần). Thời gian thật mỗi tiến trình, đo ở DEV của Study 7, là 21–65 s. Vì vậy ước tính cho SEA tăng từ 21,6 h lên 29 h.
- **Chia lượt:** mỗi model chia thành bốn lượt theo cặp ô, như Study 7. Ước tính của từng lượt được điền sau G4.
- **Mốc dừng:** 1,5 lần ước tính của mỗi lượt. Vượt mốc → dừng, báo user.
- **Dừng sớm khi:**
  - chạy lại không trùng từng bit;
  - adapter không đạt;
  - một job lỗi.

## 9. Quy trình

1. User review v0 (xong ngày 25/11).
2. **Khóa v1:** commit và push trước khi sinh bất kỳ input nào của P-N9, kể cả của tập phát triển (25/11).
3. Viết code, chỉ trong file mới. Chạy cổng G1–G6.
4. Đóng băng toàn bộ code cùng phụ thuộc, gồm cả code đọc và code vẽ hình; commit và push trước các lượt chính. Đây là bài học về thời điểm khóa ở Study 7: luật và phép kiểm khóa trước cổng, còn code đọc đóng băng cùng phần code còn lại sau cổng, trước các lượt chính.
5. Chạy các lượt chính trong ngân sách. Kiểm hoàn tất. Đọc kết quả bằng code đã đóng băng. Kiểm lại độc lập bằng một script post hoc.
6. Báo cáo theo cam kết ở đầu file.

## 10. Nhật ký (append-only sau khi khóa)

- **v0, 25/11/2026:** nháp. Viết theo `PN9_n_grid_design_vi.md` và các quyết định của user ngày 24–25/11.
- **v1, 25/11/2026, KHÓA.** User duyệt v0 và chấp nhận mặc định của cả sáu điểm ở §11. v1 = v0 cộng đúng các quyết định sau; không đổi gì khác:
  - O1: không thêm thành phần thứ 12; họ Holm giữ 11 thành phần;
  - O2: chỉ dùng đệm Gauss; không chạy đệm có cấu trúc;
  - O3: giữ hai mức mô tả 100 và 1000 của AVICI;
  - O4: không kiểm chất lượng ở k0 trên DEV; cổng chỉ kiểm tính khả thi;
  - O5: không có thành phần GROWS;
  - O6: A1, C1 và S1 dùng t phân tầng với Holm thay cho CI bootstrap 95% của Study 1.
- **Cổng DEV, 25/11/2026** (sau khóa v1, trước khi đóng băng code). Luật không đổi. Trên DEV không in hay xem giá trị nào của §3; chế độ kiểm cấu trúc của G6 tính chúng trong bộ nhớ nhưng chỉ in số đếm.
  - **Kết quả:** G1–G6 đạt, ghi ở [checks/gates9.json](checks/gates9.json). Không áp phương án dự phòng nào của §6.1.
    - G1: 288 input, hai lần dựng và một bản tính độc lập trùng nhau; 628 bản ghi có mã băm trùng khi so giữa các tiến trình; không hệ nào bị thay seed.
    - G2: cả sáu model chạy lại trùng từng bit.
    - G3, peak working set (ngưỡng 6144 MB): AVICI 2635; CDFM 1684; FoundCause 2449; SEA 1384; GES 251 MB.
    - G5: AVICI, CDFM, FoundCause, PC, GES tái lập output của Study 1 trùng từng bit; SEA đạt kiểm nhãn `true`, AUC, đồ thị rỗng và tái lập Study 7.
    - G6 đạt, nhưng trên DEV chỉ tính được 6/11 thành phần (DEV không có FoundCause ở n = 500 và không đủ mức, đủ seed của SEA). Phần còn lại được kiểm bằng selftest bên dưới.
  - **G4:** tổng ước tính 75,8 h, dưới mốc 145,5 h. AVICI 1,2; CDFM 12,8; FoundCause 42,2; SEA 19,2; GES 0,3; PC 0,1 h. Lệch so với giả định ở §8: thời gian của CDFM tăng khoảng n^1,5, không tuyến tính (12,8 h thay vì 6,0 h); SEA nhanh hơn (19,2 h thay vì 29 h). FoundCause ở n = 500 lấy thời gian đo ở cổng (192,6 s ở D = 10; 532,7 s ở D = 40); ở D = 20 và 30, vốn không đo ở cổng, lấy trung vị Study 1 nhân 1,32, là mức chậm lớn nhất đo được.
  - **Mốc dừng mỗi lượt** (1,5 × ước tính, làm tròn lên 0,1 h; R1/R2/R3/R4): AVICI 0,5/0,5/0,5/0,5; CDFM 3,9/3,9/5,8/5,8; FoundCause 13,9/13,9/17,9/17,9; SEA 6,3/6,3/8,1/8,1; PC 0,1 và GES 0,1/0,5 (chỉ R1, R3).
  - **Sửa code trước khi đóng băng:**
    1. runner: phép kiểm header của lượt chính khớp nhầm cả chế độ REPRO, làm DEV dừng một lần ở AVICI REPRO; sửa xong chạy tiếp, job đã xong được bỏ qua;
    2. runner: lưu output nguyên tử; chỉ bỏ qua job khi output đọc được và mã băm input đúng (đúng chữ của §1; trước đó chỉ xem file có tồn tại);
    3. code đọc: bổ sung Δp (§3), hình flips và panel SEA trong hình hệ tuyến tính (§4.4), vốn bị thiếu; sửa bố cục trục và chú giải;
    4. G4: dùng thời gian đo ở cổng cho FoundCause ở n = 500; bản đầu dùng trung vị Study 1 và cho tổng 70,2 h.
  - **Thêm ngoài luật, chỉ mô tả hoặc chỉ kiểm:**
    - `flips_seed` và `dp_seed` của SEA (k0 so với k0 khác seed), như Study 7; không vào Holm;
    - `selftest9.py`, ghi ở [checks/selftest9.json](checks/selftest9.json), chạy trên output tổng hợp với đồ thị ngẫu nhiên và trên input DEV, không sinh input held-out. Đạt: 6 kịch bản đọc khớp với một bản tính độc lập (11 thành phần, Holm, nhãn, 191 giá trị mô tả, ρ̂ ở mỗi kịch bản); kiểm hoàn tất đạt trên dữ liệu đủ và bắt được 14/14 lỗi cài sẵn; đường lượt chính của runner AVICI, PC, GES, SEA cho output trùng từng bit với DEV, từ chối khi thiếu hoặc hỏng header, chạy tiếp, dừng đúng mốc, từ chối output hỏng.
    - Giới hạn của selftest: bản tính độc lập do cùng người viết nên không phát hiện được lỗi hiểu sai luật; đường lượt chính của FoundCause không được chạy thử (dùng chung `run9.py` với AVICI); tổ hợp nhãn SHRINKS + STABLE không xuất hiện trong sáu kịch bản.

## 11. Điểm mở (đã quyết ngày 25/11: user chấp nhận mặc định của cả sáu điểm)

| # | Điểm mở | Mặc định, đã được duyệt |
|---|---|---|
| O1 | **Thành phần thứ 12.** Ví dụ: H của SEA ở n = 20 000 theo dấu, hoặc hiện tượng còn ở n = 125 với FoundCause | không thêm, giữ 11 |
| O2 | **Đệm có cấu trúc cho SEA, như S20 của Study 7.** Thêm một tiến trình mỗi hệ mỗi mức, ở D = d_T + 20 (43–65 s), tức khoảng 9 h; S20 chỉ để mô tả, không vào Holm | chỉ dùng đệm Gauss |
| O3 | **Hai mức mô tả 100 và 1000 của AVICI.** Chi phí dưới 1 h | giữ |
| O4 | **Kiểm chất lượng ở k0 theo n trên DEV,** như G4 của Study 7. Kiểm này chỉ ghi cờ để giới hạn diễn giải, không loại giả thuyết, nhưng nó đọc F1 ở k0 trên DEV | không thêm, vì cổng chỉ kiểm khả thi |
| O5 | **Không có thành phần GROWS** (§4.3) | xác nhận |
| O6 | **Thay CI bootstrap 95% của Study 1 bằng t phân tầng với Holm** trong A1, C1, S1 (§4.3) | xác nhận |
