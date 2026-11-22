# P-N7: FoundCause trên hai bảng thật, gap 4 (luật v0, nháp ngày 22/11/2026)

> **Trạng thái:** **v0, NHÁP, chưa khóa.**
>
> - Chưa viết code, chưa sinh input mới, chưa chạy FoundCause trên bảng thật nào.
> - Khóa v1 sau khi user duyệt, và trước khi có bất kỳ output nào của FoundCause trên hai bảng thật.
>
> **Nguồn:**
>
> - gap 4 của [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md) §2, và C11;
> - [P-N5](../n5_real_data_consistency_2026-11-22/PN5_rules_vi.md) cho bảng, tiền xử lý, đệm và phép kiểm;
> - số thiết kế ở [`design/pn7_design_inputs.py`](design/pn7_design_inputs.py) và [`design/pn7_design_inputs.json`](design/pn7_design_inputs.json). Script này chỉ đọc output đã đóng băng của P-N5 và log thời gian của P-N1, không chạy model.
>
> **Quyết định của user ngày 22/11 (lượt 6):** GO cho một thiết kế thu gọn của gap 4, nếu việc thêm model kiểm được một claim cụ thể. Đo ngân sách trước lượt chạy chính. Gap 4 không chặn việc viết.

## 0. Câu hỏi và điều không thể kết luận

- **Claim được kiểm: C11 cho model thứ ba.** Trên hai bảng thật đã cố định của P-N5, thêm 20 cột Gauss độc lập có làm skeleton khối thật của FoundCause đổi nhiều hơn đối chứng cổ điển đổi nhiều hơn ở từng lần sinh, tức max(PC, GES) theo từng lần sinh, không?
- **Lý do chọn:**
  - C11 hiện chỉ có AVICI và CDFM; bản thảo đang ghi rằng FoundCause chưa chạy trên bảng thật;
  - FoundCause đã có trong venv và đã chạy ở P-N1, nên không phải cài gì;
  - input, phép kiểm và output PC/GES của P-N5 đã đóng băng, nên giữ được tính tương đương giữa các phương pháp.
- **Logic:** như P-N5. Cột thêm vào là cột tổng hợp, độc lập với khối thật theo thiết kế, nên quan hệ trong khối thật không đổi. Một bộ ước lượng hữu hạn mẫu vẫn không bắt buộc cho output trùng hệt. Phép thử đo **độ bất ổn**, không đo độ chính xác.
- **Riêng với FoundCause: nhiễu lịch ensemble** (luật P-N1 v2.1 §A5).
  - Mỗi lần chạy trong ensemble dùng một hoán vị nội bộ có seed `42 + run_i`. Khi D đổi, các hoán vị này cũng đổi.
  - Vì vậy một phần thay đổi khi thêm cột có thể là nhiễu lịch, không phải tác động riêng của cột thêm vào.
  - P-N1 xử lý bằng τ_sched, tức độ lệch giữa lịch base 42 và base 1042 ở k0.
  - P-N7 giữ giả thuyết so với đối chứng cổ điển, như C11, và thêm một **tham chiếu nhiễu lịch** ở dạng mô tả (§3).
- **Không kết luận được:**
  - bất kỳ điều gì về độ chính xác của FoundCause, PC hay GES trên hai bảng;
  - rằng mọi model học sẵn đều bất ổn;
  - k = 40: D = 51 nằm ngoài dải D ∈ [2, 50] mà tác giả công bố (dải này cần đối chiếu nguồn gốc trước khi viết vào bài);
  - đệm có cấu trúc, và cách sửa R-L với FoundCause: không chạy trong P-N7;
  - so sánh cỡ hiệu ứng giữa FoundCause và AVICI hoặc CDFM như một phép kiểm: chỉ mô tả.

## 1. Dữ liệu

- Hai bảng của P-N5 (Sachs CD3/CD28 và Wine trắng). Giữ nguyên 500 hàng đã chọn, normal-score theo hạng, và cùng khối thật X_R. Mã băm input phải khớp `checks/inputs5.json` của P-N5.
- **Input:** k0 và k = 20 với đệm Gauss (`k20_e0`), dùng đúng các lần sinh r = 0, …, R − 1 của P-N5. Input sinh lại bằng `assemble5` đã đóng băng.
- **Số lần sinh R:** user chọn một trong ba phương án ở §8, trước khi khóa v1.
- **Đối chứng cổ điển:** output PC và GES của P-N5 trên đúng các input đó, đã đóng băng và đã được xem ở P-N5. Không chạy lại. Mã băm của chúng được đóng băng cùng code.

## 2. Model và cách đọc (khóa ở v1)

- **Cấu hình như P-N1:**
  - API gốc của gói: `foundcause.predict(model, X, cpu, n_runs=10, temperature=1.0, max_samples=5000)`, lịch mặc định của gói;
  - checkpoint có SHA-256 như manifest của P-N1; 4 luồng, như các lượt FoundCause ở P-N1;
  - chạy tuần tự, không chạy song song với tiến trình nào khác.
- **Skeleton NATIVE:** ma trận `adjacency` của FoundCause OR chuyển vị, trên 55 cặp của khối thật, như `metrics.skel_native` đã đóng băng của P-N1.
- **Lịch khác cho tham chiếu nhiễu lịch:** adapter `predict_sched(base)` đã đóng băng của P-N1 (`fc_adapter.py`). Adapter này chỉ thay seed lịch `42 + run_i` bằng `base + run_i`. Điều kiện dùng như P-N1: ở base 42, xác suất, agreement và adjacency trùng API trong 10⁻⁶.
- **Không** dùng đồ thị tham chiếu nào của Sachs.

## 3. Biến đo

- **flips:** số trong 55 cặp của khối thật có trạng thái skeleton khác k0.
- **Contrast theo lần sinh:** D_r = flips_FC,r − max(flips_PC,r, flips_GES,r) ở `k20_e0`. Max lấy theo từng lần sinh, như P5-1.
- **Tham chiếu nhiễu lịch** (mô tả, không thuộc bộ Holm):
  - ở k0 của mỗi bảng, chạy adapter với base 1042, 2042, 3042 và 4042;
  - với mỗi base b, flips_sched,b là số cặp khác giữa output API (base 42) và output base b, trên cùng input k0;
  - báo trung bình và giá trị lớn nhất của bốn số này, đặt cạnh flips ở k = 20;
  - đây là nhiễu do đổi lịch trên cùng input; nó không tách được phần nhiễu lịch nằm trong flips khi D đổi.
- **Mô tả:**
  - số cạnh ở k0 (m0) và Δm;
  - Δp, tức trung bình |p_ij − p_ij(k0)| trên các cặp có thứ tự của khối thật;
  - phân bố flips qua các lần sinh;
  - đặt cạnh số của AVICI và CDFM ở P-N5 để mô tả, không kiểm.

## 4. Giả thuyết (khóa ở v1): hai giả thuyết, Holm 0.05

| ID | Bảng | Thành phần | Dự đoán | Phép kiểm |
|---|---|---|---|---|
| P7-1S | Sachs | E_r[D_r] | > 0 | t ghép cặp một phía qua R lần sinh (df = R − 1) |
| P7-1W | Wine | E_r[D_r] | > 0 | như trên |

- SE = 0 thì ghi DEGENERATE, dùng p = 1 và không xác nhận.
- Holm ở mức familywise 0.05 trên đúng hai p-value.
- **Nhãn cỡ** (mô tả): biên 1 cặp, như P-N5. CI và nhãn cỡ không được Holm bảo vệ.
- **Cách đọc:**
  - CONFIRMED chỉ xác nhận dấu của trung bình có điều kiện qua các lần sinh đệm, trên bảng, cách chọn hàng và tiền xử lý đã cố định;
  - R lần sinh không phải R bộ dữ liệu thật;
  - t là xấp xỉ, vì flips là số đếm rời rạc có nhiều giá trị trùng.

## 5. Mô tả (không thuộc bộ Holm)

- Bảng flips theo lần sinh (trung bình, nhỏ nhất, lớn nhất), m0, Δm và Δp cho FoundCause.
- Tham chiếu nhiễu lịch ở k0 (§3), đặt cạnh flips ở k = 20.
- Đặt cạnh flips của AVICI và CDFM trên cùng lần sinh, lấy từ P-N5. Chỉ mô tả.
- Nếu FoundCause báo cột trùng hay cột bị bỏ (`duplicates`, `dropped`), ghi lại theo từng input.

## 6. Kiểm hoàn tất trước khi đọc

- mọi job có đúng một trạng thái kết thúc `ok`, không có `error` hay `budget_stop`;
- mã băm input khớp input sinh lại và khớp `inputs5.json`; khối thật trùng từng bit giữa các input;
- chạy lại k0 trên mỗi bảng: output trùng từng bit;
- adapter ở base 42 trùng API trong 10⁻⁶ ở k0 của mỗi bảng; nếu không, không có tham chiếu nhiễu lịch, và phần đó chỉ được báo là không có;
- mã băm output PC và GES của P-N5 khớp bản đóng băng;
- cổng đóng băng `ok` ở đầu và cuối mỗi lượt, cùng commit.

Nếu một điều kiện sai: báo lỗi, không đọc kết quả, không nới luật.

## 7. Cổng (DEV7, trên bảng thay thế mô phỏng của P-N5)

DEV7 dùng bảng thay thế mô phỏng (d = 11) và hai lần sinh đệm của DEV5 ở P-N5. Không chạm hai bảng thật.

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | Input DEV7 và các input bảng thật của phương án đã chọn (42 với phương án B) sinh lại khớp mã băm của P-N5 | khớp |
| G2 | Cấu hình FoundCause như P-N1: chạy lại một input DEV của P-N1, so với output đã lưu của P-N1 | trùng từng bit. Nếu không trùng: báo độ lệch tối đa và dừng để user quyết, không tự chọn dung sai |
| G3 | Tất định trong cùng phiên: chạy lại k0 của DEV7 | trùng từng bit |
| G3b | Adapter ở base 42 so với API, ở k0 của DEV7 | trong 10⁻⁶ (luật P-N1) |
| G4 | Cách đọc skeleton khớp `metrics.skel_native` đã đóng băng | khớp |
| G5 | max(PC, GES) theo lần sinh, tính lại từ output P-N5, khớp các thành phần đã báo của P5-1 | khớp chính xác |
| G6 | Code kiểm định: t một phía, DEGENERATE, Holm với 2 giả thuyết, so với cài đặt tham chiếu | khớp |
| G7 | Code đọc chạy hết trên DEV7, chỉ kiểm cấu trúc | không in hay ghi giá trị |
| G8 | Thời gian và bộ nhớ trên DEV7; ước tính cho lượt chính theo phương án đã chọn: trung vị mỗi lần gọi × số job × 1.10 + 300 s | mỗi lượt ≤ 3 giờ; nếu vượt thì báo user |

## 8. Power và ngân sách (số thiết kế; chờ user chọn phương án)

**Power** ([`design/pn7_design_inputs.json`](design/pn7_design_inputs.json)):

- Hiệu ứng thật của FoundCause trên hai bảng chưa biết. Số dưới đây dùng contrast theo lần sinh của AVICI và CDFM ở P-N5 làm số tham chiếu; đó không phải bảo đảm.
- Power là tỉ lệ bootstrap có p < 0.025, tức ngưỡng Holm chặt nhất với hai giả thuyết; B = 4 000.

| Số tham chiếu (P-N5) | Trung bình, SD | R = 10 | R = 12 | R = 16 | R = 20 |
|---|---|---|---|---|---|
| Sachs, AVICI | +2.65, 0.88 | 0.99 | 1.00 | 1.00 | 1.00 |
| Sachs, CDFM | +1.30, 0.98 | 0.99 | 1.00 | 1.00 | 1.00 |
| Wine, AVICI | +5.30, 4.92 | 1.00 | 1.00 | 1.00 | 1.00 |
| Wine, CDFM | +10.90, 2.34 | 1.00 | 1.00 | 1.00 | 1.00 |
| Sachs, CDFM, trung bình giảm một nửa | +0.65, 0.98 | 0.49 | 0.62 | 0.79 | 0.89 |
| Wine, AVICI, trung bình giảm một nửa | +2.65, 4.92 | 0.22 | 0.30 | 0.51 | 0.67 |

**Ngân sách:**

- Ước tính từ log FoundCause của P-N1 trên cùng máy, 4 luồng. Trung vị mỗi lần gọi: 146 s ở D = 10, 339 s ở D = 30, 437 s ở D = 40.
- Một đường thẳng khớp các trung vị cho khoảng 157 s ở D = 11 và 352 s ở D = 31.
- Ước tính = tổng thời gian các lần gọi × 1.10 + 300 s, như G9 của P-N6.
- Mỗi bảng có thêm một lần chạy lại k0, và 5 lần gọi ở k0 cho tham chiếu nhiễu lịch: adapter ở base 42 để kiểm, rồi bốn base.

| Phương án | Lượt chạy | Ước tính mỗi lượt | Tổng |
|---|---|---|---|
| A′: cả hai bảng, R = 10 (r = 0–9) | 1 | 2.90 giờ | 2.90 giờ |
| A: cả hai bảng, R = 12 | 1 | 3.33 giờ, **vượt 3 giờ** | — |
| **B: mỗi bảng một lượt, R = 20** (đúng 20 lần sinh của P-N5) | 2 | 2.57 giờ | khoảng 5.1 giờ |
| C: một bảng, R = 20 | 1 | 2.57 giờ | 2.57 giờ |

- **Đề xuất: B.**
  - B dùng đúng 20 lần sinh mà C11 đã dùng cho AVICI và CDFM, nên so sánh tương đương hơn.
  - Power cũng cao nhất nếu hiệu ứng của FoundCause nhỏ hoặc nhiễu.
  - Hai lượt dùng cùng bản đóng băng. Kết quả chỉ đọc sau khi cả hai lượt xong.
- **Nếu không muốn tổng thời gian khoảng 5.1 giờ:** chọn A′ (R = 10) trong một lượt. Ước tính 2.90 giờ sát mốc 3 giờ, nên G8 có thể không đạt.
- **Số thật đo ở G8 trên DEV7, trước lượt chính:**
  - DEV7 cần khoảng 5 lần gọi FoundCause: k0, hai lần sinh ở k = 20, một lần chạy lại, và adapter ở base 42. Tổng khoảng 20 phút;
  - G2 thêm một lần gọi ở D = 10, khoảng 2.5 phút.

## 9. Đọc kết quả

- **Câu được viết** (ví dụ): "Trên 500 hàng đã chọn của bảng [Sachs/Wine], với tiền xử lý đã khóa, thêm 20 cột Gauss độc lập làm skeleton của FoundCause trên khối thật đổi trạng thái trung bình … trong 55 cặp. Đối chứng cổ điển đổi nhiều hơn ở từng lần sinh đổi trung bình … cặp."
- **Không được viết:**
  - bất kỳ câu nào về độ chính xác, hay rằng FoundCause sai;
  - "mọi model học sẵn đều bất ổn";
  - kết luận cho k = 40, cho đệm có cấu trúc, hay cho biến có sẵn trong dữ liệu thật;
  - rằng FoundCause bất ổn hơn hay kém hơn AVICI hoặc CDFM: chỉ mô tả, không kiểm;
  - rằng một giả thuyết không được xác nhận chứng minh FoundCause ổn định;
  - rằng toàn bộ flips ở k = 20 là tác động riêng của cột thêm vào: một phần có thể là nhiễu lịch ensemble khi D đổi, và tham chiếu ở k0 không tách được phần đó;
  - rằng CI hay nhãn cỡ được Holm bảo vệ.

## 10. Quy trình

1. User duyệt v0 và chọn phương án ở §8.
2. Khóa v1: commit và push trên nhánh công khai, trước khi có output FoundCause nào trên hai bảng thật.
3. Viết code dưới dạng file mới trong `artifacts/n7_runs/pn7/`. Import nguyên trạng `common5.py` của P-N5, và `common.py` cùng `metrics.py` của P-N1.
4. Chạy DEV7 và G1–G8. Đóng băng code, phụ thuộc và mã băm output PC/GES của P-N5; commit, push.
5. Chạy lượt chính nếu các cổng đạt và ước tính mỗi lượt không vượt 3 giờ. Bước này cần user duyệt trước. Chạy tuần tự, không chạy gì song song.
6. Kiểm hoàn tất (§6), rồi đọc bằng code đã đóng băng.

## 11. Câu hỏi cho user (trước khi khóa v1)

1. Phương án ở §8: B (đề xuất), A′ hay C?
2. Giữ tham chiếu nhiễu lịch ở k0, 5 lần gọi mỗi bảng (đề xuất)? Nếu bỏ, mỗi lượt bớt khoảng 15 phút, nhưng flips của FoundCause khó đọc hơn.
3. Giữ đúng hai giả thuyết (Holm trên 2), hay thêm mô tả đệm có cấu trúc ở k = 20? Phần mô tả đó tốn thêm khoảng 2 giờ cho mỗi bảng; agent không đề xuất thêm.
4. Có duyệt trước lượt chính, với điều kiện G1–G8 đạt và ước tính mỗi lượt không vượt 3 giờ, như P-N6?

## 12. Nhật ký (append-only sau khi khóa)

- **v0, 22/11/2026:** bản nháp, theo quyết định của user ngày 22/11 (lượt 6).
