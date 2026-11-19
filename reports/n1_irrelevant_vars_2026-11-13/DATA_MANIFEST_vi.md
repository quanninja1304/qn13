# Manifest cho P-N1 (mô hình, checkpoint, môi trường)

> **Môi trường dùng cho pilot: bản do user dựng ngày 13/11/2026**, mô tả ở [`../direction_scan_2026-11-13/N1_cpu_setup_vi.md`](../direction_scan_2026-11-13/N1_cpu_setup_vi.md): `artifacts/n1_models_cpu/.venv` (Python 3.11.16, torch 2.15.0+cpu, JAX 0.4.38, NumPy 1.26.4, AVICI 1.0.7 với hai sửa tương thích Windows đã ghi, cdfm-base 0.1.0 editable, FoundCause qua `.pth`). Hash checkpoint và revision mã nguồn: [`n1_checkpoint_manifest.json`](../direction_scan_2026-11-13/n1_checkpoint_manifest.json), [`n1_source_revisions.json`](../direction_scan_2026-11-13/n1_source_revisions.json). Smoke test ba mô hình: PASS ([`n1_cpu_validation.json`](../direction_scan_2026-11-13/n1_cpu_validation.json)).
>
> Bản venv do agent dựng ngày 13/11 (`venv_n1`, Python 3.12) **đã xóa**: AVICI không cài được vì gói `sklearn` cũ; không dùng.

## 1. Checkpoint (theo manifest của user, đã kiểm hash)

| Model | Checkpoint | Nguồn | Ghi chú dùng trong P-N1 |
|---|---|---|---|
| AVICI | `scm-v0` (chính); `neurips-linear`, `neurips-rff`, `neurips-grn` (đã tải, chưa forward-test) | HF `larslorch/avici` | README tác giả: `scm-v0` huấn luyện "with up to 100 nodes" [Verified, README dòng 72]. Chỉ dùng checkpoint **continuous**; không dùng `neurips-grn` vì nhánh count-data chuẩn hóa theo library size toàn hàng (audit lần hai của user, §2) |
| CDFM | `model.safetensors` 38.7 MB | HF `DMIRLAB/CDFM` | Ngưỡng tự hiệu chỉnh là hàm logistic trên đặc trưng của phân phối điểm (xem `cdfm/utils.py::suggest_threshold`); phải lưu logits thô |
| FoundCause | `checkpoint.pt` 556 069 081 byte, SHA-256 `703defa1…dc04` | GitHub release `checkpoint-2026-11` | README cũ ghi 1.6 GB, không khớp; dùng số thực. Bản tải riêng của agent tại `artifacts/n1_models/foundcause/` trùng hash, giữ làm dự phòng |
| TabCausal | `checkpoints/tabcausal-base.pt` 17.7 MB (có trong clone) | GitHub `LAMDA-Tabular/TabCausal` | Clone tại `artifacts/n1_models/tabcausal/`; **chưa cài** vào môi trường (yêu cầu `numpy<2`, tương thích với env của user); quyết định dùng hay không ghi ở §8 luật đọc trước lần chạy đầu |

## 2. Không dùng

- Arrow: trọng số chưa phát hành.
- SEA: yêu cầu torch 1.13 + CUDA 11.6, inference qua script GPU.

## 3. Bài tải thêm cho audit

- `docs/papers/Aliferis_2010_JMLR_part2.pdf` (JMLR 11:235–284): §3 thêm 7 990 biến không liên quan bằng hoán vị giá trị, đo local causal discovery [Verified, đọc text trích].
