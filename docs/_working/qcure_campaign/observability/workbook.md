---
ttl: task_bound
title: QCure作业簿·observability
session: st-qcure-20260925
---
# observability 作业簿

## 1 环节定义与边界
观测与运维 = 提交链（enqueue→landing→gate）的记账、活性、告警与值守自动化：四本账（bottleneck_ledger/landing_phase_stats/gate_execution_stats/preflight_events）+ 心跳/纪元 + 计划任务/daemon 在岗。边界：不含死信生命周期处置（deadletter 簿）、不含告警阈值的业务语义修订。

## 2 六向台账
### ①上游输入
- bottleneck_ledger.jsonl 三写者混写：daemon（kind=dead_letter/registry_drift/landing_staleness/phantom_staging/alert，commit_belt_daemon.py:120-259）、CQ slow_item（scripts/commit_queue.py:1595-1612，**ts=epoch float**）、env_abort CRITICAL（daemon:598-625，**ts=ISO**）——同文件双时间格式。
- preflight_events.jsonl：commit_preflight.py:397-408 写入，字段 ts/session/event(blocked|passed)/path/gates_failed/degraded/files_count/ms（:76 自述）；无处方字段。
- gate_execution_stats.jsonl：commit_gate_registry.py:77,114 每链 flush（n_specs/failed[]/reused{}/ms/total_ms）；随 serializer worktree 分账。
- landing_phase_stats.jsonl：landing.py:832-862 一行一单件（phases 分段+residual_ms），落各工 worktree（worktrees/w0-w3）。
- 心跳 belt_daemon.heartbeat：独立线程 30s 续写（daemon:261-279，st-k4-20260923 治长 drain 假死）。
### ②下游消费
- gate_execution_stats：usage_stats.py:93,131 + standard_checkup.py:9,31,69（30 天窗运营，2026-09-15 起积累、当前人工点火）。
- bottleneck_ledger：仅 daemon 自查积压 `_check_ledger_backlog`（:480-553，W5 只数 kind=dead_letter；R-06 冷却状态机 :515-551）。
- queue_health（CQ:1807-1862）→ 积压/爆发告警（CQ:1865/2081）。
- **landing_phase_stats 零消费方**（全仓 grep 仅写者）；preflight_events/commit_block_events 无报表消费方。
### ③机制现状（+业界参照）
- 纪元换血：daemon 每轮 drain 后自检三子树（gov_enforcement|scripts/governance|scripts/commit_queue.py）HEAD tree sha，变更即安全点 re-exec（daemon:628-765；裁定#281+#ARCH-323+st-commitchain R4 三次扩圈）——盘上热修对常驻 daemon 无效是已知约束（QCure 方案 §1.3-6）。
- 业界参照：DLQ 深度/重试计数类指标聚合+阈值告警（https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues）；失败元数据结构化随消息留痕（https://www.redpanda.com）；有界重试+退避的运维观测（https://oneuptime.com；https://www.glukhov.org）。
- 本仓对标缺口：账本分散四处+worktree 三处，无统一视图/无周报机械；"观测死亡"事故（belt daemon 09-18 起死 4 天无人发现，alert_threshold_registry.yaml v1.5.0 注）已有 THD-ALERT-007 补课但见⑤盲区。
### ④代码面（实现/测试/调用方）
- daemon：活性/离线缺口/积压/爆发/纪元全在 commit_belt_daemon.py（:261-279 心跳、:298+ 离线缺口、:433-477 陈旧 pending 扫描、:480+ 积压自检、:628-765 纪元）；启动即全量补账（:781-789）。
- 测试：tests/governance/rule_bridge/test_commit_belt_daemon.py、test_commit_preflight.py；CQ 侧 tests/governance/test_commit_queue*.py。
- 已知缺陷史：心跳失写"7 例模式"文档面查无（docs/_working 与政策目录 grep 心跳失写零命中，归因：或仅存于夜班临时记录/.runtime/tmp）；仓内最近证据=daemon:274-279（夜班四轮实证"长 drain 期间心跳写入器沉默"，已线程化治本）+ 心跳写失败本身 fail-open 仅 log 无账（:270-271）——写失败不可观测，与"观测死亡"同族残余。
### ⑤运维/呈现面
- 计划任务在岗清单：ZephyrAlpha_BeltDaemon（Running）、ProcessReaper（Running）、DataScheduler/DeadmanSwitch/CHHealthProbe/IOCheck-Monthly 等 37 项；**无"每 30 分 commit_queue 巡检"型 cron**——daemon 事件驱动即全部。
- 离线告警盲区：`_check_daemon_offline_gap` 只在**下一次启动**时跑（daemon:298-303 自认"守护自己死后无人记账，唯一记账人=下一次启动"）——daemon 死且无人拉起=无告警机（与 09-18 四天事故同构残余）；DeadmanSwitch 计划任务在岗但不读心跳。
- 呈现：health CLI + task_board 标签，前端零接线。
### ⑥失败态与数据面（2026-09-25 实测）
- 行数级：bottleneck_ledger 17494 行/8.6MB（ts 双格式混写）；preflight_events 4476 行（path 分布 direct 1871/enqueue 2475/redblue 111/**probe+debug 测试垃圾 23 行直写生产账**；blocked 1681/passed 2798）；gate_execution_stats 1804；commit_block_events 2032；landing_phase_stats w0-w3 各 17-24 行（k=4 池上线后才有）。
- 活性：heartbeat 存活（pid 23356）；health_alert_state 显示 09-24 双告警已鸣（daily_burst+session_chain，dead_total=378）——告警链实证通。
- phase 账样本：total_ms=101984 vs accounted 2563 → **residual 97.5%**（gate 链段未纳入 _timed_phase，单项耗时大头不可归因）。
- 审计膨胀无轮转：write_audit 37MB×4 轮、feature_flags 1.5GB；bottleneck_ledger 尚无轮转机制。

## 3 缺陷与矿脉清单
1.【新矿脉·QCure 验收直需】"死信率下降"对消仪表缺口：方案 §4-2 要求"周窗 preflight 拒收 vs dead/ 新增按死因族对消"，现无任何机械可出此数。挂点建议：preflight_events（gates_failed[]）×dead/（dead_reason）按族 join——族判据复用三分类表+族抽取；落地形态=health 扩展字段或独立 commit_queue_report.py 生成器（红线 §9-5 禁手工清单），周窗口径进验收。
2.【新矿脉】daemon 离线探测外置：DeadmanSwitch/IOCheck 既有计划任务加一步读 belt_daemon.heartbeat 年龄超阈即留痕——零新常驻进程补掉"死后无人记账"盲区（THD-ALERT-007 的执行者从"下次启动"外扩）。
3.【新矿脉】landing_phase_stats 零消费+residual 97.5%：把 gateway/commit 段纳入 _timed_phase（LAND:815-829 装饰器挂点现成），并给该账配消费方（ QCure §1.3-10 成本口径的实证面）。
4.【新矿脉】账本卫生：bottleneck_ledger ts 双格式统一；preflight_events 的 probe/debug 测试路径隔离（红线 §9-6 违例在案 23 行）；瓶颈账轮转策略并入 M5.4。
5.【已知→方案】preflight 事件无处方字段=M3.3 审计侧挂点（PF:397-408 加一键即成）；create_guard `registry_data` 注入点（方案 §1.3-3）是同源化观测的判据基准修正位。

## 4 自审闸三态裁定
**施工**——矿脉 1（对消报表）是验收 §4-2 的直接承重件且全只读零风险；矿脉 2-4 为小件可随批或挂期排。

## 5 长尾清单
- 四本账+worktree 分账的汇总视图缺失：每工 gate_execution_stats/phase_stats 散在 worktrees/w*/.runtime/audit，聚合需遍历（报表生成器应统一锚定）。
- commit_block_events 与 preflight blocked 口径相近但双账（gate 链内 vs 锁外预检），对消时需去重规则。
- health_alert_state.json 与 bottleneck_backlog_alert_state.json 两套冷却状态文件分居两目录，语义重叠。
- THD-ALERT-005/006/007 阈值自 09-22/09-23 上线未经复发校准（0924 单日 285 死已触发，数值合理性待一季回看）。
- standard_checkup 30 天窗"人工点火"未自动化——观测闭环的最后一公里。
