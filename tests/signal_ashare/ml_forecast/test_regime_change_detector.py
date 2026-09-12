"""regime 变更检测器 单元测试（10 号 regime spec §2.1 BM-BUY-02-A-1-d，MOD-SIG-039）"""

import pytest

from zephyr.signal_ashare.regime_change_detector import (
    ChangePhase,
    MarketRegime,
    RegimeChangeConfig,
    RegimeChangeDataError,
    RegimeChangeDetector,
    build_regime_series,
    classify_regime,
    cusum_level,
    detect_regime_change,
)


def _bull_closes(n: int = 400) -> list[float]:
    """稳定慢牛：100 起每日 +0.2%"""
    return [100.0 * 1.002**i for i in range(n)]


def _bull_then_crash(crash_days: int, crash_daily: float = 0.05, bull_days: int = 400) -> list[float]:
    """慢牛后接快速下跌（默认每日 -5%），用于制造牛熊翻转。

    5% 急跌下：crash 第 1 天仍在 MA60 上方（BULL），第 2 天起跌破（BEAR），
    故 BEAR 尾部连续天数 = crash_days - 1。
    """
    closes = _bull_closes(bull_days)
    last = closes[-1]
    for i in range(1, crash_days + 1):
        closes.append(last * (1.0 - crash_daily) ** i)
    return closes


class TestClassifyRegime:
    def test_bull_by_price_above_ma(self):
        assert classify_regime(_bull_closes()) == MarketRegime.BULL

    def test_bear_by_price_below_ma(self):
        """跌破 MA60 即判 BEAR（即使回撤未达 20%）"""
        closes = _bull_then_crash(crash_days=5)
        assert classify_regime(closes) == MarketRegime.BEAR

    def test_bear_by_drawdown(self):
        """价格仍在 MA 上方但自峰值回撤 ≥20% → BEAR（牛熊分界线规则）"""
        # 急涨（每日 +5%×20 天）后回撤 22%，现价仍高于 MA30
        closes = [100.0 * 1.05**i for i in range(20)]  # 100 → ~265
        peak = closes[-1]
        closes += [peak * (1 - 0.22 * i / 10) for i in range(1, 11)]  # 回撤至 78%
        assert closes[-1] > sum(closes[-30:]) / 30  # 现价仍在 MA30 上方
        assert classify_regime(closes, ma_window=30) == MarketRegime.BEAR

    def test_insufficient_history_raises(self):
        with pytest.raises(ValueError):
            classify_regime([100.0] * 30)


class TestBuildRegimeSeries:
    def test_persistent_bull_series_all_bull(self):
        series = build_regime_series(_bull_closes(), days=60)
        assert len(series) == 60
        assert all(r == MarketRegime.BULL for r in series)

    def test_series_captures_flip(self):
        closes = _bull_then_crash(crash_days=10)
        series = build_regime_series(closes, days=60)
        assert series[-1] == MarketRegime.BEAR
        assert series[0] == MarketRegime.BULL


class TestCusumLevel:
    def test_white_noise_low_level(self):
        """零漂移交替小噪声 → CUSUM 远低于报警水平"""
        returns = [0.0005 * (1 if i % 2 == 0 else -1) for i in range(100)]
        assert cusum_level(returns) < 0.5

    def test_persistent_negative_drift_detected(self):
        """窗口内收益均值发生负漂移 → CUSUM 统计量 ≥1（σ√n 归一）"""
        returns = [0.0002] * 60 + [-0.006] * 40
        assert cusum_level(returns) >= 1.0

    def test_empty_returns_zero(self):
        assert cusum_level([]) == 0.0


class TestDetectRegimeChange:
    def test_persistent_bull_stable(self):
        snap = detect_regime_change(_bull_closes())
        assert snap.phase == ChangePhase.STABLE
        assert snap.regime == MarketRegime.BULL
        assert snap.candidate is None
        assert snap.switch_probability < 0.3
        assert 0.0 <= snap.confidence <= 1.0

    def test_recent_flip_triggered(self):
        """刚翻转 1 天（< confirm_days=3）→ TRIGGERED，体制仍为 BULL，候选 BEAR"""
        snap = detect_regime_change(_bull_then_crash(crash_days=2))
        assert snap.phase == ChangePhase.TRIGGERED
        assert snap.regime == MarketRegime.BULL
        assert snap.candidate == MarketRegime.BEAR
        assert snap.days_in_candidate == 1
        assert 0.3 < snap.switch_probability < 0.9

    def test_persistent_flip_confirmed(self):
        """翻转持续 > confirm_days → CONFIRMED，体制更新为 BEAR"""
        snap = detect_regime_change(_bull_then_crash(crash_days=10))
        assert snap.phase == ChangePhase.CONFIRMED
        assert snap.regime == MarketRegime.BEAR
        assert snap.candidate is None
        assert snap.switch_probability >= 0.7

    def test_triggered_probability_grows_with_days(self):
        """触发态切换概率随候选持续天数单调上升"""
        p1 = detect_regime_change(_bull_then_crash(crash_days=2)).switch_probability
        p2 = detect_regime_change(_bull_then_crash(crash_days=3)).switch_probability
        p3 = detect_regime_change(_bull_then_crash(crash_days=4)).switch_probability
        assert p1 < p2 < p3

    def test_custom_confirm_days(self):
        cfg = RegimeChangeConfig(confirm_days=5)
        snap = detect_regime_change(_bull_then_crash(crash_days=6), cfg)
        assert snap.phase == ChangePhase.TRIGGERED
        snap7 = detect_regime_change(_bull_then_crash(crash_days=7), cfg)
        assert snap7.phase == ChangePhase.CONFIRMED

    def test_stable_with_cusum_pressure_escalates_to_watch(self):
        """体制未翻转但 CUSUM 压力逼近阈值 → STABLE 升级为 WATCH 预警"""
        closes = _bull_then_crash(crash_days=1)  # 单日 -5% 急跌未破 MA60
        cfg = RegimeChangeConfig(watch_band=0.4)
        snap = detect_regime_change(closes, cfg)
        assert snap.phase == ChangePhase.WATCH
        assert snap.regime == MarketRegime.BULL
        assert snap.candidate is None
        assert snap.cusum_level >= 0.4

    def test_watch_band_default_not_triggered_by_one_day_dip(self):
        """默认 watch_band 下单日急跌不升级（保持 STABLE）"""
        snap = detect_regime_change(_bull_then_crash(crash_days=1))
        assert snap.phase == ChangePhase.STABLE

    def test_insufficient_history_raises(self):
        with pytest.raises(ValueError):
            detect_regime_change([100.0] * 50)


class TestRegimeChangeDetectorLoader:
    def test_load_and_detect_with_fake_query(self):
        closes = _bull_then_crash(crash_days=10)
        rows = "\n".join(f"2026-01-01\t{c:.4f}" for c in closes)
        detector = RegimeChangeDetector(query_fn=lambda sql, timeout=30: rows)
        snap = detector.detect("000300", "2025-01-01", "2026-08-31")
        assert snap.phase == ChangePhase.CONFIRMED
        assert snap.regime == MarketRegime.BEAR

    def test_empty_query_raises(self):
        detector = RegimeChangeDetector(query_fn=lambda sql, timeout=30: "")
        with pytest.raises(RegimeChangeDataError):
            detector.detect("000300", "2025-01-01", "2026-08-31")
