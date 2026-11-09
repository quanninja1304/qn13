# Archive — các hướng nghiên cứu đã đóng hoặc tạm dừng

Tài liệu trong thư mục này được **giữ nguyên văn**, không xóa. Phán quyết, lý do và điều kiện mở lại nằm ở [`../RESEARCH_HISTORY_vi.md`](../RESEARCH_HISTORY_vi.md). Đọc file đó trước khi dùng lại bất cứ thứ gì ở đây.

| Thư mục | Giai đoạn | Trạng thái | Nội dung |
|---|---|---|---|
| [`2026-09_safe_imperfect_priors/`](2026-09_safe_imperfect_priors/) | 18/09 – 21/10/2026 | Kill test K0 PASS, K1 PASS (decision), K2–K4 NOT_RUN. Certified Blockwise ICD: **PAUSED** | `proposal/` đề cương 01/02/02a · `handoff/` bàn giao 01–15 (kill test, portfolio, Sprint 0, C0–C2) · `research_notes/` portfolio 4 vòng, OP-PDS, block-ICD contracts, Sprint-0 semantics · `reports/` checkpoint 19/10 (kèm figures), dossier, amendment, addendum A-001 |
| [`2026-10_dcfci_direction_c/`](2026-10_dcfci_direction_c/) | 30/10 – 03/11/2026 | **SUBSUMED / DEPRIORITIZED** (reset 03/11) | Review literature/gap 30/10 (ứng viên A/B/C), đặc tả dcFCI pruning T1–T3, đánh giá phê bình Hướng C (D1–D4) |
| [`2026-11_t4_selection_indexed/`](2026-11_t4_selection_indexed/) | 06/11 – 07/11/2026 | T4 theo card gốc **NO-GO**; T4-L **REFUTED** theo framing đã thử (X27, X29), phần toán **SUBSUMED** (X26) | Kill test, audit văn liệu, pilot mức thuật toán và chẩn đoán; script, log, số liệu. Card T4 vẫn ở `reports/reassessment_2026-11-03_vi/topic_cards/` |

## Những gì **không** chuyển vào archive (vì code phụ thuộc đường dẫn)

| Đường dẫn | Lý do giữ nguyên |
|---|---|
| `src/`, `tests/` | Package Python `safety_prior` đang chạy được |
| `configs/kill_test/`, `configs/tensorized_icd/` | `src/safety_prior/*.py` đọc trực tiếp |
| `env/` | Manifest delta-handoff tham chiếu |
| `docs/kill_test/` | `delta_handoff.py` tham chiếu `docs/kill_test/windows_i9_delta_handoff.md` |
| `reports/kill_test/`, `reports/algorithm_sprints/` | Output của runner và các audit CLI |
| `artifacts/` | Raw outputs (~29 GB), không nằm trong Git |
