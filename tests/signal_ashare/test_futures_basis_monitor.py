"""MOD-SIG-058 期指基差情绪监测器 单元测试（44号备忘录 §9.8 通道2）"""

import json
from dataclasses import asdict
from datetime import date, datetime, timedelta

import pytest

from zephyr.signal_ashare import futures_basis_monitor as mod
from zephyr.signal_ashare.futures_basis_monitor import (
    FuturesBasisSnapshot,
    compute_futures_basis,
)

TS = datetime(2026, 8, 18, 10, 30)  # 周二盘中
TRADE_DATE = date(2026, 8, 18)


def _biz_days(end: date, n: int) -> list[date]:
    """向前生成 n 个工作日（含 end），升序。"""
    days: list[date] = []
    cur = end
    while len(days) < n:
        if cur.weekday() < 5:
            days.append(cur)
        cur -= timedelta(days=1)
    return sorted(days)


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 路由返回合成行（不触库）。"""

    def __init__(self, spot_quote=None, fut_qmt=None, fut_daily=None, spot_daily=None, position=None, events=None, fail=()):
        self._spot_quote = spot_quote or []
        self._fut_qmt = fut_qmt or []
        self._fut_daily = fut_daily or []
        self._spot_daily = spot_daily or []
        self._position = position or []
        self._events = events or []
        self._fail = tuple(fail)

    def execute(self, sql, params=None):
        for key in self._fail:
            if key in sql:
                raise RuntimeError(f"boom:{key}")
        if "index_quote" in sql:
            return list(self._spot_quote)
        if "futures_kline_qmt" in sql:
            return list(self._fut_qmt)
        if "kline_futures" in sql:
            return list(self._fut_daily)
        if "kline_index" in sql:
            return list(self._spot_daily)
        if "futures_position" in sql:
            return list(self._position)
        if "calendar_event" in sql:
            return list(self._events)
        return []


def _hist_days(n: int = 21) -> list[date]:
    """TRADE_DATE 之前 n 个工作日（不含当日）。"""
    return _biz_days(TRADE_DATE - timedelta(days=1), n)


def _fut_daily_rows(symbol: str, days: list[date], base: float, wiggle: float = 0.5) -> list[tuple]:
    """合成 kline_futures 日频行：(trade_date, symbol, close, volume)。"""
    return [(d, symbol, base + (i % 3) * wiggle, 1000 + i) for i, d in enumerate(days)]


def _spot_daily_rows(symbol: str, days: list[date], base: float) -> list[tuple]:
    """合成 kline_index 日频行：(trade_date, close)。"""
    return [(d, base) for d in days]


def _flat_basis_client(product: str = "IM") -> _FakeCH:
    """常态贴水小幅波动的合成场景（σ 小、无告警）。"""
    days = _hist_days()
    prefix = product
    spot_base = 7000.0
    fut_base = spot_base * 0.9985  # 常态小幅贴水
    return _FakeCH(
        spot_quote=[("2026-08-18 10:29:57", spot_base)],
        fut_qmt=[(f"{prefix}2609.CFFEX", fut_base + 1.0, 5000)],
        fut_daily=_fut_daily_rows(f"{prefix}2608", days, fut_base),
        spot_daily=_spot_daily_rows("000852", days, spot_base),
        position=[(days[-1], f"{prefix}2608", 10000, 9000)],
    )


# ---------- 贴水急扩触发（A1） ----------


def test_discount_alert_triggered_on_rapid_widening() -> None:
    """贴水急扩：basis_vel < -1.5σ_20d → discount_alert=True（机构对冲避险急增）。"""
    days = _hist_days()
    spot_base = 7000.0
    fut_base = spot_base * 0.9985
    # 今日期货盘中暴跌 → 基差从 -0.15% 急扩至 -1.43%
    client = _FakeCH(
        spot_quote=[("2026-08-18 10:29:57", spot_base)],
        fut_qmt=[("IM2609.CFFEX", spot_base * 0.985, 8000)],
        fut_daily=_fut_daily_rows("IM2608", days, fut_base),
        spot_daily=_spot_daily_rows("000852", days, spot_base),
        position=[(days[-1], "IM2608", 10000, 9000)] * 6,
    )
    snap = compute_futures_basis(ts=TS, ch_client=client, config=_im_only_config())
    assert snap.degraded is False
    im = snap.per_symbol["IM"]
    assert im.basis_rate == pytest.approx(-0.015, abs=1e-6)
    assert im.basis_vel_30m is not None and im.basis_vel_30m < 0
    assert im.sigma_20d is not None
    assert im.basis_vel_30m < -1.5 * im.sigma_20d
    assert im.discount_alert is True


def test_no_alert_when_basis_stable() -> None:
    """常态小幅贴水波动 → 不触发告警。"""
    snap = compute_futures_basis(ts=TS, ch_client=_flat_basis_client(), config=_im_only_config())
    im = snap.per_symbol["IM"]
    assert im.discount_alert is False
    assert im.basis_vel_30m is not None


def test_sigma_insufficient_samples_no_alert() -> None:
    """σ_20d 样本不足（<5 个差分）→ 不定性不出告警（噪声护栏）。"""
    days = _hist_days(3)  # 仅 3 天历史
    spot_base = 7000.0
    client = _FakeCH(
        spot_quote=[("2026-08-18 10:29:57", spot_base)],
        fut_qmt=[("IM2609.CFFEX", spot_base * 0.985, 8000)],
        fut_daily=_fut_daily_rows("IM2608", days, spot_base * 0.9985),
        spot_daily=_spot_daily_rows("000852", days, spot_base),
    )
    snap = compute_futures_basis(ts=TS, ch_client=client, config=_im_only_config())
    im = snap.per_symbol["IM"]
    assert im.sigma_20d is None
    assert im.discount_alert is False
    assert any("σ_20d 样本不足" in n for n in im.notes)


# ---------- 交割周降权（A2） ----------


def test_delivery_week_downweight() -> None:
    """futures_delivery 当周 → delivery_week=True，applied_weight=0.5。"""
    client = _flat_basis_client()
    client._events = [(date(2026, 8, 21),)]  # 本周五交割（08-18 周二同周）
    snap = compute_futures_basis(ts=TS, ch_client=client, config=_im_only_config())
    assert snap.delivery_week is True
    assert snap.applied_weight == pytest.approx(0.5)
    assert any("交割周" in n for n in snap.notes)


def test_no_delivery_event_full_weight() -> None:
    """非交割周 → applied_weight=1.0。"""
    snap = compute_futures_basis(ts=TS, ch_client=_flat_basis_client(), config=_im_only_config())
    assert snap.delivery_week is False
    assert snap.applied_weight == pytest.approx(1.0)


def test_delivery_query_failure_fail_open() -> None:
    """calendar_event 查询失败 → fail-open 不降权+留痕。"""
    client = _flat_basis_client()
    client._fail = ("calendar_event",)
    snap = compute_futures_basis(ts=TS, ch_client=client, config=_im_only_config())
    assert snap.delivery_week is False
    assert snap.applied_weight == pytest.approx(1.0)
    assert any("calendar_event" in n and "fail-open" in n for n in snap.notes)


# ---------- 持仓确认与打折（A3） ----------


def _alert_client(position_rows) -> _FakeCH:
    """贴水急扩场景 + 可定制持仓行。"""
    days = _hist_days()
    spot_base = 7000.0
    return _FakeCH(
        spot_quote=[("2026-08-18 10:29:57", spot_base)],
        fut_qmt=[("IM2609.CFFEX", spot_base * 0.985, 8000)],
        fut_daily=_fut_daily_rows("IM2608", days, spot_base * 0.9985),
        spot_daily=_spot_daily_rows("000852", days, spot_base),
        position=position_rows,
    )


def test_position_surge_confirms_alert() -> None:
    """告警 + 持仓同步激增(>10%) → confirm_flag=True（真对冲），信号不打折。"""
    days = _hist_days(6)
    rows = [(d, "IM2608", 10000, 9000) for d in days[:-1]]  # 前 5 日总持仓 19000
    rows.append((days[-1], "IM2608", 14000, 12000))  # 最新日 26000，激增 36.8%
    snap = compute_futures_basis(ts=TS, ch_client=_alert_client(rows), config=_im_only_config())
    im = snap.per_symbol["IM"]
    assert im.discount_alert is True
    assert im.confirm_flag is True
    assert im.signal_weight == pytest.approx(1.0)
    assert im.position_surge_pct == pytest.approx(26000 / 19000 - 1, abs=1e-6)


def test_position_flat_discounts_alert() -> None:
    """告警 + 持仓平稳 → confirm_flag=False，signal_weight×0.5（或为期指单边投机）。"""
    days = _hist_days(6)
    rows = [(d, "IM2608", 10000, 9000) for d in days]  # 全程平稳
    snap = compute_futures_basis(ts=TS, ch_client=_alert_client(rows), config=_im_only_config())
    im = snap.per_symbol["IM"]
    assert im.discount_alert is True
    assert im.confirm_flag is False
    assert im.signal_weight == pytest.approx(0.5)
    assert any("信号打折" in n for n in im.notes)


def test_position_unavailable_no_discount() -> None:
    """持仓数据不可用 → confirm_flag=None，告警不打折（fail-open）。"""
    snap = compute_futures_basis(ts=TS, ch_client=_alert_client([]), config=_im_only_config())
    im = snap.per_symbol["IM"]
    assert im.discount_alert is True
    assert im.confirm_flag is None
    assert im.signal_weight == pytest.approx(1.0)


# ---------- 降级链（A4） ----------


def test_minute_leg_missing_degrades_to_daily() -> None:
    """期货分钟腿缺失 → 降级 kline_futures 日频腿 + per-symbol degraded 标注。"""
    days = _hist_days()
    spot_base = 7000.0
    fut_base = spot_base * 0.9985
    client = _FakeCH(
        spot_quote=[("2026-08-18 10:29:57", spot_base)],
        fut_qmt=[],  # 分钟腿空
        fut_daily=_fut_daily_rows("IM2608", days + [TRADE_DATE], fut_base),
        spot_daily=_spot_daily_rows("000852", days, spot_base),
    )
    snap = compute_futures_basis(ts=TS, ch_client=client, config=_im_only_config())
    assert snap.degraded is False
    im = snap.per_symbol["IM"]
    assert im.futures_leg == "kline_futures_daily"
    assert im.spot_leg == "index_quote_intraday"
    assert im.degraded is True
    assert im.basis_rate is not None
    assert any("期货分钟腿缺失" in n for n in im.notes)


def test_spot_intraday_missing_degrades_to_daily() -> None:
    """现货盘中腿缺失 → 降级 kline_index 日收 + degraded 标注。"""
    days = _hist_days()
    spot_base = 7000.0
    client = _FakeCH(
        spot_quote=[],
        fut_qmt=[("IM2609.CFFEX", spot_base * 0.9985, 5000)],
        fut_daily=_fut_daily_rows("IM2608", days, spot_base * 0.9985),
        spot_daily=_spot_daily_rows("000852", days + [TRADE_DATE], spot_base),
    )
    snap = compute_futures_basis(ts=TS, ch_client=client, config=_im_only_config())
    im = snap.per_symbol["IM"]
    assert im.spot_leg == "kline_index_daily"
    assert im.degraded is True


def test_both_legs_missing_snapshot_degraded() -> None:
    """两腿皆无 → snapshot degraded=True 空结果不炸。"""
    snap = compute_futures_basis(ts=TS, ch_client=_FakeCH(), config=_im_only_config())
    assert snap.degraded is True
    assert snap.per_symbol == {}
    assert snap.notes


def test_client_unavailable_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    """ch_client 未注入且默认客户端不可用 → degraded=True（显式模拟不可用，不依赖环境 CH 在线状态）。"""
    monkeypatch.setattr(mod, "_default_client", lambda: None)
    snap = compute_futures_basis(ts=TS, ch_client=None, config=_im_only_config())
    assert snap.degraded is True
    assert snap.per_symbol == {}


def test_query_exception_per_leg_fail_open() -> None:
    """单腿查询异常不阻塞其余腿：期货腿异常→日频兜底仍出结果。"""
    days = _hist_days()
    spot_base = 7000.0
    client = _FakeCH(
        spot_quote=[("2026-08-18 10:29:57", spot_base)],
        fut_daily=_fut_daily_rows("IM2608", days + [TRADE_DATE], spot_base * 0.9985),
        spot_daily=_spot_daily_rows("000852", days, spot_base),
        fail=("futures_kline_qmt",),
    )
    snap = compute_futures_basis(ts=TS, ch_client=client, config=_im_only_config())
    assert snap.degraded is False
    im = snap.per_symbol["IM"]
    assert im.futures_leg == "kline_futures_daily"
    assert any("fail-open" in n for n in im.notes)


def test_invalid_ts_raises() -> None:
    """ts 格式非法 → ValueError（fail-closed 契约）。"""
    with pytest.raises(ValueError):
        compute_futures_basis(ts="2026/08/18", ch_client=_FakeCH(), config=_im_only_config())


# ---------- 四品种映射 ----------


def _im_only_config() -> mod.FuturesBasisConfig:
    """单品种配置（多数用例只看 IM，缩小合成数据面）。"""
    return mod.FuturesBasisConfig(products=(mod.DEFAULT_PRODUCTS[2],))


def test_four_product_mapping() -> None:
    """四品种 IF/IC/IM/IH → 沪深300/中证500/中证1000/上证50 映射齐全且各自出结果。"""
    days = _hist_days()
    spot_quote, fut_qmt, fut_daily, spot_daily = [], [], [], []
    for p in mod.DEFAULT_PRODUCTS:
        spot_quote.append(("2026-08-18 10:29:57", 4000.0))
        fut_qmt.append((f"{p.product}2609.CFFEX", 4000.0 * 0.998, 5000))
        fut_daily.extend(_fut_daily_rows(f"{p.product}2608", days, 4000.0 * 0.9985))
        spot_daily.extend(_spot_daily_rows(p.kline_symbols[0], days, 4000.0))
    # index_quote 按 symbol 过滤语义在 fake 中简化——逐品种返回同一批行不影响断言语义
    client = _FakeCH(spot_quote=spot_quote, fut_qmt=fut_qmt, fut_daily=fut_daily, spot_daily=spot_daily)
    snap = compute_futures_basis(ts=TS, ch_client=client)
    assert set(snap.per_symbol) == {"IF", "IC", "IM", "IH"}
    names = {p.product: p.spot_name for p in mod.DEFAULT_PRODUCTS}
    assert names == {"IF": "沪深300", "IC": "中证500", "IM": "中证1000", "IH": "上证50"}
    assert "打板" in snap.per_symbol["IM"].sensitivity
    assert "大盘蓝筹" in snap.per_symbol["IF"].sensitivity


# ---------- 输出契约 ----------


def test_snapshot_json_serializable() -> None:
    """frozen dataclass asdict JSON 可序列化（prediction_log 预留）。"""
    snap = compute_futures_basis(ts=TS, ch_client=_flat_basis_client(), config=_im_only_config())
    payload = json.dumps(asdict(snap), ensure_ascii=False)
    assert "IM" in payload
    assert isinstance(snap, FuturesBasisSnapshot)
    assert snap.ts == "2026-08-18 10:30:00"
    assert snap.trade_date == "2026-08-18"
