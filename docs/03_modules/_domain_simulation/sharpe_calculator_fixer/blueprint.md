---
module_id: MOD-SIM-023
title: "Sharpe 计算修正器蓝图 — 非正态检测+Sortino+DSR+滚动"
doc_type: blueprint
status: Active
version: "0.1.1"
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

# MOD-SIM-023 Sharpe Calculator Fixer — Sharpe 计算修正器 蓝图

> **module_id**: MOD-SIM-023 | **域**: D_SIMULATION | **层**: L03 仿真
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-033 过拟合系统性防护
> **SSoT**: depgraph MOD-SIM-023 | **设计真源**: 19-D-SIMULATION §1 SIM-23

## 1. 定位

Sharpe 计算修正器——A股场景的 Sharpe 比率修正计算。解决标准 Sharpe 的5个问题:
1. 无风险利率用中国10年期国债(非美国T-bill)
2. 样本量<60不计算(统计不显著)
3. 非正态分布用 Sortino 替代
4. 多重测试偏差用 DSR(MOD-SIM-024)修正
5. 滚动 rolling Sharpe + 年化按频率自动选择

属 A 类基础设施(确定性数学计算), 纯基础层不涉及策略。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | returns (收益率序列) | — |
| 输入 | num_trials (试次数, 传给DSR) | — |
| 输入 | risk_free_rate (默认中国10Y国债) | — |
| 输出 | SharpeResult (Sharpe+Sortino+DSR+方法选择) | — |
| 输出 | rolling Sharpe 序列 | — |

## 3. 核心规则

### 3.1 样本量门禁
```
if len(returns) < min_samples (60):
    return SharpeResult(sharpe=None, reason="样本不足")
```

### 3.2 非正态检测 (Jarque-Bera)
```
JB = n/6 * (γ² + κ²/4)
if JB > jb_critical (5.99, α=0.05, χ²(2)):
    method = "sortino"  # 非正态 -> 用 Sortino
else:
    method = "sharpe"   # 正态 -> 用 Sharpe
```

### 3.3 Sortino 比率 (非正态替代)
```
downside_returns = min(0, returns - rf)
downside_std = sqrt(mean(downside_returns²))
Sortino = (mean(returns) - rf) / downside_std
```

### 3.4 DSR 集成
调用 MOD-SIM-024 DeflatedSharpeCalculator 计算 DSR, 纳入结果。

### 3.5 年化
```
annual_factor = sqrt(periods_per_year)
sharpe_annual = sharpe * annual_factor
```
频率自动选择: 日度=252 / 周度=52 / 月度=12。

## 4. 关键不变量

- SharpeResult/SharpeConfig 为 frozen dataclass
- 样本<60 时 sharpe=None (不计算)
- float 计算(非 Decimal)
- 无第三方依赖(自实现 Jarque-Bera + Sortino)

## 5. 错误契约

- `SimulationError` (ZA-SIM-0023): 输入非法(空序列/非法频率)

## 6. 数据模型

```python
class SharpeMethod(str, Enum):
    SHARPE = "sharpe"
    SORTINO = "sortino"
    INSUFFICIENT = "insufficient"

@dataclass(frozen=True)
class SharpeConfig:
    min_samples: int = 60
    periods_per_year: int = 252
    risk_free_rate: float = 0.025/252  # 中国10Y国债~2.5%年化
    jb_critical: float = 5.99  # χ²(2) α=0.05
    dsr_threshold: float = 0.95

@dataclass(frozen=True)
class SharpeResult:
    sharpe: float | None          # 非年化(样本不足为None)
    sharpe_annualized: float | None
    sortino: float | None         # 非正态时计算
    sortino_annualized: float | None
    dsr: float | None             # DSR(来自MOD-SIM-024)
    method: SharpeMethod
    is_non_normal: bool
    skewness: float
    kurtosis: float
    jb_statistic: float
    num_obs: int
    risk_free_rate: float
```

## 7. API

```python
class SharpeCalculatorFixer:
    def __init__(self, config: SharpeConfig | None = None) -> None: ...
    def calculate(self, returns, num_trials=1, risk_free_rate=None) -> SharpeResult: ...
    def rolling_sharpe(self, returns, window=60, num_trials=1) -> list[SharpeResult]: ...
```

## 8. 依赖

- `zephyr.simulation.deflated_sharpe_calculator` (DeflatedSharpeCalculator) — data
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-SIM-002 (strategy_simulator), MOD-SIM-012 (result_analyzer)
- 设计真源: 19-D-SIMULATION §1 SIM-23

## 9. 测试

- `tests/simulation/test_sharpe_calculator_fixer.py`
- 覆盖: 样本不足返回None、正态用Sharpe、非正态用Sortino、DSR集成、
  年化、滚动Sharpe、Jarque-Bera检测、中国国债利率默认值

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIM-023`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIM-023` 的 3 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIM-023` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIM-023 | MOD-SIM-023 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/simulation/__init__.py` | ⚠️ 骨架 | |
| `tests/simulation/test_sharpe_calculator_fixer.py` | ✅ 已实现 | |

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
