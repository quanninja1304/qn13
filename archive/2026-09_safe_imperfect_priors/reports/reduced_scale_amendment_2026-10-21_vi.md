# Amendment REDUCED-SCALE cho K0–K4 và nhánh benchmark bán tổng hợp

**Ngày đăng ký:** 21/10/2026  
**Trạng thái:** `REDUCED-SCALE`  
**Mục đích:** giảm chi phí CPU/RAM để chạy pilot và tìm phản ví dụ, nhưng không thay đổi định nghĩa hay ngưỡng của formal K0–K4.  
**Phạm vi:** dự án Safety Prior trong `D:\REsearch\causal multi-agent\safety_prior`.

## 1. Nguyên tắc amendment

Amendment này tạo một nhánh thực nghiệm rút gọn để:

1. tìm phản ví dụ sớm;
2. ước lượng sơ bộ cost–quality frontier;
3. xác định gate nào đáng được scale lên ma trận đầy đủ;
4. chạy được trên máy có CPU/RAM hạn chế.

Kết quả của nhánh này phải được gắn nhãn `REDUCED-SCALE`, `PILOT` hoặc `INCONCLUSIVE`. Không được đổi nhãn thành formal `PASS` chỉ vì kết quả pilot dương.

Formal contract của K0–K4 vẫn là source of truth. Nếu muốn thay đổi formal contract, phải tạo một version contract mới trước khi xem kết quả của version đó.

## 2. Thứ tự ưu tiên khi giảm quy mô

| Hạng mục bị cắt | Hậu quả thống kê/khoa học | Quyết định |
|---|---|---|
| Graph seed hoặc data seed | Khoảng tin cậy rộng hơn, power giảm xấp xỉ theo `1/sqrt(N)`; loại claim cơ bản không đổi | Ưu tiên cắt đầu tiên |
| Số cell topology | Thu hẹp miền claim; điều kiện “≥3/4 nhóm” phải được diễn giải lại theo miền còn lại | Chỉ dùng khi cần, phải ghi rõ |
| Ngưỡng, alpha, depth cap, metric và semantics | Thay đổi câu hỏi khoa học hoặc gate | Không được cắt |

Giảm scale có tính bất đối xứng:

- kết quả âm với cận tin cậy chặt vẫn có thể dùng để kill một hướng;
- kết quả dương với ít seed thường chỉ là tín hiệu, vì cận tin cậy có thể quá rộng để chứng nhận an toàn.

Mọi pilot phải báo cáo ba trạng thái:

```text
PASS         = vượt ngưỡng với cận tin cậy phù hợp trong phạm vi pilot;
FAIL         = không đạt hoặc bị phản ví dụ rõ ràng;
INCONCLUSIVE = chưa đủ power hoặc cận tin cậy cắt qua ngưỡng.
```

`PASS` trong bảng trên chỉ có nghĩa là pass trong pilot; không phải formal gate pass.

## 3. Kế hoạch rút gọn theo gate

### 3.1. K0 — Mechanical correctness

K0 chính thức đã đạt `220/220`. Không cần chạy lại toàn bộ chỉ vì máy yếu.

- Có thể chạy regression smoke nhỏ trước mỗi thay đổi code.
- Smoke chỉ là kiểm tra lỗi hồi quy, không thay thế bằng chứng K0 đã có.
- Không giảm hoặc đổi các invariant provenance, canonical output, replay và eligibility.

### 3.2. K1 — Oracle headroom

K1 chính thức có:

```text
p ∈ {10, 20}
latent_ratio ∈ {0.2, 0.4}
average_degree ∈ {2, 4}
20 graph seeds mỗi cell
8 cells × 20 = 160 graphs
160 graphs × 5 schedulers = 800 runs
```

Ưu tiên hiện tại là hoàn tất 125 row còn thiếu. Nếu máy không đủ khả năng hoàn tất trong thời gian chấp nhận được, chạy một pilot đã đăng ký trước:

```text
10 graph seeds đầu tiên trong mỗi 8 cell
= 80 graphs × 5 schedulers
= 400 scheduler runs
```

Việc chọn `seed index 0–9` phải được cố định trước khi phân tích pilot, không chọn theo graph đã cho kết quả tốt. Pilot phải giữ đủ cả tám cell; không được chỉ giữ những cell có tín hiệu tích cực.

Trade-off:

- vẫn có coverage về `p`, latent ratio và degree;
- nhưng mỗi cell chỉ có một nửa số seed, nên bootstrap CI rộng hơn;
- điều kiện formal “≥3/4 nhóm” không được dùng nguyên văn cho pilot nếu đơn vị nhóm khác với formal contract.

Kết luận pilot K1 chỉ có thể là: `FAIL`, `INCONCLUSIVE` hoặc “tín hiệu đủ mạnh để chạy full K1”.

### 3.3. K2 — Prior khả dụng

Pilot K2 tập trung vào claim chính:

- Prior B;
- AUC mục tiêu `0.65`;
- oracle scheduler;
- baseline prior-free mạnh nhất đã chọn trước;
- cùng graph subset với K1 pilot.

Có thể bỏ sweep AUC rộng trong pilot. Nếu cần chẩn đoán độ nhạy, Prior A được chạy tối đa ba mức, nhưng không được dùng Prior A để thay cho claim Prior B.

Không được đổi:

- cách định nghĩa positive query;
- cách tính score của Prior B;
- dung sai realized AUC `±0.02`;
- đơn vị bootstrap theo graph.

Nếu pilot K2 không đạt rõ ràng, hướng Prior B hiện tại có thể bị kill mà chưa cần chạy full sweep. Nếu pilot dương nhưng CI rộng, trạng thái là `INCONCLUSIVE` và cần scale up.

### 3.4. K3 — Lỗi tương quan và baseline mạnh

Pilot phải giữ ba chế độ lỗi:

1. lỗi độc lập;
2. lỗi theo node;
3. lỗi theo motif.

Chỉ được dùng một mức AUC chính trong pilot, với cùng realized AUC giữa ba chế độ. Có thể giới hạn pilot ở `p=10` và `p=20`, nhưng phải đăng ký rõ các giá trị `latent_ratio` và `average_degree` được giữ lại. Nếu bỏ các cell này, claim phải thu hẹp tương ứng; không được gọi là robustness trên toàn K1 grid.

Không được bỏ lỗi theo node hoặc motif chỉ vì chúng tốn thời gian, vì đó là phần kiểm tra chính cho lỗi tương quan.

### 3.5. K4 — Finite-sample safety

Formal K4 có:

```text
30 graph seeds × 3 data seeds × 2 sample sizes = 180 datasets
n ∈ {500, 2000}
```

Pilot được đăng ký:

```text
20 graph seeds × 2 data seeds × 2 sample sizes = 80 datasets
```

Giữ cả `n=500` và `n=2000`. Cắt graph seed trước, không cắt data seed, vì data seed đo nhiễu lấy mẫu của endpoint harm. Với 80 dataset, kết luận chính vẫn chỉ là pilot; cận trên của endpoint harm có thể chưa đủ hẹp để chứng nhận ngưỡng `0.1 endpoint/graph`.

## 4. Giảm chi phí mà không đổi semantics

### 4.1. Cache CI

Các scheduler trên cùng graph/dataset thường hỏi lại cùng một truy vấn. Có thể dùng cache kết quả CI, nhưng cache key phải bao gồm toàn bộ yếu tố ảnh hưởng kết quả:

```text
(graph_digest hoặc dataset_digest,
 X, Y, canonical(S),
 CI backend,
 alpha,
 sample size,
 numerical mode,
 ridge/pinv policy,
 implementation version)
```

Cache chỉ chia sẻ **kết quả CI**. Mỗi scheduler vẫn phải có provenance riêng, bao gồm thứ tự query, budget, witness và trạng thái resume. Không được dùng một trace của scheduler này làm trace của scheduler khác.

Đối với Fisher-Z, covariance có thể tính một lần cho mỗi dataset và chia sẻ cho các scheduler, miễn là cùng preprocessing, sample mask, alpha và numerical policy.

Đối với oracle d-separation, cache theo graph và canonical `(X,Y,S)` là hợp lệ vì oracle xác định. Cache phải invalid khi graph digest hoặc implementation version thay đổi.

### 4.2. RAM và worker

Thiết lập thực thi cho máy yếu:

- `workers=1`;
- batch memory plan khoảng 50–60% RAM khả dụng tại thời điểm bắt đầu;
- batch size nhỏ và bounded wave;
- ghi từng row/artifact xuống đĩa ngay sau khi hoàn tất;
- không giữ toàn bộ artifact của shard trong RAM;
- resume theo graph/run đã hoàn tất.

Giảm số seed chủ yếu giảm wall time và dung lượng output; giảm worker và batch size mới là biện pháp chính để giảm peak RAM.

## 5. Nhánh dữ liệu bán tổng hợp và dữ liệu thật

### 5.1. Vì sao không thay testbed chính bằng dữ liệu thật

K0–K3 cần ground truth để tính oracle headroom, query correctness và endpoint harm. Dữ liệu quan sát thật thường không có:

- DAG đầy đủ;
- latent mask;
- PAG chuẩn tuyệt đối;
- nhãn độc lập/phụ thuộc cho mọi `(X,Y,S)`.

Do đó dữ liệu thật không thể thay thế testbed synthetic latent DAG cho các gate này.

### 5.2. Nhánh topology công khai có ground truth

Có thể lấy các DAG công khai từ kho `bnlearn`, ví dụ `Asia`, `Sachs`, `Child`, `Insurance` và `Alarm`, rồi:

1. cố định DAG topology;
2. sinh nhiều latent mask có tỷ lệ khoảng `0.3`;
3. chuyển DAG + latent mask thành MAG/PAG bằng converter độc lập;
4. chạy K1/K2/K3 bằng oracle CI;
5. với K4, mô phỏng linear-Gaussian SEM trên topology đó.

Các mạng `bnlearn` gốc thường là mạng Bayesian rời rạc. Vì vậy chúng phù hợp trực tiếp cho oracle/topology test, nhưng K4 linear-Gaussian cần một lớp sinh dữ liệu mới. Không được gọi dữ liệu sinh từ topology này là “dữ liệu thật”.

Lưu ý tên `Sachs`: cần phân biệt mạng `Sachs` trong kho `bnlearn` với dataset protein-signaling thực nghiệm của Sachs et al. Hai thứ có mục đích và mức ground truth khác nhau.

Nếu có nhiều latent mask trên cùng một DAG gốc, các mask đó không độc lập. Bootstrap phải resample theo **cụm DAG gốc**, không resample từng mask như các quan sát độc lập.

### 5.3. Dataset thật thuần túy

Dataset thật chỉ nên là nhánh external-validity/sanity-check, không đưa vào PASS/FAIL của K0–K4.

- Sachs protein-signaling phù hợp làm case study thực tế, nhưng mạng tham chiếu không phải ground truth hoàn chỉnh cho latent confounding.
- CauseMe có các benchmark causal discovery kèm ground truth, phù hợp hơn cho so sánh định lượng bên ngoài.
- DREAM4 là benchmark công bố rộng rãi có ground truth, nhưng vẫn là in-silico, không phải dữ liệu quan sát thật.
- Causal Chambers có thể là ứng viên dữ liệu vật lý, nhưng phải kiểm tra giấy phép, định dạng và cách xác định đồ thị trước khi thêm vào.

Với dữ liệu thật thuần túy, chỉ nên báo cáo:

- runtime và peak memory;
- số query và cost curve;
- độ ổn định giữa preprocessing hợp lý;
- mức phù hợp với kiến thức miền;
- các PAG/endpoint không chắc chắn.

Không được báo cáo endpoint F1 như ground-truth accuracy nếu đồ thị tham chiếu chỉ là prior miền.

## 6. Kế hoạch tối thiểu cho benchmark arm

| Thành phần | Giá trị đăng ký |
|---|---|
| DAG topology | `bnlearn`: Sachs (11), Child (20), Insurance (27) |
| Latent mask | 10 mask mỗi DAG, latent ratio khoảng 0.3 |
| Gate | K1/K2 bằng oracle CI; K4 bằng linear-Gaussian SEM trên topology |
| Bootstrap | Theo cụm DAG gốc |
| Blocker trước khi tuyên bố PAG | OI-02: converter DAG + latent → MAG/PAG độc lập |
| Claim | Đa dạng topology và robustness bổ sung, không phải tổng quát hóa thống kê |

Ba DAG gốc chỉ chứng minh được rằng phương pháp không phụ thuộc hoàn toàn vào topology Erdős–Rényi. Đây không phải bằng chứng đủ cho khả năng tổng quát hóa trên mọi mạng nhân quả.

## 7. Quy tắc quyết định và báo cáo

Mọi kết quả phải ghi đồng thời:

```text
contract_version
amendment = REDUCED-SCALE
pilot_or_official
graph/data seed rule
cells included/excluded
effective sample size
bootstrap unit
status = PASS | FAIL | INCONCLUSIVE
```

Không được:

- chọn seed sau khi xem kết quả;
- đổi ngưỡng hoặc alpha để pilot đạt;
- gộp các mask cùng một DAG như các đơn vị độc lập;
- dùng dữ liệu thật không có ground truth để đóng K0–K4;
- dùng kết quả pilot dương để tuyên bố formal PASS.

## 8. Quyết định triển khai

1. Giữ K0 chính thức đã đạt; chỉ chạy regression smoke khi sửa code.
2. Ưu tiên hoàn tất 125 row K1 còn thiếu trước khi tạo một K1 pilot mới.
3. Nếu máy không đủ, chạy K1 `REDUCED-SCALE` với 10 seed trong cả 8 cell.
4. Chạy K2 pilot tại AUC 0.65, sau đó K3 pilot với đủ ba kiểu lỗi tương quan.
5. Chạy K4 pilot 80 dataset, giữ cả hai cỡ mẫu.
6. Tạo nhánh benchmark topology `bnlearn` sau khi đóng OI-02.
7. Thêm Sachs protein-signaling hoặc dataset thật tương tự chỉ như external-validity arm.

## 9. Kết luận

Amendment này giảm chi phí bằng cách cắt số seed và số sweep, không cắt semantics, ngưỡng hay loại lỗi quan trọng. Nó cho phép dùng máy yếu để tìm phản ví dụ và quyết định nơi cần scale up, nhưng vẫn giữ ranh giới giữa:

```text
pilot evidence  ≠  formal gate evidence
public topology ≠ real observational ground truth
real dataset    ≠ known latent PAG
```

Formal K0–K4 chỉ được kết luận sau khi chạy đủ contract tương ứng hoặc sau khi đăng ký một contract mới với phạm vi claim hẹp hơn.
