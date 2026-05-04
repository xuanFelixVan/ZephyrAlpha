---
module_id: "MOD-INF-006"
title: "任务系统蓝图 — 全链路：草稿→蓝图真源→任务卡→双管线执行→脚本系统"
doc_type: blueprint
status: approved
version: "0.3.2"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
construction_progress: phase_1_complete
summary: "ZephyrAlpha 任务系统全链路蓝图 v0.3.0。覆盖从草稿→蓝图真源→任务卡拆解→AI双管线执行→脚本系统校验的完整工作流。v0.3.0 融合两套设计的各自最优部分：旧规则体系在任务管理基础（ID格式/状态机/SQLite存储）上更专业，新蓝图在 Vibe Coding 执行层（防漂移字段/G0-G7门禁/M1-M11管线/规则引用）上更创新。TaskCard 模型继承 shared/schemas.py Task（28字段基座）+ 24个扩展字段 = 52字段总线（全部存入 SQLite data/zalpha_metadata.db——单源存储零丢失）。task_id 格式 {NAMESPACE}-{SEQ}，标签改为扁平 tags[] 保留五轴推荐约定。v0.3.1：移除 .md 双轨→SQLite 单源存储，MCP 6 Tool→5 Tool（删除 sync_file_state），DB 路径迁移 docs/09_audit/state/ → data/。"
tags: [task-system, task-card, vibe-coding, dual-pipelines, script-system, state-machine, gates, ai-execution, infrastructure, emergent-design, path-compliance, anti-drift]
depends_on:
  - {target: PS-STD-001, at: "§7.10", why: "任务卡 task_id 格式 + 28字段定义——本蓝图 §3.2.1 的真源"}
  - {target: PS-STD-011, at: "MTH-012|MTH-013", why: "涌现式设计+路径合规创建——本蓝图编写方法论"}
  - {target: GOV-DOC-002, at: "§5.1.2", why: "路径映射——产出物物理存放"}
  - {target: MOD-INF-005, at: "全篇", why: "脚本系统——本蓝图管线产出的审计消费方"}
  - {target: GOV-TASK-004, at: "全篇", why: "任务生命周期治理——取消权限、优先级裁决"}
  - {target: GOV-TASK-005, at: "全篇", why: "任务关闭标准——三步法"}
  - {target: TEMPLATE-TASK-001, at: "全篇", why: "任务卡模板——所有任务卡 .md 格式标准"}
  - {target: REG-LLM-001, at: "全篇", why: "模型基准排名——execution_model 数据依据"}
  - {target: GOV-AI-002, at: "全篇", why: "模型路由策略——任务分配决策树"}
  - {target: "src/zephyr/shared/schemas.py", at: "Task类", why: "Task模型基座——本蓝图 TaskCard 继承其 28 字段"}
  - {target: "src/zephyr/db/task_repo.py", at: "全篇", why: "SQLite CRUD + 10状态机 + N:N task_files——本蓝图数据层真源"}
---

# 任务系统蓝图 + 施工指引

> module_id: MOD-INF-006 | version: 0.3.2 | status: approved | layer: cross_layer

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
| 1 | 元数据注册表 | PS-STD-001 | 2.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | §7 任务卡字段真源——task_id格式/28字段/状态机 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | 2.6.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\governance-methodology-standard.md` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 脚本系统蓝图 | MOD-INF-005 | 3.0.0+ | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\script-system\blueprint.md` | 审计消费方——管线产出→12维度审计 |
| 5 | 任务卡标准 | GOV-TASK-003 | 3.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\task\task-card-standard.md` | 操作指南——字段定义已迁入 metadata-registry.md §7 |
| 6 | 任务生命周期标准 | GOV-TASK-004 | 2.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\task\task-lifecycle-standard.md` | 取消权限、优先级裁决 |
| 7 | 任务关闭标准 | GOV-TASK-005 | 1.1.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\task\task-closure-standard.md` | 关闭三步法 |
| 8 | 任务卡模板 | TEMPLATE-TASK-001 | 1.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\task-card-template.md` | 所有任务卡 .md 的标准格式 |
| 9 | 模型基准排名 | REG-LLM-001 | 1.1.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\frontier-llm-benchmark-ranking.md` | execution_model 数据依据 |
| 10 | 模型路由策略 | GOV-AI-002 | 2.0.0+ | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\ai\model-routing-policy.md` | 任务分配决策树 |
| 11 | AGENTS.md 项目基准 | — | 4.6.1+ | `D:\ZephyrAlpha\AGENTS.md` | 项目全局规则 |
| 12 | Task 模型基座 | shared/schemas.py | 现有代码 | `D:\ZephyrAlpha\src\zephyr\shared\schemas.py` | Task 28字段 Pydantic V2 模型——TaskCard 继承此模型 |
| 13 | task_repo.py | — | 现有代码 | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | SQLite CRUD + 10状态机 + N:N task_files——数据层真源 |
| 14 | 任务卡元注册表 | task-card-meta-registry | V-13 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml` | 三套任务卡系统登记——迁移状态追踪 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-INF-003（旧蓝图层） | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-card-kms\blueprint.md` | 任务卡制度+KMS体系 | deprecated——已被本蓝图合并 |
| 2 | MOD-INF-004（旧双管线） | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vibe-coding-pipelines\blueprint.md` | 双管线流程+M模块 | deprecated——已被本蓝图合并 |
| 3 | Task 模型（shared/schemas.py） | `D:\ZephyrAlpha\src\zephyr\shared\schemas.py` | 28字段任务模型——task_id/状态机/CRUD | ✅ 可复用——本蓝图 TaskCard 继承此模型 |
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
| 2 | **全链路贯通**：草稿→蓝图→任务卡→双管线→脚本系统——每步有输入/输出/门禁 | 每个环节 Schema 完整 |
| 3 | **TaskCard 模型取最优**：基座继承 shared/schemas.py Task（28字段）+ 扩展六维防漂移字段 | 基座对齐 metadata-registry.md §7 真源——不留两套模型 |
| 4 | **task_id 格式统一为 `{NAMESPACE}-{SEQ}`** | ADR-001 / STD-005 / SRC-042——对标 Jira，自文档 |
| 5 | **路径合规创建**：MTH-013 原则——AI 不得自主决定目录层级 | 所有路径可追溯到索引 |
| 6 | **模型分工明确**：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种救援 | 分工有基准数据支撑 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | KMS 知识库的 KE 条目定义和抓取机制 | 属于独立的 KMS 系统升级——后续讨论，接口预留 |
| 2 | 模型注册表（model-registry.yaml）的完整建设 | 独立小任务——后续处理。任务卡模板中已预埋引用字段 |
| 3 | 草稿治理系统（草稿的讨论优化流程） | 独立系统——后续讨论。本蓝图关注草稿→蓝图之后的链路 |
| 4 | SQLite 数据库物理迁移 | 已有代码`task_repo.py`——蓝图只定义数据模型规范 |
| 5 | Phase 5 AI 自治模块 | 按照 MTH-005——预留字段不实现 |

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
| 7 | **KMS 知识管理**（beta+ 排除） | 接口预留——实现在后续版本独立讨论 |

### 2.3 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | SQLite CRUD + 10状态机 + N:N映射 | `task_repo.py`（`src/zephyr/db/`）— 已有生产级代码 |
| 2 | Task 模型基座（Pydantic V2 28字段） | `shared/schemas.py`（`src/zephyr/shared/`）— metadata-registry.md §7 真源 |
| 3 | MCP Server Web 层 | `task_manager_server.py`（`src/zephyr/mcp/`）— 本蓝图更新后重写 |
| 4 | 审计脚本 | MOD-INF-005 — 已有 9+ 脚本 |
| 5 | context_engine | `context_engine/` — 已有 7 模块 + experimental 补齐 |
| 6 | dashboard | `dashboard/` — 已有代码 |
| 7 | Phase 5 AI 自治 | 预留字段不实现 |

---

## 3. 接口契约

> ⚠️ 完整升级方案——6 个子节。强制 Pydantic V2 BaseModel（ADR-0040）。
>
> **模型层级**：`shared/schemas.py` Task（28字段，metadata-registry.md §7 真源）→ 本蓝图 TaskCard 继承 Task 并扩展 Vibe Coding 执行层字段。

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

> **基座**：继承 [shared/schemas.py](file:///D:/ZephyrAlpha/src/zephyr/shared/schemas.py) `Task`（28字段，真源 [metadata-registry.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/meta/metadata-registry.md) §7）
>
> **扩展**：本蓝图追加 6 维防漂移 + 门禁 + 管线等 Vibe Coding 执行层字段

```python
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional
from zephyr.shared.schemas import Task, TaskStatus, Priority, SafetyLevel, Classification, EvolutionPolicy

class GateLevel(str, Enum):
    """全生命周期门禁——G0-G7"""
    G0 = "G0"  # 创建门禁——字段完整性校验（21必填）
    G7 = "G7"  # 完整度门禁——上游文件存在+下游路径完整+回滚可执行
    G1 = "G1"  # 指派门禁——模型/管线/模块不冲突
    G2 = "G2"  # 前置门禁——depends_on 全部 COMPLETED/VERIFIED
    G3 = "G3"  # 执行门禁——context_assembly_manifest 全部可读
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

class TaskCard(Task):
    """
    Vibe Coding 任务模型——继承 shared/schemas.py Task（28字段）+ 追加执行层字段

    父类（Task，metadata-registry.md §7 真源）提供：
      task_id(namespace-seq), namespace, seq, title, status(10态), priority(P0-P3),
      phase, execution_model, model_rationale, fallback_model, safety_level,
      directive, idempotent, classification, evolution_policy, estimate_hours,
      actual_hours, files_in_scope, deliverables, acceptance, depends_on,
      tags(扁平[]), session_id, waiting_for, ready_at, completed_at, created_at, updated_at

    本类追加 Vibe Coding 执行层字段——防漂移六维 + 门禁 + 管线
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

    # ---- AI 自治（Phase 5 预留——MTH-005 只预留不实现）----
    ai_autonomy_level: str = Field(default="supervised")
    autonomy_checklist: list[str] = Field(default_factory=list)

    # ---- 施工/验证状态 ----
    construction_status: str = Field(default="pending")
    verification_status: str = Field(default="unverified")
```

> **字段源流对照表**：

| 来源 | 字段数 | 提供什么 |
|------|:---:|------|
| `shared/schemas.py` Task（基座） | 28 | task_id/namespace/status/priority/execution_model/files_in_scope/deliverables/tags/depends_on/...——基础任务管理 |
| 本蓝图 TaskCard 扩展 | +14 | 防漂移六维(upstream_files/downstream_outputs/allowed_touch/forbidden_touch/applicable_rules/context_assembly_manifest/rollback_instructions) + 门禁(gates) + 管线(pipeline) + 产物+审计+自治预留 |

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
| `update_status` | `transition()` | `{task_id, to_status, skip_gate?}` | `{task_id, old_status, new_status}` | `task_repo.update_status()` |
| `list_tasks` | — | `{status?, namespace?, tags?, limit?}` | `{tasks: [{task_id, title, status, execution_model}]}` | `task_repo.list_tasks()` |
| `register_from_triage` | — | `{raw_description, triage_context}` | `{task_id, draft_fields}` | `task_repo.create()` |
| `sync_file_state` | — | `{task_id}` | `{status, files_verified, drift_detected}` | `task_repo.get_task()` + 文件系统校验 |

**错误码**：`TASK_NOT_FOUND(404)` / `STATUS_MISMATCH(409)` / `ILLEGAL_TRANSITION(422)` / `GATE_BLOCKED(422)` / `VALIDATION_ERROR(400)` / `PATH_NOT_COMPLIANT(422)`

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

### 4.2 容量估算

| 维度 | 当前 | 峰值 | 极限 | 够用？ |
|------|:--:|:--:|:--:|:--:|
| 蓝图 | 6（含 retired） | 200+ | 无上限 | ✅ |
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
| PS-STD-001 | 必须 | §7 任务卡字段真源——task_id格式/28字段/状态机 | ≥2.0.0 |
| PS-STD-011 | 必须 | MTH-012 涌现式设计 + MTH-013 路径合规 | ≥2.6.0 |
| GOV-DOC-002 | 必须 | §5.1.2 路径映射 | — |
| GOV-TASK-003 | 必须 | 任务卡操作指南 | ≥3.0.0 |
| GOV-TASK-004 | 必须 | 取消权限、优先级裁决 | ≥2.0.0 |
| GOV-TASK-005 | 必须 | 关闭三步法 | ≥1.1.0 |
| MOD-INF-005 | 必须 | 脚本系统 12 维度 | ≥3.0.0 |
| TEMPLATE-TASK-001 | 必须 | 任务卡 .md 模板 | ≥1.0.0 |
| REG-LLM-001 | 必须 | 模型基准排名 | ≥1.1.0 |
| GOV-AI-002 | 必须 | 模型路由策略 | ≥2.0.0 |
| shared/schemas.py | 必须 | Task 28字段模型（TaskCard 基座）| 现有代码 |
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
| Task 模型基座（28字段）| `D:\ZephyrAlpha\src\zephyr\shared\schemas.py` | .py |
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

## 9. 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:--:|:--:|------|
| 1 | **任务卡 .md 与 SQLite 不同步** | 中 | 高 | transition() 前双轨一致性校验 |
| 2 | **蓝图 §11 不完整→拆卡遗漏** | 高 | 高 | MTH-012 涌现式设计——§11 必须极度详细；unassigned_items >10%→拒绝拆解 |
| 3 | **DeepSeek V4 Pro 幻觉**（幻觉率 94%） | 高 | 高 | GLM 审查纠错→Claude 关键兜底——三层防御 |
| 4 | **DeepSeek V4 Pro API 不可用** | 低 | 高 | fallback_model 明确降级——见 GOV-AI-002 §降级与容灾 |
| 5 | **路径漂移**——AI 自作主张建目录 | 中 | 高 | MTH-013 零自主创建权——强制索引查询 |
| 6 | **Change Folder 爆炸** | 低 | 低 | 任务卡状态 CANCELLED/VERIFIED 后 Change Folder 可归档/删除 |
| 7 | **TaskCard 基座切换破坏已有代码** | 高 | 高 | experimental 步骤3——同步重写 `core/models.py`/`blueprint_decomposer.py`/`task_manager_server.py`；不留两套模型 |

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
| 3 | shared/schemas.py Task 模型已理解——28字段+10状态机 | 能回答"Task.task_id 格式" |
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
| 5 | task_manager_server.py — MCP 5 Tool | `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py` |
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

## 治理信息

### SSoT 声明

| 内容 | 真源 |
|------|------|
| 任务系统全链路架构 | **本文档 §2.1** |
| TaskCard 模型——基座 Task（28字段）+ 执行层扩展 | 基座：**src/zephyr/shared/schemas.py Task + metadata-registry.md §7** / 扩展：**本文档 §3.2.1** |
| task_id 格式 `{NAMESPACE}-{SEQ}` | **`metadata-registry.md` §7.10**（本文档 §3.2.1 引用） |
| 10 态状态机 | **`task_repo.py`**（本文档 §3.1.2 包装） |
| G0-G7 门禁系统 | **本文档 §3.2.1 GateLevel enum** |
| AI 双管线 M1-M11 模块分工 | **本文档 §11.3 步骤 6**（引用 GOV-AI-002 决策树） |
| 蓝图→任务卡拆解算法 | **本文档 §3.1.1** |
| 模型分工策略 + 降级/救援 | **GOV-AI-002**（本文档 §11.3 步骤6 引用） |
| 路径合规创建 | **PS-STD-011 MTH-013**（本文档 §4.1 约束 #9） |

### 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-03 | 0.3.1 | **路径修正 + 蓝图-代码同步**：① 修正 §6 产出物路径——task_metadata.db→data/zalpha_metadata.db、移除 .md 副本（双轨已废弃）、file_task_mapper.py 路径 core/→orchestrator/；② 新增 §12 已实现代码路径索引（对标 §6.14 蓝图-代码同步强制约定）——21 模块全路径登记含实现状态；③ §11.6 施工状态 pending_rewrite→completed、unverified→verified（全量测试 1530 passed）；④ 补充缺失路径：sqlite_schema.py、tool_contracts.yaml、triage.py、src/zephyr/pipeline/models.py、context_assembler.py、src/zephyr/gates/task_completion_gate.py、validate_blueprint_code_sync.py、b_db.yaml |
| 2026-05-02 | 0.3.0 | **融合最优——取各家之长**：① TaskCard 模型基座从独立 BaseModel → 继承 src/zephyr/shared/schemas.py Task（28字段，metadata-registry.md §7 真源）——消除两套并行模型；② task_id 格式 TASK-INF-XXXX → {NAMESPACE}-{SEQ}（ADR-001/SRC-042）——对标 Jira 行业标准；③ TaskStatus 从 created/queued/.../closed → PENDING/IN_PROGRESS/.../CANCELLED——对齐 task_repo.py 10状态机（WAITING≠BLOCKED，有 FAILED→RETRY）；④ 标签从五轴强制字段 → 扁平 tags[]（五轴降格为推荐前缀约定）；⑤ **保留** 防漂移六维字段（upstream_files/downstream_outputs/allowed_touch/forbidden_touch/applicable_rules/context_assembly_manifest/rollback_instructions）——v0.2.0 的创新保留；⑥ **保留** G0-G7 全周期门禁 + M1-M11 管线 + Claude 救援；⑦ MCP Server 6 Tool（原有4+新增2）——强制对接 SQLite 真源(task_repo)；⑧ BlueprintDecomposer 输出改为 task_repo.create()为主 + .md同步为辅；⑨ 必备链接从8项扩展到14项（增加 task_repo/schemas/governance-tasks/task-card-meta-registry 等）；⑩ 施工指引 §11.3 重写——反映破坏性变更；⑪ **设计原则**：旧系统在任务管理基础上更专业→取其形；新系统在 Vibe Coding 执行层上更创新→取其神。融合而非取舍。 |
| 2026-05-02 | 0.2.0 | **重大重写**：① 删除 §2 架构决策——蓝图只呈现最终设计结果；② 新建 TEMPLATE-TASK-001（34字段防漂移任务卡模板）；③ 新增 G7 完整度门禁（G0→G7→G1）；④ 新增 MTH-013 路径架构合规创建——写入 §4.1 约束 #9；⑤ 模型分工重分配：DeepSeek V4 Pro 主力 + GLM M7 深度审查 + Claude 特种救援（GOV-AI-002 v2.0.0）；⑥ KMS 排除 beta+；⑦ 蓝图 12节→11节；⑧ 必备链接 +6（REG-LLM-001/GOV-AI-002/TEMPLATE-TASK-001 等）。遵循 MTH-012 涌现式设计——先填模板，后纳血肉。 |
| 2026-05-02 | 0.1.0 | 初始版本——合并 MOD-INF-003+004 + 两份场外草稿为 12 节蓝图。 |
