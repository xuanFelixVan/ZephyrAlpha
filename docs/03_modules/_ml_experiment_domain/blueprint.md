---
module_id: MOD-ML_EXPERIMENT_DOMAIN
title: "ML-Experiment Domain 蓝图 — L11平台→L13实验跨层集成"
doc_type: blueprint
status: Active
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
actual_disk_path: "D:\\ZephyrAlpha\\src\\zephyr\\ml_train\\ + D:\\ZephyrAlpha\\src\\zephyr\\simulation\\"
template_for: blueprint
generation: 2
functional_domain: ml_experiment
parent_module: "SYS-MASTER-001"
belongs_to: "SYS-MASTER-001"
rule_form: structural
scope: domain
stability: evolving
verifiability: manual
priority: P2
summary: "ML实验域（L11+L13）Level 1集成蓝图——定义ML平台(MOD-ML-001)到实验管线(MOD-EXP-001)的模型生命周期、AB测试链路、特征存储读写和实验元数据追踪。"
codification_level: L1
codification_at: "2026-05-14"
submodule_path: src/zephyr/
submodule_paths_scope: ml-experiment-domain
submodule_paths_extra:
  - src/zephyr/ml_train/
  - src/zephyr/simulation/
ssot_yaml: "architecture_model/layers/l11_ml_platform.yaml + l13_experimentation.yaml"
depends_on:
  - target: "SYS-MASTER-001"
    at: "§七十八~§八十四"
    why: "系统总蓝图——ML-Experiment域是金字塔Level 1节点"
  - target: "MOD-ML-001"
    at: "全篇"
    why: "L11 ML平台模块蓝图"
  - target: "MOD-EXP-001"
    at: "全篇"
    why: "L13 实验管线模块蓝图"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    section: "§七十八~§八十四"
    why: "系统总蓝图ML-Experiment域章节"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md"
    section: "全篇"
    why: "蓝图模板v3.5/v3.6"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml"
    section: "全篇"
    why: "压缩工作流标准"
tags:
  - ml-experiment-domain
  - l11
  - l13
  - ml-platform
  - experimentation
  - domain-integration
---

# ML-Experiment Domain 蓝图 — L11平台→L13实验跨层集成

> module_id: ML-EXPERIMENT-DOMAIN-001 | version: 0.4.0 | status: active | layer: cross_layer | blueprint_level: domain
> actual_disk_path: D:\ZephyrAlpha\src\zephyr\ml_train\ + D:\ZephyrAlpha\src\zephyr\simulation\ | generation: 2 | construction_progress: partially_implemented

## 概述

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[system-dependency-map.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/system-dependency-map.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

## 模板章节映射表

| 模板必需章节 | 本文件对应章节 | 状态 |
|------------|-------------|:---:|
| §1 设计背景与目标 | §1 设计背景与目标 | ✅ |
| §2 模块边界 | §2 模块边界 | ✅ |
| §3 架构设计 | §3 架构设计 | ✅ |
| §4 接口契约 | §4 接口契约 | ✅ |
| §5 约束条件 | §5 约束条件 | ✅ |
| §6 错误处理 | §6 错误处理 | ✅ |
| §7 备选方案 | 已删除→§18决策记录覆盖 | v3.6删除 |
| §8 安全考量 | §8 安全考量 | ✅ |
| §9 测试策略 | §9 测试策略 | ✅ |
| §10 依赖关系 | §10 依赖关系 | ✅ |
| §11 产出物 | §11 产出物存放目录 | ✅ |
| §12 集成目标 | §12 集成目标 | ✅ |
| §13 需要更新 | §13 需要更新 | ✅ |
| §14 风险 | §14 风险 | ✅ |
| §15 后果 | 已删除→正面在§1，负面在§14 | v3.6删除 |
| §0 代码对齐 | §0 代码对齐验证 | ✅ |
| §16 施工指引 | §16 施工指引 | ✅ |
| §17 容量升级 | §17 容量升级附录 | ✅ |
| §18 决策记录 | §18 决策记录 | ✅ |
| 治理信息 | 见文件末尾 | ✅ |

---

## §0 分派表

| 维度 | 值 |
|------|-----|
| module_id | ML-EXPERIMENT-DOMAIN-001 |
| actual_disk_path | `D:\ZephyrAlpha\src\zephyr\ml_train\` + `D:\ZephyrAlpha\src\zephyr\simulation\` |
| 施工程度 | 部分实现（L11/L13模块骨架已就位，跨层管道未施工） |
| ssot_yaml | `D:\ZephyrAlpha\architecture_model\layers\l11_ml_platform.yaml` + `l13_experimentation.yaml` |
| blueprint_level | domain |
| priority | P2 |

## §1 设计背景与目标

### 1.1 背景

L11 ML 平台和 L13 实验管线是 ZephyrAlpha 量化策略的模型验证链路。模型训练→实验验证的跨层数据流需要统一的集成协议，防止模型上线未经充分验证。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 定义 L11→L13 完整模型生命周期 | 6 条 ME-CT-* 契约完整 |
| 2 | Pipeline Gate 覆盖所有关键节点 | 7 个 Gate 节点通过 |
| 3 | 实验元数据可追踪 | experiment tracking DB 覆盖率 100% |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | L11/L13 模块内部设计 | 各模块蓝图负责 |
| 2 | 生产部署逻辑 | 部署系统蓝图负责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 模型训练 MUST 在 4h 内完成 | 资源占用时间限制 |
| AB 测试 MUST 通过 G13.1~G13.3 | 未验证模型不可上线 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 模型生命周期定义 | L11→L13 数据流拓扑 |
| 2 | 跨层接口契约 | ME-CT-* 契约定义 |
| 3 | Pipeline Gate | G11.1~G13.3 节点定义 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 训练逻辑 | MOD-ML-001 |
| 2 | 实验执行逻辑 | MOD-EXP-001 |
| 3 | 生产部署 | 部署系统蓝图 |

---

## §3 架构设计

### 3.1 模型生命周期 Pipeline

Feature Store (VMS/KB) → ML Core (L11) → Experiment Pipeline (L13)。子组件见 §4 契约表 ME-CT-*。

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | VMS/KB 特征存储 | 特征读取 | L11 ML Core | ChromaDB vectors |
| 2 | L11 ML Core | 检查点导出 | L13 Experiment Pipeline | MODEL_CHECKPOINTS |
| 3 | L13 Experiment Pipeline | 实验结果 | 生产部署系统 | ExperimentArtifact |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| TRAINING | 训练收敛 | VALIDATED | G11.2+G11.3 通过 |
| VALIDATED | Sanity Check 通过 | CHECKPOINTED | G11.4 通过 |
| CHECKPOINTED | AB 测试启动 | AB_TESTING | G13.1 通过 |
| AB_TESTING | 评估显著 | PROD_READY | G13.2+G13.3 通过 |

---

## §4 接口契约

| 契约ID | 方向 | 描述 | 状态 | CT引用 |
|---------|------|------|:---:|------|
| ME-CT-FEATURE-001 | VMS/KB→L11 | 特征向量读取（ChromaDB collections: factor-signals, model-features） | Draft | MOD-INF-011 |
| ME-CT-TRAIN-001 | L11 internal | 训练Pipeline Gate：数据→训练→验证→Sanity→发布 | Draft | — |
| ME-CT-CHECKPOINT-001 | L11→L13 | 检查点导入（MODEL_CHECKPOINTS→AB/Backtest Experiment） | Draft | MOD-DATABASE |
| ME-CT-AB-001 | L13 internal | AB实验全流程：config→traffic_split→gate[eval]→analyst→deploy/rollback | Draft | — |
| ME-CT-BACKTEST-001 | L13 internal | 回测实验：ckpt→historical→PnL→Attribution→Report | Draft | — |
| ME-CT-SHADOW-001 | L13 | Shadow Mode：旁路预测→threshold→divergence alert→正式切流 | Draft | — |

### 4.1 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| ME-CT-CHECKPOINT-001 | model_id | ✅ | 唯一标识 |
| ME-CT-CHECKPOINT-001 | checkpoint_path | ✅ | 绝对路径 |
| ME-CT-CHECKPOINT-001 | metrics | ✅ | Dict[str, float] |

### 4.2 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| ME-CT-AB-001 | AB 实验结论 | ERROR + 回滚 |

### 4.3 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 Gate 节点 | ✅ 向后兼容 | 不影响已有流程 |
| 修改 Gate 通过条件 | ❌ 破坏性 | 需 Owner 审批 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 模型训练超时 | 4h |
| 2 | AB 测试流量分配上限 | ≤1% |
| 3 | 检查点必须包含 provenance | 必填 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 并行训练任务 | 1 | 5 | — | ✅ | GPU 调度 |
| 并行实验 | 1 | 10 | — | ✅ | 实验队列 |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。

无迁移需求。

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Model Pipeline Timeout | 超时检测 | kill + Checkpoint 保留 | 训练中断 |
| 2 | AB Test 无预算 | Budget Enforcer(INF-024) | 自动拒绝 | 实验无法启动 |
| 3 | Checkpoint Corruption | Audit Provenance(INF-020) | Rollback(INF-021) | Shadow→Prod 切流失败 |
| 4 | AB 统计不显著 | Bayesian 戳 + Sequential Testing | 继续观察 | 噪声误判 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 未验证模型上线 | 交易损失 | Pipeline Gate 强制 | G11.1~G13.3 全通过 |
| 2 | 检查点篡改 | 模型行为异常 | Audit Provenance + checksum | 校验通过率 100% |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | ME-CT-CHECKPOINT-001 | 检查点格式校验 | schema 匹配 |
| 2 | 集成测试 | L11→L13 管道 | 训练→实验端到端 | 实验结果合理 |
| 3 | 回归测试 | 全链路 | 已有模型不退化 | 0 failure |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| SYS-MASTER-001 | 必须 | 系统总蓝图 §七十八~§八十四 | — | `D:\ZephyrAlpha\docs\03_modules\_sys-master\blueprint.md` |
| MOD-ML-001 | 必须 | L11 ML 平台核心 | — | `D:\ZephyrAlpha\docs\03_modules\_domain-ml_train\ml-platform-core\blueprint.md` |
| MOD-EXP-001 | 必须 | L13 实验管线核心 | — | `D:\ZephyrAlpha\docs\03_modules\_domain-simulation\experimentation-core\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint ML-EXPERIMENT-DOMAIN-001` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

无内部依赖。

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 否 | 依赖数量少，手动维护 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖 |
| 3 | 临时时态内容自动清理 | 否 | 无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 2 | 施工步骤完成度自动检测 | pytest+ruff | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 2 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| L11 ML 平台核心 | `D:\ZephyrAlpha\src\zephyr\ml_train\` | 训练+验证+检查点 |
| L13 实验管线核心 | `D:\ZephyrAlpha\src\zephyr\simulation\` | AB测试+回测+Shadow |
| 域集成文档 | `D:\ZephyrAlpha\docs\03_modules\_ml-experiment-domain\blueprint.md` | 本文件 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| L11 ML Platform Core | 检查点传递 | ME-CT-CHECKPOINT-001 | schema 校验 |
| L13 Experiment Pipeline | 实验配置 | ME-CT-AB-001/BACKTEST-001 | 实验结果校验 |
| INF-012 Database | SQL | MODEL_CHECKPOINTS 表 | 表存在 |

### 12.1 域契约锚点（条件可选）

> 条件可选：仅当本模块有域治理集成契约时填写。本蓝图 belongs_to = SYS-MASTER-001，不涉及 DOM-GOV-XXX 契约。不适用。

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | l11_ml_platform.yaml | `D:\ZephyrAlpha\architecture_model\layers\l11_ml_platform.yaml` | 新模型类型注册 | 模型白名单 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | Pipeline Gate 条件过严 | 中 | 中 | Shadow Mode 兜底 | 风险 |
| 2 | 检查点格式不兼容 | 低 | 高 | 契约版本控制 | 风险 |
| 3 | 跨层契约变更需同步更新两个模块蓝图 | — | 中 | 契约版本控制+变更通知 | 负面后果 |
| 4 | Pipeline Gate 可能延迟模型上线 | — | 中 | Shadow Mode 兜底 | 负面后果 |

---

## §0 代码对齐验证

### 代码文件清单

> **架构归属SSoT**：PostgreSQL `depgraph` 数据库（`get_depgraph_pg_connection()`）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules ML-EXPERIMENT-DOMAIN-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | ml_train/ | §3 | ML平台核心 | 已实现 | — |
| 2 | simulation/ | §3 | 实验管线核心 | 已实现 | — |
| 3 | ME-CT-CHECKPOINT-001 管道 | §4 | 跨层数据流 | 未实现 | — |
| 4 | ME-CT-FEATURE-001 特征读取 | §4 | 特征向量 | 未实现 | — |

### 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| L11 __init__.py 存在 | Grep `ml_train` | ☐ |
| L13 __init__.py 存在 | Grep `simulation` | ☐ |
| ME-CT-CHECKPOINT-001 管道实现 | Grep `ME-CT-CHECKPOINT-001` | ☐ |

### 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.4.0 | L11/L13 模块骨架 | 跨层管道 | 待基建域就绪 |

---

## §16 施工指引

### AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取 L11/L13 模块蓝图 | 逐条确认 | ☐ |
| 2 | 已读取本蓝图 §二 契约表 | 逐条确认 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 渐进式 |
| 核心风险 | Pipeline Gate 条件不兼容 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | L11 ML Platform Core 骨架 | hard | phase_1_partial | ⚠️ |
| 2 | L13 Experimentation Core 骨架 | hard | phase_1_partial | ⚠️ |
| 3 | INF-012 Database | hard | completed | ✅ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：实现 ME-CT-CHECKPOINT-001 管道

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 ME-CT-CHECKPOINT-001 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ml_train\checkpoint_pipeline.py` |
| 验收标准 | 检查点格式校验通过 |
| 验证命令 | `python -m pytest tests/ -k ml_experiment -v` |

#### 步骤 2：实现 ME-CT-AB-001 管道

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 ME-CT-AB-001 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\simulation\ab_pipeline.py` |
| 验收标准 | AB 实验流程校验通过 |
| 验证命令 | `python -m pytest tests/ -k ml_experiment -v` |

#### 步骤 3：端到端集成测试

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 测试策略 |
| 产出位置 | `D:\ZephyrAlpha\tests\test_ml_experiment_integration.py` |
| 验收标准 | 训练→实验端到端通过 |
| 验证命令 | `python -m pytest tests/test_ml_experiment_integration.py -v` |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 管道 schema 不兼容 | 修改 ME-CT-* 契约定义 |
| 2 | 集成测试失败 | 回退到模块独立运行 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | ME-CT-CHECKPOINT-001 管道 | `D:\ZephyrAlpha\src\zephyr\ml_train\checkpoint_pipeline.py` | ☐ | ☐ | ☐ |
| 2 | ME-CT-AB-001 管道 | `D:\ZephyrAlpha\src\zephyr\simulation\ab_pipeline.py` | ☐ | ☐ | ☐ |
| 3 | 集成测试 | `D:\ZephyrAlpha\tests\test_ml_experiment_integration.py` | ☐ | ☐ | ☐ |

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
| 并行训练任务 | 1 | 统计 GPU 调度队列 |
| 并行实验 | 1 | 统计 experiment tracking DB |

### 17.2 缺口分析

generation=2，跨层管道未施工为主要缺口。

### 17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.2.0 | 1 | 基线 | 跨层契约定义 | ☐ |
| v0.3.0 | 2 | 模板对齐 | v3.3 模板升级 | ☐ |
| v0.4.0 | 2 | 模板升级 | v3.5/v3.6 模板升级 | ☐ |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> 本节同时覆盖原 §7 备选方案——§18 的"选项"列已包含备选方案信息，无需独立章节。
> 本节同时覆盖原 §15 后果——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-ME-01 | Pipeline Gate 强制 | A:强制/B:建议 | A | 未验证模型不可上线 | 2026-05-06 |
| 2 | D-ME-02 | Shadow Mode 作为上线前必经步骤 | A:必经/B:可选 | A | 防止模型行为异常 | 2026-05-06 |

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
| 7 | 涉及文件范围必须明确列出 | 范围漂移——改了不该改的文件 |
| 8 | 容量估算必须写 | 容量瓶颈——上线后发现不够用 |
| 9 | 迁移/废弃方案必须写 | 断链或垃圾积累 |
| 10 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移——AI 自行决定 |
| 11 | 蓝图必须自包含 | 信息缺失——AI 缺少关键上下文 |
| 12 | 删除文件必须遵守安全删除协议 | 永久丢失——无法恢复 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

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

### 本蓝图拆分判定

本蓝图当前 ~500 行，未超过 ~800 行阈值。职责域单一（ML实验域跨层集成）。**不拆分**。

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。ML-Experiment 域为纯新增设计。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | 系统总蓝图 | SYS-MASTER-001 | 当前版本 | `D:\ZephyrAlpha\docs\03_modules\_sys-master\blueprint.md` | 系统拓扑 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | ALPHA-SIGNAL-DOMAIN-001 | `D:\ZephyrAlpha\docs\03_modules\_alpha-signal-domain\blueprint.md` | 域集成模式 | Alpha-Signal 定义因子域集成，本蓝图定义ML实验域集成 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 域集成蓝图 | `D:\ZephyrAlpha\docs\03_modules\_ml-experiment-domain\blueprint.md` | 修改 | 本文件 |
| 2 | L11 ML 平台 | `D:\ZephyrAlpha\src\zephyr\ml_train\` | 读取 | 代码对齐 |
| 3 | L13 实验管线 | `D:\ZephyrAlpha\src\zephyr\simulation\` | 读取 | 代码对齐 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| ML-Experiment 域集成契约 ME-CT-* | **本文档 §4** | — |
| L11 ML 平台内部设计 | MOD-ML-001 | — |
| L13 实验管线内部设计 | MOD-EXP-001 | — |

**任何与本蓝图冲突的跨层定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-ML-001 | ME-CT-TRAIN-001/CHECKPOINT-001 |
| Tier 1 | MOD-EXP-001 | ME-CT-CHECKPOINT-001/AB-001/BACKTEST-001/SHADOW-001 |
| Tier 2 | 生产部署系统 | ME-CT-AB-001 实验结论 |

### 变更同步规则

| 变更类型 | Tier 1（下游模块） | Tier 2（集成系统） |
|---------|------------------|------------------|
| ME-CT-* 契约变更 | 通知所有签约方 | 更新 circuit_breaker.py |
| Pipeline Gate 条件变更 | 更新训练/实验流程 | 更新监控告警 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| ME-CT-* 契约新增 | AI 可自主 |
| ME-CT-* 契约修改 | 需 Owner 审批 + 通知所有签约方 |
| Pipeline Gate 条件变更 | 需 Owner 审批 |
