---
ttl: permanent
doc_type: architecture_view
title: AutoRuntime Core 施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.2"
date: 2026-08-17
topic: autoruntime_core_build
scope: 09_ai_architecture
---

# AutoRuntime Core 施工图

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：GP0 T0 七件落地——auto_runtime_core.py（MOD-INF-035 系统大脑本体）+capability_registry.py（内存缓存+读写锁+TTL+命中计数）+runtime_config.py（max_brain_memory_mb RAM 预算）+start_brain.py（--boot-sla-ms 冷启动 SLA 埋点）+stop_gate.py（会话预算）+resource_optimization.py（PressureLevel 降级链）；§3.6 自治层不变量 INV-AU-001~008 设计态登记。
> **最终成果**：GP0 范围全落地（蓝图 5 漂移项裁定留痕）。
> **未做+原因**：①容量升级 12 项 GAP 属 GP1+ 触发式施工（既定分期，非缺口）；②boot watchdog NoneType 存量缺陷+SLA 20 次连跑复测（tracker #255 登记）；③本文版本未回写施工后状态（小滞后）。

> 本文定位：AutoRuntime Core（系统大脑）五层同心圆架构的施工落地计划。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md) §1（基础设施层），蓝图见 `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md`（MOD-INF-035，v6.0.2）。
>
> **阅读顺序**：§2 背景（现状实测）→ §3 设计决策（why）→ §4 施工计划（how，Phase 0→3）→ §5 不做什么 → §6 开放问题。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | AutoRuntime Core 施工 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·基础设施层（「AutoRuntime Core · 三层运行时 · LLM 安全栈」） |
| 依赖 | AutoRuntime Core 蓝图 v6.0.2（MOD-INF-035，`docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md`） |
| 优先级 | P0——系统大脑是所有 AI 能力的运行时载体 |
| 状态 | draft（骨架填充完成，进入循环修订） |

---

## 2. 背景

### 2.1 项目处境

AutoRuntime Core 是 ZephyrAlpha 的系统大脑（MOD-INF-035），负责全局运行时编排：MAPE-K 调和循环、工作编排（DAG）、自动接入（孤儿检测）、能力注册、健康监控、审计日志。它是 AI 层所有能力（自我进化、执行层 Agent、AI 安全）的运行时底座。

**实测现状（2026-08-17 扫描，验证命令见 §2.4）**：

| 维度 | 现状 | 出处 |
|---|---|---|
| 蓝图版本 | v6.0.2，generation=2，`build_status: planned`（容量升级设计完成、代码待施工） | blueprint frontmatter |
| 基线代码 | v5.0.0「24 子组件完整实现」已落地（蓝图 §17.3 标 ✅） | blueprint §17.3 |
| 代码落盘位置 | `src/zephyr/trading/`（实测 44 个 .py 文件），与蓝图 frontmatter `actual_disk_path: src/zephyr/trading/` 一致 | LS 实测 |
| 当前规模基线 | ~51 模块 / ~268 治理脚本 / 0 AI 并发 Session；大脑 RAM 稳态 ~50MB、VRAM ~2GB、MAPE-K 单轮 ~50ms、冷启动 ~2s | blueprint §17.1 |
| 目标容量 | 1,500 模块 / 10,000 脚本 / 100 AI 并发（远期容量愿景，触发式施工，见 §3.1 决策 6） | blueprint §1.1 |
| 运行模式 | `start_brain.py` 默认 `--once` 单次模式（boot → reconcile → shutdown → 退出），进程不常驻；CircadianScheduler 的 start/register_task/stop/save_state 均为 no-op 空实现 | `scripts/construction/start_brain.py` docstring |
| 启动入口 | `scripts/construction/start_brain.py`（MOD-INF-005，production） | 文件头实测 |

**关键认知**：大脑不是「待从零新建」的模块——基线 24 组件已在生产运行（`[MATURITY] production`）。本文档的施工对象是 **generation=2 容量升级（12 项 GAP）+ 蓝图-代码对齐修复**，而非基线重建。

### 2.2 核心问题

1. **蓝图-代码漂移（P0，阻塞后续一切）**：蓝图 §0.1 文件清单与磁盘实测不符——`circadian_scheduler.py`、`health-monitor.py`、`feedback_loop.py`、`boot_cron_jobs.py` 四个条目在 `src/zephyr/trading/` 下不存在。实测：节律调度功能现由 `status_dashboard.py`（内含原 `get_current_phase()` 的内联实现）/ `auto_runtime_core.py`（保留 boot 流程钩子）承载，`lifecycle_manager.py`/`runtime_config.py` 不含调度参数与调用，全程无独立 `circadian_scheduler.py` 文件；健康监控实为 `health_monitor.py`（下划线命名）；反馈闭环在独立包 `src/zephyr/feedback_loop/`；启动钩子实为 `boot_hooks.py`。另有第 5 项：蓝图 §16.3/§16.5 的产出位置写 `src/zephyr/runtime/`、测试目录写 `tests/runtime/`，实测代码在 `src/zephyr/trading/`、测试在 `tests/trading/`+`tests/automation/`（`tests/runtime/` 不存在）。蓝图 §16 施工指引仍引用这些幽灵文件名/路径，按蓝图施工会直接踩空。
2. **容量升级 12 项 GAP 全部「待施工」**（蓝图 §17 缺口清单）：MAPE-K 全量轮询 O(n) 退化、WorkOrchestrator 无 WIP 限制、Scanner 全量扫描、GPU 无调度模型、大脑无自监控、RAM 无预算、I/O 无缓冲、无全局准入、无降级链、无冷启动 SLA、Agent Spec 语义路由缺失、AGENTS.md 触发表膨胀。其中 GAP-008 需新建 `brain_admission_controller.py`（磁盘实测不存在；现有 `admission_controller.py` 是 MOD-INF-033 行为审计准入，不同物）。
3. **施工顺序问题（骨架 Q1）**：五层同心圆（L0 自举 → L1 调和 → L2 执行 → L3 知识 → L4 编排）的基线已全部有代码，真正的顺序问题是 **12 项容量 GAP 的落地顺序**——蓝图已给出答案：按 T0→T1→T2→T3 四拐点触发式推进（§3.1 决策 6 采纳）。
4. **与既有运行时的边界问题（骨架 Q2）**：`src/zephyr/runtime/intraday_main.py` 实测为 MOD-RUNTIME_INTRADAY（盘中 tick→因子数据流编排器，production），与 AutoRuntime Core 是**不同物**——前者管交易时段数据流，后者管全项目模块运行时治理。不重写、不合并（§3.3）。

### 2.3 约束条件

| 约束 | 对大脑施工的影响 | 出处 |
|---|---|---|
| 单机 i7-12700KF 12C20T / 64GB RAM / RTX 3090 24GB，无集群/K8s | 大脑进程预留 8GB RAM / 4GB VRAM 不可超限；单进程架构（D-INF035-01） | system_charter §2 / blueprint §1.4 |
| GPU 显存 <90% 硬上限（≈21.6GB 可用） | GPU 时间分片 + VRAM 硬分区（D-INF035-04）；白天 Worker Pool / 夜间 DreamCycle 共享 | blueprint §1.4 |
| Windows 单机、家用环境、RTO<5 分钟 | L0 自举层需 Windows Service 包装器（`windows_service.py` 已有）；用降级链而非热备 | blueprint §1.4 |
| Python GIL | I/O 密集用 ThreadPoolExecutor；CPU 密集才考虑多进程 | blueprint §1.4 |
| miniQMT 10 笔/秒、Tick=3 秒、T+1 | 交易时段大脑降载（降级链 Lv1+ 暂停 OrphanDetector/推迟 DreamCycle），盘中资源让给数据流 | system_charter §2 / blueprint §3.3 |
| 无 git 备份容错、删除不可逆 | 大脑施工遵守安全删除协议；蓝图-代码对齐修复只改登记不删文件 | blueprint §1.4 |
| 1 人 + 100% AI 生成代码 | 容量项触发式施工——无触发不建，避免 1 人维护过剩产能 | system_charter §2 施工方式 |
### 2.4 已施工设施盘点

> 实测纪律：每行均经 LS/Read/Grep 验证。验证基准日 2026-08-17。
> 验证命令示例：`Get-ChildItem -File src\zephyr\trading -Filter *.py`（44 个文件）；`Test-Path <路径>`。

**A. 蓝图与治理**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 蓝图 | `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md` | MOD-INF-035 v6.0.2，五层同心圆 24 组件 + §17 容量升级附录（12 GAP + 四拐点矩阵） | Active / build_status=planned |
| 蓝图索引 | `docs/03_modules/_cross_layer/auto_runtime_core/index.md` | 蓝图配套索引 | Active |
| 依赖登记 | `scripts/governance/apply_depgraph.py` | depgraph 设计态/生产态登记工具（规则 19 使用，支持 --batch/--dry-run） | production |

**B. 大脑核心代码（`src/zephyr/trading/`，蓝图 §3.1 的 24 组件映射，实测存在）**

| 层级 | 组件（蓝图 §3.1） | 实测代码文件 | 状态 |
|---|---|---|---|
| L1 调和 | AutoRuntimeCore（MAPE-K 主控） | `auto_runtime_core.py`（MOD-INF-035，含 `_OllamaProcessManager`/`_LocalModelBootstrap`） | production |
| L1 调和 | HealthMonitor 健康监控+自愈 | `health_monitor.py`（⚠️ 蓝图写 `health-monitor.py` 连字符，漂移项） | production |
| L1 调和 | FeedbackLoop 反馈闭环 | 独立包 `src/zephyr/feedback_loop/`（⚠️ 蓝图写 `trading/feedback_loop.py`，漂移项） | production |
| L1 调和 | StatusDashboard 状态面板 | `status_dashboard.py` | production |
| L1 调和 | StopGate / Finalizer / TaskGate | `stop_gate.py` / `finalizer.py` / `task_gate.py` | production |
| L2 执行 | AutoTaskGenerator 推理任务生成 | `auto_task_generator.py` | production |
| L2 执行 | AutoIntegrator / ModuleOnboardingScanner / OrphanDetector | `auto_integrator.py` / `module_onboarding_scanner.py` / `orphan_detector.py` | production |
| L2 执行 | CapabilityRegistry / CapabilityCard | `capability_registry.py` / `capability_card.py` | production |
| L2 执行 | AiAuditLogger / IntegrationRegistry / ActionDispatcher | `ai_audit_logger.py` / `integration_registry.py` / `action_dispatcher.py`（另有同名子目录 `action_dispatcher/`） | production |
| L3 知识 | DreamCycle 夜间固化 / NightShiftQueue | `dream_cycle.py` / `night_shift_queue.py` | production |
| L4 编排 | WorkOrchestrator / WorkDAG | `work_orchestrator.py` / `work_dag.py` | production |
| L0 自举 | RuntimeConfig / LifecycleManager / WindowsService | `runtime_config.py` / `lifecycle_manager.py` / `windows_service.py` | production |
| L1 调和 | CircadianScheduler 节律调度接口 | ❌ 无独立文件——start/register_task/stop/save_state 为 no-op 空实现；`status_dashboard.py` 内含原 `get_current_phase()` 内联实现，`auto_runtime_core.py` 保留 boot 流程钩子 | **deprecated** |

**C. 大脑配套组件（`src/zephyr/trading/`，蓝图 §0.1 附加行，实测存在）**

| 路径 | 内容简述 | 状态 |
|---|---|---|
| `boot_hooks.py` | 启动钩子（⚠️ 蓝图写 `boot_cron_jobs.py`，漂移项） | production |
| `capability_sync.py` | 能力同步 | production |
| `resource_optimization.py` | 资源优化 | production |
| `staging_area.py` | 多 AI 并发草稿暂存（CP-1010~1014） | production |
| `gpu_monitor.py` / `ide_health_daemon.py` / `zombie_scanner.py` | GPU 监控 / IDE 健康守护 / 僵尸进程扫描 | production |
| `autopilot.py` / `conductor.py` / `auto_dispatcher.py` / `trigger_registry.py` / `speed_baseline_checker.py` | 自动领航 / 指挥 / 自动分派 / 触发登记 / 速度基线（trading 包内大脑周边，归属以 depgraph 为准） | production |

**D. 启动入口与测试**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 启动脚本 | `scripts/construction/start_brain.py` | 大脑一键启动（`--once` 单次调和为默认；`--no-generate` 跳过任务生成） | production（MOD-INF-005） |
| 单元/E2E 测试 | `tests/automation/test_auto_runtime_core.py`、`test_auto_runtime_e2e.py`、`test_auto_runtime_fle_integration.py` | 大脑核心 + 端到端 + 反馈环集成测试 | production |
| 编排测试 | `tests/trading/test_work_orchestrator.py` | WorkOrchestrator 测试 | production |

**E. 易混淆但非本主题的设施（归属澄清，防止盘点串味）**

| 路径/位置 | 实际归属 | 与本主题关系 |
|---|---|---|
| `src/zephyr/runtime/intraday_main.py` | MOD-RUNTIME_INTRADAY（D_INFRA_RUNTIME）盘中数据流编排 | 不同物，见 §3.3；互不重写 |
| `src/zephyr/autonomy_core/`（实测 113 个 .py：根 14 + `context/` 39 + `integration/` 2 + `skills/` 58） | MOD-AUTONOMY_CORE（AI 自治基础设施：技能子系统 + 上下文引擎子系统） | 大脑的能力消费对象之一；Context Engine 施工图见 [07_context_engine_build.md](07_context_engine_build.md) |
| `data/brain/job_matrix.yaml` + `data/brain/passports/`（7 个模型护照 JSON）+ 3 个 exam_results.json | 06 号文模型画像流水线域（消费方 `src/zephyr/intelligence/model_profiling/job_matcher.py`） | 目录名含 brain 但**不是** AutoRuntime 设施；大脑经 ModelRouter 间接消费其产出 |
| `src/zephyr/trading/admission_controller.py`、`gpu_consensus_scheduler.py`、`verdict_engine.py` | MOD-INF-033 行为审计（behavioral_auditor 蓝图 §17） | 与 GAP-008 拟新建的 `brain_admission_controller.py` 不同物，禁止复用混名 |

---

## 3. 设计决策

### 3.1 五层同心圆架构决策

**分层（以蓝图 §3.1 为真源）**：L0 自举层 → L1 调和层 → L2 执行层 → L3 知识层 → L4 编排层。

| 层 | 职责 | Why 这样分层 | 考虑过的替代方案 |
|---|---|---|---|
| L0 自举 | 配置模型、生命周期序列、Windows Service 包装 | 单机 Windows 家用环境必须能在崩溃后 5 分钟内自愈重启（RTO<5min 约束），自举逻辑必须与调和逻辑隔离——调和循环崩了，自举层还能拉起它 | 并入 L1：调和循环故障时无人拉起，违反 RTO 约束 |
| L1 调和 | MAPE-K 对账循环、健康监控、反馈闭环、质量闸门、状态面板 | 「巡模块、发现漂移、调和修复」是大脑存在的理由；水平触发式对账（事件驱动+兜底轮询，D-INF035-02）避免纯轮询 O(1500) 退化，也避免纯事件漏检 | 纯轮询（O(n) 不可接受）/ 纯事件（漏检风险），均已否决 |
| L2 执行 | 任务生成、模块接入、孤儿检测、能力注册、审计、动作分派 | 「做事的手」与「决策的脑」（L1）分离：执行组件可被 L1 单独重启/降级（降级链 Lv1 暂停 Scanner、Lv2 停 OrphanDetector），耦合则无法按组件降级 | 并入 L1：降级粒度从组件级退化为全有或全无 |
| L3 知识 | DreamCycle 夜间固化、夜班登记 | 知识固化是重 GPU/重 I/O 的批处理，必须押后到夜间窗口，与日间盘中共存需要独立层做时间隔离 | 并入 L2：日间推理任务与夜间固化抢 GPU，无隔离手段 |
| L4 编排 | WorkOrchestrator DAG 调度、WorkDAG 数据模型 | 多 AI Session 并发的工作必须 DAG 化才能做依赖排序+公平调度+饥饿防护（GAP-002）；编排决策依赖 L2 的能力注册产出，故在最外圈 | 消息队列直投：无依赖表达、无公平性，100 AI 并发下饥饿无解 |
**关键已裁定决策（蓝图 §18，本文不重开，仅登记为施工约束）**：

| # | 决策ID | 决策 | 对施工的含义 |
|---|---|---|---|
| 1 | D-INF035-01 | 单进程架构（瓶颈在 I/O 不在 CPU） | 不引入多进程大脑；ThreadPoolExecutor 承载 I/O 并发 |
| 2 | D-INF035-02 | MAPE-K 事件驱动 + 兜底轮询 | GAP-001 施工按此实现 |
| 3 | D-INF035-03 | 容量升级渐进四拐点（T0→T3） | 本文 §4 的 Phase 划分直接对齐四拐点 |
| 4 | D-INF035-04 | GPU 时间分片 + VRAM 硬分区 | GAP-004 施工按此实现；不建独立 GPU 调度器（10 号文同判） |
| 5 | D-INF035-05 | 四级降级链 Lv0~Lv3 | 代替热备满足 RTO<5min（§5 第 2 项） |
| 6 | D-INF035-06 | Skill 路由语义向量检索（>500 Skill 触发） | 由 MOD-INF-019 承接，不在本文施工范围 |
| 7 | D-INF035-07 | AiAuditLogger 环形缓冲 + 批量 flush | GAP-007 施工按此实现 |
| 8 | D-INF035-08 | 大脑 RAM 上限 2GB | GAP-006 `max_brain_memory_mb` 参数来源 |
| 9 | D-INF035-09 | 冷启动 SLA P99 <10s | GAP-010 验收标准来源 |
| 10 | D-INF035-10 | Agent Spec 容量缺口由 MOD-INF-019 承接 | GAP-011/012 不在本文施工范围 |

**容量目标定位说明**：1,500 模块 / 100 AI 并发是蓝图远期容量愿景，非当前需求（当前 51 模块 / 0 AI 并发）。按通用规则 5，已显式标注触发阈值的远期工程不算过度工程——本文施工计划严格执行「无触发不施工」（§4 Phase 1~3 的启动条件）。

### 3.2 与 AI 层的关系：大脑如何承载上层能力

| 上层能力 | 承载机制 | 证据/出处 |
|---|---|---|
| LLM 三层运行时（10 号文） | 大脑内含 `_OllamaProcessManager`（Ollama 进程生命周期）+ `_LocalModelBootstrap`（本地模型栈启动编排），是 L2 本地推理的实际承载者 | `auto_runtime_core.py` 实测 + 10 号文 §2 |
| 模型路由/画像（06 号文） | 大脑 import `ModelRouter`（governance）与 `model_profiling` 包，任务→模型分发经 ModelRouter 决策 | `auto_runtime_core.py` import 实测 |
| Context Engine（07 号文） | 蓝图 references 声明「MOD-CONTEXT_ENGINE——大脑消费上下文注入」；`autonomy_core/context/` 子系统已 production | blueprint frontmatter references |
| 自我进化（11/12/13 号文） | DreamCycle（L3）夜间知识固化 + AutoTaskGenerator（L2）自动生成推理任务 = 自我进化的运行时引擎；`autonomy_core/skills/` 技能子系统由大脑经 Skill 注册发现（蓝图 references MOD-INF-019） | blueprint §2.1 |
| AI 安全（09/15/16 号文） | AiAuditLogger 行为审计、StopGate/TaskGate 双闸门、四级降级链 Lv3→Kill Switch 通知 Owner | blueprint §3.1/§3.3 |
| 多 AI 并发治理（08 号文） | `staging_area.py`（CP-1010~1014 多 AI 草稿写入+冲突检测）已在 trading 包内 production | 文件头实测 |

### 3.3 与 `src/zephyr/runtime/` 的关系（骨架 Q2 的实测裁定）

实测：`src/zephyr/runtime/intraday_main.py` 是 MOD-RUNTIME_INTRADAY——盘中单进程数据流编排器（tick_subscriber → Redis → IntradayFactorLoop），管的是**交易时段数据管道**；AutoRuntime Core 管的是**全项目模块的运行时治理**。两者领域不同（数据流 vs 模块治理）、生命周期不同（盘中常驻 vs `--once` 单次调和）、代码无继承关系。

**决策**：在现有代码上扩展，不重写、不合并。大脑的容量升级全部落在 `src/zephyr/trading/` 既有文件上追加（蓝图 §16.1 施工模式=扩展）；`intraday_main.py` 不在本文施工范围。

### 3.4 与 10 号文（LLM 基础设施）的接口对齐

10 号文 v0.2.2 已填充，其 §6 Q3 假设：「AutoRuntime Core 继续承担 Ollama 进程管理与本地模型栈 boot；`llm_runtime_gateway` 门面被 AutoRuntime Core 消费而非取代其编排职责」。

**本文确认该假设成立**，理由：① 现状代码已如此（`_OllamaProcessManager`/`_LocalModelBootstrap` 在 `auto_runtime_core.py` 内 production）；② 门面只做协议适配+路由分发，大脑的编排职责（boot 序列、降级链、健康监控）与门面正交；③ 取代=重写 production 代码，违反 §3.3 的「扩展不重写」。对齐动作：10 号文 Phase 1 的 `llm_runtime_gateway` 落地后，大脑的 LLM 调用点（DeepSeekChat/EmbeddingRouter/LocalModelScheduler 消费处）改经门面入口——该改动列为本文 Phase 1 的联动步骤 1.4，不新建模块。

### 3.5 与 07 号文（Context Engine）的接口对齐

07 号文 v0.2.2 已填充，其 §6 Q2 假设：「AutoRuntime 经 EventBus 调度 context_pipeline_auto，任务启动时触发四段流水线」。

**本文按实测将该假设精确化**：`autonomy_core/context/context_pipeline_auto.py`（production）的 `auto_start()` 在系统启动时初始化 ContextPipeline 并注册 EventBus 订阅（`zephyr.shared.event_bus`），其模块头消费者清单含 `zephyr.trading.boot_hooks`——即大脑在 boot 阶段经 `boot_hooks.py` 触发其自动注册，此后流水线由 EventBus 事件驱动。大脑的角色是 **boot 触发方 + 事件驱动订阅源**，不逐任务编排四段流水线；蓝图 references 声明的「MOD-CONTEXT_ENGINE——大脑消费上下文注入」成立，大脑不向 Context Engine 反向输出编排职责；`autonomy_core/context/` 子系统（39 个文件已 production）的剩余施工归 07 号文。双向确认动作已登记 §6 Q5。

### 3.6 自治层不变量与契约（设计态登记）

> 真源：depgraph 草稿 `.runtime/aidrafts/09_drafts_audit/依赖图/project-entity-depgraph.yaml` 的 invariants/events/contracts 段 + `01-跨域交叉点与因果链.md` D-AUTONOMY 模块表。depgraph 域模型中 D-AUTONOMY-CORE 对应系统大脑运行时（layer_domain_mapping L01），D-AUTONOMY-PERM 为自治保护层。本节为**设计态登记**——登记自治层三件套作为大脑施工的约束基线，不变量落地与事件/契约的代码实现归属 §4 Phase 1+ 各触发式阶段，不在 Phase 0 超前施工。

**A. 自治不变量 INV-AU-001~008（8 项）**

| 编号 | 名称 | 内容 | owner_domain | 执行点 | 违反动作 |
|---|---|---|---|---|---|
| INV-AU-001 | PERM 不改 CORE 状态 | PERM 只能读取 CORE 状态 + 发出阻止指令，不能修改 CORE 任何状态 | D-AUTONOMY-PERM | compile_time | block |
| INV-AU-002 | PERM 预算豁免 | PERM 自身不受 budget 限制，防止死锁——PERM 扣光 budget 就无法阻止 CORE | D-AUTONOMY-PERM | runtime | alert |
| INV-AU-003 | KillSwitch 直通不经 CORE | Kill Switch 直通路径不经过 CORE，不能被 CORE 拦截 | D-AUTONOMY-PERM | architecture | block |
| INV-AU-004 | 交易时段仅监控 | 交易时段 PERM 仅做监控+告警，修复操作延至盘后 | D-AUTONOMY-PERM | runtime | alert |
| INV-AU-005 | 决策可解释性 | 每笔 AI 自主决策必须有完整的决策溯源链 | D-AUTONOMY-CORE | runtime | block |
| INV-AU-006 | AI 自主执行率阈值 | AI 自主执行率目标 >90%，单笔自主执行置信度 ≥95% | D-AUTONOMY-CORE | runtime | alert |
| INV-AU-007 | 参数安全边界 | 参数变化幅度 ±20%/次，性能回撤 >5% 回滚，OOS 必须优于 IS | D-AUTONOMY-CORE | runtime | block |
| INV-AU-008 | 能力只经 CapabilityCard 发现 | 自治域不依赖任何业务域实现细节，只通过 CapabilityCard 发现能力 | D-AUTONOMY-CORE | architecture | block |

与本文既有决策的关系：INV-AU-004 与 §2.3「交易时段大脑降载」同向（盘中仅监控，动作延盘后）；INV-AU-008 是 L2 执行层 `capability_card.py`/`capability_registry.py`（已 production）的存在理由——能力发现唯一入口；INV-AU-006 的阈值口径是 §6 之外不再有歧义的量化基线（>90% / ≥95%）。

**B. 自治事件体系 E-AU-01~14 + E-AP 系列（实测 14+4=18 个）**

| 编号 | 事件 | payload 要点 | 源→目标 | 级别 |
|---|---|---|---|---|
| E-AU-01 | KillSwitchActivated | {reason, timestamp, initiator} | CORE→EX-CORE/PERM | P0 |
| E-AU-02 | KillSwitchDeactivated | {timestamp, approver} | CORE→EX-CORE/PERM | P0 |
| E-AU-03 | PermissionDenied | {subject, action, resource, policy_id} | PERM→CORE/OPS | P0 |
| E-AU-04 | BudgetExceeded | {budget_type, current, limit, agent_id} | CORE→PERM/OPS | P1 |
| E-AU-05 | HealthDegraded | {component, score, threshold} | CORE→PERM/OPS | P1 |
| E-AU-06 | DriftDetected | {detector_id, drift_type, magnitude} | PERM→CORE/OPS | P1 |
| E-AU-07 | EscalationTriggered | {reason, level, target_agent} | CORE→PERM/OPS | P1 |
| E-AU-08 | SessionStateChanged | {session_id, old_state, new_state} | CORE→PERM | P1 |
| E-AU-09 | StrategyRetired | {strategy_id, fingerprint_match, retirement_reason}（指纹匹配换名复活触发） | CORE→PERM/PF-CORE | P0 |
| E-AU-10 | AutonomousExecutionRateDegraded | {rate, threshold, duration}（自主执行率 <90% 持续 1 小时触发，INV-AU-006 的事件面） | CORE→PERM/OPS | P0 |
| E-AU-11 | OverfittingDetected | {oos_score, is_score, purge_gap, walk_forward_windows}（OOS<IS 或 Purged K-Fold 泄漏触发，INV-AU-007 的事件面） | CORE→PERM | P1 |
| E-AU-12 | CrowdnessWarning | {factor_id, msci_risk_exposure, a_share_stampede_risk} | CORE→PERM/RISK | P1 |
| E-AU-13 | BlackSwanDetected | {pattern_id, trigger_conditions, historical_occurrences} | CORE→PERM/RISK | P1 |
| E-AU-14 | DecisionTraceBroken | {decision_id, break_point, expected_chain}（溯源链断链，INV-AU-005 的事件面） | CORE→PERM | P0 |
| E-AP-01 | PERMIndependentHealthCheck | {core_reachable, perm_health_score}（PERM 独立健康检查发现 CORE 不可达，GAP-AP-01 的事件面） | PERM→CORE/OPS | P0 |
| E-AP-02 | TradingSessionSwitch | {market, session_type, timestamp}（INV-AU-004 的切换信号） | PERM→CORE | P0 |
| E-AP-05 | KillSwitchDirectActivated | {reason, timestamp, path:direct, issuer:PERM}（直通路径触发，INV-AU-003/GAP-AP-05 的事件面） | PERM→EX-CORE | P0 |
| E-AP-07 | BacktestRealtimeDeviationAlert | {strategy_id, deviation_pct, threshold} | PERM→CORE/RISK | P1 |

编号口径说明：草稿源中 E-AP 系列仅实测到 E-AP-01/02/05/07 四个（E-AP-03/04/06 编号在草稿中不存在），本节按实测登记，不补造跳号。

**C. 自治契约 CTR-AU-001~006 + CTR-AP-001~003（6+3=9 个）**

| 编号 | 契约 | schema | 源→目标 | 稳定性 |
|---|---|---|---|---|
| CTR-AU-001 | TraceContext | {agent_id, session_id, permission_level, audit_chain_hash} | CORE→PERM/INFRA-RUNTIME/INFRA-OPS/SECURITY/INTEGRATION/DATA/FACTOR/SIGNAL/PF-CORE/EX-CORE/RISK/ML-TRAIN/ML-SERVE/REPORTING/OPS | frozen |
| CTR-AU-002 | RBACDecision | {subject, action, resource, verdict, policy_id} | PERM→CORE/INFRA-RUNTIME/DATA/FACTOR/SIGNAL/PF-CORE/EX-CORE/RISK | frozen |
| CTR-AU-003 | AuditRecord | {event_type, actor, action, target, timestamp, merkle_hash} | PERM→COMPLIANCE/REPORTING | frozen |
| CTR-AU-004 | HealthStatus | {component, score, latency_ms, error_rate} | CORE→OPS/INFRA-OPS | frozen |
| CTR-AU-005 | LLMInference | {model_id, prompt_hash, response_hash, token_count, latency_ms} | CORE→ML-TRAIN/ML-SERVE/SIGNAL/REPORTING | frozen |
| CTR-AU-006 | CapabilityCard | {capability_id, version, endpoint, health} | CORE→PERM/INFRA-RUNTIME | frozen |
| CTR-AP-001 | CoreReadOnlyState | CoreState{session_states, agent_status, task_queue_depth, permission_mode}（INV-AU-001 的只读视图载体） | CORE→PERM | evolving |
| CTR-AP-002 | PERMBlockCommand | BlockCommand{target_agent, reason, duration, issuer:PERM, audit_hash}（INV-AU-001 允许的「阻止指令」载体） | PERM→CORE | evolving |
| CTR-AP-003 | PERMBudgetExemption | BudgetExemption{perm_operation_id, exempt:True, justification}（INV-AU-002 的豁免凭证） | PERM→CORE | evolving |

契约与现状代码的映射：CTR-AU-006 已有 `capability_card.py`（production）承载；CTR-AU-004 与 `health_monitor.py` 的健康评分输出同型；CTR-AU-003 与 `ai_audit_logger.py`（GAP-007 环形缓冲待施工）同域；CTR-AP-001/002/003 为 PERM 侧契约，代码归属 D-AUTONOMY-PERM 域施工（不在本文施工范围，本文只登记 CORE 侧消费/生产点）。

---

## 4. 施工计划

> **depgraph L1 铁律（通用规则 19）**：凡涉及新建模块的步骤，第一步用 `python scripts/governance/apply_depgraph.py` 将依赖关系登记到 depgraph 设计态（status=planned），最后一步验证通过后 planned→production。禁止先施工后补登记。本文唯一新建模块 = `brain_admission_controller.py`（Phase 2）。
>
> **施工模式**：扩展（蓝图 §16.1 裁定）——在既有组件上追加规模适配，不重写基线。
>
> **触发式施工原则**：Phase 1/2/3 的启动以蓝图 §17 触发矩阵的真实度量为准（如「全量扫描 >3s」「活跃 DAG >50」），未触发不施工。
>
> **施工顺序注记（depgraph 草稿 activation 段登记）**：D-AUTONOMY-CORE 的就绪前提（readiness_prerequisites，arb_ref=AUT-CORE-READY）为 **D-AUTONOMY-PERM.GAP-AP-01（PERM 独立健康检查就绪）+ D-AUTONOMY-PERM.GAP-AP-05（Kill Switch 直通路径就绪）**——即「PERM 顺序 0 先于 CORE 顺序 1」：PERM 侧两项就绪门禁必须先于 CORE 就绪成立，CORE 的就绪验收不得在 PERM 两项 GAP 未就绪前宣布完成（INV-AU-001/003 的激活时序面；两项 GAP 的施工归属 D-AUTONOMY-PERM 域，不在本文施工范围，本文登记为 CORE 侧就绪的阻塞条件）。域级自治口径：depgraph 草稿为全部域逐域标注 `ai_autonomy` 属性，实测 28 域——24 域 `ai_modifiable`，4 域 `human_gated`（D-RISK / D-COMPLIANCE / D-SECURITY / D-GOVERNANCE），无 `immutable` 域；逐域清单真源在 depgraph 草稿，本文不复制。

### Phase 0：蓝图-代码对齐 + T0 拐点（P0，当前规模即可做）

> 目标：消除幽灵文件引用，让蓝图可施工；落地「始终需要」的 GAP（降级链/RAM 预算/冷启动 SLA）与 T0 三项（缓存/聚合视图/预算）。
> 对应蓝图：§16.3 步骤 1（T0：51→200 模块 / 1→5 AI）。

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 0.1 | **蓝图对齐修复登记**：将 §2.2 问题 1 的 5 个漂移项（circadian_scheduler.py 无实体文件 / health-monitor.py→health_monitor.py / feedback_loop.py→独立包 / boot_cron_jobs.py→boot_hooks.py / §16.3·§16.5 产出位置与测试目录 runtime→trading）提交蓝图维护方修订 blueprint §0.1/§16（蓝图只读，本文不代改，走 §6 Q3 裁定流程） | 漂移项全部有裁定结论；施工图内引用与磁盘一致（本文已一致） |
| 0.2 | CapabilityRegistry 内存缓存 + 读写锁（GAP-006 配套，蓝图 §16.3 步骤 1） | 缓存命中率 >95%；`python -m pytest tests/trading/ -k capability_registry -v` 通过 |
| 0.3 | StatusDashboard 聚合视图 + 下钻 | 聚合视图可用；降级 Lv1 时降采样生效 |
| 0.4 | StopGate session 预算参数 | 预算超限阻断有单测 |
| 0.5 | 四级降级链落地（GAP-009，蓝图 §3.3 状态机）：CPU>75%/MEM>70%→Lv1 降采样；>85%/80%→Lv2 纯增量+降频 30s；>95%/90%→Lv3 拒非 P0 DAG+仅心跳+通知 Owner | 人工压测触发 Lv1/Lv2/Lv3 各一次，状态迁移与蓝图 §3.3 表一致 |
| 0.6 | 大脑 RAM 预算（GAP-006）：`max_brain_memory_mb`（2GB，D-INF035-08）写入 runtime_config + 超限触发降级 | 超限注入测试通过 |
| 0.7 | 冷启动/崩溃恢复 SLA（GAP-010）：`boot_timeout_ms`/`recovery_timeout_ms` 参数化，boot P99 <10s（D-INF035-09） | `python scripts/construction/start_brain.py --once` 连跑 20 次，boot 耗时 P99 <10s |

**Phase 0 出口**：蓝图 §16.5 完成标准逐项核对（capability_registry/work_orchestrator/health_monitor/dream_cycle 存在且内容非空——四者已存在，按对齐后文件名核对）。

### Phase 1：T1 拐点（P1，触发式启动）

> 启动条件（蓝图 §17 触发矩阵口径，实测为准）：模块数 >200，或 ModuleOnboardingScanner 全量扫描 >3s，或 AI 并发 >5。未触发不施工。
> 对应蓝图：§16.3 步骤 2（T1：200→500 模块 / 5→20 AI）。

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 1.1 | ModuleOnboardingScanner 增量 diff 模式 + 自动注册 API（GAP-003） | 增量 diff <3s；漏检时回退全量扫描（蓝图 §16.4 回滚 2） |
| 1.2 | HealthMonitor 分层检查频率（核心模块 30s / 其他 5min）+ 异常触发深检（GAP-001 配套；落在实测文件 `health_monitor.py`） | 分层频率配置生效；异常注入触发深检有单测 |
| 1.3 | MAPE-K 事件驱动 Monitor + 兜底轮询（GAP-001，D-INF035-02）+ 大脑自观测 SLI（GAP-005） | 事件驱动生效且兜底轮询保留；`mape_k_loop_latency_ms` 等 SLI 可查询 |
| 1.4 | 【联动 10 号文】`llm_runtime_gateway` 门面落地后，大脑的 LLM 调用点（DeepSeekChat/EmbeddingRouter/LocalModelScheduler 消费处）改经门面入口（§3.4；不新建模块） | 调用点切换后 `tests/automation/test_auto_runtime_core.py` 全绿 |
| 1.5 | GPU 时间分片 + VRAM 硬分区参数落地 runtime_config（GAP-004，D-INF035-04；不建独立 GPU 调度器） | 分区参数生效；显存超限场景与降级链联动有测试 |

**Phase 1 出口**：蓝图 §16.3 步骤 2 验收（增量 diff <3s；核心 30s/其他 5min 分层生效；事件驱动生效）。

### Phase 2：T2 拐点（P2，触发式启动）

> 启动条件：活跃 DAG >50，或 AI 并发 >20。未触发不施工。
> 对应蓝图：§16.3 步骤 3（T2：500→1,000 模块 / 20→50 AI）。本文唯一新建模块在本 Phase，严格执行 depgraph L1 铁律。

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 2.1 | **depgraph L1 铁律·第一步**：用 `python scripts/governance/apply_depgraph.py` 将 `brain_admission_controller`（GAP-008 全局准入）登记到 depgraph 设计态（status=planned），依赖边按蓝图 §10/§17；与 MOD-INF-033 的 `admission_controller.py`（行为审计准入）显式区分，禁止混名复用 | depgraph 查询可见 planned 节点与依赖边 |
| 2.2 | WorkOrchestrator WIP 池 + session 配额 + 饥饿防护（GAP-002） | 公平调度生效；饥饿防护超时有单测；死锁时回退无限制提交（蓝图 §16.4 回滚 3） |
| 2.3 | DreamCycle 轮转策略 + 窗口溢出截断——蓝图步骤 3 原挂在幽灵文件 `circadian_scheduler.py` 名下，实际承载文件以 Phase 0 步骤 0.1 裁定结论为准（候选：`dream_cycle.py`/`night_shift_queue.py`），不复活幽灵文件（§6 Q4） | 轮转策略生效；窗口溢出截断有测试 |
| 2.4 | 新建 `brain_admission_controller.py`（GAP-008 全局准入，组件交互组合态分析） | 全局准入决策有单测；与四级降级链联动测试通过 |
| 2.5 | AiAuditLogger 环形缓冲 + 批量 flush（GAP-007，D-INF035-07） | 并发 append 无文件锁排队退化；flush 批量大小可配 |
| 2.6 | **depgraph L1 铁律·最后一步**：步骤 2.4 全部验收通过后，`brain_admission_controller` 状态 planned→production | depgraph 查询 status=production |

**Phase 2 出口**：蓝图 §16.3 步骤 3 验收（WIP 池 + 公平调度生效；无饥饿任务）。

### Phase 3：T3 拐点（P3，触发式启动）

> 启动条件：DreamCycle 夜间窗口溢出，或模块数 >1,000。未触发不施工。
> 对应蓝图：§16.3 步骤 4（T3：1,000→1,500 模块 / 50→100 AI）。

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 3.1 | DreamCycle 分层固化优先级 + 知识老化 + 去重 | 固化优先级配置生效；固化在夜间窗口内完成（溢出则截断并标记未完成，蓝图 §16.4 回滚 4） |
| 3.2 | runtime_config 全量参数调优对齐 1,500 模块容量 | 增量扫描 <1min；全量周检 <75min |
| 3.3 | 边界确认：GAP-011（Agent Spec 语义路由）/ GAP-012（AGENTS.md 分层索引）由 MOD-INF-019 承接（D-INF035-10），本文只做消费侧接口核对，不施工 | 接口核对记录落档 |

**Phase 3 出口**：蓝图 §16.3 步骤 4 验收（分层固化生效；全量参数对齐 1,500）。

### 全程回滚与测试基线

- **回滚**：各 Phase 故障回退以蓝图 §16.4 回滚方案为准（禁内存缓存 / 回全量扫描 / 禁 WIP 限制 / 固化推迟次日窗口）。
- **测试基线**：现有 `tests/automation/test_auto_runtime_core.py`、`test_auto_runtime_e2e.py`、`test_auto_runtime_fle_integration.py`、`tests/trading/test_work_orchestrator.py` 必须全程保持绿色；新增测试按实测落位 `tests/trading/` 或 `tests/automation/`（蓝图所写的 `tests/runtime/` 不存在，见 §2.2 问题 1）。

---

## 5. 不做什么

1. **不做分布式运行时/集群/K8s**——system_charter §2 约束二（单机 PC 无集群）；大脑单进程架构（D-INF035-01），I/O 并发用 ThreadPoolExecutor 承载。
2. **不做热备/故障转移**——RTO<5 分钟由 L0 自举层重启 + 四级降级链 Lv0~Lv3 满足（D-INF035-05），不建 standby 实例。
3. **不与交易决策侧业务逻辑耦合**——大脑只做全项目模块的运行时治理；盘中 tick→因子数据流归 MOD-RUNTIME_INTRADAY（§3.3），策略/信号/下单逻辑归交易决策侧，均不在本文范围。
4. **不重写基线 24 组件**——施工模式为扩展（蓝图 §16.1），禁止以容量升级为借口重写 production 代码。
5. **不建独立 GPU 调度器**——GAP-004 以 runtime_config 参数（时间分片 + VRAM 硬分区，D-INF035-04）落地；现有 `gpu_consensus_scheduler.py` 属交易域与推理的显存协调，不改造。
6. **不承接 GAP-011/012**——Agent Spec 语义路由与 AGENTS.md 分层索引由 MOD-INF-019 承接（D-INF035-10），本文只核对消费侧接口。
7. **不做无触发的超前容量施工**——1,500 模块 / 100 AI 并发是远期容量愿景（§3.1 决策 6），Phase 1/2/3 严格按触发矩阵实测阈值启动；1 人维护不建过剩产能。
8. **不复活幽灵文件**——不新建 `circadian_scheduler.py`/`health-monitor.py`/`boot_cron_jobs.py` 实体文件；蓝图漂移项走 §6 Q3 裁定修订蓝图，而非让代码迁就蓝图。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|---|---|---|
| Q1 | 五层同心圆的施工顺序 | ✅ 已闭环 | 基线 24 组件全部 production，真正的顺序问题是 12 项容量 GAP 的落地顺序——采纳蓝图四拐点触发式推进（§2.2 问题 3、§3.1 决策 3） |
| Q2 | 与 `src/zephyr/runtime/` 既有运行时的关系 | ✅ 已闭环 | 实测裁定为不同物（§3.3）：在现有代码上扩展，不重写、不合并 |
| Q3 | 蓝图-代码漂移 5 项的修订 | 待蓝图维护方/Owner 裁定 | §2.2 问题 1 的 5 项漂移（4 个幽灵文件条目 + §16 产出位置/测试目录 runtime→trading）；蓝图只读，本文不代改；Phase 0 步骤 0.1 跟踪 |
| Q4 | T2「DreamCycle 轮转策略」的承载文件 | 待裁定（依赖 Q3） | 蓝图 §16.3 步骤 3 挂在幽灵文件 `circadian_scheduler.py` 名下；候选承载 `dream_cycle.py`/`night_shift_queue.py`；裁定前 Phase 2 步骤 2.3 不开工 |
| Q5 | 与 07 号文（Context Engine）接口双向确认 | ✅ 已闭环（判定：部分成立） | 接口复审判定：07 号文 §6 Q2 假设「AutoRuntime 经 EventBus 调度 context_pipeline_auto，任务启动时触发四段流水线」**部分成立**——EventBus 事件驱动成立，「逐任务调度」不成立；以本文 §3.5 实测精确化口径为准（boot 阶段经 boot_hooks.py 触发注册，此后 EventBus 事件驱动，大脑不逐任务编排四段流水线） |
| Q6 | 与 10 号文（LLM 基础设施）接口闭环 | ✅ 已闭环（判定：成立） | 接口复审判定：10 号文 §6 Q3 假设「AutoRuntime Core 继续承担 Ollama 进程管理与本地模型栈 boot；llm_runtime_gateway 门面被 AutoRuntime Core 消费而非取代其编排职责」**成立**（本文 §3.4 确认）；联动动作列入 Phase 1 步骤 1.4 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.2.0 | 骨架填充：§1 主题组 + §2 背景（含已施工设施实测盘点）+ §3 设计决策 + §4 Phase 0 | AI-FILL-04 首轮填充（会话中断，留存半成品） |
| 2026-08-17 | 0.2.1 | 续写补完 §4 Phase 1~3 + §5 不做什么 + §6 开放问题 + 修订记录；过渡表述合规改写（GOV-DOC-016：运行模式行/漂移项/deprecated 行改当前状态描述）；实测修正 passports 10→7、07/10 号文版本与接口状态；漂移项 4→5（补 §16 产出位置与测试目录漂移） | AI-FILL-04 续写补完 |
| 2026-08-17 | 0.2.2 | 回填 §3.6 自治层不变量与契约（设计态登记：INV-AU-001~008 / E-AU-01~14+E-AP 实测 4 个 / CTR-AU-001~006+CTR-AP-001~003，真源 depgraph 草稿 invariants/events/contracts 段）；§4 增施工顺序注记（GAP-AP-01/05 就绪门禁「PERM 顺序 0 先于 CORE 顺序 1」+ 域级 ai_autonomy 实测 28 域口径）；§6 Q5/Q6 接口复审判定回填并闭环（Q5 部分成立 / Q6 成立） | AI-FILL-04-R2 回填 |