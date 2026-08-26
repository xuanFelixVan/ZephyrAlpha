---
ttl: task_bound
---

# 市场日历消费点全量盘点报告（W0 / CAND-CRYPTO-001 / AI-CAL-001）

> 日期：2026-08-26 ｜ 依据：94 号 §4.1 + W0 派单步骤 1 ｜ 方法：预侦察 25 文件基线 + Grep 宽口径 60 文件全量复核 + 32 文件逐一精读

## 〇、结论摘要

- **无统一日历接口**（Step 1.5 结论确认）：全库 6 种日历假设形态并存，is_trading_day 语义 4 处独立实现（trading_calendar.py 函数式 / trading/reference_data_manager SQLite / tick_subscriber xtdata / feedback_loop holiday 集）。
- **四类消费点改造面**：①scheduler=模块级函数直调（改造）②K线聚合=已注入 trading_days，补 4h 频率（增量）③回测时间轴=数据驱动无日历假设（零改造，装配声明）④PIT asof=embargo 自然日口径（加可选 calendar 参数，默认不变）。
- **A股零行为变化路径**：A股实现=ASHareCalendar 薄封装委托 trading_calendar.py 真源（真源本体一行不动）；消费点改造=加 calendar 参数默认 None→A股实例。
- **同名区分**：feedback_loop.collectors.market_calendar.MarketCalendar（holiday 集合，FLE 防误报）与本任务接口同名不同义，新接口落 `src/zephyr/data/calendar/` 包以包路径区分。

## 一、假设形态分类法（6 类）

| 类 | 形态 | 改造方向 |
|---|---|---|
| A | 直接 import trading_calendar 函数直调 | 改注入 calendar 实例方法 |
| B | 硬编码交易时段（09:30/15:00 等） | calendar.session_windows(date) |
| C | 硬编码 weekday/BDay 周末判断 | calendar.is_trading_day / trading_days_in_range |
| D | 自带独立日历实现（XHKG/xtdata/SQLite） | 登记为市场实例，装配层按键注入 |
| E | 已参数化注入（trading_days/trading_calendar 参数） | 形态合规，装配层统一真源 |
| F | 无日历假设（数据驱动/自然日口径为有意设计） | 不动 |

## 二、四类核心消费点（W0 改造对象）

### ① scheduler（src/zephyr/data/scheduler.py）
| 位置 | 函数 | 形态 | 改造方式 |
|---|---|---|---|
| L94 | 模块级 import is_trading_day, TRADING_DAY_GUARDED_SCHEDULES | A | IntegratorScheduler.__init__ 加 calendar 参数（L386） |
| L199-216 | _schedule_should_skip：L201 is_trading_day 直调；L207 weekday>=5（interval 周末守卫） | A+C | 加 calendar 形参；is_trading_day 改实例调用；L207 属 A股调度语义保留 |
| L260-286 | _filter_schedule_tasks：L261 is_trading_day 直调 | A | 同上 |

### ② K线聚合（multi_timeframe 体系）
| 位置 | 函数 | 形态 | 改造方式 |
|---|---|---|---|
| multi_timeframe_fusion.py L49-56 | SUPPORTED_FREQS={1/5/15/30/60min,1d} 无 120min/4h | — | 增量加 "4h":240（A股路径不触碰，零行为变化） |
| multi_timeframe_fusion.py L114-183 | resample(trading_days=None) 日历对齐过滤桶 | E | 加可选 calendar 便利参数（内部展开为 trading_days；显式 trading_days 优先） |
| internal_compute_provider.py L956-992 | _aggregate_120min：2×60min 相邻配对（docstring 写 A股时段，实现无时刻硬编码） | F（A股管道专用） | 不动；币 4h 走 fusion 原生 floor 锚定 00:00 |
| technical_indicator_registry.yaml L25 | 9 周期（120min 由 60min 聚合） | 注册表层 | 币 4h=第 10 周期候选，W1 数据落地后登记 |

### ③ 回测时间轴（src/zephyr/backtest/）
| 位置 | 函数 | 形态 | 改造方式 |
|---|---|---|---|
| core/data_handler.py L128-134 | _normalize_data：时间轴=输入数据日期去重排序 | F | 零改造（时间轴数据驱动，天然市场无关） |
| implementations/vectorized_engine.py L276-283 | _get_sorted_dates 同上 | F | 零改造 |
| implementations/event_driven_engine.py L170+ | tick timestamp 驱动 | F | 零改造 |
| core/walk_forward.py L98-188 | split_*：dates 注入按位置切分 | E | 零改造（装配层注入 calendar.trading_days_in_range 产物） |
| core/pit_manager.py L218-270 | apply_embargo(trading_calendar=None)：None→BDay 近似（L261）；注入→真历锚定 | E | 零改造（BDay 默认分支为 A股既有语义，保留） |
| core/purged_kfold.py / cpcv.py | embargo=样本数 | F | 零改造 |

### ④ PIT asof（src/zephyr/data/pit_query.py）
| 位置 | 函数 | 形态 | 改造方式 |
|---|---|---|---|
| L152-161 | _embargo_clause：`- INTERVAL N DAY`（自然日） | F（自然日为声明口径） | PITQuery.__init__ 加可选 calendar 参数：提供交易日口径 embargo 可选路径，默认 None=自然日（现状零变化） |
| L263-264 | __init__(config) 注入点 | — | 同上 |

## 三、扩展消费点（W0 登记，后续波次改造）

### A 类（is_trading_day 直调）
- intelligence/event_score.py L75/L444-457（trading_days_ago 薄封装）
- runtime/intraday_main.py L141/L208-211（盘中守卫，force 旁路）
- ex_core/pre_execution_checker.py L59-94（时段+直调+weekday 降级三段）——**ex_core 避让区，W0 零触碰**；其 _ASHARE_SESSION_WINDOWS 语义由 ASHareCalendar.session_windows 收编（复制语义不改文件）

### B 类（硬编码时段）
- data/backfill_checker.py L521-525（093000/153000 补数分段）
- data/tick_subscriber.py L643-651（9*60+30<=hm<=15*60 盘中判定）
- plan_engine/scenario_planner.py L89-91（竞价三时刻）；closing_session_decision.py L63-64（14:45/15:00）；auction_hit_recorder.py L89-90；scenario_plan_recorder.py L115-116
- data/implementations/limit_up_pool_collector.py L142（15*3600 收盘基准）

### C 类（weekday/BDay 近似）
- data/backfill_checker.py L976；data/scheduler.py L207（见①）
- data/implementations/calendar_event_derivations.py L84-105（MLF/LPR/A50 顺延）
- data/implementations/internal_compute_provider.py L299-325（第n个星期x/LPR 顺延）
- plan_engine/overnight_boundary_reviser.py L166-189（A50 交割/下一工作日）
- pf_core/core/rebalance_scheduler.py L457（周五触发，节假日不落周四）
- position/core/calendar_position_constraint.py L459-496（_third_friday/_fourth_wednesday 交割算术）

### D 类（独立日历实现）
- data/implementations/internal_compute_provider.py L118-137（XHKG 港股历懒加载）
- data/tick_subscriber.py L624-641（xtdata get_trading_dates("SH") + weekday 回退）
- trading/reference_data_manager.py L193-324（SQLite calendar_days，calendar_name="SSE_A" 命名空间键，**注入形态最成熟**，可作未来日历持久化后端参考）

### E 类（已注入，装配对齐即可）
- data/auto_backfiller.py L122/L134（trading_days_provider；未注入回退=连续自然日）
- backtest/core/pit_manager.py / walk_forward.py；risk/core/drawdown_forced_rest.py L88-89；regime/regime_cycle_analyzer.py L214-245；position/core/calendar_position_constraint.py（holiday_dates 注入）

### F 类（无假设/有意设计，不动）
- data/sector_intraday_aggregator.py（数据代历 max(trade_date)）；data/manual_calendar_events.py；data/sector_report_builder.py（连板 trailing 日历=数据日期集，弱假设）；backtest 时间轴三件（见③）；backtest/services/scheduler.py；position/core/position_time_budget.py（明示自然日，职责上推）；plan_engine/sit_out_list.py（自然日事件窗）；intelligence/nightly_sentiment_window.py（18:00-08:00 窗+自然日-1，docstring 声明有意）；data/source_health_check.py / speed_tester.py（日历为探针对象）；data/reference_data_manager.py（无日历代码）

## 四、日历数据生产方（非消费点，不改）
- baostock_provider.py L262-279（c1_market.trade_calendar 表填充，is_open 口径）；tushare/akshare provider 同族；internal_compute_provider._fetch_hk_trade_calendar L739-770（XHKG 5年~+2年窗口填充）

## 五、Step 1.5 复用决策（四档结论）
| 候选等价物 | 结论 | 理由 |
|---|---|---|
| feedback_loop.collectors.market_calendar.MarketCalendar | 不复用 | holiday 集合 dataclass，无时段/范围/聚合语义，FLE 防误报专用；命名以包路径区分 |
| trading/reference_data_manager（SQLite calendar_days） | 不复用为接口，登记参考 | 注入形态成熟但语义=键值存储，无时段/聚合；可作未来持久化后端 |
| zephyr.data.trading_calendar（函数式真源） | **收编** | A股实现=ASHareCalendar 薄封装委托，真源本体零改动（零行为变化最稳路径） |
| 统一接口 | **新建**（决策档=无等价物新建） | 25+ 消费点各自直读，无策略对象抽象 |

## 六、改造范围裁定（克制版）
- **W0 改**：scheduler.py（①）、multi_timeframe_fusion.py（② 4h 键+calendar 便利参数）、pit_query.py（④ calendar 可选参数）；新增 src/zephyr/data/calendar/ 包（base/ashare/crypto）+ 单测
- **W0 声明不改**：回测时间轴（③ 数据驱动零改造点，装配层注入指引）；pit_manager/walk_forward 等 E 类（已合规）
- **后续波次**：A/B/C/D 类扩展消费点（§三全清单登记）；ex_core/pre_execution_checker 待 ex_core 战线空窗
- **避让区零触碰**：signal_ashare 全域（bj-daily）、ex_core/、risk/core/
