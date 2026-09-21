---
ttl: task_bound
title: 深度审查报告——TF11 research_nightly研报族(2任务)
object: TF11 research_nightly 研报任务族
target: src/zephyr/data/config/tasks.yaml:606-630（research_report_detail_incremental、consensus_daily_build）；schedule.yaml:91-96
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF11 research_nightly研报族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **2 任务**：research_report_detail_incremental（akshare 东财研报中心全字段，历史已回补 14.7 万行）→consensus_daily_build（internal，读 research_report 窗口聚合每股每日×日历年矩阵）。20:30 default 池 + max_instances: 1（schedule.yaml:91-96），交易日**不守卫**（research_nightly 不在 TRADING_DAY_GUARDED_SCHEDULES——akshare 源节假日跑无害）。
- 前科语境：2026-09-14 研报快照冒充历史（research_report 快照 PIT 污染）事件的治本配套即本族（consensus_crosscheck 23:30 双向验证，独立班次 I15 已审）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | DAG 同时段强约束：consensus_daily_build dependencies=["research_report_detail_incremental"]——研报明细落库后才重建矩阵（task_queue READY 判定），链路有效；"增量起点按表内实况推断-重叠窗吸收迟到研报"（tasks.yaml:630）——迟到研报经重叠窗自愈，ReplacingMergeTree 幂等 | tasks.yaml:619-630 | 已查无 | 人为迟到一行看次日重建吸收 |
| B | research_report_detail fallback 显式置空（"券商研报明细仅东财研报中心免费可得"，tasks.yaml:615）——单源认定诚实；东财反爬前科在案（money_flow 同族接口），断供时 task 级 ERROR 告警+23:00 对账兜底，无跨源自愈（如实留痕达标） | tasks.yaml:615 | P3 | 停接口看告警链 |
| E | **20:30 批次错过无补跑（系统发现 S7）**：research_nightly 不在 catchup_guard 三桶（catchup_guard.py:43-47），misfire 1 小时兜底——错过日=研报明细缺当日窗口，次日增量窗是否回补取决于 provider 窗口参数（"日度仅补增量窗口"），若窗口=T-1 起则自愈，否则永久缺一日——窗口语义未见配置留痕 | catchup_guard.py:43-47；tasks.yaml:617 | P2 | 读 provider 增量窗参数；或人为停跑一日观察次日是否回补 |
| C | 消费端：EXP 因子族标准输入（tasks.yaml:630）+consensus_crosscheck 23:30 互查——本族断供会被 23:30 交叉验证的新鲜度检查捕获（I15 报告 §2 已审其阈值）——双保险闭环 | schedule.yaml:98-106 | 已查无 | 停本族看 23:30 交叉验证告警 |
| D | 与 news_slow 的 research_report_incremental（个股研报简版写 news_data）为旁系——两路研报的字段/表分离清晰（detail→c3_fundamental.research_report vs 简版→news_data），无双承载漂移 | tasks.yaml:606-617 vs 1323-1334 | 已查无 | — |
| A | consensus_daily_build 的 PIT=只认 publish_date（tasks.yaml:630）——对 9/14 源污染事件的口径正面回答；日期列 trade_date 在 internal 计算侧语义=快照日 | tasks.yaml:630 | 已查无 | 抽样核对 publish_date≤trade_date |
| F | 受阻（未检索）。分析师一致预期聚合（事件流→日历年矩阵）与卖方金工惯例对等（训练记忆；中文研报语境不算盲区——deep_review_policy §3.F.2） | — | 受阻 | — |

## 3 SOTA 对照
- 受阻。I15 报告（同日班次）已对交叉验证方法面给立卡结论，本族不重复。

## 4 缺陷清单
1. P2 增量窗口语义留痕：research_report_detail 的增量回看窗参数显式写入 tasks.yaml extra（如 lookback_days），否则"断供一日是否自愈"不可机查→验证法=读 provider fetch 窗口逻辑回填文档。

## 5 挂起疑问
- 20:30 与 19:00 daily_event 池同 default(8线程)——research_report_detail 全市场逐股约 2h（schedule.yaml:91 注释），20:30-22:30 窗口与 22:00 nightly_financial(heavy 独立池) 不冲突，但与 event_driven */3 持续共享 akshare 单例限流——研报明细 2h 期间快新闻被限流降速的量化影响未画像。

## 6 完备性自评
六轴全查（F 受阻）。长尾：14.7 万行历史回补的重复率/PIT 抽检未做（属数据质量班次）；consensus_daily 矩阵数学（EXP 因子口径）属 p1 决策链范围。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
