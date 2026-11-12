# Danh sách bài cần tải vào `docs/papers/`: causal ML tài chính (09/11/2026)

Đi kèm [`00_finance_causal_directions_vi.md`](00_finance_causal_directions_vi.md).

Ký hiệu cột "Kiểm":
- ✓CR: DOI đã đối chiếu metadata Crossref trong phiên.
- arXiv: DOI dạng `10.48550/arXiv.*`, lấy từ arXiv ID trong kết quả tìm kiếm.
- ?: DOI nhớ từ trước, **chưa xác minh**.

## Ưu tiên 1: cần để audit hạng 1 (selective labels)

| # | Bài | Venue | DOI | Kiểm |
|---|---|---|---|---|
| 1 | Rambachan, Coston, Kennedy, *Robust Design and Evaluation of Predictive Algorithms under Unobserved Confounding* | Review of Economics and Statistics 2026 | `10.1162/rest.a.1815` (arXiv: `10.48550/arXiv.2212.09844`) | ✓CR |
| 2 | Lakkaraju et al., *The Selective Labels Problem* | KDD 2017 | `10.1145/3097983.3098066` | ✓CR |
| 3 | Coston, Rambachan, Chouldechova, *Characterizing Fairness Over the Set of Good Models Under Selective Labels* | ICML 2021 | `10.48550/arXiv.2101.00352` | arXiv |
| 4 | Kozodoi et al., *Fighting sampling bias: A framework for training and evaluating credit scoring models* | EJOR 2025 | `10.1016/j.ejor.2025.01.040` | ✓CR |
| 5 | Scarone & Baeza-Yates, *The Illusion of Improvement: Reject Inference Strategies in Credit Scoring* | ECML PKDD 2026 | `10.48550/arXiv.2606.18479` | arXiv |
| 6 | *Causal Label Recovery in Payment Networks* | Preprint 2026 | `10.48550/arXiv.2605.29272` | arXiv |
| 7 | Altman et al., *Realistic Synthetic Financial Transactions for Anti-Money Laundering Models* (AMLworld) | NeurIPS 2023 D&B | `10.48550/arXiv.2306.16424` | arXiv |
| 8 | Jesus et al., *Turning the Tables: Biased, Imbalanced, Dynamic Tabular Datasets for ML Evaluation* (BAF) | NeurIPS 2022 D&B | `10.48550/arXiv.2211.13358` | arXiv |
| 9 | Dal Pozzolo et al., *Credit Card Fraud Detection: A Realistic Modeling and a Novel Learning Strategy* | IEEE TNNLS 2018 | `10.1109/TNNLS.2017.2736643` | ✓CR |
| 10 | *PolicyShift-AML: Auditing Selective-Label Policy Dependence in AML Transaction Monitoring* | Research Square 2026 | Không có DOI trong kết quả; link: researchsquare.com/article/rs-10968989/v1 | — |
| 11 | *Performative Prediction with Selective Labels* | NeurIPS 2026 | arXiv ID chưa xác minh; tìm theo tên | — |

## Ưu tiên 2: dự phòng (systemic risk) và dữ liệu tín dụng

| # | Bài | Venue | DOI | Kiểm |
|---|---|---|---|---|
| 12 | Billio, Getmansky, Lo, Pelizzon, *Econometric measures of connectedness and systemic risk…* | J. Financial Economics 2012 | `10.1016/j.jfineco.2011.12.010` | ✓CR |
| 13 | Diebold & Yilmaz, *On the network topology of variance decompositions* | J. Econometrics 2014 | `10.1016/j.jeconom.2014.04.012` | ✓CR |
| 14 | Anand et al., *The missing links: A global study on uncovering financial network structures from partial data* | J. Financial Stability 2018 | `10.1016/j.jfs.2017.05.012` | ✓CR |
| 15 | Adrian & Brunnermeier, *CoVaR* | AER 2016 | `10.1257/aer.20120555` | ✓CR |
| 16 | Brownlees & Engle, *SRISK* | Review of Financial Studies 2017 | `10.1093/rfs/hhw060` | ✓CR |
| 17 | Gerhardus & Runge, *High-recall causal discovery for autocorrelated time series with latent confounders* (LPCMCI) | NeurIPS 2020 | `10.48550/arXiv.2007.01884` | arXiv |
| 18 | Runge et al., *Causal inference for time series* | Nature Reviews Earth & Environment 2023 | `10.1038/s43017-023-00431-y` | ✓CR |
| 19 | Runge et al., *Detecting and quantifying causal associations in large nonlinear time series datasets* (PCMCI) | Science Advances 2019 | `10.1126/sciadv.aau4996` | ✓CR |
| 20 | Gardner, Popovic, Schmidt, *Benchmarking Distribution Shift in Tabular Data with TableShift* | NeurIPS 2023 D&B | `10.48550/arXiv.2312.07577` | arXiv |
| 21 | Fuster et al., *Predictably Unequal? The Effects of Machine Learning on Credit Markets* | J. Finance 2022 | `10.1111/jofi.13090` | ✓CR |

## Ưu tiên 3: pricing, fairness, AML bổ sung

| # | Bài | Venue | DOI | Kiểm |
|---|---|---|---|---|
| 22 | Karlan & Zinman, *Credit Elasticities in Less-Developed Economies: Implications for Microfinance* | AER 2008 | `10.1257/aer.98.3.1040` | ✓CR |
| 23 | Phillips, Simsek, van Ryzin, *The Effectiveness of Field Price Discretion: Empirical Evidence from Auto Lending* | Management Science 2015 | `10.1287/mnsc.2014.2084` | ✓CR |
| 24 | Ban & Keskin, *Personalized Dynamic Pricing with Machine Learning…* | Management Science 2021 | `10.1287/mnsc.2020.3680` | ✓CR |
| 25 | *A Causal Perspective on Loan Pricing: Investigating the Impacts of Selection Bias on Identifying Bid-Response Functions* | Preprint 2023 | `10.48550/arXiv.2309.03730` | arXiv |
| 26 | *Balanced Off-Policy Evaluation for Personalized Pricing* | 2023 | `10.48550/arXiv.2302.12736` | arXiv |
| 27 | Plecko & Bareinboim, *Causal Fairness Analysis* | Foundations and Trends in ML 2024 | `10.1561/2200000106` | ✓CR |
| 28 | Rosenblatt & Witter, *Counterfactual Fairness Is Basically Demographic Parity* | AAAI 2023 | `10.1609/aaai.v37i12.26691` | ✓CR |
| 29 | Kusner et al., *Counterfactual Fairness* | NeurIPS 2017 | `10.48550/arXiv.1703.06856` | ? |
| 30 | Bellei et al., *The Shape of Money Laundering… Elliptic2* | Preprint 2024 | `10.48550/arXiv.2404.19109` | arXiv |
| 31 | Hardt et al., *Strategic Classification* | ITCS 2016 | `10.1145/2840728.2840730` | ✓CR |
| 32 | Perdomo et al., *Performative Prediction* | ICML 2020 | `10.48550/arXiv.2002.06673` | arXiv |
| 33 | Diemert et al., *A Large Scale Benchmark for Individual Treatment Effect Prediction and Uplift* (Criteo) | 2021 | `10.48550/arXiv.2111.10106` | arXiv |

**Đã tra lại:** DOI `10.1287/mnsc.2014.2049` tôi nhớ trước đây cho bài Phillips et al. là **sai**; Crossref trả về một bài khác. DOI đúng là `10.1287/mnsc.2014.2084`.
