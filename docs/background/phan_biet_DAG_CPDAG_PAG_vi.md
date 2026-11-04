# Phân biệt DAG, CPDAG và PAG — Tại sao FCI sử dụng PAG?

## 1. Bảng so sánh DAG, CPDAG và PAG

| Tiêu chí | DAG | CPDAG | PAG |
| --- | --- | --- | --- |
| Tên đầy đủ | Directed Acyclic Graph | Completed Partially Directed Acyclic Graph | Partial Ancestral Graph |
| Bản chất | Một đồ thị nhân quả cụ thể | Đại diện cho một lớp DAG tương đương Markov | Đại diện cho một lớp MAG tương đương Markov |
| Loại cạnh | `A → B` | `A → B`, `A — B` | `A → B`, `A ↔ B`, `A o→ B`, `A o—o B`, ... |
| Biến nhiễu ẩn | Có thể tồn tại trong DAG đầy đủ | Giả định không có nhiễu ẩn giữa các biến được xét | Cho phép nhiễu ẩn |
| Selection bias | Không mặc định xử lý | Không mặc định xử lý | Có thể biểu diễn tác động của selection bias |
| Hướng cạnh | Xác định hoàn toàn | Xác định một phần | Xác định một phần, kể cả dấu đầu mút |
| Ý nghĩa | Một cấu trúc nhân quả cụ thể | Thông tin chung cho mọi DAG trong lớp tương đương | Thông tin tổ tiên và phi tổ tiên chung cho các MAG trong lớp tương đương |
| Thuật toán liên quan | Có thể là đầu ra của phương pháp có giả định bổ sung | PC, PC-Stable | FCI, RFCI, ICD |
| Độ chắc chắn về cấu trúc | Cụ thể nhất về hướng cạnh | Có thể còn cạnh chưa định hướng | Có thể còn đầu mút chưa xác định |

**Điểm quan trọng:**

- DAG biểu diễn một cấu trúc nhân quả cụ thể.
- CPDAG đại diện cho một tập DAG tương đương Markov.
- PAG đại diện cho một tập MAG (Maximal Ancestral Graph) tương đương Markov.

PAG không đơn giản là CPDAG có thêm cạnh hai chiều. Hai đồ thị này biểu diễn hai loại Markov equivalence class khác nhau.

---

## 2. Ý nghĩa các loại cạnh

### 2.1. DAG

DAG (Directed Acyclic Graph) chỉ chứa cạnh có hướng và không có chu trình có hướng.

Ví dụ:

    A → B → C
    A ─────→ C

Ý nghĩa:

- A là nguyên nhân trực tiếp của B.
- B là nguyên nhân trực tiếp của C.
- A cũng là nguyên nhân trực tiếp của C.

DAG xác định một cấu trúc nhân quả cụ thể.

### 2.2. CPDAG

CPDAG (Completed Partially Directed Acyclic Graph) chứa:

| Cạnh | Ý nghĩa |
| --- | --- |
| `A → B` | Hướng A → B xuất hiện trong mọi DAG thuộc lớp tương đương |
| `A — B` | Hướng cạnh chưa thể xác định duy nhất |

Ví dụ:

    A — B → C

Trong đó:

- B → C đã được xác định.
- A — B chưa thể xác định hướng dựa trên thông tin hiện có.

**Lưu ý:** Một CPDAG hợp lệ phải biểu diễn đúng các hướng cạnh bất biến trong toàn bộ lớp DAG tương đương Markov.

### 2.3. PAG

PAG (Partial Ancestral Graph) cho phép nhiều loại đầu mút hơn.

| Ký hiệu | Ý nghĩa |
| --- | --- |
| `A → B` | A là tổ tiên của B; B không là tổ tiên của A |
| `A ↔ B` | A không là tổ tiên của B và B không là tổ tiên của A |
| `A o→ B` | B không là tổ tiên của A; chưa rõ A có là tổ tiên của B hay không |
| `A o—o B` | Cả hai đầu mút đều chưa được xác định |
| `A — B` | Hai đầu mút là tail; có ý nghĩa đặc biệt trong trường hợp selection bias |
| `A ←o B` | A không là tổ tiên của B; chưa rõ B có là tổ tiên của A hay không |

Trong PAG:

- Tail (`—`) tại A biểu thị A là tổ tiên của B.
- Arrowhead (`>`) tại A biểu thị A không là tổ tiên của B.
- Circle (`o`) tại A biểu thị quan hệ tổ tiên ở đầu mút đó chưa được xác định.

Các ý nghĩa trên áp dụng cho những dấu đầu mút bất biến trong lớp MAG tương đương.

**Quan trọng:** Quan hệ tổ tiên không nhất thiết là quan hệ nhân quả trực tiếp.

Ví dụ:

    A → M → B

A là tổ tiên của B, nhưng A không trực tiếp gây ra B.

---

## 3. Tại sao FCI sử dụng PAG thay vì CPDAG?

### 3.1. Vấn đề cốt lõi: Latent confounding

Giả sử có ba biến:

- X: Lượng cà phê tiêu thụ.
- Y: Chất lượng giấc ngủ.
- L: Mức độ căng thẳng, không được quan sát.

Cấu trúc nhân quả thực tế:

        L
       / \
      v   v
      X   Y

Tương đương:

    X ← L → Y

Trong đó L là biến nhiễu ẩn (latent confounder).

Khi chỉ quan sát X và Y, chúng ta có thể phát hiện:

    X không độc lập thống kê với Y

Ký hiệu:

    X ⫫̸ Y

Tuy nhiên, sự phụ thuộc thống kê không chứng minh rằng:

    X → Y

Bởi vì có ít nhất ba khả năng:

    (1) X → Y

    (2) X ← Y

    (3) X ← L → Y

Do đó, nếu chỉ có hai biến và không có thêm thông tin, FCI không thể xác định quan hệ nhân quả chính xác.

Kết quả PAG thích hợp thường là:

    X o—o Y

Điều này có nghĩa cả hai đầu mút đều chưa được xác định.

**Lưu ý:** Không thể tự động kết luận `X ↔ Y` chỉ vì nghi ngờ tồn tại biến nhiễu ẩn.

Cạnh `X ↔ Y` chỉ được xác định khi có đủ thông tin để loại trừ quan hệ tổ tiên theo cả hai hướng.

### 3.2. Vì sao CPDAG không đủ?

CPDAG biểu diễn một lớp tương đương Markov của các DAG trên tập biến đang xét.

Điều này phù hợp với giả định causal sufficiency:

> Không tồn tại nguyên nhân chung chưa quan sát của các biến được xét.

Nhưng khi có biến nhiễu ẩn, cấu trúc nhân quả trên riêng các biến quan sát có thể không còn biểu diễn đầy đủ bằng DAG thông thường.

Do đó, FCI sử dụng MAG và PAG.

Quá trình biểu diễn:

    DAG đầy đủ
    (Observed + Latent + Selection)
            |
            v
           MAG
    (Maximal Ancestral Graph)
            |
            v
           PAG
    (Partial Ancestral Graph)

Trong đó:

1. DAG đầy đủ biểu diễn hệ thống nhân quả thực tế, bao gồm cả biến quan sát và biến ẩn.
2. MAG biểu diễn cấu trúc trên các biến quan sát, bảo toàn các quan hệ độc lập có điều kiện thích hợp.
3. PAG đại diện cho lớp MAG tương đương Markov, thể hiện những thông tin định hướng bất biến.

MAG có thể chứa:

- Directed edges (`→`)
- Bidirected edges (`↔`)
- Undirected edges (`—`)

PAG bổ sung circle endpoints (`o`) để thể hiện sự không chắc chắn về quan hệ tổ tiên.

---

## 4. So sánh pipeline PC và FCI

| Giai đoạn | PC | FCI |
| --- | --- | --- |
| Input | Dữ liệu quan sát | Dữ liệu quan sát |
| Skeleton discovery | CI tests trên tập láng giềng | CI tests trên tập láng giềng, sau đó kiểm tra bổ sung |
| Separating sets | Chủ yếu tìm trong adjacency sets | Bổ sung Possible-D-SEP |
| Collider orientation | Xác định v-structures | Xác định colliders, kể cả cấu trúc phức tạp do biến ẩn |
| Orientation | Meek rules | Quy tắc định hướng PAG, thường là R0–R10 trong phiên bản đầy đủ |
| Output | CPDAG | PAG |
| Giả định then chốt | Causal sufficiency | Cho phép latent confounding |

### 4.1. PC hoạt động như thế nào?

Pipeline đơn giản:

    Observational Data
            |
            v
    Conditional Independence Tests
            |
            v
    Skeleton Discovery
            |
            v
    Collider Orientation
            |
            v
    Meek Orientation Rules
            |
            v
           CPDAG

PC dựa trên giả định causal sufficiency, Markov và faithfulness.

### 4.2. FCI hoạt động như thế nào?

Pipeline khái quát:

    Observational Data
            |
            v
    Initial Skeleton Discovery
            |
            v
    Initial Collider Orientation
            |
            v
    Possible-D-SEP Search
            |
            v
    Additional Edge Removal
            |
            v
    Collider Reorientation
            |
            v
    PAG Orientation Rules
          R1–R10
            |
            v
           PAG

FCI cần bước Possible-D-SEP vì khi có biến ẩn, tập phân tách hợp lệ có thể không nằm trong tập láng giềng hiện tại.

Điều này khiến FCI phức tạp và tốn tài nguyên tính toán hơn PC.

---

## 5. Ý nghĩa của Markov Equivalence Class

Giả sử tồn tại nhiều MAG:

    M1, M2, M3, ..., Mk

Các MAG này có cùng những quan hệ độc lập có điều kiện trên các biến quan sát:

    I(M1) = I(M2) = ... = I(Mk)

Trong đó I(M) là tập các quan hệ độc lập có điều kiện do đồ thị M hàm ý.

Do đó, chỉ từ các quan hệ độc lập có điều kiện, FCI không thể phân biệt chính xác MAG nào là cấu trúc thực tế.

Thay vì chọn tùy tiện một MAG, FCI trả về PAG đại diện cho cả lớp tương đương:

    {M1, M2, ..., Mk}
             |
             v
            PAG

PAG giữ lại những đặc điểm bất biến của toàn bộ lớp MAG tương đương.

Ví dụ:

Nếu trong mọi MAG thuộc lớp tương đương, A không phải là tổ tiên của B, thì PAG có thể xác định arrowhead tại A.

Nếu quan hệ tổ tiên thay đổi giữa các MAG, PAG phải giữ circle tại đầu mút tương ứng.

---

## 6. Ý nghĩa đối với tối ưu hóa FCI/ICD trên GPU

Đối với nghiên cứu tối ưu hóa các thuật toán khám phá nhân quả khi có latent confounding, cần phân biệt hai thành phần:

### 6.1. Conditional Independence Testing (CIT)

Mục tiêu:

- Giảm các phép kiểm định CI trùng lặp.
- Tái sử dụng những đại lượng thống kê đã tính toán.
- Vector hóa và ma trận hóa các phép tính.
- Thực hiện song song trên GPU.
- Giảm chi phí tìm kiếm tập phân tách.

Điều kiện quan trọng:

> Các tối ưu hóa không được làm thay đổi kết quả CI cần thiết cho tính đúng đắn của thuật toán.

Trong thực tế, cần tính đến sai số số học và các trường hợp kết quả kiểm định nằm gần ngưỡng quyết định.

### 6.2. Orientation Rules

Mục tiêu:

- Giảm chi phí xác định các cấu trúc cần định hướng.
- Tránh kiểm tra lặp lại những cấu hình đồ thị giống nhau.
- Song song hóa các thao tác định hướng độc lập khi an toàn.
- Tối ưu việc áp dụng các quy tắc R1–R10.

Điều kiện quan trọng:

> Chỉ được định hướng cạnh khi có đủ căn cứ từ kết quả CI và các quy tắc định hướng hợp lệ.

Ví dụ:

    A o→ B

Không thể tùy tiện chuyển thành:

    A → B

Chỉ vì mô hình dự đoán hướng A → B có xác suất cao.

Lý do:

- Circle biểu thị sự chưa xác định về mặt nhân quả.
- Việc thay circle bằng tail cần được chứng minh bằng quy tắc định hướng hợp lệ hoặc thông tin bổ sung.
- Nếu định hướng sai, đồ thị đầu ra có thể không còn biểu diễn đúng lớp tương đương Markov.

---

## 7. Kết luận

| Câu hỏi | Trả lời |
| --- | --- |
| DAG biểu diễn gì? | Một cấu trúc nhân quả cụ thể |
| CPDAG biểu diễn gì? | Một lớp DAG tương đương Markov |
| PAG biểu diễn gì? | Một lớp MAG tương đương Markov |
| Vì sao PC trả về CPDAG? | Vì PC giả định causal sufficiency |
| Vì sao FCI trả về PAG? | Vì FCI cho phép latent confounding và selection bias |
| Vì sao PAG có circle endpoints? | Vì một số quan hệ tổ tiên không thể nhận dạng duy nhất |
| PAG có xác định chính xác causal DAG không? | Không nhất thiết |
| PAG có cho phép biểu diễn confounding ẩn không? | Có |
| Có thể tối ưu hóa FCI mà không thay đổi PAG không? | Có, nếu bảo toàn các kết quả CI và logic định hướng cần thiết |

**Kết luận cốt lõi:**

DAG biểu diễn một cấu trúc nhân quả cụ thể.

CPDAG biểu diễn sự không chắc chắn giữa các DAG tương đương Markov khi giả định causal sufficiency.

PAG biểu diễn sự không chắc chắn giữa các MAG tương đương Markov khi cho phép biến nhiễu ẩn và selection bias.

FCI sử dụng PAG vì nó cần thể hiện cả khả năng tồn tại latent confounding lẫn những quan hệ nhân quả chưa thể xác định duy nhất.

Đối với nghiên cứu tối ưu hóa FCI/ICD, mục tiêu không phải là ép PAG thành DAG, mà là giảm chi phí tính toán để tìm được PAG đúng theo những giả định và bảo đảm của thuật toán.
