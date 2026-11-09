# Rà soát độc lập RG1: `RG1_R1_proof_vi.md`

> Ngày 2026-11-04. Người rà soát: một agent AI ngữ cảnh mới, do user yêu cầu chạy, chỉ đọc repo và tự viết code kiểm tra. **Đây không phải rà soát của con người.**
> Văn bản dưới đây là báo cáo gốc của agent, chỉ thêm phần đầu này và đổi đường dẫn script. Nó phản ánh bản tài liệu **trước khi sửa**; các nhãn M1–M10 và cách xử lý nằm ở `RG1_R1_proof_vi.md` §12. Một số số liệu đã được đo lại độc lập ở `RG1_followup_checks.py`.
> Script của agent được lưu nguyên tại `RG1_review_scripts/`.

---

## 1. Phán quyết: **PASS WITH CORRECTIONS**

Tôi không tìm được phản ví dụ cho định lý trung tâm nào. Thm 1, 3, 4, 5, 7, Lemma 1 và Mệnh đề 2–8 đều đứng được khi tôi tự dẫn lại. Thm 3 còn đúng dưới điều kiện yếu hơn tài liệu nêu.

Phần phải sửa nằm ở các kết luận rút ra từ định lý, tức §0, §5, §8.7, §10:
- "Regime duy nhất" chỉ đúng khi η ≤ β.
- "T(f) ≡ 0 khi K > rank" sai như đã viết.
- Cột R1′ ở §8.7 dùng một ngưỡng không valid trong chính regime mà §5 cho là có nội dung.
- V2 với λ_n = n^{-1/3} (tốc độ số chính của tài liệu) vượt mức nặng ở K ≥ 70, là vùng K chưa từng được mô phỏng.

RG1 chưa nên ghi PASS và RG2 chưa nên pre-register cho tới khi các điểm M1–M4 ở mục 2 được xử lý.

## 2. Phát hiện, nặng nhất trước. Không có FATAL.

### A. Lỗi đã xác nhận

**M1. MAJOR: §5 bảng regime, §0 mục 3 ("Regime duy nhất mà R1 có thể có nội dung").**
- *Sai ở đâu:* bảng chỉ xét lớp η ≤ β, nhưng phát biểu không ghi điều kiện này. Ngoài lớp đó, R1 và CT khác nhau về chất, kể cả khi √nη ≫ 2t_K.
- *Phản ví dụ:* collider X→Z←Y với hệ số 0.5 và 0.05, β = 0.022, M = 25 DAG, K = 6, 600 replicate.

| η = 0.2 > 2β, n | 200 | 500 | 1000 | 2000 | 5000 | 10⁴ | ≥ 2·10⁴ |
|---|---|---|---|---|---|---|---|
| FWER CT | .565 | .83 | .918 | .983 | 1 | 1 | 1 |
| FWER R1 có abstain | .82 | .93 | .815 | .61 | .19 | .013 | 0 |
| FWER R1 không abstain | .822 | 1 | 1 | 1 | 1 | 1 | 1 |
| FWER BL1 (hộp Bonferroni) | .123 | .922 | .805 | .603 | .165 | .01 | 0 |

- *Chiều ngược lại:* với β ∈ (η/2, η) (η = 0.04, 400 replicate), CT đúng pattern khi n ≥ 5·10⁴ (FWER 0, chứng nhận .67–.82). R1 khi đó C_n luôn rỗng và chứng nhận 0.
- *Giải thích:*
  - Khi β < η/2, CT sai vĩnh viễn và im lặng; R1 tự phát hiện qua C_n = ∅.
  - Khi η/2 < β < η, CT thắng.
  - Lợi thế tự phát hiện không riêng của R1, vì BL1 cũng có.
- *Sửa:* thêm vào bảng hàng "η > β" và ghi "regime duy nhất **trong lớp** 𝓟_n".
- *Liên quan:* dòng này cũng mô phỏng luôn kịch bản mà §8.4 và §11 ghi "chưa mô phỏng" (Mệnh đề 4c). FWER của R1 lên tới 0.93 ở cỡ mẫu trung bình.

**M2. MAJOR: §8.2 ("V2 hơi anti-conservative khi K lớn"), §10.1, §10.4. Giới hạn hữu hạn mẫu, không phải lỗi Thm 3.**
- *Đo được:* P(W_n > ĉ_n), Q đủ bậc ≤ 2, R = I hoặc DAG thưa, λ = n^{-1/3}.

| K (p) | n = 200 | n = 500 | n = 1000 | n = 5000 | V1 cắt cứng |
|---|---|---|---|---|---|
| 70 (5) | .114–.124 | .086–.092 | .064–.072 | .051–.062 | .046–.053 |
| 165 (6) | **.216** (R = I) | .153 (R = I) | .089–.112 | .061–.070 | .046–.064 (trừ dòng R thưa n = 200, n = 500 tôi chưa đọc) |
| 616 (8) | **.58–.67** | chưa chạy | **.24–.30** | chưa chạy | .05–.11 |

- *Nguyên nhân [Inference]:* sai số tương đối của metric có hằng số tăng theo K. Vector z − ζ có chuẩn² cỡ K, và một góc lệch cỡ n^{-1/2} giữa các không gian riêng rò vào hướng bị nhân 1/λ.
- *Tăng λ thì mức về đúng* (R = I): K = 70, n = 1000 cho .081 / .061 / .050 ứng với λ = n^{-1/3} / 0.5 / 2. K = 165, n = 500 cho .141 / .073 / .056.
- *Mâu thuẫn với power (xem M3):* λ lớn xóa đúng phần lợi R² mà Mệnh đề 8 dựa vào.
- *Giới hạn của phép đo:* P(W > ĉ) chỉ là cận trên của FWER. Tôi **chưa đo FWER thật** ở K ≥ 70, nên đây là "bảo đảm không còn được cận này che", chưa phải bằng chứng FWER vượt α.
- *Sửa:* RG2 phải khai báo λ theo K và thêm K ≥ 70 vào kiểm tra size. Từ "hơi" không còn đúng.

**M3. MAJOR: Mệnh đề 8, §8.7, §10.4, §0 mục 4 ("R² chính là đại lượng quyết định").** Ba lỗi chồng nhau.
- *(a) Cột R1′ dùng ngưỡng χ²_{|I′|}.* Đây là ngưỡng mà Thm 6(b) chứng minh không đều, nên không valid trong regime h < 2t_K, tức regime duy nhất §5 cho là có nội dung. Tôi đo trên dữ liệu Gaussian thật: Q = {XY, XY|Z, XZ}, I = {1, 2}, D = {3}, ζ_D tại biên, rớt rank bên trong khối I, 2500 replicate.
  - P(bác bỏ m*) với ĉ_I là **.087–.110** ở h = 2–14.
  - Với chi-bar là .029–.058.
  - Vậy các cột R1′ và cột break-even tương ứng so sánh một thủ tục không hợp lệ trong regime đó.
- *(b) Giả thiết "ràng buộc inactive" của Mệnh đề 8(ii)–(iii) mâu thuẫn với regime này.* Nó cần |z_k| ≥ √n_kη + √S_m trên D. Vì lý do đó, phép sàng lọc rẻ của Mệnh đề 6(ii) cũng ít khi kích hoạt ở đó.
- *(c) Công thức NCP là của Σ⁻¹, không phải của V2.* Theo chính Mệnh đề 6(iii), mẫu số thật là (1+λ)(1−R̂²_λ).
  - Với một query trong I: 1+λ − r²/(1+λ).
  - Ở R² = .9, λ = .1 (n = 1000): .282, thay vì .1. Lợi ích giảm từ 10 lần xuống 3.5 lần.
  - Ở K = 70, |I′| = 3, tính tay xấp xỉ với I gồm một query, break-even .24 thành khoảng .37.
- *Ngoài ra:* break-even còn phụ thuộc (K, r, |I′|). Bảng chỉ cho 90% power, một đối thủ.
- *Thiếu đối thủ:* một contrast 1-df (z_k − bᵀz_I)/√(1−R²) có cùng NCP mà bậc tự do nhỏ hơn, nên "lợi từ R²" không phải của riêng χ². Danh sách đối thủ RG2 (§10.4) không có MaxT sau whitening, nên có thể nghiêng về R1.
- *Sửa:* tính lại bảng bằng c̄_m hoặc hybrid với metric ridge thật, và thêm đối thủ contrast/whitened.

**M4. MAJOR: §0 bảng và mục 1, Cor 4.1(d), `A1_pilot_readiness.md` §12.1.**
- *Phát biểu sai như đã viết:* "T(f) ≡ 0 khi K > rank" và "thu hẹp M theo sparsity không cứu được".
- *Phản ví dụ từ chính bảng của tài liệu:* K = 18, rank 6, M = DAG tối đa 2 cạnh cho 0/34 pattern mù và 0/24 feature có T ≡ 0. Tôi tái lập độc lập.
- *Điều kiện đúng:* M_¬f phải chứa một mô hình thỏa (B1)–(B2).
- *Kiểm tra số:* r + |I| < K, tức |D(m)| > r, là **điều kiện cần**. Nó đủ ở K = 24 (178/178), không đủ ở K = 18 (127 so với 99 pattern mù).
- *Khi K = rank:* Σ PD và không có mù.
- *Biến thể bị bỏ qua:* "Không dùng seminorm" chỉ đúng với seminorm **toàn cục cố định theo K**. Seminorm theo khối riêng từng mô hình, Ω_m = (Σ̂_II)⁺ ⊕ 0, cộng test một phía trên D (hybrid Thm 6(d) thay ridge bằng cắt cứng), thì không mù. Ví dụ z_{XY|Z} = 40 cho 1600, thay vì 0.
  - Nó có thể hơn hẳn ridge về size ở K lớn, vì V1 toàn cục giữ ≈ .05 đúng nơi V2 vỡ (M2).
  - [Hypothesis, chưa mô phỏng trực tiếp; size đều khi rớt rank trong khối là Open.]
- *Sửa:* ghi rõ phạm vi và đưa biến thể này vào danh sách ứng viên.

**M5. MINOR: §0 mục 2 "power → 1".** Với quy tắc abstain của §1.3, kết quả đúng là liminf ≥ 1−α (Thm 5(iii)).
- Giới hạn thực tế là 1 − P(S_{m*} > ĉ_n).
- Ở S3: khối I có rank 2, nên 1 − P(χ²₂ > χ²_{3,.95}) = .980. Khớp .981 trong log.
- CT đạt → 1 nên R1 có abstain không nhất quán ở nghĩa này.

**M6. MINOR: Mệnh đề 5(iii) "R1 chứng nhận mọi thứ BL1 chứng nhận".** Khi C_n = ∅ ≠ C_n^B thì R1 abstain còn BL1 vẫn assert. Sửa: thêm "khi C_n ≠ ∅", như Thm 6(a) đã làm.

**M7. MINOR, phần thân định lượng đánh giá thấp mức hỏng.**
- §0 mục 2 viết oracle "đuôi tới 0.124". Thực ra sup → 1. Trên đường a = c/√n, b = 0, giới hạn U² + (wv/c)² cho:

| c | .05 | .1 | .25 | .5 | 1 |
|---|---|---|---|---|---|
| Đuôi đo được (n = 5000, khớp giới hạn) | .772 | .633 | .401 | .224 | .126 |

- V0 không dừng ở .0609/.063. Với a = b = c/√n, ρ_XY = c²/n, dữ liệu thật n = 5000: c = 1.5 cho .088, c = 2 cho **.0906**. Giới hạn trên lưới đạt ≈ .09.

**M8. MINOR: Nhận xét 3.5, §10.2, `A1_mathematical_contract_v2.md` §11b, §0 ("cần √nλ_n → ∞").** Điều kiện này chỉ là **đủ**. **Thm 3 vẫn đúng dưới nλ_n → ∞**, chứng minh ngắn:
- Viết Σ(C) = M(C)M(C)ᵀ, M Lipschitz trên lân cận compact. Khi đó Σ̂ − Σ = ΔMᵀ + MΔᵀ + ΔΔᵀ với ‖Δ‖ = O_p(n^{-1/2}).
- Vì ‖A^{-1/2}M‖ ≤ 1, ta có ‖A^{-1/2}(Σ̂−Σ)A^{-1/2}‖ ≤ 2λ^{-1/2}‖Δ‖ + λ⁻¹‖Δ‖² = O_p((nλ)^{-1/2}).
- Bước 4 dùng Ostrowski cho (σ̂_j+λ)/(σ_j+λ). Tương tự, σ̂_j = O_p(1/n) với j > r, nên V1 chỉ cần nτ_n → ∞.
- *Số:* Q₂, λ = n^{-3/4} cho .040–.052. Hội tụ chậm và phụ thuộc K: K = 24 cho .145 / .108 / .098 / .073 ở n = 10³ / 5·10³ / 2·10⁴ / 10⁵.
- *Lưu ý:* công thức (wv)²/(2nλ) của Nhận xét 3.5 chỉ cho Σ oracle. Với Σ̂ plug-in, số hạng đó là (wv)²/(w²+v²+2nλ), nên V2 trên Q₂ không nổ kể cả khi nλ ≈ 2–3 (.037–.049). Vì vậy "quy tắc tốc độ" suy từ Day-2 không phải thứ chi phối V2. Điều chi phối là nλ so với K.

**M9. MINOR: §0 mục 4 "bị trội (Thm 6)".** Thm 6 chỉ chứng minh trội cho ngưỡng (a), là ngưỡng không đều. Với ngưỡng valid thì tài liệu không nêu kết quả, dù có chứng minh một dòng:
- v = 0 ∈ C₀^σ nên T₀^σ(G) ≤ GᵀÂ⁻¹G, từ đó **c̄_m ≤ ĉ_n**.
- Số xác nhận: c̄ > ĉ_n ở 0% replicate.
- Cận χ²_{K} trong (c) yếu hơn cận này.
- §10.1 chọn chi-bar làm ưu tiên trong khi bản Gaussian của nó còn là Sketch. Nhãn thì đúng, nhưng thứ tự ưu tiên đi trước bằng chứng.
- Thm 7 chỉ phát biểu cho ĉ_n chung; áp cho chi-bar cần ghi thêm (ngưỡng không phụ thuộc η nên chuyển được).

**M10. MINOR, các ghi chú nhỏ.**
- Cor 4.1(b): §9 gọi (B1)–(B2) là "đặc trưng" nhưng chỉ chứng minh chiều đủ. Chiều ngược đúng với η > 0:
  - Nếu 0 ≠ w ∈ 𝓛 ∩ C_I thì (wᵀz)² ≤ c·d².
  - Nếu e_k = ℓ + c_I thì với z_I = z_k = 0, d² ≥ δ_k²/c.
- Thm 5, dòng "dưới V1, không điều nào đúng": chỉ đúng khi có mô hình mù trong M_¬f.
- §3 Thm 2: "tính đều của V1 là Open" có thể thu hẹp. Khi Q chứa chart, σ_d liên tục dương trên 𝓚 nên V0 = V1 đều ngay.
- Bảng §5 hàng 1 bỏ mất điều kiện √nη_n → ∞ của Mệnh đề 7(i). Khi √nη_n = O(1), CT không nhất quán còn R1 vẫn valid (dù gần như không có power).

### B. Nghi ngờ chưa kết luận được

- **S1.** Không kịch bản nào trong tài liệu (và cả của tôi) cho thấy đồng thời CT vượt α và R1 có power dương.
  - Chain không có feature Q-identifiable, nên FWER R1 = 0 ở đó không nói lên gì.
  - Collider h ≤ 3 thì R1 chỉ chứng nhận ≤ .17, và CT không vi phạm mức.
  - Nội dung của R1 trong regime "có nội dung" vẫn chưa có chứng cứ.
- **S2.** Chưa kiểm được thủ tục chi-bar trên dữ liệu Gaussian ngoài một cấu hình K = 3, |D| = 1. Ở đó size ≤ .058 (SE .0044). Đối số liên tục tại nguyên tử 0 có vẻ đóng được bằng định lý Tsirelson cho hàm lồi của Gaussian, tôi chưa viết đầy đủ.

## 3. Sổ cái

| Phát biểu | Kết luận | Cách kiểm |
|---|---|---|
| Bổ đề 0, Lemma 1, (2.1) | CONFIRMED | Tự dẫn; 3 đường số (MC ψ N = 4·10⁶, z thô, 2tr(HRHR) sai số 3e-10) |
| Mệnh đề 2 (i)–(v) | CONFIRMED | Tự dẫn |
| Mệnh đề 3 | CONFIRMED | Tự dẫn, gồm dạng đóng Σ₁₂ = [ad − ½rq(a²+d²)]/(1−r²); tail .0172 |
| Giới hạn đường a = n^{-1/2} (nhãn Derived) | CONFIRMED, chưa là sup (M7) | Tự dẫn + số |
| Thm 1 | CONFIRMED | Tự dẫn |
| Thm 2 | CONFIRMED | Tự dẫn |
| Thm 3 | CONFIRMED, điều kiện yếu hơn được (M8) | Tự dẫn từng bước |
| Hệ quả 3.1–3.4 | CONFIRMED | Tự dẫn 3.1, 3.4; đọc 3.2, 3.3 |
| Nhận xét 3.5 | CONFIRMED cho oracle; không mang sang V2 (M8) | Tự dẫn |
| Thm 4 | CONFIRMED | Tự dẫn; dựng n tường minh trên Σ̂ mẫu thật, d² ≈ 1e-12 |
| Cor 4.1 | CONFIRMED WITH GAP (M4, M10) | Tự dẫn; p = 4 tái lập bằng d-sep và rank độc lập |
| Mệnh đề 4 | CONFIRMED | Tự dẫn |
| Mệnh đề 5 | CONFIRMED WITH GAP (M6) | Tự dẫn |
| Thm 5 | CONFIRMED | Tự dẫn |
| Mệnh đề 6 | CONFIRMED | Tự dẫn |
| Mệnh đề 7 | CONFIRMED (lớp η ≤ β) | Tự dẫn; bảng regime theo M1 |
| Mệnh đề 8 | Công thức CONFIRMED; diễn giải sai phạm vi (M3) | Tự dẫn |
| Thm 6(a), (b), (d) | CONFIRMED | Tự dẫn; (b) cũng đo trên Gaussian |
| Thm 6(c) | Working model CONFIRMED; Gaussian là Sketch, nhãn đúng | Tự dẫn + 1 cấu hình số |
| Thm 7 (a)–(d) | CONFIRMED | Tự dẫn, không chạy lại số |
| Thm 7(e) | Nhãn Inference, chấp nhận | Chỉ đọc |
| §1.2 ngữ nghĩa | CONFIRMED WITH GAP | Đọc nguồn, xem mục 6 |

Không có mục WRONG ở cấp định lý. Câu trả lời cụ thể cho mục 1 của đề: tính đều giữ được cả với Σ_n trôi về rớt rank. Sup trên (P, m*) hợp lệ vì luật của (z, Σ̂) chỉ phụ thuộc R, và sự kiện W_n > ĉ_n không phụ thuộc m*. Hằng số thì không đều theo K (M2).

## 4. Diễn giải đúng về toán nhưng quá mức

- "Không giả định beta-min" (Thm 7b): đúng, nhưng giả định chỉ chuyển vào vế "hoặc". Muốn đọc thành "f đúng" vẫn phải giả định β > η*(f). Với P không faithful theo m*, β = 0 và phát biểu rỗng.
- "Valid nhưng rỗng nghĩa" công bằng với Ω toàn cục khi có mô hình |D| > r; không công bằng với "seminorm" nói chung (M4).
- "h_CT" là điều kiện đủ. Trên chain, đo 10⁵ replicate:

| h | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| FWER CT | .2115 | .1287 | .0482 | .0143 |

Tài liệu ghi .112 ở h = 2 với 1000 replicate, thấp hơn khoảng 1.6 SE. Như vậy khoảng thực sự có khác biệt trên họ này hẹp hơn h < 5.28.

- "Nhận định R2 phần phụ phải đảo lại": hợp lý trong lớp η ≤ β, nhưng tài liệu chưa có bằng chứng R2 hữu ích.
- §10.1 và tính khả thi: d² là min trên 2^{|D|} orthant và c̄_m là max trên từng ấy nón. §11 ghi "chưa đo", song ưu tiên chi-bar ở §10.1 chưa tính đến điều này khi K lớn.

## 5. Kiểm toán số và số của tôi

**Khớp:**
- 211 PASS, 0 FAIL trong log.
- Tôi đối chiếu tay mọi khoảng ở §8.2, các dòng §8.4, §8.6, §8.7 với log: khớp.
- Q₂ giữa JSON và log: 0/24 lệch.
- K, L có trong JSON, nhưng được ghép tay sau (file partial không còn, meta có ghi chú), nên JSON không phải output trực tiếp của một lần chạy.

**Vấn đề:**
- Các giá trị "Dự đoán" .1247, .0186, .0905, .0609 ở §8.1 **không có** trong script, log hay JSON. Chúng vẫn đúng: tôi tính ra .1249, .0188, .0908, .0609.
- Assertion yếu:
  - Size chỉ kiểm ở n = 5000, dung sai .015–.02 (10 SE), nên .064 cũng qua.
  - `E.Lipschitz` có hằng số cỡ 245 so với bước rất nhỏ, gần như không thể fail.
  - `G.noncentral` tính thẳng Schur, không chạy solver vùng; comment "inactive" không được dùng, nên là đồng nhất thức.
  - `H.R1 FWER` trên chain không thể fail vì R1 không có gì để assert.
  - `I.chi-bar` chỉ dùng δ = 2 (max .034), không chạm LFC, mà header ghi "exact".
- Bảng đuôi dùng chung (common random numbers) gây lệch cố định không có trong SE. Tái tạo bằng seed tác giả, tail thật tại quantile bảng là .0483 (trọng số (1,1)) và .0490 ((1,0)). Điều này giải thích một phần cột V2 Q₂ thấp hơn cột cắt cứng khoảng .001–.002.
- Check H: đổi kịch bản đã được công khai đúng. Không có check nào bị làm cho pass giả bằng cách đổi ngưỡng. Nhưng các dòng "S1, η = 1.5n^{-1/4}" (η > β ở n nhỏ, FWER ≤ .002) có trong log và không vào §8.6. Chúng cho ấn tượng dễ chịu, trái với M1.
- K tối đa chỉ 24, trong khi §8.7 suy luận tới K = 70 và hơn.
- J: Day-2 đúng là dùng Σ oracle và χ²_rank, nên công thức đối chiếu đúng. Dung sai .03 khá rộng, và công thức được viết sau khi đã có số Day-2.

**Số của tôi** (ngoài các bảng ở mục 2):
- (2.1): |Cov ψ − (2.1)| ≤ .0035 và |Cov z − …| ≤ .021 (K = 8, p = 5, sai số MC mong đợi tương ứng .0015 và .018).
- Mù: tái lập 7/11 (p = 3), 99/137 và 178/185 (p = 4), cả ở Σ tại R lẫn Σ̂ mẫu.
- Nỗ lực phá của tôi **không thành** trên:
  - K = 2^m subset độc lập: size **thấp hơn** α (K = 64, n = 200: .011; K = 256: ≤ .006). Dự đoán "lạm phát" ban đầu của tôi sai.
  - Nhiều khối rớt rank, K ≤ 16: .043–.069.
  - Gần biên PD: K = 6 với λ_min = .001 cho .044–.056; K = 24 cho .044–.095, phần cao ở n ≤ 200.

## 6. Kiểm tra nguồn

- **Richardson–Spirtes:**
  - Thm 4.18 đúng nguyên văn (tr. PDF 20, 30).
  - Lemma 4.7 đúng là chỉ cho bao hàm, nên loại selection là đúng.
  - Cor 4.8 đúng, nhưng là về **ant (anterior)**, không phải ancestor. Tài liệu thiếu bước: G là DAG và S = ∅ nên không có cạnh vô hướng, do đó anterior = ancestor. Cũng thiếu bước Markov toàn cục ⇒ CI ⇒ θ_k = 0. Gap nhỏ, vá được.
- **Silvapulle–Sen Thm 3.8.1:** đúng (PDF tr. 106, khớp tr. 91). Định lý cho nón lồi đóng với V PD; tài liệu chỉ mượn lập luận bao hàm tập, ghi vậy là đúng.
- **Wang–Kolar–Drton Lemma 3:** đúng là 1−2α. Nhưng "khác biệt duy nhất: dùng chung một sự kiện" không chính xác. Theo chứng minh của họ, khi ordering duy nhất đã có 1−α (eq. 23); 2α đến từ việc cần **hai** ordering đúng cùng nằm trong tập.
- **Drton–Xiao Thm 2.3 (Glonek):** đúng, Wf,Σ ~ ¼χ²₁, Bernoulli 2016, v2.
- **Dufour–Valéry:**
  - Cor 8.7 đúng ("will destroy power"), Prop 8.1 và Prop 10.1 đúng. Prop 10.1 có b_nc_n → ∞ tức cùng điều kiện √nλ_n → ∞, và họ nêu cn = n^{-1/3}.
  - Cor 8.3–8.4 cho cận trên, và họ nói dùng χ² chuẩn gây méo size.
  - Điều này củng cố kết luận "V2 không mới về kỹ thuật".
- **Không xác minh:** bản công bố của Dufour–Valéry; Andrews 1987; Dufour–Renault–Zinde-Walsh.

## 7. Chưa kiểm

- FWER thật ở K ≥ 70.
- Size của seminorm theo khối (M4).
- Sup của FWER CT trên toàn họ ngoài chain.
- Thm 7 trên dữ liệu mới (chỉ tự dẫn).
- Chi-bar với |D| > 1 trên dữ liệu Gaussian.
- MAG có bidirected.
- Browne 1984, Berger, Uhler et al., Shah–Peters, và phần Robins et al. mà tài liệu trích.
- K = 256 chỉ tới n = 1000 (tôi dừng job vì chậm). K = 616 chỉ n = 200, 1000 với 120 replicate (SE ≈ .02).
- `A1_pilot_readiness.md` §12 và `A1_mathematical_contract_v2.md` §11b chỉ đọc ở phần liên quan.
