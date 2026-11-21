# Lịch sử chuyển dịch nghiên cứu (Research pivot log)

> **Đọc file này trước khi đề xuất bất kỳ hướng mới nào.** Mục đích là tránh làm lại những gì đã bị bác bỏ, đã có prior art hoặc đã bị gác lại có lý do.
> Cập nhật lần cuối: **2026-11-12**. Quy tắc bảo trì ở §6: **append-only**. Không sửa phán quyết cũ; nếu đảo quyết định thì thêm một mục mới tham chiếu mục cũ.
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
| P7 | 04/11 | **RG1: chứng minh R1/R2** | R1 có chứng minh đầy đủ và có power không? | Validity có chứng minh. Bản seminorm toàn cục **REFUTED về power** (T(f) ≡ 0 khi có mô hình mù), sửa thành ridge + χ² có trọng số (đều khi K cố định). Trong lớp η ≤ β, pointwise không phân biệt được R1. Rà soát bởi agent AI: `PASS WITH CORRECTIONS`, đã áp dụng; **user duyệt PASS có điều kiện 05/11; chưa có người rà; RG2 chưa chạy** | [`RG1_R1_proof_vi.md`](reports/aprime_review_2026-11-04/RG1_R1_proof_vi.md) |
| P8 | 05/11 | **RG3 + S1 (phép thử rẻ trước RG2)** | R1 có lợi thế và có kịch bản có nội dung không? | Không dừng theo tiêu chí khai báo trước, tín hiệu yếu. Hybrid không có lợi thế; T có gain 1.2–2.9 lần; S1 đạt 2/761 ở h = 3; cơ chế có lẽ là whitening toàn vector. Chưa so với hộp whitening | [`RG3_S1_report_vi.md`](reports/aprime_review_2026-11-04/RG3_S1_report_vi.md) |
| P9 | 06/11 | **RG3b: T so với hộp whitening** | Hình dạng χ² có cần thiết không? | Không có khác biệt rõ theo luật khai báo trước; T nhỉnh hơn nhẹ ở K = 24, gần hòa ở K = 70; ít nhất một thủ tục hơn BL1. Whitening dạng hộp gần như không thêm gì so với MaxT đơn giản. Khuyến nghị của agent: chuyển sang T4 | [`RG3b_report_vi.md`](reports/aprime_review_2026-11-04/RG3b_report_vi.md) |
| P10 | 06/11 | **User quyết định chuyển sang T4** | Giữ A′ làm hướng chính hay kiểm tra T4? | A′ **DEPRIORITIZED** làm hướng chính: thủ tục đúng và có lợi hơn Bonferroni, nhưng lợi thế nhỏ, chưa thấy cơ chế mới. RG2 không chạy. T4 **ACTIVE**, bắt đầu bằng kill test lý thuyết | [card T4](reports/reassessment_2026-11-03_vi/topic_cards/T4_selection_indexed_premises_missingness_vi.md) |
| P11 | 06/11 | **Kill test T4** | Có giữ được target M1 bằng luật cục bộ không? Regime-indexed FCI có phải cơ chế không? | Card gốc **NO-GO** với truy vấn giữa biến O. Luật theo regime đúng nhưng lợi ích chủ yếu đến từ phép tách đơn giản. Nảy sinh **T4-L** (lift bằng kiểm định chỉ báo): positive ở họ cộng tính, fragile ở họ tương tác, toán lõi không mới. **GO có điều kiện** tới audit và pilot thuật toán, chờ user | [`T4_kill_test_vi.md`](archive/2026-11_t4_selection_indexed/T4_kill_test_vi.md) |
| P12 | 06/11 | **Audit văn liệu T4-L** | Đã có ai dùng phép test chỉ báo làm bước xác nhận CI trong discovery chưa? | Tiêu chí no-go **không bị kích hoạt** trong giới hạn sàng lọc. Novelty **hạ xuống**: toán đã có (Didelez 2010 Thm 6), tính testable, dạng test và pretest cũng đã có. Baseline FCI có chỉ báo không thay thế được T4-L ở oracle. Pilot thuật toán chờ user | [`T4L_literature_audit_vi.md`](archive/2026-11_t4_selection_indexed/T4L_literature_audit_vi.md) |
| P13 | 06/11 | **Pilot thuật toán T4-L** | LiftG2 có giảm claim sai so với M1 mà giữ claim đúng không? | **NO-GO theo K8:** tỉ lệ sai 1.06 [1.02, 1.10], Naive và các baseline khác hòa hoặc thắng. Chẩn đoán post hoc một phần: lỗi nền chiếm phần lớn, tiến gần target listwise không giúp claim về DAG. Chờ user xác nhận đóng; **chưa có backup** | [`T4L_pilot_report_vi.md`](archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md) |
| P14 | 07/11 | **User đóng T4-L** | Có đóng T4-L sau NO-GO và chẩn đoán đủ 9 ô không? | T4-L **REFUTED** theo framing đã thử; card T4 gốc NO-GO. Tài liệu chuyển vào `archive/`. Không còn hướng ACTIVE, chưa có backup | [`archive/2026-11_t4_selection_indexed/`](archive/2026-11_t4_selection_indexed/) |
| P15 | 07/11 | **User đặt lại quy trình: dữ liệu trước** | Gap nào nhìn thấy được trên dữ liệu uy tín, thay vì bắt đầu từ chứng minh toán? | Pilot trên Causal Chamber và Sachs. Ứng viên chính **C1** (mất cạnh mạnh do đo lường dư thừa khi có latent), **Conditional**, chờ phép thử R1 với BOSS-FCI, GFCI, FCIT. Dự phòng **C2**. Chưa có cơ chế mới | [`00_data_first_gap_report_vi.md`](reports/data_first_gap_2026-11-07/00_data_first_gap_report_vi.md) |
| P16 | 09–12/11 | **Đi vòng: finance (bỏ trong ngày) rồi time-series TS-G1 trên CausalRivers** | Confounding ẩn do mưa có đo được trên dữ liệu sông thật không; LPCMCI có sửa được không? | Lỗi sampler Confounder của CausalRivers **xác nhận bằng đếm lại** (24/361 = Bảng 6 của bài). Pilot P1 (2400 job): R1 đạt (0.31), R2 **không đạt**, R3 = **GAP-A ở mức tin cậy thấp**, còn bốn giải thích thay thế A1–A4 chưa loại trừ. User chuyển hướng 12/11 sau khi đọc một tài liệu tham khảo nội bộ; TS-G1 **DEPRIORITIZED** (X32) | [`P1_results_vi.md`](reports/timeseries_deep_dive_2026-11-09/P1_results_vi.md), [deep dive](reports/timeseries_deep_dive_2026-11-09/00_ts_causal_discovery_deep_dive_vi.md), [audit gap (2)](reports/timeseries_deep_dive_2026-11-09/G2_prior_art_audit_vi.md) |
| P17 | 12/11 | **Mở lại hướng LLM-prior + FCI có biến ẩn với framing mới** | FCI lấy gì từ một guess của LLM dưới biến ẩn, và guess sai gây hại theo cách nào không thể có dưới causal sufficiency? | Kế hoạch và luật đọc cho hai pilot P-A (lỗi LLM theo loại cặp D/B/I/N) và P-B (lan truyền guess sai có kiểu trong FCI oracle) đã viết, **chờ user duyệt**. X1 và X5 **vẫn đóng**. **ACTIVE (conditional)** | [`00_plan_vi.md`](reports/llm_prior_latent_fci_2026-11-12/00_plan_vi.md), [`PA_PB_reading_rules_vi.md`](reports/llm_prior_latent_fci_2026-11-12/PA_PB_reading_rules_vi.md) |
| P18 | 12–13/11 | **Pilot P-B và P-A, quyết định D1** | Lỗi LLM có tập trung ở cặp ↔ không (P-A)? Lỗi đặc thù biến ẩn có lan nhiều hơn trong FCI không (P-B)? | P-B: **NO LATENT-SPECIFIC HARM** (đảo chiều lan nhiều nhất). P-A: **H-TYPE NOT CONFIRMED** (OpenAI, Llama; DeepSeek bị loại theo RA0). D1 = **đóng hướng P17** (X33). Phụ: `dag2pag` của causal-learn 0.1.4.8 không sound | [`PB_results_vi.md`](reports/llm_prior_latent_fci_2026-11-12/PB_results_vi.md), [`PA_results_vi.md`](reports/llm_prior_latent_fci_2026-11-12/PA_results_vi.md) |
| P19 | 13/11 | **Quét hướng mới sau P17; user đưa danh sách N1–N4; audit N1** | Có gap nào thỏa bộ lọc mới (giao hai hiệu ứng đã biết, câu "vì sao", đòn bẩy sạch) không? | Quét cho C1 (khoảng cách hiệu chỉnh cho PAG; gap được Henckel 2024 và Wahl–Runge 2025 tự xác nhận) và C2–C4. User đưa N1–N4; N2 = C1. Audit N1 ("thêm biến độc lập có làm mô hình causal discovery học sẵn đổi kết luận không"): 8 bài, không ai thử; CausalArena loại biến cô lập khỏi benchmark; kiến trúc attention trên trục biến không bảo đảm bất biến; PC/GES/FCI bất biến tiệm cận làm mốc. **User chốt N1 làm chính, C1 dự phòng (13/11). ACTIVE: N1** | [`00_direction_scan_vi.md`](reports/direction_scan_2026-11-13/00_direction_scan_vi.md), [`N1_prior_art_audit_vi.md`](reports/direction_scan_2026-11-13/N1_prior_art_audit_vi.md) |

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

### P6 → P7: RG1 giữ validity nhưng đổi định nghĩa R1
- Chi tiết và chứng minh ở [`RG1_R1_proof_vi.md`](reports/aprime_review_2026-11-04/RG1_R1_proof_vi.md).
  1. **Validity có chứng minh đầy đủ** (joint CLT dạng đóng, V1 pointwise, V2 đều trên compact).
  2. **Bản seminorm toàn cục Σ⁺ + χ²_rank của contract §7 rỗng nghĩa khi M_¬f chứa mô hình mù:** inf đi theo null Σ, T(f) ≡ 0 với mọi dữ liệu. K > rank một mình không đủ. Ở p = 4, K = 24 có 178/185 pattern mù. Vì R_n ⊋ A_n chứa các điểm không đạt được.
  3. **Sửa:** Ω̂ = (Σ̂ + λ_nI)⁻¹ với ngưỡng χ² có trọng số. Valid đều khi p, K cố định, không cần ước lượng rank, T(f) → ∞. Ở K lớn lệch nặng nếu λ quá nhỏ. Kỹ thuật thuộc họ regularized Wald (Dufour–Valéry), không mới.
  4. **"Valid pointwise" không phải điểm mạnh:** thresholding nhất quán đạt FWER → 0, power → 1. Trong lớp η ≤ β, regime duy nhất R1 có thể có nội dung là √nη < 2t_K, và **chưa có kịch bản nào cho thấy nội dung đó**. Vì vậy R2 không phải phần phụ (đảo nhận định ở readiness §11.4), nhưng cũng chưa có bằng chứng nó hữu ích.
  5. **Ngưỡng chiếu χ²_r bị trội** bởi ngưỡng valid theo từng mô hình. Lợi từ R² yếu đi dưới metric ridge và không phải của riêng χ². RG3 phải đo R² và số tọa độ khác nhau của đối thủ gần nhất.
  6. **Rà soát độc lập bởi agent AI:** `PASS WITH CORRECTIONS` ([báo cáo](reports/aprime_review_2026-11-04/RG1_independent_review_vi.md)); các định lý đứng được, các kết luận rút ra bị thu hẹp.

### P10 → P11: kill test T4 (06/11)

- **Vì sao đổi:** phản ví dụ cho thấy không luật cục bộ nào chỉ dùng CI giữa biến O giữ được target listwise của M1. Regime-indexed FCI đúng (0 vi phạm oracle), nhưng phần lớn claim thêm chỉ cần phép tách.
- **Học được:** chỉ báo thiếu luôn quan sát được nên phép test chỉ báo làm được trên hàng đủ U. Ở họ cộng tính, phụ thuộc do selection là bậc hai còn phụ thuộc với chỉ báo là bậc nhất; ở họ tương tác thứ tự đảo lại. Lift1 giảm định hướng sai rất mạnh ở họ đầu, gần bằng naive ở họ sau.
- **Tự sửa:** phép đo PP so với LW đầu tiên bị lệch (tỉ lệ > 1 khi q = 0); đã thêm đối chứng LWu và K5 trước lần chạy đầy đủ. Card T4 ghi M1 §10.1 có ví dụ, thực tế không có đồ thị tường minh.
- **Bằng chứng:** [`T4_kill_test_vi.md`](archive/2026-11_t4_selection_indexed/T4_kill_test_vi.md).

### P11 → P12: audit văn liệu T4-L (06/11)

- **Vì sao làm:** bước 1 của điều kiện đi tiếp ở kill test.
- **Học được:** điều tôi gọi là Mệnh đề L đã có trong Didelez et al. 2010 Theorem 6. Test chỉ báo cũng đã có trong kinh tế lượng (attrition), và logic pretest rồi xóa dữ liệu đã có trong Ji et al. 2023. Phần chưa tìm thấy chỉ còn: dùng làm bước xác nhận trong FCI có latent, và so sánh power theo bậc hiệu ứng.
- **Tự sửa:** bản đầu của phép thử baseline tạo cạnh giả R_i–O_i, bị đối chứng q = 0 phát hiện; số của bản đó đã bỏ.
- **Giới hạn:** sàng lọc trích dẫn chỉ trên tiêu đề và tóm tắt; năm bài gần chưa đọc được toàn văn.
- **Bằng chứng:** [`T4L_literature_audit_vi.md`](archive/2026-11_t4_selection_indexed/T4L_literature_audit_vi.md).

### P12 → P13: pilot thuật toán T4-L (06/11)

- **Vì sao đổi:** lợi thế lớn ở mức một bộ ba biến không còn ở FCI đầy đủ. LiftG2 tăng nhẹ claim sai so với M1, kể cả ở cơ chế cộng tính.
- **Học được:** M1 thật sự không đạt target listwise ở finite sample và lift khớp target tốt hơn, nhưng khớp target hơn không giảm claim sai về DAG. Naive có ít claim sai quy cho missing data nhất. Có thể target listwise không phải thứ đáng tiến tới. (Suy luận từ 4/9 ô post hoc.)
- **Tự sửa:** không có lỗi code làm đổi kết luận. Đã ghi rõ: FCI tự viết chưa đối chiếu thư viện, trường `flag_false` không được tính, ngưỡng K8 chưa được user chốt.
- **Chưa loại trừ:** MNAR rất mạnh, vì ô b × 3 bị dừng do thiếu RAM.
- **Bằng chứng:** [`T4L_pilot_report_vi.md`](archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md).

### P13 → P14: đóng T4-L (07/11)

- **Vì sao đóng:** NO-GO theo K8; tăng liều MNAR không đảo kết quả mà làm lift tệ hơn; toán lõi đã có từ Didelez 2010.
- **Học được:** ở mô phỏng này, target listwise đúng ở oracle nhưng chỉ còn khoảng một phần ba số claim, và các phương pháp còn rất xa nó ở n đã thử. Lỗi nền chủ yếu do sai số CI ở finite sample.
- **Giới hạn của phán quyết:** dựa trên mô phỏng tuyến tính Gauss do agent thiết kế, FCI tự viết chưa đối chiếu với thư viện, chưa ai rà độc lập các chứng minh; ngưỡng K8 do agent đề xuất và user không chỉnh trước khi đóng.
- **Bằng chứng:** [`T4L_pilot_report_vi.md`](archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md).

### P14 → P15: quy trình dữ liệu trước (07/11)

- **Vì sao đổi:** user đánh giá lối đi từ chứng minh toán học khó tiếp cận và kém khả quan; muốn gap được chứng minh tồn tại trên dữ liệu uy tín, đồng thời vẫn đủ mạnh về ý nghĩa khoa học.
- **Học được:** trên Chamber, FCI mất 14/21 cạnh mạnh nhưng nhận đúng 3 cặp confounded; BOSS giữ 21/21 nhưng không nói được về confounding. Precision giảm theo n chủ yếu do sai dạng hàm, không phải phụ thuộc residual như agent dự đoán. Chấm lại benchmark gần như không đổi thứ hạng.
- **Tự sửa:** ba dự đoán của agent bị dữ liệu bác bỏ hoặc không ủng hộ (E6, E7, E1b); đều được ghi trong báo cáo.
- **Giới hạn:** một hệ vật lý; lớp phương pháp lai chưa chạy; E3 phần Sachs chưa xong do hệ thống dừng vì thiếu RAM.
- **Bằng chứng:** [`00_data_first_gap_report_vi.md`](reports/data_first_gap_2026-11-07/00_data_first_gap_report_vi.md).

### P15 → P16: đi vòng qua finance và chuỗi thời gian (09–12/11)

- **Vì sao:** user muốn dataset và hướng có đóng góp cao; sáu bài toán tài chính được quét rồi bỏ trong ngày; chọn causal discovery chuỗi thời gian; TS-G1 (mưa là confounder ẩn có thể lộ hoặc giấu trên CausalRivers) được chọn làm chính, luật đọc khóa 10/11 trước khi chạy.
- **Học được:** (1) sampler Confounder của CausalRivers không bao giờ bỏ nút confounder, và đếm lại cho thấy Bảng 3 của bài chấm trên fork quan sát đầy đủ; (2) có dependence giả giảm theo khoảng cách giữa các sông không nối nhau (PCMCI+ 0.48 ở gần so với 0.14 ở xa), nhưng proxy mưa không giải thích được nó (R2 không đạt); (3) LPCMCI đưa ra claim tổ tiên sai **nhiều hơn** PCMCI+ và tệ hơn nữa khi lộ mưa (0.67 → 0.88); (4) về quy trình: pilot thiết kế dạng chuỗi cổng go/no-go nên mọi nhánh trừ một đều là "dừng", và đòn bẩy (proxy mưa cách 20 km) quá yếu để tách nguồn confounding.
- **Tự sửa:** hai đơn vị có proxy mưa trùng hệt gây `LinAlgError`; sửa thành một biến mưa chung và ghi §8 trước khi xem metric. Một lần chạy dừng với mã lỗi 4 không rõ lý do, đã chạy tiếp.
- **Bằng chứng:** [`P1_results_vi.md`](reports/timeseries_deep_dive_2026-11-09/P1_results_vi.md), [`TS_G1_reading_rules_vi.md`](reports/timeseries_deep_dive_2026-11-09/TS_G1_reading_rules_vi.md) §8, [`G2_prior_art_audit_vi.md`](reports/timeseries_deep_dive_2026-11-09/G2_prior_art_audit_vi.md).

### P16 → P17: đọc một tài liệu tham khảo nội bộ, chẩn đoán lại quy trình tìm gap (12/11)

- **Vì sao đổi:** user đánh giá các hướng agent tìm được không đáng đi sâu và đưa một tài liệu tham khảo nội bộ (không công khai) để chẩn đoán. Bài học rút ra: một đóng góp không cần phương pháp mới nếu có một phép tách đo được trong cùng đơn vị, một cơ chế trả lời "vì sao", một cảnh báo phương pháp luận và một lần tính lại benchmark.
- **Học được, về quy trình:** (1) câu hỏi phải có giá trị ở mọi nhánh kết quả, không phải chuỗi cổng cho một phương pháp tương lai; (2) đóng góp kiểu "phát hiện + cơ chế + audit" là hợp lệ, trong khi X31 và yêu cầu "novel mechanism" trong AGENTS.md đã lọc bỏ đúng loại này; (3) hỏi "vì sao" thay vì "có không"; (4) đòn bẩy phải là thứ kiểm soát hoàn toàn; (5) gap mạnh là **phép giao** hai hiện tượng đã biết chưa ai đo cùng lúc, không phải ô trống trong bảng phân loại. Kết quả bất ngờ (lỗi CausalRivers, LPCMCI tệ hơn khi lộ confounder) đã bị xếp dưới kết quả theo kế hoạch.
- **Quyết định của user:** chiến lược "cải thiện những gì đã có, đọc limitation" được chấp nhận với điều kiện chỉ lấy hai loại limitation (thiết kế không tách được hai thứ; câu hỏi "vì sao" chưa trả lời). Chọn giao điểm **LLM làm prior cho causal discovery có biến ẩn, baseline FCI**. Mentor đặt câu hỏi về "độ tự nhiên" của việc chèn LLM vào FCI; phân tích và framing mới ở [`00_plan_vi.md`](reports/llm_prior_latent_fci_2026-11-12/00_plan_vi.md) §1.2.
- **Chưa quyết:** nới X31 hay không; user chưa trả lời.

### P17: ranh giới với hướng cũ (12/11)

- Hướng 18/09–21/10 được mở lại **không** theo framing scheduler. X1 (đổi thứ tự CI query làm đóng góp chính) và X5 (LLM + latent discovery như gap) vẫn SUBSUMED. Con số K1 (23% với oracle, chỉ FAS) được dùng làm bằng chứng rằng trần của framing "tối ưu" đã đo và không đủ.
- Framing mới: đo **lỗi của LLM theo loại cặp của MAG** (D/B/I/N) và **lan truyền guess sai có kiểu** trong FCI, kèm tính phát hiện được từ dữ liệu. Phương pháp chỉ là hệ quả nếu hai pilot cùng dương.
- Ràng buộc kỹ thuật đã kiểm trong mã: `BackgroundKnowledge` của causal-learn xóa cạnh khi hai chiều đều forbidden và không giữ cạnh required trong FAS, nên P-B phải tự chèn dấu đầu mút.

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
| X18 | **R1 với seminorm toàn cục Σ⁺ (quy ước C-c) + χ²_rank** làm thủ tục chứng nhận | REFUTED | Valid nhưng rỗng nghĩa: T(f) ≡ 0 khi M_¬f chứa mô hình mù (p = 4, K = 24: 178/185 pattern mù) | [RG1 Thm 4](reports/aprime_review_2026-11-04/RG1_R1_proof_vi.md) | Dùng tập đạt được A_n (R3), hoặc seminorm theo khối từng mô hình |
| X19 | "Valid pointwise với η_n → 0" làm điểm khác biệt của R1 | SUBSUMED | Thresholding nhất quán đạt FWER → 0, power → 1 | RG1 Mệnh đề 7; Robins et al. 2003 | Chỉ khi nhắm regime cục bộ √nη < 2t_K |
| X20 | Σ̂⁺ không cắt rank, hoặc Σ⁻¹ oracle, với ngưỡng χ² gần điểm rớt rank | REFUTED | Giới hạn không phải χ²: 0.017 (bảo thủ) và 0.06–0.09 (anti-conservative) | RG1 Mệnh đề 3, §8.1 | Q chứa mọi query biên thì rank hằng |
| X21 | η*(f) không kèm cận trên η̄ | REFUTED (định nghĩa) | Cả f lẫn ¬f đều có η* hữu hạn | RG1 Thm 7(c) | — |
| X22 | Hybrid (Wald khối I + hộp phía D) làm thủ tục chính của R1 | REFUTED như ứng viên chính | Gain = 1 so với box ở mọi ô RG3 | [RG3 §2](reports/aprime_review_2026-11-04/RG3_S1_report_vi.md) | Đối thủ khó nhất không còn nằm ở phía D |
| X23 | Giữ đúng target listwise của M1 bằng luật cục bộ chỉ dùng CI giữa biến O | REFUTED | Cặp DAG giống nhau ở mọi regime không chứa T nhưng khác target listwise | [T4 §4](archive/2026-11_t4_selection_indexed/T4_kill_test_vi.md) | Không áp dụng nếu dùng truy vấn chỉ báo, xem T4-L |
| X24 | Ghép premise từ các regime khác nhau rồi kết luận thuần, không xác nhận | REFUTED | R0, R1, R4 ngây thơ cho claim sai: 395/1761, 457/1674, 16/1610 | [T4 §4](archive/2026-11_t4_selection_indexed/T4_kill_test_vi.md) | Bản theo regime thì đúng |
| X25 | Lấy regime-indexed FCI làm cơ chế trung tâm của bài | DEPRIORITIZED | Bổ đề đơn giản; PP/SepOnly chỉ 1.04–1.21 ở p = 6, 7 (gần 1.00–1.06 ở p = 4, 5), đạt 1.10 chỉ ở đồ thị dày; quy về FCI trên tập con | [T4 §4](archive/2026-11_t4_selection_indexed/T4_kill_test_vi.md) | Vẫn dùng được làm lớp nền |
| X26 | Trình bày lift bằng chỉ báo như kết quả toán mới | REFUTED | Chính là Didelez et al. 2010 Theorem 6, áp dụng có điều kiện trên S_U; chiều test-wise có ở Witte Lemma 6 | [Audit §1–2](archive/2026-11_t4_selection_indexed/T4L_literature_audit_vi.md) | Không bác bỏ việc dùng nó làm thủ tục; chỉ bác bỏ tuyên bố novelty về toán |
| X27 | T4-L: thay bước xác nhận listwise của FCI bằng chuỗi kiểm định chỉ báo | NO-GO theo K8, chờ user xác nhận đóng | Sai 1.06 lần M1; LW, Naive, Flag, MI, FCI-R hòa hoặc thắng | [Pilot §1](archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md) | Nếu xem lại: phải có bằng chứng mới về MNAR rất mạnh, hoặc đổi target khỏi listwise |
| X28 | Đánh giá phương pháp missing-data trong FCI mà không có đối chứng dữ liệu đầy đủ | Bài học phương pháp | Dữ liệu đầy đủ đã có 8–13 claim sai mỗi đồ thị; phần do missing data chỉ 2–8 | [Pilot §4](archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md) | Luôn đo lỗi nền trước |
| X29 | Đóng T4-L theo quyết định của user (cập nhật X27) | REFUTED theo framing đã thử; phần toán SUBSUMED (X26) | Pilot §1 và §4 đủ 9 ô | [Pilot](archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md) | Mở lại chỉ khi có bằng chứng mới mâu thuẫn trực tiếp, ví dụ dữ liệu thật hoặc mô phỏng độc lập cho thấy lift giảm claim sai so với M1. Câu hỏi "chọn target nào dưới missing data" là câu hỏi khác, chưa được audit, không bị đóng ở đây |
| X30 | Giả thuyết: precision giảm theo n trên Chamber chủ yếu do phụ thuộc residual giữa sensor | REFUTED theo L5 | Knock-out: bỏ phụ thuộc residual nhưng giữ phi tuyến vẫn giảm .23; tuyến tính hóa chỉ giảm .017 | [E6](reports/data_first_gap_2026-11-07/E6_summary.json) | Không áp dụng cho ba cặp `ir_i`–`vis_i`, vốn là phụ thuộc thật |
| X31 | Kiểm toán benchmark thật sẽ đảo thứ hạng thuật toán, làm đề tài độc lập | DEPRIORITIZED | Chấm lại trên Chamber: Spearman .89–1.00; chỉ đổi điểm tuyệt đối. Post hoc, một hệ | [E7](reports/data_first_gap_2026-11-07/E7_outputs.json) | Có hệ khác cho thấy đảo thứ hạng thật |
| X32 | TS-G1 (confounding ẩn do mưa trên CausalRivers) và khoảng trống (2) "confounder cục bộ, thay đổi theo thời gian" làm hướng phương pháp | DEPRIORITIZED | P1 cho GAP-A nhưng R2 không đạt và A1–A4 (bộ nhớ dài hơn τ_max, ParCorr sai mô hình, artefact nội suy, lỗi topology) chưa loại trừ; FNETS chưa kiểm; user chuyển hướng 12/11 | [`P1_results_vi.md`](reports/timeseries_deep_dive_2026-11-09/P1_results_vi.md), [`G2_prior_art_audit_vi.md`](reports/timeseries_deep_dive_2026-11-09/G2_prior_art_audit_vi.md) | Chạy P2 theo §6 của P1_results (τ_max dài, mưa tích lũy, test phi tuyến, bỏ đoạn nội suy, lọc chain, baseline khử nhân tố) với luật đọc mới |
| X33 | P17: "chèn LLM vào FCI dưới biến ẩn có kiểu lỗi đặc thù" (H-type, H-prop) làm cơ sở cho phương pháp | REFUTED theo framing đã thử | P-A: ΔFP OpenAI +0.005, Llama +0.063, cả hai CI chứa 0; P-B: ΔL = −0.45, đảo chiều lan nhiều hơn các lỗi đặc thù biến ẩn | [`PA_results_vi.md`](reports/llm_prior_latent_fci_2026-11-12/PA_results_vi.md), [`PB_results_vi.md`](reports/llm_prior_latent_fci_2026-11-12/PB_results_vi.md) | Bằng chứng mới mâu thuẫn trực tiếp: model lớn hơn hoặc mạng không thuộc lòng cho ΔFP ≥ 0.10 với CI > 0, **và** P-B ở mẫu hữu hạn cho lỗi đặc thù biến ẩn lan nhiều hơn đảo chiều |

**Chưa bị bác bỏ, chỉ chưa kiểm tra:** ứng viên A/B của review 30/10 (LLM feedback loop, calibration consensus→disputed); T4 (selection-indexed premises dưới missing data; backup); C-S (coordinated-shift breakdown radius); K2–K4 của kill test.

**Nới X31 (12/11, quyết định của user):** X31 chỉ còn nghĩa "audit benchmark **đơn lẻ** không đủ làm đề tài". Một bài gồm **phép đo có đối chứng + cơ chế giải thích + audit**, không có thuật toán mới, là đích hợp lệ của dự án (mẫu: một tài liệu tham khảo nội bộ; phân tích ở [`00_plan_vi.md`](reports/llm_prior_latent_fci_2026-11-12/00_plan_vi.md) §1.2). Phán quyết cũ của X31 và bằng chứng E7 giữ nguyên, không bị xóa.

**Bổ sung 12/11 vào danh sách chưa kiểm tra:** P2 của TS-G1 (A1–A4, FNETS); bốn giả thuyết của P17 (H-type, H-prop, H-silent, H-fix), đang chờ pilot P-A và P-B. Lỗi sampler Confounder của CausalRivers đã xác nhận nhưng **chưa báo cho tác giả** theo quyết định của user.

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

## 5. Trạng thái hiện tại (07/11/2026)

- **Từ 07/11: không có hướng ACTIVE và chưa có backup.** T4-L đã đóng theo quyết định của user (X29). Các dòng bên dưới là trạng thái lúc ghi, giữ lại theo quy tắc append-only. Việc kế tiếp chưa được quyết định.
- **ACTIVE từ 06/11: T4.** Phần A′ bên dưới là trạng thái khi dừng. A′ reformulated, gồm R1 (*simultaneous certified ancestral assertions* cho MAG có latent, từ vector CI statistics, metric ridge với λ khai báo theo K, ngưỡng valid theo từng mô hình) và R2 (η-profile kèm η̄, là phần mang nội dung của bảo đảm). Định nghĩa theo [RG1](reports/aprime_review_2026-11-04/RG1_R1_proof_vi.md) §10.1; bản χ²_rank + seminorm đã bị bác bỏ (X18).
- **RG1:** đã qua một lượt rà soát bởi agent AI (`PASS WITH CORRECTIONS`), các sửa chữa đã áp dụng; user duyệt PASS có điều kiện ngày 2026-11-05; chưa có người rà.
- **Quyết định của user (06/11):** A′ không còn là hướng chính, chuyển sang T4. A′ chỉ DEPRIORITIZED, không bị bác bỏ; phần đã làm đủ cho một ghi chú phương pháp ngắn nếu cần. Xem [RG3b](reports/aprime_review_2026-11-04/RG3b_report_vi.md).
- **Đang kiểm tra:** T4 (selection-indexed premises dưới missing data), kill test lý thuyết R0/R4. **Chưa có backup mới.**
- **Cập nhật 06/11 sau kill test:** T4 theo card gốc NO-GO; **T4-L** (lift bằng kiểm định chỉ báo) GO có điều kiện, bước kế là audit văn liệu rồi pilot mức thuật toán, **chờ user quyết định**. Theo luật khai báo trước, cơ chế phụ thuộc vào mô hình chỉ báo đúng. Chưa có người rà các chứng minh. Xem [`T4_kill_test_vi.md`](archive/2026-11_t4_selection_indexed/T4_kill_test_vi.md). **Chưa có backup mới.**
- **Cập nhật 06/11 sau audit:** no-go không bị kích hoạt, nhưng novelty hẹp (X26). Kỳ vọng hạ xuống một bài phương pháp ngắn. Khuyến nghị: chạy pilot thuật toán và tìm song song hướng dự phòng, **chờ user quyết định**. Xem [`T4L_literature_audit_vi.md`](archive/2026-11_t4_selection_indexed/T4L_literature_audit_vi.md).
- **Cập nhật 06/11 sau pilot:** T4-L **NO-GO theo K8** (X27), chờ user xác nhận đóng. T4 không còn ứng viên đang chạy. **Chưa có backup.** Xem [`T4L_pilot_report_vi.md`](archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md).
- **Cập nhật 06/11 sau chẩn đoán đủ 9 ô:** tăng liều MNAR không đảo kết quả. Sửa cách đọc: target listwise không có hại ở oracle (0 claim sai) nhưng rất nghèo (20.7 so với 61.5 claim đúng), và ở n đã thử các phương pháp còn rất xa nó. Việc cắt tập điều kiện không phải nguyên nhân ở oracle. Câu hỏi có thể đáng xem: chọn target nào, chưa kiểm tra văn liệu. Xem [`T4L_pilot_report_vi.md`](archive/2026-11_t4_selection_indexed/T4L_pilot_report_vi.md) §4.
- **Cập nhật 07/11, quy trình dữ liệu trước:** chưa có hướng ACTIVE đã cam kết. Ứng viên **C1** ở trạng thái `Conditional`; bước kế là R1 (chạy BOSS-FCI, GFCI, FCIT trên Chamber) và đọc các bài ưu tiên 1. **Chờ user quyết định.** Xem [`00_data_first_gap_report_vi.md`](reports/data_first_gap_2026-11-07/00_data_first_gap_report_vi.md).
- **Cập nhật 09–12/11:** C1 không được theo đuổi (user đổi phạm vi). Finance quét rồi bỏ. TS-G1 trên CausalRivers chạy xong P1: GAP-A ở mức tin cậy thấp; **DEPRIORITIZED** theo quyết định user 12/11 (X32). Xem [`P1_results_vi.md`](reports/timeseries_deep_dive_2026-11-09/P1_results_vi.md).
- **Cập nhật 12/11, ACTIVE (conditional): P17.** Hướng LLM-prior + FCI có biến ẩn, framing "FCI lấy gì từ một guess của LLM dưới biến ẩn". Kế hoạch và luật đọc P-A/P-B đã viết, **chờ user duyệt** và điền ba tham số (danh sách LLM, trần chi phí, cho phép tải bnlearn). X1 và X5 vẫn đóng. Quyết định D1 dự kiến chậm nhất 30/11. Xem [`00_plan_vi.md`](reports/llm_prior_latent_fci_2026-11-12/00_plan_vi.md).
- **Cập nhật 12/11, P-B xong:** luật đọc khóa; P-B cho **NO LATENT-SPECIFIC HARM**. Đảo chiều lan nhiều nhất; các kiểu lỗi đặc thù biến ẩn lan ít hơn. H-prop bị bác bỏ. Phát hiện phụ: (1) `dag2pag` của causal-learn 0.1.4.8 không sound (79 claim sai trên 40 đồ thị); (2) bất đối xứng: guess "↔ thành →" gần như luôn bị dữ liệu bắt, guess "→ thành ↔" phần lớn im lặng. P-A **chưa chạy được** vì cả hai API key chưa có số dư khả dụng. Theo bảng quyết định: nếu P-A xác nhận H-type thì phần phương pháp NO-GO ở oracle, P-A thành phát hiện riêng, cần chạy P-B mẫu hữu hạn trước khi đóng; nếu không thì đóng hướng. Xem [`PB_results_vi.md`](reports/llm_prior_latent_fci_2026-11-12/PB_results_vi.md).
- **Cập nhật 13/11, D1:** P-A chạy xong (ba họ, khoảng 2.1 USD). **H-TYPE NOT CONFIRMED.** Theo bảng quyết định, **đóng hướng P17** (X33). **Không còn hướng ACTIVE, chưa có backup.** Các phát hiện mô tả đáng giữ (tên biến mang gần hết recall; gpt-4.1-mini mặc định trả lời "confounded" khi tên vô nghĩa; T3 là lỗi im lặng nhất trong FCI; `dag2pag` không sound) nằm ở [`PA_results_vi.md`](reports/llm_prior_latent_fci_2026-11-12/PA_results_vi.md) §4.
- **Cập nhật 13/11, chọn hướng mới: ACTIVE = N1** (độ nhạy của mô hình causal discovery học sẵn với biến độc lập thêm vào; audit ở [`N1_prior_art_audit_vi.md`](reports/direction_scan_2026-11-13/N1_prior_art_audit_vi.md)). **Backup = C1** (khoảng cách hiệu chỉnh cho PAG). User cho phép cài JAX/torch CPU và tải checkpoint AVICI, CDFM, FoundCause. Bước kế: luật đọc P-N1, khóa trước khi chạy.
- **Cập nhật 14/11:** user tự dựng môi trường CPU và tải checkpoint (AVICI 4 bản, CDFM, FoundCause; smoke test PASS; [`N1_cpu_setup_vi.md`](reports/direction_scan_2026-11-13/N1_cpu_setup_vi.md)), viết **audit lần hai** cho N1 ([`N1_prior_art_second_audit_vi.md`](reports/direction_scan_2026-11-13/N1_prior_art_second_audit_vi.md): sửa bốn suy luận quá mức của audit đầu; thêm tiền lệ Aliferis et al. JMLR 2010 §3 với 7 990 biến không liên quan; thêm cơ chế M4 decoder/threshold) và **luật đọc P-C1a** độc lập cho hướng dự phòng ([`P_C1a_reading_rules_vi.md`](reports/direction_scan_2026-11-13/P_C1a_reading_rules_vi.md)). Agent đối sánh và sửa luật đọc P-N1 thành v2 (xem `reports/n1_irrelevant_vars_2026-11-13/`). N1 vẫn ACTIVE; gap được hạ từ "đứng vững và mạnh" xuống "đủ để pilot, chưa đủ để claim".
- **Cập nhật 16/11, E1 của P-N1:** cả ba model (AVICI, CDFM, FoundCause) đổi kết luận và bị hại khi thêm 20 cột Gauss độc lập (H_NATIVE 0.064–0.075); hơn mốc cổ điển ở 5/6 so sánh; review độc lập không thấy lỗi. Chi tiết: [`PN1_E1_results_vi.md`](reports/n1_irrelevant_vars_2026-11-13/PN1_E1_results_vi.md).
- **Cập nhật 19/11, E2 của P-N1:** kiểm toàn vẹn đạt; cách đọc E2 ghi và commit trước khi xem số. Chữ ký exploratory: **AVICI M1** (đệm có cấu trúc hại gấp đôi đệm Gauss, dấu −); **CDFM M2** chỉ ở FIXED; **FoundCause UNEXPLAINED** (near-miss A − B ngược dấu AVICI); M3 không đạt ở model nào. Mốc cổ điển gần bất biến ở mọi kiểu và k. Hại của AVICI và FoundCause chủ yếu là mất recall. Bước kế: user duyệt đóng băng held-out (24 hệ). Chi tiết: [`PN1_E2_results_vi.md`](reports/n1_irrelevant_vars_2026-11-13/PN1_E2_results_vi.md).
- **Ghi chú lịch sử git (19/11):** các commit từ 13/11 đến 19/11 trên nhánh `docs/n1-pilot` được viết lại ngày 19/11 trước lần push đầu tiên, để bỏ tham chiếu tới tài liệu không công khai. Nội dung khoa học, số liệu và ngày giờ commit không đổi.
- **Cập nhật 19/11, đóng băng held-out (v2.2):** user duyệt held-out 80 hệ lồng nhau cho AVICI, CDFM, PC, GES và 24 hệ cho FoundCause (k0, A20, B20), sau khi mô phỏng cho thấy với 24 hệ lead AVICI M1 chỉ có khoảng 0.55 khả năng đạt luật. Luật RN5 tác nghiệp, snapshot mã kèm SHA-256 và cổng `verify_freeze.py` được commit và push trước khi chạy. Chi tiết: [`PN1_rules_v2_2_amendment_vi.md`](reports/n1_irrelevant_vars_2026-11-13/PN1_rules_v2_2_amendment_vi.md).
- **Cập nhật 20/11, held-out của P-N1:** chạy dưới đóng băng `4d789de`, toàn vẹn đạt. **Hại lặp lại ở cả ba model** (H 0.07–0.09, BEYOND_CLASSICAL PASS ở mọi estimand, kể cả CDFM native). **Cơ chế chưa xác lập:** AVICI M1 và CDFM M2 đều INCONCLUSIVE (đúng dấu nhưng chưa vượt biên); FoundCause B20 xác nhận dấu (nhánh phụ). Không đạt "GO mechanism validation"; user quyết bước tiếp. Agent đề xuất: nghiên cứu cơ chế mới (thay mật độ khối đệm ở k cố định) kèm kiểm lại prior art. Chi tiết: [`PN1_HELD_results_vi.md`](reports/n1_irrelevant_vars_2026-11-13/PN1_HELD_results_vi.md).
- **Cập nhật 20/11, user chọn hướng 2 (nghiên cứu cơ chế), kiểm prior art trước:** không thấy bài nào báo cáo đúng phát hiện của N1 (kể cả CausalArena 09/2026: không có phép đối sánh giữ nguyên khối đích). Hiện tượng gần đã biết ở bài toán dự đoán (Grinsztajn NeurIPS 2022 ≈ kiểu A; TabPFN ICLR 2023 ≈ kiểu C) và ở CD cổ điển (Aliferis 2010; Runge 2019): không được claim "lần đầu" hay "mạng nơ-ron bị feature thừa làm hại". Đã xác minh prior huấn luyện: AVICI `scm-v0` và CDFM 1–3 cạnh/nút với d tới 100; FoundCause: đường DoWhy liên thông, q = min(q0, k/(Dtot−1)). Rủi ro: một bước sàng lọc cổ điển rẻ có thể xóa phần lớn hại, phải làm baseline. Tự sửa: đòn bẩy "cạnh khác tương quan" không tách được ở hệ tuyến tính Gauss, thay bằng đòn bẩy cường độ. Chi tiết: [`N1_prior_art_recheck_2026-11-20_vi.md`](reports/n1_irrelevant_vars_2026-11-13/N1_prior_art_recheck_2026-11-20_vi.md).
- **Cập nhật 20/11, đính chính kiểm prior art sau review của user** (danh sách ở §7 của file trên):
  - Noise Immunity không ủng hộ "đệm có phụ thuộc làm giảm chất lượng": cột tương quan sinh từ biến có thông tin, và ROC-AUC không giảm.
  - FoundCause: "∝ 1/(D−1)" chỉ đúng khi trần chặn; đường DoWhy chỉ dùng với xác suất 0.5ζ.
  - Thêm Self-Compatibility (AISTATS 2024): nguyên lý nhất quán khi đổi tập biến đã có.
  - L1 giữ D cố định nên không kiểm prior gắn với d. Mask attention toàn phần chỉ là đối chứng kênh. Điều kiện dừng thay bằng contrast định trước kèm CI.
  - **Hậu nghiệm trên held-out (mô tả, không đổi nhãn):**
    - Khi đổi A → B, AVICI và CDFM đều dự đoán ít cạnh hơn (−4.9 và −10.4). F1 ngược chiều vì ở k0 AVICI dự đoán thiếu cạnh còn CDFM dự đoán thừa.
    - Khi giữ số cạnh như k0: con số gộp của AVICI gần 0 nhưng hai họ ngược chiều (tuyến tính +0.052, RFF −0.036); CDFM B kém A; FoundCause B tốt hơn A.
    - Ngưỡng NATIVE của CDFM tăng mạnh với B. Việc đổi ngưỡng góp +0.047 F1 vào B − A, nhưng ở ngưỡng cố định 0.5 thì B vẫn tốt hơn A, nên ngưỡng không phải nguyên nhân duy nhất (đính chính lần 2).
  - Câu hỏi P-N2 đặt lại theo số cạnh và thứ hạng; pilot AVICI + CDFM. Chi tiết: [`PN1_HELD_posthoc_rank_level_vi.md`](reports/n1_irrelevant_vars_2026-11-13/PN1_HELD_posthoc_rank_level_vi.md).
- **Cập nhật 20/11, review thứ hai của user; bản nháp luật P-N2 cho pha exploratory:**
  - **User chốt:** exploratory 40 hệ; held-out 80 hệ là kế hoạch ban đầu, cỡ mẫu chốt sau exploratory; biên ±1.5 cạnh cho hiệu ứng trung bình; nhánh R dùng Fisher-z cho tuyến tính, HSIC cho RFF, với Bonferroni; bộ sinh lồng nhau giữ nguyên họ RFF của AVICI.
  - **Đính chính:** phân rã theo m0 là kế toán, không phải nguyên nhân; con số gộp của AVICI che hai họ ngược chiều; ở CDFM, dấu của B − A phụ thuộc cách chọn ngưỡng.
  - **Bản nháp luật (chưa khóa):** bộ sinh đệm lồng nhau, contrast REP, L1-END, L2, 11 giả thuyết định trước, quy trình chọn α cho R trên DEV2, 11 cổng DEV. Chi tiết: [`PN2_rules_exploratory_vi.md`](reports/n2_context_mechanism_2026-11-20/PN2_rules_exploratory_vi.md).
- **Cập nhật 20/11, khóa luật P-N2 exploratory v1** (review thứ ba của user), trước khi có output P-N2 nào:
  - **α:** riêng cho Fisher-z và HSIC.
  - **k0:** không tính vào J, nhưng chất lượng tại k0 trước/sau R là bắt buộc.
  - **PC/GES:** chạy tại k0, e = 0, e = e_T, e = 3.
  - **HSIC:** dùng cho cả hai họ, chỉ để đo sàng lọc.
  - **HELD2:** tối đa 5 giả thuyết, Holm ở mức 0.05 trên p-value đã khóa.
  - **Ba chỉnh sửa:**
    - G8 kiểm quyết định tại ngưỡng Bonferroni thật, còn G9 chỉ là kiểm chẩn đoán (α_HSIC là mức danh nghĩa);
    - tách "R làm giảm thay đổi" khỏi "R sửa được lỗi";
    - giả thuyết chỉ xét theo REP, L1-END ngược dấu là "hình dạng khác dự đoán".
  - **Bước kế:** code và DEV2.
- **Cập nhật 21/11, DEV2 của P-N2 xong, đóng băng code trước EXP2:**
  - **Cổng đạt:** G1–G8 và G10 đều đạt.
    - Bộ sinh lồng nhau khớp phép tính gốc của AVICI.
    - HSIC vector hóa khớp `KCI_UInd` trên 14 580 cặp, kể cả quyết định tại các ngưỡng Bonferroni thật.
    - Kết quả tất định trùng từng bit.
  - **α chọn theo J:** Fisher-z 0.05, HSIC 0.01.
  - **G9 (chẩn đoán):** đuôi của HSIC dễ dãi, khoảng 3–4 lần mức danh nghĩa ở 0.001, nên α_HSIC chỉ là mức danh nghĩa.
  - **G11:** ước tính tự động vượt 12 giờ vì máy ngủ 7.15 giờ giữa một job. Chạy lại job đó cho output trùng từng bit; ước tính thật khoảng 2.5 giờ.
  - **Thay đổi code:** thêm lệnh giữ máy thức trong runner.
  - **Bước kế:** chờ user duyệt chạy EXP2.
  - Chi tiết: §13 của [`PN2_rules_exploratory_vi.md`](reports/n2_context_mechanism_2026-11-20/PN2_rules_exploratory_vi.md).
- **Cập nhật 21/11, EXP2 của P-N2 (exploratory, 40 hệ):** chạy dưới đóng băng `fddfadd`; kiểm hoàn tất đạt (1 440 output, 0 lỗi, mã băm input khớp, cổng đầu và cuối lượt đều `ok`).
  - **Giả thuyết:** 7/11 CONSISTENT, không có CONTRARY.
    - AVICI dự đoán ít hơn khoảng 4 cạnh ở cả hai họ (LARGE).
    - Ngưỡng của CDFM RFF tăng khoảng 0.16 (LARGE), số cạnh NATIVE giảm khoảng 15. Phân rã hậu nghiệm (mốc là ngưỡng của e = 0): phần do điểm +2.00, phần do ngưỡng −17.25. Ngưỡng là phần đóng góp lớn, nhưng điều đó chưa giải thích vì sao model đổi điểm hay đổi ngưỡng.
    - Mất thứ hạng ở RFF cho cả hai model.
  - **Không lặp lại:** pattern "AVICI tuyến tính xếp hạng tốt hơn với đệm có cấu trúc".
  - **Dạng đáp ứng:**
    - Ước lượng điểm gợi ý dạng bậc ở AVICI tuyến tính và CDFM RFF; điều này chưa được kiểm trực tiếp.
    - AVICI RFF tăng dần theo liều.
    - CDFM tuyến tính không đơn điệu (s = 0.25: +10 cạnh).
    - Ở AVICI tuyến tính, thay đổi thứ hạng chưa rõ (UNCLEAR).
  - **Nhánh R:** sàng lọc gần như luôn tách đúng khối đệm.
    - R đưa các contrast trung bình xuống dưới biên đã chọn. Điều đó không có nghĩa bất biến ở từng hệ: có một hệ CDFM đổi 7 cạnh.
    - Là cách sửa có ích ở RFF; UNCLEAR ở tuyến tính, vì giá tách chính khối đích làm F1 giảm khoảng 0.02.
  - **Mốc cổ điển:** PC bất biến, GES gần bất biến.
  - **User chốt HELD2:**
    - 5 giả thuyết: HA1, HA2, HC1, HA5, HC4.
    - 120 hệ (15 mỗi ô), chạy k0, e = 0 và e = e_T; chi phí dự trù 2–3 giờ.
    - Nhánh R là phân tích phụ.
    - p-value: kiểm trung bình một phía, sai số chuẩn theo ô thiết kế, Holm 0.05; chốt trong luật HELD2.
  - Diễn giải đã đính chính (§10 của báo cáo).
- **Cập nhật 21/11, khóa luật HELD2 của P-N2 và đóng băng code:**
  - **Luật v1:** commit `7bc8ba0`, push lúc 2026-11-21T06:28:11Z. Đây là bản nháp v0 user duyệt nguyên trạng.
  - **Phép kiểm:** năm giả thuyết REP (HA1, HA2, HC1, HA5, HC4), kiểm t một phía trên trung bình cân bằng theo ô, sai số chuẩn phân tầng, df Welch–Satterthwaite, rồi Holm 0.05. Nhánh R là phân tích phụ.
  - **Code HELD2:** toàn file mới; phụ thuộc không đổi. Code đọc kiểm trên EXP2 tái lập đúng năm ước lượng REP. Snapshot ở `code_held2/`.
  - **Bước kế:** chạy 120 hệ (dự trù 2–3 giờ), kiểm hoàn tất, rồi đọc.
  - Chi tiết: [`PN2_EXP2_results_vi.md`](reports/n2_context_mechanism_2026-11-20/PN2_EXP2_results_vi.md).

---

## 6. Quy tắc bảo trì file này

1. Mỗi lần đổi hướng hoặc qua/rớt gate quan trọng: **thêm** một dòng vào §1, một mục vào §2, và cập nhật §3 nếu có ý tưởng bị bác bỏ.
2. Không xóa hay sửa phán quyết cũ. Nếu đảo ngược, thêm mục mới ghi "đảo ngược X# vì …".
3. Mỗi dòng phải có **đường dẫn bằng chứng**. Không ghi phán quyết không có nguồn.
4. Tài liệu của hướng bị đóng chuyển vào `archive/<YYYY-MM>_<tên>/` (không xóa); cập nhật [`archive/README.md`](archive/README.md).
