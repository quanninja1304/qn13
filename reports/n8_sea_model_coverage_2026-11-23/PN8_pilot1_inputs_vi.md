# P-N8, bước 1: pilot không chạy mạng cho SEA (23/11/2026)

> **Mục đích** (theo đề xuất của user, lượt 10): đo hai đại lượng trung gian phía input của SEA khi thêm cột độc lập:
>
> - độ phủ của từng cặp đích theo đúng sampler của SEA;
> - độ trôi của thống kê toàn cục mà aggregator nhận.
>
> **Mức bằng chứng:** EXPLORATORY.
>
> - Không chạy mạng của SEA, nên không kết luận gì về output của SEA.
> - Pilot không dùng để chọn giả thuyết cho bước 3. Nếu sau này có giả thuyết nào lấy từ pilot, phần xác nhận phải dùng dữ liệu mới.
>
> **Dữ liệu:**
>
> - input EXP2 của Study 2: 40 hệ exploratory, k0, e = 0 (Gauss) và e = e_T (có cấu trúc), k = 20;
> - bảng thay thế DEV5 của Study 4: d = 11; k0, đệm Gauss và có cấu trúc ở k = 20 và k = 40, hai lần sinh.
>
> **Không dùng hai bảng thật**, để bước 3 có thể đánh giá SEA trên chúng mà dữ liệu đó chưa định hướng điều gì.

## 1. SEA làm gì lúc suy luận (đọc code, commit `bfb507b`)

Nguồn:

- repo `rmwu/sea-reproduce` (link `github.com/rmwu/sea` dẫn tới đây), clone vào `artifacts/n8_runs/sea_src/` (git bỏ qua);
- GitHub không ghi nhận giấy phép nào (`license: null`).

**Cấu hình FCI** (`config/aggregator_tf_fci.yaml`):

- `fci_batches_inference: 500`, `fci_vars: 5`, `fci_batch_size: 500`, `use_learned_sampler: False`;
- checkpoint `checkpoints/fci_synthetic/model_best_epoch=373_auprc=0.842.ckpt`.

**Sampler** (`src/data/dataset.py`, `get_samplers`; `src/data/samplers.py`): khi không dùng sampler học được, có hai sampler nối tiếp, mỗi cái 250 lô.

- `RandomSampler`: mọi cặp có điểm 1.
- `CorrelationSampler`: điểm là |inverse covariance| tính trên 500 hàng chọn ngẫu nhiên. Với bảng 500 hàng, đó là cả bảng.
- Số lần thăm của từng cặp được chuyển từ sampler đầu sang sampler sau.

**Chọn biến của mỗi lô** (`sample_nodes`):

- điểm chung = điểm / √(1 + số lần thăm);
- biến đầu tiên có xác suất tỉ lệ với tổng điểm của nó với **mọi** biến;
- mỗi biến tiếp theo có xác suất tỉ lệ với tổng điểm của nó với các biến đã chọn.

**Thống kê toàn cục** (`compute_features`):

- `np.linalg.pinv(np.cov(x), rcond=1e-10)` trên **mọi** biến (dưới 100 biến), tính trên lô hàng cuối của sampler đầu;
- từ 100 biến trở lên thì dùng ước lượng precision của Ledoit–Wolf.

**Trên mỗi lô:**

- FCI của causal-learn, Fisher-z, α = 0.05, trên 5 biến và 500 hàng;
- aggregator nhận kết quả của các lô, danh sách cặp đã được phủ và thống kê toàn cục.

**Output:**

- mỗi cặp có softmax trên ba lớp: không cạnh, i→j, j→i;
- hàm đánh giá của SEA dùng ngưỡng 0.5 cho từng hướng;
- không có ràng buộc acyclic.

**Ghi chú:** các khóa của file cấu hình ghi đè tham số dòng lệnh (`process_args`), và cấu hình gốc đặt `num_workers: 40`.

## 2. Cách làm

- Viết lại sampler bằng numpy, theo đúng thứ tự gọi trong code: không import code của SEA.
- Script, bản sao trong `dev_code/`:
  - `sea_input_pilot.py` chạy pilot;
  - `summarize_pilot.py` tính các bảng ở §3. Script pilot ghi tóm tắt của đệm có cấu trúc vào khóa `eT`, đè lên số e_T của ô. Vì vậy `summarize_pilot.py` lấy ô từ mã hệ.
- Năm seed của sampler (0–4) cho mỗi input. Các số dưới đây là trung bình qua hệ và qua seed.
- Dòng số ngẫu nhiên không trùng từng bit với một lượt chạy thật của SEA. Trong lượt thật, việc lấy mẫu nằm trong DataLoader. Pilot chỉ tái lập phân phối của sampler.
- **Độ phủ của một cặp đích:** số lô trong 500 lô chứa cả hai đầu của cặp.
- **Độ trôi của thống kê toàn cục:** partial correlation của cặp đích tính từ inverse covariance toàn cục, ρ_ij = −Θ_ij/√(Θ_ii Θ_jj). Đo bằng trung bình |ρ_ij(k) − ρ_ij(k0)| trên các cặp đích.

## 3. Kết quả (EXPLORATORY)

**EXP2, 5 hệ mỗi ô:**

| d_T | Họ | e_T | Độ phủ k0 | Gauss k = 20 | Có cấu trúc | Gauss/k0 | Cấu trúc/k0 | Tỉ lệ lượt chọn vào biến đích (Gauss; cấu trúc) | Nửa sau / nửa đầu (Gauss; cấu trúc) | Độ trôi ρ (Gauss; cấu trúc) | \|ρ\| ở k0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | lin | 1 | 111.1 | 46.6 | 14.9 | 0.42 | 0.13 | 0.60; 0.33 | 7.24; 1.62 | 0.0062; 0.0062 | 0.195 |
| 10 | rff | 1 | 111.1 | 31.1 | 16.8 | 0.28 | 0.15 | 0.50; 0.35 | 4.50; 1.98 | 0.0078; 0.0062 | 0.170 |
| 10 | lin | 2 | 111.1 | 58.3 | 22.7 | 0.52 | 0.20 | 0.65; 0.39 | 9.30; 3.01 | 0.0060; 0.0060 | 0.327 |
| 10 | rff | 2 | 111.1 | 34.6 | 12.7 | 0.31 | 0.11 | 0.52; 0.30 | 5.12; 1.24 | 0.0065; 0.0063 | 0.182 |
| 20 | lin | 1 | 26.3 | 14.5 | 9.0 | 0.55 | 0.34 | 0.71; 0.55 | 3.63; 1.86 | 0.0071; 0.0071 | 0.121 |
| 20 | rff | 1 | 26.3 | 10.8 | 6.1 | 0.41 | 0.23 | 0.63; 0.46 | 2.44; 0.95 | 0.0070; 0.0071 | 0.094 |
| 20 | lin | 2 | 26.3 | 15.8 | 7.2 | 0.60 | 0.27 | 0.74; 0.48 | 4.02; 1.28 | 0.0068; 0.0068 | 0.167 |
| 20 | rff | 2 | 26.3 | 12.0 | 7.5 | 0.46 | 0.28 | 0.66; 0.50 | 2.83; 1.39 | 0.0075; 0.0069 | 0.118 |

Trên cả 40 hệ: độ phủ còn 0.44 lần (Gauss) và 0.22 lần (có cấu trúc) so với k0. Tỉ lệ cặp đích không được phủ lần nào là 0.1% và 0.3%. Độ trôi ρ trung bình là 0.0069 và 0.0066.

**Bảng thay thế DEV5 (d = 11):**

| Input | Độ phủ | Thấp nhất | Không phủ | Tỉ lệ lượt chọn vào biến đích | Nửa đầu; nửa sau | Độ trôi ρ (trung bình; lớn nhất) |
|---|---|---|---|---|---|---|
| k0 | 90.9 | 42.6 | 0 | 1.00 | 45.5; 45.5 | 0; 0 |
| Gauss k = 20 (2 lần sinh) | 29.6; 28.8 | 4.4; 4.6 | 0; 0 | 0.54 | 5.3; 24.0 | 0.0065; 0.0063 (lớn nhất 0.029) |
| Gauss k = 40 | 15.8; 15.5 | 1.4; 1.6 | 0; 0.004 | 0.37 | 2.0; 13.6 | 0.0079; 0.0085 (lớn nhất 0.039) |
| Có cấu trúc k = 20 | 14.4; 14.2 | 3.0; 2.6 | 0; 0 | 0.37 | 5.3; 9.0 | 0.0052; 0.0073 |
| Có cấu trúc k = 40 | 5.9; 5.5 | 0.0; 0.4 | 0.029; 0.022 | 0.22 | 2.0; 3.6 | 0.0089; 0.0069 |

## 4. Đọc kết quả (suy luận, chưa kiểm)

- **Phân bổ lô là kênh lớn ở phía input.** Ngân sách cố định 500 lô, nên khi thêm cột, mỗi cặp đích được ước lượng ít lần hơn.
  - Với đệm Gauss, nửa sau (chọn theo |inverse covariance|) bù lại một phần, vì nó dồn lượt chọn về biến đích.
  - Với đệm có cấu trúc thì gần như không bù được, vì khối đệm hút lượt chọn.
- **Thống kê toàn cục trôi ít:** khoảng 0.007 so với độ lớn điển hình 0.09–0.33 của |ρ| ở k0.
- **Chưa biết output của SEA có đổi không.** Nó còn phụ thuộc cách aggregator gộp các ước lượng; ít lô hơn có thể chỉ làm output nhiễu hơn. Bước 3 trả lời câu hỏi này.
- **Muốn quy độ bất ổn cho phân bổ lô hay thống kê toàn cục** thì cần can thiệp riêng, như giữ cố định các lô hay thống kê ở giá trị k0. Việc đó không thuộc kế hoạch hiện tại.
