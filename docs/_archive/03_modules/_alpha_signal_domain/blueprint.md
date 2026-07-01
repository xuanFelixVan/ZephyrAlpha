---
module_id: MOD-ALPHA_SIGNAL_DOMAIN
title: "Alpha-Signal Domain 蓝图 — L02因子→L03信号跨层集成"
doc_type: blueprint
status: Deprecated
version: "0.4.0"
layer: cross_layer
layer_name: cross_layer
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
ttl: permanent
last_updated: "2026-05-15"
last_verified: "2026-05-14"
construction_progress: partially_implemented
actual_disk_path: "D:\\ZephyrAlpha\\src\\zephyr\\factor\\ + D:\\ZephyrAlpha\\src\\zephyr\\signal_ashare\\ + D:\\ZephyrAlpha\\src\\zephyr\\signal_fundamental\\ + D:\\ZephyrAlpha\\src\\zephyr\\signal_quality\\"
template_for: blueprint
generation: 2
functional_domain: alpha_signal
parent_module: "SYS-MASTER-001"
belongs_to: "SYS-MASTER-001"
rule_form: structural
scope: domain
stability: evolving
verifiability: manual
priority: P1
activation_phase: delete
summary: "Alpha因子域（L02+L03）Level 1集成蓝图——定义Alpha因子核心(MOD-AF-001)到信号生成核心(MOD-SIG-001)的数据流、接口契约、共享数据模型和施工门禁。"
codification_level: L1
codification_at: "2026-05-14"
submodule_path: src/zephyr/
submodule_paths_scope: alpha_signal_domain
submodule_paths_extra:
  - src/zephyr/factor/
  - src/zephyr/signal/
ssot_yaml: "docs/03_modules/_alpha_signal_domain/blueprint.md"
depends_on:
  - target: "SYS-MASTER-001"
    at: "§53~§57"
    why: "系统总蓝图——Alpha-Signal域是金字塔Level 1节点"
  - target: "MOD-AF-001"
    at: "全篇"
    why: "L02 Alpha因子核心模块蓝图"
  - target: "MOD-SIG-001"
    at: "全篇"
    why: "L03 信号生成核心模块蓝图"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_system_master\\blueprint.md"
    section: "§53~§57"
    why: "系统总蓝图Alpha-Signal域章节"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md"
    section: "全篇"
    why: "蓝图模板v3.5/v3.6"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml"
    section: "全篇"
    why: "压缩工作流标准"
tags:
  - alpha_signal_domain
  - l02
  - l03
  - alpha-factor
  - signal-generation
  - domain-integration
---

# Alpha-Signal Domain 蓝图 — L02因子→L03信号跨层集成

> module_id: alpha_signal_domain-001 | version: 0.4.0 | status: deprecated | layer: cross_layer | blueprint_level: domain
> actual_disk_path: D:\ZephyrAlpha\src\zephyr\factor\ + D:\ZephyrAlpha\src\zephyr\signal_ashare\ + D:\ZephyrAlpha\src\zephyr\signal_fundamental\ + D:\ZephyrAlpha\src\zephyr\signal_quality\ | generation: 2 | construction_progress: partially_implemented

## 概述

本蓝图是 Alpha-Signal 因子域的 Level 1 集成蓝图。核心职责：定义 L02 Alpha 因子核心到 L03 信号生成核心的完整数据流拓扑、跨层接口契约（AS-CT-*）、共享数据模型和施工门禁。不重复 L02/L03 模块内部规范，只定义跨层集成协议。上游依赖 SYS-MASTER-001 §53~§57 和 L00 数据源，下游被 L04 风控引擎消费。当前 L02/L03 模块骨架已就位，跨层管道未施工。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[system-dependency-map.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/system-dependency-map.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

## 模板章节映射表

> 本文件按域内逻辑组织（§0~§五），以下映射表说明与蓝图模板 v3.5/v3.6 必需章节的对应关系。

| 模板必需章节 | 本文件对应章节 | 状态 |
|------------|-------------|:---:|
| §1 设计背景与目标 | §一 跨层数据流拓扑 | ✅ |
| §2 模块边界 | §0 分派表 | ✅ |
| §3 架构设计 | §一 跨层数据流拓扑 | ✅ |
| §4 接口契约 | §二 跨层接口契约 | ✅ |
| §5 约束条件 | §三 施工门禁 | ✅ |
| §6 错误处理 | §四 故障模式 | ✅ |
| §8 安全考量 | — | 缺失 |
| §9 测试策略 | — | 缺失 |
| §10 依赖关系 | frontmatter depends_on | ✅ |
| §11 产出物 | §0 分派表 actual_disk_path | ✅ |
| §12 集成目标 | §一 数据流拓扑 | ✅ |
| §13 需要更新 | §三 施工门禁 | ✅ |
| §14 风险 | §四 故障模式 | ✅ |
| §0 代码对齐 | §五 施工程度标注 | ✅ |
| §16 施工指引 | §三 施工门禁 | ✅ |
| §17 容量升级 | — | 缺失 |
| §18 决策记录 | — | 缺失 |
| 治理信息 | 见文件末尾 | ✅ |
| §7 备选方案 | 已删除→§18决策记录覆盖 | v3.6删除 |
| §15 后果 | 已删除→正面在§1，负面在§14 | v3.6删除 |

---

## §0 分派表

| 维度 | 值 |
|------|-----|
| module_id | alpha_signal_domain-001 |
| actual_disk_path | `D:\ZephyrAlpha\src\zephyr\factor\` + `D:\ZephyrAlpha\src\zephyr\signal\` |
| 施工程度 | 部分实现（L02/L03模块骨架已就位，跨层管道未施工） |
| ssot_yaml | `D:\ZephyrAlpha\docs\03_modules\_alpha_signal_domain\blueprint.md` |
| blueprint_level | domain |
| priority | P1 |

## §1 设计背景与目标

### 1.1 背景

L02 Alpha 因子计算和 L03 信号生成是 ZephyrAlpha 量化策略的核心链路。因子→信号的跨层数据流需要统一的集成协议，防止接口不一致和重复实现。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 定义 L02→L03 完整数据流拓扑 | 5 条 AS-CT-* 契约完整 |
| 2 | 跨层管道可运行 | 因子→信号端到端集成测试通过 |
| 3 | 因子→信号链路变更可控 | G6 蓝图合规门禁覆盖 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | L02/L03 模块内部设计 | 各模块蓝图负责 |
| 2 | L04 风控逻辑 | L04 模块蓝图负责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 因子计算 MUST 在 L00 数据到达后 60s 内完成 | 延迟影响信号时效性 |
| 信号合成 MUST 在因子到达后 30s 内完成 | 延迟影响交易执行 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 跨层数据流定义 | L02→L03 数据流拓扑 |
| 2 | 跨层接口契约 | AS-CT-* 契约定义 |
| 3 | 施工门禁 | G0/G6 门禁规则 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 因子计算逻辑 | MOD-AF-001 |
| 2 | 信号合成逻辑 | MOD-SIG-001 |
| 3 | 风控逻辑 | L04 模块蓝图 |

---

## §3 架构设计

### 3.1 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | L00 Market Data | 因子计算 | L02 Alpha Factor Core | OHLCV/orderbook/tick |
| 2 | L02 Alpha Factor Core | 因子→信号合成 | L03 Signal Generation Core | MultiIndex DataFrame |
| 3 | L03 Signal Generation Core | 信号评估+发送 | L04 Risk Management | Signal DataFrame |

### 3.2 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| DRAFT | 因子计算完成 | COMPUTED | 因子值非空 |
| COMPUTED | 信号合成触发 | SIGNAL_GENERATED | 因子覆盖度 > 80% |
| SIGNAL_GENERATED | 风控通过 | SENT | 风控门禁通过 |

---

## §4 接口契约

| 契约ID | 方向 | 描述 | 状态 | CT引用 |
|---------|------|------|:---:|------|
| AS-CT-DATA-001 | L00→L02 | 市场数据→因子引擎（OHLCV/orderbook/tick） | Draft | — |
| AS-CT-FACTOR-001 | L02→L03 | 因子数据帧（MultiIndex DataFrame: (timestamp, asset)×factor） | Draft | — |
| AS-CT-FACTOR-002 | L02 internal | Code-Dedup-Engine→去重后的因子值（唯一source_key） | Draft | MOD-INF-005 |
| AS-CT-SIGNAL-001 | L03→L04 | 信号数据帧→风控引擎 | Draft | — |
| AS-CT-VMS-001 | L02+L03→VMS | 因子嵌入向量存储（8 collections: signal-embeddings） | Draft | MOD-INF-011 |

### 4.1 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| AS-CT-FACTOR-001 | timestamp | ✅ | ISO 8601 |
| AS-CT-FACTOR-001 | asset | ✅ | 合约代码 |
| AS-CT-FACTOR-001 | factor_values | ✅ | Dict[str, float] |

### 4.2 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| AS-CT-SIGNAL-001 | Signal DataFrame | ERROR + 日志 |

### 4.3 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增因子列 | ✅ 向后兼容 | 不影响已有信号合成 |
| 修改因子列类型 | ❌ 破坏性 | 需 Owner 审批 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 因子计算延迟 | < 60s |
| 2 | 信号合成延迟 | < 30s |
| 3 | 因子去重必须使用 source_hash | — |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 因子数量 | ~10 | ~200 | — | ✅ | 按需扩展 |
| 信号频率 | ~1/min | ~60/min | — | ✅ | 批量合成 |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于临时时态——执行完毕后即成为历史，从蓝图删除。

无迁移需求。

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | L02 crash mid-factor | Checkpoint 校验 | 增量因子刷新 | stale 因子不入 L03 |
| 2 | L03 信号合成参数漂移 | Drift Detector(INF-023) | 告警+人工校准 | 信号质量退化 |
| 3 | Code-Dedup 误删唯一因子 | Audit Trail(INF-020) | source_hash 回溯 | 因子缺失→信号失真 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 因子数据篡改 | 错误信号触发交易 | Audit Trail + source_hash | 校验通过率 100% |
| 2 | 未授权因子注册 | 因子污染 | wt_factor_universe.yaml 白名单 | 注册校验通过 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | AS-CT-FACTOR-001 | 因子 DataFrame 格式校验 | schema 匹配 |
| 2 | 集成测试 | L02→L03 管道 | 因子→信号端到端 | 信号值合理 |
| 3 | 回归测试 | 全链路 | 已有因子不退化 | 0 failure |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| SYS-MASTER-001 | 必须 | 系统总蓝图 §53~§57 | — | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` |
| MOD-AF-001 | 必须 | L02 Alpha 因子核心 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\alpha_factor_core\blueprint.md` |
| MOD-SIG-001 | 必须 | L03 信号生成核心 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_signal\signal_generation_core\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint alpha_signal_domain-001` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 同上 |

### 10.3 内部依赖图

无内部依赖。

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 否 | 跨层蓝图，依赖关系简单 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖 |
| 3 | 临时时态内容自动清理 | 否 | 无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 2 | 施工步骤完成度自动检测 | pytest+ruff | 部分 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 2 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| L02 因子核心 | `D:\ZephyrAlpha\src\zephyr\factor\` | 因子计算+清洗+存储 |
| L03 信号核心 | `D:\ZephyrAlpha\src\zephyr\signal\` | 信号合成+评估+发送 |
| 域集成文档 | `D:\ZephyrAlpha\docs\03_modules\_alpha_signal_domain\blueprint.md` | 本文件 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| L02 Alpha Factor Core | 数据帧传递 | AS-CT-FACTOR-001 | schema 校验 |
| L03 Signal Generation Core | 数据帧传递 | AS-CT-SIGNAL-001 | 信号值校验 |
| INF-012 Database | SQL | ALPHA_FACTORS / SIGNALS 表 | 表存在 |

### 12.1 域契约锚点（条件可选）

本蓝图不涉及 DOM-GOV-XXX 域治理集成契约，不适用。

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | ~~wt_factor_universe.yaml~~ | 已删除（迁移至35域架构） | — | 旧14层架构YAML已废弃 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 跨层管道延迟超标 | 中 | 高 | Checkpoint + 增量刷新 | 风险 |
| 2 | 因子→信号 schema 不兼容 | 低 | 高 | 契约版本控制 | 风险 |
| 3 | 跨层契约变更需同步更新两个模块蓝图 | — | 中 | 变更同步规则（见治理信息） | 负面后果 |

---

## §0 代码对齐验证

### 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules alpha_signal_domain-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | factor/ | §一 | 因子计算核心 | 已实现 | — |
| 2 | signal/ | §一 | 信号生成核心 | 已实现 | — |
| 3 | AS-CT-FACTOR-001 管道 | §四 | 跨层数据流 | 未实现 | 待基建域就绪 |
| 4 | AS-CT-VMS-001 向量存储 | §四 | 因子嵌入 | 未实现 | 待基建域就绪 |

### 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| L02 __init__.py 存在 | Grep `factor` | ☐ |
| L03 __init__.py 存在 | Grep `signal` | ☐ |
| AS-CT-FACTOR-001 管道实现 | Grep `AS-CT-FACTOR-001` | ☐ |

### 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.3.0 | L02/L03 模块骨架 | 跨层管道 | 待基建域就绪 |
| v0.4.0 | L02/L03 模块骨架 | 跨层管道 | 待基建域就绪 |

---

## §16 施工指引

### AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取 L02/L03 模块蓝图 | 逐条确认 | ☐ |
| 2 | 已读取本蓝图 §二 契约表 | 逐条确认 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 渐进式 |
| 核心风险 | 跨层管道 schema 不兼容 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | L02 Alpha Factor Core 骨架 | hard | phase_1_partial | ⚠️ |
| 2 | L03 Signal Generation Core 骨架 | hard | phase_1_partial | ⚠️ |
| 3 | INF-012 Database | hard | completed | ✅ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于临时时态——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：实现 AS-CT-FACTOR-001 管道

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 AS-CT-FACTOR-001 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\factor\pipeline.py` |
| 验收标准 | 因子 DataFrame 格式校验通过 |
| 验证命令 | `python -m pytest tests/ -k alpha_signal -v` |

#### 步骤 2：实现 AS-CT-SIGNAL-001 管道

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 AS-CT-SIGNAL-001 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\signal\pipeline.py` |
| 验收标准 | 信号 DataFrame 格式校验通过 |
| 验证命令 | `python -m pytest tests/ -k alpha_signal -v` |

#### 步骤 3：端到端集成测试

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 测试策略 |
| 产出位置 | `D:\ZephyrAlpha\tests\test_alpha_signal_integration.py` |
| 验收标准 | 因子→信号端到端通过 |
| 验证命令 | `python -m pytest tests/test_alpha_signal_integration.py -v` |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 管道 schema 不兼容 | 修改 AS-CT-* 契约定义 |
| 2 | 集成测试失败 | 回退到模块独立运行 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | AS-CT-FACTOR-001 管道 | `D:\ZephyrAlpha\src\zephyr\factor\pipeline.py` | ☐ | ☐ | ☐ |
| 2 | AS-CT-SIGNAL-001 管道 | `D:\ZephyrAlpha\src\zephyr\signal\pipeline.py` | ☐ | ☐ | ☐ |
| 3 | 集成测试 | `D:\ZephyrAlpha\tests\test_alpha_signal_integration.py` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_implemented | 施工者 |
| verification_status | pending | 审计者 |
| code_alignment_verified | no | 审计者 |

---

## §17 容量升级附录

### 17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 因子数量 | ~10 | 统计 wt_factor_universe.yaml |
| 信号频率 | ~1/min | 统计 SIGNALS 表写入频率 |

### 17.2 缺口分析

generation=2，跨层管道未施工为主要缺口。

### 17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.2.0 | 1 | 基线 | 跨层契约定义 | ☐ |
| v0.3.0 | 2 | 模板对齐 | v3.3 模板升级 | ☐ |
| v0.4.0 | 2 | 模板对齐 | v3.5/v3.6 模板升级 | ☐ |

---

## §18 决策记录

> **时态属性**：决策记录属于永久时态——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> 本节同时覆盖原 §7 备选方案——§18 的"选项"列已包含备选方案信息。
> 本节同时覆盖原 §15 后果——负面后果合并到 §14 风险，正面后果与 §1 目标重复。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-AS-01 | 批处理而非流式因子→信号 | A:批处理/B:流式 | A | 当前因子频率低，批处理足够 | 2026-05-06 |
| 2 | D-AS-02 | MultiIndex DataFrame 作为因子数据格式 | A:DataFrame/B:dict | A | 支持多资产多因子索引 | 2026-05-06 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径 | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 6 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 7 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4） | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 8 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 9 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

---

## 蓝图拆分判定标准

> 铁律 #9 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

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

本蓝图不涉及文件删除。Alpha-Signal 域为纯新增设计。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | 系统总蓝图 | SYS-MASTER-001 | — | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` | 系统拓扑 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | MOD-GOVERNANCE | `D:\ZephyrAlpha\docs\03_modules\_domain_governance\blueprint.md` | 域集成模式 | DOM-GOV 定义治理域集成，本蓝图定义因子域集成 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 域集成蓝图 | `D:\ZephyrAlpha\docs\03_modules\_alpha_signal_domain\blueprint.md` | 修改 | 本文件 |
| 2 | L02 因子核心 | `D:\ZephyrAlpha\src\zephyr\factor\` | 读取 | 代码对齐 |
| 3 | L03 信号核心 | `D:\ZephyrAlpha\src\zephyr\signal\` | 读取 | 代码对齐 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| Alpha-Signal 域集成契约 AS-CT-* | **本文档 §4** | — |
| L02 因子内部设计 | MOD-AF-001 | — |
| L03 信号内部设计 | MOD-SIG-001 | — |

**任何与本蓝图冲突的跨层定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-AF-001 | AS-CT-FACTOR-001/002 |
| Tier 1 | MOD-SIG-001 | AS-CT-FACTOR-001/AS-CT-SIGNAL-001 |
| Tier 2 | L04 Risk Management | AS-CT-SIGNAL-001 |

### 变更同步规则

| 变更类型 | Tier 1（下游模块） | Tier 2（集成系统） |
|---------|------------------|------------------|
| AS-CT-* 契约变更 | 通知所有签约方 | 更新 circuit_breaker.py |
| 因子白名单变更 | 更新因子注册 | 更新监控告警 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| AS-CT-* 契约新增 | AI 可自主 |
| AS-CT-* 契约修改 | 需 Owner 审批 + 通知所有签约方 |
| 因子白名单变更 | 需 Owner 审批 |
