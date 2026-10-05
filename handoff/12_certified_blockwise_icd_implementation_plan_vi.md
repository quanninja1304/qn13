# Implementation plan — Certified Blockwise ICD với batched CI và Safety Prior

**Tài liệu nguồn:** [11_formal_tensorization_fci_icd_survey_vi.md](11_formal_tensorization_fci_icd_survey_vi.md)

**Trạng thái:** kế hoạch triển khai chi tiết, chưa phải tuyên bố thuật toán đã đúng hoặc đã nhanh hơn

**Phạm vi chính:** oracle ICD trước, Gaussian finite-sample sau; PAG có biến ẩn; CPU reference trước GPU; prior chỉ điều khiển tài nguyên

**Quyết định dự án:** K1 được dùng là `PASS`; K2–K4 chưa chạy

## 1. Kết luận kiến trúc

Hướng mới không được triển khai dưới tên “tensor hóa toàn bộ FCI/ICD”. Kiến trúc mục tiêu là:

> **Certified Blockwise ICD:** mỗi vòng ICD tạo một candidate family hợp lệ từ snapshot đã khóa, thực thi CI theo batch có giới hạn bộ nhớ, commit duy nhất các witness đã được kiểm định, và chỉ chạy song song giữa các block có dependency certificate. Safety Prior được phép xếp hạng block/wave nhưng không thay đổi eligibility, CI decision hay evidence commit.

Tensor/GPU là backend. Đóng góp thuật toán nằm ở separator coverage, dependency certificate, commutation/confluence và work efficiency.

### 1.1 Luồng end-to-end mục tiêu

```text
Data / oracle DAG
  |
  v
Scalar CI contract + canonical reference
  |
  +--> batched CPU CI (D1-D2) --> optional batched GPU CI
  |
  v
PAG snapshot at ICD radius r
  |
  v
Exact ICD-Sep candidate enumeration
  |  - induced-subgraph path condition
  |  - avoid opposite endpoint
  |  - cardinality/radius
  |  - optional possible-ancestor filter
  v
Frozen epoch candidate family
  |
  v
Semantic read/write footprints
  |
  v
Conservative dependency graph + certificates (D7)
  |
  +--> giant component: reference one-block fallback
  |
  v
Ready blocks
  |
  +--> Safety Prior ranks blocks/waves only
  |
  v
Bounded-memory batched execution
  |
  v
Witness records + deterministic sepset selection (D5-D6)
  |
  v
Barrier commit of edge deletions
  |
  v
Reference anytime-FCI orientation closure
  |
  +--> optional D4/R4 algebra audit, not authoritative initially
  |
  v
Canonical PAG equality + evidence/provenance audit
  |
  +--> incomplete budget: DiscoveryState
  +--> completed all radii: PAGResult
```

### 1.2 Ba mặt phẳng

| Mặt phẳng | Được làm | Không được làm |
|---|---|---|
| Evidence plane | CI test, witnessed sepset, reference orientation rule, certified graph mutation | dùng prior score để xóa/định hướng cạnh |
| Control plane | rank block/query wave, cấp budget, chọn device/batch size, speculative execution | đổi candidate eligibility hoặc coi prediction là CI fact |
| Audit plane | digest, certificate, trace, cost counters, equality report | âm thầm sửa artifact/report generated |

## 2. Phạm vi MVP và phần hoãn

### 2.1 MVP phải làm

1. Sửa hai correctness blocker hiện hữu: sepset union và `GaussianCI` luôn trả dependent.
2. Khóa scalar CI và scalar stable-epoch reference.
3. Triển khai batched Gaussian CI trên CPU theo D1–D2.
4. Triển khai frozen ICD round với separator coverage theo D5–D6.
5. Xây executable dependency certificate và one-block fallback theo D7.
6. Đo work, span proxy, memory, speculative work và certificate overhead.
7. Chỉ sau các gate trên mới thêm GPU backend.
8. Sau GPU correctness mới cho Safety Prior xếp hạng ready blocks/waves.

### 2.2 Không thuộc MVP

- Không thay toàn bộ R0–R10 bằng tensor compiler.
- Không tuyên bố raw R1–R10 tạo monotone fixed point.
- Không dùng walk reachability thay simple-path predicate trong orientation.
- Không dùng D4/R4 algebra làm authoritative orientation trước conformance gate.
- Không tích hợp LLM trước khi prior-free algorithm vượt mechanism gate.
- Không regularize/pseudoinverse CI rồi coi là cùng statistical procedure.
- Không gọi GPU throughput là algorithmic work reduction.
- Không gọi budgeted prefix là PAG hoàn chỉnh.

### 2.3 Hai track phụ

`Track-R4`: kiểm chứng D4 như một exact discriminating-path primitive.

`Track-Closure`: nghiên cứu certificate system cho R0–R10 theo D8. Track này chỉ được nhập vào core sau khi có proof và exhaustive conformance riêng.

## 3. Ánh xạ D1–D8 sang deliverable

| Mệnh đề | Deliverable code | Test bắt buộc | Gate |
|---|---|---|---|
| D1 | scalar/batch Schur or local-precision kernel | scalar–batch rho/p/decision equality | G1 |
| D2 | exact-size bucket và identity-padding reference | padding invariance, memory bound | G1 |
| D3 | ordered-edge lift cho PDS walk envelope | exact walk equality; path-superset check | G2-R |
| D4 | R4 discriminating-path predicate | exhaustive reference equivalence | G2-R |
| D5 | frozen stable epoch + OR deletion + canonical witness | schedule-invariant deletion/sepset | G2 |
| D6 | ICD round coverage contract | reference round/PAG equality | G3 |
| D7 | footprint, dependency certificate, block executor | critical-pair/commutation/confluence | G4-A/G4-B |
| D8 | fact/certificate research prototype | rule closure equality và conflict tests | hoãn `GC-CLOSURE` |

## 4. Kiến trúc package đề xuất

Giữ module hiện có để không phá kill-test; thêm namespace mới cho hướng thuật toán:

```text
src/safety_prior/
├── ci.py                              # sửa scalar GaussianCI, giữ OracleCI
├── ci_batch.py                        # API batch, CPU reference, bucketing
├── models.py                          # bổ sung witness/certificate/state types
├── provenance.py                      # evidence IDs, batch/wave/block fields
├── algorithms/
│   ├── icd_reference.py               # primitive hiện có
│   ├── icd_official_adapter.py        # reference đã pin
│   ├── epoch.py                       # frozen candidate family + commit
│   ├── icd_round.py                   # one certified radius
│   ├── path_algebra.py                # D3 và D4 reference predicates
│   ├── dependencies.py                # semantic footprints/certificates
│   └── blockwise_icd.py               # block execution + fallback
├── backends/
│   ├── __init__.py
│   ├── cpu_batch.py                   # NumPy/SciPy backend
│   └── torch_batch.py                 # optional CUDA backend
├── execution/
│   ├── workspan.py                    # counters và bound fields
│   └── algorithm_pilot.py             # run/resume/artifacts
├── pilots/
│   ├── equality.py                    # mở rộng equality hiện có
│   ├── schemas.py                     # schema version mới
│   └── counterexamples.py             # minimal failure artifacts
└── cli.py                             # command pilot/audit/benchmark

configs/tensorized_icd/
├── correctness.yaml
├── cpu_batch.yaml
├── block_oracle.yaml
├── gpu_batch.yaml
├── prior_control.yaml
└── finite_sample.yaml

tests/
├── ci/
├── algorithms/
├── property/
└── integration/

artifacts/tensorized_icd/
reports/tensorized_icd/
```

Không bắt buộc tạo toàn bộ file ngay Sprint đầu. Mỗi file chỉ xuất hiện khi interface và test tương ứng đã khóa.

## 5. Data contracts cốt lõi

### 5.1 CI query và result

```python
@dataclass(frozen=True)
class CIQuery:
    query_id: str
    x: int
    y: int
    conditioning_set: tuple[int, ...]
    phase: str
    epoch_id: str
    pair_order: int
    canonical_rank: int

@dataclass(frozen=True)
class CIResult:
    independent: bool | None
    p_value: float | None
    statistic: float | None
    effect: float | None
    numerical_status: str       # ok | singular | insufficient_df | nonfinite
    decision_margin: float | None
```

`independent=None` nghĩa là test không xác định; không được ngầm chuyển thành dependent. Oracle luôn có `numerical_status="ok"`.

### 5.2 Batch contract

```python
class BatchCI(Protocol):
    backend: str
    def test_many(self, queries: Sequence[CIQuery]) -> list[CIResult]: ...
```

Invariant:

- output giữ đúng thứ tự input;
- mỗi result chỉ phụ thuộc data/oracle và query, không phụ thuộc các query cùng batch;
- cùng query không đổi decision theo batch composition;
- conditioning set được canonicalize và không có endpoint/duplicate;
- backend phải công bố dtype, device, regularization mode và tolerance;
- numerical failure không được che bằng clipping hoặc pseudoinverse im lặng.

### 5.3 Witness và sepset

```python
@dataclass(frozen=True)
class SeparationWitness:
    pair: tuple[int, int]
    conditioning_set: tuple[int, ...]
    query_id: str
    ci_result_digest: str
    epoch_id: str
    canonical_rank: int
```

Mỗi stored sepset phải trỏ tới đúng một `SeparationWitness`. Không có operation union witness.

Nếu nhiều witness tồn tại, `SepsetPolicy` của MVP chọn `min(canonical_rank)`. Canonical rank được sinh trước scheduling nên prior, worker completion order và GPU batch order không thay đổi sepset.

### 5.4 Epoch snapshot

```python
@dataclass(frozen=True)
class EpochSnapshot:
    epoch_id: str
    radius: int
    pag_digest: str
    pag: PAGSnapshot
    candidate_family_digest: str
    reference_id: str
```

Mọi query của epoch phải có `state_digest == snapshot.pag_digest`. Mutation chỉ xảy ra ở commit barrier.

### 5.5 Dependency certificate

```python
@dataclass(frozen=True)
class SemanticFootprint:
    event_id: str
    read_edges: frozenset[EdgeKey]
    read_nonadjacencies: frozenset[PairKey]
    read_path_contexts: frozenset[PathContextKey]
    read_sepsets: frozenset[PairKey]
    write_edges: frozenset[EdgeKey]
    opens_events: frozenset[str]

@dataclass(frozen=True)
class DependencyCertificate:
    left_event: str
    right_event: str
    independent: bool
    reasons: tuple[str, ...]
    snapshot_digest: str
    checker_version: str
```

Trong MVP, nếu checker không chứng minh được độc lập thì mặc định là dependent. False dependency chỉ giảm parallelism; false independence có thể phá correctness và là lỗi P0.

### 5.6 Block plan

```python
@dataclass(frozen=True)
class BlockPlan:
    epoch_id: str
    blocks: tuple[tuple[str, ...], ...]
    dependency_edges: tuple[tuple[str, str], ...]
    certificate_digest: str
    fallback_one_block: bool
    estimated_work: int
    critical_path_work: int
```

### 5.7 Output

`DiscoveryState` cần bổ sung:

- current ICD radius;
- epoch snapshot digest;
- completed/pending block IDs;
- pending canonical witnesses;
- dependency certificate digest;
- completeness certificate hoặc lý do chưa hoàn tất;
- work/memory counters;
- device/backend metadata.

Chỉ `PAGResult` được tạo sau khi mọi radius và authoritative orientation closure hoàn tất.

## 6. WP0 — Correctness quarantine và sửa baseline

**Mục tiêu:** không xây batch/block/GPU trên semantics sai.

### 6.1 WP0-A — Sửa GaussianCI

Hiện [ci.py](../src/safety_prior/ci.py) tính `p` nhưng trả `CIResult(False, p, stat)`. Kế hoạch:

1. thêm `alpha` vào `GaussianCI.__init__` hoặc một immutable decision policy;
2. quyết định `independent = p_value > alpha`;
3. dùng đúng Fisher-Z degrees of freedom `n - |S| - 3`;
4. phân biệt correlation/covariance input;
5. không dùng `max(1, ...)` để che insufficient degrees of freedom;
6. không dùng `pinv` mặc định như thể cùng thủ tục exact;
7. tạo explicit modes:
   - `strict`: singular/insufficient DF trả undefined;
   - `ridge(lambda)`: thủ tục khác, tên backend khác;
   - `pinv`: chỉ diagnostic, không dùng cho equality theorem;
8. lưu `rho`, statistic, p-value, decision margin và numerical status.

Tests:

- unconditional independent Gaussian;
- chain/fork/collider synthetic Gaussian;
- scalar formula so SciPy/manual Schur;
- `n <= |S|+3` trả undefined;
- singular covariance không âm thầm pass;
- decision hai phía đúng tại alpha;
- kết quả bất biến với column ordering sau canonicalization.

### 6.2 WP0-B — Loại sepset union

Hiện [discovery.py](../src/safety_prior/discovery.py) union mọi conditioning set độc lập của một pair. Thay bằng:

1. lưu danh sách `SeparationWitness` riêng;
2. chọn một witness đã kiểm định theo canonical policy;
3. provenance event trỏ đúng `query_id` của witness được chọn;
4. nếu conservative/majority mode được thêm sau, lưu toàn bộ witness nhưng không union chúng;
5. không commit edge deletion khi epoch dừng giữa chừng và canonical choice chưa được chứng nhận;
6. thêm regression motif nơi `S1` và `S2` đều là witness nhưng `S1 union S2` mở collider/không còn là witness.

### 6.3 WP0-C — Quarantine claim

Cho tới khi WP0 pass:

- K1 vẫn chỉ được diễn giải trong scope skeleton/oracle đã đăng ký;
- không dùng `GaussianCI` cho K4;
- không dùng stored sepset hiện tại để claim final-PAG finite-sample correctness;
- không benchmark GPU.

### 6.4 Gate G0

`G0_CORRECTNESS_BASELINE = PASS` khi:

- mọi graph event xóa cạnh có một witnessed sepset ID;
- không còn union sepset trong evidence path;
- scalar Gaussian tests pass;
- oracle regression/K0 không đổi canonical output;
- full current test suite pass;
- failure artifact được tạo cho numerical undefined thay vì silently continuing.

Nếu sửa semantics làm K0 mismatch, dừng và điều tra; không cập nhật expected output để ép test xanh.

## 7. WP1 — Khóa reference và artifact contract

### 7.1 Authoritative references

- FAS/FCI comparison: causal-learn revision đã pin bởi environment.
- ICD candidate/orientation: official causality-lab revision `36625da6eeef059e36dab2b4467235a036136b76`.
- Local `icd_reference.py`: candidate enumerator, không giả làm complete ICD round.
- Canonical equality: node order, skeleton, endpoint matrix và witnessed sepset validity.

### 7.2 Reference modes

Mỗi benchmark phải ghi một mode:

| Mode | Ý nghĩa |
|---|---|
| `dynamic_reference` | candidate/state được cập nhật theo official reference |
| `frozen_epoch_reference` | candidate family đóng băng đúng contract D5/D6 |
| `block_candidate` | frozen epoch cộng dependency/block execution |
| `tensor_backend` | cùng algorithm, đổi scalar thành batch backend |

Không so `block_candidate` với dynamic reference rồi gọi mọi trace difference là bug. Claim phải nêu equality target: trace, evidence hay final PAG.

### 7.3 Artifact schema version 0.2.0

Mỗi run row phải có:

- graph/data/prior/scheduler seeds;
- Git revision, config digest, dependency lock;
- reference ID/mode;
- backend/device/dtype;
- radius/epoch ID;
- candidate count, executed count, skipped count;
- independent witness count;
- block count/largest block/ready width;
- dependency build work/time;
- CI arithmetic work proxy;
- graph work proxy;
- speculative work;
- peak RSS/VRAM;
- exact equality fields;
- status/failure signature.

Full trace chỉ lưu khi mismatch, first failure signature, numerical instability hoặc sample theo policy.

### 7.4 Gate G0.5

- official ICD optional dependency chạy được trên clean reference environment;
- 40-graph audit tái lập;
- regression seed `74304` được giữ;
- artifact validator từ chối thiếu field;
- resume không tạo duplicate logical key;
- generated report luôn ghi reference mode.

## 8. WP2 — Batched Gaussian CI trên CPU (D1–D2)

### 8.1 API và preprocessing

`GaussianBatchCI` nhận data một lần, center data và tính covariance/correlation một lần. Query được nhóm theo `d=|S|+2`.

Pipeline một batch:

1. validate/canonicalize query;
2. gather local covariance blocks `C_q`;
3. group exact size hoặc geometric bucket;
4. dùng Cholesky/linear solve nếu SPD, không explicit inverse nếu không cần;
5. lấy local precision/Schur correlation;
6. Fisher transform với `k` thật;
7. áp cùng decision policy scalar;
8. trả result theo input order;
9. ghi numeric diagnostics.

### 8.2 Hai chiến lược batching

`exact_size`: mọi query trong batch có cùng `d`; đây là backend correctness đầu tiên.

`power_of_two`: identity-padding tới `D=2^ceil(log2 d)` theo D2; chỉ bật sau padding test.

Không pad mọi query tới `P`.

### 8.3 Shared-S optimization

Phép chia sẻ Schur complement cho nhiều pair dùng cùng `S` theo phương trình (8) được triển khai sau exact-size backend:

- key bằng canonical `S`;
- chỉ dùng khi số pair reuse vượt threshold;
- cost model quyết định shared-S hay per-query solve;
- kết quả phải khớp scalar;
- ghi `shared_factorization_count` và work saved estimate.

### 8.4 Bounded-memory planner

Cho memory budget `M_CI`, planner chọn:

```text
B_k <= floor(M_CI / bytes_per_matrix(k+2))
waves_k = ceil(Q_k / B_k)
```

Thực tế phải tính thêm gather buffers, factorization workspace, results và safety factor đo bằng profiling. Planner không được dựa duy nhất trên asymptotic formula.

### 8.5 Tests

- scalar vs batch `rho`, statistic, p-value;
- exact decision equality ngoài numerical margin;
- batch composition/permutation invariance;
- exact-size vs power-of-two padding;
- shared-S vs per-query;
- float64 CPU reference;
- singular/near-singular/insufficient DF;
- batch size 1;
- mixed `k` bucketing;
- memory planner không vượt configured budget trong tolerance;
- deterministic replay.

### 8.6 Gate G1

`G1_BATCH_CI_EQUIVALENT = PASS` khi:

- 100% decision equality cho cases ngoài pre-registered numeric margin;
- mismatches trong margin được ghi, không che;
- p/rho error nằm trong tolerance theo dtype;
- undefined status equality 100%;
- peak workspace tuân budget;
- work counters khớp số query và matrix sizes;
- CPU batch không đổi candidate/evidence/final output trên integration suite.

Speedup không phải điều kiện của G1.

## 9. WP3 — Frozen stable epoch và canonical evidence (D5)

### 9.1 Epoch construction

Tại đầu radius/depth:

1. canonicalize PAG snapshot;
2. tạo `epoch_id = hash(graph_digest, radius, reference_id, contract_version)`;
3. sinh toàn bộ eligible candidates từ đúng snapshot;
4. gán `canonical_rank` trước khi scheduler can thiệp;
5. khóa candidate-family digest;
6. chỉ sau đó cho control plane chia wave/xếp thứ tự.

Candidate sinh sau mutation phải thuộc epoch mới, không được chèn vào epoch đang chạy mà không đổi contract.

### 9.2 Execution semantics

- Các CI query trong epoch không mutate graph.
- Independent results tạo `SeparationWitness` provisional.
- Dependent results không tạo graph fact ngoài audit record.
- Sau khi epoch hoàn tất, deletion của pair là OR trên witnessed results.
- Sepset là witnessed set có canonical rank nhỏ nhất, không phải first-completed và không phải union.
- Mọi deletion được commit atomically tại barrier theo canonical pair order.

### 9.3 Work-efficient early cancellation

Batching tất cả candidate giữ deletion equality nhưng có thể tăng work. MVP hỗ trợ hai mode:

- `exhaustive_epoch`: chạy mọi candidate; dùng cho correctness/reference.
- `canonical_frontier`: chạy theo wave nhưng chỉ dừng một pair khi đã có witness và mọi candidate có canonical rank nhỏ hơn witness đã được giải quyết.

Không được hủy một query có rank thấp hơn witness hiện tại, vì điều đó có thể đổi canonical sepset và orientation downstream.

`speculative_work` gồm mọi query đã chạy nhưng reference canonical-frontier có thể tránh. Metric này bắt buộc.

### 9.4 Budget semantics

Nếu budget hết giữa epoch:

- không commit deletion chưa qua barrier;
- giữ provisional witnesses trong `DiscoveryState`;
- lưu pending candidates và canonical frontier;
- resume cùng epoch digest;
- prior không được biến provisional fact thành final graph mutation.

### 9.5 Tests

- mọi permutation schedule cho cùng deletion set;
- mọi permutation completion order cho cùng chosen sepset;
- scalar và batch epoch equality;
- interrupted/resumed bằng uninterrupted run;
- collider-opening union regression;
- budget before/after witness;
- duplicate query suppression;
- candidate-family digest drift detection;
- no mutation before barrier.

### 9.6 Gate G2

`G2_STABLE_EPOCH_SOUND = PASS` khi exhaustive small candidate tables cho:

- deletion equality 100%;
- selected witnessed-sepset equality 100%;
- graph-event provenance đầy đủ;
- replay/resume equality 100%;
- prior permutation không đổi completed epoch state;
- budgeted output luôn là incomplete `DiscoveryState`.

## 10. WP4 — Graph algebra reference primitives (D3–D4)

WP4 không nằm trên authoritative path của MVP ban đầu. Nó tạo checker và candidate acceleration primitives.

### 10.1 Ordered-edge lift cho PDS walk

`path_algebra.py` xây:

- adjacency channel `A`;
- endpoint channels `H`, `T`, `C` theo convention đã khóa;
- triple predicate `Theta[u,v,w]`;
- ordered-edge state index `(u,v)`;
- transition relation `B[(u,v),(v,w)]`;
- reachability theo max path length và avoid mask.

Ba output riêng:

1. `walk_reachable`;
2. `simple_path_reference` bằng DFS/enumeration nhỏ;
3. `conservative_envelope`, chỉ dùng làm candidate superset.

Không dùng `walk_reachable` trực tiếp làm orientation witness.

### 10.2 ICD-Sep predicate

Checker phải đánh giá trên induced subgraph `G[{x} union S]`, tránh `y`, với path length/radius đúng và optional possible-ancestor flag. Global graph distance không đủ.

Local implementation được so với:

- `enumerate_icd_sep_candidates` hiện có;
- official ICD adapter;
- brute-force simple path checker trên graph nhỏ.

### 10.3 D4/R4 predicate

Triển khai độc lập hai phía:

- `reference_discriminating_paths`: enumeration từ rule semantics;
- `algebraic_r4_witnesses`: closure `K_y*` theo D4.

Output không chỉ là boolean; phải giữ `(x, q, ..., a, b, y)` hoặc certificate đủ để biết `a-b` và `b-y` cần xử lý.

### 10.4 Property/exhaustive tests

- endpoint-channel round trip;
- walk lift bằng direct walk enumeration;
- every simple PDS path nằm trong walk envelope;
- counterexample nơi walk không phải simple path;
- ICD-Sep induced-subgraph restriction;
- avoid endpoint mask;
- D4 hai chiều trên mọi small PAG snapshot hợp lệ trong generator range;
- shortest `K_y` path tạo simple discriminating path;
- trường hợp `q=a`;
- circle tại `b-y`, nonadjacency `x-y`, parent-of-y guards;
- exact oriented endpoint set equality với reference R4.

### 10.5 Gate G2-R

- D3 được công nhận là exact cho walk, không đổi nhãn thành path.
- Conservative envelope không có false negative so với simple-path reference trong exhaustive range.
- D4 có zero witness/output mismatch trong range đăng ký.
- Nếu D4 fail, lưu minimal graph và giữ reference R4; không chặn core MVP.

## 11. WP5 — Certified ICD round (D6)

### 11.1 Một radius là unit khoa học

`run_certified_icd_round(snapshot, radius, ci, backend, policy)`:

1. kiểm snapshot là `r-1`-representing theo metadata/reference chain;
2. sinh đủ ICD-Sep candidate sets kích thước `r`;
3. freeze epoch;
4. thực thi stable epoch;
5. commit witnessed deletions;
6. gọi authoritative anytime-FCI orientation closure;
7. trả `r`-representing candidate state cùng certificate;
8. so canonical output với official dynamic/reference mode.

### 11.2 Coverage certificate

Trong oracle small-graph test, certificate có thể kiểm trực tiếp:

- mọi pair cần xóa ở radius `r` có ít nhất một executed witness;
- mọi edge bị xóa có CI oracle witness;
- conditioning set đúng cardinality và ICD-Sep eligibility;
- không bỏ witness vì prior;
- orientation chỉ chạy sau barrier.

Trong production không biết ground truth, certificate chỉ xác nhận candidate/execution completeness theo algorithm contract; không giả vờ biết mọi true separator.

### 11.3 Orientation boundary

MVP gọi official/reference orientation ở cuối mỗi radius. Local causal-learn full FCI closure không được tự coi là anytime-ICD orientation reference. Adapter phải ghi:

- implementation/revision;
- input snapshot digest;
- rules enabled;
- output digest;
- endpoint changes;
- failure/unsupported status.

Nếu official adapter không chạy được, round được đánh dấu `REFERENCE_UNAVAILABLE`, không tự hạ chuẩn equality.

### 11.4 Tests

- all current motifs;
- random oracle graphs range nhỏ;
- dynamic vs frozen final-round equality;
- radius-by-radius skeleton/endpoint equality;
- valid witness equality;
- regression seed `74304` giữ expected trace difference nhưng final output equality;
- interruption chỉ ở epoch boundary và safe mid-epoch state;
- final full-radius PAG equality.

### 11.5 Gate G3

`G3_ICD_ROUND_EQUIVALENT = PASS` khi:

- zero false deletion;
- zero wrong determined endpoint;
- canonical round output equality trong exhaustive range;
- full final PAG equality với official ICD/reference;
- coverage certificate complete;
- mọi mismatch có minimized artifact.

G3 fail thì không được xây block executor; quay lại candidate/orientation semantics.

## 12. WP6 — Executable dependency certificate (D7)

Đây là work package quyết định novelty.

### 12.1 Event granularity

Thử theo thứ tự từ bảo thủ tới chi tiết:

1. `pair-event`: toàn bộ candidate tests và deletion decision cho một pair trong radius;
2. `region-event`: nhóm pair chia sẻ induced PDS region;
3. `query-wave-event`: chỉ nếu pair granularity tạo giant block quá thường xuyên.

Không bắt đầu bằng từng scalar rule application vì dependency graph sẽ quá lớn và khó audit.

### 12.2 Semantic footprint

Với pair-event, read footprint tối thiểu gồm:

- adjacency/endpoint facts dùng để sinh PDS paths;
- nonadjacency facts dùng cho collider/triangle;
- induced nodes/edges của mọi candidate path;
- sepset facts orientation sẽ đọc;
- possible-ancestor facts nếu filter bật;
- radius/phase barrier;
- candidate family digest.

Write footprint gồm:

- target adjacency deletion;
- sepset record;
- graph predicates có thể đổi sau deletion;
- orientation events có thể được mở ở barrier.

### 12.3 Certificate levels

| Level | Điều kiện | Vai trò |
|---|---|---|
| L0 | mọi event cùng một block | fallback correctness |
| L1 | disjoint semantic read/write footprints | sufficient certificate đầu tiên |
| L2 | path-context-aware noninterference | giảm false dependencies |
| L3 | critical-pair joinability | nghiên cứu sau khi L1/L2 đứng vững |

MVP chỉ cần L1 đúng và computable. L2 được thêm nếu L1 collapse.

### 12.4 Dependency graph

Cạnh dependency được tạo nếu:

- `W_e` giao `R_f` hoặc `W_f`;
- hai event cùng ghi một graph/sepset fact;
- deletion của một event có thể đổi path/nonadjacency predicate của event kia;
- orientation consequences có thể giao nhau trước next barrier;
- checker không quyết định được.

Connected components tạo block ở L1. Nếu direction/ordering được chứng minh, có thể tạo dependency DAG; không gán hướng tùy tiện chỉ để tăng ready width.

### 12.5 Certificate checker

Checker có hai mode:

- `static_conservative`: chỉ từ frozen snapshot/footprints;
- `exhaustive_semantic`: graph nhỏ, thử cả hai event orders để kiểm static certificate.

Mọi pair được static checker gọi là independent phải commute trong exhaustive semantic checker. Một false-independent là `KILL_CERTIFICATE` cho version đó.

### 12.6 Counterexample suite

- diamond separator;
- collider activation;
- latent confounder nối vùng;
- discriminating path qua hai region;
- deletion tạo unshielded triple;
- PDS path mất sau deletion;
- alternative sepsets đổi R0/R4;
- two events ghi cùng pair;
- same evidence/different mutation order;
- giant component;
- dynamic event opening;
- conflicting endpoint consequences.

### 12.7 Metrics

- certificate construction time/work;
- dependency edge count;
- block count;
- largest block weighted-cost fraction;
- ready width;
- critical path work;
- false-dependency proxy so exhaustive checker;
- false-independent count;
- giant-component rate;
- certificate bytes;
- update/rebuild cost mỗi radius.

### 12.8 Gate G4-A — Correctness

`G4A_BLOCK_CERTIFIED = PASS` khi:

- zero false-independent trong exhaustive registered range;
- every interleaving of certified independent blocks cho cùng completed-round state;
- one-block fallback bằng reference;
- certificate digest/provenance đầy đủ;
- critical-pair failure tự động thành regression fixture.

Một false definite endpoint hoặc false deletion là lỗi kill, không phải performance noise.

### 12.9 Gate G4-B — Structural headroom

Sau correctness, đo trên oracle mechanism grid:

- `GO`: median largest-block weighted-cost fraction `<= 0.70` ở ít nhất hai graph families quan trọng và ready width `>=2`;
- `RESTRICTED_GO`: chỉ một class graph mô tả được đạt điều kiện;
- `KILL_HEADROOM`: trên hơn 70% graph mục tiêu, một block giữ trên 80% weighted work hoặc certificate overhead xóa gain.

Threshold có thể kế thừa research contract hiện tại; thay đổi phải diễn ra trước khi xem benchmark chính.

## 13. WP7 — Block executor và scheduling

### 13.1 Deterministic executor trước

`BlockExecutor` ban đầu chạy serial theo topological/canonical block order. Mục tiêu là chứng minh block plan không đổi result trước khi thêm concurrency.

Sau serial equality:

- process pool hoặc thread pool cho CPU tùy GIL/kernel;
- một writer/commit coordinator;
- worker chỉ trả evidence package, không mutate shared graph;
- merge theo canonical event order tại barrier;
- retry idempotent theo block ID;
- atomic block artifact.

### 13.2 Ready queue

Queue item chứa:

- block ID;
- prerequisites;
- estimated weighted work;
- memory estimate;
- priority score;
- snapshot/certificate digest;
- backend/batch plan.

Scheduler chỉ được order các block đang ready và hợp memory. Nó không được bỏ block trong completed/full-budget mode.

### 13.3 Safety Prior hook

```python
class BlockPriorityPolicy(Protocol):
    def rank(self, ready_blocks, public_state, prior_view) -> Sequence[str]: ...
```

`public_state` không chứa oracle future CI outcome. Oracle policy chỉ tồn tại trong upper-bound experiment và có nhãn riêng.

Baselines:

- canonical FIFO;
- smallest-work-first;
- largest-work-first;
- graph-locality;
- random-valid;
- oracle-value upper bound;
- synthetic-prior;
- LLM prior sau cùng.

### 13.4 Prefix semantics

Khi dừng giữa các block:

- completed evidence packages được lưu;
- graph chỉ phản ánh các barrier commit hợp lệ theo contract;
- pending dependencies được lưu;
- output là `(DiscoveryState, EvidenceCertificate)`;
- không chạy orientation dựa trên provisional/incomplete skeleton trừ khi anytime theorem cho đúng boundary đó.

### 13.5 Gate G5

- serial block executor bằng certified round;
- concurrent executor bằng serial block executor;
- retry/resume bằng uninterrupted;
- prior-free schedules cùng completed output;
- no shared mutable graph in workers;
- oracle block order cho mechanism headroom hoặc hướng bị hạ cấp.

## 14. WP8 — Work–span và resource instrumentation

### 14.1 Counters bắt buộc

Không chỉ đo query count. Mỗi run lưu:

```text
Q_k_dynamic, Q_k_executed, Q_k_speculative
sum (k+2)^3 cho CI work proxy
candidate-generation work
submatrix-gather work
path-predicate work
dependency-certificate work
orientation work/sweeps
merge/commit work
block W_j và D_j proxy
peak RSS, peak VRAM, transfer bytes
CPU time, wall time, GPU kernel time
```

### 14.2 Derived metrics

```text
eta_total = W_candidate / W_reference
eta_CI = weighted_CI_work_candidate / weighted_CI_work_reference
parallelism = W_candidate / D_candidate
net_work_saving = 1 - W_candidate / W_reference
net_wall_speedup = T_reference / T_candidate
certificate_fraction = W_dependency / W_candidate
speculation_fraction = W_speculative / W_candidate
```

### 14.3 Fair benchmark protocol

- cùng graph/data/CI table;
- warm-up tách riêng;
- CPU threads khóa và ghi lại;
- GPU synchronization trước timing;
- transfer time được tính trong end-to-end;
- compile/JIT time báo riêng và end-to-end cold/warm;
- median và distribution qua graph seed;
- paired analysis theo graph;
- không dùng query count thay wall-clock;
- không dùng wall-clock thay algorithmic work.

### 14.4 Gate G6

`GO_WORK_EFFICIENT` khi candidate đạt một trong hai:

1. giảm actual weighted work sau khi tính certificate; hoặc
2. `eta` đủ thấp để bounded parallelism tạo end-to-end gain ổn định, đồng thời memory trong budget.

Nếu chỉ tăng throughput bằng work inflation rất lớn, ghi là systems trade-off, không phải algorithmic optimization.

## 15. WP9 — GPU backend

GPU chỉ bắt đầu sau G1, G3, G4-A và profiling cho thấy CI/batchable kernel chiếm phần lớn runtime.

### 15.1 Dependency

Thêm optional extra, không ép mọi user cài CUDA:

```toml
[project.optional-dependencies]
gpu = ["torch>=<pinned-compatible-version>"]
```

Version thật phải pin theo CUDA matrix của môi trường benchmark, không để placeholder khi merge.

### 15.2 Backend contract

`TorchGaussianBatchCI` thực hiện cùng `BatchCI` contract:

- float64 là correctness mode;
- float32/mixed precision chỉ là performance mode có gate riêng;
- exact-size bucket trước;
- bounded VRAM planner;
- async transfer chỉ sau deterministic baseline;
- explicit synchronization cho timing;
- device OOM trả structured failure và giảm batch size, không mất run.

### 15.3 CPU–GPU equivalence

So:

- rho/statistic/p-value;
- decision margin;
- undefined/singular behavior;
- witnessed sepset;
- completed epoch graph;
- final PAG;
- provenance logical content, bỏ qua wall-clock/order vật lý.

### 15.4 GPU gate G7

`G7_GPU_BACKEND = PASS` khi:

- decision equality ngoài numeric margin;
- zero final-output mismatch;
- VRAM planner không vượt budget;
- end-to-end gain so optimized batch CPU, không chỉ scalar Python;
- transfer/compile/speculative costs được báo;
- có crossover curve theo batch size, `k`, `P`, `n`;
- fallback CPU không đổi semantics.

GPU fail performance không giết Blockwise ICD; chỉ loại GPU khỏi claim.

## 16. WP10 — Safety Prior và LLM integration

### 16.1 Trình tự prior

1. no prior;
2. random score;
3. cheap graph heuristic;
4. synthetic calibrated prior;
5. correlated-error prior;
6. expert metadata/tier prior;
7. LLM prior.

Không đi thẳng tới LLM vì sẽ không biết gain đến từ mechanism hay prompt.

### 16.2 Prior được phép dự đoán

- block expected value;
- probability block chứa early deletion witness;
- expected work/memory;
- likely useful wave;
- abstention/uncertainty;
- source/group ID để mô hình correlated error.

Prior không trả một `CIResult` và không tạo `SeparationWitness`.

### 16.3 Full-budget invariant

Với mọi prior permutation:

- same eligible candidate universe;
- same completed blocks;
- same witnessed evidence set theo contract;
- same canonical final PAG;
- khác biệt chỉ ở trajectory/cost.

### 16.4 Budgeted evaluation

Primary curves:

- invariant endpoint gain theo weighted work;
- skeleton/PAG quality theo budget;
- completed certificates theo budget;
- time-to-fixed-target;
- regret so oracle block policy;
- failure conditional on prior error group.

### 16.5 Gate G8-Prior

- heuristic/prior policy phải vượt random-valid trên paired graphs;
- synthetic prior gain tồn tại dưới correlated errors;
- wrong prior không tạo wrong evidence;
- uninformative prior suy biến về prior-free policy;
- LLM chỉ được giữ nếu cost-adjusted gain vượt heuristic rẻ.

## 17. WP11 — Finite-sample consistency và robustness

Chỉ bắt đầu sau oracle correctness.

### 17.1 Statistical universe

Mỗi algorithm/config phải định nghĩa universe `U_n` hoặc một deterministic upper envelope để phân tích uniform CI error. Không dùng số realized adaptive queries thay thế mà không có proof.

### 17.2 Regimes

- linear Gaussian, no selection;
- varying `n/P`;
- conditioning order gần DF limit;
- weak partial correlations;
- near-singular covariance;
- latent ratios và degree grid;
- prior independent errors;
- source/node/motif correlated errors.

Selection bias chỉ được thêm khi data-generating/statistical test assumptions rõ; không dùng Fisher-Z cho arbitrary selected distribution.

### 17.3 Comparisons

- dynamic sample ICD/FCI;
- frozen stable version;
- block executor;
- scalar CPU;
- batch CPU;
- GPU;
- no-prior/heuristic/prior policies.

Phân biệt:

- cùng CI table nhưng khác schedule;
- cùng sample nhưng candidate universe khác;
- numerical backend difference;
- statistical sampling difference.

### 17.4 Gate G9

- finite-sample output differences được giải thích theo stable/dynamic semantics;
- no evidence leak;
- safety metrics không xấu đi ngoài margin đăng ký;
- cost-quality gain có confidence interval paired;
- K2/K3/K4 chỉ được cập nhật bằng evaluator/report chính thức.

## 18. Track-R4 và Track-Closure

### 18.1 Track-R4

D4 được coi là một lemma candidate độc lập. Deliverables:

- formal convention test cho endpoint indices;
- brute-force discriminating-path enumerator;
- algebraic closure implementation;
- exhaustive PAG/motif equivalence;
- complexity/work comparison;
- proof document cập nhật nếu counterexample xuất hiện.

Nếu pass và nhanh hơn reference, có thể thay R4 witness generation. Nếu chỉ đúng nhưng chậm, giữ làm checker.

### 18.2 Track-Closure D8

Không áp Tarski trực tiếp lên raw circle guards. Track này phải xây:

- immutable evidence facts;
- durable certificate premises;
- conflict representation khác bidirected edge;
- monotone/inflationary operators;
- fair closure schedule;
- projection từ fact closure sang PAG;
- equivalence với R0–R10.

Gate nghiên cứu:

- termination;
- soundness;
- confluence;
- completeness/equivalence trong scope;
- work không tệ hơn reference một cách vô dụng.

Nếu toàn bộ điều kiện trên đạt, decision record của track dùng nhãn `GC-CLOSURE`; không dùng chung số gate với `G8-Prior`.

Track này có thể thành paper/đóng góp riêng; không chặn MVP.

## 19. CLI đề xuất

```text
kill-test tensor-ci-audit
kill-test epoch-audit
kill-test icd-round-audit
kill-test block-plan
kill-test block-run
kill-test block-status
kill-test workspan-report
kill-test gpu-ci-audit
kill-test algorithm-report
```

Mọi command cần:

- `--config`;
- `--artifact-root`;
- `--resume` khi thích hợp;
- `--reference-mode`;
- `--backend`;
- deterministic seed;
- dry-run/preflight;
- structured exit status.

`block-run` không tự bật GPU hoặc LLM chỉ vì dependency có sẵn; config phải cho phép rõ.

## 20. Artifact layout

```text
artifacts/tensorized_icd/<contract_version>/<experiment_id>/
├── manifest.json
├── logical_inventory.parquet
├── runs.parquet
├── epochs.parquet
├── blocks.parquet
├── queries.parquet
├── witnesses.parquet
├── certificates/
│   ├── dependency/
│   └── completeness/
├── traces/
│   ├── mismatches/
│   └── sampled_success/
├── failures/
└── environment/
```

### 20.1 Logical keys

```text
graph_id + data_seed + radius + method + backend + scheduler + config_digest
```

Query và block có subkeys riêng. Resume dựa trên logical key và content digest, không dựa vào file tồn tại đơn thuần.

### 20.2 Failure signature

```text
failure_type + reference_mode + radius + graph_digest
+ first_differing_pair/endpoint + certificate_version
```

First occurrence lưu full trace; repeats chỉ tăng count và link về representative artifact.

## 21. Test matrix

| Lớp | Nội dung | Khi chạy |
|---|---|---|
| Unit | CI formula, bucket, witness, footprint | mỗi commit |
| Property | permutation, batching, padding, resume | mỗi PR |
| Motif | chain/fork/collider/latent/diamond/R4 | mỗi PR |
| Exhaustive small | graph/order/interleaving equivalence | nightly/milestone |
| Reference optional | official ICD pinned | reference CI job |
| Numerical | singular, weak signal, dtype | milestone |
| Performance smoke | work/memory regression | mỗi PR có core change |
| Full mechanism | oracle graph grid | sau gate |
| GPU | CPU–GPU correctness/performance | GPU runner |

### 21.1 Test oracle hierarchy

1. mathematical scalar formula;
2. independent brute-force small checker;
3. official ICD pinned;
4. causal-learn FCI where scopes match;
5. candidate implementation.

Không để candidate và expected output gọi cùng một helper cho logic đang kiểm.

## 22. Gate DAG

```text
G0 correctness baseline
  -> G0.5 reference/artifact freeze
      -> G1 batch CPU equivalence
      -> G2 stable epoch soundness
          -> G3 certified ICD round equivalence
              -> G4A dependency correctness
                  -> G4B decomposition headroom
                      -> G5 block executor/scheduler
                          -> G6 work efficiency
                              -> G7 GPU backend
                              -> G8 prior/LLM
                                  -> G9 finite-sample robustness

Track-R4: G2-R chạy song song, không chặn trước khi nhập core
Track-Closure: research-only, nhập core qua gate riêng
```

Không bỏ qua gate bằng cách thêm hardware, LLM hoặc threshold tuning.

## 23. Sprint/commit plan

### Sprint C0 — Correctness repair, 2–4 ngày

Commits dự kiến:

1. `fix: make gaussian ci decisions explicit and auditable`
2. `fix: preserve witnessed separating sets without union`
3. `test: add numerical and collider-union regressions`

Exit: G0.

### Sprint C1 — Contracts và CPU batch, 4–7 ngày

1. schema 0.2.0;
2. `CIQuery`, extended result, witness types;
3. exact-size CPU batch;
4. bucketing/padding;
5. memory planner;
6. scalar–batch audit CLI.

Exit: G0.5 và G1.

### Sprint C2 — Stable epoch, 4–6 ngày

1. frozen snapshot/candidate digest;
2. exhaustive epoch;
3. canonical witness policy;
4. budget/resume;
5. canonical-frontier cancellation;
6. schedule property tests.

Exit: G2.

### Sprint C3 — Certified ICD round, 5–8 ngày

1. official orientation wrapper hardening;
2. radius state/certificate;
3. exhaustive round comparisons;
4. final PAG comparisons;
5. mismatch minimizer.

Exit: G3.

### Sprint C4 — Dependency theorem kill, 7–12 ngày

1. pair-event footprints;
2. L1 static checker;
3. exhaustive semantic checker;
4. counterexample suite;
5. block/giant-component report;
6. revise or kill decision.

Exit: G4-A, rồi G4-B hoặc `KILL_HEADROOM`.

### Sprint C5 — Executor và work–span, 5–8 ngày

1. serial executor;
2. concurrent workers;
3. commit coordinator;
4. instrumentation;
5. fair baselines;
6. oracle block-order upper bound.

Exit: G5/G6.

### Sprint C6 — GPU, 5–9 ngày

1. optional torch extra;
2. float64 exact-size backend;
3. VRAM planner;
4. CPU–GPU audit;
5. performance crossover;
6. optional lower precision study.

Exit: G7 hoặc quyết định CPU-only.

### Sprint C7 — Safety Prior, 5–8 ngày

1. priority-policy API;
2. no/random/heuristic/oracle;
3. synthetic/correlated prior;
4. LLM schema/abstention cuối cùng;
5. cost-quality curves.

Exit: G8.

### Sprint C8 — Finite sample và paper evidence, 7–12 ngày

1. statistical grid;
2. numerical margins;
3. K2/K3/K4 evaluator;
4. paired bootstrap;
5. figures/tables/limitations.

Exit: G9.

Ước lượng serial thô: 44–74 ngày nghiên cứu-kỹ thuật. Counterexample hoặc reference mismatch có thể làm C3/C4 dài hơn; không rút ngắn bằng cách bỏ exhaustive gate.

## 24. Phân công artifact cho mỗi sprint

Mỗi sprint phải bàn giao đủ:

- code;
- unit/property/reference tests;
- config cố định;
- artifact schema/version;
- một command tái chạy;
- report generated;
- decision `PASS | REVISE | KILL | DEFER`;
- known limitations;
- Git commit sạch đối với file trong scope.

Một notebook hoặc chat conclusion không được coi là deliverable chính.

## 25. Tiêu chí khoa học cuối cùng

### 25.1 Claim tối thiểu để paper đứng vững

1. Một certified decomposition của ICD epochs có sufficient conditions rõ.
2. Full-budget oracle equivalence với reference trong scope.
3. One-block safe degeneration.
4. Work–span/accounting tính cả dependency và speculative work.
5. Nontrivial graph class/regime nơi blocks nhỏ và có gain.
6. Prior chỉ đổi resource trajectory, không đổi evidence semantics.
7. GPU result nếu có được tách khỏi algorithmic result.

### 25.2 Kết quả âm vẫn có giá trị

- mọi sound dependency certificate collapse thành giant block trên class rộng;
- exact path algebra cần work/space quá lớn;
- speculative batching xóa gain do K1 dự báo;
- GPU chỉ nhanh ở batch không xuất hiện trong ICD thực;
- D4 factorization có counterexample;
- finite-sample stable semantics khác dynamic quá nhiều.

Kết quả âm phải đi kèm boundary/counterexample, không chỉ “benchmark không nhanh”.

### 25.3 Điều kiện kill main direction

Kill Certified Blockwise ICD như đóng góp chính nếu:

- không xây được executable certificate không có false independence;
- certificate đúng nhưng trên hơn 70% graph mục tiêu tạo block >80% work;
- overhead xây certificate/merge luôn vượt benefit;
- confluence chỉ đúng khi giả định làm thuật toán tương đương một block;
- gain chỉ là GPU batching đã có trong PC literature, không có latent/ICD novelty.

Khi kill, giữ lại batched CI backend như engineering asset và chuyển sang Robust Tier Envelope hoặc exact checker direction.

## 26. Definition of done toàn chương trình

Chương trình được coi là hoàn tất khi:

- G0–G6 pass;
- G7 có quyết định rõ `PASS` hoặc `CPU_ONLY`, không treo;
- G8/G9 có kết quả theo scope paper;
- mọi full-budget completed run có canonical PAG equality;
- mọi deletion/orientation có evidence/certificate provenance;
- resume/replay deterministic về logical result;
- báo cáo tách query saving, weighted work và wall-clock;
- counterexample suite được version-control;
- theorem assumptions khớp config benchmark;
- claim matrix ghi rõ oracle, finite-sample, CPU và GPU;
- handoff/reproduction command chạy được trên environment sạch.

## 27. Bước đầu tiên cần thực hiện

Không bắt đầu bằng CUDA hoặc block worker. Thứ tự ngay sau khi duyệt plan:

1. tạo branch/commit mốc;
2. viết failing tests cho sepset union và `GaussianCI`;
3. sửa WP0;
4. tái chạy toàn test suite và K0 regression;
5. đóng G0 bằng report;
6. sau đó mới tạo `CIQuery`/`BatchCI` và CPU batch audit.

Đây là đường ngắn nhất để biến khảo cứu D1–D8 thành một thuật toán có thể kiểm chứng mà không làm mất nguyên tắc Safety Prior.
