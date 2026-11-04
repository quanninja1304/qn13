# Sprint C2 — Frozen stable epoch và Gate G2

**Trạng thái:** `PASS`

**Gate:** `G2_STABLE_EPOCH_SOUND = PASS`

**Phạm vi:** WP3/D5 trong `12_certified_blockwise_icd_implementation_plan_vi.md`.

## 1. Kết quả

Sprint C2 triển khai một epoch bất biến làm ranh giới giữa sinh candidate, thực thi CI và mutation của PAG. Scheduler được phép đổi thứ tự hoặc gom batch, nhưng không được thay đổi tập candidate đã khóa, canonical witness hay graph trong lúc epoch đang chạy.

Các deliverable chính:

1. digest độc lập cho PAG snapshot, epoch và candidate family;
2. canonical rank được gán trước khi scheduler can thiệp;
3. hai mode `exhaustive_epoch` và `canonical_frontier`;
4. canonical witnessed sepset thay cho first-completed hoặc union;
5. atomic commit tại epoch barrier;
6. weighted budget, checkpoint tuần tự hóa được và resume đúng epoch;
7. structured failure khi CI result là undefined;
8. accounting `speculative_work` cho query chạy quá canonical frontier;
9. audit CLI và exhaustive truth-table test cho Gate G2.

Equality target `completed_epoch_state` được đăng ký trong artifact schema 0.2.0 và reference contract. Gate evaluator từ chối audit thiếu công suất: kết quả cục bộ không mismatch vẫn là `FAIL` nếu không đủ đúng 64 truth tables và tối thiểu 256 audited schedules. Raw artifact ghi Git revision, config digest và dependency-lock digest.

## 2. Contract nhận dạng

Ba identity không bị trộn lẫn:

| Identity | Nội dung | Mục đích |
|---|---|---|
| `snapshot_digest` | nodes và endpoint marks của PAG đầu epoch | phát hiện graph drift |
| `epoch_id` | snapshot digest, radius, reference ID và contract version | định danh barrier logic |
| `candidate_family_digest` | toàn bộ canonical CI query sau deduplication | phát hiện candidate drift khi resume |

Hai candidate có cùng ngữ nghĩa `(x, y, S, phase)` được co thành một query; query ID nhỏ nhất theo từ điển được giữ. Cùng query ID nhưng khác ngữ nghĩa là lỗi contract.

Thứ tự canonical là:

```text
(x, y, |S|, S, phase, query_id)
```

`pair_order` và `canonical_rank` được ghi vào `CIQuery` sau khi candidate family đã canonicalize.

## 3. Semantics thực thi

### 3.1 Exhaustive epoch

`exhaustive_epoch` chạy mọi candidate trong frozen family. Đây là reference của G2. Các kết quả independent chỉ tạo provisional `SeparationWitness`; chúng chưa được phép xóa cạnh.

Khi barrier hoàn tất:

- một pair bị xóa khi tồn tại ít nhất một independent witness;
- sepset được chọn là witness có canonical rank nhỏ nhất;
- mỗi deletion sinh đúng một graph event trỏ tới đúng evidence query;
- mọi deletion được áp dụng lên bản sao snapshot, không mutate input.

### 3.2 Canonical frontier

`canonical_frontier` chỉ hủy phần suffix của một pair khi:

1. đã có independent witness;
2. mọi candidate có rank thấp hơn witness đó đã được giải quyết.

Query rank cao hoàn tất sớm vẫn được giữ làm provisional evidence nhưng không thể chiếm canonical sepset. Phần work đó được ghi vào `speculative_work`.

### 3.3 Scalar và batch

Executor gọi `test_many` khi backend hỗ trợ, nếu không sẽ gọi scalar `test`. Cả hai đường đi dùng cùng frozen candidate family và cùng finalizer. Test Gaussian CPU xác nhận decision, numerical status, deletion và selected witness giống nhau; các trường số thực nằm trong tolerance `1e-12`.

## 4. Budget, interruption và resume

Chi phí của query là `(2 + |S|)^3`. Khi query kế tiếp vượt weighted budget:

- epoch dừng ở checkpoint;
- không có deletion nào được coi là final;
- `commit_epoch` từ chối state chưa hoàn tất;
- frozen graph, provisional results và pending query được giữ trong `DiscoveryState`;
- resume chỉ được phép khi `epoch_id`, `candidate_family_digest` và execution mode khớp;
- checkpoint có thể round-trip qua JSON mà không đổi kết quả.

Budget trước witness tạo incomplete state không deletion. Với một pair đã giải quyết đủ canonical frontier, budget sau witness có thể hoàn tất epoch và hủy suffix an toàn.

## 5. Undefined CI và failure semantics

Nếu backend trả `independent=None`, executor ném `UndefinedCIResultError` với terminal status, query ID, numerical status, epoch ID, candidate-family digest và payload CI result. Không có đường commit graph từ kết quả undefined.

## 6. Bằng chứng Gate G2

Audit duyệt toàn bộ `2^6 = 64` bảng quyết định independent/dependent của sáu query thuộc hai pair. Với mỗi bảng, audit chạy bốn permutation scheduler, tổng cộng 256 lịch, đồng thời kiểm tra completion-order permutation, canonical frontier, checkpoint/resume, provenance và budget-zero state.

| Tiêu chí | Kết quả |
|---|---:|
| Truth tables | 64 |
| Scheduler permutations | 256 |
| Deletion mismatches | 0 |
| Selected witnessed-sepset mismatches | 0 |
| Completion-order mismatches | 0 |
| Canonical-frontier mismatches | 0 |
| Replay/resume mismatches | 0 |
| Provenance mismatches | 0 |
| Budget-state mismatches | 0 |

Regression suite:

| Suite | Kết quả |
|---|---:|
| C2 targeted | 30 passed |
| Default, không optional reference | 118 passed, 15 skipped |
| Có exact official ICD source snapshot | 133 passed |

Raw audit nằm tại `artifacts/tensorized_icd/c2_stable_epoch_audit.json`; snapshot gate được lưu tại `reports/algorithm_sprints/g2_stable_epoch_sound.json`.

## 7. Các regression cụ thể

Test suite khóa các failure mode sau:

- mọi scheduler permutation cho cùng deletion và canonical witness;
- completion order không đổi evidence;
- scalar/batch epoch equality;
- interruption/resume bằng uninterrupted execution;
- candidate-family digest drift bị từ chối;
- duplicate semantic query bị co, conflicting query ID bị từ chối;
- budget trước/sau witness;
- undefined CI fail mà không commit;
- snapshot không mutation trước barrier;
- collider-opening union regression từ C0 vẫn pass trong full suite.

## 8. Ranh giới claim

Gate G2 chứng minh contract nội bộ của **một frozen candidate family** trên testbed hữu hạn: schedule invariance, canonical evidence, barrier atomicity và replay/resume equality.

Gate này chưa chứng minh:

- frozen epoch tương đương official dynamic ICD;
- candidate generator đầy đủ hoặc đúng cho mọi PAG;
- block decomposition sound;
- concurrent executor confluent giữa các block;
- final PAG equality trên benchmark rộng;
- giảm runtime hay speedup CPU/GPU.

Các claim đó thuộc Sprint C3/G3 trở đi. Bước kế tiếp đúng theo plan là certified ICD round: nối frozen epoch vào official orientation wrapper, tạo radius certificate, rồi so exhaustive round và final PAG với dynamic reference.
