---
module_id: MOD-FEEDBACK_LOOP
submodule_path: src/zephyr/trading/feedback_loop
title: "Feedback Loop Engine 蓝图 — 氛围编程原生元自知全维自防御AIOps核心"
doc_type: blueprint
template_for: blueprint
status: Draft
version: "0.35.1"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-06"
ttl: permanent
construction_progress: design_only
actual_disk_path: "src/zephyr/trading/feedback_loop/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: "自我改进闭环引擎：regime→detect→diagnose→inversion-verify→act→verify→self-heal，67+ Detector多模态检测"

tags: ["feedback_loop", "fle", "self-improvement", "anomaly-detection", "auto-evolution", "infrastructure", "regime", "self-heal", "govern", "ensemble-detection", "aiops", "vibe-coding-native", "capacity-upgrade", "deterministic-guardrail", "causal-inference", "autonomous-operations"]
priority: P0
runtime_plane: hot
generation: 1
functional_domain: operations
last_verified: "2026-05-13"
depends_on:
  - {target: "MOD-MASTER_BLUEPRINT", at: "all", why: "FLE→Orc异常调度+联邦协调+自治边界"}
  - {target: "MOD-TASK_SYSTEM", at: "all", why: "任务系统→检测输入"}
  - {target: "MOD-GATE_ENGINE", at: "all", why: "门禁引擎→ADJUST_GATE"}
  - {target: "MOD-INF-009", at: "all", why: "管线→动态路由反馈"}
  - {target: "MOD-INF-021", at: "all", why: "回滚→VERIFY+配置回滚联动"}
  - {target: "MOD-INF-023", at: "all", why: "漂移检测→HyperNetwork自适应联动"}
  - {target: "MOD-INF-024", at: "all", why: "预算强制→per-model扣费+自反思成本"}
  - {target: "MOD-INF-018", at: "all", why: "agent-rbac→PermissionGuard+联邦策略+自治阶梯"}
  - {target: "MOD-INF-005", at: "all", why: "ScriptSystem→扫描触发契约(Protocol A/B/C)"}
  - {target: "MOD-INF-035", at: "all", why: "AutoRuntime→异常调度+联邦协调"}
  - {target: "MOD-INF-020", at: "all", why: "Audit Trail→运行期审计日志写入"}
references:
  - {id: "MOD-INF-020", at: "all", why: "Audit Trail——运行期写入；DAG 上不保留 depends_on"}
last_updated: "2026-05-19"
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Feedback Loop Engine 蓝图 — 氛围编程原生元自知全维自防御AIOps核心

## 概述

本蓝图描述 Feedback Loop Engine——ZephyrAlpha 的自我改进闭环引擎。它解决了系统运行时异常检测、根因诊断、自动修复和自我进化的问题。核心职责包括：regime→predict→detect→diagnose→act→verify→self-heal→govern 全链路自治、67+ Detector 多模态检测、三级检测池并行化、32 代进化×429 盲点覆盖。当前规模单线程 30s 轮询，目标容量 100 AI Session 并发/500 findings/cycle/240 events/s。上游依赖 ScriptSystem(MOD-INF-005)提供扫描结果，下游被 AutoRuntime(MOD-INF-035)消费异常调度。

> module_id: MOD-FEEDBACK_LOOP | version: 0.35.1 | status: Draft | layer: cross_layer
> actual_disk_path: src/zephyr/trading/feedback_loop/ | generation: 1 | construction_progress: completed
>
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图模板 v3.5：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> ⚠️ 防止 construction_progress 与实际代码不符。
> 每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§14）。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-FEEDBACK_LOOP`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|:-----:|-------------------|
| 1 | `__init__.py` | §3 | 模块身份——MODULE_ID=MOD-FEEDBACK_LOOP | 已实现 | — |
| 2 | `config.py` | §4 | FLEConfig——7项配置 | 已实现 | — |
| 3 | `protocols.py` | §4 | FeedbackProtocolAdapter——fire-and-forget防循环依赖 | 已实现 | — |
| 4 | `exceptions.py` | §6 | FLEBaseException+ForensicContext——4种子类 | 已实现 | — |
| 5 | `auto_evolution.py` | §3 | 自我进化引擎 | 已实现 | — |
| 6 | `eval_harness.py` | §9 | 评估工具 | 已实现 | — |
| 7 | `evolution_engine.py` | §3 | 进化引擎 | 已实现 | — |
| 8 | `feedback_collector.py` | §3 | 反馈收集器 | 已实现 | — |
| 9 | `fitness_functions.py` | §3 | 适应度函数 | 已实现 | — |
| 10 | `metrics_collector.py` | §4 | 指标收集器 | 已实现 | — |
| 11 | `_gen_inherited.py` | §3.1 |  gen inherited | 已实现 | — |
| 12 | `alert_dispatcher.py` | §3.1 | alert dispatcher | 已实现 | — |
| 13 | `backpressure_bridge.py` | §3.1 | backpressure bridge | 已实现 | — |
| 14 | `db_bridge.py` | §3.1 | db bridge | 已实现 | — |
| 15 | `decision_engine.py` | §3.1 | decision engine | 已实现 | — |
| 16 | `error_budget.py` | §3.1 | error budget | 已实现 | — |
| 17 | `generator.py` | §3.1 | generator | 已实现 | — |
| 18 | `scheduler.py` | §3.1 | scheduler | 已实现 | — |
| 19 | `scheduler_act.py` | §3.1 | scheduler act | 已实现 | — |
| 20 | `scheduler_collect_detect.py` | §3.1 | scheduler collect detect | 已实现 | — |
| 21 | `scheduler_health.py` | §3.1 | scheduler health | 已实现 | — |
| 22 | `scheduler_safety.py` | §3.1 | scheduler safety | 已实现 | — |
| 23 | `slo_manager.py` | §3.1 | slo manager | 已实现 | — |
| 24 | `template.py` | §3.1 | template | 已实现 | — |
| 25 | `validator.py` | §3.1 | validator | 已实现 | — |
| 26 | `db_writer.py` | §3.1 | db writer | 已实现 | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/trading/feedback_loop/` 逐文件核对 | ☐ |
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| construction_progress = scaffold → __init__.py 存在且非空 | `cat __init__.py` | ☐ |
| construction_progress = design_only → 代码目录不存在或为空 | `ls src/zephyr/trading/feedback_loop/` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (基线) | 6文件骨架+metrics_collector+fitness_functions | — | — |
| v0.34.0-draft (容量升级) | §1A-§1N设计规格 | DetectorPool/EventDispatcher/CPUScheduler等L级组件 | 待施工 |

---

## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha 扩容至 100 AI 并发 Session → FLE 当前单线程 30s 轮询、67+ Detector 串行执行 → 无法满足 L 级容量需求。需将 FLE 自身检测-诊断-修复流水线并行化。

### §1.2 目标

| # | 目标 | 衡量 |
|---|------|------|
| 1 | 全链路自治闭环 | regime→predict→detect→diagnose→act→verify→self-heal→govern |
| 2 | 100 AI Session 并发支撑 | 500 findings/cycle, 240 events/s peak |
| 3 | MTTD < 5min, MTTR < 15min | §17 E2E SLA 分解 |
| 4 | L 级容量 (10K 脚本 / 1.5K 模块) | §17 升级矩阵 |

### §1.3 不包含的目标

| # | 内容 | 原因 |
|---|------|------|
| 1 | AI Session 运行时内同步检查 | 阻断 AI 交互流 → 违反氛围编程非侵入原则 |
| 2 | 多实例分布式 FLE | 本地 Windows 部署 → 单实例架构 |
| 3 | GPU 实时推理 | v0.34.0 无 GPU 依赖；GP1 预留预算 |

### §1.4 运行场景约束

| 约束 | 值 |
|------|-----|
| max_workers | 8 (ThreadPoolExecutor) |
| CPU | i7-12700KF 20线程 |
| 部署模式 | 本地 Windows 单实例 |
| LLM 提供方 | OpenAI/DeepSeek/Claude 三级降级 |

---

## §2 模块边界

### §2.1 职责范围

| # | 职责 |
|---|------|
| 1 | 异常检测：67+ Detector 多模态检测（EMA/统计/LLM/因果推理/多假设跟踪） |
| 2 | 根因诊断：DiagnoserPool 并行诊断 → FindingAggregator 去重关联排序 |
| 3 | 修复验证：安全门 L0-L67 串行检查 → ActorPool 执行 → Verify 验证 |
| 4 | 自我进化：Skill/Detector/KB 在线增量添加，32 代进化 × 429 盲点覆盖 |
| 5 | 容量自适应：QuickPool(6)/DeepPool(4)/BatchPool(2) 三级检测池 + 双 RingBuffer |
| 6 | AI Session 感知：SessionLifecycle 事件 → 自动调整检测节奏 |
| 7 | 自身可观测：3 层可观测 Telemetry + Self-Health Dashboard |

### §2.2 不包含的职责

| # | 内容 | 归属 |
|---|------|------|
| 1 | 管线编排 | MOD-INF-009 Pipeline Orchestrator |
| 2 | 任务状态机 | MOD-TASK_SYSTEM TaskRepository |
| 3 | 门禁规则定义 | MOD-GATE_ENGINE Gate Engine |
| 4 | 回滚执行 | MOD-INF-021 Rollback System |
| 5 | 审计日志持久化 | MOD-INF-020 Audit Trail |

---

## §3 架构设计

### §3.1 组件架构

| 组件 | Worker数 | 配置键 | 延迟 | 职责 |
|------|:---:|------|------|------|
| RingBuffer-A | — | `fle.event.ringbuf_a` | — | CodeChange + SessionLifecycle (cap 4096) |
| RingBuffer-B | — | `fle.event.ringbuf_b` | — | ScanResult + Anomaly + ActionCompleted (cap 4096) |
| EventDispatcher | 1 | — | — | 单线程无锁事件分发到 DetectorRouter |
| DetectorRouter | — | — | — | 按 detector estimated_latency_ms 路由到 Quick/Deep/Batch pool |
| QuickPool | **6** | `fle.detector.quick_workers` | <100ms | EMA/统计/阈值 detector |
| DeepPool | **4** | `fle.detector.deep_workers` | 1~5s | LLM/因果推理/反事实 detector |
| BatchPool | **2** | `fle.detector.batch_workers` | >1min | 日/周批处理 detector |
| FindingAggregator | — | — | — | 去重 (TTL 60s) + 关联 + 优先级排序 |
| DiagnoserPool | **6** | `fle.diagnoser.workers` | — | 并行诊断, 互不干扰 |
| GateQueue | 1(串行) | — | — | L0→L67 安全门有序串联检查 |
| ActorPool | **4** | `fle.actor.workers` | — | DryRunSandbox + 修复动作执行 |

### §3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | AI Session×100 | 事件写入 | RingBuffer(Dual 4096) | Event dict |
| 2 | RingBuffer | 单线程无锁分发 | EventDispatcher | Event dict |
| 3 | EventDispatcher | 按 latency 分类路由 | DetectorRouter | Event dict |
| 4 | DetectorRouter | 分类到检测池 | QuickPool/DeepPool/BatchPool | Event + state_snapshot |
| 5 | 检测池 | 多模态检测 | FindingAggregator | list[Finding] |
| 6 | FindingAggregator | 去重(TTL 60s)+排序 | DiagnoserPool | AggregatedFinding |
| 7 | DiagnoserPool | 并行诊断×6 | GateQueue | DiagnosisResult |
| 8 | GateQueue | 串行L0→L67安全门 | ActorPool | ApprovedAction |
| 9 | ActorPool | DryRun+执行×4 | Verify | ActionResult |
| 10 | Verify | 验证修复结果 | KB Write | VerifiedResult |

### §3.3 状态生命周期

| 阶段 | 触发 | FLE 行为 |
|------|------|---------|
| Session Start | AI Session 启动 | FLE 初始化 SessionContext + 增量扫描注册 |
| Active | 正常操作 | 5s 轮询检测 + 事件处理 |
| Teardown | AI Session 关闭 | Cleanup hooks + SessionKnowledge 归档 |
| Cold Start / Crash | 异常终止 | Checkpoint Rewind + 不丢失 scan delta |

---

## §4 接口契约

### §4.1 FLE ↔ ScriptSystem (Protocol A/B/C)

| Protocol | 方向 | 触发条件 | Payload |
|---------|------|---------|---------|
| TriggerIncrementalScan | FLE → ScriptSystem | AI push 代码后 | `{module_path, session_id, change_type}` |
| ScanResultDelivery | ScriptSystem → FLE | 增量扫描完成 | `{findings[], module_path, scan_duration_ms}` |
| TriggerFullScan | FLE → ScriptSystem | 周检窗口 (Sunday 02:00) | `{scan_type: "full", module_filter: "*"}` |

### §4.2 FeedbackProtocolAdapter

fire-and-forget 防循环依赖：FLE → Pipeline/Orchestrator/AuditTrail 单向上报，不等待回调。

### §4.3 配置契约

| 配置键 | 默认值 | 说明 |
|--------|-------|------|
| `fle.scheduler.poll_interval_ms` | 5000 | 轮询间隔 |
| `fle.scheduler.max_findings_per_cycle` | 500 | 单周期上限 |
| `fle.event.ringbuf_a_cap` | 4096 | RingBuf A capacity |
| `fle.event.ringbuf_b_cap` | 4096 | RingBuf B capacity |
| `fle.findings.dedup_ttl_s` | 60 | 去重 TTL |

### §4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| TriggerIncrementalScan | `{scan_id: str}` | `SCAN_REJECTED` / `MODULE_NOT_FOUND` |
| ScanResultDelivery | `{findings_processed: int}` | `PARSE_ERROR` / `TIMEOUT` |
| FeedbackProtocolAdapter.fire() | `{event_id: str}` | `RATE_LIMITED` / `CIRCUIT_OPEN` |

### §4.5 MCP 接口

本模块不暴露 MCP 接口。FLE 通过内部事件总线消费/产出，不对外提供 Tool。

### §4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 Detector/安全层 | ✅ 向后兼容 | 不影响已有消费者 |
| Protocol A/B/C Payload 变更 | ❌ 破坏性 | 需 Owner 审批 + ScriptSystem 同步 |
| 配置键新增 | ✅ 向后兼容 | 默认值保证旧行为 |
| RingBuffer 容量变更 | ⚠️ 需通知 | 影响内存预算 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | CPU 线程预算 | Quick(6)+Deep(4)+Batch(2)+Diagnoser(6)+Actor(4)+Dispatcher(1)=**23** |
| 2 | RingBuffer 总容量 | **8192** (A 4K + B 4K) |
| 3 | 事件峰值速率 | **240 events/s** |
| 4 | Detector 纯函数化 | `(event, state_snapshot) → list[Finding]`，无副作用 |
| 5 | GateQueue 全局串行 | L0→L67 有序串联 (后门依赖前门结果)，不可并行 |
| 6 | 蓝图 YAML SSoT 双向对齐 | 修改蓝图 ⇔ 同步 `architecture_model/layers/b_feedback_loop.yaml` |
| 7 | Python 3.12+, Pydantic V2, Ruff lint | 与项目标准一致 |

### §5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 并发 AI Session | 1~5 | 100 | ThreadPoolExecutor 23 workers | ❌ | §17 三级检测池并行化 |
| ScriptSystem 脚本数 | 388 | 10,000 | RingBuffer 8192 events | ❌ | §17 D7 存储分片 |
| 模块数 | 1,623 | 1,500+ | Detector 67+ | ✅ | §17 D8 KG 扩展 |
| Detector 数量 | 67+ | 100~120 | Quick(6)+Deep(4)+Batch(2) | ❌ | §17 D1 检测池扩容 |
| 每周期 findings | 100 | 500 | FindingAggregator 去重 TTL 60s | ❌ | §17 D11 批处理聚合 |
| 事件峰值 | ~5/s | 240/s | RingBuffer Dual 4096 | ❌ | §17 D2 事件总线吞吐 |

### §5.3 迁移/废弃方案

> ⚠️ 临时时态：迁移方案执行完毕后从蓝图删除。

> ⚠️ **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| — | 无 | — | — | 本蓝图不涉及文件废弃或迁移，容量升级为增量式 | — |

旧 `run_all.py ThreadPoolExecutor(8)` 仅管脚本执行并发 → **不变**。新 Scheduler v2 是 FLE **分析并发**层——两者不同层，并存不冲突。

---

## §6 错误处理

| # | 错误场景 | 检测 | 响应 |
|---|---------|------|------|
| 1 | RingBuffer 溢出 | `backpressure_alert_counter` | DROP lowest_priority + log_warning |
| 2 | Detector OOM | `memory_monitor` | 减少 batch_size + GC + alert |
| 3 | LLM API 限流 | 429 检测 | DetectorRouter → DeepPool→BatchPool 自动降级 |
| 4 | GateQueue 阻塞 | `gate_process_timeout` (60s) | 跳过当前 finding + 触发 Owner 旁路 |
| 5 | Diagnoser 死循环 | `diagnoser_timeout_ms` | process pool terminate + restart |
| 6 | DryRun Sandbox 泄漏 | `sandbox_timeout_ms` | kill sandbox process |
| 7 | KB 写入失败 | WAL replay | WAL mode atomic write + replay |

---

## §8 安全考量

| # | 威胁 | 缓解 |
|---|------|------|
| 1 | FLE 自我篡改 (关闭保护) | Immutable Core Guard: `[AI_AUTONOMY] immutable_core` |
| 2 | LLM Prompt 注入 → 危险修复 | Safety Gate L0-L67 串联检查 + DryRun Sandbox |
| 3 | FLE 幻觉修复 | Self-Hallucination Auditor (Detector 333) |
| 4 | FLE 运维人格漂移 | Personality Stability Monitor (Detector 335) |
| 5 | Detector 集体盲区 | Adversarial Self-Test Engine (Detector 296) |

---

## §9 测试策略

| 层级 | 测试类型 | 覆盖 |
|------|---------|------|
| L0 | Detector 单元测试 | 每个 detector `__init__.py` + pure function test |
| L1 | Diagnoser 集成测试 | 并行诊断 → 一致性验证 |
| L2 | GateQueue 链式测试 | L0→L67 有序 + 中断/旁路路径 |
| L3 | DryRun Sandbox | 高风险修复预飞 → 副作用沙箱 |
| L4 | E2E 回归 | 已修复 bug → 回归不复发 |
| L5 | Adversarial Self-Test | FLE 攻击自己 → 防御有效性 |

---

## §10 依赖关系

### §10.1 依赖声明

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-035 AutoRuntime Core | 必须 | 异常调度+联邦协调+自治边界 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |
| MOD-TASK_SYSTEM Task System | 必须 | 任务状态→检测输入 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\task_system\blueprint.md` |
| MOD-GATE_ENGINE Gate Engine | 必须 | ADJUST_GATE | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-INF-009 Pipeline | 必须 | 动态路由反馈 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\pipeline\blueprint.md` |
| MOD-INF-021 Rollback | 必须 | VERIFY+配置回滚联动 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\rollback\blueprint.md` |
| MOD-INF-023 Drift Detector | 必须 | HyperNetwork 自适应联动 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\drift-detector\blueprint.md` |
| MOD-INF-024 Budget Enforcer | 必须 | per-model 扣费+自反思成本 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\budget-enforcer\blueprint.md` |
| MOD-INF-018 Agent RBAC | 必须 | PermissionGuard+联邦策略+自治阶梯 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\agent-rbac\blueprint.md` |
| MOD-INF-005 Script System | 必须 | 扫描触发契约 (Protocol A/B/C) | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\script-system\blueprint.md` |
| MOD-INF-020 Audit Trail | 可选 | 运行期审计日志写入 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-trail\blueprint.md` |

### §10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-FEEDBACK_LOOP` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### §10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| `config.py` | `protocols.py` | FLEConfig 实例化参数 | 检查 config 导入 |
| `exceptions.py` | `auto_evolution.py` | FLEBaseException 基类 | 检查 exceptions 导入 |
| `feedback_collector.py` | `evolution_engine.py` | 反馈数据输入 | 检查 collector 产出物 |
| `evolution_engine.py` | `auto_evolution.py` | 进化策略执行 | 检查 engine 产出物 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| `feedback_collector.py` | `evolution_engine.py` | 反馈事件 | 函数调用 |
| `metrics_collector.py` | `eval_harness.py` | 指标数据 | 函数调用 |
| `fitness_functions.py` | `auto_evolution.py` | 适应度评分 | 函数调用 |
| `config.py` | 全部模块 | 配置参数 | 模块导入 |

### §10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 10个外部依赖+4个内部依赖，手动维护易漂移 |
| 2 | 依赖对齐自动验证 | 是 | 有10个外部依赖需对齐 |
| 3 | 临时时态内容自动清理 | 否 | 当前无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | L级容量升级待施工 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | `asset_inventory/dependency.py` | 不覆盖scripts/目录 |
| 2 | 依赖对齐自动验证 | CI门禁 | `validate_path_alignment.py` | 无 |
| 3 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback_loop\blueprint.md` | 本文件（含设计和施工指引） |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\feedback_loop\` | FLE 源码（10 文件） |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\` | FLE 测试用例 |
| YAML SSoT | `D:\ZephyrAlpha\architecture_model\layers\b_feedback_loop.yaml` | 结构真源 |
| FLE安全门禁代码 | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\` | 43个FLE门禁实现（FLE-ACTION-REVERSIBILITY ~ FLE-SCOPE-CREEP-MONITOR + FLE-SAFETY-GATE-L1~L67），gate_id在_registry.yaml中注册，实现归属本蓝图 |

---

## §12 集成目标

### §12.1 域契约锚点

| 域 | 锚点 | 集成方式 |
|---|------|---------|
| Operations | AutoRuntime Core | FLE→Orc 异常调度 (runtime event bus) |
| Governance | Gate Engine | FLE→Gate ADJUST_GATE (gate API) |
| Intelligence | Context Engine | FLE diagnostics → CE context injection |
| Infrastructure | ScriptSystem | FLE↔Script 扫描触发契约 (Protocol A/B/C) |

---

## §13 需要更新

| 变更 | 需同步文件 |
|------|----------|
| Scheduler v2 部署 | `run_all.py` → 新增 `scheduler_v2.py` |
| Detector 注册格式变更 | 所有 `src/zephyr/trading/feedback_loop/detectors/*.py` 头部 |
| Config 键新增 | `config.py` + `b_feedback_loop.yaml` |
| 容量升级施工 | Phase 0~4 路线图条目逐项 tick |

---

## §14 已知风险与缓解

> 本节同时承接原 §15 后果中的**负面后果**——设计决策带来的已知代价。
> 正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:---:|:---:|---------|------|
| 1 | RingBuffer 溢出静默丢事件 | M | H | 双缓冲 4096 + DROP lowest priority + backpressure counter | 风险 |
| 2 | 23 线程 CPU 超订 | M | M | `fle.scheduler.cpu_throttle_threshold` 自适应降速 | 风险 |
| 3 | LLM 限流导致 MTTD 恶化 | L | H | 三级 LLM fallback (OpenAI→DeepSeek→Claude) | 风险 |
| 4 | GateQueue 单点阻塞 | L | H | Owner 旁路协议 + `gate_process_timeout` 60s | 风险 |
| 5 | 并发寻找冲突 (多个 Actor 抢同一个修复) | M | L | Action Atomicity Manager + Saga 补偿 | 风险 |
| 6 | FLE 自我修改导致保护关闭 | L | H | Immutable Core Guard | 风险 |
| 7 | 32 代进化 → KB 膨胀 | M | M | Session 归档 + 知识新鲜度评分淘汰 | 风险 |
| 8 | FLE 自身资源消耗 ~20% CPU/内存 | — | M | 容量规划预留 + 自适应降速 | 负面后果 |
| 9 | 无外部备份 → 需要 Session rewind | — | M | Checkpoint Rewind + 冷启动恢复 | 负面后果 |
| 10 | FLE 被禁用时 32 代进化知识冻结不可用 | — | H | 知识归档 + 离线导出 | 负面后果 |

---

## §16 施工指引

| Phase | 内容 | 优先级 | 依赖 |
|:---:|------|:---:|------|
| Phase 0 | 蓝图补全 (本文件) | — | — |
| Phase 1 | D1+D2+D3+D4: Scheduler v2 + RingBuffer + DetectorRouter + Protocol A/B | 🔴 P0 | — |
| Phase 2 | D5+D6+D7+D11: Session 感知 + Scan 追踪 + 存储分片 + 批处理 | 🟠 P1 | Phase 1 |
| Phase 3 | D8+D12+D13+D14: KG 扩展 + SLA 架构 + 自观测 + 全量窗口 | 🟡 P2 | Phase 2 |
| Phase 4 | D9+D10: 部署扩缩 + 全量扫描可选 | 🟡 P2 | Phase 3 |

---

## §17 容量升级附录

> 完整容量升级方案（基线/缺口分析/升级版本矩阵/容量估算/施工指引）见：
> `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback_loop\capacity-upgrade\blueprint.md`

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-FLE-01 | EventDispatcher 单线程无锁 | A:多线程 B:单线程无锁 | B | 热点路径最短链路 → 无锁=最低延迟 | 2026-05-06 |
| 2 | D-FLE-02 | Detector 纯函数化 | A:有状态 B:纯函数 | B | 无副作用 → DetectorPool 安全并行 | 2026-05-06 |
| 3 | D-FLE-03 | RingBuffer 双缓冲 A/B | A:单缓冲 B:双缓冲 | B | 事件类别隔离 → A=CodeChange+Session, B=Scan+Anomaly | 2026-05-06 |
| 4 | D-FLE-04 | GateQueue 全局串行 | A:并行 B:串行 | B | L0→L67 有依赖链，并行=一致性断裂 | 2026-05-06 |
| 5 | D-FLE-05 | ActorPool 前置 GateQueue | A:直接执行 B:先过安全门 | B | 通过全部安全门后才执行 | 2026-05-06 |
| 6 | D-FLE-06 | DetectorRouter 按 latency 分类 | A:随机 B:按延迟分类 | B | ≤100ms→Quick; ≤5s→Deep; >5s→Batch | 2026-05-06 |
| 7 | D-FLE-07 | 单实例部署 | A:多实例 B:单实例 | B | 本地 Windows → 无 K8s | 2026-05-06 |
| 8 | D-FLE-08 | ThreadPoolExecutor (非 multiprocessing) | A:multiprocessing B:ThreadPool | B | I/O 密集 → GIL 无影响 | 2026-05-06 |
| 9 | D-FLE-09 | 周检 Sunday 02:00 | A:工作日 B:周末凌晨 | B | 最小化对正常运维干扰 | 2026-05-06 |
| 10 | D-FLE-10 | DryRun Sandbox | A:直接执行 B:沙箱预飞 | B | 高风险动作预飞 → 零生产环境副作用 | 2026-05-06 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉 |
| 5 | **涉及文件范围必须明确列出** | 范围漂移 |
| 6 | **容量估算必须写** | 容量瓶颈 |
| 7 | **迁移/废弃方案必须写** | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | 执行漂移 |
| 9 | **蓝图必须自包含** | 信息缺失 |
| 10 | **删除文件必须遵守安全删除协议** | 永久丢失 |
| 11 | **construction_progress 必须与代码实际状态一致** | 误导下一个AI |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| FLE 蓝图中"运行资产清单"(§1+§A+§B+§C) | **已拆分** → MOD-INF-041 | 独立职责域(资产盘点) + 内容>200行且与FLE主体无直接数据流 |
| FLE 蓝图中"检测器池目录"(蓝图特有A节) | **原地** | 检测器是 FLE 核心能力，不是独立子系统 |
| FLE 蓝图中"安全门注册表"(蓝图特有B节) | **原地** | 安全门是 FLE 核心防护，不是独立子系统 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| — | 本蓝图不涉及文件删除 | — | — | — | — |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持1个Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012+MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块ID注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 脚本系统蓝图 | MOD-INF-005 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\script-system\blueprint.md` | FLE↔ScriptSystem接口契约 |
| 8 | AI自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | Drift Detector | `D:\ZephyrAlpha\src\zephyr\drift-detector\` | 异常检测 | FLE是闭环自改进引擎，Drift Detector是单点检测器；FLE包含检测+诊断+修复+验证全链路 |
| 2 | Pipeline Orchestrator | `D:\ZephyrAlpha\src\zephyr\pipeline\` | 管线编排 | Pipeline是M1-M11静态管线，FLE是动态反馈闭环；职责不重叠 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | FLE源码 | `D:\ZephyrAlpha\src\zephyr\feedback_loop\` | 修改 | L级扩容组件新增 |
| 2 | FLE测试 | `D:\ZephyrAlpha\tests\unit\` | 修改 | 新增测试用例 |
| 3 | FLE蓝图 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback_loop\blueprint.md` | 修改 | 本文件 |
| 4 | YAML SSoT | `D:\ZephyrAlpha\architecture_model\layers\b_feedback_loop.yaml` | 修改 | 同步更新 |
| 5 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | 版本号更新 |

---

## 蓝图特有章节

### §A 检测器池目录

| 类别 | 数量 | 代表 detector | 延迟 |
|------|:---:|------|:---:|
| Quick: 统计/阈值 | ~30 | EMA, DynamicThreshold, ConformalPrediction | <100ms |
| Quick: 配置/Schema | ~10 | ConfigDrift, SchemaValidation | <100ms |
| Deep: LLM/Causal | ~15 | CausalInference, Counterfactual, MultiHypothesis | 1~5s |
| Deep: 安全合规 | ~10 | ImmutableCoreGuard, SecretLeak, CharterCompliance | 1~5s |
| Deep: 涌现行为 | ~5 | EmergentBehavior, ModelEnsembleDiversity | 1~5s |
| Batch: 知识/进化 | ~8 | SkillAtrophy, KnowledgeFreshness, CrossVersionRegression | >1min |
| Batch: 合同/审计 | ~5 | APIContractDrift, RegulatoryAudit, ForensicChain | >1min |

### §B 安全门注册表 (L0-L67)

| 层级 | 门 | 典型检查 |
|:---:|------|------|
| L0-L9 | 硬阻断 | ImmutableCore, SecretLeak, ConfigTampering |
| L10-L19 | 软门控 | SchemaValidation, BudgetOverflow, SkillFreshness |
| L20-L29 | 自指涉 | PersonalityStability, HallucinationAudit, TemporalCoherence |
| L30-L39 | 因果/涌现 | MultiHypothesis, EmergentBehavior, AdversarialSelfTest |
| L40-L49 | 自治/信任 | SubsystemMaturity, ResourceBudget, CharterCompliance |
| L50-L59 | 灾备/冗余 | CriticalPathRedundancy, InternalDeadlock, SupplyChain |
| L60-L67 | 金融专项 | ExchangeHalt, MarketAnticipatory, BestExecution, PnLAttribution |

### §C 演进审计总结

| 指标 | 值 |
|------|---|
| 进化代数 | 32 代 (v0.1.0 → v0.35.0-draft) |
| 盲点覆盖 | 429 (B1-B429, 来自 32 轮审计) |
| 安全纵深 | 67 层 (L0-L67) |
| 反模式注册 | AP1-AP65 (从 32 轮盲点审计提炼) |
| 设计决策 | DD1-DD142 (从 §1A-§1N + GP1-GP5 + 32 轮) |

### 完整路径索引

> 335 源码文件 + 7 测试文件分布在 `src/zephyr/trading/feedback_loop/` 下（actors/collectors/detectors/diagnosers/evolution/forensic/gates/resilience/security/verifiers 10 子包）。完整文件清单由 `python scripts/governance/generate_project_path_tree.py --write` 生成至 `data/asset_index/`。

---

## 治理信息

### SSoT声明

| 项 | 值 |
|---|---|
| SSoT文件 | `architecture_model/layers/b_feedback_loop.yaml` |
| 蓝图文件 | `docs/03_modules/_cross_layer/feedback_loop/blueprint.md`（本文件） |
| 冲突规则 | YAML SSoT为准；蓝图提供设计细节和施工指引 |

### 消费者注册表

| 消费者 | 消费方式 | 影响评估 |
|--------|---------|---------|
| Orchestrator | FLE异常调度接口 | 接口变更需同步 |
| Script System | FLE↔Script契约 | 接口变更需同步 |
| Audit Trail | FLE审计日志写入 | 日志格式变更需同步 |
| Blueprint Registry | 版本号+完整度 | 版本变更需同步 |

### 变更同步规则

| 变更本蓝图时 | 必须同步更新 |
|-------------|------------|
| 版本号变更 | `blueprint_registry.yaml` + `b_feedback_loop.yaml` |
| 接口契约变更 | 消费者模块蓝图 + `shared_quickref.yaml` |
| 新增/删除文件 | `module_registry.yaml` + `__init__.py` |
| 安全层变更 | `quality-standard.md` + gate注册表 |

### 修改条件

| 条件 | 触发 |
|------|------|
| 新增检测器/安全层 | 必须更新§3架构+§14风险+§0代码对齐 |
| 接口签名变更 | 必须更新§4接口契约+消费者蓝图 |
| 容量升级 | 必须更新§5.2容量估算+§17容量升级 |
| 删除组件 | 必须遵守安全删除协议 |

---

## 已实现代码完整路径索引

> 完整路径索引（335 源码 + 7 测试）由 `python scripts/governance/generate_project_path_tree.py --write` 生成至 `data/asset_index/`。代码分布在 `src/zephyr/trading/feedback_loop/` 下 10 个子包：actors/collectors/detectors/diagnosers/evolution/forensic/gates/resilience/security/verifiers。

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 反馈闭环——6文件骨架+metrics_collector+fitness_functions已实现

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/observability/feedback_loop/_gen_inherited.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/action_selector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/agent_lifecycle.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/actors/alert_router.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/api_version_contract.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/global_action_scheduler.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/incident_priority_triage_automator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/intent_driven_ops.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/multi_agent_orchestrator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/actors/notification_personalizer.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/owner_absence_escalation.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/actors/saga_compensator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/actors/secondary_alert_channel.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/auto_evolution.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/backpressure_bridge.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/calendar_adapter.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/collectors/config_timeline.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/data_quality_validator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/collectors/feedback_collector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/financial_stratification.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/collectors/kb_provenance.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/collectors/knowledge_capture.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/knowledge_freshness.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/knowledge_injection.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/knowledge_packaging.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/collectors/known_unknown_registry.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/llm_cost_accounting.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/market_calendar.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/market_event_integrator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/metrics_collector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/notification_feedback.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/schema_evolution.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/collectors/schema_migration.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/temporal_event_store.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/collectors/token_finops.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/config.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/db_bridge.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/decision_engine.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/action_efficacy_decay_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/action_interaction_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/action_side_effect_cumulative_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/agent_trajectory_anomaly_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/alert_desensitization_curve.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/anomaly_clustering.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/anomaly_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/autoscale_remediation.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/blast_radius.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/blast_radius_budget.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/capacity_forecast.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/chaos_engineering.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/concept_drift.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/config_drift.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/context_window_contamination_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/cross_signal_validator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/cross_system_correlator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/decision_provenance.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/dependency_freshness_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/diminishing_returns_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/ebpf_monitor.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/emergent_behavior_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/ensemble_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/ensemble_drift.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/external_health.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/external_validation_checkpoint.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/flag_lifecycle.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/flapping_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/fle_performance_regression_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/gradual_poisoning_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/guard_cascade_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/guard_oscillation_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/heisenbug_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/infinite_loop_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/intermittent_failure_pattern.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/log_anomaly.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/maintenance_coordinator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/metric_cardinality_guard.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/multi_signal_correlator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/openfeature.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/otel_adapter.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/placebo_action_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/positive_feedback_defense.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/recursive_diagnosis_trust_evaluator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/regime_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/regulatory_audit.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/resolution_tracker.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/rumor_noise_filter.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/runbook_executor.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/self_audit.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/self_diagnosis_data_leak_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/self_ha.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/silent_corruption_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/synthetic_anomaly_generator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/temporal_coherence_of_self_model.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/temporal_pattern.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/trace_causal_bridge.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/traffic_replay_validator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/detectors/trend_cycle_separator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/detectors/version_migrator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/action_composition_health_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/adaptive_param_tuning.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/amplification_guard.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/api_dependency_metrics.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/auto_diagnosis.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/burn_rate_alerter.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/burnout_alarm.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/capacity_aware_repair.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/causal_inference_engine.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/cognitive_load.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/cognitive_load_budget.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/cold_start_conservative_mode.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/collaborative_learning.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/confidence_decomposer.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/context_truncation.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/context_window_pressure_manager.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/counterfactual.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/cross_guard_conflict_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/cross_session_consistency_validator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/data_volume_growth_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/diagnosis_engine.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/diagnosis_kpi.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/dr_resilience_metrics.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/e2e_integration_health.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/feedback_delay_compensator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/fle_dogfood_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/fle_self_slo_metrics.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/gamification.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/global_health_map.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/guard_interaction_topology_mapper.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/guard_self_consistency_auditor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/human_anomaly_flood_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/impact_predictor.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/incident_knowledge_injector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/interactive_diagnosis.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/knowledge_bus_factor_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/knowledge_market.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/latency_slo.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/llm_provider_integrity.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/llm_quality_regression.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/memory_self_check.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/meta_guard_latency_budget.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/model_health.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/model_rotation.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/model_rotation_v2.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/model_version_semantic_drift.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/mtti_tracker.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/nonstationary_effectiveness.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/numerical_stability_guard.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/operational_seasonality.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/prompt_fingerprint.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/prompt_sanitizer.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/recovery_time_stats.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/regime_gain_scheduling.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/retirement_planner.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/self_benchmark.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/self_bottleneck_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/self_health_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/self_llm_observability.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/slo_capacity_metrics.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/socratic_questions.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/diagnosers/statistical_hygiene_auditor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/system_entropy_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/temporal_integrity_guard.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/timezone_semantic_reasoner.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/toil_quantification.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/tone_adapter.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/tone_adapter_v2.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/value_added_baseline.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/vertical_self_assessment.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/diagnosers/zombie_fle_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/docs/cold_start_manual.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/error_budget.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/eval_harness.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/auto_reward.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/evolution/conformal_prediction.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/evolution/cross_gen_validation.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/evolution/dynamic_threshold.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/evolution/ewc_kb_review.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/failure_replay.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/graduated_activation_protocol.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/hypernetwork.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/evolution/knowledge_distillation.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/evolution/online_feature_importance.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/prompt_factory_governance.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/prompt_optimization_regression_detector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/prompt_self_optimization_loop.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/self_modification_rate_limiter.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/self_reflection.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/evolution/self_upgrade_canary.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/semantic_intent_preservation_guard.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/teacher_transfer.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution/training_data_gov.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/evolution_engine.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/exceptions.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/feedback_collector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/fitness_functions.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/architectural_sod.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/automated_rca_postmortem_generator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/boot_integrity_attestation.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/crypto_bootstrap.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/deterministic_replay.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/external_verifier.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/fle_upgrade_safety_validator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/guard_complexity_budget.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/guard_configuration_drift_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/interrupt_coherence_validator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/knowledge_injection_pre_flight_verifier.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/point_in_time_reconstructor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/self_modification_audit.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/serialization_format_tracker.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/state_migration_validator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/sub_agent_collusion.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/toctou_guard.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/forensic/worm_write_integrity.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/action_reversibility.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/adversarial_validation.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/autonomy_credit.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/autonomy_maturity.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/blueprint_code_reconciler.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/blueprint_validator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/checkpoint_manager.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/ci_cd_pre_scanner.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/concurrent_change_deconfliction.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/config_complexity_budget.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/config_governance.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/conflict_arbitration.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/cve_scanner.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/data_quality_gate.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/db_integrity.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/deployment_suppression.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/dynamic_llm_cost_router.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/emergency_takeover.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/federated_security.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/flag_lifecycle_manager.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/license_compliance.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/llm_cost_router.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/merkle_audit_root.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/meta_performance_gate.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/gates/parameterized_safety_gate.py` | ✅ 已实现 | |
| `src/zephyr/trading/feedback_loop/gates/safety-gate-config.yaml` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L1_L27.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L28_L29.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L36_L37.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L38_L39.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L40_L41.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L42_L43.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L44_L45.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L46_L47.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L48_L49.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L50_L51.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L52_L53.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L54_L55.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L56_L57.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L58_L59.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L60_L61.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L62_L63.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L64_L65.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/safety_gate_L66_L67.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/gates/scope_creep_monitor.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/generator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/metrics_collector.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/protocols.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/config_hot_reload_guard.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/deadman_switch.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/dr_automation.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/graceful_degradation_planner.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/multi_instance_coord.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/oscillation_damping.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/resource_starvation_aware.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/self_api_throttle_defense.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/resilience/split_brain_quorum.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/scheduler.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/scheduler_act.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/scheduler_collect_detect.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/scheduler_health.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/scheduler_safety.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/security/agent_skill_guard.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/security/dep_cve_correlator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/security/metric_prompt_scanner.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/security/remote_attestation.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/security/secret_rotation.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/security/wireheading_prevention.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/slo_manager.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/subdir/test_file.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/template.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/tests/e2e/integration_test_pipeline.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/validator.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/ab_test.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/action_explainability.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/ai_comment_veracity.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/attack_simulator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/auto_rollback.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/build_reproducibility_verifier.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/canary_repair.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/cascading_rollback_analyzer.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/cross_blueprint_contract_drift.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/cross_module_integration.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/cross_session_knowledge_integrity.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/digital_twin_sandbox.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/dry_run_sandbox.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/federated_protocol.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/golden_test_external.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/no_llm_degradation.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/pre_flight_simulator.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/preventive_repair.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/rollback_integrity.py` | ⚠️ 骨架 | |
| `src/zephyr/observability/feedback_loop/verifiers/sim2real_calibration.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/stochastic_diagnosis_verifier.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/toctou_revalidation.py` | ✅ 已实现 | |
| `src/zephyr/observability/feedback_loop/verifiers/verification_engine.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/test_metrics_collector.py` | ❌ 未实现 | |
| `tests/test_fitness_functions.py` | ✅ 已实现 | |
| `tests/test_feedback_collector.py` | ✅ 已实现 | |
| `tests/test_auto_evolution.py` | ✅ 已实现 | |
| `tests/test_evolution_engine.py` | ✅ 已实现 | |
| `tests/test_eval_harness.py` | ✅ 已实现 | |
| `tests/integration/test_evolution_e2e.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-14 | — | v3.5模板升级：§0前移至概述后；§7备选方案删除；§15后果删除（负面合并到§14）；§0.1新增存在性列；§5.1去掉原因列；§5.3标注临时时态；§10拆为4子节；§14新增类型列；铁律#13-#15；蓝图拆分判定标准；压缩工作流执行 |
| 2026-05-15 | 0.34.2 | v3.5模板升级+压缩：§0前移至概述后；§7备选方案删除(信息由§18覆盖)；§15后果删除(负面合并到§14+类型列)；§0.1新增存在性列(受控词表)；§5.3标注临时时态；§10拆为10.1-10.4；铁律新增#13-#15；新增蓝图拆分判定标准；frontmatter summary压缩≤80字；标准锚点更新v3.5；§3.2 ASCII图转表格；施工声明标注时态属性 |
| 2026-05-14 | 0.34.1 | v3.3 模板重构：新增概述段；章节重排(§1-§15→§0→§16-§18→规则参考)；§4补充4.4-4.6；§5.2/§5.3/§10/§11/§14/§17/§18格式升级；规则参考段移至尾部 |
| 2026-05-13 | 0.34.0-codified | Layer 2 深度规格化砍削：22,384行→648行(-97%)。砍A.0-A.7审计叙述、§2.211-2.xxx 300+检测器规格→A节汇总表、§7 R1-R433风险注册表→§14 7项核心风险、§1A-§1N ASCII图→§3.1组件表+§3.2数据流、depends_on外部系统清理。 |
| 2026-05-10 | 0.34.0-draft | L级容量升级方案。14设计缺口+14新设计+Phase 0~4 |
| 2026-05-06 | 0.33.0 | 32轮：市场滥用监控+金融压力测试+L66 |
| 2026-05-06 | 0.32.0 | 31轮：Pre-Trade风险+最佳执行+P&L归因+L64+L65 |
| 2026-05-06 | 0.31.0 | 30轮：策略隔离+网络分区+不可变基础设施+L62+L63 |
| 2026-05-06 | 0.30.0 | 29轮：ExchangeHalt+企业事件+Flag债务+L60+L61 |
| 2026-05-06 | 0.29.0 | 28轮：量子签名+信息隐瞒+时区语义+L58+L59 |
| 2026-05-06 | 0.28.0 | 27轮：演化债务+目的偏离+循环检测+L56+L57 |
| 2026-05-06 | 0.27.0 | 26轮：子系统冲突+认知失调+死锁+L52+L53 |
| 2026-05-06 | 0.26.0 | 25轮：子系统成熟度+资源预算+章程合规+L50+L51 |
| 2026-05-06 | 0.25.0 | 24轮：云API+模型漂移+渐进自治+L48+L49 |
| 2026-05-06 | 0.24.0 | 23轮：涌现行为+管道背压+对抗自测+L46+L47 |
| 2026-05-06 | 0.23.0 | 22轮：自SLO+Prompt链放大+Runbook自生成+L44+L45 |
| 2026-05-06 | 0.22.0 | 21轮：观察者效应+反事实+动作原子性+L42+L43 |
| 2026-05-06 | 0.21.0 | 20轮：元自知+不可变核心+技能萎缩+L40+L41 |
| 2026-05-06 | 0.20.0 | 19轮：确定性护栏+FMEA+创伤后知识+L38+L39 |
| 2026-05-06 | 0.19.0 | 18轮：AI代码SAST+信任衰减+部署完整性+L36+L37 |
| 2026-05-06 | 0.18.0 | 17轮：MTTI+全局调度+认知负载+L34+L35 |
| 2026-05-06 | 0.17.0 | 16轮：氛围编程原生+ZombieFLE+Config预算+L32+L33 |
| 2026-05-06 | 0.16.0 | 15轮：外部取证+密码学信任+Deadman+L30+L31 |
| 2026-05-05 | 0.15.0 | 14轮：DR自动化+SLO管理+供应链+L28+L29 |
| 2026-05-05 | 0.14.0 | 13轮：混沌工程+Flag治理+合规审计 |
| 2026-05-05 | 0.13.0 | 12轮：意图驱动+AgenticOps+LLM自观测 |
| 2026-05-05 | 0.12.0 | 11轮：数据根基+元性能+运维智能 |
| 2026-05-05 | 0.11.0 | 10轮：联邦+自治+生态可移植 |
| 2026-05-05 | 0.10.0 | 9轮：数据质量+Schema+合成异常 |
| 2026-05-05 | 0.9.0 | 8轮：Auto-Rollback+冷启动+CVE |
| 2026-05-05 | 0.8.0 | 7轮：动态阈值+共形预测+自治阶梯 |
| 2026-05-05 | 0.7.0 | 6轮：EWC+数字孪生+认知负载 |
| 2026-05-05 | 0.6.0 | 5轮：跨模块集成+知识新鲜度+Regime |
| 2026-05-05 | 0.5.0 | 4轮：Ensemble检测+多信号关联 |
| 2026-05-05 | 0.4.0 | 3轮：因果推断+Config-as-Code+Dry-Run |
| 2026-05-05 | 0.3.0 | 2轮：盲点补丁因果推断+配置治理 |
| 2026-05-03 | 0.2.0 | 蓝图-代码地址簿完善 |
| 2026-05-03 | 0.1.0 | 初始创建三阶段流水线+EMA异常检测 |
