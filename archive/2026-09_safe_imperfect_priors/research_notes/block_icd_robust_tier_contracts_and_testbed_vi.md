# Research contracts và falsification plan

## Blockwise ICD, Fallible-Tier Robust Envelope và testbed chung

**Ngày chốt thiết kế:** 2026-09-30  
**Trạng thái:** pre-implementation; theorem-first; có thể bị bác bỏ  
**Giả định điều hành:** K1 được coi là `PASS` cho đến khi có đính chính  
**Tài liệu mẹ:** `latent_fci_optimization_directions_4rounds_vi.md`  
**Phạm vi:** khám phá nhân quả quan sát với biến ẩn, đầu ra đích là PAG; prior có thể sai và sai theo cụm

---

## 1. Quyết định nghiên cứu mà tài liệu này phải hỗ trợ

Không triển khai đồng thời năm ý tưởng ở quy mô lớn. Giai đoạn tiếp theo chỉ trả lời ba câu hỏi:

1. **Blockwise ICD:** có tồn tại một cách chia một vòng refinement của ICD thành các block sao cho từng prefix vẫn có diễn giải an toàn và khi chạy hết thì đúng bằng vòng ICD chuẩn không?
2. **Robust tier:** có thể dùng temporal/tier prior sai trong một uncertainty set để cắt bớt candidate separators mà vẫn giữ kết quả oracle của FCI khi true tiering nằm trong tập đó không?
3. **Headroom:** ngay cả khi đúng về toán học, hai cơ chế có tạo lợi ích đủ lớn để đáng phát triển thành thuật toán hoàn chỉnh không?

Kết quả hợp lệ của giai đoạn này có thể là `GO`, `REVISE` hoặc `KILL`. Một kết quả âm được xem là có ích nếu nó xác định rõ impossibility boundary hoặc failure mode mới.

### 1.1. Những gì chưa làm ở giai đoạn này

- Không gọi LLM API.
- Không huấn luyện mô hình.
- Không tối ưu GPU.
- Không chạy ma trận finite-sample lớn.
- Không tuyên bố prefix graph là một PAG hoàn chỉnh.
- Không dùng prior làm bằng chứng xóa cạnh hoặc định hướng endpoint.
- Không thay đổi code và artifact K1 đang chạy.

### 1.2. Nguyên tắc chung

Mọi claim phải được kiểm tra theo thứ tự:

1. định nghĩa có nhất quán không;
2. phản ví dụ nhỏ có bác bỏ không;
3. oracle exhaustive test có khớp baseline không;
4. cơ chế có headroom không;
5. finite-sample có còn lợi ích không;
6. sau cùng mới xét LLM và GPU.

---

## 2. Ký hiệu và đối tượng chung

Cho:

- \(V\): tập biến quan sát;
- \(L\): tập biến ẩn;
- \(D\): DAG đầy đủ trên \(V\cup L\);
- \(M\): latent projection MAG trên \(V\);
- \(P^*\): PAG oracle biểu diễn Markov equivalence class của \(M\);
- \(CI(X,Y\mid Z)\): oracle hoặc statistical conditional-independence test;
- \(S_r\): discovery state sau khi hoàn tất depth/refinement round \(r\);
- \(PDS_{S_r}(X,Y)\): Possible-D-SEP candidates được tính từ snapshot \(S_r\);
- \(K\): tập các claim từ prior;
- \(\Gamma\): budget cho số nhóm claim có thể sai.

Ba đối tượng đầu ra phải được phân biệt:

1. **Completed PAG:** chỉ trả khi thuật toán đã hoàn tất toàn bộ các bước cần thiết.
2. **Discovery state:** graph còn extra edges/circle marks và danh sách công việc chưa chạy.
3. **Evidence certificate:** CI decisions, sepsets và orientation-rule premises đã được kiểm chứng.

Ở prefix của Blockwise ICD, đầu ra là `(DiscoveryState, EvidenceCertificate)`, không mặc nhiên là PAG.

---

# PHẦN I — RESEARCH CONTRACT A: BLOCKWISE ASYNCHRONOUS ICD

## 3. Phát biểu vấn đề

ICD tiến theo các vòng refinement toàn cục. Điều cần nghiên cứu không phải đơn giản là “chạy vùng được prior thích trước”, mà là:

> Có thể phân rã một global refinement round thành các toán tử block có dependency rõ ràng, cho phép ưu tiên computation và dừng ở prefix, trong khi vẫn bảo toàn soundness của mọi kết luận đã commit và confluence khi hoàn tất round hay không?

Đây là bài toán về **phân rã toán tử và hội tụ**, không chỉ là query scheduling.

## 4. Claim ledger

### A-C1 — Prefix evidence soundness

Sau bất kỳ block đã commit nào:

- mỗi edge deletion phải có một oracle-valid separating set certificate;
- mỗi definite endpoint phải được suy ra bởi một orientation rule sound với các premise đã được certificate;
- prior không xuất hiện trong proof trace của deletion hoặc endpoint.

Claim này không nói discovery state đã complete hoặc maximally oriented.

### A-C2 — Full-round equivalence

Nếu tất cả block của round \(r+1\) được hoàn tất, state thu được phải bằng state của một reference global ICD round chạy trên cùng snapshot \(S_r\), cùng CI oracle và cùng tie-breaking đã cố định.

### A-C3 — Order confluence

Mọi topological order hợp lệ của block-dependency DAG phải cho cùng completed-round state và cùng tập evidence, không kể thứ tự log.

### A-C4 — Budget value

Tồn tại một block policy không dùng CI ground truth, thu được nhiều invariant information hơn reference order tại cùng weighted CI budget trên một miền graph được định nghĩa trước.

### A-C5 — Safe degeneration

Nếu dependency closure tạo một giant block, thuật toán phải suy biến về global ICD round, không thay đổi output. Trường hợp này làm mất speed/headroom nhưng không được làm mất correctness.

## 5. Claim không được đưa ra

- Không claim worst-case asymptotic speedup trước khi có complexity result.
- Không claim giảm tổng số CI tests khi full completion nếu chỉ thay đổi thứ tự.
- Không claim wall-clock speedup từ parallelism khi chưa tách algorithmic gain khỏi hardware gain.
- Không gọi mọi orientation ở prefix là invariant nếu chưa chứng minh trên mọi legal completion.
- Không claim prior “sửa” causal graph.

## 6. Thiết kế thuật toán tối thiểu cần kiểm tra

### 6.1. Snapshot semantics

Tại đầu round \(r+1\):

1. đóng băng `snapshot = S_r`;
2. sinh candidate universe \(Q_{r+1}(S_r)\);
3. mỗi query chứa pair, conditioning set, path/radius witness và read footprint;
4. kết quả CI được ghi thành evidence delta;
5. graph update chỉ được commit theo quy tắc đã định nghĩa trước;
6. khi mọi block hoàn tất, chạy canonical orientation closure.

Snapshot semantics là ứng viên chính để loại order effect. Nếu reference ICD sinh candidate động trong cùng round, contract phải hoặc:

- chứng minh frozen candidate universe tương đương; hoặc
- mô hình hóa candidate-generation events như dependency nodes và so sánh với dynamic reference.

Không được ngầm chọn cách dễ hơn rồi gọi là ICD-equivalent.

### 6.2. Evidence lattice

Xem evidence state là:

\[
E=(I,R,O),
\]

trong đó:

- \(I\): tập CI facts đã kiểm tra;
- \(R\): edge-removal certificates `(X,Y,Z)`;
- \(O\): orientation certificates gồm rule và premises.

Join của hai block là phép hợp evidence:

\[
E_1\sqcup E_2.
\]

Mục tiêu là chứng minh các update cần thiết là monotone trên evidence lattice, còn canonical graph chỉ là materialized view của evidence. Cách diễn đạt này tránh để mutation order quyết định kết quả.

### 6.3. Read/write footprint

Mỗi query/event \(q\) phải khai báo:

- `read_nodes(q)`;
- `read_edges(q)`;
- `read_paths(q)`;
- `write_deletions(q)`;
- `affected_triples(q)`;
- `affected_discriminating_paths(q)`;
- candidate-generation dependencies.

Hai event chỉ được xem là độc lập nếu write footprint của event này không giao với transitive read/orientation footprint của event kia theo cả hai chiều.

### 6.4. Dependency hypergraph và block closure

Xây hypergraph \(H_r\):

- vertex là query hoặc graph-update event;
- hyperedge nối các event có chung dependency witness;
- connected components sau transitive closure là candidate blocks.

Một block \(B\) là **PDS/dependency-closed** nếu với mọi event trong \(B\), toàn bộ event có thể:

1. thay đổi eligibility của nó;
2. thay đổi path witness của nó;
3. tạo/phá triple dùng cho orientation của nó;
4. tạo/phá discriminating path liên quan;

đều nằm trong \(B\) hoặc được đánh dấu là predecessor bắt buộc.

Đây là định nghĩa cần được tinh chỉnh bằng theorem/counterexample, không phải giả định đã đúng.

### 6.5. Block execution

Một block operator \(T_B\):

1. đọc snapshot và evidence từ predecessor;
2. chạy toàn bộ query bắt buộc trong block theo deterministic local order;
3. thêm CI/removal certificates;
4. chạy chỉ các orientation rules mà premise đã được certificate;
5. materialize discovery state mới;
6. ghi unresolved consequences vào pending agenda.

Prior chỉ được dùng để chọn một block trong tập `ready_blocks`.

### 6.6. Prefix output

Prefix output phải gồm:

- conservative graph state;
- completed block IDs;
- pending block IDs;
- certified removals;
- certified definite endpoints;
- unresolved marks;
- dependency digest;
- proof trace không chứa prior như evidence.

Nếu chưa chứng minh definite endpoints ở prefix sound, phiên bản tối thiểu chỉ công bố certified non-adjacencies và giữ endpoint là circle. Đây là fallback hợp lệ.

## 7. Nghĩa vụ lý thuyết

### A-T1 — Certificate soundness

Với oracle CI, mỗi removal certificate do block tạo ra là đúng đối với true MAG/PAG dưới các giả định chuẩn của ICD/FCI.

### A-T2 — Conservative prefix theorem

Mọi definite non-adjacency/endpoint công bố ở prefix phải xuất hiện trong completed reference result hoặc phải được chứng minh invariant trên mọi legal completion của pending agenda.

Hai mức theorem được tách:

- **A-T2a:** sound certified non-adjacencies;
- **A-T2b:** sound definite endpoints.

A-T2a có thể sống ngay cả khi A-T2b thất bại.

### A-T3 — Pairwise commutation lemma

Với hai ready blocks độc lập \(B_i,B_j\):

\[
T_{B_i}(T_{B_j}(E))=T_{B_j}(T_{B_i}(E)).
\]

Phải phát biểu trên evidence canonicalized, không dựa vào thứ tự log.

### A-T4 — Global confluence theorem

Nếu dependency relation terminating và mọi critical pair commute hoặc join được, mọi topological execution kết thúc ở cùng normal form.

Một lộ trình chứng minh phù hợp là:

1. termination do candidate/event universe hữu hạn;
2. local confluence trên critical pairs;
3. suy ra confluence bằng lập luận kiểu Newman nếu các điều kiện thực sự thỏa.

Không được viện dẫn lemma này nếu dynamic candidate generation làm hệ không terminating/monotone theo định nghĩa đã chọn.

### A-T5 — Reference-round equivalence

Normal form của block system bằng output của reference global ICD operator \(T_{r+1}\).

### A-T6 — Decomposition characterization

Cần ít nhất một kết quả không chỉ correctness, ví dụ:

- điều kiện graph-theoretic đủ để có nhiều hơn một block;
- upper bound cho block width theo locality/PDS overlap;
- hoặc lower bound cho thấy family nào bắt buộc collapse thành giant block.

A-T6 là phần giúp hướng này trở thành đóng góp khoa học thay vì chỉ refactor.

## 8. Bộ phản ví dụ bắt buộc

### A-X1 — Diamond separator

\[
A\to B\to D,\qquad A\to C\to D.
\]

Kiểm tra separator cần thông tin từ hai nhánh có bị tách sai thành hai block hay không.

### A-X2 — Collider activation

Một conditioning variable mở collider path. Kiểm tra block-local reasoning có nhầm “node gần pair” với separator hợp lệ không.

### A-X3 — Latent confounder

\[
X\leftarrow L\rightarrow Y.
\]

Kiểm tra không dùng DAG adjacency trực tiếp thay cho MAG/PAG semantics.

### A-X4 — Discriminating path crossing blocks

Construct một discriminating path có vertices trải qua hai candidate blocks. Nếu orientation ở block đầu phụ thuộc non-adjacency tạo bởi block sau, hai block không độc lập.

### A-X5 — Deletion creates unshielded triple

Một edge deletion trong \(B_i\) tạo unshielded triple có endpoint nằm trong \(B_j\). Dependency closure phải nối hai block hoặc trì hoãn orientation.

### A-X6 — Scenario-S2/PDS-dominant motif

Graph mà useful separator nằm ngoài adjacency neighborhood nhưng trong Possible-D-SEP. Mục tiêu là phát hiện local block construction quá hẹp.

### A-X7 — Giant dependency component

Hub/dense PAG nơi hầu hết queries nối qua shared paths. Đây không phải correctness failure, nhưng có thể bác bỏ computational headroom.

### A-X8 — Same evidence, different mutation order

Hai execution có cùng CI facts nhưng raw mutation log khác nhau. Canonical output phải giống nhau; nếu không, implementation đang phụ thuộc order ngoài contract.

## 9. Falsification plan cho Blockwise ICD

### A-F0 — Definition audit

**Mục tiêu:** tìm mâu thuẫn trước khi code thuật toán.

Checklist:

- Reference ICD round được định nghĩa đến mức pseudocode executable.
- Snapshot/dynamic semantics được chọn công khai.
- Equality của state bỏ qua log order nhưng không bỏ qua graph marks/sepsets.
- Prefix soundness xác định trên non-adjacency và endpoint riêng.
- Block independence có tiêu chuẩn decidable.

**KILL/REVISE:** nếu không thể định nghĩa một unit of work mà reference algorithm cũng thừa nhận, chuyển từ “Blockwise ICD” sang “certified query agenda” và giảm claim.

### A-F1 — Hand proof trên motifs

Chạy bằng tay A-X1 đến A-X6:

1. lập candidate/event universe;
2. xây dependency hypergraph;
3. liệt kê blocks;
4. chạy mọi legal order;
5. so với reference round;
6. ghi critical pair đầu tiên không join được.

**Gate:** không code random benchmark trước khi sáu motifs có expected trace.

### A-F2 — Exhaustive small-graph oracle

Tập kiểm thử:

- non-isomorphic DAGs với tổng số node nhỏ, ưu tiên observed `3..5` và tổng node `<=6`;
- mọi latent mask hợp lệ có ít nhất ba observed nodes;
- lọc/ghi rõ các graph không thỏa assumptions;
- latent projection hoặc full-DAG d-separation oracle trên observed variables;
- reference PAG/round độc lập với block implementation.

Với mỗi state/round:

- mọi permutation nếu số ready blocks `<=7`;
- nếu lớn hơn: mọi pairwise swap critical pair cộng ít nhất 100 seeded topological orders;
- compare removals, sepsets, endpoint matrix và pending agenda canonicalized.

**Hard kill:**

- bất kỳ false certified non-adjacency;
- bất kỳ false definite endpoint được claim bởi A-T2b;
- completed-round mismatch không giải thích được bằng tie convention;
- nondeterminism dưới replay cùng seed/config.

### A-F3 — Decomposition headroom

Sau correctness:

- random sparse, hub, chain-of-modules, scale-free và PDS-dominant graphs;
- observed nodes `10, 20, 50` ở oracle CI;
- latent ratios kế thừa K1: `0.2, 0.4`;
- mean degrees `2, 4`, thêm dense stress cell chỉ để failure analysis.

Đo:

- số blocks;
- largest-block fraction theo nodes, queries và weighted cost;
- dependency-DAG width/critical path;
- closure-construction cost;
- tỷ lệ graph collapse thành một giant block.

**Pre-registered gate:**

- `GO`: median largest-block weighted-cost fraction `<=0.70` ở ít nhất hai family quan trọng và có ready width `>=2`;
- `RESTRICTED_GO`: decomposition chỉ tồn tại ở modular/sparse family nhưng family được mô tả bằng điều kiện A-T6;
- `KILL_HEADROOM`: trên hơn 70% graph mục tiêu, một block giữ trên 80% weighted cost.

### A-F4 — Oracle policy upper bound

Mục đích không phải deploy oracle mà đo trần giá trị của việc chọn block.

So sánh:

- stable/reference block order;
- random ready block;
- cheapest-ready;
- graph-only heuristic;
- oracle block order, chỉ dùng để đo upper bound;
- K1 query scheduler như baseline ngân sách.

Budget checkpoints: `10%, 25%, 50%, 100%` tổng weighted cost của full reference round.

Primary prefix utility:

\[
U_b = w_s\,F1_{skeleton}+w_e\,F1_{invariant\ endpoint}
-w_f\,N_{false\ definite},
\]

nhưng báo riêng từng thành phần; không chỉ báo scalar tổng hợp.

**Gate:**

- `KILL_POLICY`: oracle block order không cải thiện frontier so với reference/K1 scheduler;
- `GO_MECHANISM`: tại 25% budget, oracle block policy thu ít nhất 75% invariant-mark gain của full next round hoặc cải thiện time-to-fixed-target ít nhất 15%;
- sau đó graph-only/noisy-prior policy phải thu hồi một phần pre-registered của oracle gain trước khi tích hợp LLM.

### A-F5 — Cost accounting

Tính đầy đủ:

- CI calls theo conditioning order;
- weighted CI cost;
- dependency construction;
- block closure/revalidation;
- orientation closure;
- serialization/checkpoint;
- peak RAM;
- wall time CPU đơn luồng và parallel riêng.

Nếu algorithmic saving biến mất khi tính dependency overhead, hướng không qua.

### A-F6 — Finite-sample sanity, chỉ sau oracle GO

SEM linear Gaussian trước, sample sizes `500, 2_000, 10_000`; dùng cùng data và CI backend giữa methods.

Mục đích:

- không chứng minh theorem;
- chỉ kiểm tra order/block policy có khuếch đại statistical errors không;
- đo stability qua bootstrap và false definite endpoints.

Không chạy grid lớn nếu A-F2–A-F5 chưa qua.

## 10. Success, revise và kill contract cho hướng A

### GO-A

Chỉ `GO-A` khi đồng thời:

1. A-T2a, A-T3 và A-T5 không bị exhaustive test bác bỏ;
2. không có false definite endpoint trong phạm vi claim;
3. có decomposition headroom trên family không tầm thường;
4. oracle block ordering có budget value;
5. một policy không oracle giữ được phần có ý nghĩa của gain;
6. overhead không xóa lợi ích.

### REVISE-A

- A-T2b fail nhưng A-T2a đúng: chỉ xuất certified non-adjacencies ở prefix.
- Confluence chỉ đúng với barrier giữa sub-rounds: đổi tên thành staged/block-synchronous ICD.
- Chỉ modular graph có headroom: thu hẹp domain và chứng minh characterization.

### KILL-A

- Full-round equivalence sai theo bản chất.
- Dependency-safe closure luôn collapse trên miền mục tiêu.
- Oracle policy không tạo prefix value hơn scheduler K1.
- Claim còn lại chỉ là parallel engineering không có kết quả thuật toán/lý thuyết.

---

# PHẦN II — RESEARCH CONTRACT B: FALLIBLE-TIER ROBUST ENVELOPE

## 11. Phát biểu vấn đề

Temporal/tier knowledge đúng có thể thu hẹp search space, nhưng expert hoặc LLM prior có thể sai theo source, node hoặc cả tier. Câu hỏi nghiên cứu là:

> Có thể biến một tập tier claims có lỗi theo nhóm thành một envelope candidate an toàn, sao cho khi true tiering nằm trong uncertainty set thì oracle output vẫn bằng FCI, đồng thời envelope thường nhỏ hơn full PDS đủ nhiều để có lợi?

Hướng này thay đổi **candidate set**, nên prior gián tiếp ảnh hưởng edge deletion. Do đó safety condition phải mạnh hơn scheduler-only K1.

## 12. Mô hình prior và uncertainty

### 12.1. Tiering

Một tiering \(\tau\) ánh xạ mỗi observed variable tới một thứ tự/tier, cho phép ties nếu thiết kế chọn partial order.

Không tự sáng chế quy tắc temporal admissibility. Ta định nghĩa:

\[
A_\tau(X,Y)
\]

là candidate restriction được chứng minh đủ bởi theorem chính xác của tier-aware FCI được chọn làm reference. Mọi implementation phải ghi citation/lemma và chuyển nó thành executable predicate.

### 12.2. Grouped claims

Mỗi claim \(k\in K\) gồm:

- relation, ví dụ `tier(X) < tier(Y)` hoặc `not-after(X,Y)`;
- source ID;
- group ID;
- optional confidence/weight;
- provenance.

Các prompt lặp lại hoặc claims cùng một source/motif không được coi là independent votes.

### 12.3. Violation budget

Cho:

\[
v_K(\tau)=\sum_{g\in G} w_g\,
\mathbf 1[\tau\text{ vi phạm ít nhất một claim trong }g].
\]

Tập tiering khả thi:

\[
\mathcal T_\Gamma(K)=
\{\tau:\tau\text{ hợp lệ và }v_K(\tau)\le\Gamma\}.
\]

Group budget là thiết kế chính. Node/source/motif-correlated errors phải được biểu diễn bằng group, không giả độc lập giả tạo.

### 12.4. Robust envelope

Với một pair \((X,Y)\):

\[
R_\Gamma(X,Y)=
\bigcup_{\tau\in\mathcal T_\Gamma(K)}A_\tau(X,Y),
\]

và:

\[
J_\Gamma(X,Y)=PDS(X,Y)\cap R_\Gamma(X,Y).
\]

FCI chỉ tìm separating sets trong \(J_\Gamma\) nếu coverage condition được chấp nhận. Nếu uncertainty set rỗng hoặc không được certify, fallback là full PDS.

## 13. Claim ledger

### B-C1 — Conditional exactness

Nếu:

1. assumptions oracle FCI thỏa;
2. \(\tau^*\in\mathcal T_\Gamma(K)\);
3. \(A_{\tau^*}\) giữ candidate-sufficiency lemma;

thì robust-envelope FCI trả cùng oracle PAG với reference FCI.

### B-C2 — No-prior fallback

Khi `K` rỗng, `Gamma` cực đại, uncertainty infeasible hoặc envelope không tạo saving, implementation phải chạy full PDS/reference FCI.

### B-C3 — Correlation-aware robustness

Với cùng marginal claim accuracy, grouped uncertainty phải có coverage tốt hơn independent-claim budget khi lỗi thực tế theo source/node/motif, hoặc phải chỉ ra rõ trade-off coverage–shrinkage.

### B-C4 — Computational tractability

Có thể quyết định membership `Z in R_Gamma(X,Y)` hoặc xây toàn envelope mà không enumerate mọi tier order, với complexity được mô tả theo số variables, số groups, \(\Gamma\), hoặc width của partial order.

### B-C5 — Nontrivial shrinkage

Trên ít nhất một miền graph/prior được xác định trước, envelope an toàn giảm candidate/test cost đủ lớn sau khi tính overhead.

## 14. Claim không được đưa ra

- Không claim unconditional safety nếu không biết \(\tau^*\in\mathcal T_\Gamma\).
- Không dùng posterior confidence của LLM như coverage proof.
- Không dùng uncertain tier claims trực tiếp để orient cạnh trong phiên bản này.
- Không claim exactness finite-sample; theorem là oracle-level.
- Không giấu trường hợp envelope collapse về full PDS.
- Không chọn \(\Gamma\) trên test graph bằng cách nhìn ground truth.

## 15. Nghĩa vụ lý thuyết

### B-T0 — Reference restriction lemma

Phải tái phát biểu và kiểm chứng lemma từ tier-aware FCI:

> Với một true-valid tiering \(\tau^*\), nếu \(X,Y\) m-separated trong true MAG thì tồn tại một minimal separator cần thiết nằm trong candidate family tạo bởi \(A_{\tau^*}(X,Y)\).

Nếu lemma chỉ đúng dưới giả định hẹp hơn, contract kế thừa nguyên vẹn giả định đó.

### B-T1 — Robust superset lemma

Nếu \(\tau^*\in\mathcal T_\Gamma(K)\), thì:

\[
A_{\tau^*}(X,Y)\subseteq R_\Gamma(X,Y).
\]

Đây là bước đơn giản nhưng chỉ có ích khi kết hợp B-T0.

### B-T2 — Oracle equivalence theorem

Từ B-T0 và B-T1, chứng minh robust-envelope FCI không bỏ mọi valid separator cần thiết và có cùng completed oracle PAG với reference FCI.

Cần audit thêm orientation/sepset semantics: cùng skeleton nhưng chọn separator khác có thể ảnh hưởng collider orientation. Equality phải ở canonical PAG, không chỉ skeleton.

### B-T3 — Smallest universally safe envelope

Ứng viên kết quả mạnh:

\[
R^*_{\Gamma}(X,Y)=
\bigcup_{\tau\in\mathcal T_\Gamma(K)}A_\tau(X,Y)
\]

là envelope nhỏ nhất an toàn đồng đều trong một class được xác định. Để claim minimality, phải chứng minh với mỗi candidate bị bỏ có một admissible model nơi nó là thành viên thiết yếu/duy nhất của separator.

Nếu không chứng minh được cho mọi candidate, phát biểu characterization trên một subclass cụ thể.

### B-T4 — Envelope computation theorem

Giảm bài toán membership về constraint feasibility:

\[
Z\in R_\Gamma(X,Y)
\Longleftrightarrow
\exists\tau:
\tau\in\mathcal T_\Gamma(K)
\land Z\in A_\tau(X,Y).
\]

Thiết kế có thể dùng SAT/ILP/DP, nhưng cần:

- chứng minh encoding sound và complete;
- cache pair-independent constraints;
- complexity bound hoặc fixed-parameter result;
- so sánh overhead với CI cost thực tế.

### B-T5 — Collapse/no-free-lunch result

Nếu uncertainty set cho phép đủ nhiều tier permutations, robust union có thể bằng full PDS. Một theorem âm có thể mô tả điều kiện:

\[
R_\Gamma(X,Y)=PDS(X,Y).
\]

Kết quả này có giá trị vì chỉ ra chính xác khi safety và pruning không thể đồng thời đạt được.

### B-T6 — Coverage corollary, tùy chọn

Nếu \(\Gamma\) được chọn từ calibration data độc lập sao cho:

\[
\Pr(\tau^*\in\mathcal T_\Gamma(K))\ge 1-\delta,
\]

thì exactness có xác suất ít nhất \(1-\delta\) đối với randomness của prior model. Đây là tầng probabilistic riêng, không thay thế theorem deterministic B-T2.

## 16. Bộ phản ví dụ bắt buộc

### B-X1 — Unique confounder separator

\[
X\leftarrow Z\rightarrow Y.
\]

Nếu prior đặt `Z` sau cả `X,Y` và \(\Gamma\) không chứa lỗi này, edge giả phải còn lại. Test chứng minh coverage condition là cần thiết.

### B-X2 — Whole-tier swap

Đổi chỗ hai tier làm sai nhiều pairwise claims nhưng chỉ là một correlated event. Independent-error budget có thể đánh giá sai nghiêm trọng.

### B-X3 — One bad source, many duplicate claims

Một source sinh nhiều claims gần trùng. Grouped budget phải tính là một source failure thay vì biến repetition thành confidence.

### B-X4 — Union collapse

Nhiều candidates \(Z_i\), mỗi feasible tiering cho phép một \(Z_i\). Union qua tierings trả toàn PDS dù từng tiering riêng lẻ rất hẹp.

### B-X5 — Empty uncertainty set

Claims tạo cycle hoặc \(\Gamma\) quá nhỏ. Hệ thống phải phát hiện infeasible và fallback; không trả empty search pool.

### B-X6 — Alternative sepsets, different collider consequences

Hai minimal separators đều tách pair nhưng membership của middle node khác nhau. Test equality ở PAG/orientation, không chỉ edge deletion.

### B-X7 — Latent bidirected structure

Tier restriction chỉ áp lên directed temporal relations; không được diễn giải bidirected edge như hai temporal directions.

### B-X8 — Prior adversarial nhưng confidence cao

Kiểm tra confidence không tự động làm nhỏ \(\Gamma\), và fallback/coverage diagnostics hoạt động.

## 17. Falsification plan cho robust tiers

### B-F0 — Lemma audit trước code

1. Chọn đúng tier-aware FCI reference.
2. Trích nguyên assumptions và candidate restriction.
3. Viết `A_tau(X,Y)` dưới dạng predicate executable.
4. Chứng minh/tái tạo theorem trên motifs.
5. Liệt kê trường hợp selection bias, ties và latent confounding có/không được hỗ trợ.

**Hard stop:** nếu không tái tạo được B-T0, không code robust union. Khi đó hướng này chưa có nền tảng safety.

### B-F1 — True-tier upper bound

Trước uncertainty, đo giới hạn tốt nhất khi biết đúng \(\tau^*\):

- full PDS FCI;
- correct-tier candidate restriction;
- scheduler-only sử dụng cùng tier signal;
- hard incorrect-tier negative control.

Đo candidate count, actual CI calls, weighted cost và final PAG equality.

**Kill:** true tier giảm dưới 15% weighted candidate/CI cost trên miền mục tiêu. Nếu oracle tier còn không giúp, robust tier không thể cứu headroom.

### B-F2 — Exact uncertainty enumeration trên graph nhỏ

Với `p<=8` observed variables:

- enumerate all tierings/linear extensions khả thi;
- tính envelope bằng brute force;
- so với SAT/ILP/DP implementation;
- enumerate group-violation budgets nhỏ;
- verify B-T1 và B-T2 cho mọi pair.

**Hard kill:** optimized envelope bỏ candidate có trong brute-force union hoặc final PAG khác reference khi \(\tau^*\) thuộc feasible set.

### B-F3 — Error-model matrix

Prior synthetic được tạo từ true tiering với các mode:

- independent pair flips;
- whole-tier swaps;
- node-correlated displacement;
- source-correlated batch errors;
- motif-correlated errors;
- adversarial but budget-bounded errors.

Không so sánh các mode chỉ bằng raw accuracy. Phải ghi:

- marginal pair accuracy;
- group violation count;
- Kendall/partial-order distance nếu phù hợp;
- uncertainty-set coverage;
- envelope retention ratio.

### B-F4 — Coverage–shrinkage frontier

Với mỗi \(\Gamma\), báo:

\[
Coverage(\Gamma)=
\Pr[\tau^*\in\mathcal T_\Gamma(K)]
\]

và:

\[
Retention(\Gamma)=
\frac{\sum_{X,Y}|J_\Gamma(X,Y)|}
{\sum_{X,Y}|PDS(X,Y)|}.

\]

Không chọn một \(\Gamma\) duy nhất rồi che trade-off. Primary comparison tại coverage targets `0.90`, `0.95`, `0.99` nếu có calibration protocol hợp lệ.

**Gate:**

- `GO`: tại coverage target pre-registered, median retention `<=0.80` và weighted CI saving `>=15%` trên ít nhất một miền quan trọng;
- `RESTRICTED_GO`: chỉ một family/source model đạt;
- `KILL_COLLAPSE`: tại realistic \(Gamma\), median retention `>0.90` và net saving không đạt 10%.

### B-F5 — Solver overhead

So sánh:

- brute-force enumeration nhỏ;
- SAT/ILP membership query;
- batched/cached solver;
- conservative analytic approximation nếu có.

Đo:

- build time;
- per-pair membership time;
- cache hit rate;
- peak RAM;
- solver timeouts;
- saved CI cost.

**Kill/Revise:** nếu envelope solve cost lớn hơn CI saving ở oracle benchmark, dùng robust tier chỉ làm scheduler score hoặc giới hạn vào conditioning order cao nơi CI đắt.

### B-F6 — Calibration không leakage

Nếu phát triển B-T6:

- tách graph/source families thành train-calibration-test;
- chọn \(\Gamma\) chỉ trên calibration;
- khóa group construction trước test;
- báo empirical coverage và confidence interval;
- stress-test distribution shift theo source/error cluster.

Không dùng test true tier để chọn \(\Gamma\).

### B-F7 — Finite-sample sanity, chỉ sau oracle GO

Dùng cùng SEM/data/CI realization cho full FCI và robust variant. Đo:

- skeleton/endpoint precision-recall;
- PAG mismatch;
- CI call/cost;
- false definite endpoints;
- failure conditional on coverage miss.

Phân tách rõ hai nguyên nhân lỗi:

1. statistical CI error dù true tier được cover;
2. prior coverage failure.

## 18. Success, revise và kill contract cho hướng B

### GO-B

Chỉ `GO-B` khi:

1. B-T0 được tái tạo chính xác;
2. brute-force và optimized envelope trùng trên graph nhỏ;
3. oracle PAG equivalence giữ khi true tier được cover;
4. coverage–shrinkage frontier không collapse;
5. solver overhead nhỏ hơn saving;
6. grouped uncertainty thực sự xử lý correlated errors tốt hơn baseline độc lập.

### REVISE-B

- Exact pruning collapse nhưng ranking vẫn có ích: chuyển envelope thành scheduler, giữ full PDS.
- Chỉ high-order CI có net saving: áp dụng restriction từ một order threshold.
- Coverage chỉ đáng tin theo source family: thu hẹp claim/domain.
- Minimality theorem quá mạnh: giữ equivalence + computation/collapse theorem.

### KILL-B

- B-T0 không áp dụng cho setting latent/PAG đã chọn.
- Có PAG mismatch dù true tier thuộc feasible set.
- Safe envelope gần full PDS trong hầu hết miền mục tiêu.
- Solver overhead lớn hơn CI saving.
- “Robustness” chỉ tồn tại do dùng ground truth để chọn \(Gamma\).

---

# PHẦN III — TESTBED CHUNG

## 19. Mục tiêu thiết kế

Testbed phải trả lời lần lượt:

1. implementation có đúng reference không;
2. theorem có bị graph nhỏ bác bỏ không;
3. mechanism có headroom oracle không;
4. prior noisy có giữ được headroom không;
5. finite-sample có phá lợi ích không.

Không dùng một ma trận khổng lồ để trả lời đồng thời cả năm câu hỏi.

## 20. Tách testbed thành bốn tầng

### Tầng T0 — Unit motifs và proof traces

Quy mô vài chục hand-crafted cases:

- chain, fork, collider;
- latent confounder và latent mediator;
- diamond;
- discriminating paths;
- deletion-created unshielded triples;
- Scenario-S2/PDS-dominant;
- whole-tier swap và union-collapse motifs.

Mỗi motif có:

- full DAG;
- observed/latent mask;
- expected CI facts;
- expected MAG/PAG hoặc reference digest;
- expected block dependencies;
- expected tier envelope;
- expected failure nếu assumption bị vi phạm.

### Tầng T1 — Exhaustive oracle small graphs

Mục tiêu là falsification, không phải performance:

- enumerate non-isomorphic DAGs trong giới hạn khả thi;
- tổng node `<=6`, observed `3..5`;
- enumerate latent masks có kiểm soát;
- deduplicate theo canonical latent projection/PAG digest;
- chạy mọi legal block order khi nhỏ;
- enumerate tierings khi `p<=8`;
- lưu minimal counterexample thay vì toàn bộ verbose logs.

T1 phải chạy được trên CPU và tạo artifact nhỏ.

### Tầng T2 — Oracle mechanism benchmark

Ma trận khởi đầu:

| Trục | Giá trị |
|---|---|
| Observed nodes | 10, 20, 50 |
| Latent ratio | 0.2, 0.4 |
| Mean degree | 2, 4 |
| Families | random sparse, hub, modular, PDS-dominant |
| Seeds/cell pilot | 10 trước, 50 sau GO |
| CI | oracle |
| Budget | 0.10, 0.25, 0.50, 1.00 |

Chỉ mở rộng từ 10 lên 50 seeds sau khi pilot confidence intervals cho thấy hiệu ứng không sát zero.

### Tầng T3 — Finite-sample confirmation

Chỉ chạy nếu T0–T2 qua:

| Trục | Giá trị khởi đầu |
|---|---|
| SEM | linear Gaussian |
| n | 500, 2,000, 10,000 |
| alpha | khóa trước, thêm sensitivity grid nhỏ |
| repeats | 20 pilot, tăng sau power analysis |
| graph sizes | 10, 20 trước |

Nonlinear/non-Gaussian là external validity phase, không được dùng để cứu một core mechanism đã fail.

## 21. Baselines bắt buộc

### Chung

- FCI-stable/reference upstream;
- RFCI-stable nếu implementation được xác nhận;
- current K1 stable/random/cost-only/graph-only/oracle scheduler;
- identical CI cache khi so algorithmic control flow, hoặc báo cả cached và uncached.

### Cho Blockwise ICD

- reference ICD/global refinement;
- random legal block order;
- cheapest-ready block;
- graph-only block score;
- oracle block order chỉ làm upper bound;
- query-level K1 scheduler để kiểm tra block abstraction có thêm giá trị không.

### Cho robust tiers

- full-PDS FCI;
- correct-tier FCI upper bound;
- noisy tier dùng hard restriction, negative control;
- noisy tier scheduler-only, safe fallback;
- independent-claim uncertainty;
- grouped robust envelope.

## 22. Ground truth và reference independence

Không dùng cùng một hàm để tạo output được kiểm tra và reference expected output.

Tối thiểu:

- CI oracle dùng d-separation trong full DAG trên observed queries;
- reference PAG dùng upstream FCI hoặc một pipeline độc lập đã conformance-test;
- latent projection/MAG digest được lưu nếu thư viện hỗ trợ đáng tin;
- block/tier implementation không được gọi helper nội bộ của chính nó để tạo expected result.

Mỗi mismatch phải được phân loại:

- true algorithmic counterexample;
- endpoint encoding convention;
- sepset tie difference;
- upstream/reference limitation;
- implementation bug.

Không tự động bỏ mismatch khỏi thống kê.

## 23. Metrics

### 23.1. Correctness metrics

- exact canonical PAG equality;
- skeleton equality;
- endpoint confusion matrix;
- wrong determined endpoints;
- sepset validity;
- completed-round state equality;
- replay determinism;
- prior-as-evidence violations.

### 23.2. Search/computation metrics

- CI calls;
- CI calls by conditioning order;
- weighted cost, với trọng số khóa trước;
- maximum conditioning-set size;
- PDS/candidate retention;
- dependency/envelope build time;
- orientation/revalidation time;
- peak RAM;
- wall-clock và CPU time.

### 23.3. Anytime metrics

- skeleton F1 theo weighted budget;
- certified non-adjacency recall;
- invariant endpoint precision/recall;
- area under quality–cost curve;
- cost to fixed target;
- oracle-gain recovery fraction.

### 23.4. Robustness metrics

- true-tier coverage;
- retention ratio;
- group violation count;
- performance by error mode;
- regret so full FCI và correct-tier upper bound;
- fallback frequency;
- failure severity khi coverage miss.

## 24. Artifact contract

Không lặp lại mô hình raw output 70+ GB ở pilot. Mặc định lưu bảng tổng hợp và chỉ giữ trace đầy đủ cho failures/counterexamples.

### 24.1. Cấu trúc đề xuất

```text
artifacts/algorithm_pilots/
├── manifests/
│   ├── graph_manifest.parquet
│   ├── seed_manifest.parquet
│   └── environment.json
├── references/
│   ├── pag_digests.parquet
│   └── ci_oracle_digests.parquet
├── block_icd/
│   ├── runs.parquet
│   ├── block_stats.parquet
│   ├── prefix_metrics.parquet
│   └── counterexamples/
├── robust_tier/
│   ├── runs.parquet
│   ├── envelope_stats.parquet
│   ├── coverage_frontier.parquet
│   └── counterexamples/
└── reports/
    ├── gate_decisions.json
    └── falsification_report.md
```

### 24.2. Full traces chỉ lưu khi

- mismatch;
- false definite endpoint;
- solver discrepancy;
- first instance của một failure signature;
- seeded audit sample, ví dụ 1% successful runs.

Successful repeated runs chỉ lưu digest và aggregate row. Chính sách này vừa đủ reproducibility mà không phình disk.

### 24.3. Provenance bắt buộc

- git revision và dirty-state digest;
- config digest;
- library versions;
- graph/data/prior/scheduler seeds tách riêng;
- reference implementation version;
- solver/version/options;
- CPU/GPU information dù GPU chưa dùng;
- start/end time và interruption status.

## 25. Kiến trúc code đề xuất

Không sửa trực tiếp K1 runner trước khi pilot độc lập qua unit tests. Tạo namespace mới:

```text
src/safety_prior/
├── algorithms/
│   ├── icd_reference.py
│   ├── block_icd.py
│   ├── block_dependencies.py
│   └── evidence.py
├── tiers/
│   ├── claims.py
│   ├── uncertainty.py
│   ├── envelope.py
│   └── solver.py
└── pilots/
    ├── graph_catalog.py
    ├── exhaustive.py
    ├── run_block_icd.py
    └── run_robust_tier.py
```

Tests tương ứng:

```text
tests/algorithm_pilots/
├── test_reference_icd.py
├── test_block_critical_pairs.py
├── test_prefix_certificates.py
├── test_tier_reference_lemma.py
├── test_envelope_bruteforce_equivalence.py
├── test_fallbacks.py
└── test_counterexample_regressions.py
```

Mọi counterexample mới phải trở thành regression fixture trước khi sửa thuật toán.

## 26. Statistical protocol

- Unit/exhaustive correctness dùng exact counts, không cần significance test.
- Mechanism benchmark báo median, paired differences và bootstrap confidence intervals theo graph seed.
- Pair methods trên cùng graph/CI realization.
- Graph seed là sampling unit; không coi từng query là independent sample.
- Báo effect size và distribution, không chỉ p-value.
- Khóa primary metric và thresholds trước full run.
- Không tăng seeds chỉ vì kết quả pilot chưa đẹp; tăng theo power/precision target đã ghi.

## 27. Compute protocol

### 27.1. CPU trước

T0–T2 chủ yếu là graph logic, oracle d-separation và solver; CPU là reference phù hợp. Bắt đầu một worker để correctness, sau đó parallel theo graph seed.

### 27.2. Parallelism an toàn

- Một run/graph là unit độc lập.
- Không parallel các block trong correctness experiment đầu tiên; trước hết kiểm tra mọi serial order.
- Sau confluence mới benchmark parallel block execution.
- Worker count được giới hạn bởi RAM và solver license/threading, không chỉ logical CPUs.
- Tránh nested parallelism: process workers × BLAS/solver threads.

### 27.3. GPU gate

Chỉ mở GPU work khi một trong hai hướng qua oracle mechanism gate và profiling chỉ ra kernel vectorizable chiếm phần lớn runtime. Ứng viên:

- batched covariance/residual CI ở finite sample;
- batched scoring/envelope masks;
- simulation SEM số lượng lớn.

Graph traversal, dynamic PDS và small SAT/ILP không mặc nhiên nhanh hơn trên GPU. GPU speedup là system contribution phụ, không thay theorem.

## 28. Trình tự triển khai và checkpoint

### Sprint 0 — Reference freeze, 2–3 ngày

Deliverables:

- executable definition của reference ICD round;
- executable `A_tau` từ tier-aware reference;
- canonical equality conventions;
- motif catalog;
- artifact schemas.

Decision:

- thiếu một trong hai reference semantics thì hướng tương ứng `BLOCKED`, không được đo performance.

### Sprint 1A — Block theorem kill, 3–5 ngày

- dependency footprints;
- hand traces A-X1..A-X6;
- critical-pair checker;
- exhaustive small graphs;
- minimal counterexample reducer.

Decision: `A_THEORY_SURVIVES`, `A_REVISE_PREFIX`, hoặc `KILL-A`.

### Sprint 1B — Tier lemma/envelope kill, 3–5 ngày

- reproduce B-T0;
- brute-force uncertainty sets;
- envelope computation prototype;
- B-X1..B-X8;
- exact-PAG equivalence on small graphs.

Decision: `B_THEORY_SURVIVES`, `B_REVISE_SCOPE`, hoặc `KILL-B`.

Hai sprint có thể dùng chung graph catalog nhưng không dùng kết quả của nhau để đổi threshold.

### Sprint 2 — Headroom pilots, 3–4 ngày mỗi hướng sống sót

- 10 seeds/cell;
- oracle policy/true-tier upper bounds;
- decomposition và coverage–shrinkage frontiers;
- full cost accounting.

Decision: `GO_MECHANISM`, `RESTRICTED_GO` hoặc `NO_HEADROOM`.

### Sprint 3 — Non-oracle prior, 4–6 ngày

Chỉ cho hướng sống sót:

- synthetic prior với independent/correlated errors;
- graph-only policy hoặc grouped uncertainty;
- K1 scheduler baseline;
- no-leak calibration.

LLM vẫn chưa cần thiết.

### Sprint 4 — Finite sample và scale

Chỉ sau `GO_MECHANISM`:

- finite-sample CI;
- larger graphs;
- profiling;
- quyết định có GPU hay không;
- sau cùng mới case study LLM.

## 29. Bảng quyết định chéo

| Blockwise ICD | Robust tier | Quyết định |
|---|---|---|
| GO | GO | Chọn một core contribution theo strength; hướng kia làm complementary method/ablation |
| GO | KILL | Tập trung block decomposition; tier prior chỉ dùng rank blocks |
| KILL | GO | Tập trung robust candidate envelope; giữ K1 scheduler làm fallback |
| RESTRICTED | RESTRICTED | Tìm giao miền có cấu trúc rõ; không gộp hai heuristic tùy tiện |
| KILL | KILL | Quay lại exact dcFCI/PAG branch-and-bound hoặc công bố negative boundary; không cứu bằng LLM/GPU |

Không hợp nhất hai hướng trước khi từng hướng qua gate riêng. Nếu gộp sớm, mismatch sẽ không còn truy được về block logic hay tier pruning.

## 30. Deliverables để bước sang implementation plan đầy đủ

Mỗi hướng phải có đủ:

1. `definitions.md` với semantics executable;
2. `claim_ledger.yaml` chứa assumptions, success và kill rules;
3. motif fixtures;
4. reference implementation tests;
5. exhaustive falsification report;
6. headroom pilot report;
7. một quyết định `GO/REVISE/KILL` có chữ ký config digest.

Chỉ sau đó mới lập implementation plan production-scale, tối ưu worker/GPU hoặc sinh raw output lớn.

---

## 31. Kết luận thực thi

Bước code đầu tiên không phải scheduler mới hay solver lớn. Nó là **đóng băng hai reference semantics**:

1. một global ICD refinement round chính xác;
2. candidate restriction \(A_\tau\) chính xác của tier-aware FCI.

Sau đó xây motif catalog và exhaustive checker. Đây là con đường ngắn nhất để loại các ý tưởng nghe hợp lý nhưng sai về PAG/PDS trước khi tiêu compute.

Thứ tự ưu tiên cuối:

1. reference semantics;
2. hand counterexamples;
3. exhaustive oracle correctness;
4. decomposition hoặc shrinkage headroom;
5. synthetic imperfect prior;
6. finite sample;
7. LLM;
8. GPU.

Nếu hai hướng sống sót đến bước 4, khi đó mới có đủ bằng chứng để viết implementation plan chi tiết cho thuật toán sẽ trở thành đóng góp chính.
