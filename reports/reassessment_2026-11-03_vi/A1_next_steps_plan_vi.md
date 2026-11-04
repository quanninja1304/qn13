# Kế hoạch các bước tiếp theo cho A′ — Dependence-aware feature confidence

> **Ngày lập:** 03-11-2026. **Cập nhật:** 04-11-2026. **Trạng thái plan:** v0.3, *chưa có bước nào được thực hiện*.
> **Tài liệu PDF:** danh sách có/thiếu ở **§12**. Agent không tự tìm PDF; user bổ sung vào `docs/papers/`.
> **Trạng thái A′:** Primary (Conditional), **chưa Go**. Độ tin vào H-rank đã giảm, hypothesis chính là H-cal.
> **Nguồn đầu vào:** [`00_final_reassessment_vi.md`](00_final_reassessment_vi.md) (Report G/H/J), [`A1_gap_confirmation_and_proof_sketch_vi.md`](A1_gap_confirmation_and_proof_sketch_vi.md) (Phần 2–4), [`topic_cards/A1_dependence_aware_feature_confidence_vi.md`](topic_cards/A1_dependence_aware_feature_confidence_vi.md).
> **Quy ước nhãn:** [Verified], [Inference], [Hypothesis], [Unresolved], [Proposal — cần chốt]. Mọi số liệu trong file này là *thiết kế*, không phải kết quả.

---

## 0. Cách dùng file này để backtrack

1. **Mỗi phase có ID** (`A′-P0` … `A′-P7`), **mỗi gate có ID** (`GA0` … `GA6`). Mọi artifact, commit, run log phải ghi ID phase tương ứng.
2. **Decision log (§9) là append-only.** Khi qua hoặc rớt gate, thêm một dòng: ngày, gate, kết quả, bằng chứng (đường dẫn), quyết định, người chốt. Không sửa dòng cũ; nếu đảo quyết định thì thêm dòng mới tham chiếu dòng cũ.
3. **Mỗi gate có "điểm quay lui"** (§8): nếu rớt, quay về đâu, giữ lại artifact nào, bỏ giả định nào.
4. **Pre-registration (§3)** phải được *đóng băng* (commit + hash ghi vào §9) trước khi chạy confirmatory seeds. Sửa sau khi đóng băng phải ghi là *deviation* trong §9.
5. **Changelog (§10)** ghi mọi thay đổi của chính plan này (version, lý do).
6. Khi tiếp tục ở phiên mới: đọc §1 (snapshot) → §9 (dòng cuối) → phase đang mở trong §4.

---

## 1. Snapshot xuất phát (03-11-2026)

| Hạng mục | Trạng thái | Nguồn |
|---|---|---|
| Gap sau Guo–Wu–Yiu (UAI 2026) | Còn sống [Verified-full] | A1 §1.1 |
| Gap sau BSC-D (ECML-PKDD 2017) | Còn sống nhưng hẹp; BSC-D không thấy đổi thứ tự PAG/SHD → chuyển sang H-cal | A1 §1.2, §4.2 |
| Đe dọa full-likelihood feature posterior | Mở; A′ định vị lại cho CI statistics tổng quát (kernel/GCM/mixed) | A1 §1.3 |
| P1, P2, P3, P5, P6, P7 | Chứng minh rút gọn | A1 Phần 3 |
| P4 (non-separability) | Chỉ K=2, ràng buộc inactive; K tổng quát **[Open]** | A1 P4 |
| (A1) cho GCM/kernel, bootstrap Σ̂ consistency | **[Open]** | A1 bảng tóm tắt |
| Implementation ACI / BSC-D / MAG enumeration / dist QP | **Chưa có** trong repo | kiểm tra `src/safety_prior/` |
| Hạ tầng tái sử dụng được | `graphs.generate_dag` (có latent), `ci.OracleCI`, `ci.GaussianCI`, `causal-learn==0.1.4.8`, `networkx`, `scipy` | `src/safety_prior/`, `pyproject.toml` |
| Dữ liệu public (bnlearn, Causal Chamber) | Chưa tải, chưa pin version | Report E |
| RICF (likelihood MAG Gaussian, cho B4) | PDF đã có (04-11), đã đọc các định lý chính | `docs/papers/Computing Maximum Likelihood Estimates in Recursive.pdf`; §4 P3, §12 |
| Framing GLS cho D(f) | [Inference] D(f) là constrained GLS; ACI tương ứng WLS | §2 (đoạn "Framing GLS") |

---

## 2. Câu hỏi nghiên cứu và hypotheses (bản làm việc)

**RQ:** Khi các CI statistic được tính trên cùng mẫu với conditioning sets chồng lấp, score cộng tính (ACI Eq. 16) có làm *miscalibrated* độ tin cậy ở cấp feature (ancestral/endpoint) không, và khoảng cách Mahalanobis D(f) dùng hiệp phương sai đầy đủ Σ̂ có sửa được điều đó ở cùng budget không?

| ID | Hypothesis | Vai trò | Dự đoán có thể bác bỏ |
|---|---|---|---|
| **H-prev** | Tương quan off-diagonal của Σ̂ trên query universe thực tế (FCI/ACI-style) là đáng kể | **Tiền đề.** Nếu sai, A′ không có đối tượng | Phần lớn |r_ij| giữa các query cùng dùng trong một proof < 0.2 ở mọi regime → yếu |
| **H-cal** (chính) | Ở regime chồng lấp, false-assertion rate tại ngưỡng cố định của ACI tăng theo mức dư thừa của Q; D(f) thì không | **Claim chính** | False rate của ACI không đổi khi thêm query gần dư thừa |
| H-rank (phụ) | D(f) đổi ranking feature so với ACI/GLS-ACI, cải thiện risk–coverage | Phụ | Kendall τ ≈ 1 |
| H-gen | Lợi ích còn khi CI test là GCM với Σ̂ bootstrap (không có full likelihood) | **Niche định vị** | Lợi ích biến mất hoặc Σ̂ bootstrap quá nhiễu ở n ≤ 1000 |
| H-null | Không có lợi ích khi query gần độc lập (đồ thị thưa, conditioning sets rời) | Kiểm soát (phải *đúng*) | Nếu D(f) vẫn "thắng" ở đây → nghi bug/leak |

**Framing GLS (thêm 04-11-2026) [Inference].** Mô hình z = ζ + ε, ε ~ N(0, Σ), ζ ∈ R(m) là một linear model có design matrix đơn vị, mean bị ràng buộc và sai số tương quan.

| Score | Tương đương cổ điển |
|---|---|
| ACI với weights per-test | WLS (Σ chéo), ứng với P3 |
| GLS-ACI (B2) | WLS với weights chọn lại |
| D(f) | Constrained GLS với full Σ, ứng với P4 |

Hệ quả cổ điển [chưa đối chiếu primary source]: bỏ qua tương quan thì point estimate vẫn không lệch, nhưng standard error bị sai; khi tương quan dương thì inference tự tin quá mức. Điều này cho **cơ sở lý thuyết cho H-cal**, và giải thích vì sao H-rank yếu (BSC-D không thấy đổi argmax PAG). Đồng thời nó **thu hẹp novelty**: toán lõi là GLS. Contribution chỉ có thể là:
- (a) chẩn đoán rằng feature confidence hiện nay là WLS sai mô hình;
- (b) đo mức miscalibration trong regime thực tế (H-prev, H-cal);
- (c) constrained GLS cho vùng hợp đa diện do m-separation sinh ra, kèm calibration (P6).

---

## 3. Pre-registration (đóng băng trước confirmatory) — [Proposal — cần chốt]

- **Đơn vị độc lập:** một SCM (graph + parameters + mẫu). Paired comparison theo SCM.
- **Seeds:** pilot seeds `0–49`; confirmatory seeds `1000–1199`. Không dùng confirmatory seeds cho tuning.
- **Ngưỡng assertion:** mỗi phương pháp được *calibrate ngưỡng* trên regime tham chiếu "minimal Q, đồ thị thưa" ở pilot seeds sao cho false-assertion rate = 5%; sau đó **giữ cố định** ngưỡng đó trên mọi regime khác. Đây là cách đo H-cal: phương pháp calibrated tốt thì false rate không trôi khi đổi regime.
- **Primary metric (H-cal):** độ trôi false-assertion rate: Δ_FAR = FAR(regime chồng lấp, redundant Q) − FAR(tham chiếu). So sánh |Δ_FAR| giữa D(f) và từng baseline.
- **Secondary:** risk–coverage AUC; precision@k; Kendall τ với ACI/GLS-ACI; Brier/ECE nếu score được chuyển thành xác suất (cách chuyển phải chốt trước).
- **Ngưỡng "có lợi ích"** [Proposal]: |Δ_FAR| của D(f) nhỏ hơn của *baseline mạnh nhất* ít nhất **50% tương đối** và **≥ 2 điểm phần trăm tuyệt đối**, paired 95% bootstrap CI theo SCM loại 0, ở **≥ 2 regime chồng lấp** độc lập.
- **Matched budget:** cùng Q, cùng CI test, cùng α (với ACI weights), cùng model family M, cùng số lần resample cho mọi phương pháp dùng bootstrap.
- **Báo cáo bắt buộc:** mọi run thất bại/timeout, mọi regime (kể cả regime A′ thua).

---

## 4. Các phase

Thứ tự phụ thuộc: P0 → P1 → P2 → (P3 ∥ P6) → P4 → P5 → P7. P6 (theory) chạy song song, không chặn P4/P5 trừ khi ghi rõ.

### A′-P0 — Chuẩn bị (≈0.5 ngày, không compute)

- [ ] Chốt §3 với user (ngưỡng lợi ích, seeds, cách calibrate ngưỡng).
- [ ] Chốt layout code đề xuất (§7) — đây là module mới, không refactor code cũ.
- [ ] Tạo `configs/aprime/` với schema regime (p, n, density, latent fraction, Q-type, CI test).
- **Artifact:** §3 được sửa thành bản chốt; commit.
- **GA0:** user đồng ý pre-registration và layout. *Không có GA0 thì không viết code.*

### A′-P1 — Thí nghiệm rẻ nhất: toy H-cal + đo H-prev (≈1–2 ngày, CPU nhẹ)

**P1a — Toy giải tích/mô phỏng (K = 2–4, không cần MAG enumeration).**
- Thiết lập: K query đều đúng là *independent* (ρ_k = 0), z ~ N(0, Σ_r) với Σ_r có tương quan r giữa các query. Một feature f "được xác nhận" khi đủ evidence rằng các query là independent (hoặc dependent, với biến thể dưới alternative).
- So sánh dưới null: phân phối ACI C(f) (weights |log p − log α|) vs D(f), khi r ∈ {0, 0.3, 0.6, 0.9} và khi nhân bản query.
- **Lưu ý trung thực:** kết quả "ACI trôi, D(f) không trôi" ở toy này gần như *được đảm bảo bởi cấu trúc* (P3–P5). P1a chỉ là sanity check của code và công thức, **không phải bằng chứng** về practical relevance.

**P1b — Đo H-prev trên query universe thực tế (đây mới là bằng chứng đầu tiên).**
- Sinh SCM linear-Gaussian bằng `graphs.generate_dag`, p ∈ {5, 8, 12}, mean degree ∈ {2, 4}, latent ratio ∈ {0, 0.2}, n ∈ {200, 1000}.
- Lấy Q = tập CI query mà FCI (causal-learn) thực sự dùng, cộng thêm Q "redundant" (các superset/subset liền kề của sepsets).
- Ước lượng Σ̂ của vector Fisher-z bằng (i) delta method closed-form, (ii) row bootstrap B = 500; kiểm tra (i) ≈ (ii).
- Thống kê: phân phối |r_ij| cho các cặp query *cùng xuất hiện trong một proof orientation* (không phải mọi cặp).
- **Artifact:** `reports/aprime/P1_toy_and_prevalence.md` + raw Σ̂ (`.npz`) + config + git hash.
- **GA1 (kill sớm):**
  - **No-go/hạ cấp** nếu ở *mọi* regime, median |r_ij| của các cặp cùng-proof < 0.1 và quantile 90% < 0.2 [Proposal]. → Quay lui §8 GA1.
  - **Tiếp tục** nếu có ≥ 2 regime với quantile 90% ≥ 0.3.
  - Vùng giữa: tiếp tục nhưng ghi "effect size dự kiến nhỏ" vào §9.

### A′-P2 — Engine lõi, chỉ cho p ≤ 5 exhaustive (≈4–6 ngày)

- [ ] Enumerate MAG (hoặc ancestral structures) trên p ≤ 5, có latent → model family M; tính pattern π(m) ∈ {0,1}^K bằng m-separation. *Kiểm tra số lượng MAG ở p=5 trước — nếu quá lớn, giới hạn M theo skeleton hoặc dùng p=4.* [Unresolved: kích thước M]
- [ ] Tính feature truth: m ⊨ f cho ancestral features (X ∈ An(Y)) và endpoint features.
- [ ] `dist_W(z, R_n(m))` exact: hợp 2^{#dep} QP lồi (mỗi QP: ràng buộc z'_k = 0 hoặc dấu cố định với |z'_k| ≥ δ). Dùng `scipy.optimize` hoặc QP closed-form trên tập active nhỏ; *không* thêm dependency mới nếu không cần.
- [ ] D_W(f) theo A1 Phần 2 (dạng hiệu).
- [ ] Σ̂: closed-form (Gaussian partial correlations, delta method) và bootstrap; pseudo-inverse cho query trùng (P5).
- **Unit tests bắt buộc (khớp mệnh đề trên giấy):**
  - T-P1 oracle soundness: z = ζ_n ⇒ D(f) = +∞ khi f Q-identifiable.
  - T-P3 diagonal reduction: W chéo ⇒ quyết định/ranking trùng ACI với weights tương ứng (so số học).
  - T-P4: ví dụ K=2 trong A1 cho kết quả non-separable như dự đoán.
  - T-P5 duplicate invariance: thêm bản sao byte-identical không đổi D(f).
  - T-P7: search trên tập con của M_¬f cho score ≥ score exact.
- **Artifact:** `src/safety_prior/aprime/` + `tests/aprime/`.
- **GA2 (correctness):** toàn bộ test trên pass; kiểm tra chéo m-separation với causal-learn/networkx trên ≥ 100 graph ngẫu nhiên. *Không qua GA2 thì không chạy P4/P5.*

### A′-P3 — Baselines (≈5–8 ngày; song song một phần với P2)

| # | Baseline | Cách có | Ghi chú task equivalence |
|---|---|---|---|
| B1 | **ACI Eq. 16** (frequentist weights; Bayesian weights nếu kịp) | Tự viết, thay ASP bằng exhaustive trên cùng M | Cùng Q, M, α. Ghi rõ là reimplementation |
| B2 | **GLS-ACI** (reweight chéo) | Tự viết | Control quan trọng nhất: tách lợi ích "reweight" khỏi "off-diagonal" |
| B3 | **Bootstrap FCI feature frequency** | causal-learn FCI + resample | Cùng số resample B với Σ̂ bootstrap |
| B4 | **Forced-feature Gaussian MAG LR/BIC** | Exhaustive trên M; MLE mỗi MAG bằng **RICF** (Drton–Eichler–Richardson, JMLR 2009; `RICF_Drton_Eichler_Richardson_JMLR_2009.pdf`). Tự viết bằng numpy, vì RICF chỉ cần các phép least squares. Score = max_{m⊨f} ℓ̂(m) − max_{m⊨¬f} ℓ̂(m), có bản BIC | Chỉ ở Gaussian arm. Đây là "đáp án đúng" khi có full likelihood |
| B5 | **BSC-D-ACI** (adaptation) | Tự viết theo `docs/papers/bscd.pdf` | Ghi rõ adaptation từ discrete sang Gaussian/GCM |
| B6 | **Triantafillou et al., PGM 2014** | Cần đọc full text trước — [Unresolved: đã có PDF chưa] | Thêm theo A1 §4.2 |
| B7 | dcFCI (tùy chọn) | Chỉ nếu chi phí thấp | Không khôi phục dcFCI pruning |

- **Ghi chú RICF cho B4** [Verified-full theo bản arXiv math/0601631v4; đã có bản JMLR 10 (2009) nhưng chưa đối chiếu số định lý giữa hai bản]:
  - Theorem 4.3: nếu G là BAP và S xác định dương thì accumulation points của RICF là local maxima hoặc saddle points. Nếu model everywhere identifiable và likelihood equations có hữu hạn nghiệm thì RICF hội tụ tới một nghiệm.
  - Ancestral graph (MAG) thì everywhere identifiable (§3, trước Prop. 3.3), nên là curved exponential family (Cor. 2.10). Khi đó LR giữa hai model *lồng nhau* tiệm cận χ².
  - Likelihood có thể multimodal ở n nhỏ hoặc khi misspecified (§1.2(v)). **Yêu cầu:** multi-start (≥ 5 điểm khởi tạo) và báo cáo tỷ lệ bất đồng giữa các lần chạy.
  - DAG thì RICF hội tụ trong 1 cycle. Đây là unit test T-RICF-DAG: so với OLS từng nút.
  - So sánh max_{M_f} với max_{M_¬f} là **không lồng nhau**, nên χ² không áp dụng trực tiếp. B4 chỉ dùng như score xếp hạng/calibration thực nghiệm, không dùng làm p-value.
  - RICF không có latent node tường minh; latent được biểu diễn qua bidirected edges của MAG. Vì vậy dùng được trực tiếp cho M.
- **GA3 (baseline sanity):** B1 tái lập được hành vi định tính của ACI trên setting gốc của paper (n ≤ 9 biến, accuracy ancestral tăng theo confidence). B4 hội tụ về truth khi n lớn. Nếu B1 không tái lập được → dừng, tìm bug trước khi so sánh.

### A′-P4 — Kill test (a): Gaussian arm (≈2–3 ngày compute nhẹ, p ≤ 5)

- Regimes: p ∈ {4, 5}; n ∈ {200, 1000}; density ∈ {thưa, dày}; latent ∈ {0, 0.2}; Q ∈ {minimal, redundant}.
- Methods: D(f) (closed-form Σ̂), B1, B2, B3, B4, B5.
- Pilot seeds trước; chỉ sau khi đóng băng §3 mới chạy confirmatory.
- **GA4:**
  - **Dừng arm Gaussian** nếu D(f) *không* tiến gần B4 **và** *không* vượt B1 theo metric §3 (A1 §4.6a).
  - Nếu D(f) ≈ B4 > B1: kết luận "ở Gaussian, A′ chỉ tái tạo full-likelihood" — hợp lệ, là sanity cho P5, *không* phải contribution.
  - Nếu D(f) > B4: nghi ngờ bug hoặc leak; kiểm tra trước khi tin.

### A′-P5 — Kill test (b): Nonparametric arm — **gate quyết định** (≈4–7 ngày; có thể tốn compute)

- CI test: GCM (residual-product statistic, ổn định và có dạng tiệm cận chuẩn). Σ̂ bằng row bootstrap (hoặc influence function nếu P6 cho được).
- Data: nonlinear additive noise + mixed (một phần biến rời rạc) + nonparanormal; p ≤ 5; n ∈ {300, 1000}.
- Methods: D(f) (bootstrap Σ̂), B1, B2, B3, B5, B6. *Không có B4* (không có full likelihood) — đó chính là niche.
- **Ước tính compute [Unresolved]:** bootstrap × GCM × |Q| × #SCM có thể lớn. Phải đo runtime trên 5 SCM pilot, báo cáo, và **xin phép user** trước khi chạy confirmatory.
- **GA5 (Go/No-go cho A′):**
  - **Go** nếu đạt ngưỡng lợi ích §3 cho H-cal ở ≥ 2 regime chồng lấp, H-null đúng, và lợi ích không tái tạo được bằng B2/B3 ở cùng budget.
  - **No-go** nếu không có lợi ích calibration ở ≥ 2 regime. Lợi ích chỉ ở ranking (H-rank) khi calibration không đổi là **không đủ** (A1 §4.6b).
  - **Conditional** nếu lợi ích có nhưng Σ̂ bootstrap quá nhiễu ở n nhỏ → chỉ định *một* test bổ sung (ví dụ n = 3000 hoặc shrinkage Σ̂), không mở rộng lan man.

### A′-P6 — Theory còn mở (song song, không chặn trừ khi ghi chú)

| Mục | Mục tiêu | Chặn gì |
|---|---|---|
| P4 cho K tổng quát | Điều kiện trên Σ để off-diagonal đổi argmin; có thể một điều kiện kiểu "góc giữa các mặt đa diện" | Không chặn pilot; chặn claim theory trong paper |
| (A1) cho GCM + bootstrap Σ̂ consistency | Dựa trên literature GCM (Shah & Peters 2020) cho joint vector nhiều query; đọc primary source | **Chặn diễn giải** P5 |
| Calibration mapping | Cách chuyển D(f) → xác suất (ví dụ qua GLR χ² mixture, P6) | Chặn metric Brier/ECE |
| **Null distribution của constrained GLS** (thêm 04-11) | Với ràng buộc đẳng thức + bất đẳng thức, LR có phân phối chi-bar-squared (hỗn hợp χ² có trọng số). R_n(M_¬f) là hợp các đa diện, không lồi, nên có thể cần lý thuyết intersection–union test [Hypothesis]. Cần nguồn ở §12 nhóm C | Chặn calibration mapping và metric Brier/ECE |
| Quan hệ D(f) ↔ B4 ở Gaussian arm | Khi n → ∞, D(f) (Σ̂ closed-form) có xấp xỉ forced-feature LR (RICF) không? Nếu có, đó là sanity proposition cho GA4 | Không chặn; hỗ trợ diễn giải GA4 |
| Chi phí tính dist exact | Bound số QP; relaxation lồi làm cận dưới (P7) | Chặn P7 scale-up |

- **Artifact:** cập nhật `A1_gap_confirmation_and_proof_sketch_vi.md` (thêm mục, không xóa mục cũ) hoặc file theory mới.

### A′-P7 — Sau GA5

- **Nếu Go:** scalable approximation (candidate set + báo cáo search gap, P7), p = 10–20; bnlearn (ALARM/CHILD subsets, ẩn biến, ghi rõ adaptation); Causal Chamber cho ancestry đã validation; viết paper concept (Report I). **GA6:** adversarial review (tự review + nhờ người ngoài nếu có).
- **Nếu No-go:** viết `reports/aprime/negative_result_memo.md` (characterization trung thực, có thể publish dạng workshop/short) → chuyển sang **T4** theo Report H. Không ép A′ sống tiếp.

---

## 5. Ước lượng thời gian (tạm, không phải cam kết)

| Phase | Ước lượng | Tuần dự kiến |
|---|---|---|
| P0 | 0.5 ngày | Tuần 1 |
| P1 | 1–2 ngày | Tuần 1 |
| P2 | 4–6 ngày | Tuần 1–2 |
| P3 | 5–8 ngày | Tuần 2–3 |
| P4 | 2–3 ngày | Tuần 3 |
| P5 | 4–7 ngày | Tuần 4 |
| P6 | song song | Tuần 1–4 |
| P7 | phụ thuộc GA5 | Tuần 5–6 |

Hai gate liên tiếp rớt ở A′ → chuyển T4 (theo Report H).

---

## 6. Rủi ro chính và cách giảm

| Rủi ro | Dấu hiệu sớm | Giảm thiểu |
|---|---|---|
| Off-diagonal nhỏ trong thực tế | GA1 | P1b đo trực tiếp trước khi viết engine |
| Kích thước M ở p=5 quá lớn | P2 enumeration | Giới hạn p=4 hoặc restrict theo skeleton; báo cáo rõ |
| Full likelihood lấn át ở Gaussian | GA4 | Đã định vị niche ở P5; Gaussian chỉ là sanity |
| Σ̂ bootstrap nhiễu, suy biến khi |Q| lớn | P1b (so closed-form vs bootstrap), P5 | Shrinkage (Ledoit–Wolf), pseudo-inverse, giới hạn |Q| |
| ACI reimplementation sai | GA3 | Tái lập setting gốc trước khi so |
| "Lợi ích" chỉ do abstain nhiều hơn | P4/P5 | Metric ở matched coverage + ngưỡng calibrate trên tham chiếu |
| Sunk cost | Bất kỳ gate nào rớt | Tuân thủ §8; ghi §9 |
| Reviewer cho rằng "đây chỉ là GLS" | Khi viết concept | Trích dẫn rõ nguồn GLS / constrained inference; định vị contribution theo (a)–(c) ở §2; không claim cơ chế toán mới |
| RICF kẹt ở local max hoặc saddle (B4 sai) | Multi-start không khớp nhau | Multi-start, báo cáo tỷ lệ bất đồng, loại SCM không hội tụ và báo cáo số lượng |

---

## 7. Layout code/artifact đề xuất (chờ GA0)

```
configs/aprime/                  # regime configs (yaml), một file / phase
src/safety_prior/aprime/
    models_enum.py               # enumerate MAG/ancestral structures, π(m), feature truth
    stats.py                     # Fisher-z, GCM statistic, Σ̂ closed-form + bootstrap
    distance.py                  # dist_W(z, R(m)) exact (union of QPs), D_W(f)
    baselines/                   # aci.py, gls_aci.py, bootstrap_fci.py, forced_lr.py, bscd_aci.py
    run_pilot.py                 # config-driven runner, lưu raw z, Σ̂, scores
tests/aprime/                    # T-P1, T-P3, T-P4, T-P5, T-P7, m-sep cross-check
reports/aprime/                  # P1_..., P4_..., P5_..., memo; mỗi file ghi git hash + config
```

Raw evidence luôn lưu: z, Σ̂, pattern π, scores mọi phương pháp, seed, runtime. Không lưu chỉ con số tổng hợp.

---

## 8. Điểm quay lui theo gate

| Gate rớt | Quay về | Giữ lại | Bỏ / sửa giả định |
|---|---|---|---|
| GA0 | Sửa §3/§7 theo user | Toàn bộ plan | — |
| GA1 (H-prev sai) | Viết memo ngắn "co-error không đáng kể ở regime X"; đánh giá lại A′ trong §9 | Code P1b (tái dùng cho T4/C-S) | A′ hạ xuống backup hoặc no-go; kích hoạt T4 |
| GA2 (engine sai) | Sửa P2, không chạy tiếp | Tests | — |
| GA3 (baseline không tái lập) | Sửa baseline; nếu không tái lập được ACI → ghi rõ, dùng B2/B3 làm baseline chính | Engine | Claim "so với ACI" phải được hạ cấp |
| GA4 (Gaussian thất bại cả hai điều kiện) | Kiểm tra bug; nếu không bug → A′ yếu, chỉ còn P5 | Engine + baselines | Bỏ mọi claim ở Gaussian arm |
| GA5 No-go | Negative-result memo → T4 | Toàn bộ code + raw data | A′ đóng |
| GA6 rớt | Sửa paper concept hoặc hạ venue | — | — |

---

## 9. Decision log (append-only)

| # | Ngày | Gate / sự kiện | Kết quả | Bằng chứng (path, hash) | Quyết định | Người chốt |
|---|---|---|---|---|---|---|
| 1 | 2026-11-03 | Reassessment + đọc full text Guo–Wu–Yiu, BSC-D | Gap sống, hẹp; chuyển H-rank → H-cal | `A1_gap_confirmation_and_proof_sketch_vi.md` §4 | A′ = Primary (Conditional) | agent + user |
| 2 | 2026-11-03 | Lập plan v0.1 | — | file này | Chờ GA0 | — |
| 3 | 2026-11-04 | User thêm PDF RICF; bổ sung framing GLS | B4 có đường triển khai (tự viết RICF); H-cal có cơ sở lý thuyết; novelty thu hẹp theo (a)–(c) | `docs/papers/Computing Maximum Likelihood Estimates in Recursive.pdf`; §2, §4 P3, P6 | Plan v0.2; vẫn chờ GA0 | agent + user |
| 4 | 2026-11-04 | User tải 13 PDF + 1 ZIP (11/14 mục) | Agent kiểm lại 14/14 SHA-256 khớp manifest. Thiếu A2, A4, C1 | `docs/papers/DOWNLOAD_STATUS_2026-11-04.md`, `download_manifest_2026-11-04.json` | Phạm vi ban đầu: chỉ ancestral features (do thiếu A4); B6 pending (do thiếu A2). Không phase nào bị chặn | agent + user |
| 5 | 2026-11-04 | Day 1: audit toán độc lập (`aprime-three-day-prompts/01`) | P1, P5, P6 PROVED (có sửa); P2, P3, P7 VALID WITH MODIFICATION; P4: công thức đúng, diễn giải "đếm trùng" bị bác bỏ; (A1) "Σ PD" **sai** (rank ≤ p(p−1)/2; first-order duplicate r = 1); D dạng hiệu không calibrated; đề xuất R1/R2 | `reports/aprime_review_2026-11-04/A1_mathematical_contract_v2.md` | Day 2 = TOY-WITH-CAVEATS | agent (**chưa có user duyệt**) |
| 6 | 2026-11-04 | Day 2: toy validation (`02`) | 192/192 assertion PASS. H-cal cho D **bác bỏ** ở δ = 3; protocol §3 Δ_FAR phạt phương pháp đúng; quy ước support gán +∞ cho mô hình đúng; evidence ≈ query ngoài Q; η misspecified ⇒ sai dấu | `…/A1_toy_results.md`, `A1_toy_mechanism_validation.py`, `A1_toy_outputs.json`, `A1_toy_run_log.txt` | MIXED / REFORMULATION NEEDED | agent (**chưa có user duyệt**) |
| 7 | 2026-11-04 | Day 3: pilot readiness + novelty (`03`) | Framing gốc (D(f), H-cal) STOP; reformulated R1 (certified assertions, χ²_rank) + R2 (η-profile) có validity trên giấy, novelty bị chặn bởi Wang–Kolar–Drton (JASA 2025, mới đọc abstract) và Triantafillou 2014; power chưa có bằng chứng. §3 pre-registration và GA1 không còn phù hợp | `…/A1_pilot_readiness.md`, `A1_missing_references_register.md`, `A1_review_handoff.md` | **REFORMULATE + HOLD FOR SOURCE**; gates RG0–RG3 trước mọi pilot; không xây `src/safety_prior/aprime/` | agent (**chưa có user duyệt**) |
| 8 | 2026-11-04 | User bổ sung 8 PDF (Triantafillou 2014, kỷ yếu LNAI 8754, Zhang 2008, Silvapulle–Sen, Berger 1982, Olkin–Finn 1995, Wang–Kolar–Drton JASA, Strieder et al. UAI 2021) | 5/5 nguồn ban đầu đã có full text. RG0 tạm thời: PASS CÓ ĐIỀU KIỆN (không nguồn nào làm projection cho ancestral features với latent/MAG từ CI statistics; nhưng khung test inversion đã có ở dòng Drton). Còn thiếu: supplement Wang–Kolar–Drton, Strieder–Drton 2023/2024, Wang–Drton 2023, Zhang–Spirtes 2003, Uhler et al. 2013 | `reports/aprime_review_2026-11-04/A1_missing_references_register.md` §4 | Vẫn REFORMULATE; RG0 chưa chốt | agent (**chưa có user duyệt**) |
| 9 | 2026-11-04 | User bổ sung 11 PDF (WKD supplement, Strieder–Drton 2023/2024, Wang–Drton 2023, Chang–Guo–Malinsky, Zhang–Spirtes 2003, Uhler et al. 2013, Robins et al. 2003, ICP 2016, Browne 1984) | Không còn tài liệu chặn quyết định. RG0: PASS (không có chứng nhận ancestral feature valid cho setting latent từ CI statistics). Novelty thu hẹp: projection = lập luận WKD Lemma 3; test từng MAG = khung Browne 1984. Erratum: R1 valid pointwise với η_n → 0 (Robins 2003, Zhang–Spirtes 2003). Baseline mới BL9 (Chang-style resampling cho feature) | `reports/aprime_review_2026-11-04/A1_missing_references_register.md` §5; `A1_pilot_readiness.md` §11; `A1_mathematical_contract_v2.md` §10b | REFORMULATE, bỏ HOLD; gate tiếp theo RG1 + RG2 (toy power, kill test) | agent (**chưa có user duyệt**) |

---

## 10. Changelog của plan

| Version | Ngày | Thay đổi | Lý do |
|---|---|---|---|
| v0.1 | 2026-11-03 | Tạo plan P0–P7, gates GA0–GA6, pre-registration đề xuất | Theo yêu cầu user sau cập nhật tiến độ A′ |
| v0.2 | 2026-11-04 | Thêm framing GLS (§2); chi tiết RICF cho B4 (§4 P3); 2 mục theory P6; 2 rủi ro (§6); danh sách PDF (§12); sửa câu hỏi §11 | User thêm PDF RICF và yêu cầu cập nhật plan; agent không tự tìm PDF |
| v0.3 | 2026-11-04 | Viết lại §12 theo trạng thái tải thực tế; thêm cột phiên bản; phân tích ảnh hưởng của 3 mục thiếu; giới hạn phạm vi ancestral features | User đã tải tài liệu |

---

## 11. Câu hỏi mở cần user chốt (cho GA0)

1. Ngưỡng "có lợi ích" ở §3 (50% tương đối, ≥ 2 điểm % tuyệt đối, ≥ 2 regime) có chấp nhận không?
2. Ngưỡng kill sớm H-prev ở GA1 (median |r| < 0.1 và q90 < 0.2) có hợp lý không?
3. ~~PDF~~: đã có 11/14 mục (04-11). Còn thiếu A2, A4, C1 (§12), nhưng không chặn phase nào. Có đồng ý thu hẹp phạm vi ban đầu về **chỉ ancestral features** cho tới khi có Zhang 2008 không?
4. Ngân sách compute tối đa chấp nhận được cho P5 (số giờ CPU) là bao nhiêu?
5. Đồng ý tạo module mới `src/safety_prior/aprime/` (không động vào code ICD/C1 hiện có)?

---

## 12. Danh sách tài liệu PDF (agent không tự tìm; user thêm vào `docs/papers/`)

**Cập nhật 04-11-2026.** User đã tải 13 PDF mới và 1 ZIP; nguồn và trạng thái ở `docs/papers/DOWNLOAD_STATUS_2026-11-04.md`, hash ở `docs/papers/download_manifest_2026-11-04.json`. Agent đã kiểm tra lại: **14/14 file khớp SHA-256 trong manifest**. Agent mới kiểm tra danh tính file, **chưa đọc sâu nội dung**.

Quy ước: cột "Phiên bản" ghi đúng bản đang có. Khi trích dẫn số định lý/công thức từ technical report hoặc arXiv, phải ghi rõ phiên bản; chưa được coi là giống bản journal.

### Nhóm A — engine và baseline (P2/P3)

| # | Tài liệu | File | Phiên bản | Trạng thái | Chặn gì nếu thiếu |
|---|---|---|---|---|---|
| A1 | Magliacane, Claassen, Mooij — ACI, NIPS 2016 | `ACI_2016.pdf`, `ACI_2016_supplement_supplementary.pdf` (+ ZIP) | Proceedings + supplement chính thức | **Có** | — |
| A2 | Triantafillou, Tsamardinos, Roumpelaki — *Learning Neighborhoods of High Confidence in Constraint-Based Causal Discovery*, PGM 2014, LNCS 8754 | — (shortcut `Triantafillou_2014_download.url`) | — | **Thiếu** — ResearchGate 403 | Chỉ B6. Đưa B6 xuống cuối P3; mọi baseline khác không bị ảnh hưởng |
| A3 | Richardson & Spirtes — *Ancestral Graph Markov Models*, Ann. Statist. 2002 | `Richardson_Spirtes_2002_Ancestral_Graph_Markov_Models.pdf` | Journal | **Có** | — |
| A4 | Zhang — completeness of orientation rules, AIJ 2008 | — (shortcut `Zhang_2008_download.url`; metadata XML, không phải toàn văn) | — | **Thiếu** — ScienceDirect 403 | Chỉ semantics của **endpoint features**. P2 bắt đầu với ancestral features (đủ với A3); endpoint features hoãn tới khi có A4 |
| A5 | Guo, Wu, Yiu — UAI 2026, PMLR 337 | `Guo_Wu_Yiu_2026_Price_Valid_Inference.pdf` | Proceedings | **Có** | — |
| A6 | Drton, Eichler, Richardson — RICF, JMLR 10 (2009) | `RICF_Drton_Eichler_Richardson_JMLR_2009.pdf` (+ bản arXiv v4 cũ) | Journal | **Có** | — |

### Nhóm B — nonparametric arm (P5) và Σ̂ (P1b/P2)

| # | Tài liệu | File | Phiên bản | Trạng thái | Ghi chú |
|---|---|---|---|---|---|
| B1 | Shah & Peters — GCM, Ann. Statist. 2020 | `Shah_Peters_GCM_arxiv.pdf` | **arXiv cập nhật 25-03-2022** | **Có (arXiv)** | Trích dẫn kết quả theo bản arXiv; đối chiếu bản journal trước khi nộp paper |
| B2 | Olkin & Finn — *Correlations Redux*, Psych. Bull. 1995 | `Olkin_Finn_1994_Correlations_Redux_Technical_Report.pdf` | **Stanford TR 299, 08-1994** | **Có (TR)** | Chưa xác nhận bài có công thức covariance *joint* cho partial correlations với conditioning sets chồng lấp như P1b cần. Nếu không có, agent tự suy ra bằng delta method, ghi [Inference], và kiểm chứng bằng bootstrap |

### Nhóm C — calibration / null distribution (P6)

| # | Tài liệu | File | Phiên bản | Trạng thái | Ghi chú |
|---|---|---|---|---|---|
| C1 | Silvapulle & Sen — *Constrained Statistical Inference*, Wiley 2005 | — (shortcut `Silvapulle_Sen_2005_archive.url`) | — | **Thiếu** — Internet Archive giới hạn truy cập | Không chặn: C2 + C3 + C4 đủ cho bước đầu. Sách là tài liệu tham khảo tổng hợp |
| C2 | Shapiro — Biometrika 1985 | `Shapiro_1985_Inequality_Constraints.pdf` | Scan journal, không có text layer | **Có** | Cần đọc bằng render ảnh |
| C3 | Berger — intersection–union test, Technometrics 1982 | `Berger_1980_M555_Technical_Report.pdf` | **FSU TR M555, 07-1980** | **Có (TR)** | Đối chiếu bản journal trước khi trích số định lý |
| C4 | Drton — *Likelihood ratio tests and singularities*, Ann. Statist. 2009 | `Drton_2009_Likelihood_Ratio_Tests_Singularities.pdf` | arXiv v3 (02-04-2009), có thông tin journal | **Có** | — |

### Nhóm D — threats / baseline phụ

| # | Tài liệu | File | Phiên bản | Trạng thái |
|---|---|---|---|---|
| D1 | Parviainen & Koivisto — ECML PKDD 2011 | `Parviainen_Koivisto_2011_Ancestor_Relations.pdf` | Publisher | **Có** |
| D2 | Bucur, Claassen, Heskes — *Large-Scale Local Causal Inference of Gene Regulatory Relationships*, arXiv 1909.03818 | `Bucur_et_al_2019_Local_Causal_Inference.pdf` | arXiv v2 (10-09-2019) | **Có (preprint)** |
| D3 | Claassen & Heskes — BCCD, UAI 2012 | `BCCD_Claassen_Heskes_2012.pdf` | PMLR R10 | **Có** |

### Còn thiếu và ảnh hưởng

| Thiếu | Ảnh hưởng | Cách xử lý tạm |
|---|---|---|
| A2 Triantafillou 2014 | B6 không triển khai được | Chạy P3 với B1–B5; ghi B6 "pending" trong mọi bảng kết quả |
| A4 Zhang 2008 | Không định nghĩa chuẩn endpoint features | Phạm vi P2–P5 ban đầu: **chỉ ancestral features**; ghi giới hạn này trong §9 |
| C1 Silvapulle–Sen 2005 | Thiếu tài liệu tổng hợp cho chi-bar-squared | Dùng C2/C3/C4 |
| (tùy chọn) Berger 1982, Olkin–Finn 1995 bản journal | Chỉ ảnh hưởng tới trích dẫn chính xác | Trích dẫn theo TR, ghi rõ phiên bản |

**Kết luận:** không PDF nào còn thiếu chặn P0–P5 phần lõi. P1 có thể bắt đầu ngay sau GA0.
