---
module_id: GOV-FSTR-001
submodule_paths_scope: restructuring
title: "File Structure Governance 蓝图 — 文件结构治理·大文件拆分·重复合并·安全搬家"
doc_type: blueprint
status: Active
version: "4.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-12"
ttl: permanent
construction_progress: design_only
actual_disk_path: "scripts/governance/restructuring/"
template_for: blueprint
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 3
functional_domain: governance
parent_module: ""
belongs_to: "MOD-MASTER-001"
rule_form: structural
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: "INF-020", at: "全篇", why: "Audit Trail——重组操作审计"}
  - {target: "INF-021", at: "全篇", why: "Rollback——重组回滚"}
  - {target: "INF-023", at: "全篇", why: "Drift Detector——重组后漂移检测"}
  - {target: "INF-016", at: "全篇", why: "Shared Core——注册表访问"}
references:
  - {path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md", section: "全篇", why: "蓝图模板v3.6"}
  - {path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml", section: "全篇", why: "压缩工作流标准"}
codification_level: L2
codification_at: "2026-05-15"
summary: "文件结构治理蓝图——大文件拆分、跨目录重复合并、安全搬家。覆盖全项目文件结构治理。"
tags: [file-structure-governance, cross-layer, governance, file-split, dedup, migration]
priority: P0
runtime_plane: cold
---

> module_id: GOV-FSTR-001 | version: 4.2.0 | status: active | layer: cross_layer
> actual_disk_path: scripts/governance/restructuring/ | generation: 3 | construction_progress: design_only

# File Structure Governance 蓝图 — 文件结构治理·大文件拆分·重复合并·安全搬家

> **真源声明**：本蓝图是 ZephyrAlpha 文件结构治理的唯一真源。

## 概述

本蓝图定义 ZephyrAlpha 系统重组治理规则——解决快速迭代中产生的大文件（>500行）、跨目录重复文件、未按需激活的模块等问题。核心职责：文件拆分（>500行按职责拆分）、重复合并（跨目录同功能合并为唯一真源）、按需激活（未使用模块延迟加载）、安全搬家（文件移动不破坏导入链）。当前规模 ~20 个大文件 + ~10 组跨目录重复，目标 LLM 友好上限 300 行/文件。上游被 MOD-MASTER-001 治理，下游消费 INF-020（审计）、INF-021（回滚）、INF-023（漂移检测）。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[system-dependency-map.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/system-dependency-map.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> 防止 construction_progress 与实际代码不符。每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§14）。
> 本蓝图为流程蓝图，重组脚本待施工。代码对齐验证待脚本落地后填写。

### §0.1 代码文件清单

> **架构归属SSoT**：`data/databases/depgraph.db`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules GOV-FSTR-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | scan_targets.py | §16 施工步骤：扫描 | 扫描大文件、重复项、导入链 | 未实现 | 重组脚本待施工 |
| 2 | split_executor.py | §16 施工步骤：拆分 | 大文件拆分执行 | 未实现 | 重组脚本待施工 |
| 3 | merge_executor.py | §16 施工步骤：合并 | 跨目录重复合并执行 | 未实现 | 重组脚本待施工 |
| 4 | import_validator.py | §16 施工步骤：验证 | 导入链验证 | 未实现 | 重组脚本待施工 |
| 5 | migrate_executor.py | §16 施工步骤：迁移 | 文件移动 | 未实现 | 重组脚本待施工 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = design_only → 重组规则已定义 | 检查蓝图 §2 职责范围 | ☐ |
| 重组脚本待施工 | 检查 `D:\ZephyrAlpha\scripts\governance\restructuring\` 目录 | ☐ |
| actual_disk_path 与 §11 一致 | 比对 frontmatter 与 §11 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v3.0.0 | 重组规则定义 | 自动化重组脚本 | 待施工 |
| v4.0.0 | 同 v3.0.0 + 模板v3.3对齐+规格化 | 自动化重组脚本 | 待施工 |
| v4.2.0 | 同 v4.0.0 + 模板v3.5/v3.6对齐 | 自动化重组脚本 | 待施工 |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 项目在快速迭代中产生了大文件（>500行）、跨目录重复文件、未按需激活的模块等问题，影响 LLM 理解效率和代码维护性。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 大文件拆分 | >500行文件拆分为职责单一模块 |
| 2 | 跨目录重复合并 | 同功能文件合并为唯一真源 |
| 3 | 按需激活 | 未使用模块延迟加载 |
| 4 | LLM接入 | 重组后文件对LLM友好（<300行/文件） |
| 5 | 版本分叉审计 | 重组操作可追溯——依赖 INF-020 Audit Trail |
| 6 | 安全搬家 | 文件移动不破坏导入链 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 代码逻辑重构 | 各模块蓝图负责 |
| 2 | 新功能开发 | 各模块蓝图负责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 重组必须原子执行 | 中间状态不可用——需回滚机制 |
| 导入链必须完整 | 移动后所有 import 仍有效——需自动验证 |
| 注册表必须同步 | 重组后注册表反映新路径——依赖 auto_sync_all_registries.py 同步 + audit_registration.py 验证 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 文件拆分 | 大文件按职责拆分为小文件 |
| 2 | 重复合并 | 跨目录同功能文件合并 |
| 3 | 路径迁移 | 文件移动+导入链修复 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 代码质量改进 | code-dedup-engine (INF-017) |
| 2 | 门禁检查 | gate-engine (INF-007) |
| 3 | 注册表同步 | auto_sync_all_registries.py + audit_registration.py |
| 4 | 审计追踪 | INF-020 Audit Trail (bridge.py write_to_core) |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | RestructurePlanner | 生成重组计划 | INF-016 ModuleRegistry | 同步调用 |
| 2 | RestructureExecutor | 执行重组操作 | INF-020 AuditTrail, INF-021 Rollback | 同步调用 |
| 3 | ImportChainValidator | 验证导入链完整性 | — | 同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | 全项目文件清单 | 识别>500行文件+跨目录重复 | RestructurePlan | dict |
| 2 | RestructurePlan | 执行拆分/合并/迁移 | RestructureResult + AuditLog | dict |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| PLANNED | Owner 审批 | EXECUTING | 计划完整 |
| EXECUTING | 执行完成 | VALIDATING | 无异常 |
| VALIDATING | audit_registration exit 0 | COMPLETED | 导入链完整 |
| EXECUTING | 执行失败 | ROLLED_BACK | INF-021 回滚成功 |

---

## §4 接口契约

### 4.1 公共 API

```python
class RestructurePlanner:
    """重组计划生成器"""

    def plan(self, scope: str) -> "RestructurePlan":
        """
        生成重组计划
        输入：scope = "full" | "module:<id>" | "file:<path>"
        输出：RestructurePlan 包含拆分/合并/迁移操作列表
        """

class RestructureExecutor:
    """重组执行器"""

    def execute(self, plan: "RestructurePlan") -> "RestructureResult":
        """
        执行重组计划
        输入：RestructurePlan
        输出：RestructureResult 包含成功/失败操作列表
        """
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum

class RestructureOpType(str, Enum):
    SPLIT = "split"
    MERGE = "merge"
    MIGRATE = "migrate"

class RestructurePlan(BaseModel):
    operations: list[RestructureOperation] = Field(..., description="重组操作列表")

class RestructureOperation(BaseModel):
    op_type: RestructureOpType = Field(..., description="操作类型")
    source_path: str = Field(..., description="源文件绝对路径")
    target_path: str = Field(..., description="目标文件绝对路径")

class RestructureResult(BaseModel):
    plan_id: str = Field(..., description="计划ID")
    success_count: int = Field(..., description="成功操作数")
    fail_count: int = Field(..., description="失败操作数")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `plan()` | `scope` | ✅ | "full" / "module:<id>" / "file:<path>" |
| `execute()` | `plan` | ✅ | RestructurePlan 实例 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `plan()` | `RestructurePlan` | `SCOPE_INVALID` |
| `execute()` | `RestructureResult` | `EXECUTION_FAILED` / `ROLLBACK_REQUIRED` |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增操作类型 | ✅ 向后兼容 | 不影响已有消费者 |
| 修改操作字段 | ❌ 破坏性 | 需 Owner 审批 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 重组必须原子执行 | 中间状态不可用——需回滚机制 |
| 2 | 导入链必须完整 | 移动后所有 import 仍有效——需自动验证 |
| 3 | 注册表必须同步 | 重组后注册表反映新路径——依赖 auto_sync_all_registries.py 同步 + audit_registration.py 验证 |
| 4 | LLM 友好上限 | 300 行/文件 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| >500行文件数 | ~20 | ~50 | — | ✅ | 按需拆分 |
| 跨目录重复文件 | ~10 | ~30 | — | ✅ | 按需合并 |

### 5.3 迁移

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 执行状态 |
|---|-------------|---------|---------|---------|:-------:|
| — | 本蓝图不涉及文件废弃/迁移 | — | — | — | — |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 导入链断裂 | import 验证脚本 | 自动回滚（INF-021） | 全系统不可用 |
| 2 | 注册表不同步 | auto_sync_all_registries.py | 强制运行 auto_sync_all_registries.py --all + audit_registration.py 验证 | 孤儿文件 |
| 3 | 部分重组失败 | 执行结果检查 | 回滚已执行操作 | 中间状态 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 重组导致导入链断裂 | 高 | 原子执行+自动回滚 | import 验证脚本 |
| 2 | 重组后注册表不一致 | 中 | 强制 auto_sync_all_registries.py --all + audit_registration.py 验证 | auto_sync exit 0 && audit exit 0 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | ImportChainValidator | 文件移动后 import 仍有效 | 100% 通过 |
| 2 | 集成测试 | 重组→注册表同步 | 重组后 auto_sync_all_registries.py --all exit 0 && audit_registration.py exit 0 | 端到端通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| INF-020 Audit Trail | 必须 | 重组操作审计 | — | `D:\ZephyrAlpha\docs\03_modules\_domain-infra_ops\audit-trail\blueprint.md` |
| INF-021 Rollback | 必须 | 重组回滚 | — | `D:\ZephyrAlpha\docs\03_modules\_domain-infra_ops\rollback-system\blueprint.md` |
| INF-023 Drift Detector | 必须 | 重组后漂移检测 | — | `D:\ZephyrAlpha\docs\03_modules\_domain-infra_ops\drift-detector\blueprint.md` |
| INF-016 Shared Core | 必须 | 注册表访问 | — | `D:\ZephyrAlpha\docs\03_modules\_domain-infra_ops\shared-core\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint GOV-FSTR-001` |

### 10.3 内部依赖图

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| scan_targets.py | split_executor.py | 扫描产出物是拆分执行的前置条件 | 检查扫描结果 JSON 是否存在 |
| split_executor.py | import_validator.py | 拆分后需要验证导入链 | 检查拆分后的文件是否存在 |
| merge_executor.py | migrate_executor.py | 合并后需迁移路径 | 检查合并结果 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 操作类型多（拆分/合并/迁移）|
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖需要验证 |
| 3 | 临时时态内容自动清理 | 否 | 施工步骤在完成后由施工者手动清理 |
| 4 | 施工步骤完成度自动检测 | 是 | 待施工中，完成度需要追踪 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具 | 缺口 |
|---|---------|---------|---------|------|
| 1 | 依赖对齐自动验证 | CI 门禁 | validate_path_alignment.py | 无 |
| 2 | 施工步骤完成度自动检测 | 产出物存在性检查 | auto_sync_all_registries.py + audit_registration.py | 需集成到重组流程 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖对齐自动验证 | CI pipeline | PR 提交时 |
| 2 | 施工步骤完成度自动检测 | 手动 | 施工步骤完成后 |

---

## §11 产出物

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\restructuring\blueprint.md` | 本文件 |
| 重组脚本 | `D:\ZephyrAlpha\scripts\governance\restructuring\` | 重组自动化脚本（待施工） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| blueprint_registry.yaml | 注册 | GOV-FSTR-001 条目 | 条目存在 |
| INF-020 Audit Trail | 审计事件 | 重组操作可追溯 | 审计日志存在 |
| INF-021 Rollback | 回滚点 | 重组可回滚 | 回滚成功 |

---

## §13 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | blueprint_registry.yaml | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress 更新 | 重组进度变更 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 导入链断裂——文件移动后所有 import 失效 | 中 | 高 | 原子执行+自动回滚 | 风险 |
| 2 | 注册表不同步——重组后注册表反映旧路径 | 中 | 中 | 重组后强制 auto_sync_all_registries.py --all | 风险 |
| 3 | LLM context溢出——拆分后文件仍需维护 | 低 | 中 | 300行上限强制 | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§15 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则（§5）已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 4 | GOV-DOC-002 防幻觉路径映射（§5.1.2）已理解 | 能回答"某类文件该放哪" | ☐ |
| 5 | MTH-013 路径合规创建原则已理解 | 能回答"新文件创建前三步验证流程" | ☐ |
| 6 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 7 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 渐进式 |
| 核心风险 | 导入链断裂 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板v3.3对齐+规格化） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | INF-020 Audit Trail | hard | phase_1_partial | ☐ |
| 2 | INF-021 Rollback | hard | phase_2_complete | ☐ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：识别重组目标

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 RestructurePlanner |
| 产出位置 | `D:\ZephyrAlpha\scripts\governance\restructuring\` |
| 验收标准 | 拆分计划完整——所有>500行文件已识别 |
| 验证命令 | `python scripts/governance/restructuring/scan_targets.py --warn-only` |
| G7 检查项 | 上游文件清单完整？下游产出物路径精确？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| GOV-FSTR-001 | scan_targets.py | code | `D:\ZephyrAlpha\scripts\governance\restructuring\scan_targets.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| scan_targets.py | 扫描全项目>500行文件+跨目录重复 | ①文件行数统计 ②重复内容检测 ③JSON格式输出 |

#### 步骤 2：执行拆分

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 RestructureExecutor |
| 产出位置 | `D:\ZephyrAlpha\scripts\governance\restructuring\` |
| 验收标准 | 拆分后文件 import 成功 |
| 验证命令 | `python -c "import zephyr"` |
| G7 检查项 | 导入链完整？注册表已同步（auto_sync_all_registries.py exit 0）？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| GOV-FSTR-001 | split_executor.py | code | `D:\ZephyrAlpha\scripts\governance\restructuring\split_executor.py` |
| GOV-FSTR-001 | import_validator.py | code | `D:\ZephyrAlpha\scripts\governance\restructuring\import_validator.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| split_executor.py | 按 RestructurePlan 执行文件拆分 | ①原子写入 ②导入链自动修复 ③回滚支持 |
| import_validator.py | 验证文件移动后导入链完整性 | ①全项目 import 扫描 ②断裂检测 ③修复建议 |

#### 步骤 3：合并重复+验证

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 RestructureExecutor |
| 产出位置 | `D:\ZephyrAlpha\scripts\governance\restructuring\` |
| 验收标准 | auto_sync_all_registries.py --all exit 0 && audit_registration.py exit 0 |
| 验证命令 | `python scripts/governance/auto_sync_all_registries.py --all && python scripts/governance/audit_registration.py` |
| G7 检查项 | 无孤儿文件？所有 import 链完整？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| GOV-FSTR-001 | merge_executor.py | code | `D:\ZephyrAlpha\scripts\governance\restructuring\merge_executor.py` |
| GOV-FSTR-001 | migrate_executor.py | code | `D:\ZephyrAlpha\scripts\governance\restructuring\migrate_executor.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| merge_executor.py | 跨目录同功能文件合并 | ①内容去重 ②引用重定向 ③调用 auto_sync_all_registries.py 同步注册表 |
| migrate_executor.py | 文件路径迁移+导入链修复 | ①原子移动 ②全局引用更新 ③调用 auto_sync_all_registries.py 更新注册表路径 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 扫描失败 | 重新扫描 |
| 2 | 拆分失败 | git checkout -- 恢复被拆分文件 |
| 3 | 合并失败 | git checkout -- 恢复被合并文件 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | 重组脚本 | `D:\ZephyrAlpha\scripts\governance\restructuring\` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | not_started | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| >500行文件数 | ~20 | `find . -name "*.py" \| xargs wc -l` |
| 跨目录重复文件 | ~10 | 全项目 Grep |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-RSTR-001 | 无自动化重组脚本 | 施工 scan_targets.py + split/merge/migrate_executor.py | 重组需求出现时 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v3.0.0 | 1 | 基线 | 重组规则定义 | ❌ |
| v4.0.0 | 2 | 模板v3.3对齐+规格化 | 章节重排+frontmatter更新+§16增强+§17补全 | ❌ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-RSTR-001 | 自动化重组脚本未施工 | P1 | v5.0.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| RestructurePlanner | GAP-RSTR-001 | scan_targets.py | Phase 1 | 待施工 |
| RestructureExecutor | GAP-RSTR-001 | split_executor.py / merge_executor.py / migrate_executor.py | Phase 2-3 | 待施工 |
| ImportChainValidator | GAP-RSTR-001 | import_validator.py | Phase 2 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-RSTR-01 | 重组采用原子执行+自动回滚 | A:原子/B:非原子 | A | 中间状态不可用——必须原子 | 2026-05-12 |
| 2 | D-RSTR-02 | LLM友好上限300行/文件 | A:300/B:500/C:无限制 | A | LLM context window 限制 | 2026-05-12 |
| 3 | D-RSTR-03 | 蓝图按模板v3.3重构 | A:保持旧结构/B:按新模板重构 | B | REQUIRED_SECTIONS合规；AI阅读顺序优化 | 2026-05-14 |
| 4 | D-RSTR-04 | 蓝图模板 v3.5/v3.6 升级 | A:不升级/B:升级 | B | 模板升级要求 | 2026-05-14 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链或垃圾积累 |
| 8 | 禁止"待定"/"建议"/"按需"等模糊词 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容一旦执行完毕即成为历史 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | AI 不知道该读哪个蓝图 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同 → 原地升级（§17 容量升级附录增量记录）
  └ 职责不同 → 拆分独立蓝图（独立 frontmatter + 概述 + §0~§18）
      触发条件（满足任一）：独立 module_id 前缀 / 独立 Phase 路线图 / 独立依赖图（交集<50%）

STEP 3: 拆分后验证
  - 独立 frontmatter + 概述 + §0~§18
  - belongs_to 指向父蓝图
  - blueprint_registry.yaml 同步更新
```

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。
> 来源：蓝图特有内容（B-16）——重组蓝图涉及文件迁移/删除，安全删除协议是核心防护
> 仅本蓝图需要：其他蓝图不涉及批量文件删除操作
> 不可砍理由：砍掉后 AI 可能直接删除文件导致不可逆损失

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| — | 本蓝图不涉及文件删除 | — | — | — | — |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | 给足缓冲期 |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 + MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | code-dedup-engine | `D:\ZephyrAlpha\src\zephyr\infra_ops\code_dedup_engine\` | 代码去重 | code-dedup-engine 做运行时去重检测，本蓝图做文件级重组——层级不同 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 重组蓝图 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\restructuring\blueprint.md` | 修改 | v3.3模板对齐 |
| 2 | blueprint_registry.yaml | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | construction_progress 更新 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 重组规则与流程 | **本文档 §1-§16** | — |
| 重组操作审计日志 | INF-020 Audit Trail | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | INF-020 Audit Trail | RSTR-001 重组计划 |
| Tier 1 | INF-023 Drift Detector | RSTR-002 重组结果 |
| Tier 2 | INF-016 Shared Core | 注册表同步 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 重组规则变更 | 通知 INF-020/INF-023 | 更新注册表 |
| 重组流程变更 | 更新审计事件格式 | 更新集成路由 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 重组策略变更 | 需 Owner 审批 |
| 具体文件移动 | AI 可自主 |
| 接口契约变更 | 需 Owner 审批 + 通知所有消费者 |

### 负向责任

| # | 本蓝图不涉及 | 由谁负责 |
|---|-------------|---------|
| 1 | 代码逻辑重构 | 各模块蓝图负责 |
| 2 | 新功能开发 | 各模块蓝图负责 |

### 触发条件

| 场景 | AI 应读取本蓝图 |
|------|---------------|
| 发现 >500 行文件 | 读 §4 接口契约 + §16 施工指引 |
| 发现跨目录重复文件 | 读 §2 职责范围 + §4 合并规则 |
| 文件搬家需求 | 读 §4 安全搬家 + §6 导入链验证 |

### 导航路径

| 步骤 | 操作 |
|:---:|------|
| 1 | 读本蓝图 §4 接口契约 → 确认操作类型 |
| 2 | 读重组规范 → 了解拆分/合并/搬家规则 |
| 3 | 执行重组 → 按 §16 施工指引步骤落地 |

### 漂移防护

| 修改本文件 | 必须同步更新 |
|-----------|------------|
| 重组规则变更 | INF-020 Audit Trail + INF-023 Drift Detector |
| 文件移动 | import 链验证脚本 |
| construction_progress 变更 | blueprint_registry.yaml |
