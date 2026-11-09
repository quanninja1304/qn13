# RG1 — Chứng minh đầy đủ cho R1, tính đơn điệu của R2 và điều kiện power

> Ngày 2026-11-04. Gate **RG1** của `A1_pilot_readiness.md` §9: chứng minh R1 (rank-aware, seminorm, χ²_rank, Σ ước lượng, Q cố định, η_n pointwise), độ đơn điệu của η*(f), điều kiện để T(f) có power.
> Kiểm chứng số: `RG1_numeric_checks.py`, `RG1_numeric_outputs.json`, `RG1_numeric_run_log.txt`; sau rà soát: `RG1_followup_checks.py`, `RG1_followup_outputs.json`, `RG1_followup_run_log.txt`. **Đây không phải RG2 và không phải pilot nhân quả.**
> **Nhãn:** [Proved] có chứng minh đầy đủ trong tài liệu này. [Source-verified] đã đọc từ nguồn trong phiên này. [Sketch] mới có lập luận phác thảo. [Inference] suy luận chưa kiểm chứng đầy đủ. [Hypothesis]. [Open]. [ABSTRACT] chỉ đọc tóm tắt hoặc qua nguồn thứ cấp.
> **Người viết là agent.** Đã có một lượt rà soát độc lập bởi agent AI ngữ cảnh mới (`RG1_independent_review_vi.md`): `PASS WITH CORRECTIONS`. Tài liệu này là **bản đã sửa theo lượt đó** (§12). Bản sửa chưa được rà lại, và chưa có người rà. User đã duyệt RG1 là PASS có điều kiện ngày 2026-11-05 (§10.3).

---

## 0. Kết luận

**Phán quyết: các định lý trung tâm đứng được qua một lượt rà soát độc lập bởi agent AI, nhưng R1 phải đổi định nghĩa, và một số kết luận trước đây đã bị thu hẹp. Chưa có bằng chứng R1 đáng dùng.**

| Hạng mục của RG1 | Kết quả | Trạng thái |
|---|---|---|
| Joint CLT, Σ dạng đóng, rank | Lemma 1, Mệnh đề 2 | Proved + số + rà soát |
| Validity với Σ̂, rank-aware, η_n pointwise | Thm 1, Thm 2, Hệ quả 3.1 | Proved + số + rà soát |
| Validity đều, không cần ước lượng rank | Thm 3 (ridge + χ² có trọng số), điều kiện nλ_n → ∞ | Proved + số + rà soát; p, K cố định |
| Seminorm toàn cục + χ²_rank của contract §7 | **Valid nhưng T(f) ≡ 0 khi M_¬f chứa mô hình mù** (Thm 4). Ở p = 4, K = 24: 178/185 pattern mù, và 24/24 feature không chứng nhận được ngay khi M chứa DAG 2 cạnh | **Bác bỏ làm thủ tục** |
| Điều kiện power | Thm 5, Mệnh đề 4, 5, 8 | Proved + rà soát |
| Đơn điệu của R2 và ngữ nghĩa | Thm 7 | Proved + rà soát |
| Kiểm tra độc lập | Một lượt bởi agent AI: `PASS WITH CORRECTIONS` (§12) | Chưa có người rà; user duyệt PASS có điều kiện 2026-11-05 |

**Những điều thay đổi so với trước RG1:**

1. **Không dùng seminorm toàn cục.** Null Σ là các hướng thống kê không dao động, nhưng seminorm cho đi miễn phí theo các hướng đó, và vùng R_n ⊋ A_n có sẵn điểm để đi tới. Điều kiện đúng là (B1)–(B2), không phải "K > rank". Seminorm theo khối riêng từng mô hình thì không mù và là ứng viên còn mở (Hệ quả 4.1(e)).
2. **Metric ridge với ngưỡng χ² có trọng số** valid đều trên tập compact của ma trận tương quan khi p, K cố định, và T(f) → ∞ cho mọi feature đúng Q-identifiable (với quy tắc abstain: liminf P(assert) ≥ 1−α). **Σ⁻¹ oracle không đều**: đuôi đo được 0.765 ở mức 0.05 gần điểm rớt rank, trong khi ridge giữ khoảng 0.05 trên cùng đường đó.
3. **Ridge có giới hạn hữu hạn mẫu nặng khi K lớn.** Với λ = n^{-1/3}, P(W_n > ĉ_n) là 0.12 (K = 70, n = 200), 0.22 (K = 165), 0.66 (K = 616). λ phải khai báo theo K. FWER thật ở K = 70 vẫn dưới α trên các kịch bản đã đo (cận trên tối đa 0.052), vì P(W_n > ĉ_n) chỉ là cận trên của nó (§8.2).
4. **"Valid pointwise" không phải điểm mạnh.** Trong lớp η ≤ β, thresholding đơn giản đạt FWER → 0 và power → 1 (Mệnh đề 7). Regime duy nhất **trong lớp đó** mà R1 có thể có nội dung là √nη < 2t_K. **Khi η > β thì không còn bảo đảm:** FWER của R1 tới 0.91 ở cỡ mẫu vừa, dù C_n rỗng dần khi n lớn; khả năng tự phát hiện này BL1 cũng có.
5. **Ngưỡng chiếu χ²_r bị trội** bởi ngưỡng valid theo từng mô hình (c̄_m ≤ ĉ_n, Thm 6(c)). Công thức "R² quyết định" đã bị thu hẹp: lợi từ R² yếu đi dưới metric ridge, và không phải của riêng χ² (Mệnh đề 8).
6. **η*(f) phải đi kèm cận trên η̄** (Thm 7c). Bảo đảm cuối cùng có dạng: với xác suất ≥ 1 − α − o(1), đồng thời cho mọi f, "f đúng, hoặc phụ thuộc yếu nhất của m* không vượt η*(f)".

**Không suy ra được từ RG1:** R1 có power hơn baseline valid hay không. **Chưa có kịch bản nào cho thấy đồng thời CT vượt α và R1 có power dương** (§5). RG2 chưa chạy. Novelty vẫn hẹp: kỹ thuật lõi là regularized Wald, test inversion, minimum-discrepancy đã có (§9).

---

## 1. Thiết lập

### 1.1 Dữ liệu và query

**(G)** V₁,…,V_n i.i.d. N_p(μ, C), C xác định dương (PD); R là ma trận tương quan của C.
**(Q)** Q = {q_k = (X_k, Y_k | S_k)}_{k≤K}, họ MAG M và họ feature F được cố định trước dữ liệu (hoặc chọn trên mẫu độc lập, Hệ quả 3.3). p, K cố định khi n → ∞; n > p và n > max|S_k| + 3.

Với C̃ PD: C̃_{ab·S} = C̃_ab − C̃_aS C̃_SS⁻¹ C̃_Sb; ρ_k(C̃) = C̃_{XY·S}/√(C̃_{XX·S} C̃_{YY·S}); g_k = atanh ρ_k. Các g_k bất biến theo scale: g_k(DC̃D) = g_k(C̃) với D chéo dương.

Ĉ là hiệp phương sai mẫu. Đặt n_k = n − |S_k| − 3, θ_k = g_k(C), và

  z_k = √n_k · g_k(Ĉ),  ζ_{n,k} = √n_k · θ_k.

### 1.2 Mô hình, vùng và giả định

π_k(m) = 1 nếu X_k, Y_k m-separated bởi S_k trong m. I(m) = {k : π_k(m) = 1}, D(m) là phần bù. Với η ≥ 0:

  R_n^η(m) = { u ∈ R^K : u_k = 0 (k ∈ I(m));  |u_k| ≥ √n_k · η (k ∈ D(m)) }.

**(M)** (P, m*) là *Q-Markov*: m* ∈ M và θ_k = 0 với mọi k ∈ I(m*).
**β(P, m*)** = min_{k∈D(m*)} |θ_k| (= +∞ nếu D(m*) rỗng).
**(F)** *Q-faithful*: (M) và β(P, m*) > 0.

**Bổ đề 0.** ζ_n ∈ R_n^η(m*) ⇔ (M) và η ≤ β(P, m*). [Proved: ζ_{n,k} và ngưỡng cùng hệ số √n_k.]

**Ngữ nghĩa nhân quả.** Nếu P là marginal trên V của SCM Gaussian tuyến tính với DAG G, latent L, không selection, và m* = G[^∅_L] (MAG), thì (M) suy từ global Markov của DAG (d-separation ⇒ CI ⇒ θ_k = 0 với Gaussian) cùng Richardson–Spirtes 2002, Theorem 4.18 (Im(G)[^S_L] = Im(G[^S_L])). Quan hệ tổ tiên được bảo toàn theo Corollary 4.8 (ant_G(α) \ L = ant_{G[^∅_L]}(α)); corollary này nói về anterior, nhưng G là DAG và S = ∅ nên không có cạnh vô hướng, do đó anterior = ancestor [Source-verified]. Với selection, Lemma 4.7 chỉ cho bao hàm, nên **selection nằm ngoài phạm vi** định lý về feature tổ tiên ở đây.

**Feature** là ánh xạ bất kỳ f : M → {0,1}; M_f, M_¬f như contract. f gọi là *Q-identifiable* nếu π(m) = π(m*) ⇒ f(m) = f(m*).

### 1.3 Thống kê và thủ tục

Σ̂ := Σ(Ĉ), với Σ(·) dạng đóng ở (2.1). Với Ω̂ PSD (phụ thuộc dữ liệu):

  d²_η(z, m) = inf_{u∈R_n^η(m)} (z−u)ᵀ Ω̂ (z−u),  W_n = (z−ζ_n)ᵀ Ω̂ (z−ζ_n),
  T^η(f) = min_{m∈M_¬f} d²_η(z, m) (min ∅ = +∞),  C_n(η) = { m ∈ M : d²_η(z, m) ≤ ĉ_n }.

**Quy tắc R1.** Assert f ⇔ C_n(η) ≠ ∅ và T^η(f) > ĉ_n, tức ∅ ≠ C_n(η) ⊆ M_f. Khi C_n(η) = ∅ (mọi mô hình bị bác bỏ) thì **abstain**: contract v2 không nêu quy ước này, và thiếu nó thì cả f lẫn ¬f đều được "assert". Feature có M_¬f = ∅ là *vacuous*, không tính vào power.

Ba lựa chọn (σ̂₁ ≥ … ≥ σ̂_K ≥ 0 là trị riêng của Σ̂):

| Mã | Ω̂ | ĉ_n | Tham số |
|---|---|---|---|
| **V0** pinv thường | Σ̂⁺ | χ²_{rank Σ̂, 1−α} | — |
| **V1** cắt cứng (quy ước C-c của contract, viết chặt) | Σ_{σ̂_j>τ_n} σ̂_j⁻¹ û_j û_jᵀ | χ²_{r̂, 1−α}, r̂ = #{j : σ̂_j > τ_n} | τ_n → 0, nτ_n → ∞ |
| **V2** ridge + χ² có trọng số | (Σ̂ + λ_n I)⁻¹ | q_{1−α}(Σ_j ŵ_j g_j²), ŵ_j = σ̂_j/(σ̂_j + λ_n), g_j i.i.d. N(0,1) | 0 < λ_n ≤ λ̄, nλ_n → ∞ |

V2 cho phép cả λ cố định lẫn λ_n → 0.

---

## 2. Joint CLT, Σ dạng đóng, rank

**Lemma 1 (tuyến tính hóa).** [Proved] Dưới (G), gọi e_X^k, e_Y^k là residual chuẩn hóa (phương sai 1) của X_k, Y_k khi hồi quy tuyến tính lên S_k, và

  ψ_k(V) = [ e_X^k e_Y^k − (ρ_k/2)((e_X^k)² + (e_Y^k)²) ] / (1 − ρ_k²).

Khi đó z − ζ_n = G_n + B_n, với G_n = n^{-1/2} Σ_i ψ(V_i), E ψ = 0, ‖B_n‖ = O_p(n^{-1/2}). Hơn nữa Σ := Cov ψ có **đường chéo đơn vị** và, với a = Cov(e_X^k, e_X^l), b = Cov(e_X^k, e_Y^l), c = Cov(e_Y^k, e_X^l), d = Cov(e_Y^k, e_Y^l):

  (2.1) Σ_kl = [ (ad + bc) − ρ_l(ac + bd) − ρ_k(ab + cd) + ½ρ_kρ_l(a² + b² + c² + d²) ] / [ (1−ρ_k²)(1−ρ_l²) ].

Nếu R chạy trong tập compact 𝓚 các ma trận tương quan PD, các O_p đều theo R ∈ 𝓚, và ‖Σ̂ − Σ‖ = O_p(n^{-1/2}) đều theo R ∈ 𝓚.

*Chứng minh.* Do bất biến, giả sử μ = 0, C = R.
(a) Vi phân của Schur complement theo hướng H là (e_a − β_a)ᵀ H (e_b − β_b), với β_a = C_SS⁻¹C_Sa đặt trên tọa độ S. Lấy H = vvᵀ − C và r_a = (e_a − β_a)ᵀv, ta được r_a r_b − C_{ab·S}.
(b) Quy tắc chuỗi cho ρ = C_{XY·S}/√(C_{XX·S}C_{YY·S}) cho e_Xe_Y − ρ − (ρ/2)(e_X² − 1 + e_Y² − 1) = e_Xe_Y − (ρ/2)(e_X² + e_Y²). Chia cho 1 − ρ² để được đạo hàm của atanh. Vậy ψ_k(v) = ⟨H_k, vvᵀ − R⟩ với H_k = ∇g_k(R) đối xứng.
(c) Ĉ − R = (n⁻¹ΣV_iV_iᵀ − R) − V̄V̄ᵀ (hệ số chia không ảnh hưởng vì g_k bất biến scale). Trên {‖Ĉ − R‖ ≤ ε}, với ε < ½ min_{𝓚} λ_min, khai triển Taylor bậc hai có phần dư ≤ L‖Ĉ − R‖², L chỉ phụ thuộc 𝓚. Vì E‖n⁻¹ΣV_iV_iᵀ − R‖² ≤ c/n, phần dư và √n V̄V̄ᵀ đều là O_p(n^{-1/2}). Cuối cùng √(n_k/n) = 1 + O(1/n).
(d) (2.1) là Isserlis cho bốn biến Gaussian đơn vị với c₁₂ = ρ_k, c₃₄ = ρ_l. Với k = l: a = d = 1, b = c = ρ, tử số = (1 − ρ²)², nên Σ_kk = 1.
(e) Σ(·) là hàm trơn (hữu tỉ và căn bậc hai của các đại lượng dương), mẫu số bị chặn khỏi 0 trên lân cận compact của 𝓚, nên Lipschitz. ∎

**Hệ quả.** Vì ψ(V) ∈ range Σ h.c.c., G_n ∈ range Σ. Do đó, với P là phép chiếu lên range Σ:

  (2.2) (I − P)(z − ζ_n) = (I − P)B_n = O_p(n^{-1/2}).

Phần lệch khỏi range **khác 0 nhưng cấp n^{-1/2}**. Đó là lý do quy ước support C-b gán +∞ cho mô hình đúng (CE2), và là nguồn của điều kiện nλ_n → ∞ ở Thm 3.

**Mệnh đề 2 (rank).** [Proved] Dưới (G), đặt d = p(p−1)/2.
(i) Σ_kl = 2 tr(H_k C H_l C), nên **rank Σ = dim span{H₁,…,H_K}**.
(ii) rank Σ ≤ min(K, d).
(iii) Nếu Q chứa mọi query biên (S = ∅, mọi cặp) thì **rank Σ = d tại mọi C**.
(iv) Khi Q không chứa một chart như vậy, rank có thể rớt trên tập con giải tích thực sự. Ví dụ Q₂ = {X⊥Y, X⊥Y|Z} tại ρ_XY = ρ_YZ = 0, ρ_XZ = a có Σ₁₂ = √(1−a²) (R′ của contract), rớt về rank 1 khi a = 0.
(v) rank Σ̂ h.c.c. bằng rank tổng quát r_gen = max_C rank Σ(C).

*Chứng minh.* (i) Var⟨H, vvᵀ⟩ = 2 tr(HCHC) = 2‖C^{1/2}HC^{1/2}‖²_F (Isserlis), là tích vô hướng PD trên ma trận đối xứng; Σ là ma trận Gram của các H_k. (ii) Bất biến scale cho ⟨H_k, DC + CD⟩ = 0 với mọi D chéo; D ↦ DC + CD đơn ánh (đường chéo là 2D_iiC_ii), nên H_k nằm trong không gian linh hóa tử chiều p(p+1)/2 − p = d. (iii) Tại C = R, đạo hàm của atanh ρ_ij theo hướng E_ab + E_ba bằng 1[(a,b)=(i,j)]/(1−ρ_ij²), nên các H_ij độc lập tuyến tính. (v) Các định thức con là hàm giải tích trên nón PD liên thông; Ĉ có mật độ khi n > p. ∎

**Mệnh đề 3 (V0 sai tại điểm rớt rank).** [Proved dựa trên định lý nguồn] Lấy Q₂, C = I₃. Khi đó, với U, U′ ~ N(0,1) độc lập,

  W_n^{V0} ⇒ U² + ¼U′²,  **không phải χ²₂**.

*Chứng minh.* Đặt u = √n ρ̂_XY, v = √n ρ̂_YZ, w = √n ρ̂_XZ, hội tụ về i.i.d. N(0,1). Từ công thức ρ_XY·Z: (z₁+z₂)/2 = u + o_p(1) và √n(z₁−z₂) = wv + o_p(1). Thay vào (2.1) tại Ĉ, các số hạng u²/n triệt tiêu và 1 − Σ̂₁₂ = (w²+v²)/(2n)·(1+o_p(1)). Với đường chéo đơn vị, trong cơ sở (1,1)/√2, (1,−1)/√2:

  W_n^{V0} = (z₁+z₂)²/(2(1+Σ̂₁₂)) + (z₁−z₂)²/(2(1−Σ̂₁₂)) ⇒ u² + w²v²/(w²+v²) (ánh xạ liên tục ngoài tập w = v = 0 có xác suất 0).

Số hạng cuối là W_{f,I} với f(x) = x₁x₂, phân phối ¼χ²₁ theo Glonek/Drton–Xiao 2016, Theorem 2.3 [Source-verified, arXiv v2], và độc lập với u. ∎

Điều này **giải thích định lượng** con số "plug-in bảo thủ" 0.018 / 0.014 của toy Day-2 (§8).

**Nhưng V0 không phải lúc nào cũng bảo thủ, và ngay cả nghịch đảo của Σ thật cũng hỏng.** [Derived, cùng khai triển; khớp số ở §8.1] Khi Σ PD nhưng trị riêng nhỏ cỡ 1/n, nó cùng bậc với sai số bậc hai mà Σ bậc một bỏ qua. Đặt U ~ N(0,1):
- Đường a = c/√n, b = 0 (w ~ N(c,1), v ~ N(0,1)): oracle (z−ζ_n)ᵀΣ⁻¹(z−ζ_n) ⇒ U² + (wv/c)². Đuôi tại χ²_{2,.95} là **0.1247** ở c = 1 và tăng tới 0.77 ở c = 0.05, tức **sup → 1**. V0 ⇒ U² + (wv)²/(w²+v²), đuôi 0.0187 ở c = 1.
- Đường a = b = c/√n, ρ_XY = c²/n (w, v ~ N(c,1)): V0 ⇒ U² + (wv−c²)²/(w²+v²), đuôi **0.0605** ở c = 1 và **0.0898** ở c = 1.5. Ở c = 1, oracle ⇒ U² + (wv−1)²/2, đuôi **0.0904** (Var(wv−1) = 3, trong khi Σ bậc một tính ra 2).

Tổng quát, Wald suy biến có thể under- hoặc over-reject tùy cấu trúc (Dufour–Renault–Zinde-Walsh, arXiv 1312.0569 v1, tr. 4–5 [Source-verified phần mở đầu]), nên **V0 không có bảo đảm** khi rank rớt hoặc gần rớt. Theo mô tả của Dufour–Valéry (WP 2011, tr. 1), điều kiện để g-inverse giữ giới hạn χ² là rank Σ̂ = rank Σ với xác suất → 1 (Andrews 1987 [ABSTRACT]). Khi Q chứa mọi query biên, điều kiện này luôn đúng và V0 = V1 tại τ_n đủ nhỏ.

---

## 3. Validity

**Định lý 1 (bao hàm tất định).** [Proved] Với mọi thực hiện dữ liệu, mọi Ω̂ PSD, mọi ĉ: nếu (M) đúng và η ≤ β(P, m*) thì

  { ∃ f : f được assert và f(m*) = 0 } ⊆ { m* ∉ C_n(η) } ⊆ { W_n > ĉ }.

*Chứng minh.* Theo Bổ đề 0, ζ_n ∈ R_n^η(m*), nên d²_η(z, m*) ≤ W_n. Nếu W_n ≤ ĉ thì m* ∈ C_n(η). Nếu f(m*) = 0 thì m* ∈ M_¬f, nên T^η(f) ≤ d²_η(z, m*) ≤ ĉ, tức f không được assert. ∎

**Nhận xét.**
(a) Sự kiện vế phải không phụ thuộc f, nên bảo đảm là **đồng thời cho mọi f**, kể cả f chọn sau khi xem dữ liệu, và **đồng thời cho mọi η ≤ β** (dùng ở Thm 7).
(b) Không dùng R_n = A_n: relaxation chỉ làm giảm power, đúng như contract §1.4.
(c) Quy tắc R1 chính là "feature bất biến trên confidence set C_n", tức lập luận tổ hợp của Wang–Kolar–Drton Lemma 3 [Source-verified]. Mức ở đây là 1−α vì chỉ cần một m* cố định nằm trong C_n; Lemma 3 có 1−2α vì cần hai ordering đúng cùng nằm trong tập, còn khi ordering duy nhất thì họ cũng có 1−α.

**Định lý 2 (V1, pointwise).** [Proved] Dưới (G), (Q), với P cố định: P(W_n > ĉ_n) → α. Do đó, nếu (M) và η_n ≤ β(P, m*) từ một lúc nào đó (đặc biệt: (F) và η_n → 0, hoặc η cố định ≤ β), thì limsup P(∃ f assert sai) ≤ α.

*Chứng minh.* Đặt r = rank Σ ≥ 1 (đường chéo đơn vị). Viết Σ(C) = M(C)M(C)ᵀ với M(C) = √2 [vec(C^{1/2}H_k(C)C^{1/2})]_k trơn, Δ = M(Ĉ) − M(C) = O_p(n^{-1/2}). Với u ∈ null Σ: uᵀΣ̂u = ‖Δᵀu‖² = O_p(1/n), nên theo Courant–Fischer σ̂_j = O_p(1/n) < τ_n với j > r. Theo Weyl σ̂_j ≥ σ_r − O_p(n^{-1/2}) > τ_n với j ≤ r. Cả hai có xác suất → 1. Vậy P(r̂ = r) → 1. Trên sự kiện đó Ω̂ = h(Σ̂), h(x) = x⁻¹1[x > σ_r/2], giải tích quanh phổ của Σ (phép chiếu Riesz), nên Ω̂ → Σ⁺ theo xác suất. Từ z − ζ_n ⇒ G ~ N(0, Σ): W_n ⇒ GᵀΣ⁺G ~ χ²_r. Áp dụng Thm 1. ∎

Tốc độ P(r̂ = r) → 1 phụ thuộc σ_r(Σ(P)), nên chứng minh này **chỉ cho pointwise**. Ngoại lệ: khi Q chứa mọi query biên, r = d hằng và σ_d liên tục dương trên 𝓚, nên V0 = V1 valid đều. Khi Q không chứa chart, tính đều của V1 là [Open].

**Định lý 3 (V2, đồng đều, không cần ước lượng rank).** [Proved] Dưới (G), (Q), với 𝓚 compact các ma trận tương quan PD và α ∈ (0,1):

  lim_{n→∞} sup_{R∈𝓚} | P_R(W_n > ĉ_n) − α | = 0.

Do đó, với **mọi dãy** η_n ≥ 0 và 𝓟_n = {(P, m*) : R ∈ 𝓚, (M), β(P, m*) ≥ η_n}:

  limsup_n sup_{(P,m*)∈𝓟_n} P(∃ f assert sai) ≤ α.

Nếu thêm λ_n → 0 và P cố định với rank Σ = r, thì W_n ⇒ χ²_r và ĉ_n → χ²_{r,1−α}. Tức V2 tái lập ngưỡng rank-aware của contract mà không cần biết hay ước lượng r.

*Chứng minh.* Giả sử μ = 0, C = R. Phản chứng: nếu không đều, có dãy R_n ∈ 𝓚 và ε > 0 với |P_{R_n}(W_n > ĉ_n) − α| ≥ ε dọc một dãy con. Trích tiếp để R_n, cơ sở riêng U_n và trọng số w_n = (σ_j(Σ_n)/(σ_j(Σ_n)+λ_n))_j hội tụ, với Σ_n = Σ(R_n), A_n = Σ_n + λ_nI, Â = Σ̂ + λ_nI.

*Bước 1 (đổi metric).* Viết Σ(·) = M(·)M(·)ᵀ như ở Thm 2, Δ = M(Ĉ) − M(R_n) = O_p(n^{-1/2}) đều trên 𝓚. Khi đó Σ̂ − Σ_n = ΔMᵀ + MΔᵀ + ΔΔᵀ, và vì ‖A_n^{-1/2}M‖ ≤ 1:

  ε_n := ‖A_n^{-1/2}(Â − A_n)A_n^{-1/2}‖ ≤ 2λ_n^{-1/2}‖Δ‖ + λ_n⁻¹‖Δ‖² = O_p((nλ_n)^{-1/2}) = o_p(1).

Do đó (1+ε_n)⁻¹A_n⁻¹ ≼ Â⁻¹ ≼ (1−ε_n)⁻¹A_n⁻¹ và W_n = (1 + o_p(1)) · ‖A_n^{-1/2}(G_n + B_n)‖².

*Bước 2 (bỏ phần dư).* ‖A_n^{-1/2}B_n‖ ≤ λ_n^{-1/2}‖B_n‖ = O_p((nλ_n)^{-1/2}) = o_p(1).

*Bước 3 (CLT sau chuẩn hóa).* Đặt Y_n = A_n^{-1/2}G_n = n^{-1/2}Σ_i A_n^{-1/2}ψ(V_i), Cov Y_n = U_n diag(w_n) U_nᵀ ≼ I. Với vector đơn vị a, x = aᵀA_n^{-1/2}ψ(V) là dạng toàn phương Gaussian đã quy tâm: x = Σ_ℓ μ_ℓ(g_ℓ² − 1), do đó E x² = 2Σμ_ℓ² ≤ 1 và

  E x⁴ = 48Σμ_ℓ⁴ + 12(Σμ_ℓ²)² ≤ 15(E x²)² ≤ 15.

Đây là bất đẳng thức sơ cấp, chặn đều theo hướng và theo R_n, kể cả các hướng có trị riêng tiến về 0. Lyapunov và Cramér–Wold cho Y_n ⇒ N(0, Ξ), Ξ = lim U_n diag(w_n) U_nᵀ. Vậy W_n ⇒ L(w) := Σ_j w_j g_j², w = lim w_n.

*Bước 4 (ngưỡng).* Theo Ostrowski, σ̂_j + λ_n = θ_j(σ_j(Σ_n) + λ_n) với θ_j ∈ [1−ε_n, 1+ε_n]. Vì w = 1 − λ/(σ+λ): ‖ŵ − w_n‖_∞ ≤ ε_n/(1−ε_n) = o_p(1). Vì tr Σ = K nên σ₁ ≥ 1, suy ra max_j w_j ≥ 1/(1+λ̄) > 0. Trên tập {w ∈ [0,1]^K : max w ≥ 1/(1+λ̄)}, hàm phân phối của L(w) liên tục, tăng ngặt trên (0, ∞), nên w ↦ q_{1−α}(L(w)) liên tục. Vậy ĉ_n → q_{1−α}(L(w)) theo xác suất.

*Bước 5.* Slutsky và tính liên tục của phân phối L(w) cho P(W_n > ĉ_n) → α dọc dãy con, mâu thuẫn. Phần về 𝓟_n suy từ Thm 1 (sự kiện W_n > ĉ_n không phụ thuộc m*). Trường hợp λ_n → 0: ŵ_j → 1 với j ≤ r, và với j > r thì σ_j = 0 nên ŵ_j ≤ ε_n/(1−ε_n) → 0. ∎

**Hằng số không đều theo K.** Thm 3 cố định p, K. Các O_p ở Bước 1–2 có hằng số tăng theo K, và ở K lớn hữu hạn mẫu lệch nặng (§8.2).

**Hệ quả 3.1 (pointwise, không cần biết η).** P cố định, (F), η_n → 0 ⇒ limsup P(assert sai) ≤ α. Đây là phát biểu erratum §10b của contract, nay đã có chứng minh. Giả thiết √nη_n → ∞ **không cần** cho validity, chỉ cần cho power.
**Hệ quả 3.2 (η cố định hoặc cục bộ).** Thm 3 áp dụng cho η cố định và cho η_n = h/√n. Đây là bảo đảm có nội dung (§5).
**Hệ quả 3.3 (chọn Q trên mẫu khác).** Q, M, F chọn trên mẫu độc lập từ tập hữu hạn: áp dụng có điều kiện rồi lấy max trên tập hữu hạn đó. Q thích nghi **trên cùng mẫu không được phủ** (contract §2.5).
**Hệ quả 3.4 (cận chặt).** p = 2, M = {m₁: X→Y, m₂: rỗng}, Q = {X⊥Y}, f = "X ∈ An(Y)", truth m₂, η = 0: M_¬f = {m₂}, T⁰(f) = W_n, m₁ luôn thuộc C_n, nên P(assert f) → α. Vậy α không cải thiện được trên toàn bộ các cặp (M, f). Với M giàu, T ≪ W_n và thủ tục bảo thủ (§8).

**Nhận xét 3.5 (vì sao ridge "hỏng" ở Day-2).** Tại a = 0 của Q₂ với Σ oracle: W ≈ 2u²/(2+λ) + (wv)²/(2nλ). Số hạng thứ hai chỉ biến mất khi **nλ → ∞**. Day-2 dùng λ cố định rất nhỏ (nλ ∈ {0.02, 0.1, 0.2, 1}), đúng vùng công thức dự đoán FAR lớn. Contract §2.4 kết luận "kết quả do quy ước quyết định"; kết luận đúng hơn là **kết quả do tốc độ của λ_n quyết định**, và điều kiện tiệm cận là nλ_n → ∞ (§8.1). Công thức này chỉ dành cho **Σ oracle**. Với Σ̂ plug-in, số hạng thứ hai thành (wv)²/(w²+v²+2nλ), nên V2 không nổ theo cách đó trên Q₂. Ở thực hành, điều chi phối V2 là nλ so với K (§8.2).

---

## 4. Power

### 4.1 Kết quả âm: seminorm mù

**Định lý 4 (blindness).** [Proved] Cho Ω PSD bất kỳ, 𝓛 = range Ω, N = 𝓛^⊥ = null Ω. Với mô hình m, đặt C_I = span{e_k : k ∈ I(m)}. Nếu

  **(B1)** 𝓛 ∩ C_I = {0},  **(B2)** e_k ∉ 𝓛 + C_I với mọi k ∈ D(m),

thì **d²_η(z, m) = 0 với mọi z ∈ R^K và mọi η ≥ 0**. Ngược lại, với η > 0 cố định, nếu (B1) hoặc (B2) sai thì tồn tại z để d²_η(z, m) > 0. Tức (B1)–(B2) **đặc trưng** blindness.

*Chứng minh.* Cần n ∈ N sao cho u = z − n ∈ R_n^η(m); khi đó (z−u)ᵀΩ(z−u) = nᵀΩn = 0.
*Bước 1.* Ánh xạ N → R^{|I|}, n ↦ n_I là toàn ánh: nếu w ⊥ ảnh của nó thì w (bù 0) thuộc N^⊥ = 𝓛 và thuộc C_I, nên w = 0 theo (B1). Chọn n⁰ ∈ N với n⁰_I = z_I.
*Bước 2.* N₀ = {n ∈ N : n_I = 0} có phần bù trực giao 𝓛 + C_I. Theo (B2), với mỗi k ∈ D(m), hàm tọa độ n ↦ n_k khác 0 trên N₀. Hợp hữu hạn các không gian con thực sự không phủ được N₀, nên có n¹ ∈ N₀ với n¹_k ≠ 0 mọi k ∈ D(m).
*Bước 3.* Lấy n = n⁰ + t n¹, t đủ lớn: u_I = 0 và |u_k| ≥ t|n¹_k| − |z_k − n⁰_k| ≥ √n_k η.
*Chiều ngược.* Với ℓ ∈ 𝓛: (ℓᵀv)² ≤ (ℓᵀΩ⁺ℓ) vᵀΩv. Nếu 0 ≠ w ∈ 𝓛 ∩ C_I thì wᵀu = 0 với mọi u ∈ R_n^η(m), nên chọn z có wᵀz ≠ 0 cho d² > 0. Nếu e_k = ℓ + c với ℓ ∈ 𝓛, c ∈ C_I, k ∈ D(m), thì với z_I = 0, z_k = 0: |ℓᵀ(z−u)| = |u_k| ≥ √n_k η, nên d² > 0. ∎

**Hệ quả 4.1.**
(a) Điều kiện đúng ở mức feature: nếu **M_¬f chứa một mô hình thỏa (B1)–(B2)** thì **T^η(f) ≡ 0: f không bao giờ được assert, với mọi dữ liệu, mọi n, mọi η**. K > rank một mình **không đủ**: ở p = 4, K = 18, M gồm DAG tối đa 2 cạnh thì không có pattern mù nào (§8.3).
(b) Mô hình đầy đủ (I = ∅) mù khi và chỉ khi không có e_k nào thuộc 𝓛. Mọi feature tổ tiên "X ∈ An(Y)" và phủ định của nó đều sai trên một DAG đầy đủ nào đó. Do đó, khi M chứa mọi DAG/MAG đầy đủ và không e_k nào thuộc 𝓛 (đúng tại mọi R tổng quát đã kiểm ở §8.3), **R1 với seminorm không chứng nhận được bất kỳ feature tổ tiên nào**.
(c) Theo Mệnh đề 2, N ≠ {0} là không tránh được khi K > d, và xảy ra ở điểm rớt rank khi K ≤ d. Từ (B1)–(B2), |D(m)| > r là **điều kiện cần** để m mù (vì 𝓛 + C_I phải khác R^K khi D ≠ ∅); nó không đủ (§8.3).
(d) [Số, §8.3] Thu hẹp M theo sparsity cứu rất ít: ở p = 4, K = 24 chỉ cần M chứa DAG 2 cạnh, ở K = 18 chỉ cần DAG 3 cạnh, là mọi feature tổ tiên đã có T ≡ 0.
(e) **Phạm vi:** Thm 4 nói về một Ω **toàn cục dùng chung cho mọi mô hình**. Seminorm theo khối riêng từng mô hình, Ω_m = (Σ̂_II)⁺ ⊕ 0 cộng với kiểm định một phía trên D(m) (tức hybrid ở Thm 6(d) với cắt cứng thay ridge), **không mù**: ví dụ z_{XY|Z} = 40 cho 1600 thay vì 0. Đây là ứng viên đáng thử ở K lớn (§8.2) [Hypothesis; size đều khi rớt rank trong khối là Open].

Trực giác: null Σ là các hướng **thống kê không dao động**, nên lệch theo hướng đó phải đắt vô hạn. Seminorm làm điều ngược lại: miễn phí. Vì vùng tọa độ R_n ⊋ A_n chứa các điểm không đạt được (contract §2.2), inf đi thẳng tới đó. Một test không bao giờ bác bỏ thì dĩ nhiên valid: **validity của R1 với seminorm toàn cục trong contract §7 đúng nhưng rỗng nghĩa** khi M_¬f chứa mô hình mù. Contract §2.4 chỉ ghi "cái giá là mất thông tin ngoài range"; thực tế cái giá là toàn bộ power.

Với **tập A_n thật** (R3) thì không có hiện tượng này, nhưng khi đó phải tối ưu trên ma trận tương quan Markov theo m, và mất ưu thế "chỉ cần vector CI statistics". Ridge giữ được R_n.

Cùng họ với Dufour–Valéry (WP 2011), Corollary 8.7: spectral cut-off "will destroy power" theo hướng ∆ ∈ null Σ [Source-verified]. Thm 4 là phiên bản với tập mô hình: mọi hướng null đều bị lợi dụng đồng thời.

### 4.2 Kết quả dương: V2 có power

**Mệnh đề 5 (cận sup-norm, so sánh với Bonferroni).** [Proved] Với V2 và mọi z, m, η:

  (i) d²_η(z, m) ≥ dist²_∞(z, R_n^η(m)) / (1 + λ_n),

với dist_∞(z, R_n^η(m)) = max{ max_{k∈I(m)} |z_k|, max_{k∈D(m)} (√n_k η − |z_k|)₊ }.

(ii) **BL1 hộp Bonferroni:** C_n^B = {m : dist_∞(z, R_n^η(m)) ≤ t_K}, t_K = z_{1−α/(2K)}, valid đều trên 𝓟_n (union bound + biên chuẩn của Lemma 1).
(iii) Nếu ĉ_n(1 + λ_n) ≤ t_K² thì C_n ⊆ C_n^B: khi C_n ≠ ∅, R1 chứng nhận mọi thứ BL1 chứng nhận.
(iv) Điều kiện (iii) tương đương xấp xỉ K ≥ K_crit(r) := α/(2Φ̄(√χ²_{r,1−α})). Với Q đủ (r = C(p,2)), kể cả K lớn nhất có thể K_full = C(p,2)·2^{p−2}, luôn có K_full < K_crit(r) (kiểm tra cho p = 3,…,30, §8). Tức **khi Q chứa chart, cận (iii) không bao giờ kích hoạt, nên R1 không tự động chứa BL1**; R1 chỉ có thể thắng nhờ gộp nhiều tọa độ hoặc giảm phương sai (Mệnh đề 8). Khi Q nhỏ và trùng nhiều (ví dụ r = 1, K = 2) thì (iii) có thể đúng.

*Chứng minh (i).* Cauchy–Schwarz: v_k² ≤ (eₖᵀÂeₖ)(vᵀÂ⁻¹v) = (1 + λ_n) vᵀÂ⁻¹v, do Σ̂ có đường chéo đơn vị. Áp dụng với v = z − u, u ∈ R_n^η(m). R_n^η(m) là tích Descartes theo tọa độ nên dist_∞ có dạng trên. (iii) trực tiếp từ (i). ∎

**Định lý 5 (điều kiện đủ cho power).** [Proved] Dưới (G), (M), V2. Với m′ ∈ M, đặt Δ(m′) = {k : π_k(m′) ≠ π_k(m*)} và

  gap_k(m′) = |ζ_{n,k}| nếu k ∈ I(m′) ∩ D(m*);  gap_k(m′) = √n_k η nếu k ∈ D(m′) ∩ I(m*).

Đặt Gap_n(f) = min_{m′∈M_¬f} max_{k∈Δ(m′)} gap_k(m′) (max ∅ = 0, tức Gap_n = 0 nếu f không Q-identifiable).
(i) (Tất định) Với mọi z: T^η(f) ≥ (Gap_n(f) − ‖z − ζ_n‖_∞)₊² / (1 + λ_n).
(ii) Do đó, nếu Gap_n(f) > t + √(ĉ_n(1+λ_n)) thì trên {‖z − ζ_n‖_∞ ≤ t}: T^η(f) > ĉ_n. Xác suất sự kiện này ≥ 1 − 2KΦ̄(t) − o(1), và ĉ_n ≤ χ²_{K,1−α}.
(iii) (Nhất quán) P cố định, (F), f đúng và Q-identifiable, η_n → 0, √nη_n → ∞: T^{η_n}(f) → ∞ theo xác suất, tốc độ ≥ c·nη_n². Với quy tắc abstain, liminf P(f được assert) ≥ 1 − α, vì P(C_n = ∅) ≤ P(W_n > ĉ_n) → α; không có abstain thì P(T > ĉ_n) → 1.
(iv) Với f như (iii) và η cố định ≤ β: T^η(f) ≥ c·n với xác suất → 1, vì Gap_n ≍ √n · min(η, |θ_k|).

*Chứng minh.* (i) Với u ∈ R_n^η(m′), k ∈ Δ(m′): |ζ_{n,k} − u_k| ≥ gap_k(m′) (nếu k ∈ I(m′) ∩ D(m*) thì u_k = 0; nếu k ∈ D(m′) ∩ I(m*) thì ζ_{n,k} = 0 và |u_k| ≥ √n_k η). Vậy ‖z − u‖_∞ ≥ gap_k − ‖z − ζ_n‖_∞; áp dụng Mệnh đề 5(i). (iii) f Q-identifiable và đúng nên mọi m′ ∈ M_¬f có Δ(m′) ≠ ∅, và Gap_n ≥ min_k √n_k min(|θ_k|, η_n) → ∞. ∎

**So sánh:** dưới V1, khi M_¬f chứa mô hình mù thì không điều nào trong Thm 5 đúng (Thm 4). Bước (b) trong chứng minh P2 của contract được khôi phục nhờ đường chéo của Â bị chặn, **không cần Σ PD**.

**Mệnh đề 4 (điều kiện cần).** [Proved]
(a) Nếu f đúng tại m* nhưng không Q-identifiable, thì với η ≤ β: P(f được assert) ≤ P(W_n > ĉ_n) → α.
(b) **η = 0 không chứng nhận được gì khi M chứa mô hình đầy đủ trong M_¬f:** R_n⁰(m_c) = R^K nên T⁰(f) = 0 với mọi z, mọi metric. Muốn bỏ η thì phải thu hẹp M bằng giả định tiên nghiệm khác (sparsity…), và giả định đó cũng không kiểm định được.
(c) Nếu η > β(P, m*): Thm 1 không áp dụng. Trường hợp mọi mô hình cùng bị bác bỏ thì abstain; nếu mô hình sai sống sót thì có thể chứng nhận sai với xác suất cao (Experiment E của Day-2 là minh họa cho score cũ).

**Mệnh đề 6 (Schur, chứng nhận inactive).** [Proved] Với V2, I = I(m), S_m(z) := z_Iᵀ(Σ̂_II + λ_nI)⁻¹z_I (S_m = 0 nếu I rỗng):
(i) S_m ≤ d²_η(z, m).
(ii) Nếu |z_k| ≥ √n_k η + √S_m với mọi k ∈ D(m) thì d²_η(z, m) = S_m.
(iii) Với I′ = I ∪ {k}: S_{I′} = S_I + (z_k − b̂ᵀz_I)² / ((1+λ_n)(1 − R̂²_{k|I})), b̂ = Â_II⁻¹Â_Ik, R̂²_{k|I} = Â_kIÂ_II⁻¹Â_Ik/Â_kk.

*Chứng minh.* (i) Tối thiểu hóa dạng toàn phương theo các tọa độ tự do D cho nghịch đảo của khối Â_II. (ii) Điểm cực tiểu tự do là u°_D = z_D − Σ̂_DI(Σ̂_II + λ_nI)⁻¹z_I. Viết Σ̂ = L̂L̂ᵀ, ℓ_k là hàng k của L̂ (‖ℓ_k‖ = 1), A = Σ̂_II + λ_nI: |u°_k − z_k| = |ℓ_kᵀL̂_IᵀA⁻¹z_I| ≤ (z_IᵀA⁻¹Σ̂_IIA⁻¹z_I)^{1/2} ≤ √S_m, vì A⁻¹Σ̂_IIA⁻¹ ≼ A⁻¹. Vậy u° ∈ R_n^η(m). (iii) Chain rule của Mahalanobis. ∎

Mệnh đề 6 cũng cho một phép sàng lọc rẻ: S_m > ĉ thì bác bỏ ngay; nếu (ii) đúng thì không cần duyệt 2^{|D|} orthant.

**Mệnh đề 8 (noncentrality, cận trên cho mọi thủ tục).** [Proved] Working model z ~ N(ζ, Σ), Σ PD, f(m′) = 0.
(i) Mọi thủ tục có P_{ζ′}(assert f) ≤ α với mọi ζ′ ∈ R^η(m′) đều thỏa P_ζ(assert f) ≤ Φ(√NCP − z_{1−α}), với NCP = min_{ζ′∈R^η(m′)} (ζ−ζ′)ᵀΣ⁻¹(ζ−ζ′). (Neyman–Pearson.)
(ii) Đối thủ có thêm một độc lập, I(m′) = I(m*) ∪ {k}, ràng buộc inactive: d²_η(z, m′) = S_{I′} ~ noncentral χ²_{|I′|}(NCP), với **NCP = ζ_k²/(1 − R²_{k|I(m*)})**.
(iii) Đối thủ supermodel, I(m′) = I(m*) \ {k}, các tọa độ phụ thuộc khác inactive: **NCP = δ_k²/(1 − R²_{k|I(m′)})**, δ_k = √n_k η. Đây là chỗ h = √nη quyết định power, và là lý do η không thể bỏ (Mệnh đề 4b).

**Ba giới hạn của các công thức trên** (M3 của lượt rà soát):
- (ii)–(iii) cần ràng buộc inactive, tức |z_k| ≥ √n_kη + √S_m trên D. Trong regime cục bộ ở §5 điều này không đương nhiên đúng, nên chúng chỉ là phép xấp xỉ định hướng ở đó.
- NCP viết theo Σ⁻¹. Với metric ridge, mẫu số là (1+λ)(1 − R̂²_λ) theo Mệnh đề 6(iii): một query trong I cho 1+λ − r²/(1+λ). Ở R² = .9, λ = .1 mẫu số là .282 thay vì .1, tức lợi ích giảm từ 10 lần xuống 3.5 lần.
- **Lợi từ R² không phải của riêng thống kê χ².** Contrast 1-df (z_k − bᵀz_I)/√(1−R²) có cùng NCP với ít bậc tự do hơn. Trên mọi cấu hình đã tính, ở đối thủ một tọa độ, χ² không hơn contrast đó (§8.7); ưu thế riêng của χ², nếu có, phải đến từ tín hiệu trên nhiều tọa độ.

Do đó R² là một đại lượng **quan trọng** để đo ở RG3, nhưng không tự quyết định R1 có đáng dùng. Bảng số ở §8.7 dùng các ngưỡng valid trong regime cục bộ.

---

## 5. Bảo đảm thật sự nói gì

**Mệnh đề 7 (thresholding nhất quán, CT).** [Proved] Định nghĩa CT_η: π̂_k = 1[|z_k| < √n_k η/2]; assert f ⇔ π̂ ∈ π(M) và f đúng trên {m : π(m) = π̂}.
(i) **Pointwise.** P cố định, (F), η_n → 0, √nη_n → ∞: P(π̂ = π(m*)) → 1. Do đó **FWER → 0 và mọi feature đúng Q-identifiable được assert với xác suất → 1**.
(ii) **η cố định.** Đều trên 𝓟: P(π̂ ≠ π(m*)) ≤ 2KΦ̄(√nη/2) + o(1) → 0.
(iii) **Cục bộ.** Nếu min_k √n_k η > 2t_K thì trên {‖z − ζ_n‖_∞ ≤ t_K} (xác suất ≥ 1 − α − o(1)) có π̂ = π(m*): CT không assert sai và assert mọi feature đúng Q-identifiable. Khi đó không thủ tục nào hơn CT quá α.

*Chứng minh.* (i) Với k ∈ I: z_k = O_p(1), ngưỡng → ∞. Với k ∈ D: |z_k| ≥ √n_k|θ_k| − O_p(1) ≫ √n_kη_n. (ii) Tương tự, dùng biên đều của Lemma 1. (iii) k ∈ I: |z_k| ≤ t_K < δ_k/2. k ∈ D: |z_k| ≥ δ_k − t_K > δ_k/2. ∎

**Hệ quả — phân loại regime:**

| Regime | Bảo đảm của R1 | CT đạt được | Kết luận |
|---|---|---|---|
| Pointwise, η_n → 0, √nη_n → ∞ | FWER ≤ α + o(1), power → ≥ 1−α | FWER → 0, power → 1 | **R1 không có lợi thế**; "valid pointwise" không phân biệt được R1 |
| η cố định, n → ∞ | như trên, đều | FWER → 0, đều | **Như trên** |
| Cục bộ, √nη ≥ h_CT := 2t_K | FWER ≤ α | FWER ≤ α, power ≥ 1−α | R1 hơn tối đa α |
| **Cục bộ, √nη < h_CT** | **FWER ≤ α đều** | Không có bảo đảm; vi phạm mức α khi h đủ nhỏ (§8.6) | **Regime duy nhất trong lớp η ≤ β mà R1 có thể có nội dung** |
| **η > β** (ngoài mọi bảo đảm) | Không có bảo đảm; FWER có thể rất cao ở n vừa, nhưng C_n rỗng dần khi n lớn | β < η/2: sai vĩnh viễn và im lặng; η/2 < β < η: đúng khi n lớn | R1 tự phát hiện được giả định sai, CT thì không; **BL1 cũng có khả năng này**, nên đây không phải lợi thế riêng (§8.6) |

Trong lớp η ≤ β, ngoài regime cục bộ, **erratum §10b của contract đúng về toán nhưng không phải điểm mạnh**: Robins et al. 2003 đã ghi nhận tồn tại thủ tục pointwise-consistent, và thủ tục đơn giản CT đã đạt. Hệ quả: nhận định "R2 trở thành phần phụ" (`A1_pilot_readiness.md` §11.4) phải **đảo lại**: nội dung của R1 chính là bảo đảm có điều kiện theo η.

Trong regime cục bộ, đối thủ valid tự nhiên không phải CT mà là BL1: quyết định ba trạng thái theo từng tọa độ (độc lập / phụ thuộc / chưa rõ). Đó là câu hỏi của RG2.

**Chưa có bằng chứng R1 có nội dung ngay trong regime này** (S1 của lượt rà soát): chưa kịch bản nào cho thấy đồng thời CT vượt α và R1 có power dương. Trên chain, CT vượt α nhưng R1 không có feature Q-identifiable nào để chứng nhận. Trên collider với h ≤ 3, R1 chứng nhận tối đa khoảng 0.17 và CT không vi phạm mức. h_CT cũng chỉ là điều kiện đủ. RG2 phải dựng được một kịch bản như vậy.

---

## 6. R1′: ngưỡng theo từng MAG

Theo Thm 1, chỉ cần **một** phép kiểm định đúng cho H_{m*}: không có multiplicity giữa các m. Vì vậy mỗi m có thể dùng ngưỡng riêng.

**Định lý 6.** Với V2, ĉ_I := q_{1−α}(Σ_j ŵ_j^{(I)} g_j²), ŵ^{(I)} tính từ trị riêng của Σ̂_II (ĉ_∅ = 0).

(a) [Proved] **Pointwise.** C′_n = {m : d²_{η_n}(z, m) ≤ ĉ_{I(m)}}. Với P cố định, (F), η_n → 0: P(m* ∉ C′_n) → α (→ 0 nếu I(m*) rỗng). Hơn nữa **tất định C′_n ⊆ C_n**, nên khi C′_n ≠ ∅, R1′ chứng nhận mọi thứ R1 chứng nhận. Sự trội này chỉ cho **ngưỡng pointwise**, là ngưỡng không đều theo (b); trong regime cục bộ phải dùng (c) hoặc (d).

(b) [Proved] **Ngưỡng ở (a) không đồng đều.** K = 2, Σ = [[1, ϱ], [ϱ, 1]], I = {1}, D = {2}, z ~ N((0, δ), Σ), δ lớn: d²(z, m) có phân phối hỗn hợp ½χ²₁ + ½χ²₂, nên P(bác bỏ m) → 0.098 ở mức danh nghĩa 0.05.

(c) [Proved trong working model; Sketch cho dữ liệu Gaussian] **Ngưỡng chi-bar.** Với σ ∈ {±1}^{D(m)}, C₀^σ = {v : v_I = 0, σ_kv_k ≥ 0}, T₀^σ(g) = inf_{v∈C₀^σ}(g−v)ᵀΩ(g−v). Nếu ζ ∈ R^η(m) có dấu σ thì, **với mọi z**, d²_η(z, m) ≤ T₀^σ(z − ζ). Do đó c̄_m = max_σ q_{1−α}(T₀^σ(G)), G ~ N(0, Σ), là ngưỡng valid đều trong working model. Vì v = 0 ∈ C₀^σ nên T₀^σ(G) ≤ GᵀΩG, suy ra **c̄_m ≤ ĉ_n** với Ω = Â⁻¹, G ~ N(0, Σ̂): đây là phát biểu trội đúng cho ngưỡng valid. Khi Ω = Σ⁻¹ PD còn có q_{1−α}(χ²_{rank Σ_II}) ≤ c̄_m. Vì c̄_m không phụ thuộc η, Thm 7 chuyển được sang ngưỡng này cho từng mô hình.

(d) [Proved] **Hybrid, đều trên 𝓟_n, kể cả rank suy biến.** Bác bỏ m khi S_m > q_{1−α₁}(Σŵ_j^{(I)}g_j²) hoặc khi ∃k ∈ D(m): |z_k| < √n_kη − z_{1−α₂/|D|}, α₁ + α₂ = α (α₁ = 0 nếu I rỗng, α₂ = 0 nếu D rỗng).

*Chứng minh.*
(a) Thm 3 áp dụng cho họ con Q_I cho P(S_{m*} > ĉ_I) → α. Mệnh đề 6(ii): |z_k| − √n_kη_n ≥ √n_k(β − η_n) − O_p(1) → ∞ và √S_{m*} = O_p(1), nên d² = S_{m*} với xác suất → 1. Cauchy interlacing: σ_j(Σ̂_II) ≤ σ_j(Σ̂), và x/(x+λ) tăng, nên ŵ_j^{(I)} ≤ ŵ_j, do đó ĉ_I ≤ ĉ_n.
(b) d² = z₁² + (δ − t*)₊²/(1−ϱ²) khi δ lớn (chỉ nhánh dương), với t* = z₂ − ϱz₁ ~ N(δ, 1−ϱ²) độc lập z₁.
(c) Với v ∈ C₀^σ, u = ζ + v ∈ R^η(m) (u_I = 0; σ_ku_k ≥ σ_kζ_k ≥ δ_k), nên d²(z,m) ≤ ‖(z−ζ) − v‖²_Ω. Đây là lập luận của Silvapulle–Sen, Theorem 3.8.1 (tr. 91) [Source-verified]. Phần Sketch cho dữ liệu Gaussian: Y_n ⇒ N(0, Ξ) như Thm 3 và compact hóa các nón Â^{-1/2}C₀^σ theo Painlevé–Kuratowski. Chưa kiểm tra đủ chi tiết tại nguyên tử 0 của chi-bar.
(d) Union bound: Thm 3 cho khối I; và nếu σ_k = sign ζ_k, |ζ_k| ≥ δ_k thì {|z_k| < δ_k − t} ⊆ {σ_k(z_k − ζ_k) < −t}, xác suất → Φ̄(t). ∎

---

## 7. R2: η-profile

Với V2; ĉ_n không phụ thuộc η. Định nghĩa

  η*_m(z) = inf{η ≥ 0 : d²_η(z, m) > ĉ_n} (inf ∅ = +∞),  η*(f) = max_{m∈M_¬f} η*_m,  η̄ = max_{m∈M} η*_m.

**Định lý 7.** [Proved]
(a) **Đơn điệu, Lipschitz.** η ↦ d_η(z, m) không giảm và Lipschitz với hằng số ≤ λ_n^{-1/2}(Σ_k n_k)^{1/2}. Do đó T^η(f) > ĉ_n với mọi η > η*(f) và T^η(f) ≤ ĉ_n với mọi η < η*(f). C_n(η) ≠ ∅ khi η ≤ η̄ và C_n(η) = ∅ khi η > η̄ (trừ trường hợp biên η̄ = 0 với mọi d²₀ > ĉ_n, không xảy ra khi M chứa mô hình đầy đủ). Cả η*(f) lẫn η̄ tính được bằng bisection theo từng pattern.
(b) **Ngữ nghĩa, đều, không giả định beta-min.** Trên E_n = {W_n ≤ ĉ_n}, với mọi (P, m*) thỏa (M), β = β(P, m*):

  (b1) với **mọi** f có f(m*) = 0: η*(f) ≥ β;  (b2) β ≤ η̄.

Và sup_{R∈𝓚} |P_R(E_n) − (1−α)| → 0. Tức với xác suất ≥ 1 − α − o(1), **đồng thời cho mọi f**: "f đúng, hoặc phụ thuộc yếu nhất của m* không vượt η*(f)". Giả định beta-min không biến mất mà chuyển vào vế "hoặc": muốn đọc thành "f đúng" vẫn phải giả định β > η*(f), và với P không faithful theo m* thì β = 0 và phát biểu rỗng.
(c) **Phải báo cáo η̄.** f chỉ được chứng nhận không vacuous khi η*(f) < η̄, trên khoảng (η*(f), η̄]. Với η > η̄ thì mọi mô hình đều bị bác bỏ. Thiếu cận trên này, η*(f) hữu hạn gần như luôn tồn tại và **vô nghĩa**: cả f lẫn ¬f đều có η* hữu hạn nếu không pattern nào "độc lập hoàn toàn". Định nghĩa gốc ở contract §7 thiếu điều này.
(d) **Thang 1/√n.** P cố định, (F), f đúng và Q-identifiable. Với m′ ∈ M_¬f: nếu I(m′) ∩ D(m*) ≠ ∅ thì η*_{m′} = 0 với xác suất → 1; nếu không (I(m′) ⊊ I(m*)), chọn k ∈ D(m′) ∩ I(m*) thì η*_{m′} ≤ (|z_k| + √(ĉ_n(1+λ_n)))/√n_k. Vậy **√n · η*(f) = O_p(1)**.
(e) Hai phía không đối xứng: dữ liệu cho **cận trên** của β (b2), nhưng không có cận dưới đều. [Inference, phù hợp no-free-lunch của Shah–Peters và Robins et al.: một phụ thuộc rất nhỏ thêm vào không phân biệt được ở cỡ mẫu cho trước.]

*Chứng minh.* (a) R_n^η(m) = ∪_σ (C₀^σ + η t_σ), t_σ = (σ_k√n_k)_{k∈D}, 0 trên I. Do đó d_η = min_σ dist_Ω(z − ηt_σ, C₀^σ), mỗi dist là 1-Lipschitz; ‖t_σ‖_Ω ≤ λ_n^{-1/2}‖t_σ‖. Không giảm vì R_n^η giảm theo η. Phần còn lại từ tính liên tục. (b) Với η ≤ β, Bổ đề 0 cho d²_η(z, m*) ≤ W_n ≤ ĉ_n, nên η*_{m*} ≥ β. Với f(m*) = 0: m* ∈ M_¬f nên η*(f) ≥ η*_{m*}. Và η̄ ≥ η*_{m*}. Xác suất từ Thm 3; không dùng giả định nào về độ lớn của β. (d) Từ Mệnh đề 5(i). ∎

Giá trị thực hành: η cần báo cáo ở cỡ (√ĉ + |z_k|)/√n. Với α = 0.05, K = 6, n = 1000, cỡ này khoảng 0.1 (§8.5). η*(f) nhỏ là tin tốt về độ mạnh của giả định cần có. Tuy nhiên **chưa có bằng chứng** "β(P, m*) > η*(f)" thường đúng trên SCM thực tế: Uhler et al. 2013 cho thấy phân phối vi phạm λ-strong faithfulness có thể chiếm tỷ lệ đáng kể khi đồ thị lớn hoặc dày [abstract, Source-verified ở register]. Đây là việc phải đo, chưa phải kết quả.

---

## 8. Kiểm chứng số

**Tái lập:** `python -P -E RG1_numeric_checks.py` (khoảng 25 phút; thêm nhãn như `L` để chạy riêng, `--quick` để chạy nhanh). **Thiết lập.** Python 3.14.7, NumPy 2.5.2, SciPy 1.18.1. Seed gốc 20261104, mỗi kiểm tra có offset riêng. λ_n = n^{-1/3}, τ_n = n^{-1/4}, α = 0.05. **211 assertion PASS, 0 FAIL** ở `RG1_numeric_checks.py` (202 ở lần chạy chính 1239 giây; 6 của kiểm tra K và 3 của kiểm tra L chạy riêng, cùng script). Một số assertion trong đó yếu (§8.9), nên con số này nói lên ít hơn vẻ ngoài. `RG1_followup_checks.py` đo lại các điểm mà rà soát nêu (6 assertion PASS, 0 FAIL, 1825 giây; phần lớn là bảng số để đọc, không phải assertion). Phần lớn assertion là đồng nhất thức và bao hàm tất định. **Không con số nào là bằng chứng power so với baseline, hay bằng chứng nhân quả.**

Dữ liệu Gaussian được sinh qua phân phối Wishart chính xác của Ĉ (Bartlett), đã đối chiếu với sinh dữ liệu thô. Khoảng cách tính bằng NNLS chính xác trên từng orthant, đã đối chiếu với bộ giải Day-2 (120/120) và SLSQP.

### 8.1 Dự đoán từ công thức giấy so với số đo độc lập

| Cấu hình (Q₂, truth (1,1) hoặc tương đương) | Giới hạn trên giấy | Dự đoán | Đo |
|---|---|---|---|
| V0, a = b = 0 (Mệnh đề 3) | U² + ¼U′² | 0.0170 | n = 200/1000/5000: 0.0173 / 0.0176 / 0.0173. Day-2: 0.018, 0.014 |
| Oracle Σ⁻¹, a = n^{-1/2}, b = 0 | U² + (wv)² | **0.1247** | 0.1246 / 0.1239 / 0.1240 |
| V0, a = n^{-1/2}, b = 0 | U² + (wv)²/(w²+v²) | 0.0187 | 0.0184 / 0.0180 / 0.0175 |
| Oracle Σ⁻¹, a = b = n^{-1/2} | U² + (wv−1)²/2 | **0.0904** | 0.0920 / 0.0929 / 0.0878 |
| V0, a = b = n^{-1/2} | U² + (wv−1)²/(w²+v²) | **0.0605** | 0.0560 / 0.0634 / 0.0622 |
| Ridge Day-2, a = 0, λ = 10⁻³, n = 200 (nλ = 0.2) | 2u²/(2+λ) + (wv)²/(2nλ) | 0.234 | Day-2: 0.238 |
| Như trên, λ = 10⁻⁴, n = 200 (nλ = 0.02) | | 0.543 | Day-2: 0.540 |
| Như trên, λ = 10⁻³, n = 1000 (nλ = 1) | | 0.093 | Day-2: 0.085 |
| Như trên, λ = 10⁻⁴, n = 1000 (nλ = 0.1) | | 0.324 | Day-2: 0.311 |
| Thm 6(b), biên active | ½χ²₁ + ½χ²₂ | 0.0983 | 0.0988 |

Trên đường a = c/√n, b = 0, n = 5000 (`RG1_followup_checks.py`, 20000 replicate, V2 và V1 đều 0.048–0.051):

| c | 0.05 | 0.1 | 0.25 | 0.5 | 1 |
|---|---|---|---|---|---|
| Oracle, giới hạn U² + (wv/c)² | 0.769 | 0.634 | 0.398 | 0.227 | 0.125 |
| Oracle, đo | 0.765 | 0.631 | 0.399 | 0.231 | 0.130 |

Trên đường a = b = c/√n, n = 5000, V0 đo 0.062 / 0.091 / 0.089 / 0.072 ở c = 1 / 1.5 / 2 / 3, giới hạn 0.061 / 0.090 / 0.089 / 0.073; V2 và V1 đều 0.046–0.051.

Bốn dòng ridge dùng số Day-2 chạy từ trước, với code khác và seed khác; tuy vậy công thức được viết sau khi đã có các số đó, nên đây là đối chiếu hậu nghiệm. Ở hai dòng a = n^{-1/2} thì w ~ N(1,1), v ~ N(0,1); ở a = b = n^{-1/2} thì w, v ~ N(1,1). Giới hạn của các dòng này là [Derived] từ cùng khai triển, không phải định lý đóng khung.

### 8.2 Size của W_n (khoảng min–max trên các truth; danh nghĩa 0.05)

| Nhóm | n | V2, λ = n^{-1/3} | V2, λ = n^{-1/4} | V1 cắt cứng | V0 pinv thường | Oracle Σ⁺ |
|---|---|---|---|---|---|---|
| Q₂, 8 giá trị của a (SE 0.0015) | 200 | 0.046–0.050 | 0.047–0.051 | 0.048–0.053 | 0.017–0.051 | 0.048–**0.125** |
| | 1000 | 0.046–0.049 | 0.046–0.049 | 0.047–0.050 | 0.018–0.050 | 0.050–**0.124** |
| | 5000 | 0.046–0.051 | 0.047–0.051 | 0.048–0.052 | 0.017–0.050 | 0.049–**0.124** |
| Over-complete: K = 6, 18, 24 (SE 0.002–0.003) | 200 | 0.053–**0.064** | 0.053–0.057 (K = 6) | 0.049–0.054 | = V1 | 0.046–0.054 |
| | 1000 | 0.050–0.054 | 0.050–0.053 (K = 6) | 0.045–0.052 | = V1 | 0.045–0.052 |
| | 5000 | 0.050–0.054 | 0.049–0.054 (K = 6) | 0.049–0.054 | = V1 | 0.049–0.053 |
| Đối kháng K: 6 truth (SE 0.002) | 200 | 0.047–0.054 | 0.047–0.054 | 0.049–0.053 | 0.017–0.056 | 0.050–0.092 |
| | 1000 | 0.047–0.055 | 0.046–0.055 | 0.048–0.054 | 0.017–**0.063** | 0.048–0.093 |
| | 5000 | 0.048–0.053 | 0.048–0.053 | 0.048–0.052 | 0.018–**0.062** | 0.048–0.088 |

**Đọc bảng:**
- V2 phù hợp Thm 3 trên mọi đường đã thử, kể cả ma trận gần suy biến (λ_min(R) = 0.03) và rớt rank với ρ_XY = 0.5.
- **V0 và oracle không đều** (Mệnh đề 3). Kết luận "T_full đúng mức 5%" của toy Day-2 chỉ đúng trong working model, đúng như toy đã ghi là tautological.
- **V1 có size tốt trên mọi đường đã thử**, dù tôi chỉ chứng minh pointwise; tính đều của V1 là [Open]. Điểm yếu của V1 là blindness, không phải size.
- Mẫu nhỏ: V2 đã lệch ở K = 24 (0.064 ở n = 200). λ cố định 0.05 cho 0.062–0.064 ở n = 200, K = 6 (nλ = 10), và 0.050–0.054 ở n ≥ 1000.
- Phần lệch khỏi range: √n · trung vị ‖(I−P)(z−ζ_n)‖ = 0.72 / 0.65 / 0.66 ở n = 200/1000/5000, xác nhận (2.2).

**K lớn** (`RG1_followup_checks.py`, Q đủ bậc ≤ 2; R = I / chain .4 của toàn bộ p biến; 2000, 1000, 150 replicate ở K = 70, 165, 616):

| K | n | Ridge n^{-1/3} | Ridge λ = 0.5 | Ridge λ = 2 | V1 cắt cứng | Seminorm theo khối (khối I đúng) |
|---|---|---|---|---|---|---|
| 70 | 200 | 0.123 / 0.117 | 0.072 / 0.075 | 0.055 / 0.056 | 0.046 / 0.054 | 0.046 / 0.061 |
| | 1000 | 0.067 / 0.070 | 0.049 / 0.053 | 0.043 / 0.049 | 0.044 / 0.051 | 0.044 / 0.050 |
| | 5000 | 0.056 / 0.055 | 0.051 / 0.049 | 0.049 / 0.049 | 0.051 / 0.049 | 0.051 / 0.051 |
| 165 | 200 | **0.222** / 0.186 | 0.104 / 0.084 | 0.064 / 0.055 | 0.051 / 0.047 | 0.051 / 0.050 |
| | 1000 | 0.098 / 0.086 | 0.059 / 0.058 | 0.055 / 0.053 | 0.052 / 0.049 | 0.052 / 0.049 |
| | 5000 | 0.076 / 0.057 | 0.062 / 0.040 | 0.059 / 0.039 | 0.058 / 0.037 | 0.058 / 0.044 |
| 616 | 200 | **0.660** / **0.660** | 0.340 / 0.300 | 0.160 / 0.107 | 0.087 / 0.073 | 0.087 / 0.053 |
| | 1000 | **0.347** / 0.280 | 0.140 / 0.107 | 0.087 / 0.073 | 0.073 / 0.067 | 0.073 / 0.073 |

Số này khớp với số của agent rà soát. **Đây là giới hạn hữu hạn mẫu, không mâu thuẫn Thm 3** vốn cố định K. λ lớn đưa mức về đúng, nhưng làm yếu lợi ích từ R² (Mệnh đề 8). V1 và seminorm theo khối giữ mức tốt hơn nhiều ở K lớn; seminorm theo khối ở đây chỉ đo phần khối I tại mô hình đúng, chưa phải toàn bộ thủ tục.

**FWER thật** (họ DAG; η = β; 400 replicate; khoảng là cận dưới và trên, vì khi quá nhiều orthant phải duyệt thì mô hình bị xếp "chưa rõ"):

| Cấu hình K = 70 | P(W_n > ĉ_n) | Khoảng FWER |
|---|---|---|
| Mọi DAG (7452 pattern), hai cạnh .5, n = 200–5000, λ = n^{-1/3} | 0.058–0.110 | [0, 0] |
| DAG cục bộ, h = 6, chain/collider/hai cạnh, n = 500–5000, λ = n^{-1/3} | 0.035–0.087 | cao nhất [0.003, 0.003] |
| DAG cục bộ, h = 3, n = 500–5000, λ = n^{-1/3} | 0.045–0.092 | cao nhất [0, 0.052] |
| DAG cục bộ, h = 3, n = 1000, λ = 2 | 0.018–0.043 | cao nhất [0, 0.010] |

Họ cục bộ (DAG cách truth tối đa 2 bước sửa cạnh, 107–119 pattern) là lựa chọn bảo thủ: nếu f được assert trong M thì cũng được assert trong họ con chứa truth, trừ khi C_n của họ con rỗng. Ở **K = 165** (họ cục bộ, 230–255 pattern, chain và collider, h = 3, λ = n^{-1/3}; mỗi dòng có giới hạn 180 giây nên chỉ đạt 121–171 replicate, SE khoảng 0.02): P(W_n > ĉ_n) = 0.13 ở n = 500 và 0.09–0.11 ở n = 1000; khoảng FWER [0, 0.050], [0, 0.030], [0, 0.031], [0, 0.041]. **K = 616 chưa đo FWER.**

Tóm lại, ở K = 70 và 165, FWER thật không vượt α đáng kể trên các kịch bản này, dù cận P(W_n > ĉ_n) vượt. Đây là các SCM ít cạnh; kịch bản khó hơn chưa được thử, nên chưa thể xem là bảo đảm.

### 8.3 Blindness (Thm 4, chỉ đại số tuyến tính, tại R tổng quát)

| Cấu hình | K | rank | Pattern mù / tổng |
|---|---|---|---|
| p = 3, bậc ≤ 1, R tổng quát | 6 | 3 | **7/11** |
| p = 3, bậc ≤ 1, R = I | 6 | 3 | 1/11 (chỉ mô hình đầy đủ) |
| p = 4, bậc ≤ 1 | 18 | 6 | **99/137** |
| p = 4, bậc ≤ 2 | 24 | 6 | **178/185** |

Ở p = 3, mọi pattern được (B1)–(B2) đánh dấu mù đều có d² = 0 trên các z ngẫu nhiên, và mọi pattern không mù đều có d² > 0 ở một z nào đó (p = 4 chỉ kiểm bằng đại số tuyến tính). Ví dụ cực đoan: chain X⊥Y|Z với z_{XY|Z} = 40 vẫn có d²_seminorm = 0, trong khi ridge cho 1454 ≥ 40²/(1+λ).

**Ở mức feature, kể cả khi M bị hạn chế** (kiểm tra L; p = 4, feature "X ∈ An(Y)" và phủ định, 24 feature không vacuous; cùng kết quả tại hai R tổng quát khác nhau):

| M = DAG có tối đa e cạnh | Pattern mù / tổng, K = 18 | Feature có T ≡ 0, K = 18 | Pattern mù / tổng, K = 24 | Feature có T ≡ 0, K = 24 |
|---|---|---|---|---|
| e ≤ 1 | 0/7 | 0/24 | 0/7 | 0/24 |
| e ≤ 2 | 0/34 | 0/24 | 27/34 | **24/24** |
| e ≤ 3 | 56/94 | **24/24** | 87/94 | **24/24** |
| e ≤ 6 (mọi DAG) | 99/137 | **24/24** | 178/185 | **24/24** |

Vậy blindness không phải hiện tượng riêng của M đầy đủ, nhưng cũng không phải hệ quả của K > rank: ở K = 18 với e ≤ 2 không có gì mù. Trong các pattern p = 4 ở K = 18, có 127 pattern thỏa |D| > r nhưng chỉ 99 pattern mù (điều kiện cần, không đủ; số của agent rà soát, đã đo lại ở kiểm tra W). Chỉ xét DAG, chưa tính MAG có bidirected; họ MAG lớn hơn chứa các DAG này nên kết luận "T ≡ 0" giữ nguyên khi M là mọi MAG.

Trên dữ liệu Gaussian (S2, S3 là hai SCM có feature Q-identifiable; 100 replicate mỗi dòng), **V1 chứng nhận 0% ở mọi dòng**, trong khi V2 trên cùng dữ liệu đạt tới 0.99 (§8.4).

### 8.4 False certification trên họ DAG p = 3 (25 DAG, 11 pattern, 12 feature, 2000 replicate mỗi dòng)

24 dòng có ζ_n ∈ R_n(m*): **0 vi phạm bao hàm của Thm 1**. P(W_n > ĉ_n) ∈ [0.040, 0.066] (SE 0.005). FWER thô tối đa 0.035; **có abstain tối đa 0.003**: phần lớn sai chứng nhận đến từ sự kiện C_n = ∅. R1 chiếu rất bảo thủ so với α, tức để lãng phí ngân sách lỗi; đây là động lực của R1′.

Đối chứng âm η = 2β (S1, ζ_n ∉ R_n(m*)): FWER thô 0.955–1.000, nhưng C_n rỗng ở đúng các replicate đó nên có abstain thì FWER = 0. **Không được đọc thành "η sai là an toàn"**: nếu một mô hình sai sống sót thì sai chứng nhận xảy ra với xác suất cao (§8.6).

Tỷ lệ chứng nhận feature đúng, Q-identifiable (mô tả, **không phải so sánh power**):

| SCM | n | η = ½n^{-1/4} | η = β |
|---|---|---|---|
| S2 collider | 200 / 1000 / 5000 | 0.00 / 0.10 / 0.83 | 0.00 / 0.90 / 0.99 |
| S3 một cạnh | 200 / 1000 / 5000 | 0.01 / 0.96 / 0.98 | 0.97 / 0.97 / 0.97 |

S1 (chain) và S4 (đầy đủ) không có feature tổ tiên Q-identifiable nào: MEC của chúng không có quan hệ tổ tiên bất biến. Ở S3, trần 0.97–0.98 khớp với 1 − P(C_n = ∅), đúng như Thm 5(iii).

### 8.5 R2

Năm cấu hình, 300 replicate mỗi cấu hình: P(E_n) = 0.94–0.96; **0 vi phạm** cả (b1) và (b2) của Thm 7; tính đơn điệu và Lipschitz đúng trên mọi bước thử. Với S2: trung bình √n·η*(f) = 3.40 (n = 1000) và 3.59 (n = 5000), nhất quán với √n·η*(f) = O_p(1), và cỡ η*(f) ≈ 0.11 ở n = 1000.

### 8.6 CT và R1 (Mệnh đề 7; 1000 replicate mỗi dòng, SE ≈ 0.007 tại α)

| Kịch bản | √nη | FWER R1 | FWER CT | Chứng nhận R1 | Chứng nhận CT |
|---|---|---|---|---|---|
| Pointwise S2, η = ½n^{-1/4}, n = 200 | 1.88 | 0 | 0 | 0.00 | 0.58 |
| n = 1000 | 2.81 | 0 | 0 | 0.10 | 0.84 |
| n = 5000 | 4.20 | 0 | 0 | 0.82 | 0.96 |
| n = 20000 | 5.95 | 0 | 0 | 1.00 | 1.00 |
| **Cục bộ, chain yếu, n = 2000**, h = 2 | 2 | 0 | **0.112** | — | — |
| h = 3 | 3 | 0.003 | 0.043 | — | — |
| h = 4 | 4 | 0.003 | 0.008 | — | — |
| h = 8 | 8 | 0 | 0 | — | — |
| Cục bộ, collider yếu, n = 2000, h = 2 | 2 | 0 | 0 | 0.00 | 0.65 |
| h = 3 | 3 | 0 | 0 | 0.17 | 0.84 |
| h = 4 | 4 | 0 | 0 | 0.77 | 0.94 |
| h = 6 | 6 | 0 | 0 | 0.991 | 0.995 |

**Đọc bảng:** ở pointwise, CT trội R1 như Mệnh đề 7 dự đoán. Ở cục bộ, CT **vi phạm mức α trên chain**, còn FWER của R1 = 0 ở đó **không nói lên gì**: chain không có feature Q-identifiable nên R1 gần như không có gì để assert. Trên collider, CT có tỷ lệ chứng nhận cao hơn và FWER = 0, nhưng đó **không phải đối thủ hợp lệ** vì CT không có bảo đảm đều qua các SCM. Log còn có các dòng S1 với η = 1.5n^{-1/4} (η > β ở n nhỏ, FWER ≤ 0.002) mà bản trước không đưa vào bảng; chúng không đại diện, xem kịch bản dưới đây.

FWER của CT trên chain với 50000 replicate: 0.212 / 0.128 / 0.047 / 0.014 / 0.0005 ở h = 1 / 2 / 3 / 4 / 6. Vậy h_CT = 5.28 (K = 6) chỉ là điều kiện đủ, và trên họ p = 3 này CT đã dưới α từ h = 3.

**Khi η > β** (collider hệ số 0.5 và 0.05, β = 0.022, M = 25 DAG, K = 6, 600 replicate):

| η = 0.2, n | 200 | 500 | 1000 | 2000 | 5000 | 10⁴ | ≥ 2·10⁴ |
|---|---|---|---|---|---|---|---|
| FWER CT | 0.547 | 0.803 | 0.922 | 0.988 | 1 | 1 | 1 |
| FWER R1, có abstain | 0.810 | **0.907** | 0.838 | 0.640 | 0.185 | 0.003 | 0 |
| FWER R1, không abstain | 0.810 | 1 | 1 | 1 | 1 | 1 | 1 |
| FWER BL1 | 0.158 | 0.910 | 0.833 | 0.618 | 0.158 | 0 | 0 |

| η = 0.04 ∈ (β, 2β), n | 1000 | 5000 | 2·10⁴ | 5·10⁴ | 10⁵ |
|---|---|---|---|---|---|
| FWER CT / chứng nhận CT | 0.138 / 0.31 | 0.020 / 0.45 | 0 / 0.61 | 0 / 0.73 | 0 / 0.75 |
| FWER R1 / chứng nhận R1 | 0 / 0 | 0.162 / 0.20 | 0 / 0.01 | 0 / 0 | 0 / 0 |
| FWER BL1 / chứng nhận BL1 | 0 / 0 | 0.003 / 0.14 | 0 / 0.55 | 0 / 0.11 | 0 / 0 |

Hai bảng cho thấy: giả định η sai làm R1 sai nặng ở cỡ mẫu vừa. R1 tự dừng khi n lớn nhờ C_n rỗng, BL1 cũng vậy, và ở cỡ mẫu nhỏ BL1 thường ít sai hơn R1. Quy tắc abstain là cần thiết.

### 8.7 Ngưỡng và noncentrality (giải tích, α = 0.05)

| p, bậc | K | r | c_r = χ²_{r,.95} | t²_K | c_r/t²_K | K_crit(r) | K_full(p) | h_CT = 2t_K |
|---|---|---|---|---|---|---|---|---|
| 3, 1 | 6 | 3 | 7.81 | 6.96 | 1.12 | 9.6 | 6 | 5.28 |
| 4, 2 | 24 | 6 | 12.59 | 9.47 | 1.33 | 129 | 24 | 6.16 |
| 5, 2 | 70 | 10 | 18.31 | 11.45 | 1.60 | 2.7×10³ | 80 | 6.77 |
| 5, 3 | 80 | 10 | 18.31 | 11.70 | 1.56 | 2.7×10³ | 80 | 6.84 |
| 10, 2 | 1665 | 45 | 61.66 | 17.42 | 3.54 | 1.2×10¹³ | 11520 | — |
| 20, 2 | 32680 | 190 | 223.2 | 23.11 | 9.66 | 2.7×10⁴⁸ | 5.0×10⁷ | — |

K_full(p) < K_crit(r) đã kiểm tra cho p = 3,…,30. Với Q nhỏ, K_crit(1) = 1, K_crit(2) ≈ 3.5, K_crit(3) ≈ 9.6, K_crit(4) ≈ 24.

Bảng noncentrality của bản trước đã bị **rút lại**: cột R1′ dùng ngưỡng không valid trong regime cục bộ, và NCP viết theo Σ⁻¹ thay vì metric ridge (M3).

**Bảng thay thế:** h² = ζ_k² cần cho power 90% ở đối thủ thêm một độc lập, working model, metric ridge, chỉ ngưỡng valid. Ba số trong mỗi ô ứng với R² = 0 / 0.5 / 0.9. Cột hybrid và các cột theo mô hình đều dùng ngân sách α/2 trên khối I′, phần còn lại dành cho phía D.

| K, r, \|I′\| | λ | R1 chiếu | Hybrid χ² | Contrast sau whitening | BL1 | Bonf. theo mô hình | R² hòa vốn: chiếu vs BL1 | R² hòa vốn: hybrid vs Bonf. theo mô hình |
|---|---|---|---|---|---|---|---|---|
| 6, 3, 2 | 0.1 | 15.9 / 8.9 / 3.2 | 14.7 / 7.8 / 2.4 | 14.3 / 7.2 / 1.5 | 15.4 | 14.3 | 0.04 | 0.03 |
| 6, 3, 2 | 0.5 | 17.7 / 12.4 / 7.8 | 14.8 / 9.5 / 5.3 | 14.3 / 7.9 / 2.9 | 15.4 | 14.3 | 0.22 | 0.04 |
| 18, 6, 2 | 0.1 | 23.2 / 13.1 / 4.9 | 14.8 / 7.8 / 2.4 | 14.3 / 7.2 / 1.5 | 18.3 | 14.3 | 0.24 | 0.04 |
| 18, 6, 2 | 0.5 | 26.8 / 19.2 / 12.7 | 14.8 / 9.4 / 5.4 | 14.3 / 7.9 / 2.9 | 18.3 | 14.3 | 0.56 | 0.05 |
| 24, 6, 3 | 0.1 | 22.2 / 12.6 / 4.7 | 16.4 / 9.0 / 2.9 | 15.4 / 7.7 / 1.7 | 19.0 | 15.4 | 0.17 | 0.07 |
| 24, 6, 3 | 0.5 | 26.6 / 19.2 / 12.6 | 16.4 / 10.9 / 6.5 | 15.4 / 8.5 / 3.1 | 19.0 | 15.4 | 0.51 | 0.09 |
| 70, 10, 3 | 0.1 | 30.7 / 17.4 / 6.7 | 16.3 / 8.9 / 2.9 | 15.4 / 7.7 / 1.7 | 21.8 | 15.4 | 0.34 | 0.07 |
| 70, 10, 3 | 0.5 | 37.9 / 27.6 / 18.7 | 16.5 / 10.9 / 6.5 | 15.4 / 8.5 / 3.1 | 21.8 | 15.4 | 0.77 | 0.09 |
| 70, 10, 6 | 0.1 | 27.2 / 15.5 / 5.9 | 20.0 / 11.0 / 3.9 | 17.2 / 8.7 / 1.8 | 21.8 | 17.2 | 0.23 | 0.16 |
| 70, 10, 6 | 0.5 | 34.6 / 25.1 / 17.1 | 20.0 / 13.8 / 8.7 | 17.2 / 9.6 / 3.4 | 21.8 | 17.2 | 0.67 | 0.22 |

Cận NP cho mọi thủ tục là h² = 8.6(1−R²). Hòa vốn là nội suy tuyến tính trên lưới R² = 0, .1, .25, .5, .75, .9, .99.

**Đọc bảng:**
- Trên cả 70 ô đã tính (10 cấu hình × 7 giá trị R²), **contrast không cần tín hiệu lớn hơn hybrid hay chiếu**. Ở R² = 0 contrast trùng Bonferroni theo mô hình. Chiếu thua hybrid rất xa khi K lớn.
- Hybrid hơn Bonferroni theo mô hình khi R² vượt khoảng 0.03–0.22. Chiếu hơn BL1 chỉ khi R² vượt 0.04–0.77; tăng λ để giữ mức làm ngưỡng này cao lên rõ rệt.
- **Thiết kế này thuận lợi cho contrast:** tín hiệu chỉ ở một tọa độ. Contrast đo ở đây dùng hệ số ridge tại đúng tọa độ k. Khi không biết k, có thể dùng MaxT trên Σ_{I′I′}⁻¹z đã chuẩn hóa, có cùng NCP ở λ → 0 mà không phụ thuộc thứ tự [Derived, chưa mô phỏng].
- **Hệ quả:** ở đối thủ một tọa độ, dạng χ² không có lợi thế trước một đối thủ dạng hộp đã whitening. Lợi thế riêng của nó, nếu có, chỉ có thể đến từ tín hiệu trên nhiều tọa độ, và điều này chưa được đo.

Bảng này là tính toán trong working model cho một đối thủ, **không phải mô phỏng power trên SCM**.

### 8.8 Điều kiện yếu của Thm 3 và ngưỡng chi-bar

**Thm 3 dưới nλ_n → ∞ nhưng √nλ_n → 0** (λ = n^{-3/4}; 10000 replicate với Q₂, 2500 với K = 24):

| n | 1000 | 5000 | 2·10⁴ | 10⁵ |
|---|---|---|---|---|
| Q₂, 4 giá trị của a | 0.043–0.048 | 0.047–0.051 | 0.047–0.051 | 0.047–0.054 |
| K = 24 | **0.151** | 0.117 | 0.110 | 0.075 |
| K = 24, λ = n^{-1/3} (đối chứng) | 0.060 | 0.051 | 0.060 | 0.043 |

Phù hợp với định lý ở K nhỏ, nhưng ở K = 24 hội tụ rất chậm. Điều kiện yếu chỉ có giá trị lý thuyết; thực hành nên dùng λ lớn hơn.

**Chi-bar tại điểm bất lợi nhất** (working model, K = 3, I = {1}, D = {2, 3}, δ = 25). Lần chạy trong script cho tối đa 0.0534 vì các ngưỡng dùng chung một mẫu hiệu chỉnh 40000 điểm. Kiểm tra lại với mẫu hiệu chỉnh riêng cho từng orthant, 150000 điểm, seed mới: P(bác bỏ) tại đỉnh của chính ngưỡng đó là 0.0496–0.0509 (SE 0.0006), tại c̄_m cao nhất 0.0496. Vậy 0.0534 là nhiễu hiệu chỉnh và **chi-bar đạt đúng α tại đỉnh bất lợi nhất**. Kiểm tra lại này là script tạm, không nằm trong artifact.

**Chi-bar trên dữ liệu Gaussian** (K = 6, |D| = 5, collider yếu, n = 2000, h = 2, 4, 8, 3000 replicate; c̄_m hiệu chỉnh tại Σ tổng thể): P(bác bỏ m*) ≈ 0.006 với chi-bar (c̄_m ≈ 7.2–7.4), so với 0.063–0.077 với ngưỡng pointwise ở Thm 6(a). Tức chi-bar valid nhưng **rất bảo thủ** khi chỉ một trong năm tọa độ D nằm gần biên, vì nó trả giá cho trường hợp xấu nhất. Đây vẫn là một cấu hình, nên Thm 6(c) cho dữ liệu Gaussian giữ nhãn Sketch.

### 8.9 Minh bạch về quy trình

- Lần quick đầu có 2 FAIL ở kiểm tra H. Cả hai do **tôi chọn sai kịch bản**, không phải định lý sai: (a) S1 chain không có feature Q-identifiable nên mẫu số power rỗng; (b) collider cục bộ không tạo được sai chứng nhận cho CT vì các pattern nhầm không có feature bất biến nào. Tôi đổi sang S2 cho power và chain cho FWER, và **giữ** các dòng collider vì chúng có thông tin. Lý do ghi ngay trong script.
- Quy tắc abstain được thêm sau khi quick-run cho thấy FWER trùng P(C_n = ∅). Bảng ở trên báo cáo cả hai cách tính.
- λ_n, τ_n và dung sai được khai báo trong script trước lần chạy đầy đủ, nhưng đã có quick-run trước đó, nên **không phải pre-registration chặt**.
- Kiểm tra K được thêm sau quick-run để cố tìm vi phạm. Nó không tìm thấy vi phạm của Thm 3, nhưng tìm thấy các dòng V0/oracle anti-conservative ở §8.1.
- Kiểm tra L được thêm sau lần chạy chính để trả lời một câu hỏi mở thật: card C1 trong `reports/literature_gap_2026-11-04_vi/` (một phiên song song) ghi nhận blindness nhưng nêu "chưa có kết quả feature-level".
- Andrews 1987 không tải được bản đầy đủ (trang trả HTML), nên chỉ trích ở mức tóm tắt và qua Dufour–Valéry.
- **Assertion yếu** do agent rà soát chỉ ra, chưa được viết lại trong `RG1_numeric_checks.py`: size chỉ kiểm ở n = 5000 với dung sai rộng; `E.Lipschitz` gần như không thể fail; `G.noncentral` là đồng nhất thức; `H.R1 FWER` trên chain không thể fail; `I.chi-bar` chỉ dùng δ = 2 nên không chạm điểm bất lợi nhất. Kiểm tra W của script mới bù phần chi-bar (§8.8). Bảng đuôi dùng chung cũng gây lệch cố định khoảng 0.001–0.002.
- Lần chạy đầu của `RG1_followup_checks.py` bị hệ thống dừng vì máy thiếu bộ nhớ, không phải do lỗi script. Lần chạy lại, do user yêu cầu, hoàn tất; P, Q, R và các dòng K = 70 của T trùng khớp hoàn toàn với lần đầu. Các dòng K = 165 có giới hạn thời gian, nên **số replicate phụ thuộc tốc độ máy và không tái lập chính xác**.
- Thiết kế đầu tiên của kiểm tra T sai: các truth có đường dài cho β rất nhỏ (√nβ < 1), nên FWER = 0 chỉ vì η ≈ 0. Tôi phát hiện ở quick-run và đổi sang truth cục bộ với h cố định.

---

## 9. Prior art và novelty sau RG1

| Thành phần | Nguồn | Trạng thái đọc | Hệ quả |
|---|---|---|---|
| Confidence set mô hình ⇒ feature bất biến | Wang–Kolar–Drton 2026, Lemma 3 (+ supplement) | Source-verified | Thm 1 là cùng lập luận |
| Kiểm định minimum-discrepancy theo mô hình | Browne 1984 | Source-verified (register §5.2) | Khung cổ điển |
| IUT; LFC tại đỉnh nón | Berger 1982; Silvapulle–Sen 2005, Thm 3.8.1 | Source-verified | Thm 6(c) là áp dụng |
| g-inverse giữ χ² khi rank hội tụ | [Andrews 1987](https://econpapers.repec.org/RePEc:cup:etheor:v:3:y:1987:i:03:p:348-358_01); Lütkepohl–Burda 1997 | [ABSTRACT], qua Dufour–Valéry | Thm 2 chứng minh lại trực tiếp |
| Regularized Wald (Tikhonov, spectral cut-off), giới hạn tổ hợp χ² có trọng số; spectral cut-off "destroy power" | [Dufour–Valéry, WP 02/2011](https://webarchive.ucr.edu/economics.ucr.edu/wp-content/uploads/2019/10/Valery-paper-updt-2-for-2-7-11-seminar.pdf), Prop 8.1, Cor 8.2–8.7, Prop 10.1. **Chưa xác minh bản công bố** | Source-verified WP | **V2 không mới về kỹ thuật.** Khác biệt có thể có: phát biểu đều trên compact và trường hợp λ_n → 0 với chi phí null phân kỳ, là biến thể trực tiếp |
| Giới hạn ¼χ²₁ tại điểm kỳ dị | Glonek; [Drton–Xiao 2016](https://arxiv.org/abs/1304.6746), Thm 2.3 | Source-verified | Mệnh đề 3 là áp dụng |
| Wald không đều ở ràng buộc suy biến | [Dufour–Renault–Zinde-Walsh](https://arxiv.org/abs/1312.0569) (arXiv 2013; AoS 2025 theo metadata) | Đọc phần mở đầu | Không tuyên bố tổng quát cho V0 |
| Uniform consistency, strong faithfulness | Robins et al. 2003; Zhang–Spirtes 2003; Uhler et al. 2013 | Source-verified (abstract, register) | Định vị Thm 7, Mệnh đề 7 |

Bốn nguồn có URL ở trên nằm ngoài `docs/papers/` và **chưa được thêm vào corpus**; nếu RG1 được dùng để viết bài thì nên tải về và đọc lại, nhất là bản công bố của Dufour–Valéry và toàn văn Andrews.

**Đánh giá trung thực [Inference]:** không có định lý nào ở đây là đột phá. Toàn bộ lõi là các kỹ thuật cổ điển được ghép đúng cách. Những phần tôi **chưa thấy** trong nguồn đã đọc (không có nghĩa là chưa ai làm):
- (a) đặc trưng (B1)–(B2) và hệ quả "R1-seminorm rỗng nghĩa" cho hợp vùng tọa độ của MAG;
- (b) phân loại regime ở §5, cho thấy pointwise không phân biệt;
- (c) ngữ nghĩa η-profile (b1)–(b2) cùng η̄.

Đây là đóng góp hạng **phương pháp/công cụ**, chỉ có giá trị nếu RG2/RG3 cho thấy power. Rủi ro novelty ở readiness §11 **không giảm**.

---

## 10. Hệ quả cho các gate và errata

### 10.1 Định nghĩa R1 sau RG1

R1 là thủ tục ở §1.3 với metric ridge, kèm abstain khi C_n rỗng, và **λ phải khai báo theo K** (§8.2). Về ngưỡng: hybrid (Thm 6(d)) có chứng minh đầy đủ trên dữ liệu Gaussian nhưng **RG3 cho thấy nó không có lợi thế nào so với box** (`RG3_S1_report_vi.md`), nên thủ tục có tín hiệu là thống kê T với ngưỡng chiếu hoặc chi-bar (Thm 6(c), bản Gaussian còn là Sketch và chi phí 2^{|D|}). Seminorm theo khối (Hệ quả 4.1(e)) là ứng viên thứ ba, chưa có chứng minh. Báo cáo (η*(f), η̄) theo Thm 7.

### 10.2 Errata cho tài liệu trước

| Vị trí | Phát biểu | Sửa |
|---|---|---|
| Contract §7 R1, readiness §0.2 | "Seminorm + χ²_rank tránh được B1" | Validity đúng nhưng rỗng nghĩa khi M_¬f chứa mô hình mù: Thm 4 |
| Contract §2.4 C-d | Ridge: "kết quả do quy ước quyết định" | Tiệm cận: cần nλ_n → ∞ (Thm 3, Nhận xét 3.5); hữu hạn mẫu: λ phải đủ lớn so với K (§8.2) |
| Contract §4-P2 | P2 cần Σ PD | Với V2 không cần: Thm 5 |
| Contract §7 R2 | η*(f) = inf{η : f được chứng nhận} | Phải kèm η̄ (Thm 7c) |
| Contract §10b, readiness §11.4 | Pointwise làm R1 "dễ bảo vệ", R2 "phần phụ" | Pointwise không phân biệt (Mệnh đề 7); R2 là phần có nội dung |
| Mệnh đề R (contract §2.4) | rank ≤ min(K, d) | Mạnh hơn: Mệnh đề 2 (bằng span gradient; = d khi Q chứa query biên) |
| Toy §4.2 | Plug-in "bảo thủ" chưa giải thích | Mệnh đề 3 |

### 10.3 Trạng thái RG1

Đã có kiểm tra độc lập bởi agent AI (`PASS WITH CORRECTIONS`) và các sửa chữa đã áp dụng (§12). **RG1: PASS có điều kiện, user duyệt ngày 2026-11-05.** Điều kiện: trước khi dùng cho bài báo cần người đọc Thm 3, Thm 4; các phần mới viết trong lượt sửa chưa được rà lại. Nhánh seminorm toàn cục của R1 **rớt** điều kiện power và được sửa (đúng nhánh "Fail ⇒ Sửa" của gate).

### 10.4 Đề xuất sửa đặc tả RG2 (chưa duyệt, chưa chạy)

> **Cập nhật 2026-11-06:** phép thử T so với hộp whitening đã xong (`RG3b_report_vi.md`): không có khác biệt rõ theo luật khai báo trước; T nhỉnh hơn nhẹ ở K = 24, gần hòa ở K = 70. RG2 chưa chạy; khuyến nghị chuyển sang T4, chờ user quyết định.

Tôi **cố ý không so power với Bonferroni trên mô phỏng** ở RG1, để RG2 còn pre-register được.

- **Regime:** trong lớp η ≤ β, h = √nη < 2t_K (§5), lưới h từ 1 tới 2t_K. Thêm một nhánh η > β để đo hành vi khi giả định sai.
- **Điều kiện tiên quyết:** phải dựng được ít nhất một kịch bản mà CT vượt α và R1 có power dương (§5). Nếu không dựng được, đó là tín hiệu mạnh để dừng.
- **Thủ tục:** hybrid, ngưỡng chiếu, chi-bar khi |D| nhỏ, seminorm theo khối; λ khai báo theo K trước khi chạy và K ≥ 70 có mặt trong kiểm tra size.
- **Đối thủ valid:** BL1, Bonferroni theo mô hình, MaxT theo mô hình, **contrast/MaxT sau whitening** (§8.7), BL9 nếu định nghĩa được. CT chỉ để mô tả.
- **Tín hiệu:** phải có cả đối thủ khác nhiều tọa độ, vì ở một tọa độ χ² không thể hơn contrast.
- **Tiêu chí kill đề xuất:** nếu các thủ tục R1 không hơn đối thủ valid tốt nhất ở cùng mức valid tại các cấu hình xuất hiện thực tế, STOP A′. Ngưỡng "hơn đáng kể" là quyết định quản lý, cần user chốt trước khi chạy.
- **Thứ tự:** làm RG3 sớm. Đại lượng cần đo là R²_{k|I} và phân bố số tọa độ khác nhau giữa truth và đối thủ gần nhất; cả hai tính giải tích được bằng (2.1).

**Dự đoán (không phải kết quả trên SCM):** ở đối thủ một tọa độ, χ² không hơn contrast đã whitening ở mọi R² đã tính, và chiếu thua hybrid xa khi K lớn (§8.7). Ưu thế riêng của χ² chỉ có thể đến từ tín hiệu trên nhiều tọa độ. Chưa biết trường hợp này phổ biến đến đâu; đây là câu hỏi quyết định của hướng A′.

---

## 11. Giới hạn và checklist rà soát

**Giới hạn:**
- Chỉ Gaussian; p, K cố định. Không có phát biểu high-dimensional.
- Q thích nghi trên cùng mẫu không được phủ. Selection nằm ngoài phạm vi. GCM/phi tham số: **chưa có** (Lemma 1 dùng dạng toàn phương Gaussian ở bước Lyapunov).
- Mô phỏng họ đầy đủ ở p = 3 và K = 70 (p = 5), họ cục bộ ở K = 70, 165. **Không có MAG có bidirected trong mô phỏng**; các định lý không phụ thuộc điều này vì chỉ dùng pattern π, nhưng power trên MAG chưa đo.
- Power mất do relaxation R_n ⊋ A_n chưa được lượng hóa. Chi phí tính toán khi K lớn chưa đo có hệ thống, nhưng đã thấy: đo FWER ở K = 70 trong regime h = 3 mất cỡ một phút cho 400 replicate trên khoảng 110 pattern, và với 7452 pattern thì không khả thi nếu không có sàng lọc.
- Thm 6(c) cho dữ liệu Gaussian mới là Sketch. Tính đều của V1 khi Q không chứa chart là [Open]. Size đều của seminorm theo khối khi rớt rank trong khối là [Open].
- FWER thật ở K = 165 có SE lớn, K = 616 chưa đo; chỉ trên SCM ít cạnh.
- Andrews 1987 chỉ đọc tóm tắt và qua nguồn thứ cấp. Bản đầy đủ không tải được.

**Chỗ người rà soát tiếp theo nên tấn công trước** (lượt agent AI đã qua các mục 1–5; phần mới viết ở Bước 1, Bước 4 của Thm 3 và chiều ngược của Thm 4 chưa được rà lại):
1. Lemma 1(c): tính đều của phần dư trên 𝓚.
2. Thm 3 Bước 3–4: CLT sau chuẩn hóa khi trị riêng → 0; tính liên tục của quantile.
3. Thm 4 Bước 2: (N∩C_I^⊥)^⊥ = 𝓛 + C_I; hợp hữu hạn không gian con.
4. Mệnh đề 3: khai triển 1 − Σ̂₁₂ và triệt tiêu số hạng u²/n.
5. Thm 7(a): điểm mút của {η : d²_η > ĉ}.
6. Mệnh đề 7(iii) và cột "R1 có nội dung" ở §5: có regime nào khác không?
7. Câu hỏi nền: abstain khi C_n rỗng có làm hỏng phát biểu power nào không?

---

## 12. Xử lý kết quả rà soát độc lập

Báo cáo gốc: `RG1_independent_review_vi.md`; script của agent: `RG1_review_scripts/`. Tôi đã tự kiểm lại các chứng minh mà agent đề xuất trước khi đưa vào.

| Nhãn | Nội dung | Xử lý | Vị trí |
|---|---|---|---|
| M1 | "Regime duy nhất" chỉ đúng khi η ≤ β | Sửa; số đo lại độc lập | §0, §5, §8.6 |
| M2 | Ridge vượt mức nặng ở K lớn | Sửa; số đo lại; đo thêm FWER thật ở K = 70 | §0, §8.2, §10.1 |
| M3 | Cột R1′ không valid; NCP sai metric; thiếu contrast | Rút bảng cũ, sửa diễn giải, tính bảng mới | Mệnh đề 8, §8.7, §10.4 |
| M4 | "T(f) ≡ 0 khi K > rank" sai; seminorm theo khối bị bỏ qua | Sửa; thêm ứng viên | §0, Hệ quả 4.1, §10.1 |
| M5 | "power → 1" với abstain | Sửa | §0 |
| M6 | Mệnh đề 5(iii) thiếu điều kiện C_n ≠ ∅ | Sửa | Mệnh đề 5 |
| M7 | Đánh giá thấp mức hỏng của oracle và V0 | Sửa; số đo lại | Mệnh đề 3, §8.1 |
| M8 | Thm 3 chỉ cần nλ_n → ∞; V1 chỉ cần nτ_n → ∞; Nhận xét 3.5 chỉ cho oracle | Sửa chứng minh; số đo lại | Thm 2, Thm 3, Nhận xét 3.5 |
| M9 | Trội chỉ cho ngưỡng không đều; c̄_m ≤ ĉ_n | Sửa; đổi thứ tự ưu tiên sang hybrid | Thm 6, §10.1 |
| M10 | Chiều ngược của (B1)–(B2); phạm vi câu về V1; điều kiện bảng §5 | Sửa | Thm 4, Thm 5, §5 |
| S1 | Chưa có kịch bản CT vượt α và R1 có power dương | **Chưa giải quyết**; thành điều kiện tiên quyết của RG2 | §5, §10.4 |
| S2 | Chi-bar trên Gaussian chỉ kiểm rất hạn chế | **Thu hẹp, chưa giải quyết**: thêm một cấu hình \|D\| = 5, valid nhưng rất bảo thủ; vẫn là Sketch | Thm 6(c), §8.8 |
