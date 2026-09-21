---
ttl: task_bound
title: 深度审查报告——TF09 daily_capital盘后资金族(35任务)
object: TF09 daily_capital 盘后资金任务族
target: "src/zephyr/data/config/tasks.yaml（schedule: daily_capital 实测 35 条，主锚 107/119/131/170/198/230/246/545/578/1079/1310/1376/1388/1508-1622/1649/1941/2030/2997-3031/3361-3464）；schedule.yaml:80-83"
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审；任务书"29任务"为旧版口径，18/19 夜班新增 rate_decision_calendar/macro_daily_gauge/ndrc_fuel_price/futures_warehouse_receipt/agri_wholesale 后=35）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF09 daily_capital盘后资金族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **35 任务**（disabled 6：hk_connect_flow×2 北向退役裁定#257、kline_us_daily_qmt、三个 qmt_placeholder 退役冻结）。18:00 default(8线程)，交易日守卫（schedule.yaml:80-83；trading_calendar.py:156）。构成：资金面经典 8（block_trade/dragon_tiger×2/money_flow(tushare主)/kline_futures(miniqmt+akshare fb)/kline_us_daily+us_index(tickflow)/share_unlock/restricted_shares/shareholder(东财 datacenter 9/18 切源)+美股、美股指数、EIA、qweather×2、hot_rank、JOB-077 postclose 四件、limit_up_pool(internal)、ipo_calendar、concept_board、block_trade_detail、share_change、st_stock_list、rate_decision_calendar、macro_daily_gauge、D4 油价链 3+agri。
- 深查代表：money_flow_incremental（tushare 升主源治东财反爬，tasks.yaml:170-183）+ shareholder_incremental（miniqmt 清退→东财 datacenter RPT_HOLDERNUM_DET，tasks.yaml:578-592）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| B | daily_valuation_full_refresh（weekend_calibration 但表同族语境）fallback 第二源 local_valuation **未注册**（create_provider 无此分支，scheduler.py:1234-1338）——fallback 链第 3 源必失败=死 fallback（akshare→miniqmt 两源有效，死源仅产噪音日志"未知数据源"） | tasks.yaml:1157-1161；scheduler.py:1333-1335 | P2 | 跑该任务观察第三源报错日志 |
| A | futures_position_incremental 挂**本族？否**——实际挂 intraday_realtime（tasks.yaml:218）归 TF01；本族 kline_futures_incremental 是它的依赖生产者（跨时段名义边已在 TF01 报）。本族内 DAG 边=0（全部 dependencies: []），35 任务并发 default 池 8 线程串行按源排队——tushare/akshare 单例互斥使实际并行度受 provider 锁约束（policy concurrency，registry DS-AKSHARE policy）——18:00 批次总时长可能挤压 19:00 daily_event 窗口（历史上 daily_event 即为错峰从 daily_capital 拆出，schedule.yaml:85 注释） | tasks.yaml:107-3464 该族全部；schedule.yaml:85 | P3 | 统计近一周 18:00 批次完成时刻 vs 19:00 |
| B | qweather×2/eia 需 API key（tasks.yaml:3007,3019,1089）——key 缺失=env_missing 静默跳过（系统发现 S2，无 notify）→weather_data/macro_data 的 EIA 子集停更仅 23:00 对账可见；eia_petroleum 有 start_days_back=30 回看窗可自愈 | tasks.yaml:1079-1092,2997-3020 | P2 | 清 key 复跑看 failures/ 零新增 |
| A | shareholder_incremental 9/18 切源质量：东财 datacenter 按公告日窗口（HOLD_NOTICE_DATE），date_col=announce_date 与窗口语义一致；fallback 显式置空理由（tushare 需 2000 分权限）成立——"任务存在≠管线活着"反例本体治本，切源留痕完备 | tasks.yaml:578-592 | 已查无 | 对比切源日前后 shareholder_count 表行数连续性 |
| C | money_flow tushare 主源 5540 行/日实证（tasks.yaml:172）；akshare 降 fallback 语义正确（反爬解除可恢复）——主备切换有实证背书 | tasks.yaml:170-183 | 已查无 | 对拍 tushare pro.moneyflow 与表行数 |
| E | **northbound_hold_snapshot 不在本族**（nightly_financial 侧）确认；hk_connect_flow 双任务北向停发退役（表止于 2024-08-16，CH 实证零行）——停发事件曾有"融合加零不报错"前科（checklist #6：bf7a8283cd），本次处置=显式 disabled+留痕而非静默加零，处置方向正确 | tasks.yaml:185-196,1336-1348 | 已查无 | 查表 2024-08-16 后零行 |
| D | share_unlock（daily_capital）与 share_unlock_forward_refresh（weekend_calibration）同表双窗口（历史 vs 前瞻 365d）——同表双任务在 backfill 发现"取第一个非 disabled"下只按历史任务口径检测，前瞻任务断供不触发表级哨兵；但 supply_sentinel.yaml:36 已含 c3_fundamental.share_unlock（事件日历口径）兜底 | tasks.yaml:545-576；backfill_checker.py 发现逻辑；data_supply_sentinel.yaml:36 | P3 | 停 forward 任务一周看哨兵 |
| F | 受阻（未检索）。 | — | 受阻 | — |

## 3 SOTA 对照
- 受阻。资金流/龙虎榜/大宗为 A 股特色数据，无国际对标；北向停发后以 hk_hold 季度快照替代（memo 19）口径留痕充分。

## 4 缺陷清单
1. P2 local_valuation 死 fallback：改 `fallback_sources` 删该条或注册 LocalValuationProvider——当前为噪音源+假韧性（checklist #9 邻接）。
2. P2 qweather/eia key 前置静默：同 TF05 FRED 修法（配置性跳过显式化）。
3. P3 18:00 批次时长监控：default 池饱和时 19:00 批次顺延风险（job 队列互不抢占但线程池独立——两池独立不互堵，仅需观察单池内 35 任务完成时刻）。

## 5 挂起疑问
- futures_warehouse_receipt_incremental 仅 CZCE 一所（tasks.yaml:3385 exchange: CZCE；SHFE 归档窗回填、DCE WAF rejected 留痕）——仓单表多所覆盖缺口已登记 known_data_gaps 与 disabled 回填任务，完整性符合"如实留痕"纪律，但消费端若假设全所覆盖会踩坑（挂起待消费端确认）。

## 6 完备性自评
六轴全查（F 受阻）。长尾：D4 油价链三件（ndrc/futures_warehouse/road_freight…road_freight 归 TF14）9/18 新落地，源探测证据（tasks.yaml:3354-3359）未复测；35 任务逐个 provider 深查未做（抽 money_flow/shareholder 两件）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
