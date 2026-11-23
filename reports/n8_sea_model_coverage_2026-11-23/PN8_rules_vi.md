# P-N8: SEA trên phép thử khối đích cố định (luật v1, ĐÃ KHÓA; 23/11/2026)

> **Trạng thái:** v1 ĐÃ KHÓA. User duyệt v0.2 ngày 23/11 kèm các sửa ở G3, G4 và §5; v1 = v0.2 cộng đúng các sửa đó (§10). Khóa bằng commit và push trước khi SEA chạy trên bất kỳ input nào của §2 hoặc của tập phát triển base 510000.
>
> - Chưa chạy SEA trên bất kỳ input nào của §2.
> - Bước 1 (`PN8_pilot1_inputs_vi.md`) và bước 2 (`PN8_step2_feasibility_vi.md`) chỉ dùng dữ liệu phát triển, và là exploratory.
> - Các thay đổi qua v0, v0.1, v0.2 và v1 nằm ở §10.
>
> **Vai trò:**
>
> - **study bổ sung về phạm vi model**, thiết kế sau các study chính. Luật và nhãn của các pha trước giữ nguyên;
> - trong bài: Study 7, với bảng riêng. Không ghép vào bảng của các study khác như một phép so trực tiếp giữa bốn model;
> - câu hỏi: hiện tượng của bài có xuất hiện ở một pipeline tổng hợp ước lượng cổ điển trên tập con biến (SEA) không?
>
> **Cam kết báo cáo:** nếu kiểm hoàn tất đạt, cả sáu giả thuyết ở §4 được báo cáo trong bài, với Label và Size, bất kể chiều và độ lớn. Quyết định này không phụ thuộc kết quả.

## 0. Câu hỏi và điều không thể kết luận

- **SEA là pipeline ngẫu nhiên.** Chỉ đổi seed, skeleton khối đích đã đổi 2–4 cặp ở k0 trên 3 bảng phát triển (bước 2). Vì vậy, mọi phép so về thay đổi skeleton đều đặt cạnh các output k0 ở seed khác.
- **Câu hỏi:**
  - (A) Trên hệ tổng hợp held-out mới, sau khi thêm 20 cột độc lập (Gauss; có cấu trúc), output khối đích của SEA có nằm xa các output k0 ở seed khác hơn so với output k0 cùng seed không? Khoảng cách đo bằng số cặp có trạng thái skeleton khác nhau. F1 skeleton có giảm không, và có giảm nhiều hơn ở PC và GES (trên hệ tuyến tính) không?
  - (B) Trên hai bảng thật cố định của Study 4, cùng câu hỏi về khoảng cách như (A).
- **Δ đo gì và không đo gì:**
  - Δ là chênh lệch khoảng cách trung bình tới các output k0 tham chiếu (§3).
  - Nếu phân phối output theo seed không đổi khi thêm cột, thì E[Δ] = 0. **Chiều ngược lại không đúng.**
  - Ví dụ một cạnh: ở k0, SEA dự đoán có cạnh ở 50% số seed. Sau khi thêm đệm, SEA luôn dự đoán có cạnh. Khoảng cách kỳ vọng từ mỗi loại output tới một output k0 độc lập đều là 0.5, nên E[Δ] = 0, dù phân phối đã đổi rõ. Giá trị Δ đo trên một số hữu hạn seed vẫn dao động quanh 0. Với nhiều cạnh, các thay đổi còn có thể bù nhau.
  - Vì vậy Δ **không** đo "độ ổn định sau khi loại nhiễu seed", và không cho kết luận về độ ổn định của toàn bộ phân phối output. Câu hỏi đó cần thiết kế khác và không thuộc bài này.
- **Không kết luận được:**
  - kênh nào gây ra thay đổi: phân bổ lô, thống kê toàn cục, hay aggregator. Bước 1 chỉ đo phía input; muốn quy nguyên nhân cần can thiệp riêng;
  - nguyên nhân thuộc về chính thiết kế tổng hợp trên tập con. Kết quả bổ sung bằng chứng cho một pipeline tổng hợp trên tập con (một model, một checkpoint), không đại diện cho mọi model có cùng kiểu thiết kế;
  - bất kỳ so sánh nào giữa SEA và AVICI, CDFM hay FoundCause như một phép kiểm;
  - với bảng thật: độ chính xác, và khái quát sang bảng khác.
- **Điều kiện thử so với điều kiện huấn luyện của SEA** (bài SEA, §4.1 và Appendix B.1; user kiểm, agent đọc lại bản HTML arXiv 2402.01929v3 ngày 23/11):
  - SEA được huấn luyện trên đồ thị ER và scale-free với N = 10, 20, 100 biến và E = N, 2N, 3N, 4N cạnh kỳ vọng; cơ chế Linear, NN với nhiễu Gauss cộng và NN không cộng; mỗi dataset 1000N hàng;
  - RFF không có trong danh sách cơ chế huấn luyện;
  - D = 30 và D = 40 nằm giữa các kích thước đã công bố, nhưng **không** gọi toàn bộ điều kiện thử là in-distribution;
  - n = 500 bằng kích thước lô b = 500. Vì vậy lô nào cũng dùng đủ 500 hàng, trong khi lúc huấn luyện mỗi lô là mẫu con của 1000N hàng.
- **Nguồn sinh dữ liệu tổng hợp:**
  - phần (A) sinh bằng simulator của AVICI, với khối cơ chế lấy từ ví dụ của tác giả AVICI, như Studies 1–3 và 5;
  - đây là một mất cân đối về nguồn sinh giữa các model. Chưa có bằng chứng nó nhất thiết có lợi cho AVICI. Cùng simulator và nằm trong dải tham số không có nghĩa toàn bộ thí nghiệm nằm trong phân phối huấn luyện của bất kỳ model nào;
  - giới hạn này cũng cần ghi trong §7.1 của bài.
- **Dữ liệu dùng lại:**
  - Phần (B) dùng lại input và output PC/GES của Study 4. SEA chưa chạy trên các input này, và luật được khóa trước khi chạy, nên đây là đánh giá thiết kế trước cho một model mới trên dữ liệu cũ, **không** phải lần lặp lại trên dữ liệu mới.
  - Phần (A) dùng hệ mới, chưa sinh ở pha nào.

## 1. Model và cách chạy

- **Phiên bản:**
  - SEA, repo `rmwu/sea-reproduce` ở commit `bfb507b002d7f066f307a0dc15bd23fc703848b4`;
  - checkpoint `checkpoints/fci_synthetic/model_best_epoch=373_auprc=0.842.ckpt`, SHA-256 `fa1a1d39d9c019fe045282c7455ea33fbc624552cfb3d9516d6966c185f3bcc0`;
  - cấu hình `config/aggregator_tf_fci.yaml` (SHA-256 `3f22a75d…6dabc746`), giữ nguyên, chỉ đổi `data_file`, `results_file` và `num_workers: 0`.
- **Code so với bài:** Appendix B.6 của bài SEA mô tả nửa đầu số lô chọn theo thống kê toàn cục và nửa sau chọn ngẫu nhiên. Code ở commit đã ghim chạy `RandomSampler` trước, rồi mới `CorrelationSampler` (`get_samplers`). Study 7 đánh giá code đã phát hành và ghi rõ khác biệt này.
- **Môi trường:** Python 3.10.21, torch 1.13.1+cpu, pytorch-lightning 1.9.0, torchmetrics 1.3.0, causal-learn 0.1.3.7, numpy 1.23.5, scipy 1.10.1, scikit-learn 1.2.2, setuptools 69.5.1. Bản khóa đầy đủ (`pip freeze`) được đóng băng cùng code.
- **Đơn vị chạy:**
  - mỗi input chạy riêng trong một tiến trình mới, bằng script `src/inference.py` nguyên bản, với `--gpu -1 --seed s`, trên CPU;
  - lý do: SEA đặt seed một lần cho cả lượt. Nếu nhiều input nằm trong một file, output của mỗi input phụ thuộc vị trí của nó (đã kiểm ở bước 2).
- **Seed:**
  - mỗi lần chạy có seed ghi trước (§2);
  - seed mặc định 0 không được dùng riêng. Lý do: ở một seed cố định, mọi input cùng D dùng chung 250 tập biến của nửa ngẫu nhiên (đọc code, bước 2 §3).
- **Cách đọc skeleton:**
  - **NATIVE** (chính): cạnh {i, j} khi max(P(i→j), P(j→i)) > 0.5. Đây là ngưỡng 0.5 cho từng hướng mà hàm đánh giá của SEA dùng. Với SEA, FIXED và FROZEN trùng NATIVE;
  - **đọc phụ, phân tích độ nhạy định trước:** cạnh {i, j} khi 1 − P(không cạnh) > 0.5. SEA trả softmax ba lớp, hai hướng loại trừ nhau, nên một cạnh có hướng không chắc có thể bị cách đọc chính bỏ qua. Mọi contrast ở §4 được tính lại với cách đọc này và báo như mô tả, không vào Holm.

## 2. Dữ liệu và seed

- **(A) Tổng hợp, held-out mới:**
  - 8 ô như Study 2: d_T ∈ {10, 20}, e_T ∈ {1, 2}, tuyến tính và RFF; đồ thị ER; n = 500. Thứ tự ô như Study 2; các ô tuyến tính là 0, 2, 4, 6;
  - khối đích sinh bằng bộ sinh đã đóng băng của Study 1, seed `500000 + 1000·c + r`. Base 500000 chưa dùng ở pha nào; tập phát triển dùng base 510000;
  - đệm bằng bộ sinh đã đóng băng của Study 2: A20 là e = 0 (Gauss), S20 là e = e_T (có cấu trúc), k = 20;
  - số hệ: **15 mỗi ô, tổng 120** (r = 0, …, 14); 60 hệ tuyến tính;
  - chỉ số hệ i = 15·c + r;
  - **seed của SEA:**
    - lượt chính của hệ i: a_i = 600000 + i, dùng chung cho k0, A20 và S20;
    - lượt tham chiếu ở k0: b_{i,m} = 610000 + 10·i + m, với m = 1, …, 4 (**M = 4**).
- **(B) Bảng thật:**
  - input k0 và đệm Gauss ở k = 20 của Study 4, 20 lần sinh mỗi bảng, sinh lại bằng `assemble5` đã đóng băng. Mã băm phải khớp `inputs5.json`;
  - bảng j: Sachs là j = 0, Wine là j = 1. Lần sinh r = 0, …, 19;
  - **seed của SEA:**
    - lượt chính của lần sinh r: a_{j,r} = 620000 + 100·j + r, dùng chung cho k0 và input đệm r;
    - lượt tham chiếu ở k0: b_{j,r,m} = 630000 + 1000·j + 10·r + m, m = 1, …, 4.
- **Cỡ mẫu:** bốn seed tham chiếu được lấy trung bình trong mỗi đơn vị. Đơn vị độc lập vẫn là 120 hệ ở phần A và 20 lần sinh mỗi bảng ở phần B; seed tham chiếu không làm cỡ mẫu thành 480 hay 80.
- **Tập phát triển** (cổng ở §6): cùng công thức seed, cộng thêm 1 000 000.
- **Đối chứng cổ điển:**
  - (A) PC (Fisher-z, α = 0.05, stable) và GES (BIC Gauss), causal-learn, ở k0 và A20. Chỉ đọc trên hệ tuyến tính, như Study 1. Không chạy trên S20;
  - (B) output PC và GES của Study 4, chỉ dùng cho contrast mô tả.

## 3. Biến đo

- **flips(X, Y):** số cặp khối đích có trạng thái skeleton khác nhau giữa hai output X và Y.
- **Δ, chênh lệch khoảng cách trung bình tới các output k0 tham chiếu,** của một đơn vị u (hệ i ở phần A; lần sinh r ở phần B) với input đệm X:

  Δ_u = (1/4) Σ_m [flips(k0@b_{u,m}, X@a_u) − flips(k0@b_{u,m}, k0@a_u)]

  - Số hạng đầu: khoảng cách trung bình từ output đệm tới các output k0 tham chiếu. Số hạng sau: khoảng cách trung bình từ output k0 cùng seed tới chính các output tham chiếu đó.
  - Mỗi số hạng chỉ so hai lượt có seed khác nhau. Vì vậy tính chất "phân phối không đổi thì E[Δ_u] = 0" vẫn đúng khi X@a_u và k0@a_u có liên hệ với nhau do dùng chung seed. Chiều ngược lại không đúng (§0).
- **Hại:** H_i = F1(k0@a_i) − F1(A20@a_i), với F1 skeleton khối đích so với đồ thị thật (chỉ ở phần A).
- **Mô tả:**
  - flips cùng seed: flips(k0@a_u, X@a_u). Đây là thứ người dùng thấy khi chạy SEA hai lần với cùng seed;
  - flips chỉ do seed: flips(k0@b_{u,m}, k0@a_u);
  - contrast so với đối chứng cổ điển, như C11: flips(k0@a_u, X@a_u) − max(flips_PC, flips_GES) theo từng đơn vị (phần B, và phần A trên hệ tuyến tính). **Chỉ mô tả**;
  - Δp (trung bình |P − P(k0)| trên các cặp có thứ tự của khối đích); ΔTP và ΔFP; hại ở S20; số cạnh;
  - mọi contrast của §4 với cách đọc phụ 1 − P(không cạnh) > 0.5.

## 4. Giả thuyết (một family Holm riêng)

| ID | Phần | Contrast | Dự đoán | Biên M | Phép kiểm |
|---|---|---|---|---|---|
| P8-1 | A | Δ_i với X = A20 | > 0 | 1 cặp | t phân tầng một phía, 8 ô, trọng số bằng nhau |
| P8-1S | A | Δ_i với X = S20 | > 0 | 1 cặp | như trên |
| P8-2 | A | H_i | > 0 | 0.05 | t phân tầng một phía, 8 ô |
| P8-3 | A, hệ tuyến tính | H_SEA,i − max(H_PC,i, H_GES,i) | > 0 | 0.05 | t phân tầng một phía, 4 ô tuyến tính |
| P8-4S | B, Sachs | Δ_r với X = input đệm r | > 0 | 1 cặp | t một phía, df = 19 |
| P8-4W | B, Wine | như trên | > 0 | 1 cặp | như trên |

**Phép kiểm và nhãn:**

- t phân tầng như Study 2: trọng số bằng nhau cho các ô, df Welch–Satterthwaite.
- Holm ở mức familywise 0.05 trên đúng sáu p-value. Family này tách riêng khỏi các study khác.
- SE = 0: DEGENERATE, p = 1, không xác nhận.
- **Label:** CONFIRMED hoặc NOT_CONFIRMED theo Holm. CONFIRMED là kết luận về dấu.
- **Size**, như Study 6 (`stats7.py`), với CI 95%:
  - SMALL khi CI nằm trong (−M, M);
  - LARGE khi CI nằm trọn trên M hoặc trọn dưới −M;
  - UNCLEAR trong các trường hợp còn lại.
- **Biên:** 1 cặp cho Δ, như flips ở Studies 1, 4 và 6. 0.05 cho P8-2 và P8-3, thống nhất với HARM và BEYOND_CLASSICAL của Study 1.
- **Bảng kết quả có hai cột Label và Size.** Không có cột "Outcome" và không có nhãn tổng hợp nào khác.

**Cách đọc:**

- **Δ > 0, CONFIRMED:** output sau khi thêm đệm nằm xa các output k0 tham chiếu hơn output k0 cùng seed, theo flips.
- **Δ, Size SMALL:** contrast Δ nằm trong ±1 cặp. **Không** gọi là "SEA ổn định trong biên".
- **Δ âm** có thể phản ánh một thay đổi (§0). Không diễn giải thành "không có tác động".
- **NOT_CONFIRMED** không chứng minh không có hiệu ứng.
- **H, CONFIRMED:** F1 skeleton giảm khi thêm 20 cột Gauss, ở mức dấu. Vượt biên 0.05 chỉ khi Size là LARGE.
- Size và CI là mô tả, không được Holm bảo vệ, và không phải phép kiểm tương đương.

## 5. Cỡ mẫu và power (phân tích kịch bản, không phải chứng minh)

- N = 15 hợp lý hơn N = 10 trong ngân sách này, nhưng **chưa được chứng minh là đủ power**. SD của các contrast của SEA chưa biết.
- Bảng dưới là kịch bản theo SD giả định.
  - Cột "dấu": hiệu ứng nhỏ nhất để phép kiểm một phía so với 0 đạt với xác suất 80%, ở mức Holm bảo thủ α/6.
  - Cột "LARGE": hiệu ứng cần để cận dưới CI 95% vượt biên M với xác suất 80%.
  - Phát hiện dấu khác 0 khác với kết luận hiệu ứng vượt biên thực tiễn.
  - SD 0.10 cho hại F1 lấy từ độ rộng CI của Study 1 cho AVICI, CDFM và FoundCause. Đó là các model tất định hoặc gần tất định; SD của SEA có thể lớn hơn.
- **Công thức** (mô hình phân tầng đồng phương sai: cùng SD σ và cùng N = 15 trong mọi ô, C ô):
  - phần A: SE = σ/√(C·N), ν = C·(N − 1). C = 8 cho P8-1, P8-1S, P8-2 (ν = 112); C = 4 cho P8-3 (ν = 56). Đây là df Welch–Satterthwaite khi các ô có cùng phương sai và cùng cỡ;
  - phần B: SE = σ/√20, ν = 19;
  - "dấu" = (t_{1−α/6, ν} + t_{0.80, ν}) · SE, với α = 0.05;
  - "LARGE" = M + (t_{0.975, ν} + t_{0.80, ν}) · SE.

| Giả thuyết | Đơn vị | SD giả định | Dấu | LARGE | M |
|---|---|---|---|---|---|
| P8-2 | 120 hệ, 8 ô | 0.10 | 0.030 | 0.076 | 0.05 |
| P8-3 | 60 hệ, 4 ô | 0.10 | 0.043 | 0.087 | 0.05 |
| P8-1, P8-1S | 120 hệ, 8 ô | 2 / 3 / 4 cặp | 0.60 / 0.90 / 1.20 | 1.52 / 1.77 / 2.03 | 1 |
| P8-4S, P8-4W | 20 lần sinh | 2 / 3 cặp | 1.56 / 2.34 | 2.32 / 2.98 | 1 |

- **Nhãn SMALL cho Δ** cần |Δ̂| + t_{0.975, ν} · SE < 1 cặp.
  - SD dưới khoảng 5.5 cặp ở phần A, và dưới khoảng 2.1 cặp ở phần B, chỉ là điều kiện cần về độ rộng CI (khi Δ̂ = 0).
  - Tâm CI còn phải đủ gần 0.

## 6. Cổng trên tập phát triển (tiêu chí ghi trước khi chạy)

Dữ liệu: base 510000, 2 hệ mỗi ô (16 hệ, r = 0, 1; chỉ số i = 15·c + r như §2), và 2 lần sinh đệm Gauss k = 20 trên bảng thay thế DEV5 (r = 0, 1, đúng tập DEV5 đã đóng băng của Study 4). Mọi tiêu chí dưới đây được khóa cùng luật, trước khi chạy cổng.

- **G1, adapter và lặp lại:**
  - nhãn `true` khớp đồ thị đã ghi, và AUROC do SEA tính khớp AUROC tính lại, trên mọi output có cả cạnh và không cạnh;
  - chạy lại một input với cùng seed trong tiến trình mới cho output trùng từng bit;
  - **output không phụ thuộc file đồ thị:** một input DEV chạy hai lần với cùng seed, một lần với đồ thị thật và một lần với đồ thị toàn số 0, phải cho xác suất trùng từng bit. Bảng thật không có ground truth, nên phần B dùng đồ thị toàn số 0; kiểm này phải đạt trước. Ở phần B, kiểm adapter chỉ gồm bố cục của `true`, vì AUROC không xác định.

  Không đạt → dừng, báo user. Lỗi cấu hình hoặc adapter được sửa rồi chạy lại cổng; không tinh chỉnh theo ground truth.
- **G2, khối đích và input:** khối đích trùng từng bit giữa các input của một hệ; mã băm input khớp input sinh lại. Không đạt → dừng.
- **G3, chẩn đoán hoán vị cột** (8 hệ r = 0, input A20):
  - ba lượt: input gốc ở seed a; cùng input với một hoán vị cột ở seed a; input gốc ở seed a′ = a + 500000;
  - hoán vị của hệ DEV i: π = `np.random.default_rng([20261123, 3, i]).permutation(D)`; input hoán vị là X[:, π]. Output được ánh xạ về thứ tự gốc bằng P_gốc[π[a], π[b]] = P_hoán vị[a, b];
  - Δp_perm = trung bình |P_perm − P| trên các cặp có thứ tự của khối đích; Δp_seed = trung bình |P(a′) − P(a)|. Báo cả flips;
  - **đạt** khi phân vị 95 qua 8 hệ của Δp_perm ≤ phân vị 95 của Δp_seed, như tiêu chí của FoundCause ở Study 1 (A5). Với 8 hệ, phân vị 95 (nội suy tuyến tính của numpy) gần giá trị lớn nhất;
  - đạt chỉ có nghĩa là mức đổi do hoán vị không vượt mức đổi do seed trên DEV. Đây là chẩn đoán, **không** chứng minh permutation equivariance;
  - **không đạt** → nhãn `POSITION_SENSITIVE`, như Study 1, trình bày theo đúng nghĩa chẩn đoán này: không phải kết luận rằng SEA có hay không có tính equivariance. Lượt chính vẫn chạy với protocol chính (đệm nối sau, khối đích ở cùng chỉ số trong mọi input). Thêm một điều kiện độ nhạy trên 40 hệ (r < 5), khoảng 0.5 h:
    - input: A20 của hệ i với cột xen ngẫu nhiên, π = `np.random.default_rng([20261123, 4, i]).permutation(D)`, chạy ở seed a_i;
    - phép so, khóa trước: A20 đệm xen so với A20 nối sau, trên cùng dữ liệu và cùng seed suy luận a_i, sau khi ánh xạ output về thứ tự biến gốc. Báo flips và Δp trên khối đích, như mô tả;
    - không có giả thuyết xác nhận nào cho nhánh này. Đệm xen không được mô tả là đã loại confound vị trí.
- **G4, chất lượng ở k0** (8 hệ tuyến tính của DEV, ô 0, 2, 4, 6, r = 0, 1):
  - F1 skeleton ở k0 với cách đọc NATIVE, so với đồ thị rỗng, đồ thị đầy đủ, PC và GES trên cùng hệ;
  - **đạt** khi F1 trung bình của SEA lớn hơn F1 trung bình của đồ thị đầy đủ, như Study 1 (A10);
  - **G4 dùng để giới hạn diễn giải, không loại giả thuyết.**
  - **Không đạt** → đối chiếu cấu hình với tài liệu của tác giả một lần. Nếu phát hiện lỗi cấu hình hoặc adapter, sửa lỗi rồi chạy lại cổng; không tinh chỉnh theo ground truth.
  - Nếu cấu hình đúng mà chất lượng vẫn yếu, ghi cờ `BASELINE_TOO_WEAK_FOR_THIS_HARM_TEST`. P8-2 và P8-3 vẫn được tính và báo cáo; Holm vẫn trên sáu giả thuyết.
  - Khi có cờ, phần diễn giải nêu rõ khả năng phát hiện hại có thể bị giới hạn bởi F1 nền thấp, và không dùng NOT_CONFIRMED làm bằng chứng về khả năng chống chịu.
  - G4 chỉ kiểm tám hệ tuyến tính, còn P8-2 gồm cả hệ RFF. Cờ này áp cho diễn giải của cả P8-2 và P8-3.
  - Luật đã khóa của Study 1 (A10) giữ nguyên; cách xử lý này chỉ áp cho Study 7.
- **G5, thời gian:** ước tính lượt chính từ thời gian đo ở cổng. Nếu vượt 1.5 lần ước tính ở §8 → báo user trước khi chạy.
- Ngoài F1 ở k0 cho G4, cổng không đọc Δ, H hay bất kỳ contrast nào của §4 trên dữ liệu DEV. Code đọc kết quả được chạy thử trên output DEV ở chế độ chỉ kiểm cấu trúc, không in giá trị, như G7 của Study 6.

## 7. Kiểm hoàn tất trước khi đọc

- Mọi job có đúng một trạng thái kết thúc, không có `error` hay `budget_stop`.
- Mỗi job chạy đúng một input, và seed ghi trong output khớp kế hoạch §2.
- Mã băm input khớp input sinh lại. Khối đích trùng từng bit giữa các input của cùng một hệ; với phần B, input khớp `inputs5.json`.
- **Kiểm adapter trên mọi output:** như G1.
- **Chạy lại từng bit:**
  - cuối mỗi lượt, chạy lại k0@a_i của hệ đầu tiên trong mỗi ô, và k0@a_{j,0} của mỗi bảng có trong lượt đó;
  - output phải trùng từng bit.
- **Mã băm:**
  - checkpoint, các file được git theo dõi của code SEA ở commit đã ghim, và code đánh giá phải khớp bản đóng băng, kiểm ở đầu và cuối lượt;
  - file rỗng `dummy` do `run_fci` của SEA tạo trong thư mục làm việc được bỏ qua.

## 8. Ngân sách và điều kiện dừng

**Thời gian mỗi tiến trình**, đo ở bước 2 trên máy chạy (i3-1005G1, 2 nhân, RAM 7.8 GB, chỉ CPU), bằng thời gian SEA tự ghi cộng khoảng 9 s:

| D | 10 | 11 | 20 | 30 | 31 | 40 |
|---|---|---|---|---|---|---|
| Ước tính (s) | 20 | 22 | 24 | 34 | 41 | 62 |

**Ước tính với N = 15, M = 4:**

| Lượt | Nội dung | Số tiến trình | Ước tính | Mốc dừng (1.5 lần) |
|---|---|---|---|---|
| A1 | 2 ô d_T = 10, tuyến tính | 210 | 1.4 h | 2.1 h |
| A2 | 2 ô d_T = 10, RFF | 210 | 1.4 h | 2.1 h |
| A3 | 2 ô d_T = 20, tuyến tính | 210 | 2.0 h | 3.0 h |
| A4 | 2 ô d_T = 20, RFF | 210 | 2.0 h | 3.0 h |
| B | Sachs và Wine | 240 | 1.7 h | 2.5 h |

- Tổng lượt chính: khoảng 8.6 h CPU, chạy tuần tự. PC và GES thêm vài phút.
- Cổng trên tập phát triển (§6): khoảng 0.9 h. Nếu G3 không đạt, điều kiện độ nhạy thêm khoảng 0.5 h.
- Bộ nhớ: peak working set tối đa đo được là 2.4 GB, cho một lượt 11 input có D tới 51. Chạy riêng một input D = 10 cần 0.36 GB.
- Mốc dừng tính từ cổng đầu lượt. Vượt mốc thì dừng và báo user.
- **Dừng sớm khi:**
  - chạy lại không trùng từng bit;
  - adapter không đạt;
  - một job lỗi.
- Không chạy việc nặng nào song song với các lượt này. Bật chống ngủ máy như các study trước.

## 9. Quy trình

1. User review v0.2 (xong ngày 23/11, kèm các sửa ở §10).
2. Khóa v1: commit và push trước khi SEA chạy trên bất kỳ input nào của §2 hoặc của tập phát triển base 510000.
3. Viết code; chạy cổng G1–G5 trên tập phát triển. Đóng băng code cùng phụ thuộc; commit và push.
4. Các lượt chính trong ngân sách; kiểm hoàn tất; đọc bằng code đã đóng băng; kiểm lại độc lập.
5. Báo cáo theo cam kết ở đầu file.

## 10. Nhật ký (append-only sau khi khóa)

- **v0, 23/11/2026:** nháp, theo đề xuất ba bước của user.
- **v0.1, 23/11/2026:** sửa sau bước 2 (chỉ dữ liệu phát triển; chưa có output SEA nào trên dữ liệu của §2):
  - mỗi input chạy riêng một tiến trình, vì output phụ thuộc thứ tự input khi chạy chung một file (đã kiểm, max|Δp| = 0.48);
  - seed ghi trước cho từng đơn vị, thay cho seed 0 chung, vì ở một seed cố định, mọi input cùng D dùng chung nửa ngẫu nhiên của lịch (đọc code);
  - P8-1: từ "flips(A20) > 1 cặp" sang Δ. Ngưỡng 1 cặp có nguy cơ chủ yếu phản ánh biến động lịch suy luận, vì chỉ đổi seed đã làm skeleton đổi 2–4 cặp ở k0 trên 3 bảng phát triển;
  - P8-4S/W: từ so với đối chứng cổ điển sang Δ. Contrast cổ điển có nguy cơ chủ yếu phản ánh biến động lịch suy luận: ở Study 4, đối chứng cổ điển đổi 0.10–0.20 cặp, nhỏ hơn nhiều mức đổi chỉ do seed của SEA trên dữ liệu phát triển. Contrast này được giữ làm mô tả;
  - thêm P8-1S (S20); điền ngân sách đo được.
  - Đã thấy trước khi viết v0.1: contrast đối xứng trên 3 bảng phát triển (bước 2 §4). Kết quả đó không được dùng để chọn chiều của giả thuyết.
- **v0.2, 23/11/2026, theo quyết định của user** (chưa có output SEA nào trên dữ liệu của §2):
  - **thiết kế:** phương án II (hệ mới, seed riêng cho từng đơn vị), N = 15 mỗi ô (120 hệ), M = 4; giữ P8-1S; P8-3 giữ trong family xác nhận; contrast cổ điển trên bảng thật chỉ mô tả; Study 7 với bảng riêng;
  - **diễn giải Δ sửa lại:** Δ là chênh lệch khoảng cách trung bình tới các output k0 tham chiếu. E[Δ] = 0 khi phân phối không đổi, nhưng chiều ngược lại không đúng (ví dụ ở §0). SMALL không gọi là "ổn định trong biên"; Δ âm không diễn giải thành không có tác động. Bỏ cột Outcome và ba nhãn tổng hợp của v0.1; giữ Label và Size;
  - **biên của P8-2 và P8-3:** 0.05 (v0.1 ghi 0.03), thống nhất với HARM và BEYOND_CLASSICAL của Study 1;
  - **đọc phụ 1 − P(không cạnh) > 0.5:** phân tích độ nhạy định trước;
  - **thêm vào cổng:** chẩn đoán hoán vị cột (G3) và chất lượng ở k0 (G4), với tiêu chí đạt và cách xử lý thất bại ghi trước;
  - **thêm giới hạn:** nguồn sinh dữ liệu của AVICI; khoảng huấn luyện của SEA (bài SEA §4.1, Appendix B.1: N = 10, 20, 100; Linear và NN; không có RFF); n = 500 bằng kích thước lô; thứ tự hai sampler trong code ngược với mô tả ở Appendix B.6;
  - **power:** bảng kịch bản theo SD giả định (§5); N = 15 chưa được chứng minh là đủ power.
- **v1, 23/11/2026, KHÓA.** User duyệt v0.2: GO cho thiết kế; N = 15, M = 4 và cách diễn giải Δ được duyệt. v1 = v0.2 cộng đúng các sửa sau:
  - **G4:** dùng để giới hạn diễn giải, không loại giả thuyết. Nếu cấu hình đúng mà chất lượng vẫn yếu, ghi cờ `BASELINE_TOO_WEAK_FOR_THIS_HARM_TEST`, vẫn tính và báo P8-2 và P8-3, Holm vẫn trên sáu giả thuyết. Không dùng NOT_CONFIRMED làm bằng chứng về khả năng chống chịu. Luật đã khóa của Study 1 giữ nguyên;
  - **G3:** ghi công thức hoán vị; nhãn `POSITION_SENSITIVE` mang nghĩa chẩn đoán; khóa phép so của nhánh đệm xen (cùng dữ liệu, cùng seed suy luận, ánh xạ về thứ tự gốc, flips và Δp như mô tả, không có giả thuyết xác nhận);
  - **§5:** ghi rõ công thức với ngưỡng t và df giả định, thay cho "xấp xỉ chuẩn"; số trong bảng tính lại theo công thức đó; điều kiện SMALL là |Δ̂| + t_{0.975, ν} · SE < 1, còn ngưỡng SD chỉ là điều kiện cần về độ rộng CI;
  - **§0:** trong ví dụ một cạnh, viết E[Δ] = 0 thay cho Δ = 0;
  - **hai chỉnh kỹ thuật của agent, không đổi giả thuyết hay phép kiểm:**
    - G1 thêm kiểm output không phụ thuộc file đồ thị. Phần B cần đồ thị toàn số 0, vì bảng thật không có ground truth; SEA chỉ dùng đồ thị để tính metric của chính nó;
    - cổng dùng 2 lần sinh đệm của DEV5 (r = 0, 1), đúng tập đã đóng băng của Study 4, thay cho "3 lần sinh" của v0.2.
