# P-N2 HELD2: luật xác nhận (bản nháp v0, chưa khóa, 21/11/2026)

> **Trạng thái:** **NHÁP, chưa khóa.** Luật chỉ có hiệu lực sau khi user duyệt, commit và push. Việc đó phải xảy ra trước khi bất kỳ input HELD2 nào được sinh ra. Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §9 kèm lý do, và không được dựa trên metric đã thấy.
> **Nguồn:**
>
> - luật exploratory [v1](PN2_rules_exploratory_vi.md) (§10 quy định HELD2);
> - [kết quả EXP2](PN2_EXP2_results_vi.md) (§7, §8, §10);
> - quyết định của user ngày 21/11.
>
> **Phạm vi:** HELD2 xác nhận **dấu** của năm hiệu ứng REP đã chọn. Nó không xác lập cơ chế bên trong model. Nó cũng không xác nhận nhánh R; R chỉ là phân tích phụ.

## 0. Quy trình

1. User duyệt bản nháp này. Khóa: commit và push.
2. Viết code HELD2 dưới dạng **file mới**, không sửa các file đã đóng băng ở `fddfadd`. Các file đó vẫn được import nguyên trạng.
3. Kiểm code đọc trên dữ liệu EXP2 (§7). Đóng băng (snapshot mới kèm SHA-256), commit, push.
4. Chạy HELD2. Input chỉ được sinh ra lúc chạy, sau bước 3.
5. Kiểm hoàn tất (§6), rồi mới đọc bằng code đã đóng băng.

## 1. Dữ liệu

- **Hệ:** seed = 430000 + 1000 × ô + r, với r = 0, …, 14.
  - 15 hệ mỗi ô, 120 hệ tổng, 60 mỗi họ.
  - Hệ đích sinh như P-N1 và EXP2.
  - Base này đã đặt chỗ từ luật v1 và không trùng tập nào trước đó. Quy tắc thay seed (+500) không chạm tới r khác hay ô khác.
- **Input:**
  - k0;
  - e = 0;
  - e = e_T (e = 1 cho ô có e_T = 1, e = 2 cho ô có e_T = 2).

  Bộ sinh khối đệm và các định nghĩa giữ nguyên như luật v1 §3, §5.
- **Model:** AVICI và CDFM, gọi như EXP2. Không chạy PC/GES.
- **Nhánh R:** như luật v1 §8, với α đã khóa (Fisher-z 0.05, HSIC 0.01), chạy trên cùng 120 hệ và ba input.
- **Số output kỳ vọng:** AVICI 360 lần chạy thường + 360 lần chạy R; CDFM cũng vậy. Tổng 1 440.
- **Chi phí dự trù:** 2–3 giờ.

## 2. Năm giả thuyết (khóa)

Tất cả dùng contrast **REP**: D_i = Y_i(e = e_T) − Y_i(e = 0) trên lần chạy thường. Định nghĩa của Y theo luật v1 §5.

| ID | Model | Họ | Y | Dấu dự đoán |
|---|---|---|---|---|
| HA1 | AVICI | tuyến tính | m NATIVE (số cạnh dự đoán trên khối đích) | NEG |
| HA2 | AVICI | RFF | m NATIVE | NEG |
| HC1 | CDFM | RFF | ngưỡng NATIVE | POS |
| HA5 | AVICI | RFF | F1 ở top-m0, với m0 = m NATIVE ở k0 | NEG |
| HC4 | CDFM | RFF | AUROC trên các cặp của khối đích | NEG |

Với HA5, hệ nào có m0 = 0 bị loại khỏi phép kiểm; số hệ bị loại được báo.

## 3. Phép kiểm (khóa)

Cho mỗi giả thuyết, gọi σ = +1 nếu dự đoán POS, −1 nếu NEG. Trong họ tương ứng có 4 ô c, mỗi ô có n_c hệ (15, trừ hệ bị loại).

1. **Ước lượng:** θ̂ = Σ_c w_c · D̄_c, với w_c = 1/4. Đây là trung bình cân bằng theo ô; khi không có hệ bị loại, nó bằng trung bình thường.
2. **Sai số chuẩn theo ô thiết kế:** SE² = Σ_c a_c, với a_c = w_c² · s_c² / n_c. Ở đây s_c² là phương sai mẫu trong ô (ddof = 1).
3. **Thống kê:** t = σ · θ̂ / SE, đã định hướng để chiều dự đoán là dương.
4. **Bậc tự do Welch–Satterthwaite:** df = (Σ_c a_c)² / Σ_c [a_c² / (n_c − 1)].
5. **p-value một phía:** p = P(T_df ≥ t), tính bằng `scipy.stats.t.sf(t, df)`.
   - Trường hợp suy biến SE = 0: p = 0 nếu σθ̂ > 0, ngược lại p = 1. Trường hợp này được báo riêng.
6. **Holm** ở mức familywise 0.05 trên đúng năm p-value:
   - sắp p tăng dần: p_(1) ≤ … ≤ p_(5);
   - bác bỏ H_(j) khi p_(j) ≤ 0.05 / (5 − j + 1);
   - dừng ở lần không bác bỏ đầu tiên.
7. **Nhãn:**
   - **CONFIRMED:** bị Holm bác bỏ, tức xác nhận dấu dự đoán;
   - **NOT_CONFIRMED:** không bị bác bỏ.

   Không có nhãn "bác bỏ giả thuyết". Nếu θ̂ ngược dấu, nhãn vẫn là NOT_CONFIRMED, kèm ghi chú "ước lượng ngược dấu".

**Giả định và giới hạn của phép kiểm:**

- Đây là phép kiểm xấp xỉ mẫu lớn trên trung bình theo ô, chịu được phương sai khác nhau giữa các ô. Nó cần xấp xỉ chuẩn của các trung bình ô (n_c = 15), không cần giả định đối xứng.
- Contrast của số cạnh là rời rạc và có thể lệch. Vì vậy có thêm phép kiểm độ nhạy ở §4. Phép kiểm độ nhạy không thay quyết định Holm.
- Không dùng sign-flip làm phép kiểm chính: nó cần giả định đối xứng hoặc khả năng hoán đổi phù hợp dưới null, và trung bình bằng 0 không đủ.

## 4. Báo cáo mô tả đi kèm (không thuộc bộ Holm)

- **Cho mỗi giả thuyết:**
  - θ̂ kèm CI 95% hai phía, theo t với df Satterthwaite;
  - nhãn cỡ theo biên thực tiễn của luật v1 §6 (SMALL/LARGE/UNCLEAR). 120 hệ là để kiểm dấu, không bảo đảm vượt biên;
  - CI bootstrap phân tầng (lấy mẫu lại trong từng ô, 2000 lần, seed 20261121) làm phép kiểm độ nhạy;
  - kết quả tách theo ô và theo d_T.
- **CDFM RFF:** phân rã hậu nghiệm số cạnh NATIVE ở REP, lấy ngưỡng của e = 0 làm mốc. Phần do điểm là số cạnh của điểm ở e_T với ngưỡng của e = 0, trừ số cạnh ở e = 0. Phần do ngưỡng là phần còn lại. Đây là phân rã theo mốc đã chọn, không phải nguyên nhân.
- **Các Y khác** của luật v1 ở REP (F1, TP, FP, |Δm|, AP, FROZEN, FIXED), chỉ mô tả.

## 5. Nhánh R (phân tích phụ, không thuộc bộ Holm)

- **REP sau R** cho Δm, F1 ở top-m0 (vẫn dùng mốc m0 trước R), AUROC và F1. Báo θ̂, CI 95% và nhãn cỡ, như §4.
  - Ngưỡng NATIVE sau R chỉ báo mô tả theo thành phần, như luật v1 §8.1.
- **Giá tại k0:** F1 sau R tại k0 trừ F1 trước R tại k0, theo model và họ, kèm CI và nhãn cỡ (biên 0.03).
- **Chất lượng sau R:** F1 sau R ở e = 0 và ở e = e_T, so với F1 k0 ban đầu (trước R), kèm CI và nhãn cỡ.
- **Lỗi sàng lọc:** gộp, tách và số cạnh chéo giả, theo họ và điều kiện.
- **Theo từng hệ:** phân phối |Δm| ở REP sau R (tối đa, tỉ lệ hệ có |Δm| ≥ 2). Trung bình SMALL không có nghĩa bất biến ở từng hệ.
- **Kết luận cho R** dùng đúng ngôn ngữ của luật v1 §10.3: "làm giảm thay đổi" và "cách sửa có ích". Không gọi đó là kết quả đã được xác nhận.

## 6. Kiểm hoàn tất trước khi đọc (khóa)

Chỉ đọc kết quả khi tất cả các điều sau đều đạt:

- đủ 1 440 output (AVICI 720, CDFM 720), mỗi model 360 lần chạy thường và 360 lần chạy R;
- 0 job lỗi trong log;
- mã băm input của mọi output khớp input sinh lại;
- cổng đóng băng ghi `ok: true` ở cả đầu và cuối lượt, cùng commit đóng băng và cùng mã băm SHA256SUMS.

Script kiểm là file riêng, nằm trong snapshot.

## 7. Code và kiểm code trước khi đóng băng

**Code mới** (không sửa file đã đóng băng ở `fddfadd`):

- `held2.py`: hệ và input của HELD2;
- `run2_held2.py`: runner thường và R, gọi model như `run2.py`;
- `analyze_held2.py`: phép kiểm §3 và báo cáo §4–§5;
- `held2_completeness.py`;
- `verify_freeze_held2.py`;
- `run_held2.sh`.

Snapshot mới ở `code_held2/`, gồm cả các file phụ thuộc không đổi (`common2.py`, `screen.py`, `alpha.json`) để cổng kiểm luôn mã băm của chúng.

**Kiểm code đọc:** chạy `analyze_held2.py` ở chế độ kiểm trên 40 hệ EXP2, chỉ với ba input.

- Ước lượng điểm phải trùng các giá trị REP đã báo ở EXP2: HA1 −3.95, HA2 −3.90, HC1 +0.159, HA5 −0.040, HC4 −0.039.
- p-value và Holm tính trên EXP2 chỉ để kiểm code, không phải kết quả.

## 8. Đọc kết quả

- Báo nhãn CONFIRMED hoặc NOT_CONFIRMED cho từng giả thuyết, kèm p-value, ngưỡng Holm, θ̂, CI và nhãn cỡ.
- Kết luận chỉ ở mức dấu, trong phạm vi: hai checkpoint, dữ liệu tổng hợp ER, n = 500, k = 20.
- Không được viết:
  - "cơ chế đã được xác lập";
  - "R đã được xác nhận";
  - "mọi model học sẵn đều bị".

## 9. Nhật ký (append-only sau khi khóa)

- **v0, 21/11/2026:** bản nháp, theo quyết định của user ngày 21/11.
