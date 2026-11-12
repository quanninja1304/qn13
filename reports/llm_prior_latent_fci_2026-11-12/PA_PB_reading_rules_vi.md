# Luật đọc cho hai pilot P-A và P-B: "FCI lấy gì từ một guess của LLM dưới biến ẩn?" (12/11/2026)

> **Trạng thái: KHÓA ngày 12/11/2026** sau khi user đọc và duyệt ("tôi đã đọc và duyệt"). Mọi thay đổi về sau chỉ được ghi thêm ở §7, và không bao giờ sau khi đã xem metric. Ba tham số đã điền theo quyết định của user cùng ngày (§2.1, §4.4).
> **Thứ tự chạy:** P-B trước (không cần LLM, không cần dữ liệu), P-A sau.
> **Nhãn:** [Verified-code] đã kiểm trong mã nguồn trên máy; [Inference]; [Hypothesis].
> Kế hoạch tổng thể và bối cảnh: [`00_plan_vi.md`](00_plan_vi.md).

## 0. Mục đích

Hai pilot đo **hai vế** của cùng một câu hỏi, mỗi vế độc lập với vế kia:

- **P-A (vế LLM):** lỗi của LLM khi đoán cấu trúc nhân quả có **tập trung vào các cặp bị confound bởi biến ẩn** hay không. Giả thuyết **H-type**: LLM khẳng định "A gây B" ở cặp A↔B (nguyên nhân chung bị ẩn) nhiều hơn hẳn ở cặp không liên quan.
- **P-B (vế FCI):** khi một guess sai được đưa vào FCI như tri thức nền cứng, lỗi **lan** tới đâu, qua luật nào, và **có phát hiện được từ dữ liệu không**. Giả thuyết **H-prop**: các kiểu guess sai chỉ tồn tại khi có biến ẩn (↔ bị đoán thành →, → bị đoán thành ↔) gây hại nhiều hơn kiểu guess sai cũng tồn tại dưới causal sufficiency (đảo chiều).

Cả hai pilot đều có giá trị ở mọi nhánh kết quả (bảng quyết định ở §5). Không pilot nào kiểm một phương pháp mới.

## 1. Đối tượng và thuật ngữ

- DAG thật G trên V = O ∪ L (O quan sát, L ẩn). Không có selection bias.
- **MAG thật** M = MAG(G, O): A và B kề nhau trong M khi và chỉ khi có inducing path giữa chúng tương đối với L, tức không tập con nào của O \ {A, B} d-tách chúng trong G. Dấu: A → B nếu A ∈ An_G(B); A ↔ B nếu không ai là tổ tiên của ai.
- **PAG thật** P* = PAG của lớp tương đương Markov của M, tính bằng `causallearn.utils.DAG2PAG.dag2pag` [Verified-code: hàm tồn tại, chữ ký `(dag, islatent, isselection=[])`].
- **Loại cặp quan sát** {A, B} ⊆ O, theo M và G:

| Loại | Định nghĩa | Ý nghĩa |
|---|---|---|
| **D** | kề trong M, A → B | quan hệ tổ tiên trực tiếp giữa biến quan sát |
| **B** | kề trong M, A ↔ B | liên kết chỉ do nguyên nhân chung bị ẩn |
| **I** | không kề trong M, A ∈ An_G(B) | tổ tiên qua trung gian quan sát |
| **N** | không kề trong M, không có quan hệ tổ tiên hai chiều | không liên quan nhân quả |

- **Claim tổ tiên** trong một PAG output: đuôi tại X trên cạnh X–Y (dạng `X --> Y`) nghĩa là output khẳng định X ∈ An(Y). **Claim không tổ tiên:** mũi tên tại X (dạng `X <-* Y`) nghĩa là X ∉ An(Y).

## 2. Dữ liệu chung

### 2.1 Đồ thị thật

**(a) Mạng bnlearn** (user cho phép tải, 12/11), chỉ lấy cấu trúc từ file `.bif` (parser tự viết, chỉ đọc dòng `probability ( X | P1, P2 )`), SHA-256 ghi vào `DATA_MANIFEST_vi.md`. Mười mạng có tên biến đọc được: `asia` (8), `cancer` (5), `earthquake` (5), `survey` (6), `sachs` (11), `child` (20), `insurance` (27), `alarm` (37), `hailfinder` (56), `hepar2` (70). Số nút ghi từ trí nhớ, sẽ đối chiếu khi tải. Nếu một mạng không tải được thì bỏ và ghi lại, không thay bằng mạng khác.

**(b) Đồ thị tổng hợp** (chỉ P-B): `safety_prior.graphs.generate_dag(observed_nodes, latent_ratio, mean_degree, seed)` [Verified-code: tồn tại trong `src/safety_prior/graphs.py`], lưới observed ∈ {10, 15} × latent_ratio ∈ {0.2, 0.4} × mean_degree ∈ {2.0, 3.0}, 50 seed mỗi ô (seed bắt đầu 20261112), tổng 400 DAG. Đồ thị không có cặp B nào bị loại khỏi các kiểu cần cặp B và được đếm riêng.

### 2.2 Ẩn biến trong mạng bnlearn

Với mỗi mạng và mỗi seed ẩn s ∈ {1, 2, 3}:
- số nút ẩn k = max(2, ⌈0.25 · |V|⌉);
- rút không hoàn lại từ tập nút có ≥ 2 con; nếu tập này không đủ k thì bổ sung từ các nút còn lại;
- yêu cầu đơn vị (mạng, s) có ≥ 1 cặp B; nếu không, rút lại với seed s + 100, tối đa 5 lần; ghi số lần rút.

### 2.3 Cách tính MAG và kiểm tra

- Với |O| ≤ 12: kề nhau ⇔ không tập con nào của O \ {A, B} d-tách (vét cạn bằng `networkx.is_d_separator`).
- Với |O| > 12: kề nhau ⇔ A và B d-liên thông khi cho (An_G({A, B}) ∩ O) \ {A, B}. Tiêu chí rút gọn này **phải** khớp 100% với vét cạn trên mọi đồ thị có |O| ≤ 12 trong cả hai nguồn dữ liệu; nếu không khớp, dừng và điều tra trước khi chạy bất kỳ pilot nào.
- **S0:** PAG dựng từ M (qua FCI oracle, §3.1) phải trùng `dag2pag` trên 100% đồ thị.

## 3. Pilot P-B: lan truyền lỗi trong FCI oracle khi có guess sai có kiểu

### 3.1 Thuật toán và oracle

- causal-learn 0.1.4.8 [Verified-code]. CI oracle: d-separation trên G đầy đủ, chỉ truy vấn giữa biến O (`CIT(data, method=d_separation, true_dag=...)` hoặc `safety_prior.ci.OracleCI`, chọn một và ghi).
- Skeleton: FAS + loại cạnh bằng Possible-D-SEP như trong `fci()` của causal-learn, `depth = -1`, `max_path_length = -1`.
- Định hướng: gọi lại **chính các hàm** `rule0`, `rulesR1R2cycle`, `ruleR3`, `ruleR4B`, `rule8`, `rule9`, `rule10` của `causallearn.search.ConstraintBased.FCI` [Verified-code: các hàm này là module-level và được `dag2pag` import] trong một vòng lặp tự viết, đúng thứ tự của `fci()`, với hai bổ sung: chèn dấu (§3.2) và ghi log "luật nào đổi dấu nào" bằng cách so khớp ma trận đồ thị trước và sau mỗi lần gọi luật. Không dùng R5–R7 (không có selection).
- **Vì sao không dùng `background_knowledge` của causal-learn:** FAS xóa cạnh khi cả hai chiều bị forbidden [Verified-code: `Fas.py` dòng 99–100], và FAS không giữ cạnh required. Vì vậy không biểu diễn được "A ↔ B" hay "thêm cạnh" bằng cơ chế sẵn có.

### 3.2 Ngữ nghĩa chèn ("hard background knowledge" kiểu Tetrad)

Sau khi có skeleton và sepset từ oracle, **trước** bước định hướng collider:
- `required X → Y`: nếu X, Y không kề thì **thêm cạnh**; đặt đuôi tại X và mũi tên tại Y.
- `asserted X ↔ Y`: giữ cạnh; mũi tên ở cả hai đầu.
- Dấu đã chèn là **bất biến**: định hướng collider và R1–R10 chỉ đổi dấu tròn, không ghi đè dấu chèn. Khi một collider lẽ ra được định hướng theo sepset nhưng bị chặn bởi dấu chèn, sự kiện đó được đếm là **xung đột phát hiện được** (§3.4).

Đây là cách "chèn tự nhiên" mà người dùng Tetrad hoặc causal-learn làm khi có tri thức nền; pilot đo hậu quả của chính cách này.

### 3.3 Các kiểu chèn

Mỗi lần chạy chèn **đúng một** guess. Với mỗi (đồ thị, kiểu): rút tối đa 5 cặp đủ điều kiện, không hoàn lại, seed cố định theo đồ thị. Chiều của cặp B và N rút ngẫu nhiên.

| Kiểu | Cặp thật | Guess đưa vào | Tồn tại dưới causal sufficiency? |
|---|---|---|---|
| T1 reverse | D (A → B) | required B → A | Có |
| **T2 confounded-as-causal** | B (A ↔ B) | required A → B | **Không** |
| **T3 causal-as-confounded** | D (A → B) | asserted A ↔ B | **Không** |
| T4 indirect-as-direct | I | required A → B | Có |
| T5 spurious | N | required A → B | Có |
| T6 correct-directed (đối chứng) | D (A → B) | required A → B | Có |
| T7 correct-bidirected (đối chứng) | B (A ↔ B) | asserted A ↔ B | Không |

Cộng một lần chạy **baseline** không chèn cho mỗi đồ thị.

### 3.4 Metric

So output với P* và với An_G. Mọi đại lượng tính **trên các cạnh khác cạnh được chèn**, trừ khi ghi "tổng".

| Ký hiệu | Định nghĩa |
|---|---|
| FA | số cặp có thứ tự (X, Y) mà output có đuôi tại X trên cạnh X–Y nhưng X ∉ An_G(Y) (claim tổ tiên sai) |
| FNA | số cặp (X, Y) mà output có mũi tên tại X nhưng X ∈ An_G(Y) (claim không tổ tiên sai) |
| Skel | số cạnh khác với M (thêm hoặc bớt) |
| **Prop** | FA + FNA ngoài cạnh chèn (mức lan truyền) |
| Dist | khoảng cách trên skeleton của M từ cạnh chèn tới dấu sai xa nhất; 0 nếu không lan |
| Conflict | 1 nếu có ít nhất một collider bị chặn (§3.2), hoặc cạnh được thêm (T4, T5) kề một cặp mà oracle có sepset; ngược lại 0 |
| **Silent** | 1 nếu Prop > 0 và Conflict = 0 |
| Rule | với mỗi dấu sai ngoài cạnh chèn, luật đầu tiên tạo ra nó (R0 collider, R1, R2, R3, R4, R8, R9, R10) |

Đơn vị thống kê là **đồ thị**: lấy trung bình trên các lần chèn cùng kiểu trong đồ thị, rồi bootstrap theo đồ thị, 2000 lần, percentile 95%, seed 20261112. Đồ thị tổng hợp và bnlearn **báo cáo riêng**; quyết định dựa trên đồ thị tổng hợp (400 đồ thị độc lập); bnlearn (≤ 30 đơn vị, 10 cụm) chỉ để đối chiếu.

### 3.5 Luật đọc P-B

- **RB0, kiểm tra bắt buộc trước khi đọc:** (i) baseline không chèn trùng `dag2pag` trên 100% đồ thị; (ii) T6 và T7 có FA = FNA = Skel = 0 trên 100% lần chạy (tri thức đúng cộng oracle không được sinh dấu sai, vì các luật là sound). Sai một trong hai thì dừng, sửa, ghi §7.
- **RB1, có lan truyền:** với kiểu T ∈ {T1, …, T5}, ghi tỉ lệ lần chèn có Prop > 0 và trung bình Prop. Mô tả, không quyết định.
- **RB2, hại đặc thù biến ẩn (quyết định chính):** Đặt ΔL = max{Prop(T2), Prop(T3)} − Prop(T1), tính trên đồ thị tổng hợp, CI bootstrap ghép cặp theo đồ thị.
  - **LATENT-SPECIFIC HARM** nếu ΔL ≥ 0.5 dấu sai mỗi lần chèn **và** cận dưới CI > 0.
  - **NO LATENT-SPECIFIC HARM** nếu ước lượng điểm ΔL < 0.5 và CI chứa 0 hoặc nằm dưới 0.
  - Trường hợp còn lại (điểm ≥ 0.5 nhưng CI chứa 0): INCONCLUSIVE, báo cáo và không quyết.
  - Lý do chọn T1 làm đối chứng: T1 cùng lớp "cặp vẫn kề, chỉ sai dấu" với T2 và T3, nhưng tồn tại cả dưới causal sufficiency. T4 và T5 (thêm cạnh) báo cáo riêng ở RB4.
- **RB3, im lặng:** trong các lần chèn T2 hoặc T3 có Prop > 0, tỉ lệ Silent. Nếu ≥ 0.5 thì ghi **SILENT**. Đây là điều kiện cho câu chuyện phương pháp: lỗi phát hiện được từ dữ liệu thì bài toán quy về kiểm tra nhất quán, đã có prior art (CICheck, Optimal Correction Sets); lỗi im lặng thì không.
- **RB4, mô tả:** phân bố Rule; Dist; T4, T5; theo latent_ratio và mean_degree; đối chiếu bnlearn.

### 3.6 Giới hạn biết trước của P-B

- Oracle CI: đo lan truyền **thuần logic** của luật định hướng, không có sai số thống kê. Lặp lại với mẫu hữu hạn là việc của Phase 2, chỉ khi P-B cho hại.
- Chỉ một guess sai mỗi lần; không đo tương tác giữa nhiều guess.
- Hard BK là cách chèn tự nhiên; soft BK và cách chèn chỉ-đổi-thứ-tự (Guess2Graph) không được đo, vì dưới oracle thứ tự kiểm định **không thể** đổi output [Inference: oracle trả cùng đáp án bất kể thứ tự], nên dưới oracle cách duy nhất một guess đổi được output của FCI là qua dấu hoặc cạnh.
- Phụ thuộc cài đặt của causal-learn 0.1.4.8, kể cả cách nó xử lý R4 với `max_path_length = -1`.

## 4. Pilot P-A: lỗi của LLM theo loại cặp dưới biến ẩn

### 4.1 Đơn vị và cặp

- Đơn vị: (mạng, seed ẩn) từ §2.2, tối đa 30 đơn vị, 10 cụm mạng.
- Cặp cho định dạng theo cặp (§4.3): **tất cả** cặp B của đơn vị; mỗi loại D, I, N rút ngẫu nhiên bằng số cặp B, tối thiểu 5 và tối đa 15 mỗi loại, seed theo đơn vị; trần 60 cặp mỗi đơn vị.

### 4.2 Điều kiện tên

- **KEEP:** tên biến đúng như trong `.bif`.
- **PSEUDO:** mỗi biến thay bằng một pseudoword 4–6 chữ cái sinh từ seed, kiểm tra không trùng từ tiếng Anh thông dụng (danh sách 10 000 từ), cố định cho cả hai định dạng và mọi model.
- Cả hai điều kiện đều kèm **một câu mô tả miền** giống nhau (ví dụ "a network describing variables in a medical diagnosis setting"), lấy từ mô tả của kho bnlearn, để chỉ tên biến thay đổi giữa hai điều kiện.

### 4.3 Hai định dạng hỏi

- **Q-GRAPH, cách chèn tự nhiên** (như Guess2Graph và các bài dùng LLM đoán DAG): đưa danh sách biến quan sát, yêu cầu trả về DAG dưới dạng danh sách cạnh `X -> Y` nghĩa là X gây ra Y trực tiếp. **Không** nhắc tới biến ẩn. Một lần gọi cho mỗi (đơn vị, điều kiện tên, model).
- **Q-PAIR, câu hỏi đúng với MAG:** với từng cặp được chọn, nêu rõ "danh sách biến có thể không chứa mọi biến liên quan của hệ", hỏi quan hệ giữa A và B, với năm lựa chọn cố định: (a) A gây B trực tiếp, không qua biến nào trong danh sách; (b) B gây A trực tiếp; (c) chỉ gián tiếp qua biến khác trong danh sách; (d) không bên nào gây bên kia nhưng có nguyên nhân chung không nằm trong danh sách; (e) không liên quan. Ánh xạ (a)/(b) ↔ D, (c) ↔ I, (d) ↔ B, (e) ↔ N.
- Prompt nguyên văn, mã sinh prompt và mã phân tích được **commit trước lần gọi đầu tiên**; hash commit ghi vào §7. Mọi response thô lưu trong `artifacts/` (không commit). Mỗi câu hỏi một lần gọi, temperature 0 nếu model cho phép, một câu trả lời.

### 4.4 Model và ngân sách (user chốt 12/11)

- **Họ 1, chạy trước: DeepSeek** qua API chính thức (tương thích OpenAI). Bản chính là model chat không reasoning (dòng V3) ở temperature 0; tên model và ngày phiên bản ghi vào §7 khi gọi lần đầu. Model reasoning (R1) nếu dùng thì chỉ ở Q-GRAPH, một câu trả lời, báo cáo riêng.
- **Họ 2, bổ sung sau: OpenAI** (một model GPT, ghim snapshot). **Họ 3, tùy chọn:** Claude qua Anthropic API nếu user mua credit; gói Claude Pro không dùng được cho API. Llama 3.3 70B qua OpenRouter chỉ thêm nếu còn ngân sách.
- Key chỉ đọc từ biến môi trường, không bao giờ ghi vào repo. Trần chi phí toàn P-A: **40 USD**; script dừng khi chạm trần và ghi lại.
- Ước lượng số lần gọi mỗi họ: Q-GRAPH 10 × 3 × 2 = 60; Q-PAIR ≤ 60 × 30 × 2 = 3600. Khoảng 1.5 triệu token mỗi họ.
- **Điều kiện quyết định:** RA1 chỉ được đọc khi đã chạy đủ **ít nhất hai họ từ hai nhà phát triển**. Kết quả với một họ chỉ là mô tả, không ra phán quyết H-type.
- Model có tỉ lệ phân tích được câu trả lời dưới 90% ở một định dạng bị loại khỏi quyết định ở định dạng đó (RA0).

### 4.5 Metric

Tính trên mỗi đơn vị, rồi trung bình theo mạng; bootstrap theo **mạng** (10 cụm), 2000 lần, seed 20261112.

| Ký hiệu | Định dạng | Định nghĩa |
|---|---|---|
| FP_B | Q-GRAPH | tỉ lệ cặp B mà DAG đoán có cạnh A → B hoặc B → A |
| FP_N | Q-GRAPH | tỉ lệ cặp N có cạnh |
| FP_I | Q-GRAPH | tỉ lệ cặp I có cạnh (indirect-as-direct) |
| TP_D, Rev_D | Q-GRAPH | tỉ lệ cặp D có cạnh đúng chiều; sai chiều |
| FP_B^pair | Q-PAIR | tỉ lệ cặp B được trả lời (a) hoặc (b) |
| Conf_B | Q-PAIR | tỉ lệ cặp B được trả lời (d) |
| Conf_D | Q-PAIR | tỉ lệ cặp D được trả lời (d) (causal-as-confounded) |
| TP_D^pair | Q-PAIR | tỉ lệ cặp D được trả lời đúng (a)/(b) đúng chiều |

### 4.6 Luật đọc P-A

- **RA0, hợp lệ:** tỉ lệ phân tích được ≥ 90% mỗi (model, định dạng); DAG đoán có chu trình được ghi và vẫn chấm theo cạnh.
- **RA1, H-type (quyết định chính; KEEP, Q-GRAPH):** ΔFP = FP_B − FP_N.
  - **H-TYPE CONFIRMED** nếu ΔFP ≥ 0.10 và cận dưới CI > 0 ở **ít nhất hai họ model từ hai nhà phát triển**; nếu chạy ba họ thì cần 2/3.
  - **H-TYPE NOT CONFIRMED** nếu điều trên không đạt.
  - Chưa đủ hai họ thì **không đọc RA1** (§4.4).
- **RA2, đối chứng PSEUDO:** ΔFP dưới PSEUDO phải nhỏ hơn dưới KEEP với cận dưới CI của hiệu > 0. Đây là kiểm tra rằng sự bất đối xứng B so với N đến từ tên biến chứ không từ cách trình bày cặp. Nếu không đạt, RA1 bị hạ xuống INCONCLUSIVE.
- **RA3, có sửa được bằng cách hỏi đúng không (KEEP):** nếu FP_B^pair ≤ FP_B − 0.10 với cận dưới CI của hiệu > 0 thì **FIXABLE BY ASKING**; ngược lại **NOT FIXABLE BY ASKING**. Kết quả này quyết định cơ chế ở Phase 2 nằm ở bước hỏi (elicitation) hay ở bước thuật toán.
- **RA4, mô tả:** Rev_D, FP_I, Conf_D; TP_D theo KEEP và PSEUDO cho từng mạng (kiểm tra thuộc lòng, đặc biệt `asia` và `sachs`); theo từng model.

### 4.7 Giới hạn biết trước của P-A

- Mười mạng, nhiều mạng nổi tiếng; PSEUDO chỉ loại được việc nhớ **tên**, không loại được việc nhớ **khuôn mẫu** của kho bnlearn.
- Loại cặp phụ thuộc vào bộ biến bị ẩn do ta chọn; LLM không biết biến nào bị ẩn trong Q-GRAPH, và đó chính là điều kiện mà cách chèn tự nhiên đặt nó vào.
- Một câu trả lời mỗi câu hỏi; không đo phương sai lấy mẫu của model.

## 5. Kết hợp hai pilot thành quyết định hướng

| P-A (RA1) | P-B (RB2) | Quyết định |
|---|---|---|
| H-TYPE CONFIRMED | LATENT-SPECIFIC HARM | **GO Phase 2.** Hai vế đều có: LLM sai đúng ở cặp bị confound, FCI khuếch đại lỗi đó nhiều hơn lỗi thường. SILENT (RB3) quyết định phần lý thuyết cần nhắm tới |
| H-TYPE CONFIRMED | NO LATENT-SPECIFIC HARM | Phần phương pháp **NO-GO** ở mức oracle. P-A đứng một mình là một phát hiện về LLM prior dưới biến ẩn; cân nhắc một bài ngắn hoặc gộp vào benchmark note. Trước khi đóng, chạy một lần P-B với CI mẫu hữu hạn (n = 500) trên 100 đồ thị để chắc hại không xuất hiện khi có sai số thống kê |
| H-TYPE NOT CONFIRMED | LATENT-SPECIFIC HARM | Hại là có thật nhưng nguồn lỗi là giả định. **NO-GO** trừ khi chỉ ra được nguồn prior khác (chuyên gia, ontology) mắc lỗi kiểu B |
| H-TYPE NOT CONFIRMED | NO LATENT-SPECIFIC HARM | **Đóng hướng**, ghi vào sổ do-not-redo. Câu hỏi của mentor đúng toàn phần |

INCONCLUSIVE ở một trong hai được xử lý như nhánh âm cho quyết định GO, và được ghi là chưa quyết.

## 6. Những điều không được làm trong hai pilot

- Không điều chỉnh ngưỡng, cách chọn cặp, prompt hay danh sách model sau khi đã thấy bất kỳ metric nào.
- Không gộp đồ thị tổng hợp với bnlearn trong RB2.
- Không diễn giải P-B oracle thành phát biểu về mẫu hữu hạn.
- Không gọi kết quả P-A là "LLM không thể làm causal discovery"; P-A chỉ đo một kiểu lỗi có cấu trúc.

## 7. Nhật ký thay đổi (append-only)

- 12/11/2026: bản nháp, chờ user duyệt và điền ba tham số.
- 12/11/2026: **user đọc và duyệt; file khóa.** Tham số điền theo quyết định của user: cho phép tải bnlearn; LLM bắt đầu với DeepSeek, bổ sung OpenAI sau, Claude chỉ nếu có API credit; trần 40 USD. RA1 ghi rõ cần ít nhất hai họ từ hai nhà phát triển mới được đọc. User cũng đồng ý trao đổi với nhóm trước khi chạy P-A và nới X31. Chưa chạy gì, chưa xem metric nào.
- 12/11/2026, **làm rõ và một thay đổi trước khi chạy P-B, CHƯA xem metric nào của P-B hay P-A:**
  1. **Đổi chuẩn của RB0(i):** `causallearn.utils.DAG2PAG.dag2pag` (0.1.4.8) **không sound**. Trên 40 đồ thị kiểm thử (seed 777–781, lưới §2.1(b)), nó cho 9 claim tổ tiên sai và 70 claim không tổ tiên sai so với An_G. Nguyên nhân khả dĩ đọc từ mã: `sepset` của nó chứa đối tượng `Node`, trong khi R3 và R4 tra theo chỉ số nguyên. Chuẩn mới là `causallearn.search.ConstraintBased.FCI.fci` chạy với `independence_test_method='d_separation'` và DAG thật (FAS + Possible-D-SEP + R1–R10 gốc). Trên cùng 40 đồ thị, cài đặt P-B trùng chuẩn mới 40/40 và cả hai có 0 claim sai. RB0(i) nay đòi baseline trùng `fci()` oracle trên 100% đồ thị; mọi đồ thị đều được kiểm, kể cả bnlearn lớn (timeout 600 s mỗi đồ thị, timeout được báo riêng).
  2. **Skeleton và sepset:** lấy trực tiếp từ MAG thật (tiêu chí An-set, đã kiểm vét cạn 132 đồ thị, 0 lệch), sepset(a, c) = (An_G({a, c}) ∩ O) \ {a, c}. Dưới oracle, điều này tương đương FAS + Possible-D-SEP; tương đương được kiểm gián tiếp qua mục 1.
  3. **Conflict:** ngoài hai trường hợp ở §3.4, một lần luật R1–R10 tìm cách ghi đè dấu chèn (bị hoàn lại) cũng tính là Conflict = 1, vì đó là mâu thuẫn phát hiện được. Số lần ghi đè được báo cáo riêng.
  4. **Đơn vị bnlearn trùng:** khi số nút có ≥ 2 con đúng bằng k, cả ba seed ẩn cho cùng tập ẩn (asia, cancer, earthquake, sachs, child, hepar2). Các đơn vị có cùng tập ẩn được **gộp làm một** cho cả P-A và P-B; số đơn vị thực tế được báo cáo.
  5. **Seed đồ thị tổng hợp:** seed = 20261112 + 1000 × (chỉ số ô lưới, 0–7) + i, i = 0–49. Cặp chèn rút bằng `random.Random(seed × 7 + 13)`.
  6. **Hai bài prior art cần kiểm ở Phase 0** đã đọc: Andrews, Spirtes, Cooper 2020 chỉ xét tiered BK đúng (và nêu FCI không complete với BK "A gây B"); Wang, Qin, Zhou 2022 chỉ xét local BK đúng. Không bài nào xét BK sai; P-B không bị thừa.
  7. **API LLM:** cả hai key hợp lệ nhưng khi kiểm 12/11 DeepSeek trả 402 (hết số dư), OpenAI trả 429 (không có credit). P-A chưa thể chạy.
  8. **Cách tính ΔL (RB2), chốt khi P-B đang chạy, trước khi đọc bất kỳ dòng kết quả nào:** với mỗi đồ thị và mỗi kiểu, lấy trung bình Prop trên các lần chèn của kiểu đó; Prop(T) là trung bình trên các đồ thị **có** kiểu T (đồ thị không có cặp B không có T2 và T7); ΔL = max{Prop(T2), Prop(T3)} − Prop(T1); CI bằng bootstrap lại tập đồ thị tổng hợp (2000 lần, seed 20261112) và tính lại ΔL trên mỗi mẫu. RB3 lấy tỉ lệ Silent gộp trên mọi lần chèn T2 và T3 có Prop > 0. Mã: `PB_analysis.py`.
- 12/11/2026, **đọc kết quả P-B** (không đổi luật): RB0 đạt (413/413 baseline trùng `fci()` oracle; T6/T7 0 lỗi). RB2 = **NO LATENT-SPECIFIC HARM** (ΔL = −0.45, CI [−0.53, −0.36]; T1 1.06 > T3 0.61 > T2 0.19). RB3 = SILENT (0.79) theo định nghĩa khóa, nhưng định nghĩa có điểm mù đối với kiểu chèn chỉ có mũi tên; phân tích post hoc cho khoảng 0.47. Sáu đơn vị bnlearn timeout. Chi tiết: [`PB_results_vi.md`](PB_results_vi.md).
- 13/11/2026, **làm rõ cho P-A, trước mọi lời gọi LLM** (chưa có lời gọi nào thành công):
  9. **Lấy mẫu cặp khi vượt trần 60:** q = min(15, max(5, #B)) cặp cho mỗi loại D, I, N (lấy hết nếu có ít hơn); cặp B lấy tối đa phần còn lại tới 60. Kết quả: 19 đơn vị (sau khi gộp tập ẩn trùng), 726 câu Q-PAIR mỗi điều kiện tên. Các mạng nhỏ (cancer, earthquake, survey) chỉ có 1 cặp B mỗi đơn vị.
  10. **Câu mô tả miền** chỉ nêu miền, không nêu khái niệm nào là biến. Bản nháp đầu có câu cho asia nhắc "tuberculosis, lung cancer, bronchitis", làm lộ nghĩa ở PSEUDO; đã sửa trước khi gọi.
  11. **Prompt** nguyên văn nằm trong `PA_prompts.py` (Q_GRAPH, Q_PAIR). Q-PAIR yêu cầu trả lời một chữ cái; max_tokens nhỏ. Thứ tự biến trong danh sách và vai trò A/B được xáo theo seed của đơn vị.
  12. **DeepSeek mặc định bật thinking** (theo trang giá chính thức, đọc 13/11). Phải dùng chế độ non-thinking cho bản chính; nếu API không cho tắt thì ghi lại và báo user trước khi chạy.
  13. **Pseudoword** sinh theo mẫu phụ âm–nguyên âm, 4–6 chữ cái. Bước kiểm trùng với danh sách 10 000 từ tiếng Anh **chưa làm** vì chưa có danh sách trên máy; phải làm trước lần gọi PSEUDO đầu tiên.
  14. **Chi phí đo trước** bằng tokenizer cục bộ và bảng giá chính thức: xem [`PA_cost_estimate_vi.md`](PA_cost_estimate_vi.md).
- 13/11/2026, **user chọn phương án B: KHÓA danh sách họ model trước mọi lời gọi.** Thay thế phần danh sách ở §4.4; ngưỡng RA1 giữ nguyên chữ nhưng được cố định như sau.
  15. **Ba họ, ba nhà phát triển, mỗi họ đúng một kênh, không trộn kênh trong một họ:**
      - **OpenAI:** `gpt-4.1-mini-2025-04-14`, API gốc, temperature 0.
      - **DeepSeek:** snapshot `DeepSeek-V4.1-Flash-1017`, chế độ non-thinking, temperature 0. Kênh ưu tiên là API gốc (`deepseek-flash`). Nếu API gốc chưa dùng được khi bắt đầu chạy họ này, dùng OpenRouter `deepseek/deepseek-v4.1-flash-1017` **ghim nhà cung cấp DeepSeek**, `allow_fallbacks = false`, tắt reasoning. Kênh đã chọn ghi vào đây trước lời gọi đầu tiên của họ, và giữ nguyên tới hết.
      - **Meta:** `meta-llama/llama-3.3-70b-instruct` qua OpenRouter, **ghim nhà cung cấp CoreWeave** (fp16, nhà cung cấp duy nhất ở độ chính xác 16 bit khi kiểm 13/11; không có bf16), `allow_fallbacks = false`, temperature 0, seed 20261112.
  16. **Ngưỡng RA1:** H-TYPE CONFIRMED khi **ít nhất 2 trong 3** họ đạt (ΔFP ≥ 0.10 và cận dưới CI > 0). Nếu một họ không chạy được hoặc bị loại theo RA0, ngưỡng **thành 2/2** trên hai họ còn lại, không bao giờ nới. Không thêm họ thứ tư.
  17. **Không xem metric nào của P-A** cho tới khi cả ba họ chạy xong (hoặc một họ bị loại có ghi lý do). Trong lúc chạy chỉ được xem tỉ lệ đọc được câu trả lời (RA0) và chi phí.
  18. **Nhà cung cấp ngừng giữa chừng:** dừng họ đó, ghi lại, không đổi sang nhà cung cấp khác; báo user.
- 13/11/2026, **sẵn sàng chạy P-A, vẫn chưa có lời gọi P-A nào** (chỉ có các lời gọi kiểm kênh với prompt trung tính "Reply with exactly one word: ready"):
  19. **Đã xác nhận với nhóm** P-A không trùng kế hoạch đang có (theo user, 13/11).
  20. **Danh sách từ tiếng Anh** (user cho phép tải): `google-10000-english.txt` từ github.com/first20hours/google-10000-english, 10 000 dòng, SHA-256 `9c965d384526facc59260e94f8ccff1582633fa385004abe1455ed457062acbc`. Pseudoword nào trùng danh sách hoặc trùng tên biến thật được sinh lại: 1 ứng viên bị loại; 369 pseudoword cuối cùng, 0 trùng.
  21. **Prompt cuối cùng:** `artifacts/llm_prior_p17/pa_prompts.jsonl`, 1 490 prompt mỗi họ, SHA-256 `f1603796285a13ae34eda41e1f27505ec6cfa729646fb4cbdcfdc3fbdcbb76b6`. Sinh tất định bởi `PA_prompts.py`.
  22. **Kiểm kênh 13/11:** OpenAI gpt-4.1-mini-2025-04-14 trả lời được; Llama 3.3 70B qua OpenRouter, nhà cung cấp CoreWeave, trả lời được; DeepSeek V4.1-Flash-1017 qua OpenRouter, nhà cung cấp DeepSeek, reasoning tắt, trả lời bằng 1 token (sau khi user bật "Allow paid endpoints that train on request data"). API gốc DeepSeek vẫn 0 USD.
  23. **Pipeline phân tích** đã chạy thử trên dữ liệu giả sinh từ đáp án đúng (FP_B = 0, Q-PAIR đọc được 100%); output thử đã xóa. Commit chứa mã chạy và mã phân tích: ghi ở mục kế tiếp.
  24. **Commit trước lời gọi đầu tiên:** `31afdbe` trên nhánh `docs/p17-llm-prior-plan` (PA_prompts.py, PA_run.py, PA_analysis.py, luật đọc tới mục 23).
  25. **Kênh DeepSeek:** API gốc vẫn 0 USD lúc bắt đầu chạy, nên dùng **OpenRouter, nhà cung cấp DeepSeek** (`deepseek_openrouter` trong PA_run.py) cho toàn bộ họ này.
  26. **Trần chi phí mỗi họ** (dưới trần chung 40 USD): OpenAI 1.0 USD, DeepSeek 0.5 USD, Llama 1.0 USD.
