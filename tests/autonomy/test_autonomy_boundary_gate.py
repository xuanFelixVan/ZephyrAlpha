"""tests/autonomy/test_autonomy_boundary_gate.py — AutonomyBoundaryGate（MOD-AU-001）单元测试.

覆盖 15号文（15_autonomy_boundary_risk.md）§4.1 S0.2 验收口径：
①human_gated 样例写操作被拦截并升级人审工单留痕（.runtime/autonomy_gate/queue/）
②ai_modifiable 样例放行（留痕可回溯）
③immutable_core 样例物理拦截并告警留痕（alerts.jsonl，severity=critical）
④注册表不可读时 fail-closed 生效（拒绝自治写入，按 human_gated 升级人审）
⑤目标未登记时 fail-closed 生效（同上）
⑥判定全留痕，审计记录符合 16号文 §4.2 P0-1 统一事件 schema。

被测对象：src/zephyr/autonomy_core/autonomy_boundary_gate.py
真源注册表：GOV-AI-001（docs/01_policies_and_standards/_registry/catalogs/
ai_autonomy_authority_registry.yaml）——三分类判定以注册表为准，本测试直接用真表。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.autonomy_core.autonomy_boundary_gate import (
    AutonomyBoundaryGate,
    AutonomyLayer,
    GateDecision,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "ai_autonomy_authority_registry.yaml"
)


@pytest.fixture
def gate(tmp_path):
    instance = AutonomyBoundaryGate(
        registry_path=REGISTRY_PATH, runtime_dir=tmp_path, repo_root=REPO_ROOT
    )
    yield instance
    instance.close()


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestThreeClassDecision:
    """三分类判定：放行 / 升级人审 / 物理拦截."""

    def test_ai_modifiable_allowed(self, gate):
        verdict = gate.check_write_permission("act-1", "src/zephyr/factor/alpha_momentum.py")
        assert verdict.allowed is True
        assert verdict.decision is GateDecision.ALLOW
        assert verdict.layer is AutonomyLayer.AI_MODIFIABLE
        assert verdict.fail_closed is False
        assert verdict.matched_path == "src/zephyr/factor/"

    def test_human_gated_escalated(self, gate):
        verdict = gate.check_write_permission("act-2", "src/zephyr/data/market_connect.py")
        assert verdict.allowed is False
        assert verdict.decision is GateDecision.ESCALATE
        assert verdict.layer is AutonomyLayer.HUMAN_GATED
        assert verdict.fail_closed is False

    def test_immutable_core_blocked(self, gate):
        verdict = gate.check_write_permission("act-3", "src/zephyr/risk/risk_engine.py")
        assert verdict.allowed is False
        assert verdict.decision is GateDecision.BLOCK
        assert verdict.layer is AutonomyLayer.IMMUTABLE_CORE
        assert verdict.fail_closed is False

    def test_component_level_entries(self, gate):
        """组件级路径登记（config/scripts）同样命中三分类."""
        assert (
            gate.check_write_permission("act-4", "config/capabilities.yaml").decision
            is GateDecision.BLOCK
        )
        assert (
            gate.check_write_permission("act-5", "config/drift_thresholds.yaml").decision
            is GateDecision.ESCALATE
        )
        assert (
            gate.check_write_permission(
                "act-6", "scripts/governance/validate_truth_source_cascade.py"
            ).decision
            is GateDecision.ALLOW
        )

    def test_absolute_path_normalized_to_repo_relative(self, gate):
        target = str(REPO_ROOT / "src" / "zephyr" / "factor" / "alpha.py")
        verdict = gate.check_write_permission("act-7", target)
        assert verdict.decision is GateDecision.ALLOW

    def test_outside_repo_absolute_path_fail_closed(self, gate):
        verdict = gate.check_write_permission("act-8", "C:/Windows/system32/drivers/etc/hosts")
        assert verdict.allowed is False
        assert verdict.fail_closed is True
        assert verdict.layer is AutonomyLayer.UNREGISTERED


class TestFailClosed:
    """fail-closed 兜底：注册表不可读 / 目标未登记 → 拒绝自治写入，升级人审."""

    def test_registry_unreadable_fail_closed(self, tmp_path):
        broken = AutonomyBoundaryGate(
            registry_path=tmp_path / "missing_registry.yaml",
            runtime_dir=tmp_path,
            repo_root=REPO_ROOT,
        )
        try:
            verdict = broken.check_write_permission("act-9", "src/zephyr/factor/alpha.py")
            assert verdict.allowed is False
            assert verdict.decision is GateDecision.ESCALATE
            assert verdict.layer is AutonomyLayer.REGISTRY_UNAVAILABLE
            assert verdict.fail_closed is True
        finally:
            broken.close()

    def test_registry_malformed_fail_closed(self, tmp_path):
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("- this is a list not a mapping\n", encoding="utf-8")
        broken = AutonomyBoundaryGate(
            registry_path=bad_yaml, runtime_dir=tmp_path, repo_root=REPO_ROOT
        )
        try:
            verdict = broken.check_write_permission("act-10", "src/zephyr/factor/alpha.py")
            assert verdict.allowed is False
            assert verdict.fail_closed is True
            assert verdict.layer is AutonomyLayer.REGISTRY_UNAVAILABLE
        finally:
            broken.close()

    def test_unregistered_target_denied(self, gate):
        verdict = gate.check_write_permission(
            "act-11", "src/zephyr/totally_unknown_domain_xyz/foo.py"
        )
        assert verdict.allowed is False
        assert verdict.decision is GateDecision.ESCALATE
        assert verdict.layer is AutonomyLayer.UNREGISTERED
        assert verdict.fail_closed is True

    def test_gate_never_raises_on_internal_error(self, gate, monkeypatch):
        """ERROR_CONTRACT：判定链路内部异常也降级为 fail-closed 判定而非抛出."""
        monkeypatch.setattr(
            gate, "_normalize_target", lambda *_: (_ for _ in ()).throw(RuntimeError("boom"))
        )
        verdict = gate.check_write_permission("act-12", "src/zephyr/factor/alpha.py")
        assert verdict.allowed is False
        assert verdict.fail_closed is True
        assert verdict.layer is AutonomyLayer.INTERNAL_ERROR


class TestTrace:
    """留痕断言：审计 jsonl / 人审工单 / immutable 告警."""

    def test_allow_writes_audit_record(self, gate, tmp_path):
        verdict = gate.check_write_permission(
            "act-13", "src/zephyr/factor/alpha.py", {"session_id": "sess-A"}
        )
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert len(records) == 1
        record = records[0]
        # 16号文 §4.2 P0-1 统一事件 schema 字段
        assert record["schema_version"] == "1.0"
        assert record["event_id"] == verdict.verdict_id
        assert record["source_domain"] == "access_control"
        assert record["severity"] == "info"
        assert record["threat_category"] == "none"
        assert record["session_id"] == "sess-A"
        assert record["decision"] == "allow"
        assert record["timestamp"]

    def test_escalate_writes_ticket_and_audit(self, gate, tmp_path):
        verdict = gate.check_write_permission("act-14", "src/zephyr/data/conn.py")
        tickets = list((tmp_path / "autonomy_gate" / "queue").glob("ticket-*.json"))
        assert len(tickets) == 1
        ticket = json.loads(tickets[0].read_text(encoding="utf-8"))
        assert ticket["status"] == "pending_review"
        assert ticket["ticket_id"] == verdict.verdict_id
        assert ticket["verdict"]["decision"] == "escalate"
        assert verdict.ticket_path.endswith(tickets[0].name)
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert records[0]["severity"] == "elevated"
        assert records[0]["threat_category"] == "human_approval_required"

    def test_block_writes_alert_and_audit(self, gate, tmp_path):
        verdict = gate.check_write_permission("act-15", "src/zephyr/risk/engine.py")
        alerts = _read_jsonl(tmp_path / "autonomy_gate" / "alerts.jsonl")
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "critical"
        assert alerts[0]["threat_category"] == "immutable_core_violation"
        assert alerts[0]["event_id"] == verdict.verdict_id
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert records[0]["decision"] == "block"
        assert records[0]["severity"] == "critical"

    def test_fail_closed_records_unauthorized_attempt(self, gate, tmp_path):
        gate.check_write_permission("act-16", "src/zephyr/unknown_xyz/a.py")
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert records[0]["fail_closed"] is True
        assert records[0]["threat_category"] == "unauthorized_write_attempt"

    def test_every_decision_traced(self, gate, tmp_path):
        """判定全留痕：三种判定各一次，审计行数=3."""
        gate.check_write_permission("a1", "src/zephyr/factor/x.py")
        gate.check_write_permission("a2", "src/zephyr/data/x.py")
        gate.check_write_permission("a3", "src/zephyr/risk/x.py")
        records = _read_jsonl(tmp_path / "audit" / "autonomy_boundary_gate.jsonl")
        assert len(records) == 3
        assert {r["decision"] for r in records} == {"allow", "escalate", "block"}
