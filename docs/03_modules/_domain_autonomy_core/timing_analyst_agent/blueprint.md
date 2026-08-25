---
blueprint_id: MOD-AU-010
module_name: timing_analyst_agent
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/autonomy_core/agents/timing_analyst_agent.py
granularity: file
---

# MOD-AU-010 timing_analyst_agent 蓝图（择时 Agent / TimingAnalyst）

> **module_id**: MOD-AU-010 | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **来源**: B1-00242（AUD-DRAFT-001-DIGEST P1 波 W-P1-11）
> 代码：`src/zephyr/autonomy_core/agents/timing_analyst_agent.py`

## 0. 定位

TimingAnalyst 角色（14号文 §3.0 role façade 族卡模式，与 MOD-AU-007/008/009
同族）：综合 C-021 大盘状态（regime_state）+ C-014 大盘预测
（forecast_score）+ 做T 点位（t0_signal，MOD-SIG-068 口径），给出
**开/加/减仓时机**（OPEN/ADD/REDUCE/HOLD）与**执行策略**
（市价/限价/拆单）建议；建议**经风控校验后才生效**
（risk_check_trigger 回调，本 Agent 不产生任何生效指令）。

查重分工：regime 判定归 MOD-REGIME-001；做T 点位归 MOD-SIG-068；执行
策略选择本体归 MOD-EX-062 execution_strategy_selector；本角色只做三者
输入的融合裁决与风控前置信号，不复制任何计算件。

## 1. 判定阶梯（确定性，纯函数）

`advise(ctx) -> TimingAdvice`（requires_risk_check 恒 True）：
1. regime=volatile：forecast ≤ 减仓线 → REDUCE+SLICED；否则 HOLD；
2. forecast ≤ 减仓线（默认 -0.3）→ REDUCE+SLICED（拆单减）；
3. t0=T卖 且 forecast < 开仓线 → REDUCE+LIMIT（做T卖点联动）；
4. forecast ≥ 强开线（默认 0.6）且 t0=T买 → OPEN+MARKET（强共振市价）；
5. forecast ≥ 开仓线（默认 0.3）且 t0=T买 → OPEN+LIMIT（择时点共振限价）；
6. forecast ≥ 开仓线 → ADD+SLICED（无点位共振拆单加）；
7. 其余 → HOLD。
`act(ctx)`：advise → 建议审计 → 非 HOLD 时 risk_check_trigger（风控前置
信号）→ 校验审计。

## 2. 接口

```python
class TimingAction(str, Enum): OPEN/ADD/REDUCE/HOLD
class ExecutionStyle(str, Enum): MARKET/LIMIT/SLICED
@dataclass(frozen=True) TimingContext: regime_state{trending,range,volatile}/forecast_score∈[-1,1]/t0_signal∈{None,T买,T卖}
@dataclass(frozen=True) TimingAnalystThresholds: open_threshold=0.3/strong_open_threshold=0.6/reduce_threshold=-0.3
@dataclass(frozen=True) TimingAdvice: action/execution_style/reasons/requires_risk_check
@dataclass(frozen=True) TimingAnalystAction: advice/risk_check_signaled/audit_records
class TimingAnalystAgent(thresholds=None, risk_check_trigger=None, audit_sink=None):
    ROLE/AGENT_CARD（族卡模式）; .advise(ctx)/.act(ctx)
class InvalidTimingContextError / InvalidTimingAnalystConfigError(ZephyrBaseError)
```

## 3. 不变量

- advise 纯函数无 IO；ctx 非法（regime 出封闭集/forecast 越界/t0 出封闭集）
  → InvalidTimingContextError（Fail-Closed）。
- 建议永远 requires_risk_check=True（经风控校验后生效）；本角色无下单语义。
- 非 HOLD 必发风控前置信号并双审计；回调/sink 异常不阻断判定。

## 4. 依赖

- MOD-REGIME-001 regime_detector（设计边：C-021 状态真源）
- MOD-SIG-068 t0_point_analyzer（设计边：做T 点位联动）
- MOD-EX-062 execution_strategy_selector（设计边：执行策略选择本体对齐）

## 5. MVP 边界

- 运行时接线（C-021/C-014 实时输入装配、risk_check_trigger 接风控校验链、
  建议生效后的执行策略选择接 MOD-EX-062、审计持久化）留运行时装配批；
  本模块交付角色卡 + 判定阶梯纯函数 + 风控前置信号/双审计契约。
