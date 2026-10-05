# 4. Kill test và kết luận K1 PASS

## 4.1 Vì sao cần kill test

Trước khi xây một hệ thống LLM phức tạp, dự án hỏi câu đơn giản hơn: nếu có một oracle biết truy vấn nào sẽ giúp graph tiến gần output cuối nhanh nhất, oracle có tiết kiệm đủ CI tests để đáng nghiên cứu không?

Nếu câu trả lời là không, mọi scheduler dựa trên LLM — vốn kém oracle và còn tốn chi phí — gần như không có cơ sở. Kill test vì thế là một falsification gate, không phải benchmark để tô đẹp kết quả.

Thiết kế gốc: [02a](../02a_safe_imperfect_priors_kill_test_vi.md), [scientific contract](../docs/kill_test/03_scientific_contract.md), [evaluator contract](../docs/kill_test/04_evaluator_contract.md).

## 4.2 K0 — mechanical safety

K0 kiểm tra rằng thay scheduler không làm thay đổi semantics khi chạy full budget:

- cùng candidate universe;
- query chỉ được chạy khi eligible;
- dependency được tôn trọng;
- prior không tạo graph evidence;
- replay deterministic;
- canonical output khớp reference.

Kết quả lưu trong repo:

| Chỉ báo | Kết quả |
|---|---:|
| Run Phase 0 | 220/220 |
| Exact canonical equivalence | 1.0 |
| Failure | 0 |
| Quyết định | `PASS` |

220 run tương ứng 20 graph, mỗi graph có một stable schedule và mười random schedules. K0 cho phép đi tới câu hỏi headroom nhưng không tự chứng minh scientific benefit.

## 4.3 Thiết kế K1

### Grid

| Trục | Giá trị |
|---|---|
| Số observed nodes | 10, 20 |
| Latent fraction | 0.2, 0.4 |
| Mean degree | 2, 4 |
| Seed/cell | 20 |
| Tổng graph | 160 |
| Scheduler/graph | 5 |
| Tổng logical run | 800 |
| Budget fractions | 0.10, 0.25, 0.50, 1.00 |

### Scheduler

- `stable_default`: baseline deterministic.
- `random_valid`: random order trong tập candidate hợp lệ.
- `cost_only`: ưu tiên theo ước lượng chi phí.
- `graph_only`: dùng trạng thái graph nhưng không có oracle.
- `oracle_query`: upper bound biết giá trị của query.

### Metric chính

`tests_to_95` là số CI tests cần để đạt 95% chất lượng đích theo contract. So sánh phải paired theo graph; graph, không phải scheduler-run đơn lẻ, là đơn vị bootstrap.

Saving cho graph `g` so với baseline `b`:

```text
saving_g = (tests_to_95(b, g) - tests_to_95(oracle, g))
           / tests_to_95(b, g)
```

Statistic chính là median của `saving_g` và percentile bootstrap confidence interval trên graph pairs.

### Ngưỡng đăng ký

K1 pass nếu:

1. median saving so với `stable_default` ≥ 20%;
2. cận dưới bootstrap 95% CI > 10%;
3. hiệu ứng không chỉ ở một pocket: ít nhất ba nhóm cấu hình đạt tiêu chuẩn nhóm.

## 4.4 Snapshot bằng chứng hiện có

Inventory và artifact trực tiếp cho thấy:

| Shard | Completed run rows | Expected |
|---:|---:|---:|
| 0 | 100 | 100 |
| 1 | 100 | 100 |
| 2 | 100 | 100 |
| 3 | 100 | 100 |
| 4 | 100 | 100 |
| 5 | 30 | 100 |
| 6 | 100 | 100 |
| 7 | 26 | 100 |
| **Tổng** | **656** | **800** |

Theo scheduler:

| Scheduler | Run rows |
|---|---:|
| `stable_default` | 132 |
| `random_valid` | 131 |
| `cost_only` | 131 |
| `graph_only` | 131 |
| `oracle_query` | 131 |

Có 131 graph pair hoàn chỉnh với đủ năm scheduler, tương đương 655 run; một graph còn lại có một scheduler row. Không có failure artifact được phát hiện trong snapshot.

## 4.5 Kết quả trên 131 graph pair hoàn chỉnh

Bootstrap dùng 10.000 resample và seed 51001, theo utility hiện có của repo.

| So sánh oracle với | Median saving | Bootstrap 95% CI |
|---|---:|---:|
| `stable_default` | 23.31% | [20.24%, 27.70%] |
| `random_valid` | 22.23% | [17.96%, 24.95%] |
| `cost_only` | 24.04% | [20.08%, 27.23%] |
| `graph_only` | 28.55% | [23.64%, 33.11%] |

Median `tests_to_95`:

| Scheduler | Median tests-to-95 |
|---|---:|
| `oracle_query` | 411 |
| `stable_default` | 607 |
| `random_valid` | 616 |
| `cost_only` | 623 |
| `graph_only` | 691 |

Phân nhóm cho so sánh oracle với stable default:

| Observed nodes | Latent fraction | Graph pairs | Median saving | Bootstrap 95% CI (xấp xỉ) |
|---:|---:|---:|---:|---:|
| 10 | 0.2 | 40 | 21.59% | [15.03%, 34.86%] |
| 10 | 0.4 | 40 | 21.25% | [12.54%, 29.58%] |
| 20 | 0.2 | 26 | 25.72% | [18.74%, 30.14%] |
| 20 | 0.4 | 25 | 24.34% | [19.59%, 43.13%] |

Cả bốn nhóm đều có median trên 20% và cận dưới trên 10% trong snapshot hoàn chỉnh.

## 4.6 Quyết định

> **K1 = PASS theo quyết định dự án hiện hành.**

Lý do: trên toàn bộ 131 graph pair hoàn chỉnh hiện có, point estimate vượt ngưỡng chính, lower confidence bound vượt safety margin, và hiệu ứng tái hiện ở 4/4 nhóm cấu hình.

Quyết định này cho phép bắt đầu phát triển thuật toán mà không cần chờ đóng toàn bộ matrix. Nó không xóa nghĩa vụ hoàn tất matrix để có báo cáo cuối cùng.

## 4.7 Vì sao report cũ vẫn ghi NOT_RUN

[Gate status sinh tự động](../reports/kill_test/gate_status.json) và [oracle headroom report](../reports/kill_test/oracle_headroom.md) được thiết kế bảo thủ: chúng không ra quyết định chính thức khi full matrix chưa đủ 800 run. Vì artifacts hiện mới có 656 run và analyzer chưa được chạy lại sau khi đóng matrix, report đó ghi `NOT_RUN`/blocked.

Hai phát biểu sau đồng thời đúng:

- dự án đã chấp nhận K1 `PASS` dựa trên evidence snapshot hoàn chỉnh theo pair;
- pipeline report chưa chứng nhận full-matrix K1 vì còn thiếu 144 run.

Người nhận không được sửa report JSON bằng tay để làm nó khớp quyết định. Cách đúng là hoàn tất run và tái sinh report.

## 4.8 Giới hạn diễn giải

K1 chỉ thiết lập **oracle headroom** trong phạm vi implementation hiện tại. Nó không chứng minh:

- một LLM scheduler có thể đạt headroom đó;
- gain tồn tại dưới finite-sample CI noise;
- prior sai tương quan là an toàn;
- wall-clock giảm đúng bằng query saving;
- toàn bộ Possible-D-SEP/FCI pipeline đã được scheduler tối ưu;
- GPU sẽ tạo gain khoa học;
- kết quả tổng quát ra dataset thực.

Đặc biệt, kill test hiện có scope `FAS_STABLE_SKELETON_ONLY`: thứ tự query ở stable FAS được can thiệp; downstream PDS có provenance nhưng chưa phải đối tượng reorder đầy đủ.

## 4.9 Việc còn lại để đóng hồ sơ K1

1. Hoàn tất 144 logical run còn thiếu, chủ yếu shard 5 và 7.
2. Xác nhận 160 graph đều đủ năm scheduler.
3. Kiểm tra duplicate logical key, truncated JSON, failure artifact và config hash.
4. Chạy `phase1-analyze` bằng code revision đã khóa.
5. Tái sinh gate report và figures.
6. So snapshot 131 graph với full 160 graph; giải thích nếu effect thay đổi đáng kể.
7. Lưu machine/environment manifest và bootstrap seed.

## 4.10 Ý nghĩa đối với roadmap

K1 trả lời “có khoảng trống để tối ưu không?” bằng câu trả lời có. Bước tiếp theo phải trả lời “một thuật toán khả thi có chiếm được khoảng trống đó với guarantee rõ ràng không?”. Vì thế trọng tâm chuyển từ chạy thêm baseline sang research contracts của Blockwise ICD và Fallible-Tier Robust Envelope, trong khi completion của K1 được xử lý như một luồng tái lập song song.
