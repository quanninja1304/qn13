# Chi phí P-A tính từ prompt thật (13/11/2026)

> **Đã kiểm:**
> - Số lần gọi và số token **input**: đếm trên prompt thật do `PA_prompts.py` sinh ra, bằng tokenizer `o200k_base` (tiktoken 0.14.0) cộng 7 token định dạng mỗi lời gọi. Số liệu trong `PA_prompt_stats.json`.
> - Giá: đọc từ trang chính thức ngày 13/11/2026: [DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing), [OpenAI pricing](https://developers.openai.com/api/docs/pricing).
>
> **Còn là ước lượng:**
> - Token **output** của Q-GRAPH, vì phụ thuộc số cạnh model đề xuất.
> - Token của DeepSeek, tính bằng tokenizer của OpenAI (DeepSeek dùng tokenizer khác; với văn bản tiếng Anh, chênh lệch thường nhỏ).

## 1. Khối lượng mỗi họ model (một lần chạy đủ P-A, cả KEEP và PSEUDO)

| Phần | Số lần gọi | Token input (đếm) | Token output (ước lượng) |
|---|---|---|---|
| Q-GRAPH | 38 | 6 557 | 11 000–45 000 (695 cạnh thật × 2 điều kiện × 1–2 lần × khoảng 8 token/dòng; cận trên có dư) |
| Q-PAIR | 1 452 | 374 502 | khoảng 3 000 (một chữ cái mỗi câu) |
| **Tổng** | **1 490** | **381 059** | **14 000–48 000** |

Con số tôi đưa trước đây (3600 câu Q-PAIR, 1.5 triệu token mỗi họ) là trần trong luật đọc, không phải số thực tế. Sau khi lấy mẫu cặp thật, khối lượng chỉ còn khoảng một phần tư.

## 2. Chi phí mỗi lần chạy đủ P-A

Giá dùng ở đây là mức đắt nhất trên trang chính thức, không tính giảm giá cache.

| Model | Giá in / out (USD mỗi triệu token) | Chi phí, chế độ non-thinking |
|---|---|---|
| **gpt-4.1-mini** | 0.40 / 1.60 | **0.18–0.23 USD** |
| gpt-4.1 | 2.00 / 8.00 | 0.88–1.15 USD |
| **deepseek-flash** (giá giờ cao điểm; ngoài giờ cao điểm rẻ một nửa) | 0.30 / 1.20 | **0.13–0.17 USD** |
| deepseek-v4-pro (giá giờ cao điểm) | 1.32 / 3.96 | 0.56–0.69 USD |

**Nếu để DeepSeek ở chế độ thinking mặc định** (giả định khoảng 1000 token suy nghĩ mỗi lời gọi, đây là ước đoán), phải cộng thêm khoảng 1.8 USD với flash và 5.9 USD với v4-pro. Vì vậy chế độ non-thinking là bắt buộc (§7 mục 12).

## 3. So với số dư

| | Số dư | Bản chính đề xuất | Dư cho chạy lại, kiểm độ bền, model lớn hơn |
|---|---|---|---|
| OpenAI | 5.98 USD | gpt-4.1-mini: khoảng 0.2 USD | Còn chạy được gpt-4.1 khoảng 4 lần đủ P-A |
| DeepSeek | khoảng 2 USD (khi hết pending) | deepseek-flash: khoảng 0.15 USD | Còn chạy được v4-pro khoảng 2 lần |

**Kết luận:** số tiền hiện có đủ cho P-A, cho các lần chạy lại, và cho phần kiểm với model lớn hơn mà reviewer có thể đòi. Phase 2 không gọi LLM mới. Chỉ khi thêm một họ thứ ba (Claude hoặc Llama) mới cần mở tài khoản khác.
