# [A_test] module_id: MOD-GOV_exchange_reg_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_exchange_reg_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_exchange_reg_monitor.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.data_governance.exchange_reg_monitor import ExchangeRegMonitor


class TestExchangeRegMonitorInit:
    def test_exchanges_list_not_empty(self):
        monitor = ExchangeRegMonitor()
        assert len(monitor.EXCHANGES) > 0

    def test_exchanges_contains_major(self):
        monitor = ExchangeRegMonitor()
        assert "NYSE" in monitor.EXCHANGES
        assert "NASDAQ" in monitor.EXCHANGES

    def test_exchanges_count(self):
        monitor = ExchangeRegMonitor()
        assert len(monitor.EXCHANGES) == 5


class TestListExchanges:
    def test_returns_list(self):
        monitor = ExchangeRegMonitor()
        result = monitor.list_exchanges()
        assert isinstance(result, list)

    def test_returns_all_exchanges(self):
        monitor = ExchangeRegMonitor()
        result = monitor.list_exchanges()
        assert result == ["SSE", "SZSE", "HKEX", "NYSE", "NASDAQ"]

    def test_no_duplicate_exchanges(self):
        monitor = ExchangeRegMonitor()
        result = monitor.list_exchanges()
        assert len(result) == len(set(result))


class TestRegisterChange:
    def test_returns_dict_with_required_keys(self):
        monitor = ExchangeRegMonitor()
        result = monitor.register_change("NYSE", "Rule-42", "2026-06-01")
        assert "exchange" in result
        assert "rule" in result
        assert "effective" in result
        assert "requires_escalation" in result

    def test_requires_escalation_always_true(self):
        monitor = ExchangeRegMonitor()
        result = monitor.register_change("SSE", "NewRule", "2026-07-01")
        assert result["requires_escalation"] is True

    def test_fields_match_input(self):
        monitor = ExchangeRegMonitor()
        result = monitor.register_change("HKEX", "MarginRule", "2026-08-15")
        assert result["exchange"] == "HKEX"
        assert result["rule"] == "MarginRule"
        assert result["effective"] == "2026-08-15"

    def test_boundary_empty_strings(self):
        monitor = ExchangeRegMonitor()
        result = monitor.register_change("", "", "")
        assert result["exchange"] == ""
        assert result["rule"] == ""
        assert result["effective"] == ""
        assert result["requires_escalation"] is True

    def test_multiple_registrations_independent(self):
        monitor = ExchangeRegMonitor()
        r1 = monitor.register_change("NYSE", "Rule-A", "2026-06-01")
        r2 = monitor.register_change("SSE", "Rule-B", "2026-07-01")
        assert r1["exchange"] != r2["exchange"]
        assert r1["rule"] != r2["rule"]
