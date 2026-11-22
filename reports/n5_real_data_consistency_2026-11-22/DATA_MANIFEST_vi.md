# P-N5 (gap 2): manifest dữ liệu thật (22/11/2026)

> **Mục đích:** ghi nguồn, giấy phép, mã băm và cấu trúc của hai bảng dữ liệu thật mà user đã chọn cho gap 2, trước khi viết luật và trước khi chạy bất kỳ model nào.
> **Lưu trữ:** dữ liệu nằm trong `artifacts/data_real/` (git-ignored) và **không bao giờ được commit**. Repo chỉ giữ manifest này và [`manifest/data_manifest.json`](manifest/data_manifest.json); cả hai được sinh từ [`manifest/make_data_manifest.py`](manifest/make_data_manifest.py).
> **Cách tải:** `curl` từ URL chính thức, không dùng tài khoản; ngày 22/11/2026. Mỗi archive nằm trong một thư mục mới, và chỉ file cần dùng được giải nén, sang một thư mục riêng.
> **Chưa có output model nào** trên hai bảng này.

## 1. Sachs, điều kiện CD3/CD28 (bảng chính)

| Mục | Giá trị |
|---|---|
| Nguồn | Zenodo, [bản ghi 7681811](https://zenodo.org/records/7681811), DOI `10.5281/zenodo.7681811` (concept DOI `10.5281/zenodo.7679091`) |
| Tên, tác giả bản phát hành | "Sachs: Protein and Phospholipids Expressions", Mathematical Research Data Initiative (MaRDI); phát hành 26/02/2023 |
| Giấy phép | CC BY 4.0 (metadata của Zenodo) |
| Dẫn xuất từ | Sachs et al., *Science* 2005, DOI `10.1126/science.1105809` |
| Archive | `sachs.zip`, 454 496 byte; md5 `d50ccd7f88bb3705bcf6eda3978bcc41`, **khớp md5 do Zenodo công bố**; SHA-256 `42d3c5eef7804ce065dec7e16edebb606e0e5b4ae6298310e55e1ca053b959b2` |
| File dùng | `Data Files/cd3cd28.csv`, 44 448 byte, SHA-256 `07087f7020995980f998b6683a85bb974b6e129cd4ce3a8cd55633ab79b814d0` |
| Cấu trúc | **853 hàng × 11 biến**: Raf, Mek, Plcg, PIP2, PIP3, Erk, Akt, PKA, PKC, P38, Jnk |
| Đặc điểm | Không thiếu giá trị; mọi giá trị ≥ 1; đuôi nặng (giá trị lớn nhất tới 4 491); không có hàng trùng |
| Không dùng | 13 file điều kiện khác, `GroundTruth.csv` và các file mô tả; không giải nén |

**Về `GroundTruth.csv`:** archive có kèm một đồ thị tham chiếu. Gap 2 đo độ bất ổn, không đo độ chính xác, nên file này không được dùng. Mạng tham chiếu của Sachs cũng còn bị tranh luận.

## 2. UCI Wine Quality, rượu trắng (bảng bổ trợ)

| Mục | Giá trị |
|---|---|
| Nguồn | UCI Machine Learning Repository, [dataset 186](https://archive.ics.uci.edu/dataset/186/wine+quality), DOI `10.24432/C56S3T` |
| Tác giả | Paulo Cortez, A. Cerdeira, F. Almeida, T. Matos, J. Reis; bài giới thiệu: Cortez et al., *Decision Support Systems*, 2009 |
| Giấy phép | CC BY 4.0 (trang dataset) |
| Archive | `wine_quality.zip`, 91 353 byte; SHA-256 `3ed56667f4b828242bd732d7d1dd7f2861e54432239d7fa63877014cbb0304d4`. UCI không công bố checksum; mã băm do agent tính khi tải |
| File dùng | `winequality-white.csv`, 264 426 byte, SHA-256 `76c3f809815c17c07212622f776311faeb31e87610d52c26d87d6e361b169836` |
| Cấu trúc | 4 898 hàng × 12 cột, phân cách bằng `;`. **Dùng 11 biến lý–hóa**, bỏ cột `quality` |
| Đặc điểm | Không thiếu giá trị. `citric acid` có giá trị 0. **937 hàng trùng hoàn toàn với một hàng khác** (trên cả 11 biến dùng) |
| Không dùng | `winequality-red.csv`, `winequality.names`; không giải nén |

## 3. Quy tắc dùng về sau

- Mọi script đọc dữ liệu phải kiểm SHA-256 của file dùng so với manifest trước khi đọc.
- Script đọc dữ liệu chạy bằng `python -I` và nằm ngoài thư mục dữ liệu.
- Cách chọn 500 hàng và tiền xử lý được khóa trong luật P-N5, trước khi có output model nào.
- Không dùng đồ thị tham chiếu nào làm đáp án đúng.
