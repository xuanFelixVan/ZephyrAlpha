# [BLUEPRINT] MOD-INF-090 | docs/03_modules/_domain_infrastructure_operations/strategic_message_bus/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.strategic_message_bus
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] 无（协议核心纯内存；a2a_gateway/audit_sink/clock/agent_layers 全注入）
# [CONSUMERS] 运行时装配批（战略/战术/执行三层总线实例装配 / A2A 检查网关绑定 / 审计留痕路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层词表闭合(strategic|tactical|execution); topic 命名空间前缀匹配层词表; 订阅权限=仅本层 topic; 发布同层直连+层间强制 A2A 网关(未注入 Fail-Closed 不旁路); 层内直连层间留痕审计; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/strategic_message_bus/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StrategicBusError(占位 ZA-INF-UNREGISTERED-STRATEGIC-BUS)——空topic/未知前缀/未知agent/越权订阅/网关缺失/网关拒绝时抛
# [TESTS] tests/infrastructure/test_strategic_message_bus.py
# [A_module] module_id=MOD-INF-090 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""StrategicMessageBus — 战略层三层逻辑消息总线（MOD-INF-090）。

B11-02493（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAA2A-002，A7-Agent
架构）：strategic.* / tactical.* / execution.* 三层 topic 命名空间校验 +
发布订阅权限按 Agent 层级校验（层级表注入）+ 跨层消息强制流经 A2A 检查
网关（注入网关回调，未注入 Fail-Closed）+ 层内直连层间留痕（审计回
调）。战术层/执行层总线作为同机制实例（layer 参数实例化）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "BusAudit",
    "BusLayer",
    "StrategicBusError",
    "StrategicMessageBus",
]


class StrategicBusError(Exception):
    """三层总线协议输入/权限非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-STRATEGIC-BUS。
    """


class BusLayer(str, Enum):
    """总线层级（词表闭合，与 topic 前缀一一对应）。"""

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    EXECUTION = "execution"


#: topic 前缀 → 层级（前缀匹配："<layer>."）
_PREFIX_TO_LAYER: Final[dict[str, BusLayer]] = {layer.value: layer for layer in BusLayer}


@dataclass(frozen=True)
class BusAudit:
    """总线留痕审计载荷（frozen）。"""

    agent_id: str
    topic: str
    path: str  # "intra_layer" | "cross_layer"
    at: datetime.datetime


class StrategicMessageBus:
    """三层逻辑总线件（命名空间校验 + 层级权限 + 跨层网关 + 审计）。"""

    def __init__(
        self,
        *,
        layer: BusLayer,
        agent_layers: Mapping[str, BusLayer],
        a2a_gateway: Callable[[str, str, Mapping], bool] | None = None,
        audit_sink: Callable[[BusAudit], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not isinstance(layer, BusLayer):
            raise StrategicBusError(f"非法总线层级: {layer!r}")
        if not agent_layers:
            raise StrategicBusError("agent_layers 为空（无 Agent 层级声明）")
        for agent_id, agent_layer in agent_layers.items():
            if not agent_id:
                raise StrategicBusError("agent_id 为空")
            if not isinstance(agent_layer, BusLayer):
                raise StrategicBusError(f"非法 Agent 层级: {agent_id}={agent_layer!r}")
        self._layer = layer
        self._agent_layers: dict[str, BusLayer] = dict(agent_layers)
        self._gateway = a2a_gateway
        self._audit_sink = audit_sink
        self._clock = clock or datetime.datetime.now
        self._subs: dict[str, list[tuple[str, Callable[[Mapping], None]]]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _topic_layer(self, topic: str) -> BusLayer:
        if not topic:
            raise StrategicBusError("topic 为空")
        prefix, sep, _ = topic.partition(".")
        if not sep or prefix not in _PREFIX_TO_LAYER:
            raise StrategicBusError(
                f"topic 命名空间非法: {topic!r}（须 strategic.*/tactical.*/execution.* 前缀）"
            )
        return _PREFIX_TO_LAYER[prefix]

    def _layer_of(self, agent_id: str) -> BusLayer:
        layer = self._agent_layers.get(agent_id)
        if layer is None:
            raise StrategicBusError(f"未知 agent: {agent_id!r}（未在层级声明中）")
        return layer

    def _audit(self, agent_id: str, topic: str, path: str) -> None:
        record = BusAudit(agent_id=agent_id, topic=topic, path=path, at=self._clock())
        _log.info("总线留痕: %s -> %s (%s)", agent_id, topic, path)
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception:  # noqa: BLE001 — 审计回调不阻断主路
                _log.exception("audit_sink 留痕失败")

    # ── 订阅（权限=仅本层 topic） ──────────────────────────────────────────

    def subscribe(
        self,
        agent_id: str,
        topic: str,
        handler: Callable[[Mapping], None],
    ) -> None:
        """订阅：Agent 仅可订本层 topic（越层订阅 → Fail-Closed）。"""
        agent_layer = self._layer_of(agent_id)
        topic_layer = self._topic_layer(topic)
        if topic_layer is not agent_layer:
            raise StrategicBusError(
                f"越权订阅拒绝: {agent_id}({agent_layer.value}) 订 {topic!r}（仅可订本层 topic）"
            )
        self._subs.setdefault(topic, []).append((agent_id, handler))

    # ── 发布（同层直连 / 跨层强制网关） ─────────────────────────────────────

    def publish(self, agent_id: str, topic: str, payload: Mapping) -> str:
        """发布：同层直连投递+留痕；跨层强制 A2A 网关（未注入 Fail-Closed）。"""
        if payload is None:
            raise StrategicBusError("payload 不可为 None")
        agent_layer = self._layer_of(agent_id)
        topic_layer = self._topic_layer(topic)

        if topic_layer is not agent_layer:
            # 跨层消息：强制流经 A2A 检查网关，禁止旁路直传
            if self._gateway is None:
                raise StrategicBusError(
                    "a2a_gateway 未注入（跨层消息强制 A2A 检查网关，禁止旁路）"
                )
            try:
                ok = bool(self._gateway(agent_id, topic, dict(payload)))
            except Exception as exc:  # noqa: BLE001 — 网关异常按拒绝处理
                _log.exception("a2a_gateway 检查异常: %s", topic)
                raise StrategicBusError(f"a2a_gateway 检查异常: {topic!r}") from exc
            if not ok:
                raise StrategicBusError(f"a2a_gateway 拒绝跨层消息: {agent_id} -> {topic!r}")
            self._audit(agent_id, topic, "cross_layer")
            return "cross_layer"

        delivered = 0
        for _, handler in self._subs.get(topic, []):
            handler(dict(payload))
            delivered += 1
        self._audit(agent_id, topic, "intra_layer")
        _log.debug("层内直连投递: %s -> %s (%d 订阅者)", agent_id, topic, delivered)
        return "intra_layer"

    # ── 查询 ─────────────────────────────────────────────────────────────

    @property
    def layer(self) -> BusLayer:
        """本总线实例所属层级。"""
        return self._layer

    def subscriber_count(self, topic: str) -> int:
        """单 topic 订阅者数（topic 非法 → Fail-Closed）。"""
        self._topic_layer(topic)
        return len(self._subs.get(topic, []))
