---
module_id: MOD-L04-001
submodule_path: src/zephyr/risk
title: "Risk Management Core 蓝图+施工图 — 风险管理引擎"
doc_type: blueprint
status: Active
version: "2.2.0"
layer: L2_domain
layer_name: risk_management
functional_domain: risk
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
last_updated: "2026-05-15"
last_verified: "2026-05-15"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/risk/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-14"
generation: 2
rule_form: structural
scope: module
stability: evolving
design_maturity: prototype
verifiability: manual
depends_on:
  - target: "MOD-L02-001"
    at: "CTR-002"
    why: "消费 FactorSignal"
  - target: "MOD-L03-001"
    at: "CTR-P1-015"
    why: "消费 SynthesizedSignal"
  - target: "MOD-L05-001"
    at: "CTR-004"
    why: "消费 Order"
  - target: "MOD-L06-001"
    at: "CTR-006"
    why: "消费 PositionSnapshot"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_risk\\blueprint.md"
    section: "全篇"
    why: "本蓝图即SSoT"
summary: "D_RISK 风险管理引擎——止损执行+风控校验+Kill Switch 熔断。Phase 1 部分实现：OCP 扩展点骨架+默认实现+止损引擎。"
tags: [risk-management, l04, phase-1-partial, stop-loss, kill-switch]
priority: P0
runtime_plane: hot
ssot_yaml: "docs/03_modules/_domain_risk/blueprint.md"
responsibility_domain: 
build_status: generated
---

> ⚠️ **业务层已开放，可施工** — D_RISK 属于 C 轨业务层，当前业务层处于冻结状态。
> 任何新增施工、功能扩展、接口变更均需 Owner 明确批准后方可执行。
> 本蓝图仅做审查、回填、压缩、对齐，不触发任何代码变更。

> actual_disk_path: src/zephyr/risk/ (10 .py files)
> module_id: MOD-L04-001 | version: 2.2.0 | status: Active | layer: L2_domain
> generation: 2 | construction_progress: partially_implemented

# Risk Management Core 蓝图+施工图 — 风险管理引擎

> **真源声明**：本蓝图是 ZephyrAlpha 风险管理体系的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 风险管理引擎——止损执行+风控校验+Kill Switch 熔断。核心职责：风险限额计算、Pre/Post-trade 风控校验、4 种止损模式评估与触发、Kill Switch 熔断与人工恢复。当前规模 10 个代码文件（5 ABC 基类 + 5 默认实现），目标容量 20+ 风控策略 × 100/s 并发校验。上游消费 D_FACTOR FactorSignal、D_SIGNAL SynthesizedSignal、D_EXECUTION_CORE PositionSnapshot，下游被 D_PORTFOLIO_CORE 组合构建、D_EXECUTION_CORE 交易执行、D_FRONTEND 人机界面消费。

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

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules MOD-L04-001`
> 以下手写内容保留职责描述（depgraph 无此信息），文件列表以 depgraph 为准。

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L04-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:-----:|
| 1 | `risk_limits.py` | §3.1 | 风险限额数据模型+RiskLimitsCalculator ABC | 已实现 |
| 2 | `risk_manager_base.py` | §3.1 | RiskCheckResult/RiskReport 数据类+3个ABC基类 | 已实现 |
| 3 | `risk_manager.py` | §3.1 | RiskManagerBase ABC+RiskLimits/RiskLimitViolationError/RiskDashboardSnapshot/RiskMetricsReport | 已实现 |
| 4 | `risk_validator.py` | §3.1 | RiskValidator ABC+ViolatedConstraint/ViolationDetail | 已实现 |
| 5 | `stop_loss.py` | §3.1 | evaluate_stop_loss/trigger_kill_switch/reset_kill_switch+StopLossResult | 已实现 |
| 6 | `implementations/default_position_limit_checker.py` | §3.1 | PositionLimitCheckerBase 默认实现 | 已实现 |
| 7 | `implementations/default_risk_limits_calculator.py` | §3.1 | RiskLimitsCalculator 默认实现 | 已实现 |
| 8 | `implementations/default_risk_manager_orchestrator.py` | §3.1 | RiskManagerOrchestratorBase 默认实现 | 已实现 |
| 9 | `implementations/default_risk_validator.py` | §3.1 | RiskValidator 默认实现 | 已实现 |
| 10 | `implementations/default_stop_loss_engine.py` | §3.1 | StopLossEngineBase 默认实现 | 已实现 |

> YAML SSoT 列出 10 个文件在根目录，实际磁盘将 5 个 default_* 实现放入 `implementations/` 子目录。

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| §0.1 文件清单 10 个文件全部存在于磁盘 | `ls D:\ZephyrAlpha\src\zephyr\risk\` | ☐ |
| implementations/ 子目录包含 5 个 default_* 文件 | `ls D:\ZephyrAlpha\src\zephyr\risk\implementations\` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v2.2.0 (模板v4.1合规回填) | 5 ABC + 5 默认实现 + 4 种止损模式 | RiskDashboardSnapshot 产出、D_PORTFOLIO_CORE/D_EXECUTION_CORE 集成测试、INV-001 性能验证、测试目录 | Phase 2 待施工 |

---

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L04-001`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L04-001` 的 14 个 file 节点 | prototype | `extract_depgraph.py --modules MOD-L04-001` |
| 数据流图 (dataflow) | 1 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 76 个决策节点 / 2 个决策层 | design | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L04-001 | MOD-L04-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 14 文件 | 10 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 设计背景与目标

### 1.1 背景

量化交易系统缺乏统一风控层——止损靠人工判断，限额无硬约束，Kill Switch 无自动化触发。D_RISK 风险管理层填补此空白，提供实时风控与止损执行能力，作为 D_PORTFOLIO_CORE 组合构建的约束提供者。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 事前风控：订单发出前校验限额 | Pre-trade 校验覆盖率 100% |
| 2 | ✅ 包含 | 事后风控：成交后检查风险敞口 | Post-trade 校验覆盖率 100% |
| 3 | ✅ 包含 | 止损执行：固定比例/移动/时间/波动率止损 | 4 种止损模式全部实现 |
| 4 | ✅ 包含 | Kill Switch：熔断触发延迟 < 1ms（INV-001） | 延迟测试通过 |
| 5 | ✅ 包含 | Kill Switch 人工确认后方可恢复 | 恢复流程需人工确认 |
| 6 | ❌ 排除 | 信号生成 | D_SIGNAL 职责 |
| 7 | ❌ 排除 | 订单生成 | D_PORTFOLIO_CORE 职责 |
| 8 | ❌ 排除 | 订单执行 | D_EXECUTION_CORE 职责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| C 轨 hot plane——低延迟要求 | Kill Switch 延迟 < 1ms，禁止阻塞 I/O |
| 多策略并发风控检查 | 需幂等键（INV-007）防竞争 |
| 日终盈亏检查触发 kill_switch | INV-004 每日亏损硬限 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策+风控参数审批 | 设计+施工 | D_RISK 为 Immutable Core（GOV-AI-001），变更需 Owner+KB 决策记录 |
| D_PORTFOLIO_CORE 组合构建 | RiskLimits 产出 | 集成 | CTR-003 消费方 |
| D_EXECUTION_CORE 交易执行 | 风控阻断+持仓数据 | 集成 | CTR-ERR-004 消费方 |
| D_FRONTEND 人机界面 | 风控仪表板数据 | 集成 | CTR-P1-008 消费方 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 风控校验 | 5 ABC + 5 默认实现 | 20+ 风控策略 | 策略数量不足 | P1 |
| 止损模式 | 4 种模式已实现 | 4 种模式 + 性能验证 | INV-001 延迟未验证 | P0 |
| 集成 | 无集成测试 | D_PORTFOLIO_CORE/D_EXECUTION_CORE/D_FRONTEND 端到端集成 | 集成测试缺失 | P1 |
| 监控 | 无可观测性指标 | 全量指标+告警 | §6.1 未实现 | P1 |
| 测试 | 测试目录不存在 | 覆盖率 > 90% | 测试完全缺失 | P0 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| Pre-trade 校验 | D_PORTFOLIO_CORE 下单请求 | validate_order→检查限额→pass/reject | RiskCheckResult |
| 止损触发 | 价格跌破止损线 | evaluate_stop_loss→trigger_kill_switch→阻断所有订单 | StopLossResult + Kill Switch 激活 |
| Kill Switch 恢复 | 人工确认 | reset_kill_switch→验证确认信息→恢复交易 | 交易恢复 |
| 日终亏损超限 | daily_pnl_check 失败 | daily_pnl_check→触发 kill_switch→阻断 | RiskReport + Kill Switch 激活 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 风险限额计算 | 基于 FactorSignal 和 SynthesizedSignal 计算限额约束集 | 本模块 |
| 2 | ✅ 包含 | 止损评估与触发 | 固定比例/移动/时间/波动率四种止损模式 | 本模块 |
| 3 | ✅ 包含 | Kill Switch 激活/重置 | 熔断触发 + 人工确认恢复 | 本模块 |
| 4 | ✅ 包含 | Pre-trade 风控校验 | 订单发出前校验限额 | 本模块 |
| 5 | ✅ 包含 | Post-trade 风控校验 | 成交后检查风险敞口 | 本模块 |
| 6 | ❌ 排除 | 信号生成 | D_SIGNAL 职责 | D_SIGNAL |
| 7 | ❌ 排除 | 订单生成 | D_PORTFOLIO_CORE 职责 | D_PORTFOLIO_CORE |
| 8 | ❌ 排除 | 订单执行 | D_EXECUTION_CORE 职责 | D_EXECUTION_CORE |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | RiskLimitsCalculator | 风险限额计算（OCP 扩展点） | FactorSignal, SynthesizedSignal | 同步调用 |
| 2 | RiskValidator | Pre/Post-trade 风控校验（OCP 扩展点） | Order, PositionSnapshot | 同步调用 |
| 3 | RiskManagerOrchestrator | 风控总管编排（OCP 扩展点） | RiskLimitsCalculator, RiskValidator, PositionLimitChecker, StopLossEngine | 同步调用 |
| 4 | StopLossEngine | 止损评估与触发（OCP 扩展点） | PositionSnapshot | 同步调用 |
| 5 | PositionLimitChecker | 仓位限额检查（OCP 扩展点） | PositionSnapshot | 同步调用 |
| 6 | RiskManagerBase | 风控管理器 ABC | Kill Switch 状态 | 同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_FACTOR FactorSignal | 限额计算 → RiskLimits | D_PORTFOLIO_CORE 组合构建 | Pydantic Model |
| 2 | D_SIGNAL SynthesizedSignal | 参数调整 → RiskValidator | D_PORTFOLIO_CORE 组合构建 | Pydantic Model |
| 3 | D_PORTFOLIO_CORE Order | Pre-trade 校验 → pass/reject | D_EXECUTION_CORE 交易执行 | Pydantic Model |
| 4 | D_EXECUTION_CORE PositionSnapshot | Post-trade 校验 → RiskDashboardSnapshot | D_FRONTEND 人机界面 | Pydantic Model |
| 5 | Kill Switch 触发 | 熔断 → 阻断所有订单 | D_PORTFOLIO_CORE/D_EXECUTION_CORE | 状态信号 |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| Normal | 风控校验通过 | Normal | 限额未超 |
| Normal | 风控校验失败 | Warning | 限额超限但未达 HALT |
| Normal | Kill Switch 触发 | Halted | INV-001/INV-004 条件满足 |
| Warning | 风控校验恢复 | Normal | 限额恢复 |
| Warning | Kill Switch 触发 | Halted | INV-001/INV-004 条件满足 |
| Halted | 人工确认恢复 | Normal | 人工确认 + 限额恢复 |

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。
> ⚠️ 代码中 risk_manager_base.py 使用了 `@dataclass(frozen=True)` 定义 RiskCheckResult/RiskReport，与 KBG-0040 不一致——Phase 2 需迁移为 Pydantic BaseModel。

### 4.1 公共 API

```python
class RiskManagerOrchestratorBase:
    def pre_trade_check(self, order: Any, limits: Any, positions: Any) -> RiskCheckResult: ...
    def post_trade_check(self, fill: Any, positions: Any) -> RiskCheckResult: ...
    def daily_pnl_check(self, daily_pnl: Decimal, loss_limit: Decimal) -> RiskCheckResult: ...
    def aggregate_report(self) -> RiskReport: ...

class RiskValidator:
    def validate_order(self, symbol: str, target_weight: float, current_holdings: Dict[str, float], limits: Any) -> List[ViolationDetail]: ...
    def validate_portfolio(self, holdings: Dict[str, float], market_values: Dict[str, float], total_nav: Decimal, limits: Any) -> List[ViolationDetail]: ...

class StopLossEngineBase:
    def evaluate(self, symbol: str, entry_price: Decimal, current_price: Decimal, position_qty: Decimal, rules: dict[str, Any]) -> RiskCheckResult: ...
    def get_stop_price(self, symbol: str) -> Optional[Decimal]: ...

class RiskLimitsCalculator:
    def calculate(self, positions: Dict[str, float], market_values: Dict[str, float], total_nav: Decimal, factor_signals: Optional[Dict[str, float]] = None) -> RiskLimits: ...
```

### 4.2 数据模型

```python
class RiskLevel(str, Enum):
    WARNING = "warning"
    HALT = "halt"

class RiskValidationResult(BaseModel):
    passed: bool = Field(..., description="是否通过风控校验")
    risk_level: Optional[RiskLevel] = Field(default=None, description="风险级别")
    violation_details: Optional[str] = Field(default=None, description="违规详情")
    idempotency_key: str = Field(..., description="幂等键（INV-007）")

class RiskDashboardSnapshot(BaseModel):
    total_exposure: float = Field(..., description="总敞口")
    daily_pnl: float = Field(..., description="日盈亏")
    kill_switch_active: bool = Field(..., description="Kill Switch 是否激活")
    risk_limits: "RiskLimits" = Field(..., description="当前风险限额")

class ViolationDetail(BaseModel):
    constraint: str = Field(..., description="违规约束类型")
    description: str = Field(..., description="违规描述")
    limit_value: Decimal = Field(..., description="限额值")
    actual_value: Decimal = Field(..., description="实际值")
    severity: str = Field(default="HALT", description="HALT | WARNING")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `pre_trade_check()` | `order`, `limits`, `positions` | ✅ | Order 契约（CTR-004）+ RiskLimits + PositionSnapshot |
| `validate_order()` | `symbol`, `target_weight`, `current_holdings`, `limits` | ✅ | symbol 非空，weight ∈ [0,1] |
| `evaluate()` | `symbol`, `entry_price`, `current_price`, `position_qty`, `rules` | ✅ | price > 0，qty > 0 |
| `trigger_kill_switch()` | `reason` | ✅ | 非空字符串 |
| `reset_kill_switch()` | `confirmation` | ✅ | {confirmed_by, confirmed_at, override_reason} |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `pre_trade_check()` | `RiskCheckResult(passed=True)` | `RiskCheckResult(passed=False, severity=HALT)` / CTR-ERR-004 |
| `validate_order()` | `[]`（无违规） | `[ViolationDetail(severity=HALT)]` |
| `evaluate()` | `RiskCheckResult(passed=True)` | `RiskCheckResult(passed=False, severity=HALT)` |
| `trigger_kill_switch()` | `{status, event_id, reason, scope, requires_manual_reset}` | Kill Switch 已激活时忽略重复触发 |
| `reset_kill_switch()` | `True` | 未人工确认时拒绝重置 |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/方法 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名字段/方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | INV-001: Kill Switch 延迟 < 1ms | 纯内存操作，禁止 I/O |
| 2 | INV-004: 每日亏损硬限 | 日终盈亏检查触发 kill_switch |
| 3 | INV-007: 幂等键 | 所有跨层调用携带 idempotency_key |
| 4 | HALT 级别违规禁止降级为 WARNING | 硬编码禁止 |
| 5 | kill_switch 触发后 MUST 阻断所有订单 | 直到人工确认恢复 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 风控策略数 | 5 | 20 | 100 | ✅ | OCP 扩展点支持无限扩展 |
| 并发校验请求 | 10/s | 100/s | 1000/s | ✅ | 幂等键 + 无状态设计 |
| Kill Switch 延迟 | <1ms | <1ms | <1ms | ✅ | 纯内存操作，无 I/O |

### 5.3 迁移

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | ~~YAML SSoT files 列表~~ | 已删除（迁移至35域架构） | — | 旧14层架构YAML已废弃 |
| 2 | RiskCheckResult/RiskReport @dataclass | `src/zephyr/risk/risk_manager_base.py` | 同文件 | 迁移为 Pydantic BaseModel（KBG-0040） | Phase 2 执行 |

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | Kill Switch 可用率 | 99.99% | 监控 | kill_switch_trigger_success/total | 99.99% | 每月允许 4.3min 不可用 | <99.99% 触发 P0 |
| 延迟 | Kill Switch 触发延迟 | <1ms | 基准测试 | p99_trigger_latency | <1ms | 0（硬约束） | >0.5ms 触发 P1 |
| 可维护性 | MTTR | <30min | 故障记录 | — | — | — | — |
| 可观测性 | 指标覆盖率 | 100% | 指标审计 | — | — | — | — |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | `@dataclass` 用于数据模型 | Pydantic BaseModel | KBG-0040 强制 Pydantic V2 |
| 2 | 编码模式 | Kill Switch 中包含 I/O 操作 | 纯内存操作 | INV-001 延迟 < 1ms |
| 3 | 编码模式 | HALT 降级为 WARNING | 硬编码禁止降级 | 资金安全 |
| 4 | 导入源 | `from zephyr.pf_core.* import *` | 通过 CTR-003/CTR-004 契约消费 | 分层约束——risk 不直接导入 pf_core 实现 |
| 5 | 导入源 | `from zephyr.ex_core.* import *` | 通过 CTR-006 契约消费 | 分层约束——risk 不直接导入 ex_core 实现 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Kill Switch 延迟超标（>1ms） | INV-001 监控 | 告警 + 人工介入 | D_PORTFOLIO_CORE/D_EXECUTION_CORE 订单无法阻断 |
| 2 | HALT 级别违规被降级为 WARNING | 安全约束硬编码检查 | 代码层禁止降级 | 资金安全风险 |
| 3 | 多策略并发风控检查竞争 | 幂等键冲突检测 | INV-007 幂等键重试 | 风控校验结果不一致 |
| 4 | Kill Switch 触发后订单仍通过 | 订单阻断监控 | 熔断重试 + 告警 | 资金安全风险 |
| 5 | 每日亏损超限未触发 kill_switch | INV-004 日终检查 | 人工确认 + 紧急熔断 | 资金安全风险 |
| 6 | RiskDashboardSnapshot 产出失败 | 产出监控 | 降级为空快照 + 告警 | D_FRONTEND 仪表板数据缺失 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| risk_check_total | Counter | 自动埋点 | — | — |
| risk_check_failed_total | Counter | 自动埋点 | >5/min | P2 |
| kill_switch_trigger_latency_ms | Histogram | 自动埋点 | >0.5ms | P1 |
| kill_switch_active | Gauge | 自动埋点 | active=true | P0 |
| daily_pnl_breach | Counter | 自动埋点 | >0 | P0 |
| risk_limits_violation_total | Counter | 自动埋点 | >10/min | P1 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| RiskLimitsCalculator | 无（硬依赖） | 限额计算 | 阻断所有新订单 | 计算器恢复 |
| RiskValidator | 无（硬依赖） | 风控校验 | 阻断所有新订单 | 校验器恢复 |
| StopLossEngine | 无（硬依赖） | 止损评估 | 触发 Kill Switch | 引擎恢复 |
| RiskDashboardSnapshot 产出 | 风控校验（核心） | 仪表板数据 | 空快照 + 告警 | 产出恢复 |
| Kill Switch | 无（硬依赖） | 熔断 | 全系统冻结 | 人工确认恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | HALT 降级为 WARNING 的代码逻辑风险 | 高 | 安全约束硬编码，禁止降级 | 代码审查 + 单元测试 |
| 2 | Kill Switch 延迟超标 | 高 | INV-001 持续监控 + 纯内存操作 | 延迟基准测试 |
| 3 | Kill Switch 未授权恢复 | 高 | 人工确认机制 + 审计日志 | 恢复流程测试 |
| 4 | 风控参数被篡改 | 中 | 参数签名校验 + 变更审计 | 参数完整性测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | RiskValidator, RiskLimitsCalculator, StopLossEngine, PositionLimitChecker | 限额校验通过/拒绝、4种止损模式触发、Kill Switch 触发/重置、HALT 降级防护 | 覆盖率 > 90% |
| 2 | 集成测试 | D_RISK↔D_PORTFOLIO_CORE, D_RISK↔D_EXECUTION_CORE | CTR-003 RiskLimits 产出→D_PORTFOLIO_CORE 消费、CTR-ERR-004 阻断→D_EXECUTION_CORE | 端到端通过 |
| 3 | 性能测试 | Kill Switch 延迟 | INV-001 延迟 < 1ms | 延迟测试通过 |
| 4 | 安全测试 | HALT 降级防护 | HALT 违规无法降级为 WARNING | 降级测试失败=通过 |

> ⚠️ 当前测试目录 `tests/risk/` 不存在——违反防幻觉铁律 #14（新代码必测）。

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-L00-001 | 可选 | CTR-001 NormalizedMarketData | v1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_data\blueprint.md` |
| MOD-L02-001 | 必须 | CTR-002 FactorSignal | v1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` |
| MOD-L03-001 | 必须 | CTR-P1-015 SynthesizedSignal | v1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_signal\blueprint.md` |
| MOD-L05-001 | 必须 | CTR-004 Order（消费） | v1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\portfolio-core\blueprint.md` |
| MOD-L06-001 | 必须 | CTR-006 PositionSnapshot（消费） | v1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` |
| MOD-L08-001 | 可选 | CTR-P1-008 RiskDashboardSnapshot（产出） | v1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_frontend\hmi_core\blueprint.md` |
| MOD-FEEDBACK_LOOP | 可选 | CTR-P1-013 Telemetry（产出） | v1.0.0 | 风控告警→线4 |

> **对齐说明**：dependency_path_panorama §3.10 列出 CTR-001/CTR-002/CTR-006 为输入，CTR-003/CTR-P1-011/CTR-P1-013 为输出。蓝图 §10.1 补充了 CTR-P1-015（代码 __init__.py 已声明消费）和 CTR-004（pre-trade 校验必需）。CTR-P1-011 RiskMetricsReport 产出待 Phase 2 实现。

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-L04-001` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

> **依赖图子模块差异**：dependency_path_panorama §3.10 列出 4 子模块（l04-metrics/l04-limits/l04-stop-loss/l04-monitor），实际代码为 1 个模块（MOD-L04-001）含 5 ABC + 5 实现。待业务层开放后按需拆分。

### 10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**：

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| RiskLimitsCalculator | DefaultRiskManagerOrchestrator | RiskLimits | 函数调用 |
| DefaultRiskValidator | DefaultRiskManagerOrchestrator | ViolationDetail[] | 函数调用 |
| DefaultPositionLimitChecker | DefaultRiskManagerOrchestrator | RiskCheckResult | 函数调用 |
| DefaultStopLossEngine | DefaultRiskManagerOrchestrator | RiskCheckResult | 函数调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 单模块，依赖关系简单 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防漂移 | CI门禁 | validate_path_alignment.py | 待接入CI | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 否 | 蓝图中无临时时态内容 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | 防虚假进度 | pytest+mypy+ruff | pytest/mypy/ruff | 测试目录不存在 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` | 本文件（含设计和施工指引） |
| 接口定义 | `D:\ZephyrAlpha\src\zephyr\risk\*.py` | ABC 基类 + 数据模型 |
| 默认实现 | `D:\ZephyrAlpha\src\zephyr\risk\implementations\` | 5 个 default_* 实现类 |
| 契约 SSoT | `D:\ZephyrAlpha\src\zephyr\shared\contracts\risk\` | 风险相关契约定义 |
| 错误类型 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\errors.py` | CTR-ERR-004 RiskLimitViolationError |
| 测试代码 | `D:\ZephyrAlpha\tests\risk\` | 单元测试 + 集成测试（待创建） |
| 交易门禁（规则真源） | `D:\ZephyrAlpha\src\zephyr\gates\g7-position-limits.yaml` + `g8-leverage.yaml` | G10持仓限制 + G11杠杆限制——消费 CTR-003 RiskLimits 契约（实现归属 MOD-GATE_ENGINE） |
| 风险仪表盘快照契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\risk\risk_dashboard_snapshot.py` | 风险仪表盘数据快照（归属 MOD-INF-016） |
| 风险指标契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\risk\risk_metrics.py` | 风险指标计算结果（归属 MOD-INF-016） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_PORTFOLIO_CORE 组合构建 | 产出接口 | CTR-003 RiskLimits → D_PORTFOLIO_CORE 消费 | D_PORTFOLIO_CORE 风控约束生效 |
| D_EXECUTION_CORE 交易执行 | 产出接口 + 错误阻断 | CTR-ERR-004 阻断订单 + CTR-006 消费持仓 | 违规订单被阻断 |
| D_FRONTEND 人机界面 | 产出接口 | CTR-P1-008 RiskDashboardSnapshot | 仪表板显示风控数据 |
| Kill Switch 全链路 | 状态信号 | 触发逻辑 → D_PORTFOLIO_CORE/D_EXECUTION_CORE 阻断 | 全链路熔断测试 |

### 集成状态

| 目标 | 状态 | 说明 |
|------|------|------|
| D_PORTFOLIO_CORE 组合构建 | 部分集成 | CTR-003 RiskLimits 产出，D_PORTFOLIO_CORE 消费 |
| D_EXECUTION_CORE 交易执行 | 部分集成 | CTR-ERR-004 阻断订单，CTR-006 消费持仓 |
| D_FRONTEND 人机界面 | 待集成 | CTR-P1-008 RiskDashboardSnapshot |
| Kill Switch 全链路 | 骨架就位 | 触发逻辑已实现，人工恢复流程待完善 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | ~~YAML SSoT~~ | 已删除（迁移至35域架构） | — | 旧14层架构YAML已废弃 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress 更新为 phase_1_partial | 进度同步 |
| 3 | 跨层契约 | `D:\ZephyrAlpha\architecture_model\cross_layer_contracts.yaml` | 确认 CTR-003/CTR-ERR-004/CTR-P1-008 状态 | 契约状态确认 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | §3.10 子模块定义与实际代码对齐 | 4子模块 vs 1模块差异 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | HALT 降级为 WARNING 的代码逻辑风险 | 低 | 高 | 安全约束硬编码，禁止降级 | 风险 |
| 2 | Kill Switch 延迟超标 | 低 | 高 | INV-001 持续监控 + 纯内存操作 | 风险 |
| 3 | 多策略并发风控检查竞争 | 中 | 中 | INV-007 幂等键 + idempotency_key | 风险 |
| 4 | YAML 与磁盘文件路径不一致 | 高 | 低 | 以磁盘为准，YAML 待同步 | 风险 |
| 5 | D_PORTFOLIO_CORE/D_EXECUTION_CORE依赖本层产出，未产出则风控/阻断失效 | — | 高 | Phase 2 优先实现产出 | 负面后果 |
| 6 | Kill Switch失效则资金安全无保障 | — | 高 | INV-001 持续监控 + 纯内存操作 | 负面后果 |
| 7 | 代码 [AI_AUTONOMY]=ai_modifiable 与 GOV-AI-001 声明 D_RISK=Immutable Core 不一致 | 高 | 高 | 代码头部需修正为 human_gated，变更需 Owner+KB 决策记录 | 风险 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §0 对齐 + §1-§14 架构 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 5 | D_RISK 为 Immutable Core（GOV-AI-001），变更需 Owner+KB 决策记录 | 确认审批链 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 2 个 Phase |
| 施工模式 | 扩展 |
| 核心风险 | Kill Switch 延迟超标（INV-001） |
| 目标 generation | 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | D_FACTOR FactorSignal 契约已定义 | hard | ✅ | ✅ |
| 2 | D_SIGNAL SynthesizedSignal 契约已定义 | hard | ✅ | ✅ |
| 3 | D_PORTFOLIO_CORE Order 契约已定义 | hard | ✅ | ✅ |
| 4 | D_EXECUTION_CORE PositionSnapshot 契约已定义 | hard | ✅ | ✅ |

### 16.3 实施步骤

#### 步骤 1：OCP 扩展点骨架 + 默认实现 + 止损引擎（Phase 1）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\risk\` |
| 验收标准 | 5 个 ABC 基类 + 5 个 default_* 实现 + 4 种止损模式 + Kill Switch |
| 验证命令 | `python -m pytest tests/risk/ -k "test_risk" -v` |
| G7 检查项 | 上游文件全部列出？下游产出物路径精确？回滚方案可执行？ |
| AI 自治范围 | human_gated（Immutable Core）——需 Owner 审批 |
| 检查点 | 10 个 .py 文件存在且非空 |

**状态**：✓ 完成

#### 步骤 2：RiskDashboardSnapshot + 集成测试 + 性能验证（Phase 2）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2, §4.4 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\risk\` |
| 验收标准 | CTR-P1-008 产出 + D_PORTFOLIO_CORE/D_EXECUTION_CORE 集成测试通过 + INV-001 延迟 < 1ms |
| 验证命令 | `python -m pytest tests/risk/ -k "test_integration or test_performance" -v` |
| G7 检查项 | 上游文件全部列出？下游产出物路径精确？回滚方案可执行？ |
| AI 自治范围 | human_gated（Immutable Core）——需 Owner 审批 |
| 检查点 | RiskDashboardSnapshot 产出 + 集成测试通过 |

**状态**：待实现

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | OCP 扩展点骨架编译失败 | 删除新增文件，恢复 __init__.py |
| 2 | 集成测试失败 | 回退到 Phase 1 状态，修复后重试 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | OCP 扩展点骨架存在 | `ls D:\ZephyrAlpha\src\zephyr\risk\*.py` exit 0 | 完成 | ☐ |
| 2 | 默认实现存在 | `ls D:\ZephyrAlpha\src\zephyr\risk\implementations\` exit 0 | 完成 | ☐ |
| 3 | RiskDashboardSnapshot 存在 | `grep "RiskDashboardSnapshot" risk_manager.py` exit 0 | 完成 | ☐ |
| 4 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 5 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 6 | 告警已配置 | §6.1 每项阈值有告警规则 | 就绪 | ☐ |
| 7 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 8 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 9 | 文档已更新 | §13 需要更新的文件全部更新 | 就绪 | ☐ |
| 10 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 止损价计算算法 | 算法 | fixed_pct: `entry_price * (1 - stop_loss_pct)`; trailing: `max(highest, current) * (1 - trailing_pct)`; time_based: 强制平仓; volatility: `entry_price - (vol * mult * entry_price)` | `implementations/default_stop_loss_engine.py` |
| 2 | IV 调整逻辑 | 算法 | factor_signals 中 \|v\| > 3.0 视为 unstable，每个收紧 10%，最低收紧到 50% | `implementations/default_risk_limits_calculator.py` |
| 3 | VaR 估算 | 算法 | 持仓数≤2: concentration×0.05; ≤5: ×0.03; >5: ×0.02; 空仓: 0.02 | `implementations/default_risk_limits_calculator.py` |
| 4 | Kill Switch 触发判定 | 协议 | halt_violations 非空 → 触发; 触发后必须人工确认恢复 | `risk_validator.py` + `stop_loss.py` |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/risk/ -v` | 运行全部测试 | — | exit 0 = 通过 |
| 2 | 命令 | `python -m pytest tests/risk/ -k "test_integration" -v` | 集成测试 | — | exit 0 = 通过 |
| 3 | 命令 | `python -m pytest tests/risk/ -k "test_performance" -v` | 性能测试（INV-001） | — | 延迟 < 1ms |
| 4 | 配置 | StopLossRules | 止损规则配置 | method/stop_loss_pct/trailing_pct/max_hold_days/vol_multiplier/lookback_days | 见 default_stop_loss_engine.py |
| 5 | 配置 | DefaultRiskLimitsCalculator 参数 | 限额默认值 | max_single_position=0.10/max_gross_leverage=1.0/max_sector_concentration=0.30/max_drawdown_limit=0.20/var_confidence=0.95 | 见 default_risk_limits_calculator.py |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | ABC 基类编译失败 | 类型注解错误 | `python -c "from zephyr.risk import *"` | 修复类型注解 | import 成功 |
| 2 | 运行 | Kill Switch 误触发 | 参数配置错误 | 检查 RiskLimits 参数 + kill_switch_active 状态 | reset_kill_switch(confirmation) | 人工确认后恢复 |
| 3 | 运行 | Kill Switch 未触发 | INV-001/INV-004 监控告警 | 检查 daily_pnl + violations 列表 | 手动 trigger_kill_switch | 人工确认 |
| 4 | 运行 | 紧急冻结 | 安全事件 | trigger_kill_switch(reason, scope="all") | 所有交易暂停 | 威胁解除后人工恢复 |
| 5 | 运行 | 紧急旁路 | D_RISK 阻塞 CI | 跳过 D_RISK + 降级为无风控模式 | — | D_RISK 恢复后取消旁路 |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 多策略同时调用 pre_trade_check | idempotency_key（INV-007） | 幂等——相同 key 返回缓存结果 | 以首次结果为准 |
| Kill Switch 触发与恢复竞争 | kill_switch_active 状态锁 | 触发优先于恢复 | 触发覆盖恢复 |
| 多 AI Session 同时修改风控参数 | lock_files.py 文件锁 | 后写者等待 | FIFO |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 风控策略数 | 5（5 个 OCP 扩展点） | 扩展点注册表 |
| 并发校验 QPS | 10/s | 压测 |
| Kill Switch 延迟 | <1ms | 基准测试 |
| 代码文件数 | 10 | 磁盘文件计数 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L04-001 | RiskDashboardSnapshot 未实现 | 实现 CTR-P1-008 产出 | P1 | Phase 2 启动 | v2.2.0 | 待施工 |
| GAP-L04-002 | D_PORTFOLIO_CORE/D_EXECUTION_CORE 集成测试缺失 | 编写集成测试 | P1 | Phase 2 启动 | v2.2.0 | 待施工 |
| GAP-L04-003 | INV-001 性能未验证 | 延迟基准测试 | P0 | Phase 2 启动 | v2.2.0 | 待施工 |
| GAP-L04-004 | 测试目录不存在 | 创建 tests/risk/ | P0 | 立即 | v2.2.0 | 待施工 |
| GAP-L04-005 | 代码 AI_AUTONOMY 与 GOV-AI-001 不一致 | 修正代码头部为 human_gated | P1 | 立即 | v2.2.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v2.0.0 | 2 | 基线 | OCP 扩展点 + 默认实现 | ✅ |
| v2.1.0 | 2 | 模板v3.5升级 | §0前移+§7/§15删除+§10拆分 | ⚠️ |
| v2.2.0 | 2 | 模板v4.1合规回填 | 17个缺失章节回填+依赖图对齐+压缩 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| RiskDashboardSnapshot | GAP-L04-001 | `risk_dashboard.py` | Phase 2 | 待施工 |
| D_PORTFOLIO_CORE/D_EXECUTION_CORE 集成测试 | GAP-L04-002 | `tests/risk/test_integration.py` | Phase 2 | 待施工 |
| INV-001 延迟基准测试 | GAP-L04-003 | `tests/risk/test_performance.py` | Phase 2 | 待施工 |
| 单元测试 | GAP-L04-004 | `tests/risk/test_*.py` | Phase 2 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L04-01 | OCP 扩展点设计——5 个 ABC 基类 + 注册机制 | A: 单一大类 / B: OCP 扩展点 / C: 策略模式 | B | 开闭原则——新增风控策略不修改已有代码 | 2026-05-05 |
| 2 | D-L04-02 | 默认实现放入 implementations/ 子目录 | A: 根目录平铺 / B: 子目录隔离 | B | 接口与实现分离，根目录保持简洁 | 2026-05-05 |
| 3 | D-L04-03 | Kill Switch 纯内存操作，禁止 I/O | A: 允许日志 I/O / B: 纯内存 | B | INV-001 延迟 < 1ms 约束 | 2026-05-05 |
| 4 | D-L04-04 | HALT 级别违规硬编码禁止降级 | A: 可配置降级 / B: 硬编码禁止 | B | 资金安全——降级 = 资金安全风险 | 2026-05-05 |
| 5 | D-L04-06 | 模板v3.5升级 | A: 保持旧结构 / B: 按v3.5升级 | B | §0前移+§7/§15删除+§10拆分 | 2026-05-15 |
| 6 | D-L04-07 | 模板v4.1合规回填 | A: 仅回填 / B: 回填+压缩+对齐 | B | 17个缺失章节+依赖图对齐+压缩 | 2026-05-15 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| Kill Switch | 全仓熔断机制，触发后阻断所有订单直到人工恢复 | 止损 | 止损是单标的级别，Kill Switch 是全组合级别 |
| HALT | 风控违规最高级别，必须阻断操作 | WARNING | HALT=硬阻断不可降级；WARNING=告警可继续 |
| RiskLimits | 风险限额约束集（CTR-003），包含多项限额参数 | RiskCheckResult | RiskLimits=限额定义；RiskCheckResult=校验结果 |
| Pre-trade | 订单发出前的风控校验 | Post-trade | Pre-trade=事前阻断；Post-trade=事后检查 |
| INV-001 | Kill Switch 延迟 < 1ms 的不变量约束 | INV-004 | INV-001=延迟约束；INV-004=每日亏损硬限 |
| OCP 扩展点 | 开闭原则抽象基类，新增策略不修改已有代码 | 策略模式 | OCP=通过注册机制扩展；策略模式=通过注入切换 |
| idempotency_key | 幂等键（INV-007），防止并发重复执行 | check_id | idempotency_key=跨层幂等；check_id=单次检查标识 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 测试目录不存在 | 高 | Phase 1 未创建测试 | 创建 tests/risk/ + 单元测试 | 铁律#14 | 待解决 |
| 2 | 代码 AI_AUTONOMY=ai_modifiable 与 GOV-AI-001=Immutable Core 不一致 | 高 | 代码头部未同步注册表声明 | 修正代码头部为 human_gated | GOV-AI-001 | 待解决 |
| 3 | RiskCheckResult/RiskReport 使用 @dataclass 而非 Pydantic BaseModel | 中 | Phase 1 快速实现 | 迁移为 Pydantic BaseModel | KBG-0040 | 待解决 |
| 4 | dependency_path_panorama §3.10 列出 4 子模块但实际为 1 模块 | 中 | 架构设计与实现未同步 | 待业务层开放后按需拆分或更新依赖图 | §10.2 | 待解决 |
| 5 | INV-001 Kill Switch 延迟未验证 | 高 | 无性能测试 | 创建延迟基准测试 | INV-001 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ☐ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ☐ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ☐ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文（概述→§0→§1-§18→术语表→自检清单） | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答"X和Y的区别是什么" | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些设计可改哪些不可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | evolving | 中 | Phase 2 完成后 → stable | OCP 扩展点设计已验证，但集成未完成 |
| 接口契约 | evolving | 中 | D_PORTFOLIO_CORE/D_EXECUTION_CORE 集成通过后 → stable | ABC 接口已定义，实际消费方未验证 |
| 数据模型 | volatile | 低 | Pydantic 迁移完成后 → evolving | @dataclass 需迁移为 Pydantic BaseModel |
| 施工步骤 | evolving | 中 | Phase 2 完成后 → stable | Phase 1 已完成，Phase 2 待施工 |
| Kill Switch | stable | 高 | INV-001 验证通过后 → frozen | 核心安全机制，设计稳定 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v2.0.0 | OCP 扩展点 + 默认实现 + 4 种止损模式 | — | 已完成 |
| v2.1.0 | 模板 v3.5 升级（§0 前移 + §7/§15 删除） | v2.0.0 | 已完成 |
| v2.2.0 | 模板 v4.1 合规回填 + 依赖图对齐 + 压缩 | v2.1.0 | 已完成 |
| v2.3.0 | RiskDashboardSnapshot + 集成测试 + 性能验证（Phase 2） | v2.2.0 | 待施工 |
| v3.0.0 | Pydantic 迁移 + 子模块拆分（如需） | v2.3.0 | 待施工 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略 | 信息缺失 |
| 3 | 蓝图必须是最终设计结果 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索/导入失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 实现与蓝图漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | 职责混乱 |
| 16 | 术语表不可省略——每个蓝图 MUST 包含术语表 | 术语漂移 |
| 17 | 参考实现规格 vs 已实现代码重复——接口契约无法表达的逻辑规格MUST保留在§16.7；Pydantic模型字段定义等接口代码不重复 | 逻辑错误/双源漂移 |
| 18 | 对标验证表格 vs 对标散文——结构化对标表格MUST保留；长篇对标散文MUST删除 | 验证缺失/噪音 |
| 19 | SLO 必须定义——§5.4 服务水平目标不可省略 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略——§6.1 可观测性规格不可省略 | 故障无法发现 |
| 21 | 退化矩阵必须声明——§6.2 退化矩阵不可省略 | 部分失败时行为不可预测 |

### 蓝图拆分判定标准

**判定流程**：
1. 当前蓝图是否包含 ≥2 个独立职责域？→ 否 → 不拆分
2. 各职责域是否各自有独立的消费者和演进节奏？→ 否 → 不拆分
3. 拆分后各蓝图是否各自自包含（接口+依赖+施工）？→ 是 → 拆分

| 判定示例 | 职责域数量 | 消费者独立？ | 演进独立？ | 结论 |
|---------|:---:|:---:|:---:|------|
| 风险管理引擎（本蓝图） | 1 | 否 | 否 | 不拆分 |
| 假设：风控校验+止损引擎 | 2 | 是 | 是 | 拆分为 D_RISK-RiskValidation + D_RISK-StopLoss |
| 假设：风控校验+Kill Switch | 2 | 否 | 否 | 不拆分（职责紧密） |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。风险管理模块为纯新增/扩展型模块，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 + MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限——D_RISK=Immutable Core |
| 9 | 本蓝图 | — | — | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` | 本蓝图即SSoT |

---

## 项目中已有类似功能

无。D_RISK 风险管理层是项目中唯一的风控执行层，无重复功能。

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 风险管理模块 | `D:\ZephyrAlpha\src\zephyr\risk\` | 读取 | 确认文件存在 |
| 2 | 默认实现目录 | `D:\ZephyrAlpha\src\zephyr\risk\implementations\` | 读取 | 确认文件存在 |
| 3 | 契约 SSoT | `D:\ZephyrAlpha\src\zephyr\shared\contracts\risk\` | 读取 | 确认契约状态 |
| 4 | 本蓝图 | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` | 读取 | 本蓝图即SSoT |
| 5 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | construction_progress 同步 |
| 6 | 跨层契约 | `D:\ZephyrAlpha\architecture_model\cross_layer_contracts.yaml` | 修改 | 确认契约状态 |
| 7 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 修改 | §3.10 子模块对齐 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| D_RISK 核心架构设计 | **本文档 §1-§10** | 旧蓝图 |
| D_RISK 施工步骤 | **本文档 §16** | 旧施工图 |
| D_RISK 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\portfolio-core\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 2 | `D:\ZephyrAlpha\docs\03_modules\_domain_frontend\hmi_core\blueprint.md` | §12 集成点 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\risk\` | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步（下游蓝图） | Tier 2 同步（集成系统） |
|---------|---------|---------------------|---------------------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |
