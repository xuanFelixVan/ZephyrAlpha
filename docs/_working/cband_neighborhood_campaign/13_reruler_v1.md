---
ttl: task_bound
campaign: cband-20261012
generated_by: scripts/backtest/fexam/cband_grid.py --rejudge（机生禁手改）
---

# cband_reruler_v1（v1，机生）

- 依据：统筹晨裁 2026-10-12（②号发给 C 族邻域班）①：换尺＝批，两案并用
- 等级：**尺判别力标定（折减前＋在标为无效待复算的快照上），非任何格的录用判定**
- 底层读数有效性：void_pending_recompute——晨裁①原文：基线被 TI 回填挪了零点，159 格现读数全部标记无效待复算
- 继承阈数值（禁改）：{"maxdd_gain_pp": 0.05, "sharpe_delta_floor": -0.2}
- 近似申报：实现波动量级 σ=|年化收益|/|Sharpe|（年化收益由 total_return 与 n_days 几何折算；Sharpe 与收益符号相反时取量级，因 λ 是比值故抵消）；参照臂按 λ=σ_cell/σ_ref 等比缩放：Sharpe 对缩放不变，回撤/收益按 (1+x)^λ−1 几何缩放——只有端点统计量时的近似，随册申报；复算时（令 D 晨裁⑤）应改从逐日净值序列量 σ，本近似届时退役

## leg2_atr_stop_vs_nostop

- 格数 114（可判 114／不可判 0｜λ 可信带内 82）
- 判别力（命中/可判）：{"在册原尺_仅OOS": {"hit": 105, "of_comparable": 114}, "案A_IS与OOS双窗同改": {"hit": 15, "of_comparable": 114}, "案B_同波动缩放对照_仅OOS": {"hit": 69, "of_comparable": 114}, "新尺_案A且案B": {"hit": 6, "of_comparable": 114}, "案B_仅λ可信带内_诊断": {"hit": 59, "of_comparable": 82}, "新尺A且B_仅λ可信带内_诊断": {"hit": 6, "of_comparable": 82}}

## leg4_allocator_vs_same_scheme_baseline

- 格数 39（可判 39／不可判 0｜λ 可信带内 39）
- 判别力（命中/可判）：{"在册原尺_仅OOS": {"hit": 0, "of_comparable": 39}, "案A_IS与OOS双窗同改": {"hit": 0, "of_comparable": 39}, "案B_同波动缩放对照_仅OOS": {"hit": 4, "of_comparable": 39}, "新尺_案A且案B": {"hit": 0, "of_comparable": 39}, "案B_仅λ可信带内_诊断": {"hit": 4, "of_comparable": 39}, "新尺A且B_仅λ可信带内_诊断": {"hit": 0, "of_comparable": 39}}

### leg2_atr_stop_vs_nostop 逐格（最多 400 行）

| cell | λ(OOS) | 原尺仅OOS | 案A双窗 | 案B缩放 | 新尺A∧B | 原始OOS: dd改善pp/SharpeΔ | 缩放后OOS: dd改善pp |
|---|---|---|---|---|---|---|---|
| 61c80032#face=coupled;mode=initial_only;mult=2.0;win=7 | 0.3285 | True | False | False | False | 23.01 / 1.0387 | -14.68 |
| d7f76b25#face=coupled;mode=trailing_only;mult=2.0;win=7 | 0.2819 | True | True | False | False | 33.41 / 0.9808 | -8.26 |
| f#face=coupled;mode=initial_or_trailing_max;mult=2.0;win=7 | 0.2935 | True | True | False | False | 33.25 / 1.0046 | -7.41 |
| 9689a640#face=coupled;mode=initial_only;mult=2.5;win=7 | 3.8045 | True | False | True | False | 13.79 / 0.5402 | 41.51 |
| 4638503e#face=coupled;mode=trailing_only;mult=2.5;win=7 | 0.6021 | True | False | False | False | 22.3 / 0.6884 | 3.84 |
| 5#face=coupled;mode=initial_or_trailing_max;mult=2.5;win=7 | 0.7114 | True | False | True | False | 21.97 / 0.6794 | 9.53 |
| 953b9fa6#face=coupled;mode=initial_only;mult=3.0;win=7 | 1.6194 | True | False | True | False | 9.46 / 0.4051 | 24.88 |
| c58b8572#face=coupled;mode=trailing_only;mult=3.0;win=7 | 26.7754 | True | False | True | False | 16.49 / 0.5844 | 45.07 |
| d#face=coupled;mode=initial_or_trailing_max;mult=3.0;win=7 | 11.9357 | True | False | True | False | 16.61 / 0.6008 | 45.19 |
| c98fb4ed#face=coupled;mode=initial_only;mult=3.5;win=7 | 1.6341 | True | False | True | False | 8.33 / 0.4024 | 23.99 |
| 752560ac#face=coupled;mode=trailing_only;mult=3.5;win=7 | 1.458 | True | False | True | False | 10.57 / 0.3996 | 23.04 |
| 6#face=coupled;mode=initial_or_trailing_max;mult=3.5;win=7 | 1.8081 | True | False | True | False | 11.37 / 0.4545 | 29.56 |
| 3cfc9055#face=coupled;mode=initial_only;mult=4.0;win=7 | 1.2417 | False | False | True | False | 4.91 / 0.2393 | 12.38 |
| 7864bddc#face=coupled;mode=trailing_only;mult=4.0;win=7 | 1.3314 | True | False | True | False | 9.78 / 0.3613 | 19.48 |
| a#face=coupled;mode=initial_or_trailing_max;mult=4.0;win=7 | 1.4459 | True | False | True | False | 10.23 / 0.3913 | 22.46 |
| bf2b9f6d#face=coupled;mode=initial_only;mult=5.0;win=7 | 0.9989 | False | False | False | False | 1.33 / 0.0325 | 1.29 |
| 11b9f37b#face=coupled;mode=trailing_only;mult=5.0;win=7 | 1.1148 | True | False | True | False | 5.05 / 0.1981 | 8.88 |
| 1#face=coupled;mode=initial_or_trailing_max;mult=5.0;win=7 | 1.1256 | True | False | True | False | 5.33 / 0.2108 | 9.49 |
| 8cc74203#face=coupled;mode=initial_only;mult=2.0;win=10 | 0.4113 | True | False | False | False | 27.16 / 1.2381 | -4.0 |
| 10c18ccc#face=coupled;mode=trailing_only;mult=2.0;win=10 | 0.355 | True | True | False | False | 37.5 / 1.1962 | 1.97 |
| #face=coupled;mode=initial_or_trailing_max;mult=2.0;win=10 | 0.3549 | True | True | False | False | 38.17 / 1.2109 | 2.63 |
| c1b5eaa6#face=coupled;mode=initial_only;mult=2.5;win=10 | 3.6831 | True | False | True | False | 14.84 / 0.6267 | 42.42 |
| 0c39e9f8#face=coupled;mode=trailing_only;mult=2.5;win=10 | 0.0926 | True | False | False | False | 25.98 / 0.8152 | -34.5 |
| #face=coupled;mode=initial_or_trailing_max;mult=2.5;win=10 | 0.0522 | True | False | False | False | 24.93 / 0.7957 | -40.16 |
| 4f0864fc#face=coupled;mode=initial_only;mult=3.0;win=10 | 6.5439 | True | False | True | False | 13.49 / 0.5626 | 42.04 |
| 33e2e848#face=coupled;mode=trailing_only;mult=3.0;win=10 | 4.3804 | True | False | True | False | 16.15 / 0.5535 | 44.32 |
| #face=coupled;mode=initial_or_trailing_max;mult=3.0;win=10 | 5.3814 | True | False | True | False | 16.83 / 0.6127 | 45.29 |
| 3a17ae74#face=coupled;mode=initial_only;mult=3.5;win=10 | 1.542 | True | False | True | False | 9.31 / 0.3888 | 23.39 |
| 84f8882d#face=coupled;mode=trailing_only;mult=3.5;win=10 | 1.6404 | True | False | True | False | 10.96 / 0.4347 | 26.73 |
| #face=coupled;mode=initial_or_trailing_max;mult=3.5;win=10 | 2.6357 | True | False | True | False | 12.13 / 0.5104 | 37.02 |
| 8a9dba24#face=coupled;mode=initial_only;mult=4.0;win=10 | 1.385 | True | False | True | False | 5.89 / 0.308 | 16.82 |
| 2974a64e#face=coupled;mode=trailing_only;mult=4.0;win=10 | 1.3615 | True | False | True | False | 9.6 / 0.3705 | 20.01 |
| #face=coupled;mode=initial_or_trailing_max;mult=4.0;win=10 | 1.7289 | True | False | True | False | 10.78 / 0.4424 | 27.89 |
| 40dffd9b#face=coupled;mode=initial_only;mult=5.0;win=10 | 1.0646 | False | False | True | False | 2.92 / 0.1109 | 5.14 |
| 895a544c#face=coupled;mode=trailing_only;mult=5.0;win=10 | 1.0799 | False | False | True | False | 2.45 / 0.1134 | 5.17 |
| #face=coupled;mode=initial_or_trailing_max;mult=5.0;win=10 | 1.1001 | False | False | True | False | 3.07 / 0.1406 | 6.44 |
| b418f09a#face=coupled;mode=initial_only;mult=2.0;win=14 | 0.4146 | True | True | False | False | 31.61 / 1.318 | 0.7 |
| 7687a895#face=coupled;mode=trailing_only;mult=2.0;win=14 | 0.2912 | True | False | False | False | 40.64 / 1.0455 | -0.22 |
| #face=coupled;mode=initial_or_trailing_max;mult=2.0;win=14 | 0.2771 | True | False | False | False | 41.17 / 1.016 | -0.92 |
| b0a05b19#face=coupled;mode=initial_only;mult=2.5;win=14 | 0.0095 | True | False | False | False | 19.38 / 0.8201 | -50.87 |
| 61bb59fa#face=coupled;mode=trailing_only;mult=2.5;win=14 | 0.1801 | True | False | False | False | 30.14 / 0.8613 | -21.08 |
| #face=coupled;mode=initial_or_trailing_max;mult=2.5;win=14 | 0.0423 | True | False | False | False | 29.3 / 0.7783 | -36.96 |
| d08a9a36#face=coupled;mode=initial_only;mult=3.0;win=14 | 1.8056 | True | False | True | False | 15.58 / 0.6547 | 33.74 |
| dc23ebf6#face=coupled;mode=trailing_only;mult=3.0;win=14 | 0.4323 | True | False | False | False | 20.11 / 0.7085 | -9.5 |
| #face=coupled;mode=initial_or_trailing_max;mult=3.0;win=14 | 0.0611 | True | False | False | False | 21.87 / 0.8189 | -42.18 |
| be79d150#face=coupled;mode=initial_only;mult=3.5;win=14 | 24.3913 | True | False | True | False | 13.7 / 0.5962 | 42.28 |
| f94fcf5e#face=coupled;mode=trailing_only;mult=3.5;win=14 | 2.1436 | True | False | True | False | 12.98 / 0.4869 | 34.74 |
| #face=coupled;mode=initial_or_trailing_max;mult=3.5;win=14 | 9.4297 | True | False | True | False | 14.1 / 0.5719 | 42.67 |
| ed78accc#face=coupled;mode=initial_only;mult=4.0;win=14 | 1.4197 | True | False | True | False | 9.03 / 0.3585 | 20.71 |
| 8c76881d#face=coupled;mode=trailing_only;mult=4.0;win=14 | 1.6191 | True | False | True | False | 10.45 / 0.4257 | 25.87 |
| #face=coupled;mode=initial_or_trailing_max;mult=4.0;win=14 | 2.1279 | True | False | True | False | 11.59 / 0.4817 | 33.21 |
| 3c653c00#face=coupled;mode=initial_only;mult=5.0;win=14 | 1.199 | False | False | True | False | 4.77 / 0.2181 | 11.08 |
| 768d7546#face=coupled;mode=trailing_only;mult=5.0;win=14 | 1.0962 | False | False | True | False | 2.9 / 0.1373 | 6.15 |
| #face=coupled;mode=initial_or_trailing_max;mult=5.0;win=14 | 1.2325 | False | False | True | False | 4.71 / 0.2367 | 11.93 |
| 5303ed07#face=coupled;mode=initial_only;mult=2.0;win=21 | 0.4293 | True | True | True | True | 36.64 / 1.4336 | 6.8 |
| 46d8fc2d#face=coupled;mode=trailing_only;mult=2.0;win=21 | 0.4535 | True | True | True | True | 43.34 / 0.6433 | 15.26 |
| #face=coupled;mode=initial_or_trailing_max;mult=2.0;win=21 | 0.1224 | True | True | False | False | 45.2 / 0.7766 | -12.01 |
| 8b8a0db7#face=coupled;mode=initial_only;mult=2.5;win=21 | 0.3449 | True | False | False | False | 27.91 / 1.0795 | -8.43 |
| 053fd825#face=coupled;mode=trailing_only;mult=2.5;win=21 | 0.2382 | True | False | False | False | 35.3 / 0.9145 | -10.32 |
| #face=coupled;mode=initial_or_trailing_max;mult=2.5;win=21 | 0.0159 | True | False | False | False | 35.12 / 0.7346 | -34.33 |
| 0ce615c1#face=coupled;mode=initial_only;mult=3.0;win=21 | 0.6244 | True | False | False | False | 16.58 / 0.7155 | -0.58 |
| d70d2f7b#face=coupled;mode=trailing_only;mult=3.0;win=21 | 0.5094 | True | False | False | False | 26.75 / 0.6794 | 2.5 |
| #face=coupled;mode=initial_or_trailing_max;mult=3.0;win=21 | 0.1804 | True | False | False | False | 27.15 / 0.7201 | -24.04 |
| aaa4a0e4#face=coupled;mode=initial_only;mult=3.5;win=21 | 4.6947 | True | False | True | False | 15.05 / 0.6193 | 43.35 |
| 7df9f7ae#face=coupled;mode=trailing_only;mult=3.5;win=21 | 5.5114 | True | False | True | False | 17.18 / 0.5631 | 45.66 |
| #face=coupled;mode=initial_or_trailing_max;mult=3.5;win=21 | 1.1001 | True | False | True | False | 18.63 / 0.6671 | 22.0 |
| 8ef05545#face=coupled;mode=initial_only;mult=4.0;win=21 | 10.94 | True | False | True | False | 13.43 / 0.574 | 42.01 |
| 66c4f0fd#face=coupled;mode=trailing_only;mult=4.0;win=21 | 1.8022 | True | False | True | False | 12.94 / 0.458 | 31.05 |
| #face=coupled;mode=initial_or_trailing_max;mult=4.0;win=21 | 4.2442 | True | False | True | False | 14.11 / 0.5463 | 42.19 |
| 01d118b8#face=coupled;mode=initial_only;mult=5.0;win=21 | 1.4099 | True | False | True | False | 6.42 / 0.3175 | 17.89 |
| d800ad82#face=coupled;mode=trailing_only;mult=5.0;win=21 | 1.2823 | True | False | True | False | 5.01 / 0.2615 | 13.52 |
| #face=coupled;mode=initial_or_trailing_max;mult=5.0;win=21 | 1.6498 | True | False | True | False | 6.89 / 0.3787 | 22.8 |
| 24390364#face=coupled;mode=initial_only;mult=2.0;win=30 | 0.3814 | True | True | True | True | 38.8 / 1.2865 | 5.36 |
| aa12323f#face=coupled;mode=trailing_only;mult=2.0;win=30 | 0.0308 | True | True | False | False | 47.52 / 0.6921 | -20.12 |
| #face=coupled;mode=initial_or_trailing_max;mult=2.0;win=30 | 0.1419 | True | False | False | False | 48.07 / 0.6666 | -7.07 |
| 640d03a5#face=coupled;mode=initial_only;mult=2.5;win=30 | 0.3807 | True | False | False | False | 31.95 / 1.1926 | -1.54 |
| c5a9881e#face=coupled;mode=trailing_only;mult=2.5;win=30 | 2.6192 | True | True | True | True | 38.2 / 0.5669 | 63.02 |
| #face=coupled;mode=initial_or_trailing_max;mult=2.5;win=30 | 1.9419 | True | True | True | True | 39.09 / 0.5575 | 58.88 |
| db08c8b4#face=coupled;mode=initial_only;mult=3.0;win=30 | 0.3345 | True | False | False | False | 27.15 / 1.0531 | -10.04 |
| 9869d4c5#face=coupled;mode=trailing_only;mult=3.0;win=30 | 0.201 | True | False | False | False | 34.72 / 0.871 | -14.44 |
| #face=coupled;mode=initial_or_trailing_max;mult=3.0;win=30 | 0.0019 | True | False | False | False | 34.51 / 0.7468 | -36.67 |
| 7121fd77#face=coupled;mode=initial_only;mult=3.5;win=30 | 0.4844 | True | False | False | False | 17.21 / 0.729 | -8.72 |
| 1175733e#face=coupled;mode=trailing_only;mult=3.5;win=30 | 2.5817 | True | False | True | False | 26.57 / 0.6181 | 51.21 |
| #face=coupled;mode=initial_or_trailing_max;mult=3.5;win=30 | 0.0724 | True | False | False | False | 28.78 / 0.7933 | -33.97 |
| 380b99f2#face=coupled;mode=initial_only;mult=4.0;win=30 | 3.5978 | True | False | True | False | 15.22 / 0.6272 | 42.69 |
| 629ac1e7#face=coupled;mode=trailing_only;mult=4.0;win=30 | 0.5915 | True | False | False | False | 20.65 / 0.6888 | 1.56 |
| #face=coupled;mode=initial_or_trailing_max;mult=4.0;win=30 | 0.0478 | True | False | False | False | 21.92 / 0.7738 | -43.69 |
| 7f115379#face=coupled;mode=initial_only;mult=5.0;win=30 | 1.5141 | True | False | True | False | 7.44 / 0.3509 | 21.01 |
| 419cf68c#face=coupled;mode=trailing_only;mult=5.0;win=30 | 1.2699 | True | False | True | False | 5.58 / 0.2666 | 13.78 |
| #face=coupled;mode=initial_or_trailing_max;mult=5.0;win=30 | 1.4653 | True | False | True | False | 6.98 / 0.3409 | 19.6 |
| upled_filter14;mode=initial_or_trailing_max;mult=2.0;win=7 | 0.2935 | True | False | False | False | 33.25 / 1.0046 | -7.41 |
| upled_filter14;mode=initial_or_trailing_max;mult=2.5;win=7 | 0.7114 | True | False | True | False | 21.97 / 0.6794 | 9.53 |
| upled_filter14;mode=initial_or_trailing_max;mult=3.0;win=7 | 11.9357 | True | False | True | False | 16.61 / 0.6008 | 45.19 |
| upled_filter14;mode=initial_or_trailing_max;mult=3.5;win=7 | 1.8081 | True | False | True | False | 11.37 / 0.4545 | 29.56 |
| upled_filter14;mode=initial_or_trailing_max;mult=4.0;win=7 | 1.4459 | True | False | True | False | 10.23 / 0.3913 | 22.46 |
| upled_filter14;mode=initial_or_trailing_max;mult=5.0;win=7 | 1.1256 | True | False | True | False | 5.33 / 0.2108 | 9.49 |
| pled_filter14;mode=initial_or_trailing_max;mult=2.0;win=10 | 0.3549 | True | True | False | False | 38.17 / 1.2109 | 2.63 |
| pled_filter14;mode=initial_or_trailing_max;mult=2.5;win=10 | 0.0522 | True | False | False | False | 24.93 / 0.7957 | -40.16 |
| pled_filter14;mode=initial_or_trailing_max;mult=3.0;win=10 | 5.3814 | True | False | True | False | 16.83 / 0.6127 | 45.29 |
| pled_filter14;mode=initial_or_trailing_max;mult=3.5;win=10 | 2.6357 | True | False | True | False | 12.13 / 0.5104 | 37.02 |
| pled_filter14;mode=initial_or_trailing_max;mult=4.0;win=10 | 1.7289 | True | False | True | False | 10.78 / 0.4424 | 27.89 |
| pled_filter14;mode=initial_or_trailing_max;mult=5.0;win=10 | 1.1001 | False | False | True | False | 3.07 / 0.1406 | 6.44 |
| pled_filter14;mode=initial_or_trailing_max;mult=2.0;win=21 | 0.1224 | True | True | False | False | 45.2 / 0.7766 | -12.01 |
| pled_filter14;mode=initial_or_trailing_max;mult=2.5;win=21 | 0.0159 | True | False | False | False | 35.12 / 0.7346 | -34.33 |
| pled_filter14;mode=initial_or_trailing_max;mult=3.0;win=21 | 0.1804 | True | False | False | False | 27.15 / 0.7201 | -24.04 |
| pled_filter14;mode=initial_or_trailing_max;mult=3.5;win=21 | 1.1001 | True | False | True | False | 18.63 / 0.6671 | 22.0 |
| pled_filter14;mode=initial_or_trailing_max;mult=4.0;win=21 | 4.2442 | True | False | True | False | 14.11 / 0.5463 | 42.19 |
| pled_filter14;mode=initial_or_trailing_max;mult=5.0;win=21 | 1.6498 | True | False | True | False | 6.89 / 0.3787 | 22.8 |
| pled_filter14;mode=initial_or_trailing_max;mult=2.0;win=30 | 0.1419 | True | False | False | False | 48.07 / 0.6666 | -7.07 |
| pled_filter14;mode=initial_or_trailing_max;mult=2.5;win=30 | 1.9419 | True | True | True | True | 39.09 / 0.5575 | 58.88 |
| pled_filter14;mode=initial_or_trailing_max;mult=3.0;win=30 | 0.0019 | True | False | False | False | 34.51 / 0.7468 | -36.67 |
| pled_filter14;mode=initial_or_trailing_max;mult=3.5;win=30 | 0.0724 | True | False | False | False | 28.78 / 0.7933 | -33.97 |
| pled_filter14;mode=initial_or_trailing_max;mult=4.0;win=30 | 0.0478 | True | False | False | False | 21.92 / 0.7738 | -43.69 |
| pled_filter14;mode=initial_or_trailing_max;mult=5.0;win=30 | 1.4653 | True | False | True | False | 6.98 / 0.3409 | 19.6 |

### leg4_allocator_vs_same_scheme_baseline 逐格（最多 400 行）

| cell | λ(OOS) | 原尺仅OOS | 案A双窗 | 案B缩放 | 新尺A∧B | 原始OOS: dd改善pp/SharpeΔ | 缩放后OOS: dd改善pp |
|---|---|---|---|---|---|---|---|
| 3e652b9#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.2;mom=0.5 | 0.9908 | False | False | False | False | -0.66 / -0.016 | -0.99 |
| 3418d8f#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.3;mom=0.4 | 0.9846 | False | False | False | False | -0.37 / -0.0155 | -0.92 |
| 3c3c1d0#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.4;mom=0.3 | 0.9769 | False | False | False | False | -0.23 / -0.0188 | -1.06 |
| cd43a58#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.2;mom=0.4 | 1.0001 | False | False | False | False | -0.42 / -0.0062 | -0.41 |
| 0fa667c#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.3;mom=0.3 | 0.9923 | False | False | False | False | -0.18 / -0.0075 | -0.46 |
| c12f530#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.4;mom=0.2 | 0.9847 | False | False | False | False | -0.08 / -0.011 | -0.62 |
| 8a8f852#allocator=ALC-THREELAYER-001;eq=0.5;iv=0.2;mom=0.3 | 1.0092 | False | False | False | False | -0.18 / 0.0028 | 0.15 |
| 457b270#allocator=ALC-THREELAYER-001;eq=0.5;iv=0.4;mom=0.1 | 0.9924 | False | False | False | False | 0.07 / -0.0037 | -0.2 |
| 786e6b5#allocator=ALC-THREELAYER-001;eq=0.6;iv=0.2;mom=0.2 | 1.0181 | False | False | False | False | 0.05 / 0.0113 | 0.68 |
| 327aceb#allocator=ALC-THREELAYER-001;eq=0.6;iv=0.3;mom=0.1 | 1.008 | False | False | False | False | 0.17 / 0.0074 | 0.46 |
| 8ed6925c#allocator=ALC-THREELAYER-001;iv_lookback=30 | 1.4325 | False | False | True | False | 0.22 / 0.1666 | 13.32 |
| a6eac444#allocator=ALC-THREELAYER-001;iv_lookback=90 | 0.8954 | False | False | False | False | -0.04 / -0.1022 | -3.9 |
| 0ffe00fc#allocator=ALC-THREELAYER-001;iv_lookback=120 | 0.8576 | False | False | False | False | -1.74 / -0.1716 | -7.08 |
| 8bc2d572#allocator=ALC-THREELAYER-001;mom_lookback=10 | 1.0108 | False | False | False | False | 0.39 / 0.0097 | 0.77 |
| a555eb53#allocator=ALC-THREELAYER-001;mom_lookback=40 | 0.9903 | False | False | False | False | 0.1 / -0.0051 | -0.25 |
| f85b492d#allocator=ALC-THREELAYER-001;mom_lookback=60 | 0.9897 | False | False | False | False | 0.16 / -0.0055 | -0.21 |
| 25eaa062#allocator=ALC-THREELAYER-001;cap_frac=0.25 | 1.0 | False | False | False | False | 0.0 / 0.0 | 0.0 |
| 185cbdaf#allocator=ALC-THREELAYER-001;cap_frac=0.75 | 1.0 | False | False | False | False | 0.0 / 0.0 | 0.0 |
| 149f299c#allocator=ALC-THREELAYER-001;cap_frac=1.0 | 1.0 | False | False | False | False | 0.0 / 0.0 | 0.0 |
| 6faf9af3#allocator=ALC-RK08-001;iv_lookback=20 | 1.5324 | False | False | True | False | 0.9 / 0.2858 | 16.45 |
| 4ffc8ffb#allocator=ALC-RK08-001;iv_lookback=30 | 1.53 | False | False | True | False | 0.76 / 0.2949 | 16.25 |
| 47a73062#allocator=ALC-RK08-001;iv_lookback=40 | 1.3469 | False | False | True | False | 0.42 / 0.2307 | 11.25 |
| 51fe0966#allocator=ALC-RK08-001;iv_lookback=90 | 0.8863 | False | False | False | False | 0.24 / -0.1964 | -3.96 |
| d5703fd4#allocator=ALC-RK08-001;iv_lookback=120 | 0.8693 | False | False | False | False | -0.92 / -0.2332 | -5.78 |
| 25fd#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.3, 0.7] | 0.9928 | False | False | False | False | -0.04 / -0.0054 | -0.3 |
| c4a3#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.3, 0.7] | 0.9835 | False | False | False | False | -0.12 / -0.0128 | -0.71 |
| 2767#allocator=ALC-PA015-001;down=[0.7, 0.3];up=[0.4, 0.6] | 0.979 | False | False | False | False | 0.2 / -0.0155 | -0.56 |
| 58c3#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.4, 0.6] | 0.9716 | False | False | False | False | 0.17 / -0.0212 | -0.86 |
| 45a2#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.4, 0.6] | 0.9624 | False | False | False | False | 0.11 / -0.0289 | -1.25 |
| 55df#allocator=ALC-PA015-001;down=[0.7, 0.3];up=[0.5, 0.5] | 0.9575 | False | False | False | False | 0.35 / -0.0331 | -1.19 |
| e26b#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.5, 0.5] | 0.9502 | False | False | False | False | 0.32 / -0.0392 | -1.48 |
| fecb#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.5, 0.5] | 0.9413 | False | False | False | False | 0.28 / -0.047 | -1.86 |
| 270c4eb9#allocator=ALC-PA015-001;mom_lookback=10 | 1.0127 | False | False | False | False | 1.05 / 0.0155 | 1.5 |
| 29d0c949#allocator=ALC-PA015-001;mom_lookback=40 | 0.9683 | False | False | False | False | 0.76 / -0.014 | -0.38 |
| 930a0512#allocator=ALC-SIG131-001;cap_frac=0.0 | 1.0 | False | False | False | False | 0.0 / 0.0 | 0.0 |
| 136ff88f#allocator=ALC-SIG131-001;cap_frac=0.25 | 1.0 | False | False | False | False | 0.0 / 0.0 | 0.0 |
| 90251a15#allocator=ALC-SIG131-001;cap_frac=0.75 | 1.0 | False | False | False | False | 0.0 / 0.0 | 0.0 |
| 8aee97cd#allocator=ALC-SIG131-001;cap_frac=1.0 | 1.0 | False | False | False | False | 0.0 / 0.0 | 0.0 |
| 736f0e19#allocator=ALC-SIG131-001;cap_frac=1.5 | 1.0 | False | False | False | False | 0.0 / 0.0 | 0.0 |

