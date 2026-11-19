# Luật đọc P-C1a — pilot oracle cho C1

Ngày: **13/11/2026**. Trạng thái: **PROTOCOL v1, chưa chạy; chưa có kết quả P-C1a**.

**C1 ở đây là ứng viên ngày 13/11 về đánh giá hậu quả hiệu chỉnh của PAG**, tương ứng N2 trong `research_reset_2026-11-13`; không phải C1 về sensor redundancy ngày 07/11. Theo cập nhật P19 của lịch sử, N1 là hướng chính, C1 dự phòng. Viết luật này không mở lại P17 và không cấp kết luận GO cho C1.

## 1. Câu hỏi và phạm vi kết luận

**Câu hỏi:** với cùng hệ thật và cùng câu hỏi can thiệp, những PAG sai khác nhau làm người dùng (a) đưa ra công thức sai, (b) bỏ lỡ câu hỏi có thể trả lời, hay (c) chỉ gặp thiếu thông tin vốn có như thế nào? Khoảng cách cấu trúc có phân biệt được các hậu quả ấy không, và loại thay đổi nào giải thích được chúng?

P-C1a chỉ là **graph-oracle diagnostic**, chưa lấy mẫu dữ liệu và chưa chạy leaderboard discovery. Pilot có thể kiểm semantics, tìm phản ví dụ và đề xuất cơ chế cho bước sau. Nó **không thể kết luận** FCI tốt hơn FCIT, một thuật toán bị xếp hạng sai trên dữ liệu thật, hoặc metric mới đã đủ thành bài.

Ba câu hỏi tách riêng:

1. **Correctness:** evaluator có đọc đúng PAG và công thức không?
2. **Information:** structural distance bỏ qua khác biệt downstream nào, trong phạm vi nào?
3. **Mechanism:** khác biệt được giải thích bằng visible edge/amenability, forbidden set hay blocking như thế nào, và có giữ trên graph mới không?

Nguồn nền: [AID, Henckel et al. 2024](https://proceedings.mlr.press/v244/henckel24a.html); [GAC, Perković et al. 2018, Definitions 1–4, Theorem 5 và Definition 12](https://jmlr.org/papers/v18/16-319.html); [SD, Wahl–Runge 2025](https://proceedings.mlr.press/v258/wahl25b.html); [FID, Li–Kilbertus 2025, preprint](https://arxiv.org/abs/2510.25037). Các thiết kế và luật dưới đây là đề xuất của repo, không phải kết quả của các bài này.

## 2. Những điểm phải sửa trước khi đọc số liệu

| Bản quét ban đầu | Quy tắc của P-C1a |
|---|---|
| Một PAG thật không trả lời được nhưng DAG thật trả lời được thì tính PAG sai | **Không.** Oracle PAG có ít thông tin hơn full DAG; abstention này không phải lỗi discovery |
| Gom mọi thứ thành PAG-AID, vừa phạt abstention trên vừa đòi zero tại oracle PAG | Dùng vector outcome tách loại. Chưa đặt tên distance có tính chất toán học chưa chứng minh |
| Chèn một dấu vào PAG thật rồi đọc như PAG hợp lệ | Phải kiểm hợp lệ; primary design dùng DAG thay thế hợp lệ rồi suy ra PAG. Không mặc định một edit giữ được tính ancestral/maximal/MEC |
| Lỗi loại (i)–(iv) có sẵn một hậu quả cố định | Đây là **giả thuyết cần kiểm**. Một đuôi sai không tự chứng minh backdoor mở; một cạnh hai chiều không tự chứng minh mất mọi identification |
| Không có adjustment set = không định danh | Chỉ là **không có công thức covariate adjustment hợp lệ theo graph đó**. Front-door/general ID nằm ngoài scope |
| Không đổi thứ hạng ⇒ metric cấu trúc đủ tốt nói chung | Chỉ kết luận trên graph families, queries và mức nhiễu đã kiểm, với uncertainty tương ứng |
| FCI nhiều dấu tròn nên precision thấp | Không suy ra. Circles có thể giảm số claim; phải đọc mẫu số metric |
| Chọn MAG từ PAG rồi chạy FID | Không dùng làm baseline tương đương: causal MAG và ADMG có ngữ nghĩa khác, chọn một đại diện cũng thêm thông tin |

Ví dụ bắt buộc: hệ thật chỉ có `T → Y`, nhưng observational oracle không có giả định định hướng bổ sung nên PAG hai nút có circles. Full DAG có hiệu ứng hiệu chỉnh được; oracle PAG không được chọn chiều. Evaluator không được tính việc oracle chưa trả lời là false claim hay missed opportunity của discovery.

## 3. Khóa assumptions và hai chuẩn tham chiếu

- Hệ thật `D*` là causal DAG acyclic trên `O ∪ L`; `O` quan sát, `L` ẩn. **Không selection bias** trong pilot này. Positivity và causal Markov theo mô hình; CI oracle lấy bằng d-separation, không sinh phân phối rồi viện faithfulness nếu chưa kiểm.
- Query là toàn bộ cặp có thứ tự `q=(T,Y)`, `T≠Y`, trong cùng tập `O`. Không loại query sau khi nhìn kết quả.
- `P*` là **oracle PAG hoàn chỉnh** tương ứng với thông tin observational CI trên `O`, cùng assumptions/không background knowledge. Oracle FCI là một cách tính, không phải bằng chứng độc lập rằng implementation đúng.
- `P′` là PAG ứng viên hợp lệ trên đúng `O`, do phép perturbation đã đăng ký tạo ra. Không đổi tập quan sát hay tập query giữa các nhánh paired.

**Chuẩn 1 — D***: kiểm công thức do P′ đề nghị có hợp lệ trong hệ thật không. Adjustment set chỉ được chứa biến thuộc `O\{T,Y}`, mặc dù verifier được biết cả `L` để kiểm đường.

**Chuẩn 2 — P***: xác định câu hỏi nào có thể được trả lời bằng policy quy định dưới cùng mức thông tin. Đây là chuẩn để đo cơ hội bị bỏ lỡ; không lấy những cơ hội chỉ nhìn thấy khi biết D* để phạt P′.

Hai chuẩn trả lời hai câu hỏi khác nhau. Một công thức có thể đúng trong D* nhưng không được bảo đảm đồng thời cho mọi mô hình phù hợp P*. Khi đó ghi **đúng ở hệ này nhưng không được oracle cùng thông tin bảo đảm**, không tự coi đó là tiến bộ hợp lệ.

## 4. Policy đọc graph phải cố định trước chạy

Với mỗi PAG G và query q, policy `π(G,q)` trả đúng một trong ba hành động, theo thứ tự sau:

1. **ZERO:** nếu G bảo đảm T không phải tổ tiên của Y, xuất công thức `p(y | do(t)) = p(y)`. Điều kiện triển khai dùng sự không tồn tại proper possibly directed path, với định nghĩa thống nhất từ nguồn. Không dùng một DAG completion tùy ý để quyết định.
2. **ADJUST(Z):** nếu không ZERO, tính tập canonical `Adjust(T,Y,G)` theo Perković Definition 12 rồi **kiểm GAC**. Chỉ trả Z nếu criterion đạt. Không lấy tập nhỏ nhất hậu nghiệm theo outcome; cùng quy tắc cho P* và P′.
3. **ABSTAIN:** các trường hợp còn lại. Nghĩa là policy không có công thức ZERO/adjustment được bảo đảm; **không phải tuyên bố hiệu ứng không tồn tại hoặc không thể định danh bằng mọi phương pháp**.

Tập canonical dựa trên possible ancestors và forbidden set như nguồn; chi tiết implementation phải khớp chính xác định nghĩa đường proper/definite status/visible. Không thay `Adjust` bằng parents trong PAG rồi gọi tương đương.

Verifier trên D*:

- ZERO đúng về mặt graphical-uniform nếu không có directed path `T→…→Y` trong D*. Không dùng parameter cancellation để tha một claim graph sai.
- ADJUST(Z) đúng khi Z thỏa criterion adjustment đầy đủ cho D* với Z quan sát được. Không chỉ kiểm một backdoor criterion đủ nhưng không complete rồi gọi mọi thất bại là invalid.
- ABSTAIN không phải một claim công thức và không đi vào mẫu số false-claim risk.

Không kiểm sai số estimation hay độ rộng confidence interval ở P-C1a. Pilot chưa có SEM coefficients/sample data nên chỉ kiểm **tính hợp lệ của công thức đối với lớp mô hình**, không đo bias số của một effect estimator.

## 5. Outcome chính — báo riêng, không dùng trọng số tùy tiện

Với mỗi `(D*,P*,P′,q)` lưu `action`, `Z`, `valid_in_Dstar`, `oracle_action` và `valid_uniformly_in_Pstar` khi có claim. Mỗi claim phải đi kèm lý do verifier/witness.

| Outcome | Định nghĩa | Cách đọc |
|---|---|---|
| **W — sai công thức** | P′ trả ZERO/ADJUST nhưng verifier D* bác bỏ | Tác hại khẳng định sai |
| **M — bỏ lỡ cơ hội** | P′ ABSTAIN và policy P* trả ZERO/ADJUST | Mất câu trả lời mà cùng assumptions cho phép |
| **U — oracle cũng chưa trả lời** | P′ ABSTAIN và policy P* ABSTAIN | Bất định vốn có trong phạm vi policy; không cộng vào W/M |
| **V — công thức hợp lệ ở D*** | P′ trả claim và verifier D* chấp nhận | Tách tiếp hợp lệ đồng thời ở P* hay chỉ đúng ở hệ cụ thể |
| **C — coverage** | Tỷ lệ query mà P′ trả ZERO/ADJUST | Mức trả lời, không tự là chất lượng |

Primary summaries theo mỗi graph/perturbation:

- `w = W / |Q|`; `m = M / |Q|`; `u = U / |Q|`; `c = C / |Q|` nếu C dùng như số đếm. Trong raw schema dùng tên `n_claim` và `coverage` để tránh nhập nhằng.
- `risk = W / n_claim`, **NA khi n_claim=0**, không ghi 0.
- `miss_rate = M / n_oracle_answerable`, **NA khi oracle không trả lời query nào**.
- Trong V, báo số claim chỉ đúng ở D* nhưng không robust với P*. Nhóm này không bị gọi là incorrect effect trong D*, cũng không được quảng cáo như uniform-valid gain.

Tại `P′=P*`, bắt buộc W=M=0; U có thể lớn hơn 0. C của oracle không phải 100%. Always-abstain có W=0 nhưng M bằng số query oracle trả lời và risk=NA. Đây là hai sanity checks bắt buộc.

**Không kết luận một P′ “tốt hơn” nếu nó giảm W nhưng tăng M mà chưa định nghĩa utility của người dùng.** Báo trade-off/Pareto, không đổi trọng số để tạo ranking reversal. Matched coverage vẫn cần cùng query hoặc phân tầng độ khó; hai tập query khác nhau không tự công bằng chỉ vì cùng kích thước.

## 6. Perturbation và đòn bẩy

### 6.1 Primary design: thay đổi graph thật dùng để tạo graph đoán

Từ D*, tạo DAG D′ trên cùng danh sách nút bằng một primitive edit đã đăng ký: thêm/xóa/đảo một cạnh khi vẫn acyclic. Giữ cùng O/L. Suy ra P′ bằng oracle CI của D′; **đánh giá P′ trên D***. D′ chỉ là bộ sinh graph đoán, không thay ground truth của phép so.

Ưu điểm: P′ xuất phát từ một causal model hợp lệ. Giới hạn: một edit ở D có thể đổi nhiều endpoint ở PAG. Phải lưu riêng `dag_edit_count`, `pag_adjacency_edits`, `pag_endpoint_edits`; không gọi đây là “một lỗi PAG” nếu thực tế nhiều thay đổi. Không áp kết quả cho một arbitrary one-mark intervention.

Sau projection, gán **nhãn mô tả**, có thể đồng thời nhiều nhãn:

- giảm thông tin định hướng (mark cố định thành circle);
- đổi claim ancestry/arrowhead-tail;
- thay bidirected status;
- thêm/mất adjacency.

Nhãn không được gán trước kết quả như “harmful” hoặc “safe”. Do các nhãn có thể đi cùng nhau, chênh lệch nhóm **không tự là causal effect riêng của từng loại endpoint**. So matched edit counts/graph/query strata trước khi bàn cơ chế.

### 6.2 Secondary diagnostic: một edit trực tiếp ở PAG

Chỉ sử dụng nếu validator độc lập xác nhận graph sau edit là PAG của một MEC hợp lệ. Ancestral/acyclic check đơn lẻ chưa đủ chứng minh maximality hoặc complete PAG. Candidate không hợp lệ được lưu và báo `INVALID_PAG`, không đưa vào ranking metric rồi gọi đó là failure của adjustment.

Với graph nhỏ, có thể tìm một DAG/MAG witness và kiểm hoàn chỉnh lại MEC bằng enumeration đã kiểm chứng. Không bắt buộc thực hiện nhánh này để chạy primary design. Nếu không có đủ valid single-edit cases, báo thiếu khả năng tách riêng loại lỗi; không dùng multi-edit thay thế mà giấu thay đổi thiết kế.

## 7. Gate correctness RC0 — phải đạt trước bảng kết quả khoa học

1. **Oracle:** baseline dùng oracle FCI với complete orientation phù hợp no-selection. Repo đã ghi `causal-learn 0.1.4.8 dag2pag` không sound trong P-B; không dùng nó làm truth. `pb_fci_typed.py` dùng lại nhiều rule của causal-learn, vì thế trùng output giữa hai đường code dùng chung rules **không phải kiểm chứng độc lập completeness**.
2. **Microcases:** graph 3–6 observed nodes, có/không latent, gồm disconnected, chain, fork, collider, confounding và đường tạo invisible edge; kiểm oracle bằng enumeration/reference độc lập khi khả thi. Bao gồm ví dụ hai nút ở §2.
3. **GAC verifier:** đối chiếu existence và validity của **cùng Z** với dagitty hoặc một implementation độc lập. Không yêu cầu hai chương trình trả cùng Z nếu chúng chọn hai valid sets khác nhau. Ít nhất 500 triples nhỏ `(G,T,Y)` như gate ban đầu; báo số graph độc lập và tổ hợp, không gọi 500 triples là 500 datasets.
4. **Full-DAG verifier:** ở graph nhỏ, enumerate mọi Z quan sát được để kiểm tồn tại adjustment; không cho phép latent vào Z. Có trường hợp có observed adjustment và trường hợp không có.
5. **Exact checks:** P′=P* cho W=M=0; relabeling tất cả nodes giữ outcomes; always-abstain có risk=NA; zero-effect và invalid-set witnesses được xuất ra đọc được.
6. **Bất kỳ mismatch chưa giải thích nào:** dừng tổng hợp khoa học. Lưu counterexample, sửa validator và version protocol trước khi chạy lại. Không dung sai 1% cho lỗi semantics.

R/dagitty chưa được cài trong công việc này; không coi RC0 đã đạt. Nếu dùng checker khác phải ghi nguồn/version và mức độc lập. Không cần Java/Tetrad cho thiết kế P-C1a; P-C1b là việc riêng.

## 8. Lưới và thống kê cho pilot

**Hai pha, không dùng lại dữ liệu khám phá để gọi xác nhận:**

- **Pha semantics:** microcases ở RC0; không bootstrap, đây là kiểm logic tất định.
- **Pha exploratory oracle:** khởi đầu từ lưới của bản quét: 20 total nodes, target mean degree 2/4/6, số latent 0/4/8. Định nghĩa “degree” phải theo generator cụ thể (undirected mean degree khác mean indegree); ghi tham số generator và realized degree. Đề xuất 10 D* mỗi ô và tối đa 12 primitive edits chọn ngẫu nhiên theo seed cố định mỗi D*, cân bằng add/delete/reverse khi có. Các con số là **giới hạn pilot quản lý tài nguyên**, không phải power calculation hay điều kiện đủ publishable. Không bổ sung edit hậu nghiệm vì outcome đẹp.
- Bnlearn giữ cấu trúc public làm external structural check, không trộn các latent masks cùng mạng thành datasets độc lập. Lưu rõ nguồn và latent mask. Không gọi graph benchmark là full causal truth thực tế.
- Nếu oracle/exhaustive verification quá tốn, giảm kích thước graph trước chạy theo budget log; ghi protocol amendment. Timeouts/invalid/no-op projections là outcomes vận hành cần báo, không bỏ âm thầm.

**Đơn vị thống kê:** D* độc lập; các edits và ordered queries bên trong là repeated measures. Gộp outcome theo D* trước bootstrap/CI. Khi so hai perturbations, dùng paired within-D* comparisons. Với bnlearn, mạng gốc là cluster, latent masks nằm trong cluster.

Báo raw numerators/denominators, median/IQR và paired differences; nếu ước lượng CI dùng cluster bootstrap 2.000 resamples theo D*, seed cố định. Số graph ít hoặc nhiều graph không có eligible edits thì ghi thiếu precision. CI mô tả population của **generator đã dùng**, không uncertainty của một phép đếm tất định trên graph cố định.

**Không dùng tương quan Spearman giữa đúng bốn loại lỗi làm kết luận chính.** SHD có thể bằng nhau theo thiết kế single-edit; ties lúc ấy không phải “rank reversal”. Primary evidence là cùng structural cost nhưng W/M khác, và nguồn của khác biệt. Kendall tau-b/Spearman với tie handling chỉ là summary phụ khi có đủ variation; báo cùng scatterplot và số unique metric values.

## 9. Baselines và kiểm cơ chế

| Baseline/control | Vai trò và giới hạn |
|---|---|
| Endpoint-Hamming + adjacency mismatch | Quy ước rõ: mỗi unordered pair mã hóa hai endpoint trong `{absent, circle, tail, arrow}`; đếm khác biệt từng endpoint, báo adjacency riêng. Không gọi công thức tự chọn là SHD chuẩn của mọi thư viện |
| Published PAG Mod-SHD | Chỉ đưa vào sau xác minh công thức/nguồn; ghi trọng số. Nếu chưa audit thì `NOT IMPLEMENTED`, không thay bằng bản tự đặt |
| Separation distance của Wahl–Runge | Direct published baseline; phải dùng entrypoint đúng MAG/MEC semantics. Không convert PAG sang đại diện tùy ý rồi che phần assumptions thêm |
| Oracle P*, always-abstain | Kiểm rằng evaluator không phạt bất định vốn có và không thưởng từ chối tất cả |
| Existing AID/FID ở supported subtask | Có thể làm control DAG/ADMG riêng; **không** trộn điểm với PAG như cùng task. FID là prior art quan trọng dù chưa có direct PAG baseline |
| Structural cost + coverage/query strata | Baseline giải thích đơn giản: khác biệt có còn sau cùng edit count và cùng query mix không? |

Với mỗi W/M witness, ghi đường/điều kiện cụ thể:

1. Amenability có đổi không? Visible directed edge nào cần được xét?
2. Z có đụng forbidden set không?
3. Có proper definite-status noncausal path không bị block không?
4. ZERO có tạo claim no-ancestry sai không?

Các điều kiện có thể đồng thời thất bại; báo multi-label, không chọn một “nguyên nhân” thuận câu chuyện. Cần phân biệt lý do policy P′ trả claim/abstain với lý do claim bị verifier D* bác bỏ. Một chỉ số topology tương quan với W chưa xác nhận cơ chế.

## 10. Luật đọc RC1–RC4 và quyết định

| Luật | Quan sát | Phán quyết được phép | Việc tiếp theo |
|---|---|---|---|
| **RC0 FAIL** | Mismatch oracle/GAC hoặc oracle P* có W/M>0 | **EVALUATOR NOT VALIDATED** | Chỉ sửa semantics; không công bố kết luận C1 |
| **RC1: counterexample** | Cùng structural cost, khác W/M, có witness kiểm được | **STRUCTURAL SCORE DOES NOT DETERMINE ADJUSTMENT CONSEQUENCE** trong ví dụ/lớp đã kiểm | Phát hiện này riêng lẻ gần AID/FID, chưa đủ novelty; đo tần suất và ranh giới |
| **RC2: coverage explanation** | Chênh lệch “tốt hơn” hết khi tách abstention/coverage/query mix | **NO EXTRA MECHANISM ESTABLISHED** | Bỏ framing ranking superiority; giữ protocol đúng, chưa chạy leaderboard lớn |
| **RC3: mechanism lead** | Hậu quả khác nhau được witness giải thích; dự đoán được trên graph mới ngoài tập tìm cơ chế, không chỉ edit count/coverage | **CONDITIONAL GO** cho kiểm tra mở rộng | Khóa claim, primary outcome và độ lớn quan trọng trước confirmatory/P-C1b |
| **RC4: agreement/low variation** | Không thấy khác biệt; hoặc oracle gần như luôn abstain; hoặc CI quá rộng | **INCONCLUSIVE hoặc LIMITED NEGATIVE**, tùy precision | Phân biệt task không đủ thông tin với structural metric thật sự dự đoán tốt; không tự tăng budget đến khi có kết quả dương |
| **Prior art subsumes** | AID/FID/SD hoặc công trình khác đã giải thích trọn hiện tượng cùng task | **NO-GO cho claim novelty hiện tại** | Có thể giữ evaluator làm hạ tầng; không đổi tên metric để tiếp tục |

**Không đặt một ngưỡng “Spearman <0.5”, “đảo top-2” hoặc “10 điểm phần trăm” làm định luật khoa học.** P-C1a là pilot tìm và kiểm witness; một counterexample đủ bác bỏ mệnh đề phổ quát, nhưng không đủ chứng minh tầm quan trọng thực tế. Trước confirmatory, phải chốt một effect size/precision có lý do gắn với query/use case và variance từ exploratory; ghi rõ đây là quyết định nghiên cứu. Không chọn ngưỡng sau nhìn confirmation.

Conditional GO ở RC3 chỉ mở quyền **đề xuất** bước tiếp theo. Pilot oracle chưa chứng minh phương pháp discovery thực tế thường tạo đúng những lỗi này; đó là câu hỏi P-C1b. Không dùng “mọi nhánh báo cáo được” để suy ra mọi nhánh đều đủ thành bài Q1.

## 11. Artifact và khóa trước khi chạy

Chưa tạo kết quả/schema code trong lượt viết này. Khi thực thi cần lưu:

- `protocol.json`: version/hash của luật đọc, generator, seeds, splits, budgets/caps và metric conventions;
- `graphs.jsonl`: D*, O/L, P*, D′, P′, hashes, primitive edit, validity/correctness status;
- `query_outcomes.jsonl`: action/Z/oracle action, hai verifier labels, witness và metric values;
- `failures.jsonl`: invalid graphs, timeouts, no-op projections, checker mismatches;
- `analysis.json` và báo cáo: outcomes theo graph, strata, paired summaries, mọi amendment;
- môi trường/version của checker; gate RC0 phải được báo PASS bằng evidence trước outcome tables.

**Những điểm còn phải giải quyết ở implementation gate:** independent oracle-PAG checker, GAC/dagitty checker, supported SD entrypoint, công thức published Mod-SHD, generator degree convention và budget theo smoke test. Đây là các phụ thuộc công khai, không phải kết quả đã hoàn thành. Chúng không ngăn việc viết luật đọc, nhưng ngăn gọi pilot là ready-to-run/validated trước khi kiểm.

Tài liệu này không sửa bản quét gốc để giữ lịch sử; những bất đồng về semantics đã được ghi trực tiếp ở §2. Không chạy pilot, không cài R/Java và không triển khai framework trong tác vụ viết luật này.
