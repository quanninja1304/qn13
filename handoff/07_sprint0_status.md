# 7. Trạng thái Sprint 0

## 7.1 Mục tiêu Sprint 0

Sprint 0 không nhằm chứng minh speedup. Mục tiêu là khóa semantics đủ chắc để hai hướng thuật toán không xây trên một reference mơ hồ.

Nguồn trạng thái: [Sprint 0 reference semantics](../docs/research/sprint0_reference_semantics_vi.md). Commit khởi tạo được ghi nhận trong lịch sử repo là `1185b05` (`research: start sprint 0 reference semantics`).

## 7.2 Những gì đã có

### Official ICD adapter

Adapter tùy chọn trỏ tới Intel causality-lab revision:

```text
36625da6eeef059e36dab2b4467235a036136b76
```

Dependency này không nên âm thầm trôi version. Environment không cài extra reference vẫn phải chạy được test core; reference audit được đánh dấu optional/skip rõ ràng.

### ICD reference primitives

Repo có implementation độc lập ban đầu cho:

- ICD-Sep/PDS path construction;
- possible-ancestor filtering;
- dynamic và precomputed candidate behavior để đối chiếu.

Đây là reference work, chưa phải Blockwise ICD hoàn chỉnh.

### Tier semantics

Repo có:

- `TierOrdering`;
- restriction đơn giản kiểu tFCI cho adjacency/PDS;
- brute-force robust envelope dùng làm semantic oracle trên case nhỏ.

Brute-force là tiêu chuẩn kiểm chứng, không phải implementation scale cuối.

### Test infrastructure

- canonical equality helper;
- motif catalog;
- artifact schema;
- audit CLI;
- regression seed cho khác biệt query trace.

## 7.3 Audit 40 graph nhỏ

| So sánh | Kết quả |
|---|---:|
| Official dynamic ICD vs upstream FCI final PAG mismatch | 0/40 |
| Dynamic vs precomputed final output mismatch | 0/40 |
| Dynamic vs precomputed query-trace mismatch | 10/40 |

Regression seed đáng chú ý:

- seed `74304`;
- 4 observed, 2 latent;
- dynamic: 21 CI queries;
- precomputed: 25 CI queries;
- ở round 2: 5 so với 9 queries;
- final PAG giống nhau.

Kết quả này quan trọng vì nó cho thấy final-output equality không kéo theo query-trace equality. Nó cũng gợi ý candidate recomputation/dynamic invalidation là đối tượng thuật toán thật, nhưng chưa chứng minh block decomposition.

## 7.4 Trạng thái hai hướng

| Hướng | Trạng thái | Diễn giải |
|---|---|---|
| Blockwise ICD | `REFERENCE_PARTIAL` | Có primitives/audit, chưa có exhaustive equivalence và block algorithm |
| Fallible-Tier Envelope | `CANDIDATE_SEMANTICS_FROZEN` | Có semantics ứng viên và brute-force oracle, chưa có theorem/efficient algorithm |

Sprint 0 chưa nên được gọi là `PASS` toàn bộ.

## 7.5 Việc cần hoàn tất để đóng Sprint 0

### Blockwise track

1. Mở rộng exhaustive dynamic-vs-precomputed comparison.
2. Khóa canonical equality đối với circle/tail/arrowhead.
3. Xác định khi query-trace difference là hợp lệ.
4. Xây dependency/event model tối thiểu.
5. Kiểm tra official ICD wrapper trên environment sạch.
6. Lưu minimal counterexample cho mọi mismatch.

### Tier track

1. Hoàn thiện simple-tFCI wrapper đủ để so oracle/full-budget.
2. Kiểm hard-tier restriction trên motifs có latent.
3. Chứng minh hoặc bác bỏ separator coverage condition.
4. Thêm group/source corruption model.
5. So efficient candidate với brute-force envelope trên case nhỏ.
6. Đo collapse/shrinkage trước khi scale.

## 7.6 Definition of done

Sprint 0 chỉ đóng khi:

- reference revision và dependency tái lập được;
- canonical equality được test;
- small-graph audit không có unexplained mismatch;
- mỗi hướng có schema input/output và failure artifact;
- counterexample suite được version-control;
- assumption và scope được ghi rõ;
- có command một bước để tái chạy audit;
- không có claim speedup dựa trên reference chưa ổn định.

## 7.7 Nợ kỹ thuật không được che lấp

- official dependency là optional, nên CI mặc định có thể không kiểm toàn bộ reference path;
- 40 graph chỉ là smoke-scale;
- output equality hiện chưa thay thế proof;
- tier semantics đang là candidate, không phải định nghĩa cuối đã được literature-positioned;
- query count difference cần giải thích bằng eligibility/dependency, không chỉ ghi nhận;
- chưa có benchmark memory/runtime đủ lớn.
