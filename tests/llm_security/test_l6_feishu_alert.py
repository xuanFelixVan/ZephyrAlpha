# [A_test] module_id: MOD-LLM_SECURITY_l6_feishu_alert | layer=test | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §9
# [MODULE] tests.llm_security.test_l6_feishu_alert
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""L6 飞书告警测试（09 号文 §4.3 P1-1）。

验收：注入高危探针事件 → Webhook 送达；Webhook 不可达/未配置时本地持久化
不丢事件；retry 成功出队。webhook 网络调用一律 mock，不触网。
"""

from __future__ import annotations

import json
from typing import Any

from zephyr.security.llm_defense.llm_security.layers.l6_feishu_alert import LsgFeishuAlerter
from zephyr.security.security_event_bus import FeishuAlertChannel


def _make_alerter(tmp_path: Any, **kwargs: Any) -> LsgFeishuAlerter:
    kwargs.setdefault("pending_path", tmp_path / "alerts_pending.jsonl")
    kwargs.setdefault("webhook_url", "https://feishu.invalid/webhook/test")
    return LsgFeishuAlerter(**kwargs)


def _mock_webhook_ok(monkeypatch: Any) -> None:
    monkeypatch.setattr(FeishuAlertChannel, "_post_webhook", lambda self, webhook, text: True)


def _mock_webhook_down(monkeypatch: Any) -> None:
    monkeypatch.setattr(FeishuAlertChannel, "_post_webhook", lambda self, webhook, text: False)


class TestHighRiskProbeDelivery:
    def test_probe_event_delivered_via_webhook(self, tmp_path: Any, monkeypatch: Any) -> None:
        _mock_webhook_ok(monkeypatch)
        alerter = _make_alerter(tmp_path)
        delivered = alerter.send_high_risk_alert(
            layer="l1_input", rule="direct_injection", target="probe-001", result="block"
        )
        assert delivered is True
        assert alerter.pending_count() == 0

    def test_event_schema_mapping(self, tmp_path: Any, monkeypatch: Any) -> None:
        captured: list[str] = []

        def _capture(self: Any, webhook: str, text: str) -> bool:
            captured.append(text)
            return True

        monkeypatch.setattr(FeishuAlertChannel, "_post_webhook", _capture)
        alerter = _make_alerter(tmp_path)
        alerter.send_high_risk_alert(layer="l3_output", rule="pii_leak", severity="critical")
        assert captured
        text = captured[0]
        assert "severity=critical" in text
        assert "domain=lsg_security_stack" in text
        assert "lsg://l3_output/pii_leak/" in text

    def test_detail_merged_into_event(self, tmp_path: Any, monkeypatch: Any) -> None:
        _mock_webhook_ok(monkeypatch)
        alerter = _make_alerter(tmp_path)
        delivered = alerter.send_high_risk_alert(
            layer="l4_agent", rule="privilege_violation", detail={"tool": "shell"}
        )
        assert delivered is True


class TestUnreachableLocalPersistence:
    def test_unreachable_webhook_persists_event_not_lost(self, tmp_path: Any, monkeypatch: Any) -> None:
        _mock_webhook_down(monkeypatch)
        alerter = _make_alerter(tmp_path)
        delivered = alerter.send_high_risk_alert(layer="l1_input", rule="jailbreak", result="block")
        assert delivered is False
        assert alerter.pending_count() == 1

        pending_file = tmp_path / "alerts_pending.jsonl"
        records = [json.loads(line) for line in pending_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(records) == 1
        assert records[0]["status"] == "pending"
        assert records[0]["reason"] == "webhook_unreachable"
        assert records[0]["event"]["source_domain"] == "lsg_security_stack"
        assert records[0]["event"]["severity"] == "high"

    def test_webhook_not_configured_persists(self, tmp_path: Any, monkeypatch: Any) -> None:
        monkeypatch.setattr(FeishuAlertChannel, "_resolve_webhook", lambda self: "")
        alerter = _make_alerter(tmp_path)
        delivered = alerter.send_high_risk_alert(layer="l2_prompt", rule="prompt_leak", result="deny")
        assert delivered is False
        assert alerter.pending_count() == 1

    def test_retry_delivers_and_drains_queue(self, tmp_path: Any, monkeypatch: Any) -> None:
        _mock_webhook_down(monkeypatch)
        alerter = _make_alerter(tmp_path)
        alerter.send_high_risk_alert(layer="l1_input", rule="direct_injection")
        alerter.send_high_risk_alert(layer="l5_resource", rule="cost_breaker")
        assert alerter.pending_count() == 2

        _mock_webhook_ok(monkeypatch)
        stats = alerter.retry_pending()
        assert stats["delivered"] == 2
        assert alerter.pending_count() == 0


class TestDryRun:
    def test_dry_run_no_network_but_traced(self, tmp_path: Any, monkeypatch: Any) -> None:
        def _forbidden(self: Any, webhook: str, text: str) -> bool:
            raise AssertionError("dry_run 模式不得发起网络请求")

        monkeypatch.setattr(FeishuAlertChannel, "_post_webhook", _forbidden)
        alerter = _make_alerter(tmp_path, dry_run=True)
        delivered = alerter.send_high_risk_alert(layer="l1_input", rule="direct_injection")
        assert delivered is True
        dryrun_file = tmp_path / "alerts_dryrun.jsonl"
        assert dryrun_file.exists()
        assert "direct_injection" in dryrun_file.read_text(encoding="utf-8")
