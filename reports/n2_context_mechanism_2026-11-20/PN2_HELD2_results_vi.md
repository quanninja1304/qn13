# P-N2 HELD2: kết quả xác nhận (21/11/2026)

> **Luật:** [HELD2 v1](PN2_rules_held2_vi.md), khóa ở commit `7bc8ba0` (push lúc 06:28:11Z). Code đóng băng ở `16ea97f` (push lúc 06:32:16Z), trước khi sinh input HELD2 nào.
> **Chạy:** 120 hệ (15 mỗi ô), từ 06:33:25 đến 08:09:00 UTC ngày 21/11 (1 giờ 36 phút).
> **Đọc:** bằng `analyze_held2.py` đã đóng băng, sau khi kiểm hoàn tất đạt (§1).
> **Nhãn:**
>
> - [Verified-run] cho số liệu.
> - Nhãn CONFIRMED / NOT_CONFIRMED chỉ áp cho **năm** giả thuyết, qua Holm ở mức familywise 0.05.
> - Mọi phần khác (§3–§5) là **mô tả**, không thuộc bộ Holm.
> - Phạm vi: hai checkpoint (AVICI `scm-v0`, CDFM), dữ liệu tổng hợp ER tuyến tính và RFF, n = 500, d_T ∈ {10, 20}, k = 20.

## 1. Hoàn tất và toàn vẹn (đạt hết)

Script đóng băng `held2_completeness.py` (luật §6) cho kết quả:

- **Đủ output:** 1 440 output (mỗi model 360 lần chạy thường và 360 lần chạy R).
- **Không lỗi:** 0 job lỗi; 0 lệch mã băm input khi sinh lại toàn bộ input.
- **Cổng đóng băng:** `held2_start` và `held2_end` đều `ok: true`, cùng commit `16ea97f`.
- **Không có hệ m0 = 0.**

## 2. Năm giả thuyết: cả năm CONFIRMED

Kiểm một phía trên trung bình contrast REP cân bằng theo ô, sai số chuẩn phân tầng theo ô, df Welch–Satterthwaite, rồi Holm 0.05 (luật §3).

| ID | Model, họ, Y | Dự đoán | θ̂ [CI 95%] | t (df) | p một phía | Hạng, ngưỡng Holm | Nhãn | Cỡ |
|---|---|---|---|---|---|---|---|---|
| HC1 | CDFM, RFF, ngưỡng NATIVE | POS | +0.175 [+0.159, +0.191] | 22.39 (27.5) | 1.6e-19 | 1, 0.0100 | **CONFIRMED** | LARGE |
| HA1 | AVICI, tuyến tính, m NATIVE | NEG | −6.05 [−8.18, −3.92] | 5.82 (26.5) | 1.8e-6 | 2, 0.0125 | **CONFIRMED** | LARGE |
| HA2 | AVICI, RFF, m NATIVE | NEG | −1.93 [−2.85, −1.02] | 4.27 (43.4) | 5.3e-5 | 3, 0.0167 | **CONFIRMED** | UNCLEAR |
| HA5 | AVICI, RFF, F1 ở top-m0 | NEG | −0.027 [−0.044, −0.009] | 3.10 (52.1) | 0.0016 | 4, 0.0250 | **CONFIRMED** | UNCLEAR |
| HC4 | CDFM, RFF, AUROC | NEG | −0.014 [−0.025, −0.003] | 2.51 (36.4) | 0.0083 | 5, 0.0500 | **CONFIRMED** | SMALL |

- **Kiểm tra độ nhạy** (không phải căn cứ xác nhận; quyết định xác nhận chỉ đến từ phép kiểm đã khóa và Holm): CI bootstrap phân tầng của cả năm giả thuyết đều loại 0 theo chiều dự đoán, cùng chiều với phép kiểm t:

  | ID | CI bootstrap phân tầng |
  |---|---|
  | HC1 | [+0.159, +0.189] |
  | HA1 | [−8.12, −4.10] |
  | HA2 | [−2.82, −1.12] |
  | HA5 | [−0.043, −0.011] |
  | HC4 | [−0.024, −0.003] |

- **Theo d_T:** dấu giống nhau ở d_T = 10 và d_T = 20 cho cả năm giả thuyết.
- **Đọc nhãn cỡ:** xác nhận chỉ là ở mức **dấu**.
  - HA1 và HC1 vượt biên thực tiễn (LARGE).
  - HA2 và HA5 có CI cắt biên (UNCLEAR).
  - HC4 có dấu được xác nhận, nhưng toàn bộ CI nằm trong ±0.03, tức nhỏ theo biên đã chọn.
- **So với EXP2** (ước lượng EXP2 có thể lạc quan, vì giả thuyết được chọn theo chính dữ liệu đó):
  - HA2 thu nhỏ từ −3.90 xuống −1.93;
  - HA5 thu nhỏ từ −0.040 xuống −0.027;
  - HC4 thu nhỏ từ −0.039 xuống −0.014;
  - HA1 tăng từ −3.95 lên −6.05;
  - HC1 tương đương (+0.159 so với +0.175).

**Điều có thể nói** (trong phạm vi ở đầu file): khi khối đệm có cấu trúc (e = e_T) so với khối đệm độc lập (e = 0), ở cùng D:

- AVICI dự đoán ít cạnh hơn trên khối đích, ở cả hệ tuyến tính lẫn RFF;
- AVICI mất thứ hạng ở RFF;
- ngưỡng NATIVE của CDFM tăng ở RFF;
- AUROC của CDFM giảm ở RFF, nhưng mức giảm nhỏ.

## 3. Mô tả: các Y khác ở REP (không thuộc bộ Holm)

| Model, họ | Đáng chú ý (θ̂ [CI 95%], dấu/cỡ) |
|---|---|
| AVICI tuyến tính | TP −2.45 [−3.40, −1.50] NL; FP −3.60 [−5.03, −2.17] NL; F1 −0.049 [−0.087, −0.011] NU; **AUROC +0.027 [+0.011, +0.044] PU**; AP +0.037 PU; top-m0 +0.018 [−0.004, +0.039] 0U |
| AVICI RFF | F1 −0.051 [−0.069, −0.034] NL; TP −1.72 NU; FP −0.22 0S; AP −0.028 NU; AUROC −0.019 NS |
| CDFM tuyến tính | ngưỡng +0.030 [+0.017, +0.042] PU; m NATIVE +1.68 0U; F1 +0.020 PU; m FIXED −6.08 NL; m FROZEN −1.95 0U |
| CDFM RFF | m NATIVE −15.57 NL (TP −3.33, **FP −12.23**); F1 NATIVE +0.030 PU; **m FROZEN +5.07 [+2.89, +7.25] PL**; F1 FROZEN −0.023 NU; AP −0.037 NU |

Hai quan sát mô tả, **không** được tính là xác nhận:

- **AVICI tuyến tính:** AUROC và AP có dấu dương. Đây là chiều mà P-N1 từng thấy, còn EXP2 không lặp lại được (HA3, HA4 khi đó INCONCLUSIVE). Pattern này không nằm trong năm giả thuyết, nên chỉ được ghi nhận, không được claim.
- **CDFM RFF:** với ngưỡng của k0, có thêm cặp vượt ngưỡng (số cạnh +5.07). Điều này chưa chứng minh toàn bộ phân phối điểm dịch lên. Ngưỡng NATIVE tăng mạnh, nên số cạnh NATIVE giảm 15.6, chủ yếu là cạnh sai (FP −12.2). F1 NATIVE tăng nhẹ. *(Câu này sửa ngày 21/11, xem §7.)*

**Phân rã ngưỡng ở CDFM** (luật §4; mốc là ngưỡng của e = 0; theo mốc đã chọn, không phải nguyên nhân):

| Họ | Phần do điểm | Phần do ngưỡng |
|---|---|---|
| RFF | +2.30 [−0.15, +4.75] 0U | **−17.87 [−19.86, −15.87] NL** |
| Tuyến tính | +3.08 [+0.05, +6.12] PU | −1.40 [−3.22, +0.42] 0U |

Ở CDFM RFF, phần do ngưỡng chiếm gần hết mức giảm ròng, lặp lại hướng của EXP2. Phân rã này không giải thích vì sao model đổi ngưỡng hay đổi điểm.

## 4. Nhánh R (phân tích phụ, không được xác nhận bằng Holm)

| Model, họ | Giá tại k0 (F1 sau R − trước R) | F1 sau R − F1 k0 ban đầu (e = 0; e = e_T) | Δm ở REP sau R | Gộp nhầm / tách nhầm | \|Δm\| tối đa theo hệ ở REP sau R |
|---|---|---|---|---|---|
| AVICI tuyến tính | −0.000 [−0.018, +0.017] SMALL | −0.001; +0.000, SMALL | −0.05 SMALL | 0.08% / 5.5% | 3 (1 hệ ≥ 2) |
| AVICI RFF | +0.007 [−0.001, +0.015] SMALL | +0.007; +0.005, SMALL | +0.03 SMALL | tới 2.1% / 5.1% | 1 |
| CDFM tuyến tính | −0.018 [−0.031, −0.005] NU | −0.021; −0.022, NU | −0.18 SMALL | 0.08% / 5.5% | **11** (1 hệ: `HELD2-c6-r14`) |
| CDFM RFF | +0.000 [−0.012, +0.012] SMALL | +0.001; +0.000, SMALL | −0.10 SMALL | tới 2.1% / 5.1% | 4 (2 hệ ≥ 2) |

- **R làm giảm thay đổi trên các biến đo:** ở cả bốn ô, mọi contrast REP sau R đều SMALL (Δm, F1, top-m0, AUROC; với CDFM thêm FROZEN và FIXED).
- **Cách sửa có ích** (theo tiêu chí luật v1 §10.3, ở đây chỉ để mô tả):
  - có ở AVICI tuyến tính, AVICI RFF và CDFM RFF;
  - UNCLEAR ở CDFM tuyến tính: giá tại k0 −0.018, cận dưới −0.031, sát biên −0.03.
- **Không bất biến ở từng hệ:** `HELD2-c6-r14` đổi 11 cạnh với CDFM và 3 cạnh với AVICI.
- Các ngưỡng thành phần của CDFM sau R gần như không đổi giữa k0, e = 0 và e_T (khoảng 0.57 ở họ tuyến tính, 0.61 ở RFF). Chỉ để mô tả.
- α_HSIC là mức danh nghĩa. R không cung cấp bảo đảm FWER, và nó hiệu quả một phần vì khối đệm ở đây độc lập **đúng** với khối đích.

## 5. Không được nói

- "Cơ chế bên trong model đã được xác lập." Mới có phân rã kế toán và các chiều hiệu ứng.
- "R đã được xác nhận." R chỉ là phân tích phụ.
- "Mọi model học sẵn đều bị."
- "Hiệu ứng vượt biên thực tiễn" cho HA2, HA5, HC4.
- "AVICI tuyến tính cải thiện thứ hạng." Đó chỉ là quan sát mô tả, không thuộc bộ kiểm.

## 6. Ý nghĩa cho N1 và bước tiếp (để user quyết)

- **Phát hiện đã đứng vững qua ba lớp dữ liệu:**
  - P-N1 held-out: mức hại;
  - P-N2 EXP2: chọn giả thuyết;
  - P-N2 HELD2: xác nhận dấu.
- **Kênh thay đổi đã đo** (mô tả): ở AVICI là số cạnh, cùng mất thứ hạng ở RFF; ở CDFM RFF là ngưỡng toàn bảng, cùng mất thứ hạng nhỏ.
- **Cách sửa rẻ:** sàng lọc rồi tách thành phần đưa các thay đổi trung bình về dưới biên, với chi phí chất lượng nhỏ ở 3/4 ô.
- **Khung bài:** "failure + các kênh đã đo + cách sửa rẻ" là hợp lý. Phần còn thiếu để gọi là "cơ chế" là bằng chứng bên trong model.
- **Lựa chọn tiếp theo:**
  1. **Bước can thiệp attention** (luật v1 §10.4 đã mở), để tìm đường truyền bên trong AVICI và CDFM: mask theo lớp; tách đóng góp value khỏi mẫu số softmax.
  2. **Mở rộng độ bền** trước khi viết: kích thước đệm k khác, họ đồ thị khác (SF), n khác; FoundCause.
  3. **Viết báo cáo phát hiện** với phạm vi hiện có. Trước đó cần lặp lại tìm kiếm prior art, như đã ghi ở sổ claim.

## 7. Đính chính diễn giải (21/11, sau review của user)

Số liệu và nhãn không đổi. User đã tính lại năm ước lượng, CI, p-value và Holm, và kết quả khớp: cả năm CONFIRMED. User cũng xác nhận chín file đóng băng khớp mã băm.

| # | Chỗ | Bản trước | Sửa thành |
|---|---|---|---|
| 1 | §3, CDFM RFF | "với ngưỡng của k0, số cạnh tăng (+5.07), tức điểm dịch lên" | "có thêm cặp vượt ngưỡng k0". Điều đó chưa chứng minh toàn bộ phân phối điểm dịch lên |
| 2 | §2 | "Độ nhạy: … cho cùng kết luận với phép kiểm t" | "Kiểm tra độ nhạy". Quyết định xác nhận chỉ đến từ phép kiểm đã khóa và Holm |
