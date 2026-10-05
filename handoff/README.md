# Handoff dự án Safety Prior cho khám phá nhân quả có biến ẩn

Tài liệu trong thư mục này là bản bàn giao nghiên cứu bám theo trạng thái hiện tại của repository. Nó nối liền đề cương khoa học, thiết kế kill test, bằng chứng K1, kiến trúc phần mềm, danh mục hướng tối ưu thuật toán, research contract, kế hoạch falsification và Sprint 0.

## Trạng thái ngắn gọn

- Luận điểm trung tâm: prior từ chuyên gia hoặc LLM chỉ được dùng để **phân bổ tính toán**; prior không được dùng như bằng chứng để xóa cạnh hoặc định hướng cạnh.
- Miền bài toán: causal discovery có biến ẩn, đầu ra PAG, với FCI/ICD và các biến thể làm nền tảng.
- K0: `PASS` — kiểm tra cơ học, tương đương full-budget và các invariant provenance.
- K1: `PASS` theo quyết định dự án hiện hành. Trên 131 graph có đủ năm scheduler, oracle đạt median saving 23.31% so với `stable_default`, bootstrap 95% CI xấp xỉ [20.24%, 27.70%], và cả bốn nhóm cấu hình đều vượt tiêu chuẩn nhóm.
- Giới hạn của kết luận K1: artifacts hiện có mới chứa 656/800 run; báo cáo tự động cũ chưa được tái sinh nên vẫn ghi `NOT_RUN`. Phần thiếu tập trung ở shard 5 và 7. Đây là nợ tái lập, không bị trình bày nhầm thành 800/800.
- K2, K3, K4: chưa chạy; không được diễn giải là đã pass.
- Hai hướng ưu tiên: **Blockwise ICD** và **Fallible-Tier Robust Envelope**.
- Sprint 0: đã khóa một phần semantics và dựng reference primitives; Blockwise ICD ở `REFERENCE_PARTIAL`, Fallible-Tier ở `CANDIDATE_SEMANTICS_FROZEN`.

## Thứ tự đọc khuyến nghị

1. [Tóm tắt điều hành](01_executive_summary.md)
2. [Đề cương và nền tảng khoa học](02_proposal_and_scientific_foundations.md)
3. [Kiến trúc repository và khả năng tái lập](03_repo_architecture_and_reproducibility.md)
4. [Kill test và kết luận K1 PASS](04_kill_test_and_k1_pass.md)
5. [Danh mục hướng tối ưu thuật toán](05_algorithm_optimization_portfolio.md)
6. [Research contract và falsification plan](06_research_contracts_and_falsification.md)
7. [Trạng thái Sprint 0](07_sprint0_status.md)
8. [Runbook và các bước tiếp theo](08_execution_runbook_and_next_steps.md)
9. [Rủi ro, ranh giới claim và quyết định](09_risks_claim_boundaries_and_decisions.md)
10. [Bản đồ nguồn và glossary](10_source_map_and_glossary.md)
11. [Khảo cứu đại số hóa FCI/ICD](11_formal_tensorization_fci_icd_survey_vi.md)
12. [Implementation plan cho Certified Blockwise ICD](12_certified_blockwise_icd_implementation_plan_vi.md)

## Quy ước trạng thái

Tài liệu phân biệt ba lớp trạng thái để tránh trộn lẫn quyết định khoa học và trạng thái vận hành:

| Lớp | Ý nghĩa |
|---|---|
| Project decision | Quyết định nghiên cứu đang được nhóm sử dụng để đi tiếp. Hiện tại K1 là `PASS`. |
| Evidence snapshot | Thống kê trực tiếp từ artifacts hiện có tại thời điểm bàn giao. |
| Generated report | Kết quả của reporter trong repo. Có thể cũ nếu chưa chạy lại analyzer sau khi thêm artifacts. |

Khi ba lớp chưa đồng bộ, tài liệu luôn ghi rõ cả ba thay vì chọn một con số thuận lợi.

## Phạm vi bàn giao

Bộ tài liệu này không thay thế các file nguồn. Các link trỏ tới proposal, config, code, test, report và artifact trong repository để người nhận có thể kiểm chứng. Nếu code hoặc artifacts thay đổi, cần tái sinh snapshot và cập nhật lại các bảng số liệu tại đây.
