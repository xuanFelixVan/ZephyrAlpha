---
blueprint_id: MOD-AU-009
module_name: signal_analyst_agent
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
path: src/zephyr/autonomy_core/agents/signal_analyst_agent.py
granularity: file
---

# MOD-AU-009 signal_analyst_agent 蓝图（信号 Agent / SignalAnalyst）

> **module_id**: MOD-AU-009 | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **来源**: B1-00241（AUD-DRAFT-001-DIGEST P1 波 W-P1-11）
> 代码：`src/zephyr/autonomy_core/agents/signal_analyst_agent.py`

## 0. 定位

SignalAnalyst 角色（14号文 §3.0 role façade 族卡模式，与 MOD-AU-007/008
同族）：汇总 C-028 信号工厂输出（`SignalSnapshot` 由调用方装配注入），做
**IC 衰减与拥挤度质量评估**（确定性阶梯），产出**漏斗处置建议**
（FORWARD/DOWNWEIGHT/HOLD_BACK——输出入漏斗，**绝不直接下单**），异常
信号降级建议经 `degrade_sink` 外发。

查重分工：
- MOD-SIG-087 signal_factory（C-028，W-P1-01 已建）：信号生产；本角色只做
  质量裁决与漏斗建议，不重算信号。
- D_SIGQC signal_quality（MOD-INF-040）：信号质量基础设施族；本角色是
  "职责化 Agent 编排层"（衰减/拥挤度→漏斗处置），评估输入由装配层注入，
  不复制 QC 计算件。
- MOD-PLAN-013 trading_analyst_agents：辩论链五角色雏形；本角色为独立
  单职责 Agent（14号文族卡），不下单不辩论。

## 1. 判定阶梯（确定性，纯函数）

`assess(snapshot) -> QualityAssessment`（ic_decay = ic_current/ic_baseline，
baseline ≤ 0 或 NaN → Fail-Closed）：
- 硬降级：ic_decay ≤ crit_ratio 或 crowding ≥ crit → QUARANTINE（HOLD_BACK）；
- 预警带：ic_decay ≤ warn_ratio 或 crowding ≥ warn → DEGRADE（DOWNWEIGHT）；
- 健康：→ PROMOTE（FORWARD）。
`act(snapshot)`：assess → 评估审计 → 非 PROMOTE 时 degrade_sink 降级建议
→ 处置审计。

## 2. 接口

```python
class SignalQualityVerdict(str, Enum): PROMOTE/DEGRADE/QUARANTINE
class FunnelAction(str, Enum): FORWARD/DOWNWEIGHT/HOLD_BACK
@dataclass(frozen=True) SignalSnapshot: signal_id/ic_current/ic_baseline/crowding_score
@dataclass(frozen=True) SignalAnalystThresholds: decay_warn_ratio=0.5/decay_crit_ratio=0.25/crowding_warn=0.7/crowding_crit=0.9
@dataclass(frozen=True) QualityAssessment: verdict/funnel_action/reasons/ic_decay_ratio
@dataclass(frozen=True) SignalAnalystAction: assessment/degrade_adviced/audit_records
class SignalAnalystAgent(thresholds=None, degrade_sink=None, audit_sink=None):
    ROLE/AGENT_CARD（族卡模式）; .assess(snapshot)/.act(snapshot)
class InvalidSignalSnapshotError / InvalidSignalAnalystConfigError(ZephyrBaseError)
```

## 3. 不变量

- assess 纯函数无 IO；snapshot 非法（空 id / ic 越界 [-1,1] / baseline ≤ 0 /
  crowding ∉ [0,1]）→ InvalidSignalSnapshotError（Fail-Closed）。
- 输出永远只到漏斗建议层（FORWARD/DOWNWEIGHT/HOLD_BACK），本角色无下单
  语义（immutable 边界：下单执行属执行域）。
- 非 PROMOTE 必落降级建议审计；sink 异常不阻断判定。

## 4. 依赖

- MOD-SIG-087 signal_factory（设计边：C-028 信号工厂输出汇总面）
- MOD-PLAN-013 trading_analyst_agents（设计边：交易分析 Agent 雏形对齐）

## 5. MVP 边界

- 运行时接线（C-028 输出批量装配 snapshot、degrade_sink 接漏斗权重真实
  调整、SIGQC 指标对接、评估持久化）留运行时装配批；本模块交付角色卡 +
  判定阶梯纯函数 + 漏斗处置/降级建议审计契约。
