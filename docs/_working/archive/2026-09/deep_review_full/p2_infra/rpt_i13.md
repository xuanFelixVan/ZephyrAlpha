---
ttl: task_bound
title: 深度审查报告——I13 补跑守卫（catchup_guard）
object: I13 补跑守卫
target: src/zephyr/data/catchup_guard.py:168（run_catchup_guard 主入口；分桶常量 L43-68）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I13 catchup_guard（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：调度对账补跑层（档期 vs 打卡）——分桶 overdue 判定、空表兜底、≤15 补跑上限、单实例锁。05:30 每日 cron（schedule.yaml L10.7）。
- checklist #2 前科核实：测试日期漂移史案（623e32b9c5，真实日期漂出 10 天窗口致 3 失败）对象即本文件 `window_start = today - 10 days`（L195）。现有 tests/zephyr/data/test_catchup_guard.py 存在；本审查未逐断言验证"是否已全部注入日期"（长尾），但生产代码 today 全部参数化为入口 today 变量（L194 单点），注入缝存在。
- 变更热力：2 commits（稳定）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| D | **P2 对账分桶配置漂移：新时段未入桶也不在豁免清单**——daily_crypto(08:41)/nightly_sentiment(08:20)/consensus_crosscheck(23:30)/daily_alt_fx(23:35)/data_supply_sentinel(06:50) 等 2026-09 后新增时段既不在 _MONTHLY/_WEEKLY/_DAILY/_INTRADAY/_ALWAYS_ON 五桶，也不在 _SKIP_SCHEDULES——`_cadence_of` 返 None 静默跳出对账：这些档期错过（调度器宕机/9-01 型事故）永不补跑不告警，catchup_guard 治本承诺对半仓时段不成立 | catchup_guard.py:43-52,206-213 vs schedule.yaml 17 槽 | P2 | 新增 slot 后跑对账看 overdue 恒空；对照 catchup_guard.py:211 debug 分支 |
| A | monthly 桶月初双跑：catchup 05:30 判上月成功→overdue→补跑；monthly_static 09:16 正点再跑——同日两跑（幂等可兜，静态表 DELETE+重建语义未核实） | catchup_guard.py:155-156 + schedule.yaml monthly_static | P3 | 月初跑一轮看两次执行记录 |
| E | 单实例锁 check-then-act 非原子（读 PID→判断→写文件三步无互斥），05:30 单 cron 触发下窗口小；psutil 活性检测+30min 陈锁强破已到位 | catchup_guard.py:91-114 | P3 | 并发起两进程竞态窗口复现 |
| A | RUNNING 跳过依赖 last_status——reap_stale_runs 6h 后转 STALE，catchup 次日即可补跑：闭环正确 | catchup_guard.py:217-219 + progress_store.py:306-369 | 已查无 | 对读 |
| B | 空表兜底只覆盖 monthly_static/weekend_calibration 两桶；daily 桶"打卡成功但数据被清"形态由 L11/integrity_check 行数检测兜——分层清晰 | catchup_guard.py:64,227-231 | 已查无 | 对读 rpt_i14 |
| C | 补跑经 scheduler.run_task 幂等（Replacing/先删后写）——承接 I01 的删写非原子缺陷面，本层不放大 | catchup_guard.py:238-243 | 已查无 | 联动 rpt_i01 |
| A | MAX_RERUN_PER_RUN=15 截断顺延收敛设计正确；持续失败任务每日重试+每日 ERROR 告警=可见不静默 | catchup_guard.py:66,238-247 | 已查无 | 读码 |

## 3 SOTA 对照
- "调度对账（档期 vs 打卡）+ 上限截断 + 错峰独立时段"与 Airflow dataset/sensor 或 cron-reconciler 模式同构：**对等已有**。来源：工作流对账工程通识（未单独检索 URL=受阻如实记，检索预算已用于 I01/I08）。

## 4 缺陷清单
1. P2 分桶漂移（新时段漏对账）：修法=分桶常量改为 schedule.yaml 派生（cron 频率→桶映射生成器），或至少给"不在任何桶"的 schedule 加 WARN 显式留痕（当前 debug 级=无人看见）。这是 checklist #14（重构丢路由）的配置版。
2. P3：月初双跑、锁竞态窗口。

## 5 挂起疑问
- 桶名单是否刻意"新时段暂缓对账"——无注释证据，按漂移处理；若 Owner 裁定豁免，建议改入 _SKIP_SCHEDULES 显式化。

## 6 完备性自评
六轴全查。长尾：test_catchup_guard.py 是否已对 #2 前科全量拨钟回归未逐断言核（建议 metamorphic 拨钟用例——与 deep_review_policy §8 变形测试立卡项衔接）。
