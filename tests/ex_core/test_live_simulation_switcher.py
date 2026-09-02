# [BLUEPRINT] MOD-EX-035 | docs/03_modules/MOD-EX-035/
# [MODULE] tests.ex_core.test_live_simulation_switcher
# [DOMAIN] D_EX_CORE
# [INVARIANTS] 默认模拟盘; 令牌失败/空令牌Fail-Closed停留模拟; 令牌原文不落痕(仅指纹); 降风险方向免令牌; 假钟确定性
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LiveSwitchError
# [TESTS] self
# [TTL] permanent
"""实盘/模拟切换开关测试（MOD-EX-035，阶段9 执行链路批）。"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from zephyr.ex_core.live_simulation_switcher import (
    LiveSimulationSwitcher,
    LiveSwitchError,
    TradingMode,
    _fingerprint,
)

_GOOD_TOKEN = "owner-signed-token-20260823"


def _make_switcher(**kwargs):
    return LiveSimulationSwitcher(lambda token: token == _GOOD_TOKEN, **kwargs)


class TestDefaults:
    def test_default_mode_is_simulation(self):
        switcher = _make_switcher()
        assert switcher.current_mode is TradingMode.SIMULATION
        assert switcher.is_live is False
        assert switcher.switch_history() == ()


class TestSwitchToLive:
    def test_valid_token_switches_and_records(self):
        clock_values = iter([datetime(2026, 8, 23, 9, 30, tzinfo=UTC)])
        switcher = _make_switcher(clock=lambda: next(clock_values))
        record = switcher.switch_to_live(confirmation_token=_GOOD_TOKEN, reason="实盘小资金上线", operator="owner")
        assert switcher.is_live is True
        assert record.from_mode is TradingMode.SIMULATION
        assert record.to_mode is TradingMode.LIVE
        assert record.reason == "实盘小资金上线"
        assert record.token_fingerprint == _fingerprint(_GOOD_TOKEN)
        assert _GOOD_TOKEN not in repr(record)  # 令牌原文不落痕

    def test_wrong_token_fail_closed(self):
        switcher = _make_switcher()
        with pytest.raises(LiveSwitchError) as exc_info:
            switcher.switch_to_live(confirmation_token="wrong", reason="x")
        assert exc_info.value.error_code == "ZA-EX-0019"
        assert switcher.current_mode is TradingMode.SIMULATION  # 停留模拟盘
        assert switcher.switch_history() == ()  # 失败不留切换痕

    def test_empty_token_fail_closed(self):
        switcher = _make_switcher()
        with pytest.raises(LiveSwitchError):
            switcher.switch_to_live(confirmation_token="", reason="x")
        assert switcher.current_mode is TradingMode.SIMULATION

    def test_verifier_exception_treated_as_rejection(self):
        def _boom(_token):
            raise RuntimeError("token store offline")

        switcher = LiveSimulationSwitcher(_boom)
        with pytest.raises(LiveSwitchError):
            switcher.switch_to_live(confirmation_token=_GOOD_TOKEN, reason="x")
        assert switcher.current_mode is TradingMode.SIMULATION

    def test_empty_reason_rejected(self):
        switcher = _make_switcher()
        with pytest.raises(LiveSwitchError):
            switcher.switch_to_live(confirmation_token=_GOOD_TOKEN, reason="  ")
        assert switcher.current_mode is TradingMode.SIMULATION

    def test_double_live_rejected(self):
        switcher = _make_switcher()
        switcher.switch_to_live(confirmation_token=_GOOD_TOKEN, reason="r")
        with pytest.raises(LiveSwitchError):
            switcher.switch_to_live(confirmation_token=_GOOD_TOKEN, reason="r2")


class TestSwitchToSimulation:
    def test_live_to_sim_no_token_needed(self):
        switcher = _make_switcher()
        switcher.switch_to_live(confirmation_token=_GOOD_TOKEN, reason="上线")
        record = switcher.switch_to_simulation(reason="回撤超限降级")
        assert switcher.current_mode is TradingMode.SIMULATION
        assert record.token_fingerprint == ""
        assert len(switcher.switch_history()) == 2

    def test_double_simulation_rejected(self):
        switcher = _make_switcher()
        with pytest.raises(LiveSwitchError):
            switcher.switch_to_simulation(reason="x")


class TestAuditTrail:
    def test_audit_sink_receives_record(self):
        sink: list = []
        switcher = _make_switcher(audit_sink=sink.append)
        switcher.switch_to_live(confirmation_token=_GOOD_TOKEN, reason="r")
        assert len(sink) == 1
        assert sink[0].to_mode is TradingMode.LIVE

    def test_audit_sink_failure_does_not_rollback(self):
        def _bad_sink(_record):
            raise RuntimeError("audit store offline")

        switcher = _make_switcher(audit_sink=_bad_sink)
        switcher.switch_to_live(confirmation_token=_GOOD_TOKEN, reason="r")
        assert switcher.is_live is True  # 审计失败不回滚切换
        assert len(switcher.switch_history()) == 1  # 内存留痕仍在
