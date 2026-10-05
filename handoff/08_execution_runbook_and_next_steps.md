# 8. Runbook và các bước tiếp theo

## 8.1 Hai luồng công việc độc lập

Từ thời điểm bàn giao, nên chạy song song về mặt quản lý nhưng không trộn artifact:

### Luồng A — đóng hồ sơ K1

Hoàn tất shard 5 và 7, nhập delta, phân tích lại đủ 800 run và sinh report chính thức.

### Luồng B — nghiên cứu thuật toán

Hoàn tất Sprint 0 reference semantics, sau đó prototype/falsify Blockwise ICD và Fallible-Tier Robust Envelope.

Không cần trì hoãn Luồng B chỉ vì K1 còn nợ 144 run, nhưng nếu full K1 đảo kết luận thì phải mở lại quyết định portfolio.

## 8.2 Checklist trước mọi lần chạy

Trong PowerShell tại repo root:

```powershell
git status --short
git rev-parse HEAD
python --version
python -m safety_prior.cli --help
```

Kiểm tài nguyên:

```powershell
$os = Get-CimInstance Win32_OperatingSystem
[pscustomobject]@{
    FreeRAMGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    TotalRAMGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    FreeRAMPercent = [math]::Round(100 * $os.FreePhysicalMemory / $os.TotalVisibleMemorySize, 1)
}
Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors
```

Các command thực thi cụ thể phải lấy từ `--help` của revision hiện tại. Không hard-code option theo tài liệu nếu CLI đã đổi.

## 8.3 Chính sách worker

Worker count được chọn theo memory peak quan sát:

```text
safe_workers = min(
    physical/logical concurrency target,
    floor((free_RAM - safety_margin) / peak_RAM_per_worker),
    disk-I/O practical limit
)
```

Với máy 16 GB đang dùng gần hết RAM, một worker có thể là lựa chọn đúng dù CPU có 20 logical processors. Muốn hai worker, trước hết phải đóng ứng dụng chiếm RAM và đo peak của một worker. Không suy worker count chỉ từ nhãn i9.

Khuyến nghị:

- để safety margin ít nhất 2–4 GB trên Windows;
- khóa `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS` nếu worker đã parallel ở process level;
- chạy pilot 1–2 graph để đo peak RSS;
- tránh oversubscription P-core/E-core;
- cắm nguồn, performance mode, kiểm thermal throttling;
- không đồng bộ cloud folder trực tiếp trong lúc ghi hàng chục GB artifacts.

## 8.4 Resume và dừng an toàn

- Ưu tiên Ctrl+C một lần để process xử lý interrupt.
- Chỉ kill process sau khi xác định đúng PID/command line.
- Artifact hoàn thành phải được ghi atomically; run chưa hoàn thành có thể chạy lại.
- Sau khi dừng, đếm run rows và queue state trước khi resume.
- Không xóa lock/claim file khi chưa xác nhận worker đã chết.
- Không chạy hai cơ chế runner lên cùng output root.

Kiểm Python process:

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Select-Object ProcessId, CreationDate, CommandLine
```

Nếu buộc phải dừng một PID đã xác nhận:

```powershell
Stop-Process -Id <PID>
```

Không dùng lệnh kill tất cả Python nếu máy có workload khác.

## 8.5 Đóng K1

### Trước khi chạy

1. Xác nhận commit/config khớp artifact gốc.
2. Verify delta input nếu chạy trên máy khác.
3. Kiểm disk: raw return có thể hàng chục GB.
4. Chạy preflight.
5. Ghi machine manifest.

### Trong khi chạy

Theo dõi:

- completed logical rows;
- failed rows;
- expected rows;
- completed graph pairs;
- worker PID/CPU/RSS;
- disk free;
- queue claimed/pending/stale.

### Sau khi chạy

1. Verify return package.
2. Import theo CLI, không copy chồng tùy tiện.
3. Kiểm uniqueness và hashes.
4. Xác nhận 800/800 và 160 complete graph pairs.
5. Chạy analyzer.
6. So kết quả full với snapshot 131 pairs.
7. Commit generated report/artifact manifest theo policy repo.

Tài liệu chi tiết: [Windows i9 delta handoff](../docs/kill_test/windows_i9_delta_handoff.md).

## 8.6 Kế hoạch hai sprint thuật toán đầu tiên

### Sprint 1A — Block dependency semantics

Deliverables:

- event/dependency schema;
- block constructor đơn giản;
- one-block fallback;
- exhaustive motif runner;
- dynamic/reference final-output equality;
- counterexample artifact schema;
- measurement của block size và giant-component rate.

Không tối ưu thread/GPU trong sprint này.

### Sprint 1B — Robust tier reference

Deliverables:

- formal uncertainty set với source groups;
- brute-force envelope oracle;
- simple restricted discovery wrapper;
- coverage tests trên motifs/exhaustive graph nhỏ;
- collapse/shrinkage curves theo `Gamma`;
- minimal counterexample khi hard tier sai.

### Gate cuối Sprint 1

Mỗi hướng nhận một trong ba quyết định:

- `GO`: theorem target và prototype còn đứng;
- `REVISE`: thu hẹp claim hoặc thay representation;
- `KILL`: không tiếp tục như main contribution.

## 8.7 Sprint 2 — Candidate algorithm

Chỉ cho hướng `GO/REVISE` có plan sửa rõ:

- efficient block update hoặc robust-envelope algorithm;
- property tests so với brute-force/reference;
- work counters;
- prior-free baseline;
- synthetic prior corruption;
- reproducible paired benchmark.

Mục tiêu là biết algorithm có giảm work, chưa phải tuning tối đa.

## 8.8 Sprint 3 — Robustness và finite sample

- đưa candidate qua Phase 2-style prior noise;
- independent và correlated errors;
- finite-sample CI;
- sample size/effect size grid;
- multiple sepset instability;
- calibration/abstention;
- K2/K3/K4 criteria được cập nhật trước khi xem kết quả chính.

Không tái sử dụng oracle prior như bằng chứng cho robustness.

## 8.9 Sprint 4 — Scale, GPU và paper evidence

- profile để tìm kernel thật sự chiếm thời gian;
- CPU vectorization trước;
- GPU batch CI/simulation nếu profile ủng hộ;
- báo cáo algorithmic vs hardware gain riêng;
- real/semi-synthetic validation;
- ablation hoàn chỉnh;
- theorem/proof/counterexample appendix;
- paper reviewer chỉ đánh giá sau khi evidence package ổn định.

## 8.10 Decision log tối thiểu

Mỗi thay đổi claim cần một record:

```text
Date:
Commit:
Question:
Evidence inspected:
Decision: GO | REVISE | KILL | DEFER
Claim retained:
Claim removed:
New falsifier:
Owner / next artifact:
```

Không để quyết định chỉ tồn tại trong chat.

## 8.11 Definition of handoff success

Người nhận mới phải có thể:

1. phát biểu đúng thesis trong hai phút;
2. phân biệt K1 project decision và stale generated report;
3. tìm code/config/artifact cho một run;
4. chạy test/reference audit;
5. resume K1 mà không lặp run hoàn thành;
6. giải thích vì sao hai hướng thuật toán có thể là novelty;
7. biết điều kiện kill từng hướng;
8. không dùng prior làm graph evidence;
9. không gọi partial state là PAG;
10. không gọi GPU speedup là algorithmic contribution.
