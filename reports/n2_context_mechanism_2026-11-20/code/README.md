# Snapshot nguồn của P-N2 (đóng băng trước EXP2, 21/11/2026)

Bản chép **để đối chiếu**, không chạy từ thư mục này.
- Code chạy thật nằm ở `artifacts/n2_runs/` (git-ignored) và tính đường dẫn theo vị trí file.
- `pn2/verify_freeze2.py` kiểm mỗi file ở đó có cùng SHA-256 với file tương ứng ở đây. Nó cũng kiểm `artifacts/n1_runs/pn1/common.py` của P-N1 (dùng để sinh hệ đích) vẫn khớp snapshot đã đóng băng của P-N1.
- `run_exp2.sh` dừng trước mọi job nếu cổng không đạt, và kiểm lại cổng khi chạy xong.

Kiểm sau khi clone: `cd reports/n2_context_mechanism_2026-11-20/code && sha256sum -c SHA256SUMS`. `.gitattributes` tắt chuyển đổi xuống dòng để mã băm giữ đúng trên mọi hệ điều hành.

| Đường dẫn | Vai trò |
|---|---|
| `pn2/common2.py` | Tập seed, bộ sinh khối đệm lồng nhau (luật v1 §3), ghép input |
| `pn2/screen.py` | Nhánh R: Fisher-z, HSIC (tái tạo `KCI_UInd`, đuôi bằng `gamma.sf`), Spearman, Bonferroni, BH, thành phần liên thông, chỉ số sàng lọc |
| `pn2/run2.py`, `pn2/run2_classical.py` | Runner AVICI/CDFM (input thường, nhánh R theo thành phần, chạy lại, R-oracle) và PC/GES |
| `pn2/dev2_data_gates.py`, `pn2/dev2_model_gates.py` | Cổng G1–G11 trên DEV2 và chọn α theo J |
| `pn2/analyze2.py`, `pn2/screen_variants.py` | Đọc EXP2 (luật v1 §5–§7, §10) và các biến thể chỉ đo sàng lọc (§8.2) |
| `pn2/verify_freeze2.py`, `pn2/run_dev2_models.sh`, `pn2/run_exp2.sh` | Cổng đóng băng và script chạy |
| `pn2_out/alpha.json` | α đã chọn trên DEV2: Fisher-z 0.05, HSIC 0.01 |
| `pn2_out/dev2_data_gates.json`, `pn2_out/dev2_model_gates.json` | Kết quả cổng DEV2 |

Không có dữ liệu, checkpoint hay output model trong thư mục này. Luật đọc: [v1](../PN2_rules_exploratory_vi.md); kết quả DEV2 ở §13 của luật.
