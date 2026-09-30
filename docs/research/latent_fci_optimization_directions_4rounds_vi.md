# Các hướng tối ưu thuật toán cho khám phá nhân quả có biến ẩn

**Tên làm việc:** Research Portfolio after Four-Round Literature Debate  
**Ngày tổng hợp:** 2026-09-30  
**Trạng thái:** Danh mục giả thuyết để thử–sai; chưa phải thiết kế thuật toán cuối cùng  
**Giả định điều hành:** K1 được coi là `PASS` cho đến khi có đính chính  
**Phạm vi:** FCI/RFCI/ICD/dcFCI, đầu ra PAG, tồn tại latent confounding, prior từ chuyên gia hoặc LLM có thể sai và sai tương quan

## 1. Kết luận điều hành

Đóng góp kiểu OP-PDS hoặc chỉ đổi thứ tự một số kiểm định là chưa đủ mạnh để làm đóng góp khoa học chính. K1 có thể chứng minh rằng PDS/query scheduling có headroom tính toán, nhưng không tự tạo novelty trước các công trình đã có.

Các công trình gần nhất đã bao phủ phần lớn không gian “prior hướng dẫn thứ tự kiểm định”:

- Guess2Graph dùng expert để đổi thứ tự edge và conditioning set trong PC;
- Anytime FCI và ICD đã trả kết quả trung gian sound theo global conditioning depth;
- lFCI đã xây local separator pools;
- FCIT đã có score initialization, recursive path blocking, targeted CI tests và kiểm tra well-formed PAG.

Vì vậy, một hướng mới chỉ đủ tầm khoa học nếu tạo ra ít nhất một trong các kết quả sau:

1. một loại trạng thái PAG trung gian mới có soundness/confluence guarantee;
2. một semantics robust mới cho prior sai tương quan;
3. một exact search procedure trên PAG với admissible bound đặc thù cấu trúc;
4. một query/stopping certificate có complexity result không chỉ là scheduling heuristic.

Portfolio đề xuất gồm năm hướng:

| Ưu tiên | Hướng | Trạng thái |
|---:|---|---|
| 1 | Blockwise Asynchronous ICD | Pilot ưu tiên, theorem-first |
| 2 | Fallible-Tier Robust Envelope | Pilot rẻ song song |
| 3 | Exact dcFCI/PAG Branch-and-Bound | Moonshot lý thuyết/tính toán |
| 4 | Gamma-Robust Endpoint Sensitivity | Hướng backup, thay đổi phạm vi |
| 5 | Active r-PAG Witness Search | Exploratory, chỉ làm sau |

Không nên tiếp tục phát triển OP-PDS thành phương pháp cuối. Giữ K1 và OP-PDS làm baseline, bằng chứng về headroom và negative/positive motivation.

---

## 2. Corpus đã đọc và bài học thuật toán

### 2.1. Guess2Graph

Nguồn: [From Guess2Graph](https://arxiv.org/abs/2510.14488).

Guess2Graph đã chiếm claim tổng quát rằng expert có thể thay đổi thứ tự statistical tests mà không trực tiếp thay outcome.

- `PC-Guess` ưu tiên edge và candidate separating sets theo expert.
- `gPC-Guess` đổi control flow thành edge-first để tận dụng expert mạnh hơn.
- Lý thuyết chủ yếu ở DAG/causal sufficiency.
- Expert được mô hình hóa gần như một symmetric binary channel với lỗi độc lập.
- Conditioning-set ordering trong một candidate universe cố định chủ yếu tác động runtime.

Các ý tưởng sau không còn đủ novelty nếu đứng riêng:

- port edge/PDS ordering sang FCI;
- confidence-weighted ordering;
- one-probe hoặc multi-probe mà không có PAG theorem mới;
- chọn expert, reprompt hoặc update confidence online;
- batching/GPU đơn thuần.

Khoảng trống còn lại là latent confounding, correlated advice error, PAG-level correctness và budgeted partial output.

### 2.2. RFCI

Nguồn: [Learning high-dimensional DAGs with latent and selection variables](https://arxiv.org/abs/1104.5617).

FCI gồm các khối chính:

1. adjacency search để lấy initial skeleton;
2. orient unshielded triples;
3. exhaustive search trên Possible-D-SEP để tìm final skeleton;
4. orient lại v-structures;
5. áp dụng R1–R10 để hoàn thiện PAG.

Bottleneck chính là bước Possible-D-SEP. RFCI không chỉ reorder PDS; nó bỏ exhaustive PDS search và dùng các local adjacency tests kèm các kiểm tra cần thiết trước khi orient triples/discriminating paths.

Đổi lại:

- RFCI nhanh hơn rất nhiều;
- cạnh vắng vẫn có separator certificate;
- cạnh còn lại có nghĩa yếu hơn cạnh trong FCI;
- RFCI-PAG có thể đại diện nhiều MEC;
- tails và arrowheads được trả vẫn sound trong oracle setting.

RFCI đã gợi ý họ `PDS_k`, nối `k=1` gần RFCI với `k=|V|-2` gần FCI. Vì vậy, dùng prior chọn một global cutoff không đủ mới.

Khoảng trống đáng chú ý là một refinement procedure không đồng đều theo region nhưng mọi intermediate output vẫn sound.

### 2.3. tFCI và tIOD

Nguồn: [Constraint-based causal discovery with tiered background knowledge](https://arxiv.org/abs/2503.21526).

Kết quả cốt lõi: nếu tier ordering đúng, một pair có thể tách được thì tồn tại separator trong past của một endpoint. Do đó simple tFCI có thể thay:

\[
PDS(X,Y)
\quad\text{bằng}\quad
PDS(X,Y)\cap past_\tau(X,Y)
\]

mà oracle output vẫn bằng FCI.

Giới hạn:

- tier knowledge được giả định đúng;
- một critical tier error có thể loại valid separator;
- full tFCI sound nhưng có thể chưa complete vì thiếu orientation rules tổng quát;
- finite-sample improvement chưa được thiết lập đầy đủ;
- tIOD giả định các dataset là marginal của cùng một joint MAG.

Đây là động lực trực tiếp cho robust tier uncertainty, nhưng phép union qua nhiều tier hypotheses có nguy cơ phình trở lại full PDS.

### 2.4. dcFCI

Nguồn: [dcFCI](https://arxiv.org/abs/2505.06542).

dcFCI thay một chuỗi CI decisions duy nhất bằng search trên nhiều candidate r-PAG:

1. tìm potential minimal separators ở depth `r`;
2. sinh các combination của uncertain independencies;
3. dựng và kiểm tra candidate r-PAG;
4. chấm điểm bằng các hypotheses cần để phân biệt skeleton và colliders-with-order;
5. giữ top-`k` candidate cho vòng tiếp theo.

Điểm khoa học mạnh là data-PAG compatibility score gắn với characterization của MEC, không phải beam search tự nó.

Giới hạn:

- greedy top-`k` có thể loại một candidate hiện chưa tốt nhưng sẽ trở thành tốt ở vòng sau;
- score phụ thuộc candidate list và các common hypotheses;
- Fréchet bounds có thể rất lỏng;
- worst-case candidate powerset tăng cực nhanh;
- chưa có cách chọn `k` tối ưu;
- future work đề cập prior integration và progressive variable expansion.

Khoảng trống là exact search hoặc certified pruning không phụ thuộc chất lượng prior.

### 2.5. RoaDs

Nguồn: [Robust Causal Discovery Under Imperfect Structural Constraints](https://ojs.aaai.org/index.php/AAAI/article/view/41001).

RoaDs gồm:

- prior alignment bằng surrogate regression/feature importance;
- data objective và knowledge objective tách riêng;
- conflict resolution bằng multi-gradient descent/Pareto optimization.

Hạn chế đối với đề tài hiện tại:

- giả định causal sufficiency;
- output DAG, không phải MAG/PAG;
- latent confounding có thể làm một non-parent nhận regression importance lớn;
- lý thuyết cần ideal/consistent constraints;
- random constraint flips chưa đại diện clustered/correlated LLM errors.

MGDA giải conflict optimization nhưng không biến prior sai thành causal evidence.

### 2.6. L2D-CD

Nguồn: [Learning to Defer for Causal Discovery](https://arxiv.org/abs/2502.13132).

L2D-CD học một gate chọn giữa pairwise statistical causal discovery và expert/LLM prediction. Nó có ích vì mô hình hóa expert reliability khác nhau theo domain.

Giới hạn:

- chỉ bivariate cause–effect;
- cần labeled training data;
- graph-level extension chưa được triển khai;
- không tạo MAG/PAG;
- chưa có global causal soundness guarantee;
- pairwise decisions trong cùng graph không độc lập.

Learning-to-defer có thể là reliability module, nhưng không đủ làm lõi thuật toán PAG.

### 2.7. Các novelty baselines bắt buộc ngoài folder

- [Anytime FCI](https://proceedings.mlr.press/r3/spirtes01a.html): có thể dừng sớm và trả output đúng nhưng ít thông tin hơn.
- [ICD](https://proceedings.neurips.cc/paper/2021/hash/144a3f71a03ab7c4f46f9656608efdb2-Abstract.html): sound, complete, anytime; tăng conditioning size cùng PDS distance.
- [lFCI](https://arxiv.org/abs/2107.03597): local-graph separator search cho latent/selection settings.
- [FCIT](https://arxiv.org/abs/2510.04263): score-guided targeted testing, recursive path blocking và well-formed PAG validation.
- [Restricted essential ancestral graphs with expert knowledge](https://arxiv.org/abs/2407.07338): thu hẹp MAG MEC bằng hard expert marks.
- [Order-independent FCI](https://jmlr.org/papers/v15/colombo14a.html): xử lý order dependence và ambiguous collider orientations.

---

## 3. Hướng 1 — Blockwise Asynchronous ICD

### 3.1. Câu hỏi nghiên cứu

ICD tăng conditioning depth đồng loạt trên toàn graph. Có thể cho các vùng khác nhau tiến ở depth khác nhau mà vẫn trả một output sound sau mỗi block hay không?

### 3.2. Core algorithm tối giản

Tại global depth `r`:

1. sinh agenda cho vòng `r+1`;
2. phân hoạch agenda thành các **PDS-closed blocks**;
3. mỗi block phải chứa đầy đủ PDS paths, separator candidates và dependencies có thể ảnh hưởng các pair trong block;
4. prior chỉ rank block;
5. refine trọn một block;
6. revalidate affected sepsets/triples và chạy sound orientation closure;
7. có thể dừng sau bất kỳ completed block nào;
8. hoàn tất mọi block phải bằng global ICD iteration `r+1`.

Prior không được:

- trả lời CI;
- loại candidate;
- xóa cạnh;
- orient endpoint;
- cung cấp ground truth.

### 3.3. Central theorem target

**Blockwise Confluence/Commutation Theorem**

Cho các PDS-closed blocks `B1,...,Bm` và refinement operators `T_Bi`:

1. mọi prefix composition trả graph có definite marks sound;
2. với các block độc lập:

\[
T_{B_i}\circ T_{B_j}
=
T_{B_j}\circ T_{B_i};
\]

3. composition của toàn bộ block operators bằng global ICD operator:

\[
T_{B_m}\circ\cdots\circ T_{B_1}
=T_{r+1};
\]

4. prior chỉ đổi time-to-information, không đổi final oracle result.

Đây là phần có novelty. “Prior chọn block trước” tự nó không phải đóng góp.

### 3.4. Counterexample phải vượt qua

Diamond DAG:

\[
A\to B\to D,
\qquad
A\to C\to D.
\]

Một separator có thể cần cả `B` và `C`. Hai local regions tách riêng đều thiếu một phần separator. Edge-specific radii hoặc blocks không PDS-closed sẽ không tái tạo global depth-2 refinement.

Một edge deletion cũng có thể tạo unshielded triple mới hoặc phá discriminating path cũ. Vì vậy local reorientation ngây thơ không đủ.

### 3.5. Oracle pilot

- exhaustive DAG/MAG với `p<=6`;
- enumerate mọi valid block order;
- handcrafted collider, discriminating-path và Scenario-S2 cases;
- random sparse/hub graphs `p=15..50` sau khi small-graph correctness qua;
- baselines: ICD, RFCI, FCI, lFCI và FCIT.

Đo:

- soundness của từng tail/arrowhead ở mọi prefix;
- final equality với global ICD/FCI target;
- block size distribution;
- information gain theo budget;
- CI test count và revalidation cost.

### 3.6. Kill thresholds

- một false definite endpoint: `KILL_THEOREM`;
- final result khác global ICD: `KILL_CONFLUENCE`;
- trên hơn 70% graph chỉ có một block chứa trên 80% nodes: `NO_DECOMPOSITION_HEADROOM`;
- oracle best block ở 25% budget không thu ít nhất 75% invariant-mark gain của full next iteration: `NO_BUDGET_VALUE`;
- không giảm ít nhất 15% time-to-target so với ICD hoặc không thắng information/query frontier của FCIT: `NO_GO`.

### 3.7. Đánh giá

**Trạng thái:** pilot ưu tiên số 1.  
**Ưu điểm:** bám sát đề cương; prior chỉ phân bổ computation; latent/PAG-specific; theorem rõ.  
**Rủi ro:** PDS dependencies có thể làm blocks collapse thành một giant component hoặc confluence có thể sai.

---

## 4. Hướng 2 — Fallible-Tier Robust Envelope

### 4.1. Câu hỏi nghiên cứu

Có thể dùng temporal/tier advice sai theo cụm để loại CI candidates mà vẫn giữ exact-FCI semantics dưới một uncertainty set rõ ràng hay không?

### 4.2. Core algorithm

Cho prior claims `K` và group-error budget `Gamma`:

\[
\mathcal T_\Gamma(K)
=
\{\tau:v_K(\tau)\le\Gamma\}.
\]

Trong đó `v_K` đếm số nhóm/source constraints bị vi phạm, không đếm các prompt lặp lại như bằng chứng độc lập.

Robust past envelope:

\[
R_\Gamma(X,Y)
=
\bigcup_{\tau\in\mathcal T_\Gamma(K)}
past_\tau(X,Y).
\]

Search pool:

\[
J_\Gamma(X,Y)
=
PDS(X,Y)\cap R_\Gamma(X,Y).
\]

Không dùng uncertain tier prior để orient cạnh.

### 4.3. Theorem target

Nếu true tier order `tau*` nằm trong `T_Gamma(K)`, oracle robust-envelope FCI trả cùng PAG với oracle FCI.

Để theorem đủ tầm paper, cần thêm ít nhất một kết quả:

- characterization của smallest universally safe envelope;
- thuật toán tính envelope không enumerate toàn bộ tier orders;
- complexity bound theo poset width/number of group violations;
- hoặc impossibility/no-free-lunch result chỉ ra khi robustness bắt buộc khôi phục full PDS.

### 4.4. Counterexample

\[
X\leftarrow Z\rightarrow Y.
\]

Separator duy nhất là `Z`. Nếu prior sai đặt `Z` ở sau cả `X,Y` và `Gamma` quá nhỏ, `Z` bị loại và cạnh giả `X-Y` tồn tại.

Nếu cho phép bất kỳ một trong nhiều `Z_i` bị mis-tiered, union qua `Gamma=1` hypotheses có thể đưa toàn bộ `Z_i` trở lại envelope. Khi đó method an toàn nhưng gần full FCI.

### 4.5. Pilot và kill thresholds

- graph `p=5..20`, gồm random và PDS-dominant/S2-enriched cases;
- prior errors: independent flips, whole-tier swaps, node/source/motif clusters;
- first measure true-tier oracle upper bound;
- sau đó mới dùng noisy uncertainty set.

Kill nếu:

- true tier vẫn chỉ giảm dưới 15% CI candidates;
- ở realistic `Gamma`, median envelope giữ trên 90% full PDS;
- có PAG mismatch khi true tier thuộc feasible set;
- chi phí xây envelope/ILP lớn hơn CI saving.

### 4.6. Đánh giá

**Trạng thái:** pilot rẻ song song.  
**Ưu điểm:** đơn giản; trực tiếp xử lý correlated prior errors; generalize tFCI.  
**Rủi ro:** theorem cơ bản có thể quá gần tFCI cộng phép union; uncertainty set có thể collapse về full search.

---

## 5. Hướng 3 — Exact dcFCI/PAG Branch-and-Bound

### 5.1. Câu hỏi nghiên cứu

Có thể thay greedy top-`k` của dcFCI bằng exact search có certificate, trong đó prior chỉ cải thiện search order nhưng không ảnh hưởng optimum hay pruning validity hay không?

### 5.2. Core algorithm

Ở mỗi depth `r`:

1. đóng băng candidate/hypothesis comparison universe;
2. state chứa partial assignments của potential minimal-separator decisions;
3. suy mandatory skeleton/collider hypotheses từ state;
4. tính admissible upper bound cho mọi valid completion;
5. prior order branches hoặc cung cấp incumbent;
6. chỉ prune bằng data-only admissible bound;
7. dừng khi incumbent top-`k` không kém frontier upper bounds;
8. trả optimality certificate hoặc anytime gap.

### 5.3. Central theorem target

**Mandatory-Closure Upper-Bound Lemma**

Với state `s`, gọi `Cl(s)` là tập hypotheses bắt buộc trong mọi valid PAG completion. Cần xây `UB(s)` sao cho:

\[
UB(s)
\ge
\max_{P\in completions(s)} Score(P),
\]

và bound phải đủ chặt, tính được mà không enumerate toàn bộ completions.

Generic theorem “B&B với admissible bound trả optimum” không đủ novelty. Đóng góp phải là PAG-specific closure/bound.

### 5.4. Khó khăn cốt lõi

Score dcFCI loại các hypotheses common trong active candidate list. Nếu pruning một candidate làm thay đổi common-hypothesis set, ranking có thể đổi sau chính quyết định pruning. Vì vậy phải:

- freeze comparison universe; hoặc
- xây candidate-independent objective/bound mới.

Nếu không giải quyết điểm này, exactness claim không đứng.

### 5.5. Pilot và kill thresholds

- exhaustive candidate enumeration ở `p=5,6` làm gold standard;
- so greedy `k=1/2`, exhaustive và B&B;
- prior: oracle/good, random, correlated/adversarial;
- sau exactness mới thử `p=7,8,10`.

Kill nếu:

- một top-`k` mismatch;
- cần enumerate candidate family mới tính được closure;
- median expanded states lớn hơn 30–50% exhaustive;
- bound ties ở phần lớn nodes;
- exact optimum không cải thiện true-PAG recovery hoặc uncertainty so với greedy dcFCI;
- không vượt được `p=8` trong resource budget thực tế.

### 5.6. Đánh giá

**Trạng thái:** moonshot.  
**Ưu điểm:** claim lý thuyết sạch; prior sai không ảnh hưởng correctness; khác Guess2Graph/FCIT.  
**Rủi ro:** state explosion; Fréchet bounds lỏng; có thể tối ưu chính xác một score chưa đủ tốt.

---

## 6. Hướng 4 — Gamma-Robust Endpoint Sensitivity

### 6.1. Scope change

Hướng này không còn tuân thủ hoàn toàn nguyên tắc “prior chỉ phân bổ computation”. Nó dùng prior để thu hẹp equivalence class, nhưng làm việc đó theo uncertainty set và trả certificate.

Nên coi đây là một hướng paper riêng về robust identifiability hoặc một analysis layer, không trộn sớm với Block-ICD.

### 6.2. Core formulation

Cho PAG `P`, prior claims `K` và group-error budget `Gamma`:

\[
\mathcal M_\Gamma(P,K)
=
\{M\in[P]:v_K(M)\le\Gamma\}.
\]

Chỉ xuất ancestral relation hoặc endpoint assertion đúng trong mọi MAG thuộc `M_Gamma`.

Với assertion `a`, định nghĩa robustness radius:

\[
\rho_K(a)
=
\min_{M\in[P],\,M\models\neg a}v_K(M).
\]

Nếu không tồn tại counterexample MAG, đặt radius là vô cùng.

Mỗi output cần:

- `entailed` kèm proof/certificate;
- `not entailed` kèm witness MAG;
- hoặc `infeasible` nếu prior budget không tương thích với PAG.

### 6.3. Theory target

- **Gamma-soundness:** nếu true MAG thuộc `M_Gamma`, không assertion được xuất sai.
- **Maximality:** không thủ tục uniformly sound trên cùng `M_Gamma` có thể xác nhận thêm assertion ngoài tập invariant.
- Một trong các kết quả không tầm thường sau:
  - exact/complete MAG encoding;
  - compact representation của restricted class;
  - điều kiện endpoint intersection tạo graph hợp lệ;
  - complexity/tractability cho một constraint family.

Soundness và maximality theo định nghĩa chưa đủ làm toàn bộ đóng góp.

### 6.4. Counterexample

PAG hai nodes:

\[
X\circ-\circ Y.
\]

Prior nói `X->Y`.

- `Gamma=0`: có thể restrict theo hard prior.
- `Gamma=1`: MAG mang direction đối nghịch quay lại feasible set.

Bất kỳ method nào vẫn force `X->Y` là unsound. Nhiều paraphrase cùng sai phải được tính như một correlated source group, không phải nhiều bằng chứng độc lập.

### 6.5. Pilot và kill thresholds

- enumerate toàn bộ MAG/PAG với `p=4,5`, sau đó `p=6..10` bằng solver;
- sinh independent và clustered ancestral errors;
- so brute force, hard knowledge và robust method;
- đo true-MAG retention, resolved circles và solver time.

Kill headline nếu:

- có false certified relation;
- ở `Gamma=1`, trên 80–90% graphs output trở về original PAG;
- median circle reduction dưới 5–10% khi prior có ích;
- solver không scale qua `p=8..10`;
- solver tương đương existing restricted-essential-graph method mà không có theorem mới.

### 6.6. Đánh giá

**Trạng thái:** backup/auxiliary direction.  
**Ưu điểm:** trực tiếp xử lý arbitrary correlated errors; scientific semantics rõ.  
**Rủi ro:** thay đổi phạm vi; theorem cơ bản gần tautology; robust class có thể mất gần hết gain.

---

## 7. Hướng 5 — Active r-PAG Witness Search

### 7.1. Core idea

Version space phải chứa distinct r-PAG/MEC independence models, không chứa individual MAGs trong cùng MEC:

\[
\mathcal H_t
=
\{P:P\text{ phù hợp với các CI outcomes đã thấy}\}.
\]

Một query `q=(X,Y|S)` chia candidates theo m-separation prediction. Chọn query giảm worst-case survivor set hoặc phủ nhiều candidate pairs nhất.

Prior chỉ tie-break/reweight. Nó không được hard-delete candidates nếu không có error-set certificate.

### 7.2. Theory target

- mọi hai candidate r-PAG khác nhau phải có ít nhất một essential CI witness;
- stopping chỉ khi mọi survivors cùng PAG;
- witness-set hoặc decision-tree approximation bound;
- tốt hơn nữa: structural split bound theo PDS width/treewidth.

Generic generalized-binary-search hoặc set-cover theorem chỉ là mức tối thiểu; có thể bị xem là application của kết quả cũ.

### 7.3. Counterexample

Có thể xây star version space gồm một baseline PAG và nhiều candidates, mỗi candidate chỉ khác trên một unique high-order CI. Mỗi query chỉ loại một candidate. Không có balanced split và query complexity gần tuyến tính.

Nếu version space chứa MAGs cùng MEC, không observational CI query nào phân biệt được chúng.

### 7.4. Pilot và kill thresholds

- enumerate r-PAG candidates ở `p=4..6`;
- exact optimal decision tree làm comparator;
- so greedy minimax, witness cover, ICD và FCIT query sets;
- đo query saving và candidate-maintenance overhead.

Kill nếu:

- candidate pool không pairwise separable;
- median best split giữ trên 90% candidate mass;
- greedy dùng hơn 2 lần optimum queries;
- unique-query saving dưới 20% so với ICD/FCIT;
- version-space overhead lớn hơn saved CI runtime.

### 7.5. Đánh giá

**Trạng thái:** exploratory, hoãn.  
Chỉ nên thử sau khi có candidate enumerator từ hướng dcFCI hoặc Gamma-robust solver.

---

## 8. Kế hoạch thử–sai đề xuất

### Sprint A — Block-ICD theorem kill

1. Cài hoặc wrap oracle ICD.
2. Định nghĩa PDS-closed dependency graph.
3. Sinh blocks bằng connected components của dependency relation ban đầu.
4. Exhaustive small-graph search để tìm counterexample cho confluence.
5. Chưa dùng LLM, GPU hoặc finite-sample CI.

Kết quả:

- confluence fail nhanh: dừng hướng;
- confluence đúng nhưng giant-block collapse: negative structural result;
- confluence và useful decomposition: viết proof trước khi làm scheduler.

### Sprint B — Robust-tier collapse test

1. Sinh true tiers từ topological layers.
2. Đo upper bound với perfect tier.
3. Corrupt theo source/motif/tier clusters.
4. Tính robust envelope theo `Gamma`.
5. Đo envelope/PDS ratio và exact PAG.

Kết quả:

- perfect tier không có headroom: dừng;
- robust envelope gần full PDS: dừng hoặc viết no-free-lunch result;
- envelope nhỏ và safe: phát triển compact solver/theory.

### Sprint C — dcFCI bound feasibility

1. Đóng băng objective và candidate universe.
2. Exhaustive candidate generation ở `p<=6`.
3. Xây mandatory closure.
4. Chứng minh/check admissibility bằng enumeration.
5. Đo explored-state fraction.

Kết quả:

- bound invalid: dừng;
- bound valid nhưng lỏng: negative result;
- bound valid và prune mạnh: nâng thành main method candidate.

### Sprint D — Robust endpoint utility

1. Enumerate MAGs/PAGs nhỏ.
2. Build exact violation-budget filter.
3. Trả invariant assertions và witness MAGs.
4. Vẽ sensitivity path theo `Gamma`.
5. Novelty audit với restricted essential ancestral graph literature.

### Sprint E — Active query geometry

Chỉ mở sau khi có version-space engine. Trước tiên đo split coefficient và optimal decision tree; không viết full active learner trước.

---

## 9. Gate tổng hợp

| Hướng | Điều kiện GO tối thiểu |
|---|---|
| Block-ICD | Zero false endpoint; final equality; blocks không collapse; thắng ICD/FCIT frontier |
| Robust tiers | True tier có headroom; realistic uncertainty không trả gần full PDS; exact PAG equality |
| dcFCI B&B | Exact match 100%; bound tính được rẻ; giảm ít nhất 50% states ở pilot |
| Gamma endpoints | True MAG retained; nontrivial circle resolution; complete/auditable solver |
| Active r-PAG | Pairwise witness separability; meaningful split; trên 20% query saving |

Không rescue một hướng đã fail bằng cách thêm learned router, Hedge, nhiều LLM, GPU hoặc nhiều hyperparameter.

---

## 10. Vai trò của định lý

Không cần tạo ra một lý thuyết nhân quả hoàn toàn mới như một mục tiêu hình thức. Tuy nhiên, với các từ “safe”, “robust”, “exact” hoặc “certified”, ít nhất một kết quả không tầm thường là bắt buộc.

Các theorem đủ mạnh:

- mixed-depth refinement confluence và soundness;
- equivalence-to-FCI dưới structured uncertainty set;
- admissible PAG-specific pruning bound và exact top-`k`;
- complete robust-entailment/representation result;
- PAG-specific query/stopping complexity.

Các theorem không đủ mạnh nếu đứng một mình:

- reordering không đổi kết quả khi chạy đủ mọi test;
- branch order không đổi optimum;
- intersection của feasible models là robust;
- true tier nằm trong union thì separator còn lại;
- closure của sound CI statements vẫn sound.

Một paper tốt nên có cấu trúc:

1. một giả định rõ;
2. một thuật toán nhỏ;
3. một theorem đúng đúng chỗ khó;
4. một counterexample khi giả định bị vi phạm;
5. oracle experiment để tách lỗi thuật toán khỏi lỗi thống kê;
6. finite-sample và imperfect-prior experiments sau khi oracle gate qua.

---

## 11. GPU và tối ưu hệ thống

GPU là secondary engineering contribution, không phải scientific core của portfolio này.

GPU phù hợp cho:

- batch CI tests có cùng conditioning size;
- covariance, matrix factorization và regression residualization;
- kernel CI/HSIC computations;
- chấm điểm nhiều candidate PAG;
- vectorized evaluation của nhiều constraints;
- chạy nhiều graph/seed song song.

CPU vẫn phù hợp hơn cho:

- graph traversal;
- PDS path generation;
- PAG validity/maximality checks;
- orientation rules;
- branch-and-bound control logic;
- SAT/ASP orchestration.

Nguyên tắc đánh giá:

1. trước tiên giảm số unique logical queries;
2. sau đó batch các query còn lại;
3. so GPU với optimized/vectorized CPU;
4. báo crossover theo `n`, `p`, conditioning size và CI-test type;
5. GPU không được thay đổi query set, graph semantics hoặc output.

Không dùng GPU speedup để cứu một hướng không có novelty hoặc không vượt kill test.

---

## 12. Vai trò của K1 và artifact hiện tại

Với giả định K1 PASS, có thể dùng kết quả hiện tại để hỗ trợ các phát biểu hẹp:

- PDS scheduling có headroom;
- prior tổng hợp có tín hiệu;
- implementation/evaluator đủ để làm baseline;
- correlated-prior benchmark đã có giá trị tái sử dụng.

K1 không chứng minh:

- Block-ICD confluence;
- mixed-depth partial PAG soundness;
- robust-tier coverage;
- exact dcFCI optimization;
- Gamma-robust identification;
- novelty trước ICD/lFCI/FCIT.

Artifact K1 nên được giữ nguyên và dùng làm:

- empirical motivation;
- regression/conformance baseline;
- negative comparison cho scheduling-only approaches;
- source của graph/prior/error generators.

---

## 13. Quyết định cuối sau bốn vòng debate

1. Không nâng OP-PDS thành final paper method.
2. Bắt đầu bằng hai falsification sprint độc lập:
   - Blockwise Asynchronous ICD;
   - Fallible-Tier Robust Envelope.
3. Song song, làm một feasibility prototype rất nhỏ cho exact dcFCI B&B.
4. Chỉ dùng Gamma-Robust Endpoint Sensitivity nếu muốn chuyển trọng tâm từ compute allocation sang robust causal identifiability.
5. Hoãn Active r-PAG Witness Search cho tới khi có candidate/version-space engine.
6. LLM thực tế chỉ vào sau controlled-prior oracle experiments.
7. GPU chỉ vào sau khi central algorithmic claim đã qua kill test.

Portfolio này cố ý giữ các failure mode độc lập:

- Block-ICD có thể fail vì refinement operators không commute hoặc graph không decomposable;
- robust tiers có thể fail vì uncertainty envelope collapse;
- dcFCI B&B có thể fail vì bound quá lỏng;
- Gamma endpoints có thể fail vì robust class không còn informativeness;
- active query có thể fail vì version space không có balanced witnesses.

Đây là thiết kế try-and-fail phù hợp: mỗi hướng có một câu hỏi toán học riêng, một phản ví dụ rõ và một pilot nhỏ có thể bác bỏ trước khi tiêu API, GPU hoặc hàng chục GB output.
