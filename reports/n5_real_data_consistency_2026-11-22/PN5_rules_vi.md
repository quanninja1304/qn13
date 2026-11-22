# P-N5: kiểm tính nhất quán trên dữ liệu thật, gap 2 (luật v0, nháp, 22/11/2026)

> **Trạng thái:** **v0, NHÁP, CHƯA KHÓA.** Khóa bằng một commit kèm push trên nhánh công khai sau khi user duyệt, trước khi chạy bất kỳ model nào trên hai bảng thật. Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §12 kèm lý do, và không được dựa trên output đã thấy.
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
> **Đề xuất của agent, cần user quyết:** cách tiền xử lý (§1), tám giả thuyết khóa (§5) và phạm vi chạy GES (§3).

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
  - Mã băm của `idx` được ghi lại.
  - Wine có 937 hàng trùng trong file gốc. Hàng trùng được giữ như bản phát hành, không lọc. Số hàng trùng trong 500 hàng đã chọn được báo.
- **Tiền xử lý** (đề xuất): biến đổi normal-score theo hạng cho từng cột, tính trên 500 hàng đã chọn. Mỗi giá trị nhận hạng trung bình r khi có giá trị bằng nhau, rồi được đổi thành Φ⁻¹(r / (n + 1)). Sau đó z-score bằng hàm `zscore` của P-N1 (float64 → float32).
  - **Lý do:**
    - cùng một quy tắc cho cả hai bảng, không cần nhìn hình dạng phân phối để chọn;
    - không đổi khi biến đổi đơn điệu từng biến, và bỏ ảnh hưởng của đuôi nặng (Sachs có giá trị tới 4 491);
    - gần với phân phối biên của dữ liệu tổng hợp đã z-score mà hai model thấy khi huấn luyện;
    - trên thang này, Fisher-z của PC và BIC Gauss của GES có cơ sở hơn (cách tiếp cận nonparanormal).
  - **Phương án thay thế, không chạy:** log rồi z-score cho Sachs, chỉ z-score cho Wine.
- **Khối thật** X_R (500 × 11, float32) đóng vai khối đích. Input k0 là X_R.

## 2. Khối đệm (khóa)

- **Bộ sinh:** các hàm đã đóng băng `pad_params`, `pad_graph`, `pad_data` của `common2.py` (P-N2), họ RFF, s = 1, với k ∈ {20, 40}, như P-N4.
- **Hai kiểu đệm,** dùng chung randomness trong cùng một lần sinh:
  - **Gauss:** mức e = 0. Mỗi cột là nhiễu độc lập; sau z-score là Gauss i.i.d., như kiểu A của P-N1.
  - **Có cấu trúc:** mức e = 2. Đồ thị ER với 2 cạnh kỳ vọng mỗi nút, cơ chế RFF đa biến của AVICI.
- **Seed** của lần sinh r cho bảng j: 460000 + 1000·j + r, với r = 0, …, 19.
  - Khóa luồng `SeedSequence([seed, 20261120, 2])` như P-N2. k = 20 và k = 40 rút từ cùng một luồng, như P-N4.
  - Base 460000 chưa dùng ở tập nào trước: P-N1 dùng 100000–300000, P-N2 dùng 410000–430000, P-N4 dùng 440000 và 450000.
- **Ghép:** X = zscore([X_R | P]). Khối thật phải trùng từng bit với X_R ở mọi input.

## 3. Input và thuật toán

- **Input mỗi bảng:** k0, cộng 2 giá trị k × 2 kiểu đệm × 20 lần sinh, tức 81 input. Hai bảng: 162 input.
- **Thuật toán,** gọi như P-N1 và P-N2:
  - AVICI `scm-v0`: lưu xác suất; NATIVE là ngưỡng 0.5;
  - CDFM: lưu xác suất, logits, ma trận kề NATIVE và ngưỡng NATIVE;
  - PC: causal-learn, Fisher-z, α = 0.05, stable;
  - GES: BIC Gauss.
- Mỗi input chạy đúng một lần cho mỗi thuật toán. Các thuật toán chạy tuần tự, không song song (RAM).
- **Tất định:** chạy lại k0 hai lần cho mỗi thuật toán; output phải trùng từng bit.
- **Phạm vi chạy GES** (đề xuất, theo §10): GES chạy mọi input, **trừ k = 40 với đệm có cấu trúc**. Ở điều kiện đó, đối chứng cổ điển chỉ có PC, và chỉ ở phần mô tả. Tám giả thuyết ở §5 chỉ cần GES ở k = 20 với đệm Gauss.
  - GES có giới hạn 900 giây mỗi lần chạy. Lần chạy quá giới hạn được ghi là `timeout` và bị loại khỏi phần mô tả của GES.
  - Nếu một lần chạy GES thuộc input của P5-1 (k = 20, Gauss) quá giới hạn, lượt chạy dừng và báo user; không tự đổi quy tắc.

## 4. Biến đo

Mọi biến đo tính trên khối thật, so với k0 của cùng thuật toán:

- **Δp** (AVICI, CDFM): trung bình |p_ij − p_ij(k0)| trên các cặp có thứ tự của khối thật.
- **flips:** số cặp không thứ tự của khối thật đổi trạng thái skeleton so với k0, theo NATIVE. Với CDFM báo thêm theo FIXED (0.5) và FROZEN (ngưỡng ở k0); hai cách đọc này chỉ là mô tả.
- **Δm = m − m0** và **|Δm|**, với m0 là số cạnh skeleton ở k0.
- **Δτ** (CDFM): ngưỡng NATIVE trừ ngưỡng ở k0.
- **Bối cảnh:** m0 của từng thuật toán.
- **Theo từng cặp:** tần suất đổi trạng thái của mỗi cặp thật qua 20 lần sinh; chỉ là mô tả.

## 5. Giả thuyết (đề xuất khóa): tám giả thuyết, Holm 0.05

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

- **P5-1** hỏi output của model trên khối thật có đổi nhiều hơn đối chứng cổ điển không, ở điều kiện chuẩn của P-N1 (20 cột Gauss). Dùng max của PC và GES là chọn đối chứng chặt hơn.
- **P5-2** hỏi kết quả N4-b (ngưỡng tăng khi đệm có cấu trúc) có lặp lại khi khối đích là bảng thật không. Cả hai kiểu đệm đều là tổng hợp.
- **Phép kiểm:** t ghép cặp một phía qua 20 lần sinh (df = 19): t = trung bình / (độ lệch chuẩn / √20), p = `t.sf(t, 19)`.
  - SE = 0 thì ghi DEGENERATE, dùng p = 1 và không xác nhận, như P-N4.
  - Holm ở mức familywise 0.05 trên đúng tám p-value.
- **Nhãn:** CONFIRMED / NOT_CONFIRMED. Nhãn cỡ (mô tả): biên 1 cặp cho flips, 0.03 cho ngưỡng.
- **Diễn giải:** CONFIRMED nghĩa là, với bảng và cách xử lý đã cố định, hiệu ứng trung bình qua các lần sinh đệm có dấu dự đoán. Nó không nói gì về các bảng thật khác.

## 6. Báo cáo mô tả (không thuộc bộ Holm)

- Cho mỗi bảng, thuật toán và điều kiện: trung bình, trung vị, khoảng tứ phân vị, nhỏ nhất và lớn nhất qua 20 lần sinh của Δp, flips, Δm, |Δm| và Δτ. Kèm CI 95% theo t qua các lần sinh (có điều kiện).
- flips của CDFM theo FIXED và FROZEN.
- Tần suất đổi trạng thái theo từng cặp; liệt kê cặp có tần suất ≥ 0.5.
- Chênh lệch ghép cặp: đệm có cấu trúc trừ đệm Gauss; k = 40 trừ k = 20.
- m0 của từng thuật toán trên từng bảng.
- Không có câu nào về độ chính xác.

## 7. Kiểm hoàn tất trước khi đọc (khóa)

Chỉ đọc kết quả khi tất cả các điều sau đều đạt:

- đủ output theo §3 cho bốn thuật toán, kể cả hai lần chạy lại ở k0;
- 0 job lỗi;
- mã băm input của mọi output khớp input sinh lại;
- khối thật trùng từng bit ở mọi input;
- SHA-256 của hai file dữ liệu khớp manifest, kiểm ở đầu và cuối lượt;
- cổng đóng băng `ok: true` ở đầu và cuối lượt, cùng commit;
- hai lần chạy lại ở k0 trùng từng bit.

## 8. Cổng khả thi (trước khi đóng băng; không chạy model nào trên bảng thật)

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | Nạp dữ liệu: SHA-256 hai file khớp manifest; đúng kích thước; `idx` tái lập; ghi mã băm của bảng đã biến đổi. Không chạy model | 100% |
| G2 | Đệm: ở k = 20 trùng đường `padding2`; ở k = 40 đạt các kiểm như cổng G2 của P-N4, trên một số lần sinh của P-N5 | trùng từng bit; sai lệch tương đối ≤ 1e-9 |
| G3 | Khối thật trùng từng bit ở cả 81 input mỗi bảng (chỉ sinh input) | 100% |
| G4 | Code đọc chạy hết trên một bảng thay thế tổng hợp cùng kích thước; chỉ kiểm cấu trúc | chạy hết, không in giá trị |
| G5 | Code kiểm định: t ghép cặp so với tính độc lập; SE = 0 cho DEGENERATE; Holm dừng đúng | khớp; đúng kết quả định trước |
| G6 | Tất định của bốn thuật toán trên bảng thay thế: chạy lại, so từng bit | trùng từng bit |
| G7 | Thời gian và bộ nhớ (§10); ước tính tổng | báo user nếu vượt 3 giờ |

## 9. Đọc kết quả

- **Câu được viết** (ví dụ): "Trên 500 hàng đã chọn của bảng X, với tiền xử lý đã khóa, thêm 20 cột Gauss độc lập làm output của model Y trên khối thật đổi trạng thái trung bình Z cặp, nhiều hơn PC và GES." Mọi câu đều có điều kiện trên bảng đã cố định.
- **Không được viết:**
  - "model sai" hay "model đúng" trên dữ liệu thật; "giảm độ chính xác";
  - "trên dữ liệu thật nói chung";
  - "20 bộ dữ liệu";
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
- GES chạy đủ mọi input: khoảng 4.1 giờ, gần như toàn bộ do 40 lần chạy ở k = 40 với đệm có cấu trúc. Với phạm vi đề xuất ở §3: khoảng 5 phút.
- **Tổng với phạm vi đề xuất:** khoảng 1.1 giờ, cộng thời gian sinh input và khởi động tiến trình; dưới 3 giờ. Chạy đủ GES thì khoảng 5.2 giờ, vượt 3 giờ.
- Đây là số đo trên bảng thay thế. Trên bảng thật, khối thật có thể dày phụ thuộc hơn, nên PC và GES có thể chậm hơn. G7 đo lại trước khi chạy, và nếu ước tính vượt 3 giờ thì báo user.
- AVICI dùng tới 1.38 GB ở D = 51. Vì vậy không chạy gì nặng song song.

## 11. Quy trình

1. User duyệt v0 (gồm ba đề xuất ở đầu file). Khóa: commit và push trên nhánh công khai.
2. Viết code dưới dạng file mới trong `artifacts/n5_runs/pn5/`. Import nguyên trạng `common.py` và `common2.py`.
3. Chạy G1–G7. Đóng băng code cùng các phụ thuộc và mã băm của hai file dữ liệu. Commit, push.
4. Chạy P-N5. Kiểm hoàn tất (§7), rồi đọc bằng code đã đóng băng.

## 12. Nhật ký (append-only sau khi khóa)

- **v0, 22/11/2026:** bản nháp, theo quyết định của user ngày 22/11.
