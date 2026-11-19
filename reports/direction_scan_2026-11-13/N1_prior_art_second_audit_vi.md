# N1 — Audit prior art lần hai và sửa các suy luận trước pilot

Ngày 13/11/2026. **Không chạy pilot.** Giữ nguyên [audit ban đầu](N1_prior_art_audit_vi.md); file này bổ sung kiểm chứng trực tiếp và điều chỉnh claim. Trạng thái repo mới nhất ghi N1 ACTIVE; audit này không tự đổi quyết định đó.

## 1. Kết luận

**Giữ N1 để làm pilot, nhưng không giữ nguyên lập luận “gap đã đứng vững và mạnh hơn”.** Trong các phần thí nghiệm/phụ lục đã đọc, chưa thấy phép thử **giữ nguyên bảng đích, thêm hoặc thay module độc lập, rồi đo riêng output khối đích** cho các mô hình học sẵn được audit. Đây là kết luận có giới hạn của tìm kiếm, không chứng minh “chưa ai làm”.

Có bốn sửa đổi ảnh hưởng trực tiếp đến thiết kế:

1. `no feature dropout` của DAG-FM **không** chứng minh mô hình chưa từng gặp biến độc lập/thừa.
2. CausalArena loại node cô lập trong synthetic pool; điều đó **không** loại mọi cặp module độc lập có cấu trúc nội bộ.
3. Tính bất biến của PC/FCI/GES là mốc **oracle hoặc consistency dưới điều kiện**, không phải bảo đảm miễn phí ở n=1000 và alpha cố định.
4. **CDFM có threshold thích nghi theo toàn graph và log(d).** Output nhị phân có thể đổi dù raw scores không đổi; phải tách decoder trước khi bàn attention/prior.

Prior art mới cần đưa vào related work: **Aliferis et al., JMLR 2010, Part II §3 đã thêm hàng nghìn biến không liên quan bằng hoán vị và đo lỗi local causal discovery.** N1 không thể claim thêm irrelevant variables vào causal discovery là trục chưa từng được nghiên cứu. Phần còn tiềm năng là mô hình amortized hiện đại, fixed-target counterfactual và phân biệt cơ chế gây đổi kết luận.

## 2. Phạm vi đọc và bằng chứng từng bài

[V] = nội dung kiểm trực tiếp; [I] = suy luận audit; [H] = giả thuyết cần thí nghiệm; [U] = chưa xác minh. Đọc có mục tiêu các phần ghi dưới, không tuyên bố kiểm mọi proof hoặc tái lập kết quả tác giả. Cache mới ở `artifacts/n1_second_audit_2026-11-13/`, có PDF, text và SHA-256; AVICI/Arena/TabCausal dùng cache lượt trước.

| Nguồn và phiên bản | Phần đã đọc | Thí nghiệm liên quan [V] | Hệ quả cho N1 [I] |
|---|---|---|---|
| **AVICI — Amortized Inference for Causal Structure Learning**, Lorch et al., NeurIPS 2022; [arXiv](https://arxiv.org/abs/2205.12934) | §§5–7; App.A Tables3–4; App.E.1–E.3; architecture ablation §6.3 | OOD graph/mechanism/noise, transfer LINEAR↔RFF, tăng d/n, ablate trục attention; §7 nói không có theoretical performance guarantee | Chưa thấy fixed-target append. SBM/GRG OOD đã xét nên không claim chưa xét module/sparsity. Ablate attention axis không đồng nghĩa kiểm irrelevant columns |
| **DAG-FM: A Foundation Model for Causal Discovery under Heterogeneous Causal Mechanisms**, Chen et al.; arXiv2607.11510v2, preprint, 33p; [nguồn](https://arxiv.org/abs/2607.11510) | §4.2, §5; App.B, C.1–C.3, D.1 | Size/density, warping/discretization; OOD SBM, PNL-HNM, noise và heterogeneous mixture; MoLE expert ablation | Gần N1 về mechanism mixture/routing. Không thấy append test. Bài không có mục limitations riêng trong text đã quét; caveat gồm sufficiency, general-mechanism identifiability và omission OOM runs |
| **TRACE — Your Autoregressive Model Already Reveals the Causal Graph**, Hugo Math, Rainer Lienhart; arXiv2602.01135v4, ICML2026 SPIGM **workshop** theo arXiv; [nguồn](https://arxiv.org/abs/2602.01135) | §6, App.D.1–D.2, E.2 | Single discrete event sequence; thay vocabulary/sequence length/memory, noise-token replacement, temporal drops, particle count và CMI threshold | Không phải table-to-DAG model; noise replacement phá dữ liệu đích, khác append độc lập. Có robustness tests liên quan, không được ghi “chỉ đổi d/noise”. Threshold scaling là nhắc nhở mạnh cho pilot |
| **Arrow**, Thompson et al.; arXiv2605.07204; [nguồn](https://arxiv.org/abs/2605.07204) | §6 OOD; App.E.2–E.3, F | Graph/function/noise shifts; independent generator; Sachs; hạn chế observational assumptions, size và quadratic scaling | Chưa thấy fixed-target append; equivariance được nêu cho variable permutation, không cho augmentation |
| **CDFM: Towards a General-Purpose Causal Discovery Foundation Model**, Qiao et al.; arXiv2607.11508v1, preprint, 27p; [nguồn](https://arxiv.org/abs/2607.11508) | §5.3–5.4, §6.1–6.5, conclusion | Multivariate size/mechanism benchmarks, real tables, task-specific adapted identifiability diagnostics, MCAR imputation; graph-adaptive calibrator | Chưa thấy append test. Diagnostics được fine-tune riêng, không quy cho frozen checkpoint. Native threshold dùng global features, phải đo nó như một cơ chế riêng |
| **TabCausal**, Li et al.; arXiv2605.31156v2; [nguồn](https://arxiv.org/abs/2605.31156) | Limitations, App.D.1–D.2; setup từ lượt trước | Prior-strength ablation giữ backbone/budget; held-out generator/protocol tests; n/d scaling | Prior support đã được ablate; N1 cần kiểm nguồn thông tin từ context trên cùng target. Bài nêu uncertainty-aware decoding chưa calibrated, đừng gọi mọi score là xác suất đúng |
| **CausalArena**, Li et al.; arXiv2609.11897; [nguồn](https://arxiv.org/abs/2609.11897) | App.A.1–A.2, graph families và sensitivity suite | Synthetic graph filter: không isolated node; min depth/edges. Dataset checks gồm near-constant, dominant category, duplicate; có block-sparse/dense-local-module families | Claim đúng hẹp: synthetic pool không đo isolated-column augmentation. Không suy rộng sang “mọi independent context bị loại” hoặc benchmark không thể thấy bất kỳ biểu hiện nào |
| **Noise Immunity in In-Context Tabular Learning: An Empirical Robustness Analysis of TabPFN’s Attention Mechanisms**, James Hu, Mahdi Ghelichi; arXiv2604.04868, 2026; [nguồn](https://arxiv.org/abs/2604.04868) | §§3.2.1, 4–5, limitations | Binary prediction, thêm random features, correlated features, attention diagnostics; authors thừa nhận chưa tách nguyên nhân do training design | Tiền lệ đo clutter và attention; không phải structure recovery. Không biến attention concentration thành causal explanation |

**Chú ý phiên bản AVICI:** [README tác giả](https://github.com/larslorch/avici) phân biệt `neurips-*` của bài 2022 với `scm-v0` mới, train tới 100 biến và broad prior. Không dùng phạm vi train 2–50 của bài để gán OOD cho `scm-v0`. Pilot phải ghi checkpoint/hash và matching training support.

**Chú ý preprocessing theo checkpoint:** code `avici/utils/data_jax.py` ở revision `40fb30de976b4264627b3c32996e4d059130aa4e` dùng `_jax_cpm_standardizer` cho count data: library size là tổng trên các biến trong mỗi hàng. Vì thế `neurips-grn` không có preprocessing độc lập từng cột; thêm biến làm đổi giá trị đích sau chuẩn hóa. Chỉ các checkpoint continuous được xử lý bằng nhánh z-standardization tương ứng. Nếu dùng GRN, phải tách ảnh hưởng library-size normalization khỏi encoder; không gộp nó vào đối chứng “target tensor giữ nguyên”. Nguồn: [code tác giả](https://github.com/larslorch/avici/blob/40fb30de976b4264627b3c32996e4d059130aa4e/avici/utils/data_jax.py).

## 3. Những kết luận của audit đầu phải sửa

### 3.1 Không dropout biến khác với không có biến độc lập

DAG-FM không bỏ feature sau khi sinh SCM nhằm giữ causal sufficiency. Bỏ một biến có thể tạo confounder ẩn; **thêm một biến độc lập không phá sufficiency**. Một generator ER cũng có thể sinh node cô lập nếu không có bước rejection. Chỉ từ câu no-dropout không kết luận được xác suất training gặp isolated nodes, càng không kết luận chưa gặp “biến thừa”. Phải xem generator/rejection rules thực tế. [DAG-FM §4.2](https://arxiv.org/abs/2607.11510).

### 3.2 CausalArena không chứng minh “benchmark không thể thấy lỗi” theo nghĩa rộng

Một node cô lập có degree0; một module độc lập có thể gồm nhiều node với degree>0. Ví dụ hai chain tách rời không có isolated nodes. Điều kiện depth/edge count cũng có thể được đáp ứng bởi một graph không liên thông. Ngoài ra “low-information” theo near-constant/duplicate không bằng độc lập với module đích. Vì vậy nên viết: **protocol được audit không trực tiếp đo counterfactual append trên fixed target**, và filter loại riêng trường hợp isolated nodes trong synthetic pool. Cần audit release graph connectivity nếu muốn claim mọi graph đều connected.

### 3.3 Softmax không bảo đảm invariance, nhưng cũng không chứng minh dilution

Permutation equivariance: `f(XΠ)=Πᵀf(X)Π`. Thuộc tính N1 hỏi: `f([X,Z])_XX ≈ f(X)` khi Z độc lập. Đây là hai yêu cầu khác nhau. Softmax denominator thay đổi là một đường ảnh hưởng có thể xảy ra; learned key/query, residual, normalization và decoder có thể bù lại. Không suy ra score phải giảm, hoặc tất cả kiến trúc có cùng cơ chế. SEA có thống kê/subsampling/aggregation riêng; phải xem code trước khi gộp vào một nhóm softmax đơn giản.

### 3.4 Mốc cổ điển cần oracle, assumptions và đúng output

**Suy luận đủ điều kiện:** giả sử `P(X,Z)=P(X)P(Z)`, fixed finite dimension, faithful causal model phù hợp, không có selection/coupling mới. Với CI oracle, PC/FCI loại mọi cạnh cross-block ở bậc0. CI nội bộ X không đổi; orientation paths trong graph còn lại không đi qua block Z. Output CPDAG/PAG hạn chế trên X vì thế không đổi, với implementation/rules/tie handling phù hợp. Đây là chứng minh cấu trúc ngắn, không phải định lý mới.

Với dữ liệu hữu hạn, không chỉ có “lỗi kiểm định bội”: false cross-edge làm đổi search neighborhoods, conditioning sets và orientation propagation; misspecification, order effects, conditioning dimension và implementation cũng có thể góp phần. Tăng n với **alpha cố định** không tự làm xác suất false rejection của một true-null test về0. Consistency phải dùng conditions/tuning đúng. [Kalisch–Bühlmann 2007](https://jmlr.org/papers/v8/kalisch07a.html).

GES có large-sample guarantee với perfect-map/score assumptions thích hợp; decomposability của BIC **một mình** chưa chứng minh finite-sample search output invariant. Không dùng Gaussian BIC trên arbitrary nonlinear SCM làm chuẩn consistency. [Chickering 2002](https://jmlr.org/papers/v3/chickering02b.html). FCI có output PAG, PC/GES thường CPDAG: chấm sự thay đổi trong output native hoặc common identifiable claims, không ép unresolved directions thành DAG sai.

### 3.5 Không tuyên bố phương pháp mới là “in-distribution nên không thể đổ cho OOD”

Target A lấy từ generator training chỉ cho biết **A** giống training. Bảng `[A,B]` ghép disconnected modules có thể đổi density, component count, mechanism-family coupling và interventional proportions, tức joint input vẫn OOD. Đây có thể chính là đối tượng nghiên cứu; cần đặt tên đúng. Cố định p khi swap B và thêm shared-prior/independent-prior controls giúp phân biệt size OOD khỏi context transfer.

## 4. Prior art ngoài danh sách ban đầu

| Nguồn | Đã kiểm và mức đọc | Điều buộc phải tránh |
|---|---|---|
| **Local Causal and Markov Blanket Induction … Part II: Analysis and Extensions**, Aliferis, Statnikov, Tsamardinos, Mani, Koutsoukos; JMLR11:235–284, 2010; [PDF §3, pp.240–244](https://jmlr.org/papers/volume11/aliferis10b/aliferis10b.pdf) | Đọc trực tiếp §3: augment original network bằng 7,990 irrelevant variables, tạo bằng permutation; có signal weakening và chỉ irrelevant controls; đo false positives/negatives local | Không claim “chưa ai thêm irrelevant variables rồi đo causal output”. N1 phải khác ở amortized graph prediction, fixed-target scores, mechanisms và prior mismatch; local classical baseline có tiền lệ thực nghiệm |
| **Self-Compatibility: Evaluating Causal Discovery without Ground Truth**, Faller et al., AISTATS2024; [nguồn](https://proceedings.mlr.press/v238/faller24a.html) | Setup đã đọc trong lượt trước: compatibility qua variable subsets | Không claim kiểm consistency khi đổi tập biến là mới |
| **Marginal causal consistency in constraint-based causal learning**, Roumpelaki et al., UAI-CFA workshop2016; [nguồn](https://ceur-ws.org/Vol-1792/paper5.pdf) | Setup/abstract đã đọc trong lượt trước | Phải phân biệt bỏ biến có liên quan làm đổi target với append independent block |
| **It Just Takes Two: Scaling Amortized Inference to Large Sets**, Wehenkel, Kagan, Heinrich, Pollard; arXiv2605.07972v2, 06/11/2026; [nguồn](https://arxiv.org/abs/2605.07972) | Abstract/metadata nguồn gốc; chưa audit full proof. Set-size generalization với shared nuisance và mean-pool representation | Có literature về cardinality/generalization ngoài causal discovery; ở đây set observations khác variable columns. Không claim equivariance⇒size generalization |

Các truy vấn đã chạy: `amortized inference irrelevant variables equivariance`, `causal discovery distractor variables`, `amortized causal uninformative`, `causal discovery random features transformer`, `causal discovery irrelevant variables foundation model`, `amortized inference projective consistency`. Nhiều kết quả “noise variables” nói về exogenous errors hoặc random Fourier features, **không** phải distractor columns; đã loại khỏi bằng chứng exact prior art. Không tìm exact match không phải systematic proof of absence.

## 5. Ba cơ chế cũ chưa có đòn bẩy phân biệt duy nhất

| Cơ chế | Vấn đề trong dự đoán cũ | Sửa thiết kế |
|---|---|---|
| M1 density prior | ER expected edges/node giữ cố định khi d tăng thì pairwise edge prior có thể **giảm**; không suy ra cạnh nội bộ A tăng. Structured B còn đổi covariance/attention, không riêng density | Audit graph prior của checkpoint; so context cùng p, khớp marginals/noise, đổi internal connectivity. Ghi cả số cạnh và raw scores; dự đoán dấu phải có mô hình cụ thể |
| M2 dilution | Row-permuted target columns và iid columns đều thêm tokens; sự khác nhau không cô lập denominator dilution. Permuted copy dùng chung empirical sample nên không là độc lập unconditional hoàn hảo | Coi permutation là marginal-matched negative control. Nếu cần mechanism claim, instrument attention hoặc mask cross-block attention với kiến trúc hợp lệ; giữ residual/decoder controls; không lấy weight plot làm proof |
| M3 global statistics | Đổi Gaussian→heavy-tail tác động distribution shift và encoder, không chỉ một summary statistic | Kiểm actual features trong code; freeze/replace summary riêng khi khả thi. Tách encoder/raw-score changes khỏi calibrator/threshold changes |
| **M4 decoder/calibration** | CDFM threshold chứa log(d), quantiles, gaps; FoundCause CLI/README có default khác nhau. Có thể tạo F1 shift dù representation không đổi | Lưu raw logits/probabilities; chạy native decoder, fixed manual threshold, và freeze threshold lấy từ A baseline. Không optimize threshold bằng graph truth test |

**Code kiểm trực tiếp:** `artifacts/n1_models_cpu/repos/CDFM/src/cdfm/{inference,wrapper,checkpoint}.py` và README; `foundcause/predict.py`; AVICI README. Đây là code đang được setup trong lượt này; hash/version cụ thể do manifest setup ghi. CDFM `predict(..., threshold=0.5)` là control hỗ trợ sẵn, nhưng phải log threshold native của từng input. FoundCause `--threshold 0.5`, `--temperature 1.0` là CLI defaults hiện đọc, không đồng nhất với cấu hình mô tả cũ trong README.

**Bổ sung kiểm preprocessing AVICI [V-code]:** `artifacts/n1_models_cpu/repos/avici/avici/utils/data_jax.py:10` dùng `_jax_cpm_standardizer`: library size bằng tổng **tất cả cột** trong từng hàng rồi tính log2 CPM. Nhánh count-data còn dùng global minimum và standard deviation trên cả hàng lẫn cột (`_jax_standardize_count`, dòng32–45). Vì vậy với dữ liệu gene counts/`neurips-grn`, append biến làm đổi target normalization theo thiết kế, dù raw target giữ nguyên. Nhánh continuous mặc định của `scm-v0`/`neurips-linear`/`neurips-rff` dùng mean/std theo từng cột; không được suy từ nhánh này rằng mọi checkpoint preprocessing đều column-local. [Mã tác giả](https://github.com/larslorch/avici/blob/main/avici/utils/data_jax.py).

Hệ quả pilot: bắt đầu bằng continuous checkpoint/input phù hợp; nếu xét count branch, tách **native end-to-end effect** khỏi **encoder effect với tensor đích đã cố định**. Freezing library-size/global scaling là một diagnostic intervention thay preprocessing chuẩn, phải ghi rõ và kiểm tương thích; không tự coi đó là native model performance. Không cấp Gaussian cột âm cho count checkpoint chỉ để cùng protocol với continuous models.

## 6. Sửa luật đọc P-N1 trước khi khóa

1. **Tách ba câu hỏi:** output có đổi không; đổi có gây hại không; cơ chế gì gây đổi. `ΔF1>0.05` không định nghĩa non-invariance: score có thể đổi lớn mà binary graph giữ nguyên; F1 có thể không đổi dù cạnh sai khác nhau.
2. Non-invariance đo paired raw score distance/edge flips so repeatability và numerical tolerance. Harm định nghĩa dấu rõ: `H=F1(A alone)−F1(A with B)`; H>0 là giảm chất lượng. Threshold0.05 là mức tác hại thực dụng do nhóm chọn, không định lý hoặc cutoff novelty.
3. “PC/GES đổi <0.02” chỉ được gọi gần tương đương nếu uncertainty nằm trong equivalence margin đã chốt; non-significance không chứng minh bất biến. Có oracle baseline độc lập với finite-sample runs.
4. Hai mô hình trong ba không bảo đảm tổng quát; checkpoint family và decoder có thể chung mechanism. Nếu một model không chạy được, không thay denominator hậu nghiệm. Ghi model-level conclusions trước pooled narrative.
5. Bootstrap theo target SCM; contexts/seeds của cùng target là repeated measurements. Chọn primary k/n và data regime trước confirmation; các k khác exploratory hoặc multiple-comparison-aware.
6. A trong tensor thực vào encoder phải giống bitwise giữa điều kiện; kiểm dtype, missing encoding, clipping, row-subsampling và randomness ngoài standardization.
7. **Negative result là giới hạn trong phạm vi đã test**, không chứng minh mô hình biết marginalization và không mặc định đủ bài báo. Positive result ở decoder có thể hữu ích nhưng phải tách khỏi claim failure của learned causal representation.

## 7. Gap statement sau audit

> Với checkpoint causal discovery học sẵn nhận bảng iid, đánh giá hiện có đã kiểm nhiều distribution shifts và classical local discovery đã có irrelevant-feature stress tests. Trong những nguồn được đọc ở đây, chưa thấy một đánh giá ghép **fixed-target module augmentation/swap**, **raw-score vs adaptive-decoder decomposition**, và **shared-prior vs independent-module controls** để xác định khi nào thông tin từ khối độc lập làm thay đổi kết luận nội bộ và vì sao. N1 kiểm giả thuyết này; failure và cơ chế chưa được xác nhận.

**Quyết định:** đủ cơ sở làm pilot nhỏ với luật đọc sửa; chưa đủ để khẳng định gap mạnh hoặc ưu thế xuất bản. Không cần đổi đề tài chỉ vì audit phát hiện overclaim, nhưng cần bỏ các lập luận đó trước khi chạy và viết bài.
