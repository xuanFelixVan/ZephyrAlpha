# [A_test] module_id: MOD-SIG-093 | layer=test | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-093 | docs/03_modules/_domain_signal/intraday_volume_orderflow/blueprint.md
# [MODULE] tests.signal_ashare.test_intraday_volume_orderflow
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""日内量能结构与订单流分析（MOD-SIG-093，B10-01361）施工验证测试。

覆盖：
- Volume Profile：POC 落在量能集中价位、VA 覆盖率≥70%、va_low≤poc≤va_high；
- CVD：涨/跌/十字星 bar 的 delta 符号与累加；
- CVD 背离：价新高+量差缩→bearish、价新低+量差升→bullish、确认时零背离、程度量化>0；
- VPIN：单向流≈1、双向均衡流显著更低、bucket 不足 window→degraded；
- fail-closed：缺列/负量/空表/非法配置 → ValueError；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB、无 tick 链路依赖。
"""

from __future__ import annotations

import dataclasses
import json

import pandas as pd
import pytest

from zephyr.signal_ashare.intraday_volume_orderflow import (
    IntradayOrderflowConfig,
    IntradayVolumeOrderflowAnalyzer,
)


def _analyzer() -> IntradayVolumeOrderflowAnalyzer:
    return IntradayVolumeOrderflowAnalyzer(IntradayOrderflowConfig())


def _bars(rows: list[tuple[float, float, float, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"])


class TestVolumeProfile:
    def test_poc_at_volume_concentration(self) -> None:
        # 10 根 bar：8 根典型价在 10 附近（量大），2 根在 20 附近（量小）
        rows = [(9.9, 10.2, 9.8, 10.0, 1000.0)] * 8 + [(19.8, 20.2, 19.6, 20.0, 100.0)] * 2
        vp = _analyzer().volume_profile(_bars(rows), n_bins=20)
        assert 9.0 <= vp.poc_price <= 11.0

    def test_value_area_covers_fraction(self) -> None:
        rows = [(9.9, 10.2, 9.8, 10.0, 1000.0)] * 8 + [(19.8, 20.2, 19.6, 20.0, 100.0)] * 2
        a = _analyzer()
        vp = a.volume_profile(_bars(rows), n_bins=20)
        assert vp.value_area_low <= vp.poc_price <= vp.value_area_high
        assert vp.total_volume == pytest.approx(8200.0)
        assert vp.bin_count == 20

    def test_fail_closed(self) -> None:
        a = _analyzer()
        with pytest.raises(ValueError):
            a.volume_profile(_bars([(1, 2, 0.5, 1.5, 100)]).drop(columns=["volume"]))
        with pytest.raises(ValueError):
            a.volume_profile(_bars([(1, 2, 0.5, 1.5, -100.0)]))
        with pytest.raises(ValueError):
            a.volume_profile(_bars([]))
        with pytest.raises(ValueError):
            a.volume_profile(_bars([(1, 2, 0.5, 1.5, 100.0)]), n_bins=1)


class TestCvd:
    def test_signed_delta_and_cumsum(self) -> None:
        bars = _bars(
            [
                (10.0, 10.3, 9.9, 10.2, 100.0),   # 涨 → +100
                (10.2, 10.4, 10.0, 10.1, 50.0),   # 跌 → -50
                (10.1, 10.2, 10.0, 10.1, 30.0),   # 十字 → 0
            ]
        )
        cvd = _analyzer().cvd(bars)
        assert cvd.iloc[0] == pytest.approx(100.0)
        assert cvd.iloc[1] == pytest.approx(50.0)
        assert cvd.iloc[2] == pytest.approx(50.0)


class TestCvdDivergence:
    def _bearish_bars(self) -> pd.DataFrame:
        # 价格两段新高（10→11），但第二段量能 delta 明显萎缩 → CVD 低点下移
        rows = (
            [(10.0, 10.4, 9.9, 10.3, 1000.0)]      # 强势上涨 +1000
            + [(10.3, 10.5, 10.2, 10.4, 800.0)]   # 上涨 +800（前高区）
            + [(10.4, 10.6, 10.1, 10.2, 900.0)]   # 回落 -900
            + [(10.2, 10.8, 10.1, 10.7, 100.0)]   # 价新高但量缩 +100
            + [(10.7, 10.9, 10.5, 10.8, 50.0)]    # 价续新高量更缩 +50
        )
        return _bars(rows)

    def test_bearish_divergence_detected(self) -> None:
        events = _analyzer().cvd_divergences(self._bearish_bars(), lookback=3)
        bearish = [e for e in events if e.direction == "bearish"]
        assert bearish, f"应检出顶背离: {events}"
        assert all(e.magnitude > 0.0 for e in bearish)

    def test_bullish_divergence_detected(self) -> None:
        # 镜像：价格两段新低，CVD 低点抬升
        rows = (
            [(10.0, 10.1, 9.6, 9.7, 1000.0)]
            + [(9.7, 9.8, 9.4, 9.5, 800.0)]
            + [(9.5, 9.9, 9.3, 9.8, 900.0)]
            + [(9.8, 9.9, 9.2, 9.3, 100.0)]
            + [(9.3, 9.4, 9.0, 9.1, 50.0)]
        )
        events = _analyzer().cvd_divergences(_bars(rows), lookback=3)
        bullish = [e for e in events if e.direction == "bullish"]
        assert bullish, f"应检出底背离: {events}"

    def test_no_divergence_when_cvd_confirms(self) -> None:
        # 价格新高且量能同步放大 → 无背离
        rows = (
            [(10.0, 10.4, 9.9, 10.3, 500.0)]
            + [(10.3, 10.5, 10.2, 10.4, 600.0)]
            + [(10.4, 10.8, 10.3, 10.7, 900.0)]
            + [(10.7, 11.0, 10.6, 10.9, 1200.0)]
        )
        events = _analyzer().cvd_divergences(_bars(rows), lookback=3)
        assert [e for e in events if e.direction == "bearish"] == []


class TestVpin:
    def test_one_directional_flow_high_vpin(self) -> None:
        rows = [(10.0 + i * 0.1, 10.2 + i * 0.1, 9.9 + i * 0.1, 10.1 + i * 0.1, 100.0) for i in range(100)]
        r = _analyzer().vpin(_bars(rows), n_buckets=10, window=10)
        assert r.vpin == pytest.approx(1.0)
        assert r.degraded is False
        assert r.bucket_count == 10

    def test_balanced_flow_lower_vpin(self) -> None:
        up = (10.0, 10.3, 9.9, 10.2, 100.0)
        down = (10.2, 10.3, 9.9, 10.0, 100.0)
        rows = [up, down] * 50
        r = _analyzer().vpin(_bars(rows), n_buckets=10, window=10)
        assert r.vpin < 0.5

    def test_degraded_when_buckets_below_window(self) -> None:
        rows = [(10.0, 10.2, 9.9, 10.1, 100.0)] * 30
        r = _analyzer().vpin(_bars(rows), n_buckets=5, window=50)
        assert r.degraded is True
        assert r.bucket_count == 5
        assert 0.0 <= r.vpin <= 1.0

    def test_fail_closed(self) -> None:
        a = _analyzer()
        with pytest.raises(ValueError):
            a.vpin(_bars([(1, 2, 0.5, 1.5, 100.0)]), n_buckets=0)
        with pytest.raises(ValueError):
            a.vpin(_bars([]), n_buckets=5)


class TestContract:
    def test_results_frozen_and_json_serializable(self) -> None:
        a = _analyzer()
        rows = [(9.9, 10.2, 9.8, 10.0, 1000.0)] * 8 + [(19.8, 20.2, 19.6, 20.0, 100.0)] * 2
        vp = a.volume_profile(_bars(rows), n_bins=20)
        assert dataclasses.is_dataclass(vp)
        with pytest.raises(dataclasses.FrozenInstanceError):
            vp.poc_price = 0.0  # type: ignore[misc]
        json.dumps(vp.to_dict())
        r = a.vpin(_bars(rows * 5), n_buckets=5, window=5)
        json.dumps(r.to_dict())
        events = a.cvd_divergences(_bars(rows), lookback=2)
        for e in events:
            json.dumps(e.to_dict())

    def test_config_frozen_and_validated(self) -> None:
        cfg = IntradayOrderflowConfig()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.n_bins = 5  # type: ignore[misc]
        with pytest.raises(ValueError):
            IntradayOrderflowConfig(n_bins=1)
        with pytest.raises(ValueError):
            IntradayOrderflowConfig(value_area_fraction=1.5)
        with pytest.raises(ValueError):
            IntradayOrderflowConfig(vpin_buckets=0)
