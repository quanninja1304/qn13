# A′ — Xác nhận gap còn lại (Guo–Wu–Yiu, BSC-D) và chứng minh rút gọn trên giấy

Ngày: **03-11-2026**. **Không chạy thí nghiệm.** Các chứng minh dưới đây là **derivation trên giấy do audit tự thực hiện, chưa được review độc lập**. Mỗi mệnh đề ghi rõ giả định; phần nào chưa chứng minh được ghi **[Open]**.

Nhãn nguồn: **[Verified-full]** đọc full text (ở đây bằng trích xuất text thô từ PDF chính thức, nên ký hiệu toán bị hỏng một phần); **[Verified-impl]** đọc tài liệu triển khai chính thức, không phải paper; **[Verified-abstract]**; **[Inference]**; **[Open]**.

---

## Phần 1 — Xác nhận gap

### 1.1 Guo, Wu, Yiu — *The Price of Valid Inference After Causal Discovery*, UAI 2026, PMLR 337:1804–1822 [Verified-full]

Nguồn: [landing](https://proceedings.mlr.press/v337/guo26a.html); PDF chính thức qua link "Download PDF" (raw GitHub của mlresearch), trích xuất text bằng script stdlib trong scratchpad. Không đọc được OpenReview (browser challenge).

| Điểm kiểm tra | Nội dung đọc được | Hệ quả cho A′ |
|---|---|---|
| Theorem 1 (*Polyhedral Characterization of FCI in Fisher-z Space*) | Dưới phân phối Gaussian đồng thời, sự kiện "FCI ở mức α₀ xuất ra PAG P̂" được biểu diễn là {Y : A_P̂ · z(Y) ≤ b_P̂}, điều kiện trên execution trace và signs. Ràng buộc là \|z_k\| ≤ c hoặc ≥ c cho từng test đã thực hiện | Hình học "vùng trong không gian Fisher-z" **đã có**. Nhưng đây là vùng của **selection event của thuật toán** (dữ liệu nào cho ra *cùng output*), **không phải** vùng của các vector thống kê tương thích với một **mô hình** phủ định một feature |
| Theorem 2 (*Selective Confidence Interval for FCI-PAGs*) và Table 1 | Target là **causal effect** β_{i→j} / adjustment functional; Table 1 so sánh với Chang+ 2026, Gradu+ 2025, Strieder+ 2021, tất cả đều về effect | **Không** có confidence, p-value hay score cho edge/endpoint/ancestral feature |
| Covariance giữa các z | Chứng minh dùng sufficient statistic là sample covariance; truncation tính trong Y-space theo hướng inference. Không định nghĩa khoảng cách Mahalanobis giữa các z | Không có score kiểu "khoảng cách tới vùng ¬f" |
| Limitations / Open questions (§8, App. I) | Gaussianity; GES chỉ là heuristic rate; distortion ρ² không biến mất; chưa tách γ₁-coverage khỏi β-coverage. Open questions: độ chặt của bound splitting, mở rộng sang nonparanormal | Không nêu feature-level uncertainty như future work |

**Kết luận 1.1:** gap của A′ **còn sống** so với Guo–Wu–Yiu. Hai công trình dùng chung hình học (vùng đa diện trong không gian Fisher-z) nhưng khác **đối tượng** (model-consistency region vs algorithm-selection region) và **target** (feature confidence vs effect CI). Paper này là **related work bắt buộc** và là **công cụ tiềm năng** cho extension selective-inference (§3, P6). A′ không được claim "hình học Fisher-z" là mới.

### 1.2 BSC-D — Jabbari, Ramsey, Spirtes, Cooper, ECML-PKDD 2017, pp. 142–157 [Verified-full]

Nguồn: bản PDF người dùng cung cấp, `docs/papers/bscd.pdf`, trích xuất text thô (đủ 20 trang). Các trích dẫn dưới đây là **nguyên văn** từ bản trích xuất.

**Cơ chế:**
- **§3.1, Eq. 1–2.** Dựa trên *data relevance assumption* P(r_i | D) = P(r_i | D_i). Đại lượng P(r_i | D_i) được tính bằng BDeu, so sánh cấu trúc X_i ← Z_i → Y_i với Z_i → (X_iY_i). Paper xét **discrete variables**.
- **§3.2, Algorithm 1.** RFCI-BSC (RB): mỗi lần RFCI hỏi một CI, RB **lấy mẫu** "independent" với xác suất p = BSC, rồi lặp n vòng để sinh tối đa n PAG.
- **§4, Eq. 3–5.** P(G_j | D) ≈ P(r = r*_j | D), với r là hợp các constraint đã được hỏi qua mọi vòng. Đây là xác suất của **cả PAG**.
- **§4.1, Eq. 7 (BSC-I):** tích các marginal P(r*_i | D_i).
- **§4.2, Algorithm 2, Eq. 8 (BSC-D):**
  1. Bootstrap dữ liệu 500 lần.
  2. Trong mỗi bootstrap, **nhị phân hóa** từng constraint (BSC ≥ 0.5 ⇒ 1).
  3. Học BN_r trên các biến nhị phân đó bằng FGES, ước lượng tham số bằng MAP.
  4. Score: P(G_j | D) ≈ ∏_i P(r*_i | Pa(r_i), D).
- **Feature-level output (§4):** xác suất edge-type = "the fraction of the sampled PAGs that contain E", tức tần suất trên các PAG được lấy mẫu. **Không** dùng BSC-D để điều chỉnh xác suất này. §6 liệt kê "selective Bayesian model averaging of the edge probabilities" là việc **tương lai**.

**Đánh giá (§5):**
- Mạng: Alarm (37 nút), Hailfinder (56), Hepar II (70).
- n ∈ {200, 2000}; ẩn 0/10/20% số confounder nodes; 100 vòng; 10 runs.
- Baseline duy nhất: RFCI với chi-square, α = 0.05.
- Metrics: skeleton SHD và edge-mark SHD so với PAG-True. **Không đo calibration và không đo feature-level confidence.**

**Kết quả và lập luận then chốt (nguyên văn):**
- "We observed that BSC-I and BSC-D performed very similarly."
- "BSC-I and BSC-D may result in different probabilities for the generated PAGs; however, the ordering of the PAGs according to their posterior probabilities is almost always the same."
- "We conjecture that performance of BSC-I is analogous to a naive Bayes classifier, which often performs classification well, even though it can be highly miscalibrated."
- §6: "As the sample size increases, we expect the constraints to become independent of each other, but in our experiments, dependence did not matter for SHD, even with small sample sizes."

**Xác minh gián tiếp ACI.** Phần related work của BSC-D viết rằng ACI "score[s] their marginal probabilities" của ancestral relations, và rằng [24] (ACI) cho rằng "modeling the relationships among the constraints may be an improvement". Điều này xác nhận độc lập mục [Summary-only] về ACI §6.

**Prior art mới được trích trong BSC-D (chưa đọc):** Triantafillou, Tsamardinos, Roumpelaki, *Learning neighborhoods of high confidence in constraint-based causal discovery*, PGM 2014, LNCS 8754:487–502. Paper này chuyển p-values thành posterior probabilities của adjacencies/non-adjacencies, tức một **feature-level confidence khác**. Phải thêm làm baseline và đọc trước khi claim.

**So sánh với A′:**

| Chiều | BSC-D (paper) | A′ |
|---|---|---|
| Evidence | Quyết định nhị phân sau bootstrap (ngưỡng 0.5) | Thống kê liên tục z và Σ |
| Dependence | BN rời rạc trên constraints | Hiệp phương sai của z (P4: thống kê điều kiện) |
| Target | Xác suất/thứ hạng **của cả PAG**; argmax PAG | Score **từng feature**; risk–coverage; calibration |
| Feature-level | Tần suất trên các PAG được lấy mẫu; dependence không được dùng | Dependence là cơ chế trung tâm |
| Data | Discrete (BDeu) | CI statistics tiệm cận chuẩn |
| Điều đã đo | SHD của argmax PAG | (đề xuất) feature risk–coverage, calibration |

**Hệ quả quan trọng cho A′. Đây là bằng chứng chống A′ mạnh nhất cho tới nay:**

1. **[Verified-full] Phản chứng một phần.** Ở cấp **argmax PAG**, việc mô hình hóa dependence **không thay đổi thứ tự** trong thực nghiệm của BSC-D. Đây là dữ liệu tiên nghiệm cho thấy hiệu ứng có thể nhỏ, và nó **phải được đưa vào hypothesis**, không được lờ đi.
2. **[Inference] Vì sao điều này chưa giết A′:**
   - (a) BSC-D so sánh các PAG **chia sẻ phần lớn constraints**. Phần đếm trùng gần như là hằng số chung, triệt tiêu khi lấy argmax; điều này giống B(z) trong P3. A′ so sánh **các feature khác nhau** dựa trên **các tập test khác nhau** với mức dư thừa khác nhau, nên đếm trùng có thể đổi thứ tự **giữa các features**.
   - (b) BSC-D chỉ đo SHD và **chính tác giả** dự đoán miscalibration (lập luận naive Bayes). A′ có thể kiểm tra điều mà BSC-D không đo: **calibration** và **error rate tại ngưỡng cố định**.
   - (c) Kỳ vọng "constraints become independent" khi n tăng đúng với **quyết định nhị phân**: chúng trở nên tất định, nên dependence biến mất. Với **thống kê liên tục**, các tọa độ independence (ζ_k = 0) vẫn là nhiễu O(1) với tương quan r cố định ở mọi n. Vì vậy đếm trùng ở phía independence **không biến mất tiệm cận**. Đây là điểm khác biệt về cơ chế có thể kiểm chứng.
3. **Cập nhật hypothesis của A′:**
   - **H-rank (yếu hơn, có thể thất bại):** đổi thứ tự features có ý nghĩa.
   - **H-cal (chính):** ở ngưỡng cố định, score cộng tính (ACI) có false-assertion rate vượt mức danh nghĩa, tăng theo mức dư thừa của query universe; D(f) giảm sai lệch này.
   - **Dự đoán của chính A′:** hiệu ứng ranking nhỏ hơn hiệu ứng calibration. Nếu cả hai đều ≈ 0 thì **no-go**.

**Kết luận 1.2:** gap **còn sống nhưng phải định vị lại sang calibration/feature-level**. Bằng chứng thực nghiệm duy nhất đã công bố về dependence-aware scoring (BSC-D) cho thấy **không có lợi ích về argmax/SHD**. A′ không được claim lợi ích về accuracy của best graph.

#### (Ghi chú lịch sử) Trước khi có bản PDF người dùng cung cấp

- **Full text paper: chưa đọc được.** PMC trả về reCAPTCHA; PDF ở Pitt trả 404; Europe PMC trả 500/403. Không có bản arXiv. Nội dung paper trong `source_audit_ci.md` (CI05) đến từ phiên trước và vẫn giữ nhãn cũ.
- **[Verified-impl]** Tài liệu Tetrad cho `RfciBsc` ([manual](https://tetrad-manual.readthedocs.io/en/latest/_sources/algorithms/rfci-bsc.md.txt)) mô tả cơ chế BSC-D như sau:
  1. Chạy nhiều RFCI ngẫu nhiên hóa để sinh candidate PAGs.
  2. Chỉ giữ các independence facts có xác suất trong một dải "informative" [lowerBound, upperBound].
  3. Bootstrap dữ liệu; với mỗi replicate, **mã hóa mỗi fact thành 0/1**, tạo thành một "constraint dataset".
  4. **Học một Bayesian network trên các fact** bằng FGES + BDeu để nắm dependence giữa chúng.
  5. Score log-probability của mỗi PAG, chuẩn hóa trên ensemble.
  6. Output là **một PAG tốt nhất** (theo BSC-D hoặc BSC-I), kèm **tần suất edge-type trên ensemble**.
  7. **Chỉ hỗ trợ discrete data**; tài liệu mô tả là "computationally heavy", "parameter-rich", nhạy với bounds và kích thước bootstrap.
  - Tài liệu ghi "There is no dedicated public paper for RfciBsc" và không trích dẫn Jabbari et al., nên việc gán đúng cơ chế này cho paper 2017 là **[Inference]**, khớp với CI05.

| Chiều so sánh | BSC-D | A′ |
|---|---|---|
| Đại diện evidence | Quyết định nhị phân (0/1) qua bootstrap | Thống kê liên tục z và Σ |
| Mô hình dependence | BN rời rạc học trên các fact (FGES/BDeu) | Hiệp phương sai tiệm cận/bootstrap của z |
| Output | Best PAG + tần suất edge-type trên ensemble | Score D(f) cho từng feature + risk–coverage |
| Data | Discrete | Bất kỳ CI statistic tiệm cận chuẩn (Gaussian trước) |

**Kết luận 1.2:** gap **còn sống nhưng hẹp hơn**. "Mô hình hóa dependence giữa các CI fact" **không phải** novelty (BSC-D đã làm). Phần còn lại là: dependence trong **không gian thống kê liên tục**, dùng cho **feature-level score**, và có **reduction tường minh** về ACI (§2). **Baseline bắt buộc mới:** "BSC-D-ACI", tức ACI Eq. 16 với joint distribution của các fact lấy từ BN của BSC-D, để kiểm tra lợi ích có đến từ biểu diễn liên tục hay không.

### 1.3 Đe dọa mới phát hiện khi làm chứng minh: feature posterior dựa trên full likelihood [Verified-abstract/search; Inference]

Với dữ liệu Gaussian, một **likelihood ratio đầy đủ** giữa mô hình tốt nhất trong M_f và trong M_¬f (Gaussian MAG likelihood qua RICF, hoặc BIC) dùng trực tiếp sufficient statistic Σ̂. Vì vậy nó **tự động "đếm evidence một lần"**. Dòng Bayesian feature-posterior đã tồn tại:

- Parviainen & Koivisto, ECML-PKDD 2011: ancestor relations khi có biến ẩn; báo cáo rằng averaging tốt hơn MAP.
- Chen, Meng, Tian, AISTATS 2015 ([PMLR](https://proceedings.mlr.press/v38/chen15e.html)): exact posterior của ancestor relations, chỉ cho DAG.
- arXiv [1909.03818](https://arxiv.org/pdf/1909.03818): posterior của local causal structures với DMAG Gaussian.
- BCCD (CI03): Bayesian score trên local structures.

**Hệ quả:** ở arm **Gaussian**, A′ có thể bị lấn át bởi baseline "forced-feature BIC/likelihood-ratio" (§3, Mệnh đề P5 cho thấy D(f) chính là một GLR trong xấp xỉ Gaussian của z). **Niche có thể bảo vệ dịch sang:** CI statistics **tổng quát, tiệm cận chuẩn**, nơi không có full likelihood: kernel/GCM tests, mixed data, nonparanormal. Ở đó Σ̂ lấy bằng bootstrap hoặc influence function. Đây là thay đổi định vị quan trọng nhất của phiên này.

---

## Phần 2 — Thiết lập

- **Queries:** Q = {q_1, …, q_K}, q_k = (X_k ⊥ Y_k | S_k).
- **Statistics:** vector z ∈ R^K (ví dụ Fisher-z z_k = √(n−|S_k|−3) · atanh ρ̂_k).
- **Population counterpart:** ζ_n = E-scaled version, ζ_{n,k} = √(n−|S_k|−3) · atanh ρ_k.
- **(A1) Asymptotic normality:** z − ζ_n ⇒ N(0, Σ), Σ xác định dương (PD) trên các query không trùng lặp, và có Σ̂ → Σ in probability. [Inference: với partial correlations Gaussian, Σ thu được qua delta method trên sample covariance; với test tổng quát, Σ̂ lấy bằng bootstrap. Chưa chứng minh độc lập trong phiên này.]
- **Model family:** M hữu hạn (MAGs/ancestral structures). Mỗi m ∈ M cho pattern π(m) ∈ {0,1}^K, với π_k = 1 ⇔ X_k và Y_k m-separated bởi S_k trong m.
- **(A2) Faithfulness + beta-min trên Q:** mô hình đúng m* ∈ M; π_k(m*) = 1 ⇒ ρ_k = 0; π_k(m*) = 0 ⇒ |atanh ρ_k| ≥ η > 0.
- **Ngưỡng:** δ_{n,k} := √(n−|S_k|−3) · η.
- **Vùng tương thích:** R_n(m) := { z' ∈ R^K : z'_k = 0 nếu π_k(m) = 1; |z'_k| ≥ δ_{n,k} nếu π_k(m) = 0 }. Đây là tập đóng, hợp của 2^{#dep} đa diện.
- **Với M' ⊆ M:** R_n(M') := ∪_{m∈M'} R_n(m), một hợp hữu hạn của tập đóng, nên cũng đóng.
- **Khoảng cách:** với ma trận PD W, ‖v‖_W := √(vᵀ W⁻¹ v) và dist_W(z, R) := inf_{z'∈R} ‖z − z'‖_W.
- **Feature f** (ví dụ "X là ancestor của Y"): M_f = {m : m ⊨ f}, M_¬f = M \ M_f.
- **Score:** D_W(f) := dist_W(z, R_n(M_¬f))² − dist_W(z, R_n(M_f))². Đây là dạng hiệu, song song với ACI Eq. 16.
- **Định nghĩa phụ:** f gọi là **Q-identifiable** nếu mọi m với π(m) = π(m*) đều thỏa f.

---

## Phần 3 — Mệnh đề và chứng minh rút gọn

### P1 (Oracle soundness). Giả sử (A2), z = ζ_n (không nhiễu) và n cố định. Khi đó:
(i) nếu f Q-identifiable thì D(f) > 0; (ii) nếu ¬f Q-identifiable thì D(f) < 0; (iii) nếu cả M_f và M_¬f đều chứa mô hình có pattern π(m*) thì D(f) = 0.

**Chứng minh.**
- **Bổ đề:** ζ_n ∈ R_n(m) ⇔ π(m) = π(m*).
  - (⇐) Theo (A2), các tọa độ independent của ζ_n bằng 0, các tọa độ dependent có |ζ_{n,k}| ≥ δ_{n,k}.
  - (⇒) Nếu π_k(m) = 1 thì cần ζ_{n,k} = 0. Điều này loại π_k(m*) = 0, vì khi đó |ζ_{n,k}| ≥ δ_{n,k} > 0. Nếu π_k(m) = 0 thì cần |ζ_{n,k}| ≥ δ_{n,k} > 0. Điều này loại π_k(m*) = 1, vì khi đó ζ_{n,k} = 0.
- (i): mọi m ∈ M_¬f có π(m) ≠ π(m*), nên ζ_n ∉ R_n(M_¬f). Tập này đóng và ‖·‖_W là chuẩn, nên khoảng cách > 0. Trong khi đó m* ∈ M_f, nên khoảng cách tới R_n(M_f) bằng 0. Suy ra D > 0.
- (ii) đối xứng với (i). (iii): cả hai khoảng cách đều bằng 0. ∎

### P2 (Asymptotic consistency). Giả sử (A1), (A2) và f Q-identifiable. Khi đó D_{Σ̂}(f) → +∞ in probability, với tốc độ ít nhất bậc n.

**Chứng minh.**
- **(a) Lipschitz.** Với mọi tập R và mọi z, ζ: |dist_W(z,R) − dist_W(ζ,R)| ≤ ‖z − ζ‖_W. Đây là bất đẳng thức tam giác cho khoảng cách điểm–tập.
- **(b) Chặn dưới tại ζ_n.** Lấy m ∈ M_¬f. Có một tọa độ k với π_k(m) ≠ π_k(m*).
  - Nếu π_k(m) = 1 và π_k(m*) = 0: mọi z' ∈ R_n(m) có z'_k = 0, nên |ζ_{n,k} − z'_k| ≥ δ_{n,k}.
  - Nếu π_k(m) = 0 và π_k(m*) = 1: ζ_{n,k} = 0, nên |ζ_{n,k} − z'_k| = |z'_k| ≥ δ_{n,k}.
  - Trong cả hai trường hợp, ‖ζ_n − z'‖_W ≥ λ_max(W)^{−1/2} · |ζ_{n,k} − z'_k| ≥ λ_max(W)^{−1/2} · δ_{n,k} = Θ(√n).
  - M hữu hạn, nên dist_W(ζ_n, R_n(M_¬f)) ≥ c√n.
- **(c) Kết hợp.** ‖z − ζ_n‖_{Σ̂} = O_p(1), vì Σ̂ → Σ PD và có (A1). Từ (a):
  - dist(z, R_n(M_¬f)) ≥ c√n − O_p(1);
  - dist(z, R_n(M_f)) ≤ dist(ζ_n, R_n(m*)) + O_p(1) = O_p(1).
  - Bình phương rồi lấy hiệu: D ≥ c²n − O_p(√n) → ∞.
- Thay W = Σ̂ cho W = Σ chỉ đổi các hằng số, nhờ λ(Σ̂) bị chặn trong một khoảng compact w.p. → 1. ∎

*Ghi chú.* P1–P2 là bản tương tự của ACI Theorems 1–2. Chúng là **điều kiện cần (sanity)**, **không** phải novelty.

### P3 (Exact diagonal reduction — "không có off-diagonal thì không có gì mới"). Nếu W = diag(w_1, …, w_K) thì tồn tại các trọng số a_k(z_k) ≥ 0 và quyết định ŝ_k(z_k) ∈ {0,1}, mỗi cái **chỉ phụ thuộc z_k**, sao cho với mọi m:

dist_W(z, R_n(m))² = Σ_k a_k(z_k) · 1[π_k(m) ≠ ŝ_k(z_k)] + B(z),

trong đó B(z) không phụ thuộc m. Do đó D_W(f) **trùng với ACI C(f)** (Eq. 16) dùng các weights a_k.

**Chứng minh.**
- W chéo và R_n(m) là tích Descartes của các tập một chiều ({0} hoặc (−∞, −δ] ∪ [δ, ∞)), nên bài toán inf tách theo tọa độ: dist² = Σ_k c_k(z_k, π_k(m)) / w_k.
- Ở đây c_k(z, 1) = z² và c_k(z, 0) = (δ_{n,k} − |z|)₊².
- Đặt B_k = min(c_k(z_k,0), c_k(z_k,1)) / w_k, ŝ_k = argmin, và a_k = |c_k(z_k,1) − c_k(z_k,0)| / w_k.
- Khi đó mỗi số hạng bằng B_k + a_k · 1[π_k(m) ≠ ŝ_k].
- min_{m∈M'} bảo toàn hằng số cộng B = Σ_k B_k, nên B triệt tiêu trong hiệu D.
- Kết quả đúng là dạng loss của ACI (Eq. 13), với "test decision" ŝ_k là ngưỡng |z_k| = δ_{n,k}/2. ∎

### P4 (Non-separability khi có off-diagonal). Xét K = 2 và Σ = [[1, r], [r, 1]] với 0 < |r| < 1. Lấy m_a với π = (1,1) và m_b với π = (1,0). Giả sử ràng buộc |·| ≥ δ không active. Khi đó:

dist²(z, R(m_a)) − dist²(z, R(m_b)) = (z_2 − r·z_1)² / (1 − r²).

Đại lượng này phụ thuộc z_1. Vì vậy **không** tồn tại họ trọng số per-test "a_k chỉ phụ thuộc z_k" nào tái tạo được hiệu này. Lý do: trong mọi loss dạng ACI, hiệu giữa hai mô hình chỉ khác nhau ở q_2 bằng ±a_2(z_2), chỉ là hàm của z_2.

**Chứng minh.**
- R(m_a) = {0}, nên dist² = zᵀΣ⁻¹z = (z_1² − 2r·z_1·z_2 + z_2²)/(1 − r²).
- R(m_b) = {(0, t) : |t| ≥ δ}. Cực tiểu của (z − (0,t))ᵀ Σ⁻¹ (z − (0,t)) theo t đạt tại t* = z_2 − r·z_1. Đây là regression của tọa độ 2 theo tọa độ 1. Giá trị cực tiểu là z_1², hợp lệ khi |t*| ≥ δ.
- Lấy hiệu hai biểu thức, ta được công thức trên. Vì ∂/∂z_1 của hiệu bằng −2r(z_2 − r·z_1)/(1 − r²), khác 0 tổng quát, nên hiệu thực sự phụ thuộc z_1. ∎

**Diễn giải (đây là insight trung tâm của A′):** evidence mà q_2 đóng góp để phân biệt m_a với m_b là z_2 **sau khi loại phần dự đoán được từ z_1**. Nói cách khác, đó là thống kê điều kiện z_2 | z_1 ~ N(r·z_1, 1 − r²). ACI cộng z_2 như evidence độc lập, nên nó **đếm lại** phần nhiễu mà q_2 chia sẻ với q_1. Hiệu chỉnh "thay weights" kiểu GLS không làm được việc này, vì whitening không bảo toàn cấu trúc tích của các vùng R(m). **[Open]** Mở rộng P4 cho K tổng quát (khối 2×2 nhúng trong các mô hình chỉ khác nhau ở một query) là trực tiếp nếu ràng buộc không active. Trường hợp active cần xét theo từng mảnh đa diện.

### P5 (Duplicate invariance; ACI không có tính chất này). Giả sử q_{K+1} là **bản sao byte-identical** của q_K: cùng statistic, nên Σ⁺ suy biến với hai hàng/cột trùng nhau. Định nghĩa ‖v‖² = vᵀ Σ⁺ v nếu v ∈ range(Σ), và +∞ nếu không. Khi đó D(f) trên Q ∪ {q_{K+1}} **bằng đúng** D(f) trên Q. Ngược lại, ACI với weights per-test **cộng hai lần** weight của q_K, nên C(f) thay đổi khi q_K có mặt trong một proof phân biệt f.

**Chứng minh.**
- Gọi L ∈ R^{(K+1)×K} là ma trận nhân bản tọa độ K (full column rank), z = L·y và Σ = L·Σ_r·Lᵀ.
- Khoảng cách hữu hạn đòi hỏi z' ∈ z + range(Σ) = range(L), nên z' = L·y'.
- Vì π_{K+1}(m) = π_K(m) (cùng một statement), R(m) ∩ range(L) = L·R_r(m).
- Vì LΣ_r có full column rank và Lᵀ có full row rank, (LΣ_rLᵀ)⁺ = (Lᵀ)⁺ Σ_r⁻¹ L⁺. Suy ra Lᵀ (LΣ_rLᵀ)⁺ L = Σ_r⁻¹, dùng L⁺L = I và Lᵀ(Lᵀ)⁺ = I.
- Do đó ‖L(y − y')‖² = (y − y')ᵀ Σ_r⁻¹ (y − y'). ∎

*Lưu ý trung thực.* Trường hợp byte-identical có thể sửa tầm thường bằng dedup. Giá trị thực của A′ nằm ở **near-duplicates** (0 < r < 1, P4). **[Open]** D có liên tục khi r → 1 hay không phụ thuộc dữ liệu (dạng 0/0 trong P4), nên **không được claim liên tục**.

### P6 (Diễn giải GLR, chỉ trong xấp xỉ Gaussian). Nếu z ~ N(ζ, Σ) đúng chính xác thì dist_Σ(z, R(M'))² = −2 · max_{ζ'∈R(M')} log φ_Σ(z − ζ') + const. Do đó D(f) là **generalized likelihood ratio statistic** của H_f : ζ ∈ R(M_f) so với H_¬f : ζ ∈ R(M_¬f), với dữ liệu là vector z.

**Chứng minh.** Thay vào mật độ Gaussian; hằng số chuẩn hóa triệt tiêu trong hiệu. ∎

**Hệ quả:**
- (a) Calibration của D có thể được nghiên cứu qua lý thuyết chi-bar-square trên hợp các cone. **[Open; đây là extension, không phải entry ticket.]**
- (b) Ở arm Gaussian, D là một GLR **trên thống kê đã nén z**, không phải trên dữ liệu đầy đủ. Vì vậy forced-feature full-likelihood ratio (§1.3) là đối thủ trực tiếp, và về nguyên tắc có thể hiệu quả hơn khi mô hình đúng. **[Inference]** Đó là lý do niche phải là CI statistics tổng quát.

### P7 (Search gap là anti-conservative). Nếu chỉ tìm trên M̃_¬f ⊂ M_¬f thì dist(z, R(M̃_¬f)) ≥ dist(z, R(M_¬f)). Do đó score tính được **≥** score thật, tức **tự tin quá mức**.

**Chứng minh.** Inf trên tập con lớn hơn hoặc bằng inf trên tập lớn. ∎

**Nghĩa vụ thiết kế:** mọi approximation phải báo cáo search gap, hoặc dùng cận dưới (ví dụ relaxation lồi của hợp các đa diện).

### Tóm tắt những gì đã và chưa chứng minh

| Mệnh đề | Trạng thái | Vai trò |
|---|---|---|
| P1 oracle soundness | Chứng minh rút gọn | Sanity, không phải novelty |
| P2 consistency | Chứng minh rút gọn, dưới (A1)–(A2) | Sanity |
| P3 diagonal ⇒ ACI | Chứng minh, exact | Xác định ranh giới novelty |
| P4 off-diagonal ⇒ không separable | Chứng minh cho K=2, ràng buộc inactive; K tổng quát **[Open]** | **Cơ chế trung tâm** |
| P5 duplicate invariance | Chứng minh | Phân biệt với ACI (yếu, vì dedup có thể sửa) |
| P6 GLR | Chứng minh trong xấp xỉ Gaussian | Diễn giải; mở đường calibration **[Open]** |
| P7 search gap | Chứng minh | Nghĩa vụ thiết kế |
| (A1) cho kernel/GCM tests, Σ̂ bootstrap consistency | **[Open]**, dựa vào literature từng test | Điều kiện để niche có thể bảo vệ |
| Lợi ích về ranking/risk–coverage | **[Hypothesis]** — toán **không** chứng minh được điều này | Phải đo bằng pilot |
| Tính toán exact dist(z, R(m)) | Hợp 2^{#dep} QP; exact chỉ khi K nhỏ | Feasibility |

---

## Phần 4 — Cập nhật quyết định cho A′

1. **Gap còn sống sau Guo–Wu–Yiu** [Verified-full]. Paper đó về effect inference, dùng selection-event polyhedra, và không có feature score.
2. **Gap còn sống sau BSC-D nhưng hẹp hơn và phải định vị lại** [Verified-full, `docs/papers/bscd.pdf`].
   - BSC-D mô hình dependence của **quyết định nhị phân** trên discrete data, ở cấp chọn PAG.
   - Paper báo cáo dependence **không thay đổi thứ tự PAG và không thay đổi SHD**, và tác giả phỏng đoán BSC-I bị miscalibrated (lập luận naive Bayes).
   - Vì vậy hypothesis chính của A′ chuyển từ ranking sang **calibration/error rate tại ngưỡng cố định ở cấp feature** (H-cal). H-rank chỉ là phụ.
   - Phải thêm baseline Triantafillou et al., PGM 2014.
3. **Cơ chế có nội dung toán học thật** (P3–P4): novelty nằm hoàn toàn ở off-diagonal và có diễn giải rõ ("đếm evidence một lần" = thống kê điều kiện).
4. **Đe dọa mới (§1.3):** full-likelihood feature posteriors và forced-feature BIC/LR làm A′ yếu ở arm Gaussian thuần. **Định vị lại:** *dependence-aware feature confidence cho constraint-based discovery với các CI statistics tổng quát (kernel/GCM/mixed)*. Gaussian chỉ là arm kiểm chứng nơi đáp án full-likelihood được biết.
5. **Baselines bắt buộc bổ sung:** (i) forced-feature Gaussian MAG BIC/LR, tức full likelihood; (ii) BSC-D-ACI; (iii) Bayesian ancestor-relation posterior ở quy mô nhỏ nếu có implementation.
6. **Kill test cập nhật (chưa chạy):**
   - (a) **Gaussian arm:** nếu D(f) không tiến gần forced-feature LR **và** không vượt ACI thì dừng.
   - (b) **Nonparametric arm** (GCM test, Σ̂ bootstrap, p ≤ 5):
     - **Primary metric (H-cal):** false ancestry assertion rate tại một ngưỡng cố định định trước, và calibration (Brier/ECE nếu score được chuyển thành xác suất). Đo **theo mức dư thừa** của query universe (minimal vs redundant).
     - **Secondary (H-rank):** Kendall τ và risk–coverage AUC so với ACI, BSC-D-ACI và Triantafillou et al.
     - **No-go** nếu không có lợi ích calibration ở ≥ 2 regime chồng lấp. Lợi ích chỉ ở ranking, khi calibration không đổi, không đủ.
7. **Trạng thái:** vẫn **Conditional (primary)**, nhưng **độ tin vào H-rank giảm**, vì BSC-D không thấy hiệu ứng ở argmax.
   - Lý do giữ: cơ chế khác BSC-D ở ba điểm có thể kiểm chứng: thống kê liên tục; dependence phía independence không biến mất tiệm cận; target là calibration theo feature. BSC-D chưa đo calibration.
   - Bước rẻ nhất tiếp theo: một **thí nghiệm trên giấy/mô phỏng nhỏ** cho H-cal. Lấy hai feature, một dựa trên các test gần dư thừa và một dựa trên các test độc lập, cùng magnitude, rồi so sánh ACI C(f) với D(f) dưới null. Sau đó chạy kill test (b).
