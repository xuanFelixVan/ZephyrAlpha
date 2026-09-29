"""L9 知识供给就绪度闸测试（F34 消费接线，st-c9-f34-20260929）。

仿 test_anchored_cap.py 三段式：态映射 / PIT 装载多态 / 组合层裁剪留痕。
设计真源=f34 册 §四缺口 3："黄/红=降级留痕，仿 anchored_cap 旁路先例"。
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from zephyr.pf_alloc.allocation_inputs import (
    L9_READINESS_RED_CAP,
    L9_READINESS_STALE_DAYS,
    L9_READINESS_YELLOW_CAP,
    l9_cap_from_status,
    l9_readiness_enabled,
    load_l9_readiness,
)


class TestStatusMapping:
    """AGG 汇总态 → 降级上限：黄轻降/红重降/未知保守按红。"""

    def test_yellow_light_trim(self) -> None:
        assert l9_cap_from_status("yellow") == L9_READINESS_YELLOW_CAP

    def test_red_heavy_trim(self) -> None:
        assert l9_cap_from_status("red") == L9_READINESS_RED_CAP

    def test_unknown_conservative_red(self) -> None:
        assert l9_cap_from_status("weird") == L9_READINESS_RED_CAP
        assert l9_cap_from_status("") == L9_READINESS_RED_CAP

    def test_red_tighter_than_yellow(self) -> None:
        assert L9_READINESS_RED_CAP < L9_READINESS_YELLOW_CAP < 1.0


class TestLoadL9Readiness:
    """PIT 装载多态：旁路/无行/陈旧/态坏 → applied=False 留痕；green 不施加；黄/红施加。"""

    @staticmethod
    def _reader(rows: list):
        return lambda sql: rows

    @staticmethod
    def _row(day: date, status: str):
        return {"trade_date": day, "status": status, "produced_at": f"{day} 08:00:00"}

    def test_disabled_flag_bypasses(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        flag = tmp_path / "l9_readiness_check.disabled"
        flag.write_text("", encoding="utf-8")
        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", flag)
        assert not l9_readiness_enabled()
        gate = load_l9_readiness("2026-09-29", reader=self._reader([self._row(date(2026, 9, 28), "red")]))
        assert gate.applied is False
        assert gate.degraded_reasons == ("disabled_flag",)

    def test_enabled_when_no_flag(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", tmp_path / "absent.flag")
        assert l9_readiness_enabled()

    def test_no_row_fail_disclosed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", tmp_path / "absent.flag")
        gate = load_l9_readiness("2026-09-29", reader=self._reader([]))
        assert gate.applied is False
        assert gate.degraded_reasons == ("no_row",)

    def test_green_not_applied_no_reasons(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", tmp_path / "absent.flag")
        gate = load_l9_readiness("2026-09-29", reader=self._reader([self._row(date(2026, 9, 28), "green")]))
        assert gate.applied is False
        assert gate.cap == 1.0
        assert gate.degraded_reasons == ()
        assert gate.lag_days == 1

    def test_yellow_applies_cap(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", tmp_path / "absent.flag")
        gate = load_l9_readiness("2026-09-29", reader=self._reader([self._row(date(2026, 9, 28), "yellow")]))
        assert gate.applied is True
        assert gate.cap == pytest.approx(L9_READINESS_YELLOW_CAP)
        assert gate.status == "yellow"

    def test_red_applies_cap(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", tmp_path / "absent.flag")
        gate = load_l9_readiness("2026-09-29", reader=self._reader([self._row(date(2026, 9, 28), "red")]))
        assert gate.applied is True
        assert gate.cap == pytest.approx(L9_READINESS_RED_CAP)

    def test_stale_row_skipped_with_reason(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", tmp_path / "absent.flag")
        stale = date(2026, 9, 29) - timedelta(days=ai.L9_READINESS_STALE_DAYS + 2)
        gate = load_l9_readiness("2026-09-29", reader=self._reader([self._row(stale, "green")]))
        assert gate.applied is False
        assert any(r.startswith("stale:") for r in gate.degraded_reasons)

    def test_unparsable_status_degraded(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", tmp_path / "absent.flag")
        gate = load_l9_readiness("2026-09-29", reader=self._reader([self._row(date(2026, 9, 28), "banana")]))
        assert gate.applied is False
        assert any("status" in r for r in gate.degraded_reasons)

    def test_tuple_row_supported(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """DatabaseService execute 位置 tuple 形态（anchored tuple-poison 同款兼容）。"""
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "L9_READINESS_DISABLE_FLAG", tmp_path / "absent.flag")
        rows = [(date(2026, 9, 28), "red", "2026-09-28 08:00:00")]
        gate = load_l9_readiness("2026-09-29", reader=self._reader(rows))
        assert gate.applied is True
        assert gate.cap == pytest.approx(L9_READINESS_RED_CAP)

    def test_sql_is_pit_bounded(self) -> None:
        """SQL 必须带 trade_date <= 边界（禁未来函数）与 ingest_ts tiebreaker。"""
        from zephyr.pf_alloc.allocation_inputs import SQL_LATEST_L9_AGG

        assert "trade_date <= '{date}'" in SQL_LATEST_L9_AGG
        assert "ingest_ts DESC" in SQL_LATEST_L9_AGG
        assert "source_line = 'AGG'" in SQL_LATEST_L9_AGG

    def test_stale_days_constant_matches_daily_edge(self) -> None:
        """边 frequency=daily（latency_budget=T-1 08:00）——陈旧窗必须是紧的小窗。"""
        assert 0 < L9_READINESS_STALE_DAYS <= 7


class TestPortfolioLayerL9ReadinessTrim:
    """组合层 L9_READINESS_CAP 裁剪：只减不加、与锚定 cap 并存取更紧、留痕可归因。"""

    @staticmethod
    def _facts(l9_readiness_cap: float | None = None, anchored_cap: float | None = None):
        from zephyr.pf_alloc.allocation_orchestrator import _LayerFacts

        return _LayerFacts(
            sleeve_cap=0.25,
            total_cap=1.0,
            sum_effective=1.0,
            symbol_aggregate={},
            freeze={},
            retain={},
            calendar_block_new=False,
            calendar_cap_adjustment=0.0,
            is_crisis=False,
            anchored_cap=anchored_cap,
            l9_readiness_cap=l9_readiness_cap,
        )

    @staticmethod
    def _request(weight: float):
        from zephyr.position.core.position_adjudication_center import (
            AdjudicationRequest,
            IntendedAction,
        )

        return AdjudicationRequest(
            request_id="t-1",
            strategy_id="s1",
            symbol="000001",
            action=IntendedAction.OPEN,
            intended_weight=weight,
            context={},
        )

    def _run(self, facts):
        from zephyr.pf_alloc.allocation_orchestrator import _portfolio_layer

        return _portfolio_layer(facts)(self._request(0.6))

    def test_cap_trims_and_tags(self) -> None:
        verdict = self._run(self._facts(l9_readiness_cap=0.7))
        assert "L9_READINESS_CAP" in verdict.violations
        # 先 sleeve_cap（0.6×0.25=0.15），再 L9 cap（sum_effective=1.0 > 0.7 → ×0.7）= 0.105
        assert verdict.adjusted_weight == pytest.approx(0.105)
        assert "L9" in verdict.reason

    def test_no_cap_when_absent(self) -> None:
        verdict = self._run(self._facts())
        assert "L9_READINESS_CAP" not in verdict.violations

    def test_no_trim_when_under_cap(self) -> None:
        verdict = self._run(self._facts(l9_readiness_cap=1.0))
        assert "L9_READINESS_CAP" not in verdict.violations

    def test_both_gates_min_semantics(self) -> None:
        """锚定 cap 与 L9 cap 并存：串联乘缩（各自只减不加），两处留痕齐备。"""
        verdict = self._run(self._facts(l9_readiness_cap=0.9, anchored_cap=0.5))
        assert "ANCHORED_CAP" in verdict.violations
        assert "L9_READINESS_CAP" in verdict.violations
        # sleeve(0.6×0.25=0.15) → anchored ×0.5 = 0.075 → L9 ×0.9 = 0.0675
        assert verdict.adjusted_weight == pytest.approx(0.0675)
