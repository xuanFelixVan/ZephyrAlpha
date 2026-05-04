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
