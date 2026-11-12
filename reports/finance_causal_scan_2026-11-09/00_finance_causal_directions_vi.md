# Rà soát dữ liệu và hướng nghiên cứu: causal ML trong tín dụng và tài chính (09/11/2026)

> **ĐÃ BỎ cùng ngày.** User quyết định quay lại hướng causal discovery. File giữ lại để truy vết; không làm tiếp.

> **Bối cảnh:** user đổi phạm vi sang sáu bài toán tài chính, nhắm Q1/A*. Quy trình vẫn là "dữ liệu trước": chỉ coi là gap khi đo được trên dữ liệu uy tín.
> **Mức xác minh:** đây là **lượt quét đầu**. Chưa đọc PDF gốc của bài tài chính nào. Mọi nội dung về các bài đó là [Verified-search], tức chỉ qua abstract, trang proceedings hoặc kết quả tìm kiếm. DOI ngoài arXiv đã đối chiếu metadata Crossref [Verified-Crossref].
> **Nhãn:** [Verified] đọc nguồn gốc trong phiên; [Verified-search]; [Verified-Crossref]; [Inference]; [Hypothesis].
> **Chưa tải dữ liệu, chưa chạy gì.**

## 0. Tóm tắt

1. **Đổi phạm vi** [Inference]. Năm trong sáu bài toán là causal *inference* và ra quyết định (ước lượng hiệu ứng, uplift, off-policy, fairness), không phải causal *discovery*. Mission trong `AGENTS.md` hiện ghi "causal discovery". Nếu user chốt hướng mới thì cần sửa `AGENTS.md` và `RESEARCH_HISTORY_vi.md`. Tôi chưa sửa hai file này.
2. **Điểm chung lớn nhất** [Inference]: năm trong sáu bài toán (1, 2, 3, 5, 6) có cùng một cấu trúc nhân quả. Đó là **nhãn bị che bởi chính chính sách** (*policy-induced selective labels*, MNAR):
   - Tín dụng chỉ thấy vỡ nợ ở người được duyệt.
   - Gian lận và rửa tiền chỉ có nhãn ở giao dịch đã bị cảnh báo và điều tra.
   - Định giá chỉ thấy phản ứng ở mức lãi đã chào.
   - Thu hồi nợ chỉ thấy kết quả của hành động đã thực sự làm.

   Bài toán 4 (systemic risk) khác hẳn: đó là causal discovery trên chuỗi thời gian có biến ẩn (nhân tố chung của thị trường).
3. **Căn cứ đánh giá nhân quả là điểm nghẽn.** Dữ liệu tài chính công khai gần như chỉ là dữ liệu quan sát. Có ba loại căn cứ:
   - Thí nghiệm ngẫu nhiên thật: Karlan & Zinman, AER 2008 (lãi suất ngẫu nhiên), nhưng **chưa thấy dữ liệu công khai**.
   - Mô phỏng có nhãn đầy đủ: AMLworld, NeurIPS 2023 D&B.
   - Bán tổng hợp: áp một chính sách duyệt giả lên dữ liệu đã có nhãn (Home Credit, BAF). Cách này cho phép giữ lại nhãn thật để chấm điểm.
4. **Xếp hạng tạm** (§3):
   - **Ứng viên chính để audit:** selective labels, đánh giá và học dưới MNAR, kiểm trên AML/fraud và tín dụng.
   - **Dự phòng:** systemic risk bằng causal discovery chuỗi thời gian có biến ẩn.
   - **Có điều kiện:** causal pricing, nếu lấy được dữ liệu RCT.
   - **Không khuyến nghị làm trục chính:** thu hồi nợ (không có dữ liệu ngẫu nhiên công khai) và counterfactual fairness (đại lượng không định danh được từ dữ liệu, tranh cãi nhiều).
5. **Cảnh báo novelty:** vùng selective labels **đã dày** (§2.0). Muốn đạt Q1/A* phải có cơ chế mới cụ thể; chỉ "áp dụng vào tài chính" là không đủ. Do-not-redo X31 cũng nhắc rằng một bài thuần kiểm toán benchmark đã bị deprioritize trước đây.

## 1. Tiêu chí

Dùng lại bộ tiêu chí của review benchmark 09/11, điều chỉnh cho tài chính:

| # | Tiêu chí |
|---|---|
| C1 | Dữ liệu **uy tín**: từ dataset paper ở venue mạnh, hoặc dữ liệu hành chính hay cơ quan quản lý được dùng ở journal top |
| C2 | Có **căn cứ đánh giá nhân quả**: RCT, natural experiment, hoặc mô phỏng/bán tổng hợp giữ được nhãn đối chứng |
| C3 | **Failure đo được** trên dữ liệu đó trước khi đề xuất phương pháp |
| C4 | Còn chỗ cho **cơ chế mới**, sau khi đối chiếu prior art |
| C5 | Khả thi trên máy 7.8 GB RAM, truy cập được mà không cần đối tác |

## 2. Từng bài toán

### 2.0 Vấn đề xuyên suốt: selective labels (áp dụng cho 1, 2, 3, 5, 6)

Prior art đã thấy [Verified-search trừ khi ghi khác]:

| Công trình | Venue | Nội dung chính | Giả định hoặc giới hạn |
|---|---|---|---|
| Lakkaraju et al., *The Selective Labels Problem* | KDD 2017 [Verified-Crossref] | Đặt tên bài toán; đánh giá bằng "contraction" | Dựa vào sự khác nhau giữa người quyết định |
| Coston, Rambachan, Chouldechova | ICML 2021 (PMLR 139) | Khoảng disparity trên tập "good models" dưới selective labels | **Giả định không có confounder ẩn** |
| Rambachan, Coston, Kennedy, *Robust Design and Evaluation of Predictive Algorithms under Unobserved Confounding* | REStat 2026 [Verified-Crossref] | Bỏ giả định không có confounder ẩn; dùng mô hình độ nhạy (mean outcome sensitivity) để có cận | Cận có thể rộng |
| Kozodoi et al., *Fighting sampling bias* | EJOR 2025 [Verified-Crossref] | Reject inference khi học; khung Bayes khi đánh giá. Kết luận: xử lý bias **khi đánh giá** hứa hẹn hơn khi học | — |
| Scarone & Baeza-Yates, *The Illusion of Improvement* | ECML PKDD 2026 (arXiv 2606.18479) | Khi retrain, accuracy tăng trong khi recall với người vỡ nợ giảm. Khám phá 2–5% là đủ để chẩn đoán | Ba bộ dữ liệu thật |
| *Performative Prediction with Selective Labels* | NeurIPS 2026 (poster) | Objective worst-case dựa trên khoảng tin cậy; thí nghiệm cho vay có fairness | Có giả định độ nhạy |
| Narayan, *Reject Inference as a MNAR Problem* | SSRN 2026 | Bán tổng hợp trên Home Credit: áp chính sách duyệt giả, giữ nhãn bị từ chối làm ground truth | Preprint |
| Dal Pozzolo et al., *Credit Card Fraud Detection: A Realistic Modeling…* | IEEE TNNLS 2018 [Verified-Crossref] | Alert-feedback gây sample selection bias; phải tách feedback của điều tra viên và delayed labels | — |
| *PolicyShift-AML* | Research Square 2026 (preprint) | Trên 3 029 170 giao dịch TransXion: latent Recall@500 chênh 26.1–29.3% giữa các chính sách điều tra; recall thấy được cao hơn recall thật 0.1085 | Chưa bình duyệt |
| *Causal Label Recovery in Payment Networks* | arXiv 2605.29272 (2026) | Ba cổng chọn mẫu (authorization, reporting, delay) cộng với nhãn nhiễu; ước lượng triply robust | Preprint |

**Nhận định** [Inference]:
- Failure "đánh giá sai dưới selective labels" **đã được chứng minh** ở cả tín dụng lẫn AML. Đo lại failure này thì không còn là đóng góp.
- Chỗ trống có thể còn [Hypothesis, **chưa audit**]:
  - (a) **Kết hợp dữ liệu khám phá nhỏ** (2–5% khoản vay được duyệt ngẫu nhiên, như Scarone đề xuất) với dữ liệu lớn bị chọn mẫu, để thu hẹp cận của Rambachan et al. Câu hỏi then chốt: cần bao nhiêu khám phá để cận đủ hẹp mà vẫn xếp hạng đúng các mô hình.
  - (b) **Selective labels nhiều tầng có confounder ẩn**: cảnh báo, rồi điều tra, rồi báo cáo SAR, rồi xác nhận. Kiểm trên AMLworld, nơi biết nhãn thật của mọi giao dịch.
- Phải đọc kỹ Rambachan et al. và *Causal Label Recovery* trước, vì hai bài này có thể đã phủ cả (a) lẫn (b).

### 2.1 Robust Credit Scoring

| Dữ liệu | Nguồn | Thật hay sinh | Điểm đáng chú ý | Truy cập |
|---|---|---|---|---|
| **Home Credit, Credit Risk Model Stability** | Kaggle 2024 | Thật | Có `WEEK_NUM`. Metric chấm cả Gini trung bình theo tuần, độ dốc Gini và độ dao động quanh xu hướng. Người chơi đã khai thác được kẽ hở của metric [Verified-search, nguồn thứ cấp] | Kaggle |
| Home Credit Default Risk | Kaggle 2018 | Thật | Chỉ có khoản vay đã duyệt; được dùng làm nền bán tổng hợp cho reject inference (Narayan 2026) | Kaggle |
| **Lending Club** (đã duyệt và bị từ chối) | Dữ liệu công bố của LC 2007–2018 | Thật | Khoảng 2.26 triệu hồ sơ được duyệt và khoảng 27.6 triệu bị từ chối, nhưng hồ sơ bị từ chối **chỉ có 9 biến** [Verified-search] | Bản sao trên Kaggle; trang gốc của LC chưa xác minh |
| FICO HELOC, qua **TableShift** | NeurIPS 2023 D&B | Thật | Một trong 15 task có shift định nghĩa sẵn. Phát hiện: accuracy ID và OOD có quan hệ tuyến tính; các phương pháp robust thu hẹp khoảng cách shift nhưng làm giảm accuracy ID [Verified-search] | Cần đăng ký |
| BAF (xem 2.6) | NeurIPS 2022 D&B | Sinh từ dữ liệu thật | Có biến thể bias và shift theo thời gian | Kaggle |

- **Góc nhân quả:** invariance hoặc anticausal features; strategic manipulation (Hardt et al. ITCS 2016; performative prediction, Perdomo et al. ICML 2020).
- **Rủi ro bị bác bỏ** [Verified-search]: TableShift cho thấy các phương pháp robustness trên dữ liệu bảng hiếm khi thắng ERM về OOD mà không mất ID. Mọi claim kiểu "causal thì robust hơn" phải vượt được baseline ERM cộng GBDT.
- **Gap tiềm năng** [Hypothesis]: một phần "shift theo thời gian" trong tín dụng có thể đến từ **việc đổi chính sách duyệt** (selection shift), chứ không phải hành vi người vay thay đổi. Nếu tách được hai nguồn này thì gắn được Robust Scoring với 2.0.
- **C2:** chấm OOD theo thời gian là đo thật, nhưng không có ground truth nhân quả.

### 2.2 Counterfactual Fairness

| Dữ liệu | Nguồn | Điểm đáng chú ý |
|---|---|---|
| **HMDA** (dữ liệu vay thế chấp Mỹ) | CFPB/FFIEC, công khai | Thật, rất lớn, có chủng tộc và giới tính, có quyết định duyệt và giá. **Không có biến vỡ nợ.** Fuster et al., *Predictably Unequal?*, J. Finance 2022 [Verified-Crossref] dùng gần 10 triệu khoản vay; snippet chưa xác nhận nguồn là HMDA |
| BAF | NeurIPS 2022 D&B | Có thuộc tính nhạy cảm; mỗi biến thể có một loại bias được cấy vào có kiểm soát |
| Folktables | NeurIPS 2021 | Thay cho Adult; không phải tín dụng |

- **Vấn đề nền tảng** [Verified-search]:
  - Counterfactual fairness (Kusner et al., NeurIPS 2017) **không định danh được** từ dữ liệu quan sát cộng với causal diagram, kể cả khi giả định Markov. Hai SCM cùng phân phối và cùng diagram có thể cho kết luận fairness khác nhau (Plecko & Bareinboim, FnT ML 2024 [Verified-Crossref]).
  - Rosenblatt & Witter (AAAI 2023 [Verified-Crossref]) cho rằng counterfactual fairness "basically" tương đương demographic parity.
  - Hướng đi hiện có: cận (Wu et al., IJCAI 2019) và graph biết một phần (Zuo et al., NeurIPS 2022).
- **C2 thất bại trên dữ liệu thật:** không có ground truth phản thực. Muốn chứng minh failure phải dùng bán tổng hợp, và reviewer sẽ hỏi SCM lấy từ đâu.
- **Kết luận:** không làm trục chính. Có thể làm **nhánh** của 2.0: fairness đánh giá trên dữ liệu đã duyệt bị lệch, như Coston et al. đã chỉ ra.

### 2.3 Causal Collections (thu hồi nợ)

- **Không tìm thấy bộ dữ liệu thu hồi nợ có ngẫu nhiên hóa nào công khai** [Verified-search, hai lượt tìm].
- Gần nhất là preprint SSRN của Aguilera Gonzalez về hiệu ứng tái cơ cấu nợ. Bài này kiểm trên credit bán tổng hợp và trên RCT churn của Orange Belgium, và thấy **thứ hạng các CATE estimator gần như đảo ngược khi chuyển sang dữ liệu ngẫu nhiên thật**. Đây là tín hiệu đáng chú ý nhưng chưa bình duyệt.
- Benchmark uplift ngẫu nhiên công khai: Criteo (Diemert et al., khoảng 13.9 triệu dòng). Đây là quảng cáo, không phải tài chính.
- **C1 và C2 thất bại** nếu không có đối tác ngân hàng. Không khuyến nghị, **trừ khi user có dữ liệu nội bộ**.

### 2.4 Systemic Risk Contagion

| Dữ liệu | Nguồn | Điểm đáng chú ý |
|---|---|---|
| Lợi suất cổ phiếu ngân hàng, bảo hiểm, broker | CRSP (cần license) hoặc nguồn công khai | Nền của Billio et al. (JFE 2012) và Diebold & Yilmaz (J. Econometrics 2014) [Verified-Crossref] |
| Mạng phơi nhiễm thật | Bảo mật, chỉ ngân hàng trung ương có | Anand et al. (JFS 2018 [Verified-Crossref]) so các phương pháp tái dựng mạng trên **25 thị trường ở 13 khu vực pháp lý** có mạng thật. Kết luận: phương pháp thắng phụ thuộc vào đặc trưng mạng cần giữ |
| Thống kê ngân hàng BIS; EBA transparency exercise | Công khai | Phơi nhiễm ở mức tổng hợp (quốc gia, hoặc ngân hàng với chủ quyền) [Inference, chưa kiểm tra] |

- **Failure đã biết** [Verified-search]:
  - Mạng Granger cặp đôi (pairwise) của Billio et al. "highly dense due to spurious causalities". Billio tự xử lý bằng cách hồi quy lên S&P 500 rồi kiểm định Granger trên phần dư, và gọi kết quả là "conservative upper bound".
  - Các phê bình: Basu et al. 2017, Etesami et al. 2017, bài leave-one-out (J. Econ. Dynamics & Control).
  - Đây chính là **latent confounding** (nhân tố chung) và **conditioning không đủ**, đúng bài toán mà LPCMCI giải quyết (§Phụ lục A).
- **Gap tiềm năng** [Hypothesis, chưa audit]: dùng causal discovery chuỗi thời gian có biến ẩn (LPCMCI, PAG) để đưa ra **claim tổ tiên có chứng nhận** về lan truyền rủi ro. Kiểm chứng bằng phơi nhiễm công khai (BIS/EBA) hoặc bằng sự kiện (2008, SVB 2023). Chưa biết đã có ai chạy LPCMCI hoặc PAG trên mạng tài chính hay chưa.
- **C2 yếu:** không có ground truth ở cấp ngân hàng nếu không có dữ liệu ngân hàng trung ương.
- **Venue:** Q1 tài chính và kinh tế lượng (J. Financial Stability, J. Financial Econometrics) khả thi hơn A* ML.
- **Ưu điểm:** khớp mission causal discovery và kinh nghiệm FCI/PAG của repo.

### 2.5 Causal Pricing (lãi suất)

| Dữ liệu | Nguồn | Căn cứ nhân quả | Truy cập |
|---|---|---|---|
| **Karlan & Zinman**, lãi suất ngẫu nhiên tại Nam Phi | AER 2008 [Verified-Crossref] | **RCT thật**: 58 168 khách cũ nhận thư chào lãi suất ngẫu nhiên. Đăng ký AEARCTR-0001354 | **Chưa thấy gói replication công khai** [Verified-search]; phải kiểm tra openICPSR/J-PAL hoặc hỏi tác giả |
| **Columbia CPRM-12-001**, auto loan online | Phillips, Simsek, van Ryzin, Management Science 2015 [Verified-Crossref] | Quan sát; giá có biến thiên. Dùng trong Ban & Keskin (MS 2021) và nhiều bài OPE pricing | Theo yêu cầu qua CPRM (chưa xác minh) |
| Lending Club | — | Quan sát; lãi suất gắn với hạng tín dụng | Kaggle |

- **Prior art** [Verified-search]: *A Causal Perspective on Loan Pricing* (arXiv 2309.03730) về selection bias khi ước lượng bid-response; *Balanced Off-Policy Evaluation for Personalized Pricing* (arXiv 2302.12736); và các bài offline RL pricing tín dụng.
- **Gap tiềm năng** [Hypothesis]: **within-study comparison** kiểu LaLonde. Dùng RCT Karlan–Zinman làm chuẩn, rồi đo xem các estimator quan sát (DML, OPE, IV) tái tạo được độ co giãn theo lãi suất đến đâu. Chưa biết đã có ai làm.
- **Điều kiện:** chỉ khả thi nếu lấy được dữ liệu RCT.

### 2.6 Causal AML/Fraud

| Dữ liệu | Venue | Thật hay sinh | Điểm đáng chú ý |
|---|---|---|---|
| **AMLworld** (Altman et al.) | NeurIPS 2023 D&B [Verified-search] | Mô phỏng đa tác tử, hiệu chỉnh theo giao dịch thật | **Nhãn thật đầy đủ cho mọi giao dịch**; mô phỏng cả placement, layering và integration. Là testbed lý tưởng để áp chính sách điều tra giả rồi chấm bằng nhãn thật |
| **BAF** (Jesus et al., Feedzai) | NeurIPS 2022 D&B [Verified-search] | Sinh từ dữ liệu mở tài khoản ngân hàng thật | 6 biến thể, mỗi biến thể có một loại bias; có động học theo thời gian và mất cân bằng lớp; có thuộc tính nhạy cảm |
| Elliptic (2019) và **Elliptic2** (Bellei et al. 2024) | Workshop KDD 2019; arXiv 2024 | Thật (Bitcoin) | Elliptic2 có 122 nghìn subgraph có nhãn trong nền khoảng 49 triệu cluster. Nhãn đến từ góc nhìn AML của một công ty tình báo, tức bản thân nhãn cũng bị chọn |
| IEEE-CIS Fraud, ULB credit card | Kaggle | Thật | Không có thông tin về chính sách cảnh báo |

- **Góc nhân quả:** selective labels do năng lực điều tra hữu hạn; nhãn đến muộn (chargeback); đối thủ thích nghi (performative).
- **Prior art đang tăng nhanh năm 2026** (§2.0): PolicyShift-AML, Causal Label Recovery, *The Fundamental Limits of Fraud Detection in Card Payment Networks* (arXiv 2605.27557). Cửa sổ novelty đang hẹp lại.

## 3. Xếp hạng tạm

| Hạng | Bài toán | C1 dữ liệu | C2 căn cứ nhân quả | C4 chỗ cho cơ chế mới | Khớp năng lực repo | Ghi chú |
|---|---|---|---|---|---|---|
| **1 (chính, cần audit)** | 2.0 selective labels, kiểm trên **AML/fraud (AMLworld, BAF) và tín dụng (Home Credit, Lending Club)** | Mạnh | **Mạnh** nhờ mô phỏng hoặc bán tổng hợp có nhãn thật | **Trung bình đến thấp**: prior art dày, phải nhắm (a) hoặc (b) ở §2.0 | Trung bình (partial identification, cận, gần mảng confidence của A′) | Phủ được 1, 2, 5, 6 |
| **2 (dự phòng)** | 2.4 systemic risk bằng causal discovery chuỗi thời gian có biến ẩn | Trung bình | **Yếu** | Có thể cao, chưa audit | **Cao** (FCI/PAG, LPCMCI) | Q1 tài chính khả thi hơn A* |
| 3 (có điều kiện) | 2.5 pricing, within-study comparison với RCT | Tùy dữ liệu | Mạnh nếu có RCT | Chưa rõ | Thấp–trung bình | Phụ thuộc truy cập dữ liệu Karlan–Zinman |
| 4 | 2.1 robust scoring | Mạnh | Trung bình (chỉ OOD theo thời gian) | Thấp (TableShift cho kết quả âm) | Thấp | Nên gộp vào hạng 1 qua "selection shift" |
| 5 | 2.2 counterfactual fairness | Trung bình | **Thất bại** (không định danh được) | Thấp, tranh cãi | Thấp | Làm nhánh của hạng 1 |
| 6 | 2.3 collections | **Thất bại** | — | — | — | Chỉ làm nếu user có dữ liệu nội bộ |

**Tiêu chí go/no-go cho hạng 1** (đề xuất, chờ user duyệt):
- **NO-GO** nếu audit thấy Rambachan et al. (REStat 2026) cộng *Causal Label Recovery* đã phủ cả (a) kết hợp khám phá với cận, lẫn (b) selective labels nhiều tầng có confounder ẩn.
- **GO sang pilot** nếu còn ít nhất một chỗ trống. Pilot đầu tiên:
  - Trên AMLworld, áp hai chính sách điều tra giả có năng lực giới hạn.
  - Đo mức sai lệch xếp hạng mô hình giữa đánh giá trên nhãn quan sát được và trên nhãn thật.
  - Đo xem (a) hoặc (b) thu hẹp sai lệch đó được bao nhiêu so với baseline IPW/DR và cận Rambachan.
  - Luật đọc phải khai báo trước khi chạy.

## 4. Điều chưa làm, cần nói rõ

- Chưa đọc PDF gốc của bất kỳ bài tài chính nào. Mọi con số về các bài đó (58 168, 27.6 triệu, 26.1–29.3%…) lấy từ abstract hoặc snippet.
- Chưa audit prior art cho từng gap (a), (b), 2.4 hay 2.5. "Chưa thấy" không có nghĩa là chưa có.
- Chưa kiểm tra điều khoản truy cập: HMDA, CPRM, FICO HELOC, dữ liệu Karlan–Zinman, CRSP.
- Ba bài 2026 (PolicyShift-AML, Causal Label Recovery, Fundamental Limits) là preprint, chưa bình duyệt.

## Phụ lục A. Deep dive chuỗi thời gian bị dừng giữa chừng (09/11)

User chuyển hướng giữa chừng. Ghi lại các phát hiện vì liên quan trực tiếp đến 2.4:

- **CausalRivers, ICLR 2025** [Verified, đọc PDF trong `docs/papers/`]:
  - Bảng 3: mọi phương pháp tụt điểm trên tập Confounder, ví dụ VAR có AUROC .82 trên Random-3 nhưng .71 trên Confounder-3.
  - Tập Confounder-3 **chỉ có 24 đồ thị**, Confounder-5 có 361 (Bảng 6).
  - Siêu tham số được chọn theo nhãn ("best-performing Hyperparameter combination"); tác giả thừa nhận cách này có thể đánh giá quá cao.
  - Không chạy LPCMCI.
- **Chưa xác minh:** một repo GitHub cá nhân (Mathindata/causal-rivers-lab) cho rằng **code phát hành vẫn giữ nút cha chung trong tập Confounder**, trái với mô tả trong bài. Nếu đúng, tập này không hề kiểm confounder ẩn. Việc kiểm tra code gốc bị dừng giữa chừng.
- **CausalDynamics, NeurIPS 2025 D&B** [Verified]:
  - Tier đơn giản: hầu hết phương pháp có AUROC khoảng .50.
  - Phương pháp duy nhất có tính biến ẩn là RCD, vốn không thiết kế cho dữ liệu thời gian. Không có LPCMCI.
- **Survey của Butler et al., IEEE Signal Processing Magazine 2026** (arXiv 2610.13430) [Verified-fetch]: nêu unobserved confounding là vấn đề mở (§VI); không nêu trường hợp nào phương pháp có biến ẩn được đánh giá trên dữ liệu thật.
- **AutoCause** (arXiv 2608.00198) [Verified-search]: loại LPCMCI khỏi thí nghiệm trên CausalRivers vì vượt giới hạn thời gian chạy.
- **Lohse & Wahl**, TMLR 2025 [Verified-search]: dữ liệu chuỗi thời gian thật có var-sortability cao.
