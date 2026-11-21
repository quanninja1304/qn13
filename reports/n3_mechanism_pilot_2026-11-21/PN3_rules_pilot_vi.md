# P-N3: pilot cơ chế, phạm vi hẹp (bản nháp v0, chưa khóa, 21/11/2026)

> **Trạng thái:** **NHÁP, chưa khóa.** Luật chỉ có hiệu lực sau khi user duyệt, commit và push, trước khi chạy bất kỳ phép tính nào của pilot. Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §8 kèm lý do.
> **Nền:**
>
> - HELD2 xác nhận dấu của năm hiệu ứng REP ([kết quả](../n2_context_mechanism_2026-11-20/PN2_HELD2_results_vi.md)).
> - Prior art của pilot: [ghi chú 21/11](N3_prior_art_attention_2026-11-21_vi.md).
>
> **Ưu tiên theo user:** CDFM RFF (bộ chọn ngưỡng) và AVICI tuyến tính (attention).
> **Bản chất:** pilot **exploratory**. Kết quả chỉ để chọn dự đoán. Nếu tìm được can thiệp phân biệt được, dự đoán phải được khóa rồi kiểm trên seed mới (§7).

## 0. Dữ liệu chung

- **Hệ:** 40 hệ của EXP2 (seed 420000 + 1000 × ô + r, r = 0, …, 4), với output đã có ở lần chạy thường.
  - Phần A dùng 20 hệ RFF.
  - Phần B dùng 20 hệ tuyến tính.
- **Input:** k0, e = 0, e = e_T, sinh bằng bộ sinh đã đóng băng.
- **Contrast chính:** REP = Y(e = e_T) − Y(e = 0), như luật P-N2.
- **Ước lượng:** trung bình cân bằng theo ô, kèm CI 95% theo t với sai số chuẩn phân tầng (như luật HELD2 §3). Không có phép kiểm xác nhận trong pilot.

## 1. Phần A: CDFM RFF, bộ chọn ngưỡng (chỉ tính lại, không chạy model)

**Câu hỏi.** Phần nào của ma trận điểm, nằm ngoài khối đích, làm ngưỡng NATIVE tăng?

**Thiết kế giai thừa 2³ trên ma trận xác suất D×D** đưa vào `suggest_threshold`. Chia ma trận thành ba phần, mỗi phần lấy từ output ở e = 0 hoặc ở e = e_T của cùng một hệ:

- **T:** khối đích, d_T × d_T;
- **P:** khối đệm, 20 × 20;
- **X:** hai khối chéo, đích × đệm và đệm × đích, đổi cùng nhau.

Với mỗi hệ có 8 ma trận lai H(a_T, a_P, a_X), với a ∈ {e = 0, e = e_T}. Tính logit ngưỡng ℓ(H) bằng đúng công thức và trọng số đã lưu của CDFM.

**Biến đo** (theo hệ, rồi lấy trung bình cân bằng theo ô):

- **hiệu ứng chính** của T, P, X lên ℓ, mỗi cái lấy trung bình qua mức của hai phần còn lại, cùng các tương tác;
- **phần đóng góp theo từng đặc trưng** của bộ chọn ngưỡng cho từng hiệu ứng chính;
- **số cạnh trên khối đích** khi áp ngưỡng của từng ma trận lai lên điểm khối đích ở e_T, để đổi ra đơn vị cạnh;
- **phản thực "ngưỡng cục bộ":** ngưỡng tính chỉ từ khối đích, với D = d_T. Đo REP của số cạnh dưới ngưỡng này, rồi so với phần do điểm (+2.30 ở HELD2).

**Dự đoán** (sinh từ phân rã hậu nghiệm trên HELD2, chưa kiểm):

- hiệu ứng chính của P chiếm phần lớn mức tăng của ℓ, chủ yếu qua đặc trưng `mean`;
- hiệu ứng của X nhỏ;
- dưới ngưỡng cục bộ, REP của số cạnh gần với phần do điểm.

**Gate A0:** tái tạo ngưỡng đã lưu từ ma trận gốc, với sai lệch tuyệt đối tối đa ≤ 1e-12. Trên HELD2, sai lệch đã thấy là 3.3e-16.

## 2. Phần B: AVICI tuyến tính, can thiệp attention

**Câu hỏi.** Mức giảm số cạnh đi qua nội dung truyền vào, qua chuẩn hóa attention, hay qua tương tác giữa hai thứ đó?

**Can thiệp.** Chỉ áp ở 8 lớp attention theo trục biến của AVICI `scm-v0` (16 khối xen kẽ). Chỉ áp cho **query của biến đích** đối với **key/value của biến đệm**; query của biến đệm giữ nguyên.

| Tên | Định nghĩa | Tương ứng prior art |
|---|---|---|
| PLAIN | Không can thiệp; đường tính attention đã sửa | — |
| V0 | Giữ softmax trên mọi key (mẫu số có biến đệm), rồi đặt trọng số tới key đệm bằng 0 sau softmax. Nội dung của đệm bị triệt, phần pha loãng giữ nguyên | Value zeroing (Mohebbi et al. 2023) |
| KO | Loại key đệm khỏi cả tử số lẫn mẫu số (mask trước softmax) | Attention knockout (Geva et al. 2023) |

Mỗi can thiệp chạy theo hai cách:

- ở **cả 8 lớp** (V0-all, KO-all);
- ở **từng lớp một** (V0-ℓ, KO-ℓ, ℓ = 1, …, 8), các lớp khác chạy PLAIN.

**Gate:**

- **B0:** PLAIN tái lập output gốc của AVICI **trùng từng bit**, trên 6 input EXP2 (k0, e = 0, e = e_T của 2 hệ). Không đạt thì dừng phần B.
- **B1:** cây tham số không đổi; không có tham số mới, không thiếu tham số.
- **B2:** KO-all là kiểm tra kỹ thuật. Xác suất khối đích phải bằng của k0, với sai lệch tuyệt đối tối đa ≤ 1e-6. Đây không phải kết quả.

**Biến đo cho mỗi can thiệp I:**

- REP_I của Δm, AUROC và F1 ở top-m0. Mốc m0 là số cạnh ở k0 của lần chạy gốc.
- Phần hiệu ứng bị xóa: f_I = 1 − REP_I / REP_PLAIN, với Δm.
- **Kiểm phá khả năng dự đoán:** ΔF1 và ΔAUROC của khối đích ở e = 0 dưới I, so với PLAIN ở e = 0. Can thiệp có |ΔF1| > 0.03 hoặc |ΔAUROC| > 0.03 ở e = 0 bị gắn cờ "phá dự đoán". f_I của can thiệp đó không được diễn giải.

**Quy tắc đọc** (định trước, exploratory; mọi tỉ lệ dùng ước lượng điểm, kèm CI):

| Kết quả | Nhãn |
|---|---|
| V0-all xóa ≥ 50% hiệu ứng Δm và không phá dự đoán | **kênh nội dung**: cần nội dung của biến đệm |
| V0-all xóa < 25% trong khi KO-all xóa ≥ 75% | **kênh chuẩn hóa**: đi qua mẫu số, tức phần pha loãng |
| Cả hai chỉ xóa một phần, không thuộc hai dòng trên | **hỗn hợp** |
| Có một lớp ℓ mà V0-ℓ hoặc KO-ℓ một mình xóa ≥ 50% và không phá dự đoán | **khu trú theo lớp** (tính tới rò rỉ qua lớp trước, như Geva et al. đã cảnh báo) |

## 3. Chi phí ước tính

- **Phần A:** vài phút, vì chỉ tính lại trên output đã lưu.
- **Phần B:** 20 hệ × 2 input (e = 0, e = e_T) × 19 cấu hình (PLAIN, 2 bản "all", 16 bản theo lớp), cộng k0. Khoảng 780 lần chạy × khoảng 5 giây, tức khoảng 1–1.5 giờ.

## 4. Điểm dừng (theo user)

- **Không phân biệt được:** chỉ KO-all xóa được hiệu ứng, còn V0 và các can thiệp theo lớp không phân biệt được lời giải thích. Khi đó giữ kết luận ở mức "kênh thay đổi", rồi chuyển sang mở rộng có chọn lọc hoặc viết bài.
- **Phân biệt được:** có một can thiệp phân biệt rõ, tức nhãn "kênh nội dung", "kênh chuẩn hóa" hoặc "khu trú theo lớp" với CI đủ hẹp. Khi đó khóa dự đoán rồi kiểm trên seed mới (§7).
- **Phần A:** nếu hiệu ứng chính của P chiếm phần lớn Δℓ, kênh ngưỡng của CDFM được mô tả ở mức "đặc trưng nào của bộ chọn ngưỡng". Phần này là tính toán trên một hàm đã biết; kiểm trên seed mới chỉ cần nếu muốn claim độ lớn.

## 5. Không được nói

- "N1 là attention sink." Chưa có bằng chứng.
- "Value zeroing hay knockout là phương pháp mới."
- "Kết quả theo lớp loại trừ rò rỉ qua lớp trước."
- "Phần A giải thích vì sao model đổi điểm." Phần A chỉ phân tích bộ chọn ngưỡng.

## 6. Code (sau khi khóa)

- **Phần A:** script mới, đọc output EXP2 đã lưu và trọng số calibrator của CDFM.
- **Phần B:** module mới thay `hk.MultiHeadAttention.__call__` bằng bản chép nguyên văn của Haiku, có thêm cờ can thiệp. Nhận lớp theo trục biến qua số token bằng D. Tái tạo forward cho mỗi cấu hình, để tránh cache của jit.
- Kiểm khả thi trước, rồi chạy gate B0–B2.
- Mọi code là file mới; không sửa file đã đóng băng của P-N2.

## 7. Nếu cần xác nhận

Khóa dự đoán (can thiệp, lớp, contrast, metric, dấu, phép kiểm) trong một luật mới, rồi chạy trên seed mới (đề xuất base 440000), trước khi viết claim cơ chế.

## 8. Nhật ký

- **v0, 21/11/2026:** bản nháp, theo đề xuất của user ngày 21/11.
