---
module_id: MOD-MASTER-001
title: "Agent Spec 蓝图 — CBAC能力矩阵·Skill路由"
doc_type: blueprint
status: Active
version: "1.3.0"
layer: L1_foundation
layer_name: cross_layer
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
ttl: permanent
last_updated: "2026-05-15"
last_verified: "2026-05-15"
construction_progress: completed
actual_disk_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_agent_spec.md"
template_for: blueprint
generation: 2
functional_domain: infrastructure
parent_module: "MOD-MASTER_BLUEPRINT"
belongs_to: "MOD-MASTER_BLUEPRINT"
rule_form: structural
scope: global
stability: stable
verifiability: automated
priority: P0
summary: "CBAC能力访问控制矩阵：12系统×12系统完整授权关系、违规响应、离线更新流程、编排器特权声明、Skill路由接口定义。"
codification_level: L1
codification_at: "2026-05-15"
depends_on:
  - target: "MOD-MASTER-002"
    at: "§二"
    why: "基线蓝图契约总表——CBAC矩阵基于CT-*契约定义"
  - target: "MOD-INF-019"
    at: "全篇"
    why: "Agent Spec蓝图——Skill路由接口定义"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_baseline.md"
    section: "§二"
    why: "基线蓝图契约总表"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md"
    section: "全篇"
    why: "蓝图模板v3.6"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml"
    section: "全篇"
    why: "压缩工作流标准"
tags:
  - master-blueprint
  - cbac
  - capability-matrix
  - agent-spec
  - skill-routing
  - access-control
responsibility_domain: 
build_status: stable
design_maturity: design
---

# Agent Spec 蓝图 — CBAC能力矩阵·Skill路由

> module_id: MOD-MASTER-001 | version: 1.3.0 | status: active | layer: cross_layer | blueprint_level: domain
> actual_disk_path: D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_agent_spec.md | generation: 2 | construction_progress: completed

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）
> - 基线蓝图：[blueprint_baseline.md](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md)

---

## 概述

本蓝图是 MOD-MASTER_BLUEPRINT 的 Agent Spec 接口定义——定义了 ZephyrAlpha 12 个基础设施系统间的能力访问控制矩阵（CBAC）。核心职责：跨系统调用的授权关系定义、违规响应规则、离线更新流程、编排器特权声明、Skill 路由接口。上游依赖 baseline（CT-* 契约定义），下游被 gates/circuit_breaker.py 消费执行。

---

## §1 设计背景与目标

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | CBAC 矩阵覆盖所有跨系统调用 | 12×12 矩阵完整 |
| 2 | 违规响应自动化 | LOG+ALERT+DENY 三步自动 |
| 3 | 离线更新支持 | checksum 校验通过 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 系统内部权限控制 | 各模块蓝图负责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| CBAC 检查必须在每次跨系统调用前执行 | 调用延迟增加 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | CBAC 矩阵定义 | 12 系统×12 系统授权关系 |
| 2 | 违规响应 | LOG+ALERT+DENY |
| 3 | 离线更新 | checksum 校验流程 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 | 委托说明 |
|---|--------|---------|---------|
| 1 | 系统内部权限 | 各模块蓝图 | — |
| 2 | Skill 路由实现 | MOD-INF-019 Agent Spec | 本蓝图只定义 CBAC 授权矩阵和 Skill 路由接口契约，具体路由实现（关键词匹配+语义fallback+Progressive Disclosure）委托给 MOD-INF-019 |
| 3 | Skill 渐进加载 | MOD-INF-019 Agent Spec | L1→L2→L3 三层递进加载由 MOD-INF-019 实现 |
| 4 | Skill 生命周期管理 | MOD-INF-019 Agent Spec | 四阶段状态机由 MOD-INF-019 实现 |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | capability_matrix | 授权关系定义 | — | YAML 配置 |
| 2 | capability_check() | 运行时检查 | capability_matrix | 函数调用 |
| 3 | checksum 校验 | 防篡改 | capability_matrix | 启动时校验 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | 跨系统调用请求 | capability_check() | 允许/拒绝 | bool |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| CHECKING | 跨系统调用 | ALLOWED | capability 存在 |
| CHECKING | 跨系统调用 | DENIED | capability 不存在 |

---

## §4 接口契约

### 4.1 公共 API

```python
def capability_check(caller: str, target: str, action: str) -> bool:
    """
    CBAC 能力检查
    输入：caller=调用方系统名, target=目标系统名, action=动作
    输出：True=允许, False=拒绝
    """
```

### 4.2 数据模型

见 §十五 CBAC 能力矩阵 YAML 定义。

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `capability_check()` | `caller` | ✅ | 系统名枚举值 |
| `capability_check()` | `target` | ✅ | 系统名枚举值 |
| `capability_check()` | `action` | ✅ | CT-* 契约定义的动作 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `capability_check()` | `True` | `False` + CRITICAL 日志 |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 capability | ✅ 向后兼容 | 不影响已有调用 |
| 修改 capability | ❌ 破坏性 | 需 Owner 审批 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | implicit_deny | true（最小权限原则） |
| 2 | checksum 校验 | 启动时校验——防运行时篡改 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| capability 条目 | ~18 | ~50 | — | ✅ | 按需扩展 |

### 5.3 迁移/废弃方案

> **时态属性**：临时时态——执行完毕后即成为历史，从蓝图删除。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 | 执行状态 |
|---|-------------|---------|---------|---------|------------|:-------:|
| — | 无 | — | — | — | — | — |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 未授权调用 | capability_check()=False | LOG+ALERT+DENY | 调用被拒绝 |
| 2 | checksum 不一致 | 启动校验 | 拒绝启动+ALERT | 系统不可用 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 运行时篡改 capability_matrix | 高 | checksum 校验 | 启动时校验 |
| 2 | 权限提升 | 高 | implicit_deny + 编排器特权声明 | capability_check() 覆盖率 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | capability_check() | 合法调用→True, 非法调用→False | 100% 通过 |
| 2 | 集成测试 | checksum 校验 | 篡改矩阵→启动拒绝 | 通过 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-MASTER-002 | 必须 | CT-* 契约定义 | — | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_baseline.md` |
| MOD-INF-019 Agent Spec | 必须 | Skill 路由接口 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-spec\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-MASTER_BLUEPRINT` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |

### 10.3 内部依赖图

无内部依赖。

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 否 | 依赖关系简单（2 个依赖） |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖需要验证 |
| 3 | 临时时态内容自动清理 | 否 | 无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 否 | 施工已完成 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具 | 缺口 |
|---|---------|---------|---------|------|
| 1 | 依赖对齐自动验证 | CI 门禁 | validate_path_alignment.py | 无 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖对齐自动验证 | CI pipeline | PR 提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| CBAC 实现 | `D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py` | capability_check()（MOD-GATE_ENGINE 所有） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| gates/circuit_breaker.py | 函数调用 | capability_check() | 单元测试 |
| baseline §二 | 契约引用 | CT-* 契约编号 | 条目存在 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | blueprint_baseline.md | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_baseline.md` | CT-* 契约变更时同步 | CBAC 矩阵基于 CT-* |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 新增 CT-* 忘记更新 CBAC | 中 | 高 | CI 校验 checksum | 风险 |

---

## §0 代码对齐验证

### 代码文件清单

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | gates/circuit_breaker.py | §十五 | CBAC capability_check() | 已实现 |

### 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| capability_check() 存在 | Grep `def capability_check` in `gates/circuit_breaker.py` | ✅ |
| CBAC 矩阵 checksum 校验 | 运行 `gates/circuit_breaker.py` 自检 | ☐ |

### 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.1.0 | CBAC 矩阵 + capability_check() | gates/circuit_breaker.py（MOD-GATE_ENGINE 所有） | 外部实现 |

---

## §16 施工指引

### AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取基线蓝图 §二 契约总表 | 逐条确认 | ☐ |
| 2 | 已读取本蓝图 §十五 CBAC 矩阵 | 逐条确认 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 1 个 Phase |
| 施工模式 | 渐进式 |
| 核心风险 | CBAC 矩阵不完整 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-MASTER-002 §二 | hard | completed | ✅ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于临时时态——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：实现 capability_check()

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 capability_check() |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py` |
| 验收标准 | 合法调用→True, 非法调用→False |
| 验证命令 | `python -m pytest tests/ -k capability -v` |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | capability_check() 失败 | git checkout -- 恢复 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | capability_check() | `D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py` | ✅ | ✅ | ✅ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者 |
| verification_status | verified | 审计者 |
| code_alignment_verified | yes | 审计者 |

---

## §17 容量升级附录

### 17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| capability 条目数 | ~18 | 统计 capability_matrix entries |

### 17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.1.0 | 1 | 基线 | CBAC 矩阵定义 | ✅ |

---

## §18 决策记录

> **时态属性**：永久时态——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> **本节覆盖原 §7 备选方案**——"选项"列已包含备选方案信息。
> **本节覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-CBAC-01 | CBAC 而非 RBAC | A:CBAC/B:RBAC | A | 系统间细粒度授权需要 capability 级别控制 | 2026-05-03 |
| 2 | D-CBAC-02 | implicit_deny=true | A:true/B:false | A | 最小权限原则 | 2026-05-03 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | CBAC 矩阵变更必须同步 checksum | 运行时篡改检测失效 |
| 2 | 新增 CT-* 契约必须更新 capability_matrix | 未授权调用 |
| 3 | 编排器特权不可扩展 | 权限提升 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容一旦执行完毕即成为历史 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | AI 不知道该读哪个蓝图 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义。本蓝图是 MOD-MASTER_BLUEPRINT 拆分后的子蓝图（agent-spec），独立管理 CBAC 矩阵和 Skill 路由——拆分判定基于独立能力域。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？

STEP 2: 职责域判定
  ├ 职责相同 → 原地升级（§17 容量升级附录增量记录）
  └ 职责不同 → 拆分独立蓝图（独立 frontmatter + 概述 + §0~§18）

STEP 3: 拆分后验证
  - 独立 frontmatter + 概述 + §0~§18
  - belongs_to = MOD-MASTER_BLUEPRINT
  - blueprint_registry.yaml 同步更新
```

### MOD-MASTER_BLUEPRINT 拆分实例

| 子蓝图 | 触发条件 | 判定理由 |
|--------|---------|---------|
| blueprint_agent_spec.md | CBAC 矩阵 + Skill 路由 | 独立能力域——跨系统访问控制 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 基线蓝图 | MOD-MASTER-002 | v1.3.0 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_baseline.md` | CT-* 契约定义 |
| 2 | Agent Spec 蓝图 | MOD-INF-019 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-spec\blueprint.md` | Skill 路由 |
| 3 | circuit_breaker.py | MOD-GATE_ENGINE | — | `D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py` | CBAC 实现（MOD-GATE_ENGINE 所有） |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| — | 无 | — | — | — |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | gates/circuit_breaker.py | `D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py` | CBAC 实现（MOD-GATE_ENGINE 所有） | 无变更 |

---

## 蓝图特有章节

### §十五 CBAC 能力访问控制矩阵

#### 15.1 能力矩阵（Capability Matrix）

```yaml
contract: CT-CBAC-001
title: "跨系统能力访问控制矩阵"
principle: "最小权限原则 (Least Privilege) → 每个系统仅拥有执行其 CT-* 合同所需的 capabilities"

capability_matrix:
  entries:
    - {caller: orchestrator, target: context_engine, actions: [build_context, inject_context], auth: cbac_token}
    - {caller: orchestrator, target: gates, actions: [check_gate], auth: cbac_token}
    - {caller: orchestrator, target: pipeline, actions: [route_task], auth: cbac_token}
    - {caller: orchestrator, target: vector_memory, actions: [write_output_vectors], auth: cbac_token}
    - {caller: orchestrator, target: database, actions: [write_task_repo, read_task_repo], auth: cbac_token}
    - {caller: orchestrator, target: feedback_loop_engine, actions: [receive_dispatch], auth: cbac_token}
    - {caller: script_system, target: gates, actions: [emit_exit_code], auth: cbac_token}
    - {caller: script_system, target: orchestrator, actions: [emit_finding], auth: cbac_token}
    - {caller: script_system, target: knowledge_base, actions: [emit_ke_draft], auth: cbac_token}
    - {caller: context_engine, target: vector_memory, actions: [search_vectors], auth: cbac_token}
    - {caller: context_engine, target: knowledge_base, actions: [resolve_ke_by_id], auth: cbac_token}
    - {caller: context_engine, target: llm_security_gate, actions: [validate_context], auth: cbac_token}
    - {caller: knowledge_base, target: vector_memory, actions: [store_embeddings], auth: cbac_token}
    - {caller: knowledge_base, target: database, actions: [read_ke_repo, write_ke_repo], auth: cbac_token}
    - {caller: feedback_loop_engine, target: database, actions: [write_metrics, read_metrics], auth: cbac_token}
    - {caller: feedback_loop_engine, target: orchestrator, actions: [dispatch_action], auth: cbac_token}
    - {caller: feedback_loop_engine, target: gates, actions: [adjust_threshold], auth: cbac_token_signed}
    - {caller: telemetry, target: database, actions: [write_metrics_repo], auth: cbac_token}

  implicit_deny: true

  check_sum: >
    启动时遍历 capability_matrix 所有条目，
    计算 checksum → 运行时每次 capability_check() 校验 checksum 一致性。
    不一致 → ALERT + 拒绝调用（防运行时篡改）。
```

#### 15.2 违规响应

```yaml
unauthorized_access_response:
  action: "LOG + ALERT + DENY"
  log_level: "CRITICAL"
  notify: "Owner（飞书）"
  record: "写入 audit_log 表"
  retry_forbidden: true
```

#### 15.3 离线更新流程 (Offline Update T)

```yaml
cbac_update_flow:
  trigger: "新增/修改 CT-* 契约 → 相应 capability 变更"
  steps:
    - "Owner 修改 capability_matrix YAML"
    - "重新计算 checksum → 写入 capability_registry"
    - "CI 校验 checksum 一致性 → PASS → 合并"
    - "所有系统重启后读取新 checksum"
  rollback: "保留上一版本 checksum → 启动时支持 hot-reload 回退"
```

#### 15.4 编排器特权声明

Orc 是唯一能够"跨系统编排"的系统——但特权仅限于 CT-* 合同定义的动作：
- 不能直接调用 LSG（必须通过 CE）
- 不能直接调用 Script System（必须通过 Gates）
- 不能修改 Gate Engine 阈值（仅 FLE 可以，且需 calibrated token）
- 不能绕过 pre-commit 门禁（GATE-18）

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| CBAC 能力矩阵 | **本文档 §十五** | — |
| CT-* 契约定义 | MOD-MASTER-002 §二 | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | circuit_breaker.py | capability_matrix + capability_check() |
| Tier 1 | MOD-MASTER-002 | CT-CBAC-001 契约 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| CBAC 矩阵变更 | 通知 baseline §二 | 更新 checksum |
| 新增 CT-* 契约 | 更新 capability_matrix | 更新 circuit_breaker.py |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 新增 capability | AI 可自主 |
| 修改已有 capability | 需 Owner 审批 + 通知所有消费者 |
| 删除 capability | 需 Owner 审批 + 确认无消费者 |

### 负向责任

| # | 本蓝图不涉及 | 由谁负责 |
|---|-------------|---------|
| 1 | CT-* 契约定义 | MOD-MASTER-002 §二 负责 |
| 2 | 具体的模块实现代码 | 各模块蓝图 (MOD-INF-*) 负责 |

### 触发条件

| 场景 | AI 应读取本蓝图 |
|------|---------------|
| 跨系统调用开发前 | 读 §十五 CBAC 矩阵 |
| CBAC 矩阵变更时 | 读 §十五 + checksum 更新流程 |
| checksum 不一致告警 | 读 §十五 离线更新流程 + §6 错误处理 |

### 导航路径

| 步骤 | 操作 |
|:---:|------|
| 1 | 读 MOD-MASTER-002 §二 CT-* 契约定义 |
| 2 | 读本蓝图 §十五 CBAC 能力矩阵 |
| 3 | 读 circuit_breaker.py 实现 |

### 漂移防护

| 修改本文件 | 必须同步更新 |
|-----------|------------|
| CBAC 矩阵变更 | checksum + MOD-MASTER-002 §二 |
| 新增 CT-* 契约 | capability_matrix |
| construction_progress 变更 | blueprint_registry.yaml |

---
