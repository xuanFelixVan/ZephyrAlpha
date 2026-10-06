# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] tests.shared.alerts.test_alert_escalation
# [DOMAIN] D_SHARED
# [INVARIANTS] 超时真源=注册表fail-closed(THD-ALERT-002=300); 显式传参覆盖; 状态属性正确
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlertThresholdConfigError
# [TESTS] self
# [TTL] permanent
"""shared/alerts AlertEscalation 测试债清偿（55 号 §7 新发现 2，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.shared.alerts.alert_escalation import (
    AlertEscalation,
    EscalationLevel,
    _load_auto_escalate_after_seconds,
)
from zephyr.shared.alerts.threshold_loader import AlertThresholdConfigError


class TestThresholdLoading:
    def test_default_timeout_from_registry(self):
        esc = AlertEscalation()
        assert esc.auto_escalate_after_seconds == 300  # THD-ALERT-002 注册表值

    def test_explicit_override(self):
        esc = AlertEscalation(auto_escalate_after_seconds=60)
        assert esc.auto_escalate_after_seconds == 60

    def test_missing_registry_fail_closed(self, tmp_path: Path):
        with pytest.raises(AlertThresholdConfigError):
            _load_auto_escalate_after_seconds(registry_path=tmp_path / "nope.yaml")


class TestStateModel:
    def test_defaults(self):
        esc = AlertEscalation()
        assert esc.level is EscalationLevel.WARNING
        assert esc.is_resolved is False
        assert esc.is_acknowledged is False
        assert esc.escalation_chain == []
        assert esc.triggered_at  # default_factory 生成

    def test_acknowledge_resolve_flags(self):
        esc = AlertEscalation(acknowledged_at="2026-08-20T10:00:00")
        assert esc.is_acknowledged is True
        assert esc.is_resolved is False
        esc2 = AlertEscalation(resolved_at="2026-08-20T11:00:00")
        assert esc2.is_resolved is True

    def test_full_fields(self):
        esc = AlertEscalation(
            alert_id="A1",
            title="回撤告警",
            level=EscalationLevel.CRITICAL,
            source="drawdown_tracker",
            escalation_chain=["owner", "wechat"],
            metadata={"k": "v"},
        )
        assert esc.alert_id == "A1"
        assert esc.level is EscalationLevel.CRITICAL
        assert esc.escalation_chain == ["owner", "wechat"]
        assert esc.metadata == {"k": "v"}
