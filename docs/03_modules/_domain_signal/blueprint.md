---
module_id: MOD-L03-001
submodule_path: src/zephyr/signal
title: "Signal Generation Core 蓝图+施工图 — 信号工厂·策略生命周期管理"
doc_type: blueprint
status: Active
version: "3.0.0"
layer: L2_domain
layer_name: signal_generation
functional_domain: research
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-12"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/signal_ashare/ + src/zephyr/signal_fundamental/ + src/zephyr/signal_quality/"
last_updated: "2026-07-05"
last_verified: "2026-07-05"
generation: 3
belongs_to: ""
parent_module: ""
codification_level: L1
codification_at: "2026-07-05"
rule_form: structural
scope: module
stability: evolving
verifiability: manual
depends_on:
  - target: MOD-L02-001
    at: §10
    why: 因子计算结果输入(CTR-002 FactorSignal)
  - target: MOD-INF-015
    at: §10
    why: 信号生成监控
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_signal\\blueprint.md"
    section: "§1"
    why: "本蓝图即SSoT"
summary: "信号工厂蓝图——4个OCP扩展点+2个默认实现+策略生命周期管理(7阶段)+策略池容量管理+灰度发布。Phase B骨架已就位，业务层已开放，可施工。"
ssot_yaml: "docs/03_modules/_domain_signal/blueprint.md"
tags: [signal-generation, l03, c-track, ocp-extension-point, signal-factory]
priority: P0
runtime_plane: hot
# ============================================================
# 子模块清单（蓝图内部使用，不进入blueprint_registry）
# 命名体系：D-SIGNAL-XX（依赖图设计态子模块ID）
# 蓝图module_id保持MOD-L03-001（域级单一ID，SSoT）
# ============================================================
submodules:
  # ===== P0 核心骨架 =====
  - id: D-SIGNAL-01
    name: Synthesizer
    description: "信号合成+权重分配（SignalSynthesizerBase OCP扩展点）"
    priority: P0
    construction_status: partially_implemented
    gates: []
    corresponds_to: "signal_fundamental/synth/signal_synthesizer.py"
  - id: D-SIGNAL-02
    name: Aggregator
    description: "信号聚合（SignalAggregatorBase OCP扩展点）"
    priority: P0
    construction_status: partially_implemented
    gates: []
    corresponds_to: "signal_fundamental/gen/aggregator_base.py"
  - id: D-SIGNAL-03
    name: Capital Allocator
    description: "资金分配（CapitalAllocatorBase OCP扩展点）"
    priority: P0
    construction_status: partially_implemented
    gates: []
    corresponds_to: "signal_fundamental/capital/capital_allocator.py"
  - id: D-SIGNAL-04
    name: Degradation Monitor
    description: "信号退化检测（DegradationMonitorBase OCP扩展点）"
    priority: P0
    construction_status: partially_implemented
    gates: []
    corresponds_to: "signal_fundamental/gen/aggregator_base.py"
  # ===== P1 策略管理 =====
  - id: D-SIGNAL-14
    name: Strategy Lifecycle Manager
    description: "策略生命周期管理（7状态机：创意→原型→回测→模拟→实盘→监控→优化）"
    priority: P1
    construction_status: not_started
    gates: []
    corresponds_to: "services/strategy_lifecycle/"
  - id: D-SIGNAL-115
    name: 策略模板库
    description: "趋势跟踪+价值回归+市场中性+套利等模板"
    priority: P1
    construction_status: not_started
    gates: []
    corresponds_to: "services/strategy_templates/"
  - id: D-SIGNAL-120
    name: 统一策略接口定义器
    description: "统一策略初始化+数据处理+信号生成接口"
    priority: P1
    construction_status: not_started
    gates: []
    corresponds_to: "services/strategy_interface/"
  - id: D-SIGNAL-140
    name: 策略灰度发布
    description: "回测→实盘灰度发布（5%→20%→100%）"
    priority: P1
    construction_status: not_started
    gates: []
    corresponds_to: "services/strategy_rollout/"
  - id: D-SIGNAL-151
    name: 策略池容量引导器
    description: "池容量监控+入场退池自动化"
    priority: P1
    construction_status: not_started
    gates: []
    corresponds_to: "services/strategy_pool/"
  # ===== P2 A股特色 =====
  - id: D-SIGNAL-21
    name: A股主力行为分析
    description: "主力资金行为分析+大单检测+主力成本线"
    priority: P2
    construction_status: not_started
    gates: []
    corresponds_to: "signal_ashare/services/mainforce/"
  - id: D-SIGNAL-58
    name: 双引擎融合决策
    description: "量化+主观双引擎融合决策"
    priority: P2
    construction_status: not_started
    gates: []
    corresponds_to: "signal_ashare/services/dual_engine/"
# ============================================================
# 策略生命周期七阶段状态机
# ============================================================
strategy_lifecycle:
  states:
    - IDEA                     # 创意（研究员提出）
    - PROTOTYPE                # 原型（代码可运行）
    - BACKTESTED               # 已回测（通过回测引擎验证）
    - SIMULATED                # 已模拟（模拟盘验证）
    - LIVE                     # 实盘（实盘运行）
    - MONITORED                # 监控中（运行时指标追踪）
    - OPTIMIZED                # 已优化（参数调优完成）
  rollout_gates:
    - stage: "BACKTESTED→SIMULATED"
      condition: "回测Sharpe>0.5 + OOS Sharpe>70%IS"
    - stage: "SIMULATED→LIVE"
      condition: "模拟盘偏差<30% + 运行>20交易日"
    - stage: "LIVE→MONITORED"
      condition: "实盘运行>5交易日"
# ============================================================
# 策略池容量管理
# ============================================================
strategy_pool:
  max_active_strategies: 20    # 活跃策略上限
  max_total_strategies: 50     # 总策略上限（含休眠）
  rollout_phases: [0.05, 0.20, 1.0]  # 灰度发布：5%→20%→100%
responsibility_domain: 
design_maturity: prototype
build_status: generated
---

> ✅ **业务层已开放——可施工**
> 本蓝图所属 C 轨业务层已开放，AI 可自主施工。
> 开工条件已满足：Owner 已解除 C 轨占位禁令，基础设施已就绪。
> 任何修改需 Owner 审批。

> module_id: MOD-L03-001 | version: 3.0.0 | status: active | domain: signal
> actual_disk_path: src/zephyr/signal_ashare/ + src/zephyr/signal_fundamental/ + src/zephyr/signal_quality/ | generation: 3 | construction_progress: partially_implemented
> 子模块体系: D-SIGNAL-01~164（蓝图内部编号，不进blueprint_registry）

# Signal Generation Core 蓝图+施工图 — 信号工厂·策略生命周期管理

## 概述

本蓝图描述 ZephyrAlpha **信号工厂**——从因子信号到可执行交易信号的标准化转换 + 策略全生命周期管理。核心职责包括：

- **信号生成核心**：4个OCP扩展点（SignalAggregatorBase / CapitalAllocatorBase / DegradationMonitorBase / SignalSynthesizerBase）+ 2个默认实现
- **策略管理**：策略生命周期7阶段状态机（创意→原型→回测→模拟→实盘→监控→优化）+ 策略池容量管理 + 灰度发布（5%→20%→100%）
- **A股特色**：主力行为分析、资金线形态、短线选股、日内买卖点、市场情绪、板块轮动等完整A股交易决策链

当前规模 4个Base类 + 2个Default实现 + 3个信号子域（signal_fundamental/signal_ashare/signal_quality），Phase B骨架已就位。上游依赖 D_DATA（CTR-001）和 D_FACTOR（CTR-002 FactorSignal），下游被 D_PORTFOLIO_CORE（消费 CTR-P1-015 SynthesizedSignal）和 D_RISK（消费 CTR-P1-003 + CTR-ERR-003）使用。

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

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L03-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | `signal_fundamental/__init__.py` | §3.1 | 基础信号域包入口+re-export | 已实现 |
| 2 | `signal_fundamental/gen/aggregator_base.py` | §3.1 | SignalAggregatorBase + CapitalAllocatorBase + DegradationMonitorBase | 已实现 |
| 3 | `signal_fundamental/gen/implementations/default_signal_aggregator.py` | §3.1 | DefaultSignalAggregator | 已实现 |
| 4 | `signal_fundamental/capital/capital_allocator.py` | §3.1 | CapitalAllocatorBase 兼容导出（re-export only） | 已实现 |
| 5 | `signal_fundamental/capital/default_capital_allocator.py` | §3.1 | DefaultCapitalAllocator + AllocationMethod | 已实现 |
| 6 | `signal_fundamental/capital/capital_allocation_result.py` | §4.2 | CapitalAllocationResult 数据模型 | 已实现 |
| 7 | `signal_fundamental/synth/signal_synthesizer.py` | §3.1 | SignalSynthesizerBase | 已实现 |
| 8 | `signal_fundamental/combiner/synthesized_signal.py` | §4.2 | SynthesizedSignal 数据模型 | 已实现 |
| 9 | `signal_fundamental/pipeline.py` | §3.1 | 信号生成管线 | 已实现 |
| 10 | `signal_fundamental/strategy/capital_allocator.py` | §3.1 | 策略层资金分配（re-export） | 已实现 |
| 11 | `signal_fundamental/strategy/implementations/default_capital_allocator.py` | §3.1 | 策略层默认资金分配实现 | 已实现 |
| 12 | `signal_ashare/__init__.py` | §3.1 | A股信号子域包入口（占位） | 占位 |
| 13 | `signal_ashare/{core,api,services,models,infrastructure,_extensions}/__init__.py` | — | A股信号子域占位子包（6个） | 占位 |
| 14 | `signal_quality/__init__.py` | §3.1 | 信号质量子域包入口（占位） | 占位 |
| 15 | `signal_quality/{core,api,services,models,infrastructure,_extensions}/__init__.py` | — | 信号质量子域占位子包（6个） | 占位 |

> **注**：v2.2.0中§0.1声明的7个文件路径（`src/zephyr/signal/`）与实际代码路径（`src/zephyr/signal_fundamental/`）不一致，v3.0.0已修正。完整文件清单SSoT：`python scripts/governance/extract_depgraph.py --modules MOD-L03-001`

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | `ls D:\ZephyrAlpha\src\zephyr\signal_fundamental\` 逐文件核对 | ☐ |
| 蓝图描述的类名 = 代码中的类名 | `grep "class" D:\ZephyrAlpha\src\zephyr\signal_fundamental\*.py` | ☐ |
| 4 个 Base 类均存在 | `grep "class.*Base" aggregator_base.py signal_synthesizer.py` | ☐ |
| 2 个 Default 实现均存在 | `grep "class Default" implementations/*.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v2.2.0 (模板v4.1回填) | 4 Base + 2 Default + 1 re-export | CTR-008 SignalQualityMetrics; DegradationMonitor 实现 | 已解除 |

---

## §1 设计背景与目标

### 1.1 背景

D_FACTOR Alpha Factor 层产出因子信号后，需要标准化聚合、合成、资金分配和降级监控机制，将多因子信号转化为可执行的交易信号。当前痛点：无统一信号聚合框架、无资金分配标准化、无信号退化检测。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 信号聚合标准化 | SignalAggregatorBase OCP 扩展点可用 |
| 2 | ✅ 包含 | 资金分配标准化 | CapitalAllocatorBase OCP 扩展点可用 |
| 3 | ✅ 包含 | 降级监控 | DegradationMonitorBase 可检测信号退化 |
| 4 | ✅ 包含 | 信号合成 | SignalSynthesizerBase 可合成多源信号 |
| 5 | ✅ 包含 | 信号质量度量 | CTR-008 SignalQualityMetrics 可产出 |
| 6 | ❌ 排除 | 因子计算 | → D_FACTOR Alpha Factor (MOD-L02-001) |
| 7 | ❌ 排除 | 组合构建 | → D_PORTFOLIO_CORE Portfolio Construction |
| 8 | ❌ 排除 | 风险评估 | → D_RISK Risk Management |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 可施工 | AI 不可自主修改本层代码，需 Owner 审批 |
| 信号输出必须标准化 | 下游 D_PORTFOLIO_CORE/D_RISK 依赖统一格式 |
| OCP 扩展点接口不可变 | 新策略只加不改，Base 类接口冻结 |
| 交易时段运行 | 信号生成延迟<50ms |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策+C轨占位解除 | 设计+施工 | 审批权限 |
| D_PORTFOLIO_CORE Portfolio | 合成信号格式 | 消费 | CTR-P1-015 契约 |
| D_RISK Risk | 分配结果+降级警告 | 消费 | CTR-P1-003/CTR-ERR-003 契约 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 信号聚合 | DefaultSignalAggregator 已实现 | 多策略聚合（IC加权/ML驱动） | IC加权为占位，ML未实现 | P2 |
| 降级监控 | DegradationMonitorBase ABC 已定义 | DefaultDegradationMonitor 实现 | 无 Default 实现 | P1 |
| 信号质量 | 无 | CTR-008 SignalQualityMetrics | 完全缺失 | P1 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 因子聚合 | D_FACTOR 产出 FactorSignal | aggregate()→加权组合→normalize→SynthesizedSignal | CTR-P1-015 |
| 资金分配 | 多策略 SynthesizedSignal 就绪 | allocate()→权重计算→CapitalAllocationResult | CTR-P1-003 |
| 退化检测 | 合成信号置信度下降 | evaluate()→退化判定→SignalDegradationWarning | CTR-ERR-003 |
| 空信号兜底 | 因子信号为空 | _empty_signal()→is_degraded=True | 空信号+退化标记 |
| 策略上线 | 新策略通过回测+模拟 | 灰度发布5%→20%→100%→MONITORED | 策略状态=LIVE |
| 策略退役 | 策略持续亏损 | 监控触发→策略池退池→DORMANT | 策略状态=DORMANT |

### 1.8 子模块清单（D-SIGNAL-XX 体系）

> **命名体系说明**：子模块编号 D-SIGNAL-XX 是**蓝图内部编号**，用于门禁挂载和契约落点，**不进入 blueprint_registry**。蓝图 module_id 保持 MOD-L03-001（域级单一ID，SSoT）。详见 frontmatter `submodules` 字段。完整164子模块清单待后续补录到蓝图内部（当前仅列出P0/P1核心子模块）。

#### 1.8.1 P0 核心骨架（信号生成4个OCP扩展点）

| 子模块ID | 名称 | 职责 | 优先级 | 建设状态 |
|---------|------|------|:------:|:-------:|
| D-SIGNAL-01 | Synthesizer | 信号合成+权重分配（SignalSynthesizerBase） | P0 | partially_implemented |
| D-SIGNAL-02 | Aggregator | 信号聚合（SignalAggregatorBase） | P0 | partially_implemented |
| D-SIGNAL-03 | Capital Allocator | 资金分配（CapitalAllocatorBase） | P0 | partially_implemented |
| D-SIGNAL-04 | Degradation Monitor | 信号退化检测（DegradationMonitorBase） | P0 | partially_implemented |

#### 1.8.2 P1 策略管理

| 子模块ID | 名称 | 职责 | 优先级 | 建设状态 |
|---------|------|------|:------:|:-------:|
| D-SIGNAL-14 | Strategy Lifecycle Manager | 策略生命周期7状态机 | P1 | not_started |
| D-SIGNAL-115 | 策略模板库 | 趋势跟踪+价值回归+市场中性+套利模板 | P1 | not_started |
| D-SIGNAL-120 | 统一策略接口定义器 | 统一策略初始化+数据处理+信号生成接口 | P1 | not_started |
| D-SIGNAL-140 | 策略灰度发布 | 回测→实盘灰度发布（5%→20%→100%） | P1 | not_started |
| D-SIGNAL-151 | 策略池容量引导器 | 池容量监控+入场退池自动化 | P1 | not_started |
| D-SIGNAL-152 | 策略基类接口版本化器 | on_bar/on_signal签名变更版本管理 | P1 | not_started |
| D-SIGNAL-153 | 策略运行时异常隔离器 | 单策略异常不影响其他策略 | P1 | not_started |

#### 1.8.3 P2 A股特色信号子域

| 子模块ID | 名称 | 职责 | 优先级 | 建设状态 |
|---------|------|------|:------:|:-------:|
| D-SIGNAL-21 | A股主力行为分析 | 主力资金行为+大单检测+主力成本线 | P2 | not_started |
| D-SIGNAL-22~30 | 资金线形态系列 | 资金线形态+短线选股+日内买卖点 | P2 | not_started |
| D-SIGNAL-31~40 | 市场情绪系列 | 市场情绪+板块轮动+集合竞价 | P2 | not_started |
| D-SIGNAL-41~50 | 涨停基因评估系列 | 涨停基因+游资接力情绪+量化短线强度 | P2 | not_started |
| D-SIGNAL-58 | 双引擎融合决策 | 量化+主观双引擎融合决策 | P2 | not_started |

> **注**：完整164子模块清单（D-SIGNAL-01~164）待后续补录到蓝图内部。本蓝图仅列出P0/P1核心子模块，P2子模块按需补充。

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 信号聚合 | SignalAggregatorBase + DefaultSignalAggregator | 本模块 |
| 2 | ✅ 包含 | 资金分配 | CapitalAllocatorBase + DefaultCapitalAllocator | 本模块 |
| 3 | ✅ 包含 | 降级监控 | DegradationMonitorBase（在 aggregator_base.py） | 本模块 |
| 4 | ✅ 包含 | 信号合成 | SignalSynthesizerBase（在 signal_synthesizer.py） | 本模块 |
| 5 | ✅ 包含 | 信号质量度量 | CTR-008 SignalQualityMetrics（规划） | 本模块 |
| 6 | ❌ 排除 | 因子计算 | → D_FACTOR Alpha Factor | MOD-L02-001 |
| 7 | ❌ 排除 | 组合优化 | → D_PORTFOLIO_CORE Portfolio Construction | MOD-L04-001 |
| 8 | ❌ 排除 | 风险控制 | → D_RISK Risk Management | MOD-L05-001 |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | SignalAggregatorBase | 因子信号聚合抽象基类（OCP扩展点D_SIGNAL-AGG） | CTR-002 FactorSignal | 同步调用 |
| 2 | CapitalAllocatorBase | 资金分配抽象基类（OCP扩展点D_SIGNAL-ALC） | CTR-P1-015 SynthesizedSignal | 同步调用 |
| 3 | DegradationMonitorBase | 信号退化检测抽象基类（OCP扩展点D_SIGNAL-DEG） | CTR-P1-015 SynthesizedSignal | 同步调用 |
| 4 | SignalSynthesizerBase | 多源信号合成抽象基类（OCP扩展点D_SIGNAL-SYN） | CTR-002 FactorSignal | 同步调用 |
| 5 | DefaultSignalAggregator | 等权/置信度/IC加权聚合 | SignalAggregatorBase | 继承 |
| 6 | DefaultCapitalAllocator | 等权/信号/Sharpe/RiskParity分配 | CapitalAllocatorBase | 继承 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_FACTOR FactorSignal | SignalAggregatorBase.aggregate() → 加权组合 | SignalSynthesizerBase | FactorSignal → SynthesizedSignal |
| 2 | SynthesizedSignal | CapitalAllocatorBase.allocate() → 资金分配 | D_RISK Risk Management | CapitalAllocationResult (CTR-P1-003) |
| 3 | SynthesizedSignal | DegradationMonitorBase.evaluate() → 退化检测 | D_PORTFOLIO_CORE, D_RISK | SignalDegradationWarning (CTR-ERR-003) |
| 4 | D_FACTOR FactorSignal | SignalSynthesizerBase.synthesize() → 合成+归一化 | D_PORTFOLIO_CORE Portfolio Construction | SynthesizedSignal (CTR-P1-015) |

### 3.3 状态生命周期

本模块无状态机。所有 Base 类为无状态 ABC，每次调用独立执行。

---

## §4 接口契约

> 强制 Pydantic V2 BaseModel（KBG-0040），禁止 @dataclass。实际契约类型为 codegen 生成的 frozen dataclass（CTR-002/CTR-P1-015），蓝图只保留接口签名。

### 4.1 公共 API

| 类 | 关键方法签名 |
|----|-------------|
| SignalAggregatorBase | `aggregate(factor_signals: list[FactorSignal], symbol: str, idempotency_key: str) → SynthesizedSignal` |
| SignalAggregatorBase | `normalize_signal(raw: float, clip_range: tuple[float, float]) → float` |
| CapitalAllocatorBase | `allocate(signals: list[SynthesizedSignal], idempotency_key: str) → CapitalAllocationResult` |
| DegradationMonitorBase | `evaluate(signals: list[SynthesizedSignal]) → list[SignalDegradationWarning]` |
| SignalSynthesizerBase | `synthesize(factor_signals: list[FactorSignal], symbol: str, as_of_timestamp: datetime, weights: Optional[Dict[str, float]]) → SynthesizedSignal` |
| SignalSynthesizerBase | `normalize_signal(raw: float) → float` |
| SignalSynthesizerBase | `direction_from_value(value: float, threshold: float) → str` |
| SignalSynthesizerBase | `default_idempotency_key(symbol: str, as_of_timestamp: datetime) → str` |

### 4.2 数据模型

| 模型 | 基类 | 核心字段 | 契约ID |
|------|------|---------|--------|
| SynthesizedSignal | frozen dataclass | signal_id, symbol, as_of_timestamp, signal_value, signal_direction, confidence, idempotency_key | CTR-P1-015 |
| CapitalAllocationResult | frozen dataclass | allocation_date, total_allocated_weight, allocation_method, idempotency_key, strategy_allocations | CTR-P1-003 |
| SignalDegradationWarning | frozen dataclass | symbol, degradation_type, severity, affected_signals | CTR-ERR-003 |
| FactorSignal | frozen dataclass | factor_id, symbol, raw_value, normalized_value, confidence, is_valid, as_of_date, idempotency_key | CTR-002 |
| AllocationMethod | str, Enum | EQUAL, SIGNAL, SHARPE, RISK_PARITY | — |

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `aggregate()` | `factor_signals` | ✅ | 非空 list[FactorSignal] |
| `aggregate()` | `symbol` | ✅ | 非空 str |
| `aggregate()` | `idempotency_key` | ✅ | 非空 str（INV-007） |
| `allocate()` | `signals` | ✅ | 非空 list[SynthesizedSignal] |
| `allocate()` | `idempotency_key` | ✅ | 非空 str |
| `evaluate()` | `signals` | ✅ | 非空 list[SynthesizedSignal] |
| `synthesize()` | `factor_signals` | ✅ | 非空 list[FactorSignal] |
| `synthesize()` | `symbol` | ✅ | 非空 str |
| `synthesize()` | `as_of_timestamp` | ✅ | datetime |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `aggregate()` | SynthesizedSignal (CTR-P1-015) | _empty_signal() 兜底（is_degraded=True） |
| `allocate()` | CapitalAllocationResult (CTR-P1-003) | _empty_allocation() 兜底 |
| `evaluate()` | list[SignalDegradationWarning] | 空列表（无退化） |
| `synthesize()` | SynthesizedSignal (CTR-P1-015) | _empty_signal() 兜底 |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| Base 类 ABC 方法签名 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 新增 Default 实现类 | ✅ 向后兼容 | 不影响已有消费者 |
| 新增 AllocationMethod 枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| CTR-P1-015/CTR-P1-003/CTR-ERR-003 字段 | ❌ 破坏性 | 需 Owner 审批 + 通知 D_PORTFOLIO_CORE/D_RISK |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | SignalAggregatorBase 为 OCP 扩展点 | 新聚合策略只加不改 |
| 2 | CapitalAllocatorBase 为 OCP 扩展点 | 新分配策略只加不改 |
| 3 | DegradationMonitorBase 为 OCP 扩展点 | 新降级检测策略只加不改 |
| 4 | SignalSynthesizerBase 为 OCP 扩展点 | 新合成策略只加不改 |
| 5 | 信号输出必须标准化 | SynthesizedSignal / CapitalAllocationResult |
| 6 | Python 3.12+ / Pydantic V2 | 项目统一技术栈 |
| 7 | signal_value 归一化范围 | [-3.0, 3.0] |
| 8 | 幂等键（INV-007） | 所有合成/分配操作必须关联 idempotency_key |
| 9 | max_per_strategy 上限 | 0.40（DefaultCapitalAllocator） |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| Base 类数量 | 4 | 8 | 20 | ✅ | 新增 Base 类按 OCP 扩展 |
| Default 实现 | 2 | 6 | 20 | ✅ | implementations/ 目录扩展 |
| 因子信号输入 | <100/symbol | 500/symbol | — | ✅ | 聚合算法优化 |
| 合成信号输出 | <50/symbol | 200/symbol | — | ✅ | 批量合成 |

### 5.3 迁移/废弃方案

本蓝图不涉及迁移。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 信号生成成功率 | 99.9% | 产出计数/调用计数 | 信号生成成功率 | 99.9% | 每月允许失败<0.1% | 成功率<99.5% |
| 延迟 | 信号生成延迟 | P95<50ms | generation_latency_ms | P95延迟 | <50ms | — | P95>100ms |
| 可维护性 | 新策略接入时间 | <1天 | OCP扩展点验证 | — | — | — | — |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | Base 类方法签名变更 | 新增 Default 实现类 | OCP 扩展点接口冻结 |
| 2 | 编码模式 | look-ahead bias | 仅使用 as_of_timestamp 前数据 | 门禁约束 GATE-F |
| 3 | 编码模式 | 因子权重动态调整为负值 | 做空在 D_PORTFOLIO_CORE 组合层面处理 | 门禁约束 GATE-F |
| 4 | 导入源 | zephyr.risk.* / zephyr.pf_core.* | 仅消费 CTR 契约类型 | 分层约束，signal 不依赖 risk/pf_core |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 因子信号为空列表 | aggregate() 入口校验 | 返回 _empty_signal() 兜底 | D_PORTFOLIO_CORE 收到空信号 |
| 2 | 合成信号置信度过低 | DegradationMonitorBase.evaluate() | 发出 SignalDegradationWarning (CTR-ERR-003) | D_PORTFOLIO_CORE/D_RISK 收到退化警告 |
| 3 | 资金分配输入为空 | allocate() 入口校验 | 返回 _empty_allocation() 兜底 | D_RISK 收到空分配 |
| 4 | 多信号冲突导致合成不稳定 | 仲裁机制 + 权重可配置 | 降级为等权聚合 | 信号质量下降 |
| 5 | 有效因子数不足 | min_factors_required 校验 | 返回 _empty_signal() + warning | D_PORTFOLIO_CORE 收到空信号 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| signal_generation_latency_ms | Gauge | generation_latency_ms 字段 | P95>100ms | P2 |
| signal_degradation_rate | Counter | is_degraded=True 计数/总计数 | >5% | P1 |
| empty_signal_rate | Counter | _empty_signal() 调用计数/总调用 | >1% | P2 |
| capital_allocation_total_weight | Gauge | total_allocated_weight 字段 | ≠1.0 | P2 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| SignalAggregatorBase | 空信号兜底 | 正常信号聚合 | _empty_signal(is_degraded=True) | 上游因子恢复 |
| CapitalAllocatorBase | 空分配兜底 | 正常资金分配 | _empty_allocation(total=0) | 上游信号恢复 |
| DegradationMonitorBase | 无退化检测 | 退化警告 | 下游自行判断信号质量 | Monitor 实现完成 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 信号退化未检测 | 中 | DegradationMonitorBase 实时监控 | CTR-ERR-003 触发率 > 0 |
| 2 | 恶意因子信号注入 | 低 | FactorSignal Pydantic/frozen dataclass 校验 | 非法输入被拒绝 |
| 3 | 资金分配越界 | 中 | CapitalAllocatorBase max_per_strategy=0.40 | total_capital 一致性检查 |
| 4 | look-ahead bias | 高 | GATE-F 门禁约束 | 因子仅使用 as_of_timestamp 前数据 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | 4 个 Base 类 + 2 个 Default 实现 | aggregate/allocate/evaluate/synthesize 核心路径 | 覆盖率≥80% |
| 2 | 集成测试 | D_FACTOR→D_SIGNAL→D_PORTFOLIO_CORE 数据流 | 因子输入→信号合成→组合构建 端到端 | 端到端通过 |
| 3 | 契约测试 | CTR-P1-015/CTR-P1-003/CTR-ERR-003 | Schema 变更不破坏下游 | 0 契约破坏 |
| 4 | 边界测试 | 空输入/零值/None | _empty_signal/_empty_allocation 兜底 | 兜底逻辑正确 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-L00-001 Data Source | 必须 | CTR-001 NormalizedMarketData | — | `D:\ZephyrAlpha\docs\03_modules\_domain_data\blueprint.md` |
| MOD-L02-001 Alpha Factor | 必须 | CTR-002 FactorSignal + 因子计算结果 | v4.0.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` |
| MOD-INF-015 Telemetry | 可选 | 信号生成监控 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\system_telemetry\blueprint.md` |

> **注**：v2.2.0 中的 `MOD-ALPHA_SIGNAL_DOMAIN` 依赖已移除（域已拆分为 D_FACTOR + D_SIGNAL 两个平级独立域，详见 [contract_mapping_table.yaml v1.1.0](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/contract_mapping_table.yaml) 变更记录）。

### 10.2 依赖图对齐声明

| 对齐项 | 对齐方式 | 对齐状态 | 说明 |
|--------|---------|:-------:|------|
| §10.1 依赖声明 ↔ dependency_path_panorama.md §5 | D_SIGNAL 依赖 D_FACTOR+D_DATA | ⚠️ 部分对齐 | dep-map §17 标注 D_SIGNAL 输出 CTR-008，蓝图实际输出 CTR-P1-015，待对齐 |
| §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 逐条核对 | 未对齐 | 待验证 |
| §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 未对齐 | 待验证 |

### 10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**：

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| aggregator_base.py | implementations/default_signal_aggregator.py | SignalAggregatorBase ABC | 继承 |
| aggregator_base.py | implementations/default_capital_allocator.py | CapitalAllocatorBase ABC | 继承 |
| aggregator_base.py | capital_allocator.py | CapitalAllocatorBase + CapitalAllocationResult | re-export |
| signal_synthesizer.py | implementations/default_signal_aggregator.py | SignalSynthesizerBase | 继承（未来） |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 |  | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防止蓝图与dep-map漂移 | CI门禁 | validate_path_alignment.py | 需D_SIGNAL条目 | CI | PR提交时 |
| 3 | 临时时态内容自动清理 | 否 | 无临时内容 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | C轨解除后需验证 | pytest+mypy+ruff | — | 需测试文件 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_signal\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\signal\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\signal\` | 测试用例（待创建） |
| 市场数据契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\market\market_data.py` | 行情数据结构（归属 MOD-INF-016） |
| 宏观因子信号契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\market\macro_factor_signal.py` | 宏观因子信号结构（归属 MOD-INF-016） |
| 因子监控报告契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\market\factor_monitor_report.py` | 因子监控报告结构（归属 MOD-INF-016） |
| 因子计算错误契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\errors\factor_computation_error.py` | 因子计算异常（归属 MOD-INF-016） |
| 信号退化警告契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\errors\signal_degradation_warning.py` | 信号退化告警（归属 MOD-INF-016） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_FACTOR Alpha Factor | 因子消费 | SignalAggregatorBase.aggregate() 消费 FactorSignal | 信号聚合可消费因子结果 |
| D_PORTFOLIO_CORE Portfolio Construction | 契约输出 | CTR-P1-015 SynthesizedSignal | 组合构建可消费合成信号 |
| D_RISK Risk Management | 契约输出 | CTR-P1-003 + CTR-ERR-003 | 风险管理可消费分配结果和降级警告 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress + version 更新 | 蓝图升级 |
| 2 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 版本号更新 | 蓝图升级 |
| 3 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | D_SIGNAL 输出契约 CTR-008→CTR-P1-015 对齐 | 契约ID不一致 |
| 4 | 代码文件头部 | `D:\ZephyrAlpha\src\zephyr\signal\*.py` | [BLUEPRINT] 字段指向 MOD-L03-001 | 当前指向 alpha_signal_domain-001 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 信号退化检测延迟 | 中 | 错误信号进入 D_PORTFOLIO_CORE | DegradationMonitorBase 实时监控 | 风险 |
| 2 | 多信号冲突 | 中 | 合成信号不稳定 | 仲裁机制 + 权重可配置 | 风险 |
| 3 | CTR-008 质量度量缺失 | 低 | D_FRONTEND 无法评估信号质量 | Phase C 优先实现 | 风险 |
| 4 | Base 类接口变更影响下游 | 低 | D_PORTFOLIO_CORE/D_RISK 编译错误 | Base 类接口冻结，破坏性变更需 Owner 审批 | 风险 |
| 5 | 代码头部 [BLUEPRINT] 指向域蓝图而非模块蓝图 | 中 | AI 施工时找不到正确蓝图 | §13 #4 修正 | 风险 |
| 6 | dep-map 契约ID不一致 | 中 | 依赖图与蓝图漂移 | §13 #3 对齐 | 风险 |
| 7 | 新策略需实现对应Base类 | — | 中 | OCP扩展点设计，新策略继承即可 | 负面后果 |
| 8 | C轨占位已解除 | — | 中 | 已解除 | 负面后果 |

---

## §16 施工指引

> ⚠️ **可施工**。以下施工指引为未来施工准备，当前阶段 AI 不可自主执行。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §0 对齐 + §1-§14 架构 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 5 | **Owner 已解除 C轨占位禁令** | Owner 明确授权 | ✅ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase |
| 施工模式 | 渐进式（扩展为主） |
| 核心风险 | 信号合成正确性 |
| 目标 generation | 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | SignalAggregatorBase 定义 | 必须 | ✅ | ✅ |
| 2 | CapitalAllocatorBase 定义 | 必须 | ✅ | ✅ |
| 3 | SignalSynthesizerBase 定义 | 必须 | ✅ | ✅ |
| 4 | D_FACTOR 因子产出 | 必须 | 部分实现 | ⚠️ |
| 5 | Owner 已解除 C轨占位 | 必须 | ✅ | ✅ |

### 16.3 实施步骤

#### 步骤 1：完善 DefaultSignalAggregator

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SignalAggregatorBase |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\signal\implementations\default_signal_aggregator.py` |
| 验收标准 | import 成功 + 单元测试通过 |
| 验证命令 | `python -m pytest tests/signal/test_default_signal_aggregator.py -v` |
| G7 检查项 | 上游 FactorSignal 契约一致；下游 SynthesizedSignal 契约一致 |
| AI 自治范围 | ai_modifiable |
| 检查点 | DefaultSignalAggregator 可实例化 + aggregate() 返回 SynthesizedSignal |

#### 步骤 2：完善 DefaultCapitalAllocator

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 CapitalAllocatorBase |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\signal\implementations\default_capital_allocator.py` |
| 验收标准 | import 成功 + 单元测试通过 |
| 验证命令 | `python -m pytest tests/signal/test_default_capital_allocator.py -v` |
| G7 检查项 | 上游 SynthesizedSignal 契约一致；下游 CapitalAllocationResult 契约一致 |
| AI 自治范围 | ai_modifiable |
| 检查点 | DefaultCapitalAllocator 可实例化 + allocate() 返回 CapitalAllocationResult |

#### 步骤 3：实现 CTR-008 SignalQualityMetrics

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SignalQualityMetrics（规划） |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\signal\signal_quality_metrics.py` |
| 验收标准 | D_PORTFOLIO_CORE/D_FRONTEND 可消费 |
| 验证命令 | `python -m pytest tests/signal/test_signal_quality_metrics.py -v` |
| G7 检查项 | CTR-008 契约定义完成；D_PORTFOLIO_CORE/D_FRONTEND 集成测试通过 |
| AI 自治范围 | human_gated |
| 检查点 | SignalQualityMetrics 可产出信号质量度量 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | DefaultSignalAggregator 修改破坏已有功能 | `git checkout -- src/zephyr/signal/gen/implementations/default_signal_aggregator.py` |
| 2 | DefaultCapitalAllocator 修改破坏已有功能 | `git checkout -- src/zephyr/signal/strategy/implementations/default_capital_allocator.py` |
| 3 | SignalQualityMetrics 新增失败 | 删除 signal_quality_metrics.py + 更新 __init__.py |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | DefaultSignalAggregator 存在 | `ls` exit 0 | 完成 | ☐ |
| 2 | DefaultCapitalAllocator 存在 | `ls` exit 0 | 完成 | ☐ |
| 3 | SignalQualityMetrics 存在 | `ls` exit 0 | 完成 | ☐ |
| 4 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 5 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 6 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 7 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 8 | 文档已更新 | §13 需要更新的文件全部更新 | 就绪 | ☐ |
| 9 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | not_started | — |
| verification_status | unverified | — |
| code_alignment_verified | no | — |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 等权聚合算法 | 算法 | `raw = sum(s.normalized_value for s in signals) / n; clip to [-3.0, 3.0]` | `implementations/default_signal_aggregator.py` |
| 2 | 置信度加权聚合 | 算法 | `weights = [c/total_conf for c in confidences]; raw = sum(val*w)` | `implementations/default_signal_aggregator.py` |
| 3 | 等权资金分配 | 算法 | `base = 1.0/n; min(base, max_per_strategy)` | `implementations/default_capital_allocator.py` |
| 4 | RiskParity 分配 | 算法 | `inv_vols = [1.0/max(abs(val/3.0), 0.05)]; weights = [iv/total for iv in inv_vols]` | `implementations/default_capital_allocator.py` |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/signal/ -v` | 运行全部D_SIGNAL测试 | — | 0 failed |
| 2 | 配置 | `aggregation_method` | 聚合方法选择 | `equal_weight`/`confidence_weight`/`ic_weight` | 默认 `equal_weight` |
| 3 | 配置 | `AllocationMethod` | 资金分配方法 | `EQUAL`/`SIGNAL`/`SHARPE`/`RISK_PARITY` | 默认 `EQUAL` |
| 4 | 配置 | `min_factors_required` | 最少有效因子数 | int, 默认 2 | 因子数不足→空信号 |
| 5 | 配置 | `max_per_strategy` | 单策略最大分配权重 | float, 默认 0.40 | 超限截断 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | 聚合器测试失败 | pytest exit≠0 | 检查 FactorSignal 字段是否匹配 CTR-002 | 修正字段映射 | pytest exit 0 |
| 2 | 运行 | 信号生成延迟超限 | P95>100ms | 检查因子数量+聚合算法复杂度 | 降级为等权聚合 | P95<50ms |
| 3 | 运行 | 空信号率过高 | >1% | 检查上游因子产出+is_valid率 | 修复因子源 | 空信号率<0.1% |
| 4 | 运行 | 资金分配总权重≠1.0 | total_allocated_weight≠1.0 | 检查 max_per_strategy 截断 | 归一化权重 | 总权重=1.0 |

### 16.12 并发操作模型

本模块无并发操作。所有 Base 类为无状态 ABC，每次调用独立执行，无共享状态。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| Base 类数量 | 4 | `grep "class.*Base" *.py` |
| Default 实现 | 2 | `ls implementations/` |
| 代码文件数 | 7 | `find src/zephyr/signal/ -name "*.py"` |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-001 | CTR-008 SignalQualityMetrics 缺失 | 新增 signal_quality_metrics.py | P1 | D_FRONTEND 需要信号质量评估时 | v2.2.0 | 待施工 |
| GAP-002 | 无 ML 驱动信号合成 | SignalSynthesizerBase 扩展 ML 实现 | P2 | 因子数 > 50 时 | v3.0.0 | 规划 |
| GAP-003 | 无 DefaultDegradationMonitor | 新增 default_degradation_monitor.py | P1 | C轨解除占位后 | v2.2.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v2.1.0 | 2 | 模板v3.5升级 | §0前移+§7/§15删除+§10拆分+铁律扩展 | ✅ |
| v2.2.0 | 2 | 模板v4.1回填 | 补齐模板缺失章节+压缩+对齐 | ✅ |
| v3.0.0 | 3 | 信号工厂体系升级 | 子模块清单(D-SIGNAL-01~164)+策略生命周期7阶段+策略池容量+灰度发布+§0.1对齐15条目/25文件+去除MOD-ALPHA_SIGNAL_DOMAIN依赖 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| SignalQualityMetrics | GAP-001 | signal_quality_metrics.py | Phase 3 | 待施工 |
| DefaultDegradationMonitor | GAP-003 | implementations/default_degradation_monitor.py | Phase 2 | 待施工 |
| MLSignalSynthesizer | GAP-002 | implementations/ml_signal_synthesizer.py | Phase ∞ | 规划 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L03001-01 | 信号聚合架构 | 单一聚合器 / OCP 扩展点 | OCP 扩展点 | 新策略只加不改 | 2026-05-05 |
| 2 | D-L03001-02 | CapitalAllocatorBase 归属 | 独立文件 / 与 SignalAggregatorBase 同文件 | 同文件（aggregator_base.py） | 3 个 Base 类职责紧密 | 2026-05-05 |
| 3 | D-L03001-03 | capital_allocator.py 定位 | 完整实现 / re-export | re-export only | 真源在 aggregator_base.py，避免重复定义 | 2026-05-05 |
| 4 | D-L03001-04 | CTR-008 实现时机 | 立即 / Phase C | Phase C | 优先级低于 D_PORTFOLIO_CORE/D_RISK | 2026-05-05 |
| 5 | D-L03001-05 | 契约类型选择 | Pydantic BaseModel / frozen dataclass | frozen dataclass（codegen） | CTR 契约由 codegen 生成，统一为 dataclass | 2026-05-05 |
| 6 | D-L03001-06 | 模板v4.1回填 | 保持压缩版/按模板回填 | 按模板回填 | 模板 REQUIRED_SECTIONS 缺失=不合规 | 2026-05-15 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| OCP 扩展点 | 开放封闭原则——对扩展开放、对修改封闭的抽象基类 | 普通ABC | OCP扩展点接口冻结，新功能只能通过继承添加 |
| SignalAggregation | 多个因子信号聚合为单个合成信号 | SignalSynthesis | 聚合=多→一加权组合；合成=多→一归一化 |
| DegradationMonitor | 检测信号质量退化的监控器 | 质量门禁 | Monitor只检测不阻断；门禁可阻断 |
| idempotency_key | 保证操作幂等性的唯一键（INV-007） | signal_id | idempotency_key=操作去重；signal_id=信号标识 |
| CTR-P1-015 | 合成交易信号契约 | CTR-008 | CTR-P1-015=SynthesizedSignal（已实现）；CTR-008=SignalQualityMetrics（规划） |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 代码头部 [BLUEPRINT] 指向 alpha_signal_domain-001 而非 MOD-L03-001 | 中 | 初始创建时使用域蓝图ID | 修正 [BLUEPRINT] 字段 | §5.1 #1 | 待解决 |
| 2 | dep-map §17 标注 D_SIGNAL 输出 CTR-008，蓝图实际输出 CTR-P1-015 | 中 | dep-map 使用旧契约ID | 对齐 dep-map 契约ID | §10.2 | 待解决 |
| 3 | 无测试文件（tests/signal/ 不存在） | 高 | 待创建测试 | 优先创建 | §9 | 待解决 |
| 4 | IC加权聚合为占位实现（直接调用等权） | 低 | IC数据不可用 | D_FACTOR IC数据就绪后实现 | §16.7 #2 | 待解决 |
| 5 | SyntaxWarning: invalid escape sequence '\Z' | 低 | 代码头部路径含反斜杠 | 使用原始字符串 r"" | — | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ⚠️ 测试文件缺失 |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ⚠️ 待验证 |
| 6 | 前 | 已读取蓝图全文（概述→§0→§1-§18→术语表→自检清单） | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答"X和Y的区别是什么" | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些设计可改哪些不可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ✅ 无临时内容 |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | C轨解除+3个Default实现完成 | 4个OCP扩展点已冻结 |
| 接口契约 | stable | 高 | CTR-008实现 | CTR-P1-015/CTR-P1-003/CTR-ERR-003已定义 |
| 数据模型 | stable | 高 | codegen更新 | frozen dataclass由codegen生成 |
| 施工步骤 | evolving | 中 | C轨解除 | 占位状态，施工步骤待验证 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 蓝图 | — | 已完成 |
| v2.0.0 | 4 Base + 2 Default 实现 | v0.1.0 | 已完成 |
| v2.1.0 | 模板v3.5升级 | v2.0.0 | 已完成 |
| v2.2.0 | 模板v4.1回填+压缩+对齐 | v2.1.0 | 已完成 |
| v3.0.0 | 信号工厂体系升级：子模块清单+策略生命周期+策略池+灰度发布+§0.1对齐 | v2.2.0 | 蓝图就绪，待施工 |
| v3.1.0 | DefaultDegradationMonitor + CTR-008 SignalQualityMetrics 实现 | v3.0.0 | 待施工 |
| v3.2.0 | D-SIGNAL-14 策略生命周期管理器 + D-SIGNAL-140 灰度发布 实现 | v3.1.0 | 待施工 |

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
| 8 | 禁止模糊词 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索/导入失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 实现与蓝图漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | 职责混乱 |
| 16 | 术语表不可省略 | 理解漂移 |
| 17 | 参考实现规格 vs 已实现代码重复——接口契约无法表达的逻辑规格MUST保留在§16.7 | 关键逻辑实现错误 |
| 18 | 对标验证表格 vs 对标散文——结构化对标表格MUST保留；长篇对标散文MUST删除 | 验证基准丢失 |
| 19 | SLO 必须定义 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略 | 故障无法发现 |
| 21 | 退化矩阵必须声明 | 部分失败时行为不可预测 |

### 蓝图拆分判定标准

**判定流程**：
1. 当前蓝图是否包含 ≥2 个独立职责域？→ 否 → 不拆分
2. 各职责域是否各自有独立的消费者和演进节奏？→ 否 → 不拆分
3. 拆分后各蓝图是否各自自包含（接口+依赖+施工）？→ 是 → 拆分

| 判定示例 | 职责域数量 | 消费者独立？ | 演进独立？ | 结论 |
|---------|:---:|:---:|:---:|------|
| 信号生成层（本蓝图） | 1 | 否 | 否 | 不拆分 |
| 假设：信号聚合+资金分配 | 2 | 是 | 是 | 拆分为 D_SIGNAL-SignalAggregation + D_SIGNAL-CapitalAllocation |
| 假设：信号聚合+降级监控 | 2 | 否 | 否 | 不拆分（职责紧密） |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。信号生成层为纯新增/扩展型模块，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 跨层契约 SSoT | — | — | `D:\ZephyrAlpha\architecture_model\contracts\cross_layer_contracts.yaml` | CTR 契约定义 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | D_FACTOR Alpha Factor | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` | 因子信号产出 | D_FACTOR 是因子计算层，D_SIGNAL 是信号聚合层，职责不同 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 信号生成代码 | `D:\ZephyrAlpha\src\zephyr\signal\` | 修改 | 蓝图描述的核心代码 |
| 2 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_signal\blueprint.md` | 修改 | 本文件 |
| 3 | 测试代码 | `D:\ZephyrAlpha\tests\signal\` | 新建 | 测试用例（待创建） |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 信号生成层架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| 信号生成层施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 信号生成层接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` | §4 接口契约、§10 依赖关系 |
| Tier 2 | `D:\ZephyrAlpha\src\zephyr\pf_core\` | §4 数据模型、§11 产出物路径 |
| Tier 2 | `D:\ZephyrAlpha\src\zephyr\risk\` | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |
| Base 类接口变更 | 需 Owner 审批（OCP冻结） | 下游检查兼容性 | 更新集成代码 |
| Default 实现类变更 | AI 可自主修改 | — | — |
