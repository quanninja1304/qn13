# 2. Đề cương và nền tảng khoa học

## 2.1 Bối cảnh

Trong causal discovery có causal sufficiency, nhiều thuật toán có thể biểu diễn kết quả bằng CPDAG. Khi có biến ẩn và selection effects, lớp tương đương thường được biểu diễn bằng PAG, với các endpoint như tail, arrowhead và circle. FCI và các biến thể phải tìm separating sets ngoài vùng lân cận tức thời; đây là một nguồn chi phí lớn.

Repository này tập trung vào trường hợp thực tế hơn:

- dữ liệu hữu hạn;
- có biến quan sát và biến ẩn;
- prior không hoàn hảo;
- lỗi prior có thể tương quan theo node, motif hoặc nguồn;
- ngân sách CI test và compute hữu hạn;
- mục tiêu cuối là PAG hoặc một trạng thái khám phá được gắn nhãn đúng.

Nguồn đề cương gốc nằm ở [bản high-level](../01_safe_imperfect_priors_high_level_vi.md), [bản chuyên sâu](../02_safe_imperfect_priors_chuyen_sau_vi.md) và [thiết kế kill test](../02a_safe_imperfect_priors_kill_test_vi.md).

## 2.2 Câu hỏi nghiên cứu

### RQ1 — An toàn cấu trúc

Khi prior sai, hệ thống có giữ được nguyên tắc rằng mọi xóa cạnh và định hướng đều có provenance từ dữ liệu và luật causal discovery hợp lệ không?

### RQ2 — Độ bền hữu hạn mẫu

Khi CI test có lỗi do sample size, effect size và conditioning dimension, prior-guided compute allocation có cải thiện trade-off giữa cost và chất lượng graph hay khuếch đại lỗi?

### RQ3 — Lỗi tương quan

Khi nhiều gợi ý prior cùng sai vì chung một nguồn, node hub hoặc motif, phương pháp có suy giảm có kiểm soát không? Calibration theo từng fact độc lập là chưa đủ cho câu hỏi này.

### RQ4 — Ngân sách

Với budget thấp, trung bình và đầy đủ, phương pháp đạt được chất lượng nào theo số CI test, wall-clock, peak memory và graph metrics? Khi budget đầy đủ, nó có trở về output reference không?

### RQ5 — Vai trò thật của LLM

LLM có cung cấp tín hiệu tốt hơn heuristic rẻ hoặc random prior sau khi tính cả calibration cost, token cost và lỗi tương quan không? Đây là câu hỏi empirical sau khi thuật toán đã có guarantee, không phải tiền đề mặc định.

## 2.3 Giả thuyết tổng thể

Giả thuyết làm việc là: prior fallible có thể cải thiện anytime behavior và giảm compute nếu nó chỉ điều khiển thứ tự/phạm vi tìm kiếm, trong khi evidence semantics vẫn do CI tests và luật graph quyết định.

Giả thuyết này có ba tầng:

1. **Existence:** tồn tại headroom từ việc chọn truy vấn tốt hơn. K1 kiểm tra tầng này.
2. **Algorithmic attainability:** một policy khả thi, không có oracle, có thể thu được phần đáng kể headroom.
3. **Robust usefulness:** lợi ích còn tồn tại dưới finite sample và lỗi prior tương quan mà không phá safety.

Pass K1 chỉ giải quyết tầng thứ nhất.

## 2.4 Các nguyên tắc bất biến

### Evidence separation

Prior không được trực tiếp:

- tuyên bố một CI relation;
- xóa cạnh;
- gán arrowhead hoặc tail;
- tạo sepset giả;
- bỏ qua vĩnh viễn một truy vấn cần thiết mà vẫn tuyên bố output là PAG đầy đủ.

Prior được phép:

- sắp thứ tự candidate query;
- ưu tiên node, pair, block hoặc conditioning set;
- cấp budget;
- điều khiển speculative execution;
- chọn thời điểm mở rộng envelope;
- dự báo giá trị thông tin, miễn dự báo không trở thành bằng chứng.

### Full-budget equivalence

Nếu candidate generation và stopping rules không loại bỏ truy vấn cần thiết, chạy đến full budget phải cho output canonical tương đương reference. Equality phải xét semantics PAG, không dựa vào thứ tự log hay representation ngẫu nhiên.

### Honest partial output

Một lần chạy dừng vì budget phải trả về `DiscoveryState` hoặc nhãn tương đương, gồm ít nhất:

- graph hiện tại;
- truy vấn đã thực hiện;
- candidate chưa xử lý;
- pha/vòng hiện tại;
- budget đã dùng;
- provenance;
- cờ completeness.

Không được gọi graph dở dang là PAG cuối cùng.

### Fallible-prior evaluation

Đánh giá phải bao gồm:

- prior hoàn hảo như upper bound;
- prior đúng ngẫu nhiên ở nhiều accuracy;
- lỗi tương quan;
- adversarial hoặc motif-level error;
- uninformative prior;
- missing prior;
- prior mâu thuẫn giữa nhiều nguồn.

## 2.5 Đối tượng đo lường

### Compute metrics

- tổng số CI tests;
- tests-to-target-quality, đặc biệt tests-to-95;
- kích thước conditioning set;
- số candidate được sinh nhưng không test;
- wall-clock;
- CPU time;
- peak RSS;
- GPU utilization và transfer overhead nếu có GPU kernel.

### Graph metrics

- adjacency precision/recall/F1;
- endpoint accuracy;
- structural Hamming distance thích hợp cho PAG;
- số invariant endpoint đúng/sai;
- exact canonical equality ở oracle/full-budget setting;
- quality trajectory theo budget.

### Prior metrics

- fact-level accuracy;
- calibration;
- coverage;
- cluster/source correlation;
- motif-conditioned error;
- abstention;
- chi phí tạo prior.

## 2.6 Thiết kế pha nghiên cứu

| Pha | Mục tiêu | Gate |
|---|---|---|
| Phase 0 | Chứng minh implementation scheduler không đổi tập truy vấn/graph ở full budget | K0 |
| Phase 1 | Đo oracle headroom trong setting tổng hợp có latent | K1 |
| Phase 2 | Prior tổng hợp không hoàn hảo và lỗi tương quan | K2/K3 |
| Phase 3 | Finite-sample CI và safety margin | K4 |
| Algorithm sprint | Phát triển Blockwise ICD và Robust Envelope | Research contracts riêng |
| LLM integration | LLM tạo prior có schema, calibration và abstention | Chỉ sau khi algorithmic baseline đứng vững |

## 2.7 Điều gì sẽ bác bỏ chương trình nghiên cứu

Chương trình cần dừng hoặc đổi thesis nếu một trong các điều sau xảy ra:

- oracle không có headroom đáng kể;
- headroom chỉ đến từ bug hoặc khác biệt candidate set;
- policy khả thi không vượt heuristic rẻ;
- guarantee chỉ đúng khi prior hoàn hảo;
- robust envelope luôn co về baseline trong regime thực tế;
- chi phí xây prior lớn hơn compute tiết kiệm;
- gain chỉ là parallel hardware gain, không phải algorithmic gain;
- output partial bị trình bày như causal conclusion hoàn chỉnh.

K1 đã loại bỏ một phần nguy cơ đầu tiên, nhưng các nguy cơ còn lại vẫn mở.
