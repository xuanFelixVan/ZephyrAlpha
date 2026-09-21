---
ttl: task_bound
title: 深度审查报告——TF15 monthly_static月度静态族(21任务+4停用)
object: TF15 monthly_static 月度静态任务族
target: "src/zephyr/data/config/tasks.yaml（schedule: monthly_static 实测 21 条，主锚 957/981/996/1012/1025/1039/1162/1434/1452/1701/1716/2048/2077-2264；schedule: disabled 4 条=704/3393/3410/3440）；schedule.yaml:121-125"
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审；任务书"20+dividend"为旧版口径，9/18 夜班新增 index_adjustment_derive 后=21+4）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF15 monthly_static月度静态族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **21 任务**（disabled 1：kline_5min_history_backfill）+4 条 `schedule: disabled`（dividend_incremental:704、futures_warehouse_receipt_backfill_czce:3393、shfe:3410、road_freight_index_full_refresh:3440——schedule 级停用约定）。cron `16 9 1 * *` 每月 1 日 09:16 default 池；不在交易日守卫集（月初遇周末靠逐任务 trading_day_only，_filter_schedule_tasks scheduler.py:358-360）。
- 事故背景：9/1 调度器 10:37 才被拉起整批错过→catchup_guard（L10.7 05:30 月度桶）治本（schedule.yaml:150-158）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **S6【族级核心发现】schedule:disabled 任务被 integrity_check 永久判缺**：_should_run_today 只排除 extra.disabled 与 _NON_DAILY_SCHEDULES 三档（integrity_checker.py:61-67,80-82），`schedule: disabled` 不是被识别的停用关键字——4 条停用任务每个交易日都进"应跑"名单却永不运行→**23:00 对账 ERROR 告警永久红**（任务级对账 missing 永含 4 任务）。告警疲劳=真缺口被淹没（checklist #6 反面：不是死了没人知，而是天天喊狼来了） | integrity_checker.py:61-67,80-82,302-317；tasks.yaml:704,3393,3410,3440 | P2 | 跑 run_daily_check 看 missing 列表恒含 4 任务 |
| A | 停用语义双轨：extra.disabled=true（经 _filter_schedule_tasks/integrity 识别）vs schedule: disabled（仅靠"无此 cron 槽位"自然不跑，_schedules 无 disabled 键）——后者**代码层无任何识别点**（grep 全库无 schedule=='disabled' 判断），属隐式约定，第三处消费方（未来新对账器）极易再犯 | scheduler.py:336-361；全库 grep 无 disabled 槽位判断 | P2 | grep -r "'disabled'" src/zephyr/data 验证零识别 |
| B | sector_list_refresh（miniqmt，get_stock_list_in_sector）无 fallback 且 trading_day_only: true——9/1 事故 8 缺表之一（schedule.yaml:152 自述"sector_list/index_list/hk_stock_list 等 8 表"）；月初遇周末跳过后靠 catchup 顺延到交易日补——链路成立但 sector_list 断供影响 kline_sector_intraday 符号解析（TF03 侧 _resolve_sector_symbols 用 sector_constituent 表非 sector_list——实际消费链待查，影响面或有限） | tasks.yaml:1716-1726；schedule.yaml:150-158；tdx_provider.py:295 | P3 | grep sector_list 消费方 |
| A | index_adjustment_derive（9/18 新增，internal）：快照差分→事件，effective_date 派生近似+announcement_date=PIT 诚实锚（tasks.yaml:2044-2061 注释自证）——依赖 index_constituent_refresh 同时段强约束有效；"第 2 个周五次一交易日"规则近似已声明为近似——口径诚实 | tasks.yaml:2044-2061 | 已查无 | 抽 000300 历史调仓日对照 |
| B | trade_calendar_refresh（baostock 主+akshare fb #ARCH-DATA-015 治本）与 hk_trade_calendar_refresh（internal exchange_calendars）→calendar_event_refresh（internal，依赖双日历）——日历族 DAG 同时段串联有效；**trade_calendar 是全系统交易日守卫的底座**（MarketCalendar 消费），其停更=所有守卫失效——该表在 supply_sentinel 16 表内（data_supply_sentinel.yaml:62 calendar_event 附近，实锚待核）——日历底座的哨兵覆盖是本族最高杠杆点 | tasks.yaml:981-994,2124-2149；data_supply_sentinel.yaml:28-124 | P2 | 核对 sentinel yaml 是否含 trade_calendar 本表（本次实测清单未列——若确无，为 P1 级哨兵盲区：日历停更→守卫静默失效） |
| D | st_namechange_backfill/kline_daily_delisted_backfill（幸存者偏差治理 JOB-083/084）与 stock_list_delisted_refresh upsert 共存——同表（stock_list/kline_daily/st_stock_list）多任务写侧按 update_mode/行键分区，幂等语义已注明 | tasks.yaml:1012-1023,1434-1464 | 已查无 | — |
| C | etf_benchmark_refresh 依赖 etf_list_refresh（同时段）——tushare 主源切源（P8）后 list_date 1970 前科治本留痕（tasks.yaml:2090）——历史缺陷闭环 | tasks.yaml:2088-2204 | 已查无 | — |
| F | 受阻（未检索）。 | — | 受阻 | — |

## 3 SOTA 对照
- 受阻。

## 4 缺陷清单
1. **P2 schedule:disabled 识别缺失→对账永久红（S6）**：修法（三选一）①integrity/catchup 识别 `schedule=='disabled'` ②4 任务补 extra.disabled: true ③停用统一走 extra.disabled 单轨并禁 schedule: disabled 写法→验证法=改后跑 run_daily_check 看 missing 清零。
2. P2 trade_calendar 哨兵确认/补配：日历底座停更=全守卫静默失效（若 sentinel 确无本表，升级 P1）。
3. P2 停用单轨化（见上 A 行）。

## 5 挂起疑问
- sector_constituent_refresh（tqcenter，requires tdx 客户端）月初 09:16 在非交易日运行——tdx 客户端周末是否可用未验证（trading_day_only 未配，与 miniqmt 拼写防护同缺口——tqcenter 非防护名单源）。
- index_adjustment_derive 的 effective_date 近似规则对 000985/000852 的适用性（中证细则）未逐条核。

## 6 完备性自评
六轴全查（F 受阻）。长尾：21 任务中 baostock 退市 universe 解析（JOB-084）与北交所缺口（tasks.yaml:1463 自认已知缺口）未深查；catchup_guard 月度桶的"空表兜底"实测未做。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
