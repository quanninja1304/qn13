# N1: cập nhật prior art trước khi viết (21/11/2026)

> **Phạm vi:** lặp lại tìm kiếm "khớp chính xác" như sổ claim yêu cầu ("Lặp lại tìm kiếm ngay trước khi viết bài"), cộng các nguồn mới sau lượt 20/11.
> **Mức đọc:** [V-search], gồm abstract, trang HTML và một phần nội dung qua agent đọc trang. Phần giữa của một số bài chỉ có tóm tắt.
> **Không phải systematic review.**

## 1. Kết quả tìm khớp chính xác

Ba truy vấn mở rộng về mô hình causal discovery học sẵn kèm thêm biến độc lập, tính nhất quán khi thêm hoặc bỏ biến, và hiệu chỉnh ngưỡng. Kết quả: **không thấy** nguồn nào kiểm việc giữ nguyên một khối đích rồi thêm khối biến độc lập vào input của mô hình causal discovery học sẵn. Kết luận "chưa có bài làm đúng điều này" vẫn chỉ ở mức **suy luận, trong phạm vi đã tìm**.

## 2. Nguồn mới hoặc mới kiểm

| Nguồn | Trạng thái | Liên quan | Mức đọc |
|---|---|---|---|
| Zhu & Zhu, "Amortized Nonlinear Variable Selection with Prior-Data Fitted Networks" (MambaPFN); [arXiv 2611.04848](https://arxiv.org/abs/2611.04848), 3/11/2026 | Preprint | Chọn biến (Markov blanket của biến đáp ứng) bằng PFN học sẵn. Không phải học đồ thị. Không có thí nghiệm thêm cột thừa; chỉ quét số chiều. Có thể là một **baseline cách sửa** cùng họ với nhánh R (chọn biến trước khi học cấu trúc) | V-search |
| Vowels, Rochat, Akbari, "CaTs and DAGs: Integrating Directed Acyclic Graphs with Transformers for Causally Constrained Predictions"; [arXiv 2410.14485](https://arxiv.org/abs/2410.14485) (v5, 1/2026) | Trang arXiv không ghi venue; claim "ICLR 2026" từ kết quả tìm kiếm **chưa kiểm được** | Dự đoán dưới DAG cho trước, với attention bị mask theo DAG. Đây là cách sửa theo thiết kế ở bài toán dự đoán, không phải học cấu trúc | V-search |
| Li, Liu, Wang, Ye, "TabCausal: Pretraining Across Causal Environments for Tabular Causal Discovery"; [arXiv 2605.31156](https://arxiv.org/abs/2605.31156) (v2, 8/2026) | Preprint | Một model causal discovery học sẵn khác. Theo phần đã đọc, không có phép thử thêm biến; chỉ có scaling theo số biến. Cùng nhóm tác giả với CausalArena | V-search (phần giữa chỉ có tóm tắt) |
| Montagna, Cairney-Leeming, Sridhar, Locatello, "Demystifying amortized causal discovery with transformers"; [arXiv 2405.16924](https://arxiv.org/abs/2405.16924) | **TMLR 2025** (journal-ref trên arXiv) | Phân phối huấn luyện ngầm định một prior trên mô hình nhân quả của dữ liệu kiểm thử. Khung này hợp để diễn giải N1 như một hệ quả của prior huấn luyện, nhưng bài không bàn thêm biến | V-search |
| "Transformer Is Inherently a Causal Learner"; [arXiv 2601.05647](https://arxiv.org/abs/2601.05647) | Preprint | Bền vững với nhiễu và biến ẩn; không thấy phép thử thêm biến | V-search (snippet) |
| Mask2Cause; [arXiv 2605.07280](https://arxiv.org/abs/2605.07280) | Preprint | Nhị phân hóa điểm theo mật độ hoặc bằng phân cụm 1D (chuỗi thời gian). Liên quan tới chính sách chọn ngưỡng | V-search (snippet) |
| Jabbari et al., "Obtaining Accurate Probabilistic Causal Inference by Post-Processing Calibration"; [arXiv 1712.08626](https://arxiv.org/abs/1712.08626) | Preprint 2017 | Hiệu chỉnh xác suất cạnh bằng một tập hiệu chỉnh | V-search |

## 3. Hệ quả cho bản thảo

- **Vị trí đóng góp không đổi:**
  - Nguyên lý nhất quán khi đổi tập biến đã có (Self-Compatibility, AISTATS 2024).
  - Hiện tượng gần ở bài toán dự đoán đã có: Grinsztajn 2022; TabPFN 2023 §B.3.2; Noise Immunity 2026, bài này cho thấy ROC-AUC không giảm.
  - Tiền lệ cổ điển: Aliferis 2010.
  - Đóng góp nằm ở: failure cụ thể với đáp án biết trước; đường ảnh hưởng đã cô lập ở CDFM (bộ chọn ngưỡng, tới mức khối); các kênh đã đo ở AVICI; phạm vi hiệu quả của cách sửa.
- **Related work cần thêm:** MambaPFN (cách sửa bằng chọn biến); CaTs (mask theo DAG ở bài toán dự đoán); Montagna et al. (khung prior huấn luyện); TabCausal (model có thể đưa vào phép thử).
- **Trước khi gửi:** lặp lại lượt tìm này, vì preprint ra liên tục; bài MambaPFN chỉ mới ra ngày 3/11/2026.
