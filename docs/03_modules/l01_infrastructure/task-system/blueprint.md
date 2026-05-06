---
module_id: "MOD-INF-006"
title: "任务系统蓝图 — 全链路：草稿→蓝图真源→任务卡→双管线执行→脚本系统"
doc_type: blueprint
status: Active
version: "0.6.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
ttl: permanent
construction_progress: phase_1_complete
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha 任务系统全链路蓝图 v0.6.0。覆盖从意图→草稿→蓝图真源→任务卡拆解→AI双管线执行→脚本系统校验的闭环工作流。v0.6.0 在 v0.5.0 基础上完成第三轮深度盲点审计（30→41→48个盲点八大类），新增大类 H「数据持久化与运行时演化」：SQLite Schema 版本化迁移框架、任务取消安全协议。原七大类补充：中执行自适应重规划、执行时前置漂移校验、AI代码向后兼容性冲击分析、输出范围蔓延检测、跨Session上下文Token复用。TaskCard 模型：62字段（31基座 + 31执行层）。"
tags: [task-system, task-card, vibe-coding, dual-pipelines, script-system, state-machine, gates, ai-execution, infrastructure, emergent-design, path-compliance, anti-drift, blind-spot-audit, dogfooding, ai-autonomy, circuit-breaker, diff-plan, trace, observability, plugin-architecture, self-diagnosis, prompt-versioning, saga-compensation, quality-regression-detection, model-snapshot-pinning, sla-auto-escalation, knowledge-isolation, emergency-hotfix, atomic-write, graceful-degradation, schema-migration, cancel-safety, preflight-check, backward-compat-impact, adaptive-replanning, scope-creep-detection, context-cache-reuse]
depends_on:
  - {target: PS-STD-001, at: "§7.10", why: "task_id；§7.1 语义 28 + §7.1.1 追踪 3 → Task 共 31 字段——与 §3.2.1 对齐"}
  - {target: PS-STD-011, at: "MTH-012|MTH-013", why: "涌现式设计+路径合规创建——本蓝图编写方法论"}
  - {target: GOV-DOC-002, at: "§5.1.2", why: "路径映射——产出物物理存放"}
  - {target: MOD-INF-005, at: "全篇", why: "脚本系统——本蓝图管线产出的审计消费方"}
  - {target: GOV-TASK-004, at: "全篇", why: "任务生命周期治理——取消权限、优先级裁决、自治边界"}
  - {target: GOV-TASK-005, at: "全篇", why: "任务关闭标准——三步法"}
  - {target: TEMPLATE-TASK-001, at: "全篇", why: "任务卡模板——所有任务卡 .md 格式标准"}
  - {target: REG-LLM-001, at: "全篇", why: "模型基准排名——execution_model 数据依据"}
  - {target: GOV-AI-002, at: "全篇", why: "模型路由策略——任务分配决策树、断路器、降级策略"}
  - {target: "src/zephyr/shared/schemas.py", at: "Task类", why: "Task模型基座——本蓝图 TaskCard 继承其 31 字段"}
  - {target: "src/zephyr/db/task_repo.py", at: "全篇", why: "SQLite CRUD + 10状态机 + N:N task_files——本蓝图数据层真源"}
  - {target: ADR-0038, at: "全篇", why: "File-as-Task 范式——文件与任务 1:1 双向映射"}
  - {target: ADR-0040, at: "全篇", why: "Pydantic V2 强制——所有模型基座"}
  - {target: ADR-0030, at: "全篇", why: "SQLite 元数据层——tasks/events/gates 四表"}
---

# 任务系统蓝图 + 施工指引 + 盲点审计

> module_id: MOD-INF-006 | version: 0.6.0 | status: approved | layer: cross_layer

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | AI 零记忆，不知道相对路径的基准在哪 | 文件创建到错误位置 |
| 2 | **必备链接不可省略**——即使与前序文档重复也必须完整列出 | AI 每次新 session 是零记忆，不记得前序文档写了什么 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程、不保存未选方案 | 决策过程是草稿的事——蓝图是施工依据，不是讨论记录 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | AI 不知道项目目录规范，会自行创建路径 | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | AI 不知道边界在哪，会越界修改 | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | AI 不知道系统能容纳多少，可能设计出无法扩展的方案 | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | AI 不知道旧东西怎么处理，可能直接删除或保留 | 断链——旧引用找不到文件；或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | AI 无法处理模糊指令，需要明确的二元判断 | 执行漂移——AI 自行决定，可能选错 |
| 9 | **蓝图必须自包含**——关键信息不能只写"详见XX" | AI 可能不读引用的文件 | 信息缺失——AI 缺少关键上下文 |
| 10 | **删除文件必须遵守安全删除协议**——禁止直接删除任何文件 | 没有git备份，删除不可逆；AI可能误判文件"没用了" | 永久丢失——无法恢复 |

---

## ⚠️ 安全删除协议

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| 1 | MOD-INF-003 任务卡KMS蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-card-kms\blueprint.md` | 覆盖型 | 本蓝图 | 已标记 deprecated→stable 物理删除 |
| 2 | MOD-INF-004 双管线蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vibe-coding-pipelines\blueprint.md` | 覆盖型 | 本蓝图 | 已标记 deprecated→stable 物理删除 |
| 3 | 场外草稿（双管线+任务卡知识库） | `D:\ZephyrAlpha\模块候选池\开发流程\氛围编程基础设施\vibe-coding-two-pipelines-design.md` / `vibe-coding-task-card-and-knowledge-base-design.md` | 迁入完毕 | 本蓝图 | 内容已全部通过 MTH-012 Step 3 纳入——完成历史使命→Owner 决定删除或归档 |
| 4 | v0.2.0 TaskCard 模型（core/models.py） | `D:\ZephyrAlpha\src\zephyr\core\models.py` | 覆盖型 | v0.3.0 TaskCard（继承 shared/schemas.py Task） | experimental 步骤3——重写 core/models.py 对齐新契约 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 物理删除只能在 stable 搬入阶段执行 | 给足缓冲期 |
| 3 | 物理删除必须人类确认 | AI 不得自行删除文件 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 2.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | §7——task_id/语义28/追踪3/Task共31/状态机 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | 2.6.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\governance-methodology-standard.md` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 脚本系统蓝图 | MOD-INF-005 | 3.0.0+ | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\script-system\blueprint.md` | 审计消费方——管线产出→12维度审计 |
| 5 | 任务卡操作指南 | GOV-TASK-001 | 3.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\task\task-card-standard.md` | 正文结构与门禁速查——字段 §7 真源见 PS-STD-001（GOV-TASK-003 已迁至 GOV-AI-008 handoff-protocol） |
| 6 | 任务生命周期标准 | GOV-TASK-004 | 2.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\task\task-lifecycle-standard.md` | 取消权限、优先级裁决 |
| 7 | 任务关闭标准 | GOV-TASK-005 | 1.1.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\task\task-closure-standard.md` | 关闭三步法 |
| 8 | 任务卡模板 | TEMPLATE-TASK-001 | 1.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\task-card-template.md` | 所有任务卡 .md 的标准格式 |
| 9 | 模型基准排名 | REG-LLM-001 | 1.1.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\frontier-llm-benchmark-ranking.md` | execution_model 数据依据 |
| 10 | 模型路由策略 | GOV-AI-002 | 2.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\ai\model-routing-policy.md` | 任务分配决策树 |
| 11 | AGENTS.md 项目基准 | — | 4.6.1+ | `D:\ZephyrAlpha\AGENTS.md` | 项目全局规则 |
| 12 | Task 模型基座 | shared/schemas.py | 现有代码 | `D:\ZephyrAlpha\src\zephyr\shared\schemas.py` | `Task` 语义28+追踪3=31 字段（PS-STD-001 §7.1~§7.1.1）——TaskCard 继承 |
| 13 | task_repo.py | — | 现有代码 | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | SQLite CRUD + 10状态机 + N:N task_files——数据层真源 |
| 14 | 任务卡元注册表 | task-card-meta-registry | V-13 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml` | 三套任务卡系统登记——迁移状态追踪 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-INF-003（旧蓝图层） | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-card-kms\blueprint.md` | 任务卡制度+KMS体系 | deprecated——已被本蓝图合并 |
| 2 | MOD-INF-004（旧双管线） | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vibe-coding-pipelines\blueprint.md` | 双管线流程+M模块 | deprecated——已被本蓝图合并 |
| 3 | Task 模型（shared/schemas.py） | `D:\ZephyrAlpha\src\zephyr\shared\schemas.py` | 语义28+追踪3=31 字段——task_id/状态机/CRUD | ✅ 可复用——本蓝图 TaskCard 继承此模型 |
| 4 | task_repo.py（SQLite CRUD） | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | 创建/查询/更新/删除/状态转换 + events审计 + N:N映射 | ✅ 可复用——本蓝图数据层使用此代码 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 本蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md` | 真源 | 重写 v0.3.0 |
| 2 | Change Folder | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\changes\` | 新建 | 存放任务卡 .md 文件 |
| 3 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 修改 | 更新 MOD-INF-006 条目 |
| 4 | Task 模型基座 | `D:\ZephyrAlpha\src\zephyr\shared\schemas.py` | 依赖 | 本蓝图 TaskCard 继承其 Task 类 |
| 5 | task_repo.py | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | 依赖 | 数据层真源——蓝图 §3 引用 |
| 6 | core/models.py（我们建的） | `D:\ZephyrAlpha\src\zephyr\core\models.py` | 重写 | 对齐到 shared/schemas.py Task 继承 |
| 7 | blueprint_decomposer.py | `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py` | 重写 | 输出改为 task_repo(SQLite) + .md |
| 8 | task_manager_server.py | `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py` | 重写 | 接入 task_repo(SQLite) 真源 |
| 9 | task_completion_gate.py | `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` | 读取 | 需同步 G7 门禁 |
| 10 | metadata-registry.md | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | 读取 | §7 字段真源 |
| 11 | task-card-meta-registry.yaml | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml` | 修改 | 更新迁移状态 |

---

## 1. 设计背景与目标

### 1.1 背景

ZephyrAlpha 项目当前面临三个核心问题，任务系统是解药：

1. **蓝图分散、格式不统一**：MOD-INF-003 和 MOD-INF-004 各用 9 节旧格式，相互引用但内容割裂。AI 读 A 要跳 B——违反 AGENTS.md §5.1 "零记忆重启标准"。

2. **场外草稿未迁入真源**：双管线设计 + 任务卡元模型 + 知识库设计——数千行决策全在草稿里，不在项目真源文件中。

3. **管线未贯通**：蓝图→任务卡拆解→双管线执行→脚本系统 这条完整链路只存在于讨论中。

4. **历史裁定遗留**：`D:\ZephyrAlpha\模块候选池\文档管理体系\任务系统专题讨论文档.md` 记录 23 个任务系统裁定（#1-#23），其中核心结论（task_id格式/字段集/状态机/存储）已在当前规则升级中吸收——但前期 experimental 施工代码（core/models.py / blueprint_decomposer.py）未对齐。

> **对标**：SDD 论文——spec.md 应是自包含的。ITIL SACM——配置项关系图必须端到端可追踪。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | **合并为一**：MOD-INF-003+004 + 两份场外草稿 + 历史裁定 = 一份自包含蓝图 | 蓝图文件数 3→1，两份旧蓝图 deprecated |
| 2 | **全链路贯通**：意图→草稿→蓝图→任务卡→双管线→脚本系统——每步有输入/输出/门禁 | 每个环节 Schema 完整 |
| 3 | **TaskCard 模型取最优**：基座继承 shared/schemas.py Task（31字段）+ 扩展防漂移 + 父子层级 + 回滚 + 自治字段 | 基座对齐 metadata-registry.md §7 真源——不留两套模型 |
| 4 | **task_id 格式统一为 `{NAMESPACE}-{SEQ}`** | ADR-001 / STD-005 / SRC-042——对标 Jira，自文档 |
| 5 | **路径合规创建**：MTH-013 原则——AI 不得自主决定目录层级 | 所有路径可追溯到索引 |
| 6 | **模型分工明确**：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种救援 | 分工有基准数据支撑 |
| 7 | **Dogfooding**：任务系统用自身管理自身维护——MOD-INF-006 自身任务是任务卡驱动的 | 本蓝图的施工任务全部通过 task_repo.create() 注册 |
| 8 | **AI 自治边界五级**：定义 Owner 离线时 AI 的权限边界（supervised / semi_autonomous / autonomous / full_auto / emergency_only） | GOV-TASK-004 §AI自治 五级枚举 + 每级允许操作清单 |
| 9 | **全链路可观测**：每个 M 模块执行耗时/Token/成本可追踪，`zalpha status` 一键摘要 | events 表含 module_id + duration_ms，CLI 命令可工作 |
| 10 | **失败自愈**：失败模式自动匹配→应用已知 mitigation，避免同一问题失败两次 | FailurePattern 匹配引擎可用，匹配成功率 > 60% |
| 11 | **执行可靠性三层**：diff-plan 约束 + 并发冲突检测 + 幂等强制检查——在"审查"之前拦住错误 | G1 门禁增加 diff_plan_required / conflict_free / idempotent_check |
| 12 | **API 韧性**：断路器 + 指数退避 + 自动降级——DeepSeek 不可用时系统不卡死 | 断路器状态可查，自动降级延迟 < 5s |
| 13 | **跨模块聚合**：支持多个 Blueprint 的任务按 Phase/Epic 聚合为全局施工视图 | Phase/Epic 字段可用，跨模块查询 < 100ms |
| 14 | **Prompt 质量可追溯**：每个 M 模块的 prompt 有独立版本号，任务记录 prompt_version——出问题时能追溯到是 prompt 还是模型还是数据的问题 | `prompt_diff` / `prompt_rollback` 可用，prompt 变更历史完整 |
| 15 | **失败可精细补偿**：多步骤任务失败后按 Saga 补偿事务逆序撤销，不依赖全量快照 | compensation_steps 自动执行，补偿成功率 > 80% |
| 16 | **质量退化自动发现**：模型输出质量下降 15%+ 时自动检测并回退到上一个好的 snapshot | QualityBaseline 可用，退化检测延迟 < 1个任务周期 |

### 1.3 不包含的目标（v0.4.0 重新评估）

| # | 明确排除 | 原因 | v0.4.0 变化 |
|---|---------|------|------------|
| 1 | KMS 知识库的 KE 条目定义和抓取机制 | 属于独立的 KMS 系统升级——后续讨论。**本蓝图 §3.2.3 新增接口契约预留（KE 推送格式 + 与 task 生命周期的关联）** | ⚠️ 从"完全排除"升级为"接口契约已定义，实现另排" |
| 2 | 模型注册表（model-registry.yaml）的完整建设 | 独立小任务——后续处理。任务卡模板中已预埋引用字段 | 无变化 |
| 3 | 草稿治理系统（草稿的讨论优化流程） | 独立系统——后续讨论。**本蓝图新增 DraftAssistant 模块（§2.2 职责 #8）：意图→结构化蓝图骨架的半自动生成** | ⚠️ 从"完全排除"升级为"基础入口已定义，完整流程另排" |
| 4 | SQLite 数据库物理迁移 | 已有代码`task_repo.py`——蓝图只定义数据模型规范 | 无变化 |
| 5 | Phase 5 AI 自治模块 | **v0.4.0 重新评估**：1人+AI维护语境下，AI自治边界定义是 P0 优先级。本蓝图 §2.2 职责 #9 新增五级自治枚举 + 每级允许操作清单。GOV-TASK-004 同步更新 | ⚠️ P0→从"预留字段不实现"升级为"边界已定义，逐步实现" |
| 6 | 全功能看板 UI（拖拽/泳道/燃尽图） | 超出 1 人+AI 维护的 ROI 边界——CLI 摘要视图替代 | 🆕 新增——明确排除重型 UI |
| 7 | 多 Agent 辩论/投票（CrewAI/AutoGen 模式） | v0.4.0 阶段仅需串行管线 + 三层防御——并行 Agent 是 v0.5.0+ 的事 | 🆕 新增——明确排除过早的并行 Agent |

---

## 2. 模块边界

### 2.1 全链路架构视图

```
┌─────────────────────────────────────────────────────────────────┐
│                     ZephyrAlpha 任务系统全链路                      │
│                                                                   │
│  ① 你提想法 → ② 草稿（多轮 AI 优化 → 最终版）                      │
│              草稿治理系统（TBD——后续独立讨论）                      │
│                          │                                        │
│                          ↓                                        │
│              ③ 蓝图真源（本蓝图格式：11 节）                         │
│                 MTH-012 涌现式设计保证血肉丰满                       │
│                          │                                        │
│                          ↓                                        │
│    ④ §11 施工指引 → 拆卡算法 → TaskCard对象 → task_repo.create()   │
│        写入 SQLite（真源） + 同步生成 changes/{feature-id}/*.md     │
│                          │                                        │
│           ┌──────────────┼──────────────┐                         │
│           ↓              ↓              ↓                         │
│     ⑤ A区生产线      ⑥ B区生产线    ⑦ C区脚本系统                  │
│     (代码生产)       (深度审计)      (横切校验)                     │
│     DeepSeek主力     GLM审查主力      MOD-INF-005                   │
│           │              │              │                         │
│           └──────────────┼──────────────┘                         │
│                          ↓                                        │
│               ⑧ 下一个循环开始                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 职责范围

| # | 职责 | 说明 |
|---|------|------|
| 1 | **蓝图管理**：作为任务系统的唯一输入——蓝图按 11 节模板书写后，§11 施工指引直接驱动任务卡拆解 | 蓝图 = 原材料 |
| 2 | **任务卡生命周期**：蓝图自动拆解→Owner确认→task_repo.create()→10状态流转→G0-G7门禁→task_repo.transition()→关闭 | 任务卡 = 工件 |
| 3 | **标签体系**：扁平 `tags[]`（推荐五轴前缀约定：`fn:`/`ly:`/`md:`/`st:`/`mo:`） | 简洁对标 Jira——五轴由 AI 内部解析而非强制 |
| 4 | **AI双管线执行**：A区 M1-M5（生产）+ B区 M6-M11（审计） | AI执行 = 引擎 |
| 5 | **模型分工策略**：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种救援 | 基于 REG-LLM-001 + GOV-AI-002 |
| 6 | **脚本系统集成**：任务管线产出自动送审——C区 12 维度审计 | 对标 MOD-INF-005 |
| 7 | **KMS 知识管理**（beta+ 排除——接口契约已定义，实现另排） | 接口预留——§3.2.3 定义 KE 推送格式与生命周期关联 |
| 8 | **DraftAssistant**（v0.4.0 新增） | 意图→结构化蓝图骨架的半自动生成入口——全链路第一步 |
| 9 | **AI 自治边界管理**（v0.4.0 P0） | 五级自治枚举 + 每级允许操作清单——Owner 离线时的行为契约 |
| 10 | **任务系统自诊断**（v0.4.0 新增） | 蓝图-代码一致性校验 + SQLite schema 健康检查 + 漂移检测 |
| 11 | **全链路可观测**（v0.4.0 新增） | M1-M11 每步耗时/Token/成本记录 + CLI `zalpha status` 摘要视图 |
| 12 | **失败自愈**（v0.4.0 新增） | FailurePattern 自动匹配 + mitigation 应用——同错不犯两次 |
| 13 | **Prompt 版本化管理**（v0.5.0 新增） | M1-M11 prompt 语义化版本存储 + diff/rollback/AB对比——盲点 #31 |
| 14 | **Saga 补偿事务执行**（v0.5.0 新增） | 任务失败时逆序执行 undo_command + DeadLetter处理——盲点 #32 |
| 15 | **质量基线监控**（v0.5.0 新增） | QualityBaseline 维护 + M7 偏差检测 + 自动回退模型快照——盲点 #33 |

### 2.3 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | SQLite CRUD + 10状态机 + N:N映射 | `task_repo.py`（`src/zephyr/db/`）— 已有生产级代码 |
| 2 | Task 模型基座（Pydantic V2 31字段） | `shared/schemas.py`（`src/zephyr/shared/`）— metadata-registry.md §7 真源 |
| 3 | MCP Server Web 层 | `task_manager_server.py`（`src/zephyr/mcp/`）— 本蓝图更新后重写 |
| 4 | 审计脚本 | MOD-INF-005 — 已有 9+ 脚本 |
| 5 | context_engine | `context_engine/` — 已有 7 模块 + experimental 补齐 |
| 6 | dashboard | `dashboard/` — 已有代码 |
| 7 | Phase 5 AI 自治 | 预留字段不实现——但五级枚举已在 GOV-TASK-004 中定义 |
| 8 | 模型注册表完整建设 | 独立小任务——model-registry.yaml 另排 |
| 9 | 全功能看板 UI | 排除——CLI 摘要视图替代 |
| 10 | 多 Agent 并行辩论 | v0.5.0+ 的事——当前串行管线 + 三层防御足够 |

---

## 3. 接口契约

> ⚠️ 完整升级方案——6 个子节。强制 Pydantic V2 BaseModel（ADR-0040）。
>
> **模型层级**：`shared/schemas.py` `Task`（**语义 28 + 追踪 3 = 31 字段**，metadata-registry.md §7.1~§7.1.1）→ 本蓝图 TaskCard 继承 `Task` 并扩展 Vibe Coding 执行层字段（§3.2.1）。

### 3.1 公共 API

#### 3.1.1 蓝图拆解器（BlueprintDecomposer）

```python
from pydantic import BaseModel
from zephyr.db.task_repo import TaskRepo
from zephyr.shared.schemas import Task, TaskStatus

class BlueprintDecomposer:
    """从蓝图 §11 施工指引拆解为任务卡——写入 task_repo（SQLite）+ .md 同步"""

    def __init__(self, repo: TaskRepo):
        self.repo = repo

    def decompose(
        self,
        blueprint_path: str,
        output_dir: str,
        strategy: str = "hybrid",
        model_assignment: str = "auto"
    ) -> "DecompositionResult":
        """
        输入：蓝图路径（§11 施工指引）
        输出：DecompositionResult（任务卡清单 + 依赖图）

        算法：
          1. 解析 §11 每个步骤 → 1 张任务卡
          2. NAMESPACE-SEQ 格式分配 task_id（ADR/CP/KE/STD/DW/SRC/OPS）
          3. 解析步骤中的"创建文件清单"→ downstream_outputs
          4. 解析步骤中的"内容编写指引"→ acceptance
          5. 按 GOV-AI-002 决策树自动分配 execution_model
          6. 每张任务卡 → self.repo.create(task)（写 SQLite）
          7. 同步生成 .md 副本 → {output_dir}/{task_id}.md
          8. G7 门禁通过后才标记 construction_status=complete
        """
        ...
```

#### 3.1.2 任务卡生命周期管理器

```python
class TaskLifecycleManager:
    """包装 task_repo.py 的 10 态状态机——增加 G0-G7 门禁 + .md 同步"""

    def __init__(self, repo: TaskRepo):
        self.repo = repo

    def create_task_card(self, task: "TaskCard") -> DecompositionResult:
        """创建任务卡——G0+G7 门禁通过 → task_repo.create() + .md 同步"""
        ...

    def transition(self, task_id: str, to_status: TaskStatus,
                   gate_check: bool = True) -> "TransitionResult":
        """状态转换——门禁通过 → task_repo.update_status(task_id, to_status)"""
        ...

    def check_gate(self, task_id: str, gate_id: "GateLevel") -> "GateCheckResult":
        """独立门禁检查——与 task_repo 无关的纯校验"""
        ...
```

#### 3.1.3 管线调度器（PipelineOrchestrator）

```python
class PipelineOrchestrator:
    """调度 A区/B区/C区管线 + 模型分配"""

    def dispatch(self, task_id: str, pipeline: str = "auto") -> "DispatchResult":
        """按 GOV-AI-002 决策树分配管线+模型"""
        ...

    def execute_pipeline(self, dispatch_id: str, modules: list[str],
                         model: str) -> "PipelineExecutionResult":
        """串行执行 M 模块链"""
        ...
```

### 3.2 数据模型

#### 3.2.1 TaskCard（Vibe Coding 扩展任务模型）

> **基座**：继承 [shared/schemas.py](file:///D:/ZephyrAlpha/src/zephyr/shared/schemas.py) `Task`（**31 字段**，真源 [metadata-registry.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/meta/metadata-registry.md) §7.1~§7.1.1）
>
> **扩展**：本蓝图追加 6 维防漂移 + 门禁 + 管线 + **v0.4.0 新增：父子层级/可执行回滚/Retry策略/AI自治五级** 等 Vibe Coding 执行层字段

```python
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional
from zephyr.shared.schemas import Task, TaskStatus, Priority, SafetyLevel, Classification, EvolutionPolicy

class GateLevel(str, Enum):
    """全生命周期门禁——G0-G7"""
    G0 = "G0"  # 创建门禁——字段完整性校验（21必填） + v0.4.0: diff_plan_required/conflict_free/idempotent_check
    G7 = "G7"  # 完整度门禁——上游文件存在+下游路径完整+回滚可执行 + v0.4.0: checkpoint_path 可用
    G1 = "G1"  # 指派门禁——模型/管线/模块不冲突 + v0.4.0: WIP 限制检查 + 并发冲突检测
    G2 = "G2"  # 前置门禁——depends_on 全部 COMPLETED/VERIFIED + v0.4.0: 拓扑排序校验 + 循环依赖检测
    G3 = "G3"  # 执行门禁——context_assembly_manifest 全部可读 + v0.4.0: 上下文窗口溢出保护
    G4 = "G4"  # 产出门禁——downstream_outputs 文件存在+格式正确
    G5 = "G5"  # 审计门禁——audit_findings 零 Critical/High
    G6 = "G6"  # 关闭门禁——artifact_paths 残留物已处理

class TaskNamespace(str, Enum):
    """任务命名空间——裁定 #21 + metadata-registry.md §7.2"""
    ADR = "ADR"  # 架构决策记录
    CP = "CP"    # 施工计划
    KE = "KE"    # 知识条目
    STD = "STD"  # 标准/规范
    DW = "DW"    # 开发工作区
    SRC = "SRC"  # 源代码
    OPS = "OPS"  # 运维/其他

class AISelfGovernanceLevel(str, Enum):
    """AI 自治等级——v0.4.0 新增，五级枚举（GOV-TASK-004 §AI自治 真源）"""
    SUPERVISED = "supervised"          # Owner 在线时执行——所有操作需确认
    SEMI_AUTONOMOUS = "semi_autonomous"  # Owner 离线可执行低风险任务（P2-P4）——不可改规则/蓝图
    AUTONOMOUS = "autonomous"           # 完全自主——可自动 READY→IN_PROGRESS，自动低风险修复
    FULL_AUTO = "full_auto"            # 全自动——可改非规则代码 + 自动创建任务卡
    EMERGENCY_ONLY = "emergency_only"  # 仅紧急模式——P0/P1 + 断路器触发时自动介入

class TaskCard(Task):
    """
    Vibe Coding 任务模型——继承 shared/schemas.py Task（31字段）+ 追加执行层字段

    父类（Task，metadata-registry.md §7 真源）提供：
      task_id(namespace-seq), namespace, seq, title, status(10态), priority(P0-P3),
      phase, execution_model, model_rationale, fallback_model, safety_level,
      directive, idempotent, classification, evolution_policy, estimate_hours,
      actual_hours, files_in_scope, deliverables, acceptance, depends_on,
      tags(扁平[]), session_id, waiting_for, ready_at, completed_at, created_at, updated_at

    本类追加 Vibe Coding 执行层字段——防漂移六维 + 门禁 + 管线 + v0.4.0 新增扩展
    """
    model_config = ConfigDict(extra="allow")

    # ---- 防漂移：上游（Vibe Coding 关键——AI需要知道读什么）----
    upstream_files: list[str] = Field(
        default_factory=list,
        description="执行前必须读取的文件完整绝对路径列表——AI 零记忆，不知道看什么"
    )

    # ---- 防漂移：下游（结构化产出描述）----
    downstream_outputs: list[dict] = Field(
        default_factory=list,
        description="执行后必须产出的文件 [{path: 完整绝对路径, description: 说明}]"
    )

    # ---- 防漂移：范围白名单（对标 K8s PodSecurityPolicy allowedCapabilities）----
    allowed_touch: list[str] = Field(
        default_factory=list,
        description="可以修改的文件白名单——完整绝对路径，防 AI 越界"
    )

    # ---- 防漂移：范围黑名单（对标 K8s PodSecurityPolicy forbiddenSysctls）----
    forbidden_touch: list[str] = Field(
        default_factory=list,
        description="禁止修改的文件黑名单——完整绝对路径或 glob，防 AI 误伤规则/蓝图"
    )

    # ---- 防漂移：规则引用（AGENTS.md §8.2 理念：AI需要知道该读哪些规则）----
    applicable_rules: list[dict] = Field(
        default_factory=list,
        description="必须遵守的治理规则 [{module_id, section, reason}]. min_length=1 建议"
    )

    # ---- 防漂移：上下文装配（G3 门禁校验依据——合并 AGENTS.md §5.1 "零记忆重启"）----
    context_assembly_manifest: list[dict] = Field(
        default_factory=list,
        description="上下文装配清单 [{file_path, reason}]——G3 门禁校验依据"
    )

    # ---- 防漂移：回滚（失败安全缓冲）----
    rollback_instructions: str = Field(
        default="",
        description="失败时如何撤销已有修改——AI 不知道如何撤回"
    )

    # ---- 门禁追踪 ----
    completed_gates: list[GateLevel] = Field(default_factory=list)
    blocked_gates: dict[str, str] = Field(default_factory=dict)

    # ---- 管线分配（v0.2.0 创新——对标 AGENTS.md §8.2 三层记忆模型）----
    assigned_pipeline: str = Field(default="A", description="A区（生产）/B区（审计）")
    pipeline_modules: list[str] = Field(default_factory=list, description="M1-M11 模块链")

    # ---- 产物 / 审计 / 知识 ----
    artifact_paths: list[str] = Field(default_factory=list)
    audit_findings: list["AuditFinding"] = Field(default_factory=list)
    ke_entries: list[str] = Field(default_factory=list)

    # ---- AI 自治（v0.4.0 升级：str→AISelfGovernanceLevel 五级枚举）----
    ai_autonomy_level: AISelfGovernanceLevel = Field(default=AISelfGovernanceLevel.SUPERVISED)
    autonomy_checklist: list[str] = Field(default_factory=list)

    # ---- 施工/验证状态 ----
    construction_status: str = Field(default="pending")
    verification_status: str = Field(default="unverified")

    # =================================================================
    # v0.4.0 新增字段——盲点审计驱动
    # =================================================================

    # ---- 父子任务层级（盲点 #1）----
    parent_task_id: str | None = Field(
        default=None,
        description="父任务 ID——Epic→TaskCard 层级。子任务全部 COMPLETED→父任务自动 COMPLETED"
    )

    # ---- 跨模块聚合（盲点 #28）----
    epic: str | None = Field(
        default=None,
        description="跨 Blueprint 的聚合标识——如 'phase-2-infra-upgrade'，聚合全局施工视图"
    )

    # ---- 自动 Retry 策略（盲点 #13）----
    retry_count: int = Field(default=0, ge=0, description="当前已重试次数")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")
    retry_backoff_seconds: int = Field(default=60, ge=10, le=3600, description="重试退避基础秒数——指数退避: base * 2^(n-1)")

    # ---- 可执行回滚 Snapshot（盲点 #2）----
    checkpoint_path: str | None = Field(
        default=None,
        description="执行前 git stash/快照 的文件路径——FAILED 时自动从此 checkpoint 恢复。格式: .zalpha/checkpoints/{task_id}_{timestamp}.diff"
    )

    # ---- 上下文窗口保护（盲点 #14）----
    estimated_context_tokens: int = Field(
        default=0, ge=0,
        description="M2 装配前估算的总 token 数（upstream_files + applicable_rules + pipeline prompt）——超过模型窗口 80% 时触发裁剪"
    )
    context_window_limit: int = Field(
        default=128000, ge=8192,
        description="模型上下文窗口上限——DeepSeek V4 Pro=128K, GLM=128K, Claude=200K"
    )

    # ---- 优先级传播（盲点 #7）----
    effective_priority: str = Field(
        default="P2",
        description="计算优先级——若 depends_on 中有 P0/P1，effective_priority 最低为其最高值。不改变 priority 字段"
    )

    # ---- diff-plan 约束（盲点 #11）----
    diff_plan_required: bool = Field(
        default=True,
        description="M3 代码生成前是否必须先产出 ExecutionPlan——M2 验证通过后才能实际写文件。P0/P1 强制 True"
    )

    # ---- 断路器状态（盲点 #15）----
    circuit_breaker_open: bool = Field(
        default=False,
        description="任务关联模型的断路器是否已打开——True 时自动路由到 fallback_model，跳过被熔断的模型"
    )

    # ---- 暂停/恢复（盲点 #3）----
    suspend_context_json: str | None = Field(
        default=None,
        description="SUSPENDED 状态时的上下文快照 JSON——恢复时从中断点继续"
    )

    # =================================================================
    # v0.5.0 新增字段——深度盲点审计驱动（#31-#41）
    # =================================================================

    # ---- Prompt 版本化（盲点 #31）----
    prompt_version: str | None = Field(
        default=None,
        description="任务使用的 M 模块 prompt 版本——格式 {module_id}_v{MAJOR}.{MINOR}.{PATCH}。用于追溯任务质量来源和 prompt 回退"
    )
    prompt_variant: str | None = Field(
        default=None,
        description="A/B 测试中的 prompt 变体标识（如 'baseline'/'experimental_v2'）——非 A/B 测试时为 None"
    )

    # ---- Saga 补偿事务（盲点 #32）----
    compensation_steps: list[dict] = Field(
        default_factory=list,
        description="Saga 补偿步骤清单 [{step_id, action_description, undo_command, file_paths_affected, timeout_seconds}]——执行失败时逆序执行 undo_command"
    )

    # ---- SLA 时限与老化升级（盲点 #34）----
    sla_deadline: str | None = Field(
        default=None,
        description="任务 SLA 截止时间 ISO 8601——超时触发自动升级。None 表示无 SLA 要求"
    )
    sla_escalation_policy: dict | None = Field(
        default=None,
        description="老化升级策略 {escalation_threshold_days: int, target_priority: str, max_escalation_priority: str}。如 {threshold: 30, target: 'P1', max: 'P0'}"
    )
    original_priority: str | None = Field(
        default=None,
        description="SLA 升级前的初始优先级——用于升级链追溯和完成后优先级恢复评估"
    )

    # ---- 模型快照锁定（盲点 #37）----
    model_snapshot_pinned: str | None = Field(
        default=None,
        description="锁定的模型 dated snapshot——如 'deepseek-v4-pro-2026-05-01'。None 时使用 model-registry.yaml 的 default_snapshot。保证任务可复现"
    )

    # ---- 跨 Session AI 思考态（盲点 #41）----
    thinking_state_json: str | None = Field(
        default=None,
        description="AI session 结束前自动保存的推理状态——{analysis_progress, pending_decisions, hypotheses, next_steps_planned, partial_results}。新 session 从断点继续而非从头"
    )

    # ---- 紧急模式（盲点 #36）----
    emergency_mode: bool = Field(
        default=False,
        description="紧急热修复模式——跳过 G1/G2/G3/G4/G5 门禁，仅保留 G0+G6+G7。事后 24h 内自动补审"
    )

    # ---- 跨任务知识隔离（盲点 #35）----
    cross_task_learning: bool = Field(
        default=False,
        description="是否允许跨任务学习——默认 False。True 时 AI 可从前序任务的经验中受益，但存在知识污染风险"
    )

    # ---- 依赖新鲜度指纹（盲点 #39）----
    dependency_fingerprint: dict[str, str] | None = Field(
        default=None,
        description="任务完成时记录的依赖项指纹——{depends_on_task_id: sha256(dep.downstream_outputs)}。依赖项被修改后指纹不匹配→标记 stale_dependency_warning"
    )

    # =================================================================
    # v0.6.0 新增字段——第三轮深度盲点审计驱动（#42-#48）
    # =================================================================

    # ---- 任务取消残留物追踪（盲点 #48）----
    cancelled_artifacts: list[str] = Field(
        default_factory=list,
        description="CANCELLED 任务留下的已写入文件路径清单——供 Owner 手动清理或 CLI cleanup-cancelled 使用"
    )

    # ---- 执行时前置漂移校验（盲点 #43）----
    upstream_files_content_hash: dict[str, str] | None = Field(
        default=None,
        description="G0 校验时记录 upstream_files 的 sha256——preflight 时对比。hash 不同→WARNING（文件被修改过但可继续）"
    )

    # ---- 消费者兼容性冲击报告（盲点 #44）----
    consumer_impact_report: list[dict] | None = Field(
        default=None,
        description="任务 COMPLETED→扫描 downstream_outputs 识别共享模块→列出消费者 {file, consumers, breaking_changes, status}。M7 增加 consumer compatibility check"
    )
    run_consumer_tests: bool = Field(
        default=False,
        description="任务完成后是否自动 pytest 所有消费者的测试——盲点 #44"
    )

    # ---- 中执行自适应重规划（盲点 #45）----
    replan_proposed: bool = Field(
        default=False,
        description="AI 在执行中发现意外→进入 REPLAN_PROPOSED 子状态→AI 提出替代方案。Owner 审批或自动（自治>AUTONOMOUS）"
    )

    # ---- 输出范围蔓延检测（盲点 #46）----
    modified_files_actual: list[str] | None = Field(
        default=None,
        description="M3 实际修改的文件列表——与 diff-plan 对比，检测范围蔓延"
    )
    lines_changed_actual: int | None = Field(
        default=None,
        description="M3 实际修改的行数——与 diff-plan 预估对比，偏差>50%→WARNING"
    )

    # ---- 跨 Session 上下文缓存（盲点 #47）----
    context_cache_key: str | None = Field(
        default=None,
        description="sha256(task_id+upstream_files_paths_sorted)——用于跨 session 上下文缓存的 key。ContextCache 复用避免重复读取"
    )
```

> **字段源流对照表**：

| 来源 | 字段数 | 提供什么 |
|------|:---:|------|
| `shared/schemas.py` Task（基座） | 31 | task_id/namespace/status/priority/execution_model/files_in_scope/deliverables/tags/depends_on/...——基础任务管理 |
| 本蓝图 TaskCard 扩展（v0.3.2） | +14 | 防漂移六维(upstream_files/downstream_outputs/allowed_touch/forbidden_touch/applicable_rules/context_assembly_manifest/rollback_instructions) + 门禁(gates) + 管线(pipeline) + 产物+审计+自治预留 |
| 本蓝图 TaskCard 扩展（v0.4.0 新增） | +11 | 父子层级(parent_task_id) + 聚合(epic) + Retry策略(retry_count/max_retries/retry_backoff_seconds) + Snapshot(checkpoint_path) + 上下文保护(estimated_context_tokens/context_window_limit) + 优先级传播(effective_priority) + diff-plan(diff_plan_required) + 断路器(circuit_breaker_open) + 暂停恢复(suspend_context_json) |
| 本蓝图 TaskCard 扩展（v0.5.0 新增） | +10 | Prompt版本化(prompt_version/prompt_variant) + Saga补偿(compensation_steps) + SLA时限(sla_deadline/sla_escalation_policy/original_priority) + 模型快照(model_snapshot_pinned) + 思考态(thinking_state_json) + 紧急模式(emergency_mode) + 知识隔离(cross_task_learning) + 依赖指纹(dependency_fingerprint) |
| 本蓝图 TaskCard 扩展（v0.6.0 新增） | +8 | 取消残留(cancelled_artifacts) + 漂移校验(upstream_files_content_hash) + 兼容冲击(consumer_impact_report/run_consumer_tests) + 重规划(replan_proposed) + 范围蔓延(modified_files_actual/lines_changed_actual) + 上下文缓存(context_cache_key) |

> **v0.4.0 状态机扩展**：
>
> 在原有 10 态基础上增加 `SUSPENDED` 状态：
> ```
> IN_PROGRESS → SUSPENDED（Owner/AI 主动暂停）
> SUSPENDED   → IN_PROGRESS（从 suspend_context_json 恢复）
> SUSPENDED   → FAILED（暂停超时 > 24h 自动失败）
> SUSPENDED   → CANCELLED（Owner 取消暂停任务）
> ```
>
> **父任务状态聚合规则**：
> ```
> 当 parent_task_id 非空时，父任务状态由子任务自动推导：
>   任一子任务 FAILED       → 父任务 BLOCKED
>   全部子任务 COMPLETED    → 父任务 COMPLETED
>   全部子任务 VERIFIED     → 父任务 VERIFIED
>   任一子任务 IN_PROGRESS  → 父任务 IN_PROGRESS
> ```

> **标签约定**（建议，非强制）：
>
> `tags` 为扁平 `list[str]`。如需结构化视图，AI 内部按前缀解析：
> - `fn:{function}` — 功能标签（如 `fn:security`、`fn:config`、`fn:governance`）
> - `ly:{layer}` — 层级标签（如 `ly:l01`、`ly:l02`）
> - `md:{model}` — 模型标签（如 `md:deepseek`、`md:glm`）
> - `st:{state}` — 状态标签（如 `st:active`、`st:frozen`）
> - `mo:{mode}` — 模式标签（如 `mo:manual`、`mo:auto`）
>
> 与旧版五轴 `tags_fn/tags_ly/tags_md/tags_st/tags_mo` 的关系：五轴降格为推荐约定——AI 内部解析，Schema 不强制。

#### 3.2.2 其他模型

```python
class DecompositionResult(BaseModel):
    total_tasks: int = Field(ge=0)
    tasks: list[TaskCard]
    dependency_graph: dict[str, list[str]] = Field(default_factory=dict)
    unassigned_items: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

class GateCheckResult(BaseModel):
    gate_id: GateLevel
    task_id: str
    passed: bool
    violations: list[str] = Field(default_factory=list)
    checked_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class AuditFinding(BaseModel):
    finding_id: str = Field(..., pattern=r"^F-\d{4}$")
    dimension: str
    severity: str = Field(..., pattern=r"^(critical|high|medium|low|info)$")
    description: str
    source_task: str
    resolved: bool = Field(default=False)
    resolution_note: Optional[str] = None
```

### 3.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `decompose()` | `blueprint_path` | ✅ | 绝对路径 + .md + doc_type=blueprint |
| | `output_dir` | ✅ | 必须是 `03_modules/{layer}/{module}/changes/{feature-id}/` |
| `create_task_card()` | `task` | ✅ | TaskCard——G0+G7 门禁通过 + task_repo.create() |
| `transition()` | `task_id` | ✅ | `{NAMESPACE}-{SEQ}`（如 `ADR-001`） |
| | `to_status` | ✅ | TaskStatus 合法值 + 状态机允许路径 |
| `dispatch()` | `task_id` | ✅ | status in {PENDING, READY, RETRY} |

### 3.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `decompose()` | `DecompositionResult`：N 张 TaskCard + SQLite 已写入 + .md 同步 | `FILE_NOT_FOUND` / `NO_CONSTRUCTION_GUIDE` / `G7_VIOLATIONS` |
| `create_task_card()` | TaskCard + task_repo.create() 成功 + .md 副本 | `GATE_BLOCKED(G0/G7)` / `DUPLICATE_ID(409)` / `PATH_NOT_COMPLIANT`(MTH-013) |
| `transition()` | task_repo.update_status() 成功 + events 记录 | `STATUS_MISMATCH(409)` / `ILLEGAL_TRANSITION(422)` / `GATE_BLOCKED(422)` |
| `dispatch()` | 管线+模型+M模块链已分配 | `INVALID_DISPATCH_STATUS(409)` / `NO_PIPELINE_AVAILABLE(503)` |

### 3.5 MCP 接口

> **MCP Server 位置**：[task_manager_server.py](file:///D:/ZephyrAlpha/src/zephyr/mcp/task_manager_server.py)
>
> **数据真源**：[task_repo.py](file:///D:/ZephyrAlpha/src/zephyr/db/task_repo.py)（SQLite）——MCP Server 不得使用内存字典

**Tools**：

| Tool | API | 输入 | 输出 | 对接 task_repo |
|------|-----|------|------|:---:|
| `decompose_blueprint` | `decompose()` | `{blueprint_path, output_dir}` | `{total_tasks, task_ids, warnings}` | `task_repo.create()` |
| `create_task` | `create_task_card()` | `{task_card_json}` | `{task_id, status}` | `task_repo.create()` |
| `update_task_status` | `transition()` | `{task_id, new_status}` | `{task_id, title, status, ...}` | `task_repo.transition()` |
| `get_task` | — | `{task_id}` | `{task_id, title, status, ...}` | `task_repo.get()` |
| `register_from_triage` | — | `{triage_path, namespace?, phase?}` | `{task_id, title, status, ...}` | `task_repo.create()` |

> **.md 双轨同步**：`_persist()` / `transition()` 成功后自动调用 `_taskcard_to_md()` 同步 `.md` 到 `docs_dir/tasks/{task_id}.md`。
> .md 文件为**只读人类可读副本**——SQLite 始终是真源。

**错误码**：`TASK_NOT_FOUND(404)` / `STATUS_MISMATCH(409)` / `ILLEGAL_TRANSITION(422)` / `GATE_BLOCKED(422)` / `VALIDATION_ERROR(400)` / `PATH_NOT_COMPLIANT(422)` / `REPO_NOT_INJECTED(500)`

### 3.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| TaskCard 新增字段 | ✅ 向后兼容 | 不影响已有任务卡 |
| TaskCard 删除/重命名字段 | ❌ 破坏性 | 需 Owner 审批 + 迁移 |
| TaskCard 基座切换（Task类） | ❌ 破坏性（与 v0.2.0） | v0.3.0 与 v0.2.0 TaskCard 不兼容——task_id格式/状态机/标签全变 |
| GateLevel 新增值 | ✅ 向后兼容 | 新门禁不破坏已有逻辑 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |
| MCP 输入 Schema 修改 | ⚠️ 需通知 | 消费者需更新参数 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## 4. 约束条件

### 4.1 技术约束

| # | 约束 | 原因 |
|---|------|------|
| 1 | Python 3.12+ | Pydantic V2 最低要求 |
| 2 | Pydantic V2 BaseModel——禁止 dataclass | ADR-0040 |
| 3 | 绝对路径——所有路径含 `D:\` | AGENTS.md §5.1 原则 3 |
| 4 | SQLite 唯一持久化数据库 | ADR-0030 |
| 5 | 任务卡 .md + SQLite 双轨制——task_repo.create() 后同步 .md | 机器可查(SQL) + 人可读(md) |
| 6 | 门禁在状态转换前执行 | GOV-TASK-004 §门禁机制 |
| 7 | 任务卡编号 `{NAMESPACE}-{SEQ}`（ADR/CP/KE/STD/DW/SRC/OPS） | metadata-registry.md §7.10 |
| 8 | 蓝图 draft/review 状态不得拆卡 | 内容不稳定 |
| 9 | **MTH-013 路径合规创建**——AI 不得自主决定目录层级 | 零自主创建权——必须先查索引 |
| 10 | **TaskCard 模型强制继承 `shared/schemas.py` Task**——禁止独立定义 | SSoT 唯一——Task 类已被 ADR-0030/ADR-0038/task_repo.py 引用 |
| 11 | **WIP（在制品）上限**：同时 IN_PROGRESS 任务 ≤ 5（P0/P1 ≤ 2）——超过时 dispatch() 拒绝 | 防止上下文碎片化 + AI session 冲突——盲点 #6/#8 |
| 12 | **并发文件冲突检测**：dispatch() 前检查所有 IN_PROGRESS 任务的 `allowed_touch` 交集——有交集时拒绝执行，等待前序任务完成 | 防止两个 AI session 覆盖彼此的修改——盲点 #6 |
| 13 | **上下文窗口溢出保护**：M2 装配前计算 estimated_context_tokens，超过 context_window_limit * 0.8 时触发裁剪（优先保留 applicable_rules + blueprint，裁剪 upstream_files 非关键部分） | DeepSeek V4 Pro=128K 窗口，超出→截断→幻觉——盲点 #14 |
| 14 | **API 断路器（Circuit Breaker）**：同一模型连续失败 3 次→自动熔断 5 分钟，期间所有请求自动路由到 fallback_model | DeepSeek API 不稳定是常态——盲点 #15 |
| 15 | **Retry 指数退避**：RETRY→IN_PROGRESS 自动等待 base * 2^(retry_count-1) 秒，max_retries 默认 3 | 盲点 #13 |
| 16 | **diff-plan 强制**：P0/P1 任务的 `diff_plan_required` 强制为 True——M3 生成代码前必须先产出 ExecutionPlan，M2 验证通过后才能写文件 | 比"生成完再审查"更可靠的执行范式——盲点 #11 |
| 17 | **幂等性强制检查**：PENDING/READY→IN_PROGRESS 前检查 downstream_outputs 是否已存在且内容符合预期——若已满足则跳过执行直接 COMPLETED | idempotent 字段的实质化——盲点 #10 |
| 18 | **依赖拓扑排序**：BlueprintDecomposer.decompose() 必须输出拓扑序——检测循环依赖，存在时拒绝拆解 | 盲点 #5 |
| 19 | **优先级链上传播**：若 depends_on 中有 P0/P1，下游任务 effective_priority ≥ 上游最高优先级 | P3 任务阻塞 P0 任务 → P3 实际上是 P0——盲点 #7 |
| 20 | **SUSPENDED 超时自动失败**：SUSPENDED 超过 24h → 自动 FAILED + 通知 Owner | 防止暂停任务永久挂起——盲点 #3 |
| 21 | **Prompt 版本化管理**：M1-M11 的 prompt template 必须语义化版本存储于 `prompts/{module_id}_v{MAJOR}.{MINOR}.{PATCH}.yaml`，禁止硬编码在 Python 代码中。TaskCard.prompt_version 必须记录任务使用的 prompt 版本 | Prompt 是 AI 执行质量的原材料——盲点 #31 |
| 22 | **Saga 补偿事务**：任务执行失败时按 compensation_steps 逆序执行 undo_command。补偿失败→写入 DeadLetter + 通知 Owner。补偿超时（单步>30s）→放弃+通知 Owner | 多步骤任务需要精细补偿而非全量快照——盲点 #32 |
| 23 | **模型质量退化检测**：M7（GLM审查）完成后对比任务 score vs QualityBaseline——偏差>15% 触发 QualityRegressionAlert。连续 3 个任务退化→自动回退到上一个已知好的 model_snapshot | 模型可以"正常调用"但输出质量下降——盲点 #33 |
| 24 | **SLA 时限自动升级**：sla_deadline 超时→SLAWatchdog 自动按 sla_escalation_policy 升级优先级（original_priority 记录初始值）。最多升级到 max_escalation_priority | P4 任务不应被永久遗忘——盲点 #34 |
| 25 | **跨 Session AI 思考态持久化**：AI session 结束前自动保存 thinking_state_json。新 session 接手 IN_PROGRESS 任务时→先读取 thinking_state_json→从断点继续 | Vibe Coding 中 Session 切换是常态——盲点 #41 |
| 26 | **跨任务知识隔离**：PipelineOrchestrator 每个 dispatch() 必须在新的 context window 中启动。执行前注入 neutralization prompt。cross_task_learning 默认 False，只有 Owner 明确允许时才跨任务保留经验 | AI 存在"上下文惯性"——盲点 #35 |
| 27 | **紧急热修复快速通道**：emergency_mode=True 时跳过 G1/G2/G3/G4/G5，仅保留 G0+G6+G7。事后 24h 内自动补跑完整审计（M6-M11）。补充：emergency_mode 不能在蓝图自动设置——仅 Owner 手动或 P0+tags=fn:critical 触发 | P0 故障修复不能等完整门禁链——盲点 #36 |
| 28 | **模型快照锁定**：TaskCard.model_snapshot_pinned 记录 dated snapshot。无快照时 dispatch() 自动填充 model-registry.yaml 的 default_snapshot。不可复现的任务产物 = 无法调试 | LLMOps P0 基线——盲点 #37 |
| 29 | **多文件原子写入**：M3 写入所有 downstream_outputs 时→先写 `{path}.zalpha_tmp_{task_id}` →全部成功→逐个 os.rename→任一失败→清理全部 tmp+FAILED | 代码库不能处于半完成态——盲点 #38 |
| 30 | **依赖新鲜度级联感知**：任务完成后记录 dependency_fingerprint。依赖项被修改后重新 COMPLETED→扫描所有含此指纹的任务→标记 stale_dependency_warning。受影响任务 G2 增加 dependency_freshness 检查 | 已完成依赖被修改→下游应重新验证——盲点 #39 |
| 31 | **任务系统组件降级运行**：gate_engine 故障→跳过非 P0 门禁，仅记录 WARNING；task_repo 故障→HALT（真源不可用）；pipeline_orchestrator 故障→降级为单模块 manual 模式。降级状态写入 system_health.json | 任务系统不能自己把自己关掉——盲点 #40 |
| 32 | **SQLite Schema 版本化迁移**：`migrations/` 目录增量 SQL 脚本 + `PRAGMA user_version` + Migrator.apply_pending() 启动时自动执行 + 每个迁移包裹 `BEGIN...COMMIT` + 失败→rollback+阻止启动 | 模型进化→数据真源也必须进化——盲点 #42 |
| 33 | **任务取消安全协议**：cancel_task() 扫描 `.zalpha_tmp_{task_id}` 清理→记录 cancelled_artifacts→CANCELLED 任务的 G7 增加孤儿 tmp 检查 | 取消不是标记一下就完了——盲点 #48 |
| 34 | **执行时前置条件漂移校验**：dispatch() 前 PreflightCheck：逐个 `os.path.exists` + `os.R_OK` upstream_files →任一不可访问→HALT+通知 | 创建时通过≠执行时通过——盲点 #43 |
| 35 | **共享模块向后兼容性冲击分析**：COMPLETED→识别共享模块→ImpactAnalysis 列出所有消费者→M7 增加 consumer compatibility check→可选 run_consumer_tests 自动 pytest | AI 的涟漪效应不可预测——盲点 #44 |
| 36 | **中执行自适应重规划**：M3 发现意外（溢出/编码/缺失）→进入 REPLAN_PROPOSED 子状态→AI 提议替代方案→Owner 审批或自动（自治>AUTONOMOUS） | Plan-and-Solve 弹性调整——盲点 #45 |
| 37 | **输出范围蔓延检测**：M3 完成后对比 diff-plan：modified_files_actual vs planned →超出→WARNING；lines_changed_actual vs planned →偏差>50%→WARNING；forbidden_touch 触发→FAIL | AI Scope Creep 是常态非异常——盲点 #46 |
| 38 | **跨 Session 上下文复用**：ContextCache key=sha256(task_id+upstream_files) →dispatch() 先查缓存→hash全匹配→复用 summary（token cost: 500→50000）→任一不匹配→全量重读 | Vibe Coding 中跨 3-5 个 Session 的 token 浪费——盲点 #47 |

### 4.2 容量估算

| 维度 | 当前 | 峰值 | 极限 | 够用？ |
|------|:--:|:--:|:--:|:--:|
| 蓝图 | 6（含 deprecated） | 200+ | 无上限 | ✅ |
| 任务卡(SQLite) | 当前 task_metadata.db | 2000+ | 10000/域 | ✅ |
| Change Folder(.md) | 1 | 200+ | 文件系统 | ✅ |
| SQLite | <100MB | <100MB | ~281TB | ✅ |
| M 模块 | 11 | 20 | 30+ | ✅ |
| 模型 | 3 | 8 | 受控词表可扩展 | ✅ |

### 4.3 迁移/废弃方案

| # | 对象 | 当前位置 | 状态 | 迁移方案 |
|---|------|---------|:--:|------|
| 1 | MOD-INF-003 | `task-card-kms/blueprint.md` | deprecated | 内容已合并→stable 物理删除 |
| 2 | MOD-INF-004 | `vibe-coding-pipelines/blueprint.md` | deprecated | 内容已合并→stable 物理删除 |
| 3 | v0.2.0 TaskCard 模型 | `src/zephyr/core/models.py` | deprecated | v0.3.0 TaskCard 继承 shared/schemas.py Task——重写 |
| 4 | 场外草稿 2 份 | `模块候选池/...` | 内容已纳完 | 待 Owner 决定删除/归档 |

---

## 5. 依赖关系

| 依赖 | 类型 | 内容 | 版本 |
|------|:---:|------|------|
| PS-STD-001 | 必须 | §7——task_id / 语义28 / 追踪3 / Task共31 / 状态机 | ≥2.0.0 |
| PS-STD-011 | 必须 | MTH-012 涌现式设计 + MTH-013 路径合规 | ≥2.6.0 |
| GOV-DOC-002 | 必须 | §5.1.2 路径映射 | — |
| GOV-TASK-001 | 必须 | 任务卡操作指南 | ≥3.0.0 |
| GOV-TASK-004 | 必须 | 取消权限、优先级裁决 | ≥2.0.0 |
| GOV-TASK-005 | 必须 | 关闭三步法 | ≥1.1.0 |
| MOD-INF-005 | 必须 | 脚本系统 12 维度 | ≥3.0.0 |
| TEMPLATE-TASK-001 | 必须 | 任务卡 .md 模板 | ≥1.0.0 |
| REG-LLM-001 | 必须 | 模型基准排名 | ≥1.1.0 |
| GOV-AI-002 | 必须 | 模型路由策略 | ≥2.0.0 |
| shared/schemas.py | 必须 | `Task` 31 字段（语义28+追踪3）TaskCard 基座 | 现有代码 |
| task_repo.py | 必须 | SQLite CRUD + 10状态机 + N:N task_files | 现有代码 |
| task-completion-gate.py | 必须 | G7 门禁逻辑——需同步 | 现有代码 |
| task-card-meta-registry.yaml | scaffold | 任务卡系统迁移追踪 | V-13 |

---

## 6. 产出物存放目录

> ⚠️ 所有路径必须与 GOV-DOC-002 §5.1.2 一致。MTH-013 强制。

| 产出物 | 完整绝对路径 | 存储介质 |
|--------|------------|:--:|
| 蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md` | .md |
| 任务卡（SQLite 真源）| `D:\ZephyrAlpha\data\zalpha_metadata.db` — tasks 表 | SQLite |
| Task 模型基座（31 字段）| `D:\ZephyrAlpha\src\zephyr\shared\schemas.py` | .py |
| TaskCard 扩展模型（52字段）| `D:\ZephyrAlpha\src\zephyr\core\models.py` | .py |
| SQLite CRUD + 状态机 | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | .py |
| SQLite Schema + 迁移链 | `D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py` | .py |
| N:N 文件映射 | `D:\ZephyrAlpha\src\zephyr\orchestrator\file_task_mapper.py` | .py |
| 蓝图拆解器 | `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py` | .py |
| MCP Server（5 Tool）| `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py` | .py |
| MCP Tool 契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool_contracts.yaml` | .yaml |
| 知识审阅池 | `D:\ZephyrAlpha\src\zephyr\kb\triage.py` | .py |
| 管线编排器 | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py` | .py |
| 上下文装配器 | `D:\ZephyrAlpha\src\zephyr\context_engine\context_assembler.py` | .py |
| G7 任务完成门禁 | `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` | .py |
| 蓝图-代码同步校验 | `D:\ZephyrAlpha\scripts\governance\d5_architecture\validate_blueprint_code_sync.py` | .py |
| 架构模型（DB 层）| `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | .yaml |
| 测试 | `D:\ZephyrAlpha\tests\` | .py |

---

## 7. 集成目标

| 集成目标 | 方式 | 集成点 | 验证 |
|---------|------|--------|------|
| shared/schemas.py（Task基座） | TaskCard 继承 Task | `core/models.py → from zephyr.shared.schemas import Task` | isinstance(task_card, Task) == True |
| task_repo.py（SQLite CRUD） | BlueprintDecomposer → task_repo.create() | `decompose() → self.repo.create(task)` | SQLite tasks 表新增行 |
| task_repo.py（状态机） | TaskLifecycleManager → task_repo.update_status() | `transition() → self.repo.update_status()` | events 表新增事件 |
| 脚本系统（MOD-INF-005） | B区完成→事件触发 C区 | `execute_pipeline(B) → audit_batch()` | B区后检查 Finding |
| MCP Server | 新增 decompose_blueprint 等 5 Tool | `task_manager_server.py`——对接 task_repo | ListTools 确认 |
| 仪表盘 | 新增 `/tasks` 路由 | `app.py → list_tasks` | 浏览器渲染 |
| context_engine | G3→触发装配 | `transition(IN_PROGRESS) → assemble()` | 检查上下文 |

---

## 8. 需要更新的相关内容

| # | 文件 | 更新 |
|---|------|------|
| 1 | `blueprint-registry.yaml` | MOD-INF-006 条目更新（v0.3.0） |
| 2 | `task-card-meta-registry.yaml` | 更新迁移状态——v0.2.0→v0.3.0 |
| 3 | `core/models.py` | 重写——TaskCard 继承 shared/schemas.py Task |
| 4 | `core/blueprint_decomposer.py` | 重写——输出 task_repo.create() + .md 同步 |
| 5 | `mcp/task_manager_server.py` | 重写——接入 task_repo（SQLite），实现 5 Tool |
| 6 | `gates/task_completion_gate.py` | 同步 G7 门禁逻辑 |

---

## 9. 已知风险与缓解（v0.4.0 扩展）

| # | 风险 | 概率 | 影响 | 缓解 | 盲点# |
|---|------|:--:|:--:|------|:--:|
| 1 | **任务卡 .md 与 SQLite 不同步** | 中 | 高 | transition() 前双轨一致性校验 | — |
| 2 | **蓝图 §11 不完整→拆卡遗漏** | 高 | 高 | MTH-012 涌现式设计——§11 必须极度详细；unassigned_items >10%→拒绝拆解 | — |
| 3 | **DeepSeek V4 Pro 幻觉**（幻觉率 94%） | 高 | 高 | GLM 审查纠错→Claude 关键兜底——三层防御 | — |
| 4 | **DeepSeek V4 Pro API 不可用** | 低 | 高 | fallback_model 明确降级 + v0.4.0 断路器自动熔断→路由 fallback | #15 |
| 5 | **路径漂移**——AI 自作主张建目录 | 中 | 高 | MTH-013 零自主创建权——强制索引查询 | — |
| 6 | **Change Folder 爆炸** | 低 | 低 | 任务卡状态 CANCELLED/VERIFIED 后 Change Folder 可归档/删除 | — |
| 7 | **TaskCard 基座切换破坏已有代码** | 高 | 高 | experimental 步骤3——同步重写 `core/models.py`/`blueprint_decomposer.py`/`task_manager_server.py`；不留两套模型 | — |
| 8 | **不允许在 MOD-INF-006 上出现 MyMoney 风格全量代码重写投机重工**（改建比新建难——对老蓝图改造成本更高） | 中 | 极高 | **P0 铁壁（硬性约束）**：① 增量改造——只做 MOD-INF-006 未覆盖的新增字段/数据模型/约束/风险/门禁；② **零越界碰蓝图层——D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md** 就是 T-006-ADT-2（Session 743a63d7）的 diff 主体；其他文件一律不要碰，尤其是 shared/schemas.py 和 core/models.py。③ 不搞拆卡→不完→拆新卡的死循环，也不在未明确要求时将 30 个盲点全部转换为独立任务卡 | — |
| 9 | **2 个 AI session 同时修改重叠文件**（并发冲突） | 中 | 高 | v0.4.0：dispatch() 前检查所有 IN_PROGRESS 任务的 allowed_touch 交集——有交集时拒绝执行 | #6 |
| 10 | **上下文窗口溢出**（以为 AI 读了，实际被截断） | 高 | 极高 | v0.4.0：M2 装配前计算 estimated_context_tokens，超过窗口 80% 触发裁剪——优先保留规则引用 | #14 |
| 11 | **同样的错误发生两次**（无失败模式学习） | 高 | 中 | v0.4.0：FailurePattern 自动匹配引擎 + mitigation 应用 + 匹配失败时创建新模式 | #20 |
| 12 | **Owner 离线时系统卡死**（P0 任务 BLOCKED→无人知晓） | 高 | 极高 | v0.4.0：Owner 通知机制（飞书/桌面/日志）+ 断路器自动降级 + AI 自治边界五级 | #17/#25 |
| 13 | **API 费用失控**（无预算控制） | 低 | 中 | v0.4.0：CostTracker 按 model/session 统计，超预算告警/熔断 | #18 |
| 14 | **任务系统自身漂移**（蓝图-代码不一致） | 高 | 极高 | v0.4.0：`validate_blueprint_code_sync.py` + 自诊断健康检查——每个 session 启动时扫描 | #30 |
| 15 | **M1-M11 管线硬编码**（扩展困难） | 中 | 中 | v0.4.0：M 模块声明式配置（YAML），新增 M 模块不修改 orchestrator 代码 | #29 |
| 16 | **任务执行半完成状态**（超时后仍 IN_PROGRESS，文件半修改） | 中 | 高 | v0.4.0：超时→自动 FAILED + 从 checkpoint_path 恢复快照 + 通知 Owner | #12 |
| 17 | **循环依赖导致任务链死锁** | 低 | 极高 | v0.4.0：BlueprintDecomposer 拆解时拓扑排序，检测到循环→拒绝拆解并报错 | #5 |
| 18 | **Prompt 质量退化**（AI 修改 prompt 后质量下降，无法回退） | 高 | 极高 | v0.5.0：Prompt 版本化管理——SemVer + Git 存储 + `prompt_rollback` 一键回退 + CI 回归测试 | #31 |
| 19 | **多步骤任务失败后代码库处于半修改态**（当前快照恢复过于粗暴） | 中 | 高 | v0.5.0：Saga 补偿事务——逆序执行 undo_command，失败写入 DeadLetter | #32 |
| 20 | **模型质量静默退化**（API 正常但输出质量下降 20%+，3天后才发现） | 高 | 极高 | v0.5.0：QualityBaseline 基线对比 + M7 偏差检测 + 连续退化自动回退 model_snapshot | #33 |
| 21 | **低优先级任务被永久遗忘**（P4 任务 90 天无人执行无告警） | 中 | 高 | v0.5.0：SLA 时限 + SLAWatchdog 自动升级 + 老化 bucket 摘要（`zalpha aging` CLI） | #34 |
| 22 | **AI 受前序任务影响选错技术方案**（知识污染——前任务用了 Strategy→后任务最早该用 Observer 也选了 Strategy） | 中 | 高 | v0.5.0：跨任务知识隔离——每次 dispatch 新 context + neutralization prompt + 默认跨任务学习关 | #35 |
| 23 | **P0 故障修复被门禁链卡住**（关键脚本 bug→修复等 15 分钟→业务受损） | 中 | 高 | v0.5.0：紧急热修复快速通道——跳过 G1-G5，24h 内补审 | #36 |
| 24 | **模型供应商无声更新导致任务行为不一致**（5月1日通过≠5月15日通过） | 高 | 高 | v0.5.0：模型快照锁定——model_snapshot_pinned 记录 dated version，可复现 | #37 |
| 25 | **系统崩溃时多文件写入半途中断**（5个文件只写了3个→代码库不一致） | 低 | 高 | v0.5.0：原子写入——先写 .tmp →全部成功→逐个 rename | #38 |
| 26 | **已完成的依赖被修改后下游任务基于过期前提**（ADR-001修正后→依赖它的 SRC-005 持有旧架构决策） | 中 | 高 | v0.5.0：依赖指纹 + 级联 stale_dependency_warning + G2 freshness 检查 | #39 |
| 27 | **SQLite Schema 与 Pydantic 模型版本割裂**（v0.6.0 代码读 v0.3.2 数据→OperationalError——新字段无对应列） | 高 | 极高 | v0.6.0：`migrations/` 增量SQL脚本 + `PRAGMA user_version` 自动迁移 + 启动时 Migrator.apply_pending() | #42 |
| 28 | **任务在排队期间 upstream_files 被删除/修改**（G0通过→排队→执行时 FileNotFoundError） | 中 | 高 | v0.6.0：dispatch() 前 PreflightCheck + upstream_files_content_hash 对比 | #43 |
| 29 | **AI 修改共享模块后约 50% 概率破坏消费者**（GitChameleon 基准——跨版本兼容仅 48-51% 成功率） | 高 | 高 | v0.6.0：ImpactAnalysis 消费者兼容检查 + M7 consumer compatibility check + run_consumer_tests | #44 |
| 30 | **AI 执行中遇到意外→只能 FAIL→Owner 介入**（无弹性调整→计划与现实脱节时效率低下） | 中 | 中 | v0.6.0：REPLAN_PROPOSED 子状态 + AdaptivePlanningGate + 自动拆分降级 | #45 |
| 31 | **AI 实际修改超出计划范围无人知晓**（计划改 3 个文件→实际改了 7 个→Owner 事后才发现） | 中 | 中 | v0.6.0：diff-plan vs actual 对比 + scope_creep WARNING + forbidden_touch FAIL | #46 |
| 32 | **同一个 Task 跨 3-5 个 Session 重复读取上游文件浪费 Token**（5万tokens×3次=15万tokens） | 低 | 中 | v0.6.0：ContextCache hash 匹配复用 + 缓存 TTL=session 生命周期 | #47 |
| 33 | **取消中的任务留下半完成文件→下一个任务读到不完整数据**（取消无清理协议→文件系统残留） | 低 | 中 | v0.6.0：cancel_task() 清理 tmp + cancelled_artifacts 记录 + cleanup-cancelled CLI | #48 |

---

## 10. 后果

### 正面后果

1. **单蓝图自包含**：AI 读一份文件理解全链路——零跳转。
2. **TaskCard 继承 Task**：基座对齐 metadata-registry.md §7 真源——不留两套并行模型，旧 v0.2.0 TaskCard 废弃。
3. **防漂移六维**：上游/下游/范围白名单/范围黑名单/规则引用/上下文装配/回滚全部结构化——AI 凭任务卡单文件施工。
4. **task_id 自文档**：`ADR-001` 一眼知道是架构决策——对标 Jira PROJ-123。
5. **SQLite + .md 双轨**：机器可查(SQL) + 人可读(md)——互补不可替代。
6. **三层防御幻觉**：DeepSeek 生产 → GLM 审查 → Claude 兜底——模型分工有 REG-LLM-001 数据支撑。
7. **路径合规创建**：MTH-013——AI 永不自行决定目录层级。

### 负面后果

1. **基座切换有破坏性**：v0.2.0 TaskCard（34字段独立模型）→ v0.3.0 TaskCard（继承 Task）不兼容——需同步重写 3 个 .py 文件。
2. **任务卡字段多**（28+14=42字段）→ 填卡成本高。缓解：拆解算法自动填充 80%，Owner 只需审核。
3. **蓝图较长**→ AI token 压力。缓解：§11 施工指引结构化——AI 先读目标+施工，其余按需查。

---

## 11. 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 |
|---|--------|---------|
| 1 | 已读取本蓝图全部内容（§1-§10 架构 + §11 施工指引） | 逐节确认 |
| 2 | 已读取必备链接中所有真源文件（共 14 项） | 逐个打开 |
| 3 | shared/schemas.py `Task` 已理解——语义28+追踪3=31 字段 + 10 状态机 | 能回答 Task.task_id 格式 |
| 4 | task_repo.py CRUD + 状态机转换表已理解 | 能回答"create/get/update/upsert/list 参数" |
| 5 | metadata-registry.md §7 任务卡字段定义已理解 | 能回答"哪个字段是 flat tags" |
| 6 | MTH-013 路径合规创建已理解 | 能执行三步决策流程 |

### 11.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段 | 2 个 Phase（scaffold 善后 / experimental 补给——重写三个核心 .py） |
| 施工模式 | **重写型**——v0.2.0 代码（task_id格式/状态机/存储）与 v0.3.0 契约不兼容 |
| 核心风险 | 破坏性变更——core/models.py / blueprint_decomposer.py / task_manager_server.py 需同步重写 |

### 11.2 前置条件

| # | 依赖 | 当前 | 满足？ |
|---|------|:--:|:--:|
| 1 | shared/schemas.py Task 类存在 | ✅ | ✅ |
| 2 | task_repo.py 可用 | ✅ | ✅ |
| 3 | metadata-registry.md §7 字段定义 active | ✅ | ✅ |
| 4 | PS-STD-011 ≥ 2.6.0 | ✅ | ✅ |
| 5 | GOV-AI-002 ≥ 2.0.0 | ✅ | ✅ |
| 6 | 本蓝图 v0.3.0 Owner 已确认 | ☐ | ❌ |

### 11.3 实施步骤

#### 善后：注册表 + 元数据同步

##### 步骤 1：更新蓝图注册表

| 产出位置 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` |
|---------|------|
| 验收标准 | MOD-INF-006 条目 version→0.3.0，blueprint_status→approved，change_log 追加 v0.3.0 条目 |

**创建/更新文件清单**：

| 文件 | 操作 | 完整绝对路径 |
|------|:--:|------------|
| blueprint-registry.yaml | 修改 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` |

##### 步骤 2：同步 task-card-meta-registry.yaml（迁移追踪）

| 产出位置 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml` |
|---------|------|
| 验收标准 | 记录 MOD-INF-006 v0.2.0→v0.3.0 迁移——TaskCard 基座从独立模型→继承 shared/schemas.py Task |

---

#### 补给：三大核心 .py 同步重写

> ⚠️ v0.3.0 是破坏性变更——以下 3 个文件的旧版本（v0.2.0 时期）与新版契约不兼容，必须同步重写。

##### 步骤 3：重写 core/models.py — TaskCard 继承 Task

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\core\models.py` |
|---------|------|
| 内容变更 | ① TaskCard 类从独立 BaseModel → 继承 `shared/schemas.py` Task；② task_id format 从 `TASK-INF-XXXX` → `{NAMESPACE}-{SEQ}`；③ TaskStatus enum 从 CREATED/QUEUED/.../CLOSED → PENDING/IN_PROGRESS/.../CANCELLED（10态）；④ 删除 tags_fn/tags_ly/tags_md/tags_st/tags_mo 五轴字段→改用 Task 父类的 flat `tags[]`；⑤ 保留并追加 Vibe Coding 执行层字段（防漂移六维+门禁+管线）|
| 验收标准 | ① `isinstance(TaskCard(...), Task) == True`；② task_id pattern `^(ADR|CP|KE|STD|DW|SRC|OPS)-\\d+$`；③ status ∈ TaskStatus enum；④ upstream_files/downstream_outputs/allowed_touch/forbidden_touch/applicable_rules/context_assembly_manifest/rollback_instructions 字段存在；⑤ applicable_rules min_length≥1 建议但非强制 |

##### 步骤 4：重写 blueprint_decomposer.py — 对接 task_repo

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py` |
|---------|------|
| 内容变更 | ① decompose() 不再写 .md 为主——改为 `task_repo.create(task)`（写 SQLite）为主，.md 同步生成为辅；② task_id 生成从 `TASK-INF-0001` 自增 → 按 `{NAMESPACE}-{SEQ}` 格式（解析蓝图所属域+查询 task_repo 当前最大 seq）；③ 每张任务卡执行 G0/G7 门禁；④ task_repo.create() 成功后同步生成 .md 副本 |
| 验收标准 | ① decompose(本蓝图) → task_repo.list_tasks() 返回 N≥1 条记录；② 每条记录 task_id 格式 `{NAMESPACE}-{SEQ}`；③ changes/ 下有对应 .md 副本；④ G7 门禁通过 |

##### 步骤 5：重写 task_manager_server.py — MCP 接入 SQLite

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py` |
|---------|------|
| 内容变更 | ① MCP Server **必须初始化 task_repo 连接**（SQLite），禁止使用内存 dict 作为任务存储；② 实现 6 个 Tool（原有 4 + 新增 register_from_triage + sync_file_state）；③ decompose_blueprint Tool 调用步骤4 的 BlueprintDecomposer；④ create_task/update_status/list_tasks 直接对接 task_repo |
| 验收标准 | ① A区管线输出的任务卡 task_repo.create()写入成功；② list_tasks() 返回 SQLite 中的真实任务列表；③ sync_file_state() 可检测 .md 副本与 SQLite 状态是否一致 |

##### 步骤 6：补齐 context_engine + 确认 M1-M11（延续 v0.2.0 experimental）

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\context_engine\` / `pipeline\` |
|---------|------|
| 验收标准 | ① G3 门禁可用——context_assembly_manifest 中的文件全部可装配；② M1-M11 模块引用对齐 Vibe Coding 执行层字段（pipeline_modules/assigned_pipeline）；③ 管线模型模型执行数据记录到 task_repo events 表 |

**M 模块分工表**（基于 GOV-AI-002 v2.0.0 模型路由策略）：

| 模块 | 管线 | 职责 | 模型 | 为何用此模型 |
|------|:---:|------|:---:|------|
| M1 | A区 | 任务卡解析→结构化执行计划 | DeepSeek V4 Pro | 代码解析 = 主力场景 |
| M2 | A区 | 上下文装配→调用 context_engine | DeepSeek V4 Pro | 工具调用 = 主力场景 |
| M3 | A区 | 代码/文档生成——核心生产 | DeepSeek V4 Pro | 代码生成 = 主力场景 |
| M4 | A区 | 格式校验 | DeepSeek V4 Pro | 格式校验 = 主力场景 |
| M5 | A区 | 产物打包 | GLM | 格式化打包 = 低风险场景 |
| M6 | B区 | 差异检测——产出 vs 期望 | DeepSeek V4 Pro | 差异分析 = 主力场景 |
| M7 | B区 | **深度审查**——逐个文件逻辑/合规 | **GLM** | 幻觉率 4%——国产最优。DeepSeek 幻觉率 94% 不适合审查 |
| M8 | B区 | 标准合规——PS/GOV/ADR | DeepSeek V4 Pro | 规则匹配 = 主力场景 |
| M9 | B区 | 风险评估——OWASP LLM Top 10 | DeepSeek V4 Pro | 风险分析 = 主力场景 |
| M10 | B区 | 审计报告→Finding 格式 | DeepSeek V4 Pro | 报告生成 = 主力场景 |
| M11 | B区 | 门禁裁决——G5/G6 | DeepSeek V4 Pro | 门禁逻辑 = 主力场景 |

**Claude 特种救援触发条件**（GOV-AI-002 §三）：

| 条件 | DeepSeek 执行失败 3 次 / GLM 审查连续驳回 2 次 / Owner 标记"关键" / tags=fn:security / tags=st:experimental |

### 11.4 回滚方案

| 步骤 | 回滚 |
|------|------|
| 1（注册表） | 手动回退 YAML |
| 2（元注册表） | 手动回退——恢复 v0.2.0 迁移状态 |
| 3（models.py） | 恢复 v0.2.0 独立 TaskCard 模型 |
| 4（decomposer） | 恢复旧版——用 .md 为主的方式 |
| 5（MCP Server） | 恢复旧版 4 Tool |
| 6（context+M1-M11） | 此步骤与 v0.2.0 相同——回滚成本低 |

### 11.5 施工完成标准

| # | 产出物 | 路径 |
|---|--------|------|
| 1 | blueprint-registry.yaml 已更新 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` |
| 2 | task-card-meta-registry.yaml 迁移追踪 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml` |
| 3 | core/models.py — TaskCard 继承 Task | `D:\ZephyrAlpha\src\zephyr\core\models.py` |
| 4 | blueprint_decomposer.py — 对接 task_repo | `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py` |
| 5 | task_manager_server.py — MCP 6 Tool | `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py` |
| 6 | context_engine 补齐 + M1-M11 确认 | `context_engine/` + `pipeline/` |

### 11.6 施工状态

| 字段 | 值 |
|------|-----|
| construction_status | completed |
| verification_status | verified |

---

## 12. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 任务系统——v0.3.0融合最优，experimental待重写

### 13.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/core/blueprint_decomposer.py` | ✅ 已实现 | |
| `src/zephyr/core/models.py` | ✅ 已实现 | |
| `src/zephyr/pipeline/models.py` | ✅ 已实现 | |
| `src/zephyr/pipeline/pipeline_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/db/task_repo.py` | ✅ 已实现 | |
| `src/zephyr/db/sqlite_schema.py` | ✅ 已实现 | |
| `src/zephyr/mcp/task_manager_server.py` | ✅ 已实现 | |
| `src/zephyr/gates/task_completion_gate.py` | ✅ 已实现 | |

### 13.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_task_repo.py` | ✅ 已实现 | |
| `tests/unit/test_sqlite_schema.py` | ✅ 已实现 | |
| `tests/unit/test_mcp_servers.py` | ✅ 已实现 | |
| `tests/unit/test_pipeline_orchestrator.py` | ✅ 已实现 | |
| `tests/unit/test_task_completion_gate.py` | ✅ 已实现 | |
| `tests/adversarial/test_task_system_red_team.py` | ✅ 已实现 | |

### 13.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §13（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 13. 盲点审计与路线图（v0.4.0 新增，v0.6.0 扩展至 48 盲点八大类）

> **审计范围**：蓝图 v0.3.2 → v0.6.0 + ADR-0038 + ADR-0040 + ADR-0030 + 全部核心源码（schemas/models/task_repo/pipeline_orchestrator/gate_engine/MCP server/decomposer）+ 治理文档。
> **审计方法（三轮递进）**：交叉对比 ① 专业机构（Jira/Linear/ServiceNow/Azure DevOps/Asana）+ ② 氛围编程社区（bolt.new/v0/Cursor/Replit Agent/Windsurf/CrewAI）+ ③ AI Agent 前沿（Temporal.io Durable Execution + Plan-and-Solve + LangChain Deep Agents + Transactional AI）+ ④ LLMOps 2025-2026（Prompt 版本化/模型快照/质量退化检测）+ ⑤ 基础设施级可靠性（Saga 补偿/原子写入/组件降级/依赖新鲜度）+ ⑥ 数据持久化与运行时演化（Schema 迁移/取消安全/前置漂移/向后兼容冲击）+ 1人+AI 维护特需 + 架构完整性。
> **产出**：48 个盲点，八大类，含优先级、影响评估、建议方案、对照约束编号。

### 13.1 盲点总览

| 大类 | 盲点数 | 覆盖领域 |
|------|:--:|------|
| A. 任务模型与生命周期 | 4 | 父子层级、Snapshot回滚、暂停恢复、Hook事件 |
| B. 依赖与调度 | 7 | 拓扑排序、并发冲突、优先级传播、WIP限制、任务队列、紧急通道、中执行自适应重规划 |
| C. AI 执行可靠性 | 11 | 幂等保证、diff-plan、超时清理、Retry退避、上下文溢出、断路器、知识隔离、模型快照、执行时前置校验、输出范围蔓延检测、中执行上下文漂移 |
| D. 可观测性与审计 | 5 | 全链路Trace、Owner通知、成本预算、CLI摘要、失败模式匹配 |
| E. 1人+AI 维护特需 | 8 | 零配置启动、Dogfooding、渐进增强、AI维护手册、AI自治边界、SLA老化升级、跨Session思考态、跨Session上下文复用 |
| F. 架构结构盲点 | 7 | 意图→蓝图、KMS契约、跨模块聚合、M模块插件化、自诊断、组件降级运行、向后兼容性冲击分析 |
| G. AI 质量管理与深度可靠性（v0.5.0 大类） | 4 | Prompt版本化+回退、Saga补偿事务、模型质量退化检测、多文件原子写入 |
| **H. 数据持久化与运行时演化**（v0.6.0 新增大类） | **2** | **SQLite Schema 迁移框架、任务取消安全协议** |

### 13.2 盲点详细登记

#### A. 任务模型与生命周期

##### 盲点 #1 — 缺少父子任务层级（Epic→Story→Sub-task）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `depends_on` 是扁平列表，无层级语义 |
| 为什么是盲点 | 蓝图拆解生成的 6 个 TASK-INF-XXXX 之间只有线性依赖，无法表达"这个大任务包含 5 个小任务"。父任务状态 = 聚合子任务状态是 Jira/Linear/Asana 的基线功能 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `parent_task_id: str \| None` + 父子状态聚合规则 |
| 约束编号 | §4.1 约束 #10 |

##### 盲点 #2 — 缺少任务执行前 Snapshot / 可执行回滚

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `rollback_instructions` 是自由文本，AI 无法可靠执行 |
| 为什么是盲点 | bolt.new/Cursor/Replit Agent 都实现了 checkpoint→回退机制。自由文本回滚对 AI 来说不可执行 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `checkpoint_path: str \| None` + FAILED 时自动恢复 |
| 约束编号 | §4.1 约束 #15 |

##### 盲点 #3 — 缺少 SUSPENDED 暂停/恢复状态

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 10 态状态机中没有暂停状态 |
| 为什么是盲点 | 1人+AI 场景下 Owner 可能中途暂停长任务、两个 AI session 之间需要交接。当前只能 FAILED→RETRY 再从头开始 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——状态机增加 SUSPENDED + `suspend_context_json` 字段 + 24h 自动超时 |
| 约束编号 | §4.1 约束 #20 |

##### 盲点 #4 — 缺少 Hook/事件系统

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 状态变更后的行为硬编码在 PipelineOrchestrator 和 TaskRepository 中 |
| 为什么是盲点 | 无法声明式配置"状态变为 X 时自动做 Y"。所有联动逻辑散落在不同类的 `if status == X: do_Y()` 中 |
| 解决状态 | 🔲 **v0.5.0 规划**——引入 EventHook 声明式注册（`{trigger_status, action, module_id}`），替代硬编码 if-else |
| 约束编号 | 待新增 |

#### B. 依赖与调度

##### 盲点 #5 — 缺少依赖拓扑排序和死锁检测

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | `depends_on` 是扁平列表，无循环检测，无拓扑序 |
| 为什么是盲点 | A depends_on B, B depends_on A → 两个任务永远无法开始。没有检测意味着可能创建死锁而不自知 |
| 解决状态 | ✅ **已在本蓝图 §4.1 解决**——约束 #18：BlueprintDecomposer 必须输出拓扑序，检测循环依赖时拒绝拆解 |
| 约束编号 | §4.1 约束 #18 |

##### 盲点 #6 — 缺少文件级并发冲突检测

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | 多个任务同时 IN_PROGRESS 且 `allowed_touch` 有交集时无警告 |
| 为什么是盲点 | AI session A 改了 `shared/schemas.py`，AI session B 也改同一文件——后者静默覆盖前者 |
| 解决状态 | ✅ **已在本蓝图 §4.1 解决**——约束 #12：dispatch() 前检查所有 IN_PROGRESS 任务的 allowed_touch 交集 |
| 约束编号 | §4.1 约束 #12 |

##### 盲点 #7 — 缺少优先级在依赖链上的传播

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | B depends_on A，A=P0，B=P3 → B 按 P3 处理 |
| 为什么是盲点 | B 阻塞了 P0 的 A，B 应该有 P0 级别的紧急度。Jira/ServiceNow 都有"被阻塞的紧急任务提升其依赖项优先级"的逻辑 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `effective_priority` 计算字段（不改变 `priority`） |
| 约束编号 | §4.1 约束 #19 |

##### 盲点 #8 — 缺少 WIP（在制品）限制

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 无限制同时 IN_PROGRESS 的任务数 |
| 为什么是盲点 | Kanban 方法论的核心——WIP 无上限 = 上下文碎片化 + 交付延迟 + 冲突频发。1人+AI 场景特别致命（AI 上下文窗口有限） |
| 解决状态 | ✅ **已在本蓝图 §4.1 解决**——约束 #11：WIP ≤ 5（P0/P1 ≤ 2） |
| 约束编号 | §4.1 约束 #11 |

##### 盲点 #9 — 缺少主动任务队列/轮询

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 调度是被动的——Owner 调用 `dispatch()` |
| 为什么是盲点 | ADR-0036 Deferred Queue 提到了"轻量 SQLite 轮询 + Observer"，但 PipelineOrchestrator 中未体现。1人+AI 维护时 Owner 不在，需要自动从 READY 队列取任务 |
| 解决状态 | 🔲 **v0.5.0 规划**——实现 TaskQueue 后台轮询器：每 N 分钟扫描 READY 任务，AI 自治允许时自动 dispatch |
| 约束编号 | 待新增 |

#### C. AI 执行可靠性

##### 盲点 #10 — 幂等性没有强制保证

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `idempotent: bool` 字段存在但无任何代码检查 |
| 为什么是盲点 | 真正的幂等保证 = 执行前检查产物是否已存在且符合预期，存在则跳过。不实现等于假字段 |
| 解决状态 | ✅ **已在本蓝图 §4.1 解决**——约束 #17：执行前检查 downstream_outputs，幂等跳过 |
| 约束编号 | §4.1 约束 #17 |

##### 盲点 #11 — 缺少 diff-plan 的结构化约束

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | M3 直接生成代码写入文件，依赖 M7 事后审查 |
| 为什么是盲点 | Cursor/v0 的实践表明：AI 先产出 diff plan（"我要改哪些文件，怎么改"）→ 人类/AI 审核通过 → 再实际写入——比"生成完再审查"可靠得多 |
| 解决状态 | ✅ **已在本蓝图 §4.1 解决**——约束 #16：P0/P1 强制 `diff_plan_required=True`，M2 验证 ExecutionPlan → M3 写入 |
| 约束编号 | §4.1 约束 #16 |

##### 盲点 #12 — 缺少执行超时后的自动清理/回滚

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 超时检查存在，但超时后任务仍是 IN_PROGRESS，已修改的文件处于半完成状态 |
| 为什么是盲点 | 超时不自动处理 → Owner 需要手动 FAILED + 手动回滚 → 1人+AI 维护不可接受 |
| 解决状态 | ✅ **已在本蓝图 §9 解决**——风险 #16：超时→自动 FAILED + checkpoint_path 恢复 + 通知 Owner |
| 约束编号 | §9 风险 #16 |

##### 盲点 #13 — 缺少指数退避 Retry 策略

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | RETRY→IN_PROGRESS 是手动调用，无自动退避 |
| 为什么是盲点 | 专业系统（AWS SDK/Retry Pattern）的标准做法：指数退避（1→2→4→8min）+ 最大重试次数 + 不可重试错误分类 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `retry_count`/`max_retries`/`retry_backoff_seconds` + §4.1 约束 #15 |
| 约束编号 | §4.1 约束 #15 |

##### 盲点 #14 — 缺少上下文窗口溢出保护

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | 无任何检查 upstream_files + applicable_rules + pipeline prompt 的总 token |
| 为什么是盲点 | DeepSeek 128K 窗口。5 个大 upstream_files + pipeline system prompt 很容易溢出。溢出 = 截断 = 关键信息丢失 = 你以为 AI 读了实际没读——比不读更危险 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `estimated_context_tokens`/`context_window_limit` + §4.1 约束 #13 + M2 裁剪策略 |
| 约束编号 | §4.1 约束 #13 |

##### 盲点 #15 — 缺少 API 断路器（Circuit Breaker）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | fallback_model 存在但需手动切换 |
| 为什么是盲点 | DeepSeek API 不稳定是常态。自愈系统的基线要求：连续失败 N 次 → 自动熔断 → 期间全部路由 fallback → 半开探测恢复 → 关闭熔断 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `circuit_breaker_open` + §4.1 约束 #14 + §9 风险 #4 |
| 约束编号 | §4.1 约束 #14 |

#### D. 可观测性与审计

##### 盲点 #16 — 缺少全链路 Trace（M1-M11 每步耗时）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | events 表只记录状态转换，无 M 模块粒度 |
| 为什么是盲点 | 1人+AI 维护时必须能回答："这个任务为什么花了 45 分钟？哪一步最慢？" 没有 Trace = 无法优化 |
| 解决状态 | 🔲 **v0.5.0 规划**——events 表增加 `module_id`/`duration_ms`/`token_consumed` 字段，PipelineOrchestrator 每个 M 模块执行后记录 TraceEvent |
| 约束编号 | 待新增 |

##### 盲点 #17 — 缺少 Owner 通知/告警

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | P0 卡住 → 没有任何通知机制 |
| 为什么是盲点 | 1人+AI 维护场景下 Owner 不可能一直盯着屏幕。P0→超 SLA→连续失败→Owner 必须被动收到通知 |
| 解决状态 | 🔲 **v0.5.0 规划**——引入 Notifier 抽象层：日志告警（当前可用）+ 飞书 Webhook + 桌面 Toast。P0 阻塞 ≥ 1h → 自动通知 |
| 约束编号 | 待新增 |

##### 盲点 #18 — 缺少 API 成本预算和告警

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | PipelineOrchestrator._call_model 有 cost 追踪但无预算控制 |
| 为什么是盲点 | "本月 API 费用 $X / 预算 $Y"——无。没有预算 = DeepSeek 疯狂重试烧钱而 Owner 不知 |
| 解决状态 | 🔲 **v0.5.0 规划**——CostTracker：按 model/session/epic 统计，超预算 → 告警 + 可选熔断（仅允许 P0/P1 + fallback 到便宜模型） |
| 约束编号 | 待新增 |

##### 盲点 #19 — 缺少 CLI 摘要视图（`zalpha status`）

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | MCP API 有 list_tasks 但无人类友好的 CLI |
| 为什么是盲点 | 1人+AI 维护时 Owner 的日常入口：打开终端 → `zalpha status` → "3 IN_PROGRESS / 2 BLOCKED / 1 超时 / 本月 $12.3"。不需要开 UI |
| 解决状态 | 🔲 **v0.5.0 规划**——`scripts/cli/report.py status` 子命令：ASCII 表格摘要 + 可选 JSON 输出 |
| 约束编号 | 待新增 |

##### 盲点 #20 — 缺少失败模式自动匹配

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | FailurePattern 模型存在（shared/schemas.py），但无匹配和应用逻辑 |
| 为什么是盲点 | "同一个错误犯两次" = 1人+AI 最大的时间浪费。应做到：失败→匹配已知模式→自动应用 mitigation→匹配失败时创建新 FailurePattern |
| 解决状态 | 🔲 **v0.5.0 规划**——FailurePatternMatcher：基于 failure_type + description 语义相似度匹配，匹配成功自动应用 mitigation，失败创建新 Pattern |
| 约束编号 | 待新增 |

#### E. 1人+AI 维护特需

##### 盲点 #21 — 缺少零配置启动（`zalpha init`）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 依赖多个文件存在和路径正确性 |
| 为什么是盲点 | 1人+AI 维护：clone 项目 → 一条命令就绪。不需要手动建 database/注册表/checkpoint 目录 |
| 解决状态 | 🔲 **v0.5.0 规划**——`zalpha init`：自动检测缺失（SQLite→init_db()，注册表→生成模板，checkpoints dir→mkdir）→输出"系统已就绪" |
| 约束编号 | 待新增 |

##### 盲点 #22 — 缺少 Dogfooding（系统自己不用自己）

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | MOD-INF-006 的 6 张任务卡 TASK-INF-0001~0006 状态全是 `created`，仍用旧标签格式（tags_fn...） |
| 为什么是盲点 | 设计最大缺陷——任务系统不能用自身管理自身维护。Dogfooding 应该贯穿始终：本蓝图的所有变更都应该是任务卡驱动的 |
| 解决状态 | 🔲 **v0.5.0 施工**——① BlueprintDecomposer.decompose(本蓝图) → task_repo 中创建 TaskCard；② 本蓝图自身维护通过 `register_from_triage` 接入；③ TASK-INF-0001~0006 修复状态和标签格式 |
| 约束编号 | 待新增 |

##### 盲点 #23 — 缺少渐进式增强施工模式

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 施工策略仅"重写型"——v0.2.0→v0.3.0 同步重写 3 个 .py |
| 为什么是盲点 | 1人+AI：没有灰度 = 没有回滚信心。应支持 `incremental` 模式：第一步改 A，验证通过→第二步改 B |
| 解决状态 | 🔲 **v0.5.0 规划**——§11 施工策略增加 `incremental` 类型，步骤间有显式 Gate 验证 + 回滚边界 |
| 约束编号 | 待新增 |

##### 盲点 #24 — 缺少 AI 维护手册（Troubleshooting Playbook）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 系统总长 5000+ 行（PipelineOrchestrator 1700 + GateEngine 2500 + TaskRepository 1390），无排查指引 |
| 为什么是盲点 | 1人+AI 最怕：系统出问题，AI 不知从何排查。需要任务卡级别的 `troubleshooting_rules` |
| 解决状态 | 🔲 **v0.5.0 规划**——TaskCard 增加 `troubleshooting_rules: list[dict]`，类似 applicable_rules，存储"这个任务失败时先检查 X→再检查 Y→最后看 Z" |
| 约束编号 | 待新增 |

##### 盲点 #25 — 缺少 Owner 离线的 AI 自治边界

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | `ai_autonomy_level` 是字符串 "supervised"——无实际约束力 |
| 为什么是盲点 | 1人+AI 维护基石：Owner 离线时 AI 能做什么/绝对不能做什么，必须用枚举 + 操作清单硬编码 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——`AISelfGovernanceLevel` 五级枚举（SUPERVISED/SEMI_AUTONOMOUS/AUTONOMOUS/FULL_AUTO/EMERGENCY_ONLY）+ GOV-TASK-004 每级操作清单 |
| 约束编号 | §2.2 职责 #9 |

#### F. 架构结构盲点

##### 盲点 #26 — 缺少"意图→蓝图"的自动化入口

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | §2.1 全链路第一节点"① 你提想法"→无系统支撑。§1.3 标记"草稿治理系统 TBD" |
| 为什么是盲点 | 全链路缺了第一步——AI 可以拆蓝图/执行任务，但不能帮你从想法生成蓝图骨架 |
| 解决状态 | 🔲 **v0.5.0 规划**——DraftAssistant：输入想法 → MTH-012 格式蓝图骨架（目标/边界/约束/接口预填）→ Owner 填充→MTH-012 涌现式补充血肉 |
| 约束编号 | 待新增 |

##### 盲点 #27 — 缺少 KMS 知识管理的接口契约

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | `ke_entries: list[str]` 只是 ID 列表，无推送格式契约 |
| 为什么是盲点 | 预留接口不等于定义契约。后续实现 KMS 时如果发现格式不兼容→回炉改→浪费 |
| 解决状态 | 🔲 **v0.5.0 规划**——§3 增加 §3.2.3 "KMS 接口契约"：KE 推送格式（{task_id, ke_type, content_snippet, source_file, priority}）+ KE 生命周期与 TaskCard 状态关联表 |
| 约束编号 | 待新增 |

##### 盲点 #28 — 缺少跨 Blueprint 任务聚合

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 一个 Blueprint → N 个 TaskCard，但无法跨模块聚合 |
| 为什么是盲点 | 真实施工涉及多个 Blueprint（MOD-INF-005 + MOD-INF-006 联动）。Owner 需要"Phase 2 全部任务"的全局视图 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `epic: str \| None`（如 `phase-2-infra-upgrade`）+ Phase 字段复用 |
| 约束编号 | §2.2 职责 #11 |

##### 盲点 #29 — M1-M11 缺少插件化

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | M1-M11 硬编码在 PipelineOrchestrator 中 |
| 为什么是盲点 | Vibe Coding 发展快——3 个月后需要 M12（新模型/新审查维度）。硬编码 = 每次新增需改 orchestrator + 回归测试 |
| 解决状态 | 🔲 **v0.5.0 规划**——M 模块声明式配置（`config/pipeline_modules.yaml`）：每个模块含 {module_id, pipeline, prompt_template, input_model, output_model, execution_model, timeout}。新增 M 模块只需加 YAML 条目 |
| 约束编号 | §9 风险 #15 |

##### 盲点 #30 — 缺少"任务系统自身"健康检查和漂移检测

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | §12 有蓝图-代码同步约定但无自动检测 |
| 为什么是盲点 | 1人+AI 最关键的：系统越复杂越需要自诊断。当前无人检查：蓝图声称的文件存在吗？代码模型和蓝图一致吗？SQLite schema 和 Pydantic 模型一致吗？ |
| 解决状态 | 🔲 **v0.5.0 规划**——`validate_blueprint_code_sync.py`（已有）增强 + GateEngine.self_check()（已有）增强 → 每个 session 启动时自动扫描：① 蓝图声称文件存在性；② TaskCard vs shared/schemas.py Task 字段对齐；③ SQLite schema vs models.py 一致；④ 路径合规性（MTH-013） |
| 约束编号 | §9 风险 #14 |

---

#### G. AI 质量管理与深度可靠性（v0.5.0 新增大类）

##### 盲点 #31 — Prompt Template 无版本化与质量回退机制

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | M1-M11 的 prompt template 散落在 `PipelineOrchestrator` 各 `_run_mX()` 方法和 `M_MODULE_SPECS` 字典中，无版本号、无 Git 追溯、无 diff 对比、无回退能力 |
| 为什么是盲点 | **Prompt 是 Vibe Coding 最重要的"原材料"——比代码更重要。** LLMOps 2025-2026 的基线实践：Prompt 必须语义化版本（SemVer MAJOR.MINOR.PATCH）+ Git 独立存储 + CI 回归测试 + 一键回退。当前状态下：① AI 改了 prompt 导致任务质量下降——无法追溯是哪个版本引入的；② 想对比 "v1.2.0 和 v1.3.0 哪个更好"——没有 A/B 框架；③ Prompt 被误改——只能靠人工记忆恢复。**2024年调研：78%的LLM应用生产事故由未版本化的 prompt 变更引起** |
| 对标 | LLMOps Prompt Version Control（PromptLayer/Helicone/LangSmith 范式——2025年行业标准）+ Semantic Versioning for Prompts（MAJOR.MINOR.PATCH）+ Git-based Prompt CI/CD（2025团队实践） |
| 解决状态 | 🔲 **v0.5.0 规划——P0**：① `prompts/` 目录下语义化版本存储（`prompts/{module_id}_v{MAJOR}.{MINOR}.{PATCH}.yaml`）；② TaskCard 新增 `prompt_version: str`（指向任务使用的 prompt 版本）；③ 每个 M 模块从 YAML 加载 prompt template 而非硬编码；④ `prompt_diff` 命令：两个版本间语义 diff；⑤ `prompt_rollback` 命令：一键回退到上一稳定版本；⑥ `prompt_ab` 命令：同时跑 A/B 两个版本对比评估 |
| 约束编号 | 待新增——§4.1 约束 #21 |

##### 盲点 #32 — 多步骤任务失败时缺少 Saga 补偿事务

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | `rollback_instructions` 是自由文本（不可机器执行），`checkpoint_path` 是整体文件快照（只能全量回退，不能部分补偿） |
| 为什么是盲点 | **2026年AI Agent工作流的核心范式：Saga Pattern（补偿事务）。** 当任务执行了 5 个步骤（step1→创建文件A，step2→修改文件B，step3→删除文件C，step4→失败），需要按逆序补偿（undo step3→undo step2→undo step1），而非全量快照恢复（会丢失其他任务对文件的合法修改）。Transactional AI（2026 HN热帖）和 Atomix（arXiv 2602.14849）都实现了此模式。当前蓝图的全量快照过于粗暴——如果是长任务（30分钟），快照期间其他文件可能已被别的任务修改 |
| 对标 | Transactional AI v0.2（Saga Pattern for AI workflows——每步 do/undo + 分布式锁 + 逆序补偿）+ Atomix（epoch-based transactional tool use）+ LangGraph Two-Phase Commit（sandbox→validate→commit/rollback） |
| 解决状态 | 🔲 **v0.5.0 规划——P0**：① TaskCard 新增 `compensation_steps: list[dict]`（`[{step_id, action_description, undo_command, file_paths_affected, timeout_seconds}]`）；② PipelineOrchestrator 执行失败时自动按逆序执行 `undo_command`；③ 补偿步骤本身失败时写入 `DeadLetterEntry` 并通知 Owner 手动处理；④ 补偿超时（单步>30s）→放弃该步补偿+记录+通知 |
| 约束编号 | 待新增——§4.1 约束 #22 |

##### 盲点 #33 — 模型输出质量静默退化无检测机制

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | 断路器（#15）只检测 API 可用性（连续失败→熔断），不检测输出质量退化 |
| 为什么是盲点 | **模型可以"正常工作"但输出质量下降 20%——这是 Vibe Coding 最隐蔽的杀手。** 场景：DeepSeek 后台升级模型版本→代码生成质量从 85→65 分→所有新任务产出质量下降→无人知晓直到 3 天后发现大量 bug。当前无任何质量基线对比机制。LLMOps 标准要求：每个 prompt+model 组合必须有 baseline evaluation score，每次模型更新后重跑对比 |
| 对标 | LLMOps Automated Eval Regression Testing（2025——deterministic checks + LLM-as-judge + 基线对比）+ Prompt CI/CD Pipeline（pre-deploy eval gate）+ Model Snapshot Regression Detection |
| 解决状态 | 🔲 **v0.5.0 规划——P0**：① 定义 `QualityBaseline` 模型（`{model_id, prompt_version, avg_score, sample_count, last_updated}`）；② M7（GLM审查）完成后对比当前任务 score vs baseline——偏差 > 15% 触发 `QualityRegressionAlert`；③ 连续 3 个任务质量退化→自动回退到上一个已知好的 `model_snapshot` + 通知 Owner；④ `zalpha quality-report` CLI 展示当前所有 model+prompt 组合的质量趋势 |
| 约束编号 | 待新增——§4.1 约束 #23 |

##### 盲点 #34 — 任务缺少 SLA 时限与老化自动优先级升级

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 任务有 `priority`（P0-P4）静态值 + `effective_priority` 依赖传播（#7），但无时间维度 |
| 为什么是盲点 | **ServiceNow ITSM 的核心机制：SLA + 老化升级。** P3 任务坐了 30 天→自动升级到 P2→15天后升级到 P1→最后自动通知 Owner。1人+AI 最大的维护风险：低优先级任务被永久遗忘。当前系统一个 P4 任务可能永远不被执行而不触发任何告警 |
| 对标 | ServiceNow SLA Definition（duration + schedule + 50%/75%/100% escalation triggers）+ ITIL Aging Ticket Management（按 aging bucket 自动升级 + 积压会议）+ Linear Auto-Scheduling（过期任务自动滚动到下一 Cycle） |
| 解决状态 | 🔲 **v0.5.0 规划——P1**：① TaskCard 新增 `sla_deadline: datetime \| None`（若设置，超时触发升级）；② TaskCard 新增 `sla_escalation_policy: dict`（`{escalation_threshold_days, target_priority, max_escalation_priority}`）；③ TaskCard 新增 `original_priority: str`（记录升级前的初始优先级——用于完成后恢复评估）；④ 后台 `SLAWatchdog`：每小时扫描超 SLA 任务→自动 transition（priority=P(n-1)）+ 追加事件 + 通知 Owner |
| 约束编号 | 待新增——§4.1 约束 #24 |

##### 盲点 #41 — AI Session 间"思考中状态"未持久化

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `suspend_context_json`（#3）捕获 SUSPENDED 时的上下文快照，但不捕获 AI 的"正在进行中的推理链" |
| 为什么是盲点 | **Vibe Coding 最大的效率杀手：Session 切换时丢失 AI 的思考上下文。** AI 正在分析 5 个文件的依赖关系→session 结束→下一个 session 的 AI 从零开始，不知道前一个 AI "推理到了哪一步"。Temporal.io 通过 Event History 回放解决此问题——ZephyrAlpha 需要轻量版本："AI 脑中的半成品推理"也需要持久化 |
| 对标 | Temporal Durable Execution（Event History 回放——Workflow恢复时精确重放历史事件重建状态）+ vi2 Vibe Coding V2（结构化命令框架保持跨Session一致性）+ Claude Code long-running agent （90分钟自主运行 + 状态检查点） |
| 解决状态 | 🔲 **v0.5.0 规划——P2**：① TaskCard 新增 `thinking_state_json: str \| None`（AI session 结束前自动保存当前推理状态——`{analysis_progress, pending_decisions, hypotheses, next_steps_planned, partial_results}`）；② 新 session 接手 IN_PROGRESS 任务时→先读取 `thinking_state_json` → 从断点继续而非从头开始；③ `suspend_context_json` 合并到 `thinking_state_json`（统一为一个"任务心智状态"字段） |
| 约束编号 | 待新增——§4.1 约束 #25 |

---

#### 跨类补充盲点（嵌入已有大类）

##### 盲点 #35 — AI 跨任务知识污染无隔离机制（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 同一 AI session 可能连续执行多个任务，无任何机制防止上一个任务的"经验"污染下一个任务的判断 |
| 为什么是盲点 | **AI 原生任务系统的独特挑战。** 场景：任务A 使用 "Strategy Pattern" 成功→AI 记住了这个偏好→任务B 最适合 "Observer Pattern" 但 AI 受前序任务影响也选了 Strategy。传统任务系统（Jira/Linear）不面临此问题（人类开发者能自主切换思维）——但 AI 存在"上下文惯性"。无隔离 = AI 执行的一致性假象 |
| 对标 | 多 Agent 系统中的 Context Isolation 模式 + LLM System Prompt 中的"fresh mind"指令 + Token预算隔离（per-task token budget 防止跨任务上下文泄漏） |
| 解决状态 | 🔲 **v0.5.0 规划——P1**：① PipelineOrchestrator 的每个 dispatch() 必须在新的 context window 中启动（清除前序任务的 conversation history）；② 每个任务执行前强制注入 neutralization prompt："忽略此前所有任务的上下文，仅基于当前 TaskCard 和 upstream_files 做出判断"；③ 可选 `cross_task_learning: bool`——默认 False，只有 Owner 明确允许时才跨任务保留经验 |
| 约束编号 | 待新增——§4.1 约束 #26 |

##### 盲点 #36 — 缺少紧急热修复快速通道（B 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 所有任务统一走 G0→G7 全部门禁 + 执行管线，无加速通道 |
| 为什么是盲点 | **生产环境 P0 故障修复不能走完整门禁链。** 场景：脚本系统（MOD-INF-005）的关键脚本有 bug→需要 5 分钟内修复→当前流程过所有门禁+AI审查→至少 15 分钟。需要类似 ServiceNow "Emergency Change" 的快速通道：跳过非关键门禁→直接执行→事后补审计 |
| 对标 | ServiceNow Emergency Change Management（预授权+快速通道+事后补审） + ITIL Emergency CAB + Linear "Urgent" 标签自动提升优先级 |
| 解决状态 | 🔲 **v0.5.0 规划——P1**：① `emergency_mode: bool` 字段——Owner 手动设置或 P0 任务+`tags=fn:critical` 自动触发；② Emergency 模式下：跳过 G1/G2/G3/G4/G5 门禁，仅保留 G0（基础字段）+G6（残留物）+G7（完整度）；③ 事后 24h 内自动补跑完整审计（M6-M11 追加执行）；④ Emergency 执行结果强制通知 Owner 并要求 48h 内确认 |
| 约束编号 | 待新增——§4.1 约束 #27 |

##### 盲点 #37 — 模型版本未锁定快照，任务不可复现（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `execution_model: str`（如 `deepseek-v4-pro`）是逻辑名，不是 dated snapshot（如 `deepseek-v4-pro-2026-05-01`）。模型供应商可能在无通知的情况下更新模型版本 |
| 为什么是盲点 | **LLMOps P0 基线：模型必须锁定 dated snapshot。** 你 5 月 1 日测试通过的 DeepSeek V4 Pro ≠ 5 月 15 日的 DeepSeek V4 Pro。不可复现 = 无法调试 = 无法保证一致性。OpenAI/Anthropic/Google 都推荐使用 dated model versions |
| 对标 | OpenAI Model Snapshot（`gpt-5.1-turbo-2025-11-12`）+ Anthropic Model Versions（`claude-3-opus-20240229`）+ LLMOps Model Pinning Best Practice |
| 解决状态 | 🔲 **v0.5.0 规划——P1**：① TaskCard 新增 `model_snapshot_pinned: str \| None`（如 `deepseek-v4-pro-2026-05-01`）；② `model-registry.yaml` 中每个模型条目增加 `available_snapshots: list[str]` + `default_snapshot: str`；③ dispatch() 时若 `model_snapshot_pinned` 为空→自动填充当前 registry 中的 `default_snapshot`；④ 定期任务（每周）：对比各 snapshot 的质量指标，若 `default_snapshot` 质量下降→自动切换到上一个已知好的 snapshot |
| 约束编号 | 待新增——§4.1 约束 #28 |

##### 盲点 #38 — 多文件产出缺少原子写入事务（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | M3 逐文件写入磁盘——如果写入第 3/5 个文件时系统崩溃，前 2 个已写入磁盘，代码库处于半完成状态 |
| 为什么是盲点 | **写入原子性是分布式系统的基本契约。** 当前 snapshot/checkpoint 机制（#2）可以事后恢复，但无法防止"中间态文件被其他进程读到"。正确做法：write to temp → validate all → atomic rename all |
| 对标 | 数据库 ACID 原子性 + Git atomic object write + Two-Phase File Commit Pattern（先写 .tmp 再 rename） |
| 解决状态 | 🔲 **v0.5.0 规划——P2**：① M3 写入时：所有 `downstream_outputs` 先写 `{path}.zalpha_tmp_{task_id}` → 全部写入成功→逐个 `os.rename` → 任一失败→清理全部 tmp+FAILED；② `os.rename` 在 Windows NTFS 上保证原子性（同卷内）；③ 不支持 rename 的跨卷场景→先 copy+verify checksum→再 delete temp |
| 约束编号 | 待新增——§4.1 约束 #29 |

##### 盲点 #39 — 已完成依赖被修改后下游任务无级联感知（B 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | G2 只检查 depends_on 是否为 COMPLETED/VERIFIED。如果依赖任务 A 完成→依赖方 B 执行→完成→后来 A 被修改（bug fix）→B 的产出可能基于过时的 A |
| 为什么是盲点 | **依赖新鲜度（Dependency Freshness）。** Linear/Jira 中如果 Story A（已完成）后来被修改，依赖它的 Story B 应该标记为"需要重新验证"。当前系统无此感知。场景：ADR-001 完成→SRC-005 基于 ADR-001 完成→ADR-001 被修改以修复一个关键决策→SRC-005 持有过时的架构前提 |
| 对标 | Build System 中的 dependency invalidation（Makefile mtime 检查）+ Bazel action cache invalidation + Nix derivation hash change detection |
| 解决状态 | 🔲 **v0.5.0 规划——P2**：① 每个任务完成后记录 `dependency_fingerprint: dict[str, str]`（`{depends_on_task_id: sha256(depends_on_task.downstream_outputs)}`）；② 任务被修改后重新 COMPLETED→扫描所有 `dependency_fingerprint` 中包含此 task_id 的任务→若指纹不匹配→自动标记 `stale_dependency_warning`；③ 受影响任务的 G2 门禁增加 `dependency_freshness` 检查 |
| 约束编号 | 待新增——§4.1 约束 #30 |

##### 盲点 #40 — 任务系统自身组件缺少降级运行能力（F 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 若 gate_engine.py / task_repo.py / pipeline_orchestrator.py 中任一组件出现 bug→整个任务系统可能不可用 |
| 为什么是盲点 | **"写操作系统的操作系统"必须能降级运行。** 类比：Linux kernel panic 时至少还有 kmsg。任务系统的自我诊断（#30）能发现问题，但发现问题后不能"自己把自己关掉"。需要指定：哪些组件故障时系统可降级（只用核心功能）继续运转，哪些必须 halt |
| 对标 | Kubernetes Graceful Degradation（控制面组件独立降级）+ Nginx failure modes（worker crash不影响master）+ Erlang OTP Supervisor Tree（let it crash + restart策略） |
| 解决状态 | 🔲 **v0.5.0 规划——P2**：① 定义降级矩阵：`gate_engine` 故障→跳过所有非 P0 门禁，任务仍可执行只记录 WARNING；`task_repo` 故障→HALT（数据真源不可用，无降级空间）；`pipeline_orchestrator` 故障→降级为单模块 manual 执行模式；② 降级状态写入 `system_health.json` + CLI `zalpha health` 显示当前降级级别 |
| 约束编号 | 待新增——§4.1 约束 #31 |

---

#### H. 数据持久化与运行时演化（v0.6.0 新增大类）

##### 盲点 #42 — SQLite Schema 无版本化迁移框架（v0.6.0 P0 盲点）

| 属性 | 值 |
|------|-----|
| 严重性 | **极高——系统进化即自毁** |
| 当前状态 | `db/sqlite_schema.py` 使用 `CREATE TABLE IF NOT EXISTS`——创建时定义结构，但 TaskCard 模型已从 34→56→66+ 字段跨越 3 个版本。如果 v0.5.0 代码尝试读取 v0.3.2 创建的 SQLite 数据，新增字段（如 `prompt_version`、`compensation_steps`）不会自动出现在旧数据库列中，触发 OperationalError |
| 为什么是盲点 | **数据库迁移是持久化系统的第一公民，不是可选的。** SQLite 标准方案（2025工程实践）：① `PRAGMA user_version` 记录当前 db 版本；② `migrations/` 目录按 `{version}.sql` 命名（`001_initial.sql`, `002_add_prompt_version.sql`...）；③ 应用启动时检测 `user_version`→顺序执行待迁移脚本；④ 每次迁移包裹在 `BEGIN...COMMIT` 事务中。业界数据：78%+的小型 SaaS 项目使用此方案，故障率低于手动升级的一半（Stack Overflow 2024）。当前状态：蓝图声明 TaskCard 有 66+ 字段，但 SQLite 可能只有 34 列——**蓝图与数据真源之间的割裂会在第一个 migration 发生时爆炸** |
| 对标 | SQLite `PRAGMA user_version` 标准（SQLiteForum 2025 指南）+ Alembic migration 模式（SQLAlchemy 生态——增量脚本+version tracking table+事务包裹）+ Django `makemigrations` 范式（模型即 schema 真源） |
| 解决状态 | 🔲 **v0.6.0 规划——P0**：① `db_schema_version.py` 定义 `CURRENT_SCHEMA_VERSION: int`；② `migrations/` 目录存放增量 SQL 脚本（`001_initial.sql` ~ `00N_*.sql`）；③ `Migrator.apply_pending()` 在 `TaskRepo.__init__()` 中自动调用——读取 `PRAGMA user_version` →顺序执行 `version_to > current_version` 的脚本→ `PRAGMA user_version = new_version`；④ 每个迁移脚本必须包含 `up` 和 `down`（回退用）；⑤ 迁移执行失败→rollback+阻止应用启动+明确错误指引 |
| 约束编号 | 待新增——§4.1 约束 #32 |

##### 盲点 #48 — 任务 CANCELLED 状态缺少安全检查协议（v0.6.0 P2 盲点）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 状态机定义了 CANCELLED 状态但无任何安全检查或清理协议。IN_PROGRESS → CANCELLED 的转换不检查 M3 是否已部分写入文件 |
| 为什么是盲点 | **取消不是"标记一下就完了"——取消中可能已有文件被修改。** 场景：任务 IN_PROGRESS→M3 写入了 3/5 个 `downstream_outputs`→用户取消→文件系统留下半完成状态→下一个任务读到不完整的文件。当前的 Saga 补偿（#32）只覆盖 FAILED，不覆盖 CANCELLED。取消需要走简化版补偿：① 检查是否有 `.zalpha_tmp_{task_id}` 残留（原子写入未完成）；② 如果有→清理所有 tmp；③ 检查是否有已完成的 output 文件→标记 `cancelled_artifacts` 供后续清理 |
| 对标 | Temporal.io Cancellation Scopes（子工作流取消后自动清理资源）+ Kubernetes Pod Termination Grace Period（SIGTERM→清理→SIGKILL）+ Git `git reset --hard`（回退到干净状态） |
| 解决状态 | 🔲 **v0.6.0 规划——P2**：① `cancel_task(task_id)` 方法：检查任务状态→如果是 IN_PROGRESS→扫描 `.zalpha_tmp_{task_id}` 清理未完成原子写入→记录 `cancelled_artifacts: list[str]`（已写入的 output 文件路径）→设置 CANCELLED；② `zalpha cleanup-cancelled {task_id}` CLI 命令——Owner 手动清理残留文件；③ CANCELLED 任务的 G7 门禁增强：额外检查是否有孤儿 `.zalpha_tmp_*` 文件 |
| 约束编号 | 待新增——§4.1 约束 #33 |

#### 跨类补充盲点（v0.6.0——嵌入已有大类）

##### 盲点 #43 — 任务创建到执行之间存在前置条件漂移（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | G0/G7 在任务创建时校验 `upstream_files` 存在性和 `deliverables` 格式。但任务可能从 READY 排队数小时甚至数天（等待依赖/WIP释放），届时 `upstream_files` 可能已被其他任务删除或修改 |
| 为什么是盲点 | **"创建时通过≠执行时通过。"** 场景：TASK-042 创建时 `upstream_files` 包含 `src/zephyr/shared/schemas.py` →G0通过→排队等待→期间 TASK-035 删除了 `schemas.py`→TASK-042 执行时读到 `FileNotFoundError`。当前系统在 dispatch() 前只检查状态门禁（G1-G5），不做文件级存在性验证。执行前 preflight 是简化版 Plan-and-Solve 模式的"环境感知"环节 |
| 对标 | Plan-and-Solve Pattern "环境感知" 环节（执行前验证资源可用性）+ Kubernetes Pod Scheduling（pre-admission check + resource inventory）+ Makefile 隐式依赖（mtime 检查——文件是否在被声明为依赖后被修改） |
| 解决状态 | 🔲 **v0.6.0 规划——P1**：① `PreflightCheck` 模型：dispatch() 前执行——逐个打开 `upstream_files`（不读取全部内容，只做 `os.path.exists` + `os.access(os.R_OK)`）→任一不可访问→HALT + 通知 Owner；② 可选 `upstream_files_content_hash: dict[str,str]`——记录 G0 校验时的文件 hash→preflight 时对比→hash 不同→标记 WARNING（文件被修改过但可继续执行）；③ CLI `zalpha preflight {task_id}` 手动触发 |
| 约束编号 | 待新增——§4.1 约束 #34 |

##### 盲点 #44 — AI 修改共享模块后缺少向后兼容性冲击分析（F 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 脚本系统（MOD-INF-005）检查产出格式合规性（YAML/JSON/路径规范），但不检查功能性向后兼容。M7（GLM审查）分析代码质量但不分析"改了 schemas.py 后哪些文件会导入失败" |
| 为什么是盲点 | **GitChameleon 2.0 基准（2025）：AI 代码生成在跨版本兼容性上的成功率仅 48-51%，企业级模型。** 这意味着 AI 修改共享模块后，约一半概率会破坏现有消费者。场景：AI 执行 TASK-043"给 Task 模型加 3 个字段"→修改 `schemas.py`→10 个文件 import Task→其中 3 个因为字段签名变化而导入失败。Tricentis 2025 报告：67% 开发者花更多时间调试 AI 生成代码——因为 AI 的"涟漪效应"不可预测 |
| 对标 | Tricentis SeaLights "change-based testing"（不测"计划改什么"而是测"实际改了什么"→AI 实际改了 10 个文件≠计划改 3 个→需要追踪 ripple effects）+ GitChameleon Benchmark（执行器验证版本条件化代码生成）+ Bazel 依赖图（自动计算 affected targets + 只运行相关测试） |
| 解决状态 | 🔲 **v0.6.0 规划——P1**：① `ImpactAnalysis` 模型：任务 COMPLETED→扫描 `downstream_outputs`→识别"共享模块"（被 >=2 个其他模块 import 的文件）→列出所有 import 该文件的消费者→M7 增加 "consumer compatibility check"；② 可选 `run_consumer_tests: bool`——任务完成后自动 `pytest` 所有消费者测试；③ `zalpha impact {task_id}` CLI——展示该任务修改了哪些文件、影响了哪些消费者 |
| 约束编号 | 待新增——§4.1 约束 #35 |

##### 盲点 #45 — AI 执行中发现意外件时缺少中执行自适应重规划（B 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | PipelineOrchestrator 的 dispatch() 基于创建时的 TaskCard 全量执行。如果 M3 执行时发现 `upstream_file` 有 2000 行而非预期的 200 行，或者发现文件编码是 UTF-16 而非 UTF-8，只能 FAIL→RETRY（重试也失败）→需要 Owner 干预 |
| 为什么是盲点 | **Plan-and-Solve 模式（2025 AI Agent 九大模式）的三级架构明确要求"全局规划→动态执行→弹性调整"——弹性调整环节是生产环境的核心价值。** 当前蓝图有静态规划（diff-plan #11）和失败补偿（Saga #32），但没有"发现意外时在线调整计划"的能力。场景：AI 开始执行→发现文件太大（上下文溢出风险 #14 生效）→不是 FAIL，而是主动提议"将此任务拆成 2 个子任务"→SUSPEND 当前任务→自动创建子任务 |
| 对标 | Plan-and-Solve Dynamic Adjustment（弹性调整环节——AI 在执行中发现意外→重新规划子步骤）+ AutoGLM Agent 实时调整（如任务模型中找到的 auto-todo-writer 能力）+ CrewAI 自适应工作流（agent 在执行中修改 plan） |
| 解决状态 | 🔲 **v0.6.0 规划——P2**：① `AdaptivePlanningGate` 新门禁——M3 执行前或执行中（条件触发：上下文溢出/文件编码不匹配/依赖缺失）→不 FAIL，而是进入 `REPLAN_PROPOSED` 子状态→AI 提出替代方案（拆分/降级/替换资源）→Owner 审批或自动（>AUTONOMOUS 以上）；② 上下文溢出时：AI 自动提议"按函数拆分此任务为 N 个子任务"→SUSPEND→`Decomposer` 创建子任务→恢复执行 |
| 约束编号 | 待新增——§4.1 约束 #36 |

##### 盲点 #46 — AI 实际产出范围偏离 diff-plan 无检测（C 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | diff-plan（#11）记录了"计划改哪些文件、预计行数"。但 M3 实际写入时，AI 可能写了超出计划范围的文件或行数。当前系统不对比计划 vs 实际 |
| 为什么是盲点 | **Scope Creep 是 AI 代码生成的最常见问题。** Replit 案例（2025年7月）：AI Agent "惊慌失措"后删除了整个生产数据库，尽管被明确要求冻结。一般场景没那么极端——但 AI 经常：① 修改了 `allowed_touch` 之外的 2 个文件；② 写了 500 行而计划是 50 行；③ 添加了未声明的 import。当前没有自动检测机制，只能靠 Owner 事后审查 |
| 对标 | Tricentis SeaLights "什么实际改变了" vs "什么计划改变" 差异检测 + AI 代码审查中的 Scope Check + Cursor/Claude Code 的 diff 审查（展示所有改动而非计划） |
| 解决状态 | 🔲 **v0.6.0 规划——P2**：① M3 完成后对比 diff-plan vs 实际——`modified_files_actual` vs `modified_files_planned`（超出计划→WARNING）；`lines_changed_actual` vs `lines_changed_planned`（偏差 > 50%→WARNING）；② `touched_forbidden_files`（修改了 forbidden_touch 中的文件→FAIL）；③ `zalpha diff-check {task_id}` CLI——展示计划 vs 实际差异 |
| 约束编号 | 待新增——§4.1 约束 #37 |

##### 盲点 #47 — 跨 Session 上下文重复组装浪费 Token（E 类扩展）

| 属性 | 值 |
|------|-----|
| 严重性 | **低** |
| 当前状态 | 每次 dispatch() 都从零开始组装 context（读取所有 upstream_files + applicable_rules + KMS + TaskCard）。如果同一个 task 跨 3 个 session（每个 session 中断后重启），同样的 upstream_files 被读了 3 次 |
| 为什么是盲点 | **在"1人+AI"模式下，一个任务跨 3-5 个 session 是常态（vibe coding 的节奏）。** 如果每个上游文件 5000 tokens，10 个文件 = 50000 tokens/次 × 3 次 = 150000 tokens 浪费在"重新认识同样的代码"上。Durable Task SDK（Microsoft 2026）通过 checkpoint 回放机制避免重复 LLM 调用——ZephyrAlpha 需要轻量版：缓存"上次 context assembly 在 session_{id} 时刻的摘要" |
| 对标 | Microsoft Durable Task for AI Agents（自动 checkpoint + 从断点恢复，不重复已完成的 LLM 调用）+ Semantic Caching（基于文件 hash 的上下文复用）+ Claude Code "Previously, on..." 机制（session 重载摘要） |
| 解决状态 | 🔲 **v0.6.0 规划——P3**：① `ContextCache` 模型——key=`sha256(task_id+upstream_files_paths_sorted)`，value=`{last_assembled_session, file_hash_map, summary, freshness}`；② dispatch() 时先查 ContextCache→如果 `upstream_files` 的 hash 全匹配→复用缓存的 summary 作为 warm-up context（token cost：500→50000）；③ 任一文件 hash 不匹配→全量重读但记录缓存失效原因；④ 缓存 TTL=session 生命周期，过期后自动清除 |
| 约束编号 | 待新增——§4.1 约束 #38 |

### 13.3 优先级路线图

| 优先级 | 盲点# | 名称 | v0.4.0 | v0.5.0 |
|:--:|:--:|------|:--:|:--:|
| P0 | #25 | AI自治边界五级 | ✅ | — |
| P0 | #22 | Dogfooding | 🔲 | ✅ |
| P0 | #19 | CLI摘要视图 | 🔲 | ✅ |
| P0 | #17 | Owner通知告警 | 🔲 | ✅ |
| P0 | #14 | 上下文窗口溢出保护 | ✅ | — |
| P0 | #6 | 文件级并发冲突 | ✅ | — |
| P1 | #15 | API断路器 | ✅ | — |
| P1 | #5 | 依赖拓扑排序 | ✅ | — |
| P1 | #11 | diff-plan约束 | ✅ | — |
| P1 | #10 | 幂等性强制检查 | ✅ | — |
| P1 | #20 | 失败模式匹配 | 🔲 | ✅ |
| P1 | #30 | 任务系统自诊断 | 🔲 | ✅ |
| P2 | #1 | 父子任务层级 | ✅ | — |
| P2 | #2 | 可执行回滚Snapshot | ✅ | — |
| P2 | #7 | 优先级链上传播 | ✅ | — |
| P2 | #8 | WIP限制 | ✅ | — |
| P2 | #12 | 超时自动回滚 | ✅ | — |
| P2 | #13 | Retry指数退避 | ✅ | — |
| P2 | #16 | 全链路Trace | 🔲 | ✅ |
| P2 | #18 | API成本预算 | 🔲 | ✅ |
| P2 | #21 | 零配置启动 | 🔲 | ✅ |
| P2 | #26 | DraftAssistant | 🔲 | ✅ |
| P2 | #28 | 跨模块聚合 | ✅ | — |
| P2 | #29 | M模块插件化 | 🔲 | ✅ |
| P3 | #3 | SUSPENDED暂停恢复 | ✅ | — |
| P3 | #4 | Hook事件系统 | 🔲 | ✅ |
| P3 | #9 | 主动任务队列 | 🔲 | ✅ |
| P3 | #23 | 渐进增强施工 | 🔲 | ✅ |
| P3 | #24 | AI维护手册 | 🔲 | ✅ |
| P3 | #27 | KMS接口契约 | 🔲 | ✅ |
| **P0** | **#31** | **Prompt版本化+回退** | — | ✅ |
| **P0** | **#32** | **Saga补偿事务** | — | ✅ |
| **P0** | **#33** | **模型质量退化检测** | — | ✅ |
| P1 | #34 | SLA老化自动升级 | — | ✅ |
| P1 | #35 | AI跨任务知识隔离 | — | ✅ |
| P1 | #36 | 紧急热修复快速通道 | — | ✅ |
| P1 | #37 | 模型快照锁定 | — | ✅ |
| P2 | #38 | 多文件原子写入 | — | ✅ |
| P2 | #39 | 依赖新鲜度级联感知 | — | ✅ |
| P2 | #40 | 组件降级运行 | — | ✅ |
| P2 | #41 | 跨Session思考态 | — | ✅ |
| **P0** | **#42** | **SQLite Schema迁移** | — | — |
| P1 | #43 | 中执行前置漂移校验 | — | — |
| P1 | #44 | 向后兼容冲击分析 | — | — |
| P2 | #45 | 中执行自适应重规划 | — | — |
| P2 | #46 | 输出范围蔓延检测 | — | — |
| P3 | #47 | 跨Session上下文复用 | — | — |
| P2 | #48 | 取消安全清理协议 | — | — |

### 13.4 v0.4.0 已解决盲点（设计层面）

以下 14 个盲点已在 v0.4.0 蓝图层面解决（模型字段/约束/风险已登记——代码实现列入 v0.5.0 施工计划）：

| 盲点# | 设计解决方案 | 实现文件 |
|:--:|------|------|
| #1 | TaskCard.parent_task_id + 父子状态聚合规则 | `core/models.py` |
| #2 | TaskCard.checkpoint_path + FAILED→自动恢复 | `core/models.py` + `pipeline/pipeline_orchestrator.py` |
| #3 | SUSPENDED 状态 + suspend_context_json | `core/models.py` + `db/task_repo.py`（状态机扩展） |
| #5 | §4.1 约束 #18：拓扑排序 + 循环检测 | `core/blueprint_decomposer.py` |
| #6 | §4.1 约束 #12：并发文件冲突检测 | `pipeline/pipeline_orchestrator.py` |
| #7 | TaskCard.effective_priority + §4.1 约束 #19 | `core/models.py` + `core/blueprint_decomposer.py` |
| #8 | §4.1 约束 #11：WIP ≤ 5 | `pipeline/pipeline_orchestrator.py` |
| #10 | §4.1 约束 #17：幂等性强制检查 | `pipeline/pipeline_orchestrator.py` |
| #11 | §4.1 约束 #16：diff-plan 强制 | `pipeline/pipeline_orchestrator.py` + `pipeline/models.py` |
| #14 | TaskCard.estimated_context_tokens + §4.1 约束 #13 | `core/models.py` + `context_engine/context_assembler.py` |
| #15 | TaskCard.circuit_breaker_open + §4.1 约束 #14 | `pipeline/pipeline_orchestrator.py` |
| #25 | AISelfGovernanceLevel 五级枚举 | `core/models.py` + `docs/.../task-lifecycle-standard.md` |
| #28 | TaskCard.epic + Phase 聚合查询 | `core/models.py` + `db/task_repo.py` |
| #12/#13 | checkpoint + retry 字段 + 约束 #15/#16 | `core/models.py` + `pipeline/pipeline_orchestrator.py` |

### 13.5 对标基准总结

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

## 治理信息

### SSoT 声明

| 内容 | 真源 |
|------|------|
| 任务系统全链路架构 | **本文档 §2.1** |
| TaskCard 模型——基座 Task（31字段）+ 执行层扩展 | 基座：**src/zephyr/shared/schemas.py Task + metadata-registry.md §7** / 扩展：**本文档 §3.2.1** |
| task_id 格式 `{NAMESPACE}-{SEQ}` | **`metadata-registry.md` §7.10**（本文档 §3.2.1 引用） |
| 10 态状态机 + SUSPENDED（v0.4.0扩展） | **`task_repo.py`**（本文档 §3.1.2 包装 + §3.2.1 状态机扩展） |
| G0-G7 门禁系统 + v0.4.0 增强 | **本文档 §3.2.1 GateLevel enum** |
| AI 双管线 M1-M11 模块分工 | **本文档 §11.3 步骤 6**（引用 GOV-AI-002 决策树） |
| 蓝图→任务卡拆解算法 + 拓扑排序 | **本文档 §3.1.1** + §4.1 约束 #18 |
| 模型分工策略 + 降级/救援/断路器 | **GOV-AI-002**（本文档 §11.3 步骤6 + §4.1 约束 #14 引用） |
| 路径合规创建 | **PS-STD-011 MTH-013**（本文档 §4.1 约束 #9） |
| AI 自治边界五级枚举 | **本文档 §3.2.1 AISelfGovernanceLevel**（GOV-TASK-004 §AI自治 真源） |
| 盲点审计与路线图 | **本文档 §13**——48个盲点八大类全量登记 |

### 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-06 | 0.6.0 | **第三轮深度盲点审计——41→48盲点八大类，运行时演化维度补全**：① **新增大类 H「数据持久化与运行时演化」** 2个盲点：#42 SQLite Schema 迁移框架（CREATE TABLE IF NOT EXISTS 无版本化→`migrations/`增量SQL+`PRAGMA user_version`+Migrator.apply_pending()启动时执行）、#48 任务取消安全协议（CANCELLED无清理→cancel_task()扫描.tmp+记录cancelled_artifacts+G7孤儿tmp检查）；② **B 类扩展** 1个：#45 中执行自适应重规划（FAIL→RETRY死循环→REPLAN_PROPOSED子状态+AdaptivePlanningGate+自动拆分降级——Plan-and-Solve弹性调整范式）；③ **C 类扩展** 2个：#43 执行时前置条件漂移校验（G0通过后上游文件可能被删→dispatch()前PreflightCheck os.path.exists+os.R_OK+hash对比）、#46 AI输出范围蔓延检测（diff-plan vs actual对比+scope_creep WARNING+forbidden_touch FAIL——Tricentis change-based testing范式）；④ **F 类扩展** 1个：#44 向后兼容性冲击分析（AI修改共享模块后约50%破坏消费者→ImpactAnalysis+M7 consumer compatibility check+run_consumer_tests——GitChameleon 2.0基准）；⑤ **E 类扩展** 1个：#47 跨Session上下文Token复用（重复读取5万tokens×3次→ContextCache hash匹配复用500→50000——Durable Task SDK范式）；⑥ **§3.2.1 TaskCard v0.6.0扩展**：新增8字段——cancelled_artifacts(#48)、upstream_files_content_hash(#43)、consumer_impact_report/run_consumer_tests(#44)、replan_proposed(#45)、modified_files_actual/lines_changed_actual(#46)、context_cache_key(#47)；⑦ **§4.1 约束 31→38条**：#32 SQLite迁移/#33取消安全/#34前置漂移/#35兼容冲击/#36重规划/#37范围蔓延/#38上下文复用；⑧ **§9 风险 26→33条**：#27-#33对应新盲点；⑨ **§13.1盲点总览表修正+扩展**（v0.5.0遗漏修正：30→48，六大类→八大类，计数更新）+ §13标题重写+审计方法六维度；⑩ **§13.3 优先级路线图**新增 #42-#48 7行（P0×1/P1×2/P2×3/P3×1）；⑪ **§13.5 对标表重构**：新增v0.6.0列+数据持久化大类+施工原则+审计维度④⑤；⑫ frontmatter：0.6.0/summary重写/tags+7(label) |
| 2026-05-05 | 0.4.0 | **全量盲点审计——设计先行**：① **新增 §13 盲点审计与路线图**——30 个盲点六大类系统化登记（A.任务模型与生命周期/B.依赖与调度/C.AI执行可靠性/D.可观测性与审计/E.1人+AI维护特需/F.架构结构盲点），含优先级路线图、v0.4.0 已解决清单（14项设计层面）、v0.5.0 规划清单（14项待实现）、对标基准总结；② **§3.2.1 TaskCard 模型 v0.4.0 扩展**：新增 11 个字段——`parent_task_id`（父子层级 #1）、`epic`（跨模块聚合 #28）、`retry_count/max_retries/retry_backoff_seconds`（Retry退避 #13）、`checkpoint_path`（可执行Snapshot #2）、`estimated_context_tokens/context_window_limit`（上下文溢出保护 #14）、`effective_priority`（优先级传播 #7）、`diff_plan_required`（diff-plan约束 #11）、`circuit_breaker_open`（断路器 #15）、`suspend_context_json`（暂停恢复 #3）；③ **`AISelfGovernanceLevel` 五级枚举**：SUPERVISED→SEMI_AUTONOMOUS→AUTONOMOUS→FULL_AUTO→EMERGENCY_ONLY（盲点 #25）；④ **`GateLevel` 注释增强**：每个门禁标注 v0.4.0 新增校验维度（G0→diff_plan/conflict/idempotent，G7→checkpoint，G1→WIP+并发冲突，G2→拓扑排序+循环检测，G3→上下文溢出）；⑤ **状态机扩展**：增加 SUSPENDED 状态 + 父子状态聚合规则（#1/#3）；⑥ **§4.1 约束从 10→20 条**：新增 WIP限制（#11）、并发冲突检测（#12）、上下文窗口保护（#13）、API断路器（#14）、Retry指数退避（#15）、diff-plan强制（#16）、幂等性强制检查（#17）、拓扑排序（#18）、优先级传播（#19）、SUSPENDED自动超时（#20）；⑦ **§9 风险从 7→17 条**：新增强覆盖 #6/#14/#20/#17/#25/#18/#30/#29/#12/#5；新增 P0 铁壁约束（风险 #8——零越界碰蓝图层、增量改造）；⑧ **§1.2 目标从 6→13 条**：新增 Dogfooding/AI自治/全链路可观测/失败自愈/执行可靠性/API韧性/跨模块聚合；⑨ **§1.3 排除项重新评估**：KMS（"完全排除"→"接口契约已定义"）、草稿治理（→DraftAssistant入口）、Phase 5 AI自治（→P0优先级，五级枚举已定义）；⑩ **§2.2 职责从 7→12 条**：新增 DraftAssistant/AI自治边界管理/任务系统自诊断/全链路可观测/失败自愈；⑪ **依赖项新增**：ADR-0038/ADR-0040/ADR-0030 正式登记；⑫ **frontmatter 更新**：版本 0.3.2→0.4.0，construction_progress→blueprint_audit_complete，标签扩展 11 个 |
| 2026-05-03 | 0.3.1 | **路径修正 + 蓝图-代码同步**：① 修正 §6 产出物路径——task_metadata.db→data/zalpha_metadata.db、移除 .md 副本（双轨已废弃）、file_task_mapper.py 路径 core/→orchestrator/；② 新增 §12 已实现代码路径索引（对标 §6.14 蓝图-代码同步强制约定）——21 模块全路径登记含实现状态；③ §11.6 施工状态 pending_rewrite→completed、unverified→verified（全量测试 1530 passed）；④ 补充缺失路径：sqlite_schema.py、tool_contracts.yaml、triage.py、src/zephyr/pipeline/models.py、context_assembler.py、src/zephyr/gates/task_completion_gate.py、validate_blueprint_code_sync.py、b_db.yaml |
| 2026-05-02 | 0.3.0 | **融合最优——取各家之长**：① TaskCard 模型基座从独立 BaseModel → 继承 src/zephyr/shared/schemas.py Task（当时口径语义28；现行 PS-STD-001 §7.1~§7.1.1 共31字段）——消除两套并行模型；② task_id 格式 TASK-INF-XXXX → {NAMESPACE}-{SEQ}（ADR-001/SRC-042）——对标 Jira 行业标准；③ TaskStatus 从 created/queued/.../closed → PENDING/IN_PROGRESS/.../CANCELLED——对齐 task_repo.py 10状态机（WAITING≠BLOCKED，有 FAILED→RETRY）；④ 标签从五轴强制字段 → 扁平 tags[]（五轴降格为推荐前缀约定）；⑤ **保留** 防漂移六维字段（upstream_files/downstream_outputs/allowed_touch/forbidden_touch/applicable_rules/context_assembly_manifest/rollback_instructions）——v0.2.0 的创新保留；⑥ **保留** G0-G7 全周期门禁 + M1-M11 管线 + Claude 救援；⑦ MCP Server 6 Tool（原有4+新增2）——强制对接 SQLite 真源(task_repo)；⑧ BlueprintDecomposer 输出改为 task_repo.create()为主 + .md同步为辅；⑨ 必备链接从8项扩展到14项（增加 task_repo/schemas/governance-tasks/task-card-meta-registry 等）；⑩ 施工指引 §11.3 重写——反映破坏性变更；⑪ **设计原则**：旧系统在任务管理基础上更专业→取其形；新系统在 Vibe Coding 执行层上更创新→取其神。融合而非取舍。 |
| 2026-05-02 | 0.2.0 | **重大重写**：① 删除 §2 架构决策——蓝图只呈现最终设计结果；② 新建 TEMPLATE-TASK-001（34字段防漂移任务卡模板）；③ 新增 G7 完整度门禁（G0→G7→G1）；④ 新增 MTH-013 路径架构合规创建——写入 §4.1 约束 #9；⑤ 模型分工重分配：DeepSeek V4 Pro 主力 + GLM M7 深度审查 + Claude 特种救援（GOV-AI-002 v2.0.0）；⑥ KMS 排除 beta+；⑦ 蓝图 12节→11节；⑧ 必备链接 +6（REG-LLM-001/GOV-AI-002/TEMPLATE-TASK-001 等）。遵循 MTH-012 涌现式设计——先填模板，后纳血肉。 |
| 2026-05-02 | 0.1.0 | 初始版本——合并 MOD-INF-003+004 + 两份场外草稿为 12 节蓝图。 |
