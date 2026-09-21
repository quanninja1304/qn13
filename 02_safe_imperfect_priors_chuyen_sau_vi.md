# Đề cương chuyên sâu: Tận dụng an toàn tri thức không hoàn hảo trong khám phá nhân quả có nhiễu ẩn

**Tên tiếng Anh để tra cứu:** Safe Imperfect Priors for Latent-Confounded Causal Discovery  
**Mục tiêu tài liệu:** Làm rõ mô hình toán, giả định, thiết kế thuật toán, thí nghiệm, rủi ro và tiêu chuẩn đầu ra  
**Phạm vi khuyến nghị:** Khám phá cấu trúc dựa trên kiểm định độc lập có điều kiện; đầu ra là PAG; dữ liệu quan sát có biến ẩn

## 1. Luận điểm nghiên cứu

Tri thức chuyên gia hoặc mô hình ngôn ngữ không nên được coi là bằng chứng để thêm, xóa hoặc định hướng cạnh. Nó nên được coi là **tín hiệu điều khiển tìm kiếm**: quyết định kiểm định nào nên chạy trước, tập điều kiện nào nên thử trước, và vùng nào của không gian đồ thị đáng dành ngân sách.

Đề tài cần chứng minh hoặc cung cấp bằng chứng mạnh cho hai phát biểu tách biệt:

1. **Chế độ đầy đủ:** nếu cuối cùng mọi kiểm định cần thiết vẫn được thực hiện, lời khuyên chỉ thay đổi lịch tìm kiếm và không làm thay đổi đích tiệm cận của thuật toán cơ sở.
2. **Chế độ giới hạn ngân sách:** khi không thể chạy hết, phương pháp dùng lời khuyên tạo đường cong chất lượng–chi phí tốt hơn nhưng vẫn trả về kết luận thận trọng và chỉ rõ phần chưa được kiểm chứng.

Không nên gộp hai phát biểu này thành một tuyên bố no-harm chung. Chế độ thứ hai khó có bảo đảm không gây hại cho mọi loại lời khuyên.

## 2. Bối cảnh hình thức

### 2.1. Hệ sinh dữ liệu

Giả sử có tập biến quan sát (X=\{X_1,\ldots,X_p\}), biến ẩn (L), và có thể có biến chọn mẫu (S). Hệ thống đầy đủ được biểu diễn bởi một DAG (G^+\) trên (X\cup L\cup S).

Sau khi lấy biên trên các biến ẩn và điều kiện hóa theo chọn mẫu, quan hệ giữa các biến quan sát có thể được biểu diễn bởi một **đồ thị tổ tiên cực đại** (M) (MAG). Từ các quan hệ độc lập có điều kiện trên dữ liệu quan sát, ta thường chỉ nhận dạng được lớp tương đương Markov của (M), được biểu diễn bởi PAG (P^\star).

Các dấu đầu cạnh trong PAG có ý nghĩa:

- đuôi (X_i -\!* X_j): (X_i) là tổ tiên của (X_j) trong mọi MAG phù hợp;
- đầu mũi tên (X_i \leftarrow\!* X_j): (X_i) không là tổ tiên của (X_j);
- vòng tròn (X_i \circ\!\!* X_j): dấu đầu cạnh chưa được xác định từ dữ liệu và giả định.

Đầu ra khoa học đúng là (P^\star) hoặc một đối tượng thận trọng chứa (P^\star), không nhất thiết là DAG.

### 2.2. Kiểm định độc lập có điều kiện

Thuật toán FCI truy vấn một bộ kiểm định:

\[
\phi_n(i,j,Z) \in \{\text{phụ thuộc},\text{độc lập}\},
\]

với câu hỏi (X_i \perp X_j\mid X_Z). Trong lý tưởng oracle, các câu trả lời hoàn toàn đúng. Ở mẫu hữu hạn, chúng phụ thuộc mức ý nghĩa, loại dữ liệu, kích thước tập điều kiện và độ mạnh tín hiệu.

Sai số một kiểm định có thể lan truyền:

- xóa nhầm cạnh làm mất đường đi cần thiết;
- giữ nhầm cạnh làm tăng không gian Possible-D-SEP;
- chọn sai tập phân tách làm định hướng collider sai;
- định hướng sai tiếp tục lan qua các quy tắc của FCI.

Do đó, “thứ tự kiểm định” không vô nghĩa ở mẫu hữu hạn hoặc dưới ngân sách giới hạn, dù ở mức oracle một hoán vị đầy đủ có thể cho cùng đích.

### 2.3. Biểu diễn tri thức không hoàn hảo

Ký hiệu tri thức ngoài dữ liệu là (K). Không nên giới hạn (K) vào dự đoán hướng cạnh. Có thể phân thành:

| Loại tri thức | Ví dụ | Cách dùng an toàn hơn |
|---|---|---|
| Thứ tự thời gian | Điều trị xảy ra trước kết quả | Ưu tiên/loại bỏ một số truy vấn rõ ràng; chỉ dùng làm ràng buộc nếu nguồn thực sự đáng tin |
| Nhóm hoặc tầng | Nhân khẩu học, hành vi, kết quả | Ưu tiên đường đi và tập điều kiện |
| Khả năng liên hệ | Hai biến có thể liên quan | Ưu tiên kiểm tra cạnh kề |
| Ứng viên tập phân tách | Nhóm (Z) có thể chặn đường đi | Xếp thứ tự các tập điều kiện |
| Khả năng có nhiễu ẩn | Hai biến có nguyên nhân chung | Ưu tiên kiểm tra mô-típ/path; không tự thêm cạnh hai đầu mũi tên |
| Hướng cạnh | (X_i\to X_j) | Chỉ dùng như tín hiệu tìm kiếm; không trực tiếp định hướng PAG |

Một giao diện tổng quát là bộ chấm điểm:

\[
s_K(q\mid c)\in\mathbb{R},
\]

trong đó (q) là một hành động tìm kiếm, chẳng hạn kiểm định ((i,j,Z)), và (c) là trạng thái PAG hiện tại, lịch sử kiểm định và mô tả biến.

Thuật toán chọn truy vấn có điểm cao trước, nhưng câu trả lời cho truy vấn vẫn đến từ dữ liệu.

## 3. Khoảng trống so với công trình gần nhất

### 3.1. Guess2Graph

[Guess2Graph](https://arxiv.org/abs/2510.14488) dùng lời đoán để hướng dẫn thứ tự kiểm định trong PC và giữ tính nhất quán bất kể lỗi chuyên gia. Đây là tiền lệ trực tiếp nhất. Nhưng PC nhắm tới CPDAG dưới giả định đủ nguyên nhân; FCI phải xử lý MAG/PAG, Possible-D-SEP và các quy tắc định hướng phức tạp hơn.

Đề tài chỉ có novelty nếu phần mở rộng sang FCI tạo ra vấn đề mới thực sự, ví dụ:

- lời khuyên cấp đường đi thay vì cấp cạnh;
- Possible-D-SEP có kích thước lớn;
- phân biệt cạnh trực tiếp và liên hệ do nhiễu ẩn;
- kiểm soát dấu đầu cạnh;
- lời khuyên sai có tương quan trong một vùng đồ thị;
- đầu ra anytime thận trọng dưới ngân sách.

### 3.2. Learning to Defer

[L2D-CD](https://arxiv.org/abs/2502.13132) học hàm lựa chọn giữa chuyên gia và thuật toán dữ liệu trên bài toán nhân quả từng cặp. Nó chưa giải quyết sự phụ thuộc toàn cục giữa các quyết định cạnh trong PAG. Đề tài hiện tại không chỉ chọn “tin ai”, mà sử dụng lời khuyên để tổ chức chuỗi kiểm định phụ thuộc lẫn nhau.

### 3.3. tFCI và tri thức phân tầng

[tFCI](https://arxiv.org/abs/2503.21526) cho thấy tri thức tầng đúng có thể làm FCI hiệu quả và cung cấp nhiều thông tin hơn. Điểm khác biệt cần giữ là tri thức của ta có thể sai, không đầy đủ và không đồng nhất theo vùng.

### 3.4. Các phương pháp sửa lỗi hoặc ràng buộc mềm

[dcFCI](https://arxiv.org/abs/2505.06542) tìm kiếm và xếp hạng các PAG tương thích dữ liệu để xử lý tính không trung thành thực nghiệm và dữ liệu hỗn hợp. Các phương pháp ràng buộc cấu trúc mềm hoặc lan truyền cạnh tin cậy xử lý một phần lỗi tri thức, nhưng thường cho phép tri thức tham gia trực tiếp vào mục tiêu hoặc định hướng. Đề tài này ưu tiên nguyên tắc **không quyết định thay dữ liệu**.

### 3.5. Bằng chứng phản biện về mô hình ngôn ngữ

[Wu et al.](https://arxiv.org/abs/2506.00844) đưa ra bằng chứng rằng prompt có thể làm phóng đại năng lực và đề xuất giới hạn mô hình ngôn ngữ ở vai trò hỗ trợ không quyết định. Điều này không bác bỏ đề tài; nó chính là lý do thiết kế phải tách “lời khuyên” khỏi “bằng chứng”.

## 4. Phạm vi và đối tượng đầu ra

### 4.1. Phạm vi nên chọn

- Dữ liệu i.i.d. quan sát.
- Có biến gây nhiễu ẩn; tạm thời không xử lý chuỗi thời gian.
- Không có hoặc cố định cơ chế chọn mẫu trong phiên bản đầu.
- Số biến quan sát ban đầu (p\in\{10,20,50\}).
- FCI hoặc RFCI làm thuật toán cơ sở.
- Tri thức dùng để lập lịch, không trực tiếp thay đổi kết quả kiểm định.

### 4.2. Đối tượng trả về

Mỗi lần chạy nên trả về bộ bốn:

\[
(P,\;\mathcal{T},\;\mathcal{U},\;B),
\]

trong đó:

- (P): PAG hiện tại;
- (\mathcal{T}): nhật ký kiểm định đã chạy và kết quả;
- (\mathcal{U}): truy vấn hoặc vùng đồ thị chưa kiểm tra;
- (B): ngân sách đã sử dụng.

Điều này tránh việc chỉ trả một đồ thị trông hoàn chỉnh nhưng che giấu các bước chưa được xác nhận.

## 5. Các câu hỏi nghiên cứu và tiêu chuẩn trả lời

### RQ1. Lập lịch có giữ tính đúng đắn trong chế độ đầy đủ không?

**Mục tiêu:** chứng minh thuật toán đề xuất thực hiện cùng họ truy vấn cần thiết và áp dụng cùng quy tắc hợp lệ như FCI/RFCI.

**Kết quả mong muốn:** dưới oracle CI, tính Markov và faithfulness phù hợp, lịch tìm kiếm chỉ là hoán vị hợp lệ nên đầu ra bằng thuật toán cơ sở. Với kiểm định CI nhất quán, đầu ra nhất quán tiệm cận.

**Điểm cần thận trọng:** FCI có các bước mà kết quả trung gian quyết định không gian tìm kiếm sau đó. Không được giả định mọi hoán vị đều hợp lệ. Cần định nghĩa scheduler tôn trọng quan hệ phụ thuộc giữa truy vấn.

### RQ2. Lời khuyên tốt ở mức nào thì tạo lợi ích?

Không nên định nghĩa “độ chính xác expert” chỉ bằng tỷ lệ hướng cạnh đúng. Một điều kiện phù hợp hơn là **lợi thế xếp hạng**:

\[
\Pr\big(s_K(q^+) > s_K(q^-)\big) \geq \tfrac12 + \gamma,
\]

trong đó (q^+) là truy vấn hữu ích sớm cho việc tìm tập phân tách hoặc xác định cấu trúc, còn (q^-) là truy vấn kém hữu ích. (\gamma>0) đo mức lời khuyên tốt hơn ngẫu nhiên.

**Kết quả mong muốn:** số truy vấn hoặc chi phí trung bình giảm theo (\gamma), ít nhất trên một lớp đồ thị giới hạn.

### RQ3. Làm thế nào mô hình hóa lỗi tương quan?

Các bộ sinh lỗi cần bao gồm:

1. **Lỗi độc lập:** lật từng lời khuyên với xác suất (\epsilon).
2. **Lỗi theo nút:** mọi quan hệ liên quan đến một nút đều dễ sai.
3. **Lỗi theo mô-típ:** nhầm nguyên nhân chung thành chuỗi nhân quả.
4. **Lỗi theo miền:** chuyên gia giỏi trong nhóm biến A nhưng kém trong B.
5. **Lỗi vị trí ngôn ngữ:** đổi thứ tự tên biến làm đổi câu trả lời.
6. **Lỗi đối nghịch:** lời khuyên cố tình ưu tiên truy vấn kém hữu ích.

### RQ4. Đầu ra dưới ngân sách nên có bảo đảm gì?

Ba phương án từ dễ đến khó:

- **Phương án A:** chỉ báo cáo risk–budget curve, không tuyên bố no-harm.
- **Phương án B:** giữ các dấu đầu cạnh chưa chứng minh ở dạng vòng tròn; chỉ định hướng khi có chứng cứ FCI hợp lệ.
- **Phương án C:** xây confidence sequence hoặc kiểm soát lỗi đồng thời cho các kiểm định thích nghi, từ đó đưa ra bảo đảm xác suất cho PAG thận trọng.

Khuyến nghị project 6–7 tháng: hoàn thành A và B; coi C là mục tiêu mở rộng.

## 6. Kiến trúc thuật toán đề xuất

### 6.1. Mô-đun 1 — Chuẩn hóa lời khuyên

Đưa mọi nguồn tri thức về các bản ghi:

| Trường | Ý nghĩa |
|---|---|
| `scope` | cạnh, nút, đường đi, tầng hoặc nhóm |
| `claim` | nội dung lời khuyên |
| `source` | oracle nhiễu, chuyên gia, mô hình ngôn ngữ |
| `confidence_raw` | độ tự tin thô, không coi là xác suất |
| `context` | prompt, mô tả biến, phiên bản mô hình |
| `provenance` | nguồn và thời điểm tạo |

### 6.2. Mô-đun 2 — Bộ chấm điểm truy vấn

Điểm của một kiểm định có thể gồm:

\[
s(q)=\alpha s_{\text{prior}}(q)+\beta s_{\text{graph}}(q)+
\eta s_{\text{cost}}(q)+\delta s_{\text{uncertainty}}(q).
\]

Trong đó:

- (s_{\text{prior}}): mức phù hợp với lời khuyên;
- (s_{\text{graph}}): khả năng ảnh hưởng đến nhiều quyết định PAG;
- (s_{\text{cost}}): ưu tiên tập điều kiện nhỏ/rẻ;
- (s_{\text{uncertainty}}): ưu tiên vùng chưa chắc chắn.

Phiên bản đầu nên dùng công thức minh bạch, không dùng mạng học sâu. Một mô hình học-to-rank có thể là mở rộng sau.

### 6.3. Mô-đun 3 — Bộ lập lịch có ràng buộc phụ thuộc

Bộ lập lịch duy trì hàng đợi ưu tiên nhưng chỉ mở một truy vấn khi các tiền đề của nó đã hoàn thành. Ví dụ, chỉ tìm Possible-D-SEP sau khi đã có skeleton sơ bộ.

Quy trình khái quát:

1. Khởi tạo đồ thị đầy đủ.
2. Sinh các kiểm định hợp lệ ở mức điều kiện hiện tại.
3. Chấm điểm và sắp thứ tự.
4. Chạy kiểm định; cập nhật skeleton và separating sets.
5. Khi đủ tiền đề, mở các truy vấn Possible-D-SEP.
6. Áp dụng quy tắc định hướng chuẩn của FCI.
7. Không dùng lời khuyên để viết dấu cạnh.
8. Dừng khi hết truy vấn hoặc hết ngân sách.

### 6.4. Mô-đun 4 — Nhật ký chứng cứ

Mỗi cạnh/dấu cạnh cần truy ngược được:

- kiểm định nào đã xóa cạnh;
- separating set nào được sử dụng;
- quy tắc FCI nào định hướng dấu;
- lời khuyên nào chỉ ảnh hưởng thứ tự;
- truy vấn nào chưa chạy do hết ngân sách.

Đây vừa là tính năng kỹ thuật vừa là công cụ đánh giá tính an toàn.

## 7. Mệnh đề lý thuyết mục tiêu

### Mệnh đề 1 — Tương đương oracle trong chế độ đầy đủ

Một phiên bản hợp lý:

> Nếu bộ lập lịch chỉ hoán vị các truy vấn hợp lệ, không lược bỏ truy vấn cần thiết, tôn trọng quan hệ tiền đề giữa các giai đoạn, và thuật toán sử dụng oracle độc lập có điều kiện, thì đầu ra của phiên bản tăng cường bằng lời khuyên trùng với đầu ra của FCI/RFCI cơ sở.

Đây có thể không phải định lý mới sâu nếu chỉ là hệ quả trực tiếp. Giá trị của nó phụ thuộc việc ta định nghĩa lớp lịch đủ rộng và xử lý đúng các truy vấn thích nghi.

### Mệnh đề 2 — Nhất quán với kiểm định hữu hạn mẫu

Nếu mỗi kiểm định CI nhất quán và xác suất sai đồng thời trên tập truy vấn cần thiết tiến về 0, đầu ra của thuật toán tăng cường hội tụ về PAG thật dưới các giả định của FCI.

### Mệnh đề 3 — Lợi ích dưới lời khuyên có lợi thế xếp hạng

Trên một lớp đồ thị hoặc giai đoạn skeleton đơn giản, chứng minh số truy vấn kỳ vọng để tìm separating set giảm khi (\gamma) tăng. Nếu không chứng minh được cho FCI đầy đủ, có thể chứng minh cho một bài toán con rồi kiểm tra thực nghiệm trên FCI.

### Kết quả âm cũng có giá trị

Nếu tồn tại đồ thị mà mọi scheduler không thể cải thiện worst-case query complexity, một lower bound như vậy giúp định vị đóng góp ở average-case hoặc budgeted setting.

## 8. Thiết kế bộ sinh dữ liệu

### 8.1. Sinh cấu trúc

1. Sinh DAG đầy đủ trên (p+h) nút.
2. Chọn (p) nút quan sát và (h) nút ẩn.
3. Lấy latent projection để thu MAG ground truth.
4. Chuyển MAG sang PAG oracle để đánh giá.

Các trục cần thay đổi:

- (p\in\{10,20,50\});
- tỷ lệ nút ẩn (h/(p+h)\in\{0.1,0.3,0.5\});
- bậc trung bình (\in\{1.5,3,5\});
- số collider và độ dài đường đi;
- mức gần không-faithful.

### 8.2. Sinh cơ chế

- tuyến tính Gaussian;
- tuyến tính phi Gaussian;
- mô hình cộng nhiễu phi tuyến;
- biến rời rạc;
- dữ liệu hỗn hợp nếu dùng dcFCI làm baseline.

### 8.3. Cỡ mẫu


\[
n\in\{200,500,1000,5000\}.
\]

Mục đích không phải tìm một cấu hình thắng, mà vẽ bản đồ khi nào prior giúp hoặc gây hại.

## 9. Sinh và thu thập lời khuyên

### 9.1. Lời khuyên tổng hợp có kiểm soát

Từ ground truth, tạo tín hiệu ở các mức:

- cạnh kề;
- quan hệ tổ tiên;
- cùng tầng;
- ứng viên separating set;
- quan hệ do nguyên nhân chung.

Sau đó áp dụng các cơ chế lỗi ở Mục 5.

### 9.2. Lời khuyên từ mô hình ngôn ngữ

Để tránh leakage:

- tạo tên biến hư cấu hoặc paraphrase nhiều lần;
- không đưa mô tả chứa trực tiếp quan hệ đúng;
- đảo thứ tự biến trong prompt;
- dùng nhiều mẫu prompt cố định trước thí nghiệm;
- ghi phiên bản mô hình và nhiệt độ;
- không dùng cùng benchmark nổi tiếng mà mô hình có thể ghi nhớ;
- tách tập phát triển và tập đánh giá theo generator/mô-típ.

Không nên dùng độ tự tin tự báo cáo làm xác suất. Có thể xây tín hiệu ổn định từ:

- độ nhất quán qua paraphrase;
- độ nhất quán khi đảo vị trí;
- đồng thuận giữa nhiều mẫu;
- đồng thuận giữa nhiều mô hình.

## 10. Baseline bắt buộc

| Nhóm | Baseline |
|---|---|
| Không dùng prior | FCI, RFCI |
| Tri thức đúng | tFCI hoặc FCI với tầng đúng |
| Tri thức cứng sai | FCI với ràng buộc bị lật ở các mức lỗi |
| Lập lịch | Scheduler ngẫu nhiên; oracle scheduler; G2G-inspired scheduler |
| Chọn chuyên gia | L2D-CD ở phần pairwise hoặc biến thể đơn giản |
| Độ bất định cấu trúc | dcFCI nếu tương thích loại dữ liệu |
| LLM trực tiếp | Dự đoán cạnh/hướng rồi ép vào graph, dùng như negative baseline |

Nếu không tái lập được baseline gần nhất một cách công bằng, không nên tuyên bố cải tiến.

## 11. Thước đo

### 11.1. Chất lượng PAG

- precision/recall/F1 của adjacency;
- precision/recall của dấu đuôi, mũi tên và vòng tròn;
- số định hướng sai chắc chắn;
- lỗi quan hệ tổ tiên;
- khoảng cách PAG phù hợp nếu có implementation đáng tin cậy;
- tỷ lệ PAG chứa MAG thật hoặc tương thích với các CI oracle.

### 11.2. Hiệu quả tìm kiếm

- tổng số CI tests;
- số test theo kích thước conditioning set;
- số Possible-D-SEP candidates;
- thời gian chạy;
- bộ nhớ;
- diện tích dưới đường cong chất lượng–ngân sách.

### 11.3. Độ bền trước prior

- chất lượng theo error rate;
- chất lượng theo correlation strength của lỗi;
- worst-group performance;
- monotonic degradation;
- regret so với FCI không prior và oracle scheduler.

### 11.4. Hiệu chỉnh và từ chối

Nếu hệ thống có module đánh giá độ tin cậy:

- expected calibration error chỉ dùng khi có nhãn xác suất phù hợp;
- precision–coverage của việc chấp nhận lời khuyên;
- false-acceptance rate của lời khuyên nguy hiểm;
- mức cải thiện sau khi bỏ các lời khuyên không ổn định.

## 12. Ma trận thí nghiệm cốt lõi

Không cần chạy tích Descartes đầy đủ ngay. Dùng thiết kế theo giai đoạn:

### Giai đoạn A — Kiểm tra cơ chế

- (p=10,20);
- tuyến tính Gaussian;
- (n=500,1000);
- prior error (0,0.2,0.4,0.5,0.7);
- lỗi độc lập và theo nút;
- 30–50 seed.

### Giai đoạn B — Kiểm tra độ bền

- phi tuyến, rời rạc/hỗn hợp;
- mật độ nhiễu ẩn khác nhau;
- gần vi phạm faithfulness;
- lỗi theo mô-típ và domain.

### Giai đoạn C — Tri thức ngôn ngữ

- tên biến hư cấu và thực tế;
- paraphrase/đảo vị trí;
- ít nhất hai mô hình mở hoặc một mô hình mở và một API;
- đóng băng prompt trước tập test.

## 13. Ablation cần có

1. Chỉ prior score.
2. Chỉ graph-uncertainty score.
3. Chỉ cost score.
4. Prior + cost.
5. Prior + uncertainty.
6. Không module ổn định prompt.
7. Edge-level advice so với path/tier advice.
8. Chế độ đầy đủ so với giới hạn ngân sách.
9. Scheduler học được so với công thức minh bạch.
10. Có và không có nhật ký/chứng nhận không ảnh hưởng accuracy nhưng kiểm tra khả năng truy vết.

## 14. Phân tích thống kê

- Báo cáo trung bình và khoảng tin cậy theo graph seed, không coi mọi cạnh là mẫu độc lập.
- Dùng paired comparisons trên cùng graph/data seed.
- Báo cáo effect size, không chỉ p-value.
- Tách kết quả theo mật độ nhiễu ẩn và conditioning-set size.
- Đăng ký trước primary metrics và primary comparison để tránh chọn kết quả có lợi.
- Khi có nhiều cấu hình, dùng hierarchical model hoặc correction phù hợp cho multiple comparisons.

## 15. Stop conditions

### NO-GO sớm

- Oracle scheduler không cải thiện đáng kể đường cong chất lượng–chi phí so với lịch chuẩn.
- Phần mở rộng FCI chỉ thay đổi thứ tự một vòng lặp và không tạo câu hỏi PAG mới.
- Kết quả chỉ tốt khi dùng edge accuracy của expert, nhưng không tốt dưới lỗi tương quan.
- LLM advice mất toàn bộ tín hiệu khi dùng tên biến hư cấu và prompt chống leakage.
- Hard-prior baseline tốt tương đương ở mọi mức lỗi thực tế.

### GO

- Có lợi ích ổn định dưới ít nhất hai kiểu cơ chế dữ liệu và nhiều seed.
- Degradation theo prior quality có thể giải thích và không đột ngột.
- PAG endpoint validity được cải thiện hoặc giữ nguyên ở cùng ngân sách.
- Có formal statement không tầm thường về scheduler hoặc anytime output.
- Code có thể tái lập trên máy thông thường.

## 16. Rủi ro và cách giảm thiểu

| Rủi ro | Cách giảm thiểu |
|---|---|
| Novelty bị Guess2Graph đóng | Tập trung vào PAG, Possible-D-SEP, lỗi tương quan và anytime certificate |
| Lời khuyên LLM không có tín hiệu | Đặt controlled prior là đối tượng khoa học chính; LLM chỉ là case study |
| FCI quá chậm | Bắt đầu RFCI, giới hạn (p\leq50), profile theo giai đoạn |
| CI tests không ổn định | Dùng oracle-CI experiments tách lỗi thuật toán khỏi lỗi thống kê |
| Metrics PAG thiếu chuẩn | Báo cáo endpoint và ancestral metrics, kiểm thử evaluator trên graph nhỏ |
| Tuyên bố no-harm quá mức | Tách chế độ đầy đủ và budgeted; ghi rõ điều kiện |
| Dữ liệu thực không có ground truth | Chỉ dùng làm minh họa, không dùng để xác nhận accuracy |

## 17. Kế hoạch kỹ thuật và cấu trúc kho mã

```text
project/
├── configs/
│   ├── graphs/
│   ├── priors/
│   └── experiments/
├── src/
│   ├── graphs/          # DAG, MAG, PAG và latent projection
│   ├── data/            # cơ chế sinh dữ liệu
│   ├── ci_tests/        # oracle và kiểm định mẫu hữu hạn
│   ├── priors/          # bộ sinh lời khuyên và bộ mã hóa
│   ├── schedulers/      # các chiến lược lập lịch
│   ├── discovery/       # FCI/RFCI wrapper
│   ├── provenance/      # nhật ký bằng chứng
│   └── metrics/
├── experiments/
│   ├── kill_test/
│   ├── synthetic/
│   ├── robustness/
│   └── llm_case_study/
├── tests/
└── reports/
```

Yêu cầu tái lập:

- cấu hình bất biến;
- seed cho graph, data, prior và model riêng biệt;
- lưu toàn bộ CI query log;
- lưu prompt và raw response khi dùng mô hình ngôn ngữ;
- xuất kết quả dạng bảng máy đọc được;
- kiểm tra hai lần chạy cùng cấu hình cho kết quả giống nhau khi có thể.

## 18. Mốc công việc chi tiết

### Tuần 1–2

- Đọc FCI/PAG và công trình gần nhất.
- Chọn thư viện causal discovery.
- Kiểm thử chuyển DAG có biến ẩn sang MAG/PAG.

### Tuần 3–4

- Tái lập FCI/RFCI.
- Xây oracle CI và synthetic prior.
- Chạy kill test scheduler.

### Tuần 5–8

- Xây scheduler có ràng buộc phụ thuộc.
- Thêm budget và evidence log.
- So sánh random/oracle/noisy scheduler.

### Tháng 3–4

- Mô hình hóa lỗi tương quan.
- Viết formal statement và proof.
- Chạy experiment Giai đoạn A.

### Tháng 5

- Giai đoạn B; ablation; kiểm tra evaluator.
- Quyết định có thêm LLM hay không.

### Tháng 6

- LLM case study, anti-leakage protocol.
- Viết paper draft và reproducibility package.

### Tháng 7

- Stress test; phản biện nội bộ; hoàn thiện artifact.

## 19. Đầu ra kỳ vọng theo mức thành công

### Mức tối thiểu có giá trị

- Một benchmark lỗi prior tương quan cho PAG discovery.
- Kết quả âm rõ ràng về khi test ordering không giúp.
- Bộ đánh giá endpoint/ancestral validity có thể tái lập.

### Mức paper tốt

- Scheduler mới cho FCI/RFCI.
- Tương đương oracle/nhất quán ở chế độ đầy đủ.
- Lợi ích hữu hạn mẫu hoặc ngân sách ổn định.
- LLM case study không leakage.

### Mức paper rất mạnh

- Một bảo đảm anytime hoặc finite-sample không tầm thường.
- Điều kiện lợi thế xếp hạng giải thích chính xác khi prior giúp.
- Thực nghiệm cho thấy quy luật này chuyển qua nhiều cơ chế và nguồn prior.

## 20. Tiêu chí đóng góp khoa học

Paper không nên được định vị là “LLM cải thiện causal discovery”. Định vị mạnh hơn là:

> Một khuôn khổ học tăng cường cho khám phá lớp tương đương nhân quả dưới nhiễu ẩn, trong đó tri thức có thể sai chỉ điều khiển tìm kiếm, còn mọi kết luận cấu trúc đều có nguồn gốc từ kiểm định và quy tắc hợp lệ.

Đóng góp tổng quát là nguyên tắc tách **prior dùng để phân bổ tính toán** khỏi **evidence dùng để kết luận nhân quả**.

## 21. Danh mục đọc có thứ tự

### Nền tảng

- Richardson & Spirtes về ancestral graph/MAG.
- Zhang về tính đầy đủ của các quy tắc định hướng FCI.
- Colombo et al. về RFCI.

### Gần nhất

- [Guess2Graph](https://arxiv.org/abs/2510.14488).
- [Learning to Defer for Causal Discovery](https://arxiv.org/abs/2502.13132).
- [Causal Discovery with Language Models as Imperfect Experts](https://arxiv.org/abs/2307.02390).
- [tFCI/tIOD với tri thức phân tầng](https://arxiv.org/abs/2503.21526).
- [dcFCI](https://arxiv.org/abs/2505.06542).
- [Robust Causal Discovery under Imperfect Structural Constraints](https://arxiv.org/abs/2511.06790).
- [LLM Cannot Discover Causality](https://arxiv.org/abs/2506.00844).

### Câu hỏi phải trả lời sau khi đọc

1. Guess2Graph dùng thuộc tính nào của PC không còn đúng trong FCI?
2. tFCI cần tri thức đúng ở mức nào?
3. dcFCI có thể làm backend thay FCI hay là baseline cạnh tranh?
4. Lời khuyên path-level có thể được định nghĩa mà không dùng ground truth như thế nào?
5. Có thể tạo conservative anytime PAG từ tập kiểm định chưa đầy đủ hay không?
