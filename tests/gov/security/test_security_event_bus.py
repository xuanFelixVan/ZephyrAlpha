"""统一安全事件总线测试（16号文 Phase 0：P0-1 schema 校验 / P0-3 告警通道）。

覆盖：合法/缺字段/非法枚举/版本不匹配的 schema 校验；四域 adapter 探针 100%
通过；单 adapter 异常独立降级不阻塞总线；高危告警本地持久化不丢；webhook
失败降级与重试语义；dry_run 留痕不真发。
"""

from __future__ import annotations

import json

import pytest

from zephyr.security.security_event_bus import (
    SCHEMA_VERSION,
    DomainEventAdapter,
    FeishuAlertChannel,
    SecurityEvent,
    SecurityEventBus,
    SecurityEventValidationError,
    Severity,
)


def _valid_raw() -> dict:
    return {
        "source_domain": "runtime",
        "threat_category": "emergence",
        "severity": "high",
        "evidence_ref": "runtime://probe/detector",
        "session_ref": "sess-probe",
        "schema_version": SCHEMA_VERSION,
    }


class TestSchemaValidation:
    def test_valid_event_accepted(self):
        event = SecurityEvent.from_raw(_valid_raw())
        assert event.schema_version == SCHEMA_VERSION
        assert event.severity is Severity.HIGH
        assert event.event_id

    def test_missing_required_field_rejected(self):
        raw = _valid_raw()
        del raw["evidence_ref"]
        with pytest.raises(SecurityEventValidationError):
            SecurityEvent.from_raw(raw)

    def test_missing_source_domain_rejected(self):
        raw = _valid_raw()
        del raw["source_domain"]
        with pytest.raises(SecurityEventValidationError):
            SecurityEvent.from_raw(raw)

    def test_illegal_severity_enum_rejected(self):
        raw = _valid_raw()
        raw["severity"] = "p0_fatal"
        with pytest.raises(SecurityEventValidationError):
            SecurityEvent.from_raw(raw)

    def test_illegal_threat_category_rejected(self):
        raw = _valid_raw()
        raw["threat_category"] = "alien_abduction"
        with pytest.raises(SecurityEventValidationError):
            SecurityEvent.from_raw(raw)

    def test_unsupported_schema_version_rejected(self):
        raw = _valid_raw()
        raw["schema_version"] = "0.9"
        with pytest.raises(SecurityEventValidationError):
            SecurityEvent.from_raw(raw)

    def test_empty_evidence_ref_rejected(self):
        raw = _valid_raw()
        raw["evidence_ref"] = ""
        with pytest.raises(SecurityEventValidationError):
            SecurityEvent.from_raw(raw)

    def test_extra_field_rejected(self):
        raw = _valid_raw()
        raw["unexpected"] = "x"
        with pytest.raises(SecurityEventValidationError):
            SecurityEvent.from_raw(raw)

    def test_bad_ts_rejected(self):
        raw = _valid_raw()
        raw["ts"] = "not-a-timestamp"
        with pytest.raises(SecurityEventValidationError):
            SecurityEvent.from_raw(raw)


class TestFourDomainAdapters:
    """P0-1 验收：四域各注入一条合成探针事件，schema 校验 100% 通过。"""

    PROBES = {
        "lsg_security_stack": {
            "layer": "l1",
            "rule": "injection_pattern",
            "target": "user_prompt",
            "result": "blocked",
            "session_id": "sess-lsg",
        },
        "autonomy_gate": {
            "gate": "path_guard",
            "decision": "block",
            "reason": "protected path",
            "agent_id": "agent-1",
            "session_id": "sess-gate",
        },
        "governance_gate": {
            "policy_id": "GOV-AI-001",
            "verdict": "RED",
            "finding": "unapproved_exemption",
            "session_id": "sess-gov",
        },
        "runtime": {
            "detector": "emergent_behavior_detector",
            "state": "CRITICAL",
            "risk_score": 0.91,
            "is_breached": True,
            "session_id": "sess-rt",
        },
    }

    def test_all_four_probes_pass_schema_and_persist(self, tmp_path):
        bus = SecurityEventBus(event_dir=tmp_path, dry_run_alert=True)
        bus.register_default_adapters()
        for name, raw in self.PROBES.items():
            event = bus.emit_via_adapter(name, raw)
            assert event is not None, f"adapter {name} 探针被拒"
        assert bus.degraded == []
        events = list(bus.iter_events())
        assert len(events) == 4
        domains = {e.source_domain.value for e in events}
        assert domains == {"lsg_security_stack", "autonomy_gate", "governance_gate", "runtime"}
        # 落盘后可被机器遍历消费且每条仍可过 schema 校验（iter_events 内部 from_raw）
        for line in bus.events_path.read_text(encoding="utf-8").splitlines():
            SecurityEvent.from_raw(json.loads(line))

    def test_adapter_severity_mapping(self, tmp_path):
        bus = SecurityEventBus(event_dir=tmp_path, dry_run_alert=True)
        bus.register_default_adapters()
        assert bus.emit_via_adapter("lsg_security_stack", self.PROBES["lsg_security_stack"]).severity is Severity.HIGH
        assert bus.emit_via_adapter("runtime", self.PROBES["runtime"]).severity is Severity.CRITICAL
        gov = bus.emit_via_adapter("governance_gate", {"policy_id": "P", "verdict": "PASS"})
        assert gov.severity is Severity.LOW


class _BrokenAdapter(DomainEventAdapter):
    name = "broken"

    def raw_mapping(self, raw):
        raise RuntimeError("synthetic adapter failure")


class TestAdapterIndependentDegradation:
    def test_single_adapter_failure_does_not_block_bus(self, tmp_path):
        bus = SecurityEventBus(event_dir=tmp_path, dry_run_alert=True)
        bus.register_default_adapters()
        bus.register_adapter(_BrokenAdapter())
        assert bus.emit_via_adapter("broken", {"x": 1}) is None
        assert len(bus.degraded) == 1
        assert bus.degraded[0]["adapter"] == "broken"
        # 总线与其他 adapter 仍正常
        event = bus.emit_via_adapter("runtime", {"detector": "d", "state": "STABLE"})
        assert event is not None
        assert bus.count_events() == 1

    def test_unregistered_adapter_degrades_not_raises(self, tmp_path):
        bus = SecurityEventBus(event_dir=tmp_path, dry_run_alert=True)
        assert bus.emit_via_adapter("ghost", {}) is None
        assert len(bus.degraded) == 1

    def test_schema_reject_via_adapter_degrades_not_raises(self, tmp_path):
        bus = SecurityEventBus(event_dir=tmp_path, dry_run_alert=True)
        bus.register_default_adapters()
        # adapter 默认 severity 映射合法，但显式注入非法枚举应被 schema 拒收并降级
        assert bus.emit_via_adapter("runtime", {"detector": "d", "severity": "ultra"}) is None
        assert len(bus.degraded) == 1
        assert bus.count_events() == 0


class TestAlertChannel:
    def test_webhook_not_configured_persists_pending(self, tmp_path):
        channel = FeishuAlertChannel(pending_path=tmp_path / "alerts_pending.jsonl", webhook_url="")
        event = SecurityEvent.from_raw(_valid_raw())
        assert channel.send(event) is False
        assert channel.pending_count() == 1

    def test_webhook_unreachable_persists_pending_not_lost(self, tmp_path):
        channel = FeishuAlertChannel(
            pending_path=tmp_path / "alerts_pending.jsonl",
            webhook_url="http://127.0.0.1:1/webhook",
            timeout_sec=0.5,
        )
        event = SecurityEvent.from_raw(_valid_raw())
        assert channel.send(event) is False
        assert channel.pending_count() == 1
        rec = json.loads((tmp_path / "alerts_pending.jsonl").read_text(encoding="utf-8").strip())
        assert rec["status"] == "pending"
        assert rec["event"]["event_id"] == event.event_id

    def test_retry_failure_increments_then_dead_letters(self, tmp_path):
        channel = FeishuAlertChannel(
            pending_path=tmp_path / "alerts_pending.jsonl",
            webhook_url="http://127.0.0.1:1/webhook",
            timeout_sec=0.5,
        )
        event = SecurityEvent.from_raw(_valid_raw())
        channel.send(event)
        stats = channel.retry_pending()
        assert stats["retried"] == 1 and stats["delivered"] == 0
        rec = json.loads((tmp_path / "alerts_pending.jsonl").read_text(encoding="utf-8").strip())
        assert rec["retry_count"] == 1  # 不丢，计数累加

    def test_retry_success_drains_queue(self, tmp_path, monkeypatch):
        channel = FeishuAlertChannel(
            pending_path=tmp_path / "alerts_pending.jsonl",
            webhook_url="http://127.0.0.1:1/webhook",
            timeout_sec=0.5,
        )
        channel.send(SecurityEvent.from_raw(_valid_raw()))
        assert channel.pending_count() == 1
        monkeypatch.setattr(channel, "_post_webhook", lambda url, text: True)
        stats = channel.retry_pending()
        assert stats["delivered"] == 1
        assert channel.pending_count() == 0

    def test_high_severity_triggers_dry_run_alert_trace(self, tmp_path):
        bus = SecurityEventBus(event_dir=tmp_path, dry_run_alert=True)
        bus.emit(_valid_raw())  # severity=high
        dryrun = tmp_path / "alerts_dryrun.jsonl"
        assert dryrun.exists()
        rec = json.loads(dryrun.read_text(encoding="utf-8").strip())
        assert rec["status"] == "dry_run"
        assert "severity=high" in rec["text"]

    def test_low_severity_does_not_alert(self, tmp_path):
        bus = SecurityEventBus(event_dir=tmp_path, dry_run_alert=True)
        raw = _valid_raw()
        raw["severity"] = "low"
        bus.emit(raw)
        assert not (tmp_path / "alerts_dryrun.jsonl").exists()
        assert bus.count_events() == 1

    def test_invalid_event_rejected_not_persisted(self, tmp_path):
        bus = SecurityEventBus(event_dir=tmp_path, dry_run_alert=True)
        with pytest.raises(SecurityEventValidationError):
            bus.emit({"severity": "high"})
        assert bus.count_events() == 0
