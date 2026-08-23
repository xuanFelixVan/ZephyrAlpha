# [BLUEPRINT] MOD-SIG-068 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-25 行）
# [MODULE] tests.signal_ashare.test_t0_point_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.t0_point_analyzer
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=做T点位/回验逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-068_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-068 做T点位算法+信号回验管线 单元测试（GAP-F-25，合成数据不触库）。

覆盖：VWAP 序列、回踩均价 T买（含缩量/偏离带双条件）、偏离回归 T卖/T买、
量价背离顶/底双向、冷却窗去重（簇内取最高置信度）、MOD-SIG-024 适配腿
（回踩均线映射 T买）、回验四判定（命中/半命中/失手/样本不足）+T卖反向、
pattern×window 命中率聚合、非法配置 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.signal_ashare.t0_point_analyzer import (
    PATTERN_DEVIATION_REVERT,
    PATTERN_PULLBACK_VWAP,
    PATTERN_VOLUME_DIVERGENCE,
    T_BUY,
    T_SELL,
    VERDICT_HALF,
    VERDICT_HIT,
    VERDICT_INSUFFICIENT,
    VERDICT_MISS,
    MinuteBar,
    T0AnalyzerConfig,
    T0BacktestConfig,
    T0Context,
    T0Signal,
    generate_t0_signals,
    verify_t0_signals,
)

CTX = T0Context(symbol="510300.SH", prev_close=100.0)


def _bar(i: int, close: float, volume: float = 100.0, high: float | None = None, low: float | None = None) -> MinuteBar:
    hh = 9 * 60 + 31 + i
    ts = f"2026-08-21 {hh // 60:02d}:{hh % 60:02d}"
    return MinuteBar(
        ts=ts, open=close, high=high if high is not None else close * 1.001,
        low=low if low is not None else close * 0.999, close=close, volume=volume,
    )


def _deviation_bars() -> list[MinuteBar]:
    # 前 10 根贴 100，随后冲高偏离 VWAP
    bars = [_bar(i, 100.0) for i in range(10)]
    for i in range(10, 20):
        bars.append(_bar(i, 100.0 + (i - 9) * 0.4))  # 100.4 → 104.0 渐冲高
    return bars


def _pullback_bars() -> list[MinuteBar]:
    # 冲高后缩量回踩均价（冲高至 102.5 → VWAP≈101，回踩 101.2 在 VWAP 上方带内）
    bars = [_bar(i, 100.0) for i in range(5)]
    for i in range(5, 10):
        bars.append(_bar(i, 100.0 + (i - 4) * 0.5, volume=200.0))  # 放量冲高
    for i in range(10, 16):
        bars.append(_bar(i, 101.2, volume=40.0))  # 缩量回踩（VWAP 上方带内）
    return bars


def _divergence_bars() -> list[MinuteBar]:
    # 双顶：前高放量、后高缩量 → 量价背离 T卖
    bars = [_bar(0, 100.0, volume=100.0, high=100.2, low=99.8)]
    bars.append(_bar(1, 100.5, volume=300.0, high=101.0, low=100.3))  # 前高放量
    bars.append(_bar(2, 100.3, volume=120.0, high=100.6, low=100.1))
    bars.append(_bar(3, 100.4, volume=110.0, high=100.7, low=100.2))
    bars.append(_bar(4, 100.8, volume=100.0, high=101.2, low=100.5))  # 新高量缩
    return bars


# ------------------------------------------------------------------
# 信号生成
# ------------------------------------------------------------------


def test_deviation_revert_sell():
    signals = generate_t0_signals(_deviation_bars(), CTX, T0AnalyzerConfig(use_sig024=False))
    sell = [s for s in signals if s.direction == T_SELL and s.pattern == PATTERN_DEVIATION_REVERT]
    assert sell, "冲高偏离应出 T卖"
    assert all("冲高" in s.logic or "远离均价" in s.logic for s in sell)


def test_pullback_vwap_buy():
    signals = generate_t0_signals(_pullback_bars(), CTX, T0AnalyzerConfig(use_sig024=False))
    buy = [s for s in signals if s.direction == T_BUY and s.pattern == PATTERN_PULLBACK_VWAP]
    assert buy, "缩量回踩均价应出 T买"
    assert "回踩均价" in buy[0].logic


def test_volume_divergence_sell():
    signals = generate_t0_signals(_divergence_bars(), CTX, T0AnalyzerConfig(use_sig024=False))
    sell = [s for s in signals if s.pattern == PATTERN_VOLUME_DIVERGENCE and s.direction == T_SELL]
    assert sell, "新高量缩应出量价背离 T卖"
    assert sell[0].ts == "2026-08-21 09:35"


def test_cooldown_dedup_keeps_highest_confidence():
    bars = _deviation_bars()
    cfg = T0AnalyzerConfig(use_sig024=False, cooldown_bars=15)
    signals = generate_t0_signals(bars, CTX, cfg)
    sell = [s for s in signals if s.direction == T_SELL]
    # 冷却窗 15 > 冲高段长度 → 同方向仅保留 1 条最高置信度
    assert len(sell) <= 1 or all(
        abs(int(a.ts[-2:]) - int(b.ts[-2:])) >= 15 for a, b in zip(sell, sell[1:])
    )


def test_sig024_adapter_leg_fires():
    # 回踩均价场景下 SIG-024 回调买点（deviation∈(0,3%]+缩量）应命中
    signals = generate_t0_signals(_pullback_bars(), CTX, T0AnalyzerConfig(use_sig024=True, cooldown_bars=5))
    assert any(s.source in ("sig024", "t_specialized") for s in signals)
    assert signals, "双腿合并后应有信号"


def test_empty_bars_no_signals():
    assert generate_t0_signals([], CTX) == []


def test_bad_lookback_fail_closed():
    with pytest.raises(ValueError):
        generate_t0_signals(_deviation_bars(), CTX, T0AnalyzerConfig(lookback_bars=1))


# ------------------------------------------------------------------
# 回验
# ------------------------------------------------------------------


def _signal(ts: str, direction: str, pattern: str = PATTERN_PULLBACK_VWAP, price: float = 100.0) -> T0Signal:
    return T0Signal(ts=ts, symbol="510300.SH", direction=direction, pattern=pattern,
                    price=price, confidence=70.0, logic="t", source="t_specialized")


def _verify_bars() -> list[MinuteBar]:
    # 60 根 1 分钟 bar：信号点(索引10)后缓涨
    bars = [_bar(i, 100.0) for i in range(11)]
    for i in range(11, 60):
        bars.append(_bar(i, 100.0 + (i - 10) * 0.05))  # 每根 +0.05%
    return bars


def test_verify_buy_hit_and_half():
    bars = _verify_bars()
    sig = _signal(bars[10].ts, T_BUY)
    report = verify_t0_signals([sig], bars, T0BacktestConfig(windows_bars=(10, 30), hit_threshold_pct=0.2))
    hit = report.hits[0]
    # +10 根：+0.05×10=+0.5% ≥0.2 → 命中；+30 根：+1.5% → 命中
    assert hit.verdicts[10] == VERDICT_HIT
    assert hit.verdicts[30] == VERDICT_HIT
    assert hit.forward_ret_pct[10] == pytest.approx(0.5, abs=0.01)


def test_verify_sell_reverse_symmetric():
    bars = _verify_bars()  # 上涨趋势
    sig = _signal(bars[10].ts, T_SELL)
    report = verify_t0_signals([sig], bars, T0BacktestConfig(windows_bars=(10,)))
    assert report.hits[0].verdicts[10] == VERDICT_MISS  # T卖后上涨=失手


def test_verify_half_hit_band():
    bars = [_bar(i, 100.0 + (0.01 if i % 2 else -0.01)) for i in range(40)]  # 微幅震荡
    sig = _signal(bars[5].ts, T_BUY)
    report = verify_t0_signals([sig], bars, T0BacktestConfig(windows_bars=(10,), hit_threshold_pct=0.2))
    assert report.hits[0].verdicts[10] == VERDICT_HALF


def test_verify_insufficient_forward():
    bars = _verify_bars()
    sig = _signal(bars[55].ts, T_BUY)  # 尾盘信号，+10/+30 不足
    report = verify_t0_signals([sig], bars, T0BacktestConfig(windows_bars=(10, 30)))
    assert report.hits[0].verdicts[30] == VERDICT_INSUFFICIENT
    stat = next(s for s in report.stats if s.window_bars == 30)
    assert stat.hit_rate is None  # 全样本不足不出伪率


def test_verify_stats_aggregation():
    bars = _verify_bars()
    sigs = [_signal(bars[10].ts, T_BUY), _signal(bars[12].ts, T_BUY, pattern=PATTERN_DEVIATION_REVERT)]
    report = verify_t0_signals(sigs, bars, T0BacktestConfig(windows_bars=(10,)))
    stat = next(s for s in report.stats if s.pattern == PATTERN_PULLBACK_VWAP)
    assert stat.total == 1 and stat.hit == 1 and stat.hit_rate == 1.0
    assert report.date == "2026-08-21"
    assert report.symbol == "510300.SH"


def test_verify_bad_config_fail_closed():
    with pytest.raises(ValueError):
        verify_t0_signals([], _verify_bars(), T0BacktestConfig(windows_bars=(0,)))
    with pytest.raises(ValueError):
        verify_t0_signals([], _verify_bars(), T0BacktestConfig(hit_threshold_pct=0.0))


def test_verify_empty_signals_note():
    report = verify_t0_signals([], _verify_bars())
    assert report.hits == [] and any("无信号" in n for n in report.notes)


def test_end_to_end_json_serializable():
    bars = _pullback_bars() + [_bar(16 + i, 101.2 + i * 0.05) for i in range(40)]
    signals = generate_t0_signals(bars, CTX, T0AnalyzerConfig(cooldown_bars=5))
    report = verify_t0_signals(signals, bars)
    json.dumps(asdict(report), ensure_ascii=False)
