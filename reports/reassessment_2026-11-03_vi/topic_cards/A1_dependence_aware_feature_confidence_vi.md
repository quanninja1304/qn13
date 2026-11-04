# Research Topic Card — A′: Feature confidence nhận biết co-error giữa các CI test (Dependence-aware feature confidence)

> Status: **Hypothesis** (gap chưa source-verified; đã bị thu hẹp sau khi đối chiếu ACI). Pilot **chưa chạy**.
> Owner/date: reassessment 03-11-2026.

## One-sentence research question

Với dữ liệu quan sát (ban đầu linear-Gaussian, có latent, acyclic) và một query universe CI cố định, liệu thay loss cộng tính, giả định độc lập của ACI/HEJ bằng một **khoảng cách thống kê chung** (dùng hiệp phương sai tiệm cận/bootstrap của vector Fisher-z) có cho **xếp hạng độ tin cậy của ancestral/endpoint features** tốt hơn đáng kể ở cùng coverage và compute không?

## Problem & significance

Người dùng PAG/ancestral output cần biết feature nào **đáng tin để hành động** (chọn adjustment set, thiết kế can thiệp). Các score hiện tại (ACI Eq. 16, bootstrap frequency) quyết định mức tự tin ở cấp feature. Nếu chúng **đếm trùng evidence** từ các test tương quan, người dùng sẽ tự tin quá mức đúng ở những feature dựa trên nhiều test gần như dư thừa. Đây là lỗi về **uncertainty quality**, không phải về accuracy của best graph.

## Closest prior art & gap

| Source | Closest contribution | Explicit assumption/limitation | Consequence for novelty |
|---|---|---|---|
| ACI, Magliacane–Claassen–Mooij, NeurIPS 2016 ([HTML](https://arxiv.org/html/1606.07035v3)) | Eq. 16: C(f) = min L(¬f) − min L(f); weights \|log p − log α\| | Loss cộng tính; [Summary-only] §6 thừa nhận giả định test độc lập là sai | Cơ chế "forced-feature distance" **không mới**. Chỉ còn phần dependence. |
| BSC-D, Jabbari et al., ECML-PKDD 2017 ([DOI](https://doi.org/10.1007/978-3-319-71246-8_9)) | Mô hình dependence giữa CI facts qua bootstrap khi scoring PAG | Discrete/BDeu; theo audit CI05, RB-I/RB-D thường chọn cùng best PAG | Dependence modelling đã có ở cấp **graph scoring**; chưa có bằng chứng ở cấp **feature confidence ranking**. [Unresolved] |
| Guo–Wu–Yiu, UAI 2026 ([PMLR](https://proceedings.mlr.press/v337/guo26a.html)) | Selection event của FCI là polyhedron trong không gian Fisher-z | Target là effect inference, Gaussian | Joint Fisher-z geometry đã được hình thức hóa; A′ phải khác ở **target** (feature risk) và **output**. [Verified-abstract] |
| Faller–Janzing, AISTATS 2026 ([PMLR](https://proceedings.mlr.press/v300/faller26b.html)) | Phân biệt các loại redundancy; MMD | DAG/tree chủ yếu | "Redundancy-aware" là prior art về khái niệm. |
| Bootstrap FCI / stability selection | Tần suất feature qua resample | Không có ngưỡng calibrated cho PAG features | Baseline mạnh, rẻ. |

**Defensible gap claim (hẹp, [Hypothesis]):** chưa thấy (trong các nguồn đã đọc) một feature-confidence score cho latent-variable causal discovery mà (i) dùng dependence **chung** của các thống kê CI tính trên cùng mẫu, và (ii) được đánh giá như một **risk–coverage ranking** cho features, so với ACI Eq. 16. "Chưa thấy" không phải "không tồn tại". Phải đọc full text S3 và BSC-D trước khi nâng nhãn.

## Reproducible failure

- **Observed symptom ([Hypothesis], chưa tái lập):** ACI confidence của một feature tăng gần tuyến tính khi thêm các test **gần dư thừa** (ví dụ X⊥Z|Y và X⊥Z|{Y,W} với W gần độc lập), dù thông tin thống kê hầu như không tăng.
- **Specific conditions:** n nhỏ/vừa (100–1000), conditioning sets chồng lấp mạnh, đỉnh có bậc cao, có latent.
- **Suspected mechanism:** các Fisher-z statistics từ cùng hàng dữ liệu với conditioning sets chồng lấp có tương quan tiệm cận lớn. Loss cộng tính coi chúng là bằng chứng độc lập.
- **Evidence:** [Verified] ACI Eq. 13 cộng tính. [Inference] tương quan của sample partial correlations có công thức tiệm cận đã biết dưới Gaussian, nên cơ chế là thật về mặt toán. **Mức độ ảnh hưởng tới feature ranking chưa biết** — đây chính là điều pilot phải đo.
- **Strongest existing remedy:** BSC-D (dependence-aware), bootstrap ACI/FCI, CFCI-stable abstention.
- **Smallest reproduction:** p=4–5, một latent, exhaustive model space; so ACI C(f) khi query universe chỉ có test tối thiểu và khi thêm các test gần dư thừa.

## New scientific insight & method

- **Insight ([Hypothesis]):** độ tin cậy của một feature nên được đo bằng **khoảng cách Mahalanobis** từ vector Fisher-z quan sát tới **vùng các vector thống kê tương thích với ¬f**. Vùng này là hợp của các "sign/threshold cones", một cho mỗi CI pattern của một mô hình phủ định f. Hiệp phương sai off-diagonal chính là thứ tách "nhiều bằng chứng độc lập" khỏi "một bằng chứng lặp lại".
- **Central mechanism:** (1) cố định query universe Q và model family M (MAG/ancestral structures, exhaustive khi p nhỏ); (2) ước lượng vector z ∈ R^|Q| và Σ̂ (tiệm cận Gaussian closed-form hoặc row-bootstrap); (3) với mỗi feature f: D(f) = min_{m ∈ M, m ⊨ ¬f} min_{z' ∈ R(m)} (z − z')ᵀ Σ̂⁻¹ (z − z'), trong đó R(m) là vùng thống kê "consistent" với CI pattern của m dưới ngưỡng tách δ (beta-min); (4) output là ranking D(f) và risk–coverage curve. Đây là **sensitivity score**, không phải posterior hay p-value.
- **Why not routine:** với Σ̂ chéo, D(f) gần với ACI Eq. 16 có weights bình phương. Khác biệt duy nhất là off-diagonal. **Nếu off-diagonal không thay đổi ranking một cách đáng kể, hướng này chết** — đó là điều kiện novelty được đặt tường minh, không giấu đi.
- **Predicted effect and conditions:** lợi ích lớn nhất khi conditioning sets chồng lấp, đồ thị dày, n vừa; gần như bằng 0 khi các test hầu như độc lập (đồ thị thưa, conditioning sets nhỏ rời nhau).
- **Expected failure boundary:** misspecification của CI test (non-Gaussian, nonlinear) làm Σ̂ tiệm cận sai; δ không biết; |Q| lớn làm Σ̂ suy biến.

## Required evidence

- **Proof obligations (tối thiểu):** (i) soundness ở oracle (D(f)=∞ ⇔ f identifiable dưới Q, tương tự ACI Thm 1); (ii) invariance trước bản sao byte-identical của một test (Σ̂ suy biến → dùng pseudo-inverse / reduce rank); (iii) reduction: Σ̂ chéo ⇒ D(f) tương đương một ACI có weights xác định. Coverage/selective inference là **extension**, không phải entry ticket.
- **Baselines (≥3):** (1) ACI Eq. 16, frequentist và Bayesian weights; (2) BSC-D (hoặc bản Gaussian tương ứng, ghi rõ adaptation); (3) bootstrap FCI/CFCI-stable feature frequency, matched compute; (4) GLS-reweighted ACI (control quan trọng nhất: kiểm tra xem lợi ích có chỉ đến từ reweighting chéo hay không); (5) dcFCI ở small latent setting.
- **Controlled synthetic:** latent DAG → MAG/PAG bằng implementation đã kiểm tra; p=4–8; n ∈ {100, 300, 1000}; mật độ ∈ {thưa, dày}; latent fraction ∈ {0, 0.2}; query universe ∈ {minimal, redundant}.
- **Public benchmark:** bnlearn networks (ALARM/CHILD subsets) với biến bị ẩn, ghi rõ là benchmark adaptation; Causal Chamber light-tunnel cho ancestry đã được validation.
- **Real-world + truth caveat:** Sachs chỉ dùng cho intervention consistency; không coi là full ground truth.
- **Metrics:** false asserted ancestry/endpoint ở matched coverage; risk–coverage AUC; calibration của ranking (precision@k); runtime/RSS. Đơn vị độc lập là SCM. Paired CI theo SCM; tách seeds pilot và confirmatory.
- **Ablations:** Σ̂ chéo vs đầy đủ; closed-form vs bootstrap Σ̂; δ; minimal vs redundant Q.

## Minimal falsification pilot (chưa chạy)

- **Cheap decisive test:** (a) trên giấy: chứng minh/bác bỏ reduction Σ̂ chéo ⇒ ACI; (b) p=4–5 exhaustive, 50 SCM, n ∈ {200, 1000}: đo |Δ ranking| (Kendall τ) giữa D(f) đầy đủ và GLS-reweighted ACI, rồi đo false-assertion tại matched coverage.
- **Positive signal:** ở ít nhất hai regime (dày/chồng lấp), full-Σ D(f) giảm false assertions so với **GLS-ACI và bootstrap** ở cùng coverage; paired interval loại 0; lợi ích không biến mất khi bootstrap được cho cùng compute.
- **No-go:** Kendall τ ≈ 1 giữa full-Σ và GLS-ACI trên hầu hết regime; hoặc lợi ích chỉ đến từ abstain nhiều hơn; hoặc S3/BSC-D (sau khi đọc full text) đã định nghĩa cùng score cho features.
- **Resource constraints:** CPU-only; exhaustive search p ≤ 5. Runtime chưa đo; đặt timeout trước khi chạy.

## Research outcomes

- **Minimum complete contribution:** characterization định lượng, reproducible về việc co-errors của CI ảnh hưởng thế nào tới feature-confidence ranking của các phương pháp cộng tính (bao gồm cả kết quả "không đáng kể" nếu đúng như vậy — là một negative result có giá trị nhưng khó publish ở venue mạnh).
- **Strong contribution:** score D(f) với reduction theorem, oracle soundness, scalable approximation (search trên candidate set, có báo cáo rõ search gap) và lợi ích nhất quán trên synthetic + bnlearn adaptation.
- **Ambitious optional extension:** selective-inference-valid feature statements, kết nối với polyhedral selection geometry (S3); chỉ khi pilot dương.
- **Publication fit (conditional):** strong outcome phù hợp UAI/AISTATS hoặc Q1 journal (ví dụ IJAR, JMLR nếu có theory đầy đủ); ICML/NeurIPS chỉ khi có extension về guarantee. Không hứa acceptance.

## Cập nhật 03-11-2026 (sau khi đọc full text Guo–Wu–Yiu và tài liệu triển khai BSC-D)

Xem `../A1_gap_confirmation_and_proof_sketch_vi.md`.

- Gap còn sống sau Guo–Wu–Yiu [Verified-full], vì paper đó nhắm effect CI và không có feature score.
- Gap còn sống sau BSC-D nhưng hẹp hơn [Verified-impl]: BSC-D mô hình dependence của các quyết định 0/1, trên discrete data, ở cấp chọn PAG.
- Chứng minh rút gọn trên giấy:
  - P1–P2: oracle soundness và consistency.
  - P3: với Σ chéo, D(f) **trùng đúng** ACI.
  - P4: với off-diagonal, D(f) không tách được thành các weight per-test. Evidence là thống kê điều kiện z_2 | z_1.
  - P5: duplicate invariance.
  - P6: D(f) là một GLR trong xấp xỉ Gaussian.
  - P7: search gap là anti-conservative.
- **Đe dọa mới:** feature posterior/LR dựa trên full likelihood. **Định vị lại** A′ cho CI statistics tổng quát (kernel/GCM/mixed); Gaussian chỉ còn là arm kiểm chứng.
- **Baselines bổ sung:** forced-feature Gaussian MAG BIC/LR; BSC-D-ACI.

## Cập nhật thứ hai — đã đọc full text BSC-D (`docs/papers/bscd.pdf`)

- BSC-D (Eq. 8) học một BN trên các constraint **nhị phân hóa** sau bootstrap, chỉ cho discrete data, và chấm xác suất **cả PAG**.
- Kết quả thực nghiệm (Alarm/Hailfinder/Hepar II): BSC-I ≈ BSC-D; "ordering of the PAGs ... almost always the same"; "dependence did not matter for SHD". Tác giả phỏng đoán BSC-I bị miscalibrated (lập luận naive Bayes).
- **Hệ quả:**
  - A′ **không được** claim lợi ích về accuracy của best graph.
  - Hypothesis chính chuyển sang **calibration/error rate tại ngưỡng cố định ở cấp feature (H-cal)**; ranking (H-rank) là phụ.
  - Thêm baseline Triantafillou, Tsamardinos, Roumpelaki (PGM 2014).

## Decision

**Conditional (primary candidate).** Lý do: failure mechanism có thật về toán và kill test rất rẻ. Tuy vậy, novelty đã bị thu hẹp tới đúng một yếu tố (off-diagonal dependence) và có hai đối thủ mạnh chưa đọc full text (S3, BSC-D). Test rẻ nhất tiếp theo: đọc full text S3 + BSC-D, rồi làm reduction trên giấy.
