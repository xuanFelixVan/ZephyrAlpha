---
ttl: task_bound
title: I 段·运行时调度常驻链挖矿档（W3-3）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# I 段·运行时调度常驻链（F76-F85+F132，11 环节）

> 方法：以代码为准，00_skeleton.md §1/§2 I 段为线索；每环节 ≥1 个 grep/读码级证据锚。
> 运行态证据源：docs/_working/fullflow_chief_20261001/automation_panorama.md（10-01 13:07-13:16 快照）。
> 本轮要点：**F82 order_daemon 已翻绿**（09-30 st-circ-a7 接线，骨架仍标断链 P0）；**F81 健康监控运行载体未证（新降级）**。

## 六向台账

| 环节id | 名称 | 上游 | 下游 | 生产者路径:行 | 消费者 | 自动化态 | 运行态 | 三态复核(骨架→本轮) |
|--------|------|------|------|--------------|--------|----------|--------|--------------------|
| I-01(F76) | Windows 计划任务群 | — | 全链 | scripts/register_*.ps1（32 件，ls 实测）；config/resource_profile_registry.yaml:13-15（total_entities: 101，generated 2026-09-30） | Task Scheduler 52 任务（全景 §1.1：Ready38/Running8/Disabled6） | 定时（Logon+Time 混合） | 在跑（V1 任务 MetaqAuditReconcile 在册，见 F 档交叉） | 挖干→挖干（实体数 96→101 漂移，机生四源再生） |
| I-02(F77) | 数据调度常驻 | F76 | F01/F20/F82 唤醒链 | src/zephyr/data/scheduler.py:2748(main)、:1006/:1093/:1152/:1284(while self._started 常驻环)、:543-545(lane_g_intake_sweep 慢路径+总闸)、:816-821(wire_data_scheduler) | F01 采集槽、pipeline_events.py:1348 订阅链 | 常驻 | PID 21944 Running（全景 §1.2） | 挖干→挖干 |
| I-03(F78) | belt daemon | F76 | 提交链 | src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py:855(main)、:8(ReadDirectoryChangesW 事件驱动)、:18(M10 豁免注记) | commit_queue drain/k=4 池化 | 常驻+watchdog 事件 | 任务 BeltDaemon 每 1min spawn-if-absent，PID 11620（全景 §1.1/§1.2） | 挖干→挖干 |
| I-04(F79) | reaper 与水位监控 | F76 | 全链安全 | src/zephyr/trading/process_reaper.py:169(keep 文件路径)、:259(_load_keep_patterns) | 全链进程安全；keep 册=data/runtime/process_reaper_keep.txt（218 有效条目，全景 §4） | 定时（10min） | Ready，上轮 13:07:27 killed=1/reported=13/breaches=1（全景 §1.1） | 挖干→挖干 |
| I-05(F80) | 资源画像与排班 | F76 | 全链排班 | scripts/governance/generators/generate_resource_profile_registry.py（+morning_report/week_view 同目录）；src/zephyr/infrastructure/system_telemetry/resource_sampler.py | registry groups 7 互斥组（config/resource_profile_registry.yaml:17-24） | 定时（SamplerScan 10min/Writeback/ViewPublish/MorningReport/RegenCheck 1h，全景 §1.1） | 任务族 5 件全 Ready | 挖干→挖干 |
| I-06(F81) | 监控告警 | 全链 | 值守 | src/zephyr/trading/health_monitor.py:8/:40/:48（THD-HEALTH-001~004 fail-closed 加载）；REG-ATH-001=docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml | 值守/告警分发 | 骨架称"常驻+定时" | **未证**：scripts/*.ps1 全族 grep health_monitor=0 命中；全景 §1.1/§1.2 进程表无 health_monitor（ch_health_probe 属 A 段 CH 探针非本件） | 挖干→**存疑（运行载体缺失，新降级）** |
| I-07(F82) | 订单与结算常驻 | F57 | F63/ai_work_order | src/zephyr/ai_layer/scheduling/order_daemon.py（20KB，build_task_order:167）；**接线链：scheduler.py:816-821→pipeline_events.py:1348(subscribe task_completed)→:1121/:1202(maybe_drain_order_daemon)**；post_settlement_pipeline.py:96、night_shift_queue.py:58 | PG ai_work_order（scripts/ai_layer/apply_ai_layer_scheduling_ddl.py:87） | 事件（task_completed 唤醒，journal 非空才 spawn） | 接线在码；守护流量未实测 | 挖干 ｜ 存疑(P0 断链)→**挖干(接线，翻绿候选)**——详见 F82.md |
| I-08(F83) | 自动化班底 | F76 | 全链 | docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md:4(双引擎两班制)、:33(夜班 9 席)；docs/_working/cmd_ledger/automation_master_plan.md | 夜班任务卡执行 | 定时（双引擎两班制） | ZCode 定时自动化 10 条（全景 §5） | 挖干→挖干 |
| I-09(F84) | 反馈循环 FBL | F81 | 治理/演进 | src/zephyr/feedback_loop/（40+ 件：evolution_engine.py:40-113 五类型、scheduler_collect_detect.py:51 CollectDetectHandler、error_budget.py:27/:36） | 外部消费 4 处实测：ai_layer/perceive/translator.py、autonomy_core/skill_postmortem.py、compliance/regulatory_change_tracker.py、data/calendar/base.py | 事件（骨架口径） | 未见独立任务/常驻进程挂 FBL 调度族（全景两表零命中） | 存疑(M5 补挖)→存疑（件全、自动触发链未证）——详见 F84.md |
| I-10(F85) | 环境与启动链 | F76 | 全链 | src/zephyr/trading/windows_service.py:49(install_service)/:59/:66；scripts/register_desktop_shell_startup.ps1:1-8（Electron 壳 logon 自启，ensureApi/ensureDocs） | 全链开机 | 定时（冷启动三步） | 全景进程表无 windows_service/Electron 壳实例 | 存疑(M5 补挖)→存疑——详见 F85.md |
| I-11(F132) | infra_ops 运维工程域 | I 段 | 运维面 | src/zephyr/infra_ops/（6 py：config_effect_checker/loki_log_pipeline/runtime_topology_visualizer/storage_cost_calculator/wal_checkpoint_monitor） | config_effect_checker→任务 ZephyrAlpha_ConfigCheck Daily 08:05（全景 §1.1） | 域内 1/5 实件已挂任务 | ConfigCheck Ready 在册 | 盲区(未挖)→盲区收窄（P1；1 件已接线在跑）——详见 F132.md |

## 段内小结

- 环节 11：挖干 6（F76/F77/F78/F79/F80/F83）+ 翻绿候选 1（F82）+ 存疑 3（F81 新降级/F84/F85）+ 盲区收窄 1（F132）。
- **三态变迁 3 笔**：F82 断链→接线；F81 挖干→存疑（降级）；F132 盲区→收窄。单列见 ../W3-3_transitions.md。
- F125（data_governance）为 A/K 交界，归 A 段挖矿档，本段不重挖。
- V 红线交叉：本段 I-01 持 V1 任务的注册载体（scripts/register_metaq_audit_reconcile_task.ps1），交叉详记 K 段档 §V。
