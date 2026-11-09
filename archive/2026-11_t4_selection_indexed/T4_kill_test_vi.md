# T4 kill test: transport theo proof và cơ chế lift bằng chỉ báo thiếu

> Ngày 2026-11-06. Script: `T4_oracle_checks.py`, `T4_lift_checks.py`. Số: `T4_oracle_outputs.json`, `T4_lift_outputs.json`. Log: `T4_oracle_run_log.txt`, `T4_lift_run_log.txt`.
> **Phạm vi bằng chứng:** oracle d-separation trên đồ thị nhỏ (p ≤ 7) và mô phỏng mức một bộ ba biến, tuyến tính Gauss. **Chưa có** pilot mức thuật toán FCI, chưa có dữ liệu thật. Toàn bộ chứng minh trong báo cáo này chưa được người hay agent độc lập rà soát.

## 1. Kết luận

| Câu hỏi | Kết quả | Nhãn |
|---|---|---|
| Có thể giữ đúng target của M1 bằng luật cục bộ chỉ dùng CI giữa các biến O không? | **Không** (K1). Có cặp DAG giống nhau ở mọi regime không chứa T nhưng khác target listwise | Đã chứng minh bằng phản ví dụ, kiểm tra số |
| Luật định hướng theo regime có đúng không? | **Có** (K2). R0, R1, R4 không có vi phạm; bản ghép ngây thơ sinh claim sai | Có chứng minh ngắn, kiểm tra oracle |
| Regime-indexed FCI có thêm claim đúng so với listwise không? | **Có** (K3), PP/LWu ≥ 1.10 ở 21/24 ô MNAR, tối đa 2.32 | Oracle, cận trên |
| Phần thêm đó có đến từ máy định hướng không? | **Phần lớn không.** Đa số đến từ các phép tách đơn giản (SepOnly). Phần vượt SepOnly đạt ≥ 1.10 ở 8/16 ô khi chạy lại, và cả 8 ô đều là đồ thị dày (K6) | Oracle |
| Lift bằng chỉ báo có giảm định hướng sai ở finite sample không? | **Có trong họ cộng tính** (K7: positive, 23/23 ô). **Thất bại nặng ở họ tương tác** với mô hình chỉ báo chính hiệu ứng (K7: fragile, vượt tới +0.97) | Mô phỏng do tôi thiết kế, mức truy vấn |

**Khuyến nghị [Inference]:**
- **NO-GO** cho T4 theo card gốc ("giữ đúng target với ít recheck nhất"), nếu chỉ dùng truy vấn giữa các biến O.
- **Không nên** lấy regime-indexed FCI làm đóng góp trung tâm: bổ đề đơn giản, phần lợi chính chỉ cần phép tách.
- **GO có điều kiện** cho một hướng hẹp hơn, tạm gọi **T4-L**: thay bước xác nhận CI trực tiếp bằng kiểm định chỉ báo. Chỉ đi tiếp sau khi audit văn liệu thêm và pilot mức thuật toán (§8). Đây chưa phải cam kết xây phương pháp đầy đủ.

**Điểm yếu lớn nhất của T4-L:** toán lõi **không mới** (§6), họ thuận lợi do tôi chọn, và theo luật khai báo trước thì cơ chế **phụ thuộc vào việc đặc tả đúng mô hình chỉ báo**.

## 2. Đính chính so với các tài liệu trước

- **Card T4 và M1 §10.1.** Card ghi failure đã được xác minh ở mức ví dụ. Khi đọc toàn văn M1, Appendix 10.1 chỉ giải thích vì sao R1 có thể hỏng với heuristic test-wise deletion; **không có đồ thị phản ví dụ tường minh**. Phản ví dụ trong báo cáo này do tôi tự dựng (§4).
- **Mục tiêu "giữ đúng target" của card T4 và card C2** không đạt được nếu chỉ dùng truy vấn giữa biến O. Tôi không sửa card C2 vì nó thuộc phiên làm việc song song.
- **Phép đo ban đầu của tôi bị lệch.** Lần quick-run đầu so PP với LW cho tỉ lệ > 1 ngay cả khi q = 0, nơi mọi regime cho cùng kết quả CI nên không thể có lợi thật. Lý do: PP đọc claim từ nhiều PAG con, LW từ một PAG. Tôi đã thêm đối chứng LWu và K5 **trước lần chạy đầy đủ**. Thay đổi được ghi trong docstring. Sau khi sửa, PP = LWu trên mọi đồ thị q = 0.

## 3. Mô hình và lý thuyết

**Mô hình.** O là biến quan sát, mỗi O_i có chỉ báo R_i (R_i = 1 khi quan sát được). Regime U ⊆ O là tập hàng đủ U, tức điều kiện trên S_U = S ∪ {R_i : i ∈ U}. Regime O là listwise. Assumption 1 của M1: phần tử của cơ chế thiếu không là tổ tiên của O ∪ S hay của cơ chế khác.

**Lemma A (đơn điệu theo regime; tổng quát hóa M1 Lemma 1).** Với U ⊂ U′: d-connected tại U ⇒ d-connected tại U′.
*Chứng minh.* Lấy đường π d-connecting tại U. Mọi collider vẫn mở khi thêm điều kiện. Một non-collider trên π có đường có hướng tới đầu mút hoặc tới một collider, nên là tổ tiên của O ∪ S ∪ cơ chế. Theo Assumption 1 nó không thể là phần tử của S_U′ \ S_U. ∎

**Luật R0 theo regime.** Xét U ⊇ {X,Y,Z} ∪ W, X ⊥ Y | W tại S_U với W tối thiểu, và X,Z cùng Y,Z phụ thuộc cho (W \ Z) tại một regime con. Khi đó Z ∈ W ⇔ Z ∈ An({X,Y} ∪ S_U).
*Chứng minh.* Lemma A đưa các phụ thuộc lên U, rồi áp dụng Colombo et al. Lemma 3.1 với S := S_U. ∎

**Luật R1 theo regime.** Nếu Z ∉ An(X ∪ S_U1) và Z ∈ An({X,Y} ∪ S_U2) thì Z ∈ An(Y ∪ (S_U2 \ S_U1)). Khi U2 ⊂ U1 kết luận là Z ∈ An(Y) thuần. Suy trực tiếp từ tính chất hợp của An.

**Quy tắc theo proof.** Xác nhận mọi premise tách tại U_proof, là hợp các biến của proof; kết luận đúng tại S_{U_proof}. Với R4 dùng Colombo Lemma 3.2 tương tự. Phần dư phụ thuộc lên regime lớn hơn nhờ Lemma A.

**Claim non-ancestor đọc từ PAG.** Nếu Z là tổ tiên DAG của X, các nút quan sát liên tiếp trên đường có hướng đều kề nhau trong MAG (chỉ báo không có con nên không nằm trên đường), và không có đầu mũi tên ở phía nguồn. Vậy không có đường possibly-directed từ Z đến X nghĩa là Z không phải tổ tiên X, kể cả khi có selection. Tôi dùng điều này cho mọi phương pháp.

## 4. Kết quả oracle

**Phản ví dụ tường minh** (kiểm tra trong phần S, không có FAIL nào):
- *Ghép ngây thơ sai.* O = {x,y,z}: z → x, y cô lập, R_z có cha {y,z}. x ⊥ y | ∅ tại S_xy, y,z phụ thuộc tại S_yz qua R_z, x,z kề. Ghép lại cho v-structure, tức khẳng định z ∉ An(x), **sai**. Listwise không khẳng định điều sai này.
- *Không giữ được target chỉ với truy vấn O.* X → Z ← Y, T cô lập; DAG thứ hai thêm Z → R_T. Mọi truy vấn CI giữa biến O ở regime không chứa T đều giống nhau, nhưng target listwise khác: DAG thứ hai có cạnh X–Y do selection.
- *Kiểm tra một biến thêm là chưa đủ.* X → R_T1 ← L → R_T2 ← Y: X,Y tách ở mọi regime thiếu một trong T1, T2, và phụ thuộc khi có cả hai.

**Kiểm tra số:**

| Mục | Số trường hợp | Vi phạm |
|---|---|---|
| Lemma A, vét cạn p = 3 (12 800 m-DAG) | 139 413 | 0 |
| Lemma A, ngẫu nhiên p = 4 có latent | 243 326 | 0 |
| Đối chứng phá Assumption 1 (phải có vi phạm) | 122 221 | 632 |
| R0 theo regime | 7 819 | 0 |
| R1 theo regime, gồm kết luận thuần khi cùng regime (487) | 2 161 | 0 |
| R4 theo regime (1 021 b1, 404 b2) | 1 425 | 0 |
| R0 ngây thơ: claim thuần sai | 1 761 | **395** |
| R1 ngây thơ: claim thuần sai | 1 674 | **457** |
| R4 ngây thơ: claim thuần sai | 1 610 | **16** |

**Headroom** (số claim đúng trung bình mỗi đồ thị; FCI vét cạn với R0–R4, không có R5–R10, cùng máy cho mọi phương pháp):
- **LW** = FCI tại regime O, là output oracle của M1 Algorithm 1 (M1 Theorem 1).
- **LWu** = hợp FCI trên mọi tập con biến, mọi truy vấn ở regime O.
- **SepOnly** = LWu cộng các claim không cần luật định hướng: một phép tách ở regime nhỏ nhất cho "không có cạnh trực tiếp", tách biên cho "không phải tổ tiên" hai chiều.
- **PP** = hợp FCI theo mọi regime. Đây là **cận trên oracle, 2^p regime, chưa tính đa kiểm định**.
- **Naive** = test-wise không xác nhận, có claim sai.

| p, mật độ, q (Rc = 0) | N | LWu | SepOnly | PP | Naive | IdealU | PP/LWu | PP/SepOnly |
|---|---|---|---|---|---|---|---|---|
| 4, .5, q = 0 (đối chứng) | 500 | 7.66 | 7.66 | 7.66 | 7.66 | 7.66 | 1.000 | 1.000 |
| 4, .5, q = .1 | 500 | 6.05 | 6.44 | 6.52 | 6.84 | 7.66 | 1.077 | 1.012 |
| 4, .5, q = .3 | 500 | 3.07 | 4.19 | 4.28 | 5.15 | 7.65 | 1.394 | 1.020 |
| 5, .5, q = .1 | 200 | 9.76 | 10.89 | 11.45 | 12.57 | 14.50 | 1.173 | 1.050 |
| 5, .5, q = .3 | 200 | 3.31 | 5.42 | 5.61 | 7.79 | 13.65 | 1.692 | 1.035 |
| 6, .5, q = .1 | 50 | 9.28 | 12.60 | 15.02 | 19.14 | 23.34 | 1.619 | 1.192 |
| 6, .5, q = .3 | 50 | 2.48 | 4.20 | 4.88 | 8.42 | 19.48 | 1.968 | 1.162 |

Chạy lại K6 với N lớn hơn, seed mới (khoảng tin cậy bootstrap 95%, Rc = 0):

| p, mật độ, q | N | SepOnly | PP | PP/SepOnly |
|---|---|---|---|---|
| 6, .3, .1 | 400 | 24.44 | 25.54 | 1.045 [1.036, 1.054] |
| 6, .3, .3 | 400 | 13.47 | 14.16 | 1.051 [1.041, 1.063] |
| 6, .5, .1 | 400 | 12.85 | 14.41 | 1.122 [1.101, 1.146] |
| 6, .5, .3 | 400 | 6.05 | 6.68 | 1.104 [1.081, 1.129] |
| 7, .3, .1 | 100 | 30.52 | 33.12 | 1.085 [1.064, 1.111] |
| 7, .3, .3 | 100 | 17.90 | 19.30 | 1.078 [1.054, 1.107] |
| 7, .5, .1 | 100 | 17.05 | 20.58 | 1.207 [1.157, 1.263] |
| 7, .5, .3 | 100 | 7.05 | 8.13 | 1.153 [1.093, 1.221] |

**Đọc theo luật khai báo trước:**
- **K1:** NO-GO cho "cùng target" với truy vấn O.
- **K2:** đạt. PP, LWu, LW, SepOnly, PP3, IdealU đều 0 claim sai.
- **K3:** "đáng pilot" (21/24 ô MNAR ≥ 1.10).
- **K5:** đạt.
- **K6/K6R:** "K6 đứng vững", 8/16 ô đạt ≥ 1.10 với cận dưới > 1.05, **cả 8 ô đều ở mật độ .5**.

**Đọc thêm [Inference]:**
- Giá trị 1.192 ban đầu giảm còn 1.122 khi tăng N từ 50 lên 400 với seed mới. Số từ N = 50 không đáng tin.
- Tỉ lệ PP/SepOnly có vẻ tăng theo p và mật độ, nhưng chỉ có p ≤ 7 nên không ngoại suy.
- Naive có nhiều claim đúng hơn PP, nhưng có claim sai trên 1052/9000 đồ thị có q > 0 (11.7%).
- PP vẫn xa IdealU khi q lớn: chỉ thu hẹp 3–15% khoảng cách ở q = .6. Regime không cứu được khi cơ chế thiếu dày.
- Phần lớn claim listwise lấy được ở regime nhỏ (|U| nhỏ nhất trung bình 2.1–3.9 khi q ≤ .3). Đây là lợi thế về số hàng nhưng chưa đo được ở finite sample. M1 báo cáo test-wise chỉ giữ thêm 8.96% mẫu trên mỗi CI trong cohort 1514 của họ, nên lợi thế hàng có thể nhỏ trong thực tế.

**Mối đe dọa novelty (K4).** PP về bản chất là FCI listwise trên tập con U (biến còn lại là latent) rồi ghép claim. Nếu biết m-graph, mọi thứ quy về m-separation chuẩn. Tôi không xem đây là cơ chế mới.

## 5. Cơ chế lift

**Quan sát.** Phản ví dụ "cùng target" chỉ đúng với truy vấn O. Chỉ báo R_j **luôn quan sát được**. Trên các hàng đủ U, ta có x, y, W và mọi R_j với j ∉ U.

**Mệnh đề L (chiều đủ).** Đặt R* = 1 khi mọi biến trong U′ \ U đều quan sát được. Nếu trên các hàng đủ U có x ⊥ y | W và x ⊥ R* | y, W thì x ⊥ y | W trên các hàng đủ U′.
*Chứng minh.* P(x | y, W, U, R* = 1) = P(x | y, W, U) = P(x | W, U). Lấy trung bình theo y trong R* = 1 được P(x | W, U, R* = 1) = P(x | W, U). Hai vế bằng nhau nên có độc lập. ∎ Chiều này không cần faithfulness hay Assumption 1, và đối xứng khi đổi vai x, y.

**Chiều ngược (một chỉ báo, cần faithfulness trên cả chỉ báo):** với x ⊥ y | W tại U, thì x ⊥ y | W tại U+j ⇔ R_j ⊥ x | y,W,S_U hoặc R_j ⊥ y | x,W,S_U. Lập luận bằng weak transitivity và contraction.

**Kiểm tra oracle:** L1 (70 428 trường hợp) và L2 (52 392) đều 0 vi phạm, không có chứng nhận sai nào. Một chứng nhận gộp từ regime nhỏ nhất phủ 94–97% các phép tách listwise; phần còn lại cần chuỗi nhiều bước hoặc test trực tiếp.

**Giả thuyết về power và kiểm tra tay.** Xét họ A: z → x (hệ số β), y cô lập, logit P(R_z = 1) = b(y + z), a = 0, b nhỏ. Khai triển expit quanh 0 [Inference, tính tay]:
- Corr(x, y | R_z = 1) ≈ −βb²/4: **bậc hai** theo b.
- Corr(R_z, x) ≈ βb/2: **bậc nhất** theo b.
- Với hàng đủ xy gấp đôi hàng đủ xyz, tỉ số noncentrality của test chỉ báo so với test trực tiếp ≈ **8/b²**, không phụ thuộc β.

Đối chiếu với bảng ở §6: ở b = .5, n = 5000 công thức cho power test trực tiếp 0.24, bảng ngụ ý 0.21, khớp. Từ b ≥ 1 công thức **ước lượng quá cao** power trực tiếp (b = 1, n = 2000: 0.89 so với 0.47), nên đây chỉ là lập luận cho b nhỏ, không phải định lý.

**Vì sao họ D hỏng, cùng lập luận:** với logit = b·y·z, Corr(x, y | R_z = 1) ≈ βb/2 là bậc nhất, còn Cov(R_z, x) và Cov(R_z, y) bằng 0 ở bậc nhất do đối xứng. Test chính hiệu ứng mù; số hạng xy trong mô hình chỉ báo có Cov ≈ βb/4 nên lại thấy được. Thứ tự bậc **đảo chiều theo dạng cơ chế thiếu**.

## 6. Mô phỏng mức truy vấn

Thiết lập: x, y MCAR 20%, năm biến phụ MCAR 15% xác định hàng listwise, α = .05, 400 replicate mỗi ô (SE tối đa ≈ .025), 32 ô mỗi họ. Mọi quy tắc đều cần dep(x,z), dep(y,z) và sep(x,y) trên hàng tương ứng, rồi khác nhau ở bước xác nhận:
- **PerProof:** test lại x,y trên hàng đủ xyz.
- **M1global:** test lại trên hàng listwise (Algorithm 1 áp cho truy vấn này).
- **Lift1, Lift2:** điểm số logistic trên hàng đủ xy; Lift1 chính hiệu ứng, Lift2 thêm bình phương và tích xy.
- **LiftG:** như Lift1 với R* gồm cả năm biến phụ, cùng target với M1global.

Bảng là tỉ lệ khẳng định v-structure.

**Họ A: khẳng định SAI** (z → x, y cô lập, f = b(y + z)):

| a, b, n | Naive | PerProof | M1global | Lift1 | Lift2 | LiftG |
|---|---|---|---|---|---|---|
| 0, .5, 1000 | .188 | .163 | .175 | .022 | .045 | .125 |
| 0, .5, 5000 | .620 | .492 | .520 | .000 | .000 | .040 |
| 0, 1, 1000 | .820 | .583 | .700 | .000 | .003 | .203 |
| 0, 1, 5000 | .955 | .160 | .532 | .000 | .000 | .000 |
| 0, 1.5, 500 | .850 | .590 | .718 | .007 | .020 | .347 |
| −1.5, 1, 2000 | .848 | .590 | .690 | .000 | .000 | .035 |
| −1.5, 1.5, 1000 | .945 | .603 | .767 | .000 | .003 | .083 |
| −1.5, .5, 500 | .052 | .043 | .043 | .043 | .045 | .048 |

Trên toàn họ A: Lift1 tối đa .048, Lift2 tối đa .090, M1global tối đa .768. LiftG ≤ M1global ở 31/32 ô. Tỉ lệ sai của PerProof và M1global **tăng rồi giảm theo n**: có một cửa sổ mà test-wise đã thấy phụ thuộc y–z nhưng test xác nhận chưa đủ power. Đây là failure mode finite-sample của chính bước xác nhận, ở mô hình này.

**Họ B: khẳng định ĐÚNG, tách vẫn giữ** (x → z ← y, f = b·y). Mọi quy tắc gần nhau, PerProof .880–.940, Lift1 .882–.932. Lift1 − PerProof thấp nhất −.028; Lift2 − PerProof thấp nhất −.032.

**Họ C: DAG đúng nhưng target regime không cho định hướng** (x → z ← y, f = b(x + y)). Lift1 về 0 gần như ngay (.015 ở a = 0, b = .5, n = 500) trong khi PerProof vẫn .875, Naive .950. **Đây là cái giá thật:** lift tới giới hạn tiệm cận sớm hơn, nên cũng mất định hướng đúng sớm hơn. Trong họ này, không xác nhận gì lại "đúng" vì may, nhưng không có quy tắc nào được phép khẳng định theo target.

**Họ D: khẳng định SAI, đối nghịch với mô hình chính hiệu ứng** (f = b·y·z):

| a, b, n | Naive | PerProof | M1global | Lift1 | Lift2 | LiftG |
|---|---|---|---|---|---|---|
| 0, .5, 500 | .895 | .623 | .772 | .892 | .675 | .892 |
| 0, 1, 1000 | .948 | .092 | .420 | .948 | .030 | .945 |
| 0, 1, 5000 | .958 | .000 | .000 | .955 | .000 | .953 |
| −1.5, .5, 500 | .848 | .573 | .708 | .843 | .677 | .845 |
| −1.5, .5, 1000 | .932 | .495 | .700 | .927 | .585 | .922 |
| −1.5, .5, 2000 | .938 | .158 | .485 | .932 | .233 | .935 |

Lift1 và LiftG **gần bằng Naive ở mọi ô**, không tự sửa khi n tăng. Lift2 tốt hơn PerProof ở một số ô và kém hơn PerProof quá .02 ở 5/32 ô, đều ở n nhỏ hoặc b = .5, nặng nhất +.105.

**Họ E (mô tả, không tính vào luật):** f = b·sin(3y)·z. Mọi phương pháp đều gần như mù, sai .03–.18, và tỉ lệ sai có xu hướng tăng theo n ở b lớn. Lift1 kém PerProof tối đa khoảng +.04. Đây là giới hạn chung của test tuyến tính.

**Đọc K7 theo luật khai báo trước:**

| Luật | Kết quả |
|---|---|
| Lift1 ở họ A, B | **Positive**: 23/23 ô có PerProof ≥ .10 đều giảm ít nhất một nửa; họ B đạt |
| Lift1 ở họ D | **Fragile**: vượt PerProof tới +.97 |
| Lift2 ở họ A, B | **Không đạt Positive**: họ A đạt (22/23), họ B thấp hơn PerProof .0325 so với dung sai .03, sát SE |
| Lift2 ở họ D | **Không đạt** dung sai .02 (+.105) |
| Hệ quả theo luật | **Cơ chế được báo cáo là phụ thuộc vào mô hình chỉ báo đúng** |

Lift2 trượt họ B với khoảng cách nhỏ hơn nhiễu mô phỏng, nhưng tôi giữ nguyên luật. Tỉ lệ vượt ở họ D thì có thật, không phải nhiễu.

**Không đọc quá mức các bảng này:**
- Đây là một bộ ba biến, W = ∅, không phải FCI đầy đủ. Không có lan truyền lỗi, không có đa kiểm định.
- Dữ liệu tuyến tính Gauss, cơ chế logit do tôi chọn; họ A thuận lợi cho lift và tôi đã biết điều đó trước khi chạy.
- Lần code-test (40 replicate, 2 giá trị n) cho tôi thấy số trước khi chốt lần chạy đầy đủ. Sau đó tôi chỉ thêm họ E mô tả, không đổi ngưỡng.
- Không so với MVPC, MI-FCI, hay FCI có chỉ báo làm biến. Baseline mạnh nhất **chưa được thử**.

## 7. Prior art và novelty

| Nguồn | Nội dung liên quan | Trạng thái kiểm tra | Hệ quả |
|---|---|---|---|
| [M1, Strobl et al. 2018](https://arxiv.org/pdf/1705.09031) | Lemma 1 (đơn điệu), Algorithm 1, Theorem 1 | Đọc toàn văn | Lemma A chỉ là khái quát trực tiếp |
| [Witte et al.](https://arxiv.org/abs/2108.13331) (Lemma 6, Prop 2) | X ⊥ Y \| (Z, R_XYZ = 1) ⇔ R_XYZ ⊥ X \| (Y,Z) hoặc R_XYZ ⊥ Y \| (X,Z), dùng weak transitivity, contraction | Đọc đoạn liên quan | **Chiều ngược của tôi là bản chuyển vị của lemma này**, trong khung PC. Họ nói điều kiện *không kiểm chứng được thực nghiệm*, vì R_XYZ chứa chỉ báo của chính biến được test |
| Didelez et al. 2010, Theorem 6 | Witte nêu lemma trên dựa vào đây | **Chỉ qua Witte**, chưa đọc gốc | Nguồn gốc collapsibility |
| [Mohan & Pearl 2014](http://proceedings.mlr.press/v33/mohan14.pdf), Theorem 1 | Tiêu chí d-separation kiểm tra trực tiếp được | Đọc định nghĩa và định lý | Tính kiểm tra được của phép test chỉ báo **đã có** |
| [Tu et al. 2019](https://proceedings.mlr.press/v89/tu19a/tu19a.pdf) (MVPC) | Prop 1 (CI test-wise ⇒ CI thật); phát hiện cha của chỉ báo để chọn hiệu chỉnh; giả định đủ nhân quả, không self-masking | Đọc các đoạn liên quan | Cùng dùng phép test R–V, nhưng để hiệu chỉnh chứ không để xác nhận. SepOnly chủ yếu là hệ quả của Prop 1 |
| [JCI](https://arxiv.org/pdf/1611.10351) §4.3.3 | IOD là phương pháp đa dataset duy nhất nêu rõ xử lý selection, giả định mọi context là marginal của một MAG chung | Đọc đoạn đó; IOD chỉ qua mô tả của JCI | Đe dọa cho phần ghép regime |
| [Gain & Shpitser 2018](https://proceedings.mlr.press/v72/gain18a/gain18a.pdf) | Phương pháp reweighting; tính đúng khi m-graph chưa biết là vấn đề mở | Đọc §3.4 | Hướng khác, cần baseline |
| [PAIR-CI (preprint 2026)](https://arxiv.org/pdf/2605.04838) | CI test dựa imputation, gắn vào PC | Đọc tóm tắt, quét từ khóa | Hướng khác; FCI chỉ được nhắc là khả năng |

**Chưa đọc, phải đọc trước khi tuyên bố gì:** [bài OpenReview về missing values](https://openreview.net/pdf?id=ouMvHDxAFQ) (tải về chỉ được HTML), [survey CI test 2026](https://arxiv.org/pdf/2608.11156), IOD gốc, Didelez toàn văn, [COmbINE](https://arxiv.org/pdf/1403.2150), [fedCI-IOD](https://arxiv.org/pdf/2603.05149), [tiered overlapping datasets](https://arxiv.org/pdf/2503.21526) (các bài sau mới được đọc lướt).

**Tách bạch:**
- **[Verified]** Các lemma trong bảng có trong nguồn đã nêu. Các số của tôi có trong file đầu ra.
- **[Inference]** Toán lõi của lift là collapsibility và đã biết. Điểm khác so với Witte: khi chỉ báo thuộc các biến **ngoài** phát biểu CI thì phép test kiểm tra được.
- **[Hypothesis]** Đóng góp có thể nằm ở việc dùng phép test này làm bước xác nhận trong FCI dưới MNAR có latent, kèm lập luận về bậc hiệu ứng và điều kiện nó đảo chiều.
- **[Unresolved]** Có ai đã làm đúng việc này chưa. Tìm kiếm của tôi chưa thấy, đó **chỉ là bằng chứng tìm kiếm, không phải bằng chứng về gap**.

## 8. Điều kiện đi tiếp cho T4-L

**Bước 1, audit văn liệu** (rẻ). No-go nếu có công trình đã dùng phép test chỉ báo làm bước xác nhận CI, hoặc phân tích power tương tự, trong constraint-based discovery.

**Bước 2, pilot mức thuật toán**, viết luật trước khi chạy.
- *So sánh:* M1 Algorithm 1, listwise FCI, naive test-wise, Lift-FCI với mô hình chỉ báo linh hoạt.
- *Baseline phải thử:* FCI có chỉ báo làm biến (đối thủ đơn giản nhất), MI-FCI theo Witte, MVPC trên tầng đủ nhân quả không self-masking. Giữ nguyên giả định, ngân sách, output, metric.
- *Lưới:* p ∈ {10, 20}, có latent, cơ chế thiếu cộng tính, tương tác và phi tuyến; **trộn các dạng trong cùng một đồ thị** thay vì chọn dạng thuận lợi.
- *Metric:* false endpoint và ancestry assertion so với DAG thật, số claim đúng giữ lại, số CI test.

*Đề xuất ngưỡng (lựa chọn quản lý dự án, cần bạn chốt):*
- **Go:** ở cơ chế trộn, Lift-FCI giảm false assertion ≥ 30% so với M1 Algorithm 1, giữ ≥ 90% số claim đúng của M1, và hơn cả baseline đơn giản nhất.
- **No-go:** chênh lệch biến mất với chỉ báo linh hoạt, hoặc FCI có chỉ báo làm biến đạt tương đương.

**Câu hỏi khoa học cần trả lời ở mức đó:** mất định hướng đúng ở họ C có lớn hơn lợi ích ở họ A không, khi cơ chế trộn lẫn và không biết trước? Nếu không có lời giải, T4-L chỉ là một đánh đổi khác trên cùng đường cong sai–bỏ sót.

**Nếu bước 1 hoặc 2 thất bại:** phần đã có đủ cho một ghi chú ngắn về failure mode của bước xác nhận, chưa đủ cho bài phương pháp. Khi đó nên quay lại tìm ứng viên mới, vì **hiện chưa có backup**.

## 9. Giới hạn và minh bạch

- FCI tự viết (R0–R4, tách vét cạn), không phải thư viện. Các đối chứng (K5, phá Assumption 1, 0 claim sai) ủng hộ tính đúng nhưng chưa đối chiếu với bản FCI độc lập.
- Sinh đồ thị do tôi chọn (phân phối cha của chỉ báo theo q, mỗi chỉ báo độc lập). Headroom phụ thuộc phân phối này.
- Luật K3, K5, K6, K7 được đặt hoặc sửa sau quick-run, như ghi trong docstring. Giá trị ngưỡng của K3 không đổi; K5, K6 thêm trước lần chạy đầy đủ nhưng sau khi tôi đã thấy các con số quick-run của K3. **Luật K6R được viết sau khi đã thấy toàn bộ kết quả H**, gồm giá trị 1.192; nó dùng seed mới nên số là mới, nhưng ngưỡng không hoàn toàn độc lập với kết quả cũ. Luật K7 được viết trước khi có số lift nào, nhưng ý tưởng lift nảy sinh sau khi xem kết quả H.
- Oracle không nói về đa kiểm định. PP có 2^p regime, ở finite sample cần chọn họ regime và kiểm soát sai, chưa thiết kế.
- Toàn bộ Mệnh đề L dựa trên kết luận từ **không bác bỏ**, cùng nhược điểm với mọi phương pháp constraint-based.
- Chưa có người hay agent độc lập rà các chứng minh ở §3, §5.

## 10. Đính chính sau audit văn liệu (2026-11-06)

Xem [`T4L_literature_audit_vi.md`](T4L_literature_audit_vi.md). Phần trên giữ nguyên, nhưng cần đọc với các đính chính sau:

- **Mệnh đề L ở §5 là trường hợp đặc biệt của Didelez et al. 2010, Theorem 6**, không phải kết quả riêng. Dòng "chỉ qua Witte" ở §7 đã lỗi thời: tôi đã đọc nguồn gốc.
- **Câu "Không so với ... FCI có chỉ báo làm biến" ở §6 đã lỗi thời ở mức oracle:** baseline này không thay thế được T4-L ở oracle (`T4L_baseline_oracle_check.py`). Ở finite sample vẫn chưa thử.
- **§8 bước 1:** tiêu chí no-go không bị kích hoạt, trong giới hạn của phép sàng lọc, nhưng novelty hẹp hơn: toán, tính testable và dạng test đều đã có.
