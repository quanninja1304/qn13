# Snapshot nguồn của pilot P-N3 (đóng băng trước khi chạy, 21/11/2026)

Bản chép **để đối chiếu**, không chạy từ thư mục này.

- Code chạy thật nằm ở `artifacts/n3_runs/` (git-ignored).
- `pn3/verify_freeze_pn3.py` kiểm mỗi file ở đó có cùng SHA-256 với file ở đây. Nó cũng kiểm hai phụ thuộc đã đóng băng: `common2.py` của P-N2 và `common.py` của P-N1.
- Luật: [P-N3 v1](../PN3_rules_pilot_vi.md).

| Đường dẫn | Vai trò |
|---|---|
| `pn3/avici_patch.py` | Subclass `MultiHeadAttention` (chép nguyên văn Haiku 0.0.13), can thiệp V0/KO, xác định lớp theo chỉ số khối, chốt chặn trace cũ |
| `pn3/partB_gates.py`, `pn3_out/partB_gates.json` | Gate B0–B5 và kết quả (đều đạt) |
| `pn3/partA_cdfm.py` | Phần A: giai thừa 2³ trên đầu vào bộ chọn ngưỡng của CDFM, Shapley, chính sách ngưỡng cục bộ, gate A0 |
| `pn3/partB_run.py`, `pn3/partB_run_configs.py` | Phần B: 19 cấu hình × 40 input, so mọi PLAIN với output P-N2 |
| `pn3/partB_analyze.py` | Đọc Phần B: θ có dấu, chênh lệch ghép cặp, a_I với bootstrap ghép cặp, cờ suy giảm, phân loại |
| `pn3/verify_freeze_pn3.py`, `pn3/run_pn3.sh` | Cổng đóng băng và script chạy |
