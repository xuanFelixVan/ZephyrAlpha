# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [TTL] permanent
"""A2A 检查网关测试（B11-02516 / CAND-INFRAA2A-001）。

测试内容（内存注册表 + 真实 Ed25519 签名，不触达网络与审批人）：
- 三段校验：身份（Agent ID+层级签名复用 agent_signer）→ 能力匹配（Agent Card 能力集）→ 边界（通信对/三区/四级自治）
- 三态：PASS / DENY / GATED；GATED 挂起写审批队列转人工，approve 后同 request_id 放行
- 热路径 <1ms（PASS 路径纯内存+单次签名验证）
- OWASP ASI01-10 逐条映射（每条款一个用例，命名 test_asiNN_*）
"""

from __future__ import annotations

import pytest

from zephyr.gov_audit.agent_signer import AgentSigner
from zephyr.infrastructure.a2a_protocol.a2a_check_gateway import (
    A2aCheckGateway,
    A2AGateRequest,
    GateDecision,
    build_signed_event,
)
from zephyr.infrastructure.a2a_protocol.layer1_discovery.agent_card import AgentCapability, AgentCard


class _FakeRegistry:
    """内存 Agent Card 注册表（满足 A2ARegistryProtocol）。"""

    def __init__(self) -> None:
        self._cards: dict[str, AgentCard] = {}

    def register(self, card: AgentCard) -> AgentCard:
        self._cards[card.agent_id] = card
        return card

    def discover(self, capability: str | None = None) -> list[AgentCard]:
        return list(self._cards.values())

    def get(self, agent_id: str) -> AgentCard | None:
        return self._cards.get(agent_id)

    def unregister(self, agent_id: str) -> bool:
        return self._cards.pop(agent_id, None) is not None


def _card(
    agent_id: str,
    *,
    public_key: str | None = None,
    capabilities: tuple[str, ...] = ("read",),
    zone: str = "core",
    autonomy: str = "L2",
) -> AgentCard:
    return AgentCard(
        agent_id=agent_id,
        name=agent_id,
        description="gateway test card",
        capabilities=[AgentCapability(c) for c in capabilities],
        public_key=public_key,
        metadata={"zone": zone, "autonomy_level": autonomy},
    )


@pytest.fixture
def keys():
    return AgentSigner.generate_key_pair()  # (private_hex, public_hex)


@pytest.fixture
def registry(keys):
    reg = _FakeRegistry()
    _, pub = keys
    reg.register(_card("agent-orchestrator", public_key=pub, capabilities=("read", "grep", "search")))
    reg.register(_card("agent-worker", public_key=pub, capabilities=("read", "write")))
    return reg


@pytest.fixture
def gateway(registry):
    return A2aCheckGateway(registry=registry)


def _request(priv: str, *, request_id: str = "req-1", capability: str = "read",
             from_agent: str = "agent-orchestrator", to_agent: str = "agent-worker") -> A2AGateRequest:
    req = A2AGateRequest(
        from_agent=from_agent,
        to_agent=to_agent,
        capability=capability,
        payload={"task": "scan"},
        request_id=request_id,
    )
    return A2AGateRequest(
        from_agent=req.from_agent,
        to_agent=req.to_agent,
        capability=req.capability,
        payload=req.payload,
        request_id=req.request_id,
        signature=AgentSigner.sign(build_signed_event(req), priv),
    )


# ── 核心三态 ──────────────────────────────────────────────


def test_pass_path_three_stages_ok(gateway, keys):
    priv, _ = keys
    verdict = gateway.check(_request(priv))
    assert verdict.decision is GateDecision.PASS
    assert verdict.reason == "ok"
    assert verdict.from_agent == "agent-orchestrator"
    assert verdict.to_agent == "agent-worker"
    assert verdict.request_id == "req-1"


def test_hot_path_under_1ms(gateway, keys):
    priv, _ = keys
    verdict = gateway.check(_request(priv, request_id="req-lat"))
    assert verdict.decision is GateDecision.PASS
    assert verdict.latency_ms < 1.0  # 热路径预算 <1ms


def test_self_communication_pass(gateway, keys):
    priv, _ = keys
    req = A2AGateRequest(from_agent="agent-worker", to_agent="agent-worker", capability="read", request_id="req-self")
    verdict = gateway.check(req)
    assert verdict.decision is GateDecision.PASS
    assert verdict.reason == "self_communication"


def test_gated_then_human_approve_flow(gateway, registry, keys):
    priv, pub = keys
    registry.register(_card("agent-edge", public_key=pub, capabilities=("read",), zone="edge"))
    req = _request(priv, request_id="req-gated", to_agent="agent-edge")
    # orchestrator↔edge 通信对未授权→先补一条同区 GATED 场景：改用跨区但通信对已授权对
    req = _request(priv, request_id="req-gated", from_agent="agent-orchestrator", to_agent="agent-worker")
    registry.unregister("agent-worker")
    registry.register(_card("agent-worker", public_key=pub, capabilities=("read", "write"), zone="edge"))
    verdict = gateway.check(req)
    assert verdict.decision is GateDecision.GATED
    assert gateway.pending_approvals() and gateway.pending_approvals()[0]["request_id"] == "req-gated"
    assert gateway.approve("req-gated") is True
    assert gateway.approve("req-nonexistent") is False
    again = gateway.check(req)
    assert again.decision is GateDecision.PASS
    assert again.reason == "human_approved"


# ── OWASP ASI01-10 逐条映射 ───────────────────────────────


def test_asi01_goal_hijack_forged_signature_denied(gateway, keys):
    """ASI01 Agent Goal Hijack：伪造/替换签名 → DENY（层级签名身份校验）。"""
    other_priv, _ = AgentSigner.generate_key_pair()
    verdict = gateway.check(_request(other_priv, request_id="req-asi01"))  # 用他钥签名冒充 orchestrator
    assert verdict.decision is GateDecision.DENY
    assert verdict.reason == "invalid_signature"


def test_asi02_tool_misuse_undeclared_capability_denied(gateway, keys):
    """ASI02 Tool Misuse：请求能力不在被调方 Agent Card 声明集 → DENY。"""
    priv, _ = keys
    verdict = gateway.check(_request(priv, request_id="req-asi02", capability="bash"))  # worker 未声明 bash
    assert verdict.decision is GateDecision.DENY
    assert verdict.reason == "capability_not_declared"


def test_asi03_identity_privilege_abuse_unknown_agent_denied(gateway, keys):
    """ASI03 Identity/Privilege Abuse：未注册 Agent ID → DENY。"""
    priv, _ = keys
    verdict = gateway.check(_request(priv, request_id="req-asi03", to_agent="agent-ghost"))
    assert verdict.decision is GateDecision.DENY
    assert verdict.reason == "unknown_agent"


def test_asi04_resource_overload_approval_queue_bounded(gateway, registry, keys):
    """ASI04 Resource Overload：GATED 审批队列有界（maxlen），挂起洪泛不撑爆内存。"""
    priv, pub = keys
    registry.unregister("agent-worker")
    registry.register(_card("agent-worker", public_key=pub, capabilities=("read", "write"), zone="edge"))
    for i in range(1100):
        gateway.check(_request(priv, request_id=f"req-flood-{i}"))
    assert len(gateway.pending_approvals()) <= 1000


def test_asi05_unexpected_code_execution_l0_write_gated(registry, keys):
    """ASI05 Unexpected Code Execution：L0 纯规则自治 Agent 的 write/bash 调用 → GATED 转人工。"""
    priv, pub = keys
    registry.register(_card("agent-auditor", public_key=pub, capabilities=("read", "write"), autonomy="L0"))
    gateway = A2aCheckGateway(registry=registry)
    verdict = gateway.check(_request(priv, request_id="req-asi05", to_agent="agent-auditor", capability="write"))
    assert verdict.decision is GateDecision.GATED
    assert verdict.reason == "autonomy_escalation"


def test_asi06_insecure_channel_pair_not_allowed_denied(registry, keys):
    """ASI06 Insecure Inter-Agent Communication：通信对未授权 → DENY（边界检查）。"""
    priv, pub = keys
    registry.register(_card("agent-researcher", public_key=pub, capabilities=("read",)))
    registry.register(_card("agent-executor", public_key=pub, capabilities=("read",)))
    gateway = A2aCheckGateway(registry=registry)
    verdict = gateway.check(_request(priv, request_id="req-asi06", from_agent="agent-researcher", to_agent="agent-executor"))
    assert verdict.decision is GateDecision.DENY
    assert verdict.reason == "pair_not_allowed"


def test_asi07_misaligned_behavior_cross_zone_gated(registry, keys):
    """ASI07 Misaligned Behaviors：跨区（三区边界）调用 → GATED 转人工审批。"""
    priv, pub = keys
    registry.unregister("agent-worker")
    registry.register(_card("agent-worker", public_key=pub, capabilities=("read",), zone="edge"))
    gateway = A2aCheckGateway(registry=registry)
    verdict = gateway.check(_request(priv, request_id="req-asi07"))
    assert verdict.decision is GateDecision.GATED
    assert verdict.reason == "cross_zone_call"


def test_asi08_repudiation_verdict_full_trace(gateway, keys):
    """ASI08 Repudiation/Untraceability：verdict 全字段留痕（request_id/双方/能力/耗时/理由）。"""
    priv, _ = keys
    verdict = gateway.check(_request(priv, request_id="req-asi08"))
    assert verdict.request_id == "req-asi08"
    assert verdict.from_agent and verdict.to_agent and verdict.capability
    assert verdict.latency_ms >= 0 and verdict.reason


def test_asi09_human_bypass_gated_never_auto_pass(registry, keys):
    """ASI09 Human-in-the-loop Bypass：GATED 未审批前重复提交仍 GATED，绝不自动放行。"""
    priv, pub = keys
    registry.unregister("agent-worker")
    registry.register(_card("agent-worker", public_key=pub, capabilities=("read",), zone="edge"))
    gateway = A2aCheckGateway(registry=registry)
    req = _request(priv, request_id="req-asi09")
    assert gateway.check(req).decision is GateDecision.GATED
    assert gateway.check(req).decision is GateDecision.GATED  # 未 approve 不转 PASS


def test_asi10_data_exfiltration_cross_zone_read_gated(registry, keys):
    """ASI10 Data Exfiltration：跨区 read（数据出域通道）→ GATED 需人工审批。"""
    priv, pub = keys
    registry.unregister("agent-worker")
    registry.register(_card("agent-worker", public_key=pub, capabilities=("read",), zone="dmz"))
    gateway = A2aCheckGateway(registry=registry)
    verdict = gateway.check(_request(priv, request_id="req-asi10", capability="read"))
    assert verdict.decision is GateDecision.GATED
    assert verdict.reason == "cross_zone_call"


def test_missing_signature_denied(gateway):
    """身份校验缺签名 → DENY（missing_signature）。"""
    req = A2AGateRequest(from_agent="agent-orchestrator", to_agent="agent-worker", capability="read", request_id="req-nosig")
    verdict = gateway.check(req)
    assert verdict.decision is GateDecision.DENY
    assert verdict.reason == "missing_signature"
