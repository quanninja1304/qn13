# 9. Rủi ro, ranh giới claim và quyết định

## 9.1 Sổ đăng ký rủi ro

| ID | Rủi ro | Mức | Dấu hiệu | Giảm thiểu |
|---|---|---|---|---|
| R1 | Prior leak vào evidence | Critical | graph event không có CI/rule provenance | invariant test và audit log |
| R2 | K1 selection bias do matrix thiếu | High | shard 5/7 khác distribution | hoàn tất 800, paired reanalysis |
| R3 | Scheduler scope bị nói quá | High | claim “FCI speedup” từ FAS-only intervention | ghi scope ở mọi table/abstract |
| R4 | Reference circularity | High | candidate và evaluator dùng cùng bug/library path | independent primitives/exact checker |
| R5 | Block dependency toàn cục | High | giant component gần 100% | đo sớm, thu hẹp graph class hoặc kill |
| R6 | Robust envelope collapse | High | `|J|/|PDS|≈1` ở Gamma plausible | group model/adaptive expansion hoặc đổi claim |
| R7 | Correlated error bị mô hình sai | High | chỉ flip fact độc lập | source/group corruption |
| R8 | Finite sample lấn át scheduling gain | High | query saving nhưng PAG quality giảm | joint cost-quality, safety margin |
| R9 | LLM không hơn heuristic | Medium-high | cost-adjusted gain ≤ graph/cost baseline | giữ LLM là optional prior source |
| R10 | GPU overhead | Medium | transfer/kernel launch vượt compute | profile và batch threshold |
| R11 | Non-deterministic artifacts | Medium | resume tạo duplicate/mismatch | atomic writes, logical key, hashes |
| R12 | Disk/RAM exhaustion | High vận hành | swap, truncated file, low free disk | preflight, worker cap, monitoring |
| R13 | Literature novelty collision | High | gần trùng tFCI/ICD/dcFCI | claim matrix và nearest-work audit |
| R14 | Optional reference tests bị bỏ qua lâu dài | Medium | CI xanh nhưng reference extra skip | scheduled full-reference job |

## 9.2 Open issues kế thừa

Theo [open issues](../docs/kill_test/open_issues.md), các điểm quan trọng gồm:

- RFCI chưa được triển khai như baseline riêng;
- chưa có converter DAG+latent sang MAG/PAG hoàn toàn độc lập;
- FCIT chưa được reproduce;
- scheduler mới can thiệp stable FAS, PDS mới chủ yếu được log;
- sepset union behavior từ causal-learn cần audit;
- Phase 3 safety margin scale chưa validate;
- hard-prior và Phase 2/3 runner chưa hoàn chỉnh;
- peak-memory reporting trong báo cáo cũ chưa nhất quán, dù run rows mới có thể đã chứa `peak_rss_bytes`;
- path portability và một số memory-copy issue đã được xử lý nhưng cần regression test.

Open-issue file có thể stale ở chi tiết; đóng issue chỉ khi code, test và report cùng khớp.

## 9.3 Claim ladder

Chỉ leo một bậc khi bậc dưới đã được chứng minh:

1. Scheduler implementation giữ mechanical invariants. `K0 PASS`.
2. Oracle scheduling có headroom. `K1 PASS` theo quyết định dự án.
3. Policy khả thi chiếm được headroom trên oracle-CI synthetic data.
4. Policy bền với imperfect/correlated prior.
5. Policy bền với finite-sample CI.
6. End-to-end wall-clock/memory tốt hơn baseline mạnh.
7. LLM prior tốt hơn heuristic với cost hợp lý.
8. Kết quả tổng quát trên real/semi-synthetic data.

Hiện dự án đứng chắc ở bậc 2; Sprint 0 chuẩn bị cho bậc 3.

## 9.4 Những câu được phép viết hiện tại

- “K0 pass trên 220 run mechanical-equivalence suite.”
- “K1 được dự án chấp nhận là pass trên 131 complete graph pairs; full matrix còn thiếu 144/800 run.”
- “Oracle median query saving so với stable default là khoảng 23.31% trong snapshot.”
- “Kết quả hỗ trợ tiếp tục nghiên cứu compute-allocation algorithms.”
- “Sprint 0 không thấy final-PAG mismatch trong audit 40 graph được báo cáo.”
- “Hai hướng đang được kiểm chứng là Blockwise ICD và Fallible-Tier Robust Envelope.”

## 9.5 Những câu chưa được phép viết

- “K1 chính thức pass trên toàn bộ 800 run.”
- “LLM cải thiện FCI 23%.”
- “Thuật toán đề xuất đã nhanh hơn FCI.”
- “Blockwise ICD đã được chứng minh tương đương.”
- “Robust envelope an toàn với mọi tier error.”
- “GPU giải quyết bottleneck causal discovery.”
- “K2/K3/K4 pass.”
- “Kết quả đã được validate trên dữ liệu thực.”

## 9.6 Quyết định đã khóa

| Quyết định | Trạng thái |
|---|---|
| Prior là control signal, không phải causal evidence | Khóa |
| Partial run trả DiscoveryState, không gọi là PAG hoàn chỉnh | Khóa |
| K1 được dùng là PASS cho roadmap hiện tại | Khóa, chờ full-matrix report |
| Không chờ K2/K3 để bắt đầu algorithm sprint | Khóa |
| Ưu tiên Blockwise ICD và Fallible-Tier Envelope | Khóa cho vòng falsification đầu |
| Tối đa bốn vòng nghiên cứu tổng thể | Khóa |
| GPU là optimization layer sau semantics/algorithm | Khóa |
| Paper-writing không phải ưu tiên trước kết quả nghiên cứu | Khóa theo định hướng hiện tại |

## 9.7 Quyết định còn mở

- Definition chính xác của block dependency.
- Class graph nơi decomposition hữu ích.
- Uncertainty set và group budget cho tier errors.
- Coverage target: mọi valid separator hay ít nhất một witness.
- Efficient representation của robust envelope.
- Policy dùng prior/LLM sau khi core algorithm đứng vững.
- Benchmark real/semi-synthetic nào phù hợp.
- Hardware/GPU backend sau profiling.
- Ngưỡng chính thức K2/K3/K4 sau khi runner hoàn chỉnh.

## 9.8 Threats to validity

### Internal validity

- paired runs chưa đủ toàn matrix;
- shared upstream code có thể tạo correlated implementation error;
- oracle definition có thể vô tình dùng future information quá mạnh;
- tests-to-95 phụ thuộc quality target/candidate trace implementation.

### Construct validity

- query count không đồng nhất với wall-clock;
- PAG metric có thể che endpoint error quan trọng;
- synthetic prior accuracy không đại diện lỗi LLM có cấu trúc;
- tier uncertainty budget có thể không phản ánh source correlation.

### External validity

- graph nhỏ và random generator khác network thực;
- latent fraction/degree grid còn hẹp;
- linear-Gaussian finite sample không bao phủ nonlinear/non-Gaussian;
- laptop hardware không đại diện server/GPU platform.

### Conclusion validity

- graph là unit; không được giả tăng n bằng nhiều scheduler/budget points;
- subgroup selection sau khi xem data tạo multiplicity;
- median effect cần confidence interval và distribution;
- completion pattern shard 5/7 cần kiểm missingness.

## 9.9 Nguyên tắc cập nhật tài liệu

Khi có evidence mới:

1. không sửa lịch sử bằng cách xóa trạng thái cũ;
2. ghi ngày, commit và artifact root;
3. cập nhật project decision nếu gate đổi;
4. tái sinh report bằng code thay vì sửa JSON/Markdown generated;
5. thêm counterexample vào regression suite;
6. thu hẹp claim nếu theorem assumption tăng;
7. liên kết decision record với code/test.
