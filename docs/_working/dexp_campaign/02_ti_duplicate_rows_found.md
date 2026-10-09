---
ttl: task_bound
---

# 【随手挖出的非本战役缺陷】technical_indicator 非 FINAL 读同键多行（2026-10-09）

> 本件不是 D 盘清账的一部分，是分诊过程中撞上的**读数正确性**问题。
> 三条判据我都自己读到/跑过（不是转述车道结论）。**处置属业务资产门位，只呈报不自裁。**

## 1. 三条自证

**① 表引擎与排序键（`system.tables` 直读，我本人查询）**

```sql
SELECT engine, sorting_key, primary_key, partition_key FROM system.tables
WHERE database='c1_market' AND name='technical_indicator';
-- ReplacingMergeTree | symbol, period, trade_time | symbol, period, trade_time | (period, toYYYYMM(trade_date))
```

⇒ 排序键里**没有版本列**。`ReplacingMergeTree` 无版本参数时只在**合并时**按"后写胜出"折叠；
合并未发生前，重复版本同时可见。

**② 重复密度（我自己跑的查询，2026-09-15 单日）**

```sql
SELECT count() AS n_keys, countIf(cnt>1) AS n_dup, max(cnt) AS max_rows_per_key
FROM (SELECT symbol, period, trade_time, count() AS cnt
      FROM c1_market.technical_indicator WHERE trade_date='2026-09-15'
      GROUP BY symbol, period, trade_time);
-- n_keys=1,787,374   n_dup=1,671,859 (93.5%)   max_rows_per_key=5
```

⇒ 该日 **93.5% 的键有重复行，单键最多 5 行**。

**③ 读取侧确实不去重（文件行级）**

- `src/zephyr/factor/indicator_reader.py:108`
  `sql = f"SELECT {select_cols} FROM {_TABLE} WHERE ... ORDER BY trade_time"`
  —— **无 `FINAL`、无 `GROUP BY`、无 `argMax`**，且函数返回值直接给 RangeIndex DataFrame
  （docstring 自称"PIT 安全读取技术指标宽表"，只防前视不防重）。
- 下游仅在 `src/zephyr/factor/core/evaluation/backtest.py:211` 与 `:313` 有
  `drop_duplicates(subset=["symbol","trade_date"], keep="last")`——
  **去重键比表键粗**（丢了 `period` 与 `trade_time`），且只覆盖这两条路径。

## 2. 影响面（诚实分级，不夸大）

- **已证**：`read_indicator()` 的原始返回在 2026-09 区间**会**含重复 bar（因①②③三项俱全）。
- **未证**：我没有逐个审计 `read_indicator` 的全部消费者，故**不能断言"所有回测结果已错"**。
  判为"视消费者而定"：走 backtest.py 那两条路径的被粗粒度去重掩盖了一部分，
  其余消费者（因子评测/面板构建/指标对拍）若直接按行消费即受影响。
- **同时是磁盘问题**：车道 `lane-chsize` 估 9 月 TI 内有 **25-30 GiB 重复行版本**
  （`1min` 1.682 / `5min` 1.688 / `30min` 2.438 / `60min` 3.52 版本/键，其 `uniqExact`
  触到 5.33 GiB 服务端上限故为估计值）。**这条与我"160G 压缩"的错觉无关**，见 00 号文 §0。

## 3. 疑似诱因（待查，本件未定因）

`system.tables` 里存在 `technical_indicator_hugebk_20261008`（0.24 GiB）与
三张 `*_preeng_backup_20261007`（kline daily/weekly/monthly hfq，共 0.40 GiB）
⇒ 10-07/10-08 有过一次改表/重灌动作。**重复版本极可能是"重灌写新 parts 而旧 parts 未清"**，
与本仓既有教训 [[repolluting-incremental-leg-beats-one-time-recompute]]（重算换名后增量腿仍写旧口径
＋ReplacingMergeTree 无版本列 ⇒ 视图旧行覆盖修正行）**同型**。定因需查写入侧，本件未做。

## 4. 可选处置（**全部属业务资产门位，我不自裁**）

| 方案 | 动作 | 代价/风险 |
|---|---|---|
| A 读取侧治本 | `indicator_reader.py:108` 加 `FINAL`，或改 `GROUP BY (symbol,period,trade_time)` 取终值 | FINAL 在大表上有显著性能代价（本表 220.93 GiB）；改判据须配套测试 |
| B 存储侧治本 | 给 ORDER BY 补版本列 → 需**重建表**（新表+迁移+改名） | 生产库结构动作，族内须对拍（参见 [[hfq-table-family-cascade]]） |
| C 手工合并 | 对受影响分区 `ALTER TABLE ... MATERIALIZE TTL`/`OPTIMIZE ... FINAL` | 是 DDL；`§2A 原则3` 禁 DELETE/TRUNCATE/DROP PARTITION 通道 |
| D 只做观测 | 先加一条"同键多行"哨兵门，量化到底有多少消费者真受影响 | 最便宜，且把"是否已污染历史结论"变成可测问题 |

**我的建议序**＝先 D（零风险定量），再据结果由 Owner 在 A/B 之间定。
**未做任何一项**——本战役红线与宪法 §5 都把它挡在门位外。
