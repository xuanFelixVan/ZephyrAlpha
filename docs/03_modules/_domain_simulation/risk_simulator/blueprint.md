---
module_id: MOD-SIM-003
title: "Risk Simulator 蓝图 — 风控仿真器"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
layer: L03_simulation
layer_name: simulation
functional_domain: simulation
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-SIM-003 Risk Simulator — 风控仿真器 蓝图

> **module_id**: MOD-SIM-003 | **域**: D_SIMULATION | **层**: L03 仿真
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-040 系统性压力测试
> **SSoT**: depgraph MOD-SIM-003 | **设计真源**: 19-D-SIMULATION §1 SIM-03

## 1. 定位

风控仿真器——VaR(风险价值)模拟 + 回撤模拟 + 熔断模拟。基于收益率序列
计算多方法 VaR/CVaR、最大回撤及恢复期、熔断触发判定, 供风控评估和
压力测试使用。

属 A 类基础设施(确定性计算), 纯基础层不涉及策略。
**纯基础设施: 不决定"买什么/何时买", 只负责"算这个组合的风险有多大"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | returns (收益率序列, list[float]) | — |
| 输入 | confidence_levels (置信水平, 默认 0.95/0.99) | — |
| 输入 | method (VaR方法: historical/parametric/monte_carlo) | — |
| 输入 | trigger_level (熔断触发回撤阈值, 默认 -0.10) | — |
| 输出 | RiskSimulationResult (VaR+回撤+熔断) | — |

## 3. 核心算法

### 3.1 历史 VaR
```
sorted_returns = sort(returns)
idx = floor((1 - confidence) * n)
VaR = -sorted_returns[idx]   (正数=损失)
CVaR = -mean(returns <= sorted_returns[idx])   (条件期望损失)
```

### 3.2 参数 VaR (正态假设)
```
z = Φ^(-1)(1 - confidence)   (标准正态分位数, 用 math.erfinv 近似)
VaR = -(mean - z * std)      (注意 z 为负)
CVaR = -(mean - std * φ(z)/(1-confidence))   (φ=正态pdf)
```

### 3.3 蒙特卡洛 VaR
```
拟合 N(mean, std²), 模拟 mc_paths 条路径
VaR = -percentile(simulated_returns, (1-confidence)*100)
```

### 3.4 回撤模拟
```
wealth = cumprod(1 + returns)
peak = running_max(wealth)
drawdown = (wealth - peak) / peak
max_drawdown = min(drawdown)
duration = trough_pos - peak_pos
recovery = next_peak_pos - trough_pos (None 若未恢复)
```

### 3.5 熔断模拟
```
triggered = min(drawdown) <= trigger_level
hit_count = count(drawdown <= trigger_level 的连续段)
```

## 4. 关键不变量 (INVARIANTS)

- RiskConfig / VaRResult / DrawdownResult 等为 frozen dataclass
- VaR/CVaR 用正数表示损失(亏损越大值越大)
- max_drawdown <= 0 (负数或0)
- 蒙特卡洛使用固定 seed(可复现)
- 纯计算无副作用, 无第三方依赖(用 math 实现 Φ^(-1))

## 5. 错误契约

- `SimulationError` (ZA-SIM-0003): 输入非法(空序列/样本不足)

## 6. 数据模型

```python
class RiskMethod(str, Enum):
    HISTORICAL = "historical"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"

@dataclass(frozen=True)
class RiskConfig:
    confidence_levels: tuple[float, ...] = (0.95, 0.99)
    mc_paths: int = 10000
    mc_seed: int = 42
    periods_per_year: int = 252

@dataclass(frozen=True)
class VaRResult:
    confidence: float
    var: float       # 正数=损失
    cvar: float      # 条件VaR(预期短缺)
    method: RiskMethod

@dataclass(frozen=True)
class DrawdownResult:
    max_drawdown: float
    max_dd_duration: int       # 回撤持续期数
    recovery_duration: int | None  # 恢复期数(None=未恢复)
    current_drawdown: float

@dataclass(frozen=True)
class CircuitBreakerResult:
    triggered: bool
    trigger_level: float
    hit_count: int
    worst_drawdown: float

@dataclass(frozen=True)
class RiskSimulationResult:
    var_results: list[VaRResult]
    drawdown: DrawdownResult
    circuit_breaker: CircuitBreakerResult
    method: RiskMethod
    num_obs: int
```

## 7. API

```python
class RiskSimulator:
    def __init__(self, config: RiskConfig | None = None) -> None: ...
    def calculate_var(
        self, returns, confidence_levels=None, method=RiskMethod.HISTORICAL,
    ) -> list[VaRResult]: ...
    def simulate_drawdown(self, returns) -> DrawdownResult: ...
    def simulate_circuit_breaker(
        self, returns, trigger_level=-0.10,
    ) -> CircuitBreakerResult: ...
    def run_full_simulation(
        self, returns, method=RiskMethod.HISTORICAL, trigger_level=-0.10,
    ) -> RiskSimulationResult: ...
    def audit_summary(self, result) -> str: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-SIM-012 (result_analyzer 风险分析)
- 设计真源: 19-D-SIMULATION §1 SIM-03

## 9. 测试

- `tests/simulation/test_risk_simulator.py`
- 覆盖: 历史VaR/CVaR、参数VaR、蒙特卡洛VaR、回撤模拟(最大回撤/持续期/恢复)、
  熔断触发/未触发、全量仿真、边界值(空/样本不足)、配置自定义、frozen不可变、
  审计摘要

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIM-003`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIM-003` 的 3 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIM-003` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIM-003 | MOD-SIM-003 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/simulation/risk_simulator.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/simulation/test_risk_simulator.py` | ✅ 已实现 | |
| `tests/simulation/test_scenario_generator.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


