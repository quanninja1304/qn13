# Luật đọc P-N1, bản sửa v2.1 (đề xuất, chờ duyệt) — 14/11/2026

> **Trạng thái: KHÓA ngày 14/11/2026 (user duyệt cả ba điểm ở §3).** Bản này sửa [luật v2](PN1_reading_rules_vi.md) theo [review 14/11](PN1_v2_review_and_next_steps_2026-11-14_vi.md). File v2 giữ nguyên làm lịch sử, §8 của v2 trỏ sang đây. Sau khi khóa, chỉ được điền §2 (tham số kỹ thuật: runtime, timeout, trần ngân sách, chọn lưới đầy đủ hay rút gọn cho FoundCause) **trước lần chạy đầu trên hệ đích**; mọi thay đổi khác ghi ở §4, không bao giờ sau khi đã xem metric.
> **Outcome đã thấy tính đến lúc viết:** không có metric khoa học nào. Chỉ có (i) smoke test, (ii) resource check trên Gauss ngẫu nhiên, (iii) kiểm config bộ sinh (số cạnh, tính acyclic; không gọi model). Chưa có hệ đích nào được đưa qua model.
> Chỗ nào bản này không nhắc tới thì v2 còn hiệu lực. Mọi ngưỡng là quyết định của nhóm.

## 0. Đã kiểm lại review trên mã nguồn

Chín điểm của review đều được giữ. Các khẳng định về mã đã đối chiếu trực tiếp [Verified-code]:

| Khẳng định của review | Kết quả kiểm |
|---|---|
| FoundCause `predict` không có tham số seed; mỗi run dùng `RandomState(42 + run_i)` và seed Torch tương ứng | Đúng, `foundcause.py` dòng 1712–1714, rev `d937cbf` |
| n = 500 thì mỗi run lấy 450 hàng; chọn hàng xảy ra trước hoán vị cột nên không phụ thuộc d | Đúng, dòng 1700 và 1718–1723 |
| Hoán vị cột nội bộ `rng_eval.permutation(d)` phụ thuộc d | Đúng, dòng 1723 |
| Output native của FoundCause có cắt cạnh theo agreement < 0.5 | Đúng, dòng 1780–1784; ngoài ra còn bước `sanitize` bỏ cột hằng và cột trùng trước khi suy luận |
| Config mẫu `lin-gauss`, `rff-gauss` của AVICI không có Erdős–Rényi | Đúng; ER chỉ có trong `config/train/scm-v0.yaml` với edges/node ∈ {1, 2, 3} |
| CDFM: `threshold=None` → `suggest_threshold` trên toàn bộ ma trận d × d, có đặc trưng `logD` | Đúng, `wrapper.py` dòng 128–151, `utils.py` dòng 6–67 |

Ghi thêm, ngoài review: FoundCause cảnh báo khi d > 51 ("trained on d ≤ 51"), nên d = 50 là sát biên support của model này [Verified-code, dòng 1655].

## 1. Các sửa đổi

### A1. Tách ba nhãn thay đổi (thay RN1 và điều kiện vào RN3)

| Nhãn | Đại lượng | Chế độ |
|---|---|---|
| `SCORE_CHANGE` | Δp(k) trên xác suất thô | không phụ thuộc decoder |
| `GRAPH_CHANGE_NATIVE` | Flips_N(k): số cặp không thứ tự trong khối đích đổi trạng thái skeleton so với k = 0 | output thật của gói |
| `GRAPH_CHANGE_FIXED` | Flips_F(k), cùng định nghĩa | decoder chuẩn hóa |

Mỗi đại lượng nhận một trong bốn mức (CI bootstrap theo hệ như v2):

- **DETECTABLE:** cận dưới CI > τ (dung sai lặp lại của chính đại lượng đó, A5).
- **MEANINGFUL:** cận dưới CI > max(τ, m). Biên m: 0.01 cho median Δp; **1 cặp mỗi hệ** cho trung bình Flips.
- **BELOW_MARGIN:** cận trên CI ≤ max(τ, m). Không gọi là "bất biến".
- **INCONCLUSIVE:** còn lại.

RN3 mở cho model có **bất kỳ** nhãn nào trong ba nhãn đạt DETECTABLE. Hai đường đọc: (a) điểm thô đổi → phân tích encoder/prior/thống kê bảng (M1–M3); (b) điểm thô BELOW_MARGIN nhưng graph native đổi → phân tích decoder (M4). Đường (b) là một failure thật của pipeline; nếu chỉ có (b), quyết định dự án là "audit decoder phạm vi hẹp, user quyết có đầu tư không", không ghi là "không có failure".

### A2. HARM có hai estimand đồng chính (sửa RN2)

- **H_NATIVE:** hại của pipeline như người dùng nhận được.
- **H_FIXED:** hại còn lại khi decoder được chuẩn hóa.

Cả hai đọc tại kiểu A, k = 20 với cùng ngưỡng v2 (H ≥ 0.05, cận dưới CI > 0). Số so sánh chính: 3 model × 2 estimand = **6**, báo đủ cả sáu; "≥ 1 trong 6 đạt" là bằng chứng exploratory, chỉ held-out mới xác nhận. Luôn báo F1(k = 0) cạnh H, để một model gần như không dự đoán gì không trông "bền".

### A3. Mốc cổ điển chỉ dùng để claim trên hệ tuyến tính Gauss

- `HARM-BEYOND-CLASSICAL` chỉ tính trên **40 hệ tuyến tính** (4 ô). Mốc: max(H_PC, H_GES), trong đó max lấy **sau khi** gộp mỗi mốc trên cùng tập hệ và **tính lại trong từng lần bootstrap**; báo kèm hai hiệu ghép cặp riêng (model − PC, model − GES).
- Trên **hệ RFF:** chỉ kết luận CHANGE và HARM của từng model. PC/Fisher-z và GES/BIC-Gauss vẫn chạy nhưng ghi nhãn **diagnostic misspecified**, không vào bất kỳ nhãn "beyond classical" nào (Fisher-z chỉ đặc trưng độc lập có điều kiện dưới Gauss; [Kalisch–Bühlmann 2007](https://jmlr.org/papers/v8/kalisch07a.html)).
- **Không thêm PC-KCI trong pilot này** [quyết định đề xuất]: KCI ở n = 500, d = 50 chưa có resource check và nhiều khả năng vượt ngân sách CPU. Hệ quả phải nói rõ: pilot không thể claim "tệ hơn cổ điển" trên dữ liệu phi tuyến.
- Hệ quả về power: claim chính dựa trên 40 hệ thay vì 80.

### A4. Tương đương chất lượng khác tương đương output

- CI của H_PC, H_GES nằm trong [−0.02, +0.02] → ghi **"F1 gần tương đương"**, không ghi "output bất biến".
- Thêm Flips cho PC và GES. Chỉ ghi **"output gần bất biến"** khi cận trên CI của trung bình Flips < 1 cặp mỗi hệ.
- **M2 (sửa chữ ký):** cả ba hiệu ghép cặp H_A − H_B, H_A − H_C, H_B − H_C có CI nằm trọn trong [−0.03, +0.03], **và** Δp(30) − Δp(5) có cận dưới CI > 0 với median Δp không giảm theo k ∈ {5, 10, 20, 30}. "CI chứa 0" không còn đủ. Đây vẫn chỉ là pattern nhất quán với pha loãng, chưa xác nhận attention dilution.

### A5. Tính ngẫu nhiên và dung sai lặp lại

- **τ_rep (mọi model):** gọi nguyên API hai lần trên cùng input; kỳ vọng ≈ 0. Đo trên tập DEV (A9), phân vị 95.
- **τ_sched (chỉ FoundCause):** biến động giữa các lịch ensemble. Đo bằng adapter `predict_sched(base)` sao lại vòng lặp của `predict` với `42` thay bằng `base`. Điều kiện dùng adapter: với base = 42, xác suất, agreement và adjacency trùng nguyên API trong 10⁻⁶ trên mọi hệ DEV; không đạt → không có τ_sched, FoundCause chỉ được đọc ở mức mô tả. τ_sched = phân vị 95 của Δp (và của Flips) giữa base 42 và base 1042 tại k = 0.
- Với FoundCause, τ trong A1 là **max(τ_rep, τ_sched)**: đổi d làm đổi hoán vị nội bộ, nên một phần Δp là nhiễu lịch, không phải tác động của biến thêm. Lưới chính vẫn chạy nguyên API (base 42).
- Ghi lại chỉ số hàng mỗi run để xác nhận lựa chọn hàng giống nhau giữa các k (thay phần tương ứng của RN0.4).
- **Equivariance (sửa RN0.1):** AVICI, CDFM giữ ngưỡng 10⁻⁴. FoundCause: sai khác do hoán vị ngoài phải ≤ τ_sched; đạt thì ghi "equivariant trong mức nhiễu ensemble". Model không đạt nhận nhãn `POSITION_SENSITIVE`; cách nối cột đệm **sau** vẫn là protocol chính cho mọi model, và model đó chạy thêm một điều kiện phụ (A, k = 20, cột đệm xen ngẫu nhiên với seed cố định), báo như phân tích độ nhạy. Đệm xen không được mô tả là đã loại confound vị trí.

### A6. Ba decoder, một lần forward

Mỗi input chỉ forward **một lần**; lưu xác suất, logits (nếu có), adjacency native, agreement, threshold; mọi decoder tính offline từ output đã lưu.

| Chế độ | AVICI | CDFM | FoundCause |
|---|---|---|---|
| **NATIVE** | p > 0.5 (theo README; gói không có decoder riêng) | adjacency với `threshold=None` (ngưỡng thích nghi trên bảng d × d) | `output['adjacency']`, gồm sanitize và cắt theo agreement |
| **FIXED** | max(p_ij, p_ji) > 0.5 | như AVICI | như AVICI, **không** cắt agreement |
| **FROZEN** | trùng NATIVE → M4 `NOT_APPLICABLE` | ngưỡng thích nghi tính ở k = 0, áp cho k > 0 | không có ngưỡng vô hướng để đóng băng → không định nghĩa |

Skeleton native = cạnh nếu adjacency có hướng nào đó. **M4 (sửa chữ ký):** CDFM: H_NATIVE − H_FROZEN ≥ 0.03, CI nằm ngoài 0; hoặc `SCORE_CHANGE` BELOW_MARGIN cùng `GRAPH_CHANGE_NATIVE` DETECTABLE. FoundCause: H_NATIVE − H_FIXED ≥ 0.03, CI ngoài 0, ghi là "agreement pruning", không ghi "ngưỡng". Chênh native/fixed không mặc định là do ngưỡng vô hướng.

### A7. Bộ sinh và kiểu đệm B (điền ⟦KIỂM⟧ ở §2 của v2)

- Dùng `avici.simulate_data(path=...)` với bốn YAML riêng tại `artifacts/n1_runs/config/er{1,2}-{lin,rff}-gauss.yaml`: đồ thị chỉ có `ErdosRenyi`, `edges_per_var` ∈ {1.0, 2.0}; khối cơ chế **chép nguyên** từ config mẫu của tác giả (tuyến tính: hệ số ±U[1, 3], nhiễu Gauss, scale U[0.2, 2]; RFF: length scale U[7, 10], output scale U[10, 20]). Các khoảng này nằm trong khoảng huấn luyện của `scm-v0` [Verified, so với `config/train/scm-v0.yaml`].
- Kiểm config đã chạy (20 seed mỗi d, không gọi model; `config_check.json`): mọi đồ thị acyclic; không có đồ thị 0 cạnh; số cạnh trung bình sát kỳ vọng (d = 10: 10.45 và 20.85; d = 20: 19.35 và 39.85).
- **Giới hạn của kiểu B:** ER đặt p = min(2e/(k − 1), 0.99). Tại **k = 5, e = 2** thì p bị cắt ở 0.99, khối đệm gần như là DAG đầy đủ (9–10 cạnh trên 10 cặp). Điều kiện này vẫn chạy nhưng đánh dấu `B_CLIPPED` và không vào chữ ký M1/M2 (hai chữ ký này đọc ở k = 20). B được gọi là "khớp **ngân sách cạnh kỳ vọng**", không gọi là kiểm soát mật độ.
- Không lọc đồ thị theo số cạnh thực. Ngoại lệ duy nhất, đăng ký trước: hệ đích có 0 cạnh (F1 không xác định) thì lấy seed kế tiếp và ghi log.
- Chiều của ma trận (g[i, j] = 1 nghĩa là i → j) kiểm bằng ca hai biến dựng tay ở bước adapter; metric chính là skeleton nên không phụ thuộc điểm này.

### A8. Contrast có dấu

M1 và M3 dùng contrast **có dấu** δ (H_A − H_B; H_D − H_A): đạt nếu CI nằm trọn ngoài [−m, +m] về một phía (m = 0.03 cho M1, 0.05 cho M3). Dấu được ghi lại; ở held-out phải lặp lại **đúng dấu** đó.

### A9. Ba tập hệ, và từ ngữ

1. **DEV (mới): 16 hệ**, 2 mỗi ô, seed riêng. Chỉ dùng cho RN0, kiểm adapter, đo τ. Không vào bất kỳ số liệu kết luận nào.
2. **EXPLORATORY: 80 hệ.** Contrast chính định trước là A, k = 20; lead cơ chế chọn theo luật.
3. **HELD-OUT: 24 hệ, 3 mỗi ô, trọng số ô bằng nhau** (thay 20 hệ "2–3 mỗi ô" của v2). Trước khi mở phải đóng băng: lead, contrast và dấu, seed, adapter, tập điều kiện.

Điều kiện chạy ở held-out theo lead (luôn có k = 0): M1 → A và B tại k = 20; M2 → A tại k ∈ {5, 10, 20, 30} cùng B, C tại k = 20; M3 → A và D tại k = 20; M4 → A tại k = 20, decoder offline. Nếu lead là failure điểm thô thì `SCORE_CHANGE` phải được kiểm lại.

Nhãn RN5: `REPLICATED` / `NOT_REPLICATED` / `INCONCLUSIVE` (CI quá rộng thì INCONCLUSIVE; 12 hệ tuyến tính không đủ power cho hiệu ứng nhỏ, nói trước). Quyết định dự án khi REPLICATED là **"GO mechanism validation"** (thiết kế can thiệp vào model hoặc test lệch prior), thay cho "GO confirmatory". Báo số so sánh đã làm ở exploratory; "≥ 1 model đạt" không phải claim đã kiểm soát familywise.

### A10. Kiểm năng lực nền (thay RN0.2)

Trên hệ tuyến tính của DEV, chế độ FIXED, k = 0: so F1 của model với hai output tham chiếu (đồ thị rỗng, đồ thị đầy đủ). Đạt nếu F1 trung bình của model lớn hơn F1 của đồ thị đầy đủ trên DEV. Nếu không đạt: đối chiếu cấu hình với tài liệu tác giả **một lần**, không chỉnh ngưỡng theo ground truth. Vẫn không đạt → nhãn `BASELINE_TOO_WEAK_FOR_THIS_HARM_TEST`: model ở lại mẫu số, vẫn đọc CHANGE, không đọc HARM. Không thay model khác vào.

### A11. Thứ tự chạy và ngân sách

- **Pha E1:** k = 0 và (A, k = 20) trên 80 hệ, cả ba model và PC/GES → đọc được A1, A2, A3.
- **Pha E2:** phần còn lại của lưới. AVICI và CDFM chạy đủ lưới v2. FoundCause: xem bảng §2; nếu tổng ước tính vượt trần thì chạy **lưới rút gọn định trước** (B, C, D tại k = 20 và A tại k ∈ {5, 10, 30}: đủ cho M1–M4, mất đường cong theo k của B, C, D).
- FoundCause giữ `n_runs = 10` trong mọi trường hợp. Quá timeout → `RESOURCE_LIMIT`, không phải "không đổi". Runner có checkpoint/resume theo hash input.

### A12. Giới hạn bổ sung (thêm vào §7 của v2)

1. Pilot đo hại trên **skeleton**. Model có thể đảo hướng mà giữ skeleton; NO-GO theo H không bác bỏ failure về hướng. AUPRC có hướng chỉ là mô tả.
2. A so với B tại cùng k là một contrast về context; chưa kiểm "prior chung" so với "prior rút độc lập theo họ". M1–M3 là dấu hiệu để thiết kế bước sau.
3. Một bản rút đệm mỗi (hệ, kiểu, k): ước lượng được trung bình trên hệ, không tách được phương sai theo context trong một hệ.
4. Kết quả của một checkpoint ở một contrast không nói gì về mọi mô hình học sẵn.

## 2. Ngân sách đo được

Đo trên Gauss ngẫu nhiên, n = 500, mỗi model 2 luồng, máy 4 lõi, RAM tổng 8,4 GB (trống khoảng 1,6–2,3 GB). Một lần đo mỗi d; một số điểm đo khi một tiến trình 2 luồng khác chạy song song, nên có thể hơi cao. Log: `artifacts/n1_models_cpu/logs/rc_*`.

| d | AVICI (lần gọi sau, s) | CDFM (s) | FoundCause, 10 runs (s) |
|---:|---:|---:|---:|
| 10 | 2,4 | 4,7 | 324 |
| 15 | 3,2 | 6,7 | 432 |
| 20 | 4,3 | 8,3 | 502 |
| 25 | 5,4 | 11,0 | 547 |
| 30 | 6,2 | 13,2 | 658 |
| 40 | 8,3 | 17,6 | 810 (song song với AVICI) |
| 50 | 7,1 | 14,5 | 624 |

PC, GES và oracle-PC (1 luồng): PC dưới 5 s mỗi lần; GES lâu nhất đã gặp là 128 s (d = 50, đệm B dày).

**Ngân sách đã chốt (AVICI, CDFM, PC, GES):** chạy đủ lưới v2 cho DEV, E1, E2 và held-out. Ước tính dưới 4 giờ cho AVICI, dưới 8 giờ cho CDFM, vài giờ cho PC/GES. Timeout mỗi job: 600 s (AVICI, CDFM), 1 800 s (GES). Quá timeout → `RESOURCE_LIMIT`.

**FoundCause:** ước tính theo bảng trên: DEV (58 lần gọi) khoảng 6,6 giờ; E1 (160 lần gọi) khoảng 23 giờ; E2 đầy đủ khoảng 190 giờ; E2 rút gọn khoảng 78 giờ; held-out tối đa khoảng 10 giờ. FoundCause cần khoảng 2–2,9 GB RAM nên phải chạy một mình. **Phương án FoundCause (user chọn 14/11/2026, trước khi xem bất kỳ output E1 nào): mở rộng có điều kiện.**
- Luôn chạy DEV và E1. E1 đủ cho A1 (ba nhãn thay đổi), A2 (H_NATIVE, H_FIXED), và M4 (FoundCause: H_NATIVE − H_FIXED tại A, k = 20).
- Chạy E2 **rút gọn** (A tại k ∈ {5, 10, 30}; B, C, D tại k = 20) khi và chỉ khi ở E1 (A, k = 20, 80 hệ) ít nhất một trong `SCORE_CHANGE`, `GRAPH_CHANGE_NATIVE`, `GRAPH_CHANGE_FIXED` của FoundCause đạt DETECTABLE với τ = max(τ_rep, τ_sched).
- Nếu không đạt: M1–M3 của FoundCause ghi `NOT_RUN (conditional expansion not triggered)`. Kết luận về FoundCause khi đó chỉ ở mức "không phát hiện thay đổi tại A, k = 20", không mở rộng sang các kiểu đệm khác.
- Mọi job FoundCause dùng cùng một số luồng, chốt trước DEV và ghi trong output.

## 3. Quyết định của user (14/11/2026)

1. v2.1: **duyệt**.
2. A3: **chấp nhận** không có mốc cổ điển trên RFF; không thêm PC-KCI.
3. A9: **chấp nhận** held-out 24 hệ (3 mỗi ô, trọng số ô bằng nhau).
4. Trần ngân sách CPU cho FoundCause: điền ở §2 sau phép đo runtime, trước lần chạy đầu.

## 4. Nhật ký thay đổi sau khóa (append-only)

- 14/11/2026: khóa. Chưa có metric khoa học nào được xem.
- 14/11/2026, **cách đọc tác nghiệp của RN0, ghi trước khi xem output model nào trên DEV** (code: `artifacts/n1_runs/pn1/rn0.py`):
  - τ_rep, τ_sched, τ_flips = phân vị 95 qua 16 hệ DEV của thống kê từng hệ.
  - Equivariance FoundCause: phân vị 95 qua 10 hệ của Δp(hoán vị so với gốc) ≤ τ_sched (cùng thống kê, cùng phân vị). AVICI, CDFM: max qua 10 hệ của max|sai khác| ≤ 10⁻⁴.
  - Repeat của FoundCause = lần gọi adapter với base 42. Nếu parity đạt (≤ 10⁻⁶) thì lần gọi này tương đương mã với lần gọi API thứ hai; việc này tiết kiệm 16 lần gọi, khoảng 1,7 giờ.
  - Chỉ số hàng FoundCause: `RandomState(42 + i).choice(500, 450)` không phụ thuộc d [Verified-code], nên chọn hàng giống nhau giữa các k theo cấu trúc mã; không ghi lại từng lần.
  - RN0.5 oracle-PC: **PASS**, 40/40 cặp (20 hệ × kiểu A, B tại k = 20) cho khối đích bất biến chính xác, 0 cạnh đích↔đệm; ở k = 0 oracle khôi phục đúng skeleton thật. Đây là kiểm cài đặt, không phải metric khoa học.
  - RN0.4 bitwise: assert trong `common.assemble` cho mọi input; đã qua trên mọi kiểu và mọi k của 4 hệ DEV.
- 14/11/2026: **FoundCause chốt 4 luồng** cho mọi job (DEV-c0-r0 k = 0: 229 s với 4 luồng, so với 324 s với 2 luồng trên dữ liệu ngẫu nhiên cùng shape). Quyết định chỉ dựa trên thời gian chạy, chưa xem output. AVICI và CDFM giữ 2 luồng. Ước tính lại cho FoundCause: DEV khoảng 4,5 giờ, E1 khoảng 16 giờ.
- 16/11/2026, **đọc E1** (không đổi luật): FoundCause DEV 58/58 và E1 160/160 do user chạy trong PowerShell, 0 lỗi; RN0 FoundCause đạt (parity, tất định, equivariance trong τ_sched = 0.0116). Phán quyết theo model: cả ba có SCORE_CHANGE, GRAPH_CHANGE_NATIVE, GRAPH_CHANGE_FIXED ở mức MEANINGFUL và HARM ở cả H_NATIVE, H_FIXED; BEYOND_CLASSICAL đạt 5/6 (CDFM native không đạt); M4 không đạt ở CDFM và FoundCause. **Điều kiện mở E2 rút gọn của FoundCause: ĐẠT.** Chi tiết: [`PN1_E1_results_vi.md`](PN1_E1_results_vi.md).
- 19/11/2026, **cách đọc tác nghiệp của E2, ghi trước khi xem bất kỳ metric E2 nào** (code: `artifacts/n1_runs/pn1/analyze_e2.py`). Trước bước này, output E2 chỉ được `integrity_e2.py` mở để kiểm shape, giá trị hữu hạn và mã băm. Kết quả kiểm: đủ 1200/1200 job (AVICI, CDFM, PC, GES) và 480/480 (FoundCause rút gọn), 0 lỗi; mã băm input tính lại từ `assemble` khớp mọi job; input trùng giữa các thuật toán; target_sha không đổi trong mỗi hệ. Ba job FoundCause có thời gian treo đồng hồ do cửa sổ PowerShell bị dừng (QuickEdit); không ảnh hưởng output.
  1. **Estimand của chữ ký.** Luật không nói M1–M3 đọc trên H nào. Mỗi chữ ký tính riêng trên **H_NATIVE và H_FIXED**, báo cả hai, không gộp. CDFM FROZEN chỉ mô tả.
  2. **Contrast:** hiệu ghép cặp theo hệ tại k = 20, trung bình trên 80 hệ EXP; bootstrap theo hệ, 2 000 lần, seed 20261114, percentile 95%.
     - M1: δ = H_A − H_B; đạt nếu CI nằm trọn trên +0.03 hoặc trọn dưới −0.03 (A8); ghi dấu. Chiều của E_T (A so với B) chỉ ghi.
     - M3: δ = H_D − H_A; như trên với m = 0.05.
     - M2: CI của trung bình ba hiệu H_A − H_B, H_A − H_C, H_B − H_C đều nằm trọn trong [−0.03, +0.03]; **và** cận dưới CI của median theo hệ của [Δp_A(30) − Δp_A(5)] > 0; **và** median Δp_A không giảm qua k = 5, 10, 20, 30 (ước lượng điểm). Đường Δp đọc trên **kiểu A**, vì chỉ A có đủ k cho cả ba model. Phần Δp không phụ thuộc decoder nên dùng chung cho hai estimand.
     - M4: giữ kết quả E1, không tính lại.
     - UNEXPLAINED: không chữ ký nào đạt cho estimand đó.
  3. `B_CLIPPED` chỉ ở (B, k = 5, e = 2), không chạm chữ ký nào (đều ở k = 20); bảng mô tả đánh dấu.
  4. **Mô tả (RN4):** với mỗi (kiểu, k): median Δp, Flips native và fixed, H_NATIVE, H_FIXED, E_T, X, AUPRC có hướng và AUPRC skeleton trên khối đích; mốc cổ điển (H, Flips) theo kiểu và k; hiệu so với mốc cổ điển trên 40 hệ tuyến tính cho B, C, D tại k = 20 chỉ là mô tả, không phải nhãn.
  5. **Số phép thử exploratory của RN3:** 3 model × 2 estimand × 3 chữ ký (M1, M2, M3) = 18, không kiểm soát familywise; báo đủ.
  6. **Chọn lead (đề xuất, ghi trước khi xem; user quyết ở bước đóng băng):** script không chọn. Đề xuất mặc định là **không chọn**: mọi chữ ký đạt ở bất kỳ estimand nào đều đi tiếp held-out, với dấu đã ghi, và tập điều kiện là hợp của các điều kiện A9 tương ứng. Nếu hợp này vượt ngân sách held-out khoảng 10 giờ của FoundCause, user quyết trước khi chạy.
- 19/11/2026, **đọc E2** (không đổi luật; đọc đúng cách đã ghi ở mục trước): AVICI **M1** đạt ở cả hai estimand, dấu − (H_B > H_A); CDFM **M2** đạt ở H_FIXED, H_NATIVE UNEXPLAINED; FoundCause UNEXPLAINED ở cả hai estimand; M3 không đạt ở model nào. Đề xuất đóng băng held-out theo mục 6 (mọi chữ ký đạt đều đi tiếp), **chờ user duyệt**; chưa mở hệ held-out nào. Chi tiết: [`PN1_E2_results_vi.md`](PN1_E2_results_vi.md).
