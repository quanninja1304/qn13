# Pilot mức thuật toán cho T4-L

> Ngày 2026-11-06. Script: `T4L_algorithm_pilot.py`, `T4L_pilot_analysis.py`, `T4L_pilot_diagnostics.py`. Số: `T4L_pilot_results.jsonl`, `T4L_pilot_summary.json`, `T4L_pilot_checks.json`, `T4L_pilot_diagnostics.json`. Log: `T4L_pilot_run_log.txt`, `T4L_pilot_diagnostics_log.txt`.
> Mô phỏng tuyến tính Gauss do tôi thiết kế, không có dữ liệu thật. Ngưỡng K8 là đề xuất ở [kill test §8](T4_kill_test_vi.md), viết cho đo được; **user chưa chốt**. Số thô được lưu nên có thể đọc lại nếu đổi ngưỡng.

## 1. Kết luận

**Theo luật khai báo trước: NO-GO.**

| Điều kiện K8, gộp các ô cơ chế trộn | Yêu cầu | Kết quả | Đạt |
|---|---|---|---|
| (a) Claim định hướng sai, LiftG2 so với M1 | ≤ 0.70, cận trên CI < 1 | **1.062** [1.025, 1.103] | Không |
| (b) Claim định hướng đúng, LiftG2 so với M1 | ≥ 0.90 | 0.996 [0.989, 1.004] | Có |
| (c) Không baseline đơn giản nào hòa hoặc thắng | Không có | LW, Naive, Flag, MI, FCI-R đều hòa hoặc thắng | Không |

LiftG2 **không giảm mà còn tăng nhẹ** claim sai so với M1, với số claim đúng gần như bằng nhau. Naive, tức không xác nhận gì, có ít claim sai hơn LiftG2 (0.89 lần) và số claim đúng bằng nhau.

**Khuyến nghị [Inference]: dừng T4-L.** Lợi thế lớn ở mức một bộ ba biến không còn ở mức thuật toán. Chẩn đoán post hoc (§4) gợi ý lý do: phần lớn claim sai đến từ sai số CI chứ không từ missing data, target listwise đúng ở oracle nhưng chỉ còn khoảng một phần ba số claim, và đường tới nó ở finite sample nhiều lỗi. Quyết định đóng hướng là của bạn. **Vẫn chưa có hướng dự phòng.**

## 2. Thiết kế

- **Nhiệm vụ, giống nhau cho mọi phương pháp:** từ dữ liệu thiếu, output claim trên O, dưới Assumption 1, có latent, α = .05, tập điều kiện ≤ 3 từ các kề hiện tại, PC-stable, không có pha possible-d-sep, R0–R4. So với DAG thật.
- **Dữ liệu:** bậc kỳ vọng 2.5, round(.15p) latent, 60% biến thiếu, 1–2 cha của chỉ báo (được phép self-masking), hiệu ứng b ~ U(.5, 1.5). Cơ chế trộn: mỗi chỉ báo rút đều từ cộng tính, tương tác, chẵn (z² − 1), MCAR.
- **Lưới:** p ∈ {10, 20}, cơ chế ∈ {trộn, cộng tính, MCAR}, ρ ∈ {.1, .25}, n ∈ {1000, 4000}. Tổng 504 bộ dữ liệu (30 đồ thị mỗi ô ở p = 10, 12 đồ thị ở p = 20), cộng 160 ở tầng MVPC.
- **Phương pháp:** LW; Naive; M1 (Algorithm 1); LiftG1 và LiftG2 (thay bước xác nhận bằng chuỗi chỉ báo, mô hình chính hiệu ứng và mô hình có bình phương, tích); PP và PPL2 (skeleton naive, R0 xác nhận theo proof, không có R1–R4); Flag; MI; FCI-R (chỉ p = 10); MVPC (tầng riêng).

**Kiểm tra oracle, đạt cả hai điều kiện bắt buộc:**
- V1: chuỗi chỉ báo trùng phép tách listwise, 0 sai lệch trên 31 387 truy vấn.
- V2: Lift-FCI bằng hệt LW trên 400 đồ thị; LW và PP 0 claim sai; Naive có claim sai trên 91 đồ thị.
- V3: bài kiểm định linear probability cho cùng kết luận với bản logistic ở 99–100% trường hợp trên ba họ A, B, D.

## 3. Kết quả chính

Claim định hướng sai / đúng, trung bình mỗi đồ thị, cơ chế trộn:

| p, ρ, n | Hàng listwise | LW | Naive | M1 | LiftG1 | LiftG2 | PP | MI |
|---|---|---|---|---|---|---|---|---|
| 10, .1, 1000 | 534 | 16.1/66.3 | 15.4/67.3 | 15.2/67.6 | 15.1/66.9 | 16.4/67.5 | 12.9/62.1 | 15.5/66.5 |
| 10, .1, 4000 | 2125 | 13.3/69.2 | 12.1/68.1 | 12.2/69.5 | 11.8/68.0 | 13.0/67.8 | 8.2/59.2 | 11.7/67.4 |
| 10, .25, 1000 | 178 | 16.3/67.2 | 14.7/67.7 | 15.1/68.0 | 14.9/67.8 | 15.8/67.9 | 12.3/62.2 | 15.4/68.7 |
| 10, .25, 4000 | 706 | 14.8/68.2 | 11.7/68.1 | 12.6/67.5 | 11.4/66.8 | 12.6/67.0 | 7.3/56.9 | 13.4/68.9 |
| 20, .1, 1000 | 277 | 37.1/330 | 32.9/328 | 33.5/330 | 32.7/328 | 33.4/329 | 30.2/322 | 32.6/331 |
| 20, .1, 4000 | 1132 | 42.1/326 | 33.8/326 | 39.0/326 | 34.8/325 | 44.1/326 | 28.5/299 | 34.1/325 |
| 20, .25, 1000 | 32 | 44.8/324 | 36.2/329 | 38.5/329 | 37.2/328 | 37.2/330 | 34.2/322 | 35.6/330 |
| 20, .25, 4000 | 129 | 47.1/324 | 26.8/332 | 29.8/330 | 29.9/329 | 36.8/331 | 19.9/304 | 29.8/331 |

Tỉ lệ so với M1 (sai, đúng), gộp theo cách của K8. K8 chỉ dùng cột cơ chế trộn; hai cột còn lại để đối chiếu.

| So với M1 | Trộn | Cộng tính | MCAR |
|---|---|---|---|
| LiftG2 | 1.06, 1.00 | 1.07, 0.99 | 0.96, 1.00 |
| LiftG1 | 0.96, 0.99 | 1.03, 0.99 | 0.96, 1.00 |
| Naive | 0.95, 1.00 | 0.96, 1.00 | 0.95, 1.00 |
| LW | 1.16, 0.99 | 1.19, 1.00 | 1.17, 0.99 |
| MI | 0.98, 1.00 | 0.97, 1.00 | 0.95, 1.01 |
| PP | 0.77, 0.92 | 0.78, 0.93 | 0.75, 0.93 |
| PPL2 | 0.77, 0.91 | 0.75, 0.91 | 0.76, 0.93 |
| Flag | 1.14, 0.95 | 1.47, 0.86 | 1.01, 1.00 |

**Đọc thêm [Inference]:**
- **Cơ chế cộng tính, họ thuận lợi nhất cho lift ở mức bộ ba, cũng không có lợi** (1.07). Cả LiftG1 cũng 1.03.
- **PP giảm 23% claim sai và mất 8% claim đúng, nhưng tỉ lệ này gần như y hệt ở MCAR** (0.75, 0.93). Vậy đó là hiệu ứng thận trọng của việc bỏ R1–R4, không phải xử lý missing data.
- **PPL2 không khác PP.** Trong FCI đầy đủ, thay test trực tiếp bằng test chỉ báo gần như không đổi gì.
- Dưới MCAR, Lift gần như bằng Naive, vì không phát hiện được phụ thuộc chỉ báo. Lợi 4–5% so với M1 chỉ là bỏ bước xác nhận trên ít hàng.

**Tầng MVPC (không latent, không self-masking; claim sai/đúng mỗi đồ thị, 80 đồ thị mỗi cơ chế):**

| Cơ chế | M1 | LiftG2 | Naive | MI | MVPC |
|---|---|---|---|---|---|
| Trộn | 13.2/67.7 | 12.6/67.6 | 11.7/68.3 | 11.1/68.4 | **7.8/68.1** |
| Cộng tính | 11.5/67.9 | 11.0/67.5 | 10.8/67.3 | 10.6/68.3 | **8.1/67.4** |

MVPC có ít claim sai nhất trong tầng này. **Không suy ra MVPC thắng nhờ hiệu chỉnh:** nó dùng giả định đủ nhân quả và output CPDAG, trong khi các phương pháp khác chạy kiểu FCI, nên chênh lệch có thể phần lớn do giả định mạnh hơn. Tôi chưa tách được hai yếu tố này.

## 4. Chẩn đoán post hoc: vì sao lợi thế biến mất

> **Viết sau khi đã biết NO-GO, chỉ để giải thích, không có luật đọc, không đổi kết luận.** p = 10, ρ = .25, 30 đồ thị mỗi ô. Lần chạy đầu bị hệ thống dừng vì thiếu RAM sau 4/9 ô; 5 ô còn lại chạy sau theo yêu cầu của bạn, 4 ô cũ giữ nguyên. Seed theo từng ô, nên **các ô khác n dùng đồ thị khác nhau** và không nên so trực tiếp giữa các dòng. `add3` là cơ chế cộng tính với hiệu ứng gấp ba.

**Claim sai mỗi đồ thị / phần quy được cho missing data** (claim sai mà bản dữ liệu đầy đủ không mắc):

| Cơ chế, n | Hàng listwise | Đầy đủ | Naive | LW | M1 | LiftG1 | LiftG2 |
|---|---|---|---|---|---|---|---|
| Trộn, 1000 | 178 | 13.0 | 13.2 / 2.1 | 15.5 / 4.8 | 13.1 / 2.1 | 13.5 / 2.2 | 13.9 / 2.4 |
| Trộn, 4000 | 707 | 8.8 | 10.5 / 3.2 | 14.2 / 6.9 | 12.1 / 5.1 | 12.2 / 5.2 | 14.4 / 7.7 |
| Trộn, 20000 | 3595 | 7.7 | 8.6 / 2.5 | 11.3 / 5.7 | 11.4 / 5.9 | 11.2 / 5.5 | 12.4 / 7.7 |
| Cộng tính, 1000 | 176 | 12.4 | 13.5 / 3.1 | 15.5 / 5.9 | 13.9 / 3.5 | 14.1 / 4.1 | 14.1 / 3.8 |
| Cộng tính, 4000 | 717 | 9.1 | 9.2 / 2.0 | 11.4 / 5.1 | 9.5 / 2.7 | 9.2 / 3.4 | 10.2 / 3.4 |
| Cộng tính, 20000 | 3648 | 11.0 | 12.4 / 2.9 | 14.2 / 5.3 | 13.6 / 4.2 | 14.6 / 7.6 | 14.8 / 8.2 |
| add3, 1000 | 190 | 12.3 | 12.7 / 2.5 | 16.1 / 5.5 | 13.0 / 2.8 | 13.7 / 5.0 | 13.6 / 4.6 |
| add3, 4000 | 751 | 12.2 | 13.1 / 3.3 | 16.0 / 5.8 | 13.9 / 4.4 | 14.5 / 6.5 | 14.5 / 6.4 |
| add3, 20000 | 3596 | 9.0 | 12.1 / 4.2 | 16.9 / 9.8 | 13.5 / 6.9 | 17.0 / 12.8 | 15.9 / 10.3 |

**Mức độ khớp với target listwise**, trên các truy vấn test-wise không bác bỏ trong lần chạy Naive, so với d-separation oracle ở regime O:

| Cơ chế, n | Target phụ thuộc / tổng | M1 nhầm "tách" | LiftG1 | LiftG2 | M1 nhầm "phụ thuộc" | LiftG1 | LiftG2 |
|---|---|---|---|---|---|---|---|
| Trộn, 1000 | 691 / 998 | .897 | .961 | .854 | .042 | .003 | .013 |
| Trộn, 4000 | 758 / 951 | .860 | .821 | .636 | .016 | .010 | .031 |
| Trộn, 20000 | 635 / 939 | .753 | .646 | .389 | .049 | .020 | .095 |
| Cộng tính, 1000 | 808 / 992 | .938 | .749 | .823 | .054 | .038 | .054 |
| Cộng tính, 4000 | 794 / 974 | .935 | .592 | .674 | .061 | .033 | .017 |
| Cộng tính, 20000 | 731 / 906 | .885 | .302 | .334 | .046 | .051 | .057 |
| add3, 1000 | 810 / 980 | .909 | .511 | .584 | .024 | .018 | .018 |
| add3, 4000 | 755 / 953 | .836 | .266 | .302 | .030 | .020 | .045 |
| add3, 20000 | 749 / 907 | .712 | .180 | .175 | .038 | .032 | .152 |

**Kiểm tra oracle về việc cắt tập điều kiện** (`T4L_truncation_oracle_check.py`, 60 đồ thị p = 10, cơ chế trộn, ρ = .25). Tôi thêm phép này vì nghi kết quả do pilot giới hạn tập điều kiện ≤ 3 và không có possible-d-sep. Luật khai báo trước: việc cắt góp phần nếu LW3 có claim sai trên > 10% đồ thị trong khi LWall không có. **Kết quả: không góp phần.**

| Oracle, mỗi đồ thị | Claim sai | Claim đúng | Số cạnh | Đồ thị có claim sai |
|---|---|---|---|---|
| Đầy đủ, tập ≤ 3 | 0 | 61.5 | 15.1 | 0% |
| LW, tập ≤ 3 | 0 | **20.7** | 23.3 | 0% |
| LW, vét cạn | 0 | 21.2 | 21.4 | 0% |
| Naive, tập ≤ 3 | 3.4 | 58.0 | 18.2 | 62% |
| Naive, vét cạn | 3.7 | 59.3 | 17.2 | 62% |

**Đọc được [Inference]:**

1. **Lỗi nền chủ yếu do sai số CI ở finite sample.** Dữ liệu đầy đủ có 8–13 claim sai ở finite sample nhưng 0 ở oracle, kể cả khi cắt tập điều kiện. Phần quy cho missing data là 2–13 tùy phương pháp.
2. **Target listwise đúng nhưng rất nghèo, và ở n thực tế các phương pháp còn rất xa nó.** Ở oracle, LW chỉ có 20.7 claim đúng, khoảng một phần ba của dữ liệu đầy đủ, và 68–83% truy vấn test-wise không bác bỏ có target phụ thuộc. Ở finite sample LW, M1 và cả LiftG2 vẫn có 64–72 claim đúng, ngay cả ở n = 20000. Vậy bảo đảm oracle của M1 mô tả một đích mà trong mô phỏng này không phương pháp nào tới gần ở các n đã thử.
3. **Sửa cách nói trước đây của tôi.** Tôi từng viết "target listwise có thể không đáng tiến tới" theo nghĩa nó có hại. Chính xác hơn: ở oracle nó không có claim sai. Vấn đề là **đường tới nó ở finite sample nhiều lỗi**, và đích thì mất phần lớn claim. **Giả thuyết:** khi chỉ phát hiện được một phần các phụ thuộc do selection, mẫu tách biệt trở nên không nhất quán và sinh định hướng sai; chưa kiểm chứng riêng.
4. **Failure mode có thật theo target, nhưng không theo DAG.** M1 nhầm "tách" 71–94%; lift khớp tốt hơn nhiều khi n lớn và hiệu ứng mạnh (.175 so với .712). Nhưng ở chính ô đó LiftG2 có 10.3 claim sai quy cho missing data so với 6.9 của M1, và ít claim đúng hơn (63.7 so với 68.3). **Tăng liều không đảo kết quả, mà làm lift tệ hơn.**
5. **Naive có ít claim sai quy cho missing data nhất ở 8/9 ô** (ô còn lại xấp xỉ bằng M1, cùng khoảng 2.1), và con số 2.0–4.2 của nó xấp xỉ mức 3.4 ở oracle. Vậy lỗi của Naive có vẻ chủ yếu là tính không đúng đắn đã biết ở oracle. Naive không an toàn: claim sai trên 62% đồ thị ở oracle. Nó chỉ đổi mức sai đó lấy nhiều claim hơn.
6. **Khớp ở mức truy vấn không dẫn đến khớp ở mức cạnh.** LiftG2 nhầm "tách" chỉ 17.5% mỗi truy vấn nhưng số claim vẫn gấp ba target. **Giả thuyết:** một lần chấp nhận nhầm là đủ xóa cạnh, và mỗi cặp có nhiều tập điều kiện để thử, nên sai số tích lũy.
7. **Test chỉ báo linh hoạt mất hiệu chỉnh khi n và hiệu ứng lớn:** tỉ lệ nhầm "phụ thuộc" của LiftG2 lên .152 ở add3, n = 20000, trong khi LiftG1 chỉ .032. **Giả thuyết:** phần phi tuyến chưa mô hình hóa của R theo (y, W) tương quan với các số hạng của x.

**Hệ quả [Inference]:** câu hỏi đáng giá hơn "đạt target listwise nhanh hơn" có thể là **chọn target nào**: đánh đổi giữa khoảng 3.4 claim sai với 58 claim đúng (Naive) và 0 claim sai với 21 claim đúng (listwise), ở một mô phỏng cụ thể. Tôi chưa kiểm tra văn liệu về câu hỏi này, và các con số phụ thuộc vào cơ chế sinh dữ liệu của tôi.

## 5. Điều chưa loại trừ

- **n cực lớn:** ở n rất lớn M1 và lift có thể tiến về 0 claim sai, đúng như oracle. Điều này không cứu được T4-L: khi đó chúng cũng chỉ còn khoảng 21 claim đúng, và M1 tới cùng đích đó.
- **Đồ thị lớn hơn, dày hơn, dữ liệu phi Gauss, mô hình chỉ báo phi tham số.** Có thể cải thiện test, nhưng không giải quyết vấn đề ở §4 mục 2–4.
- **Metric khác.** K8 tính cả claim non-ancestor lan truyền theo đường; đếm riêng đầu mũi tên trên cạnh có thể nhạy hơn. Số liệu hiện lưu không tách được.
- **Cấu trúc tập trung.** Cha của chỉ báo trong mô phỏng được chọn ngẫu nhiên. Dữ liệu tập trung nhiều cấu trúc bất lợi kiểu họ A có thể cho kết quả khác; không có bằng chứng dữ liệu thật như vậy.

## 6. Giới hạn và minh bạch

- **Ngưỡng K8 chưa được bạn chốt.** Với chênh lệch quan sát (LiftG2 tăng claim sai), đổi ngưỡng hợp lý cũng khó đảo kết luận về (a).
- **FCI tự viết**, không có possible-d-sep, không R5–R10. Kiểm tra oracle ở §4 cho thấy việc cắt không sinh claim sai ở oracle, nhưng chỉ trên p = 10 và finite sample không được kiểm tra. Tôi chưa đối chiếu với thư viện độc lập; đã định làm nhưng chưa làm. Oracle V1, V2 chỉ kiểm tra tính nhất quán nội bộ.
- **MI do tôi tự viết**, kiểu Witte et al. và `micd`, không phải gói của họ. **Flag** là bộ lọc đơn giản lấy cảm hứng từ MVPC Step 3, không phải MVPC.
- **Trường `flag_false` trong `T4L_pilot_checks.json` là chỗ chưa dùng**: luôn bằng 0 vì code không tính nó. Không phải kết quả kiểm tra. Flag không được kiểm tra oracle.
- **Thời gian trong log không so sánh được giữa các phương pháp**, vì kết quả test được cache và dùng chung theo thứ tự chạy.
- **Bootstrap chỉ ở mức đồ thị trong từng p.** p = 20 chỉ có 12 đồ thị mỗi ô, nên số theo ô nhiễu; kết luận K8 dựa trên số gộp.
- Quick-run chỉ để kiểm tra code và thời gian: tôi đọc kiểm tra oracle V cùng thời gian chạy, không đọc số claim của các phương pháp, rồi xóa kết quả.
- Tôi đã biết kết quả ở họ A trước khi thiết kế pilot, nên cơ chế trộn có chủ đích gồm cả dạng thuận và bất lợi cho lift.

## 7. Trạng thái các hướng T4

| Hướng | Trạng thái đề xuất | Bằng chứng |
|---|---|---|
| T4 theo card gốc (giữ target bằng luật cục bộ, truy vấn O) | NO-GO | [Kill test §4](T4_kill_test_vi.md) |
| Regime-indexed FCI làm cơ chế trung tâm | Không nên | [Kill test §4](T4_kill_test_vi.md); PP ở đây chỉ là thận trọng |
| T4-L (lift bằng chỉ báo) | **NO-GO theo K8**, chờ user xác nhận đóng | Báo cáo này |

**Đóng góp có thể giữ lại:** ví dụ tường minh về ghép regime, và quan sát rằng ở mô phỏng này bước xác nhận listwise không làm giảm claim sai về DAG, dù nó có lý do oracle. Đó là ghi chú nhỏ cần kiểm chứng thêm, không phải đóng góp phương pháp đủ theo tiêu chí dự án.
