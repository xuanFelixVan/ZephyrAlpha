---
module_id: MOD-SIM-024
title: "Deflated Sharpe Ratio 计算器蓝图 — 多重测试偏差修正"
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
build_status: production
---

# MOD-SIM-024 Deflated Sharpe Ratio Calculator — DSR 计算器 蓝图

> **module_id**: MOD-SIM-024 | **域**: D_SIMULATION | **层**: L03 仿真
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-033 过拟合系统性防护
> **SSoT**: depgraph MOD-SIM-024 | **设计真源**: 19-D-SIMULATION §1 SIM-24

## 1. 定位

Deflated Sharpe Ratio (DSR) 计算器——多重测试偏差修正的 Sharpe 比率。
基于 Bailey & López de Prado (2014) 论文, 修正回测中"试了 N 次取最好"导致的
Sharpe 虚高问题。产出 DSR 值 + 显著性判定 + 趋势追踪, 供过拟合检测和回测验证使用。

属 A 类基础设施(确定性数学计算), 纯基础层不涉及策略。
**纯基础设施: 不决定"买什么/何时买", 只负责"算这个 Sharpe 是不是试出来的运气"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | returns (收益率序列, list[float]) | — |
| 输入 | num_trials (试次数, 默认1) | — |
| 输入 | risk_free_rate (无风险利率, 默认0) | — |
| 输入 | periods_per_year (年化频率, 默认252) | — |
| 输出 | DSRResult (DSR值+Sharpe+显著性+统计量) | — |
| 输出 | DSRTrendPoint (趋势追踪点) | — |

## 3. 核心公式

### 3.1 Sharpe 比率

```
SR = (mean(returns) - risk_free_rate) / std(returns)
SR_annual = SR * sqrt(periods_per_year)
```

### 3.2 Sharpe 估计量方差 (非正态修正)

```
V[SR] = (1 - γ·SR + (κ-1)/4·SR²) / (T - 1)
```
- γ = 偏度, κ = 峰度, T = 样本数, SR = 非年化 Sharpe

### 3.3 多重测试期望最大值 (Bailey-LdP)

```
E[max(Z_N)] ≈ sqrt(2·ln(N)) - (ln(π) + ln(ln(N))) / (2·sqrt(2·ln(N)))   (N > 1)
E[max(Z_1)] = 0                                                            (N = 1)
```

### 3.4 Deflated Sharpe Ratio

```
SR* = (SR - SR_0) / sqrt(V[SR]) - E[max(Z_N)]
DSR = Φ(SR*)    # Φ = 标准正态CDF
```
- SR_0 = 0 (零假设下的 Sharpe)
- DSR ∈ (0, 1), 越大越显著

### 3.5 显著性判定

```
is_significant = DSR >= threshold   # 默认 0.95
```

## 4. 关键不变量 (INVARIANTS)

- DSRResult / DSRConfig / DSRTrendPoint 为 frozen dataclass (不可变)
- DSR ∈ (0, 1) 恒成立 (Φ 的值域)
- 样本数 < 3 时 raise SimulationError (无法计算偏度/峰度)
- num_trials < 1 时 raise SimulationError
- 所有统计计算使用 float (非 Decimal, 与 empyrical/numpy 生态一致)
- 无第三方依赖 (不依赖 scipy, 用 math.erf 实现 Φ)

## 5. 错误契约

- `SimulationError` (ZA-SIM-0024): 输入非法(空序列/样本不足/试次数非法)

## 6. 数据模型

```python
@dataclass(frozen=True)
class DSRConfig:
    significance_threshold: float = 0.95
    periods_per_year: int = 252
    risk_free_rate: float = 0.0

@dataclass(frozen=True)
class DSRResult:
    sharpe: float              # 非年化 Sharpe
    sharpe_annualized: float   # 年化 Sharpe
    dsr: float                 # Deflated Sharpe Ratio ∈ (0,1)
    num_trials: int
    num_obs: int
    skewness: float
    kurtosis: float
    var_sr: float              # V[SR]
    expected_max: float        # E[max(Z_N)]
    is_significant: bool

@dataclass(frozen=True)
class DSRTrendPoint:
    index: int
    dsr: float
    sharpe: float
```

## 7. API

```python
class DeflatedSharpeCalculator:
    def __init__(self, config: DSRConfig | None = None) -> None: ...
    def calculate(
        self, returns: list[float], num_trials: int = 1,
        risk_free_rate: float | None = None,
    ) -> DSRResult: ...
    def track_trend(
        self, returns: list[float], num_trials: int = 1,
        window: int = 60,
    ) -> list[DSRTrendPoint]: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-SIM-023 (sharpe_calculator_fixer 集成 DSR), MOD-SIM-012 (result_analyzer)
- 设计真源: 19-D-SIMULATION §1 SIM-24

## 9. 测试

- `tests/simulation/test_deflated_sharpe_calculator.py`
- 覆盖: 基本DSR计算、N=1无修正、N>1多重测试修正、偏度/峰度影响、
  显著性判定、趋势追踪、边界值(空序列/样本不足拒绝/年化)、
  已知值验证(正态分布DSR≈0.5)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIM-024`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIM-024` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIM-024` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIM-024 | MOD-SIM-024 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/simulation/test_deflated_sharpe_calculator.py` | ✅ 已实现 | |

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


