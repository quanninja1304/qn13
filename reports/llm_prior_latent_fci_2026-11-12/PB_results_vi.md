# Kết quả P-B: guess sai có kiểu lan truyền thế nào trong FCI oracle (12/11/2026)

> **Luật đọc:** [`PA_PB_reading_rules_vi.md`](PA_PB_reading_rules_vi.md), khóa 12/11; các làm rõ 1–8 ở §7 đều ghi **trước** khi đọc kết quả.
> **Số liệu:**
> - `PB_results.jsonl`: 11 612 dòng.
> - `PB_analysis_outputs.json` và `PB_analysis_log.txt`, sinh bởi `PB_analysis.py`.
> - `PB_posthoc_contradiction_log.txt`: phân tích post hoc ở §4.
>
> **Nhãn:** [Verified-run] số từ lần chạy này; [Post hoc] phân tích thêm sau khi xem kết quả, không dùng để quyết định; [Inference]; [Hypothesis].

## 1. Trạng thái chạy

- **Đồ thị tổng hợp:** 400/400 chạy xong, trong đó 270 đồ thị có ít nhất một cặp ↔ (B).
- **bnlearn:** 19 đơn vị sau khi gộp tập ẩn trùng. 13 chạy xong; 6 timeout ở mức 600 giây (insurance ×3, alarm_3, hailfinder_1, hepar2_1). bnlearn chỉ dùng để đối chiếu.
- **Hạ tầng (phát hiện phụ, [Verified-run]):** `dag2pag` của causal-learn 0.1.4.8 **không sound**. Trên 40 đồ thị kiểm thử, nó cho 79 claim sai (9 FA, 70 FNA). Chuẩn RB0 vì vậy đổi sang `fci()` oracle (§7 mục 1). Bất kỳ công trình nào dùng `dag2pag` làm ground truth PAG đều có thể bị ảnh hưởng.

## 2. Đọc theo luật

| Luật | Kết quả [Verified-run] | Phán quyết |
|---|---|---|
| RB0 (i) | 413/413 baseline trùng `fci()` oracle; 0 claim sai | **Đạt** |
| RB0 (ii) | T6 và T7 (chèn đúng): 0 claim sai trên 2772 lần chèn | **Đạt** |
| **RB2** | Prop(T1) = **1.06**, Prop(T2) = 0.19, Prop(T3) = 0.61. ΔL = **−0.45**, CI [−0.53, −0.36] | **NO LATENT-SPECIFIC HARM** |
| RB3 | 79% số lần chèn T2/T3 có lan truyền là "im lặng" theo định nghĩa đã khóa | **SILENT**, nhưng xem §4: định nghĩa có điểm mù |

**H-prop bị bác bỏ, và chiều thực tế ngược với giả thuyết.** Đảo chiều một cạnh (T1), kiểu lỗi có cả dưới causal sufficiency, lan **nhiều nhất**. Hai kiểu chỉ có dưới biến ẩn lan ít hơn: T3 bằng khoảng 58% T1, T2 bằng khoảng 18%. Kết quả giữ nguyên ở cả 8 ô lưới và ở bnlearn (T1 1.52, T3 0.68, T2 0.05).

## 3. Bảng mô tả (RB1, RB4; đồ thị tổng hợp)

| Kiểu | Guess sai | Tỉ lệ có lan | Prop trung bình | Conflict (định nghĩa khóa) | Luật lan chính |
|---|---|---|---|---|---|
| T1 | đảo chiều A → B | 0.40 | 1.06 | 0.68 | R1/R2 (88%), R4 |
| T2 | ↔ đoán thành → | 0.18 | 0.27 | 0.58 | R1/R2, R4 |
| T3 | → đoán thành ↔ | 0.25 | 0.61 | **0.00** | R1/R2 (96%) |
| T4 | gián tiếp đoán thành trực tiếp | **0.00** | 0.00 | 1.00 | — |
| T5 | không liên quan đoán thành → | 0.06 | 0.08 | 1.00 | R1/R2, R9, R4 |

- Lan truyền rất **cục bộ**: khoảng cách trung bình từ cạnh chèn tới dấu sai xa nhất, tính khi có lan, là 0.04–0.31 cạnh. Gần như mọi dấu sai nằm trên cạnh kề với cạnh chèn, qua R1/R2.
- T4 không bao giờ lan, và luôn để lại dấu vết vì cạnh được thêm vào một cặp có sepset.
- Ở mọi kiểu, độ dày đồ thị (mean degree 3 so với 2) làm lan truyền tăng gần gấp đôi.

## 4. [Post hoc] Điểm mù của định nghĩa Conflict, và một bất đối xứng

**Điểm mù:** định nghĩa đã khóa chỉ bắt hai loại mâu thuẫn: collider bị **đuôi** chèn chặn, và cạnh bị thêm vào cặp có sepset. T3 chỉ chèn mũi tên, nên theo cấu trúc không bao giờ có Conflict. Còn "override" không bao giờ kích hoạt, vì các luật của causal-learn chỉ đổi dấu tròn. Vì thế "SILENT" ở RB3 bị thổi phồng.

**Phép kiểm bổ sung:** guess có mâu thuẫn với một dấu mà PAG không có tri thức nền đã định hướng hay không. Đây là phép kiểm hiển nhiên mà người dùng có thể làm: chạy FCI không BK, so với guess.

| Kiểu | Guess mâu thuẫn dấu do dữ liệu định hướng | Trong các lần có lan: phát hiện được bởi ít nhất một phép kiểm |
|---|---|---|
| T1 đảo chiều | 73% | 84% |
| **T2 ↔ thành →** | 59% | **99%** |
| **T3 → thành ↔** | 21% | **40%** (60% im lặng thật) |
| T5 | 0% | 100% (do cạnh thêm) |

Tính lại theo phép kiểm đầy đủ, tỉ lệ im lặng gộp của T2 và T3 khoảng 47%, sát ngưỡng 0.5 của RB3. Con số này là post hoc, **không** thay phán quyết đã khóa; nó cho thấy phán quyết SILENT không đáng tin.

**Bất đối xứng** [Verified-run cho số liệu; giải thích là Inference]:
- **T2**, kiểu lỗi mà H-type dự đoán LLM hay mắc (nói "A gây B" ở cặp chỉ bị confound), ít khi lan, và khi lan thì gần như **luôn bị dữ liệu bắt** (99%). Lý do khả dĩ: một đuôi tại A trên cặp ↔ thường xung đột với collider mà dữ liệu đã thấy.
- **T3**, kiểu lỗi ngược lại (nói "có nguyên nhân chung ẩn" ở cặp thật ra có quan hệ trực tiếp), lan nhiều hơn và **phần lớn im lặng**. Mũi tên chèn vào chỉ thêm ràng buộc "không phải tổ tiên", không chặn được luật nào, nên không để lại dấu vết.
- [Hypothesis, quan trọng cho P-A]: nếu thiết kế hỏi LLM theo kiểu tương thích MAG (Q-PAIR, cho phép trả lời "confounded") đẩy LLM sang **phòng thủ bằng cách nói "confounded"**, nó có thể đổi một lỗi dễ phát hiện (T2) thành một lỗi im lặng (T3). Như vậy "hỏi đúng hơn" có thể an toàn **kém** hơn. P-A đo được trực tiếp điều này qua Conf_D (RA4).

## 5. Ý nghĩa cho quyết định hướng

- **Theo bảng §5 của luật đọc:** P-B = NO LATENT-SPECIFIC HARM.
  - Nếu P-A cho **H-TYPE CONFIRMED**: phần phương pháp NO-GO ở mức oracle; P-A đứng riêng thành một phát hiện; trước khi đóng phải chạy P-B với CI mẫu hữu hạn (n = 500, 100 đồ thị).
  - Nếu P-A cho **NOT CONFIRMED**: đóng hướng.
- **Trả lời câu hỏi của mentor ở mức oracle:** về **cơ chế lan truyền trong FCI**, biến ẩn không làm một guess sai nguy hiểm hơn. Lỗi nguy hiểm nhất vẫn là đảo chiều, giống như dưới causal sufficiency. Lập luận (c) trong phân tích ngày 12/11 ("luật định hướng của FCI lan lỗi theo cách khác PC") **không được dữ liệu ủng hộ** về độ lớn.
- **Điều còn mở:**
  - Tổng tác hại trong thực tế = tần suất từng kiểu lỗi của LLM × tác hại mỗi kiểu. P-B chỉ đo vế sau; P-A đo vế trước.
  - Bất đối xứng T2/T3 về tính phát hiện được là phát hiện đáng giữ. Nó có cùng dạng câu hỏi "vì sao chỉ một số guess sai gây hại" như một tài liệu tham khảo nội bộ, nhưng chưa đủ làm trụ một bài.

## 6. Giới hạn

- Oracle CI: không có sai số thống kê. Ở mẫu hữu hạn, lỗi CI có thể che hoặc khuếch đại lỗi do guess.
- Mỗi lần chỉ một guess sai. LLM thật đưa ra cả một DAG với nhiều lỗi cùng lúc, có thể tương tác.
- Hard BK theo ngữ nghĩa Tetrad. Soft BK chưa được đo.
- bnlearn: 13 đơn vị, 6 timeout loại khỏi đối chiếu; phân bố theo mạng không cân.
- Định nghĩa Conflict có điểm mù như §4.
