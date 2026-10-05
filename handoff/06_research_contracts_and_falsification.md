# 6. Research contract và falsification plan

Tài liệu nguồn chi tiết: [research contracts và testbed](../docs/research/block_icd_robust_tier_contracts_and_testbed_vi.md). Chương này cô đọng thành hợp đồng bàn giao có tiêu chí ra quyết định.

## 6.1 Testbed chung

### Mục tiêu

Hai hướng dùng chung graph, equality, logging và metrics để tránh mỗi prototype tự tạo benchmark thuận lợi.

### Các tầng test

| Tầng | Dữ liệu | Mục đích |
|---|---|---|
| T0 | Hand-built motifs | Debug semantics và minimal counterexample |
| T1 | Exhaustive/small enumerated DAGs với latent subsets | Tìm sai khác output |
| T2 | Random synthetic graph grid | Đo prevalence và work reduction |
| T3 | Finite-sample SEM | Đo tương tác với CI error |
| T4 | Prior corruption regimes | Đo robustness và collapse |
| T5 | Scale/hardware | Wall-clock, memory, CPU/GPU |

### Baseline bắt buộc

- upstream/reference FCI;
- official/reference ICD khi dependency cho phép;
- stable implementation hiện tại;
- random-valid ordering;
- cost-only và graph-only heuristic;
- oracle upper bound;
- hard tier, no tier và perfect tier cho tier experiments.

### Equality

Phân biệt:

- query-trace equality;
- evidence-set equality;
- canonical final PAG equality;
- Markov-equivalence-level equality nếu representation khác;
- anytime trajectory equality.

Không được đòi query trace giống nhau nếu theorem chỉ hứa final PAG, nhưng mọi query khác biệt phải audit được.

### Experimental unit

- graph/SEM seed là unit chính cho paired comparison;
- nhiều scheduler hoặc method trên cùng graph phải ghép pair;
- bootstrap theo graph, không theo từng budget point hoặc run row có tương quan;
- multiple comparisons phải được công bố khi chọn best variant.

## 6.2 Contract A — Blockwise ICD

### A1. Research object

Cho discovery state `S`, candidate event set `Q(S)` và dependency relation `D`. Một partition `B_1,...,B_k` là admissible nếu event ở hai block khác nhau không thể thay đổi eligibility hoặc semantic effect của nhau trước synchronization boundary đã định nghĩa.

Đây mới là schema; dependency relation cuối cùng phải được formalize từ ICD-Sep/PDS/orientation semantics, không được định nghĩa vòng tròn bằng “những gì implementation thấy độc lập”.

### A2. Minimal claims

1. **Prefix evidence soundness:** mọi edge deletion/orientation trong bất kỳ prefix nào đều có provenance hợp lệ.
2. **Full-round equivalence:** sau khi mọi admissible event của round được xử lý và synchronized, canonical state khớp reference round.
3. **Order confluence:** mọi topological execution tôn trọng dependency relation hội tụ về cùng canonical state.
4. **Safe degeneration:** nếu dependency graph là một component, behavior khớp reference.
5. **Budget value:** ưu tiên block tạo quality-cost curve tốt hơn baseline trong ít nhất một regime đã đăng ký.

### A3. Theorem targets

- Evidence states tạo một partial order/lattice theo tập CI facts và graph consequences.
- Pairwise commutation lemma cho event không phụ thuộc.
- Local commutation cộng termination dẫn tới global confluence dưới điều kiện thích hợp.
- Characterization theorem hoặc sufficient condition cho block separation.
- Bound cho số lần candidate recomputation/synchronization theo cut structure.

Không cần ép tất cả thành theorem ngay. Thành công tối thiểu là một condition không tầm thường, proof đúng và algorithm dùng được condition đó.

### A4. Falsification suite

Phải cố tình dựng:

- diamond;
- collider activation;
- latent confounder nối hai vùng;
- discriminating path băng qua block;
- edge deletion tạo unshielded triple ở vùng khác;
- PDS path thay đổi sau update;
- alternative sepsets ở hai block;
- giant-component collapse;
- cùng evidence nhưng khác event order;
- race ở merge/synchronization.

Mỗi failure phải lưu graph, latent set, query trace, event trace, expected/reference output và minimal reproduction seed.

### A5. Ablations

- dynamic block vs block precomputed;
- exact dependency vs local approximation;
- synchronous vs asynchronous;
- one block vs many block;
- no-prior block ordering vs heuristic vs oracle;
- recompute every event vs incremental invalidation;
- CPU serial vs CPU parallel, tách khỏi algorithmic work.

### A6. Metrics

- exact final PAG mismatch rate;
- round-state mismatch rate;
- number/size distribution of blocks;
- giant component rate;
- CI tests;
- candidate generation/recomputation count;
- synchronization count;
- work, wall-clock, peak RSS;
- load imbalance và wasted speculative work.

### A7. Quy tắc quyết định

`GO` nếu:

- không có mismatch trong exhaustive range đã đăng ký;
- condition phân rã xuất hiện đủ thường xuyên;
- giảm actual work hoặc tạo parallel speedup có ý nghĩa sau overhead;
- claim vẫn đứng khi bỏ prior.

`REVISE` nếu:

- semantics đúng nhưng giant block thường xuyên;
- chỉ một số round/motif phân rã;
- dependency approximation quá bảo thủ;
- gain chỉ có ở graph lớn hơn testbed hiện tại.

`KILL` như main contribution nếu:

- có counterexample phá soundness/equivalence mà không thể sửa cục bộ;
- condition đúng nhưng gần như không bao giờ nontrivial;
- method chỉ đổi scheduling thread, không có insight hay work reduction;
- overhead luôn vượt benefit trong regime mục tiêu.

## 6.3 Contract B — Fallible-Tier Robust Envelope

### B1. Research object

Cho tier prior `K`, uncertainty model có group/source structure và budget `Gamma`. Tập khả dĩ `T_Gamma(K)` chứa tier assignments không mâu thuẫn với uncertainty contract. Với pair `(X,Y)`, robust envelope là union của admissible region qua assignments, rồi intersect với baseline PDS.

Nhóm lỗi là bắt buộc nếu thesis nói về correlated errors. Một uncertainty budget chỉ đếm số node sai độc lập là baseline, không phải model cuối.

### B2. Minimal claims

1. **Reference restriction:** khi tier đúng, restricted search không mất mọi valid separating witness cần thiết.
2. **Robust coverage:** nếu true tier nằm trong uncertainty set, robust envelope chứa ít nhất một witness cần cho mỗi deletion mà baseline có thể chứng minh trong scope định nghĩa.
3. **Oracle/full-budget equivalence:** dùng robust envelope và chạy đủ budget khớp reference dưới điều kiện coverage.
4. **Safe fallback:** khi uncertainty lớn, envelope bằng baseline PDS.
5. **Shrinkage:** khi prior informative, envelope nhỏ hơn baseline trên một lớp graph không tầm thường.
6. **Tractability:** tính envelope không cần liệt kê mọi tier assignment ở implementation cuối.

### B3. Theorem targets

- sufficient condition để tier restriction giữ separator completeness;
- robust-superset theorem;
- monotonicity: `Gamma` tăng thì envelope không co;
- degeneration/no-free-lunch: bất định đủ lớn buộc về full PDS;
- minimality trong một class envelope đã định nghĩa;
- complexity bound theo số tier, group budget hoặc graph width;
- optional probabilistic coverage nếu uncertainty set được calibration.

### B4. Falsification suite

Phải gồm:

- unique separator đi qua node bị xếp sai tier;
- một tier swap làm mất witness;
- nhiều fact cùng sai do một nguồn;
- duplicate evidence từ cùng source bị tính nhầm độc lập;
- union collapse thành full PDS;
- `Gamma=0`, `Gamma=max` và empty prior;
- multiple alternative sepsets;
- latent bidirected motif;
- adversarial prior nhắm vào hub;
- prior mâu thuẫn và abstention;
- true tier nằm ngoài uncertainty set.

### B5. Ablations

- no tier;
- perfect hard tier;
- fallible hard tier;
- independent-fact robust set;
- group/source robust set;
- brute-force envelope;
- efficient proposed envelope;
- fixed `Gamma` vs calibrated `Gamma`;
- static envelope vs adaptive expansion;
- synthetic prior vs LLM prior.

### B6. Metrics

- separator coverage rate;
- final PAG equality/mismatch;
- envelope size ratio `|J|/|PDS|`;
- number of candidate conditioning sets;
- CI tests và tests-to-quality;
- collapse rate;
- coverage conditional on true tier in/out uncertainty set;
- compute để xây envelope;
- calibration/coverage của uncertainty set;
- performance theo error correlation.

### B7. Quy tắc quyết định

`GO` nếu:

- coverage theorem và exhaustive tests phù hợp;
- envelope thu hẹp đáng kể trong regime plausible;
- correlated-error model không bị thay bằng independent toy noise;
- efficient implementation gần brute-force semantics trên graph nhỏ.

`REVISE` nếu:

- envelope đúng nhưng thường collapse;
- cần adaptive expansion/certificate;
- guarantee chỉ đúng với subclass graph rõ ràng nhưng subclass có giá trị;
- tractability cần parameterization khác.

`KILL` như compute-saving contribution nếu:

- robustness luôn đòi full PDS;
- hard-to-compute envelope đắt hơn CI work tiết kiệm;
- coverage phụ thuộc prior đúng gần như hoàn hảo;
- correlated errors phá guarantee cốt lõi.

Trong trường hợp bị kill về speedup, artifact có thể chuyển thành endpoint sensitivity hoặc impossibility result nếu đủ chặt.

## 6.4 Falsification trước optimization

Thứ tự bắt buộc cho cả hai hướng:

1. khóa reference semantics;
2. tạo counterexample generator;
3. chạy exhaustive graph nhỏ;
4. thu nhỏ mismatch;
5. sửa theorem/condition;
6. chỉ sau đó tối ưu runtime;
7. GPU sau khi CPU reference và equality ổn định.

Việc tối ưu sớm có thể che giấu mismatch bằng nondeterminism hoặc numeric differences.

## 6.5 Reviewer roles trong bốn vòng

Nếu dùng nhiều agent/reviewer, mỗi vòng phải có output khác nhau:

- Proposer: định nghĩa và proof sketch.
- Adversarial critic: tìm counterexample, novelty threat và hidden assumption.
- Experiment critic: kiểm leakage, unit of analysis, baseline và metric.
- Reconciler: sửa contract, ghi quyết định và unresolved issue.

Các vai trò không bỏ phiếu theo cảm tính. Mọi bất đồng phải quy về theorem obligation, executable test hoặc decision record.
