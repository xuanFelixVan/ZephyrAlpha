---
blueprint_id: MOD-RK-41
module_name: risk_signal_sequencer
domain: D_RISK
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
domain_id: D_RISK
path: src/zephyr/risk/risk_signal_sequencer.py
granularity: file
---

# MOD-RK-41 risk_signal_sequencer 蓝图（风险-信号交互排序器 / D-SIGNAL-72）

> **module_id**: MOD-RK-41 | **域**: D_RISK | **优先级**: P1
> **来源**: B14-04732（AUD-DRAFT-001-DIGEST P1 波 W-P1-14，A9 运维架构 §8.3.13）
> 代码：`src/zephyr/risk/risk_signal_sequencer.py`

## 0. 定位

**风控事件优先于信号生效的全序定序判定核心**：定义风控 veto/降级/解除事件
优先于新信号生效的全序规则；乱序检测（先生效信号、后到更早发生的风控事件）
+ 冲突仲裁（风控恒胜，信号不可绕过风控）；顺序违规写审计链。

查重分工（W-P1-14 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| risk_layer_orchestrator | MOD-L06-001 | 风控层**运行时执行编排**（回撤/VaR/熔断/清算，D_EX_CORE） | 编排执行面；无定序规则/乱序仲裁 |
| risk_event_consumer | MOD-SIG-088 | E-RK-01 风险事件→信号域降级处置的**消费处理器**（幂等/DLQ/回执） | 消费处置面；不判定"谁先谁后" |
| gov_audit writer | MOD-INF-020 | 审计链写入 | 违规留痕经 audit_sink 委托 |

不做什么：不执行降级/清算（执行面委托既有族）、不做消息传输（事件由调用方
注入）、不直连审计库（audit_sink 注入委托 D_GOV_AUDIT）。

## 1. 判定规则（确定性，纯内存）

事件模型（frozen dataclass）：
- `RiskEvent(event_id, kind∈{VETO,DOWNGRADE,CLEAR}, scope, symbol, occurred_at, seq)`
  ——scope∈{GLOBAL,SYMBOL}，SYMBOL 必带 symbol；
- `SignalEvent(signal_id, symbol, occurred_at, seq)`。

全序规则：同一覆盖范围内，风控事件按 (occurred_at, seq) 先于信号生效；
`CLEAR` 之前的 VETO/DOWNGRADE 处于活跃期，活跃期内新信号一律
`SUPPRESSED`（不可绕过）；`CLEAR` 解除后信号 `ADMITTED`。

乱序检测与仲裁（`ingest` 单事件入口，按到达序处理）：
- 到达风控事件 E：若存在**已生效（ADMITTED）**且 occurred_at/seq 晚于 E 的
  同范围信号 → `ORDER_VIOLATION`，仲裁 `REVOKE_SIGNAL`（撤销该信号生效），
  违规记录经 audit_sink 写审计；
- 到达信号 S：覆盖范围内有活跃 VETO/DOWNGRADE（occurred_at ≤ S.occurred_at
  且未被后续 CLEAR 解除）→ `SUPPRESSED` 留痕；否则 `ADMITTED`；
- 幂等：event_id/signal_id 重复到达 → 返回首判结果不重复处置（deduped=True）；
- 审计：SUPPRESSED/REVOKED/ORDER_VIOLATION 均经 audit_sink 留痕；
  audit_sink 异常不阻断判定（错误计数如实记录）。

## 2. 接口

```python
RiskEventKind: Final = Enum {VETO, DOWNGRADE, CLEAR}
RiskScope: Final = Enum {GLOBAL, SYMBOL}
ArbitrationAction: Final = Enum {ADMITTED, SUPPRESSED, REVOKED}
@dataclass(frozen=True) RiskEvent / SignalEvent
@dataclass(frozen=True) ArbitrationRecord: subject_id/action/reason/violation/
    deduped/risk_event_id
class RiskSignalSequencer(audit_sink=None):
    .ingest_risk(event) -> ArbitrationRecord 列表（含被撤销信号的仲裁记录）
    .ingest_signal(event) -> ArbitrationRecord
    .active_blocks(symbol=None) -> 活跃阻断快照
class InvalidSequencerEventError / InvalidSequencerConfigError(ZephyrBaseError)
```

## 3. 不变量

- 判定核心纯内存无 IO（audit_sink 注入，单测不触库）；
- 字段空白/时间非法/scope=SYMBOL 缺 symbol → InvalidSequencerEventError
  （Fail-Closed 到条）；audit_sink 非 callable（非 None 时）→ 配置 Fail-Closed；
- 风控恒胜：活跃阻断期内信号永不 ADMITTED；乱序必检出必撤销必留痕；
- 幂等去重：同 id 重复事件不重复处置不重复留痕；
- 同输入序列必同输出（按到达序确定判定）；
- frozen dataclass asdict JSON 可序列化；仅定序语义，无下单/执行含义。

## 4. 依赖

- MOD-L06-001 risk_layer_orchestrator（设计边：风控层执行编排分工——其产
  veto/降级语义，本件定序）
- MOD-SIG-088 risk_event_consumer（设计边：风险事件消费处置分工）
- MOD-INF-020 gov_audit writer（设计边：顺序违规审计链委托）

## 5. 测试

`tests/risk/test_risk_signal_sequencer.py`：全序规则（阻断期内信号 SUPPRESSED/
CLEAR 后 ADMITTED/GLOBAL 覆盖全 symbol/SYMBOL 仅覆盖同标的）、乱序检测
（后到更早风控事件→已生效信号 REVOKED+violation）、仲裁风控恒胜、幂等去重、
输入 Fail-Closed、audit_sink 触发范围与异常不阻断、确定性。
