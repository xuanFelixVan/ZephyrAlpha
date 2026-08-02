---
module_id: MOD-SIM-003
title: "Risk Simulator 蓝图 — 风控仿真器"
doc_type: blueprint
status: Active
version: "0.1.0"
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
