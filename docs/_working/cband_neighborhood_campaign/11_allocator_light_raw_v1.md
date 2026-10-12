---
ttl: task_bound
campaign: cband-20261012
generated_by: scripts/backtest/fexam/cband_grid.py（机生禁手改）
---

# cband_allocator_raw（v1，机生）

- 生成：2026-10-11 22:04:41.228006+00:00｜读数等级：**未折减（pre-deflation）；轻面读数——与在册批4 引擎面不同面，禁混排同表直读**
- 预登记册：docs/_working/cband_neighborhood_campaign/01_prereg_axis_sets_v1.yaml｜partial=False｜selftest=False
- 计数：{'rows': 44, 'ok': 44, 'error_rows': 0}
- 速率标定：{'per_cell_seconds_mean': 0.976, 'n_cells_timed': 44}
- 装置：{"face": "exit_sim.simulate(stop_enabled=False) 消费分配器权重帧（无 PIT/剔ST/滑点/冲击/参与率，佣金同源双边）", "param_faces_used": ["three_layer_weights(w_eq/w_iv/w_mom)", "pa015_weights(up_w_iv/up_w_mom/down_w_iv/down_w_mom)"], "composite_columns_n": 24, "columns_source": "docs/_working/fexam/allocator_shadow_report_v1.yaml", "windows": {"run": ["2018-01-02", "2026-09-30"], "is": ["2018-01-02", "2025-09-30"], "oos": ["2025-10-09", "2026-09-30"]}, "regime_source": "sma200_default", "regime_delta_vs_register_v1": "在册 v1 标 regime_table+sma_fallback；本班跑现默认 SMA200 帘子 ⇒ ALC-PA015 行不得当同面重跑读", "priceable_mask": {"masked_columns": 1, "months_with_masked_target": 21, "note": "秩仍在全截面（含不可定价列）上算，只在目标权重帧里剔除无收盘价的标的＝与在册引擎面 flat.dropna(subset=['close']) 同语义；被剔份额留为现金（轻面无杠杆，与 leg② 同装置）"}}

| cell | 轴 | OOS Sharpe | OOS MaxDD | IS Sharpe | ΔOOS Sharpe vs nostop | t vs nostop | 秒 | 状态 |
|---|---|---|---|---|---|---|---|---|
| 83e652b9#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.2;mom=0.5 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.3, "iv": 0.2, "mom": 0.5} | -0.359 | -53.81% | -0.218 | - | - | 1.2016 | ok |
| d3418d8f#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.3;mom=0.4 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.3, "iv": 0.3, "mom": 0.4} | -0.359 | -53.52% | -0.216 | - | - | 1.0371 | ok |
| 33c3c1d0#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.4;mom=0.3 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.3, "iv": 0.4, "mom": 0.3} | -0.362 | -53.38% | -0.211 | - | - | 1.1002 | ok |
| 8cd43a58#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.2;mom=0.4 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.4, "iv": 0.2, "mom": 0.4} | -0.350 | -53.56% | -0.224 | - | - | 1.0993 | ok |
| 40fa667c#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.3;mom=0.3 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.4, "iv": 0.3, "mom": 0.3} | -0.351 | -53.33% | -0.221 | - | - | 1.1009 | ok |
| ac12f530#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.4;mom=0.2 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.4, "iv": 0.4, "mom": 0.2} | -0.354 | -53.22% | -0.216 | - | - | 1.1168 | ok |
| 28a8f852#allocator=ALC-THREELAYER-001;eq=0.5;iv=0.2;mom=0.3 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.5, "iv": 0.2, "mom": 0.3} | -0.341 | -53.33% | -0.229 | - | - | 1.1006 | ok |
| a7bddf22#allocator=ALC-THREELAYER-001;eq=0.5;iv=0.3;mom=0.2 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.5, "iv": 0.3, "mom": 0.2} | -0.343 | -53.15% | -0.226 | - | - | 1.1609 | ok |
| 5457b270#allocator=ALC-THREELAYER-001;eq=0.5;iv=0.4;mom=0.1 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.5, "iv": 0.4, "mom": 0.1} | -0.347 | -53.07% | -0.220 | - | - | 1.1201 | ok |
| e786e6b5#allocator=ALC-THREELAYER-001;eq=0.6;iv=0.2;mom=0.2 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.6, "iv": 0.2, "mom": 0.2} | -0.332 | -53.10% | -0.234 | - | - | 1.1373 | ok |
| 5327aceb#allocator=ALC-THREELAYER-001;eq=0.6;iv=0.3;mom=0.1 | {"allocator": "ALC-THREELAYER-001", "kind": "simplex", "eq": 0.6, "iv": 0.3, "mom": 0.1} | -0.336 | -52.97% | -0.230 | - | - | 1.098 | ok |
| 8ed6925c#allocator=ALC-THREELAYER-001;iv_lookback=30 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "iv_lookback": 30} | -0.177 | -52.93% | -0.266 | - | - | 1.0461 | ok |
| a6eac444#allocator=ALC-THREELAYER-001;iv_lookback=90 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "iv_lookback": 90} | -0.446 | -53.19% | -0.160 | - | - | 1.1037 | ok |
| 0ffe00fc#allocator=ALC-THREELAYER-001;iv_lookback=120 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "iv_lookback": 120} | -0.515 | -54.88% | -0.131 | - | - | 1.1068 | ok |
| 8bc2d572#allocator=ALC-THREELAYER-001;mom_lookback=10 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "mom_lookback": 10} | -0.334 | -52.76% | -0.225 | - | - | 1.105 | ok |
| a555eb53#allocator=ALC-THREELAYER-001;mom_lookback=40 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "mom_lookback": 40} | -0.349 | -53.05% | -0.232 | - | - | 1.051 | ok |
| f85b492d#allocator=ALC-THREELAYER-001;mom_lookback=60 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "mom_lookback": 60} | -0.349 | -52.99% | -0.231 | - | - | 0.9716 | ok |
| 25eaa062#allocator=ALC-THREELAYER-001;cap_frac=0.25 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "cap_frac": 0.25} | -0.343 | -53.15% | -0.226 | - | - | 1.1608 | ok |
| 185cbdaf#allocator=ALC-THREELAYER-001;cap_frac=0.75 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "cap_frac": 0.75} | -0.343 | -53.15% | -0.226 | - | - | 1.0585 | ok |
| 149f299c#allocator=ALC-THREELAYER-001;cap_frac=1.0 | {"allocator": "ALC-THREELAYER-001", "kind": "ofat", "cap_frac": 1.0} | -0.343 | -53.15% | -0.226 | - | - | 1.1125 | ok |
| 6faf9af3#allocator=ALC-RK08-001;iv_lookback=20 | {"allocator": "ALC-RK08-001", "kind": "ofat", "iv_lookback": 20} | -0.210 | -51.84% | -0.240 | - | - | 0.7933 | ok |
| 4ffc8ffb#allocator=ALC-RK08-001;iv_lookback=30 | {"allocator": "ALC-RK08-001", "kind": "ofat", "iv_lookback": 30} | -0.201 | -51.97% | -0.274 | - | - | 0.8004 | ok |
| 47a73062#allocator=ALC-RK08-001;iv_lookback=40 | {"allocator": "ALC-RK08-001", "kind": "ofat", "iv_lookback": 40} | -0.266 | -52.31% | -0.225 | - | - | 0.8911 | ok |
| d44d9a2b#allocator=ALC-RK08-001;iv_lookback=60 | {"allocator": "ALC-RK08-001", "kind": "ofat", "iv_lookback": 60} | -0.496 | -52.73% | -0.166 | - | - | 0.8341 | ok |
| 51fe0966#allocator=ALC-RK08-001;iv_lookback=90 | {"allocator": "ALC-RK08-001", "kind": "ofat", "iv_lookback": 90} | -0.693 | -52.49% | -0.046 | - | - | 0.8043 | ok |
| d5703fd4#allocator=ALC-RK08-001;iv_lookback=120 | {"allocator": "ALC-RK08-001", "kind": "ofat", "iv_lookback": 120} | -0.729 | -53.65% | -0.007 | - | - | 0.8887 | ok |
| 9592518f#allocator=ALC-PA015-001;down=[0.7, 0.3];up=[0.3, 0.7] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.3, 0.7], "down": [0.7, 0.3]} | -0.407 | -53.59% | -0.174 | - | - | 0.9904 | ok |
| 3d2c25fd#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.3, 0.7] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.3, 0.7], "down": [0.6, 0.4]} | -0.412 | -53.63% | -0.180 | - | - | 1.0843 | ok |
| 40a9c4a3#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.3, 0.7] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.3, 0.7], "down": [0.5, 0.5]} | -0.419 | -53.71% | -0.188 | - | - | 0.9424 | ok |
| 0ddf2767#allocator=ALC-PA015-001;down=[0.7, 0.3];up=[0.4, 0.6] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.4, 0.6], "down": [0.7, 0.3]} | -0.422 | -53.40% | -0.176 | - | - | 0.9961 | ok |
| 75e058c3#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.4, 0.6] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.4, 0.6], "down": [0.6, 0.4]} | -0.428 | -53.43% | -0.182 | - | - | 1.1247 | ok |
| 21f545a2#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.4, 0.6] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.4, 0.6], "down": [0.5, 0.5]} | -0.436 | -53.48% | -0.190 | - | - | 1.0292 | ok |
| a7af55df#allocator=ALC-PA015-001;down=[0.7, 0.3];up=[0.5, 0.5] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.5, 0.5], "down": [0.7, 0.3]} | -0.440 | -53.24% | -0.177 | - | - | 1.0595 | ok |
| cb8ce26b#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.5, 0.5] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.5, 0.5], "down": [0.6, 0.4]} | -0.446 | -53.27% | -0.184 | - | - | 1.0105 | ok |
| cc63fecb#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.5, 0.5] | {"allocator": "ALC-PA015-001", "kind": "split", "up": [0.5, 0.5], "down": [0.5, 0.5]} | -0.454 | -53.32% | -0.192 | - | - | 1.0767 | ok |
| 270c4eb9#allocator=ALC-PA015-001;mom_lookback=10 | {"allocator": "ALC-PA015-001", "kind": "ofat", "mom_lookback": 10} | -0.391 | -52.55% | -0.185 | - | - | 1.0753 | ok |
| 29d0c949#allocator=ALC-PA015-001;mom_lookback=40 | {"allocator": "ALC-PA015-001", "kind": "ofat", "mom_lookback": 40} | -0.421 | -52.83% | -0.203 | - | - | 1.104 | ok |
| 930a0512#allocator=ALC-SIG131-001;cap_frac=0.0 | {"allocator": "ALC-SIG131-001", "kind": "ofat", "cap_frac": 0.0} | -0.277 | -53.30% | -0.228 | - | - | 0.5914 | ok |
| 136ff88f#allocator=ALC-SIG131-001;cap_frac=0.25 | {"allocator": "ALC-SIG131-001", "kind": "ofat", "cap_frac": 0.25} | -0.277 | -53.30% | -0.228 | - | - | 0.5755 | ok |
| 1bd64b64#allocator=ALC-SIG131-001;cap_frac=0.5 | {"allocator": "ALC-SIG131-001", "kind": "ofat", "cap_frac": 0.5} | -0.277 | -53.30% | -0.228 | - | - | 0.7343 | ok |
| 90251a15#allocator=ALC-SIG131-001;cap_frac=0.75 | {"allocator": "ALC-SIG131-001", "kind": "ofat", "cap_frac": 0.75} | -0.277 | -53.30% | -0.228 | - | - | 0.7187 | ok |
| 8aee97cd#allocator=ALC-SIG131-001;cap_frac=1.0 | {"allocator": "ALC-SIG131-001", "kind": "ofat", "cap_frac": 1.0} | -0.277 | -53.30% | -0.228 | - | - | 0.7077 | ok |
| 736f0e19#allocator=ALC-SIG131-001;cap_frac=1.5 | {"allocator": "ALC-SIG131-001", "kind": "ofat", "cap_frac": 1.5} | -0.277 | -53.30% | -0.228 | - | - | 0.7172 | ok |
| 9b7800e5#allocator=ALC-EQUAL-001 | {"allocator": "ALC-EQUAL-001", "kind": "reference"} | -0.277 | -53.31% | -0.226 | - | - | 0.4057 | ok |

## 证据量（各套基线臂 vs 同套邻域臂，配对 t；只报证据不判终胜负）

- ALC-THREELAYER-001：83e652b9#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.2;mom=0.5 → n=2122 ann_diff=-0.00071 t=-0.171
- ALC-THREELAYER-001：d3418d8f#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.3;mom=0.4 → n=2122 ann_diff=-0.00124 t=-0.5642
- ALC-THREELAYER-001：33c3c1d0#allocator=ALC-THREELAYER-001;eq=0.3;iv=0.4;mom=0.3 → n=2122 ann_diff=-0.002296 t=-0.648
- ALC-THREELAYER-001：8cd43a58#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.2;mom=0.4 → n=2122 ann_diff=-5.8e-05 t=-0.0159
- ALC-THREELAYER-001：40fa667c#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.3;mom=0.3 → n=2122 ann_diff=-0.000568 t=-0.539
- ALC-THREELAYER-001：ac12f530#allocator=ALC-THREELAYER-001;eq=0.4;iv=0.4;mom=0.2 → n=2122 ann_diff=-0.001646 t=-0.5651
- ALC-THREELAYER-001：28a8f852#allocator=ALC-THREELAYER-001;eq=0.5;iv=0.2;mom=0.3 → n=2122 ann_diff=0.000664 t=0.1854
- ALC-THREELAYER-001：5457b270#allocator=ALC-THREELAYER-001;eq=0.5;iv=0.4;mom=0.1 → n=2122 ann_diff=-0.001074 t=-0.4217
- ALC-THREELAYER-001：e786e6b5#allocator=ALC-THREELAYER-001;eq=0.6;iv=0.2;mom=0.2 → n=2122 ann_diff=0.001335 t=0.3432
- ALC-THREELAYER-001：5327aceb#allocator=ALC-THREELAYER-001;eq=0.6;iv=0.3;mom=0.1 → n=2122 ann_diff=0.000497 t=0.5079
- ALC-THREELAYER-001：8ed6925c#allocator=ALC-THREELAYER-001;iv_lookback=30 → n=2122 ann_diff=0.001142 t=0.0649
- ALC-THREELAYER-001：a6eac444#allocator=ALC-THREELAYER-001;iv_lookback=90 → n=2122 ann_diff=-0.010885 t=-0.7908
- ALC-THREELAYER-001：0ffe00fc#allocator=ALC-THREELAYER-001;iv_lookback=120 → n=2122 ann_diff=-0.014097 t=-0.8084
- ALC-THREELAYER-001：8bc2d572#allocator=ALC-THREELAYER-001;mom_lookback=10 → n=2122 ann_diff=-0.000759 t=-0.3402
- ALC-THREELAYER-001：a555eb53#allocator=ALC-THREELAYER-001;mom_lookback=40 → n=2122 ann_diff=0.001686 t=0.8279
- ALC-THREELAYER-001：f85b492d#allocator=ALC-THREELAYER-001;mom_lookback=60 → n=2122 ann_diff=0.00147 t=0.6801
- ALC-THREELAYER-001：25eaa062#allocator=ALC-THREELAYER-001;cap_frac=0.25 → n=2122 ann_diff=0.0 t=None
- ALC-THREELAYER-001：185cbdaf#allocator=ALC-THREELAYER-001;cap_frac=0.75 → n=2122 ann_diff=0.0 t=None
- ALC-THREELAYER-001：149f299c#allocator=ALC-THREELAYER-001;cap_frac=1.0 → n=2122 ann_diff=0.0 t=None
- ALC-RK08-001：6faf9af3#allocator=ALC-RK08-001;iv_lookback=20 → n=2122 ann_diff=0.003232 t=0.0955
- ALC-RK08-001：4ffc8ffb#allocator=ALC-RK08-001;iv_lookback=30 → n=2122 ann_diff=0.011221 t=0.3484
- ALC-RK08-001：47a73062#allocator=ALC-RK08-001;iv_lookback=40 → n=2122 ann_diff=0.002122 t=0.0736
- ALC-RK08-001：51fe0966#allocator=ALC-RK08-001;iv_lookback=90 → n=2122 ann_diff=-0.020963 t=-0.9057
- ALC-RK08-001：d5703fd4#allocator=ALC-RK08-001;iv_lookback=120 → n=2122 ann_diff=-0.029522 t=-0.8798
- ALC-PA015-001：3d2c25fd#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.3, 0.7] → n=2122 ann_diff=0.001899 t=1.2551
- ALC-PA015-001：40a9c4a3#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.3, 0.7] → n=2122 ann_diff=0.004086 t=1.264
- ALC-PA015-001：0ddf2767#allocator=ALC-PA015-001;down=[0.7, 0.3];up=[0.4, 0.6] → n=2122 ann_diff=0.001287 t=0.4627
- ALC-PA015-001：75e058c3#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.4, 0.6] → n=2122 ann_diff=0.003265 t=1.0271
- ALC-PA015-001：21f545a2#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.4, 0.6] → n=2122 ann_diff=0.005599 t=1.3059
- ALC-PA015-001：a7af55df#allocator=ALC-PA015-001;down=[0.7, 0.3];up=[0.5, 0.5] → n=2122 ann_diff=0.002722 t=0.5579
- ALC-PA015-001：cb8ce26b#allocator=ALC-PA015-001;down=[0.6, 0.4];up=[0.5, 0.5] → n=2122 ann_diff=0.00478 t=0.9348
- ALC-PA015-001：cc63fecb#allocator=ALC-PA015-001;down=[0.5, 0.5];up=[0.5, 0.5] → n=2122 ann_diff=0.007209 t=1.2292
- ALC-PA015-001：270c4eb9#allocator=ALC-PA015-001;mom_lookback=10 → n=2122 ann_diff=0.001776 t=0.2701
- ALC-PA015-001：29d0c949#allocator=ALC-PA015-001;mom_lookback=40 → n=2122 ann_diff=0.008202 t=1.2327
- ALC-SIG131-001：930a0512#allocator=ALC-SIG131-001;cap_frac=0.0 → n=2122 ann_diff=0.0 t=0.0
- ALC-SIG131-001：136ff88f#allocator=ALC-SIG131-001;cap_frac=0.25 → n=2122 ann_diff=0.0 t=None
- ALC-SIG131-001：90251a15#allocator=ALC-SIG131-001;cap_frac=0.75 → n=2122 ann_diff=0.0 t=None
- ALC-SIG131-001：8aee97cd#allocator=ALC-SIG131-001;cap_frac=1.0 → n=2122 ann_diff=0.0 t=None
- ALC-SIG131-001：736f0e19#allocator=ALC-SIG131-001;cap_frac=1.5 → n=2122 ann_diff=0.0 t=None
