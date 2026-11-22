# P-N5: kiểm tính nhất quán trên dữ liệu thật, gap 2 (luật v1, khóa ngày 22/11/2026)

> **Trạng thái:** **v1, ĐÃ KHÓA** bằng commit chứa dòng này. Commit được push trên nhánh công khai trước khi chạy bất kỳ model nào trên hai bảng thật. v1 là bản nháp v0 (`cfe5144`) cộng năm chỉnh sửa theo duyệt của user ngày 22/11 (§12). Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §12 kèm lý do, và không được dựa trên output đã thấy.
> **Nguồn:**
>
> - gap 2 của [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md) §2;
> - quyết định của user ngày 22/11: hai bảng thật và phạm vi;
> - [manifest dữ liệu](DATA_MANIFEST_vi.md).
>
> **Phạm vi:**
>
> - AVICI `scm-v0` và CDFM. PC và GES là đối chứng thực nghiệm, không phải đáp án đúng.
> - Hai bảng thật: Sachs CD3/CD28 và Wine trắng; mỗi bảng 500 hàng chọn trước.
> - k ∈ {0, 20, 40}; đệm Gauss và đệm ER–RFF có cấu trúc, cả hai độc lập với bảng thật theo thiết kế; 20 lần sinh đệm mỗi điều kiện.
>
> **Quyết định của user ngày 22/11:**
>
> - tiền xử lý: normal-score theo hạng rồi z-score, cho cả hai bảng (§1);
> - giữ tám giả thuyết, Holm 0.05, suy luận có điều kiện trên từng bảng cố định (§5);
> - bỏ GES ở k = 40 với đệm có cấu trúc (§3);
> - giữ hàng trùng của Wine như bản phát hành (§1).

## 0. Câu hỏi và điều không thể kết luận

- **Câu hỏi:** trên một bảng thật đã cố định, việc thêm cột tổng hợp độc lập có làm output của AVICI và CDFM trên khối thật đổi nhiều hơn PC và GES không? Ngưỡng của CDFM có tăng khi đệm có cấu trúc, như đã xác nhận trên dữ liệu tổng hợp (P-N4) không?
- **Logic:** cột thêm vào độc lập với khối thật theo thiết kế, nên quan hệ thật trong khối thật không đổi. Một bộ ước lượng hữu hạn mẫu vẫn không bắt buộc cho output trùng hệt. Độ đổi là chẩn đoán độ bền, không phải sai số; **không gọi thay đổi là giảm độ chính xác**.
- **Không kết luận được:**
  - model nào đúng hơn trên dữ liệu thật;
  - bất kỳ điều gì về độ chính xác;
  - khái quát sang bảng khác, cách chọn hàng khác hay cách tiền xử lý khác.
- **Đơn vị thống kê:** lần sinh đệm r = 0, …, 19. Mọi suy luận là có điều kiện trên bảng thật, cách chọn hàng và cách tiền xử lý đã cố định. 20 lần sinh đệm **không** phải 20 bộ dữ liệu thật độc lập.
- **Không dùng đồ thị tham chiếu nào**, kể cả `GroundTruth.csv` trong archive của Sachs.

## 1. Dữ liệu và tiền xử lý (khóa)

- **File:** đúng hai file trong [manifest](DATA_MANIFEST_vi.md). Mọi script kiểm SHA-256 trước khi đọc.
  - Sachs: `cd3cd28.csv`, 853 × 11, SHA-256 `07087f70…b814d0`.
  - Wine: `winequality-white.csv`, 4 898 × 12. Bỏ cột `quality`, còn 11 biến; SHA-256 `76c3f809…169836`.
  - Giữ đúng thứ tự cột như trong file.
- **Chọn 500 hàng:** `rng = default_rng(SeedSequence([20261122, j]))`, với j = 0 cho Sachs và j = 1 cho Wine; lấy `idx = sort(rng.choice(N, 500, replace=False))`.
  - SHA-256 của `idx` (int64), 16 ký tự đầu: Sachs `c2914a4f8500a51f`, Wine `1335a9a588b6d5e3`. Agent tính hai mã này khi kiểm lại số của user (§12); G1 phải tái lập đúng.
- **Hàng trùng:** giữ như bản phát hành, không lọc.
  - Wine có 937 hàng dư sau khi loại trùng trên 11 biến dùng, tức số hàng trừ số vector khác nhau. Trong 500 hàng đã chọn có 10 hàng dư, tức 490 vector khác nhau.
  - Sachs không có hàng trùng, cả trong file lẫn trong 500 hàng đã chọn.
  - Các con số này được báo cùng kết quả. Suy luận qua các lần sinh đệm vẫn có điều kiện trên bảng đã cố định.
- **Tiền xử lý (khóa):** biến đổi normal-score theo hạng cho từng cột của khối thật, tính trên 500 hàng đã chọn.
  - Mỗi giá trị nhận hạng trung bình r khi có giá trị bằng nhau (`rankdata(method='average')`), rồi được đổi thành Φ⁻¹(r / (n + 1)), với n = 500.
  - Sau đó z-score bằng hàm `zscore` của P-N1 (float64 → float32).
  - Kết quả là **X_R** (500 × 11, float32). X_R được lưu lại và dùng nguyên trạng ở mọi input; nó đóng vai khối đích. Input k0 là X_R.
  - **Chỉ áp dụng cho khối thật.** Khối đệm giữ bộ sinh đã chọn (§2) và không đi qua normal-score.
- **Lý do chọn normal-score:**
  - giảm ảnh hưởng của giá trị cực đoan (Sachs có giá trị tới 4 491);
  - áp dụng một quy tắc xác định trước, giống nhau cho cả hai bảng, không chọn theo hình dạng phân phối.
- **Điều normal-score không bảo đảm:**
  - Phân phối chung sau biến đổi không nhất thiết là Gauss. Vì vậy giả định của Fisher-z (PC) và BIC Gauss (GES) không vì thế mà đúng.
  - Kết quả nhất quán của PC trong Harris & Drton (2013) dựa trên giả định nonparanormal, tức Gaussian copula (Định nghĩa 2, Định lý 8).
  - "Rank PC" trong bài đó ước lượng ma trận tương quan bằng tương quan hạng Spearman hoặc Kendall's τ, rồi kiểm tương quan riêng phần bằng một ngưỡng cố định (§4, công thức 9). Đó không phải Fisher-z trên dữ liệu đã normal-score.
  - Do đó PC và GES tiếp tục chỉ là **đối chứng thực nghiệm** trong P-N5.
  - Nguồn: N. Harris, M. Drton, "PC Algorithm for Nonparanormal Graphical Models", *JMLR* 14(105):3365–3383, 2013, <https://www.jmlr.org/papers/v14/harris13a.html>.
- **Phương án thay thế, không chạy:** log rồi z-score cho Sachs, chỉ z-score cho Wine.

## 2. Khối đệm (khóa)

- **Bộ sinh:** các hàm đã đóng băng `pad_params`, `pad_graph`, `pad_data` của `common2.py` (P-N2), họ RFF, s = 1, với k ∈ {20, 40}, như P-N4.
  - Khối đệm là `zscore(pad_data(...))`, tức chuẩn hóa từng cột một lần.
  - Ở k = 20, đường này trùng `padding2` của P-N2; G2 kiểm.
- **Hai kiểu đệm,** dùng chung randomness trong cùng một lần sinh:
  - **Gauss:** mức e = 0, đồ thị rỗng. Mỗi cột sinh từ nhiễu Gaussian độc lập rồi chuẩn hóa từng cột.
  - **Có cấu trúc:** mức e = 2. Đồ thị ER với 2 cạnh kỳ vọng mỗi nút, cơ chế RFF đa biến của AVICI.
- **Seed** của lần sinh r cho bảng j: 460000 + 1000·j + r, với r = 0, …, 19.
  - Khóa luồng `SeedSequence([seed, 20261120, 2])` như P-N2. k = 20 và k = 40 rút từ cùng một luồng, như P-N4.
  - Base 460000 chưa dùng ở tập nào trước: P-N1 dùng 100000–300000, P-N2 dùng 410000–430000, P-N4 dùng 440000 và 450000.
  - Tập cổng DEV5 (§8) dùng base 470000, cũng chưa dùng.
- **Ghép (sửa ở v1):** X = [X_R | P], ghép trực tiếp, **không chuẩn hóa lại toàn bảng**.
  - Hai khối đã được chuẩn hóa riêng từng cột.
  - Ở mọi input, khối thật trùng từng bit với X_R đã lưu, và khối đệm trùng từng bit với output của bộ sinh.
  - **Lý do sửa:** ở v0, X = zscore([X_R | P]) chuẩn hóa X_R lần thứ hai. Trên 500 hàng đã chọn, việc này đổi 97 giá trị của khối thật ở Sachs (tối đa 3.73e−9) và 283 giá trị ở Wine (tối đa 7.45e−9). Điều đó trái yêu cầu trùng từng bit với k0. User phát hiện lỗi này; agent tính lại và ra cùng số.
  - **Khác các pha trước:** ở P-N1, P-N2 và P-N4, khối đích là dữ liệu thô, nên chuẩn hóa toàn bảng chỉ chuẩn hóa khối đích một lần. Trong các pha đó, khối đệm bị chuẩn hóa hai lần. Ở P-N5, khối đệm chỉ chuẩn hóa một lần. Sai khác ở mức làm tròn float32; bộ sinh không đổi.

## 3. Input, thuật toán và trạng thái job

- **Input mỗi bảng:** k0, cộng 2 giá trị k × 2 kiểu đệm × 20 lần sinh, tức 81 input. Hai bảng: 162 input.
- **Thuật toán,** gọi như P-N1 và P-N2:
  - AVICI `scm-v0`: lưu xác suất; NATIVE là ngưỡng 0.5. Chạy 2 luồng.
  - CDFM: `from_pretrained(threshold=None)`, `predict(x, threshold=None, standardize=False)`. Lưu xác suất, logits, ma trận kề NATIVE và ngưỡng NATIVE. Chạy 2 luồng.
  - PC: causal-learn, Fisher-z, α = 0.05, stable. Chạy 1 luồng.
  - GES: causal-learn, BIC Gauss. Chạy 1 luồng.
- Mỗi input chạy đúng một lần cho mỗi thuật toán. Các thuật toán chạy tuần tự, không song song (RAM).
- **Tất định:** k0 của mỗi bảng chạy hai lần cho mỗi thuật toán: lần chính và một lần chạy lại. Hai output phải trùng từng bit.
- **Phạm vi GES (khóa):** GES chạy mọi input, **trừ k = 40 với đệm có cấu trúc**. Ở điều kiện đó, đối chứng cổ điển chỉ có PC, và chỉ ở phần mô tả. Tám giả thuyết ở §5 chỉ cần GES ở k0 và ở k = 20 với đệm Gauss.
- **Số job:** AVICI, CDFM và PC có 82 job mỗi bảng; GES có 62 job mỗi bảng. Tổng cộng 616 job.
- **Thứ tự chạy:** AVICI, CDFM, PC, GES. Trong mỗi thuật toán, input chính chạy trước: k0, lần chạy lại k0, rồi k = 20 với đệm Gauss. Sau đó tới các input còn lại.
- **Trạng thái kết thúc (sửa ở v1):** mỗi job phải ghi đúng một trạng thái kết thúc: `ok`, `timeout` hoặc `error`.
  - **Giới hạn thời gian:** PC và GES có giới hạn 900 giây mỗi job. Mỗi job chạy trong một tiến trình con; quá giới hạn thì tiến trình bị dừng và job ghi `timeout`. AVICI và CDFM không có giới hạn theo job.
  - **Chỗ được phép timeout:** chỉ ở input mô tả của PC và GES, tức k = 20 với đệm có cấu trúc và k = 40 với đệm Gauss; với PC thêm k = 40 với đệm có cấu trúc.
    - Số timeout được báo theo thuật toán, bảng và điều kiện.
    - Thống kê chỉ dùng các lần hoàn tất.
    - **Không gán timeout thành "không đổi"** hay bất kỳ giá trị nào.
  - **Input chính của PC và GES:** k0, lần chạy lại k0, và k = 20 với đệm Gauss, vì P5-1 cần chúng. Nếu một job ở đó timeout, lượt chạy dừng và báo user; không tự đổi quy tắc. Quy tắc này áp dụng cho cả PC và GES.
  - **`error`** không được phép ở bất kỳ job nào. Nếu có, kiểm hoàn tất (§7) không đạt và kết quả không được đọc; báo user.
- **Theo dõi ngân sách trong lượt chạy thật (thêm ở v1):**
  - Runner ghi thời gian đã chạy sau mỗi job.
  - Trước mỗi job, runner kiểm thời gian tính từ đầu lượt, tức mốc `pn5_start` của cổng đóng băng. Nếu đã vượt 3 giờ, runner dừng ở ranh giới job, ghi `budget_stop` và không chạy thuật toán tiếp theo.
  - Khi đó kiểm hoàn tất không đạt; báo user.

## 4. Biến đo

Mọi biến đo tính trên khối thật, so với k0 của cùng thuật toán:

- **Δp** (AVICI, CDFM): trung bình |p_ij − p_ij(k0)| trên 110 cặp có thứ tự của khối thật.
- **flips:** số cặp không thứ tự của khối thật đổi trạng thái skeleton so với k0, theo NATIVE, trên 55 cặp.
  - Skeleton của AVICI: max(p_ij, p_ji) > 0.5.
  - Skeleton của CDFM: hợp của ma trận kề NATIVE và chuyển vị của nó.
  - Skeleton của PC và GES: mọi loại cạnh của đồ thị output trên toàn bảng, giới hạn vào khối thật.
  - Với CDFM báo thêm theo FIXED (0.5) và FROZEN (ngưỡng ở k0); hai cách đọc này chỉ là mô tả.
- **Δm = m − m0** và **|Δm|**, với m0 là số cạnh skeleton ở k0.
- **Δτ** (CDFM): ngưỡng NATIVE trừ ngưỡng ở k0.
- **Bối cảnh:** m0 của từng thuật toán, luôn báo cạnh flips. **Độ ổn định không chứng minh độ chính xác:** một thuật toán có thể không đổi vì luôn cho cùng một output sai.
- **Theo từng cặp:** tần suất đổi trạng thái của mỗi cặp thật qua 20 lần sinh; chỉ là mô tả.

## 5. Giả thuyết (khóa): tám giả thuyết, Holm 0.05

Mọi giả thuyết có điều kiện trên bảng, cách chọn hàng và tiền xử lý đã cố định. Contrast tính theo từng lần sinh r rồi ghép cặp.

| ID | Bảng | Thuật toán | Điều kiện | Contrast theo lần sinh r | Dự đoán |
|---|---|---|---|---|---|
| P5-1S-A | Sachs | AVICI | k = 20, Gauss | flips_AVICI,r − max(flips_PC,r, flips_GES,r) | > 0 |
| P5-1S-C | Sachs | CDFM | k = 20, Gauss | flips_CDFM,r − max(flips_PC,r, flips_GES,r) | > 0 |
| P5-1W-A | Wine | AVICI | k = 20, Gauss | như trên | > 0 |
| P5-1W-C | Wine | CDFM | k = 20, Gauss | như trên | > 0 |
| P5-2S-20 | Sachs | CDFM | k = 20 | τ_r(có cấu trúc) − τ_r(Gauss) | > 0 |
| P5-2S-40 | Sachs | CDFM | k = 40 | như trên | > 0 |
| P5-2W-20 | Wine | CDFM | k = 20 | như trên | > 0 |
| P5-2W-40 | Wine | CDFM | k = 40 | như trên | > 0 |

- **P5-1** hỏi output của model trên khối thật có đổi nhiều hơn đối chứng cổ điển không, ở điều kiện chuẩn của P-N1 (20 cột Gauss).
  - **Estimand:** E_r[flips_M,r − max(flips_PC,r, flips_GES,r)], có điều kiện trên bảng đã cố định.
  - Max lấy theo từng lần sinh. Vì vậy model được so với đối chứng đổi nhiều hơn ở chính lần sinh đó.
  - Vì E[max] ≥ max của hai trung bình, contrast này chặt hơn việc so với trung bình riêng của từng đối chứng.
  - Báo cáo phải nêu đúng ý nghĩa này, kèm trung bình riêng của flips_M, flips_PC, flips_GES và của max.
- **P5-2** hỏi kết quả N4-b (ngưỡng tăng khi đệm có cấu trúc) có lặp lại khi khối đích là bảng thật không. Cả hai kiểu đệm đều là tổng hợp, và ghép cặp trong cùng lần sinh.
- **Phép kiểm:** t ghép cặp một phía qua 20 lần sinh (df = 19): t = trung bình / (độ lệch chuẩn / √20), p = `t.sf(t, 19)`.
  - SE = 0 thì ghi DEGENERATE, dùng p = 1 và không xác nhận, như P-N4.
  - Holm ở mức familywise 0.05 trên đúng tám p-value.
- **Giới hạn của phép kiểm (thêm ở v1):**
  - t là xấp xỉ, nhất là khi flips là số đếm rời rạc hoặc có nhiều giá trị bằng nhau qua 20 lần sinh.
  - Holm chỉ kiểm soát sai số familywise khi từng p-value đã được hiệu chỉnh tốt. Holm không khắc phục p-value xấp xỉ kém.
  - Để người đọc thấy mức rời rạc, phần mô tả báo số lần sinh có contrast dương, bằng 0 và âm, cùng số giá trị khác nhau.
  - CONFIRMED chỉ xác nhận **dấu** của trung bình có điều kiện. CI 95% và nhãn cỡ hiệu ứng của từng giả thuyết là mô tả; Holm không bảo vệ chúng đồng thời.
- **Nhãn:** CONFIRMED / NOT_CONFIRMED. Nhãn cỡ (mô tả): biên 1 cặp cho flips, 0.03 cho ngưỡng.
- **Diễn giải:** CONFIRMED nghĩa là, với bảng và cách xử lý đã cố định, hiệu ứng trung bình qua các lần sinh đệm có dấu dự đoán. Nó không nói gì về các bảng thật khác.

## 6. Báo cáo mô tả (không thuộc bộ Holm)

- **Thống kê theo nhóm:** cho mỗi bảng, thuật toán và điều kiện, báo các đại lượng sau qua 20 lần sinh của Δp, flips, Δm, |Δm| và Δτ:
  - trung bình, trung vị, khoảng tứ phân vị, nhỏ nhất và lớn nhất;
  - CI 95% theo t qua các lần sinh (có điều kiện);
  - số lần hoàn tất và số timeout.
- **Bốn thành phần của P5-1:** trung bình của flips_M, flips_PC, flips_GES và max. Kèm số lần sinh có contrast dương, bằng 0 và âm.
- **Contrast kiểu P5-1 ở các điều kiện khác:**
  - là mô tả;
  - chỉ dùng các lần sinh có đủ output;
  - ở k = 40 với đệm có cấu trúc, chỉ so với PC.
- **Theo cách đọc của CDFM:** flips theo FIXED và FROZEN.
- **Theo từng cặp:** tần suất đổi trạng thái; liệt kê cặp có tần suất ≥ 0.5, kèm tên biến.
- **Chênh lệch ghép cặp:** đệm có cấu trúc trừ đệm Gauss; k = 40 trừ k = 20. GES thiếu điều kiện k = 40 có cấu trúc, nên các chênh lệch cần điều kiện đó bỏ trống cho GES.
- **Bối cảnh:** m0 của từng thuật toán trên từng bảng; số hàng dư của Wine trong 500 hàng chọn (10; 490 vector khác nhau).
- Không có câu nào về độ chính xác.

## 7. Kiểm hoàn tất trước khi đọc (khóa; sửa ở v1)

Chỉ đọc kết quả khi tất cả các điều sau đều đạt:

- mọi job trong danh sách ở §3 (616 job) có đúng một trạng thái kết thúc trong log;
- 0 job `error`, và không có `budget_stop`;
- `timeout` chỉ ở input mô tả của PC và GES (§3); số timeout được ghi lại;
- mọi job `ok` có file output, và mã băm input của output khớp input sinh lại;
- ở mọi input, khối thật trùng từng bit với X_R, và khối đệm trùng từng bit với output của bộ sinh;
- mã băm của X_R khớp số G1 đã ghi;
- SHA-256 của hai file dữ liệu khớp manifest, kiểm ở đầu và cuối lượt;
- cổng đóng băng `ok: true` ở đầu và cuối lượt, cùng commit;
- với mỗi thuật toán và mỗi bảng, hai lần chạy ở k0 trùng từng bit.

## 8. Cổng khả thi (trước khi đóng băng; không chạy model nào trên bảng thật)

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | **Nạp dữ liệu,** không chạy model: SHA-256 hai file khớp manifest; đúng kích thước và tên cột; `idx` tái lập và khớp mã băm ở §1; số hàng dư trong 500 hàng chọn (Sachs 0; Wine 10, tức 490 vector khác nhau); X_R hữu hạn, mỗi cột có trung bình ≈ 0 và độ lệch chuẩn ≈ 1. Ghi mã băm của X_R | 100% |
| G2 | **Đệm,** trên cả 40 seed của P-N5: ở k = 20, đường sinh tổng quát trùng từng bit với `padding2`; ở k = 40, tham số như nhau giữa hai lần gọi, đồ thị đúng là U < p_e, e = 0 cho đồ thị rỗng, sai lệch tương đối so với code RFF của AVICI ≤ 1e-9 | trùng từng bit; ≤ 1e-9 |
| G3 | **Cả 81 input mỗi bảng,** chỉ sinh input: khối thật trùng từng bit với X_R; khối đệm trùng từng bit với output bộ sinh; float32, hữu hạn, đúng kích thước. Ghi mã băm từng input | 100% |
| G4 | **Code đọc** chạy hết trên DEV5 (xem dưới); chỉ kiểm cấu trúc | chạy hết, không in hay ghi giá trị |
| G5 | **Code kiểm định:** t ghép cặp so với `scipy.stats.ttest_1samp` một phía; SE = 0 cho DEGENERATE và p = 1; Holm dừng đúng; contrast max đúng trên ví dụ định trước; timeout bị loại khỏi thống kê và không bị gán giá trị | khớp; đúng kết quả định trước |
| G6 | **Tất định** của bốn thuật toán trên DEV5: chạy lại k0 và một input D = 51, so từng bit | trùng từng bit |
| G7 | **Thời gian và bộ nhớ** trên DEV5, cộng số đo ở §10; ước tính tổng cho 616 job | ≤ 3 giờ; nếu vượt thì báo user |

- **DEV5:**
  - Bảng thay thế là bảng của §10 (`simulate_data` với d = 11, n = 500, seed 999000, config `er2-rff-gauss.yaml`), đi qua cùng tiền xử lý với bảng thật.
  - Đệm dùng base 470000, 2 lần sinh.
  - Output chỉ dùng cho cổng, không bao giờ báo như kết quả.

## 9. Đọc kết quả

- **Câu được viết** (ví dụ): "Trên 500 hàng đã chọn của bảng X, với tiền xử lý đã khóa, thêm 20 cột Gauss độc lập làm skeleton của model Y trên khối thật đổi trạng thái trung bình Z trong 55 cặp. Mức đổi này lớn hơn mức đổi của đối chứng cổ điển đổi nhiều hơn ở từng lần sinh (max của PC và GES), trung bình W cặp."
  - Mọi câu đều có điều kiện trên bảng đã cố định.
  - Câu về P5-1 phải nói rõ max lấy theo từng lần sinh.
- **Không được viết:**
  - "model sai" hay "model đúng" trên dữ liệu thật; "giảm độ chính xác";
  - "ổn định hơn nên đúng hơn";
  - "trên dữ liệu thật nói chung";
  - "20 bộ dữ liệu";
  - rằng CI hay nhãn cỡ của từng giả thuyết được Holm bảo vệ;
  - bất kỳ so sánh nào với một đồ thị tham chiếu.

## 10. Ngân sách

**Đo trên bảng thay thế tổng hợp,** không đọc dữ liệu thật: một hệ ER–RFF với d = 11 (config `er2-rff-gauss.yaml` của P-N1, seed 999000), n = 500, cùng bộ sinh đệm và cùng các mức k, e. Mỗi thuật toán chạy một lần trên mỗi input, trong tiến trình riêng. Script và số đo: [`design/budget5.py`](design/budget5.py), [`design/budget5.jsonl`](design/budget5.jsonl).

| Thuật toán | D = 11 (k0) | D = 31, Gauss | D = 31, có cấu trúc | D = 51, Gauss | D = 51, có cấu trúc | Bộ nhớ đỉnh |
|---|---|---|---|---|---|---|
| AVICI | 9.5 s (gồm biên dịch) | 12.0 s (gồm biên dịch) | 5.2 s | 15.9 s (gồm biên dịch) | 8.5 s | 1.38 GB |
| CDFM | 4.4 s | 10.6 s | 10.8 s | 15.8 s | 15.3 s | 0.62 GB |
| PC | 0.1 s | 0.2 s | 0.4 s | 0.6 s | 4.0 s | 0.25 GB |
| GES | 0.2 s | 1.0 s | 3.8 s | 2.9 s | **359 s** | 0.19 GB |

**Ước tính** cho 162 input (hai bảng):

- AVICI khoảng 19 phút; CDFM khoảng 35 phút; PC khoảng 4 phút.
- GES chạy đủ mọi input: khoảng 4.1 giờ, gần như toàn bộ do 40 lần chạy ở k = 40 với đệm có cấu trúc. Với phạm vi đã khóa ở §3: khoảng 5 phút.
- **Tổng với phạm vi đã khóa:** khoảng 1.1 giờ, cộng thời gian sinh input và khởi động tiến trình; dưới 3 giờ. Chạy đủ GES thì khoảng 5.2 giờ, vượt 3 giờ.
- Đây là số đo trên bảng thay thế, nên chưa bảo đảm thời gian trên Sachs và Wine. Khối thật có thể dày phụ thuộc hơn, nên PC và GES có thể chậm hơn.
  - G7 đo lại trên DEV5 trước khi chạy; nếu ước tính vượt 3 giờ thì báo user.
  - Trong lượt chạy thật, mốc 3 giờ được theo dõi theo §3.
- AVICI dùng tới 1.38 GB ở D = 51. Vì vậy không chạy gì nặng song song.

## 11. Quy trình

1. User duyệt v0 với năm chỉnh sửa (22/11). Khóa v1: commit và push trên nhánh công khai.
2. Viết code dưới dạng file mới trong `artifacts/n5_runs/pn5/`. Import nguyên trạng `common.py` và `common2.py`.
3. Chạy DEV5 (bốn thuật toán trên bảng thay thế), rồi chạy G1–G7. Đóng băng code cùng các phụ thuộc và mã băm của hai file dữ liệu. Commit, push.
4. Chạy P-N5 nếu các cổng đạt và ước tính không vượt 3 giờ; user đã duyệt bước này, không cần thêm vòng duyệt. Kiểm hoàn tất (§7), rồi đọc bằng code đã đóng băng.

## 12. Nhật ký (append-only sau khi khóa)

- **v0, 22/11/2026 (`cfe5144`):** bản nháp, theo quyết định của user ngày 22/11.
- **v1, 22/11/2026 (khóa):** user duyệt bốn quyết định (normal-score cho cả hai bảng; giữ tám giả thuyết; bỏ GES ở k = 40 có cấu trúc; giữ hàng trùng của Wine). User cho GO sau năm chỉnh sửa, không cần thêm vòng duyệt. Các thay đổi so với v0:
  1. **§2, chuẩn hóa:** sửa X = zscore([X_R | P]) thành X = [X_R | P]. Hai khối được chuẩn hóa riêng; X_R được lưu và dùng nguyên trạng. G3 kiểm cả 81 input mỗi bảng.
     - User tính trên 500 hàng đã chọn: chuẩn hóa lần hai đổi 97 giá trị của khối thật ở Sachs (tối đa 3.73e−9) và 283 giá trị ở Wine (tối đa 7.45e−9).
     - Agent tính lại bằng một script tạm, không chạy model, và ra cùng bốn con số.
  2. **§1, lý do chọn normal-score:**
     - Giữ hai lý do: giảm ảnh hưởng của giá trị cực đoan, và một quy tắc xác định trước.
     - Bỏ lập luận rằng normal-score làm dữ liệu gần phân phối biên của dữ liệu huấn luyện: z-score không Gauss hóa dữ liệu.
     - Bỏ lập luận rằng Fisher-z và BIC Gauss "có cơ sở hơn" trên thang này. Thêm điều normal-score không bảo đảm, có trích Harris & Drton (2013). Agent đối chiếu Định nghĩa 2, §4 (công thức 9) và Định lý 8 trên bản PDF của bài.
     - Khóa rõ: normal-score chỉ áp dụng cho khối thật.
     - §2: câu "sau z-score là Gauss i.i.d." sửa thành "sinh từ nhiễu Gaussian độc lập rồi chuẩn hóa từng cột".
  3. **§5, ý nghĩa của P5-1 và giới hạn của phép kiểm:**
     - estimand có max theo từng lần sinh;
     - t là xấp xỉ, và Holm không khắc phục p-value xấp xỉ kém;
     - SE = 0 vẫn là DEGENERATE;
     - CONFIRMED chỉ về dấu, CI và nhãn cỡ không được Holm bảo vệ đồng thời;
     - flips đo trên 55 cặp, độ ổn định không chứng minh độ chính xác, m0 luôn được báo (§4).
     - Phần mô tả thêm số lần sinh có contrast dương, bằng 0, âm, để thấy mức rời rạc (§6).
  4. **§3 và §7, timeout và ngân sách:**
     - mọi job có một trạng thái kết thúc;
     - timeout chỉ được phép ở input mô tả của PC và GES, được đếm, và không bao giờ được gán thành "không đổi";
     - thống kê chỉ dùng các lần hoàn tất.
     - Quy tắc dừng khi thiếu output thuộc giả thuyết chính được giữ. Agent áp dụng nó cho cả PC, vì PC cũng nằm trong max của P5-1.
     - Mốc 3 giờ được theo dõi cả trong lượt chạy thật, với `budget_stop`.
  5. **§1 và §6, hàng trùng của Wine:** 937 hàng dư trong file; 10 hàng dư trong 500 hàng chọn, tức 490 vector khác nhau. Agent tính lại và ra cùng số. Hai con số này được báo cùng kết quả.
  - **Làm rõ, không đổi thiết kế:**
    - k0 chạy hai lần cho mỗi thuật toán (lần chính và một lần chạy lại);
    - tổng 616 job; thứ tự chạy với input chính trước;
    - số luồng như P-N1 và P-N2 (model 2 luồng, PC và GES 1 luồng);
    - định nghĩa skeleton của từng thuật toán (§4);
    - mã băm `idx`;
    - định nghĩa DEV5.
  - **Trình tự đã duyệt:** khóa và push luật, rồi G1–G7, đóng băng, và chạy P-N5 trong phạm vi đã nêu.
