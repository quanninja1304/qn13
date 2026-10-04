# Sprint 0 — Reference semantics freeze

**Ngày audit:** 2026-09-30
**Trạng thái:** đang thực hiện; ICD adapter và primitive semantics đã executable
**Mục tiêu:** khóa reference trước khi viết Blockwise ICD hoặc robust-envelope solver

## 1. Kết luận audit

Sprint 0 xác minh được hai primitive quan trọng nhưng chưa xác nhận một complete Blockwise ICD implementation.

1. ICD-Sep đã được chuyển thành một candidate enumerator độc lập.
2. Một optional adapter đã chạy được implementation ICD chính thức ở revision khóa.
3. Simple-tFCI adjacency và PDS restrictions đã được chuyển thành predicates độc lập.
4. Robust envelope brute-force qua một tập tierings tường minh đã có để làm oracle cho solver về sau.
5. Canonical PAG equality, motif catalog và artifact row schemas đã được đóng băng bước đầu.
6. Anytime-FCI orientation closure chưa được port vào local code, nhưng được gọi qua official adapter; local candidate enumerator tự nó vẫn không phải một reference ICD round hoàn chỉnh.

## 2. Reference ICD đã khóa

Primary sources:

- [NeurIPS 2021 paper](https://proceedings.neurips.cc/paper/2021/hash/144a3f71a03ab7c4f46f9656608efdb2-Abstract.html)
- [Official Intel Labs implementation](https://github.com/IntelLabs/causality-lab)
- Audited source revision: `36625da6eeef059e36dab2b4467235a036136b76`
- Reference class: `causal_discovery_algs.icd.LearnStructICD`

### 2.1. ICD-Sep semantics

Với ordered pair `(A,B)` và iteration/radius `r`, một conditioning set `Z` hợp lệ khi:

1. `|Z| = r`;
2. với mọi `z in Z`, tồn tại một PDS-path từ `A` tới `z`, không đi qua `B`;
3. path dài không quá `r` cạnh;
4. mọi node sau root trên witness path thuộc `Z`;
5. optional condition 3 của paper: `z` là possible ancestor của `A` hoặc `B`.

Candidates của unordered tested edge là union của predicates cho `(A,B)` và `(B,A)`, deduplicate theo conditioning set và sort theo tổng shortest PDS-path distance.

Executable primitive:

```python
from safety_prior.algorithms.icd_reference import enumerate_icd_sep_candidates
```

### 2.2. PDS-path semantics

Một simple path là PDS-path nếu với mọi interior triple `(U,V,W)`:

- `V` là definite collider; hoặc
- `U` và `W` adjacent, tạo triangle.

Implementation local dùng immutable `PAGSnapshot`; nó không phụ thuộc causal-learn hoặc Intel Labs code. Mục đích là tạo một oracle nhỏ có thể audit bằng mắt.

### 2.3. Possible-ancestor semantics

Một path từ `Vi` đến `Vi+1` có thể đi theo hướng ancestor nếu:

- không có arrowhead tại `Vi`;
- không có tail tại `Vi+1`.

Search tồn tại path thỏa predicate này được dùng cho optional ICD-Sep condition 3.

### 2.4. Phát hiện quan trọng về order semantics

Official implementation có hai mode:

- mặc định: candidate sets được tính từ **current PAG**, và edge deletion trước có thể ảnh hưởng query sau trong cùng iteration;
- optional `is_pre_calc_cond_set=True`: precompute candidates trước iteration.

Do đó “snapshot block round” không tự động tương đương reference ICD mặc định. Ta phải coi đây là một hypothesis cần test, không phải một refactor hiển nhiên.

Reference chính cho conformance được khóa là:

```text
dynamic_current_pag / is_pre_calc_cond_set=False
```

Snapshot/precalculated mode là comparator riêng. Nếu hai mode khác output hoặc evidence trên oracle small graphs, Blockwise ICD phải:

1. mô hình hóa dynamic candidate-generation dependency; hoặc
2. hạ claim xuống block-synchronous variant và chứng minh variant đó độc lập.

### 2.4.1. Kết quả random conformance đầu tiên

Pilot `40` graph, observed size `4..7`, latent ratio `0.0/0.3`, mean degree `2.0` cho kết quả:

| Check | Kết quả |
|---|---:|
| Official dynamic ICD khác upstream FCI final PAG | `0/40` |
| Dynamic khác precomputed final PAG | `0/40` |
| Dynamic khác precomputed query trace | `10/40` |

Phản ví dụ trace nhỏ nhất đã đóng băng:

- motif: `dynamic_snapshot_trace_gap`;
- 4 observed nodes, 2 latent nodes;
- generator seed gốc: `74304`;
- dynamic query counts theo round: `[6, 10, 5, 0]`;
- precomputed query counts: `[6, 10, 9, 0]`;
- final canonical PAG giống nhau.

Tại `r=2`, dynamic mode xóa edge `(1,2)` rồi không còn chạy bốn query tiếp theo mà snapshot mode đã precompute. Điều này bác bỏ giả định rằng snapshot chỉ đổi execution order nhưng giữ nguyên computation trace. Nó chưa bác bỏ final-output equivalence; câu hỏi đó cần exhaustive search.

### 2.5. Orientation semantics chưa hoàn tất

Official ICD:

- reset endpoint marks về circles sau skeleton refinement;
- orient v-structures;
- áp dụng R1–R4 trong nonterminal iterations;
- áp dụng R5–R7 và R8–R10 khi kết thúc, tùy selection-bias/tail-completeness flags.

Codebase hiện tại có causal-learn FCI closure, nhưng chưa có bằng chứng nó tái tạo đúng từng `r`-representing PAG của anytime-FCI. Vì vậy không được dùng FCI hoàn chỉnh để giả làm ICD iteration reference.

Optional adapter:

```python
from safety_prior.algorithms.icd_official_adapter import run_official_icd
```

Dependency được tách khỏi runtime K1:

```powershell
python -m pip install -e ".[reference]"
```

Adapter convert official PAG endpoint matrix về canonical convention hiện tại và expose từng iteration, `r`, `done`, sepsets và PAG state.

**S0-ICD-1 đã giải quyết ở mức adapter.** Conformance hiện đã qua trên năm base motifs. Phần còn lại là mở rộng sang random/exhaustive small graphs và các discriminating-path motifs trước khi khóa `PASS`.

## 3. Reference simple tFCI đã khóa

Primary source:

- [Bang & Didelez, tiered FCI/tIOD](https://arxiv.org/abs/2503.21526)
- Proposition 6: past restriction cho separating sets.
- Proposition 7: oracle simple tFCI sound và complete.

### 3.1. Tiering

Tiering là map:

\[
\tau:V\rightarrow\{1,\ldots,T\}.
\]

Past của một node:

\[
past^\tau_V(A)=\{Z:\tau(Z)\leq\tau(A)\}.
\]

Joint past:

\[
past^\tau_V(\{A,B\})=
\{Z:\tau(Z)\leq\max(\tau(A),\tau(B))\}.
\]

### 3.2. First-stage adjacency restriction

Với ordered pair `(Vi,Vj)`, simple tFCI chỉ xét subsets của:

\[
adj_G(V_i)\cap past^\tau_V(V_i)\setminus\{V_j\}.
\]

Executable primitive:

```python
from safety_prior.tiers import simple_tfci_adjacency_candidates
```

Phải gọi cho cả hai ordered directions nếu reference algorithm làm như vậy.

### 3.3. PDS restriction

Ở Possible-D-SEP stage, candidate pool là:

\[
pds_G(V_i,V_j)\cap past^\tau_V(\{V_i,V_j\})\setminus\{V_j\}.
\]

Executable primitive:

```python
from safety_prior.tiers import simple_tfci_pds_candidates
```

### 3.4. Không dùng tier orientation

Simple tFCI bỏ phần orient cross-tier edges của full tFCI. Đây là reference phù hợp với research contract vì mục tiêu vẫn là PAG của independence model và oracle output giống FCI.

Nếu dùng tier để orient, output target đổi thành graph có background knowledge và full tFCI chỉ được chứng minh sound, không nhất thiết complete. Hướng hiện tại không làm việc này.

### 3.5. Robust envelope oracle

Với explicit feasible tierings `T`, brute-force reference là:

\[
R(X,Y)=\bigcup_{\tau\in T}
\left(PDS(X,Y)\cap past^\tau(\{X,Y\})\right).
\]

Executable primitive:

```python
from safety_prior.tiers import robust_pds_envelope
```

Empty feasible set raise error thay vì trả empty envelope. Caller bắt buộc fallback full PDS.

**Blocker S0-TIER-1:** code hiện mới khóa candidate-pool semantics; chưa wrap toàn simple-tFCI pipeline để chứng minh exact canonical PAG equality với FCI.

## 4. Canonical equality đã khóa

So sánh phải báo riêng:

1. node order/equality;
2. skeleton equality;
3. endpoint-matrix equality;
4. exact canonical PAG equality;
5. sepset validity qua CI oracle.

Không yêu cầu exact sepset identity vì hai minimal separating sets khác nhau có thể đều hợp lệ. Tuy nhiên nếu sepset khác làm endpoint output khác, endpoint mismatch vẫn là failure.

Executable helper:

```python
from safety_prior.pilots.equality import compare_canonical_pags
```

## 5. Motif catalog đã khóa

Catalog ban đầu:

- chain;
- fork;
- collider;
- latent confounder;
- latent mediator;
- diamond;
- future-confounder-claim failure;
- latent diamond.
- dynamic-snapshot trace gap.

Executable catalog:

```python
from safety_prior.pilots import common_motif_catalog
```

Mỗi motif là full DAG với observed/latent mask, purpose và optional expected failure. Các motif discriminating-path/PDS-dominant đầy đủ sẽ được thêm khi official orientation adapter tồn tại, vì expected PAG trace phải đến từ reference độc lập.

## 6. Artifact schema đã khóa bước đầu

Config:

```text
configs/algorithm_pilots/sprint0.yaml
```

Run schemas:

```python
from safety_prior.pilots.schemas import validate_run_record
```

Nguyên tắc storage:

- successful runs lưu digest/aggregate;
- full trace chỉ cho mismatch, false endpoint, solver discrepancy, first failure signature và audit sample;
- graph/data/prior/scheduler seeds tách riêng;
- reference ID và config/git digest bắt buộc.

## 7. Tests hiện có

Các test Sprint 0 kiểm tra:

- ICD radius 0 và 1;
- PDS triangle và definite-collider extension;
- ICD-Sep condition 2b;
- possible-ancestor endpoint semantics;
- tier past/joint past;
- first-stage và PDS simple-tFCI restrictions;
- robust union và empty-set fallback;
- motif DAG validity;
- canonical skeleton/endpoint distinction;
- artifact required fields.

Khi optional pinned reference có mặt, test bổ sung kiểm tra:

- local ICD-Sep candidates khớp official candidates tại radius `0,1,2`;
- official ICD final PAG khớp upstream FCI trên chain, fork, collider, latent confounder và latent mediator;
- dynamic và precomputed official modes khớp trên năm base motifs.

## 8. Gate còn lại để kết thúc Sprint 0

Sprint 0 chỉ `PASS` khi:

1. official ICD adapter chạy được ở pinned revision — **đã qua smoke/conformance motifs**;
2. local ICD-Sep enumerator khớp official enumerator trên motif/random small PAG snapshots — **đã qua một stress snapshot, còn random/exhaustive**;
3. dynamic và precomputed ICD modes được so sánh, mismatch được ghi lại — **đã có trace mismatch ở 10/40 random graphs; chưa thấy output mismatch**;
4. full ICD iteration canonical output được conformance-test — **0/40 final mismatch với FCI, còn exhaustive/discriminating-path**;
5. simple-tFCI wrapper khớp FCI oracle trên small graphs với correct tiering;
6. các expected traces được thêm vào motif catalog;
7. toàn bộ repository tests pass.

Cho đến khi đạt bảy mục này:

- Blockwise ICD status: `REFERENCE_PARTIAL`;
- Fallible-tier status: `CANDIDATE_SEMANTICS_FROZEN`;
- không chạy headroom benchmark;
- không dùng LLM/GPU.

## 9. Bước thực thi tiếp theo

Ưu tiên tiếp theo là mở rộng conformance cho ICD official, chưa phải block scheduler:

1. chạy random/exhaustive conformance giữa official ICD và upstream FCI;
2. exhaustive search tìm graph nhỏ nhất nơi dynamic và precomputed modes khác final output; trace mismatch đã được đóng băng;
3. bổ sung discriminating-path/PDS-dominant motifs;
4. chỉ khi conformance pass mới xây block dependency graph.

Song song ở tier branch:

1. wrap causal-learn FCI candidate stages;
2. chèn exact simple-tFCI pool filters;
3. verify correct-tier oracle output bằng FCI;
4. sau đó mới thêm grouped claims và `Gamma`.
