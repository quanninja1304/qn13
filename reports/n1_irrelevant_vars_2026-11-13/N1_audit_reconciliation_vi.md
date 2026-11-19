# Đối sánh hai audit N1 và hai bản luật đọc (14/11/2026)

> **Đối tượng đối sánh:** (A) audit đầu của agent [`N1_prior_art_audit_vi.md`](../direction_scan_2026-11-13/N1_prior_art_audit_vi.md) so với (B) audit lần hai của user [`N1_prior_art_second_audit_vi.md`](../direction_scan_2026-11-13/N1_prior_art_second_audit_vi.md); và (C) luật đọc P-N1 v1 của agent so với các yêu cầu sửa trong (B) §6; cộng (D) luật đọc P-C1a của user [`P_C1a_reading_rules_vi.md`](../direction_scan_2026-11-13/P_C1a_reading_rules_vi.md) so với phác thảo C1 §1.5 của agent trong [`00_direction_scan_vi.md`](../direction_scan_2026-11-13/00_direction_scan_vi.md).
>
> **Cách làm:** mỗi điểm bất đồng được tôi kiểm lại bằng nguồn gốc (mã trong `artifacts/n1_models_cpu/repos/`, README, PDF) trước khi phán. Nhãn: [Verified-code], [Verified-text], [Accept], [Partial], [Disagree].

## 1. Kết luận đối sánh

- **Audit (B) đúng ở mọi điểm sửa chính.** Bốn suy luận trong (A) là quá mức; tôi rút lại cả bốn (§2). Tiền lệ Aliferis 2010 là bổ sung quan trọng nhất: N1 **không được** claim "lần đầu thêm biến không liên quan vào causal discovery".
- **Gap statement của (B) §7 thay cho của (A) §1.** Mức độ: đủ để pilot, chưa đủ để claim ưu thế xuất bản.
- **Luật đọc P-N1 v1 bị thay bằng v2** ([`PN1_reading_rules_vi.md`](PN1_reading_rules_vi.md)), tiếp nhận cả 7 yêu cầu ở (B) §6 và cơ chế M4.
- **Luật đọc P-C1a của user (D) thay cho phác thảo C1 của agent.** Nó chặt hơn ở ba chỗ then chốt (§4). Tôi có hai bổ sung nhỏ, không có bất đồng về nguyên tắc.

## 2. Từng điểm sửa của (B) đối với (A)

| # | Claim trong (A) | Sửa trong (B) | Kiểm lại của tôi | Phán |
|---|---|---|---|---|
| 1 | DAG-FM "no feature dropout" ⇒ mô hình chưa từng gặp biến thừa | Không suy ra được: không dropout giữ causal sufficiency; thêm biến độc lập không phá sufficiency; ER không rejection vẫn sinh nút cô lập | Đúng về logic. Tôi chưa đọc generator của DAG-FM để biết có rejection hay không | [Accept]. Bỏ claim; nếu cần, audit generator sau |
| 2 | CausalArena loại biến cô lập ⇒ "benchmark không thể thấy lỗi" | Chỉ loại **isolated node**; module độc lập nhiều nút vẫn có thể có trong pool (block-sparse families); claim đúng chỉ ở phạm vi hẹp | Đúng. Phát biểu đúng là: protocol đã audit **không đo counterfactual append trên target cố định**, và riêng trường hợp cột cô lập bị loại khỏi synthetic pool | [Accept], giữ dạng hẹp |
| 3 | Softmax trên trục biến ⇒ không bất biến, gợi ý pha loãng | Softmax không bảo đảm bất biến nhưng cũng không chứng minh dilution; residual, normalization, decoder có thể bù; không gộp SEA vào cùng nhóm | Đúng. Trong (A) tôi đã ghi là [Inference], nhưng (A) §3 M2 dự đoán dấu quá tự tin | [Accept]. M2 giữ là giả thuyết, bỏ dự đoán dấu |
| 4 | PC/GES/FCI "bất biến tiệm cận, chỉ còn lỗi kiểm định bội" | Bất biến là kết quả **oracle hoặc consistency có điều kiện**; ở mẫu hữu hạn còn thay đổi neighborhood, conditioning set, propagation; GES BIC Gauss không phải chuẩn cho SCM phi tuyến | Đúng. Chứng minh ngắn dưới oracle của (B) §3.4 là đủ và tôi đồng ý | [Accept]. v2 thêm oracle-PC làm kiểm cài đặt, và biên tương đương cho mốc hữu hạn mẫu |
| 5 | AVICI huấn luyện d ≤ 50 (từ bài 2022) | `scm-v0` huấn luyện "up to 100 nodes" | README dòng 72 [Verified-text] | [Accept]. Sửa mọi chỗ |
| 6 | Chuẩn hóa từng cột không phụ thuộc k | Đúng cho nhánh continuous; **sai cho `neurips-grn`** (library size trên cả hàng) | Theo (B) đọc `avici/utils/data_jax.py`; tôi không kiểm lại dòng mã, chấp nhận theo trích dẫn có số dòng | [Accept]. v2 chỉ dùng checkpoint continuous |
| 7 | (không có) | **CDFM ngưỡng thích nghi** phụ thuộc toàn ma trận và log(d) | `cdfm/utils.py::suggest_threshold`: logistic trên mean, std, p25/p50/p75/p90, **logD**, median_gap, max_gap, knee_T; `wrapper.predict` dùng nó khi `threshold=None` [Verified-code] | [Accept]. Thêm cơ chế **M4 decoder** và ba chế độ giải mã trong v2 |
| 8 | (không có) | **Aliferis et al. JMLR 2010 Part II §3**: thêm 7 990 biến không liên quan bằng hoán vị giá trị, đo local causal discovery | PDF tr. ~240–244: "we augment the original network with 7990 irrelevant variables"; "we create irrelevant variables by randomly permuting values" [Verified-text] | [Accept]. Hệ quả: (i) không claim "chưa ai thêm irrelevant variables"; (ii) kiểu đệm C (hoán vị cột đích) **chính là** cách dựng của Aliferis, phải trích dẫn; (iii) phần mới của N1 là mô hình amortized, target cố định, tách decoder, và cơ chế |
| 9 | M1 "prior mật độ" dự đoán E_T tăng | ER với edges/node cố định ⇒ xác suất cạnh từng cặp **giảm** theo d; dấu không suy ra được; B còn đổi covariance và attention | Đúng. Dấu phụ thuộc prior của từng checkpoint (AVICI: edges/node; DAG-FM: density ∈ [0,1]) | [Accept]. v2 đổi chữ ký M1 thành "A khác B" (cùng d, khác thống kê edges/node), không dự đoán dấu |
| 10 | "Target in-distribution nên không thể đổ cho OOD" | Chỉ A giống training; bảng [A,B] có thể OOD về density, số thành phần liên thông | Đúng, và đó chính là đối tượng đo | [Accept]. Đổi cách gọi: "A nằm trong support huấn luyện; [A,B] là context có thể OOD" |

**Điểm (B) nêu mà tôi giữ nguyên lập trường:** không có. **Điểm (A) đúng và (B) giữ:** chưa ai làm fixed-target append với mô hình amortized trong các nguồn đã đọc; kiến trúc không cho bất biến "miễn phí"; tiền lệ TabPFN cho dự báo.

## 3. Bảy yêu cầu sửa luật đọc ở (B) §6 và cách v2 đáp ứng

| Yêu cầu | v2 |
|---|---|
| 1. Tách "có đổi", "có hại", "cơ chế" | Ba khối luật riêng: RN1 CHANGE (khoảng cách điểm thô so với dung sai lặp lại), RN2 HARM (ΔF1 có dấu), RN3 MECHANISM |
| 2. Non-invariance đo bằng raw score + edge flips so với repeatability; H có dấu; 0.05 là mức thực dụng | Có; τ_rep đo bằng chạy lặp k = 0; H ≥ 0.05 ghi rõ là ngưỡng do nhóm chọn |
| 3. Mốc cổ điển cần biên tương đương; có oracle baseline | Oracle-PC (d-separation) phải bất biến **chính xác** (kiểm cài đặt); PC/GES hữu hạn mẫu chỉ được gọi "xấp xỉ bất biến" nếu CI của H nằm trong ±0.02 |
| 4. Không gộp "2/3" thành tổng quát; không đổi mẫu số hậu nghiệm; kết luận theo từng model | Phán quyết **theo từng model** là kết quả khoa học; quyết định hướng (GO/NO-GO) là **quyết định dự án** ghi riêng, cần ≥ 1 model có CHANGE + HARM-BEYOND-CLASSICAL + cơ chế lặp lại trên tập held-out |
| 5. Bootstrap theo target SCM; contexts là repeated measures; chọn k/n chính trước | Có; k = 20, kiểu A, n = 500 là confirmatory; các k và kiểu khác là exploratory |
| 6. Tensor đích phải giống bitwise giữa các điều kiện | RN0.4: so sánh bitwise khối đích sau chuẩn hóa, kể cả dtype và thứ tự hàng; FoundCause có row-subsampling nội bộ nên kiểm bằng seed cố định và ghi rõ |
| 7. Kết quả âm giới hạn trong phạm vi test; không mặc định đủ bài | Ghi ở §0 và §7 của v2 |

## 4. Luật đọc P-C1a của user so với phác thảo C1 của agent

| Khía cạnh | Phác thảo agent (§1.5 của direction scan) | P-C1a của user | Phán |
|---|---|---|---|
| Đối tượng đo | Một "PAG-AID" duy nhất, phạt cả abstention | Vector outcome W/M/U/V/C, tách **sai công thức**, **bỏ lỡ**, **bất định vốn có**; risk = W/n_claim, NA khi không có claim | User đúng. Gộp thành một số là lỗi của tôi: oracle PAG abstain không phải lỗi discovery |
| Cách tạo P′ | Chèn một dấu vào PAG thật | Primary: sửa DAG thật (thêm/xóa/đảo một cạnh) rồi chiếu ra PAG; secondary: sửa dấu trực tiếp chỉ khi validator độc lập xác nhận là PAG hợp lệ | User đúng về tính hợp lệ. Giới hạn user tự nêu: một edit DAG có thể đổi nhiều dấu; phải lưu số dấu đổi |
| Chuẩn tham chiếu | Chỉ D* | Hai chuẩn: D* (công thức có đúng không) và P* (câu hỏi nào trả lời được ở cùng mức thông tin) | User đúng; đây là điểm mạnh nhất của (D) |
| Luật quyết định | Spearman < 0.5, đảo top-2 | Không đặt ngưỡng tùy tiện; RC1 counterexample, RC2 coverage explanation, RC3 mechanism lead lặp trên graph mới, RC4 inconclusive | Đồng ý bỏ các ngưỡng của tôi. **Bổ sung 1:** vẫn cần một **điều kiện dừng theo ngân sách** ghi trước, để pilot không kéo dài; RC3 "lặp trên graph mới" đã là điều kiện GO, nên chỉ cần thêm: nếu sau lưới exploratory đã định không có witness, dừng |
| Gate đúng đắn | Kiểm chéo dagitty 500 bộ | RC0 đầy đủ: oracle độc lập (không coi `pb_fci_typed` là độc lập vì dùng chung rule với causal-learn), microcases, GAC verifier, full-DAG verifier, exact checks; không dung sai | User đúng, kể cả điểm về `pb_fci_typed` |
| Baseline | SHD, Mod-SHD, SD, FID | Như agent nhưng đòi xác minh công thức Mod-SHD trước khi dùng, và **không** chọn một MAG từ PAG để chạy FID | Đồng ý. **Bổ sung 2:** với SD của Wahl–Runge, cần xác nhận entrypoint MAG/PAG trong mã công khai của họ trước khi gọi là baseline đã chạy |
| Claim "FCI precision thấp vì nhiều dấu tròn" | Agent nêu như cơ chế | User: không suy ra được, phải đọc mẫu số metric | Đúng; rút lại |

**Kết luận cho C1:** dùng (D) làm luật đọc của hướng dự phòng, kèm hai bổ sung nhỏ ở trên. Chưa chạy; C1 vẫn là backup.

## 5. Môi trường

- Dùng `artifacts/n1_models_cpu/.venv` của user (Python 3.11; AVICI 1.0.7 với hai sửa tương thích Windows đã ghi và không chạm mô hình; CDFM 0.1.0; FoundCause; smoke PASS).
- Venv của agent (`venv_n1`, Python 3.12) không cài được AVICI (gói `sklearn` cũ kéo theo), **đã xóa**.
- Lưu ý từ setup của user: máy chỉ còn khoảng 0.6 GB RAM trống khi bắt đầu; FoundCause RSS khoảng 0.9 GB. P-N1 v2 vì vậy chạy **tuần tự từng model, từng tiến trình**, và có bước resource check ở d = 50, n = 500 trước khi chạy lưới.

## 6. Gap statement dùng chung từ đây

Lấy nguyên văn (B) §7:

> Với checkpoint causal discovery học sẵn nhận bảng iid, đánh giá hiện có đã kiểm nhiều distribution shifts và classical local discovery đã có irrelevant-feature stress tests. Trong những nguồn được đọc ở đây, chưa thấy một đánh giá ghép **fixed-target module augmentation/swap**, **raw-score vs adaptive-decoder decomposition**, và **shared-prior vs independent-module controls** để xác định khi nào thông tin từ khối độc lập làm thay đổi kết luận nội bộ và vì sao. N1 kiểm giả thuyết này; failure và cơ chế chưa được xác nhận.
