# [BLUEPRINT] MOD-POS-030 | docs/_working/fullconnect_campaign/e_decision_chain/06_f42_p1_position_checkup.md（G42-1）
# [MODULE] tests.position.test_position_checkup_orchestrator
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.position_checkup_orchestrator(run_position_checkup/default_positions_loader/CheckupPositionInput)
# [INVARIANTS] 测试隔离零生产路径（audit_path/REPO_ROOT 全走 tmp_path）；动作映射确定性断言；缺装配=人工确认默认态；fail-open 逐段断言
# [TTL] permanent

"""P1 持仓体检棒单测：六段链编排/参数传递/动作映射/裁决消费/审计落盘（全 mock）。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.position.core.position_adjudication_center import LayerVerdict
from zephyr.position.core.position_checkup_orchestrator import (
    CheckupPositionInput,
    default_positions_loader,
    run_position_checkup,
)


def _allow_layer(name: str, weight: float = 0.25):
    def _fn(_request):
        return LayerVerdict(layer=name, allowed=True, adjusted_weight=weight, reason="mock-allow")

    return _fn


def _wired_layers() -> dict:
    return {name: _allow_layer(name) for name in ("portfolio", "strategy", "symbol", "dynamic")}


@pytest.fixture()
def _isolate_repo_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """REPO_ROOT 改指 tmp：默认审计面/投放面零触生产路径。"""
    monkeypatch.setattr("zephyr.position.core.position_checkup_orchestrator.REPO_ROOT", str(tmp_path))
    return tmp_path


def _basic(symbol: str = "600519.SH", **kw) -> CheckupPositionInput:
    base = dict(
        symbol=symbol,
        strategy_id="s1",
        entry_price=100.0,
        current_price=95.0,
        stop_loss_price=90.0,
        atr_value=2.0,
        weight_actual=0.06,
        weight_target=0.05,
    )
    base.update(kw)
    return CheckupPositionInput(**base)


class TestActionMapping:
    """P1-06 确定性动作映射：止损∨DEAD→EXIT；漂移越带→REDUCE；其余→HOLD。"""

    def test_stop_loss_triggered_maps_exit(self, _isolate_repo_root: Path, tmp_path: Path) -> None:
        pos = _basic(current_price=89.0)  # 跌破止损线 90
        rep = run_position_checkup(
            [pos], data_date="2026-09-29", adjudication_layers=_wired_layers(), audit_path=tmp_path / "a.jsonl"
        )
        row = rep["positions"][0]
        assert row["derived_action"] == "EXIT"
        assert row["action"] == "EXIT"
        assert row["manual_confirmation"] is False
        adj = row["segments"]["adjudication"]
        assert adj["status"] == "ok" and adj["adjudicated"] is True and adj["allowed"] is True

    def test_thesis_dead_maps_exit(self, tmp_path: Path) -> None:
        pos = _basic(thesis_type="LIMIT_UP_CHASING", thesis_evidence={"sentiment_ladder_alive": False})
        rep = run_position_checkup(
            [pos], data_date="2026-09-29", adjudication_layers=_wired_layers(), audit_path=tmp_path / "a.jsonl"
        )
        assert rep["positions"][0]["derived_action"] == "EXIT"

    def test_drift_overweight_maps_reduce(self, tmp_path: Path) -> None:
        pos = _basic(weight_actual=0.20, weight_target=0.05)  # 漂移 0.15 > 0.03 越带
        rep = run_position_checkup(
            [pos], data_date="2026-09-29", adjudication_layers=_wired_layers(), audit_path=tmp_path / "a.jsonl"
        )
        assert rep["portfolio_drift"]["has_drift"] is True
        assert rep["positions"][0]["derived_action"] == "REDUCE"

    def test_healthy_position_maps_hold_without_adjudication(self, tmp_path: Path) -> None:
        rep = run_position_checkup(
            [_basic()], data_date="2026-09-29", adjudication_layers=_wired_layers(), audit_path=tmp_path / "a.jsonl"
        )
        row = rep["positions"][0]
        assert row["action"] == "HOLD"
        assert row["segments"]["adjudication"]["adjudicated"] is False

    def test_summary_counts_actions(self, tmp_path: Path) -> None:
        rep = run_position_checkup(
            [_basic(), _basic("000001.SZ", current_price=89.0)],
            data_date="2026-09-29",
            adjudication_layers=_wired_layers(),
            audit_path=tmp_path / "a.jsonl",
        )
        assert rep["summary"]["actions"] == {"HOLD": 1, "EXIT": 1}


class TestParameterPassing:
    """编排触发/参数传递：分段输入直传各体检器，缺维度降级不误判。"""

    def test_segments_receive_inputs(self, tmp_path: Path) -> None:
        pos = _basic(
            thesis_type="MULTI_FACTOR",
            thesis_evidence={"factor_exposure_drift": 0.7},
            stop_loss_inputs={"sector_momentum": -0.05},
        )
        rep = run_position_checkup(
            [pos], data_date="2026-09-29", adjudication_layers=_wired_layers(), audit_path=tmp_path / "a.jsonl"
        )
        seg = rep["positions"][0]["segments"]
        assert seg["triage"]["status"] == "ok" and seg["triage"]["triage"] == "MONITOR"
        assert seg["thesis"]["status"] == "ok" and seg["thesis"]["state"] == "DEAD"
        assert seg["stop_loss"]["status"] == "ok"

    def test_missing_dimensions_degrade_skipped(self, tmp_path: Path) -> None:
        pos = CheckupPositionInput(symbol="300750.SZ")
        rep = run_position_checkup([pos], data_date="2026-09-29", audit_path=tmp_path / "a.jsonl")
        seg = rep["positions"][0]["segments"]
        assert seg["triage"]["status"] == "skipped"
        assert seg["thesis"]["status"] == "skipped"
        assert seg["stop_loss"]["status"] == "skipped"
        assert seg["snapshot"]["status"] == "ok"

    def test_bad_state_fails_open_as_error(self, tmp_path: Path) -> None:
        rep = run_position_checkup([_basic(state="BOGUS")], data_date="2026-09-29", audit_path=tmp_path / "a.jsonl")
        seg = rep["positions"][0]["segments"]
        assert seg["snapshot"]["status"] == "error"
        assert rep["positions"][0]["action"] == "HOLD"  # 快照坏不擢升动作（人工面归裁决段语义外）

    def test_bad_date_fail_closed(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="data_date 非法"):
            run_position_checkup([_basic()], data_date="20260929", audit_path=tmp_path / "a.jsonl")


class TestAdjudicationConsumption:
    """体检器输出消费：裁决中心四层 callable 注入与人工确认默认态。"""

    def test_denied_verdict_downgrades_to_manual(self, tmp_path: Path) -> None:
        def _deny(_request):
            return LayerVerdict(layer="portfolio", allowed=False, adjusted_weight=0.0, violations=("V",), reason="r")

        layers = {**_wired_layers(), "portfolio": _deny}
        pos = _basic(current_price=85.0)  # 破止损→EXIT 意图
        rep = run_position_checkup(
            [pos], data_date="2026-09-29", adjudication_layers=layers, audit_path=tmp_path / "a.jsonl"
        )
        row = rep["positions"][0]
        assert row["derived_action"] == "EXIT"
        assert row["action"] == "MANUAL_CONFIRM" and row["manual_confirmation"] is True

    def test_layers_not_wired_manual_confirmation(self, tmp_path: Path) -> None:
        rep = run_position_checkup(
            [_basic(current_price=85.0)], data_date="2026-09-29", audit_path=tmp_path / "a.jsonl"
        )
        row = rep["positions"][0]
        assert row["segments"]["adjudication"]["reason"] == "adjudication_layers_not_wired"
        assert row["action"] == "MANUAL_CONFIRM"

    def test_reduce_without_target_uses_actual_anchor(self, tmp_path: Path) -> None:
        pos = _basic(weight_actual=0.20, weight_target=None)
        rep = run_position_checkup(
            [pos], data_date="2026-09-29", adjudication_layers=_wired_layers(), audit_path=tmp_path / "a.jsonl"
        )
        row = rep["positions"][0]
        # 目标权重缺席→漂移段 skip→不擢升 REDUCE（组合级看结构需双权重锚）
        assert row["derived_action"] == "HOLD"
        assert rep["portfolio_drift"]["status"] == "skipped"


class TestAuditAndLoader:
    """审计 JSONL 追加（append-only）+ 投放面读数契约（REPO_ROOT 已隔离 tmp）。"""

    def test_audit_jsonl_appends(self, tmp_path: Path) -> None:
        sink = tmp_path / "audit.jsonl"
        run_position_checkup([_basic()], data_date="2026-09-29", audit_path=sink)
        run_position_checkup([_basic()], data_date="2026-09-29", audit_path=sink)
        lines = sink.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[1])["node"] == "TDM-P-P1"

    def test_default_audit_path_under_isolated_root(self, _isolate_repo_root: Path) -> None:
        rep = run_position_checkup([_basic()], data_date="2026-09-29")
        expected = _isolate_repo_root / "data" / "runtime" / "position_checkup" / "audit_2026-09-29.jsonl"
        assert rep["audit_path"] == str(expected)
        assert expected.exists()

    def test_audit_failure_fail_open(self, tmp_path: Path) -> None:
        blocker = tmp_path / "blocker"
        blocker.write_text("x", encoding="utf-8")
        rep = run_position_checkup([_basic()], data_date="2026-09-29", audit_path=blocker / "nested" / "a.jsonl")
        assert "audit_error" in rep
        assert rep["portfolio_drift"]["status"] in {"ok", "skipped"}

    def test_loader_missing_file_returns_empty(self, _isolate_repo_root: Path) -> None:
        assert default_positions_loader("2026-09-29") == []

    def test_loader_reads_dropped_inputs(self, _isolate_repo_root: Path) -> None:
        drop = _isolate_repo_root / "data" / "runtime" / "position_checkup"
        drop.mkdir(parents=True)
        (drop / "inputs_2026-09-29.json").write_text('[{"symbol":"600519.SH"}]', encoding="utf-8")
        assert default_positions_loader("2026-09-29") == [{"symbol": "600519.SH"}]
