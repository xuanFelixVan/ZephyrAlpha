---
module_id: MOD-L09-001
submodule_path: src/zephyr/intelligence/research
title: "Research Innovation Core 蓝图+施工图 — 研究创新层"
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
construction_progress: design_only
actual_disk_path: "src/zephyr/research/"
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 2
functional_domain: research
summary: "研究创新层。BacktestEngineBase OCP扩展点 + BacktestResult/FactorDiscovery 数据类。业务层已开放，可施工。"
tags: [research-innovation, l09, c-track]
priority: P2
runtime_plane: warm
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-L00-001
    at: "§10"
    why: "CTR-001 NormalizedMarketData"
  - target: MOD-L02-001
    at: "§10"
    why: "CTR-002 FactorSignal"
  - target: MOD-L07-001
    at: "§10"
    why: "盘后分析→研究输入"
  - target: MOD-L13-001
    at: "§10"
    why: "CTR-P1-014 ExperimentResult消费"
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture_model\\layers\\l09_research_innovation.yaml"
    section: ""
    why: "架构层YAML真源"
codification_level: L1
codification_at: "2026-05-15"
responsibility_domain: 
design_maturity: prototype
build_status: generated
---

> ✅ **业务层已开放——可施工**
> 本模块属于 C 轨业务层，当前阶段为 T2-deferred（依赖图 §3.14）。
> 不允许启动新施工。仅允许维护已有代码和修复阻断性 bug。
> 解除条件：B轨容量升级完成(CAP-C01~C03) + T0/T1层验证通过。

# Research Innovation Core 蓝图+施工图 — 研究创新层

> module_id: MOD-L09-001 | version: 2.1.0 | status: active | domain: research
> actual_disk_path: src/zephyr/research/ | generation: 2 | construction_progress: partially_implemented

## 概述

本蓝图描述研究创新层（D_RESEARCH）——它解决了策略回测标准化和因子发现生命周期管理问题。核心职责包括：BacktestEngineBase OCP扩展点（新策略只加不改）、BacktestResult 不可变数据类、FactorDiscovery 因子生命周期管理、DefaultBacktestEngine 向量化日频回测。当前规模 1 个回测策略 + 0 个因子发现，目标容量 5 策略 + 50 因子。上游依赖 D_DATA NormalizedMarketData + D_FACTOR 因子信号 + D_REPORTING 盘后分析，下游被 实验 Experiment Pipeline 消费。

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

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L09-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | backtest_base.py | §3.1 | BacktestEngineBase + BacktestResult + FactorDiscovery | 已实现 |
| 2 | implementations/default_backtest_engine.py | §3.1 | DefaultBacktestEngine + BacktestConfig | 已实现 |
| 3 | implementations/__init__.py | §3.1 | 子包初始化 | 已实现 |
| 4 | __init__.py | §3.1 | 包初始化+导出 | 已实现 |

> YAML 真源（l09_research_innovation.yaml）定义3个子模块（experiments/notebooks/prototypes），均为 planned 状态。当前代码实现的是回测引擎，与YAML子模块划分不同——这是 ARB-23 裁定的"YAML-磁盘双重现实"问题，待 GOV-FSTR-001 统一。

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| §4 接口签名 = 代码实际签名 | 逐方法核对 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | BacktestEngineBase, BacktestResult, FactorDiscovery, DefaultBacktestEngine | — | — |
| v2.0.0 (模板重构) | 同 v1.0.0 | — | 结构重组，无功能变更 |
| v2.1.0 (回填+对齐) | 同 v1.0.0 | YAML子模块(experiments/notebooks/prototypes) | T2-deferred，待施工 |

---

## §1 设计背景与目标

### 1.1 背景

D_RESEARCH 研究创新层是量化策略研究的核心工作台。当前痛点：回测缺乏标准化框架、因子发现无生命周期管理、研究结果无法跨层传递。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 回测引擎标准化 | BacktestEngineBase OCP扩展点可用 |
| 2 | ✅ 包含 | 回测结果标准化 | BacktestResult frozen dataclass可产出 |
| 3 | ✅ 包含 | 因子发现标准化 | FactorDiscovery dataclass可产出 |
| 4 | ✅ 包含 | 向量化回测 | DefaultBacktestEngine可执行日频回测 |
| 5 | ❌ 排除 | 因子计算 | D_FACTOR Alpha Factor |
| 6 | ❌ 排除 | 信号生成 | D_SIGNAL Signal Generation |
| 7 | ❌ 排除 | 实验管理 | 实验 Experiment Pipeline |
| 8 | ❌ 排除 | 知识沉淀 | MOD-KB-001 Knowledge Base |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 回测使用Decimal类型进行资金计算 | 金融精度要求，禁止float |
| DefaultBacktestEngine使用pandas向量化 | 日频回测性能要求 |
| 本层当前无producer契约 | BacktestResult无法跨层传递，需Phase C注册 |
| FactorDiscovery状态机未实现 | 因子生命周期无管理 |
| 运行时平面: cold/warm | 依赖图 §2.0-A：C-Track各层，非运行时平面 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策+施工审批 | 设计+施工 | 可施工期间审批新施工 |
| 实验 消费者 | BacktestResult接口兼容 | 集成 | 需CTR-P1-014注册 |
| D_FACTOR 消费者 | FactorDiscovery提升流程 | 集成 | 因子验证通过后提升 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 回测策略数 | 1 (Default) | 5 | OCP扩展点已有，缺具体策略实现 | P2 |
| 因子发现 | 0 | 50 | FactorDiscovery状态机未实现 | P2 |
| 跨层契约 | 无producer | CTR-P1-014 | 未注册 | P2 |
| YAML子模块 | 3个planned | 3个active | 代码与YAML不匹配(ARB-23) | P2 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 日频回测 | 研究员提交信号+行情 | DefaultBacktestEngine.run(data, signals) → 指标计算 | BacktestResult |
| 因子验证 | 因子IC/IR达标 | FactorDiscovery(candidate→validated) | validated因子 |
| 因子提升 | Owner审批 | FactorDiscovery(validated→promoted) → 通知D_FACTOR | promoted因子 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 回测引擎 | BacktestEngineBase + DefaultBacktestEngine | 本模块 |
| 2 | ✅ 包含 | 回测结果 | BacktestResult (frozen dataclass) | 本模块 |
| 3 | ✅ 包含 | 因子发现 | FactorDiscovery (frozen dataclass) | 本模块 |
| 4 | ✅ 包含 | 向量化日频回测 | DefaultBacktestEngine: data + signals → BacktestResult | 本模块 |
| 5 | ❌ 排除 | 因子计算 | D_FACTOR Alpha Factor | D_FACTOR |
| 6 | ❌ 排除 | 信号合成 | D_SIGNAL Signal Generation | D_SIGNAL |
| 7 | ❌ 排除 | 实验注册与追踪 | 实验 Experiment Pipeline | 实验 |
| 8 | ❌ 排除 | 知识沉淀 | MOD-KB-001 Knowledge Base | KB |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | BacktestEngineBase | 回测OCP扩展点(ABC) | — | 同步调用 |
| 2 | BacktestResult | 回测结果(frozen dataclass) | — | 数据传递 |
| 3 | FactorDiscovery | 因子发现(frozen dataclass) | — | 数据传递 |
| 4 | DefaultBacktestEngine | 默认回测实现 | BacktestEngineBase | 继承 |
| 5 | BacktestConfig | 回测配置(dataclass) | — | 配置注入 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_DATA NormalizedMarketData + D_FACTOR因子信号 | 向量化回测 → 指标计算 | 实验 / D_FACTOR反馈 | BacktestResult |
| 2 | D_REPORTING盘后分析 | 研究假设输入 | D_ML_TRAIN ML / 实验 | 研究方向 |
| 3 | 因子信号 | 验证 → 生命周期管理 | D_FACTOR反馈 | FactorDiscovery |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| candidate | IC/IR验证通过 | validated | ic_ir>阈值 |
| validated | Owner审批 | promoted | Owner审批 |
| validated | 验证失败 | rejected | ic_ir<阈值 |
| promoted | 降级审批 | candidate | Owner审批 |

---

## §4 接口契约

> ⚠️ 以下签名与代码对齐（B-20：已实现代码不在蓝图中重复，只保留接口签名）。

### 4.1 公共 API

```python
class BacktestEngineBase(abc.ABC):
    """回测OCP扩展点——新回测策略继承此类"""
    _registry: ClassVar[dict[str, type]]
    @abc.abstractmethod
    def run(self, signals: List[Any], prices: List[Any]) -> "BacktestResult": ...

class FactorDiscovery:
    """因子发现数据类（frozen dataclass）"""
    factor_id: str
    name: str
    ic_mean: float
    ic_ir: float
    t_stat: float
    status: str  # candidate / validated / promoted / rejected (default="candidate")

class DefaultBacktestEngine(BacktestEngineBase):
    """默认回测引擎——向量化日频回测"""
    def run(self, data: pd.DataFrame, signals: pd.DataFrame,
            initial_capital: float = 1000000.0, **kwargs) -> BacktestResult: ...
```

### 4.2 数据模型

```python
@dataclass(frozen=True)
class BacktestResult:
    strategy_id: str
    start_date: str
    end_date: str
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    trades_count: int
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    risk_free_rate: float = 0.0
    annualization_factor: int = 252
    sample_size: int = 0
    volatility_annual: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BacktestConfig:
    initial_capital: Decimal = Decimal("1000000")
    commission_rate: Decimal = Decimal("0.0003")
    slippage_bps: Decimal = Decimal("1")
    benchmark_symbol: str = "000300"
    risk_free_rate: float = 0.0
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `run()` | `data` | ✅ | DataFrame(MultiIndex symbol×date, 含OHLCV)，非空 |
| `run()` | `signals` | ✅ | DataFrame(date×symbol, 目标权重)，非空 |
| `run()` | `initial_capital` | ❌ | float, default=1000000.0 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `run()` | `BacktestResult` (frozen) | 数据不足→sharpe=0.0降级返回 |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增BacktestEngineBase子类 | ✅ 向后兼容 | OCP扩展 |
| BacktestResult新增字段 | ✅ 向后兼容 | frozen dataclass+默认值 |
| 删除/重命名BacktestResult字段 | ❌ 破坏性 | 需Owner审批+迁移方案 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | BacktestEngineBase为OCP扩展点 | 新回测策略只加不改 |
| 2 | BacktestResult为frozen dataclass | 回测结果不可变 |
| 3 | FactorDiscovery状态机: candidate→validated→promoted/rejected | 因子生命周期管理 |
| 4 | DefaultBacktestEngine使用pandas向量化 | 日频回测性能要求 |
| 5 | 回测使用Decimal类型进行资金计算 | 金融精度要求 |
| 6 | 最小样本量_MIN_SAMPLE_SIZE=60 | sharpe/sortino计算前置条件 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 回测策略数 | 1 (Default) | 5 | 无上限 | ✅ | OCP扩展 |
| 日频回测记录 | ~100 | ~1000 | 无上限 | ✅ | 批量处理 |
| 因子发现数 | 0 | 50 | 无上限 | ✅ | 状态机管理 |

### 5.3 迁移/废弃方案

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| — | 无迁移计划 | — | — | — | — |

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 回测执行成功率 | 99% | 执行结果统计 | 成功/总执行 | 99% | 每月允许1%失败 | <95%告警 |
| 可维护性 | 新策略接入时间 | <1h | 接入记录 | — | — | — | — |
| 性能 | 日频回测P95 | <30s | 执行耗时 | 回测耗时P95 | <30s | — | >60s告警 |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | float资金计算 | Decimal | 金融精度 |
| 2 | 编码模式 | 修改BacktestResult字段值 | frozen dataclass不可变 | 回测结果完整性 |
| 3 | 导入源 | zephyr.signal.* | 通过CTR-002消费 | 分层约束 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 输入数据不足 | DataFrame为空/样本量<60 | sharpe=0.0降级返回 | 回测指标不可靠 |
| 2 | 回测计算溢出 | OverflowError捕获 | Decimal类型兜底 | 计算结果异常 |
| 3 | 因子状态机非法转换 | 状态守卫条件检查 | 拒绝转换+日志记录 | 因子状态不一致 |
| 4 | 价格数据缺失 | KeyError in _get_price | 返回Decimal("0") | 持仓估值为零 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| backtest_execution_count | Counter | 自动埋点 | — | — |
| backtest_execution_duration_seconds | Histogram | 自动埋点 | P95>60s | P2 |
| factor_discovery_status_count | Gauge | 手动上报 | — | — |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| DefaultBacktestEngine | — | 回测执行 | 返回sharpe=0.0的BacktestResult | 输入数据修复 |
| FactorDiscovery | 只读查询 | 状态转换 | 拒绝转换 | 守卫条件满足 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 回测结果被篡改 | 高 | BacktestResult frozen dataclass | 单元测试验证不可变 |
| 2 | 因子状态非法提升 | 中 | 状态机守卫条件 | 单元测试验证转换规则 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | BacktestEngineBase | ABC不可实例化+注册表存在 | 覆盖率>80% |
| 2 | 单元测试 | BacktestResult | frozen不可变+默认timestamp | 修改抛AttributeError |
| 3 | 单元测试 | FactorDiscovery | 默认status=candidate | 状态正确 |
| 4 | 单元测试 | DefaultBacktestEngine | run返回BacktestResult | 指标计算正确 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-L00-001 Data Source | 必须 | CTR-001 NormalizedMarketData | — | `D:\ZephyrAlpha\docs\03_modules\_domain_data\blueprint.md` |
| MOD-L02-001 Alpha Factor | 必须 | CTR-002 FactorSignal | — | `D:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` |
| MOD-L07-001 Post-Trade Analytics | 可选 | 盘后分析→研究输入 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_reporting\blueprint.md` |
| MOD-L13-001 Experiment Pipeline | 可选 | CTR-P1-014 ExperimentResult | — | `D:\ZephyrAlpha\docs\03_modules\_domain_simulation\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §5 | D_RESEARCH依赖与依赖图模块归属表一致 | 已对齐 | 逐项核对 |
| 2 | §10.1 依赖声明 ↔ l09_research_innovation.yaml | YAML接口声明与蓝图依赖一致 | 已对齐 | 逐项核对 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `ls src/zephyr/research/` |

> 依赖图对齐说明：dependency_path_panorama.md §5 将 MOD-L09-001 归类为 T2-deferred、线7业务价值线。蓝图 priority 从 P1 修正为 P2 以对齐依赖图。

### 10.3 内部依赖图

**执行顺序依赖**：

| 上游步骤 | 下游步骤 | 依赖关系 |
|---------|---------|---------|
| BacktestEngineBase定义 | DefaultBacktestEngine实现 | 继承依赖 |

**数据流依赖**：

| 数据生产者 | 数据消费者 | 数据格式 |
|-----------|-----------|---------|
| DefaultBacktestEngine | 实验 Experiment Pipeline | BacktestResult |
| FactorDiscovery(validated) | D_FACTOR Alpha Factor | 因子提升信号 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 模块简单，手动维护 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 否 | T2层暂不需要 | — | — | — | — | — |
| 3 | 临时时态内容自动清理 | 否 | 无临时内容 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 否 | 可施工 | — | — | — | — | — |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_research\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\research\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\research\` | 测试用例 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_DATA Data Source | CTR-001消费 | 回测可接收行情数据 | 回测可执行 |
| D_FACTOR Alpha Factor | CTR-002消费+因子提升反馈 | 回测可消费因子信号 | 因子回测可运行 |
| D_REPORTING Post-Trade Analytics | 盘后数据输入 | 研究方向可由盘后分析驱动 | 数据可消费 |
| 实验 Experiment Pipeline | CTR-P1-014消费 | 实验结论可指导研究方向 | 实验可消费 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress+priority更新 | 进度+优先级变更 |
| 2 | 架构层YAML | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\layers\l09_research_innovation.yaml` | 确认files列表与磁盘一致 | ARB-23双重现实 |
| 3 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 确认D_RESEARCH条目与蓝图一致 | 依赖对齐 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | DefaultBacktestEngine简化 | 高 | 不适用于高频/复杂策略 | OCP扩展点允许替换 | 风险 |
| 2 | 无producer契约 | 中 | BacktestResult无法跨层传递 | Phase C注册CTR-P1-014 | 风险 |
| 3 | FactorDiscovery状态机未实现 | 中 | 因子生命周期无管理 | Phase C实现状态转换 | 风险 |
| 4 | YAML子模块与代码不匹配 | 高 | ARB-23双重现实 | GOV-FSTR-001统一 | 风险 |
| 5 | 新策略需实现BacktestEngineBase | — | — | — | 负面后果 |
| 6 | 日频粒度不适用于高频场景 | — | — | — | 负面后果 |

---

## §16 施工指引

> ✅ **业务层已开放——可施工**。当前不允许启动新施工步骤。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | C轨占位已解除 | 确认✅标记 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个 Phase（可施工期间执行） |
| 施工模式 | 扩展 |
| 核心风险 | 回测计算正确性 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板重构+回填） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | BacktestEngineBase定义 | hard | 已实现 | ✅ |
| 2 | BacktestResult定义 | hard | 已实现 | ✅ |
| 3 | FactorDiscovery定义 | hard | 已实现 | ✅ |
| 4 | CTR-001 NormalizedMarketData | hard | 部分实现 | ❌ |
| 5 | B轨容量升级完成(CAP-C01~C03) | hard | 未完成 | ❌ |

### 16.3 实施步骤

#### 步骤 1：完善DefaultBacktestEngine

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\research\implementations\default_backtest_engine.py` |
| 验收标准 | import成功，run返回BacktestResult |
| 验证命令 | `python -c "from zephyr.research.implementations.default_backtest_engine import DefaultBacktestEngine"` |
| G7 检查项 | 上游backtest_base.py存在，下游实验可消费 |
| AI 自治范围 | ai_modifiable |
| 检查点 | DefaultBacktestEngine可实例化 |

#### 步骤 2：实现FactorDiscovery状态机

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.3 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\research\backtest_base.py` |
| 验收标准 | candidate→validated→promoted/rejected状态转换正确 |
| 验证命令 | `python -m pytest tests/ -k factor_discovery` |
| G7 检查项 | 状态守卫条件完整 |
| AI 自治范围 | ai_modifiable |
| 检查点 | 状态转换测试通过 |

#### 步骤 3：注册CTR-P1-014

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4 |
| 产出位置 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\cross_layer_contracts.yaml` |
| 验收标准 | BacktestResult注册为producer契约，实验可消费 |
| 验证命令 | `grep "CTR-P1-014" cross_layer_contracts.yaml` |
| G7 检查项 | 下游实验可消费 |
| AI 自治范围 | human_gated |
| 检查点 | 契约注册完成 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | DefaultBacktestEngine实现失败 | 还原implementations/ |
| 2 | FactorDiscovery状态机实现失败 | 还原backtest_base.py |
| 3 | CTR-P1-014注册失败 | 还原cross_layer_contracts.yaml |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | DefaultBacktestEngine 存在 | `ls` exit 0 | 完成 | ☐ |
| 2 | DefaultBacktestEngine 非空 | `cat` 有内容 | 完成 | ☐ |
| 3 | SLO 已定义 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 4 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 5 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 6 | 文档已更新 | §13 需要更新的文件全部更新 | 就绪 | ☐ |
| 7 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_implemented | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 向量化回测算法 | 算法 | 遍历日期→信号权重归一化→调仓(先卖后买)→NAV计算→指标计算(sharpe/sortino/calmar/maxDD) | `src/zephyr/research/simulation/default_backtest_engine.py` |
| 2 | 频率检测 | 算法 | 日期间隔中位数≤2d=daily, ≤8d=weekly, else=monthly | 同上 |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -c "from zephyr.research.backtest_base import BacktestEngineBase"` | 验证基类可导入 | — | 无报错 |
| 2 | 配置 | `BacktestConfig` → `initial_capital` | 初始资金 | Decimal, 默认1000000 | >0 |
| 3 | 配置 | `BacktestConfig` → `commission_rate` | 佣金率 | Decimal, 默认0.0003 | >0 |

### 16.10 故障与操作

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | 回测结果全零 | 输入数据为空 | 检查DataFrame非空 | 修复输入数据 | 重新执行 |
| 2 | 运行 | 因子状态转换被拒 | 守卫条件不满足 | 检查ic_ir/t_stat值 | 修正因子参数 | 重新提交 |

### 16.12 并发操作模型

本模块无并发操作——回测为单线程同步执行。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 回测策略数 | 1 (Default) | BacktestEngineBase子类计数 |
| 因子发现数 | 0 | FactorDiscovery实例计数 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L09-001 | 无producer契约 | 注册CTR-P1-014 BacktestResult | P2 | 跨层传递需求>0 | v2.2.0 | 待施工 |
| GAP-L09-002 | FactorDiscovery状态机未实现 | 实现状态转换 | P2 | 因子管理需求>0 | v2.2.0 | 待施工 |
| GAP-L09-003 | YAML子模块与代码不匹配 | GOV-FSTR-001统一 | P2 | T2层开工前 | v3.0.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | BacktestEngineBase+BacktestResult+FactorDiscovery+DefaultBacktestEngine | ⚠️ |
| v2.0.0 | 2 | 模板重构 | 章节重排+新增概述+标准锚点 | ⚠️ |
| v2.1.0 | 2 | 回填+对齐 | 模板缺失章节回填+代码签名对齐+依赖图对齐 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| CTR-P1-014注册 | GAP-L09-001 | cross_layer_contracts.yaml | Phase 3 | 待施工 |
| FactorDiscovery状态机 | GAP-L09-002 | backtest_base.py | Phase 2 | 待施工 |
| YAML-代码统一 | GAP-L09-003 | l09_research_innovation.yaml | Phase 4 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L09-01 | BacktestResult用frozen dataclass而非Pydantic BaseModel | dataclass/BaseModel | dataclass | 量化模块数据类无需验证中间态，frozen保证不可变 | 2026-05-05 |
| 2 | D-L09-02 | BacktestEngineBase用ABC+注册表模式 | ABC+Registry/Protocol | ABC+Registry | OCP扩展点需要运行时发现机制 | 2026-05-05 |
| 3 | D-L09-03 | DefaultBacktestEngine用pandas向量化 | pandas向量化/numpy循环/numba | pandas向量化 | 日频回测pandas生态最成熟 | 2026-05-05 |
| 4 | D-L09-04 | FactorDiscovery状态机暂不实现 | 立即实现/暂不实现 | 暂不实现 | C轨已解除，可施工，状态机为Phase C内容 | 2026-05-05 |
| 5 | D-L09-05 | 模板v3.5升级 | 保持v3.3/按v3.5升级 | 按v3.5升级 | §0前移+§7/§15删除+§10拆分+铁律扩展 | 2026-05-15 |
| 6 | D-L09-06 | priority从P1修正为P2 | P1/P2 | P2 | 对齐dependency_path_panorama.md T2-deferred分类 | 2026-05-15 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| BacktestResult | 回测结果frozen dataclass，包含夏普/回撤/胜率等指标 | BacktestConfig | Config是输入配置，Result是输出结果 |
| FactorDiscovery | 因子发现记录，包含IC/IR/t-stat和生命周期状态 | FactorSignal(CTR-002) | Discovery是研究态，Signal是生产态 |
| OCP扩展点 | 开闭原则——对扩展开放，对修改关闭的抽象基类 | 策略模式 | OCP强调不修改已有代码 |
| C轨占位 | C-Track业务层占位蓝图，标记为T2-deferred | B轨模块 | B轨是基础设施，C轨是业务 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | BacktestResult无producer契约 | 中 | CTR-P1-014未注册 | Phase C注册 | §5.1 #3 | 待解决 |
| 2 | FactorDiscovery状态机未实现 | 中 | C轨已解除，可施工 | Phase C实现 | §3.3 | 待解决 |
| 3 | YAML子模块(experiments/notebooks/prototypes)与代码不匹配 | 高 | ARB-23双重现实 | GOV-FSTR-001统一 | §0.1 | 待解决 |
| 4 | DefaultBacktestEngine._rebalance简化(固定100股) | 低 | MVP实现 | Phase C完善 | §4.1 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ✅ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在依赖图有对应条目 | 逐依赖核对 | ✅ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 13 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | evolving | 中 | FactorDiscovery状态机实现 | 回测引擎OCP已验证，因子发现待实现 |
| 接口契约 | evolving | 中 | CTR-P1-014注册 | 接口签名已稳定，跨层契约未注册 |
| 数据模型 | stable | 高 | — | BacktestResult frozen已验证 |
| 施工步骤 | evolving | 低 | T2层开工 | 可施工期间步骤为实施态 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v1.0.0 | 初始设计+BacktestEngineBase+BacktestResult+FactorDiscovery | — | 已完成 |
| v2.0.0 | 模板重构+章节重排 | v1.0.0 | 已完成 |
| v2.1.0 | 回填缺失章节+代码签名对齐+依赖图对齐 | v2.0.0 | 已完成 |
| v2.2.0 | FactorDiscovery状态机+CTR-P1-014注册 | v2.1.0 | 待施工(T2) |
| v3.0.0 | YAML子模块统一+experiments/notebooks/prototypes实现 | v2.2.0 | 待施工(T2) |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> 完整铁律（含"为什么"和"违反后果"）→ [blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)

| # | 铁律 |
|---|------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） |
| 2 | 必备链接不可省略 |
| 3 | 蓝图必须是最终设计结果 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 |
| 5 | 涉及文件范围必须明确列出 |
| 6 | 容量估算必须写 |
| 7 | 迁移/废弃方案必须写 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 |
| 9 | 蓝图必须自包含 |
| 10 | 删除文件必须遵守安全删除协议 |
| 11 | construction_progress 必须与代码实际状态一致 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4） |
| 14 | 临时时态内容执行完毕后从蓝图删除 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 |
| 16 | 术语表不可省略 |
| 17 | 参考实现规格 vs 已实现代码重复——接口契约无法表达的逻辑规格MUST保留在§16.7 |
| 18 | 对标验证表格保留，对标散文删除 |
| 19 | SLO必须定义 |
| 20 | 可观测性不可省略 |
| 21 | 退化矩阵必须声明 |

---

## 蓝图拆分判定标准

> 判定流程 → [blueprint-construction-template.md 蓝图拆分判定标准](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)

### 判定示例

| 场景 | 职责不同？ | 独立依赖？ | 判定 |
|------|:---:|:---:|------|
| 回测引擎 + 因子发现 | 否（同属研究创新） | 否（共享D_DATA/D_FACTOR） | 原地升级 |
| 回测引擎 + 合规引擎 | 是 | 是 | 拆分独立蓝图 |

---

## ⚠️ 安全删除协议

> 删除铁律 → [blueprint-construction-template.md 安全删除协议](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| — | 无删除计划 | — | — | — | — |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
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
| 1 | backtest_base.py | `D:\ZephyrAlpha\src\zephyr\research\backtest_base.py` | 读取/修改 | 补充状态机 |
| 2 | implementations/ | `D:\ZephyrAlpha\src\zephyr\research\implementations\` | 修改 | 完善实现 |
| 3 | __init__.py | `D:\ZephyrAlpha\src\zephyr\research\__init__.py` | 读取 | 导出验证 |

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
| Tier 1 | 实验 Experiment Pipeline | §4 接口契约、§10 依赖关系 |
| Tier 2 | D_FACTOR Alpha Factor | 因子验证反馈（规划） |
| Tier 2 | D_REPORTING Post-Trade Analytics | 研究方向输入（规划） |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改（§4） | 需Owner审批+通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需Owner审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需§0对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充 | AI可自主修改 | — | — |
| 容量升级方案新增（§17） | 需Owner审批 | 下游评估影响 | 更新容量预算 |
