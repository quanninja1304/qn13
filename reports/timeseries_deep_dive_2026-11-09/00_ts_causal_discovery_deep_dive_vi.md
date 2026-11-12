# Deep dive: causal discovery trên chuỗi thời gian (09/11/2026)

> **Bối cảnh:** user muốn đào sâu causal discovery cho dữ liệu chuỗi thời gian. Hướng tài chính đã bỏ cùng ngày (xem [`../finance_causal_scan_2026-11-09/`](../finance_causal_scan_2026-11-09/00_finance_causal_directions_vi.md)).
> **Nhãn:**
> - [Verified]: đã đọc PDF trong `docs/papers/`.
> - [Verified-code]: đã đọc code gốc trên GitHub.
> - [Verified-fetch]: đã đọc trang HTML đầy đủ.
> - [Verified-search]: chỉ qua abstract hoặc kết quả tìm kiếm.
> - [Verified-CR]: metadata đối chiếu qua Crossref hoặc arXiv API.
> - [Inference], [Hypothesis].
>
> **Chưa tải dữ liệu, chưa chạy thuật toán nào.** Do-not-redo X1–X31 không có mục nào về chuỗi thời gian. Các mục cần tránh lặp lại được ghi ở §6.

## 0. Tóm tắt

1. **Bài toán khác i.i.d. ở hai điểm.**
   - Thứ tự thời gian cho định hướng miễn phí với **link trễ** (lagged), nhưng chỉ khi có causal sufficiency và tần số lấy mẫu đủ cao.
   - Khi có **biến ẩn** hoặc **lấy mẫu thưa hoặc gộp** (subsampling, aggregation), lợi thế này mất. Kể cả link trễ cũng có thể là giả, và dữ liệu "causally underdetermined" (Butler et al. 2026, §IV-A).
2. **Phát hiện chính từ dữ liệu (xuyên suốt):**
   - **Chưa benchmark thật nào đánh giá đúng confounding ẩn.** Survey IEEE SPM 2026 gọi unobserved confounding là vấn đề mở và không nêu trường hợp nào phương pháp có biến ẩn được đánh giá trên dữ liệu thật [Verified-fetch].
   - **Tập "Confounder" của CausalRivers (ICLR 2025) thực ra không che nút confounder** trong code công khai [Verified-code, §3.1]. Tập này chỉ có 24 đồ thị (Confounder-3) [Verified].
   - CausalDynamics (NeurIPS 2025) không chạy LPCMCI [Verified]. AutoCause (2026) loại LPCMCI khỏi thí nghiệm trên CausalRivers vì chạy quá thời gian [Verified-search].
3. **Phát hiện phụ:**
   - Trên dữ liệu thật, VAR-Granger tuyến tính là phương pháp ổn định nhất, và baseline ngây thơ thường ngang các phương pháp causal (CausalRivers) [Verified].
   - Trên mô phỏng, phương pháp deep learning thua phương pháp không cần tinh chỉnh nhiều; tier đơn giản cho AUROC khoảng .50 (CausalDynamics) [Verified].
   - Siêu tham số được chọn theo nhãn, nên điểm báo cáo có thể bị thổi phồng; chính tác giả CausalRivers thừa nhận [Verified].
4. **Đề xuất:**
   - **Chính, TS-G1:** đo confounding ẩn *thật* trên CausalRivers. Biến ẩn là **mưa**. Mưa đo được qua dữ liệu DWD mà bộ công cụ có sẵn, nên có thể so cùng một đồ thị khi che và khi lộ confounder [Hypothesis về giá trị; Verified về việc có công cụ].
   - **Dự phòng, TS-G2:** chọn độ phân giải thời gian mà không dùng nhãn, đo trên dữ liệu thật 15 phút có thể gộp có kiểm soát.

   Cả hai đều mới ở mức "failure đo được". **Chưa có cơ chế phương pháp.** Theo `AGENTS.md`, phải đo failure trước rồi mới đề xuất cơ chế.

## 1. Đối tượng đồ thị và giả định

**Ba loại graph** (Butler et al., IEEE SPM 2026, §II-B) [Verified-fetch]:

| Graph | Nội dung | Ghi chú |
|---|---|---|
| Full time graph | Mỗi biến ở mỗi thời điểm là một nút | Linh hoạt nhất nhưng "intractable" |
| **Window graph** | Cửa sổ tối thiểu theo trễ τ_max; giả định causal stationarity | Biểu diễn mặc định của PCMCI, LPCMCI, SVAR-FCI |
| Summary graph | Chỉ cho biết biến nào gây ra biến nào, không có trễ; có thể có chu trình | Mức mà CausalRivers và CausalDynamics chấm điểm |

**Giả định** [Verified-fetch trừ khi ghi khác]:

| Giả định | Ý nghĩa | Khi bị vi phạm |
|---|---|---|
| Causal stationarity | Cơ chế bất biến khi dịch thời gian. **Khác** stationarity của quá trình: random walk vẫn thỏa | Trễ thay đổi theo lưu lượng (CausalRivers §3.2 [Verified]); nhiều regime |
| Causal sufficiency | Không có confounder ẩn | Butler §IV-C: "entirely untestable" |
| Faithfulness | — | Tự tương quan mạnh làm effect size của kiểm định CI nhỏ, nên recall thấp; đây là động cơ của LPCMCI [Verified-search, abstract] |
| Tần số lấy mẫu đủ cao | Không subsampling hay aggregation | Link tức thời "is often a signature of too-low sampling rate" (Butler §III-A); dữ liệu bị underdetermined (Butler §IV-A) |
| Không có lỗi đo, không thiếu dữ liệu | — | CausalRivers thiếu dưới 10% giá trị [Verified, Hình 7] |

**Hệ quả** [Inference]:
- Trong window graph, link X_{t−1} → Y_t chỉ đúng là nhân quả khi không có L ẩn sao cho L_{t−2} → X_{t−1} và L_{t−2} → Y_t.
- Biến ẩn **có tự tương quan** (như mưa, nhiệt độ, nhân tố thị trường) làm điều này xảy ra ở mọi độ trễ. Granger không phân biệt được.

## 2. Bản đồ phương pháp

| Họ | Phương pháp | Venue | Output | Biến ẩn | Link tức thời | Nhãn |
|---|---|---|---|---|---|---|
| Granger | Granger (VAR) | Econometrica 1969 | Summary/lag | Không | Không | [Verified-CR] |
| | Neural Granger (Tank et al.) | TPAMI 2021 | Summary | Không | Không | [Verified-CR] |
| | CUTS, CUTS+, JRNGC | ICLR 2023, AAAI 2024, 2024 | Summary | Không | — | [Verified-search] |
| Constraint-based | **PCMCI** | Science Advances 2019 | Window DAG (lagged) | Không | Không | [Verified-CR] |
| | **PCMCI+** | UAI 2020 | Window CPDAG | Không | **Có** | [Verified-CR, arXiv 2003.03685] |
| | **LPCMCI** | NeurIPS 2020 | **Window PAG** | **Có** | Có | [Verified-search]; reviewer NeurIPS ghi nhận *không có dữ liệu thật* |
| | tsFCI (Entner & Hoyer 2010), SVAR-FCI (Malinsky & Spirtes 2018) | Workshop | PAG | Có | SVAR-FCI có | [Verified-search qua Butler] |
| | **TS-ICD** (Rohekar et al.) | ICML 2023 | PAG | **Có** | Có | [Verified-search]; nói có dữ liệu thật, có thể là thủy văn, **chưa kiểm** |
| | J-PCMCI+ (Günther et al.) | UAI 2023 | Window | Context ẩn qua biến giả | Có | [Verified-CR, arXiv 2306.12896] |
| | RPCMCI (Saggioro et al.) | Chaos 2020 | Một graph mỗi regime | Không | Không; phải biết trước số regime | [Verified-CR] |
| FCM / noise | VARLiNGAM | JMLR 2010 | Window DAG | Không | Có | [Verified-search] |
| | TiMINo | — | — | Không | — | [Verified-fetch, Butler Table I] |
| | RCD (biến ẩn, i.i.d.) | AISTATS | — | Có | — | Không dành cho dữ liệu thời gian (CausalDynamics dùng làm baseline) [Verified] |
| Score / continuous | DYNOTEARS | AISTATS 2020 | Window | Không | Có | [Verified-CR, arXiv 2002.00498] |
| | Rhino | ICLR 2023 (chưa xác nhận venue) | Window | Không | Có; nhiễu phụ thuộc lịch sử | [Verified-search] |
| Động lực học | CCM (Sugihara 2012), TSCI | — | Summary | "Relaxed" theo Butler Table I | — | [Verified-fetch] |
| Amortized / foundation | ACD (Löwe et al.) | CLeaR 2022 | Summary | Có bản mô hình hóa biến ẩn | — | [Verified-search] |
| | Causal Pretraining (Stein et al.) | AAAI workshop 2024 | Window | Không | — | [Verified-search]; fine-tune trên CausalRivers giúp ích [Verified] |
| Subsampling | Gong et al. | ICML 2015, UAI 2017 | VAR ở tần số gốc | Không | — | Cần nhiễu non-Gaussian [Verified-search] |
| | Hyttinen et al. (sRASL) | PGM 2016, IJAR 2017 | Graph ở tần số gốc | Không | — | [Verified-CR] |
| | Liu et al. (proxy) | NeurIPS 2023 | Định danh đầy đủ | Coi biến ẩn là proxy của chính nó | — | [Verified-CR, arXiv 2305.05276] |
| Không dừng | CD-NOD (Huang et al.) | JMLR 2020 | Summary | Dùng chỉ số thời gian làm surrogate | — | [Verified-CR, arXiv 1903.01672] |
| | SpaceTime (AAAI 2025), CASTOR (2023) | — | Theo regime | — | — | [Verified-search] |
| Lý thuyết summary graph | Assaad, Ferreira và cộng sự | AAAI 2025, arXiv 2508.21742 | Summary graph có confounding | Có | — | [Verified-search] |

**Nhận xét** [Inference]:
- Họ có biến ẩn (LPCMCI, SVAR-FCI, TS-ICD) có lý thuyết và có code (tigramite; causality-lab của Intel cho TS-ICD [chưa kiểm]).
- Nhưng họ này (i) chậm: Butler §III-D viết "markedly more computationally demanding" và AutoCause loại LPCMCI vì quá thời gian; và (ii) gần như **chưa được đánh giá trên dữ liệu thật có căn cứ**.

## 3. Benchmark

| Benchmark | Venue | Dữ liệu | Ground truth | Biến ẩn | Phát hiện | Nhãn |
|---|---|---|---|---|---|---|
| **CausalRivers** | ICLR 2025 | **Thật**: lưu lượng sông, 666 trạm (đông Đức) + 494 (Bavaria) + RiversElbeFlood; 2019–2023, mỗi 15 phút | Topology sông | Mưa (đo được qua DWD); tập "Confounder" (§3.1) | VAR ổn định nhất; baseline ngây thơ ngang phương pháp causal; CP và CDMI không hơn phương pháp tuyến tính | [Verified] |
| CausalTime | ICLR 2024 | Bán tổng hợp từ AQI, Traffic, MIMIC | Graph từ mô hình fit | Giả định sufficiency | — | [Verified-search] |
| **CausalDynamics** | NeurIPS 2025 D&B | ODE/SDE, khí hậu lý tưởng; 14 693 graph | Graph sinh | Có, nhưng chấm bằng adjacency | Tier đơn giản có AUROC khoảng .50; phương pháp không dùng DL tốt hơn; chuẩn hóa ít tác dụng; "autocorrelation is inferred where none exists" | [Verified] |
| TimeGraph | KDD 2025 D&B | Tổng hợp, có hoặc không có U | Graph sinh | Có; có chạy LPCMCI | LPCMCI chịu được ở trường hợp tuyến tính có confounder (A1C), kém khi phi tuyến mạnh | [Verified-CR cho venue; kết quả qua review thứ cấp] |
| CausalCompass | arXiv 2602.07915; poster NeurIPS 2026 | Tổng hợp (VAR, Lorenz-96), 8 kịch bản sai giả định, có confounder ẩn | Graph sinh | Có | Không phương pháp nào thắng mọi kịch bản; DL mạnh nhất trung bình | [Verified-search] |
| CauseMe | Runge et al., Nature Communications 2019 | Nền tảng thi đấu, phần lớn mô phỏng khí hậu | — | Một phần | — | [Verified-CR cho bài] |
| Sortability | Lohse & Wahl, TMLR 2025 | Mô phỏng cộng dữ liệu thật (CauseMe, sông, Causal Chamber) | — | — | **Dữ liệu chuỗi thời gian thật có var-sortability cao** | [Verified-search] |

### 3.1 Tập "Confounder" của CausalRivers không che confounder [Verified-code]

- **Bài báo** (§4.1): "we here selected sub-graphs with **four or six nodes** and where a single node has multiple children … We then **removed** the node that has multiple children from the sample to simulate permanent hidden confounding scenarios."
- **Code** `tools/graph_sampling_tools.py`, hàm `select_confounder_samples`:

  ```python
  candidates = [x for x in potential_list if con in x]
  for succ in list(G.successors(con)):
      candidates = [x for x in candidates if succ in x]
  # remove confounder from set
  samples.append([tuple([y for y in x]) for x in candidates])
  ```

  - Comment ghi "remove confounder" nhưng biểu thức `[y for y in x]` **giữ nguyên mọi nút, kể cả `con`**.
  - `0_generate_datasets.py` gọi hàm với `n_vars` bằng 3 hoặc 5, nên mỗi mẫu có 3 hoặc 5 nút **gồm cả nút confounder**, chứ không phải 4 hoặc 6 nút rồi bỏ đi 1.
  - Không có bước nào ở `benchmark.py`, `tools.py` hay `scoring_tools.py` loại nút này.
- **Lịch sử:** đoạn code này giống hệt từ commit đầu tiên `f377e45` (10/02/2025). Các commit ngày 21/02/2025 chỉ định dạng lại.
- **Cập nhật 09/11, đã giải quyết** [Verified bằng đếm lại, xem `P0_outputs.json`]: đếm bằng code công khai trên graph đã phát hành cho đúng **24 và 361 mẫu**, khớp Bảng 6 của bài. Đếm theo mô tả trong bài cho 106 và 1170. Vậy Bảng 3 đã dùng các mẫu **giữ** nút confounder. Đoạn dưới đây là trạng thái trước khi đếm lại.
- **Chưa biết** (trước khi đếm lại):
  - Bảng 3 của bài báo có được sinh bằng code này không, hay bằng một repo thí nghiệm riêng.
  - Các tập dữ liệu đã sinh sẵn (nếu có phát hành) chứa gì.
  - Muốn kết luận chắc thì phải tải graph pickle và đếm. Ví dụ: nếu số mẫu Confounder-3 trên đông Đức bằng 24 với code hiện tại thì code này đã được dùng cho bài.
- **Phát hiện này trùng với claim của một repo cá nhân** (Mathindata/causal-rivers-lab) mà tôi thấy qua tìm kiếm; giờ đã được kiểm độc lập trên code gốc.
- **Hệ quả** [Inference]: nếu code này được dùng, cột "Confounder" trong Bảng 3 đo **fork quan sát đầy đủ**, không đo confounding ẩn. Khi đó trên dữ liệu thật chưa có phép đo confounding ẩn nào.

## 4. Failure mode có bằng chứng

| # | Failure | Bằng chứng | Mức |
|---|---|---|---|
| F1 | **Confounding ẩn trên dữ liệu thật chưa được đo** | §3.1; Confounder-3 chỉ có n = 24 (Bảng 6); CausalDynamics không chạy LPCMCI; AutoCause loại LPCMCI; reviewer của LPCMCI ghi nhận không có dữ liệu thật; Butler §VI | Verified, Verified-code, Verified-search |
| F2 | **Giao thức đánh giá thổi phồng điểm** | Chọn siêu tham số theo nhãn ("best-performing Hyperparameter combination"; tác giả thừa nhận có thể "overestimates"); bỏ link tự hồi quy; AUROC "deceptively high" trên graph thưa (CausalDynamics §5) | Verified |
| F3 | **Metric chỉ dựa trên adjacency không ghi điểm được output PAG** | Cả CausalRivers lẫn CausalDynamics chấm bằng ma trận adjacency của summary graph. Dấu ↔ hay o→ của LPCMCI không được tính là đúng khi phát hiện confounding [Inference từ mô tả metric] | Inference |
| F4 | **Phương pháp đơn giản ngang hoặc thắng** | CausalRivers: VAR có AUROC .80–.82 trên tập Random; RP ngây thơ .75–.79. CausalDynamics: phương pháp không dùng DL tốt hơn | Verified |
| F5 | **Thang đo mang thông tin nhân quả** | Dữ liệu thật có var-sortability cao (Lohse & Wahl); chuẩn hóa ít tác dụng (CausalDynamics) | Verified-search, Verified |
| F6 | **Độ phân giải ảnh hưởng mạnh nhưng được chọn theo nhãn** | CausalRivers thử độ phân giải từ 15 phút đến 24 giờ như một siêu tham số. Lý thuyết nói dữ liệu bị underdetermined khi lấy mẫu thưa | Verified, Verified-fetch |
| F7 | **Trễ thay đổi và không dừng** | Trễ phụ thuộc lượng nước (CausalRivers §3.2). Preprint 2605.04081 về trễ thay đổi giả định sufficiency và để biến ẩn cho future work | Verified, Verified-search |
| F8 | **Chi phí tính toán của phương pháp có biến ẩn** | Butler §III-D; AutoCause | Verified-fetch, Verified-search |

## 5. Ứng viên gap (dữ liệu trước)

### TS-G1 (chính): confounding ẩn thật trên CausalRivers, che hoặc lộ mưa

- **Insight** [Hypothesis]: trong lưu vực sông, **mưa** là confounder có tự tương quan. Nó tác động lên nhiều trạm, kể cả các trạm **không nối nhau** theo topology. Mưa **đo được** qua DWD, và bộ công cụ CausalRivers đã có sẵn notebook `3_tutorial_subselect_weather_condition.ipynb` [Verified-code]. Vậy có thể chạy **cùng một đồ thị** ở hai chế độ: che mưa (latent) và lộ mưa (observed). Đây là một thí nghiệm "biến ẩn có kiểm soát" trên dữ liệu thật, điều mà các benchmark hiện có chưa làm được.
- **Cặp trạm đối chứng có sẵn:** các tập Random+1 và Disjoint của CausalRivers chứa nút hoặc nhóm nút **không có đường nhân quả** tới phần còn lại [Verified]. Link dự đoán giữa chúng là sai chắc chắn. Có thể phân tầng theo khoảng cách địa lý: gần nhau thì chung mưa, xa nhau thì không.
- **Câu hỏi đo đầu tiên** (luật đọc phải khai báo trước khi chạy):
  1. Tỉ lệ link giả giữa các cặp không nối nhau có **tăng theo mức chung mưa** (khoảng cách gần, cùng sự kiện mưa) không? Đo với VAR-Granger, PCMCI+ và VARLiNGAM.
  2. **Lộ mưa** (thêm chuỗi mưa từ trạm DWD gần nhất làm biến quan sát) có làm tỉ lệ link giả giảm không?
  3. Khi mưa bị che, LPCMCI, SVAR-FCI và TS-ICD có thay link giả bằng ↔ hoặc o-o (đúng ngữ nghĩa PAG), **trong khi vẫn giữ recall** ở các link thật không? Chi phí tính toán là bao nhiêu?
  4. Sửa sampler Confounder (bỏ thật nút cha chung, kích thước 4 hoặc 6) rồi đo lại cột Confounder.
- **Metric:**
  - Tách (i) recall của link thật theo topology; (ii) tỉ lệ claim *có hướng* sai giữa các cặp không nối nhau.
  - Với output PAG: tỉ lệ claim tổ tiên sai, so với tỉ lệ ↔, o-o hoặc không có cạnh.
  - Siêu tham số **không được chọn theo nhãn**: cố định trước, hoặc chọn bằng tiêu chí không dùng nhãn.
- **Baseline:** VAR-Granger; PCMCI+; VARLiNGAM; LPCMCI; SVAR-FCI hoặc TS-ICD; baseline ngây thơ RP và CC của CausalRivers.
- **Luật đọc đề xuất:**
  - **Có gap phương pháp** nếu (1) đúng, và (3) cho thấy phương pháp có biến ẩn hoặc mất nhiều recall, hoặc không chạy được ở cỡ thật.
  - **Chỉ là gap đánh giá** nếu LPCMCI đã sửa được (1) mà recall tương đương. Khi đó bài toán thu về một bài kiểm toán benchmark, rơi vào vùng X31 (DEPRIORITIZED).
- **Rủi ro:**
  - Mưa không phải confounder "sạch": nó vừa gây ra lưu lượng trực tiếp, vừa truyền theo dòng chảy.
  - Topology không cho biết **độ lớn** hiệu ứng.
  - Trạm DWD gần nhất chỉ là proxy của mưa trên cả lưu vực, nên lộ mưa chỉ là lộ một phần. Điều này cũng có thể biến thành một điểm thú vị: biến proxy cho confounder.
  - Cần tải dữ liệu CausalRivers và DWD. **Phải hỏi user trước.**

### TS-G2 (dự phòng): chọn độ phân giải thời gian mà không dùng nhãn

- **Insight** [Hypothesis]: dữ liệu 15 phút của CausalRivers cho phép **gộp có kiểm soát** trên dữ liệu thật (15 phút → 1 giờ → 6 giờ → 24 giờ) với topology cố định. Lý thuyết subsampling (Gong; Hyttinen; Liu) chủ yếu được kiểm trên dữ liệu tổng hợp. CausalRivers chỉ coi độ phân giải là siêu tham số chọn bằng nhãn.
- **Đo đầu tiên:** ở mỗi độ phân giải, link nào xuất hiện hoặc biến mất; link tức thời tăng ra sao. Sự **nhất quán giữa các độ phân giải** có dự đoán được độ phân giải tốt nhất mà không cần nhãn không?
- **Prior art cần audit:** rate-agnostic learning (Plis, Danks, Hyttinen); multi-scale Granger.

### Các hướng khác, xếp sau

- **Trễ thay đổi theo trạng thái** (lưu lượng quyết định trễ): prior art đang xuất hiện (arXiv 2605.04081, 2026).
- **Causal pretraining hoặc foundation model:** dựa nhiều vào dữ liệu và hạ tầng, ít insight nhân quả, rủi ro bị trùng cao.

## 6. Đối chiếu với do-not-redo

- **X12–X22 (A′, R1/R2, "certified ancestral assertions", η-profile) đều đã đóng.** Bất kỳ cơ chế nào ở TS-G1 kiểu "chứng nhận claim tổ tiên cho link trễ" sẽ **rơi lại vào A′/R1** nếu chỉ đổi sang dữ liệu thời gian. Muốn đi theo hướng đó phải có lý do khoa học mới.
- **X31** (kiểm toán benchmark như một đề tài độc lập): §3.1 là một **phát hiện**, không phải đề tài. Chỉ dùng nó làm động cơ cho TS-G1.
- **X5** (LLM cộng discovery có biến ẩn): không liên quan.

## 7. Giới hạn

- Venue và nội dung của TS-ICD, Rhino, J-PCMCI+, tsFCI và SVAR-FCI chỉ qua tìm kiếm.
- Chưa đọc PDF của LPCMCI, TimeGraph, CausalCompass.
- §3.1 đã kiểm trên code nhưng chưa chạy được để so số lượng mẫu với bài báo.
- "Chưa thấy ai đánh giá LPCMCI trên CausalRivers" dựa trên 3 lượt tìm kiếm cộng AutoCause. **Chưa audit kỹ.**
