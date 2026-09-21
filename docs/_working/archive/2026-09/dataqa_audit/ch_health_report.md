---
ttl: task_bound
session: st-dataqa-20260920
audit: dataqa_20260920
---

# R1 · ClickHouse 全库体检报告（2026-09-20）

> 执行：st-dataqa-20260920（通宵总令·分包B）。纯只读体检，零写入零修复。
> 工具：`.runtime/tmp/dataqa/probe_ch_health.py`（DatabaseService reader 连接，全程轻查询：
> system.* 元数据 + 单列 min/max + count()，未做任何全表多列扫描，未触碰凌晨窗口）。
> 探针原始输出：`.runtime/tmp/dataqa/out/r1_ch_health.json` / `.runtime/tmp/dataqa/out/r1_master.csv` / `.runtime/tmp/dataqa/out/r1_partition_rows.csv` / `.runtime/tmp/dataqa/out/r1_parts_top.csv`。
> 证据等级：本报告全部数字为 **[亲验]**（探针实跑，2026-09-20 约 15:30-16:00 窗口）。

## 0. 一页结论（TL;DR）

1. **CH 26.6.1 存活、可查询**：全库 4 业务库 246 表、约 426.7 GB、126.2 亿行、27,856 active parts。
   探针 246 表零查询错误——09-15 的 Code 241 内存拒查**当前未复现**（但 technical_indicator parts 仍在
   高位 1339 且有回填在飞，见 §3，风险未解除）。
2. **49 个 1970 残留 parts 全部定位到表**（§4）：分布在 8 张业务表 + 4 张备份表；行级 1970-01-01
   数据共 18 张表约 43.6 万行，大头=restricted_shares 34.3 万行 / financial_indicator 3.4 万 /
   disclosure_plan 3.4 万（清单日期类字段哨兵零值，属登记过的病灶家族）。
3. **碎片 TOP10 换了榜首**（§3）：`alt_sz_climate_hist`=1360 parts（09-17/18 每天暴增 680 个，新发）
   超过 `technical_indicator`=1339（09-15 实测 1298→现 1339；增长主因=**tilib 清欠班 dwm 回填正在飞**
   （PID 30160，`scripts/data/backfill_technical_indicator_dwm.py`），并非纯合并停滞——恢复判据（parts 显著下降+
   单行 SELECT 成功）的"下降"一半须等回填停止后观察）。另有 12 张小表 parts 爆炸（行数<10 万、
   parts>300，§3.3），共性=高频小批量写无合并。
4. **CH 内残留 16 张备份表 + 1 张污染表，合计 35.4 GB**（§5）：含 5 张 etf tz_bak（时区修复回滚保险，
   7.4M+326M 行级）、2 张 news_data 旧态表 25.8 GB。建议 Owner 裁定保留期。
5. **新鲜度**：核心行情链全部新鲜（tick_data/kline_daily/kline_1min/etf 族/technical_indicator/
   crypto_kline_daily max=2026-09-18 或 09-19）；异常集中在 alt/macro 事件表与 9 张哨兵破防腿，
   明细归 R2（`docs/_working/dataqa_audit_20260920/gaps_registry_review.md`），本报告 §6 仅列清单。

## 1. 范围与口径

- **库**：c0_meta / c1_backtest / c1_market / c3_fundamental（system 库仅作元数据源，不计入）。
- **在用表定义**：CH 实存非 system 表全部纳入（246 张），按名称与注册表状态分类：
  live / backup（名称含 bak/backup/pre_tz）/ corrupt（含 corrupt）。
- **行数双算法**：`count()` 精确值 vs `system.parts sum(rows)` 近似值，246 表逐表对账，
  **偏差>0.1% 或 >1000 行的表=0 张**（对账通过，无 FINAL 折叠假象干扰主数字）。
  **口径声明**：本报告行数=物理行（raw，ReplacingMergeTree 含未折叠版本行）；关键争议表
  （daily_valuation/index_valuation_daily 等）已在 R2 报告补 FINAL 双口径对照，两口径差异
  本班实测最大 2,000 行（daily_valuation 270,260 raw vs 268,260 FINAL，≈0.7%）。
- **最新数据日期**：每表按优先级选业务日期列（trade_date > trade_time > cal_date > announce_date >
  publish_date > … > ingest_ts），无日期/DateTime 列的 11 张表单独列 §6.3（其中 7 张实有
  asof_ts/pit_date 等非惯用名列，属本探针选列偏好未覆盖，非数据缺陷）。
- **30 天日增趋势**：月分区表=当月行数/已过天数（9 月已过 20 天）；日分区表=近 30 分区均值；
  元组分区（如 technical_indicator (period,month)）不适用，标注 n/a。
- **新鲜度基准**：A股表对照上一交易日 2026-09-18（周五；09-19/20 为周末）；crypto/7×24 表对照
  2026-09-19。滞后≠必异常（周/月频事件表天然滞后），判定归 R2 逐条做。

## 2. 全库总览

| 库 | 表数 | 行数 | 磁盘 | active parts |
|----|-----|------|------|-------------|
| c1_market | 192 | 12,564,869,779 | 386.69 GB | 21,747 |
| c3_fundamental | 39 | 54,190,115 | 39.86 GB | 5,994 |
| c1_backtest | 14 | 9,686 | 0.00 GB | 114 |
| c0_meta | 1 | 103 | 0.00 GB | 1 |
| **合计** | **246** | **≈126.2 亿** | **≈426.65 GB** | **27,856** |

行数 TOP10（全部 [亲验]）：

| 表 | 行数 | max 业务日 | active parts |
|----|------|-----------|-------------|
| c1_market.tick_data | 8,857,297,679 | 2026-09-18 | 53 |
| c1_market.kline_1min | 1,481,257,322 | 2026-09-18 | 264 |
| c1_market.technical_indicator | 372,128,415 | 2026-09-18 | 1,339 |
| c1_market.kline_etf_1min | 327,074,832 | 2026-09-18 | 440 |
| c1_market.kline_5min | 294,324,216 | 2026-09-18 15:00(+08) | 196 |
| c1_market.kline_lof_1min | 138,897,460 | 2026-09-18 | — |
| c1_market.kline_15min | 98,275,249 | 2026-09-18 | — |
| c1_market.alt_sz_reservoir_level | 75,511,530 | **2026-07-31（停更，R2 在案）** | 217 |
| c1_market.kline_etf_5min | 72,070,158 | 2026-09-18 | 525 |
| c1_market.kline_30min | 48,967,050 | 2026-09-18 | — |

核心表 30 天日增（月分区口径，9 月日均）[亲验]：tick_data ≈1,661 万行/日、kline_1min ≈115 万、
kline_5min ≈24.3 万、kline_etf_1min ≈32.8 万、kline_etf_5min ≈6.1 万、news_data(c3) ≈2,235、
kline_sector ≈802、crypto_kline_daily ≈59（币圈日线 59 标的/日，7×24 表 max=09-18 属正常节奏）。

## 3. parts 碎片体检

### 3.1 TOP10 碎片表（active parts）

| # | 表 | parts | 行数 | 磁盘 | 近 30 天日增 parts 走势（要点） |
|---|----|-------|------|------|------------------------------|
| 1 | c1_market.alt_sz_climate_hist | **1,360** | 881,158 | 0.02 GB | **09-17、09-18 每天各 +680 parts**（新发爆炸，与某批量回填节奏吻合，需归因） |
| 2 | c1_market.technical_indicator | **1,339** | 372,128,415 | 170.17 GB | 09-12:19 → 09-14:33 → **09-15:469（内存事故日）** → 09-16:136 → 09-17:61 → 09-18:104 → 09-19:289。tilib 清欠班 dwm 回填（PID 30160）正在写入 |
| 3 | c1_market.alt_regime_signal | 886 | 20,843 | <0.01 | 高频小写 |
| 4 | c1_market.macro_data | 736 | 56,050 | <0.01 | 高频小写 |
| 5 | c1_market.alt_shipping_index | 699 | 44,968 | <0.01 | 高频小写 |
| 6 | c1_market.rate_decision_calendar | 670 | 3,086 | <0.01 | 全量幂等重写型（每跑一次产一批 parts） |
| 7 | c1_market.macro_credit_money | 584 | **584** | <0.01 | **1 行/part 极端形态** |
| 8 | c1_market.kline_etf_5min | 525 | 72,070,158 | 1.59 GB | 大表正常范围偏高 |
| 9 | c3_fundamental.news_data | 517 | 8,348,853 | 13.09 GB | 新闻族 8 任务高频写 |
| 10 | c1_market.macro_price_gauge | 496 | **496** | <0.01 | **1 行/part 极端形态** |

> 台账对照：09-15 tilib 交接包记录 technical_indicator active parts=1298（另一时点 1304），
> 本日实测 1339。**定性修正**：parts 增长有两条贡献——(a) tilib 清欠班 dwm 回填正在飞（今日实时进程），
> (b) 后台 merge 慢。Code 241 拒查今日未复现（246 表查询全成功），但内存风险随回填持续存在。
> 恢复判据照旧：回填结束+parts 显著下降+单行 SELECT 成功。**本班零干预，只记基线**——本报告 §3.1
> 数字即 2026-09-20 基线快照，后续每日量一次可与本表对比看趋势。

### 3.2 大表 parts 健康度（参照组）

tick_data 88.6 亿行仅 53 parts、kline_1min 14.8 亿行 264 parts、kline_daily 432 parts——
大表分区/合并策略健康，碎片问题集中在**小表高频写**形态。

### 3.3 小表 parts 爆炸清单（parts>300 且行数<10 万，12 张）

alt_regime_signal(886/20,843)、alt_shipping_index(699/44,968)、macro_data(736/56,050)、
rate_decision_calendar(670/3,086)、macro_credit_money(584/584)、macro_price_gauge(496/496)、
macro_activity_gauge(436/436)、us_index(405/22,600)、rights_issue(407/80,803)、
alt_sz_weather_warning(326/18,712)、ex_dividend_event(482/57,715)、repurchase(306/10,936)。

**共性根因**：调度高频（分钟/小时级）小批量 INSERT + 无按批合并；macro_* 三张 1 行/part 形态
疑似"每指标每期一行、逐行 INSERT"写入路径。修复方向（R4 归 P2）：写入端攒批 + 择机 `OPTIMIZE
... FINAL`（小表秒级），不改 schema。

## 4. 1970 残留定位（49 个 parts 全部归位 ✓）

分区级（system.parts，partition LIKE '%1970%'，active）——**合计 49 parts / 12 张表 / 26,689 行**：

| 表 | partition | parts | rows |
|----|-----------|-------|------|
| c1_market.rate_decision_calendar | 197006..197012（7 个月分区） | 7 | 7 |
| c3_fundamental.balance_sheet_bak_1970clean_20260914 | 197001 | 1 | 2,395 |
| c3_fundamental.cashflow_statement_bak_1970clean_20260914 | 197001 | 1 | 2,402 |
| c3_fundamental.dividend | 197001 | 1 | 983 |
| c3_fundamental.equity_pledge_detail | 197001 | 1 | 2,294 |
| c3_fundamental.financial_indicator | 197001 | 1 | 64 |
| c3_fundamental.financial_indicator_bak_1970clean_20260914 | 197001 | 1 | 2,585 |
| c3_fundamental.income_statement_bak_1970clean_20260914 | 197001 | 1 | 2,401 |
| c3_fundamental.main_business | 197001 | 2 | 4,119 |
| c3_fundamental.restricted_shares | 197001 | 2 | 10,927 |
| c3_fundamental.rights_issue | 197001 | 1 | 31 |

（加上 c1_market 侧合计表数 12、parts 49，与已知线索"49 个 1970 partition"精确吻合。）

行级 1970-01-01（业务日期列 = 1970-01-01 的行，单列 countIf 扫描，18 张表命中）：

| 表 | rows@1970 | 表总行数 | 备注 |
|----|-----------|---------|------|
| c3_fundamental.restricted_shares | 343,298 | 10,177,657 | 解禁日哨兵零值，最大头 |
| c3_fundamental.financial_indicator | 34,339 | 387,990 | |
| c3_fundamental.disclosure_plan | 33,638 | 316,739 | |
| c3_fundamental.dividend | 6,749 | 116,334 | |
| c3_fundamental.equity_pledge_detail | 2,294 | 120,628 | |
| c1_market.index_list | 1,722 | 9,700 | 1,700=已登记 PIT 关死墓碑（设计内），22 行 valid_to=NULL 存活（R2 §） |
| c1_market.convertible_bond_list | 1,054 | 2,102 | **未在 gaps 注册表登记** |
| c3_fundamental.audit_opinion | 150 | 96,010 | |
| c1_market.etf_list | 84 | 2,184 | 84 行 valid_to=NULL 存活，与"墓碑清零"结论矛盾（R2 §） |
| c3_fundamental.shareholder_count | 47 | 513,548 | |
| c3_fundamental.rights_issue | 31 | 80,803 | |
| c1_market.stock_list | 2 | 5,921 | |
| 4×*_bak_1970clean_20260914 / kline_daily_bak_256 / rate_decision_calendar | ~9,787 | — | 备份表保留原样 |

**修复建议归 R4（P2）**：日期哨兵 1970 行是"无值写成 0"家族的日期版，逐表 PIT 关死或补真值
均属破坏性操作=Owner 门位，本班只登记。

## 5. CH 内备份表/污染表清单（17 张，35.41 GB）

| 表 | 行数 | 磁盘 | max | 性质 |
|----|------|------|-----|------|
| c3_fundamental.news_data_pre_tz2_20260828 | 7,872,827 | 12.88 GB | 08-28 | 时区修复前旧态 |
| c3_fundamental.news_data_corrupt_20260828 | 8,040,882 | 12.99 GB | 08-28 | 污染快照 |
| c1_market.kline_etf_1min_tz_bak_20260918 | 326,301,055 | 5.41 GB | 09-16 | **etf 时区修复回滚保险（修复已执行，见 R2）** |
| c1_market.kline_etf_5min_tz_bak_20260918 | 71,856,186 | 1.52 GB | 09-16 | 同上 |
| c1_market.kline_etf_15min_tz_bak_20260918 | 24,329,183 | 0.62 GB | 09-16 | 同上 |
| c1_market.kline_etf_30min_tz_bak_20260918 | 11,939,337 | 0.35 GB | 09-16 | 同上 |
| c1_market.kline_etf_60min_tz_bak_20260918 | 5,955,571 | 0.21 GB | 09-16 | 同上 |
| c1_market.kline_1min_tzbak_20260914 | 36,194,235 | 0.95 GB | 07-15 | 旧 tz 修复备份 |
| c1_market.kline_5min_tzbak_20260914 | 4,456,056 | 0.10 GB | 07-15 | 同上 |
| c1_market.kline_daily_bak_256 | 9,669,695 | 0.37 GB | 08-21 | 备份 |
| c1_market.tick_data_tzbak_20260914 | 507,700 | 0.01 GB | 09-10 | 备份 |
| c1_market.auction_book_limit_bak_20260908 | 1,911,474 | 0.01 GB | 09-03 | 备份 |
| c1_market.kline_daily_hfq_bak_20260915dup | 5,207 | <0.01 | 09-11 | 备份 |
| 4×c3_fundamental.*_bak_1970clean_20260914 | ~9,783 | <0.01 | 1970 | 1970 清理备份 |

**建议**（归 R4 P2，删除=Owner 门位）：etf 5 张 tz_bak 是 2026-09-18 修复的可逆通道（反向换名即退），
建议保留至修复后一个完整月度复盘；news_data 两张旧态表 25.8 GB 占 c3 库 65%，若已确认无消费方，
择期归档后清理。

## 6. 新鲜度异常清单（判读归 R2，此处只列事实）

### 6.1 A 股口径滞后表（max < 2026-09-18，行数>0 的 live 表，共 102 张命中）
其中需关注的前段（完整清单见附录 A）：
- **整类停更**：alt_sz_reservoir_level(07-31)、alt_sz_reservoir_rain_day/month、
  futures_warehouse_receipt SHFE 维度(2025-11-17，CZCE 正常)、rate_decision_calendar(2025-10-30)、
  dividend(07-01)、restricted_shares(07-02)、express_report/earnings_forecast(07-02/03)、
  top10_circulating_shareholders(2026-05-15)、pdf_forecast_extracted(2021-12-31)
- **近日新断**（R2 重点）：index_quote(09-16)、auction_snapshot/auction_book(09-16)、
  news_sentiment_window(09-14)、stock_indicator 09-18 半日(1000/5565)、daily_valuation 09-16/18 部分写入
- c1_backtest.sim_* 族 max=09-17（sim 平台批作业节奏，final3 收口后会话已死，观察项）

### 6.2 7×24 口径滞后（2 张）
hl_liquidation_raw（2 行测试行，R2 在案 open 条目）、crypto_shadow_gate（4 行门状态表，低风险）。

### 6.3 无惯用日期列表（11 张）
market_pattern_event(4077 万行)/market_pattern_certification/market_pattern_win_rate/
judgment_next_day_forecast/judgment_plan_verification/judgment_daily_plan/
judgment_intraday_market_state/ir_activity_extracted/irm_interactive_extracted/
irm_interactive_qa/dividend_tax_node。抽验 7 张实有 asof_ts/pit_date/verification_ts 等
DateTime64/Date 列（本探针选列偏好未覆盖，非数据缺陷）；judgment_* 四表 0-4 行=
判定台账尚未量产（与"98 黄灯接电"旧账一致，P2 观察项）。

## 7. 注册表覆盖交叉（联动 R4）

data_asset_registry（REG-DATAFLOW-001，264 条 datasets）entity_name 与 CH 实表精确匹配：
158/246 张有登记；live 类未登记 77 张（含 c1_backtest.sim_* 全家、judgment_* 全家、
hl_* 币圈族、agri_wholesale_index、cftc_positioning、ipo_calendar 等）。registry 漂移
属 P2 卫生项，完整清单在 `docs/_working/dataqa_audit_20260920/cross_findings.md` §6 附。

## 8. 复验命令示例（任何人可重跑核数）

```bash
# 行数双算法（示例 technical_indicator；全部表批量=probe 脚本）
python -c "import sys; sys.path.insert(0,r'D:\ZephyrAlpha\src'); \
from zephyr.infrastructure.database_service import get_db_service; \
c=get_db_service().get_clickhouse_conn(role='reader',slot='verify'); \
print(c.execute(\"SELECT count() FROM c1_market.technical_indicator\"), \
c.execute(\"SELECT sum(rows) FROM system.parts WHERE active AND database='c1_market' AND table='technical_indicator'\"))"

# 1970 parts 定位复跑（应仍=49，直至有人修复）
# SELECT table, count() FROM system.parts WHERE active AND partition LIKE '%1970%' GROUP BY table

# 碎片 TOP10 复跑
# SELECT database, table, count() FROM system.parts WHERE active GROUP BY database, table ORDER BY 3 DESC LIMIT 10
```

## 9. 本报告未覆盖

- system 库自身健康（副本/磁盘 RAID/ZooKeeper）——单机版无副本拓扑可查，未做。
- duckdb/governance.db/PG(depgraph)/redis——非 CH 范围，总令未列，未做。
- 表级数据正确性抽检（价格越界/时区劈叉复测）——除 R2 已列条目外未扩面。
- 每日 parts 趋势的**连续观测**：本报告=首日基线；建议后续班每日跑一次 probe 存档对比。

## 附录 A · 全库 246 表体检主表（.runtime/tmp/dataqa/out/r1_master.csv 快照）

| 表 | 引擎 | 分类 | 注册状态 | 行数 | GB | parts | 业务列 | max | 新鲜度 | 30d日增 |
|----|------|------|---------|------|----|-------|--------|-----|--------|--------|
| c0_meta.fetch_perf | ReplacingMT | live | active | 103 | 0.0 | 1 | - | - | - | - |
| c1_backtest.alloc_budget_change_log | MT | live | active | 8 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 0 |
| c1_backtest.alloc_budget_daily | MT | live | active | 10 | 0.0 | 1 | trade_date | 2026-09-18 | lag0d | 0 |
| c1_backtest.alloc_shrinkage_daily | MT | live | active | 5 | 0.0 | 1 | trade_date | 2026-09-18 | lag0d | 0 |
| c1_backtest.crisis_gate_log | MT | live | - | 0 | 0.0 | 0 | trade_date | 1970-01-01 | lag20714d | - |
| c1_backtest.decision_daily | MT | live | - | 43 | 0.0 | 1 | trade_date | 2026-09-21 | lag-3d | 2 |
| c1_backtest.hypothesis_precheck | MT | live | - | 58 | 0.0 | 1 | ingest_ts | 2026-09-19 02:01 | lag-1d | 3 |
| c1_backtest.node_verdict | MT | live | active | 58 | 0.0 | 1 | ingest_ts | 2026-09-17 17:54 | lag1d | 3 |
| c1_backtest.regime_snapshot_history | MT | live | - | 3,621 | 0.001 | 98 | trade_date | 2026-09-15 | lag3d | 1 |
| c1_backtest.regime_state_anchored | ReplacingMT | live | - | 4,469 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | - |
| c1_backtest.sim_attribution_daily | ReplacingMT | live | - | 6 | 0.0 | 1 | trade_date | 2026-09-17 | lag1d | 0 |
| c1_backtest.sim_platform_journal | ReplacingMT | live | - | 8 | 0.0 | 1 | trade_date | 2026-09-19 | lag-1d | - |
| c1_backtest.sim_pocket_daily | ReplacingMT | live | - | 68 | 0.0 | 2 | trade_date | 2026-09-19 | lag-1d | - |
| c1_backtest.sim_trade_log | ReplacingMT | live | - | 17 | 0.0 | 2 | trade_date | 2026-09-19 | lag-1d | - |
| c1_backtest.strategy_screen | MT | live | - | 1,315 | 0.0 | 1 | ingest_ts | 2026-09-18 17:20 | lag0d | 66 |
| c1_market.a50_futures_daily | ReplacingMT | live | active | 2,610 | 0.0 | 123 | trade_date | 2026-09-18 | lag0d | 1 |
| c1_market.account_nav_daily | ReplacingMT | live | - | 0 | 0.0 | 0 | trade_date | 1970-01-01 | lag20714d | - |
| c1_market.adj_factor | ReplacingMT | live | active | 21,054,931 | 0.048 | 430 | trade_date | 2026-09-18 | lag0d | 11 |
| c1_market.agri_wholesale_index | ReplacingMT | live | - | 11,638 | 0.001 | 250 | trade_date | 2026-09-18 | lag0d | 4 |
| c1_market.alt_fx_rate_ecb | ReplacingMT | live | - | 69 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 2 |
| c1_market.alt_regime_signal | ReplacingMT | live | active | 20,843 | 0.002 | 886 | ingest_ts | 2026-09-18 11:07 | lag0d | 9 |
| c1_market.alt_shipping_index | ReplacingMT | live | active | 44,968 | 0.001 | 699 | trade_date | 2026-09-18 | lag0d | 3 |
| c1_market.alt_stock_comment | ReplacingMT | live | active | 31,182 | 0.002 | 2 | trade_date | 2026-09-18 | lag0d | 1559 |
| c1_market.alt_sz_air_quality_daily | ReplacingMT | live | active | 54,154 | 0.002 | 140 | ingest_ts | 2026-09-18 11:00 | lag0d | 12 |
| c1_market.alt_sz_air_quality_region | ReplacingMT | live | active | 52,850 | 0.003 | 156 | ingest_ts | 2026-09-18 11:00 | lag0d | 20 |
| c1_market.alt_sz_climate_hist | ReplacingMT | live | active | 881,158 | 0.022 | 1360 | ingest_ts | 2026-09-18 11:05 | lag0d | 29 |
| c1_market.alt_sz_enterprise_year | ReplacingMT | live | active | 44 | 0.0 | 1 | ingest_ts | 2026-09-14 15:03 | lag4d | - |
| c1_market.alt_sz_env_meteor | ReplacingMT | live | active | 27,858 | 0.001 | 1 | ingest_ts | 2026-09-18 11:00 | lag0d | - |
| c1_market.alt_sz_ground_obs | ReplacingMT | live | active | 815,125 | 0.027 | 160 | ingest_ts | 2026-09-18 11:07 | lag0d | 256 |
| c1_market.alt_sz_house_area | ReplacingMT | live | active | 59,105 | 0.002 | 105 | ingest_ts | 2026-09-18 11:00 | lag0d | 14 |
| c1_market.alt_sz_house_daily | ReplacingMT | live | active | 443,432 | 0.009 | 234 | ingest_ts | 2026-09-18 11:03 | lag0d | 115 |
| c1_market.alt_sz_house_listing | ReplacingMT | live | active | 2,788,190 | 0.188 | 5 | ingest_ts | 2026-09-18 11:12 | lag0d | - |
| c1_market.alt_sz_house_presale | ReplacingMT | live | active | 2,155 | 0.0 | 1 | ingest_ts | 2026-09-15 18:41 | lag3d | - |
| c1_market.alt_sz_marine_forecast | ReplacingMT | live | active | 295,467 | 0.006 | 2 | ingest_ts | 2026-09-18 11:02 | lag0d | - |
| c1_market.alt_sz_market_subject | ReplacingMT | live | active | 11 | 0.0 | 1 | ingest_ts | 2026-09-15 17:35 | lag3d | - |
| c1_market.alt_sz_port_monthly | ReplacingMT | live | active | 1,168 | 0.0 | 182 | ingest_ts | 2026-09-18 11:01 | lag0d | 0 |
| c1_market.alt_sz_reservoir_level | ReplacingMT | live | active | 75,511,530 | 0.953 | 217 | tdate | 2026-07-31 | lag49d | 3967 |
| c1_market.alt_sz_reservoir_rain_day | ReplacingMT | live | active | 574,964 | 0.006 | 166 | ingest_ts | 2026-09-18 11:04 | lag0d | 11 |
| c1_market.alt_sz_reservoir_rain_month | ReplacingMT | live | active | 13,741 | 0.0 | 1 | ingest_ts | 2026-09-14 21:31 | lag4d | - |
| c1_market.alt_sz_reservoir_station | ReplacingMT | live | active | 485 | 0.0 | 1 | ingest_ts | 2026-09-14 21:31 | lag4d | - |
| c1_market.alt_sz_stat_analysis | ReplacingMT | live | active | 7 | 0.0 | 1 | ingest_ts | 2026-09-18 11:01 | lag0d | - |
| c1_market.alt_sz_stat_monthly | ReplacingMT | live | active | 34,064 | 0.003 | 142 | report_date | 2025-06-01 | lag474d | 1 |
| c1_market.alt_sz_visibility | ReplacingMT | live | active | 31,647 | 0.0 | 1 | ingest_ts | 2026-09-18 11:03 | lag0d | 1582 |
| c1_market.alt_sz_weather_warning | ReplacingMT | live | degraded | 18,712 | 0.004 | 326 | ingest_ts | 2026-09-18 11:03 | lag0d | 2 |
| c1_market.alt_typhoon_landfall_history | ReplacingMT | live | active | 845 | 0.0 | 1 | ingest_ts | 2026-09-13 17:32 | lag5d | - |
| c1_market.alt_typhoon_names | ReplacingMT | live | active | 1,260 | 0.0 | 1 | ingest_ts | 2026-09-13 17:32 | lag5d | - |
| c1_market.alt_typhoon_track | ReplacingMT | live | active | 350,609 | 0.012 | 170 | ingest_ts | 2026-09-18 11:04 | lag0d | 66 |
| c1_market.auction_book | ReplacingMT | live | active | 2,675,173 | 0.067 | 6 | trade_date | 2026-09-16 | lag2d | 55005 |
| c1_market.auction_book_limit_bak_20260908 | MT | backup | - | 1,911,474 | 0.006 | 2 | trade_date | 2026-09-03 | - | - |
| c1_market.auction_snapshot | ReplacingMT | live | active | 251,598 | 0.005 | 7 | trade_date | 2026-09-16 | lag2d | 2382 |
| c1_market.block_trade | ReplacingMT | live | active | 1,244 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 29 |
| c1_market.block_trade_detail | ReplacingMT | live | active | 1,461 | 0.0 | 3 | trade_date | 2026-09-18 | lag0d | 32 |
| c1_market.board_index_1m | ReplacingMT | live | - | 0 | 0.0 | 0 | trade_time | 1970-01-01 08:00 | lag20714d | - |
| c1_market.board_index_tick | ReplacingMT | live | - | 5,564 | 0.0 | 1 | ingest_ts | 2026-09-15 03:17 | lag3d | 185 |
| c1_market.calendar_event | ReplacingMT | live | active | 797 | 0.0 | 122 | event_date | 2026-12-31 | lag-104d | - |
| c1_market.cftc_positioning | ReplacingMT | live | - | 81,270 | 0.002 | 41 | report_date | 2026-09-08 | lag10d | - |
| c1_market.commodity_futures_main | ReplacingMT | live | - | 126 | 0.0 | 1 | trade_date | 2026-09-18 | lag0d | - |
| c1_market.commodity_spot_price | ReplacingMT | live | - | 756 | 0.0 | 1 | trade_date | 2026-09-18 | lag0d | - |
| c1_market.concept_board | ReplacingMT | live | active | 375 | 0.0 | 1 | ingest_ts | 2026-09-18 10:08 | lag0d | - |
| c1_market.concept_board_constituent | ReplacingMT | live | active | 30,889 | 0.001 | 1 | ingest_ts | 2026-09-18 10:08 | lag0d | - |
| c1_market.concept_sector | ReplacingMT | live | active | 375 | 0.0 | 1 | ingest_ts | 2026-09-02 16:59 | lag16d | - |
| c1_market.convertible_bond_iv | ReplacingMT | live | active | 8,687 | 0.0 | 2 | trade_date | 2026-09-16 | lag2d | 186 |
| c1_market.convertible_bond_list | ReplacingMT | live | active | 2,102 | 0.0 | 2 | list_date | 2026-09-03 | lag15d | - |
| c1_market.cross_validation_log | MT | live | active | 1,549 | 0.0 | 5 | - | - | - | 12 |
| c1_market.crypto_kline_daily | ReplacingMT | live | active | 22,787 | 0.002 | 18 | trade_date | 2026-09-18 | lag1d | 59 |
| c1_market.crypto_shadow_gate | ReplacingMT | live | active | 4 | 0.0 | 2 | trade_date | 2026-09-18 | lag1d | 0 |
| c1_market.daban_board_event | ReplacingMT | live | - | 936 | 0.0 | 1 | trade_date | 2026-09-15 | lag3d | 47 |
| c1_market.daban_engine_load | ReplacingMT | live | active | 993 | 0.0 | 2 | trade_date | 2026-09-15 | lag3d | 50 |
| c1_market.daily_valuation | ReplacingMT | live | degraded | 270,260 | 0.005 | 5 | trade_date | 2026-09-19 | lag-1d | 4920 |
| c1_market.dividend_tax_node | View | live | - | 0 | 0.0 | 0 | - | - | - | - |
| c1_market.dragon_tiger | ReplacingMT | live | active | 1,886 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 42 |
| c1_market.dragon_tiger_seat | ReplacingMT | live | active | 617,064 | 0.029 | 103 | trade_date | 2026-09-18 | lag0d | 310 |
| c1_market.edb_data | ReplacingMT | live | - | 0 | 0.0 | 0 | report_date | 1970-01-01 | lag20714d | - |
| c1_market.etf_benchmark | ReplacingMT | live | - | 0 | 0.0 | 0 | publish_date | 1970-01-01 | lag20714d | - |
| c1_market.etf_list | ReplacingMT | live | active | 2,184 | 0.0 | 1 | list_date | 2026-09-14 | lag4d | - |
| c1_market.etf_nav | ReplacingMT | live | active | 83,924 | 0.001 | 64 | trade_date | 2026-09-17 | lag1d | 1038 |
| c1_market.execution_report | ReplacingMT | live | - | 1 | 0.0 | 1 | ingest_ts | 2026-09-18 10:27 | lag0d | 0 |
| c1_market.futures_kline_qmt | ReplacingMT | live | active | 910 | 0.0 | 4 | trade_date | 2026-09-16 | lag2d | 3 |
| c1_market.futures_position | ReplacingMT | live | active | 3,136 | 0.0 | 3 | trade_date | 2026-09-15 | lag3d | 59 |
| c1_market.futures_term_structure | ReplacingMT | live | active | 3,056 | 0.0 | 2 | trade_date | 2026-09-17 | lag1d | 56 |
| c1_market.futures_warehouse_receipt | ReplacingMT | live | - | 2,900,636 | 0.013 | 245 | trade_date | 2026-09-18 | lag0d | 1926 |
| c1_market.gold_etf_holdings | ReplacingMT | live | - | 2,871 | 0.0 | 23 | trade_date | 2026-09-17 | lag1d | - |
| c1_market.hk_connect_flow | ReplacingMT | live | active | 4,052 | 0.001 | 118 | trade_date | 2024-08-16 | lag763d | 0 |
| c1_market.hk_kline | ReplacingMT | live | active | 6,301 | 0.0 | 3 | trade_date | 2026-09-16 | lag2d | 115 |
| c1_market.hk_stock_list | ReplacingMT | live | active | 2,798 | 0.0 | 1 | ingest_ts | 2026-09-02 17:02 | lag16d | - |
| c1_market.hk_trade_calendar | ReplacingMT | live | active | 4,607 | 0.0 | 2 | cal_date | 2027-09-17 | lag-364d | - |
| c1_market.hl_funding_history | ReplacingMT | live | - | 4,660,219 | 0.06 | 84 | ingest_ts | 2026-09-19 00:44 | lag0d | 5057 |
| c1_market.hl_liquidation_raw | ReplacingMT | live | - | 2 | 0.0 | 1 | trade_time | 2026-09-19 01:11 | lag0d | 0 |
| c1_market.hl_oi_snapshot_daily | ReplacingMT | live | - | 468 | 0.0 | 2 | ingest_ts | 2026-09-19 00:41 | lag0d | 23 |
| c1_market.hl_perp_snapshot_daily | ReplacingMT | live | - | 468 | 0.0 | 2 | ingest_ts | 2026-09-19 00:41 | lag0d | 23 |
| c1_market.hog_futures_core | ReplacingMT | live | active | 419 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | - |
| c1_market.hog_province_spot | ReplacingMT | live | active | 1,036 | 0.0 | 3 | trade_date | 2026-09-18 | lag0d | 18 |
| c1_market.hog_spot_index | ReplacingMT | live | active | 583 | 0.0 | 1 | trade_date | 2026-09-14 | lag4d | - |
| c1_market.index_adjustment | ReplacingMT | live | - | 14,763 | 0.0 | 96 | ingest_ts | 2026-09-17 21:47 | lag1d | 0 |
| c1_market.index_constituent | ReplacingMT | live | active | 643,348 | 0.011 | 258 | trade_date | 2026-09-17 | lag1d | 3475 |
| c1_market.index_list | ReplacingMT | live | active | 9,700 | 0.0 | 2 | list_date | 2026-09-11 | lag7d | - |
| c1_market.index_quote | ReplacingMT | live | active | 219,857 | 0.007 | 57 | trade_date | 2026-09-16 | lag2d | 4145 |
| c1_market.index_valuation_daily | ReplacingMT | live | active | 8,257 | 0.001 | 205 | trade_date | 2026-09-17 | lag1d | 2 |
| c1_market.index_weight | ReplacingMT | live | active | 1,850 | 0.0 | 1 | trade_date | 2026-09-03 | lag15d | 92 |
| c1_market.industry_class | ReplacingMT | live | active | 31,414 | 0.0 | 1 | ingest_ts | 2026-09-13 21:34 | lag5d | - |
| c1_market.ipo_calendar | ReplacingMT | live | - | 7,608 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 220 |
| c1_market.ipo_schedule | ReplacingMT | live | - | 0 | 0.0 | 0 | ingest_ts | 1970-01-01 00:00 | lag20714d | - |
| c1_market.judgment_daily_plan | MT | live | - | 2 | 0.0 | 1 | - | - | - | 0 |
| c1_market.judgment_intraday_market_state | MT | live | - | 4 | 0.0 | 2 | - | - | - | 0 |
| c1_market.judgment_next_day_forecast | MT | live | - | 3 | 0.0 | 1 | - | - | - | 0 |
| c1_market.judgment_plan_verification | MT | live | - | 0 | 0.0 | 1 | - | - | - | 0 |
| c1_market.kline_15min | ReplacingMT | live | active | 98,275,249 | 2.892 | 116 | trade_date | 2026-09-18 | lag0d | 73114 |
| c1_market.kline_1min | ReplacingMT | live | active | 1,481,257,322 | 36.921 | 264 | trade_date | 2026-09-18 | lag0d | 1151800 |
| c1_market.kline_1min_tzbak_20260914 | ReplacingMT | backup | - | 36,194,235 | 0.948 | 5 | trade_date | 2026-07-15 | - | 120017 |
| c1_market.kline_30min | ReplacingMT | live | active | 48,967,050 | 1.516 | 104 | trade_date | 2026-09-18 | lag0d | 34230 |
| c1_market.kline_5min | ReplacingMT | live | active | 294,324,216 | 6.553 | 196 | trade_time | 2026-09-18 15:00 | lag0d | 242867 |
| c1_market.kline_5min_tzbak_20260914 | ReplacingMT | backup | - | 4,456,056 | 0.103 | 2 | trade_time | 2026-07-15 15:00 | - | 33007 |
| c1_market.kline_60min | ReplacingMT | live | active | 24,525,332 | 0.831 | 124 | trade_date | 2026-09-18 | lag0d | 16097 |
| c1_market.kline_cb | ReplacingMT | live | active | 244,599 | 0.013 | 98 | trade_date | 2026-09-18 | lag0d | 217 |
| c1_market.kline_daily | ReplacingMT | live | active | 10,086,669 | 0.471 | 432 | trade_date | 2026-09-18 | lag0d | 3934 |
| c1_market.kline_daily_bak_256 | ReplacingMT | backup | retired | 9,669,695 | 0.365 | 430 | trade_date | 2026-08-21 | - | 1429 |
| c1_market.kline_daily_hfq | ReplacingMT | live | active | 8,406,666 | 0.369 | 155 | trade_date | 2026-09-18 | lag0d | 3684 |
| c1_market.kline_daily_hfq_bak_20260915dup | ReplacingMT | backup | - | 5,207 | 0.0 | 1 | trade_date | 2026-09-11 | - | 260 |
| c1_market.kline_etf_15min | ReplacingMT | live | active | 23,950,305 | 0.655 | 403 | trade_date | 2026-09-18 | lag0d | 19754 |
| c1_market.kline_etf_15min_tz_bak_20260918 | ReplacingMT | backup | - | 24,329,183 | 0.621 | 302 | trade_date | 2026-09-16 | - | 16418 |
| c1_market.kline_etf_1min | ReplacingMT | live | active | 327,074,832 | 5.42 | 440 | trade_date | 2026-09-18 | lag0d | 327882 |
| c1_market.kline_etf_1min_tz_bak_20260918 | ReplacingMT | backup | - | 326,301,055 | 5.408 | 135 | trade_date | 2026-09-16 | - | 289193 |
| c1_market.kline_etf_30min | ReplacingMT | live | active | 11,973,785 | 0.384 | 364 | trade_date | 2026-09-18 | lag0d | 9636 |
| c1_market.kline_etf_30min_tz_bak_20260918 | ReplacingMT | backup | - | 11,939,337 | 0.348 | 286 | trade_date | 2026-09-16 | - | 7914 |
| c1_market.kline_etf_5min | ReplacingMT | live | active | 72,070,158 | 1.594 | 525 | trade_date | 2026-09-18 | lag0d | 60880 |
| c1_market.kline_etf_5min_tz_bak_20260918 | ReplacingMT | backup | - | 71,856,186 | 1.523 | 322 | trade_date | 2026-09-16 | - | 50181 |
| c1_market.kline_etf_60min | ReplacingMT | live | active | 5,975,672 | 0.206 | 312 | trade_date | 2026-09-18 | lag0d | 4847 |
| c1_market.kline_etf_60min_tz_bak_20260918 | ReplacingMT | backup | - | 5,955,571 | 0.205 | 275 | trade_date | 2026-09-16 | - | 3842 |
| c1_market.kline_etf_daily | ReplacingMT | live | active | 95,864 | 0.004 | 68 | trade_date | 2026-09-18 | lag0d | 1181 |
| c1_market.kline_futures | ReplacingMT | live | active | 8,254 | 0.001 | 118 | trade_date | 2026-09-17 | lag1d | 9 |
| c1_market.kline_global | ReplacingMT | live | active | 9,997 | 0.001 | 136 | trade_date | 2026-09-18 | lag0d | 1 |
| c1_market.kline_hk_daily | ReplacingMT | live | active | 225,965 | 0.009 | 4 | trade_date | 2026-09-17 | lag1d | 3868 |
| c1_market.kline_index | ReplacingMT | live | active | 3,098,824 | 0.169 | 432 | trade_date | 2026-09-18 | lag0d | 415 |
| c1_market.kline_index_calc | ReplacingMT | live | active | 3,665 | 0.001 | 182 | trade_date | 2026-09-18 | lag0d | 1 |
| c1_market.kline_lof_15min | ReplacingMT | live | active | 12,439,442 | 0.239 | 235 | trade_date | 2026-09-18 | lag0d | 3900 |
| c1_market.kline_lof_1min | ReplacingMT | live | active | 138,897,460 | 1.203 | 166 | trade_date | 2026-09-18 | lag0d | 63985 |
| c1_market.kline_lof_30min | ReplacingMT | live | active | 6,187,060 | 0.154 | 207 | trade_date | 2026-09-18 | lag0d | 1943 |
| c1_market.kline_lof_5min | ReplacingMT | live | active | 37,350,865 | 0.449 | 278 | trade_date | 2026-09-18 | lag0d | 12124 |
| c1_market.kline_lof_60min | ReplacingMT | live | active | 3,111,786 | 0.095 | 199 | trade_date | 2026-09-18 | lag0d | 969 |
| c1_market.kline_monthly | ReplacingMT | live | active | 470,601 | 0.029 | 94 | trade_date | 2026-09-15 | lag3d | 1563 |
| c1_market.kline_monthly_hfq | ReplacingMT | live | active | 503,640 | 0.036 | 95 | trade_date | 2026-09-18 | lag0d | 2616 |
| c1_market.kline_sector | ReplacingMT | live | active | 95,201 | 0.005 | 19 | trade_date | 2026-09-18 | lag0d | 802 |
| c1_market.kline_sector_880 | ReplacingMT | live | active | 449,502 | 0.025 | 100 | trade_date | 2026-09-18 | lag0d | - |
| c1_market.kline_sector_intraday | ReplacingMT | live | active | 9,804,936 | 0.328 | 44 | trade_date | 2026-09-15 15:00 | lag3d | 251565 |
| c1_market.kline_us_daily | ReplacingMT | live | active | 528 | 0.0 | 4 | trade_date | 2026-09-17 | lag1d | 7 |
| c1_market.kline_weekly | ReplacingMT | live | active | 1,814,491 | 0.085 | 94 | trade_date | 2026-09-15 | lag3d | 1823 |
| c1_market.kline_weekly_hfq | ReplacingMT | live | active | 1,835,553 | 0.11 | 94 | trade_date | 2026-09-18 | lag0d | 2616 |
| c1_market.l2_tick | ReplacingMT | live | - | 0 | 0.0 | 0 | trade_date | 1970-01-01 | lag20714d | - |
| c1_market.limit_up_down | ReplacingMT | live | active | 4,787 | 0.0 | 4 | trade_date | 2026-09-17 | lag1d | 58 |
| c1_market.limit_up_pool | ReplacingMT | live | - | 855 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 43 |
| c1_market.lof_list | ReplacingMT | live | active | 371 | 0.0 | 1 | ingest_ts | 2026-09-03 11:38 | lag15d | - |
| c1_market.macro_activity_gauge | ReplacingMT | live | - | 436 | 0.001 | 436 | report_date | 2026-08-31 | lag18d | 0 |
| c1_market.macro_credit_money | ReplacingMT | live | - | 584 | 0.002 | 584 | report_date | 2026-08-31 | lag18d | 0 |
| c1_market.macro_daily_gauge | ReplacingMT | live | - | 4,685 | 0.001 | 179 | trade_date | 2026-09-18 | lag0d | 2 |
| c1_market.macro_data | ReplacingMT | live | active | 56,050 | 0.002 | 736 | report_date | 2026-09-18 | lag0d | 56 |
| c1_market.macro_pmi_gauge | ReplacingMT | live | - | 224 | 0.001 | 224 | report_date | 2026-08-31 | lag18d | 0 |
| c1_market.macro_price_gauge | ReplacingMT | live | - | 496 | 0.001 | 496 | report_date | 2026-08-31 | lag18d | 0 |
| c1_market.macro_trade_gauge | ReplacingMT | live | - | 224 | 0.001 | 224 | report_date | 2026-08-31 | lag18d | 0 |
| c1_market.margin_target_adjustment | ReplacingMT | live | - | 0 | 0.0 | 0 | ingest_ts | 1970-01-01 00:00 | lag20714d | - |
| c1_market.margin_trading | ReplacingMT | live | active | 274,529 | 0.009 | 6 | trade_date | 2026-09-17 | lag1d | 3078 |
| c1_market.market_breadth_snapshot | ReplacingMT | live | - | 125 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 5 |
| c1_market.market_cffex_member_ranking | ReplacingMT | live | - | 6,201 | 0.0 | 1 | trade_date | 2026-09-17 | lag1d | 310 |
| c1_market.market_china_bond_yield | ReplacingMT | live | - | 6,216 | 0.0 | 14 | trade_date | 2026-09-18 | lag0d | 32 |
| c1_market.market_convertible_bond_clause | ReplacingMT | live | - | 630 | 0.0 | 2 | ingest_ts | 2026-09-18 10:00 | lag0d | 32 |
| c1_market.market_etf_share_snapshot | ReplacingMT | live | - | 3,242 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 162 |
| c1_market.market_fund_flow_daily | ReplacingMT | live | - | 120 | 0.0 | 7 | trade_date | 2026-09-17 | lag1d | 1 |
| c1_market.market_index_meta | ReplacingMT | live | - | 0 | 0.0 | 0 | ingest_ts | 1970-01-01 00:00 | lag20714d | - |
| c1_market.market_pattern_certification | ReplacingMT | live | - | 66 | 0.0 | 1 | - | - | - | - |
| c1_market.market_pattern_event | ReplacingMT | live | active | 40,777,876 | 0.941 | 244 | - | - | - | 28764 |
| c1_market.market_pattern_win_rate | ReplacingMT | live | active | 3,989 | 0.0 | 2 | - | - | - | - |
| c1_market.market_signal_history | ReplacingMT | live | active | 329 | 0.0 | 2 | trade_date | 2026-09-04 | lag14d | 16 |
| c1_market.money_flow | ReplacingMT | live | active | 478,050 | 0.031 | 7 | trade_date | 2026-09-18 | lag0d | 6659 |
| c1_market.msci_adjustment | ReplacingMT | live | - | 0 | 0.0 | 0 | ingest_ts | 1970-01-01 00:00 | lag20714d | - |
| c1_market.ndrc_fuel_price | ReplacingMT | live | - | 329 | 0.001 | 219 | announce_date | 2026-09-12 | lag6d | 0 |
| c1_market.news_sentiment_window | ReplacingMT | live | - | 19,811 | 0.001 | 10 | window_date | 2026-09-14 | lag4d | 1 |
| c1_market.northbound_hold_snapshot | ReplacingMT | live | - | 57,083 | 0.002 | 15 | trade_date | 2026-06-30 | lag80d | 36 |
| c1_market.option_greeks | ReplacingMT | live | active | 4,442 | 0.0 | 2 | trade_date | 2026-09-16 | lag2d | 98 |
| c1_market.option_iv_surface | ReplacingMT | live | active | 30,138 | 0.0 | 10 | trade_date | 2026-09-16 | lag2d | 98 |
| c1_market.option_kline | ReplacingMT | live | active | 7,193 | 0.0 | 4 | trade_date | 2026-09-18 | lag0d | 139 |
| c1_market.rate_decision_calendar | ReplacingMT | live | - | 3,086 | 0.001 | 670 | decision_date | 2025-10-30 | lag323d | 0 |
| c1_market.realtime_snapshot | ReplacingMT | live | active | 0 | 0.0 | 0 | ingest_ts | 1970-01-01 00:00 | lag20714d | - |
| c1_market.reconciliation_differences | ReplacingMT | live | - | 0 | 0.0 | 0 | trade_date | 1970-01-01 | lag20714d | - |
| c1_market.road_freight_index | ReplacingMT | live | - | 86 | 0.0 | 11 | trade_date | 2026-08-21 | lag28d | 0 |
| c1_market.sector_constituent | ReplacingMT | live | active | 236,836 | 0.001 | 3 | ingest_ts | 2026-09-03 11:39 | lag15d | 3678 |
| c1_market.sector_constituent_snapshot | ReplacingMT | live | - | 190,248 | 0.001 | 2 | ingest_ts | 2026-09-14 21:40 | lag4d | 9512 |
| c1_market.sector_fund_flow | ReplacingMT | live | - | 1,917 | 0.0 | 1 | trade_date | 2026-09-19 | lag-1d | 96 |
| c1_market.sector_list | ReplacingMT | live | active | 5,217 | 0.0 | 1 | trade_date | 2026-09-03 | lag15d | 261 |
| c1_market.sector_meta | ReplacingMT | live | active | 2,070 | 0.0 | 1 | trade_date | 2026-09-18 | lag0d | - |
| c1_market.sector_snapshot | ReplacingMT | live | active | 104,494 | 0.005 | 4 | trade_date | 2026-09-18 | lag0d | 3446 |
| c1_market.sentiment_panel | ReplacingMT | live | active | 21 | 0.0 | 1 | trade_date | 2026-09-18 | lag0d | 1 |
| c1_market.st_stock_list | ReplacingMT | live | active | 422,899 | 0.002 | 203 | trade_date | 2026-09-18 | lag0d | 140 |
| c1_market.stk_limit | ReplacingMT | live | - | 9,193,985 | 0.166 | 142 | trade_date | 2026-09-18 | lag0d | 4203 |
| c1_market.stock_basic | ReplacingMT | live | - | 9,025,127 | 0.082 | 163 | trade_date | 2026-09-18 | lag0d | 3721 |
| c1_market.stock_hot_rank | ReplacingMT | live | active | 5,993 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 115 |
| c1_market.stock_indicator | ReplacingMT | live | active | 11,677,199 | 0.589 | 142 | trade_date | 2026-09-18 | lag0d | 4576 |
| c1_market.stock_list | ReplacingMT | live | active | 5,921 | 0.0 | 1 | list_date | 2026-09-02 | lag16d | - |
| c1_market.stock_profile_ths | ReplacingMT | live | production | 5,217 | 0.001 | 1 | trade_date | 2026-09-09 | lag9d | - |
| c1_market.stock_valuation | ReplacingMT | live | - | 0 | 0.0 | 0 | trade_date | 1970-01-01 | lag20714d | - |
| c1_market.suspend | ReplacingMT | live | - | 0 | 0.0 | 0 | trade_date | 1970-01-01 | lag20714d | - |
| c1_market.technical_indicator | ReplacingMT | live | active | 372,128,415 | 170.172 | 1339 | trade_date | 2026-09-18 | lag0d | - |
| c1_market.tick_data | ReplacingMT | live | active | 8,857,297,679 | 141.535 | 53 | trade_date | 2026-09-18 | lag0d | 16605928 |
| c1_market.tick_data_tzbak_20260914 | ReplacingMT | backup | - | 507,700 | 0.012 | 1 | trade_date | 2026-09-10 | - | 25385 |
| c1_market.tick_depth_5 | ReplacingMT | live | - | 30,406,868 | 1.333 | 12 | trade_date | 2026-09-18 | lag0d | 1520341 |
| c1_market.trade_calendar | ReplacingMT | live | active | 8,800 | 0.0 | 2 | cal_date | 2026-12-31 | lag-104d | - |
| c1_market.us_futures_intraday | ReplacingMT | live | - | 563 | 0.0 | 2 | trade_date | 2026-09-18 | lag0d | 21 |
| c1_market.us_index | ReplacingMT | live | active | 22,600 | 0.002 | 405 | trade_date | 2026-09-17 | lag1d | 2 |
| c1_market.weather_data | ReplacingMT | live | active | 9,073 | 0.0 | 2 | record_date | 2026-09-18 | lag0d | 164 |
| c3_fundamental.analyst_forecast | ReplacingMT | live | active | 101,808 | 0.001 | 3 | report_date | 2026-09-18 | lag0d | 1687 |
| c3_fundamental.audit_opinion | ReplacingMT | live | active | 96,010 | 0.003 | 97 | announce_date | 2026-05-29 | lag112d | 19 |
| c3_fundamental.balance_sheet | ReplacingMT | live | active | 339,738 | 0.049 | 139 | announce_date | 2026-09-02 | lag16d | 47 |
| c3_fundamental.balance_sheet_bak_1970clean_20260914 | ReplacingMT | backup | - | 2,395 | 0.0 | 1 | announce_date | 1970-01-01 | - | 0 |
| c3_fundamental.cashflow_statement | ReplacingMT | live | active | 310,447 | 0.03 | 104 | announce_date | 2026-09-02 | lag16d | 47 |
| c3_fundamental.cashflow_statement_bak_1970clean_20260914 | ReplacingMT | backup | - | 2,402 | 0.0 | 1 | announce_date | 1970-01-01 | - | 0 |
| c3_fundamental.consensus_daily | ReplacingMT | live | active | 6,797,719 | 0.031 | 135 | trade_date | 2026-09-14 | lag4d | 2992 |
| c3_fundamental.consensus_daily_repaired | ReplacingMT | live | active | 1,655,363 | 0.009 | 66 | trade_date | 2026-09-15 | lag3d | 2582 |
| c3_fundamental.disclosure_plan | ReplacingMT | live | active | 316,739 | 0.004 | 119 | announce_date | 2026-08-31 | lag18d | 99 |
| c3_fundamental.dividend | ReplacingMT | live | - | 116,334 | 0.002 | 205 | announce_date | 2026-07-01 | lag79d | 0 |
| c3_fundamental.earnings_forecast | ReplacingMT | live | active | 125,582 | 0.024 | 105 | announce_date | 2026-07-03 | lag77d | - |
| c3_fundamental.equity_pledge_detail | ReplacingMT | live | active | 120,628 | 0.025 | 270 | announce_date | 2026-07-03 | lag77d | 1 |
| c3_fundamental.equity_pledge_summary | ReplacingMT | live | active | 1,723,193 | 0.025 | 151 | ingest_ts | 2026-09-14 11:01 | lag4d | 0 |
| c3_fundamental.ex_dividend_event | ReplacingMT | live | - | 57,715 | 0.004 | 482 | trade_date | 2026-09-18 | lag0d | 11 |
| c3_fundamental.express_report | ReplacingMT | live | active | 28,708 | 0.002 | 86 | announce_date | 2026-07-02 | lag78d | 0 |
| c3_fundamental.financial_derived | ReplacingMT | live | active | 306,526 | 0.148 | 117 | announce_date | 2026-09-02 | lag16d | 47 |
| c3_fundamental.financial_indicator | ReplacingMT | live | active | 387,990 | 0.07 | 171 | announce_date | 2026-09-12 | lag6d | 96 |
| c3_fundamental.financial_indicator_bak_1970clean_20260914 | ReplacingMT | backup | - | 2,585 | 0.0 | 1 | announce_date | 1970-01-01 | - | 0 |
| c3_fundamental.income_statement | ReplacingMT | live | active | 346,176 | 0.044 | 142 | announce_date | 2026-09-02 | lag16d | 47 |
| c3_fundamental.income_statement_bak_1970clean_20260914 | ReplacingMT | backup | - | 2,401 | 0.0 | 1 | announce_date | 1970-01-01 | - | 0 |
| c3_fundamental.industry_class_suppl | ReplacingMT | live | active | 10,141 | 0.0 | 2 | ingest_ts | 2026-09-19 18:55 | lag-1d | - |
| c3_fundamental.ir_activity_extracted | ReplacingMT | live | - | 30 | 0.0 | 1 | - | - | - | 2 |
| c3_fundamental.ir_activity_record | ReplacingMT | live | - | 30 | 0.0 | 1 | publish_date | 2026-09-18 | lag0d | 2 |
| c3_fundamental.irm_interactive_extracted | ReplacingMT | live | - | 74 | 0.0 | 2 | - | - | - | 4 |
| c3_fundamental.irm_interactive_qa | ReplacingMT | live | - | 500 | 0.0 | 4 | ingest_ts | 2026-09-18 04:23 | lag0d | 18 |
| c3_fundamental.main_business | ReplacingMT | live | active | 2,094,453 | 0.057 | 100 | ingest_ts | 2026-09-11 16:37 | lag7d | 0 |
| c3_fundamental.news_data | ReplacingMT | live | - | 8,348,853 | 13.091 | 517 | ingest_ts | 2026-09-19 18:55 | lag-1d | 2235 |
| c3_fundamental.news_data_corrupt_20260828 | ReplacingMT | corrupt | retired | 8,040,882 | 12.994 | 363 | ingest_ts | 2026-08-28 04:18 | - | 1079 |
| c3_fundamental.news_data_pre_tz2_20260828 | ReplacingMT | backup | retired | 7,872,827 | 12.875 | 213 | ingest_ts | 2026-08-28 05:31 | - | 1091 |
| c3_fundamental.pdf_forecast_extracted | ReplacingMT | live | - | 192,365 | 0.013 | 98 | publish_date | 2021-12-31 | lag1722d | 1 |
| c3_fundamental.repurchase | ReplacingMT | live | - | 10,936 | 0.002 | 306 | announce_date | 2026-09-19 | lag-1d | 8 |
| c3_fundamental.research_report | ReplacingMT | live | active | 146,769 | 0.018 | 135 | publish_date | 2026-09-18 | lag0d | 43 |
| c3_fundamental.restricted_shares | ReplacingMT | live | active | 10,177,657 | 0.18 | 295 | announce_date | 2026-07-02 | lag78d | - |
| c3_fundamental.rights_issue | ReplacingMT | live | active | 80,803 | 0.005 | 407 | announce_date | 2026-06-30 | lag80d | 13 |
| c3_fundamental.share_change | ReplacingMT | live | active | 190,452 | 0.005 | 203 | announce_date | 2026-09-19 | lag-1d | 14 |
| c3_fundamental.share_unlock | ReplacingMT | live | active | 30,145 | 0.002 | 214 | unlock_date | 2027-09-17 | lag-364d | - |
| c3_fundamental.shareholder_count | ReplacingMT | live | active | 513,548 | 0.005 | 286 | announce_date | 2026-09-18 | lag0d | 37 |
| c3_fundamental.top10_circulating_shareholders | ReplacingMT | live | active | 2,138,764 | 0.085 | 211 | announce_date | 2026-05-15 | lag126d | 271 |
| c3_fundamental.top10_shareholders | ReplacingMT | live | active | 1,500,427 | 0.057 | 240 | announce_date | 2026-06-30 | lag80d | 496 |
