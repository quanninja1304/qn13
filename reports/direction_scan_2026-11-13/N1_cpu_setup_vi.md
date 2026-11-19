# Môi trường CPU và checkpoint N1 — đã kiểm tra hoạt động

Ngày 13/11/2026. **Cài đặt hoàn tất; ba mô hình đã nạp trọng số và chạy một forward pass nhỏ trên CPU. Chưa chạy pilot N1 hoặc P-C1a.**

## 1. Vị trí sử dụng

Môi trường độc lập, không thay môi trường `.venv` cũ của repo:

```text
artifacts/n1_models_cpu/
  .venv/Scripts/python.exe
  repos/avici/
  repos/CDFM/
  repos/foundcause/
  checkpoints/avici/scm-v0/
  checkpoints/avici/neurips-linear/
  checkpoints/avici/neurips-rff/
  checkpoints/avici/neurips-grn/
  checkpoints/cdfm/
  checkpoints/foundcause/checkpoint.pt
  logs/
  checkpoint_manifest.json
  source_revisions.json
```

Chạy từ root repo bằng PowerShell:

```powershell
& '.\artifacts\n1_models_cpu\.venv\Scripts\python.exe' -X utf8 '.\reports\direction_scan_2026-11-13\smoke_n1_cpu.py' imports
```

Thay `imports` bằng `avici`, `cdfm` hoặc `foundcause` để kiểm riêng. Các lượt kiểm chạy tuần tự, giới hạn hai CPU threads ở nơi API cho phép. Script khóa CPU và dùng checkpoint local, không tự tải model khác.

## 2. Phiên bản đã cài

| Thành phần | Phiên bản/ghi chú |
|---|---|
| Python | 3.11.16; AVICI hiện yêu cầu Python <3.12 |
| JAX / jaxlib | 0.4.38 / 0.4.38; device được kiểm `TFRT_CPU_0` |
| PyTorch | **2.15.0+cpu**, lấy từ index CPU chính thức; `torch.version.cuda is None` |
| NumPy | 1.26.4, tương thích constraint `numpy<2` của AVICI |
| AVICI | 1.0.7, editable từ repo tác giả, có hai compatibility fixes bên dưới |
| CDFM | `cdfm-base==0.1.0`, editable từ repo tác giả |
| FoundCause | Module từ repo tác giả, đăng ký bằng `.pth` trong môi trường riêng; có thể `import foundcause` |
| Haiku / Optax | 0.0.13 / 0.2.4 |
| Các gói phụ | safetensors, huggingface-hub, scipy, pandas, scikit-learn, schedulefree, causal-learn và dependencies AVICI |
| TensorFlow | 2.18.0 và các gói được AVICI khai báo; không được dùng làm backend inference của ba model trong smoke test |

`uv pip check` đạt: **182 packages, không có xung đột dependency được metadata phát hiện**. Điều này không xác nhận mọi training API của các package đều hoạt động. Bản freeze đầy đủ: [n1_cpu_requirements_lock.txt](n1_cpu_requirements_lock.txt).

## 3. Checkpoint, nguồn và dung lượng

| Model | Nội dung | Byte tải về, gồm config nhỏ | Nguồn chính thức |
|---|---|---:|---|
| AVICI | `scm-v0` và cả ba `neurips-*` | 273.548.070 | [larslorch/avici](https://huggingface.co/larslorch/avici) |
| CDFM | `model.safetensors`, config, model card | 38.713.536 | [DMIRLAB/CDFM](https://huggingface.co/DMIRLAB/CDFM) |
| FoundCause | `checkpoint.pt`, release **checkpoint-2026-11** | 556.069.081 | [GitHub release](https://github.com/amazon-science/foundcause/releases/tag/checkpoint-2026-11) |
| **Tổng checkpoint** | | **868.330.687 byte ≈ 868 MB / 828 MiB** | |

Con số FoundCause 1,6 GB trong README cũ không khớp asset release hiện tại; đã dùng số byte thực và digest do GitHub trả. Toàn thư mục gồm môi trường và mã nguồn khoảng **3,95 GB** sau cài đặt; không bao gồm cache tải package của uv ở vị trí mặc định.

Đã đối chiếu kích thước file và SHA-256 LFS do Hugging Face cung cấp cho các trọng số; FoundCause khớp publisher SHA-256 `703defa18043514873fe2a487f6b4498c0492a978c77bba1376f4e02f31edc04`. Các JSON/config cũng có hash cục bộ trong manifest.

- [Manifest checkpoint và hash](n1_checkpoint_manifest.json).
- [Revision ba kho mã](n1_source_revisions.json).
- [Script tải từ URL cố định](download_n1_checkpoints.py).

Source revisions: AVICI `40fb30de976b4264627b3c32996e4d059130aa4e`; CDFM `996816049ac5d36fc85e3c2b501509cbd8bc3d7f`; FoundCause `d937cbfcb1db7af64251dbc20424836a457e6f46`. Không dùng nhãn `latest` như một định danh tái lập.

## 4. Kết quả kiểm tra môi trường

Dữ liệu smoke là mảng ngẫu nhiên **32 dòng × 3 biến**, seed cố định. Chỉ kiểm nạp model, shape và giá trị hữu hạn, không chấm causal accuracy.

| Check | Trạng thái | Thời gian một lượt, gồm import/load | Kết quả |
|---|---|---:|---|
| Imports/backend | PASS sau compatibility patch | 22,2 giây | JAX CPU, torch CPU, import avici/cdfm/causal-learn |
| AVICI `scm-v0` | PASS | 10,6 giây | Output 3×3 hữu hạn |
| CDFM | PASS | 6,0 giây | Output 3×3 hữu hạn, manual threshold=0,5 |
| FoundCause | PASS | 24,4 giây | 138.986.803 parameters, output 3×3 hữu hạn, một permutation run |

Log JSON: `artifacts/n1_models_cpu/logs/smoke_{imports,avici,cdfm,foundcause}.json`; bản tổng hợp được lưu tại [n1_cpu_validation.json](n1_cpu_validation.json). Thời gian này không phải benchmark so tốc độ: mỗi model có preprocessing, compilation và API khác nhau.

FoundCause dùng `torch.load(weights_only=True, mmap=True)` và tạo module trên `meta` trước `load_state_dict(assign=True)`, tránh cấp phát thêm một bản tham số. Không đổi trọng số hay phép forward. RSS cuối lượt FoundCause khoảng 889 MB; **đây không phải peak RAM**. Lúc bắt đầu máy chỉ còn khoảng 0,6 GB RAM trống; không suy từ smoke nhỏ rằng n=1000, d=60 chắc chắn đủ RAM. Trước pilot cần resource check ở cấu hình dự kiến, từng model một.

Chỉ `scm-v0` của AVICI đã forward-test; ba checkpoint `neurips-*` đã tải và kiểm hash, chưa forward-test riêng. Không kết luận training hoặc async data pipeline hoạt động trên Windows.

## 5. Hai sửa tương thích AVICI được ghi rõ

1. **Plasma:** AVICI import bộ đệm huấn luyện ngay khi import package; wheel PyArrow Windows thiếu `pyarrow._plasma`. Đã đổi import thành optional có thông báo lỗi rõ khi thực sự gọi async Plasma buffer. Inference và synchronous sampling không cần bộ đệm ấy. Lỗi trước sửa được giữ trong `logs/smoke_imports_before_patch.json`.
2. **Local config path:** assertion của `load_pretrained(checkpoint_dir=...)` kiểm nhầm `kwargs.json` ở thư mục cha, trong khi loader đọc config ngay tại checkpoint directory. Đã sửa assertion cho khớp loader.

Không sửa attention, normalization, decoder hay weights. [Script áp sửa](patch_avici_windows.py) và [patch chính xác](avici_windows_compat.patch) được lưu để kiểm lại. Bản sửa nằm trong source copy ở `artifacts/`, không sửa code nghiên cứu chính của repo.

## 6. Cách tái lập cài đặt

Các source checkout phải ở ba revision ghi trong manifest; script dưới giả định đã clone chúng vào đúng `artifacts/n1_models_cpu/repos/`. Không reset hoặc ghi đè checkout có sửa đổi để tái lập.

```powershell
uv venv --python 3.11 artifacts/n1_models_cpu/.venv
uv pip install --python artifacts/n1_models_cpu/.venv/Scripts/python.exe 'torch==2.15.0+cpu' --index-url https://download.pytorch.org/whl/cpu
uv pip install --python artifacts/n1_models_cpu/.venv/Scripts/python.exe -r reports/direction_scan_2026-11-13/n1_cpu_requirements_lock.txt
python -X utf8 reports/direction_scan_2026-11-13/patch_avici_windows.py
python -X utf8 reports/direction_scan_2026-11-13/download_n1_checkpoints.py
```

Script download cần `requests` trong Python chạy nó; môi trường model đã có gói này. Trên máy hiện tại đăng ký FoundCause bằng file `artifacts/n1_models_cpu/.venv/Lib/site-packages/n1_foundcause.pth` chứa đường dẫn tuyệt đối tới source repo. Khi chuyển workspace, cập nhật `.pth` này; script smoke cũng tự thêm đường dẫn source từ root repo.

## 7. Trước pilot khoa học

- Dùng [audit lần hai](N1_prior_art_second_audit_vi.md), đặc biệt raw scores vs adaptive threshold, assumptions của classical baseline và count normalization của AVICI GRN.
- [Luật đọc P-C1a](P_C1a_reading_rules_vi.md) đã viết độc lập. Các gate oracle/adjustment verifier trong tài liệu chưa chạy.
- Chưa có pilot results, chưa freeze protocol P-N1 đầy đủ, chưa cài R/Java và chưa huấn luyện/fine-tune model. Setup thành công chỉ xác nhận đường nạp trọng số và inference CPU nhỏ hoạt động.
