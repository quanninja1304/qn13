# A′ — Day 2: Minimal toy mechanism validation & falsification

> Ngày: 2026-11-04. **Phạm vi: TOY ONLY**, theo authorization `TOY-WITH-CAVEATS` của `A1_mathematical_contract_v2.md` §9.
> **Không** có enumeration MAG, so sánh với ACI/BSC-D/FCI, hay pilot nhân quả.
> Mọi kết quả dưới đây đến từ một lần chạy thật:
> - Script: `A1_toy_mechanism_validation.py` (spec `v2-toy-1`).
> - Log: `A1_toy_run_log.txt`. Raw output: `A1_toy_outputs.json`.
> - Môi trường: Python 3.14.7, NumPy 2.5.2, SciPy 1.18.1, Windows 10. Runtime 312.3 s.
> - Seeds: calib 101, eval 202, data 303, ref 404. NMC = 20 000, NDATA = 4 000.
> - **192 assertion PASS, 0 FAIL.** Một kỳ vọng ban đầu sai ở bản quick-run được chuyển thành phát hiện (§2.4), **không** bị sửa để "pass".
>
> **Caveat bắt buộc** cho mọi bảng:
> - (i) working model z ~ N(ζ, Σ) với Σ chung cho mọi giả thuyết (giả định A3);
> - (ii) vùng R(m) là relaxation theo tọa độ (A4);
> - (iii) η, δ biết trước;
> - (iv) Q cố định;
> - (v) Experiment A và B **không** dùng dữ liệu nhân quả; Experiment C dùng dữ liệu Gaussian từ SCM 3 biến.
>
> Nhiều kết quả "full-Σ đúng mức danh nghĩa" là **tautological theo cấu trúc** của toy (đã ghi rõ bên dưới).

## 1. Spec đóng băng và thay đổi so với đề xuất gốc

| Mục | Đề xuất gốc ([GAP] Phần 2, [PLAN] P1a/P2) | Toy spec v2-toy-1 | Lý do |
|---|---|---|---|
| Score | D(f) dạng hiệu | D(f) **và** T(f) = dist²(z, R(M_¬f)) một phía | Contract §7 R1 |
| Weight | Σ̂⁻¹; pseudo-inverse cho trùng lặp | 5 quy ước: `inv`, `diag`, `pinv` (C-c), `support` (C-b), `ridge` (C-d) | Contract §2.4 |
| Diagonal control | "ACI weights \|log p − log α\|" | Loss kiểu ACI với weights a_k (4.1) | Contract P3: chỉ đây mới là reduction chính xác |
| Ngưỡng | Calibrate ở regime tham chiếu, giữ cố định ([PLAN] §3) | (a) transfer từ r = 0 (hoặc K = 1); (b) χ²_K | Để kiểm tra chính protocol của [PLAN] |
| Unit test T-P1 | D = +∞ | 0 < D < ∞ | CE4 |
| Solver | QP qua scipy | Liệt kê active set chính xác; đối chiếu độc lập bằng SLSQP multistart | Không tự kiểm chính mình |

## 2. Experiment A — Đại số tất định (minh họa toán học tại z cố định, *không* phải bằng chứng calibration)

**Phát biểu được kiểm tra, tiêu chí bác bỏ:**
- (4.2) đúng cho cả nhánh inactive và active;
- r = 0 cho full = diag;
- non-separability;
- P5 đúng dưới C-b;
- P7.

Bác bỏ nếu có bất kỳ sai lệch nào > 1e-9 so với công thức giải tích (hoặc > 1e-5 so với SLSQP).

### 2.1 Công thức (4.2) và P3

- **Lưới thử:** z ∈ {(2, 1.8), (−2, 1.8), (2, −1.8), (0.5, 2.5), (2.5, 0.5)}, r ∈ {0, ±0.3, ±0.6, ±0.9}, δ ∈ {1, 3}. Tổng cộng 70 tổ hợp, bao gồm cả nhánh active và inactive.
- **PASS toàn bộ** cho full-Σ so với (4.2), và diag so với z_2² − (δ − |z_2|)₊². Sai số < 1e-9.
- r = 0: full = diag chính xác (< 1e-12) ở cả 10 tổ hợp (z, δ).
- **Đổi dấu r hoặc z:** công thức vẫn đúng. Ví dụ (z = (2, 1.8), r = −0.6) cho t* = 3.0, rơi vào nhánh inactive với δ = 1. Hiệu ứng **không** chỉ do một ví dụ được chọn thuận lợi: dấu và độ lớn thay đổi đúng như (4.2) dự đoán.

### 2.2 Non-separability (r = 0.6, z_2 = 1.8, z_1 ∈ {−2, 0, 2})

Giá trị D_full thay đổi theo z_1 ở cả δ = 1 (một phần active) và δ = 3 (active). **PASS.** Xem `A1_toy_outputs.json → A.nonseparability`.

Đây là tính chất tổng quát của dạng toàn phương không chéo (contract §4-P4), **không** phải bằng chứng cho insight nhân quả.

### 2.3 Gần suy biến r → ±1 (δ = 1)

Giá trị nằm trong `A.near_singular`.
- Với z_1 ≠ z_2, D_full tăng không giới hạn khi r → 1. Ví dụ z = (2, 1.8): t* = z_2 − r z_1 → −0.2, nên |t*| < δ (active), và D ∝ 1/(1 − r²) với tử số âm, khiến D → −∞.
  Các giá trị đo được: D = −5.26, −32.2, −302, −3002 tại r = 0.9, 0.99, 0.999, 0.9999.
- **Với z_1 = z_2 = 2, D cũng phân kỳ:** D = −3.16, −48.2, −498, −4998. Lý do: t* = z_1(1 − r) → 0 rơi vào nhánh active, nên D ≈ −δ²/(1 − r²). Khi r → −1 với z = (2, 2), D → +∞ (79 996 tại r = −0.9999).
- **Erratum cho contract v2 §4-P5(iii):** câu "nếu z_1 = z_2 thì hiệu → 0" chỉ đúng trên nhánh inactive. Với δ > 0 cố định, nhánh inactive không bao giờ đạt được khi r → 1, nên **không có giới hạn hữu hạn ở cả hai trường hợp**.
- Số điều kiện của Σ đạt ~2·10⁴ ở r = 0.9999.

→ **D phân kỳ khi r → ±1 tại mọi z thử nghiệm.** Dấu phụ thuộc z và dấu của r. Xác nhận, và **mạnh hơn**, nhận định "không được claim liên tục".

### 2.4 Bản sao chính xác — **phát hiện mới**

| r | z | K = 2 full | K = 3 C-b (support) | K = 3 C-c (pinv) | K = 3 naive diag (đếm 2 lần) | K = 2 dedup diag |
|---|---|---|---|---|---|---|
| 0.0 | (2, 1.8) | 3.2400 | 3.2400 ✓ | 3.2400 | 6.48 | 3.24 |
| 0.0 | (0.5, 2.5) | 6.2500 | 6.2500 ✓ | 6.2500 | 12.50 | 6.25 |
| 0.6 | (2, 1.8) | **0.3125** | 0.3125 ✓ | **0.5625 ✗** | 6.48 | 3.24 |
| 0.6 | (0.5, 2.5) | 7.5625 | 7.5625 ✓ | 7.5625 | 12.50 | 6.25 |

(Cột dedup diag dùng weights đơn vị, nên ở r = 0.6 nó bằng điểm chéo của K = 2, không bằng full-Σ.)

- **P5 dưới C-b: PROVED và xác nhận số** (4/4).
- **Dưới C-c (seminorm), P5 SAI khi ràng buộc beta-min active.** Lý do: hướng null (0, 1, −1) cho phép z′_2 ≠ z′_3 thỏa |·| ≥ δ với chi phí 0, nên ràng buộc beta-min bị "lách". Đây là counterexample mới **CE8**: kết quả phụ thuộc quy ước pseudo-inverse **ngay cả với bản sao chính xác**.
- Naive additive đếm q_2 hai lần nên đổi D. Dedup control khôi phục giá trị K = 2. Duplicate invariance vì vậy **không phân biệt** A′ với "ACI + dedup".

### 2.5 Kiểm tra độc lập solver và P7

- Liệt kê active set khớp **SLSQP multistart** trên 25 instance ngẫu nhiên K = 3 (pattern, Σ, δ ngẫu nhiên). Sai số tương đối < 1e-5, **25/25 PASS**.
- P7: khoảng cách tới tập con ≥ khoảng cách tới toàn tập ở 200/200 instance.

## 3. Experiment B — Monte Carlo dưới working model (toy, *không* phải causal validation)

- Null: z ~ N(0, Σ_r), tức pattern đúng là (1,1) và f sai. "False assertion" là score > ngưỡng.
- Ngưỡng transfer được hiệu chỉnh ở r = 0 bằng seed 101, đánh giá bằng seed 202.
- SE Monte Carlo của FAR ≈ 0.0015 tại 5%.

**Khai báo trước:**
- Giả thuyết H-cal (theo [GAP] §1.2/[PLAN] §2): "FAR của diag trôi theo r; D_full thì không".
- Bác bỏ nếu D_full cũng trôi, hoặc diag không trôi.
- **Tautology:** T_full với ngưỡng χ²_K là χ²_K chính xác theo cấu trúc. Kết quả "T_full = 5%" **không** phải bằng chứng.

### 3.1 B1 — hai mô hình khác nhau ở **1** tọa độ (cấu hình ví dụ P4)

| δ | r | FAR D_full (transfer) | FAR D_diag (transfer) | FAR T_full (χ²₂) | FAR T_diag (χ²₂) | Kendall τ(D_full, D_diag) |
|---|---|---|---|---|---|---|
| 1.5 | 0 | 0.052 | 0.052 | 0.052 | 0.052 | 1.000 |
| 1.5 | 0.6 | 0.049 | 0.049 | 0.052 | 0.063 | 0.333 |
| 1.5 | 0.9 | 0.024 | **0.049** | 0.052 | 0.080 | 0.054 |
| 3.0 | 0.6 | 0.025 | **0.049** | 0.052 | 0.063 | 0.333 |
| 3.0 | 0.9 | 0.0003 | **0.049** | 0.052 | 0.080 | 0.054 |
| 3.0 | −0.6 | 0.025 | 0.049 | 0.052 | 0.063 | 0.336 |

**Kết luận B1:**
- **D_diag KHÔNG bị miscalibrated** trong cấu hình P4: FAR = 0.048–0.049 ở mọi r. Điều này xác nhận CE3, tức z_2² ~ χ²_1 chính xác.
- Full-Σ trở nên **bảo thủ hơn**, không "chính xác hơn".
- Thứ hạng giữa hai score gần như **không tương quan** ở r = 0.9 (τ = 0.054). Dependence làm thay đổi **thứ tự** mạnh, nhưng toy không nói thứ tự nào tốt hơn, vì ở đây không có alternative.

### 3.2 B2 — hai mô hình khác nhau ở **2** tọa độ tương quan (đếm trùng thật)

| δ | r | FAR D_full (transfer) | FAR D_diag (transfer) | FAR T_full (χ²₂) | FAR T_diag (χ²₂) |
|---|---|---|---|---|---|
| 1.5 | 0.6 | 0.049 | 0.071 | 0.052 | 0.063 |
| 1.5 | 0.9 | **0.049** | **0.092** | 0.052 | 0.080 |
| 3.0 | 0.6 | **0.074** | 0.078 | 0.052 | 0.063 |
| 3.0 | 0.9 | **0.110** | **0.105** | 0.052 | 0.080 |
| 3.0 | −0.6 | 0.074 | 0.078 | 0.052 | 0.063 |

**Kết luận B2:**
- **Với δ = 1.5:** H-cal đúng trong toy. Diag trôi 0.049 → 0.092; D_full giữ 0.049.
- **Với δ = 3.0: H-cal bị BÁC BỎ cho score dạng hiệu D.** D_full trôi gần như diag (0.110 so với 0.105). Lý do: phân phối null của D phụ thuộc r qua số hạng phía M_f (khoảng cách tới vùng dependent). Ngưỡng transfer do đó không còn bất biến.
- **Chỉ score một phía T với ngưỡng χ²** giữ mức danh nghĩa. Điều này **tautological**.
- Đây là bằng chứng số cho blocker B2 (D không calibrated) và ủng hộ reformulation R1.

### 3.3 B3 — mức dư thừa K (equicorrelated), protocol [PLAN] §3 (ngưỡng chuyển từ K = 1, r = 0)

| K | r | FAR T_full (transfer) | FAR T_diag (transfer) | FAR T_full (χ²_K) | FAR T_diag (χ²_K) |
|---|---|---|---|---|---|
| 1 | 0 | 0.049 | 0.049 | 0.049 | 0.049 |
| 2 | 0.9 | 0.144 | 0.158 | 0.050 | 0.082 |
| 4 | 0.9 | **0.432** | 0.336 | 0.052 | 0.119 |
| 8 | 0 | 0.871 | 0.871 | 0.049 | 0.049 |
| 8 | 0.9 | **0.871** | **0.509** | 0.049 | 0.156 |

**Kết luận B3 (quan trọng cho thiết kế pilot):**
- Dưới protocol "hiệu chỉnh ngưỡng ở regime minimal-Q rồi giữ cố định" của [PLAN] §3, **full-Σ trôi MẠNH HƠN diag** khi thêm query: 0.871 so với 0.509 ở K = 8, r = 0.9.
- Lý do: T_full ~ χ²_K, phụ thuộc K, không phụ thuộc r. Còn diag với r cao co lại gần một biến χ²_1 nhân hệ số.
- Chỉ ngưỡng **phụ thuộc rank** (χ²_K) mới calibrated cho full-Σ.
- Metric Δ_FAR trong [PLAN] §3 vì vậy **không đo được điều nó muốn đo**: nó sẽ phạt chính phương pháp đúng. **Pre-registration §3 phải được viết lại** trước mọi pilot.

### 3.4 B4 — Σ̂ ước lượng (Wishart(ν, Σ)/ν, thay thế cho sai số ước lượng; K = 8, r = 0.9)

| ν | 20 | 50 | 200 | 1000 | oracle |
|---|---|---|---|---|---|
| FAR T_full (χ²₈) | **0.337** | **0.132** | 0.063 | 0.051 | 0.045 |
| median cond(Σ̂) | 313 | 155 | 102 | 84 | 73 |

**Kết luận B4:** khi Σ̂ nhiễu (ν ≤ 50, ví dụ bootstrap ít replicate hoặc K lớn so với số mẫu hiệu dụng), full-Σ trở nên **anti-conservative rõ rệt**. Đây là regime mà full-Σ **tệ hơn** diag về calibration (T_diag ở K = 8, r = 0.9 là 0.156 với oracle). Nó có liên quan trực tiếp tới arm nonparametric (H-gen), nơi Σ̂ bắt buộc phải lấy từ bootstrap.

## 4. Experiment C — Dữ liệu Gaussian, rank, first-order duplicate, evidence ngầm

### 4.1 C1 — Rank (CE1), p = 3, K = 6 query bậc ≤ 1

| R | n | 3 trị riêng nhỏ của cov MC của z | n × trị riêng nhỏ | 3 trị riêng lớn | sai lệch tương đối MC so với delta |
|---|---|---|---|---|---|
| empty | 200 | 0.0023, 0.0024, 0.0026 | 0.45–0.51 | 1.89–2.03 | 3.0% |
| empty | 5000 | ≈ 1e-4 | 0.51–0.57 | 1.97–2.09 | 3.4% |
| generic | 200 | 0.0017–0.0020 | 0.33–0.40 | 1.90–2.05 | 3.5% |
| generic | 5000 | ≈ 1e-4 | 0.37–0.44 | 1.94–2.11 | 3.2% |

- Delta method cho **rank 3 chính xác** ở cả hai R (PASS).
- Cov mẫu hữu hạn thật **là PD**, nhưng có 3 trị riêng **O(1/n)** (n·λ ổn định ≈ 0.3–0.6).
- Công thức delta method tự cài khớp Monte Carlo trong khoảng 3–3.5% (đúng cỡ nhiễu MC với 4 000 replicate). Đây là kiểm chứng thay thế cho Olkin–Finn, vốn chưa đọc được.

→ **Xác nhận B1:** Σ̂ dùng nghịch đảo sẽ khuếch đại các hướng có phương sai O(1/n) lên hệ số ~n.

### 4.2 C2 — First-order duplicate (CE2): X→Z (ρ = a), Y cô lập; Q = {X⊥Y, X⊥Y|Z}; pattern đúng (1,1)

FAR ở đây là tỷ lệ **bác bỏ nhầm mô hình đúng** ở ngưỡng χ²_{rank}.

| a | n | r MC | r lý thuyết √(1−a²) | C-b support: tỷ lệ +∞ | C-c pinv FAR | C-d ridge λ = 1e-3 / 1e-4 FAR | plug-in Σ̂ FAR (χ²₂) | cond(Σ̂) median |
|---|---|---|---|---|---|---|---|---|
| 0 | 200 | 0.9976 | 1 | **1.00** | 0.053 | **0.238 / 0.541** | 0.018 | 580 |
| 0 | 1000 | 0.9995 | 1 | **1.00** | 0.045 | 0.085 / **0.312** | 0.014 | 2888 |
| 0.3 | 200 | 0.9521 | 0.9539 | 0 | 0.061 | — | 0.036 | 40 |
| 0.6 | 1000 | 0.8022 | 0.8000 | 0 | 0.059 | — | 0.058 | 9.0 |
| 0.9 | 1000 | 0.4390 | 0.4359 | 0 | 0.052 | — | 0.051 | 2.5 |

- r = √(1−a²) **xác nhận** bằng mô phỏng (PASS ở 6/6 tổ hợp với a > 0, sai lệch < 0.03).
- **CE2 xác nhận:** dưới quy ước support C-b của P5 gốc, **mô hình đúng bị gán khoảng cách +∞ ở 100% replicate**.
- Ridge với λ nhỏ cho FAR tới 54%: **kết quả do quy ước quyết định**.
- Plug-in Σ̂ gần điểm suy biến là bảo thủ (FAR 1.4–1.8%), với số điều kiện ~10³. Tức calibration thay đổi theo vị trí so với điểm suy biến.

### 4.3 C3 — Mệnh đề E (evidence ngoài Q), a = 0.6

| n | 200 | 1000 | 5000 |
|---|---|---|---|
| corr((z₂ − r z₁)/√(1−r²), z_{YZ\|X}) | −0.9955 | −0.9991 | −0.9998 |

**Xác nhận (4.3):** phần "dependence-aware" mà full-Σ trích ra để phân biệt m_a (X→Z, Y cô lập) với m_b (X→Z←Y) **chính là thống kê của query Y⊥Z|X, không có trong Q**.

Hệ quả: một ACI chỉ cần thêm Y⊥Z|X vào Q sẽ nhận được cùng thông tin. Lợi thế của D so với ACI "cùng Q" có thể chỉ là lợi thế **thông tin**, không phải lợi thế **xử lý dependence**. Control bắt buộc: **ACI trên Q-closure** (R4).

### 4.4 C4 — Realizability và tính không đơn điệu của CI

- **Collider X→Z←Y** (hệ số 0.6, 0.5): ρ_{XY} = 0 (sai số máy) và ρ_{XY·Z} ≠ 0 (|·| > 0.1). Pattern (1,0) **khả thi** (PASS).
- Thêm Z vào tập điều kiện **phá** độc lập. Do đó "conditioning set dư thừa" không bảo toàn CI. Không được giả định CI đơn điệu theo tập điều kiện.
- Σ_z dưới m_b khác Σ_z dưới m_a (`C4_realizability` trong JSON). Giả định Σ chung (A3) là **xấp xỉ**.

## 5. Experiment E — Nhạy cảm theo beta-min η (working model, K = 2, r = 0.5)

Hiệu ứng thật trên q_2: atanh ρ = 0.1. f đúng (pattern (1,0)).

| n | η = 0.05 | 0.10 | 0.15 | 0.20 | 0.30 |
|---|---|---|---|---|---|
| 200: P(D < 0) (sai dấu) | 0.085 | 0.203 | 0.342 | 0.495 | **0.792** |
| 1000 | 0.004 | 0.038 | 0.182 | 0.493 | **0.966** |
| 5000 | 0.000 | 0.000 | 0.023 | 0.498 | **1.000** |
| 5000: mean D | 67.5 | 67.0 | 49.8 | −0.3 | **−200.2** |

**Kết luận E:**
- Khi η ≤ hiệu ứng thật, D nhất quán (P2).
- Khi η = 2 × hiệu ứng, D là tung đồng xu **ở mọi n**.
- Khi η > 2 × hiệu ứng, D **sai dấu với xác suất → 1 và độ tự tin tăng tuyến tính theo n** (mean D = −200 ở n = 5000).

η là tham số không kiểm định được (contract §1.6), và nó quyết định kết luận. Điều này xác nhận CE6/B3. Reformulation R2 (η-profile) biến chính sự phụ thuộc này thành output báo cáo.

## 6. Ledger: phát biểu → kết quả

| Phát biểu | Kết quả toy | Tautological? | Còn chưa kiểm tra |
|---|---|---|---|
| (4.2) inactive + active; P3 diag; r = 0 trùng | **Xác nhận** | Không: công thức độc lập, đối chiếu SLSQP | K tổng quát |
| Non-separability | Xác nhận | Gần như (tính chất dạng toàn phương) | — |
| P5 dưới C-b | Xác nhận | Không | — |
| P5 dưới C-c | **Bác bỏ** (CE8) | Không | — |
| H-cal "diag trôi, D_full không" | **Hỗn hợp**: đúng ở B2 với δ = 1.5; **sai** ở B2 với δ = 3; **sai tiền đề** ở B1 (diag không trôi) | Phần "T_full đúng" là tautological | Toàn bộ trong causal SCM |
| Protocol Δ_FAR ([PLAN] §3) đo đúng H-cal | **Bác bỏ** (B3: full trôi mạnh hơn) | Không | — |
| Full-Σ không tệ hơn diag | **Bác bỏ** khi Σ̂ nhiễu (B4) | Không | Bootstrap Σ̂ GCM |
| Σ PD (A1-b) | **Bác bỏ** (C1, C2) | Không | — |
| Mệnh đề E | **Xác nhận** | Không | Đồ thị lớn hơn |
| η-sensitivity: sai tự tin khi η misspecified | **Xác nhận** | Một phần (do cấu trúc) | — |

## 7. Quyết định Day 2: **MIXED / REFORMULATION NEEDED**

- Các đồng nhất thức đại số đã được sửa đều đúng. Hành vi phi tầm thường **có thấy được**: thứ hạng thay đổi mạnh, và có miscalibration diag ở cấu hình đếm trùng thật.
- Nhưng toy cũng cho thấy:
  - (i) score dạng hiệu D **không** giữ calibration (B2, δ = 3);
  - (ii) protocol pre-registration hiện tại phạt phương pháp đúng (B3);
  - (iii) full-Σ tệ hơn khi Σ̂ nhiễu (B4);
  - (iv) quy ước pseudo-inverse quyết định kết quả (CE2, CE8);
  - (v) lợi ích có thể chỉ là thông tin ngoài Q (Mệnh đề E);
  - (vi) η quyết định dấu (E).
- **Không** được đọc là MECHANISM VALIDATED.
- **Không** phê duyệt pilot đầy đủ.

### Bằng chứng tối thiểu cần có trước bất kỳ claim novelty nào (từ causal SCM và baseline gần nhất)

1. **H-prev:** phân bố tương quan off-diagonal giữa các query **cùng xuất hiện trong một suy luận phân biệt feature**, trên query universe cố định trước. Gaussian: tính được **giải tích** qua delta method (C1 đã kiểm chứng công thức), không cần mô phỏng lớn.
2. **Số lượng và tỷ lệ cặp "first-order duplicate"** (r tiệm cận ≈ 1) trong Q thực tế. Nếu lớn, B1 chi phối mọi kết quả.
3. So sánh **cùng thông tin**: T_full (R1) với ACI-type diag trên **Q-closure** (R4). Nếu lợi ích biến mất, đóng góp chỉ là "thêm query".
4. So sánh với **forced-feature Gaussian likelihood (B4 của [PLAN])** ở Gaussian arm, vì Mệnh đề E và R3 cho thấy D là xấp xỉ của nó.
5. Ở arm nonparametric: **độ ổn định của Σ̂ bootstrap** (B4 toy cho thấy ν ≤ 50 đã hỏng) trước khi đo bất cứ thứ gì khác.
