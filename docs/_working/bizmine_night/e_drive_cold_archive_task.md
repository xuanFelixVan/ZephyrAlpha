---
ttl: task_bound
title: E:/zephyr_cold_archive 冷归档挂回工单——盘点实测·导入通道·功效账·排期·风险
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: open（工单已立待数据线排期；今晚只登记不接入——裁定#367）
session: st-final3-20260919
gap_ref: src/zephyr/data/config/known_data_gaps.yaml#cold_archive_minute_kline_e_drive
ruling: "裁定#367（2026-09-19）：E 盘冷归档挂回立工单排期，有界矩阵与分钟级信号的最大单点历史深度杠杆，挂回后可救 kline_etf_daily 过浅"
---

# E:/zephyr_cold_archive 冷归档挂回工单（数据线正门）

> **一句话**：E 盘分钟线冷归档（约 118GB，parquet 按月分区，manifest 逐行 verified）是 miniQMT 退役后**唯一已知批量历史分钟源**；本工单登记盘点实测、挂回通道设计、功效账与风险，供数据线排期施工。**裁定#367：今天只登记工单，不施工挂回。**

## 1. 盘点实测（2026-09-19 ls/pyarrow 实测，非转抄）

| 目录 | 分区数 | 区间（首→末分区） | 实测备注 |
|------|--------|------------------|---------|
| c1_market/kline_1min | 255 | 200006 → 202108 | 样本 200006=3,019,007 行/月 |
| c1_market/kline_5min | 255 | 200006 → 202108 | |
| c1_market/kline_15min | 255 | 200006 → 202108 | |
| c1_market/kline_30min | 255 | 200006 → 202108 | |
| c1_market/kline_60min | 255 | 200006 → 202108 | |
| c1_market/kline_etf_1min | 167 | 200502 → 201812 | 早期分区极薄（200502 实测仅 964 行） |
| c1_market/kline_lof_1min | 101 | 201008 → 201812 | **台账 06:0x 未列，实测补登** |
| c1_market/technical_indicator/{60min,120min} | 255+255 | 200006 → 202108 | manifest 表名/period 细分与目录布局需对账（§5） |
| c1_market/tick_data | 36 | 202201 → 202412 | 样本 202201=38,425,289 行/月（约 400MB/月）；**见下实测修正** |
| c3_fundamental/news_data | 121 | 199912 → 200912 | 台账 06:0x 未列，实测补登 |

- 总量：`du -sh` 实测 **118GB**；E 盘 932GB 已用 86%（余 134GB）。
- manifest：`archive_manifest.jsonl` 共 **2210 行**，与磁盘 parquet 总数 2210 计数一致；每行含 table/partition/parquet_path/parquet_size_bytes/archived_at/verified/dropped（**dropped=true=库侧原表已删，E 盘为唯一副本**）。
- schema 实测（kline_1min 200006）：trade_date(date32)、**trade_time(timestamp[ms, tz=UTC])**、symbol、open/close/high/low(decimal 18,4)、volume(uint64)、amount(18,2)、pct_change/amplitude、data_source、ingest_ts(timestamp[ms, tz=UTC])。tick_data 另有 recorded_time/market_type/direction/bid/ask 五档/quality_flag。
- **实测修正（对台账 06:0x 的两处出入，以实测为准）**：
  1. 台账写"**无 tick**"——实测 c1_market/tick_data 存在 **202201-202412 共 36 分区**（约 38.4M 行/月）。即 E 盘 tick 覆盖 2022-2024，恰为库内 tick（2025-01 起）的前置空窗段；
  2. 台账未列 kline_lof_1min（101 月）与 news_data（121 月，199912-200912）。

## 2. 挂回方案（导入通道=照 bdpan 导入器先例，禁裸写）

- **先例真源**：`scripts/data/import_bdpan_tick_zip.py`（+ `bdpan_tick_watch.py`）——其配方即本工单通道模板：幂等预检（导入前断言目标分区行数=0，非 0 跳过，重跑安全）→ 分块 insert_rows（20 万行/块）直写 → 单分区失败不挡其余 → 预检缺失/异常清单先行打印（不假装成功）→ 退出码 0=全成/2=部分/3=全败。全部读写经 `DatabaseService`（`zephyr.infrastructure.database_service`），禁裸 duckdb、禁裸 SQL 散落。
- **通道设计要点**（施工批细化，此处钉纪律）：
  1. 新建 `scripts/data/import_cold_archive_parquet.py` 型 CLI：读 `archive_manifest.jsonl` 逐行驱动，**verified=true 才导**；manifest 分区与磁盘文件先对账（§5 风险 4）。
  2. 分区键=YYYYMM parquet；幂等=每分区导入前 count 预检（对齐 bdpan 配方）；导入后 FINAL 逐位验证（行数+抽样对拍，data_ops_sop 纪律）+ `check_tick_duplication.py` 判重（禁聚合数判重）。
  3. 行规映射：按目标表现行 schema 逐列映射并登记 data_source 标记（如 `cold_archive` 溯源列/值，与 bdpan 用 `data_source='bdpan'` 同思路），ingest_ts 语义（原始入库时间 vs 本次重导时间）在施工批预注册写死。
  4. 时区转换口径先对齐再批量（§5 风险 3）：parquet trade_time=UTC tz-aware → 库内 DateTime64(3)+显式时区（RULE-SCHEMA-TZ），试点分区逐位验证后才放开。
  5. 排序：建议先 kline_1min 3 个月试点分区（如 200006/201006/202006 各一）端到端验收，再全量。
- **禁做**：挂回前禁清理/搬动 E 盘任何文件（唯一副本，无二次来源）；禁跳过 manifest 直接扫目录导（manifest verified 字段是质量闸）。

## 3. 功效账（三受益+一附加）

1. **有界矩阵（algo 车道）**：1min 深度从库内约 4.7 年扩到 2000-06 起 21+ 年——`matrix_necessity_verdict.md` ≤36 判定格矩阵的功效门（120 日/桶）与跨轮 N+ 累计获得全周期样本；台账 04:5x 行原话"E 盘挂回=最大杠杆"。
2. **分钟因子（F 车道系）**：IC 大海选/分钟因子获得跨牛熊全周期（2000-2021 含 2008/2015 极端段）IS 窗，factor_mining_sop 预注册协议可直接扩窗重跑；regime 条件化（§2 条款）分桶样本量同步翻倍以上。
3. **kline_etf_daily 重建**：ETF 1min 167 月（200502-201812）聚合重建日线，直接救 kline_etf_daily 过浅（裁定#367 明示受益）；LOF 1min 101 月附带同法可重建。
4. **附加（实测修正带来）**：tick_data 202201-202412 36 月填库内 tick 前置空窗（库内 tick 唯二=tick_data 2025-01 起 21 个月+tick_depth_5 07-24 起）——tick 级有界矩阵格子（tick 轴）从 21 个月扩到约 57 个月。

## 4. 排期建议（数据线正门工单排序，供 Owner/数据线裁定）

| 优先级 | 内容 | 理由 |
|--------|------|------|
| P1 | kline_1min 255 月 | 三受益中两受益（矩阵+分钟因子）的主粮；先试点 3 分区 |
| P2 | kline_etf_1min 167 月 + kline_lof_1min 101 月 | ETF/LOF 日线重建（第三受益） |
| P2.5 | tick_data 36 月 | 附加受益；体积大头（约 400MB/月，总量约 15GB 级），单列批次 |
| P3 | kline_5/15/30/60min 各 255 月 | 可由 1min 重聚合则降级为按需；否则随 P1 批顺带 |
| 挂账 | technical_indicator 60/120min、news_data | 有明确消费端需求再排（避免无消费挂回） |

- 施工窗口：避开交易时段与夜间管线高峰（BufferedWriter 压力）；每批导入后判重+复验留痕再进下一批。

## 5. 风险登记

1. **盘符稳定性/介质唯一性**：E 盘 86% 已用（余 134GB）；manifest 固化绝对路径 `E:\zephyr_cold_archive\...`，盘符映射/盘搬家即断链；**dropped=true=唯一副本**，挂回完成前禁任何 E 盘清理。施工批建议：开工前对 manifest 全量做 sha256 抽检（verified 复核），并存 manifest 副本入库。
2. **重复键/衔接缝**：与库内现存分钟段（约 2022-01 起）重叠面待实测；E 盘 1min 止于 2021-08，库内起点约 2022-01——**2021-09..2021-12 疑似无人覆盖的衔接缝**，施工批须先 SQL 实查库内分钟最小 trade_date 定缝；幂等预检+check_tick_duplication.py 判重（禁聚合数）双保险。
3. **时区**：parquet trade_time/ingest_ts 为 tz=UTC，库内 RULE-SCHEMA-TZ=DateTime64(3)+显式时区；UTC→交易所本地时口径转换若错，全部分钟因子 T-1/T 口径全错且难察觉——试点分区逐位对拍（含 09:30 开盘Bar边界与午休切割）后放行。
4. **manifest 与目录对账**：manifest 中 technical_indicator 记 64 行（无 period 后缀表名，路径入 `60min/` 子目录带 period 字段）+ technical_indicator_60min/120min 各 223 行，与磁盘 60min/120min 各 255 文件的路径/命名存在表述差异（总数 2210=2210 一致）；施工批须逐行对账后以磁盘+manifest 双确认为准。
5. **薄分区**：ETF 1min 早期分区极薄（200502=964 行），聚合重建日线时薄月须标记 low_coverage，禁硬凑。
6. **复权链无关性**：本归档为分钟原生数据，不解决 adj_factor 恒 1（exam_policy §4 暂定档条款继续适用其日线衍生结论）。

## 6. 登记链

- 裁定#367（2026-09-19）：立工单排期，今天只登记不施工。
- `src/zephyr/data/config/known_data_gaps.yaml` 条目 `cold_archive_minute_kline_e_drive` 已加"工单已立"指针（本工单=其 resolution_plan 的载体件）。
- 施工批开工时：按 construction_workflow_policy 走 15 步闭环 + 本工单 §2 纪律；完成须回写 known_data_gaps 条目销项。
