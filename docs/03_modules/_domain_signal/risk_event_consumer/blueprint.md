---
blueprint_id: MOD-SIG-088
module_name: risk_event_consumer
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_ASHARE_SIGNAL
path: src/zephyr/signal_ashare/risk_event_consumer.py
granularity: file
---

# MOD-SIG-088 risk_event_consumer 蓝图（D-SIGNAL-99 Risk Event E-RK-01 Consumer Handler）

> **module_id**: MOD-SIG-088 | **域**: D_ASHARE_SIGNAL | **优先级**: P1
> **来源**: CAND-TESTB-028（B14-04728，AUD-DRAFT-001-DIGEST P1 波 W-P1-06）
> 代码：`src/zephyr/signal_ashare/risk_event_consumer.py`

## 0. 定位

风险事件到信号域降级处置的消费处理器：Redis Streams 消费组订阅 E-RK-01 风险
事件，幂等键去重 + DLQ 兜底，触发信号降级/撤销/权重调整并回执，消费滞后监控
告警。事件总线与 DLQ 设施已有（shared/event_bus.py、shared/events/dlq.py），
本件补"消费处理器"缺环；跨域运维事件从"单域自治"升级"全域协同"关键件。

## 1. 接口

```python
class RiskAction(str, Enum): DEGRADE/REVOKE/REWEIGHT
@dataclass(frozen=True) RiskEvent: event_id/event_type/occurred_at/payload/idempotency_key
@dataclass(frozen=True) ConsumeReceipt: event_id/action/applied/deduped/reason/lag_seconds
class RiskEventConsumer(stream_client, *, group="signal_ashare", consumer_name=...,
                        action_handler=None, dlq_sink=None, ack_hook=None,
                        lag_warn_seconds=30.0, clock=None):
    .poll_once(max_events=10) -> list[ConsumeReceipt]   # 拉一批→幂等去重→处置→回执
    .seen_count / dlq_count / last_lag_seconds           # 监控指标快照
class RiskEventConsumerError(ZephyrBaseError)            # 未挂错误码（纪律⑦）
```

## 2. 不变量

- 幂等：idempotency_key 去重（进程内滑动窗口集合），重复事件产 deduped=True
  回执且不重复处置；处置动作委托 action_handler（信号降级/撤销/权重调整的
  执行体在信号侧，本件不复制其逻辑）。
- Fail-safe：事件解析失败/action_handler 抛错 → 事件进 dlq_sink（DLQ 兜底），
  回执 applied=False + reason；DLQ sink 异常不阻断后续事件。
- 回执：每个事件（含去重/入 DLQ）产 ConsumeReceipt，ack_hook 外置 ACK/落库。
- 滞后监控：lag = clock() - occurred_at，超 lag_warn_seconds 的回执标记
  lag_exceeded=True 供告警路由读取；last_lag_seconds 持续可查。
- 纯内存判定核心：stream_client 注入式（Redis Streams XREADGROUP 语义由
  client 实现，测试用内存 stub），本件不 import redis。

## 3. 依赖

- shared/event_bus.py（事件总线语义对齐，设计边）
- shared/events/dlq.py（DLQ 兜底语义对齐，设计边）
- 信号降级/撤销/权重调整执行体（信号侧既有件，action_handler 注入点）

## 4. MVP 边界

- 真实 Redis Streams client 装配、消费者组注册、告警路由接线留运行时装配批；
  本模块只交付消费处置判定核心（去重/DLQ/回执/滞后监控）。
