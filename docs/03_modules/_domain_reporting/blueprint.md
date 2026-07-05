---
module_id: MOD-L07-001
submodule_path: src/zephyr/reporting
title: "Post Trade Analytics Core 蓝图 — 盘后分析层"
doc_type: blueprint
status: Active
version: "2.1.0"
layer: L2_domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/reporting/"
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 2
functional_domain: analytics
parent_module: ""
summary: "盘后分析层。TCAEngineBase + AttributionEngineBase OCP扩展点。Phase B骨架就位，Brinson分解待Phase C实现。"
tags: [post-trade-analytics, l07, c-track]
priority: P1
runtime_plane: warm
belongs_to: "MOD-MASTER_BLUEPRINT"
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-L06-001
    at: "§10"
    why: "CTR-005 Fill + CTR-004 Order"
  - target: MOD-L05-001
    at: "§10"
    why: "CTR-006 PositionSnapshot"
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture_model\\layers\\l07_post_trade_analytics.yaml"
    section: ""
    why: "架构层YAML真源"
codification_level: L1
codification_at: "2026-05-15"
---

> module_id: MOD-L07-001 | version: 2.1.0 | status: active | domain: reporting
> actual_disk_path: src/zephyr/reporting/ | generation: 2 | construction_progress: partially_implemented

# ✅ Post Trade Analytics Core 蓝图 — 盘后分析层

> **✅ 业务层已开放，可施工**
> C轨业务层已解除占位禁令[ARCH-045 P0]。AI 可自主施工。
> 当前 construction_progress = partially_implemented，骨架代码已实现，Brinson核心算法待填充。

## 概述

本蓝图描述 ZephyrAlpha 盘后分析层——它解决了交易成本量化与绩效归因标准化的问题。核心职责包括：TCA 交易成本分析、绩效归因（Brinson 三因子分解）、执行报告/归因报告产出。当前规模 2 个 EngineBase + 2 个 Default 实现（骨架），目标容量 5 个 TCA 策略 + 3 个归因模型。上游依赖 MOD-L06-001（Fill/Order）和 MOD-L05-001（PositionSnapshot），下游被 D_FRONTEND Dashboard 和 D_COMPLIANCE Compliance 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L07-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因 |
|---|--------|------------|------|:---:|---------|
| 1 | analytics_base.py | §3.1 | TCAEngineBase + AttributionEngineBase OCP 扩展点 | 已实现 | — |
| 2 | default_tca_engine.py | §3.1 | 默认 TCA 引擎实现 | 已实现 | — |
| 3 | default_attribution_engine.py | §3.1 | 默认归因引擎实现 | 已实现 | — |
| 4 | tests/reporting/ | §9 | 测试用例 | 已阻塞 | C轨未开放，测试目录未创建 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 骨架代码已实现，Brinson核心算法待填充 | `ls src/zephyr/reporting/` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | TCAEngineBase, AttributionEngineBase, DefaultTCAEngine, DefaultAttributionEngine | — | — |
| v2.0.0 (模板v3.3重构) | 同 v1.0.0 | — | 结构重组，无功能变更 |
| v2.1.0 (模板v4.1回填+禁止施工) | 同 v1.0.0 | 测试代码 | C轨 blocked |

---

## §1 设计背景与目标

### 1.1 背景

盘后分析是量化交易闭环的最后一环——交易执行后需要量化交易成本（TCA）和拆解收益来源（Brinson 归因），为策略迭代和合规审查提供数据支撑。当前系统无标准化 TCA/归因框架，各策略自行计算，结果不可比。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | TCA 标准化 | TCAEngineBase OCP 扩展点可用 |
| 2 | ✅ 包含 | 绩效归因标准化 | AttributionEngineBase OCP 扩展点可用 |
| 3 | ✅ 包含 | 执行报告产出 | CTR-P1-007 ExecutionReport 可产出 |
| 4 | ✅ 包含 | 归因报告产出 | CTR-P1-009 PerformanceAttributionReport 可产出 |
| 5 | ❌ 排除 | 交易执行 | D_EXECUTION_CORE Trade Execution |
| 6 | ❌ 排除 | 风险评估 | D_RISK Risk Management |
| 7 | ❌ 排除 | 合规审查 | D_COMPLIANCE Compliance |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 价格字段必须使用 Decimal 类型 | 金融精度要求，禁止 float |
| TCA 计算依赖 D_EXECUTION_CORE Fill 数据 | Fill 不可用时 TCA 无法执行 |
| 归因计算依赖 D_EXECUTION_CORE PositionSnapshot | PositionSnapshot 不可用时归因返回 0 |
| C轨已解除 | 骨架代码可 import，但业务逻辑未填充 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 | 设计+施工 | 审批权限 |
| D_FRONTEND Dashboard | 归因报告展示 | 集成 | CTR-P1-009 消费 |
| D_COMPLIANCE Compliance | 合规审查 | 集成 | CTR-P1-009 消费 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| TCA | DefaultTCAEngine 骨架实现 | 5 个 TCA 策略 | 缺 4 个策略 | P1 |
| 归因 | DefaultAttributionEngine 返回 0 | Brinson 三因子分解 | 核心算法未实现 | P0 |
| 测试 | 无 | 覆盖率 > 80% | 测试目录不存在 | P0 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 日终 TCA 分析 | D_EXECUTION_CORE Fill 到达 | DefaultTCAEngine.analyze(fill, order) → ExecutionReport | CTR-P1-007 |
| 日终归因分析 | ExecutionReport/Fill 事件触发（禁止时间触发） | DefaultAttributionEngine.attribute() → PerformanceAttributionReport | CTR-P1-009 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | TCA 交易成本分析 | TCAEngineBase + DefaultTCAEngine | 本模块 |
| 2 | ✅ 包含 | 绩效归因 | AttributionEngineBase + DefaultAttributionEngine | 本模块 |
| 3 | ✅ 包含 | 执行报告生成 | Fill + Order → ExecutionReport | 本模块 |
| 4 | ✅ 包含 | 归因报告生成 | PositionSnapshot → PerformanceAttributionReport | 本模块 |
| 5 | ❌ 排除 | 订单执行 | D_EXECUTION_CORE Trade Execution 负责 | D_EXECUTION_CORE |
| 6 | ❌ 排除 | 组合构建 | D_PORTFOLIO_CORE Portfolio Construction 负责 | D_PORTFOLIO_CORE |
| 7 | ❌ 排除 | 风险度量 | D_RISK Risk Management 负责 | D_RISK |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | TCAEngineBase | TCA OCP 扩展点 | — | 同步调用 |
| 2 | AttributionEngineBase | 归因 OCP 扩展点 | — | 同步调用 |
| 3 | DefaultTCAEngine | 默认 TCA 实现 | TCAEngineBase | 继承 |
| 4 | DefaultAttributionEngine | 默认归因实现 | AttributionEngineBase | 继承 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_EXECUTION_CORE Fill + Order | 滑点计算 → ExecutionReport | D_FRONTEND, D_COMPLIANCE | ExecutionReport |
| 2 | D_EXECUTION_CORE PositionSnapshot | Brinson 分解 → PerformanceAttributionReport | D_FRONTEND, D_COMPLIANCE | PerformanceAttributionReport |

### 3.3 状态生命周期

本模块无状态机。

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。

### 4.1 公共 API

```python
class TCAEngineBase(abc.ABC):
    """TCA OCP扩展点——新TCA策略继承此类"""
    def analyze(self, fill: Fill, order: Order, idempotency_key: str) -> "ExecutionReport": ...
    def analyze_batch(self, fills: list[Fill], orders: dict[str, Order], idempotency_key: str) -> "list[ExecutionReport]": ...

class AttributionEngineBase(abc.ABC):
    """归因OCP扩展点——新归因模型继承此类"""
    def attribute(self, portfolio_id: str, period_start: str, period_end: str, idempotency_key: str) -> "PerformanceAttributionReport": ...
```

### 4.2 数据模型

> ⚠️ 当前代码使用 `@dataclass(frozen=True)`（codegen 自动生成），非 Pydantic BaseModel。待 KBG-0040 全面落地后迁移。

```python
@dataclass(frozen=True)
class ExecutionReport:
    """执行报告 (CTR-P1-007) — SSoT: cross_layer_contracts.yaml"""
    order_id: str
    symbol: str
    direction: str
    intended_quantity: int
    actual_quantity: int
    intended_price: Decimal
    vwap_price: Decimal
    slippage_bps: float
    commission: Decimal
    execution_start: str
    execution_end: str
    broker_id: str
    idempotency_key: str
    algo_type: str = "NONE"
    schema_version: str = "1.0"

@dataclass(frozen=True)
class PerformanceAttributionReport:
    """归因报告 (CTR-P1-009) — SSoT: cross_layer_contracts.yaml"""
    portfolio_id: str
    period_start: str
    period_end: str
    total_return: float
    allocation_effect: float
    selection_effect: float
    interaction_effect: float
    transaction_cost_drag: float
    idempotency_key: str
    factor_contributions: dict[str, float] = field(default_factory=dict)
    schema_version: str = "1.0"
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `analyze()` | `fill` | ✅ | Fill 对象（CTR-005），fill_price > 0 |
| `analyze()` | `order` | ✅ | Order 对象（CTR-004），limit_price > 0 |
| `analyze()` | `idempotency_key` | ✅ | 非空字符串 |
| `attribute()` | `portfolio_id` | ✅ | 非空字符串 |
| `attribute()` | `period_start` | ✅ | ISO8601 日期 |
| `attribute()` | `period_end` | ✅ | ISO8601 日期 |
| `attribute()` | `idempotency_key` | ✅ | 非空字符串 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `analyze()` | `ExecutionReport`（含 execution_start/end/broker_id/algo_type） | `ZeroDivisionError`（intended_price=0 时已守卫） |
| `attribute()` | `PerformanceAttributionReport`（含 transaction_cost_drag/factor_contributions） | 当前返回 0 值报告（骨架实现） |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 Engine 子类 | ✅ 向后兼容 | OCP 扩展 |
| ExecutionReport 新增字段 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名报告字段 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | TCAEngineBase 为 OCP 扩展点 | 新 TCA 策略只加不改 |
| 2 | AttributionEngineBase 为 OCP 扩展点 | 新归因模型只加不改 |
| 3 | 价格字段使用 Decimal 类型 | Decimal |
| 4 | slippage_bps = (vwap_price - intended_price) / intended_price × 10000 | TCA 标准计算公式 |
| 5 | total_return = allocation + selection + interaction | Brinson 三因子分解 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| TCA 策略数 | 1 (Default) | 5 | 无上限 | ✅ | OCP 扩展 |
| 归因模型数 | 1 (Default) | 3 | 无上限 | ✅ | OCP 扩展 |
| 日处理报告 | ~100 | ~1000 | 无上限 | ✅ | 批量处理 |

### 5.3 迁移

本蓝图不涉及迁移。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | TCA 分析可用性 | 99.9% | 日终执行记录 | TCA 执行成功率 | 99.9% | 每月允许 1 次失败 | 连续 2 次失败 |
| 延迟 | TCA 单笔分析延迟 | P95 < 100ms | 计时 | analyze() 耗时 | P95 < 100ms | — | P95 > 500ms |
| 准确性 | 归因三因子和 | = total_return | 单元测试 | 三因子求和误差 | 0 误差 | — | 误差 ≠ 0 |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | float 用于价格 | Decimal | 金融精度 |
| 2 | 编码模式 | 直接修改 Base 类 | 继承 Base 类实现新策略 | OCP 原则 |
| 3 | 导入源 | zephyr.ex_core.* | zephyr.shared.contracts.execution.* | 分层约束，通过契约解耦 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Fill 数据不足 | 列表为空检测 | 返回空 ExecutionReport 列表 | TCA 无法执行 |
| 2 | Decimal 精度溢出 | OverflowError 捕获 | 统一使用 Decimal 类型 | 计算结果异常 |
| 3 | PositionSnapshot 不可用 | 数据为空检测 | 归因返回 0 值报告 | 归因无实际意义 |
| 4 | intended_price = 0 | ZeroDivisionError 守卫 | slippage_bps = 0 | 滑点计算跳过 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| l07_tca_analysis_total | Counter | 自动埋点 | — | — |
| l07_tca_analysis_errors | Counter | 自动埋点 | 连续 3 次失败 | P2 |
| l07_attribution_report_total | Counter | 自动埋点 | — | — |
| l07_attribution_zero_report_total | Counter | 自动埋点 | > 50% 为零值报告 | P2 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| DefaultTCAEngine | — | TCA 分析 | 返回空报告列表 | Fill 数据恢复 |
| DefaultAttributionEngine | 零值报告输出 | 真实归因分析 | 返回 allocation=0/selection=0/interaction=0 | PositionSnapshot 数据恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 归因结果被篡改 | 中 | PerformanceAttributionReport Pydantic frozen 配置 | 单元测试验证不可变 |
| 2 | 幂等键重复提交 | 低 | idempotency_key 参数传递到下游 | 幂等性测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | TCAEngineBase/DefaultTCAEngine | slippage_bps 计算正确 | 覆盖率 > 80% |
| 2 | 单元测试 | AttributionEngineBase/DefaultAttributionEngine | Brinson 分解正确 | 覆盖率 > 80% |
| 3 | 单元测试 | 边界条件 | intended_price=0 守卫 | ZeroDivisionError 不抛出 |
| 4 | 集成测试 | D_EXECUTION_CORE→D_REPORTING 数据流 | Fill+Order→ExecutionReport | 端到端通过 |

> ⚠️ 测试目录 `tests/reporting/` 尚未创建，C轨开放后 MUST 创建。

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-L06-001 Trade Execution | 必须 | CTR-005 Fill + CTR-004 Order | — | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` |
| MOD-L05-001 Portfolio Construction | 必须 | CTR-006 PositionSnapshot | — | `D:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\portfolio-core\blueprint.md` |
| MOD-L04-001 Risk Management | 可选 | CTR-P1-011 RiskMetricsReport | — | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` |
| MOD-L02-001 Alpha Factor | 可选 | CTR-P1-001 FactorMonitorReport | — | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §5 MOD-L07-001 行 | 逐项核对 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-L07-001` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**：

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| analytics_base.py | default_tca_engine.py | TCAEngineBase 接口 | 继承 |
| analytics_base.py | default_attribution_engine.py | AttributionEngineBase 接口 | 继承 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 模块简单，手动维护可行 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防止蓝图与依赖图漂移 | CI 门禁 | validate_path_alignment.py | 无 | CI 门禁 | PR 提交时 |
| 3 | 临时时态内容自动清理 | 否 | 无临时内容 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | C轨开放后需验证 | pytest | — | 测试目录未创建 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_reporting\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\reporting\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\reporting\` | 测试用例（待创建） |
| 绩效归因报告契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\portfolio\performance_attribution_report.py` | 绩效归因报告结构（归属 MOD-INF-016） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_EXECUTION_CORE Trade Execution | CTR-005/004 消费 | TCA 可接收 Fill+Order | TCA 分析可执行 |
| D_FRONTEND Dashboard | CTR-P1-009 产出 | Dashboard 可展示归因报告 | Dashboard 可渲染 |
| D_COMPLIANCE Compliance | CTR-P1-009 产出 | 合规可审查归因结果 | 合规可消费 |

---

## §13 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress 更新 | 进度变更 |
| 2 | 架构层 YAML | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\layers\l07_post_trade_analytics.yaml` | 确认 files 列表与磁盘一致 | 文件清单同步 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | DefaultTCAEngine 滑点计算简化 | 高 | 中 | OCP 扩展点允许替换 | 风险 |
| 2 | DefaultAttributionEngine 返回 0 | 高 | 高 | Phase C 实现 Brinson 计算 | 风险 |
| 3 | Decimal 精度溢出 | 低 | 中 | 统一使用 Decimal 类型 | 风险 |
| 4 | 新策略需实现对应 Base 类 | — | 中 | OCP 扩展点文档 + 示例 | 负面后果 |
| 5 | 默认实现为骨架，需 Phase C 填充 | — | 高 | Phase C 施工计划已排期 | 负面后果 |

---

## §16 施工指引

> ✅ **C轨已解除——以下施工步骤可执行。**

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | C轨已解除 | MOD-MASTER_BLUEPRINT construction_progress >= implementation_phase | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 扩展 |
| 核心风险 | 归因计算正确性 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板 v4.1 回填） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | TCAEngineBase 定义 | hard | 已实现 | ☐ |
| 2 | AttributionEngineBase 定义 | hard | 已实现 | ☐ |
| 3 | CTR-005 Fill 契约 | hard | 部分实现 | ☐ |
| 4 | CTR-006 PositionSnapshot 契约 | hard | 部分实现 | ☐ |
| 5 | C轨已解除解除 | hard | 未满足 | ☐ |

### 16.3 实施步骤

#### 步骤 1：完善 DefaultTCAEngine

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\reporting\implementations\default_tca_engine.py` |
| 验收标准 | import 成功，slippage_bps 计算使用 Decimal |
| 验证命令 | `python -c "from zephyr.reporting.implementations.default_tca_engine import DefaultTCAEngine"` |
| G7 检查项 | 上游 analytics_base.py 存在，下游 D_FRONTEND/D_COMPLIANCE 可消费 |
| AI 自治范围 | ai_modifiable |
| 检查点 | DefaultTCAEngine 可实例化且 analyze() 可调用 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-L07-001 | default_tca_engine.py | code | `D:\ZephyrAlpha\src\zephyr\reporting\implementations\default_tca_engine.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| default_tca_engine.py | TCA 滑点计算 + Implementation Shortfall | ① slippage_bps 使用 Decimal ② intended_price=0 守卫 ③ analyze_batch 批量处理 |

#### 步骤 2：实现 DefaultAttributionEngine Brinson 分解

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\reporting\implementations\default_attribution_engine.py` |
| 验收标准 | import 成功，Brinson 三因子分解正确 |
| 验证命令 | `python -c "from zephyr.reporting.implementations.default_attribution_engine import DefaultAttributionEngine"` |
| G7 检查项 | 上游 analytics_base.py 存在，下游 D_FRONTEND/D_COMPLIANCE 可消费 |
| AI 自治范围 | ai_modifiable |
| 检查点 | DefaultAttributionEngine.attribute() 返回非零 allocation/selection/interaction |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-L07-001 | default_attribution_engine.py | code | `D:\ZephyrAlpha\src\zephyr\reporting\implementations\default_attribution_engine.py` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| default_attribution_engine.py | Brinson 三因子分解 | ① allocation_effect 非零 ② selection_effect 非零 ③ interaction_effect 非零 ④ total_return = 三者之和 |

#### 步骤 3：实现 CTR-P1-009 完整产出 + 测试

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 + §9 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\reporting\implementations\` + `D:\ZephyrAlpha\tests\reporting\` |
| 验收标准 | PerformanceAttributionReport 可被 D_FRONTEND/D_COMPLIANCE 消费，测试通过 |
| 验证命令 | `python -m pytest tests/reporting/ -k attribution -v` |
| G7 检查项 | 下游 D_FRONTEND/D_COMPLIANCE 可消费，测试覆盖率 > 80% |
| AI 自治范围 | ai_modifiable |
| 检查点 | pytest exit 0 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | DefaultTCAEngine 实现失败 | 还原 implementations/default_tca_engine.py |
| 2 | DefaultAttributionEngine 实现失败 | 还原 implementations/default_attribution_engine.py |
| 3 | CTR-P1-009 产出失败 | 还原 implementations/ |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | DefaultTCAEngine 存在 | `ls` exit 0 | 完成 | ☐ |
| 2 | DefaultAttributionEngine 存在 | `ls` exit 0 | 完成 | ☐ |
| 3 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 4 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 5 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 6 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 7 | 测试已通过 | §9 pytest exit 0 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | not_started | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | slippage_bps 计算 | 算法 | `(fill_price - intended_price) / intended_price * 10000` | default_tca_engine.py |
| 2 | Brinson 三因子 | 算法 | `total_return = allocation_effect + selection_effect + interaction_effect` | default_attribution_engine.py |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -c "from zephyr.reporting import TCAEngineBase"` | 验证 import | — | exit 0 |
| 2 | 配置 | `benchmark_price_source` | TCA 基准价格来源 | `arrival`/`vwap` | 默认 `arrival` |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | import 失败 | 模块路径错误 | 检查 __init__.py | 修正路径 | `python -c "import ..."` |
| 2 | 运行 | TCA 分析异常 | Fill 数据为空 | 检查 D_EXECUTION_CORE 数据流 | 返回空报告列表 | 日志确认 |
| 3 | 运行 | 归因全零 | PositionSnapshot 缺失 | 检查 D_EXECUTION_CORE 数据流 | 返回零值报告 | 日志确认 |

### 16.12 并发操作模型

本模块无并发操作——日终批处理，单线程执行。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| TCA 策略数 | 1 (Default) | TCAEngineBase 子类计数 |
| 归因模型数 | 1 (Default) | AttributionEngineBase 子类计数 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L07-001 | DefaultAttributionEngine 返回 0 | 实现 Brinson 分解 | P0 | 归因结果全为 0 | v2.1.0 | 待施工 |
| GAP-L07-002 | 测试目录不存在 | 创建测试套件 | P0 | C轨开放 | v2.1.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | TCAEngineBase + AttributionEngineBase + 默认实现 | ⚠️ |
| v2.0.0 | 2 | 模板v3.3重构 | 章节重排 + 新增概述/标准锚点/§6/§9/§12/§14/§18 | ⚠️ |
| v2.1.0 | 2 | 模板v4.1回填 | §1.5/§1.6/§1.7/§5.4/§5.7/§6.1/§6.2/§16.5/§16.7/§16.8/§16.10/§16.12/术语表/自检清单/成熟度 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工 Phase | 状态 |
|--------|---------|---------|----------|:---:|
| BrinsonAttribution | GAP-L07-001 | default_attribution_engine.py | Phase 2 | 待施工 |
| TestSuite | GAP-L07-002 | tests/reporting/ | Phase 3 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L07-01 | TCA/归因使用 OCP 扩展点 | A: 单一实现 / B: OCP Base 类 | B | 策略可扩展，只加不改 | 2026-05-05 |
| 2 | D-L07-02 | 价格使用 Decimal | A: float / B: Decimal | B | 金融精度要求 | 2026-05-05 |
| 3 | D-L07-03 | 归因模型选择 Brinson | A: Brinson / B: Carino / C: 多模型 | A | Brinson 三因子为行业标准，实现简单 | 2026-05-05 |
| 4 | D-L07-04 | 模板v4.1升级 | A: 保持v3.3 / B: 按v4.1升级 | B | v4.1 模板合规 | 2026-05-15 |
| 5 | D-L07-05 | construction_progress 修正为 partially_implemented | A: partially_implemented / B: partially_implemented | B | C轨未开放，骨架代码≠部分实现 | 2026-05-15 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| TCA | Transaction Cost Analysis，交易成本分析 | 归因分析 | TCA 量化执行成本，归因拆解收益来源 |
| Brinson 分解 | 将组合收益拆为 allocation + selection + interaction 三因子 | Carino 分解 | Brinson 为加法模型，Carino 为乘法模型 |
| OCP | Open-Closed Principle，开闭原则 | 继承 | OCP = 对扩展开放对修改关闭，继承是实现手段 |
| slippage_bps | 滑点基点 = (实际价格 - 目标价格) / 目标价格 × 10000 | 佣金 | slippage 衡量执行偏差，佣金是固定成本 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | DefaultAttributionEngine 三因子全返回 0 | 高 | Brinson 算法未实现 | Phase C 实现 | §5.1 #5 | 待解决 |
| 2 | 测试目录不存在 | 高 | C轨已解除 | 可创建 | §9 | 待解决 |
| 3 | analyze() 接口与蓝图 v2.0.0 描述不一致 | 中 | v2.0.0 写 list 参数，代码用单参数 | v2.1.0 已修正蓝图与代码对齐 | §4.1 | 已解决 |
| 4 | §4.2 数据模型与代码实际不一致 | 高 | v2.0.0 用 Pydantic BaseModel 且字段不匹配 | v2.1.0 已修正为 @dataclass(frozen=True) + 与代码字段对齐 | §4.2 | 已解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ✅ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | Brinson 实现后可升级为 frozen | OCP 扩展点设计已稳定 |
| 接口契约 | stable | 高 | 新增策略后验证兼容性 | TCAEngineBase/AttributionEngineBase 签名已冻结 |
| 数据模型 | evolving | 中 | Brinson 实现后补全字段 | PerformanceAttributionReport 字段可能扩展 |
| 施工步骤 | evolving | 中 | C轨开放后执行验证 | 步骤可能根据实际施工调整 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 初始占位 | — | 已完成 |
| v1.0.0 | Base 类 + 默认实现骨架 | v0.1.0 | 已完成 |
| v2.0.0 | 模板 v3.3 重构 | v1.0.0 | 已完成 |
| v2.1.0 | 模板 v4.1 回填 + 禁止施工标注 | v2.0.0 | 已完成 |
| v3.0.0 | Brinson 实现 + 测试套件 | v2.1.0 | 待施工（C轨开放后） |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略 | 关键信息缺失 |
| 3 | 蓝图必须是最终设计结果 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 上下文缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 蓝图与代码漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | 职责混淆 |
| 16 | 术语表不可省略 | 术语理解漂移 |
| 17 | 参考实现规格 vs 已实现代码重复——接口契约无法表达的逻辑规格 MUST 保留在 §16.7 | 关键逻辑实现错误 |
| 18 | 对标验证表格 vs 对标散文——结构化对标表格 MUST 保留；长篇对标散文 MUST 删除 | 丢表格/留噪音 |
| 19 | SLO 必须定义——§5.4 不可省略 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略——§6.1 不可省略 | 故障无法发现 |
| 21 | 退化矩阵必须声明——§6.2 不可省略 | 部分失败时行为不可预测 |

---

## 蓝图拆分判定标准

| 判定条件 | 结果 | 操作 |
|---------|------|------|
| 服务对象相同 + 变更频率同步 + 依赖关系重叠 | 原地升级 | 在 §17 容量升级附录中增量记录 |
| 有独立 module_id 前缀 | 拆分 | 创建子蓝图，belongs_to=本蓝图 |
| 有独立 Phase 路线图和交付节奏 | 拆分 | 同上 |
| 有独立依赖关系图（与主体 depends_on 交集<50%） | 拆分 | 同上 |
| 内容超100行且与主体无直接数据流 | 拆分 | 同上 |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。盘后分析层为纯新增/扩展型模块，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type 词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| — | 无 | — | — | — |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | analytics_base.py | `D:\ZephyrAlpha\src\zephyr\reporting\analytics_base.py` | 读取 | 无变更 |
| 2 | implementations/ | `D:\ZephyrAlpha\src\zephyr\reporting\implementations\` | 修改 | 完善实现（C轨开放后） |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本蓝图的核心架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| 本模块的施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 本模块的接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | D_FRONTEND Dashboard | §4 接口契约、§10 依赖关系 |
| Tier 1 | D_COMPLIANCE Compliance | §4 接口契约 |
| Tier 2 | D_RESEARCH Research | CTR-P1-007 ExecutionReport |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| Base 类接口变更 | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 默认实现类变更 | AI 可自主修改 | — | — |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 容量升级方案新增 | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |
