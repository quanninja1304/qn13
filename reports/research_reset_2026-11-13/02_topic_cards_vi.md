# Topic cards — bốn câu hỏi nghiên cứu để review

Ngày 13/11/2026. Tất cả: **Hypothesis; pilot NOT RUN**. Mã nguồn tài liệu P01–P24 và URL nằm trong [evidence matrix](01_evidence_matrix_vi.md). Các đề xuất thiết kế/cơ chế dưới đây là suy luận của audit, không phải kết quả của bài được trích.

## N1. Khi các cột không liên quan làm đổi kết luận nhân quả

### Câu hỏi một câu

**Với dữ liệu của một causal module giữ nguyên, các mô hình amortized causal discovery có dùng đặc trưng của một module độc lập để quyết định hướng cạnh trong module đích không; khi nào việc đó là chuyển thông tin hợp lệ, khi nào là áp giả định sai?**

### Problem và significance

Một bảng có thể ghép nhiều nhóm biến: nhóm xét nghiệm, nhóm hành vi, nhóm thiết bị; không có lý do mặc định rằng tất cả cùng có noise family hoặc mức phi tuyến. Mô hình nhận cả bảng có thể dựa vào đặc trưng toàn cục để chọn cách suy luận trong từng phần. Nếu vậy, chất lượng ở một benchmark đồng nhất không mô tả được việc dùng nó trên bảng có nhiều cơ chế.

Ví dụ minh họa: A và B là hai sensor của một hệ. C–F đến từ hệ khác, được lấy độc lập. Dữ liệu A/B không đổi. Chỉ thay C–F từ hệ tuyến tính sang phi tuyến, mô hình có đổi score A → B hay không? Đây là **can thiệp vào input của thuật toán**, không phải can thiệp vật lý lên A hoặc B.

### Giao hai hiệu ứng và prior art gần nhất

| Nguồn | Đã biết | Điều câu hỏi mới phải vượt qua |
|---|---|---|
| P02 AVICI; P04 TabCausal | Simulator tạo prior; attention trao đổi thông tin giữa các biến | Không claim việc có prior hoặc attention là mới |
| P03 Demystifying, TMLR 2025 | Training distribution chứa giả định identifiability; phân tích CSIvA bivariate | Không lặp lại “mô hình vẫn cần giả định”; phải xác định **nguồn** dữ liệu nào làm model chọn giả định |
| P07 Self-Compatibility; P08 Marginal consistency | So output giữa tập biến đã là cách kiểm tra causal discovery | Chỉ phát hiện output đổi khi đổi cột là chưa đủ; phải tách context cơ chế khỏi thay đổi target và dimensionality |
| P05 CausalArena; P06 R²-sortability | Đổi simulator có thể đổi kết quả; standardization không loại mọi shortcut | Giữ nguyên khối đích để tránh đổi đồng thời độ khó, graph và local statistics |

**Gap có thể bảo vệ [Hypothesis]:** trong các nguồn đã rà, chưa thấy thiết kế hoán đổi module độc lập, cùng kích thước, giữ nguyên local data, để phân biệt chuyển giả định toàn cục hợp lệ với việc chuyển sai giữa các module. Đây là kết luận tìm kiếm có giới hạn, không tuyên bố “đầu tiên”.

### Insight và cơ chế cần kiểm tra

Giả sử H biểu thị họ cơ chế dùng chung trong một simulator. Một bộ suy luận Bayes lý tưởng có thể tính:

`P(G_A | D_A, D_B) = Σ_h P(G_A | D_A, h) P(h | D_A, D_B)`.

Dù hai hệ độc lập có điều kiện trên H, D_B vẫn giúp học H và đổi suy luận về G_A. **Độc lập giữa các biến trong một hệ cố định không đồng nghĩa độc lập giữa các bài toán trong training prior.** Đây là lý giải Bayes quen thuộc, không phải định lý mới.

Nếu triển khai trên các module có `H_A ⟂ H_B`, đồng thời graph/mechanism prior của hai module phân rã độc lập và không có selection hay ràng buộc chung, thì Bayes lý tưởng cho lớp đó thỏa:

`P(G_A | D_A, D_B) = P(G_A | D_A)`.

Khoảng cách giữa hai chế độ này là đối tượng nghiên cứu. **Không gọi mọi ảnh hưởng của context là lỗi.** Khi các module thực sự chia sẻ prior, context có thể là thông tin hợp lệ và cải thiện kết quả. Cũng chưa có bằng chứng checkpoint cụ thể đã học H theo cách này; đó là hypothesis.

### Thiết kế tách các giải thích

**Đơn vị lặp:** SCM đích A; nhiều context B cho cùng A là phép đo lặp, không phải SCM độc lập.

1. Sinh và lưu cố định D_A với seed tách khỏi D_B. A là module 3–5 biến, có DAG truth và cả chế độ hướng dễ/khó xác định.
2. Tạo B độc lập A, cùng số cột và số dòng giữa các nhánh; B có thể có liên hệ nội bộ nhưng không có cạnh/chung nguyên nhân với A.
3. So B cùng family, B khác family và B noise control. Ghép theo hàng chỉ là ghép các sample độc lập.
4. Cross với hai chế độ tạo dữ liệu: family chung giữa module và family được chọn độc lập. Các lần thay context trong chế độ chung phải được gắn nhãn là stress test ra ngoài prior, không giả làm một mẫu cùng distribution.
5. Giữ D_A sau preprocessing giống nhau **từng bit**; tách thí nghiệm p thay đổi khỏi thí nghiệm context thay đổi cùng p.
6. Chỉ xét giai đoạn đầu causal sufficiency, iid, acyclic. Chưa đưa latent, selection, time series vào để tránh thêm nguồn lỗi.

| Giải thích cạnh tranh | Đối chứng phân biệt |
|---|---|
| B làm đổi normalization toàn bảng | Tiền xử lý từng cột, đóng băng tham số A; so input thực vào network |
| Chỉ do số cột lớn hơn | Thay B ở **cùng p**, thêm một nhánh p riêng |
| Do attention đông hơn, không liên quan loại cơ chế | B cùng số tokens và scale; đổi riêng đặc trưng cơ chế/noise; family-neutral control |
| Do sample correlation ngẫu nhiên A–B | Nhiều seed B độc lập, tăng n, paired permutation controls; không ép orthogonal mẫu rồi gọi đó là độc lập |
| Do decoder cycle-pruning toàn graph | Đo raw logits/scores trước decoder và graph sau decoder riêng |
| Do model ngẫu nhiên | Eval mode, lặp cùng input, ghi tolerance số học |
| Do prior chung là đúng | Positive control simulator có H chung; so với simulator module độc lập |
| Chỉ xảy ra ở task không thể định hướng | Thêm nonlinear/non-Gaussian identifiable và interventional strata; không đòi hướng đúng ở Gaussian MEC mơ hồ |

### Baselines và evaluation

- **Hai mô hình học sẵn:** AVICI và TabCausal; đã xác minh repo/checkpoint công khai, **chưa chạy**. Hai mô hình có kiến trúc gần nhau, vì vậy không đủ để kết luận mọi foundation model đều thế. Nếu tín hiệu còn, thêm family khác như CSIvA/SEA sau audit checkpoint.
- **Phương pháp cổ điển:** PC với CI phù hợp; GES; DirectLiNGAM ở stratum tuyến tính non-Gaussian. Không cho phương pháp thắng/thua vì bị ép dùng ngoài giả định mà không ghi rõ.
- **Đối chứng đơn giản:** inference chỉ trên A; chạy theo partition A/B **biết từ thiết kế**; random/permuted context cùng kích thước. Partition biết trước là diagnostic oracle, không phải thuật toán deployable miễn phí.
- **Prior-control:** posterior của simulator nhỏ với prior chung vs prior phân rã, nếu tính được; minh họa ranh giới “context có ích” và “context gây hại”.

Metrics chính: paired change trong hướng/edge score nội bộ A, flip rate, độ chính xác khi hướng identifiable, Brier/log loss ở simulator có label hợp lệ; ở non-identifiable stratum chỉ kiểm độ nhạy/overcommitment theo prior được chỉ rõ. Không gọi output sigmoid là calibrated confidence nếu chưa kiểm. SHD/F1 toàn bảng chỉ là phụ.

Nguồn dữ liệu: generators chính thức AVICI/TabCausal, SCM của CausalArena, generator độc lập do nhóm khác; phối hợp module là **benchmark adaptation mới**, không giả làm protocol gốc. Causal Chambers có thể cung cấp D_A vật lý rồi ghép B độc lập để kiểm stability; đây là semi-real stress test, không phải một hệ vật lý kết hợp thật. Chưa tải benchmark mới trong lượt này.

### Minimal falsification pilot — đề xuất, chưa khóa

Khám phá: 20–30 SCM đích, p nhỏ, hai mức n và ba B mỗi family; dùng fixed checkpoint, không train. Trước chạy phải chốt model size/runtime bằng smoke test và ghi ngân sách. Xác nhận: SCM mới và context mới, cluster bootstrap theo A, giữ một generator family ngoài giai đoạn khám phá.

**Positive:** thay đổi phụ thuộc family context, vượt numerical/permutation controls, xuất hiện trên dữ liệu mới; phần tác hại tập trung ở modular mismatch và giảm khi local identifying evidence mạnh. Hướng của dự đoán cuối có thể cần đăng ký sau exploratory, không chọn hậu nghiệm rồi gọi confirmatory.

**No-go cho framing cơ chế:** hiệu ứng biến mất khi sửa preprocessing, chỉ có ở p thay đổi, hoặc không phân biệt được với một hiệu ứng kích thước/numerics chung. Nếu chỉ một checkpoint gặp, chỉ kết luận về checkpoint đó. Nếu interval hẹp quanh 0 sau một pilot đủ power: ghi giới hạn, không tiếp tục phát minh repair.

### Method nếu insight được xác nhận

Đầu tiên là **protocol đo chuyển thông tin giữa module**, không cần thuật toán mới. Chỉ sau đó mới xét component-conditioned inference hoặc training với module priors độc lập. Cả partitioning và data augmentation đều là kỹ thuật quen thuộc; chỉ có thể thành phần phương pháp nếu chứng minh cơ chế cần xử lý và đánh đổi: chặn chuyển sai mà vẫn giữ lợi từ chia sẻ đúng. Không xây “module gate” trước pilot.

### Research survivability

- **Tối thiểu:** phép tách nguồn thông tin + ranh giới context hữu ích/có hại, xác nhận nhiều family, đủ quan trọng; không hứa bài chỉ từ một biểu đồ flip rate.
- **Mạnh:** nguồn lỗi cụ thể trong training distribution/decoder, sửa bằng thay đổi tối thiểu và kiểm ngoại suy.
- **Mở rộng:** học khi nào được chia sẻ giả định giữa module, cần bài toán và bằng chứng riêng.
- **Quyết định:** **Conditional, ưu tiên kiểm tra**, không phải GO xây framework.

## N2. Đánh giá hậu quả của graph mà không đánh đồng sai với chưa biết

### Câu hỏi một câu

**Sau khi giữ tương đương phạm vi câu hỏi mà phương pháp trả lời, loại lỗi cấu trúc nào thực sự tạo công thức hiệu ứng sai, và phần tiến bộ nào chỉ là trả lời nhiều hơn hoặc bớt bảo thủ?**

### Problem, gap và prior art

SHD đếm lỗi graph, còn người dùng muốn biết can thiệp có tác dụng thế nào. Dưới latent, một PAG đúng vẫn có quan hệ chưa rõ. Vì thế phải đánh giá cả chất lượng quyết định và giới hạn thông tin.

| Nguồn | Đã giải quyết | Ranh giới của N2 |
|---|---|---|
| P09 AID | Strategy-specific identification distances, kể cả CPDAG | Không claim metric downstream mới nói chung; phải giữ graph class/target |
| P10 GAC | Adjustment criterion cho DAG/CPDAG/MAG/PAG | Công cụ nền, không phải novelty |
| P11 SD | Separation-based distances cho graph/MEC có latent | Cần baseline trực tiếp, không chỉ SHD |
| P12 FID | Estimand distance cho ADMG, perturbation analysis | Khoảng cách một graph không đồng nghĩa đánh giá abstention của một MEC |
| P13 PAGcauses | Các hiệu ứng khả dĩ qua adjustment | Tập hiệu ứng khả dĩ không phải confidence interval; không suy diễn coverage thống kê |
| P14 FCIT | Strong hybrid baselines cho PAG | Cần đánh giá trên output hợp lệ, không dùng FCI làm đối thủ duy nhất |

**Gap còn lại [Hypothesis]:** tác động của *loại lỗi × khả năng trả lời của oracle cùng thông tin* lên downstream error, khi so phương pháp có mức khẳng định khác nhau. Novelty phải nằm ở giải thích có khả năng tổng quát; “thêm PAG vào AID” chỉ là khả năng công cụ.

### Insight và định nghĩa nhiệm vụ

Chốt tập câu hỏi Q={(X,Y)} trên biến quan sát trước khi chạy. Cho mỗi query, một strategy cố định trả `adjust(Z)`, `zero` hoặc `abstain`. `abstain` chỉ nghĩa **strategy không cung cấp câu trả lời**, không tự là tuyên bố “không thể định danh bằng bất kỳ phương pháp nào”.

Hai chuẩn khác nhau:

- `D*`: DAG sinh dữ liệu gồm latent, dùng kiểm công thức có hợp lệ với hệ thật không; Z chỉ gồm biến quan sát.
- `P*`: oracle PAG với cùng tập quan sát và giả định, dùng xác định những query có thể trả lời theo strategy đã chốt.

Đếm riêng wrong claims, valid claims, missed oracle-answerable queries, correct abstentions và extra assumptions. Việc một graph đoán sai vô tình đề xuất công thức đúng ở D* nhưng P* không đủ thông tin phải được ghi riêng; không biến nó thành bằng chứng học đúng cấu trúc.

**Cơ chế [Hypothesis]:** một số lỗi không chỉ tăng endpoint distance mà đổi khả năng chặn đường gây nhiễu, tính visible của cạnh, hoặc tập biến bị cấm điều chỉnh. Hậu quả phụ thuộc vào query. Dấu tròn có thể làm mất câu trả lời mà không tạo câu trả lời sai. Không được mặc định mọi mũi tên/đuôi sai đều thuộc một loại tác hại duy nhất.

### Đòn bẩy và nghĩa vụ toán

Pilot graph-oracle dùng D* và D' hợp lệ, thay đổi cấu trúc có kiểm soát, rồi suy ra PAG tương ứng bằng quy trình đã kiểm chéo. **Không tùy tiện đổi một endpoint rồi coi output là PAG hợp lệ.** Một thay đổi DAG có thể đổi nhiều dấu PAG; phải ghi cả hai liều, không gọi là cùng “một lỗi”.

So tác hại trước/sau trong cùng Q và D*, phân tầng loại thay đổi, query answerability và quy mô ảnh hưởng. Bên cạnh đó chạy discovery thực trên cùng sample để xem loại lỗi đó có đủ phổ biến không. Không chỉ chọn motif thuận lợi.

Nghĩa vụ: (i) verifier `adjust(Z)` đúng trong D*; (ii) oracle P* không bị tính wrong claim; (iii) không có query trả lời thì risk là **NA**, không phải 0; (iv) không lẫn MAG với ADMG; (v) general adjustment completeness không phải completeness của mọi do-calculus strategy. Kiểm graph nhỏ bằng enumeration/implementation độc lập. Không yêu cầu metric thỏa triangle inequality.

### Baselines, dữ liệu, metrics

- Discovery: FCI, RFCI, GFCI/BOSS-FCI; FCIT nếu implementation tái lập được. Giữ CI family, dữ liệu, tuning budget và timeout tương đương; native PAG không chuyển tùy tiện sang DAG.
- Metric: SHD/endpoint precision–recall, SD, AID trên stratum phù hợp, FID trên ADMG khi đúng task, ba nhóm claim/coverage theo strategy cố định.
- Simple baselines: always-abstain; oracle PAG; policy chỉ trả query mà bootstrap strategy đồng ý; random downsampling claims chỉ làm diagnostic về số lượng, không là fairness guarantee.
- Mô phỏng: dùng generator công bố FCIT và graph bnlearn đã có, thêm generator độc lập, nhiều mức latent/sparsity. Ghi rõ graph bnlearn + SEM là semi-synthetic.
- Thật: Chambers chỉ trên estimand/intervention được datasheet hỗ trợ; Sachs và gene screens không có full DAG truth nên không chấm mọi cạnh như oracle.

Risk phải đi kèm coverage; matched coverage chưa đủ nếu hai thuật toán chọn các query khác độ khó. Cần common-query analysis và phân tầng theo oracle answerability/strength. Không chọn ngưỡng bằng ground truth test; không ép hệ không có score phải có cả đường cong giả tạo.

### Pilot và quyết định

Khởi đầu 20–30 graph nhỏ và tất cả ordered query, chỉ kiểm semantics; sau đó một lưới finite-sample độc lập nhỏ. Một đảo thứ hạng không phải gate duy nhất. Cần kiểm rằng cơ chế graph-query dự đoán downstream harm trên graph families chưa dùng tìm cơ chế, vượt dự đoán từ edge count/coverage.

**No-go:** khác biệt hết khi kiểm coverage và query mix; baseline AID/FID/SD đã giải thích đủ; hoặc evaluator mới chủ yếu phạt oracle abstention. Không tuyên bố metric cấu trúc “đủ tốt nói chung” từ một kết quả âm trên lưới nhỏ.

**Tối thiểu:** decomposition có nghĩa và phát hiện được xác nhận, không chỉ leaderboard. **Mạnh:** protocol đánh giá có verifier, quan hệ cơ chế giữa lỗi và quyết định, khuyến nghị thực hành. **Quyết định:** **Conditional, backup**; nguy cơ incremental cao hơn N1.

## N3. Mua thêm mẫu hay mua phép đo tốt hơn?

### Câu hỏi một câu

**Dưới ngân sách thu thập cố định, khi nào giảm sai số đo ở những biến tham gia separating sets đáng hơn tăng số cá thể, và có nhận diện được tình huống đó mà không biết trước graph thật không?**

### Prior art, gap và cơ chế

P15 Scheines–Ramsey đã chỉ ra measurement error làm mất CI và có tác động không cục bộ. P16 Blom et al. đã dùng bounds/correction của measurement variance. P17 TIN có discovery riêng cho measurement model tuyến tính non-Gaussian. P18 Yang et al. xử lý cả latent lẫn measurement error dưới separability/faithfulness. **Không có gap rộng “discovery chưa xử lý measurement error”.**

Gap ứng viên là **thiết kế thu thập có chi phí**, tách vị trí sai số đo khỏi tổng lượng nhiễu và khỏi n, dưới các correction mạnh đang có. Không có dữ liệu mới chứng minh gap này còn lớn.

Ví dụ đại số [Inference, không phải kết quả mới]:

`X ~ N(0,1); Z=aX+e_Z; Y=bZ+e_Y; W=Z+δ`, các noise độc lập, `Var(Z)=v`, `Var(δ)=τ²`.

Khi điều kiện hóa vào phép đo W thay vì Z:

`Cov(X,Y | W) = ab τ²/(v+τ²)`.

Với m technical replicates độc lập cùng đo Z, dùng trung bình thì thay τ² bằng τ²/m. Tăng n làm kiểm định nhìn rõ residual dependence này; giảm nó bằng đo lặp lại làm giảm số cá thể có thể mua. Đây là bias–variance trade-off quen thuộc. **Phần có thể mới phải là vai trò cấu trúc của biến đo và một quyết định thu thập hữu ích ngoài correction cổ điển**, không phải công thức trên.

### Đòn bẩy và controls

Thiết kế crossed: vị trí nhiễu (biến tách trung gian/biến đầu cuối/biến không liên quan) × mức replication, giữ SCM sạch và nested sample pool. Giai đoạn đầu Gaussian tuyến tính, causal sufficiency ở latent substantive variables, independent additive measurement errors. Stratum non-Gaussian dành cho TIN phải chấm đúng ordered-group output; không ép thành complete DAG.

Ngân sách minh bạch: `B = N[c_subject + Σ_j m_j c_measure,j]`. Không coi nhiều phép đo cùng cá thể là nhiều sample iid. Với dữ liệu thật, hai lần đo cùng sensor theo thời gian không tự là technical replicates: có thể trạng thái hệ đã đổi.

### Baselines bắt buộc

1. Tăng N, mỗi biến một phép đo.
2. Replicate đều; replicate theo noise variance/reliability, chưa dùng causal role.
3. **Ước lượng covariance sạch từ cross-replicates**, sau đó PC/GES phù hợp; đây là đối thủ đơn giản có thể giết ý tưởng.
4. Bound/correction của P16 trong đúng giả định; TIN trong stratum non-Gaussian thích hợp.
5. Oracle noise variance và oracle role allocation chỉ là upper bounds.

Từ hai measurements độc lập cùng đo vector X, cross-replicate covariance có thể loại additive measurement noise ở population. Nên nếu đề xuất chỉ là “lấy trung bình nhiều hơn”, rất dễ thua một correction dùng hai lần đo. Phải tính variance và mọi chi phí của correction; không khẳng định cách nào thắng trước khi đo.

### Data và evaluation

- Synthetic: public graph families và measurement models của P15–P18; thêm graph family khác, misspecified correlated/device-dependent errors.
- Real: **chưa xác minh** dataset có cả technical replicates và causal reference phù hợp. Chambers chỉ là candidate cần audit timestamps, operating states, calibration. Không hứa rằng đọc nhiều dòng đo liên tiếp là có m phép đo độc lập cùng một trạng thái.
- Chấm substantive graph/CPDAG hoặc partial order đúng target. FCI trên observed measurements cho graph về phép đo, không tự là graph về biến sinh học gốc.
- Metrics: correct/false structural claims theo budget, number of independent subjects, measurement variance estimation error và downstream effects khi định danh được. Paired bootstrap theo SCM; đối chứng n sạch để tách lỗi nền.

### Pilot, survivability và verdict

Pilot rẻ: chain/fork/collider cùng matched coefficients, rồi random public graphs; fixed budget vài mức. Chưa cần adaptive algorithm. Nếu vai trò biến chỉ có ích khi được cung cấp graph thật thì chưa phải phương pháp khả dụng.

**No-go:** correction đơn giản bằng replicates xử lý gần hết; chỉ thấy trade-off quen thuộc; lợi thế mất khi có correlated errors hoặc khi causal role phải ước lượng. **Conditional positive:** quy tắc phân bổ dùng thông tin khả dụng vượt variance-only và uniform replication trên graph mới, lý giải được khi nào lợi/hại.

**Tối thiểu:** boundary map giúp quyết định thu thập, có validation độc lập. **Mạnh:** acquisition rule được đánh giá dưới chi phí và sai giả định. **Quyết định:** giữ ứng viên, **chưa ưu tiên**, vì headroom chưa rõ và dữ liệu thật chưa chốt.

## N4. Lọc tế bào đáp ứng: cải thiện bằng chứng hay tạo thiên lệch?

### Câu hỏi một câu

**Khi đánh giá causal network từ Perturb-seq, bao nhiêu lợi ích của lọc tế bào đáp ứng đến từ sửa perturbation labels, bao nhiêu đến từ chọn theo hậu quả và dùng lại tín hiệu chọn mẫu trong thước đo?**

### Problem, prior art và gap

P20 Mixscape, P21 ContrastiveVI+ và P22 perturbation-response score đã giải quyết nhiều khía cạnh escape/response heterogeneity. P19 CausalBench dùng interventional response để đánh giá mạng; nó không cung cấp full direct-edge truth. P23 ARGEN đã có proxy/IV để xử lý confounding trong network recovery. Không được gọi “perturbation labels noisy” hay “latent confounding in Perturb-seq” là gap mới.

Giao điểm đề xuất là **efficacy correction × evaluation conditional on detected response**. Cần phân biệt ba cơ chế: loại label sai, chọn nhóm có outcome mạnh, và selection/collider làm sai quan hệ. Những hiện tượng nền đều đã biết; novelty cần một phép tách cụ thể và tác động đáng kể trên protocol thực.

### Insight và target

Ký hiệu A là gRNA assignment, E là actual editing/perturbation efficacy, U là trạng thái trước can thiệp, Y là readout và S là cờ “giữ cell”. Nếu S được xây từ Y thì phân bố Y sau lọc đã đổi theo construction. Nếu U ảnh hưởng cả response và selection thì còn có thể đổi thành phần nhóm. Một random assignment A ban đầu không bảo vệ mọi phép so sánh sau chọn S.

**Không mặc định có collider bias trong mọi pipeline.** Ví dụ lọc đúng escape dựa trên assay độc lập có thể có ích. Quan trọng hơn, ITT theo assignment và effect ở true responders là hai estimand khác nhau. Khác nhau giữa chúng không tự là bias. Phải chốt estimand trước.

P22 đã bàn survival bias. N4 phải tách **tế bào chết trước khi quan sát** khỏi **tế bào bị phần mềm loại sau khi đã quan sát**. Không có thuật toán lọc nào tự khôi phục được mọi cell đã chết.

### Thiết kế thực nghiệm

Giai đoạn đầu chưa infer full GRN: trên một danh sách perturbation–outcome được chốt, so filter với outcome held-out. Sau đó mới xem tác động lên network output.

Cross hai trục:

- E ngẫu nhiên vs E liên quan trạng thái U, với số cell, tỷ lệ efficacy và effect size được kiểm soát trong simulator.
- Nhãn giữ cell lấy từ assay độc lập/oracle E vs expression-derived score vs không lọc.

Dùng cùng cell pool và cùng assignment; không so hai screen khác nhau rồi quy khác biệt cho filter. Cân bằng số cell bằng subsampling độc lập để tách gain do chọn mẫu khỏi loss do ít mẫu.

Controls: null gRNAs; outcome không dùng huấn luyện filter; batch/guide holdout; assay editing hoặc protein orthogonal khi phù hợp. **Cross-fitting theo cell chỉ giảm overfitting, không tự loại bias vì conditioning on post-treatment response.** Protein cũng có thể là hậu quả và chịu chung state; không gọi nó ground truth editing nếu biology không hỗ trợ.

### Baselines và dữ liệu

1. All-assigned/ITT theo đúng estimand, negative-control calibrated.
2. Mixscape hard filtering và response-score weighting.
3. Joint latent efficacy model như ContrastiveVI+; audit output task trước khi dùng.
4. Independent-assay filter; oracle E chỉ trong simulation.
5. Nếu chuyển sang network: ARGEN hoặc phương pháp thích hợp cho soft interventions/confounding; không dùng duy nhất FCI và NOTEARS.

Data candidates đã có nguồn công khai: Papalexi ECCITE-seq (multimodal), CausalBench K562/RPE1; P22 công bố GSE247601 và mã PS. **Chưa tải và chưa kiểm đủ metadata** cho phép ghép efficacy/orthogonal outcome/replicate. Simulator count data dùng để biết ground truth là lớp kiểm cơ chế, không đại diện đầy đủ sinh học.

Primary metrics: false-positive rate trên negative-control perturbations, agreement với held-out independent readout, hiệu ứng theo estimand đã chọn, độ ổn định theo guide/replicate và ranking shift sau đánh giá độc lập. Cell không phải luôn đơn vị độc lập: phân tích phải theo biological replicate/guide hoặc cluster được metadata hỗ trợ. Không dùng “direct-edge accuracy” trên mọi gene chỉ từ differential expression.

### Pilot, survivability và verdict

Pilot: một screen nhỏ có readout orthogonal, fixed pair list và control perturbations, chưa train full foundation model. Chạy giả lập để xác nhận có thể tách selection theo outcome khỏi correction label; sau đó kiểm trên dữ liệu thật mới được nói pipeline hiện hành bị ảnh hưởng.

**No-go:** khác biệt chỉ do đổi estimand; hết khi evaluate outcome độc lập; best existing joint model đã giải quyết; hoặc không có assay/replicate phù hợp. Nếu gain giảm sau bỏ circularity, đó là kết quả audit có giá trị nhưng phải đủ rộng và có cơ chế để thành bài.

**Tối thiểu:** một decomposition có validation đa phương thức và tác động thực lên conclusions. **Mạnh:** đánh giá và ước lượng phù hợp với latent efficacy/selection, có replication qua screen. **Quyết định:** ứng viên ứng dụng đáng review, **không ưu tiên nếu thiếu teammate/domain expert về single-cell**. Không liên hệ ai trong lượt này.
