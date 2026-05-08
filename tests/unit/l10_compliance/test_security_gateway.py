"""
单元测试：src/zephyr/l10_compliance/security_gateway_base.py
=============================================================

覆盖矩阵：
  SecurityGateway (ABC):
    - 抽象类不可实例化 × 1
    - 子类化 pre_filter / security_scan / decide × 1
  ComplianceEngine (ABC):
    - 抽象类不可实例化 × 1
    - 子类化 evaluate / enforce × 1
    - register_rule 默认 no-op × 1
  AuditAction:
    - 枚举完整性 × 1
  AuditDecision:
    - frozen × 1
    - 默认值 × 1
  DefaultSecurityGateway (from implementations):
    - pre_filter 返回 True × 1
    - security_scan 检测 eval × 1
    - security_scan 检测 os.system × 1
    - security_scan 干净内容返回空 × 1
    - decide BLOCK risks → BLOCK × 1
    - decide WARN risks → FLAG × 1
    - decide 无风险 → ALLOW × 1
"""
from __future__ import annotations


from datetime import datetime
from typing import Any

import pytest
from zephyr.l10_compliance.security_gateway_base import (
    AuditAction,
    AuditDecision,
    ComplianceEngine,
    ComplianceRule,
    SecurityGateway,
)


class TestSecurityGatewayABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            SecurityGateway()

    def test_subclass_implements_interface(self):
        class _TestGateway(SecurityGateway):
            def pre_filter(self, content: str, source: str) -> bool:
                return True

            def security_scan(self, content: str) -> list[str]:
                return []

            def decide(self, risks: list[str], context: dict[str, Any]) -> AuditDecision:
                return AuditDecision(
                    decision_id="test",
                    action=AuditAction.ALLOW,
                    rule_id="test-rule",
                    reason="no risks",
                )

        gw = _TestGateway()
        assert gw.pre_filter("hello", "test") is True
        assert gw.security_scan("hello") == []
        decision = gw.decide([], {})
        assert decision.action == AuditAction.ALLOW


class TestComplianceEngineABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ComplianceEngine()

    def test_subclass_implements_interface(self):
        class _TestEngine(ComplianceEngine):
            def evaluate(self, context: dict[str, Any], idempotency_key: str) -> list[ComplianceRule]:
                return []

            def enforce(self, rule: ComplianceRule, context: dict[str, Any]) -> AuditDecision:
                return AuditDecision(
                    decision_id="test",
                    action=AuditAction.ALLOW,
                    rule_id=rule.rule_id,
                    reason="ok",
                )

        engine = _TestEngine()
        rules = engine.evaluate({}, "test-key")
        assert rules == []

    def test_register_rule_default_noop(self):
        class _TestEngine(ComplianceEngine):
            def evaluate(self, context: dict[str, Any], idempotency_key: str) -> list[ComplianceRule]:
                return []

            def enforce(self, rule: ComplianceRule, context: dict[str, Any]) -> AuditDecision:
                return AuditDecision(
                    decision_id="test",
                    action=AuditAction.ALLOW,
                    rule_id="r1",
                    reason="ok",
                )

        engine = _TestEngine()
        rule = ComplianceRule(
            rule_id="r1",
            rule_name="test",
            rule_type="position",
            rule_logic="check",
            severity="high",
            enforcement_action="block",
            jurisdiction="CN_CSRC",
            description="test rule",
            is_active=True,
            version="1.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            idempotency_key="test",
        )
        engine.register_rule(rule)


class TestAuditAction:
    def test_all_values(self):
        expected = {"allow", "block", "flag", "redirect"}
        actual = {e.value for e in AuditAction}
        assert actual == expected


class TestAuditDecision:
    def test_frozen(self):
        d = AuditDecision(
            decision_id="d1",
            action=AuditAction.BLOCK,
            rule_id="r1",
            reason="test",
        )
        with pytest.raises(Exception):
            d.action = AuditAction.ALLOW

    def test_defaults(self):
        d = AuditDecision(
            decision_id="d1",
            action=AuditAction.ALLOW,
            rule_id="r1",
            reason="ok",
        )
        assert isinstance(d.timestamp, datetime)
        assert d.metadata == {}


class TestDefaultSecurityGateway:
    def test_pre_filter_returns_true(self):
        from zephyr.l10_compliance.implementations.default_security_gateway import DefaultSecurityGateway

        gw = DefaultSecurityGateway()
        assert gw.pre_filter("eval(x)", "ai") is True

    def test_security_scan_detects_eval(self):
        from zephyr.l10_compliance.implementations.default_security_gateway import DefaultSecurityGateway

        gw = DefaultSecurityGateway()
        risks = gw.security_scan("eval(user_input)")
        assert len(risks) > 0

    def test_security_scan_detects_os_system(self):
        from zephyr.l10_compliance.implementations.default_security_gateway import DefaultSecurityGateway

        gw = DefaultSecurityGateway()
        risks = gw.security_scan("os.system('rm -rf /')")
        assert len(risks) > 0

    def test_security_scan_clean_content(self):
        from zephyr.l10_compliance.implementations.default_security_gateway import DefaultSecurityGateway

        gw = DefaultSecurityGateway()
        risks = gw.security_scan("x = 1 + 2")
        assert len(risks) == 0

    def test_decide_with_blocked_risks(self):
        from zephyr.l10_compliance.implementations.default_security_gateway import DefaultSecurityGateway

        gw = DefaultSecurityGateway()
        risks = gw.security_scan("eval(user_input)")
        decision = gw.decide(risks, {"source": "ai"})
        assert decision.action == AuditAction.BLOCK
        assert "BLOCK:dynamic_eval" in decision.metadata.get("blocked_risks", [])

    def test_decide_with_warned_risks_flags(self):
        from zephyr.l10_compliance.implementations.default_security_gateway import DefaultSecurityGateway

        gw = DefaultSecurityGateway()
        risks = gw.security_scan("DROP TABLE users;")
        decision = gw.decide(risks, {"source": "ai"})
        assert decision.action == AuditAction.FLAG

    def test_decide_without_risks_allows(self):
        from zephyr.l10_compliance.implementations.default_security_gateway import DefaultSecurityGateway

        gw = DefaultSecurityGateway()
        decision = gw.decide([], {})
        assert decision.action == AuditAction.ALLOW
