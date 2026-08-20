---
module_id: MOD-SIM-021
title: "Parameter Robustness Tester 蓝图 — 参数鲁棒性测试器"
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

# MOD-SIM-021 Parameter Robustness Tester — 参数鲁棒性测试器 蓝图

> **module_id**: MOD-SIM-021 | **域**: D_SIMULATION | **层**: L03 仿真
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-033 过拟合系统性防护
> **SSoT**: depgraph MOD-SIM-021 | **设计真源**: 19-D-SIMULATION §1 SIM-21

## 1. 定位

参数鲁棒性测试器——寻找参数**稳定区间**而非最优值, 输出参数敏感性曲线 +
扰动测试 + 稳定区间标注 + 过拟合风险评估。核心思想: 鲁棒参数在较宽范围内
表现稳定(宽稳定区间), 过拟合参数仅在最优点附近表现好(窄峰=高风险)。

属 A 类基础设施(确定性计算), 纯基础层不涉及策略。
**纯基础设施: 不决定"买什么/何时买", 只负责"检查最优参数是不是过拟合的尖峰"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | objective_func (目标函数, 接受参数值返回目标值如Sharpe) | — |
| 输入 | param_name + param_values (参数名+待测值序列) | — |
| 输入 | baseline (基准目标值, None=用max) | — |
| 输出 | ParameterSensitivity (敏感性曲线+稳定区间+过拟合风险) | — |
| 输出 | RobustnessReport (多参数汇总) | — |

## 3. 核心算法

### 3.1 稳定区间检测
```
baseline = max(objective) 或传入值
threshold = baseline * stable_threshold_ratio   (默认 0.9)
stable_points = [p for p in points if p.objective >= threshold]
stable_region = (min(stable_points), max(stable_points))   # 最大连续区间
stable_width = high - low
```

### 3.2 稳定性比率
```
stability_ratio = stable_width / total_range
```
- ratio 高 → 参数鲁棒(宽稳定区间)
- ratio 低 → 参数敏感(窄峰, 过拟合风险)

### 3.3 过拟合风险分级
```
stability_ratio >= 0.5  → LOW    (宽稳定区间, 鲁棒)
0.2 <= ratio < 0.5      → MEDIUM
ratio < 0.2             → HIGH   (窄峰, 高过拟合风险)
```

### 3.4 扰动测试
对基准参数值施加 ±δ 扰动, 测量目标值退化:
```
max_degradation = max(|baseline - objective(perturbed)| / baseline)
max_degradation < threshold → 稳定
```

## 4. 关键不变量 (INVARIANTS)

- RobustnessConfig / ParameterSensitivity / RobustnessReport 等为 frozen dataclass
- stability_ratio ∈ [0, 1]
- 无稳定区间时 stable_region=None, stability_ratio=0
- 过拟合风险分级阈值由 config 控制(可调)
- 纯计算无副作用, 无第三方依赖(纯 math)

## 5. 错误契约

- `SimulationError` (ZA-SIM-0021): 输入非法(空参数序列/单值无法计算区间)

## 6. 数据模型

```python
class OverfitRisk(str, Enum):
    LOW = "low"; MEDIUM = "medium"; HIGH = "high"

@dataclass(frozen=True)
class RobustnessConfig:
    stable_threshold_ratio: float = 0.9
    low_risk_min_ratio: float = 0.5
    high_risk_max_ratio: float = 0.2
    default_perturbations: tuple[float, ...] = (-0.1, -0.05, 0.05, 0.1)
    perturbation_stable_threshold: float = 0.1

@dataclass(frozen=True)
class ParameterPoint:
    param_value: float
    objective: float

@dataclass(frozen=True)
class StableRegion:
    low: float; high: float; width: float; point_count: int

@dataclass(frozen=True)
class ParameterSensitivity:
    param_name: str
    points: list[ParameterPoint]
    optimal_value: float
    optimal_objective: float
    stable_region: StableRegion | None
    total_range: float
    stability_ratio: float
    objective_std: float
    overfit_risk: OverfitRisk

@dataclass(frozen=True)
class RobustnessReport:
    sensitivities: list[ParameterSensitivity]
    overall_stability: float
    overall_overfit_risk: OverfitRisk
    is_robust: bool
```

## 7. API

```python
class ParameterRobustnessTester:
    def __init__(self, config: RobustnessConfig | None = None) -> None: ...
    def test_parameter(
        self, objective_func, param_name, param_values, baseline=None,
    ) -> ParameterSensitivity: ...
    def perturb_parameter(
        self, objective_func, param_name, baseline_value, perturbations=None,
    ) -> PerturbationResult: ...
    def assess(self, sensitivities: list[ParameterSensitivity]) -> RobustnessReport: ...
    def audit_summary(self, report: RobustnessReport) -> str: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-SIM-002 (strategy_simulator 参数稳定性合规检查)
- 设计真源: 19-D-SIMULATION §1 SIM-21

## 9. 测试

- `tests/simulation/test_parameter_robustness_tester.py`
- 覆盖: 鲁棒参数(宽稳定区间→LOW)、过拟合参数(窄峰→HIGH)、稳定区间检测、
  扰动测试、多参数汇总、边界值(空/单值)、配置自定义、frozen不可变、审计摘要

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIM-021`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIM-021` 的 4 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIM-021` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIM-021 | MOD-SIM-021 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 4 文件 | N/A | — |

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
| `tests/simulation/test_parameter_robustness_tester.py` | ✅ 已实现 | |
| `tests/simulation/test_result_analyzer.py` | ✅ 已实现 | |
| `tests/simulation/test_strategy_simulator.py` | ✅ 已实现 | |

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
