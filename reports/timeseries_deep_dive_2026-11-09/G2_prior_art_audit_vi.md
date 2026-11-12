# Audit prior art: khoảng trống (2), confounding ẩn có cấu trúc trong chuỗi thời gian (11/11/2026)

> **Mức xác minh:** lượt audit qua tìm kiếm cộng một bài đọc toàn văn (Supple et al., qua HTML arXiv). Chưa đọc PDF của các bài khác.
> **Nhãn:**
> - [Verified-fetch]: đọc toàn văn HTML.
> - [Verified-search]: chỉ qua abstract hoặc kết quả tìm kiếm.
> - [Verified-CR]: DOI hoặc venue đối chiếu qua Crossref hoặc arXiv API.
> - [Inference], [Hypothesis].
>
> **Câu hỏi:** đã có phương pháp nào học cấu trúc nhân quả trên chuỗi thời gian khi confounder ẩn là một **quá trình thay đổi theo thời gian, có tự tương quan, tác động lên nhiều biến và giảm dần theo khoảng cách** (như mưa đối với các trạm sông), với output có ngữ nghĩa nhân quả (PAG hoặc claim tổ tiên), và được kiểm trên dữ liệu thật hay chưa?

## 1. Bản đồ prior art

| Công trình | Loại confounder ẩn | Chuỗi thời gian | Output | Kiểm trên dữ liệu thật có căn cứ | Nhãn |
|---|---|---|---|---|---|
| LPCMCI (NeurIPS 2020), SVAR-FCI, TS-ICD (ICML 2023) | Tổng quát, xử lý **từng cặp**; không khai thác cấu trúc | Có | PAG | Không | Verified-search |
| **FNETS**, Barigozzi, Cho, Owens (JBES 2023/2024) | **Nhân tố động lan tỏa (pervasive)** qua dynamic PCA; cho phép nhân tố yếu | Có | Mạng Granger, mạng đồng thời, mạng tổng hợp; **không có ngữ nghĩa PAG** | Dự báo; không có ground truth nhân quả | Verified-CR, Verified-search |
| Zorzi & Sepulchre, *AR Identification of Latent-variable Graphical Models* (IEEE TAC 2016) | Một số ít biến ẩn, dạng sparse cộng low-rank trên phổ | Có (AR) | Graph vô hướng | Ảnh thần kinh | Verified-search |
| Frot, Nandy, Maathuis (JRSS-B 2019) | Lan tỏa, low-rank | **Không** (i.i.d.) | CPDAG trên dữ liệu đã khử nhiễu | — | Verified-CR |
| DeCAMFounder, Agrawal et al. (JRSS-B 2023) | Lan tỏa, khử bằng phân rã phổ; phi tuyến | **Không** | DAG | — | Verified-CR |
| DCL-DECOR (arXiv 2512.24696, 2025) | Lan tỏa cộng cục bộ; phân rã precision matrix | **Không** | DAG với nhiễu tương quan | — | Verified-search |
| **Supple, Worthington, Swallow** (arXiv 2510.26485 v4, 10/2026) | U = h(S): **hàm cố định theo vị trí, không có động học theo thời gian**; là cha của mọi biến | Có (sửa PCMCI+) | Như PC; **không có PAG** | **Không có thí nghiệm nào** ("We are currently working to implement this framework", §5.3) | **Verified-fetch** |
| Rabel & Runge (arXiv 2511.21537, 2025) | **Ngữ cảnh rời rạc ẩn** (regime, vùng không gian); quan tâm cơ chế đổi theo ngữ cảnh | Có (PCMCI, PCMCI+, LPCMCI) | Graph theo ngữ cảnh | Ví dụ lưới không gian | Verified-search |
| SPACY, Wang et al. (arXiv 2411.05331) | Học biến ẩn **là** các mode không gian; dữ liệu dạng lưới | Có | DAG giữa các mode ẩn | Khí hậu, không có ground truth | Verified-search |
| Christiansen et al., LSCM (JASA 2022) | Confounder không gian ẩn, dừng | Có | **Ước lượng hiệu ứng**, không học cấu trúc | Colombia | Verified-CR |
| Liu et al. (ICML 2024) | Có proxy của confounder | Không | Kiểm định CI | Có | Verified-search |
| J-PCMCI+ (UAI 2023) | Ngữ cảnh ẩn hằng theo thời gian | Có | Window graph | — | Verified-search |

## 2. Kết luận audit

**Phần đã có người làm:**
- (a) Confounding ẩn **tổng quát** trong chuỗi thời gian (LPCMCI và các phương pháp cùng họ).
- (b) Confounding **lan tỏa toàn cục** trong chuỗi thời gian, nhưng chỉ cho ra mạng Granger (FNETS, Zorzi & Sepulchre).
- (c) Confounding lan tỏa trong dữ liệu i.i.d. cho DAG (Frot, DeCAMFounder, DCL-DECOR).
- (d) Confounder **không gian tĩnh** (Supple et al., chỉ là khung lý thuyết).
- (e) Ngữ cảnh ẩn **rời rạc** (Rabel & Runge; J-PCMCI+).

**Phần còn trống** [Hypothesis; dựa trên khoảng 10 lượt tìm kiếm, cần đọc PDF để chắc]:
- Confounder ẩn là một **quá trình liên tục, thay đổi theo thời gian, có tự tương quan, và ảnh hưởng *cục bộ*** (giảm theo khoảng cách). Nó nằm **giữa** hai thái cực đã có: (i) từng cặp, tức LPCMCI; và (ii) toàn cục, tức FNETS.
- Thêm ba yêu cầu: trạm đo đặt **không đều** (không phải dạng lưới), output có **ngữ nghĩa nhân quả** (PAG hoặc claim tổ tiên), và **kiểm trên dữ liệu thật có căn cứ**.
- Không bài nào trong bảng thỏa đồng thời các điều kiện này.
- Supple et al. tự nêu "extensions to insufficient settings" và "relationships … do not change over time" là việc của tương lai (§4.2.3, §5.3) [Verified-fetch]. Nhưng nên nhớ: nhóm này **đang làm tiếp**, nên cửa sổ có thể đóng nhanh.

**Rủi ro lớn nhất cho novelty** [Inference]:
- Có thể đã có công trình trong **kinh tế lượng không gian** (spatial VAR, nhân tố cục bộ, "local factors") hoặc **địa thống kê** mà lượt tìm kiếm chưa chạm tới.
- Cách "khử nhân tố rồi chạy PCMCI" có thể đã được dùng *ad hoc* trong khí hậu (ví dụ bỏ tín hiệu ENSO trước khi chạy). Khi đó đóng góp phải nằm ở **lý thuyết**: khử nhân tố cục bộ mà vẫn giữ đúng quan hệ độc lập có điều kiện cho phần còn lại.

## 3. Pilot P1 trả lời được gì cho khoảng trống này

- **Q1 (tầng gần so với tầng xa):** link giả có **giảm theo khoảng cách** không? Nếu có, đó là chữ ký của confounding **cục bộ**. Đây là tiền đề của khoảng trống.
- **Q3 (LPCMCI):** phương pháp cho confounding tổng quát có đủ dùng không, hay mất recall hoặc chạy quá chậm (GAP-A hoặc GAP-B)?
- **Chưa trả lời:** FNETS (nhân tố toàn cục) có giải được bài toán không. FNETS **không có** trong luật đọc đã khóa. Nếu P1 cho GAP-A hoặc GAP-B, bước tiếp theo phải là một **pilot riêng có FNETS làm baseline**, với luật đọc mới. FNETS có gói R `fnets` trên CRAN; máy cần cài R, việc này sẽ hỏi bạn trước.

## 4. Bài cần tải

| # | Bài | Venue | DOI | Kiểm |
|---|---|---|---|---|
| 1 | Barigozzi, Cho, Owens, *FNETS: Factor-Adjusted Network Estimation and Forecasting for High-Dimensional Time Series* | JBES 42(3), 2024 | `10.1080/07350015.2023.2257270` | ✓CR |
| 2 | Supple, Worthington, Swallow, *Discovering causal relationships between time series with spatial structure* | arXiv 2025, v4 2026 | `10.48550/arXiv.2510.26485` | đã đọc HTML |
| 3 | Rabel & Runge, *Context-Specific Causal Graph Discovery with Unobserved Contexts: Non-Stationarity, Regimes and Spatio-Temporal Patterns* | arXiv 2025 | `10.48550/arXiv.2511.21537` | s |
| 4 | Frot, Nandy, Maathuis, *Robust Causal Structure Learning with Some Hidden Variables* | JRSS-B 81(3), 2019 | `10.1111/rssb.12315` | ✓CR |
| 5 | Agrawal, Squires, Prasad, Uhler, *The DeCAMFounder* | JRSS-B 2023 | `10.1093/jrsssb/qkad071` | ✓CR |
| 6 | *Causal Discovery with Mixed Latent Confounding via Precision Decomposition* (DCL-DECOR) | arXiv 2025 | `10.48550/arXiv.2512.24696` | ✓arX |
| 7 | Liu, Sun, Qiao, Wang, *Causal Discovery via Conditional Independence Testing with Proxy Variables* | ICML 2024 | `10.48550/arXiv.2305.05281` | s |
| 8 | Zorzi & Sepulchre, *AR Identification of Latent-variable Graphical Models* | IEEE TAC 2016 | `10.48550/arXiv.1405.0027` | ✓arX |
| 9 | Wang et al., *Discovering Latent Structural Causal Models from Spatio-Temporal Data* (SPACY) | arXiv 2024 | `10.48550/arXiv.2411.05331` | s |
| 10 | Christiansen et al., *Towards Causal Inference for Spatio-Temporal Data: Conflict and Forest Loss in Colombia* | JASA 117, 2022 | `10.48550/arXiv.2005.08639` | ✓arX (journal_ref) |
| 11 | Ćevid, Bühlmann, Meinshausen, *Spectral Deconfounding via Perturbed Sparse Linear Models* | JMLR 2020 | `10.48550/arXiv.1811.05352` | ? chưa xác minh |
