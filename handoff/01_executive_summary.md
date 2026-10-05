# 1. Tóm tắt điều hành

## Bài toán

Khám phá cấu trúc nhân quả khi có biến ẩn đòi hỏi nhiều phép kiểm định độc lập có điều kiện (CI test), đặc biệt ở các vòng Possible-D-SEP của FCI/ICD. Chi phí này tăng nhanh theo số biến, kích thước conditioning set và độ phức tạp của vùng đồ thị phải tìm kiếm. Trong khi đó, kiến thức ngoài dữ liệu — từ chuyên gia, metadata hoặc LLM — có thể chỉ đúng một phần, có tương quan lỗi và đôi khi sai theo cả một motif.

Dự án đặt câu hỏi: có thể dùng prior không hoàn hảo để giảm thời gian hoặc số CI test mà vẫn giữ ranh giới an toàn và ý nghĩa thống kê của causal discovery hay không?

## Luận điểm cốt lõi

Giải pháp không coi LLM là causal oracle. Dự án tách hai vai trò:

1. **Evidence plane:** chỉ dữ liệu, CI result và các luật định hướng hợp lệ được phép thay đổi graph.
2. **Control plane:** prior được phép sắp thứ tự truy vấn, phân bổ budget, chọn block/vùng cần ưu tiên, hoặc quyết định khi nào mở rộng phạm vi tìm kiếm.

Sự tách biệt này tạo ra một nguyên tắc an toàn có thể kiểm thử: khi budget đầy đủ và thuật toán không bỏ qua truy vấn hợp lệ, output phải tương đương baseline không dùng prior. Khi dừng sớm, output phải được gọi là trạng thái khám phá chưa hoàn tất, không được đánh tráo thành PAG hoàn chỉnh.

## Kết quả kill test

Kill test được thiết kế để giết sớm giả thuyết nếu ngay cả oracle scheduler — biết truy vấn nào hữu ích — cũng không tạo ra headroom tính toán đáng kể.

Kết luận đang được dự án sử dụng là:

> **K1 PASS:** tồn tại headroom đủ lớn để tiếp tục nghiên cứu thuật toán phân bổ truy vấn.

Snapshot artifacts hiện tại cho thấy:

| Chỉ báo | Giá trị |
|---|---:|
| Ma trận dự kiến | 800 run = 160 graph × 5 scheduler |
| Run row đã có | 656/800 (82.0%) |
| Graph có đủ năm scheduler | 131/160 |
| Failure artifact | 0 |
| Median tests-to-95 của oracle | 411 |
| Median tests-to-95 của stable default | 607 |
| Median saving oracle so với stable default | 23.31% |
| Bootstrap 95% CI | khoảng [20.24%, 27.70%] |
| Nhóm cấu hình vượt tiêu chuẩn nhóm | 4/4 |

Ngưỡng đăng ký là median saving ít nhất 20%, cận dưới bootstrap 95% lớn hơn 10%, và hiệu ứng xuất hiện trong ít nhất ba nhóm cấu hình. Phần dữ liệu ghép cặp hoàn thành vượt cả ba điều kiện.

Tuy nhiên, file report tự động hiện có được sinh trước khi matrix hoàn tất nên vẫn đánh dấu K1 `NOT_RUN`. Vì vậy `PASS` ở đây là quyết định khoa học dựa trên snapshot hoàn thành, chưa phải xác nhận rằng 800/800 run đã đóng và reporter đã được tái sinh. Cần hoàn thành 144 run còn thiếu rồi chạy analyzer để tạo bản ghi chính thức cuối cùng.

## Ý nghĩa của K1

K1 không chứng minh một thuật toán mới đã thành công. Nó chỉ xác nhận rằng thứ tự/phân bổ truy vấn là một đòn bẩy có tiềm năng. Phạm vi can thiệp trong implementation K1 hiện tại còn hẹp: scheduler thực sự điều khiển pha stable FAS skeleton; Possible-D-SEP được ghi log nhưng chưa được reorder. Do đó K1 hợp thức hóa đầu tư vào thiết kế thuật toán, không hợp thức hóa claim về toàn bộ FCI.

## Hướng nghiên cứu ưu tiên

### Blockwise ICD

Mục tiêu là khai thác tính cục bộ hoặc khả năng giao hoán của các cập nhật bằng chứng để xử lý nhiều block độc lập hay gần độc lập, nhưng vẫn khớp với ICD chuẩn khi chạy đến hội tụ. Novelty chỉ đứng vững nếu chứng minh được điều kiện phân rã, confluence/equivalence và giảm được công việc thực, chứ không chỉ chạy cùng thuật toán bằng nhiều thread.

### Fallible-Tier Robust Envelope

Mục tiêu là dùng tier knowledge có thể sai để tạo một envelope bảo thủ cho tập conditioning candidate. Thuật toán phải bao phủ baseline hợp lệ dưới mô hình sai lệch đã công bố, tự suy biến về baseline khi bất định lớn, và chỉ thu hẹp tìm kiếm khi prior thực sự cung cấp thông tin. Novelty nằm ở robust set construction và định lý exactness/coverage, không nằm ở việc áp một hard tier constraint.

## Vai trò của GPU

GPU là hướng tối ưu implementation thứ cấp, không phải đóng góp khoa học tự thân. Nó phù hợp với simulation hàng loạt, linear algebra cho CI test, residual/covariance theo batch và scoring nhiều candidate. Graph traversal động, Possible-D-SEP và logic định hướng thường khó tăng tốc hiệu quả bằng GPU. Quy tắc là: trước tiên chứng minh thuật toán giảm số phép tính hoặc có guarantee mới; sau đó dùng GPU để giảm wall-clock của phần kernel phù hợp.

## Trạng thái hiện tại và quyết định tiếp theo

- Giả thuyết tổng thể còn sống vì K1 pass.
- Không cần coi K2/K3 là điều kiện để bắt đầu Sprint thuật toán; chúng sẽ trở thành testbed cho độ bền của candidate sau khi semantics ổn định.
- Sprint 0 đã dựng reference primitives, motif catalog, equality tooling và official ICD adapter tùy chọn.
- Bước quyết định kế tiếp là hoàn tất reference-equivalence checks, sau đó xây prototype nhỏ nhất cho từng hướng ưu tiên và cố tình tìm counterexample trước khi scale benchmark.

## Deliverable khoa học kỳ vọng

Một kết quả đủ mạnh không nên chỉ là “LLM giúp chạy nhanh hơn”. Gói đóng góp mục tiêu gồm:

1. Một abstraction rõ ràng tách evidence khỏi compute allocation.
2. Một thuật toán có semantics chính xác trong bối cảnh latent-variable discovery.
3. Ít nhất một định lý hoặc mệnh đề về soundness/equivalence/coverage/degeneration.
4. Counterexample suite cho biết guarantee hỏng ở đâu.
5. Đánh giá query count, wall-clock, memory và chất lượng PAG dưới prior đúng, sai độc lập và sai tương quan.
6. LLM chỉ là một prior generator được calibration, so sánh với prior tổng hợp và heuristic rẻ.
