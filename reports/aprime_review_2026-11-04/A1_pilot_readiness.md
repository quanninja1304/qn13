# A′ — Pilot readiness, novelty audit & decision memo (Day 3)

> Ngày: 2026-11-04. Đầu vào:
> - Day 1: `A1_mathematical_contract_v2.md`
> - Day 2: `A1_toy_results.md` (+ `A1_toy_mechanism_validation.py`, `A1_toy_outputs.json`, `A1_toy_run_log.txt`)
> - `A1_missing_references_register.md`
> - Tài liệu gốc trong `reports/reassessment_2026-11-03_vi/` (không sửa)
>
> Nhãn: [Source-verified], [Derived], [Toy-observed] (đã chạy, chỉ toy), [Proposed] (chưa chạy), [UNVERIFIED], [ABSTRACT ONLY].
> **Không có benchmark nhân quả nào đã được chạy.**

---

## 0. Executive verdict

**Quyết định: `REFORMULATE` (kèm `HOLD FOR SOURCE` cho phần novelty của bản reformulated). Không GO tới pilot nhân quả. A′ theo framing gốc: STOP.**

Ba lý do chính:

1. **Framing gốc không đứng được.** Framing gốc là: D(f) dạng hiệu dùng full Σ̂, claim chính H-cal ("ACI trôi, D(f) không trôi"), Gaussian chỉ làm arm kiểm chứng, niche là GCM/kernel. Cả bốn trụ của nó đều có phản chứng:
   - **Toán:** Σ của Fisher-z Gaussian suy biến cấu trúc (rank ≤ p(p−1)/2). Các query "gần trùng", vốn là động lực của A′, có tương quan tiệm cận đúng bằng 1. Quy ước P5 gán +∞ cho chính mô hình đúng ở 100% replicate. [Derived + Toy-observed: C1, C2]
   - **Thống kê:** D dạng hiệu không có calibration. Ở toy, D_full trôi FAR như diag (0.110 so với 0.105 ở δ = 3, r = 0.9). D đổi dấu với xác suất → 1 khi η misspecified. [Toy-observed: B2, E]
   - **Thiết kế:** metric Δ_FAR được pre-register trong [PLAN] §3 **phạt chính phương pháp đúng**: full-Σ trôi 0.871 so với diag 0.509 ở K = 8. [Toy-observed: B3]
   - **Novelty:** phần "dependence-aware" là constrained GLS/projection cổ điển. Ở ví dụ khả thi, evidence nó trích ra chính là thống kê của một query **ngoài Q** (corr = −0.9998). [Derived + Toy-observed: C3]
2. **Có một bản reformulated có nghĩa thống kê đã chứng minh được** (R1 + R2, contract §7):
   - *Simultaneous certified ancestral assertions*: assert f ⇔ d_Σ(z, R(M_¬f))² > χ²_{rank, 1−α}.
   - Kèm *η-profile* η*(f): mức strong-faithfulness tối thiểu cần để f được chứng nhận.
   - Validity (conservative) được **chứng minh trên giấy** dưới: Q cố định, joint CLT, beta-min. Nó **không** phụ thuộc relaxation R ⊋ A, và **tránh** được vấn đề rank nhờ seminorm cùng ngưỡng χ²_rank.
   - Đây là câu hỏi khoa học khác: từ "dependence-aware confidence" sang "**chứng nhận feature dưới strong faithfulness**".
3. **Novelty của bản reformulated chưa đánh giá được.** Wang–Kolar–Drton (JASA 2025) theo tóm tắt đã nghịch đảo kiểm định để có confidence set ordering, suy ra sub/superset ancestral relations [ABSTRACT ONLY]. Triantafillou et al. (PGM 2014) chưa đọc. Đây là hai nguồn quyết định.

**Điều làm đảo ngược quyết định:** xem §9.

---

## 1. Claim & prior-art register (Workstream 1)

| # | Claim dự kiến | Nghĩa toán/thống kê chính xác | Prior art gần nhất và điều nó thực sự làm | Residual novelty [giả thuyết] | Bằng chứng cần | Tier hiện tại | Falsification tối thiểu |
|---|---|---|---|---|---|---|---|
| C1 | "Feature confidence cộng tính (ACI) đếm trùng evidence" | Loss Eq. 13 cộng weights; với thống kê tương quan dương và mô hình khác nhau ở ≥ 2 tọa độ, tổng chéo có đuôi nặng hơn χ² | **ACI** [Source-verified, tr. 4–5, 9]: loss cộng tính; chính tác giả viết "loss function essentially assumes that the test results are independent… (which is not true)". **BSC-D** [Source-verified]: mô hình dependence quyết định nhị phân; BSC-I ≈ BSC-D về SHD/thứ tự PAG; phỏng đoán miscalibration | **Thấp.** Đã được chính ACI thừa nhận. Toy B1 cho thấy trong cấu hình P4 *không có* đếm trùng (diag đúng mức 0.049) | Đo trên causal SCM: tần suất cấu hình "≥ 2 tọa độ tương quan cùng phân biệt f" | Toy-observed (B2), chưa causal | H-prev (§5) cho thấy hiếm |
| C2 | "Off-diagonal là cơ chế mới" | Non-separability của dạng toàn phương không chéo (P4) | GLS/WLS cổ điển; constrained GLS | **Không.** Tính chất tổng quát [Derived] | — | Derived | — |
| C3 | "D(f) calibrated hơn ACI (H-cal)" | Ngưỡng cố định ⇒ FAR không trôi | — | — | — | **Bác bỏ cho D** (B2, δ = 3; B3) | Đã falsify ở toy |
| C4 | "Duplicate invariance" (P5) | Bất biến dưới bản sao chính xác, quy ước C-b | ACI + dedup đạt cùng tính chất | **Không** (tầm thường); lại sai dưới C-c (CE8) | — | Derived + toy | — |
| C5 | "Arm GCM là niche không có full likelihood" | Joint CLT cho K thống kê GCM + bootstrap Σ̂ | **Shah–Peters** [Source-verified]: CLT đơn biến (Thm 6), no-free-lunch (Thm 2), power chỉ khi E cov ≠ 0 | Có thể, nhưng **chưa có joint CLT** và toy B4 cho thấy Σ̂ nhiễu làm full-Σ anti-conservative | Chứng minh joint CLT; đo ổn định Σ̂ bootstrap | Open | B4-type check với bootstrap GCM thật |
| C6 | **(R1)** Simultaneous certified assertions: P(∃ f bị assert sai) ≤ α + o(1) dưới (Q cố định, joint CLT, beta-min η) | Projection của Mahalanobis confidence ellipsoid lên hợp vùng m-separation; ngưỡng χ²_rank | Scheffé-type projection [cổ điển]; Berger IUT [Source-verified TR]. **Wang–Kolar–Drton JASA 2025** [ABSTRACT ONLY]: test inversion → confidence set ordering → sub/superset ancestral, SEM identifiable, không latent (theo tóm tắt). **Strieder et al. UAI 2021** [METADATA]. **Guo–Wu–Yiu** [Source-verified]: selective inference cho effect, không feature | **Chưa biết.** Phần có thể mới: (a) dùng vùng m-separation của MAG (latent) thay cho ordering; (b) chỉ cần vector CI statistics, nên áp dụng được cho test tổng quát | Đọc full text Wang–Kolar–Drton và Triantafillou 2014 | Derived (validity, giấy); chưa toy cho power | Nếu một trong hai paper đã làm projection lên ancestral features **có latent** ⇒ STOP |
| C7 | **(R2)** η-profile η*(f) là sensitivity analysis có nghĩa với strong faithfulness | η*(f) = inf{η : f được chứng nhận}; đơn điệu theo η (vùng phía ¬f co lại khi η tăng) [Derived: R_n(m) giảm theo η ⇒ d tăng] | **Zhang–Spirtes 2003; Uhler et al. 2013** [METADATA/ABSTRACT]: λ-strong faithfulness, tần suất co lại theo kích thước đồ thị | **Chưa biết** [Hypothesis]: chưa thấy báo cáo "mức strong-faithfulness tối thiểu cho từng feature" trong nguồn đã đọc. "Chưa thấy" ≠ "không có" | Tìm kiếm có hệ thống; chứng minh đơn điệu chặt; power check | Hypothesis | Nếu η*(f) > hiệu ứng điển hình cho hầu hết feature đúng ở n ≤ 5000 ⇒ vô dụng thực tế |
| C8 | "Ở Gaussian, D ≈ full-likelihood" (thay vì đối thủ) | Mệnh đề E; R3 minimum-distance | RICF/Gaussian MAG likelihood [Source-verified ở [PLAN]]; Browne-type ADF [UNVERIFIED] | Không phải đóng góp; là **sanity proposition** | — | Derived bậc một + toy C3 | — |

**Phân tích đối nghịch "phương pháp đã biết có làm được không?":**
- Với C6, một reviewer sẽ hỏi: *"Đây chỉ là chiếu confidence ellipsoid của các partial correlation, rồi đọc ra feature nào bất biến trên mọi MAG tương thích, đúng không?"* Câu trả lời trung thực là **đúng vậy**.
- Đóng góp phải nằm ở:
  - (i) vùng tương thích cho MAG có latent và cách tính khoảng cách tới hợp của chúng;
  - (ii) η-profile;
  - (iii) bằng chứng rằng nó **có power** ở kích thước thực tế.
- Nếu (iii) thất bại, không có đóng góp.

---

## 2. Missing references

Xem `A1_missing_references_register.md`. Tóm tắt các quyết định bị chặn:

| Nguồn | Quyết định bị chặn |
|---|---|
| Wang–Kolar–Drton (full text) | Novelty C6 |
| Triantafillou 2014 | Novelty C6/C7 cho feature-level trong constraint-based; baseline B6 |
| Silvapulle–Sen | Chỉ calibration *chặt* (non-conservative); không chặn R1 |
| Zhang 2008 | Endpoint features (đã loại khỏi phạm vi) |
| Berger, Olkin–Finn | Không chặn quyết định nào |

---

## 3. Giả định nhân quả và thống kê (cho bản reformulated)

| Giả định | Loại | Kiểm tra được? | Nếu sai |
|---|---|---|---|
| Acyclic, latent/selection được biểu diễn bởi MAG trong M; m* ∈ M | Nhân quả | Không | Validity mất |
| Faithfulness + **λ-strong (beta-min) với η** | Nhân quả/thống kê | **Không** (no-free-lunch) | Đó là lý do R2 báo cáo η*(f) thay vì giả định η |
| Q cố định trước dữ liệu (hoặc split) | Thiết kế | Có (bằng thủ tục) | Nếu Q thích nghi trên cùng mẫu thì validity mất (Guo–Wu–Yiu Thm 1) |
| Joint CLT của z; Σ hoặc rank(Σ) ước lượng nhất quán | Thống kê | Một phần | Gaussian: có (delta method, C1 kiểm chứng). GCM: **chưa chứng minh** |
| Σ chung giữa các giả thuyết | Working model | Đo được (C4: 0.81 so với 0.80) | Ảnh hưởng bậc hai lên calibration |

---

## 4. Estimand

| Lựa chọn | Estimand | Ưu | Nhược | Khuyến nghị |
|---|---|---|---|---|
| E1 | **Family-wise false certification rate**: P(∃ f ∈ F được assert mà f(m*) sai), cùng **certification power** (tỷ lệ feature đúng & Q-identifiable được assert) | Có guarantee đã chứng minh (R1); định nghĩa rõ | Có thể bảo thủ quá mức khi K lớn (χ²_K) | **Primary** |
| E2 | η*(f) cho từng feature; đánh giá bằng quan hệ giữa η*(f) và min |atanh ρ| thật trên các dependence liên quan | Biến giả định thành output | Chưa có prior art đã đọc; cần định nghĩa "các dependence liên quan" | Secondary, chỉ sau E1 |
| E3 | FAR tại ngưỡng cố định (H-cal gốc) | — | Đã bị toy bác bỏ cho D; protocol transfer phạt phương pháp đúng (B3) | **Loại** |
| E4 | Risk–coverage / ranking (H-rank) | Không cần calibration | BSC-D cho thấy ranking ít đổi ở cấp PAG; toy cho thấy ranking đổi mạnh nhưng không biết theo chiều nào | Báo cáo mô tả, không làm primary |

**Primary hypothesis (đề xuất, chưa pre-register):**
- *H-power:* ở p ≤ 5, n ∈ {500, 2000, 5000}, với Q cố định (mọi query bậc ≤ 1 hoặc ≤ 2), R1 (rank-aware) chứng nhận được một tỷ lệ **khác không đáng kể** các ancestral feature đúng, trong khi giữ family-wise false certification ≤ α.
- Tỷ lệ này cao hơn các thủ tục valid đơn giản cùng mức α: Bonferroni per-test IUT, và diag-χ² trên tập query đã làm trắng.
- Nếu R1 không vượt **Bonferroni per-test** ở cùng validity, thì "dependence-aware" không mua được gì.

---

## 5. Baseline contracts (Workstream 4) — cho estimand E1

| Baseline | Provenance | Input | Output semantics | Valid ở mức α? | Same-target? | Trạng thái |
|---|---|---|---|---|---|---|
| **BL1: Bonferroni per-test IUT** | Tự viết; Berger TR M555 Thm 1 | z, Q, M, η | Assert f nếu mọi m ∈ M_¬f bị bác bỏ bởi ít nhất một test tọa độ ở mức α/K | **Có** (union bound) [Derived] | **Có**, cùng target | Proposed |
| **BL2: R1 với Σ chéo** (diag-χ²) | Tự viết | z, Q, M, η | Như R1 nhưng bỏ off-diagonal | **Không** khi tương quan dương (toy B2/B3: tới 0.156) | Có | Proposed; control quan trọng nhất |
| **BL3: R1 trên Q-closure** | Tự viết | Q′ ⊇ Q | — | Có | Có, nhưng khác input | Proposed; tách "thông tin thêm" (Mệnh đề E) |
| BL4: ACI Eq. 16 (thresholded C(f) > c) | Tự cài lại ([PLAN] B1); bản gốc dùng clingo/ASP | p-values, α | Score, **không** có validity | Không | **Apples-to-oranges** về semantics; dùng chỉ để mô tả | Proposed, phụ |
| BL5: Bootstrap FCI feature frequency (ngưỡng) | causal-learn 0.1.4.8 (đã có trong env) | data | Tần suất | Không | Apples-to-oranges | Proposed, phụ |
| BL6: Forced-feature Gaussian LR + parametric bootstrap calibration | RICF tự viết ([PLAN] B4) | data | LR có ngưỡng bootstrap | Xấp xỉ | Có, chỉ Gaussian | Proposed; đắt |
| BL7: Wang–Kolar–Drton confidence set | Paper JASA 2025 | data | Confidence set ordering ⇒ ancestral | Có (theo tóm tắt), **dưới giả định khác** (không latent?) | Chỉ khi không latent | **Chờ đọc paper** |
| BL8: BSC-D | bscd.pdf | discrete data | xác suất PAG | Không | Apples-to-oranges (discrete, cấp PAG) | **Không dùng** cho E1 |

---

## 6. Benchmark registry — **chỉ đề xuất, chưa chạy** (Workstream 4)

| ID | Mục đích | Thiết lập | Graph truth | Ghi chú |
|---|---|---|---|---|
| S0 | H-prev giải tích | Linear-Gaussian SCM ngẫu nhiên, p ∈ {4, 5}, mật độ ∈ {thưa, dày}, latent ∈ {0, 1 biến}; Q = mọi query bậc ≤ 1 (≤ 2); **không cần mô phỏng dữ liệu**: Σ tính bằng delta method tại ma trận tương quan thật (công thức đã kiểm chứng ở C1) | MAG = latent projection (cần implementation đã kiểm tra) | Đo: rank Σ, số first-order duplicate (r > 0.99), phân phối \|r_ij\| giữa các query cùng phân biệt một feature |
| S1 | Power/validity E1 (pilot tối thiểu) | Như S0, n ∈ {500, 2000, 5000}, 200 SCM × 1 dataset/SCM (pilot seeds 0–199) | như trên | Đơn vị độc lập: SCM |
| S2 | Hold-out adaptive-Q stress | Q do FCI chọn trên cùng mẫu so với split | như trên | Kiểm tra mức vi phạm validity khi bỏ qua selection |
| S3 | η-misspecification | Hiệu ứng thật lấy ngẫu nhiên quanh η | như trên | Lặp lại Experiment E trong causal setting |
| S4 | Nonparametric (chỉ khi joint CLT GCM được chứng minh) | ANM phi tuyến, p ≤ 4 | như trên | Σ̂ bootstrap; B ∈ {200, 1000} |
| Public | bnlearn subsets (CHILD/ALARM) với biến ẩn | Gaussianized hoặc discrete | Graph công bố, ghi rõ là adaptation | Chỉ sau S1 dương |
| Real | Sachs | — | **Không** coi là ground truth đầy đủ | Chỉ plausibility |

**Không dùng graph truth để chọn mô hình hay chọn η.** η phải cố định trước, hoặc báo cáo η-profile.

---

## 7. Metrics và robustness (Workstream 5)

| Hypothesis | Primary metric | Định nghĩa / mẫu số | Đơn vị | Uncertainty | Negative/adverse control |
|---|---|---|---|---|---|
| E1-validity | Family-wise false certification rate | #SCM có ≥ 1 assertion sai / #SCM | SCM | Clopper–Pearson theo SCM | Tương quan off-diagonal = 0 (r ≈ 0) phải cho R1 ≈ BL2 |
| E1-power | Certification rate | #(f đúng, Q-identifiable, được assert) / #(f đúng, Q-identifiable) gộp theo SCM | SCM (trung bình tỷ lệ trong SCM) | Paired bootstrap theo SCM | Feature không Q-identifiable: phải luôn 0 (P1-iii) |
| E2 | Quan hệ η*(f) với min-effect thật | Spearman giữa η*(f) và min \|atanh ρ\| trên các query trong "proof" | feature lồng trong SCM | Bootstrap phân cấp | Hoán vị nhãn feature |
| Chi phí | #CI test, #QP, runtime, RSS | — | SCM | — | — |

- **Rò rỉ:** dùng cùng mẫu để chọn Q và để score là vi phạm (S2 đo mức độ).
- **Tương quan giữa feature:** các feature trong một SCM phụ thuộc nhau, nên mọi CI phải tính theo SCM.
- **Ngưỡng go/no-go** ở §9 là **lựa chọn quản lý dự án**, không phải tiêu chuẩn thống kê. Chưa có pre-registration nào được khóa.

---

## 8. Resource & feasibility (Workstream 6)

| Hạng mục | Ước lượng | Cơ sở |
|---|---|---|
| Solver dist exact (liệt kê active set) | **Đã có trong toy**; chi phí 3^{#dep} QP nhỏ mỗi mô hình. K = 6, #dep ≤ 6 ⇒ ≤ 729 hệ tuyến tính | Đo thật: Experiment A chạy nhanh (toàn bộ script 312 s, phần lớn là MC dữ liệu) |
| K lớn (mọi query bậc ≤ 2, p = 5: 10 cặp × 7 tập ≤ 2 = 70) | 3^{#dep} **không khả thi** nếu #dep lớn ⇒ cần QP solver thật / MIQP; chưa đo | **UNKNOWN**, phải microbenchmark |
| Enumerate MAG p = 4, 5 | **UNKNOWN**: chưa đếm; repo chưa có code | [PLAN] §4 P2 cũng ghi Unresolved |
| m-separation / latent projection | `networkx` 3.6.1, `causal-learn` có trong env; cần kiểm chứng chéo | — |
| ACI reproduce | Không có clingo trong env (chưa kiểm tra); dùng exhaustive trên M | [PLAN] B1 |
| GCM joint CLT | Công việc lý thuyết, chưa có nguồn | Shah–Peters Thm 6 chỉ đơn biến |
| Licensing | causal-learn (MIT, theo hiểu biết; **chưa xác minh** trong phiên) | — |

---

## 9. Adversarial decision & branching (Workstream 7)

| Kết cục | Điều kiện | Đánh giá với bằng chứng hiện có |
|---|---|---|
| GO TO MINIMAL CAUSAL PILOT | Target toán hợp lệ, toy relevant, residual novelty plausible, có same-target baseline | **Chưa đủ.** Target R1 hợp lệ trên giấy; baseline BL1–BL3 có. Nhưng novelty bị chặn bởi 2 nguồn, và **power chưa có bất kỳ bằng chứng nào** |
| **REFORMULATE** | Vấn đề lõi giải được nhưng câu hỏi/score/estimand phải đổi | **Chọn.** Đổi D → T + χ²_rank (R1); đổi H-cal → E1 (validity + power); thêm η-profile (R2); bỏ claim "dependence-aware là đóng góp" |
| **HOLD FOR SOURCE** | Nguồn quyết định chưa có | **Áp dụng đồng thời** cho novelty của R1/R2: Wang–Kolar–Drton, Triantafillou 2014 |
| STOP / PIVOT | Không có gap, objective sai, hoặc không đo được | **Áp dụng cho framing gốc** (D(f), H-cal). Bản reformulated **chưa** đủ bằng chứng để STOP |

### Phase gates cho bản reformulated (đề xuất; mỗi gate cần user duyệt)

| Gate | Việc (bounded) | Pass | Fail ⇒ |
|---|---|---|---|
| **RG0 – Source** | User bổ sung PDF Wang–Kolar–Drton và Triantafillou 2014; đọc full text | Không paper nào đã làm projection/test-inversion cho ancestral features **với latent (MAG)** từ vector CI statistics | **STOP A′**, pivot T4 hoặc hướng khác |
| **RG1 – Paper math** | Viết chứng minh đầy đủ R1 (rank-aware, seminorm, χ²_rank, Q cố định); đơn điệu của η*(f); điều kiện để T(f) có power (khoảng cách giữa R(M_¬f) và ζ_n) | Chứng minh được kiểm tra độc lập | Sửa hoặc STOP |
| **RG2 – Toy power** (rẻ, không MAG) | Trên toy K = 2–6 với ζ thật đã biết: so sánh power R1 với BL1 (Bonferroni) và BL2 ở cùng α | R1 > BL1 rõ rệt ở ít nhất một regime tương quan thực tế | Nếu R1 ≤ BL1 mọi nơi ⇒ dependence không mua gì ⇒ STOP |
| **RG3 – H-prev giải tích (S0)** | Delta method trên SCM ngẫu nhiên p = 4–5 | Có ≥ 2 regime với tương quan đáng kể giữa các query cùng phân biệt feature | Nếu tương quan nhỏ ⇒ R1 ≈ BL2 ⇒ STOP |
| RG4 – Minimal causal pilot (S1) | Chỉ sau RG0–RG3 | Validity ≤ α và power > BL1, paired CI loại 0 | Negative-result memo |

### Bằng chứng sẽ đảo ngược quyết định

- **Từ REFORMULATE → STOP:**
  - RG0 cho thấy prior art đã có;
  - RG2 cho thấy R1 không hơn Bonferroni;
  - RG3 cho thấy tương quan liên quan nhỏ.
- **Từ REFORMULATE → GO (pilot S1):** RG0 sạch, RG1 có chứng minh đã kiểm tra, RG2 dương, RG3 dương.
- **Từ STOP-framing-gốc → sống lại:** chỉ khi có bằng chứng mới rằng D dạng hiệu có calibration trên một lớp bài toán đã định nghĩa. Day 2 không cho thấy điều đó.

**Hướng khác:** T4 (*selection-indexed premises under missingness*, `reports/reassessment_2026-11-03_vi/topic_cards/T4_…`) vẫn mở. Nó **không** tự động mới chỉ vì A′ yếu đi, và phải qua cùng audit.

---

## 10. Next action chính xác

1. **(User)** Bổ sung vào `docs/papers/`: Wang, Kolar, Drton, *Confidence Sets for Causal Orderings*, JASA 2025 (doi:10.1080/01621459.2025.2542552; arXiv 2305.14506), và Triantafillou et al. PGM 2014. Quyết định chọn REFORMULATE (RG0–RG3) hay chuyển sang T4.
2. **(Agent, không cần compute, làm được ngay khi user đồng ý)** RG1: viết chứng minh R1 đầy đủ. RG2: mở rộng script toy với BL1/BL2 power, vẫn là toy, cùng spec.
3. **Không** xây `src/safety_prior/aprime/`, **không** enumerate MAG, **không** chạy S1 trước RG0–RG3.
4. [PLAN] §3 (pre-registration) và §4 P1a/GA1 **không còn phù hợp** (B3). Nếu tiếp tục, cần viết plan mới; **không sửa** file plan cũ ngoài việc append decision log.

---

## 11. Addendum 2026-11-04 — sau khi đọc 19 nguồn bổ sung (`A1_missing_references_register.md` §4–§5)

**RG0 (agent, chưa có user duyệt): PASS.** Không nguồn nào trong số đã đọc (WKD 2026 + supplement, Strieder et al. 2021, Strieder–Drton 2023/2024, Wang–Drton 2023, Chang–Guo–Malinsky, Guo–Wu–Yiu, Triantafillou 2014, ACI, BSC-D, ICP) cho **chứng nhận ancestral feature có validity frequentist trong setting có latent (MAG/PAG), từ CI statistics**:

| Nguồn gần nhất | Thiếu gì so với R1 |
|---|---|
| WKD 2026 | Causal sufficiency; SEM identifiable (không Gaussian-Markov-equivalence) |
| Chang–Guo–Malinsky | Target effect; PC (causal sufficiency) |
| Guo–Wu–Yiu | Target effect (FCI, có latent) |
| Triantafillou 2014 | Chỉ skeleton; Bayesian heuristic; không validity |
| ACI / BSC-D | Không validity |
| Strieder–Drton | Equal variances; target effect |

**Nhưng novelty bị thu hẹp thêm, và phải nói thẳng:**
1. **Bước projection** (confidence set mô hình ⇒ feature) là lập luận tổ hợp của WKD Lemma 3. Không có lý thuyết mới.
2. **Bước kiểm định từng MAG** từ vector CI statistics là GLS/minimum-discrepancy kiểu Browne 1984 với ràng buộc. Khung này cổ điển; phần áp vào hợp vùng của MAG là [Derived].
3. **Phần còn lại có thể là đóng góp:**
   - (a) **công cụ** chứng nhận feature cho setting latent + Markov equivalence, nơi WKD không áp dụng được;
   - (b) bằng chứng **power** thực tế so với baseline valid đơn giản;
   - (c) η-profile cho guarantee đồng đều.
   Đây là đóng góp **phương pháp/ứng dụng** cỡ UAI/AISTATS hoặc journal chuyên ngành **nếu (b) dương**. Nó không phải cơ chế khoa học mới, và **không** mang danh "dependence-aware" như A′ gốc.
4. **Erratum η** (contract v2 §10b): R1 valid **pointwise** với η_n → 0, không cần biết η. η chỉ cần cho guarantee uniform. Điều này làm R1 *dễ bảo vệ hơn*, nhưng làm R2 trở thành phần phụ.
5. **Rủi ro bị đi trước:** WKD nêu mở rộng sang latent là future work, trỏ tới Wang–Drton 2023 (non-Gaussian, có latent). Một "WKD + latent" non-Gaussian từ nhóm này là khả năng thật. R1 chỉ giữ được khác biệt ở setting **CI-based/Gaussian/Markov-equivalence**.

**Baseline bắt buộc mới:**
- **BL9: Chang-style resampling & screening chuyển sang feature.** Chạy FCI nhiều lần với thống kê CI bị nhiễu ngẫu nhiên, giữ các PAG còn lại, chứng nhận f nếu f đúng trên mọi PAG còn lại. Đây là đối thủ cùng target, có validity, cùng thông tin.
- Nếu R1 không vượt BL9 và BL1 (Bonferroni IUT) về power ở cùng validity, thì **STOP**.

**Quyết định cập nhật:** vẫn **REFORMULATE**, **bỏ HOLD FOR SOURCE**. Gate tiếp theo là **RG1 (chứng minh R1 pointwise + rank-aware)** và **RG2 (toy power: R1 so với BL1, BL2)**. Cả hai không cần MAG enumeration, nên rẻ. RG2 là kill test thực sự: nếu dependence-aware projection không có power hơn Bonferroni, toàn bộ hướng A′ nên dừng.
