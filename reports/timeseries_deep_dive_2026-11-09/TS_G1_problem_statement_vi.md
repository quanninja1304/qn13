# Phát biểu bài toán TS-G1: causal discovery chuỗi thời gian dưới confounding ẩn có tự tương quan, kiểm trên dữ liệu thật

> 09/11/2026. Viết **trước** pilot. Mọi điều nói về kết quả đều là [Hypothesis], cho tới khi luật đọc ([`TS_G1_reading_rules_vi.md`](TS_G1_reading_rules_vi.md)) được duyệt và pilot chạy xong.
> Nhãn: [Verified], [Verified-code], [Verified-search], [Inference], [Hypothesis].

## 1. Bối cảnh trong một đoạn

Causal discovery trên chuỗi thời gian dựa vào hai điều:
- **thứ tự thời gian**, để định hướng link trễ;
- **causal sufficiency**, tức không có confounder ẩn.

Trong hệ thật (thủy văn, khí hậu, tài chính), confounder ẩn thường là một **quá trình**, không phải một biến tĩnh. Mưa, nhiệt độ hay nhân tố thị trường đều có tự tương quan và phủ không gian rộng. Khi đó link giả xuất hiện **ở mọi độ trễ**, và thứ tự thời gian không còn bảo vệ được.

Các phương pháp tính đến biến ẩn (LPCMCI, SVAR-FCI, TS-ICD) đã có lý thuyết, nhưng **chưa có đánh giá trên dữ liệu thật có căn cứ** [Verified-fetch: Butler et al. 2026 §VI; Verified: CausalDynamics; Verified-search: reviewer của LPCMCI]. Benchmark thật duy nhất có tập "Confounder", tức CausalRivers (ICLR 2025), thực ra **không che confounder** trong code công khai [Verified-code].

## 2. Mô hình

### 2.1 Quá trình

- Chỉ số thời gian t ∈ ℤ, lưới lấy mẫu Δ (pilot dùng Δ = 6 giờ).
- **Quan sát:** X_t = (X_t^1, …, X_t^p) là lưu lượng tại p trạm đo.
- **Ẩn:** L_t ∈ ℝ^q là trường khí tượng (mưa, cùng các thành phần khác như tuyết tan và nhiệt độ), có tự tương quan và tương quan không gian.
- **Proxy quan sát được của L:** R_t = h(L_t) + ε_t, là mưa đo tại các trạm DWD. Đây là phép đo điểm và có nhiễu, nên **R_t ≠ L_t**.

Giả định mô hình cấu trúc dừng nhân quả (causal stationarity) trên window graph với độ trễ tối đa τ_max:

```
X_t^i = f_i( {X_{t-τ}^j : (j,τ) ∈ Pa_X(i)},  {L_{t-τ}^k : (k,τ) ∈ Pa_L(i)},  η_t^i )
L_t   = g( L_{t-1}, …, L_{t-τ_max}, ξ_t )        (L ngoại sinh: không X nào gây ra L)
```

Nhiễu η và ξ độc lập, không có selection bias.

### 2.2 Ground truth có thể kiểm chứng

- **Topology G\*** trên p trạm đo: i → j trong G\* khi nước chảy từ i tới j. Đây là graph do CausalRivers dựng bán tự động rồi kiểm tay [Verified, §3.1 của bài].
- **Cặp không nối nhau:** (i, j) thỏa (a) không có đường có hướng giữa i và j theo cả hai chiều trong G\*, và (b) **không có tổ tiên chung** trong G\*.

  Với các cặp này, theo topology, mọi phụ thuộc thống kê giữa X^i và X^j **chỉ có thể đi qua L** (hoặc qua lỗi dựng graph, xem §6).

  **Nhận định quan trọng** [Inference]: sông gần như chỉ hợp lưu chứ ít khi tách nhánh. Vì vậy nhóm các cặp không nối nhau rất lớn, và không có confounder **quan sát được** nào giữa chúng. Đó là lý do lưu vực sông là một **phòng thí nghiệm tự nhiên cho confounding ẩn**: ta biết chắc chắn những cặp nào *không* có quan hệ nhân quả.

### 2.3 Đối tượng cần học

Chỉ từ X (không có R), đối tượng đúng là **window PAG** P(X), tức lớp tương đương Markov của MAG thu được khi lấy biên của window DAG trên (X, L) [Inference từ lý thuyết của LPCMCI].

Các claim của một thuật toán được chia ba loại:
- **Claim tổ tiên** i ⇝ j (dấu `-->` có đuôi ở i): khẳng định "i là nguyên nhân của j".
- **Claim không tổ tiên** (đầu mũi tên ở i): khẳng định "i không phải nguyên nhân của j".
- **Kề hoặc không kề.**

## 3. Bài toán

### 3.1 Bài toán đo lường (pilot, dữ liệu trước)

Gọi \(\mathcal{D}\) là tập cặp không nối nhau. Với mỗi cặp, đặt s(i, j) ∈ [0, 1] là **mức chung confounder**. Trong pilot, s được xấp xỉ bằng khoảng cách: gần thì chung mưa, xa thì không.

Với một thuật toán A, định nghĩa:

- **Tỉ lệ claim nhân quả sai:** FCR_A(s) = Pr[A cho claim tổ tiên i ⇝ j hoặc j ⇝ i | (i, j) ∈ 𝒟, mức chung s].
- **Recall trên cạnh thật:** Rec_A = Pr[A có cạnh không ngược hướng với i → j | i → j ∈ G\*].

Ba giả thuyết cần kiểm (tương ứng R1–R3 trong luật đọc):

- **H1, có failure:** FCR tăng theo s với các phương pháp giả định sufficiency (VAR-Granger, PCMCI+).
- **H2, nguồn của failure:** thêm proxy R làm FCR giảm. Như vậy ít nhất một phần failure đến từ mưa.
- **H3, prior art có giải được không:** LPCMCI hạ FCR về gần mức ở s thấp mà **không** mất nhiều recall và vẫn chạy được ở cỡ thật.

Nếu H1 sai thì không có bài toán. Nếu H1 đúng và H3 đúng thì chỉ còn một phát hiện về *đánh giá* (vùng X31), chưa có bài toán phương pháp.

### 3.2 Bài toán phương pháp (chỉ đặt ra nếu pilot cho GAP-A hoặc GAP-B)

**Đầu vào:**
- X_{1:T};
- tùy chọn: proxy R_{1:T} của một phần L, kèm tri thức nền rằng R ngoại sinh;
- tùy chọn: thứ tự hoặc ràng buộc topology một phần.

**Đầu ra:** một window graph có ngữ nghĩa PAG, hoặc một tập claim tổ tiên và claim không tổ tiên.

**Mục tiêu:**
1. **Kiểm soát lỗi:** FCR trên 𝒟 không phụ thuộc s, tức FCR(s cao) ≈ FCR(s thấp) ≤ α_target.
2. **Giữ thông tin:** Rec trên cạnh thật không thấp hơn đáng kể so với PCMCI+, nghĩa là không trả giá bằng cách "không nói gì".
3. **Khả thi:** chạy được với p cỡ hàng chục và T cỡ hàng nghìn đến hàng chục nghìn, trên máy 7.8 GB RAM.

**Vì sao khó** [Inference]:
- **Confounder có tự tương quan và phủ không gian:** cùng một L tác động lên nhiều trạm ở nhiều độ trễ, nên link giả có thể vừa trễ vừa tức thời.
- **Lấy mẫu thô (Δ = 6 giờ) so với thời gian truyền nước:** sinh link tức thời; phần định hướng không còn "miễn phí" từ thứ tự thời gian.
- **Không dừng theo sự kiện:** mưa xuất hiện đột ngột, trễ phụ thuộc lưu lượng [Verified, CausalRivers §3.2]. Test CI tuyến tính (ParCorr) có thể sai mô hình.
- **Proxy không hoàn hảo:** chỉ đưa R vào như một biến quan sát (điều kiện O) vẫn để lại confounding dư. Bỏ hẳn R (điều kiện L) thì phí thông tin. Cả hai cách đều không đúng về nguyên tắc.

### 3.3 Hướng cơ chế tiềm năng (chỉ là giả thuyết, CHƯA audit)

Hai hướng sau chỉ được xét **sau** khi pilot cho GAP-A hoặc GAP-B. Cả hai đều cần audit prior art trước.

- **(M1) Discovery có biến ẩn với proxy nhiễu của confounder.** Dùng R như proxy của L trong kiểm định CI và trong quy tắc định hướng, thay vì coi R là L hoặc bỏ R. Prior art cần kiểm:
  - proxy cho subsampling (Liu et al., NeurIPS 2023);
  - proxy trong ước lượng hiệu ứng (Miao, Geng, Tchetgen Tchetgen 2018);
  - discovery dưới lỗi đo (Zhang et al. 2017).
- **(M2) Tận dụng tri thức nền "ngoại sinh cộng không gian":** mưa ngoại sinh, và mức chung confounder giảm theo khoảng cách, để thu hẹp lớp PAG.

**Không** đi theo hướng "chứng nhận claim tổ tiên bằng thống kê tin cậy", vì đó là A′/R1 đã đóng (X12–X22), trừ khi có lý do khoa học mới.

## 4. Đóng góp có thể có (nếu pilot ủng hộ)

1. **Giao thức đánh giá confounding ẩn trên dữ liệu thật**, dựa trên các cặp không nối nhau trong mạng sông, có proxy mưa để lộ một phần confounder. Ghi chú: X31 nói rằng một bài *chỉ* làm kiểm toán benchmark thì không đủ.
2. **Bằng chứng định lượng** rằng confounding do mưa sinh ra claim nhân quả sai đo được, và phương pháp có biến ẩn hiện có xử lý nó tới đâu.
3. **Một cơ chế** (M1 hoặc M2) giải quyết phần còn lại, nếu prior art chưa có.

## 5. Tiêu chí go/no-go

| Cổng | Điều kiện | Nếu không đạt |
|---|---|---|
| G0 | R0 (đủ đơn vị dữ liệu) | Dừng, báo cáo dữ liệu không đủ |
| G1 | H1 / R1 | **NO-GO** cho TS-G1 |
| G2 | H3 sai, tức có GAP-A hoặc GAP-B | Nếu H3 đúng: dừng ở mức phát hiện đánh giá, chuyển sang TS-G2 hoặc hướng khác |
| G3 | Audit prior art cho M1/M2 cho thấy còn chỗ trống | Dừng phần phương pháp |

## 6. Nguy cơ đe dọa tính đúng

- **Lỗi dựng topology:** kênh nhân tạo, trạm bơm, tách nhánh không được ghi nhận. Khi đó một cặp "không nối nhau" thật ra lại có nối. Hướng kiểm tra: dùng cột `origin` và cột chất lượng của cạnh, và báo cáo kết quả khi bỏ các cạnh có chất lượng thấp.
- **Confounder khác mưa:** tuyết tan, điều tiết hồ chứa, nhiệt độ. H2 chỉ tách được phần do mưa.
- **Khoảng cách chỉ là proxy của s:** nó tương quan với địa hình và khí hậu vùng.
- **Một benchmark, một vùng:** muốn tổng quát hơn có thể thêm RiversBavaria, cũng như các miền khác có cấu trúc mạng tương tự (hệ thống điện, giao thông).
