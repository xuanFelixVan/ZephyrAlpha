---
ttl: task_bound
title: 深度审查报告——TF14 weekend_calibration周末校准族(42任务)
object: TF14 weekend_calibration 周末校准任务族
target: "src/zephyr/data/config/tasks.yaml（schedule: weekend_calibration 实测 42 条，主锚 564/835/1050-1161/1578-1604/2168-2181/2377-2495/2512-2617/2714-2938/2947-2992/3065-3078/3253-3263/3306-3338/3423-3435）；schedule.yaml:114-119"
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF14 weekend_calibration周末校准族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **42 任务**（disabled 1：factor_decay_monitor_weekly，由 trading_lifecycle_weekly 替代职能，tasks.yaml:3043/3263 自述）。cron `00 3 * * 0` =**周一 03:00**（APScheduler 0=周一；schedule.yaml:114-119 自述"原周六02:00已废弃：QMT 服务器周末连不上 error 10061"），heavy(2线程)；**不在**交易日守卫集（周一凌晨=工作日但盘前，守卫集无它——trading_calendar.py:151-163）。
- 构成：全量刷新类 20（日K/可转债/期权/港股K/分析师/指标/涨跌停/净值/回购/质押/生猪/航运/台风×3/宏观 worldbank/fred/eia/估值回填/商品×2/资金流/估值/停牌推导/解禁前瞻）、internal 3（daban_board_event_derive/technical_indicator_full/trading_lifecycle）、ROAD 运价爬虫 1。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| D | **注释与实际执行日漂移**：tasks.yaml:2374-2376 注释"每周六运行，下载完整历史数据"——实际周一 03:00（schedule.yaml:114-117 已废弃周六档）。尾追病式注释漂移（checklist #10 邻接），误导运维在周六等日志 | tasks.yaml:2374-2376 vs schedule.yaml:114-119 | P3 | 两处文本对照 |
| B | hk_kline_full_refresh（miniqmt，5 年回补）**无 fallback**（tasks.yaml:2405-2414 注释自述"移除假fallback akshare/hk_kline"）——9/18 后全量校准通道同步死亡（hk_kline_incremental 亦然，TF01 已报）——港股 K 线表将无任何供给路径，台账 §2.3 待裁定 | tasks.yaml:2405-2414；migration-ledger §2.3 | P1 | 9/19 后跑该任务必失败 |
| B | daily_valuation_full_refresh 三源链 akshare→miniqmt→**local_valuation（未注册死源）**——同 TF09 发现，第三源必报"未知数据源" | tasks.yaml:1157-1161；scheduler.py:1333-1335 | P2 | 跑任务看第三源报错 |
| A | kline_sector_incremental 的错峰依赖治理（09-15 追加 serial 依赖防 tqcenter SDK 单例竞争，tasks.yaml:877）属本族 industry_class_refresh 侧影响面——同时段内部依赖 industry_class→kline_sector 顺序由 daily_kline 槽位跨时段承接（名义边），实际错峰靠时段差（周一03:00 vs 16:30）天然满足——设计成立 | tasks.yaml:835-844,871-883 | 已查无 | 周一跑完查 kline_sector 板块数 |
| E | **周一凌晨 heavy 池排队**：L10 weekend_backfill 02:00 + L8 本族 03:00 同 heavy(2线程)——本族 40+ 全量任务与 tick 补下载串行抢占 2 线程，最坏排队至盘中前（QMT 类任务 trading_day_only 在非交易日跳过、但周一是交易日会跑）——05:30 catchup 的"03:30 落 L8 窗口内"注释自证拥挤（schedule.yaml:155-156）| schedule.yaml:150-156；scheduler.py:2197 | P2 | 统计近四周周一 heavy 池完成时刻 |
| B | macro_fred_full_refresh/macro_worldbank_full_refresh/eia_full_refresh：key+VPN 双前置（tasks.yaml:2946-2992,1077-1105）——周末 VPN 断=全量回补静默 missing（S2 健康跳过无 notify）；三表在 integrity 对账"应跑"内（weekend_calibration 在 _NON_DAILY 排除集——**周一 03:00 跑的它们不被当日 23:00 对账要求**（对账排除了 weekend_calibration 任务）→错过周只能靠下周一次重试或 catchup weekly 桶（05:30 月/周对账含 weekend_calibration）——兜底延迟 1 天 | integrity_checker.py:61-67；catchup_guard.py:44 | P3 | 周一停任务看周二 05:30 catchup 补跑 |
| A | technical_indicator_full_refresh 9 周期遍历（1min~monthly，120min 由 60min 两根聚合，tasks.yaml:2179）——依赖分钟K输入；TF02 断供后周末全量重算的分钟周期段将永远缺新段（传导性登记，与 TF02 P1 联动） | tasks.yaml:2168-2181 | P2 | TF2 断供周查 technical_indicator 分钟周期 max(trade_date) |
| C | trading_lifecycle_weekly 无落表（回写 registry/JSON 台账，tasks.yaml:3254-3263）——integrity 表级哨兵对"无表任务"只能靠任务级对账（weekend_calibration 被对账排除）——**该任务失败告警仅 task 级 ERROR 文件**，无第二道 | tasks.yaml:3253-3263；integrity_checker.py:61-67 | P3 | 注入失败看兜底层次 |

## 3 SOTA 对照
- 受阻（未检索）。全量校准与增量互补的双层下载为成熟范式（训练记忆）。

## 4 缺陷清单
1. P1 hk_kline_full_refresh/incremental 断供（合并 TF01 项）：港股 K 线双任务均 miniqmt 独源——9/17 窗口切源裁定待落地（台账 §2.3）。
2. P2 周一 heavy 拥堵：本族与 L10 错峰至 02:30/04:00 或拆池→验证法=完成时刻分布统计。
3. P3 周六注释修正；local_valuation 死源清理；trading_lifecycle_weekly 建议加轻量落表/心跳供对账。

## 5 挂起疑问
- share_unlock_forward_refresh（前瞻 365 天窗）在本族周一 03:00 跑——与 daily_capital 18:00 的历史窗口任务的写入时序交错对 ReplacingMergeTree 幂等无影响（键同），但"当日 18:00 历史+次日 03:00 前瞻"的合并可见性时差未验证。

## 6 完备性自评
六轴全查（F 受阻）。长尾：40 全量任务的 5 年回补时长画像缺（heavy 池单批可行性，commodity_spot_price_full_refresh 自述 5 年窗为单批可行口径 tasks.yaml:3338）；road_freight 爬虫礼貌 1.2s/请求的 134 页枚举实测未做。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
