# [BLUEPRINT] MOD-SIG-079 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-20 行）
# [MODULE] tests.signal_ashare.test_sector_volume_anomaly
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sector_volume_anomaly
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网（ch_client 鸭子类型 SQL 子串路由）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=板块量能异动检测逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-079_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-079 板块量能异动检测 单元测试（GAP-F-20，合成数据不触库）。

覆盖：偏离度=当日/N 日均值口径、五档标签封闭（显著放量/温和放量/正常/温和缩量/
显著缩量）、z-score（std=0 → None）、PIT（>trade_date 点剔除）、历史不足跳过留痕、
当日缺量跳过留痕、零均值守卫、排序与 top_n、日期校验 fail-closed、
主入口降级链、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.signal_ashare.sector_volume_anomaly import (
    LABEL_MILD_SHRINK,
    LABEL_MILD_SPIKE,
    LABEL_NORMAL,
    LABEL_SPIKE,
    LABEL_STRONG_SHRINK,
    SectorAmountSeries,
    VolumeAnomalyConfig,
    detect_volume_anomaly,
    run_sector_volume_anomaly,
)


def _series(code: str, amounts: list[float], start_day: int = 1) -> SectorAmountSeries:
    pts = tuple((f"2026-08-{d:02d}", a) for d, a in zip(range(start_day, start_day + len(amounts)), amounts))
    return SectorAmountSeries(sector_code=code, sector_name=f"板块{code}", points=pts)


def _cfg(**kw) -> VolumeAnomalyConfig:
    return VolumeAnomalyConfig(**kw)


BASE = [100.0] * 20  # 20 日平稳量


def test_spike_label() -> None:
    s = _series("880001", BASE + [250.0])  # 2.5× → +150% ≥ +100% 显著放量
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    assert rep.items[0].label == LABEL_SPIKE
    assert rep.items[0].deviation_pct == pytest.approx(150.0)
    assert rep.items[0].ma_n == pytest.approx(100.0)
    assert rep.label_counts[LABEL_SPIKE] == 1


def test_mild_spike_label() -> None:
    s = _series("880001", BASE + [140.0])  # +40%
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    assert rep.items[0].label == LABEL_MILD_SPIKE


def test_normal_label() -> None:
    s = _series("880001", BASE + [110.0])  # +10%
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    assert rep.items[0].label == LABEL_NORMAL


def test_shrink_labels() -> None:
    s1 = _series("880001", BASE + [60.0])   # -40% 温和缩量
    s2 = _series("880002", BASE + [30.0])   # -70% 显著缩量
    rep = detect_volume_anomaly({"880001": s1, "880002": s2}, trade_date="2026-08-21", config=_cfg())
    labels = {i.sector_code: i.label for i in rep.items}
    assert labels["880001"] == LABEL_MILD_SHRINK
    assert labels["880002"] == LABEL_STRONG_SHRINK


def test_zscore_none_when_std_zero() -> None:
    s = _series("880001", BASE + [150.0])  # 历史 std=0
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    assert rep.items[0].zscore is None


def test_zscore_computed_when_std_positive() -> None:
    hist = [90.0, 110.0] * 10
    s = _series("880001", hist + [200.0])
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    assert rep.items[0].zscore is not None
    assert rep.items[0].zscore > 0


def test_pit_excludes_future_points() -> None:
    pts = tuple((f"2026-08-{d:02d}", 100.0) for d in range(1, 22)) + (("2026-08-22", 999.0),)
    s = SectorAmountSeries(sector_code="880001", sector_name="x", points=pts)
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    assert rep.items[0].amount_today == pytest.approx(100.0)


def test_insufficient_history_skipped() -> None:
    s = _series("880001", [100.0] * 3 + [200.0])  # 历史仅 3 < min_history=5
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-04", config=_cfg())
    assert rep.items == []
    assert any("历史不足" in n for n in rep.notes)


def test_missing_today_amount_skipped() -> None:
    s = _series("880001", BASE)  # 无 2026-08-21 当日点
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    assert rep.items == []
    assert any("当日成交额缺失" in n for n in rep.notes)


def test_zero_ma_guard() -> None:
    s = _series("880001", [0.0] * 20 + [100.0])
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    assert rep.items == []
    assert any("均值为 0" in n for n in rep.notes)


def test_sorted_by_deviation_desc_and_topn() -> None:
    series = {
        "880001": _series("880001", BASE + [300.0]),
        "880002": _series("880002", BASE + [150.0]),
        "880003": _series("880003", BASE + [50.0]),
    }
    rep = detect_volume_anomaly(series, trade_date="2026-08-21", config=_cfg(top_n=2))
    assert [i.sector_code for i in rep.items] == ["880001", "880002"]
    assert rep.total_sectors == 3


def test_invalid_trade_date_fail_closed() -> None:
    with pytest.raises(ValueError, match="trade_date"):
        detect_volume_anomaly({}, trade_date="2026-13-01", config=_cfg())


def test_invalid_series_type_fail_closed() -> None:
    with pytest.raises(ValueError, match="series_map 元素非法"):
        detect_volume_anomaly({"x": [1, 2]}, trade_date="2026-08-21", config=_cfg())  # type: ignore[dict-item]


def test_all_skipped_degraded() -> None:
    s = _series("880001", [100.0] * 3 + [200.0])
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-04", config=_cfg())
    assert rep.degraded is True


def test_json_serializable() -> None:
    s = _series("880001", BASE + [250.0])
    rep = detect_volume_anomaly({"880001": s}, trade_date="2026-08-21", config=_cfg())
    json.dumps(asdict(rep), ensure_ascii=False)


# ------------------------------------------------------------------
# 主入口（假 ch_client）
# ------------------------------------------------------------------


class _FakeClient:
    def execute(self, sql, params=None):
        assert "kline_sector_880" in sql
        return [
            ("880001.SH", "半导体", f"2026-08-{d:02d}", 100.0) for d in range(1, 21)
        ] + [("880001.SH", "半导体", "2026-08-21", 250.0)]


def test_run_main_entry() -> None:
    rep = run_sector_volume_anomaly(
        trade_date="2026-08-21", ch_client=_FakeClient(), config=_cfg()
    )
    assert rep.degraded is False
    assert rep.items[0].label == LABEL_SPIKE


def test_run_query_failure_degraded() -> None:
    class _Bad:
        def execute(self, sql, params=None):
            raise RuntimeError("boom")

    rep = run_sector_volume_anomaly(trade_date="2026-08-21", ch_client=_Bad(), config=_cfg())
    assert rep.degraded is True
    assert any("kline_sector_880" in n for n in rep.notes)
