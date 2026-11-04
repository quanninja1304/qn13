# Audit nguồn bổ sung — đóng các khoảng trống trước khi xếp hạng

Ngày: **03-11-2026**. File này bổ sung (không sửa) bốn audit nhánh `source_audit_{ci,budget,heterogeneity,missingness}.md`. **Không chạy thí nghiệm, không tải dataset, không cài package.**

Nhãn: **[Verified]** = đã đối chiếu nội dung trong primary source đã truy cập (không có nghĩa đã tái lập); **[Verified-abstract]** = chỉ đối chiếu metadata/abstract trên landing page chính thức; **[Summary-only]** = nội dung chỉ đọc qua bản trích xuất tự động của trang, phải đọc lại nguyên văn trước khi trích dẫn; **[Inference]**, **[Hypothesis]**, **[Unresolved]** như các audit nhánh.

## 1. Lý do có file này

Rà soát chéo bốn audit nhánh phát hiện năm khoảng trống có thể làm sai thứ hạng:

1. Audit A không nêu **Ancestral Causal Inference (ACI)** — đối thủ gần nhất của cơ chế "khoảng cách tới mô hình phủ định feature".
2. Các đe dọa confidence/coverage của A mới đọc ở mức abstract.
3. C-S chưa đối chiếu literature robust-invariance/contamination và các follow-up 2026 của CoCo.
4. T4 cần nêu rõ ranh giới với M1 Algorithm 1.
5. Baseline family "bootstrap/stability" cho A chưa được tách rõ.

## 2. Evidence matrix bổ sung

| ID; công trình, tác giả, venue/status, nguồn | Problem/output | Assumptions | Central mechanism | Theory | Baselines/data/metrics | Hệ quả cho candidate |
|---|---|---|---|---|---|---|
| **S1. Ancestral Causal Inference** — Sara Magliacane, Tom Claassen, Joris M. Mooij. **NeurIPS 2016** (NIPS 29, pp. 4466–4474). [Proceedings](https://papers.nips.cc/paper/6266-ancestral-causal-inference), [arXiv v3 HTML](https://arxiv.org/html/1606.07035v3). | Ancestral / non-ancestral relations (partial order trên biến quan sát), kèm confidence score. | Acyclic DAG, cho phép latent; **không selection bias, không feedback** (§2); Markov + faithfulness. | Loss = tổng trọng số các CI statements bị vi phạm (Eq. 12–13); weights tần suất \|log p − log α\| (Eq. 14) hoặc Bayesian log-odds (Eq. 15). **Confidence C(f) = min L(I ∪ {(¬f,∞)}) − min L(I ∪ {(f,∞)}) (Eq. 16)**, được diễn giải là xấp xỉ MAP log-odds. | Theorem 1: oracle soundness (C = ±∞ khi identifiable, 0 nếu không); Theorem 2: asymptotic consistency dưới Eq. 17/18. Completeness của rule set chỉ là phỏng đoán. | Đối thủ: HEJ (acyclic, causally insufficient), bootstrapped anytime FCI/CFCI; synthetic linear-Gaussian có latent, N=500, Fisher-z, α=0.05; Sachs; precision–recall cho ancestral features; n ≤ 9 (Fig. 1). | **[Verified, §§1–5 nguyên văn]** Cơ chế "forced-feature re-optimization" trong A′ **chính là ACI Eq. 16** → không được claim. **[Summary-only]** §6 thừa nhận loss "giả định các test results độc lập (điều không đúng)" và mở rộng "có thể không đơn giản". Theo AGENTS.md, việc tác giả ghi nhận hạn chế **không** tự tạo novelty. |
| **S2. HEJ** — Antti Hyttinen, Frederick Eberhardt, Matti Järvisalo, **UAI 2014** (= CI04 trong audit A). | Graph tối thiểu tổng trọng số vi phạm. | Như CI04. | Như CI04. | Như CI04. | Như CI04. | **[Unresolved]** Chưa đọc được nguyên văn PDF (không trích xuất được text trong môi trường này) nên không biết HEJ có tự định nghĩa per-feature confidence hay không. **[Inference]** ACI mô tả HEJ là search min-weighted-violation và tự giới thiệu Eq. 16, rồi áp dụng Eq. 16 lên HEJ trong §5. Nhận định trong plan rằng "HEJ đã có forced-feature confidence" **được rút lại** cho tới khi đọc được nguyên văn. |
| **S3. The Price of Valid Inference After Causal Discovery** — Dongxin Guo, Jikun Wu, Siu Ming Yiu. **UAI 2026, PMLR 337:1804–1822** (một danh sách ghi là oral; chưa đối chiếu). [Proceedings](https://proceedings.mlr.press/v337/guo26a.html). | Selective inference cho causal effect sau discovery. | Gaussian cho phần FCI; có nhánh nonparametric. | Theo abstract: với FCI có latent dưới Gaussianity, **selection event (cho execution trace + signs) là một polyhedron trong không gian Fisher-z**; sample splitting Θ(n^{3/4}) cho width ratio 1+Θ(n^{−1/4}) so với known-graph oracle. | Có claim theorem trong abstract; chưa đọc proof. | Chưa đọc. | **[Verified-abstract]** Đe dọa **trực tiếp** tới phần "joint geometry trong không gian Fisher-z" của A′. Paper này đã hình thức hóa hình học *chung* của các thống kê CI trong FCI, dù target là **effect**, không phải graph-feature confidence. A′ phải đọc full text trước khi claim cơ chế; khác biệt khả dĩ duy nhất là target (feature/endpoint risk ranking thay vì effect CI). |
| **S4. Post-selection inference for causal effects after causal discovery** — Ting-Hsuan Chang, Zijian Guo, Daniel Malinsky. arXiv 2405.06763 (v4, 09-2025); EconPapers ghi **Biometrika 113(1), 2026, asaf073**. [arXiv](https://arxiv.org/abs/2405.06763). | Inference hợp lệ cho effect cố định sau constraint-based discovery. | Theo nguồn. | Resampling (dựa trên Xie & Wang 2022; Guo et al. 2023). | Coverage cho fixed population-level effect. | Chưa đọc. | **[Verified-abstract]** Target là effect, không phải feature. Chặn mọi claim "đầu tiên đưa uncertainty của discovery vào inference". |
| **S5. Confidence in Causal Discovery with Linear Causal Models** — David Strieder, Tobias Freidling, Stefan Haffner, Mathias Drton. **UAI 2021, PMLR 161:1217–1226**. [Proceedings](https://proceedings.mlr.press/v161/strieder21a.html). | Confidence region cho total causal effect có tính structural uncertainty. | **Bivariate** linear, homoscedastic errors; tác giả nêu khả năng mở rộng. | Test inversion. | Coverage trong setting bivariate. | Chưa đọc. | **[Verified-abstract]** Chỉ đe dọa phần coverage claim của A′, không đe dọa feature-fragility ranking ở p>2 có latent. |
| **S6. Valid Inference After Causal Discovery** — Paula Gradu, Tijana Zrnic, Yixin Wang, Michael I. Jordan. arXiv 2208.05949 (NeurIPS 2022 listing). [arXiv](https://arxiv.org/abs/2208.05949). | Effect inference sau GES ngẫu nhiên hóa. | Theo nguồn. | Randomized GES; target phụ thuộc graph được chọn. | Theo abstract: kết hợp naive gây miscoverage lớn. | Chưa đọc. | **[Verified-abstract]** Prior art nền cho "selection uncertainty"; không task-matched với PAG feature ranking. |
| **S7. Detecting and Measuring Confounding Using Causal Mechanism Shifts** — Reddy, Balasubramanian, arXiv 2409.17840 (2024). [arXiv](https://arxiv.org/html/2409.17840v1). | Phát hiện/đo confounding từ multi-context data. | Chưa đọc. | Mechanism shifts. | Chưa đọc. | Chưa đọc. | **[Verified-abstract, preprint; venue chưa xác minh]** Thêm một đối thủ gần cho C-S; phải đọc trước khi claim gap. |
| **S8. StruBI** — Nanavati, Vreeken, Kaltenpoth, preprint 06-2026 (mở rộng CoCo sang confounding + selection bias). | Confounding + selection từ mechanism shifts. | Chưa đọc. | Chưa đọc. | Chưa đọc. | Theo một trang tổng hợp: synthetic + real. | **[Unresolved]** Chỉ thấy qua trang tổng hợp thứ cấp (chatpaper), **chưa xác minh primary source**. Phải tìm bản arXiv chính thức; nếu StruBI xử lý contamination/coordinated shifts thì gap C-S có thể bị chặn. |
| **S9. Robust/invariant prediction dưới outlier environments** — ví dụ Robust-FILM (arXiv 2503.02611, 2025), DRIG (2023), anchor regression (Rothenhäusler et al. 2021), `hiddenICP` trong package R `InvariantCausalPrediction`. | Prediction/effect bất biến, robust trước outlier environments. | Đa dạng. | Robust trimming/DRO. | Đa dạng. | Đa dạng. | **[Verified-abstract/search]** Đây là các phương pháp **prediction/effect**, không phải confounder discovery kiểu CoCo. Chúng cung cấp *baseline family* "robust trimming" cho C-S và làm yếu mọi claim rằng "robust aggregation qua environments" là mới. Không thấy công trình nào về sensitivity của **confounding declarations** trước coordinated shifts; "không tìm thấy" ≠ "chưa tồn tại". |

## 3. Ranh giới T4 so với M1 Algorithm 1 [Inference]

M1 (Strobl et al. 2018) chỉ chấp nhận một CI tìm thấy dưới test-wise deletion sau khi xác nhận lại trên listwise regime. Đó là một rule **toàn cục, theo từng CI**. Residual của T4 chỉ tồn tại nếu có thể chứng minh một điều kiện **theo từng proof orientation**: các premises có selection sets khác nhau vẫn kết hợp hợp lệ khi một m-separation trên augmented graph (missingness indicators) bảo đảm transport. Nếu điều kiện đó rút về đúng việc áp dụng d-/m-separation chuẩn trên augmented graph với missingness graph đã biết, thì T4 là **engineering** (no-go cho novelty). Câu hỏi này chưa được giải trong audit nào.

## 4. Baseline family "bootstrap/stability" cho A′ [Verified về sự tồn tại]

- Bootstrapped anytime FCI/CFCI đã là baseline trong ACI §5 (100 resample trên nửa dữ liệu).
- Stability selection (Meinshausen & Bühlmann, JRSS-B 2010) là khung chuẩn cho tần suất chọn có kiểm soát error. Việc áp dụng nó lên PAG features phải được định nghĩa rõ trước khi dùng. Paper này **chưa được đọc lại** trong phiên; dùng làm baseline category, không trích theorem.

## 5. Cập nhật claim register (thay thế các dòng tương ứng ở audit nhánh)

| Claim | Nhãn mới | Lý do |
|---|---|---|
| "Khoảng cách nhỏ nhất tới một counterexample model là feature-confidence mới" | **Bác bỏ** [Verified] | ACI Eq. 16. |
| "Joint/covariance-aware geometry của CI statistics khi chấm feature confidence là mới" | **[Unresolved], bị đe dọa mạnh** | BSC-D mô hình dependence giữa các CI fact; S3 hình thức hóa joint Fisher-z geometry cho FCI (target effect). Khả năng còn lại: target feature/endpoint ranking + co-errors tự nhiên do dùng chung hàng dữ liệu. |
| "Sensitivity của confounding declarations trước coordinated/contaminated environments chưa được nghiên cứu" | **[Unresolved]** | Không có hit trực tiếp; S7/S8 chưa đọc; S9 chỉ là prediction/effect. |
| "HEJ đã định nghĩa forced-feature confidence" | **Rút lại → [Unresolved]** | Chưa đọc được nguyên văn. |

## 5b. Cập nhật sau đọc full text

- **S3** (Guo–Wu–Yiu) đã được nâng lên **[Verified-full]**, đọc qua trích xuất text thô của PDF chính thức. Theorem 1 là polyhedron của selection event của FCI, điều kiện trên trace và signs; Theorem 2 là selective CI cho effect. Paper không có feature score.
- **CI05** (BSC-D): đã đọc **full text** từ bản PDF người dùng cung cấp, `docs/papers/bscd.pdf` [Verified-full], cùng tài liệu triển khai Tetrad [Verified-impl].
  - Theo paper, BSC-I và BSC-D cho cùng thứ tự PAG, và dependence không ảnh hưởng tới SHD.
  - Paper trích dẫn thêm prior art về feature confidence: Triantafillou, Tsamardinos, Roumpelaki, PGM 2014 (chưa đọc).
  - Paper xác nhận độc lập rằng ACI đề xuất mô hình hóa quan hệ giữa các constraints như một cải tiến.
- **Đe dọa mới:** các phương pháp feature posterior dựa trên full likelihood (Parviainen & Koivisto 2011; Chen, Meng, Tian, AISTATS 2015; arXiv 1909.03818).
- Chi tiết của cả ba điểm: `A1_gap_confirmation_and_proof_sketch_vi.md` §1.

## 6. Giới hạn truy cập

- arXiv PDF và HEJ PDF tải về dạng nhị phân; môi trường không có thư viện trích xuất PDF. ACI được đọc qua arXiv HTML/ar5iv (§§1–5 nguyên văn, §§6+ chỉ qua bản trích xuất tự động).
- S3–S8 mới đọc metadata/abstract. Mọi kết luận dùng chúng chỉ ở mức "đe dọa novelty", không trích theorem chi tiết.
- Không dùng các trang tổng hợp (sotaverified, chatpaper, deepai) làm bằng chứng cho nội dung; S8 được ghi rõ là chưa xác minh.
