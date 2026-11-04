# Sprint C1 — Reference contracts và CPU Batch CI

**Trạng thái:** `PASS`

**Gate:** `G0.5_REFERENCE_AND_ARTIFACT_CONTRACT = PASS`, `G1_BATCH_CI_EQUIVALENT = PASS`

**Phạm vi:** WP1–WP2 trong `12_certified_blockwise_icd_implementation_plan_vi.md`.

## 1. Kết quả

Sprint C1 tạo nền tính toán CPU có thể audit cho các sprint Blockwise ICD tiếp theo. Sprint này không triển khai block decomposition, concurrent executor hoặc GPU và không đưa ra claim speedup.

Các deliverable chính:

1. reference contract và artifact schema `0.2.0`;
2. `CIQuery` canonical, immutable;
3. `GaussianBatchCI` NumPy/CPU/float64;
4. exact-size batching;
5. identity padding theo power-of-two;
6. shared-conditioning-set Schur path;
7. bounded-memory microbatch planner;
8. scalar–batch audit CLI;
9. reference ICD audit CLI có structured blocked result khi dependency vắng;
10. unit, randomized và discovery-integration tests.

## 2. Reference contract

Config `configs/tensorized_icd/reference_contract.yaml` khóa bốn mode:

| Mode | Nghĩa |
|---|---|
| `dynamic_reference` | Candidate và graph state cập nhật theo official dynamic algorithm |
| `frozen_epoch_reference` | Candidate family đóng băng tại epoch barrier |
| `block_candidate` | Frozen epoch cộng dependency-certified block execution |
| `tensor_backend` | Không đổi algorithm, chỉ đổi numerical backend |

Mọi audit mới phải ghi `reference_id`, `reference_mode` và `equality_target`. Việc final PAG giống nhau không còn được diễn giải nhầm thành query-trace equality.

Authoritative references hiện được ghi rõ:

- FCI: `causal-learn==0.1.4.8`;
- ICD: `causality-lab@36625da6eeef059e36dab2b4467235a036136b76`;
- scalar finite-sample CI: `GaussianCI.scalar.strict`.

## 3. Artifact schema 0.2.0

Schema mới yêu cầu đầy đủ:

- graph/data/prior/scheduler seeds;
- Git revision, config digest và dependency lock;
- reference ID/mode/equality target;
- backend/device/dtype/regularization mode;
- radius và epoch ID;
- candidate/executed/skipped/witness counts;
- block count/largest block/ready width;
- dependency, CI, graph và speculative-work counters;
- RSS/VRAM;
- equality fields;
- terminal status và failure signature.

Validator từ chối:

- thiếu field;
- contract version sai;
- reference mode hoặc equality target không biết;
- counter âm;
- completed run không account đủ candidate;
- witness count lớn hơn executed count;
- failed run không có failure signature;
- logical key bị giả mạo;
- hai run cùng canonical logical key.

Canonical logical key không dựa vào `run_id`; vì vậy đổi tên attempt không thể tạo một scientific run trùng lặp khi resume.

## 4. CIQuery contract

`CIQuery` chứa:

```text
query_id, x, y, conditioning_set,
phase, epoch_id, pair_order, canonical_rank
```

Constructor:

- canonicalize endpoint pair;
- sort conditioning set;
- từ chối duplicate;
- từ chối endpoint trong conditioning set;
- từ chối phase/epoch rỗng hoặc rank âm.

Backend tiếp tục kiểm tra column bounds vì bound phụ thuộc dataset.

## 5. GaussianBatchCI

### 5.1 Preprocessing

Backend nhận data một lần và tính correlation matrix toàn cục một lần. Mỗi query gather local matrix theo thứ tự:

```text
[x, y, *canonical_conditioning_set]
```

Fisher-Z vẫn dùng kích thước conditioning set thật:

```text
df = n - |S| - 3
independent iff p > alpha
```

### 5.2 Exact-size strategy

Query được nhóm theo `d = |S| + 2`. Mỗi wave tạo tensor `(B,d,d)` và giải đồng thời hai right-hand sides để lấy các phần tử precision cần thiết. Implementation không tạo full inverse trong strict/ridge path.

### 5.3 Power-of-two strategy

Local matrix được identity-pad đến:

```text
D = 2^ceil(log2(d))
```

Padding không tham gia degrees of freedom. Rank/singularity được kiểm tra trên local matrix chưa pad để padding không thay đổi numerical status.

### 5.4 Explicit numerical modes

Batch backend giữ ba mode của scalar backend:

- `strict`;
- `ridge(lambda)`;
- diagnostic `pinv`.

Insufficient DF, singular, nonfinite correlation, invalid precision và invalid partial correlation vẫn trả undefined thay vì bị đổi thành dependent.

### 5.5 Shared-S path

Khi bật `shared_s_min_reuse`, nhiều pair có cùng conditioning set dùng chung phép giải trên `C_SS`. Backend ghi:

- `shared_factorization_count`;
- `shared_work_saved_estimate`.

Shared-S mặc định không bật trong authoritative scalar–batch audit. Nó có regression riêng so với per-query batch backend và không được dùng cho claim speedup ở C1.

## 6. Memory planner

Planner dùng local/padded matrix size, dtype, safety factor và configured budget để tính:

```text
batch_capacity = floor(memory_budget / estimated_bytes_per_query)
waves = ceil(query_count / batch_capacity)
```

Nó tính matrix gather, solve/factorization copies, RHS và result buffers. Nếu budget không chứa nổi một query, planner raise `MemoryError`; không âm thầm vượt budget.

Hai metric được tách:

- planned peak workspace dùng để enforce microbatch budget;
- observed process RSS để theo dõi runtime.

Đây chưa phải VRAM planner và chưa phải proof về mọi LAPACK allocator nội bộ.

## 7. Audit CLI

CPU batch audit:

```powershell
python -m safety_prior.cli batch-ci-audit `
  --strategy both `
  --queries 256 `
  --samples 512 `
  --variables 12 `
  --memory-mb 64 `
  --output artifacts/tensorized_icd/c1_batch_audit.json
```

Official ICD audit:

```powershell
python -m safety_prior.cli icd-reference-audit `
  --seeds-per-cell 5 `
  --output artifacts/tensorized_icd/c1_icd_reference_audit.json
```

Nếu official dependency không import được, command thứ hai tạo structured result `BLOCKED_EXTERNAL_DEPENDENCY`, có reference ID/mode, thay vì stack trace không có ngữ nghĩa gate.

## 8. G0.5 evidence

Audit được chạy trong một venv mới với project editable, core dependencies kế thừa từ environment đã khóa và official source snapshot từ đúng commit trên `PYTHONPATH`.

| Check | Kết quả |
|---|---:|
| Graphs | 40 |
| Official dynamic ICD vs FCI final-PAG mismatch | 0 |
| Dynamic vs precomputed final-PAG mismatch | 0 |
| Dynamic vs precomputed trace mismatch | 10 |
| First trace mismatch seed | 74304 |
| Dynamic/precomputed queries tại seed đó | 21 / 25 |

Direct `pip install -e ".[reference]"` bị treo ở Git transport trên máy này. Audit dùng source ZIP URL của exact commit; source semantics không bị sửa. Đây là transport limitation cần ghi lại, không phải conformance failure.

## 9. G1 evidence

Authoritative audit dùng 256 mixed-order queries cho mỗi strategy.

| Metric | Exact-size | Power-of-two | Tolerance |
|---|---:|---:|---:|
| Decision mismatch ngoài margin | 0 | 0 | 0 |
| Decision mismatch trong margin | 0 | 0 | ghi nhận, không che |
| Numerical-status mismatch | 0 | 0 | 0 |
| Max rho/effect error | 7.63e-17 | 7.63e-17 | 1e-11 |
| Max statistic error | 1.89e-15 | 1.89e-15 | 1e-10 |
| Max p-value error | 8.88e-16 | 8.88e-16 | 1e-11 |
| Planned peak workspace | 75,480 B | 244,800 B | <= 64 MiB |

Additional verification:

- randomized equivalence grid: 8 seeds × 24 queries × 2 strategies;
- batch composition/permutation invariance;
- batch size 1 và empty batch;
- strict/ridge/pinv parity;
- singular, near-singular và insufficient-DF parity;
- shared-S versus per-query;
- memory budget/wave splitting;
- discovery integration giữ candidate trace, evidence query IDs và final output;
- full suite với official reference enabled: `103 passed`.
- default suite không có optional reference: `88 passed, 15 skipped`.

## 10. Claim boundary

Sprint C1 chỉ cho phép claim:

> Trong testbed và tolerance đã đăng ký, CPU batch backend giữ scalar Gaussian CI semantics và không đổi discovery output trong integration suite hiện tại.

Sprint C1 chưa chứng minh:

- frozen epoch tương đương dynamic ICD;
- block decomposition sound;
- parallel execution confluent;
- CPU batch nhanh hơn scalar trong workload ICD thật;
- GPU equivalence hoặc speedup.

## 11. Bước tiếp theo

Sprint C2/WP3 phải xây frozen stable epoch:

1. snapshot và candidate-family digest;
2. canonical rank trước scheduling;
3. exhaustive epoch và canonical-frontier modes;
4. atomic barrier commit;
5. budget/resume state;
6. schedule/completion-order property tests;
7. Gate `G2_STABLE_EPOCH_SOUND`.
