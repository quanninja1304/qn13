# Causal discovery under latent confounding — research repository

Repo gồm hai phần: (1) **quy trình và báo cáo nghiên cứu** về phương pháp cho causal discovery có biến ẩn; (2) **codebase** `safety_prior` (kill test cho scheduler-only priors, reference ICD, batch CI, frozen stable epoch).

> **Trước khi đề xuất hướng mới, đọc [`RESEARCH_HISTORY_vi.md`](RESEARCH_HISTORY_vi.md).** File này ghi mọi lần chuyển hướng, lý do, và sổ đăng ký "không làm lại".

## Trạng thái hiện tại (cập nhật 09/11/2026)

- **Không có hướng nào đang chạy.** Quy trình hiện tại là **dữ liệu trước**: tìm gap bằng cách đo failure trên dữ liệu uy tín, rồi mới đề xuất phương pháp (từ 07/11).
- **Ứng viên chính: C1, `Conditional`.** Trên Causal Chamber light tunnel (n = 10000), FCI giữ 7/21 cạnh mạnh nhưng gọi đúng 3/3 cặp confounded. BOSS giữ 21/21 cạnh nhưng không gọi cặp nào. Knock-out cho thấy nguyên nhân là phép đo dư thừa. Mới có một hệ vật lý, **chưa có cơ chế mới**. Xem [`reports/data_first_gap_2026-11-07/`](reports/data_first_gap_2026-11-07/00_data_first_gap_report_vi.md).
- **Dự phòng: C2** (chọn điểm vận hành khi không có ground truth).
- **Bước kế, chờ user quyết định:**
  - **Gate R1:** chạy BOSS-FCI, GRaSP-FCI, GFCI, FCIT trong Tetrad trên cùng dữ liệu Chamber. NO-GO đề xuất: một phương pháp đạt ≥ 19/21 cạnh mạnh **và** ≥ 2/3 cặp confounded đúng. Ngưỡng chưa được chốt.
  - Bổ sung tài liệu ưu tiên 1 theo [`PAPERS_TO_ADD_vi.md`](reports/data_first_gap_2026-11-07/PAPERS_TO_ADD_vi.md).
- **Các hướng đã đóng (chi tiết ở [`RESEARCH_HISTORY_vi.md`](RESEARCH_HISTORY_vi.md) §1, §3):**
  - **A′** (dependence-aware feature confidence): framing gốc REFUTED. Bản reformulate R1/R2 có chứng minh (RG1) và hơn Bonferroni một chút (RG3b), nhưng không có cơ chế mới → **DEPRIORITIZED** từ 06/11. Xem [`reports/aprime_review_2026-11-04/`](reports/aprime_review_2026-11-04/A1_review_handoff.md).
  - **T4 / T4-L** (selection-indexed premises dưới missing data): card gốc NO-GO; T4-L có phần toán đã biết (Didelez 2010) và pilot NO-GO → đóng 07/11. Xem [`archive/2026-11_t4_selection_indexed/`](archive/2026-11_t4_selection_indexed/T4_kill_test_vi.md).
- [`reports/current_research_status_2026-11-04_vi.md`](reports/current_research_status_2026-11-04_vi.md) và [`reports/literature_gap_2026-11-04_vi/`](reports/literature_gap_2026-11-04_vi/00_literature_matrix_and_gap_audit_vi.md) là **ảnh chụp ngày 04/11**; một phần đã bị kết quả sau thay thế.

## Bản đồ repo

| Đường dẫn | Nội dung |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Điểm vào cho research agent: mission, read order, quy tắc bắt buộc |
| [`RESEARCH_HISTORY_vi.md`](RESEARCH_HISTORY_vi.md) | Lịch sử chuyển hướng P0–P15 và do-not-redo registry (X1–X31) |
| [`research/`](research/README.md) | Protocol nghiên cứu (01–08) và `prompts/` (các prompt review theo gate) |
| [`templates/`](templates/) | Topic card, evidence matrix |
| [`reports/`](reports/README.md) | Pilot dữ liệu trước 07/11 (hiện hành), review A′ và RG1–RG3b, reassessment 03/11, ảnh chụp 04/11, và output tự sinh của code |
| [`archive/`](archive/README.md) | Hướng đã đóng/tạm dừng, giữ nguyên văn: Safe Imperfect Priors và Blockwise ICD (09–10/2026); dcFCI Direction C (10–11/2026); T4/T4-L (11/2026) |
| [`docs/papers/`](docs/papers/DOWNLOAD_STATUS_2026-11-04.md) | Corpus tài liệu. **PDF không nằm trong Git**; chỉ commit status và manifest SHA-256 |
| [`docs/background/`](docs/background/phan_biet_DAG_CPDAG_PAG_vi.md) | Giải thích nền (DAG, CPDAG, PAG) |
| [`docs/kill_test/`](docs/kill_test/03_scientific_contract.md) | Contract kill test. Giữ tại chỗ vì code tham chiếu |
| `src/`, `tests/`, `configs/`, `env/` | Package `safety_prior` cùng test, config, environment lock |
| `artifacts/` | Raw outputs (~29 GB), **không** trong Git |

## Codebase `safety_prior`

Kill test có thể tái lập, chạy offline, để kiểm tra xem một prior không hoàn hảo có lập lịch an toàn các CI query trong FCI hay không. Prior chỉ được xếp hạng query; nó không được trả lời CI query, cũng không được sửa hay định hướng cạnh. Contract khoa học đóng băng ở [`docs/kill_test/03_scientific_contract.md`](docs/kill_test/03_scientific_contract.md).

```text
python -m pip install -e .[test]
pytest
python -m safety_prior.cli --help
```

Audit gate của Certified Blockwise ICD: `batch-ci-audit`, `icd-reference-audit`, `stable-epoch-audit` (G2). Output nằm ở `reports/algorithm_sprints/`.

Chuyển từ Windows sang Linux: xem [`docs/kill_test/vps_migration.md`](docs/kill_test/vps_migration.md).

```text
python -m safety_prior.cli migration-prepare
python -m safety_prior.cli migration-validate
```
