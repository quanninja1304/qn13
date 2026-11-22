# P-N6: so sánh cách sửa theo thông tin mỗi cách dùng, gap 3 (luật v0, NHÁP, 22/11/2026)

> **Trạng thái:** v0, **NHÁP, chưa khóa.** Chưa sinh input P-N6 nào và chưa chạy model nào.
> Sau khi user duyệt: khóa v1 (commit, push), viết code mới, chạy DEV6 và các cổng, đóng băng, rồi chạy.
>
> **Nguồn:**
>
> - gap 3 của [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md) §2;
> - nhánh R của [HELD2](../n2_context_mechanism_2026-11-20/PN2_HELD2_results_vi.md) §4 (mô tả);
> - số thiết kế: [`design/pn6_design_inputs.py`](design/pn6_design_inputs.py) và [`design/pn6_design_inputs.json`](design/pn6_design_inputs.json). Script chỉ đọc output đã đóng băng của P-N2, không chạy model.
>
> **Phạm vi đề xuất:**
>
> - AVICI và CDFM;
> - dữ liệu tổng hợp mới (8 ô như HELD2), k = 20, đệm Gauss và đệm có cấu trúc;
> - thêm hai bảng thật của P-N5 cho phần độ đổi.

## 0. Câu hỏi và điều không thể kết luận

- **Câu hỏi chính:** một cách sửa chỉ dùng bảng input, không biết khối nào là đích và không biết họ cơ chế, có khôi phục kết luận trên khối đích khi thêm cột độc lập không? Và nó tốn bao nhiêu chất lượng khi không có đệm (k0)?
- **Câu hỏi phụ:** các cách sửa ở decoder của CDFM dùng nhiều thông tin hơn. FROZEN dùng lần chạy k0; ngưỡng cục bộ biết khối đích. So với chúng, cách sửa chỉ dùng input giữ output ban đầu tốt hơn hay kém hơn?
- **Logic:** cột thêm vào độc lập với khối đích theo thiết kế, nên đáp án ở mức tổng thể trên khối đích không đổi (luật P-N1 §1). Một cách sửa tốt phải giữ chất lượng ở k0, và trên bảng có đệm phải cho kết quả gần output ban đầu.
- **Không kết luận được:**
  - cách sửa có ích với biến có sẵn trong dữ liệu thật, vốn không độc lập với khối đích theo thiết kế;
  - cách sửa là tối ưu, hay tốt hơn các cách không được thử (ví dụ MambaPFN, chỉ ở related work);
  - bất kỳ điều gì về FoundCause;
  - trên bảng thật, bất kỳ điều gì về độ chính xác (như P-N5).

## 1. Các cách sửa và thông tin mỗi cách dùng

| Cách | Thông tin dùng | Vai trò | Model |
|---|---|---|---|
| plain | không | mốc | AVICI, CDFM |
| **R-L** (HSIC mọi cặp, mức cố định mỗi cặp) | chỉ bảng input | ứng viên chính (đề xuất) | AVICI, CDFM |
| **R-H** (HSIC mọi cặp, Bonferroni trên toàn bảng) | chỉ bảng input | ứng viên so sánh | AVICI, CDFM |
| R-B (R của P-N2) | bảng input **và họ cơ chế**: Fisher-z cho hệ tuyến tính, HSIC cho RFF; Bonferroni trên toàn bảng | đối chiếu với HELD2; tùy chọn chạy lại (§12) | AVICI, CDFM |
| FIXED 0.5 | không thêm; bỏ bộ chọn ngưỡng | đối chứng decoder | CDFM |
| FROZEN | lần chạy k0 trên riêng khối đích | đối chứng, dùng nhiều thông tin hơn R | CDFM |
| Ngưỡng cục bộ | biết khối đích: đặc trưng ngưỡng chỉ tính trên các cặp đích | đối chứng, dùng nhiều thông tin hơn R | CDFM |
| R-oracle | ranh giới đích/đệm thật | kiểm sanity; trùng k0 theo cấu trúc | chỉ ở cổng |

- **Sửa bảng thông tin cũ:**
  - Bảng ở gap 3 ghi rằng R "chỉ dùng dữ liệu input". Thực ra R của P-N2 chọn phép kiểm theo họ cơ chế đã biết (`run2.py`: Fisher-z nếu hệ tuyến tính, HSIC nếu RFF). Như vậy nó dùng thêm thông tin về họ cơ chế.
  - P-N6 gọi cách đó là R-B, và thêm hai biến thể không dùng thông tin này.
- **Nguyên tắc cục bộ, giả thuyết thiết kế của P-N6:** một quyết định về khối đích không nên phụ thuộc vào thống kê tính trên toàn bảng.
  - Bộ chọn ngưỡng của CDFM vi phạm điều này (C5, C6a).
  - Phép hiệu chỉnh Bonferroni trên mọi cặp của bảng cũng vậy. Mức cho mỗi cặp là α / (D(D − 1)/2), nên quyết định giữa hai biến đích có thể đổi khi D đổi.
  - **Số thiết kế** (EXP2, mô tả): khi thêm 20 cột Gauss, Bonferroni tách thêm cạnh đích ở 1/20 hệ RFF (trung bình +0.25 cạnh), và ở 1/20 hệ tuyến tính nếu dùng HSIC (+0.20). Fisher-z trên hệ tuyến tính: 0/20.
- **Vì sao R-L bất biến theo cấu trúc:**
  - p-value HSIC của một cặp chỉ phụ thuộc hai cột của cặp đó, và khối đích trùng từng bit giữa các input của một hệ.
  - Với mức cố định mỗi cặp, phân hoạch của các biến đích vì vậy giống hệt nhau ở k0 và ở mọi input có đệm.
  - Nếu không cột đệm nào bị gộp nhầm vào thành phần chứa biến đích, model nhận đúng cùng input trên mỗi thành phần đích, nên output trên khối đích trùng từng bit với k0. Đường đổi duy nhất còn lại là gộp nhầm.
- **Cái giá của R-L:**
  - R-L không thắt mức khi bảng lớn lên. Với một phép kiểm hiệu chỉnh tốt, số gộp nhầm kỳ vọng xấp xỉ α_L · d_T · k mỗi input.
  - Đuôi gamma của HSIC dễ dãi: ở P-N2 (G9), tỉ lệ bác bỏ thực tế gấp 3–4 lần mức danh nghĩa 0.001. Với mức nhỏ hơn mà R-L sẽ dùng, sai lệch này chưa được đo, nên số gộp nhầm thật có thể cao hơn.

## 2. Dữ liệu

- **Tổng hợp, held-out mới:**
  - seed base 480000, chưa dùng ở tập nào trước; DEV6 dùng base 490000;
  - 8 ô như HELD2: d_T ∈ {10, 20}, e_T ∈ {1, 2}, tuyến tính và RFF; đồ thị ER; n = 500. Khối đích sinh bằng `common.py` đã đóng băng của P-N1, seed 480000 + 1000·c + r;
  - đệm sinh bằng bộ sinh lồng nhau của P-N2 (`common2.py` đã đóng băng), k = 20: e = 0 (Gauss, tức kiểu A) và e = e_T (có cấu trúc), cùng họ cơ chế với khối đích;
  - đề xuất 120 hệ (15 mỗi ô), như HELD2 (§10);
  - input mỗi hệ: k0, A20 (e = 0) và S20 (e = e_T).
- **Bảng thật,** chỉ cho phần độ đổi:
  - X_R đã lưu của P-N5 (Sachs, Wine), cùng đúng các lần sinh đệm Gauss của P-N5 ở k = 20 và k = 40. Mã băm của các input này đã có trong `checks/inputs5.json` của P-N5.
  - Output plain của P-N5 đã được xem; chỉ output của R-L và R-H là mới.
  - R-B không áp dụng được cho bảng thật, vì họ cơ chế không biết.

## 3. Cách sửa: định nghĩa

- **R-H:** HSIC (hàm `p_hsic` đã đóng băng của P-N2) trên mọi cặp; bác bỏ khi p < α_H / (D(D − 1)/2).
- **R-L:** HSIC trên mọi cặp; bác bỏ khi p < α_L, không hiệu chỉnh theo bảng.
- **R-B:** đúng như P-N2: α_Fz = 0.05 cho hệ tuyến tính, α_HSIC = 0.01 cho RFF, Bonferroni trên mọi cặp.
- **Thành phần:**
  - lấy các thành phần liên thông của đồ thị các cặp bị bác bỏ;
  - model chạy trên mỗi thành phần có từ 2 biến trở lên và chứa ít nhất một biến đích. Điều kiện "chứa biến đích" chỉ chọn output cần đọc; quy trình sửa không cần biết khối đích;
  - cặp đích nằm ở hai thành phần khác nhau là không-cạnh.
- **Chọn α trên DEV6,** trước khi đóng băng và không dùng output model:
  - tiêu chí J = merged/k + split/|E_T| như P-N2, tính trên A20 và S20, trung bình qua cả hai họ, vì cách sửa không biết họ;
  - lưới: α_H ∈ {0.001, 0.01, 0.05}; α_L ∈ {10⁻⁵, 10⁻⁴, 10⁻³}; hòa thì chọn mức nhỏ hơn;
  - báo thêm số tách nhầm ở k0 cho mỗi mức.
- **Đối chứng decoder của CDFM,** tính từ output plain, không chạy thêm model:
  - FIXED: max(p_ij, p_ji) > 0.5;
  - FROZEN: p_ij > τ của plain ở k0;
  - ngưỡng cục bộ: bộ chọn ngưỡng của CDFM (bản chép lại đã đóng băng ở P-N4, `selector4.py`), áp lên ma trận xác suất của riêng khối đích (D = d_T). Ở k0, cách này trùng NATIVE.
- **R-oracle:** model trên riêng khối đích. Theo cấu trúc, nó trùng plain ở k0 từng bit; chỉ kiểm ở cổng G4, không chạy trên held-out.

## 4. Biến đo

Dữ liệu tổng hợp, cho mỗi hệ, cách sửa f và input c ∈ {A20, S20}:

- F1 skeleton của f(c) so với skeleton thật của khối đích;
- **giá ở k0:** Q0_f = F1_f(k0) − F1_plain(k0);
- **khôi phục:** Q_f(c) = F1_f(c) − F1_plain(k0);
- **lợi ích:** G_f(c) = F1_f(c) − F1_plain(c);
- **flips trung thành** φ_f(c): số cặp đích có trạng thái skeleton của f(c) khác plain ở k0. Đây là thước đo chung cho mọi cách sửa, vì mọi cách đều so với cùng một output ban đầu;
- **flips tự bất biến** σ_f(c): f(c) so với chính f ở k0;
- Δm so với plain ở k0;
- chỉ số sàng lọc: số cột đệm gộp nhầm, số cạnh đích tách nhầm, số cặp đích–đệm bị bác bỏ, số thành phần đích.

Bảng thật: σ_f(c), φ_f(c) và φ_f(k0), tức độ lệch ở k0 nếu sàng lọc tách khối thật. Không có thước đo chất lượng.

## 5. Giả thuyết (đề xuất: 6, Holm 0.05)

R\* là cách sửa chính chỉ dùng input. Đề xuất R\* = R-L; user chọn giữa R-L và R-H (§12).

| ID | Model, họ | Contrast theo hệ | Dự đoán | Phép kiểm |
|---|---|---|---|---|
| P6-1A-lin | AVICI, tuyến tính | Q_R\*(A20) | nằm trong (−0.03, +0.03) | TOST |
| P6-1A-rff | AVICI, RFF | Q_R\*(A20) | như trên | TOST |
| P6-1C-lin | CDFM, tuyến tính | Q_R\*(A20) | như trên | TOST |
| P6-1C-rff | CDFM, RFF | Q_R\*(A20) | như trên | TOST |
| P6-2C-lin | CDFM, tuyến tính | φ_FROZEN(S20) − φ_R\*(S20) | > 0 | một phía |
| P6-2C-rff | CDFM, RFF | φ_FROZEN(S20) − φ_R\*(S20) | > 0 | một phía |

- **P6-1** hỏi: chạy R\* trên bảng có 20 cột Gauss có cho F1 trong biên ±0.03 quanh F1 của output ban đầu không.
  - Contrast gộp cả giá ở k0 (tách nhầm) lẫn độ đổi do đệm (gộp nhầm).
  - Đây là điều kiện chuẩn của P-N1, nơi mức hại đã được xác nhận (C1).
- **P6-2** hỏi: ở đệm có cấu trúc, nơi kênh ngưỡng quan trọng (C5), R\* có giữ output ban đầu tốt hơn FROZEN không.
  - FROZEN dùng nhiều thông tin hơn R\*, nhưng chỉ chặn kênh ngưỡng; điểm của khối đích vẫn đổi. Ở HELD2, với CDFM RFF, số cạnh theo FROZEN tăng +5.07 [+2.89, +7.25] khi đổi từ đệm Gauss sang đệm có cấu trúc (REP, mô tả).
  - Cả hai cách được đo bằng flips trung thành, nên giá ở k0 của R\* bị tính vào. Phép so này nghiêng về phía bất lợi cho R\*.
- **Phép kiểm:**
  - t phân tầng theo ô như HELD2: w_c = 1/4 trong một họ, SE² = Σ_c w_c² s_c² / n_c, df Welch–Satterthwaite;
  - TOST là hai phép một phía, so với −0.03 và +0.03; p của giả thuyết là p lớn hơn;
  - SE = 0 thì ghi DEGENERATE, dùng p = 1 và không xác nhận;
  - Holm ở mức familywise 0.05 trên đúng sáu p-value.
- **Giới hạn:**
  - CONFIRMED ở TOST nghĩa là trung bình có điều kiện nằm trong biên. Nó không nghĩa là mọi hệ nằm trong biên, và không chứng minh bất biến ở từng hệ.
  - CONFIRMED ở P6-2 chỉ xác nhận dấu.
  - CI và nhãn cỡ của từng giả thuyết là mô tả; Holm không bảo vệ chúng đồng thời.

## 6. Báo cáo mô tả (không thuộc bộ Holm)

- Mọi cách sửa × model × họ × input: Q0, Q, G, φ, σ và Δm, với trung bình, CI theo t phân tầng và nhãn cỡ (biên 0.03 cho F1, 1.5 cạnh cho Δm).
- **R-L so với R-H:**
  - σ và φ; số hệ có σ > 0;
  - với R-L, tách σ theo có hay không có gộp nhầm. Theo §1, σ = 0 ở mọi input không gộp nhầm; completeness kiểm điều này.
- R-B, nếu chạy lại: như trên, để so với HELD2 và đo tác dụng của thông tin về họ cơ chế.
- Ngưỡng cục bộ và FIXED: φ và σ.
- Trường hợp xấu nhất: |Δm| lớn nhất theo hệ, cho mỗi cách sửa.
- **Bảng thật:**
  - σ và φ của R-L và R-H ở k = 20 và k = 40, số lần sinh có σ > 0, và φ(k0);
  - so với plain chỉ để mô tả, vì output plain đã được xem ở P-N5.

## 7. Kiểm hoàn tất trước khi đọc

Như P-N5:

- mọi job có đúng một trạng thái kết thúc, không có `error`;
- mã băm input khớp input sinh lại; khối đích trùng từng bit giữa các input của mỗi hệ;
- với bảng thật, input khớp mã băm trong `checks/inputs5.json` của P-N5;
- cổng đóng băng `ok` ở đầu và cuối lượt, cùng commit;
- **kiểm cấu trúc của R-L:** ở mọi input held-out không có gộp nhầm, output R-L trên khối đích trùng từng bit với R-L ở k0. Nếu điều này sai, kết quả không được đọc và báo user, vì nó chỉ ra lỗi cài đặt.

## 8. Cổng (DEV6, base 490000, 2 hệ mỗi ô = 16 hệ)

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | Sinh input: khối đích như P-N1, đệm như P-N2, cùng seed thì trùng từng bit | trùng từng bit |
| G2 | HSIC dùng đúng hàm đã đóng băng của P-N2; p-value của các cặp đích giống hệt nhau ở k0, A20 và S20 | trùng từng bit |
| G3 | Chọn α_H và α_L bằng J trên DEV6, không dùng output model; ghi lại trước khi đóng băng | có bản ghi |
| G4 | R-L: phân hoạch biến đích giống k0 ở mọi input; output trùng k0 từng bit khi không gộp nhầm. R-oracle trùng plain ở k0 từng bit | trùng từng bit |
| G5 | Bộ chọn ngưỡng chép lại tái lập ngưỡng NATIVE của CDFM trên output DEV6; ngưỡng cục bộ ở k0 bằng NATIVE | ≤ 1e-12 |
| G6 | Code kiểm định: t phân tầng và TOST so với cài đặt tham chiếu; Holm; DEGENERATE | khớp; đúng kết quả định trước |
| G7 | Code đọc chạy hết trên DEV6, chỉ kiểm cấu trúc | không in hay ghi giá trị |
| G8 | Tất định: chạy lại k0 và một input có đệm cho mỗi model và mỗi biến thể R | trùng từng bit |
| G9 | Thời gian và bộ nhớ trên DEV6; ước tính tổng | ≤ 3 giờ; nếu vượt thì báo user |

## 9. Đọc kết quả

- **Câu được viết** (ví dụ): "Trên hệ tổng hợp mới, chạy R\* trên bảng có 20 cột Gauss cho F1 skeleton nằm trong ±0.03 quanh F1 của output ban đầu ở [ô], trung bình …"
- **Không được viết:**
  - "R\* sửa được vấn đề" mà không kèm phạm vi; "R\* bất biến ở mọi hệ";
  - rằng R\* áp dụng được cho biến có sẵn trong dữ liệu thật;
  - "R\* tốt hơn mọi cách sửa"; "FROZEN vô dụng";
  - trên bảng thật: "R\* đúng hơn" hay bất kỳ câu nào về độ chính xác;
  - "tương đương" cho một TOST không được xác nhận;
  - rằng CI hay nhãn cỡ được Holm bảo vệ.

## 10. Power và ngân sách (ước tính sơ bộ)

**Power cho P6-1** ước tính từ HELD2. HELD2 dùng R-B, có 60 hệ mỗi họ, và báo CI của giá ở k0; SE suy ra từ nửa độ rộng của CI.

- Ước tính dùng mức chặt nhất của Holm (0.05/6, một phía, t ≈ 2.48 với df ≈ 50) và xấp xỉ chuẩn cho μ̂.
  - TOST đạt khi cả hai cận một phía nằm trong biên, tức |μ̂| < 0.03 − 2.48·SE.
  - Giá trị μ lấy theo số "F1 sau R − F1 k0 ban đầu (e = 0)" của HELD2.
  - Ở các bước sau của Holm, mức nới hơn, nên power cao hơn.

| Ô | μ (HELD2) | SE (HELD2) | Power xấp xỉ |
|---|---|---|---|
| AVICI tuyến tính | −0.001 | 0.0087 | khoảng 0.67 |
| AVICI RFF | +0.007 | 0.0040 | gần 1 |
| CDFM tuyến tính | −0.021 | 0.0065 | **khoảng 0.14** |
| CDFM RFF | +0.001 | 0.0060 | khoảng 0.99 |

- Nếu R\* có giá giống R-B, P6-1C-lin nhiều khả năng **không** được xác nhận với 60 hệ mỗi họ. Muốn có power 0.8 ở ô này cần khoảng 360 hệ cho họ tuyến tính, gấp sáu lần, vượt ngân sách.
- Kết quả không xác nhận ở ô này vẫn là một phát hiện về giá của cách sửa, không phải lỗi thiết kế.
- Power ở AVICI tuyến tính chỉ ở mức vừa phải. 160 hệ (20 mỗi ô) sẽ nâng mức này.
- R-L và R-H có thể có giá khác R-B. Hồ sơ power chính thức, tính từ SD theo hệ của HELD2, sẽ ghi trong `design/` sau khi user chọn giả thuyết, như P-N4.
- **P6-2:** chưa có số trực tiếp cho flips trung thành của FROZEN hay của R ở S20.
  - Dự kiến hiệu ứng lớn, vì ở P-N1 held-out, CDFM NATIVE đổi 19.1 [14.9, 23.5] cặp mỗi hệ với 20 cột Gauss. Ở điều kiện đó, FIXED có mức hại gần bằng NATIVE (0.087 so với 0.085), nên kênh ngưỡng không phải đường chính.
  - Ở HELD2, sau R, Δm ở REP chỉ còn khoảng 0.1–0.2 cạnh.
  - Hồ sơ power sẽ tính trực tiếp từ output HELD2.

**Ngân sách,** từ thời gian chạy của HELD2 (120 hệ; cùng ba input k0, e = 0, e = e_T ở k = 20):

- plain: AVICI 22.9 phút, CDFM 38.3 phút;
- mỗi biến thể R: khoảng 14 phút (AVICI) và 19 phút (CDFM), đo với R-B; HSIC trên hệ tuyến tính có thể chậm hơn Fisher-z;
- bảng thật: 2 bảng × (k0 + 20 lần sinh × 2 mức k) = 82 input, × 2 biến thể × 2 model, ước tính khoảng 20–30 phút;
- **tổng với R-L và R-H:** khoảng 2.5 giờ. Nếu chạy lại cả R-B: khoảng 3.1 giờ, vượt 3 giờ;
- G9 đo lại trên DEV6 trước khi chạy.

## 11. Quy trình

1. User duyệt v0 và các điểm ở §12. Khóa v1: commit và push trên nhánh công khai, trước khi sinh input P-N6.
2. Viết code dưới dạng file mới trong `artifacts/n6_runs/pn6/`. Import nguyên trạng `common.py`, `common2.py`, `screen.py` và `selector4.py` đã đóng băng.
3. Chạy DEV6. Chọn α_H và α_L bằng J, không dùng output model. Chạy G1–G9. Đóng băng code, phụ thuộc và hai mức α; commit, push.
4. Chạy P-N6 nếu các cổng đạt và ước tính không vượt 3 giờ. Kiểm hoàn tất (§7), rồi đọc bằng code đã đóng băng.

## 12. Điểm cần user quyết

1. **R\* chính:** R-L (đề xuất) hay R-H.
   - R-L bất biến theo cấu trúc trên phân hoạch đích và thể hiện nguyên tắc cục bộ.
   - R-H gộp nhầm ít hơn khi bảng lớn, nhưng quyết định giữa hai biến đích phụ thuộc D.
2. **Có chạy lại R-B trên seed mới không.** Chạy lại cho phép đo trực tiếp tác dụng của thông tin về họ cơ chế, nhưng thêm khoảng 34 phút và đưa tổng lên khoảng 3.1 giờ. Đề xuất: không chạy lại; chỉ so mô tả với HELD2.
3. **Cỡ mẫu:** 120 hệ (đề xuất), hay 160 (20 mỗi ô) nếu muốn tăng power cho P6-1C-lin; 160 hệ vẫn không đủ cho ô này nếu giá thật gần −0.02.
4. **Bảng thật:** chỉ mô tả (đề xuất), hay khóa thêm 4 giả thuyết (bảng × model).
   - Nếu khóa, không dùng phép t: R-L cho σ = 0 ở mọi lần sinh không gộp nhầm, nên phép t sẽ DEGENERATE.
   - Thay vào đó, dùng phép kiểm nhị thức chính xác trên tỉ lệ lần sinh có σ > 0, so với một ngưỡng chọn trước, ví dụ 0.25.
5. **Có thêm k = 40 cho dữ liệu tổng hợp không,** để thấy rõ sự phụ thuộc vào D của Bonferroni (R-H so với R-L).
   - Việc này thêm khoảng 2–3 giờ: plain ở D = 50–60 cần khoảng 48 giây mỗi hệ cho hai model và hai input, cộng các lần chạy R.
   - Tổng khi đó vượt 3 giờ. Đề xuất: không thêm ở P-N6; ở bảng thật đã có k = 40, chi phí thấp.
6. **Biên:** 0.03 cho F1 như P-N2, và 1.5 cạnh cho Δm.
