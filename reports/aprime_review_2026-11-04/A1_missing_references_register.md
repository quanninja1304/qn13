# A′ — Missing references & dependency register (Day 3, Workstream 2)

> Ngày: 2026-11-04. Mức truy cập được ghi theo thực tế **trong phiên này**: đã kiểm tra `docs/papers/` và chạy vài truy vấn web.
> Không có nguồn nào bị ghi là "đã đọc" nếu không thực sự đọc. Kết quả web search chỉ cung cấp **metadata hoặc tóm tắt từ search engine** (ghi là ABSTRACT ONLY hoặc METADATA). Đó không phải full text.

## 1. Năm nguồn được yêu cầu

| # | Nguồn (bibliographic identity) | Access state | Vì sao cần | Câu hỏi / định lý cụ thể | Quyết định bị chặn (chính xác) | Việc làm được khi chưa có |
|---|---|---|---|---|---|---|
| 1 | Triantafillou S., Tsamardinos I., Roumpelaki A., *Learning Neighborhoods of High Confidence in Constraint-Based Causal Discovery*, PGM 2014 (European Workshop on Probabilistic Graphical Models), pp. 487–502. Volume LNCS 8754 theo [GAP] và bscd.pdf ref. [34]; chưa đối chiếu trang publisher. DOI: **chưa xác minh** | **MISSING** (full text). Chỉ có: mô tả gián tiếp trong BSC-D [Source-verified: `docs/papers/bscd.pdf` tr. 4–5: "convert p-values to posterior probabilities of adjacencies and non-adjacencies… identify neighborhoods… post-processing step on the skeleton"]; citation pp. 487–502 qua web search (METADATA). `docs/papers/Triantafillou_2014_download.url` là shortcut, ResearchGate 403 | Prior art trực tiếp nhất cho **feature-level confidence trong constraint-based discovery** | (a) Mô hình p-value có giả định độc lập giữa các test không? (b) Feature là adjacency hay cả orientation/ancestral? (c) Có xử lý latent không? (d) Có đánh giá calibration/precision theo ngưỡng không? (e) Họ dùng mixture Beta cho p-values (arXiv 1403.2150 cùng nhóm, METADATA) hay cách khác? | **Chặn:** claim novelty cho mọi score "confidence ở cấp feature với ngưỡng calibrated" (H-cal/R1); baseline B6. **Không chặn:** kết luận toán Day 1/2 (độc lập với paper này) | Đọc arXiv 1403.2150 (Triantafillou et al., cùng nhóm, có thể chứa cơ chế p-value → posterior) như proxy, ghi rõ là proxy |
| 2 | Zhang J., *On the completeness of orientation rules for causal discovery in the presence of latent confounders and selection bias*, Artificial Intelligence 172 (2008) | **PARTIAL – METADATA ONLY** (`docs/papers/Zhang_2008_publisher_metadata.xml`; ScienceDirect 403) | Semantics của endpoint/orientation features trong PAG; tính complete của FCI | Định nghĩa chính xác các invariant mark; R1–R10 complete ⇒ "feature identifiable từ oracle CI" cho endpoint | **Chặn:** mọi claim về **endpoint features**. **Không chặn:** ancestral features trên MAG enumeration nhỏ (Richardson–Spirtes 2002 đủ; ACI cũng dùng ancestral) | Giới hạn phạm vi vào ancestral features (đã làm trong contract v2 §1.2) |
| 3 | Silvapulle M.J., Sen P.K., *Constrained Statistical Inference: Inequality, Order, and Shape Restrictions*, Wiley 2005 | **MISSING** (`Silvapulle_Sen_2005_archive.url`; Internet Archive giới hạn) | Tổng hợp chuẩn về chi-bar-square, LRT dưới ràng buộc bất đẳng thức, kiểm định có indifference zone | (a) Phân phối LRT khi null/alternative là hợp các nón (không lồi)? (b) Least-favorable configuration cho bài toán non-nested có indifference zone? (c) Các kết quả "projection/Scheffé" cho ràng buộc đa diện | **Chặn:** mọi claim calibration *chặt* (không conservative) cho D hoặc T; claim "phân phối null của constrained GLS". **Không chặn:** R1 với ngưỡng χ²_rank (validity conservative tự chứng minh được, contract §7) | Dùng Berger (IUT, đã có), Drton 2009 (đã có, chưa đọc kỹ), Shapiro 1985 (scan, cần OCR/đọc ảnh) |
| 4 | Berger R.L., *Multiparameter Hypothesis Testing and Acceptance Sampling*, Technometrics 24 (1982) | **PARTIAL**: bản **FSU TR M555 (07/1980)** có trong `docs/papers/Berger_1980_M555_Technical_Report.pdf`. Đã đọc Theorem 1 (IUT có level α) và Theorem 2 (size đúng α dưới điều kiện) qua OCR, có lỗi ký tự. Bản journal chưa có | Cơ sở cho R1′: null là hợp ⇒ intersection–union test | Số định lý ở bản journal có trùng TR không; điều kiện Theorem 2 (size đúng) có áp dụng cho vùng R(m) với nhiều sign orthant không | **Không chặn quyết định nào ở Day 3.** Chỉ ảnh hưởng tới trích dẫn chính xác trong paper | Trích dẫn theo TR, ghi rõ phiên bản |
| 5 | Olkin I., Finn J.D., *Correlations Redux*, Psychological Bulletin 118 (1995) | **PARTIAL**: Stanford TR (08/1994) có trong `docs/papers/Olkin_Finn_1994_Correlations_Redux_Technical_Report.pdf`, nhưng **không có text layer** (trích text rỗng), nên **chưa đọc** | Công thức cov tiệm cận của tương quan và partial correlation (delta method) cho Σ của vector Fisher-z | Công thức joint cov cho partial correlations với conditioning sets **chồng lấp** | **Không chặn**: script Day 2 tự cài delta method và **đối chiếu bằng Monte Carlo** (C1: sai lệch tương đối 3.0–3.5% ở 4 000 replicate; xem `A1_toy_results.md` §4.1). Chỉ ảnh hưởng tới trích dẫn | Giữ bản tự suy ra, gắn nhãn [Derived + MC-checked] |

## 2. Nguồn bổ sung phát hiện trong phiên này (không có trong danh sách 5)

| Nguồn | Access state | Tại sao quan trọng cho quyết định |
|---|---|---|
| Wang Y.S., Kolar M., Drton M., *Confidence Sets for Causal Orderings*, JASA 2025, doi:10.1080/01621459.2025.2542552; arXiv 2305.14506 | **ABSTRACT ONLY** (tóm tắt từ web search, chưa đọc full text) | Theo tóm tắt: **nghịch đảo kiểm định** để tạo confidence set các ordering, asymptotically valid, cho **sub/superset ancestral relations**. Đây là prior art rất gần với reformulation R1 (projection của confidence set lên ancestral features), dù giả định khác (SEM identifiable, additive errors, có vẻ không latent). **Chặn:** novelty của R1 cho đến khi đọc full text |
| Strieder D., Freidling T., Haffner S., Drton M., *Confidence in causal discovery with linear causal models*, UAI 2021, PMLR 161 | **METADATA** (tên, venue qua web search; Guo–Wu–Yiu Table 1 có nhắc) | Test inversion cho structure + effect uncertainty (bivariate linear). Chặn một phần novelty của R1/R2 |
| Zhang J., Spirtes P., *Strong faithfulness and uniform consistency in causal inference*, UAI 2003 (arXiv 1212.2506); Uhler C., Raskutti G., Bühlmann P., Yu B., *Geometry of the faithfulness assumption*, Ann. Statist. 2013 (arXiv 1207.0547) | **METADATA/ABSTRACT** (web search) | λ-strong faithfulness chính là beta-min η của A′. Uhler et al.: tỷ lệ phân phối λ-strong-faithful co lại nhanh theo kích thước/mật độ đồ thị. **Hệ quả:** R2 (η-profile) phải định vị so với dòng này; giả định η của A′ là giả định đã biết là rất mạnh |
| Robins J., Scheines R., Spirtes P., Wasserman L., *Uniform consistency in causal inference*, Biometrika 2003 | **MISSING** | Kết quả bất khả thi nền tảng; dùng để biện minh vì sao η là cần thiết. Không chặn quyết định |
| Triantafillou et al., arXiv 1403.2150 (mixture Beta cho p-values của (non)adjacency) | **METADATA** | Proxy cho nguồn #1 |
| Claassen T., Heskes T., *Bayesian probabilities for constraint-based causal discovery*, IJCAI 2013 | **METADATA** | Prior art về xác suất cho input statements; liên quan tới ACI Bayesian weights |
| Browne M.W. (1984) và văn liệu minimum-distance/ADF cho covariance structures | **MISSING; chưa xác minh bibliographic** | Contract v2 §2.4: D(f) với tham số hóa đúng rank là một minimum-distance test. Cần xác minh trước khi viết trong paper rằng "đây là GLS/ADF cổ điển" |
| Shapiro A. (1985), Biometrika (chi-bar) | **PRESENT nhưng là scan, chưa đọc** | Thay thế một phần cho Silvapulle–Sen |

## 3. Thứ tự đọc đề xuất (nếu user bổ sung PDF)

1. **Wang–Kolar–Drton (JASA 2025)**. Ưu tiên cao nhất. Quyết định R1 có còn residual novelty không: liệu projection của confidence set lên ancestral features đã có, cùng validity.
2. **Triantafillou et al. PGM 2014**. Quyết định baseline B6 và novelty của feature-level confidence trong constraint-based.
3. **Strieder et al. UAI 2021**. Test inversion trong causal discovery.
4. Zhang–Spirtes 2003 / Uhler et al. 2013. Bắt buộc nếu theo R2.
5. Silvapulle–Sen ch. 3–4 (theo mục lục; **chưa xác minh** số chương). Chỉ khi cần calibration chặt.
6. Zhang 2008. Chỉ khi mở rộng sang endpoint features.

---

## 4. Cập nhật 2026-11-04 (lần 2): user bổ sung 8 PDF — kiểm tra danh tính và đọc

### 4.1 Danh tính file mới (đã mở bằng PyMuPDF; số trang và text layer được kiểm tra)

| File trong `docs/papers/` | Danh tính xác nhận | Trang | Text layer | Thay cho mục |
|---|---|---|---|---|
| `Learning Neighborhoods of High Confidence.pdf` | Triantafillou, Tsamardinos, Roumpelaki, PGM 2014, **LNAI 8754**, pp. 487–502 (header của file) | 16 | Có | #1 → **FULL TEXT VERIFIED** |
| `Probabilistic Graphical Models.pdf` | Toàn bộ kỷ yếu **LNAI 8754** (van der Gaag & Feelders eds.) | 609 | Có | Bản trùng của #1; không cần thêm |
| `On the completeness of orientation rules … selection bias.pdf` | Zhang, *Artificial Intelligence* 172 (2008) 1873–1896, doi:10.1016/j.artint.2008.08.001 | 24 | Có | #2 → **FULL TEXT AVAILABLE** (chưa đọc sâu: phạm vi hiện tại không có endpoint features) |
| `Constrained Statistical Inference Inequality, Order, and Shape Restrictions.pdf` | Silvapulle & Sen, Wiley 2005 (sách, bản OCR, không có TOC/bookmark) | 551 | Có (OCR, ký hiệu toán lỗi một phần) | #3 → **FULL TEXT AVAILABLE**. Mục lục: ch. 3 *Tests on Multivariate Normal Mean* (§3.4 chi-bar-square), §4.9 (mle khi tham số trên biên), **§5.3 IUT** (tr. 235) |
| `Multiparameter Hypothesis Testing and Acceptance Sampling.pdf` | Berger, *Technometrics* 24:4 (1982) 295–300, bản journal | 7 | Có | #4 → **FULL TEXT VERIFIED**; nên trích theo bản journal thay cho TR M555 |
| `Correlations Redux.pdf` | Olkin & Finn, bản *Psychological Bulletin* | 10 | **Có** (khác bản TR) | #5 → **FULL TEXT AVAILABLE**; chưa đối chiếu công thức với delta method tự cài |
| `Confidence Sets for Causal Orderings.pdf` | Wang, Kolar, Drton, *JASA* 121:553 (2026) 690–703, doi:10.1080/01621459.2025.2542552 | 15 | Có | Mục mới → **FULL TEXT VERIFIED (bài chính)**; **supplement thiếu** |
| `Confidence in Causal Discovery with Linear Causal Models.pdf` | Strieder, Freidling, Haffner, Drton, UAI 2021 | 10 | Có | Mục mới → **FULL TEXT VERIFIED (bài chính)** |

### 4.2 Điều đọc được, liên quan trực tiếp tới gate RG0 (`A1_pilot_readiness.md` §9)

- **Wang–Kolar–Drton (JASA 2026)** [Source-verified, bài chính]:
  - Phạm vi: "identifiable structural equation models with additive errors" (abstract), tức nonlinear hoặc non-Gaussian. Họ dùng goodness-of-fit qua residual bootstrap cho từng **ordering**, rồi nghịch đảo kiểm định.
  - Lemma 3: Â∩ ⊆ A ⊆ Â∪ với xác suất tiệm cận ≥ 1 − 2α (ancestral relations suy ra từ confidence set ordering).
  - Kết luận nêu **causal sufficiency** là giới hạn: "Future work could extend this procedure to settings where causal sufficiency may not hold (see, e.g., Wang and Drton 2023)".
  - Họ cũng nhấn mạnh "we do not require a minimum effect size", và hệ quả là khoảng tin cậy rộng.
  - Proofs nằm trong **supplementary material (thiếu)**.
- **Triantafillou et al. (PGM 2014)** [Source-verified]:
  - PROPeR ước lượng posterior cho **adjacency/non-adjacency của skeleton** (bỏ qua orientation), từ p-value lớn nhất của mỗi cặp, bằng mixture Beta(1,1) + Beta(ξ,1) (tr. 491–492).
  - Tác giả viết rằng giả định p-values i.i.d. "is clearly violated" cho p-values thu trong skeleton search (tr. 492).
  - BiND tìm clique có độ tin cậy tối thiểu trên ngưỡng.
  - Paper **không** có ancestral/orientation features, **không** có bảo đảm frequentist, và **không** mô hình dependence giữa các test.
- **Strieder et al. (UAI 2021)** [Source-verified, quét]: test inversion cho **bivariate linear SEM homoscedastic**; tập mô hình là hợp M_r1 ∪ M_r2. Target là causal effect. Không latent.

**Đánh giá RG0 tạm thời (agent, chưa có user duyệt): PASS CÓ ĐIỀU KIỆN.**
- Không nguồn nào đã đọc làm *projection/test inversion cho ancestral features trong MAG có latent, từ vector CI statistics, dưới beta-min*.
- Khác biệt so với Wang–Kolar–Drton là có thật và kiểm tra được: latent/MAG, Markov equivalence (Gaussian không identifiable), và đầu vào là CI statistics thay cho residual GOF trên ordering.
- Nhưng có hai điểm phải nói trung thực:
  - (a) **Khung ý tưởng** (nghịch đảo kiểm định → tập mô hình không bị bác bỏ → feature bất biến trên tập đó) **đã có** trong dòng Drton (2021–2026). R1 vì vậy là *mở rộng khung đã biết sang setting latent/CI-based*, không phải khung mới.
  - (b) Wang–Kolar–Drton tránh beta-min nhờ identifiability. Trong setting CI-based có latent, R1 bắt buộc cần η (no-free-lunch). Reviewer sẽ coi η là điểm yếu, trừ khi R2 (η-profile) được trình bày như đóng góp chính.

### 4.3 Vẫn còn thiếu (xếp theo mức ảnh hưởng tới quyết định)

| Ưu tiên | Tài liệu | Vì sao cần / quyết định bị ảnh hưởng | Trạng thái |
|---|---|---|---|
| **Cao** | **Supplementary material** của Wang–Kolar–Drton (JASA; proofs Thm 1–2, Lemma 3) | Kiểm tra chứng minh Lemma 3 có tổng quát hóa thẳng sang tập mô hình MAG hay không. Nếu có, lý thuyết của R1 là hệ quả trực tiếp ⇒ novelty còn hẹp hơn | MISSING |
| **Cao** | Strieder & Drton (2023), *Confidence in causal inference under structure uncertainty in linear causal models with equal variances*, J. Causal Inference 11, 20230030 (arXiv 2309.04298) | Mở rộng nhiều chiều của dòng test inversion; có thể chứa kỹ thuật union-of-models gần R1 | MISSING (open access) |
| **Cao** | Strieder & Drton (2024), *Dual likelihood for causal inference under structure uncertainty*, CLeaR 2024, PMLR 236 | Như trên | MISSING (open access) |
| **Cao** | Wang & Drton (2023), *Causal discovery with unobserved confounding and non-Gaussian data*, JMLR 24 | Wang–Kolar–Drton chỉ tới đây như đường mở rộng sang latent. Đây là nơi một đối thủ trực tiếp có thể xuất hiện | MISSING (open access) |
| **Cao (cho R2)** | Zhang & Spirtes (2003), *Strong faithfulness and uniform consistency in causal inference*, UAI (arXiv 1212.2506) | Định vị η-profile so với λ-strong faithfulness | MISSING (arXiv) |
| **Cao (cho R2)** | Uhler, Raskutti, Bühlmann, Yu (2013), *Geometry of the faithfulness assumption in causal inference*, Ann. Statist. 41 (arXiv 1207.0547) | Như trên; ngoài ra tỷ lệ phân phối λ-strong-faithful co lại theo kích thước đồ thị, nên ảnh hưởng tới power của R1/R2 | MISSING (arXiv) |
| Trung bình | arXiv 2405.06763, *Post-selection inference for causal effects after causal discovery* (có thể là "Chang+ 2026" trong Table 1 của Guo–Wu–Yiu, **chưa xác minh**) | Target là effect; cần để chắc chắn không có feature-level output | MISSING |
| Trung bình | Peters, Bühlmann, Meinshausen (2016), *Causal inference by using invariant prediction*, JRSSB 78 | Wang–Kolar–Drton so Â∩ với "conservative set of causal predictors" của ICP. Đây là tiền lệ cho chứng nhận nhân quả bảo thủ có validity | MISSING |
| Thấp | Robins, Scheines, Spirtes, Wasserman (2003), Biometrika | Trích dẫn nền cho lý do η là cần thiết | MISSING |
| Thấp | Browne (1984) / văn liệu minimum-distance (ADF) | Chỉ cần khi viết rằng D(f) đúng rank là minimum-distance cổ điển | MISSING |
| Thấp | Supplement của Strieder et al. UAI 2021 | Proofs | Chưa kiểm tra có hay không |

**Không còn thiếu cho 5 nguồn ban đầu:** cả 5 đã có full text. Zhang 2008 chỉ cần nếu mở lại endpoint features.

---

## 5. Cập nhật 2026-11-04 (lần 3): user bổ sung 11 PDF — mọi mục ở §4.3 đã có

### 5.1 Danh tính (đã mở; tất cả có text layer)

| File | Danh tính | Trang |
|---|---|---|
| `Wang_Kolar_Drton_2026_Supplementary_Material.pdf` | Supplement khoa học của JASA 2026 (proofs, simulation thêm) | 29 |
| `Wang_Kolar_Drton_2026_Reproducibility_Form.pdf` | Biểu mẫu tái lập (không phải nội dung khoa học) | 5 |
| `Confidence in Causal Inference under Structure Uncertainty … Equal Variances.pdf` | Strieder & Drton, J. Causal Inference 2023, doi:10.1515/jci-2023-0030 | 21 |
| `Strieder & Drton 2024, Dual Likelihood ….pdf` | Strieder & Drton, *Dual likelihood for causal inference under structure uncertainty* (bản trong file là bản tác giả; venue CLeaR 2024 theo trích dẫn trong WKD) | 17 |
| `Causal Discovery with Unobserved Confounding and Non-Gaussian Data.pdf` | Wang & Drton, JMLR 24 (2023) | 61 |
| `Strong Faithfulness and Uniform Consistency in Causal Inference.pdf` | Zhang & Spirtes, UAI 2003, tr. 632–639 | 8 |
| `Geometry of the Faithfulness Assumption in Causal Inference.pdf` | Uhler, Raskutti, Bühlmann, Yu, Ann. Statist. 41(2) 2013, doi:10.1214/12-AOS1080 | 28 |
| `Uniform Consistency in Causal Inference.pdf` | Robins, Scheines, Spirtes, Wasserman, Biometrika 90(3) 2003 | 25 |
| `Post-selection Inference for Causal Effects After Causal Discovery.pdf` | Chang, Guo, Malinsky; **bản tác giả (PMC author manuscript)**, Biometrika. Chưa xác minh là bản typeset | 21 |
| `Causal Inference by Using Invariant Prediction ….pdf` | Peters, Bühlmann, Meinshausen, JRSSB 78 (2016) 947–1012, kèm discussion | 66 |
| `Asymptotically Distribution-Free Methods … Covariance Structures.pdf` | Browne, Br. J. Math. Stat. Psychol. 37 (1984) 62–83 | 22 |

### 5.2 Điều đọc được, ảnh hưởng tới quyết định

1. **WKD supplement, chứng minh Lemma 3** [Source-verified, tr. 46]: chứng minh **hoàn toàn tổ hợp**. Nếu ordering đúng nằm trong confidence set (Eq. 2) thì Â∩ ⊆ A ⊆ Â∪; trường hợp nhiều ordering đúng dùng hai ordering, nên tốn 2α.
   - **Hệ quả cho R1:** bước "projection lên feature" của R1 là cùng lập luận (thay ordering bằng MAG). Với một ellipsoid chung, lập luận này còn cho 1 − α. **Bước này không có novelty lý thuyết.**
   - Ghi chú phụ: dòng "for every (u,v) ∈ A, θ1(v) < θ1(u)" trong chứng minh có vẻ là lỗi đánh máy (đúng ra là θ1(u) < θ1(v)). Không ảnh hưởng kết luận.
2. **Wang & Drton (JMLR 2023)** [Source-verified, abstract + quét]:
   - Phát hiện **điểm** (BANG) cho bow-free acyclic path diagrams với latent confounding, dưới non-Gaussianity.
   - Có khái niệm "certifying ancestral relationships" ở mức **population/sound-complete**, **không** có confidence/uncertainty.
   - Không phải đối thủ trực tiếp. Nhưng nó cho thấy một mở rộng "WKD + latent" trong setting **non-Gaussian** là đường tự nhiên của nhóm Drton, và đó là rủi ro bị đi trước (scooping). A′/R1 khác ở chỗ dựa trên CI statistics và Markov equivalence, kể cả Gaussian.
3. **Chang, Guo, Malinsky** [Source-verified]:
   - Resampling & screening quanh **PC** (causal sufficiency). Target là **causal effect**.
   - Theorem 2 cho validity "under weak conditions" (Markov + faithfulness, tức pointwise). Strong faithfulness chỉ dùng cho efficiency (Theorem 3, tr. 11–12; tác giả viết "this assumption is indeed very strong").
   - **Hệ quả:** cơ chế "chạy discovery nhiều lần với thống kê nhiễu, lấy hợp các đồ thị" chuyển thẳng được sang feature (feature được chứng nhận nếu đúng trên mọi đồ thị còn lại). Đó là **baseline cùng target bắt buộc** cho R1 (BL9).
4. **Robins et al. 2003; Zhang & Spirtes 2003** [Source-verified, abstract]: dưới Markov + faithfulness có thủ tục **pointwise consistent**; **uniform** consistency là không thể khi có latent hoặc không biết thứ tự thời gian. Dưới λ/k-strong faithfulness thì uniform consistency đạt được. → **Erratum cho contract v2 §1.6/B3** (xem bên dưới).
5. **Uhler et al. 2013** [Source-verified, abstract]: tập phân phối không λ-strong-faithful có measure dương và "can be surprisingly large". Điều này gợi ý η*(f) (R2) sẽ thường nhỏ, nên power của bản "uniform" sẽ thấp. Đây là một dự đoán có thể kiểm tra, **không** phải kết quả.
6. **Browne 1984** [Source-verified]: GLS/ADF minimum-discrepancy cho covariance structures: nF(S, Σ(γ̂) | U) tiệm cận χ² (non-central) với p* − q bậc tự do, cần Jacobian **full column rank** (điều kiện R4). → Nhận định của contract v2 §2.4/R3 ("D(f) tham số hóa đúng rank là minimum-distance cổ điển") nay được **xác nhận từ nguồn** về khung. Việc áp vào vùng hợp của MAG vẫn là [Derived].
7. **Peters–Bühlmann–Meinshausen 2016 (ICP)**: tiền lệ cho tập chứng nhận nhân quả bảo thủ có coverage, nhưng **cần nhiều environment/intervention**. Không cùng setting (observational).

### 5.3 Còn thiếu?

**Không còn tài liệu nào chặn quyết định.** Các mục tùy chọn, ưu tiên thấp:
- Kalisch & Bühlmann (2007, JMLR): tốc độ α_n → 0 cho PC Gaussian. Được ACI Eq. 17 và Chang et al. trích dẫn; hữu ích khi chọn η_n → 0 cho R1 pointwise.
- Supplement của Strieder et al. UAI 2021: chỉ để kiểm proofs.
- Supplement của Chang et al., nếu có.
