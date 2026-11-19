# Chọn lại hướng nghiên cứu: bốn ứng viên để review

Ngày: **13/11/2026**. Trạng thái: **RESEARCH SHORTLIST — chưa chọn đề tài, chưa chạy pilot mới**.

## 1. Kết luận để ra quyết định

**Tôi đề nghị ưu tiên kiểm tra N1, giữ N2 làm dự phòng; N3 và N4 là hai lựa chọn khác về câu hỏi khoa học, không phải biến thể của N1.** Chưa ứng viên nào đủ bằng chứng để cam kết xây một framework.

| Hạng | Đề tài ứng viên | Nói đơn giản | Hai hiệu ứng giao nhau | Câu hỏi “vì sao” | Đòn bẩy sạch |
|---|---|---|---|---|---|
| **1 — N1** | **Khi dữ liệu không liên quan làm đổi kết luận nhân quả: chuyển giả định giữa các phần của bảng dữ liệu trong amortized causal discovery** | Giữ nguyên dữ liệu A và B; thay các cột độc lập đi kèm. Vì sao mô hình có thể đổi ý về A → B? | Mô hình học prior từ simulator × mô hình đọc đồng thời cả bảng | Nó dùng bằng chứng tại A/B, hay suy ra loại cơ chế từ phần khác rồi áp sang A/B? | Hoán đổi một khối dữ liệu độc lập; giữ nguyên từng giá trị của khối đích, số dòng, số cột và tiền xử lý |
| **2 — N2** | **Đồ thị tốt hơn có dẫn tới kết luận hiệu ứng tốt hơn? Tách sai lầm khỏi việc chưa đủ thông tin khi đánh giá discovery có biến ẩn** | Thuật toán nói được nhiều hơn chưa chắc nói đúng hơn; nhưng thuật toán luôn “chưa biết” cũng không thể được coi là tốt nhất | Lỗi cấu trúc có hậu quả khác nhau × PAG chứa bất định thực sự | Lợi thế nằm ở kết luận đúng thêm, kết luận liều hơn, hay cách chấm điểm? | Cùng câu hỏi can thiệp, so hậu quả của các thay đổi đồ thị hợp lệ; dùng cả ground-truth DAG và oracle PAG đúng vai trò |
| **3 — N3** | **Đo nhiều đối tượng hay đo chính xác hơn? Vai trò vị trí sai số đo trong thiết kế dữ liệu cho causal discovery** | Với cùng tiền, lấy thêm bệnh nhân hay đo lại một xét nghiệm? Tại sao đo lại đúng biến có thể đáng hơn tăng toàn bộ mẫu? | Sai số ở biến dùng để điều kiện hóa làm mất CI × mẫu lớn phát hiện phụ thuộc nhỏ hơn | Vấn đề nằm ở thiếu mẫu hay đang đo chính xác hơn một quan hệ sai do thiết bị? | Cùng SCM và các cá thể gốc; thay vị trí nhiễu và số phép đo lặp độc lập dưới cùng ngân sách |
| **4 — N4** | **Lọc tế bào “đã đáp ứng” giúp tìm quan hệ nhân quả hay chọn sẵn kết quả?** | Loại tế bào không phản ứng có thể làm tín hiệu đẹp hơn; nhưng có thể đã chọn theo chính thứ muốn kiểm tra | Can thiệp gene có hiệu lực không đồng đều × chọn tế bào bằng biểu hiện sau can thiệp | Điểm tăng do bỏ nhãn can thiệp sai, do chọn nhóm đáp ứng, hay do dùng lại outcome để đánh giá? | Cùng cell pool; thay nguồn dùng để gán trạng thái đáp ứng và mức phụ thuộc vào trạng thái tế bào; đánh giá bằng dữ liệu độc lập |

**Cả bốn đều là hypothesis.** Literature xác nhận các thành phần của câu hỏi, chưa xác nhận hiệu ứng giao nhau theo thiết kế đề xuất. “Chưa tìm thấy bài làm đúng phép thử này” không đồng nghĩa đã chứng minh novelty.

Tài liệu đi kèm:

- [Ma trận 24 nguồn và sổ claim](01_evidence_matrix_vi.md).
- [Bốn topic card: giả thuyết, đối thủ, thiết kế, điều kiện loại](02_topic_cards_vi.md).
- [Ba failure-mode dossier, lộ trình và paper concept](03_evaluation_va_quyet_dinh_vi.md).
- [Manifest nguồn PDF đã đọc](source_manifest.json). Bản cache ở `artifacts/research_reset_2026-11-13/sources/`; không thay đổi kho `docs/papers/`.

## 2. Đọc lại repo đã thay đổi cách chọn đề tài như thế nào?

Đã đọc `AGENTS.md`, tám tài liệu `research/01–08`, lịch sử X1–X33, kết quả P-A/P-B, bản quét 13/11 và một tài liệu tham khảo nội bộ. Lịch sử xác nhận P17 đã đóng; không có hướng ACTIVE. Các dòng trạng thái cũ trong history là nhật ký append-only, không phải quyết định mới.

Những hướng sau **không được mở lại** trong đề xuất này:

- A′/R1: đổi hình dạng miền thống kê rồi kỳ vọng có lợi thế phương pháp.
- T4/T4-L: thay xác nhận listwise bằng phép lift chỉ báo thiếu.
- TS-G1: lấy mưa làm proxy rồi quy thay đổi output cho confounding.
- P17: giả thuyết LLM mắc và lan lỗi đặc thù biến ẩn nhiều hơn.
- Scheduler, pruning, caching, “LLM + FCI”, hoặc audit một lỗi benchmark làm toàn bộ đề tài.

N1 dùng mô hình nhận **bảng số**, không dùng LLM đoán cạnh từ tên biến; không phải P17 đổi tên. N3 nghiên cứu sai số của phép đo và chi phí thu thập, không tiếp tục C1 về sensor redundancy hoặc X30 về misspecification phi tuyến. N4 là selection **do quy trình phân tích can thiệp**, không phục hồi T4-L.

N2 có liên hệ với C1 trong bản quét sơ bộ 13/11. Bản quét đó chưa phải hướng đã được user chọn. Tôi chỉ giữ câu hỏi downstream sau khi sửa các lỗi về target và ranh giới novelty ở §4; không kế thừa khuyến nghị “xây PAG-AID” như một đóng góp đã chắc.

## 3. Áp dụng đúng bài học từ tài liệu tham khảo nội bộ

Nguồn: tài liệu tham khảo nội bộ (không công khai). Các kết quả của tài liệu đó không được tái lập trong lượt này.

| Bài học | Điều phải có trong một ứng viên | Điều không đủ |
|---|---|---|
| Giao hai hiệu ứng đã biết | Hai cơ chế có lý do cụ thể để tương tác trên cùng một quyết định | Ghép hai keyword, hai thuật toán, hoặc hai loại dữ liệu |
| Đo trong cùng đơn vị | Cùng bảng dữ liệu đích, cùng SCM hoặc cùng câu hỏi; thay thứ muốn khảo sát | So hai benchmark khác nhau rồi quy chênh lệch cho một nguyên nhân |
| Hỏi “vì sao” | Ít nhất hai giải thích cạnh tranh và đối chứng phân biệt chúng | Chỉ vẽ accuracy theo mức nhiễu |
| Đòn bẩy sạch | Biết chính xác thứ đã đổi và thứ được giữ nguyên | Proxy gần đúng, graph truth chưa rõ, hoặc đổi cả generator |
| Khám phá rồi xác nhận | Tách seeds/SCM/dataset dùng tìm cơ chế khỏi tập xác nhận | Chọn hiện tượng đẹp rồi dùng chính nó để kết luận |
| Kết quả âm vẫn học được | Mỗi nhánh thu hẹp một giải thích hoặc một phạm vi áp dụng | Hứa rằng mọi kết quả âm đều đủ thành bài Q1 |

Một tương tác đáng kiểm tra có thể viết dưới dạng:

`I = [Kết quả(A1,B1) − Kết quả(A0,B1)] − [Kết quả(A1,B0) − Kết quả(A0,B0)]`.

Nhưng **có interaction thống kê chưa chứng minh cơ chế**. Cần tiếp tục thay nguồn thông tin, loại confound trong thiết kế và kiểm trên dữ liệu mới. Cũng không nhất thiết phải có interaction khác 0 để bài có giá trị: một cận trên chặt có thể bác bỏ một lời giải thích quan trọng. Nó không tự động tạo thành đóng góp đủ lớn.

## 4. Vì sao không dùng nguyên bản quét 13/11?

### 4.1 PAG đúng vẫn có thể chưa cho phép tính hiệu ứng

Giả sử thực tế là `X → Y`, nhưng chỉ có quan sát trên X và Y, không có giả định bổ sung cho hướng. Một phương pháp đúng có thể trả lớp tương đương, không đủ cơ sở chọn chiều. Nếu lấy DAG đầy đủ làm chuẩn rồi phạt câu trả lời “chưa xác định được”, ta đang phạt **thiếu thông tin vốn có**, không riêng lỗi thuật toán.

Do đó, hai yêu cầu của bản quét — phạt “không có adjustment set” nếu DAG thật có set, và đòi metric bằng 0 cho PAG thật — **không đồng thời đúng nói chung**. AID đã phân biệt graph classes và cách đọc non-identifiability; đây không phải lỗi của AID, mà là lỗi khi chuyển target. [AID, §4](https://proceedings.mlr.press/v244/henckel24a.html); [Perković et al., Definitions 1–4 và Theorem 5](https://jmlr.org/papers/v18/16-319.html).

N2 vì vậy phải báo cáo riêng:

1. **Kết luận sai:** công thức mà thuật toán đề nghị không hợp lệ trong hệ thật.
2. **Cơ hội bị bỏ lỡ:** oracle có cùng thông tin và giả định giải được, thuật toán thì không.
3. **Bất định không tránh được:** chính oracle cũng chưa giải được.
4. **Phạm vi trả lời:** bao nhiêu câu hỏi được trả lời, trên mẫu câu hỏi nào.

### 4.2 Không phải “chưa có metric khi có latent”

Separation distances đã xét MAG và MEC; FID đã đo sai khác cause-effect estimands trên ADMG. PAGcauses đã tính các hiệu ứng khả dĩ qua adjustment. Không được gọi “đánh giá hậu quả hiệu ứng” hoặc “xử lý latent” là gap mới. [Wahl–Runge 2025](https://proceedings.mlr.press/v258/wahl25b.html), [Li–Kilbertus 2025](https://arxiv.org/abs/2510.25037), [Wang et al. 2023](https://proceedings.mlr.press/v202/wang23ag.html).

PAG-AID chỉ là một công cụ tiềm năng cho nghiên cứu. Ghép adjustment criterion với khung AID **chưa đủ novelty**. FID trên một ADMG chọn tùy ý cũng không thay được đánh giá toàn bộ ý nghĩa của PAG.

### 4.3 Không mặc định FCI kém precision vì nhiều dấu tròn

Để dấu tròn thường làm giảm số khẳng định hướng, không tự động làm giảm precision của những khẳng định đã đưa ra. Muốn giải thích một bảng metric phải đọc chính xác mẫu số và quy ước chấm. Nhận định trong bản quét là hypothesis chưa được chứng minh, không được dùng làm động cơ thực nghiệm đã xác nhận.

### 4.4 Không phục hồi P17 bằng phát hiện “im lặng” hậu nghiệm

P-B ghi rõ phép đo conflict ban đầu có điểm mù; tỷ lệ “silent” thay đổi sau kiểm bổ sung. Hướng mới về silent errors có thể tồn tại, nhưng hiện thiếu bằng chứng mới vượt X33. Tôi không chọn nó làm backup mặc định.

### 4.5 Phép 2×2 có/không latent chưa tự tách được nguyên nhân

Ẩn một biến đổi cả tập biến, target projection, độ dày graph và họ query. Chênh lệch với finite-sample CI không tự là “phần lỗi do Possible-D-SEP”. Thiết kế cần theo dõi những câu hỏi giữ nguyên ý nghĩa; một bảng 2×2 không tự làm đòn bẩy sạch.

## 5. Đánh giá tương đối bốn hướng

Các mức dưới đây là **đánh giá của lượt audit**, không phải xác suất được nhận bài. “Novelty tiềm năng” chỉ áp dụng cho câu hỏi hẹp trong topic card.

| Tiêu chí | N1: chuyển giả định giữa khối | N2: sai vs chưa biết | N3: ngân sách đo lường | N4: lọc responder |
|---|---|---|---|---|
| Ý nghĩa | Cao: độ tin cậy của mô hình học sẵn trên bảng ghép từ nhiều nguồn | Cao: dùng graph để chọn điều chỉnh và suy luận hiệu ứng | Cao: quyết định thu thập dữ liệu tốn tiền | Cao: diễn giải can thiệp gene và đánh giá mô hình sinh học |
| Bằng chứng nền | Có prior học từ simulator và kiến trúc trao đổi thông tin; hiệu ứng remote chưa đo | Có lý thuyết và metric rất gần; chênh lệch thực tế chưa đo | Failure do sai số đo đã rõ; lợi ích phân bổ chưa đo | Heterogeneity đã rõ; bias của pipeline cụ thể chưa đo |
| Novelty tiềm năng | **Khá nhất** ở ranh giới giữa dùng context hợp lệ và áp prior sai giữa module | Vừa: rất gần AID/FID; cần phát hiện cơ chế, không chỉ metric | Vừa–thấp: correction và repeated measurement đều cổ điển | Vừa: cần tách khỏi selection bias/circular analysis đã biết |
| Đòn bẩy | **Rất sạch** với khối đích cố định và khối độc lập thay thế | Sạch ở graph-oracle; khó hơn với output không hợp lệ | Sạch trong mô phỏng, khó có technical replicates thật | Sạch trong mô phỏng; khó xác định true efficacy ở dữ liệu thật |
| Yêu cầu toán | Một phân tích hierarchical prior; không cần theorem nền mới | Semantics verifier và oracle reference phải đúng | Sai số CI và covariance correction; không cần định danh mọi graph | DAG selection, định nghĩa estimand, không được lẫn ITT với effect among responders |
| Baseline dễ giết ý tưởng | Tiền xử lý đúng, giữ cùng p, component-only inference | AID/FID + risk/coverage và phân tầng đơn giản | Covariance correction từ hai phép đo lặp | Independent outcome evaluation; all-assigned analysis; joint latent model |
| Dữ liệu công khai | Có generators/checkpoints; benchmark đối chiếu có | Có mô phỏng tác giả; truth thật giới hạn | Chưa xác minh dataset có replicates và causal truth cùng lúc | Có screen công khai; không có full DAG truth |
| Khả thi hiện tại | Inference mô hình có sẵn; tài nguyên thực tế cần smoke test | Hợp kỹ năng repo; validator graph là khâu khó | Pilot nhỏ khả thi; validation thật là nút thắt | Cần năng lực/domain review sinh học; chi phí cao hơn |
| Nguy cơ thành audit nhỏ | Vừa nếu chỉ thấy score dao động | Cao nếu chỉ đổi leaderboard | Cao nếu chỉ có bias–variance trade-off quen thuộc | Cao nếu chỉ minh họa collider bias |
| Quyết định | **Ưu tiên kiểm tra** | **Dự phòng** | Giữ để review, chưa ưu tiên | Giữ như lựa chọn chuyển sang ứng dụng, chưa ưu tiên |

**Điểm phân biệt:** N1 cho phép hỏi một câu mà benchmark tổng hợp thông thường khó trả lời: với dữ liệu cần suy luận không đổi, phần còn lại của bảng đang cung cấp bằng chứng hợp lệ hay đang áp đặt giả định? N2 tốt về năng lực thực hiện nhưng không được ưu tiên chỉ vì repo đã có FCI/MAG.

## 6. Bằng chứng cần trước khi đầu tư nhiều tháng

| Hướng | Bằng chứng đầu tiên có tính quyết định | Nếu không đạt |
|---|---|---|
| N1 | Context thay thế cùng kích thước gây thay đổi có hệ thống ở khối đích; giải thích bằng loại cơ chế tốt hơn normalization/dimension/randomness; xác nhận trên checkpoint khác | Nếu hiệu ứng mất sau controls: đóng framing chuyển prior; giữ kết quả giới hạn, không xây kiến trúc mới |
| N2 | Phân loại sai/abstain giải thích hậu quả hiệu ứng ngoài SHD và ngoài thay đổi coverage, trên nhiều graph families | Nếu mọi khác biệt chỉ do coverage hoặc metric có sẵn đã giải thích đủ: không xây metric mới |
| N3 | Chiến lược đo dựa vào vai trò biến có ích ngoài correction đơn giản, khi chưa biết graph thật và tính đủ chi phí | Nếu correction hoặc replication đều đạt tương đương: không phát triển adaptive acquisition |
| N4 | Dấu hiệu cải thiện tồn tại khi dùng cùng outcome cho lọc/chấm nhưng thay đổi rõ với readout độc lập; tách được khỏi đổi estimand và giảm sample size | Nếu chỉ là đổi estimand hoặc joint model đã xử lý đủ: thu hẹp/đóng; không kết luận Mixscape “sai” |

Không khóa trước một ngưỡng “10 điểm phần trăm” cho mọi hướng. Trước pilot xác nhận phải định nghĩa **đại lượng chính, mức thay đổi có ý nghĩa ứng dụng, độ chính xác cần đạt và đơn vị lặp**. Giai đoạn khám phá dùng để ước lượng chi phí/variance, không dùng lại làm bằng chứng xác nhận.

## 7. Phạm vi công việc đã hoàn thành và giới hạn

- Đã đối chiếu **24 nguồn lõi, gồm một tài liệu nội bộ**, với nguồn gốc/venue/mức đọc trong matrix; đọc có mục tiêu các định nghĩa, cơ chế và thực nghiệm liên quan. Không tuyên bố đã kiểm toàn bộ chứng minh của mọi bài hoặc hoàn tất systematic review.
- Đã lấy PDF mở từ nguồn tác giả/proceedings để audit, lưu manifest SHA-256; không sửa/xóa các tài liệu cũ.
- Đã viết bốn topic card, ba dossier, thiết kế đối chứng, roadmap và paper concept giả định.
- **Chưa chạy bất kỳ pilot N1–N4 nào; chưa đo runtime/RAM checkpoint; chưa tải dataset mới quy mô lớn; chưa huấn luyện mô hình.** Các ví dụ đại số trong báo cáo là phân tích, không phải kết quả thực nghiệm.
- Không thay đổi quyết định lịch sử hay đánh dấu ứng viên ACTIVE. Danh sách này chờ user review.

Kết luận của audit là **có bốn câu hỏi đáng xem xét ở các mức ưu tiên khác nhau, nhưng chưa có gap đã được xác nhận bằng pilot**. Khuyến nghị đầu tư lượt kiểm tra tiếp theo vào N1, không cam kết một thuật toán trước khi biết cơ chế có thật.
