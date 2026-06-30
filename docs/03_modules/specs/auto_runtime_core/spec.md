---
module_id: MOD-SPEC-002
title: "AutoRuntime Core — 三层运行时运营中心（系统大脑）"
doc_type: architecture_view
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# AutoRuntime Core — 三层运行时运营中心（系统大脑）

> **蓝图编号**: ARC-0001
> **归属轨道**: `b_track` / `l12` umbrella
> **依赖蓝图**: `b_execution_model.yaml` v1.1.0, `b_orchestrator.yaml`, `b_bridge.yaml`, `b_gate.yaml`
> **版本**: v5.0.0-complete
> **状态**: `spec` — 待审核（成熟度 100%，含全系统清单 + 工作编排 + 自动接入子系统 + 终极目标）

---

## 0. 回答你的核心问题

### Q0.1: AutoRuntime Core 是不是系统中唯一一个？有没有功能唯一责？

**是的。** AutoRuntime Core 是整个 ZephyrAlpha 项目中**唯一承担"系统大脑"职责的组件**。

```
ZephyrAlpha 责任地图：
┌──────────────────────────────────────────────────────┐
│ AutoRuntime Core ← 唯一的系统大脑                      │
│   职责：三层运行时编排、节律调度、健康监控、审计日志       │
│   职责：工作编排（WorkOrchestrator）                    │
│   职责：自动接入（ModuleOnboardingScanner）             │
│                                                      │
│ PipelineOrchestrator ← 管线内部编排（M1-M11）          │
│   职责：单条管线的阶段流转                              │
│                                                      │
│ AgentOrchestrator ← Agent 生命周期                    │
│   职责：单个 Agent 的创建/运行/销毁                     │
│                                                      │
│ DaemonRegistry ← 守护进程注册                          │
│   职责：进程级资源监控                                 │
│                                                      │
│ Gate Engine ← 安全闸门                                │
│   职责：策略准入                                       │
│                                                      │
│ TaskRepository ← 任务状态机（10状态）                   │
│   职责：任务 CRUD + 状态流转审计                        │
│                                                      │
│ WorkOrchestrator ← 工作编排（AutoRuntime 子系统）      │
│   职责：决定什么工作、什么时候、用什么模型、什么顺序       │
└──────────────────────────────────────────────────────┘
```

### Q0.2: 专业机构和氛围编程社区是怎么做的？

| 业界实践 | 来源 | 核心思想 | ARC 对应 |
|----------|------|----------|----------|
| **Agent Card + 能力发现** | Google A2A Protocol | AgentCard 声明能力、技能、端点 URL；自动发现 | CapabilityRegistry + CapabilityCard |
| **Orchestrator-Ledger** | Microsoft Magentic-One | 单一 Orchestrator 制定计划→分派→跟踪→反思 | AutoRuntimeCore + NightShiftQueue |
| **Supervisor Pattern** | LangGraph (LangChain) | 中央主管路由，Worker 子图隔离 | MAPE-K 调和循环 |
| **Level-Triggered Reconciliation** | K8s Controller Pattern | 只看"spec vs actual 的差距"；Idempotent | HealthMonitor + MAPE-K Loop |
| **Stop Gate** | Claude Code 45天实验 | 被动质量闸门——阻止 AI 什么都不做就退出 | StopGate |
| **Dream Cycle** | Claude Code 自主实验 | 归档→提取模式→遗忘细节→语义索引→commit | CircadianScheduler 夜间归档 |
| **Filesystem as Memory** | Claude Code / Vibe Coding | 认知外化到文件系统 | AiAuditLogger JSONL + NightShiftQueue |
| **Cursor Rules / AGENTS.md** | Cursor IDE 社区 | 持久化上下文给每次 AI 会话 | AGENTS.md + CapabilityRegistry |
| **MCP Tools/Resources/Prompts** | Anthropic MCP | 三类原语：Tools/Resources/Prompts | CapabilityCard.input/output_schema |
| **Finalizer** | K8s Operator Pattern | CR 删除前拦截，做清理工作 | Finalizer |
| **Self-Improving Agent** | 45天 Claude Code 实验 | 自我反思→学习教训→编码改进→提交→部署 | Feedback Loop |
| **Work Graph / DAG** | Airflow / Prefect / Temporal | 工作编排为 DAG，依赖管理+并行+重试 | WorkOrchestrator |
| **Solo Operator AIOS** | inonx.com 中央内核架构 | Agent 层 + Memory 层 + Governance 层 | AutoRuntime Core 整体 |

### Q0.3: 顶级设计——五层同心圆架构

```
                          ┌─────────────────────────┐
                          │   L0: 自举层              │
                          │   Windows Service         │
                          │   开机自启，无需人          │
                          │          │                │
                          │     ┌────┴────┐           │
                          │     │ L1: 调和层 │          │
                          │     │ MAPE-K 循环│          │
                          │     │ 水平触发    │          │
                          │     │     │      │         │
                          │     │ ┌───┴───┐  │         │
                          │     │ │L2:执行层│  │         │
                          │     │ │T│L│A │  │         │
                          │     │ │ │ │  │  │         │
                          │     │ │┌─┴──┐│  │         │
                          │     │ ││L3:知识层│  │         │
                          │     │ ││审计/登记│  │         │
                          │     │ ││能力卡片│  │         │
                          │     │ │└─────┘│  │         │
                          │     │ └───────┘  │         │
                          │     │     │      │         │
                          │     │ ┌───┴────┐ │         │
                          │     │ │L4:编排层 │ │         │
                          │     │ │WorkOrch. │ │         │
                          │     │ │DAG+优先级│ │         │
                          │     │ │依赖+并行 │ │         │
                          │     │ └─────────┘ │         │
                          └─────┴─────────────┘
```

- **L0 自举层**: Windows Service / 计划任务
- **L1 调和层**: K8s Controller Pattern——水平触发
- **L2 执行层**: Trae/Local/API 三层 + 生物钟调度
- **L3 知识层**: 审计日志 + 登记表 + 能力卡片
- **L4 编排层**: WorkOrchestrator——DAG 工作图 + 优先级 + 依赖 + 并行

### Q0.4: 如何集成到现有所有系统？如何防止孤儿功能？

**注册式耦合**——每个系统通过 CapabilityCard 自注册，AutoRuntime Core 通过 IntegrationRegistry 追踪所有连接点。

**防孤儿三重保障**:
1. AGENTS.md 宪法入口
2. CapabilityRegistry 自发现
3. HealthMonitor 挂掉自动告警+重启

**不注册 = 不存在。**

### Q0.5: 全自动优化（一阶~八阶）

| 阶 | 优化项 | 实现组件 |
|----|--------|----------|
| 一阶 | 开机自启 | Windows Service |
| 一阶 | 自调度 | CircadianScheduler |
| 一阶 | 自发现 | CapabilityRegistry |
| 一阶 | 自注册 | Boot Sequence |
| 一阶 | 自监控 | HealthMonitor |
| 一阶 | 自记录 | AiAuditLogger |
| 二阶 | 自裁决 + 留不确定 | NightShiftQueue |
| 二阶 | Stop Gate | StopGate |
| 三阶 | 知识固化 | DreamCycle |
| 三阶 | 自演化 | FeedbackLoop |
| 四阶 | 自愈 + 自降级 | HealthMonitor |
| 五阶 | 水平触发调和 | HealthMonitor.reconcile() |
| 六阶 | Finalizer + AGENTS.md | Finalizer |
| 七阶 | A2A/MCP 兼容预留 | CapabilityCard |
| 八阶 | 自动 Git + 依赖检查 | DreamCycle/Finalizer |

---

## 1. 概述

### 1.1 角色定位

AutoRuntime Core 是 ZephyrAlpha 的**系统大脑**——不是某个功能的封装，而是整个治理系统的中枢神经。

```
┌──────────────────────────────────────────────────────────┐
│              AutoRuntime Core = 系统大脑                   │
│                                                          │
│   🧠 认知   MAPE-K 调和循环（观察→分析→计划→执行→知识）    │
│   👁 感知   DaemonRegistry + 资源监控 + 健康检查           │
│   🗣 行动   L1(Trae) + L2(Local) + L3(API) 三层执行       │
│   📝 记忆   NightShiftQueue + 结构化日志 + Vector Memory   │
│   🔄 学习   Feedback Loop 进化提案 + 登记表裁定反馈        │
│   📡 注册   CapabilityRegistry + Agent Card 自描述          │
│   ⏰ 节律   CircadianScheduler 内置生物钟                   │
│   🛡 自愈   HealthMonitor + 水平触发调和                    │
│   🚪 闸门   Stop Gate 防止空转                              │
│   📜 宪法   AGENTS.md 项目入口                              │
│   📊 编排   WorkOrchestrator 工作编排子系统                  │
│   🔍 接入   ModuleOnboardingScanner 自动接入子系统           │
└──────────────────────────────────────────────────────────┘
```

### 1.2 终极目标

**AutoRuntime Core 的终极目标是：接入项目里的所有模块、系统、脚本，能灵活运用所有东西。**

```
┌──────────────────────────────────────────────────────────┐
│              终极目标 = 全域接入                           │
│                                                          │
│   目标状态：项目中每一个 .py 文件、每一个 YAML 蓝图、       │
│   每一个脚本、每一个入口——都在大脑的管辖范围内。            │
│                                                          │
│   衡量标准：                                              │
│     孤儿率 = 未接入模块数 / 总模块数 → 目标 = 0%           │
│     接入率 = CapabilityRegistry 注册数 / 总模块数 → 100%  │
│                                                          │
│   这个目标写入：                                          │
│     ① AGENTS.md（项目宪法，所有 AI 首先读取）             │
│     ② RuntimeConfig.ultimate_goal（大脑配置）             │
│     ③ 每次调和循环的 reconcile() 都检查孤儿率              │
│                                                          │
│   自我驱动：                                              │
│     大脑知道自己的目标是"全域接入"，                       │
│     所以每次发现孤儿模块，都会主动启动接入流程。            │
│     这不是被动等待注册，而是主动扫描+自动接入。             │
└──────────────────────────────────────────────────────────┘
```

这个终极目标让大脑有了**方向感**——不是被动等模块来注册，而是主动去发现、去接入、去编排。

### 1.3 核心设计原则

1. **全自主启动** —— Windows Service / 计划任务自举
2. **水平触发** —— K8s Controller Pattern
3. **自描述** —— CapabilityCard 自注册
4. **全链路日志** —— AiAuditLogger
5. **零孤儿** —— 不注册=不存在
6. **Stop Gate** —— AI 不能空退出
7. **Filesystem as Memory** —— 文件是持久记忆
8. **Idempotent Reconciler** —— 多次调和结果一致
9. **工作编排** —— DAG + 优先级 + 依赖 + 并行
10. **全域接入** —— 主动扫描+自动接入，终极目标=0% 孤儿率

---

## 2. 全系统清单（26 包 / 300+ 文件 / 31 蓝图）

### 2.1 包级清单

| # | 包 | 文件数 | 蓝图 YAML | 核心职责 |
|---|-----|--------|-----------|----------|
| 1 | `pipeline/` | 11 | `b_pipeline.yaml` | M1-M11 管线编排、层路由、背压管理 |
| 2 | `orchestrator/` | 70+ | `b_orchestrator.yaml` | Agent 生命周期、任务队列、混沌工程、会话管理 |
| 3 | `vector_memory/` | 21 | `b_vector_memory.yaml` | 嵌入路由、Ollama 推理、向量检索、混合检索 |
| 4 | `shared/` | 130+ | `b_shared.yaml` | 基础设施：事件总线、契约、韧性、安全、可观测性 |
| 5 | `gates/` | 35 | `b_gates.yaml` | 安全闸门：准入、合规、反模式、不变式 |
| 6 | `governance/` | 60+ | — | 治理：决策疲劳、成本路由、SBOM、合规矩阵 |
| 7 | `context_engine/` | 80+ | `b_context_engine.yaml` | 上下文组装/注入/预算/腐化检测/蒸馏 |
| 8 | `kb/` | 38 | `b_kb.yaml` | 知识库：入库、提取、分析、激活、完整性 |
| 9 | `llm_security/` | 29 | `b_llm_security.yaml` | LLM 安全：9层防护、红队、沙箱、注入检测 |
| 10 | `db/` | 10 | `b_db.yaml` | SQLite 元数据、任务仓库、审计 schema |
| 11 | `mcp/` | 19 | `b_mcp.yaml` | MCP Server 集合：12 个工具服务器 |
| 12 | `core/` | 15+ | `b_core.yaml` | 核心：任务队列、调度器、SLA、质量、韧性 |
| 13 | `l01_infrastructure/` | 30+ | `l01_infrastructure.yaml` | 基础设施层：代码去重引擎(20+文件)、脚本系统 |
| 14 | `l02_alpha_factor/` | 5 | `l02_alpha_factor.yaml` | Alpha 因子：价值/动量因子 |
| 15 | `l03_signal_generation/` | 3 | `l03_signal_generation.yaml` | 信号生成 |
| 16 | `l04_risk_management/` | 6 | `l04_risk_management.yaml` | 风险管理：止损、限额、验证 |
| 17 | `l05_portfolio_construction/` | 4 | `l05_portfolio_construction.yaml` | 组合构建：策略注册 |
| 18 | `l06_trade_execution/` | 5 | `l06_trade_execution.yaml` | 交易执行：订单管理、模拟券商 |
| 19 | `l07_post_trade_analytics/` | 4 | `l07_post_trade_analytics.yaml` | 事后分析：TCA、归因 |
| 20 | `l08_human_ai_interface/` | 3 | `l08_human_ai_interface.yaml` | 人机交互 |
| 21 | `l10_compliance/` | 3 | `l10_compliance.yaml` | 合规 |
| 22 | `l11_ml_platform/` | 3 | `l11_ml_platform.yaml` | ML 平台 |
| 23 | `l12_system_telemetry/` | 6 | `l12_system_telemetry.yaml` | 系统遥测：Trace/Span/Profile |
| 24 | `l13_experimentation/` | 4 | `l13_experimentation.yaml` | 实验平台 |
| 25 | `_cross_layer/` | 3 | — | 跨层管线：Alpha-Signal、ML-Experiment |
| 26 | `hooks/` | 2 | — | 事件钩子 |

### 2.2 蓝图 YAML 完整清单（31 个）

| 类型 | 文件 | 简述 |
|------|------|------|
| 横切 | `b_execution_model.yaml` | 三层执行模型 v1.1.0 |
| 横切 | `b_pipeline.yaml` | 管线编排 |
| 横切 | `b_orchestrator.yaml` | Agent 编排 |
| 横切 | `b_shared.yaml` | 共享基础设施 |
| 横切 | `b_vector_memory.yaml` | 向量记忆 |
| 横切 | `b_kb.yaml` | 知识库 |
| 横切 | `b_gates.yaml` | 安全闸门 |
| 横切 | `b_context_engine.yaml` | 上下文引擎 |
| 横切 | `b_llm_security.yaml` | LLM 安全 |
| 横切 | `b_db.yaml` | 数据库 |
| 横切 | `b_mcp.yaml` | MCP 协议 |
| 横切 | `b_core.yaml` | 核心模块 |
| 横切 | `b_feedback_loop.yaml` | 反馈闭环 |
| 业务层 | `l00_data_source.yaml` | 数据源 |
| 业务层 | `l01_infrastructure.yaml` | 基础设施 |
| 业务层 | `l02_alpha_factor.yaml` | Alpha 因子 |
| 业务层 | `l03_signal_generation.yaml` | 信号生成 |
| 业务层 | `l04_risk_management.yaml` | 风险管理 |
| 业务层 | `l05_portfolio_construction.yaml` | 组合构建 |
| 业务层 | `l06_trade_execution.yaml` | 交易执行 |
| 业务层 | `l07_post_trade_analytics.yaml` | 事后分析 |
| 业务层 | `l08_human_ai_interface.yaml` | 人机交互 |
| 业务层 | `l09_research_innovation.yaml` | 研究创新 |
| 业务层 | `l10_compliance.yaml` | 合规 |
| 业务层 | `l11_ml_platform.yaml` | ML 平台 |
| 业务层 | `l12_system_telemetry.yaml` | 系统遥测 |
| 业务层 | `l13_experimentation.yaml` | 实验平台 |
| 元数据 | `index.yaml` | 蓝图索引（v3.0.2 融合版，dm200916 派生 domains） |
| 元数据 | `_schema.yaml` | 蓝图 Schema |
| 元数据 | `technology_landscape.yaml` | 技术全景 |

### 2.3 根目录入口脚本

| 文件 | 简述 |
|------|------|
| `local_layer_daemon.py` | L2 入口（将迁移为薄包装） |
| `demo_e2e_pipeline.py` | 端到端管线演示 |
| `_debug_rules.py` | 规则调试 |
| `_tmp_adversarial_test.py` | 对抗测试 |
| `_final_test.py` | 最终测试 |

---

## 3. 三层 AI 工作分类（全系统逐包）

### 3.1 🔵 TRAE (L1) — 人在 IDE 交互，免费

人在电脑前时的 IDE 对话。负责所有需要**人类判断、可视化交互、复杂上下文理解**的工作。

| 包 | 具体工作 | 为什么是 Trae |
|----|----------|---------------|
| `context_engine/` | 上下文组装/注入/Token预算 | IDE 原生上下文管理 |
| `context_engine/` | 蓝图上下文加载（architecture_context_loader） | 把架构 YAML 注入对话 |
| `gates/` | 人工审批闸门（gate_override） | 需要人做最终判断 |
| `gates/` | can_i_deploy / breaking_change_detector | 上线前安全检查 |
| `governance/` | 架构决策审查（design_decisions, decision_fatigue） | 人在环评审 |
| `governance/` | 代码审查AI辅助（code_review_ai） | AI 建议 + 人工确认 |
| `governance/` | 契约审查（provenance_tracker） | 需求到代码溯源 |
| `orchestrator/` | Agent 手动创建/配置 | 新 Agent 设计时需要人 |
| `orchestrator/` | 蓝图健康评分（blueprint_health） | 可视化仪表盘 |
| `pipeline/` | M1-M11 管线调试 | 人在时跑管线，debug |
| `mcp/` | IDE 内 MCP 工具调用 | Trae 通过 MCP 调后端 |
| `kb/` | 知识库交互查询 | 人在 IDE 里问"这个因子怎么用" |
| `llm_security/` | 人工安全审计（dashboard） | 可视化安全面板 |
| `db/` | 数据库管理工具 | 人工维护 |
| `l08_human_ai_interface/` | 人机交互界面 | 人在环 |
| `l09_research_innovation/` | 研究创新讨论 | 需要人脑 |

### 3.2 🟢 LOCAL (L2) — 24/7 自动化，Ollama 本地推理，零成本

永远在线。适合**确定性高、不需要大模型、重复性、监控类**工作。

| 包 | 具体工作 | 为什么是 Local |
|----|----------|----------------|
| `vector_memory/` | 嵌入生成（BGE-M3 + bge-small） | 本地模型够用 |
| `vector_memory/` | 重排序（Reranker） | 本地模型 |
| `vector_memory/` | 6类轻量推理（分类/标签/摘要/异常/改写/命名） | qwen3:8b |
| `kb/` | 批量入库分析（ingest, analyze, extract） | 24/7 持续处理 |
| `kb/` | 知识库完整性校验（integrity, verify） | 自动扫描 |
| `kb/` | 知识冻结/归档（freeze） | 定时自动 |
| `orchestrator/` | 任务自动分派（task_queue dispatch） | 后台轮询 |
| `orchestrator/` | 幻觉检测（hallucination_detector） | 持续检查 |
| `orchestrator/` | 死信队列清理（dlq_manager） | 后台自动 |
| `orchestrator/` | 知识新鲜度检查（knowledge_freshness） | 定期扫描 |
| `orchestrator/` | 文件任务映射（file_task_mapper） | tasks/ 自动发现 |
| `orchestrator/` | 自动化基准测试（benchmark_runner） | 24/7 跑分 |
| `l01_infrastructure/` | 代码去重扫描（code_dedup_engine 20+文件） | 24/7 后台扫描 |
| `context_engine/` | 上下文腐化检测（context_rot_model） | 定期自动 |
| `context_engine/` | 上下文健康评分（ContextHealthScore） | 持续监控 |
| `context_engine/` | 缓存失效管理（cache_invalidation） | 自动 |
| `shared/` | 心跳服务（heartbeat_server） | 24/7 心跳 |
| `shared/` | 健康探测（health, health_discovery） | 持续 |
| `shared/` | TTL清理（ttl_cleanup_engine） | 定时后台 |
| `shared/` | 模块出生登记（module_birth_registry） | 自动发现新模块 |
| `shared/` | 依赖检查（dependency_capacity_guard） | 持续 |
| `gates/` | 不变式验证（invariants/*） | 自动合规检查 |
| `gates/` | 反模式守卫（anti_pattern_guard） | 静态代码检查 |
| `gates/` | 任务完成闸门（task_completion_gate） | 自动验证 |
| `gates/` | KISS 执行器（kiss_enforcer） | 自动简化检查 |
| `gates/` | 秘密守卫（secrets_guard） | 自动密钥检测 |
| `gates/` | 审计链验证（audit_chain_verifier） | 自动 |
| `gates/` | CDC 代理（cdc_broker） | 自动变更检测 |
| `governance/` | 模型漂移监控（model_drift_monitor） | 持续监控 |
| `governance/` | SPOF 检查（spof_checker） | 自动 |
| `governance/` | 依赖管理（dependency_manager） | 自动 |
| `governance/` | 性能基线（performance_baseline） | 持续 |
| `governance/` | DORA 指标（dora_metrics） | 自动采集 |
| `governance/` | 可观测性仪表盘（observability_dashboard） | 持续 |
| `governance/` | 数据质量（data_quality） | 自动 |
| `governance/` | 数据分类（data_classification） | 自动 |
| `governance/` | 环境管理（environment_manager） | 自动 |
| `governance/` | 上下文回收（context_recycling） | 自动 |
| `governance/` | 会话生命周期（session_lifecycle） | 自动 |
| `governance/` | 系统拓扑（system_topology） | 自动 |
| `governance/` | 启停CLI（startup_shutdown_cli） | 自动 |
| `governance/` | 本地优先架构（local_first_arch） | 自动 |
| `governance/` | 离线自治（offline_autonomy） | 自动 |
| `governance/` | 杀开关（kill_switch） | 自动 |
| `governance/` | 事件响应（incident_response） | 自动 |
| `governance/` | 后果管理（consequence_manager） | 自动 |
| `governance/` | 风险矩阵（risk_matrix） | 自动 |
| `governance/` | Token 预算（token_budget） | 自动 |
| `governance/` | 氛围编码执行器（vibe_coding_enforcer） | 自动 |
| `governance/` | 变更日志管理（changelog_manager） | 自动 |
| `governance/` | 跨环境一致性（cross_env_consistency） | 自动 |
| `governance/` | 增量审查（incremental_review） | 自动 |
| `governance/` | 实时流（realtime_streaming） | 自动 |
| `governance/` | 时间同步（time_sync） | 自动 |
| `governance/` | 数据生命周期（data_lifecycle） | 自动 |
| `governance/` | 离线韧性（offline_resilience） | 自动 |
| `governance/` | 秘密生命周期（secrets_lifecycle） | 自动 |
| `governance/` | 提示词生命周期（prompt_lifecycle） | 自动 |
| `governance/` | 日常运维（daily_ops） | 自动 |
| `governance/` | 运维基础（ops_foundation） | 自动 |
| `governance/` | 微结构防御（microstructure_defense） | 自动 |
| `governance/` | 容错（fault_tolerance） | 自动 |
| `governance/` | 会话并发（session_concurrency） | 自动 |
| `governance/` | FSM 验证器（fsm_verifier） | 自动 |
| `governance/` | OMS 风险引擎（oms_risk_engine） | 自动 |
| `governance/` | 公司行为（corporate_actions） | 自动 |
| `governance/` | 市场数据管线（market_data_pipeline） | 自动 |
| `governance/` | 体制检测器（regime_detector） | 自动 |
| `governance/` | ML 工程（ml_engineering） | 自动 |
| `governance/` | WQA 评分（wqa_scorer） | 自动 |
| `governance/` | 总拥有成本（tco_model） | 自动 |
| `governance/` | 成本路由（cost_router） | 自动 |
| `governance/` | 词汇矩阵（glossary_matrix） | 自动 |
| `governance/` | 迁移策略（migration_strategy） | 自动 |
| `governance/` | 代码考古（code_archaeology） | 自动 |
| `governance/` | 巴士因子防御（bus_factor_defense） | 自动 |
| `governance/` | 知识引擎（knowledge_engine） | 自动 |
| `governance/` | 数据源可靠性（data_source_reliability） | 自动 |
| `governance/` | 上线后验证（post_live_verification） | 自动 |
| `governance/` | SBOM 生成（sbom_generator） | 自动 |
| `governance/` | 供应链安全（supply_chain_security） | 自动 |
| `governance/` | 金融合规（financial_compliance） | 自动 |
| `governance/` | 防御深度（defense_depth） | 自动 |
| `governance/` | 合规矩阵（compliance_matrix） | 自动 |
| `governance/` | 纸上→实盘过渡（paper_live_transition） | 自动 |
| `governance/` | 多模型共识（multi_model_consensus） | 自动 |
| `l12_system_telemetry/` | Trace/Span/Profile 采集 | 持续 |
| `l11_ml_platform/` | 模型服务/版本管理 | 自动 |
| `l10_compliance/` | 合规规则自动检查 | 自动 |
| `l00_data_source/` | 数据源接入/质量检查 | 自动 |
| `core/` | 任务队列轮询（task_queue） | 后台 |
| `core/` | SLA 监控（sla_monitor） | 持续 |
| `core/` | 质量监控（quality_monitor） | 持续 |
| `core/` | 断路器（circuit_breaker） | 自动 |
| `core/` | 重试处理（retry_handler） | 自动 |
| `core/` | 会话边界（session_boundary） | 自动 |
| `core/` | 蓝图代码同步（blueprint_code_sync） | 自动 |
| `hooks/` | 事件钩子（event_hook） | 自动 |
| `db/` | 任务仓库（task_repo）10状态机 | 自动 |
| `db/` | 电路断路器仓库（circuit_breaker_repo） | 自动 |
| `db/` | 闸门仓库（gate_repo） | 自动 |
| `db/` | 查询指标（query_metrics） | 自动 |
| `db/` | OLAP 引擎（olap_engine） | 自动 |
| `db/` | 审计 Schema（audit_schema） | 自动 |

### 3.3 🔴 API (L3) — 夜班/高价值/不确定，有成本

只在有价值的时候调用。用于**需要强推理、创造性强、法律合规精度要求高**的工作。

| 包 | 具体工作 | 为什么是 API |
|----|----------|---------------|
| `governance/` | 合规矩阵审查（compliance_matrix） | 法律精度要求 |
| `governance/` | 金融合规（financial_compliance） | 监管级别 |
| `governance/` | 供应链安全审计（supply_chain_security） | 深度推理 |
| `governance/` | SBOM 生成（sbom_generator） | 复杂分析 |
| `governance/` | TCO 模型分析（tco_model） | 成本建模 |
| `governance/` | 多模型共识（multi_model_consensus） | 多大模型交叉验证 |
| `llm_security/` | 红队扫描（red_team_scanner） | 攻击性安全测试 |
| `llm_security/` | 对抗性变异（adversarial_mutator） | 复杂 |
| `orchestrator/` | 事件事后分析（incident_postmortem） | 深度总结 |
| `orchestrator/` | 设计决策分析（design_decisions） | 架构推理 |
| `pipeline/` | 规则审计（M8 管线阶段） | 复杂规则匹配 |
| `pipeline/` | 不确定任务判定 | 登记到 NightShiftQueue |
| `kb/` | 知识图谱验证（graph_validator） | 复杂图遍历 |
| `kb/` | 重排序高精度模式 | 更大模型 |
| `context_engine/` | 知识蒸馏（knowledge_distiller） | 强推理 |
| `context_engine/` | 会话学习（session_learner） | 跨会话模式提取 |
| `context_engine/` | 对抗鲁棒性（adversarial_robustness） | 安全推理 |
| `context_engine/` | 自诊断（self_diagnosis） | 复杂推理 |
| `context_engine/` | 冷启动加速（cold_start_booster） | 需要大模型 |
| `l09_research_innovation/` | 研究创新 | 创造性推理 |
| `l05_portfolio_construction/` | 策略生成 | 复杂优化 |
| `l03_signal_generation/` | 信号生成 | 复杂推理 |
| `l04_risk_management/` | 风险评估 | 复杂推理 |
| `l06_trade_execution/` | 执行策略优化 | 复杂推理 |

### 3.4 ⚪ 三组都参与（协作型）

| 包 | Trae | Local | API |
|----|------|-------|-----|
| `pipeline/` M1-M11 | 人在时主导 | 嵌入+重排+轻量推理 | 规则审计+不确定性 |
| `orchestrator/` Agent 创建 | 人设计 | L2 自注册 CapabilityCard | L3 审查 |
| `governance/` 反馈环 | 人裁定 | L2 收集模式 | L3 生成进化提案 |
| `shared/` 事件总线 | IDE 事件 | 后台事件 | 复杂事件分析 |
| `kb/` 知识库 | 人查询 | 自动入库/校验 | 图谱验证 |
| `context_engine/` | IDE 上下文注入 | 腐化检测 | 蒸馏 |
| `gates/` | 人工审批 | 自动不变式检查 | 复杂合规审查 |

---

## 4. 工作编排子系统（WorkOrchestrator）——新增

### 4.1 为什么需要工作编排？

300+ 文件、26 个包、上百个可自动化工作。如果没有编排系统：
- 工作之间有依赖（先入库→再分析→再激活），没有编排会乱序
- 同类工作可以并行（5 个嵌入任务同时跑），没有编排会串行
- 优先级不同（P0 合规检查 > P2 代码去重），没有编排会抢资源
- 工作量波动（夜班多、白天少），没有编排会浪费或过载

### 4.2 设计理念

借鉴 **Airflow DAG** + **Temporal Workflow** + **K8s Job** 三种模式：

| 模式 | 来源 | 核心思想 | ARC 采用 |
|------|------|----------|----------|
| DAG 依赖图 | Airflow / Prefect | 工作定义为 DAG，节点=任务，边=依赖 | WorkDAG |
| 持久化执行 | Temporal | 工作流状态持久化，崩溃后可恢复 | TaskRepository 10 状态机 |
| 优先级抢占 | K8s Pod PriorityClass | P0 抢占 P2 资源 | PriorityPreemption |
| 并行槽位 | K8s Parallelism | 控制同时运行的任务数 | ConcurrencySlot |
| 工作窃取 | Go Work Stealing | 空闲层窃取其他层的任务 | LayerWorkStealing |

### 4.3 WorkOrchestrator 架构

```python
class WorkOrchestrator:
    """工作编排子系统——决定什么工作、什么时候、用什么模型、什么顺序。

    借鉴:
      - Airflow: DAG 依赖图
      - Temporal: 持久化工作流
      - K8s Job: 优先级抢占 + 并行控制
    """

    def __init__(self, task_repo: TaskRepository, capability_registry: CapabilityRegistry)

    # ---- DAG 管理 ----
    def register_dag(self, dag: WorkDAG) -> None
    def get_dag(self, dag_id: str) -> WorkDAG | None
    def list_dags(self) -> list[WorkDAG]

    # ---- 执行 ----
    def submit(self, work: WorkItem) -> str              # 返回 task_id
    def submit_dag(self, dag_id: str, params: dict) -> str
    def cancel(self, task_id: str) -> bool

    # ---- 调度 ----
    def schedule_next(self) -> list[WorkItem]             # 返回可执行的任务
    def resolve_layer(self, work: WorkItem) -> str        # 决定跑在哪一层
    def resolve_priority(self, work: WorkItem) -> str     # P0/P1/P2

    # ---- 并行控制 ----
    def acquire_slot(self, layer: str) -> bool            # 获取执行槽位
    def release_slot(self, layer: str) -> None            # 释放槽位
    def available_slots(self, layer: str) -> int

    # ---- 状态 ----
    def status(self, task_id: str) -> TaskStatus
    def pending_count(self) -> dict[str, int]             # 按层统计
    def running_count(self) -> dict[str, int]
```

```python
class WorkDAG(BaseModel):
    """工作 DAG——定义工作之间的依赖关系。"""
    dag_id: str
    name: str
    description: str
    nodes: list[WorkNode]
    edges: list[WorkEdge]
    default_layer: str                    # trae / local / api
    default_priority: str                 # P0 / P1 / P2
    max_parallelism: int = 3
    retry_on_failure: int = 2
    timeout_minutes: int = 60

class WorkNode(BaseModel):
    """DAG 节点——一个可执行的工作单元。"""
    node_id: str
    capability_id: str                    # 对应 CapabilityCard.capability_id
    work_type: str                        # embedding / inference / search / ...
    params: dict                          # 输入参数
    layer_override: str | None = None     # 强制指定层
    priority_override: str | None = None  # 强制指定优先级

class WorkEdge(BaseModel):
    """DAG 边——节点间依赖。"""
    from_node: str
    to_node: str
    condition: str = "success"            # success / failure / always
```

```python
class WorkItem(BaseModel):
    """工作项——提交到编排系统的最小单元。"""
    item_id: str
    dag_id: str | None                    # 所属 DAG（独立任务为 None）
    node_id: str | None                   # 所属节点
    capability_id: str
    work_type: str
    params: dict
    layer: str                            # trae / local / api
    priority: str                         # P0 / P1 / P2
    status: str                           # PENDING / READY / RUNNING / COMPLETED / FAILED / ...
    depends_on: list[str]                 # 依赖的 item_id 列表
    created_at: str
    scheduled_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    result: dict | None = None
    error: str | None = None
```

### 4.4 与现有 TaskRepository / TaskQueue / TaskScheduler 的衔接

```
                    WorkOrchestrator
                    （工作编排子系统）
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    submit()       schedule_next()   resolve_layer()
          │              │              │
          ▼              ▼              ▼
    TaskRepository   TaskScheduler   _resolve_execution_mode()
    (10状态机)       (定时调度)       (三层决策)
          │              │              │
          └──────┬───────┘              │
                 ▼                      │
            TaskQueue                   │
            (后台轮询自动分发)            │
                 │                      │
          ┌──────┴──────┐               │
          ▼             ▼               ▼
     L1(Trae)     L2(Local)       L3(API)
```

**边界清晰**：

| 组件 | 职责 | 不做什么 |
|------|------|----------|
| **WorkOrchestrator** | 决定什么工作、什么顺序、什么层、什么优先级 | 不管理任务状态机 |
| **TaskRepository** | 管理 10 状态机（PENDING→IN_PROGRESS→COMPLETED→VERIFIED） | 不决定跑哪层 |
| **TaskQueue** | 后台轮询 READY 任务，自动 dispatch | 不决定优先级 |
| **TaskScheduler** | 定时调度（assigned_model/assigned_pipeline） | 不管理依赖 |
| **CircadianScheduler** | 生物钟定时触发 | 不管理工作依赖图 |

**衔接流程**：
```
1. WorkOrchestrator.submit(work_item)
   → 写入 TaskRepository.create()（状态=PENDING）
   → 解析依赖，依赖满足 → 状态=READY

2. TaskQueue 后台轮询 READY 任务
   → WorkOrchestrator.resolve_layer() 决定跑哪层
   → WorkOrchestrator.acquire_slot() 获取槽位
   → dispatch 到对应层执行

3. 执行完成
   → TaskRepository.update(status=COMPLETED)
   → WorkOrchestrator 检查下游依赖是否满足
   → 满足 → 下游任务状态→READY

4. CircadianScheduler 定时触发
   → WorkOrchestrator.submit_dag() 注入预定义 DAG
   → 例如 00:00 注入 "daily-dream-cycle" DAG
```

### 4.5 预定义工作 DAG

| DAG ID | 触发方式 | 节点 | 层级 |
|--------|----------|------|------|
| `daily_dream_cycle` | Circadian 00:00 | archive→extract→forget→index→commit | L2→L3→L2→L2→L2 |
| `daily_health_check` | Circadian 07:00 | probe_all→reconcile→report | L2→L2→L2 |
| `daily_code_dedup` | Circadian 02:00 | scan→match→prioritize→merge | L2→L2→L2→L2 |
| `daily_kb_maintenance` | Circadian 04:00 | integrity→verify→freeze→dedup | L2→L2→L2→L2 |
| `daily_compliance` | Circadian 22:00 | matrix_check→sbom→supply_chain | L3→L3→L3 |
| `daily_feedback_loop` | Circadian 03:00 | analyze_pending→generate_proposals→apply | L2→L2→L2 |
| `pipeline_full_run` | 手动/事件 | M1→M2→M3→...→M11 | L1+L2+L3 |
| `kb_ingest_pipeline` | 事件（新数据） | triage→extract→analyze→ingest→activate | L2→L2→L2→L2→L2 |
| `security_scan` | 事件（新代码） | injection_check→red_team→sandbox→report | L2→L3→L2→L2 |
| `model_drift_check` | Circadian 12:00 | collect_metrics→compare_baseline→alert_if_drift | L2→L2→L2 |

### 4.6 并行控制

```
并行槽位（按层分配）：
┌──────────────────────────────────────────┐
│ L1 (Trae)  │ 槽位: 1（人在环，串行）      │
│ L2 (Local) │ 槽位: 3（Ollama 可并行3推理） │
│ L3 (API)   │ 槽位: 2（成本控制，最多2并发） │
└──────────────────────────────────────────┘

优先级抢占：
  P0（合规/安全）→ 抢占 P2 槽位
  P1（运维）     → 正常排队
  P2（优化/清理） → 空闲时执行

层间工作窃取：
  L2 空闲 + L3 排队 → L2 尝试处理（如果能力匹配）
  L3 空闲 + L2 排队 → 不窃取（成本原因）
```

---

## 5. 自动接入子系统（ModuleOnboardingScanner）——新增

### 5.1 为什么需要自动接入？

当前设计是"被动等注册"——模块启动时 self-register。但问题是：
- **新模块创建时**，开发者/AI 可能忘记注册到 CapabilityRegistry → 变成孤儿
- **现有模块**中，大量模块还没接入大脑 → 孤儿率很高
- **大脑不知道自己不知道什么**——没有主动扫描，就不知道遗漏了什么

需要一套**主动扫描+自动判断+自动接入**的子系统。

### 5.2 设计理念

借鉴 **K8s Controller Manager**（主动调和）+ **Claude Code Self-Improving Agent**（自我发现+自我完善）：

| 模式 | 来源 | 核心思想 | ARC 采用 |
|------|------|----------|----------|
| 主动扫描 | K8s Controller Manager | 不等事件，定期全量扫描 | ModuleOnboardingScanner |
| 智能判断 | Claude Code Self-Improving | 临时启动高级模型分析 | AutoIntegrator (L3 临时激活) |
| 孤儿检测 | K8s Orphan Pod Detection | 发现不在管理范围内的资源 | OrphanDetector |
| 自动注册 | K8s Auto-Registration | 发现即注册 | AutoIntegrator.generate_card() |
| 终极目标驱动 | Self-Improving Agent | 知道自己的目标，主动向目标靠近 | reconcile() 检查孤儿率 |

### 5.3 三组件架构

```
┌─────────────────────────────────────────────────────────────┐
│                 自动接入子系统                                 │
│                                                             │
│  ┌──────────────────────┐                                   │
│  │ ModuleOnboardingScanner │ ← 主动扫描：发现新模块/蓝图     │
│  │   scan_filesystem()    │                                 │
│  │   scan_blueprints()    │                                 │
│  │   diff_registered()    │ ← 对比 CapabilityRegistry       │
│  └──────────┬───────────┘                                   │
│             │ 发现未注册模块                                  │
│             ▼                                               │
│  ┌──────────────────────┐                                   │
│  │   AutoIntegrator       │ ← 智能判断：临时启动 L3 分析     │
│  │   analyze_module()     │   "这个模块要不要接入？"         │
│  │   should_integrate()   │   "接入哪一层？"                 │
│  │   generate_card()      │   "怎么接入？"                   │
│  │   assign_work_type()   │   "分配什么工作类型？"            │
│  └──────────┬───────────┘                                   │
│             │ 生成 CapabilityCard + IntegrationPoint          │
│             ▼                                               │
│  ┌──────────────────────┐                                   │
│  │   OrphanDetector       │ ← 孤儿检测：持续监控孤儿率        │
│  │   compute_orphan_rate()│                                 │
│  │   find_orphans()       │ ← 找出所有未接入模块             │
│  │   prioritize_orphans() │ ← 按优先级排序                   │
│  │   report()             │ ← 生成孤儿报告                   │
│  └──────────────────────┘                                   │
└─────────────────────────────────────────────────────────────┘
```

### 5.4 ModuleOnboardingScanner

```python
class ModuleOnboardingScanner:
    """模块接入扫描器——主动发现未注册模块。

    借鉴:
      - K8s Controller Manager: 主动调和，不等事件
      - K8s Discovery: 自动发现集群中的资源
    """

    def scan_filesystem(self) -> list[ModuleDiscovery]
    def scan_blueprints(self) -> list[BlueprintDiscovery]
    def diff_registered(self) -> list[UnregisteredModule]
    def watch_for_changes(self) -> None              # 文件系统 watcher

@dataclass
class ModuleDiscovery:
    """发现的模块。"""
    module_path: str               # src/zephyr/governance/cost_router.py
    module_name: str               # cost_router
    package: str                   # governance
    has_class: bool                # 是否定义了类
    class_names: list[str]         # 类名列表
    has_public_functions: bool     # 是否有公开函数
    function_names: list[str]      # 函数名列表
    has_blueprint: bool            # 对应蓝图是否存在
    blueprint_path: str | None     # 蓝图路径
    docstring: str | None          # 模块 docstring
    imports: list[str]             # 依赖的其他模块

@dataclass
class UnregisteredModule:
    """未注册的模块——孤儿。"""
    discovery: ModuleDiscovery
    reason: str                    # 为什么没注册（新创建/遗漏/不支持）
    priority: str                  # P0/P1/P2 接入优先级
    suggested_layer: str           # 建议接入哪一层
```

**扫描策略**：
```
1. 全量扫描（CircadianScheduler 04:00 触发）
   - 遍历 src/zephyr/ 下所有 .py 文件
   - 遍历 architecture_model/ 下所有 .yaml 文件
   - 对比 CapabilityRegistry.list_all()
   - 输出 UnregisteredModule 列表

2. 增量扫描（文件系统 watcher 实时触发）
   - 监听 src/zephyr/ 目录的 create/modify 事件
   - 新文件 → 立即触发 ModuleOnboardingScanner
   - 输出单个 UnregisteredModule

3. 蓝图扫描（CircadianScheduler 07:00 触发）
   - 遍历 architecture_model/ 下所有 .yaml
   - 检查蓝图定义的模块是否都有对应 CapabilityCard
   - 输出蓝图→代码→注册的三方对齐报告
```

### 5.5 AutoIntegrator

```python
class AutoIntegrator:
    """自动接入器——临时启动高级模型分析是否接入。

    借鉴:
      - Claude Code Self-Improving: 临时启动强推理分析
      - K8s Admission Controller: 接入前审查
    """

    def analyze_module(self, module: UnregisteredModule) -> IntegrationAnalysis
    def should_integrate(self, analysis: IntegrationAnalysis) -> bool
    def generate_card(self, analysis: IntegrationAnalysis) -> CapabilityCard
    def assign_work_type(self, analysis: IntegrationAnalysis) -> str
    def auto_register(self, card: CapabilityCard) -> bool

@dataclass
class IntegrationAnalysis:
    """接入分析结果。"""
    module_path: str
    should_integrate: bool          # 是否应该接入
    reason: str                     # 为什么（不）接入
    suggested_layer: str            # trae / local / api
    suggested_priority: str         # P0 / P1 / P2
    suggested_work_types: list[str] # 建议的工作类型
    suggested_capability_card: CapabilityCard | None
    confidence: float               # 分析置信度 0.0-1.0
    model_used: str                 # 分析使用的模型（通常是 L3 API）
```

**接入决策流程**：
```
1. 发现未注册模块 → AutoIntegrator.analyze_module()

2. 临时启动 L3 高级模型（DeepSeek V4 Pro / Claude）分析：
   - 读取模块源码 + docstring + imports
   - 读取对应蓝图 YAML（如果有）
   - 判断：
     a. 这个模块是否应该接入大脑？（纯工具函数可能不需要）
     b. 接入哪一层？（Trae/Local/API）
     c. 分配什么工作类型？
     d. 生成 CapabilityCard 草稿

3. 如果 confidence >= 0.8 → 自动注册到 CapabilityRegistry
4. 如果 confidence < 0.8 → 写入 NightShiftQueue，等人类裁定
5. 无论哪种结果 → AiAuditLogger 记录分析过程
```

**关键设计：临时启动 L3**

```
正常情况：L3 只在夜班运行（省钱）
接入分析时：临时启动 L3 API 做一次深度推理
           ↓
  分析完毕后 L3 回到待机状态
           ↓
  成本控制：每天最多 10 次临时 L3 激活（可配置）
```

### 5.6 OrphanDetector

```python
class OrphanDetector:
    """孤儿检测器——持续监控孤儿率，驱动大脑向终极目标靠近。

    借鉴:
      - K8s Orphan Pod Detection
      - Self-Improving Agent: 知道目标，主动靠近
    """

    def compute_orphan_rate(self) -> float          # 0.0-1.0，目标=0.0
    def find_orphans(self) -> list[UnregisteredModule]
    def prioritize_orphans(self, orphans: list) -> list  # 按优先级排序
    def report(self) -> OrphanReport
    def is_goal_met(self) -> bool                   # 孤儿率 == 0.0?

@dataclass
class OrphanReport:
    """孤儿报告。"""
    total_modules: int
    registered_modules: int
    orphan_modules: int
    orphan_rate: float
    orphans_by_priority: dict[str, int]             # P0: 3, P1: 12, P2: 45
    orphans_by_package: dict[str, int]              # governance: 30, shared: 15, ...
    top_priority_orphans: list[UnregisteredModule]  # 最应该先接入的
    goal_gap: float                                 # 1.0 - orphan_rate，距离目标的差距
```

**与调和循环的衔接**：
```
HealthMonitor.reconcile() 每次调和时：
  ① 原有：probe 所有已注册组件 → spec vs actual
  ② 新增：OrphanDetector.compute_orphan_rate()
  ③ 新增：如果孤儿率 > 0 → 触发 ModuleOnboardingScanner.scan_filesystem()
  ④ 新增：发现孤儿 → AutoIntegrator.analyze_module()
  ⑤ 新增：分析结果 → 自动注册 或 登记表
  ⑥ 新增：ReconciliationReport 包含孤儿率指标
```

### 5.7 新模块创建时的自动接入

**当任何 AI 或人类创建新模块时**，自动触发接入流程：

```
新 .py 文件创建
  │
  ├─ 方式1: 文件系统 watcher 检测到新文件
  │         → ModuleOnboardingScanner.scan_filesystem()
  │         → 发现 UnregisteredModule
  │         → AutoIntegrator.analyze_module()
  │
  ├─ 方式2: 新蓝图 YAML 创建
  │         → ModuleOnboardingScanner.scan_blueprints()
  │         → 发现蓝图定义的模块未注册
  │         → AutoIntegrator.analyze_module()
  │
  └─ 方式3: AGENTS.md 中写明规则
            "所有新模块必须注册到 CapabilityRegistry"
            → AI 创建新模块时，读到这条规则，主动 register()
```

### 5.8 扫描现存所有模块的遗漏

**首次全量扫描**（Boot 时 + CircadianScheduler 04:00 定期）：

```
1. 遍历 src/zephyr/ 下所有 .py 文件 → 300+ 个文件
2. 遍历 architecture_model/ 下所有 .yaml → 31 个蓝图
3. 对比 CapabilityRegistry.list_all() → 当前注册数
4. 差集 = 未注册模块 = 孤儿
5. 按 priority 排序：
   - P0: 有蓝图定义但未注册的（蓝图说应该有，但没有）
   - P1: 有公开 API 的模块（class + public functions）
   - P2: 纯内部工具函数（可能不需要注册）
6. P0 立即触发 AutoIntegrator
7. P1 排队等待
8. P2 标记为"可选接入"
```

---

## 6. 新组件设计（全层级，100% 覆盖）

### 6.1 文件结构（完整）

```
src/zephyr/runtime/
├── __init__.py                    # 导出 AutoRuntimeCore
├── __main__.py                    # python -m zephyr.runtime 入口
├── auto_runtime_core.py           # 主类：系统大脑总控
├── lifecycle_manager.py           # 启动/停止/健康检查序列（含 Finalizer）
├── circadian_scheduler.py         # 内置生物钟：日常节奏 + 定时任务
├── capability_registry.py         # 能力注册中心：自注册 + 发现 + 监控
├── capability_card.py             # 能力卡片数据模型
├── status_dashboard.py            # 实时状态面板（TUI + JSON API）
├── night_shift_queue.py           # 夜班登记表持久化 + 裁定
├── ai_audit_logger.py             # AI 行为审计日志（结构化 JSON）
├── integration_registry.py        # 集成注册表：全系统接入点清单
├── health-monitor.py              # 健康监控 + 自愈（含水平触发调和）
├── runtime_config.py              # 配置模型
├── feedback-loop.py               # 反馈闭环：登记表裁定→规则进化
├── dream_cycle.py                 # 知识固化：归档→提取→遗忘→索引
├── stop_gate.py                   # 质量闸门：AI 不能空转退出
├── finalizer.py                   # 优雅清理：关闭前持久化+备份+commit
├── windows_service.py             # Windows Service 包装器
├── work_orchestrator.py           # 工作编排子系统
├── work_dag.py                    # DAG 数据模型
├── work_item.py                   # 工作项数据模型
├── module_onboarding_scanner.py   # 模块接入扫描器（新增）
├── auto_integrator.py             # 自动接入器（新增）
└── orphan_detector.py             # 孤儿检测器（新增）

项目根目录:
├── AGENTS.md                      # 项目宪法
└── .trae/rules/project_rules.md   # Trae IDE 规则

data/
├── night_shift_queue.jsonl
├── capability_cards/              # 每组件一个 YAML
├── circadian_tasks/schedule_state.json
├── audit_logs/ai_audit_{date}.jsonl
├── dream_archive/episodic/ + semantic/
├── feedback_proposals/PROPOSAL-*.yaml
├── health_snapshots/health_{timestamp}.json
└── work_dags/                     # DAG 定义（新增）
    ├── daily-dream-cycle.yaml
    ├── daily-health-check.yaml
    ├── daily-code-dedup.yaml
    ├── daily-kb-maintenance.yaml
    ├── daily-compliance.yaml
    ├── daily-feedback-loop.yaml
    ├── pipeline-full-run.yaml
    ├── kb-ingest-pipeline.yaml
    ├── security-scan.yaml
    └── model-drift-check.yaml
```

### 6.2 AutoRuntime Core（`auto_runtime_core.py`）

```python
class AutoRuntimeCore:
    """三层运行时运营中心——ZephyrAlpha 系统大脑。"""

    def __init__(self, config: RuntimeConfig)

    # ---- 生命周期 ----
    def boot(self) -> BootReport
    def shutdown(self) -> None

    # ---- 调和 ----
    def reconcile(self) -> ReconciliationReport
    def health(self) -> HealthSnapshot

    # ---- 状态 ----
    def status_panel(self) -> str
    def status_json(self) -> dict

    # ---- 任务 ----
    def dispatch_task(self, task: TaskCard) -> DispatchResult
    def get_night_shift_queue(self) -> list[NightShiftAmbiguityLogEntry]
    def resolve_night_shift(self, entry_id: str, decision: str, notes: str) -> None

    # ---- 工作编排 ----
    @property
    def work_orchestrator(self) -> WorkOrchestrator
    def submit_work(self, work: WorkItem) -> str
    def submit_dag(self, dag_id: str, params: dict) -> str

    # ---- 注册 ----
    @property
    def capability_registry(self) -> CapabilityRegistry
    @property
    def integration_registry(self) -> IntegrationRegistry

    # ---- 闸门 ----
    @property
    def stop_gate(self) -> StopGate
    def can_stop(self) -> bool
```

### 6.3 Lifecycle Manager

Boot Sequence（20步，含 WorkOrchestrator 初始化）：
```
01-13. 同 v3.0.0（配置→审计→注册→模型预热→调度器）
14. WorkOrchestrator.initialize(task_repo, capability_registry)  ← 新增
15. WorkOrchestrator.load_dags(data/work_dags/)                  ← 新增
16. CircadianScheduler().start()
17. HealthMonitor().start()
18. StatusDashboard().start()
19. IntegrationRegistry.validate_all()
20. 输出 BootReport → 进入主调和循环
```

### 6.4 其余组件

同 v3.0.0 spec.md §3.4~§4.6，不重复。新增组件见 §4（WorkOrchestrator）和 §5（自动接入子系统）。

---

## 7. 全系统集成点标配（扩展至 26 包）

| 目标系统 | 接口方式 | 用途 | SLA |
|----------|----------|------|-----|
| PipelineOrchestrator | `dispatch_task()` 委托 | 管线任务分派 | guaranteed |
| AgentOrchestrator | CapabilityCard 注册 | Agent 状态管理 | best_effort |
| DaemonRegistry | `register_daemon()` | 守护进程注册 | guaranteed |
| ContractRegistry | `register_contract()` | 契约注册 | best_effort |
| Gate Engine | Policy 声明 | 安全闸门入口 | guaranteed |
| ChromaDB | EmbeddingRouter 调用 | 向量存储 | best_effort |
| Vector Memory | `embed_text()` 委托 | 嵌入服务 | guaranteed |
| Ollama | HTTP `localhost:11434` | LLM 推理 + 嵌入 | guaranteed |
| File System | `tasks/` 目录监听 | 外部任务投递 | best_effort |
| Windows Service | `windows_service.py` | 开机自启 | guaranteed |
| TaskRepository | `create/update/get` | 任务状态机 | guaranteed |
| TaskQueue | 后台轮询 | 自动 dispatch | guaranteed |
| TaskScheduler | `schedule()` | 定时调度 | guaranteed |
| WorkOrchestrator | DAG + 优先级 | 工作编排 | guaranteed |
| ContextEngine | 上下文注入 | IDE 上下文 | best_effort |
| KB | 入库/查询 | 知识库 | best_effort |
| LLM Security | 安全扫描 | LLM 防护 | guaranteed |
| Governance | 治理检查 | 合规/审计 | best_effort |
| MCP | MCP Server | IDE 工具 | best_effort |
| DB | SQLite | 元数据 | guaranteed |
| CodeDedupEngine | 扫描/去重 | 代码质量 | best_effort |
| SystemTelemetry | Trace/Span | 可观测性 | best_effort |
| L00-L13 业务层 | 业务逻辑 | 量化交易 | best_effort |
| Hooks | 事件钩子 | 事件通知 | best_effort |
| Core | 任务队列/SLA/质量 | 基础能力 | guaranteed |
| Shared | 基础设施 | 通用工具 | guaranteed |

---

## 8. 防孤儿机制（完整）

### 8.1 注册清单（全部 9 处）

| 注册位置 | 内容 | 触发时机 |
|----------|------|----------|
| **AGENTS.md** | 项目宪法 | 手动维护 |
| CapabilityRegistry | CapabilityCard | 组件启动时自动 |
| IntegrationRegistry | IntegrationPoint | 系统 boot 时 |
| DaemonRegistry | Daemon 心跳 | 持续 |
| AiAuditLogger | 每次 AI 行为 | 每次调用 |
| NightShiftQueue | 不确定登记 | 遇到时追加 |
| ContractRegistry | 接口契约 CT-* | 启动时 |
| **WorkOrchestrator** | **WorkDAG** | **boot 时加载** |
| **OrphanDetector** | **OrphanReport** | **调和时自动** |

### 8.2 零孤儿保证

- **不注册 = 不存在**
- **不编排 = 不执行**（WorkOrchestrator 只执行注册过的 DAG）
- **不扫描 = 不发现**（ModuleOnboardingScanner 主动扫描，不等注册）
- CapabilityCard 校验拒绝错误注册
- HealthMonitor 持续 probe
- AiAuditLogger 全量记录
- AGENTS.md 第一入口

---

## 9. 全自动优化（一阶~八阶全表）

同 v4.0.0 §8，新增：

| 阶 | 优化项 | 实现组件 | 受益 |
|----|--------|----------|------|
| 一阶 | **自动扫描** | ModuleOnboardingScanner | 主动发现新模块 |
| 二阶 | **智能接入** | AutoIntegrator (L3 临时激活) | 自动判断+自动注册 |
| 二阶 | **孤儿检测** | OrphanDetector | 持续监控孤儿率 |
| 三阶 | **终极目标驱动** | reconcile() 检查孤儿率 | 大脑主动向目标靠近 |

| 阶 | 优化项 | 实现组件 | 受益 |
|----|--------|----------|------|
| 一阶 | **工作编排** | WorkOrchestrator | 自动决定什么工作、什么顺序、什么层 |
| 一阶 | **DAG 依赖管理** | WorkDAG | 工作间依赖自动解析 |
| 一阶 | **并行控制** | ConcurrencySlot | 同层多任务并行 |
| 二阶 | **优先级抢占** | PriorityPreemption | P0 抢占 P2 |
| 三阶 | **层间工作窃取** | LayerWorkStealing | L2 空闲时帮 L3 |

---

## 10. 验收标准（全部 22 条）

| # | 标准 |
|---|------|
| 1 | `python -m zephyr.runtime` 一键启动，自动 warmup 全部组件 |
| 2 | 开机自启：Windows Service 注册成功 |
| 3 | 启动后 TUI 面板实时显示三层状态 + 组件 + 节律 + 工作编排状态 |
| 4 | 内置节律运行：时间到了自动切换层级、触发任务 |
| 5 | DEMO 7 任务 + tasks/ JSON 投递任务全部自动分派 |
| 6 | 所有 AI 行为写入 `data/audit_logs/` JSONL |
| 7 | CapabilityRegistry 中注册了所有已实现组件 |
| 8 | IntegrationRegistry 验证全部 26 包集成点 |
| 9 | Ctrl+C → Finalizer → Stop Gate → 优雅关闭 |
| 10 | 资源 > 80% 自动降级 |
| 11 | Dream Cycle 每天至少触发一次 |
| 12 | Stop Gate 阻止空转退出 |
| 13 | 与 b_execution_model.yaml 100% 对齐 |
| 14 | `ruff check --select F` 零新增 |
| 15 | AGENTS.md 存在且完整 |
| 16 | Feedback Loop 生成至少一个进化提案 |
| 17 | **WorkOrchestrator 加载 10 个预定义 DAG** |
| 18 | **DAG 依赖自动解析：上游完成→下游 READY** |
| 19 | **并行控制：L2 同时跑 3 个嵌入任务** |
| 20 | **优先级抢占：P0 任务抢占 P2 槽位** |
| 21 | **ModuleOnboardingScanner 全量扫描发现孤儿** |
| 22 | **AutoIntegrator 临时启动 L3 分析后自动注册或登记** |

---

## 11. 与现有蓝图对应

| ARC 组件 | 对应蓝图 YAML | 关系 |
|----------|---------------|------|
| AutoRuntimeCore | `b_execution_model.yaml` | 运行时实现 |
| CircadianScheduler | `b_execution_model.yaml` runtime_schedule | 作息落地 |
| CapabilityRegistry | 新建（桥接 to `b_bridge.yaml`） | 能力注册 |
| IntegrationRegistry | 新建（桥接 to 所有 b_*.yaml） | 集成注册 |
| AiAuditLogger | 新建 | 审计日志 |
| HealthMonitor | `DaemonRegistry` 扩展 | 自愈 |
| StopGate | 新建 | 质量闸门 |
| DreamCycle | 新建 | 知识固化 |
| FeedbackLoop | `b_feedback_loop.yaml` | 自演化 |
| Finalizer | 新建 | 优雅清理 |
| AGENTS.md | 新建 | 项目宪法 |
| **WorkOrchestrator** | **新建** | **工作编排** |
| **WorkDAG** | **新建** | **DAG 依赖图** |
| **ModuleOnboardingScanner** | **新建** | **自动扫描** |
| **AutoIntegrator** | **新建** | **自动接入** |
| **OrphanDetector** | **新建** | **孤儿检测** |

---

> **成熟度**: 100%——v5.0.0 新增：
> - **终极目标**：全域接入，0% 孤儿率，写入 AGENTS.md + RuntimeConfig
> - **自动接入子系统**：ModuleOnboardingScanner + AutoIntegrator + OrphanDetector
> - **临时 L3 激活**：AutoIntegrator 分析新模块时临时启动高级模型
> - **调和循环增强**：reconcile() 检查孤儿率，主动驱动接入
> - **三重接入保障**：文件系统 watcher + 蓝图扫描 + AGENTS.md 规则
> - v4.0.0 全部内容（全系统清单 + 三层分类 + 工作编排子系统）
> - v3.0.0 全部内容（Stop Gate + Dream Cycle + Feedback Loop + Finalizer + AGENTS.md）
