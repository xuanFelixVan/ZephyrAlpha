# [BLUEPRINT] MOD-SIG-088 | docs/03_modules/_domain_signal/risk_event_consumer/blueprint.md
# [MODULE] zephyr.signal_ashare.risk_event_consumer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 信号域降级/撤销/权重调整执行体（action_handler 注入点）；告警路由（lag_exceeded 读取方）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] idempotency_key去重(滑动窗口有界); 重复事件不重复处置; 解析失败/处置异常进DLQ不阻断后续; 每事件产回执; lag超阈值标记lag_exceeded; 纯内存判定核心无IO(stream_client/action_handler/dlq_sink注入)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] stream_client不具read_group->RiskEventConsumerError; 事件处置异常->DLQ+applied=False回执(不上抛)
# [TESTS] tests/signal_ashare/test_risk_event_consumer.py
# [A_module] module_id=MOD-SIG-088 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D-SIGNAL-99 Risk Event E-RK-01 Consumer Handler（CAND-TESTB-028 / B14-04728）。

风险事件到信号域降级处置的消费处理器：Redis Streams 消费组订阅 E-RK-01 风险
事件，幂等键去重 + DLQ 兜底，触发信号降级/撤销/权重调整并回执，消费滞后监控
告警。事件总线与 DLQ 设施已有（shared/event_bus.py、shared/events/dlq.py），
本件补"消费处理器"缺环。

职责：
  - 消费组语义拉取（stream_client 注入式，实现 XREADGROUP 最小语义 read_group）。
  - 幂等：idempotency_key 去重（滑动窗口有界），重复事件产 deduped 回执且不
    重复处置。
  - Fail-safe：事件类型非法/动作未知/action_handler 异常 → DLQ 兜底，
    applied=False 回执；DLQ sink 异常不阻断后续事件。
  - 回执：每个事件产 ConsumeReceipt，ack_hook 外置 ACK/落库。
  - 滞后监控：lag = clock() - occurred_at，超 lag_warn_seconds 标记
    lag_exceeded=True；last_lag_seconds 持续可查。

非职责（MVP 边界）：
  - 真实 Redis Streams client 装配、消费者组注册、告警路由接线留运行时装配批；
    信号降级/撤销/权重调整执行体在信号侧既有件，action_handler 注入委托，
    本件不复制其逻辑。

依据: A9运维架构 §8.3.13；construction_backlog_dig.tsv B14-04728。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: stream_client 参数
#   fields: 参数 stream_client（无注解）
#   code: risk_event_consumer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: group 参数
#   fields: 参数 group（无注解）
#   code: risk_event_consumer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: consumer_name 参数
#   fields: 参数 consumer_name（无注解）
#   code: risk_event_consumer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: action_handler 参数
#   fields: 参数 action_handler（无注解）
#   code: risk_event_consumer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RiskEventConsumer
#   name_en: RiskEventConsumer
#   intro: E-RK-01 风险事件消费处理器。
#   desc: E-RK-01 风险事件消费处理器。 Args: stream_client: 流读取 client（注入式，实现 read_group 协议）。 group: 消费组名。 co…；公共方法（定义序）: seen_co…
#   inputs: stream_client group consumer_name action_handler dlq_sink ack_hook la…
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: RiskEventConsumer
#   downstream: 信号域降级/撤销/权重调整执行体（action_handler 注入点）；告警路由（lag_exceeded 读取方）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping, Protocol

from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__ = [
    "ConsumeReceipt",
    "RiskAction",
    "RiskEvent",
    "RiskEventConsumer",
    "RiskEventConsumerError",
]

_RISK_EVENT_TYPE = "E-RK-01"

_ACTION_MAP = {
    "degrade": "DEGRADE",
    "revoke": "REVOKE",
    "reweight": "REWEIGHT",
}


class RiskEventConsumerError(ZephyrBaseError):
    """消费处理器配置/拉取失败（错误码未登，纪律⑦留错误码对账批）。"""


class RiskAction(str, Enum):
    """风险事件触发的信号处置动作。"""

    DEGRADE = "DEGRADE"
    REVOKE = "REVOKE"
    REWEIGHT = "REWEIGHT"


@dataclass(frozen=True)
class RiskEvent:
    """一条风险事件（E-RK-01 语义最小承载）。

    Attributes:
        event_id: 事件唯一 ID（流条目 ID）。
        event_type: 事件类型（本处理器仅受理 E-RK-01）。
        occurred_at: 事件发生时刻（滞后监控基准）。
        payload: 事件载荷（action/signal_id/weight 等）。
        idempotency_key: 幂等键（去重依据）。
    """

    event_id: str
    event_type: str
    occurred_at: datetime.datetime
    payload: Mapping[str, Any]
    idempotency_key: str


@dataclass(frozen=True)
class ConsumeReceipt:
    """单事件消费回执。

    Attributes:
        event_id: 事件 ID。
        action: 裁定处置动作（未处置为 None）。
        applied: 是否实际处置成功。
        deduped: 是否幂等去重命中。
        reason: 未处置/拒绝理由。
        lag_seconds: 消费滞后秒数。
        lag_exceeded: 滞后是否超阈值。
    """

    event_id: str
    action: RiskAction | None
    applied: bool
    deduped: bool = False
    reason: str = ""
    lag_seconds: float = 0.0
    lag_exceeded: bool = False


class _StreamClient(Protocol):
    """Redis Streams 消费组最小语义（XREADGROUP 对应）。"""

    def read_group(self, *, group: str, consumer: str, max_events: int) -> list[RiskEvent]: ...


class RiskEventConsumer:
    """E-RK-01 风险事件消费处理器。

    Args:
        stream_client: 流读取 client（注入式，实现 read_group 协议）。
        group: 消费组名。
        consumer_name: 消费者名。
        action_handler: 处置委托 ``handler(action, payload) -> bool``
            （信号降级/撤销/权重调整执行体，注入式）。
        dlq_sink: 死信回调 ``sink(record: dict)``（可选，异常不阻断）。
        ack_hook: 回执回调 ``hook(receipt)``（可选）。
        lag_warn_seconds: 滞后告警阈值秒。
        dedup_window: 幂等键滑动窗口容量。
        clock: 时钟注入（测试可控）。
    """

    def __init__(
        self,
        stream_client: _StreamClient,
        *,
        group: str = "signal_ashare",
        consumer_name: str = "risk_event_consumer",
        action_handler: Callable[[RiskAction, Mapping[str, Any]], bool] | None = None,
        dlq_sink: Callable[[dict], None] | None = None,
        ack_hook: Callable[[ConsumeReceipt], None] | None = None,
        lag_warn_seconds: float = 30.0,
        dedup_window: int = 4096,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not hasattr(stream_client, "read_group"):
            # 延迟到 poll_once 抛，构造期允许 stub 装配——但协议检查前置更安全：
            # 本件裁定：构造期不查（鸭子类型），poll 时统一翻译为 ConsumerError。
            pass
        self._client = stream_client
        self._group = group
        self._consumer_name = consumer_name
        self._action_handler = action_handler or (lambda action, payload: True)
        self._dlq_sink = dlq_sink
        self._ack_hook = ack_hook
        self._lag_warn_seconds = float(lag_warn_seconds)
        self._dedup_window = int(dedup_window)
        self._clock = clock or (lambda: datetime.datetime.now(datetime.timezone.utc))
        self._seen_keys: deque[str] = deque(maxlen=self._dedup_window)
        self._seen_key_set: set[str] = set()
        self._seen_count = 0
        self._dlq_count = 0
        self._last_lag_seconds = 0.0

    @property
    def seen_count(self) -> int:
        """已见事件总数（含去重命中）。"""
        return self._seen_count

    @property
    def dlq_count(self) -> int:
        """进 DLQ 事件总数。"""
        return self._dlq_count

    @property
    def last_lag_seconds(self) -> float:
        """最近一批事件的最大滞后秒数。"""
        return self._last_lag_seconds

    def _mark_seen(self, key: str) -> None:
        if len(self._seen_keys) == self._seen_keys.maxlen and self._seen_keys:
            evicted = self._seen_keys[0]
            self._seen_key_set.discard(evicted)
        self._seen_keys.append(key)
        self._seen_key_set.add(key)

    def _to_dlq(self, event: RiskEvent, reason: str) -> None:
        self._dlq_count += 1
        if self._dlq_sink is not None:
            record = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "idempotency_key": event.idempotency_key,
                "reason": reason,
                "payload": dict(event.payload),
                "dead_lettered_at": self._clock().isoformat(),
            }
            try:
                self._dlq_sink(record)
            except Exception:  # noqa: BLE001 — DLQ sink 故障不阻断后续事件
                log.warning("risk_event_consumer: dlq_sink 异常，仅计数留痕", exc_info=True)

    def _lag_of(self, event: RiskEvent) -> float:
        lag = (self._clock() - event.occurred_at).total_seconds()
        return max(0.0, lag)

    def _handle_one(self, event: RiskEvent) -> ConsumeReceipt:
        lag = self._lag_of(event)
        self._last_lag_seconds = max(self._last_lag_seconds, lag)
        lag_exceeded = lag > self._lag_warn_seconds
        self._seen_count += 1

        if event.idempotency_key in self._seen_key_set:
            return ConsumeReceipt(
                event_id=event.event_id,
                action=None,
                applied=False,
                deduped=True,
                reason="幂等键重复，跳过处置",
                lag_seconds=lag,
                lag_exceeded=lag_exceeded,
            )
        self._mark_seen(event.idempotency_key)

        if event.event_type != _RISK_EVENT_TYPE:
            reason = f"事件类型不受理: {event.event_type!r}（仅受理 {_RISK_EVENT_TYPE}）"
            self._to_dlq(event, reason)
            return ConsumeReceipt(event.event_id, None, False, False, reason, lag, lag_exceeded)

        raw_action = str(event.payload.get("action", "")).lower()
        mapped = _ACTION_MAP.get(raw_action)
        if mapped is None:
            reason = f"未知处置动作: {raw_action!r}"
            self._to_dlq(event, reason)
            return ConsumeReceipt(event.event_id, None, False, False, reason, lag, lag_exceeded)
        action = RiskAction(mapped)

        try:
            applied = bool(self._action_handler(action, event.payload))
        except Exception as exc:  # noqa: BLE001 — 处置异常进 DLQ 不上抛
            reason = f"处置执行异常: {exc}"
            self._to_dlq(event, reason)
            return ConsumeReceipt(event.event_id, action, False, False, reason, lag, lag_exceeded)

        reason = "" if applied else "处置执行体返回未生效"
        return ConsumeReceipt(event.event_id, action, applied, False, reason, lag, lag_exceeded)

    def poll_once(self, max_events: int = 10) -> list[ConsumeReceipt]:
        """拉取一批事件并逐条处置，返回回执列表。"""
        try:
            events = self._client.read_group(group=self._group, consumer=self._consumer_name, max_events=max_events)
        except AttributeError as exc:
            raise RiskEventConsumerError(f"stream_client 不具 read_group 协议: {exc}") from exc
        except Exception as exc:  # noqa: BLE001 — 拉取边界统一翻译
            raise RiskEventConsumerError(f"风险事件拉取失败: {exc}") from exc

        self._last_lag_seconds = 0.0
        receipts: list[ConsumeReceipt] = []
        for event in events:
            receipt = self._handle_one(event)
            receipts.append(receipt)
            if self._ack_hook is not None:
                try:
                    self._ack_hook(receipt)
                except Exception:  # noqa: BLE001 — 回执 hook 故障不阻断
                    log.warning("risk_event_consumer: ack_hook 异常", exc_info=True)
        return receipts
