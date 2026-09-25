---
ttl: task_bound
---

# 去重改造等价性判据书（T0 200 格对拍 · st-ddup-20260925）

> 判据：新旧引擎同参重跑（T0 标定 200 格：--stage t0 --n-samples 200 --seed 20260915 --start 2019-01-04 --end 2025-09-09），manifest 逐格一致或统计量容差 ≤1e-5（Owner 通宵令原文）。**裁定：PASS。**

## 对拍证据

| 项 | 旧引擎基线 | 新引擎重跑 |
|---|---|---|
| 运行目录 | data/strategy_intake/grid_20260925-232032 | data/strategy_intake/grid_20260926-021530 |
| 发车/完成 | 09-25 23:20 → 09-26 02:35（195 min） | 09-26 02:15 → 09-26 02:50（35 min，**5.6x**） |
| 引擎代码 | HEAD 62898892 前盘面态（进程 23:20 装载旧码） | HEAD 62898892（掩码向量化+LRU 缓存/单趟合并/多档标量线） |
| evaluated/dead | 200 / 0 | 200 / 0 |
| 数据快照 | CH 2026-09-25 18:00 灌水后（下一灌水 09-26 18:00 前无漂移） | 同左（两跑同窗同数据） |

- manifest：recipe_id 集合全同（seed/schema 同源）；sharpe/ann_return/max_drawdown/avg_turnover/net_days/degraded 全列达标（舍入列逐位一致）。
- net_returns.parquet：200 序列 × 1622 交易日全量逐元素比较，**max|Δ|=4.441e-16 = 1 个 float64 ULP**（比 1e-5 容差低 10 个数量级；源自浮点归约次序的单比特噪声级差异，非语义分歧）。
- 先行证据：真实库掩码逐位对拍 PASS（hs300 337 列窗 2024-01-02..2025-09-09，sealed_up 739/sealed_down 190 全等）；合成面板 run_backtest_full/net_returns_by_tiers/nets_by_tier 注入三探针逐位一致；10 测试套件 114 例绿（新增 12 例守护）。

## 提速实测（同机同负载：旧 T1 在跑+t0_rule_engine+reexam 并发）

- 单格均值：旧 ~58s/格（195min/200）→ 新 ~10.5s/格（35min/200）≈ **5.6x**（与 hotspot_census §二·补 的 8.6x 上修口径同向； contention 差异解释残差）。
- 3,700 格 T1 预估：单进程 ~11-14h（受 CPU 争用浮动）。

## 判据执行链

1. 掩码重复键语义严格复刻：up 取 min / down 取 max（OR 累积=原逐行 any-row-seals 语义），C4 对拍用例守护（test_c4_limit_gate）。
2. 三处去重全部"替代式"施工（内收声明在文件头），原函数签名/语义零变化。
3. 复核命令：`python .runtime/tmp/ddup/compare_grid_runs.py <old_dir> <new_dir>`（临时探针件，判据入册后可转正式证尺）。

（st-ddup-20260925 · 2026-09-26 02:52）
