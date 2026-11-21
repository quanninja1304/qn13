# P-N3: pilot cơ chế, phạm vi hẹp (v1, khóa ngày 21/11/2026)

> **Trạng thái:** **v1, ĐÃ KHÓA** bằng commit chứa dòng này, push trước khi chạy bất kỳ phép tính nào của pilot.
>
> - Bản nháp v0 ở commit `769e9b2`.
> - User duyệt kèm năm chỉnh sửa (§8).
> - Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §8 kèm lý do.
>
> **Nền:**
>
> - HELD2 xác nhận dấu của năm hiệu ứng REP ([kết quả](../n2_context_mechanism_2026-11-20/PN2_HELD2_results_vi.md)).
> - Prior art của pilot: [ghi chú 21/11](N3_prior_art_attention_2026-11-21_vi.md). User đã đối chiếu thêm Value Zeroing §3.2, attention knockout §5 và phần Limitations.
>
> **Bản chất:** pilot **exploratory**, chạy trên EXP2, để tìm và chọn lời giải thích. Mọi ngưỡng ở đây là ngưỡng sàng lọc để quản lý pilot, không phải tiêu chuẩn thống kê. Dự đoán chọn ra phải được khóa rồi kiểm trên seed mới, base 440000 (§7).

## 0. Dữ liệu chung

- **Hệ:** 40 hệ của EXP2 (seed 420000 + 1000 × ô + r, r = 0, …, 4).
  - Phần A dùng 20 hệ RFF.
  - Phần B dùng 20 hệ tuyến tính.
- **Input:** k0, e = 0, e = e_T, sinh bằng bộ sinh đã đóng băng.
- **Contrast chính:** REP = Y(e = e_T) − Y(e = 0). θ là REP trung bình cân bằng theo ô; CI 95% theo t với sai số chuẩn phân tầng (như luật HELD2 §3).
- **Ghép cặp:** mọi đối chiếu ghép cặp tính trên **chính EXP2**, với mốc ngưỡng ghi rõ. Không dùng số của HELD2 làm mốc so sánh.
- Pilot không có phép kiểm xác nhận.

## 1. Phần A: CDFM RFF, bộ chọn ngưỡng (chỉ tính lại, không chạy model)

**Câu hỏi.** Phần nào của ma trận điểm, nằm ngoài khối đích, làm ngưỡng NATIVE tăng?

**Thiết kế giai thừa 2³.** Ma trận xác suất D×D đưa vào `suggest_threshold` được chia làm ba phần, mỗi phần lấy từ output ở e = 0 hoặc ở e = e_T của cùng một hệ:

- **T:** khối đích;
- **P:** khối đệm;
- **X:** hai khối chéo, đổi cùng nhau.

Với mỗi hệ có 8 ma trận lai H(a_T, a_P, a_X). Logit ngưỡng ℓ(H) tính bằng đúng công thức và trọng số đã lưu của CDFM.

**Biến đo** (theo hệ, rồi lấy trung bình cân bằng theo ô):

- **Hiệu ứng chính và tương tác** theo contrast chuẩn của thiết kế 2³. Hiệu ứng chính không tự động cộng thành chênh lệch hai đầu khi có tương tác.
- **Đóng góp Shapley** của ba nhóm T, P, X cho chênh lệch hai đầu Δℓ = ℓ(e_T, e_T, e_T) − ℓ(e = 0, e = 0, e = 0).
  - Tính từ tám ma trận; φ_T + φ_P + φ_X = Δℓ đúng.
  - Vì ℓ tuyến tính theo các đặc trưng, φ của mỗi nhóm được tách tiếp theo từng đặc trưng.
  - Chỉ dùng φ khi nói một nhóm "chiếm phần lớn" chênh lệch.
- **Số cạnh trên khối đích** khi áp ngưỡng của từng ma trận lai. Báo với hai mốc điểm: điểm khối đích ở e = e_T, và điểm khối đích ở e = 0.
- **Phản thực "ngưỡng cục bộ":** ngưỡng tính chỉ từ khối đích (D = d_T).
  - Đây là một **chính sách phản thực riêng**: nó thay cả thống kê lẫn D. Chỉ báo REP của số cạnh dưới chính sách đó.
  - **Không** được xem là bằng chứng đã tách được phần do điểm.
  - Phần do điểm (mốc là ngưỡng ở e = 0) được tính lại trên EXP2 và báo riêng.

**Dự đoán** (sinh từ phân rã hậu nghiệm trên HELD2, chưa kiểm): φ_P chiếm phần lớn Δℓ, chủ yếu qua đặc trưng `mean`; φ_X nhỏ.

**Gate A0:** tái tạo ngưỡng đã lưu từ ma trận gốc, với sai lệch tuyệt đối tối đa ≤ 1e-12.

## 2. Phần B: AVICI tuyến tính, can thiệp attention

**Câu hỏi.** Mức giảm số cạnh nhạy với đường value, với chuẩn hóa attention, hay chưa phân biệt được?

**Xác định lớp.** Theo định danh tường minh: chỉ số khối b = 0, …, 15 lấy từ thứ tự trong vòng lặp của model. Trục biến ứng với b chẵn; lớp ℓ = b/2 + 1, với ℓ = 1, …, 8. Kèm một phép kiểm: ở b chẵn, độ dài trục token bằng D; ở b lẻ, bằng n.

**Can thiệp.** Chỉ áp ở các lớp theo trục biến, chỉ cho **query của biến đích** đối với **key/value của biến đệm**.

| Tên | Định nghĩa | Prior art |
|---|---|---|
| PLAIN | Không can thiệp; đường tính attention đã sửa | — |
| V0 | Softmax trên mọi key, rồi đặt trọng số tới key đệm bằng 0 sau softmax. Mẫu số giữ nguyên, đường value của đệm bị triệt | Value zeroing |
| KO | Loại key đệm khỏi cả tử số lẫn mẫu số (mask trước softmax) | Attention knockout |

Mỗi can thiệp chạy ở cả 8 lớp (V0-all, KO-all) và ở từng lớp một (V0-ℓ, KO-ℓ).

**Gate:**

- **B0:** PLAIN tái lập output gốc **trùng từng bit**, trên 6 input EXP2.
- **B1:** cây tham số trùng output gốc về tên, hình dạng **và giá trị** (trùng từng bit).
- **B2:** KO-all là kiểm tra kỹ thuật. Xác suất khối đích bằng của k0, với sai lệch tuyệt đối tối đa ≤ 1e-6.
- **B3:** can thiệp là no-op khi không có đệm. Ở k0, V0-all và KO-all trùng từng bit với PLAIN.
- **B4:** ghi lại số lớp nhận được và phép kiểm độ dài trục.
- **B5:** đo thời gian, **kể cả biên dịch JIT** cho mỗi cấu hình và mỗi hình dạng input. Báo user trước khi chạy đầy đủ nếu ước tính vượt 3 giờ.

**Biến đo cho mỗi can thiệp I:**

- **θ_I có dấu:** REP của Δm (chính), AUROC và F1 ở top-m0 (mốc m0 là số cạnh ở k0 của lần chạy gốc).
- **Chênh lệch ghép cặp** θ_I − θ_PLAIN, kèm CI.
- **Mức giảm độ lớn:** a_I = 1 − |θ_I| / |θ_PLAIN|, tính trên Δm. Mọi trường hợp **đảo chiều** được ghi rõ (θ_I và θ_PLAIN khác dấu).
- **CI của a_I:** bootstrap 2000 lần, lấy mẫu lại hệ trong từng ô, **đồng thời** cho mọi cấu hình trên cùng các hệ (ghép cặp), seed 20261121. Nếu CI của θ_PLAIN chứa 0, a_I không được dùng để phân loại.
- **Kiểm suy giảm chất lượng:** ΔF1 và ΔAUROC của khối đích dưới I so với PLAIN, xét **riêng ở e = 0 và ở e = e_T**, kèm CI.
  - Gắn cờ "suy giảm" khi ước lượng điểm ΔF1 < −0.03 hoặc ΔAUROC < −0.03, ở bất kỳ điều kiện nào.
  - Cải thiện **không** bị gắn cờ: KO-all có thể đưa F1 ở e = 0 về gần k0, với F1 k0 0.687 so với 0.540 ở e = 0 trên EXP2.
  - Không bị gắn cờ theo ước lượng điểm không có nghĩa đã chứng minh chất lượng được bảo toàn.

**Quy tắc đọc** (sàng lọc exploratory). Chỉ xét can thiệp không bị gắn cờ suy giảm và không đảo chiều có ý nghĩa, tức CI của θ_I không nằm hẳn ở phía ngược dấu θ_PLAIN.

| Điều kiện | Nhãn |
|---|---|
| KO-all xóa được hiệu ứng | **Chỉ là kiểm tra kỹ thuật**; không đủ để chọn một cơ chế đi tiếp |
| Cùng một lớp ℓ: a(V0-ℓ) ≤ 25% và a(KO-ℓ) ≥ 75%, và CI của θ_{KO-ℓ} − θ_{V0-ℓ} loại 0 | **Ứng viên nhạy với chuẩn hóa tại lớp ℓ** |
| a(V0-all) ≥ 50%, hoặc a(V0-ℓ) ≥ 50% ở một lớp | **Ứng viên nhạy với đường value** (toàn bộ, hoặc tại lớp ℓ). Không viết "nội dung đệm là cần thiết" |
| a(V0-ℓ) ≥ 50% hoặc a(KO-ℓ) ≥ 50% ở một lớp | **Nhạy với can thiệp tại lớp ℓ**. Không phải "nơi duy nhất chứa cơ chế"; vẫn có thể đã có thông tin truyền qua lớp trước |
| Các trường hợp còn lại | **Chưa phân biệt được**. Không tự động gọi là "hỗn hợp" |

## 3. Chi phí ước tính

- **Phần A:** vài phút.
- **Phần B:** khoảng 780 lần chạy × khoảng 5 giây, cộng biên dịch JIT cho 19 cấu hình × 2 hình dạng input (D = 30 và D = 40). Tổng khoảng 1.3–1.8 giờ; đo lại ở B5.

## 4. Điểm dừng

- **Không có ứng viên:** không có ứng viên nào theo §2 (chỉ KO-all thành công, các trường hợp khác chưa phân biệt được). Khi đó giữ kết luận ở mức "kênh thay đổi", rồi chuyển sang mở rộng có chọn lọc hoặc viết bài.
- **Có ứng viên:** khóa dự đoán (can thiệp, lớp, contrast, metric, dấu, phép kiểm) trong một luật mới, rồi kiểm trên seed mới (§7).
- **Phần A:** kênh ngưỡng của CDFM được mô tả ở mức nhóm khối và đặc trưng của bộ chọn ngưỡng, qua φ. Đây là phân tích trên một hàm đã biết; chỉ cần kiểm trên seed mới nếu muốn claim độ lớn.

## 5. Không được nói

- "N1 là attention sink."
- "Value zeroing hay knockout là phương pháp mới."
- "Nội dung đệm là cần thiết."
- "Lớp ℓ là nơi duy nhất chứa cơ chế."
- "Kết quả theo lớp loại trừ rò rỉ qua lớp trước."
- "Phần A giải thích vì sao model đổi điểm."
- "Ngưỡng cục bộ đã tách được phần do điểm."

## 6. Code (sau khi khóa)

- **Phần A:** script mới, đọc output EXP2 đã lưu và trọng số calibrator của CDFM.
- **Phần B:** module mới thay `hk.MultiHeadAttention.__call__` bằng bản chép nguyên văn của Haiku, có thêm cờ can thiệp.
  - Lớp được xác định theo chỉ số khối tường minh.
  - Forward được dựng lại cho mỗi cấu hình, để tránh cache của jit.
- **Thứ tự:** kiểm khả thi và gate B0–B5 trước, rồi đóng băng code (snapshot kèm SHA-256), commit, push, rồi mới chạy pilot.
- Mọi code là file mới; không sửa file đã đóng băng của P-N2.

## 7. Nếu có ứng viên

Khóa dự đoán trong một luật mới, rồi chạy trên seed mới (base 440000), trước khi viết claim cơ chế.

## 8. Nhật ký

- **v0, 21/11/2026 (`769e9b2`):** bản nháp.
- **v1, 21/11/2026 (khóa):** theo review của user.
  - **Quyết định:**
    - giữ ngưỡng 50% / 25% / 75% làm ngưỡng sàng lọc exploratory;
    - ngưỡng chất lượng 0.03 chỉ xét suy giảm;
    - giữ EXP2, giữ base 440000 cho bước kiểm.
  - **Năm chỉnh sửa:**
    1. Cổng chất lượng chỉ gắn cờ suy giảm (ΔF1 hoặc ΔAUROC < −0.03), xét riêng ở e = 0 và e = e_T, kèm CI.
    2. a_I tính bằng mức giảm độ lớn; báo θ có dấu và chênh lệch ghép cặp; ghi đảo chiều; bootstrap ghép cặp trong ô; không phân loại khi CI của θ_PLAIN chứa 0.
    3. KO-all chỉ là kiểm tra kỹ thuật. Nhãn "chuẩn hóa" chỉ theo lớp, kèm CI của chênh lệch ghép cặp. Thay "kênh nội dung" bằng "nhạy với đường value", và "hỗn hợp" bằng "chưa phân biệt được".
    4. CDFM: dùng Shapley khi nói "chiếm phần lớn"; "ngưỡng cục bộ" là chính sách phản thực riêng; mọi đối chiếu ghép cặp tính trên EXP2.
    5. B1 kiểm cả giá trị trọng số; thêm B3 (no-op khi không có đệm), B4 (định danh lớp), B5 (thời gian kể cả JIT).
