---
ttl: task_bound
created: 2026-09-23
---

# 夜窗数据两件·执行回执（st-nightdata-20260923，2026-09-23 17:50 执行）

> Max 改令：夜写阶段由 02:00-05:00 窗提前至 09-23 17:50 执行（收盘链已过、活小幂等、离 02:30 夜班更远）；验收口径不变。准备阶段记录见同目录白班报告+夜班卡。

## 件1 ✅ ETF60min 深史全量回补（通道C）

**命令**：`python scripts/data/backfill_etf60min_depth.py --execute`（退出码 0，耗时 99s，日志=`.runtime/sessions/st-nightdata-20260923/staging/backfill_run.log`）

**结果：目标缺格=88,273，写入=88,273，复验剩余=0（缺格清零硬门通过）。**

前后覆盖矩阵（逐日 60min 覆盖与 1min 源精确拉齐，bar=只数×4）：

| 日 | 60min 前只数 | 后只数 | 后 bar | 1min 源只数 |
|---|---|---|---|---|
| 2026-07-01~07-03 | 31 | 1,575-1,579 | 6,300-6,316 | 1,575-1,579 |
| 2026-07-06~07-10 | 31 | 1,581-1,594 | 6,324-6,376 | 1,581-1,594 |
| 2026-07-13~07-17 | 31 | 1,595-1,601 | 6,380-6,404 | 1,595-1,601 |
| 2023-06-05 | 0 | 759 | 3,036 | 759 |
| 2026-07-28 | 545 | 1,607 | 6,428 | 1,607 |

**如实标注**：
1. 07-01~07-17 各日回补前原有 31 只/124 bar 考试子集幸存（非全零；白班初版"07-01~07-07 全零"系 tail 截断显示伪影，已勘误）。
2. **残余缺口=159915@2021-02-08 共 4 bar**：通道D 探针实证 XMiniQmt 沙箱活着且 xtquant 连通（sim 实例，近月 1h 可下 12 行），但 2021 深史 0 行不可得——需第三方历史K线源选型，未硬补。
3. 写入形态：data_source 落表默认 'bdpan'（全表同形态）；ReplacingMergeTree 同键替换，重跑幂等。

## 件2 ✅ financial_indicator 分区级 OPTIMIZE FINAL（Max 已批）

**命令**：逐分区 `OPTIMIZE TABLE c3_fundamental.financial_indicator PARTITION '<yyyymm>' FINAL`（5 个，各 0.0-0.1s；未触整表、零 DELETE）

**前后对账（全部 MATCH）**：

| 指标 | 执行前 | 执行后 | 判定 |
|---|---|---|---|
| 伪影普查（raw 同键>1） | 5 分区 2,518 键/2,518 盈余（202503:504/202506:504/202509:502/202512:504/202603:504） | **0 键** | ✅ 清零 |
| raw 总行数 | 388,849 | 386,331 | ✅ 恰降 2,518=盈余合计 |
| FINAL 总行数 | 386,331 | 386,331 | ✅ 分毫未动（业务数据零伤） |

## 交付物清单

| 件 | 落点 |
|---|---|
| 回补 CLI（本班新建+入队） | scripts/data/backfill_etf60min_depth.py（q-20260923-st-nightdata-20260923-0001） |
| 本回执 | docs/_working/datatail/2026-09-23-night-run-report.md |
| 执行日志 | .runtime/sessions/st-nightdata-20260923/staging/backfill_run.log |

**待裁/移交**：①02:05 automation 已按 Max 令删除（执行提前完成）②159915@2021-02-08 4 bar 待第三方源选型 ③known_data_gaps `kline_etf_60min_depth_windows` 条目 resolution_actual 回写待数据线车道（回补已落地，缺口仅余通道D 残余 4 bar）。
