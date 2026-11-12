# Danh sách bài cần tải: causal discovery chuỗi thời gian (09/11/2026)

Đi kèm [`00_ts_causal_discovery_deep_dive_vi.md`](00_ts_causal_discovery_deep_dive_vi.md).

Đã có trong `docs/papers/` và không cần tải lại: `causalrivers.pdf`, `causaldynamics.pdf`, `tFCI & tIOD.pdf`.

Ký hiệu cột "Kiểm":
- ✓CR: DOI đã kiểm qua Crossref.
- ✓arX: arXiv ID đã kiểm qua arXiv API.
- s: chỉ qua kết quả tìm kiếm.

## Ưu tiên 1: cần cho TS-G1

| # | Bài | Venue | DOI | Kiểm |
|---|---|---|---|---|
| 1 | Gerhardus & Runge, *High-recall causal discovery for autocorrelated time series with latent confounders* (LPCMCI) | NeurIPS 2020 | `10.48550/arXiv.2007.01884` | s |
| 2 | Runge, *Discovering contemporaneous and lagged causal relations in autocorrelated nonlinear time series datasets* (PCMCI+) | UAI 2020 | `10.48550/arXiv.2003.03685` | ✓arX |
| 3 | Rohekar et al., *From Temporal to Contemporaneous Iterative Causal Discovery in the Presence of Latent Confounders* (TS-ICD) | ICML 2023 | `10.48550/arXiv.2306.00624` | s |
| 4 | Runge et al., *Detecting and quantifying causal associations in large nonlinear time series datasets* (PCMCI) | Science Advances 2019 | `10.1126/sciadv.aau4996` | ✓CR |
| 5 | Butler et al., *One Thing Leads to Another: The Essentials of Time Series Causal Discovery* | IEEE Signal Processing Magazine 2026 | `10.48550/arXiv.2610.13430` | s |
| 6 | Reiser, *Causal discovery for time series with latent confounders* (đánh giá độc lập LPCMCI) | arXiv 2022 | `10.48550/arXiv.2209.03427` | ✓arX |
| 7 | Ferdous, Hossain, Gani, *TimeGraph* | KDD 2025 D&B | `10.1145/3711896.3737439` | ✓CR |
| 8 | *CausalCompass: Evaluating the Robustness of Time-Series Causal Discovery in Misspecified Scenarios* | NeurIPS 2026 (poster), arXiv | `10.48550/arXiv.2602.07915` | s |
| 9 | *AutoCause: … environmental time-series causal discovery* (loại LPCMCI vì chạy quá thời gian) | arXiv 2026 | `10.48550/arXiv.2608.00198` | s |
| 10 | Lohse & Wahl, *Sortability of Time Series Data* | TMLR 2025 | `10.48550/arXiv.2407.13313` | s |

## Ưu tiên 2: nền tảng và TS-G2

| # | Bài | Venue | DOI | Kiểm |
|---|---|---|---|---|
| 11 | Runge et al., *Inferring causation from time series in Earth system sciences* | Nature Communications 2019 | `10.1038/s41467-019-10105-3` | ✓CR |
| 12 | Runge et al., *Causal inference for time series* | Nature Reviews Earth & Environment 2023 | `10.1038/s43017-023-00431-y` | ✓CR |
| 13 | Assaad, Devijver, Gaussier, *Survey and Evaluation of Causal Discovery Methods for Time Series* | JAIR 2022 | `10.1613/jair.1.13428` | ✓CR |
| 14 | Hyttinen et al., *A constraint optimization approach to causal discovery from subsampled time series data* | IJAR 2017 | `10.1016/j.ijar.2017.07.009` | ✓CR |
| 15 | Liu et al., *Causal Discovery from Subsampled Time Series with Proxy Variables* | NeurIPS 2023 | `10.48550/arXiv.2305.05276` | ✓arX |
| 16 | Gong et al., *Discovering Temporal Causal Relations from Subsampled Data* | ICML 2015 (PMLR v37) | Không có DOI; tìm theo tên | — |
| 17 | Günther, Ninad, Runge, *Causal discovery for time series from multiple datasets with latent contexts* (J-PCMCI+) | UAI 2023 | `10.48550/arXiv.2306.12896` | ✓arX |
| 18 | Saggioro et al., *Reconstructing regime-dependent causal relationships from observational time series* (RPCMCI) | Chaos 2020 | `10.1063/5.0020538` | ✓CR |
| 19 | Huang et al., *Causal Discovery from Heterogeneous/Nonstationary Data with Independent Changes* (CD-NOD) | JMLR 2020 | `10.48550/arXiv.1903.01672` | ✓arX |
| 20 | Reisach, Seiler, Weichwald, *Beware of the Simulated DAG!* | NeurIPS 2021 | `10.48550/arXiv.2102.13647` | ✓arX |

## Ưu tiên 3: các họ phương pháp khác

| # | Bài | Venue | DOI | Kiểm |
|---|---|---|---|---|
| 21 | Granger, *Investigating Causal Relations by Econometric Models and Cross-spectral Methods* | Econometrica 1969 | `10.2307/1912791` | ✓CR |
| 22 | Tank et al., *Neural Granger Causality* | TPAMI 2021 | `10.1109/TPAMI.2021.3065601` | ✓CR |
| 23 | Pamfil et al., *DYNOTEARS* | AISTATS 2020 | `10.48550/arXiv.2002.00498` | ✓arX |
| 24 | Löwe et al., *Amortized Causal Discovery* | CLeaR 2022 | `10.48550/arXiv.2006.10833` | s |
| 25 | Stein, Shadaydeh, Denzler, *Embracing the black box* (Causal Pretraining) | AAAI AI4TS workshop 2024 | `10.48550/arXiv.2402.09305` | s |
| 26 | Cheng et al., *CausalTime* | ICLR 2024 | `10.48550/arXiv.2310.01753` | ✓arX |
| 27 | *Time series causal discovery with variable lags* | arXiv 2026 | `10.48550/arXiv.2605.04081` | s |
| 28 | Hyttinen et al., *Causal Discovery from Subsampled Time Series Data by Constraint Optimization* | PGM 2016 | `10.48550/arXiv.1602.07970` | s |

**Chưa tìm được ID đáng tin, tìm theo tên:**
- Entner & Hoyer 2010 (tsFCI).
- Malinsky & Spirtes 2018 (SVAR-FCI, workshop KDD, PMLR v92).
- Gerhardus 2023/2024 về PAG cho chuỗi thời gian.
- Rhino (ICLR 2023).
