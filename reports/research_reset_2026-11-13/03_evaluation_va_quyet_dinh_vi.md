# Failure modes, kế hoạch kiểm tra và quyết định có điều kiện

Ngày 13/11/2026. **Tất cả thí nghiệm dưới đây là đề xuất; chưa chạy.** Đọc cùng [shortlist](00_shortlist_va_danh_gia_vi.md), [matrix nguồn](01_evidence_matrix_vi.md) và [topic cards](02_topic_cards_vi.md).

## 1. Ba failure-mode dossier

Không gọi cả ba là failure đã được tái lập: F1 là giả thuyết mới dựa trên hai thành phần đã có bằng chứng; F2 là vấn đề target/evaluation có thể kiểm bằng ví dụ; F3 có failure nền trong literature nhưng cơ hội phương pháp mới chưa được xác nhận.

### F1 — Chia sẻ giả định giữa các phần dữ liệu không nên chia sẻ

**Quan sát nền [nguồn]:** AVICI học inductive bias qua simulator; Demystifying giải thích prior và identifiability của amortized discovery; TabCausal trao đổi thông tin trên các chiều của bảng. Xem P02–P04. **Chưa có quan sát mới** rằng một checkpoint đổi hướng vì remote module theo cơ chế N1.

**Điều kiện cần kiểm:** module đích có bằng chứng định hướng yếu; simulator huấn luyện chia sẻ một cấu hình cơ chế cho nhiều biến; khi sử dụng, module lại đến từ các hệ có cơ chế độc lập.

**Nguyên nhân giả thuyết:** mô hình dùng phần còn lại của bảng để nhận diện loại hệ sinh dữ liệu, rồi áp giả định ấy vào module đích. Đây có thể là suy luận hợp lý khi prior chung đúng, nhưng sai khi hệ thực tế ghép nhiều module độc lập. Không đồng nhất causal independence với independence trong prior.

**Remedy mạnh nhất phải so:** tiền xử lý cố định từng cột, inference theo module biết trước, prior phân rã, thuật toán cổ điển trong đúng lớp giả định. Module biết trước chỉ là oracle diagnostic. Cần kiểm raw score trước global decoder để tránh gán lỗi hậu xử lý cho encoder.

**Minimal reproduction đề xuất:** lưu một bảng đích A; ghép lần lượt các B độc lập cùng kích thước nhưng khác mechanism family; xác nhận A thực vào network giống từng bit. Lặp trên SCM mới, context mới, ít nhất hai checkpoint nếu khả thi. Đo paired score change và tác hại trên các cạnh có hướng identifiable.

**Ý nghĩa:** xác định ranh giới sử dụng mô hình học sẵn trên bảng ghép nhiều nguồn. Liên quan vấn đề ML hiện tại về chuyển tri thức từ dữ liệu tổng hợp và khả năng truy nguồn của một dự đoán; không cần gắn thêm LLM để tạo tính thời sự.

**Bác bỏ:** hiệu ứng chỉ do normalization, p, số học, hoặc decoder; không phân biệt family; biến mất trên xác nhận độc lập. Nếu ảnh hưởng có ích đúng trong shared-prior regime, đó là positive control, không phải failure.

### F2 — Điểm graph không nói rõ thuật toán đã trả lời sai hay chỉ chưa biết

**Quan sát nền [nguồn]:** AID/FID cho thấy cần đánh giá identification/estimands ngoài đếm graph edits; GAC và PAGcauses phân biệt những gì graph với latent cho phép suy ra. Xem P09–P13. Không có kết quả mới rằng bảng xếp hạng FCI/RFCI chắc chắn đảo chiều.

**Điều kiện:** phương pháp trả PAG/MEC với mức định hướng khác nhau; người dùng đọc graph để chọn công thức cho cùng một tập câu hỏi can thiệp.

**Nguyên nhân có thể:** một metric gộp sai khẳng định, bỏ lỡ cơ hội và bất định không tránh được; hoặc các phương pháp trả lời các tập query khác độ khó. Một graph edit có thể ảnh hưởng nhiều query hoặc không ảnh hưởng query đang xét.

**Remedy mạnh nhất:** strategy-specific identification distance có sẵn, generalized adjustment, risk/coverage và phân tầng query. Nếu các cách đơn giản này đủ giải thích mọi khác biệt, không có cơ sở tạo metric mới.

**Minimal reproduction đề xuất:** chọn DAG nhỏ có latent, suy ra oracle PAG; cố định query list. Dùng full DAG để kiểm công thức đúng/sai và oracle PAG để kiểm cơ hội mà cùng assumptions cho phép. Dựng thay đổi graph hợp lệ bằng D′ rồi suy ra PAG′. Không sửa tùy ý một endpoint rồi giả định vẫn là PAG hợp lệ. Tách graph-oracle khỏi finite-sample discovery.

**Ý nghĩa:** giúp người dùng lựa chọn output cho quyết định can thiệp, không thưởng phương pháp luôn từ chối và không phạt phương pháp vì bất định vốn có.

**Bác bỏ gap:** existing AID/FID plus stratification đã đáp ứng đúng task; chênh lệch chỉ là coverage; không tìm ra giải thích vượt số lượng lỗi hoặc độ khó query. Khi đó giữ công cụ evaluation nếu hữu ích, không gọi là đề tài phương pháp mới.

### F3 — Thu thập thêm mẫu khi phép đo làm biến đổi quan hệ cần học

**Quan sát nền [nguồn]:** sai số đo có thể phá conditional independence của các biến thực; P15–P18 có phân tích, correction hoặc phương pháp dành cho measurement error. Không khẳng định tăng n luôn làm graph tệ hơn.

**Điều kiện:** nhiễu tại biến dùng để điều kiện hóa; target là quan hệ giữa đại lượng thực; lặp phép đo cùng trạng thái có noise đủ độc lập; có chi phí thu thập đối tượng và chi phí phép đo.

**Nguyên nhân:** tăng n giảm bất định lấy mẫu nhưng không xóa bias do đo sai. Vị trí noise trong graph ảnh hưởng những CI nào bị phá; reliability thấp một mình chưa chắc xác định đúng biến nên đo lại.

**Remedy mạnh nhất:** covariance correction từ independent replicates; các correction/measurement-error methods P16–P18; thiết kế ngân sách và validation subsample cổ điển. Không lấy simple averaging làm baseline mạnh nhất.

**Minimal reproduction đề xuất:** chain, fork và collider cùng mức variance/noise; giữ SCM và pool đối tượng; phân bổ cùng tổng chi phí sang N và số technical replicates. Chạy baseline correction và tăng N trước một chiến lược thích nghi. Oracle graph-role chỉ là upper bound; quyết định thực tế chỉ được dùng pilot data và phải tính chi phí pilot.

**Ý nghĩa:** quyết định mua thêm mẫu hay cải thiện phép đo có hậu quả ngân sách thật. Nhưng cần dataset có replicates phù hợp; repeated time points không tự là technical replicates.

**Bác bỏ gap:** cách phân bổ cổ điển/correction đơn giản đã đạt tương đương; lợi ích chỉ xuất hiện khi biết graph thật; hoặc không có thực tế nào thỏa giả định noise của phép đo lặp. Hạ ưu tiên thay vì ép thành adaptive framework.

## 2. Nguyên tắc evaluation chung

| Thành phần | Quy tắc cụ thể |
|---|---|
| Đơn vị độc lập | N1–N3: SCM/dataset, không coi cạnh hay nhiều context của cùng SCM là replicates độc lập. N4: xem cấu trúc guide, batch và biological replicate; nhiều cell không tự tạo nhiều biological replicates |
| Paired comparisons | Giữ cùng local data hoặc cùng SCM/query/pool; thay một tác nhân đã định nghĩa. Ghi checksum cho input cần cố định |
| Khám phá/xác nhận | Dùng seeds/families riêng; chốt primary metric, expected direction nếu có, mức hiệu ứng có ý nghĩa và precision trước confirmation |
| Sai số thống kê | Báo effect size và uncertainty theo đơn vị lặp; bootstrap cluster khi phù hợp. Không dùng p-value nhỏ từ hàng nghìn cạnh phụ thuộc như bằng chứng độc lập |
| Synthetic | Dùng simulator tác giả và generator độc lập; công khai tham số/seed, cả regimes thuận và nghịch giả thuyết; không chỉ benchmark tự thiết kế |
| Dữ liệu thực | Chỉ dùng truth được thí nghiệm/nguồn xác lập; effect sau perturbation không tự là direct edge. Dữ liệu ghép phải gắn nhãn semi-real stress test |
| So sánh công bằng | Khớp assumptions, output, intervention information, query set, budget và tuning. Tách diagnostic oracle khỏi deployable method |
| Coverage | Báo cả số query trả lời và lỗi trên chúng; risk ở zero coverage là NA. Matched coverage chưa đủ nếu query difficulty khác |
| Robustness | Mechanism/noise/density/sample-size shift, permutations, preprocessing và decoder; chọn theo hypothesis từng hướng, không nhân vô hạn factorial grid |
| Chi phí | Ghi thời gian, RAM/VRAM và checkpoint/version; chưa có số đo nên không hứa chạy laptop được hay speedup |

**Không cần chờ hết benchmark mới quyết định dừng.** Một counterexample đúng target hoặc một baseline đơn giản loại mechanism là bằng chứng có giá trị để dừng sớm. Không dựng threshold hậu nghiệm để cứu hướng đã thất bại.

## 3. Lộ trình 4–6 tuần nếu user chọn N1

Đây là roadmap đề xuất sau review, không phải công việc đã chạy hoặc cam kết runtime. Thời gian là phân bổ công việc, phụ thuộc kiểm tra tài nguyên.

| Tuần | Công việc | Artifact | Gate |
|---|---|---|---|
| 1 | Citation-chain P03/P07; đọc training generator và preprocessing của hai checkpoint; xác định family-level shared hyperparameters; smoke test inference nhỏ | Prior/architecture audit, phiên bản/checksum, budget thực đo; protocol v1 | Nếu prior art đã trả lời đúng câu hỏi, hoặc không giữ A cố định được: đổi thiết kế/đóng |
| 2 | Paired exploratory swap cùng p; eval repeatability; normalization, permutation và decoder controls | Paired results + hình theo module; nhật ký mọi cấu hình, kể cả âm | Nếu chỉ có bug/numerics/dimension: không tiếp tục framing chuyển giả định |
| 3 | Phân biệt shared-prior positive control với independent-module deployment; tăng local identifying evidence; chạy cổ điển/module-only baselines | Competing-explanation table; chốt primary outcome và confirmation plan | Cần tín hiệu phù hợp giải thích hơn ít nhất một alternative mạnh; không chỉ một outlier |
| 4 | Xác nhận trên SCM/context chưa dùng và simulator độc lập; checkpoint thứ hai | Frozen confirmatory results, uncertainty và resource report | Nếu không tái lập: thu hẹp kết luận hoặc no-go, không chọn lại subset đẹp |
| 5, có điều kiện | Causal Chambers semi-real test; thêm architecture nếu tài nguyên cho phép; thử correction tối thiểu được cơ chế gợi ý | External-validity dossier; trade-off lợi/hại của sharing | Không quy mọi thay đổi output thành lỗi; real task cần truth đúng phạm vi |
| 6, có điều kiện | Viết mechanism/evidence narrative; audit claims, reproducibility và closest prior work lần nữa | Paper concept cập nhật, limitations, code/results nhỏ tái lập được | Chỉ GO dài hạn nếu có insight và bằng chứng ngoài protocol engineering |

Nếu N1 dừng, **không tự động chuyển N2 thành ACTIVE**. N2 phải qua gate riêng: kiểm nghĩa của output, validator và closest prior art trước khi chạy bảng thuật toán lớn. N3/N4 không chạy song song chỉ để tăng xác suất tìm kết quả dương.

## 4. Paper concept giả định cho N1

**Tên tạm:** *What Does the Rest of the Table Tell a Causal Discovery Model?*

**Câu hỏi:** khi phần dữ liệu đích không đổi, thông tin từ module độc lập ảnh hưởng đến suy luận nhân quả bằng cơ chế nào, và khi nào sự ảnh hưởng đó hợp lệ?

**Problem statement:** xét input D = [D_A, D_B], graph target G_A, với module A/B được sinh độc lập ở mức SCM. Phân biệt prior huấn luyện có shared hyperparameter H với prior phân rã trong triển khai. Đo output nội bộ A trước/sau decoder khi thay B cùng kích thước; kiểm cả sensitivity và correctness theo lớp assumptions. Không đòi invariant một cách vô điều kiện.

**Closest work:** P03 về prior/identifiability; P07/P08 về compatibility; P02/P04/P05 về inference học sẵn và benchmark. Contribution phải vượt “training distribution matters” và “output thay đổi khi đổi tập biến”.

**Scientific insight cần kiểm:** context có thể hoạt động như bằng chứng về loại cơ chế, dù không phải nguyên nhân của module đích. Lợi ích/hại phụ thuộc việc training prior và cấu trúc module khi sử dụng có tương thích hay không.

**Cơ chế nghiên cứu đề xuất:** paired module replacement, kết hợp shared-vs-independent prior và local identifying evidence. Đây là một protocol thử nghiệm để kiểm lời giải thích; **chưa phải cơ chế thuật toán mới đã được xác nhận**. Nếu có bằng chứng, thử module-aware sharing và kiểm cả mất lợi ích hợp lệ lẫn giảm tác hại; partition/gating bản thân không mới.

**Ba đóng góp tiềm năng, không phải đã đạt:**

1. Phép thử tách nguồn ảnh hưởng đến một kết luận local, có controls loại thay đổi chiều dữ liệu, preprocessing và decoding.
2. Giải thích khi nào context có ích/có hại bằng mismatch của shared mechanism prior, với dự đoán bác bỏ được trên nhiều simulator/checkpoint.
3. Khuyến nghị sử dụng hoặc sửa tối thiểu được kiểm trên dữ liệu mới, kèm trade-off giữa chia sẻ đúng và chuyển sai.

**Nghĩa vụ lý thuyết:** phát biểu đúng factorization đủ cho invariance; đưa ví dụ shared-H mà dependence là hợp lệ; phân biệt sample-size effects và population/prior identifiability. Công thức Bayes trong topic card là nền, không claim định lý mới. Nếu đề xuất gate có bảo đảm, phải chứng minh đúng điều kiện hoặc chỉ trình bày empirical method.

**Thực nghiệm:** các hypotheses/controls/baselines trong N1 card; public authors' generators, generator độc lập, fixed checkpoints và semi-real Chambers nếu khả thi. Bắt đầu causal sufficiency/iid; chưa suy rộng sang latent, dynamics hoặc dữ liệu text.

**Giới hạn:** independence của module trong đời thực khó biết; cơ chế prior có thể không xác định duy nhất từ input-output; hai mô hình axial attention không đại diện mọi foundation model. Không diễn giải attention weights như causal mediation proof.

### Abstract giả định — không có kết quả thực nghiệm

Các mô hình học sẵn có thể suy ra đồ thị nhân quả bằng cách đọc toàn bộ bảng dữ liệu. Tuy nhiên, chưa rõ phần dữ liệu bên ngoài một hệ con ảnh hưởng thế nào đến kết luận trong hệ đó. Nghiên cứu đề xuất giữ nguyên hệ con đích và thay các khối độc lập đi kèm, với cùng kích thước và tiền xử lý. Thiết kế phân biệt hai trường hợp: các hệ chia sẻ giả định về cơ chế, hoặc có cơ chế được chọn độc lập. Chúng tôi sẽ kiểm tra liệu ảnh hưởng của dữ liệu đi kèm phản ánh việc học giả định chung, nhiễu lấy mẫu hay hậu xử lý đồ thị. Đánh giá dự kiến sử dụng mô hình công khai, phương pháp cổ điển và các bộ sinh dữ liệu độc lập. Mục tiêu là xác định khi nào chia sẻ thông tin giúp suy luận, khi nào gây hại, và liệu thay đổi tối thiểu có giảm tác hại mà vẫn giữ lợi ích. Các kết quả sẽ quyết định phạm vi đóng góp.

## 5. Bảy câu trả lời để ra quyết định

| Câu hỏi | Đánh giá hiện tại |
|---|---|
| Vấn đề khoa học quan trọng nhất? | Với mục tiêu ML-methodology của nhóm, N1: hiểu nguồn bằng chứng của mô hình học sẵn khi áp dụng trên dữ liệu ghép nhiều cơ chế. N4 có stakes ứng dụng cao nhưng không vì thế khả thi hơn |
| Cơ chế có novelty dễ bảo vệ nhất? | N1 có khoảng trống **tiềm năng** rõ nhất trong shortlist: phân biệt chuyển giả định đúng/sai bằng same-target context swap. Bayes/prior/partitioning không mới; novelty của hiện tượng và explanation chưa confirmed |
| Có thể làm với nguồn lực hiện tại? | Có thể chuẩn bị inference pilot N1 và graph-oracle pilot N2; checkpoint/code công khai. Chưa đo tài nguyên nên chưa xác nhận ngân sách. N3 thiếu dataset phù hợp, N4 cần domain review |
| Cân bằng chất lượng/rủi ro cho Q1? | N1 ưu tiên, N2 backup có điều kiện. N1 có phép thử sạch và ý nghĩa ngoài một thuật toán; N2 hợp kỹ năng nhưng rất dễ thành metric extension. Không có cam kết acceptance |
| Điều gì có thể cạnh tranh ICML/NeurIPS? | Hiện tượng quan trọng, tái lập qua kiến trúc/generator, giải thích phân biệt alternatives, insight về chuyển prior và intervention có trade-off được xác nhận. Một flip plot hoặc SOTA gain đơn lẻ không đủ |
| Bằng chứng không thể thiếu? | A giữ nguyên sau preprocessing, B cùng p; ảnh hưởng có cấu trúc vượt controls và tác động correctness đúng assumptions; confirmation độc lập và đối chiếu closest prior art |
| Hạ ưu tiên hướng nào? | N3 vì prior art correction/design mạnh và thiếu data; N4 vì identification/selection/biology khó. Loại framing “PAG-AID là mới vì có latent” và việc phục hồi P17 bằng silent-error metric cũ |

**Quyết định của bản báo cáo: SHORTLIST FOR USER REVIEW.** Không mở lại hướng đã đóng, không chọn hộ đề tài ACTIVE và không triển khai framework.

## 6. Đối chiếu deliverables của repo

| Yêu cầu research/08 | Vị trí |
|---|---|
| A. Landscape | 01_evidence_matrix_vi.md: 24 nguồn lõi + nguồn lân cận có mức đọc riêng |
| B. Failure dossiers | §1 của file này; phân biệt verified nền và hypothesis chưa tái lập |
| C–E. Opportunities, novelty, methods/theory | 02_topic_cards_vi.md, N1–N4 |
| F. Evaluation | Topic cards và §2 của file này |
| G. Recommendation | 00_shortlist_va_danh_gia_vi.md, §§5–6 |
| H. Roadmap | §3 của file này |
| I. Paper concept | §4 của file này |
| J. Critical verdict | §5 của file này |
