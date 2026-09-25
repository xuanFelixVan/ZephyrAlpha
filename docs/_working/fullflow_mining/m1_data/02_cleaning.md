---
ttl: task_bound
lane: M1 数据链
segment: D4 清洗校验与坏数修复 + D5 判重与数据审计
mined_at: 2026-09-25
session: st-commitspeed-tbl-20260924
---

# 02_cleaning — 清洗段作业簿（D4/D5）

> 前序战役继承声明：本册在 docs/_working/automation/campaign/mining/04_洗数据/工段作业簿.md（st-mineline-20260918）基础上**增量重挖**，行号与闭环状态全部按 2026-09-24 现场重新核实（该簿多处已被后续战役改变状态，差异逐条标注）。

## 一、环节定义与边界

一句话：写前规则门禁 + 三班哨兵（断供/变异/完整性）+ 缺口回补自愈 + 判重正门 + 事故驱动修复兵器，把原料修成决策级 clean 层。
- **供料方**：01_ingest 的 FetchResult 流。
- **消费方**：03_ch_warehouse（clean 行落库）、02 自产的修复/回补命令面。

## 二、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游输入 | 采集侧 FetchResult + 既有脏数据（1970 残留/时区偏移/幽灵日/零值行）+ 已知缺口清单（known_data_gaps.yaml 63 条） |
| 下游消费 | ch_writer.py:971-986（写路径内联 apply_quality_gate，flagged WARN :976）；integrity_check 班 subprocess 调 check_tick_duplication（integrity_checker.py:54-66） |
| 自动化触发 | **三班哨兵全部挂 06:50 data_supply_sentinel 槽**（schedule.yaml:228-236）：supply_sentinel（58 条腿，yaml 实数）宿主托管 quality_sentinel 7 天节奏闸（config/quality_sentinel_tables.yaml:103-106 wiring 块）；integrity_check 17:xx 日批（L11）；weekend_backfill/daily_backfill（L10/L10.5 缺口回补）；catchup_guard 05:30（L10.7）；consensus_crosscheck 日批（双向对答案）；eod_reconciliation 15:40（三账核对，recon_runner.py）；停摆总闸=data/runtime/quality_sentinel.disabled（标记文件实查机制） |
| 真源与注册表 | 哨兵表册=config/quality_sentinel_tables.yaml（**9 表**，grep 实数）；断供阈值=src/zephyr/data/config/data_supply_sentinel.yaml（58 腿，含 allow_empty 永久静默开关 BRK-046 收口纪律）；判重判据=scripts/governance/data_quality/check_tick_duplication.py:18-23（**14 字段全同才算真重复，禁 count-uniqExact**）；RULE-DATA-OPS=trae_063_data_ops_discipline.yaml |
| 门禁与质量尺 | 写前四门禁（ohlc/change/swing/adj 四类 FailureReason，gov_enforcement/rule_enforcement/quality_gate.py，失败不阻断写入 ch_writer.py:923-925）；quality_sentinel 四检测器（epoch/tz_shift/empty_segment/non_trading_day，quality_sentinel.py 模块头）；supply_sentinel 六维判据（row_filter/lag_basis/cadence/min_rows_in_window/column_fill_ratio/heartbeat_leg+blind_spots，:31-40）；AI 清洗考尺=config/cleaning_policy.yaml（L3 抽验协议 v0，OBJ_R 通道） |
| 当前运行状态 | **绿**。哨兵班 06:50 每日（DataScheduler Running 承载）；tick 判重走 integrity_check 班自动；实测发现能力在案：rate_decision_calendar 435 行 epoch 残留、daily_valuation 77,668 幽灵行、futures_warehouse_receipt SHFE 停 305 天均被哨兵捕获入册（quality_sentinel_tables.yaml:72-97 与 supply_sentinel.py 头注释=检测面工作证明） |

## 三、子模块清单（file:line 实核）

| 模块 | 入口 | 状态（vs 04_洗数据簿 09-18 版的差异） |
|---|---|---|
| 写前质量门禁 | ch_writer.py:971-986 | production，无变化 |
| quality_sentinel（1970/tz/空段/非交易日哨兵） | quality_sentinel.py（903 行，四检测器）+ config/quality_sentinel_tables.yaml | **新建成已接线**（09-18 簿记 WO-④-01 待立项→今已闭环：9 表在册+7 天节奏闸+停摆开关） |
| supply_sentinel（断供哨兵） | supply_sentinel.py（555 行）+ data_supply_sentinel.yaml（58 腿） | **新建**（09-18 之后）；六维判据扩容在案（:31-40） |
| check_tick_duplication | scripts/governance/data_quality/check_tick_duplication.py（357 行；2026-07-16 误删 21 个月 tick 事故治本件） | production；integrity_check 班唯一自动触发清洗件 |
| integrity_checker | integrity_checker.py（L11 日批，动态发现 tasks.yaml 全表） | production |
| backfill_checker / auto_backfiller | L10 七天行数扫描（不依赖 last_key，#ARCH-BACKFILL-001）/ 事件触发回填（新因子/公式升级/源修复） | production |
| catchup_guard | L10.7 任务档期 vs 打卡对账+自动补跑 | production（治 2026-09-01 monthly_static 空缺 32h） |
| cross_source_validator | QMT 主 vs TDX 备内容级比对（价格偏差阈值） | production（QMT 清退后待验证备源有效性） |
| consensus_crosscheck | 自建聚合 vs 同花顺快照双向验证（秩相关/覆盖/分布/新鲜度） | production |
| news_dedup | 标题 MD5 去重（MOD-L00-004 §4.3） | production |
| cleaning_rule_engine | cleaning_rule_engine.py（DSL gt/lt/between/rolling_quantile+滚动分位护栏） | **仍零调用**（2026-09-24 grep 实核：全仓仅 __init__.py re-export）——04 簿 WO-④-03 未闭环 |
| cleaning_anomaly_engine + data_anomaly_alerter | src/zephyr/data_eng/（前值填充≤3根/剔除必人工审核；静默窗 Fail-Closed） | **仍零调用**（同上，仅包 re-export） |
| 修复兵器 7 件 | scripts/data/repair_kline_tz_monthly.py、finish_p0_1.py、p02_month_gapfill.py、repair_kline_degraded_pull.py、wipe_tick3days.py；scripts/ch/repair_etf_minute_tz_split.py、rebuild_news_data.py+purge_news_data_rr_dup.py | manual 事故驱动；**ETF 4.12 亿行 tz 修复已结案归档**（docs/_working/archive/2026-09/flash_biz/biz5_etf15min_tz_defect.md，五表 max_date=2026-09-24 实查活体） |
| 隔离区 | data/local_fallback_quarantine/_README.txt（2026-09-15 手工隔离 11 条永久死信） | **仍手工**（src/scripts 零代码引用，WO-④-05 未闭环） |
| AI 判净站 | 不存在；config/cleaning_policy.yaml=考尺真源已立 | 待 Owner 门（花钱点唯一） |
| eod_reconciliation | src/zephyr/trading/recon_runner.py run_daily_reconciliation 三账核对 | production（15:40 班） |

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| C1 | 清洗三引擎（rule/anomaly/alerter）建成未接线，DSL 无 YAML 承载（config/ 无规则文件） | 写前只挂了四门禁一个点，三引擎无宿主班次 | 挂 supply_sentinel 宿主同款托管模式（先例现成）+ rules YAML 承载 | 1-2 天 | 是 |
| C2 | daily_valuation 77,668/259,238 幽灵行（29.96% 落 14 个周末幽灵日）+ 同表 close/amount/turnover 全 0 行——**检测已闭环（C-36 四维哨兵），清理未闭环** | DB 净删=Owner 门位（§5）；写入端日历闸（C-35/C-34）另案未落地 | 挂 pending_ruling 请 Owner 批清理窗+写侧日历闸立项 | 清理 0.5 天（批后） | 检测✅；清理=待裁 |
| C3 | rate_decision_calendar 435/3086 行 decision_date<1990-01-01（哨兵实测抓到） | 上游源纪元占位直写 | 同 C2：Owner 门清理+源侧哨兵占位约定（1970-01-01 语义已在 business_data_categories.yaml 头声明） | 0.5 天 | 清理=待裁 |
| C4 | 隔离区物理落点手工化（11 条死信无自动分拣/回灌/TTL） | ch_writer 死信链（:792-815 HTTP 失败→local_replay.save_fallback）与隔离目录无代码桥 | 死信落盘时同步登记隔离目录 manifest+TTL 扫描挂哨兵班 | 1 天 | 是 |
| C5 | 历史病灶闭环总核验：①tick 误删 21 月→判重正门**已闭环**；②kline_1min 2635 万行 1970 错位+15.6 亿行 -8h→修复三件套+quality_sentinel **已闭环**；③news_data 折叠吞数/research_report 2.0x 冗余→rebuild+purge 双件**已闭环**；④ETF 4.12 亿行→**已结案**；⑤hfq 复权链重算 WO-004（2026-09-24）adj_factor 21,055,022 行零重复+600519 全历史口径验证**已交付**（WO-004.md metrics，quarantine 表留观中） | — | — | — | — |

## 五、提速与合并机会

1. **哨兵三班一宿主**：integrity_check/supply_sentinel(+托管 quality_sentinel)/calendar_coverage_check 三个 06:50-07:10 班次共享 CH 连接与告警通道，可合并为一个"数据体检班"单入口多检测器（省 3 次进程冷启+重复表发现）。
2. **回补双轨合并**：weekend_backfill（L10 查 7 天）与 daily_backfill（L10.5 查当天）同用 backfill_checker._discover_backfill_tables，仅窗口参数不同——可合一任务双窗口。
3. cleaning_policy.yaml（AI L3 考尺）与三引擎接线合并立项：接线完成前 AI 判净无上游流量，考尺空转。

## 六、自审闸三态

**挖干可施工**（C1 接线、C4 隔离区自动化可直开；C2/C3 清理与 AI 判净=待裁，已登记 pending_rulings.md）。

## 七、复核命令

```bash
grep -c "^  - table:" config/quality_sentinel_tables.yaml                        # 9 表
grep -c "^  - table:" src/zephyr/data/config/data_supply_sentinel.yaml           # 58 腿
sed -n '971,986p' src/zephyr/data/ch_writer.py                                   # 写前门禁
grep -rn "cleaning_rule_engine" src/zephyr/ --include="*.py" | grep -v __pycache__  # 仅 __init__ re-export=零调用证
sed -n '18,23p' scripts/governance/data_quality/check_tick_duplication.py        # 14 字段判重铁律
sed -n '72,97p' config/quality_sentinel_tables.yaml                              # 幽灵行/epoch 病灶实测注
```
