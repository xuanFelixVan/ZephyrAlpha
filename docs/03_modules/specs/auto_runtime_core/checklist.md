---
module_id: MOD-SPEC-001
title: "AutoRuntime Core — 验收清单"
doc_type: service_spec
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# AutoRuntime Core — 验收清单

> **蓝图**: ARC-0001 / spec.md
> **版本**: v5.0.0-complete
> **总验收项**: 10 大类 / 90+ 条目

---

## A. 架构一致性

### A.1 责任唯一性
- [ ] A.1.1 `AutoRuntimeCore` 为唯一"系统大脑"
- [ ] A.1.2 `PipelineOrchestrator` 只管线内部
- [ ] A.1.3 `WorkOrchestrator` 只管工作编排（不管理任务状态机）
- [ ] A.1.4 `TaskRepository` 只管任务状态机（不决定跑哪层）

### A.2 三层模型对齐
- [ ] A.2.1 人在 → TRAE
- [ ] A.2.2 嵌入/搜索/重排 → LOCAL
- [ ] A.2.3 规则内黑白判定 → API
- [ ] A.2.4 不确定/创造性 → API + ambiguity_log
- [ ] A.2.5 L2 24/7 常驻
- [ ] A.2.6 L3 夜班

### A.3 业界对标
- [ ] A.3.1 CapabilityCard 对标 A2A AgentCard
- [ ] A.3.2 WorkOrchestrator DAG 对标 Airflow DAG
- [ ] A.3.3 Stop Gate 对标 Claude Code 实验被动闸门
- [ ] A.3.4 Dream Cycle 对标 Claude Code 情节→语义记忆
- [ ] A.3.5 HealthMonitor.reconcile() 对标 K8s Level-Triggered
- [ ] A.3.6 Finalizer 对标 K8s Finalizer

### A.4 全系统清单覆盖
- [ ] A.4.1 spec.md §2 包含全部 26 个包
- [ ] A.4.2 spec.md §2 包含全部 31 个蓝图 YAML
- [ ] A.4.3 spec.md §3 三层分类覆盖所有包

### A.5 终极目标
- [ ] A.5.1 AGENTS.md 包含终极目标（全域接入，0% 孤儿率）
- [ ] A.5.2 RuntimeConfig.ultimate_goal 字段存在
- [ ] A.5.3 reconcile() 每次调和检查孤儿率

---

## B. 功能验收

### B.1 一键启动
- [ ] B.1.1 `python -m zephyr.runtime` 正常启动
- [ ] B.1.2 20 步 Boot Sequence 依次执行
- [ ] B.1.3 启动失败时清晰错误提示
- [ ] B.1.4 `--once` / `--no-demo` / `--no-dream` 参数正常

### B.2 AGENTS.md
- [ ] B.2.1 项目根目录存在 AGENTS.md
- [ ] B.2.2 内容完整：项目概述、核心系统、能力发现、关键路径、规范、禁止事项

### B.3 AI 审计日志
- [ ] B.3.1 6 类日志全部可写
- [ ] B.3.2 JSONL 追加式写入
- [ ] B.3.3 `has_pending_flush()` / `flush()` 正确

### B.4 能力注册中心
- [ ] B.4.1 register/unregister/discover/list_all/find_by_tags/dump_snapshot 全部正常
- [ ] B.4.2 注册时校验 schema
- [ ] B.4.3 持久化到 capability_cards/{id}.yaml

### B.5 夜班登记表
- [ ] B.5.1 append/pending/resolve/has_unresolved/flush_all 全部正常
- [ ] B.5.2 PipelineOrchestrator 同时写入 NightShiftQueue + AiAuditLogger

### B.6 Stop Gate
- [ ] B.6.1 check() 返回 (can_stop, reasons)
- [ ] B.6.2 无新日志/未解决登记/未归档 → can_stop=False
- [ ] B.6.3 acknowledge_shutdown() 正确

### B.7 Dream Cycle
- [ ] B.7.1 trigger_archival() 正确执行归档→提取→遗忘→索引→commit
- [ ] B.7.2 情节/语义记忆归档到正确路径
- [ ] B.7.3 forgotten.log 存在
- [ ] B.7.4 needs_archival() 正确

### B.8 Feedback Loop
- [ ] B.8.1 generate_proposals() 生成 EvolutionProposal
- [ ] B.8.2 apply_proposal() 写入 feedback_proposals/

### B.9 Health Monitor
- [ ] B.9.1 probe/probe_all/reconcile/auto_restart 全部正常
- [ ] B.9.2 资源 > 80% → pressure_response() 关 L3 保 L2
- [ ] B.9.3 dump_last_snapshot() 正确

### B.10 Integration Registry
- [ ] B.10.1 validate_all() 验证 26 包集成点
- [ ] B.10.2 status_all() 返回各集成点状态

### B.11 Circadian Scheduler
- [ ] B.11.1 14 个定时任务按时间表触发
- [ ] B.11.2 5 个事件触发任务正确响应
- [ ] B.11.3 定时触发 → WorkOrchestrator.submit_dag() 衔接

### B.12 工作编排子系统（新增）
- [ ] B.12.1 WorkOrchestrator 加载 10 个预定义 DAG
- [ ] B.12.2 submit() → TaskRepository.create() 衔接
- [ ] B.12.3 submit_dag() 展开为多个 WorkItem + 依赖关系
- [ ] B.12.4 DAG 依赖解析：上游完成→下游自动 READY
- [ ] B.12.5 resolve_layer() 正确决定任务跑在哪一层
- [ ] B.12.6 resolve_priority() 正确返回 P0/P1/P2
- [ ] B.12.7 acquire_slot()/release_slot() 并行控制正确
- [ ] B.12.8 L2 同时跑 3 个嵌入任务
- [ ] B.12.9 P0 任务抢占 P2 槽位
- [ ] B.12.10 schedule_next() 返回可执行任务列表
- [ ] B.12.11 完成回调 → TaskRepository.update() + 依赖解析

### B.13 自动接入子系统（新增）
- [ ] B.13.1 ModuleOnboardingScanner.scan_filesystem() 扫描 src/zephyr/ 下所有 .py
- [ ] B.13.2 ModuleOnboardingScanner.scan_blueprints() 扫描 architecture_model/ 下所有 .yaml
- [ ] B.13.3 ModuleOnboardingScanner.diff_registered() 正确对比 CapabilityRegistry
- [ ] B.13.4 AutoIntegrator.analyze_module() 临时启动 L3 API 分析
- [ ] B.13.5 confidence >= 0.8 → 自动注册到 CapabilityRegistry
- [ ] B.13.6 confidence < 0.8 → 写入 NightShiftQueue
- [ ] B.13.7 AutoIntegrator.generate_card() 生成 CapabilityCard 草稿
- [ ] B.13.8 OrphanDetector.compute_orphan_rate() 返回 0.0-1.0
- [ ] B.13.9 OrphanDetector.find_orphans() 正确找出未接入模块
- [ ] B.13.10 OrphanDetector.prioritize_orphans() 按 P0/P1/P2 排序
- [ ] B.13.11 OrphanDetector.is_goal_met() 当孤儿率=0.0 时返回 True
- [ ] B.13.12 文件系统 watcher 检测新文件 → 触发扫描
- [ ] B.13.13 成本控制：每天 L3 临时激活次数 <= max_daily_l3_activations

### B.14 任务分派
- [ ] B.14.1 DEMO 7 任务全部自动完成
- [ ] B.14.2 tasks/ JSON 投递 → 自动发现
- [ ] B.14.3 6 类推理任务全部正常
- [ ] B.14.4 嵌入返回正确维度

### B.15 状态面板
- [ ] B.15.1 TUI 面板显示三层状态 + 组件 + 节律 + 工作编排 + 孤儿率
- [ ] B.15.2 面板包含 DAG 列表、槽位占用、排队数、孤儿率
- [ ] B.15.3 status_json() 返回合法 JSON

### B.16 Finalizer
- [ ] B.16.1 run() 按序执行所有清理函数
- [ ] B.16.2 任一清理失败不阻断后续

### B.17 优雅关闭
- [ ] B.17.1 Ctrl+C → StopGate.check → Finalizer.run → 关闭
- [ ] B.17.2 ShutdownReport 输出汇总

---

## C. 集成验收

- [ ] C.1 AutoRuntimeCore 正确委托 DaemonRegistry
- [ ] C.2 AutoRuntimeCore 正确委托 LocalModelScheduler
- [ ] C.3 dispatch_task() 正确调用 _resolve_execution_mode()
- [ ] C.4 PipelineOrchestrator night_shift_log 与 NightShiftQueue + AiAuditLogger 一致
- [ ] C.5 local_layer_daemon.py 向后兼容
- [ ] C.6 AGENTS.md → CapabilityRegistry 桥接
- [ ] C.7 Windows Service 注册成功
- [ ] C.8 b_execution_model.yaml 包含 ARC-0001 引用
- [ ] C.9 WorkOrchestrator → TaskRepository 衔接正确
- [ ] C.10 WorkOrchestrator → TaskQueue 衔接正确
- [ ] C.11 CircadianScheduler → WorkOrchestrator.submit_dag() 衔接正确

---

## D. 防孤儿验收

- [ ] D.1 所有已实现组件注册 CapabilityCard
- [ ] D.2 新 AI → AGENTS.md → CapabilityRegistry.list_all() → 发现服务
- [ ] D.3 CapabilityCard 校验拒绝错误注册
- [ ] D.4 组件挂了 → HealthMonitor DEGRADED → auto_restart
- [ ] D.5 data/capability_cards/ 有 7+ 个 YAML
- [ ] D.6 data/work_dags/ 有 10 个 DAG YAML
- [ ] D.7 不编排=不执行（WorkOrchestrator 只执行注册过的 DAG）

---

## E. 全自动验收（一阶~八阶）

| 阶 | 验收项 | 判定 |
|----|--------|------|
| 一阶 | 开机自启 | [ ] |
| 一阶 | 自调度 | [ ] |
| 一阶 | 自发现 | [ ] |
| 一阶 | 自注册 | [ ] |
| 一阶 | 自监控 | [ ] |
| 一阶 | 自记录 | [ ] |
| 一阶 | **工作编排** | [ ] |
| 一阶 | **DAG 依赖管理** | [ ] |
| 一阶 | **并行控制** | [ ] |
| 一阶 | **自动扫描** | [ ] |
| 二阶 | Stop Gate | [ ] |
| 二阶 | 自裁决 + 留不确定 | [ ] |
| 二阶 | **优先级抢占** | [ ] |
| 二阶 | **智能接入** | [ ] |
| 二阶 | **孤儿检测** | [ ] |
| 三阶 | Dream Cycle | [ ] |
| 三阶 | Feedback Loop | [ ] |
| 三阶 | Filesystem as Memory | [ ] |
| 三阶 | **层间工作窃取** | [ ] |
| 三阶 | **终极目标驱动** | [ ] |
| 四阶 | 自愈 | [ ] |
| 四阶 | 自降级 | [ ] |
| 五阶 | 水平触发调和 | [ ] |
| 五阶 | Idempotent Reconciler | [ ] |
| 六阶 | Finalizer | [ ] |
| 六阶 | AGENTS.md | [ ] |
| 七阶 | A2A 兼容预留 | [ ] |
| 七阶 | MCP 兼容预留 | [ ] |
| 八阶 | 自动 Git 提交 | [ ] |
| 八阶 | 自动依赖检查 | [ ] |

---

## F. 质量验收

- [ ] F.1 `ruff check --select F` 零新增
- [ ] F.2 所有新文件有 docstring
- [ ] F.3 `python -m zephyr.runtime --help` 输出合法
- [ ] F.4 线程安全：WorkOrchestrator, NightShiftQueue, HealthMonitor 无竞态
- [ ] F.5 异常情况有日志，不崩溃

---

## G. 文档验收

- [ ] G.1 b_execution_model.yaml 包含 ARC-0001 引用
- [ ] G.2 spec.md 组件清单与实际代码一致
- [ ] G.3 tasks.md 依赖关系图与实施顺序一致
- [ ] G.4 checklist.md 全部验收项有判定标准
- [ ] G.5 AGENTS.md 内容完整

---

## H. 高阶验收

- [ ] H.1 Dream Cycle forgotten.log 内容合理
- [ ] H.2 Feedback Loop 进化提案 confidence >= 0.5
- [ ] H.3 Stop Gate 连续 3 次阻止退出触发告警
- [ ] H.4 Finalizer 清理步骤可配、可跳过
- [ ] H.5 CapabilityCard examples 至少一个有效示例
- [ ] H.6 24 小时运行后 audit_logs/ 至少一天日志
- [ ] H.7 WorkDAG 循环依赖检测
- [ ] H.8 WorkOrchestrator 崩溃恢复：重启后从 TaskRepository 恢复状态
- [ ] H.9 AutoIntegrator 分析结果与人工判断一致性 >= 80%
- [ ] H.10 孤儿率在系统运行 7 天后 < 20%
- [ ] H.11 新模块创建后 5 分钟内被 ModuleOnboardingScanner 发现

---

> **判定**: 所有 A~H 项全部打勾 → ARC-0001 v5.0.0 通过验收
