---
module_id: MOD-SIM-022
title: "Look-Ahead Bias Detector 蓝图 — 未来函数风险检测器"
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

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIM-022`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIM-022` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIM-022` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIM-022 | MOD-SIM-022 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

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
| `tests/simulation/test_look_ahead_bias_detector.py` | ✅ 已实现 | |

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
