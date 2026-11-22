# P-N5: phân rã thăm dò mức đổi số cạnh NATIVE của CDFM (EXPLORATORY, 22/11/2026)

> **Nhãn: EXPLORATORY.**
>
> - Tính sau khi đã xem kết quả P-N5, theo yêu cầu của user. Không thuộc luật đã khóa và không có kiểm soát đa kiểm định.
> - Không chạy model mới; chỉ đọc output CDFM đã lưu của lượt chạy dưới đóng băng `b1a9f29`.
> - User tính nhanh các số chính trước. Agent tính lại bằng một script riêng và ra cùng số.
>
> **Script:** [`posthoc/decomp_pn5.py`](posthoc/decomp_pn5.py). **Output:** [`posthoc/decomp_output.json`](posthoc/decomp_output.json), gồm giá trị theo từng lần sinh, và [`posthoc/decomp_output.txt`](posthoc/decomp_output.txt).
> **Kết quả đã xác nhận:** [P-N5](PN5_results_vi.md). Phạm vi xác nhận của P-N4 (C5) giữ nguyên.

## 1. Định nghĩa

- **Quy tắc đếm m(A, τ),** như P-N4 (luật PN4 §2): số cặp không thứ tự của khối thật (55 cặp) có max(A_ij, A_ji) > τ, bỏ đường chéo.
  - Quy tắc này tái lập đúng ma trận kề NATIVE đã lưu ở cả 164 output CDFM của P-N5, với 0 lệch, trên toàn ma trận và trên skeleton của khối thật.
  - Vì vậy T + S đúng bằng mức đổi số cạnh NATIVE.
- **Phép so:** trong mỗi lần sinh r, ở cùng k, so đệm có cấu trúc (s, e = 2) với đệm Gauss (g, e = 0).
  - **Mốc e = 0** (như P-N4):
    - phần do điểm S = m(P_s, τ_g) − m(P_g, τ_g);
    - phần do ngưỡng T = m(P_s, τ_s) − m(P_s, τ_g).
  - **Mốc đảo** (ngưỡng ở e = 2):
    - S′ = m(P_s, τ_s) − m(P_g, τ_s);
    - T′ = m(P_g, τ_s) − m(P_g, τ_g).
  - Theo định nghĩa, T + S = T′ + S′ = mức đổi số cạnh NATIVE.
- Trung bình qua 20 lần sinh, với CI 95% theo t (df 19), có điều kiện trên bảng đã cố định.
- **Đây là phân rã kế toán phụ thuộc mốc, chưa phải hai nguyên nhân tách biệt.**

## 2. Kết quả, mốc e = 0

| Bảng | k | T (ngưỡng) [CI 95%] | S (điểm) [CI 95%] | T + S [CI 95%] | T − S [CI 95%] | Lần sinh có T_r < −\|S_r\| |
|---|---|---|---|---|---|---|
| Sachs | 20 | +0.55 [−0.89, +1.99] | −0.50 [−2.03, +1.03] | +0.05 [−1.74, +1.84] | +1.05 [−1.32, +3.42] | 15% |
| Sachs | 40 | −10.45 [−13.96, −6.94] | +10.95 [+7.28, +14.62] | +0.50 [−1.34, +2.34] | −21.40 [−28.34, −14.46] | 35% |
| Wine | 20 | −19.70 [−21.58, −17.82] | +0.60 [−2.93, +4.13] | −19.10 [−23.21, −14.99] | −20.30 [−24.18, −16.42] | 100% |
| Wine | 40 | −23.85 [−26.25, −21.45] | +6.45 [+4.15, +8.75] | −17.40 [−20.99, −13.81] | −30.30 [−33.34, −27.26] | 95% |

## 3. Độ nhạy theo mốc

| Bảng | k | T′ (ngưỡng, mốc đảo) [CI 95%] | S′ (điểm, mốc đảo) [CI 95%] |
|---|---|---|---|
| Sachs | 20 | +0.00 [−0.26, +0.26] | +0.05 [−1.76, +1.86] |
| Sachs | 40 | −0.45 [−0.89, −0.01] | +0.95 [−0.78, +2.68] |
| Wine | 20 | −19.45 [−22.38, −16.52] | +0.35 [−2.81, +3.51] |
| Wine | 40 | −21.60 [−23.41, −19.79] | +4.20 [+0.93, +7.47] |

## 4. Đọc (thăm dò)

- **Wine:**
  - Ở cả hai k, phần do ngưỡng âm và lớn hơn hẳn độ lớn phần do điểm. Hai mốc cho T gần nhau: −19.70 so với −19.45 ở k = 20, và −23.85 so với −21.60 ở k = 40.
  - Ở mốc e = 0, mẫu hình của tiêu chí (c) trong C5 đều thỏa: CI của T nằm dưới −1.5, CI của T + S và của T − S nằm dưới 0.
  - Vậy Wine phù hợp với mẫu hình C5, ở mức thăm dò.
  - Ước lượng điểm ở Wine gần P-N4 trên dữ liệu tổng hợp (T −19.24 ở k = 20, −26.04 ở k = 40). Hai thiết kế khác nhau về khối đích, d_T và e, và không có phép kiểm so sánh.
- **Sachs, k = 40:**
  - Số cạnh NATIVE gần như giữ nguyên (T + S = +0.50), nhưng điều đó không có nghĩa là ngưỡng ít ảnh hưởng. Theo mốc e = 0, T = −10.45 và S = +10.95 bù nhau.
  - Tiêu chí (c) không thỏa, vì CI của T + S chứa 0.
- **Sachs, k = 20:** cả hai phần nhỏ, CI chứa 0. Điều này khớp với việc ngưỡng gần như không đổi giữa hai kiểu đệm (P5-2S-20 NOT_CONFIRMED).
- **Vì sao hai mốc khác nhau ở Sachs k = 40** (đọc trực tiếp từ định nghĩa):
  - Ở ô này, τ_s > τ_g ở cả 20 lần sinh. Vì vậy |T| là số cặp mà điểm *với đệm có cấu trúc* nằm trong khoảng (τ_g, τ_s], trung bình 10.45 cặp. |T′| là số cặp mà điểm *với đệm Gauss* nằm trong cùng khoảng đó, trung bình 0.45 cặp.
  - Như vậy, đệm có cấu trúc vừa đẩy điểm của khoảng 10 cặp lên khoảng này, vừa nâng ngưỡng vượt qua chúng.
  - Hai thay đổi này tương tác, nên mức đổi không chia duy nhất được cho điểm hay cho ngưỡng. Ở Wine, tương tác này nhỏ.

## 5. Không được viết

- "Ngưỡng gây ra mất X cạnh" hay "điểm gây ra thêm Y cạnh" như hai nguyên nhân tách biệt.
- "C5 được xác nhận trên dữ liệu thật." Đây là kết quả thăm dò; phạm vi xác nhận của P-N4 giữ nguyên.
- "Ở Sachs, ngưỡng không ảnh hưởng tới quyết định." Ở k = 40, theo mốc e = 0, phần do ngưỡng là −10.45.
- Khái quát sang bảng khác, cách chọn hàng khác hay cách tiền xử lý khác.
- Bất kỳ điều gì về độ chính xác.

## 6. Ý nghĩa cho bảng claim

- **C5:** thêm kết quả này ở mức EXPLORATORY. Wine phù hợp với mẫu hình C5 ở cả hai mốc. Ở Sachs k = 40, hai phần bù nhau theo mốc e = 0 và phụ thuộc mạnh vào mốc.
- Muốn xác nhận trên dữ liệu thật thì cần dữ liệu chưa xem (bảng mới, hoặc cách chọn hàng mới) và luật khóa trước. Bước này chưa có trong kế hoạch; user quyết.
