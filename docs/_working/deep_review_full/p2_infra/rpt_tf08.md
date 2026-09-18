---
ttl: task_bound
doc_type: report
title: 深度审查报告——TF08 pre_market盘前族(8任务)
object: TF08 pre_market 盘前任务族
target: src/zephyr/data/config/tasks.yaml:1403-1506(premarket×5)、3109-3152(a50/wti/gold)；schedule.yaml:24-31
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF08 pre_market盘前族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **8 任务**：盘前元数据 5（stock_basic/st_status/suspend_status/index_member/stk_limit_premarket，全 akshare，trading_day_only: true）+ 夜盘衍生 3（a50_futures/global_wti/global_gold，akshare futures_foreign_hist 新浪源，单次全量本地窗口过滤）。cron `34 8 * * 0-4`（schedule.yaml:28-31，注释写 08:30 属措辞漂移），executor=default；时段**不在**交易日守卫集（trading_calendar.py:151-163 无 pre_market），靠逐任务 trading_day_only 实现节假日跳过（_filter_schedule_tasks，scheduler.py:358-360）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | stk_limit_premarket 的 dependencies=["st_status_premarket"] 是**同时段强约束**（有效）；注释自证"ST标记快照前提；昨收=kline_daily 昨日盘后已落库，均非本调度组任务"——跨时段前提（昨日 kline_daily）用文字而非依赖边表达，属正确取舍（昨日盘后必然已跑），但若前日 daily_kline 整批失败，今日 stk_limit 规则法用陈旧昨收**无检查**（涨跌停价=撮合约束前提，错价→回测撮合失真） | tasks.yaml:1494-1506；task_queue.py:150-164 | P2 | 人为删昨日 kline_daily 当日行，跑 stk_limit_premarket 看是否告警 |
| B | 全 akshare 单源族 + fallback_sources 显式置空（JOB-077"天然无副源"裁定，tasks.yaml:1399-1402）——东财/中证官网反爬时整族停，且 08:34 时点 akshare 限流余量受 event_driven */3 与 nightly_sentiment 08:20 邻近批次竞争 | tasks.yaml:1399-1402 | P3 | 08:34 前后 akshare 调用频率实测 |
| B | a50/wti/gold 三件 capability 复用 a50_futures_daily（payload.symbols 覆盖品种，tasks.yaml:3135 注释"机制复用"）——三任务同 capability 同 provider 路由，启动契约校验无法区分品种集；symbols 显式列 CL/GC 无缺——配置合法但属"一 capability 多任务"模式，与 TF03 同型 | tasks.yaml:3109-3152 | P3 | 读 akshare meta a50_futures_daily 契约 |
| E | **时段错过无兜底（系统发现 S7）**：pre_market 不在 catchup_guard 任何桶（catchup_guard.py:43-47 只有 monthly/weekly/daily_kline/capital/event/nightly_financial/daily_backfill），misfire_grace_time=3600 只覆盖调度器宕机 1 小时内——08:34 批次错过→当日停牌/ST/涨跌停约束数据缺位，盘中撮合约束与 universe 过滤带旧数据跑一天，唯一自愈=18:00 postclose 双调度点重算（stk_limit/suspend/index_member 有 postclose 副本，stock_basic_postclose 也在 daily_capital）——JOB-077 双调度点设计实际兜住了大部分（tasks.yaml:24-27 注释） | catchup_guard.py:43-47；tasks.yaml:1508-1562 | P3 | 停调度器跨 08:34-09:34 验证无补跑 |
| C | 消费端=universe 构造+回测撮合约束（打板/做T 撮合用 stk_limit）——错值传播属 P1 决策链爆炸半径，本族只报数据面：stk_limit 规则法三级解析链有 88445 样本验证背书（tasks.yaml:1589，daban 侧引用同链） | tasks.yaml:1505,1589 | P3 | 抽样核对 stk_limit 表 vs 交易所当日涨跌停价 |
| D | suspend_status_derive_weekend（weekend_calibration 侧）以 K 线缺口推导停牌作为本族自愈旁系——链路闭环设计完备 | tasks.yaml:1591-1604 | 已查无 | — |
| F | 受阻（未检索）。盘前元数据快照+盘后双调度点设计与业内 pre-market checklist 惯例对等（训练记忆） | — | 受阻 | — |

## 3 SOTA 对照
- 受阻。

## 4 缺陷清单
1. P2 昨收前提无断言：stk_limit_premarket 建议加"昨日 kline_daily 当日 000300/样本行数>0"前置断言（或挂 dependencies 无法表达的轻量自查），防带旧昨收算价→验证法=构造昨收缺失场景看行为。
2. P3 pre_market 纳入 catchup_guard 当日对账口径（当前 23:00 integrity 对账把 pre_market 任务当"应跑"（_NON_DAILY 不含它）——错过日实际**会**进 missing 告警，兜底其实存在；本条降级为"补跑缺失"而非"告警缺失"，与 TF13 daily_crypto 同修）。
3. P3 注释 08:30 vs cron 08:34 措辞统一。

## 5 挂起疑问
- a50 夜盘收盘时间（北京 05:15）与 08:34 拉取间隔内源站数据延迟性未实测——盘前 gap_adj w3 通道校准（tasks.yaml:3112）依赖该时效。

## 6 完备性自评
六轴全查（F 受阻）。长尾：DS-081~085 五接口逐字段 PIT 核未做（属数据质量班次）；40 城市 qweather（TF09 侧）与本族无交集确认。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
