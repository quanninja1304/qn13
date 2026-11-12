# Hồ sơ dữ liệu: TS-G1 (09/11/2026)

Dữ liệu thô nằm ở `artifacts/ts_causalrivers/` (không đưa vào Git; `/artifacts/` đã có trong `.gitignore`). User cho phép tải ngày 09/11.

| Dữ liệu | Nguồn | Kiểm tra | Ghi chú |
|---|---|---|---|
| CausalRivers `product.zip` (release `First_release`, 19/02/2025) | `https://api.github.com/repos/CausalRivers/causalrivers/releases/assets/230648753`. Link tải trực tiếp trong README trả 504, nên tải qua API asset, có ngắt giữa chừng và tải tiếp bằng `curl -C -` | 133 228 548 byte; SHA-256 `4f779fa9222653af092046eacba39a955cc65638bfb70fb7e31a32d9d8373b55`; `zipfile.testzip()` không báo lỗi | Giải nén một phần vào `artifacts/ts_causalrivers/product/`: các file East Germany (`.p`, `ts`, `meta`), cộng `rivers_flood.p` và `rivers_bavaria.p` |
| Graph `.p` | Pickle của networkx | Đọc bằng `SafeUnpickler` trong `P0_descriptive.py`, chỉ cho phép lớp của networkx, builtins và numpy | East Germany: 666 nút, 651 cạnh. **Thuộc tính `p` là (vĩ độ, kinh độ)**, ngược với README (README ghi X là kinh độ) |
| DWD, danh sách trạm mưa theo giờ | `opendata.dwd.de/.../hourly/precipitation/historical/RR_Stundenwerte_Beschreibung_Stationen.txt` | 1861 dòng | Điều khoản: "Frei" |
| DWD, danh sách trạm mưa theo ngày | `opendata.dwd.de/.../daily/more_precip/historical/RR_Tageswerte_Beschreibung_Stationen.txt` | 6632 dòng | Chưa dùng |
| DWD, chuỗi mưa theo giờ | **Chưa tải.** Chỉ tải các trạm cần dùng, sau khi luật đọc được duyệt | — | — |

**Code tham chiếu** (chỉ đọc, không chạy): CausalRivers HEAD và CausalRivers/experiments HEAD, đọc ngày 09/11/2026 qua GitHub API. `select_confounder_samples` không loại nút confounder từ commit `f377e45` trở đi.

**Môi trường:** Python 3.14 (`C:\Python314`), networkx 3.6.1, pandas 3.0.5, numpy 2.5.2, statsmodels 0.15.0. `tigramite` chưa cài.
