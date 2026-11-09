# A′ — Mathematical contract v2 (Day 1: Independent Mathematical Audit)

> Ngày: **2026-11-04**. Người thực hiện: agent review độc lập (phiên mới, không kế thừa kết luận cũ).
> Phạm vi: audit toán học của đề xuất A′ (*dependence-aware causal feature scoring*). **Không** implement solver, **không** benchmark.
> Tài liệu gốc được giữ nguyên: `reports/reassessment_2026-11-03_vi/A1_gap_confirmation_and_proof_sketch_vi.md` (gọi tắt **[GAP]**), `A1_next_steps_plan_vi.md` (**[PLAN]**), `topic_cards/A1_dependence_aware_feature_confidence_vi.md` (**[CARD]**), `00_final_reassessment_vi.md`.
> Nhãn: **[Source-verified]** đã đọc trong phiên này từ PDF trong `docs/papers/` (trích text bằng PyMuPDF); **[Derived]** tự suy ra trong phiên này, có kiểm tra số; **[Inference]** suy luận chưa kiểm chứng đầy đủ; **[Hypothesis]**; **[UNVERIFIED]** nguồn không có trong repo hoặc chưa đọc; **[Open]**.
> Kiểm tra số cho Day 1: `C:\Users\ADMIN\.claude\jobs\a0a25a18\tmp\chk\d1check.py` (tạm). Bản tái lập chính thức nằm trong script Day 2 (`A1_toy_mechanism_validation.py`).

---

## 0. Executive verdict

1. **Phần đại số lõi phần lớn đúng nhưng thu hẹp hơn tuyên bố.** P1, P2, P5, P6, P7 đúng *dưới giả định đã ghi*. P3 đúng như một reduction về **loss kiểu ACI**, nhưng **sai** nếu hiểu là trùng với ACI đã công bố (weights Eq. 14/15, ngưỡng α). Công thức P4 đúng; diễn giải "đếm trùng" **không khớp** với chính ví dụ của P4.
2. **Blocker toán học mới (B1, nghiêm trọng): giả định (A1) "Σ xác định dương trên các query không trùng" là sai cho Fisher-z Gaussian.** [Derived + kiểm tra số] Mọi Fisher-z là hàm của ma trận tương quan, nên rank của Σ tiệm cận không vượt quá p(p−1)/2. Ví dụ: p = 3 với cả 6 query bậc ≤ 1 cho rank Σ = 3. Thêm nữa, cặp "gần trùng" như X⊥Y và X⊥Y|Z với Z độc lập có **tương quan tiệm cận đúng bằng 1**, dù hai thống kê khác nhau ở n hữu hạn. Đây chính là regime mà A′ lấy làm động lực. Ở đó, quy ước pseudo-inverse có support constraint (P5) cho **dist = +∞ với chính mô hình đúng**.
3. **Score D(f) dạng hiệu không có diễn giải "confidence".** Hai giả thuyết không lồng nhau, là hợp không lồi, và dùng Σ chung cho mọi giả thuyết. Ngoài ra kết quả phụ thuộc quyết định vào **beta-min η đã biết**: không có η thì mọi mô hình ít độc lập hơn luôn khớp ít nhất bằng nhau. **Sửa tối thiểu có cơ sở:** score một phía dist²(z, R(M_¬f)), cùng ngưỡng projection của confidence ellipsoid hoặc nguyên lý intersection–union. Score này **valid (conservative) dưới working model với Q cố định và η đã biết**. Tuy vậy đây là thủ tục cổ điển, không phải cơ chế mới.
4. **Novelty đã yếu đi thêm.** Ở arm Gaussian, khi xử lý đúng rank, D(f) tiệm cận một kiểm định **minimum-distance trong không gian tương quan**. Đó là họ hàng của full-likelihood baseline B4, không phải đối thủ độc lập. Ví dụ P4 khả thi minh họa điều này: "evidence dependence-aware" mà D trích ra **bằng (bậc một) Fisher-z của một query không nằm trong Q** (Y⊥Z|X).
5. **Day 2 authorization: `TOY-WITH-CAVEATS`.** Chỉ cho phép kiểm tra đại số/số học các thành phần ghi ở §9, cùng các counterexample. **Không** cho phép so sánh hiệu năng, claim calibration hay pilot nhân quả.

---

## 1. Reconstructed contract (tái dựng độc lập)

### 1.1 Notation table

| Ký hiệu | Ý nghĩa | Kích thước / đơn vị | Ghi chú quantifier |
|---|---|---|---|
| V, p = \|V\| | biến quan sát | — | cố định |
| P | phân phối quan sát (marginal của SCM có latent/selection) | — | cố định, không phụ thuộc n (trừ khi ghi rõ) |
| M | họ mô hình hữu hạn (MAG trên V, có thể giới hạn) | \|M\| hữu hạn | cố định trước dữ liệu |
| m* ∈ M | MAG đúng (latent projection của DAG đúng) | — | **giả định** m* ∈ M |
| Q = {q_1..q_K}, q_k = (X_k ⊥ Y_k \| S_k) | query universe | K | **phải cố định trước dữ liệu** (xem §2.5) |
| π(m) ∈ {0,1}^K | π_k(m) = 1 ⇔ X_k, Y_k m-separated bởi S_k trong m | — | tất định |
| ρ_k | partial correlation tổng thể của q_k | không đơn vị, ∈ (−1,1) | |
| z_k = √(n−\|S_k\|−3)·atanh ρ̂_k | Fisher-z mẫu | O_p(1) dưới H0; O(√n) dưới H1 | |
| ζ_{n,k} = √(n−\|S_k\|−3)·atanh ρ_k | "population counterpart" | O(√n) | E z_k = ζ_{n,k} + O(n^{-1/2}) |
| Σ | cov tiệm cận của z − ζ_n | K×K, O(1) | **phụ thuộc P**, không phụ thuộc mô hình giả thuyết (giả định working model) |
| Σ̂ | ước lượng Σ (delta-method plug-in hoặc bootstrap) | K×K | |
| η | beta-min: π_k(m*) = 0 ⇒ \|atanh ρ_k\| ≥ η | không đơn vị | **phải biết trước** |
| δ_{n,k} = √(n−\|S_k\|−3)·η | ngưỡng tách | O(√n) | |
| R_n(m) | vùng tương thích theo tọa độ (Eq. 1.1) | ⊂ R^K | |
| A_n(m) | **tập attainable thật**: {ζ_n(P′) : P′ Gaussian Markov với m, faithful theo π(m), thỏa beta-min η} | ⊂ R^K | khác R_n(m), xem §1.4 |
| f, M_f, M_¬f | feature (ở đây: ancestral X ∈ An(Y) trong m), và hai tập con | — | |
| ‖v‖_W² = vᵀW⁻¹v | chuẩn Mahalanobis | đơn vị χ² | cần W PD; nếu không, xem §2.4 |
| D_W(f) | Eq. 1.3 | đơn vị χ² | |

### 1.2 Target output và truth

- **Target:** feature f là hàm của MAG (ancestral relation; endpoint feature **hoãn**, vì thiếu Zhang 2008 [UNVERIFIED]). Truth của f là f(m*).
- **Identifiability:** f gọi là *Q-identifiable trong M* nếu ∀m ∈ M: π(m) = π(m*) ⇒ m ⊨ f. Khái niệm này **tương đối với (Q, M)**, không phải identifiability từ toàn bộ phân phối. Một feature có thể không Q-identifiable nhưng vẫn identifiable từ P, ví dụ khi Q thiếu một test then chốt. Khi đó output đúng là "không quyết định", tương tự ACI Thm 1 với C(f) = 0 [Source-verified: ACI_2016.pdf tr. 5].

### 1.3 Vùng và score (theo [GAP] Phần 2, viết lại tường minh)

(1.1)  R_n(m) = { z′ ∈ R^K : z′_k = 0 nếu π_k(m) = 1;  |z′_k| ≥ δ_{n,k} nếu π_k(m) = 0 }

(1.2)  d_W(z; M′) = inf_{m∈M′} inf_{z′∈R_n(m)} ‖z − z′‖_W,   với inf ∅ = +∞

(1.3)  D_W(f) = d_W(z; M_¬f)² − d_W(z; M_f)²   (score dạng hiệu, song song ACI Eq. 16)

(1.4)  T_W(f) = d_W(z; M_¬f)²   (score một phía; **đề xuất thay thế**, §7)

**Trường hợp biên** [Derived]:
- M_¬f = ∅ ⇒ D = +∞.
- M_f = ∅ ⇒ D = −∞.
- Cả hai rỗng: M rỗng, ngoài contract.
- Nếu cả hai khoảng cách đều = +∞ (có thể xảy ra dưới quy ước support, §2.4) thì D = ∞ − ∞, **không xác định**. Output phải là "undefined", **không** được ép về 0.

### 1.4 Attainable set vs R_n(m) — **relaxation, không phải equality**

[Derived] A_n(m) ⊆ R_n(m): mọi phân phối Markov và faithful với m, thỏa beta-min, cho ζ_n ∈ R_n(m). Bao hàm này **thực sự chặt** (⊊) vì hai lý do:
- (a) **Số chiều.** Với Gaussian, ζ_n là hàm trơn của p(p−1)/2 tương quan. Khi K > p(p−1)/2, A_n(m) nằm trên một đa tạp có chiều ≤ p(p−1)/2 − (#ràng buộc), còn R_n(m) có chiều K − #indep.
- (b) **Ràng buộc đại số giữa các tọa độ dependent.** Ví dụ: ρ_{XY} và ρ_{XY·Z} không độc lập về đại số, vì ρ_{XY·Z} = (ρ_{XY} − ρ_{XZ}ρ_{YZ}) / √((1−ρ_{XZ}²)(1−ρ_{YZ}²)).

**Hệ quả:**
- Với score một phía (1.4), relaxation chỉ làm **mất power**: khoảng cách tới tập lớn hơn thì nhỏ hơn, nên khó assert f hơn. **Validity được giữ** (§7).
- Với score dạng hiệu (1.3), relaxation giảm **cả hai** khoảng cách, nên **dấu sai lệch của D không xác định**. Không thể nói D "conservative" hay "anti-conservative".
- Có **≥ 2 diễn giải** nên phải nêu rõ: (I-a) R_n là working-model relaxation, tức dùng như ACI dùng logic trên pattern; (I-b) R_n được thay bằng A_n, tức gần với Gaussian MAG likelihood thật (RICF). Mọi claim "GLR" (P6) chỉ đúng cho (I-a).

### 1.5 Loss/score

- **D (1.3):** chênh lệch hai bình phương khoảng cách. Đây là GLR trên working model (P6). Nó **không** phải log-odds, p-value hay posterior.
- **T (1.4):** thống kê kiểm định cho H_¬f : ζ ∈ R_n(M_¬f).
- [Derived] Hai score **không tương đương về thứ tự**: D trừ thêm d(M_f)², là đại lượng biến thiên theo feature.

### 1.6 Vai trò của η

- **η không phải faithfulness.** Faithfulness chỉ yêu cầu ρ_k ≠ 0 khi π_k(m*) = 0. Beta-min yêu cầu |atanh ρ_k| ≥ η > 0 **với η biết trước và đồng đều** (dạng *strong faithfulness*).
- **Khi η → 0** [Derived]: δ_{n,k} → 0, nên bao đóng của {|z′_k| ≥ δ} tiến tới R. Khi đó khoảng cách tới một mô hình có tập độc lập là con của mô hình khác luôn ≤ khoảng cách tới mô hình kia. Mô hình đầy đủ (complete MAG, không có độc lập nào) có dist = 0 với mọi z. Do đó, nếu cả M_f và M_¬f cùng chứa một mô hình đầy đủ (ví dụ X→Y và Y→X trong đồ thị đầy đủ), thì D → 0 với mọi dữ liệu. **η thay thế cho penalty độ phức tạp** (vai trò của α trong ACI hay penalty của BIC). Không có η, score suy biến.
- **Không kiểm định được.** Với kiểm định CI tổng quát, không thể kiểm tra một ngưỡng η từ dữ liệu một cách đồng đều [Source-verified: Shah & Peters, arXiv v. 25-03-2022, Theorem 2 "No-free-lunch", tr. 7]. Kết quả bất khả thi về uniform consistency trong causal inference (Robins–Scheines–Spirtes–Wasserman 2003) là nền tảng tương tự [UNVERIFIED trong phiên: không có PDF].

---

## 2. Assumption ledger và failure modes

| ID | Giả định | Cần cho | Trạng thái | Ghi chú |
|---|---|---|---|---|
| A0 | m* ∈ M; M hữu hạn, cố định | P1, P2 | Giả định thiết kế | Khi M bị giới hạn (theo skeleton…), A0 có thể sai |
| A1-a | z − ζ_n ⇒ N(0, Σ) đồng thời, Q cố định | P2, P6 | Đúng cho Fisher-z Gaussian (delta method trên S) [Inference chuẩn] | **Không** tự động đúng khi Q chọn thích nghi (§2.5) |
| A1-b | **Σ PD** | P2 (λ bị chặn), P4, Σ⁻¹ | **SAI tổng quát** [Derived, §2.4] | Blocker B1 |
| A1-c | Σ̂ → Σ | P2 | Đúng nếu Σ PD; nếu Σ suy biến, Σ̂⁻¹ không hội tụ | |
| A2-a | faithfulness trên Q | P1 | Giả định chuẩn | |
| A2-b | beta-min với **η đã biết** | P1, P2, mọi validity | Mạnh, không kiểm định được | Blocker B3 |
| A3 | Σ giống nhau dưới mọi giả thuyết (working model) | P6 | Relaxation: cov thật phụ thuộc P, khác nhau giữa các m | Ảnh hưởng calibration bậc hai |
| A4 | R_n(m) thay A_n(m) | mọi score | Relaxation (§1.4) | |

### 2.1 Model identifiability — thử chứng minh và phản ví dụ

- [Derived] Nếu f không Q-identifiable thì tồn tại m_1 ∈ M_f, m_2 ∈ M_¬f với π(m_1) = π(m_2) = π(m*). Khi đó R_n(m_1) = R_n(m_2), suy ra d(M_f) = d(M_¬f) và D = 0 **với mọi z**, không chỉ ở oracle. Score phân biệt được các feature không Q-identifiable là **không thể**. Đây là tính chất đúng mong muốn, **không phải** failure.
- **Phản ví dụ cho "Q-identifiable ⇔ identifiable":** p = 3, M = {m_1: X→Z←Y, m_2: X→Z→Y}, Q = {X⊥Z}. Cả hai mô hình cho π = 0 (X, Z kề nhau). Feature "Y ∈ An(Z)" đúng trong m_1 và sai trong m_2, nên **không Q-identifiable**. Thêm X⊥Y vào Q thì π(m_1) = (0,1) ≠ π(m_2) = (0,0), và feature trở thành identifiable. **Ý nghĩa:** kết quả chỉ có nghĩa tương đối với Q đã chọn. "Thêm query" thay đổi tập feature quyết định được. Vì thế so sánh ACI với D phải **cùng Q** (xem thêm §4-P4: D ngầm dùng thông tin ngoài Q).

### 2.2 Statistical realizability

- [Derived] R_n(m) chứa vector **không thể đạt được** bởi bất kỳ phân phối Gaussian nào. Ví dụ p = 3, Q = 6 query bậc ≤ 1, m = đồ thị đầy đủ (π ≡ 0). R_n(m) chứa z′ = δ·(1, −1, 1, −1, 1, −1). Vector này yêu cầu ρ_{XY} và ρ_{XY·Z} ngược dấu với cùng độ lớn tiệm cận, đồng thời cho cả ba cặp, với chỉ 3 tham số tương quan. Nó **vi phạm ràng buộc PD** khi độ lớn đủ lớn. Lý do tổng quát: dim R_n(m) = K = 6 > 3 = số tham số.
- **Kết luận:** R_n là **working-model relaxation tiện lợi**, không phải tập tham số MAG chính xác. Mọi claim "likelihood" phải nói "likelihood của working model z ~ N(ζ, Σ), ζ ∈ R_n".

### 2.3 Beta-min — xem §1.6

- **Cần cho P1?** Có. Nếu một dependence thật có |atanh ρ_k| < η, thì ζ_n ∉ R_n(m*), và Bổ đề của P1 hỏng.
- **Phản ví dụ khi η bị misspecify** [Derived]: giả sử dependence thật có |atanh ρ_k| = η/2. Khi đó dist(ζ_n, R_n(m*)) ≥ λ_max^{−1/2} · √n · η/2. Mô hình đúng bị **loại với độ tự tin tăng theo n**. Nếu feature đúng chỉ nhận được từ m*, thì D → −∞: **sai và tự tin tăng dần**. ACI có rủi ro tương tự với α cố định, nhưng hành vi tiệm cận khác.
- **Ý nghĩa với GCM:** β-min cho GCM là điều kiện trên E[Cov(X,Y|S)], không phải trên "dependence". [Source-verified: Shah & Peters tr. 11, §3.1.1: "does not necessarily need to be non-zero under an alternative"]. Như vậy "π_k = 0 ⇒ |ζ_k| ≥ δ" là một **giả định faithfulness riêng cho GCM**, mạnh hơn faithfulness thông thường.

### 2.4 Covariance: PD, suy biến, ước lượng — **Blocker B1**

**Mệnh đề R (rank bound)** [Derived, kiểm tra số]. Với dữ liệu Gaussian, mọi Fisher-z z_k là hàm trơn g_k của ma trận tương quan mẫu R̂ (vì partial correlation bất biến theo scale). Theo delta method, √n(vec R̂ − vec R) ⇒ N(0, Γ) với Γ có kích thước d × d, d = p(p−1)/2. Khi đó Σ = J Γ Jᵀ với J = ∂g/∂ρ ∈ R^{K×d}. Suy ra **rank Σ ≤ min(K, d)**.

Kiểm tra số (delta method với công thức cov tiệm cận của tương quan Pearson; công thức tự cài đặt, sẽ được đối chiếu Monte Carlo ở Day 2):
- p = 3, K = 6 (mọi query bậc ≤ 1), ở 3 ma trận tương quan khác nhau (đồ thị rỗng, X→Z với a = 0.6, tổng quát): trị riêng của Σ = (0, 0, 0, ≈2, ≈2, ≈2), tức **rank 3** trong cả 3 trường hợp.

**Mệnh đề R′ (first-order duplicate)** [Derived, kiểm tra số]. Xét Q = {X⊥Y, X⊥Y|Z} tại tương quan ρ_{XY} = ρ_{YZ} = 0, ρ_{XZ} = a. Khi đó

(2.1)  Σ = [[1, r], [r, 1]],   r = √(1 − a²).

Kiểm tra số: a ∈ {0, 0.3, 0.6, 0.9} cho r ∈ {1, 0.9539, 0.8, 0.4359}, khớp chính xác.
- Tại **a = 0** (Z độc lập với X, Y): r = 1, nên Σ suy biến. Nhưng z_1 ≠ z_2 ở n hữu hạn, vì khác hệ số √(n−3) so với √(n−4), và khác ở số hạng bậc hai ρ̂_{XZ}ρ̂_{YZ}.
- Vì vậy z ∉ z_0 + range(Σ) với z_0 = 0 (vùng của mô hình đúng). Dưới **quy ước support của P5** (‖v‖ = +∞ nếu v ∉ range Σ), ta có **dist(z, R(m*)) = +∞ với chính mô hình đúng, xác suất 1**.

**Bốn quy ước và hệ quả:**

| Quy ước | Định nghĩa | Hệ quả |
|---|---|---|
| C-a: chỉ cho phép Q với Σ PD | Lọc Q | Loại đúng regime A′ muốn nhắm tới (near-duplicates); với Gaussian buộc K ≤ p(p−1)/2 |
| C-b: Σ⁺ + support constraint (P5) | +∞ nếu ngoài range | Phản ví dụ R′: true model có dist +∞; D có thể là ∞ − ∞ |
| C-c: Σ⁺ không support | seminorm | Thành phần ngoài range bị bỏ qua. Bước (b) trong chứng minh P2 (chặn dưới qua λ_max) **không còn đúng** nếu hướng tách mô hình nằm trong null space |
| C-d: shrinkage Σ̂ + λI | PD giả tạo | D phụ thuộc λ. Khi λ → 0, thành phần ngoài range được chia cho λ, nên D bùng nổ. Kết quả do quy ước quyết định, không do dữ liệu |

**Bootstrap Σ̂.** Covariance mẫu hữu hạn thật của z là PD, vì các khác biệt bậc hai là O(n^{−1/2}). Bootstrap sẽ ước lượng các trị riêng nhỏ cỡ O(1/n). Σ̂⁻¹ khi đó **khuếch đại** các khác biệt bậc hai. Score bị chi phối bởi các hướng mà lý thuyết bậc một coi là không có thông tin. [Inference; Day 2 kiểm tra.]

**Kết luận B1:** "near-duplicate queries" (động lực của A′, [CARD] "Reproducible failure") **chính là** regime Σ suy biến tiệm cận. Hành vi của D ở đó do quy ước pseudo-inverse/shrinkage quyết định. Đây là **REFORMULABLE**: tham số hóa lại trong không gian tương quan (d chiều) thay vì không gian query (K chiều). Nhưng cách sửa đó biến D thành **kiểm định minimum-distance cho cấu trúc tương quan**, tức một họ phương pháp cổ điển (Browne-type GLS/ADF cho covariance structures [UNVERIFIED: không có nguồn trong repo]). Arm Gaussian vì vậy không còn là "arm kiểm chứng độc lập".

### 2.5 Adaptive querying

- [Derived/Inference] Nếu Q do FCI chọn trên cùng dữ liệu, thì Q = Q(z_full) là biến ngẫu nhiên. Phân phối của z_Q **điều kiện trên sự kiện chọn** không còn là N(ζ, Σ). Guo–Wu–Yiu chứng minh sự kiện chọn của FCI là đa diện trong không gian Fisher-z [Source-verified: Guo_Wu_Yiu_2026, Theorem 1, tr. 4–5]. Nghĩa là z bị truncate.
- Mọi claim P2/P6 **chỉ áp dụng cho Q cố định trước**. Ba cách hợp lệ:
  - (i) Q cố định, ví dụ mọi query với |S| ≤ c. Khi đó K tăng tổ hợp, nên B1 nặng hơn.
  - (ii) data splitting: chọn Q trên nửa này, score trên nửa kia.
  - (iii) selective inference kiểu Guo–Wu–Yiu cho feature. Đây là một nghiên cứu mới, chưa có.
- **Ghi chú:** [PLAN] P1b đề xuất "Q = query FCI thực sự dùng + superset/subset". Nếu dùng chung mẫu thì vi phạm (A1).

### 2.6 Nonparametric extension (GCM)

- [Source-verified, Shah & Peters arXiv 2022] Theorem 6(i): CLT **đơn biến** đồng đều cho T^(n) dưới H0 khi A_f·A_g = o_P(n^{−1}), B_f = o_P(1), B_g = o_P(1), và 0 < E(ε²ξ²) < ∞ (tr. 9–10). Theorem 2: không có kiểm định CI non-trivial nào đồng đều trên mọi phân phối liên tục. Power chỉ có với E cov(X,Y|Z) ≠ 0 (tr. 11).
- **Joint CLT cho vector K thống kê GCM** (các tập S_k khác nhau, chung mẫu): **không có trong paper** (không tìm thấy). Có thể suy ra bằng Cramér–Wold khi mỗi thành phần thỏa điều kiện Theorem 6 và các residual product có moment bậc hai đồng thời hữu hạn [Inference, chưa chứng minh]. Dưới alternative cần thêm điều kiện cho ν_f, ν_g (tr. 11).
- "Residual product trung bình = 0 ⇒ CI" là **sai** dưới phân phối tùy ý. Chiều đúng là: CI ⇒ E cov = 0.
- Rank bound kiểu R **không** áp dụng trực tiếp, vì không có tham số hóa hữu hạn chiều. Nhưng **first-order duplicate** (S và S ∪ {W} với W độc lập) vẫn cho tương quan tiệm cận ≈ 1 [Inference].

---

## 3. P1–P7 proof audit (ledger)

| P | Phát biểu gốc ([GAP] Phần 3) | Giả định đầy đủ | Kết quả | Hệ quả |
|---|---|---|---|---|
| P1 | Oracle z = ζ_n: f Q-id ⇒ D > 0; ¬f Q-id ⇒ D < 0; cả hai chứa π(m*) ⇒ D = 0 | A0, A2-a, A2-b (η đúng), W PD, n cố định | **PROVED** (đã kiểm tra lại từng bước) **với sửa đổi**: (1) nếu M_¬f = ∅ thì D = +∞; (2) D hữu hạn khi M_¬f ≠ ∅, **không** phải +∞. Unit test T-P1 trong [PLAN] §4 P2 ("D(f) = +∞") là **sai**: nó chép từ ACI Thm 1, vốn dùng *infinite weights* [Source-verified ACI tr. 5]. Test đúng: D > 0, D = Θ(n) | Sửa test T-P1 |
| P2 | D_{Σ̂} → +∞ in prob., tốc độ ≥ n | A0, A1-a, **A1-b (PD)**, A1-c, A2, Q và M cố định, P cố định | **VALID WITH MODIFICATION**. Bước (a) (Lipschitz) và (c) đúng. Bước (b) cần λ_max(W) < ∞ **và W PD**; nếu không, (b) hỏng (C-c). Tốc độ: D ≥ c²n − O_p(√n) ✓ | Chỉ áp dụng khi Σ PD (C-a) và Q cố định |
| P3 | W chéo ⇒ D_W trùng ACI C(f) | W chéo, R_n tích Descartes | **VALID WITH MODIFICATION** (§4) | Đổi chữ "trùng ACI" thành "trùng một loss kiểu ACI (HEJ/ACI Eq. 13 với weights a_k và quyết định ŝ_k riêng)" |
| P4 | K = 2, inactive ⇒ hiệu = (z_2 − r z_1)²/(1−r²), không separable | Σ PD, \|t*\| ≥ δ | **PROVED** (công thức); **có thêm** trường hợp active (4.2). **Diễn giải "đếm trùng": COUNTEREXAMPLE** (§4) | Không dùng P4 làm bằng chứng double counting |
| P5 | Bản sao byte-identical ⇒ D bất biến (quy ước C-b) | Sao chép chính xác, quy ước C-b | **PROVED** (kiểm tra lại (AB)⁺ = B⁺A⁺) | **Không** mở rộng được sang first-order duplicate: COUNTEREXAMPLE R′ |
| P6 | D là GLR | z ~ N(ζ, Σ) **đúng chính xác**, Σ chung | **PROVED trong working model (I-a)**; **không** là LR của Gaussian MAG | Không được dùng χ²/chi-bar trực tiếp (§4-P6) |
| P7 | Search trên tập con của M_¬f ⇒ score ≥ thật | inf trên tập con | **VALID WITH MODIFICATION**: đúng cho d(M_¬f) và cho T(f). Với D, nếu xấp xỉ **cả hai** phía thì **không có chiều bất đẳng thức** | "Safe bound" chỉ có với T(f), hoặc D khi M_f exact |

---

## 4. Chi tiết re-derivation và counterexamples

### P1 [Derived, kiểm tra lại]

- **Bổ đề:** ζ_n ∈ R_n(m) ⇔ π(m) = π(m*). Hai chiều đều đúng như [GAP], cần δ_{n,k} > 0 (tức η > 0).
- R_n(m) đóng (tích của {0} và hợp hai nửa đường đóng), và M hữu hạn, nên R_n(M′) đóng. Với W PD, inf đạt được và > 0 khi điểm nằm ngoài.
- (i) cần m* ∈ M_f. Điều này suy ra từ Q-identifiability cộng A0. ✓ (ii) và (iii) đúng theo đối xứng.
- **Không cần** z không nhiễu cho (iii): (iii) đúng với mọi z (§2.1).

### P2 [Derived]

- **(a)** |d(z,R) − d(ζ,R)| ≤ ‖z − ζ‖_W. Đúng cho mọi chuẩn và cho cả seminorm.
- **(b)** ‖v‖_W ≥ λ_max(W)^{−1/2}·|v_k|. Đúng khi W PD, vì vᵀW⁻¹v ≥ λ_min(W⁻¹)‖v‖² ≥ λ_max(W)^{−1}v_k².
- **(c)** ‖z − ζ_n‖_{Σ̂} = O_p(1) cần Σ PD (nếu Σ suy biến và Σ̂ → Σ, thì Σ̂⁻¹ có thể → ∞ theo các hướng của null space).
- **Kết luận:** P2 đúng dưới A1-b. **Phản ví dụ cho P2 dưới C-d với λ_n → 0:** ở R′ (a = 0), z_1 − z_2 = O_p(n^{−1/2}) ≠ 0. Với W = Σ + λI và λ → 0, ‖z − 0‖²_W ⊇ (z_1 − z_2)²/(2λ). Nếu λ = o(1/n) thì số hạng này → ∞, nên d(z, R(m*)) → ∞. Do đó (c) **sai**. [Derived; Day 2 minh họa.]

### P3 [Derived]

- Tách theo tọa độ: c_k(z,1) = z², c_k(z,0) = (δ − |z|)₊². ✓
- Quyết định: ŝ_k = 1 (độc lập) ⇔ z² ≤ (δ − |z|)₊² ⇔ |z| ≤ δ/2. Ngưỡng |z| = δ_{n,k}/2 = √(n−|S|−3)·η/2 **tăng theo √n**.
- Trọng số:

(4.1)  a_k = |c_k(z,1) − c_k(z,0)| / w_k = δ·| 2|z| − δ | / w_k khi |z| < δ;  = z²/w_k khi |z| ≥ δ.

- **So với ACI đã công bố** [Source-verified ACI tr. 4, Eq. 14–15; tr. 5, Eq. 16–17]:
  - Weight tần suất là w = |log p − log α|, với α cố định (hoặc α_N → 0 cho consistency, Eq. 17).
  - Quyết định của ACI là p ≶ α, tương đương |z| ≶ Φ^{−1}(1 − α/2), **cố định theo n** khi α cố định.
  - Loại statement cũng khác: ACI còn có input ancestral từ intervention.
- **Kết luận:**
  - D_W với W chéo = C(f) của ACI Eq. 16 **với input set {(q_k, ŝ_k, a_k)}**. Đẳng thức đúng cho **giá trị loss (sai khác hằng số B)**, **optimizer** và **thứ tự feature**, nhưng chỉ **với weights a_k, không phải weights ACI**.
  - Hai cách gán weights cho thứ tự feature khác nhau nói chung. Do đó "diagonal control" B2 trong [PLAN] phải được định nghĩa là đúng loss này (4.1), **không** phải ACI Eq. 14.
  - Ghi chú: Fisher-z có w_k = Σ_kk = 1, nên W chéo của Fisher-z là trọng số đơn vị.

### P4 [Derived; công thức đúng, diễn giải bị bác bỏ một phần]

- **Công thức inactive:** Σ⁻¹ = (1−r²)^{−1}[[1, −r], [−r, 1]]. Với z′ = (0, t):

  Q(t) = z_1² + (t − t*)²/(1−r²),  t* = z_2 − r z_1.

  Do đó inf_{|t|≥δ} Q = z_1² + (δ − |t*|)₊²/(1−r²).

(4.2)  dist²(z, R(m_a)) − dist²(z, R(m_b)) = [ t*² − (δ − |t*|)₊² ] / (1 − r²).

  Khi |t*| ≥ δ, công thức trở về (z_2 − r z_1)²/(1−r²) của [GAP] ✓. Khi |t*| < δ (active), nó bằng (2δ|t*| − δ²)/(1−r²). Biểu thức này **vẫn phụ thuộc z_1**, nên non-separability cũng đúng ở trường hợp active.

- **Non-separability là tính chất tổng quát của mọi dạng toàn phương không chéo**, không phải insight nhân quả. Đúng là không tồn tại a_k(z_k) tái tạo (4.2). Đó là hệ quả tầm thường của việc Σ⁻¹ không chéo.

- **Phản ví dụ cho diễn giải "ACI đếm trùng phần nhiễu chung":**
  - Trong ví dụ P4, hai mô hình **cùng đồng ý** về q_1 (π_1 = 1). Số hạng ACI-kiểu cho q_2 là z_2²/1. Dưới m_a, z_2 ~ N(0,1), nên z_2² ~ χ²_1 **chính xác**, tức calibration biên đúng.
  - Full-Σ dùng z_1 làm **control variate**: z_1 là nhiễu thuần (ζ_1 = 0 dưới cả hai), nên trừ r·z_1 làm **giảm phương sai** của ước lượng ζ_2 từ 1 xuống (1−r²).
  - Đây là **tăng hiệu quả**, không phải "khử đếm trùng".
  - Đếm trùng thật sự xuất hiện khi **hai mô hình khác nhau ở ≥ 2 tọa độ tương quan dương**, ví dụ π = (1,1) so với (0,0). Khi đó loss chéo cộng z_1² + z_2² như hai bằng chứng. Dưới null, tổng này có E = 2 nhưng Var = 4(1 + r²) > 4, nên **đuôi nặng hơn χ²_2** [Derived: Var(z_1² + z_2²) = 2 + 2 + 2·Cov(z_1², z_2²) = 4 + 4r²].
  - Day 2 phải kiểm tra **cả hai** cấu hình.

- **Realizability (MAG):**
  - Q = {X⊥Y, X⊥Y|Z}. m_a: X→Z, Y cô lập, cho π = (1,1). m_b: X→Z←Y, cho π = (1,0). Cả hai là MAG (DAG) hợp lệ.
  - Dưới m_a với ρ_{XZ} = a, có r = √(1−a²) (2.1).
  - **Mệnh đề E (evidence ngoài Q)** [Derived bậc một]. Tuyến tính hóa quanh m_a: z_1 ≈ u, z_2 ≈ (u − a v)/√(1−a²), với u, v là sai số chuẩn hóa của ρ̂_{XY}, ρ̂_{YZ}. Khi đó

(4.3)  (z_2 − r z_1)/√(1−r²) ≈ (a u − v)/√(1−a²) ≈ − z_{YZ|X}.

  - Tức là "evidence dependence-aware" mà D trích ra để phân biệt m_a với m_b là (bậc một) **thống kê của query Y⊥Z|X, không thuộc Q**. Điều này đúng về thống kê, vì Y⊥Z|X đúng trong m_a và sai trong m_b. Nhưng nó cho thấy:
    - (i) so sánh "cùng Q" giữa ACI và D **không cân bằng thông tin**: D khai thác cấu trúc tuyến tính nối các query, qua Σ;
    - (ii) control tự nhiên là **ACI trên Q mở rộng** (thêm các query mà Σ ngầm tái tạo);
    - (iii) ở Gaussian, D là xấp xỉ của một phép so sánh trên toàn ma trận tương quan, tức họ hàng của B4.
  - Day 2 kiểm tra (4.3) bằng Monte Carlo.

### P5 [Derived]

- Với L full column rank và Σ_r PD: LΣ_rLᵀ = (LΣ_r^{1/2})(Σ_r^{1/2}Lᵀ). Áp dụng (AB)⁺ = B⁺A⁺ khi A full column rank và B full row rank, ta được (Lᵀ)⁺Σ_r^{−1}L⁺. Với v = Lw: vᵀΣ⁺v = wᵀΣ_r^{−1}w. ✓ R(m) ∩ range(L) = L·R_r(m), vì π_{K+1} = π_K và δ_{K+1} = δ_K. ✓ **PROVED.**
- **Giới hạn:**
  - (i) ACI với dedup cũng đạt bất biến. Do đó P5 không phân biệt A′ với một ACI có tiền xử lý tầm thường.
  - (ii) Phản ví dụ R′: bản sao **bậc một** (r = 1 tiệm cận, nhưng z_1 ≠ z_2) cho +∞ dưới C-b.
  - (iii) Liên tục khi r → 1 với z cố định: theo (4.2), nếu z_1 = z_2 = c thì t* = c(1 − r), và hiệu (inactive) bằng c²(1−r)/(1+r) → 0. Nếu z_1 ≠ z_2 cố định, t* → z_2 − z_1 ≠ 0, nên hiệu ~ (z_2 − z_1)²/(2(1−r)) → ∞. **Giới hạn phụ thuộc z, không liên tục đều.** Xác nhận [GAP] "không được claim liên tục".
    - **[ERRATUM 2026-11-04, phát hiện ở Day 2, `A1_toy_results.md` §2.3]:** trường hợp z_1 = z_2 ở trên **sai**. Khi t* = c(1 − r) → 0 thì |t*| < δ, nên rơi vào nhánh **active**. Khi đó hiệu ≈ −δ²/(1 − r²) → −∞ (số: −4998 tại r = 0.9999, δ = 1). Kết luận đúng: **với δ > 0, D phân kỳ khi r → 1 ở mọi z thử nghiệm.** Nhận định "không liên tục" còn mạnh hơn.

### P6 [Derived]

- −2 log φ_Σ(z − ζ′) = ‖z − ζ′‖²_Σ + log det(2πΣ). Lấy max trên ζ′ ∈ R(M′) rồi lấy hiệu, ta được D = 2[ℓ̂(H_f) − ℓ̂(H_¬f)]. ✓ (trong working model, Σ chung).
- **Không phải** LR của Gaussian MAG: (i) R ⊋ A (§1.4); (ii) Σ thật khác nhau giữa các giả thuyết (A3).
- **Calibration:**
  - H_f và H_¬f **không lồng nhau**, và mỗi bên là hợp không lồi. Lý thuyết chi-bar-square áp dụng cho kiểm định nón lồi lồng nhau [UNVERIFIED về điều kiện chính xác: Shapiro 1985 là scan không text layer, chưa đọc; Silvapulle–Sen thiếu]. Vì thế **không** có phân phối chuẩn tắc cho D.
  - Ngoài ra hai vùng cách nhau một **indifference zone** độ rộng δ = Θ(√n). Dưới H_f gần biên, D không có phân phối pivot.
  - Kết luận: **D không calibrated theo bất kỳ nghĩa tần suất nào đã chứng minh.**

### P7 [Derived]

- d(z; M̃) ≥ d(z; M) khi M̃ ⊆ M. ✓
- Với D:
  - M_¬f xấp xỉ, M_f exact ⇒ D̃ ≥ D (anti-conservative) ✓.
  - M_f xấp xỉ, M_¬f exact ⇒ D̃ ≤ D.
  - Cả hai xấp xỉ ⇒ **không so sánh được**.
- Solver cục bộ cho bài toán không lồi (hợp đa diện) có hiệu ứng giống "tập con", nên cũng anti-conservative cho phía ¬f. Relaxation lồi (bao lồi) của R(M_¬f) cho cận dưới ⇒ an toàn cho T(f).

---

## 5. Counterexamples (tổng hợp, tái lập được)

| # | Mục tiêu bác bỏ | Ví dụ nhỏ nhất | Kết quả |
|---|---|---|---|
| CE1 | (A1-b) Σ PD | p = 3, K = 6 bậc ≤ 1, mọi R | rank Σ = 3 (số) |
| CE2 | P5 mở rộng cho near-duplicate; P2 dưới C-b/C-d | Q = {X⊥Y, X⊥Y\|Z}, Z ⊥ (X, Y) (a = 0) | r = 1, z_1 ≠ z_2 ⇒ dist(z, R(m*)) = +∞ (C-b); → ∞ khi λ → 0 (C-d) |
| CE3 | Diễn giải "đếm trùng" của P4 | P4, m_a vs m_b | Số hạng chéo z_2² ~ χ²_1 chính xác dưới m_a; full-Σ là control variate |
| CE4 | "D(f) = +∞ ở oracle" (T-P1) | bất kỳ M_¬f ≠ ∅ | D = Θ(n) hữu hạn |
| CE5 | "D trùng ACI" (P3) | weights (4.1) vs \|log p − log α\| | Ngưỡng quyết định khác (δ/2 tăng theo √n so với hằng số); thứ tự feature có thể khác |
| CE6 | Score có nghĩa khi không có η | η → 0, M_f, M_¬f cùng chứa complete MAG | D → 0 với mọi z |
| CE7 | P7 cho D xấp xỉ hai phía | M̃_f ⊊ M_f, M̃_¬f ⊊ M_¬f | dấu của D̃ − D tùy ý |

---

## 6. Implementation test specification (cho Day 2, theo toán đã sửa)

| Test | Input | Kỳ vọng | Tolerance |
|---|---|---|---|
| T-P1′ | oracle z = ζ_n, f Q-id, M_¬f ≠ ∅ | 0 < D < ∞; D/n → hằng số > 0 khi n tăng | tương đối 1e-8 |
| T-P3′ | W chéo, K = 2, mọi pattern | D_W = hiệu loss kiểu ACI với a_k (4.1), ŝ_k = 1[\|z\| ≤ δ/2] | tuyệt đối 1e-10 |
| T-P4 | Σ = [[1, r], [r, 1]], z = (2, 1.8), r ∈ {0, ±0.3, ±0.6, ±0.9}, δ ∈ {1, 3} | khớp (4.2) giải tích, cả nhánh inactive lẫn active | 1e-9 |
| T-P5 | bản sao chính xác, C-b | D không đổi | 1e-9 |
| T-CE2 | R′ a = 0, mô phỏng | dưới C-b: +∞; dưới C-c: hữu hạn; dưới C-d: tăng khi λ ↓ | định tính, có số |
| T-R | p = 3, K = 6 | rank số của Σ delta = 3; Monte Carlo cov của z có 3 trị riêng O(1) và 3 trị riêng ≪ 1, giảm theo n | ghi giá trị |
| T-E | (4.3) | corr Monte Carlo giữa (z_2 − r z_1)/√(1−r²) và z_{YZ\|X} → −1 khi n lớn | ghi giá trị, không ngưỡng cứng |
| T-P7 | tập con ngẫu nhiên của M_¬f | d tăng | đúng tuyệt đối |

---

## 7. Alternative formulations (sửa tối thiểu — để đánh giá, không bắt buộc)

| Sửa | Định nghĩa | Mua được gì | Đổi câu hỏi khoa học thế nào | Mức novelty [Inference] |
|---|---|---|---|---|
| **R1: score một phía + projection** | Assert f ⇔ T_Σ(f) = d_Σ(z; M_¬f)² > c_α, với c_α = χ²_{rank(Σ), 1−α} | [Derived] Nếu ζ_n ∈ R_n(m*) (beta-min đúng) và z − ζ_n ~ N(0, Σ) (Σ PD, Q cố định), thì P(assert f sai) ≤ P(‖z − ζ_n‖² > c_α) = α, đồng thời cho **mọi** feature. Đây là projection từ confidence ellipsoid. Relaxation R ⊋ A chỉ làm giảm power. **Ghi chú [Derived]:** lập luận chỉ dùng T ≤ ‖z − ζ_n‖² (tính Lipschitz/inf), nên vẫn đúng với *seminorm* C-c (Σ⁺, không có support) và ngưỡng χ²_{rank Σ}. Như vậy R1 **tránh được B1 cho validity**, với điều kiện rank Σ biết trước hoặc ước lượng nhất quán; cái giá là mất thông tin ngoài range | Từ "confidence score" sang "**simultaneous certified assertions**" dưới beta-min | Thấp: projection của confidence set (kiểu Scheffé) là cổ điển. Phần còn lại là *ứng dụng* vào vùng m-separation |
| R1′: IUT theo từng m | Assert f ⇔ ∀m ∈ M_¬f: test của H_m bác bỏ ở mức α | Berger: IUT là test mức α cho null là hợp [Source-verified: Berger 1980 TR M555, Theorem 1, tr. 7 (OCR)] | Như R1, ngưỡng có thể chặt hơn theo từng m | Thấp |
| **R2: η-profile (fragility)** | η*(f) = inf{η : f được assert ở mức α} | Biến giả định không kiểm định được (η) thành **đại lượng báo cáo**: "f được chứng nhận nếu mọi dependence thật có \|atanh ρ\| ≥ η*(f)" | Từ calibration sang **sensitivity analysis đối với strong faithfulness** | Trung bình [Hypothesis]: chưa thấy trong nguồn đã đọc. Cần tìm prior art về λ-strong faithfulness (Zhang–Spirtes 2003; Uhler et al. 2013 [UNVERIFIED]) |
| R3: tham số hóa trong không gian tương quan | Thay z ∈ R^K bằng ρ̂ ∈ R^d; vùng = A(m) thật | Sửa B1 (rank) | Gaussian: thành minimum-distance/likelihood cho MAG, tức B4 | Thấp; trùng full-likelihood |
| R4: Q-closure ACI control | ACI trên Q′ ⊇ Q chứa các query "ngầm" (Mệnh đề E) | Tách lợi ích "thêm thông tin" khỏi "dependence" | — | Baseline, không phải phương pháp |
| R5: data splitting cho Q thích nghi | Chọn Q trên D_1, score trên D_2 | Sửa §2.5 | Mất một nửa n | Thấp |
| R6: bỏ "confidence", chỉ ranking | D như ranking score, đánh giá bằng risk–coverage | Không cần calibration | Câu hỏi thuần thực nghiệm. BSC-D đã quan sát ranking ít thay đổi ở cấp PAG [Source-verified bscd.pdf tr. 13–14] | Thấp–trung bình, phụ thuộc pilot |

**Đánh giá trung thực:** R1 + R2 là cách duy nhất tìm thấy trong phiên này cho **một score có nghĩa thống kê đã chứng minh được** (dưới working model). Nhưng:
- (a) R1 là cổ điển;
- (b) R1 vẫn chịu B1 (cần Σ PD, hoặc rank-aware χ² cùng tham số hóa R3);
- (c) R2 đổi trọng tâm từ "dependence-aware" sang "**beta-min-aware**". Dependence chỉ còn là chi tiết kỹ thuật cần thiết để ellipsoid đúng.

Nói cách khác, **phần "dependence-aware" tự nó không phải đóng góp khoa học**. Nó là điều kiện đúng đắn của mọi phương pháp dựa trên vector thống kê chung.

---

## 8. Blockers

| # | Blocker | Loại | Bằng chứng | Có thể làm gì |
|---|---|---|---|---|
| B1 | Σ suy biến hoặc gần suy biến (rank ≤ p(p−1)/2; first-order duplicates r = 1), đúng ở regime động lực | **REFORMULABLE** (R3, C-a), nhưng sửa đi thì novelty ở Gaussian sụp | CE1, CE2 | Day 2: minh họa số |
| B2 | D dạng hiệu không có calibration hay diễn giải tần suất | **REFORMULABLE** (R1/R1′) | §4-P6 | Day 2: so sánh FAR của T và D dưới null |
| B3 | Phụ thuộc η biết trước; misspecification cho sai tự tin; không kiểm định được | **REFORMULABLE thành R2**, không loại bỏ được | §1.6, §2.3, CE6 | Day 2: sensitivity theo η |
| B4 | Q thích nghi trên cùng mẫu | **REFORMULABLE** (Q cố định / R5) | §2.5 | Ghi trong contract pilot |
| B5 | GCM: beta-min là giả định riêng; joint CLT chưa có nguồn | **UNKNOWN** | §2.6 | Không test được ở Day 2 ngoài mô phỏng mô tả |
| B6 | Relaxation R ⊋ A | **TESTABLE** (power) | §1.4, §2.2 | Day 2: chỉ ghi nhận |
| B7 | Novelty: lõi là constrained GLS / projection / IUT; non-separability tổng quát; D ngầm dùng thông tin ngoài Q | **UNKNOWN → nghiêng về FATAL cho framing gốc** | §4-P4, §7 | Day 3: register prior art; thiếu Triantafillou 2014, Silvapulle–Sen, Browne-type literature |

**Không có blocker nào FATAL cho *toán* ở dạng sửa đổi.** Nhưng framing gốc ("off-diagonal là cơ chế trung tâm của một đóng góp mới, Gaussian chỉ là arm kiểm chứng, H-cal là claim chính") **không đứng được** như đã viết. Lý do: B1 làm arm Gaussian trùng full-likelihood, B2 làm "calibration" không có định nghĩa, B7 làm cơ chế không đặc thù nhân quả.

---

## 9. Day 2 authorization: **TOY-WITH-CAVEATS**

**Được phép (chỉ đại số/số học, toy):**
1. Experiment A (K = 2): kiểm tra (4.2) inactive và active; r = 0 trùng chéo; đổi dấu r và z; r → ±1; bản sao chính xác dưới C-b; so với naive additive và dedup control. Mọi so sánh tại cùng z là **minh họa toán**.
2. Experiment B (Monte Carlo, working model Gaussian thuần):
   - phân phối dưới null của số hạng chéo và full-Σ trong **hai** cấu hình: khác 1 tọa độ (CE3) và khác 2 tọa độ (đếm trùng thật);
   - FAR tại ngưỡng **định nghĩa trước**: ngưỡng χ² của R1 và ngưỡng chuyển từ regime r = 0;
   - Σ oracle và Σ̂ ước lượng.
   - Ghi rõ: kết quả "chéo trôi, full không trôi" là **tautological theo cấu trúc toy**.
3. Experiment C: rank (CE1) bằng Monte Carlo trên dữ liệu Gaussian thật (p = 3); first-order duplicate (CE2) dưới C-b/C-c/C-d; Mệnh đề E (4.3) trên SCM 3 biến khả thi; kiểm tra r = √(1−a²) bằng mô phỏng.
4. Sensitivity theo η (CE6, misspecification) trên toy K = 2–3.

**Không được phép:**
- so sánh hiệu năng với ACI/BSC-D/FCI;
- enumerate MAG;
- claim calibration/coverage;
- dùng D (1.3) như "confidence";
- pilot nhân quả;
- benchmark.

**Caveat bắt buộc trong mọi kết quả Day 2:**
- Σ chung (A3);
- relaxation R (A4);
- η biết trước;
- Q cố định;
- Gaussian working model.

---

## 10. Citation / evidence register

| Nguồn | File | Phần đã đọc trong phiên | Dùng cho |
|---|---|---|---|
| Magliacane, Claassen, Mooij, *Ancestral Causal Inference*, NIPS 2016 | `docs/papers/ACI_2016.pdf` | tr. 4: Eq. 12–15 (loss cộng tính, weights); tr. 5: Eq. 16, Thm 1–2, Eq. 17–18; tr. 9: Discussion ("loss function essentially assumes that the test results are independent… may not be straightforward") | P3, CE4, CE5, động lực |
| Jabbari, Ramsey, Spirtes, Cooper, BSC-D, ECML-PKDD 2017 | `docs/papers/bscd.pdf` | tr. 13–14: "BSC-I and BSC-D performed very similarly"; "ordering … almost always the same"; naive Bayes conjecture; tr. 4–5: mô tả [34] (Triantafillou 2014) | R6, Day 3 |
| Guo, Wu, Yiu, UAI 2026 | `docs/papers/Guo_Wu_Yiu_2026_Price_Valid_Inference.pdf` | Abstract; Theorem 1 (đa diện Fisher-z cho selection event FCI); Theorem 2 (CI cho effect) | §2.5 |
| Shah & Peters, GCM (arXiv, 25-03-2022) | `docs/papers/Shah_Peters_GCM_arxiv.pdf` | Theorem 2 (no-free-lunch); Theorem 6(i) (CLT đơn biến); §3.1.1 (power chỉ khi E cov ≠ 0) | §1.6, §2.6 |
| Berger, *Multiparameter Hypothesis Testing and Acceptance Sampling*, FSU TR M555 (1980) | `docs/papers/Berger_1980_M555_Technical_Report.pdf` | Theorem 1 (IUT mức α), Theorem 2 (size đúng α) — OCR lỗi một phần | R1′ |
| Olkin & Finn, *Correlations Redux*, TR 1994 | `docs/papers/Olkin_Finn_1994_Correlations_Redux_Technical_Report.pdf` | **Không có text layer** (trích text rỗng). **Chưa đọc.** Công thức cov tiệm cận của tương quan Pearson trong kiểm tra số là bản tự cài, sẽ đối chiếu Monte Carlo | CE1, CE2 |
| Shapiro 1985 (chi-bar) | `docs/papers/Shapiro_1985_Inequality_Constraints.pdf` | **Chưa đọc** (scan) | P6 [UNVERIFIED] |
| Silvapulle & Sen 2005 | thiếu | — | P6 [UNVERIFIED] |
| Robins et al. 2003; Zhang–Spirtes 2003; Uhler et al. 2013; Browne-type covariance-structure GLS | không có trong repo | — | [UNVERIFIED]; chỉ dùng làm câu hỏi prior art |

---

## 10b. ERRATUM 2026-11-04 (sau khi đọc Robins et al. 2003, Zhang–Spirtes 2003, Chang–Guo–Malinsky)

- **§1.6, A2-b, blocker B3 phát biểu quá mạnh.** η **cố định và biết trước** chỉ cần cho validity **đồng đều (uniform) hoặc hữu hạn mẫu**.
- Với validity **pointwise tiệm cận** (P cố định, n → ∞), có thể dùng δ_{n,k} = √(n−|S_k|−3)·η_n với η_n → 0 và √n·η_n → ∞. Cách này tương tự α_N → 0 của ACI Eq. 17 [Source-verified ACI tr. 5]. Với mọi P faithful cố định, min |atanh ρ_k| trên các dependence là một hằng số > 0, nên beta-min đúng với η_n khi n đủ lớn. Khi đó R1 valid pointwise **không cần biết η**. [Derived]
- Phân biệt pointwise/uniform là chuẩn: Robins et al. 2003 (pointwise consistent nhưng không uniform khi có latent); Zhang & Spirtes 2003 (uniform dưới strong faithfulness) [Source-verified, abstract của cả hai].
- **Không thay đổi:**
  - Experiment E (Day 2) vẫn đúng như minh họa **hữu hạn mẫu**: η đặt sai ở n cố định cho kết luận sai.
  - CE6 (η → 0 ở n cố định làm D suy biến) vẫn đúng, vì η_n → 0 phải chậm hơn 1/√n.
- **Thay đổi định vị R2:** η-profile là báo cáo cho **guarantee đồng đều/hữu hạn mẫu**, bổ sung cho R1 pointwise. Nó không còn là "cách duy nhất để có validity".

## 11. Decision log entry (đề xuất append vào [PLAN] §9)

| # | Ngày | Gate / sự kiện | Kết quả | Bằng chứng | Quyết định | Người chốt |
|---|---|---|---|---|---|---|
| 5 | 2026-11-04 | Day 1 independent mathematical audit | P1, P5, P6 PROVED (có sửa); P2, P3, P7 VALID WITH MODIFICATION; P4 công thức đúng, diễn giải bị bác bỏ một phần; (A1-b) Σ PD **sai** (CE1, CE2); D không calibrated | `reports/aprime_review_2026-11-04/A1_mathematical_contract_v2.md` | Day 2 = TOY-WITH-CAVEATS | agent (chưa có user duyệt) |

## 11b. ERRATUM 2026-11-04 (RG1, `RG1_R1_proof_vi.md`)

Các phát biểu sau của contract này được sửa. Bản gốc giữ nguyên để truy vết.

- **§7 R1, ghi chú "R1 tránh được B1 cho validity… cái giá là mất thông tin ngoài range":** validity đúng, nhưng cái giá là **toàn bộ power**. Với seminorm toàn cục, d(z, m) = 0 với mọi z cho mọi m thỏa (B1)–(B2) (RG1 Thm 4); K > rank Σ là chưa đủ. Không dùng C-c toàn cục làm thủ tục.
- **§2.4 C-d "kết quả do quy ước quyết định":** quyết định bởi **tốc độ của λ_n**. Với nλ_n → ∞ thì valid đều khi p, K cố định (RG1 Thm 3, Nhận xét 3.5); ở hữu hạn mẫu λ phải đủ lớn so với K. Toy Day-2 dùng nλ ≤ 1 ở các dòng FAR lớn.
- **§4-P2 "cần Σ PD":** không cần khi dùng ridge, nhờ đường chéo của Σ̂ + λ_nI bị chặn (RG1 Mệnh đề 5, Thm 5).
- **§2.4 Mệnh đề R:** mạnh hơn, rank Σ bằng số chiều span các gradient, và = d khi Q chứa mọi query biên (RG1 Mệnh đề 2).
- **§7 R2:** η*(f) phải báo cáo cùng cận trên η̄ (RG1 Thm 7c).
- **§10b:** phát biểu pointwise đúng và đã có chứng minh, nhưng thresholding nhất quán đạt tốt hơn, nên không phải điểm mạnh của R1 (RG1 Mệnh đề 7).
