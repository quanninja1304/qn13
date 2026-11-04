# Tình trạng tải tài liệu — 04/11/2026

**Dọn dẹp 04/11/2026:** đã xóa 10 file trùng hoặc phụ trợ hết giá trị sử dụng: 1 PDF bị đặt nhầm tên supplement (trùng byte với bài chính), 4 ZIP đã được giải nén và kiểm tra nội dung, 3 shortcut `.url`, 1 XML metadata và 1 JSON ghi thử tải thất bại. PDF supplement Wang–Kolar–Drton thật là [bản 29 trang](Wang_Kolar_Drton_2026_Supplementary_Material.pdf); [biểu mẫu tái lập](Wang_Kolar_Drton_2026_Reproducibility_Form.pdf) dài 5 trang. Các mục mô tả file thiếu bên dưới là **nhật ký lịch sử**, không phản ánh thư mục hiện tại. Manifest ghi hash của đợt tải ban đầu và các file từng được dọn.

**Trạng thái hiện tại:** năm tài liệu từng thiếu của danh sách đầu và mười mục bổ sung sau đó đều có toàn văn trong thư mục. Hai file Wang–Kolar–Drton đã tách là supplement khoa học 29 trang và biểu mẫu tái lập 5 trang. File Chang–Guo–Malinsky là bản tác giả, chưa xác minh là PDF typeset Biometrika. Các đoạn bên dưới là nhật ký tải ban đầu, không phải trạng thái hiện tại.

## Kết quả tìm bổ sung ba tài liệu còn thiếu

**Thử riêng Zhang bằng trình duyệt và phương án OCR:** đã chạy Chrome cài sẵn qua Playwright, mở trang nhà xuất bản và chụp ảnh. Chrome nhận HTTP 403, mã `CPE00001`; ảnh chỉ chứa trang lỗi, không có trang bài báo để OCR. Đã kiểm tra thêm OpenAlex, đường dẫn từ nhóm đọc tại Đại học Amsterdam và API Elsevier; chưa lấy được toàn văn. Vì vậy `Zhang_2008_Complete_Orientation_Rules.pdf` vẫn chưa tồn tại. Chi tiết được ghi trong trường `zhang_browser_followup` của manifest.

**Chưa tải thêm được PDF toàn văn trong lần tìm bổ sung.** Ba mục vẫn thiếu trên máy, nhưng đã tìm được các đầu mối cụ thể hơn:

- **Triantafillou et al. 2014:** xác minh bản do Ioannis Tsamardinos đăng trên ResearchGate, đủ **16 trang**, đúng tiêu đề và tác giả. Công cụ duyệt web đọc được PDF; tải trực tiếp về máy trả HTTP 403. [Mở PDF bản tác giả](https://www.researchgate.net/profile/Ioannis-Tsamardinos/publication/266379149_Learning_Neighborhoods_of_High_Confidence_in_Constraint-Based_Causal_Discovery/links/542e56c80cf29bbc126f0c14/Learning-Neighborhoods-of-High-Confidence-in-Constraint-Based-Causal-Discovery.pdf). Nếu tải bằng trình duyệt được, lưu thành `Triantafillou_et_al_2014_High_Confidence.pdf`.
- **Zhang 2008:** [metadata chính thức Elsevier](https://api.elsevier.com/content/article/pii/S0004370208001008?httpAccept=text/xml) xác nhận `openaccessArticle=true` và `openArchiveArticle=true`. [Liên kết PDF ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0004370208001008/pdf) trả HTTP 403 và yêu cầu xác minh người dùng; đây là trở ngại kỹ thuật, không phải bằng chứng bài bị paywall. Lưu phản hồi metadata tại `Zhang_2008_publisher_metadata.xml` (?? d?n), **không phải toàn văn**. Tên PDF dự kiến: `Zhang_2008_Complete_Orientation_Rules.pdf`.
- **Silvapulle–Sen 2005:** tìm thấy [bản scan đúng sách trên Internet Archive](https://archive.org/details/constrainedstati0000silv). [Metadata của kho](https://archive.org/metadata/constrainedstati0000silv) ghi `access-restricted-item=true`, PDF toàn văn là private; chưa tải được sách. Wiley và các đường dẫn sample đã thử cũng không cung cấp được PDF trong môi trường này. Tên PDF dự kiến: `Silvapulle_Sen_2005_Constrained_Statistical_Inference.pdf`.

Đã lưu ba shortcut `.url` trong thư mục này để mở các nguồn trên bằng trình duyệt. Việc trình duyệt cá nhân có tải được hay không **chưa xác minh**. Nhật ký bổ sung: `download_followup_attempts.json` (?? d?n). Không dùng trang metadata, bản xem thử hoặc tài liệu khác để thay thế ba toàn văn được yêu cầu.

Đã lưu **13 PDF mới và 1 ZIP supplement**: có bản toàn văn cho 11/14 mục được yêu cầu (trong đó Berger và Olkin–Finn là technical report), thêm supplement ACI và bản xuất bản JMLR của RICF. **Còn thiếu toàn văn 3 mục:** Triantafillou et al. 2014, Zhang 2008, Silvapulle–Sen 2005. Không ghi đè các PDF đã có.

Phạm vi kiểm tra: xác minh thư mục, nguồn và phiên bản; mở PDF, kiểm tra số trang và nội dung nhận dạng. Đây không phải báo cáo đọc sâu, thẩm định định lý hay đối chiếu từng dòng giữa preprint và bản journal. Các trạng thái dưới đây là **[Verified]** về việc tải/nhận dạng; tính đồng nhất giữa các phiên bản chưa được kiểm chứng.

## Nhóm A

| Mục | Thông tin xác minh và nguồn | File / trạng thái |
|---|---|---|
| A1 | **Ancestral Causal Inference** — Sara Magliacane, Tom Claassen, Joris M. Mooij. NIPS 2016, Advances in Neural Information Processing Systems 29. [Proceedings chính thức](https://proceedings.neurips.cc/paper_files/paper/2016/hash/f3d9de86462c28781cbe5c47ef22c3e5-Abstract.html). | [Paper](ACI_2016.pdf), 9 trang; [supplement](ACI_2016_supplement_supplementary.pdf), 13 trang. ZIP gốc đã dọn sau khi đối chiếu nội dung. |
| A2 | **Ancestral Graph Markov Models** — Thomas Richardson, Peter Spirtes. Annals of Statistics 30(4), 962–1030 (2002). DOI: [10.1214/aos/1031689015](https://doi.org/10.1214/aos/1031689015). PDF từ [trang Spirtes tại CMU](https://www.cmu.edu/dietrich/philosophy/docs/spirtes/annals2002.pdf). | [PDF](Richardson_Spirtes_2002_Ancestral_Graph_Markov_Models.pdf), 69 trang, bản journal. |
| A3 | **Learning Neighborhoods of High Confidence in Constraint-Based Causal Discovery** — Sofia Triantafillou, Ioannis Tsamardinos, Anna Roumpelaki. PGM 2014, LNCS 8754, 487–502. [Springer / DOI 10.1007/978-3-319-11433-0_32](https://link.springer.com/chapter/10.1007/978-3-319-11433-0_32). | **Chưa tải được PDF toàn văn.** Springer hiển thị yêu cầu quyền truy cập; thử URL PDF không nhận được PDF. [Bản tác giả trên Academia](https://www.academia.edu/10033037/Triantafillou_pgm_2014) được tìm thấy nhưng tải trực tiếp trả 403. ResearchGate trả 403; nguồn FORTH không truy cập ổn định. |
| A4 | **On the completeness of orientation rules for causal discovery in the presence of latent confounders and selection bias** — Jiji Zhang. Artificial Intelligence 172(16–17), 1873–1896 (2008). [DOI 10.1016/j.artint.2008.08.001](https://doi.org/10.1016/j.artint.2008.08.001); [kho Lingnan](https://commons.ln.edu.hk/sw_master/732/). | **Chưa tải được PDF.** ScienceDirect liệt kê Open archive nhưng các URL tải trả 403 trong môi trường này. Lingnan chỉ liên kết đến publisher; Caltech là metadata-only. Không kết luận bài này không có open access. |
| A5 | **The Price of Valid Inference After Causal Discovery** — **Dongxin Guo, Jikun Wu, Siu Ming Yiu**. UAI 2026, PMLR 337, 1804–1822. [Proceedings chính thức](https://proceedings.mlr.press/v337/guo26a.html). | [PDF](Guo_Wu_Yiu_2026_Price_Valid_Inference.pdf), 19 trang, lấy từ kho mlresearch được proceedings liên kết. |

## Nhóm B

| Mục | Thông tin xác minh và nguồn | File / trạng thái |
|---|---|---|
| B1 | **The Hardness of Conditional Independence Testing and the Generalised Covariance Measure** — Rajen D. Shah, Jonas Peters. Annals of Statistics 48(3), 1514–1538 (2020), DOI [10.1214/19-AOS1857](https://doi.org/10.1214/19-AOS1857). [arXiv 1804.07203](https://arxiv.org/abs/1804.07203). | [PDF arXiv](Shah_Peters_GCM_arxiv.pdf), 46 trang; trang đầu đề **25/03/2022**. Đây là bản arXiv cập nhật, không gắn nhãn nhầm là PDF typeset 2020. |
| B2 | **Correlations Redux** — Ingram Olkin, Jeremy D. Finn. Psychological Bulletin 118(1), 155–164 (1995), DOI [10.1037/0033-2909.118.1.155](https://doi.org/10.1037/0033-2909.118.1.155). [Hồ sơ tại đại học của Finn](https://researchconnect.buffalo.edu/en/publications/correlations-redux/). [Stanford technical report](https://statistics.stanford.edu/technical-reports/correlations-redux). | [PDF technical report](Olkin_Finn_1994_Correlations_Redux_Technical_Report.pdf), 24 trang, **Report 299, tháng 8/1994**. Chưa tải bản journal 1995; chưa đối chiếu tính đồng nhất hoặc xác nhận công thức cụ thể phù hợp với mọi partial correlation cần cho P5. |

## Nhóm C

| Mục | Thông tin xác minh và nguồn | File / trạng thái |
|---|---|---|
| C1 | **Constrained Statistical Inference: Inequality, Order, and Shape Restrictions** — Mervyn J. Silvapulle, Pranab K. Sen. Wiley, 2005; ISBN 9780471208273; DOI [10.1002/9781118165614](https://onlinelibrary.wiley.com/doi/book/10.1002/9781118165614). [Hồ sơ tác giả tại Monash](https://research.monash.edu/en/publications/constrained-statistical-inference-inequality-order-and-shape-rest/) xác nhận 2005. | **Chưa tải được toàn bộ sách.** URL Wiley và cả các URL thử cho front matter / sample chapter trả 403. Trang Wiley có trường “First published” 2001 không nhất quán với copyright 2005 và hồ sơ Monash; giữ năm 2005, ghi nhận bất nhất metadata. |
| C2 | **Asymptotic distribution of test statistics in the analysis of moment structures under inequality constraints** — Alexander Shapiro. Biometrika 72(1), 133–144 (1985), DOI [10.1093/biomet/72.1.133](https://doi.org/10.1093/biomet/72.1.133). [Trang tác giả tại Georgia Tech](https://sites.gatech.edu/alexander-shapiro/publications/). | [PDF](Shapiro_1985_Inequality_Constraints.pdf), 12 trang, scan bản journal. Đã xem ảnh trang đầu để xác minh vì không có text layer hữu ích. |
| C3 | **Multiparameter Hypothesis Testing and Acceptance Sampling** — Roger L. Berger. Technometrics 24(4), 295–300 (1982), DOI [10.1080/00401706.1982.10487790](https://doi.org/10.1080/00401706.1982.10487790). | [PDF technical report](Berger_1980_M555_Technical_Report.pdf), 14 trang, **FSU Statistics Report M555 / USARO D48, tháng 7/1980**, DTIC ADA091607. Tải [bản lưu DTIC trên Internet Archive](https://archive.org/download/DTIC_ADA091607/DTIC_ADA091607.pdf). Đã xem ảnh trang tiêu đề. **Chưa có bản journal 1982**, chưa đối chiếu hai phiên bản. |
| C4 | **Likelihood ratio tests and singularities** — Mathias Drton. Annals of Statistics 37(2), 979–1012 (2009), DOI [10.1214/07-AOS571](https://doi.org/10.1214/07-AOS571). [arXiv math/0703360](https://arxiv.org/abs/math/0703360). | [PDF](Drton_2009_Likelihood_Ratio_Tests_Singularities.pdf), 35 trang; arXiv v3 ngày 02/04/2009, có thông tin journal trên trang đầu. |

## Nhóm D

| Mục | Thông tin xác minh và nguồn | File / trạng thái |
|---|---|---|
| D1 | **Ancestor Relations in the Presence of Unobserved Variables** — Pekka Parviainen, Mikko Koivisto. ECML PKDD 2011, Part II, LNCS 6912, 581–596. [DOI 10.1007/978-3-642-23783-6_37](https://doi.org/10.1007/978-3-642-23783-6_37). | [PDF](Parviainen_Koivisto_2011_Ancestor_Relations.pdf), 16 trang, tải từ Springer. Link KTH cũ trả 404; đã dùng nguồn publisher thay thế. |
| D2 | **Large-Scale Local Causal Inference of Gene Regulatory Relationships** — **Ioan Gabriel Bucur, Tom Claassen, Tom Heskes**. [arXiv 1909.03818](https://arxiv.org/abs/1909.03818). | [PDF](Bucur_et_al_2019_Local_Causal_Inference.pdf), 32 trang, **v2 ngày 10/09/2019**. Ghi nhận là bản arXiv; không suy diễn venue từ mô tả ban đầu. |
| D3 | **A Bayesian Approach to Constraint Based Causal Inference** — Tom Claassen, Tom Heskes. UAI 2012, 205–214. [Proceedings / PMLR R10](https://proceedings.mlr.press/r10/claassen12a.html). Đây là paper BCCD được yêu cầu. | [PDF](BCCD_Claassen_Heskes_2012.pdf), 10 trang. PMLR ghi tái phát hành 04/10/2026; năm công bố paper vẫn là **2012**, không phải 2026. |

## RICF đã có và bản xuất bản bổ sung

- [File cũ](Computing%20Maximum%20Likelihood%20Estimates%20in%20Recursive.pdf) đúng là arXiv **math/0601631v4, 23/05/2008**, 22 trang. Đã kiểm tra trang đầu trong lần này; giữ nguyên file.
- [File JMLR mới](RICF_Drton_Eichler_Richardson_JMLR_2009.pdf), 20 trang: **Computing Maximum Likelihood Estimates in Recursive Linear Models with Correlated Errors**, Mathias Drton, Michael Eichler, Thomas S. Richardson. **JMLR 10(81), 2329–2348 (2009)**. [PDF chính thức](https://www.jmlr.org/papers/volume10/drton09a/drton09a.pdf).

## Kiểm tra file và phần còn thiếu

Các PDF mới đã được kiểm tra chữ ký `%PDF`, mở bằng PyMuPDF và duyệt các trang; manifest ghi URL, kích thước, số trang và SHA-256. Với các bản scan Shapiro, Berger và Olkin–Finn, đã kiểm tra trực quan trang nhận dạng. ACI supplement được lấy từ ZIP chính thức; bỏ qua metadata `__MACOSX`.

[Manifest tải và kiểm tra](download_manifest_2026-11-04.json) chứa cả lịch sử thử thất bại và danh sách file cuối cùng. Lỗi 403 không đồng nghĩa với paywall; phân biệt lỗi truy cập kỹ thuật với yêu cầu subscription được publisher hiển thị.

Để hoàn tất đúng toàn bộ danh sách cần bổ sung ba toàn văn A3, A4, C1. Nếu cần đúng version of record thay vì technical report thì còn cần Berger 1982 và Olkin–Finn 1995. Các bản report hiện có không được mặc nhiên coi là giống hoàn toàn bản journal.
