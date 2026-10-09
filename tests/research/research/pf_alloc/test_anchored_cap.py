"""锚定态熔断上限测试（AGG 消费切换终批，st-tdm20-20260923）。

映射数字=agg-switch-design §2 Owner 2026-09-14 签字：
cap(vol_pct) = 1.0 − 0.70 × clamp((vol_pct − 0.30) / (1.00 − 0.30), 0, 1)
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from zephyr.pf_alloc.allocation_inputs import (
    ANCHORED_CAP_FULL,
    ANCHORED_CAP_MAX_REDUCTION,
    ANCHORED_CAP_START,
    anchored_cap_enabled,
    anchored_cap_from_vol_pct,
    load_anchored_cap,
)


class TestCapCurve:
    """连续灰度曲线边界（禁档位跳变，方案A v2 定稿）。"""

    def test_no_cap_zone(self) -> None:
        assert anchored_cap_from_vol_pct(0.0) == 1.0
        assert anchored_cap_from_vol_pct(ANCHORED_CAP_START) == 1.0

    def test_midpoint_linear(self) -> None:
        # 0.65 = 起控/满压中点 → 1 − 0.70×0.5 = 0.65
        mid = (ANCHORED_CAP_START + ANCHORED_CAP_FULL) / 2
        assert anchored_cap_from_vol_pct(mid) == pytest.approx(1.0 - ANCHORED_CAP_MAX_REDUCTION / 2)

    def test_full_pressure_clamp(self) -> None:
        assert anchored_cap_from_vol_pct(ANCHORED_CAP_FULL) == pytest.approx(0.30)
        assert anchored_cap_from_vol_pct(1.50) == pytest.approx(0.30)  # 越界 clamp 到底

    def test_nonfinite_fail_open_to_no_cap(self) -> None:
        assert anchored_cap_from_vol_pct(float("nan")) == 1.0


class TestLoadAnchoredCap:
    """PIT 装载三态：旁路/无行/陈旧 → applied=False 留痕；正常行 → cap 施加。"""

    @staticmethod
    def _reader(rows: list[dict]):
        return lambda sql: rows

    def test_disabled_flag_bypasses(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        flag = tmp_path / "anchored_cap.disabled"
        flag.write_text("", encoding="utf-8")
        monkeypatch.setattr(ai, "ANCHORED_DISABLE_FLAG", flag)
        assert not anchored_cap_enabled()
        cap = load_anchored_cap(
            "2026-09-23", reader=self._reader([{"trade_date": date(2026, 9, 22), "dominant": "r3", "vol_pct": 0.24}])
        )
        assert cap.applied is False
        assert cap.degraded_reasons == ("disabled_flag",)

    def test_enabled_when_no_flag(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "ANCHORED_DISABLE_FLAG", tmp_path / "absent.flag")
        assert anchored_cap_enabled()

    def test_no_row_fail_disclosed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "ANCHORED_DISABLE_FLAG", tmp_path / "absent.flag")
        cap = load_anchored_cap("2026-09-23", reader=self._reader([]))
        assert cap.applied is False
        assert cap.degraded_reasons == ("no_row",)

    def test_fresh_row_applies_cap(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "ANCHORED_DISABLE_FLAG", tmp_path / "absent.flag")
        rows = [{"trade_date": date(2026, 9, 22), "dominant": "r3", "vol_pct": 0.24}]
        cap = load_anchored_cap("2026-09-23", reader=self._reader(rows))
        assert cap.applied is True
        assert cap.dominant == "r3"
        assert cap.cap == pytest.approx(anchored_cap_from_vol_pct(0.24))
        assert cap.lag_days == 1

    def test_stale_row_skipped_with_reason(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "ANCHORED_DISABLE_FLAG", tmp_path / "absent.flag")
        stale = date(2026, 9, 23) - timedelta(days=ai.ANCHORED_STALE_DAYS + 3)
        rows = [{"trade_date": stale, "dominant": "r4", "vol_pct": 0.9}]
        cap = load_anchored_cap("2026-09-23", reader=self._reader(rows))
        assert cap.applied is False
        assert any(r.startswith("stale:") for r in cap.degraded_reasons)

    def test_missing_vol_pct_degraded(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from zephyr.pf_alloc import allocation_inputs as ai

        monkeypatch.setattr(ai, "ANCHORED_DISABLE_FLAG", tmp_path / "absent.flag")
        rows = [{"trade_date": date(2026, 9, 22), "dominant": "r2", "vol_pct": None}]
        cap = load_anchored_cap("2026-09-23", reader=self._reader(rows))
        assert cap.applied is False
        assert any("vol_pct" in r for r in cap.degraded_reasons)


class TestPortfolioLayerAnchoredCapTrim:
    """组合层 ANCHORED_CAP 裁剪：只减不加、min 语义、留痕可归因。"""

    @staticmethod
    def _facts(anchored_cap: float | None):
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
        verdict = self._run(self._facts(anchored_cap=0.5))
        assert "ANCHORED_CAP" in verdict.violations
        # 先 sleeve_cap 裁剪（0.6×0.25=0.15），再锚定 cap（sum_effective=1.0 > 0.5 → ×0.5）= 0.075
        assert verdict.adjusted_weight == pytest.approx(0.075)

    def test_no_cap_when_absent(self) -> None:
        verdict = self._run(self._facts(anchored_cap=None))
        assert "ANCHORED_CAP" not in verdict.violations

    def test_no_trim_when_under_cap(self) -> None:
        # sum_effective=1.0 ≤ cap → 不约束（上限只在总暴露想突破时才约束）
        verdict = self._run(self._facts(anchored_cap=1.0))
        assert "ANCHORED_CAP" not in verdict.violations
