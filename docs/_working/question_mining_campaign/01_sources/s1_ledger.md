---
ttl: task_bound
completes_when: 挖矿战役归档后随包清理
---

# S1 数据源挖矿台账（st-pqmine-20260927 · 2026-09-27）

> 产出配套：[s1_candidates.yaml](s1_candidates.yaml)（32 题草稿：fail 28 / pass 4）
> 只读纪律：全程 DatabaseService reader 角色（`get_clickhouse_conn(role='reader')`），零写入任何库；探查脚本暂存 `.runtime/tmp/st-pqmine-20260927/s1/probe1~13*.py`。
> 文件锁：s1_candidates.yaml / s1_ledger.md 已 `lock_files.py acquire`（st-pqmine-20260927）。

## 一、探查范围

全库底册（probe1/probe2，system.tables 全扫，249 表 / 122.77 亿行）：

| 库 | 表数 | 行数 | 挖矿深度 |
|----|------|------|---------|
| c0_meta | 1（fetch_perf 103 行） | 103 | 浅（schema+新鲜度） |
| c1_market | 198 | 122.3 亿 | 中深：~55 张主表逐表 coverage/freshness/dup/orphan；分钟线/tick 族只扫了底册+代表表 |
| c3_fundamental | 34 | 4594 万 | 中深：财报三表/股东/预期/新闻/解禁全探；dividend/repurchase/rights_issue 等仅底册 |
| c1_backtest | 16 | 1.1 万 | 浅（max 日期+decision_daily schema——属 L3/L4 层矿区，留给 S3/S4） |

探查证据（关键 probe → 发现）：
- probe3/3b/5（system.columns PIT 列全扫）：ingest_ts 全库普及；macro_data_vintage 独有 (report_date, pub_ts)；analyst_forecast 无任何公告列。
- probe4/6（覆盖率）：kline_daily 1990-12-19~2026-09-24/5913 只；kline_1min 2021-09-01 起；daily_valuation 仅 2026-08-03 起；macro_data 2261 指标 vs vintage 28 指标；news_sentiment_score 止于 2025-09-09。
- probe7（质量）：money_flow 同键重复 88800 组（全同值）；kline_daily 113 组；consensus_daily 17390 组；news_id 重复 194859；macro_data 2517 组（同值，判幂等，弃题）；news publish>crawl+1h 3963 行；restricted_shares announce 空 373783；OHLC 高低价倒挂=0（干净）。
- probe8/9/10（对账）：adj_factor 死列（kline_daily.adj_factor 全 1，同键失配 931 万行）；daily_valuation vs kline close 容差外 116433 行；repaired vs 主表分歧 78570 行；月线 legacy 丢在市股史 105914 键；quarantine 隔离交集=0；情绪/板块状态表 dup=0；打分 PIT 顺序 0 违规。
- probe11/13（新鲜度+孤儿）：hk_connect_flow 停 2024-08-16（披露制度变更终态）；option_daily_stats 停 09-22；cftc 停 09-08；fetch_perf 停 07-11；kline 孤儿代码 20 只（北交所段）；c1_market 零行生产表 13 张；decision_daily 存在 trade_date=次日行（判为 T-1 预写设计，非违规，未立题）。

## 二、数据面事实清单（出题依据的硬数字）

1. PIT 基建半成品：macro_data_vintage 表已建（对 PQ-0185 缺口的补救）但 pub_ts 16091/16091 全 NULL、pub_ts_basis 单值 backfill_final、vintage 单值 1、指标覆盖 28/2261（1.24%）——PIT 重放当前不可用。
2. analyst_forecast 无公告时点列（仅 report_date），是全库唯一缺 PIT 列的预测类表。
3. 2026 中报：income_statement 期末 06-30 覆盖 5217 只（达标）；但 top10_shareholders 07-01 后公告=0（整季缺失，与中报同源却未跟更）。
4. hfq 重建链：kline_daily_hfq 比 kline_daily 少 4 只代码；月线 hfq 主表比 legacy_r1 少 105940 个在市 (symbol,月末) 键；09-25 隔离表 10475 键与主表零交集（隔离语义成立）。
5. 价格对账：daily_valuation.close 与 kline_daily.close 容差外差 116433 行；kline_daily.adj_factor 列 1010 万行恒=1（死列），与 adj_factor 独立表失配 9313778 行。
6. 重复行族：money_flow 88800 / news_id 194859 / consensus 17390 / kline_daily 113 / macro_data 2517（均同值重复）；kline_sector_880 3599 条重复是 PQ-0143/0144 遗留已知项（results_all.yaml:6312）。
7. 新鲜度异常族：hk_connect_flow（2024-08-16 终态）、option_daily_stats（-2 交易日）、cftc_positioning（-2 期周报）、fetch_perf（-2.5 月）、news_sentiment_score（停在 PIT 切点）、emotion_index.auction（-1 交易日）、sector_state.pre_open（仅 09-23 单日 469 行）。
8. 治理面：c1_market 零行生产表 13 张（edb_data/l2_tick/realtime_snapshot/stock_valuation/ipo_schedule 等）；stock_list.list_status 取中文枚举（上市/退市）与 tushare L/D 不互通。
9. 干净面（pass 题依据）：income 2026H1 覆盖 5217 只；打分表 scored_at≥publish_time 全量成立；隔离表不变量成立；情绪/板块状态表主键唯一。
10. 迟到入库：近 90 日窗 ingest 晚于交易日 >7 天，kline_daily 250875 行、money_flow 285052 行——管线以批量回补为主要写模式。

## 三、去重决策记录

- **弃题（翻案/同义风险）**：macro_data 2517 组同值重复——PQ-0172（SL-A08）已定『同值重复=幂等重采 pass』口径，虽对象不同仍弃，防同义争议。
- **近邻区分登记**：S1-001/002 ↔ PQ-0185（机制缺失 vs 补建表空转）；S1-003 ↔ PQ-0202（股东户数哨兵 vs top10 季批完整性）；S1-004 ↔ PQ-0012（比率对齐 vs 键域完整性）；S1-019/023 ↔ PQ-0172（行数卫生 vs 值冲突审计）；S1-024 ↔ PQ-0012/退役簇 0110-0112（列完整性 vs 口径/预测力）；S1-012 ↔ PQ-0015（前向连续 vs 存量回填；不涉预测力不触退役禁令）；S1-027/028 ↔ 退役情绪因子簇（管线连续性 vs 预测力）。
- **保留理由核心**：退役 30 问全部是『因子/信号无预测力』型；本题册全部是数据链路验收（覆盖/PIT/新鲜度/质量/一致性），无一题断言预测力，不存在修参数翻案通道。

## 四、自审三态

- **挖干**：c1_market 与 c3_fundamental 的核心事实表（行情/复权/估值/资金流/财报/股东/预期/新闻/宏观/情绪/板块状态）五问题面均已扫过并留下机解判据；249 表底册全量建立。
- **未干**：①198 张 c1_market 表中约 140 张 alt_*/期货/期权/可转债/港美金属性表仅做了底册与代表表抽查，未逐表五面扫描（建议 S1 第二轮按族扫描）；②c1_backtest 16 张属 L3/L4 矿区，本轮只取了新鲜度样点，深度验收题让位 S3/S4；③trade_calendar.pretrade_date 正确性校验因 ClickHouse 内存限制（6.95GiB limit exceeded）受阻未出题；④kline_1min~60min 五周期起点一致性未逐周期核实。
- **受阻**：trade_calendar 窗口自连接内存超限（已用 lagInFrame 重写仍因列名歧义失败，两法皆弃）；c0_meta 仅 1 表无深挖面；无权限/网络类受阻。

## 五、移交事项

1. 32 题草稿待 90_consolidated 汇总去重 → 质量闸 → registry.py intake 正门注册（PQ-0284+）。
2. CREATE-GUARD creation_token 与 TRANSLATION 登记不适用于本产物（数据文件非代码模块），但注册批须按 intake 规范补 origin 锚点（本册 origin 已含表名+探查数字，probe 脚本路径在 .runtime 24h TTL 内有效，注册时应把关键 SQL 固化进 exam_plan）。
3. 建议第二轮：alt_* 族表（19 张深圳多源表+气象/台风/水库）、期货期权可转债族、港美股族的逐表五面扫描。
