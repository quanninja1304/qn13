# P-N8, bước 2: kiểm khả thi SEA trên dữ liệu phát triển (23/11/2026)

> **Mục đích** (theo đề xuất của user, lượt 10): nạp đúng checkpoint FCI, chạy trên dữ liệu DEV, rồi kiểm adapter, RAM, thời gian và tính lặp lại.
>
> **Mức bằng chứng:** ghi chép kỹ thuật, chỉ dùng dữ liệu phát triển.
>
> - Không dùng hai bảng thật, không dùng tập held-out nào, không dùng base 500000.
> - Không kết luận gì về độ ổn định của SEA. Số flips và F1 ở §2 và §4 là mô tả trên 3 bảng phát triển.
> - Kết quả ở đây đã làm thay đổi bản nháp luật bước 3 (v0.1 và v0.2, xem nhật ký trong `PN8_rules_vi.md`). Mọi giả thuyết được kiểm trên hệ mới hoặc trên bảng thật mà SEA chưa từng chạy.

## 1. Thiết lập

**Code và checkpoint:**

- repo `rmwu/sea-reproduce`, commit `bfb507b002d7f066f307a0dc15bd23fc703848b4`, clone trong `artifacts/n8_runs/sea_src/` (git bỏ qua);
- checkpoint `checkpoints/fci_synthetic/model_best_epoch=373_auprc=0.842.ckpt`, SHA-256 `fa1a1d39d9c019fe045282c7455ea33fbc624552cfb3d9516d6966c185f3bcc0`;
- cấu hình `config/aggregator_tf_fci.yaml`, SHA-256 `3f22a75d5d833deb98ba9e84b1f6de0955770555b34cdc14ff8670e26dabc746`. Bản sao chỉ đổi `data_file`, `results_file` và `num_workers: 0`;
- script suy luận `src/inference.py` của SEA, chạy nguyên bản qua `runpy`, với `--gpu -1` (CPU) và `--seed s`.

**Môi trường** (`artifacts/n8_runs/sea_env/`): Python 3.10.21, torch 1.13.1+cpu, pytorch-lightning 1.9.0, torchmetrics 1.3.0, causal-learn 0.1.3.7, numpy 1.23.5, scipy 1.10.1, scikit-learn 1.2.2, setuptools 69.5.1.

- setuptools được ghim ở 69.5.1 vì pytorch-lightning 1.9.0 cần `pkg_resources`.
- Code tải về được chạy với `python -E -s`.

**Máy:** Intel Core i3-1005G1 (2 nhân, 4 luồng), RAM 7.8 GB, chỉ CPU, một tiến trình, không chạy việc nặng nào song song.

**Input phát triển** (11 input, `artifacts/n8_runs/sea_adapter/make_inputs.py`, sinh bằng bộ sinh đã đóng băng):

- bảng thay thế DEV5 của Study 4 (d = 11): k0; đệm Gauss k = 20 (hai lần sinh); đệm có cấu trúc k = 20; đệm Gauss k = 40;
- hai hệ DEV2 của Study 2: DEV2-c0-r0 (d_T = 10, tuyến tính, e_T = 1) và DEV2-c7-r1 (d_T = 20, RFF, e_T = 2), mỗi hệ ở k0, e = 0 (Gauss) và e = e_T (có cấu trúc), k = 20.

**Các lượt chạy:**

- A (seed 0), B (seed 0, chạy lại) và C (seed 1): mỗi lượt chạy cả 11 input trong một file CSV, theo cùng thứ tự;
- hai lượt chạy riêng một input, seed 0: bảng thay thế ở k0, và DEV2-c0-r0 ở k0.

**Code:** bản sao trong `dev_code/`. Các script nhận đường dẫn qua tham số, không có đường dẫn cứng.

- `make_inputs.py`: viết input;
- `sea_wrapper.py`: chạy SEA, đo thời gian và bộ nhớ;
- `read_results.py`: §2;
- `order_check.py`: kiểm phụ thuộc thứ tự;
- `dev_contrast.py`: §4.

**Đọc kết quả** (`read_results.py`, môi trường của Study 1):

- skeleton NATIVE: cạnh {i, j} khi max(P(i→j), P(j→i)) > 0.5, đọc trên khối đích;
- flips đếm trên các cặp không thứ tự của khối đích: 55 cặp với d_T = 11, 45 với d_T = 10, 190 với d_T = 20.

## 2. Kết quả kiểm

| Input | D | Layout `true` | AUROC | A = B từng bit | Seed 1: max\|Δp\| | Seed 1: flips | Số cạnh | F1 | flips so với k0 (lượt A) | Thời gian (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| bảng thay thế, k0 | 11 | khớp | khớp | có | 0.474 | 3 | 11 | 0.667 | 0 | 13.3 |
| Gauss k = 20, lần sinh 0 | 31 | khớp | khớp | có | 0.214 | 0 | 8 | 0.571 | 3 | 35.5 |
| Gauss k = 20, lần sinh 1 | 31 | khớp | khớp | có | 0.380 | 0 | 10 | 0.696 | 3 | 30.7 |
| có cấu trúc k = 20 | 31 | khớp | khớp | có | 0.477 | 3 | 11 | 0.667 | 4 | 28.5 |
| Gauss k = 40 | 51 | khớp | khớp | có | 0.510 | 0 | 10 | 0.696 | 3 | 105.3 |
| DEV2-c0-r0, k0 | 10 | khớp | khớp | có | 0.320 | 2 | 10 | 0.700 | 0 | 10.4 |
| DEV2-c0-r0, e = 0 | 30 | khớp | khớp | có | 0.310 | 2 | 7 | 0.588 | 5 | 24.6 |
| DEV2-c0-r0, e = 1 | 30 | khớp | khớp | có | 0.720 | 3 | 9 | 0.737 | 5 | 25.1 |
| DEV2-c7-r1, k0 | 20 | khớp | khớp | có | 0.356 | 4 | 30 | 0.686 | 0 | 14.7 |
| DEV2-c7-r1, e = 0 | 40 | khớp | khớp | có | 0.490 | 6 | 32 | 0.694 | 8 | 48.1 |
| DEV2-c7-r1, e = 2 | 40 | khớp | khớp | có | 0.514 | 6 | 27 | 0.687 | 3 | 57.9 |

Cột "Seed 1" so lượt C với lượt A trên cùng input. Số cạnh, F1 và thời gian lấy từ lượt A. Thời gian là thời gian SEA tự ghi cho từng input.

**Adapter (đã kiểm):**

- Ở cả 11 input, vector `true` mà SEA trả về khớp đồ thị đã ghi trong `DAG.npy`, theo bố cục [P(i→j) với i < j] + [P(j→i) với i < j].
- AUROC do SEA tính khớp AUROC tính lại bằng scikit-learn, sai khác dưới 1e-6.

**Lặp lại (đã kiểm):**

- Lượt A và lượt B (cùng seed 0, cùng file CSV) cho output trùng từng bit ở cả 11 input.
- Chạy riêng bảng thay thế ở k0 với seed 0 cũng cho output trùng từng bit với input đó ở lượt A. Ở lượt A, input này đứng đầu.

**Phụ thuộc thứ tự (đã kiểm):**

- Chạy riêng DEV2-c0-r0 ở k0 với seed 0 cho output **khác** input đó ở lượt A, nơi nó đứng thứ sáu. max|Δp| là 0.48.
- Nguyên nhân (đọc code, §3): seed được đặt một lần cho cả lượt, và mọi input dùng chung dòng số ngẫu nhiên toàn cục.
- Vì vậy, ở lượt A, B và C, lịch của mỗi input phụ thuộc vị trí của nó trong file. So sánh giữa hai input trong cùng một lượt là so sánh giữa hai lịch khác nhau.

**Độ nhạy theo seed (đã đo, mô tả):**

- Chỉ đổi seed, input giữ nguyên: skeleton khối đích đổi 0–6 cặp. Ở k0 là 3 trên 55 cặp, 2 trên 45 và 4 trên 190.
- max|Δp| trên khối đích là 0.21–0.72.
- Thêm cột độc lập (so trong lượt A): đổi 3–8 cặp. Con số này gồm cả phần do lịch đổi, nên chưa tách được phần do đệm.

**Thời gian và bộ nhớ (đã đo trên máy trên):**

- Thời gian mỗi input tăng nhanh theo D: khoảng 10–15 s với D = 10–20, 25–36 s với D = 30–31, 48–58 s với D = 40, 105 s với D = 51.
- Mỗi tiến trình mất thêm khoảng 9 s cho import, nạp dữ liệu và nạp model. Lượt chạy riêng DEV2-c0-r0 ở k0 mất 19.7 s, trong đó SEA tự ghi 10.6 s.
- Tổng thời gian của ba lượt 11 input: 406.5 s, 372.3 s và 347.1 s. Cùng một việc, thời gian lệch nhau tới 17%.
- Peak working set: 2.2–2.4 GB cho lượt 11 input (có input D = 51); 0.36 GB cho lượt chạy riêng một input D = 10.

**Ghi chú phụ:**

- `run_fci` của SEA chuyển hướng output của FCI vào một file rỗng tên `dummy` trong thư mục làm việc (`src/data/utils.py`, dòng 118 và 144). File này xuất hiện trong bản clone, không thuộc code đã ghim.
- torchmetrics 1.3.0 có cảnh báo "yanked" khi cài. Không thấy lỗi lúc chạy.

## 3. Cơ chế ngẫu nhiên của SEA lúc suy luận (đọc code, commit `bfb507b`)

- `src/inference.py`: `set_seed(args.seed)` đặt seed cho `random`, `numpy` và `torch` một lần, trước khi nạp model.
- `InferenceDataModule.predict_dataloader`: `batch_size = 1`, `shuffle=False`. Input được xử lý theo thứ tự trong file CSV.
- `TestDataset.__getitem__` lấy mẫu từ dòng `np.random` toàn cục, không đặt lại seed cho từng input.
- **Trong mỗi lô** (`ObservationalSampler.sample_batches`):
  - hàng: `np.random.choice(n, 500, replace=False)`. Với n = 500, đó là một hoán vị của mọi hàng, nên lô nào cũng dùng đủ 500 hàng;
  - biến: năm lần `np.random.choice(len(p), 1, p=p)`, mỗi lần tiêu một số ngẫu nhiên;
  - `CorrelationSampler.compute_scores` rút thêm một hoán vị 500 hàng mỗi lô, rồi tính |pinv cov| trên mọi hàng.
- **Hệ quả** (suy ra từ code, chưa kiểm bằng chạy):
  - Số lượng số ngẫu nhiên tiêu cho mỗi lô chỉ phụ thuộc n, không phụ thuộc D.
  - Ở nửa đầu (`RandomSampler`), điểm của mọi cặp là 1. Vì vậy, với cùng seed và cùng D, 250 tập biến của nửa đầu giống hệt nhau, bất kể dữ liệu. Ví dụ: ở seed 0, 20 lần sinh đệm của cùng một bảng (cùng D = 31) dùng chung 250 tập biến đầu.
  - Với n = 500, thống kê toàn cục (pinv cov trên mọi hàng) không phụ thuộc seed. Seed chỉ quyết định tập biến của từng lô.

## 4. So sánh mô tả trên dữ liệu phát triển (EXPLORATORY)

Lượt A và lượt C cho mỗi input hai lịch độc lập. Phép so dưới đây đặt mức đổi do đệm cạnh mức đổi chỉ do lịch.

- **Contrast đối xứng:** flips(k0 ở lịch C, input đệm ở lịch A) − flips(k0 ở lịch C, k0 ở lịch A); và tương tự khi đổi vai A với C.
- Nếu đệm không đổi phân phối output, kỳ vọng của contrast này là 0. Chiều ngược lại không đúng: contrast bằng 0 hoặc âm vẫn có thể đi cùng một phân phối output đã đổi (ví dụ ở luật v0.2 §0).

| Bảng gốc | Seed-only flips ở k0 | Input đệm | flips cùng lượt (A; C) | Contrast đối xứng (hai giá trị) | F1 k0 (A; C) | F1 đệm (A; C) |
|---|---|---|---|---|---|---|
| bảng thay thế (55 cặp) | 3 | Gauss k = 20, lần sinh 0 | 3; 2 | −1; 0 | 0.667; 0.696 | 0.571; 0.571 |
| | | Gauss k = 20, lần sinh 1 | 3; 0 | −3; 0 | | 0.696; 0.696 |
| | | có cấu trúc k = 20 | 4; 2 | −2; 0 | | 0.667; 0.609 |
| | | Gauss k = 40 | 3; 0 | −3; 0 | | 0.696; 0.696 |
| DEV2-c0-r0 (45 cặp) | 2 | e = 0 | 5; 5 | +5; +3 | 0.700; 0.636 | 0.588; 0.588 |
| | | e = 1 | 5; 6 | +5; +6 | | 0.737; 0.700 |
| DEV2-c7-r1 (190 cặp) | 4 | e = 0 | 8; 10 | +6; +4 | 0.686; 0.686 | 0.694; 0.667 |
| | | e = 2 | 3; 11 | +3; +5 | | 0.687; 0.648 |

**Đọc (suy luận, chưa kiểm; chỉ 3 bảng):**

- Trên bảng thay thế, contrast không dương: output đệm không nằm xa các output k0 ở lịch khác hơn output k0 của lịch còn lại. Điều này không có nghĩa là đệm không tác động. Ở lượt C, hai input đệm cho skeleton trùng hẳn với k0.
- Trên hai hệ DEV2, contrast là +3 đến +6 cặp: output đệm nằm xa các output k0 ở lịch khác hơn.
- Phép so này không bị định sẵn theo một chiều. Vì vậy nó có thể dùng làm contrast chính ở bước 3. Kết quả trên 3 bảng này không được dùng để chọn chiều của giả thuyết.

## 5. Hệ quả cho bước 3 (suy luận, đưa vào nháp v0.1)

1. **Mỗi input chạy riêng trong một tiến trình mới**, với script suy luận nguyên bản và seed ghi trước. Nếu không, output phụ thuộc thứ tự input trong file (đã kiểm ở §2).
2. **Ngưỡng 1 cặp của v0 (P8-1) có nguy cơ chủ yếu phản ánh biến động lịch suy luận.** Chỉ đổi seed đã làm skeleton đổi 2–4 cặp ở k0 trên 3 bảng phát triển. Ba bảng này chưa đủ để biết chắc kết quả của lượt chính.
3. **So với đối chứng cổ điển trên bảng thật cũng có nguy cơ chủ yếu phản ánh biến động lịch suy luận.** Ở Study 4, max(PC, GES) đổi trung bình 0.20 cặp (Sachs) và 0.10 cặp (Wine), còn SEA đổi 3 cặp chỉ do seed trên bảng thay thế d = 11. Contrast này vẫn được báo cáo để đặt cạnh C11, nhưng chỉ như mô tả.
4. **Không cố định seed 0 cho mọi đơn vị.** Ở một seed cố định, mọi input cùng D dùng chung nửa đầu của lịch (§3). Kết luận khi đó chỉ đúng cho một lịch. Nháp v0.1 gán cho mỗi đơn vị (hệ, hoặc lần sinh đệm) một seed riêng, ghi trước.
5. **Contrast chính cho thay đổi skeleton là contrast đối xứng ở §4**, so với nhiều seed tham chiếu ở k0. Khi đệm không đổi phân phối output, kỳ vọng của nó đúng bằng 0, kể cả khi các lượt cùng seed có liên hệ với nhau. Chiều ngược lại không đúng. Vì vậy, từ v0.2, Δ được đọc là chênh lệch khoảng cách trung bình tới các output k0 tham chiếu, không phải độ ổn định sau khi loại nhiễu seed.
6. **Hại F1 không cần điều chỉnh.** F1(k0) − F1(đệm) là hiệu hai kỳ vọng biên, nên nhiễu do lịch chỉ làm tăng phương sai, không gây lệch.

## 6. Thời gian ước tính cho bước 3

Thời gian mỗi tiến trình ≈ thời gian SEA đo ở §2 + 9 s.

| D | 10 | 11 | 20 | 30 | 31 | 40 |
|---|---|---|---|---|---|---|
| Ước tính mỗi tiến trình (s) | 20 | 22 | 24 | 34 | 41 | 62 |

Mỗi hệ hay mỗi lần sinh có 1 + m lượt ở k0, trong đó m là số seed tham chiếu. Phần A có thêm A20 và S20 cho mỗi hệ; phần B có thêm input đệm cho mỗi lần sinh.

| Phương án | Phần A (8 ô) | Phần B (2 bảng × 20 lần sinh) | Tổng lượt chính |
|---|---|---|---|
| N = 10 mỗi ô, m = 4 | 4.6 h | 1.7 h | 6.3 h |
| N = 10 mỗi ô, m = 2 | 3.6 h | 1.2 h | 4.8 h |
| N = 15 mỗi ô, m = 4 | 6.9 h | 1.7 h | 8.6 h |

- PC và GES ở k0 và A20 (đệm Gauss) không đáng kể. Theo nhật ký của Study 2 (`pn2_out/ges/log_EXP2.jsonl`, `pc/log_EXP2.jsonl`, 40 hệ tuyến tính), mỗi lần gọi mất tối đa 6.1 s, trung bình 0.2–3.4 s.
- Với đệm có cấu trúc, GES có lần mất tới 384 s. Nháp v0.1 không chạy đối chứng cổ điển trên S20.
- Cổng trên tập phát triển (base 510000, một hệ mỗi ô, cộng 3 lần sinh trên bảng thay thế): khoảng 35 phút.
- Thời gian thực có thể lệch tới khoảng 17% (§2). Nháp v0.1 đặt mốc dừng của mỗi lượt ở 1.5 lần ước tính.
