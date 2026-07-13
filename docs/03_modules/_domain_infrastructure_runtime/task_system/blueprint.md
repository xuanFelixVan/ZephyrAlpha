---
module_id: MOD-TASK_SYSTEM
title: "Task System 蓝图 — 全链路任务卡生命周期管理"
doc_type: blueprint
template_for: blueprint
status: Active
version: "0.9.5"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
last_updated: "2026-05-16"
last_verified: "2026-05-15"
generation: 1
functional_domain: execution
parent_module: ""
rule_form: structural
scope: global
stability: evolving
ssot_claims:
  - {claim: "TaskCard 数据模型定义", scope: "global"}
  - {claim: "蓝图→任务卡拆解流程", scope: "global"}
  - {claim: "任务状态机 10 态定义", scope: "global"}
  - {claim: "任务 CRUD 业务接口", scope: "global"}
verifiability: hybrid
references: []
codification_level: L2
codification_at: "2026-05-15"
submodule_path: src/zephyr/governance
actual_disk_path: "src/zephyr/governance/"
runtime_plane: hot
ttl: permanent
construction_progress: partially_implemented
belongs_to: "MOD-MASTER_BLUEPRINT"
summary: "Task System 全链路蓝图 v0.9.1。覆盖意图→草稿→蓝图真源→任务卡拆解→AI双管线执行→脚本系统校验的闭环工作流。TaskCard 62字段（31基座+31执行层）。v0.9.1 回填OCP扩展点+施工步骤内容变更+依赖对齐+规格化压缩。"
tags: [task_system, task-card, vibe-coding, dual-pipelines, script-system, state-machine, gates, ai-execution, infrastructure, anti-drift, blind-spot-audit, dogfooding, ai-autonomy, circuit-breaker, diff-plan, saga-compensation, quality-regression-detection, model-snapshot-pinning, schema-migration, cancel-safety, atomic-write, adaptive-replanning, scope-creep-detection, context-cache-reuse]
depends_on:
  - {target: PS-STD-001, at: "§7.10", why: "task_id；§7.1 语义28+§7.1.1 追踪3→Task共31字段"}
  - {target: PS-STD-011, at: "MTH-012|MTH-013", why: "涌现式设计+路径合规创建"}
  - {target: GOV-DOC-002, at: "§5.1.2", why: "路径映射——产出物物理存放"}
  - {target: MOD-INF-005, at: "全篇", why: "脚本系统——管线产出的审计消费方"}
  - {target: GOV-TASK-004, at: "全篇", why: "任务生命周期治理——取消权限、优先级裁决、自治边界"}
  - {target: GOV-TASK-005, at: "全篇", why: "任务关闭标准——三步法"}
  - {target: TEMPLATE-TASK-001, at: "全篇", why: "任务卡模板——所有任务卡.md格式标准"}
  - {target: REG-LLM-001, at: "全篇", why: "模型基准排名——execution_model数据依据"}
  - {target: GOV-AI-002, at: "全篇", why: "模型路由策略——任务分配决策树、断路器、降级策略"}
  - {target: "src/zephyr/shared/schemas.py", at: "Task类", why: "Task模型基座——TaskCard继承其31字段"}
  - {target: "src/zephyr/governance/task_repo.py", at: "全篇", why: "Event Sourcing append_event+投影——数据层真源（v3.0 MOD-INF-012B）"}
  - {target: "MOD-INF-012B", at: "全篇", why: "Database v3.0 Event Sourcing——TaskRepo 底层架构"}
  - {target: KBG-0038, at: "全篇", why: "File-as-Task范式——文件与任务1:1双向映射"}
  - {target: KBG-0040, at: "全篇", why: "Pydantic V2强制——所有模型基座"}
  - {target: KBG-0030, at: "全篇", why: "SQLite元数据层——tasks/events/gates四表"}
priority: P0
runtime_plane: hot
responsibility_domain: 
design_maturity: prototype
build_status: generated
---

# Task System 蓝图 — 全链路任务卡生命周期管理

> module_id: MOD-TASK_SYSTEM | version: 0.9.5 | status: active | layer: L0_infrastructure
> actual_disk_path: src/zephyr/governance/task_repo.py | generation: 1 | construction_progress: partially_implemented

## 概述

Task System 是 ZephyrAlpha 的任务系统——解决"蓝图→任务卡→执行→完成"全链路管理问题。核心职责包括：蓝图拆解（BlueprintDecomposer）、任务卡生命周期管理（TaskManager 10状态机）、管线调度委托 MOD-INF-009（PipelineOrchestrator M1-M11）、MCP 接口（TaskManagerServer）。当前规模 100 AI 并发写入，目标容量 1000 任务/天。上游依赖蓝图和脚本系统，下游被 PipelineOrchestrator、审计系统、Dashboard 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **存在性状态受控词表**：`未实现` / `已实现` / `已阻塞` / `已废弃`
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-TASK_SYSTEM`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `task_system/__init__.py` | §4.1 | 包初始化（re-export from db/task_repo.py） | 已实现 | |
| 2 | `db/task_repo.py` | §4.2 | SQLite CRUD + 10状态机(MOD-INF-038 StateMachine[TaskStatus]) + N:N task_files | 已实现 | |
| 3 | `shared/schemas.py` | §4.2.1 | Task 模型基座（31 字段） | 已实现 | |
| 4 | `task_system/core/models.py` | §4.2.1 | TaskCard 模型（62 字段） | 已实现 | |
| 5 | `task_system/core/blueprint_decomposer.py` | §4.1.1 | 蓝图拆解器 | 已实现 | |
| 6 | `task_system/core/task_manager_server.py` | §4.5 | MCP 接口 | 已实现 | |
| 7 | `orchestrator/` | §4.1.3 | 管线调度器目录（73 个 .py 文件） | 已实现 | |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 代码文件清单100%存在 | `ls src/zephyr/governance/task_repo.py` + `ls src/zephyr/orchestrator/` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class/|def" src/zephyr/governance/task_repo.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.8.0 (基线) | task_repo/schemas/orchestrator/models/decomposer/task_manager_server | — | — |
| v0.9.0 (模板v3.5/v3.6升级+压缩) | 同 v0.8.0 + §0前移+§7/§15删除+§10拆分+§14类型列+铁律#13-#15 | — | 结构重组，无功能变更 |

### §0.4 SSoT 与责任唯一性声明

| 维度 | 真源 | 声明 |
|------|------|------|
| Task 数据模型 | shared/schemas.py Task（31字段） | 本蓝图 TaskCard 继承 Task，不重复定义基座字段 |
| 任务 CRUD + 状态机 | task_repo.py（SQLite） | 单源存储，.md 为伴读副本 |
| 蓝图→任务卡拆解 | blueprint_decomposer.py | RULE-ZERO-TASK：建卡来源之一（蓝图拆解路径） |
| 门禁判定 | MOD-GATE_ENGINE GateEngine | 本蓝图委托，不内嵌门禁逻辑 |
| 管线调度 | MOD-INF-009 PipelineOrchestrator | 本蓝图委托，不内嵌管线调度 |
| MCP 协议层 | MOD-INF-013 MCP Servers | 业务逻辑归属本蓝图，协议层归属 MOD-INF-013 |

### §0.5 代码目录唯一性声明

| 目录 | 归属蓝图 | 说明 |
|------|---------|------|
| src/zephyr/governance/task_repo.py | MOD-TASK_SYSTEM | 主代码目录 |
| src/zephyr/orchestrator/ | MOD-TASK_SYSTEM + MOD-INF-009 | BatchOrchestrator/file_task_mapper 归 MOD-TASK_SYSTEM；PipelineOrchestrator 归 MOD-INF-009 |
| src/zephyr/governance/task_repo.py | MOD-TASK_SYSTEM（业务接口）/ MOD-DATABASE（物理存储） | 业务接口定义权归 MOD-TASK_SYSTEM |
| src/zephyr/shared/shared_services/models.py | MOD-TASK_SYSTEM | TaskCard 模型 |
| src/zephyr/shared/shared_services/blueprint_decomposer.py | MOD-TASK_SYSTEM | 蓝图拆解器 |
| src/zephyr/integration/mcp/task_manager_server.py | MOD-TASK_SYSTEM（业务逻辑）/ MOD-INF-013（协议层） | 见 §0.4 SSoT 声明 |
| src/zephyr/pipeline/ | MOD-INF-009 | 管线调度 |
| src/zephyr/governance/rule_enforcement/ | MOD-GATE_ENGINE | 门禁引擎 |

---

## §1 设计背景与目标

### §1.1 背景

| # | 核心问题 | 说明 |
|---|---------|------|
| 1 | 蓝图分散、格式不统一 | MOD-INF-003/004 各用 9 节旧格式，相互引用但内容割裂——违反 "零记忆重启标准" |
| 2 | 场外草稿未迁入真源 | 双管线设计+任务卡元模型+知识库设计——数千行决策全在草稿里，不在项目真源文件中 |
| 3 | 管线未贯通 | 蓝图→任务卡拆解→双管线执行→脚本系统——完整链路只存在于讨论中 |

### §1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|------|------|-----------|
| 1 | ✅包含 | **合并为一**：MOD-INF-003+004 + 两份场外草稿 + 历史裁定 = 一份自包含蓝图 | 蓝图文件数 3→1，两份旧蓝图 deprecated |
| 2 | ✅包含 | **全链路贯通**：意图→草稿→蓝图→任务卡→双管线→脚本系统——每步有输入/输出/门禁 | 每个环节 Schema 完整 |
| 3 | ✅包含 | **TaskCard 模型取最优**：基座继承 shared/schemas.py Task（31字段）+ 扩展防漂移 + 父子层级 + 回滚 + 自治字段 | 基座对齐 metadata_registry.yaml §7 真源 |
| 4 | ✅包含 | **task_id 格式统一为 `{NAMESPACE}-{SEQ}`** | KBG-001 / STD-005 / SRC-042 |
| 5 | ✅包含 | **路径合规创建**：MTH-013 原则——AI 不得自主决定目录层级 | 所有路径可追溯到索引 |
| 6 | ✅包含 | **模型分工明确**：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种救援 | 分工有基准数据支撑 |
| 7 | ✅包含 | **Dogfooding**：任务系统用自身管理自身维护 | 本蓝图的施工任务全部通过 task_repo.create() 注册 |
| 8 | ✅包含 | **AI 自治边界五级**：supervised / semi_autonomous / autonomous / full_auto / emergency_only | GOV-TASK-004 §AI自治 五级枚举 + 每级允许操作清单 |
| 9 | ✅包含 | **全链路可观测**：每个 M 模块执行耗时/Token/成本可追踪 | events 表含 module_id + duration_ms |
| 10 | ✅包含 | **失败自愈**：失败模式自动匹配→应用已知 mitigation | FailurePattern 匹配引擎可用，匹配成功率 > 60% |
| 11 | ✅包含 | **执行可靠性三层**：diff-plan 约束 + 并发冲突检测 + 幂等强制检查 | G1 门禁增加 diff_plan_required / conflict_free / idempotent_check |
| 12 | ✅包含 | **API 韧性**：断路器 + 指数退避 + 自动降级 | 断路器状态可查，自动降级延迟 < 5s |
| 13 | ✅包含 | **跨模块聚合**：支持多个 Blueprint 的任务按 Phase/Epic 聚合 | Phase/Epic 字段可用，跨模块查询 < 100ms |
| 14 | ✅包含 | **Prompt 质量可追溯**：每个 M 模块的 prompt 有独立版本号 | `prompt_diff` / `prompt_rollback` 可用 |
| 15 | ✅包含 | **失败可精细补偿**：多步骤任务失败后按 Saga 补偿事务逆序撤销 | compensation_steps 自动执行，补偿成功率 > 80% |
| 16 | ✅包含 | **质量退化自动发现**：模型输出质量下降 15%+ 时自动检测并回退 | QualityBaseline 可用，退化检测延迟 < 1个任务周期 |
| 17 | ❌排除 | KMS 知识库的 KE 条目定义和抓取机制 | 属于独立的 KMS 系统升级——本蓝图 §4.2.3 新增接口契约预留（KE 推送格式+与 task 生命周期关联） |
| 18 | ❌排除 | 模型注册表（model-registry.yaml）的完整建设 | 独立小任务——任务卡模板中已预埋引用字段 |
| 19 | ❌排除 | 草稿治理系统 | 独立系统——本蓝图新增 DraftAssistant 模块（§2.1 职责 #8） |
| 20 | ❌排除 | SQLite 数据库物理迁移 | 已有代码 task_repo.py——蓝图只定义数据模型规范 |
| 21 | ❌排除 | Phase 5 AI 自治模块 | 五级枚举已在 GOV-TASK-004 中定义，逐步实现 |
| 22 | ❌排除 | 全功能看板 UI | 超出 1 人+AI 维护的 ROI 边界——CLI 摘要视图替代 |
| 23 | ❌排除 | 多 Agent 辩论/投票 | v0.5.0+ 的事——当前串行管线 + 三层防御足够 |

### §1.4 运行场景约束

| # | 场景 | 约束 | 验证方式 |
|---|------|------|---------|
| 1 | 单 AI Session 执行 | WIP ≤ 3，串行 dispatch | task_repo 查询 IN_PROGRESS 数 |
| 2 | 10+ AI Session 并行 | BatchOrchestrator 原子认领 + 依赖感知 | 并发测试无重复认领 |
| 3 | Owner 离线 | AI 自治边界五级约束生效 | PermissionGuard 检查 |
| 4 | 紧急热修复 | emergency_mode 跳过非关键门禁 | 事后 24h 补审计 |

### §1.5 利益相关者映射

| # | 利益相关者 | 角色 | 核心关注 | 交互接口 |
|---|-----------|------|---------|---------|
| 1 | Owner | 任务审批、优先级裁决 | 任务价值对齐、WIP 可控 | `task_repo.transition()` 审批门 |
| 2 | AI (Vibe Coding) | 施工执行、状态推进 | 任务可执行性、上下文完整 | `BlueprintDecomposer` → `TaskManager` |
| 3 | CI/CD Pipeline | 门禁检查、质量守门 | 门禁通过率、回归阻断 | `GateEngine` G0-G7 检查 |

> ⚠️ 利益相关者冲突时，Owner 优先级最高。AI 不得绕过 Owner 审批执行 `human_gated` 操作。

### §1.6 当前态/目标态差距

| # | 维度 | 当前态 (v0.8.0) | 目标态 (v1.0.0) | 差距 |
|---|------|:---:|:---:|------|
| 1 | 任务状态机 | 7 状态 | 10 状态（+BLOCKED/SUSPENDED/CANCELLED） | 缺 3 状态 + 转换规则 |
| 2 | 门禁覆盖 | G0-G3 | G0-G7 | 缺 G4-G7 实现 |
| 3 | 并发模型 | 单 Worker | Multi-Worker Batch Coordination | 缺原子认领 + 批量调度 |
| 4 | MCP 接口 | HTTP mock | SQLite 持久化 + 完整 CRUD | 缺持久化层 |
| 5 | 蓝图拆解 | 手动 | BlueprintDecomposer 自动拆解 | 缺自动拆解器 |

> ⚠️ v0.8.0 → v1.0.0 升级必须按 §16.3 步骤顺序执行，禁止跳步。

### §1.7 典型场景

| # | 场景 | 触发 | 流转路径 | 完成条件 |
|---|------|------|---------|---------|
| 1 | 蓝图拆解→任务创建 | Owner 提交蓝图 | `BlueprintDecomposer.parse()` → `task_repo.create()` × N | 所有 TaskCard 状态 = CREATED |
| 2 | 门禁检查→执行 | AI 认领任务 | `GateEngine.check(G0-G7)` → PASS → `transition(IN_PROGRESS)` | 门禁全 PASS + 状态 = IN_PROGRESS |
| 3 | 执行→完成 | AI 提交产出 | `transition(REVIEW)` → Owner 审批 → `transition(DONE)` | Owner 确认 + 门禁 G6-G7 PASS |
| 4 | 紧急热修复 | emergency_mode=True | 跳过 G1-G5 → 执行 → 24h 内补审计 | 事后审计完成 |

> ⚠️ 场景 4 仅限 `emergency_mode`，常态施工禁止跳过任何门禁。

---

## §2 模块边界

### §2.1 职责边界

| # | 类型 | 内容 | 标准/原因 |
|---|------|------|-----------|
| 1 | ✅包含 | **蓝图管理**：作为任务系统的唯一输入——蓝图按模板书写后，§16 施工指引直接驱动任务卡拆解 | 蓝图 = 原材料 |
| 2 | ✅包含 | **任务卡生命周期**：蓝图自动拆解→Owner确认→task_repo.create()→10状态流转→G0-G7门禁→task_repo.transition()→关闭 | 任务卡 = 工件 |
| 3 | ✅包含 | **标签体系**：扁平 `tags[]`（推荐五轴前缀约定：`fn:`/`ly:`/`md:`/`st:`/`mo:`） | 五轴由 AI 内部解析而非强制 |
| 4 | ✅包含 | **AI双管线执行**：A区 M1-M5（生产）+ B区 M6-M11（审计） | AI执行 = 引擎 |
| 5 | ✅包含 | **模型分工策略**：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种救援 | 基于 REG-LLM-001 + GOV-AI-002 |
| 6 | ✅包含 | **脚本系统集成**：任务管线产出自动送审——C区 12 维度审计 | MOD-INF-005 |
| 7 | ✅包含 | **KMS 知识管理**（beta+ 排除——接口契约已定义，实现另排） | 接口预留——§4.2.3 定义 KE 推送格式与生命周期关联 |
| 8 | ✅包含 | **DraftAssistant** | 意图→结构化蓝图骨架的半自动生成入口——全链路第一步 |
| 9 | ✅包含 | **AI 自治边界管理** | 五级自治枚举 + 每级允许操作清单——Owner 离线时的行为契约 |
| 10 | ✅包含 | **任务系统自诊断** | 蓝图-代码一致性校验 + SQLite schema 健康检查 + 漂移检测 |
| 11 | ✅包含 | **全链路可观测** | M1-M11 每步耗时/Token/成本记录 + CLI `zalpha status` 摘要视图 |
| 12 | ✅包含 | **失败自愈** | FailurePattern 自动匹配 + mitigation 应用——同错不犯两次 |
| 13 | ✅包含 | **Prompt 版本化管理** | M1-M11 prompt 语义化版本存储 + diff/rollback/AB对比 |
| 14 | ✅包含 | **Saga 补偿事务执行** | 任务失败时逆序执行 undo_command + DeadLetter处理 |
| 15 | ✅包含 | **质量基线监控** | QualityBaseline 维护 + M7 偏差检测 + 自动回退模型快照 |
| 16 | ❌排除 | SQLite CRUD + 10状态机 + N:N映射 | `task_repo.py`（`src/zephyr/db/`）— 已有生产级代码 |
| 17 | ❌排除 | Task 模型基座（Pydantic V2 31字段） | `shared/schemas.py`（`src/zephyr/shared/`）— metadata_registry.yaml §7 真源 |
| 18 | ❌排除 | MCP Server Web 层 | `task_manager_server.py`（`src/zephyr/mcp/`） |
| 19 | ❌排除 | 审计脚本 | MOD-INF-005 — 已有 9+ 脚本 |
| 20 | ❌排除 | context_engine | `context_engine/` — 已有 7 模块 |
| 21 | ❌排除 | dashboard | `dashboard/` — 已有代码 |
| 22 | ❌排除 | 模型注册表完整建设 | 独立小任务——model-registry.yaml 另排 |
| 23 | ❌排除 | 全功能看板 UI | 排除——CLI 摘要视图替代 |
| 24 | ❌排除 | 多 Agent 并行辩论 | v0.5.0+ 的事——当前串行管线 + 三层防御足够 |

> ⛔ **强制规则（RULE-ZERO-TASK）**：任务卡 MUST 通过 `TaskRepository.create()` 写入 SQLite，禁止手写 `.md` 建卡。
> 建卡触发 = 用户主动 OR 八指标阈值触发（详见 trae_003_task_granularity_threshold.yaml）。
> 蓝图拆解（`BlueprintDecomposer.decompose(blueprint_path)`）是建卡来源之一，非唯一路径。
> 其他来源（Bug修复/架构债务/代码扫描/重构任务）可通过 `TaskRepository.create(allow_direct_create=True)` 建卡。
> `Blueprint → Decomposer → SQLite（真源）→ .md（伴读）` 是蓝图拆解的路径；`Task → TaskRepository.create() → SQLite → .md` 是非蓝图任务的路径。

---

## §3 架构设计

> 全链路：① 意图→② 草稿（多轮 AI 优化）→③ 蓝图真源→④ §16 施工指引→拆卡算法→TaskCard→task_repo.create()→⑤ A区生产线(DeepSeek) / ⑥ B区审计线(GLM) / ⑦ C区脚本系统(MOD-INF-005)→⑧ 下一个循环

### §3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | BlueprintDecomposer | 蓝图→TaskCard 拆解 | task_repo | 同步调用 |
| 2 | TaskLifecycleManager | 10态状态机 | task_repo | 同步调用 |
| 3 | TaskManagerServer | MCP 5 Tool 接口 | task_repo | MCP 协议 |
| 4 | BatchOrchestrator | 10+ AI Session 并行认领 | task_repo | SQLite 原子 UPDATE |

> 管线调度委托 → MOD-INF-009 PipelineOrchestrator（见 §10 依赖）。MOD-TASK_SYSTEM 不内嵌管线调度逻辑。

### §3.2 数据流

> **v3.0 架构变更（MOD-INF-012B）**：Task 状态变更为 Event Sourcing 模型——状态不再通过 `UPDATE tasks SET status=...` 直接修改，而是通过 `append_event()` 追加不可变事件到 `task_events` 表。当前状态 = 事件流投影（ProjectionEngine.fold）。详见 [MOD-INF-012B §3](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/sub-blueprints/MOD-INF-012B-blueprint.md)。

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | 蓝图.md | BlueprintDecomposer 解析§16 | task_repo(append_event) | TaskCard Pydantic |
| 2 | task_repo | PipelineOrchestrator 调度 | A区/B区管线 | DispatchResult |
| 3 | A区产出 | B区审计 | C区脚本系统 | AuditFinding |

### §3.3 状态生命周期

> 10 态状态机 + SUSPENDED（v0.4.0 扩展）。**状态机基础设施已迁移至 MOD-INF-038 `StateMachine[TaskStatus]`**（`src/zephyr/shared/state_machine.py`），本蓝图仅定义任务领域业务语义（状态/转换/守卫）。
>
> **v3.0 实现变更（MOD-INF-012B）**：状态变更从 `UPDATE tasks SET status` 改为 `append_event(TASK_CLAIMED/COMPLETED/...)`。业务语义（守卫条件/转换规则）不变，仅存储机制从可变行变为不可变事件流。当前状态 = `ProjectionEngine.fold(task_events)`。

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| PENDING | G0+G7 通过 | READY | 字段完整性+路径合规 |
| READY | dispatch() | IN_PROGRESS | WIP≤5 + 依赖 COMPLETED |
| IN_PROGRESS | M1-M11 完成 | COMPLETED | G4+G5 通过 |
| COMPLETED | 审计通过 | VERIFIED | G6 通过 |
| IN_PROGRESS | Owner/AI 暂停 | SUSPENDED | — |
| SUSPENDED | 恢复 | IN_PROGRESS | suspend_context_json 可用 |
| SUSPENDED | 超时>24h | FAILED | — |
| FAILED | 自动/手动 | RETRY | retry_count < max_retries |
| 任一状态 | Owner 取消 | CANCELLED | cancel_task() 清理协议 |

> 父任务状态聚合：任一子任务 FAILED→父 BLOCKED；全部 COMPLETED→父 COMPLETED；全部 VERIFIED→父 VERIFIED

> **迁移记录**：`task_repo.py` 的 `_ALLOWED_TRANSITIONS` 字典已替换为 `StateMachineConfig[TaskStatus]`（`_TASK_STATE_MACHINE_CONFIG`），转换校验委托 `_TASK_SM.can_transition_from()`。REG-SM-001 已注册 `fsm_id=task-lifecycle`。

---

## §4 接口契约

> 强制 Pydantic V2 BaseModel（KBG-0040），禁止 `@dataclass`。
> **模型层级**：`shared/schemas.py` `Task`（31 字段）→ 本蓝图 TaskCard 继承 `Task` 并扩展执行层字段。

### §4.1 公共 API

#### §4.1.1 蓝图拆解器（BlueprintDecomposer）

```python
class BlueprintDecomposer:
    """从蓝图 §16 施工指引拆解为任务卡——写入 task_repo（SQLite）+ .md 同步"""

    def __init__(self, repo: TaskRepo):
        self.repo = repo

    def decompose(self, blueprint_path: str, output_dir: str,
                  strategy: str = "hybrid", model_assignment: str = "auto"
                  ) -> "DecompositionResult":
        """
        输入：蓝图路径（§16 施工指引）
        输出：DecompositionResult（任务卡清单 + 依赖图）
        核心逻辑：解析§16→分配task_id→G0/G7门禁→task_repo.create()→.md同步
        """
        ...
```

#### §4.1.2 任务卡生命周期管理器

```python
class TaskLifecycleManager:
    """包装 task_repo.py 的 10 态状态机 + .md 同步。门禁判定委托 MOD-GATE_ENGINE GateEngine（见 §10 依赖）。"""

    def create_task_card(self, task: "TaskCard") -> DecompositionResult: ...
    def transition(self, task_id: str, to_status: TaskStatus, gate_check: bool = True) -> "TransitionResult": ...
    def check_gate(self, task_id: str, gate_id: "GateLevel") -> "GateCheckResult":
        """委托 GateEngine.evaluate()。MOD-TASK_SYSTEM 不内嵌门禁逻辑，门禁 SSoT = MOD-GATE_ENGINE。"""
```

#### §4.1.3 管线调度接口

> 管线调度接口定义见 MOD-INF-009 §4.1 PipelineOrchestrator。MOD-TASK_SYSTEM 不重复定义已委托组件的接口。
>
> MOD-TASK_SYSTEM 消费方式：`from zephyr.pipeline.pipeline_orchestrator import PipelineOrchestrator` → `dispatch(task_card)`

### §4.2 数据模型

#### §4.2.1 TaskCard（Vibe Coding 扩展任务模型）

> **基座**：继承 `shared/schemas.py` `Task`（31 字段，真源 metadata_registry.yaml §7.1~§7.1.1）
> **扩展**：本蓝图追加 6 维防漂移 + 门禁 + 管线 + 父子层级/可执行回滚/Retry策略/AI自治五级/Prompt版本化/Saga补偿/SLA时限/模型快照/紧急模式/知识隔离/依赖指纹/取消残留/漂移校验/兼容冲击/重规划/范围蔓延/上下文缓存

> ⚠️ **B-20 铁律**：§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码。完整 TaskCard 字段定义见 `src/zephyr/infrastructure/runtime_integration/auto-fix-engine/models.py`。

| 字段分组 | 字段数 | 关键字段 |
|---------|:---:|------|
| 基座（shared/schemas.py Task） | 31 | task_id/namespace/status(10态)/priority/execution_model/files_in_scope/deliverables/tags/depends_on/... |
| 防漂移六维 | 7 | upstream_files/downstream_outputs/allowed_touch/forbidden_touch/applicable_rules/context_assembly_manifest/rollback_instructions |
| 门禁+管线 | 4 | completed_gates/blocked_gates/assigned_pipeline/pipeline_modules |
| 产物+审计+自治 | 4 | artifact_paths/audit_findings/ke_entries/ai_autonomy_level |
| v0.4.0 扩展 | 11 | parent_task_id/epic/retry_count+max_retries+retry_backoff_seconds/checkpoint_path/estimated_context_tokens+context_window_limit/effective_priority/diff_plan_required/circuit_breaker_open/suspend_context_json |
| v0.5.0 扩展 | 10 | prompt_version+prompt_variant/compensation_steps/sla_deadline+sla_escalation_policy+original_priority/model_snapshot_pinned/thinking_state_json/emergency_mode/cross_task_learning/dependency_fingerprint |
| v0.6.0 扩展 | 8 | cancelled_artifacts/upstream_files_content_hash/consumer_impact_report+run_consumer_tests/replan_proposed/modified_files_actual+lines_changed_actual/context_cache_key |
| v0.7.0 依赖对齐 | 4 | depgraph_nodes/depgraph_layer/dependency_type(hard/soft/none)/dependency_rationale |

**枚举类型**：

| 枚举 | 值 |
|------|-----|
| GateLevel | G0(创建)/G1(指派)/G2(前置)/G3(执行)/G4(产出)/G5(审计)/G6(关闭)/G7(完整度) |
| TaskNamespace | KB 决策记录/CP/KE/STD/DW/SRC/OPS/DM |
| AISelfGovernanceLevel | supervised/semi_autonomous/autonomous/full_auto/emergency_only |

#### §4.2.2 其他模型

| 模型 | 关键字段 |
|------|---------|
| DecompositionResult | total_tasks, tasks: list[TaskCard], dependency-graph, unassigned_items, warnings |
| GateCheckResult | gate_id, task_id, passed, violations, checked_at |
| AuditFinding | finding_id(F-NNNN), dimension, severity(critical~info), description, source_task, resolved |

### §4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `decompose()` | `blueprint_path` | ✅ | 完整路径（相对优先）+ .md + doc_type=blueprint |
| | `output_dir` | ✅ | 必须是 `03_modules/{layer}/{module}/changes/{feature-id}/` |
| `create_task_card()` | `task` | ✅ | TaskCard——G0+G7 门禁通过 |
| `transition()` | `task_id` | ✅ | `{NAMESPACE}-{SEQ}` |
| | `to_status` | ✅ | TaskStatus 合法值 + 状态机允许路径 |
| `dispatch()` | `task_id` | ✅ | status in {PENDING, READY, RETRY} |

### §4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `decompose()` | `DecompositionResult`：N 张 TaskCard + SQLite 已写入 + .md 同步 | `FILE_NOT_FOUND` / `NO_CONSTRUCTION_GUIDE` / `G7_VIOLATIONS` |
| `create_task_card()` | TaskCard + task_repo.create() 成功 + .md 副本 | `GATE_BLOCKED(G0/G7)` / `DUPLICATE_ID(409)` / `PATH_NOT_COMPLIANT` |
| `transition()` | task_repo.update_status() 成功 + events 记录 | `STATUS_MISMATCH(409)` / `ILLEGAL_TRANSITION(422)` / `GATE_BLOCKED(422)` |
| `dispatch()` | 管线+模型+M模块链已分配 | `INVALID_DISPATCH_STATUS(409)` / `NO_PIPELINE_AVAILABLE(503)` |

### §4.5 MCP 接口

> MCP Server 位置：[task_manager_server.py](file:///D:/ZephyrAlpha/src/zephyr/integration/mcp/task_manager_server.py)
> 数据真源：[task_repo.py](file:///D:/ZephyrAlpha/src/zephyr/governance/task_repo.py)（SQLite）——MCP Server 不得使用内存字典

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `decompose_blueprint` | `decompose()` | `{blueprint_path, output_dir}` | `{total_tasks, task_ids, warnings}` |
| `create_task` | `create_task_card()` | `{task_card_json}` | `{task_id, status}` |
| `update_task_status` | `transition()` | `{task_id, new_status}` | `{task_id, title, status, ...}` |
| `get_task` | — | `{task_id}` | `{task_id, title, status, ...}` |
| `register_from_triage` | — | `{triage_path, namespace?, phase?}` | `{task_id, title, status, ...}` |

> **.md 双轨同步**：`_persist()` / `transition()` 成功后自动调用 `_taskcard_to_md()` 同步 `.md`。SQLite 始终是真源。

**错误码**：`TASK_NOT_FOUND(404)` / `STATUS_MISMATCH(409)` / `ILLEGAL_TRANSITION(422)` / `GATE_BLOCKED(422)` / `VALIDATION_ERROR(400)` / `PATH_NOT_COMPLIANT(422)` / `REPO_NOT_INJECTED(500)`

### §4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| TaskCard 新增字段 | ✅ 向后兼容 | 不影响已有任务卡 |
| TaskCard 删除/重命名字段 | ❌ 破坏性 | 需 Owner 审批 + 迁移 |
| TaskCard 基座切换（Task类） | ❌ 破坏性（与 v0.2.0） | task_id格式/状态机/标签全变 |
| GateLevel 新增值 | ✅ 向后兼容 | 新门禁不破坏已有逻辑 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |
| MCP 输入 Schema 修改 | ⚠️ 需通知 | 消费者需更新参数 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

### §4.7 OCP 扩展点

| 扩展点 | 扩展方式 | 约束 |
|--------|---------|------|
| 新增 TaskNamespace | 枚举新增值 | ✅ 向后兼容——不影响已有命名空间 |
| 新增 GateLevel | 枚举新增值 | ✅ 向后兼容——新门禁不破坏已有逻辑 |
| 新增 MCP Tool | Server 新增方法 | ✅ 向后兼容——不影响已有消费者 |
| 新增 Pipeline Module | pipeline_modules 列表追加 | ✅ 向后兼容——M1-M11 可扩展至 M20+ |
| TaskCard 字段扩展 | Pydantic extra="allow" | ✅ 向后兼容——新字段有默认值 |
| 状态机新增转换 | STATE_MACHINE 字典新增 key | ⚠️ 需验证——新转换路径不得破坏已有守卫条件 |

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 版本 | 3.12+ |
| 2 | 模型基座 | Pydantic V2 BaseModel——禁止 dataclass |
| 3 | 路径格式 | 项目根相对路径+正斜杠（如 `docs/03_modules/...`） |
| 4 | 持久化数据库 | SQLite 唯一 |
| 5 | 双轨制 | 任务卡 .md + SQLite 双轨——task_repo.create() 后同步 .md |
| 6 | 门禁执行时机 | 门禁在状态转换前执行 |
| 7 | 任务卡编号 | `{NAMESPACE}-{SEQ}`（KB 决策记录/CP/KE/STD/DW/SRC/OPS） |
| 8 | 蓝图状态限制 | 蓝图 draft/review 状态不得拆卡 |
| 9 | 路径合规创建 | MTH-013——AI 不得自主决定目录层级 |
| 10 | TaskCard 基座 | 强制继承 `shared/schemas.py` Task——禁止独立定义 |
| 11 | WIP 上限 | 同时 IN_PROGRESS ≤ 5（P0/P1 ≤ 2）——超过时 dispatch() 拒绝 |
| 12 | 并发文件冲突检测 | dispatch() 前检查所有 IN_PROGRESS 任务的 allowed_touch 交集——有交集时拒绝 |
| 13 | 上下文窗口溢出保护 | M2 装配前计算 estimated_context_tokens，超过 context_window_limit * 0.8 时触发裁剪 |
| 14 | API 断路器 | 同一模型连续失败 3 次→自动熔断 5 分钟，路由到 fallback_model |
| 15 | Retry 指数退避 | RETRY→IN_PROGRESS 自动等待 base * 2^(retry_count-1) 秒，max_retries 默认 3 |
| 16 | diff-plan 强制 | P0/P1 任务的 diff_plan_required 强制为 True |
| 17 | 幂等性强制检查 | PENDING/READY→IN_PROGRESS 前检查 downstream_outputs 是否已存在 |
| 18 | 依赖拓扑排序 | BlueprintDecomposer.decompose() 必须输出拓扑序——检测循环依赖 |
| 19 | 优先级链上传播 | 若 depends_on 中有 P0/P1，下游 effective_priority ≥ 上游最高优先级 |
| 20 | SUSPENDED 超时自动失败 | SUSPENDED 超过 24h → 自动 FAILED + 通知 Owner |
| 21 | Prompt 版本化管理 | M1-M11 prompt template 语义化版本存储于 `prompts/{module_id}_v{MAJOR}.{MINOR}.{PATCH}.yaml` |
| 22 | Saga 补偿事务 | 执行失败时按 compensation_steps 逆序执行 undo_command。补偿失败→DeadLetter+通知 |
| 23 | 模型质量退化检测 | M7 完成后对比 score vs QualityBaseline——偏差>15% 触发 QualityRegressionAlert |
| 24 | SLA 时限自动升级 | sla_deadline 超时→SLAWatchdog 自动按 sla_escalation_policy 升级优先级 |
| 25 | 跨 Session AI 思考态持久化 | AI session 结束前自动保存 thinking_state_json |
| 26 | 跨任务知识隔离 | 每个 dispatch() 必须在新的 context window 中启动。cross_task_learning 默认 False |
| 27 | 紧急热修复快速通道 | emergency_mode=True 时跳过 G1-G5，仅保留 G0+G6+G7。事后 24h 内补审 |
| 28 | 模型快照锁定 | model_snapshot_pinned 记录 dated snapshot。无快照时自动填充 default_snapshot |
| 29 | 多文件原子写入 | M3 写入时先写 `.zalpha_tmp_{task_id}` →全部成功→逐个 os.rename |
| 30 | 依赖新鲜度级联感知 | 任务完成后记录 dependency_fingerprint。依赖项被修改→标记 stale_dependency_warning |
| 31 | 任务系统组件降级运行 | gate_engine 故障→跳过非 P0 门禁；task_repo 故障→HALT；pipeline 故障→降级为 manual |
| 32 | SQLite Schema 版本化迁移 | `migrations/` 增量 SQL + `PRAGMA user_version` + Migrator.apply_pending() 启动时自动执行 |
| 33 | 任务取消安全协议 | cancel_task() 扫描 `.zalpha_tmp_{task_id}` 清理→记录 cancelled_artifacts |
| 34 | 执行时前置条件漂移校验 | dispatch() 前 PreflightCheck：逐个 os.path.exists + os.R_OK upstream_files |
| 35 | 共享模块向后兼容性冲击分析 | COMPLETED→识别共享模块→ImpactAnalysis 列出消费者→M7 增加 consumer compatibility check |
| 36 | 中执行自适应重规划 | M3 发现意外→REPLAN_PROPOSED 子状态→AI 提议替代方案→Owner 审批或自动 |
| 37 | 输出范围蔓延检测 | M3 完成后对比 diff-plan：modified_files_actual vs planned→超出→WARNING |
| 38 | 跨 Session 上下文复用 | ContextCache key=sha256(task_id+upstream_files) →hash全匹配→复用 summary |

### §5.2 容量估算

| 维度 | 当前 | 峰值 | 极限 | 够用？ |
|------|:--:|:--:|:--:|:--:|
| 蓝图 | 6（含 deprecated） | 200+ | 无上限 | ✅ |
| 任务卡(SQLite) | 当前 task_metadata.db | 2000+ | 10000/域 | ✅ |
| Change Folder(.md) | 1 | 200+ | 文件系统 | ✅ |
| SQLite | <100MB | <100MB | ~281TB | ✅ |
| M 模块 | 11 | 20 | 30+ | ✅ |
| 模型 | 3 | 8 | 受控词表可扩展 | ✅ |

### §5.3 迁移

> 临时时态内容已全部执行完毕并验证通过——已从蓝图删除。历史记录见 git log。

| # | 已完成迁移 | 说明 |
|---|-----------|------|
| 1 | MOD-INF-003/004 deprecated→物理删除 | 内容已合并至本蓝图 |
| 2 | v0.2.0 TaskCard → v0.3.0 继承 Task | core/models.py 已重写 |

### §5.4 非功能需求与服务水平

| # | 维度 | 目标值 | 度量方式 | 不达标处置 |
|---|------|--------|---------|-----------|
| 1 | 可用性 | 99.9% | `task_repo` 操作成功数 / 总请求数 | 降级到内存暂存（见 §6.2） |
| 2 | MTTR | < 10 min | 故障检测 → 服务恢复时长 | 告警升级到 Owner |
| 3 | 可观测性 | 100% 操作有审计日志 | `AiAuditLogger` 覆盖率扫描 | 补充日志后才能关闭任务 |
| 4 | 并发安全 | 0 重复认领 | 并发测试断言 | 修复原子认领 SQL |
| 5 | 数据持久性 | 0 丢失 | SQLite WAL + 原子写入验证 | 启用 `os.replace()` 模式 |

> ⚠️ 可用性 99.9% 基于单机 SQLite 部署。分布式部署需重新评估。


| # | SLO | 目标 | 测量窗口 | 告警阈值 | 降级策略 |
|---|-----|------|---------|---------|---------|
| 1 | 任务创建延迟 | p99 < 500ms | 5 min 滚动 | > 1s | 排队 + 异步创建 |
| 2 | 门禁通过率 | ≥ 95%（首次提交） | 每日统计 | < 80% | 阻断 dispatch + 通知 Owner |
| 3 | 状态转换一致性 | 100%（SQLite ↔ .md 双写） | 每次转换后校验 | 任何不一致 | 暂停转换 + 修复同步 |
| 4 | 批量认领延迟 | p99 < 2s（50 任务/批） | 10 min 滚动 | > 5s | 减小 batch_size |

> ⚠️ SLO 3（状态转换一致性）为硬性要求——0 容忍。任何双写不一致必须立即修复。

### §5.5 自动化触发机制

| 触发类型 | 触发方式 | 触发条件 | 自动化组件 |
|---------|---------|---------|-----------|
| 服务启动 | AutoRuntimeCore.boot() | 系统启动 | CircadianScheduler + HookRegistry + TaskQueue |
| 定时维护 | CircadianScheduler cron | 每日0时：升级/超时检查；每日2时：孤儿扫描 | task_repo.check_escalation / check_task_timeout / TaskCompletionGate.scan |
| 事件响应 | hook_registry.fire() | 任务状态转换 | auto_unblock_dependents / auto_retry_on_failure |
| 队列轮询 | TaskQueue.start_polling() | 300s间隔 | READY/PENDING 任务自动 dispatch |
| 手动操作 | MCP Tool 调用 | AI/人工触发 | decompose_blueprint / create_task / update_task_status |

### §5.7 禁止模式与导入约束

| # | 禁止模式 | 替代方案 | 违反后果 | 检测方式 |
|---|---------|---------|---------|---------|
| 1 | 直接操作 SQLite（绕过 `task_repo`） | `TaskRepository` 公共 API | 数据不一致 + 审计断裂 | Grep `sqlite3.connect` 在 `src/zephyr/` 非 `task_repo` 位置 |
| 2 | 跳过门禁直接 `transition()` | `GateEngine.check()` → PASS → `transition()` | 非法状态转换 | `transition()` 内置门禁断言 |
| 3 | 硬编码状态转换路径 | `STATE_MACHINE[next_state]` 查表 | 状态机漂移 | Grep 字符串 `"IN_PROGRESS"` 等状态字面量 |
| 4 | 在 `task_repo` 外维护任务状态 | 仅 `task_repo` 为 SSoT | 多源冲突 | 审计脚本扫描非 `task_repo` 状态写入 |

> ⚠️ 禁止模式 = 代码审查硬阻断。任何 PR 包含上述模式必须打回。

| # | 允许导入 | 禁止导入 | 原因 |
|---|---------|---------|------|
| 1 | `zephyr.task_system.*` | `zephyr.kb.*` | 知识库是消费者，不是依赖 |
| 2 | `zephyr.orchestrator.*` | `zephyr.runtime.*` | 运行时是上层编排，循环依赖 |
| 3 | `zephyr.core.shared_schemas` | `zephyr.infra_ops.a2a_protocol.*` | A2A 是通信层，任务系统不应直接依赖 |
| 4 | `zephyr.gates.*` | `zephyr.mcp.*`（反向） | MCP 是传输层，门禁不应依赖传输 |

> ⚠️ 导入约束违反 = 架构漂移。新增导入前 MUST 在 `[MODIFY-GUARD]` 中声明并经 Owner 批准。

---

## §6 错误处理

### §6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| task_create_latency | Histogram | task_repo.create() 计时 | p99 > 500ms | P2 |
| gate_pass_rate | Gauge | GateEngine.evaluate() 结果 | < 80% | P1 |
| state_consistency | Gauge | task_repo vs .md 三态校验 | any 不一致 | P0 |
| queue_depth | Gauge | TaskQueue.pending_count | > 100 | P2 |
| auto_decompose_latency | Histogram | BlueprintWatcher._trigger_decompose() 计时 | p99 > 30s | P2 |
| hook_callback_error_rate | Gauge | HookRegistry.fire() 异常率 | > 5% | P1 |

### §6.2 异常场景

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | task_repo 写入冲突 | SQLite busy_timeout | 重试 3 次 | 任务创建延迟 |
| 2 | 蓝图解析失败 | try/except + 日志 | 跳过损坏蓝图，标记错误 | 部分任务卡未创建 |
| 3 | Saga 补偿死锁 | 超时检测 | 回滚整个 Saga | 关联任务回退 |
| 4 | WIP 超限 | 水位监控 | 拒绝新任务 / 排队 | 任务创建被阻塞 |

### §6.3 退化矩阵

| # | 故障组件 | 退化模式 | 退化行为 | 恢复条件 | 数据风险 |
|---|---------|---------|---------|---------|---------|
| 1 | PipelineOrchestrator | 单步执行 | 跳过批量调度，逐任务串行 dispatch | Orchestrator 健康检查恢复 | 无 |
| 2 | TaskRepository (SQLite) | 内存暂存 | `InMemoryTaskStore` 替代，操作日志写入本地文件 | SQLite 恢复后从日志回放 | 日志丢失 = 数据丢失 |
| 3 | GateEngine | 宽松模式 | 仅执行 G0/G1 关键门禁，非关键门禁记录告警 | GateEngine 恢复后补执行 G2-G7 | 跳过门禁期间质量无保障 |
| 4 | BlueprintDecomposer | 降级为直接建卡 | 蓝图拆解路径不可用时，非蓝图任务仍可通过 `TaskRepository.create(allow_direct_create=True)` 建卡 | Decomposer 恢复后蓝图任务恢复拆解路径 | 蓝图任务暂停创建，非蓝图任务不受影响 |

> ⚠️ 退化模式不是常态——故障恢复后 MUST 退出退化。`InMemoryTaskStore` 数据 MUST 在 SQLite 恢复后完整回放，否则视为数据丢失事故。

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 未授权任务状态变更 | 高 | PermissionGuard 检查 | 单元测试 |
| 2 | 任务注入（恶意 TaskCard） | 中 | G1-G5 门禁验证 | 集成测试 |
| 3 | 敏感数据泄露（context 字段） | 中 | 日志脱敏 | 扫描脚本 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | task_repo/状态机 | CRUD + 状态转换合法性 | 覆盖率 ≥80% |
| 2 | 集成测试 | 拆解→创建→执行→完成 | 端到端任务生命周期 | 端到端通过 |
| 3 | 并发测试 | 100 Session 写入 | WIP 限制 + 写入冲突 | 无死锁 / 无数据丢失 |

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| PS-STD-001 | 必须 | §7——task_id/语义28/追踪3/Task共31/状态机 | ≥2.0.0 | `docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml` |
| PS-STD-011 | 必须 | MTH-012 涌现式设计 + MTH-013 路径合规 | ≥2.6.0 | `docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml` |
| GOV-DOC-002 | 必须 | §5.1.2 路径映射 | — | `docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml` |
| GOV-TASK-001 | 必须 | 任务卡操作指南 | ≥3.0.0 | `docs/01_policies_and_standards/governance/task/task-card-standard.md` |
| GOV-TASK-004 | 必须 | 取消权限、优先级裁决 | ≥2.0.0 | `docs/01_policies_and_standards/governance/task/task-lifecycle-standard.md` |
| GOV-TASK-005 | 必须 | 关闭三步法 | ≥1.1.0 | `docs/01_policies_and_standards/governance/task/task-closure-standard.md` |
| MOD-INF-005 | 必须 | 脚本系统 12 维度 | ≥3.0.0 | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` |
| MOD-GATE_ENGINE | 必须 | 门禁引擎 G0-G7 任务门禁 + G1-G5 KMS决策门 | ≥2.0.0 | `docs/03_modules/_cross_layer/gate_engine/blueprint.md` |
| MOD-INF-009 | 必须 | 管线调度 SSoT——任务管线 M1-M11 双管线路由 + Fast/Batch双通道 | ≥2.0.0 | `docs/03_modules/_cross_layer/pipeline/blueprint.md` |
| shared/schemas.py | 必须 | Task 31 字段 TaskCard 基座 | 现有代码 | `src/zephyr/shared/schemas.py` |
| task_repo.py | 必须 | SQLite CRUD + 10状态机 + N:N + BatchCoordination | 现有代码 | `src/zephyr/governance/task_repo.py` |

### §10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-TASK_SYSTEM` |
| 2 | §11 产出物路径 ↔ 依赖图 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### §10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| blueprint_decomposer.py | task_manager_server.py | decompose() 产出 TaskCard → MCP Tool 消费 | 检查 TaskCard 实例 |
| task_repo.py | pipeline_orchestrator.py | SQLite 状态 → dispatch() 前置条件 | 检查 task status |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| blueprint_decomposer.py | task_repo.py | TaskCard Pydantic | 函数调用 |
| task_repo.py | pipeline_orchestrator.py | Task status | SQLite 查询 |
| pipeline_orchestrator.py | task_repo.py | events (duration_ms/token_consumed) | SQLite 写入 |

### §10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 蓝图依赖 12+ 模块 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖 |
| 3 | 临时时态内容自动清理 | 是 | 有迁移方案 |
| 4 | 施工步骤完成度自动检测 | 否 | 已施工完成 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | asset-inventory/dependency.py | 不覆盖scripts/ |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |

### §10.5 概念重叠声明

| 重叠维度 | 重叠蓝图 | 处置 | 依据 |
|---------|---------|------|------|
| 门禁判定逻辑 | MOD-GATE_ENGINE GateEngine | 委托——MOD-TASK_SYSTEM 调用 GateEngine.evaluate() | §0.4 SSoT 声明 |
| 管线调度逻辑 | MOD-INF-009 Pipeline | 委托——MOD-TASK_SYSTEM 消费 PipelineOrchestrator.dispatch() | §0.4 SSoT 声明 |
| MCP 协议层 | MOD-INF-013 MCP Servers | 分层——业务逻辑归 MOD-TASK_SYSTEM，协议层归 MOD-INF-013 | §0.4 SSoT 声明 |
| 任务生成 | MOD-INF-035 AutoTaskGenerator | 无重叠——AutoTaskGenerator 生成 L2 推理任务，非 TaskCard | §0.4 SSoT 声明 |
| task_repo 物理存储 | MOD-DATABASE Database | 分层——业务接口归 MOD-TASK_SYSTEM，物理存储归 MOD-DATABASE | §0.4 SSoT 声明 |

### §10.6 依赖链风险评级

| 依赖链 | 深度 | 风险等级 | 缓解措施 |
|--------|:---:|---------|---------|
| MOD-TASK_SYSTEM→MOD-GATE_ENGINE→MOD-INF-009→MOD-INF-005 | 4 | L2(中) | 逐级超时+断路器+降级 |
| MOD-TASK_SYSTEM→MOD-CONTEXT_ENGINE(X-02) | 2 | L1(低) | 上下文注入失败→降级为空上下文 |
| MOD-TASK_SYSTEM→MOD-INF-018(X-01) | 2 | L1(低) | RBAC 查询失败→默认拒绝 |
| MOD-FEEDBACK_LOOP→MOD-TASK_SYSTEM(X-04) | 2 | L2(中) | 自愈任务走 TaskRepository.create() 建卡（RULE-ZERO-TASK） |

---

## §11 产出物存放目录

> ⚠️ 所有路径必须与 GOV-DOC-002 §5.1.2 一致。MTH-013 强制。

| 产出物类型 | 存放完整路径（相对优先） | consumer_min | 说明 |
|----------|---------------|:---:|------|
| 蓝图文件 | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` | 0 | 本文件 |
| 业务代码 | `src/zephyr/governance/task_repo.py` | 1 | TaskSystem 包 |
| 业务代码 | `src/zephyr/orchestrator/` | 1 | 管线调度器 |
| 业务代码 | `src/zephyr/shared/shared_services/models.py` | 1 | TaskCard 模型 |
| 业务代码 | `src/zephyr/shared/shared_services/blueprint_decomposer.py` | 1 | 蓝图拆解器 |
| 数据层 | `src/zephyr/governance/task_repo.py` | 5 | SQLite CRUD + 状态机 |
| 数据层 | `src/zephyr/data/persistence/sqlite_schema.py` | 5 | Schema + 迁移链 |
| MCP 接口 | `src/zephyr/integration/mcp/task_manager_server.py` | 2 | MCP 5 Tool |
| MCP 契约 | `src/zephyr/mcp/tool-contracts.yaml` | 2 | Tool Schema |
| 门禁 | `src/zephyr/governance/rule_enforcement/task_completion_gate.py` | 1 | G7 门禁 |
| 管线 | `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_orchestrator.py` | 1 | 管线编排器 |
| 上下文 | `src/zephyr/orchestration/context_management/context_assembler.py` | 1 | 上下文装配器 |
| 任务卡（SQLite 真源）| `data/databases/governance.db` — tasks 表 | 5 | SQLite |
| Task 模型基座 | `src/zephyr/shared/schemas.py` | 5 | 31 字段基座 |
| N:N 文件映射 | `src/zephyr/orchestration/runtime_core/orchestrator/file_task_mapper.py` | 1 | 文件-任务映射 |
| 知识审阅池 | `src/zephyr/data/knowledge_management/kb/triage.py` | 1 | Triage |
| 蓝图-代码同步 | `scripts/governance/d5_architecture/validate_blueprint_code_sync.py` | 1 | 校验脚本 |
| 测试 | `tests/` | 0 | 测试用例 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| shared/schemas.py（Task基座） | TaskCard 继承 Task | `core/models.py → from zephyr.shared.schemas import Task` | isinstance(task_card, Task) == True |
| task_repo.py（SQLite CRUD） | BlueprintDecomposer → task_repo.create() | `decompose() → self.repo.create(task)` | SQLite tasks 表新增行 |
| task_repo.py（状态机） | TaskLifecycleManager → task_repo.update_status() | `transition() → self.repo.update_status()` | events 表新增事件 |
| 脚本系统（MOD-INF-005） | B区完成→事件触发 C区 | `execute_pipeline(B) → audit_batch()` | B区后检查 Finding |
| MCP Server | 新增 decompose_blueprint 等 5 Tool | `task_manager_server.py` | ListTools 确认 |
| context_engine | G3→触发装配 | `transition(IN_PROGRESS) → assemble()` | 检查上下文 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整路径（相对优先） | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | MOD-TASK_SYSTEM 条目更新 | 版本升级 |
| 2 | 任务卡元注册表 | `docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.md` | 迁移状态更新 | v0.2.0→v0.3.0 |
| 3 | core/models.py | `src/zephyr/shared/shared_services/models.py` | TaskCard 继承 Task | 基座对齐 |
| 4 | blueprint_decomposer.py | `src/zephyr/shared/shared_services/blueprint_decomposer.py` | 对接 task_repo | 数据层真源 |
| 5 | task_manager_server.py | `src/zephyr/integration/mcp/task_manager_server.py` | MCP 5 Tool | 接入 SQLite |
| 6 | task_completion_gate.py | `src/zephyr/governance/rule_enforcement/task_completion_gate.py` | G7 门禁逻辑同步 | 约束对齐 |

---

## §14 已知风险与缓解

> 本节同时承接原 §15 后果中的**负面后果**——正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 任务卡 .md 与 SQLite 不同步 | 中 | 高 | transition() 前双轨一致性校验 | 风险 |
| 2 | 蓝图 §16 不完整→拆卡遗漏 | 高 | 高 | MTH-012——§16 必须极度详细；unassigned_items >10%→拒绝拆解 | 风险 |
| 3 | DeepSeek V4 Pro 幻觉（幻觉率 94%） | 高 | 高 | GLM 审查纠错→Claude 关键兜底——三层防御 | 风险 |
| 4 | DeepSeek V4 Pro API 不可用 | 低 | 高 | fallback_model 降级 + 断路器自动熔断 | 风险 |
| 5 | 路径漂移——AI 自作主张建目录 | 中 | 高 | MTH-013 零自主创建权 | 风险 |
| 6 | TaskCard 基座切换破坏已有代码 | 高 | 高 | 同步重写 models.py/decomposer/task_manager_server | 负面后果 |
| 7 | 任务卡字段多（62字段）→填卡成本高 | 中 | 中 | 拆解算法自动填充 80% | 负面后果 |
| 8 | 蓝图较长→AI token 压力 | 中 | 中 | §16 施工指引结构化——AI 先读目标+施工 | 负面后果 |
| 9 | 2 个 AI session 同时修改重叠文件 | 中 | 高 | dispatch() 前检查 allowed_touch 交集 | 风险 |
| 10 | 上下文窗口溢出 | 高 | 极高 | M2 装配前计算 estimated_context_tokens，超过 80% 触发裁剪 | 风险 |
| 11 | 同样的错误发生两次 | 高 | 中 | FailurePattern 自动匹配引擎 + mitigation 应用 | 风险 |
| 12 | Owner 离线时系统卡死 | 高 | 极高 | 通知机制 + 断路器自动降级 + AI 自治边界五级 | 风险 |
| 13 | 任务系统自身漂移 | 高 | 极高 | validate_blueprint_code_sync.py + 自诊断健康检查 | 风险 |
| 14 | M1-M11 管线硬编码 | 中 | 中 | M 模块声明式配置（YAML） | 风险 |
| 15 | 任务执行半完成状态 | 中 | 高 | 超时→自动 FAILED + checkpoint_path 恢复 | 风险 |
| 16 | 循环依赖导致任务链死锁 | 低 | 极高 | 拓扑排序，检测到循环→拒绝拆解 | 风险 |
| 17 | Prompt 质量退化 | 高 | 极高 | Prompt 版本化管理——SemVer + Git 存储 + prompt_rollback | 风险 |
| 18 | 多步骤任务失败后代码库半修改态 | 中 | 高 | Saga 补偿事务——逆序执行 undo_command | 风险 |
| 19 | 模型质量静默退化 | 高 | 极高 | QualityBaseline 基线对比 + M7 偏差检测 | 风险 |
| 20 | 低优先级任务被永久遗忘 | 中 | 高 | SLA 时限 + SLAWatchdog 自动升级 | 风险 |
| 21 | AI 受前序任务影响选错技术方案 | 中 | 高 | 跨任务知识隔离——每次 dispatch 新 context | 风险 |
| 22 | P0 故障修复被门禁链卡住 | 中 | 高 | 紧急热修复快速通道——跳过 G1-G5，24h 内补审 | 风险 |
| 23 | 模型供应商无声更新导致行为不一致 | 高 | 高 | 模型快照锁定——model_snapshot_pinned | 风险 |
| 24 | 系统崩溃时多文件写入半途中断 | 低 | 高 | 原子写入——先写 .tmp →全部成功→逐个 rename | 风险 |
| 25 | 已完成的依赖被修改后下游基于过期前提 | 中 | 高 | 依赖指纹 + 级联 stale_dependency_warning | 风险 |
| 26 | SQLite Schema 与 Pydantic 模型版本割裂 | 高 | 极高 | migrations/ 增量SQL + PRAGMA user_version 自动迁移 | 风险 |
| 27 | 任务排队期间 upstream_files 被删除/修改 | 中 | 高 | dispatch() 前 PreflightCheck + content_hash 对比 | 风险 |
| 28 | AI 修改共享模块后约 50% 概率破坏消费者 | 高 | 高 | ImpactAnalysis 消费者兼容检查 + run_consumer_tests | 风险 |
| 29 | AI 执行中遇到意外→只能 FAIL | 中 | 中 | REPLAN_PROPOSED 子状态 + AdaptivePlanningGate | 风险 |
| 30 | AI 实际修改超出计划范围 | 中 | 中 | diff-plan vs actual 对比 + scope_creep WARNING | 风险 |
| 31 | 同一 Task 跨 3-5 个 Session 重复读取浪费 Token | 低 | 中 | ContextCache hash 匹配复用 | 风险 |
| 32 | 取消中的任务留下半完成文件 | 低 | 中 | cancel_task() 清理 tmp + cancelled_artifacts 记录 | 风险 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | shared/schemas.py `Task` 已理解——31 字段 + 10 状态机 | 能回答 Task.task_id 格式 | ☐ |
| 4 | task_repo.py CRUD + 状态机转换表已理解 | 能回答参数 | ☐ |
| 5 | MTH-013 路径合规创建已理解 | 能执行三步决策流程 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### §16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 2 个 Phase（scaffold 善后 / experimental 补给） |
| 施工模式 | 重写型——v0.2.0 代码与 v0.3.0 契约不兼容 |
| 核心风险 | 破坏性变更——core/models.py / blueprint_decomposer.py / task_manager_server.py 需同步重写 |
| 目标 generation | 1 |

### §16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | shared/schemas.py Task 类存在 | hard | ✅ | ✅ |
| 2 | task_repo.py 可用 | hard | ✅ | ✅ |
| 3 | metadata_registry.yaml §7 字段定义 active | hard | ✅ | ✅ |
| 4 | PS-STD-011 ≥ 2.6.0 | hard | ✅ | ✅ |
| 5 | GOV-AI-002 ≥ 2.0.0 | hard | ✅ | ✅ |
| 6 | 本蓝图 Owner 已确认 | hard | ☐ | ❌ |

### §16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。

#### 步骤 1：更新蓝图注册表

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §13 |
| 产出位置 | `docs/03_modules/blueprint_registry.yaml` |
| 验收标准 | MOD-TASK_SYSTEM 条目 version→0.9.3，blueprint_status→approved |
| AI 自治范围 | ai_modifiable |
| 验证命令 | `python -c "import yaml; d=yaml.safe_load(open('docs/03_modules/blueprint_registry.yaml')); print(d['modules']['MOD-TASK_SYSTEM']['version'])"` |
| 检查点 | blueprint_registry.yaml 可被 yaml.safe_load() 解析 |
| G7 检查项 | 上游文件是否全部列出？下游产出物路径是否全部精确？ |

#### 步骤 2：同步 task-card-meta-registry.md

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §13 |
| 产出位置 | `docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.md` |
| 验收标准 | 记录 MOD-TASK_SYSTEM v0.2.0→v0.9.3 迁移 |
| AI 自治范围 | ai_modifiable |
| 验证命令 | `python -c "import yaml; d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.md')); print('OK')"` |
| 检查点 | task-card-meta-registry.md 包含 MOD-TASK_SYSTEM 迁移记录 |
| G7 检查项 | 迁移状态是否准确？ |

#### 步骤 3：重写 core/models.py — TaskCard 继承 Task

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2.1 |
| 产出位置 | `src/zephyr/shared/shared_services/models.py` |
| 内容变更 | ① TaskCard 从独立 BaseModel → 继承 `shared/schemas.py` Task；② task_id format 从 `TASK-INF-XXXX` → `{NAMESPACE}-{SEQ}`；③ TaskStatus 从 created/queued/.../closed → PENDING/IN_PROGRESS/.../CANCELLED（10态）；④ 删除 tags_fn/tags_ly/tags_md/tags_st/tags_mo 五轴字段→改用 Task 父类的 flat `tags[]`；⑤ 保留并追加 Vibe Coding 执行层字段（防漂移六维+门禁+管线+父子层级+自治五级+Prompt版本化+Saga补偿+SLA+模型快照+紧急模式+知识隔离+依赖指纹+取消残留+漂移校验+兼容冲击+重规划+范围蔓延+上下文缓存） |
| 验收标准 | ① isinstance(TaskCard(...), Task) == True；② task_id pattern `^(KB 决策记录/|CP/|KE/|STD/|DW/|SRC/|OPS)-//d+$`；③ status ∈ TaskStatus enum |
| AI 自治范围 | human_gated |
| 验证命令 | `python -m pytest tests/test_task_repo.py -k test_taskcard -x` |
| 检查点 | isinstance(TaskCard(...), Task) == True |
| G7 检查项 | 基座继承正确？字段完整？ |

#### 步骤 4：重写 blueprint_decomposer.py — 对接 task_repo

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1.1 |
| 产出位置 | `src/zephyr/shared/shared_services/blueprint_decomposer.py` |
| 内容变更 | ① decompose() 不再写 .md 为主——改为 `task_repo.create(task)`（写 SQLite）为主，.md 同步生成为辅；② task_id 生成从 `TASK-INF-0001` 自增 → 按 `{NAMESPACE}-{SEQ}` 格式（解析蓝图所属域+查询 task_repo 当前最大 seq）；③ 每张任务卡执行 G0/G7 门禁；④ task_repo.create() 成功后同步生成 .md 副本 |
| 验收标准 | ① decompose(本蓝图) → task_repo.list_tasks() 返回 N≥1 条记录；② task_id 格式正确 |
| AI 自治范围 | human_gated |
| 验证命令 | `python -m pytest tests/test_blueprint_decomposer.py -x` |
| 检查点 | decompose(本蓝图) 返回 N>=1 条 task_repo 记录 |
| G7 检查项 | 输出格式正确？门禁通过？ |

#### 步骤 5：重写 task_manager_server.py — MCP 接入 SQLite

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.5 |
| 产出位置 | `src/zephyr/integration/mcp/task_manager_server.py` |
| 内容变更 | ① MCP Server 必须初始化 task_repo 连接（SQLite），禁止使用内存 dict 作为任务存储；② 实现 5 Tool（decompose_blueprint/create_task/update_task_status/get_task/register_from_triage）；③ decompose_blueprint Tool 调用 BlueprintDecomposer；④ create_task/update_task_status/get_task 直接对接 task_repo |
| 验收标准 | ① MCP Server 初始化 task_repo 连接（SQLite）；② 实现 5 Tool；③ 禁止内存 dict |
| AI 自治范围 | human_gated |
| 验证命令 | `python -m pytest tests/test_mcp_servers.py -k task_manager -x` |
| 检查点 | MCP Server 初始化 SQLite 连接成功 + 5 Tool 注册完成 |
| G7 检查项 | 数据层真源正确？Tool 签名对齐？ |

#### 步骤 6：补齐 context_engine + 确认 M1-M11

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1.3 |
| 产出位置 | `src/zephyr/context_engine/` / `src/zephyr/pipeline/` |
| 验收标准 | ① G3 门禁可用；② M1-M11 模块引用对齐执行层字段 |
| AI 自治范围 | ai_modifiable |
| 验证命令 | `python -m pytest tests/test_pipeline_orchestrator.py -x` |
| 检查点 | G3 门禁可用 + M1-M11 模块引用对齐执行层字段 |
| G7 检查项 | 管线模块完整？ |

**M 模块分工表**（基于 GOV-AI-002 v2.0.0 模型路由策略）：

| 模块 | 管线 | 职责 | 模型 |
|------|:---:|------|:---:|
| M1 | A区 | 任务卡解析→结构化执行计划 | DeepSeek V4 Pro |
| M2 | A区 | 上下文装配→调用 context_engine | DeepSeek V4 Pro |
| M3 | A区 | 代码/文档生成——核心生产 | DeepSeek V4 Pro |
| M4 | A区 | 格式校验 | DeepSeek V4 Pro |
| M5 | A区 | 产物打包 | GLM |
| M6 | B区 | 差异检测——产出 vs 期望 | DeepSeek V4 Pro |
| M7 | B区 | **深度审查**——逐个文件逻辑/合规 | **GLM** |
| M8 | B区 | 标准合规——PS/GOV/KB 决策记录 | DeepSeek V4 Pro |
| M9 | B区 | 风险评估——OWASP LLM Top 10 | DeepSeek V4 Pro |
| M10 | B区 | 审计报告→Finding 格式 | DeepSeek V4 Pro |
| M11 | B区 | 门禁裁决——G5/G6 | DeepSeek V4 Pro |

**Claude 特种救援触发条件**：DeepSeek 执行失败 3 次 / GLM 审查连续驳回 2 次 / Owner 标记"关键" / tags=fn:security

### §16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1（注册表） | YAML 损坏 | 手动回退 YAML |
| 2（元注册表） | 迁移状态错误 | 手动回退 |
| 3（models.py） | TaskCard 继承失败 | 恢复 v0.2.0 独立 TaskCard 模型 |
| 4（decomposer） | task_repo 对接失败 | 恢复旧版——用 .md 为主的方式 |
| 5（MCP Server） | 5 Tool 不可用 | 恢复旧版 4 Tool |
| 6（context+M1-M11） | 管线不完整 | 回滚成本低——与 v0.2.0 相同 |

### §16.5 施工完成标准

| # | 产出物 | 存放完整路径（相对优先） | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | blueprint_registry.yaml | `docs/03_modules/blueprint_registry.yaml` | ☐ | ☐ | ☐ |
| 2 | task-card-meta-registry.md | `docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.md` | ☐ | ☐ | ☐ |
| 3 | core/models.py | `src/zephyr/shared/shared_services/models.py` | ☐ | ☐ | ☐ |
| 4 | blueprint_decomposer.py | `src/zephyr/shared/shared_services/blueprint_decomposer.py` | ☐ | ☐ | ☐ |
| 5 | task_manager_server.py | `src/zephyr/integration/mcp/task_manager_server.py` | ☐ | ☐ | ☐ |
| 6 | context_engine + M1-M11 | `src/zephyr/context_engine/` + `pipeline/` | ☐ | ☐ | ☐ |


| # | 检查项 | 通过标准 | 验证方式 | 不通过处置 |
|---|--------|---------|---------|-----------|
| 1 | SLO 达标 | §5.5 全部 SLO 在告警阈值内 | 监控仪表盘 | 阻断上线 |
| 2 | 监控覆盖 | 所有 §6.1 异常场景有告警 | 告警规则审查 | 补充告警后重审 |
| 3 | 告警路由 | P0 → Owner 即时 / P1 → 值班 15min / P2 → 日志 | 告警配置审查 | 修正路由 |
| 4 | 退化验证 | §6.2 每种退化模式至少演练 1 次 | 演练记录 | 补演练后重审 |
| 5 | 回滚验证 | §16.4 回滚方案可执行且 < 5 min | 回滚演练 | 修复回滚脚本 |
| 6 | 文档完整 | 操作手册（§16.11）+ 故障手册（§16.10）无空项 | 文档审查 | 补充后重审 |
| 7 | 集成测试 | M1-M11 全链路测试 PASS | CI 流水线 | 修复失败用例 |

> ⚠️ 7 项全部 ☑ 才能标记 `construction_status = completed`。任何一项 ☒ = 施工未完成。

### §16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者 |
| verification_status | verified | 审计者 |
| code_alignment_verified | yes | 审计者 |

### §16.7 参考实现规格

> 从蓝图特有章节提取的关键实现规格——施工时直接引用。

#### §16.7.1 Multi-Worker Batch Coordination Schema

> B-20 铁律：已实现代码不在蓝图中重复。完整 SQL 见 `src/zephyr/governance/task_repo.py`。

新增列：`batch_id TEXT` / `claimed_by TEXT` / `claimed_at TEXT`
索引：`idx_tasks_batch` / `idx_tasks_claimed`

#### §16.7.2 原子认领 SQL

> B-20 铁律：已实现代码不在蓝图中重复。完整 SQL 见 `src/zephyr/governance/task_repo.py`。

`UPDATE tasks SET status='IN_PROGRESS', claimed_by=?, claimed_at=? WHERE task_id=? AND claimed_by IS NULL` — SQLite WAL 模式下原子操作。

#### §16.7.3 TaskRepository 关键方法签名

| 方法 | 签名 | 说明 |
|------|------|------|
| `create` | `(task: Task, *, files: list[dict] /| None = None) -> TaskCard` | 创建任务+文件映射 |
| `transition` | `(task_id, to_status, gate_check=True) -> TransitionResult` | 状态转换+门禁 |
| `claim_next` | `(batch_id, worker_id) -> TaskCard /| None` | 原子认领+自动阻塞下游(blocked_by) |
| `recover_stale_claims` | `(batch_id, timeout_minutes=30) -> int` | 超时回收+自动解除下游阻塞 |
| `batch_progress` | `(batch_id) -> dict[str, int]` | 批量进度聚合 |

#### §16.7.4 BatchOrchestrator 使用模式

> B-20 铁律：已实现代码不在蓝图中重复。完整使用示例见 `src/zephyr/orchestration/runtime_core/orchestrator/batch_orchestrator.py`。

`from zephyr.orchestrator.batch_orchestrator import BatchOrchestrator` → `claim_next()` / `mark_done()` / `mark_failed()` 循环。

### §16.8 施工参考卡

| 操作 | 命令/代码 |
|------|---------|
| 创建任务 | `from zephyr.db.task_repo import TaskRepository; repo = TaskRepository(); repo.create(task)` |
| 状态转换 | `repo.transition(task_id, TaskStatus.IN_PROGRESS)` |
| 原子认领 | `repo.claim_next(batch_id, worker_id)` |
| 超时回收 | `repo.recover_stale_claims(batch_id, timeout_minutes=30)` |
| 批量进度 | `repo.batch_progress(batch_id)` |
| 蓝图拆解 | `from zephyr.core.blueprint_decomposer import BlueprintDecomposer; BlueprintDecomposer(repo).decompose(path, out_dir)` |
| MCP 接口 | `from zephyr.mcp.task_manager_server import TaskManagerServer` |
| 门禁检查 | `repo.transition(task_id, to_status, gate_check=True)` |
| 数据库路径 | `data/databases/governance.db` |
| 回滚验证 | `python scripts/rollback.py preflight` |
| 蓝图-代码同步 | `python scripts/governance/d5_architecture/validate_blueprint_code_sync.py` |
| 依赖对齐验证 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-TASK_SYSTEM` |

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `db_path` | str | `data/databases/governance.db` | SQLite 数据库路径 |
| `busy_timeout` | int | 5000 | SQLite 并发写入等待(ms) |
| `wip_limit` | int | 5 | 同时 IN_PROGRESS 上限 |
| `wip_p01_limit` | int | 2 | P0/P1 同时 IN_PROGRESS 上限 |
| `max_retries` | int | 3 | 最大重试次数 |
| `retry_backoff_base` | int | 60 | Retry 退避基数(秒) |
| `circuit_breaker_threshold` | int | 3 | 断路器连续失败触发次数 |
| `circuit_breaker_cooldown` | int | 300 | 断路器冷却期(秒) |
| `suspended_timeout_hours` | int | 24 | SUSPENDED 自动 FAILED 超时 |
| `claim_timeout_minutes` | int | 30 | BatchOrchestrator 认领超时 |
| `emergency_gate_set` | list | `[G0, G6, G7]` | 紧急模式保留门禁 |
| `quality_regression_threshold` | float | 0.15 | 质量退化检测偏差阈值 |
| `context_window_usage_limit` | float | 0.8 | 上下文窗口使用上限比例 |
| `saga_compensation_step_timeout` | int | 30 | Saga 补偿单步超时(秒) |

### §16.10 故障与操作手册

| # | 故障现象 | 根因 | 排查步骤 | 修复方式 |
|---|---------|------|---------|---------|
| 1 | `OperationalError: database is locked` | SQLite busy_timeout 耗尽 | 检查是否有长事务未提交 | 增大 busy_timeout / 减少并发写入 / 检查未关闭连接 |
| 2 | `task_id 重复 (409)` | 同一 namespace 下 SEQ 冲突 | `SELECT task_id FROM tasks WHERE task_id LIKE 'NAMESPACE-%'` | 确认 task_repo.create() 的 SEQ 自增逻辑 |
| 3 | 状态转换被拒 (422) | 门禁未通过或非法转换路径 | 读取 GateCheckResult.violations | 按 violations 逐项修复 |
| 4 | 蓝图拆解产出 0 任务 | §16 施工指引缺失或格式错误 | 检查蓝图 `doc_type=blueprint` + §16 存在性 | 补充 §16 施工指引 |
| 5 | WIP 超限 dispatch 被拒 | IN_PROGRESS 任务数 ≥ 5 | `repo.list_tasks(status=IN_PROGRESS)` | 等待任务完成或调整 WIP 上限 |
| 6 | 并发文件冲突 | 两个 IN_PROGRESS 任务的 allowed_touch 有交集 | 检查所有 IN_PROGRESS 任务的 allowed_touch | 调整任务范围或串行执行 |
| 7 | 上下文窗口溢出 | upstream_files + prompt 超过 context_window_limit * 0.8 | 检查 estimated_context_tokens | M2 裁剪策略 / 拆分任务 |
| 8 | 断路器打开 | 同一模型连续失败 ≥ 3 次 | 检查 circuit_breaker_open 字段 | 等待冷却 / 切换 fallback_model |
| 9 | Saga 补偿失败 | undo_command 执行异常 | 检查 DeadLetterEntry | Owner 手动处理 |
| 10 | 认领超时未回收 | worker 崩溃后 claimed_at 未释放 | `repo.recover_stale_claims(batch_id)` | 自动回收 / 手动清理 |
| 11 | .md 与 SQLite 不同步 | transition() 成功但 _taskcard_to_md() 失败 | 对比 .md 文件与 SQLite 记录 | 重新执行 transition 或手动同步 |
| 12 | 迁移脚本执行失败 | PRAGMA user_version 与脚本版本不匹配 | 检查 `PRAGMA user_version` 输出 | 修复迁移脚本 / 手动设置版本号 |


#### §16.11.1 数据库迁移 SOP

| # | 步骤 | 命令/操作 | 验证 | 回退 |
|---|------|---------|------|------|
| 1 | 备份当前数据库 | `cp data/task_system.db data/task_system.db.bak.$(date +%Y%m%d%H%M%S)` | 文件存在且大小 > 0 | — |
| 2 | 检查当前版本 | `python -c "import sqlite3; c=sqlite3.connect('data/task_system.db'); print(c.execute('PRAGMA user_version').fetchone())"` | 输出版本号 | — |
| 3 | 执行迁移 | `python scripts/migrate_task_db.py --target <version>` | `PRAGMA user_version` = 目标版本 | `cp data/task_system.db.bak.* data/task_system.db` |
| 4 | 验证数据完整性 | `python scripts/migrate_task_db.py --verify` | exit 0 | 回退步骤 3 |
| 5 | 清理备份（72h 后） | `rm data/task_system.db.bak.*` | 文件已删除 | — |

> ⚠️ 迁移 MUST 在无 IN_PROGRESS 任务时执行。`repo.list_tasks(status=IN_PROGRESS)` 返回空列表才能开始。

#### §16.11.2 紧急操作 SOP

| # | 场景 | 操作 | 命令 | 事后处理 |
|---|------|------|------|---------|
| 1 | SQLite 锁死 | 强制解锁 | `python scripts/lock_files.py cleanup` + 重启 task_manager_server | 检查数据完整性 |
| 2 | 批量任务卡死 | 批量回退到 CREATED | `repo.batch_reset(batch_id, target_status=CREATED)` | 24h 内根因分析 |
| 3 | 认领泄漏 | 回收超时认领 | `repo.recover_stale_claims(batch_id, timeout_minutes=30)` | 检查 worker 健康状态 |
| 4 | 紧急热修复模式 | 启用 emergency_mode | `task_repo.set_emergency_mode(True, reason="...", owner_approved=True)` | 24h 内补审计 + 关闭 emergency_mode |

> ⚠️ 紧急操作 MUST 有 Owner 批准记录（`owner_approved=True`）。无批准执行 = 越权。

### §16.12 并发操作模型

| # | 冲突场景 | 冲突类型 | 解决策略 | 实现机制 | 一致性保证 |
|---|---------|---------|---------|---------|-----------|
| 1 | 多 Worker 认领同一任务 | Write-Write | 原子认领（先到先得） | `UPDATE tasks SET claimed_by=? WHERE task_id=? AND claimed_by IS NULL` | 最多 1 个 Worker 认领成功 |
| 2 | 同一文件被多任务修改 | Write-Write | 文件锁 + allowed_touch 互斥检查 | `pre_write_gate.py` 检查 IN_PROGRESS 任务的 allowed_touch 交集 | 0 文件冲突 |
| 3 | WIP 超限 | Capacity | 拒绝新 dispatch + 排队 | `repo.list_tasks(status=IN_PROGRESS)` 计数 vs WIP_LIMIT | WIP ≤ LIMIT |
| 4 | 批量调度部分失败 | Partial-Write | Saga 补偿——已成功的步骤执行 undo_command | `BatchOrchestrator.execute_batch()` 内置 Saga | 全成功或全回滚 |
| 5 | 认领超时未释放 | Orphan-Lock | 定时回收——claimed_at 超时后自动释放 | `repo.recover_stale_claims()` 定时任务 | 无永久锁 |

> ⚠️ 冲突策略 #1（原子认领）依赖 SQLite `UPDATE ... WHERE ... IS NULL` 的原子性。SQLite WAL 模式下此操作为原子操作。非 WAL 模式下 MUST 开启 WAL：`PRAGMA journal_mode=WAL`。

---

## §17 容量升级附录

### §17.1 容量基线

> → 见本蓝图 §5.2 容量估算

### §17.2 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.8.0 | 1 | 基线 | 当前设计 | ✅ |
| v0.9.0 | 1 | 模板升级 | §0前移+§7/§15删除+§10拆分+铁律#13-#15+压缩 | ✅ |
| v1.0.0 | 2 | 容量升级 | Multi-Worker Batch Coordination | ❌ 待施工 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-INF006-01 | TaskCard 继承 shared/schemas.py Task | A:独立模型/B:继承Task | B | KBG-0040 Pydantic V2 强制 + SSoT 唯一 | 2026-05-02 |
| 2 | D-INF006-02 | task_id 格式 {NAMESPACE}-{SEQ} | A:UUID/B:NAMESPACE-SEQ | B | KBG-001/SRC-042——自文档 | 2026-05-02 |
| 3 | D-INF006-03 | SQLite 作为唯一持久化层 | A:文件系统/B:SQLite/C:PostgreSQL | B | KBG-0030——零依赖+单机部署 | 2026-05-02 |
| 4 | D-INF006-04 | File-as-Task 范式 | A:纯任务/B:文件-任务1:1 | B | KBG-0038——双向映射 | 2026-05-02 |
| 5 | D-INF006-05 | Saga 补偿事务替代全量快照 | A:全量快照/B:Saga补偿 | B | 盲点 #32——精细补偿优于粗暴回退 | 2026-05-05 |
| 6 | D-INF006-06 | 模型快照锁定 | A:逻辑名/B:dated snapshot | B | 盲点 #37——可复现性 | 2026-05-05 |
| 7 | D-INF006-07 | BatchOrchestrator 原子认领 | A:checkpoint.json/B:SQLite UPDATE RETURNING | B | 并发安全+依赖感知+超时回收 | 2026-05-07 |
| 8 | D-INF006-08 | M7 审查使用 GLM | A:DeepSeek/B:GLM | B | GLM 幻觉率 4% vs DeepSeek 94% | 2026-05-02 |

---

## 术语表

| 术语 | 定义 |
|------|------|
| TaskCard | 任务卡模型——继承 `shared/schemas.py` Task（31字段）+ 扩展执行层字段（31字段），共62字段。SQLite 真源 + .md 伴读双轨 |
| TaskNamespace | 任务编号命名空间枚举：KB 决策记录/CP/KE/STD/DW/SRC/OPS/DM。定义于 `gates/task_types.py`，与 `_TASK_ID_PATTERN` 同文件动态生成，task_id 格式 `{NAMESPACE}-{SEQ}` |
| GateLevel | 门禁等级枚举：G0(创建)/G1(指派)/G2(前置)/G3(执行)/G4(产出)/G5(审计)/G6(关闭)/G7(完整度) |
| AISelfGovernanceLevel | AI 自治边界五级枚举：supervised/semi_autonomous/autonomous/full_auto/emergency_only |
| PipelineOrchestrator | 管线调度器——A区(M1-M5 生产)+B区(M6-M11 审计)+C区(脚本系统 12维度) |
| BlueprintDecomposer | 蓝图拆解器——从蓝图 §16 施工指引拆解为 TaskCard，写入 task_repo(SQLite)+.md 同步 |
| BatchOrchestrator | 批量编排器——10+ AI Session 并行认领任务，基于 SQLite `UPDATE RETURNING` 原子认领 |
| TaskLifecycleManager | 任务生命周期管理器——包装 task_repo.py 的10态状态机 + G0-G7 门禁 + .md 同步 |
| TaskManagerServer | MCP 接口服务器——15 Tool 接口（含 claim_task/mark_task_done/mark_task_failed/batch_progress/list_dependents/write_draft/commit_draft/list_drafts/discard_draft），数据真源为 SQLite |
| diff-plan | 结构化变更计划——P0/P1 任务强制要求，M2 验证后 M3 才写入 |
| Saga 补偿事务 | 多步骤任务失败时逆序执行 undo_command 的补偿模式。补偿失败→DeadLetter+通知 |
| QualityBaseline | 模型输出质量基线——M7 完成后对比，偏差>15% 触发 QualityRegressionAlert |
| FailurePattern | 失败模式——自动匹配已知失败模式并应用 mitigation，匹配失败时创建新 Pattern |
| WIP | 在制品(Work In Progress)——同时 IN_PROGRESS 的任务数，上限 ≤ 5（P0/P1 ≤ 2） |
| SLAWatchdog | SLA 时限看门狗——每小时扫描超 SLA 任务，自动升级优先级+通知 Owner |
| ContextCache | 跨 Session 上下文缓存——key=sha256(task_id+upstream_files)，hash 匹配则复用 summary |
| MTH-013 | 路径合规创建原则——AI 不得自主决定目录层级，所有路径可追溯到索引 |
| MTH-012 | 涌现式设计原则——蓝图 §16 必须极度详细，unassigned_items >10%→拒绝拆解 |

---

## 已知问题与盲点登记

> 从蓝图特有：盲点审计与路线图（48盲点八大类）提取的未解决问题摘要。

| # | 盲点 | 严重性 | 规划版本 | 约束编号 |
|---|------|:------:|:-------:|---------|
| 1 | Hook/事件系统 | 中 | v0.5.0 | 待新增 |
| 2 | 主动任务队列/轮询 | 中 | v0.5.0 | 待新增 |
| 3 | 全链路 Trace（M1-M11 每步耗时） | 高 | v0.5.0 | 待新增 |
| 4 | Owner 通知/告警 | 极高 | v0.5.0 | 待新增 |
| 5 | API 成本预算和告警 | 中 | v0.5.0 | 待新增 |
| 6 | CLI 摘要视图（`zalpha status`） | 极高 | v0.5.0 | 待新增 |
| 7 | 失败模式自动匹配 | 高 | v0.5.0 | 待新增 |
| 8 | 零配置启动（`zalpha init`） | 高 | v0.5.0 | 待新增 |
| 9 | Dogfooding（系统自己不用自己） | 极高 | v0.5.0 | 待新增 |
| 10 | 渐进式增强施工模式 | 中 | v0.5.0 | 待新增 |
| 11 | AI 维护手册（Troubleshooting Playbook） | 高 | v0.5.0 | 待新增 |
| 12 | 意图→蓝图自动化入口（DraftAssistant） | 高 | v0.5.0 | 待新增 |
| 13 | KMS 知识管理接口契约 | 中 | v0.5.0 | 待新增 |
| 14 | M1-M11 插件化 | 中 | v0.5.0 | §14 #14 |
| 15 | 任务系统自身健康检查和漂移检测 | 极高 | v0.5.0 | §14 #13 |
| 16 | Prompt 版本化+回退 | 极高 | v0.5.0 | §5.1 #21 |
| 17 | Saga 补偿事务 | 极高 | v0.5.0 | §5.1 #22 |
| 18 | 模型质量退化检测 | 极高 | v0.5.0 | §5.1 #23 |
| 19 | SLA 时限自动升级 | 高 | v0.5.0 | §5.1 #24 |
| 20 | AI 跨任务知识隔离 | 高 | v0.5.0 | §5.1 #26 |
| 21 | 紧急热修复快速通道 | 高 | v0.5.0 | §5.1 #27 |
| 22 | 模型快照锁定 | 高 | v0.5.0 | §5.1 #28 |
| 23 | 多文件原子写入 | 中 | v0.5.0 | §5.1 #29 |
| 24 | 依赖新鲜度级联感知 | 中 | v0.5.0 | §5.1 #30 |
| 25 | 任务系统组件降级运行 | 中 | v0.5.0 | §5.1 #31 |
| 26 | 跨 Session 思考态持久化 | 高 | v0.5.0 | §5.1 #25 |
| 27 | SQLite Schema 迁移框架 | 极高 | v0.6.0 | §5.1 #32 |
| 28 | 执行时前置漂移校验 | 高 | v0.6.0 | §5.1 #34 |
| 29 | 向后兼容性冲击分析 | 高 | v0.6.0 | §5.1 #35 |
| 30 | 中执行自适应重规划 | 中 | v0.6.0 | §5.1 #36 |
| 31 | 输出范围蔓延检测 | 中 | v0.6.0 | §5.1 #37 |
| 32 | 跨 Session 上下文复用 | 低 | v0.6.0 | §5.1 #38 |
| 33 | 取消安全清理协议 | 中 | v0.6.0 | §5.1 #33 |

---

## 成熟度声明

| 维度 | 等级 | 说明 |
|------|:----:|------|
| 架构完整性 | L3-Defined | 组件架构(§3)+数据流(§3.2)+状态机(§3.3)+接口契约(§4)完整定义 |
| 接口稳定性 | L3-Defined | §4.6 契约版本兼容性矩阵已定义，破坏性变更需 Owner 审批 |
| 测试覆盖 | L2-Managed | 单元测试+集成测试+并发测试策略已定义(§9)，覆盖率目标 ≥80% |
| 可观测性 | L2-Managed | events 表记录状态转换，M1-M11 Trace 规划于 v0.5.0 |
| 自愈能力 | L2-Managed | 断路器+Retry退避+Saga补偿已设计，FailurePattern 匹配规划于 v0.5.0 |
| 文档完整性 | L4-Quantified | 蓝图1785+行，48盲点全量登记，6个v4.0新增章节 |
| 安全防护 | L2-Managed | PermissionGuard+门禁验证+日志脱敏(§8)，注入/暴露检查规划于 v0.5.0 |
| 运维就绪 | L1-Initial | CLI 摘要视图/零配置启动/Dogfooding 规划于 v0.5.0 |

**综合成熟度**：L2-Managed（设计完成，核心功能已实现，可观测/自愈/运维能力待 v0.5.0 补齐）

---

## 版本演进路线图

| 版本 | 日期 | 核心变更 | 盲点覆盖 | 状态 |
|------|------|---------|---------|:----:|
| v0.2.0 | 2026-05-01 | 初始设计——独立 TaskCard 模型 | 0/48 | 已废弃 |
| v0.3.0 | 2026-05-02 | TaskCard 继承 Task + task_id 格式统一 | 0/48 | 已废弃 |
| v0.3.2 | 2026-05-03 | 合并 MOD-INF-003/004 + 场外草稿迁入 | 0/48 | 已废弃 |
| v0.4.0 | 2026-05-05 | 盲点审计第一轮(#1-#25) + 16个已解决 | 16/48 | 已废弃 |
| v0.5.0 | 规划中 | 盲点审计第二轮(#31-#41) + 可观测/自愈/运维 | 41/48 | 待施工 |
| v0.6.0 | 规划中 | 盲点审计第三轮(#42-#48) + Schema迁移/取消安全 | 48/48 | 待施工 |
| v0.8.0 | 2026-05-10 | 基线——模板v3.0合规 | 16/48 | 已发布 |
| v0.9.1 | 2026-05-15 | 回填OCP扩展点+施工步骤内容变更+依赖对齐+规格化压缩 | 16/48 | 已发布 |
| v0.9.2 | 2026-05-16 | 修复管线调度委托+SSoT声明+自动化触发+概念重叠声明+施工步骤回填 | 16/48 | 已发布 |
| v0.9.3 | 2026-05-16 | 修复§6.1可观测性+§10.6依赖链风险评级+§11 consumer_min+验收版本号 | 16/48 | 已发布 |
| v0.9.4 | 2026-05-16 | 修复3 FAIL+1 WARN：可观测性规格+依赖链风险评级+产出物consumer_min+版本号一致性 | 16/48 | 当前 |
| v1.0.0 | 规划中 | Multi-Worker Batch Coordination + 全部盲点解决 | 48/48 | 待施工 |

---

## 自检与闭合清单

| # | 验证项 | 验证方法 | 通过标准 | 状态 |
|---|--------|---------|---------|:----:|
| 1 | 蓝图结构完整性 | 检查 §0-§18 + 术语表/已知问题/自检与闭合清单/成熟度/路线图 均存在 | 所有必需章节存在且非空 | ☐ |
| 2 | 代码-蓝图双向对齐 | `validate_blueprint_code_sync.py` + §0 代码文件清单 | §0.1 所有已实现文件存在 + §4 接口签名与代码一致 | ☐ |
| 3 | 盲点闭环率 | 统计盲点审计中"已解决"占比 | 已解决 ≥ 33%（16/48），未解决均有规划版本 | ☐ |
| 4 | 依赖声明完整性 | `validate_path_alignment.py --blueprint MOD-TASK_SYSTEM` | §10.1 每个依赖在 registry 中有对应条目 | ☐ |
| 5 | 施工完成度 | §16.5 施工完成标准逐项检查 | 所有产出物存在+非空+§0对齐 | ☐ |

| # | 检查项 | 验证方式 | 通过标准 | 结果 |
|---|--------|---------|---------|:----:|
| 1 | frontmatter 字段完整 | 逐字段检查 | module_id/title/version/layer/owner/status/depends_on/stability 均有值 | ☐ |
| 2 | §0 代码对齐验证与实际代码一致 | `ls` + `grep` 逐项核对 | §0.1 存在性标记与磁盘一致 | ☐ |
| 3 | §4 接口签名与代码一致 | `grep "class/|def" src/zephyr/governance/task_repo.py` | 蓝图中的类名/方法名在代码中存在 | ☐ |
| 4 | §10 依赖声明与 registry 对齐 | `validate_path_alignment.py` | 依赖项在 registry 中有对应条目 | ☐ |
| 5 | §11 产出物路径与 GOV-DOC-002 一致 | 逐路径核对 | 所有路径符合目录结构标准 | ☐ |
| 6 | §14 风险缓解策略可执行 | 逐项检查缓解策略 | 每个风险有具体缓解措施而非"待定" | ☐ |
| 7 | §16 施工步骤可执行 | 逐步骤检查验证命令 | 每步有验证命令+验收标准 | ☐ |
| 8 | 盲点审计无遗漏 | 统计盲点总数 | 48 盲点全量登记，无"待补充" | ☐ |
| 9 | 铁律/约束无模糊词 | Grep "待定/建议/按需/TBD" | 蓝图中无模糊词 | ☐ |
| 10 | 蓝图自包含 | 逐章节检查关键信息 | 无"详见XX"而无实际内容 | ☐ |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须完整可定位**——优先使用项目根相对路径+正斜杠（如 `docs/03_modules/...`） | 文件创建到错误位置 / Python SyntaxError |
| 2 | **必备链接不可省略**——即使与前序文档重复也必须完整列出 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程、不保存未选方案 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | 断链——旧引用找不到文件；或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | 执行漂移——AI 自行决定，可能选错 |
| 9 | **蓝图必须自包含**——关键信息不能只写"详见XX" | 信息缺失——AI 缺少关键上下文 |
| 10 | **删除文件必须遵守安全删除协议**——禁止直接删除任何文件 | 永久丢失——无法恢复 |
| 11 | **construction_progress 必须与代码实际状态一致** | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
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

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整路径（相对优先） | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| 1 | MOD-INF-003 任务卡KMS蓝图 | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` | 覆盖型 | 本蓝图 | 已标记 deprecated→物理删除 |
| 2 | MOD-INF-004 双管线蓝图 | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` | 覆盖型 | 本蓝图 | 已标记 deprecated→物理删除 |
| 3 | v0.2.0 TaskCard 模型 | `src/zephyr/shared/shared_services/models.py` | 覆盖型 | v0.3.0 TaskCard | 重写对齐新契约 |

### 删除铁律

| # | 铁律 |
|---|------|
| 1 | 禁止蓝图阶段物理删除任何文件 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 |
| 3 | 物理删除只能在 stable 搬入阶段执行 |
| 4 | 物理删除必须人类确认 |
| 5 | "宁可慢，不可漏" |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用。永久保留在蓝图中。

| # | 文件 | module_id | 版本 | 完整路径（相对优先） | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 2.0.0+ | `docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml` | §7——task_id/语义28/追踪3/Task共31/状态机 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | 2.6.0+ | `docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 脚本系统蓝图 | MOD-INF-005 | 3.0.0+ | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` | 审计消费方 |
| 5 | 任务卡操作指南 | GOV-TASK-001 | 3.0.0+ | `docs/01_policies_and_standards/governance/task/task-card-standard.md` | 正文结构与门禁速查 |
| 6 | 任务生命周期标准 | GOV-TASK-004 | 2.0.0+ | `docs/01_policies_and_standards/governance/task/task-lifecycle-standard.md` | 取消权限、优先级裁决 |
| 7 | 任务关闭标准 | GOV-TASK-005 | 1.1.0+ | `docs/01_policies_and_standards/governance/task/task-closure-standard.md` | 关闭三步法 |
| 8 | Task Pydantic 模型 | shared/schemas.py | 现有代码 | `src/zephyr/shared/schemas.py` | Task 结构定义 SSoT |
| 9 | 模型基准排名 | REG-LLM-001 | 1.1.0+ | `docs/01_policies_and_standards/_registry/catalogs/frontier_llm_benchmark_ranking.yaml` | execution_model 数据依据 |
| 10 | 模型路由策略 | GOV-AI-002 | 2.0.0+ | `docs/01_policies_and_standards/governance/ai/model-routing-policy.md` | 任务分配决策树 |
| 11 | AGENTS.md 项目基准 | — | 4.6.1+ | `AGENTS.md` | 项目全局规则 |
| 12 | Task 模型基座 | shared/schemas.py | 现有代码 | `src/zephyr/shared/schemas.py` | Task 31 字段——TaskCard 继承 |
| 13 | task_repo.py | — | 现有代码 | `src/zephyr/governance/task_repo.py` | SQLite CRUD + 10状态机——数据层真源 |
| 14 | 任务卡元注册表 | task-card-meta-registry | V-13 | `docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.md` | 迁移状态追踪 |

---

## 项目中已有类似功能

> **时态属性**：本节属于**施工声明**——防重复检查。永久保留在蓝图中。

| # | 已有模块/文件 | 完整路径（相对优先） | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-INF-003（旧蓝图层） | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` | 任务卡制度+KMS体系 | deprecated——已被本蓝图合并 |
| 2 | MOD-INF-004（旧双管线） | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` | 双管线流程+M模块 | deprecated——已被本蓝图合并 |
| 3 | Task 模型（shared/schemas.py） | `src/zephyr/shared/schemas.py` | 语义28+追踪3=31 字段 | ✅ 可复用——本蓝图 TaskCard 继承此模型 |
| 4 | task_repo.py（SQLite CRUD） | `src/zephyr/governance/task_repo.py` | 创建/查询/更新/删除/状态转换 | ✅ 可复用——本蓝图数据层使用此代码 |

---

## 涉及的文件范围

> **时态属性**：本节属于**施工声明**——防范围漂移。永久保留在蓝图中。

| # | 文件/目录 | 完整路径（相对优先） | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 本蓝图 | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` | 真源 | 重写 v0.9.4 |
| 2 | Change Folder | `docs/03_modules/_domain_infrastructure_runtime/task_system/changes/` | 新建 | 存放任务卡 .md 文件 |
| 3 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | 修改 | 更新 MOD-TASK_SYSTEM 条目 |
| 4 | Task 模型基座 | `src/zephyr/shared/schemas.py` | 依赖 | TaskCard 继承其 Task 类 |
| 5 | task_repo.py | `src/zephyr/governance/task_repo.py` | 依赖 | 数据层真源 |
| 6 | core/models.py | `src/zephyr/shared/shared_services/models.py` | 重写 | 对齐到 shared/schemas.py Task 继承 |
| 7 | blueprint_decomposer.py | `src/zephyr/shared/shared_services/blueprint_decomposer.py` | 重写 | 输出改为 task_repo(SQLite) + .md |
| 8 | task_manager_server.py | `src/zephyr/integration/mcp/task_manager_server.py` | 重写 | 接入 task_repo(SQLite) 真源 |
| 9 | task_completion_gate.py | `src/zephyr/governance/rule_enforcement/task_completion_gate.py` | 读取 | 需同步 G7 门禁 |
| 10 | metadata_registry.yaml | `docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml` | 读取 | §7 字段真源 |
| 11 | task-card-meta-registry.md | `docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.md` | 修改 | 更新迁移状态 |

---

## 1. 已实现代码完整路径索引

> **蓝图-代码同步强制约定（见 AGENTS.md §7 代码规范）**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 任务系统——v0.3.0融合最优，experimental待重写

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/infrastructure/shared_services/adaptation/execution_tuner.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/adaptation/prompt_version_manager.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/blueprint_code_sync.py` | ✅ 已实现 | |
| `src/zephyr/shared/shared_services/blueprint_decomposer.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/compensation/saga_compensator.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/context_engine.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/dependency/dependency-graph.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/draft/draft_assistant.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/events/event_bus.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/events/event_reactor.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/events/event_store.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/events/hook_dispatcher.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/healthcheck_service.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/impact/impact_propagator.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/impact/llm_impact_analyzer.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/knowledge/ke_linker.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/knowledge/ke_structurer.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/knowledge/kms_interface.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/lifecycle/scope_guard.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/lifecycle/task_lifecycle_manager.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/maintenance/autonomy_monitor.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/maintenance/dogfooding.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/maintenance/handbook.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/maintenance/zero_config.py` | ✅ 已实现 | |
| `src/zephyr/shared/shared_services/models.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/observability/cli_summary.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/observability/cost_tracker.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/observability/failure_matcher.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/observability/notifier.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/observability/trace_decorator.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/quality/quality_monitor.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/queue/task_queue.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/queue/task_scheduler.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/reliability/circuit_breaker.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/reliability/context_guard.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/reliability/diff_planner.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/reliability/retry_handler.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/session/session_boundary.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/session/session_continuity.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/session_continuity.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/sla/sla_monitor.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/shared_services/sync/blueprint_code_sync.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/backpressure_manager.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/circuit_breaker_manager.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/cost_tracker.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/ct_pipe_routing.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/dead_letter_queue.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/layer_consumer_registry.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/layer_router.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/llm_gateway.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/benchmark_suite.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/capability_passport.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/cli.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/deepseek_v4_chat.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/exam_orchestrator.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/exam_test_cases.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/model_discovery.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/profiler.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/results_writer.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/model-profiler/task_model_learner.py` | ✅ 已迁移至顶层包 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/model_router.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/models.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_agent_bridge.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_lock.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/pipeline_roadmap.py` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/preemption_manager.py` | ✅ 已实现 | |
| `src/zephyr/pipeline/route-manifest.yaml` | ✅ 已实现 | |
| `src/zephyr/pipeline/routemanifest.yaml` | ✅ 已实现 | |
| `src/zephyr/infrastructure/runtime_integration/pipeline/routing_plugins.py` | ✅ 已实现 | |
| `src/zephyr/governance/task_repo.py` | ✅ 已实现 | |
| `src/zephyr/data/persistence/sqlite_schema.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/task_manager_server.py` | ✅ 已实现 | |
| `src/zephyr/governance/rule_enforcement/task_completion_gate.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/test_task_repo.py` | ✅ 已实现 | |
| `tests/test_sqlite_schema.py` | ✅ 已实现 | |
| `tests/test_mcp_servers.py` | ✅ 已实现 | |
| `tests/test_pipeline_orchestrator.py` | ✅ 已实现 | |
| `tests/test_task_completion_gate.py` | ✅ 已实现 | |
| `tests/adversarial/test_task_system_red_team.py` | ✅ 已实现 | |

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

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 任务系统全链路架构 | **本文档 §2.1** | 旧 MOD-INF-003/004（deprecated） |
| TaskCard 模型 | 基座：**shared/schemas.py Task + metadata_registry.yaml §7** / 扩展：**本文档 §4.2.1** | core/models.py（派生） |
| task_id 格式 | **metadata_registry.yaml §7.10** | — |
| 10 态状态机 + SUSPENDED | **task_repo.py** | — |
| G0-G7 门禁系统 | **本文档 §4.2.1 GateLevel enum** | — |
| AI 双管线 M1-M11 模块分工 | **本文档 §16.3 步骤6** | — |
| 蓝图→任务卡拆解算法 | **本文档 §4.1.1** | — |
| AI 自治边界五级枚举 | **本文档 §4.2.1 AISelfGovernanceLevel** | — |
| 盲点审计与路线图 | **本文档 蓝图特有：盲点审计** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-005 脚本系统蓝图 | §4 接口契约、§10 依赖关系 |
| Tier 1 | GOV-TASK-004 任务生命周期 | §4.2.1 TaskCard 模型、状态机 |
| Tier 2 | PipelineOrchestrator | §4.1.3 调度接口 |
| Tier 2 | TaskManagerServer (MCP) | §4.5 MCP 接口 |
| Tier 3 | core/models.py | §4.2.1 数据模型 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 |
| 修改 construction_progress | 下游更新依赖状态 | 更新集成测试 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |

---

## 蓝图特有章节

### 蓝图特有：盲点审计与路线图（48 盲点八大类）

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：48 个盲点是任务系统特有的深度审计产出
> 不可砍理由：砍掉 = AI 重复犯已发现的错误 + 路线图丢失

**审计范围**：蓝图 v0.3.2 → v0.6.0 + KBG-0038/0040/0030 + 全部核心源码 + 治理文档
**审计方法**：交叉对比 ① 专业机构（Jira/Linear/ServiceNow/Azure DevOps/Asana）+ ② 氛围编程社区 + ③ AI Agent 前沿（Temporal.io + Plan-and-Solve + LangChain）+ ④ LLMOps 2025-2026 + ⑤ 基础设施级可靠性 + ⑥ 数据持久化与运行时演化 + 1人+AI 维护特需 + 架构完整性

#### 盲点总览

| 大类 | 盲点数 | 覆盖领域 |
|------|:--:|------|
| A. 任务模型与生命周期 | 4 | 父子层级、Snapshot回滚、暂停恢复、Hook事件 |
| B. 依赖与调度 | 7 | 拓扑排序、并发冲突、优先级传播、WIP限制、任务队列、紧急通道、中执行自适应重规划 |
| C. AI 执行可靠性 | 11 | 幂等保证、diff-plan、超时清理、Retry退避、上下文溢出、断路器、知识隔离、模型快照、执行时前置校验、输出范围蔓延检测、中执行上下文漂移 |
| D. 可观测性与审计 | 5 | 全链路Trace、Owner通知、成本预算、CLI摘要、失败模式匹配 |
| E. 1人+AI 维护特需 | 8 | 零配置启动、Dogfooding、渐进增强、AI维护手册、AI自治边界、SLA老化升级、跨Session思考态、跨Session上下文复用 |
| F. 架构结构盲点 | 7 | 意图→蓝图、KMS契约、跨模块聚合、M模块插件化、自诊断、组件降级运行、向后兼容性冲击分析 |
| G. AI 质量管理与深度可靠性 | 4 | Prompt版本化+回退、Saga补偿事务、模型质量退化检测、多文件原子写入 |
| H. 数据持久化与运行时演化 | 2 | SQLite Schema 迁移框架、任务取消安全协议 |

#### 盲点解决状态摘要

| 盲点# | 名称 | 严重性 | 解决状态 | 约束编号 |
|:--:|------|:--:|:--:|------|
| #1 | 父子任务层级 | 高 | ✅ 已解决 | §5.1 #10 |
| #2 | 可执行回滚Snapshot | 高 | ✅ 已解决 | §5.1 #15 |
| #3 | SUSPENDED暂停恢复 | 中 | ✅ 已解决 | §5.1 #20 |
| #4 | Hook事件系统 | 中 | 🔲 v0.5.0 | 待新增 |
| #5 | 依赖拓扑排序和死锁检测 | 极高 | ✅ 已解决 | §5.1 #18 |
| #6 | 文件级并发冲突检测 | 极高 | ✅ 已解决 | §5.1 #12 |
| #7 | 优先级链上传播 | 高 | ✅ 已解决 | §5.1 #19 |
| #8 | WIP限制 | 高 | ✅ 已解决 | §5.1 #11 |
| #9 | 主动任务队列 | 中 | 🔲 v0.5.0 | 待新增 |
| #10 | 幂等性强制保证 | 高 | ✅ 已解决 | §5.1 #17 |
| #11 | diff-plan结构化约束 | 高 | ✅ 已解决 | §5.1 #16 |
| #12 | 执行超时自动清理/回滚 | 高 | ✅ 已解决 | §14 #15 |
| #13 | 指数退避Retry策略 | 中 | ✅ 已解决 | §5.1 #15 |
| #14 | 上下文窗口溢出保护 | 极高 | ✅ 已解决 | §5.1 #13 |
| #15 | API断路器 | 高 | ✅ 已解决 | §5.1 #14 |
| #16 | 全链路Trace | 高 | 🔲 v0.5.0 | 待新增 |
| #17 | Owner通知告警 | 极高 | 🔲 v0.5.0 | 待新增 |
| #18 | API成本预算 | 中 | 🔲 v0.5.0 | 待新增 |
| #19 | CLI摘要视图 | 极高 | 🔲 v0.5.0 | 待新增 |
| #20 | 失败模式自动匹配 | 高 | 🔲 v0.5.0 | 待新增 |
| #21 | 零配置启动 | 高 | 🔲 v0.5.0 | 待新增 |
| #22 | Dogfooding | 极高 | 🔲 v0.5.0 | 待新增 |
| #23 | 渐进式增强施工模式 | 中 | 🔲 v0.5.0 | 待新增 |
| #24 | AI维护手册 | 高 | 🔲 v0.5.0 | 待新增 |
| #25 | Owner离线AI自治边界 | 极高 | ✅ 已解决 | §2.1 #9 |
| #26 | 意图→蓝图自动化入口 | 高 | 🔲 v0.5.0 | 待新增 |
| #27 | KMS知识管理接口契约 | 中 | 🔲 v0.5.0 | 待新增 |
| #28 | 跨Blueprint任务聚合 | 中 | ✅ 已解决 | §2.1 #11 |
| #29 | M模块插件化 | 中 | 🔲 v0.5.0 | §14 #14 |
| #30 | 任务系统自身健康检查 | 极高 | 🔲 v0.5.0 | §14 #13 |
| #31 | Prompt版本化+回退 | 极高 | 🔲 v0.5.0 | §5.1 #21 |
| #32 | Saga补偿事务 | 极高 | 🔲 v0.5.0 | §5.1 #22 |
| #33 | 模型质量退化检测 | 极高 | 🔲 v0.5.0 | §5.1 #23 |
| #34 | SLA时限自动升级 | 高 | 🔲 v0.5.0 | §5.1 #24 |
| #35 | AI跨任务知识隔离 | 高 | 🔲 v0.5.0 | §5.1 #26 |
| #36 | 紧急热修复快速通道 | 高 | 🔲 v0.5.0 | §5.1 #27 |
| #37 | 模型快照锁定 | 高 | 🔲 v0.5.0 | §5.1 #28 |
| #38 | 多文件原子写入 | 中 | 🔲 v0.5.0 | §5.1 #29 |
| #39 | 依赖新鲜度级联感知 | 中 | 🔲 v0.5.0 | §5.1 #30 |
| #40 | 任务系统组件降级运行 | 中 | 🔲 v0.5.0 | §5.1 #31 |
| #41 | 跨Session思考态持久化 | 高 | 🔲 v0.5.0 | §5.1 #25 |
| #42 | SQLite Schema迁移框架 | 极高 | 🔲 v0.6.0 | §5.1 #32 |
| #43 | 执行时前置漂移校验 | 高 | 🔲 v0.6.0 | §5.1 #34 |
| #44 | 向后兼容性冲击分析 | 高 | 🔲 v0.6.0 | §5.1 #35 |
| #45 | 中执行自适应重规划 | 中 | 🔲 v0.6.0 | §5.1 #36 |
| #46 | 输出范围蔓延检测 | 中 | 🔲 v0.6.0 | §5.1 #37 |
| #47 | 跨Session上下文复用 | 低 | 🔲 v0.6.0 | §5.1 #38 |
| #48 | 取消安全清理协议 | 中 | 🔲 v0.6.0 | §5.1 #33 |

#### 盲点详细登记

##### A. 任务模型与生命周期

###### 盲点 #1 — 缺少父子任务层级（Epic→Story→Sub-task）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `depends_on` 是扁平列表，无层级语义 |
| 为什么是盲点 | 蓝图拆解生成的 6 个 TASK-INF-XXXX 之间只有线性依赖，无法表达"这个大任务包含 5 个小任务"。父任务状态 = 聚合子任务状态是 Jira/Linear/Asana 的基线功能 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——TaskCard 新增 `parent_task_id: str /| None` + 父子状态聚合规则 |
| 约束编号 | §5.1 #10 |

###### 盲点 #2 — 缺少任务执行前 Snapshot / 可执行回滚

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `rollback_instructions` 是自由文本，AI 无法可靠执行 |
| 为什么是盲点 | bolt.new/Cursor/Replit Agent 都实现了 checkpoint→回退机制。自由文本回滚对 AI 来说不可执行 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——TaskCard 新增 `checkpoint_path: str /| None` + FAILED 时自动恢复 |
| 约束编号 | §5.1 #15 |

###### 盲点 #3 — 缺少 SUSPENDED 暂停/恢复状态

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 10 态状态机中没有暂停状态 |
| 为什么是盲点 | 1人+AI 场景下 Owner 可能中途暂停长任务、两个 AI session 之间需要交接。当前只能 FAILED→RETRY 再从头开始 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——状态机增加 SUSPENDED + `suspend_context_json` 字段 + 24h 自动超时 |
| 约束编号 | §5.1 #20 |

###### 盲点 #4 — 缺少 Hook/事件系统

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 状态变更后的行为硬编码在 PipelineOrchestrator 和 TaskRepository 中 |
| 为什么是盲点 | 无法声明式配置"状态变为 X 时自动做 Y"。所有联动逻辑散落在不同类的 `if status == X: do_Y()` 中 |
| 解决状态 | 🔲 **v0.5.0 规划**——引入 EventHook 声明式注册（`{trigger_status, action, module_id}`），替代硬编码 if-else |
| 约束编号 | 待新增 |

##### B. 依赖与调度

###### 盲点 #5 — 缺少依赖拓扑排序和死锁检测

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | `depends_on` 是扁平列表，无循环检测，无拓扑序 |
| 为什么是盲点 | A depends_on B, B depends_on A → 两个任务永远无法开始。没有检测意味着可能创建死锁而不自知 |
| 解决状态 | ✅ **已在本蓝图 §5.1 解决**——约束 #18：BlueprintDecomposer 必须输出拓扑序，检测循环依赖时拒绝拆解 |
| 约束编号 | §5.1 #18 |

###### 盲点 #6 — 缺少文件级并发冲突检测

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | 多个任务同时 IN_PROGRESS 且 `allowed_touch` 有交集时无警告 |
| 为什么是盲点 | AI session A 改了 `shared/schemas.py`，AI session B 也改同一文件——后者静默覆盖前者 |
| 解决状态 | ✅ **已在本蓝图 §5.1 解决**——约束 #12：dispatch() 前检查所有 IN_PROGRESS 任务的 allowed_touch 交集 |
| 约束编号 | §5.1 #12 |

###### 盲点 #7 — 缺少优先级在依赖链上的传播

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | B depends_on A，A=P0，B=P3 → B 按 P3 处理 |
| 为什么是盲点 | B 阻塞了 P0 的 A，B 应该有 P0 级别的紧急度。Jira/ServiceNow 都有"被阻塞的紧急任务提升其依赖项优先级"的逻辑 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——TaskCard 新增 `effective_priority` 计算字段（不改变 `priority`） |
| 约束编号 | §5.1 #19 |

###### 盲点 #8 — 缺少 WIP（在制品）限制

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 无限制同时 IN_PROGRESS 的任务数 |
| 为什么是盲点 | Kanban 方法论的核心——WIP 无上限 = 上下文碎片化 + 交付延迟 + 冲突频发。1人+AI 场景特别致命（AI 上下文窗口有限） |
| 解决状态 | ✅ **已在本蓝图 §5.1 解决**——约束 #11：WIP ≤ 5（P0/P1 ≤ 2） |
| 约束编号 | §5.1 #11 |

###### 盲点 #9 — 缺少主动任务队列/轮询

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 调度是被动的——Owner 调用 `dispatch()` |
| 为什么是盲点 | KBG-0036 Deferred Queue 提到了"轻量 SQLite 轮询 + Observer"，但 PipelineOrchestrator 中未体现。1人+AI 维护时 Owner 不在，需要自动从 READY 队列取任务 |
| 解决状态 | 🔲 **v0.5.0 规划**——实现 TaskQueue 后台轮询器：每 N 分钟扫描 READY 任务，AI 自治允许时自动 dispatch |
| 约束编号 | 待新增 |

##### C. AI 执行可靠性

###### 盲点 #10 — 幂等性没有强制保证

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `idempotent: bool` 字段存在但无任何代码检查 |
| 为什么是盲点 | 真正的幂等保证 = 执行前检查产物是否已存在且符合预期，存在则跳过。不实现等于假字段 |
| 解决状态 | ✅ **已在本蓝图 §5.1 解决**——约束 #17：执行前检查 downstream_outputs，幂等跳过 |
| 约束编号 | §5.1 #17 |

###### 盲点 #11 — 缺少 diff-plan 的结构化约束

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | M3 直接生成代码写入文件，依赖 M7 事后审查 |
| 为什么是盲点 | Cursor/v0 的实践表明：AI 先产出 diff plan（"我要改哪些文件，怎么改"）→ 人类/AI 审核通过 → 再实际写入——比"生成完再审查"可靠得多 |
| 解决状态 | ✅ **已在本蓝图 §5.1 解决**——约束 #16：P0/P1 强制 `diff_plan_required=True`，M2 验证 ExecutionPlan → M3 写入 |
| 约束编号 | §5.1 #16 |

###### 盲点 #12 — 缺少执行超时后的自动清理/回滚

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 超时检查存在，但超时后任务仍是 IN_PROGRESS，已修改的文件处于半完成状态 |
| 为什么是盲点 | 超时不自动处理 → Owner 需要手动 FAILED + 手动回滚 → 1人+AI 维护不可接受 |
| 解决状态 | ✅ **已在本蓝图 §14 解决**——风险 #15：超时→自动 FAILED + checkpoint_path 恢复 + 通知 Owner |
| 约束编号 | §14 #15 |

###### 盲点 #13 — 缺少指数退避 Retry 策略

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | RETRY→IN_PROGRESS 是手动调用，无自动退避 |
| 为什么是盲点 | 专业系统（AWS SDK/Retry Pattern）的标准做法：指数退避（1→2→4→8min）+ 最大重试次数 + 不可重试错误分类 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——TaskCard 新增 `retry_count`/`max_retries`/`retry_backoff_seconds` + §5.1 #15 |
| 约束编号 | §5.1 #15 |

###### 盲点 #14 — 缺少上下文窗口溢出保护

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | 无任何检查 upstream_files + applicable_rules + pipeline prompt 的总 token |
| 为什么是盲点 | DeepSeek 128K 窗口。5 个大 upstream_files + pipeline system prompt 很容易溢出。溢出 = 截断 = 关键信息丢失 = 你以为 AI 读了实际没读——比不读更危险 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——TaskCard 新增 `estimated_context_tokens`/`context_window_limit` + §5.1 #13 + M2 裁剪策略 |
| 约束编号 | §5.1 #13 |

###### 盲点 #15 — 缺少 API 断路器（Circuit Breaker）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | fallback_model 存在但需手动切换 |
| 为什么是盲点 | DeepSeek API 不稳定是常态。自愈系统的基线要求：连续失败 N 次 → 自动熔断 → 期间全部路由 fallback → 半开探测恢复 → 关闭熔断 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——TaskCard 新增 `circuit_breaker_open` + §5.1 #14 + §14 #4 |
| 约束编号 | §5.1 #14 |

##### D. 可观测性与审计

###### 盲点 #16 — 缺少全链路 Trace（M1-M11 每步耗时）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | events 表只记录状态转换，无 M 模块粒度 |
| 为什么是盲点 | 1人+AI 维护时必须能回答："这个任务为什么花了 45 分钟？哪一步最慢？" 没有 Trace = 无法优化 |
| 解决状态 | 🔲 **v0.5.0 规划**——events 表增加 `module_id`/`duration_ms`/`token_consumed` 字段，PipelineOrchestrator 每个 M 模块执行后记录 TraceEvent |
| 约束编号 | 待新增 |

###### 盲点 #17 — 缺少 Owner 通知/告警

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | P0 卡住 → 没有任何通知机制 |
| 为什么是盲点 | 1人+AI 维护场景下 Owner 不可能一直盯着屏幕。P0→超 SLA→连续失败→Owner 必须被动收到通知 |
| 解决状态 | 🔲 **v0.5.0 规划**——引入 Notifier 抽象层：日志告警（当前可用）+ 飞书 Webhook + 桌面 Toast。P0 阻塞 ≥ 1h → 自动通知 |
| 约束编号 | 待新增 |

###### 盲点 #18 — 缺少 API 成本预算和告警

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | PipelineOrchestrator._call_model 有 cost 追踪但无预算控制 |
| 为什么是盲点 | "本月 API 费用 $X / 预算 $Y"——无。没有预算 = DeepSeek 疯狂重试烧钱而 Owner 不知 |
| 解决状态 | 🔲 **v0.5.0 规划**——CostTracker：按 model/session/epic 统计，超预算 → 告警 + 可选熔断（仅允许 P0/P1 + fallback 到便宜模型） |
| 约束编号 | 待新增 |

###### 盲点 #19 — 缺少 CLI 摘要视图（`zalpha status`）

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | MCP API 有 list_tasks 但无人类友好的 CLI |
| 为什么是盲点 | 1人+AI 维护时 Owner 的日常入口：打开终端 → `zalpha status` → "3 IN_PROGRESS / 2 BLOCKED / 1 超时 / 本月 $12.3"。不需要开 UI |
| 解决状态 | 🔲 **v0.5.0 规划**——`scripts/cli/report.py status` 子命令：ASCII 表格摘要 + 可选 JSON 输出 |
| 约束编号 | 待新增 |

###### 盲点 #20 — 缺少失败模式自动匹配

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | FailurePattern 模型存在（shared/schemas.py），但无匹配和应用逻辑 |
| 为什么是盲点 | "同一个错误犯两次" = 1人+AI 最大的时间浪费。应做到：失败→匹配已知模式→自动应用 mitigation→匹配失败时创建新 FailurePattern |
| 解决状态 | 🔲 **v0.5.0 规划**——FailurePatternMatcher：基于 failure_type + description 语义相似度匹配，匹配成功自动应用 mitigation，失败创建新 Pattern |
| 约束编号 | 待新增 |

##### E. 1人+AI 维护特需

###### 盲点 #21 — 缺少零配置启动（`zalpha init`）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 依赖多个文件存在和路径正确性 |
| 为什么是盲点 | 1人+AI 维护：clone 项目 → 一条命令就绪。不需要手动建 database/注册表/checkpoint 目录 |
| 解决状态 | 🔲 **v0.5.0 规划**——`zalpha init`：自动检测缺失（SQLite→init_db()，注册表→生成模板，checkpoints dir→mkdir）→输出"系统已就绪" |
| 约束编号 | 待新增 |

###### 盲点 #22 — 缺少 Dogfooding（系统自己不用自己）

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | MOD-TASK_SYSTEM 的 6 张任务卡 TASK-INF-0001~0006 状态全是 `created`，仍用旧标签格式（tags_fn...） |
| 为什么是盲点 | 设计最大缺陷——任务系统不能用自身管理自身维护。Dogfooding 应该贯穿始终：本蓝图的所有变更都应该是任务卡驱动的 |
| 解决状态 | 🔲 **v0.5.0 施工**——① BlueprintDecomposer.decompose(本蓝图) → task_repo 中创建 TaskCard；② 本蓝图自身维护通过 `register_from_triage` 接入；③ TASK-INF-0001~0006 修复状态和标签格式 |
| 约束编号 | 待新增 |

###### 盲点 #23 — 缺少渐进式增强施工模式

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 施工策略仅"重写型"——v0.2.0→v0.3.0 同步重写 3 个 .py |
| 为什么是盲点 | 1人+AI：没有灰度 = 没有回滚信心。应支持 `incremental` 模式：第一步改 A，验证通过→第二步改 B |
| 解决状态 | 🔲 **v0.5.0 规划**——§16 施工策略增加 `incremental` 类型，步骤间有显式 Gate 验证 + 回滚边界 |
| 约束编号 | 待新增 |

###### 盲点 #24 — 缺少 AI 维护手册（Troubleshooting Playbook）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 系统总长 5000+ 行（PipelineOrchestrator 1700 + GateEngine 2500 + TaskRepository 1390），无排查指引 |
| 为什么是盲点 | 1人+AI 最怕：系统出问题，AI 不知从何排查。需要任务卡级别的 `troubleshooting_rules` |
| 解决状态 | 🔲 **v0.5.0 规划**——TaskCard 增加 `troubleshooting_rules: list[dict]`，类似 applicable_rules，存储"这个任务失败时先检查 X→再检查 Y→最后看 Z" |
| 约束编号 | 待新增 |

###### 盲点 #25 — 缺少 Owner 离线的 AI 自治边界

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | `ai_autonomy_level` 是字符串 "supervised"——无实际约束力 |
| 为什么是盲点 | 1人+AI 维护基石：Owner 离线时 AI 能做什么/绝对不能做什么，必须用枚举 + 操作清单硬编码 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——`AISelfGovernanceLevel` 五级枚举（SUPERVISED/SEMI_AUTONOMOUS/AUTONOMOUS/FULL_AUTO/EMERGENCY_ONLY）+ GOV-TASK-004 每级操作清单 |
| 约束编号 | §2.1 #9 |

##### F. 架构结构盲点

###### 盲点 #26 — 缺少"意图→蓝图"的自动化入口

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | §2.1 全链路第一节点"① 你提想法"→无系统支撑。§1.3 标记"草稿治理系统 TBD" |
| 为什么是盲点 | 全链路缺了第一步——AI 可以拆蓝图/执行任务，但不能帮你从想法生成蓝图骨架 |
| 解决状态 | 🔲 **v0.5.0 规划**——DraftAssistant：输入想法 → MTH-012 格式蓝图骨架（目标/边界/约束/接口预填）→ Owner 填充→MTH-012 涌现式补充血肉 |
| 约束编号 | 待新增 |

###### 盲点 #27 — 缺少 KMS 知识管理的接口契约

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | `ke_entries: list[str]` 只是 ID 列表，无推送格式契约 |
| 为什么是盲点 | 预留接口不等于定义契约。后续实现 KMS 时如果发现格式不兼容→回炉改→浪费 |
| 解决状态 | 🔲 **v0.5.0 规划**——§4 增加 "KMS 接口契约"：KE 推送格式（{task_id, ke_type, content_snippet, source_file, priority}）+ KE 生命周期与 TaskCard 状态关联表 |
| 约束编号 | 待新增 |

###### 盲点 #28 — 缺少跨 Blueprint 任务聚合

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 一个 Blueprint → N 个 TaskCard，但无法跨模块聚合 |
| 为什么是盲点 | 真实施工涉及多个 Blueprint（MOD-INF-005 + MOD-TASK_SYSTEM 联动）。Owner 需要"Phase 2 全部任务"的全局视图 |
| 解决状态 | ✅ **已在本蓝图 §4.2.1 解决**——TaskCard 新增 `epic: str /| None`（如 `phase-2-infra-upgrade`）+ Phase 字段复用 |
| 约束编号 | §2.2 #11 |

###### 盲点 #29 — M1-M11 缺少插件化

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | M1-M11 硬编码在 PipelineOrchestrator 中 |
| 为什么是盲点 | Vibe Coding 发展快——3 个月后需要 M12（新模型/新审查维度）。硬编码 = 每次新增需改 orchestrator + 回归测试 |
| 解决状态 | 🔲 **v0.5.0 规划**——M 模块声明式配置（`config/pipeline_modules.yaml`）：每个模块含 {module_id, pipeline, prompt_template, input_model, output_model, execution_model, timeout}。新增 M 模块只需加 YAML 条目 |
| 约束编号 | §14 #14 |

###### 盲点 #30 — 缺少"任务系统自身"健康检查和漂移检测

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | §0 有蓝图-代码同步约定但无自动检测 |
| 为什么是盲点 | 1人+AI 最关键的：系统越复杂越需要自诊断。当前无人检查：蓝图声称的文件存在吗？代码模型和蓝图一致吗？SQLite schema 和 Pydantic 模型一致吗？ |
| 解决状态 | 🔲 **v0.5.0 规划**——`validate_blueprint_code_sync.py`（已有）增强 + GateEngine.self_check()（已有）增强 → 每个 session 启动时自动扫描：① 蓝图声称文件存在性；② TaskCard vs shared/schemas.py Task 字段对齐；③ SQLite schema vs models.py 一致；④ 路径合规性（MTH-013） |
| 约束编号 | §14 #13 |

##### G. AI 质量管理与深度可靠性（v0.5.0 新增大类）

###### 盲点 #31 — Prompt Template 无版本化与质量回退机制

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | M1-M11 的 prompt template 散落在 `PipelineOrchestrator` 各 `_run_mX()` 方法和 `M_MODULE_SPECS` 字典中，无版本号、无 Git 追溯、无 diff 对比、无回退能力 |
| 为什么是盲点 | **Prompt 是 Vibe Coding 最重要的"原材料"——比代码更重要。** LLMOps 2025-2026 的基线实践：Prompt 必须语义化版本（SemVer MAJOR.MINOR.PATCH）+ Git 独立存储 + CI 回归测试 + 一键回退。当前状态下：① AI 改了 prompt 导致任务质量下降——无法追溯是哪个版本引入的；② 想对比 "v1.2.0 和 v1.3.0 哪个更好"——没有 A/B 框架；③ Prompt 被误改——只能靠人工记忆恢复。**2024年调研：78%的LLM应用生产事故由未版本化的 prompt 变更引起** |
| 对标 | LLMOps Prompt Version Control（PromptLayer/Helicone/LangSmith 范式——2025年行业标准）+ Semantic Versioning for Prompts（MAJOR.MINOR.PATCH）+ Git-based Prompt CI/CD（2025团队实践） |
| 解决状态 | 🔲 **v0.5.0 规划——P0**：① `prompts/` 目录下语义化版本存储（`prompts/{module_id}_v{MAJOR}.{MINOR}.{PATCH}.yaml`）；② TaskCard 新增 `prompt_version: str`（指向任务使用的 prompt 版本）；③ 每个 M 模块从 YAML 加载 prompt template 而非硬编码；④ `prompt_diff` 命令：两个版本间语义 diff；⑤ `prompt_rollback` 命令：一键回退到上一稳定版本；⑥ `prompt_ab` 命令：同时跑 A/B 两个版本对比评估 |
| 约束编号 | 待新增——§5.1 #21 |

###### 盲点 #32 — 多步骤任务失败时缺少 Saga 补偿事务

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | `rollback_instructions` 是自由文本（不可机器执行），`checkpoint_path` 是整体文件快照（只能全量回退，不能部分补偿） |
| 为什么是盲点 | **2026年AI Agent工作流的核心范式：Saga Pattern（补偿事务）。** 当任务执行了 5 个步骤（step1→创建文件A，step2→修改文件B，step3→删除文件C，step4→失败），需要按逆序补偿（undo step3→undo step2→undo step1），而非全量快照恢复（会丢失其他任务对文件的合法修改）。Transactional AI（2026 HN热帖）和 Atomix（arXiv 2602.14849）都实现了此模式。当前蓝图的全量快照过于粗暴——如果是长任务（30分钟），快照期间其他文件可能已被别的任务修改 |
| 对标 | Transactional AI v0.2（Saga Pattern for AI workflows——每步 do/undo + 分布式锁 + 逆序补偿）+ Atomix（epoch-based transactional tool use）+ LangGraph Two-Phase Commit（sandbox→validate→commit/rollback） |
| 解决状态 | 🔲 **v0.5.0 规划——P0**：① TaskCard 新增 `compensation_steps: list[dict]`（`[{step_id, action_description, undo_command, file_paths_affected, timeout_seconds}]`）；② PipelineOrchestrator 执行失败时自动按逆序执行 `undo_command`；③ 补偿步骤本身失败时写入 `DeadLetterEntry` 并通知 Owner 手动处理；④ 补偿超时（单步>30s）→放弃该步补偿+记录+通知 |
| 约束编号 | 待新增——§5.1 #22 |

###### 盲点 #33 — 模型输出质量静默退化无检测机制

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | 断路器（#15）只检测 API 可用性（连续失败→熔断），不检测输出质量退化 |
| 为什么是盲点 | **模型可以"正常工作"但输出质量下降 20%——这是 Vibe Coding 最隐蔽的杀手。** 场景：DeepSeek 后台升级模型版本→代码生成质量从 85→65 分→所有新任务产出质量下降→无人知晓直到 3 天后发现大量 bug。当前无任何质量基线对比机制。LLMOps 标准要求：每个 prompt+model 组合必须有 baseline evaluation score，每次模型更新后重跑对比 |
| 对标 | LLMOps Automated Eval Regression Testing（2025——deterministic checks + LLM-as-judge + 基线对比）+ Prompt CI/CD Pipeline（pre-deploy eval gate）+ Model Snapshot Regression Detection |
| 解决状态 | 🔲 **v0.5.0 规划——P0**：① 定义 `QualityBaseline` 模型（`{model_id, prompt_version, avg_score, sample_count, last_updated}`）；② M7（GLM审查）完成后对比当前任务 score vs baseline——偏差 > 15% 触发 `QualityRegressionAlert`；③ 连续 3 个任务质量退化→自动回退到上一个已知好的 `model_snapshot` + 通知 Owner；④ `zalpha quality-report` CLI 展示当前所有 model+prompt 组合的质量趋势 |
| 约束编号 | 待新增——§5.1 #23 |

###### 盲点 #34 — 任务缺少 SLA 时限与老化自动优先级升级

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 任务有 `priority`（P0-P4）静态值 + `effective_priority` 依赖传播（#7），但无时间维度 |
| 为什么是盲点 | **ServiceNow ITSM 的核心机制：SLA + 老化升级。** P3 任务坐了 30 天→自动升级到 P2→15天后升级到 P1→最后自动通知 Owner。1人+AI 最大的维护风险：低优先级任务被永久遗忘。当前系统一个 P4 任务可能永远不被执行而不触发任何告警 |
| 对标 | ServiceNow SLA Definition（duration + schedule + 50%/75%/100% escalation triggers）+ ITIL Aging Ticket Management（按 aging bucket 自动升级 + 积压会议）+ Linear Auto-Scheduling（过期任务自动滚动到下一 Cycle） |
| 解决状态 | 🔲 **v0.5.0 规划——P1**：① TaskCard 新增 `sla_deadline: datetime /| None`（若设置，超时触发升级）；② TaskCard 新增 `sla_escalation_policy: dict`（`{escalation_threshold_days, target_priority, max_escalation_priority}`）；③ TaskCard 新增 `original_priority: str`（记录升级前的初始优先级——用于完成后恢复评估）；④ 后台 `SLAWatchdog`：每小时扫描超 SLA 任务→自动 transition（priority=P(n-1)）+ 追加事件 + 通知 Owner |
| 约束编号 | 待新增——§5.1 #24 |

###### 盲点 #41 — AI Session 间"思考中状态"未持久化

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `suspend_context_json`（#3）捕获 SUSPENDED 时的上下文快照，但不捕获 AI 的"正在进行中的推理链" |
| 为什么是盲点 | **Vibe Coding 最大的效率杀手：Session 切换时丢失 AI 的思考上下文。** AI 正在分析 5 个文件的依赖关系→session 结束→下一个 session 的 AI 从零开始，不知道前一个 AI "推理到了哪一步"。Temporal.io 通过 Event History 回放解决此问题——ZephyrAlpha 需要轻量版本："AI 脑中的半成品推理"也需要持久化 |
| 对标 | Temporal Durable Execution（Event History 回放——Workflow恢复时精确重放历史事件重建状态）+ vi2 Vibe Coding V2（结构化命令框架保持跨Session一致性）+ Claude Code long-running agent（90分钟自主运行 + 状态检查点） |
| 解决状态 | 🔲 **v0.5.0 规划——P2**：① TaskCard 新增 `thinking_state_json: str /| None`（AI session 结束前自动保存当前推理状态——`{analysis_progress, pending_decisions, hypotheses, next_steps_planned, partial_results}`）；② 新 session 接手 IN_PROGRESS 任务时→先读取 `thinking_state_json` → 从断点继续而非从头开始；③ `suspend_context_json` 合并到 `thinking_state_json`（统一为一个"任务心智状态"字段） |
| 约束编号 | 待新增——§5.1 #25 |

##### 跨类补充盲点（嵌入已有大类）

###### 盲点 #35 — AI 跨任务知识污染无隔离机制（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 同一 AI session 可能连续执行多个任务，无任何机制防止上一个任务的"经验"污染下一个任务的判断 |
| 为什么是盲点 | **AI 原生任务系统的独特挑战。** 场景：任务A 使用 "Strategy Pattern" 成功→AI 记住了这个偏好→任务B 最适合 "Observer Pattern" 但 AI 受前序任务影响也选了 Strategy。传统任务系统（Jira/Linear）不面临此问题（人类开发者能自主切换思维）——但 AI 存在"上下文惯性"。无隔离 = AI 执行的一致性假象 |
| 对标 | 多 Agent 系统中的 Context Isolation 模式 + LLM System Prompt 中的"fresh mind"指令 + Token预算隔离（per-task token budget 防止跨任务上下文泄漏） |
| 解决状态 | 🔲 **v0.5.0 规划——P1**：① PipelineOrchestrator 的每个 dispatch() 必须在新的 context window 中启动（清除前序任务的 conversation history）；② 每个任务执行前强制注入 neutralization prompt："忽略此前所有任务的上下文，仅基于当前 TaskCard 和 upstream_files 做出判断"；③ 可选 `cross_task_learning: bool`——默认 False，只有 Owner 明确允许时才跨任务保留经验 |
| 约束编号 | 待新增——§5.1 #26 |

###### 盲点 #36 — 缺少紧急热修复快速通道（B 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 所有任务统一走 G0→G7 全部门禁 + 执行管线，无加速通道 |
| 为什么是盲点 | **生产环境 P0 故障修复不能走完整门禁链。** 场景：脚本系统（MOD-INF-005）的关键脚本有 bug→需要 5 分钟内修复→当前流程过所有门禁+AI审查→至少 15 分钟。需要类似 ServiceNow "Emergency Change" 的快速通道：跳过非关键门禁→直接执行→事后补审计 |
| 对标 | ServiceNow Emergency Change Management（预授权+快速通道+事后补审）+ ITIL Emergency CAB + Linear "Urgent" 标签自动提升优先级 |
| 解决状态 | 🔲 **v0.5.0 规划——P1**：① `emergency_mode: bool` 字段——Owner 手动设置或 P0 任务+`tags=fn:critical` 自动触发；② Emergency 模式下：跳过 G1/G2/G3/G4/G5 门禁，仅保留 G0（基础字段）+G6（残留物）+G7（完整度）；③ 事后 24h 内自动补跑完整审计（M6-M11 追加执行）；④ Emergency 执行结果强制通知 Owner 并要求 48h 内确认 |
| 约束编号 | 待新增——§5.1 #27 |

###### 盲点 #37 — 模型版本未锁定快照，任务不可复现（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `execution_model: str`（如 `deepseek-v4-pro`）是逻辑名，不是 dated snapshot（如 `deepseek-v4-pro-2026-05-01`）。模型供应商可能在无通知的情况下更新模型版本 |
| 为什么是盲点 | **LLMOps P0 基线：模型必须锁定 dated snapshot。** 你 5 月 1 日测试通过的 DeepSeek V4 Pro ≠ 5 月 15 日的 DeepSeek V4 Pro。不可复现 = 无法调试 = 无法保证一致性。OpenAI/Anthropic/Google 都推荐使用 dated model versions |
| 对标 | OpenAI Model Snapshot（`gpt-5.1-turbo-2025-11-12`）+ Anthropic Model Versions（`claude-3-opus-20240229`）+ LLMOps Model Pinning Best Practice |
| 解决状态 | 🔲 **v0.5.0 规划——P1**：① TaskCard 新增 `model_snapshot_pinned: str /| None`（如 `deepseek-v4-pro-2026-05-01`）；② `model-registry.yaml` 中每个模型条目增加 `available_snapshots: list[str]` + `default_snapshot: str`；③ dispatch() 时若 `model_snapshot_pinned` 为空→自动填充当前 registry 中的 `default_snapshot`；④ 定期任务（每周）：对比各 snapshot 的质量指标，若 `default_snapshot` 质量下降→自动切换到上一个已知好的 snapshot |
| 约束编号 | 待新增——§5.1 #28 |

###### 盲点 #38 — 多文件产出缺少原子写入事务（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | M3 逐文件写入磁盘——如果写入第 3/5 个文件时系统崩溃，前 2 个已写入磁盘，代码库处于半完成状态 |
| 为什么是盲点 | **写入原子性是分布式系统的基本契约。** 当前 snapshot/checkpoint 机制（#2）可以事后恢复，但无法防止"中间态文件被其他进程读到"。正确做法：write to temp → validate all → atomic rename all |
| 对标 | 数据库 ACID 原子性 + Git atomic object write + Two-Phase File Commit Pattern（先写 .tmp 再 rename） |
| 解决状态 | 🔲 **v0.5.0 规划——P2**：① M3 写入时：所有 `downstream_outputs` 先写 `{path}.zalpha_tmp_{task_id}` → 全部写入成功→逐个 `os.rename` → 任一失败→清理全部 tmp+FAILED；② `os.rename` 在 Windows NTFS 上保证原子性（同卷内）；③ 不支持 rename 的跨卷场景→先 copy+verify checksum→再 delete temp |
| 约束编号 | 待新增——§5.1 #29 |

###### 盲点 #39 — 已完成依赖被修改后下游任务无级联感知（B 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | G2 只检查 depends_on 是否为 COMPLETED/VERIFIED。如果依赖任务 A 完成→依赖方 B 执行→完成→后来 A 被修改（bug fix）→B 的产出可能基于过时的 A |
| 为什么是盲点 | **依赖新鲜度（Dependency Freshness）。** Linear/Jira 中如果 Story A（已完成）后来被修改，依赖它的 Story B 应该标记为"需要重新验证"。当前系统无此感知。场景：KBG-001 完成→SRC-005 基于 KBG-001 完成→KBG-001 被修改以修复一个关键决策→SRC-005 持有过时的架构前提 |
| 对标 | Build System 中的 dependency invalidation（Makefile mtime 检查）+ Bazel action cache invalidation + Nix derivation hash change detection |
| 解决状态 | 🔲 **v0.5.0 规划——P2**：① 每个任务完成后记录 `dependency_fingerprint: dict[str, str]`（`{depends_on_task_id: sha256(depends_on_task.downstream_outputs)}`）；② 任务被修改后重新 COMPLETED→扫描所有 `dependency_fingerprint` 中包含此 task_id 的任务→若指纹不匹配→自动标记 `stale_dependency_warning`；③ 受影响任务的 G2 门禁增加 `dependency_freshness` 检查 |
| 约束编号 | 待新增——§5.1 #30 |

###### 盲点 #40 — 任务系统自身组件缺少降级运行能力（F 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 若 gate_engine.py / task_repo.py / pipeline_orchestrator.py 中任一组件出现 bug→整个任务系统可能不可用 |
| 为什么是盲点 | **"写操作系统的操作系统"必须能降级运行。** 类比：Linux kernel panic 时至少还有 kmsg。任务系统的自我诊断（#30）能发现问题，但发现问题后不能"自己把自己关掉"。需要指定：哪些组件故障时系统可降级（只用核心功能）继续运转，哪些必须 halt |
| 对标 | Kubernetes Graceful Degradation（控制面组件独立降级）+ Nginx failure modes（worker crash不影响master）+ Erlang OTP Supervisor Tree（let it crash + restart策略） |
| 解决状态 | 🔲 **v0.5.0 规划——P2**：① 定义降级矩阵：`gate_engine` 故障→跳过所有非 P0 门禁，任务仍可执行只记录 WARNING；`task_repo` 故障→HALT（数据真源不可用，无降级空间）；`pipeline_orchestrator` 故障→降级为单模块 manual 执行模式；② 降级状态写入 `system_health.json` + CLI `zalpha health` 显示当前降级级别 |
| 约束编号 | 待新增——§5.1 #31 |

##### H. 数据持久化与运行时演化（v0.6.0 新增大类）

###### 盲点 #42 — SQLite Schema 无版本化迁移框架（v0.6.0 P0 盲点）

| 属性 | 值 |
|------|-----|
| 严重性 | **极高——系统进化即自毁** |
| 当前状态 | `db/sqlite_schema.py` 使用 `CREATE TABLE IF NOT EXISTS`——创建时定义结构，但 TaskCard 模型已从 34→56→66+ 字段跨越 3 个版本。如果 v0.5.0 代码尝试读取 v0.3.2 创建的 SQLite 数据，新增字段（如 `prompt_version`、`compensation_steps`）不会自动出现在旧数据库列中，触发 OperationalError |
| 为什么是盲点 | **数据库迁移是持久化系统的第一公民，不是可选的。** SQLite 标准方案（2025工程实践）：① `PRAGMA user_version` 记录当前 db 版本；② `migrations/` 目录按 `{version}.sql` 命名（`001_initial.sql`, `002_add_prompt_version.sql`...）；③ 应用启动时检测 `user_version`→顺序执行待迁移脚本；④ 每次迁移包裹在 `BEGIN...COMMIT` 事务中。当前状态：蓝图声明 TaskCard 有 66+ 字段，但 SQLite 可能只有 34 列——**蓝图与数据真源之间的割裂会在第一个 migration 发生时爆炸** |
| 对标 | SQLite `PRAGMA user_version` 标准（SQLiteForum 2025 指南）+ Alembic migration 模式（SQLAlchemy 生态——增量脚本+version tracking table+事务包裹）+ Django `makemigrations` 范式（模型即 schema 真源） |
| 解决状态 | 🔲 **v0.6.0 规划——P0**：① `db_schema_version.py` 定义 `CURRENT_SCHEMA_VERSION: int`；② `migrations/` 目录存放增量 SQL 脚本（`001_initial.sql` ~ `00N_*.sql`）；③ `Migrator.apply_pending()` 在 `TaskRepo.__init__()` 中自动调用——读取 `PRAGMA user_version` →顺序执行 `version_to > current_version` 的脚本→ `PRAGMA user_version = new_version`；④ 每个迁移脚本必须包含 `up` 和 `down`（回退用）；⑤ 迁移执行失败→rollback+阻止应用启动+明确错误指引 |
| 约束编号 | 待新增——§5.1 #32 |

###### 盲点 #48 — 任务 CANCELLED 状态缺少安全检查协议（v0.6.0 P2 盲点）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 状态机定义了 CANCELLED 状态但无任何安全检查或清理协议。IN_PROGRESS → CANCELLED 的转换不检查 M3 是否已部分写入文件 |
| 为什么是盲点 | **取消不是"标记一下就完了"——取消中可能已有文件被修改。** 场景：任务 IN_PROGRESS→M3 写入了 3/5 个 `downstream_outputs`→用户取消→文件系统留下半完成状态→下一个任务读到不完整的文件。当前的 Saga 补偿（#32）只覆盖 FAILED，不覆盖 CANCELLED。取消需要走简化版补偿：① 检查是否有 `.zalpha_tmp_{task_id}` 残留（原子写入未完成）；② 如果有→清理所有 tmp；③ 检查是否有已完成的 output 文件→标记 `cancelled_artifacts` 供后续清理 |
| 对标 | Temporal.io Cancellation Scopes（子工作流取消后自动清理资源）+ Kubernetes Pod Termination Grace Period（SIGTERM→清理→SIGKILL）+ Git `git reset --hard`（回退到干净状态） |
| 解决状态 | 🔲 **v0.6.0 规划——P2**：① `cancel_task(task_id)` 方法：检查任务状态→如果是 IN_PROGRESS→扫描 `.zalpha_tmp_{task_id}` 清理未完成原子写入→记录 `cancelled_artifacts: list[str]`（已写入的 output 文件路径）→设置 CANCELLED；② `zalpha cleanup-cancelled {task_id}` CLI 命令——Owner 手动清理残留文件；③ CANCELLED 任务的 G7 门禁增强：额外检查是否有孤儿 `.zalpha_tmp_*` 文件 |
| 约束编号 | 待新增——§5.1 #33 |

##### 跨类补充盲点（v0.6.0——嵌入已有大类）

###### 盲点 #43 — 任务创建到执行之间存在前置条件漂移（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | G0/G7 在任务创建时校验 `upstream_files` 存在性和 `deliverables` 格式。但任务可能从 READY 排队数小时甚至数天（等待依赖/WIP释放），届时 `upstream_files` 可能已被其他任务删除或修改 |
| 为什么是盲点 | **"创建时通过≠执行时通过。"** 场景：TASK-042 创建时 `upstream_files` 包含 `src/zephyr/shared/schemas.py` →G0通过→排队等待→期间 TASK-035 删除了 `schemas.py`→TASK-042 执行时读到 `FileNotFoundError`。当前系统在 dispatch() 前只检查状态门禁（G1-G5），不做文件级存在性验证。执行前 preflight 是简化版 Plan-and-Solve 模式的"环境感知"环节 |
| 对标 | Plan-and-Solve Pattern "环境感知" 环节（执行前验证资源可用性）+ Kubernetes Pod Scheduling（pre-admission check + resource inventory）+ Makefile 隐式依赖（mtime 检查——文件是否在被声明为依赖后被修改） |
| 解决状态 | 🔲 **v0.6.0 规划——P1**：① `PreflightCheck` 模型：dispatch() 前执行——逐个打开 `upstream_files`（不读取全部内容，只做 `os.path.exists` + `os.access(os.R_OK)`）→任一不可访问→HALT + 通知 Owner；② 可选 `upstream_files_content_hash: dict[str,str]`——记录 G0 校验时的文件 hash→preflight 时对比→hash 不同→标记 WARNING（文件被修改过但可继续执行）；③ CLI `zalpha preflight {task_id}` 手动触发 |
| 约束编号 | 待新增——§5.1 #34 |

###### 盲点 #44 — AI 修改共享模块后缺少向后兼容性冲击分析（F 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 脚本系统（MOD-INF-005）检查产出格式合规性（YAML/JSON/路径规范），但不检查功能性向后兼容。M7（GLM审查）分析代码质量但不分析"改了 schemas.py 后哪些文件会导入失败" |
| 为什么是盲点 | **GitChameleon 2.0 基准（2025）：AI 代码生成在跨版本兼容性上的成功率仅 48-51%，企业级模型。** 这意味着 AI 修改共享模块后，约一半概率会破坏现有消费者。场景：AI 执行 TASK-043"给 Task 模型加 3 个字段"→修改 `schemas.py`→10 个文件 import Task→其中 3 个因为字段签名变化而导入失败。Tricentis 2025 报告：67% 开发者花更多时间调试 AI 生成代码——因为 AI 的"涟漪效应"不可预测 |
| 对标 | Tricentis SeaLights "change-based testing"（不测"计划改什么"而是测"实际改了什么"→AI 实际改了 10 个文件≠计划改 3 个→需要追踪 ripple effects）+ GitChameleon Benchmark（执行器验证版本条件化代码生成）+ Bazel 依赖图（自动计算 affected targets + 只运行相关测试） |
| 解决状态 | 🔲 **v0.6.0 规划——P1**：① `ImpactAnalysis` 模型：任务 COMPLETED→扫描 `downstream_outputs`→识别"共享模块"（被 >=2 个其他模块 import 的文件）→列出所有 import 该文件的消费者→M7 增加 "consumer compatibility check"；② 可选 `run_consumer_tests: bool`——任务完成后自动 `pytest` 所有消费者测试；③ `zalpha impact {task_id}` CLI——展示该任务修改了哪些文件、影响了哪些消费者 |
| 约束编号 | 待新增——§5.1 #35 |

###### 盲点 #45 — AI 执行中发现意外件时缺少中执行自适应重规划（B 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | PipelineOrchestrator 的 dispatch() 基于创建时的 TaskCard 全量执行。如果 M3 执行时发现 `upstream_file` 有 2000 行而非预期的 200 行，或者发现文件编码是 UTF-16 而非 UTF-8，只能 FAIL→RETRY（重试也失败）→需要 Owner 干预 |
| 为什么是盲点 | **Plan-and-Solve 模式（2025 AI Agent 九大模式）的三级架构明确要求"全局规划→动态执行→弹性调整"——弹性调整环节是生产环境的核心价值。** 当前蓝图有静态规划（diff-plan #11）和失败补偿（Saga #32），但没有"发现意外时在线调整计划"的能力。场景：AI 开始执行→发现文件太大（上下文溢出风险 #14 生效）→不是 FAIL，而是主动提议"将此任务拆成 2 个子任务"→SUSPEND 当前任务→自动创建子任务 |
| 对标 | Plan-and-Solve Dynamic Adjustment（弹性调整环节——AI 在执行中发现意外→重新规划子步骤）+ AutoGLM Agent 实时调整（如任务模型中找到的 auto-todo-writer 能力）+ CrewAI 自适应工作流（agent 在执行中修改 plan） |
| 解决状态 | 🔲 **v0.6.0 规划——P2**：① `AdaptivePlanningGate` 新门禁——M3 执行前或执行中（条件触发：上下文溢出/文件编码不匹配/依赖缺失）→不 FAIL，而是进入 `REPLAN_PROPOSED` 子状态→AI 提出替代方案（拆分/降级/替换资源）→Owner 审批或自动（>AUTONOMOUS 以上）；② 上下文溢出时：AI 自动提议"按函数拆分此任务为 N 个子任务"→SUSPEND→`Decomposer` 创建子任务→恢复执行 |
| 约束编号 | 待新增——§5.1 #36 |

###### 盲点 #46 — AI 实际产出范围偏离 diff-plan 无检测（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | diff-plan（#11）记录了"计划改哪些文件、预计行数"。但 M3 实际写入时，AI 可能写了超出计划范围的文件或行数。当前系统不对比计划 vs 实际 |
| 为什么是盲点 | **Scope Creep 是 AI 代码生成的最常见问题。** Replit 案例（2025年7月）：AI Agent "惊慌失措"后删除了整个生产数据库，尽管被明确要求冻结。一般场景没那么极端——但 AI 经常：① 修改了 `allowed_touch` 之外的 2 个文件；② 写了 500 行而计划是 50 行；③ 添加了未声明的 import。当前没有自动检测机制，只能靠 Owner 事后审查 |
| 对标 | Tricentis SeaLights "什么实际改变了" vs "什么计划改变" 差异检测 + AI 代码审查中的 Scope Check + Cursor/Claude Code 的 diff 审查（展示所有改动而非计划） |
| 解决状态 | 🔲 **v0.6.0 规划——P2**：① M3 完成后对比 diff-plan vs 实际——`modified_files_actual` vs `modified_files_planned`（超出计划→WARNING）；`lines_changed_actual` vs `lines_changed_planned`（偏差 > 50%→WARNING）；② `touched_forbidden_files`（修改了 forbidden_touch 中的文件→FAIL）；③ `zalpha diff-check {task_id}` CLI——展示计划 vs 实际差异 |
| 约束编号 | 待新增——§5.1 #37 |

###### 盲点 #47 — 跨 Session 上下文重复组装浪费 Token（E 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **低** |
| 当前状态 | 每次 dispatch() 都从零开始组装 context（读取所有 upstream_files + applicable_rules + KMS + TaskCard）。如果同一个 task 跨 3 个 session（每个 session 中断后重启），同样的 upstream_files 被读了 3 次 |
| 为什么是盲点 | **在"1人+AI"模式下，一个任务跨 3-5 个 session 是常态（vibe coding 的节奏）。** 如果每个上游文件 5000 tokens，10 个文件 = 50000 tokens/次 × 3 次 = 150000 tokens 浪费在"重新认识同样的代码"上。Durable Task SDK（Microsoft 2026）通过 checkpoint 回放机制避免重复 LLM 调用——ZephyrAlpha 需要轻量版：缓存"上次 context assembly 在 session_{id} 时刻的摘要" |
| 对标 | Microsoft Durable Task for AI Agents（自动 checkpoint + 从断点恢复，不重复已完成的 LLM 调用）+ Semantic Caching（基于文件 hash 的上下文复用）+ Claude Code "Previously, on..." 机制（session 重载摘要） |
| 解决状态 | 🔲 **v0.6.0 规划——P3**：① `ContextCache` 模型——key=`sha256(task_id+upstream_files_paths_sorted)`，value=`{last_assembled_session, file_hash_map, summary, freshness}`；② dispatch() 时先查 ContextCache→如果 `upstream_files` 的 hash 全匹配→复用缓存的 summary 作为 warm-up context（token cost：500→50000）；③ 任一文件 hash 不匹配→全量重读但记录缓存失效原因；④ 缓存 TTL=session 生命周期，过期后自动清除 |
| 约束编号 | 待新增——§5.1 #38 |

#### 优先级路线图

| 优先级 | 盲点# | 名称 | 状态 |
|:--:|:--:|------|:--:|
| P0 | #25 | AI自治边界五级 | ✅ 已解决 |
| P0 | #22 | Dogfooding | 🔲 v0.5.0 |
| P0 | #19 | CLI摘要视图 | 🔲 v0.5.0 |
| P0 | #17 | Owner通知告警 | 🔲 v0.5.0 |
| P0 | #14 | 上下文窗口溢出保护 | ✅ 已解决 |
| P0 | #6 | 文件级并发冲突 | ✅ 已解决 |
| P0 | #31 | Prompt版本化+回退 | 🔲 v0.5.0 |
| P0 | #32 | Saga补偿事务 | 🔲 v0.5.0 |
| P0 | #33 | 模型质量退化检测 | 🔲 v0.5.0 |
| P0 | #42 | SQLite Schema迁移 | 🔲 v0.6.0 |
| P1 | #15 | API断路器 | ✅ 已解决 |
| P1 | #5 | 依赖拓扑排序 | ✅ 已解决 |
| P1 | #11 | diff-plan约束 | ✅ 已解决 |
| P1 | #10 | 幂等性强制检查 | ✅ 已解决 |
| P1 | #20 | 失败模式匹配 | 🔲 v0.5.0 |
| P1 | #30 | 任务系统自诊断 | 🔲 v0.5.0 |
| P1 | #34 | SLA老化自动升级 | 🔲 v0.5.0 |
| P1 | #35 | AI跨任务知识隔离 | 🔲 v0.5.0 |
| P1 | #36 | 紧急热修复快速通道 | 🔲 v0.5.0 |
| P1 | #37 | 模型快照锁定 | 🔲 v0.5.0 |
| P1 | #43 | 中执行前置漂移校验 | 🔲 v0.6.0 |
| P1 | #44 | 向后兼容冲击分析 | 🔲 v0.6.0 |
| P2 | #1 | 父子任务层级 | ✅ 已解决 |
| P2 | #2 | 可执行回滚Snapshot | ✅ 已解决 |
| P2 | #7 | 优先级链上传播 | ✅ 已解决 |
| P2 | #8 | WIP限制 | ✅ 已解决 |
| P2 | #12 | 超时自动回滚 | ✅ 已解决 |
| P2 | #13 | Retry指数退避 | ✅ 已解决 |
| P2 | #16 | 全链路Trace | 🔲 v0.5.0 |
| P2 | #18 | API成本预算 | 🔲 v0.5.0 |
| P2 | #21 | 零配置启动 | 🔲 v0.5.0 |
| P2 | #26 | DraftAssistant | 🔲 v0.5.0 |
| P2 | #28 | 跨模块聚合 | ✅ 已解决 |
| P2 | #29 | M模块插件化 | 🔲 v0.5.0 |
| P2 | #38 | 多文件原子写入 | 🔲 v0.5.0 |
| P2 | #39 | 依赖新鲜度级联感知 | 🔲 v0.5.0 |
| P2 | #40 | 组件降级运行 | 🔲 v0.5.0 |
| P2 | #41 | 跨Session思考态 | 🔲 v0.5.0 |
| P2 | #45 | 中执行自适应重规划 | 🔲 v0.6.0 |
| P2 | #46 | 输出范围蔓延检测 | 🔲 v0.6.0 |
| P2 | #48 | 取消安全清理协议 | 🔲 v0.6.0 |
| P3 | #3 | SUSPENDED暂停恢复 | ✅ 已解决 |
| P3 | #4 | Hook事件系统 | 🔲 v0.5.0 |
| P3 | #9 | 主动任务队列 | 🔲 v0.5.0 |
| P3 | #23 | 渐进增强施工 | 🔲 v0.5.0 |
| P3 | #24 | AI维护手册 | 🔲 v0.5.0 |
| P3 | #27 | KMS接口契约 | 🔲 v0.5.0 |
| P3 | #47 | 跨Session上下文复用 | 🔲 v0.6.0 |

#### v0.4.0 已解决盲点（设计层面）

| 盲点# | 设计解决方案 | 实现文件 |
|:--:|------|------|
| #1 | TaskCard.parent_task_id + 父子状态聚合规则 | `core/models.py` |
| #2 | TaskCard.checkpoint_path + FAILED→自动恢复 | `core/models.py` + `pipeline/pipeline_orchestrator.py` |
| #3 | SUSPENDED 状态 + suspend_context_json | `core/models.py` + `db/task_repo.py` |
| #5 | §5.1 #18：拓扑排序 + 循环检测 | `core/blueprint_decomposer.py` |
| #6 | §5.1 #12：并发文件冲突检测 | `pipeline/pipeline_orchestrator.py` |
| #7 | TaskCard.effective_priority + §5.1 #19 | `core/models.py` + `core/blueprint_decomposer.py` |
| #8 | §5.1 #11：WIP ≤ 5 | `pipeline/pipeline_orchestrator.py` |
| #10 | §5.1 #17：幂等性强制检查 | `pipeline/pipeline_orchestrator.py` |
| #11 | §5.1 #16：diff-plan 强制 | `pipeline/pipeline_orchestrator.py` + `pipeline/models.py` |
| #14 | TaskCard.estimated_context_tokens + §5.1 #13 | `core/models.py` + `context_engine/context_assembler.py` |
| #15 | TaskCard.circuit_breaker_open + §5.1 #14 | `pipeline/pipeline_orchestrator.py` |
| #25 | AISelfGovernanceLevel 五级枚举 | `core/models.py` + `task-lifecycle-standard.md` |
| #28 | TaskCard.epic + Phase 聚合查询 | `core/models.py` + `db/task_repo.py` |
| #12/#13 | checkpoint + retry 字段 | `core/models.py` + `pipeline/pipeline_orchestrator.py` |

#### 对标基准总结

| 基准来源 | 缺失项数 | 已解决 | v0.5.0规划 | v0.6.0新增 |
|------|:--:|:--:|:--:|:--:|
| 专业机构（Jira/Linear/ServiceNow） | 7 | 3 | 4 | 0 |
| 氛围编程社区（bolt/v0/Cursor/Replit） | 6 | 4 | 2 | 0 |
| AI执行可靠性（自研深度） | 13 | 6 | 3 | **4** |
| 1人+AI 维护特需（自研） | 8 | 1 | 6 | **1** |
| 架构完整性（自研） | 8 | 2 | 5 | **1** |
| 可观测性（自研） | 3 | 0 | 3 | 0 |
| AI质量管理（LLMOps+Temporal+Saga Pattern——2025-2026前沿） | 4 | 0 | 4 | 0 |
| **🆕 数据持久化与运行时演化（DB Migration+Cancel Safety——v0.6.0**） | **2** | **0** | **0** | **2** |
| **总计** | **48** | **16** | **25** | **7** |

> **施工原则**：v0.4.0 蓝图设计完成 → v0.5.0 完成第二轮审计（#31-#41）→ **v0.6.0 完成第三轮审计（#42-#48）——48个盲点八大类全量登记**。设计先行，代码后行——避免"先乱建再重构"的 Vibe Coding 反模式。
>
> **v0.6.0 审计方法升级**：本轮审计新增两个维度——④ **运行时演化与持久化可靠性**（SQLite Schema 迁移版本化 / Alembic 增量迁移范式 / 任务取消安全协议 / Temporal.io Cancellation Scopes）；⑤ **AI 代码生成的涟漪效应管理**（GitChameleon 2.0 向后兼容性基准 / Tricentis change-based testing 差异检测 / Plan-and-Solve 中执行弹性调整 / LangChain Deep Agents 异步子代理编排）。这前两个维度是 v0.5.0 审计未触及的"系统随时间演化"维度。

---

### 蓝图特有：Multi-Worker Batch Coordination (v0.6.1 · MOD-INF-016)

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 仅本蓝图需要：10+ TRAE AI 对话并行认领任务是本系统特有需求
> 不可砍理由：砍掉 = 并发施工能力丢失

| 维度 | 决策 |
|------|------|
| **Broker** | SQLite（零外部依赖，`busy_timeout=5000` 处理并发写入） |
| **原子认领** | `UPDATE ... RETURNING`（SQLite 3.35+），单 SQL 完成 claim |
| **依赖解析** | `json_each(depends_on)` — 只认领依赖已 COMPLETED 的任务 |
| **优先级** | `ORDER BY priority ASC, created_at ASC` — 低数字高优先 |
| **超时回收** | 30 分钟 TTL → `claimed_at < cutoff` → 自动回 READY |
| **进度聚合** | `GROUP BY status` 三字段实时统计 |

**Schema v16 变更**：tasks 表新增 `batch_id TEXT` / `claimed_by TEXT` / `claimed_at TEXT` + 对应索引

```sql
ALTER TABLE tasks ADD COLUMN batch_id   TEXT;    -- 批量标识
ALTER TABLE tasks ADD COLUMN claimed_by TEXT;    -- 认领者 worker_id
ALTER TABLE tasks ADD COLUMN claimed_at TEXT;    -- 认领时间 ISO8601

CREATE INDEX idx_tasks_batch   ON tasks(batch_id);
CREATE INDEX idx_tasks_claimed ON tasks(claimed_by, status);
```

**原子认领 SQL**：

```sql
-- 原子认领：单条 UPDATE ... RETURNING（不可分割）
UPDATE tasks SET status = 'IN_PROGRESS',
                 claimed_by = :worker_id,
                 claimed_at = :now,
                 updated_at = :now
WHERE task_id = (
    SELECT t.task_id FROM tasks t
    WHERE t.status = 'READY'
      AND t.batch_id = :batch_id
      AND t.is_deleted = 0
      AND (
          t.depends_on IS NULL
          OR t.depends_on = '[]'
          OR NOT EXISTS (
              SELECT 1 FROM json_each(t.depends_on)
              WHERE value != ''
              AND (SELECT status FROM tasks WHERE task_id = value) != 'COMPLETED'
          )
      )
    ORDER BY t.priority ASC, t.created_at ASC
    LIMIT 1
)
RETURNING *;
```

**TaskRepository 新增方法**：

| 方法 | 签名 | 说明 |
|------|------|------|
| `claim_next` | `(batch_id, worker_id) -> TaskCard /| None` | 原子认领下一个可施工任务 |
| `recover_stale_claims` | `(batch_id, timeout_minutes=30) -> int` | 释放超时任务 |
| `batch_progress` | `(batch_id) -> dict[str, int]` | 批量进度聚合 |

**BatchOrchestrator 使用模式**：

```python
from zephyr.orchestrator.batch_orchestrator import BatchOrchestrator

bo = BatchOrchestrator(repo, batch_id="construction-20260507",
                       worker_id="session-20260507-001")
bo.recover_stale_claims()
while (card := bo.claim_next()):
    try:
        # ... 施工逻辑 ...
        bo.mark_done(card.task_id)
    except Exception as e:
        bo.mark_failed(card.task_id, str(e))
```

**与旧 `_construction_checkpoint.json` 对比**：

| | 旧方案（checkpoint.json） | 新方案（BatchOrchestrator） |
|---|---|---|
| 认领方式 | 手动改 JSON 指针 | SQLite 原子 `UPDATE RETURNING` |
| 并发安全 | ❌ 竞态条件 | ✅ 原子操作 |
| 依赖感知 | ❌ 无 | ✅ `json_each(depends_on)` |
| 超时回收 | ❌ 无 | ✅ 30 分钟 TTL |
| 进度查询 | 需手动数 | `batch_progress()` 一键 |
