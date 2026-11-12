# Kế hoạch tiếp tục hướng "LLM prior cho causal discovery có biến ẩn" với framing mới (12/11/2026)

> **Một câu:** tiếp tục hướng 18/09–21/10 (prior từ LLM cho FCI dưới biến ẩn), nhưng đổi câu hỏi từ *"LLM giúp FCI nhanh hơn hoặc đúng hơn bao nhiêu"* sang *"FCI lấy gì từ một guess của LLM dưới biến ẩn, và guess đó gây hại theo cách nào mà nó không thể gây dưới causal sufficiency"*. Phương pháp, nếu có, là **hệ quả** của câu trả lời, không phải điểm xuất phát.
>
> **Trạng thái:** kế hoạch chờ user duyệt. Hai pilot đầu có luật đọc riêng ở [`PA_PB_reading_rules_vi.md`](PA_PB_reading_rules_vi.md).
> **Nhãn:** [Verified] đã kiểm bằng nguồn hoặc mã; [Inference]; [Hypothesis]; [Memory] nhớ từ trước, chưa kiểm lại trong lượt này.

## 1. Bối cảnh và điều gì đã đóng

### 1.1 Những gì hướng cũ đã làm (18/09–21/10/2026)

- Luận điểm cũ: tách *evidence plane* (chỉ dữ liệu và luật hợp lệ đổi graph) khỏi *control plane* (prior chỉ lập lịch CI query). Nguồn: [`archive/2026-09_safe_imperfect_priors/handoff/01_executive_summary.md`](../../archive/2026-09_safe_imperfect_priors/handoff/01_executive_summary.md).
- K0 PASS (tương đương cơ học, 220/220). K1 PASS theo quyết định dự án: **oracle** scheduler tiết kiệm trung vị 23% số CI test, chỉ trong pha FAS-stable, chưa chạm Possible-D-SEP. K2–K4 chưa chạy.
- Bị dừng vì: Guess2Graph (AISTATS 2026) chiếm claim "expert chỉ đổi thứ tự kiểm định, giữ consistency" cho PC; review 30/10 cho thấy "LLM + discovery có biến ẩn", "học khi nào tin LLM" đều có prior art. Sổ do-not-redo: **X1** (đổi thứ tự CI query làm đóng góp chính) và **X5** (LLM + latent discovery làm gap) là SUBSUMED. Hai mục này **vẫn đóng** trong kế hoạch này.
- Tài sản còn dùng: `src/safety_prior/` có `OracleCI`, `GaussianCI`, `generate_dag(observed, latent_ratio, mean_degree, seed)`, metric skeleton và endpoint cho PAG, bootstrap [Verified: chữ ký hàm trong mã]. causal-learn 0.1.4.8 có FCI với CI oracle d-separation, `dag2pag`, và các hàm luật R0–R10 ở mức module [Verified: kiểm trong mã trên máy].

### 1.2 Câu hỏi của mentor và câu trả lời của kế hoạch này

Mentor hỏi: chèn LLM vào FCI có "tự nhiên" quá không, vì đó là điều ai cũng nghĩ khi tối ưu một thuật toán vét cạn. Phân tích đầy đủ nằm trong trao đổi ngày 12/11; tóm tắt:

- **Tự nhiên ở tầng một:** năm chỗ cắm LLM vào thuật toán ràng buộc đều đã có chủ (đổi thứ tự: Guess2Graph; ràng buộc cứng hoặc mềm: RoaDs, tFCI, Cluster-FCI; định hướng dấu tròn: NLPSCM; học khi nào tin: L2D-CD, CauTion; LLM đề xuất và dữ liệu kiểm: CauScientist, CausalFusion, AGFN).
- **Tự nhiên ở tầng hai, đây mới là vấn đề:** coi FCI là thuật toán vét cạn cần tối ưu tức là coi LLM là một CI test rẻ. Khi đó trần là một bài tối ưu, và trần đó đã đo: 23% với oracle. FCI chậm vì dưới biến ẩn vị trí tập tách không cục bộ, không phải vì nó thiếu gợi ý.
- **Điều khiến biến ẩn khác:** (a) lệch loại giữa thứ LLM biết (DAG đầy đủ của thế giới, kể cả biến không đo) và thứ PAG mã hóa (MAG trên biến quan sát, có ↔, visible và invisible edge, inducing path); (b) một tài liệu tham khảo nội bộ (không công khai) gợi ý rằng tên biến có thể đẩy LLM khẳng định hiệu ứng ở cặp không có đường nhân quả, và dưới biến ẩn cặp đó chính là cặp ↔; (c) luật định hướng của FCI (R4 discriminating path, R8–R10) lan lỗi theo cách khác PC.

Từ đó, câu hỏi nghiên cứu được đặt lại như ở đầu file. Nó có giá trị ở mọi nhánh trả lời, và nếu nhánh âm thì câu hỏi của mentor đúng toàn phần và hướng đóng vĩnh viễn.

## 2. Câu hỏi nghiên cứu và giả thuyết

**Q:** Khi một guess của LLM được đưa vào FCI dưới biến ẩn, (i) lỗi của guess tập trung ở đâu, (ii) FCI khuếch đại nó tới đâu và qua luật nào, (iii) lỗi đó có phát hiện được từ dữ liệu không, và (iv) có cách đưa guess vào mà vẫn giữ output nằm trong lớp tương đương do dữ liệu xác định hay không.

| Giả thuyết | Phát biểu | Kiểm bằng | Nhãn |
|---|---|---|---|
| **H-type** | Lỗi của LLM khi đoán cấu trúc tập trung ở cặp ↔ (nguyên nhân chung bị ẩn): LLM nói → ở đó nhiều hơn hẳn ở cặp không liên quan | P-A, RA1 | Hypothesis, có cơ sở từ một tài liệu tham khảo nội bộ |
| **H-prop** | Kiểu guess sai chỉ tồn tại dưới biến ẩn (↔ đoán thành →, → đoán thành ↔) lan xa hơn trong FCI so với kiểu đảo chiều | P-B, RB2 | Hypothesis, chưa có cơ sở định lượng; chiều có thể ngược |
| **H-silent** | Phần lớn lan truyền từ hai kiểu trên không tạo xung đột nào với sepset, nên không kiểm tra nhất quán CI nào phát hiện được | P-B, RB3 | Hypothesis |
| **H-fix** | Hỏi LLM bằng câu hỏi tương thích MAG (cho phép trả lời "confounded") giảm FP ở cặp ↔ | P-A, RA3 | Hypothesis; nếu đúng, cơ chế nằm ở bước hỏi; nếu sai, nằm ở thuật toán |

Điều **không** là giả thuyết của kế hoạch: "LLM làm FCI nhanh hơn", "prior an toàn hữu hạn mẫu", "LLM không thể làm causal discovery".

## 3. Prior art phải đối chiếu và ranh giới novelty

### 3.1 Bảng đối chiếu

| Công trình | Đã làm | Ranh giới với kế hoạch này | Nhãn |
|---|---|---|---|
| Guess2Graph, Hiremath et al., AISTATS 2026, arXiv 2510.14488 | Expert đổi thứ tự cạnh và tập điều kiện trong PC; Thm 5.1 nhất quán bất kể expert, Thm 5.2–5.3 đơn điệu theo độ đúng cạnh p_ψ; mô hình lỗi là độ đúng cạnh đồng nhất | Chỉ PC, causal sufficiency; không FCI, không PAG. Mô hình lỗi không có loại cặp. Dưới oracle, đổi thứ tự không đổi output, nên không đo được bằng P-B | Verified, đọc toàn văn bản arXiv |
| **Cluster-FCI**, Ruiz de Vargas, Padh, Kilbertus, arXiv 2512.10032 v3 (08/2026) | Cluster-DAG làm tri thức nền cho PC và FCI; ghi nhận tri thức nền có thể vi phạm ancestrality | Tri thức nền được coi là đúng. Nhận xét về ancestrality là triệu chứng của lệch loại mà H-type nhắm tới | Verified, abstract |
| Andrews, Spirtes, Cooper, AISTATS 2020 | Completeness của FCI với tiered background knowledge **đúng** | Không có tri thức sai; không có loại lỗi | Memory, **phải kiểm** |
| Wang, Qin, Zhou, NeurIPS 2022 | Sound và complete với local background knowledge **đúng** trên MAG | Như trên | Memory, **phải kiểm** |
| Faltenbacher et al., "How PC-based methods err", UAI 2026 | Lỗi cục bộ gây orientation sai ở xa; coherency scores | Chỉ PC; không có ↔; không có nguồn lỗi là LLM | Verified-search (review 30/10) |
| NLPSCM, arXiv 2506.16234 v2 | FCI và LLM cập nhật tuần tự, prior nhiễu thành background knowledge | Có FCI và LLM. Không phân loại lỗi theo loại cặp, không đo lan truyền hay tính phát hiện được. Là **baseline bắt buộc** ở Phase 2 | Verified-search (review 30/10, mức M) |
| AGFN, arXiv 2309.12032 v4 | GFlowNet trên ancestral graph với expert nhiễu, active query | Có biến ẩn và expert. Bảo đảm phụ thuộc mô hình expert; không đo lệch loại | Verified-search (review 30/10) |
| COAT, arXiv 2402.03941 | LLM đề xuất nhân tố từ dữ liệu phi cấu trúc, rồi FCI | Gần nhất với ý "LLM gọi tên biến ẩn". Không đo lỗi theo loại cặp | Verified-search |
| CauScientist, arXiv 2601.13614 | LLM đề xuất, thống kê kiểm; FCI hoặc AVICI làm bộ kiểm | DAG; không có loại cặp ↔ | Verified, abstract |
| LLM Cannot Discover Causality, arXiv 2506.00844 | Lập luận hạn chế LLM ở vai trò non-decisional; thí nghiệm với heuristic search | Trực giác của mentor thành bài; không FCI, không biến ẩn | Verified, abstract |
| From Causal Plausibility to Causal Reliability, arXiv 2608.23660 | LLM nhầm gián tiếp thành trực tiếp, đảo chiều, overconfident | Lỗi loại I (gián tiếp) đã có; lỗi loại B (confound ẩn) chưa thấy được tách riêng | Verified-search (review 30/10) |
| Long, Schuster, Piché, arXiv 2307.02390 | Thu hẹp MEC bằng expert sai | DAG; không có ↔ | Verified-search |
| Tài liệu tham khảo nội bộ (không công khai) | Gợi ý LLM dựa vào tên biến khi khẳng định quan hệ nhân quả | Khác task. **Phải phối hợp** trong nhóm để không trùng kế hoạch | Không công khai |
| CICheck 2309.05264; Optimal Correction Sets 2610.33138 | Kiểm tra nhất quán CI, sửa tập ràng buộc tối thiểu | Baseline cho câu hỏi "lỗi có phát hiện được không" (H-silent) | Verified-search (review 30/10) |

### 3.2 Ranh giới claim

- **Có thể claim nếu pilot ủng hộ:** (1) một phép đo lỗi LLM **theo loại cặp của MAG**, có đối chứng tên biến, trên nhiều mạng; (2) một mô tả cơ chế lan truyền lỗi trong FCI theo kiểu guess sai, kèm tính phát hiện được; (3) nếu Phase 2 đi tiếp, một lớp dịch có kiểu từ phát biểu LLM sang ràng buộc tương thích MAG, với mệnh đề về việc output ở lại trong lớp tương đương do dữ liệu xác định; (4) nếu phát hiện, các lỗi trong cách đánh giá hiện hành (thuộc lòng mạng bnlearn, đo prior bằng edge accuracy).
- **Không claim:** tăng tốc FCI; an toàn hữu hạn mẫu tổng quát; LLM "có" hay "không có" khả năng nhân quả.

## 4. Kế hoạch theo pha

### Phase 0 — Chuẩn bị và xác minh (13–16/11/2026)

1. **Xin phép:** tải mười file `.bif` từ kho bnlearn; cài gói client LLM; cấp API key qua biến môi trường; trần chi phí. Không commit key, dữ liệu, response thô.
2. **Mã:**
   - Parser `.bif` chỉ đọc cấu trúc; manifest SHA-256.
   - `mag_from_dag(G, O)` với vét cạn (|O| ≤ 12) và tiêu chí An-set (|O| > 12), kiểm chéo 100% theo luật §2.3.
   - `fci_oracle_typed_bk(G, O, injections)`: vòng định hướng tự viết dùng các hàm luật của causal-learn, chèn dấu theo ngữ nghĩa §3.2 của luật đọc, ghi log luật. Test: không chèn thì trùng `dag2pag`; T6, T7 không sinh dấu sai.
   - Phân loại cặp D, B, I, N; sinh pseudoword; sinh prompt; parser câu trả lời.
   - Mọi mã chạy với `python -I` hoặc `-P -E` và đọc dữ liệu tải về từ thư mục riêng trong `artifacts/`.
3. **Xác minh prior art:** đọc toàn văn Andrews 2020, Wang–Qin–Zhou 2022, NLPSCM, AGFN, COAT, 2608.23660, Faltenbacher 2026. Mục tiêu: xác nhận chưa ai đo lỗi tri thức nền **sai** theo loại cặp trong FCI, và chưa ai đo lỗi LLM theo loại ↔. Nếu có, ghi vào §3 và sửa pilot **trước** khi khóa luật.
4. **Phối hợp:** gửi nhóm một đoạn mô tả P-A để xác nhận không trùng kế hoạch đang có.

**Cổng P0:** luật đọc được khóa; test của mã pass; không phát hiện prior art làm P-A hoặc P-B thừa.

### Phase 1a — P-B (17–20/11)

Chạy theo luật §3. 400 đồ thị tổng hợp × (1 baseline + 7 kiểu × ≤ 5 cặp) ≈ 14 000 lần FCI oracle, mỗi lần dưới một giây với |O| ≤ 15 [Inference, kiểm ở Phase 0]; cộng bnlearn (≤ 30 đơn vị; `hepar2` với 70 nút có thể chậm ở Possible-D-SEP, nếu quá 10 phút mỗi lần thì ghi timeout và loại khỏi đối chiếu). Báo cáo `PB_results_vi.md` theo RB0–RB4.

### Phase 1b — P-A (19–27/11, sau khi có key)

Chạy theo luật §4. Q-GRAPH trước (180 lần gọi), Q-PAIR sau. Báo cáo `PA_results_vi.md` theo RA0–RA4.

### Quyết định D1 (chậm nhất 30/11)

Theo bảng §5 của luật đọc. Ghi vào `RESEARCH_HISTORY_vi.md` §1–§3. Nếu nhánh âm: đóng hướng, ghi mục X mới với bằng chứng, và kết thúc kế hoạch này tại đây.

### Phase 2 — Chỉ khi D1 là GO (12/2026–01/2027)

**2.1 Lặp P-B với mẫu hữu hạn.** SEM tuyến tính Gauss trên 100 đồ thị tổng hợp và trên cấu trúc bnlearn có ẩn biến; Fisher-z, α = 0.05, n ∈ {500, 2000}; cùng bảy kiểu chèn. Mục tiêu: hại ở oracle có còn khi có sai số thống kê, và lỗi mẫu hữu hạn có che lỗi do guess không.

**2.2 Đầu cuối với LLM thật.** Dùng chính guess từ P-A (Q-GRAPH, KEEP) làm tri thức nền cho FCI trên dữ liệu mô phỏng theo cấu trúc bnlearn có ẩn biến. Các nhánh, giữ cùng dữ liệu, cùng CI test, cùng α:
- FCI không tri thức nền;
- FCI với guess làm **hard BK** (cách chèn tự nhiên);
- FCI với guess chỉ đổi **thứ tự** kiểm định (tinh thần Guess2Graph, không đổi output tiệm cận);
- NLPSCM (tái lập từ mã công bố, nếu có);
- LLM một mình;
- ứng viên cơ chế của 2.3.
Metric: FA, FNA, Skel trên PAG; claim tổ tiên đúng; số CI test; thời gian. Bootstrap theo mạng.

**2.3 Cơ chế: lớp dịch có kiểu τ.** Ý tưởng [Hypothesis]: phát biểu của LLM chỉ được phép chạm vào output ở những vị trí mà dữ liệu **không** xác định (dấu tròn của PAG), và chỉ với kiểu dấu tương thích với mọi MAG trong lớp tương đương sau khi áp. Cụ thể: (i) với cặp mà LLM (Q-PAIR) trả lời "confounded" hoặc không chắc, τ không phát dấu nào; (ii) với claim có hướng, τ chỉ phát dấu nếu dấu đó không mâu thuẫn với sepset và với các dấu đã được dữ liệu xác định; (iii) mọi dấu do τ phát được gắn nhãn nguồn trong output. Mục tiêu lý thuyết, **tỉ lệ với claim**: mệnh đề rằng dưới oracle, output của FCI + τ luôn là PAG của một MAG trong lớp tương đương thật (lỗi chỉ có thể là *trong lớp*, không bao giờ *ngoài lớp*), và lỗi trong lớp bị chặn bởi số dấu τ phát. Phần này kế thừa ý "robust envelope" của hướng cũ (Fallible-Tier, [`archive/.../05_algorithm_optimization_portfolio.md`](../../archive/2026-09_safe_imperfect_priors/handoff/05_algorithm_optimization_portfolio.md)) nhưng đối tượng là dấu PAG chứ không phải tập điều kiện. Phải đối chiếu với Andrews 2020 và Wang–Qin–Zhou 2022 trước khi gọi mệnh đề là mới.

**2.4 Lý thuyết cho H-silent.** Đặc trưng hóa kiểu dấu chèn sai nào có thể rời lớp tương đương mà không tạo xung đột sepset nào trong FCI. Đây là phần đối ứng với cách phân loại lỗi theo hậu quả: không phải "guess sai gây hại bao nhiêu" mà "guess sai *loại nào* gây hại và vì sao". Nếu P-B cho SILENT, phần này là trọng tâm của bài.

**Cổng P2:** 2.1 xác nhận hại ở mẫu hữu hạn; 2.2 cho thấy hard BK tệ hơn không BK trên FA ở ít nhất một nửa số mạng với CI không chứa 0; τ không tệ hơn không BK trên FA và tốt hơn trên claim tổ tiên đúng. Không đạt thì dừng ở bài đo lường.

### Phase 3 — Viết (02–03/2027)

Hình dạng bài: **phép đo** (P-A, P-B, 2.1, 2.2) → **cơ chế** (2.4) → **phương pháp như hệ quả** (2.3) → **audit** (thuộc lòng mạng bnlearn; đo prior bằng edge accuracy che lỗi loại ↔). Đích: UAI 2027 hoặc TMLR; NeurIPS 2027 chỉ khi 2.3 và 2.4 đều có kết quả. Hạn nộp cần kiểm tra lại khi tới Phase 3.

## 5. Baseline bắt buộc (≥ 3, giữ cùng dữ liệu, giả định, ngân sách, output và metric)

1. FCI không tri thức nền.
2. FCI với hard BK từ LLM (cách chèn tự nhiên).
3. FCI với guess chỉ đổi thứ tự kiểm định (không đổi output tiệm cận).
4. NLPSCM (FCI + LLM tuần tự).
5. LLM một mình (Q-GRAPH).
6. Nếu còn thời gian: soft BK kiểu trọng số (RoaDs) chuyển sang PAG, ghi rõ đây là chuyển thể.

Mọi so sánh dùng PAG và claim tổ tiên; không dùng SHD của DAG cho output có biến ẩn.

## 6. Tài nguyên

- **Tính toán:** P-B và 2.1 chạy trên máy hiện tại (7.8 GB RAM) với |O| ≤ 20; Possible-D-SEP trên `hepar2` có thể cần timeout.
- **LLM:** 5–60 USD cho P-A tùy model; Phase 2.2 dùng lại guess của P-A, không tốn thêm.
- **Không cần R.** Không cần GPU.
- **Thời gian người:** khoảng 3 tuần cho Phase 0–1, 6–8 tuần cho Phase 2.

## 7. Rủi ro và điều kiện đóng hướng

| Rủi ro | Hậu quả | Phát hiện ở | Xử lý |
|---|---|---|---|
| Andrews 2020 hoặc Wang 2022 đã xét tri thức nền sai theo kiểu | P-B thừa | Phase 0 | Đổi P-B thành tái lập và mở rộng, hoặc đóng |
| LLM không thiên về → ở cặp ↔ (H-type sai) | Không có nguồn lỗi | P-A | Đóng phần phương pháp; giữ P-A làm phát hiện |
| T2, T3 không lan hơn T1 (H-prop sai) | Biến ẩn không thêm gì | P-B | Đóng; mentor đúng |
| Lan truyền có nhưng luôn phát hiện được (H-silent sai) | Bài toán quy về kiểm tra nhất quán, đã có prior art | P-B RB3 | Hạ kỳ vọng xuống bài đo lường |
| Thuộc lòng mạng bnlearn làm KEEP quá tốt | H-type bị che | P-A RA4 | Nhánh PSEUDO và mạng ít nổi tiếng; báo cáo theo mạng |
| Nhóm đang làm điều tương tự | Trùng lặp nội bộ | Phase 0 | Hỏi trước khi khóa luật |
| Hard BK là "rơm" dễ đánh | Reviewer bảo không ai dùng hard BK với LLM | Phase 2.2 | NLPSCM và soft BK là baseline thật; hard BK chỉ là điều kiện đo |

**Điều kiện đóng hướng vĩnh viễn:** nhánh cuối của bảng §5 luật đọc, hoặc Phase 0 phát hiện prior art làm cả hai pilot thừa.

## 8. Việc cần user quyết ngay

1. Duyệt luật đọc [`PA_PB_reading_rules_vi.md`](PA_PB_reading_rules_vi.md) sau khi điền ba tham số ⟦ĐIỀN⟧: danh sách LLM và cách truy cập; trần chi phí; cho phép tải bnlearn.
2. Cho phép cài gói client LLM vào `/c/Python314` (hoặc venv riêng) và cấp key qua biến môi trường.
3. Trao đổi với nhóm về P-A; cho tôi biết kết quả trước khi khóa.
4. Xác nhận ranh giới: X1 và X5 vẫn đóng; kế hoạch này không được trượt về "scheduler".
