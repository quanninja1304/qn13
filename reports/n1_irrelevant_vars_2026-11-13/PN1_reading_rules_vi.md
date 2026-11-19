# Luật đọc P-N1 (v2): mô hình causal discovery học sẵn có bất biến với biến độc lập thêm vào không? (14/11/2026)

> **Trạng thái: v2 KHÓA ngày 14/11/2026 (user: "duyệt").** v1 (13/11) đã bị thay toàn bộ sau audit lần hai của user; khác biệt ghi ở §8. Sau khi duyệt, file bị **khóa**; thay đổi chỉ được ghi thêm ở §8, không bao giờ sau khi đã xem metric. Chỗ đánh dấu ⟦KIỂM⟧ là tham số kỹ thuật điền sau bước resource check, **trước** lần chạy đầu tiên.
> **Nền:** [audit đầu](../direction_scan_2026-11-13/N1_prior_art_audit_vi.md), [audit lần hai](../direction_scan_2026-11-13/N1_prior_art_second_audit_vi.md), [đối sánh](N1_audit_reconciliation_vi.md), [manifest](DATA_MANIFEST_vi.md).
> **Nhãn:** [Verified], [Inference], [Hypothesis]. Mọi ngưỡng số trong file là **quyết định của nhóm**, không phải định luật hay tiêu chí novelty.

## 0. Ba câu hỏi tách riêng, và điều pilot không thể kết luận

| Câu hỏi | Đo bằng | Trả lời được ở pilot này? |
|---|---|---|
| **Q1 CHANGE:** output trên khối đích có đổi khi nối thêm biến độc lập không? | khoảng cách điểm thô so với dung sai lặp lại | Có, theo từng model |
| **Q2 HARM:** đổi có làm chất lượng giảm không, so với mốc cổ điển? | H = F1(k = 0) − F1(k), có dấu; so với PC/GES ở cùng dữ liệu | Có, theo từng model, trong phạm vi hệ đích đã test |
| **Q3 MECHANISM:** đổi do đâu? | chữ ký đăng ký trước của M1–M4 | Chỉ **gợi ý** cơ chế; xác nhận cần can thiệp vào mô hình (mask attention, đóng băng decoder), ngoài pilot |

Pilot **không** chứng minh mô hình "biết biên hóa" nếu kết quả âm; không mặc định đủ bài báo ở nhánh nào. Nó không kiểm một phương pháp mới.

**Tiền lệ phải trích:** Aliferis et al. (JMLR 2010, Part II §3) đã thêm 7 990 biến không liên quan sinh bằng hoán vị và đo local causal discovery [Verified-text]. Kiểu đệm C dưới đây là cách dựng của họ. Phần mới của N1: mô hình amortized, target cố định, tách decoder khỏi encoder, so với mốc cổ điển cùng dữ liệu.

## 1. Đối tượng

- **Hệ đích** T = (G_T, SEM, X_T) với d_T biến, n hàng.
- **Đệm** P_k: k cột sinh độc lập với X_T, cùng n hàng. Bảng X_k = [X_T | P_k]; cột đệm nối **sau** (kiểm equivariance ở RN0.1).
- **Dự đoán trên khối đích:** ma trận điểm thô S^(k) (logits hoặc xác suất tùy model, lưu cả hai nếu có), lấy khối d_T × d_T. Mọi metric tính trên khối này, trừ X.
- **Đơn vị thống kê:** hệ đích. Các (kiểu, k, lần lặp) trong cùng hệ là repeated measures; mọi so sánh ghép cặp trong hệ; bootstrap theo hệ.
- **Cách gọi phân phối:** X_T sinh từ họ nằm trong support huấn luyện của AVICI `scm-v0` (ER, edges/node 1–3, tuyến tính và RFF) [Verified, README]. Bảng [X_T | P_k] là **context có thể OOD** về mật độ và số thành phần liên thông; đó là đối tượng đo, không phải lỗi thiết kế. Với CDFM và FoundCause, "trong support" chỉ là tuyên bố prior rộng của tác giả [Inference].

## 2. Hệ đích

| Yếu tố | Giá trị |
|---|---|
| d_T | 10, 20 |
| Đồ thị | Erdős–Rényi, số cạnh kỳ vọng mỗi nút ∈ {1, 2}; ghi cả realized degree |
| Cơ chế | tuyến tính Gauss; RFF phi tuyến với nhiễu Gauss |
| n | 500 (trong [100, 600] của FoundCause; đủ cho PC/GES ở d ≤ 50) |
| Seed | 10 mỗi ô → **80 hệ đích exploratory**; thêm **20 hệ đích held-out** (seed cố định trước, 2–3 mỗi ô) chỉ chạy sau khi đã đọc exploratory, dùng cho RN5 |
| Bộ sinh | ⟦KIỂM⟧ `avici.simulate_data` với domain tương ứng nếu tên domain khớp; nếu không, bộ sinh tự viết với tham số ghi rõ. Ghi vào §8 |
| Chuẩn hóa | z-score **từng cột**, thực hiện **bên ngoài** mô hình trên X_k; tắt chuẩn hóa nội bộ nếu API cho phép (CDFM `standardize=False`); với mô hình không tắt được, ghi nhận và kiểm RN0.4 |

Hệ thật (Sachs) **bỏ khỏi v2**: chưa có bản liên tục có nguồn rõ; nếu thêm sau thì chỉ mô tả và ghi §8.

## 3. Đòn bẩy

k ∈ {0, 5, 10, 20, 30}. Với d_T = 20, k = 30 cho d = 50, trong support của cả ba model. **Confirmatory: kiểu A, k = 20.** Mọi (kiểu, k) khác là exploratory, báo cáo có nhãn.

| Kiểu | Định nghĩa | Vai trò |
|---|---|---|
| **A. Độc lập Gauss** | k cột i.i.d. N(0, 1) | Chính |
| **B. Khối độc lập có cấu trúc** | k cột từ một DAG ER riêng, **cùng edges/node và cùng họ cơ chế** với hệ đích, độc lập với X_T | Đối chứng "cùng d, cùng thống kê edges/node toàn bảng": tách M1 |
| **C. Hoán vị cột đích** (Aliferis 2010) | lặp qua các cột đích, mỗi bản sao hoán vị hàng độc lập | Đối chứng khớp phân phối biên; không hoàn toàn độc lập vô điều kiện vì dùng chung mẫu thực nghiệm, ghi rõ |
| **D. Độc lập đuôi nặng** | k cột i.i.d. Student-t(3), chuẩn hóa | Tách M3 |

Một bản rút đệm cho mỗi (hệ, kiểu, k), seed = f(seed hệ, kiểu, k), dùng chung cho mọi model và thuật toán.

## 4. Model, chế độ giải mã, mốc cổ điển

| Nhóm | Thành viên | Cấu hình |
|---|---|---|
| Học sẵn | **AVICI** `scm-v0`; **CDFM** `DMIRLAB/CDFM`; **FoundCause** `checkpoint-2026-11` | CPU; mỗi model một tiến trình, chạy tuần tự (RAM). FoundCause: `n_runs = 10`, `temperature = 1.0`, `max_samples = 5000`, seed hoán vị cố định; AVICI: output xác suất; CDFM: lưu logits |
| Thứ tư, nếu chạy được trước lần chạy đầu | TabCausal `tabcausal-base.pt` | Chỉ trong venv riêng; là model **exploratory**, không vào quyết định dự án; ghi §8 |
| Không dùng | Arrow (chưa có trọng số); SEA (torch 1.13 + CUDA); AVICI `neurips-grn` (chuẩn hóa count theo library size toàn hàng) | — |
| Cổ điển, hữu hạn mẫu | **PC** (causal-learn, Fisher-z, α = 0.05, stable); **GES** (BIC Gauss) | GES chỉ đọc trên hệ tuyến tính; trên RFF ghi là misspecified. Output CPDAG → chấm **skeleton** |
| Cổ điển, oracle | **PC với d-separation oracle** trên DAG [G_T ⊕ G_P] | Phải bất biến **chính xác**; là kiểm cài đặt, không phải mốc hữu hạn mẫu |

**Ba chế độ giải mã** cho mỗi model (lưu cả ba):
- **NATIVE:** mặc định của gói (CDFM: ngưỡng thích nghi `suggest_threshold`, phụ thuộc phân phối điểm và log d [Verified-code]; FoundCause: ngưỡng 0.5 trên max(P_ij, P_ji) với min-agreement 0.5; AVICI: 0.5).
- **FIXED:** ngưỡng 0.5 trên xác suất cho mọi model.
- **FROZEN:** ngưỡng NATIVE tính ở k = 0 của chính hệ đó, áp cho mọi k > 0 (tách M4).

## 5. Metric (trên khối đích)

| Ký hiệu | Định nghĩa |
|---|---|
| **Δp(k)** | trung bình trên i ≠ j của \|p^(k)_ij − p^(0)_ij\|, trên xác suất; cũng ghi max |
| **τ_rep** | dung sai lặp lại: chạy k = 0 hai lần (FoundCause: hai seed hoán vị khác nhau; AVICI, CDFM: hai lần chạy, kỳ vọng ≈ 0); τ_rep = phân vị 95 của Δp giữa hai lần, theo model |
| **Flips(k)** | số cặp đổi trạng thái cạnh skeleton ở chế độ FIXED so với k = 0 |
| **F1_T(k), H(k)** | F1 skeleton (cạnh nếu max(p_ij, p_ji) vượt ngưỡng của chế độ) so với skeleton thật; H(k) = F1_T(0) − F1_T(k), dương = tệ đi; tính cho cả ba chế độ |
| **E_T(k), X(k)** | số cạnh dự đoán trong khối đích; số cạnh đích↔đệm (đúng phải là 0) |
| **AUPRC_T(k)** | không phụ thuộc ngưỡng, cạnh có hướng |

CI: bootstrap theo hệ đích, 2 000 lần, percentile 95%, seed 20261114; hiệu luôn ghép cặp trong hệ.

## 6. Luật đọc

### RN0 — Kiểm bắt buộc trước khi đọc bất kỳ metric nào
1. **Equivariance:** trên 10 hệ ở k = 0, hoán vị cột rồi hoán vị ngược output; sai khác ≤ 10⁻⁴ (FoundCause: cùng seed nội bộ). Không đạt → model đó dùng đệm **xen ngẫu nhiên** với seed cố định, ghi rõ.
2. **Năng lực nền:** F1_T(0) ở chế độ FIXED ≥ 0.5 trên hệ tuyến tính, trung bình theo model. Không đạt → kiểm cấu hình, ghi §8, không chạy k > 0 trước khi sửa.
3. **Tất định:** chạy lại cùng đầu vào, cùng seed → sai khác ≤ 10⁻⁶; τ_rep đo được và ghi lại.
4. **Tensor đích giống bitwise:** khối X_T trong X_k sau chuẩn hóa ngoài phải **bằng từng byte** với khối ở k = 0, mọi k, mọi kiểu (dtype, thứ tự hàng, NaN encoding). Với FoundCause, kiểm thêm rằng row-subsampling nội bộ dùng cùng seed và cùng chỉ số hàng giữa các k; nếu API không cho phép, ghi là nguồn nhiễu đã biết và đưa vào τ_rep.
5. **Oracle-PC bất biến chính xác** trên 20 hệ với kiểu A và B, k = 20. Không đạt → lỗi cài đặt, dừng.
6. **Resource check:** một hệ d_T = 20, k = 30, n = 500 cho mỗi model; ghi peak RSS và thời gian; đặt timeout ⟦KIỂM⟧.

### RN1 — CHANGE (confirmatory: kiểu A, k = 20), theo từng model
- **CHANGE** nếu median theo hệ của Δp(20) > max(τ_rep, 0.01) và cận dưới CI của median > τ_rep.
- **NO CHANGE** nếu cận trên CI của median ≤ max(τ_rep, 0.01).
- Khác: **INCONCLUSIVE**.
- Phụ: Flips(20) ở FIXED báo kèm.

### RN2 — HARM (confirmatory: kiểu A, k = 20, chế độ FIXED), theo từng model
- **HARM** nếu H ≥ 0.05 và cận dưới CI > 0. H là trung bình theo hệ.
- **HARM-BEYOND-CLASSICAL** nếu H_model − H_PC ≥ 0.05 với cận dưới CI của hiệu ghép cặp > 0 (trên hệ RFF, chỉ PC là mốc; trên hệ tuyến tính dùng max(H_PC, H_GES)).
- **Mốc cổ điển "xấp xỉ bất biến"** chỉ được tuyên bố nếu CI 95% của H_PC (và H_GES ở hệ tuyến tính) nằm trong **[−0.02, +0.02]**; nếu không, ghi "chưa xác lập", không ghi "bất biến".
- Chế độ NATIVE và FROZEN báo cáo kèm; nếu HARM chỉ có ở NATIVE mà không có ở FIXED/FROZEN → xem RN3 M4.

### RN3 — MECHANISM (chỉ cho model có CHANGE), chữ ký đăng ký trước, tại k = 20
| Nhãn | Chữ ký |
|---|---|
| **M4 decoder** | CHANGE ở NATIVE nhưng Δp ≤ τ_rep; hoặc H(NATIVE) − H(FROZEN) ≥ 0.03 với CI > 0 |
| **M1 lệch prior theo thống kê toàn bảng** | \|H_A − H_B\| ≥ 0.03 với CI của hiệu ghép cặp > 0 (A và B cùng d, khác edges/node toàn bảng); chiều thay đổi của E_T chỉ **ghi**, không dự đoán, kèm prior đồ thị tài liệu hóa của checkpoint |
| **M2 pha loãng theo số cột** | H_A, H_B, H_C khác nhau dưới 0.03 (CI chứa 0) **và** Δp tăng đơn điệu theo k |
| **M3 phân phối của đệm** | \|H_D − H_A\| ≥ 0.05 với CI > 0 |
| **UNEXPLAINED** | không chữ ký nào thỏa |
Nhiều nhãn có thể cùng thỏa; ghi cả. Không thêm cơ chế sau khi xem dữ liệu; ý tưởng mới chỉ là giả thuyết cho pilot sau. Chữ ký không phải bằng chứng cơ chế; xác nhận cần can thiệp vào mô hình.

### RN4 — Mô tả
Theo ô (d_T, edges/node, cơ chế); theo k; X(k); AUPRC_T; F1 cạnh có hướng; TabCausal nếu có.

### RN5 — Held-out
Với mỗi model có CHANGE và HARM-BEYOND-CLASSICAL ở exploratory: chạy 20 hệ held-out, kiểu A và kiểu dùng cho chữ ký cơ chế, k = 20. **REPLICATED** nếu HARM-BEYOND-CLASSICAL và cùng nhãn cơ chế xuất hiện lại với cùng ngưỡng; nếu không → **NOT REPLICATED**.

### Quyết định dự án (không phải claim khoa học)
- **GO confirmatory** nếu ≥ 1 model đạt CHANGE + HARM-BEYOND-CLASSICAL + nhãn cơ chế khác UNEXPLAINED, và REPLICATED ở RN5.
- **NO-GO** nếu mọi model là NO CHANGE, hoặc có CHANGE nhưng không model nào HARM-BEYOND-CLASSICAL và các mốc cổ điển đã xác lập xấp xỉ bất biến.
- **INCONCLUSIVE** còn lại: báo cáo, không mở rộng ngân sách để tìm kết quả dương; quyết định tiếp theo là của user.
Không đổi mẫu số hay tập model sau khi thấy kết quả. Kết luận theo từng model được viết **trước** câu chuyện gộp.

## 7. Giới hạn biết trước
- Ba checkpoint, một họ dữ liệu tổng hợp; không có hệ thật.
- Chữ ký cơ chế là tương quan, không phải can thiệp vào mô hình.
- Kiểu C không hoàn toàn độc lập vô điều kiện (cùng mẫu thực nghiệm).
- Mốc hữu hạn mẫu của PC/GES dao động; biên ±0.02 là lựa chọn của nhóm.
- RAM khoảng 0.6 GB trống khi bắt đầu; chạy tuần tự; nếu d = 50 không chạy được với một model, giảm k tối đa cho model đó và ghi §8 trước khi chạy lưới.
- Kết quả âm giới hạn trong phạm vi đã test.

## 8. Nhật ký thay đổi (append-only)
- 13/11/2026: v1 nháp.
- 14/11/2026: **v2 thay toàn bộ v1** sau audit lần hai của user và bản đối sánh. Thay đổi chính: tách CHANGE/HARM/MECHANISM; thêm τ_rep, Flips, ba chế độ giải mã và cơ chế M4; đổi chữ ký M1 (không dự đoán dấu); thêm oracle-PC và biên tương đương ±0.02 cho mốc cổ điển; kiểm bitwise tensor đích; phán quyết theo từng model, quyết định dự án tách riêng; thêm 20 hệ held-out (RN5); bỏ Sachs; bỏ `neurips-grn`; sửa support của `scm-v0` thành d ≤ 100; trích Aliferis 2010 cho kiểu C; môi trường chuyển sang `artifacts/n1_models_cpu/.venv` của user. Chưa chạy gì, chưa xem metric nào.
- 14/11/2026: **user duyệt v2; file khóa.** User cho phép thử TabCausal trong venv riêng (model exploratory thứ tư, không vào quyết định dự án, như §4). Resource check RN0.6 chạy trên dữ liệu ngẫu nhiên (không có hệ đích, không metric) song song với việc khóa.
- 14/11/2026: **v2.1 khóa** ([`PN1_rules_v2_1_amendment_vi.md`](PN1_rules_v2_1_amendment_vi.md)), sửa RN0–RN5 theo [review 14/11](PN1_v2_review_and_next_steps_2026-11-14_vi.md). Phần nào v2.1 không nhắc thì v2 còn hiệu lực. Chưa có metric khoa học nào được xem.
