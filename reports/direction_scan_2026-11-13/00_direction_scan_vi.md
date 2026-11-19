# Quét hướng mới sau khi đóng P17 (13/11/2026)

> **Bộ lọc dùng để quét** (thống nhất 12/11): một hướng chỉ được giữ nếu (1) là **phép giao của hai kết quả đã biết chưa ai đo cùng lúc** hoặc một **câu "vì sao" đã được nêu nhưng chưa trả lời**; (2) có **đòn bẩy sạch**, tức can thiệp do mình kiểm soát hoàn toàn; (3) **mọi nhánh kết quả đều báo cáo được**; (4) không trùng X1–X33 trong [`RESEARCH_HISTORY_vi.md`](../../RESEARCH_HISTORY_vi.md) §3.
>
> **Mức xác minh:** [Verified-fetch] đã đọc đoạn văn gốc (qua agent fetch, có trích dẫn nguyên văn); [Verified-search] chỉ qua abstract hoặc kết quả tìm kiếm; [Own-data] từ pilot của chính repo; [Inference]; [Hypothesis].
>
> **Phạm vi quét:** năm vùng có sẵn dữ liệu hoặc phát hiện từ ba tuần qua, cộng vùng "đo lường và đánh giá", nơi gap thường nằm. Khoảng 12 lượt tìm kiếm và 8 bài đọc có mục tiêu. Đây không phải systematic review.

## 0. Kết luận trước

| Hạng | Ứng viên | Loại đóng góp | Phán quyết sơ bộ |
|---|---|---|---|
| **1 (chính)** | **C1. Khoảng cách dựa trên hiệu chỉnh (adjustment-based distance) cho PAG, và câu hỏi: các thuật toán có biến ẩn có bị xếp hạng sai khi đo bằng metric cấu trúc không?** | Phép đo + cơ chế + công cụ | Gap được **hai nhóm tác giả tự xác nhận bằng chữ** (Henckel et al. 2024; Wahl & Runge 2025); nguyên liệu lý thuyết đã có (Perković et al. 2018). Pilot rẻ, mọi nhánh có giá trị |
| **2 (dự phòng)** | **C2. Tri thức nền sai loại nào "im lặng" trong FCI, và vì sao** | Phép đo + cơ chế (+ lý thuyết nhỏ) | Có dữ liệu oracle từ P-B; prior art gần nhất (LGES, NeurIPS 2025) chỉ cho DAG/MEC; hẹp hơn C1 |
| 3 | C3. Tách lỗi của họ FCI thành "do biến ẩn" và "do sai số CI" (thiết kế 2×2 oracle × mẫu hữu hạn, có × không biến ẩn) | Phép đo | Có thể là nghiên cứu thứ hai bên trong C1; đứng riêng thì dễ bị xem là folklore |
| 4 | C4. Lộ proxy của confounder làm LPCMCI tệ hơn (từ TS-G1 P1) | Phép đo + cơ chế | Hiện tượng thật [Own-data] nhưng miền chuỗi thời gian đã bị user hạ ưu tiên (X32) |
| — | C5. Đánh giá LLM làm causal discovery gộp "nhớ" với "suy luận" | — | **Bỏ**: đã có position paper và audit (xem §6) |

## 1. C1 — Khoảng cách hiệu chỉnh cho PAG và xếp hạng thuật toán có biến ẩn

### 1.1 Hai kết quả đã biết được giao nhau

**(a) Adjustment Identification Distance (AID), Henckel, Würtzen, Weichwald, UAI 2024.** Thay vì đếm cạnh sai (SHD), AID đếm số cặp (T, Y) mà chiến lược hiệu chỉnh đọc từ đồ thị *đoán* cho ra một tập hiệu chỉnh **không hợp lệ** trong đồ thị *thật*, hoặc tuyên bố sai về tính định danh. Chỉ định nghĩa cho **DAG và CPDAG**. Phần Discussion của họ nói thẳng [Verified-fetch, trích nguyên văn]: các chiến lược hiệu chỉnh "are not sound and complete for settings with hidden variables"; "sound and complete alternatives exist. Yet, there are no verifiers for these alternatives"; và họ muốn công cụ này "aid the development of causal discovery under latent confounding".

**(b) Tiêu chí hiệu chỉnh tổng quát cho PAG, Perković, Textor, Kalisch, Maathuis, JMLR 2018.** Tiêu chí hiệu chỉnh **sound và complete** cho DAG, CPDAG, MAG và PAG, kèm tập hiệu chỉnh hiển (Adjust(T, Y, G)) khi tồn tại, và thuật toán liệt kê, đã cài trong dagitty [Verified-search, abstract và bảng tóm tắt].

Phép giao: **AID với đầu vào là PAG**, dùng (b) làm chiến lược hiệu chỉnh của đồ thị đoán và tiêu chí DAG thông thường để kiểm trong đồ thị thật (DAG đầy đủ gồm cả biến ẩn). Vì (b) là complete *cho hiệu chỉnh*, khoảng cách này đo đúng câu hỏi "nếu tôi dùng PAG này để hiệu chỉnh thì có sai không", là câu hỏi mà người dùng FCI thực sự hỏi. Phần Henckel gọi là thiếu ("no verifiers") chỉ cản trở khoảng cách dựa trên **định danh tổng quát** (front-door, ID-algorithm); nó không cản trở phiên bản hiệu chỉnh.

### 1.2 Ai đã đến gần

| Công trình | Làm gì | Vì sao chưa lấp gap | Nhãn |
|---|---|---|---|
| Wahl & Runge, *Separation-based distance measures*, AISTATS 2025 (PMLR 258) | Khoảng cách theo quan hệ tách (separation) cho DAG, CPDAG, MAG, PAG | Tự ghi: "For mixed graphs/MAGs the only available distances are the SHD and the ZL-SD"; xếp AID là "DAGs, CPDAGs, further extensions possible"; khuyên dùng AID cho ước lượng hiệu ứng, SD cho MEC. **Không** đánh giá thuật toán discovery nào; future work là "re-evaluation of popular causal discovery methods" | Verified-fetch |
| Li & Kilbertus, *Fixing Identification Distance* (FID), arXiv 2510.25037 (10/2025) | Khoảng cách theo estimand cho **ADMG** (một đồ thị có cạnh hai chiều), dùng fixing và bộ kiểm ký hiệu | Đầu vào là một ADMG cụ thể, không phải lớp tương đương; chính họ viết "unlike SID and AID, FID operates on ADMGs, we can only meaningfully compare to a separation-based distance computed on MAGs". Đây là nhóm có khả năng mở rộng sang PAG nhất; **rủi ro bị đi trước** | Verified-fetch |
| Ramsey et al., FCIT, arXiv 2510.04263 (2025) | Benchmark mới nhất cho họ FCI: FCI, GFCI, BOSS-FCI, GRaSP-FCI, LV-Lite, FCIT; 20/100/200 nút, 0–20 biến ẩn, N = 200–5000 | Mọi metric đều cấu trúc (AP, AR, AHP, AHR, *->-Prec, -->-Prec, <->-Lat-Prec, tỉ lệ PAG hợp lệ); **không có** metric nào về tính hợp lệ của claim hiệu ứng. FCI "lowest precision throughout" | Verified-fetch |
| NLPSCM (2506.16234) và một bài TMLR 04/2026 | "Mod. SHD" cho PAG: lỗi định hướng chắc chắn tính 1, lỗi không chắc tính 0.5; SID cho PAG qua ánh xạ sang CPDAG | Vẫn là metric cấu trúc với trọng số ad hoc; ánh xạ PAG→CPDAG bỏ ngữ nghĩa biến ẩn | Verified-search |
| Wang, Qin, Zhou, *Estimating possible causal effects with latent variables via adjustment*, ICML 2023 | Liệt kê các hiệu ứng khả dĩ từ PAG qua hiệu chỉnh | Là công cụ ước lượng, không phải khoảng cách; nhưng là nguồn cho cách xử lý "nhiều giá trị khả dĩ" | Verified-search |
| *Causal discovery needs explicit epistemic standards* (2611.03166) | Position paper, dùng ancestor-AID làm ví dụ metric đúng việc | Không có PAG | Verified-search |
| Tài liệu tham khảo nội bộ (không công khai) | Tiền lệ phương pháp luận: thang "k cạnh sai" trộn liều với thành phần | Khác miền | Không công khai |

### 1.3 Câu hỏi khoa học và vì sao mọi nhánh đều có giá trị

**Q:** Khi đo bằng tính hợp lệ của claim hiệu chỉnh thay vì bằng cạnh, thứ hạng của các thuật toán có biến ẩn có đổi không, và **loại lỗi cấu trúc nào** biến thành claim hiệu chỉnh sai?

- **Nhánh "đổi thứ hạng":** FCI, vốn "lowest precision" theo metric cấu trúc vì để lại nhiều dấu tròn, có thể lại **tốt nhất** theo AID vì dấu tròn không sinh claim sai, còn các phương pháp lai định hướng mạnh (BOSS-FCI, GRaSP-FCI) phải trả giá bằng tập hiệu chỉnh sai. Đây là bản PAG của một hiện tượng đã thấy ở LLM: một claim được tính là "sai" theo cấu trúc có thể vô hại, một claim "gần đúng" theo cấu trúc có thể cắt đứt định danh [Hypothesis, có cơ sở từ P-B: FA/FNA thô của repo đã cho thấy dấu sai chủ yếu là mũi tên/đuôi, chính là thứ quyết định hiệu chỉnh].
- **Nhánh "không đổi thứ hạng":** vẫn là kết quả có giá trị: metric cấu trúc là proxy đủ tốt cho họ FCI, và cộng đồng có thể yên tâm dùng; kèm công cụ và định nghĩa mới. Nhỏ hơn, nhưng báo cáo được.
- **Câu "vì sao" đi kèm:** phân loại lỗi cấu trúc theo hậu quả hiệu chỉnh: (i) dấu tròn thay vì đuôi trên cạnh visible (mất định danh, không sai); (ii) đuôi sai, tức claim tổ tiên sai (tập hiệu chỉnh mở đường backdoor); (iii) cạnh hai chiều giả (báo không định danh dù định danh được); (iv) thiếu cạnh. Mỗi loại đo được riêng bằng cách **chèn một lỗi vào PAG thật** (đòn bẩy sạch, cùng kỹ thuật với P-B) rồi xem AID thay đổi bao nhiêu. Đây là phần cơ chế.

### 1.4 Cơ chế và lý thuyết tỉ lệ với claim

- **Định nghĩa PAG-AID**: với mỗi cặp có thứ tự (T, Y) của biến quan sát, đồ thị đoán G′ (PAG) cho ra một trong ba kết luận: tập Adjust(T, Y, G′) theo Perković 2018; "không định danh được bằng hiệu chỉnh"; hoặc "T không phải tổ tiên khả dĩ của Y" (hiệu ứng bằng 0). Đồ thị thật G (DAG có biến ẩn) phân xử: tập đề xuất có thỏa tiêu chí hiệu chỉnh trong G không; tuyên bố không định danh có đúng không (trong G có tập hiệu chỉnh quan sát được không); tuyên bố hiệu ứng 0 có đúng không. Mỗi sai lệch tính 1. Ba biến thể như AID gốc (parent, ancestor, optimal) cần kiểm xem biến thể nào có nghĩa trong PAG; ít nhất "Adjust-set" theo Perković là xác định.
- **Mệnh đề cần có** (nhỏ): PAG-AID bằng 0 khi G′ là PAG thật của G; PAG-AID là tiền-metric; chi phí tính đa thức qua các thuật toán reachability (Henckel 2024 đã có cho DAG/CPDAG; cần kiểm lại với possibly-directed path và visible edge trong PAG). Không hứa định lý lớn.
- **Vì sao không "chỉ là ghép hai bài"**: giá trị nằm ở câu trả lời thực nghiệm (thứ hạng có đổi không, lỗi nào gây hại) và ở phân loại cơ chế, không nằm ở định nghĩa.

### 1.5 Pilot bác bỏ (viết luật đọc trước, khóa, rồi chạy)

- **P-C1a, oracle, không cần thuật toán discovery:** lấy DAG thật có biến ẩn (lưới của Ramsey 2025: 20 nút, bậc 2/4/6, 0/4/8 biến ẩn; cộng bnlearn đã ẩn biến sẵn trong repo), PAG thật từ `fci()` oracle (đã có trong `pb_fci_typed.py`). Chèn **một** lỗi có kiểu (i)–(iv) rồi đo ΔSHD, ΔMod-SHD, ΔSD (Wahl–Runge), ΔPAG-AID. Câu hỏi: các metric có **đồng ý về thứ tự độ nghiêm trọng** của bốn loại lỗi không. Nếu đồng ý hoàn toàn, câu chuyện yếu đi nhiều. Chi phí: vài giờ máy.
- **P-C1b, thuật toán thật:** chạy FCI, GFCI, BOSS-FCI, GRaSP-FCI, FCIT (Tetrad qua py-tetrad, cần Java) trên lưới Ramsey với N ∈ {500, 1000, 5000}, 20 lần lặp; tính cả bộ metric. Luật đọc: "đổi thứ hạng" = tương quan Spearman giữa thứ hạng theo PAG-AID và theo AHP/AP dưới 0.5 ở ít nhất 2/3 mức N, hoặc thuật toán đứng cuối theo cấu trúc lên top-2 theo PAG-AID với CI bootstrap theo đồ thị không chứa 0.
- **Kiểm chéo bắt buộc:** cài đặt Perković cho PAG đối chiếu với `dagitty::adjustmentSets` trên ≥ 500 bộ (PAG, T, Y) ngẫu nhiên, phải khớp 100%. Cần **R** (dagitty); phải hỏi user trước khi cài.

### 1.6 Baseline (≥ 3, cùng dữ liệu, cùng output)
SHD trên PAG; Mod-SHD (NLPSCM); AP/AR/AHP/AHR của Tetrad; separation distance ZL-SD (Wahl–Runge, có mã); FID của Li–Kilbertus trên MAG được chọn từ PAG (nếu mã công khai), để chỉ ra khác biệt giữa "một ADMG" và "lớp tương đương".

### 1.7 Rủi ro

| Rủi ro | Mức | Cách giảm |
|---|---|---|
| Nhóm Li–Kilbertus hoặc Henckel–Weichwald đang mở rộng sang PAG | Cao | Pilot P-C1a trong 1–2 tuần; nếu đi tiếp, đăng preprint sớm phần đo lường |
| Metric mới không đổi thứ hạng (kịch bản X31 lặp lại) | Trung bình | Vẫn là kết quả; nhưng khi đó chỉ đủ bài ngắn hoặc workshop |
| Cài đặt tiêu chí PAG sai | Trung bình | Kiểm chéo dagitty 100%; test trên đồ thị nhỏ vét cạn |
| Phụ thuộc Tetrad/Java cho các thuật toán lai | Thấp | py-tetrad ổn định; hoặc chỉ FCI + GFCI nếu không cài được |
| Reviewer: "chỉ là AID + Perković" | Trung bình | Trụ của bài phải là phát hiện thực nghiệm và phân loại cơ chế, không phải định nghĩa |

## 2. C2 — Tri thức nền sai loại nào im lặng trong FCI (dự phòng)

- **Hai kết quả giao nhau:** (a) completeness của FCI với tri thức nền **đúng** (Andrews–Spirtes–Cooper 2020 tiered; Wang–Qin–Zhou 2022 local) [Verified, đọc toàn văn trong Phase 0 của P17]; (b) lan truyền lỗi cục bộ trong PC ("How PC-based methods err", UAI 2026) và tính đúng tiệm cận dưới tri thức **sai** cho GES (LGES, Ejaz & Bareinboim, NeurIPS 2025, arXiv 2506.22331) [Verified-search]. Chưa thấy bài nào về tri thức sai **trong FCI/MAG**; LGES tự ghi tiered-FCI "assume that the background knowledge is correct".
- **Phát hiện đã có [Own-data, P-B]:** lỗi "→ đoán thành ↔" lan 0.61 dấu/lần chèn và **60% không để lại mâu thuẫn nào** với sepset; lỗi "↔ đoán thành →" gần như luôn bị bắt (99%). Đảo chiều lan nhiều nhất (1.06) nhưng 84% phát hiện được.
- **Câu hỏi:** vì sao mũi tên sai im lặng còn đuôi sai thì không, và điều này có còn ở mẫu hữu hạn không. Mệnh đề mục tiêu: điều kiện đồ thị để một dấu chèn sai nằm ngoài lớp tương đương mà không tạo xung đột sepset nào.
- **Pilot:** P-B ở mẫu hữu hạn (đã nằm trong plan P17 §2.1) cộng cài đặt bộ kiểm nhất quán (CICheck hoặc tự viết) làm baseline "có phát hiện được không".
- **Vì sao chỉ là dự phòng:** hẹp; đóng góp lý thuyết có thể chỉ là một bổ đề; dễ bị xem là phần phụ của một bài khác. Nhưng có thể ghép vào C1 như phần "lỗi cấu trúc nào gây hại".

## 3. C3 — Tách lỗi "do biến ẩn" và "do sai số CI" trong họ FCI

- **Thiết kế 2×2 trong cùng đồ thị:** CI oracle so với Fisher-z; có biến ẩn so với không (cùng DAG, ẩn hoặc không ẩn cùng tập nút). Mỗi ô cho một PAG; hiệu giữa các ô tách phần lỗi do Possible-D-SEP và định hướng dưới biến ẩn khỏi phần do kiểm định sai. Cùng khuôn "đo trong cùng một đơn vị".
- **Bài học đã có [Own-data, X28]:** ở T4-L, lỗi nền ở dữ liệu đầy đủ (8–13 claim sai mỗi đồ thị) lớn hơn nhiều phần do missing data (2–8). Khả năng cao điều tương tự đúng cho biến ẩn.
- **Rủi ro:** reviewer nói "ai cũng biết". Chỉ nên làm như nghiên cứu phụ của C1, dùng PAG-AID làm thước.

## 4. C4 — Lộ proxy của confounder làm LPCMCI tệ hơn

- [Own-data, TS-G1 P1]: khi thêm chuỗi mưa và khai báo ngoại sinh, LPCMCI đưa ra claim tổ tiên sai giữa các sông không nối nhau nhiều hơn (0.67 → 0.88 ở tầng gần, 0.27 → 0.55 ở tầng xa) và gần như mất hết `<->`.
- **Giao nhau:** (a) proxy variable cho kiểm định CI dưới confounding (Liu et al. ICML 2024, arXiv 2305.05281; Wu et al. 2510.17167) và (b) tri thức nền "ngoại sinh" trong discovery chuỗi thời gian có biến ẩn (LPCMCI, link assumptions). Chưa thấy bài nào đo "proxy không hoàn hảo cộng khai báo ngoại sinh" lên tính đúng của PAG chuỗi thời gian [Verified-search, một lượt].
- **Đòn bẩy sạch có:** mô phỏng với proxy có chất lượng điều khiển được (tương quan với confounder thật từ 1.0 xuống 0.3), có hoặc không khai báo ngoại sinh.
- **Vì sao xếp sau:** user đã hạ ưu tiên miền chuỗi thời gian (X32); hiện tượng chưa được tách khỏi bốn giải thích thay thế A1–A4. Nếu C1 thất bại ở pilot, C4 là ứng viên có dữ liệu thật sẵn nhất.

## 5. Vì sao hướng nào không xuất hiện

- **LLM prior cho FCI:** X33.
- **Audit benchmark đơn lẻ:** X31 đã nới, nhưng C1 không phải audit; nó là metric cộng phép đo cộng cơ chế.
- **Chứng nhận thống kê cho claim tổ tiên (A′/R1):** X12–X22.
- **Scheduler/đổi thứ tự CI:** X1.

## 6. C5 bị bỏ vì đã có người làm
- *Realizing LLMs' causal potential requires science-grounded, novel benchmarks* (arXiv 2510.16530): kiểm tra tái tạo cho thấy các mạng bnlearn bị LLM nhớ.
- *Benchmarking and enhancing agentic causal discovery* (2610.22846): đánh giá chỉ bằng tên biến.
- Audit obfuscation trong *LLM-augmented causal discovery: probabilistic fusion* (2608.27472).
- P-A của repo cũng cho cùng kết quả (TP_D sụp khi đổi tên). Không còn gì để thêm ngoài một data point.

## 7. Đề xuất quyết định

1. **Chọn C1 làm hướng chính**, C2 làm dự phòng (và là ứng viên ghép vào C1).
2. Bước kế: viết **luật đọc cho P-C1a** (oracle, không cần Java) và chạy trong tuần này; song song đọc toàn văn bốn bài: Henckel 2024, Perković 2018, Wahl–Runge 2025, Li–Kilbertus 2025.
3. Cần user cho phép: cài **R + dagitty** để kiểm chéo tiêu chí PAG; cài **Java + py-tetrad** cho P-C1b.
4. Trao đổi với nhóm: hỏi xem có ai làm metric cho PAG không.

## 8. Bài cần tải

| # | Bài | Venue | DOI hoặc arXiv | Vai trò |
|---|---|---|---|---|
| 1 | Henckel, Würtzen, Weichwald, *Adjustment identification distance: a gadjid for causal structure learning* | UAI 2024, PMLR 244 | arXiv `2402.08616` | Nền của C1; đọc §3, §5, §8, App. A |
| 2 | Perković, Textor, Kalisch, Maathuis, *Complete graphical characterization and construction of adjustment sets in Markov equivalence classes of ancestral graphs* | JMLR 18(220), 2018 | arXiv `1606.06903`; JMLR v18/16-319 | Tiêu chí hiệu chỉnh cho PAG |
| 3 | Wahl, Runge, *Separation-based distance measures for causal graphs* | AISTATS 2025, PMLR 258:3412–3420 | arXiv `2402.04952` | Baseline SD; bảng so sánh metric |
| 4 | Li, Kilbertus, *Graph distance based on cause-effect estimands with latents* (FID) | arXiv 10/2025 | arXiv `2510.25037` | Đối thủ gần nhất; nguy cơ bị đi trước |
| 5 | Ramsey et al., *Efficient latent variable causal discovery: combining score search and targeted testing* (FCIT) | arXiv 2025 | arXiv `2510.04263` | Thiết kế benchmark và các thuật toán cho P-C1b |
| 6 | Peters, Bühlmann, *Structural intervention distance for evaluating causal graphs* | Neural Computation 27(3), 2015 | `10.1162/NECO_a_00708`; arXiv `1306.1043` | Gốc của họ metric |
| 7 | Wang, Qin, Zhou, *Estimating possible causal effects with latent variables via adjustment* | ICML 2023 | PMLR 202 (kiểm) | Xử lý "nhiều hiệu ứng khả dĩ" từ PAG |
| 8 | Henckel, Perković, Maathuis, *Graphical criteria for efficient total effect estimation via adjustment in causal linear models* | JRSS-B 84(2), 2022 | `10.1111/rssb.12451` | Biến thể optimal adjustment |
| 9 | Ejaz, Bareinboim, *Less greedy equivalence search* | NeurIPS 2025 | arXiv `2506.22331` | Prior art cho C2 |
| 10 | Zhang, *Causal reasoning with ancestral graphs* | JMLR 9, 2008 | JMLR v9/zhang08a | Visible edge, possibly directed path |
| 11 | *Causal discovery needs explicit epistemic standards* | arXiv 11/2026 | arXiv `2611.03166` | Bối cảnh, dùng ancestor-AID |
| 12 | Liu, Sun, Qiao, Wang, *Causal discovery via CI testing with proxy variables* | ICML 2024 | arXiv `2305.05281` | Chỉ cho C4 |

Các DOI không ghi là tôi chưa đối chiếu Crossref trong lượt này; arXiv ID đều lấy từ kết quả tìm kiếm trực tiếp.
