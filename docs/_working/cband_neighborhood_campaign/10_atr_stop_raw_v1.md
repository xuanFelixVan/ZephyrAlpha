---
ttl: task_bound
campaign: cband-20261012
generated_by: scripts/backtest/fexam/cband_grid.py（机生禁手改）
---

# cband_atr_stop_raw（v1，机生）

- 生成：2026-10-11 22:03:11.420894+00:00｜读数等级：**未折减（pre-deflation）：不判 pass/fail，不作采纳依据；折减待令 C 预算册统一口径**
- 预登记册：docs/_working/cband_neighborhood_campaign/01_prereg_axis_sets_v1.yaml｜partial=False｜selftest=False
- 计数：{'coupled': 90, 'decoupled': 24, 'reference': 1, 'rows': 115, 'error_rows': 0}
- 速率标定：{'per_cell_seconds_mean': 0.8003, 'n_cells_timed': 114, 'note': '本装置实测口径；在册 0.53s/格属 c4 网格引擎（T3a 专用），exit_sim prereg legacy_ban 禁引用'}
- 装置：{"module": "scripts/backtest/fexam/exit_sim/exit_simulator.py", "in_register_prereg_frozen_at": "2026-10-06 10:10:50.146205+00:00", "param_faces_used": ["simulate(stop_mode=…)", "atr14_wilder(n=…)"], "windows": {"run": ["2018-01-02", "2026-09-30"], "is": ["2018-01-02", "2025-09-30"], "oos": ["2025-10-09", "2026-09-30"]}, "top_n": 20, "composite_columns_n": 24}

| cell | 轴 | OOS Sharpe | OOS MaxDD | IS Sharpe | ΔOOS Sharpe vs nostop | t vs nostop | 秒 | 状态 |
|---|---|---|---|---|---|---|---|---|
| reference#nostop | {"face": "reference", "mode": "off"} | -0.590 | -71.42% | -0.199 | - | - | None | ok |
| 61c80032#face=coupled;mode=initial_only;mult=2.0;win=7 | {"face": "coupled", "mult": 2.0, "win": 7, "mode": "initial_only"} | 0.449 | -48.41% | -0.225 | 1.0387 | 1.24 | 0.8514 | ok |
| d7f76b25#face=coupled;mode=trailing_only;mult=2.0;win=7 | {"face": "coupled", "mult": 2.0, "win": 7, "mode": "trailing_only"} | 0.391 | -38.01% | -0.249 | 0.9808 | 0.79 | 0.8183 | ok |
| ede110df#face=coupled;mode=initial_or_trailing_max;mult=2.0;win=7 | {"face": "coupled", "mult": 2.0, "win": 7, "mode": "initial_or_trailing_max"} | 0.415 | -38.17% | -0.258 | 1.0046 | 0.77 | 0.7922 | ok |
| 9689a640#face=coupled;mode=initial_only;mult=2.5;win=7 | {"face": "coupled", "mult": 2.5, "win": 7, "mode": "initial_only"} | -0.049 | -57.63% | -0.151 | 0.5402 | 1.42 | 0.8206 | ok |
| 4638503e#face=coupled;mode=trailing_only;mult=2.5;win=7 | {"face": "coupled", "mult": 2.5, "win": 7, "mode": "trailing_only"} | 0.099 | -49.12% | -0.240 | 0.6884 | 0.77 | 0.7797 | ok |
| 182f1cc5#face=coupled;mode=initial_or_trailing_max;mult=2.5;win=7 | {"face": "coupled", "mult": 2.5, "win": 7, "mode": "initial_or_trailing_max"} | 0.090 | -49.45% | -0.263 | 0.6794 | 0.68 | 0.7852 | ok |
| 953b9fa6#face=coupled;mode=initial_only;mult=3.0;win=7 | {"face": "coupled", "mult": 3.0, "win": 7, "mode": "initial_only"} | -0.185 | -61.96% | -0.156 | 0.4051 | 1.44 | 0.801 | ok |
| c58b8572#face=coupled;mode=trailing_only;mult=3.0;win=7 | {"face": "coupled", "mult": 3.0, "win": 7, "mode": "trailing_only"} | -0.005 | -54.93% | -0.193 | 0.5844 | 1.05 | 0.7986 | ok |
| 770ec8ed#face=coupled;mode=initial_or_trailing_max;mult=3.0;win=7 | {"face": "coupled", "mult": 3.0, "win": 7, "mode": "initial_or_trailing_max"} | 0.011 | -54.81% | -0.185 | 0.6008 | 1.11 | 0.8175 | ok |
| c98fb4ed#face=coupled;mode=initial_only;mult=3.5;win=7 | {"face": "coupled", "mult": 3.5, "win": 7, "mode": "initial_only"} | -0.187 | -63.09% | -0.167 | 0.4024 | 1.52 | 0.7301 | ok |
| 752560ac#face=coupled;mode=trailing_only;mult=3.5;win=7 | {"face": "coupled", "mult": 3.5, "win": 7, "mode": "trailing_only"} | -0.190 | -60.86% | -0.178 | 0.3996 | 1.15 | 0.8102 | ok |
| e52c9fd6#face=coupled;mode=initial_or_trailing_max;mult=3.5;win=7 | {"face": "coupled", "mult": 3.5, "win": 7, "mode": "initial_or_trailing_max"} | -0.135 | -60.06% | -0.157 | 0.4545 | 1.36 | 0.8033 | ok |
| 3cfc9055#face=coupled;mode=initial_only;mult=4.0;win=7 | {"face": "coupled", "mult": 4.0, "win": 7, "mode": "initial_only"} | -0.350 | -66.51% | -0.179 | 0.2393 | 1.12 | 0.7957 | ok |
| 7864bddc#face=coupled;mode=trailing_only;mult=4.0;win=7 | {"face": "coupled", "mult": 4.0, "win": 7, "mode": "trailing_only"} | -0.228 | -61.65% | -0.174 | 0.3613 | 1.26 | 0.8183 | ok |
| 386fdeaa#face=coupled;mode=initial_or_trailing_max;mult=4.0;win=7 | {"face": "coupled", "mult": 4.0, "win": 7, "mode": "initial_or_trailing_max"} | -0.198 | -61.19% | -0.172 | 0.3913 | 1.30 | 0.8546 | ok |
| bf2b9f6d#face=coupled;mode=initial_only;mult=5.0;win=7 | {"face": "coupled", "mult": 5.0, "win": 7, "mode": "initial_only"} | -0.557 | -70.10% | -0.170 | 0.0325 | 0.74 | 0.849 | ok |
| 11b9f37b#face=coupled;mode=trailing_only;mult=5.0;win=7 | {"face": "coupled", "mult": 5.0, "win": 7, "mode": "trailing_only"} | -0.392 | -66.37% | -0.206 | 0.1981 | 0.74 | 0.8677 | ok |
| a57827d1#face=coupled;mode=initial_or_trailing_max;mult=5.0;win=7 | {"face": "coupled", "mult": 5.0, "win": 7, "mode": "initial_or_trailing_max"} | -0.379 | -66.09% | -0.192 | 0.2108 | 0.94 | 0.7797 | ok |
| 8cc74203#face=coupled;mode=initial_only;mult=2.0;win=10 | {"face": "coupled", "mult": 2.0, "win": 10, "mode": "initial_only"} | 0.648 | -44.26% | -0.351 | 1.2381 | 0.72 | 0.9035 | ok |
| 10c18ccc#face=coupled;mode=trailing_only;mult=2.0;win=10 | {"face": "coupled", "mult": 2.0, "win": 10, "mode": "trailing_only"} | 0.607 | -33.92% | -0.353 | 1.1962 | 0.55 | 0.8403 | ok |
| dafe43bc#face=coupled;mode=initial_or_trailing_max;mult=2.0;win=10 | {"face": "coupled", "mult": 2.0, "win": 10, "mode": "initial_or_trailing_max"} | 0.621 | -33.26% | -0.379 | 1.2109 | 0.49 | 0.7967 | ok |
| c1b5eaa6#face=coupled;mode=initial_only;mult=2.5;win=10 | {"face": "coupled", "mult": 2.5, "win": 10, "mode": "initial_only"} | 0.037 | -56.58% | -0.283 | 0.6267 | 0.66 | 0.7778 | ok |
| 0c39e9f8#face=coupled;mode=trailing_only;mult=2.5;win=10 | {"face": "coupled", "mult": 2.5, "win": 10, "mode": "trailing_only"} | 0.225 | -45.45% | -0.349 | 0.8152 | 0.38 | 0.7762 | ok |
| 136dcc1e#face=coupled;mode=initial_or_trailing_max;mult=2.5;win=10 | {"face": "coupled", "mult": 2.5, "win": 10, "mode": "initial_or_trailing_max"} | 0.206 | -46.49% | -0.378 | 0.7957 | 0.28 | 0.718 | ok |
| 4f0864fc#face=coupled;mode=initial_only;mult=3.0;win=10 | {"face": "coupled", "mult": 3.0, "win": 10, "mode": "initial_only"} | -0.027 | -57.93% | -0.253 | 0.5626 | 0.80 | 0.7926 | ok |
| 33e2e848#face=coupled;mode=trailing_only;mult=3.0;win=10 | {"face": "coupled", "mult": 3.0, "win": 10, "mode": "trailing_only"} | -0.036 | -55.27% | -0.269 | 0.5535 | 0.59 | 0.8038 | ok |
| 5bf28d96#face=coupled;mode=initial_or_trailing_max;mult=3.0;win=10 | {"face": "coupled", "mult": 3.0, "win": 10, "mode": "initial_or_trailing_max"} | 0.023 | -54.59% | -0.294 | 0.6127 | 0.54 | 0.725 | ok |
| 3a17ae74#face=coupled;mode=initial_only;mult=3.5;win=10 | {"face": "coupled", "mult": 3.5, "win": 10, "mode": "initial_only"} | -0.201 | -62.11% | -0.242 | 0.3888 | 0.67 | 0.7442 | ok |
| 84f8882d#face=coupled;mode=trailing_only;mult=3.5;win=10 | {"face": "coupled", "mult": 3.5, "win": 10, "mode": "trailing_only"} | -0.155 | -60.46% | -0.282 | 0.4347 | 0.38 | 0.7284 | ok |
| d7840fb0#face=coupled;mode=initial_or_trailing_max;mult=3.5;win=10 | {"face": "coupled", "mult": 3.5, "win": 10, "mode": "initial_or_trailing_max"} | -0.079 | -59.29% | -0.285 | 0.5104 | 0.49 | 0.6837 | ok |
| 8a9dba24#face=coupled;mode=initial_only;mult=4.0;win=10 | {"face": "coupled", "mult": 4.0, "win": 10, "mode": "initial_only"} | -0.282 | -65.54% | -0.256 | 0.3080 | 0.32 | 0.7595 | ok |
| 2974a64e#face=coupled;mode=trailing_only;mult=4.0;win=10 | {"face": "coupled", "mult": 4.0, "win": 10, "mode": "trailing_only"} | -0.219 | -61.82% | -0.250 | 0.3705 | 0.59 | 0.7239 | ok |
| 955ba54b#face=coupled;mode=initial_or_trailing_max;mult=4.0;win=10 | {"face": "coupled", "mult": 4.0, "win": 10, "mode": "initial_or_trailing_max"} | -0.147 | -60.64% | -0.263 | 0.4424 | 0.58 | 0.7084 | ok |
| 40dffd9b#face=coupled;mode=initial_only;mult=5.0;win=10 | {"face": "coupled", "mult": 5.0, "win": 10, "mode": "initial_only"} | -0.479 | -68.50% | -0.226 | 0.1109 | 0.11 | 0.7445 | ok |
| 895a544c#face=coupled;mode=trailing_only;mult=5.0;win=10 | {"face": "coupled", "mult": 5.0, "win": 10, "mode": "trailing_only"} | -0.476 | -68.98% | -0.244 | 0.1134 | -0.20 | 0.7343 | ok |
| 5646931a#face=coupled;mode=initial_or_trailing_max;mult=5.0;win=10 | {"face": "coupled", "mult": 5.0, "win": 10, "mode": "initial_or_trailing_max"} | -0.449 | -68.35% | -0.237 | 0.1406 | 0.09 | 0.7326 | ok |
| b418f09a#face=coupled;mode=initial_only;mult=2.0;win=14 | {"face": "coupled", "mult": 2.0, "win": 14, "mode": "initial_only"} | 0.728 | -39.81% | -0.321 | 1.3180 | 0.82 | 0.7507 | ok |
| 7687a895#face=coupled;mode=trailing_only;mult=2.0;win=14 | {"face": "coupled", "mult": 2.0, "win": 14, "mode": "trailing_only"} | 0.456 | -30.79% | -0.440 | 1.0455 | 0.27 | 0.7218 | ok |
| 69ee1fc2#face=coupled;mode=initial_or_trailing_max;mult=2.0;win=14 | {"face": "coupled", "mult": 2.0, "win": 14, "mode": "initial_or_trailing_max"} | 0.426 | -30.25% | -0.463 | 1.0160 | 0.21 | 0.7787 | ok |
| b0a05b19#face=coupled;mode=initial_only;mult=2.5;win=14 | {"face": "coupled", "mult": 2.5, "win": 14, "mode": "initial_only"} | 0.230 | -52.05% | -0.287 | 0.8201 | 0.81 | 0.707 | ok |
| 61bb59fa#face=coupled;mode=trailing_only;mult=2.5;win=14 | {"face": "coupled", "mult": 2.5, "win": 14, "mode": "trailing_only"} | 0.272 | -41.28% | -0.409 | 0.8613 | 0.22 | 0.7646 | ok |
| 5fa924bd#face=coupled;mode=initial_or_trailing_max;mult=2.5;win=14 | {"face": "coupled", "mult": 2.5, "win": 14, "mode": "initial_or_trailing_max"} | 0.189 | -42.12% | -0.427 | 0.7783 | 0.13 | 0.6994 | ok |
| d08a9a36#face=coupled;mode=initial_only;mult=3.0;win=14 | {"face": "coupled", "mult": 3.0, "win": 14, "mode": "initial_only"} | 0.065 | -55.84% | -0.230 | 0.6547 | 1.07 | 0.7776 | ok |
| dc23ebf6#face=coupled;mode=trailing_only;mult=3.0;win=14 | {"face": "coupled", "mult": 3.0, "win": 14, "mode": "trailing_only"} | 0.119 | -51.32% | -0.274 | 0.7085 | 0.69 | 0.7616 | ok |
| 869c7b52#face=coupled;mode=initial_or_trailing_max;mult=3.0;win=14 | {"face": "coupled", "mult": 3.0, "win": 14, "mode": "initial_or_trailing_max"} | 0.229 | -49.55% | -0.291 | 0.8189 | 0.72 | 0.741 | ok |
| be79d150#face=coupled;mode=initial_only;mult=3.5;win=14 | {"face": "coupled", "mult": 3.5, "win": 14, "mode": "initial_only"} | 0.006 | -57.72% | -0.227 | 0.5962 | 1.10 | 0.8169 | ok |
| f94fcf5e#face=coupled;mode=trailing_only;mult=3.5;win=14 | {"face": "coupled", "mult": 3.5, "win": 14, "mode": "trailing_only"} | -0.103 | -58.44% | -0.237 | 0.4869 | 0.79 | 0.773 | ok |
| e2119dec#face=coupled;mode=initial_or_trailing_max;mult=3.5;win=14 | {"face": "coupled", "mult": 3.5, "win": 14, "mode": "initial_or_trailing_max"} | -0.018 | -57.32% | -0.279 | 0.5719 | 0.62 | 0.6911 | ok |
| ed78accc#face=coupled;mode=initial_only;mult=4.0;win=14 | {"face": "coupled", "mult": 4.0, "win": 14, "mode": "initial_only"} | -0.231 | -62.40% | -0.229 | 0.3585 | 0.81 | 0.7248 | ok |
| 8c76881d#face=coupled;mode=trailing_only;mult=4.0;win=14 | {"face": "coupled", "mult": 4.0, "win": 14, "mode": "trailing_only"} | -0.164 | -60.97% | -0.220 | 0.4257 | 1.00 | 0.7436 | ok |
| 2f1085b7#face=coupled;mode=initial_or_trailing_max;mult=4.0;win=14 | {"face": "coupled", "mult": 4.0, "win": 14, "mode": "initial_or_trailing_max"} | -0.108 | -59.84% | -0.254 | 0.4817 | 0.76 | 0.7281 | ok |
| 3c653c00#face=coupled;mode=initial_only;mult=5.0;win=14 | {"face": "coupled", "mult": 5.0, "win": 14, "mode": "initial_only"} | -0.372 | -66.65% | -0.205 | 0.2181 | 0.87 | 0.6776 | ok |
| 768d7546#face=coupled;mode=trailing_only;mult=5.0;win=14 | {"face": "coupled", "mult": 5.0, "win": 14, "mode": "trailing_only"} | -0.452 | -68.52% | -0.192 | 0.1373 | 1.00 | 0.8064 | ok |
| a099b87a#face=coupled;mode=initial_or_trailing_max;mult=5.0;win=14 | {"face": "coupled", "mult": 5.0, "win": 14, "mode": "initial_or_trailing_max"} | -0.353 | -66.71% | -0.201 | 0.2367 | 0.95 | 0.6578 | ok |
| 5303ed07#face=coupled;mode=initial_only;mult=2.0;win=21 | {"face": "coupled", "mult": 2.0, "win": 21, "mode": "initial_only"} | 0.844 | -34.79% | -0.314 | 1.4336 | 0.83 | 0.7563 | ok |
| 46d8fc2d#face=coupled;mode=trailing_only;mult=2.0;win=21 | {"face": "coupled", "mult": 2.0, "win": 21, "mode": "trailing_only"} | 0.054 | -28.08% | -0.366 | 0.6433 | 0.32 | 0.6607 | ok |
| 6fb3488e#face=coupled;mode=initial_or_trailing_max;mult=2.0;win=21 | {"face": "coupled", "mult": 2.0, "win": 21, "mode": "initial_or_trailing_max"} | 0.187 | -26.22% | -0.380 | 0.7766 | 0.34 | 0.7628 | ok |
| 8b8a0db7#face=coupled;mode=initial_only;mult=2.5;win=21 | {"face": "coupled", "mult": 2.5, "win": 21, "mode": "initial_only"} | 0.490 | -43.51% | -0.349 | 1.0795 | 0.61 | 0.717 | ok |
| 053fd825#face=coupled;mode=trailing_only;mult=2.5;win=21 | {"face": "coupled", "mult": 2.5, "win": 21, "mode": "trailing_only"} | 0.325 | -36.12% | -0.332 | 0.9145 | 0.51 | 0.7248 | ok |
| 13efd16e#face=coupled;mode=initial_or_trailing_max;mult=2.5;win=21 | {"face": "coupled", "mult": 2.5, "win": 21, "mode": "initial_or_trailing_max"} | 0.145 | -36.30% | -0.368 | 0.7346 | 0.32 | 0.7198 | ok |
| 0ce615c1#face=coupled;mode=initial_only;mult=3.0;win=21 | {"face": "coupled", "mult": 3.0, "win": 21, "mode": "initial_only"} | 0.126 | -54.84% | -0.328 | 0.7155 | 0.49 | 0.7827 | ok |
| d70d2f7b#face=coupled;mode=trailing_only;mult=3.0;win=21 | {"face": "coupled", "mult": 3.0, "win": 21, "mode": "trailing_only"} | 0.090 | -44.67% | -0.390 | 0.6794 | 0.16 | 0.7793 | ok |
| a5abb359#face=coupled;mode=initial_or_trailing_max;mult=3.0;win=21 | {"face": "coupled", "mult": 3.0, "win": 21, "mode": "initial_or_trailing_max"} | 0.130 | -44.27% | -0.409 | 0.7201 | 0.13 | 0.7312 | ok |
| aaa4a0e4#face=coupled;mode=initial_only;mult=3.5;win=21 | {"face": "coupled", "mult": 3.5, "win": 21, "mode": "initial_only"} | 0.030 | -56.37% | -0.275 | 0.6193 | 0.70 | 0.7768 | ok |
| 7df9f7ae#face=coupled;mode=trailing_only;mult=3.5;win=21 | {"face": "coupled", "mult": 3.5, "win": 21, "mode": "trailing_only"} | -0.027 | -54.24% | -0.325 | 0.5631 | 0.31 | 0.7783 | ok |
| 58928fe2#face=coupled;mode=initial_or_trailing_max;mult=3.5;win=21 | {"face": "coupled", "mult": 3.5, "win": 21, "mode": "initial_or_trailing_max"} | 0.077 | -52.79% | -0.333 | 0.6671 | 0.40 | 0.7336 | ok |
| 8ef05545#face=coupled;mode=initial_only;mult=4.0;win=21 | {"face": "coupled", "mult": 4.0, "win": 21, "mode": "initial_only"} | -0.016 | -57.99% | -0.318 | 0.5740 | 0.33 | 0.6988 | ok |
| 66c4f0fd#face=coupled;mode=trailing_only;mult=4.0;win=21 | {"face": "coupled", "mult": 4.0, "win": 21, "mode": "trailing_only"} | -0.132 | -58.49% | -0.276 | 0.4580 | 0.46 | 0.8017 | ok |
| 104ee4ff#face=coupled;mode=initial_or_trailing_max;mult=4.0;win=21 | {"face": "coupled", "mult": 4.0, "win": 21, "mode": "initial_or_trailing_max"} | -0.043 | -57.32% | -0.328 | 0.5463 | 0.26 | 0.797 | ok |
| 01d118b8#face=coupled;mode=initial_only;mult=5.0;win=21 | {"face": "coupled", "mult": 5.0, "win": 21, "mode": "initial_only"} | -0.272 | -65.01% | -0.267 | 0.3175 | 0.25 | 0.8294 | ok |
| d800ad82#face=coupled;mode=trailing_only;mult=5.0;win=21 | {"face": "coupled", "mult": 5.0, "win": 21, "mode": "trailing_only"} | -0.328 | -66.41% | -0.249 | 0.2615 | 0.31 | 0.9025 | ok |
| 502e6c58#face=coupled;mode=initial_or_trailing_max;mult=5.0;win=21 | {"face": "coupled", "mult": 5.0, "win": 21, "mode": "initial_or_trailing_max"} | -0.211 | -64.53% | -0.274 | 0.3787 | 0.33 | 0.8564 | ok |
| 24390364#face=coupled;mode=initial_only;mult=2.0;win=30 | {"face": "coupled", "mult": 2.0, "win": 30, "mode": "initial_only"} | 0.697 | -32.62% | -0.307 | 1.2865 | 0.75 | 0.9202 | ok |
| aa12323f#face=coupled;mode=trailing_only;mult=2.0;win=30 | {"face": "coupled", "mult": 2.0, "win": 30, "mode": "trailing_only"} | 0.102 | -23.91% | -0.380 | 0.6921 | 0.34 | 0.885 | ok |
| aaee09b5#face=coupled;mode=initial_or_trailing_max;mult=2.0;win=30 | {"face": "coupled", "mult": 2.0, "win": 30, "mode": "initial_or_trailing_max"} | 0.077 | -23.35% | -0.413 | 0.6666 | 0.28 | 0.9249 | ok |
| 640d03a5#face=coupled;mode=initial_only;mult=2.5;win=30 | {"face": "coupled", "mult": 2.5, "win": 30, "mode": "initial_only"} | 0.603 | -39.47% | -0.318 | 1.1926 | 0.75 | 0.8749 | ok |
| c5a9881e#face=coupled;mode=trailing_only;mult=2.5;win=30 | {"face": "coupled", "mult": 2.5, "win": 30, "mode": "trailing_only"} | -0.023 | -33.22% | -0.295 | 0.5669 | 0.46 | 0.9204 | ok |
| 6abaa5cd#face=coupled;mode=initial_or_trailing_max;mult=2.5;win=30 | {"face": "coupled", "mult": 2.5, "win": 30, "mode": "initial_or_trailing_max"} | -0.032 | -32.34% | -0.262 | 0.5575 | 0.54 | 0.8167 | ok |
| db08c8b4#face=coupled;mode=initial_only;mult=3.0;win=30 | {"face": "coupled", "mult": 3.0, "win": 30, "mode": "initial_only"} | 0.463 | -44.27% | -0.307 | 1.0531 | 0.77 | 0.8938 | ok |
| 9869d4c5#face=coupled;mode=trailing_only;mult=3.0;win=30 | {"face": "coupled", "mult": 3.0, "win": 30, "mode": "trailing_only"} | 0.281 | -36.70% | -0.321 | 0.8710 | 0.50 | 0.8465 | ok |
| 557c0b71#face=coupled;mode=initial_or_trailing_max;mult=3.0;win=30 | {"face": "coupled", "mult": 3.0, "win": 30, "mode": "initial_or_trailing_max"} | 0.157 | -36.91% | -0.355 | 0.7468 | 0.35 | 0.9498 | ok |
| 7121fd77#face=coupled;mode=initial_only;mult=3.5;win=30 | {"face": "coupled", "mult": 3.5, "win": 30, "mode": "initial_only"} | 0.139 | -54.21% | -0.275 | 0.7290 | 0.79 | 0.8878 | ok |
| 1175733e#face=coupled;mode=trailing_only;mult=3.5;win=30 | {"face": "coupled", "mult": 3.5, "win": 30, "mode": "trailing_only"} | 0.028 | -44.85% | -0.391 | 0.6181 | 0.09 | 0.8908 | ok |
| f92b91c7#face=coupled;mode=initial_or_trailing_max;mult=3.5;win=30 | {"face": "coupled", "mult": 3.5, "win": 30, "mode": "initial_or_trailing_max"} | 0.204 | -42.64% | -0.398 | 0.7933 | 0.19 | 0.896 | ok |
| 380b99f2#face=coupled;mode=initial_only;mult=4.0;win=30 | {"face": "coupled", "mult": 4.0, "win": 30, "mode": "initial_only"} | 0.038 | -56.21% | -0.285 | 0.6272 | 0.62 | 0.9032 | ok |
| 629ac1e7#face=coupled;mode=trailing_only;mult=4.0;win=30 | {"face": "coupled", "mult": 4.0, "win": 30, "mode": "trailing_only"} | 0.099 | -50.77% | -0.348 | 0.6888 | 0.27 | 0.8033 | ok |
| fd0cdb63#face=coupled;mode=initial_or_trailing_max;mult=4.0;win=30 | {"face": "coupled", "mult": 4.0, "win": 30, "mode": "initial_or_trailing_max"} | 0.184 | -49.50% | -0.382 | 0.7738 | 0.22 | 0.8325 | ok |
| 7f115379#face=coupled;mode=initial_only;mult=5.0;win=30 | {"face": "coupled", "mult": 5.0, "win": 30, "mode": "initial_only"} | -0.239 | -63.98% | -0.251 | 0.3509 | 0.47 | 0.856 | ok |
| 419cf68c#face=coupled;mode=trailing_only;mult=5.0;win=30 | {"face": "coupled", "mult": 5.0, "win": 30, "mode": "trailing_only"} | -0.323 | -65.84% | -0.274 | 0.2666 | 0.07 | 0.8704 | ok |
| 3d662596#face=coupled;mode=initial_or_trailing_max;mult=5.0;win=30 | {"face": "coupled", "mult": 5.0, "win": 30, "mode": "initial_or_trailing_max"} | -0.249 | -64.44% | -0.274 | 0.3409 | 0.26 | 0.9444 | ok |
| fcc99914#face=decoupled_filter14;mode=initial_or_trailing_max;mult=2.0;win=7 | {"face": "decoupled_filter14", "mult": 2.0, "win": 7, "mode": "initial_or_trailing_max"} | 0.415 | -38.17% | -0.350 | 1.0046 | 0.49 | 0.8803 | ok |
| e0e082dd#face=decoupled_filter14;mode=initial_or_trailing_max;mult=2.5;win=7 | {"face": "decoupled_filter14", "mult": 2.5, "win": 7, "mode": "initial_or_trailing_max"} | 0.090 | -49.45% | -0.335 | 0.6794 | 0.38 | 0.8707 | ok |
| ecead5a8#face=decoupled_filter14;mode=initial_or_trailing_max;mult=3.0;win=7 | {"face": "decoupled_filter14", "mult": 3.0, "win": 7, "mode": "initial_or_trailing_max"} | 0.011 | -54.81% | -0.266 | 0.6008 | 0.68 | 0.9988 | ok |
| 003ebf05#face=decoupled_filter14;mode=initial_or_trailing_max;mult=3.5;win=7 | {"face": "decoupled_filter14", "mult": 3.5, "win": 7, "mode": "initial_or_trailing_max"} | -0.135 | -60.06% | -0.221 | 0.4545 | 0.93 | 0.8736 | ok |
| 82d53467#face=decoupled_filter14;mode=initial_or_trailing_max;mult=4.0;win=7 | {"face": "decoupled_filter14", "mult": 4.0, "win": 7, "mode": "initial_or_trailing_max"} | -0.198 | -61.19% | -0.234 | 0.3913 | 0.81 | 0.8665 | ok |
| c38c1cc8#face=decoupled_filter14;mode=initial_or_trailing_max;mult=5.0;win=7 | {"face": "decoupled_filter14", "mult": 5.0, "win": 7, "mode": "initial_or_trailing_max"} | -0.379 | -66.09% | -0.235 | 0.2108 | 0.46 | 0.9068 | ok |
| 14b33f95#face=decoupled_filter14;mode=initial_or_trailing_max;mult=2.0;win=10 | {"face": "decoupled_filter14", "mult": 2.0, "win": 10, "mode": "initial_or_trailing_max"} | 0.621 | -33.26% | -0.352 | 1.2109 | 0.57 | 0.9313 | ok |
| 277d7ee7#face=decoupled_filter14;mode=initial_or_trailing_max;mult=2.5;win=10 | {"face": "decoupled_filter14", "mult": 2.5, "win": 10, "mode": "initial_or_trailing_max"} | 0.206 | -46.49% | -0.353 | 0.7957 | 0.38 | 0.9618 | ok |
| b191f69f#face=decoupled_filter14;mode=initial_or_trailing_max;mult=3.0;win=10 | {"face": "decoupled_filter14", "mult": 3.0, "win": 10, "mode": "initial_or_trailing_max"} | 0.023 | -54.59% | -0.289 | 0.6127 | 0.58 | 0.8508 | ok |
| 17b564e8#face=decoupled_filter14;mode=initial_or_trailing_max;mult=3.5;win=10 | {"face": "decoupled_filter14", "mult": 3.5, "win": 10, "mode": "initial_or_trailing_max"} | -0.079 | -59.29% | -0.278 | 0.5104 | 0.55 | 0.8628 | ok |
| 594fef47#face=decoupled_filter14;mode=initial_or_trailing_max;mult=4.0;win=10 | {"face": "decoupled_filter14", "mult": 4.0, "win": 10, "mode": "initial_or_trailing_max"} | -0.147 | -60.64% | -0.246 | 0.4424 | 0.77 | 0.8574 | ok |
| f1c20bcc#face=decoupled_filter14;mode=initial_or_trailing_max;mult=5.0;win=10 | {"face": "decoupled_filter14", "mult": 5.0, "win": 10, "mode": "initial_or_trailing_max"} | -0.449 | -68.35% | -0.215 | 0.1406 | 0.49 | 0.8567 | ok |
| c5de4653#face=decoupled_filter14;mode=initial_or_trailing_max;mult=2.0;win=21 | {"face": "decoupled_filter14", "mult": 2.0, "win": 21, "mode": "initial_or_trailing_max"} | 0.187 | -26.22% | -0.361 | 0.7766 | 0.38 | 0.8721 | ok |
| eec5346c#face=decoupled_filter14;mode=initial_or_trailing_max;mult=2.5;win=21 | {"face": "decoupled_filter14", "mult": 2.5, "win": 21, "mode": "initial_or_trailing_max"} | 0.145 | -36.30% | -0.345 | 0.7346 | 0.39 | 0.874 | ok |
| f727777f#face=decoupled_filter14;mode=initial_or_trailing_max;mult=3.0;win=21 | {"face": "decoupled_filter14", "mult": 3.0, "win": 21, "mode": "initial_or_trailing_max"} | 0.130 | -44.27% | -0.384 | 0.7201 | 0.22 | 0.7417 | ok |
| 1314ca87#face=decoupled_filter14;mode=initial_or_trailing_max;mult=3.5;win=21 | {"face": "decoupled_filter14", "mult": 3.5, "win": 21, "mode": "initial_or_trailing_max"} | 0.077 | -52.79% | -0.280 | 0.6671 | 0.67 | 0.7774 | ok |
| fea42cd5#face=decoupled_filter14;mode=initial_or_trailing_max;mult=4.0;win=21 | {"face": "decoupled_filter14", "mult": 4.0, "win": 21, "mode": "initial_or_trailing_max"} | -0.043 | -57.32% | -0.277 | 0.5463 | 0.60 | 0.7371 | ok |
| 22ec85d0#face=decoupled_filter14;mode=initial_or_trailing_max;mult=5.0;win=21 | {"face": "decoupled_filter14", "mult": 5.0, "win": 21, "mode": "initial_or_trailing_max"} | -0.211 | -64.53% | -0.223 | 0.3787 | 0.91 | 0.818 | ok |
| 1366841f#face=decoupled_filter14;mode=initial_or_trailing_max;mult=2.0;win=30 | {"face": "decoupled_filter14", "mult": 2.0, "win": 30, "mode": "initial_or_trailing_max"} | 0.077 | -23.35% | -0.405 | 0.6666 | 0.30 | 0.7069 | ok |
| ceb78fd2#face=decoupled_filter14;mode=initial_or_trailing_max;mult=2.5;win=30 | {"face": "decoupled_filter14", "mult": 2.5, "win": 30, "mode": "initial_or_trailing_max"} | -0.032 | -32.34% | -0.253 | 0.5575 | 0.57 | 0.7172 | ok |
| 9610c692#face=decoupled_filter14;mode=initial_or_trailing_max;mult=3.0;win=30 | {"face": "decoupled_filter14", "mult": 3.0, "win": 30, "mode": "initial_or_trailing_max"} | 0.157 | -36.91% | -0.330 | 0.7468 | 0.43 | 0.7679 | ok |
| 75347b2d#face=decoupled_filter14;mode=initial_or_trailing_max;mult=3.5;win=30 | {"face": "decoupled_filter14", "mult": 3.5, "win": 30, "mode": "initial_or_trailing_max"} | 0.204 | -42.64% | -0.349 | 0.7933 | 0.39 | 0.7451 | ok |
| c8ed9cc4#face=decoupled_filter14;mode=initial_or_trailing_max;mult=4.0;win=30 | {"face": "decoupled_filter14", "mult": 4.0, "win": 30, "mode": "initial_or_trailing_max"} | 0.184 | -49.50% | -0.337 | 0.7738 | 0.45 | 0.7305 | ok |
| 38a82565#face=decoupled_filter14;mode=initial_or_trailing_max;mult=5.0;win=30 | {"face": "decoupled_filter14", "mult": 5.0, "win": 30, "mode": "initial_or_trailing_max"} | -0.249 | -64.44% | -0.232 | 0.3409 | 0.65 | 0.717 | ok |

## nostop 基线与在册读数对锚

```json
{
 "in_register": {
  "oos_sharpe": -0.18693,
  "oos_maxdd": -0.57556,
  "run_sharpe": -0.33015
 },
 "measured": {
  "oos_sharpe": -0.58972502,
  "oos_maxdd": -0.71423225,
  "run_sharpe": -0.26260609
 },
 "verdict": "与在册不等——如实登记偏差（疑似数据面自 10-06 起重算：后复权表族/指标面续供），禁调装置凑数"
}
```
