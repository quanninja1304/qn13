# Causal discovery under latent confounding — research repository

Repo gồm hai phần: (1) **quy trình và báo cáo nghiên cứu** về phương pháp cho causal discovery có biến ẩn; (2) **codebase** `safety_prior` (kill test cho scheduler-only priors, reference ICD, batch CI, frozen stable epoch).

> **Trước khi đề xuất hướng mới, đọc [`RESEARCH_HISTORY_vi.md`](RESEARCH_HISTORY_vi.md).** File này ghi mọi lần chuyển hướng, lý do, và sổ đăng ký "không làm lại".

## Trạng thái hiện tại (04/11/2026)

- **Hướng đang theo đuổi:** A′ đã reformulate. R1 chứng nhận đồng thời ancestral features cho MAG có latent, từ vector CI statistics. R2 là η-profile. Framing gốc của A′ đã bị bác bỏ.
- **Gate tiếp theo:** RG1 (chứng minh) và RG2 (kill test power). Xem [`reports/aprime_review_2026-11-04/A1_review_handoff.md`](reports/aprime_review_2026-11-04/A1_review_handoff.md).
- **Backup:** T4. Xem [topic card](reports/reassessment_2026-11-03_vi/topic_cards/T4_selection_indexed_premises_missingness_vi.md).

## Bản đồ repo

| Đường dẫn | Nội dung |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Điểm vào cho research agent: mission, read order, quy tắc bắt buộc |
| [`RESEARCH_HISTORY_vi.md`](RESEARCH_HISTORY_vi.md) | Lịch sử chuyển hướng P0–P6 và do-not-redo registry |
| [`research/`](research/README.md) | Protocol nghiên cứu (01–08) và `prompts/` (các prompt review theo gate) |
| [`templates/`](templates/) | Topic card, evidence matrix |
| [`reports/`](reports/README.md) | Báo cáo hiện hành (reassessment 03/11, review A′ 04/11) và output tự sinh của code |
| [`archive/`](archive/README.md) | Hướng đã đóng/tạm dừng, giữ nguyên văn: Safe Imperfect Priors và Blockwise ICD (09–10/2026); dcFCI Direction C (10–11/2026) |
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
