# Snapshot nguồn của P-N1 (đóng băng v2.2, 19/11/2026)

Bản chép **để đối chiếu**, không chạy từ thư mục này. `pn1/common.py` tính đường dẫn theo vị trí file (`artifacts/n1_runs/...`). Code chạy thật nằm ở `artifacts/n1_runs/` (git-ignored). `pn1/verify_freeze.py` kiểm mỗi file ở đó có cùng SHA-256 với file tương ứng ở đây, và runner held-out dừng nếu lệch.

Kiểm sau khi clone: `cd reports/n1_irrelevant_vars_2026-11-13/code && sha256sum -c SHA256SUMS`. `.gitattributes` tắt chuyển đổi xuống dòng để mã băm giữ đúng trên mọi hệ điều hành.

| Đường dẫn | Vai trò |
|---|---|
| `pn1/common.py`, `pn1/jobs.py` | Sinh hệ đích và đệm, khóa job, danh sách job theo pha (HELD theo v2.2) |
| `pn1/run_model.py`, `pn1/run_classical.py`, `pn1/fc_adapter.py` | Runner model, runner PC/GES/oracle, adapter lịch ensemble của FoundCause (vá mã `predict` lúc chạy, không chép mã) |
| `pn1/metrics.py`, `pn1/rn0.py` | Metric trên khối đích; cổng RN0 |
| `pn1/analyze_e1.py`, `pn1/analyze_e2.py`, `pn1/integrity_e2.py`, `pn1/review_e1_independent.py` | Đọc E1, E2 và các kiểm độc lập |
| `pn1/make_held_manifest.py`, `pn1/analyze_held.py`, `pn1/verify_freeze.py`, `pn1/run_heldout.ps1` | Held-out: manifest seed, đọc RN5, cổng đóng băng, script chạy |
| `pn1/power_heldout.py` | Mô phỏng khả năng đạt luật theo cỡ held-out (lý do của v2.2 §1) |
| `pn1/run_e2_all.ps1`, `pn1/run_foundcause_dev_e1.ps1` | Script đã dùng cho E2 và cho DEV + E1 của FoundCause |
| `config/*.yaml`, `config/check_configs.py`, `config/config_check.json` | Cấu hình sinh dữ liệu ER; khối cơ chế lấy từ config mẫu của AVICI (MIT License) |
| `pn1_out/held_manifest.json` | 80 hệ held-out: seed, số cạnh thật, mã băm khối đích và mã băm mọi input |
| `pn1_out/rn0_*.json` | τ và các cổng RN0 dùng khi đọc |

Không có dữ liệu, checkpoint hay output model trong thư mục này. Luật đọc: [v2](../PN1_reading_rules_vi.md), [v2.1](../PN1_rules_v2_1_amendment_vi.md), [v2.2](../PN1_rules_v2_2_amendment_vi.md).
