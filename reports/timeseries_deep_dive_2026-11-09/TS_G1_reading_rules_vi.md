# Luật đọc khai báo trước: pilot TS-G1 (bản nháp, CHỜ USER DUYỆT)

> Ngày 09/11/2026. Viết **trước khi chạy bất kỳ thuật toán discovery nào**.
> - P0 chỉ mô tả dữ liệu (đếm mẫu, độ phủ trạm mưa, tỉ lệ thiếu, phân bố khoảng cách), không có output của phương pháp nào. P0 đã chạy để chốt ngưỡng ở §3; kết quả ở §1.
> - Sau khi user duyệt, file này bị khóa. Mọi thay đổi sau đó phải ghi ở §8 kèm lý do, và không được sửa sau khi đã thấy kết quả.

## 0. Câu hỏi

Trên dữ liệu sông thật (CausalRivers, RiversEastGermany), **mưa** là confounder có tự tương quan.

- **Q1:** Mưa có tạo ra link giả *đo được* giữa các trạm không nối nhau theo topology không?
- **Q2:** Đưa mưa vào làm biến quan sát (lộ confounder) có làm số link giả giảm không?
- **Q3:** Khi mưa bị che, các phương pháp có tính biến ẩn (LPCMCI) có tránh được claim nhân quả sai không, và trả giá bao nhiêu về recall và thời gian chạy?

Đây là bước **đo failure**, không phải kiểm định một phương pháp mới. Phát biểu hình thức của bài toán, các giả thuyết H1–H3 và cổng G0–G3 nằm ở [`TS_G1_problem_statement_vi.md`](TS_G1_problem_statement_vi.md).

## 1. Kết quả P0 (mô tả)

Nguồn: `P0_descriptive.py` → `P0_outputs.json`, và `P0d_unit_feasibility.py` → `P0d_outputs.json`. Không có output của thuật toán discovery nào.

- **P0a, tập Confounder của CausalRivers:**
  - Đếm bằng code công khai (subgraph n nút, **giữ** nút confounder) cho **24 và 361 mẫu**, khớp đúng Bảng 6 của bài báo cho cả n = 3 và n = 5.
  - Đếm theo mô tả trong bài (subgraph n + 1 nút rồi bỏ nút confounder) cho 106 và 1170.
  - Kết luận [Verified bằng đếm lại]: cột Confounder trong Bảng 3 của bài được chấm trên các fork **quan sát đầy đủ**, không đo confounding ẩn.
- **Graph East Germany:**
  - 666 nút, 651 cạnh. Có 26 nút từ 2 nhánh con trở lên (sông tách nhánh).
  - Thuộc tính tọa độ `p` là (vĩ độ, kinh độ), ngược với README.
- **Dữ liệu thiếu (2019–2023, 175 296 bước 15 phút):**
  - 24.5% chuỗi thiếu trên 10%.
  - Trung vị tỉ lệ thiếu là 3.8%.
- **Đơn vị sau khi lọc:**
  - Còn 427 chain và 82 170 cặp chain không nối nhau.
  - Ngưỡng gần ≤ 30 km cho 3051 cặp ứng viên; ngưỡng xa ≥ 150 km cho 47 550 cặp.
  - Lấy mẫu được đủ 100 đơn vị mỗi tầng, với mỗi chain dùng tối đa 3 lần.
- **DWD (trạm đo mưa theo giờ hoạt động suốt 2019–2023):**
  - Có 1250 trạm. 99.8% trạm sông có trạm mưa trong bán kính 20 km; trung vị khoảng cách tới trạm gần nhất là 7.6 km.
  - Cả 200 đơn vị đã lấy mẫu đều có ít nhất một trạm mưa trong 20 km quanh mỗi chain. Với bán kính 10 km thì chỉ còn 131/200.

## 2. Dữ liệu

| Mục | Khai báo |
|---|---|
| Sông | `product/rivers_ts_east_germany.csv` và graph `rivers_east_germany.p` (CausalRivers release `First_release`, SHA-256 ghi trong manifest) |
| Khoảng thời gian | 2019-01-01 đến 2023-12-31 |
| Độ phân giải chính | **6 giờ** (lấy trung bình như `preprocess_data` của CausalRivers). Độ nhạy: 24 giờ. **Không chọn độ phân giải theo kết quả.** |
| Giá trị thiếu | Bỏ đơn vị có bất kỳ chuỗi nào thiếu trên 10% ở độ phân giải gốc; phần còn lại nội suy tuyến tính |
| Chuẩn hóa | z-score theo từng chuỗi |
| Mưa | DWD hourly precipitation (`RR_Stundenwerte`, open data, "Frei"). Chỉ dùng trạm hoạt động suốt 2019–2023. Proxy mưa của một chain là **trung bình các trạm DWD trong bán kính R_rain km quanh các nút của chain**, gộp lên 6 giờ bằng tổng. Chain không có trạm nào thì bị loại; số chain bị loại được báo cáo |

## 3. Đơn vị phân tích

- **Chain** là một cạnh có đo trên cả hai đầu, u → v, trong graph RiversEastGermany.
- **Đơn vị** là hai chain A = (a1 → a2) và B = (b1 → b2) thỏa:
  - (i) không chung nút;
  - (ii) không có tổ tiên chung, và không có đường nối giữa bất kỳ nút nào của A với bất kỳ nút nào của B theo cả hai chiều (dùng `nx.ancestors`).

  Như vậy theo topology, **mọi cặp chéo (a_i, b_j) không có quan hệ nhân quả**.
- **Tầng:** khoảng cách nhỏ nhất (haversine) giữa các nút của A và B.
  - *Gần*: ≤ D_near km.
  - *Xa*: ≥ D_far km.
- **Lấy mẫu:** 100 đơn vị mỗi tầng, seed `20261109`, mỗi chain dùng tối đa 3 lần.
- **Ngưỡng đã chốt sau P0:** D_near = 30 km, D_far = 150 km, R_rain = 20 km. Lý do: với các ngưỡng này, cả hai tầng đều lấy đủ 100 đơn vị và mọi đơn vị đều có trạm mưa. Các ngưỡng được chốt từ dữ liệu mô tả, không dựa trên output của thuật toán nào.

## 4. Điều kiện và phương pháp

**Điều kiện:**
- **L (latent):** chỉ 4 chuỗi sông.
- **O (observed):** 4 chuỗi sông cộng 2 chuỗi mưa (proxy của A và proxy của B). Mưa được khai báo là ngoại sinh, tức không biến sông nào gây ra mưa (link assumptions trong tigramite; với VAR thì bỏ các phương trình của mưa).

**Phương pháp** (tham số cố định, không tìm theo nhãn):

| Phương pháp | Cài đặt |
|---|---|
| VAR-Granger | `statsmodels` VAR, lag cố định τ_max = 4 (= 24 giờ), Granger F-test có điều kiện trên toàn bộ biến của đơn vị, α = 0.01 |
| PCMCI+ | `tigramite` 5.2.10.1, ParCorr, τ_min = 0, τ_max = 4, pc_alpha = 0.01 |
| LPCMCI | `tigramite` 5.2.10.1, ParCorr, τ_max = 4, pc_alpha = 0.01, các tham số khác để mặc định |

- **Timeout:** 300 giây mỗi lần chạy. Lần chạy timeout được ghi là thất bại và báo cáo riêng.
- **Phải cài:** `tigramite==5.2.10.1` (pip). `lingam` và TS-ICD không nằm trong pilot.

## 5. Metric (ở mức summary, gộp mọi lag)

| Ký hiệu | Định nghĩa |
|---|---|
| q1 | Tỉ lệ cặp chéo (4 cặp mỗi đơn vị) có **bất kỳ** cạnh nào |
| q2 | Tỉ lệ cặp chéo có **claim nhân quả**. Với VAR và PCMCI+: mọi cạnh có hướng. Với LPCMCI: cạnh dạng `-->`, tức đuôi ở nút nguồn, nghĩa là khẳng định tổ tiên. `o->`, `<->`, `o-o` không tính là claim nhân quả nhưng được báo cáo riêng |
| q3 | Recall của 2 cạnh thật trong chain (a1 → a2, b1 → b2). Tính là trúng nếu có cạnh không ngược hướng: với PAG thì `-->` hoặc `o->`; `<->` tính là trượt |
| q4 | Tỉ lệ `<->` trên các cặp chéo (chỉ LPCMCI) |
| t | Thời gian chạy trung vị mỗi đơn vị |

Khoảng tin cậy: bootstrap theo đơn vị, 2000 lần, 95% percentile.

## 6. Luật đọc

- **R0, hợp lệ dữ liệu:** mỗi tầng còn ít nhất 60 đơn vị sau khi loại. Nếu không đạt thì dừng và báo cáo.
- **R1, confounding đo được:**
  - Điều kiện: với VAR ở điều kiện L, q1(gần) − q1(xa) ≥ 0.10, và cận dưới CI > 0.
  - **Không đạt thì TS-G1 là NO-GO** theo thiết kế này: không đo được confounding do mưa.
- **R2, lộ mưa có tác dụng:**
  - Điều kiện: với PCMCI+ ở tầng gần, q2(L) − q2(O) ≥ 0.05, và cận dưới CI > 0.
  - Không đạt thì ghi "không xác nhận được mưa là nguồn chính", vẫn đọc tiếp R3 nhưng hạ mức tin cậy.
- **R3, có gap phương pháp không** (tầng gần, điều kiện L, so LPCMCI với PCMCI+):
  - Đặt Δfalse = q2(PCMCI+) − q2(LPCMCI) và Δrecall = q3(PCMCI+) − q3(LPCMCI).
  - **GAP-A**, phương pháp có biến ẩn không sửa được: Δfalse < 0.05.
  - **GAP-B**, sửa được nhưng trả giá đắt: Δfalse ≥ 0.05 **và** thỏa ít nhất một trong hai điều sau: Δrecall ≥ 0.10; t(LPCMCI) > 60 giây và lớn hơn 10 lần t(PCMCI+).
  - **NO METHOD GAP**: Δfalse ≥ 0.05, Δrecall < 0.10, và thời gian chạy chấp nhận được. Khi đó TS-G1 chỉ còn là phát hiện về *đánh giá*, rơi vào vùng X31. Khuyến nghị dừng hoặc tìm hướng khác.
  - **Kiểm tra hợp lý:** ở tầng xa, q2 của mọi phương pháp phải nhỏ hơn ở tầng gần. Nếu không, metric hoặc giả định topology có vấn đề, phải điều tra trước khi đọc R3.
- **R4, mô tả:**
  - Báo cáo các đại lượng ở độ phân giải 24 giờ.
  - Báo cáo tập Confounder đã sửa (bỏ thật nút cha chung) so với tập gốc. **Không ra quyết định** từ R4.

## 7. Giới hạn đã biết trước

- Topology chỉ cho biết có hay không có đường nhân quả, không cho độ lớn hiệu ứng. "Không có đường" là chắc chắn theo dòng chảy, nhưng phải chấp nhận sai số nếu graph dựng sai, chẳng hạn kênh nhân tạo hoặc trạm bơm.
- Ngoài mưa còn có confounder ẩn khác: tuyết tan, nhiệt độ, nước ngầm, điều tiết đập. R2 giúp tách phần do mưa.
- Proxy mưa từ trạm điểm chỉ lộ confounder một phần.
- Chỉ một vùng địa lý và một benchmark; dùng nhiều đơn vị chung chain nên các đơn vị không độc lập hoàn toàn.
- Tham số α và τ_max được cố định chứ không tối ưu. Điều này có thể khiến một phương pháp bất lợi hơn phương pháp khác; kết quả phải đọc trong giới hạn đó.

## 8. Nhật ký thay đổi (append-only)

- 09/11: bản nháp.
- 09/11: điền kết quả P0 (§1) và chốt D_near, D_far, R_rain (§3). Chưa chạy discovery. Chờ user duyệt.
- 10/11: **user duyệt ("okay duyệt"). File bị khóa từ đây.** Mọi thay đổi về sau chỉ được ghi thêm ở mục này.
- 10/11, **làm rõ cách cài đặt, ghi TRƯỚC khi chạy bất kỳ phương pháp nào trên dữ liệu thật.** Không thay đổi ngưỡng hay luật nào; chỉ chốt những chỗ luật chưa nói rõ.
  1. **Recall (q3):**
     - Với PCMCI+ và VAR: tính là trúng nếu có cạnh không ngược hướng ở bất kỳ τ nào, tức `-->`, `o-o` hoặc `x-x`.
     - Với LPCMCI: chỉ `-->` hoặc `o->`. Các dấu `<->`, `o-o`, `<-o`, `<--`, `x-x` đều tính là trượt.
  2. **Đơn vị thống kê:** q1–q4 được tính trung bình trên 4 cặp chéo (hoặc 2 cạnh thật) trong mỗi đơn vị, rồi lấy trung bình theo đơn vị.
     - R1 so hai tầng độc lập, dùng bootstrap không ghép cặp.
     - R2 và R3 dùng hiệu **ghép cặp theo đơn vị**, chỉ trên các đơn vị mà cả hai lần chạy đều thành công.
     - Lần chạy timeout hoặc lỗi bị loại khỏi metric và đếm riêng. Lần chạy có runtime trên 300 giây cũng tính là timeout.
     - R3 dùng ước lượng điểm đúng như luật; khoảng tin cậy chỉ để báo cáo.
  3. **VAR ở điều kiện O:** VAR(4) ước lượng trên cả 6 biến, nhưng chỉ kiểm Granger cho đích là sông. Vì VAR ước lượng OLS theo từng phương trình, cách này tương đương với "bỏ phương trình của mưa".
  4. **Cấu hình mưa ngoại sinh trong tigramite:** sông → mưa bị cấm ở mọi τ. Mưa → sông được khai báo `-?>` ở τ ≥ 0. Giữa hai biến mưa ở τ = 0 là `o?o`. Giữa sông với sông, τ > 0 là `-?>` và τ = 0 là `o?o`.
  5. **Độ nhạy 24 giờ:** gộp dữ liệu 6 giờ đã chuẩn bị (trung bình 4 bước với sông, tổng 4 bước với mưa), chuẩn hóa lại, τ_max = 1. Như vậy chân trời 24 giờ giống bản chính.
  6. **Chuẩn bị dữ liệu:**
     - Sông: làm tròn mốc thời gian về lưới 6 giờ rồi lấy trung bình; nội suy tuyến tính cả hai chiều để lấp đầu và cuối chuỗi.
     - Mưa: trung bình các trạm trong 20 km theo từng giờ (bỏ qua giá trị thiếu); khoảng trống mà mọi trạm đều thiếu được nội suy tuyến tính; tổng 6 giờ.
     - Múi giờ: DWD dùng UTC. Mốc thời gian của CausalRivers không ghi múi giờ, nên giả định là UTC.
  7. **Chạy:** 3 tiến trình song song, BLAS một luồng. Runtime là thời gian bên trong tiến trình con, không tính thời gian khởi động.
- 11/11, **sửa trong khi chạy, CHƯA xem metric nào:**
  1. Lần chạy đầu dừng ở 231/2400 job với mã lỗi 4, log không ghi lý do. Đã chạy tiếp từ chỗ dừng.
  2. Đơn vị 27 và 59 (tầng gần) có hai chain dùng chung bộ trạm mưa, nên rain_a và rain_b trùng hệt nhau (tương quan 1.0). VAR báo `LinAlgError: Singular matrix`.
     - Quy tắc mới: ở điều kiện O, nếu tương quan giữa hai proxy mưa lớn hơn 0.999 thì chỉ giữ **một** biến mưa chung.
     - Các dòng điều kiện O của đơn vị 27 đã bị xóa và sẽ chạy lại; đơn vị 59 chưa chạy.
  3. Ba lần chạy của đơn vị 0 bị timeout (LPCMCI ở L, PCMCI+ và LPCMCI ở O). Giữ nguyên là timeout theo luật.
- 12/11, **đọc kết quả** (không thay đổi luật nào): chạy xong 2400 job, gồm 2396 thành công và 4 timeout (đều ở 6H). Kết quả: R0 đạt, R1 đạt (0.308, CI [0.247, 0.368]), R2 **không đạt** (−0.013, CI [−0.048, 0.023]), kiểm tra hợp lý đạt, R3 = **GAP-A** (Δfalse = −0.196), đọc với mức tin cậy đã hạ do R2 không đạt. Chi tiết ở [`P1_results_vi.md`](P1_results_vi.md). Mọi phân tích tiếp theo (P2) phải có luật đọc mới.
