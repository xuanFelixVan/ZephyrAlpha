---
module_id: MOD-RPT-026
title: "A股绩效审计与优化触发器蓝图 — 绩效审计+5类审计规则+自动触发优化建议+哈希指纹"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
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

# MOD-RPT-026 A-Share Performance Audit — A股绩效审计与优化触发器 蓝图

> **module_id**: MOD-RPT-026 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-010(报告归档/审计)
> **SSoT**: depgraph MOD-RPT-026 | **设计真源**: D:\临时工作区\依赖图\10-D-REPORTING-报告域.md §1.2 D-REPORTING-26, §2.1

## 1. 定位

A股绩效审计与优化触发器——报告域绩效审计基座。消费归因结果(CTR-P1-009) +
绩效指标, 执行 5 类审计规则, 自动触发优化建议。

5 类审计规则:
  - 收益率审计: 实际收益率 vs 阈值 (WARNING/CRITICAL)
  - 回撤审计: 最大回撤 vs 阈值 (WARNING/CRITICAL)
  - 风险调整收益审计: Sharpe/Sortino vs 阈值
  - 归因一致性校验: allocation+selection+interaction ≈ total_return
  - 交易成本审计: transaction_cost_drag vs 预期成本比例

优化建议: 基于审计发现自动生成 (STRATEGY_ADJUST/RISK_TIGHTEN/POSITION_ADJUST/
PARAM_OPTIMIZE/COST_CONTROL), 优先级 HIGH/MEDIUM/LOW。纯建议输出, 不自动执行。

属 A 类基础设施(确定性审计 + 规则触发), 纯消费层不发布事件(D-RPT-D01)。
**纯基础设施: 不决定优化动作, 只负责"审计绩效+生成建议"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | performance_metrics (return_pct/max_drawdown/sharpe_ratio/sortino_ratio) | dict |
| 输入 | attribution_result (total_return/allocation/selection/interaction/cost_drag) | CTR-P1-009 |
| 输入 | expected_cost (预期交易成本, 可选) | float |
| 输出 | PerformanceAuditReport (含 findings + recommendations + data_hash) | — |
| 输出 | validate_report 结果 (bool, 完整性校验) | — |

## 3. 核心规则

### 3.1 审计阈值 (AuditThresholds, C 类可调参数)

```python
@dataclass(frozen=True)
class AuditThresholds:
    return_warning: float = -0.01      # -1%
    return_critical: float = -0.05     # -5%
    drawdown_warning: float = -0.10    # -10%
    drawdown_critical: float = -0.15   # -15%
    sharpe_warning: float = 0.0
    sharpe_info: float = 0.5
    sortino_warning: float = 0.0
    attribution_tolerance: float = 0.001  # 0.1% 误差容忍
    cost_warning_ratio: float = 1.5    # 实际/预期 > 1.5
    cost_critical_ratio: float = 2.0   # 实际/预期 > 2.0
```

### 3.2 收益率审计

| 条件 | 严重度 |
|------|--------|
| return_pct < return_critical (-5%) | CRITICAL |
| return_pct < return_warning (-1%) | WARNING |
| return_pct >= return_warning | (无发现) |

### 3.3 回撤审计

| 条件 | 严重度 |
|------|--------|
| max_drawdown < drawdown_critical (-15%) | CRITICAL |
| max_drawdown < drawdown_warning (-10%) | WARNING |

### 3.4 风险调整收益审计

| 条件 | 严重度 |
|------|--------|
| sharpe_ratio < sharpe_warning (0.0) | WARNING |
| sharpe_ratio < sharpe_info (0.5) 且 >= 0.0 | INFO |
| sortino_ratio < sortino_warning (0.0) | WARNING |

### 3.5 归因一致性校验

- 校验: |allocation_effect + selection_effect + interaction_effect - total_return| > attribution_tolerance
- 不一致 → WARNING (归因分解不自洽)

### 3.6 交易成本审计

- 当 expected_cost 提供时:
  - cost_ratio = transaction_cost_drag / expected_cost
  - cost_ratio > cost_critical_ratio (2.0) → CRITICAL
  - cost_ratio > cost_warning_ratio (1.5) → WARNING
- expected_cost 未提供时: 跳过成本审计

### 3.7 优化建议触发规则

| 审计发现 | 建议类型 | 优先级 |
|---------|---------|--------|
| 收益率 CRITICAL | STRATEGY_ADJUST | HIGH |
| 回撤 CRITICAL | RISK_TIGHTEN | HIGH |
| 成本 CRITICAL | COST_CONTROL | HIGH |
| Sharpe WARNING | PARAM_OPTIMIZE | MEDIUM |
| 归因不一致 | STRATEGY_ADJUST | MEDIUM |
| 收益率 WARNING | STRATEGY_ADJUST | MEDIUM |
| 回撤 WARNING | RISK_TIGHTEN | MEDIUM |
| 成本 WARNING | COST_CONTROL | LOW |
| Sortino WARNING | PARAM_OPTIMIZE | LOW |
| Sharpe INFO | (无建议) | — |

### 3.8 data_hash 防篡改

```
data_hash = SHA-256(canonical_json(report_content))
```
report_content = performance_summary + attribution_summary + findings + recommendations。
validate_report 重算 data_hash 比对。

## 4. 关键不变量 (INVARIANTS)

- PerformanceAuditReport / AuditFinding / OptimizationRecommendation 为 frozen dataclass
- 审计规则确定性: 同输入 → 同输出 (无随机性)
- 阈值全部封装在 AuditThresholds (C 类可调参数), 非硬编码
- data_hash = SHA-256(canonical_json(content)), 篡改可检测
- 纯建议输出: recommendations 不自动执行, 需人工审批
- 纯消费层不发布事件 (D-RPT-D01)

## 5. 错误契约

- `InvalidAuditInputError` (ZA-RPT-0026): performance_metrics 缺必填字段 / attribution_result 为空

## 6. 数据模型

```python
class AuditCategory(str, Enum):
    RETURN = "return"
    DRAWDOWN = "drawdown"
    RISK_ADJUSTED = "risk_adjusted"
    ATTRIBUTION = "attribution"
    COST = "cost"

class AuditSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class RecommendationType(str, Enum):
    STRATEGY_ADJUST = "strategy_adjust"
    RISK_TIGHTEN = "risk_tighten"
    POSITION_ADJUST = "position_adjust"
    PARAM_OPTIMIZE = "param_optimize"
    COST_CONTROL = "cost_control"

class RecommendationPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass(frozen=True)
class AuditFinding:
    finding_id: str
    category: AuditCategory
    severity: AuditSeverity
    metric_name: str
    actual_value: float
    threshold: float
    description: str

@dataclass(frozen=True)
class OptimizationRecommendation:
    recommendation_id: str
    finding_id: str
    type: RecommendationType
    priority: RecommendationPriority
    description: str
    target_module: str

@dataclass(frozen=True)
class PerformanceAuditReport:
    report_id: str
    portfolio_id: str
    audit_period: str
    generated_at: datetime
    performance_summary: dict
    attribution_summary: dict
    findings: list[dict]
    recommendations: list[dict]
    data_hash: str
    schema_version: str = "1.0"
```

## 7. API

```python
class ASharePerformanceAuditor:
    def __init__(self, thresholds: AuditThresholds | None = None): ...
    def audit(
        self,
        portfolio_id: str,
        audit_period: str,
        performance_metrics: dict,
        attribution_result: dict,
        expected_cost: float | None = None,
    ) -> PerformanceAuditReport: ...
    def validate_report(self, report: PerformanceAuditReport) -> bool: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `zephyr.shared.contracts.performance_attribution_report` (CTR-P1-009, 归因报告契约)
- 消费者: D-REPORTING-03 Report Publisher (审计报告发布), D-PF-CORE (优化建议消费)
- 设计真源: D-REPORTING §1.2 D-REPORTING-26, §2.1

## 9. 测试

- `tests/reporting/test_ashare_performance_audit.py`
- 覆盖: 5类审计规则(收益率/回撤/风险调整/归因一致性/交易成本)、
  优化建议触发(10种映射)、阈值可配置、data_hash确定性+篡改检测、
  frozen不可变、边界值(空metrics/缺必填字段/expected_cost=None)、
  归因一致性校验(误差容忍/超出阈值)、多finding聚合

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RPT-026`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RPT-026` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RPT-026` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RPT-026 | MOD-RPT-026 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

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
| `src/zephyr/reporting/ashare_performance_audit.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_ashare_performance_audit.py` | ✅ 已实现 | |

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


