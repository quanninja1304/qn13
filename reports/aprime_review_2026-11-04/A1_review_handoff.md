# A′ — Review handoff (cho agent độc lập tiếp theo)

> 2026-11-04. Thư mục: `reports/aprime_review_2026-11-04/`. Tài liệu gốc trong `reports/reassessment_2026-11-03_vi/` **không bị sửa**, trừ việc append decision log ở [PLAN] §9.
> **Quyết định: REFORMULATE + HOLD FOR SOURCE. Framing gốc của A′: STOP. Chưa có pilot nhân quả nào được phép chạy.** Chưa có user duyệt.

## Đã chứng minh (giấy, kiểm tra lại trong phiên; kèm số)

- **P1** oracle soundness đúng. Sửa: D hữu hạn (Θ(n)), **không** phải +∞. Unit test T-P1 gốc sai.
- **P2** đúng **chỉ khi Σ PD**, Q cố định, η đúng.
- **P3** = loss **kiểu ACI** với weights a_k (contract eq. 4.1) và ngưỡng |z| = δ/2 (tăng theo √n). **Không** trùng ACI Eq. 14/16 đã công bố.
- **P4** đúng, kèm công thức active (eq. 4.2). **P5** đúng dưới quy ước support. **P6** là GLR của *working model*. **P7** đúng cho score một phía.
- **Mệnh đề R:** rank Σ(Fisher-z Gaussian) ≤ p(p−1)/2.
- **Mệnh đề R′:** Q = {X⊥Y, X⊥Y|Z} có r = √(1 − ρ²_{XZ}) khi Y ⊥ (X, Z).
- **R1** (contract §7): assert f ⇔ d(z, R(M_¬f))² > χ²_{rank, 1−α}. Valid đồng thời cho mọi f, dưới Q cố định, joint CLT, beta-min. Chỉ là chứng minh phác thảo **chưa review độc lập**.

## Bị phản chứng

- (A1) "Σ PD trên query không trùng": **sai** (CE1, CE2).
- Diễn giải "đếm trùng" của P4: trong chính ví dụ đó, số hạng chéo có χ²_1 chính xác (CE3; toy B1: FAR diag = 0.049).
- H-cal cho D dạng hiệu: D_full trôi như diag ở δ = 3 (0.110 so với 0.105; toy B2).
- Protocol Δ_FAR trong [PLAN] §3: phạt phương pháp đúng (toy B3: full 0.871 so với diag 0.509).
- P5 dưới seminorm C-c (CE8). Quy ước support C-b gán +∞ cho mô hình đúng ở 100% replicate (toy C2).
- "z_1 = z_2 cho giới hạn hữu hạn khi r → 1": sai (erratum, toy §2.3).

## Chỉ quan sát ở toy (không phải bằng chứng nhân quả)

- Ranking giữa D_full và D_diag gần như không tương quan ở r = 0.9 (Kendall τ = 0.054).
- Full-Σ anti-conservative khi Σ̂ nhiễu: FAR 0.34 ở ν = 20.
- Evidence dependence-aware ≈ thống kê của query ngoài Q (corr −0.9998).
- η > 2 × hiệu ứng thật ⇒ D sai dấu với xác suất → 1.

## Đề xuất (chưa chạy)

- Gates RG0 (source) → RG1 (chứng minh) → RG2 (toy power so với Bonferroni) → RG3 (H-prev giải tích) → RG4 (pilot S1).
- Estimand E1: family-wise false certification + certification power. E2: η-profile.
- Baselines BL1–BL8 (`A1_pilot_readiness.md` §5).

## Chưa xác minh / thiếu

- Full text: Wang–Kolar–Drton JASA 2025 (**quyết định novelty**), Triantafillou PGM 2014, Silvapulle–Sen, Zhang 2008, Robins et al. 2003, văn liệu ADF/minimum-distance.
- Olkin–Finn và Shapiro 1985 chỉ là scan, chưa đọc.
- Joint CLT cho vector GCM: chưa có nguồn hay chứng minh.
- Kích thước M (MAG) ở p = 4, 5 và chi phí QP khi K lớn: UNKNOWN.

## Tái lập

```
cd reports/aprime_review_2026-11-04
python -P -E A1_toy_mechanism_validation.py          # ~5 phút; --quick để chạy nhanh
```

Kỳ vọng: 192 PASS, 0 FAIL. Output: `A1_toy_outputs.json`.

## Cập nhật 2026-11-04 (sau khi đọc thêm 19 nguồn)

- Không còn tài liệu chặn quyết định. Xem `A1_missing_references_register.md` §5.
- **RG0 PASS** (agent). Quyết định vẫn REFORMULATE, **bỏ HOLD**.
- Novelty hẹp:
  - projection = lập luận WKD Lemma 3;
  - test từng MAG = khung Browne 1984;
  - phần còn lại là công cụ cho setting latent/CI-based, và power.
- **Erratum:** R1 valid *pointwise* với η_n → 0. η chỉ cần cho guarantee uniform (contract §10b).
- Baseline mới BL9: Chang-style resampling chuyển sang feature.
- **Gate tiếp theo:** RG1 (chứng minh) + RG2 (toy power so với Bonferroni/BL9). RG2 là kill test.

## Cập nhật RG1 (2026-11-04)

Chi tiết: `RG1_R1_proof_vi.md`. Tái lập: `python -P -E RG1_numeric_checks.py` (khoảng 25 phút; kỳ vọng 211 PASS, 0 FAIL). Rà soát: `RG1_independent_review_vi.md` (`PASS WITH CORRECTIONS`). Đo lại sau rà soát: `python -P -E RG1_followup_checks.py` (khoảng 30 phút; K = 616 tốn nhiều RAM, lần đầu từng bị hệ thống dừng).

- **Validity của R1 đã có chứng minh đầy đủ.** Joint CLT và Σ dạng đóng (Lemma 1); V1 cắt rank pointwise (Thm 2); V2 ridge + χ² có trọng số đều trên compact, không cần ước lượng rank (Thm 3).
- **Bản seminorm + χ²_rank ghi ở trên và ở contract §7 rỗng nghĩa:** T(f) ≡ 0 khi M_¬f chứa mô hình mù (Thm 4). Ở p = 4, K = 24, chỉ cần M chứa DAG 2 cạnh là 24/24 feature tổ tiên không chứng nhận được. Đừng cài bản này.
- **Pointwise không phân biệt được R1:** thresholding nhất quán đạt tốt hơn (Mệnh đề 7). Chỉ regime √nη < 2t_K mới có thể có nội dung. R2 không còn là phần phụ (Thm 7).
- **Ngưỡng theo từng MAG trội ngưỡng chiếu** (Thm 6). Kết quả ở đối thủ một tọa độ phụ thuộc R²_{k|I} (Mệnh đề 8).
- **Đã có một lượt rà soát bởi agent AI; các sửa chữa đã áp dụng (§12 của file đó). Chưa có người rà; user duyệt PASS có điều kiện ngày 2026-11-05.** RG2 chưa chạy; đề xuất đặc tả mới ở §10.4.
- **Đính chính sau rà soát:** "K > rank" không đủ cho blindness; "regime duy nhất" chỉ trong lớp η ≤ β; ridge lệch nặng ở K lớn với λ = n^{-1/3}; chưa có kịch bản CT vượt α mà R1 có power dương.

## Cập nhật RG3 + S1 (2026-11-05)

RG1 được user duyệt PASS có điều kiện. Chi tiết phép thử: `RG3_S1_report_vi.md`. Tái lập: `python -P -E RG3_S1_checks.py` (khoảng 1.8 giờ). **Bước tiếp đề xuất, chưa duyệt:** so T với hộp sau whitening trên toàn vector, trên SCM mới.

## Cập nhật RG3b (2026-11-06)

Chi tiết: `RG3b_report_vi.md`. Tái lập: `python -P -E RG3b_T_vs_whitened_box.py` (khoảng 1.5–2 giờ, cần vài GB RAM trống; có `--resume`). **Lưu ý:** số T ở K = 70 trong `RG3b_outputs.json` là cận dưới lỏng; dùng `RG3b_k70_recheck.json`. Khuyến nghị: chuyển sang T4, chờ user quyết định.
