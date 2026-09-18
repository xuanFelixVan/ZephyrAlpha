---
ttl: task_bound
doc_type: report
title: 深度审查报告——I14 完整性巡检（integrity_checker）
object: I14 完整性巡检
target: src/zephyr/data/integrity_checker.py:253（run_daily_check 主入口；任务级对账 L111-150）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；tasks.yaml 属他会话在途，按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I14 integrity_checker（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：L11 每日 23:00 巡检——表级行数达标（7 日均值×0.5 阈值，动态发现）、任务级对账（#ARCH-DATA-RECONCILE-001 治"37 任务漏跑零告警"）、tick 真重复 subprocess 正门接线。
- 测试：tests/zephyr/data/test_integrity_checker.py 存在。
- 变更热力：13 commits。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | **P2 任务级对账时序假阳性：23:00 检查 vs 23:00 后才跑的档期**——`_should_run_today` 把所有非周末/月初档任务都算"今日应跑"，而 daily_alt_fx 槽任务 alt_fx_ecb_daily_incremental（tasks.yaml:3341-3344）23:35 才跑、consensus_crosscheck 23:30——23:00 巡检时其当日 SUCCESS 必然缺席 → `missing` → integrity_check_task_reconcile ERROR 每交易日必响（告警疲劳=真缺口被淹没） | integrity_checker.py:73-85,138-150 + tasks.yaml L3341-3344 + schedule.yaml（23:00/23:35 两槽） | P2 | 查 data/failures/ 是否每日出现 integrity_check_task_reconcile；对时间线 |
| A | 同源假阳性：integrity_check 自身与 catchup_guard/backfill 等**特殊时段任务不经 run_task、无 task_runs 记录**——若 tasks.yaml 中存在挂这些 schedule 的任务即永 missing（当前工作区 grep 未见表附该类 schedule，风险=未来挂载即踩） | integrity_checker.py:70-85 + progress_store（特殊时段走 _save_summary 手写记录） | P3 | 给任务挂 schedule=integrity_check 跑一轮看 missing |
| B | UTC 窗口换算硬编码 -8h（"本地 today 00:00 = UTC today-1 16:00"）——机器 TZ≠UTC+8 即全窗漂移 | integrity_checker.py:88-97 | P3 | 拨 TZ 单测 |
| E | CH 故障时 `_check_table_today` 查询返空→count=0→全表 unhealthy→ERROR 告警风暴（CH 挂=满屏假火警，真火警通道被噪声淹没）；与 ch_reader count 语义合并问题联动（I09） | integrity_checker.py:181-192 | P3 | 断 CH 跑巡检看告警量 |
| A | tick 真重复检查经 subprocess 正门（RULE-DATA-OPS 单一口径真源，不在 src 复刻 14 字段口径）——架构正确；退出码 0/1/2 三态分类完备，degraded 不阻断 | integrity_checker.py:204-250 | 已查无 | 本地跑脚本对三码 |
| A | 元数据表 skipped 显式上报（Phase 3-B 治"静默跳过"）正确 | integrity_checker.py:168-179 | 已查无 | 读码 |
| C | 巡检结果落 progress_store（task_id=integrity_check_daily）供 CLI/看板消费；PARTIAL 语义=unhealthy 或 task_gaps 任一即非 SUCCESS——保守正确 | integrity_checker.py:330-341 | 已查无 | 读码 |
| D | 阈值口径与 backfill_checker _infer_threshold 同源（复用发现函数）——无双真源 | integrity_checker.py:41-44,269 | 已查无 | 对读 rpt_i11 |

## 3 SOTA 对照
- "声明 vs 实际"任务级对账+表级行数双层巡检与 SLO reconciliation 惯例对等（治漏跑盲区的设计动机充分）；时序对齐（检查点 vs 档期完成点）是同类系统常见坑，本对象正踩（P2-1）。**对等已有（含已知坑）**。来源：SRE 数据新鲜度巡检通识（未单独检索 URL=受阻如实记，检索预算已用于 I01/I08）。

## 4 缺陷清单
1. P2 对账时序假阳性：修法=_should_run_today 排除"scheduled 完成时刻晚于巡检时刻"的档期（读 schedule.yaml cron 解析比对），或把巡检挪至全部档期后（如 00:30）。
2. P3 组：-8h 硬编码、CH 故障告警风暴（建议查询失败显式 degraded 态而非 count=0）、特殊时段任务无 task_runs 的结构性盲区。

## 5 挂起疑问
- tasks.yaml 在途改动可能新增/调整 schedule 挂载——P2-1 影响面（除 alt_fx 外是否还有晚于 23:00 的任务）请收口方以定格后的 tasks.yaml 复核。

## 6 完备性自评
六轴全查。长尾：check_tick_duplication.py 脚本本体未审（P1-1 接线只审了调用面）；test_integrity_checker.py 断言强度未逐条。
