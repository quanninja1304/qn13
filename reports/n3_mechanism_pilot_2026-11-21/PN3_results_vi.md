# P-N3: kết quả pilot cơ chế (exploratory, EXP2, 21/11/2026)

> **Luật:** [P-N3 v1](PN3_rules_pilot_vi.md), khóa ở commit `8d1df20` (push lúc 08:41:52Z). Code đóng băng ở `7fbd635` (push lúc 08:53:33Z).
> **Chạy:** từ 08:54:42 đến 10:09:08 UTC ngày 21/11. Phần A mất vài giây; Phần B mất 4 448 giây.
> **Hoàn tất** (kiểm trước khi đọc):
>
> - cổng `pn3_start` và `pn3_end` đều đạt;
> - Phần B có 760/760 output, 0 lỗi; 40/40 output PLAIN trùng từng bit với output P-N2;
> - đúng 38 lần trace đầu (19 cấu hình × 2 hình dạng), không lần nào trace lại;
> - gate A0 đạt (sai lệch 3.3e-16).
>
> **Nhãn:** mọi kết quả là **exploratory**; CI 95% theo t với sai số chuẩn phân tầng, 20 hệ mỗi phần. Diễn giải là suy luận.

## 1. Phần A: CDFM RFF, bộ chọn ngưỡng

**Chênh logit ngưỡng hai đầu**, từ e = 0 sang e = e_T: Δℓ = +0.855 [+0.679, +1.032].

| Nhóm khối | Đóng góp Shapley φ | Tỉ lệ trên Δℓ | Hiệu ứng chính (2³) | Đặc trưng đóng góp chính |
|---|---|---|---|---|
| T (đích) | −0.010 [−0.044, +0.025] | −1% | −0.010 | — |
| P (đệm) | +0.352 [+0.232, +0.473] | 41% | +0.352 | `mean` +0.37, `knee_T` +0.23, `std` −0.17 |
| **X (chéo)** | **+0.513 [+0.439, +0.586]** | **60%** | +0.512 | `mean` +0.72, `p75` −0.16 |

- **Tương tác** nhỏ (TP −0.027, TX −0.004, PX −0.030, TPX +0.002). Vì vậy hiệu ứng chính gần bằng Shapley.
- **Dự đoán "P chiếm phần lớn" không được ủng hộ.** Phần lớn nhất đến từ khối chéo, là các cặp đích × đệm; khối đệm đứng thứ hai.
- **Đổi ra số cạnh**, khi áp ngưỡng lai lên điểm khối đích ở e_T:
  - toàn bộ ở e = 0: 43.8 cạnh;
  - chỉ đổi X: 30.6;
  - chỉ đổi P: 35.9;
  - đổi cả P và X: 25.5;
  - toàn bộ ở e_T: 26.5.
- **Trên chính EXP2:**
  - REP NATIVE −15.25;
  - phần do điểm (mốc là ngưỡng ở e = 0): +2.00 [−1.92, +5.92];
  - phần do ngưỡng: −17.25 [−23.39, −11.11].
- **Chính sách "ngưỡng cục bộ"** (thống kê và D của riêng khối đích): REP +6.45 [−1.08, +13.98]. Đây là một chính sách phản thực riêng, không phải phần do điểm.

**Mô tả hậu nghiệm** (ngoài danh sách định trước) để hiểu vai trò của `mean`:

| Khối | Xác suất trung bình ở e = 0 | Ở e = e_T |
|---|---|---|
| Đích | 0.395 | 0.430 |
| Đệm (mọi cặp là không-cạnh ở e = 0) | 0.546 | 0.405 |
| Chéo (mọi cặp là không-cạnh) | 0.362 | 0.189 |

- **Trọng số** của `mean` trong bộ chọn ngưỡng là **−8.56**.
- **Trung bình toàn ma trận** giảm −0.122 khi chuyển từ e = 0 sang e_T.
- **Cách đọc** (suy luận):
  - khi đệm độc lập, CDFM cho điểm khá cao ở các cặp nằm ngoài khối đích, dù đó là không-cạnh;
  - khi đệm có cấu trúc, các điểm này thấp đi, nhiều nhất ở khối chéo, khối có nhiều phần tử nhất (600, so với 380 và 235);
  - trung bình toàn ma trận vì vậy giảm, và do trọng số âm, ngưỡng tăng.
- **Đính chính một suy luận cũ:** báo cáo hậu nghiệm P-N1 từng viết "các cạnh riêng của khối đệm B đẩy phân phối điểm lên". Dữ liệu ở đây cho chiều ngược lại. Đã thêm ghi chú đính chính vào file đó.
- **Phần chưa giải thích:** vì sao CDFM cho không-cạnh điểm cao hơn khi đệm độc lập. Đó là câu hỏi bên trong model; Phần A chỉ phân tích một hàm đã biết.

## 2. Phần B: AVICI tuyến tính, can thiệp attention

**PLAIN:** REP Δm = −3.95 [−6.64, −1.26]. CI không chứa 0, nên a_I được dùng để phân loại.

| Cấu hình | REP Δm | a [CI bootstrap ghép cặp] | θ_I − θ_PLAIN | Cờ suy giảm | ΔF1 so với PLAIN (e = 0; e_T) |
|---|---|---|---|---|---|
| V0-all | −0.70 [−1.86, +0.46] | +0.82 [+0.40, +0.99] | +3.25 [+0.09, +6.41] | **có** | −0.235; −0.202 |
| KO-all | 0.00 | +1.00 (kiểm tra kỹ thuật) | +3.95 | không (cải thiện) | +0.147; +0.198 |
| V0-1 | −4.90 | −0.24 [−0.89, +0.19] | −0.95 | có | −0.010; −0.033 |
| V0-2 | −2.80 | +0.29 [−0.10, +0.75] | +1.15 | không | +0.012; +0.021 |
| V0-3 | −5.10 | −0.29 [−0.73, −0.11] | −1.15 [−2.02, −0.28] | không | +0.016; −0.016 |
| V0-4 | −4.10 | −0.04 | −0.15 | không | +0.011; −0.023 |
| V0-5 | −3.50 | +0.11 | +0.45 | không | −0.002; −0.020 |
| V0-6 | −3.40 | +0.14 | +0.55 | không | −0.028; −0.016 |
| V0-7 | −3.85 | +0.03 | +0.10 | không | +0.014; −0.012 |
| **V0-8** | −1.60 [−3.77, +0.57] | **+0.59 [+0.38, +0.93]** | +2.35 [+1.00, +3.70] | **có** (−0.031 ở e_T) | −0.008; −0.031 |
| KO-1 | −3.50 | +0.11 | +0.45 | không | −0.019; +0.000 |
| KO-2 | −2.95 | +0.25 [−0.02, +0.60] | +1.00 | không | +0.048; +0.043 |
| KO-3 | −5.10 | −0.29 | −1.15 | không | −0.012; −0.023 |
| KO-4 | −3.35 | +0.15 | +0.60 | không | −0.006; +0.025 |
| KO-5 | −5.75 | −0.46 | −1.80 | có | −0.009; −0.031 |
| KO-6 | −3.35 | +0.15 | +0.60 | có | −0.022; −0.033 |
| KO-7 | −5.25 | −0.33 [−0.87, −0.08] | −1.30 [−2.45, −0.15] | có | +0.020; −0.097 |
| **KO-8** | **−7.90 [−11.25, −4.55]** | **−1.00 [−1.95, −0.57]** | −3.95 [−5.67, −2.23] | **có** (−0.118 ở e_T) | +0.048; −0.118 |

- **Không có đảo chiều**, kể cả theo ước lượng điểm.
- **Phân loại theo luật §2: không có ứng viên nào.**
  - KO-all chỉ là kiểm tra kỹ thuật.
  - Hai can thiệp xóa từ 50% trở lên là V0-all và V0-8, nhưng cả hai đều bị cờ suy giảm.
  - Không lớp nào thỏa tiêu chí "nhạy với chuẩn hóa" (a(V0-ℓ) ≤ 25% và a(KO-ℓ) ≥ 75%).
  - Cả 8 lớp được gắn nhãn **"chưa phân biệt được"**.

**Mô tả** (không phải nhãn):

- **Lớp 8, tức lớp theo trục biến cuối cùng,** là nơi can thiệp có tác động lớn nhất.
  - Với V0-8, hiệu ứng nhỏ đi; với KO-8, hiệu ứng lớn gấp đôi.
  - Chênh lệch ghép cặp KO-8 − V0-8 là −6.30 [−8.01, −4.59]: ở lớp này, triệt value với loại khỏi mẫu số cho kết quả khác nhau rõ.
  - Nhưng cả hai đều kéo theo suy giảm F1 ở e_T, nên không được diễn giải thành cơ chế.
- **V0-all** xóa phần lớn hiệu ứng, nhưng cùng lúc làm F1 giảm khoảng 0.2. Cách đọc phù hợp: triệt value của đệm ở mọi lớp mà vẫn giữ mẫu số đã làm hỏng biểu diễn của khối đích. Đó không phải bằng chứng về kênh nội dung.
- **Cảnh báo về rò rỉ:** can thiệp theo lớp không loại trừ thông tin đã truyền qua ở các lớp trước (Geva et al. 2023).

## 3. Điểm dừng (luật §4)

- **Phần B: không có ứng viên.** Kết luận cho AVICI giữ ở mức **"kênh thay đổi"**: số cạnh giảm rõ; thay đổi thứ hạng chưa rõ. Theo luật, bước tiếp theo là mở rộng có chọn lọc hoặc viết bài, không khóa dự đoán cơ chế.
- **Phần A: kênh ngưỡng của CDFM được mô tả ở mức nhóm khối và đặc trưng.**
  - Khối chéo đóng góp khoảng 60%, khối đệm khoảng 41%, qua `mean` với trọng số âm.
  - Đây là phân tích trên một hàm đã biết. Nó cho một câu cụ thể và kiểm được: điểm của các cặp không-cạnh ngoài khối đích giảm khi đệm có cấu trúc, và qua bộ hiệu chỉnh toàn bảng, việc đó làm ngưỡng tăng.

## 4. Không được nói

- "Đã tìm ra cơ chế attention của AVICI."
- "Lớp 8 là nơi chứa cơ chế."
- "V0 cho thấy nội dung đệm là cần thiết." V0-all đã làm hỏng dự đoán.
- "Khối đệm có cạnh đẩy điểm lên." Dữ liệu cho chiều ngược lại.
- "Ngưỡng cục bộ tách được phần do điểm."

## 5. Bước tiếp (để user quyết)

1. **Viết báo cáo phát hiện** với phạm vi hiện có:
   - failure đã xác nhận qua P-N1 held-out, EXP2 và HELD2;
   - các kênh thay đổi đã đo: số cạnh và thứ hạng ở AVICI; kênh ngưỡng toàn bảng ở CDFM, phân rã tới mức khối;
   - cách sửa rẻ: R mô tả ở HELD2; với CDFM thêm "ngưỡng cục bộ" như một chính sách phản thực cần đánh giá riêng.

   Cần lặp lại tìm kiếm prior art trước khi viết.
2. **Mở rộng có chọn lọc** trước khi viết: một k khác, một n khác, họ đồ thị SF.
   - Với CDFM, có thể khóa một dự đoán cụ thể từ Phần A: khối chéo đóng góp phần lớn Δℓ.
   - Với AVICI, chưa có dự đoán cơ chế để khóa.
3. **Không nên** tiếp tục dò attention của AVICI bằng các can thiệp cùng loại. Pilot cho thấy các can thiệp mạnh đều làm hỏng dự đoán, nên cần một thiết kế khác (ví dụ thay key mà không đổi value, hoặc probing) nếu muốn đi tiếp.
