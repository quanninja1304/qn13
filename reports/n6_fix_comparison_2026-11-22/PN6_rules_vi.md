# P-N6: so sánh cách sửa theo thông tin mỗi cách dùng, gap 3 (luật v1, khóa ngày 22/11/2026)

> **Trạng thái:** **v1, ĐÃ KHÓA** bằng commit chứa dòng này. Commit được push trên nhánh công khai trước khi sinh bất kỳ input P-N6 nào.
>
> - v1 là bản nháp v0 (`c3dd77b`) cộng bốn chỉnh sửa theo review của user ngày 22/11 (§12).
> - Sau khi khóa, mọi thay đổi chỉ được ghi thêm vào §12 kèm lý do, và không được dựa trên output đã thấy.
>
> **Nguồn:**
>
> - gap 3 của [bảng claim](../manuscript_n1_2026-11-21/N1_claim_evidence_gap_vi.md) §2;
> - nhánh R của [HELD2](../n2_context_mechanism_2026-11-20/PN2_HELD2_results_vi.md) §4, chỉ để tham khảo;
> - số thiết kế: [`design/pn6_design_inputs.py`](design/pn6_design_inputs.py) và hồ sơ power [`design/pn6_power.py`](design/pn6_power.py). Cả hai chỉ đọc output đã đóng băng của P-N2, không chạy model.
>
> **Quyết định của user ngày 22/11:**
>
> | Điểm | Quyết định |
> |---|---|
> | Cách sửa chính | R-L; giữ R-H để so sánh |
> | Chạy lại R-B | Không. HELD2 chỉ để tham khảo, không dùng để quy chênh lệch cho thông tin về họ cơ chế |
> | Cỡ mẫu | 120 hệ, 15 mỗi ô |
> | Bảng thật | Chỉ mô tả; báo khoảng tin cậy cho tỉ lệ lần sinh có σ > 0 |
> | k = 40 tổng hợp | Chưa thêm trong P-N6 |
> | Biên | 0.03 cho F1, 1.5 cạnh cho Δm |

## 0. Câu hỏi và điều không thể kết luận

- **Câu hỏi chính:** một cách sửa chỉ dùng bảng input, không biết khối nào là đích và không biết họ cơ chế, có giữ chất lượng của kết luận trên khối đích, cả ở k0 lẫn khi thêm cột độc lập không?
- **Câu hỏi phụ:** các cách sửa ở decoder của CDFM dùng nhiều thông tin hơn: FROZEN dùng lần chạy k0, ngưỡng cục bộ biết khối đích. So với chúng, cách sửa chỉ dùng input giữ output ban đầu tốt hơn hay kém hơn?
- **Logic:** cột thêm vào độc lập với khối đích theo thiết kế, nên đáp án ở mức tổng thể trên khối đích không đổi (luật P-N1 §1). Một cách sửa tốt không được làm giảm chất lượng quá biên, ở k0 cũng như trên bảng có đệm.
- **Không kết luận được:**
  - cách sửa có ích với biến có sẵn trong dữ liệu thật, vốn không độc lập với khối đích theo thiết kế;
  - cách sửa là tối ưu, hay tốt hơn các cách không được thử (ví dụ MambaPFN, chỉ ở related work);
  - chênh lệch giữa R-L hoặc R-H với R-B của HELD2 là do thông tin về họ cơ chế: seed và điều kiện khác nhau;
  - bất kỳ điều gì về FoundCause;
  - trên bảng thật, bất kỳ điều gì về độ chính xác (như P-N5).

## 1. Các cách sửa và thông tin mỗi cách dùng

| Cách | Thông tin dùng | Vai trò | Model |
|---|---|---|---|
| plain | không | mốc | AVICI, CDFM |
| **R-L** (HSIC mọi cặp, mức cố định mỗi cặp) | chỉ bảng input | **cách sửa chính** | AVICI, CDFM |
| **R-H** (HSIC mọi cặp, Bonferroni trên toàn bảng) | chỉ bảng input | so sánh, mô tả | AVICI, CDFM |
| R-B (R của P-N2) | bảng input và họ cơ chế: Fisher-z cho hệ tuyến tính, HSIC cho RFF; Bonferroni trên toàn bảng | không chạy lại; HELD2 chỉ để tham khảo | — |
| FIXED 0.5 | không thêm; bỏ bộ chọn ngưỡng | đối chứng decoder, mô tả | CDFM |
| FROZEN | lần chạy k0 trên riêng khối đích | đối chứng, dùng nhiều thông tin hơn R-L | CDFM |
| Ngưỡng cục bộ | biết khối đích: đặc trưng ngưỡng chỉ tính trên các cặp đích | đối chứng, mô tả | CDFM |
| R-oracle | ranh giới đích/đệm thật | kiểm sanity; trùng k0 theo cấu trúc | chỉ ở cổng |

- **Sửa bảng thông tin cũ:** R của P-N2 chọn phép kiểm theo họ cơ chế đã biết (`run2.py`), nên nó không phải cách sửa "chỉ dùng input". P-N6 gọi cách đó là R-B.
- **Đánh đổi giữa R-L và R-H:**
  - R-H dùng Bonferroni trên mọi cặp của bảng, tức mức α_H / (D(D − 1)/2) cho mỗi cặp. Việc thắt mức theo D nhằm kiểm soát đa kiểm định và hạn chế gộp nhầm khi bảng lớn lên. Cái giá là quyết định giữa hai biến đích có thể đổi khi thêm cột.
  - Số thiết kế (EXP2, mô tả): khi thêm 20 cột Gauss, Bonferroni tách thêm cạnh đích ở 1/20 hệ RFF, và ở 1/20 hệ tuyến tính nếu dùng HSIC.
  - R-L giữ mức cố định cho mỗi cặp. Quyết định giữa hai biến đích vì vậy không phụ thuộc số cột thêm vào, đổi lại số cặp chéo bị bác bỏ nhầm tăng theo số cặp đích–đệm.
  - P-N6 trình bày hai cách như một đánh đổi giữa giữ quyết định cục bộ và hạn chế gộp nhầm, không coi việc phụ thuộc D của Bonferroni là một lỗi.
- **Điều R-L giữ nguyên (sửa ở v1):**
  - Về mặt toán học, quyết định kiểm định cho từng cặp biến đích chỉ phụ thuộc hai cột của cặp đó, và khối đích trùng từng bit giữa các input. Vì vậy các quyết định này không phụ thuộc phần còn lại của bảng.
  - Về số học, p-value có thể lệch ở mức làm tròn khi D đổi, vì `p_hsic` tính mọi cặp bằng một phép nhân ma trận. User đo: 78 phần tử p-value của khối đích lệch, tối đa khoảng 1.78e−15. Agent tính lại với d_T = 20 và ra 78/380 phần tử, tối đa 1.67e−15; quyết định ở cả ba mức α_L vẫn giống hệt.
  - Phân hoạch liên thông trên toàn bảng thì **có thể đổi**: một đường đích 1 — đệm — đích 2 nối hai thành phần đích vốn tách biệt.
  - **Phát biểu đúng:** khi quyết định giữa các cặp đích được giữ nguyên, và không có thành phần nào trộn biến đích với biến đệm, R-L nhận cùng input trên từng thành phần đích, nên cho cùng output như R-L ở k0.
- **Rủi ro gộp nhầm (sửa ở v1):**
  - Nếu từng p-value hợp lệ, E[số cặp chéo bị bác bỏ nhầm] ≤ α_L · d_T · k.
  - Đây **không** phải số cột đệm bị gộp nhầm: một cạnh nối giả có thể kéo cả một thành phần đệm, khi đệm có cấu trúc, vào thành phần đích.
  - Với xấp xỉ gamma của HSIC hiện tại, chưa có cơ sở dùng bất đẳng thức này như bảo đảm thực nghiệm. Đuôi gamma dễ dãi: ở G9 của P-N2, tỉ lệ bác bỏ thực tế gấp 3–4 lần mức danh nghĩa 0.001.

## 2. Dữ liệu

- **Tổng hợp, held-out mới:**
  - seed base 480000, chưa dùng ở tập nào trước; DEV6 dùng base 490000;
  - 8 ô như HELD2: d_T ∈ {10, 20}, e_T ∈ {1, 2}, tuyến tính và RFF; đồ thị ER; n = 500. Khối đích sinh bằng `common.py` đã đóng băng của P-N1, seed 480000 + 1000·c + r, với r = 0, …, 14;
  - đệm và cách ghép như HELD2: `padding2` và `assemble2` đã đóng băng của P-N2, k = 20. A20 là e = 0 (Gauss, tức kiểu A); S20 là e = e_T (có cấu trúc, cùng họ cơ chế với khối đích);
  - 120 hệ (15 mỗi ô); input mỗi hệ: k0, A20 và S20.
- **Bảng thật,** chỉ cho phần độ đổi:
  - input k0 và đệm Gauss ở k = 20 và k = 40 của P-N5, sinh lại bằng `assemble5` đã đóng băng; mã băm phải khớp `checks/inputs5.json` của P-N5;
  - output plain của P-N5 đã được xem; chỉ output của R-L và R-H là mới.

## 3. Cách sửa: định nghĩa (khóa)

- **p-value:** hàm `p_hsic` đã đóng băng của P-N2, trên mọi cặp của bảng input.
- **R-L:** bác bỏ cặp (i, j) khi p_ij < α_L, không hiệu chỉnh theo bảng.
- **R-H:** bác bỏ khi p_ij < α_H / (D(D − 1)/2).
- **Thành phần:**
  - các thành phần liên thông của đồ thị các cặp bị bác bỏ (`screen.components` đã đóng băng);
  - mỗi thành phần có từ 2 biến trở lên và chứa ít nhất một biến đích được đưa vào model; cặp đích nằm ở hai thành phần khác nhau là không-cạnh. Điều kiện "chứa biến đích" chỉ chọn output cần đọc; quy trình sửa không cần biết khối đích (§10 đo cả chi phí chạy mọi thành phần);
  - biến đích tạo thành phần một mình thì không có cạnh nào.
- **Khóa thêm ở v1,** để phát biểu ở §1 có nghĩa từng bit:
  - **thứ tự cột** trong một thành phần: theo chỉ số cột tăng dần của bảng input, như `run2.py`. Biến đích luôn đứng trước biến đệm;
  - **input của thành phần** là các cột đó của bảng input, giữ nguyên, không chuẩn hóa lại;
  - **cấu hình inference** như P-N1 và P-N2: AVICI `scm-v0` với `expects_counts=False`; CDFM `from_pretrained(threshold=None)` và `predict(x, threshold=None, standardize=False)`; 2 luồng; chạy tuần tự;
  - **decoder riêng cho từng thành phần:** AVICI đọc ngưỡng 0.5; CDFM dùng ngưỡng NATIVE do chính nó chọn trên ma trận của thành phần đó.
- **Chọn α trên DEV6,** trước khi đóng băng và không dùng output model:
  - tiêu chí J = merged/k + split/|E_T| như P-N2, tính trên A20 và S20, trung bình qua cả hai họ, vì cách sửa không biết họ;
  - lưới: α_L ∈ {10⁻⁵, 10⁻⁴, 10⁻³}; α_H ∈ {0.001, 0.01, 0.05}; hòa thì chọn mức nhỏ hơn;
  - báo thêm số tách nhầm ở k0 cho mỗi mức.
- **Đối chứng decoder của CDFM,** tính từ output plain, không chạy thêm model:
  - FIXED: max(p_ij, p_ji) > 0.5;
  - FROZEN: p_ij > τ của plain ở k0;
  - ngưỡng cục bộ: bộ chọn ngưỡng của CDFM (bản chép lại đã đóng băng ở P-N4, `selector4.py`), áp lên ma trận xác suất của riêng khối đích (D = d_T).
- **R-oracle:** model trên riêng khối đích. Theo cấu trúc, nó trùng plain ở k0 từng bit; chỉ kiểm ở cổng G4, không chạy trên held-out.

## 4. Biến đo

Dữ liệu tổng hợp, cho mỗi hệ, cách sửa f và input c ∈ {A20, S20}:

- F1 skeleton của f(c) so với skeleton thật của khối đích (`metrics.f1` đã đóng băng của P-N1);
- **giá ở k0:** Q0_f = F1_f(k0) − F1_plain(k0);
- **mức so với mốc ban đầu:** Q_f(c) = F1_f(c) − F1_plain(k0);
- **lợi ích:** G_f(c) = F1_f(c) − F1_plain(c);
- **flips trung thành** φ_f(c): số cặp đích có trạng thái skeleton của f(c) khác plain ở k0. Đây là thước đo chung cho mọi cách sửa, vì mọi cách đều so với cùng một output ban đầu;
- **flips tự bất biến** σ_f(c): f(c) so với chính f ở k0;
- Δm so với plain ở k0;
- chỉ số sàng lọc:
  - số cột đệm nằm trong thành phần chứa biến đích (merged), số cạnh đích bị tách (split), số cặp chéo bị bác bỏ, số thành phần đích;
  - với R-L, quyết định giữa các cặp đích có trùng k0 không, và có thành phần nào trộn đích với đệm không.

Bảng thật: σ_f(c), φ_f(c) và φ_f(k0), tức độ lệch ở k0 nếu sàng lọc tách khối thật. Không có thước đo chất lượng.

## 5. Giả thuyết (khóa): sáu giả thuyết, Holm 0.05

| ID | Model, họ | Thành phần (contrast theo hệ) | Dự đoán | Phép kiểm |
|---|---|---|---|---|
| P6-1A-lin | AVICI, tuyến tính | Q0_R-L và Q_R-L(A20) | cả hai có trung bình > −0.03 | không kém quá biên, hợp hai phép một phía |
| P6-1A-rff | AVICI, RFF | như trên | như trên | như trên |
| P6-1C-lin | CDFM, tuyến tính | như trên | như trên | như trên |
| P6-1C-rff | CDFM, RFF | như trên | như trên | như trên |
| P6-2C-lin | CDFM, tuyến tính | φ_FROZEN(S20) − φ_R-L(S20) | > 0 | một phía |
| P6-2C-rff | CDFM, RFF | như trên | > 0 | một phía |

- **P6-1 (sửa ở v1: từ TOST sang không kém quá biên):**
  - Mục tiêu là giữ chất lượng khi sửa lỗi. TOST sẽ đánh trượt cả một cách sửa làm F1 tốt hơn 0.04, nên không hợp với câu hỏi này. Phép kiểm không kém quá biên (non-inferiority) hợp hơn; user dẫn phần giải thích của Lakens về hai loại phép kiểm này.
  - Mỗi giả thuyết model × họ đòi đồng thời E[Q0] > −0.03 và E[Q(A20)] > −0.03: không làm giảm F1 trung bình quá 0.03, ở k0 cũng như khi có 20 cột Gauss.
  - p của giả thuyết là p lớn hơn của hai phép kiểm một phía (intersection–union).
- **P6-2:**
  - Ở đệm có cấu trúc, nơi kênh ngưỡng quan trọng (C5), P6-2 hỏi R-L có giữ output ban đầu tốt hơn FROZEN không.
  - FROZEN dùng nhiều thông tin hơn, nhưng chỉ chặn kênh ngưỡng; điểm của khối đích vẫn đổi.
  - Cả hai được đo bằng flips trung thành, nên giá ở k0 của R-L bị tính vào. Phép so nghiêng về phía bất lợi cho R-L.
- **Phép kiểm:**
  - t phân tầng theo ô như HELD2: w_c = 1/4 trong một họ, SE² = Σ_c w_c² s_c² / n_c, df Welch–Satterthwaite;
  - với P6-1: t = (θ̂ + 0.03)/SE cho từng thành phần, p = `t.sf(t, df)`;
  - SE = 0 thì ghi DEGENERATE, dùng p = 1 và không xác nhận;
  - Holm ở mức familywise 0.05 trên đúng sáu p-value.
- **Cách đọc và giới hạn:**
  - P6-1 CONFIRMED được viết là "không kém mốc ban đầu quá biên đã chọn". Mức giữ nguyên cấu trúc phải đọc riêng qua φ và σ.
  - Đổi phép kiểm xuất phát từ mục tiêu nghiên cứu. Nó không giải quyết được vấn đề power thấp khi hiệu ứng thật nằm gần −0.03 (§10).
  - Không xác nhận được cũng chưa chứng minh cách sửa gây tổn thất vượt biên.
  - CONFIRMED ở P6-2 chỉ xác nhận dấu. CI và nhãn cỡ của từng giả thuyết là mô tả; Holm không bảo vệ chúng đồng thời.

## 6. Báo cáo mô tả (không thuộc bộ Holm)

- Mọi cách sửa × model × họ × input: Q0, Q, G, φ, σ và Δm.
  - Trung bình và CI theo t phân tầng.
  - Nhãn cỡ: biên 0.03 cho F1, 1.5 cạnh cho Δm, và 1.5 cặp cho φ và σ (làm rõ ở v1, cùng đơn vị với Δm).
- **R-L so với R-H:** σ và φ; tỉ lệ hệ có σ > 0 ở A20 và S20, kèm CI 95% Clopper–Pearson. Với R-L, tách σ theo có hay không có gộp nhầm.
- **Ngưỡng cục bộ và FIXED:** φ và σ.
- **Trường hợp xấu nhất:** |Δm| lớn nhất theo hệ, cho mỗi cách sửa.
- **Chi phí:** thời gian của pipeline chạy mọi thành phần (đo trên DEV6, §10) và thời gian chỉ tính output đích.
- **Bảng thật:**
  - σ và φ của R-L và R-H ở k = 20 và k = 40, và φ(k0);
  - tỉ lệ lần sinh có σ > 0, kèm CI 95% Clopper–Pearson;
  - so với plain chỉ để mô tả, vì output plain đã được xem ở P-N5.
- HELD2 (R-B) chỉ được nhắc như số tham khảo, không dùng để so trực tiếp.

## 7. Kiểm hoàn tất trước khi đọc

- mọi job có đúng một trạng thái kết thúc, không có `error`;
- mã băm input khớp input sinh lại; khối đích trùng từng bit giữa các input của mỗi hệ;
- với bảng thật, input khớp mã băm trong `checks/inputs5.json` của P-N5;
- cổng đóng băng `ok` ở đầu và cuối lượt, cùng commit;
- **quyết định của R-L giữa các cặp đích** ở A20 và S20 trùng chính xác với k0, ở mọi hệ held-out và mọi input bảng thật. Nếu lệch, báo lỗi, không đọc kết quả, và không nới ngưỡng sau khi xem kết quả;
- **phát biểu có điều kiện của R-L:** ở mọi input mà quyết định giữa các cặp đích được giữ nguyên và không thành phần nào trộn đích với đệm, output R-L trên khối đích trùng từng bit với R-L ở k0. Nếu sai, kết quả không được đọc và phải báo user, vì nó chỉ ra lỗi cài đặt.

## 8. Cổng (DEV6, base 490000, 2 hệ mỗi ô = 16 hệ)

| Cổng | Nội dung | Điều kiện đạt |
|---|---|---|
| G1 | Sinh input: khối đích như P-N1, đệm và cách ghép như P-N2, cùng seed thì trùng từng bit; input bảng thật khớp mã băm của P-N5 | trùng từng bit; khớp |
| G2 (sửa ở v1) | p-value của các cặp đích ở A20 và S20 so với k0; quyết định của R-L ở mọi mức α_L trong lưới | \|Δp\| ≤ 1e-12; quyết định trùng chính xác |
| G3 | Chọn α_L và α_H bằng J trên DEV6, không dùng output model; ghi lại trước khi đóng băng | có bản ghi |
| G4 (sửa ở v1) | Phát biểu có điều kiện của R-L: ở mọi input DEV6 thỏa điều kiện, input của từng thành phần đích và output trên khối đích trùng R-L ở k0 từng bit. Không yêu cầu phân hoạch toàn bảng giữ nguyên khi đã có gộp nhầm. R-oracle trùng plain ở k0 từng bit | trùng từng bit; có ít nhất một input thỏa điều kiện cho mỗi model |
| G5 | Bộ chọn ngưỡng chép lại tái lập ngưỡng NATIVE của CDFM trên output plain của DEV6; ngưỡng cục bộ ở k0 bằng NATIVE | ≤ 1e-12 |
| G6 | Code kiểm định: t phân tầng, phép không kém quá biên và p hợp, Holm, DEGENERATE, Clopper–Pearson, so với cài đặt tham chiếu | khớp; đúng kết quả định trước |
| G7 | Code đọc chạy hết trên DEV6, chỉ kiểm cấu trúc | không in hay ghi giá trị |
| G8 | Tất định: chạy lại k0 và một input có đệm cho mỗi model và mỗi biến thể R | trùng từng bit |
| G9 (sửa ở v1) | Thời gian và bộ nhớ trên DEV6: đo riêng pipeline chạy mọi thành phần và phần chỉ tính output đích; ước tính tổng cho lượt chính | ước tính ≤ 3 giờ; nếu vượt thì báo user |

## 9. Đọc kết quả

- **Câu được viết** (ví dụ): "Trên hệ tổng hợp mới, R-L không làm giảm F1 skeleton trung bình quá 0.03 so với output ban đầu, ở k0 cũng như khi có 20 cột Gauss, ở [ô]. Mức giữ nguyên cấu trúc: φ = …, σ = …"
- **Không được viết:**
  - "R-L tương đương mốc ban đầu", hay "R-L sửa được vấn đề" mà không kèm phạm vi;
  - "R-L bất biến ở mọi hệ";
  - rằng R-L áp dụng được cho biến có sẵn trong dữ liệu thật;
  - "R-L tốt hơn mọi cách sửa"; "FROZEN vô dụng";
  - rằng chênh lệch với R-B của HELD2 là do thông tin về họ cơ chế;
  - trên bảng thật: "R-L đúng hơn", hay bất kỳ câu nào về độ chính xác;
  - với một P6-1 không xác nhận: rằng R-L gây tổn thất vượt biên;
  - rằng CI hay nhãn cỡ được Holm bảo vệ.

## 10. Power và ngân sách

**Hồ sơ power** ([`design/pn6_power.py`](design/pn6_power.py), [`design/pn6_power.json`](design/pn6_power.json)):

- tính trực tiếp trên từng hệ của HELD2, với R-B làm số tham khảo; R-L có thể khác R-B, nên đây không phải bảo đảm;
- script tái lập đúng giá ở k0 mà HELD2 đã báo (AVICI −0.000 và +0.007; CDFM −0.018 và +0.000);
- power ước tính bằng bootstrap trong từng ô (15 hệ mỗi ô, 4 000 lần), áp đúng phép kiểm của §5.

| Giả thuyết | Mức Holm chặt nhất (0.05/6) | Mức 0.05 | Nếu kém R-B 0.01 |
|---|---|---|---|
| P6-1A-lin | 0.82 | 0.97 | 0.38 |
| P6-1A-rff | 1.00 | 1.00 | 1.00 |
| P6-1C-lin | **0.21** | 0.45 | 0.01 |
| P6-1C-rff | 0.99 | 1.00 | 0.81 |
| P6-2C-lin, P6-2C-rff | 1.00 | 1.00 | 1.00 (hiệu ứng giảm một nửa) |

- **P6-2:** số tham khảo từ HELD2. User tính, agent tính lại và ra cùng số:
  - φ của FROZEN và của R-B ở e_T là 19.90 và 6.85 (tuyến tính), 18.87 và 4.43 (RFF);
  - chênh lệch 13.05 [9.72, 16.38] và 14.43 [12.32, 16.54].
- **Lưu ý:** Δm gần 0 không suy ra ít cặp đổi trạng thái; R-B có Δm ở REP gần 0 nhưng φ khoảng 4–7.
- **P6-1C-lin** nhiều khả năng không được xác nhận nếu R-L có giá giống R-B. Kết quả đó không chứng minh tổn thất vượt biên.

**Ngân sách:**

- Runner R cũ chỉ chạy các thành phần chứa biến đích. Cách đó đủ để tính output cần đánh giá, nhưng chưa phải chi phí đầy đủ của một phương pháp không biết khối đích.
- Trên DEV6, G9 đo riêng:
  - pipeline chạy mọi thành phần có từ 2 biến (chi phí của phương pháp);
  - phần chỉ tính output đích, dùng cho lượt chính.
- Ước tính sơ bộ từ HELD2 (120 hệ, cùng ba input): plain khoảng 61 phút cho hai model; mỗi biến thể R khoảng 34 phút; bảng thật khoảng 20–30 phút. Tổng khoảng 2.5 giờ.
- Lượt chính chỉ chạy khi G1–G9 đạt và ước tính đo trên DEV6 không vượt 3 giờ. Trong lượt chạy, mốc 3 giờ được theo dõi như P-N5 (`budget_stop`).

## 11. Quy trình

1. User duyệt v0 với bốn chỉnh sửa (22/11). Khóa v1: commit và push trên nhánh công khai, gộp với `71de72f` và `c3dd77b`, trước khi sinh input P-N6.
2. Viết code dưới dạng file mới trong `artifacts/n6_runs/pn6/`. Import nguyên trạng `common.py`, `metrics.py`, `common2.py`, `screen.py`, `selector4.py` và `common5.py` đã đóng băng.
3. Chạy DEV6. Chọn α_L và α_H bằng J, không dùng output model. Chạy G1–G9. Đóng băng code, phụ thuộc và hai mức α; commit, push.
4. Chạy P-N6 nếu các cổng đạt và ước tính không vượt 3 giờ; user đã duyệt bước này. Lựa chọn R-L và cỡ 120 hệ giữ cố định trước held-out. Kiểm hoàn tất (§7), rồi đọc bằng code đã đóng băng.

## 12. Nhật ký (append-only sau khi khóa)

- **v0, 22/11/2026 (`c3dd77b`):** bản nháp.
- **v1, 22/11/2026 (khóa):** user duyệt các quyết định ở đầu file và cho GO sau bốn chỉnh sửa.
  1. **§5, P6-1:** đổi từ TOST sang phép kiểm không kém quá biên, với hai thành phần Q0 và Q(A20); p là p lớn hơn. Vẫn sáu giả thuyết trong Holm. Thêm cách đọc "không kém mốc ban đầu quá biên đã chọn".
  2. **§1, §7 và G4:**
     - sửa phát biểu bất biến của R-L thành phát biểu có điều kiện;
     - khóa thứ tự cột trong thành phần, cấu hình inference và decoder riêng cho từng thành phần;
     - sửa công thức rủi ro thành số cặp chéo bị bác bỏ nhầm, không phải số cột đệm bị gộp, và không coi nó là bảo đảm thực nghiệm với HSIC gamma;
     - trình bày R-L và R-H như một đánh đổi.
  3. **G2:** p-value so trong dung sai 1e−12; quyết định R-L trùng chính xác; input và output khi không gộp nhầm vẫn kiểm từng bit. Agent tính lại số của user bằng hàm đã đóng băng (d_T = 20: 78/380 phần tử lệch, tối đa 1.67e−15; d_T = 10: không lệch; quyết định giống hệt ở cả ba mức α_L).
  4. **§10:**
     - hồ sơ power tính trực tiếp trên từng hệ của HELD2, với phép kiểm mới;
     - số P6-2 của user được tính lại và khớp;
     - G9 đo riêng chi phí pipeline chạy mọi thành phần.
  - **Làm rõ, không đổi thiết kế:**
    - nhãn cỡ 1.5 cặp cho φ và σ (mô tả);
    - CI Clopper–Pearson cho tỉ lệ hệ có σ > 0 ở dữ liệu tổng hợp, như ở bảng thật;
    - R-B không chạy lại và chỉ là số tham khảo;
    - không thêm k = 40 ở dữ liệu tổng hợp.
  - **Ghi chú cho sau P-N6, không thuộc thiết kế này:** HSIC có thể kém Fisher-z ở quan hệ tuyến tính. Một phép kiểm từng cặp kết hợp Fisher-z và HSIC, mỗi phép ở α_L/2, vẫn chỉ dùng input và giữ quyết định cục bộ. Nếu P6-1 ở hệ tuyến tính không được xác nhận, đây là ứng viên cho bước sau.
  - **Mốc khóa:** `678f55f`, push lúc 2026-11-22T09:32:14Z (GitHub activity API), cùng `71de72f` và `c3dd77b`.
- **Đóng băng code, 22/11/2026,** trước khi sinh input held-out nào và trước khi chạy model nào trên hai bảng thật.
  - **Code mới** trong `artifacts/n6_runs/pn6/`: `common6.py`, `run6.py`, `measures6.py`, `stats6.py`, `alpha6.py`, `analyze6.py`, `completeness6.py`, `gates6.py`, `verify_freeze6.py`, `freeze6.py`, `run_dev6.sh`, `run_pn6.sh`.
  - **Snapshot** [`code/`](code/):
    - `SHA256SUMS` gồm 12 file code và 11 phụ thuộc. Các phụ thuộc là `common.py`, `metrics.py` và bốn file cấu hình của P-N1; `common2.py` và `screen.py` của P-N2; `common4.py` và `selector4.py` của P-N4; `common5.py` của P-N5. Mỗi phụ thuộc khớp mã băm trong snapshot gốc của nó.
    - `DEPS_SHA256.json` gồm: nguồn gói `cdfm` và `avici`; checkpoint của CDFM và AVICI; hai file dữ liệu; bốn output plain k0 của P-N5 dùng cho φ trên bảng thật; `alpha6.json`. Thêm mã băm của manifest dữ liệu và của `inputs5.json`, cùng phiên bản gói.
  - **Làm rõ cách cài đặt, không đổi luật:**
    - p-value HSIC tính một lần cho mỗi input và lưu lại; R-L, R-H và cả hai model dùng chung. Runner kiểm mã băm input trước khi dùng p-value đã lưu.
    - Thứ tự chạy: p-value; plain (AVICI, CDFM); R-L (AVICI, CDFM); R-H (AVICI, CDFM). Trong mỗi biến thể R, dữ liệu tổng hợp chạy trước, rồi tới bảng thật.
    - Mốc cho φ trên bảng thật là output plain k0 đã có của P-N5; mã băm của chúng được đóng băng.
  - **DEV6** (16 hệ, base 490000): 48 lần tính p-value và 250 job mỗi model (plain, R-L, R-H, pipeline chạy mọi thành phần, R-oracle, chạy lại); 0 lỗi. Không chạy model nào trên bảng thật. Output chỉ dùng cho cổng.
  - **Chọn α bằng J** (G3; không dùng output model; [`checks/alpha6.json`](checks/alpha6.json)):
    - R-L: J = 0.0705 ở 10⁻⁵, **0.0641 ở 10⁻⁴**, 0.1177 ở 10⁻³ (có gộp nhầm ở 6 input). Chọn **α_L = 10⁻⁴**.
    - R-H: J = 0.0853 ở 0.001, 0.0705 ở 0.01 và ở 0.05. Hòa, nên chọn mức nhỏ hơn: **α_H = 0.01**.
    - Mô tả từ cùng bảng: với R-L, số cạnh đích bị tách ở k0 bằng số đó khi có đệm, ở cả ba mức. Với R-H, có đệm thì bị tách nhiều hơn k0, ví dụ 1.63 so với 1.56 ở 0.01, và 1.63 so với 1.25 ở 0.05.
  - **Cả chín cổng đạt** ([`checks/gates6.json`](checks/gates6.json)):
    - G1: 48 input DEV6 sinh lại trùng từng bit, khối đích của input có đệm trùng k0; 82 input bảng thật khớp `inputs5.json` của P-N5.
    - G2: 1 184/7 520 phần tử p-value của khối đích lệch so với k0, tối đa 2.05e−15, trong dung sai 1e−12. Quyết định R-L trùng chính xác ở cả ba mức; `p_hsic` tính lại trùng từng bit.
    - G3: có bản ghi chọn α.
    - G4: phát biểu có điều kiện của R-L đúng từng bit ở cả 32 input có đệm thỏa điều kiện, cho mỗi model. R-oracle trùng plain ở k0 từng bit, ở 4 input × 2 model.
    - G5: bộ chọn ngưỡng chép lại tái lập ngưỡng NATIVE của CDFM, lệch tối đa 3.3e−16; ngưỡng cục bộ ở k0 bằng NATIVE.
    - G6: sáu ca kiểm của code thống kê đều đúng.
    - G7: code đọc chạy hết trên DEV6 (6 giả thuyết, 18 nhóm mô tả). Kiểm hoàn tất DEV6 đạt: 336 job; quyết định R-L trùng k0 ở 32/32 input; phát biểu có điều kiện đúng từng bit ở 64/64 trường hợp.
    - G8: chạy lại trùng từng bit (2 input × 3 biến thể × 2 model).
    - G9:
      - ước tính 2.6 giờ cho lượt chính (trung vị DEV6 × số job, × 1.10 + 300 s), dưới 3 giờ;
      - bộ nhớ đỉnh: AVICI 1.44 GB, CDFM 0.62 GB;
      - pipeline chạy mọi thành phần trên DEV6: các thành phần không chứa biến đích thêm 92 s vào 104 s thời gian model của R-L với AVICI, và 61 s vào 136 s với CDFM.
  - Theo trình tự user đã duyệt: các cổng đạt và ước tính không vượt 3 giờ, nên chạy P-N6 sau khi push commit đóng băng.
- **Làm rõ cách viết, 22/11/2026, sau lượt chính** (theo review của user; không đổi thiết kế, không dựa trên output): ở mục đóng băng, "trước khi chạy model nào trên hai bảng thật" và "Không chạy model nào trên bảng thật" nghĩa là chưa chạy R-L hay R-H của P-N6 trên hai bảng thật. Output plain trên hai bảng đã có từ P-N5 và là mốc của φ (§2). Kết quả: [PN6_results_vi.md](PN6_results_vi.md).
