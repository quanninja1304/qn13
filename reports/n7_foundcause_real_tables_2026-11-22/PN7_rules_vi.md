# P-N7: FoundCause trên hai bảng thật, gap 4 (luật v1, khóa ngày 22/11/2026)

> **Trạng thái:** **v1, ĐÃ KHÓA** bằng commit chứa dòng này. Commit được push trên nhánh công khai, cùng bản nháp v0 (`125ce6f`), trước khi có bất kỳ output nào của FoundCause trên hai bảng thật.
>
> - v1 là bản nháp v0 cộng ba chỉnh sửa theo review của user ngày 22/11 (§12).
> - Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §12 kèm lý do, và không được dựa trên output đã thấy.
>
> **Nguồn:**
>
> - gap 4 của [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md) §2, và C11;
> - [P-N5](../n5_real_data_consistency_2026-11-22/PN5_rules_vi.md) cho bảng, tiền xử lý, đệm và phép kiểm;
> - số thiết kế ở [`design/pn7_design_inputs.py`](design/pn7_design_inputs.py) và [`design/pn7_design_inputs.json`](design/pn7_design_inputs.json). Script này chỉ đọc output đã đóng băng của P-N5 và log thời gian của P-N1, không chạy model.
>
> **Quyết định của user ngày 22/11:**
>
> | Điểm | Quyết định |
> |---|---|
> | Gap 4 (lượt 6) | GO cho một thiết kế thu gọn, nếu việc thêm model kiểm được một claim cụ thể; đo ngân sách trước lượt chính; không chặn việc viết |
> | Phương án (lượt 7) | B: hai bảng, mỗi bảng đủ 20 lần sinh của P-N5, chạy thành hai lượt. Không giảm số lần sinh chỉ để vừa một lượt |
> | Tham chiếu lịch | Giữ, với cách mô tả sửa ở v1 (§3) |
> | Lượt chính | Duyệt trước, khi các cổng đạt và ước tính mỗi lượt ≤ 3 giờ. Không đọc contrast hay đổi thiết kế giữa hai lượt. Vượt ngân sách hoặc một cổng thất bại thì dừng và báo |
> | Push | Gộp `125ce6f` với commit khóa v1, rồi đóng băng code theo §10 |

## 0. Câu hỏi và điều không thể kết luận

- **Claim được kiểm: C11 cho model thứ ba.** Trên hai bảng thật đã cố định của P-N5, thêm 20 cột Gauss độc lập có làm skeleton khối thật của FoundCause đổi nhiều hơn đối chứng cổ điển đổi nhiều hơn ở từng lần sinh, tức max(PC, GES) theo từng lần sinh, không?
- **Phạm vi của P7-1 (sửa ở v1):**
  - P7-1 kiểm độ bất ổn của **toàn bộ pipeline mặc định** của FoundCause, có điều kiện trên lịch suy luận base 42 của gói.
  - Nó **không** tách tác động của thông tin trong các cột thêm vào khỏi các thay đổi tính toán nội bộ khi D đổi (§2): hoán vị cột của từng lượt trong ensemble, và nhiễu tie-break.
  - Đây vẫn là một phép kiểm hữu ích: nó đo độ bất ổn mà người dùng gặp khi gọi model theo mặc định.
- **Dữ liệu dùng lại (sửa ở v1):**
  - input của P-N7 là input của P-N5 (hai bảng, 20 lần sinh đệm Gauss ở k = 20), đã dùng cho AVICI, CDFM, PC và GES;
  - đây **không** phải dữ liệu held-out mới; cái mới chỉ là output của FoundCause trên các input đó;
  - hai giả thuyết của P-N7 tạo thành một family Holm riêng.
- **Logic:** như P-N5. Cột thêm vào là cột tổng hợp, độc lập với khối thật theo thiết kế, nên quan hệ trong khối thật không đổi. Một bộ ước lượng hữu hạn mẫu vẫn không bắt buộc cho output trùng hệt. Phép thử đo **độ bất ổn**, không đo độ chính xác.
- **Lý do chọn:**
  - C11 hiện chỉ có AVICI và CDFM; bản thảo đang ghi rằng FoundCause chưa chạy trên bảng thật;
  - FoundCause đã có trong venv và đã chạy ở P-N1, nên không phải cài gì;
  - input, phép kiểm và output PC/GES của P-N5 đã đóng băng, nên giữ được tính tương đương giữa các phương pháp.
- **Chỉ k = 20:**
  - dải huấn luyện D ∈ [2, 50] đã được user xác minh trực tiếp ở §2 và Appendix G của FoundCause v2;
  - đó là dải huấn luyện được công bố, **không** phải giới hạn kỹ thuật: mã của gói chỉ cảnh báo khi d > 51 (V-code, `foundcause.py`). Không chạy k = 40 (D = 51) là lựa chọn phạm vi.
- **Không kết luận được:**
  - bất kỳ điều gì về độ chính xác của FoundCause, PC hay GES trên hai bảng;
  - rằng mọi model học sẵn đều bất ổn;
  - k = 40, đệm có cấu trúc, hay biến có sẵn trong dữ liệu thật;
  - bất kỳ điều gì về cơ chế ngưỡng của CDFM hay cách sửa R-L đối với FoundCause: P-N7 chỉ mở rộng bằng chứng về độ bất ổn trên bảng thật;
  - phần nào của độ bất ổn đến từ thông tin trong cột thêm vào, phần nào từ thay đổi tính toán nội bộ khi D đổi;
  - so sánh cỡ hiệu ứng giữa FoundCause và AVICI hoặc CDFM như một phép kiểm: chỉ mô tả.

## 1. Dữ liệu

- Hai bảng của P-N5 (Sachs CD3/CD28 và Wine trắng). Giữ nguyên 500 hàng đã chọn, normal-score theo hạng, và cùng khối thật X_R. Mã băm input phải khớp `checks/inputs5.json` của P-N5.
- **Input:** k0 và k = 20 với đệm Gauss (`k20_e0`), đủ 20 lần sinh r = 0, …, 19 của P-N5, cho mỗi bảng. Input sinh lại bằng `assemble5` đã đóng băng.
- **Dùng lại, không phải held-out mới** (§0).
- **Đối chứng cổ điển:** output PC và GES của P-N5 trên đúng các input đó, đã đóng băng và đã được xem ở P-N5. Không chạy lại. Mã băm của chúng được đóng băng cùng code.

## 2. Model, lịch suy luận và cách đọc (khóa)

- **Cấu hình như P-N1:**
  - API gốc của gói: `foundcause.predict(model, X, cpu, n_runs=10, temperature=1.0, max_samples=5000)`, với mặc định `min_agreement=0.5`, `threshold=0.5`, `sanitize=True`;
  - checkpoint có SHA-256 như manifest của P-N1; 4 luồng, như các lượt FoundCause ở P-N1;
  - chạy tuần tự, không chạy song song với tiến trình nào khác.
- **Lịch suy luận của gói** (V-code, `foundcause.py`, đọc ngày 22/11). Ở mỗi lượt `run_i` trong 10 lượt:
  - một `numpy.random.RandomState(42 + run_i)` chọn mẫu con không hoàn lại ceil(0.9 · 500) = 450 trong 500 hàng. Phép chọn này chỉ phụ thuộc số hàng và seed, không phụ thuộc D;
  - cùng RNG đó sinh một hoán vị của D cột, nên hoán vị phụ thuộc D;
  - RNG của torch cũng được seed `42 + run_i`; nó cho nhiễu tie-break khi xử lý giá trị trùng.
- **Hệ quả:**
  - giữ base và đổi D (k0 sang k = 20): mẫu con hàng giữ nguyên ở cả 10 lượt (user đã kiểm), còn hoán vị cột và nhiễu tie-break có thể đổi;
  - đổi base trên cùng input: cả ba thứ đều đổi.
- **Skeleton NATIVE:** ma trận `adjacency` của FoundCause OR chuyển vị, trên 55 cặp của khối thật, như `metrics.skel_native` đã đóng băng của P-N1.
- **Lịch khác cho tham chiếu:** adapter `predict_sched(base)` đã đóng băng của P-N1 (`fc_adapter.py`). Adapter chỉ thay `42 + run_i` bằng `base + run_i` ở cả ba chỗ trong mã. Điều kiện dùng như P-N1: ở base 42, xác suất, agreement và adjacency trùng API trong 10⁻⁶.
- **Không** dùng đồ thị tham chiếu nào của Sachs.

## 3. Biến đo

- **flips:** số trong 55 cặp của khối thật có trạng thái skeleton khác k0.
- **Contrast theo lần sinh:** D_r = flips_FC,r − max(flips_PC,r, flips_GES,r) ở `k20_e0`. Max lấy theo từng lần sinh, như P5-1.
- **Tham chiếu biến động của toàn bộ lịch suy luận** (mô tả, không thuộc bộ Holm; sửa ở v1):
  - ở k0 của mỗi bảng, chạy adapter với base 1042, 2042, 3042 và 4042;
  - với mỗi base b, flips_sched,b là số cặp khác giữa output API (base 42) và output base b, trên cùng input k0;
  - đổi base làm đổi cả mẫu con hàng, hoán vị cột và nhiễu tie-break (§2). Vì vậy tham chiếu này đo biến động của toàn bộ lịch, **không** phải đối chứng chỉ riêng cho hoán vị cột, vốn là thứ đổi khi D đổi ở base cố định;
  - báo **cả bốn giá trị**, trung bình và giá trị lớn nhất, đặt cạnh flips ở k = 20;
  - **không** dùng giá trị lớn nhất làm ngưỡng thống kê, và **không** lấy nó trừ khỏi flips do thêm cột.
- **Mô tả:**
  - số cạnh ở k0 (m0) và Δm;
  - Δp, tức trung bình |p_ij − p_ij(k0)| trên các cặp có thứ tự của khối thật;
  - phân bố flips qua các lần sinh;
  - đặt cạnh số của AVICI và CDFM ở P-N5 để mô tả, không kiểm.

## 4. Giả thuyết (khóa): hai giả thuyết, một family Holm riêng

| ID | Bảng | Thành phần | Dự đoán | Phép kiểm |
|---|---|---|---|---|
| P7-1S | Sachs | E_r[D_r] | > 0 | t ghép cặp một phía qua 20 lần sinh (df = 19) |
| P7-1W | Wine | E_r[D_r] | > 0 | như trên |

- SE = 0 thì ghi DEGENERATE, dùng p = 1 và không xác nhận.
- Holm ở mức familywise 0.05 trên đúng hai p-value. Family này tách riêng khỏi các family của P-N5 và P-N6.
- **Nhãn cỡ** (mô tả): biên 1 cặp, như P-N5. CI và nhãn cỡ không được Holm bảo vệ.
- **Cách đọc:**
  - CONFIRMED chỉ xác nhận dấu của trung bình có điều kiện qua các lần sinh đệm, trên bảng, cách chọn hàng và tiền xử lý đã cố định, và trên lịch base 42 của gói;
  - 20 lần sinh không phải 20 bộ dữ liệu thật;
  - t là xấp xỉ, vì flips là số đếm rời rạc có nhiều giá trị trùng.

## 5. Mô tả (không thuộc bộ Holm)

- Bảng flips theo lần sinh (trung bình, nhỏ nhất, lớn nhất), m0, Δm và Δp cho FoundCause.
- Tham chiếu biến động lịch ở k0 (§3): bốn giá trị, trung bình, lớn nhất; đặt cạnh flips ở k = 20.
- Đặt cạnh flips của AVICI và CDFM trên cùng lần sinh, lấy từ P-N5. Chỉ mô tả.
- Nếu FoundCause báo cột trùng hay cột bị bỏ (`duplicates`, `dropped`), ghi lại theo từng input.

## 6. Kiểm hoàn tất trước khi đọc

- mọi job của cả hai lượt có đúng một trạng thái kết thúc `ok`, không có `error` hay `budget_stop`;
- mã băm input khớp input sinh lại và khớp `inputs5.json`; khối thật trùng từng bit giữa các input;
- **chỉ số hàng** (sửa ở v1; không chạy thêm model): với mỗi bảng, ở cả 10 lượt của lịch base 42, chỉ số hàng được chọn ở k0 trùng chỉ số ở mọi input `k20_e0`. Chỉ số được tính lại theo đúng công thức trong mã nguồn đã băm của gói (§7, G3c);
- chạy lại k0 trên mỗi bảng: output trùng từng bit;
- adapter ở base 42 trùng API trong 10⁻⁶ ở k0 của mỗi bảng;
- mã băm output PC và GES của P-N5 khớp bản đóng băng;
- cổng đóng băng `ok` ở đầu và cuối mỗi lượt, cùng commit.

Nếu một điều kiện sai: báo lỗi, không đọc kết quả, không nới luật. **Adapter không đạt thì dừng**: không tự bỏ tham chiếu rồi tiếp tục (sửa ở v1).

## 7. Cổng (DEV7, trên bảng thay thế mô phỏng của P-N5)

DEV7 dùng bảng thay thế mô phỏng `standin` (d = 11) và hai lần sinh đệm Gauss ở k = 20 của DEV5 (base 470000). Không chạm hai bảng thật.

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | Input DEV7 sinh lại khớp mã băm DEV5 trong log của P-N5; 42 input bảng thật sinh lại khớp `inputs5.json` | khớp |
| G2 | Cấu hình FoundCause như P-N1: chạy lại một input DEV của P-N1 (`DEV-c0-r0`, k0, API), so với output đã lưu của P-N1 | trùng từng bit. Nếu không trùng: báo độ lệch tối đa và dừng để user quyết, không tự chọn dung sai |
| G3 | Tất định trong cùng phiên: chạy lại k0 của DEV7 | trùng từng bit |
| G3b | Adapter ở base 42 so với API, ở k0 của DEV7 | trong 10⁻⁶ (luật P-N1); không đạt thì dừng |
| G3c | Chỉ số hàng: kiểm văn bản mã nguồn đã băm (seed `42 + run_i`, công thức số hàng lấy, phép chọn trước hoán vị), rồi tính lại chỉ số ở 10 lượt cho k0 và mọi input `k20_e0` của DEV7 và hai bảng | công thức có đúng như mô tả; chỉ số trùng nhau |
| G4 | Cách đọc skeleton khớp `metrics.skel_native` đã đóng băng | khớp |
| G5 | Đối chứng: tính lại flips của AVICI, CDFM và max(PC, GES) từ output P-N5; hiệu theo lần sinh trùng 20 giá trị đã báo của P5-1, ở cả hai bảng và cả hai model | khớp chính xác |
| G6 | Code kiểm định: t một phía, DEGENERATE, Holm với 2 giả thuyết, so với cài đặt tham chiếu | khớp |
| G7 | Code đọc chạy hết trên DEV7, kể cả nhánh tham chiếu lịch (một base), chỉ kiểm cấu trúc | không in hay ghi giá trị |
| G8 | Thời gian và bộ nhớ trên DEV7; ước tính mỗi lượt chính: trung vị mỗi lần gọi theo D × số lần gọi × 1.10 + 300 s | mỗi lượt ≤ 3 giờ; nếu vượt thì dừng và báo user |

## 8. Power và ngân sách (phương án B)

**Power** ([`design/pn7_design_inputs.json`](design/pn7_design_inputs.json)):

- Hiệu ứng thật của FoundCause trên hai bảng chưa biết. Số dưới đây dùng contrast theo lần sinh của AVICI và CDFM ở P-N5 làm số tham chiếu; đó không phải bảo đảm.
- Power là tỉ lệ bootstrap có p < 0.025, tức ngưỡng Holm chặt nhất với hai giả thuyết; B = 4 000. User tính lại và các số khớp trong sai số mô phỏng.

| Số tham chiếu (P-N5) | Trung bình, SD | R = 20 |
|---|---|---|
| Sachs, AVICI / CDFM | +2.65, 0.88 / +1.30, 0.98 | 1.00 / 1.00 |
| Wine, AVICI / CDFM | +5.30, 4.92 / +10.90, 2.34 | 1.00 / 1.00 |
| Sachs, CDFM, trung bình giảm một nửa | +0.65, 0.98 | 0.89 |
| Wine, AVICI, trung bình giảm một nửa | +2.65, 4.92 | 0.67 |

**Ngân sách:**

- Ước tính từ log FoundCause của P-N1 trên cùng máy, 4 luồng: khoảng 157 s mỗi lần gọi ở D = 11 và 352 s ở D = 31.
- Mỗi lượt (một bảng): k0, 20 lần sinh ở k = 20, một lần chạy lại k0, adapter ở base 42, và bốn base tham chiếu; tổng 27 lần gọi.
- Ước tính = tổng thời gian các lần gọi × 1.10 + 300 s, tức 2.57 giờ mỗi lượt. User tính lại được khoảng 5.13 giờ cho hai lượt.
- **DEV7:** k0, hai lần sinh ở k = 20, chạy lại k0, adapter ở base 42, một base tham chiếu, và một input DEV của P-N1 cho G2. Khoảng 25 phút.
- Số thật đo ở G8, trước lượt chính.

## 9. Đọc kết quả

- **Câu được viết** (ví dụ): "Trên 500 hàng đã chọn của bảng [Sachs/Wine], với tiền xử lý đã khóa và pipeline mặc định của FoundCause, thêm 20 cột Gauss độc lập làm skeleton trên khối thật đổi trạng thái trung bình … trong 55 cặp. Đối chứng cổ điển đổi nhiều hơn ở từng lần sinh đổi trung bình … cặp."
- **Không được viết:**
  - bất kỳ câu nào về độ chính xác, hay rằng FoundCause sai;
  - "mọi model học sẵn đều bất ổn";
  - kết luận cho k = 40, cho đệm có cấu trúc, hay cho biến có sẵn trong dữ liệu thật;
  - rằng FoundCause bất ổn hơn hay kém hơn AVICI hoặc CDFM: chỉ mô tả, không kiểm;
  - rằng một giả thuyết không được xác nhận chứng minh FoundCause ổn định;
  - rằng độ bất ổn là do thông tin trong cột thêm vào: P7-1 không tách phần đó khỏi thay đổi tính toán nội bộ khi D đổi;
  - rằng tham chiếu bốn base là đối chứng cho hoán vị cột, là ngưỡng, hay có thể lấy trừ khỏi flips;
  - rằng các input là dữ liệu held-out mới;
  - rằng kết quả về cơ chế ngưỡng của CDFM hay về cách sửa R-L áp dụng cho FoundCause;
  - rằng CI hay nhãn cỡ được Holm bảo vệ.

## 10. Quy trình

1. User duyệt v0 với ba chỉnh sửa (22/11). Khóa v1: commit và push trên nhánh công khai, gộp với `125ce6f`, trước khi có output FoundCause nào trên hai bảng thật.
2. Viết code dưới dạng file mới trong `artifacts/n7_runs/pn7/`. Import nguyên trạng `common5.py` của P-N5, cùng `common.py`, `metrics.py` và `fc_adapter.py` của P-N1.
3. Chạy DEV7 và G1–G8. Đóng băng code, phụ thuộc và mã băm output PC/GES của P-N5; commit, push.
4. **Lượt chính,** đã được user duyệt trước nếu các cổng đạt và ước tính mỗi lượt không vượt 3 giờ:
   - hai lượt nối tiếp nhau trong một script: Sachs, rồi Wine; chạy tuần tự, không chạy gì song song;
   - mỗi lượt có cổng đóng băng ở đầu và cuối, và mốc dừng 3 giờ tính từ đầu lượt đó;
   - không đọc contrast hay đổi thiết kế giữa hai lượt;
   - vượt ngân sách hay một cổng thất bại thì dừng và báo user.
5. Kiểm hoàn tất (§6), rồi đọc bằng code đã đóng băng.

## 11. Điều đã chốt trước khi khóa

- Phương án B; giữ tham chiếu lịch theo §3; hai giả thuyết, một family Holm riêng; không thêm đệm có cấu trúc.
- Lượt chính đã được duyệt trước theo các điều kiện ở §10.

## 12. Nhật ký (append-only sau khi khóa)

- **v0, 22/11/2026 (`125ce6f`):** bản nháp, theo quyết định của user ngày 22/11 (lượt 6).
- **v1, 22/11/2026 (khóa):** user chọn phương án B và cho GO sau ba chỉnh sửa (lượt 7).
  1. **§3, tham chiếu lịch:**
     - đổi base làm đổi cả mẫu con hàng, hoán vị cột và nhiễu tie-break, nên bốn base ở k0 đo biến động của toàn bộ lịch, không phải đối chứng riêng cho hoán vị cột;
     - báo cả bốn giá trị, trung bình và cực đại; không dùng cực đại làm ngưỡng, không lấy nó trừ khỏi flips;
     - §2 mô tả lịch suy luận theo mã nguồn.
  2. **§0, §4, phạm vi:**
     - P7-1 kiểm độ bất ổn của toàn bộ pipeline mặc định, có điều kiện trên base 42, và không tách tác động của thông tin cột thêm vào khỏi thay đổi tính toán nội bộ khi D đổi;
     - hai giả thuyết là một family Holm riêng;
     - ghi rõ input là input của P-N5 được dùng lại, không phải held-out mới.
  3. **§6, §7, cổng adapter:**
     - adapter không đạt thì dừng, không tự bỏ tham chiếu rồi tiếp tục; sửa mâu thuẫn giữa §6 và §7 của v0;
     - thêm G3c: chỉ số hàng được chọn trùng nhau giữa k0 và mọi input `k20_e0`, kiểm không cần chạy model.
  - **Làm rõ, không đổi thiết kế:**
    - dải D ∈ [2, 50] đã được user xác minh ở §2 và Appendix G của FoundCause v2; đó là dải huấn luyện được công bố, không phải giới hạn kỹ thuật (mã chỉ cảnh báo khi d > 51);
    - P-N7 không mở rộng kết luận về cơ chế CDFM hay cách sửa R-L sang FoundCause;
    - G5 kiểm bộ đối chứng bằng cách so hiệu theo lần sinh với 20 giá trị đã báo của P5-1, ở cả AVICI và CDFM;
    - user tính lại ngân sách (khoảng 5.13 giờ cho hai lượt) và các số power tham chiếu.
  - **Mốc khóa:** `7bc40f8`, push lúc 2026-11-22T14:28:20Z (GitHub activity API), cùng `125ce6f`.
- **Đóng băng code, 22/11/2026,** trước khi có output FoundCause nào trên hai bảng thật.
  - **Code mới** trong `artifacts/n7_runs/pn7/`: `common7.py`, `run7.py`, `stats7.py`, `analyze7.py`, `completeness7.py`, `gates7.py`, `verify_freeze7.py`, `freeze7.py`, `run_dev7.sh`, `run_pn7.sh`.
  - **Snapshot** [`code/`](code/):
    - `SHA256SUMS` gồm 10 file code và 9 phụ thuộc. Các phụ thuộc là `common.py`, `metrics.py`, `fc_adapter.py` và bốn file cấu hình của P-N1, `common2.py` của P-N2, `common5.py` của P-N5. Mỗi phụ thuộc phải khớp mã băm trong snapshot gốc của nó.
    - `DEPS_SHA256.json` có 219 mã băm: nguồn gói `foundcause` và `avici`; checkpoint FoundCause (khớp manifest checkpoint của P-N1); hai file dữ liệu; output P-N5 của PC, GES, AVICI và CDFM trên đúng các input; đọc kết quả và log DEV5 của P-N5; output và log DEV của P-N1 dùng cho G2. Thêm mã băm của manifest dữ liệu, `inputs5.json`, manifest checkpoint, cùng phiên bản gói.
  - **DEV7** (bảng thay thế `standin`, base 470000): 7 lần gọi FoundCause, 0 lỗi, 1 612 s. Không chạm hai bảng thật.
  - **Cả mười cổng đạt** ([`checks/gates7.json`](checks/gates7.json)):
    - G1: input DEV7 khớp log DEV5; 42/42 input bảng thật khớp `inputs5.json`.
    - G2: chạy lại input `DEV-c0-r0` ở k0 của P-N1; output trùng từng bit với output đã lưu của P-N1, độ lệch 0 ở `probs`, `adj_native`, `agreement`, `threshold` và `C`. Cấu hình vì vậy trùng P-N1.
    - G3: chạy lại k0 trùng từng bit. G3b: adapter ở base 42 trùng API, độ lệch 0. G3c: dòng mã về lịch đúng như mô tả; chỉ số hàng (450/500) trùng giữa k0 và cả 42 input có đệm.
    - G4: cách đọc skeleton khớp `metrics.skel_native`.
    - G5: bộ đối chứng tái lập chính xác 20 giá trị P5-1 ở cả hai bảng và hai model.
    - G6: các ca kiểm của code thống kê đều đúng.
    - G7: code đọc chạy hết trên DEV7, kể cả nhánh tham chiếu lịch; kiểm hoàn tất DEV7 đạt.
    - G8: trung vị 174.8 s mỗi lần gọi ở D = 11 và 378.8 s ở D = 31. Ước tính 2.77 giờ mỗi lượt (27 lần gọi, × 1.10 + 300 s), dưới 3 giờ; hai lượt 5.54 giờ. Bộ nhớ đỉnh 2.09 GB.
  - Theo trình tự user đã duyệt: các cổng đạt và ước tính mỗi lượt không vượt 3 giờ, nên chạy hai lượt chính sau khi push commit đóng băng.
