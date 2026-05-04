# 上下文影子副本 — G3 门禁审计证据

- 装配时间：2026-05-02T09:46:10.042373+00:00
- 文件数：2
- 总字符数：35313
- Token 估算：8828/12000
- 是否压缩：否
- SHA-256（前 12 位）：7f474464968c
- 错误数：0

---

## 文件清单

- [OK] `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md` — 测试蓝图文件 (est. 6574 tokens)
- [OK] `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\task-card-template.md` — 任务卡模板 (est. 2183 tokens)

---

## 完整上下文

```text
--- FILE: blueprint.md (测试蓝图文件) ---
PATH: D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md

---
module_id: "MOD-INF-006"
title: "任务系统蓝图 — 全链路：草稿→蓝图真源→任务卡→双管线执行→审计工厂"
doc_type: blueprint
status: approved
version: "0.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
summary: "ZephyrAlpha 任务系统全链路蓝图 v0.2.0。覆盖从草稿→蓝图真源→任务卡拆解→AI双管线执行→审计工厂校验的完整工作流。合并旧 MOD-INF-003（任务卡KMS）和 MOD-INF-004（双管线），并纳入两份场外讨论草稿的全部血肉。重大变更：① 取消架构决策章节——蓝图只呈现最终设计结果；② 新建任务卡防漂移模板（34字段，21必填）；③ 新增 G7 完整度门禁；④ 新增 MTH-013 路径架构合规创建原则；⑤ 模型分工重分配：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种救援；⑥ KMS 排除当前范围。"
tags: [task-system, task-card, vibe-coding, dual-pipelines, audit-factory, state-machine, gates, ai-execution, infrastructure, phase-0, emergent-design, path-compliance]
depends_on:
  - {target: PS-STD-001, at: "§5", why: "编号规则——任务卡编号格式"}
  - {target: PS-STD-011, at: "MTH-012|MTH-013", why: "涌现式设计+路径合规创建——本蓝图编写方法论"}
  - {target: GOV-DOC-002, at: "§5.1.2", why: "路径映射——产出物物理存放"}
  - {target: MOD-INF-005, at: "全篇", why: "审计工厂——本蓝图管线产出的审计消费方"}
  - {target: "TEMPLATE-TASK-001", at: "全篇", why: "任务卡模板——所有任务卡.m格式标准"}
  - {target: REG-LLM-001, at: "全篇", why: "模型基准排名——assigned_model 数据依据"}
  - {target: GOV-AI-002, at: "全篇", why: "模型路由策略——任务分配决策树"}
---

# 任务系统蓝图 + 施工指引

> module_id: MOD-INF-006 | version: 0.2.0 | status: approved | layer: cross_layer

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
| 1 | MOD-INF-003 任务卡KMS蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-card-kms\blueprint.md` | 覆盖型 | 本蓝图 | 已标记 deprecated→Phase 4 物理删除 |
| 2 | MOD-INF-004 双管线蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vibe-coding-pipelines\blueprint.md` | 覆盖型 | 本蓝图 | 已标记 deprecated→Phase 4 物理删除 |
| 3 | 场外草稿（双管线+任务卡知识库） | `D:\ZephyrAlpha\模块候选池\开发流程\氛围编程基础设施\vibe-coding-two-pipelines-design.md` / `vibe-coding-task-card-and-knowledge-base-design.md` | 迁入完毕 | 本蓝图 | 内容已全部通过 MTH-012 Step 3 纳入——完成历史使命→Owner 决定删除或归档 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 物理删除只能在 Phase 4 搬入阶段执行 | 给足缓冲期 |
| 3 | 物理删除必须人类确认 | AI 不得自行删除文件 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 2.0.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | 2.6.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\governance-methodology-standard.md` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 审计工厂蓝图 | MOD-INF-005 | 1.0.0 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\audit-factory\blueprint.md` | 审计消费方 |
| 5 | 任务卡模板 | TEMPLATE-TASK-001 | 1.0.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\task-card-template.md` | 所有任务卡的标准格式 |
| 6 | 模型基准排名 | REG-LLM-001 | 1.1.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\frontier-llm-benchmark-ranking.md` | assigned_model 数据依据 |
| 7 | 模型路由策略 | GOV-AI-002 | 2.0.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\ai\model-routing-policy.md` | 任务分配决策树 |
| 8 | AGENTS.md 项目基准 | — | 4.6.0 | `D:\ZephyrAlpha\AGENTS.md` | 项目全局规则 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | MOD-INF-003（旧蓝图层） | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-card-kms\blueprint.md` | 任务卡制度+KMS体系 | deprecated——已被本蓝图合并 |
| 2 | MOD-INF-004（旧双管线） | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vibe-coding-pipelines\blueprint.md` | 双管线流程+M模块 | deprecated——已被本蓝图合并 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 本蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md` | 真源 | 重写 v0.2.0 |
| 2 | Change Folder | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\changes\` | 新建 | 存放任务卡 |
| 3 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 修改 | 更新 MOD-INF-006 条目 |
| 4 | task_repo.py | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | 读取 | 已有代码——蓝图定义其实现规范 |
| 5 | task_completion_gate.py | `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` | 读取 | 已有代码——需同步 G7 门禁 |
| 6 | schemas.py | `D:\ZephyrAlpha\src\zephyr\schemas.py` | 读取 | 已有 Task 模型——蓝图 §3.2 重新声明 |

---

## 1. 设计背景与目标

### 1.1 背景

ZephyrAlpha 项目当前面临三个核心问题，任务系统是解药：

1. **蓝图分散、格式不统一**：MOD-INF-003 和 MOD-INF-004 各用 9 节旧格式，相互引用但内容割裂。AI 读 A 要跳 B——违反 AGENTS.md §5.1 "零记忆重启标准"。

2. **场外草稿未迁入真源**：双管线设计 + 任务卡元模型 + 知识库设计——数千行决策全在草稿里，不在项目真源文件中。

3. **管线未贯通**：蓝图→任务卡拆解→双管线执行→审计工厂 这条完整链路只存在于讨论中。

> **对标**：SDD 论文——spec.md 应是自包含的。ITIL SACM——配置项关系图必须端到端可追踪。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | **合并为一**：MOD-INF-003+004 + 两份场外草稿 = 一份自包含蓝图 | 蓝图文件数 3→1，两份旧蓝图 deprecated |
| 2 | **全链路贯通**：草稿→蓝图→任务卡→双管线→审计工厂——每步有输入/输出/门禁 | 每个环节 Schema 完整 |
| 3 | **防漂移任务卡**：34 字段任务卡模板——上游/下游/允许/禁止/规则/回滚全部写死 | AI 凭任务卡单文件施工——零漂移 |
| 4 | **路径合规创建**：MTH-013 原则——AI 不得自主决定目录层级 | 所有路径可追溯到索引 |
| 5 | **模型分工明确**：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种 | 分工有基准数据支撑 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | KMS 知识库的 KE 条目定义和抓取机制 | 属于独立的 KMS 系统升级——后续讨论，接口预留 |
| 2 | 模型注册表（model-registry.yaml）的完整建设 | 独立小任务——后续处理。任务卡模板中已预埋引用字段 |
| 3 | 草稿治理系统（草稿的讨论优化流程） | 独立系统——后续讨论。本蓝图关注草稿→蓝图之后的链路 |
| 4 | SQLite 数据库物理迁移 | 已有代码——蓝图只定义数据模型规范 |
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
│    ④ §11 施工指引 → 拆卡算法 → N 张任务卡.md（物理文件）             │
│        存放在: changes/{feature-id}/ —— MTH-013 路径合规          │
│                          │                                        │
│           ┌──────────────┼──────────────┐                         │
│           ↓              ↓              ↓                         │
│     ⑤ A区生产线      ⑥ B区生产线    ⑦ C区审计工厂                  │
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
| 2 | **任务卡生命周期**：蓝图自动拆解→Owner确认→创建.md→状态流转(10态+G7)→门禁(G0-G7)→关闭→归档 | 任务卡 = 工件 |
| 3 | **五轴标签体系**：fn/ly/md/st/mo 五轴互不交叉 | 标签 = 索引维度 |
| 4 | **AI双管线执行**：A区 M1-M5（生产）+ B区 M6-M11（审计） | AI执行 = 引擎 |
| 5 | **模型分工策略**：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种救援 | 基于 REG-LLM-001 + GOV-AI-002 |
| 6 | **审计工厂集成**：任务管线产出自动送审——C区 12 维度审计 | 对标 MOD-INF-005 |
| 7 | **KMS 知识管理**（Phase 3+ 排除） | 接口预留——实现在后续版本独立讨论 |

### 2.3 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | SQLite CRUD | `task_repo.py` — 已有代码 |
| 2 | MCP Server | `task_manager_server.py` — 已有代码 |
| 3 | 审计脚本 | MOD-INF-005 — 已有 9 脚本 |
| 4 | context_engine | `context_engine/` — 已有 7 模块 |
| 5 | dashboard | `dashboard/` — 已有代码 |
| 6 | Phase 5 AI 自治 | 预留字段不实现 |

---

## 3. 接口契约

> ⚠️ 完整升级方案——6 个子节。强制 Pydantic V2 BaseModel（ADR-0040）。

### 3.1 公共 API

#### 3.1.1 蓝图拆解器（BlueprintDecomposer）

```python
from pydantic import BaseModel

class BlueprintDecomposer:
    """从蓝图 §11 施工指引拆解为任务卡清单"""

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
          2. 解析步骤中的"创建文件清单"→ 任务卡 downstream_outputs
          3. 解析步骤中的"内容编写指引"→ 任务卡 acceptance_criteria
          4. 按 GOV-AI-002 决策树自动分配 assigned_model
          5. 按 TEMPLATE-TASK-001 模板强制校验每张任务卡 → G7 门禁
        """
        ...
```

#### 3.1.2 任务卡生命周期管理器（TaskLifecycleManager）

```python
class TaskLifecycleManager:
    """10 态状态机 + G0-G7 门禁"""

    def create_task_card(self, task: "TaskCard", output_path: str) -> "TaskCard":
        """创建 .md 任务卡——G0+G7 门禁通过后才写入文件"""
        ...

    def transition(self, task_id: str, from_status: str, to_status: str,
                   gate_check: bool = True) -> "TransitionResult":
        """状态转换——带门禁验证"""
        ...

    def check_gate(self, task_id: str, gate_id: str) -> "GateCheckResult":
        """独立门禁检查"""
        ...
```

#### 3.1.3 管线调度器（PipelineOrchestrator）

```python
class PipelineOrchestrator:
    """调度 A区/B区/C区管线 + 模型分配"""

    def dispatch(self, task_card_path: str, pipeline: str = "auto") -> "DispatchResult":
        """按 GOV-AI-002 决策树分配管线+模型"""
        ...

    def execute_pipeline(self, dispatch_id: str, modules: list[str],
                         model: str) -> "PipelineExecutionResult":
        """串行执行 M 模块链"""
        ...
```

### 3.2 数据模型

#### 3.2.1 TaskCard（任务卡核心模型 — 34 字段）

```python
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime
from typing import Optional

class TaskStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REJECTED = "rejected"
    REWORK = "rework"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CLOSED = "closed"

class GateLevel(str, Enum):
    G0 = "G0"  # 创建门禁——字段完整性
    G7 = "G7"  # 完整度门禁——上游/下游/回滚
    G1 = "G1"  # 指派门禁——模型/管线不冲突
    G2 = "G2"  # 前置门禁——依赖完成
    G3 = "G3"  # 执行门禁——上下文装配
    G4 = "G4"  # 产出门禁——产出物存在+格式
    G5 = "G5"  # 审计门禁——无 Critical
    G6 = "G6"  # 关闭门禁——残留物已处理

class TaskCard(BaseModel):
    # ---- 标识 ----
    task_id: str = Field(..., pattern=r"^TASK-[A-Z]{3}-\d{4}$")
    source_blueprint: str = Field(...)
    source_section: str = Field(...)

    # ---- 内容 ----
    title: str = Field(..., min_length=5, max_length=120)
    description: str = Field(..., min_length=20)
    priority: str = Field(default="P1", pattern=r"^P[0-3]$")

    # ---- 防漂移：上游 ----
    upstream_files: list[str] = Field(..., min_length=1,
        description="执行前必须读取的文件完整绝对路径列表")

    # ---- 防漂移：下游 ----
    downstream_outputs: list[dict] = Field(..., min_length=1,
        description="执行后必须产出的文件 [{path: 完整绝对路径, description: 说明}]")

    # ---- 防漂移：范围 ----
    allowed_touch: list[str] = Field(..., min_length=1,
        description="可以修改的文件白名单——完整绝对路径")
    forbidden_touch: list[str] = Field(..., min_length=1,
        description="禁止修改的文件黑名单——完整绝对路径或glob")

    # ---- 防漂移：规则 ----
    applicable_rules: list[dict] = Field(..., min_length=1,
        description="必须遵守的治理规则 [{module_id, section, reason}]")

    # ---- 防漂移：上下文 ----
    context_assembly_manifest: list[dict] = Field(..., min_length=1,
        description="上下文装配清单 [{file_path, reason}]——G3 门禁校验依据")

    # ---- 防漂移：资源 ----
    estimated_tokens: int = Field(..., ge=1000)
    timeout_minutes: int = Field(..., ge=5)

    # ---- 防漂移：回滚 ----
    rollback_instructions: str = Field(..., min_length=20,
        description="失败时如何撤销已有修改")

    # ---- 验收 ----
    acceptance_criteria: list[str] = Field(..., min_length=1,
        description="验收标准——每条必须客观可验证")

    # ---- 状态 ----
    status: TaskStatus = Field(default=TaskStatus.CREATED)

    # ---- 五轴标签 ----
    tags_fn: list[str] = Field(..., min_length=1)
    tags_ly: str = Field(...)
    tags_md: str = Field(...)
    tags_st: str = Field(default="active")
    tags_mo: list[str] = Field(...)

    # ---- 门禁 ----
    completed_gates: list[GateLevel] = Field(default_factory=list)
    blocked_gates: dict[str, str] = Field(default_factory=dict)

    # ---- 执行 ----
    assigned_model: str = Field(default="deepseek")
    assigned_pipeline: str = Field(default="A")
    pipeline_modules: list[str] = Field(default_factory=list)

    # ---- 依赖 ----
    depends_on: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)

    # ---- 产物/审计/知识 ----
    artifact_paths: list[str] = Field(default_factory=list)
    audit_findings: list["AuditFinding"] = Field(default_factory=list)
    ke_entries: list[str] = Field(default_factory=list)

    # ---- AI 自治（Phase 5 预留）----
    ai_autonomy_level: str = Field(default="supervised")
    autonomy_checklist: list[str] = Field(default_factory=list)

    @field_validator("tags_md")
    @classmethod
    def validate_model(cls, v: str) -> str:
        if v not in {"deepseek", "claude", "glm", "auto"}:
            raise ValueError(f"tags_md must be deepseek/claude/glm/auto, got: {v}")
        return v
```

#### 3.2.2 其他模型

```python
class DecompositionResult(BaseModel):
    total_tasks: int = Field(..., ge=0)
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
| `create_task_card()` | `task` | ✅ | TaskCard 34 字段——G0+G7 门禁通过 |
| | `output_path` | ✅ | 绝对路径——MTH-013 路径合规 |
| `transition()` | `task_id` | ✅ | `TASK-{3大写}-{4数字}` |
| | `from/to_status` | ✅ | 合法枚举值 + 路径在状态机允许列表中 |
| `dispatch()` | `task_card_path` | ✅ | status in {created, queued, rework} |

### 3.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `decompose()` | `DecompositionResult`：N 张 TaskCard + 依赖图 | `FILE_NOT_FOUND` / `NO_CONSTRUCTION_GUIDE` / `G7_VIOLATIONS` |
| `create_task_card()` | `TaskCard` + .md 文件已写入 | `GATE_BLOCKED(G0/G7)` / `DUPLICATE_ID` / `PATH_NOT_COMPLIANT`(MTH-013) |
| `transition()` | 状态转换成功 | `STATUS_MISMATCH` / `GATE_BLOCKED` |
| `dispatch()` | 管线+模型+M模块链已分配 | `INVALID_DISPATCH_STATUS` / `NO_PIPELINE_AVAILABLE` |

### 3.5 MCP 接口

**Tools**：

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `decompose_blueprint` | `decompose()` | `{blueprint_path, output_dir}` | `{total_tasks, task_ids, warnings}` |
| `create_task` | `create_task_card()` | `{task, output_path}` | `{task_id, status, md_path}` |
| `list_tasks` | — | `{status?, tags_fn?, tags_md?, limit?}` | `{tasks: [{task_id, title, status, model}]}` |
| `update_status` | `transition()` | `{task_id, to_status, skip_gate?}` | `{task_id, old_status, new_status, gate?}` |

**错误码**：`TASK_NOT_FOUND(404)` / `STATUS_MISMATCH(409)` / `GATE_BLOCKED(422)` / `VALIDATION_ERROR(400)` / `PATH_NOT_COMPLIANT(422)`

### 3.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| TaskCard 新增字段 | ✅ 向后兼容 | 不影响已有任务卡 |
| TaskCard 删除/重命名字段 | ❌ 破坏性 | 需 Owner 审批 + 迁移 |
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
| 5 | 任务卡 .md + SQLite 双轨制 | 人可读 + 机可查 |
| 6 | 门禁在状态转换前执行 | GOV-TASK-004 §门禁机制 |
| 7 | 任务卡编号 `TASK-{3大写}-{4数字}` | PS-STD-001 §5 |
| 8 | 蓝图 draft/review 状态不得拆卡 | 内容不稳定 |
| 9 | **MTH-013 路径合规创建**——AI 不得自主决定目录层级 | 零自主创建权——必须先查索引 |

### 4.2 容量估算

| 维度 | 当前 | 峰值 | 极限 | 够用？ |
|------|:--:|:--:|:--:|:--:|
| 蓝图 | 6（含 retired） | 200+ | 无上限 | ✅ |
| 任务卡 | 0 | 2000+ | 10000/域 | ✅ |
| Change Folder | 1 | 200+ | 文件系统 | ✅ |
| SQLite | 0 | <100MB | ~281TB | ✅ |
| M 模块 | 11 | 20 | 30+ | ✅ |
| 模型 | 3 | 8 | 受控词表可扩展 | ✅ |

### 4.3 迁移/废弃方案

| # | 对象 | 当前位置 | 状态 |
|---|------|---------|:--:|
| 1 | MOD-INF-003 | `task-card-kms/blueprint.md` | deprecated |
| 2 | MOD-INF-004 | `vibe-coding-pipelines/blueprint.md` | deprecated |
| 3 | 场外草稿 2 份 | `模块候选池/...` | 内容已纳完→待 Owner 删除/归档 |

---

## 5. 依赖关系

| 依赖 | 类型 | 内容 | 版本 |
|------|:---:|------|------|
| PS-STD-001 | 必须 | §5 编号规则 | ≥2.0.0 |
| PS-STD-011 | 必须 | MTH-012 涌现式设计 + MTH-013 路径合规 | ≥2.6.0 |
| GOV-DOC-002 | 必须 | §5.1.2 路径映射 | — |
| GOV-TASK-004 | 必须 | 取消权限、优先级裁决 | ≥2.0.0 |
| GOV-TASK-005 | 必须 | 关闭三步法 | ≥1.1.0 |
| MOD-INF-005 | 必须 | 审计工厂 12 维度 | ≥1.0.0 |
| TEMPLATE-TASK-001 | 必须 | 任务卡模板 | ≥1.0.0 |
| REG-LLM-001 | 必须 | 模型基准排名 | ≥1.1.0 |
| GOV-AI-002 | 必须 | 模型路由策略 | ≥2.0.0 |
| task_repo.py | 必须 | CRUD + 状态机 | 现有代码 |
| task_completion_gate.py | 必须 | 门禁逻辑——需同步 G7 | 现有代码 |
| context_engine/ | Phase 1 | G3 前置——缺 compress/validate | 现有代码 |
| dashboard/ | Phase 1 | 任务可视化 | 现有代码 |

---

## 6. 产出物存放目录

> ⚠️ 所有路径必须与 GOV-DOC-002 §5.1.2 一致。MTH-013 强制。

| 产出物 | 完整绝对路径 |
|--------|------------|
| 蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md` |
| 任务卡 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\changes\{feature-id}\{task_id}.md` |
| 任务卡元数据 | SQLite `task_metadata.db` |
| 管线代码 | `D:\ZephyrAlpha\src\zephyr\pipeline\` |
| MCP Server | `D:\ZephyrAlpha\src\zephyr\mcp\` |
| 仪表盘 | `D:\ZephyrAlpha\src\zephyr\dashboard\` |
| 上下文引擎 | `D:\ZephyrAlpha\src\zephyr\context_engine\` |
| 测试 | `D:\ZephyrAlpha\tests\` |

---

## 7. 集成目标

| 集成目标 | 方式 | 集成点 | 验证 |
|---------|------|--------|------|
| 审计工厂（MOD-INF-005） | B区完成→事件触发 C区 | `execute_pipeline(B) → audit_batch()` | B区后检查 Finding |
| MCP Server | 新增 `decompose_blueprint` Tool | `task_manager_server.py` | ListTools 确认 |
| 仪表盘 | 新增 `/tasks` 路由 | `app.py → list_tasks` | 浏览器渲染 |
| context_engine | G3→触发装配 | `transition(in_progress) → assemble()` | 检查上下文 |

---

## 8. 需要更新的相关内容

| # | 文件 | 更新 |
|---|------|------|
| 1 | `blueprint-registry.yaml` | MOD-INF-006 条目更新（v0.2.0） |
| 2 | `master-document-inventory.yaml` | 登记本蓝图 + 任务卡模板 |
| 3 | `task_completion_gate.py` | 同步 G7 门禁逻辑 |
| 4 | `schemas.py` | 对齐 TaskCard 模型（可选——已有代码与蓝图声明一致即可） |

---

## 9. 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:--:|:--:|------|
| 1 | **任务卡 .md 与 SQLite 不同步** | 中 | 高 | transition() 前双轨一致性校验 |
| 2 | **蓝图 §11 不完整→拆卡遗漏** | 高 | 高 | MTH-012 涌现式设计——§11 必须极度详细；unassigned_items >10%→拒绝拆解 |
| 3 | **DeepSeek V4 Pro 幻觉**（幻觉率 94%） | 高 | 高 | GLM 审查纠错→Claude 关键兜底——三层防御 |
| 4 | **DeepSeek V4 Pro API 不可用** | 低 | 高 | GLM 作为 fallback——见 GOV-AI-002 §降级与容灾 |
| 5 | **路径漂移**——AI 自作主张建目录 | 中 | 高 | MTH-013 零自主创建权——强制索引查询 |
| 6 | **Change Folder 爆炸** | 低 | 低 | 任务卡 CLOSED 后 Change Folder 可归档或删除 |

---

## 10. 后果

### 正面后果

1. **单蓝图自包含**：AI 读一份文件理解全链路——零跳转。
2. **防漂移任务卡**：34 字段——上游/下游/范围/规则/回滚全部写死。AI 凭任务卡+模板即可施工。
3. **路径合规创建**：MTH-013——AI 永不自行决定目录层级。1500 模块未来也不怕文件乱丢。
4. **模型分工有数据支撑**：REG-LLM-001 基准排名 → GOV-AI-002 决策树 → 任务卡 assigned_model。每层可追溯。
5. **三层防御幻觉**：DeepSeek 生产 → GLM 审查 → Claude 兜底。

### 负面后果

1. **任务卡字段多**（34 字段）→ 填卡成本高。缓解：拆解算法自动填充 80%，Owner 只需审核。
2. **蓝图较长**→ AI token 压力。缓解：§11 施工指引结构化——AI 先读目标+施工，其余按需查。

---

## 11. 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 |
|---|--------|---------|
| 1 | 已读取本蓝图全部内容（§1-§10 架构 + §11 施工指引） | 逐节确认 |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开 |
| 3 | PS-STD-001 §5 编号规则已理解 | 能回答"TASK-INF-0001 格式" |
| 4 | GOV-DOC-002 §5.1.2 路径映射已理解 | 能回答"任务卡 .md 放哪" |
| 5 | MTH-013 路径合规创建已理解 | 能执行三步决策流程 |

### 11.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段 | 2 个 Phase（Phase 0 MVP / Phase 1 补齐） |
| 施工模式 | 扩展——基于已有代码扩展 |
| 核心风险 | 蓝图拆卡算法正确性 + G7 门禁与已有 gate 代码的兼容 |

### 11.2 前置条件

| # | 依赖 | 当前 | 满足？ |
|---|------|:--:|:--:|
| 1 | PS-STD-011 ≥ 2.6.0 | ✅ | ✅ |
| 2 | GOV-AI-002 ≥ 2.0.0 | ✅ | ✅ |
| 3 | REG-LLM-001 状态 active | ✅ | ✅ |
| 4 | TEMPLATE-TASK-001 状态 active | ✅ | ✅ |
| 5 | 本蓝图 Owner 已确认 | ☐ | ❌ |

### 11.3 实施步骤

#### Phase 0 — MVP：蓝图收尾 + 代码同步

##### 步骤 1：更新注册表

| 产出位置 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` |
|---------|------|
| 验收标准 | MOD-INF-006 条目 version→0.2.0，blueprint_status→approved |

##### 步骤 2：同步 task_completion_gate.py（G7 门禁）

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` |
|---------|------|
| 验收标准 | ① G7 完整度检查逻辑已加入；② GateLevel 枚举含 G7（在 G0 之后、G1 之前）；③ check_gate("G7") 返回正确结果 |

**创建/更新文件清单**：

| 文件 | 操作 | 完整绝对路径 |
|------|:--:|------------|
| task_completion_gate.py | 修改 | `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` |

#### Phase 1 — 补齐：拆解算法 + MCP + M 模块

##### 步骤 3：实现 BlueprintDecomposer

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py` |
|---------|------|
| 验收标准 | ① decompose() 对本蓝图→产出 N 张任务卡（N≥1）；② 每张任务卡符合 TEMPLATE-TASK-001 格式；③ unassigned_items ≤ 10%；④ G7 门禁通过（上游文件存在、下游路径完整） |

##### 步骤 4：MCP Server 注册 decompose_blueprint

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py` |
|---------|------|
| 验收标准 | decompose_blueprint Tool 可用 |

##### 步骤 5：补齐 context_engine（compress / validate / shadow）

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\context_engine\` |
|---------|------|
| 验收标准 | G3 门禁可用——compress 压缩上下文至 token 预算内 |

##### 步骤 6：燃气 M1-M11 模块（A区 5 + B区 6）

| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pipeline\` |
|---------|------|

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

| 条件 | DeepSeek 执行失败 3 次 / GLM 审查连续驳回 2 次 / Owner 标记"关键" / tags_fn=security / tags_st=experimental |

### 11.4 回滚方案

| 步骤 | 回滚 |
|------|------|
| 1（注册表） | 手动回退 YAML |
| 2（G7 同步） | 注释 G7 代码→恢复旧 gate 逻辑 |
| 3（BlueprintDecomposer） | 删除 .py + test |
| 4（MCP） | 删除 Tool 注册→重启 Server |
| 5（context_engine） | 降级：G3 skip_gate=True |
| 6（M 模块） | 删除 pipeline/ 目录→恢复 |

### 11.5 施工完成标准

| # | 产出物 | 路径 |
|---|--------|------|
| 1 | blueprint-registry.yaml 已更新 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` |
| 2 | task_completion_gate.py G7 可用 | `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` |
| 3 | blueprint_decomposer.py | `D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py` |
| 4 | decompose_blueprint MCP Tool | `D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py` |
| 5 | context_engine 补齐 | `D:\ZephyrAlpha\src\zephyr\context_engine\` |
| 6 | M1-M11 代码+测试 | `pipeline/` + `tests/pipeline/` |

### 11.6 施工状态

| 字段 | 值 |
|------|-----|
| construction_status | phase_1_step_4_complete |
| verification_status | unverified |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 |
|------|------|
| 任务系统全链路架构 | **本文档 §2.1** |
| 任务卡模型（TaskCard 34 字段 + G7 门禁） | **本文档 §3.2**（代码对照：TEMPLATE-TASK-001 模板） |
| AI 双管线 M1-M11 模块分工 | **本文档 §11.3 步骤 6** |
| 蓝图→任务卡拆解算法 | **本文档 §3.1.1** |
| 模型分工策略 | **GOV-AI-002**（本文档 §11.3 步骤6 引用其决策树） |
| 路径合规创建 | **PS-STD-011 MTH-013**（本文档 §4.1 约束 #9） |

### 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-02 | 0.2.0 | **重大重写**：① 删除 §2 架构决策——蓝图只呈现最终设计结果；② 新建 TEMPLATE-TASK-001（34 字段防漂移任务卡模板）；③ 新增 G7 完整度门禁（G0→G7→G1）；④ 新增 MTH-013 路径架构合规创建——写入 §4.1 约束 #9；⑤ 模型分工重分配：DeepSeek V4 Pro 主力 + GLM M7 深度审查 + Claude 特种救援（GOV-AI-002 v2.0.0）；⑥ KMS 排除 Phase 3+；⑦ 蓝图 12节→11节；⑧ 必备链接 +6（REG-LLM-001/GOV-AI-002/TEMPLATE-TASK-001 等）。遵循 MTH-012 涌现式设计——先填模板，后纳血肉。 |
| 2026-05-02 | 0.1.0 | 初始版本——合并 MOD-INF-003+004 + 两份场外草稿为 12 节蓝图。 |



--- FILE: task-card-template.md (任务卡模板) ---
PATH: D:\ZephyrAlpha\docs\01_policies_and_standards\templates\task-card-template.md

---
module_id: "TEMPLATE-TASK-001"
title: "任务卡模板 — 防漂移标准格式"
doc_type: template
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
summary: "ZephyrAlpha 任务卡唯一标准模板。21 个字段，强制填写——上游文件完整路径、下游产出完整路径、允许/禁止触碰范围、适用规则清单、上下文装配清单、回滚指令。设计目标：任何新 AI session 拿到一张按此模板填写的任务卡，无需查阅任何外部文件即可开始正确施工——零漂移、零幻觉。"
tags: [task-card, template, anti-drift, vibe-coding, zero-hallucination]
depends_on:
  - {target: PS-STD-001, at: "§5", why: "编号规则 task_id 格式"}
  - {target: GOV-DOC-002, at: "§5.1.2", why: "所有路径必须与路径映射一致"}
  - {target: MOD-INF-006, at: "§4.2", why: "TaskCard 模型真源"}
---

# 任务卡模板

> module_id: TEMPLATE-TASK-001 | version: 1.0.0 | status: active

---

## ⚠️ 填写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须为完整绝对路径**（含盘符 `D:\`） | 路径漂移——文件创建到错误位置 |
| 2 | `upstream_files` 必须 100% 精确——AI 不会自己去查蓝图，你写什么路径他就读什么文件 | 溯源漂移——AI 读了错误的文件版本 |
| 3 | `downstream_outputs` 必须 100% 精确——AI 不会自己判断文件该放哪 | 路径漂移——产出物散落各处 |
| 4 | `forbidden_touch` 必须明确列出——宁可多写，不能漏写 | 范围漂移——AI 改了不该改的文件 |
| 5 | `acceptance_criteria` 每条必须客观可验证——"代码质量好"不合法，"Pydantic V2 模型含 field_validator"合法 | AI 不知道"好"是什么意思 |
| 6 | 禁止出现"待定"/"视情况而定"/"可"——所有字段必须有明确值 | AI 自行推断 → 推断错误 |
| 7 | `rollback_instructions` 不能为空——每次施工均有不可逆失败的风险 | 不可逆破坏——AI 不知道如何撤回 |

---

## 填写示例：一张完整的防漂移任务卡

> 以"实现 BlueprintDecomposer.decompose() 核心逻辑"为例。

```markdown
---
task_id: "TASK-INF-0042"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §12.3 步骤4"

# ===== 内容 =====
title: "实现 BlueprintDecomposer.decompose() 核心逻辑"
description: |
  从蓝图 §12 施工指引自动拆解任务卡。
  核心算法：正则解析 §12.3 → 每步骤1张任务卡 → 解析 §2.2 决策推导链 → depends_on 依赖图 → 按模型分工策略分配 assigned_model。
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\\docs\\01_policies_and_standards\\templates\\task-card-template.md"
  - "D:\\ZephyrAlpha\\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\\src\\zephyr\\schemas.py"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\\src\\zephyr\\core\\blueprint_decomposer.py"
    description: "BlueprintDecomposer 类——decompose() 方法"
  - path: "D:\\ZephyrAlpha\\\tests\\core\\test_blueprint_decomposer.py"
    description: "单元测试——验证 decompose() 的依赖图正确性"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\\src\\zephyr\\core\\blueprint_decomposer.py"
  - "D:\\ZephyrAlpha\\\tests\\core\\test_blueprint_decomposer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\\src\\zephyr\\schemas.py"
  - "D:\\ZephyrAlpha\\\src\\zephyr\\db\\*.py"
  - "D:\\ZephyrAlpha\\\docs\\01_policies_and_standards\\**\\*.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-{DOMAIN}-{NNNN}"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——禁止 dataclass"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建——产出物必须符合目录结构标准"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "本蓝图——了解 §12 施工指引结构 + 模型分工策略"
  - file_path: "D:\\ZephyrAlpha\\\docs\\01_policies_and_standards\\templates\\task-card-template.md"
    reason: "任务卡模板——知道生成的任务卡 .md 该长什么样子"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 45

# ===== 验收标准 =====
acceptance_criteria:
  - "decompose() 输入本蓝图 → 产出 N 张任务卡（N ≥ 1）"
  - "依赖图正确推导 D-001→D-002/D-003/D-004/D-005"
  - "unassigned_items 为空或 ≤ 10%"
  - "每张任务卡含完整 upstream_files / downstream_outputs 绝对路径"
  - "Pydantic V2 BaseModel——导入路径 from pydantic import BaseModel"
  - "回滚方案：删除新创建的文件即可恢复"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py
  2. 删除 D:\ZephyrAlpha\tests\core\test_blueprint_decomposer.py
  3. 如果 task_repo.py 被修改——手动还原（检查 forbidden_touch 已防止此情况）

# ===== 依赖 =====
depends_on: []
blocked_by: []

# ===== 状态 =====
status: "created"

# ===== 五轴标签 =====
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

# ===== 门禁 =====
completed_gates: []
blocked_gates: {}

# ===== 产物 =====
artifact_paths: []

# ===== 审计 =====
audit_findings: []

# ===== 知识 =====
ke_entries: []

# ===== AI 自治 =====
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
```

---

## 字段定义速查表

| # | 字段 | 类型 | 必填 | 说明 | 防漂移类型 |
|:--:|------|------|:--:|------|:--:|
| 1 | `task_id` | `str` | ✅ | 唯一ID：`TASK-{3大写字母}-{4数字}` | — |
| 2 | `source_blueprint` | `str` | ✅ | 来源蓝图 module_id | 溯源 |
| 3 | `source_section` | `str` | ✅ | 来源蓝图节号 | 溯源 |
| 4 | `title` | `str` | ✅ | 一句话任务标题（5-120字） | — |
| 5 | `description` | `str` | ✅ | 详细描述（≥20字） | — |
| 6 | `priority` | `str` | ✅ | P0(阻塞)/P1(正常)/P2(延后)/P3(Backlog) | — |
| 7 | `upstream_files` | `list[路径]` | ✅ | **执行前必须读取的文件完整绝对路径** | 溯源漂移 |
| 8 | `downstream_outputs` | `list[{path,desc}]` | ✅ | **执行后必须产出的文件完整绝对路径** | 路径漂移 |
| 9 | `allowed_touch` | `list[路径]` | ✅ | **可以修改的文件白名单** | 范围漂移 |
| 10 | `forbidden_touch` | `list[路径/glob]` | ✅ | **禁止修改的文件黑名单** | 范围漂移 |
| 11 | `applicable_rules` | `list[{module_id, section, reason}]` | ✅ | **必须遵守的治理规则清单** | 规则漂移 |
| 12 | `context_assembly_manifest` | `list[{file_path, reason}]` | ✅ | **上下文装配清单**——G3 门禁校验依据 | 上下文断裂 |
| 13 | `assigned_model` | `str` | ✅ | deepseek / claude / glm | 能力漂移 |
| 14 | `assigned_pipeline` | `str` | ✅ | A(生产) / B(审计) / C(横切) | — |
| 15 | `pipeline_modules` | `list[str]` | ✅ | 管线M模块链 | — |
| 16 | `estimated_tokens` | `int` | ✅ | 预估 token 消耗 | Token溢出 |
| 17 | `timeout_minutes` | `int` | ✅ | 超时阈值 | 僵尸任务 |
| 18 | `acceptance_criteria` | `list[str]` | ✅ | **验收标准——每条必须客观可验证** | 标准漂移 |
| 19 | `rollback_instructions` | `str` | ✅ | **回滚指令——失败时如何撤销** | 不可逆破坏 |
| 20 | `depends_on` | `list[str]` | ❌ | 前置依赖任务卡 ID | 依赖断裂 |
| 21 | `blocked_by` | `list[str]` | ❌ | 阻塞当前任务的任务卡 ID | 依赖断裂 |
| 22 | `status` | `str` | ✅ | 10态之一（created→...→closed） | — |
| 23 | `tags_fn` | `list[str]` | ✅ | 功能域标签：infra/biz/data/observability/security | 检索漂移 |
| 24 | `tags_ly` | `str` | ✅ | 层级标签：l01_infrastructure/... | 检索漂移 |
| 25 | `tags_md` | `str` | ✅ | 模型分配标签：deepseek/claude/glm | 检索漂移 |
| 26 | `tags_st` | `str` | ✅ | 稳定性标签：active/stable/experimental | 检索漂移 |
| 27 | `tags_mo` | `list[str]` | ✅ | 模块归属标签 | 检索漂移 |
| 28 | `completed_gates` | `list[str]` | ❌ | 已通过的门禁 | — |
| 29 | `blocked_gates` | `dict[str,str]` | ❌ | 被阻塞门禁及原因 | — |
| 30 | `artifact_paths` | `list[str]` | ❌ | 产出物路径——执行中填充 | — |
| 31 | `audit_findings` | `list` | ❌ | 审计发现 | — |
| 32 | `ke_entries` | `list[str]` | ❌ | 关联 KE 编号 | — |
| 33 | `ai_autonomy_level` | `str` | ❌ | AI 自治级别——Phase 5 预留 | — |
| 34 | `autonomy_checklist` | `list[str]` | ❌ | 自治清单——Phase 5 预留 | — |

> **注**：共 34 个字段（含可选字段），其中 21 个为必填。`assigned_model` 合法值受模型注册表（`model-registry.yaml`，TBD）约束。

---

## 路径填写规范

| 类型 | 格式 | 示例 | 非法示例 |
|------|------|------|---------|
| 项目内文件 | `D:\ZephyrAlpha\{相对路径}` | `D:\ZephyrAlpha\src\zephyr\schemas.py` | `src/zephyr/schemas.py`（无盘符，相对路径） |
| 多文件 glob | `D:\...\*.py` | `D:\ZephyrAlpha\src\zephyr\db\*.py` | `src/zephyr/db/*.py` |
| 目录级 glob | `D:\...\**\*.md` | `D:\ZephyrAlpha\docs\**\*.md` | `docs/**/*.md` |

---

## G7 门禁：完整度检查

在 G0（字段完整性）之后、G1（指派门禁）之前，强制执行 G7 门禁：

| 检查项 | 判定标准 | 不通过 → |
|--------|---------|---------|
| `upstream_files` 每个路径 | `os.path.exists(path)` = True | 拒绝创建——上游文件不存在，原因写入 `blocked_gates.G7` |
| `downstream_outputs` 每个路径 | 含完整绝对路径（以 `D:\` 开头） | 拒绝创建——路径不完整，原因写入 `blocked_gates.G7` |
| `applicable_rules` 每条的 module_id | 在注册表中存在（`document-metadata-index.yaml`） | 告警（不拒绝）——但规则可能不存在 |
| `acceptance_criteria` 每条 | 含至少 1 个可验证关键词（路径/格式/数字/文件存在） | 告警（不拒绝）——但标准可能无法验证 |
| `rollback_instructions` | 不为空 + 不少于 20 字 | 拒绝创建——无回滚方案 |

---

## 任务卡 .md 文件存放规范

```
D:\ZephyrAlpha\docs\03_modules\{layer}\{module}\changes\{feature-id}\{task_id}.md
```

示例：
```
D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\changes\MOD-INF-006\TASK-INF-0042.md
```

> **规则**：任务卡 .md 文件必须放在对应蓝图模块的 `changes/` 子目录下。创建 `changes/` 目录前执行 MTH-013 路径合规检查。

---

*本文档是 ZephyrAlpha 所有任务卡的唯一格式标准。任何不符合此模板的任务卡，G7 门禁将拒绝创建。*
```
