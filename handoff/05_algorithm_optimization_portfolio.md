# 5. Danh mục hướng tối ưu thuật toán

## 5.1 Tiêu chuẩn để gọi là đóng góp khoa học

Một scheduler mới hoặc một lần chuyển kernel sang GPU chưa đủ. Một hướng được ưu tiên khi có ít nhất ba thành phần:

1. **Đối tượng mới hoặc điều kiện mới:** decomposition, uncertainty set, envelope, bound hoặc policy class có định nghĩa chính xác.
2. **Guarantee:** soundness, equivalence, coverage, confluence, safe degeneration hoặc regret/cost bound.
3. **Bằng chứng thực nghiệm bác bỏ được:** counterexample suite, baseline mạnh, ablation và regime nơi phương pháp thất bại.

Độ phức tạp không phải tiêu chí. Thiết kế tốt nhất là thiết kế nhỏ nhất giải quyết đúng bottleneck và có mệnh đề rõ ràng.

## 5.2 Những ý tưởng không nên đứng một mình thành claim chính

- Chỉ dùng LLM để xếp hạng CI queries.
- Chỉ chạy FCI bằng nhiều CPU worker.
- Chỉ port covariance/CI test sang GPU.
- Chỉ dùng một hard tier order được giả định đúng.
- Chỉ cache query hoặc vectorize code.
- Chỉ đặt heuristic weight lên node/edge.
- Chỉ thêm một stopping threshold mà không có semantics cho output partial.

Các kỹ thuật này vẫn hữu ích như implementation hoặc ablation, nhưng novelty cần nằm ở nguyên lý thuật toán.

## 5.3 Hướng 1 — Blockwise Asynchronous ICD

### Trực giác

ICD mở rộng conditioning radius theo vòng. Nhiều cập nhật ở các vùng khác nhau có thể không tương tác ngay lập tức. Nếu nhận diện được block độc lập theo evidence/dependency graph, ta có thể xử lý chúng riêng, ưu tiên block có expected value cao, và hợp nhất kết quả theo một rule có kiểm soát.

### Đối tượng đề xuất

Xây một dependency graph trên các candidate deletion/orientation events. Hai candidate nằm trong cùng block nếu một event có thể thay đổi eligibility, admissible path, sepset hoặc orientation context của event kia. Các component độc lập có thể xử lý song song hoặc bất đồng bộ.

### Claim mục tiêu

- Với block decomposition thỏa điều kiện separation, thực thi blockwise đến fixed point cho cùng canonical PAG như reference ICD.
- Các event thuộc block độc lập giao hoán ở mức evidence lattice.
- Khi decomposition suy biến thành một block, thuật toán suy biến an toàn về reference.
- Trong graph có locality, số lần recompute candidate hoặc synchronization giảm.

### Giá trị

Đây là đóng góp về cấu trúc computation, không phụ thuộc LLM. Prior/LLM có thể dùng sau để xếp hạng block, nhưng theorem không nên phụ thuộc prior đúng.

### Nguy cơ

- PDS và discriminating paths tạo dependency xa, làm block hợp lại thành giant component.
- Xóa cạnh có thể tạo unshielded triple và thay đổi orientation context ở block khác.
- Parallelism có thể chỉ giảm wall-clock, không giảm work.
- Nếu điều kiện độc lập quá mạnh, method hiếm khi áp dụng.

### Tiêu chí ưu tiên

Tiếp tục khi tìm được decomposition computable, nontrivial trên motif và ít nhất một lớp graph, đồng thời final-output equality giữ vững. Hạ cấp thành engineering nếu chỉ là thread parallelization.

## 5.4 Hướng 2 — Fallible-Tier Robust Envelope

### Trực giác

Tier knowledge có thể thu hẹp candidate separators hoặc admissible paths, nhưng hard constraint nguy hiểm khi tier sai. Thay vì chọn một tier order, biểu diễn một tập tier assignments khả dĩ quanh prior và lấy union của candidate regions cần thiết. Envelope này bảo thủ: nhỏ hơn unrestricted search khi knowledge hữu ích, nhưng mở rộng khi uncertainty tăng.

### Đối tượng đề xuất

Cho prior tier `K` và uncertainty budget `Gamma`, định nghĩa tập tier assignments `T_Gamma(K)`. Với mỗi assignment `tau`, tạo admissible candidate region `A_tau(X,Y)`. Robust region:

```text
R_Gamma(X,Y) = union over tau in T_Gamma(K) of A_tau(X,Y)
J_Gamma(X,Y) = PDS(X,Y) intersect R_Gamma(X,Y)
```

Không được brute-force ở implementation cuối; Sprint 0 dùng brute-force làm reference semantics.

### Claim mục tiêu

- Nếu true tier assignment nằm trong uncertainty set, separator cần thiết vẫn nằm trong robust envelope.
- Khi `Gamma` đủ lớn hoặc prior vô ích, envelope suy biến về unrestricted PDS.
- Khi uncertainty nhỏ và tier informative, envelope thu hẹp candidate set.
- Có thuật toán polynomial hoặc fixed-parameter cho nhóm uncertainty được chọn.

### Giá trị

Novelty nằm ở robustness đối với tier sai và correlation-aware uncertainty. LLM có thể sinh tier distributions/source groups, nhưng method vẫn đánh giá được bằng prior tổng hợp.

### Nguy cơ

- Union qua nhiều assignment nhanh chóng bằng full PDS.
- Fact-wise budget không mô hình được lỗi chung nguồn.
- Tier restriction đơn giản có thể không tương thích semantics FCI có latent.
- Có nhiều valid sepset; envelope phải bao phủ ít nhất một witness hợp lệ, không nhất thiết tất cả.

### Tiêu chí ưu tiên

Tiếp tục khi tìm được uncertainty representation vừa có coverage theorem vừa tạo shrinkage trên regime thực tế. Nếu mọi robust envelope đều collapse, chuyển hướng sang certificate/adaptive expansion.

## 5.5 Hướng 3 — Exact dcFCI/PAG Branch-and-Bound

### Ý tưởng

Biểu diễn ambiguity thành các branch và dùng bound hợp lệ để prune các nhánh không thể thay đổi target output/cost. Một exact search nhỏ có thể dùng làm checker độc lập cho candidate algorithms.

### Điểm mạnh

- Có tiềm năng tạo exactness theorem rõ.
- Hữu ích như oracle/reference trên graph nhỏ.
- Có thể cho counterexample tối thiểu.

### Điểm yếu

- State space bùng nổ.
- Dễ biến thành solver engineering hơn là causal insight.
- Khó cạnh tranh ở graph lớn.

### Vai trò

Moonshot hoặc auxiliary exact checker, không phải sprint chính trước khi hai hướng ưu tiên được falsify.

## 5.6 Hướng 4 — Gamma-Robust Endpoint Sensitivity

### Ý tưởng

Thay vì buộc xuất một PAG duy nhất dưới prior bất định, tính endpoint nào invariant trong toàn bộ uncertainty set và endpoint nào nhạy cảm. Output là robust core cộng sensitivity annotation.

### Điểm mạnh

- Honest uncertainty.
- Có thể tạo monotonicity result theo `Gamma`.
- Hữu ích khi robust envelope không thu hẹp compute đủ mạnh.

### Điểm yếu

- Thay đổi mục tiêu bài toán từ speedup sang sensitivity analysis.
- Metric và user story khác proposal ban đầu.
- Có thể rất tốn compute.

### Vai trò

Backup direction hoặc secondary analysis, chỉ nâng thành main claim nếu compute-allocation thesis thất bại.

## 5.7 Hướng 5 — Active r-PAG Witness Search

### Ý tưởng

Xem mỗi CI query như hành động tìm witness giúp giải quyết ambiguity trong r-PAG/partial state. Chọn query theo expected reduction of ambiguity hoặc certificate gap.

### Điểm mạnh

- Gần trực tiếp với anytime discovery.
- Có thể nối value-of-information với output uncertainty.

### Điểm yếu

- Expected value khó ước lượng mà không dùng oracle.
- Dễ quay lại heuristic scheduler.
- Theorem có thể yếu nếu state/action space phức tạp.

### Vai trò

Exploratory, hoãn tới khi có reference state semantics và baseline vững.

## 5.8 So sánh danh mục

| Hướng | Novelty lý thuyết | Rủi ro | Chi phí prototype | Vai trò |
|---|---|---|---|---|
| Blockwise ICD | Cao nếu có confluence/decomposition | Dependency toàn cục | Trung bình | Ưu tiên 1 |
| Fallible-Tier Envelope | Cao nếu có coverage + tractability | Envelope collapse | Trung bình | Ưu tiên song song |
| Exact branch-and-bound | Cao nhưng khó scale | State explosion | Cao | Checker/moonshot |
| Endpoint sensitivity | Trung bình-cao | Đổi scope | Trung bình-cao | Backup |
| Active witness search | Trung bình | Heuristic hóa | Cao | Hoãn |

## 5.9 Kiến trúc nghiên cứu bốn vòng

Mỗi hướng đi qua tối đa bốn vòng, theo tinh thần multi-role review nhưng quyết định bằng artifact:

### Vòng 1 — Formalize

- định nghĩa object và invariant;
- khóa reference semantics;
- viết claim tối thiểu;
- liệt kê nearest prior work và novelty threat;
- tạo motif/counterexample nhỏ.

### Vòng 2 — Attempt to kill

- exhaustive graph nhỏ;
- adversarial prior;
- dependency collision;
- alternative sepset;
- reviewer cố tìm counterexample;
- thu nhỏ failure thành minimal witness.

### Vòng 3 — Minimal prototype

- implementation đơn giản nhất;
- so canonical output với reference;
- đo actual work, không chỉ wall-clock;
- ablation từng assumption;
- quyết định GO/REVISE/KILL.

### Vòng 4 — Scale and position

- synthetic grid và finite sample;
- real/semi-synthetic datasets nếu thích hợp;
- CPU/GPU implementation;
- statistical analysis;
- chốt theorem/limitation và paper positioning.

Không dùng đủ bốn vòng chỉ vì đã đặt `max_rounds=4`; một hướng bị phản ví dụ nền tảng phải dừng sớm.

## 5.10 Kế hoạch GPU đúng vai trò

### Kernel phù hợp

- batched covariance/partial-correlation;
- batched regression/residualization;
- SEM simulation;
- scoring nhiều candidate trên tensor cố định;
- bitset/mask operation đủ lớn và đều.

### Kernel ít phù hợp

- graph mutation kích thước nhỏ;
- dynamic BFS/DFS cho PDS;
- rule orientation phân nhánh;
- SAT/ILP nhỏ với nhiều synchronization;
- workload có transfer CPU–GPU lớn hơn compute.

### Quy tắc claim

Báo cáo riêng:

- algorithmic work reduction;
- CPU implementation speedup;
- GPU kernel speedup;
- end-to-end speedup;
- hardware, batch size, precision và transfer cost.

Không cộng gộp chúng thành một “algorithm speedup” duy nhất.
