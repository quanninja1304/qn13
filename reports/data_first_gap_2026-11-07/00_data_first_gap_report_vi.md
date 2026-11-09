# Xác định lại research gap theo hướng dữ liệu trước

> Ngày 2026-11-07. Theo yêu cầu của user: chỉ đề xuất gap khi vấn đề được nhìn thấy trên dữ liệu uy tín, không bắt đầu từ chứng minh toán học.
> Nhãn: **[Verified]** có trong nguồn gốc hoặc output đã chạy; **[Inference]** suy luận của agent; **[Hypothesis]** chưa kiểm chứng; **[Unresolved]** chưa rõ.
> Hồ sơ dữ liệu: [`DATA_MANIFEST_vi.md`](DATA_MANIFEST_vi.md). Bài cần đọc: [`PAPERS_TO_ADD_vi.md`](PAPERS_TO_ADD_vi.md).

## 1. Kết luận

**Có một ứng viên đáng đi tiếp, nhưng chưa được gọi là gap đã chứng minh.** Bằng chứng mới đến từ **một hệ vật lý** (Causal Chamber light tunnel), Sachs chỉ là phụ vì ground truth bị tranh cãi, và **phép thử bác bỏ quan trọng nhất chưa chạy**: lớp phương pháp lai BOSS-FCI, GFCI, FCIT.

**Hiện tượng trung tâm [Verified, trên dữ liệu này, n = 10000]:**

| Phương pháp | Cạnh mạnh giữ được (RGB → sensor) | Hướng đúng | Ba cặp `ir_i`–`vis_i` gọi là confounded | Tổng số cạnh |
|---|---|---|---|---|
| BOSS, BIC chuẩn | 21/21 | 21/21 | 0/3 | 41 |
| BOSS, phạt × 32 | 21/21 | 21/21 | 0/3 | 26 |
| PC, α = .05 | 11/21 | 10/21 | 0/3 | 26 |
| FCI, α = .05 | **7/21** | **0/21** | **3/3** | 20 |

Phương pháp cho phép confounding nói đúng về confounding nhưng mất hai phần ba cạnh mạnh. Phương pháp giữ được cạnh thì khẳng định sai về confounding. **Trong các phương pháp đã chạy, không phương pháp nào làm được cả hai.**

**Điều chưa biết có thể xóa ngay gap này:** BOSS-FCI, GFCI, FCIT sinh ra chính vì lý do tương tự. Nếu chúng đạt cả hai trên Chamber thì ứng viên này đóng.

## 2. Bản đồ kết quả theo luật khai báo trước

Mỗi luật được ghi trong docstring script trước lần chạy đầy đủ. Ngưỡng là lựa chọn quản lý dự án.

| Thí nghiệm | Câu hỏi | Kết quả theo luật | Đọc đúng ra sao |
|---|---|---|---|
| E1, L1 | Test CI có giữ mức trên các độc lập biết trước không? | **PAIN** | Actuator–actuator và actuator–sensor giữ tốt (≤ .067). Sensor–sensor cho cha: 13 → 26 → 36% khi n tăng. Gồm ba cặp r ≈ .7 và nhiều cặp r rất nhỏ |
| E1b, L6 | Phần r nhỏ đó là thật hay sai số boosting? | **UNCLEAR** | Đối chứng knock-out bác bỏ 11% so với 36%. Ba cặp r ≈ .7 chắc chắn thật; các cặp r < .03 không tách được khỏi sai số hồi quy |
| E2, L2 | Precision có đảo chiều theo n không? Có hơn baseline không? | **REVERSAL: không** (PC, GES). **NO SKILL: chỉ** ở `sachs_c1` | GES giảm .08, chưa tới ngưỡng .10. BOSS, GRaSP, DirectLiNGAM giảm ≥ .13 nhưng **không nằm trong luật**, nên chỉ là quan sát |
| E3, L3 | Điểm nội bộ có chọn được điểm vận hành không? | **MIXED** | Không đạt PAIN, cũng không đạt NO PAIN. Xem §3.3 |
| E6, L5 | Precision giảm do đâu? | **NONLINEARITY** | **Bác bỏ dự đoán ban đầu của tôi** rằng nguyên nhân chính là phụ thuộc residual |
| E7 | Chấm lại có đổi thứ hạng không? | Không luật, post hoc | **Gần như không** (Spearman .89–1.00) |
| E8 | Vì sao PC mất cạnh mạnh? | Không luật, post hoc | Tập tách luôn chứa sensor; còn tồn tại trong knock-out tuyến tính |

## 3. Failure modes

### 3.1. Failure A: phép đo dư thừa làm mất cạnh mạnh nhất (ứng viên chính)

- **Triệu chứng [Verified]:** PC mất 10/21 cạnh mạnh, FCI mất 14/21 ở n = 10000. Recall của PC chỉ .33 trong khi BOSS đạt .59. Thêm dữ liệu không sửa được.
- **Cơ chế quan sát [Verified, E8]:** cả 10 cạnh PC mất đều có tập tách chứa sensor. Ví dụ `green → ir_2`: r = +.849 cho các cha khác, nhưng −.020 cho tập tách `{ir_1, current, ir_3, vis_3}`.
- **Không phải do sai dạng hàm [Verified, E8]:** ở knock-out tuyến tính, nơi DAG đúng tuyệt đối và nhiễu độc lập, PC vẫn mất 10/21.
- **Không chỉ do gần-tất-định [Verified, E8]:** nhân nhiễu sensor lên 5 lần, R² trung vị từ .92 xuống .32, PC vẫn mất 7/21.
- **Giải thích khả dĩ [Inference]:** 3 actuator điều khiển 9 sensor, nên một vài sensor anh em gần như khôi phục được actuator. Đây là dạng vi phạm adjacency-faithfulness do **dư thừa đo lường**, không phải do các hiệu ứng triệt tiêu nhau.
- **Remedy mạnh nhất [Verified qua tóm tắt]:** nhóm permutation (GRaSP, BOSS) dùng giả định yếu hơn faithfulness, và trên dữ liệu này BOSS thực sự giữ 21/21. Nhưng chúng là DAG, không nói được về latent. Lớp lai BOSS-FCI, GFCI, FCIT chưa được chạy.
- **Giả thuyết mở [Hypothesis]:** bước tinh chỉnh bằng CI của các phương pháp lai có thể xóa lại đúng những cạnh mà BOSS đã giữ, vì tập tách vẫn lấy từ các sensor kề. Chưa kiểm chứng.
- **Điều bác bỏ được vấn đề:** một phương pháp hiện có đạt cả hai trên Chamber; hoặc hiện tượng không lặp lại trên hệ khác.

### 3.2. Failure B: precision giảm theo n ở điểm vận hành mặc định

- **Triệu chứng [Verified, E2]:** chamber, n = 1000 → 10000: BOSS .85 → .72, GRaSP .76 → .56, DirectLiNGAM .71 → .55, GES .68 → .60, recall gần như không đổi. Số cạnh sai tăng theo n, gần như toàn bộ là sensor–sensor (E2b).
- **Nguyên nhân chính [Verified theo L5, E6]:** sai dạng hàm. Giữ hàm phi tuyến, bỏ phụ thuộc residual: precision giảm .23. Tuyến tính hóa: giảm .017, precision .92–1.00. Đối chứng đạt.
- **Điều này đã biết về nguyên tắc [Inference]:** mô hình đặc tả sai hội tụ về mô hình giả-đúng, và cạnh phụ trở nên có ích khi n lớn (White 1982, qua survey CI). Tôi chưa thấy nó được đo trên hệ thật theo cách này, nhưng **chưa audit đủ**.

### 3.3. Failure C: không chọn được điểm vận hành khi thiếu truth (ứng viên dự phòng)

- **Quan sát [Verified, E3, 3 replicate]:** chamber. F1 tốt nhất trong lưới ≈ .70 ở mọi n, đạt bằng hệ số phạt **tăng theo n**: × 2 ở n = 1000, × 16 ở n = 4000, × 32 ở n = 8000.

| n | Tốt nhất | Mặc định GES | BIC chọn | Held-out chọn | LOVO (bản đơn giản) | Stability chọn |
|---|---|---|---|---|---|---|
| 1000 | .707 | .654 | .673 | .683 | .657 | .211 |
| 4000 | .701 | .635 | .616 | .606 | .630 | .377 |
| 8000 | .704 | .604 | .599 | .591 | .593 | .281 |

- **Xác minh một lần chạy [Verified]:** BOSS × 16 và × 32: 3 "cạnh sai" đều là `ir_i`–`vis_i`. BOSS × 1, n = 8000: 16 cạnh sai.
- **Giải thích [Inference]:** các cạnh thừa làm tăng khả năng dự đoán của mô hình tuyến tính thật, nên điểm dự đoán chọn chúng. Điểm dự đoán đang trả lời đúng một câu hỏi khác với câu hỏi nhân quả.
- **Giới hạn:** ở n = 1000 các điểm dự đoán chọn khá tốt, nên đây không phải thất bại toàn phần. LOVO là bản đơn giản của tôi, không phải code tác giả, và chỉ có một replicate trong khi các cột khác có ba. Self-compatibility chưa được đánh giá.

### 3.4. Hiện tượng về benchmark (không đủ làm gap riêng)

- **Cạnh không thể phát hiện [Verified, E2b]:** 12/39 cạnh tham chiếu (LED) có |partial r| < .02 và gain R² ≈ 0 ở n = 10000. Ngay cả phương pháp hoàn hảo cũng chỉ đạt raw recall .69.
- **Ngữ nghĩa [Verified, Gamella et al. §3.1]:** tác giả nói cạnh nghĩa là hiệu ứng can thiệp, việc **thiếu cạnh không loại trừ hiệu ứng**, và có confounding không đo được. Nhưng các benchmark vẫn chấm thuật toán quan sát theo F1 trên graph này (ví dụ CausalArena, [Verified] có dùng Chamber trong phần real-data check).
- **Giả thuyết bị bác bỏ [Verified, E7]:** tôi kỳ vọng chấm lại sẽ đảo thứ hạng. Thực tế chỉ đổi điểm tuyệt đối (BOSS từ khoảng .68 lên khoảng .9), thứ hạng gần như giữ nguyên.
- **Còn lại:** phép chấm theo cạnh không phân biệt được FCI nói `↔` với BOSS nói `→`. Đó là một phần của Failure A.

## 4. Các ứng viên

| # | Ứng viên | Chain | Bằng chứng hiện có | Rủi ro lớn nhất |
|---|---|---|---|---|
| **C1** | Latent-aware discovery khi phép đo dư thừa | Failure A | Mạnh trên 1 hệ, cơ chế đã tách | Lớp lai có thể đã giải quyết; không lặp lại ở hệ khác |
| **C2** | Chọn độ phân giải nhân quả khi đặc tả sai, không có truth | Failure B, C | Vừa, L3 MIXED | Có thể chỉ là mẹo penalty; prior art dày |
| C3 | Kiểm toán benchmark thật | §3.4 | Yếu sau E7 | Chỉ là phê bình; thứ hạng không đổi |
| C4 | Chọn mô hình bằng can thiệp giữ lại | Landscape: < 5% dùng metric can thiệp | **Chưa đo gì** | Chưa có dữ liệu chạy được; prior art (Eigenmann 2020, Gentzel 2019) |

**Ma trận so sánh (đánh giá chủ quan):**

| Tiêu chí | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| Ý nghĩa khoa học | Cao nếu tổng quát hóa | Trung bình–cao | Trung bình | Trung bình–cao |
| Độ tin cậy của gap | Trung bình, chờ R1, R2 | Trung bình | Thấp | Chưa rõ |
| Cơ chế trung tâm mới | Chưa có, mới có giả thuyết | Chưa có | Không | Chưa có |
| Gánh nặng lý thuyết | Vừa | Vừa | Thấp | Thấp |
| Khả thi với máy hiện tại | Cao | Cao | Cao | Thấp (dữ liệu lớn) |
| Thời gian tới bằng chứng đầu | Vài ngày | Vài ngày | Đã có | Vài tuần |

## 5. Khuyến nghị

- **Chính: C1, có điều kiện.** Hiệu ứng lớn nhất, cơ chế đã tách được bằng thí nghiệm, và thẳng vào điều người dùng thực cần: tin được cả cạnh lẫn nhãn confounding. Đúng tinh thần bạn đề ra: vấn đề hiện ra từ dữ liệu trước.
- **Dự phòng: C2.** Dùng chung toàn bộ hạ tầng; nếu C1 bị bác bỏ, C2 không mất gì.
- **Chưa cam kết gì quá phép thử R1, R2 dưới đây.** Hiện chưa có cơ chế mới, nên chưa đạt tiêu chí "central mechanism" của `AGENTS.md`.

**Về mức độ cạnh tranh:** tôi không thể nói C1 đủ cho Q1 hay A*. Điều có thể nói: một bài chỉ gồm các bảng ở đây thì chưa đủ. Nó chỉ có thể cạnh tranh nếu qua được cả ba: lặp lại trên ≥ 3 hệ độc lập, các phương pháp lai thất bại có hệ thống, và có một cơ chế mới sửa được mà không phá nơi khác. Tiền lệ cho thấy phát hiện thực nghiệm đơn giản có thể đủ mạnh (Reisach et al., NeurIPS 2021), nhưng đó là tiền lệ, không phải dự báo.

### Cổng quyết định

| Cổng | Phép thử | NO-GO nếu | Trạng thái |
|---|---|---|---|
| **R1** | Chạy BOSS-FCI, GRaSP-FCI, GFCI, FCIT, LV-Dumb (Tetrad) trên Chamber, cùng dữ liệu, n, reps | Một phương pháp với cấu hình mặc định đạt ≥ 19/21 cạnh mạnh **và** ≥ 2/3 cặp `↔` đúng | **Chưa chạy.** Cần tải Tetrad; Java 17 đã có |
| **R2** | Lặp lại trên ≥ 2 hệ khác có tham chiếu độc lập | Không hệ nào cho thấy mất cạnh do tập tách dư thừa | Chưa chạy. Wind tunnel cần xử lý tự tương quan; Perturb-seq cần dữ liệu lớn |
| **R3** | Liều–đáp ứng trên semi-synthetic: thay đổi mức dư thừa độc lập với độ mạnh cạnh | Mất cạnh không tăng theo mức dư thừa | Chưa chạy |
| **R4** | Đọc: DGES (NeurIPS 2024), Ramsey et al. 2025, Lemeire 2008, Lee et al. 2025, các bài mức A trong danh sách | Đã có phương pháp xử lý đúng bài toán có cả latent | Mới đọc lướt |

Ngưỡng là đề xuất, cần bạn chốt.

### Lộ trình 4–6 tuần (chưa làm gì trong số này)

| Tuần | Việc | Cổng |
|---|---|---|
| 1 | R1, R4. Nếu NO-GO: chuyển sang C2 | R1, R4 |
| 2 | R3, đối chiếu FCI của `causal-learn` với Tetrad để loại lỗi cài đặt | R3 |
| 3–4 | R2: wind tunnel, cân nhắc Perturb-seq nếu có máy mạnh hơn, dữ liệu công nghiệp | R2 |
| 5–6 | Chỉ khi qua R1–R3: thử cơ chế mới, viết đặc tả và đánh giá trước khi cài đặt đầy đủ | |

## 6. Topic card rút gọn: C1

**Câu hỏi:** Trên hệ thật có đo lường dư thừa và confounding không đo được, làm sao đồng thời giữ được các cạnh nhân quả mạnh và phân biệt chúng với phụ thuộc do confounding, mà không biết trước cấu trúc đo lường?

**Prior art gần nhất**

| Nguồn | Đóng góp | Giới hạn liên quan | Hệ quả |
|---|---|---|---|
| [Gamella et al. 2025](https://arxiv.org/abs/2404.11341) | Testbed, ghi GES, UT-IGSP gặp khó với hiệu ứng yếu và phi tuyến | Không phân tích FCI, không tách cơ chế | Dữ liệu nền |
| [Lam et al. 2022](https://arxiv.org/abs/2206.05421), [Andrews et al. 2023](https://arxiv.org/abs/2310.17679) | GRaSP, BOSS, yếu hơn faithfulness | Không latent | Giải thích vì sao BOSS giữ được cạnh |
| [Ramsey et al. 2025](https://arxiv.org/abs/2510.04263) | BOSS-FCI, GRaSP-FCI, FCIT, LV-Dumb | **Đối thủ trực tiếp. Chưa kiểm tra trên trường hợp này** | Có thể xóa gap (R1) |
| [DGES, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/ec52572b9e16b91edff5dc70e2642240-Paper-Conference.pdf) | Score-based với quan hệ tất định | Đọc tóm tắt; cần đọc giả định về latent | Có thể trùng một phần |
| [Lemeire 2008](http://parallel.vub.ac.be/~jan/papers/JanLemeire_CausalInferenceWithDeterministicRelations2008.pdf) | Vi phạm adjacency-faithfulness do tất định | Tất định, không phải dư thừa ở R² vừa | Tiền đề |
| [Lee et al. 2025](https://proceedings.mlr.press/v286/lee25a.html) | Hạn chế tập điều kiện vì quan hệ gần tất định | Chỉ qua kết quả tìm kiếm | Baseline tiềm năng |

**Phát biểu gap, phần lớn là giả thuyết:** Với giả định cho phép latent, FCI đạt tính đúng đắn tiệm cận, nhưng trên Causal Chamber light tunnel nó mất phần lớn cạnh mạnh ở n = 10000 do tập tách gồm các sensor dư thừa **[Verified]**. Các phương pháp lai có thể khắc phục **[Unresolved]**. Nghiên cứu tìm cơ chế phân biệt tập tách thật với tập tách đo lường dư thừa **[Hypothesis]** mà không làm mất khả năng phát hiện confounding.

**Cơ chế ứng viên, chưa kiểm tra [Hypothesis]:** nếu `Z` tách `A` và `Y` chỉ vì `Z` là hậu duệ dư thừa của `A`, thì khi `A` được gán ngẫu nhiên hoặc có can thiệp, mức dự đoán được `A` từ `Z` đóng vai trò chỉ báo. Có thể định nghĩa một chứng cứ dạng "tập tách có đang tái tạo chính biến cần tách không" (ví dụ R² của `A` theo `Z`) và không xóa cạnh khi chứng cứ cao. Đây chỉ là điểm khởi đầu. Nó có thể trùng với ý tưởng đã có về kiểm soát cộng tuyến và có thể phá FCI ở nơi khác. **Không được xem là đóng góp cho tới khi qua R1–R4.**

**Baseline bắt buộc:** PC, FCI, RFCI (chuẩn); BOSS-FCI, GFCI, FCIT (đối thủ); BOSS với phạt mạnh, FCI giới hạn tập điều kiện (đơn giản); ablation bỏ cơ chế mới.

**Kết quả có thể có:** tối thiểu là một nghiên cứu thực nghiệm đa hệ về cơ chế mất cạnh, có giá trị ngay cả khi không có phương pháp mới. Mạnh là cơ chế sửa được, kèm bảo đảm phù hợp. Mở rộng là áp dụng cho dữ liệu perturbation.

**Quyết định:** `Conditional`. Phép thử rẻ nhất tiếp theo là R1.

**Tóm tắt giả định (150–200 từ, không có kết quả, chỉ minh họa nếu qua các cổng):**

> Constraint-based causal discovery under latent confounding relies on conditional independence statements that real measurement systems can violate in a specific way: when several measured variables are noisy readings of the same physical quantity, a small set of them can nearly reconstruct a cause, and a strong causal edge appears separable. We study this redundancy failure on physical testbeds with documented causal effects and on perturbation data, and we separate it experimentally from nonlinearity and weak effects. We ask whether existing score-constraint hybrids preserve strong edges while still identifying confounded pairs, and we characterize when they do not. We then propose a criterion that distinguishes genuine separators from redundant measurement separators, and we evaluate it against standard, hybrid and simple baselines on synthetic controls with varying redundancy and on real systems, reporting edge retention, confounding labels and failure boundaries.

## 7. Trả lời trực tiếp

1. **Vấn đề quan trọng nhất:** tin được kết quả discovery trên hệ thật, nơi đồng thời có đo lường dư thừa, confounding và sai dạng hàm. C1 là phần đã đo được rõ nhất.
2. **Cơ chế có novelty mạnh nhất:** hiện **chưa có cơ chế nào đã kiểm chứng**. Ứng viên ở §6 chỉ là giả thuyết.
3. **Làm được ngay với tài nguyên hiện tại:** R1, R3, R4. R2 một phần. Perturb-seq chưa, vì RAM.
4. **Cân bằng chất lượng–rủi ro tốt nhất cho Q1:** C1 nếu qua R1, R2; nếu không thì C2.
5. **Điều kiện để cạnh tranh ở ICML/NeurIPS:** thất bại có hệ thống của phương pháp lai trên ≥ 3 hệ độc lập, cộng cơ chế mới sửa được với phân tích giới hạn rõ ràng. Thiếu một trong hai thì không.
6. **Bằng chứng không thể thiếu trước khi đầu tư nhiều tháng:** R1 và R2.
7. **Nên gác lại:** C3 như một đề tài độc lập (E7 bác bỏ giả thuyết chính của nó); C4 cho tới khi có máy mạnh hơn; "chọn target dưới missing data" vì không có bằng chứng thực nghiệm mới.

## 8. Giới hạn và minh bạch

- **Một hệ vật lý.** Chamber là hệ thiết kế: actuator gán ngẫu nhiên, sensor dư thừa theo cấu trúc. Có thể không đại diện. Wind tunnel chưa dùng được vì dữ liệu có tự tương quan rất cao (lag-1 ≈ .99 trên actuator), trái giả định i.i.d. của các test này.
- **"Cạnh mạnh" là định nghĩa post hoc** (RGB → sensor), đặt sau khi xem kết quả. E7, E8 cũng post hoc, không có luật đọc.
- **Sachs:** ground truth bị tranh cãi (Brouillard et al. 2025). Ánh xạ hàng sang điều kiện trong `cyto_full_data.csv` suy từ cỡ mẫu, không có trong file. Không kết luận gì về độ chính xác trên Sachs; `sachs_c1` chỉ mang tính mô tả.
- **E3 chưa xong:** lần chạy bị hệ thống dừng do thiếu RAM trong lúc xử lý Sachs n = 3000 (replicate 3), Sachs n = 6000 chưa chạy. Phần Chamber, phần quyết định L3, đã đủ 3 replicate.
- **Hai lỗi của tôi đã sửa và ghi lại:** hệ số BIC lệch so với mặc định `causal-learn` (phát hiện trước lần chạy đầy đủ); nhãn `GES_1` sai trong phân tích E3 khiến `gain` là NaN (đã sửa; kết luận L3 không đổi). Ngoài ra trong E1 phần 3, quy tắc nhận diện target bỏ sót các file can thiệp LED, nên chỉ có 96 cặp hậu duệ được dùng. Lệnh tải file Sachs đầu tiên của tôi dùng cờ `-k` và bị từ chối; tôi đã lấy lại đúng cách từ nguồn khác.
- **LOVO** là bản đơn giản của tôi. **FCI và PC** là `causal-learn` 0.1.4.8, cấu hình mặc định. Tôi chưa đối chiếu với Tetrad, và kết quả mất cạnh có thể phụ thuộc phần nào vào cài đặt và thứ tự biến.
- **Bản chạy quick** cho tôi thấy một phần log thời gian và vài số trước khi có bản đầy đủ. Luật L1, L2, L3, L5, L6 được viết trước khi có số của chính thí nghiệm đó, nhưng các thí nghiệm sau được thiết kế sau khi đã xem kết quả các thí nghiệm trước.
- **Audit văn liệu chưa đủ để tuyên bố novelty.** Nhiều bài mới chỉ đọc tóm tắt, xem mức đọc trong `PAPERS_TO_ADD_vi.md`.
