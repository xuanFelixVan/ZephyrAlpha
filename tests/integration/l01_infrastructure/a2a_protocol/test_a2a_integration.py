# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.integration.l01_infrastructure.a2a_protocol.test_a2a_integration
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""MOD-INF-025 A2A Protocol 集成测试 — Phase 1 核心链路验证

验证: 发现→注册→通信→任务调度→状态机→死锁检测→升级 全链路打通
"""

import time

import pytest

from zephyr.l01_infrastructure.a2a_protocol.layer1_discovery import AgentCard, A2ARegistry, IdentityVerifier, AgentCapability
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication import (
    A2AMessage, A2ATask, A2ATaskStatus, A2AStateMachine, PartType,
    MessageRouter, ContextPackage, HandoffManager, PushNotifier,
)
from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination import (
    Supervisor, ConstructionVerifier,
    DeadlockGuard, LivelockDetector, CascadeGuard,
    A2AEconomics, A2AForgetting, A2ADelegationChain,
    A2ATemporalAdmission, A2AIdleGuard,
    A2ARedTeam,
)
from zephyr.l01_infrastructure.a2a_protocol import GovernanceAdapter, A2AGovernanceRecord

AGENT_A = "agent-alpha"
AGENT_B = "agent-beta"


class TestA2ADiscoveryIntegration:
    """Layer 1: Agent Card + Registry + Identity 联动"""

    def test_discover_registry_lifecycle(self):
        registry = A2ARegistry()
        card = AgentCard(
            agent_id=AGENT_A,
            name="Agent Alpha",
            description="Test agent for discovery integration",
            capabilities=[AgentCapability.WRITE, AgentCapability.SEARCH],
            skill_ids=["SKILL-DOM-BLU-001"],
        )
        registry.register(card)
        assert registry.get(AGENT_A) is not None

        agents = registry.discover(capability=AgentCapability.SEARCH)
        assert len(agents) >= 1
        assert any(a.agent_id == AGENT_A for a in agents)

        registry.unregister(AGENT_A)
        assert registry.get(AGENT_A) is None

    def test_identity_verify_roundtrip(self):
        verifier = IdentityVerifier()
        agent_id = AGENT_A
        challenge = verifier.generate_challenge()
        assert len(challenge) == 64

        payload = {"challenge": challenge, "timestamp": "2026-05-08T00:00:00Z"}
        signature = verifier.sign(agent_id, payload)
        assert verifier.verify(agent_id, payload, signature)


class TestA2ACommunicationIntegration:
    """Layer 2: Message + StateMachine + Router 联动"""

    def test_message_route_to_registered_handler(self):
        router = MessageRouter()
        received_content: list[str] = []

        def handler(content, metadata):
            received_content.append(content)

        router.register_handler(PartType.TEXT, handler)
        msg = A2AMessage(
            message_id="a2a-msg-test-001",
            from_agent=AGENT_A,
            to_agent=AGENT_B,
            task_id="a2a-task-test-001",
        )
        msg.add_part(PartType.TEXT, "hello from A")
        results = router.route(msg)
        assert len(received_content) == 1
        assert received_content[0] == "hello from A"
        assert "text" in results

    def test_handoff_roundtrip(self):
        mgr = HandoffManager()
        task_id = "a2a-task-handoff-001"
        record = mgr.handoff(AGENT_A, AGENT_B, task_id, "Agent A needs help")
        assert record.acknowledged is False

        ack_result = mgr.acknowledge(AGENT_B, task_id)
        assert ack_result is True
        assert record.acknowledged is True

    def test_push_notify_subscribe(self):
        notifier = PushNotifier()
        notified: list[str] = []

        def callback(event, data):
            notified.append(event)

        notifier.subscribe(AGENT_A, callback)
        count = notifier.notify(AGENT_A, "task.created", {"task_id": "T-1"})
        assert count == 1
        assert "task.created" in notified

    def test_context_package_creation(self):
        pkg = ContextPackage(task_id="a2a-task-ctx-001", source_agent=AGENT_A)
        pkg.add_blueprint("blueprint-a.md", "content of a")
        pkg.add_blueprint("blueprint-b.md", "content of b")
        pkg.add_decision("ADR-0001", {"title": "Test decision"})

        d = pkg.to_dict()
        assert d["blueprint_count"] == 2
        assert d["decision_count"] == 1
        assert d["source_agent"] == AGENT_A


class TestA2ACoordinationIntegration:
    """Layer 3: Supervisor + Guards + Economics 联动"""

    def test_supervisor_submit_assign_cycle(self):
        sup = Supervisor()
        task_a = A2ATask(
            task_id="a2a-task-sup-a",
            from_agent=AGENT_A,
            to_agent=AGENT_A,
            description="Task A",
        )
        sup.submit_task(task_a)

        task_b = A2ATask(
            task_id="a2a-task-sup-b",
            from_agent=AGENT_A,
            to_agent=AGENT_B,
            description="Task B",
        )
        sup.submit_task(task_b)

        task_c = A2ATask(
            task_id="a2a-task-sup-c",
            from_agent=AGENT_A,
            to_agent=AGENT_A,
            description="Task C",
        )
        sup.submit_task(task_c)

        assert sup.get_agent_load(AGENT_A) == 2
        assert sup.get_agent_load(AGENT_B) == 1

        A2AStateMachine.transition(task_b, A2ATaskStatus.QUEUED)
        ok = sup.assign_task("a2a-task-sup-b", AGENT_B)
        assert ok is True

        deadlocks = sup.detect_deadlocks()
        assert isinstance(deadlocks, list)

    def test_deadlock_guard_acquire_release(self):
        guard = DeadlockGuard()
        assert guard.try_acquire("lock-a", AGENT_A)
        assert not guard.try_acquire("lock-a", AGENT_B)
        guard.release("lock-a", AGENT_A)
        assert guard.try_acquire("lock-a", AGENT_B)
        guard.release("lock-a", AGENT_B)

    def test_livelock_detector_cycle(self):
        detector = LivelockDetector(cycle_limit=2)
        detector.record_state(AGENT_A, "hash-1")
        detector.record_state(AGENT_A, "hash-2")
        detector.record_state(AGENT_A, "hash-1")
        assert detector.check_cycle(AGENT_A, "hash-1")

    def test_cascade_guard(self):
        guard = CascadeGuard(threshold=3)
        assert guard.check(AGENT_A) is True
        guard.record_failure(AGENT_A)
        guard.record_failure(AGENT_A)
        assert guard.check(AGENT_A) is True
        guard.record_failure(AGENT_A)
        assert guard.check(AGENT_A) is False

    def test_delegation_chain_depth(self):
        chain = A2ADelegationChain()
        task_id = "a2a-task-chain-001"
        for i in range(5):
            r = chain.delegate(task_id, f"agent-{i}", f"agent-{i+1}")
            assert "error" not in r
        r = chain.delegate(task_id, "agent-5", "agent-6")
        assert r["error"] == "max_depth_exceeded"

    def test_economics_cost_tracking(self):
        econ = A2AEconomics()
        r = econ.track("a2a-task-cost-001", 1000, 500, "deepseek")
        assert r["cost_usd"] > 0
        r2 = econ.track("a2a-task-cost-002", 2000, 1000, "claude")
        assert r2["cost_usd"] > r["cost_usd"]

    def test_forgetting_fifo_limit(self):
        forget = A2AForgetting(max_memory=3)
        forget.remember({"k": "k1", "v": "v1"})
        forget.remember({"k": "k2", "v": "v2"})
        forget.remember({"k": "k3", "v": "v3"})
        forget.remember({"k": "k4", "v": "v4"})
        assert len(forget._memory) == 3
        assert forget._memory[0]["k"] == "k2"

    def test_temporal_admission(self):
        gate = A2ATemporalAdmission(max_concurrent=2)
        assert gate.admit(AGENT_A) is True
        gate.enter(AGENT_A)
        assert gate.admit(AGENT_B) is True
        gate.enter(AGENT_B)
        assert gate.admit("agent-gamma") is False
        gate.leave(AGENT_A)
        assert gate.admit("agent-gamma") is True

    def test_idle_guard(self):
        idle = A2AIdleGuard(idle_timeout=10)
        now = time.time()
        assert not idle.check_idle(AGENT_A, now - 5, now)
        assert idle.check_idle(AGENT_A, now - 15, now)

    def test_red_team_vectors(self):
        rt = A2ARedTeam()
        vectors = rt.attack_vectors
        assert len(vectors) == 6
        severity = rt.severity_summary()
        assert severity["critical"] == 3
        assert severity["high"] == 2

        result = rt.attack("test-protocol", "AV-003")
        assert result["category"] == "artifact_poisoning"
        assert result["penetrated"] is False


class TestA2AConstructionVerifierSelfCheck:
    """施工验证器自指测试"""

    def test_verify_self(self):
        verifier = ConstructionVerifier()
        result = verifier.verify()
        assert "passed" in result
        assert "total_files" in result
        assert "empty_stubs" in result
        assert "verified_files" in result
        assert "stub_ratio" in result
        assert result["total_files"] > 0


class TestA2AGovernanceAdapterIntegration:
    """治理适配器桥接测试"""

    def test_verify_pair(self):
        adapter = GovernanceAdapter()
        result = adapter.verify_pair(AGENT_A, AGENT_B)
        assert isinstance(result, A2AGovernanceRecord)
        assert result.action == "verify_pair"
        assert result.granted is False

    def test_allowed_pair_verified(self):
        adapter = GovernanceAdapter()
        result = adapter.verify_pair("reviewer", "builder")
        assert result.granted is True

    def test_escalate_if_needed(self):
        adapter = GovernanceAdapter()
        record = adapter.verify_pair(AGENT_A, AGENT_B)
        result = adapter.escalate_if_needed(record, severity="CRITICAL")
        assert result.escalation_level == "CRITICAL"

    def test_audit_communication(self):
        adapter = GovernanceAdapter()
        record = adapter.verify_pair("reviewer", "builder")
        result = adapter.audit_communication(record, session_id="sess-001")
        assert result.audit_id != ""
        assert result.audit_id.startswith("a2a-")
