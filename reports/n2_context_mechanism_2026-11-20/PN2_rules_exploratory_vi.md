# P-N2: luật đọc cho pha exploratory (v1, khóa ngày 20/11/2026)

> **Trạng thái:** **v1, ĐÃ KHÓA** bằng commit chứa dòng này, push trước khi có bất kỳ output P-N2 nào, kể cả DEV2.
>
> - Bản nháp v0 ở commit `18df91b`.
> - User duyệt v1 kèm sáu quyết định và ba chỉnh sửa (§13).
> - Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §13 kèm lý do, và không được dựa trên metric đã thấy.
>
> **Nguồn thiết kế:**
>
> - [kiểm prior art §5–§7](../n1_irrelevant_vars_2026-11-13/N1_prior_art_recheck_2026-11-20_vi.md);
> - [phân tích hậu nghiệm held-out của P-N1](../n1_irrelevant_vars_2026-11-13/PN1_HELD_posthoc_rank_level_vi.md);
> - ba review của user ngày 20/11.
>
> **Không đổi gì của P-N1:** các nhãn INCONCLUSIVE giữ nguyên; luật [v2](../n1_irrelevant_vars_2026-11-13/PN1_reading_rules_vi.md), [v2.1](../n1_irrelevant_vars_2026-11-13/PN1_rules_v2_1_amendment_vi.md) và [v2.2](../n1_irrelevant_vars_2026-11-13/PN1_rules_v2_2_amendment_vi.md) không bị sửa.

## 0. Quy trình

1. Khóa luật v1: commit và push.
2. Viết code trong `artifacts/n2_runs/pn2/` (git-ignored); không đụng `artifacts/n1_runs/`. Code đọc module đã đóng băng của P-N1 (`common.py`) chỉ để sinh hệ đích, không sửa.
3. Chạy **DEV2**:
   - kiểm các cổng ở §9;
   - chọn α cho nhánh R theo đúng §8.4;
   - ghi kết quả DEV2 và α đã chọn vào §13.
4. Viết code đọc EXP2, kiểm trên dữ liệu không thuộc EXP2. Đóng băng code (snapshot kèm SHA-256 và cổng kiểm như P-N1), commit, push.
5. Chạy **EXP2** (40 hệ). Chỉ đọc sau khi đủ 40 hệ, bằng code đọc đã đóng băng.
6. Viết luật held-out (HELD2) theo §10: cỡ mẫu tính từ phương sai của EXP2. Khóa, commit, push **trước khi** sinh dữ liệu hay chạy HELD2.

## 1. Câu hỏi và phạm vi

**Câu hỏi.** Vì sao một khối dữ liệu độc lập với khối đích lại làm model đổi cách chọn cạnh trong khối đích? Thay đổi ấy làm mất cạnh đúng hay loại cạnh sai? Nó nằm ở mức điểm (số cạnh) hay ở thứ hạng cạnh đúng/sai, và khác nhau thế nào giữa các model?

**Pha exploratory trả lời ba câu:**

- **L1:** ở cùng D, khi chỉ thay mật độ cạnh của khối đệm, output khối đích có đổi không, và theo hướng nào?
- **L2:** giữ đồ thị đệm cố định và chỉ thay cường độ phụ thuộc, output có đổi không?
- **R:** một bước sàng lọc cổ điển rẻ có làm giảm các thay đổi đó không, có sửa được lỗi không, và với chi phí gì?

**Ngoài phạm vi của pha này:** FoundCause, can thiệp attention, dữ liệu thật, claim xác nhận. Pha exploratory chỉ sinh và chọn giả thuyết cho held-out.

**Điều L1 không kiểm:** prior gắn với d (H1'), vì D giữ nguyên. Một đường liều–đáp ứng rõ chỉ xác lập độ nhạy với cấu trúc khối đệm, chưa quy nguyên nhân cho prior huấn luyện.

## 2. Hệ đích, tập seed, cỡ mẫu

- **Ô:** giữ 8 ô của P-N1, gồm d_T ∈ {10, 20} × số cạnh/nút e_T ∈ {1, 2} × cơ chế ∈ {tuyến tính, RFF}.
- **Sinh hệ đích:** như P-N1 (`target()` trong `common.py` đã đóng băng): n = 500, config ER của ô, z-score; hệ đích không có cạnh thì thay bằng seed + 500.
- **Tập và seed** (công thức seed như P-N1: base + 1000 × ô + r):

  | Tập | Base | Số hệ mỗi ô | Tổng | Dùng cho |
  |---|---|---|---|---|
  | DEV2 | 410000 | 2 | 16 | Cổng §9 và chọn α cho R. Không dùng để ước lượng hiệu ứng |
  | EXP2 | 420000 | 5 | 40 | Exploratory: 20 hệ mỗi họ cơ chế |
  | HELD2 | 430000 | kế hoạch 10 | kế hoạch 80 | Đặt chỗ seed; chưa sinh dữ liệu. Cỡ mẫu và luật chốt sau EXP2 |

  Các base này không trùng với các tập của P-N1 (100000, 150000, 200000, 300000).
- **Cỡ mẫu:** 40 hệ cho EXP2 là cố định. Theo phương sai của P-N1, nửa độ rộng CI của contrast B − A trên F1 ở top-m0 khi tách theo họ là khoảng:

  | Model và họ | 20 hệ mỗi họ (EXP2) | 40 hệ mỗi họ (HELD2 kế hoạch) |
  |---|---|---|
  | AVICI tuyến tính | ±0.048 | ±0.034 |
  | AVICI RFF | ±0.028 | ±0.020 |
  | CDFM tuyến tính | ±0.026 | ±0.018 |
  | CDFM RFF | ±0.031 | ±0.022 |

  Đây chỉ là tham chiếu, tính từ Bảng 3 của file hậu nghiệm và khớp với tính toán của user; chưa tính đa kiểm định. Thiết kế ghép cặp mới có thể làm phương sai đổi. Vì vậy EXP2 được phép cho nhiều nhãn INCONCLUSIVE hoặc UNCLEAR.

## 3. Khối đệm: bộ sinh lồng nhau

**Mục tiêu.**

- Giữ nguyên họ cơ chế của AVICI (RFF đa biến và tuyến tính, cùng phân phối tham số với config của ô).
- Ghép cặp randomness giữa các mức, để giữa hai mức chỉ đổi tập cạnh (L1) hoặc cường độ (L2).

**Luồng ngẫu nhiên.** `rng_P = default_rng(SeedSequence([seed gốc của hệ, 20261120, 2]))`.

- Seed gốc là base + 1000 × ô + r, lấy trước quy tắc thay seed của hệ đích.
- Luồng này tách khỏi luồng sinh khối đích; bộ sinh đệm không đọc dữ liệu đích.

**Rút một lần, đúng thứ tự gọi dưới đây, không phụ thuộc mức** (k = 20, n = 500). Mọi mảng được rút ngoài vòng lặp theo nút:

1. `pi = rng_P.permutation(k)`: thứ tự topo.
2. `U = rng_P.uniform(size=(k, k))`: chỉ dùng U[a, b] với a < b (vị trí trong π).
3. `noise_scale = rng_P.uniform(0.2, 2.0, size=k)`, `bias = rng_P.uniform(-3, 3, size=k)`.
4. `Z = rng_P.normal(size=(n, k))`: rút **một lần** cho cả khối, không rút theo từng nút.
5. Tham số cơ chế:
   - **Tuyến tính:** `sgn = rng_P.choice([-1, 1], size=(k, k))`, `mag = rng_P.uniform(1, 3, size=(k, k))`, W = sgn · mag. Đây là thứ tự rút của `SignedUniform` trong AVICI. W[i, j] là trọng số của cạnh i → j, như vector trọng số trên mọi nút mà `LinearAdditive` rút cho mỗi nút.
   - **RFF:**
     - `ls = rng_P.uniform(7, 10, size=k)`, `c = rng_P.uniform(10, 20, size=k)`;
     - `G = rng_P.normal(size=(k, k, 100))`, Ω_j = G[j] / ls_j, trong đó hàng i ứng với cha ứng viên i;
     - `b = rng_P.uniform(0, 2π, size=(k, 100))`, `w = rng_P.normal(size=(k, 100))`.

**Đồ thị ở mức e.** p_e = min(2e/(k − 1), 0.99). Có cạnh π[a] → π[b] khi a < b và U[a, b] < p_e.

- Vì p_e tăng theo e, tập cạnh tự lồng nhau: E(0.5) ⊆ E(1) ⊆ E(2) ⊆ E(3).
- Mỗi mức có đúng phân phối ER của AVICI với `edges_per_var = e`: mỗi cặp theo một thứ tự ngẫu nhiên có cạnh độc lập với xác suất p.

**Sinh dữ liệu** theo thứ tự π, với pa là tập cha của j (xếp tăng theo nhãn, như `onp.where` trong AVICI), tính bằng float64:

- tuyến tính: x_j = s · Σ_{i∈pa} W[i, j] x_i + bias_j + noise_scale_j · Z[:, j];
- RFF: x_j = s · f_j(x_pa) + bias_j + noise_scale_j · Z[:, j], với f_j(x_pa) = √2 · c_j · Σ_l w_jl cos(Σ_{i∈pa} Ω_j[i, l] x_i + b_jl) / √100.
  - Đây là phép cosine đa biến của `RFFAdditive._rff_mechanism`, chỉ lấy các hàng của Ω_j ứng với cha đang có cạnh.
  - Khi pa rỗng, f_j là hằng số, như trong AVICI.
- Cuối cùng z-score từng cột đệm (float64 → float32) rồi ghép như P-N1: X = zscore([X_T | P]). Khối đích phải trùng từng bit với input k0.

**Các mức:**

- **L1:** s = 1, e ∈ {0, 0.5, 1, 2, 3}.
- **L2:** e = 2, s ∈ {0, 0.25, 0.5, 1}. Tham số s chỉ nhân phần tín hiệu từ cha; nhiễu giữ nguyên và chuẩn hóa làm sau, nên tác động của s không bị chuẩn hóa xóa.

**Bí danh (khóa theo định nghĩa):**

- L2(s = 1) là **đúng input** của L1(e = 2).
- L2(s = 0) là **đúng input** của L1(e = 0).
  - Lý do: ở s = 0, mỗi cột đệm là bias + nhiễu. Ở e = 0, mỗi cột là hằng + bias + nhiễu (RFF) hoặc bias + nhiễu (tuyến tính). Z-score bỏ hằng số, nên hai input bằng nhau về toán, chỉ có thể khác ở sai số làm tròn.
  - Hai bí danh dùng chung một input float32 theo định nghĩa. Phép kiểm sai số ở G4 làm trên float64, trước khi ép kiểu.

**Tương đương với P-N1 theo cách sinh, không dựa vào kiểm định:**

- Ở e = 0, các cột đệm là nhiễu Gauss độc lập đã z-score, nên **cùng phân phối với kiểu A** của P-N1.
- Ở e = e_T (số cạnh/nút của ô), họ đồ thị và phân phối tham số trùng **kiểu B** của P-N1. Kiểu B dùng `simulate_data`; hàm này hoán vị hàng, điều không đổi phân phối khi các mẫu i.i.d. Đây là các bản rút mới.
- **Chỉ phân phối biên của từng input là trùng P-N1.** Trong P-N1, A và B rút độc lập; ở P-N2, các mức dùng chung nhiễu và tham số. Vì vậy phân phối và phương sai của hiệu theo từng cặp khác P-N1.

**Ghi lại** cho mỗi (hệ, mức):

- số cạnh đệm thực tế;
- số nút đệm cô lập;
- một chỉ số phụ thuộc của khối đệm (trung bình |Spearman ρ| trên các cặp đệm), chỉ dùng mô tả.

**Không** sửa đồ thị sau khi sinh để ép đạt kỳ vọng.

## 4. Danh sách job

Mỗi hệ có 8 input khác nhau: k0; L1 với e ∈ {0, 0.5, 1, 2, 3}; L2 với e = 2, s ∈ {0.25, 0.5}.

| Model | Input mỗi hệ | Nhánh R mỗi hệ | EXP2 (40 hệ) |
|---|---|---|---|
| AVICI `scm-v0` (2 luồng, như P-N1) | 8 | 8 input, chạy theo thành phần | 320 lần chạy thường + các lần chạy theo thành phần |
| CDFM (như P-N1, ngưỡng NATIVE tự chọn) | 8 | 8 input, chạy theo thành phần | như trên |
| PC (Fisher-z, α = 0.05, stable) và GES (BIC Gauss), như P-N1 | 4 trên hệ tuyến tính: k0, e = 0, e = e_T, e = 3 | không | 80 job mỗi thuật toán (20 hệ tuyến tính) |

- PC và GES là mốc cổ điển cho REP và L1-END; ở pha exploratory chỉ dùng để mô tả.
- Trên DEV2, mọi job trên đều chạy để kiểm pipeline và đo thời gian. Output đó không dùng để ước lượng hiệu ứng (§9).

## 5. Biến đo

Mọi biến đo tính trên khối đích, dạng skeleton, cho từng (hệ, input).

- **Số cạnh:**
  - m: số cạnh dự đoán ở NATIVE; với CDFM thêm FROZEN (ngưỡng CDFM tự chọn ở k0, lần chạy thường) và FIXED (0.5);
  - Δm = m − m(k0), |Δm| và Δm/d_T;
  - số cặp đích đổi trạng thái so với k0.
- **Thứ hạng** (không phụ thuộc ngưỡng):
  - AUROC và AP trên các cặp của khối đích, với điểm của cặp là max(p_ij, p_ji);
  - F1 ở top-m0, trong đó m0 = m(k0) của **lần chạy thường, trước R**. Mọi contrast, kể cả R-*, dùng mốc này; mốc sau R chỉ báo phụ.
  - Nếu m0 = 0, F1 ở top-m0 không mang thông tin thứ hạng. Hệ đó bị loại khỏi các contrast top-m0, số hệ bị loại được báo, và kết quả không được coi là bằng chứng thứ hạng ổn định.
- **CDFM:** chính ngưỡng NATIVE của lần chạy thường.
- **Chất lượng:** TP, FP, F1 (NATIVE; với CDFM thêm FROZEN và FIXED).
- **Phân rã kế toán theo mốc m0** (chỉ mô tả, không phải nguyên nhân): phần thứ hạng và phần số cạnh, như file hậu nghiệm P-N1.
- **Phụ:**
  - logit trung bình của cặp đúng và cặp sai;
  - số cạnh dự đoán nối đích với đệm;
  - các chỉ số ghi lại của khối đệm (§3).

## 6. Contrast, nhãn, biên

**Đơn vị phân tích:** từng model × từng họ cơ chế, 20 hệ mỗi họ. Con số gộp hai họ chỉ để tham chiếu. Con số gộp gần 0 **không** được dùng làm bằng chứng "không đổi" khi hai họ khác nhau.

**Contrast** (theo từng hệ, rồi lấy trung bình):

| Tên | Định nghĩa | Vai trò |
|---|---|---|
| REP | Y(e = e_T) − Y(e = 0) | Lặp lại **hiệu ứng trung bình** B − A của P-N1 trên seed mới (§3: chỉ phân phối biên trùng P-N1). Dùng để kiểm giả thuyết §7 |
| L1-END | Y(e = 3) − Y(e = 0) | Đầu–cuối của đường liều–đáp ứng |
| L1-PROFILE | Y(e) − Y(0) với e ∈ {0.5, 1, 2, 3}, và độ dốc OLS theo e của từng hệ | Mô tả hình dạng, để không bỏ sót đường không đơn điệu |
| L2 | Y(s) − Y(s = 0) với s ∈ {0.25, 0.5}; s = 1 trùng L1(e = 2) | Cường độ ở đồ thị đệm cố định |
| R-* | Các contrast trên tính lại trên output sau nhánh R, chỉ cho Y ở mức đồ thị (Δm, F1, top-m0, AUROC, AP) | Nhánh R có làm giảm thay đổi không (§10) |

**Y chính:**

- Δm (NATIVE; với CDFM thêm FROZEN và FIXED);
- AUROC;
- F1 ở top-m0;
- ngưỡng NATIVE của CDFM (chỉ ở lần chạy thường).

**Y phụ:** F1, TP, FP, |Δm|, số cặp đổi trạng thái, AP, Δm/d_T, logit trung bình, và kết quả tách theo d_T.

**Biên thực tiễn M:**

- Số cạnh: 1.5 cạnh, áp cho hiệu ứng **trung bình theo hệ** trong từng model và họ. Đây không có nghĩa "số cạnh không đổi ở mỗi hệ". Biên này là lựa chọn thực tiễn cho phạm vi này, không phải tiêu chuẩn thống kê phổ quát.
- AUROC, AP, F1, F1 ở top-m0: 0.03.
- Ngưỡng CDFM: 0.03, tức 3 điểm phần trăm xác suất.
  - Đây chỉ là biên cho độ đổi của ngưỡng.
  - Tác động lên đồ thị đọc riêng qua Δm, F1 và thứ hạng.

**Bootstrap:** 2000 lần, percentile, lấy mẫu lại theo hệ trong từng (model, họ), seed 20261120.

**Nhãn** cho mỗi (model, họ, contrast, Y), gồm hai phần:

- **dấu:** POS nếu cận dưới > 0; NEG nếu cận trên < 0; NONE nếu khác.
- **cỡ:**
  - SMALL nếu toàn bộ CI nằm trong [−M, M];
  - LARGE nếu toàn bộ CI nằm ngoài [−M, M] về một phía;
  - UNCLEAR nếu khác.

  Ước lượng điểm nhỏ mà CI rộng thì là UNCLEAR, không phải SMALL.

Pha exploratory không kiểm soát familywise. Mọi contrast đều được báo, không chọn lọc. Các nhãn và CI 95% ở đây chỉ để mô tả. Phép kiểm xác nhận ở HELD2 dùng p-value khóa riêng (§10).

## 7. Giả thuyết định trước

Các giả thuyết dưới đây sinh hậu nghiệm từ held-out của P-N1, nên chỉ được kiểm trên seed mới.

- **Chỉ xét theo REP.** Nhãn: **CONSISTENT** nếu dấu khớp dự đoán, **CONTRARY** nếu dấu ngược, **INCONCLUSIVE** nếu dấu là NONE. Nhãn cỡ (§6) báo kèm.
- **L1-END** báo kèm nhưng không dùng để loại giả thuyết. Nếu L1-END ngược dấu với dự đoán, ghi là **"hình dạng khác dự đoán"**. Dấu hiệu này có thể sinh giả thuyết mới cho HELD2 (§10), vì hiện tượng không đơn điệu là một phần câu hỏi nghiên cứu.

| ID | Model, họ | Y | Dấu dự đoán | Từ P-N1 (B − A, 40 hệ mỗi họ) |
|---|---|---|---|---|
| HA1 | AVICI, tuyến tính | Δm | NEG | −7.2 [−10.0, −4.7] |
| HA2 | AVICI, RFF | Δm | NEG | −2.6 [−4.1, −1.3] |
| HA3 | AVICI, tuyến tính | F1 ở top-m0 | POS | +0.052 [+0.020, +0.087] |
| HA4 | AVICI, tuyến tính | AUROC | POS | +0.028 [+0.012, +0.044] |
| HA5 | AVICI, RFF | F1 ở top-m0 | NEG | −0.036 [−0.056, −0.017] |
| HA6 | AVICI, RFF | AUROC | NEG | −0.020 [−0.032, −0.007] |
| HC1 | CDFM, RFF | ngưỡng NATIVE | POS | +0.171 [+0.151, +0.190] |
| HC2 | CDFM, RFF | Δm NATIVE | NEG | −18.9 [−25.5, −12.9] |
| HC3 | CDFM, RFF | F1 ở top-m0 | NEG | −0.042 [−0.062, −0.021] |
| HC4 | CDFM, RFF | AUROC | NEG | −0.030 [−0.044, −0.017] |
| HC5 | CDFM, tuyến tính | ngưỡng NATIVE | POS | +0.030 [+0.014, +0.047] |

- **CDFM tuyến tính chỉ có HC5:** ở P-N1, CI của Δm, F1 ở top-m0 và AUROC đều chứa 0, nên các Y này chỉ mô tả. Ngưỡng tăng có CI loại 0, nhưng cận dưới (0.014) chưa vượt biên 0.03, nên ở P-N1 cỡ của nó là UNCLEAR.
- **Quy tắc chọn giả thuyết:** một ô (model, họ, Y chính) có giả thuyết khi CI của B − A ở P-N1 loại 0. Dấu dự đoán là dấu đó.
- **Không có giả thuyết về dấu của F1 ở CDFM:** dấu của F1 phụ thuộc cách chọn ngưỡng (Bảng 5 của file hậu nghiệm).

## 8. Nhánh R: sàng lọc và tách thành phần

### 8.1 Bản chính (R-data)

Áp lên mỗi input X: D = d_T + 20, hoặc D = d_T ở k0.

1. **Kiểm phụ thuộc biên** cho mọi cặp biến, m = D(D − 1)/2 phép kiểm:
   - **Họ tuyến tính:** Fisher-z trên hệ số Pearson r: z = atanh(r) · √(n − 3), p hai phía theo phân phối chuẩn.
   - **Họ RFF:** HSIC.
     - Kernel Gauss, độ rộng theo median heuristic cho từng biến, trên dữ liệu đã z-score, như `KCI_UInd(est_width='median')` của causal-learn.
     - p-value theo **xấp xỉ gamma** của phân phối null (Gretton et al. 2008), như `KCI_UInd(approx=True)`. Bản vector hóa của mình tính đuôi bằng `scipy.stats.gamma.sf`, không dùng `1 - gamma.cdf`, để ổn định ở đuôi.
     - **α của HSIC là mức danh nghĩa.** DEV2 chỉ kiểm chẩn đoán (G9), không chứng minh FWER được kiểm soát. Nếu muốn dùng bảo đảm FWER làm luận cứ của bài, cần một nghiên cứu calibration riêng với nhiều hệ hơn.
     - **Không dùng p-value lấy mẫu:**
       - Với hoán vị, 999 lần cho p nhỏ nhất 10⁻³, không đạt ngưỡng Bonferroni 0.05/780 ≈ 6.4 × 10⁻⁵ khi D = 40.
       - `KCI_UInd(approx=False)` lấy mẫu từ phân phối null phổ (không phải hoán vị dữ liệu), `null_ss` mặc định 1000 và có thể đổi. Nó có thể trả p = 0 khi không mẫu null nào vượt thống kê quan sát; số 0 đó không được hiểu là bằng chứng ở mức 10⁻⁵.
2. **Bonferroni:** bác bỏ độc lập khi p < α / m. Mỗi phép kiểm có α riêng (α_Fz cho Fisher-z, α_HSIC cho HSIC), chọn trên DEV2 theo §8.4.
3. **Tách thành phần:** dựng đồ thị vô hướng từ các cặp bị bác bỏ, rồi lấy các thành phần liên thông.
4. **Chạy model** riêng trên từng thành phần có ít nhất 1 biến đích và ít nhất 2 biến.
   - Input là các cột gốc, đã z-score theo từng cột, nên không cần chuẩn hóa lại.
   - **CDFM:**
     - NATIVE sau R: CDFM tự chọn ngưỡng trên từng thành phần, nên có nhiều ngưỡng. Không áp lên nhánh này các contrast dành cho một ngưỡng toàn bảng; các ngưỡng thành phần chỉ báo dạng mô tả.
     - FROZEN sau R: dùng **một** ngưỡng duy nhất, là ngưỡng NATIVE ở k0 của lần chạy thường (trước R), cho mọi thành phần.
     - FIXED sau R: 0.5.
5. **Output trên khối đích:**
   - hợp các cạnh dự đoán trong từng thành phần;
   - cặp đích nằm ở hai thành phần khác nhau thì không có cạnh, và điểm của cặp là 0 khi tính AUROC, AP;
   - biến đích đứng riêng một mình thì không có cạnh nào.

### 8.2 Đối chứng và biến thể

- **R-oracle** (biết trước ranh giới đích/đệm) chạy model trên đúng khối đích, nên trùng k0 theo cấu trúc. Chỉ kiểm sanity trên DEV2 (G10), không phải kết quả.
- **R-data tại k0:** sàng lọc và chạy theo thành phần ngay trên khối đích. Phần này đo cái giá của việc tách chính khối đích, và là đầu vào bắt buộc của §10.3.
- **Biến thể chỉ đo sàng lọc** (không chạy lại model):
  - Spearman cho họ RFF (đối chứng rẻ; Spearman chủ yếu nhạy với quan hệ đơn điệu), Bonferroni ở α_HSIC.
  - HSIC cho **cả hai họ**: biến thể không cần biết họ cơ chế. Dùng đúng α_HSIC đã chọn trên các ô RFF; không chọn lại α cho họ tuyến tính.
  - BH ở mức q bằng α của phép kiểm tương ứng. BH kiểm soát tỉ lệ phát hiện sai, không trực tiếp kiểm soát xác suất nối nhầm thành phần.

### 8.3 Chỉ số sàng lọc

Cho mỗi input:

- **gộp** = số biến đệm nằm trong thành phần có ít nhất 1 biến đích;
- **tách** = số cạnh thật của khối đích có hai đầu nằm ở hai thành phần khác nhau;
- **cạnh chéo giả** = số cặp đích × đệm bị bác bỏ độc lập. Mọi cặp này thật sự độc lập, nên mỗi lần bác bỏ là một phát hiện giả;
- số thành phần chứa biến đích;
- thời gian chạy.

### 8.4 Chọn α trên DEV2

1. **Lưới:** α ∈ {0.01, 0.05, 0.10}, chọn **riêng** cho Fisher-z (4 ô tuyến tính) và HSIC (4 ô RFF). AVICI và CDFM dùng chung lựa chọn. Lựa chọn giữ nguyên cho EXP2 và HELD2.
2. **Tiêu chí:**
   - Với mỗi input có đệm của DEV2, tính j = gộp/k + tách/|E_T|, trong đó |E_T| là số cạnh thật của khối đích.
   - Lấy trung bình j theo hệ trong từng (ô, điều kiện có đệm).
   - Lấy trung bình đều theo ô và theo 7 điều kiện có đệm (e ∈ {0, 0.5, 1, 2, 3}, s ∈ {0.25, 0.5}) để được J(α).
3. **Chọn** α có J nhỏ nhất. **Hòa điểm** (J bằng nhau khi làm tròn 3 chữ số): chọn 0.05 nếu 0.05 nằm trong nhóm hòa; nếu không, chọn α nhỏ nhất trong nhóm.
4. **Dùng gì để chọn:**
   - Chỉ dùng ground truth của dữ liệu DEV2, không dùng output model.
   - Input k0 không tính vào J; lỗi tách ở k0 báo riêng. Tuy vậy, chất lượng tại k0 trước và sau R là bắt buộc khi kết luận R có ích (§10.3).

## 9. Cổng DEV2 (trước EXP2)

Output model trên DEV2 chỉ dùng cho các cổng ở đây. Nếu có tính contrast trên DEV2 để kiểm code, kết quả đó không được dùng để sửa luật đã khóa.

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | Khối đích trùng từng bit với input k0 ở mọi input | 100% |
| G2 | Đệm độc lập với đích: khối đệm sinh riêng trùng khối đệm trong bảng ghép (sau cùng phép z-score) | Trùng từng bit |
| G3 | Lồng nhau: E(0.5) ⊆ E(1) ⊆ E(2) ⊆ E(3); mã băm của π, U, noise_scale, bias, Z và tham số cơ chế như nhau ở mọi mức | 100% |
| G4 | Bí danh: input L2(s = 1) sinh theo đường L2 trùng từng bit L1(e = 2). L2(s = 0) tính theo công thức, so với L1(e = 0) sau z-score, trên float64 trước khi ép kiểu | Trùng từng bit (s = 1); sai lệch tuyệt đối tối đa ≤ 1e-12 (s = 0, float64) |
| G5 | e = 0 tương đương A: lập luận theo cách sinh (§3). Báo thêm, chỉ để mô tả: phân phối biên và trung bình \|ρ\| của cặp đệm | Mô tả, không phải kiểm định |
| G6 | Khớp phép tính gốc: với cùng đồ thị và tham số, x_j của bộ sinh mới bằng `RFFAdditive._rff_mechanism` (RFF) hoặc hàm lambda của `LinearAdditive` (tuyến tính) | Sai lệch tương đối tối đa ≤ 1e-9 ở mọi nút, mức, hệ |
| G7 | Có ghi số cạnh đệm thực tế và số nút cô lập; đồ thị dùng để sinh đúng là ma trận U < p_e | 100% |
| G8 | HSIC vector hóa so với `KCI_UInd(approx=True, est_width='median')` trên mọi cặp của các input e = 0, e = e_T và e = 3 thuộc 8 hệ RFF của DEV2. Kiểm hai thứ: sai lệch p-value, và **quyết định bác bỏ tại các ngưỡng Bonferroni thực tế** α/m, với mọi α trong lưới và đúng m của từng bảng | \|Δp\| tối đa ≤ 1e-6. Quyết định trùng 100%, trừ cặp mà cả hai p cách ngưỡng dưới 1e-9 (tương đối); những cặp đó được báo riêng. Nếu không đạt, dùng thẳng `KCI_UInd` |
| G9 | **Kiểm chẩn đoán**, cho từng phép kiểm (Fisher-z trên họ tuyến tính, HSIC trên họ RFF) và từng α trong lưới: (a) tỉ lệ bác bỏ theo cặp trên các cặp đích × đệm ở các mức từng cặp 0.05, 0.01, 0.001; (b) xác suất có ít nhất một cạnh chéo giả trong một input, tách hai trường hợp: đệm không có cạnh (e = 0) và đệm có cấu trúc (e > 0 cùng các mức L2) | Kèm CI theo hệ: Clopper–Pearson trên 8 hệ cho từng điều kiện; bootstrap cụm theo hệ (2000 lần) cho trường hợp gộp. Không phải bằng chứng "FWER đã được kiểm soát"; 0 lỗi trên 8 hệ vẫn cho cận trên một phía 95% khoảng 31%. Dừng và báo user nếu tỉ lệ bác bỏ theo cặp ở mức 0.05 lớn hơn 0.10 |
| G10 | Tất định và R-oracle: chạy lại 4 input mỗi model; R-oracle trùng k0 | Trùng trong τ đã đo ở P-N1 (`rn0_*.json`) |
| G11 | Thời gian: sàng lọc mỗi bảng, model mỗi input, PC/GES mỗi job; ước tính tổng thời gian EXP2 | Báo user trước EXP2; nếu ước tính vượt 12 giờ, dừng và hỏi |

## 10. EXP2 quyết định gì

1. **Giả thuyết mang sang HELD2:** **tổng cộng tối đa 5**, trong đó tối đa 2 giả thuyết mới. Không bắt buộc chọn đủ 5.
   - **Giả thuyết §7:** xét theo REP. L1-END ngược dấu không loại giả thuyết.
   - **Giả thuyết mới:** nhãn LARGE ở L1-END, L1-PROFILE hoặc L2 trên một Y chính, kể cả hình dạng khác dự đoán. Ghi rõ là "sinh từ EXP2".
   - **Khóa trước HELD2:** mỗi giả thuyết được khóa bằng model, họ, contrast, metric, dấu và cách tính p-value. Đề xuất: kiểm một phía bằng hoán vị dấu (sign-flip) trên contrast theo hệ; chốt ở luật HELD2.
   - **Holm** ở mức familywise 0.05 trên toàn bộ tập được chọn, áp lên các p-value đã khóa đó, không áp lên nhãn POS/NEG hay CI 95% của pha này. Holm vẫn đúng khi các phép kiểm phụ thuộc nhau.
2. **Cỡ mẫu HELD2:** tính từ phương sai của EXP2 cho đúng các contrast đã chọn, theo từng họ. Kế hoạch ban đầu là 80 hệ. Nếu ngân sách chỉ cho 80, vẫn giữ 80 và chấp nhận khả năng INCONCLUSIVE.
3. **Nhánh R: tách "làm giảm thay đổi" khỏi "sửa được lỗi".**
   - **"R làm giảm thay đổi trên biến đo Y"**: contrast R-* có nhãn SMALL trong khi contrast gốc có nhãn LARGE. Chỉ được nói đến mức đó: một R trả đồ thị rỗng ở mọi input cũng rất "ổn định" nhưng không hữu ích.
   - **"R là cách sửa có ích"** (cho từng model, họ, điều kiện c) cần thêm ba điều về chất lượng, dùng biên F1 0.03:
     - (a) **giá tại k0:** F1 sau R tại k0 so với F1 trước R tại k0. Hiệu phải SMALL.
     - (b) **sau R trên input có đệm:** F1 sau R tại c so với mốc k0 ban đầu (trước R). Hiệu phải SMALL.
     - (c) báo lỗi gộp, lỗi tách và thời gian.

     Nếu CI chưa đủ hẹp thì là UNCLEAR. Nếu (a) hoặc (b) xấu đi quá 0.03, với CI nằm hẳn ngoài biên, thì R không phải cách sửa có ích ở ô đó.
   - Nếu R không làm giảm thay đổi: ghi lại cơ chế còn sót (gộp nhầm hay tách nhầm).
4. **Bước sau:**
   - Can thiệp attention và FoundCause chỉ mở khi có ít nhất một hiệu ứng LARGE, hoặc một giả thuyết CONSISTENT.
   - Nếu mọi Y chính đều SMALL ở cả hai model và hai họ: ngừng đầu tư vào L1/L2. Failure của P-N1 vẫn đứng; quay về lựa chọn 1 (viết báo cáo phát hiện).
   - Kết quả UNCLEAR **không** được đọc là "không có hiệu ứng".

## 11. Ngân sách ước tính

Ước tính dựa trên thời gian chạy ở held-out P-N1, chưa đo cho P-N2:

- **Thời gian mỗi input ở k = 20:** AVICI khoảng 5–8 giây, CDFM khoảng 8 giây.
- **EXP2:** 40 hệ × (8 input thường + 8 input của nhánh R, chạy theo thành phần): khoảng 1–1.5 giờ mỗi model.
- **DEV2:** khoảng 0.5 giờ mỗi model.
- **Sàng lọc** với HSIC vector hóa: dự kiến vài giây mỗi bảng, sẽ đo ở G11. Phép so với `KCI_UInd` ở G8 chạy từng cặp, chậm hơn nhiều.
- **PC/GES:** 80 job mỗi thuật toán. GES ở B20 với d_T = 20 mất khoảng 14 giây; ở e = 3 có thể lâu hơn.

## 12. Quyết định đã chốt (20/11, review thứ ba của user)

| Điểm | Quyết định |
|---|---|
| 1. Chọn α | Riêng cho Fisher-z và HSIC, theo lưới và J trên DEV2. AVICI/CDFM dùng chung; giữ nguyên sang EXP2 và HELD2 |
| 2. k0 trong J | Không tính vào J. Chất lượng tại k0 trước/sau R là bắt buộc để kết luận R có ích |
| 3. Biên ngưỡng CDFM | 0.03, tức 3 điểm phần trăm xác suất; chỉ là biên cho độ đổi ngưỡng; tác động lên đồ thị đọc riêng |
| 4. PC/GES | Có, tại k0, e = 0, e = e_T và e = 3: 80 job mỗi thuật toán trên 20 hệ tuyến tính, khớp cả REP và L1-END |
| 5. HSIC cho cả hai họ | Có, chỉ đo sàng lọc, dùng cùng α_HSIC đã chọn |
| 6. Giả thuyết sang HELD2 | Tổng cộng tối đa 5, gồm tối đa 2 giả thuyết mới; Holm ở mức familywise 0.05 trên toàn bộ tập chọn; không cần chọn đủ 5 |

## 13. Nhật ký thay đổi (append-only sau khi khóa)

- **v0, 20/11/2026 (`18df91b`):** bản nháp đầu, viết sau hai review của user.
- **v1, 20/11/2026 (khóa):** theo review thứ ba của user.
  - Sáu quyết định ở §12.
  - **G8, G9:** G8 kiểm thêm quyết định bác bỏ tại ngưỡng Bonferroni thực tế. G9 báo xác suất có ít nhất một cạnh chéo giả, cho đệm không cạnh và đệm có cấu trúc, kèm CI theo hệ. α_HSIC gọi là mức danh nghĩa; G9 chỉ là kiểm chẩn đoán.
  - **§8.1:** ghi chú về `approx=False` (lấy mẫu null phổ, p có thể bằng 0); tính đuôi bằng `gamma.sf`.
  - **§10.3:** tách "làm giảm thay đổi" khỏi "sửa được lỗi", với ba điều kiện chất lượng.
  - **§8.1:** FROZEN sau R dùng một ngưỡng k0 duy nhất trước R. NATIVE sau R chỉ mô tả, không áp contrast của ngưỡng toàn bảng.
  - **§5:** top-m0 dùng mốc trước R; m0 = 0 thì loại hệ khỏi contrast đó.
  - **§7, §10.1:** giả thuyết xét theo REP; L1-END ngược dấu là "hình dạng khác dự đoán"; mỗi giả thuyết HELD2 khóa đủ sáu thành phần; Holm áp lên p-value.
  - **§3, §6:** REP chỉ lặp lại hiệu ứng trung bình, vì ghép cặp làm phân phối hiệu theo từng cặp khác P-N1.
  - **§3, G4:** Z rút một lần ngoài vòng lặp nút, với thứ tự gọi `rng_P` được ghi rõ. Phép kiểm 1e-12 của G4 làm trên float64 trước ép kiểu; hai bí danh dùng chung input float32.
  - **§4, G11:** PC/GES chạy cả trên DEV2 để đo thời gian.
- **DEV2, 20–21/11/2026** (luật v1, commit `5c2c76c`). Cổng dữ liệu chạy trước; job model chạy từ 17:16 UTC ngày 20/11 đến 01:23 UTC ngày 21/11.
  - **G1–G7 đạt.**
    - Khối đích trùng từng bit ở cả 112 input có đệm; khối đệm sinh riêng trùng khối đệm trong bảng ghép.
    - Lồng nhau và tham số như nhau ở mọi mức (16/16 hệ).
    - s = 1 trùng từng bit với e = 2. s = 0 lệch tối đa 1.06e-13 so với e = 0 (float64).
    - Khớp phép tính gốc của AVICI, sai lệch tương đối tối đa 5.2e-15. Đồ thị dùng để sinh đúng là U < p_e.
    - Số cạnh đệm thực tế trung bình 9.4, 19.6, 40.0, 60.4 ở e = 0.5, 1, 2, 3; số nút cô lập 7.2, 2.4, 0.4, 0.1.
  - **G5 (mô tả):** ở e = 0, trung bình |ρ| của cặp đệm là 0.033–0.039, so với 0.035 ± 0.002 của khối Gauss độc lập dùng làm tham chiếu.
  - **G8 đạt:** 14 580 cặp; |Δp| tối đa 6.2e-15; quyết định bác bỏ trùng 100% tại mọi ngưỡng Bonferroni thật; không có cặp sát ngưỡng.
  - **G9 (chẩn đoán), không chạm điều kiện dừng.**
    - **Fisher-z:**
      - Tỉ lệ bác bỏ theo cặp ở mức 0.05 là 0.045 (e = 0) và 0.050 (đệm có cấu trúc).
      - Không input nào có cạnh chéo giả, ở mọi α: 0/8 hệ ở e = 0 (Clopper–Pearson 95% [0, 0.37], cận trên một phía 0.31), và 0/48 input có cấu trúc.
    - **HSIC:**
      - Tỉ lệ theo cặp ở mức 0.05 là 0.044 và 0.046; ở mức 0.01 là 0.012 và 0.014; ở mức 0.001 là 0.0029 và 0.0040.
      - **Đuôi dễ dãi:** ở mức 0.001, tỉ lệ thực tế gấp 3–4 lần mức danh nghĩa.
      - Có ít nhất một cạnh chéo giả trong một input:
        - ở α = 0.01: 0/8 (e = 0) và 1/48 (có cấu trúc, 0.021 [0, 0.062]);
        - ở α = 0.05: 1/8 và 6/48 (0.125 [0, 0.375]).
    - Kết quả này đúng với giới hạn đã ghi ở §8.1: α_HSIC là mức danh nghĩa.
  - **Chọn α (§8.4):**
    - Fisher-z: J = 0.0507, 0.0382, 0.0382 ở α = 0.01, 0.05, 0.10. Hòa giữa 0.05 và 0.10, nên **α_Fz = 0.05**.
    - HSIC: J = 0.043, 0.107, 0.124, nên **α_HSIC = 0.01**.
    - Lỗi tách tại k0 (báo riêng): 2.8% cạnh thật (Fisher-z ở 0.05), 2.6% (HSIC ở 0.01).
    - Biến thể, chỉ để thông tin: HSIC trên họ tuyến tính J = 0.069; Spearman trên RFF J = 0.102; BH J = 0.43 (Fisher-z) và 0.36 (HSIC).
  - **G10 đạt:** chạy lại và R-oracle trùng từng bit với k0 ở cả hai model (τ = 0 như P-N1).
  - **G11: ước tính tự động 20.3 giờ, vượt 12 giờ.**
    - Nguyên nhân: một job CDFM (`DEV2-c5-r0`, s = 0.25) mất 25 743 giây. Máy vào chế độ ngủ từ 00:43 đến 07:52 giờ máy (nhật ký hệ thống: Kernel-Power 42 và Power-Troubleshooter 1). Job bắt đầu 7 giây trước khi máy ngủ và xong 6 giây sau khi máy thức.
    - Chạy lại job đó mất 8.78 giây và cho output trùng từng bit (`probs`, adjacency, ngưỡng). Các job CDFM khác mất 2–12 giây.
    - Thay thời gian của job đó bằng thời gian chạy lại, ước tính EXP2 khoảng 2.5 giờ.
    - Theo G11, dừng và báo user trước EXP2.
  - **Thay đổi code sau DEV2,** không ảnh hưởng phép tính: thêm lời gọi `SetThreadExecutionState` để giữ máy thức trong lúc runner chạy (`run2.py`, `run2_classical.py`, `screen_variants.py`). Lời gọi chỉ có hiệu lực trong tiến trình, không đổi cài đặt nguồn của máy.
  - **Kiểm code đọc:** `analyze2.py` (AVICI, CDFM, cổ điển) và `screen_variants.py` đã chạy trên DEV2 để kiểm code: chạy hết, đúng cấu trúc, không có NaN, một giá trị F1 khớp khi tính độc lập. Số liệu contrast của DEV2 không được dùng để sửa luật.
  - **Đóng băng cho EXP2:** snapshot ở [`code/`](code/) kèm `SHA256SUMS`; `verify_freeze2.py` chạy ở đầu và cuối EXP2.
