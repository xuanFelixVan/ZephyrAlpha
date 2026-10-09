---
ttl: task_bound
---

# 【随手挖出的非本战役缺陷】technical_indicator 非 FINAL 读同键多行（2026-10-09）

> ## ⚠ 本件 §1-③ 的机制描述已被本班后续实测更正（2026-10-09 午后）
> 本文初版说"`indicator_reader.py:108` 无 FINAL 无去重"。**更准确的机制是**：
> 该 SQL 经 `ch_reader.query()`→`inject_final()`（`ch_reader.py:127,86-104`）**有条件**注入 FINAL，
> 条件是真源探针 `ch_writer.is_replacing_engine()`；而 `get_table_engine()`
> （`ch_writer.py:777-806`）**查询失败返回 `""` 且第 805 行无条件写入进程级缓存**
> ⇒ 探针一旦失败，该进程此后所有 ReplacingMergeTree 读**永久静默失去 FINAL**。
> 定量、消费者清单、影响面评估与 A/B 之外的第三条路，见 **`04_ti_dup_quantified.md`**。
> 本件保留作发现现场记录，不再单独引用其机制结论。

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

---

# 【折入】发现三定量全文（原拟单列为 04 号件，因新建件缺 creation_token 且 token 热册被他会话接管条目阻断，故折入本已跟踪件）

## 1. 产出①：重复率分布（按 period × 单日分片，非全表——全表会撞 CH 内存上限）

2026-09-15 实测（`--periods` 全 9 值）：

| period | 键数 | 重复键 | **dup_ratio** | **值分叉键** | **divergence_ratio** | 最大行数/键 | 最大版本数 | ingest_ts 可裁决 |
|---|---|---|---|---|---|---|---|---|
| 1min | 1,338,273 | 1,338,273 | **1.000** | 0 | 0.000 | 2 | 1 | — |
| 5min | 266,544 | 266,544 | **1.000** | 0 | 0.000 | 2 | 1 | — |
| 15min | 88,848 | 0 | 0.000 | 0 | 0.000 | 1 | 1 | — |
| 30min | 44,424 | 44,424 | **1.000** | 0 | 0.000 | 3 | 1 | — |
| 60min | 22,212 | 22,212 | **1.000** | 0 | 0.000 | 5 | 1 | — |
| 120min | 11,106 | 0 | 0.000 | 0 | 0.000 | 1 | 1 | — |
| **daily** | 5,557 | 2,367 | **0.422** | **1,650** | **0.697** | 3 | **3** | **2387/2387=1.0** |
| weekly | 5,205 | 13 | 0.003 | — | — | 2 | — | — |
| monthly | 5,205 | 0 | 0.000 | 0 | 0.000 | 1 | 1 | — |

**两个性质完全不同的缺陷，别混为一谈**：

- **A 型＝等值重复**（1/5/30/60min，9-01 与 9-15 两日 100% 重复，但 `divergence_ratio=0`）：
  多行内容逐列相同 ⇒ 只是行数/体积浪费＋非 FINAL 读会看到重复 bar。9-30 同日全为 0 ⇒ **会自愈**（合并掉了）。
- **B 型＝异值重复**（daily／weekly，且**2026 每一个采样日都在**）：
  同键多行**值不同** ⇒ 这才是读数正确性问题。

**B 型的面积（2026 全年 `period='daily'`，一次查询现算）**：

```
keys=998,357  dup_keys=539,276 (dup_ratio=0.540)  divergent_keys=383,272 (38.4% of all keys)
max_rows_per_key=6  rows_total=2,039,333（行膨胀 2.04×）
```

按月的 `daily` dup_ratio：202601 0.429／202602 0.428／202603 **1.000**／202604 0.323／
202605 0.426／202606 **0.763**／202607 0.425／202608 0.424／202609 0.421——**慢性、贯穿全年，不是 9 月局部事故**。

**关键正面发现（决定 A/B 取舍）**：表里**已有 `ingest_ts DateTime64(3,'UTC')` 列**，
且实测**能区分 100% 的异值重复键**（2387/2387、5486/5486，`value_fork_same_ts=0`）。
⇒ "按最新入库取一版"是**确定性**的，不需要重建表就能拿到正确答案。

## 2. 产出②：受影响消费者清单（车道 lane-consumers 枚举＋我逐条读源复核）

**经 `ch_reader`（受条件注入支配，探针失败即降级）**

| 调用面 | file:line | 自身去重 | 性质 |
|---|---|---|---|
| `read_indicator()` | `src/zephyr/factor/indicator_reader.py:108,110` | **NONE**（只 `dropna`） | 库函数 |
| ↳ `tech_factor_pipeline` | `:104`、`:143` | **NONE**，RangeIndex 直入 `synthesize()` | 因子流水线；**无生产 import 者**（该路未接线） |
| ↳ 演示脚本 | `scripts/backtest/indicator_consumption_demo.py:98` | **NONE** | 手工演示 |

**绕过 ch_reader 的裸 SQL（不受注入保护＝真暴露面）**

| 调用面 | file:line | 折叠方式 | 键是否等价 | 是否生产 |
|---|---|---|---|---|
| fexam 取数 | `scripts/backtest/fexam/ch_data.py:84,163-169` | `pivot_table(aggfunc="last")` | period 钉死 `daily`（`:161-162`）⇒ daily 下 `(symbol,trade_date)` **键等价**；但 "last" 取的是**行序最后**，非 `ingest_ts` 最新 | 研究/评测（扇出 `conditional_exam.py:412`／`ic_exam.py:221`／`strategy_exam.py:240`／`allocator_shadow.py:170`／`exit_simulator.py:106,114,422`／`gpu_ic/parity_test.py:120`） |
| lane C 公式挖掘 | `scripts/backtest/lane_c_formula_miner.py:70-76,369` | `drop_duplicates(["date","s"], keep="first")`（`:380`，`:374` 已钉 daily） | 同上键等价但 **keep="first"**（取最早版，方向反） | **已排定任务**：`scripts/tasks/register/register_factory_lane_c_task.ps1:17` → `run_factory_lane_c.ps1:36` |
| 仪表盘深度审计 | `src/zephyr/frontend/dashboard/api_server.py:2182`（遍历含 `:1990`） | 仅 `uniqExact`/`groupUniqArrayIf`（`:2170-2180`） | 行数取自 `system.parts sum(rows)`（`:4070-4071`）＝**含未合并重复**，报表口径与实读不一致 | **生产（dashboard）** |
| 其余 ch_reader 审计件 | `scripts/audit_technical_indicator_columns.py:49,72,111`；`scripts/data/audit_technical_indicator_coverage.py:73-81`；`scripts/data/night_probe.py:5-7,11-13` | **NONE** | — | 手动 |

**DDL 真源佐证**：`schemas/categories/market/market_technical_indicator.py:296-298,307-309`
= `ENGINE = ReplacingMergeTree`（**无版本参数**）`ORDER BY (symbol, period, trade_time)`；
`:36-38` 记 daily/weekly/monthly 的 `trade_time = trade_date 00:00:00`
⇒ **只有把 period 钉死为 daily/weekly/monthly 时，`(symbol, trade_date)` 去重才与表键等价**；
对任何 `*min` 周期该子集就是**更粗**（会误并掉合法的不同分钟 bar）。这条区分很重要，别笼统说"去重键粗"。

**未决（诚实标注）**：① 各消费者进程当前探针是否成功，需活体逐进程探测，未做；
② fexam 已登记分数是否有在**未合并部件**上跑出的，未查；
③ 是否存在"不写字面表名、经注册表间接取数"的通用加载器，未穷尽。

## 3. 产出③：对回测口径的影响面评估

| 维度 | 结论 | 依据 |
|---|---|---|
| 值会不会读错 | **会**（B 型）：daily 有 **383,272 个键（2026 全年 38.4%）存着互不相同的指标值**，非 FINAL 读同键返回最多 6 版，取哪一版由**行序**决定 | §1 表＋§2 "last"/"first" 语义 |
| 现在的 FINAL 读法对不对 | **暂时对**：我直接比对过 `FINAL` 与 `argMax(col, ingest_ts)`，2026-09-15 daily 上 **5557 键零分歧** | 查询见 §5 |
| 但这个"对"可靠吗 | **不可靠**：它依赖"后写入者恰好是最新 ingest_ts"，而引擎没有版本列，这个一致性**不由任何机制保证**，随合并次序漂移 | DDL 无版本参数（`schemas/...:296-298`） |
| 报表口径 | **已经不一致**：dashboard 的行数用 `system.parts sum(rows)`（含未合并重复），实读用去重后的行，两者天然不等 | `api_server.py:4070-4071` |
| 体积 | daily 行膨胀 **2.04×**（2026 段 2,039,333 行 vs 998,357 键）；A 型（分钟级）另占约 25-30 GiB 但**会随合并自愈** | §1 |
| 是否只有 daily | **不是**：weekly 也见 0.003 重复；分钟级 9 月为等值重复（A 型）。**但只有 B 型威胁正确性** | §1 |

**A/B 之外的第三条路（数据支持它，但仍要您点头）**：
既然 `ingest_ts` 已存在且可 100% 裁决，**读取侧改 `argMax(列, ingest_ts)` 或
`... ORDER BY ingest_ts DESC LIMIT 1 BY (symbol, period, trade_time)` 就能确定性拿最新版**，
成本远小于重建 220 GiB 表；而重建（把 `ingest_ts` 提为 ReplacingMergeTree 版本参数）
才是根治合并行为的办法——两者不互斥：先改读法止血，再择窗重建。

**我明确没有做的**：任何 INSERT/DELETE/DROP/ALTER/OPTIMIZE；任何 TTL 或表结构改动；
任何对 `indicator_reader.py` 的擅自修改。尺只测量。

## 4. 尺的使用与注意

```
python scripts/data_ops/audit_ti_row_versions.py --days 2026-09-15            # 人读
python scripts/data_ops/audit_ti_row_versions.py --days ... --json            # 机读
退出码 0=零重复 / 2=存在重复 / 3=分片采集失败（fail-loud，绝不因读失败判绿）
```
- **必须按 (period,单日) 分片**：全表 GROUP BY 会撞 CH 默认 `max_memory_usage`
  （车道实测 5.33 GiB 上限即炸）。
- **测量值随后台合并漂移**：同一天我跑两次，`daily` 分叉键 1713 → 1736。
  ⇒ 这把尺是**趋势仪**，不能当固定数引用；引数要带时间戳。
- 空返回按故障处理（本仓 CH 包装出错返回 `''` 不抛，`''` 与零行不可分）。

## 5. 本文关键数字的复算命令

```sql
-- B 型面积（2026 全年 daily）
SELECT count() AS keys, countIf(cnt>1) AS dup_keys, countIf(nv>1) AS divergent_keys,
       max(cnt), sum(cnt)
FROM (SELECT symbol, trade_time, count() AS cnt,
             countDistinct((ma_5,ma_20,rsi_6,macd_hist,atr_14,kdj_j,boll_upper)) AS nv
      FROM c1_market.technical_indicator
      WHERE period='daily' AND trade_date>='2026-01-01' GROUP BY symbol, trade_time);

-- ingest_ts 可裁决性
SELECT count(), countIf(ni>1) FROM (
  SELECT symbol, trade_time, count() AS cnt, countDistinct(ingest_ts) AS ni
  FROM c1_market.technical_indicator WHERE period='daily' AND trade_date='2026-09-15'
  GROUP BY symbol, trade_time HAVING cnt>1);

-- FINAL vs 最新入库 是否分歧（当日为 0）
SELECT count() AS keys, countIf(a.v!=b.v) AS disagrees FROM (
  SELECT symbol, trade_time, argMax(ma_5, ingest_ts) AS v FROM c1_market.technical_indicator
  WHERE period='daily' AND trade_date='2026-09-15' GROUP BY symbol, trade_time) a
INNER JOIN (SELECT symbol, trade_time, any(ma_5) AS v FROM c1_market.technical_indicator FINAL
  WHERE period='daily' AND trade_date='2026-09-15' GROUP BY symbol, trade_time) b
ON a.symbol=b.symbol AND a.trade_time=b.trade_time;
```

