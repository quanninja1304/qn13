# Review luật P-N1 v2 và thứ tự công việc tiếp theo

Ngày 14/11/2026. Đã đọc bản đối sánh, luật v2, manifest, source của ba model và các log resource check hiện có. **Không sửa hai tài liệu đã khóa, không chạy model hoặc pilot trong lượt review này.** Các sửa đổi dưới đây là đề xuất amendment trước khi chạy, chưa tự thay thế v2.

## 1. Phán quyết

**Bản đối sánh đúng về định hướng. Luật v2 tiến bộ rõ nhưng chưa đủ nhất quán để giao runner thực thi nguyên văn.** Giữ N1; hoàn thiện semantics của protocol trước khi chạy lưới. Đây là lỗi thiết kế/đo lường có thể sửa, không phải bằng chứng research gap thất bại.

Những điểm nên giữ: claim novelty hẹp; giữ target data; tách change/harm/mechanism; raw scores riêng với decoder; baseline oracle riêng với finite sample; bootstrap theo hệ; báo model-level; held-out riêng; không tự hứa mọi kết quả đều đủ bài báo. Các ngưỡng 0,01/0,03/0,05 có thể là quyết định dự án, miễn định nghĩa nhất quán và khóa trước outcome.

## 2. Trạng thái thực tế đã xác minh

- Môi trường và checkpoint có; smoke ba model đã PASS từ lượt trước.
- **Resource check lớn đã có kết quả**, không chỉ script dự kiến. Nguồn: `artifacts/n1_models_cpu/logs/rc_*_d50_n500.json`; runner ở `artifacts/n1_runs/resource_check/rc.py`.
- Dữ liệu resource check là Gaussian ngẫu nhiên, không causal accuracy. Không dùng shape/determinism/runtime như evidence N1.
- Trong thư mục báo cáo hiện đọc chưa có kết quả pilot khoa học. Không khẳng định chưa có tiến trình khác đang chạy chỉ từ việc chưa thấy report.

| Model | n,d | Lần gọi đầu | Lần gọi sau | Peak RSS được logger lấy mẫu | Phạm vi |
|---|---|---:|---:|---:|---|
| AVICI | 500,50 | 12,95 s | 7,10 s | 1.216,1 MB | hai lần gọi, max score diff=0 |
| CDFM | 500,50 | 14,36 s | 14,52 s | 586,5 MB | hai lần gọi, max score diff=0 |
| FoundCause | 500,50 | 623,88 s | chưa đo | 2.855,7 MB | `n_runs=10`, một lần gọi |

Đây là số một lần đo trên máy, không phải throughput bảo đảm. Logger lấy RSS mỗi 50 ms nên có thể bỏ peak ngắn; RSS của tiến trình không phải toàn bộ RAM hệ thống. Không cần chạy lại đúng cấu hình chỉ để có thêm một PASS; cần bổ sung shape/budget còn thiếu.

## 3. Các điểm cần sửa trước runner

### 3.1 RN3 đang chặn chính failure M4 muốn tìm

RN1 định nghĩa CHANGE bằng raw probabilities. RN3 chỉ mở cho model có CHANGE, nhưng dòng M4 lại cho phép raw probabilities không đổi mà graph NATIVE đổi. Vì vậy nhánh decoder-only không đi qua được gate. RN2 chính cũng dùng FIXED, còn quyết định dự án đòi HARM-BEYOND-CLASSICAL ở nhánh đó: một lỗi chỉ ở native decoder bị bỏ qua ngay từ thiết kế.

**Sửa đề xuất:** tách `SCORE_CHANGE`, `GRAPH_CHANGE_NATIVE` và `GRAPH_CHANGE_FIXED`. Cho M4 được kiểm khi graph native đổi, không cần SCORE_CHANGE. Hai đường kết quả:

- score changes → phân tích encoder/prior/statistics;
- scores ổn định nhưng native graph đổi → phân tích decoder.

Phải nói rõ decoder-only finding có được đi tiếp thành audit nhỏ hay không. Có thể chọn không đầu tư dài hạn, nhưng đó là quyết định giá trị đề tài, không được gọi là không có failure.

### 3.2 Chuẩn PC/Fisher-z trên RFF cũng bị sai mô hình

V2 đã gắn nhãn misspecified cho Gaussian-BIC GES ở RFF nhưng vẫn dùng PC/Fisher-z làm chuẩn duy nhất tại đó. Partial correlation không đặc trưng conditional independence của nonlinear data nói chung. Kết quả consistency PC được viện dẫn là Gaussian với conditions rõ. [Kalisch–Bühlmann 2007](https://jmlr.org/papers/v8/kalisch07a.html).

**Phương án khả thi nhất hiện tại:** giữ claim HARM-BEYOND-CLASSICAL chính trên linear Gaussian; ở RFF chỉ kết luận change/harm của từng model và ghi PC/Fisher-z là diagnostic misspecified. Nếu muốn claim beyond-classical trên RFF, thêm PC với test nonlinear phù hợp và resource-check riêng. [KCI trong causal-learn](https://causal-learn.readthedocs.io/en/latest/independence_tests_index/kci.html) là lựa chọn có API, không phải bảo đảm mọi finite-sample case đúng.

Oracle-PC vẫn dùng được cho graph-oracle invariance khi assumptions và implementation đúng; nó không thay baseline hữu hạn mẫu phù hợp.

### 3.3 F1 không đổi không chứng minh graph bất biến

Hai graph có thể giữ nguyên TP/FP/FN nhưng đổi các cạnh được chọn; F1 bằng nhau, output khác nhau. Do đó CI của H_PC trong ±0,02 chỉ chứng minh **F1 gần tương đương theo margin đã chọn**, không phải output PC bất biến. Cùng lỗi logic xuất hiện ở chữ ký M2: CI chứa 0 không chứng minh hai tác động tương đương.

**Sửa:** giữ biên H cho quality equivalence; thêm số/tỷ lệ skeleton edge flips cho PC/GES. Muốn gọi output gần bất biến, phải đặt margin cho graph discrepancy và kiểm cận trên. Với M2, nếu dùng margin 0,03 thì CI của từng pairwise contrast cần nằm trong [−0,03,+0,03], không chỉ chứa 0. Đây vẫn chỉ là pattern consistency, chưa xác nhận attention dilution.

### 3.4 Seed và repeatability của FoundCause không như v2 mô tả

Đối chiếu trực tiếp `foundcause.py::predict`, quanh dòng 1601–1770, revision `d937cbfcb1db7af64251dbc20424836a457e6f46`:

- Hàm không có argument seed. Mỗi run tự tạo `RandomState(42+run_i)` và seed Torch như vậy. Đổi seed bên ngoài không tạo hai permutation ensembles khác nhau như §5 đề xuất.
- Với n=500, mỗi run lấy **450 dòng**, dù `max_samples=5000`. Lấy row indices xảy ra trước column permutation; ở cùng n và run_i, row selection không phụ thuộc d. Đây là control đã có trong code, có thể kiểm bằng recording.
- Column permutation và jitter nội bộ phụ thuộc shape/order. Cùng seed không bảo đảm cùng perturbation gắn với từng target variable khi đổi d hoặc reorder input.

**Sửa:** tách deterministic repeatability với fixed internal schedule khỏi variability giữa các schedules. Đường thứ nhất có thể đo nguyên API. Đường thứ hai cần adapter có explicit schedule/seed, ghi patch/version và kiểm adapter tái hiện nguyên API ở schedule42. Không báo hai lần gọi nguyên API với outer seeds khác nhau là phép đo Monte Carlo variability.

Để kiểm equivariance stochastic đúng, external permutation phải được ghép với permutation nội bộ tương ứng, hoặc báo biến động ensemble riêng. Chuyển sang chèn cột ngẫu nhiên sau khi fail equivariance chưa loại confounding vị trí; nó là một protocol khác cần khóa rõ.

### 3.5 Ngưỡng NATIVE không đủ mô tả decoder FoundCause

Code FoundCause lấy max của hai directed mean probabilities để quyết định skeleton, rồi **loại cạnh có agreement dưới 0,5**. F1_Native phải lấy skeleton của `output['adjacency']`; công thức max(p)>threshold trong §5 tự nó không tái hiện native output.

**Sửa:**

- NATIVE: output thực của package, gồm agreement pruning/sanitization nếu có.
- FIXED: common diagnostic decoder trên saved probabilities, không agreement pruning; ghi rõ đây là standardized decoder.
- FROZEN: giữ cấu trúc native decoder, chỉ freeze yếu tố đã chọn. Với CDFM freeze baseline threshold. Với FoundCause threshold vốn 0,5, NATIVE/FROZEN có thể trùng; agreement vẫn thay theo input. Không diễn giải mọi chênh native/fixed thành thay đổi scalar threshold.

Chạy forward **một lần** cho mỗi input, lưu raw outputs rồi tính decoder variants từ chính outputs đó. Nếu gọi model lại cho ba chế độ, thêm runtime và có thể thêm stochastic confound.

### 3.6 Domain AVICI mặc định không khớp graph grid đã khóa

`avici/config/examples/lin-gauss.yaml` và `rff-gauss.yaml` hiện liệt kê ScaleFree, ScaleFreeTranspose, WattsStrogatz, SBM, GRG; **không phải ER với edges/node 1 hoặc 2**. `simulate_data(domain=...)` lấy config đó, tên domain đúng không đủ để thỏa protocol.

**Sửa tối thiểu:** dùng API `simulate_data(path=...)` với YAML riêng chỉ định `ErdosRenyi`, `edges_per_var=1` hoặc2, mechanism/noise/parameter ranges tường minh. Giữ bộ sinh tác giả thay vì viết lại mọi SEM. Kiểm actual graph family, realized edge count, acyclicity và hướng ma trận. Không hard-filter realized edges cho khớp kỳ vọng nếu chưa đăng ký rejection rule.

Với kiểu B, same expected edges/node không đảm bảo realized density chính xác bằng target. Với k nhỏ và edges/node cao có thể chạm giới hạn số cạnh của DAG; cần ghi probability clipping/feasibility của generator. Gọi B là control khớp **expected edge budget**, không gọi kiểm soát riêng density một cách hoàn hảo.

### 3.7 CI của CHANGE và các contrasts cần viết lại không nhập nhằng

Ví dụ τ_rep=0,001, median Δp=0,012, CI=[0,002;0,022]. RN1 hiện gọi CHANGE; có evidence vượt repeatability, nhưng chưa có evidence median vượt mức thực dụng0,01. Không sai nếu chủ ý dùng hai tiêu chí khác nhau, nhưng nhãn phải nói đúng.

Đề xuất tách:

- detectable change: CI lower > numerical/repeatability tolerance;
- practically meaningful change: CI lower > margin0,01 (hoặc max của hai margin nếu đã định nghĩa cùng đại lượng);
- below margin: CI upper ≤ margin, gọi `BELOW_MARGIN` thay cho bất biến tuyệt đối;
- còn lại: inconclusive.

M1/M3 dùng trị tuyệt đối contrast nhưng đòi CI>0 của signed contrast sẽ bỏ lỡ tác động ngược chiều. Phải chọn signed contrast δ, giữ dấu và kiểm CI không chứa0 theo hai phía; nếu đòi evidence ngoài practical margin thì CI phải nằm hoàn toàn ngoài [−m,+m]. Khi chuyển sang held-out, khóa hướng từ exploratory rồi xác nhận đúng hướng, không chọn lại dấu.

Đối với `max(H_PC,H_GES)`, ghi rõ max được lấy sau khi aggregate mỗi baseline trên cùng stratum; trong bootstrap tính lại max trong từng resample, hoặc báo cả hai paired contrasts. Không chọn baseline có H lớn nhất riêng từng graph sau nhìn outcome rồi gọi đó là một thuật toán.

### 3.8 Giai đoạn exploratory/held-out và nhãn GO còn vòng tròn

§3 gọi A,k20 là confirmatory; §2 gọi80 systems exploratory; RN5 đã chạy held-out; sau REPLICATED lại gọi GO confirmatory. Cần phân biệt **primary contrast đã định trước** với **dataset confirmatory**.

Đề xuất luồng:

1. Development/calibration systems: chỉ kiểm runner/RN0, không dùng làm confirmatory.
2. 80 exploratory systems: primary contrast A,k20; chọn mechanism lead theo luật.
3. Freeze lead, contrasts, seeds, weights và adapter; chạy20 held-out.
4. Kết quả RN5 là `REPLICATED / NOT_REPLICATED / INCONCLUSIVE`; dự án `GO mechanism validation` nếu đạt, không phải GO cho chính confirmation vừa chạy.

RN5 phải đủ dữ liệu cho nhãn muốn xác nhận: M2 đòi nhiều k nên không thể xác nhận bằng k20 duy nhất. M1 cần A/B; M3 cần A/D; M4 cần native/frozen trên cùng raw outputs. Tất cả cần k0. Nên yêu cầu SCORE_CHANGE được kiểm lại nếu kết luận “raw-score failure lặp lại”.

20 systems trên8 cells có trọng số không đều: khóa cell nào2/cell nào3 và chọn equal-cell weights hoặc giải thích population khác. N=20 không tự đủ power; CI rộng phải ra INCONCLUSIVE. Nếu chọn model/lead sau nhìn exploratory, báo số comparisons và phân biệt evidence exploratory với test trên held-out; không xem điều kiện ≥1 model thành familywise-confirmed claim.

### 3.9 Gate F1≥0,5 không phải chỉ kiểm cài đặt

F1 thấp có thể do assumptions/prior mismatch, threshold không calibrated, hoặc task khó; không nhất thiết bug. V2 yêu cầu “sửa” đến khi đạt dễ dẫn đến thay config sau đã thấy outcome. Hơn nữa F1 skeleton của full graph có thể khá cao ở graph nhỏ/dày, nên0,5 không có ý nghĩa chung về causal competence.

Sửa bằng development set riêng và diagnostic baseline empty/full/known reference output. Nếu cấu hình đúng nhưng model vẫn dưới floor, báo `BASELINE_TOO_WEAK_FOR_THIS_HARM_TEST`; không tự điều chỉnh threshold theo test truth. Không loại rồi thay model mới trong denominator dự án.

## 4. Các giới hạn khoa học nên nói ngay, không nhất thiết chặn pilot

1. **Pilot hiện đo skeleton harm là chính.** Model có thể đảo hướng mà giữ skeleton và F1; NO-GO theo H_skeleton không bác bỏ mọi failure của causal orientation. Directed AP trên linear Gaussian phải đọc dưới training prior/identifiability assumptions, không ép classical CPDAG chọn một DAG truth tùy ý.
2. A/B tại cùng k cho một context contrast có ích, nhưng B cùng mechanism family chưa kiểm đầy đủ **shared-prior vs independently drawn family priors**. M1/M2/M3 là dấu hiệu để thiết kế bước sau. Không gọi pilot này đã kiểm cơ chế Bayes trong gap statement.
3. Một padding draw mỗi target/condition vẫn cho phép ước lượng joint target-context average qua nhiều systems, nhưng không tách được context variance trong mỗi fixed target. Có thể thêm repeats ở phase mechanism sau nếu cần, không tự tăng lưới hiện tại.
4. M4 có thể phân tích kỹ ngay bằng cùng raw scores và counterfactual thresholds; không cần train model mới. Native harm và fixed harm là hai estimands của pipeline khác nhau.
5. Tốt hơn ở một contrast hoặc một checkpoint không chứng minh mọi foundation model yếu hơn classical. Báo baseline F1 cùng H để tránh thuật toán vốn gần như không dự đoán gì trông “bền” chỉ vì không có gì để mất.

## 5. Ngân sách thực tế và cách chia giai đoạn

80 targets × (1 baseline + 4 types × 4 positive k) = **1.360 input evaluations/model**, chưa tính RN0, repeats và held-out. Ba model là4.080 input evaluations. FoundCause `n_runs=10` tương ứng13.600 forward passes chỉ cho exploratory của nó. Ba decoder modes không nên nhân ba số calls.

Riêng d_T20,k30 có40 targets ×4 types=160 evaluations ở d50. Nếu chi phí giống resource check thì khoảng **27,7 giờ cho riêng nhóm này** của FoundCause. Nếu mọi evaluation đều mất624s thì1.360 calls≈236giờ; đó là kịch bản quy đổi cùng chi phí, **không phải dự báo runtime toàn lưới**, vì nhiều input nhỏ hơn.

Vì vậy cần runtime theo d=10/20/30/40/50, n500, cùng10 runs; dự toán theo số calls từng shape và warm/first-call cost. Timeout tính từ phép đo, không từ mong muốn chạy nhanh. Ngoài timeout từng job cần tổng budget và checkpoint/resume theo input hash. `RESOURCE_LIMIT` là trạng thái vận hành, không phải NO CHANGE.

Đề xuất amendment về thứ tự: chạy primary k0 và A,k20 trước trên số targets đã định; sau đó mới các contrasts cơ chế. Nếu đổi từ full factorial sang conditional expansion để tiết kiệm, phải khai báo điều kiện trước outcome và giải thích ảnh hưởng tới phạm vi kết luận. Không tự giảm FoundCause10runs xuống1 sau nhìn kết quả; đó là estimator khác.

## 6. Thứ tự công việc tiếp theo

| Bước | Việc làm | Điều kiện kết thúc/đầu ra |
|---|---|---|
| **1 — Amendment trước số liệu** | Chốt các sửa §3: gateM4, nonlinear baseline, native decoder, randomness, equivalence, CI và held-out | Addendum/version mới liên kết v2; giữ v2 nguyên lịch sử; ghi mọi outcome đã thấy nếu có |
| **2 — Config và budget** | YAML ER riêng; thông số mechanisms; seed manifest; weights8cells; timeout và runtime theo shape còn thiếu | Config/hash, runtime estimate, tổng budget rõ; không sinh metric khoa học |
| **3 — Adapter tối thiểu** | Load/checkpoint một lần mỗi process; capture tensor/row schedules; output probabilities/logits/native adjacency/agreement/threshold | Tiny handcrafted tests, decoder parity và cache-key kiểm được; không framework tổng quát |
| **4 — Gate correctness/RN0** | Tensor identity; deterministic vs ensemble repeatability; paired permutation; oracle-PC; competence trên development data riêng | RN0 report với PASS/FAIL/NOT_APPLICABLE rõ, không sửa cấu hình đến khi test score đẹp |
| **5 — Exploratory** | Frozen target/padding data; model chạy tuần tự; lưu raw outputs một lần, decoder offline | Model-level change/harm/decoder tables, tất cả timeouts/failures, hypotheses lead |
| **6 — Held-out** | Chốt lead/contrasts trước mở20 targets; đủ k/đệm cho nhãn tương ứng | REPLICATED/NOT_REPLICATED/INCONCLUSIVE theo scope; không chọn lại threshold/dấu |
| **7 — Quyết định** | Có lead bền thì thiết kế model intervention hoặc prior mismatch test; nếu decoder-only thì đánh giá contribution riêng | GO có điều kiện cho bước cơ chế, hoặc dừng/thu hẹp; chưa xây full method |

**C1 dự phòng:** giữ luật P-C1a đã viết; không dùng hết CPU chạy cả hai lưới. Phần độc lập có thể chuẩn bị là audit oracle/GAC/SD entrypoint, budget và microcases. Chưa có evidence cho phép coi RC0 của C1 đã PASS. Bổ sung điểm dừng theo ngân sách trong bản đối sánh hợp lý; “không witness trong lưới đã khóa” chỉ là limited negative, không chứng minh metric cấu trúc đủ tốt mọi trường hợp.

## 7. Khuyến nghị cuối của review

Không cần quay lại mở một vòng tìm đề tài mới. Việc có giá trị nhất bây giờ là **làm cho một kết quả dương hoặc âm đều có cách đọc đúng**. Hoàn tất amendment và adapter trước khi chạy80 hệ; tận dụng resource logs đã có. Nếu triển khai nguyên văn v2, nguy cơ đáng kể nhất là bỏ sót decoder-only failure, so với nonlinear baseline sai assumptions, và xem randomness bị khóa cứng như đã đo variability.
