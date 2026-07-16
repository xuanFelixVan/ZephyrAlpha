---
module_id: MOD-L05-001
submodule_path: src/zephyr/pf_core
title: "Portfolio Construction Core 蓝图+施工图 — 组合构建层"
doc_type: blueprint
status: Active
version: "2.1.0"
layer: L2_domain
layer_name: portfolio_construction
functional_domain: portfolio
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/pf_core/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-15"
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 2
rule_form: structural
scope: module
stability: evolving
design_maturity: prototype
verifiability: manual
summary: "D_PORTFOLIO_CORE 组合构建层——StrategyBase OCP-002 扩展点 + StrategyRegistry。Phase 1 部分实现：策略骨架 + 默认股票多头策略 + 注册表。"
priority: P0
runtime_plane: hot
tags: [portfolio-construction, l05, c-track, phase-1-partial]
depends_on:
  - target: MOD-L03-001
    at: CTR-P1-015
    why: 消费 SynthesizedSignal（source_layer=D_SIGNAL）
  - target: MOD-L04-001
    at: CTR-003
    why: 消费 RiskLimits
references:
  - path: "D:\\ZephyrAlpha\\architecture_model\\layers\\l05_portfolio_construction.yaml"
    section: "全篇"
    why: "YAML SSoT"
responsibility_domain: 
build_status: generated
---

> ✅ **业务层已开放，可施工** — C轨（业务价值线·线7）当前状态为 partially_implemented。本蓝图仅供架构参考和预研代码维护，可以此蓝图为依据新增组合构建业务代码。

> module_id: MOD-L05-001 | version: 2.1.0 | status: Active | layer: L2_domain
> actual_disk_path: src/zephyr/pf_core/ | generation: 2 | construction_progress: partially_implemented

# Portfolio Construction Core 蓝图+施工图 — 组合构建层

## 概述

本蓝图描述 ZephyrAlpha 组合构建层——它解决了从信号到委托指令的转换问题。核心职责包括：策略注册与发现（StrategyBase OCP-002 扩展点）、目标权重生成（等权/信号加权/最小方差/风险平价）、订单列表生成（target_weights → 增量 Order）、风控约束应用。当前规模 1 种策略（DefaultEquityStrategy），目标容量 4 种策略 + 500 标的池。上游依赖 D_SIGNAL SynthesizedSignal + D_RISK RiskLimits，下游被 D_EXECUTION_CORE ExecutionBroker / D_REPORTING Analytics / D_COMPLIANCE Compliance 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> **命名统一（ARB-20）**：YAML module id 为 `l05-layer-ssot`，blueprint-registry 使用 `portfolio-core`。本蓝图统一为 `portfolio-core`，YAML 侧待同步。
>
> **source_layer 修正**：YAML 中 source_layer 原标注为 D_FACTOR，实际信号来源为 D_SIGNAL（SynthesizedSignal）。本蓝图以 D_SIGNAL 为准。
>
> **ARB-20 裁定**：D_PORTFOLIO_CORE 产出 CTR-007（TargetPortfolio），非 CTR-004（Order）。D_EXECUTION_CORE-oms 将 CTR-007 转化为 CTR-004。当前代码 DefaultEquityStrategy.generate_target_weights() 返回 list[Order]（CTR-004），待 Phase 2 重构为返回 TargetPortfolio（CTR-007）。

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules MOD-L05-001`
> 以下手写内容保留职责描述（depgraph 无此信息），文件列表以 depgraph 为准。

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L05-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|
| 1 | `strategy_base.py` | §3.1 | StrategyBase + StrategyMeta + StrategyRegistry + autodiscover | 已实现 | — |
| 2 | `strategy_registry.py` | §3.1 | re-export 卫星模块 | 已实现 | — |
| 3 | `strategies/default_equity_strategy.py` | §3.1 | 默认股票多头策略（等权/信号加权） | 已实现 | — |
| 4 | `strategies/__init__.py` | §11 | 策略子包初始化 | 已实现 | — |
| 5 | `__init__.py` | §11 | 包初始化 + CTR 声明 | 已实现 | — |

> YAML SSoT 列出 `default_equity_strategy.py` 在根目录，实际磁盘位于 `strategies/` 子目录。

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 strategy_base.py / strategy_registry.py / default_equity_strategy.py | ✅ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" D:\ZephyrAlpha\src\zephyr\pf_core\*.py` | ✅ |
| actual_disk_path 与 §11 产出物路径一致 | 逐项核对 | ✅ |
| §4 接口签名与代码一致 | generate_target_weights() 签名核对 | ⚠️ 见§0 ARB-20说明 |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | StrategyBase + StrategyMeta, StrategyRegistry, DefaultEquityStrategy | 最小方差/风险平价策略, CTR-P1-006 StrategyLifecycleEvent 产出 | C轨blocked |
| v2.0.0 (模板v3.3重构) | 同 v1.0.0 + 结构重组 | 同 v1.0.0 | 结构重组，无功能变更 |
| v2.1.0 (模板v4.1回填+ARB-20对齐) | 同 v2.0.0 + 接口签名修正 | 同 v1.0.0 + CTR-007 TargetPortfolio 重构 | C轨blocked |

---

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L05-001`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L05-001` 的 9 个 file 节点 | prototype | `extract_depgraph.py --modules MOD-L05-001` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 73 个决策节点 / 2 个决策层 | design | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L05-001 | MOD-L05-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 9 文件 | 5 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 量化架构需要从信号层（D_SIGNAL）和风控层（D_RISK）的输出，转化为可执行的委托指令。当前无组合构建模块，信号和风控输出无法自动转化为交易指令。D_PORTFOLIO_CORE 组合构建层填补这一空白，作为信号→执行的桥梁。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 策略扩展点：StrategyBase (OCP-002) 支持多策略注册与自动发现 | 新策略通过继承+注册即可接入，无需修改框架代码 |
| 2 | ✅ 包含 | 目标权重生成：等权 / 信号加权 / 最小方差 / 风险平价 | 4 种权重方案均产出 target_weights: dict[str, float] |
| 3 | ✅ 包含 | 订单生成：目标权重 → 增量订单 | CTR-004 Order 产出至 D_EXECUTION_CORE（待重构为 CTR-007 TargetPortfolio） |
| 4 | ✅ 包含 | 策略生命周期：CTR-P1-006 StrategyLifecycleEvent | 事件产出至 D_REPORTING/D_COMPLIANCE |
| 5 | ❌ 排除 | 信号合成 | D_SIGNAL 职责 |
| 6 | ❌ 排除 | 风险限额计算 | D_RISK 职责 |
| 7 | ❌ 排除 | 订单执行 | D_EXECUTION_CORE 职责 |
| 8 | ❌ 排除 | 策略回测 | 独立模块，不在组合构建层范围 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 运行于 hot plane（实时交易路径） | 延迟敏感，权重计算 MUST 在毫秒级完成 |
| 风控约束从 D_RISK 实时获取 | 策略 MUST 在每次调用时读取最新 RiskLimits，禁止缓存 |
| 策略注册在启动时完成 | 运行时不可动态注册新策略，避免交易中状态变更 |
| 幂等键（INV-007） | 所有跨层调用携带 idempotency_key，支持重试安全 |
| C轨 partially_implemented | 业务代码仅预研级别，不得用于生产 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 + C轨激活审批 | 设计+施工 | 审批权限 |
| D_EXECUTION_CORE 消费者 | CTR-007/CTR-004 接口兼容 | 集成 | 接口变更需通知 |
| D_REPORTING/D_COMPLIANCE 消费者 | CTR-P1-006 事件格式 | 集成 | 事件变更需通知 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 策略数量 | 1（DefaultEquityStrategy） | 4+ | 缺最小方差/风险平价 | P1 |
| 输出契约 | CTR-004 Order | CTR-007 TargetPortfolio（ARB-20） | 需重构输出格式 | P0 |
| 生命周期事件 | 无 | CTR-P1-006 | 缺事件产出 | P1 |
| 子模块覆盖 | 2/6（strategy_base + default_equity） | 6/6（rebalance/meta-router/allocator/portfolio/strategic/tactical） | 缺4个子模块 | P2 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 等权调仓 | 调仓周期触发 | universe 输入 → 等权分配 → 风控截断 → Order 列表 | CTR-004 Orders |
| 信号加权调仓 | D_SIGNAL 信号更新 | SynthesizedSignal → 信号排序 → 加权分配 → 风控截断 → Order 列表 | CTR-004 Orders |
| 风控截断 | 权重超限 | 检测超限 → 截断至 max_single_position → 记录告警 | 截断后权重 |
| 策略降级 | 信号降级（CTR-ERR-003） | 降级为等权策略 → 记录遥测 | 等权权重 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 策略注册与发现 | StrategyRegistry 维护策略注册表，autodiscover_strategies() 扫描 strategies/ 目录 | 本模块 |
| 2 | ✅ 包含 | 目标权重生成 | 等权 / 信号加权 / 最小方差 / 风险平价 | 本模块 |
| 3 | ✅ 包含 | 订单列表生成 | target_weights → 增量 Order 列表（CTR-004，待重构为 CTR-007） | 本模块 |
| 4 | ✅ 包含 | 风控约束应用 | 从 D_RISK RiskLimits 获取约束，确保目标权重不违反限额 | 本模块 |
| 5 | ❌ 排除 | 信号合成 | D_SIGNAL（SynthesizedSignal） | D_SIGNAL |
| 6 | ❌ 排除 | 风险限额计算 | D_RISK（RiskLimits） | D_RISK |
| 7 | ❌ 排除 | 订单执行 | D_EXECUTION_CORE（ExecutionBroker） | D_EXECUTION_CORE |
| 8 | ❌ 排除 | 策略回测 | 独立回测模块 | D_RESEARCH |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | StrategyBase | 策略抽象基类，定义 generate_target_weights() 接口 | 无 | 同步调用 |
| 2 | StrategyMeta | 策略元数据（strategy_id / name / strategy_type / version / description） | 无 | 属性访问 |
| 3 | StrategyRegistry | 策略注册/发现/自动扫描 | StrategyBase | 同步调用 + 装饰器注册 |
| 4 | DefaultEquityStrategy | 默认股票多头策略（等权/信号加权） | StrategyBase, RiskLimits(D_RISK), SynthesizedSignal(D_SIGNAL) | 同步调用 |

> **依赖图对齐**：dependency_path_panorama.md §3.12 列出 6 子模块（rebalance/meta-router/allocator/portfolio/strategic/tactical），当前代码仅实现 strategy_base + default_equity_strategy。6 子模块为 YAML SSoT 终局架构，当前为 Phase 1 预研实现。

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_SIGNAL SynthesizedSignal + D_RISK RiskLimits | StrategyBase.generate_target_weights() → target_weights / Order 列表 | 内部 / D_EXECUTION_CORE | Pydantic Model |
| 2 | target_weights | DefaultEquityStrategy._weights_to_orders() → Order 列表 | D_EXECUTION_CORE ExecutionBroker | CTR-004 Order |
| 3 | 策略状态变更 | StrategyLifecycleEvent 产出 | D_REPORTING 分析 / D_COMPLIANCE 合规 | CTR-P1-006 |

> **ARB-20 修正**：终局数据流应为 D_PORTFOLIO_CORE → CTR-007 TargetPortfolio → D_EXECUTION_CORE-oms 转换为 CTR-004 Order。当前代码直接产出 CTR-004 Order，待 Phase 2 重构。

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| Unregistered | @StrategyRegistry.register | Registered | strategy_id 无重复 |
| Registered | autodiscover_strategies() 扫描 | Discovered | 文件在 strategies/ 目录下 |
| Discovered | 策略实例化 | Active | 依赖的 D_SIGNAL/D_RISK 契约可用 |
| Active | 策略异常/降级 | Degraded | CTR-ERR-003 SignalDegradationWarning |

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。当前 StrategyMeta 使用 @dataclass(frozen=True)，待重构为 Pydantic BaseModel。

### 4.1 公共 API

| 类/方法 | 签名 | 说明 |
|---------|------|------|
| `StrategyBase.generate_target_weights()` | `(self, universe: list[str], signals: dict[str, float], constraints: dict[str, Any]) -> dict[str, float]` | 生成目标权重（抽象方法） |
| `DefaultEquityStrategy.generate_target_weights()` | `(self) -> list[Order]` | 覆写基类，直接返回 Order 列表（⚠️ 与基类签名不一致，待重构） |
| `StrategyBase.validate_constraints()` | `(self, weights: dict[str, float]) -> bool` | 验证约束条件（默认通过） |
| `StrategyRegistry.register` | `@classmethod decorator` | 装饰器注册策略 |
| `StrategyRegistry.get()` | `(strategy_id: str) -> Type[StrategyBase] | None` | 按 ID 获取策略类 |
| `StrategyRegistry.list_all()` | `() -> dict[str, type[StrategyBase]]` | 列出所有已注册策略 |
| `StrategyRegistry.count()` | `() -> int` | 已注册策略数 |
| `autodiscover_strategies()` | `(package_path: str) -> int` | 扫描 strategies/ 目录自动注册 |

### 4.2 数据模型

| 模型 | 字段 | 类型 | 说明 |
|------|------|------|------|
| StrategyMeta | strategy_id | str | 策略唯一标识 |
| StrategyMeta | name | str | 策略名称 |
| StrategyMeta | strategy_type | str | 策略类型 |
| StrategyMeta | version | str | 策略版本 |
| StrategyMeta | description | str | 策略描述 |
| StrategyMeta | factor_dependencies | list[str] | 因子依赖（默认[]） |
| StrategyMeta | author | str | 作者（默认"agent"） |
| StrategyMeta | tags | list[str] | 标签（默认[]） |
| StrategyMeta | supported_markets | list[str] | 支持市场（默认[]） |
| RebalanceMode | — | str, Enum | equal_weight / signal_weight / min_variance / risk_parity |
| CTR-004 Order | 见契约 SSoT | — | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\order.py` |
| CTR-P1-006 StrategyLifecycleEvent | 待实现 | — | 策略生命周期事件 |

### 4.3 输入契约

| 契约 ID | 名称 | 来源层 | 用途 |
|---------|------|--------|------|
| CTR-P1-015 | SynthesizedSignal | **D_SIGNAL** | 信号加权策略输入（source_layer=D_SIGNAL 非 D_FACTOR） |
| CTR-003 | RiskLimits | D_RISK | 风控约束（max_single_position 等） |
| CTR-ERR-004 | RiskLimitViolationError | D_RISK | 风控硬错误 |
| CTR-002 | FactorSignal | D_FACTOR | 因子依赖 |
| CTR-ERR-003 | SignalDegradationWarning | D_SIGNAL | 信号降级 |
| CTR-ERR-005 | ExecutionRejectionError | D_EXECUTION_CORE | 执行拒绝 |
| CTR-P1-003 | CapitalAllocationResult | D_SIGNAL | 资金分配 |
| CTR-P1-011 | RiskMetricsReport | D_RISK | 风险指标 |
| CTR-P1-010 | SystemConfiguration | 基础设施 | 系统配置 |
| CTR-P1-013 | TelemetryEmitter | 遥测 | 遥测 |

### 4.4 输出契约

| 契约 ID | 名称 | 目标层 | 用途 | ARB-20 修正 |
|---------|------|--------|------|------------|
| CTR-004 | Order | D_EXECUTION_CORE | 委托指令（当前实现） | 终局应为 CTR-007 TargetPortfolio |
| CTR-P1-006 | StrategyLifecycleEvent | D_REPORTING, D_COMPLIANCE | 策略生命周期事件 | — |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增策略类 | ✅ 向后兼容 | 继承 StrategyBase + 注册即可 |
| 新增权重模式 | ✅ 向后兼容 | supported_modes 扩展 |
| 修改 StrategyBase 接口 | ❌ 破坏性 | 需 Owner 审批 + 所有策略实现同步更新 |
| 修改 CTR-004 Order 结构 | ❌ 破坏性 | 需 Owner 审批 + D_EXECUTION_CORE 同步更新 |
| 新增 CTR-P1-006 事件类型 | ✅ 向后兼容 | 不影响已有消费者 |
| CTR-004 → CTR-007 重构 | ❌ 破坏性 | 需 Owner 审批 + D_EXECUTION_CORE 同步更新（ARB-20） |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

### OCP 扩展点

| 扩展点 | 基类 | 注册机制 |
|--------|------|---------|
| 策略扩展 | `StrategyBase` | `@StrategyRegistry.register` + `_strategies` |
| 策略元数据 | `StrategyMeta` | `_meta` 属性 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|------|
| 1 | OCP-002：StrategyBase 为唯一策略扩展点 | 新策略 MUST 继承 StrategyBase 并注册 |
| 2 | 风控约束 MUST 从 D_RISK RiskLimits 获取 | D_RISK RiskLimits |
| 3 | INV-007：幂等键 | 所有跨层调用携带 idempotency_key |
| 4 | CODEGEN-GUARD：CTR 声明手动维护 | CTR-declarations-manual 不可自动重生成 |
| 5 | KBG-0040：数据模型强制 Pydantic V2 BaseModel | StrategyMeta 当前为 @dataclass，待重构 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 策略数量 | 1 | 10 | 无硬限制 | ✅ | StrategyRegistry 字典查找 O(1) |
| 标的池大小 | ~50 | ~500 | 无硬限制 | ✅ | 权重计算线性复杂度 |
| 订单生成频率 | 1次/调仓周期 | 1次/分钟 | 无硬限制 | ✅ | 增量订单计算 O(n) |

### 5.3 迁移

本蓝图不涉及文件迁移/废弃。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 权重计算可用性 | 99.9% | 调用成功率 | 成功调用/总调用 | 99.9% | 每月允许失败<43min | <99.5%告警 |
| 可维护性 | MTTR | <30min | 故障记录 | — | — | — | — |
| 延迟 | 权重计算延迟 | P95<10ms | generate_target_weights() 计时 | P95延迟 | <10ms | — | >50ms告警 |
| 延迟 | 订单生成延迟 | P95<5ms | _weights_to_orders() 计时 | P95延迟 | <5ms | — | >20ms告警 |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 策略内部硬编码风控限额 | 从 D_RISK RiskLimits 获取 | 策略不可自行放宽限额 |
| 2 | 编码模式 | 运行时动态注册策略 | 启动时注册 | 避免交易中状态变更 |
| 3 | 导入源 | `from zephyr.ex_core.* import *` | 通过 CTR-004 契约交互 | 分层约束 |
| 4 | 数据模型 | `@dataclass` 用于新数据模型 | Pydantic V2 BaseModel | KBG-0040 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 策略注册冲突（重复 strategy_id） | StrategyRegistry.register 检测 | 抛出 ValueError，拒绝注册 | 策略初始化阶段 |
| 2 | 风控约束违反（权重超限） | CTR-ERR-004 RiskLimitViolationError | 截断权重至限额内 + 记录告警 | D_EXECUTION_CORE 订单执行 |
| 3 | 信号降级 | CTR-ERR-003 SignalDegradationWarning | 降级为等权策略 + 记录遥测 | 权重质量 |
| 4 | 执行拒绝 | CTR-ERR-005 ExecutionRejectionError | 重新计算权重（排除被拒标的） | D_EXECUTION_CORE 订单执行 |
| 5 | 策略依赖的 D_SIGNAL/D_RISK 契约不可用 | 导入/调用失败 | 抛出明确异常，策略保持 Degraded 状态 | 策略生命周期 |
| 6 | autodiscover 扫描失败 | importlib 异常 | 记录 warning 日志，跳过该策略 | 策略发现 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| pf_core_strategy_registry_count | Gauge | StrategyRegistry.count() | <1（无策略注册） | P2 |
| pf_core_weight_calc_duration_ms | Histogram | generate_target_weights() 计时 | P95>50ms | P2 |
| pf_core_order_gen_duration_ms | Histogram | _weights_to_orders() 计时 | P95>20ms | P3 |
| pf_core_risk_truncation_total | Counter | 风控截断事件 | >10次/调仓周期 | P1 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| D_SIGNAL SynthesizedSignal | 等权策略 | 信号加权策略 | 降级为等权 | D_SIGNAL 恢复健康 |
| D_RISK RiskLimits | 无风控约束的权重 | 风控截断 | 策略保持 Degraded，禁止下单 | D_RISK 恢复健康 |
| DefaultEquityStrategy | — | 全部策略功能 | 策略不可用，记录告警 | 策略修复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 策略自行放宽风控限额 | 高 | 风控约束 MUST 从 D_RISK RiskLimits 获取，禁止策略内部硬编码或放宽限额 | 代码审查 + 单元测试验证 RiskLimits 来源 |
| 2 | 恶意策略注册 | 中 | StrategyRegistry.register 检测重复 strategy_id 并抛出 ValueError | 单元测试验证重复注册拒绝 |
| 3 | 幂等键缺失导致重复下单 | 高 | INV-007 强制所有跨层调用携带 idempotency_key | 集成测试验证幂等性 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | StrategyBase / StrategyRegistry / StrategyMeta | 策略注册/发现/重复注册拒绝；meta frozen/默认值；抽象类不可实例化 | 覆盖率 ≥ 80% |
| 2 | 单元测试 | DefaultEquityStrategy | 等权/信号加权权重计算；风控约束截断；空 universe 处理 | 覆盖率 ≥ 80% |
| 3 | 集成测试 | D_RISK 风控约束 → D_PORTFOLIO_CORE 权重生成 → D_EXECUTION_CORE 订单 | RiskLimits 约束传递；Order 结构符合 CTR-004；幂等键传递 | 端到端通过 |
| 4 | 回归测试 | 策略注册表结构变更 | 注册表变更后所有策略仍可正常注册和执行 | 全量通过 |

> **测试路径**：`D:\ZephyrAlpha\tests\unit\pf_core\`（非蓝图原写的 `tests/pf_core/`）

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-L03-001 | 必须 | CTR-P1-015 SynthesizedSignal, CTR-P1-003 CapitalAllocationResult, CTR-ERR-003 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_signal\blueprint.md` |
| MOD-L04-001 | 必须 | CTR-003 RiskLimits, CTR-ERR-004, CTR-P1-011 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` |
| MOD-L02-001 | 可选 | CTR-002 FactorSignal | — | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` |
| MOD-L06-001 | 下游 | CTR-004 Order 消费方（终局 CTR-007 TargetPortfolio） | — | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` |
| MOD-L07-001 | 下游 | CTR-P1-006 StrategyLifecycleEvent 消费方 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_reporting\blueprint.md` |
| MOD-L10-001 | 下游 | CTR-P1-006 StrategyLifecycleEvent 消费方 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_compliance\blueprint.md` |

### §10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 说明 |
|---|--------|---------|:-------:|------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §3.12 | 蓝图声明的每个依赖在依赖图中有对应条目 | ⚠️ 部分对齐 | 依赖图列出6子模块，蓝图当前仅覆盖2个 |
| 2 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | 待验证 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | ⚠️ 部分对齐 | 依赖图6子模块 vs 代码4文件 |
| 4 | ARB-20 CTR-007 vs 当前 CTR-004 | 输出契约对齐 | ⚠️ 待重构 | 当前代码产出 CTR-004，终局应为 CTR-007 |

### §10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**：无内部依赖

### §10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 模块简单，依赖少 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防漂移 | CI门禁 | check_contract_code_drift.py | 无 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 否 | — | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | 防虚假进度 | pytest | pytest | 无 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\portfolio-core\blueprint.md` | 本文件（含设计和施工指引） |
| 接口定义 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategy_base.py` | StrategyBase + StrategyMeta + StrategyRegistry |
| 注册表卫星 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategy_registry.py` | re-export 卫星模块 |
| 策略实现 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategies\` | 策略子目录 |
| 契约 SSoT | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\order.py` | CTR-004 Order |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\pf_core\` | 测试用例 |
| 持仓契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\portfolio\position.py` | 持仓数据结构（归属 MOD-INF-016） |
| 绩效归因报告契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\portfolio\performance_attribution_report.py` | 绩效归因报告结构（归属 MOD-INF-016） |
| 资金分配结果契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\capital_allocation_result.py` | 资金分配结果（归属 MOD-INF-016） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 | 状态 |
|------------|---------|--------|---------|:---:|
| D_EXECUTION_CORE 交易执行 | 新增接口 | CTR-004 Order → SimulationBroker 消费（终局 CTR-007 → D_EXECUTION_CORE-oms 转换） | 端到端测试：权重→订单→执行 | 部分集成 |
| D_RISK 风控约束 | 修改现有接口 | DefaultEquityStrategy 消费 RiskLimits | 单元测试验证约束传递 | 部分集成 |
| D_REPORTING 分析 | 事件订阅 | CTR-P1-006 StrategyLifecycleEvent | 集成测试验证事件产出 | 待集成 |
| D_COMPLIANCE 合规 | 事件订阅 | CTR-P1-006 StrategyLifecycleEvent | 集成测试验证事件产出 | 待集成 |
| 策略自动发现 | 配置注入 | autodiscover_strategies() 扫描 strategies/ 目录 | 单元测试验证自动发现 | ✓ 完成 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | l05_portfolio_construction.yaml | `D:\ZephyrAlpha\architecture_model\layers\l05_portfolio_construction.yaml` | (1) module id `l05-layer-ssot` → `portfolio-core`（ARB-20 统一）(2) files 列表应反映 `strategies/` 子目录 (3) source_layer 修正为 D_SIGNAL | YAML 与蓝图/磁盘不一致 |
| 2 | blueprint_registry.yaml | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress 更新为 phase_1_partial | 进度同步 |
| 3 | cross_layer_contracts.yaml | `D:\ZephyrAlpha\architecture_model\cross_layer_contracts.yaml` | 确认 CTR-004/CTR-007/CTR-P1-006 状态 | 契约状态确认 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | YAML module id 与 blueprint-registry 命名不一致 | 高 | 中 | ARB-20 统一为 portfolio-core，YAML 待同步 | 风险 |
| 2 | source_layer 标注错误（D_FACTOR → 应为 D_SIGNAL） | 高 | 中 | 本蓝图已修正，YAML 待同步 | 风险 |
| 3 | YAML 文件路径与磁盘不一致 | 中 | 低 | 以磁盘为准，YAML 待同步 | 风险 |
| 4 | 策略注册冲突 | 低 | 中 | StrategyRegistry.register 检测重复 strategy_id 并抛出 ValueError | 风险 |
| 5 | CTR-004 → CTR-007 重构影响 D_EXECUTION_CORE | — | 高 | 需 Owner 审批 + D_EXECUTION_CORE 同步更新（ARB-20） | 负面后果 |
| 6 | D_RISK 不可用时策略无法运行 | — | 高 | 策略保持 Degraded 状态 | 负面后果 |
| 7 | DefaultEquityStrategy.generate_target_weights() 返回 list[Order] 与基类签名不一致 | 高 | 中 | 待 Phase 2 重构为返回 TargetPortfolio | 风险 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 4 | GOV-DOC-002 防幻觉路径映射已理解 | 能回答"某类文件该放哪" | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 7 | ✅ C轨已解除，可施工 | 确认 active 状态 | ☑ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 2 个 Phase |
| 施工模式 | 扩展 |
| 核心风险 | CTR-004 → CTR-007 重构影响 D_EXECUTION_CORE；C轨已解除 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板v4.1回填） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-L03-001 SynthesizedSignal 契约可用 | hard | ✓ | ✅ |
| 2 | MOD-L04-001 RiskLimits 契约可用 | hard | ✓ | ✅ |
| 3 | CTR-004 Order 契约定义存在 | hard | ✓ | ✅ |
| 4 | CTR-P1-006 StrategyLifecycleEvent 契约定义 | soft | 待定义 | ☐ |
| 5 | C轨已解除 | hard | 已解除 | ✅ |

### 16.3 实施步骤

#### 步骤 1：StrategyBase + StrategyMeta 定义

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 公共 API |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategy_base.py` |
| 验收标准 | StrategyBase 抽象类定义 generate_target_weights()；StrategyMeta 包含 strategy_id / name / strategy_type / version / description |
| 验证命令 | `python -m pytest D:\ZephyrAlpha\tests\unit\pf_core\ -k test_strategy_base -v` |
| G7 检查项 | 上游 D_SIGNAL/D_RISK 契约引用已列出；下游 CTR-004 Order 产出路径精确；回滚方案可执行 |

**状态**：✓ 完成

#### 步骤 2：StrategyRegistry 注册/发现/自动扫描

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 公共 API |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategy_registry.py` |
| 验收标准 | register 装饰器、get()、list_all()、count()、clear()、autodiscover_strategies() 均可正常工作；重复注册抛出 ValueError |
| 验证命令 | `python -m pytest D:\ZephyrAlpha\tests\unit\pf_core\ -k test_strategy_registry -v` |
| G7 检查项 | 策略注册表结构完整；strategies/ 目录扫描路径精确；重复注册拒绝已验证 |

**状态**：✓ 完成

#### 步骤 3：DefaultEquityStrategy（等权/信号加权）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 公共 API + §4.3 输入契约 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategies\default_equity_strategy.py` |
| 验收标准 | 等权模式：权重均匀分配；信号加权模式：按 SynthesizedSignal 加权；风控约束截断生效 |
| 验证命令 | `python -m pytest D:\ZephyrAlpha\tests\unit\pf_core\ -k test_default_equity -v` |
| G7 检查项 | D_SIGNAL SynthesizedSignal 输入正确；D_RISK RiskLimits 约束应用；CTR-004 Order 产出格式正确 |

**状态**：✓ 完成

#### 步骤 4：多策略支持（最小方差/风险平价）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 公共 API |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategies\` |
| 验收标准 | MinVarianceStrategy + RiskParityStrategy 继承 StrategyBase 并注册；权重计算正确 |
| 验证命令 | `python -m pytest D:\ZephyrAlpha\tests\unit\pf_core\ -k test_min_variance -v` |
| G7 检查项 | 新策略注册无冲突；权重计算数学正确性；风控约束应用 |

**状态**：✅ C轨已解除，可施工

#### 步骤 5：CTR-P1-006 StrategyLifecycleEvent 产出

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.4 输出契约 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\portfolio\strategy_lifecycle.py` |
| 验收标准 | StrategyLifecycleEvent Pydantic 模型定义；策略状态变更时产出事件 |
| 验证命令 | `python -m pytest D:\ZephyrAlpha\tests\unit\pf_core\ -k test_lifecycle_event -v` |
| G7 检查项 | 事件结构符合 CTR-P1-006；D_REPORTING/D_COMPLIANCE 可消费；幂等键包含 |

**状态**：✅ C轨已解除，可施工

#### 步骤 6：CTR-004 → CTR-007 重构（ARB-20）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.4 输出契约 + ARB-20 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pf_core\` |
| 验收标准 | generate_target_weights() 返回 TargetPortfolio(CTR-007) 而非 list[Order]；D_EXECUTION_CORE-oms 负责转换 |
| 验证命令 | `python -m pytest D:\ZephyrAlpha\tests\unit\pf_core\ -k test_target_portfolio -v` |
| G7 检查项 | CTR-007 结构定义；D_EXECUTION_CORE 同步更新；向后兼容方案 |

**状态**：✅ C轨已解除，可施工

#### 步骤 7：与 ex_core 集成测试

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §12 集成目标 |
| 产出位置 | `D:\ZephyrAlpha\tests\unit\pf_core\test_ex_core_integration.py` |
| 验收标准 | pf_core → ex_core 端到端：权重生成 → 订单生成 → SimulationBroker 消费 |
| 验证命令 | `python -m pytest D:\ZephyrAlpha\tests\unit\pf_core\test_ex_core_integration.py -v` |
| G7 检查项 | CTR-004 Order 格式与 ex_core 消费方一致；幂等键传递；风控约束传递 |

**状态**：✅ C轨已解除，可施工

#### 步骤 8：YAML 命名统一 + source_layer 修正

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §13 需要更新 |
| 产出位置 | `D:\ZephyrAlpha\architecture_model\layers\l05_portfolio_construction.yaml` |
| 验收标准 | module id 统一为 portfolio-core；files 列表反映 strategies/ 子目录；source_layer 修正为 D_SIGNAL |
| 验证命令 | `python D:\ZephyrAlpha\scripts\governance\d5_architecture\checkers\check_contract_code_drift.py` |
| G7 检查项 | YAML 与蓝图一致；YAML 与磁盘一致；cross_layer_contracts.yaml 状态同步 |

**状态**：待同步

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1-3 | 已完成，无需回滚 | — |
| 4 | 新策略权重计算错误 | 删除新策略文件，StrategyRegistry 自动排除未注册策略 |
| 5 | StrategyLifecycleEvent 结构不符合 D_REPORTING/D_COMPLIANCE 预期 | 删除事件文件，恢复策略为不产出事件状态 |
| 6 | CTR-007 重构导致 D_EXECUTION_CORE 不兼容 | 回退到 CTR-004 输出，D_PORTFOLIO_CORE 直接产出 Order |
| 7 | D_EXECUTION_CORE 集成测试失败 | 回退到步骤 3 状态，D_PORTFOLIO_CORE 仅产出 Order 不产出事件 |
| 8 | YAML 修改导致不一致 | `git checkout` 恢复 YAML 文件 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | strategy_base.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 2 | strategy_registry.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 3 | default_equity_strategy.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 4 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 5 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 6 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 7 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 8 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 等权分配算法 | 算法 | `weight = min(1.0/n, max_single_position)`，n = min(len(universe), max_positions) | `default_equity_strategy.py` |
| 2 | 信号加权分配算法 | 算法 | 按信号得分排序→取 top max_positions→按 abs(score)/total 归一化→截断至 max_single_position | `default_equity_strategy.py` |
| 3 | 增量订单生成 | 算法 | target_value = nav * weight；delta = target - current；过滤 |delta| < 1000 或 |qty| < 100 的微小订单 | `default_equity_strategy.py` |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/ -v` | 运行 D_PORTFOLIO_CORE 全部单元测试 | — | 12 tests passed |
| 2 | 命令 | `python -c "from zephyr.pf_core.strategy_base import autodiscover_strategies; autodiscover_strategies()"` | 策略自动发现 | `package_path`: 默认 `zephyr.pf_core.strategies` | 发现策略数 |
| 3 | 配置 | `RebalanceMode` | 权重分配模式 | `equal_weight` / `signal_weight` / `min_variance` / `risk_parity` | — |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | 策略注册冲突 | 重复 strategy_id | 检查 StrategyRegistry.list_all() | 修改 strategy_id | 重新注册 |
| 2 | 运行 | D_RISK 不可用 | RiskLimits 导入失败 | 检查 D_RISK 模块健康 | 策略保持 Degraded | D_RISK 恢复 |
| 3 | 运行 | 信号降级 | CTR-ERR-003 | 检查 D_SIGNAL 信号质量 | 降级为等权 | D_SIGNAL 恢复 |
| 4 | 运行 | 紧急冻结 | 安全事件 | 禁止策略执行 | — | 威胁解除 |

### 16.12 并发操作模型

本模块无并发操作——策略注册在启动时完成，运行时无动态注册。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 策略数量 | 1（DefaultEquityStrategy） | StrategyRegistry.count() |
| 标的池大小 | ~50 | target_weights 字典长度 |
| 权重计算延迟 | <10ms | generate_target_weights() 计时 |
| 订单生成延迟 | <5ms | _weights_to_orders() 计时 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L05-001 | 仅 1 种策略（等权/信号加权） | 新增最小方差/风险平价策略 | P1 | 策略需求 ≥ 3 | v3.0.0 | ✅ 可施工 |
| GAP-L05-002 | 无 StrategyLifecycleEvent 产出 | 实现 CTR-P1-006 事件产出 | P1 | D_REPORTING/D_COMPLIANCE 集成需求 | v3.0.0 | ✅ 可施工 |
| GAP-L05-003 | CTR-004 → CTR-007 重构 | 按 ARB-20 重构输出格式 | P0 | D_EXECUTION_CORE 集成 | v3.0.0 | ✅ 可施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | StrategyBase + StrategyRegistry + DefaultEquityStrategy | ⚠️ |
| v2.0.0 | 2 | 模板v3.3重构 | 章节重排+新增概述+标准锚点 | ⚠️ |
| v2.1.0 | 2 | 模板v4.1回填+ARB-20对齐 | 回填18个缺失章节+接口签名修正+依赖图对齐 | ⚠️ |
| v3.0.0 | 3 | C轨激活 | CTR-007重构+多策略+生命周期事件+6子模块 | ❌ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| MinVarianceStrategy | GAP-L05-001 | strategies/min_variance_strategy.py | Phase 2 | ✅ 可施工 |
| RiskParityStrategy | GAP-L05-001 | strategies/risk_parity_strategy.py | Phase 2 | ✅ 可施工 |
| StrategyLifecycleEvent | GAP-L05-002 | shared/contracts/portfolio/strategy_lifecycle.py | Phase 2 | ✅ 可施工 |
| TargetPortfolio (CTR-007) | GAP-L05-003 | strategy_base.py 重构 | Phase 2 | ✅ 可施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L05-01 | 策略扩展点设计 | A: 函数注册 / B: 继承+装饰器注册 | B | OCP-002 开闭原则，继承更利于类型检查 | 2026-05-05 |
| 2 | D-L05-02 | StrategyMeta 使用 @dataclass | A: Pydantic BaseModel / B: @dataclass(frozen=True) | B | frozen 语义简单，Phase 1 快速实现；KBG-0040 要求后续迁移 | 2026-05-05 |
| 3 | D-L05-03 | 输出契约 CTR-004 vs CTR-007 | A: 直接产出 CTR-004 Order / B: 产出 CTR-007 TargetPortfolio | A（当前）/ B（终局） | ARB-20 裁定终局为 CTR-007，当前 Phase 1 用 CTR-004 快速验证 | 2026-05-15 |
| 4 | D-L05-04 | 模板v4.1升级 | A: 保持v3.3 / B: 按v4.1升级 | B | v4.1模板合规；§0前移+§7/§15删除+§10拆分+铁律扩展 | 2026-05-15 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| StrategyBase | 策略抽象基类，OCP-002 扩展点 | StrategyRegistry | Registry 是注册表，Base 是策略基类 |
| StrategyMeta | 策略元数据（frozen dataclass） | StrategyBase | Meta 描述策略属性，Base 定义策略行为 |
| TargetPortfolio | CTR-007，D_PORTFOLIO_CORE 终局产出格式 | Order (CTR-004) | TargetPortfolio 是目标组合，Order 是委托指令；D_EXECUTION_CORE-oms 负责转换 |
| autodiscover | 自动扫描 strategies/ 目录注册策略 | register | register 是显式注册，autodiscover 是自动发现 |
| RebalanceMode | 权重分配模式枚举 | supported_modes | RebalanceMode 是代码枚举，supported_modes 是 StrategyMeta 字段 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | DefaultEquityStrategy.generate_target_weights() 返回 list[Order] 与基类签名 dict[str, float] 不一致 | 高 | Phase 1 快速实现绕过基类签名 | Phase 2 重构为返回 TargetPortfolio | §4.1 | 待解决 |
| 2 | StrategyMeta 使用 @dataclass 非 Pydantic BaseModel | 中 | Phase 1 快速实现 | 迁移为 Pydantic BaseModel | §5.1 #5 | 待解决 |
| 3 | 无 DefaultEquityStrategy 专项单元测试 | 中 | 测试覆盖不足 | 补充 test_default_equity_strategy.py | §9 | 待解决 |
| 4 | YAML module_id 与 blueprint-registry 命名不一致 | 中 | ARB-20 未同步到 YAML | YAML 待同步 | §13 #1 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ⚠️ 部分缺失 |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑 | ✅ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ✅ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | evolving | 中 | C轨激活+6子模块实现 | 当前仅 Phase 1 预研 |
| 接口契约 | evolving | 中 | CTR-007 重构完成 | 当前 CTR-004，待 ARB-20 重构 |
| 数据模型 | volatile | 低 | StrategyMeta 迁移 Pydantic | 当前 @dataclass |
| 施工步骤 | evolving | 中 | C轨已解除 | 步骤 4-7 可施工 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v1.0.0 | StrategyBase + StrategyRegistry + DefaultEquityStrategy | — | 已完成 |
| v2.0.0 | 模板v3.3重构 | v1.0.0 | 已完成 |
| v2.1.0 | 模板v4.1回填+ARB-20对齐 | v2.0.0 | 已完成 |
| v3.0.0 | CTR-007重构+多策略+生命周期事件+6子模块 | v2.1.0 | ✅ 可施工 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略——即使与前序文档重复也必须完整列出 | 关键信息缺失 |
| 3 | 蓝图必须是最终设计结果——不记录决策过程、不保存未选方案 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含——关键信息不能只写"详见XX" | 上下文缺失 |
| 10 | 删除文件必须遵守安全删除协议——禁止直接删除任何文件 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 蓝图与代码漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责混淆 |
| 16 | 术语表不可省略——每个蓝图 MUST 包含术语表 | 术语漂移 |
| 17 | 参考实现规格 vs 已实现代码重复——接口契约无法表达的逻辑规格MUST保留在§16.7；Pydantic模型字段定义等接口代码不重复 | 逻辑错误/双源漂移 |
| 18 | 对标验证表格 vs 对标散文——结构化对标表格MUST保留；长篇对标散文MUST删除 | 验证基准丢失/噪音 |
| 19 | SLO 必须定义——§5.4 服务水平目标不可省略 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略——§6.1 可观测性规格不可省略 | 故障无法发现 |
| 21 | 退化矩阵必须声明——§6.2 退化矩阵不可省略 | 部分失败时行为不可预测 |

---

## 蓝图拆分判定标准

### 判定流程

| 判定条件 | 结果 | 操作 |
|---------|------|------|
| 服务对象相同 + 变更频率同步 + 依赖关系重叠 | 原地升级 | 在 §17 容量升级附录中增量记录 |
| 有独立 module_id 前缀 | 拆分 | 创建子蓝图，belongs_to=本蓝图 |
| 有独立 Phase 路线图和交付节奏 | 拆分 | 同上 |
| 有独立依赖关系图（与主体 depends_on 交集<50%） | 拆分 | 同上 |
| 内容超100行且与主体无直接数据流 | 拆分 | 同上 |

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| D_PORTFOLIO_CORE 新增风险平价策略 | 原地升级 | 同属组合构建 |
| D_PORTFOLIO_CORE 新增回测引擎 | 拆分独立蓝图 | 回测≠组合构建 |
| D_PORTFOLIO_CORE 新增订单执行逻辑 | 拆分独立蓝图 | D_EXECUTION_CORE 已覆盖 |

---

## ⚠️ 安全删除协议

### 蓝图中的删除决策清单

本蓝图不涉及文件删除/废弃/迁移。

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | 给足缓冲期，deprecated 至少保持1个Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表、frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | YAML SSoT | — | — | `D:\ZephyrAlpha\architecture_model\layers\l05_portfolio_construction.yaml` | 本蓝图真源 |
| 10 | 系统依赖图 | — | v3.0.0 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 依赖对齐 |

---

## 项目中已有类似功能

无。D_PORTFOLIO_CORE 组合构建层在项目中无重复功能模块。

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | strategy_base.py | `D:\ZephyrAlpha\src\zephyr\pf_core\strategy_base.py` | 读取 | 已存在 |
| 2 | strategy_registry.py | `D:\ZephyrAlpha\src\zephyr\pf_core\strategy_registry.py` | 读取 | 已存在 |
| 3 | default_equity_strategy.py | `D:\ZephyrAlpha\src\zephyr\pf_core\strategies\default_equity_strategy.py` | 读取 | 已存在 |
| 4 | __init__.py | `D:\ZephyrAlpha\src\zephyr\pf_core\__init__.py` | 读取 | 已存在 |
| 5 | order.py（契约 SSoT） | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\order.py` | 读取 | 已存在 |
| 6 | l05_portfolio_construction.yaml | `D:\ZephyrAlpha\architecture_model\layers\l05_portfolio_construction.yaml` | 修改 | ARB-20 统一 + source_layer 修正 |
| 7 | blueprint_registry.yaml | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | construction_progress 更新 |
| 8 | cross_layer_contracts.yaml | `D:\ZephyrAlpha\architecture_model\cross_layer_contracts.yaml` | 修改 | 确认 CTR-004/CTR-007/CTR-P1-006 状态 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本蓝图的核心架构设计 | **本文档 §1-§10** | 已取代的旧蓝图 |
| 本模块的施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 本模块的接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| YAML 架构定义 | `D:\ZephyrAlpha\architecture_model\layers\l05_portfolio_construction.yaml` | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_reporting\blueprint.md` | §4 接口契约（CTR-P1-006） |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_compliance\blueprint.md` | §4 接口契约（CTR-P1-006） |
| Tier 2 | `D:\ZephyrAlpha\architecture_model\cross_layer_contracts.yaml` | §12 集成点 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategy_base.py` | §4 数据模型、§11 产出物路径 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\pf_core\strategy_registry.py` | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步（下游蓝图） | Tier 2 同步（集成系统） |
|---------|---------|---------------------|---------------------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |
