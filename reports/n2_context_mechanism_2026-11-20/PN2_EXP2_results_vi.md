# P-N2, pha exploratory (EXP2): kết quả (21/11/2026)

> **Luật:** [v1](PN2_rules_exploratory_vi.md), khóa ở commit `5c2c76c`. Code đóng băng ở `fddfadd`, push lúc 2026-11-21T01:46:53Z, trước khi chạy.
> **Chạy:** 40 hệ, từ 02:17:03 đến 04:53:52 UTC ngày 21/11 (2 giờ 37 phút).
> **Đọc:** bằng `analyze2.py` đã đóng băng (AVICI, CDFM, cổ điển), sau khi kiểm hoàn tất đạt (§1).
> **Nhãn:** số liệu là [Verified-run]. Mọi nhãn ở đây là **exploratory**: không kiểm soát familywise, không phải claim xác nhận. Diễn giải ở §4 là suy luận. Đơn vị phân tích là model × họ, 20 hệ mỗi họ. Mọi CI là bootstrap percentile 95% theo hệ.
> **Ký hiệu cho các ô contrast:** mỗi ô ghi ước lượng [CI 95%], kèm hai chữ cái nhãn:
>
> - chữ đầu là dấu: P = POS, N = NEG, 0 = NONE;
> - chữ sau là cỡ: L = LARGE, S = SMALL, U = UNCLEAR.

## 1. Hoàn tất và toàn vẹn (đạt hết)

Kiểm theo yêu cầu của user, bằng script riêng `artifacts/n2_runs/pn2_checks/exp2_completeness.py`, không sửa code đã đóng băng. Bản chép của script và kết quả ở [checks/](checks/); bản chép chỉ để đối chiếu, không chạy từ đó.

- **Đủ output:** 1 440 output (AVICI 640, CDFM 640, PC 80, GES 80), cùng 1 120 dòng biến thể sàng lọc.
- **Không lỗi:** 0 job lỗi trong mọi log; 0 lệch mã băm input khi sinh lại toàn bộ 320 input.
- **Cổng đóng băng:** đạt `ok: true` ở cả `exp2_start` và `exp2_end`, cùng commit `fddfadd` và cùng mã băm `SHA256SUMS`.
- **Không có hệ m0 = 0.**

## 2. Giả thuyết định trước (§7, xét theo REP)

| ID | Model, họ | Y | Dự đoán | REP | Nhãn | Cỡ | L1-END |
|---|---|---|---|---|---|---|---|
| HA1 | AVICI, tuyến tính | Δm | NEG | −3.95 [−6.45, −1.55] | **CONSISTENT** | LARGE | −3.90 [−6.50, −1.20] |
| HA2 | AVICI, RFF | Δm | NEG | −3.90 [−6.95, −1.65] | **CONSISTENT** | LARGE | −4.15 [−7.20, −1.85] |
| HA3 | AVICI, tuyến tính | F1 ở top-m0 | POS | −0.002 [−0.031, +0.027] | INCONCLUSIVE | UNCLEAR | −0.013 [−0.051, +0.021] |
| HA4 | AVICI, tuyến tính | AUROC | POS | +0.012 [−0.012, +0.037] | INCONCLUSIVE | UNCLEAR | −0.000 [−0.031, +0.029] |
| HA5 | AVICI, RFF | F1 ở top-m0 | NEG | −0.040 [−0.059, −0.023] | **CONSISTENT** | UNCLEAR | −0.054 [−0.075, −0.031] |
| HA6 | AVICI, RFF | AUROC | NEG | −0.012 [−0.027, +0.006] | INCONCLUSIVE | SMALL | −0.031 [−0.047, −0.014] |
| HC1 | CDFM, RFF | ngưỡng NATIVE | POS | +0.159 [+0.128, +0.189] | **CONSISTENT** | LARGE | +0.144 [+0.111, +0.176] |
| HC2 | CDFM, RFF | Δm NATIVE | NEG | −15.25 [−23.25, −8.90] | **CONSISTENT** | LARGE | −14.05 [−22.30, −7.65] |
| HC3 | CDFM, RFF | F1 ở top-m0 | NEG | −0.041 [−0.067, −0.016] | **CONSISTENT** | UNCLEAR | −0.058 [−0.085, −0.031] |
| HC4 | CDFM, RFF | AUROC | NEG | −0.039 [−0.057, −0.020] | **CONSISTENT** | UNCLEAR | −0.038 [−0.059, −0.019] |
| HC5 | CDFM, tuyến tính | ngưỡng NATIVE | POS | +0.017 [−0.014, +0.056] | INCONCLUSIVE | UNCLEAR | −0.004 [−0.033, +0.029] |

- **7/11 CONSISTENT**, 4 INCONCLUSIVE, **không có CONTRARY**. Không có cờ "hình dạng khác dự đoán".
- **Không lặp lại:** pattern "ở hệ tuyến tính, đệm có cấu trúc làm AVICI xếp hạng tốt hơn" (HA3, HA4) của P-N1. Ước lượng gần 0.

## 3. Đường liều–đáp ứng (L1) và cường độ (L2), các Y chính

Mỗi cột là Y(điều kiện) − Y(e = 0). Cột e = 3 là L1-END; cột s = 1 trùng với cột e = 2.

**Số cạnh và ngưỡng:**

| Model, họ, Y | e = 0.5 | e = 1 | e = 2 | e = 3 | s = 0.25 | s = 0.5 |
|---|---|---|---|---|---|---|
| AVICI tuyến tính, Δm | −3.30 [−4.65, −1.90] NL | −4.00 NL | −4.00 NL | −3.90 NU | −3.55 NU | −3.70 NU |
| AVICI RFF, Δm | −1.65 [−3.35, −0.30] NU | −3.15 NU | −3.70 NU | −4.15 NL | −1.50 NU | −3.60 NL |
| CDFM tuyến tính, Δm NATIVE | −1.15 0U | +2.60 0U | +0.15 0U | −0.95 0U | **+10.00 [+4.15, +16.65] PL** | +4.20 0U |
| CDFM tuyến tính, ngưỡng | **+0.065 [+0.040, +0.098] PL** | +0.036 PU | +0.008 0U | −0.004 0U | −0.041 NU | −0.005 0U |
| CDFM tuyến tính, Δm FROZEN | −1.50 0U | +0.00 0U | −3.40 NU | −8.05 [−13.0, −3.65] NL | −1.05 0U | −3.90 NU |
| CDFM RFF, Δm NATIVE | −11.00 NL | −15.25 NL | −15.85 NL | −14.05 NL | −10.95 NL | −14.40 NL |
| CDFM RFF, ngưỡng | +0.138 PL | +0.162 PL | +0.168 PL | +0.144 PL | +0.121 PL | +0.145 PL |
| CDFM RFF, Δm FROZEN | +1.50 0U | +1.75 0U | +1.60 0U | +3.30 [+0.05, +6.40] PU | +1.85 0U | +1.35 0U |

**Thứ hạng:**

| Model, họ, Y | e = 0.5 | e = 1 | e = 2 | e = 3 | s = 0.25 | s = 0.5 |
|---|---|---|---|---|---|---|
| AVICI tuyến tính, AUROC | +0.021 PU | +0.016 0U | +0.013 0U | −0.000 0U | +0.030 PU | +0.022 0U |
| AVICI RFF, F1 ở top-m0 | −0.022 NU | −0.030 NU | −0.051 NL | −0.054 NL | −0.022 NU | −0.038 NU |
| AVICI RFF, AUROC | −0.006 0S | −0.008 0S | −0.015 0U | −0.031 NU | +0.004 0S | −0.015 0S |
| CDFM tuyến tính, AUROC | +0.009 0U | +0.002 0S | −0.015 NS | −0.006 0S | −0.016 0U | −0.017 0U |
| CDFM RFF, F1 ở top-m0 | −0.021 0U | −0.029 NU | −0.045 NU | −0.058 NL | −0.042 NU | −0.049 NU |
| CDFM RFF, AUROC | −0.021 NU | −0.022 NU | −0.037 NU | −0.038 NU | −0.021 NU | −0.039 NU |

**F1 NATIVE (Y phụ), REP và L1-END:**

- AVICI tuyến tính: −0.051 NU và −0.084 [−0.120, −0.049] NL.
- AVICI RFF: −0.090 NL và −0.088 NL.
- CDFM tuyến tính: +0.021 0U và +0.002 0U.
- CDFM RFF: +0.026 0U và +0.001 0U.

## 4. Đọc (suy luận từ exploratory, chưa xác nhận)

1. **AVICI tuyến tính: số cạnh giảm rõ; thay đổi thứ hạng chưa rõ.** *(sửa ở đính chính 21/11, §10)*
   - Đệm có cấu trúc làm AVICI dự đoán ít hơn khoảng 4 cạnh.
   - Thứ hạng: F1 ở top-m0 có REP −0.002 [−0.031, +0.027] và AUROC +0.012 [−0.012, +0.037]. Cả hai là UNCLEAR theo biên ±0.03, nên **không** được viết là "thứ hạng không đổi". Chiều cải thiện thứ hạng của P-N1 chưa tái lập được.
   - Ước lượng điểm gợi ý dạng "bậc": −3.30 ở e = 0.5 (ở mức này, DEV2 vẫn còn khoảng 36% nút đệm cô lập) và −3.55 ở s = 0.25, gần bằng mức ở e = 2–3. Đây mới là gợi ý từ đường ước lượng, chưa được kiểm trực tiếp.
2. **AVICI RFF: dịch mức và mất thứ hạng, tăng dần theo liều.**
   - Số cạnh giảm dần: −1.65 → −3.15 → −3.70 → −4.15 khi e tăng; −1.50 → −3.60 khi s tăng.
   - F1 ở top-m0 cũng giảm dần, tới −0.054 ở e = 3.
3. **CDFM RFF: vai trò của ngưỡng được ủng hộ mạnh.** *(sửa ở đính chính 21/11, §10)*
   - Ngưỡng tăng khoảng 0.12–0.17 và số cạnh NATIVE giảm khoảng 11–16.
   - **Phân rã hậu nghiệm ở REP**, lấy ngưỡng của e = 0 làm mốc, tính lại trên output:
     - đổi điểm, giữ ngưỡng đó: +2.00 cạnh;
     - rồi đổi sang ngưỡng của đệm có cấu trúc: −17.25 cạnh;
     - tổng: −15.25 cạnh.
   - Phân rã này theo mốc đã chọn. Nó ủng hộ việc ngưỡng là phần đóng góp lớn vào mức giảm ròng, nhưng không giải thích vì sao model đổi điểm hay đổi ngưỡng.
   - Với ngưỡng của k0 (FROZEN), REP là +1.95 [−1.15, +5.40]: chưa đạt tương đương. Vì vậy không được viết "số cạnh gần như không đổi".
   - Bên cạnh đó có mất thứ hạng: AUROC giảm khoảng 0.02–0.04, F1 ở top-m0 giảm tới −0.058.
   - F1 NATIVE gần như không đổi. Một cách giải thích là ngưỡng tăng loại bớt cạnh sai, bù cho phần mất thứ hạng (suy luận).
   - Ước lượng điểm của ngưỡng và số cạnh đã gần đủ ngay ở e = 0.5 và s = 0.25. Đó mới là gợi ý dạng "bậc", chưa được kiểm trực tiếp.
4. **CDFM tuyến tính: không đơn điệu, ngoài dự đoán.**
   - Ngưỡng tăng ở e = 0.5 (+0.065) rồi trở về mức cũ ở e = 2–3.
   - Ở s = 0.25, số cạnh NATIVE **tăng** 10 cạnh, đi cùng ngưỡng giảm (−0.041). Ở s = 0.5 và s = 1, hiệu ứng nhỏ lại.
   - Ở FROZEN và FIXED, số cạnh giảm theo mật độ (L1-END −8.05 và −13.5).
   - Đây là pattern mới, sinh từ EXP2, có thể là ứng viên giả thuyết mới.
5. **Chung:** hai model đều phản ứng với cấu trúc của khối đệm ở cùng D, nhưng qua các kênh khác nhau theo họ dữ liệu:
   - số cạnh, còn thay đổi thứ hạng chưa rõ (AVICI tuyến tính);
   - số cạnh và thứ hạng (AVICI RFF);
   - ngưỡng toàn bảng và thứ hạng (CDFM RFF).

   Cơ chế bên trong model chưa được xác lập.

   L1 không quy được nguyên nhân cho prior huấn luyện (§1 của luật).

## 5. Nhánh R (§10.3)

| Model, họ | Giá tại k0 (F1 sau R − trước R) | F1 sau R trên input có đệm − F1 k0 ban đầu | Cách sửa có ích? | Gộp nhầm | Tách nhầm | Thời gian mỗi input |
|---|---|---|---|---|---|---|
| AVICI tuyến tính | −0.021 [−0.051, +0.005] 0U | −0.020 đến −0.021 0U | UNCLEAR | 0.3% biến đệm ở e = 0, còn lại 0 | 6.1% cạnh thật | 2.3–2.5 s |
| AVICI RFF | +0.008 [−0.006, +0.023] 0S | +0.008 0S | **YES** (cả 7 điều kiện) | tới 3.2% ở e = 1 | 5.0% | 3.2–4.2 s |
| CDFM tuyến tính | −0.019 [−0.032, −0.007] NU | −0.019 NU | UNCLEAR | như AVICI | 6.1% | 2.9–3.0 s |
| CDFM RFF | +0.009 [−0.009, +0.028] 0S | +0.005 đến +0.009 0S | **YES** (cả 7 điều kiện) | như AVICI | 5.0% | 3.6–3.8 s |

- **R đưa các contrast trung bình xuống dưới biên đã chọn** *(sửa ở đính chính 21/11, §10)*: mọi contrast R-* của Y chính đều SMALL.
  - Lý do: sàng lọc gần như luôn tách đúng khối đệm, nên model thường thấy cùng một tập thành phần đích ở mọi điều kiện có đệm.
  - **Trung bình SMALL không có nghĩa bất biến ở từng hệ.** Ở REP sau R, CDFM tuyến tính có một hệ đổi 7 cạnh (`EXP2-c4-r1`). AVICI đổi 2 cạnh trên chính hệ đó, và CDFM RFF có một hệ đổi 1 cạnh.
  - Các ô mà contrast gốc LARGE còn contrast R SMALL:
    - AVICI tuyến tính: Δm (REP), F1 (L1-END);
    - AVICI RFF: Δm, F1, top-m0, AP;
    - CDFM tuyến tính: Δm FROZEN và FIXED;
    - CDFM RFF: Δm, top-m0, AP.
- **Có phải cách sửa có ích:**
  - Ở RFF: có, với cả hai model.
  - Ở tuyến tính: UNCLEAR. Cái giá là tách nhầm chính khối đích (6.1% cạnh thật bị chia ra), làm F1 giảm khoảng 0.02, với CI kéo tới −0.05 (AVICI) và −0.032 (CDFM).
- **Biến thể, chỉ đo sàng lọc:**
  - HSIC dùng cho họ tuyến tính (không cần biết họ cơ chế) gộp nhầm khoảng 5% biến đệm ở e = 2–3 và tách nhiều hơn (8.2%).
  - Spearman trên RFF không gộp nhầm nhưng tách nhiều hơn (9.3%, so với 5.0%).
  - BH gộp nhầm rất nhiều (35–55% biến đệm). Như dự kiến, BH không hợp với mục tiêu tránh nối thành phần.
- **Giới hạn:**
  - α_HSIC là mức danh nghĩa (G9); kết quả R không cung cấp bảo đảm FWER.
  - R thành công một phần vì khối đệm ở đây độc lập **đúng** với khối đích. Dữ liệu thật không có bảo đảm đó.

## 6. Mốc cổ điển (20 hệ tuyến tính)

- **PC:** hoàn toàn bất biến; Δm và ΔF1 bằng 0 ở REP, L1-END và e = 0 so với k0.
- **GES:** gần bất biến.
  - REP: Δm −0.60 [−1.65, +0.15], ΔF1 +0.001.
  - L1-END: Δm −0.45, ΔF1 +0.002.
  - e = 0 so với k0: Δm +0.80 [+0.15, +1.75], ΔF1 −0.007.

So sánh, cùng các hệ đó: AVICI có ΔF1 ở L1-END là −0.084.

## 7. EXP2 quyết định gì (§10)

1. **Giả thuyết sang HELD2** (tối đa 5, trong đó tối đa 2 giả thuyết mới; Holm 0.05 trên p-value khóa trước).
   - Ứng viên CONSISTENT: HA1, HA2, HA5, HC1, HC2, HC3, HC4.
   - Ứng viên mới: CDFM tuyến tính ở s = 0.25 (Δm +10, LARGE); ngưỡng CDFM tuyến tính ở e = 0.5 (+0.065, LARGE); dạng "bậc" của AVICI tuyến tính.
   - Đề xuất của agent ở §8.
2. **Cỡ mẫu HELD2:** tính từ độ lệch chuẩn của contrast REP ở EXP2, với kiểm một phía, power 80%, xấp xỉ chuẩn:

   | Giả thuyết | d (trung bình/SD) | n mỗi họ ở α = 0.01 | ở α = 0.05 |
   |---|---|---|---|
   | HA1 | 0.66 | 23 | 15 |
   | HA2 | 0.61 | 28 | 17 |
   | HA5 | 0.90 | 13 | 8 |
   | HC1 | 2.16 | 3 | 2 |
   | HC2 | 0.88 | 13 | 8 |
   | HC3 | 0.72 | 20 | 12 |
   | HC4 | 0.88 | 13 | 9 |

   - Ước lượng của EXP2 có thể lạc quan, vì giả thuyết được chọn theo chính dữ liệu này. Ở P-N1, hiệu ứng M1 đã thu nhỏ ở held-out.
   - Nếu hiệu ứng thu nhỏ 30%, n cần tăng khoảng 2 lần; khi đó HA2 cần khoảng 57 hệ mỗi họ, nhiều hơn 40 hệ của kế hoạch 80.
   - **HELD2 chỉ cần chạy các input mà giả thuyết dùng:** REP cần k0, e = 0 và e = e_T, tức 3 input mỗi hệ thay vì 8 + R. Nhờ vậy có thể tăng cỡ mẫu mà chi phí không tăng nhiều.
3. **Nhánh R:** đã đọc ở §5. "Failure + cơ chế + cách sửa rẻ" (§10.3) là hướng phát triển hợp lý. Tuy vậy, cơ chế bên trong model chưa được xác lập; HELD2 chỉ xác nhận các hiệu ứng REP được chọn.
4. **Bước sau:** theo §10.4, can thiệp attention và FoundCause đã đủ điều kiện mở, vì có hiệu ứng LARGE và có giả thuyết CONSISTENT.

## 8. Đề xuất của agent (để user quyết)

- **HELD2, 5 giả thuyết, không giả thuyết mới:**
  - HA1, HA2: AVICI ít cạnh hơn ở cả hai họ.
  - HC1: ngưỡng của CDFM RFF tăng; kênh cơ chế rõ nhất.
  - HA5: AVICI RFF mất thứ hạng.
  - HC4: CDFM RFF mất AUROC; không phụ thuộc mốc m0.

  Bỏ HC2, vì nó phần lớn là hệ quả của HC1. Nếu muốn kiểm pattern không đơn điệu của CDFM tuyến tính ở s = 0.25, thay HC4 bằng giả thuyết mới đó.
- **Cỡ mẫu:** ưu tiên 120 hệ (60 mỗi họ), chỉ chạy k0, e = 0 và e = e_T, để còn power nếu hiệu ứng thu nhỏ.
  - Cỡ này hợp để kiểm dấu, chưa bảo đảm hiệu ứng vượt biên thực tiễn (1.5 cạnh, 0.03).
  - Chi phí: dự trù 2–3 giờ nếu chạy cả R. Theo tính toán của user từ thời gian từng job EXP2: khoảng 1.45 giờ cho nhánh thường và 0.67 giờ cho R, chưa tính chi phí phụ. Bản trước ghi "dưới 2 giờ".
- **Có thể kiểm thêm nhánh R trên HELD2,** dưới dạng mô tả, không tính vào 5 giả thuyết Holm.

## 9. Giới hạn

- Exploratory: 20 hệ mỗi họ, không kiểm soát familywise; các giả thuyết đều đã được chọn trước nên có nhãn rõ, nhưng phần §4 là suy luận.
- Một kích thước đệm (k = 20), một họ đồ thị (ER), n = 500, hai checkpoint.
- α_HSIC là mức danh nghĩa.
- Code đọc chưa từng thấy dữ liệu thật; không có ground truth ngoài dữ liệu tổng hợp.

## 10. Đính chính diễn giải và quyết định (21/11, sau review của user)

Số liệu, nhãn exploratory và code đã đóng băng giữ nguyên. User đã tính lại bảng giả thuyết từ dữ liệu từng hệ: 7/11 CONSISTENT, 4 INCONCLUSIVE, không có CONTRARY, khớp với §2.

| # | Chỗ | Bản trước | Sửa thành | Căn cứ |
|---|---|---|---|---|
| 1 | §4.1, §4.5 | "AVICI tuyến tính: dịch mức mà không đổi thứ hạng"; hiệu ứng "đủ ngay ở mức yếu nhất" | Số cạnh giảm rõ; thay đổi thứ hạng chưa rõ (cả hai metric là UNCLEAR); chưa tái lập chiều cải thiện của P-N1. Dạng "bậc" mới là gợi ý từ đường ước lượng | Review; §2, §3 |
| 2 | §4.3 | "Phần giảm số cạnh ở NATIVE đến từ ngưỡng"; "FROZEN thì số cạnh gần như không đổi" | Vai trò của ngưỡng được ủng hộ mạnh, qua phân rã hậu nghiệm với mốc là ngưỡng của e = 0: điểm +2.00, ngưỡng −17.25, tổng −15.25. FROZEN chưa đạt tương đương | Review; agent tính lại trên output và khớp |
| 3 | §5 | "R xóa mọi thay đổi do đệm" (bản trước và commit message `3f100a9`) | R đưa các contrast trung bình xuống dưới biên đã chọn. Trung bình SMALL không có nghĩa bất biến ở từng hệ: có một hệ CDFM đổi 7 cạnh | Review; agent kiểm từng hệ |
| 4 | §7.3, §8 | Khung bài "failure + cơ chế + cách sửa rẻ"; chi phí HELD2 "dưới 2 giờ" | Hướng phát triển hợp lý, nhưng cơ chế bên trong model chưa được xác lập. Chi phí dự trù 2–3 giờ nếu chạy cả R. 120 hệ là để kiểm dấu, chưa bảo đảm vượt biên thực tiễn | Review |

**Quyết định của user cho HELD2:**

- **Năm giả thuyết:** HA1, HA2, HC1, HA5, HC4.
  - Giữ HC4 để kiểm mất thứ hạng ở CDFM bằng một metric không phụ thuộc m0.
  - Chưa đưa pattern không đơn điệu của CDFM tuyến tính vào, vì pattern đó cần định nghĩa contrast riêng.
- **Cỡ mẫu:** 120 hệ (15 mỗi ô, 60 mỗi họ), chạy k0, e = 0 và e = e_T.
- **Nhánh R:** chạy trên cùng 120 hệ, là phân tích phụ. Báo CI, giá tại k0, chất lượng sau R, lỗi gộp và lỗi tách. Không gọi kết quả R là đã được xác nhận bằng bộ năm phép kiểm Holm.
- **Cách tính p-value:** chốt trong luật HELD2, trước khi khóa. Hướng của user là kiểm trung bình contrast một phía với sai số chuẩn phản ánh các ô thiết kế, rồi Holm 0.05 trên đúng năm giả thuyết. Không mặc định sign-flip là phép kiểm chính xác.
