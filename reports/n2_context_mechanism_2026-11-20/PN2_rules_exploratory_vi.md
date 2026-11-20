# P-N2: luật đọc cho pha exploratory (bản nháp v0, chưa khóa, 20/11/2026)

> **Trạng thái:** **NHÁP, chưa khóa.** Luật này chỉ có hiệu lực sau khi user duyệt, được commit và push, và việc đó phải xảy ra trước khi có bất kỳ output P-N2 nào, kể cả DEV. Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §13 kèm lý do, và không được dựa trên metric đã thấy.
> **Nguồn thiết kế:**
>
> - [kiểm prior art §5–§7](../n1_irrelevant_vars_2026-11-13/N1_prior_art_recheck_2026-11-20_vi.md);
> - [phân tích hậu nghiệm held-out của P-N1](../n1_irrelevant_vars_2026-11-13/PN1_HELD_posthoc_rank_level_vi.md);
> - hai review của user ngày 20/11.
>
> **Không đổi gì của P-N1:** các nhãn INCONCLUSIVE giữ nguyên; luật [v2](../n1_irrelevant_vars_2026-11-13/PN1_reading_rules_vi.md), [v2.1](../n1_irrelevant_vars_2026-11-13/PN1_rules_v2_1_amendment_vi.md) và [v2.2](../n1_irrelevant_vars_2026-11-13/PN1_rules_v2_2_amendment_vi.md) không bị sửa.

## 0. Quy trình

1. User duyệt bản nháp này. Khóa luật: commit và push.
2. Viết code trong `artifacts/n2_runs/pn2/` (git-ignored); không đụng `artifacts/n1_runs/`.
3. Chạy **DEV2** và kiểm các cổng ở §9. Chọn α cho nhánh R theo đúng quy trình §8.4. Ghi kết quả DEV và α đã chọn vào §13.
4. Đóng băng code (snapshot kèm SHA-256 và cổng kiểm như P-N1), commit, push.
5. Chạy **EXP2** (40 hệ). Chỉ đọc sau khi đủ 40 hệ, bằng code đọc đã đóng băng.
6. Viết luật held-out (HELD2): cỡ mẫu tính từ phương sai của EXP2. Khóa, commit, push **trước khi** sinh dữ liệu hay chạy HELD2.

## 1. Câu hỏi và phạm vi

**Câu hỏi.** Vì sao một khối dữ liệu độc lập với khối đích lại làm model đổi cách chọn cạnh trong khối đích? Thay đổi ấy làm mất cạnh đúng hay loại cạnh sai? Nó nằm ở mức điểm (số cạnh) hay ở thứ hạng cạnh đúng/sai, và khác nhau thế nào giữa các model?

**Pha exploratory trả lời ba câu:**

- **L1:** ở cùng D, khi chỉ thay mật độ cạnh của khối đệm, output khối đích có đổi không, và theo hướng nào?
- **L2:** giữ đồ thị đệm cố định và chỉ thay cường độ phụ thuộc, output có đổi không?
- **R:** một bước sàng lọc cổ điển rẻ có xóa được các thay đổi đó không, và với chi phí gì?

**Ngoài phạm vi của pha này:** FoundCause, can thiệp attention, dữ liệu thật, claim xác nhận. Pha exploratory chỉ sinh và chọn giả thuyết cho held-out.

**Điều L1 không kiểm:** prior gắn với d (H1'), vì D giữ nguyên. Một đường liều–đáp ứng rõ chỉ xác lập độ nhạy với cấu trúc khối đệm, chưa quy nguyên nhân cho prior huấn luyện.

## 2. Hệ đích, tập seed, cỡ mẫu

- **Ô:** giữ 8 ô của P-N1, gồm d_T ∈ {10, 20} × số cạnh/nút e_T ∈ {1, 2} × cơ chế ∈ {tuyến tính, RFF}.
- **Sinh hệ đích:** như P-N1 (`target()` trong `common.py`): n = 500, config ER của ô, z-score; hệ đích không có cạnh thì thay bằng seed + 500.
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

**Luồng ngẫu nhiên.** `rng_P = default_rng(SeedSequence([seed gốc của hệ, 20261120, 2]))`. Seed gốc là base + 1000 × ô + r, lấy trước quy tắc thay seed của hệ đích. Luồng này tách khỏi luồng sinh khối đích; bộ sinh đệm không đọc dữ liệu đích.

**Rút một lần, theo thứ tự cố định, không phụ thuộc mức** (k = 20, n = 500):

1. π = `rng_P.permutation(k)`: thứ tự topo.
2. U = `rng_P.uniform(size=(k, k))`: chỉ dùng U[a, b] với a < b (vị trí trong π).
3. Theo nhãn nút j = 0, …, k − 1:
   - noise_scale_j ~ U[0.2, 2.0];
   - bias_j ~ U[−3, 3];
   - Z ~ N(0, 1), cỡ (n, k).
4. **Tuyến tính:** W ~ SignedUniform[1, 3], cỡ (k, k). W[i, j] là trọng số của cạnh i → j, như vector trọng số trên mọi nút mà `LinearAdditive` rút cho mỗi nút.
5. **RFF:** với mỗi nút j:
   - ls_j ~ U[7, 10] và c_j ~ U[10, 20];
   - Ω_j = G_j / ls_j, với G_j ~ N(0, 1) cỡ (k, 100); hàng i ứng với cha ứng viên i;
   - b_j ~ U[0, 2π] và w_j ~ N(0, 1), mỗi cái cỡ 100.

**Đồ thị ở mức e.** p_e = min(2e/(k − 1), 0.99). Có cạnh π[a] → π[b] khi a < b và U[a, b] < p_e.

- Vì p_e tăng theo e, tập cạnh tự lồng nhau: E(0.5) ⊆ E(1) ⊆ E(2) ⊆ E(3).
- Mỗi mức có đúng phân phối ER của AVICI với `edges_per_var = e`: mỗi cặp theo một thứ tự ngẫu nhiên có cạnh độc lập với xác suất p.

**Sinh dữ liệu** theo thứ tự π, với pa là tập cha của j (xếp tăng theo nhãn, như `onp.where` trong AVICI):

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
  - Dùng chung một job để kết quả không phụ thuộc vào làm tròn.

**Tương đương với P-N1 theo cách sinh, không dựa vào kiểm định:**

- Ở e = 0, các cột đệm là nhiễu Gauss độc lập đã z-score, nên **cùng phân phối với kiểu A** của P-N1.
- Ở e = e_T (số cạnh/nút của ô), họ đồ thị và phân phối tham số trùng **kiểu B** của P-N1. Kiểu B dùng `simulate_data`; hàm này hoán vị hàng, điều không đổi phân phối khi các mẫu i.i.d. Đây là các bản rút mới.

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

PC và GES là tùy chọn, chờ user quyết (§12).

## 5. Biến đo

Mọi biến đo tính trên khối đích, dạng skeleton, cho từng (hệ, input).

- **Số cạnh:**
  - m: số cạnh dự đoán ở NATIVE; với CDFM thêm FROZEN (ngưỡng CDFM tự chọn ở k0) và FIXED (0.5);
  - Δm = m − m(k0), |Δm| và Δm/d_T;
  - số cặp đích đổi trạng thái so với k0.
- **Thứ hạng** (không phụ thuộc ngưỡng):
  - AUROC và AP trên các cặp của khối đích, với điểm của cặp là max(p_ij, p_ji);
  - F1 ở top-m0, trong đó m0 = m(k0).
- **CDFM:** chính ngưỡng NATIVE.
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
| REP | Y(e = e_T) − Y(e = 0) | Lặp lại B − A của P-N1 về phân phối, trên seed mới. Dùng để kiểm giả thuyết §7 |
| L1-END | Y(e = 3) − Y(e = 0) | Đầu–cuối của đường liều–đáp ứng |
| L1-PROFILE | Y(e) − Y(0) với e ∈ {0.5, 1, 2, 3}, và độ dốc OLS theo e của từng hệ | Mô tả hình dạng, để không bỏ sót đường không đơn điệu |
| L2 | Y(s) − Y(s = 0) với s ∈ {0.25, 0.5}; s = 1 trùng L1(e = 2) | Cường độ ở đồ thị đệm cố định |
| R-* | Các contrast trên tính lại trên output sau nhánh R | Nhánh R có xóa thay đổi không |

**Y chính:**

- Δm (NATIVE; với CDFM thêm FROZEN và FIXED);
- AUROC;
- F1 ở top-m0;
- ngưỡng NATIVE của CDFM.

**Y phụ:** F1, TP, FP, |Δm|, số cặp đổi trạng thái, AP, Δm/d_T, logit trung bình, và kết quả tách theo d_T.

**Biên thực tiễn M:**

- Số cạnh: 1.5 cạnh, áp cho hiệu ứng **trung bình theo hệ** trong từng model và họ. Đây không có nghĩa "số cạnh không đổi ở mỗi hệ". Biên này là lựa chọn thực tiễn cho phạm vi này, không phải tiêu chuẩn thống kê phổ quát.
- AUROC, AP, F1, F1 ở top-m0: 0.03.
- Ngưỡng CDFM: 0.03 (đơn vị xác suất).

**Bootstrap:** 2000 lần, percentile, lấy mẫu lại theo hệ trong từng (model, họ), seed 20261120.

**Nhãn** cho mỗi (model, họ, contrast, Y), gồm hai phần:

- **dấu:** POS nếu cận dưới > 0; NEG nếu cận trên < 0; NONE nếu khác.
- **cỡ:**
  - SMALL nếu toàn bộ CI nằm trong [−M, M];
  - LARGE nếu toàn bộ CI nằm ngoài [−M, M] về một phía;
  - UNCLEAR nếu khác.

  Ước lượng điểm nhỏ mà CI rộng thì là UNCLEAR, không phải SMALL.

Pha exploratory không kiểm soát familywise. Mọi contrast đều được báo, không chọn lọc.

## 7. Giả thuyết định trước

Các giả thuyết dưới đây sinh hậu nghiệm từ held-out của P-N1, nên chỉ được kiểm trên seed mới.

- Kiểm trên **REP**; báo thêm L1-END như phép ngoại suy đơn điệu.
- Nhãn: **CONSISTENT** nếu dấu khớp dự đoán, **CONTRARY** nếu dấu ngược, **INCONCLUSIVE** nếu dấu là NONE. Nhãn cỡ (§6) báo kèm.

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
     - Kernel Gauss, độ rộng theo median heuristic cho từng biến, trên dữ liệu đã z-score.
     - p-value theo **xấp xỉ gamma** của phân phối null, như `KCI_UInd(approx=True, est_width='median')` của causal-learn (dựa trên Gretton et al. 2008).
     - Không dùng p-value hoán vị: với 999 hoán vị, p-value nhỏ nhất là 10⁻³, không đạt ngưỡng Bonferroni 0.05/780 ≈ 6.4 × 10⁻⁵ khi D = 40.
2. **Bonferroni:** bác bỏ độc lập khi p < α_FW / m. α_FW chọn trên DEV2 theo §8.4.
3. **Tách thành phần:** dựng đồ thị vô hướng từ các cặp bị bác bỏ, rồi lấy các thành phần liên thông.
4. **Chạy model** riêng trên từng thành phần có ít nhất 1 biến đích và ít nhất 2 biến.
   - Input là các cột gốc, đã z-score theo từng cột, nên không cần chuẩn hóa lại.
   - CDFM: ngưỡng NATIVE do CDFM tự chọn trên từng thành phần; FROZEN dùng ngưỡng ở k0; FIXED dùng 0.5.
5. **Output trên khối đích:**
   - hợp các cạnh dự đoán trong từng thành phần;
   - cặp đích nằm ở hai thành phần khác nhau thì không có cạnh, và điểm của cặp là 0 khi tính AUROC, AP;
   - biến đích đứng riêng một mình thì không có cạnh nào.

### 8.2 Đối chứng và biến thể

- **R-oracle** (biết trước ranh giới đích/đệm) chạy model trên đúng khối đích, nên trùng k0 theo cấu trúc. Chỉ kiểm sanity trên DEV2 (§9, G10), không phải kết quả.
- **R-data tại k0:** sàng lọc và chạy theo thành phần ngay trên khối đích. Phần này đo cái giá của việc tách chính khối đích.
- **Biến thể chỉ đo sàng lọc** (không chạy lại model):
  - Spearman cho họ RFF (đối chứng rẻ; Spearman chủ yếu nhạy với quan hệ đơn điệu);
  - HSIC cho họ tuyến tính (biến thể không cần biết họ cơ chế, chờ user quyết ở §12);
  - BH ở mức q = α_FW cho từng phép kiểm. BH kiểm soát tỉ lệ phát hiện sai, không trực tiếp kiểm soát xác suất nối nhầm thành phần.

### 8.3 Chỉ số sàng lọc

Cho mỗi input:

- **gộp** = số biến đệm nằm trong thành phần có ít nhất 1 biến đích;
- **tách** = số cạnh thật của khối đích có hai đầu nằm ở hai thành phần khác nhau;
- số thành phần chứa biến đích;
- thời gian chạy.

### 8.4 Chọn α_FW trên DEV2

1. **Lưới:** α_FW ∈ {0.01, 0.05, 0.10}. Chọn riêng cho từng phép kiểm: Fisher-z trên 4 ô tuyến tính, HSIC trên 4 ô RFF.
2. **Tiêu chí:** với mỗi input có đệm của DEV2, tính j = gộp/k + tách/|E_T|, trong đó |E_T| là số cạnh thật của khối đích. Lấy trung bình j theo hệ trong từng (ô, điều kiện có đệm). Sau đó lấy trung bình đều theo ô và theo 7 điều kiện có đệm (e ∈ {0, 0.5, 1, 2, 3}, s ∈ {0.25, 0.5}) để được J(α).
3. **Chọn** α có J nhỏ nhất. **Hòa điểm** (J bằng nhau khi làm tròn 3 chữ số): chọn 0.05 nếu 0.05 nằm trong nhóm hòa; nếu không, chọn α nhỏ nhất trong nhóm.
4. **Dùng gì để chọn:**
   - Chỉ dùng ground truth của dữ liệu DEV2, không dùng output model. Vì vậy AVICI và CDFM dùng chung lựa chọn.
   - Input k0 không tính vào J; lỗi tách ở k0 báo riêng.
   - Lựa chọn giữ nguyên cho EXP2 và HELD2.

## 9. Cổng DEV2 (trước EXP2)

Output model trên DEV2 chỉ dùng cho các cổng ở đây. Nếu có tính contrast trên DEV2 để kiểm code, kết quả đó không được dùng để sửa luật đã khóa.

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | Khối đích trùng từng bit với input k0 ở mọi input | 100% |
| G2 | Đệm độc lập với đích: khối đệm sinh riêng trùng khối đệm trong bảng ghép (sau cùng phép z-score) | Trùng từng bit |
| G3 | Lồng nhau: E(0.5) ⊆ E(1) ⊆ E(2) ⊆ E(3); mã băm của π, U, W hoặc Ω, b, w, c, ls, bias, noise_scale, Z như nhau ở mọi mức | 100% |
| G4 | Bí danh: input L2(s = 1) sinh theo đường L2 trùng từng bit L1(e = 2). Input L2(s = 0) sinh theo công thức khớp L1(e = 0) sau z-score; ghi sai lệch tối đa để tài liệu hóa (job dùng chung theo định nghĩa) | Trùng từng bit (s = 1); sai lệch ≤ 1e-12 (s = 0) |
| G5 | e = 0 tương đương A: lập luận theo cách sinh (§3). Báo thêm, chỉ để mô tả: phân phối biên và trung bình \|ρ\| của cặp đệm | Mô tả, không phải kiểm định |
| G6 | Khớp phép tính gốc: với cùng đồ thị và tham số, x_j của bộ sinh mới bằng `RFFAdditive._rff_mechanism` (RFF) hoặc hàm lambda của `LinearAdditive` (tuyến tính) | Sai lệch tương đối tối đa ≤ 1e-9 ở mọi nút, mức, hệ |
| G7 | Có ghi số cạnh đệm thực tế và số nút cô lập; đồ thị dùng để sinh đúng là ma trận U < p_e | 100% |
| G8 | HSIC: bản vector hóa khớp `KCI_UInd(approx=True, est_width='median')` trên ít nhất 500 cặp của DEV2 | \|Δp\| tối đa ≤ 1e-6; nếu không đạt, dùng thẳng `KCI_UInd` |
| G9 | Hiệu chỉnh dưới null (mô tả): trên các cặp đích × đệm ở e = 0, tỉ lệ bác bỏ ở mức từng cặp 0.05, 0.01, 0.001; FWER theo hệ ở ngưỡng Bonferroni cho từng α trong lưới | Dừng và báo user nếu tỉ lệ ở 0.05 lớn hơn 0.10 |
| G10 | Tất định và R-oracle: chạy lại 4 input mỗi model; R-oracle trùng k0 | Trùng trong τ đã đo ở P-N1 (`rn0_*.json`) |
| G11 | Thời gian: đo thời gian sàng lọc mỗi bảng và thời gian model mỗi input; ước tính tổng thời gian EXP2 | Báo user trước EXP2; nếu ước tính vượt 12 giờ, dừng và hỏi |

## 10. EXP2 quyết định gì

1. **Giả thuyết mang sang HELD2:** tối đa 5.
   - Ưu tiên các giả thuyết §7 có nhãn CONSISTENT ở REP và không có dấu ngược ở L1-END.
   - Có thể thêm tối đa 2 pattern mới (nhãn LARGE ở L1-END hoặc L2 trên một Y chính), ghi rõ là "sinh từ EXP2".
   - Luật HELD2 sẽ định nghĩa nhãn xác nhận và hiệu chỉnh đa kiểm định (đề xuất Holm) trên các giả thuyết đã chọn.
2. **Cỡ mẫu HELD2:** tính từ phương sai của EXP2 cho đúng các contrast đã chọn, theo từng họ. Kế hoạch ban đầu là 80 hệ. Nếu ngân sách chỉ cho 80, vẫn giữ 80 và chấp nhận khả năng INCONCLUSIVE.
3. **Nhánh R:**
   - Nếu R-* của contrast có nhãn SMALL trong khi contrast gốc là LARGE: ghi là "R xóa thay đổi", kèm chi phí (lỗi tách ở k0, thời gian). Khi đó khung bài là "failure + cơ chế + cách sửa rẻ"; đó vẫn là kết quả có ích.
   - Nếu R không xóa được: ghi lại cơ chế còn sót (gộp nhầm hay tách nhầm).
4. **Bước sau:**
   - Can thiệp attention và FoundCause chỉ mở khi có ít nhất một hiệu ứng LARGE, hoặc một giả thuyết CONSISTENT.
   - Nếu mọi Y chính đều SMALL ở cả hai model và hai họ: ngừng đầu tư vào L1/L2. Failure của P-N1 vẫn đứng; quay về lựa chọn 1 (viết báo cáo phát hiện).
   - Kết quả UNCLEAR **không** được đọc là "không có hiệu ứng".

## 11. Ngân sách ước tính

Ước tính dựa trên thời gian chạy ở held-out P-N1, chưa đo cho P-N2:

- **Thời gian mỗi input ở k = 20:** AVICI khoảng 5–8 giây, CDFM khoảng 8 giây.
- **EXP2:** 40 hệ × (8 input thường + 8 input của nhánh R, chạy theo thành phần): khoảng 1–1.5 giờ mỗi model.
- **DEV2:** khoảng 0.5 giờ mỗi model.
- **Sàng lọc** với HSIC vector hóa: dự kiến vài giây mỗi bảng, sẽ đo ở G11.
- **PC/GES tùy chọn** (§12): GES ở B20 với d_T = 20 mất khoảng 14 giây; ở e = 3 có thể lâu hơn.

## 12. Điểm còn mở, cần user quyết trước khi khóa

1. **Chọn α:** chọn α_FW riêng cho từng phép kiểm (Fisher-z, HSIC), như §8.4; hay dùng một α chung cho cả hai họ.
2. **J có tính input k0 không:** đề xuất là không (§8.4), lỗi tách ở k0 báo riêng.
3. **Biên cho ngưỡng CDFM:** 0.03.
4. **PC và GES** trên các hệ tuyến tính, tại k0, e = 0 và e = 3: tùy chọn, khoảng 60 job mỗi thuật toán. Mục đích là giữ mốc cổ điển cho các điều kiện mới. Đề xuất: có.
5. **Biến thể R không cần biết họ** (HSIC cho cả hệ tuyến tính): chỉ đo sàng lọc, như §8.2. Đề xuất: có.
6. **Giới hạn giả thuyết mang sang HELD2:** tối đa 5, dùng Holm ở HELD2.

## 13. Nhật ký thay đổi (append-only sau khi khóa)

- **v0, 20/11/2026:** bản nháp đầu, viết sau hai review của user. Chưa khóa.
