# 四图对齐剩余 7 问题治本方案（ARCH-056 修正）

> **Status**: spec | **Created**: 2026-07-10 | **Author**: AI 架构师
> **Related**: ARCH-056, ARCH-053

## 1. 问题陈述

前一轮修复（8 Task）将四图对齐问题从 35 个降到 7 个（孤儿=0, 状态漂移=4, 域不一致=3, 设计态孤立=0）。剩余 7 个问题需要治本方案。

### 1.1 状态漂移（4个）

| module_id | depgraph | dataflow | decision | blueprint | 漂移原因 |
|---|---|---|---|---|---|
| MOD-L02-001 | prototype | production | prototype | (空) | dataflow 数据产出已 production，depgraph 部分源码仍 prototype；blueprint 缺 design_maturity 字段 |
| MOD-L04-001 | prototype | production | design | (空) | decision 有 76 条真实规划中决策节点(design)；dataflow 数据产出已 production；blueprint 缺字段 |
| MOD-L05-001 | prototype | production | design | (空) | decision 有 73 条真实规划中决策节点(design)；dataflow 数据产出已 production；blueprint 缺字段 |
| MOD-MKT_DATA | prototype | production | prototype | - | depgraph 只有 1 个 __init__.py(prototype)；无蓝图文件 |

### 1.2 域不一致（3个）

| module_id | depgraph 投票域 | blueprint responsibility_domain | 根因 |
|---|---|---|---|
| MOD-GOV-SYNC-PANORAMA | D_GOV_SCRIPTS（3 非测试脚本） | D_GOVERNANCE | 粒度不一致：物理位置=D_GOV_SCRIPTS(脚本子域)，逻辑声明=D_GOVERNANCE(治理总域) |
| MOD-INF-035 | D_TRADING（29 非测试源码在 src/zephyr/trading/） | D_INFRA_RUNTIME | 遗留目录命名错位：源码在 trading/ 目录但实际是运行时基础设施 |
| MOD-INF-039 | D_TRADING（71 非测试源码在 src/zephyr/trading/orchestrator/） | D_INFRA_RUNTIME | 同上；蓝图正文 actual_disk_path 已暗示目标路径为 src/zephyr/orchestrator/ |

## 2. 第一性原理分析

### 2.1 核心矛盾

ARCH-056 裁定"depgraph.nodes 为架构数据真源，单向派生到 dataflow/decision/blueprint"。但调研发现 depgraph 的 `domain_id` 和 `design_maturity` 有本质问题：

**问题 1：domain_id 是路径推导的启发式值**
- depgraph 通过源码文件路径投票推导域（如 `src/zephyr/trading/` → D_TRADING）
- 反映**物理位置**而非**逻辑职责**
- MOD-INF-035（系统大脑）和 MOD-INF-039（Agent 编排引擎）的源码在 `trading/` 目录下，但逻辑上是运行时基础设施
- 以物理位置覆盖逻辑声明是本末倒置

**问题 2：design_maturity 是逐文件评估的保守值**
- depgraph 按源码文件粒度评估，取最 design 状态（min rank）
- 一个模块只要有任一文件是 prototype，整个模块就判为 prototype
- dataflow 评估的是数据产出成熟度（production）
- decision 评估的是决策规划成熟度（design=规划中）
- **四图从不同维度评估同一字段，强制一致会丢失语义**

**问题 3：四图 design_maturity 的语义差异是合理的**
- depgraph=prototype：部分源码文件未到 production（如 `stop_loss_engine.py`）→ 代码成熟度
- dataflow=production：数据产出已在运行（如 `risk.limits` dataset）→ 数据流成熟度
- decision=design：有 76 条真实规划中决策节点（Kill Switch、券商熔断等）→ 决策规划成熟度
- 三者都是各自维度的真实情况，不应强制统一

### 2.2 真源分层

ARCH-056 的"depgraph 为真源"裁定对于**架构数据**（模块存在性、依赖关系、文件路径、node_type）是正确的。但对于 `domain_id` 和 `design_maturity` 这两个**模块级声明字段**，depgraph 不是合适的真源：

| 字段 | 真源 | 派生方向 | 理由 |
|------|------|----------|------|
| module_id | depgraph.nodes | depgraph → 其他图 | 模块存在性是架构数据 |
| 依赖关系 | depgraph.edges | depgraph → 其他图 | 依赖关系是架构数据 |
| **domain_id** | **blueprint frontmatter** | **blueprint → depgraph** | 逻辑职责声明，非物理位置 |
| **design_maturity** | **各图独立评估** | **不强制一致** | 四图维度不同，各有真实语义 |
| build_status | depgraph.nodes | depgraph → 其他图 | 构建状态是架构数据 |

### 2.3 100% AI 开发模式的影响

在 100% AI 开发模式下：
- AI 查询 depgraph 获取模块信息时，会看到路径推导的 domain_id（如 D_TRADING），可能误判模块属于交易域
- AI 查询 align_panoramas 报告时，会看到状态漂移警告，可能误认为数据不一致需要修复
- **正确的认知应该传递给 AI**：domain_id 以 blueprint 为准，design_maturity 各图维度不同是正常的

## 3. 裁定结果

### 裁定 A：状态漂移检测逻辑修正

**裁定**：四图 design_maturity 不再强制一致。各图从不同维度评估同一字段是合理的语义差异。

**检测逻辑变更**：
- 旧逻辑：四图 design_maturity 不完全一致 → 报漂移（WARN）
- 新逻辑：
  1. blueprint 缺 design_maturity 字段 → 报"字段缺失"（WARN，需补齐）
  2. depgraph 内部文件级别 design_maturity 混合（部分 design/部分 production）→ 报"模块未统一成熟度"（INFO）
  3. 四图维度差异（depgraph vs dataflow vs decision）→ 不再报告（正常现象）

### 裁定 B1：MOD-GOV-SYNC-PANORAMA 域修正

**裁定**：改 blueprint 的 responsibility_domain 为 `D_GOV_SCRIPTS`。

**理由**：
- 模块 3 个非测试节点全部是 `node_type=script` 且位于 `scripts/governance/`
- D_GOV_SCRIPTS 是词表合法值（定义："治理脚本域——脚本系统/自动化审计"）
- D_GOVERNANCE 是治理总域，D_GOV_SCRIPTS 是其子域，D_GOV_SCRIPTS 语义更精确
- 改蓝图成本低、零运行时风险

### 裁定 B2：MOD-INF-035/039 域不一致豁免

**裁定**：保留 blueprint 的 `D_INFRA_RUNTIME`（语义正确）。align_panoramas.py 检测逻辑变更——当 depgraph 投票域与 blueprint 域不一致时，以 blueprint 为准（blueprint 是逻辑真源），降级为 INFO。

**理由**：
- MOD-INF-035（系统大脑）和 MOD-INF-039（Agent 编排引擎）逻辑上是运行时基础设施
- 源码在 `src/zephyr/trading/` 是历史遗留目录命名错位
- depgraph 路径投票忠实反映了物理位置，但物理位置不等于逻辑职责
- 以 blueprint 为逻辑真源是正确的

**长期治理**（不在本方案施工范围内，登记为技术债务）：
- MOD-INF-035：将 `src/zephyr/trading/` 下属本模块的 29 个文件迁至 `src/zephyr/runtime/` 或 `src/zephyr/infrastructure/`
- MOD-INF-039：将 `src/zephyr/trading/orchestrator/` 迁至 `src/zephyr/orchestrator/`（蓝图正文 actual_disk_path 已暗示此目标路径）
- 迁移后 depgraph 路径投票将自然收敛到 D_INFRA_RUNTIME

### 裁定 C：ARCH-056 裁定记录修正

**裁定**：更新 architecture_issue_registry.yaml 中 ARCH-056 的裁定内容，明确分层真源规则。

**修正内容**：
- 原裁定 (a)：depgraph.nodes 为架构数据真源，dataflow/decision/blueprint 核心字段单向派生
- 修正 (a)：depgraph.nodes 为**架构数据**真源（模块存在性/依赖关系/文件路径/node_type）；**domain_id 真源为 blueprint frontmatter**（逻辑职责声明）；**design_maturity 各图独立评估**（维度不同，不强制一致）

## 4. 施工方案

### Task 1：修改 align_panoramas.py 检测逻辑

**文件**：
- Modify: `scripts/governance/d5_architecture/generators/align_panoramas.py`
- Test: `tests/test_align_panoramas.py`

**改动**：

1. `_detect_state_drifts` 函数：
   - 不再比较四图 design_maturity 是否一致
   - 改为检测 blueprint 是否缺失 design_maturity 字段（报 WARN）
   - 四图维度差异不再报告

2. `_detect_domain_mismatches` 函数：
   - 当 depgraph 域与 blueprint 域不一致时，以 blueprint 为准
   - 降级为 INFO（不报告为不一致）
   - 仅当 dataflow/decision 与 blueprint 不一致时才报 WARN

3. 更新 `PanoramaAlignmentReport.to_markdown`：
   - 状态漂移表改为"blueprint 字段缺失"表
   - 域不一致表仅显示与 blueprint 不一致的图

### Task 2：数据修复

**文件**：
- Modify: 3 个蓝图文件的 frontmatter
- Modify: 1 个蓝图的 responsibility_domain

**改动**：

1. 补齐 3 个蓝图的 design_maturity 字段：
   - `docs/03_modules/_domain_factor/blueprint.md`（MOD-L02-001）：加 `design_maturity: prototype`
   - `docs/03_modules/_domain_risk/blueprint.md`（MOD-L04-001）：加 `design_maturity: prototype`
   - `docs/03_modules/_domain_portfolio_core/blueprint.md`（MOD-L05-001）：加 `design_maturity: prototype`

2. 改 MOD-GOV-SYNC-PANORAMA 的 responsibility_domain：
   - `docs/03_modules/_domain_governance/panorama_alignment_engine/blueprint.md`：`D_GOVERNANCE` → `D_GOV_SCRIPTS`

3. MOD-MKT_DATA 评估：该模块在 depgraph 只有 1 个 `__init__.py`，无蓝图文件。暂不创建蓝图（模块粒度太小，不值得维护蓝图），在 exempt_list 中豁免其对齐检测。

### Task 3：修正 ARCH-056 + 重跑验证

**文件**：
- Modify: `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml`
- Modify: `docs/01_policies_and_standards/_registry/catalogs/panorama_exempt_list.yaml`

**改动**：

1. 更新 ARCH-056 裁定记录：
   - adjudication 字段 (a) 修正为分层真源规则
   - last_updated 改为 2026-07-10

2. exempt_list 加入 MOD-MKT_DATA：
   ```yaml
   exempt_module_ids:
     - MOD-MKT_DATA
   ```

3. 重跑 align_panoramas.py 验证 0 问题

## 5. 验证标准

1. `python -m pytest tests/test_align_panoramas.py -v` 全部通过
2. `python scripts/governance/d5_architecture/generators/align_panoramas.py` 输出 0 问题
3. 3 个蓝图 frontmatter 有 design_maturity 字段
4. MOD-GOV-SYNC-PANORAMA blueprint 的 responsibility_domain 为 D_GOV_SCRIPTS
5. ARCH-056 裁定记录已更新

## 6. 大白话解释

### 事情过程

四图（depgraph/dataflow/decision/blueprint）就像一个项目的四本账本：
- depgraph 是"代码账本"——记录每个源码文件的状态
- dataflow 是"数据账本"——记录数据产出是否在运行
- decision 是"决策账本"——记录决策是否已实现
- blueprint 是"设计账本"——记录模块整体声明

之前这四本账本对同一个模块的"成熟度"和"所属域"记录不一致，报了 7 个问题。

### 事情结果

调研发现：四本账本从不同角度看同一件事，**不一致是正常的**：
- 代码账本说"部分文件还没到 production"（prototype）
- 数据账本说"数据产出已经在运行了"（production）
- 决策账本说"有些决策还在规划中"（design）

这就像一个人的体检报告：血液指标正常、心电图异常、X 光正常——不同检查看不同维度，不需要强制统一。

对于"所属域"：代码账本按文件物理位置推导（在 trading/ 目录 → 交易域），但设计账本按逻辑职责声明（这是运行时基础设施 → D_INFRA_RUNTIME）。**以设计账本为准是正确的**，因为物理位置可能放错地方。

### 修正方案

1. **检测逻辑修正**：不再要求四本账本的成熟度一致，只检查设计账本是否填写了成熟度字段
2. **域以蓝图为准**：depgraph 的路径投票值不覆盖蓝图的逻辑声明
3. **补齐缺失字段**：3 个蓝图补上 design_maturity 字段
4. **精确化域声明**：MOD-GOV-SYNC-PANORAMA 的域从 D_GOVERNANCE 改为 D_GOV_SCRIPTS（更精确）
