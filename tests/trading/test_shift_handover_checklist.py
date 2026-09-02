# [A_test] module_id: MOD-GOV_shift_handover_checklist | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.trading.test_shift_handover_checklist
# [INVARIANTS] 总体状态=最差检查项级别(FAIL>WARN>PASS); 五项检查全部覆盖
# [MODIFY-GUARD] src/zephyr/trading/shift_handover_checklist.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from zephyr.trading.shift_handover_checklist import (
    CheckStatus,
    ComponentHealth,
    FundingRateState,
    MarginState,
    PositionState,
    ShiftHandoverChecklist,
    ShiftSnapshot,
    SignalState,
    main,
    shift_window_utc,
)

_NOW = datetime(2026, 8, 28, 0, 5, 0, tzinfo=UTC)


def _run(snapshot: ShiftSnapshot, shift: int = 0):
    return ShiftHandoverChecklist().run(snapshot, shift, now=_NOW)


def _item(report, name: str):
    return next(i for i in report.items if i.name == name)


class TestShiftWindow:
    def test_valid_windows(self):
        assert shift_window_utc(0) == "00:00-08:00"
        assert shift_window_utc(8) == "08:00-16:00"
        assert shift_window_utc(16) == "16:00-24:00"

    def test_invalid_shift_raises(self):
        with pytest.raises(ValueError):
            shift_window_utc(1)
        with pytest.raises(ValueError):
            shift_window_utc(24)

    def test_report_carries_window(self):
        report = _run(ShiftSnapshot(), shift=16)
        assert report.shift == 16
        assert report.window_utc == "16:00-24:00"


class TestCheckPositions:
    def test_no_positions_pass(self):
        report = _run(ShiftSnapshot())
        item = _item(report, "positions")
        assert item.status is CheckStatus.PASS
        assert item.summary == "无持仓"

    def test_healthy_positions_pass(self):
        snap = ShiftSnapshot(positions=[PositionState("BTCUSDT", 1.5, 3.0), PositionState("ETHUSDT", -2.0, 2.0)])
        assert _item(_run(snap), "positions").status is CheckStatus.PASS

    def test_missing_symbol_fail(self):
        snap = ShiftSnapshot(positions=[PositionState("", 1.0)])
        item = _item(_run(snap), "positions")
        assert item.status is CheckStatus.FAIL
        assert any("symbol" in f.message for f in item.findings)

    def test_zero_quantity_warn(self):
        snap = ShiftSnapshot(positions=[PositionState("BTCUSDT", 0.0)])
        assert _item(_run(snap), "positions").status is CheckStatus.WARN

    def test_excess_leverage_fail(self):
        snap = ShiftSnapshot(positions=[PositionState("BTCUSDT", 1.0, 25.0)])
        item = _item(_run(snap), "positions")
        assert item.status is CheckStatus.FAIL
        assert any("杠杆" in f.message for f in item.findings)

    def test_position_count_over_limit_warn(self):
        snap = ShiftSnapshot(positions=[PositionState(f"S{i}", 1.0) for i in range(101)])
        assert _item(_run(snap), "positions").status is CheckStatus.WARN


class TestCheckMargin:
    def test_missing_margin_warn(self):
        item = _item(_run(ShiftSnapshot()), "margin")
        assert item.status is CheckStatus.WARN
        assert "缺失" in item.summary

    def test_healthy_margin_pass(self):
        snap = ShiftSnapshot(margin=MarginState(equity=3000.0, used_margin=1000.0))
        item = _item(_run(snap), "margin")
        assert item.status is CheckStatus.PASS
        assert "3.00" in item.summary

    def test_no_used_margin_pass(self):
        snap = ShiftSnapshot(margin=MarginState(equity=1000.0, used_margin=0.0))
        assert _item(_run(snap), "margin").status is CheckStatus.PASS

    def test_warn_band(self):
        snap = ShiftSnapshot(margin=MarginState(equity=1300.0, used_margin=1000.0))  # ratio=1.3
        assert _item(_run(snap), "margin").status is CheckStatus.WARN

    def test_fail_band(self):
        snap = ShiftSnapshot(margin=MarginState(equity=1100.0, used_margin=1000.0))  # ratio=1.1
        assert _item(_run(snap), "margin").status is CheckStatus.FAIL

    def test_negative_equity_fail(self):
        snap = ShiftSnapshot(margin=MarginState(equity=-100.0, used_margin=1000.0))
        item = _item(_run(snap), "margin")
        assert item.status is CheckStatus.FAIL
        assert "权益为负" in item.summary


class TestCheckFunding:
    def test_no_funding_pass(self):
        item = _item(_run(ShiftSnapshot()), "funding_rate")
        assert item.status is CheckStatus.PASS
        assert item.summary == "无资金费率敞口"

    def test_normal_rate_pass(self):
        snap = ShiftSnapshot(funding_rates=[FundingRateState("BTCUSDT", 0.0001)])
        assert _item(_run(snap), "funding_rate").status is CheckStatus.PASS

    def test_high_rate_warn(self):
        snap = ShiftSnapshot(funding_rates=[FundingRateState("BTCUSDT", 0.002)])
        assert _item(_run(snap), "funding_rate").status is CheckStatus.WARN

    def test_extreme_rate_fail(self):
        snap = ShiftSnapshot(funding_rates=[FundingRateState("BTCUSDT", -0.005)])
        item = _item(_run(snap), "funding_rate")
        assert item.status is CheckStatus.FAIL
        assert any("极端" in f.message for f in item.findings)


class TestCheckSignals:
    def _iso(self, seconds_ago: float) -> str:
        return (_NOW - timedelta(seconds=seconds_ago)).isoformat()

    def test_no_signals_pass(self):
        item = _item(_run(ShiftSnapshot()), "signals")
        assert item.status is CheckStatus.PASS
        assert item.summary == "无活跃信号"

    def test_fresh_signal_pass(self):
        snap = ShiftSnapshot(signals=[SignalState("sig-1", generated_at=self._iso(60), ttl_seconds=300)])
        assert _item(_run(snap), "signals").status is CheckStatus.PASS

    def test_near_expiry_warn(self):
        snap = ShiftSnapshot(signals=[SignalState("sig-1", generated_at=self._iso(250), ttl_seconds=300)])
        assert _item(_run(snap), "signals").status is CheckStatus.WARN

    def test_stale_signal_fail(self):
        snap = ShiftSnapshot(signals=[SignalState("sig-1", generated_at=self._iso(600), ttl_seconds=300)])
        item = _item(_run(snap), "signals")
        assert item.status is CheckStatus.FAIL
        assert any("已过期" in f.message for f in item.findings)

    def test_missing_timestamp_warn(self):
        snap = ShiftSnapshot(signals=[SignalState("sig-1")])
        assert _item(_run(snap), "signals").status is CheckStatus.WARN

    def test_unparseable_timestamp_warn(self):
        snap = ShiftSnapshot(signals=[SignalState("sig-1", generated_at="not-a-time")])
        assert _item(_run(snap), "signals").status is CheckStatus.WARN

    def test_naive_timestamp_treated_as_utc(self):
        naive = (_NOW - timedelta(seconds=600)).replace(tzinfo=None).isoformat()
        snap = ShiftSnapshot(signals=[SignalState("sig-1", generated_at=naive, ttl_seconds=300)])
        assert _item(_run(snap), "signals").status is CheckStatus.FAIL


class TestCheckSystemHealth:
    def test_no_components_warn(self):
        item = _item(_run(ShiftSnapshot()), "system_health")
        assert item.status is CheckStatus.WARN
        assert "无系统健康数据" in item.summary

    def test_all_up_pass(self):
        snap = ShiftSnapshot(components=[ComponentHealth("gateway"), ComponentHealth("engine")])
        assert _item(_run(snap), "system_health").status is CheckStatus.PASS

    def test_degraded_warn(self):
        snap = ShiftSnapshot(components=[ComponentHealth("gateway", "degraded", "延迟偏高")])
        assert _item(_run(snap), "system_health").status is CheckStatus.WARN

    def test_down_fail(self):
        snap = ShiftSnapshot(components=[ComponentHealth("engine", "down", "无心跳")])
        item = _item(_run(snap), "system_health")
        assert item.status is CheckStatus.FAIL
        assert any("宕机" in f.message for f in item.findings)

    def test_unknown_status_warn(self):
        snap = ShiftSnapshot(components=[ComponentHealth("engine", "flapping")])
        assert _item(_run(snap), "system_health").status is CheckStatus.WARN


class TestOverallAggregation:
    def test_all_pass_overall_pass(self):
        snap = ShiftSnapshot(
            positions=[PositionState("BTCUSDT", 1.0)],
            margin=MarginState(3000.0, 1000.0),
            funding_rates=[FundingRateState("BTCUSDT", 0.0001)],
            components=[ComponentHealth("engine")],
        )
        report = _run(snap)
        assert report.overall is CheckStatus.PASS
        assert report.to_dict()["handover_allowed"] is True

    def test_worst_of_items_wins(self):
        snap = ShiftSnapshot(
            positions=[PositionState("BTCUSDT", 1.0, 25.0)],  # FAIL
            margin=MarginState(1300.0, 1000.0),  # WARN
            components=[ComponentHealth("engine")],  # PASS
        )
        report = _run(snap)
        assert report.overall is CheckStatus.FAIL
        assert report.to_dict()["handover_allowed"] is False

    def test_report_has_five_items(self):
        report = _run(ShiftSnapshot())
        assert [i.name for i in report.items] == ["positions", "margin", "funding_rate", "signals", "system_health"]


class TestJsonOutput:
    def test_to_dict_structure(self):
        report = _run(ShiftSnapshot(), shift=8)
        d = report.to_dict()
        assert d["shift"] == 8
        assert d["window_utc"] == "08:00-16:00"
        assert d["overall"] in ("PASS", "WARN", "FAIL")
        assert set(d["counts"]) == {"PASS", "WARN", "FAIL"}
        assert sum(d["counts"].values()) == 5
        assert isinstance(d["items"], list) and isinstance(d["generated_at"], str)

    def test_to_json_round_trip(self):
        report = _run(ShiftSnapshot())
        parsed = json.loads(report.to_json())
        assert parsed["overall"] == report.overall.value
        assert len(parsed["items"]) == 5

    def test_findings_serialized_as_strings(self):
        snap = ShiftSnapshot(components=[ComponentHealth("engine", "down")])
        d = _run(snap).to_dict()
        health = next(i for i in d["items"] if i["name"] == "system_health")
        assert health["status"] == "FAIL"
        assert health["findings"][0]["level"] == "FAIL"


class TestSnapshotFromDict:
    def test_round_trip(self):
        data = {
            "positions": [{"symbol": "BTCUSDT", "quantity": 1.5, "leverage": 3.0}],
            "margin": {"equity": 3000.0, "used_margin": 1000.0},
            "funding_rates": [{"symbol": "BTCUSDT", "rate": 0.0001}],
            "signals": [{"signal_id": "sig-1", "generated_at": _NOW.isoformat(), "ttl_seconds": 300}],
            "components": [{"name": "engine", "status": "up"}],
            "unknown_key": "ignored",
        }
        snap = ShiftSnapshot.from_dict(data)
        assert snap.positions[0].symbol == "BTCUSDT"
        assert snap.margin is not None and snap.margin.margin_ratio == pytest.approx(3.0)
        assert len(snap.signals) == 1

    def test_empty_dict(self):
        snap = ShiftSnapshot.from_dict({})
        assert snap.positions == [] and snap.margin is None
        assert _run(snap).overall is not CheckStatus.FAIL


class TestCli:
    def test_default_snapshot_exit_0(self, capsys):
        assert main(["--shift", "0"]) == 0
        out = json.loads(capsys.readouterr().out)
        assert out["shift"] == 0
        assert out["overall"] != "FAIL"

    def test_each_valid_shift(self, capsys):
        for shift in (0, 8, 16):
            assert main(["--shift", str(shift), "--compact"]) == 0
            assert json.loads(capsys.readouterr().out)["shift"] == shift

    def test_fail_snapshot_exit_1(self, tmp_path, capsys):
        snapshot_file = tmp_path / "snap.json"
        snapshot_file.write_text(json.dumps({"components": [{"name": "engine", "status": "down"}]}), encoding="utf-8")
        assert main(["--shift", "8", "--input", str(snapshot_file)]) == 1
        out = json.loads(capsys.readouterr().out)
        assert out["overall"] == "FAIL"
        assert out["handover_allowed"] is False

    def test_missing_input_file_exit_1(self, tmp_path, capsys):
        assert main(["--shift", "0", "--input", str(tmp_path / "nope.json")]) == 1
        assert "ERROR" in capsys.readouterr().err

    def test_invalid_shift_argparse_error(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--shift", "1"])
        assert exc_info.value.code == 2
