# Đại số hóa FCI/ICD dưới nguyên tắc Safety Prior

**Khảo cứu lý thuyết, các phép quy dẫn chính xác và mô hình work–span**

Ngày: 05-10-2026. Phạm vi: khám phá nhân quả dựa trên CI khi có biến ẩn; đầu ra là PAG. Không bao gồm mã triển khai hoặc khuyến nghị kỹ thuật phần mềm.

## Kết luận nghiên cứu

Có thể biểu diễn nhiều thành phần của FCI/ICD bằng đại số ma trận và tensor mà giữ nguyên ngữ nghĩa. Tuy nhiên, ba khẳng định sau **không tương đương**:

1. Một phép toán có biểu diễn tensor chính xác.
2. Biểu diễn ấy có work và bộ nhớ cùng bậc với thuật toán duyệt đồ thị tốt.
3. Toàn bộ thủ tục song song cho cùng PAG, cùng bằng chứng hoặc cùng vết truy vấn với reference.

Kết quả chắc chắn nhất là phép đồng nhất Gaussian CI–Schur complement, biểu diễn điều kiện cục bộ bằng Boolean tensor, và bảo đảm của FCI-stable khi giữ đúng toàn bộ ngữ nghĩa của biến thể này. Đối với Blockwise ICD, định lý cần nhắm tới là **bảo toàn separator coverage và giao hoán của các sự kiện bằng chứng**, thay vì đồng nhất mọi vòng lặp với một phép nhân tensor.

Không có cơ sở từ các nguồn đã kiểm tra để tuyên bố một thành phần của bài toán này *bắt buộc phải chạy trên CPU*. Các giới hạn có thể chứng minh liên quan đến lượng work, bộ nhớ, tính thích nghi và độ sâu phụ thuộc; chúng không phân chia thiết bị thành CPU và GPU.

## 0. Giả thiết, ký hiệu và phạm vi bằng chứng

### 0.1. Những gì lấy từ hồ sơ dự án

Báo cáo dựa trên 11 tài liệu đính kèm, đặc biệt các chương 04, 06, 07 và 09:

- K1 là quyết định `PASS` trên snapshot 131 graph có đủ năm scheduler; 656/800 run đã có. Phạm vi can thiệp là `FAS_STABLE_SKELETON_ONLY`.
- Sprint 0 ghi nhận 0/40 khác biệt PAG cuối nhưng 10/40 khác biệt query trace giữa dynamic và precomputed; ví dụ seed 74304 có 21 so với 25 CI queries.
- Những số này là **kết quả được hồ sơ báo cáo**, không phải kết quả được tái chạy hoặc kiểm chứng độc lập trong nghiên cứu này.
- Chúng không chứng minh nút thắt end-to-end đã được định lượng tại PDS, cũng không chứng minh một phân rã block là đúng. PDS và orientation là các đối tượng cần phân tích tiếp, phù hợp với giới hạn mà hồ sơ đã nêu.

### 0.2. Miền mô hình

Gọi \(P=|V|\) là số biến quan sát, \(n\) là số mẫu, \(L\) là tập biến ẩn. Đối với định lý khám phá cấu trúc, giả sử mô hình DAG nền thỏa causal Markov và faithfulness, với ngữ nghĩa MAG/PAG tương ứng. Các phát biểu oracle dùng CI chính xác. Các phát biểu hữu hạn mẫu được tách riêng.

Đối với phần thống kê, giả sử phân phối của **các biến được kiểm định** là Gaussian không suy biến. Marginalization của Gaussian qua biến ẩn vẫn là Gaussian. Tuy nhiên, lựa chọn mẫu bằng một sự kiện bất kỳ không nhất thiết giữ Gaussian; không được dùng Fisher-Z để bao phủ mọi dạng selection bias chỉ vì FCI có lý thuyết đồ thị cho selection bias.

Phân biệt ba mục tiêu:

\[
\text{query-trace equality},\qquad
\text{evidence-set equality},\qquad
\text{canonical final-PAG equality}.
\]

Không mục tiêu nào trong ba mục tiêu này tự động được suy ra chỉ từ việc CI kernel là chính xác. RFCI còn có mục tiêu yếu hơn FCI trong một số mô hình: Theorem 3.2 của Colombo và cộng sự [2] bảo đảm một **RFCI-PAG**, không bảo đảm luôn bằng complete FCI-PAG.

### 0.3. Cách đọc nhãn chứng cứ

- **[P]**: kết quả đã công bố, có vị trí nguồn cụ thể.
- **[D]**: phép quy dẫn hoặc mệnh đề được suy ra và chứng minh trong báo cáo này; không gán cho tác giả nguồn một định lý tensor/GPU mà họ không phát biểu.
- **[O]**: nghĩa vụ chứng minh còn mở đối với candidate của dự án.

Các nguồn nhân quả chính thuộc JMLR, Annals of Statistics, UAI và NeurIPS. Bài về completeness của Zhang (2008) thuộc *Artificial Intelligence*, đúng bài được yêu cầu. Tarski và Brent là nguồn nền tảng toán học/tính toán ở ngoài danh sách hội nghị ML; chúng không phải bằng chứng rằng FCI đã có một thuật toán tensor hoàn chỉnh.

Từ “đẳng cấu” cần dùng có chọn lọc. Schur complement tạo **đồng nhất đại số**; state lifting tạo **biểu diễn tương đương của chuỗi chuyển trạng thái**; Boolean reachability tạo **quy dẫn quyết định tồn tại**. Chúng không phải tất cả đều là đẳng cấu tuyến tính hay bảo toàn độ phức tạp.

## 1. Bảng đối sánh hình thức

| Thao tác FCI/ICD cổ điển | Cấu trúc đại số tương ứng | Nền tảng và ranh giới khẳng định |
| --- | --- | --- |
| Kiểm định \(X\perp Y\mid S\) trong Gaussian | Phần tử ngoài đường chéo của Schur complement bằng 0; tương đương phần tử precision cục bộ bằng 0 | **[P]** Kalisch–Bühlmann (2007), Proposition 2 và §2.2.2 [1]. **[D]** Đồng nhất block matrix ở §2 dưới đây; bài gốc không phát biểu định lý GPU. |
| Nhiều CI có cùng \(k=\lvert S\rvert\) | Tensor \(B\times(k+2)\times(k+2)\), mỗi lát là một covariance con | **[D]** Áp dụng cùng đồng nhất độc lập theo chỉ số batch; độc lập tính toán không đòi độc lập thống kê giữa các test. |
| CI có kích thước thay đổi | Direct sum với identity; partition theo kích thước hoặc geometric buckets | **[D]** \((C\oplus I)^{-1}=C^{-1}\oplus I\); cận padding <4 lần số ô và <8 lần work bậc ba so với lưu ragged đầy đủ. Không phải miễn phí so với xử lý từng test. |
| Kiểm tra collider hoặc triangle trong PDS | Tensor ba chỉ số \(\Theta_{uvw}\); ma trận chuyển trên trạng thái \((u,v)\) | **[P]** Định nghĩa PDS-path, Rohekar và cộng sự (2021), Definition 2 [4]. **[D]** Lift chính xác cho walk; path không lặp cần điều kiện bổ sung. |
| Reachability hoặc khoảng cách trong đồ thị trạng thái | Boolean semiring hoặc min-plus semiring; closure/powers | **[P]** Zhu và cộng sự (2021), §3.1, Theorem 6 về generalized Bellman–Ford [7]. **[D]** Chuyên biệt hóa sang transition của PAG, với chứng minh quy nạp. Không dùng neural relaxation làm evidence. |
| Điều kiện ICD-Sep | Reachability bị chặn bên trong \(G[\{X\}\cup S]\), kèm mask loại \(Y\), cardinality và điều kiện đường | **[P]** [4], §3.2, Lemma 1, Corollary 1, Lemma 2, Proposition 1. **[D]** Predicate chính xác ở §3.4. Chỉ kiểm tra khoảng cách trong toàn graph là chưa đủ. |
| Đường phân biệt dùng trong R4 | Closure của đồ thị bidirected trên các parent của endpoint cuối; ghép mask ở hai đầu | **[P]** Điều kiện R4 của Zhang [5], đối chiếu Table 1 của Claassen–Heskes [6]. **[D]** Mệnh đề D4 ở §3.5 chứng minh phép quy dẫn, giữ cả nút áp chót cần cho orientation. |
| Xóa cạnh ở một level stable | OR-reduction trên các CI witness từ một candidate family cố định | **[P]** Colombo–Maathuis (2014), Theorems 2–3 cho PC-stable; **§4.4** mới là phần mở rộng FCI-stable [3]. **[D]** Định lý OR của một vòng ở §4.1. |
| Nhiều block đồng thời cập nhật | Các ánh xạ sự kiện giao hoán trên state bao gồm graph, sepset và eligibility | **[D]** Hoán đổi các sự kiện độc lập giữ kết quả. **[O]** Phải xây quan hệ phụ thuộc đủ mạnh cho ICD thực; gần nhau/xa nhau trên skeleton không phải chứng nhận. |
| R1, R2, R3, R6, R7, R8 | Boolean conjunction, existential contraction, masked matrix products | **[P]** Rule semantics của [5], Table 1 của [6]. **[D]** Dịch mệnh đề logic thành tensor là chính xác trên snapshot; không tự chứng minh tính đơn điệu qua mọi snapshot. |
| R5, R9, R10 | Predicate đường uncovered/circle/potentially directed và các phép nối witness | **[P]** [5–6]. **[D]** Có biểu diễn tensor chính xác; cần giữ điều kiện không lặp, first neighbor và cạnh nằm trên witness tùy rule. Không được thay bằng reachability không nhãn. |
| Đóng suy diễn định hướng | Fixed point trên tập facts; hoặc lattice thông tin có trạng thái conflict | **[P]** Zhang [5] bảo đảm completeness của orientation đúng ngữ nghĩa; Tarski (1955), Theorem 1 [9] áp dụng nếu operator monotone trên complete lattice. **[D/O]** Phải chứng minh phép biên dịch thỏa các điều kiện này. LoCI, [6] Theorem 1, là tiền lệ causal logic hoàn chỉnh. |
| Đánh đổi work dư với parallelism | Work–span, \(\max(W/\mu,D)\le T_\mu\le W/\mu+D\) trong mô hình lý tưởng | **[P]** Brent (1974), Lemma 2 [10]. **[D]** Cận speedup theo work inflation ở §7. |

## 2. Gaussian CIT thành batched linear algebra

### 2.1. Mệnh đề D1: phép đồng nhất CI–Schur–precision

Với truy vấn \(q=(x,y,S)\), đặt \(A=(x,y)\), \(k=|S|\), \(d=k+2\). Lấy covariance của **đúng các biến** \(U=A\cup S\):

\[
C_q=\Sigma_{UU}
=\begin{pmatrix}
\Sigma_{AA}&\Sigma_{AS}\\
\Sigma_{SA}&\Sigma_{SS}
\end{pmatrix}\succ0.
\]

Covariance có điều kiện là

\[
R_q=\Sigma_{AA\cdot S}
=\Sigma_{AA}-\Sigma_{AS}\Sigma_{SS}^{-1}\Sigma_{SA}.
\tag{1}
\]

**Chứng minh.** Đặt residual
\(e_A=X_A-\mathbb E[X_A]-\Sigma_{AS}\Sigma_{SS}^{-1}(X_S-\mathbb E[X_S])\).
Nhân khai triển covariance cho \(\operatorname{Cov}(e_A)=R_q\) và \(\operatorname{Cov}(e_A,X_S)=0\). Gaussianity biến tính không tương quan này thành độc lập, nên \(R_q\) chính là covariance của phân phối Gaussian có điều kiện. Hai tọa độ độc lập khi và chỉ khi covariance chéo bằng 0. Do đó

\[
X_x\perp X_y\mid X_S
\iff (R_q)*{12}=0
\iff \rho*{xy\cdot S}=0,
\qquad
\rho_{xy\cdot S}
=\frac{(R_q)*{12}}{\sqrt{(R_q)*{11}(R_q)_{22}}}.
\tag{2}
\]

Nếu \(\Omega_q=C_q^{-1}\), block inverse cho

\[
(\Omega_q)*{AA}=R_q^{-1},\qquad
\rho*{xy\cdot S}
=-\frac{(\Omega_q)*{12}}{\sqrt{(\Omega_q)*{11}(\Omega_q)_{22}}}.
\tag{3}
\]

Dấu trừ trong (3) theo trực tiếp từ nghịch đảo ma trận \(2\times2\). Công thức vẫn đúng ở \(k=0\), với tích qua block rỗng được quy ước bằng 0.

Đây là đồng nhất đại số chính xác. **Không** được thay \(\Omega_q\) bằng submatrix của \(\Sigma^{-1}\) toàn cục: inverse toàn cục tương ứng điều kiện hóa trên toàn bộ biến còn lại, còn truy vấn hiện tại chỉ điều kiện hóa trên \(S\).

### 2.2. Tensor batch và Fisher-Z

Cho \(q_1,\ldots,q_B\) cùng kích thước \(k\):

\[
\mathcal C\in\mathbb R^{B\times d\times d},
\quad \mathcal C_{b,:,:}=\widehat\Sigma_{U_bU_b},
\qquad
\mathcal O_{b,:,:}=(\mathcal C_{b,:,:})^{-1}.
\tag{4}
\]

Phép nghịch đảo chỉ tác động lên hai trục cuối. Một trục dataset/graph độc lập bổ sung cho tensor bốn chiều \(G\times B\times d\times d\); không thay đổi chứng minh theo từng lát.

Lấy \(\widehat\rho_b\) từ (3), rồi

\[
Z_b=\sqrt{n-k_b-3}\;\operatorname{atanh}(\widehat\rho_b)
=\frac{\sqrt{n-k_b-3}}2
\log\frac{1+\widehat\rho_b}{1-\widehat\rho_b}.
\tag{5}
\]

Test hai phía bác bỏ \(H_0:\rho_b=0\) nếu
\(|Z_b|>\Phi^{-1}(1-\alpha/2)\). FCI dùng quyết định không bác bỏ để xử lý như CI, nhưng đó không phải chứng minh độc lập ở hữu hạn mẫu. Chuẩn hóa Fisher là xấp xỉ phân phối; sự đồng nhất của correlation trong (1)–(3) không làm Fisher-Z trở thành kiểm định chuẩn chính xác hữu hạn mẫu. Nền tảng thống kê và dạng ngưỡng nằm trong [1], Proposition 2, §2.2.2.

Các CI trong batch có thể dùng cùng dữ liệu và tương quan mạnh về mặt thống kê. Điều đó không cản trở tính độc lập tính toán của các lát ma trận.

### 2.3. Mệnh đề D2: padding bảo toàn thống kê

Với \(D\ge d\), đặt

\[
\widetilde C_q=C_q\oplus I_{D-d}
=\begin{pmatrix}C_q&0\\0&I\end{pmatrix}.
\tag{6}
\]

Khi đó
\(\widetilde C_q^{-1}=C_q^{-1}\oplus I\), nên hai phần tử diagonal và phần tử off-diagonal dùng trong (3) không đổi. Schur complement cũng không đổi nếu chỉ padding block conditioning bằng các tọa độ identity với cross-covariance bằng 0.

Các tọa độ thêm là thiết bị đại số, không phải biến quan sát mới. Bậc tự do trong (5) vẫn dùng \(k\) thật. Padding bằng hàng/cột toàn 0 tạo ma trận suy biến; một mask áp dụng sau nghịch đảo không sửa được điều đó.

**Cận bộ nhớ.** Với \(Q\) ma trận có kích thước \(d_q\), dung lượng dense ragged là

\[
M_{\rm ragged}=\Theta\!\left(\sum_{q=1}^Qd_q^2\right).
\]

Một tensor chung kích thước \(Q\times P\times P\) cần \(\Theta(QP^2)\) ô. Nếu phần lớn \(d_q=O(1)\), tỷ lệ có thể tăng \(\Theta(P^2)\). Vì vậy không tồn tại bảo đảm “pad tất cả lên \(P\) mà không tăng bậc không gian”.

Hai cách đồng nhất hóa có bảo đảm toán học:

- Partition chính xác theo \(d\): tổng số ô giữ nguyên \(\sum_qd_q^2\).
- Bucket theo \(D_q=2^{\lceil\log_2d_q\rceil}\): vì \(d_q\le D_q<2d_q\),

\[
\sum_qD_q^2<4\sum_qd_q^2,
\qquad
\sum_qD_q^3<8\sum_qd_q^3.
\tag{7}
\]

(7) không tăng **bậc tiệm cận so với việc lưu tất cả ma trận ragged**, nhưng vẫn tăng peak memory so với xử lý một query. Khi chỉ cho \(B_k\) lát cùng hiện diện, workspace ma trận là \(\Theta(B_k(k+2)^2)\); số đợt phải tăng ít nhất theo \(\lceil Q_k/B_k\rceil\). Đây là đánh đổi space–parallelism, không phải mẹo triển khai.

### 2.4. Một đồng nhất khác có thể giảm work

Nếu nhiều query dùng cùng \(S\), đặt \(R=V\setminus S\) và tính

\[
\Sigma_{RR\cdot S}
=\Sigma_{RR}-\Sigma_{RS}\Sigma_{SS}^{-1}\Sigma_{SR}.
\tag{8}
\]

Từ ma trận này có thể đọc correlation có điều kiện của mọi cặp trong \(R\). Với \(r=|R|\), phép đại số cổ điển có work

\[
O(k^3+k^2r+kr^2),
\]

thay vì lặp lại một phân tích block \(S\) cho từng cặp. Đây là phép chia sẻ cấu trúc toán học có khả năng giảm work, nhưng không bảo đảm hữu ích nếu các query có các tập \(S\) khác nhau. Nó cũng không xóa chi phí tìm những tập \(S\) cần kiểm định.

### 2.5. Giới hạn xác định của CI

Covariance mẫu centered có rank tối đa \(n-1\). Với \(d=k+2\), inverse dense thông thường đòi rank đủ; ở mẫu Gaussian không suy biến, điều kiện kích thước cần là \(n\ge k+3\). Công thức Fisher-Z còn đòi \(n-k-3>0\).

Do đó \(k\le P-2\) về mặt đồ thị không đồng nghĩa mọi \(k\) đều kiểm định được bằng Fisher-Z từ dữ liệu hiện có. Pseudoinverse, ridge hoặc covariance shrinkage có thể định nghĩa thủ tục khác, nhưng không tự thừa kế đồng nhất kiểm định và các bảo đảm thống kê của thủ tục chưa regularize.

Các chứng minh đại số dùng số học chính xác. Nếu sai số số học của \(Z\) bị chặn bởi \(\varepsilon\), quyết định được bảo toàn khi khoảng cách đến ngưỡng lớn hơn \(\varepsilon\). Không có margin thì không có bảo đảm bitwise/query-decision equality chỉ từ đồng nhất toán học.

## 3. Đại số đồ thị: từ điều kiện cục bộ đến điều kiện đường đi

### 3.1. Các kênh endpoint

Đặt \(A_{uv}=1\) khi \(u,v\) kề nhau, với \(A=A^T\), \(A_{uu}=0\). Quy ước:

\[
H_{uv}=1\iff\text{đầu tại }v\text{ của cạnh }u-v\text{ là arrowhead};
\]

\(T_{uv}\), \(C_{uv}\) lần lượt chỉ tail và circle **tại chỉ số thứ hai**. Trên cạnh hiện hữu, ba loại endpoint loại trừ nhau. Đặt thêm

\[
N_{uv}=[u\ne v]\land\neg A_{uv},\qquad
D_{uv}=T_{vu}\land H_{uv}.
\tag{9}
\]

\(D_{uv}\) chỉ cạnh \(u\to v\). Các predicate này được xác định từ evidence state, không từ điểm số của prior.

Điều kiện PDS trên một bộ ba phân biệt:

\[
\Theta_{uvw}
=[u,v,w\text{ đôi một khác nhau}]
\land A_{uv}\land A_{vw}
\land\big[(H_{uv}\land H_{wv})\lor A_{uw}\big].
\tag{10}
\]

Hai nhánh cuối chính xác là collider tại \(v\) hoặc triangle. Đây là bản tensor của điều kiện Definition 2 trong [4].

### 3.2. Mệnh đề D3: lift sang Boolean semiring

Xét tập trạng thái cạnh có thứ tự

\[
\mathcal E^{\to}=\{(u,v):A_{uv}=1\},\qquad N_s=|\mathcal E^{\to}|=2m.
\]

Ma trận chuyển là

\[
B_{(u,v),(r,w)}=[r=v]\land\Theta_{uvw}.
\tag{11}
\]

Trên Boolean semiring,

\[
(F\odot G)*{ij}=\bigvee_h(F*{ih}\land G_{hj}).
\tag{12}
\]

Một walk \(v_0,v_1,\ldots,v_\ell\) có mọi bộ ba thỏa (10) tương ứng với chuỗi trạng thái
\((v_0,v_1),(v_1,v_2),\ldots,(v_{\ell-1},v_\ell)\) có mọi transition bằng 1, và ngược lại. **Chứng minh** theo từng transition bằng (11); quy nạp theo số transition cho ý nghĩa của \(B^{\odot t}\).

Với vector bắt đầu \(f_x(u,v)=[u=x]\land A_{uv}\), reachability đến một trạng thái tận cùng tại \(z\) được đọc từ

\[
f_x\odot B^*,\qquad
B^*=I\lor B\lor\cdots\lor B^{\odot(N_s-1)}.
\tag{13}
\]

Nếu query yêu cầu tránh \(y\), bỏ mọi trạng thái chứa \(y\) trước khi tính closure. Nếu chỉ cho tối đa \(\ell\) cạnh ở graph gốc, dùng tối đa \(\ell-1\) transition sau cạnh khởi đầu.

Đổi Boolean thành \((\min,+)\), với chi phí transition bằng 1 và chi phí cạnh bắt đầu bằng 1, cho khoảng cách của các walk chấp nhận được. Tổng quát hóa Bellman–Ford bằng semiring đã được trình bày và chứng minh trong [7]. Ở đây chỉ sử dụng các toán tử exact; phần neural của NBFNet không có bảo đảm semiring tổng quát và không có quyền định hướng cạnh trong Safety Prior.

### 3.3. Walk không tự động là simple path

Một path trong causal graph thường yêu cầu các đỉnh phân biệt. Một chuỗi không lặp **trạng thái** \((u,v)\) vẫn có thể lặp một đỉnh gốc với các predecessor khác nhau. Vì vậy D3 chỉ chứng minh chính xác ngữ nghĩa walk. Không được viện riêng định lý về matrix powers để kết luận đã chứng minh toàn bộ PDS-path hoặc mọi luật uncovered-path.

Có một biểu diễn exact không cần giả thiết bổ sung. Với độ dài \(\ell\), đặt

\[
\begin{aligned}
\mathcal P^{(\ell)}*{v_0,\ldots,v*\ell}
={}&\left(\bigwedge_{i<j}[v_i\ne v_j]\right)
\land\left(\bigwedge_{i=0}^{\ell-1}A_{v_iv_{i+1}}\right)\\
&\land\left(\bigwedge_{i=1}^{\ell-1}
[(H_{v_{i-1}v_i}\land H_{v_{i+1}v_i})\lor A_{v_{i-1}v_{i+1}}]\right).
\end{aligned}
\tag{14}
\]

Mask mọi \(v_i\ne y\), cố định \(v_0=x,v_\ell=z\), rồi OR trên các chỉ số còn lại và \(1\le\ell\le P-1\). Kết quả đúng **theo định nghĩa**, vì mỗi assignment được chấp nhận là đúng một path hợp lệ và mọi path hợp lệ tạo một assignment.

(14) chứng minh khả năng biểu diễn, không chứng minh hiệu quả. Tensor thô có rank tăng theo chiều dài đường. Một biểu diễn khác lưu trạng thái \((u,v,U)\), trong đó \(U\) là tập đỉnh đã đi qua, có tối đa \(O(P^2 2^P)\) trạng thái. Đây là cận trên của một cách biểu diễn tổng quát, **không phải lower bound bắt buộc của PDS**. Muốn bỏ \(U\) mà vẫn exact cần một lemma loại vòng phù hợp với đúng predicate đang dùng hoặc một thuật toán chuyên biệt đã được chứng minh.

**Một lựa chọn bảo thủ có guarantee.** Gọi \(\widehat{\mathrm{PDS}}*{\rm walk}\) là tập thu từ (13), còn \(\mathrm{PDS}*{\rm path}\) là tập exact. Luôn có

\[
\mathrm{PDS}*{\rm path}(x,y)
\subseteq\widehat{\mathrm{PDS}}*{\rm walk}(x,y)
\subseteq V\setminus\{x,y\}.
\tag{15}
\]

Nếu dùng tập lớn hơn chỉ để sinh thêm conditioning candidates, kiểm định bằng CI oracle và vẫn giữ separator coverage cùng orientation hợp lệ, các test bổ sung không xóa được cạnh MAG thật. (15) có thể phục vụ **candidate envelope** an toàn; nó không chứng minh PDS equality, trace equality hoặc work saving. Không được dùng một walk giả làm bằng chứng rằng tiền đề định hướng dựa trên simple path đã thỏa.

### 3.4. ICD-Sep chứa ràng buộc trên toàn tập conditioning

Với \(S\subseteq V\setminus\{x,y\}\), \(|S|=k\), định nghĩa

\[
\mathsf{ICD}*k(x,y,S)
=[|S|=k]\land
\bigwedge*{z\in S}
\mathsf{PDSPath}_{\le k}\big(x,z;
G[\{x\}\cup S],\operatorname{avoid}=y\big).
\tag{16}
\]

Phần “mọi nút trên đường ở trong \(S\)” được hiểu **ngoại trừ nút gốc \(x\)**, vì \(x\notin S\). Predicate đường ở (16) sử dụng định nghĩa PDS gốc; số cạnh tối đa là \(k\). Xét hai đầu bằng OR của \(\mathsf{ICD}_k(x,y,S)\) và \(\mathsf{ICD}_k(y,x,S)\). Điều kiện possible-ancestor bổ sung phải theo đúng Definition 4 của [4] nếu được sử dụng; chính bài này ghi nhận đó không phải điều kiện bắt buộc cho correctness.

Một phép nhân ma trận cho “\(z\) cách \(x\) không quá \(k\) trong toàn graph” không kiểm tra được (16). Ví dụ, nếu đường hợp lệ duy nhất tới \(z\in S\) đi qua \(w\notin S\), khoảng cách có thể nhỏ nhưng tập \(S\) vẫn không admissible.

Theo Lemma 1 và Corollary 1 của [4], lớp tập admissible này bao phủ một separating witness cần thiết dưới các giả thiết của ICD. Điều đó quan trọng hơn việc có biểu diễn tensor ngắn cho riêng khoảng cách.

### 3.5. Mệnh đề D4: discriminating path của R4 bằng closure trên các parent

Đây là một trường hợp có thể tránh expansion theo toàn bộ lịch sử đường.

Xét R4 cho endpoint cuối \(y\), nút được phân biệt \(b\), với \(b\circ\!\! -\!*y\), tức \(C_{yb}=1\). Một discriminating path có dạng

\[
\pi=\langle x,q_1,\ldots,q_r=a,b,y\rangle,
\qquad r\ge1,
\tag{17}
\]

trong đó \(x\) không kề \(y\), mọi \(q_i\) là collider trên đường và là parent của \(y\). Đặt

\[
p_y(q)=D_{qy},\qquad
K_y(q,r)=p_y(q)\land p_y(r)\land H_{qr}\land H_{rq}.
\tag{18}
\]

\(K_y\) là graph bidirected giữa các parent của \(y\). Gọi \(K_y^*\) là Boolean reflexive-transitive closure trên tập parent. Khi đó predicate

\[
\begin{aligned}
\mathscr D_{xaby}
={}&[x,a,b,y\text{ đôi một khác nhau}]
\land N_{xy}\land C_{yb}\land p_y(a)\land H_{ba}\\
&\land\bigvee_q\left[p_y(q)\land H_{xq}\land(K_y^*)_{qa}\right]
\end{aligned}
\tag{19}
\]

tương đương với tồn tại discriminating path dạng (17) trong ngữ cảnh R4.

**Chứng minh chiều thuận.** Hai collider nội tiếp liên tiếp \(q_i,q_{i+1}\) đòi arrowhead ở cả hai đầu của cạnh nối chúng, nên cạnh đó bidirected và nằm trong \(K_y\). Cạnh đầu có arrowhead tại \(q_1\), cạnh \(b-a\) có arrowhead tại \(a\). Vì vậy mọi thừa số trong (19) bằng 1.

**Chiều đảo.** Chọn \(q\) và một đường ngắn nhất trong graph \(K_y\) từ \(q\) tới \(a\); đường ngắn nhất không lặp đỉnh. Nó không chứa \(y\), không chứa \(x\) vì \(x\not\sim y\), và không chứa \(b\) vì circle tại \(b\) trên cạnh \(b-y\) khiến \(b\) không thuộc tập parent của \(y\). Ghép \(x\), đường trong \(K_y\), rồi \(b,y\) được một simple path thỏa mọi điều kiện của (17). Trường hợp \(q=a\) được bao phủ bởi identity trong closure, tạo đường bốn đỉnh \(x,a,b,y\).

**Điểm cần giữ.** Không nên OR mất chỉ số \(a\) quá sớm: nhánh R4 không chứa \(b\) trong sepset còn định hướng cạnh \(a-b\). Reachability chỉ trả về “có một đường tới \(b\)” chưa đủ xác định mọi endpoint cần cập nhật. Nguồn [5–6] cung cấp rule semantics; phép factorization (18)–(19) và chứng minh trên là suy luận của báo cáo.

## 4. Batching, sequential invalidation và correctness

### 4.1. Mệnh đề D5: một vòng stable là phép OR trên witness

Tại đầu epoch \(k\), đóng băng state \(s_k\) và tập ứng viên \(\mathcal Q_k(x,y)\). Đặt \(I(x,y,S)\in\{0,1\}\) là quyết định CI cố định cho từng query. Quyết định xóa cạnh của vòng là

\[
\delta_k(x,y)
=\bigvee_{S\in\mathcal Q_k(x,y)} I(x,y,S),\qquad
A_{k+1}(x,y)=A_k(x,y)\land\neg\delta_k(x,y).
\tag{20}
\]

**Chứng minh.** Thủ tục tuần tự kiểm các phần tử của cùng \(\mathcal Q_k(x,y)\) cho đến witness đầu tiên xóa cạnh khi và chỉ khi có ít nhất một phần tử có \(I=1\). Thủ tục batch kiểm hết rồi lấy OR có đúng cùng điều kiện. Thứ tự xét các cạnh khác không tác động đến \(\mathcal Q_k(x,y)\) vì snapshot đã cố định. Kết luận giữ với một bảng quyết định CI bất kỳ, kể cả bảng có lỗi thống kê.

Mệnh đề chỉ bảo đảm skeleton của **cùng thủ tục stable**. Nó chưa bảo đảm sepset, orientation hoặc bằng nhau với bản dynamic.

Nếu cần giữ sepset theo reference tuần tự có thứ tự tổng \(\prec\), batch phải chọn

\[
\operatorname{Sep}*k(x,y)
=\min*{\prec}\{S\in\mathcal Q_k(x,y):I(x,y,S)=1\}.
\tag{21}
\]

(21) tái tạo witness đầu tiên của thứ tự đó; nó không làm reference trở nên độc lập với mọi thứ tự khác. Nếu dùng conservative/majority orientation, phải giữ đúng tập test và quy tắc tổng hợp witness của biến thể ấy. **Union các sepset không tự là một sepset**: conditioning thêm biến có thể mở collider, nên không được dùng union như bằng chứng CI mới.

### 4.2. FCI-stable thực sự bảo đảm điều gì?

Colombo–Maathuis [3], §4.4, mô tả FCI-stable bằng ba thay đổi liên quan: PC-stable ở pha đầu; collider ban đầu theo cách order-independent; và tính các Possible-D-SEP cho mọi cặp trước khi tinh lọc, không cập nhật lại các tập đó sau xóa cạnh. Vì vậy nguồn này trực tiếp hỗ trợ batching của PDS trong **ngữ nghĩa stable đã chỉ định**, chứ không chỉ của FAS.

Tuy vậy, FCI-stable riêng chưa làm mọi định hướng order-independent. CFCI/MFCI-stable bổ sung xử lý collider; LCFCI/LMFCI-stable thêm ngữ nghĩa list cho orientation. Bảo đảm correctness oracle được giữ, còn đầu ra sample có thể khác FCI dynamic. Theorems 2–3 của cùng bài nói về PC-stable; không nên trích chúng riêng như một định lý đầy đủ cho FCI có latent.

Đây là khác biệt giữa hai hợp đồng:

- **Bảo toàn full-budget oracle PAG:** có nền tảng literature cho stable variants phù hợp.
- **Giữ nguyên đầu ra hữu hạn mẫu của một implementation dynamic cụ thể:** cần chứng minh reference-specific; FCI-stable không tự cho điều đó.

### 4.3. Mệnh đề D6: separator coverage đủ cho đúng đắn oracle của một vòng ICD

Giả sử state đầu vòng \(k\) đáp ứng bất biến của ICD sau vòng \(k-1\), và mọi tập trong \(\widehat{\mathcal Q}_k(x,y)\) đều là tập con của \(V\setminus\{x,y\}\) có đúng \(k\) phần tử. Với mỗi cặp còn cạnh mà kích thước nhỏ nhất của một separator là \(k\), yêu cầu

\[
\exists S\in\widehat{\mathcal Q}_k(x,y):
|S|=k\quad\text{và}\quad X_x\perp X_y\mid X_S.
\tag{22}
\]

Thực thi tất cả query trong \(\widehat{\mathcal Q}_k\), chỉ xóa bằng CI thật, lưu separating witness thật, rồi áp dụng đúng orientation dành cho vòng anytime tương ứng. Khi đó vòng xóa chính xác các cạnh còn lại có separator tối thiểu kích thước \(k\).

**Chứng minh.** (22) bảo đảm mọi cạnh cần xóa có witness. Cạnh thật trong MAG không có separator giữa hai endpoint nên không thể bị xóa bởi oracle. Một cạnh còn lại có CI witness kích thước \(k\) thì có separator tối thiểu không lớn hơn \(k\); bất biến đầu vòng đã loại các trường hợp nhỏ hơn \(k\). Do đó không có loại cạnh nào khác bị xóa. Lemma 2 của [4] nối skeleton sau vòng với orientation anytime đúng. Quy nạp từ graph đầy đủ và dùng các vòng đến \(P-2\) cho mục tiêu PAG cuối theo Proposition 1 của [4].

Corollary 1 của [4] cung cấp (22) khi xét đủ ICD-Sep trên snapshot hợp lệ đầu vòng. Vì vậy một **vòng ICD đóng băng, xét đủ witness và giữ đúng orientation** có lập luận bảo toàn oracle dựa trên định lý đã công bố. Mệnh đề không cho phép tự ý đổi stopping rule, lọc prior, finite-sample sepset semantics hoặc lịch hướng cạnh giữa chừng.

Điểm phân biệt quan trọng: bảo đảm cần **ít nhất một witness phù hợp cho mỗi cặp cần tách**, không đòi query-trace bằng reference. Mệnh đề này cũng không tự chứng minh candidate Blockwise ICD hiện tại đáp ứng (22). Đó vẫn là nghĩa vụ [O] của dự án.

### 4.4. Vì sao thêm CI thật chưa đủ nếu đổi cả logic graph?

CI truth là thuộc tính của phân phối, không biến mất khi cạnh graph bị xóa. Tuy nhiên, **eligibility** của một query hoặc orientation witness là thuộc tính của state hiện tại. Thêm một CI fact thật không hợp thức hóa việc:

- dùng đường phân biệt đã bị phá ở state mới;
- lấy sepset của cặp khác hoặc một union chưa được test;
- áp dụng R1–R10 trên một skeleton tạm mà không đáp ứng giả thiết anytime;
- bỏ vĩnh viễn mọi witness của một cặp vì prior đánh giá thấp;
- coi PAG có finite-sample conflicts là một oracle-consistent PAG.

Trong một pha chỉ xóa cạnh, giữ endpoint cố định, các đường hiện hữu có thể mất đi. Nhưng trên toàn pipeline, xóa cạnh có thể tạo unshielded triple và suy diễn endpoint mới có thể tạo collider certificate mới. Không có phép suy “adjacency chỉ giảm nên mọi candidate/orientation predicate đều đơn điệu giảm”.

### 4.5. Mệnh đề D7: điều kiện đủ cho blockwise equality

State phải gồm ít nhất graph, sepset, CI facts, các query/sự kiện đã xử lý và pha hiện tại. Với sự kiện \(e\), gọi \(f_e\) là ánh xạ state và \(\operatorname{enabled}_e\) là tiền điều kiện.

Hai sự kiện có thể được coi là độc lập nếu, trên **mọi state có thể tới trong epoch**:

1. mỗi sự kiện không làm thay đổi enabledness của sự kiện kia;
2. \(f_e(f_f(s))=f_f(f_e(s))\), bao gồm cả sepset và tác động đến các candidate tương lai;
3. cả hai giữ các bất biến evidence/coverage của reference.

Một điều kiện đủ mạnh hơn, dễ phát biểu hình thức, là các tập đọc/ghi ngữ nghĩa thỏa

\[
W_e\cap(R_f\cup W_f)=\varnothing,
\qquad
W_f\cap(R_e\cup W_e)=\varnothing.
\tag{23}
\]

Các tập này phải bao gồm mọi dữ kiện về đường đi, nonadjacency và separator được đọc, không chỉ endpoint của cạnh được ghi.

**Kết luận.** Nếu giữ thứ tự reference bên trong mỗi block và chỉ cho các sự kiện độc lập giữa các block chạy xen kẽ, mọi interleaving hợp lệ có cùng kết quả với reference.

**Chứng minh.** Hoán đổi hai sự kiện kề nhau độc lập không đổi state theo điều kiện 2. Bằng một dãy hoán đổi như vậy, một interleaving có thể được đưa về thứ tự reference mà vẫn giữ các phụ thuộc. Điều kiện 1 bảo đảm các hoán đổi không tạo bước bất hợp lệ. Do đó state cuối bằng nhau.

Nếu muốn cho phép cả thứ tự bên trong block thay đổi hoặc tạo sự kiện động, cần bảo đảm mạnh hơn: termination cùng local confluence của **mọi critical pair**, hoặc một hệ cập nhật monotone–inflationary hội tụ công bằng như §5.3. Chỉ chứng minh vài cặp sự kiện giao hoán không đủ cho global confluence.

Hai vùng tách biệt trên skeleton chưa chắc thỏa (23): PDS, discriminating path, nonadjacency làm unshielded triple và alternative sepsets đều có thể tạo phụ thuộc xa. Một dependency graph đúng cũng có thể có duy nhất một component; đó là degeneration hợp lệ, không phải thất bại correctness.

### 4.6. Chuyển bảo đảm oracle sang consistency

Cho \(\mathcal U_n\) là một tập query xác định trước đủ bao phủ mọi query mà thuật toán có thể gọi, và giả sử

\[
\sup_{q\in\mathcal U_n}
\Pr\{\widehat I_n(q)\ne I(q)\}\le\varepsilon_n.
\]

Theo union bound,

\[
\Pr\{\exists q\in\mathcal U_n:
\widehat I_n(q)\ne I(q)\}
\le |\mathcal U_n|\varepsilon_n.
\tag{24}
\]

Nếu \(|\mathcal U_n|\varepsilon_n\to0\), mọi quyết định thuộc universe cùng đúng với xác suất tiến tới 1; cộng với định lý oracle và số học chính xác, suy ra consistency. Không được thay \(|\mathcal U_n|\) bằng số query realized ngẫu nhiên mà không có lập luận về selection/adaptivity.

Ở \(P\) cố định, một ngưỡng chuẩn hóa \(c_n\to\infty\) nhưng \(c_n/\sqrt n\to0\) có thể phân biệt zero với các partial correlation khác 0 cố định. Giữ \(\alpha\) dương cố định không bảo đảm xác suất khôi phục toàn graph tiến tới 1. Khi \(P\) tăng, cần thêm điều kiện về sparsity, kích thước conditioning, signal và tính đều của CI; các kết quả tương ứng cho FCI/RFCI nằm trong [2], §4.

Batching nhiều query hơn có thể tăng universe sai số, dù từng kernel không đổi. Bảo đảm tiệm cận phải được xét lại cho universe đó, không được suy từ “cùng công thức Fisher-Z”.

## 5. Đại số hóa R1–R10 và vấn đề fixed point

### 5.1. Những phần có phép dịch tensor trực tiếp

Với các kênh ở (9), đặt thêm

\[
U_{uv}=T_{uv}\land T_{vu},\qquad
CC_{uv}=C_{uv}\land C_{vu},\qquad
PD_{uv}=A_{uv}\land\neg H_{vu}\land\neg T_{uv}.
\tag{25}
\]

\(PD\) mô tả bước potentially directed từ \(u\) đến \(v\), theo quy ước không có arrowhead ở đầu xuất phát và không có tail ở đầu đến. Một uncovered path còn phải thỏa \(N_{v_{i-1},v_{i+1}}=1\) cho mọi triple liên tiếp và không lặp đỉnh.

Ví dụ R1 được dịch chính xác thành

\[
J^{(1)}*{bc}
=C*{cb}\land\bigvee_a(H_{ab}\land N_{ac}),
\qquad
T_{cb}\leftarrow T_{cb}\lor J^{(1)}*{bc},
\quad
H*{bc}\leftarrow H_{bc}\lor J^{(1)}_{bc}.
\tag{26}
\]

R2 có witness

\[
J^{(2)}*{ac}
=C*{ac}\land[(D\odot H)*{ac}\lor(H\odot D)*{ac}],
\tag{27}
\]

và thêm \(H_{ac}\). R3 là contraction bốn chỉ số:

\[
J^{(3)}*{db}
=C*{db}\land\bigvee_{a,c}
(H_{ab}\land H_{cb}\land C_{ad}\land C_{cd}\land N_{ac}),
\tag{28}
\]

rồi thêm \(H_{db}\). Các công thức được đọc trên snapshot hiện tại, với mask phân biệt đỉnh như trong rule gốc.

Toàn bộ mười luật có các dạng đại số sau. Bảng mô tả witness và tác động để phân biệt yêu cầu biểu diễn; nó không thay thế các điều kiện gốc bằng heuristic.

| Rule | Predicate/tác động đại số cần giữ |
| --- | --- |
| R1 | (26): một existential contraction; thêm tail tại \(b\) và head tại \(c\) trên \(b-c\). |
| R2 | (27): union của hai Boolean matrix products; thay circle tại \(c\) bằng head. |
| R3 | (28): collider, hai circle tại nút phụ và nonadjacency; thay circle tại \(b\) trên \(d-b\) bằng head. |
| R4 | \(\mathscr D_{xaby}\) từ (19), cùng predicate \(b\in\operatorname{Sep}(x,y)\). Membership cho \(b\to y\); nonmembership cho \(a\leftrightarrow b\leftrightarrow y\). Chỉ kiểm nonmembership khi có sepset đã xác định. |
| R5 | Cạnh \(a\circ\! -\!\circ b\), một uncovered circle path \(\langle a,c,\ldots,d,b\rangle\), \(N_{ad}\land N_{bc}\). Thêm tail tại cả hai đầu của cạnh \(a-b\) **và mọi cạnh trên witness**. |
| R6 | \(C_{cb}\land\bigvee_a U_{ab}\). Thêm tail \(T_{cb}\). |
| R7 | \(C_{cb}\land\bigvee_a(T_{ba}\land C_{ab}\land N_{ac})\). Thêm tail \(T_{cb}\). |
| R8 | \(C_{ca}\land H_{ac}\land\bigvee_b[(D_{ab}\lor(T_{ba}\land C_{ab}))\land D_{bc}]\). Thêm tail \(T_{ca}\). |
| R9 | \(a\circ\!\to c\), uncovered potentially directed path bắt đầu \(a,b,\ldots,c\), cùng \(N_{bc}\). Thêm tail \(T_{ca}\). |
| R10 | \(a\circ\!\to c\), hai parent khác nhau \(b,d\) của \(c\), hai uncovered potentially directed path từ \(a\) đến \(b,d\), với first neighbor \(\mu,\omega\) phân biệt và không kề. Thêm tail \(T_{ca}\). Không tự thêm điều kiện hai path phải hoàn toàn vertex-disjoint. |

Mỗi mệnh đề logic hữu hạn đều có phép biểu diễn bằng AND/OR và quantifier contraction tương ứng. Các path predicate có thể được biểu diễn exact như (14), đổi điều kiện endpoint/triple cho thích hợp. Chứng minh khả năng biểu diễn này không bảo đảm rank cố định hoặc work nhỏ.

Ngoài R1–R10, completeness cần skeleton/sepset đúng và **R0 cho unshielded colliders**. Khởi đầu từ skeleton toàn circle rồi chỉ áp R1–R10 không phải một thay thế đầy đủ cho FCI.

### 5.2. PAG marks không tự tạo Boolean lattice hợp lệ

Tại một endpoint, thứ tự thông tin tự nhiên là

\[
\circ\preceq\mathrm{tail},\qquad
\circ\preceq\mathrm{head},
\]

nhưng head và tail không so sánh được. Bộ ba này thiếu join của head với tail, nên không phải complete lattice. Một completion hình thức thêm \(\top\) biểu thị **conflict**, với encoding

\[
\circ=(0,0),\quad
\mathrm{tail}=(1,0),\quad
\mathrm{head}=(0,1),\quad
\top=(1,1).
\tag{29}
\]

Với \(m\) cạnh có \(2m\) endpoint, tích các lattice này là Boolean lattice trên \(4m\) endpoint atoms. Tuy nhiên, không phải mọi phần tử của lattice là PAG hợp lệ: còn ràng buộc ancestral, sự nhất quán với CI, và tính invariant của các marks. Conflict tại một endpoint cũng không phải một cạnh bidirected hợp lệ, vốn có một head ở **mỗi đầu khác nhau**.

Nếu mọi fact được suy ra đúng đối với cùng một lớp MAG không rỗng, conflict không xuất hiện. Ở hữu hạn mẫu, không thể suy điều đó chỉ từ thao tác OR.

### 5.3. Mệnh đề D8: định lý fixed point có điều kiện

Cho \(\mathcal F\) là tập finite facts, \(E\subseteq\mathcal F\), và

\[
F(E)=E\cup\bigcup_{j=0}^{10}\operatorname{Consequences}_j(E).
\tag{30}
\]

Giả sử:

1. skeleton và thông tin sepset cần dùng đã cố định và đúng;
2. consequences là sound, cùng nhất quán với một lớp MAG mục tiêu;
3. \(F\) monotone: \(E\subseteq E'\Rightarrow F(E)\subseteq F(E')\);
4. phép biên dịch facts/witness tương đương với rule semantics, không mất tiền đề đường đi;
5. closure xét mọi rule cần thiết; lịch bất đồng bộ, nếu dùng, là fair.

Khi đó lặp từ \(E_0\) đạt fixed point nhỏ nhất chứa \(E_0\). Với finite \(\mathcal F\), số vòng **có thêm fact** không quá \(|\mathcal F\setminus E_0|\).

**Chứng minh.** Inflationarity cho chuỗi tăng \(E_0\subseteq E_1\subseteq\cdots\). Finite height bảo đảm dừng. Nếu \(E^*\supseteq E_0\) là fixed point bất kỳ, monotonicity cho \(E_t\subseteq E^*\) bằng quy nạp; vì vậy limit là fixed point nhỏ nhất. Lập luận tương tự cho các operator thành phần monotone–inflationary được áp dụng fair: state cuối là common fixed point và nằm dưới mọi common fixed point chứa seed. Đây là dạng finite của cơ sở Tarski [9].

Trong một pha orientation có skeleton cố định và không đổi mark đã xác định, tối đa \(2m\) circle có thể được tinh chỉnh. Vì vậy không quá \(2m\) lượt cập nhật endpoint có tiến triển; nhiều endpoint có thể được cập nhật cùng một lượt. Auxiliary path facts hoặc các vòng quét không tạo thay đổi phải được tính riêng.

**Tách hai kết luận.** Termination theo số circle chỉ cần các cập nhật không đảo mark. Unique least fixed point/confluence cần thêm monotonicity hoặc một chứng minh thích hợp khác. Hai điều đó không đồng nhất.

### 5.4. Vì sao không thể áp Tarski một cách máy móc cho R1–R10?

Circle được định nghĩa bởi “chưa có head và chưa có tail”. Khi thêm một mark, một tiền đề circle có thể mất. Uncovered/potentially directed/circle-path predicates cũng có thể mất khi marks được tinh chỉnh. Do đó, toán tử “quét các luật đang enabled rồi OR kết quả” chưa mặc nhiên monotone trên toàn Boolean lattice (29).

Ví dụ hình thức: state \(E\) có \(a\to b\circ\! -\!\circ c\), \(a\not\sim c\), nên R1 thêm tail tại \(b\) của cạnh \(b-c\). State lớn hơn \(E'\) thêm head tại chính endpoint ấy làm R1 không còn enabled. Không thể kết luận \(F(E)\subseteq F(E')\) từ inclusion của input. Ví dụ này phản bác một khẳng định về **toàn lattice**, không phải phản ví dụ cho soundness của FCI oracle: \(E,E'\) không cùng nhất quán với một lớp chân lý thỏa các tiền đề R1.

Có hai cách lập luận hợp lệ:

- Giữ đúng các pha và các cập nhật được định lý completeness của Zhang bảo đảm; dùng tensor để đánh giá witness trên từng snapshot. Khi đó completeness được lấy từ semantics gốc, không cần giả vờ đã chứng minh một global monotone compiler.
- Xây một fact/certificate system có tiền đề bền vững, chứng minh soundness, monotonicity và tương đương rule closure, rồi áp D8. **Việc xây compiler ấy là một nghĩa vụ nghiên cứu**, không phải kết quả được Tarski cho miễn phí.

Một abstraction semantic luôn có tính đơn điệu là

\[
\mathcal M(E)=\{M:M\text{ là MAG phù hợp dữ kiện đã cố định và }E\},
\]

\[
\operatorname{Cl}_{\rm sem}(E)
=\{f\in\mathcal F:\forall M\in\mathcal M(E),\ M\models f\}.
\tag{31}
\]

Thêm evidence làm tập mô hình co lại, nên (31) là monotone, extensive và idempotent trên miền nhất quán. Nhưng tính (31) bằng cách liệt kê MAG có thể cực kỳ đắt. Monotonicity semantic không tự chuyển thành một thuật toán matrix closure hiệu quả. Một lượt áp rule cũng không phải phép chiếu idempotent; chỉ closure hoàn tất mới có thể có tính chất đó.

LoCI của Claassen–Heskes [6], Theorem 1, là tiền lệ quan trọng: có một hệ suy luận logic sound và complete cho causal information với latent/selection. Nó hỗ trợ hướng thiết kế certificate logic, nhưng không chứng minh bộ R1–R10 raw đã monotone hoặc có span polylog. Nếu contract của dự án chỉ cho phép R1–R10, LoCI là nguồn đối chiếu chứng minh; thay engine bằng LoCI cần giữ rõ hợp đồng tương đương.

## 6. Các giới hạn có thể khẳng định và những “bất khả” không được suy diễn

| Vấn đề | Kết luận có căn cứ | Điều không được kết luận |
| --- | --- | --- |
| Padding mọi query tới \(P\) | Tensor dense cần \(\Theta(QP^2)\) ô; có thể hơn ragged \(\Theta(P^2)\) lần. | Mask không tự làm các ô vật lý biến mất. |
| Giữ đồng thời \(B\) ma trận dense kích thước \(d\) | Riêng representation đã cần \(\Omega(Bd^2)\) ô. | Không thể yêu cầu toàn bộ parallel batch có peak space của một test mà không đổi representation hoặc tăng số đợt. |
| Conditioning lớn với mẫu nhỏ | Rank và bậc tự do khiến CI Gaussian thông thường không xác định trong một số \(k\). | GPU, padding hay semiring không giải quyết thiếu thông tin thống kê. |
| Kiểm mọi tập con của PDS | \(2^s\) tập với \(s=\lvert\mathrm{PDS}\rvert\), hoặc \(\binom{s}{k}\) ở level \(k\). Thực thi tường minh phải chịu work theo số phần tử đã thực thi. | Đây không phải lower bound cho mọi thuật toán khám phá nhân quả. |
| Tương đương walk/path | Ma trận lift hai đỉnh biểu diễn exact local-transition walks; simple-path equality cần chứng minh thêm. | Generic visited-set expansion không chứng minh mọi PDS/orientation cần exponential space. |
| Tính thích nghi | Một query phụ thuộc kết quả trước tạo cạnh trong computation DAG của lịch đó. | Cạnh phụ thuộc không bắt buộc thiết bị thực thi phải là CPU. |
| Batching và early stopping | Nếu cả hai query chạy trước khi biết query đầu đã đủ xóa cạnh, batch có thể tính một query reference sẽ bỏ. | Không thể đồng thời giữ physical query trace của mọi early-stop reference và thực hiện speculative query vốn có thể bị bỏ. |
| Lattice và confluence | Phải xác định order, complete domain, monotonicity/commutation và conflicts. | OR các marks hoặc “chỉ thêm evidence” không tự chứng minh complete PAG. |
| Latent confounding | Có thể tạo PDS lớn và phụ thuộc xa. | Không đủ để tuyên bố toàn bài toán NP-hard hoặc không có thuật toán đa thức dưới giả thiết cấu trúc. |

Đặc biệt, FCI+ của Claassen–Mooij–Heskes [8], UAI 2013, §5, cho một bảo đảm đa thức với node degree quan sát bị chặn \(\Delta\). Cận trong **bản 2013 được dùng ở đây** là \(O(P^{2(\Delta+2)})\) trong mô hình oracle hằng thời gian. Một supplementary revision về sau có cận viết khác; không trộn các phiên bản. Sự tồn tại của FCI+ bác bỏ suy luận “latent ⇒ mọi phương pháp bắt buộc exponential”. Nó không bảo đảm FCI nguyên bản hoặc một tensorization ngây thơ cũng đa thức.

### Vai trò đúng của Control Plane

Các quyết định epoch, enabledness, xử lý xung đột, xác nhận coverage và stopping phải tồn tại ở đâu đó trong semantics. Có thể gọi đó là control plane **logic**. Chạy chúng trên host là một lựa chọn kiến trúc, không phải định lý về tính không tính được trên GPU.

Một ranh giới phù hợp Safety Prior là: mọi kernel trả các ứng viên witness/CI result có ngữ nghĩa xác định; chỉ một operator evidence đã chứng minh hợp lệ mới được commit deletion/orientation. Prior thay thứ tự hoặc budget, không thay predicate CI, nội dung witness hay điều kiện dừng đầy đủ. Khi dừng trước khi có chứng nhận đầy đủ, đầu ra là discovery state chưa hoàn tất.

## 7. Mô hình chi phí hình thức

### 7.1. Mô hình tính toán và các biến chi phí

Sử dụng work–span trong mô hình arithmetic/Boolean PRAM lý tưởng. Một phép scalar arithmetic hoặc Boolean và truy cập chỉ số có chi phí đơn vị; không coi một phép nhân cả ma trận là một phép đơn vị. Với các chi phí phần cứng khác nhau, có thể gắn trọng số cho arithmetic và Boolean work mà không đổi các quan hệ phụ thuộc.

| Ký hiệu | Nghĩa |
| --- | --- |
| \(P,n\) | Số biến quan sát và số mẫu |
| \(K\le P-2\) | Bậc conditioning lớn nhất được xét |
| \(Q_k^{\rm dyn},Q_k^{\rm bat}\) | Số CI queries thực thi ở level \(k\), tương ứng dynamic và batch |
| \(B_k\) | Số ma trận kích thước \(d_k=k+2\) được giữ/tính đồng thời |
| \(m,\Delta\) | Số cạnh và bậc nút lớn nhất của snapshot |
| \(N_s,M_s\) | Số trạng thái và transition của lifted graph |
| \(\ell\) | Số bước truyền frontier cần xét trong graph trạng thái |
| \(R_{\rm or}\) | Số lượt đóng orientation có tiến triển, cộng các lượt kiểm tra kết thúc |
| \(\mu\) | Số processing elements lý tưởng |
| \(W_G,D_G\) | Tổng work/span của sinh candidate, path predicates, orientation và commit |

FCI có nhiều pha, còn RFCI có thể phát sinh CI trong orientation. Nếu lập lịch khác dạng “mỗi level một batch”, phải cộng theo **epoch thực tế**, không mặc định mọi query cùng \(k\) đã đồng thời eligible.

### 7.2. Chi phí CI khi đã có covariance

Tính covariance một lần có work \(W_{\rm cov}=O(nP^2)\). Khi các phép reduction được song song hóa hoàn toàn, arithmetic-circuit span là \(O(\log n)\); phép reduction đó cần tài nguyên trung gian tương ứng. Nếu chỉ giữ accumulator cho từng covariance entry, có thể dùng cận span \(O(n)\) với workspace nhỏ hơn. Không được đồng thời giả định span tối thiểu và mọi workspace trung gian bằng 0.

Với inverse/factorization dense cổ điển của ma trận SPD kích thước \(d\), dùng cận bảo thủ

\[
w_{\rm CI}(d)=O(d^3),\qquad
\tau_{\rm CI}(d)=O(d\log(d+1)),\qquad
m_{\rm CI}(d)=O(d^2).
\tag{32}
\]

Span trong (32) là cận cho một tổ chức elimination có các pivot phụ thuộc tuần tự và các phép cập nhật/reduction trong mỗi bước được song song hóa. Không khẳng định đây là cận tốt nhất trong lý thuyết parallel inversion; cũng không cần dựa vào thuật toán inversion NC với số học/độ ổn định khác để có mô hình này.

Do đó

\[
W_{\rm dyn}
=O\!\left(nP^2+\sum_{k=0}^KQ_k^{\rm dyn}(k+2)^3\right)+W_G^{\rm dyn},
\tag{33}
\]

\[
W_{\rm bat}
=O\!\left(nP^2+\sum_{k=0}^KQ_k^{\rm bat}(k+2)^3\right)+W_G^{\rm bat}.
\tag{34}
\]

Work sinh tập \(S\), lập submatrix và chọn witness không bị biến mất: với representation liệt kê chỉ số có thể có \(O(\sum_kQ_k k)\) work sinh danh sách và \(O(\sum_kQ_kd_k^2)\) work tập hợp covariance entries. Các phần này được tính trong \(W_G\) hoặc tính tách riêng, và thường bị term \(d_k^3\) chặn trên; path eligibility thì không nhất thiết như vậy.

Nếu mỗi level có một candidate family cố định và các level phải chờ nhau,

\[
\begin{aligned}
D_{\rm bat}
\le D_{\rm cov}+D_G^{\rm bat}
+O\!\left(\sum_{k=0}^K
\left\lceil\frac{Q_k^{\rm bat}}{B_k}\right\rceil
\left[(k+2)\log(k+3)+\log(B_k+1)\right]\right).
\end{aligned}
\tag{35}
\]

Trong (35), bucket waves được xử lý nối tiếp như một cách tổ chức đủ để tạo cận trên; không khẳng định đó là lịch tối ưu. Khi \(B_k=Q_k^{\rm bat}\), một batch không tạo thêm nhân tử \(Q_k\) cho span của CI, nhưng reduction và sự phụ thuộc giữa các epoch còn tồn tại. Một thực thi CPU hoàn toàn tuần tự có thời gian \(T_1=\Theta(W_{\rm dyn})\); không vì vậy mà mọi dependency của thuật toán gốc đều là lower bound cho một thuật toán đã biến đổi ngữ nghĩa lập lịch.

### 7.3. Cận tổ hợp và worst case của phần CI

Với candidate region cỡ \(s_k(x,y)\),

\[
Q_k^{\rm bat}
\le\sum_{\{x,y\}\in E_k}
\left[\binom{s_k(x,y)}k+\binom{s_k(y,x)}k\right]
\le 2\binom P2\binom{P-2}k.
\tag{36}
\]

Hai phía có thể trùng query; (36) là cận trên chưa khử trùng. Với \(K=P-2\),

\[
\sum_kQ_k^{\rm bat}=O(P^2 2^P),
\qquad
W_{\rm CI}=O(nP^2+P^5 2^P).
\tag{37}
\]

Nếu có đủ tài nguyên để mọi query trong một level chạy cùng lúc, từ (32) và log-reduction suy ra một cận span cho **riêng CI và phép OR của nó**:

\[
D_{\rm CI}=O(\log n+P^2\log(P+1)).
\tag{38}
\]

(38) không nói tổng thuật toán là polylog hoặc có speedup khả thi: work và bộ nhớ của batch toàn level có thể exponential, còn \(D_G\) chưa được cộng. Nếu \(K\) cố định, số query có cận \(O(P^{K+2})\); nếu toàn bộ candidate regions bị chặn bởi \(s\), cận kiểu \(O(P^2\sum_{k\le K}\binom sk)\) phù hợp hơn. Không thay \(s\) bằng degree của skeleton mà chưa có định lý, vì PDS có thể lớn hơn adjacency rất nhiều.

### 7.4. Cận cho graph algebra

Trên graph lift ở (11),

\[
N_s=2m\le P(P-1),
\qquad
M_s\le\sum_v d_v(d_v-1)\le2m(\Delta-1).
\tag{39}
\]

Trong trường hợp dense, \(N_s=O(P^2)\), \(M_s=O(P^3)\). Bảng sau dùng matrix multiplication cổ điển, không giả định số mũ nhân ma trận nhanh.

| Phép toán trên snapshot | Work | Span lý tưởng | Không gian biểu diễn chính |
| --- | ---: | ---: | ---: |
| BFS tuần tự trên lifted graph đã có | \(O(N_s+M_s)\) | \(O(N_s+M_s)\) cho lịch tuần tự đó | \(O(N_s+M_s)\) |
| Boolean frontier quét các transition cố định, \(\ell\) vòng | \(O(\ell(N_s+M_s))\) | \(O(\ell\log(P+1))\) | \(O(N_s+M_s)\), gồm trạng thái và reduction tuyến tính theo arcs |
| Dense Boolean closure bằng repeated squaring trên lift | \(O(N_s^3\log(N_s+1))\) | \(O(\log^2(N_s+1))\) | Các ma trận \(O(N_s^2)\); full-parallel reduction có thể thêm \(O(N_s^3)\) workspace |
| Cùng dense closure nhưng chỉ \(O(N_s^2)\) working cells, inner reduction tuần tự | \(O(N_s^3\log(N_s+1))\) | \(O(N_s\log(N_s+1))\) | \(O(N_s^2)\) |
| R4 theo (18)–(19), đồng thời cho mọi \(y\) | \(O(P^4\log(P+1))\) | \(O(\log^2(P+1))\) nếu đủ tài nguyên | \(O(P^3)\) closure; \(O(P^4)\) nếu giữ toàn bộ witness/reduction |
| Một lượt các motif cục bộ R1, R2, R3, R6, R7, R8 | \(O(P^4)\) theo contraction thô | \(O(\log(P+1))\) | Có thể \(O(P^4)\) nếu materialize mọi witness |
| Join R10 sau khi đã có exact first-neighbor path predicates | \(O(P^6)\) với sáu chỉ số thô | \(O(\log(P+1))\) | Có thể \(O(P^6)\); không bao gồm chi phí tạo path predicates |

Các cận reachability đầu bảng là **mỗi context** gồm các mask cố định. Nếu có \(F\) context khác nhau, work nhân \(F\); chỉ có thể giữ span bằng max span của các context khi cấp đủ tài nguyên chạy chúng đồng thời. Ví dụ, mask tránh endpoint thay đổi theo query không thể được coi như chỉ một context dùng chung miễn phí.

Thay \(N_s=O(P^2)\) vào dense closure cho

\[
W_{\rm lift,dense}=O(P^6\log(P+1)),\qquad
D_{\rm lift,dense}=O(\log^2(P+1)),
\tag{40}
\]

với \(O(P^4)\) ô ma trận và có thể \(O(P^6)\) workspace cho reduction song song đầy đủ. Đây là ví dụ rõ: depth nhỏ có thể đổi bằng work/space lớn so với duyệt sparse. “Tensor hóa” không đồng nghĩa work efficiency.

### 7.5. Một cận end-to-end exact, hữu hạn nhưng cố ý bảo thủ

Để không che các path predicates khó vào một ký hiệu không có cận, xét construction tổng quát (14) cho tất cả simple paths có độ dài tối đa \(L_p\le P-1\). Số assignment đỉnh phân biệt là

\[
g_{L_p}(P)=\sum_{\ell=1}^{L_p}
\frac{P!}{(P-\ell-1)!}.
\tag{41}
\]

Ở \(L_p=P-1\), \(g_{L_p}(P)<eP!\) và \(g_{L_p}(P)=\Theta(P!)\). Kiểm AllDifferent, các điều kiện triple, mask endpoint và đánh dấu các cạnh của witness có thể được chặn bởi \(O(P^2)\) phép toán cho mỗi assignment. Sau đó OR các witness và các join cục bộ:

\[
W_{\rm orient,one\ sweep}
=O(P^6+P^2g_{L_p}(P)),
\]

\[
D_{\rm orient,one\ sweep}
=O(\log(P+g_{L_p}(P))).
\tag{42}
\]

Đây là circuit-level depth với số xử lý và bộ nhớ witness rất lớn. Nó không cho một implementation constant-memory có cùng depth.

Cho một pha orientation trên skeleton cố định, giữ nguyên quy tắc commit của reference và chỉ tinh chỉnh circle, tối đa \(O(P^2)\) bước commit có tiến triển. Việc chọn một witness theo thứ tự xác định cũng là một phép reduction hữu hạn. Từ đó một construction exact có cận

\[
W_{\rm orient}
=O(P^8+P^4g_{L_p}(P)),
\qquad
D_{\rm orient}
=O(P^2\log(P+g_{L_p}(P))).
\tag{43}
\]

Tại \(L_p=P-1\), (43) cho \(O(P^8+P^4P!)\) work và \(O(P^3\log(P+1))\) depth. Đây là **cận trên xây dựng**, không phải khẳng định FCI orientation vốn cần factorial work: thuật toán duyệt chuyên biệt có thể tốt hơn rất nhiều. Mục đích là cho một biểu diễn exact hoàn toàn xác định mà không viện một theorem path-to-small-matrix chưa chứng minh.

Một đối chứng cụ thể là [8], §5: phân tích của FCI+ nêu chi phí orientation \(O(P^4)\) khi degree bị chặn, bằng các bài toán reachability, và dẫn Zhang (2008), p.1881. Kết quả đó không tự cung cấp span của một tensor compiler, nhưng đủ nhắc rằng độ phức tạp factorial ở (43) là giá của construction liệt kê, không phải đặc tính bắt buộc của bộ luật.

Một phiên bản FCI-stable dùng exact path predicates, candidate snapshots đúng, (20)–(21) và orientation theo reference vì vậy có thể được tensor hóa về mặt biểu diễn với cận thô

\[
\begin{aligned}
W_{\rm full}
&=O\!\left(nP^2+P^5 2^P+P^8+P^4P!\right),\\
D_{\rm full}
&=O\!\left(\log n+P^3\log(P+1)\right),
\end{aligned}
\tag{44}
\]

khi cấp đủ tài nguyên cho từng epoch/circuit và với số pha orientation của FCI bị chặn bởi một hằng số. PDS exact được tính bằng cùng loại path enumeration; các tập con PDS có thể liệt kê với work đã nằm trong các cận tổ hợp. (44) chứng minh **khả năng biểu diễn**, đồng thời cho thấy construction ngây thơ không phải một kết quả tăng tốc hữu ích.

Với ICD đóng orientation sau mỗi level, một cận bảo thủ là nhân phần graph/orientation trong (44) bởi \(K+1\). Chi phí kiểm (16) cho mỗi candidate còn phải được tính. Một construction trực tiếp xét mọi thứ tự đường trong \(\{x\}\cup S\) cho cận bổ sung

\[
W_{\rm ICD\ eligibility}
=O\!\left(\sum_k Q_k^{\rm bat}(k+2)^2(k+1)!\right).
\tag{45}
\]

Tất cả candidate cùng level có thể đánh giá song song với circuit depth \(O(k\log(k+2))\), nhưng memory/work theo (45) vẫn hiện hữu. Đây tiếp tục là cận exact tổng quát, không phải lower bound hay lựa chọn thuật toán được khuyến nghị.

Một đóng góp tensor hiệu quả phải thay những cận thô này bằng construction nhỏ hơn có proof: chẳng hạn tận dụng D4 cho R4, một lemma path-specific cho PDS/uncovered paths, hoặc chứng minh lớp graph mà dependency blocks nhỏ. Không nên công bố (38) như độ phức tạp toàn thuật toán trong lúc các hạng (43)–(45) chưa được xử lý.

### 7.6. Peak space và giới hạn batch

Nếu giữ một sepset dài tối đa \(K\) cho mỗi cặp, một biểu thức peak memory hữu ích là

\[
M_{\rm peak}
=O\!\left(P^2+P^2K+
\max_k B_k(k+2)^2\right)
+M_{\rm graph}+M_{\rm provenance}+M_{\rm reductions}.
\tag{46}
\]

Dữ liệu thô \(nP\) ô được cộng thêm nếu vẫn resident. Giữ **mọi** sepset hoặc mọi CI fact có thể làm \(M_{\rm provenance}\) lớn hơn nhiều; không được dùng cận một-sepset/cặp để báo cáo một hệ lưu toàn bộ evidence.

Nếu cho workspace CI là \(M_{\rm CI}\), thì

\[
B_k=O\!\left(\frac{M_{\rm CI}}{(k+2)^2}\right),\qquad
\text{số waves}\ge
\left\lceil\frac{Q_k^{\rm bat}}{B_k}\right\rceil.
\tag{47}
\]

(47) là câu trả lời chính xác cho yêu cầu “đồng dạng batch nhưng không tăng space”: có thể hạn chế space bằng cách hạn chế concurrency, không thể bảo đảm đồng thời mọi query đều resident và peak space như một query.

Đặc biệt, nếu baseline vốn đã giữ covariance \(P\times P\), chọn \(M_{\rm CI}=O(P^2)\) và \(B_k=O(P^2/(k+2)^2)\) có thể giữ cùng bậc **không gian số học** của baseline. Số test đồng thời khi đó giảm về \(O(1)\) lúc \(k=\Theta(P)\). Các bộ nhớ graph, sepset và provenance trong (46) vẫn phải được kiểm soát riêng.

### 7.7. Work inflation và speedup theo Brent

Đặt

\[
\eta=\frac{W_{\rm bat}}{W_{\rm dyn}},\qquad
\eta_{\rm CI}=
\frac{\sum_kQ_k^{\rm bat}(k+2)^3}
{\sum_kQ_k^{\rm dyn}(k+2)^3}.
\tag{48}
\]

\(\eta\) có thể khác \(\eta_{\rm CI}\) vì chi phí graph thay đổi. Các tỷ lệ này không mặc nhiên lớn hơn 1 trong mọi biến thể; phép chia sẻ như (8) có thể giảm work. Với speculative batching giữ cùng kernel nhưng xét thêm query, chúng đo work inflation thích hợp.

Trong mô hình lý tưởng, Brent [10], Lemma 2, cho

\[
\max\!\left(\frac{W_{\rm bat}}\mu,D_{\rm bat}\right)
\le T_\mu^{\rm bat}
\le \frac{W_{\rm bat}}\mu+D_{\rm bat}
\tag{49}
\]

tới quy ước hằng số/làm tròn của các bước. Nếu baseline chạy tuần tự với thời gian \(W_{\rm dyn}\),

\[
\mathrm{Speedup}*\mu
=\frac{W*{\rm dyn}}{T_\mu^{\rm bat}}
\le\min\!\left(
\frac\mu\eta,
\frac{W_{\rm dyn}}{D_{\rm bat}}
\right).
\tag{50}
\]

Vì vậy throughput cao không xóa giá của query dư: nếu \(\eta>\mu\), speedup so với baseline tuần tự là bất khả trong chính mô hình chi phí này. Ngược lại, \(\eta>1\) vẫn có thể đi cùng speedup khi parallelism đủ lớn và critical path đủ ngắn.

Ví dụ một cặp có \(r\) candidate cùng kích thước. Nếu witness đầu đã làm xóa cạnh, reference chỉ tốn một test còn batch toàn cặp tốn \(r\) test. Work inflation có thể bằng \(r\), không có cận hằng số chỉ từ stable correctness. Bởi vậy phải phân biệt “đúng và song song hóa được” với “work-efficient”.

K1 báo query saving trên FAS không xác định được \(\eta_{\rm CI}\), vì một CI bậc lớn có trọng số work khác CI bậc nhỏ. Nó cũng không đo \(D_G\), memory hoặc chi phí speculative queries trong PDS.

### 7.8. Nếu đã có phân rã block được chứng minh

Với các block độc lập có work \(W_j\), span \(D_j\), cùng chi phí chứng nhận phụ thuộc \(W_{\rm dep},D_{\rm dep}\):

\[
W_{\rm block}
=W_{\rm dep}+\sum_jW_j+W_{\rm merge},
\]

\[
D_{\rm block}
\le D_{\rm dep}+\max_jD_j+D_{\rm merge},
\tag{51}
\]

khi đủ processing elements chạy các block cùng lúc. Một giant component làm \(\max_jD_j\) gần span của toàn bài toán. Chi phí xây dependency certificates không thể được coi bằng 0, đặc biệt khi chúng dựa trên đường đi toàn cục.

## 8. Kết quả có thể dùng làm research contract tiếp theo

| Mục | Đã có gì trong báo cáo | Chưa được khẳng định |
| --- | --- | --- |
| Gaussian CI | D1–D2: đồng nhất exact, padding invariant, cận space/work | Không bảo đảm numeric equality khi thiếu margin; không bao phủ CI phi Gaussian |
| Graph algebra | D3: walk-to-lift equivalence; (14): exact simple-path tensor; D4: compact reduction cho R4 | Chưa có một theorem thống nhất biến mọi PDS/uncovered predicate thành ma trận nhỏ với work tuyến tính |
| Stable batching | D5: OR equivalence của vòng stable; literature FCI-stable; D6: coverage argument cho oracle ICD round | Không bảo đảm sample output bằng dynamic reference; không chứng minh implementation hiện có đáp ứng coverage |
| Blockwise ICD | D7: điều kiện đủ và chứng minh hoán đổi sự kiện | Chưa có dependency relation vừa đủ đúng vừa có block nhỏ trên lớp graph hữu ích |
| Orientation closure | Biểu thức tensor từng loại rule; D8: finite fixed-point theorem có giả thiết rõ | Chưa chứng minh raw R1–R10 monotone trên mọi PAG encoding; Tarski không tự cho completeness |
| Chi phí | (33)–(51): cost modular và một construction exact với cận đầy đủ | Không có tuyên bố speedup thực tế; không đánh đồng oracle query count với end-to-end runtime |

Ba câu hỏi lý thuyết cụ thể đáng ưu tiên:

1. **Quy dẫn path có tham số:** trên lớp PAG nào, các predicate PDS/uncovered có thể được biểu diễn bằng lifted graph cỡ đa thức nhỏ mà có chứng minh exactness hoặc envelope coverage? Cần chỉ rõ parameter: degree, separator size, path length hay cấu trúc đồ thị.
2. **Chứng nhận block:** xây điều kiện dependency đủ mạnh để D7 áp dụng, nhưng chi phí xây condition không lớn hơn phần work tiết kiệm và không thường xuyên suy biến thành một block.
3. **Certificate closure:** xây phép biên dịch R0–R10 có chứng nhận tương đương, kiểm soát circle guards và conflict, rồi mới tuyên bố monotone fixed point và tính độc lập với lịch.

Các câu hỏi này tạo đóng góp lý thuyết có thể bác bỏ được và độc lập với prior. Prior chỉ chọn cách dùng tài nguyên trong miền mà các định lý đã cho phép.

## 9. Tài liệu tham khảo và vị trí kết quả

**[1] Kalisch, M.; Bühlmann, P. (2007).** *Estimating High-Dimensional Directed Acyclic Graphs with the PC-Algorithm.* Journal of Machine Learning Research 8:613–636. **Đã đối chiếu:** Proposition 2; §2.2.2, công thức Fisher-Z (3); Lemma 2 về effective sample size. Nguồn này cung cấp Gaussian CI, không phải định lý về latent FCI batching. [PDF chính thức](https://www.jmlr.org/papers/volume8/kalisch07a/kalisch07a.pdf).

**[2] Colombo, D.; Maathuis, M. H.; Kalisch, M.; Richardson, T. S. (2012).** *Learning high-dimensional directed acyclic graphs with latent and selection variables.* Annals of Statistics 40(1):294–321. **Đã đối chiếu:** Definitions 3.1–3.2; Theorem 3.2 về RFCI-PAG; Theorem 3.3 về điều kiện liên quan đến FCI/RFCI equality; §4 về consistency. [DOI](https://doi.org/10.1214/11-AOS940); [bản tác giả](https://arxiv.org/pdf/1104.5617).

**[3] Colombo, D.; Maathuis, M. H. (2014).** *Order-Independent Constraint-Based Causal Structure Learning.* JMLR 15:3921–3962. **Đã đối chiếu:** Theorems 2–3 cho PC-stable; Theorems 6–7 cho các PC list variants; §4.4, pp.3937–3938, cho FCI-stable và các biến thể collider/list. Không gán Theorem 3 riêng cho toàn PAG latent. [PDF chính thức](https://www.jmlr.org/papers/volume15/colombo14a/colombo14a.pdf).

**[4] Rohekar, R. Y.; Nisimov, S.; Gurwicz, Y.; Novik, G. (2021).** *Iterative Causal Discovery in the Possible Presence of Latent Confounders and Selection Bias.* NeurIPS 34:2454–2465. **Đã đối chiếu:** Definitions 2–4; ICD-Sep conditions tại §3.2; Lemma 1, Corollary 1, Lemma 2, Proposition 1; phần proof trong supplement. [Bài chính](https://proceedings.neurips.cc/paper/2021/file/144a3f71a03ab7c4f46f9656608efdb2-Paper.pdf); [supplement](https://proceedings.neurips.cc/paper_files/paper/2021/file/144a3f71a03ab7c4f46f9656608efdb2-Supplemental.pdf).

**[5] Zhang, J. (2008).** *On the completeness of orientation rules for causal discovery in the presence of latent confounders and selection bias.* Artificial Intelligence 172(16–17):1873–1896. [DOI](https://doi.org/10.1016/j.artint.2008.08.001); [metadata/abstract tại cơ sở của tác giả](https://commons.ln.edu.hk/sw_master/732/). **Giới hạn truy cập:** toàn văn bản nhà xuất bản không tải được trong lượt khảo cứu này. Rule numbering/semantics được đối chiếu qua Table 1 và Algorithm 1 của nguồn nghiên cứu sơ cấp [6]; completeness còn được dẫn và sử dụng trực tiếp trong [3–4]. Vì vậy báo cáo không tự gán một số theorem chưa kiểm chứng trong bài [5].

**[6] Claassen, T.; Heskes, T. (2011).** *A Logical Characterization of Constraint-Based Causal Discovery.* Proceedings of UAI 2011:135–144. **Đã đối chiếu:** Table 1 và Algorithm 1 cho augmented FCI; Theorem 1 về soundness/completeness của LoCI; proof sketch trong appendix. Bản arXiv được đăng năm 2012, không phải năm xuất bản hội nghị. [Bản tác giả](https://arxiv.org/pdf/1202.3711); [proof supplement tại trang tác giả](https://www.cs.ru.nl/~tomc/docs/UAI2011_LCCausD_SupProofs.pdf).

**[7] Zhu, Z.; Zhang, Z.; Xhonneux, L.-P.; Tang, J. (2021).** *Neural Bellman-Ford Networks: A General Graph Neural Network Framework for Link Prediction.* NeurIPS 34. **Đã đối chiếu:** §3.1, Theorem 6 và §5 limitations. Chỉ dùng phần generalized Bellman–Ford với semiring exact; bản thân neural relaxation không có guarantee semiring tổng quát và bài này không chứng minh tensorized FCI. [PDF chính thức](https://papers.neurips.cc/paper_files/paper/2021/file/f6a673f09493afcd8b129a0bcf1cd5bc-Paper.pdf).

**[8] Claassen, T.; Mooij, J.; Heskes, T. (2013).** *Learning Sparse Causal Models is not NP-hard.* UAI 2013. **Đã đối chiếu:** §5, complexity analysis của FCI+, với cận \(O(P^{2(\Delta+2)})\) trong bản 2013. [Bản tác giả](https://arxiv.org/pdf/1309.6824); [danh sách bài được chấp nhận chính thức](https://www.auai.org/uai2013/acceptedPapers.shtml). Không dùng cận revised của supplement 2014 thay cho cận của bản này mà không báo phiên bản.

**[9] Tarski, A. (1955).** *A lattice-theoretical fixpoint theorem and its applications.* Pacific Journal of Mathematics 5(2):285–309. **Đã đối chiếu:** Theorem 1, pp.285–287; Theorem 2 bàn thêm các ánh xạ giao hoán. Báo cáo tự trình bày chứng minh finite-iteration cần dùng, không suy thời gian hội tụ hiệu quả chỉ từ tồn tại fixed point. [DOI](https://doi.org/10.2140/pjm.1955.5.285); [bản số tạp chí, bài bắt đầu ở p.285](https://msp.org/pjm/1955/5-2/pjm-v5-n2-p.pdf).

**[10] Brent, R. P. (1974).** *The Parallel Evaluation of General Arithmetic Expressions.* Journal of the ACM 21(2):201–206. **Đã đối chiếu:** Lemma 2, được tác giả trình bày lại cùng bài trên trang cá nhân; quan hệ thời gian \(t+(q-t)/p\). [Trang bài tại tác giả](https://maths-people.anu.edu.au/~brent/pub/pub022.html); [DOI](https://doi.org/10.1145/321812.321815).

**Hồ sơ dự án sử dụng:** `README(3).md` và các chương `01_executive_summary(2).md` đến `10_source_map_and_glossary(2).md` được đính kèm trong yêu cầu. Các mệnh đề D1–D8, các phép factorization và cận construction thô trong báo cáo là phần hình thức hóa ở đây, không được trình bày như kết quả đã được peer review hay như thay thế cho audit implementation của dự án.
