---
blueprint_id: MOD-AU-007
module_name: risk_manager_agent
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
priority: P0
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/autonomy_core/agents/risk_manager_agent.py
granularity: file
---

# MOD-AU-007 risk_manager_agent 蓝图（风控 Agent / RiskManager）

> **module_id**: MOD-AU-007 | **域**: D_AUTONOMY_CORE | **优先级**: P0
> **来源**: CAND-AUTONOMYCORE-003（B1-00240，AUD-DRAFT-001-DIGEST P0 波 W2d）
> 代码：`src/zephyr/autonomy_core/agents/risk_manager_agent.py`

## 0. 定位

RiskManager 角色（对齐 14号文 §3.0 role façade 四 Agent 族卡模式）：
实时读 risk 引擎限额 / 回撤 / VaR 状态（`RiskEngineState` 由调用方装配注入），
产出**熔断建议**（CircuitBreakerAdvice）与**复盘说明**（review），
触发 trading_kill_switch **仅经确定性校验路径**——硬熔断仍由确定性代码执行，
本 Agent 只在状态确证硬越限时发出触发信号（kill_switch_trigger 回调），
建议与执行**双记录**入审计（audit_sink）。

与 MOD-RK-22 agent_risk_monitor 分工：RK-22 管 agent 交易行为活动窗指标
（下单/拒单/撤单/置信度），本角色管 risk 引擎状态（限额/回撤/VaR）的解释
与熔断编排建议，二者输出互补不重复实现。

## 1. 判定阶梯（确定性阶梯，纯函数）

`assess(state) -> CircuitBreakerAdvice`：
- `kill_switch_active=True` → NONE（已熔断，不重复触发）。
- 硬越限（limits_breached 非空 / drawdown > max_drawdown_limit /
  var_95 > var_limit）→ KILL_SWITCH，recommended_kill_switch_level 按主因映射
  （DAILY_LOSS 回撤 / POSITION_LIMIT 限额 / CIRCUIT_BREAKER VaR）。
- 预警带（drawdown >= warn_ratio×limit 或 var >= warn_ratio×var_limit）→ REDUCE。
- 否则 → NONE。

`act(state)`：assess → 建议审计记录 → KILL_SWITCH 且未激活 → kill_switch_trigger
回调（确定性校验路径，回调即触发点）→ 执行审计记录。回调/sink 异常不阻断判定。

## 2. 接口

```python
class CircuitBreakerLevel(str, Enum): NONE/REDUCE/KILL_SWITCH
@dataclass(frozen=True) RiskEngineState: limits_breached/current_drawdown/max_drawdown_limit/var_95/var_limit/kill_switch_active
@dataclass(frozen=True) RiskManagerThresholds: warn_ratio=0.8
@dataclass(frozen=True) CircuitBreakerAdvice: level/reasons/recommended_kill_switch_level
@dataclass(frozen=True) RiskManagerAction: advice/triggered/audit_records
class RiskManagerAgent(thresholds=None, kill_switch_trigger=None, audit_sink=None):
    ROLE/AGENT_CARD（族卡模式）; .assess(state)/.review(state, advice)->str/.act(state)
class InvalidRiskManagerConfigError / InvalidRiskEngineStateError(ZephyrBaseError)
```

## 3. 不变量

- assess/review 纯函数无 IO；状态输入非法（负回撤/非正上限/VaR 越界）→ InvalidRiskEngineStateError（Fail-Closed）。
- 触发仅当硬越限且 kill_switch 未激活；建议与执行各落一条审计记录（双记录）。
- 配置 warn_ratio∈(0,1) 否则 InvalidRiskManagerConfigError。

## 4. 依赖

- MOD-L04-001 risk_limits（设计边：限额状态真源）
- MOD-RK-22 agent_risk_monitor（设计边：agent 风险报告语义对齐）
- MOD-INF-016 trading_kill_switch（设计边：熔断触发目标，确定性执行体）

## 5. MVP 边界

- 运行时接线（risk 引擎状态轮询装配、kill_switch_trigger 接 trading_kill_switch
  确定性路径、审计持久化接审计链）留运行时装配批；本模块交付角色卡 + 判定
  阶梯纯函数 + 建议/执行双审计契约。
