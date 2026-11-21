# Snapshot nguồn của P-N2 HELD2 (đóng băng trước khi chạy, 21/11/2026)

Bản chép **để đối chiếu**, không chạy từ thư mục này.
- Code chạy thật nằm ở `artifacts/n2_runs/` (git-ignored).
- `pn2/verify_freeze_held2.py` kiểm mỗi file ở đó có cùng SHA-256 với file tương ứng ở đây. Nó cũng kiểm `common.py` của P-N1 vẫn khớp snapshot của P-N1.
- `run_held2.sh` dừng trước mọi job nếu cổng không đạt, và kiểm lại cổng khi chạy xong.
- Luật: [HELD2 v1](../PN2_rules_held2_vi.md).

Kiểm sau khi clone: `cd reports/n2_context_mechanism_2026-11-20/code_held2 && sha256sum -c SHA256SUMS`.

| Đường dẫn | Vai trò |
|---|---|
| `pn2/held2.py` | Hệ và input của HELD2 (file mới) |
| `pn2/run2_held2.py` | Runner thường và R (file mới; bản chép của `run2.py`, chỉ giới hạn danh sách job) |
| `pn2/analyze_held2.py` | Phép kiểm t phân tầng, Holm, báo cáo mô tả và nhánh R (luật HELD2 §3–§5) |
| `pn2/held2_completeness.py` | Kiểm hoàn tất bắt buộc trước khi đọc (§6) |
| `pn2/verify_freeze_held2.py`, `pn2/run_held2.sh` | Cổng đóng băng và script chạy |
| `pn2/common2.py`, `pn2/screen.py`, `pn2_out/alpha.json` | Phụ thuộc **không đổi** từ bản đóng băng `fddfadd`; mã băm trùng snapshot [`../code/`](../code/) |
