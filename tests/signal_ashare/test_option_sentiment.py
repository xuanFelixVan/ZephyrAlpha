"""MOD-SIG-059 期权情绪三件套 单元测试（44号备忘录 §9.9，合成 IV 表面不触库）"""

import json
import sys
from dataclasses import asdict
from datetime import date, timedelta

import pytest

from zephyr.signal_ashare import option_sentiment as mod
from zephyr.signal_ashare.option_sentiment import (
    OptionSentimentResult,
    compute_option_sentiment,
)

TRADE_DATE = date(2026, 8, 20)
UNDERLYING = "510300.SH"


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 特征路由返回合成行（不触库）。"""

    def __init__(
        self, iv_rows=None, volume_rows=None, map_rows=None, greeks_rows=None, expiry_hits=None, latest=None, exc=None
    ):
        self._iv = iv_rows or []
        self._vol = volume_rows or []
        self._map = map_rows or []
        self._greeks = greeks_rows or []
        self._expiry_hits = expiry_hits if expiry_hits is not None else [(0,)]
        self._latest = latest
        self._exc = exc

    def execute(self, sql, params=None):
        if self._exc is not None:
            raise self._exc
        if "max(trade_date)" in sql:
            return list(self._latest) if self._latest is not None else [(TRADE_DATE,)]
        if "calendar_event" in sql:
            return list(self._expiry_hits)
        if "option_kline" in sql:
            return list(self._vol)
        if "option_greeks" in sql:
            return list(self._greeks)
        if "GROUP BY symbol" in sql:
            return list(self._map)
        return list(self._iv)  # option_iv_surface 历史窗


def _iv(d: date, symbol: str, strike: float, iv: float, option_type: str, expiry: date | None = None) -> tuple:
    """合成 option_iv_surface 行（列序对齐模块 SQL）。"""
    return (d, symbol, strike, expiry or (d + timedelta(days=30)), iv, option_type)


def _vol(d: date, symbol: str, volume: float) -> tuple:
    """合成 option_kline 行。"""
    return (d, symbol, volume)


def _greeks(d: date, symbol: str, delta: float, expiry: date | None = None) -> tuple:
    """合成 option_greeks 行。"""
    return (d, symbol, expiry or (d + timedelta(days=30)), delta)


def _days(n: int, end: date = TRADE_DATE) -> list[date]:
    """当日在内的连续 n 个自然日（模块不过滤周末，测试从简）。"""
    return [end - timedelta(days=i) for i in range(n - 1, -1, -1)]


def _iv_window(days: list[date], iv_of: callable) -> list[tuple]:
    """逐日平值 call/put 双行（strike=4.0 唯一即中位数），IV 由 iv_of(d) 给。"""
    rows = []
    for i, d in enumerate(days):
        v = iv_of(i, d)
        rows.append(_iv(d, f"C{i:03d}", 4.0, v, "call"))
        rows.append(_iv(d, f"P{i:03d}", 4.0, v, "put"))
    return rows


# ---------- 空表 / 异常降级 ----------


def test_empty_iv_surface_degraded() -> None:
    """iv_surface 窗内无有效行 → degraded=True 空结果不炸。"""
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH())
    assert result.degraded is True
    assert result.pcr is None
    assert result.iv_rank is None
    assert result.m1_threshold_scale == 1.0
    assert result.notes


def test_query_exception_degraded() -> None:
    """主数据查询异常 → degraded=True 不抛。"""
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(exc=RuntimeError("boom")))
    assert result.degraded is True
    assert "boom" in result.notes[0]


def test_invalid_trade_date_raises() -> None:
    """trade_date 格式非法 → ValueError（调用方契约违例，fail-closed）。"""
    with pytest.raises(ValueError):
        compute_option_sentiment("2026/08/20", ch_client=_FakeCH())


def test_default_trade_date_uses_latest() -> None:
    """trade_date=None → 取主标的 iv_surface 最新数据日（PIT 数据日口径）。"""
    latest = date(2026, 8, 19)
    client = _FakeCH(
        latest=[(latest,)],
        iv_rows=[_iv(latest, "C0", 4.0, 0.20, "call"), _iv(latest, "P0", 4.0, 0.20, "put")],
    )
    result = compute_option_sentiment(None, ch_client=client)
    assert result.date == "2026-08-19"
    assert result.degraded is False


# ---------- F1 PCR 分位两端 ----------


def _pcr_dataset(days: list[date], pcr_of: callable) -> tuple[list[tuple], list[tuple], list[tuple]]:
    """每日 call/put 各一合约，vol 由目标 PCR 反推（call=100 固定）。"""
    vol_rows, map_rows, iv_rows = [], [], []
    for i, d in enumerate(days):
        csym, psym = f"KC{i:03d}", f"KP{i:03d}"
        map_rows.append((csym, UNDERLYING, "call"))
        map_rows.append((psym, UNDERLYING, "put"))
        vol_rows.append(_vol(d, csym, 100.0))
        vol_rows.append(_vol(d, psym, 100.0 * pcr_of(i, d)))
    iv_rows.append(_iv(days[-1], "C0", 4.0, 0.20, "call"))  # iv_surface 非空兜底（iv_rank 窗不足降级）
    return vol_rows, map_rows, iv_rows


def test_pcr_high_percentile_panic_bottom() -> None:
    """PCR 历史分位 >80%（当日恐慌极端）→ +1 子分 + 底部区注解。"""
    days = _days(21)
    vol, mp, iv = _pcr_dataset(days, lambda i, d: 1.0 if d < TRADE_DATE else 3.0)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, volume_rows=vol, map_rows=mp))
    assert result.degraded is False
    assert result.pcr == pytest.approx(3.0)
    assert result.pcr_basis == "volume"
    assert result.pcr_percentile == pytest.approx(1.0)
    assert result.composite_score == pytest.approx(1.0)
    assert any("恐慌过度" in a for a in result.annotation)
    assert result.divergence_warning is False


def test_pcr_low_percentile_overoptimism() -> None:
    """PCR 历史分位 <20%（当日乐观极端）→ -1 子分 + 反向风险注解。"""
    days = _days(21)
    vol, mp, iv = _pcr_dataset(days, lambda i, d: 1.0 if d < TRADE_DATE else 0.2)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, volume_rows=vol, map_rows=mp))
    assert result.pcr == pytest.approx(0.2)
    assert result.pcr_percentile < 0.20
    assert result.composite_score == pytest.approx(-1.0)
    assert any("过度乐观" in a for a in result.annotation)


def test_pcr_window_insufficient_percentile_degraded() -> None:
    """PCR 分位窗 <20 日守卫 → pcr 原值保留、pcr_percentile=None 降级留痕。"""
    days = _days(5)
    vol, mp, iv = _pcr_dataset(days, lambda i, d: 1.5)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, volume_rows=vol, map_rows=mp))
    assert result.pcr == pytest.approx(1.5)
    assert result.pcr_percentile is None
    assert any("PCR 分位窗" in n for n in result.notes)


# ---------- F2 IV Rank 窗守卫 + 跳升 ----------


def test_iv_rank_window_insufficient_degraded() -> None:
    """可用窗 <60 日（实证 ~140 交易日不足 250 标准窗口径守卫）→ iv_rank=None degraded。"""
    days = _days(30)
    iv = _iv_window(days, lambda i, d: 0.20)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv))
    assert result.degraded is False
    assert result.iv_rank is None
    assert result.iv_jump_flag is False
    assert any("IV Rank 可用窗" in n for n in result.notes)


def test_iv_rank_high_and_jump_flag() -> None:
    """IV 当日跳升 >+3σ → iv_jump_flag=True；iv_rank=序列最高分位。"""
    days = _days(61)
    iv = _iv_window(days, lambda i, d: 0.20 + (0.01 if i % 2 else 0.0) if d < TRADE_DATE else 0.35)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv))
    assert result.iv_rank == pytest.approx(1.0)
    assert result.iv_jump_flag is True
    assert any("避险急增" in a for a in result.annotation)


def test_iv_rank_low_vol_calm() -> None:
    """IV Rank <20% 低波 → 温和 +0.5 子分。"""
    days = _days(61)
    iv = _iv_window(days, lambda i, d: 0.20 + i * 0.001 if d < TRADE_DATE else 0.100)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv))
    assert result.iv_rank < 0.20
    assert any("低波温和" in a for a in result.annotation)


# ---------- F3 Skew 极端左偏 + 背离 ----------


def _skew_dataset(days: list[date], skew_of: callable) -> tuple[list[tuple], list[tuple]]:
    """逐日平值+25Δ 合约：skew_norm 由 skew_of 给（atm=0.20 固定，call25=0.20，put25=0.20+skew×0.20）。"""
    iv_rows, greeks_rows = [], []
    for i, d in enumerate(days):
        skew_norm = skew_of(i, d)
        iv_rows.append(_iv(d, f"C{i:03d}", 4.0, 0.20, "call"))
        iv_rows.append(_iv(d, f"P{i:03d}", 4.0, 0.20, "put"))
        iv_rows.append(_iv(d, f"C25_{i:03d}", 4.2, 0.20, "call"))
        iv_rows.append(_iv(d, f"P25_{i:03d}", 3.8, 0.20 + skew_norm * 0.20, "put"))
        greeks_rows.append(_greeks(d, f"C25_{i:03d}", 0.25))
        greeks_rows.append(_greeks(d, f"P25_{i:03d}", -0.25))
    return iv_rows, greeks_rows


def test_skew_extreme_left_tail() -> None:
    """归一 skew 当日极端（>90% 分位）→ skew_extreme=True + 尾部保护注解。"""
    days = _days(11)
    iv, greeks = _skew_dataset(days, lambda i, d: 0.05 if d < TRADE_DATE else 0.80)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, greeks_rows=greeks))
    assert result.skew_norm == pytest.approx(0.80)
    assert result.skew_extreme is True
    assert any("尾部保护" in a for a in result.annotation)


def test_skew_window_insufficient_extreme_degraded() -> None:
    """Skew 分位窗 <10 日守卫 → skew_norm 保留、skew_extreme=None 降级。"""
    days = _days(3)
    iv, greeks = _skew_dataset(days, lambda i, d: 0.05)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, greeks_rows=greeks))
    assert result.skew_norm == pytest.approx(0.05)
    assert result.skew_extreme is None
    assert any("Skew 分位窗" in n for n in result.notes)


def test_divergence_warning_pcr_low_x_skew_high() -> None:
    """PCR 低分位（散户乐观）× Skew 极端（机构买保护）背离 → 多空分歧最大警示。"""
    days = _days(21)
    vol, mp, _ = _pcr_dataset(days, lambda i, d: 1.0 if d < TRADE_DATE else 0.2)
    iv, greeks = _skew_dataset(days, lambda i, d: 0.05 if d < TRADE_DATE else 0.80)
    result = compute_option_sentiment(
        TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, volume_rows=vol, map_rows=mp, greeks_rows=greeks)
    )
    assert result.pcr_percentile < 0.20
    assert result.skew_extreme is True
    assert result.divergence_warning is True
    assert any("多空分歧最大" in n for n in result.notes)


def test_no_divergence_when_skew_not_extreme() -> None:
    """PCR 低分位但 Skew 非极端 → 不触发背离警示（缺一不 trigger）。"""
    days = _days(21)
    vol, mp, _ = _pcr_dataset(days, lambda i, d: 1.0 if d < TRADE_DATE else 0.2)
    iv, greeks = _skew_dataset(days, lambda i, d: 0.05)
    result = compute_option_sentiment(
        TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, volume_rows=vol, map_rows=mp, greeks_rows=greeks)
    )
    assert result.pcr_percentile < 0.20
    assert result.skew_extreme is False
    assert result.divergence_warning is False


# ---------- 到期日阈值缩放 ----------


def test_expiry_day_threshold_scale() -> None:
    """calendar_event 命中 index_option_expiry → m1_threshold_scale=0.8（防伽马挤压假情绪）。"""
    iv = [_iv(TRADE_DATE, "C0", 4.0, 0.20, "call"), _iv(TRADE_DATE, "P0", 4.0, 0.20, "put")]
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, expiry_hits=[(1,)]))
    assert result.m1_threshold_scale == pytest.approx(0.8)
    assert any("期权到期日" in n for n in result.notes)


def test_non_expiry_day_scale_one() -> None:
    """非到期日 → m1_threshold_scale=1.0。"""
    iv = [_iv(TRADE_DATE, "C0", 4.0, 0.20, "call")]
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, expiry_hits=[(0,)]))
    assert result.m1_threshold_scale == pytest.approx(1.0)


def test_calendar_event_failure_fail_open() -> None:
    """calendar_event 查询异常 → fail-open scale=1.0 留痕，主流程不阻塞（44号 §9.12）。"""

    class _FlakyCalCH(_FakeCH):
        def execute(self, sql, params=None):
            if "calendar_event" in sql:
                raise RuntimeError("calendar down")
            return super().execute(sql, params)

    iv = [_iv(TRADE_DATE, "C0", 4.0, 0.20, "call")]
    result = compute_option_sentiment(TRADE_DATE, ch_client=_FlakyCalCH(iv_rows=iv))
    assert result.degraded is False
    assert result.m1_threshold_scale == pytest.approx(1.0)
    assert any("fail-open" in n for n in result.notes)


# ---------- 契约 ----------


def test_result_json_serializable() -> None:
    """frozen dataclass asdict → JSON 可序列化（prediction_log/注解总线预留）。"""
    days = _days(21)
    vol, mp, _ = _pcr_dataset(days, lambda i, d: 1.0 if d < TRADE_DATE else 3.0)
    iv, greeks = _skew_dataset(days, lambda i, d: 0.05)
    result = compute_option_sentiment(
        TRADE_DATE, ch_client=_FakeCH(iv_rows=iv, volume_rows=vol, map_rows=mp, greeks_rows=greeks)
    )
    payload = json.dumps(asdict(result), ensure_ascii=False)
    assert "2026-08-20" in payload
    assert isinstance(result, OptionSentimentResult)
    with pytest.raises(AttributeError):  # frozen 契约
        result.pcr = 9.9  # type: ignore[misc]


def test_component_failure_isolated() -> None:
    """kline/greeks 部件查询异常独立降级：iv_surface 主数据仍出 IV 注解，不累及整单。"""

    class _PartialCH(_FakeCH):
        def execute(self, sql, params=None):
            if "option_kline" in sql or "option_greeks" in sql:
                raise RuntimeError("part down")
            return super().execute(sql, params)

    days = _days(61)
    iv = _iv_window(days, lambda i, d: 0.20 + i * 0.001)
    result = compute_option_sentiment(TRADE_DATE, ch_client=_PartialCH(iv_rows=iv))
    assert result.degraded is False
    assert result.pcr is None
    assert result.skew_norm is None
    assert result.iv_rank is not None
    assert any("PCR 降级" in n for n in result.notes)
    assert any("Skew 降级" in n for n in result.notes)
