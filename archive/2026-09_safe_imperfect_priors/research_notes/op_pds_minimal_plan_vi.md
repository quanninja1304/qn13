# Kế hoạch nghiên cứu tối giản: One-Probe Possible-D-SEP

**Tên làm việc:** OP-PDS — One-Probe Possible-D-SEP
**Trạng thái:** kế hoạch falsification screen sau ba vòng tranh luận; chưa phải claim paper.
**Giả định điều hành:** K1 được coi là PASS cho việc lập kế hoạch, nhưng mọi validation mới vẫn phải chờ K1 thực tế hoàn tất.
**Nguyên tắc:** một ý tưởng, một can thiệp cục bộ, một định lý đường đi và một thí nghiệm có thể bác bỏ nó.

## 1. Kết quả của ba vòng tranh luận

| Vòng | Câu hỏi | Kết luận |
|---|---|---|
| 1 | FREW, pair-wave, Hedge và GPU có phải đóng góp khoa học tốt không? | Không. Chúng trộn quá nhiều cơ chế, khó quy kết hiệu quả và không giải quyết trực tiếp phần đặc thù của FCI. |
| 2 | Nên sắp lại toàn bộ danh sách hay chỉ thử một đề xuất rồi fallback? | Chỉ one-probe. Full ranking quá gần Guess2Graph và có thể chịu regret tuyến tính khi prior sai. |
| 3 | One-probe đã đủ thành phương pháp cuối chưa? | Chưa. Nó đủ sạch để chạy một falsification screen; chỉ được nâng thành hướng paper nếu PDS có headroom, prior thắng control và nghĩa vụ PAG được giải quyết. |

Các thành phần sau bị loại khỏi đóng góp khoa học chính:

- FREW, Hedge, Beta update và expert mixture;
- pair-wave, completion tail và learned router;
- GPU, batching, cache và checkpointing;
- thay đổi FAS trong pilot đầu tiên;
- LLM prior và finite-sample CI trước khi oracle screen qua.

GPU có thể được dùng sau này như executor engineering, nhưng không phải thuật toán hay novelty claim.

## 2. Câu hỏi nghiên cứu đã thu hẹp

> Trong bước Possible-D-SEP đặc thù của FCI, liệu một prior không đáng tin chỉ được phép đề xuất đúng một kiểm định hợp lệ có thể tạo shortcut đáng kể, trong khi một đề xuất sai chỉ làm tốn thêm tối đa một CI test cục bộ?

Đây là câu hỏi tốt hơn bản FREW vì:

1. can thiệp duy nhất nằm ở phần đặc thù của FCI với biến ẩn;
2. prior không xóa cạnh, định hướng cạnh hoặc thay CI outcome;
3. lợi ích và thiệt hại có công thức chính xác trên từng search episode;
4. lỗi prior có thể tương quan hoặc đối nghịch mà cận regret vẫn đúng;
5. nếu oracle one-probe không có headroom thì dừng, không thêm module để cứu kết quả.

## 3. Thuật toán OP-PDS

### 3.1. Phần giữ nguyên

- Stable FAS chạy nguyên trạng.
- Preliminary orientations trước Possible-D-SEP giữ nguyên.
- Thứ tự pair, graph commit, CI backend và toàn bộ orientation rules giữ nguyên.
- Prior chỉ được đọc sau khi danh sách candidate hợp lệ của một PDS episode đã được tạo.
- Mọi thay đổi đồ thị vẫn phải xuất phát từ CI outcome và quy tắc FCI.

### 3.2. Một PDS episode

Với một pair đang được FCI xử lý, baseline cố định có danh sách hữu hạn:

\[
L_e=(q_1,q_2,\ldots,q_m),\qquad q_i=(X,Y\mid Z_i),
\]

trong đó mọi `q_i` đều thuộc đúng candidate family Possible-D-SEP hợp lệ của baseline. Danh sách, thứ tự, chi phí và digest của nó được đóng băng trong suốt episode.

Prior được phép trả về nhiều nhất một candidate `q*` thuộc `L_e`:

1. Nếu prior abstain, đề xuất không hợp lệ hoặc `q*=q1`, chạy baseline.
2. Nếu có `q*` hợp lệ, kiểm định `q*` đúng một lần.
3. Nếu `q*` độc lập, dùng chính CI evidence đó để thực hiện edge deletion/sepset operation chuẩn của FCI và dừng episode.
4. Nếu `q*` phụ thuộc, quay lại đúng thứ tự `L_e`, bỏ qua `q*` khi gặp lại.

Không có update online, không học trọng số và không mở probe thứ hai.

### 3.3. Interface prior tối thiểu

Pilot dùng Prior B như một **controlled synthetic advice channel**, không gọi nó là chuyên gia thực tế hay LLM prior.

Với claim đã materialize `a_ijz`, score của một candidate là:

\[
s(Z\mid i,j)=\frac{1}{|Z|}\sum_{z\in Z}a_{ijz}-0.05|Z|.
\]

`q*` là candidate có score lớn nhất trong `L_e`; tie-break theo canonical order. Map từ claims sang `q*`, seed lỗi và corruption parameter phải được khóa trên development graphs. Validation không được reroll prior cho tới khi AUC rơi vào vùng mong muốn.

Global AUC chỉ là diagnostics. Đại lượng giải thích trực tiếp là:

- top-one separator hit rate;
- baseline stopping rank/cost khi probe đúng;
- tỷ lệ `LATE` khi probe sai;
- hit reward và miss penalty trong cost identity.

## 4. Kết quả lý thuyết cốt lõi

### 4.1. Định lý cục bộ

Giữ cố định một episode `e`, danh sách `L_e`, chi phí dương `c_i` và oracle outcomes. Baseline dừng ở separator đầu tiên có rank `r`; đặt:

\[
T_B=r,\qquad C_B=\sum_{i=1}^{r}c_i.
\]

Nếu không có separator, baseline exhaust toàn danh sách.

Gọi `q*=q_j`, `c*=c(q*)`. Khi đó:

| Trường hợp | Số test OP-PDS | Chi phí OP-PDS |
|---|---:|---:|
| Không có separator trong `L_e` | `T_B` | `C_B` |
| `q*` là separator | `1` | `c*` |
| `q*` sai và `j<r` | `T_B` | `C_B` |
| `q*` sai và `j>r` | `T_B+1` | `C_B+c*` |

Do đó, trên mọi episode:

\[
T_{OP}(e)\le T_B(e)+1,
\]

\[
C_{OP}(e)\le C_B(e)+c(q^*).
\]

Nếu `S_e` là sự kiện probe tìm separator và `LATE_e` là sự kiện probe sai nằm sau điểm baseline vốn đã dừng, thì identity chính xác là:

\[
T_B-T_{OP}=(T_B-1)\mathbf 1\{S_e\}-\mathbf 1\{LATE_e\},
\]

\[
C_B-C_{OP}=(C_B-c^*)\mathbf 1\{S_e\}-c^*\mathbf 1\{LATE_e\}.
\]

Đây mới là điều kiện superiority cần đo. Không suy lợi ích từ AUC 0.65 và không dùng công thức `pi>1/r` ngoài mô hình đồng nhất đặc biệt.

### 4.2. Cận toàn graph

Nếu graph `g` có `L_g` PDS episodes thực sự được probe:

\[
N_{OP,g}\le N_{B,g}+L_g,
\]

\[
C_{OP,g}\le C_{B,g}+\sum_{e=1}^{L_g}c(q^*_e).
\]

Không thêm global cap kiểu `K=p`; đó là tham số tùy tiện và làm lẫn nguyên nhân thất bại. Nếu sau này cần risk budget vận hành, nó là option hệ thống, không thuộc scientific core.

### 4.3. Phạm vi của minimax statement

Chỉ được phát biểu hẹp:

> Với một policy tất định đã quyết định chạy một off-prefix proposal trước `q1`, một đối thủ có thể làm proposal sai và `q1` đúng, buộc policy trả đúng thêm một test với chi phí `c*`.

Không tuyên bố minimax phổ quát đối với randomized/abstaining policies.

### 4.4. Điều được bảo đảm và chưa được bảo đảm

Có thể chứng minh ngay:

- cùng adjacency-deletion decision trên một frozen episode;
- cùng oracle Step-D skeleton với baseline bằng quy nạp theo pair order, nếu candidate coupling đúng;
- local count/cost identity và regret bound;
- asymptotic skeleton consistency dưới các giả định chuẩn và uniformly consistent CI tests.

Chưa được coi là đã chứng minh:

- bitwise-identical sepset trace;
- exact final PAG equality;
- finite-sample no-harm;
- runtime speedup;
- utility của LLM hoặc expert ngoài đời.

## 5. Nghĩa vụ lý thuyết quyết định: separator invariance

Trước main experiment phải chứng minh hoặc viện dẫn chính xác một lemma cho FCI variant thực tế:

> Thay separating set canonical bằng một separating set oracle-valid khác lấy từ đúng Step-D family không làm sai các membership predicates dùng trong unshielded-collider và discriminating-path orientations; với complete orientation rules, kết quả vẫn là PAG đúng `P*`.

Nếu lemma này không đứng vững:

- thu hẹp theorem về skeleton equivalence;
- giữ exact PAG equality như empirical conformance gate;
- không dùng từ “safe PAG algorithm”.

Bốn mươi graph khớp nhau không thay thế cho chứng minh phổ quát.

## 6. Tính mới và ranh giới so với Guess2Graph

[Guess2Graph](https://arxiv.org/html/2510.14488v1) đã dùng expert để sắp thứ tự edge và conditioning sets trong PC, đồng thời chứng minh các kết quả kỳ vọng dưới mô hình expert accuracy. Vì vậy, “prior chỉ đổi thứ tự test” không còn đủ novelty.

OP-PDS chỉ có cơ hội mang ý nghĩa khoa học nếu đồng thời thỏa ba điểm:

1. can thiệp tạo lợi ích nằm ở Possible-D-SEP, không phải FAS;
2. bảo đảm là pathwise và distribution-free trước prior sai tương quan/đối nghịch, không dựa vào independent binary-channel errors;
3. có phân tích PAG/separator cụ thể cho FCI với latent confounding.

Additive-one identity tự nó quá sơ cấp để thành paper. Nó là nền móng để kiểm tra cơ chế, không phải claim cuối.

Ngoài Guess2Graph, trước claim paper vẫn phải đối chiếu RFCI, FCIT/targeted testing và các phương pháp dùng ít CI tests. [Order-independent causal discovery](https://jmlr.org/papers/v15/colombo14a.html) cũng là nguồn bắt buộc cho phần order/sepset analysis.

## 7. Pilot khóa trước: 40 oracle graphs

### 7.1. Chọn cell không dựa trên kết quả thuận lợi

Không chọn `degree=4` vì đó có thể là cell thuận lợi sau khi xem K1. Dùng một slice mới, có lý do cấu trúc và chưa được chọn từ outcome:

| Cell | p quan sát | Mean degree | Latent ratio | Seeds |
|---|---:|---:|---:|---:|
| C1 | 20 | 2.5 | 0.2 | 20 new seeds |
| C2 | 20 | 2.5 | 0.4 | 20 new seeds |

Seed manifest phải được tạo và hash trước khi sinh graph. Đây là mechanism screen, không phải bằng chứng khái quát hóa.

### 7.2. Phương pháp

| ID | Phương pháp | Vai trò |
|---|---|---|
| M0 | Frozen canonical FCI baseline | Reference |
| M1 | OP-PDS + Prior B motif-correlated | Phương pháp cần kiểm tra |
| M2 | OP-PDS + strongest frozen prior-free proposal | Control cho lợi ích của generic probing |
| M3 | OP-PDS + within-episode cost-matched hashed proposal | Placebo cho thông tin prior |
| O | Oracle best eligible one-probe, shadow replay | Headroom ceiling, không dùng để tune |

`M2` phải được chọn một lần trên development data, không chọn winner theo validation cell. `M3` giữ cùng số lần proposal/abstention và cùng `|Z|` với M1 nhưng chọn candidate hợp lệ bằng hash đã khóa. Oracle `O` chọn eligible separator có chi phí nhỏ nhất; nếu không có separator, dùng rule đã đăng ký trước.

Executor là serial CPU giống nhau cho mọi method. Không cache, batch, GPU, LLM hoặc finite-sample CI trong pilot này.

### 7.3. Log bắt buộc trên từng episode

- graph id, pair id và episode id;
- baseline state digest và candidate-list digest;
- `m`, first-success rank `r`, proposal rank `j`;
- `q*`, `|Z*|`, `c*`, valid/abstain status;
- hit indicator và `LATE` indicator;
- observed/predicted calls và weighted cost;
- hit reward, miss penalty;
- Step-D skeleton digest và final PAG digest.

### 7.4. Metrics

Primary graph-level effect:

\[
d_g=\frac{N_{B,g}-N_{M1,g}}{N_{B,g}},
\]

với `N` là tổng logical CI calls của full FCI run.

Bootstrap phải paired theo graph seed và stratified theo cell; không dùng edge hoặc episode làm mẫu độc lập.

Oracle recovery dùng tỷ số aggregate, không lấy trung bình các graph-wise ratios:

\[
R=\frac{\sum_g(N_{B,g}-N_{M1,g})}
        {\sum_g(N_{B,g}-N_{O,g})}.
\]

Mẫu số phải dương trong cả hai cell.

## 8. Gates theo đúng thứ tự

### G0 — Implementation identity

- candidate digest khớp baseline;
- fallback bằng chính xác baseline order sau khi bỏ `q*`;
- observed count/cost khớp identity trên 100% episodes;
- `N_OP-N_B<=L_g` trên mọi graph.

Thất bại: `INVALID_IMPLEMENTATION`.

### G1 — Oracle output conformance

- Step-D skeleton giống baseline trên 40/40 graphs;
- final endpoint/PAG digest giống baseline trên 40/40 graphs;
- thêm exhaustive tiny-graph conformance suite.

Thất bại PAG không bác local theorem, nhưng tạo `PAG_SAFETY_UNPROVEN` và dừng mọi exact-PAG claim.

### G2 — Calibration và headroom

- Prior B corruption được calibrate ở development rồi freeze;
- validation prior không được reroll;
- báo cáo PDS macro-AUC và top-one hit rate;
- oracle one-probe gain dương ở cả hai cell.

Sai protocol/AUC ngoài tolerance đã khóa: `BLOCKED_CALIBRATION`.
Oracle không có gain đáng kể: `NO_PDS_HEADROOM`.

### G3 — Efficacy so với prior-free mạnh nhất

M1 phải đạt đồng thời:

- median `d_g >= 0.08` so với best frozen prior-free method trong M0/M2;
- paired stratified bootstrap 95% lower bound `>0`;
- cellwise median không âm ở cả C1 và C2.

Thất bại: `BOUNDED_NEGATIVE_RESULT`.

### G4 — Prior specificity

M1 phải thắng M3 trên paired graph effects với bootstrap lower bound `>0`.

Thất bại: `PLACEBO_ONLY`.

### G5 — Oracle recovery

`R>=0.30` trên aggregate và oracle denominator dương trong cả hai cell.

Thất bại: `PRIOR_TOO_WEAK`.

Qua G0–G5: `PILOT_GO_PDS`.

`PILOT_GO_PDS` chỉ cho phép mở rộng thí nghiệm. Nó không cho phép claim finite-sample safety, LLM utility, GPU acceleration hoặc publication-level novelty.

## 9. Trình tự implementation tối thiểu

### Bước 0 — Proof và baseline audit

1. Pin commit/config của v1 và không sửa artifact K1.
2. Xác định chính xác FCI Step-D semantics của implementation đang dùng.
3. Viết local theorem và thử chứng minh separator-invariance lemma.
4. Chọn một frozen prior-free baseline từ development/K1, không theo validation cell.

**Dừng** nếu không thể tạo canonical coupled PDS episode mà không thay đổi baseline semantics.

### Bước 1 — PDS trace/replay

1. Tách deterministic candidate enumerator cho một PDS episode.
2. Ghi list/state digest, query cost và oracle outcome vector.
3. Xây shadow replay cho M2/M3/O.
4. Kiểm tra replay baseline cho output và query trace giống reference.

### Bước 2 — OP wrapper

1. Validate `q*` thuộc đúng frozen list.
2. Chạy one-probe rồi canonical fallback.
3. Không cho prior truy cập CI outcome chưa query, DAG/MAG/PAG truth hoặc oracle labels.
4. Ghi exact accounting terms.

### Bước 3 — Unit/conformance tests

- bốn trường hợp của local theorem;
- invalid proposal và abstention;
- `q*=q1` là baseline;
- no-separator exhaustion không tăng calls;
- fallback exactly-once, không duplicate/drop query;
- correlated/adversarial prior vẫn giữ regret bound;
- per-pair và per-graph digests;
- tiny-graph exhaustive PAG comparison.

### Bước 4 — Freeze rồi chạy pilot

1. Freeze proposal rule, corruption parameter, seeds, baseline và bootstrap seed.
2. Sinh 40 graph mới một lần.
3. Chạy gates G0→G5 theo thứ tự.
4. Không retune sau khi mở kết quả.

## 10. Sau pilot

Chỉ khi `PILOT_GO_PDS`:

1. hoàn tất separator-invariance proof hoặc thu hẹp claim;
2. mở rộng oracle matrix đại diện, không chỉ hai cell;
3. thêm independent/correlated/adversarial prior comparison;
4. chạy finite-sample Fisher-Z với evaluator đã sửa và khóa;
5. so RFCI/FCIT/targeted baselines;
6. cuối cùng mới đánh giá LLM prior;
7. chỉ sau khi logical-query contribution đứng vững mới tối ưu CPU/GPU executor như một systems layer tách biệt.

Nếu pilot fail, kết luận có giá trị là:

> Một speculative PDS query có regret bị chặn là cơ học hợp lệ, nhưng PDS headroom hoặc prior signal không đủ để tạo đóng góp end-to-end.

Không quay lại FREW, Hedge, multi-probe, learned scheduler hay GPU để che một cơ chế đã fail.

## 11. Claim được phép ở từng mốc

| Mốc | Claim tối đa |
|---|---|
| Trước pilot | Một giả thuyết và local search theorem |
| Qua G0–G2 | Implementation đúng và có one-probe headroom |
| Qua G0–G5 | Prior tổng hợp có tín hiệu PDS trong oracle mechanism screen |
| Có separator-invariance proof | Oracle PAG correctness cho variant đã định nghĩa |
| Qua finite-sample + strong baselines | Bằng chứng thực nghiệm về usefulness, chưa mặc nhiên là LLM utility |
| Qua external/LLM validation | Claim ứng dụng có giới hạn theo domain đã test |

## 12. Quyết định cuối của ba vòng debate

OP-PDS được **chấp nhận để falsify**, chưa được chấp nhận như final paper method.

Lý do giữ lại:

- cực đơn giản;
- cận thiệt hại pathwise rõ ràng;
- upside lớn khi PDS baseline phải tìm lâu;
- prior sai tương quan không phá regret bound;
- test thất bại cho câu trả lời dứt khoát.

Lý do chưa được coi là đóng góp hoàn chỉnh:

- local identity là kết quả elementary;
- novelty so với Guess2Graph chưa đóng;
- PAG separator-invariance chưa chứng minh;
- prior hiện tại vẫn là kênh tổng hợp dùng simulation truth để tạo rồi làm nhiễu;
- chưa có finite-sample, RFCI/FCIT hoặc external-prior evidence.
