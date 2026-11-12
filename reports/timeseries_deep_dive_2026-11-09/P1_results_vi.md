# Kết quả pilot P1 (TS-G1): confounding ẩn trên CausalRivers, đọc theo luật đã khóa (12/11/2026)

> **Nguồn số liệu:**
> - `P1_results.jsonl`: 2400 dòng, không trùng.
> - `P1_analysis_outputs.json` và `P1_analysis_log.txt`, sinh bởi `P1_analysis.py`.
>
> **Luật đọc:** [`TS_G1_reading_rules_vi.md`](TS_G1_reading_rules_vi.md), khóa ngày 10/11. Mọi thay đổi khi chạy được ghi ở §8 **trước** khi xem metric.
>
> **Nhãn:**
> - [Verified-run]: số liệu từ chính lần chạy này.
> - [Inference], [Hypothesis]: suy luận và giả thuyết, chưa kiểm.

## 1. Trạng thái chạy

- **Tổng số job:** 2400 = 200 đơn vị × {L, O} × {VAR, PCMCI+, LPCMCI} × {6H, 24H}.
- **Thành công:** 2396.
- **Timeout:** 4, tất cả ở 6H. LPCMCI ở L bị 2, PCMCI+ ở O bị 1, LPCMCI ở O bị 1.
- **Lỗi:** 0, sau bản sửa cho proxy mưa trùng nhau (§8, ngày 11/11).

## 2. Đọc theo luật (6H, bản chính)

| Luật | Đại lượng | Giá trị [Verified-run] | Kết quả |
|---|---|---|---|
| R0 | Số đơn vị nhỏ nhất mỗi tầng | gần 98, xa 100 (≥ 60) | **Đạt** |
| R1 | VAR, điều kiện L: q1(gần) − q1(xa) | **0.308**, CI [0.247, 0.368] | **Đạt**, H1 được xác nhận |
| R2 | PCMCI+, tầng gần: q2(L) − q2(O) | **−0.013**, CI [−0.048, 0.023], 99 cặp | **Không đạt**: "không xác nhận được mưa là nguồn chính" |
| R3, kiểm tra hợp lý | q2 tầng xa < q2 tầng gần, mọi phương pháp | VAR 0.62 < 0.92; PCMCI+ 0.14 < 0.48; LPCMCI 0.27 < 0.67 | **Đạt** |
| R3 | Δfalse = q2(PCMCI+) − q2(LPCMCI), tầng gần, L | **−0.196**, CI [−0.263, −0.135], 98 cặp | < 0.05, nên **GAP-A** |
| R3 (báo cáo thêm) | Δrecall = q3(PCMCI+) − q3(LPCMCI) | 0.112, CI [0.056, 0.168] | — |
| R3 (báo cáo thêm) | Runtime trung vị: LPCMCI / PCMCI+ | 23.8 s / 9.2 s | — |

**Phán quyết theo luật:**
- **GAP-A**: phương pháp có biến ẩn (LPCMCI) **không sửa được** các claim sai.
- Vì R2 không đạt, phán quyết này phải đọc với **mức tin cậy đã hạ**.

**Áp vào các cổng của bài toán** ([problem statement §5](TS_G1_problem_statement_vi.md)):
- G0 đạt; G1 đạt.
- G2 đạt: H3 sai, nghĩa là LPCMCI không đưa FCR về mức thấp.
- G3: chưa xét xong. Phần audit prior art cho khoảng trống (2) nằm ở [`G2_prior_art_audit_vi.md`](G2_prior_art_audit_vi.md).

## 3. Bảng mô tả (6H; q2 là tỉ lệ cặp chéo có claim nhân quả, q3 là recall cạnh thật)

| Phương pháp | L gần | L xa | O gần | O xa | q3 (L gần / L xa) | q4 `<->` (L gần) |
|---|---|---|---|---|---|---|
| VAR | 0.92 | 0.62 | 0.91 | 0.60 | 0.92 / 0.93 | — |
| PCMCI+ | 0.48 | 0.14 | 0.48 | 0.11 | 0.94 / 0.87 | — |
| LPCMCI | **0.67** | 0.27 | **0.88** | **0.55** | 0.83 / 0.76 | 0.15 |

**Ở độ phân giải 24H** (R4, chỉ để mô tả, τ_max = 1):
- Tầng gần, điều kiện L, q2: VAR 0.69, PCMCI+ 0.46, LPCMCI 0.44.
- Như vậy Δfalse = 0.02, vẫn dưới 0.05.
- Lộ mưa cũng gần như không làm q2 của PCMCI+ thay đổi (0.46 ở L, 0.44 ở O).
- LPCMCI mất recall nặng hơn: q3 = 0.48 ở tầng gần.

**Cạnh sai của LPCMCI phân theo lag** (tầng gần, 6H, 392 cặp; mô tả, không dùng để quyết định):
- Claim `-->` có mặt ở **mọi** lag, kể cả lag lớn nhất:
  - Điều kiện L: τ = 0 có 176, τ = 1 có 206, τ = 4 có 90.
  - Điều kiện O: τ = 1 có 313, τ = 4 có 230.
- `<->` gần như chỉ xuất hiện ở τ = 0.

## 4. Diễn giải

**Đã xác lập** [Verified-run, trong giới hạn của thiết kế]:
1. **Có dependence giả giảm theo khoảng cách.** Giữa các chuỗi sông *không có đường nối*, mọi phương pháp đều đưa ra claim nhân quả nhiều hơn rõ rệt khi hai trạm ở gần nhau. Mức chênh của PCMCI+ là 0.48 so với 0.14.
   - Vì hai chuỗi không nối nhau theo dòng chảy, dependence này phải đến từ một nguyên nhân chung ngoài mạng sông, hoặc từ lỗi topology hay lỗi đo (xem mục 5).
   - Tầng xa vẫn còn tỉ lệ claim sai khác 0 (PCMCI+ 0.14). Điều này phù hợp với một thành phần **toàn cục** (mùa vụ, thời tiết quy mô lớn) cộng với một thành phần **cục bộ**.
2. **LPCMCI không sửa được mà còn tệ hơn.** LPCMCI khẳng định quan hệ tổ tiên (`-->`) giữa các cặp không nối nhau nhiều hơn PCMCI+, và có recall thấp hơn. Đây là lỗi về **tính đúng (soundness)** của output PAG trên dữ liệu thật, không chỉ là lỗi về hiệu năng.
3. **Proxy mưa từ trạm điểm không giải thích được phần dư.** Đưa proxy vào gần như không thay đổi q2 của PCMCI+ (−0.013).

**Phát hiện mô tả cần chú ý** [Verified-run; nguyên nhân là Hypothesis]:
- Khi lộ mưa và khai báo mưa là ngoại sinh, LPCMCI đưa ra **nhiều** claim tổ tiên sai hơn: ở tầng gần 0.67 tăng lên 0.88, ở tầng xa 0.27 tăng lên 0.55. Đồng thời gần như mất hẳn `<->`.
- Giả thuyết: một proxy không hoàn hảo, cộng với tri thức nền về tính ngoại sinh, cung cấp thêm "điểm neo" định hướng. Lỗi định hướng khi đó lan ra thành claim có đuôi.
- Nếu giả thuyết đúng, đây là một **insight có thể dùng cho cơ chế**: đưa proxy vào một cách ngây thơ có thể làm hỏng tính đúng của PAG.
- Hiện đây chỉ là mô tả. Chưa có kiểm định nào cho giả thuyết này.

**Chưa xác lập được** [Inference]:
- **Nguồn của confounding.** Mưa là nguồn chính hay không, R2 không xác nhận được.
- **GAP-A có phải gap phương pháp thật không**, hay do cấu hình. Đây là điểm reviewer sẽ hỏi đầu tiên. Có bốn giải thích thay thế cạnh tranh, liệt kê ở mục 5.

## 5. Các giải thích thay thế phải loại trừ trước khi khẳng định gap phương pháp

| # | Giải thích thay thế | Vì sao hợp lý | Cách kiểm |
|---|---|---|---|
| A1 | **Bộ nhớ dài vượt τ_max.** Nước ngầm, độ ẩm đất và dòng chảy nền có bộ nhớ nhiều ngày, trong khi τ_max = 24 giờ | Claim `-->` dồn cả ở lag lớn nhất (τ = 4); proxy mưa 6 giờ chỉ bắt được tác động ngắn hạn | Chạy lại với τ_max dài hơn (3–5 ngày); dùng proxy mưa **tích lũy** (tổng nhiều ngày) |
| A2 | **Sai mô hình test CI.** Quan hệ mưa–dòng chảy phi tuyến và có ngưỡng, còn ParCorr là test tuyến tính | Điều kiện hóa tuyến tính không cắt được dependence phi tuyến, nên lỗi CI lan sang bước định hướng | Lấy một tập con, dùng test phi tuyến hoặc robust (RobustParCorr, hoặc CMIknn trên chuỗi đã gộp 24H) |
| A3 | **Artefact đo hoặc tiền xử lý dùng chung.** Trạm gần thường cùng cơ quan quản lý, có thể có khoảng trống trùng thời điểm, và việc nội suy tuyến tính tạo ra đoạn giống nhau ở cả hai chuỗi | Thiên lệch theo khoảng cách sẽ xuất hiện ngay cả khi không có confounder vật lý | Đo tỉ lệ điểm nội suy trùng thời điểm theo cặp; chạy lại sau khi bỏ các đoạn nội suy |
| A4 | **Lỗi topology.** Kênh đào, trạm bơm, tách nhánh không được ghi nhận | Cặp gần dễ có liên kết nhân tạo | Dùng cột `origin` và cột chất lượng cạnh của CausalRivers; báo cáo kết quả khi bỏ các chain có cạnh chất lượng thấp |

**Ngoài ra:**
- **FNETS** (khử nhân tố toàn cục) chưa được kiểm. Theo dự đoán [Hypothesis], nó sẽ cắt được phần chung ở tầng xa nhưng **không** cắt được phần dư ở tầng gần. Nếu dự đoán sai, khoảng trống (2) đóng lại.
- **Giới hạn thống kê:** các đơn vị dùng chung chain (mỗi chain tối đa 3 lần), nên CI bootstrap theo đơn vị có thể hẹp hơn thực tế. Với T ≈ 7300, α = 0.01 không hiệu chỉnh đa kiểm định, nên dependence nhỏ cũng bị phát hiện. Điều này giải thích q1 của VAR rất cao (0.92).

## 6. Ý nghĩa với khoảng trống (2) và bước tiếp theo đề xuất

**Ý nghĩa** [Inference]:
- P1 **ủng hộ tiền đề** của khoảng trống (2): có confounding *cục bộ* đo được trên dữ liệu thật (R1), và phương pháp có biến ẩn hiện có đưa ra claim sai về tổ tiên (GAP-A).
- P1 **làm yếu** hướng M1 dùng proxy điểm: proxy mưa hiện tại không giúp gì.
- Hướng M2, khai thác cấu trúc không gian, chưa bị bác. Nhưng cần biết confounder là gì, hoặc ít nhất là nó có tính cục bộ và có bộ nhớ dài.

**Đề xuất P2: pilot kiểm độ bền, có luật đọc mới, viết và khóa trước khi chạy.** P2 có mục đích **phân biệt GAP-A thật với A1–A4**:
1. **A1:** τ_max = 12 và 20 ở 6H; proxy mưa tích lũy 1, 3 và 7 ngày. Kiểm lại H2.
2. **A2:** chạy RobustParCorr trên toàn bộ dữ liệu, và CMIknn trên một tập con 24H.
3. **A3:** thống kê nội suy trùng thời điểm; chạy lại trên các đoạn không nội suy.
4. **A4:** lọc chain theo chất lượng cạnh.
5. **Baseline FNETS** (phần khử nhân tố, sau đó PCMCI+): cần cài R và gói `fnets`, sẽ **hỏi trước**. Phương án không cần R là thay bằng khử nhân tố PCA tĩnh hoặc động viết bằng Python, nhưng khi đó phải ghi rõ đây không phải FNETS gốc.

**Quy tắc dừng gợi ý cho P2** (sẽ chốt trong luật đọc):
- Nếu Δfalse ≥ 0.05 hoặc phần chênh gần–xa biến mất dưới A1, A2 hoặc A3, thì GAP-A ở P1 là do cấu hình hoặc tiền xử lý. Khi đó TS-G1 về NO METHOD GAP.
- Nếu GAP-A vẫn còn dưới mọi biến thể, **và** khử nhân tố toàn cục không xóa được phần chênh gần–xa, thì khoảng trống (2) có bằng chứng dữ liệu. Lúc đó mới chuyển sang thiết kế cơ chế.
