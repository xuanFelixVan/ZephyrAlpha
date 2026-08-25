# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.a2a_check_gateway
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES] zephyr.gov_audit.agent_signer; zephyr.security.access_control.a2a_check; zephyr.infrastructure.a2a_protocol.layer1_discovery.agent_card; zephyr.shared.protocols.a2a.a2a_registry
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三段校验顺序固定（身份→能力→边界）；PASS/DENY/GATED 三态；GATED 必写审批队列且未 approve 绝不自动转 PASS；热路径 <1ms（纯内存+单次 Ed25519 验证）；审批队列有界 maxlen=1000
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() 不抛异常——注册表/签名/卡片异常一律收敛为 DENY
# [TESTS] tests/a2a/test_a2a_check_gateway.py
# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""A2A 检查网关（B11-02516 / CAND-INFRAA2A-001）。

A2A 调用前三段校验 + 三态门控：
  1. 身份校验——双方 Agent Card 已注册 + 层级签名验证（复用 gov_audit.agent_signer
     Ed25519；签名结构见 build_signed_event，调用方对同一结构签名）
  2. 能力匹配——请求能力必须 ∈ 被调方 Agent Card capabilities 声明集
  3. 边界检查——通信对（复用 access_control.a2a_check.verify_a2a_pair，角色按
     "agent-" 前缀归一化）+ 三区边界（card.metadata["zone"] 跨区）+ 四级自治
     （card.metadata["autonomy_level"]，L0 纯规则 Agent 的 write/bash 调用）

三态：PASS 放行 / DENY 拒绝 / GATED 挂起（写审批队列转人工，approve(request_id)
后同 request_id 重提交放行；未审批重复提交仍 GATED——Human-in-the-loop 不可绕过）。

OWASP ASI01-10 映射（tests/a2a/test_a2a_check_gateway.py 逐条用例）：
  ASI01 目标劫持→层级签名验证拒伪造；ASI02 工具滥用→能力集外 DENY；
  ASI03 身份越权→未注册 Agent DENY；ASI04 资源过载→审批队列有界；
  ASI05 意外代码执行→L0 自治 write/bash GATED；ASI06 不安全通信→通信对边界 DENY；
  ASI07 失准行为→跨区调用 GATED；ASI08 抵赖→verdict 全字段留痕；
  ASI09 人工绕行→GATED 绝不自动 PASS；ASI10 数据外泄→跨区 read GATED。

热路径：<1ms——注册表 dict 查找 + 单次 Ed25519 验证 + 内存规则匹配，零 IO。
与既有件分工：本网关管"调用前检查"；a2a_check.verify_a2a_pair 管通信对简表；
governance/policy_engine 管策略、rate_limiter 管限流（本网关不重复实现）。
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final

from zephyr.gov_audit.agent_signer import AgentSigner
from zephyr.infrastructure.a2a_protocol.layer1_discovery.agent_card import AgentCard
from zephyr.security.access_control.a2a_check import verify_a2a_pair
from zephyr.shared.protocols.a2a.a2a_registry import A2ARegistryProtocol

__all__ = [
    "A2aCheckGateway",
    "A2AGateRequest",
    "A2AGateVerdict",
    "GateDecision",
    "build_signed_event",
]

_APPROVAL_QUEUE_MAX: Final[int] = 1000  # ASI04：审批队列有界
_L0_RESTRICTED_CAPABILITIES: Final[frozenset[str]] = frozenset({"write", "bash"})  # ASI05：L0 自治受限能力
_DEFAULT_ZONE: Final[str] = "core"
_AGENT_ID_PREFIX: Final[str] = "agent-"


class GateDecision(str, Enum):
    """三态门控结论。"""

    PASS = "PASS"
    DENY = "DENY"
    GATED = "GATED"


@dataclass(frozen=True)
class A2AGateRequest:
    """A2A 调用前检查请求。"""

    from_agent: str
    to_agent: str
    capability: str
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""  # 发起方对 build_signed_event(本请求) 的 Ed25519 hex 签名
    request_id: str = ""


@dataclass(frozen=True)
class A2AGateVerdict:
    """门控裁决（ASI08：全字段留痕）。"""

    decision: GateDecision
    reason: str
    from_agent: str
    to_agent: str
    capability: str
    latency_ms: float
    request_id: str


def build_signed_event(request: A2AGateRequest) -> dict[str, Any]:
    """签名规范结构——调用方与网关 MUST 用本函数构造待签名事件（防结构歧义）。"""
    return {
        "capability": request.capability,
        "from": request.from_agent,
        "payload": request.payload,
        "request_id": request.request_id,
        "to": request.to_agent,
    }


class A2aCheckGateway:
    """A2A 检查网关：身份→能力→边界三段校验，PASS/DENY/GATED 三态。"""

    def __init__(
        self,
        *,
        registry: A2ARegistryProtocol,
        approval_queue: deque[dict[str, Any]] | None = None,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._registry = registry
        self._approval_queue: deque[dict[str, Any]] = (
            approval_queue if approval_queue is not None else deque(maxlen=_APPROVAL_QUEUE_MAX)
        )
        self._approved: set[str] = set()
        self._clock = clock
        self._seq = 0

    # ── 主入口 ────────────────────────────────────────────

    def check(self, request: A2AGateRequest) -> A2AGateVerdict:
        """三段校验并出三态裁决；任何内部异常收敛为 DENY（门控不得放行未知态）。"""
        t0 = self._clock()
        request_id = request.request_id or self._next_request_id(request)
        try:
            decision, reason = self._evaluate(request, request_id)
        except Exception:  # noqa: BLE001 — fail-closed：门控异常一律拒绝
            decision, reason = GateDecision.DENY, "gateway_internal_error"
        latency_ms = (self._clock() - t0) * 1000.0
        return A2AGateVerdict(
            decision=decision,
            reason=reason,
            from_agent=request.from_agent,
            to_agent=request.to_agent,
            capability=request.capability,
            latency_ms=latency_ms,
            request_id=request_id,
        )

    # ── 审批流 ────────────────────────────────────────────

    def pending_approvals(self) -> list[dict[str, Any]]:
        """待人工审批挂起列表（按时间正序）。"""
        return list(self._approval_queue)

    def approve(self, request_id: str) -> bool:
        """人工审批放行：挂起记录存在 → 移出队列并登记 approved，同 request_id 重提交即 PASS。"""
        for i, item in enumerate(self._approval_queue):
            if item["request_id"] == request_id:
                del self._approval_queue[i]
                self._approved.add(request_id)
                return True
        return False

    # ── 三段校验 ──────────────────────────────────────────

    def _evaluate(self, request: A2AGateRequest, request_id: str) -> tuple[GateDecision, str]:
        # 自身通信快捷通道（对齐 verify_a2a_pair 既有规则 1）
        if request.from_agent == request.to_agent:
            return GateDecision.PASS, "self_communication"

        # 人工已审批（ASI09：仅此通道可转 PASS，且需显式 approve）
        if request_id in self._approved:
            return GateDecision.PASS, "human_approved"

        # ── 第一段：身份校验（Agent ID 注册 + 层级签名）──
        from_card = self._registry.get(request.from_agent)
        to_card = self._registry.get(request.to_agent)
        if from_card is None or to_card is None:
            return GateDecision.DENY, "unknown_agent"
        if not request.signature:
            return GateDecision.DENY, "missing_signature"
        if not from_card.public_key:
            return GateDecision.DENY, "identity_unverifiable"
        if not AgentSigner.verify(build_signed_event(request), from_card.public_key, request.signature):
            return GateDecision.DENY, "invalid_signature"

        # ── 第二段：能力匹配（对 Agent Card 能力声明集）──
        declared = {c.value if hasattr(c, "value") else str(c) for c in to_card.capabilities}
        if request.capability not in declared:
            return GateDecision.DENY, "capability_not_declared"

        # ── 第三段：边界检查（通信对 / 三区 / 四级自治）──
        pair = verify_a2a_pair(self._role(request.from_agent), self._role(request.to_agent))
        if not pair["approved"]:
            return GateDecision.DENY, "pair_not_allowed"

        if self._zone(from_card) != self._zone(to_card):
            return self._gate(request, request_id, "cross_zone_call")

        if (
            to_card.metadata.get("autonomy_level", "L1") == "L0"
            and request.capability in _L0_RESTRICTED_CAPABILITIES
        ):
            return self._gate(request, request_id, "autonomy_escalation")

        return GateDecision.PASS, "ok"

    def _gate(self, request: A2AGateRequest, request_id: str, reason: str) -> tuple[GateDecision, str]:
        """GATED 挂起：写审批队列转人工（队列有界，洪泛不撑爆内存）。"""
        self._approval_queue.append(
            {
                "request_id": request_id,
                "from_agent": request.from_agent,
                "to_agent": request.to_agent,
                "capability": request.capability,
                "reason": reason,
            }
        )
        return GateDecision.GATED, reason

    # ── 内部 ──────────────────────────────────────────────

    def _next_request_id(self, request: A2AGateRequest) -> str:
        self._seq += 1
        return f"{request.from_agent}->{request.to_agent}#{self._seq}"

    @staticmethod
    def _role(agent_id: str) -> str:
        """Agent ID → 通信对角色归一化（strip "agent-" 前缀对齐 ALLOWED_TALK_PAIRS 角色表）。"""
        return agent_id[len(_AGENT_ID_PREFIX):] if agent_id.startswith(_AGENT_ID_PREFIX) else agent_id

    @staticmethod
    def _zone(card: AgentCard) -> str:
        return card.metadata.get("zone", _DEFAULT_ZONE)
