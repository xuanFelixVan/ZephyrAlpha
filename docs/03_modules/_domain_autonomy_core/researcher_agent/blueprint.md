---
blueprint_id: MOD-AU-008
module_name: researcher_agent
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/autonomy_core/agents/researcher_agent.py
granularity: file
---

# MOD-AU-008 researcher_agent 蓝图（研究 Agent / Researcher）

> **module_id**: MOD-AU-008 | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **来源**: B1-00238（AUD-DRAFT-001-DIGEST P1 波 W-P1-11）
> 代码：`src/zephyr/autonomy_core/agents/researcher_agent.py`
> **canonical 声明**：B11-02483（W-P1-12，同名"研究Agent（Researcher）"）以本
> 模块为 canonical 实现，重复候选按 REVIEW 归并到本模块。

## 0. 定位

Researcher 角色（对齐 14号文 §3.0 role façade 族卡模式，与 MOD-AU-007
RiskManager 同族）：因子假设（`FactorHypothesis`）→ 实验指标
（`ExperimentMetrics`，由 C-027 因子工厂实验与 C-003 回测门禁产出后注入）
→ 确定性**研究裁决**（ACCEPT/REJECT/NEEDS_MORE_DATA）→ 研究报告
（`ResearchReport`）经 `report_sink` 外发，**入库人工门禁**
（`human_gate_trigger` 回调，本 Agent 不直接入库）；实验登记委托
experiment_tracking（`experiment_sink` 回调，不 import 不复制）。

不做什么：不算因子（C-027 职责）、不跑回测（C-003 职责）、不写
experiment_tracking（MOD-OBS-001 职责）、不直接落库（人工门禁后由装配层
执行）。本 Agent 只做"假设→证据→裁决→报告"的编排判定。

## 1. 判定阶梯（确定性，纯函数）

`evaluate(hypothesis, metrics) -> ResearchVerdict`：
- 门禁硬否：max_drawdown 超限 或样本数 < min_samples → REJECT；
- 达标：ic ≥ min_ic 且 sharpe ≥ min_sharpe → ACCEPT；
- 边缘（ic 或 sharpe 单达标，或 ic ∈ [min_ic/2, min_ic)）→ NEEDS_MORE_DATA；
- 其余 → REJECT。
`act(hypothesis, metrics)`：evaluate → 实验登记审计（experiment_sink）→
报告草稿（纯函数）→ report_sink 外发 → ACCEPT 时 human_gate_trigger
（人工门禁信号）→ 双审计记录。

## 2. 接口

```python
class ResearchVerdict(str, Enum): ACCEPT/REJECT/NEEDS_MORE_DATA
@dataclass(frozen=True) FactorHypothesis: hypothesis_id/name/expression/rationale
@dataclass(frozen=True) ExperimentMetrics: ic/sharpe/max_drawdown/sample_count
@dataclass(frozen=True) ResearcherThresholds: min_ic=0.03/min_sharpe=1.0/max_drawdown=0.2/min_samples=60
@dataclass(frozen=True) ResearchReport: hypothesis_id/verdict/reasons/metrics/requires_human_gate
@dataclass(frozen=True) ResearcherAction: verdict/report/gate_signaled/audit_records
class ResearcherAgent(thresholds=None, experiment_sink=None, report_sink=None, human_gate_trigger=None):
    ROLE/AGENT_CARD（族卡模式）; .evaluate(hypothesis, metrics)/.draft_report(...)/.act(...)
class InvalidHypothesisError / InvalidExperimentMetricsError / InvalidResearcherConfigError(ZephyrBaseError)
```

## 3. 不变量

- evaluate/draft_report 纯函数无 IO；假设非法（空 id/name/expression）→
  InvalidHypothesisError；指标非法（ic/sharpe 越界 [-1,1] 外 NaN 语义、
  负回撤、负样本）→ InvalidExperimentMetricsError（Fail-Closed）。
- 报告永远 requires_human_gate=True（入库必过人工门禁）；回调/sink 异常
  不阻断判定，gate_signaled 如实记录；建议与门禁信号双审计记录。
- 配置阈值非法（min_ic∉(0,1] 等）→ InvalidResearcherConfigError。

## 4. 依赖

- MOD-OBS-001 experiment_tracker（设计边：实验登记委托）
- MOD-AU-001 autonomy_boundary_gate（设计边：人工门禁信号对齐）

## 5. MVP 边界

- 运行时接线（C-027 工厂实验产出接入、C-003 回测门禁指标装配、
  experiment_sink 接 experiment_tracking 真实登记、human_gate_trigger 接
  人工门禁链、报告入库持久化）留运行时装配批；本模块交付角色卡 + 判定
  阶梯纯函数 + 报告草稿 + 门禁信号/双审计契约。
