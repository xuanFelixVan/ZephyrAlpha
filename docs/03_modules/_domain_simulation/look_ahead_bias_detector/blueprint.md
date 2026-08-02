---
module_id: MOD-SIM-022
title: "Look-Ahead Bias Detector 蓝图 — 未来函数风险检测器"
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

# MOD-SIM-022 Look-Ahead Bias Detector — 未来函数风险检测器 蓝图

> **module_id**: MOD-SIM-022 | **域**: D_SIMULATION | **层**: L03 仿真
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-033 过拟合系统性防护
> **SSoT**: depgraph MOD-SIM-022 | **设计真源**: 19-D-SIMULATION §1 SIM-22

## 1. 定位

未来函数风险检测器——检测回测中的 look-ahead bias(前瞻偏差), 确保所有判断
仅基于当时已知数据。扫描特征矩阵 + 截断重算验证特征函数, 产出偏差清单 +
严重度评估 + 审计摘要, 供回测合规检查和过拟合防护使用。

属 A 类基础设施(确定性数据扫描), 纯基础层不涉及策略。
**纯基础设施: 不决定"买什么/何时买", 只负责"检查回测有没有偷看未来数据"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | df (特征 DataFrame, pandas) | — |
| 输入 | feature_columns (特征列名, 默认全部数值列) | — |
| 输入 | label_column (标签/目标列名) | — |
| 输入 | timestamp_column (时间戳列名) | — |
| 输入 | func + data (截断重算验证模式) | — |
| 输出 | DetectionResult (偏差清单+严重度+审计摘要) | — |

## 3. 检测规则

### 3.1 前瞻列名扫描 (FORWARD_COLUMN_NAME)
列名匹配前瞻模式(`_fwd`/`_forward`/`_future`/`_lead`/`_next`) → MEDIUM;
匹配目标模式(`_target`/`_label`/`_y`)且出现在特征列 → HIGH。

### 3.2 标签泄露 (LABEL_LEAKAGE)
label_column 同时出现在 feature_columns → CRITICAL(标签混入特征)。

### 3.3 尾部 NaN 模式 (FUTURE_SHIFT)
特征列的 NaN 集中在序列尾部(末尾 K 行连续 NaN, 前部无 NaN)→ 提示
`shift(-K)` 类前瞻窗口 → HIGH。前部含 NaN 的列不触发(缺失值正常)。

### 3.4 截断重算验证 (TRUNCATION_MISMATCH) —— 金标准
给定特征函数 `func(data) -> series`:
- `full[i] = func(full_data)[i]`
- `trunc[i] = func(data[:i+1])[i]`
- `full[i] != trunc[i]` → 前瞻偏差(全样本计算用了 i 之后的数据) → CRITICAL。
采样 test_points 个点(默认10)而非逐点, 控制 O(n²) 成本。

### 3.5 时间戳单调性 (NON_MONOTONIC_TIMESTAMP)
timestamp_column 非单调递增或含重复 → MEDIUM(时间点对齐失效)。

## 4. 关键不变量 (INVARIANTS)

- DetectorConfig / BiasIssue / DetectionResult 为 frozen dataclass (不可变)
- DetectionResult.issues 列表按严重度降序排列(CRITICAL→LOW)
- is_clean == (total_issues == 0)
- max_severity 为 None 当且仅当 issues 为空
- 截断重算用采样点(默认10), tolerance=1e-9 判定浮点相等
- 依赖 pandas(2.x); 纯扫描无副作用

## 5. 错误契约

- `SimulationError` (ZA-SIM-0022): 输入非法(空DataFrame/列不存在/func返回长度不匹配)

## 6. 数据模型

```python
@dataclass(frozen=True)
class DetectorConfig:
    forward_name_patterns: tuple[str, ...] = ("_fwd","_forward","_future","_lead","_next")
    target_name_patterns: tuple[str, ...] = ("_target","_label","_y")
    truncation_test_points: int = 10
    truncation_tolerance: float = 1e-9

class BiasType(str, Enum):
    FORWARD_COLUMN_NAME = "forward_column_name"
    LABEL_LEAKAGE = "label_leakage"
    FUTURE_SHIFT = "future_shift"
    TRUNCATION_MISMATCH = "truncation_mismatch"
    NON_MONOTONIC_TIMESTAMP = "non_monotonic_timestamp"

class BiasSeverity(str, Enum):
    LOW = "low"; MEDIUM = "medium"; HIGH = "high"; CRITICAL = "critical"

@dataclass(frozen=True)
class BiasIssue:
    bias_type: BiasType
    severity: BiasSeverity
    column: str | None
    description: str
    evidence: str

@dataclass(frozen=True)
class DetectionResult:
    issues: list[BiasIssue]
    is_clean: bool
    total_issues: int
    critical_count: int
    max_severity: BiasSeverity | None
```

## 7. API

```python
class LookAheadBiasDetector:
    def __init__(self, config: DetectorConfig | None = None) -> None: ...
    def scan(
        self, df, feature_columns=None, label_column=None, timestamp_column=None,
    ) -> DetectionResult: ...
    def validate_function(
        self, func, data, test_indices=None,
    ) -> DetectionResult: ...
    def audit_summary(self, result: DetectionResult) -> str: ...
```

## 8. 依赖

- `pandas` (DataFrame 操作)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-SIM-002 (strategy_simulator 回测合规检查), MOD-SIM-012 (result_analyzer)
- 设计真源: 19-D-SIMULATION §1 SIM-22

## 9. 测试

- `tests/simulation/test_look_ahead_bias_detector.py`
- 覆盖: 干净DataFrame无偏差、前瞻列名检测、标签泄露、尾部NaN检测、
  截断重算验证(有偏差/无偏差)、时间戳单调性、审计摘要、边界值(空/列缺失)、
  严重度排序、配置自定义
