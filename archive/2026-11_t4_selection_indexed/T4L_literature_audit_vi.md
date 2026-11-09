# Audit văn liệu cho T4-L

> Ngày 2026-11-06. Đây là bước 1 trong [`T4_kill_test_vi.md`](T4_kill_test_vi.md) §8. Hồ sơ: `T4L_citation_screen.json`, `T4L_citations_semanticscholar.py`, `T4L_citations_openalex.py`. Phép thử baseline: `T4L_baseline_oracle_check.py`, `T4L_baseline_oracle_outputs.json`, `T4L_baseline_oracle_run_log.txt`.
> Nhãn: **[Verified]** đã đọc trong nguồn gốc; **[Inference]** suy luận của tôi; **[Hypothesis]** chưa kiểm chứng; **[Unresolved]** chưa rõ.

## 1. Kết luận

**Tiêu chí no-go đã khai báo không bị kích hoạt, nhưng novelty của T4-L hẹp hơn tôi đánh giá trước đây.** Tiêu chí là: có công trình dùng phép test chỉ báo làm bước xác nhận CI, hoặc có phân tích power tương tự, trong constraint-based discovery. Tôi không tìm thấy công trình nào như vậy. Đây là bằng chứng tìm kiếm, có giới hạn ở §7, không phải bằng chứng rằng chưa ai làm.

| Thành phần của T4-L | Trạng thái | Nguồn gần nhất |
|---|---|---|
| Điều kiện toán học | **Đã có từ 2010, không mới** | Didelez et al. 2010, Theorem 6 |
| Chiều ngược, dạng test-wise | **Đã có** | Witte et al. 2022, Lemma 6 |
| Phép test kiểm tra được từ dữ liệu | **Đã có** | Mohan & Pearl 2014 Thm 1; 2021 Thm 5 |
| Dạng hồi quy chỉ báo trên hàng quan sát | **Đã có, lâu đời** | Test attrition trong Fitzgerald et al. |
| Pretest chỉ báo rồi mới xóa dữ liệu | **Đã có trong SEM** | Ji et al. 2023 |
| Dùng phép test chỉ báo trong PC để đánh dấu cạnh | **Đã có, cho việc khác** | MVPC (Tu et al. 2019), Step 2–3 |
| Dùng làm **bước xác nhận CI trong FCI**, có latent và selection | **Không tìm thấy** | Gần nhất là M1 và MVPC |
| So sánh power test chỉ báo với test CI trực tiếp theo bậc hiệu ứng | **Không tìm thấy** | Ji et al. chỉ nhận xét định tính |

**Đánh giá [Inference]:** T4-L không có định lý mới và cơ chế toán không mới. Nếu có đóng góp, nó nằm ở phương pháp: đặt một điều kiện collapsibility đã biết vào đúng chỗ trong FCI, kèm phân tích về khi nào nó thắng và khi nào nó hỏng. Theo tiêu chí của `AGENTS.md`, bản thân việc ghép này chưa phải cơ chế mới; nó chỉ đáng giá nếu pilot mức thuật toán cho thấy lợi ích đo được.

**Khuyến nghị:** vẫn chạy pilot mức thuật toán vì rẻ và có thể bác bỏ dứt khoát, nhưng hạ kỳ vọng xuống **một bài phương pháp ngắn**, và tìm song song một hướng dự phòng. Đây là quyết định của bạn.

## 2. Đính chính so với báo cáo kill test

- **§5 của kill test trình bày Mệnh đề L như một mệnh đề riêng. Thực ra nó là trường hợp đặc biệt của Didelez et al. 2010, Theorem 6**, áp dụng có điều kiện trên S_U. Kill test ghi "đọc qua Witte"; nay đã đọc gốc, và hai chiều đều có sẵn. **[Verified]**
- **Lập luận "bậc hai" cần sắc thái.** Theo tóm tắt của Greenland 2003 (chỉ đọc qua kết quả tìm kiếm): bias do phân tầng trên biến chịu ảnh hưởng của cả exposure và disease "có thể thường tương đương" bias nhiễu cổ điển, còn các dạng collider khác có xu hướng nhỏ hơn nhiều. Điều này phù hợp với việc thứ tự bậc đảo chiều ở họ D, và không ủng hộ khái quát "bias do selection luôn nhỏ". **[Inference]**

## 3. Phép thử baseline đơn giản nhất

MVPC Step 2 được chính tác giả mô tả là "tương đương chạy TD-PC trên V ∪ R". Vì vậy, tôi kiểm tra FCI coi chỉ báo như biến thường. Nếu nó đã hết claim sai ở oracle thì T4-L không còn lý do tồn tại. Luật được khai báo trước: baseline thay thế được T4-L nếu số đồ thị có claim sai ≤ 10% của naive và giữ ≥ 90% claim đúng.

| Tổng trên các ô MNAR (q = .1, .3; p = 4, 5) | LW | NaiveO | NaiveOR | NaiveOR+ |
|---|---|---|---|---|
| Đồ thị có claim sai | 0 | 317 | **822** | **522** |
| Claim đúng | 25 562 | 35 169 | 37 887 | 36 799 |

**Theo luật: baseline không thay thế được T4-L ở oracle.** Thêm chỉ báo làm biến còn tăng claim sai, vì mỗi truy vấn vẫn ở regime riêng và có thêm cạnh để định hướng. **[Inference]** về nguyên nhân.

**Minh bạch:** bản đầu của phép thử này có lỗi do tôi: coi cặp (R_i, O_i) không kiểm định được là "phụ thuộc", tạo cạnh giả. Đối chứng q = 0 phát hiện được (191 đồ thị có claim sai). Số của bản đó bị bỏ. Bản sửa theo giả định của MVPC (không có cạnh R_i–O_i, cặp này không dùng để định hướng) cho 0 claim sai ở q = 0. Ngưỡng không đổi.

**Giới hạn:** đây chỉ là oracle và chỉ kiểm tra FCI thuần trên O ∪ R. Nó **không** kiểm tra MVPC đầy đủ, vì MVPC có bước hiệu chỉnh và giả định đủ nhân quả, không self-masking.

## 4. Ma trận bằng chứng

Mức đọc: **A** đọc phần liên quan trong nguồn gốc; **B** tóm tắt và quét từ khóa trong nguồn gốc; **C** chỉ tóm tắt hoặc kết quả tìm kiếm. Tôi không ghi baseline hay metric của những bài chưa đọc tới phần đó.

| Bài (năm, trạng thái) | Bài toán, output | Giả định | Cơ chế | Lý thuyết | Thực nghiệm | Giới hạn | Quan hệ với gap | Mức |
|---|---|---|---|---|---|---|---|---|
| [Didelez, Kreiner, Keiding 2010](https://arxiv.org/pdf/1101.0901), Stat. Sci. | Suy luận dưới outcome-dependent sampling | S ⊥ Y \| (C,X) hoặc S ⊥ X \| (C,Y) | Nếu một trong hai giữ, thì Y ⊥ X \| C ⇔ Y ⊥ X \| (C, S = 1) | Thm 6 | Có ví dụ dữ liệu, chưa đọc | S là giả định, không phải đối tượng test | **Toán đã có** | A |
| [Witte et al. 2022](https://arxiv.org/abs/2108.13331), Stat. Med. | PC với test-wise và MI; CPDAG | Đủ nhân quả, faithful observability | Điều kiện cần và đủ cho oracle test-wise PC | Lemma 5–6, Prop 2 | Chưa đọc | Nói điều kiện *không kiểm chứng được thực nghiệm*, vì R_XYZ gồm chỉ báo của chính biến được test | Lý thuyết sát; không có bước kiểm định | A |
| [Tu et al. 2019](https://proceedings.mlr.press/v89/tu19a/tu19a.pdf), AISTATS | MVPC; CPDAG | Assumption 1–4; không self-masking, không latent | Phát hiện cha của R, đánh dấu cạnh nghi ngờ, hiệu chỉnh bằng PermC, DRW | Prop 1–2 | Chưa đọc chi tiết | Không dùng được cho họ A (có self-masking) và khi có latent | **Gần nhất về thuật toán**; dùng R để hiệu chỉnh, không để xác nhận | A |
| [Strobl et al. 2018](https://arxiv.org/pdf/1705.09031), IJDSA | FCI, RFCI test-wise; PAG | Assumption 1, có latent, selection | Xác nhận listwise khi test-wise không bác bỏ | Thm 1 | Có synthetic, cohort | Mất hàng ở bước xác nhận | **Đối thủ chính**; không có test chỉ báo | A |
| [Ji, Rabe-Hesketh, Skrondal 2023](https://link.springer.com/content/pdf/10.1007/s11336-022-09896-0.pdf), Psychometrika | Ước lượng SEM khi vi phạm MAR | m-graph, hai biến chính | Test R-MAR rồi chọn cách xóa dữ liệu: test-based estimator | Không đọc tới | Mô phỏng bias, MSE | Bài toán ước lượng, không phải discovery | **Logic pretest rất gần**; khác bài toán | A |
| [Mohan & Pearl 2014](http://proceedings.mlr.press/v33/mohan14.pdf), AISTATS | Tính kiểm tra được của m-graph | Biết m-graph | Tiêu chí cú pháp | Thm 1 | Không | Không phải thuật toán học cấu trúc | **Tính testable đã có** | A |
| [Mohan & Pearl 2021](https://arxiv.org/pdf/1801.03583), JASA | Tổng quan m-graph | Biết m-graph | X ⊥ R_y \| Z, R_x, R_z testable; X ⊥ R_x \| ... không | Thm 4–5 | Không | Như trên | Đúng dạng phép test của lift (phương trình 14) | A |
| [Nabi & Bhattacharya 2022](https://arxiv.org/pdf/2203.00132), UAI | Goodness-of-fit cho m-DAG | Lớp mô hình cho trước | Test có trọng số; xem CI như ràng buộc Verma | Có, chưa đọc hết | Mô phỏng với 6–80% complete case | Kiểm tra mô hình, không phải discovery | Công cụ hữu ích; ghi nhận test bị mất power khi hàng giảm | A |
| [Fitzgerald, Gottschalk, Moffitt](https://www.nber.org/system/files/working_papers/t0220/t0220.pdf), NBER t0220 | Attrition trong panel | Selection on observables | Hồi quy A trên x, y0; BGLW là dạng nghịch đảo | Lập luận | PSID | Không có đồ thị, không CI | **Dạng test đã có từ lâu** | A |
| [Bartlett et al. 2014](https://lshtm-eprints-repo-prod.lshtm-eprints.cdl.cosector.com/1776659/1/kxu023.pdf), Biostatistics | Hiệu quả của complete-case | R ⊥ Y \| X | Có dùng logistic của R trên biến quan sát trong ứng dụng | Có | NHANES | Ước lượng hồi quy | Thực hành tương tự, khác bài toán | A |
| [Cooper 1995](https://proceedings.mlr.press/r0/cooper95a/cooper95a.pdf), AISTATS | Phát hiện selection bias từ CI | Mạng nhỏ | Mẫu CI đặc trưng | Thm 2 | Không | Không dùng hàng ngoài selection | Khác cơ chế | B |
| [Evans & Didelez 2015](https://people.maths.bris.ac.uk/~maxvd/Evans_Didelez_UAI2015.pdf), UAI | Khôi phục từ selection, rời rạc | Ràng buộc biên | Dùng cấu trúc biên | Có | Chưa đọc | Có nhận xét về testable | Khác mục tiêu | B |
| [Tillman & Spirtes 2011](https://proceedings.mlr.press/v15/tillman11a/tillman11a.pdf), AISTATS | IOD; đa dataset chồng biến | Cùng cơ chế sinh, không mâu thuẫn CI | Gộp p-value | Có | Chưa đọc | Giả định không mâu thuẫn **không giữ** giữa các regime MNAR | Khác giả định; đe dọa phần ghép regime | B |
| [Versteeg et al. 2022](https://arxiv.org/pdf/2203.01848), CLeaR | Luật cục bộ dưới selection | Có selection, có thể có chu trình | Y-structure | Prop 4 | Mô phỏng, microarray | Không dùng chỉ báo | Liên quan phần cục bộ | B |
| [Qiao et al. 2024](https://arxiv.org/pdf/2312.12206), AAAI | ANM với weak self-masking | Assumption của Tu + weak self-masking | Xác định chỉ báo và skeleton | Thm 1–2 | Chưa đọc | Không latent | Mở rộng dòng Tu | B |
| [Dai et al. 2024](https://arxiv.org/pdf/2403.15500), ICLR | GRN với dropout | Mô hình dropout A1–A5 | Test-wise chỉ trên R của tập điều kiện | Thm 1–3 | Dữ liệu đơn bào | Nhắc giới hạn cỡ mẫu sau xóa | Cấu trúc riêng, khác hướng | B |
| [Ceriscioli et al. 2026](https://arxiv.org/pdf/2610.19211), preprint | Định danh dưới missing cho ANM | Không latent, không self-masking | Chuyển kết quả định danh | Có | Chưa đọc | Không latent | Khác giả định | B |
| [Gain & Shpitser 2018](https://proceedings.mlr.press/v72/gain18a/gain18a.pdf), PGM | PC với reweighting | Biết hoặc đoán m-graph | IPW, thử dãy fixing | Trường hợp chưa biết m-graph còn mở | Mô phỏng | Cần mô hình R | Baseline khác hướng | A |
| [PAIR-CI 2026](https://arxiv.org/pdf/2605.04838), preprint | CI test dựa imputation; PC | Chưa đọc đủ | Permutation ghép cặp | Có | Mô phỏng, HAILFINDER | FCI chỉ được nhắc là khả năng | Khác hướng | B |
| [Lin et al. 2026](https://arxiv.org/pdf/2611.04366), preprint | Khi nào LWD đúng cho ATE | Biết DAG | Thêm chỉ báo vào DAG, kiểm tra tiêu chí điều chỉnh | Có, chưa đọc | Khoa học chính trị | DAG cho trước, không học cấu trúc | Khác bài toán | B |
| [Schnell & Kenah 2024](https://arxiv.org/pdf/2407.20027), preprint | Công cụ đồ thị cho selection | Đồ thị cho trước | SWIG, chỉ báo selection theo mẫu con | Có | Chưa đọc | Không học cấu trúc | Khác bài toán | B |
| [Dai et al. 2025](https://arxiv.org/pdf/2512.11219), arXiv | Selection với biến ẩn | Tuyến tính Gauss | Ràng buộc rank | Có | Mô phỏng, thực | Không dùng hàng ngoài selection | Khác cơ chế | B |
| [Bartlett et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4597800), AJE | OR từ complete-records | Theo bảng điều kiện | Có hướng dẫn dùng dữ liệu quan sát | Có | Chưa đọc | **Không truy cập được toàn văn** | Có thể gần; cần đọc | C |
| [Verbeek & Nijman 1992](https://econpapers.repec.org/RePEc:ier:iecrev:v:33:y:1992:i:3:p:681-703), IER | Test selectivity bias trong panel | Panel | Variable addition, Hausman | Có | Có so sánh power | Chỉ đọc tóm tắt | So sánh power giữa các test, không phải bậc hiệu ứng | C |
| [Greenland 2003](https://www.scilit.net/publications/e0285bab04b404251581273845145885), Epidemiology | So sánh độ lớn collider và nhiễu | Mô hình đơn giản | Công thức bias | Có | Không | Chỉ đọc tóm tắt qua tìm kiếm | Nền cho lập luận bậc | C |
| [Causal Discovery with Incomplete Data from Multiple Sources](https://doi.org/10.1093/jssam/smag016), 2026, JSSAM | MI và DAG, đa nguồn | Chưa rõ | Propensity vào imputation, chỉ báo nguồn trong CI | Chưa rõ | Chưa rõ | **Chỉ có tóm tắt** | Chỉ báo *nguồn*, không phải regime; cần đọc | C |
| [CEIFPC 2024](https://doi.org/10.1109/tim.2024.3522374), IEEE TIM | MNAR, PC | Dùng m-graph | Tiêu chí hiệu chỉnh, information flow | Nêu tiệm cận đúng | Chưa rõ | Chỉ có tóm tắt | Cần đọc xem có test R | C |
| [Federated, JBI 2025](https://doi.org/10.1016/j.jbi.2025.104877) | Federated discovery MNAR | Chưa rõ | Cơ chế thiếu theo client | Chưa rõ | Endometrial cancer | Chỉ có tóm tắt | Chưa rõ | C |

Số bài: 28, gồm 11 mức A, 11 mức B, 6 mức C. [Survey CI test 2026](https://arxiv.org/pdf/2608.11156) không thấy mục về missing data khi quét từ khóa, nên không vào bảng.

## 5. Sổ đăng ký claim

| Claim | Nhãn | Bằng chứng | Bằng chứng hạn chế | Kiểm tra tiếp |
|---|---|---|---|---|
| Lift đúng về xác suất | Verified | Didelez Thm 6; kiểm tra L1, L2 của tôi | Chỉ khi test không sai | Không cần |
| Phép test chỉ báo làm được trên hàng đủ U khi chỉ báo ngoài phát biểu CI | Verified | Mohan & Pearl 2021 pt. 14, Thm 4 | Đặc tả mô hình R | Không cần |
| Chưa có công trình dùng nó làm bước xác nhận trong FCI | Unresolved | Sàng lọc §7 | Chưa đọc full text nhiều bài | Đọc 5 bài ở §7 |
| Bước xác nhận của M1 có failure ở finite sample | Hypothesis | Mô phỏng một bộ ba của tôi | Chưa thử FCI đầy đủ | Pilot |
| Lift giảm false orientation mà giữ claim đúng ở mức thuật toán | Hypothesis | Chỉ mức truy vấn | Họ C, họ D phản lại | Pilot |
| FCI coi chỉ báo như biến không giải quyết được | Verified ở oracle | §3 | Finite sample chưa thử; MVPC chưa thử | Pilot |
| Test chỉ báo có power cao hơn CI trực tiếp | Inference, có điều kiện | Tính tay; bảng họ A | Họ D đảo chiều; Greenland 2003 | Pilot, chứng minh hình thức nếu cần |

## 6. Failure mode, kiểm tra prior art mạnh, phát biểu gap

| Failure mode | Remedy hiện có | Vì sao chưa đủ | Tái lập rẻ nhất | Điều có thể bác bỏ gap |
|---|---|---|---|---|
| FCI test-wise ngây thơ định hướng sai | M1 Algorithm 1 | Sửa được ở oracle | `T4_oracle_checks.py` phần S | Không; đã có remedy |
| Bước xác nhận thiếu power: có cửa sổ n mà PerProof, M1global vẫn khẳng định sai | Tăng n; MVPC khi đủ giả định | MVPC không cho latent, self-masking **[Verified]** | `T4_lift_checks.py` họ A | FCI đầy đủ không còn thấy khác biệt |
| Mất định hướng đúng khi selection thật ảnh hưởng regime | Không rõ | Chính T4-L làm việc này sớm hơn | Họ C | Mất mát vượt lợi ích |

**Kiểm tra theo `research/04`:**
- *m-separation:* có. Biết m-graph thì mọi thứ quy về m-separation chuẩn. T4-L chỉ có ý nghĩa khi **không** biết m-graph.
- *Quyết định CI thận trọng hay có trọng số:* không thấy bài trùng. dcFCI, C-PC và các bài cùng loại chưa được kiểm tra riêng trong audit này.
- *Dữ liệu đa nguồn:* IOD, COmbINE, fedCI-IOD có giả định khác; chưa loại trừ hết vì COmbINE và fedCI-IOD mới đọc lướt.
- *Baseline đơn giản:* đã thử một ở §3; MVPC và MI-FCI chưa.

**Phát biểu gap (một phần là giả thuyết):**

> Dưới Assumption 1 của Strobl et al., có latent và selection, M1 đạt tính đúng oracle theo target listwise nhưng bước xác nhận dùng test CI trực tiếp trên ít hàng. **[Hypothesis]** Ở finite sample, bước này thiếu power khi phụ thuộc do selection là bậc cao. Nghiên cứu tìm hiểu liệu thay bước đó bằng phép test collapsibility trên chỉ báo (Didelez 2010, Thm 6) có giảm false assertion mà không làm mất nhiều claim đúng khi cơ chế thiếu chưa biết và không đồng nhất hay không.

## 7. Phương pháp tìm kiếm và giới hạn

- **Tìm kiếm trực tiếp:** hơn 15 truy vấn, theo cơ chế, thuật ngữ thống kê, kinh tế lượng và dịch tễ.
- **Trích dẫn xuôi** của M1, Tu, Witte, Didelez, Mohan & Pearl, Nabi & Bhattacharya, Qiao, Foraita:
  - Semantic Scholar: 454 bài duy nhất, 104 qua bộ lọc từ khóa.
  - OpenAlex: 321 bài duy nhất, 37 qua bộ lọc.
- **Giới hạn cần nêu rõ:**
  - Bộ lọc chỉ chạy trên **tiêu đề và tóm tắt**, không phải toàn văn. Một bài dùng phép test chỉ báo như chi tiết kỹ thuật có thể lọt.
  - Semantic Scholar trả về 0 bài cho Witte vì giới hạn tốc độ; OpenAlex bù được 21 bài. OpenAlex không tìm thấy Gain & Shpitser.
  - Không có Google Scholar, luận án hay kho code.
- **Chưa đọc được toàn văn:** Bartlett 2015 (PMC chặn bằng trang xác minh chống bot; bản khác không tải được), JSSAM 2026, JBI 2025, KBS 2025, misLCS (ESWA 2024), Tu et al. 2020 (OpenReview trả 403).
  **Năm bài cần đọc trước khi tuyên bố novelty trong bản thảo:** Bartlett 2015, JSSAM 2026, CEIFPC, KBS 2025, misLCS. Bạn có thể lấy qua thư viện nếu có quyền truy cập.
- Thông tin về Verbeek–Nijman, Greenland và các bài mức C chỉ từ tóm tắt.

## 8. Đề xuất điều chỉnh pilot mức thuật toán

So với [`T4_kill_test_vi.md`](T4_kill_test_vi.md) §8:
- **Thêm baseline:** bộ lọc kiểu MVPC Step 3 (bỏ định hướng khi cạnh bị đánh dấu), là bản rẻ nhất của ý "dùng R để không tin cạnh". Nếu bộ lọc này ngang Lift-FCI thì T4-L không có lý do tồn tại.
- **Thêm quy tắc kiểu Ji et al.:** khi cả hai test đều bác bỏ thì sao. Lift hiện chỉ từ chối chứng nhận; cần báo cáo rõ phương án xử lý.
- **Không bán lift như định lý mới.** Mọi bản nháp phải trích Didelez 2010 và Witte 2022 cho phần toán.
- **Nêu rõ giới hạn của "không tìm thấy"** trong mọi kết luận về gap.
- **Thứ tự:** đọc năm bài ở §7 nếu lấy được, rồi chốt ngưỡng, rồi chạy pilot.

## 9. Đánh giá định tính theo tiêu chí dự án

Đây là đánh giá chủ quan của tôi, không phải điểm số.

| Tiêu chí | Đánh giá | Lý do |
|---|---|---|
| Ý nghĩa khoa học | Trung bình | Missing data phổ biến, nhưng ảnh hưởng tới FCI đầy đủ chưa đo |
| Novelty có thể bảo vệ | Thấp đến trung bình | Toán đã có; chỉ cách dùng và phân tích là mới, nếu đúng là mới |
| Chiều sâu phương pháp | Thấp đến trung bình | Cơ chế đơn giản; phần khó là xử lý họ C, họ D |
| Tính khả thi | Cao | Pilot rẻ, không cần dữ liệu riêng |
| Bằng chứng hiện có | Sơ bộ | Một bộ ba biến, do tôi thiết kế |

## 10. Cập nhật sau pilot (2026-11-06)

Pilot mức thuật toán đã chạy và cho **NO-GO theo K8**, xem [`T4L_pilot_report_vi.md`](T4L_pilot_report_vi.md). Khuyến nghị ở §1 và §8 đã được thực hiện; năm bài ở §7 chưa được đọc trước pilot, và nay không còn gấp trừ khi hướng này được mở lại.
