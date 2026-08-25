---
blueprint_id: MOD-AU-011
module_name: t0_trader_agent
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
path: src/zephyr/autonomy_core/agents/t0_trader_agent.py
granularity: file
---

# MOD-AU-011 t0_trader_agent 蓝图（做T Agent / T0Trader）

> **module_id**: MOD-AU-011 | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **来源**: B1-00244（AUD-DRAFT-001-DIGEST P1 波 W-P1-11）
> 代码：`src/zephyr/autonomy_core/agents/t0_trader_agent.py`

## 0. 定位

T0Trader 角色（14号文 §3.0 role façade 族卡模式，与 MOD-AU-007~010 同族）：
做T 信号即时裁决编排——**底仓不变硬约束** + **T+1 可卖校验**
（t1_sellable 口径：卖出腿量 ≤ 可卖底仓，当日买入不可卖）+ 单笔价差
（min_edge_bp）与当日次数限额（max_trades_per_day）→ EXECUTE/SKIP/REJECT
建议；建议**经风控校验后生效**（risk_check_trigger），执行委托 C-012
管线（execution_sink，本 Agent 不产生任何生效指令）。

查重分工：
- MOD-SIG-068 t0_point_analyzer：做T 信号点检测与回验（信号源）。
- MOD-SELL-018 t_trade_coordinator：做T 计划生成（两腿权重/成本口径，
  生产）；本角色只做即时裁决编排，不重复计划生成。
- MOD-POS-018 intraday_position_constraint / t1_sellable：底仓与 T+1 可卖
  真源；本角色消费其结论（sellable_qty 注入），不复制校验本体。

## 1. 判定阶梯（确定性，纯函数）

`decide(ctx) -> T0Advice`（requires_risk_check 恒 True）：
1. 无信号（t0_signal=None）→ SKIP；
2. trades_done_today ≥ max_trades_per_day → SKIP（次数限额）；
3. expected_edge_bp < min_edge_bp → SKIP（净价差不足，不值得做的T不做）；
4. T卖 且 sellable_qty ≤ 0 → REJECT（无可卖底仓，T+1 硬约束不可执行）；
5. EXECUTE：direction=信号方向；suggested_qty = min(proposed_qty,
   卖出腿可卖, max_qty_per_leg)，截断留痕；底仓不变（买回=卖出）注入理由。
`act(ctx)`：decide → 裁决审计 → EXECUTE 时 risk_check_trigger（风控前置）
+ execution_sink（执行建议外发委托 C-012 管线）→ 执行审计。

## 2. 接口

```python
class T0Decision(str, Enum): EXECUTE/SKIP/REJECT
@dataclass(frozen=True) T0Context: symbol/base_position/sellable_qty/t0_signal/expected_edge_bp/trades_done_today/proposed_qty
@dataclass(frozen=True) T0Constraints: min_edge_bp=30/max_trades_per_day=3/max_qty_per_leg
@dataclass(frozen=True) T0Advice: decision/direction/suggested_qty/reasons/requires_risk_check
@dataclass(frozen=True) T0TraderAction: advice/risk_check_signaled/execution_handed_off/audit_records
class T0TraderAgent(constraints=None, risk_check_trigger=None, execution_sink=None, audit_sink=None):
    ROLE/AGENT_CARD（族卡模式）; .decide(ctx)/.act(ctx)
class InvalidT0ContextError / InvalidT0ConstraintsError(ZephyrBaseError)
```

## 3. 不变量

- decide 纯函数无 IO；ctx 非法（空 symbol / 负底仓 / 负可卖 / 信号出封闭集 /
  负价差 / 负次数 / 非正 proposed_qty）→ InvalidT0ContextError（Fail-Closed）。
- 底仓不变硬约束：卖出腿 suggested_qty ≤ sellable_qty；本角色无下单语义
  （执行委托 C-012 管线）；建议永远 requires_risk_check=True。
- EXECUTE 必发风控前置信号 + 执行外发并双审计；回调/sink 异常不阻断判定。

## 4. 依赖

- MOD-SIG-068 t0_point_analyzer（设计边：做T 信号源）
- MOD-SELL-018 t_trade_coordinator（设计边：做T 计划生成对齐，不重复实现）
- MOD-POS-018 intraday_position_constraint（设计边：底仓/T+1 可卖约束对齐）

## 5. MVP 边界

- 运行时接线（做T 信号实时接入、t1_sellable 可卖装配、risk_check_trigger
  接风控校验链、execution_sink 接 C-012 做T 日内套利管线、次数台账持久化）
  留运行时装配批；本模块交付角色卡 + 判定阶梯纯函数 + 风控前置/执行外发
  双审计契约。
