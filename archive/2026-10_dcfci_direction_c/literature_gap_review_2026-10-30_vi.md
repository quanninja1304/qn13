**Review tài liệu và các research gap để thảo luận — 30/10/2026**

**Trạng thái: bản phân tích, chưa phải quyết định đổi hướng hoặc kế hoạch triển khai đã được duyệt.** Người nghiên cứu chấp nhận cả đóng góp thuật toán và nghiên cứu thực nghiệm giải thích cơ chế nếu gap đủ mạnh. Hướng GPU đã được loại khỏi phạm vi.

Kết luận của lần review này: vấn đề của hướng cũ không chỉ nằm ở cách trình bày. Những ý tưởng rộng như dùng LLM để ưu tiên tìm kiếm, xử lý prior sai, hoặc kết hợp LLM với discovery có biến ẩn đều đã có công trình gần. Muốn có đóng góp rõ, cần chỉ ra một cơ chế chưa được giải quyết hoặc một bước thuật toán cụ thể, rồi thiết kế phép thử có thể bác bỏ chính đề xuất của mình.

Ba ứng viên dưới đây đáng được kiểm tra, nhưng chưa ứng viên nào được xác nhận có hiệu ứng đủ lớn hoặc novelty đủ mạnh. Tôi ưu tiên review **A: vòng phản hồi làm tăng sự tin tưởng vào prior sai**, giữ **C: sinh ứng viên dcFCI hiệu quả hơn** nếu muốn đóng góp thuật toán thuần, và xem **B: calibration trên cạnh dễ không chuyển được sang cạnh khó** là ứng viên dự phòng. Đây là xếp hạng dựa trên tài liệu và độ rõ của phép thử, không phải kết quả thực nghiệm.

**Phạm vi đọc và mức độ tin cậy**

Đã đọc proposal `C:\Users\ADMIN\Downloads\RESEARCH_PROPOSAL.md`, hồ sơ dự án, checkpoint và các tài liệu liên quan trong repo; đọc các phần phương pháp, giả định, định lý và thí nghiệm của sáu PDF trong `docs/papers`. Với Guess2Graph, đối chiếu thêm bản AISTATS 2026 vì bản PDF lưu trong repo là bản sớm hơn. Các tài liệu bổ sung được phân biệt theo mức đọc trong ma trận:

- **M**: đã đọc phần phương pháp hoặc thuật toán và các phần liên quan trực tiếp đến nhận định trong bảng; không có nghĩa đã kiểm chứng mọi chứng minh hay tái lập kết quả.
- **S**: sàng lọc bằng abstract/trang xuất bản và phần giới thiệu; đủ xác định có công trình gần, chưa đủ kết luận chính xác một giới hạn kỹ thuật.
- **C**: có đối chiếu thêm mã nguồn công khai.

Các kết quả của bài báo và proposal là **kết quả tác giả báo cáo**. Review này không chạy lại thí nghiệm của họ. Tìm kiếm bổ sung ưu tiên nguồn tác giả, arXiv, proceedings và nhà xuất bản, kiểm tra đến 30/10/2026. Đây là tìm kiếm có mục tiêu theo các claim liên quan, không phải systematic review toàn bộ lĩnh vực. “Chưa thấy trong các nguồn đã kiểm tra” không đồng nghĩa “chưa ai làm”.

**Tình trạng dự án ảnh hưởng thế nào đến việc chọn hướng**

Theo [hồ sơ dự án](../2026-09_safe_imperfect_priors/reports/research_project_dossier_2026-10-21_vi.md) và [checkpoint](../2026-09_safe_imperfect_priors/reports/research_checkpoint_2026-10-19_vi.md): K0 đã có 220/220 lượt pass; K1 có decision-pass trên snapshot 675/800 lượt, 133 graph hoàn chỉnh, median saving 23,60% cho chỉ tiêu tests-to-95 trong phạm vi FAS-stable skeleton. Formal gate chưa đóng; các file gate cũ chưa đồng bộ. K2/K3 chưa chạy; K4 còn phụ thuộc backend RFCI và bộ chuyển ground truth độc lập.

Vì vậy, dữ liệu hiện tại hỗ trợ phát biểu “có headroom trong một phần của thuật toán”. Chưa hỗ trợ “LLM thu hồi được headroom”, “toàn bộ FCI nhanh hơn 23,60%”, hoặc “an toàn finite-sample”. C0/C1/C2 là hạ tầng và audit có giá trị; chúng chưa tự tạo thành một scientific contribution về thuật toán mới. Frozen stable epoch cũng không tự động tương đương mọi lịch chạy dynamic ICD.

Có thể tái sử dụng CI oracle/cache, trace truy vấn, kiểm tra endpoint và bộ sinh đồ thị. Không cần buộc đề tài mới tiếp tục mục tiêu scheduler chỉ để bảo toàn công sức đã bỏ ra.

**Ma trận 1 — sáu tài liệu đã có trong repo**

| Công trình; mức đọc | Bài toán và đầu vào | Can thiệp thuật toán thực sự | Giả định/phạm vi kết luận | Điều này loại trừ hoặc để lại cho đề tài |
|---|---|---|---|---|
| [Guess2Graph / AISTATS 2026](https://proceedings.mlr.press/v300/hiremath26a.html); M, bản local và bản cuối | Tận dụng expert không hoàn hảo để cải thiện discovery trên DAG causally sufficient | PC-Guess thay thứ tự truy vấn; gPC tổ chức lại tìm kiếm separating set để loại cạnh không tồn tại sớm | Consistency với CI nhất quán; các kết quả đơn điệu theo chất lượng expert cần mô hình lỗi/điều kiện riêng. Bản cuối có Appendix D.7 về lỗi bất đối xứng theo lớp | “Prior chỉ điều khiển thứ tự nên có thể tăng tốc” đã có nền tảng gần. Không thể gọi chỉ riêng thêm nhiễu bất đối xứng là mới. PAG và finite-sample cần lập luận riêng, nhưng đổi PC thành FCI chưa đủ thành contribution |
| [L2D-CD](https://arxiv.org/abs/2502.13132); M | Khi nào dùng kết quả CD, khi nào chuyển sang LLM? | Học bộ quyết định deferral từ metadata/embedding và nhãn đúng-sai của phương pháp | Phần thực nghiệm trọng tâm là causal direction theo cặp; cần dữ liệu huấn luyện có đáp án. Mở rộng graph không tương đương một phương pháp PAG đã được xác lập | “Học khi nào nên tin LLM” đã có. Có thể nghiên cứu lỗi chuyển giao của quyết định tin cậy, nhưng phải vượt qua baseline deferral có sẵn |
| [RoaDs — Robust Causal Discovery under Imperfect Structural Constraints, AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/41001); M | Structure learning với ràng buộc cạnh có thể sai | Học trọng số surrogate, kết hợp mục tiêu fit dữ liệu và ràng buộc bằng tối ưu đa mục tiêu | Bản đọc giả định causal sufficiency; bảo đảm có điều kiện, không phải mọi prior sai đều vô hại ở mẫu hữu hạn | “Soft prior + tự giảm trọng số ràng buộc sai” không còn là novelty. Không được suy ra bài đã giải quyết PAG có biến ẩn |
| [tFCI & tIOD, CLeaR 2025](https://proceedings.mlr.press/v275/bang25a.html); M | Dùng thứ tự thời gian; có thể tích hợp các tập biến quan sát chồng lấn | Giới hạn search bằng tier, thêm orientation; tIOD dùng tier để thu hẹp ứng viên tương thích | Tier được xem là đúng; bản đọc loại selection bias. Simple tFCI và full tFCI có phạm vi completeness khác nhau | “Tận dụng prior thứ tự để giảm CI khi có biến ẩn” đã có. Prior sai là thay đổi giả định quan trọng, nhưng cần cơ chế cụ thể ngoài việc đặt tên robust-tier |
| [RFCI, Annals of Statistics 2012](https://arxiv.org/abs/1104.5617); M | Discovery có latent/selection trên nhiều biến | Thay phần tìm kiếm nặng bằng các kiểm định cục bộ, thường ít và bậc thấp hơn | Có bảo đảm nhân quả dưới giả định; không mặc nhiên trả cùng toàn bộ thông tin với FCI. Bài xác định các trường hợp trùng nhau | Baseline bắt buộc nếu claim tăng tốc. So với FCI chậm mà bỏ RFCI dễ đánh giá quá cao lợi ích; cũng không được yêu cầu RFCI luôn có output giống FCI |
| [dcFCI, Ribeiro & Heider, bản 2025](https://arxiv.org/abs/2505.06542); M+C | Duy trì nhiều cấu trúc có thể phù hợp khi CI không chắc chắn, có biến ẩn | Tạo nhiều tổ hợp minimal separating sets, dựng/kiểm tra PAG, tính score tương thích và giữ nhóm tốt | Có giả định và điều kiện giữ được ứng viên đúng qua từng vòng; không phải confidence set có coverage vô điều kiện. Số ứng viên có thể tăng theo hàm mũ | Bài đã làm uncertainty-aware PAG search, cache và parallel construction. Điểm đáng kiểm tra là tránh sinh cấu hình chắc chắn sẽ bị loại, thay vì thêm một beam heuristic nữa |

**Ma trận 2 — công trình gần phải tính vào novelty**

| Công trình; mức đọc | Đã làm gì / đối tượng | Ranh giới quan trọng đối với hướng mới |
|---|---|---|
| [ICD, NeurIPS 2021](https://arxiv.org/abs/2111.04095); M | Discovery có biến ẩn theo vòng, liên kết kích thước tập điều kiện với khoảng cách đồ thị | Anytime refinement đã có. Tính đúng sau một vòng hoàn chỉnh không đồng nghĩa mọi prefix CI là một PAG hoàn chỉnh |
| [FCIT, 2025](https://arxiv.org/abs/2510.04263); M | Kết hợp bước score-based với tìm kiếm CI/path blocking có mục tiêu cho PAG | “Dùng tín hiệu gợi ý để chọn CI triển vọng” đã có dạng mạnh. Cần đối chiếu phạm vi correctness của thuật toán cụ thể |
| [Sequential Causal Discovery with Noisy Language Model Priors — NLPSCM, v2 2026](https://arxiv.org/abs/2506.16234); M | FCI và LLM cập nhật tuần tự; histogram dự đoán edge type tham gia tạo background knowledge | LLM + FCI + prior nhiễu đã có. Đây là đối tượng trực tiếp để kiểm tra vòng phản hồi, chưa phải bằng chứng vòng phản hồi gây hại |
| [AGFN, v4 2026](https://arxiv.org/abs/2309.12032); M | GFlowNet trên ancestral graphs, expert nhiễu, chọn query và cập nhật tri thức | Discovery có biến ẩn với expert/LLM và active querying không còn trống. Bảo đảm phụ thuộc mô hình expert |
| [PRCD-MAP, 2026](https://arxiv.org/abs/2605.01669); M | Trust theo cạnh, truyền thông tin lân cận, prior-weighted regularization; trọng tâm dynamic structure learning | Đã có phân tích prior không đồng nhất và structured/adversarial corruption. “Lỗi prior không i.i.d.” riêng lẻ là gap quá yếu |
| [CauTion, 2026](https://arxiv.org/abs/2606.03602); M | Ensemble tách cạnh đồng thuận và tranh chấp; calibration từ pseudo-label rồi phân xử bằng LLM | Có một giả định chuyển giao độ tin cậy giữa hai tập cạnh cần kiểm tra. Đầu ra DAG; không được đánh đồng với PAG có latent |
| [Causal Ensemble Agent, 2026](https://arxiv.org/abs/2606.10607); S | LLM làm trọng tài để điều chỉnh trọng số các thuật toán khi confidence gần biên quyết định | Ensemble + LLM chỉ xử lý ca khó đã có. Phải đọc sâu hơn nếu chọn hướng B để xác định baseline công bằng |
| [Statistical Causal Prompting, 2024](https://arxiv.org/html/2402.01454v3); M | Đưa kết quả discovery/độ ổn định vào prompt rồi đưa tri thức LLM trở lại discovery | Đồ thị thống kê có thể ảnh hưởng LLM đã được quan sát; hướng A phải đo hậu quả tích lũy và tách nguồn thông tin |
| [CausalFusion, 2026](https://www.amazon.science/publications/causalfusion-integrating-LLMs-and-graph-falsification-for-causal-discovery); M, thuật toán trong PDF | LLM đề xuất DAG, nhận kết quả falsification và sửa graph | Vòng lặp hybrid không mới. Thích hợp kiểm tra tính khái quát của cơ chế A sau khi xác nhận trên phương pháp có latent |
| [Causal Discovery with Language Models as Imperfect Experts, 2023](https://arxiv.org/abs/2307.02390); M, phần phương pháp/thực nghiệm qua PDF | Thu hẹp MEC bằng expert sai, giữ các điều kiện nhất quán và kiểm soát rủi ro theo mô hình expert | Đã đặt vấn đề expert sai và khoảng cách giữa expert giả lập với LLM thực; không được trình bày chúng như phát hiện mới |
| [Causal Order, v2 2025](https://arxiv.org/abs/2310.15117); S | Dùng causal order làm giao diện tri thức, hỏi triplet để giảm nhầm direct/indirect và chu trình | Causal order là thứ tự nhân quả; không phải lịch thực thi CI. Cần phân biệt hai khái niệm khi so novelty |
| [From Causal Plausibility to Causal Reliability, 2026](https://arxiv.org/abs/2608.23660); M | Đánh giá direct-edge prediction và nhiều nguồn confidence; lỗi indirect/reverse, overconfidence | “LLM tự tin nhưng sai” và “nhầm tác động gián tiếp với cạnh trực tiếp” đã được đánh giá. Hướng A/B phải đi đến hậu quả trong pipeline |
| [How PC-based Methods Err, UAI 2026](https://proceedings.mlr.press/v337/faltenbacher26a.html); S | Lỗi cục bộ có thể gây orientation xa; coherency scores phát hiện lỗi không cần CI mới | “Một lỗi có thể lan rộng” không đủ mới. Nếu nghiên cứu vị trí lỗi prior, phải bổ sung cơ chế và thông tin vượt coherency score |
| [Self-Compatibility, AISTATS 2024](https://proceedings.mlr.press/v238/faller24a.html); M | Đánh giá sự tương thích của discovery trên các tập biến chồng lấn mà không có truth | Subset consistency đã có. Consistency là điều kiện cần, không chứng minh đúng |
| [HOLOGRAPH, 2025](https://arxiv.org/abs/2512.24478); M | Local causal beliefs, latent projection và ràng buộc coherence; có active query | Không thể đề xuất “lần đầu xử lý prior dưới phép ẩn biến” mà bỏ qua bài này. Cần kiểm tra giả định linear SEM và phạm vi thực nghiệm nếu đi tiếp |
| [CICheck, 2023](https://arxiv.org/abs/2309.05264); S | Kiểm tra tính nhất quán và suy luận dư thừa từ các CI bằng công cụ logic | Chỉ thêm bộ kiểm tra xung đột CI không đủ mới; liên quan trực tiếp đến baseline cho C |
| [Causal prior knowledge as path-constraints, ICML 2012](https://icml.cc/2012/papers/875.pdf); M | Tích hợp tri thức quan hệ đường đi; tìm kiếm và xử lý không tương thích | Ancestral/path constraints và tìm kiếm có pruning đã có lịch sử dài |
| [COmBINE, JMLR 2015](https://www.jmlr.org/papers/volume16/triantafillou15a/triantafillou15a.pdf); M | Ràng buộc toàn cục từ dữ liệu quan sát/can thiệp có tập biến chồng lấn và latent | Dùng SAT/logic cho causal discovery không phải mới; C cần lợi thế đặc thù cho họ ứng viên dcFCI |
| [Optimal Correction Sets for Argumentative Causal Discovery, 2026](https://spiral.imperial.ac.uk/entities/publication/1313e80e-6de1-4c80-8243-3efceb801e26); S | Sửa tập ràng buộc nhân quả bằng phương pháp logic và tối ưu | “Tìm tập xung đột nhỏ nhất rồi sửa” không nên được xem là gap mở nếu chưa đối chiếu |
| [Optimal Correction Sets for Provable Redress of Contestable Causal Discovery, 23/10/2026](https://arxiv.org/abs/2610.33138); S | Cùng nhóm tác giả; minimum-cost CI-fact repair, mã hóa ASP và bảo đảm cho việc sửa khi bị phản biện | Công trình rất mới, chỉ sàng lọc abstract. Là đối chiếu bắt buộc nếu C phát triển thành cơ chế sửa/xử lý xung đột; không mặc nhiên giải quyết generation cho dcFCI |
| [LLM Cannot Discover Causality…, 2025](https://arxiv.org/abs/2506.00844); S | Lập luận hạn chế LLM vào vai trò hỗ trợ tìm kiếm | Ý tưởng tách gợi ý tìm kiếm khỏi quyết định cấu trúc đã được nêu. Không chấp nhận tiêu đề như một định lý bất khả thi tổng quát |
| [Failing to Falsify, 2026](https://arxiv.org/abs/2604.02485); S | Confirmation bias trong khám phá quy luật, can thiệp bằng yêu cầu phản ví dụ | Hướng A không thể chỉ kết luận LLM có confirmation bias |
| [Agreement Overstates Evidence, 2026](https://arxiv.org/abs/2609.22512); S | Lỗi phụ thuộc giữa LLM judges làm consensus đánh giá quá cao bằng chứng | Hướng A cần phân biệt phụ thuộc giữa các model với phụ thuộc do graph đã chịu ảnh hưởng prior được đưa trở lại prompt |
| [Discovery of Hidden Miscalibration Regimes, 2026](https://arxiv.org/abs/2605.13484); S | Calibration toàn cục che khuất sai lệch theo vùng input; hiệu chỉnh cục bộ | Hướng B không mới ở phát hiện calibration khác nhau giữa nhóm; điểm cần chứng minh là cơ chế chọn nhóm và ảnh hưởng đến quyết định cấu trúc |

**Những hướng nên hạ ưu tiên ngay sau ma trận**

| Ý tưởng nghe hợp lý | Vì sao chưa đủ thành đề tài mạnh | Có thể dùng ở đâu |
|---|---|---|
| LLM đổi thứ tự CI, vẫn giữ kết quả khi chạy hết | Gần Guess2Graph; cần lợi thế riêng của latent discovery và baseline mạnh | Thành phần của phương pháp, hoặc baseline cho nghiên cứu khác |
| Prior sai nên dùng soft weights | Gần RoaDs, PRCD-MAP và các phương pháp trust/deferral | Baseline, không phải claim chính |
| Đánh giá lỗi tương quan theo node/motif | Structured corruption đã được xét; error propagation cũng đã có | Thí nghiệm kiểm soát trong A/B, hoặc nghiên cứu riêng nếu chỉ ra cơ chế mới |
| So hai prior cùng accuracy nhưng gây hại khác nhau | Trực giác đã rõ; có nghiên cứu tác động tri thức và calibration không đồng nhất | Có ích nếu giữ cùng confusion matrix và chứng minh đường truyền qua CI/sepset; chưa đủ mạnh khi đứng một mình |
| Kiểm tra tính nhất quán giữa các tập biến | Self-Compatibility/HOLOGRAPH và causal data integration rất gần | Một phép kiểm tra hoặc baseline |
| dcFCI chỉ phân nhánh khi CI không chắc | Bài và code đã có ngưỡng phân biệt certain/uncertain | Không dùng làm novelty |
| Thêm cache, chạy song song, beam nhỏ hơn | Đã có hoặc là cải tiến triển khai; beam nhỏ có thể đổi đáp án | Baseline engineering; chỉ đủ contribution nếu có kỹ thuật/tính chất mới thực chất |
| Mọi prior sai đều không làm hại ở finite-sample | Quá mạnh khi prior ảnh hưởng tập kiểm định/quyết định; tính nhất quán tiệm cận không suy ra điều này | Thay bằng một claim xác định được giả định, metric và phạm vi |

**Proposal của bạn kia: điều gì làm nó cụ thể, điều gì vẫn phải phản biện**

Tôi không biết lý do thực tế giáo viên khen. Nhận xét dưới đây chỉ dựa trên văn bản. File này đã chứa kết quả, phân tích phụ, audit dữ liệu và mô tả reproducibility; vì vậy không nên so độ chín của nó với một ý tưởng chưa có phép thử.

| Tiêu chí | Proposal kia làm rõ được | Khoảng thiếu trong cách đặt bài toán hiện tại |
|---|---|---|
| Hai lời giải thích cạnh tranh | Điểm đúng đến từ đọc cấu trúc hay từ tên biến/tri thức ngôn ngữ? | “Thứ tự quan trọng” chưa nêu cơ chế cạnh tranh đáng phân biệt |
| Đối tượng được giữ nguyên | Cùng câu hỏi/SCM, đổi tên và graph được cung cấp | Cần cùng graph, data, CI test và ngân sách để xác định lợi ích đến từ đâu |
| Can thiệp cụ thể | Tên gốc/không liên quan/hoán vị/ký hiệu; không graph/graph đúng/graph bị sửa | “Ưu tiên an toàn” chưa chỉ đúng bước thuật toán hoặc đầu vào bị thay |
| Loại trừ lời giải thích khác | Probe đọc đường đi, tên X/Y so với biến thứ ba, câu chuyện mới | Cần tách ưu tiên tốt khỏi lỗi CI, tie-breaking, shrinking candidate set và thay semantics |
| Chấp nhận kết quả âm | Không xác nhận giả thuyết graph đúng bù được mất mát do ẩn tên | Cần tiêu chí dừng khi oracle headroom không chuyển thành lợi ích thực |
| Đóng góp có thể viết thành phát hiện | Mô hình sử dụng nguồn thông tin nào, khi nào sai, benchmark đo gì | Hiện có nhiều tính chất mong muốn hơn một phát hiện hoặc cơ chế thuật toán |

Điểm tốt nhất của proposal là chuỗi **câu hỏi → can thiệp → đối chứng → giải thích cơ chế**. Độ phức tạp của framework không quyết định giá trị khoa học. Một kết quả thực nghiệm hẹp nhưng bác bỏ một cách đánh giá phổ biến có thể có giá trị hơn một framework bao trùm nhiều yêu cầu.

Tuy vậy, proposal không mặc nhiên nổi bật về novelty. [Caliper](https://arxiv.org/abs/2606.04915) đã xét ảnh hưởng của việc thay tên bằng placeholder; [Vernier](https://arxiv.org/abs/2606.15733) tiếp tục nghiên cứu chênh lệch giữa các cách biểu diễn; [NoisyCausal](https://arxiv.org/abs/2605.04313) xét độ bền trước nhiễu trong tác vụ nhân quả. Các bài này được sàng lọc để xác định overlap, không phải được tái lập. Phần có thể tạo khác biệt trong proposal phải nằm ở tương tác tên × graph, cơ chế cụ thể và audit, không chỉ ở thao tác đổi tên.

Các điểm nên hỏi lại tác giả proposal:

1. Nếu prompt khẳng định graph là cấu trúc của thế giới, làm theo graph sai chứng minh hạn chế nào ngoài việc chấp nhận tiền đề? Cần phân biệt “graph là giả thuyết cần kiểm tra” với “graph là giả định được cấp”.
2. Khi sửa graph mà giữ các con số cũ, đề bài còn tương thích nội tại không? Nếu không, kết quả trộn lỗi suy luận với phản ứng trước đề bài mâu thuẫn.
3. Ký hiệu/pseudoword có làm thay tokenization, độ dài và độ dễ nhớ vai trò biến không? Đây có thể là một phần hiệu ứng.
4. Giữ lại kết luận thận trọng khi câu hỏi không cung cấp đủ số để tính functional mới. Proposal đã nhận ra giới hạn này; không nên đẩy thành “LLM không biết dùng adjustment”.
5. Có mã, dữ liệu và preregistration đủ kiểm tra độc lập không? Các con số và tuyên bố tái lập trong file chưa được review này xác minh.

**Ứng viên A — Vòng phản hồi có biến một prior sai thành kết luận ngày càng được tin tưởng không?**

**Câu hỏi ngắn:** Khi LLM đọc lại đồ thị đã bị ảnh hưởng bởi ý kiến trước của chính nó, hệ thống có sửa sai nhờ dữ liệu mới, hay tăng mức tin tưởng vào cùng một lỗi?

**Điểm bám vào phương pháp hiện có.** NLPSCM có chuỗi graph → LLM → histogram/background knowledge → discovery vòng sau; Eq. 4–5 và Algorithm 1 là vị trí cần audit. Tác giả phân biệt cách làm với posterior đầy đủ trên graph. Vì vậy không được gán cho họ một bảo đảm Bayesian mà họ không tuyên bố. [Nguồn phương pháp](https://arxiv.org/html/2506.16234v2).

**Suy luận của review, chưa phải lỗi đã quan sát:** lời khuyên chịu ảnh hưởng bởi graph hiện tại có thể lặp lại một niềm tin cũ. Tần suất đồng thuận cao hơn khi đó mô tả độ ổn định của ý kiến, chưa tự chứng minh độ đúng của cấu trúc. Đáng nghiên cứu là tác động của sự phụ thuộc này lên việc chấp nhận ràng buộc và khả năng sửa graph.

Ví dụ giả định: một quan hệ sai A→B được đưa vào context ban đầu. Vòng sau LLM lại chọn A→B sau khi nhìn graph. Cần phân biệt ba nguyên nhân: LLM có tri thức độc lập ủng hộ nó; graph trong prompt làm thay đổi câu trả lời; hoặc thuật toán giữ một hard constraint vốn không thể rút lại. Chỉ nguyên nhân thứ hai kết hợp với cách tích lũy độ tin cậy mới là cơ chế trọng tâm của hướng này.

**Làm cụ thể thế nào:**

1. Tái lập đúng một pipeline sequential có FCI và xác định trong code: ai cập nhật context, ai tăng trọng số/đếm phiếu, khi nào prior được chấp nhận, có rút lại được không. Chưa sửa pipeline khi chưa tái lập được baseline.
2. Tạo cặp chạy cùng SCM, cùng mẫu và cùng chuỗi batch. Can thiệp tối thiểu vào một lời khuyên ban đầu: đúng, sai, hoặc abstain. Đối với LLM thực, dùng mô tả biến có nghĩa; graph truth phải được xác định độc lập với câu trả lời LLM.
3. So bốn điều kiện bên dưới, giữ tổng mẫu quan sát và ngân sách query được báo cáo rõ. Nhánh không có dữ liệu mới là diagnostic ngoài deployment, không dùng riêng nó để kết luận phương pháp gốc thất bại.
4. Thêm đối chứng “prior cố định từ đầu” với độ chính xác ban đầu tương đương; thêm replay câu trả lời cũ để kiểm tra tác động cơ học của đếm lặp. Replay không được gọi là các đánh giá expert độc lập.
5. Nếu tìm thấy hiệu ứng, thử hai thay đổi nhỏ: cố định context khi ước lượng độ tin cậy của prior; hoặc để graph-conditioned LLM đề xuất kiểm định nhưng không tăng trọng số prior chỉ vì nó đồng ý lại. Đây là ablation để xác định cơ chế trước khi gọi là phương pháp mới.

| | LLM chỉ thấy metadata/context cố định | LLM thấy graph đang cập nhật |
|---|---|---|
| Không thêm mẫu quan sát | Đo biến động sampling của ý kiến | Đo ảnh hưởng riêng của feedback graph |
| Có batch dữ liệu mới, giống nhau giữa các nhánh | Đo lợi ích của dữ liệu mới với nguồn prior cố định | Đo tương tác giữa dữ liệu mới và vòng phản hồi |

**Biến chính nên đo:** tỷ lệ ràng buộc sai được chấp nhận; số vòng cần để rút/sửa một ràng buộc sai khi có bằng chứng phản bác; sai endpoint/ancestry và chất lượng graph cuối tại cùng ngân sách. Histogram entropy, số phiếu và độ tự tin là biến giải thích, không phải thước đo đúng-sai chính.

**Đối chứng bắt buộc:** FCI không prior; một-shot prior; prior cố định có chất lượng tương đương; pipeline gốc; hai ablation trên. Phân tầng quan hệ có thể phân biệt từ dữ liệu và quan hệ nằm trong cùng observational equivalence class. Không trách một phương pháp vì không suy ra được hướng không định danh từ dữ liệu quan sát. Không tính một orientation đúng do tri thức ngoài cung cấp là sai chỉ vì PAG không-prior còn dấu tròn.

**Sản phẩm khoa học nếu thành công:** một nghiên cứu chỉ ra khi nào tăng confidence phản ánh thông tin mới, khi nào phản ánh tái sử dụng context; một phép kiểm tra paired có thể dùng cho nhiều pipeline; và một quy tắc cập nhật giảm lỗi mà vẫn giữ lợi ích của prior đúng. Với latent discovery, cần đánh giá bằng MAG/PAG phù hợp, không chỉ SHD của DAG.

**Novelty phải vượt:** SCP đã cho thấy prompt thống kê ảnh hưởng LLM; nghiên cứu confirmation bias và judge dependence đã tồn tại. Đóng góp phải là cơ chế khép kín trong structural discovery, hậu quả đối với ràng buộc/khả năng sửa sai, và phép can thiệp phân biệt được các nguyên nhân. Nếu chỉ thấy “đưa graph sai thì LLM trả lời sai”, kết quả quá gần proposal kia và tài liệu hiện có.

**Điều kiện dừng:** hiệu ứng biến mất sau khi cân bằng chất lượng prior ban đầu; chỉ do hard constraint không được rút lại; chỉ xuất hiện ở nhánh không dữ liệu mới; chỉ có entropy giảm mà graph không xấu đi; hoặc baseline một-shot giải thích toàn bộ khác biệt. Khi đó không nên xây thêm framework để cứu hướng.

**Khả thi:** phù hợp nhất để kiểm tra đầu tiên về mặt nội dung vì có biến ẩn và câu hỏi cơ chế rõ. Cần adapter cho phương pháp khác và ngân sách LLM được thống nhất sau; repo hiện tại chưa có bằng chứng để khẳng định hiện tượng.

**Ứng viên B — Calibration trên cạnh đồng thuận có dự đoán được độ tin cậy ở cạnh tranh chấp?**

**Câu hỏi ngắn:** Nếu kiểm tra LLM trên những cạnh các thuật toán đã đồng ý, có thể dùng điểm đó để quyết định tin LLM ở những cạnh mà các thuật toán đang bất đồng hay không?

**Điểm bám:** CauTion §3.3.2 chuyển ước lượng độ đúng từ consensus sang disputed pairs, với giả định tri thức LLM phân bố tương đương; có reweighting theo lớp existence/direction. Cần kiểm tra sai lệch còn lại bên trong từng lớp. [Nguồn phương pháp](https://arxiv.org/html/2606.03602v1).

**Suy luận của review:** cùng domain và tập biến chưa đủ suy ra hai phân phối độ khó giống nhau. Quy tắc chọn disputed pairs có thể làm tập cần trợ giúp tập trung vào quan hệ gián tiếp, hướng khó, hoặc cơ chế mà cả dữ liệu và LLM đều yếu. Reweighting theo tỷ lệ có/không cạnh không tự loại hết khác biệt này. Đây là khả năng cần kiểm tra, không phải kết luận thực nghiệm về CauTion.

Ví dụ minh họa, không phải số liệu: hai LLM cùng đúng 95% ở tập consensus; một model đúng 80%, model kia đúng 50% ở tập disputed. Một trust score chung từ tập đầu không phân biệt được hai trường hợp. Câu hỏi có giá trị là hiện tượng có xảy ra có hệ thống trong discovery thực và làm thay đổi quyết định kết hợp nguồn hay không.

**Làm cụ thể thế nào:**

1. Tái lập ensemble và quy tắc tách hai tập trong đúng setting của baseline. Bắt đầu trong giả định DAG của baseline; không chứng minh “baseline sai” bằng cách áp latent confounding mà nó không tuyên bố xử lý.
2. Trên graph có truth dùng cho đánh giá, đo độ đúng của consensus pseudo-label và độ đúng của LLM riêng biệt. Tách sai số do pseudo-label sai khỏi sai số chuyển giao sang tập disputed.
3. Giữ cùng domain/model/query policy; so chênh lệch sau khi cân bằng loại cạnh, độ dài đường đi, bậc nút và các thước đo độ khó có thể quan sát. Đặc trưng truth chỉ dùng chẩn đoán không được lén đưa vào phương pháp triển khai.
4. Đo trust-ranking reversal: model/nguồn được đánh giá tốt hơn trên calibration có lại kém hơn chính tại nơi thuật toán chọn sử dụng nó không? Theo dõi tác động đến output graph, không chỉ ECE.
5. So global trust với class-weighted trust hiện có, calibration theo nhóm/importance weighting thông thường, và một mức oracle dùng nhãn disputed chỉ để đo giới hạn. Nếu có kiểm định hiệu chỉnh mới, cần train/test theo graph/domain, không chia ngẫu nhiên các cạnh phụ thuộc của cùng graph.

**Một phương pháp cụ thể để thử nếu có gap:** chỉ sử dụng ước lượng tin cậy trong vùng đặc trưng mà tập calibration bao phủ; ngoài vùng đó abstain hoặc giữ cạnh chưa định hướng. Trong vùng có coverage, ước lượng trust theo nhóm và kiểm tra trên graph/domain chưa thấy. Đây là ứng dụng của calibration/transfer có điều kiện, chưa đủ để gọi thuật toán mới. Muốn đóng góp thuật toán cần thêm điều kiện hoặc một quy tắc phù hợp cấu trúc graph mà baseline tổng quát không có.

**Giới hạn nhận diện:** nếu không có nhãn đáng tin trên ca khó và không có giả định nối hai tập, không thể suy ra độ đúng của LLM ở ca khó chỉ từ điểm trên ca dễ. Nếu thuật toán vẫn sinh một con số confidence, con số đó cần được gọi là heuristic. Một phản ví dụ xác lập điều này dễ xây và chỉ là nền tảng, không phải toàn bộ paper.

**Sản phẩm khoa học nếu thành công:** chỉ ra một sự đảo ngược đáng kể của quyết định chọn nguồn do cách chọn tập calibration; xác định khi nào sửa bằng cân bằng lớp là đủ, khi nào cần coverage/abstention; đưa ra đánh giá end-to-end. Có thể mở rộng sang PAG sau, nhưng phải thiết kế lại nhãn quan hệ và biểu diễn bất định.

**Điều kiện dừng:** chỉ thấy selection bias quen thuộc không có hậu quả đáng kể ở graph; khác biệt do class imbalance và baseline đã giải quyết; một calibration tổng quát đã xử lý hết; hoặc không có nhiều phương pháp/miền để chứng minh đây là vấn đề vượt một implementation.

**Khả thi:** thí nghiệm đầu khá rõ và rẻ hơn A nếu có sẵn đáp án LLM. Nhưng xa trọng tâm latent hơn A/C, và novelty thuật toán yếu nếu chỉ thêm isotonic regression hoặc một bộ phân loại trust.

**Ứng viên C — Thay bước sinh tất cả tổ hợp của dcFCI bằng sinh trực tiếp cấu hình hợp lệ**

**Câu hỏi ngắn:** Có thể tránh dựng hàng loạt cấu hình separating sets cuối cùng bị loại, nhưng vẫn giữ nguyên họ ứng viên hợp lệ và kết quả lựa chọn của dcFCI không?

**Điểm bám đã kiểm tra trong code:** tại commit `a27c495acc28810a1e8e95878d535d90f82faaaf`, `R/dcFCI.R` dòng 367–429 gọi `powerSet`, sau đó lọc các tập có nhiều lựa chọn cho cùng cặp. Các bước dựng PAG và kiểm tra tiếp diễn ra sau. Code cũng đã tách certain/uncertain và dùng parallel processing. [Mã nguồn cố định theo commit](https://github.com/adele/dcFCI/blob/a27c495acc28810a1e8e95878d535d90f82faaaf/R/dcFCI.R#L367).

Đây là bottleneck về cấu trúc tính toán có thể chỉ ra bằng code. Chưa có profiling trong review này, nên chưa biết nó chiếm bao nhiêu thời gian end-to-end hoặc xuất hiện ở bao nhiêu graph thực tế.

**Bước đầu thực hiện được ngay về mặt ý tưởng:** sau khi xử lý các lựa chọn certain theo semantics gốc, gom separating sets còn lại theo cặp biến. Mỗi cặp chọn “không xóa cạnh” hoặc một separating set trong nhóm. Nếu nhóm e có s_e lựa chọn, sinh trực tiếp tích các miền có kích thước 1+s_e, thay cho sinh 2^(tổng s_e) rồi bỏ các cấu hình chọn trùng cặp.

Ví dụ minh họa: 10 cặp, mỗi cặp có hai separating sets khả dĩ → 2^20 = 1.048.576 tập con ban đầu so với 3^10 = 59.049 cấu hình thỏa điều kiện một lựa chọn mỗi cặp. Đây chỉ là phép đếm cấu hình, **không phải speedup đo được**, và chỉ đúng cho phần sinh ứng viên với assumptions vừa nêu.

Tuy nhiên, thay power set bằng Cartesian product là cải tiến hiển nhiên. Một paper mạnh cần đi xa hơn: phát hiện sớm các nhóm lựa chọn không thể cùng mở rộng thành PAG hợp lệ và tránh mọi nhánh chứa nhóm đó. Muốn làm được phải có quy tắc loại nhánh đúng đối với **mọi completion còn lại**, chứ không chỉ nhìn một partial orientation có vẻ xung đột.

**Làm cụ thể thế nào:**

1. Cố định phiên bản, các ngưỡng, cách tie-break, giới hạn danh sách và tập CI trả lời. Profile riêng sinh tổ hợp, dựng PAG, kiểm tra validity, suy luận CI bổ sung, tính score và chọn ứng viên.
2. Xây baseline sinh trực tiếp theo cặp như trên. Baseline này bắt buộc để không lấy một tối ưu elementary làm contribution.
3. Phân loại các lý do candidate bị loại. Tìm một lớp mâu thuẫn mà có thể chứng minh tồn tại bất kể các lựa chọn chưa gán; trước khi có lemma này không gọi pruning là exact.
4. Thiết kế backtracking với domain theo cặp và conflict constraints vừa chứng minh. Chỉ memoize/nogood khi nó áp dụng cho mọi completion của trạng thái đó. Các lựa chọn còn lại phải được xét đầy đủ.
5. So với code gốc, baseline theo cặp và solver ràng buộc tổng quát phù hợp. Giữ nguyên tiêu chuẩn chấm điểm và kiểm tra độc lập danh sách candidate trên graph nhỏ.

**Điểm khó thật sự:** các cạnh bị xóa sau có thể thay đổi triple, đường đi và orientation. Một “xung đột” ở graph trung gian không tự động là xung đột vĩnh viễn. Ngoài ra, score dcFCI dùng thông tin so sánh giữa các ứng viên; không được giả sử score trên một phần danh sách là upper bound cho score cuối. Vì vậy, phiên bản đầu nên chỉ bỏ cấu hình được chứng minh là không hợp lệ và chấm điểm trên cùng họ hợp lệ, chưa prune theo score chưa hoàn chỉnh.

**Đóng góp cần có:** lemma đủ mạnh về loại bỏ cấu hình, thuật toán tận dụng lemma, và lợi ích end-to-end trên một lớp graph có đặc trưng xác định được. Claim mục tiêu là tương đương phiên bản dcFCI đã cố định, không phải đúng với causal truth mọi finite sample, cũng không phải tìm mọi MAG có thể tồn tại.

**Đo gì:** số cấu hình được xét/dựng/loại; số candidate hợp lệ; số CI thực hiện; thời gian và RAM; sự trùng khớp candidate cuối/score/tập top-k có xử lý ties. Plot chi phí theo số lựa chọn uncertain và số nhóm xung đột, không chỉ theo số node.

**Điều kiện dừng:** profiling cho thấy chi phí nằm chủ yếu ở CI chứ không ở generation/validity; hầu hết mỗi cặp chỉ có một lựa chọn nên baseline đơn giản không giúp; không có quy tắc pruning đủ mạnh; solver chung làm tốt tương đương; hoặc lợi ích chỉ đến từ thu nhỏ họ candidate/đổi score.

**Khả thi:** đây là lựa chọn rõ nhất nếu muốn làm thuật toán cho latent discovery. Rủi ro cao hơn A/B vì có thể chỉ thu được một cải tiến engineering. Hạ tầng Python hiện tại cũng không tái sử dụng nguyên trạng được với implementation R; không nên lờ chi phí tích hợp này.

**Ma trận quyết định để thảo luận**

| Ứng viên | Thứ sẽ thực sự làm | Giá trị nếu kết quả dương | Phép thử đầu tiên đủ để quyết định đi tiếp | Rủi ro lớn nhất | Đề nghị hiện tại |
|---|---|---|---|---|---|
| A — Feedback và prior sai | Can thiệp context và cách tích lũy độ tin cậy trong một pipeline sequential; đo sai constraint và khả năng sửa | Giải thích một cơ chế sai có thể ảnh hưởng nhiều hệ thống hybrid; dẫn đến thiết kế cập nhật tốt hơn | Baseline tái lập + thiết kế 2×2 + đối chứng one-shot, cùng mẫu và query budget | Kết quả chỉ là confirmation bias/hard constraints quen thuộc | Ưu tiên review câu hỏi khoa học |
| B — Calibration từ consensus sang disputed | Đo và tách pseudo-label noise, selection shift, trust-ranking reversal; kiểm tra calibration theo coverage | Thay đổi cách đánh giá và chọn nguồn tri thức trong discovery | Độ đúng trên hai tập và tác động graph, sau cân bằng lớp | Áp dụng lại calibration tổng quát, xa latent | Dự phòng; cần novelty audit sâu hơn |
| C — Sinh candidate dcFCI | Profile; baseline theo cặp; tìm lemma để loại sớm cấu hình không thể hợp lệ | Thuật toán nhanh hơn mà giữ nguyên bài toán mục tiêu | Profile + tần suất/mẫu xung đột + một lemma hoặc phản ví dụ chống lemma | Chỉ sửa cách triển khai, không có contribution thuật toán | Ưu tiên nếu muốn thuật toán thuần |

**Cách đánh giá một pilot sau khi thống nhất hướng**

Các thiết kế dưới đây là đề xuất, chưa được chạy và không phải kế hoạch tự động thực thi:

- Chọn một claim chính và một metric chính; xác định trước mức hiệu ứng có ý nghĩa với ứng dụng/ngân sách, không lựa ngưỡng sau khi thấy số.
- Tách bộ graph khám phá khỏi bộ xác nhận. Dùng paired seeds/data; bootstrap hoặc phân tích theo graph/domain, không coi mọi cạnh hoặc query là mẫu độc lập.
- Với A/B, dùng expert giả lập để kiểm tra khả năng phân biệt cơ chế rồi kiểm tra trên LLM thực. Kết quả giả lập không tự chứng minh hiện tượng ở LLM.
- Với latent, dùng ground-truth latent projection độc lập và các metric phù hợp PAG/MAG; dependency đang thiếu ở repo cần được giải quyết trước khi claim correctness.
- Nếu chỉ có một dataset tham chiếu không chắc về causal truth, ghi rõ đang đánh giá so với reference graph. Không gọi disagreement với reference là bằng chứng thế giới thực chắc chắn sai.
- Trước khi claim thuật toán mới, phải vượt baseline đơn giản nhất có cùng thay đổi thông tin: one-shot/fixed-context cho A, calibration theo nhóm cho B, direct per-pair enumeration cho C.

**Các kết luận tôi đề nghị mang ra thảo luận**

1. Câu hỏi của giáo viên về độ tự nhiên của hướng cũ có cơ sở. Cần thay đổi claim hoặc cơ chế nghiên cứu, không chỉ đặt tên lại.
2. Không cần bắt đầu bằng một framework lớn. Hãy bắt đầu bằng một sự khác biệt mà tài liệu hiện tại chưa giải thích hoặc một bottleneck có thể chứng minh cách loại bỏ.
3. A đáng xem xét nhất nếu chấp nhận nghiên cứu thực nghiệm có cơ chế. C đáng xem xét nhất nếu muốn một cải tiến thuật toán rõ ràng và giữ trọng tâm biến ẩn. B hữu ích nhưng nên xếp sau vì novelty tổng quát dễ yếu.
4. Chưa nên cam kết hướng nào có “scientific contribution cao” trước các phép thử quyết định ở trên. Điều có thể cam kết lúc này là mỗi ứng viên đã có đối tượng, thao tác, đối chứng và điều kiện bỏ hướng cụ thể.

Review này chỉ bổ sung tài liệu để quyết định. Không thay đổi research contract, thuật toán, trạng thái gate hoặc kết quả của repo.
