---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 数据操作 SOP——回灌/修复/判重/PIT/探针全流程方法论（三步验证+幂等回补+FINAL 逐位验证）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-14
topic: data_ops_sop
---

# 数据操作 SOP——数据层施工方法论（真源）

> **一句话**：凡是"数据回灌、坏数据修复、表结构变更、判重、数据探针、缺口处置"的任务，动手之前 MUST 按本 SOP 走——三步验证定必要、幂等配方定做法、逐位验证定收尾、登记义务定归档；禁裸 SQL、禁凭记忆判数据、禁物理删事实。
> **诞生**：2026-09-14，Owner 批准成卷——此前回补配方/FINAL 验证/PIT 口径/探针手法散在各夜班实战记忆里，每个数据夜班都在重新发明；本卷把它们沉淀为唯一真源。
> **规则层亲缘**：[trae_063_data_ops_discipline.yaml](../../rules/trae_063_data_ops_discipline.yaml)（三步验证+判重的规则本体）；本文件是流程层展开，规则冲突以规则 YAML 为准。
> **方法论亲缘**：[../mining_sop/mining_sop_policy.md](../mining_sop/mining_sop_policy.md)（找数据源/调研先行时用挖矿 SOP；本卷管"数据已经在手、怎么安全落库"）。

## §1 三步验证（动手前的硬闸，缺一不写）

1. **必要性**：这数据没人消费就不拉（先查消费端；"北京 key 闲置/EODHD 逐日积累不跑就真空"类教训=先立卡消费方案再回灌）。
2. **真实性**：数据源本身核验过吗——样本抽查+行数对账+业务常识（千股千评 5196 行 vs 运价 22274 行先对账再入库）。
3. **可逆性**：写坏了能退吗——新表先建 staging 副本；改存量必须先备份（CH 建影子表）或确认幂等可重放；**不可逆操作（删行/物理删表）一律升级 Owner 门位**。

## §2 写入纪律（五条红线）

1. **唯一真源通道**：一律 `DatabaseService`（`zephyr.infrastructure.database_service`），禁裸 `duckdb.connect`、禁裸 SQL 散落。
2. **SSOT 方向判定**（RULE-SSOT）：规则数据改 YAML 同步 DB；架构数据走 apply_*.py 直写 DB——机械判定禁止凭记忆。
3. **DDL 真源**：表结构变更先改 `schemas/categories/` 对应簇 YAML，再走 admin 通道对 CH 执行；**CH query 失败不抛异常，DDL 后必须探针核实**（列数/mtime/describe）。
4. **时区铁律**（RULE-SCHEMA-TZ）：DateTime64(3)+显式时区；生成器禁 `datetime.now()/time.time()`（naive now 是门禁地雷）。
5. **物化列禁插**：CH MATERIALIZED 列（如 stock_indicator 的 exchange/symbol_canonical）由引擎生成，INSERT 显式带列名清单绕开。

## §3 回补配方（幂等是生命线）

**通用姿势**：按交易日/月分窗循环；每窗独立可重放；断点续扫（进度落盘）；行数对账写进产出文档。现成回补器优先复用，勿重造轮子：

| 回补器 | 覆盖 | 要点 |
|---|---|---|
| `scripts/backtest/backfill_stock_indicator_daily_basic.py`（MOD-BT-080） | tushare daily_basic 按交易日全市场 | 幂等拉取；落地解锁 fundamental_gate 翻译管线 |
| `scripts/data/backfill_technical_indicator_dwm.py` | 技术指标 日/周/月 | 指标库扩列后全量重刷 |
| `scripts/data/backfill_tick_depth5.py` | 五档 tick | 依赖 guard 重启带 env（worker 继承 guard 环境，换 env 必杀 guard 本体再触发） |
| `scripts/data/backfill_lof_minute_history.py` | LOF 分钟线 | **通道会永久消失（9-18 教训），该跑就跑别等** |
| `scripts/data/backfill_sector880_history.py` | 880 板块 | 传月初 start（曾犯"全量传月初 start 缺陷"已修） |
| `scripts/data/import_bdpan_tick_zip.py` | bdpan 网盘 tick | 行规：stock/裸码/direction 原样、手×100；BaiduPCS-Go 通道**绝对路径 meta 必 31062，须相对路径 cd 逐层导航** |
| `scripts/data/pattern_event_backfill.py` | 图形事件回扫 | 断点续扫+事件幂等（重扫 739 行不变实证） |

**外源接入**：深圳开放数据 WAF 吃自报家门 UA——要浏览器 UA+Referer；"无条件开放≠匿名开放"，绕 key 爬数据=违反条款，不做。

## §4 修复与验证（先判据，后动手）

1. **污染判据先行**：0908/0909 K 线修复先定判据（**一字板/无成交 ETF 平坦行合法，量能才是判据**），再修数；定因（盘前 09:00 拉当日 bar）后治本（`scripts/data/repair_kline_degraded_pull.py` 留盘）。
2. **FINAL 逐位验证**：删冗余行/重建表后，OPTIMIZE FINAL 重建前后**逐位比对**（FINAL 查询结果 hash 或逐列 count+sum 对账）；幂等重建以"跑两遍结果不变"为准。
3. **勿物理删事实**：错误事实行走 `valid_to`/`fact_close` 关闭通道（ig_fact 11127 行先例；物理删在 PIT 回滚时是事故——119 条误伤靠通道回滚救回）。
4. **并发写表**：多会话同表写入先 claim 协调；fetchall 结果双消费坑（游标耗尽）——结果集先物化再两次用。

## §5 PIT 口径（防前视）

1. 消费端 as-of 取数：公告日/更新日字段优先于交易日；财报因子必须 PIT（announcement_date 口径，DS-230 派生层先例）。
2. **PIT 关死字段不回填**：etf/index_list PIT 关死先例——拿不到历史时点值的字段，宁缺毋造。
3. 事件类数据先分层：事件日历层（台风库裁定）vs 连续数据层，勿混表。

## §6 判重与缺口

1. **判重**：`scripts/governance/data_quality/check_tick_duplication.py`，**禁用聚合 count 判重**（聚合数会掩盖半行重复）。
2. **缺口登记**：查不动/拉不到的缺口进 `src/zephyr/data/config/known_data_gaps.yaml`；**三渠道实证不可恢复→转 accepted**（tick 2026-07 六日先例），勿留悬账反复重试。
3. **登记义务**：新数据源/任务入 data_asset_registry（DS-*）/任务注册表（JOB-*）；**撞号让号**（后来者取下一个号，不抢注）。

## §7 探针手法（取证优先于推理）

- CH 探针：system.columns/describe/mtime 分组探针（活跃会话查 `.runtime/session_registry.json`+表 created_at 分组）。
- 文件探针：ch_writer TSV **无表头**；ig 表 schema 列差异逐列核对；SQL LIKE `%%` 转义坑。
- 数据源探针：xtdata 先小样本探针再批量；采购包节点 ID 非 md5（链 ID 才是）——ID 体系先验证再导入。
- 搜索超时换词是正解，不是加大超时。

## §8 实战范例索引（方法论实例库，新任务先翻这里）

| 案例 | 教训核心 |
|---|---|
| 0908/0909 K 线污染修复（6b54f46baa） | 判据先行+定因治本+repair 工具留盘 |
| tick 2026-07 回补（3156 万行） | 网盘通道打通+行规+六日 accepted 处置 |
| LOF 回补 142.7 万行 | 供应商通道会消失，回补别拖延 |
| ig_fact 误伤 PIT 回滚 | 勿物理删，通道化纠错 |
| 财报派生层 DS-230（e7c3a41b9c） | PIT as-of 派生表+登记三件套 |
| 台风管线（695fd39f） | 事件日历分层+增量/周全刷双任务+registry 让号 |

> 本表只增不删；新数据夜班收官时把"案例+教训核心"追加一行（登记义务的一部分）。
