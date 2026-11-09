# Hồ sơ dữ liệu và cách chạy lại

Dữ liệu thô ở `artifacts/data_first_gap/` (không nằm trong Git). Chạy với biến môi trường `GAP_DATA` trỏ tới thư mục đó, ví dụ trong Bash: `GAP_DATA="$PWD/artifacts/data_first_gap" python -P -E reports/data_first_gap_2026-11-07/E2_graph_level_real_data.py`. Nếu không đặt, script tìm ở `%TEMP%\gap_work\data`.

| Dữ liệu | Nguồn | Kiểm tra | Ghi chú |
|---|---|---|---|
| Causal Chamber `lt_interventions_standard_v1` | `https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/lt_interventions_standard_v1.zip` | MD5 `476664d024f88e8b7640998bb5e9ee33`, khớp `directory.yaml` | CC BY 4.0 theo repo của tác giả. `uniform_reference.csv` gồm 10000 hàng |
| Ground truth Chamber | `causalchamber` 0.2.8, `ground_truth/main.py`, parse bằng `ast.literal_eval`, không chạy code gói | `causal_chamber_ground_truth_edges.json` | Cạnh nghĩa là hiệu ứng can thiệp; thiếu cạnh không loại trừ hiệu ứng (Gamella et al. §3.1) |
| Sachs `cyto_full_data.csv` | CausalDiscoveryToolbox, `cdt/data/resources/` | 7466 hàng, 11 biến | Không có cột điều kiện. Thứ tự điều kiện suy từ cỡ mẫu, **chưa xác minh** |
| Sachs consensus | CausalDiscoveryToolbox, `cyto_full_target.csv` | `sachs_consensus_edges.json`, 18 cạnh có chu trình | Bị tranh cãi như ground truth |
| Wind tunnel `wt_test_v1`, `wt_bernoulli_v1`, `wt_validate_v1`; `lt_test_v1` | Cùng nguồn S3, MD5 khớp | Chỉ kiểm tra cấu trúc, **chưa dùng** | Actuator tự tương quan rất cao, không hợp test i.i.d. Tải lại khi cần |

**Môi trường:** Python 3.14, `causal-learn` 0.1.4.8, `scikit-learn` 1.9.1, `numpy` 2.5.2, `scipy` 1.18.1, `pandas` 3.0.5, Windows, 7.8 GB RAM, chạy một luồng BLAS.

**Script và output**

| Script | Nội dung | Output | Trạng thái |
|---|---|---|---|
| `E1_ci_calibration_chamber.py` | Hiệu chỉnh test CI, L1 | `E1_outputs.json`, `E1_run_log.txt` | Xong |
| `E1b_gcm_control.py` | Đối chứng GCM, L6 | `E1b_outputs.json`, `E1b_run_log.txt` | Xong |
| `E2_graph_level_real_data.py`, `E2_analysis.py` | Thuật toán theo n, L2 | `E2_results.jsonl`, `E2_summary.json` | Xong |
| `E2b_edge_anatomy.py` | Giải phẫu lỗi | `E2b_outputs.json` | Xong, mô tả |
| `E3_internal_scores.py`, `E3_analysis.py` | Điểm nội bộ, L3 | `E3_results.jsonl`, `E3_summary.json` | **Chamber xong; Sachs dở** do bị dừng vì thiếu RAM. Chạy lại lệnh cũ sẽ tiếp tục từ chỗ dừng |
| `E5_latent_aware_chamber.py` | Nhãn sensor–sensor | `E5_outputs.json` | Xong, mô tả |
| `E6_knockout_attribution.py` | Knock-out, L5 | `E6_results.json`, `E6_summary.json` | Xong |
| `E7_audited_scoring.py` | Chấm lại | `E7_outputs.json` | Xong, post hoc |
| `E8_pc_strong_edge_loss.py` | Vì sao mất cạnh mạnh | `E8_outputs.json`, `E8b_outputs.json` | Xong, post hoc. `E8b` chạy bằng script tạm, kết quả ở `E8b_run_log.txt` |
