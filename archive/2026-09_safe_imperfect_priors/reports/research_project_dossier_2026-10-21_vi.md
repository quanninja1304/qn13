# Hồ sơ tổng hợp dự án nghiên cứu Safety Prior

**Ngày lập:** 21/10/2026  
**Kho mã:** `D:\REsearch\causal multi-agent\safety_prior`  
**Phạm vi đọc:** mã nguồn `src/`, kiểm thử `tests/`, tài liệu nghiên cứu, tài liệu kill test, handoff và các report đã sinh.  
**Không đọc:** `.env`, thư mục môi trường, `configs/`, log thô, `worker_logs/` và artifact thô; kết quả chạy được lấy từ các report/manifest tổng hợp.

## 1. Tóm tắt điều hành

Dự án nghiên cứu một lớp điều khiển tính toán cho khám phá nhân quả có biến ẩn. Mục tiêu không phải để LLM tự suy luận và quyết định cạnh nhân quả, mà là dùng một **Safety Prior** (prior tri thức có thể sai) để phân bổ thứ tự hoặc ngân sách cho các kiểm định độc lập có điều kiện (conditional-independence, CI).

Nguyên tắc trung tâm của repo là tách hai mặt:

```text
Evidence plane (bằng chứng)
    CI result + luật FCI/ICD + provenance
    -> được phép thay đổi đồ thị

Control plane (điều khiển)
    prior/scheduler + cost + budget + thứ tự chạy
    -> chỉ được quyết định chạy gì trước
```

Một prior không được:

- tự trả lời truy vấn CI;
- tự xóa, thêm hoặc định hướng cạnh;
- được coi là ground truth;
- biến một trạng thái chưa hoàn tất thành PAG hoàn chỉnh.

### Trạng thái bằng chứng hiện tại

| Hạng mục | Trạng thái được ghi nhận | Diễn giải |
|---|---|---|
| K0 | `PASS` | 220/220 lượt Phase 0 giữ được output canonical và các invariant provenance |
| K1 | `PASS` theo quyết định dự án, nhưng chưa đóng formal gate | Snapshot checkpoint ghi 675/800 run, 133 graph hoàn chỉnh; oracle có median saving 23,60% so với `stable_default`, CI bootstrap [20,24%; 27,74%] |
| K2 | `NOT_RUN` | Chưa chứng minh prior khả dụng thu hồi được headroom oracle |
| K3 | `NOT_RUN` | Chưa đánh giá baseline mạnh và lỗi tương quan theo node/motif |
| K4 | `NOT_RUN/BLOCKED` | Chưa có bằng chứng finite-sample endpoint safety; OI-01/OI-02 còn mở |
| C0 | `PASS` | Sửa correctness scalar CI và canonical witness |
| C1 | `PASS` | CPU batched CI tương đương scalar trong audit đã đăng ký |
| C2 | `PASS` | Frozen stable epoch, canonical frontier, checkpoint/resume và commit barrier đã audit |

Có một **độ lệch tài liệu** cần giữ nguyên trong báo cáo: các file cũ trong `reports/kill_test/` vẫn ghi K1 là `NOT_RUN`, trong khi `reports/research_checkpoint_2026-10-19_vi.md` là checkpoint mới hơn và ghi K1 theo quyết định dự án. Vì vậy, K1 chỉ nên được mô tả là **tín hiệu tích cực/decision-pass trong phạm vi FAS-stable**, chưa phải formal `PASS` của ma trận 800 run.

## 2. Bài toán nghiên cứu

### 2.1. FCI giải quyết gì?

FCI (Fast Causal Inference) dùng các quan hệ độc lập có điều kiện để khám phá cấu trúc nhân quả khi có thể tồn tại biến ẩn hoặc selection bias. Đầu ra đầy đủ là PAG (Partial Ancestral Graph), biểu diễn những đặc trưng chung của lớp tương đương các MAG quan sát được.

Một truy vấn cơ bản có dạng:

```text
CI(X, Y | S)

X và Y có độc lập có điều kiện khi đã biết tập S hay không?
```

Luồng FCI mức cao:

```text
complete graph
    -> FAS: tăng dần kích thước tập điều kiện để loại cạnh
    -> ghi separating set và định hướng collider ban đầu
    -> Possible-D-SEP: tìm separating set ngoài lân cận trực tiếp
    -> áp dụng luật định hướng FCI
    -> PAG
```

Khi có biến ẩn, một separating set đúng có thể chứa nút không còn là hàng xóm trực tiếp. Đây là lý do Possible-D-SEP và các biến thể ICD thường là nút thắt tính toán.

### 2.2. Mục tiêu tối ưu

Mục tiêu không phải thay đổi tiêu chuẩn nhân quả, mà là đạt trạng thái có ích sớm hơn với ít chi phí hơn:

```text
giữ nguyên candidate hợp lệ và CI semantics
    -> thay đổi thứ tự / batch / block / ngân sách
    -> đạt skeleton hoặc PAG chất lượng mục tiêu sớm hơn
    -> nếu chạy đủ ngân sách, giữ nguyên semantics reference
```

Chi phí logic hiện tại dùng trọng số:

```text
cost(X, Y | S) = (|S| + 2)^3
```

Đây là proxy cho chi phí đại số của một kiểm định với ma trận cục bộ kích thước `|S|+2`. Repo đồng thời ghi số CI thô, weighted cost, wall time, CPU time và peak RSS.

### 2.3. Giả định khoa học

Các phát biểu oracle dựa trên DAG đầy đủ có biến quan sát và latent, CI oracle dựa trên d-separation/m-separation tương ứng. Các phát biểu finite-sample tách riêng và dùng GaussianCI/Fisher-Z.

Các giả định cần ghi rõ khi mở rộng:

- causal Markov;
- faithfulness hoặc giả định thay thế tương ứng;
- i.i.d. sampling ở phần Gaussian finite-sample;
- conditioning set chỉ chứa biến quan sát;
- PAG/MAG semantics phải được kiểm tra bằng reference độc lập;
- prior có thể sai, kể cả sai có tương quan theo node, motif hoặc nguồn.

## 3. Vị trí khoa học và khoảng trống

### 3.1. Các công trình gần nhất

| Công trình | Phần đã làm | Hệ quả đối với claim của dự án |
|---|---|---|
| [Guess2Graph](https://arxiv.org/abs/2510.14488), bản lưu tại [`docs/papers/Guess2Graph.pdf`](<D:/REsearch/causal multi-agent/safety_prior/docs/papers/Guess2Graph.pdf>) | Dùng chuyên gia/LLM để hướng dẫn thứ tự kiểm định, không thay thế CI outcome; có consistency/monotonicity/finite-sample criteria | Chặn claim rộng “đầu tiên dùng expert/LLM để sắp xếp CI”. Điểm khác của dự án phải nằm ở latent FCI/PAG và safety contract riêng |
| [Order-independent constraint-based causal structure learning](https://jmlr.org/papers/v15/colombo14a.html) | PC-stable/FCI-stable/RFCI-stable giảm phụ thuộc thứ tự; freeze adjacency theo level | Là baseline cho stable epoch, không phải prior-guided scheduler |
| [RFCI](https://doi.org/10.1214/11-AOS940), bản lưu tại [`docs/papers/RFCI.pdf`](<D:/REsearch/causal multi-agent/safety_prior/docs/papers/RFCI.pdf>) | Giảm chi phí FCI bằng chiến lược local hơn trong latent setting | Là baseline latent bắt buộc; không giải quyết prior mềm |
| [FCIT](https://arxiv.org/abs/2510.04263) | Dùng BOSS/GRaSP để targeted testing trong FCI, giảm exhaustive subsets và tạo PAG hợp lệ | Chặn claim “đầu tiên dùng ưu tiên/targeted testing trong FCI có latent”. FCIT không trùng hoàn toàn với Safety Prior LLM có lỗi tương quan |
| [dcFCI](https://arxiv.org/abs/2505.06542), bản lưu tại [`docs/papers/dcFCI.pdf`](<D:/REsearch/causal multi-agent/safety_prior/docs/papers/dcFCI.pdf>) | Score-guided/Anytime-FCI, xếp hạng và xác thực PAG ứng viên | Là adjacent baseline về score/search, không phải generic scheduler an toàn |
| [tFCI/tIOD](https://arxiv.org/abs/2503.21526), bản lưu tại [`docs/papers/tFCI & tIOD.pdf`](<D:/REsearch/causal multi-agent/safety_prior/docs/papers/tFCI%20%26%20tIOD.pdf>) | Tiered background knowledge trong latent/overlapping data; sound/complete dưới prior đúng | Chỉ là prior cấu trúc cứng, không phải tier claim fallible |
| [GPUCMIknn-Parallel](https://proceedings.mlr.press/v185/hagedorn22a.html) | Batch nhiều CI test trên GPU/CPU | GPU là backend engineering; không đủ làm novelty chính |
| L2D-CD, [`docs/papers/L2D-CD.pdf`](<D:/REsearch/causal multi-agent/safety_prior/docs/papers/L2D-CD.pdf>) | Learning-to-defer cho causal discovery hai biến | Liên quan fallible expert nhưng không phải FCI/PAG query scheduler |
| RoaDs, [`docs/papers/Robust Causal Discovery under Imperfect Structural Constraints.pdf`](<D:/REsearch/causal multi-agent/safety_prior/docs/papers/Robust%20Causal%20Discovery%20under%20Imperfect%20Structural%20Constraints.pdf>) | Căn chỉnh prior cấu trúc không hoàn hảo trong tối ưu liên tục | Không giữ nguyên FCI evidence semantics |

### 3.2. Claim có thể bảo vệ

Chưa nên tuyên bố “chưa ai dùng prior để tối ưu causal discovery”. Claim hẹp và có cơ sở hơn là:

> Chưa thấy công trình nào kết hợp đầy đủ: prior bên ngoài có thể sai; FCI/ICD với latent confounding và PAG; prior chỉ điều khiển query/resource scheduling; full-budget semantic equivalence; partial state có chứng nhận khi dừng sớm; robustness với lỗi tương quan; và batch/GPU executor.

Khoảng trống này vẫn là **giả thuyết novelty**, không phải kết luận cuối. FCIT là đối thủ gần nhất phải được đưa vào baseline trước khi tuyên bố đóng góp.

## 4. Đề cương nghiên cứu và giả thuyết

### RQ1 — Safety của control plane

Khi prior sai, mọi edge deletion và endpoint orientation có còn truy nguyên được về CI result và luật FCI/ICD hợp lệ không?

**H1:** prior chỉ làm thay đổi thứ tự/batch/resource allocation; không tạo causal evidence.

### RQ2 — Headroom và cost-quality frontier

Khi oracle biết truy vấn nào hữu ích, có thể đạt chất lượng skeleton/PAG mục tiêu với ít weighted CI cost hơn không?

**H2:** tồn tại headroom đủ lớn trong một miền đồ thị được xác định trước.

### RQ3 — Prior thực tế

Prior có chất lượng trung bình, không hoàn hảo, có thu hồi được một phần headroom oracle không?

**H3:** Prior B tại AUC khoảng 0,65 thu hồi được một phần đáng kể oracle saving và không tệ hơn heuristic mạnh.

### RQ4 — Lỗi tương quan

Khi prior sai theo node, motif hoặc nguồn chung, lợi ích có suy giảm có kiểm soát không?

**H4:** calibration theo từng claim độc lập là chưa đủ; cần đánh giá group-correlated corruption.

### RQ5 — Finite sample và PAG

Khi CI có sai số mẫu hữu hạn, scheduling gain có đi kèm endpoint harm vượt ngưỡng không?

**H5:** lợi ích chỉ được chấp nhận nếu giảm cost mà không tăng endpoint sai vượt biên đã đăng ký.

## 5. Thiết kế kill test K0–K4

### 5.1. K0 — Mechanical correctness

K0 kiểm tra các lịch khác nhau có cùng vũ trụ candidate, cùng dependency, cùng semantics khi chạy đủ ngân sách hay không.

Các invariant chính:

1. candidate universe không đổi;
2. chỉ chạy query khi đủ điều kiện;
3. dependency giữa các pha được tôn trọng;
4. prior không đi vào graph evidence;
5. replay cùng seed là deterministic;
6. canonical output khớp reference.

Kết quả report: `220/220`, equivalence rate `1.0`, failure `0`, quyết định `PASS`.

### 5.2. K1 — Oracle headroom

Grid của Phase 1 gồm:

| Trục | Giá trị |
|---|---|
| Observed nodes | 10, 20 |
| Latent ratio | 0,2; 0,4 |
| Mean degree | 2; 4 |
| Graph seeds | 20 mỗi cell |
| Tổng graph | 160 |
| Scheduler | stable, random-valid, cost-only, graph-only, oracle-query |
| Tổng logic run | 800 |
| CI | oracle |

Metric chính là `tests_to_95`: số CI query cần để skeleton đạt 95% F1 so với stable full-budget reference. Metric phụ gồm weighted cost, quality checkpoint, wall time, CPU time, RSS, phân bố conditioning order, FAS/PDS split và first separator cost.

Checkpoint mới nhất ghi nhận:

- 675/800 run đã có row hoàn chỉnh;
- 133 graph có đủ scheduler;
- oracle median saving so với `stable_default`: 23,60%;
- bootstrap 95%: [20,24%; 27,74%];
- bốn nhóm `p × latent_ratio` hiện có tín hiệu dương.

Giới hạn: scheduler chỉ tác động rõ ràng ở `FAS_STABLE_SKELETON_ONLY`; Possible-D-SEP và orientation chưa được chứng minh có headroom tương ứng.

### 5.3. K2 — Prior khả dụng

Prior A là oracle query score bị nhiễu, chỉ dùng để đo độ nhạy. Prior B dự đoán thành viên của minimal separator, không được gắn nhãn trực tiếp rằng query sẽ independent.

Chỉ số:

```text
oracle_saving  = saving của oracle so với baseline
prior_saving   = saving của Prior B so với baseline
recovery_ratio = prior_saving / oracle_saving
```

Ngưỡng đăng ký: AUC thực tế 0,65, thu hồi tối thiểu 30% oracle saving, giảm tối thiểu 8% CI so với prior-free baseline tốt nhất, cận dưới bootstrap dương, đạt ít nhất 3/4 nhóm.

Trạng thái: `NOT_RUN`.

### 5.4. K3 — Baseline mạnh và lỗi tương quan

Ba chế độ lỗi:

| Chế độ | Ý nghĩa |
|---|---|
| independent | Mỗi claim sai độc lập |
| node_correlated | Một nhóm node làm các claim liên quan cùng sai |
| motif_correlated | Một vùng cấu trúc/motif làm nhiều claim cùng sai |

Baseline bắt buộc: stable/FCI-stable, random-valid, cost-only, graph-only, oracle, RFCI-stable và FCIT hoặc targeted baseline tương đương khi triển khai được.

Trạng thái: `NOT_RUN`.

### 5.5. K4 — Finite-sample safety

Testbed chính:

| Trục | Giá trị |
|---|---|
| Observed nodes | 20 |
| Latent ratio | 0,3 |
| Mean degree | 2,5 |
| SEM | Linear Gaussian |
| Sample size | 500, 2000 |
| Graph seeds | 30 |
| Data seeds | 3 |
| CI | Fisher-Z, alpha 0,05 |

Metrics gồm cost/CI count, skeleton F1, endpoint precision, số endpoint sai, số circle chưa xác định và quality–budget curve. Ngưỡng endpoint harm đăng ký là tối đa 0,1 endpoint sai/graph hoặc bound tin cậy nằm trong biên đã khóa.

Trạng thái: `NOT_RUN/BLOCKED`; OI-01 là thiếu RFCI-stable backend, OI-02 là thiếu DAG-with-latents → MAG/PAG converter độc lập được xác minh.

## 6. Kiến trúc kỹ thuật của repo

### 6.1. Luồng dữ liệu

```text
graph generator
    -> GeneratedGraph + observed/latent mask + digest
    -> CI backend (OracleCI hoặc GaussianCI)
    -> candidate enumeration
    -> Scheduler.order()
    -> discovery state / PAG
    -> ProvenanceLog
    -> immutable run row
    -> metrics + bootstrap + gate report
```

### 6.2. Module chính

| Module | Vai trò kỹ thuật | Vai trò khoa học |
|---|---|---|
| `graphs.py` | Sinh DAG ngẫu nhiên/motif, canonical digest, PAG canonicalization | Khóa experimental unit, observed/latent truth và equality |
| `ci.py` | `OracleCI` bằng d-separation; `GaussianCI` bằng Fisher-Z | Tách structural truth khỏi sampling error |
| `models.py` | `CIQuery`, `QueryCandidate`, `QueryRecord`, `DiscoveryState`, `PAGResult`, `PriorView` | Schema bất biến và honest partial state |
| `schedulers.py` | Stable, random-valid, cost-only, graph-only, prior-guided, oracle-query | Control plane để so sánh chính sách |
| `discovery.py` | Scheduled FAS; nối vào FCI Possible-D-SEP và orientation rules | Evidence plane và graph mutation |
| `provenance.py` | Query log, graph event, seed refs, witness ID | Audit prior không biến thành evidence |
| `priors.py` | AUC, minimal separator membership, corruption, score materialization | Mô hình prior khả dụng và lỗi tương quan |
| `metrics.py` | F1, endpoint metrics, weighted cost, bootstrap, tests-to-target | Đo cost-quality và gate statistic |
| `gates.py` | K0/K1 record/evaluator | Quyết định machine-readable |
| `runner.py` | Seed/config/revision/artifact orchestration | Reproducibility và failure handling |
| `phase1_execution.py` | Inventory, preflight, serial shard, completion audit, K1 analysis | Tái lập ma trận Phase 1 và báo cáo |
| `phase1_parallel.py` | Queue, atomic claims, worker slots, graph-level resume | Chạy tiếp mà không chạy lại row hoàn tất |
| `algorithms/icd_reference.py` | PAG snapshot, ICD-Sep candidate enumerator độc lập | Reference primitive cho hướng ICD |
| `algorithms/icd_official_adapter.py` | Adapter tới pinned causality-lab ICD | So sánh reference chính thức với primitive độc lập |
| `algorithms/epoch.py` | Frozen epoch, candidate digest, canonical frontier, checkpoint, commit | Nền tảng correctness cho blockwise execution |
| `ci_batch.py` | CPU float64 batched Gaussian CI, memory planning, shared-S Schur path | Numerical backend, chưa phải novelty thuật toán |
| `tiers/reference.py` | Tier ordering, past, simple-tFCI restriction, robust envelope oracle | Reference semantics cho Fallible-Tier |

### 6.3. Graph và CI contract

`GeneratedGraph` giữ DAG đầy đủ, observed nodes, latent nodes, seed, parameters và digest. `OracleCI` chỉ cho phép endpoint/conditioning set thuộc observed nodes và trả independent từ `networkx.is_d_separator`.

`GaussianCI` hỗ trợ samples, covariance hoặc correlation matrix; các inversion mode là `strict`, `ridge`, `pinv`. Với strict mode:

```text
df = n - |S| - 3
rho = partial correlation from precision matrix
z = |atanh(rho)| * sqrt(df)
p = 2 * NormalSurvival(z)
independent iff p > alpha
```

Nếu CI trả `independent=None` do singular, nonfinite, invalid precision hoặc insufficient degrees of freedom, `UndefinedCIResultError` dừng mutation đồ thị và ghi structured failure artifact.

### 6.4. Scheduler contract

Mọi scheduler nhận cùng `QueryCandidate` hợp lệ và chỉ trả `ScoreBreakdown`. `Scheduler.order()` sort theo `-total_score`, tie-break deterministic và query ID.

| Scheduler | Tín hiệu |
|---|---|
| `stable_default` | canonical lexicographic order |
| `random_valid` | hash(seed, query ID) |
| `cost_only` | chi phí ước lượng thấp trước |
| `graph_only` | degree hiện tại cộng cost tie-break |
| `prior_guided` | prior score cộng cost |
| `oracle_query` | independent result biết trước; chỉ dùng upper bound, `allows_ground_truth=True` |

### 6.5. Scheduled FAS và provenance

`scheduled_fas()` đóng băng candidate theo từng depth, lấy thứ tự từ scheduler, chạy CI, thu thập mọi witness independent nhưng chỉ chọn một witness canonical có rank nhỏ nhất cho mỗi pair. Sau barrier, graph mới được mutate và sepset được ghi.

`run_scheduled_fci()` sau FAS gọi upstream causal-learn cho:

1. reorient circle;
2. rule 0 trước Possible-D-SEP;
3. `removeByPossibleDsep` qua `LoggedCIProxy`;
4. rule 0 sau Possible-D-SEP;
5. vòng rules R1–R10;
6. đánh dấu PAG và trả `PAGResult`.

Nếu budget dừng trong FAS, hệ thống trả `DiscoveryState(completed=False)` gồm graph snapshot, query đã chạy, query chưa chạy và budget; không gọi đó là PAG cuối.

### 6.6. Batch CI và memory

`GaussianBatchCI` dùng NumPy float64 trên CPU, bucket theo local size hoặc power-of-two padding. `plan_batch_memory()` ước lượng bytes/query, batch capacity, số wave và peak workspace theo memory budget.

Kỹ thuật hiện có:

- exact-size batch;
- power-of-two padding;
- bounded memory waves;
- shared-conditioning-set Schur complement;
- diagnostics về work, bucket, RSS và shared factorization.

Đây là backend có equality contract; chưa có claim GPU speedup.

### 6.7. Resume và shard

Serial Phase 1 dùng immutable row theo logical run ID. `phase1_execution.py` bỏ qua row đã completed nếu config digest khớp, còn manifest chỉ là orchestration state.

Queue graph-worker dùng:

- atomic claim bằng `O_CREAT|O_EXCL`;
- identity hostname/PID/process creation time;
- stale claim recovery;
- graph-level claims và worker manifests;
- row validation bằng logical key, graph digest, seeds và config digest.

Trong code handoff hiện tại, delta contract yêu cầu **ba graph workers**, còn serial plan ghi `execution_workers=1`. Vì vậy số worker hợp lệ phải đọc từ contract đang cài đặt, không suy ra từ các lệnh cũ trong chat.

## 7. Sprint thuật toán đã hoàn thành

### C0 — Correctness repair (`G0_CORRECTNESS_BASELINE`)

Đã sửa hai blocker:

1. GaussianCI không còn luôn trả dependent sau khi tính p-value;
2. skeleton không còn union nhiều separating witness của cùng pair; chỉ canonical witness được commit.

Report C0 ghi `67 passed, 15 skipped`, không bao gồm claim batching, block executor, GPU hay performance.

### C1 — Reference contract và CPU batch (`G1_BATCH_CI_EQUIVALENT`)

Đã thêm:

- artifact schema 0.2.0;
- canonical immutable `CIQuery`;
- scalar/batch equality audit;
- exact-size và power-of-two batching;
- shared-S Schur path;
- bounded-memory planner;
- ICD reference adapter và structured blocked result.

Audit C1 ghi 256 query mỗi strategy, zero mismatch ngoài/trong numerical margin, final output/candidate trace/evidence query IDs đều equal. Full suite có optional reference: 103 passed; default: 88 passed, 15 skipped.

### C2 — Frozen stable epoch (`G2_STABLE_EPOCH_SOUND`)

Epoch là barrier giữa:

```text
freeze snapshot + candidate family
    -> execute CI theo order/batch/checkpoint
    -> canonical witness selection
    -> commit graph mutation một lần
```

Ba digest không trộn lẫn:

- `snapshot_digest`: graph state đầu epoch;
- `epoch_id`: snapshot, radius, reference ID, contract version;
- `candidate_family_digest`: toàn bộ candidate family canonical.

Audit C2 ghi 64 truth tables × 4 schedule permutations = 256 audited schedules, zero mismatch ở deletion, witness, completion order, frontier, replay/resume, provenance và budget. Claim boundary: C2 chưa chứng minh dynamic ICD equivalence, block soundness hay speedup.

## 8. Hai hướng tối ưu chính

### 8.1. Blockwise Asynchronous ICD

#### Câu hỏi

ICD tăng conditioning radius theo vòng toàn cục. Có thể chia một round thành các block có dependency certificate, chạy block độc lập hoặc bất đồng bộ, nhưng vẫn:

- công bố prefix an toàn;
- hoàn tất toàn bộ block thì bằng reference global round;
- không false definite endpoint;
- nếu dependency graph thành giant component thì suy biến về global ICD?

#### Đối tượng thuật toán

1. snapshot PAG bất biến;
2. sinh candidate family ICD-Sep độc lập snapshot;
3. tạo evidence/dependency graph hoặc hypergraph;
4. đóng block theo read/write footprint và PDS paths;
5. chạy block theo prior/resource policy;
6. commit duy nhất ở barrier;
7. trả `DiscoveryState + EvidenceCertificate` cho prefix.

#### Nghĩa vụ định lý

| Mục tiêu | Nội dung |
|---|---|
| Certificate soundness | Mỗi witness được chứng minh bởi CI và predicate ICD hợp lệ |
| Conservative prefix | Mọi definite claim ở prefix đúng trên mọi legal completion |
| Pairwise commutation | Hai block không phụ thuộc có thể đổi thứ tự mà không đổi commit |
| Global confluence | Chạy hết các block cho cùng kết quả reference round |
| Decomposition characterization | Nêu khi nào block tách được và khi nào buộc collapse |

#### Phản ví dụ bắt buộc

Diamond separator, collider activation, latent confounder, discriminating path crossing blocks, deletion tạo unshielded triple, PDS-dominant motif, giant dependency component và same evidence/different mutation order.

#### Tiêu chí kill

- false definite endpoint: kill theorem;
- final output khác reference: kill confluence;
- dependency graph luôn là giant component: revise thành staged/block-synchronous hoặc dừng;
- không thắng frontier ICD/FCIT sau cost accounting: no-go về algorithmic benefit.

### 8.2. Fallible-Tier Robust Envelope

#### Câu hỏi

Nếu prior đưa ra tier claims có thể sai theo nhóm và `Gamma` là số nhóm vi phạm tối đa, có thể tạo một envelope candidate an toàn nhỏ hơn full PDS không?

Ký hiệu mục tiêu:

```text
J_Gamma(X,Y) = PDS(X,Y) ∩ R_Gamma(X,Y)
```

Trong đó `R_Gamma` là tập ứng viên còn có thể thuộc `past_tau({X,Y})` với mọi tiering phù hợp claim và ngân sách vi phạm.

#### Quy tắc safety

- nếu `K` rỗng, envelope fallback về full PDS;
- nếu uncertainty set rỗng/không certify, fallback full PDS;
- tier prior không được trực tiếp orient edge trong phiên bản này;
- exactness là oracle-level trước, finite-sample sau;
- phải ghi coverage–shrinkage trade-off, không che trường hợp envelope collapse.

#### Nghĩa vụ định lý

1. reference restriction lemma;
2. robust superset lemma;
3. oracle equivalence khi true tier nằm trong uncertainty set;
4. thuật toán tính envelope có complexity rõ;
5. smallest universally safe envelope hoặc collapse/no-free-lunch result.

#### Rủi ro cốt lõi

Nếu cho phép một claim tier sai, phép union qua các tier hypothesis có thể khôi phục gần như toàn bộ PDS. Khi đó phương pháp vẫn an toàn nhưng không có lợi ích tính toán; kết quả này phải được ghi là negative scientific result, không được che bằng thêm LLM/GPU.

## 9. Hướng phụ và vai trò GPU

### OP-PDS

One-Probe Possible-D-SEP phù hợp làm falsification screen nhỏ, không phải claim paper mặc định. Nó có thể kiểm tra local separator invariance và PDS headroom, nhưng chưa đủ bảo đảm PAG toàn cục.

### dcFCI/PAG branch-and-bound

Có thể nghiên cứu sau khi reference PAG và candidate score ổn định. Generic branch-and-bound theorem không đủ novelty; cần bound/closure đặc thù PAG.

### GPU

GPU là tầng hệ thống thứ cấp:

```text
algorithmic semantics
    -> candidate/dependency barrier đúng
    -> CPU scalar reference
    -> CPU batch equality
    -> profile transfer/kernel threshold
    -> GPU batch CI
```

Không được gọi “đóng góp khoa học” chỉ vì:

- port covariance inversion sang GPU;
- tăng số CPU worker;
- vectorize hoặc cache;
- chạy nhiều query mà không chứng minh dependency safety.

Claim GPU chỉ được mở sau khi có equality audit, memory bound, deterministic replay và benchmark end-to-end so với CPU batch/FCIT/ICD.

## 10. Testbed chung cho phần thuật toán

| Tầng | Nội dung | Mục đích |
|---|---|---|
| T0 | Motif nhỏ: chain, fork, collider, latent confounder, diamond, discriminating path | Debug semantics và counterexample |
| T1 | Exhaustive DAG/PAG nhỏ với latent mask | Tìm mismatch exact |
| T2 | Random sparse, hub, modular, scale-free, PDS-dominant | Đo headroom và block width |
| T3 | Linear Gaussian finite sample | Đo tương tác scheduler–CI error |
| T4 | Prior independent/node/motif/source-correlated | Đo robustness |
| T5 | CPU/GPU/worker/memory sweep | Đo wall time và systems cost |

Baseline bắt buộc:

- upstream FCI;
- pinned official ICD;
- stable implementation;
- random-valid, cost-only, graph-only;
- oracle upper bound;
- RFCI-stable;
- FCIT hoặc targeted latent baseline;
- no-tier, perfect-tier và hard-tier cho tier experiment.

Equality phải tách ba mức:

1. candidate family equality;
2. evidence/provenance equality;
3. final PAG endpoint equality.

Không được dùng một equality metric duy nhất để che việc query trace khác hoặc endpoint sai.

## 11. Rủi ro và ranh giới claim

| Rủi ro | Mức | Cách kiểm soát |
|---|---|---|
| Prior leak vào graph evidence | Critical | provenance event chỉ nhận CI/rule evidence; invariant test |
| K1 selection bias do thiếu shard | High | hoàn tất 800 logical rows, paired reanalysis |
| Nói quá phạm vi FAS thành toàn FCI | High | ghi `FAS_STABLE_SKELETON_ONLY` trong report/abstract |
| Reference circularity | High | local ICD primitive + pinned official adapter + independent audit |
| PDS dependency giant component | High | đo component distribution, kill hoặc hạ claim |
| Robust envelope collapse | High | report envelope/PDS ratio và no-free-lunch result |
| Prior lỗi tương quan bị mô hình hóa sai | High | source/node/motif corruption với cùng AUC |
| Finite-sample scheduling gain làm tăng endpoint harm | High | endpoint error và CI cùng bootstrap unit |
| GPU overhead lớn hơn compute | Medium | profile transfer/kernel launch và batching threshold |
| Resume tạo duplicate/mismatch | Medium | logical key, digest, atomic row và stale-claim recovery |
| Tài liệu gate stale | Medium | chỉ dùng checkpoint mới nhất, sau đó regenerate machine gate |

Các claim hiện **chưa được phép**:

- “Safety Prior đã chứng minh đúng trên full FCI/PAG”;
- “LLM luôn cải thiện FCI”;
- “GPU tạo ra đóng góp thuật toán”;
- “K1 đã là formal PASS 800/800”;
- “K2/K3/K4 đã đạt”;
- “Blockwise ICD hoặc robust envelope đã đúng” khi chưa qua theorem kill.

## 12. Kế hoạch triển khai tiếp theo

### Bước 1 — Đóng source-of-truth K1

1. hoàn tất các logical rows còn thiếu;
2. chạy completion audit;
3. kiểm tra duplicate/missing/config digest và artifact references;
4. tái sinh gate report từ rows, không sửa tay;
5. ghi riêng snapshot cũ và snapshot mới nếu số liệu thay đổi.

### Bước 2 — Kết thúc Sprint 0 ICD

1. mở rộng official/local ICD conformance trên random và exhaustive small PAG;
2. thêm discriminating-path và PDS-dominant motifs;
3. ghi rõ dynamic/precomputed trace mismatch; không gọi chúng là tương đương nếu chỉ final output khớp;
4. chốt `REFERENCE_PASS` hoặc hạ Blockwise ICD thành block-synchronous variant.

### Bước 3 — Chạy theorem kill cho hai hướng

Chạy Blockwise ICD và robust envelope song song ở mức oracle, không LLM, không GPU, không finite-sample. Mỗi hướng phải có:

- executable reference;
- counterexample suite;
- exact output/evidence equality;
- cost frontier;
- decision `GO`, `REVISE` hoặc `KILL`.

### Bước 4 — Prior khả dụng và lỗi tương quan

Chỉ với hướng đã qua oracle kill:

- calibrate Prior B ở AUC đã đăng ký;
- chạy independent/node/motif/source corruption;
- so với FCIT và baseline prior-free mạnh nhất;
- đo recovery ratio và failure regime.

### Bước 5 — Finite sample và GPU

Sau khi semantics và prior robustness đứng vững:

- chạy GaussianCI strict trên n=500/2000;
- xác minh endpoint harm;
- port batch executor sang GPU tùy profile;
- tách algorithmic saving, batch saving và hardware saving trong decomposition của runtime.

## 13. Cấu trúc file tham chiếu

### Nền tảng nghiên cứu

- [`01_safe_imperfect_priors_high_level_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/01_safe_imperfect_priors_high_level_vi.md>)
- [`02_safe_imperfect_priors_chuyen_sau_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/02_safe_imperfect_priors_chuyen_sau_vi.md>)
- [`02a_safe_imperfect_priors_kill_test_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/02a_safe_imperfect_priors_kill_test_vi.md>)

### Kill test

- [`docs/kill_test/00_problem_restated.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/kill_test/00_problem_restated.md>)
- [`docs/kill_test/01_repository_audit.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/kill_test/01_repository_audit.md>)
- [`docs/kill_test/02_implementation_plan.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/kill_test/02_implementation_plan.md>)
- [`docs/kill_test/03_scientific_contract.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/kill_test/03_scientific_contract.md>)
- [`docs/kill_test/04_evaluator_contract.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/kill_test/04_evaluator_contract.md>)
- [`docs/kill_test/open_issues.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/kill_test/open_issues.md>)

### Hướng tối ưu và research contract

- [`docs/research/latent_fci_optimization_directions_4rounds_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/research/latent_fci_optimization_directions_4rounds_vi.md>)
- [`docs/research/block_icd_robust_tier_contracts_and_testbed_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/research/block_icd_robust_tier_contracts_and_testbed_vi.md>)
- [`docs/research/op_pds_minimal_plan_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/research/op_pds_minimal_plan_vi.md>)
- [`docs/research/sprint0_reference_semantics_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/docs/research/sprint0_reference_semantics_vi.md>)

### Implementation và audit reports

- [`handoff/12_certified_blockwise_icd_implementation_plan_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/handoff/12_certified_blockwise_icd_implementation_plan_vi.md>)
- [`handoff/13_c0_correctness_repair_report_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/handoff/13_c0_correctness_repair_report_vi.md>)
- [`handoff/14_c1_contracts_cpu_batch_report_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/handoff/14_c1_contracts_cpu_batch_report_vi.md>)
- [`handoff/15_c2_frozen_stable_epoch_report_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/handoff/15_c2_frozen_stable_epoch_report_vi.md>)
- [`reports/research_checkpoint_2026-10-19_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/reports/research_checkpoint_2026-10-19_vi.md>)

### Amendment về quy mô chạy

- [`reports/reduced_scale_amendment_2026-10-21_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/reports/reduced_scale_amendment_2026-10-21_vi.md>) — giao thức `REDUCED-SCALE` cho pilot trên máy yếu, cùng nhánh benchmark topology bán tổng hợp; không thay thế formal K0–K4.
- [`reports/decision_addendum_A001_spec06_2026-10-21_vi.md`](<D:/REsearch/causal multi-agent/safety_prior/reports/decision_addendum_A001_spec06_2026-10-21_vi.md>) — quyết định hợp nhất sau review A-001/Spec 06; đang `REVIEW_PENDING`, chưa bật cache và chưa chạy reduced protocol.

## 14. Kết luận

Repo đã có một nền tảng khá chặt cho nghiên cứu falsifiable: candidate schema bất biến, CI scalar/batch contract, provenance, canonical witness, frozen epoch, checkpoint/resume, gate evaluator và testbed K0–K4.

Kết quả hiện tại chứng minh ba điều giới hạn nhưng quan trọng:

1. thay đổi thứ tự query trong phạm vi đã đăng ký có thể giữ semantics khi chạy đủ ngân sách;
2. trong FAS-stable skeleton tồn tại oracle headroom đáng kể;
3. batch CPU và frozen epoch đã có cơ chế audit độc lập trước khi thêm block hoặc GPU.

Nó chưa chứng minh rằng Safety Prior thực tế hữu ích, chưa chứng minh robustness trước lỗi tương quan, và chưa chứng minh toàn bộ FCI/PAG được tối ưu. Bước khoa học đúng tiếp theo là **đóng reference ICD và falsify Blockwise ICD/Fallible-Tier Robust Envelope**, sau đó mới đưa prior thực tế, finite sample và GPU vào.
