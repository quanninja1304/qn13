# 3. Kiến trúc repository và khả năng tái lập

## 3.1 Luồng tổng thể

Luồng thực nghiệm hiện tại có thể đọc như sau:

```text
config YAML
  -> graph/DAG generator
  -> latent projection / canonical PAG target
  -> CI oracle hoặc finite-sample CI
  -> candidate generator + scheduler
  -> discovery state / PAG result
  -> query log + graph event provenance
  -> per-run artifact
  -> analyzer + bootstrap
  -> gate report
```

Thiết kế quan trọng nhất là scheduler chỉ chọn thứ tự candidate; thao tác graph phải đi qua discovery engine và lưu provenance.

## 3.2 Bản đồ module

| Module | Trách nhiệm | Ý nghĩa khoa học |
|---|---|---|
| `src/safety_prior/graphs.py` | Sinh DAG, motif, latent setup, canonical graph/digest | Khóa experimental unit và ground truth |
| `src/safety_prior/ci.py` | Oracle CI và Gaussian finite-sample CI | Tách structural truth khỏi statistical error |
| `src/safety_prior/models.py` | Candidate, score, query record, discovery state, PAG result, prior view | Schema chung và honest partial state |
| `src/safety_prior/schedulers.py` | Stable, random, cost, graph, prior-guided, oracle | Control plane của thí nghiệm |
| `src/safety_prior/discovery.py` | Scheduled stable FAS và kết nối FCI orientation/PDS | Evidence plane chính; hiện scheduler can thiệp chủ yếu ở FAS |
| `src/safety_prior/provenance.py` | Query log và graph event | Audit prior không trở thành evidence |
| `src/safety_prior/priors.py` | Biểu diễn/sinh prior | Nơi mở rộng noise model và source correlation |
| `src/safety_prior/metrics.py` | Compute và graph metrics | So sánh cost-quality |
| `src/safety_prior/gates.py` | Logic K0–K4 | Định nghĩa quyết định có thể tái sinh |
| `src/safety_prior/runner.py` | Điều phối run | Gắn config, seed, artifact và failure handling |
| `src/safety_prior/phase1_execution.py` | Inventory, shard run, analyze Phase 1 | Chạy K1 có resume theo run |
| `src/safety_prior/phase1_parallel.py` | Queue theo graph, worker, atomic claim | Chạy song song và resume an toàn hơn |
| `src/safety_prior/delta_handoff.py` | Export/install/return/import delta | Bàn giao phần thiếu sang máy khác |
| `src/safety_prior/migration.py` | Đóng gói/kiểm tra migration | Theo dõi provenance khi đổi máy |
| `src/safety_prior/cli.py` | CLI entry points | Bề mặt vận hành chuẩn |

## 3.3 Các module Sprint 0

| Module | Trạng thái | Vai trò |
|---|---|---|
| `src/safety_prior/algorithms/icd_reference.py` | Reference primitive nội bộ | ICD-Sep/PDS path/possible-ancestor semantics |
| `src/safety_prior/algorithms/icd_official_adapter.py` | Adapter tùy chọn | Đối chiếu implementation ICD chính thức đã pin revision |
| `src/safety_prior/tiers/reference.py` | Candidate semantics | Tier ordering, restriction và robust envelope brute-force |
| `src/safety_prior/pilots/motifs.py` | Test fixture | Motif catalog nhỏ, có latent và counterexample-oriented |
| `src/safety_prior/pilots/equality.py` | Equality tooling | So sánh canonical output thay vì raw log order |
| `src/safety_prior/pilots/schemas.py` | Artifact schema | Khóa đầu ra pilot có thể audit |
| `src/safety_prior/pilots/audit_icd_reference.py` | Audit runner | So dynamic/precomputed/reference behavior |

## 3.4 Cấu hình

Các config chính nằm trong `configs/`:

- Phase 0: smoke và mechanical equivalence.
- Phase 1: oracle headroom, inventory 800 run.
- Phase 2: prior không hoàn hảo/correlated-error experiments theo thiết kế.
- Phase 3: finite-sample setting.
- `configs/algorithm_pilots/sprint0.yaml`: audit semantics và motif Sprint 0.

Trước khi dùng một config cho claim, cần kiểm tra:

1. seed grid có cố định không;
2. graph là experimental unit hay run là unit;
3. scheduler có dùng cùng graph/CI oracle không;
4. budget fraction được định nghĩa trên candidate universe nào;
5. target metric và bootstrap unit có bị leakage giữa scheduler không;
6. config hash/revision có được lưu trong artifact không.

## 3.5 CLI vận hành

Các command hiện có trong CLI gồm:

- `dry-run`, `smoke`;
- `phase0`;
- `phase1`, `phase1-preflight`, `phase1-shard`;
- `phase1-queue-prepare`, `phase1-graph-worker`, `phase1-queue-status`;
- `phase1-analyze`;
- delta `export`, `install`, `verify`, `return`, `import`;
- migration `prepare`, `validate`;
- `evaluate-gates`, `report`, `figures`.

Không nên sao chép command từ tài liệu cũ mà chưa xem `python -m safety_prior.cli --help` hoặc entry point hiện tại; tên option là một phần dễ drift nhất.

## 3.6 Artifact model

Phase 1 dùng các lớp artifact có mục đích khác nhau:

- `logical_inventory.parquet`: universe dự kiến, không phải bằng chứng run đã hoàn thành;
- `run_rows/*.json`: hàng kết quả hoàn thành, là nguồn đếm completion đáng tin cậy;
- query log: thứ tự và kết quả CI;
- graph event: thao tác xóa/định hướng và provenance;
- graph artifact: dữ liệu dùng chung cho năm scheduler trên một graph;
- failure artifact: lỗi được ghi thay vì làm mất dấu run;
- report tổng hợp: sản phẩm của analyzer, có thể stale nếu không tái sinh.

Nguyên tắc audit: không suy completion từ folder size hoặc số log chung; đếm `run_rows`, kiểm unique logical key và ghép đủ scheduler theo graph key.

## 3.7 Resume và concurrency

Có hai cơ chế chạy:

1. Shard runner: tiếp tục theo logical run, bỏ qua artifact hoàn thành hợp lệ.
2. Graph queue: claim graph atomically, một worker xử lý nhóm scheduler cho graph đó.

Graph-level queue phù hợp cho paired analysis vì giữ năm scheduler gần nhau và giảm partial pair. Resume không có nghĩa checkpoint giữa một CI run; nếu một run đang viết dở và chưa commit artifact atomically, run đó có thể phải chạy lại. Các run đã hoàn thành không nên bị lặp.

Khi chạy nhiều worker:

- worker count bị giới hạn bởi RAM và memory peak chứ không chỉ số core;
- tránh nested parallelism của BLAS bằng cách khóa thread count;
- cùng một queue root phải hỗ trợ atomic claim;
- không chạy shard runner và graph worker lên cùng logical key nếu không kiểm soát;
- kiểm tra disk headroom trước khi chạy vì raw output lớn.

## 3.8 Reproducibility checklist

Một handoff/run được coi là có thể tái lập khi lưu:

- Git commit và trạng thái dirty;
- Python version, OS, dependency freeze;
- config file và hash;
- code/config provenance trong artifact;
- seed;
- inventory và completed logical keys;
- machine information;
- start/end time;
- error logs;
- analyzer version;
- bootstrap seed và number of resamples;
- báo cáo generated sau cùng.

Các tài liệu vận hành liên quan: [migration](../docs/kill_test/vps_migration.md) và [Windows i9 delta handoff](../docs/kill_test/windows_i9_delta_handoff.md).

## 3.9 Ranh giới implementation hiện tại

Điểm phải ghi nhớ khi diễn giải benchmark:

- scheduler intervention hiện tập trung ở stable FAS skeleton;
- PDS/FCI downstream được sử dụng/ghi nhận nhưng chưa phải một fully scheduled end-to-end FCI;
- RFCI riêng chưa có;
- independent DAG-latent-to-MAG/PAG converter chưa hoàn chỉnh;
- một số reference semantics vẫn dựa vào upstream library;
- Phase 2/3 runner và hard-prior behavior còn nợ theo open issues.

Vì vậy bất kỳ paper claim nào cũng phải nói đúng pha được tối ưu, không dùng cụm “tăng tốc FCI toàn bộ” khi bằng chứng chỉ đến từ FAS scheduling.
