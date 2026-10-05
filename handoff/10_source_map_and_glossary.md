# 10. Bản đồ nguồn và glossary

## 10.1 Tài liệu nền

| Chủ đề | Nguồn trong repo |
|---|---|
| Proposal high-level | [01_safe_imperfect_priors_high_level_vi.md](../01_safe_imperfect_priors_high_level_vi.md) |
| Proposal chuyên sâu | [02_safe_imperfect_priors_chuyen_sau_vi.md](../02_safe_imperfect_priors_chuyen_sau_vi.md) |
| Kill-test proposal | [02a_safe_imperfect_priors_kill_test_vi.md](../02a_safe_imperfect_priors_kill_test_vi.md) |
| Problem restatement | [docs/kill_test/00_problem_restated.md](../docs/kill_test/00_problem_restated.md) |
| Repository audit | [docs/kill_test/01_repository_audit.md](../docs/kill_test/01_repository_audit.md) |
| Implementation plan | [docs/kill_test/02_implementation_plan.md](../docs/kill_test/02_implementation_plan.md) |
| Scientific contract | [docs/kill_test/03_scientific_contract.md](../docs/kill_test/03_scientific_contract.md) |
| Evaluator contract | [docs/kill_test/04_evaluator_contract.md](../docs/kill_test/04_evaluator_contract.md) |
| Open issues | [docs/kill_test/open_issues.md](../docs/kill_test/open_issues.md) |

## 10.2 Tài liệu nghiên cứu thuật toán

| Chủ đề | Nguồn trong repo |
|---|---|
| Portfolio 4 vòng | [latent_fci_optimization_directions_4rounds_vi.md](../docs/research/latent_fci_optimization_directions_4rounds_vi.md) |
| Hai research contracts và testbed | [block_icd_robust_tier_contracts_and_testbed_vi.md](../docs/research/block_icd_robust_tier_contracts_and_testbed_vi.md) |
| Sprint 0 semantics | [sprint0_reference_semantics_vi.md](../docs/research/sprint0_reference_semantics_vi.md) |
| OP-PDS minimal plan, hướng nghiên cứu trước đó | [op_pds_minimal_plan_vi.md](../docs/research/op_pds_minimal_plan_vi.md) |
| Khảo cứu đại số hóa FCI/ICD, D1–D8 và work–span | [11_formal_tensorization_fci_icd_survey_vi.md](11_formal_tensorization_fci_icd_survey_vi.md) |
| Implementation plan Certified Blockwise ICD | [12_certified_blockwise_icd_implementation_plan_vi.md](12_certified_blockwise_icd_implementation_plan_vi.md) |

OP-PDS được giữ như tài liệu suy nghĩ/baseline; không nên tự động nâng thành main contribution vì chỉ ordering đơn giản chưa đủ novelty.

## 10.3 Báo cáo và artifacts

| Nội dung | Đường dẫn |
|---|---|
| Gate status generated | [reports/kill_test/gate_status.json](../reports/kill_test/gate_status.json) |
| Oracle headroom generated report | [reports/kill_test/oracle_headroom.md](../reports/kill_test/oracle_headroom.md) |
| Kill-test reports | `reports/kill_test/` |
| Phase 1 artifacts | `artifacts/kill_test/phase1/` |
| Logical inventory | `artifacts/kill_test/phase1/logical_inventory.parquet` |
| Completed rows | `artifacts/kill_test/phase1/run_rows/` |
| Failures | `artifacts/kill_test/phase1/failures/` nếu được tạo |

Generated report là output, không phải source of truth duy nhất. Khi report và artifacts lệch thời điểm, cần kiểm provenance và tái sinh.

## 10.4 Vận hành và bàn giao máy

| Chủ đề | Nguồn |
|---|---|
| Migration | [vps_migration.md](../docs/kill_test/vps_migration.md) |
| Windows i9 delta handoff | [windows_i9_delta_handoff.md](../docs/kill_test/windows_i9_delta_handoff.md) |
| Environment manifest | `env/` |

## 10.5 Glossary

### CI test

Kiểm định độc lập có điều kiện, thường ký hiệu `X ⟂ Y | Z`. Đây là evidence source chính trong constraint-based causal discovery.

### DAG

Directed acyclic graph. Synthetic generator thường bắt đầu từ DAG gồm observed và latent nodes.

### MAG

Maximal ancestral graph, biểu diễn quan hệ giữa observed variables sau khi marginalize latent variables và có thể xét selection effects.

### PAG

Partial ancestral graph, biểu diễn một lớp tương đương MAG. Endpoint circle thể hiện ambiguity.

### FCI

Fast Causal Inference, thuật toán constraint-based cho setting có latent confounders/selection bias dưới các giả định thích hợp.

### RFCI

Really Fast Causal Inference, biến thể ưu tiên giảm chi phí với trade-off thông tin/orientation; hiện chưa là baseline hoàn chỉnh trong repo.

### ICD

Iterative Causal Discovery, tổ chức tìm kiếm theo các vòng/radius để có anytime behavior và xử lý conditioning sets tăng dần.

### PDS / Possible-D-SEP

Vùng candidate có thể chứa separating variables cần thiết trong FCI. Đây là nguồn combinatorial cost và cũng là nơi tier/envelope có thể tác động.

### Sepset

Conditioning set làm một cặp biến độc lập theo CI oracle/test. Sepset được dùng cho edge deletion và orientation logic.

### Scheduler

Control-plane policy chọn candidate query tiếp theo. Scheduler không được tự tạo CI result.

### Oracle scheduler

Policy dùng future/ground-truth information chỉ để ước lượng upper bound headroom; không phải deployable algorithm.

### Prior

Thông tin ngoài sample data: expert fact, metadata, tier/order, LLM output hoặc synthetic signal. Trong dự án này prior chỉ hướng dẫn compute.

### Provenance

Dấu vết giải thích query nào, kết quả nào và rule nào dẫn tới graph event. Provenance là cơ chế audit evidence separation.

### DiscoveryState

Đầu ra có nhãn của một quá trình chưa hoàn tất, gồm graph hiện tại, budget, pending work và provenance. Không đồng nghĩa final PAG.

### Canonical equality

So sánh output sau khi chuẩn hóa representation/node/endpoint order, tránh mismatch giả do serialization hoặc execution order.

### `tests_to_95`

Số CI tests cần để đạt 95% quality target theo evaluator contract của K1.

### Headroom

Khoảng cải thiện tối đa có thể khai thác so với baseline trong setting oracle; không phải gain của policy thực tế.

### Blockwise ICD

Hướng nghiên cứu phân rã event/candidate dependency thành block để xử lý riêng hoặc bất đồng bộ với guarantee equivalence/confluence.

### Tier knowledge

Knowledge về thứ tự/lớp thời gian hoặc causal precedence giữa variables. Hard tier có thể nguy hiểm nếu sai.

### Robust envelope

Union candidate region qua một uncertainty set của tier assignments, nhằm giữ coverage khi prior có thể sai.

### `Gamma`

Budget/độ lớn uncertainty quanh tier prior. `Gamma` tăng phải làm envelope không co; đủ lớn phải fallback về baseline.

### Falsification

Thiết kế test nhằm chủ động tìm điều kiện làm claim sai, thay vì chỉ benchmark trên trường hợp thuận lợi.

### K0–K4

- K0: mechanical safety/equivalence.
- K1: oracle headroom.
- K2: lợi ích với prior không hoàn hảo.
- K3: độ bền với correlated errors.
- K4: finite-sample safety/usefulness.

## 10.6 Điểm bắt đầu cho người nhận code

1. Đọc [README handoff](README.md).
2. Chạy `git status --short` và ghi commit.
3. Đọc `src/safety_prior/cli.py` để biết command surface hiện tại.
4. Đọc `models.py`, `provenance.py`, `discovery.py` trước khi sửa scheduler.
5. Đọc research contract trước khi implement prototype.
6. Chạy test core và optional reference audit nếu dependency sẵn có.
7. Mọi mismatch phải thành artifact/test, không chỉ comment.

## 10.7 Nguyên tắc đọc lịch sử repo

Các commit quan trọng được ghi nhận trong lịch sử gần đây:

- `1beeea2`: khởi tạo kill-test repository và migration tooling;
- `6a7a8b5`: Git-backed migration provenance;
- `f5eb799`: three-worker Phase 1 delta handoff;
- `30f50f8`: research contracts cho latent discovery;
- `1185b05`: Sprint 0 reference semantics.

Hash trên là mốc lịch sử, không đảm bảo HEAD hiện tại vẫn đúng hash đó. Luôn dùng `git log` và `git show` để xác minh nội dung.
