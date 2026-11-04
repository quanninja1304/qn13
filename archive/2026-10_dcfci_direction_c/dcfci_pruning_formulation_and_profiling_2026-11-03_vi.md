**Hướng C: đặc tả lựa chọn separating sets, pruning và profiling dcFCI**

Ngày: 03/11/2026. Trạng thái: đề xuất lý thuyết và thiết kế thực nghiệm để review; chưa triển khai thuật toán, chưa chạy profiling, chưa có kết quả tăng tốc. Các chứng minh dưới đây áp dụng cho mô hình toán học được phát biểu; chưa phải chứng minh correctness của một implementation mới.

**Đánh giá chính.** Có một thuật toán backtracking cụ thể để nghiên cứu: duy trì những quan hệ bắt buộc đúng trong mọi cách hoàn tất lựa chọn separating sets, suy ra mâu thuẫn sớm, rồi bỏ cả nhánh. Ba quy tắc bên dưới đủ làm nền tảng sound. Chúng là hệ quả của lý thuyết ancestral graph/m-separation đã biết; chưa phải ba định lý mới có thể tự tạo thành contribution. Phần cần khám phá là tính mở rộng của partial assignment khi skeleton còn thay đổi, cùng lợi ích vượt baseline sinh theo cặp.

Không thể hứa loại bỏ hàm mũ trên mọi input trong khi vẫn liệt kê toàn bộ ứng viên hợp lệ. Mục 4 đưa phản ví dụ và định nghĩa các mốc “Eureka” có thể bảo vệ được.

**1. ĐẶC TẢ TOÁN HỌC & LÝ THUYẾT**

**1.1. Chốt đối tượng tối ưu**

Tối ưu một lần mở rộng của một parent ở vòng r. Bước tạo plausible separating sets, tiêu chuẩn CI, ngưỡng certain/uncertain, scoring và chọn parent vòng sau được giữ theo reference. Không đồng nhất bài toán này với liệt kê mọi MAG trong một MEC đã biết.

Nguồn chính là [dcFCI, Algorithm 1, Theorem 3 và Appendix G](../../docs/papers/dcFCI.pdf). Bản mã đã đối chiếu:

- dcFCI: commit a27c495acc28810a1e8e95878d535d90f82faaaf.
- FCI.Utils: commit 361e8904feb448d5d8069af694670e16e96a9e1f.

Hai chi tiết của implementation phải giữ trong contract: builder reset endpoint của parent về adjacency; nhiều certain rows cùng cặp có thể ghi đè separator theo thứ tự. Vì thế không kế thừa mọi orientation của parent, cũng không âm thầm sửa preprocessing riêng trong proposed. [Builder và preprocessing](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/dcFCI.R#L301).

**1.2. Không gian lựa chọn**

Cho V là tập p biến quan sát. Cố định:

- parent skeleton E₀;
- bảng separating sets đã có và history của parent;
- các lựa chọn certain sau preprocessing giống reference;
- các cặp chưa quyết định Q = {e₁,…,e_q}.

Với mỗi cặp e={u,v}, có s_e candidate rows. Ký hiệu:

$$
\mathcal D_e=\{\mathrm{KEEP}\}\cup\{1,\ldots,s_e\},\qquad
S_{e,j}\subseteq V\setminus\{u,v\}.
$$

Giá trị j nghĩa là xóa cạnh e và gán separating set S_{e,j}; KEEP nghĩa là giữ cạnh trong ứng viên của vòng hiện tại. Candidate mới ở vòng r có kích thước r; separating sets kế thừa có thể nhỏ hơn. Dùng row ID thay vì chỉ tập S để giữ thông tin history cho đến đúng bước dedup của reference.

Không lấy union các S_{e,j} để thay separator được chọn. Union ở các công thức sau chỉ dùng kiểm tra membership chung trong domain.

Không gian theo cặp:

$$
\Omega_{\rm pair}=\prod_{e\in Q}\mathcal D_e,\qquad
N_{\rm pair}=\prod_{e\in Q}(1+s_e).
$$

Nếu m=Σ_e s_e, baseline power set sinh 2^m tập row IDs, rồi loại các tập chọn hơn một row cho cùng cặp.

**Mệnh đề 0 — Tương đương phép sinh theo cặp.** Với preprocessing certain và thứ tự row đã cố định, có song ánh giữa các tập con của m uncertain rows chứa tối đa một row mỗi cặp và các vector z∈Ω_pair.

**Chứng minh.** Một cặp không có row trong tập con ứng với KEEP; một cặp có row j ứng với j. Ánh xạ ngược lấy các row được chọn. Hai ánh xạ là nghịch đảo. Kết quả chỉ nói về phép sinh trước dedup toàn cục và graph validation, không khẳng định mọi cấu hình đều là PAG hợp lệ. ∎

Đây là baseline V1, không nên xem là contribution lý thuyết mới.

Với z hoàn chỉnh, skeleton ứng viên là:

$$
E(z)=E_0\setminus
\bigl(E_{\rm certain}\cup\{e\in Q:z_e\ne\mathrm{KEEP}\}\bigr).
$$

Sep(z) gồm separating sets kế thừa, effective certain separators và những S_{e,z_e} mới chọn. Builder, orientation, validator và history cùng xác định trạng thái ứng viên, không chỉ E(z).

**1.3. PAG hợp lệ đòi hỏi gì?**

MAG là graph có các cạnh directed, bidirected và, khi cho phép selection, undirected. Với cạnh u–v, arrowhead tại u cấm u là ancestor của v. Một MAG phải ancestral và maximal. PAG chuẩn biểu diễn một MEC: cùng skeleton, còn tails/arrowheads là những endpoint bất biến trong MEC. [Zhang, Causal Reasoning with Ancestral Graphs](https://www.jmlr.org/papers/v9/zhang08a.html).

| Lớp điều kiện | Phát biểu cần kiểm tra |
| --- | --- |
| Ancestral | Không có directed cycle; không có đường u→…→v cùng arrowhead tại u trên cạnh uv |
| Khi có undirected edges | Nếu u–v là tail–tail, u và v không được nhận arrowhead trên cạnh khác |
| Maximal | Mỗi cặp không kề nhau có một m-separator; tương đương không có inducing path nối hai đỉnh không kề |
| Separating sets | Mỗi S đã chọn thực sự m-separate đúng hai đỉnh; nếu yêu cầu minimality thì không có proper subset của S cũng tách được cặp đó |
| MEC/PAG | Collider consistency chưa đủ; còn các colliders có order/discriminating paths và đúng những endpoint bất biến của MEC |

Không có một điều kiện tiêu chuẩn độc lập gọi là “tính đầy đủ của ancestor” theo nghĩa phải thêm cạnh cho mọi quan hệ tổ tiên. A→B→C không bắt buộc có cạnh A→C. Cần phân biệt: tính ancestral, tính maximal, và completeness của orientation rules. [Ali–Richardson–Spirtes, Markov equivalence for ancestral graphs](https://arxiv.org/abs/0908.3605); [Zhang, orientation completeness](https://www.sciencedirect.com/science/article/pii/S0004370208001008).

Đối với MAG M, một đường là m-connecting given S khi mọi noncollider trong đường nằm ngoài S và mọi collider thuộc An_M(S), tính cả S. Không có đường như vậy thì hai đầu m-separated. Với yêu cầu minimal separator:

$$
x\perp_m y\mid S,\qquad
\forall T\subsetneq S:\ x\not\perp_m y\mid T.
$$

Không dùng monotonicity giả: conditioning thêm biến không luôn bảo toàn independence.

Để chứng minh pruning, không cần kiểm tra đầy đủ mọi điều kiện trên ở từng prefix. Chỉ cần phát hiện một điều kiện cần chắc chắn bị vi phạm. Validator đầy đủ vẫn giữ ở leaf.

**1.4. Partial state: những gì được phép dùng để suy luận**

Một trạng thái σ chứa residual domains không rỗng D_e^σ⊆D_e. Singleton là đã gán; domain rỗng là thất bại ngay.

Đặt:

- Ω(σ)=∏_e D_e^σ: các complete assignments còn được xét.
- K_σ: các cạnh có mặt trong mọi z∈Ω(σ).
- N_σ: các cặp vắng mặt trong mọi z∈Ω(σ).
- U_{v|u}^σ⊆{T,H}: domain endpoint tại v trên cạnh uv; T là tail, H là head.
- NC_σ(a,b,c): triple bắt buộc là noncollider.
- R_σ(x,y): có đường directed bắt buộc từ x đến y.

Đối với một cặp undecided: D_e^σ={KEEP} làm e thuộc K_σ; KEEP∉D_e^σ làm e thuộc N_σ. Domain gồm KEEP lẫn separator chưa xác định adjacency. Một nonedge do fixedGaps hoặc entry separator bị thiếu không được tự gán separator rỗng; chỉ dùng CI có witness thực sự đã được xác định.

Endpoint domains của solver không phải dấu circle của một PAG chuẩn. Một domain {T,H} có nghĩa solver chưa loại được giá trị nào, không chứng minh tồn tại cả hai loại MAG completion.

**Invariant bắt buộc:** mọi mark, NC và quan hệ R dùng để prune phải là hệ quả của các lựa chọn đã cố định/residual domains, đúng trong mọi MAG completion hợp lệ. Không dùng:

- cạnh hiện có nhưng vẫn có thể xóa;
- endpoint của parent chưa suy ra lại;
- orientation từ một cách điền tạm các lựa chọn chưa quyết định.

“Bắt buộc” chỉ xét trong các completion của vòng hiện tại. Khi sang vòng tiếp theo phải dựng lại các premises phù hợp.

Để viết chứng minh, định nghĩa một relaxation:

$$
\mathcal W(\sigma)=
\{(z,M):z\in\Omega(\sigma),\
M\text{ là MAG có skeleton }E(z),\
M\models\operatorname{CI}(\operatorname{Sep}(z))\}.
$$

Có thể thêm minimality vào W, nhưng ba pruning rules dưới đây không cần nó. W có thể chứa cấu hình mà builder/validator dcFCI sẽ loại. Vì vậy:

$$
\mathcal W(\sigma)=\varnothing
\quad\Longrightarrow\quad
\text{không có completion đúng về mặt đồ thị trong nhánh}.
$$

Chiều ngược lại không được giả định.

**1.5. Định đề T1 — Xung đột collider–noncollider bắt buộc**

Giả sử ab,bc∈K_σ và ac∈N_σ. Gọi S_ac^σ là họ separator còn có thể chọn cho ac, không rỗng và không chứa KEEP.

Nếu:

$$
b\notin\bigcup_{S\in\mathcal S_{ac}^{\sigma}}S,
$$

thì mọi completion hợp lệ có collider tại b:

$$
H_{b|a}\land H_{b|c}.
$$

Nếu:

$$
b\in\bigcap_{S\in\mathcal S_{ac}^{\sigma}}S,
$$

thì mọi completion hợp lệ phải thỏa:

$$
NC(a,b,c)
\equiv\neg(H_{b|a}\land H_{b|c}).
$$

**Prune** nếu solver đã suy ra NC(a,b,c) cùng cả hai arrowheads H_{b|a},H_{b|c}.

**Chứng minh.** Chọn một completion bất kỳ. Hai cạnh ab,bc vẫn tồn tại và S_ac vẫn là separator. Nếu b∉S_ac mà b là noncollider, đường hai cạnh a-b-c mở. Nếu b∈S_ac mà b là collider, chính b kích hoạt đường đó. Cả hai trái m-separation. Vì membership đồng nhất trên toàn domain nên kết luận áp dụng cho mọi completion. Yêu cầu đồng thời collider và noncollider là bất khả thi. ∎

Khi membership còn lẫn lộn, chưa được chọn một trong hai kết luận. Không suy luận bằng union trong trường hợp cần intersection hoặc ngược lại. Kiểm tra domain rỗng trước các điều kiện “mọi S”.

**Ví dụ để kiểm tra logic, chưa phải dữ liệu benchmark:** các cạnh ab,bc,bd chắc chắn còn; chọn ba nonedges:

$$
S_{ac}=\{b\},\quad S_{ad}=\{t\},\quad S_{cd}=\{t\},\quad t\ne b.
$$

CI của ad ép head vào b trên ab; CI của cd ép head vào b trên cb; CI của ac đòi a-b-c là noncollider. Nhánh này vô nghiệm. Các separator cùng kích thước 1. Cần kiểm tra riêng bộ tạo plausible separators của dcFCI có thực sự sinh những pool tương tự từ dữ liệu hay không; không được dùng fixture này làm bằng chứng hiệu quả thực tế.

**Propagation rẻ đi kèm:** nếu H_{b|a} và NC(a,b,c), endpoint tại b trên bc phải là tail. Vì b đã nhận một arrowhead, bc không thể là tail–tail ngay cả khi selection được phép; do đó b→c. Kết luận chỉ dùng khi các cạnh và premises đều persistent.

**1.6. Định đề T2 — Xung đột ancestry**

Xây D_σ từ các cạnh bắt buộc có tail ở đầu đi và head ở đầu đến. R_σ là transitive closure độ dài dương của D_σ.

**Prune** nếu một trong các điều kiện sau xảy ra:

$$
\exists x:\ R_\sigma(x,x),
$$

hoặc:

$$
\exists x,y:\ R_\sigma(x,y)\land xy\in K_\sigma
\land H_{x|y}.
$$

Thêm điều kiện khi cho phép selection: một cạnh bắt buộc tail–tail incident vào x không được cùng tồn tại với một arrowhead bắt buộc incident vào x.

**Chứng minh.** Mọi completion phải giữ các directed paths và endpoint vừa nêu. Điều kiện thứ nhất là directed cycle. Điều kiện thứ hai đồng thời yêu cầu x là ancestor của y và arrowhead tại x trên xy, trái định nghĩa ancestral. Điều kiện tail–tail vi phạm quy tắc của undirected edge trong ancestral graph. ∎

Ví dụ: x↔y cùng x→z→y đã không hợp lệ, dù directed subgraph không có cycle. Vì vậy chỉ dùng kiểm tra DAG cycle là thiếu.

Nếu chỉ có đường *possibly directed*, chưa được áp T2. Một cách hoàn tất có thể ngăn quan hệ ancestry. T2 dùng đường directed đã bị ép, không dùng đường “có vẻ sẽ hướng được”.

**1.7. Định đề T3 — Đường m-connecting bắt buộc trái separator**

Giả sử đã chọn cố định x⊥y|S. Nếu có một simple path π từ x đến y sao cho:

1. Tất cả các cạnh thuộc K_σ.
2. Mỗi đỉnh nội bộ v chắc chắn là noncollider trên π và v∉S; hoặc chắc chắn là collider và v∈S hay có đường directed bắt buộc đến một s∈S.

thì nhánh vô nghiệm.

**Chứng minh.** Trong mọi MAG completion, π vẫn tồn tại; các noncollider không bị chặn, còn mọi collider được kích hoạt. Vì vậy π m-connecting given S trong mọi completion, trái CI đã chọn. ∎

Nếu separator chưa cố định, chỉ loại giá trị S có witness vi phạm. Muốn bỏ toàn bộ nhánh phải loại hết domain hoặc có chứng minh cho mọi S còn lại.

T3 không cần minimality. Nhưng tìm mọi simple path có thể rất tốn kém. Phiên bản đầu chỉ tìm witness ngắn, ví dụ tối đa 3 hoặc 4 cạnh, hoặc tái sử dụng witness đã có. Giới hạn độ dài làm giảm sức prune, không làm mất soundness: không tìm thấy witness thì tiếp tục search.

**Maximality vẫn cần kiểm tra.** Có thể bổ sung rule: nếu có inducing path bắt buộc giữa hai đỉnh chắc chắn không kề nhau thì prune vì mọi completion non-maximal. Tìm và cập nhật các witness này là một hướng nâng cấp; không mặc nhiên có chi phí thấp. Ba rules T1–T3 không phải bộ điều kiện đủ của valid PAG.

**1.8. Dữ liệu và thuật toán cần xây**

| Dữ liệu | Biểu diễn đề nghị | Công dụng/chi phí cần kiểm soát |
| --- | --- | --- |
| Residual domains | Bitset các row ID, KEEP là một giá trị riêng | Xóa/khôi phục lựa chọn; ghi số giá trị còn lại |
| Separating sets | Bitset p bit, giữ row ID và thứ tự reference | Kiểm tra b∈S; tính union/intersection membership qua domain |
| K,N | Hai ma trận/bitset đối xứng, phân biệt cặp chưa quyết định | Chỉ tạo unshielded triple khi ba premises ổn định |
| Endpoint domains | Hai bit {T,H} cho mỗi ordered endpoint | Unit propagation; domain rỗng là conflict |
| Noncollider clauses | Mệnh đề cấm hai arrowheads cùng vào đỉnh giữa, indexed theo endpoint | Cập nhật khi một mark bị ép |
| Forced reachability | Bitset descendants/ancestors, kèm undo trail | T2; không hứa O(1) cho update transitive closure |
| Supports | ID lựa chọn/premise tạo mỗi suy luận | Giải thích conflict và undo đúng khi backtrack |
| Witness cache | Triple/path và premises còn cần đúng | T1/T3, invalidation theo support |
| Leaf identity | Separators, history và metadata ảnh hưởng vòng sau | Không dedup chỉ bằng endpoint matrix |

Đối với p nhỏ, recompute reachability O(p³) khi một batch marks đổi là baseline dễ audit. Sau đó mới so incremental bitsets. Một lần thêm directed edge có thể ảnh hưởng Ω(p²) cặp reachability; rollback phải khôi phục cả các bits và supports.

Ví dụ logical nogood: nếu một conflict được suy ra từ literals L={z_e₁=j₁,…,z_eₖ=jₖ}, lưu ¬(∧L). Mọi nhánh chứa toàn bộ support bị loại. Nếu premise là một residual-domain restriction, support phải ghi restriction đó; không thay nó bằng một assignment không tương đương. Không cần tìm minimal conflict ngay từ đầu.

Pseudocode:

    Enumerate(parent, pools):
        sigma = InitWithReferencePreprocessing(parent, pools)
        Search(sigma)

    Search(sigma):
        PropagateStableTriplesAndEndpointDomains(sigma)
        UpdateForcedReachability(sigma)
        if EmptyDomain or T1 or T2 or EnabledT3Witness:
            RecordConflictWithSupport()
            return

        if EveryPairAssigned:
            candidate = ReferenceBuildRawState(sigma)
            EmitUnprunedRawState(candidate)
            return

        e = ChoosePair(sigma)
        for value in ReferenceCompatibleOrder(D[e]):
            marker = TrailPosition()
            RestrictDomain(e, {value})
            Search(sigma)
            UndoTo(marker)

    After every parent has been expanded:
        ApplyReferenceDedupInReferenceOrder()
        ReferenceOrientationValidationAndMECScoring()
        IncludeCarriedParentsExactlyAsReference()
        ScoreSameValidFamily()
        SelectWithReferenceTieSemantics()

Giữ dedup toàn cục trước full validation/MEC scoring như reference. Raw builder chỉ tạo skeleton/sepset/history. Chạy validator ở từng leaf trước dedup có thể làm lặp công việc và đổi số actual CI executions; không dùng thứ tự ấy để benchmark mà gọi downstream “giữ nguyên”.

Ban đầu branch order cố định để tách tác động pruning. Sau đó ablate: smallest domain; ưu tiên cặp tham gia nhiều triples chưa hoàn tất; hoặc dự đoán khả năng tạo conflict. Một heuristic chỉ thay thứ tự không được tự bỏ giá trị.

Đây là **constraint-pruning backtracking**. Chưa gọi là score-based branch-and-bound. Score dcFCI so sánh hypotheses giữa cả họ candidate; score trên danh sách chưa hoàn tất chưa phải upper bound admissible. [Family-dependent scoring](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/score_utils.R#L290).

**1.9. Bảo đảm có thể phát biểu chính xác**

Gọi F_ref(z) là leaf acceptance thực tế của reference. Gọi F_math(z) là tính khả thi theo MAG/PAG semantics.

T1–T3 chứng minh:

$$
\operatorname{Prune}(\sigma)
\Rightarrow
\forall z\in\Omega(\sigma):F_{\rm math}(z)=0.
$$

Để suy ra không mất một leaf reference chấp nhận, cần thêm:

$$
F_{\rm ref}(z)=1\Rightarrow F_{\rm math}(z)=1.
$$

Nếu validator gốc có bug, hai phát biểu không tự đồng nhất. Một discrepancy phải được điều tra trước khi claim equivalence; không chỉnh proposed để giữ một graph sai rồi gọi đó là soundness.

**Định lý bảo toàn có điều kiện.** Giả sử preprocessing/pools giống nhau; mọi propagation sound; validator reference không nhận cấu hình vi phạm semantics dùng trong proof; các lựa chọn không bị prune đều được liệt kê; downstream dedup/score/ties/cache semantics được giữ; không có cutoff thay đổi bài toán. Cần thêm dedup key không gộp một raw state valid với một raw state invalid, và representative của nhóm valid giữ đúng thứ tự reference. Khi đó proposed và reference giữ cùng tập trạng thái hợp lệ và chọn cùng output ở mọi vòng.

**Chứng minh.** Với một trạng thái hợp lệ z, tại mọi prefix theo đường đến z, z là một completion khả thi, nên T1–T3 không thể prune prefix đó. Backtracking xét mọi giá trị còn lại nên đến z. Các trạng thái emitted đều qua validator gốc. Hai tập trạng thái sau cùng bằng nhau; cùng downstream operations cho cùng output. Quy nạp theo các vòng r. ∎

Đây là preservation của search, mạnh hơn chỉ so SHD nhưng không phải bảo đảm mới về truth từ dữ liệu hữu hạn. Theorem 3 của dcFCI còn điều kiện true r-PAG nằm trong nhóm được giữ qua các vòng; proposed chỉ kế thừa điều kiện ấy khi output thật sự tương đương.

**2. THIẾT KẾ THỰC NGHIỆM & PROFILING**

**2.1. Không đặt trước kết luận bottleneck**

Mục tiêu là xác định nút thắt, không phải chứng minh bằng mọi giá rằng power set là thủ phạm. Cần phân biệt:

$$
T=T_{\rm pools}+T_{\rm enum}+T_{\rm build}+T_{\rm orient}
+T_{\rm validate}+T_{\rm score}+T_{\rm select}+T_{\rm overhead}.
$$

Statistical CI có thể xuất hiện trong pools và score. Đo nó như thành phần con của phase, không cộng thêm lần nữa gây double counting.

Một phát hiện từ đọc source: isValidPAG dựng canonical MAG và dựng lại PAG bằng graph oracle. Vì thế graph validation có thể tốn nhiều thời gian dù không chạy CI thống kê mới. [FCI.Utils validity](https://github.com/adele/FCI.Utils/blob/361e8904feb448d5d8069af694670e16e96a9e1f/R/utils.R#L471).

Minimality checking trong dependency có duyệt proper subsets của S và tìm đường m-connecting. Do đó không lấy một bound per-candidate của paper rồi mặc nhiên áp cho mã R hiện tại. [FCI.Utils minimality](https://github.com/adele/FCI.Utils/blob/361e8904feb448d5d8069af694670e16e96a9e1f/R/metrics.R#L233).

**2.2. Các điểm instrumentation**

| Phase | Điểm bám | Counters ngoài thời gian |
| --- | --- | --- |
| Candidate CI pool | getOrdPotSepsets/getCITestResults | p,r,q,m,s_e; số certain/uncertain |
| Generation | powerSet hoặc generator V1/V2 | Raw subsets/configurations; partial states; depth |
| Pair filter/build | checkSepsetResults/createToProcessPAGList | Duplicate-pair rejects; candidates allocated |
| Orientation | udag2pag | Số closure calls; endpoint changes |
| Validity/minimality | hasViolation/isValidPAG | Calls; reject reason; graph-oracle queries; subset/path work |
| Scoring/MEC | getMEC/updateSkelScore/getSymmDiffCITestResults | New statistical CI; cache requests; family size |
| Dedup/ranking | getUniquePAGList/rankPAGList/getTopPagIds | Distinct full states; duplicates; ties; selected depth |
| Pruning | T1/T2/T3, trail, nogoods | Rule hits; support size; visited nodes; eliminated subtree mass |

Đo exclusive/self time bằng sampling profiler và timers theo phase. Runtime cuối dùng uninstrumented build hoặc instrumentation nhẹ đã đo overhead. Memory cần peak RSS của cả process chính lẫn workers; object.size không thay được peak process memory.

Tách ít nhất sáu bộ đếm:

$$
N_{\rm request},\ N_{\rm cachehit},\ N_{\rm precomputedhit},\
N_{\rm stat\_exec},\ N_{\rm stat\_unique},\ N_{\rm graphoracle}.
$$

Key CI thống kê:

$$
(\text{data/test identity},\min(x,y),\max(x,y),\operatorname{sort}(S)).
$$

Trong một run cố định data và test, ba thành phần cuối đủ làm query key. Với graph oracle, key phải thêm identity của graph; cùng (x,y,S) trên hai MAG không phải cùng query.

Cache hiện tại có thể dẫn đến lặp actual CI executions giữa candidate dù query keys trùng nhau. Do đó N_stat_unique không thay thế N_stat_exec. [CI/cache implementation](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/citest_utils.R#L34).

**Kỳ vọng cần nêu trước:** pruning những candidate bị loại ở graph validation thường không giảm CI thống kê tại scoring, vì chúng vốn không tới scoring. N_stat_exec có thể giữ nguyên trong khi N_graphoracle, số PAG constructions và runtime giảm mạnh. Đây là kết quả hợp lệ, không phải thất bại.

**2.3. Hai lớp thí nghiệm**

**Lớp A — Replay một vòng.** Lấy snapshot từ một lần chạy thật, lưu parent đầy đủ, r, candidate rows, thresholds và CI lookup cần thiết. Ba biến thể nhận cùng snapshot. Mục đích: cô lập generation/validation và kiểm tra theorem trên pool reachable. Fixture tự tạo chỉ là unit test logic, báo riêng.

Một CI table cố định dùng ở replay không có cùng chi phí với kiểm định trên dữ liệu. Không dùng tốc độ replay để thay cho end-to-end runtime.

**Lớp B — End-to-end.** Cùng dataset, CI test, parameters, seeds, dependency versions, memory/CPU limits; bắt đầu cold cache giống nhau. Đầu tiên single process; sau đó parallel cùng số workers. Không cho proposed nhiều core hơn hoặc dùng cache mạnh hơn riêng.

**Các biến thể chính:**

| Biến thể | Generation | Structural pruning | Downstream |
| --- | --- | --- | --- |
| B0 — dcFCI reference | Power set + duplicate-pair filter | Không thêm | Builder/validator/scorer đã pin |
| B1 — Pair configurations | Tích các domain {KEEP, separator IDs} | Không thêm | Giống B0 |
| B2 — Proposed | Backtracking trên cùng domain | T1+T2; T3 là ablation | Giống B0 |

Các ablations: B2 chỉ T1; chỉ T2; T1+T2; thêm T3; thêm nogoods; thêm branch heuristic. Dùng cùng leaf ordering/canonical ordering khi nó ảnh hưởng ranking/ties.

Thêm baseline memoization đơn giản nếu profiling cho thấy lặp graph validation chiếm phần lớn. Nếu solver CSP/SAT thích hợp có thể mã hóa cùng các constraints, đưa vào đối chiếu; không so hai phương pháp giải hai bài toán khác nhau.

**2.4. Dữ liệu và quy mô**

Triển khai theo thứ tự sau sau khi thống nhất thiết kế:

1. **Audit nhỏ:** p=4–6; candidate pools nhỏ đủ vét cạn. Bao gồm empty domain, duplicate/certain rows, nhiều separators/cặp, ambiguity membership, selection edge cases nếu backend cho phép.
2. **Pilot reachable pools:** một lưới nhỏ p∈{5,8}, n∈{200,1000}, latent fraction∈{0,0.3}, expected observed degree thấp; ví dụ 2 seeds/cell tạo 16 datasets. Mục tiêu là kiểm tra chi phí và tỷ lệ rules kích hoạt, chưa phải xác nhận scientific claim.
3. **Confirmatory:** cố định trước graph families và điều kiện sau pilot; dùng seeds mới, ít nhất 20 graph/data replicates mỗi cấu hình đã chọn. Tăng p lên 12/20 khi resource budget cho phép. Công bố cả timeout/OOM/capped cases.

Graph families cần có:

- Sparse random DAGs có latent projection.
- Modular graphs với nhiều triples dùng chung cạnh, để kiểm tra khả năng phát hiện xung đột sớm.
- Trường hợp ít uncertain choices hoặc ít xung đột, để đo overhead.
- Trường hợp có nhiều valid candidates, để kiểm tra giới hạn pruning.

Không đặt tên lớp “graph thuận lợi” bằng chính việc B2 đã đạt 90% prune. Định nghĩa lớp theo cấu trúc hoặc tham số sinh trước khi xem kết quả xác nhận. Khác biệt giữa Gaussian/mixed-data CI thuộc trục chi phí test; bắt đầu Gaussian, rồi mới mở rộng sang mixed nếu cần claim rộng.

Ground truth phải lấy từ latent projection của DAG sinh dữ liệu và bộ chuyển MAG→PAG độc lập. Không dùng riêng validator của proposed để xác nhận truth cho chính proposed.

**2.5. Metrics và output equality**

Để tránh mơ hồ về SHD cho PAG, đăng ký hai metric:

$$
\mathrm{SHD}_{\rm pair}(P,Q)=
\sum_{i<j}\mathbf 1[\ell_P(i,j)\ne\ell_Q(i,j)],
$$

trong đó ℓ là “absent” hoặc ordered pair hai endpoint marks theo thứ tự node cố định; mỗi cặp sai tính một đơn vị.

$$
\mathrm{EHD}(P,Q)=
\sum_{i\ne j}\mathbf 1[M^P_{ij}\ne M^Q_{ij}],
$$

với M_{ij} là mark tại j trên cạnh ij và 0 nếu không có cạnh. EHD tính riêng endpoint; edge thêm/xóa thường tạo hai sai khác. Không gọi hai metric này là cùng một convention SHD.

Nếu package có metric SHD khác, lưu tên hàm/phiên bản/convention và báo thêm, không trộn các định nghĩa.

Với output nhiều PAGs: primary dùng một top-ranked PAG được chọn bằng rule canonical cố định; báo thêm tập output, kích thước và khoảng SHD. “Best SHD trong output” dùng truth để chọn nên chỉ là diagnostic, không phải metric chính.

Với r bị giới hạn, báo rõ depth; có thể thêm truth r-PAG phù hợp. Không gộp baseline bị dừng ở r thấp với proposed chạy đủ rồi tuyên bố cùng output task.

| Nhóm | Chỉ tiêu |
| --- | --- |
| Runtime | Wall time paired, CPU time, median/geometric mean speedup B0/B1 và B1/B2 |
| Memory | Peak RSS toàn bộ process tree; OOM rate |
| CI | Sáu counters ở trên và thời gian theo loại query |
| Search | N_pair, N_valid, N_invalid, visited prefixes, prune depth, rule cost |
| Exactness | Same full candidate states, same score vectors, same selected state IDs/output |
| Accuracy | SHD_pair/EHD tới truth; discrepancy B2-vs-B1 phải bằng 0 khi claim exactness |
| Completion | Completed r, timeout/cap status; số run đủ ngân sách |

Equal SHD tới truth không chứng minh equal PAG. Equal PAG matrix cũng chưa chứng minh equal state nếu separating sets/history ảnh hưởng vòng sau.

**2.6. Những semantics dễ làm benchmark sai**

Reference có cap và đường xử lý verbosity ảnh hưởng control flow; sel_top cũng có ties/selection phụ. Tất cả phải khóa và log. Run chạm cap không được tính như một exact completed run. Nếu cần reference “không cap” cho replay nhỏ, áp cùng thay đổi cho mọi variant và ghi rõ đây là cấu hình thí nghiệm. [Vòng xử lý candidate/cutoff](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/dcFCI.R#L555).

Không thay đổi ngưỡng certain, alpha hoặc maximum conditioning size riêng cho B2. Không lặng lẽ dedup những states chỉ vì chúng có cùng PAG nếu reference giữ history khác nhau.

Mỗi workload có warm-up như nhau, sau đó đo lặp với thứ tự B0/B1/B2 được hoán đổi. Dùng paired graph/data seeds và khoảng tin cậy bootstrap theo graph; không coi hàng nghìn candidate trong cùng graph là các dataset độc lập. Kiểm tra instrumentation overhead riêng.

**2.7. Quyết định bottleneck bằng số liệu**

Gọi f là tỷ lệ thời gian B1 nằm ở phần B2 có thể tránh, ví dụ build/orient/validate các leaf chắc chắn invalid. Ngay cả khi bỏ được toàn bộ phần ấy với overhead bằng 0:

$$
\mathrm{Speedup}_{\max}\le\frac{1}{1-f}.
$$

Nếu f=0.10, trần lý tưởng khoảng 1.11×. Khi ấy một pruning engine phức tạp khó đáng làm cho runtime.

Điều kiện lợi ích thực:

$$
T_{\rm avoided\ build/orient/validate}
+T_{\rm enumeration\ saved}
>
T_{\rm propagation}+T_{\rm trail}+T_{\rm nogood}.
$$

Không viết tiêu chí chỉ theo “CI tests tiết kiệm” vì nguồn tiết kiệm chính có thể là graph work.

**3. KỊCH BẢN THẤT BẠI & ĐIỀU KIỆN NÊN BỎ**

| Trường hợp | Chẩn đoán | Quyết định |
| --- | --- | --- |
| Statistical CI/pool generation chiếm gần hết thời gian | f của phần invalid-candidate work nhỏ; trần Amdahl thấp | Không tiếp tục hứa tăng tốc lớn bằng pruning |
| Rules chỉ kích hoạt sát leaf | Rất ít persistent premises ở đầu search; subtree bị bỏ nhỏ | Thử branch order/nogood với ablation; dừng nếu overhead vẫn cao |
| B1 thu gần hết lợi ích | B2/B1 gần 1 hoặc chậm hơn | Xem như engineering improvement, không gọi theorem contribution |
| T1/T2 hầu như không kích hoạt ở pool thật | Bộ tạo plausible sets đã loại các xung đột ấy | Cần quy tắc mới mạnh hơn hoặc pivot; fixture artificial không cứu claim |
| Hầu hết ứng viên đều valid | Output size lớn, ít wasted work | Pruning không thể giúp nhiều; compact representation/top-k là bài toán khác |
| Reachability/path checking quá đắt | T_rule > chi phí avoided leaves | Giảm tần suất/độ dài witness hoặc bỏ rule |
| Solver chung/memoization đạt tương đương | Không có lợi thế đặc thù graph | Novelty yếu; cần characterization mới hoặc thay mục tiêu |
| B2 mất một accepted state | Prune dùng cạnh không persistent, orientation sai support hoặc rollback lỗi | Dừng mọi claim exactness; tạo minimal counterexample |
| Family giống nhưng score khác | History, ties, dedup, CI cache hoặc family ordering thay đổi | Sửa semantics trước performance benchmark |
| SHD tốt hơn nhưng output khác | Có thay đổi search/scoring, không phải exact speedup | Có thể là đề tài khác; cần thảo luận trước khi đổi claim |
| Chỉ nhanh nhờ cap/threshold nhỏ hơn | Bài toán/độ sâu đã khác | So lại cùng ngân sách và semantics |
| Cần dựa vào vài motif tự dựng mới có lợi | Chưa có bằng chứng lớp input thực tế đáng quan tâm | Hạ claim hoặc dừng |

Các mốc pilot để thảo luận, không phải quy luật khoa học: nếu ≥50% thời gian B1 là invalid-candidate work thì đáng thử; nếu <10% thì lợi ích runtime rất khó lớn. Khoảng giữa cần dùng profile chi tiết và overhead estimate. Chọn ngưỡng cuối trước confirmatory experiments.

**Novelty audit bắt buộc.** [MAGLIST, ICML 2024](https://proceedings.mlr.press/v235/wang24o.html) đã dùng đặc trưng cấu trúc để liệt kê MAG hiệu quả trong một MEC. Hướng này khác ở việc lựa chọn separator làm thay đổi skeleton/MEC. Vì vậy claim mới phải gắn với partial separator assignments hoặc lớp graph cụ thể; “kiểm tra graph constraints trước khi dựng graph” quá rộng.

T1–T3 là safe baselines/corollaries của kiến thức đã có. Để scientific contribution cao, cần ít nhất một trong: characterization mạnh hơn cho extendibility; bound theo tham số cấu trúc; hoặc một kết quả thực nghiệm và thuật toán đủ lớn, ổn định, giải thích được, vượt các baseline đơn giản.

**4. ĐIỂM EUREKA**

**4.1. Vì sao không thể hứa đa thức trên mọi input**

Xét 2q đỉnh, chia thành q cặp (a_i,b_i). Mọi cặp khác chắc chắn không kề nhau và có empty separator. Mỗi cặp còn lại có:

$$
z_i\in\{\mathrm{KEEP},\mathrm{DELETE}(\varnothing)\}.
$$

Mỗi z cho một PAG là matching của các cạnh circle–circle được giữ và các đỉnh cô lập. Có 2^q skeleton khác nhau; tất cả đều là PAG hợp lệ và các nonedges được tách bởi empty set.

Vì vậy, một generator phải xuất đầy đủ họ này có lower bound Ω(2^q) chỉ để phát output. Causal skeleton thậm chí có treewidth 1. Đây là phản ví dụ ở mức trạng thái generator; chưa phải tuyên bố đã đo một dataset cụ thể tạo đúng các CI thresholds ấy.

Nếu muốn phát biểu lower bound trên toàn bộ trạng thái reachable của bản dcFCI mặc định, cần chứng minh thêm reachability từ initial complete graph. Không cần bước đó để bác bỏ lời hứa đa thức cho mọi candidate pool.

Lower bound cũng không phủ định khả năng một thuật toán top-k-only nhanh hơn. Nhưng top-k trực tiếp cần xử lý lại score phụ thuộc family; đó không còn chỉ là thay bộ sinh ứng viên.

**4.2. Eureka lý thuyết khả thi: output-sensitive hoặc lớp hạn chế**

Một mục tiêu nghiên cứu đủ chính xác là:

> Tìm lớp trạng thái F được mô tả bằng cấu trúc graph/constraints, và đặc trưng cần-đủ kiểm tra trong thời gian đa thức xem partial assignment còn mở rộng được thành accepted candidate hay không.

Ký hiệu Extend_F(σ). Đây phải là khả năng mở rộng tới leaf thực sự hợp lệ, không chỉ pass ba điều kiện cần T1–T3. Oracle phải đúng và có bound đa thức cho mọi prefix/domain restriction mà DFS tạo ra từ một input thuộc F; chỉ giải được initial instances là chưa đủ. K dưới đây đếm accepted configurations trước dedup, không phải số unique PAGs.

**Định lý mục tiêu có điều kiện.** Nếu Extend_F chính xác, có chi phí C_ext=poly(p,m), domain size tối đa d, và có K accepted configurations, thì DFS dùng Extend_F có thể liệt kê với chi phí generation:

$$
O\bigl(qd(K+1)C_{\rm ext}\bigr),
$$

chưa cộng leaf construction/output/scoring. Có polynomial delay ở cấp generator nếu các bước đó được tách đúng.

**Lập luận.** Mỗi prefix còn sống thuộc ít nhất một trong K nghiệm; có nhiều nhất qK prefixes như vậy. Mỗi prefix thử tối đa d children. Prefix không mở rộng được bị nhận ra ngay bằng Extend_F. Trường hợp K=0 cần kiểm tra root. ∎

Đây là một hệ quả enumeration chuẩn khi có exact extension oracle. **Phần Eureka chưa có là xây dựng characterization/algorithm Extend_F cho một lớp graph có ý nghĩa.** Không được trình bày giả định “có oracle đa thức” như đã giải xong vấn đề.

Muốn tổng thời gian đa thức còn cần K đa thức, chi phí đọc candidate pools, leaf validation và family scoring cũng đa thức theo input được khai báo. Conditioning-set order tăng theo p hoặc implementation liệt kê paths/subsets có thể phá điều kiện đó.

Một sufficient condition dễ hiểu: sau propagation chỉ còn h=O(log(p+m)) biến lựa chọn tự do, domain bị chặn d=O(1), và mọi bước còn lại đa thức. Khi đó d^h là đa thức. Contribution phải chứng minh một lớp cấu trúc tự nhiên thực sự có tính chất ấy, không định nghĩa lớp bằng “những trường hợp solver chạy nhanh”.

Bounded treewidth của constraint graph có thể giúp CSP feasibility/counting khi đã có encoding đầy đủ; không tự giúp explicit output và không đồng nghĩa treewidth của causal skeleton. Score không factorize cũng ngăn suy ra ngay thuật toán top-k.

**4.3. Eureka thực nghiệm: tránh >90% ứng viên vô ích**

Định nghĩa trên cùng snapshot và cùng quy tắc đếm sau preprocessing. Trước hết dùng cấu hình theo cặp, chưa dedup:

$$
N_1=|\Omega_{\rm pair}|,\qquad
V_1=|\{z\in\Omega_{\rm pair}:F_{\rm ref}(z)=1\}|,\qquad
I_1=N_1-V_1.
$$

Gọi I₂ là số complete configurations invalid vẫn tới leaf không bị prune trong B2, trước cùng bước global dedup. Nếu một cấu hình được dedup và không gọi validator trực tiếp, phân loại nó qua representative tương đương đã audit. Số actual full-validation calls báo riêng. Khi đã chứng minh không prune valid configurations:

$$
R_{\rm invalid}=1-\frac{I_2}{I_1},\qquad I_1>0.
$$

Mốc mong muốn:

$$
R_{\rm invalid}>0.90.
$$

Nếu I₁=0 ghi N/A. Không dùng B0 làm mẫu số vì việc bỏ duplicate-pair subsets đã là lợi ích của B1.

Đếm thêm:

$$
R_{\rm all}=\frac{I_1-I_2}{N_1}.
$$

Nếu invalid chỉ là 2% tổng số, bỏ 90% invalid mới tránh 1,8% toàn bộ candidates. Điều đó chưa chắc có giá trị runtime.

Để tính số complete assignments bị cắt mà không duyệt lại, ghi subtree mass tại mỗi prune và các domain-value deletions, bảo đảm vùng đếm rời nhau. Nogoods có overlap thì không cộng kích thước mỗi clause trực tiếp. Với audit nhỏ, đối chiếu mass bằng enumeration đầy đủ. Với workload quá lớn baseline không chạy hết, không báo tỷ lệ exact 90% nếu không có count proof/estimator được công bố.

Nếu dedup làm nhiều configurations cho cùng state, báo thêm các số ở mức unique state sau dedup. Không lấy configurations ở mẫu số rồi unique PAGs ở tử số.

**Mốc xác nhận đề nghị, chưa đạt trong review này:**

1. Proof không mất valid candidate; kiểm thử exhaustive trên pool nhỏ và equality theo từng vòng.
2. R_invalid>90% trên lớp workload đã đăng ký trước; báo cả median, phân bố và khoảng tin cậy, không chỉ pooled ratio bị một case lớn chi phối.
3. Runtime ròng B2 nhanh hơn B1; một mục tiêu thực dụng để thảo luận là median ≥2× và paired interval không bao gồm 1×, đồng thời báo regressions.
4. Full accepted states, score/ties và output không đổi; SHD tới truth không đổi theo đó.
5. Vượt baseline theo cặp, memoization hợp lý và pruning/solver tổng quát thích hợp.

Ngưỡng 2× và 90% là tiêu chí thực nghiệm đề xuất, không phải định lý và không tự chứng minh novelty.

**4.4. Phát biểu contribution nên nhắm đến**

Phiên bản vừa sức:

> Một bộ sinh cấu hình separating sets cho dcFCI, dùng các premises bền vững dưới mọi completion để phát hiện sớm mâu thuẫn đồ thị, bảo toàn họ ứng viên và semantics lựa chọn của reference, đồng thời giảm đáng kể chi phí dựng/kiểm tra ứng viên trên lớp workload xác định.

Phiên bản lý thuyết mạnh hơn:

> Một đặc trưng extendibility cần-đủ cho partial separating-set assignments trên lớp F, dẫn đến enumeration output-sensitive/polynomial delay và tích hợp được với dcFCI.

Không nên viết “biến dcFCI từ hàm mũ thành đa thức” nếu chỉ có một số curves đẹp hoặc giảm 90% candidates. 0,1·2^q vẫn là hàm mũ.

**Điều cần quyết định trước triển khai:** chọn reference semantics và phạm vi selection; thống nhất metric/equality/cap; chạy profiling nhỏ để biết invalid-candidate work có đủ lớn; rồi mới đầu tư vào pruning engine. Review này chưa thay đổi contract hay thuật toán trong repo.
