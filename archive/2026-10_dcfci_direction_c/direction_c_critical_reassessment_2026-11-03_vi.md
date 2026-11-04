# Đánh giá lại Hướng C: nên nghiên cứu điều gì, và điều gì chưa đáng đầu tư

Ngày rà soát: **03/11/2026**. Trạng thái: **bản review để thảo luận; chưa phải quyết định chuyển hướng hay kế hoạch triển khai đã duyệt**.

Tài liệu đầu vào chính: [đặc tả Hướng C hiện tại](dcfci_pruning_formulation_and_profiling_2026-11-03_vi.md), [dcFCI bản lưu trong repo](../../docs/papers/dcFCI.pdf), Algorithm 1, Theorem 3, Appendices C/F/G; mã dcFCI và FCI.Utils tại hai commit được yêu cầu. Review bổ sung các nguồn sơ cấp bên dưới, đặc biệt những công trình làm yếu novelty của đề xuất.

**Phạm vi bằng chứng:** đã đọc tài liệu và đối chiếu mã nguồn; **chưa chạy dcFCI profiling, chưa triển khai solver, chưa xác nhận speedup hoặc tính reachable của các motif cắt tỉa**. Các con số go/no-go là ngưỡng quyết định đề xuất, không phải kết quả. “Chưa thấy trong các nguồn đã rà soát” không đồng nghĩa “chưa ai làm”.

Nhãn sử dụng: **[Đã kiểm tra]** = có nguồn/chứng minh ngắn trong review; **[Suy luận]** = nhận định từ bằng chứng; **[Mục tiêu]** = kết quả cần đạt; **[Chưa biết]** = chưa có cơ sở kết luận.

## Report A — Executive verdict

**Tôi không khuyên dành vài tháng cho Hướng C nguyên trạng như đề tài chính nhắm Q1 mạnh hoặc ICML/NeurIPS. Tôi khuyên giữ nó làm baseline và công cụ chẩn đoán, rồi dành tối đa 4–6 tuần kiểm tra một câu hỏi hẹp hơn về liệt kê các MEC khác nhau dưới các lựa chọn separator, không phải chỉ phát hiện sớm các leaf invalid.**

Đây là khuyến nghị **reframe có điều kiện**, không phải xác nhận đã tìm được một research gap đủ mạnh. Nếu các phép thử trong Report G không vượt qua, nên dừng nhánh này thay vì tiếp tục xây solver.

| Câu hỏi | Phán quyết hiện tại | Cơ sở |
| --- | --- | --- |
| Hướng C có sai về mục tiêu? | Không. Giảm chi phí tìm kiếm nhưng giữ semantics là mục tiêu hợp lệ. | Tuy nhiên một mục tiêu hợp lệ chưa phải đóng góp khoa học đáng kể. |
| Đã là research question mạnh chưa? | **Chưa.** | Chưa biết bao nhiêu chi phí tránh được; chưa có insight vượt propagation thông thường. |
| Novelty T1–T3 đủ chưa? | **Không nếu dùng chúng làm đóng góp chính.** | Collider, ancestrality và m-connection là kiến thức nền; đưa vào backtracking là mô hình CSP quen thuộc. |
| Vấn đề chỉ do cách trình bày? | **Không.** | Thiếu bằng chứng về bottleneck và thiếu kết quả mới; viết lại abstract không khắc phục được. |
| Cơ hội tốt nhất gần công việc hiện tại? | Phân biệt **cách làm chứng bằng separator** với **MEC thực sự khác nhau**, rồi tránh duyệt lại cùng một kết luận nhân quả. | dcFCI dedup theo bảng lịch sử separator; nhiều lịch sử có thể cần được phân biệt, cũng có thể là dư thừa. Mức dư thừa thực tế chưa đo. |
| Vai trò hợp lý của dcFCI? | Nguồn workload và một application/benchmark. | Không nên để mọi định nghĩa và định lý phụ thuộc vào quirks của một mã R. |

Ba tầng vấn đề cần tách:

| Tầng | Câu hỏi cụ thể | Giá trị khoa học có thể có |
| --- | --- | --- |
| Implementation | Có cần sinh toàn bộ power set rồi loại các subset chứa hai separator cùng cặp? | Đổi sang tích domain là cải tiến hợp lý, nhưng nội dung tổ hợp rất cơ bản. |
| Algorithmic | Với các lựa chọn separator tương tác qua graph constraints, làm sao tìm/liệt kê các cấu trúc hợp lệ mà ít lặp việc? | Có thể thành bài thuật toán nếu có đặc trưng mới, guarantee phù hợp và baseline mạnh. |
| Scientific | Dữ liệu/CI không chắc chắn cho phép những kết luận nhân quả khác nhau nào, và bao nhiêu chi phí thực sự cần để biểu diễn chúng đầy đủ? | Có ý nghĩa ngoài dcFCI: uncertainty, alternative explanations, constrained discovery. Cần định nghĩa chính xác tập đầu ra. |

**Điểm cần sửa trong kỳ vọng:** không nhất thiết phải có định lý “mũ thành đa thức” để đăng bài mạnh. Một thuật toán mới giải được quy mô trước đây không xử lý được, hoặc một nghiên cứu thực nghiệm xác định cơ chế thất bại quan trọng, đều có thể có giá trị. Nhưng **90% prune và 2× runtime riêng lẻ cũng không tự tạo novelty**.

### Chất lượng proposal và triển vọng contribution là hai đánh giá khác nhau

| Tiêu chí | Hướng C hiện tại | Điều cần thêm |
| --- | --- | --- |
| Significance | Vấn đề khả dĩ quan trọng, tác động thực tế chưa đo. | Chứng minh giới hạn ứng dụng bị chi phối bởi phần công việc đang tối ưu. |
| Originality | Thấp nếu contribution = T1–T3 + backtracking. | Một characterization/representation/algorithm insight không được giải quyết bởi các công trình gần nhất. |
| Soundness | Proof sketches nhìn chung đúng với premises chặt; preservation còn điều kiện. | Khóa semantics, kiểm tra dependency và đối chứng exhaustive nhỏ. |
| Technical depth | Kế hoạch triển khai chi tiết; chiều sâu khoa học chưa theo kịp. | Chứng minh vấn đề nào khó, cấu trúc nào giải được và vì sao. |
| Generality | Hiện gắn nhiều với dcFCI. | Định nghĩa input/output độc lập; dcFCI là adapter. |
| Evaluation | Thiết kế B0/B1/B2 khá tốt, chưa có kết quả. | Thêm memoization, exact solver phù hợp, phân tích reachable pools và chi phí validator. |
| Clarity | Có thể phát biểu rõ là exact search acceleration. | Không trộn guarantee search với guarantee khôi phục truth. |
| Venue fit | Chưa đủ cơ sở cho một submission mạnh. | Tùy kết quả cụ thể bên dưới, không tùy độ dài proposal. |

**Đánh giá A — proposal:** đã có cấu trúc tốt để tránh thí nghiệm sai và kiểm tra giả thuyết. **Đánh giá B — contribution kỳ vọng:** hiện còn mỏng nếu không phát hiện thêm cấu trúc mới. Đây không phải mâu thuẫn.

Với một journal AI/ML uy tín, một phương pháp chuyên biệt vẫn có thể phù hợp nếu có insight rõ, tác động đáng kể, thực nghiệm rộng và khả năng tái lập. Q1 là phân hạng theo cơ sở dữ liệu/ngành/năm; review này không gán nhãn Q1 chưa kiểm chứng cho tên journal cụ thể. Với UAI/AISTATS, cần một câu hỏi causal/statistical rõ và đóng góp hoàn chỉnh; đây không phải nơi mặc nhiên nhận một optimization nhỏ. Với ICML/NeurIPS, cần tác động hoặc hiểu biết đủ đáng kể và lập luận novelty thuyết phục; không bắt buộc mọi bài phải có theorem mới. Các tiêu chí này phù hợp với [ICML 2026 reviewer instructions](https://icml.cc/Conferences/2026/ReviewerInstructions) và [NeurIPS 2026 reviewer guidelines](https://neurips.cc/Conferences/2026/ReviewerGuidelines). **Đây là đánh giá có điều kiện, không phải xác suất nhận bài.**

## Report B — Literature & novelty audit

### B1. Ma trận các công trình quyết định novelty

Trong cột cuối, “còn khác” chỉ chỉ ra khác biệt về bài toán, **không chứng minh khác biệt ấy đủ mới hoặc quan trọng**. Các tác giả tự công bố ưu điểm thực nghiệm không được coi là kết quả đã tái lập trong repo này.

| Công trình / trạng thái đã kiểm tra | Bài toán, giả định | Kết quả lý thuyết / thuật toán / complexity liên quan | Bằng chứng thực nghiệm trong bài | Điều chưa giải quyết trực tiếp; hệ quả cho Hướng C |
| --- | --- | --- | --- | --- |
| [Ribeiro & Heider, dcFCI, arXiv 2025](https://arxiv.org/abs/2505.06542) | Search các PAG dưới latent confounding, CI hữu hạn mẫu; score data compatibility. | Algorithm 1 sinh lựa chọn separator; Theorem 3 giữ truth với điều kiện truth nằm trong nhóm được giữ mỗi vòng. Appendix G phân tích exponential candidate generation. | Synthetic và dữ liệu thực; chưa cho profile đủ để kết luận bottleneck đang nhắm. | Cải thiện generator là khoảng trống implementation có thật; chưa suy ra research gap mạnh. Trang arXiv ghi submitted to IEEE, **không coi là journal đã nhận**. |
| [Zhang, Artificial Intelligence 2008](https://doi.org/10.1016/j.artint.2008.08.001) | Orientation cho FCI với latent/selection dưới giả định chuẩn. | Quy tắc bổ sung để orientation complete. | Đóng góp chủ yếu lý thuyết. | T1 và propagation không phải discovery mới. Orientation completeness khi đầu vào phù hợp không phải oracle extendibility cho graph/separator tùy ý. |
| [Zhang, JMLR 2008](https://www.jmlr.org/papers/v9/zhang08a.html) | Causal reasoning bằng ancestral graphs. | Nền tảng MAG/PAG, diễn giải marks, m-separation và quan hệ nhân quả. | Lý thuyết. | T2/T3 dựa trực tiếp vào semantics đã biết; một circle không phải lời hứa mọi completion đều khả thi. |
| [Ali, Richardson & Spirtes, Annals of Statistics 2009](https://www.cmu.edu/dietrich/philosophy/docs/spirtes/AOS626.pdf) | Markov equivalence của MAG. | Thm 3.7: cùng adjacency và colliders with order; thuật toán nhận biết equivalence đa thức. | Lý thuyết. | Unshielded colliders chưa đủ. Có signature MEC đã biết; “tìm một signature” tự nó chưa mới. |
| [van der Zander, Liśkiewicz & Textor, UAI 2014](https://proceedings.mlr.press/r12/zander14a.html) | Tìm, kiểm tra, liệt kê m-separator trên **AG đã biết**. | Framework thuật toán, các guarantee enumeration; bản mở rộng [2018](https://arxiv.org/abs/1803.00116). | Trọng tâm thuật toán/adjustment. | Không được gọi tối ưu kiểm tra separator trên graph cố định là gap mới. Graph thay đổi đồng thời với lựa chọn separator là bài toán khác. |
| [Hyttinen et al., UAI 2013](https://arxiv.org/abs/1309.6836) | Causal models từ các CI/CD, cho phép latent và cycles theo model của bài. | Encoding SAT và suy luận trên các causal models tương thích. | Các bài toán causal discovery bằng SAT. | “Dùng solver để kiểm tra CI có nhất quán không” đã cũ; graph class và semantics cần đối chiếu với MAG. |
| [Hyttinen, Eberhardt & Järvisalo, UAI 2014](https://www.cs.helsinki.fi/matti.jarvisalo/papers/hyttinen-eberhardt-jarvisalo.uai14.pdf) | Giải conflicting CI/CD hữu hạn mẫu, latent/cyclic models. | ASP encoding và tối ưu mức vi phạm constraints có trọng số. | Synthetic với latent/cycles và các so sánh discovery. | Không thể claim mới “structural constraints + conflict resolution”. Weighted optimum của bài khác score theo family của dcFCI. |
| [Hyttinen, Saikko & Järvisalo, IJCAI 2017 — Dseptor](https://www.ijcai.org/proceedings/2017/0090.pdf) | Exact optimization causal graphs với latent/cycles. | Generic conflict cores, incremental core extraction, dynamic partial encoding, constraint hardening trong MaxSAT. | So sánh runtime với solver trước trên synthetic/real data. | **Prior art rất gần** với nogoods, incremental conflict và pruning. Thêm những thành phần ấy vào dcFCI không đủ claim mới. |
| [Magliacane, Claassen & Mooij, NeurIPS 2016 — ACI](https://proceedings.neurips.cc/paper_files/paper/2016/file/f3d9de86462c28781cbe5c47ef22c3e5-Paper.pdf) | Suy luận ancestry từ thông tin causal không chắc chắn, background/interventions. | Biểu diễn ancestry thô hơn để giảm search; soundness và asymptotic consistency; confidence cho predictions. | Đánh giá accuracy/scalability. | “Chỉ tìm ancestry thay vì cả graph” cũng đã có; không chọn làm hướng mới nếu thiếu một khác biệt kỹ thuật quyết định. |
| [Li et al., NeurIPS 2019](https://papers.neurips.cc/paper_files/paper/2019/file/e6872f5bbe75073f8c7cfb93de7f6f3a-Paper.pdf) | Separating sets nhất quán với graph skeleton/orientations, trọng tâm PC. | Lặp skeleton learning; consistent candidate sets; block-cut decomposition; Definition 1 đặt trong trường hợp không latent. | Tăng consistency/sensitivity; thực nghiệm tới graphs lớn hơn các solver exact thời đó. | Không phải full MAG extendibility. Nhưng **“separator phải nhất quán với graph cuối” đã là câu hỏi nghiên cứu từ 2019**. |
| [Claassen & Bucur, UAI 2022 — GPS](https://proceedings.mlr.press/v180/claassen22a.html) | Score-based search **qua các MEC của MAG** với latent confounders. | Characterization MEC, các phép chuyển giữa MEC, greedy PAG search; kiểm tra equivalence nhanh với sparse graphs. | So sánh speed/accuracy. | Không thể claim mới chỉ vì search trên PAG/MEC. Exact listing dưới disjunctive separator constraints không phải mục tiêu chính của GPS. |
| [Kocaoglu, NeurIPS 2023](https://arxiv.org/abs/2301.09028) | DAG discovery chỉ dùng CI với conditioning size ≤ k. | k-Markov equivalence, closure representation và k-PC. | Synthetic/finite-sample evaluation. | “Giới hạn conditioning sets” đã có characterization. Không áp kết quả causal-sufficiency trực tiếp cho MAG. |
| [Wang, Du & Zhou, ICML 2024 — MAGLIST](https://proceedings.mlr.press/v235/wang24o.html) | Liệt kê MAG **trong một MEC/PAG đầu vào đã cố định**, gồm latent/selection. | Đặc trưng valid local transformations, sound/complete incorporation rules; tránh intermediate graphs dư thừa theo nghĩa của bài. | So sánh hiệu quả listing. | Khác dcFCI ở fixed MEC/skeleton. Không được suy ra polynomial total time hoặc chuyển nguyên local tests sang skeleton đang đổi. |
| [Ganian, Korchemna & Szeider, IJCAI 2024](https://www.ijcai.org/proceedings/2024/0374.pdf) | Complexity discovery DAG từ CI oracle và super-structure. | Thm 11: PC có thể cần separator lớn dù separator nhỏ tồn tại. Thm 14/16: thuật toán theo tham số cấu trúc; giới hạn của parameter treewidth trong oracle model của bài. | Đóng góp complexity chủ yếu. | Bác tư duy “separator nhỏ ⇒ PC nhanh” hoặc “treewidth nhỏ ⇒ mọi causal problem dễ”. Không tự chuyển lower bounds sang input CI table hữu hạn/MAG search. |
| [Lee, Ribeiro & Kocaoglu, UAI 2025 — C-PC](https://proceedings.mlr.press/v286/lee25a.html) | DAG, **không latent/selection**; với mỗi C trong collection phải có thông tin CI cho mọi cặp hợp lệ; ∅ thuộc collection. | Def 3.1; C-closure, Thm 3.6 equivalence; Cor 3.10 và Thm 3.11 cho C-PC. §3.6 cho phản ví dụ adjacency search đơn giản. | So sánh discovery và một SAT baseline; xem appendix. | Khác arbitrary pair-specific query masks và latent MAGs. Đây là ranh giới giả định có thật, nhưng bỏ giả định ấy **chưa mặc nhiên là đóng góp đủ sâu**. |
| [Ma et al., CICheck, extended preprint 2023](https://arxiv.org/abs/2309.05264) | Runtime reasoning để phát hiện CI conflicts hoặc tránh tests đã được suy ra. | SMT cho reasoning theo Pearl axioms; pipeline nhẹ trước solver đầy đủ. | Runtime/CI-related evaluation theo bài. | General-purpose logical CI pruning đã có. Consistency theo axioms không đồng nhất với tồn tại MAG thỏa mọi constraints. Không dùng làm validator tương đương mà không chứng minh. |
| [Spallitta, Sebastiani & Biere, Artificial Intelligence 2025](https://doi.org/10.1016/j.artint.2025.104346) | Disjoint projected AllSAT/AllSMT. | CDCL, chronological backtracking, implicant shrinking, projection; enumerate phần biến quan tâm, existentially bỏ auxiliaries. | So sánh projected solvers. | “Bỏ witness và chỉ xuất object khác nhau” là ý tưởng tổng quát đã có. Hướng MEC enumeration phải vượt encoding chuẩn + projected solver. |
| [Freuder, AAAI 1990](https://www.aiinternational.org/Library/AAAI/1990/aaai90-001.php) | CSP trên k-tree/partial k-tree constraint networks. | Complexity tuyến tính theo số biến với phần mũ phụ thuộc width khi domain/encoding được kiểm soát. | Lý thuyết. | Bounded-width DP là công cụ nền, không phải theorem causal mới. Phải chứng minh encoding đúng và width được chặn bởi cấu trúc causal có nghĩa. |
| [Russo et al., preprint 23/10/2026](https://arxiv.org/abs/2610.33138) | Minimum-cost correction sets cho conflicting CI facts, contestable causal discovery. | ASP, correspondence và guarantees cho repair/redress. | OptABA-PC trên benchmark theo bài. | “Repair có lý do, cores và optimal correction” tiếp tục có prior art mới. **Chỉ xác nhận preprint; chưa gán venue đã nhận hoặc mở rộng latent không được chứng minh.** |

### B2. Kết quả novelty audit

**Đã có:** CI consistency solving, structural propagation, incremental conflict extraction, coarse causal representations, MEC search, projected enumeration, fixed-graph separator algorithms và fixed-MEC MAG listing.

**Chưa xác lập trong review này:** một algorithm chuyên biệt có guarantee tốt cho **liệt kê distinct MAG MECs dưới disjunction của admissible minimal separators, khi skeleton cũng thay đổi**, đồng thời vượt baseline projected solver. Đây là **candidate gap cần falsify**, không phải kết luận ưu tiên công bố.

**Không còn phù hợp để claim novelty:** “tối ưu thứ tự”; “không sinh graph sai”; “dùng CSP cho separator”; “phát hiện cycle sớm”; “có proof soundness”; “đưa vào framework”. Chúng chỉ có thể là thành phần của đóng góp cụ thể hơn.

## Report C — Mathematical & algorithmic review

### C1. State space và điều kiện hợp lệ

Fix một parent state và một vòng r. Sau preprocessing certain rows, đặt Q là các cặp có uncertain rows. Với cặp e, các row IDs là 1,…,s_e, dù hai rows có cùng giá trị separator vẫn là hai identities nếu reference phân biệt chúng:

$$D_e=\{\mathrm{KEEP},1,\ldots,s_e\},\qquad
\Omega=\prod_{e\in Q}D_e,\qquad |Ω|=\prod_e(1+s_e).$$

Nếu m=Σs_e, baseline power set có 2^m subsets trước duplicate-pair filtering. Bijection từ subset có tối đa một row/cặp sang Ω là đúng, nhưng là quan sát tổ hợp cơ bản. Khi mỗi cặp chỉ có một row, hai kích thước bằng nhau.

**KEEP chỉ có nghĩa không xóa cạnh trong bước này.** Nó không tự cung cấp một bộ CD facts mới từ dữ liệu. DELETE chọn một witness S và xóa cạnh. Với một MAG hoàn chỉnh, adjacency tất nhiên kéo theo không tồn tại m-separator giữa hai đầu; đó là semantics graph, khác với việc đã thực hiện mọi CI test.

Skeleton E(z) phải tính cả fixed gaps, certain deletions và inherited deletions. Sep(z) là effective separator matrix sau quy tắc overwrite của builder, **không mặc nhiên là tập tất cả rows trong history**. Unknown/null separator không phải empty separator.

MAG phải ancestral và maximal: không directed cycle; arrowhead tại x trên xy cấm x∈An(y); tail–tail edge cấm arrowheads incident vào hai đầu; mọi nonedge có separator. PAG chuẩn biểu diễn đầy đủ một MEC, không chỉ là mixed graph không cycle. “Ancestor completeness” không phải yêu cầu thêm cạnh bắc cầu A→C khi đã có A→B→C.

Mỗi selected separator phải m-separate; nếu yêu cầu minimality thì mọi proper subset phải không m-separate. Không sử dụng tính đơn điệu sai của conditioning. Khi cần minimality, đối chiếu thuật toán separator trên ancestral graph đã biết trước khi viết vòng duyệt subsets mới.

Với prefix σ, residual domains phải không rỗng. Kσ và Nσ chỉ chứa adjacency/nonadjacency đúng trong **mọi** completion còn lại. Endpoint domains {T,H} là biến solver; không phải dấu circle đã được chứng minh bất biến/không bất biến trên một MEC.

Một relaxation hợp lệ:

$$\mathcal W(\sigma)=\{(z,M):z\in\Omega(\sigma),\ M\text{ là MAG},\
E(M)=E(z),\ M\models\mathrm{CI}(\mathrm{Sep}(z))\}.$$

Có thể bỏ minimality khỏi relaxation để pruning dễ hơn. Khi W rỗng thì nhánh vô nghiệm về mặt toán học; W không rỗng **không đảm bảo builder dcFCI tạo được PAG mà validator nhận**.

### C2. Audit T1–T3

| Rule | Proof và hidden premises | Novelty | Khi nào có hiệu lực? | Cách gây false pruning | Nâng cấp đáng thử, chưa chứng minh lợi ích |
| --- | --- | --- | --- | --- | --- |
| T1: collider–noncollider conflict | ab,bc phải persistent; ac phải absent và có separator domain đã biết. Mọi S đều loại b ⇒ collider; mọi S đều chứa b ⇒ NC. Proof bằng đường a-b-c. | Corollary chuẩn của m-separation/R0; không phải theorem mới. | Sớm nếu nhiều cạnh đã locked KEEP và membership đồng nhất; muộn nếu adjacency còn undecided. | Lấy một S đại diện khi domain có cả chứa/không chứa b; hoặc dùng cạnh có thể bị xóa. | Maintain union/intersection membership; propagate head + NC thành tail; learned supports. |
| T2: ancestral contradiction | Forced directed reachability x↝y và head tại x trên xy vi phạm ancestry; directed cycle cũng vậy. Tail–tail restrictions cần nếu selection được phép. | Điều kiện định nghĩa ancestral graph. | Cần đủ forced marks/paths; thường sau T1/propagation. | Dùng possibly-directed path như forced-directed; giữ marks của parent sau khi builder reset. | Incremental reachability có rollback; không hứa update O(1). |
| T3: mandatory m-connecting path | Mọi cạnh persistent; mọi internal node forced NC ngoài S hoặc forced collider thuộc forced An(S), gồm S. Khi đó path mở trong mọi completion, trái CI. | Chứng minh trực tiếp từ định nghĩa m-connection. | Có thể bắt conflict dài hơn T1, nhưng cần nhiều premises. | Thay An(S) bằng possible ancestors; coi chưa xác định collider là NC; bỏ cả domain vì chỉ một S vi phạm. | Witness ngắn, cached supports; augmented-graph/global constraints nếu có proof. |

**Proof T1 cần hiểu đúng hai chiều.** Nếu b∉S nhưng b là NC thì đường hai cạnh mở. Nếu b∈S nhưng b là collider thì conditioning kích hoạt collider. Cả hai trái CI; không cần giả định S minimal. Khi membership lẫn lộn, chỉ có implication điều kiện theo giá trị được chọn, chưa có orientation vô điều kiện.

**Một false-pruning counterexample tối giản:** lấy S_ac=∅ và trạng thái tạm a→b→c. Nếu bc vẫn có thể bị DELETE, prefix có thể hoàn tất thành a→b và c cô lập, hoàn toàn thỏa a⊥c. Prune bằng đường a→b→c trước khi khóa bc là sai. Đây là phản ví dụ logic cho implementation, **không phải một pool reachable đã được đo từ dcFCI**.

**Ancestral check phải mạnh hơn DAG-cycle check:** x↔y và x→z→y không có directed cycle, nhưng không ancestral. T2 cần bắt trường hợp này.

**T1/T2 chưa đầy đủ:** graph x→a→b→y hoàn toàn ancestral/maximal, không có collider conflict, nhưng không thỏa selected CI x⊥y|∅. Một T3 witness đầy đủ bắt được; T3 giới hạn độ dài có thể bỏ sót path dài hơn. Có thể thỏa T1–T3 đang kiểm tra mà vẫn fail maximality, minimality hoặc endpoint invariance. Không được gọi closure của ba rules là test extendibility chính xác.

**Hiệu quả trên pool thật: chưa biết.** Các điều kiện plausible ancestors trong pool builder có thể đã loại nhiều motif dễ. Cần đo số rules có support trước 25%, 50%, 75% depth; tổng subtree mass tránh được; invalid reasons mà full validator trả về. Hit count cao ở depth q−1 chưa chứng minh search tiết kiệm lớn.

### C3. Các semantics của mã nguồn làm thay đổi kết luận

Hai bản pin: [dcFCI](https://github.com/adele/dcFCI/tree/a27c495acc28810a1e8e95878d535d90f82faaaf), [FCI.Utils](https://github.com/adele/FCI.Utils/tree/361e8904feb448d5d8069af694670e16e96a9e1f). Còn phải pin R, pcalg, ggm, dagitty và packages liên quan khi chạy.

| Hạng mục | Điều đã đối chiếu trong code | Hệ quả |
| --- | --- | --- |
| Builder | `potAdjM <- curpag$amat.pag > 0`; rồi xóa cạnh và viết `potSepset`. [dcFCI.R L301](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/dcFCI.R#L301) | **Parent endpoint marks bị reset.** Chỉ giữ marks đã suy ra lại từ persistent premises. |
| Certain rows | Filter tránh duplicate pair áp vào uncertain subset; nhiều certain rows/cặp có thể cùng đi vào builder. | Separator matrix dùng row viết sau cùng, history giữ cả rows. Nếu pruning coi tất cả certain rows là hard CI, proof F_ref⇒F_math có thể không còn đúng. |
| Orientation/validation | `udag2pag` → `hasViolation` → chỉ candidate valid mới `getMEC(scored=TRUE)`. [L223](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/dcFCI.R#L223) | Loại invalid candidates thường giảm graph work, không nhất thiết giảm statistical CI tại scoring. |
| Valid PAG | Canonical MAG, `ggm::isAG`, rồi chạy graph-oracle FCI và so lại endpoint matrix khi conservative=knowledge=FALSE. [utils.R L471](https://github.com/adele/FCI.Utils/blob/361e8904feb448d5d8069af694670e16e96a9e1f/R/utils.R#L471) | Validator có nội dung mạnh hơn cycle check. Có cơ sở chứng minh preservation theo dependency assumptions; chưa phải formal verification của packages. |
| Sep validation | `sepsetDistance`, `isMSeparated`, `checkSepMinimality`. [metrics.R L71](https://github.com/adele/FCI.Utils/blob/361e8904feb448d5d8069af694670e16e96a9e1f/R/metrics.R#L71) | Phải dùng effective matrix mà validator nhận. Membership in implied separator lists và path minimality có thể chặt hơn một CI witness tùy ý. |
| Cost validator | `checkSepMinimality` duyệt proper subsets và `getMConnPaths`. [L233](https://github.com/adele/FCI.Utils/blob/361e8904feb448d5d8069af694670e16e96a9e1f/R/metrics.R#L233) | Không áp máy móc per-leaf polynomial bound của paper vào implementation này. Đây có thể là bottleneck khác generator. |
| Dedup | `getUniquePAGList(key="sepset")` dùng **toàn bộ `sepsetResults` table**, bỏ row names, giữ occurrence đầu; không phải chỉ separator matrix hoặc PAG. [dcFCI.R L1020](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/dcFCI.R#L1020) | Metadata, thứ tự rows và history ảnh hưởng identity; phải bảo toàn representative order khi claim same output. |
| Dedup timing | Dedup raw children toàn cục trước orientation/validation. [L615](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/dcFCI.R#L615) | Validate mọi leaf trước dedup làm đổi lượng công việc. Không gọi đó là downstream unchanged. |
| Score | Union CI queries của valid family, gán implication theo từng PAG, lấy phần phân biệt giữa members. [score_utils.R L290](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/score_utils.R#L290) | Score candidate trên family chưa đủ không phải upper bound admissible mặc nhiên. Không prune valid candidate bằng score hiện tại mà gọi exact branch-and-bound. |
| Selection | `getTopPagIds` phối hợp tiêu chí/ties; `k=1` không nhất thiết chỉ còn một object. | Không thay tie/selection semantics bằng textbook top-k. |
| Caps/logging/cache | Cap có thể quay lại vòng trước; guard số rows có điều kiện verbosity; cache có thể merge sau batch. | Ghi rõ capped/timeout, verbosity, actual vs unique CI executions; speedup nhờ khác cutoff không chứng minh exact acceleration. |

Những điểm này là audit implementation. Chúng không chứng minh dcFCI sai về lý thuyết, và sửa chúng chưa chắc tạo ra paper mới.

### C4. Có thể chứng minh F_ref ⇒ F_math không?

**Có đường chứng minh hợp lý cho semantics hẹp; chưa hoàn tất proof cho toàn bộ pipeline đã pin.** Không nên để implication này thành một giả định mơ hồ vĩnh viễn, cũng không tuyên bố nó đã được máy kiểm chứng.

Chọn F_math đúng bằng relaxation sử dụng **effective Sep matrix và skeleton của raw builder**. Trong nhánh mặc định của `hasViolation`, acceptance đòi canonical completion ancestral, PAG khôi phục từ oracle trùng input, và các selected separators pass m-separation checks. Nếu các conversions/oracle/FCI đúng và không đổi vertex/selection semantics, điều này cung cấp một MAG witness phù hợp. Maximality phải được nối với oracle reconstruction hoặc canonical conversion theorem, không chỉ với `isAG`.

Để hoàn tất nghĩa thực thi, cần chứng minh/kiểm tra: skeleton không đổi qua orientation; canonical conversion bảo toàn labels/adjacency; oracle đúng trên graph class; effective separators chính là premises pruning. Khi conservative/knowledge bỏ reconstruction, proof phải được làm lại. Một test nhỏ pass không chứng minh theorem cho mọi p.

Ở mức pipeline còn cần:

1. **Dedup congruence:** cùng key phải có cùng acceptance theo semantics đang dùng. Có thể chứng minh bằng invariant rằng history tái dựng skeleton/sepset từ cùng initial graph; chưa được bỏ qua fixed gaps, overwrite và inherited state.
2. **Representative:** nếu hai raw states cùng key nhưng khác thông tin ảnh hưởng vòng sau, phải giữ đúng representative reference; chỉ equality PAG không đủ.
3. **Scoring:** valid family, CI values, score vectors và tie order phải giống nhau. Invalid-only pruning không đổi family nếu các điều kiện trước đúng.
4. **Execution:** caps không cắt khác tập; cache/test randomness không đổi CI values. Nếu muốn so actual CI calls, cache semantics cũng phải giữ.
5. **Induction:** cùng selected full states cuối vòng r mới suy ra cùng input vòng r+1.

Kết quả mong muốn là **bảo toàn search**, không phải guarantee mới về truth. Theorem 3 của dcFCI có điều kiện truth ở trong nhóm được giữ qua các vòng; một exact generator không loại bỏ điều kiện thống kê/selection này.

### C5. Complexity, extendibility và cơ hội theorem thực sự

Phải phân biệt ba decision problems:

$$\mathrm{Ext}_{MAG}(\sigma):\exists(z,M)\in\mathcal W(\sigma),$$
$$\mathrm{Ext}_{min}(\sigma):\exists(z,M)\in\mathcal W(\sigma)\text{ thỏa yêu cầu minimality},$$
$$\mathrm{Ext}_{ref}(\sigma):\exists z\in\Omega(\sigma):F_{ref}(z)=1.$$

Chúng không mặc nhiên tương đương. Giải relaxation Ext_MAG có thể prune sound nhưng không loại hết nhánh reference vô ích; giải Ext_ref lại phụ thuộc builder. Thuật toán cho một graph đã biết hoặc một PAG đã valid không giải ngay vấn đề simultaneous skeleton/separator completion.

| Cơ hội | Trạng thái | Điều phải chứng minh để có nội dung mới |
| --- | --- | --- |
| Characterization cần-đủ của extension trên lớp graph xác định | **Open target trong project**, không khẳng định open problem toàn ngành. | Class không được định nghĩa bằng “solver chạy nhanh”; mọi prefix/domain restriction phát sinh phải thuộc miền guarantee. |
| DP theo width của constraint encoding | Công cụ CSP đã biết. | Encoding đầy đủ cho ancestry, maximality, m-separation, minimality; width gắn với tham số causal có thể đo và nhỏ trên workload có nghĩa. |
| Global inducing/discriminating-path propagation | Necessary conditions có thể mạnh hơn local rules. | Premises persistent; support nhỏ; chi phí thấp hơn validator; completeness chỉ nếu chứng minh. |
| Output-sensitive listing | Mục tiêu hợp lệ. | Đếm output nào: assignments, raw states, distinct PAGs hay MAGs? Mỗi loại cho guarantee khác nhau. |
| Lower bound | Có thể làm sáng tỏ giới hạn. | Phân biệt output-size, oracle-query và NP-hardness bằng reduction. Không suy một loại từ loại kia. |

**Output barrier đã có chứng minh ngắn:** q cặp đỉnh rời, mỗi cặp KEEP hoặc DELETE với empty separator, các cặp khác absent. Có 2^q matching skeletons/PAGs hợp lệ; treewidth causal ≤1. Liệt kê tất cả cần Ω(2^q) output. Đây là generator-input family, **chưa phải proof rằng mọi pool ấy reachable từ dcFCI mặc định**. Nó không chứng minh NP-hardness và không cản compact representation/top-k.

**Conditional enumeration bound:** nếu có exact extension oracle cho mọi restriction, chi phí C_ext, q variables, domain tối đa d, K accepted assignments thì DFS có chi phí generation O(qd(K+1)C_ext). Đây là self-reduction quen thuộc. Nếu C_ext exponential, hoặc K exponential, chưa có polynomial total algorithm. Nếu K đếm assignments trước dedup, cũng chưa có polynomial delay giữa **distinct MEC outputs**.

**90% prune là empirical milestone:** 0,1·2^q vẫn exponential. Phải đo relative to pair-domain baseline B1, không relative to B0 power set. Nếu invalid chỉ chiếm 2% leaves, bỏ 90% invalid chỉ bỏ 1,8% toàn bộ leaves.

### C6. Profiling tối thiểu để quyết định có vấn đề đáng giải không

Giữ thiết kế B0 reference, B1 pair-domain, B2 pruning; thêm **B1 + memoization/validation reuse** và solver cùng semantics khi khả thi. Đầu tiên replay snapshots reachable, sau đó end-to-end.

Đo exclusive time của pool CI, enumeration, allocation/build, orientation, graph validity, separator minimality, MEC/score, dedup/rank; đo peak RSS toàn process tree. Tách statistical CI requests/cache hits/actual executions/unique queries khỏi graph-oracle calls. Invalid candidates không đến score nên số statistical CI giảm bằng 0 vẫn có thể phù hợp với hypothesis runtime.

Đếm chuỗi:

$$N_{power}\rightarrow N_{pair}\rightarrow N_{history}\rightarrow
N_{valid\ history}\rightarrow N_{MEC}.$$

Chuỗi này phân biệt ba nguồn lãng phí: duplicate-pair subsets, graph-invalid states và multiple witnesses cho cùng MEC. Đo thêm thời gian ở từng nguồn; tỷ lệ counts không thay thế tỷ lệ runtime.

Nếu fraction f thời gian B1 có thể tránh, speedup lý tưởng ≤1/(1−f). Nếu f<0,1 trên lớp đích, dừng tham vọng runtime lớn ở thành phần đó. Nếu f lớn nhưng memoization đã xử lý gần hết, không cần pruning engine mới. Các ngưỡng này là quy tắc quản trị dự án, không phải kết quả khoa học phổ quát.

Oracle correctness: compare endpoint matrices/full states trực tiếp, không chỉ SHD. Accuracy: dùng ground-truth PAG từ latent projection + converter được kiểm tra độc lập, ghi convention SHD/endpoint distance; với output nhiều graphs báo coverage và size, không chọn best-SHD graph rồi gọi đó là prediction chính.

## Report D — Bốn hướng nghiên cứu khác nhau về bản chất

Không hướng nào dưới đây được gắn nhãn “gap đã chắc chắn mới”. Mức độ đã xác minh khác nhau: D1 có bài toán thực thi rõ nhưng novelty yếu; D2 có target tổ hợp rõ nhưng tính hữu ích và lợi thế trên solver còn mở; D3 có mechanism khả dĩ cần falsify; D4 có ranh giới giả định trong literature đã xác minh nhưng theorem còn khó và có thể chỉ là extension đơn giản.

### D1 — Revised C: exact incremental extendibility trên một lớp cấu trúc

| Hạng mục | Đặc tả |
| --- | --- |
| 1. Title | **Incremental Extendibility of Partial Separating-Set Assignments in Ancestral Graphs**. |
| 2. Research question | Trên lớp graph/constraint nào, một partial assignment có MAG completion thỏa tất cả selected minimal separators khi và chỉ khi một hệ điều kiện kiểm tra hiệu quả được thỏa? |
| 3. Importance | Phát hiện nhánh vô nghiệm mà không dựng hàng loạt graphs; kết quả dùng được cho constrained discovery, không chỉ R implementation. |
| 4. Closest works | Zhang; MAGLIST; separator algorithms 2014/2018; ASP 2014; Dseptor 2017; bounded-width CSP. |
| 5. Exact candidate gap | **Simultaneous variable skeleton + multiple separator obligations** trên một lớp hạn chế được xác định trước. Không claim gap cho fixed valid PAG, fixed MAG hoặc arbitrary CI SAT solving. |
| 6. Scientific contribution | Characterization cần-đủ trên lớp đó, incremental algorithm, và một phân tích khi local propagation thất bại. |
| 7. Theory targets | Soundness/completeness của extension test; parameterized cost; output-sensitive assignment listing; nếu không tractable, reduction/lower bound đúng input model. |
| 8. Algorithm | Khởi đầu fixed skeleton có block size nhỏ; state boundary ghi endpoint, reachability và separator obligations. Chỉ chuyển sang changing skeleton nếu decomposition còn đúng. |
| 9. Evidence | Exhaustive MAG oracle ở p nhỏ; reachable dcFCI snapshots; đo thời điểm conflict và avoided cost; so B1, memoization, T1–T3, SAT/ASP encoding cùng graph class. |
| 10. Prerequisites | MAG separation/inducing paths, CSP decomposition, proof về separators vượt block boundaries; chốt selection/no-selection. |
| 11. Main risks | Bound giả vì global constraints phá decomposition; known CSP result giải trọn; class quá nhỏ hoặc không xuất hiện trong workload. |
| 12. Smallest complete contribution | Một class tự nhiên, theorem mới thật sự về extension, algorithm có proof và benchmark chứng minh class ấy có ích. Chỉ correctness T1–T3 + implementation chưa đủ. |
| 13. Strong outcome | Parameter quyết định khó/dễ đo được và giải thích runtime trên nhiều discovery workloads. |
| 14. Breakthrough target | Exact extension oracle và polynomial-delay listing trên lớp đáng kể, kèm ranh giới hardness rõ. **Chưa có.** |
| 15. Venue | UAI/AI journal nếu graph-theoretic result hữu ích; ICML/NeurIPS nếu insight và tác động đủ mạnh. Một bài complexity thuần có thể hợp venue thuật toán hơn. |

**Các bước và quyết định.** Stage 1: đọc proof MAGLIST/Dseptor/van der Zander, viết rõ vấn đề nào khác. Stage 2: lấy fixed forest/block-small làm miền kiểm chứng; thử tìm hai states có boundary summary giống nhau nhưng extension khác nhau để phá DP. Stage 3: một theorem hoàn chỉnh trên lớp hẹp. Stage 4: changing skeleton, broader class, runtime decomposition. Stage 5: dừng nếu chỉ còn viết lại CSP theo width hoặc nếu kiểm tra cấu trúc đắt ngang validation.

**Fatal:** characterization không mới hoặc class không mang thông tin causal đáng kể. **Manageable:** chọn no-selection trước, bỏ minimality khỏi một relaxation nhưng hạ claim rõ. **Upside:** boundary summary nhỏ dù graph lớn; có nontrivial lower bound cho local-rule systems.

### D2 — Khuyến nghị chính để kiểm tra: liệt kê MEC, không liệt kê mọi separator witness

| Hạng mục | Đặc tả |
| --- | --- |
| 1. Title | **Enumerating Causal Equivalence Classes under Alternative Separating-Set Constraints**. |
| 2. Research question | Có thể liệt kê mỗi MEC của MAG thỏa các lựa chọn separator **đúng một lần**, mà không duyệt trước mọi tổ hợp separator witnesses hoặc mọi MAG trong MEC ấy? |
| 3. Importance | Người dùng cần các giả thuyết nhân quả khác nhau; số cách chứng minh cùng một giả thuyết không nên chi phối toàn bộ computation. |
| 4. Closest works | MAG equivalence 2009; GPS 2022; MAGLIST 2024; causal SAT/ASP; projected AllSAT 2025; dcFCI. |
| 5. Exact candidate gap | Exact distinct-MEC enumeration dưới **disjunctive admissible-minimal-separator constraints và variable skeleton**. Không claim mới MEC signature, projection hoặc graph search nói chung. |
| 6. Scientific contribution | Một graph-specific representation/algorithm tránh witness multiplicity, có completeness và output-sensitive analysis; giải thích khi multiplicity chứ không phải invalidity gây khó. |
| 7. Theory targets | Characterization separator supports invariant theo MEC; sound/complete duplicate-free enumeration; bound theo số MEC và tham số cấu trúc, không chỉ theo số witnesses. Các phần elementary phải ghi nhận là tools, không contribution chính. |
| 8. Algorithm | Existentially loại separator-choice variables; search bằng MEC signatures với symbolic support sets; incremental separation checking và blocking cả MEC. Projected SAT là baseline bắt buộc. |
| 9. Evidence | Đếm assignment/history/MAG/MEC riêng; so frozen-pool enumeration, generic projected solver và optimized memoization; đo số MEC tìm được theo budget, coverage và delay. |
| 10. Prerequisites | MAG canonicalization/equivalence, m-separator minimality, projected SAT; một oracle enumeration p nhỏ độc lập. |
| 11. Main risks | Ít duplicates thật; history không thể bỏ trong dcFCI; solver generic đã đủ; encoding MEC signature đắt; số distinct MEC vẫn exponential. |
| 12. Smallest complete contribution | Một insight đặc thù graph vượt “encode rồi gọi AllSAT”, proof chính xác về target, và lợi ích ổn định trên workload độc lập. Nếu chỉ dedup sau khi sinh thì chưa đạt. |
| 13. Strong outcome | Tăng đáng kể số alternative causal classes có thể khảo sát trong cùng budget, vượt generic projected solver; không bị giới hạn vào dcFCI. |
| 14. Breakthrough target | Polynomial delay giữa **distinct MECs** trên lớp được mô tả cấu trúc, dù số separator witnesses exponential. **Mục tiêu, chưa có theorem.** |
| 15. Venue | UAI/AI journal cho enumeration có giá trị causal; ICML/NeurIPS nếu mở rộng rõ quy mô uncertainty-aware discovery và có algorithmic insight mạnh. Không đủ nếu chỉ faster dcFCI ở vài seeds. |

#### D2.1. Target toán học, để tránh một “framework” mơ hồ

Giai đoạn đầu xét MAG không selection, tức directed/bidirected edges; cycles bị cấm theo ancestrality. Selection là extension riêng.

Input gồm V; skeleton lower/upper bounds E⁻⊆E⁺; hard CI/CD facts B; một tập Q các cặp có lựa chọn KEEP hoặc DELETE; với mỗi cặp e là finite admissible separator family S_e và các restrictions tương ứng. Rows có metadata giữ riêng trong adapter; target toán học dùng separator sets và không nhân số outputs vì duplicate rows.

Đặt A là các MAG M sao cho:

1. E⁻⊆E(M)⊆E⁺ và M thỏa B.
2. Với e∈Q: nếu e được giữ thì KEEP phải được phép; nếu e bị xóa thì tồn tại S∈S_e được phép và S là minimal m-separator của e trong M.
3. Những certain/inherited requirements được biểu diễn đúng như hard constraints, hoặc declared builder semantics nếu đang xét adapter reference.

Output toán học:

$$\mathfrak P(B,\{\mathcal S_e\},E^-,E^+)
=\{\operatorname{PAG}([M]):M\in\mathcal A\},$$

trong đó [M] là **full Markov equivalence class**, không phải equivalence chỉ trên các CI đã test. Mỗi PAG xuất một lần. Empty output có nghĩa constraints inconsistent; không âm thầm sửa CI.

**Phân biệt bắt buộc:** tập này có thể rộng hơn

$$\mathfrak P_{ref}=\{B_{ref}(z):z\in\Omega,\ F_{ref}(z)=1\},$$

vì orientation builder dcFCI không được chứng minh liệt kê mọi MEC thỏa disjunction. Vì vậy B0 dcFCI là application baseline, **không tự là completeness oracle** cho target mới. Nếu chỉ muốn tăng tốc dcFCI đúng nguyên bản, dùng target P_ref và giữ full-state contract; không quảng cáo đó là giải toàn bộ P.

#### D2.2. Một phép phân rã cụ thể, đã có lập luận, nhưng chưa đủ novelty

Với một MEC/PAG P có skeleton cố định, đặt

$$A_e(P)=\{S\in\mathcal S_e:S\text{ minimal m-separates }e\text{ trong }P\}.$$

**[Đã kiểm tra bằng định nghĩa]** A_e(P) invariant trong MEC: mọi MAG trong cùng MEC có cùng tất cả m-separations, bao gồm trên mọi proper subset của S. Vì vậy minimality cũng invariant.

Nếu không có ràng buộc lịch sử bổ sung nối các lựa chọn witness, số witness assignments cho cùng P là

$$W(P)=\prod_{e\in Q:\ e\notin E(P)}|A_e(P)|,$$

với factors KEEP cho edges hiện diện bằng 1, và W(P)=0 khi một requirement không thỏa. Nếu đếm row IDs thay vì sets, thay cardinality bằng số rows admissible và ghi rõ đây là một đại lượng khác.

Ý nghĩa thực thi: với P đã cố định, chỉ cần biết mỗi A_e(P) có rỗng không để xác định existence; **không cần materialize tích Descartes**. Phép existential projection này là elementary và liên hệ trực tiếp projected CSP/SAT. Đóng góp chưa được giải là **làm sao tìm các P và maintain supports hiệu quả trước khi biết P**, vượt solver chung.

**Ví dụ xác định rõ nguồn redundancy:** q components dạng đường x_i–a_i–b_i–y_i, không collider; cả {a_i} và {b_i} là minimal separator cho x_i,y_i. Với skeleton/other obligations cố định vào MEC này, có 2^q lựa chọn witness cho cùng một MEC. Đây chứng minh multiplicity có thể exponential trong abstract input; không chứng minh phenomenon phổ biến trong dcFCI. Cần thêm reachable-pool measurement và metadata ablation.

#### D2.3. Làm gì trước khi viết solver lớn?

Stage 1: đối chiếu GPS và projected AllSAT ở cấp task/output; không né baseline bằng cách đổi tên. Stage 2: đo ρ=N_valid distinct-separator-witnesses/N_MEC và chi phí lặp; tạo exhaustive oracle ở p nhỏ; tìm counterexample “same PAG, different future dcFCI transitions”. Stage 3: một graph-specific rule/representation có proof giúp avoid work trước materialization. Stage 4: output-sensitive bound, benchmark ngoài dcFCI, uncertainty coverage under budget. Stage 5: dừng nếu ρ≈1 hoặc mọi gain biến mất khi thêm memoization/projected solver.

**Fatal:** chỉ có contribution “project known encoding”; hoặc target chỉ giải một artificial redundancy không xuất hiện trong lớp ứng dụng. **Manageable:** future-history không merge được — giới hạn theorem ở independent enumeration target và công bố adapter không exact toàn pipeline. **Upside:** theorem về symbolic support/decomposition làm cost phụ thuộc số MEC thay vì multiplicity; phép nén giữ future transitions cho một subclass đã chứng minh.

### D3 — Backup: phân biệt bất định dữ liệu với bất định do search budget

| Hạng mục | Đặc tả |
| --- | --- |
| 1. Title | **When Search Budgets Change Causal Uncertainty: Candidate-Family Effects in PAG Discovery**. |
| 2. Research question | Giữ nguyên dữ liệu và kết quả CI, việc cắt candidate family làm thay đổi ranking/uncertainty vì mất hypotheses đến mức nào; có thể chặn hoặc giảm tác động ấy không? |
| 3. Importance | Người dùng có thể diễn giải tập PAG được search được như toàn bộ bất định được dữ liệu hỗ trợ; computation và statistical evidence cần được phân biệt. |
| 4. Closest works | dcFCI scores; ACI confidence; weighted CI optimization; literature về model/search uncertainty và candidate-dependent scoring cần rà thêm. |
| 5. Exact candidate gap | Quantitative mechanism của family truncation dưới score cụ thể và causal claims. Không claim “score phụ thuộc family” là khám phá, vì dcFCI định nghĩa điều đó tường minh. |
| 6. Scientific contribution | Một counterexample realizable + decomposition/định lượng error do search + correction hoặc reporting rule có tác dụng. Có thể là empirical mechanism study. |
| 7. Theory targets | Điều kiện invariance khi mở rộng family; bounds cho score changes/claim reversals dưới assumptions xác định. Không gọi Fréchet interval là confidence interval cho truth nếu chưa chứng minh. |
| 8. Algorithm | Freeze CI evidence universe; audit nested families; fixed-evidence scoring đối chứng; kiểm tra missing alternatives bằng exact solver nhỏ. |
| 9. Evidence | Oracle/noiseless và finite-sample; exhaustive small truth families; nhiều budgets, seeds và ít nhất một family-search method khác hoặc exact comparator. Measure ranking ties/reversals, truth-class coverage và causal-feature errors. |
| 10. Prerequisites | Hiểu score estimand, CI posterior mapping, model selection và uncertainty evaluation; tránh coi các CI probabilities là joint coherent posterior mặc nhiên. |
| 11. Main risks | Effect đã được biết rõ hoặc chỉ là hệ quả hiển nhiên; counterexample số không realizable; prevalence nhỏ; score phụ thuộc family là mục tiêu thiết kế hợp lý. |
| 12. Smallest complete contribution | Một mechanism mới và có hậu quả thực nghiệm, được tách khỏi noise/graph size, kèm giải pháp hoặc giới hạn sử dụng có thể kiểm tra. Chỉ benchmark sensitivity chưa đủ. |
| 13. Strong outcome | Characterization và estimator/reporting protocol giúp người dùng phân biệt search uncertainty với statistical uncertainty trên nhiều algorithms. |
| 14. Breakthrough target | Anytime bounds cho causal features trên cả explored và unexplored families mà không complete enumeration, dưới assumptions có nghĩa. **Chưa có.** |
| 15. Venue | UAI/AISTATS hoặc journal cho một mechanism study chặt; ICML/NeurIPS nếu kết quả phổ quát và thay đổi cách đánh giá uncertainty. Không bắt buộc algorithm mới. |

Một đối chứng tối thiểu phải tách: (i) giữ cùng query universe, đổi family; (ii) family mới làm thêm query được đưa vào score; (iii) thay CI values do sample noise. Nếu không tách, không biết nguyên nhân ranking thay đổi.

Ở score dạng min-marginal upper bound, thêm một hypothesis mới mà hai graphs cùng chia sẻ có thể kéo cả hai về tie; **không được suy ngay có strict rank reversal**. Phải xây valid MAGs và probabilities từ dữ liệu/mô hình hợp lệ, hoặc công bố rõ counterexample chỉ ở tầng score algebra. Một hiệu ứng thiết kế có chủ ý không tự là bug hoặc statistical failure.

Stage 1: rà các score/uncertainty claims và prior model-selection work. Stage 2: counterexample nhỏ từ valid graphs với CI evidence đóng băng. Stage 3: mechanism + prediction đo được + benchmark có controls + mitigation. Stage 4: nhiều phương pháp và theorem bounds. Stage 5: dừng nếu chỉ có sensitivity hiển nhiên không thay đổi kết luận causal đáng quan tâm.

**Fatal:** không có insight mới ngoài định nghĩa family score. **Manageable:** prevalence tập trung ở near-ties — báo miền áp dụng thay vì bỏ các cases ấy. **Upside:** finite-budget output có thể tạo apparent certainty ngay cả khi CI evidence giữ nguyên; nếu được chứng minh và có remedy sẽ là kết quả có ý nghĩa rộng hơn speedup.

### D4 — Ambitious extension: restricted-CI equivalence cho MAG

| Hạng mục | Đặc tả |
| --- | --- |
| 1. Title | **Restricted Conditional-Independence Equivalence with Latent Confounding**. |
| 2. Research question | Với CI chỉ được biết trên collection C, những lớp MAG nào có thể được biểu diễn bằng một closure graph sound, và khi nào mất khả năng biểu diễn bằng một PAG chuẩn? |
| 3. Importance | Không phải mọi conditioning sets đều đáng tin/đã được test. Cần biết chính xác kết luận nào được suy ra dưới latent confounding từ information budget thực tế. |
| 4. Closest works | k-PC 2023, C-PC 2025, anytime/r-PAG approaches, RFCI, ACI, arbitrary-CI SAT inference. |
| 5. Exact candidate gap | Bỏ causal sufficiency trong C-PC, **trước hết giữ điều kiện pair-complete collection**. Pair-specific masks là bước sau và có thể cần representation khác. Chưa khẳng định gap này chưa có trong toàn bộ literature. |
| 6. Scientific contribution | Representation/characterization cho restricted-CI MAG equivalence, hoặc impossibility + điều kiện bổ sung đủ để có tractable representation. |
| 7. Theory targets | Với M∼C M′ iff mọi CI được phép trùng nhau: xác định closure nào bảo toàn m-separation/ancestry; soundness và phần completeness thật sự đạt. |
| 8. Algorithm | Exhaustive small MAG analysis; thử closure theo C-covered pairs; tìm counterexample trước; chỉ xây orientation procedure sau theorem. |
| 9. Evidence | Oracle recovery của đúng restricted target, rồi finite-sample với CI families do reliability rule xác định; so SAT exact, FCI/RFCI/truncated approach phù hợp. |
| 10. Prerequisites | Latent projection, ancestral graph equivalence, completeness proofs; kiểm tra kỹ assumption nào của C-PC dựa causal sufficiency. |
| 11. Main risks | Kết quả có sẵn hoặc proof C-PC mở rộng gần nguyên xi; không tồn tại compact graph representation; arbitrary masks làm inference quá khó. |
| 12. Smallest complete contribution | Một nontrivial characterization/obstruction cùng sound method cho lớp có ý nghĩa; không đủ nếu chỉ chạy SAT trên CI bị thiếu. |
| 13. Strong outcome | Sound/completeness result cho useful restricted family và algorithm hiệu quả dưới latent confounding. |
| 14. Breakthrough target | Characterization tổng quát cho mask classes, có ranh giới tractability và inference hữu ích ở quy mô lớn. **Không phải lời hứa.** |
| 15. Venue | Phù hợp UAI/AISTATS; có khả năng nhắm ML conference/journal mạnh nếu representation insight sâu. Rủi ro lý thuyết cao hơn D2/D3. |

Target đúng cho query mask Q là

$$\mathcal M_Q=\{M\in MAG(V):\forall q\in Q,\ I_M(q)=I_{obs}(q)\}.$$

Các thành viên có thể khác skeleton; vì vậy **một PAG chuẩn, vốn đại diện một MEC với skeleton chung, không tự biểu diễn M_Q**. Cũng không được lấy union endpoint marks rồi gọi đó là PAG sound/complete. C-PC có một closure construction riêng dưới assumptions của bài; chính việc tìm representation phù hợp mới là phần cần nghiên cứu.

Stage 1: proof-by-proof đối chiếu C-PC, k-PC, r-PAG và SAT. Stage 2: exhaustive small MAGs để tìm counterexample cho naive closure; ưu tiên C pair-complete chứa ∅. Stage 3: một theorem hạn chế hoặc impossibility result hữu ích. Stage 4: algorithm và finite-sample evaluation; mới xét pair-specific masks. Stage 5: dừng như đề tài chính nếu extension chỉ vài sửa ký hiệu, hoặc không thu hẹp được target sau vài tuần proof work.

**Fatal:** closest work đã bao phủ target. **Manageable:** bỏ selection; giới hạn collection; chỉ đảm bảo một loại invariant và ghi rõ. **Upside:** characterization giải thích chính xác vì sao adjacency restriction có thể sai khi CI collection bị hạn chế, đồng thời đưa ra một lớp algorithm thực dụng.

## Report E — Comparative decision matrix

Không chấm điểm 1–5: chưa có dữ liệu đủ để làm các con số ấy có nghĩa. Các khoảng thời gian dưới đây giả định một người nghiên cứu tập trung, có code environment sẵn; là ước lượng công việc, không deadline đảm bảo.

| Tiêu chí | D1: exact extension | D2: distinct-MEC enumeration | D3: budget/uncertainty mechanism | D4: restricted-CI MAG representation |
| --- | --- | --- | --- | --- |
| Problem significance | Có ý nghĩa nếu invalid branches là nút thắt thật. | Cao nếu witnesses che lấp số giả thuyết causal thực; chưa đo. | Có thể cao vì ảnh hưởng diễn giải uncertainty. | Cao về nền tảng: suy luận từ CI hạn chế với latent. |
| Gap defensibility | Yếu cho T1–T3; phải tìm class/theorem mới. | Task khác GPS/MAGLIST; còn phải vượt projected AllSAT. | Code mechanism có thật; novelty của hậu quả còn mở. | Causal-sufficiency gap C-PC đã rõ; extension novelty chưa rõ. |
| Novelty potential | Trung bình đến cao nếu characterization mới; thấp nếu solver thuần. | Đáng kiểm tra, nhờ output object khác witness space; không mới chỉ vì projection. | Cao nếu có failure mechanism chưa biết và remedy; thấp nếu chỉ sensitivity. | Có thể cao nhất, nhưng dễ thành extension đơn giản hoặc quá khó. |
| Technical depth | Graph consistency + decomposition/complexity. | Equivalence classes + symbolic support + enumeration. | Score algebra, inference/uncertainty và causal experimental controls. | Graphical representations và completeness proofs. |
| Theory opportunity | Necessary/sufficient extension, parameterized bounds. | Output-sensitive/delay bounds và representation lower bounds. | Invariance, counterexamples và uncertainty bounds. | Closure equivalence, impossibility, sound/complete inference. |
| Experimental feasibility | Khá tốt với snapshots; exhaustive oracle chỉ p nhỏ. | Khá tốt để đo redundancy; exact set truth đắt khi p tăng. | Tốt cho frozen-evidence pilots; cần dữ liệu realizable. | Oracle enumeration làm được nhỏ; đánh giá quy mô lớn phụ thuộc theorem. |
| Implementation complexity | Cao nếu rollback/global constraints; vừa cho prototype hẹp. | Vừa ở audit, cao ở enumeration engine. | Thấp–vừa ban đầu; mitigation/bounds có thể khó. | Thấp ở counterexample search, cao nếu phát triển algorithm hoàn chỉnh. |
| Resources | CPU/RAM; nhân lực proof là chính. | CPU/RAM, exact solver; chưa có lý do cần GPU. | CPU và các complete small-model libraries. | Chủ yếu thời gian lý thuyết; exhaustive MAG enumeration tốn CPU. |
| Time to first evidence | Khoảng 1–2 tuần cho prune opportunity; theorem chưa định hạn. | Khoảng 1–2 tuần cho multiplicity/cost profile. | Vài ngày–2 tuần cho mechanism counterexample. | Khoảng 1–3 tuần để biết naive extension có trở ngại; positive theorem không định hạn. |
| Fallback nếu hypothesis mạnh sai | Profile/code fixes; giá trị paper riêng thấp. | Benchmark phân rã search cost; chỉ publish nếu insight đủ rộng. | Một negative-result study có giá trị nếu bác được belief quan trọng; không tự bảo đảm. | Impossibility theorem có thể mạnh, nhưng phải hơn phản ví dụ hiển nhiên. |
| Generality/impact | Tốt nếu target độc lập builder. | Tốt cho constrained latent discovery và alternative causal explanations. | Có thể rộng hơn dcFCI nếu replicated mechanism. | Rộng về nền tảng causal discovery dưới thông tin thiếu. |
| Venue fit | UAI/AI/algorithms tùy theorem; ML top-tier có điều kiện. | UAI/AI; ICML/NeurIPS nếu scalable uncertainty exploration + insight. | UAI/AISTATS; ML top-tier nếu mechanism quan trọng và tổng quát. | UAI/AISTATS/theory; top-tier nếu characterization mạnh, liên hệ thực tế rõ. |

**Trade-off quyết định:** D4 hấp dẫn nhất về mặt tham vọng nhưng chưa có đường proof đủ ngắn để khuyên đầu tư ngay. D1 giữ gần code cũ nhất nhưng chịu prior-art pressure mạnh nhất. D3 có first evidence rẻ nhất nhưng dễ thành một observation hiển nhiên. D2 cân bằng hơn vì có target/output rõ, có thể bác bỏ nhanh bằng profile và nối trực tiếp với nguồn lãng phí đang quan tâm.

## Report F — Khuyến nghị chính, dự phòng và mở rộng

**Primary: D2, chỉ ở mức feasibility study 4–6 tuần.** Câu hỏi cam kết kiểm tra là:

> Với các CI constraints và nhiều minimal separator được phép cho mỗi nonedge, liệu có thể tránh chi phí tăng theo số tổ hợp separator bằng cách liệt kê trực tiếp các MEC hợp lệ, nhờ một cấu trúc graph mà projected solvers thông thường chưa khai thác hiệu quả?

Đầu ra mong muốn rất cụ thể: formal target; một exact small-instance oracle; profile witness multiplicity; baseline projected solver; và một lemma/representation mới có ích. **Nếu thiếu lemma/algorithmic insight ngoài projection chuẩn, không nâng nó thành đề tài vài tháng chỉ vì runtime có cải thiện.**

**Backup: D3.** Dùng được phần hạ tầng đo candidate family/CI scores của D2, nhưng chỉ chuyển nếu xuất hiện một effect thay đổi causal conclusions một cách có hệ thống và chưa được literature giải thích. Không gọi lại một optimization không thành công là “empirical paper” nếu không có research finding.

**Ambitious extension: D4.** Có lý do khoa học từ giả định causal sufficiency và pair-complete CI collection của C-PC. Chỉ dành thời gian đọc/proof audit ban đầu; chưa gộp vào D2 thành một framework lớn. Nếu tìm được một obstruction/characterization sắc nét, có thể trở thành đề tài riêng sau thảo luận.

**D1 tiếp tục ở vai trò baseline và công cụ phát hiện cấu trúc.** T1–T3 vẫn hữu ích cho correctness/profiling. Không cần loại bỏ công sức đã làm, nhưng cũng không dùng công sức ấy làm lý do giữ mục tiêu publication cũ.

Vai trò dcFCI trong D2: **application/benchmark**, không phải định nghĩa của scientific problem. Giữ hai tracks tách biệt: exact reference acceleration cho P_ref/full states; và complete mathematical enumeration cho P. Không so recall/completeness của hai tracks như thể cùng một target.

### Điều kiện tối thiểu để tôi đồng ý đầu tư vài tháng

1. **Novelty:** tìm được ít nhất một claim mới ở mức graph representation/algorithm, sau khi đối chiếu projected AllSAT, GPS, MAGLIST và causal SAT/ASP. “Chưa thấy code làm” không đủ.
2. **Need:** reachable data cho thấy chi phí do redundant witnesses đáng kể **sau** pair-domain conversion và memoization hợp lý; không chỉ do duplicate metadata.
3. **Correctness:** exhaustive p nhỏ có zero discrepancy với independent oracle, kèm proof obligations được giải quyết; test không thay proof.
4. **Mechanism:** có giải thích cấu trúc dự đoán khi nào method có lợi, và failure cases phù hợp giải thích ấy.
5. **Competitive evidence:** phương pháp vượt một generic exact projected baseline trên cùng target hoặc có guarantee hữu ích mà baseline không cung cấp với bound tương đương.

Không cần đạt toàn bộ confirmatory benchmark trong 6 tuần, nhưng cần đạt đủ cơ sở cho năm điều kiện này. Nếu không, kết luận đúng là **chưa có đề tài đủ mạnh**, không phải tiếp tục mở rộng scope.

## Report G — Roadmap sáu tuần, ưu tiên phép thử có thể bác bỏ hướng

Đây là **kế hoạch đề xuất**, chưa được thực thi trong review. Các ngưỡng runtime/tỷ lệ dưới đây là tiêu chí ra quyết định của project; nên thống nhất trước pilot xác nhận và không chỉnh sau khi xem kết quả.

| Tuần | Việc làm hữu hạn | Artifact phải có | Go / no-go |
| --- | --- | --- | --- |
| 1 — Target & prior art | Đọc proofs/algorithms GPS, MAGLIST, ASP/Dseptor, projected enumeration. Khóa P hay P_ref, selection assumptions và input encoding. Audit effective separator/history. | Bảng claim-vs-prior-work 1–2 trang; mathematical contract; 3 toy fixtures; danh sách proof obligations. | **No-go novelty** nếu đóng góp dự kiến được solver/framework có sẵn bao phủ toàn bộ và không có insight causal mới khả dĩ. Không cài solver lớn trước bước này. |
| 2 — Cheapest decisive profile | Pin environment; instrument dcFCI/B1; lấy khoảng 16 datasets pilot nhỏ, hai sizes, hai sample sizes, có/không latent, seeds cố định; lưu reachable snapshots. Đếm N_pair, N_history, N_valid_history, N_MEC và exclusive time. | Snapshot archive, cost decomposition, metadata-vs-structural duplicate analysis, caps/timeouts đầy đủ. | Với D2: nếu median ρ<2 **và** duplicated-work fraction<10% ở lớp đích thì dừng runtime hypothesis. Nếu median ρ≥5 và duplicated-work fraction≥30% trên hơn một family, đáng tiếp tục; khoảng giữa cần lý do cấu trúc. Đây không phải universal thresholds. |
| 3 — Exact oracle & counterexamples | Exhaustive MAGs p=3–4, thêm p=5 nếu vừa budget; không-selection trước. Canonicalize MEC; audit minimal separators. Tìm cùng PAG nhưng khác history/next transition. | Ground-truth solution sets; minimized counterexamples; proof của support invariance/product count; adapter contract. | Một false omission là **no-go correctness** cho implementation hiện tại. Nếu full-history merging sai, bỏ claim full dcFCI equivalence; chỉ tiếp tục target độc lập khi đã thống nhất. |
| 4 — Strong baseline trước method lớn | Xây/adapter generic exact SAT/ASP + projected enumeration cho đúng graph class; B1+memoization và T1–T3. Thử một representation/rule graph-specific có proof sketch. | Runtime/space/delay comparison nhỏ; exact output-set equality; lemma phân biệt method với generic baseline. | Nếu baseline chung xử lý toàn bộ interesting cases và đề xuất không có guarantee/insight khác, **không tiếp tục chỉ để đổi solver**. |
| 5 — Falsification & transfer | Graph families đã định trước: sparse random, nhiều alternative minimal separators, ít redundancy, nhiều valid MECs. Test một nguồn constraints ngoài dcFCI; seeds mới, báo regressions. | Performance profiles, coverage-vs-time, failure map; frozen-evidence D3 pilot chỉ khi có tín hiệu. | Mục tiêu thực dụng: ≥2× median end-to-end so strongest same-target baseline trên lớp đích, paired interval vượt 1×, hoặc theorem mở khả năng mới. Gain do caps/cache khác nhau bị loại. 2× riêng nó không đủ novelty. |
| 6 — Decision | Hoàn thiện theorem hoặc xác định chỗ thiếu; viết short paper skeleton, không polish abstract thay proof. Review cả negative evidence. | Decision memo: claim, proof status, first figure, closest baseline, risk; kế hoạch tiếp nếu qua. | **Commit** khi có target rõ + insight mới + correctness + need + competitive evidence. **Pivot D3** chỉ với mechanism mới đáng kể. **Stop** nếu cả hai không đạt; không kéo dài vô hạn. |

**Nếu chỉ có bốn tuần:** gộp tuần 1 với setup; chạy tuần 2–3; tuần 4 kết thúc ở baseline và decision, không tự nhận đã có confirmatory evidence.

Resource policy đề nghị: CPU single-process để audit trước parallel; giới hạn thời gian/RAM cho mỗi run và báo đầy đủ timeout/OOM. Không tăng p cho đến khi correctness nhỏ pass. Không sử dụng GPU. Đánh giá confirmatory sau feasibility dùng graph/data replicates mới, paired comparisons, bootstrap theo graph chứ không theo số candidates trong một graph.

**Ngừng ngay việc quảng cáo exactness** nếu có false pruning, mismatch full-state khi claim reference preservation, hoặc ground-truth converter chưa đáng tin. Sửa và điều tra được coi là công việc verification, không phải một negative research result tự động.

## Report H — Proposed paper positioning cho D2

**Mọi performance/theorem contribution dưới đây là mục tiêu, chưa đạt.** Support invariance và product count ở D2.2 đã có lập luận trực tiếp nhưng quá elementary để đứng một mình làm main contribution.

| Thành phần | Nội dung đề xuất |
| --- | --- |
| Tentative title | **Beyond Separator Witnesses: Exact Enumeration of Causal Equivalence Classes under Latent Confounding**. |
| One-sentence RQ | Làm sao liệt kê đầy đủ, không trùng các MAG MECs thỏa những lựa chọn minimal separator mà tránh công việc tăng theo số witness assignments? |
| Problem statement | Input hard CI/CD, optional skeleton edges và admissible separators; output distinct full MAG MECs satisfying existential separator constraints. Ban đầu không selection, không finite-sample consistency claim. |
| Closest works | GPS: search qua MEC; MAGLIST: list MAG trong một MEC; Hyttinen et al.: exact CI constraints/optimization; projected AllSAT: generic existential projection; dcFCI: motivating candidate search. |
| Core novelty claim — **target** | Một cấu trúc/thuật toán đặc thù MAG duy trì separator support và loại trùng MEC trước khi materialize witnesses, có guarantee và ưu thế so generic projection. Không claim projection hoặc MEC signature mới. |
| Contribution 1 — **target** | Characterization về khi separator supports có thể nén/cập nhật mà giữ đúng tập MEC khả thi, kèm giới hạn hoặc counterexamples của state merging. |
| Contribution 2 — **target** | Exact enumeration algorithm, proof soundness/completeness/no duplicate; output-sensitive hoặc parameterized bound trên lớp công bố rõ. |
| Contribution 3 — **target** | Reproducible study chứng minh source of complexity, đối chiếu generic solvers và đo số causal alternatives có thể khảo sát trong budget. |
| Main theorem — **target** | Trên lớp F được mô tả bằng cấu trúc input, thuật toán xuất đúng P một lần mỗi MEC với delay D(p,L,w) được chứng minh; L là độ dài encoding separator/CI input, w là parameter có định nghĩa rõ. **Chưa có F và D đủ để phát biểu theorem hoàn chỉnh.** |
| Empirical claim — **target** | Redundant witnesses là nguồn chi phí đáng kể trên lớp đích, và representation tránh chúng cải thiện time/memory/delay mà giữ exact solution set. |
| Baselines bắt buộc | Exhaustive small MAG oracle; pair enumeration + orientation/validation khi cùng target; memoization; T1–T3; generic SAT/ASP projected enumeration. GPS/dcFCI chỉ so coverage/runtime như approximate/application baselines nếu target khác; MAGLIST không được giả làm across-MEC enumeration baseline. |
| Metrics | Exact MEC-set recall/precision nhỏ; first-output time, delay distribution, total time, memory, unique outputs/budget; counts ở từng level; end-to-end truth-PAG coverage/SHD nếu có selection rule tương thích. |
| Limitations dự kiến | Số outputs vẫn exponential; generic solvers có thể mạnh hơn; constraints nhiễu có thể inconsistent; không tự kế thừa history-dependent dcFCI semantics; no-selection trước; graph validity không chứng minh causal truth từ finite data. |

**Abstract giả định — 179 từ theo cách đếm khoảng trắng; mô tả mục tiêu, không báo kết quả đã có:**

Trong khám phá nhân quả có biến ẩn, nhiều lựa chọn tập phân tách có thể dẫn đến cùng một lớp tương đương Markov. Nghiên cứu dự kiến xem xét bài toán liệt kê các lớp này dưới những ràng buộc độc lập có điều kiện và các tập phân tách được phép. Mục tiêu là tránh chi phí lặp theo số cách chứng minh cùng một cấu trúc. Chúng tôi sẽ khảo sát biểu diễn tập phân tách hợp lệ theo từng lớp, điều kiện nén chúng, và thuật toán duyệt không sinh kết quả trùng. Tính đúng đắn, đầy đủ và độ phức tạp theo kích thước đầu ra sẽ được phân tích trên lớp đồ thị xác định. Đánh giá dự kiến đối chiếu bộ giải ràng buộc tổng quát, phép liệt kê theo cặp và dcFCI, sử dụng dữ liệu tổng hợp cùng các trạng thái tìm kiếm thực tế. Kết quả mong muốn là xác định khi nào dư thừa biểu diễn hạn chế việc khảo sát các giả thuyết nhân quả khác nhau.

**Lưu ý về định vị:** abstract này chưa thể biến thành abstract kết quả bằng cách đổi “sẽ” thành “đã”. Cần thay F, D, mechanism và empirical claims bằng kết quả thực tế. Nếu đến cuối feasibility vẫn không điền được một main claim cụ thể khác prior art, không nên bắt đầu viết full paper.

## Trả lời câu hỏi quyết định cuối cùng

**Không, tôi chưa đầu tư vài tháng tiếp theo vào Hướng C nguyên trạng nếu mục tiêu là một paper khoa học mạnh.** Nó hiện là một thiết kế optimization và verification tốt, nhưng chưa có bằng chứng bottleneck và chưa có insight mới vượt các phương pháp cấu trúc/CSP đã có.

Tôi sẽ đầu tư **một đợt kiểm chứng có giới hạn** cho câu hỏi D2: **có thể liệt kê trực tiếp các MEC thỏa alternative-separator constraints, không trả chi phí theo số separator witnesses, bằng một cơ chế đặc thù MAG vượt generic projected enumeration hay không?**

Bằng chứng khiến tôi cam kết dài hơn là: redundancy thật trên reachable workloads sau baseline mạnh; một lemma/representation mới không chỉ lặp lại projection; exactness trên small exhaustive oracle; và lợi ích được giải thích, tái lập trên hơn một nguồn constraints. Nếu thiếu các bằng chứng này, tôi sẽ dừng hoặc chuyển sang D3 chỉ khi đã thấy một cơ chế thất bại thống kê/tính toán đủ quan trọng. **Không có lý do khoa học để bảo vệ Hướng C chỉ vì proposal đã được viết kỹ.**
