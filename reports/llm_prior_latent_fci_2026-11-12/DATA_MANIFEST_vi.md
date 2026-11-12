# Manifest dữ liệu cho P17 (P-A, P-B)

> Dữ liệu tải về nằm trong `artifacts/llm_prior_p17/` (gitignore). Mọi script đọc chúng chạy với `python -I` và coi chúng là dữ liệu không tin cậy.

## 1. Mạng bnlearn (tải 12/11/2026, user cho phép)

Nguồn: `https://www.bnlearn.com/bnrepository/<name>/<name>.bif.gz`. Chỉ dùng **cấu trúc** (dòng `variable` và `probability ( child | parents )`), không dùng bảng xác suất.

| Mạng | Số biến (đếm từ file) | Bytes (.gz) | SHA-256 của `.bif.gz` |
|---|---|---|---|
| asia | 8 | 310 | `7d5e7b8549834824c1b05f367eb7860fa3fca3adaf3649f0c7be6035af197197` |
| cancer | 5 | 288 | `dcfafbaadabcd1b8c9ec531e16721a19fc06829e980a3967d6345496ea081818` |
| earthquake | 5 | 271 | `77a41f1d509cea15eb7caf9dba932907837149e7145a2cc9d6c95c80849e62b0` |
| survey | 6 | 368 | `676e1fe97efec18b31d1a0a3bcd9b7d52985129c60a78b69172c99e82902ef96` |
| sachs | 11 | 1916 | `ed1830fbde101ed50cce3c7a3c8cbf1d2f5225531cf35ff09fb3cec0af101bce` |
| child | 20 | 1443 | `2bc3236dcbdbf9c9f1bbdeb060aa93c0bdee389d23a549b7248b9d89ed8a980c` |
| insurance | 27 | 3802 | `92bcecd1b85387726af564bf1b50cd400ddbbea1b017303cc54d4654e50a8971` |
| alarm | 37 | 1832 | `f5860caa7137b5817e0c4f169cce0f1451ce6c246b96f5ce4fb4a8167993be29` |
| hailfinder | 56 | 9075 | `efa122a88c4b550569ec821c7879bed9007f2b1e012e1ea52ea26069c7f26099` |
| hepar2 | 70 | 12148 | `f98d4a65c496b79d76b15797e6a6cbeafaff32a17d66a844d8e5b9506d379fcd` |

Số biến khớp với con số ghi từ trí nhớ trong luật đọc §2.1 cho cả mười mạng.

## 2. Bài báo tải để xác minh prior art (Phase 0)

Lưu trong `docs/papers/` (PDF bị gitignore):
- `Andrews_2020_tiered_BK_FCI.pdf`: Andrews, Spirtes, Cooper, AISTATS 2020, PMLR 108:4002–4011, [proceedings.mlr.press/v108/andrews20a](https://proceedings.mlr.press/v108/andrews20a.html).
- `Wang_Qin_Zhou_2022_local_BK_MAG.pdf`: Tian-Zuo Wang, Tian Qin, Zhi-Hua Zhou, NeurIPS 2022, [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2022/hash/4334031bd9d518af18a6aba32ad70c8e-Abstract.html).

## 3. LLM

- Key đọc từ `.env` ở gốc repo (đã thêm vào `.gitignore` ngày 12/11; chưa từng được commit). Biến: `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`.
- Model khả dụng khi kiểm tra 12/11: DeepSeek `deepseek-flash`, `deepseek-v4-pro`; OpenAI có `gpt-4.1-2025-04-14` cùng các dòng gpt-5.x. Model dùng thật sẽ ghi vào luật đọc §7 trước lần gọi đầu tiên của P-A.
- Response thô lưu trong `artifacts/llm_prior_p17/llm_raw/` (gitignore).
