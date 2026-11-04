# Lịch sử chuyển dịch nghiên cứu (Research pivot log)

> **Đọc file này trước khi đề xuất bất kỳ hướng mới nào.** Mục đích là tránh làm lại những gì đã bị bác bỏ, đã có prior art hoặc đã bị gác lại có lý do.
> Cập nhật lần cuối: **2026-11-04**. Quy tắc bảo trì ở §6: **append-only**. Không sửa phán quyết cũ; nếu đảo quyết định thì thêm một mục mới tham chiếu mục cũ.
> Mọi tài liệu gốc vẫn còn nguyên trong repo. Các hướng cũ nằm ở [`archive/`](archive/README.md), hướng hiện tại ở [`reports/`](reports/README.md) và [`research/`](research/README.md).

## 0. Cách đọc nhãn trạng thái

| Nhãn | Nghĩa | Được mở lại khi nào |
|---|---|---|
| **REFUTED** | Bị bác bỏ bằng bằng chứng: chứng minh, phản ví dụ, hoặc thí nghiệm đã chạy | Chỉ khi có bằng chứng mới mâu thuẫn trực tiếp với bằng chứng cũ |
| **SUBSUMED** | Đã có prior art làm điều tương đương; novelty không đủ | Chỉ khi chỉ ra được một khác biệt kỹ thuật cụ thể so với nguồn đã ghi |
| **DEPRIORITIZED** | Gác lại vì ưu tiên/chi phí/rủi ro. **Không** bị bác bỏ | Khi hướng hiện tại thất bại và có lý do mới |
| **PAUSED** | Hạ tầng/kết quả còn giá trị, công việc dừng giữa chừng | Khi một hướng mới cần đúng hạ tầng đó |
| **ACTIVE** | Đang theo đuổi | — |

Nhãn chỉ phản ánh **quyết định của dự án tại thời điểm ghi**, kèm bằng chứng. Nhãn REFUTED/SUBSUMED cho một *framing cụ thể* không có nghĩa toàn bộ chủ đề rộng là vô giá trị.

---

## 1. Dòng thời gian tổng quát

| # | Thời gian | Giai đoạn | Câu hỏi trung tâm | Kết cục | Tài liệu chính |
|---|---|---|---|---|---|
| P0 | 18–21/09/2026 | Đề cương **Safe Imperfect Priors** | Prior (chuyên gia/LLM) có thể sai, có được dùng chỉ để lập lịch CI query trong FCI có biến ẩn, mà không thành bằng chứng? | Thiết kế kill test K0–K4 (chốt 19/09) | [`archive/2026-09_safe_imperfect_priors/proposal/`](archive/2026-09_safe_imperfect_priors/proposal/) |
| P1 | 21/09–21/10 | **Kill test K0–K4** | K0 tương đương cơ học; K1 oracle headroom; K2 prior khả dụng; K3 lỗi tương quan; K4 hữu hạn mẫu | K0 **PASS** (220/220). K1 **PASS theo quyết định dự án** trong phạm vi FAS-stable (snapshot 675/800 run, 133 graph, median saving 23,60%, bootstrap CI [20,24%; 27,74%]); formal gate **chưa đóng**. K2–K4 **NOT_RUN** | [checkpoint 19/10](archive/2026-09_safe_imperfect_priors/reports/research_checkpoint_2026-10-19_vi.md), [dossier 21/10](archive/2026-09_safe_imperfect_priors/reports/research_project_dossier_2026-10-21_vi.md), `reports/kill_test/` |
| P1b | 30/09–05/10 | **Portfolio tối ưu thuật toán** sau 4 vòng tranh luận literature | Đóng góp nào vượt "đổi thứ tự kiểm định"? | OP-PDS **SUBSUMED** làm đóng góp chính; chọn Blockwise ICD + Fallible-Tier làm ưu tiên | [portfolio](archive/2026-09_safe_imperfect_priors/research_notes/latent_fci_optimization_directions_4rounds_vi.md), [OP-PDS](archive/2026-09_safe_imperfect_priors/research_notes/op_pds_minimal_plan_vi.md) |
| P2 | 04/10–06/10 | **Certified Blockwise ICD**: Sprint 0, C0, C1, C2 (C2 commit vào Git 04/11) | Xây executor đúng semantics (reference contracts, batch CI, frozen epoch) | Gate G0/G0.5/G1/G2 **PASS** về correctness. **PAUSED**: hạ tầng, chưa phải đóng góp khoa học | [`archive/…/handoff/`](archive/2026-09_safe_imperfect_priors/handoff/README.md), `src/`, `reports/algorithm_sprints/` |
| P3 | 30/10 | **Literature/gap review** sau K1 | Hướng "LLM prior cho discovery" còn gap không? | Ý tưởng rộng đã có prior art gần; GPU loại khỏi phạm vi; 3 ứng viên A (feedback loop), B (calibration consensus→disputed), C (sinh candidate dcFCI) | [review 30/10](archive/2026-10_dcfci_direction_c/literature_gap_review_2026-10-30_vi.md) |
| P4 | 03/11 | **Hướng C: dcFCI pruning** + đánh giá phê bình | Backtracking với pruning T1–T3 có đóng góp không? | T1–T3 **SUBSUMED** (kiến thức nền + CSP); đề xuất D1–D4; khuyến nghị reframe tối đa 4–6 tuần | [đặc tả C](archive/2026-10_dcfci_direction_c/dcfci_pruning_formulation_and_profiling_2026-11-03_vi.md), [đánh giá C](archive/2026-10_dcfci_direction_c/direction_c_critical_reassessment_2026-11-03_vi.md) |
| P5 | 03/11 | **Research reset** + reassessment A–J | Định vị lại: problem-driven methodology; không neo vào dcFCI/D1–D4 | D1–D4 và dcFCI pruning **DEPRIORITIZED** (không khôi phục vì sunk cost). Chọn **A′** (primary, conditional), **T4** (backup); C-S thứ ba; B′ hạ cấp | [`AGENTS.md`](AGENTS.md), [`research/`](research/README.md), [reassessment](reports/reassessment_2026-11-03_vi/00_final_reassessment_vi.md) |
| P6 | 04/11 | **Review độc lập A′** (3 phase) | A′ có đúng toán, có nghĩa thống kê, có mới không? | Framing gốc **REFUTED/STOP**. Reformulation R1/R2 **ACTIVE (REFORMULATE)**. RG0 PASS; gate tiếp theo RG1/RG2 | [`reports/aprime_review_2026-11-04/`](reports/aprime_review_2026-11-04/A1_review_handoff.md) |

---

## 2. Từng lần chuyển dịch: vì sao rời đi, học được gì

### P0 → P1/P1b: từ "prior an toàn" sang "đóng góp thuật toán nào?"
- **Giữ lại:** nguyên tắc tách *evidence plane* (chỉ dữ liệu và luật hợp lệ đổi graph) với *control plane* (prior chỉ lập lịch). K0 xác nhận nguyên tắc này đúng trong testbed cơ học.
- **Vì sao không dừng ở đó:** K1 chỉ chứng minh **có headroom khi biết oracle**, trong phạm vi FAS-stable. Nó không chứng minh prior thực tế thu được headroom (K2), không chịu lỗi tương quan (K3), cũng không an toàn hữu hạn mẫu (K4). Ba gate này **chưa bao giờ chạy**.
- **Không được claim:** "FCI nhanh hơn 23,6%", "LLM thu hồi headroom", "an toàn finite-sample".

### P1b: OP-PDS và "đổi thứ tự kiểm định" bị loại làm đóng góp chính
- **Lý do (SUBSUMED):** Guess2Graph đổi thứ tự edge/conditioning set theo expert trong PC; Anytime FCI và ICD có kết quả trung gian sound; lFCI có local separator pools; FCIT có targeted CI tests.
- FREW, Hedge, pair-wave, learned router, GPU/batching bị loại khỏi phần *khoa học* (GPU chỉ còn là engineering).

### P2 → P3: hạ tầng ICD đúng nhưng không tự thành đóng góp
- C0/C1/C2 cho executor có contract và audit (G2: 64 truth table × ≥ 256 lịch, 0 mismatch). Review 30/10 kết luận đây là **hạ tầng có giá trị, chưa phải scientific contribution**. Frozen stable epoch không tự động tương đương mọi lịch dynamic ICD.
- **Trạng thái code:** vẫn ở `src/`, test pass. **PAUSED**, không xóa.

### P3 → P4: từ LLM-prior sang dcFCI thuần thuật toán
- Review 30/10 chỉ ra: "dùng LLM ưu tiên tìm kiếm", "xử lý prior sai", "LLM + discovery có biến ẩn" đều đã có công trình gần (Guess2Graph, L2D-CD, Causal Ensemble Agent…).
- Câu hỏi của người hướng dẫn về "độ tự nhiên" của hướng cũ được ghi nhận là **có cơ sở**: cần đổi claim/cơ chế, không chỉ đổi tên.
- Ứng viên A (feedback loop) và B (calibration transfer) **chưa từng được kiểm tra**. Chúng được **DEPRIORITIZED** khi reset P5 đổi phạm vi khỏi LLM-prior, **không** bị bác bỏ.

### P4 → P5: dcFCI pruning không đủ, reset định vị
- T1–T3 là hệ quả của lý thuyết ancestral graph/m-separation đã biết. Đưa vào backtracking là mô hình CSP quen thuộc → **SUBSUMED**.
- Chưa có profiling cho thấy bottleneck nằm ở sinh candidate.
- D1–D4 được đề xuất nhưng reset P5 quyết định **không** coi chúng là hướng bắt buộc (`research/02-context-and-scope.md`). D1–D4 vì vậy là **DEPRIORITIZED**, chưa bị bác bỏ bằng thí nghiệm.

### P5 → P6: A′ bị review độc lập bác bỏ framing gốc
- A′ gốc: thay loss cộng tính của ACI bằng khoảng cách Mahalanobis trên vector Fisher-z, với claim chính H-cal ("ACI trôi calibration, D(f) thì không").
- Review 04/11 cho thấy (chi tiết và số liệu ở [`A1_review_handoff.md`](reports/aprime_review_2026-11-04/A1_review_handoff.md)):
  1. Σ của Fisher-z Gaussian **suy biến cấu trúc** (rank ≤ p(p−1)/2). Các query "gần trùng", vốn là động lực của A′, có tương quan tiệm cận **= 1**. Quy ước pseudo-inverse gán +∞ cho mô hình đúng.
  2. Score D dạng hiệu **không calibrated**: ở toy, D_full trôi FAR như diag (0.110 so với 0.105).
  3. Metric Δ_FAR pre-register **phạt chính phương pháp đúng** (0.871 so với 0.509 ở K = 8).
  4. "Evidence dependence-aware" chính là thống kê của một **query ngoài Q** (corr −0.9998).
  5. Phần "off-diagonal" là GLS/minimum-distance cổ điển (Browne 1984).
- **Còn sống:** R1 (chứng nhận đồng thời ancestral feature bằng projection, ngưỡng χ²_rank; valid pointwise) và R2 (η-profile). Novelty hẹp: bước projection là lập luận của Wang–Kolar–Drton (JASA 2026) Lemma 3.

---

## 3. Sổ đăng ký "KHÔNG LÀM LẠI" (do-not-redo registry)

| # | Ý tưởng / framing | Nhãn | Lý do ngắn | Bằng chứng | Điều kiện mở lại |
|---|---|---|---|---|---|
| X1 | Prior/LLM sắp lại thứ tự CI query (full ranking) như đóng góp chính | SUBSUMED | Guess2Graph, Anytime FCI/ICD, lFCI, FCIT | [portfolio §1](archive/2026-09_safe_imperfect_priors/research_notes/latent_fci_optimization_directions_4rounds_vi.md) | Khác biệt kỹ thuật cụ thể so với 4 nguồn trên |
| X2 | OP-PDS (one-probe Possible-D-SEP) làm phương pháp cuối | SUBSUMED / DEPRIORITIZED | Chỉ là falsification screen; không đủ novelty | [OP-PDS](archive/2026-09_safe_imperfect_priors/research_notes/op_pds_minimal_plan_vi.md) | Không đề xuất |
| X3 | FREW / Hedge / pair-wave / learned router / GPU như novelty | SUBSUMED | Trộn nhiều cơ chế; GPU là engineering | [OP-PDS §1](archive/2026-09_safe_imperfect_priors/research_notes/op_pds_minimal_plan_vi.md) | Không |
| X4 | Claim "FCI nhanh hơn ~23%" từ K1 | REFUTED (như claim) | K1 chỉ đo oracle, FAS-stable, 675/800 run | [checkpoint](archive/2026-09_safe_imperfect_priors/reports/research_checkpoint_2026-10-19_vi.md) | Chạy đủ K1 + K2–K4 |
| X5 | "LLM + discovery có biến ẩn", "học khi nào tin LLM" như gap | SUBSUMED | L2D-CD, Causal Ensemble Agent và các công trình khác | [review 30/10](archive/2026-10_dcfci_direction_c/literature_gap_review_2026-10-30_vi.md) | Cơ chế cụ thể chưa có |
| X6 | dcFCI pruning T1–T3 như định lý mới | SUBSUMED | Kiến thức nền + CSP | [đánh giá C, Report A–B](archive/2026-10_dcfci_direction_c/direction_c_critical_reassessment_2026-11-03_vi.md) | Profiling cho thấy bottleneck và có lemma mới thật |
| X7 | D1–D4 (extendibility, distinct-MEC, search-budget uncertainty, restricted-CI equivalence) | DEPRIORITIZED | Reset 03/11: không khôi phục vì sunk cost | [`research/02`](research/02-context-and-scope.md) | Lý do khoa học mới, không phải "đã làm dở" |
| X8 | Multi-environment FCI; joint graph + partition learning | SUBSUMED | Prior art trực tiếp | [reassessment Report D](reports/reassessment_2026-11-03_vi/00_final_reassessment_vi.md) | — |
| X9 | Anytime latent discovery; restricted-CI semantics; weighted conflict resolution | SUBSUMED | Prior art trực tiếp | như trên | — |
| X10 | "Forced-feature confidence" (khoảng cách tới mô hình phủ định feature) | SUBSUMED | Chính là ACI Eq. 16 (NeurIPS 2016) | như trên; ACI tr. 5 | — |
| X11 | B′ — query complementarity / budget framework độc lập | DEPRIORITIZED | Prior art dày (ICD, k-PC, C-PC, CCPG, GAS) | [card B1](reports/reassessment_2026-11-03_vi/topic_cards/B1_query_complementarity_budget_vi.md) | Chỉ pilot oracle nhỏ, nếu A′ và T4 đều thất bại |
| X12 | **A′ gốc:** D(f) dạng hiệu dùng full Σ̂ làm "confidence"; claim H-cal | **REFUTED** | Không calibrated; Σ suy biến; η quyết định dấu | [contract v2](reports/aprime_review_2026-11-04/A1_mathematical_contract_v2.md), [toy](reports/aprime_review_2026-11-04/A1_toy_results.md) | Chứng minh calibration cho D trên lớp bài toán xác định |
| X13 | "Off-diagonal / dependence-aware là cơ chế khoa học mới" | SUBSUMED | GLS/minimum-distance (Browne 1984); non-separability là tính chất chung của dạng toàn phương | contract v2 §4-P4; register §5 | — |
| X14 | Δ_FAR với ngưỡng hiệu chỉnh ở minimal-Q rồi giữ cố định ([PLAN] §3) làm metric calibration | REFUTED | Phạt phương pháp đúng (toy B3) | [toy §3.3](reports/aprime_review_2026-11-04/A1_toy_results.md) | — |
| X15 | Quy ước pseudo-inverse có support (P5) cho near-duplicate queries | REFUTED | Gán +∞ cho mô hình đúng ở 100% replicate | toy §4.2 | — |
| X16 | Chỉ dùng duplicate-invariance làm điểm khác ACI | SUBSUMED | ACI + dedup đạt cùng tính chất | contract v2 P5 | — |
| X17 | So sánh hiệu năng chỉ dựa trên SHD/argmax PAG cho dependence-aware scoring | REFUTED như kỳ vọng lợi ích | BSC-D: thứ tự PAG "almost always the same" | bscd.pdf tr. 13–14 | — |

**Chưa bị bác bỏ, chỉ chưa kiểm tra:** ứng viên A/B của review 30/10 (LLM feedback loop, calibration consensus→disputed); T4 (selection-indexed premises dưới missing data; backup); C-S (coordinated-shift breakdown radius); K2–K4 của kill test.

---

## 4. Tài sản còn giá trị (đừng viết lại từ đầu)

| Tài sản | Ở đâu | Trạng thái |
|---|---|---|
| Kill-test runner, schedulers, oracle/Gaussian CI, provenance gates | `src/safety_prior/`, `configs/kill_test/`, `tests/` | Chạy được; full test suite pass (04/11/2026) |
| Reference ICD, batch CI, frozen stable epoch + audit CLI | `src/safety_prior/algorithms/`, `src/safety_prior/pilots/`, `configs/tensorized_icd/` | G0–G2 PASS |
| Raw artifacts K0/K1 | `artifacts/` (**không** trong Git, ~29 GB) | Lưu cục bộ |
| Toy validation A′ (exact distance-to-union solver, delta-method Σ cho Fisher-z đã kiểm chứng Monte Carlo) | `reports/aprime_review_2026-11-04/A1_toy_mechanism_validation.py` | 192/192 assertion PASS |
| Corpus paper + manifest SHA-256 | `docs/papers/` (PDF không trong Git) | Đầy đủ cho A′/R1 |

---

## 5. Trạng thái hiện tại (04/11/2026)

- **ACTIVE:** A′ reformulated, gồm R1 (*simultaneous certified ancestral assertions* cho MAG có latent, từ vector CI statistics, ngưỡng χ²_rank, valid pointwise với η_n → 0) và R2 (η-profile cho guarantee đồng đều).
- **Gate tiếp theo:** RG1 (chứng minh) và **RG2 (kill test: power của R1 so với Bonferroni IUT và Chang-style resampling)**. Nếu RG2 âm thì dừng A′, chuyển sang T4.
- **Backup:** T4.

---

## 6. Quy tắc bảo trì file này

1. Mỗi lần đổi hướng hoặc qua/rớt gate quan trọng: **thêm** một dòng vào §1, một mục vào §2, và cập nhật §3 nếu có ý tưởng bị bác bỏ.
2. Không xóa hay sửa phán quyết cũ. Nếu đảo ngược, thêm mục mới ghi "đảo ngược X# vì …".
3. Mỗi dòng phải có **đường dẫn bằng chứng**. Không ghi phán quyết không có nguồn.
4. Tài liệu của hướng bị đóng chuyển vào `archive/<YYYY-MM>_<tên>/` (không xóa); cập nhật [`archive/README.md`](archive/README.md).
