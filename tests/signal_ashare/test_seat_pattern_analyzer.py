"""MOD-SIG-056 龙虎榜席位形态分析器 单元测试"""

import pytest

from zephyr.signal_ashare.seat_pattern_analyzer import (
    FollowDirection,
    SeatPatternAnalyzer,
    SeatPatternConfig,
    SeatPatternDataError,
    SeatRecord,
)


@pytest.fixture
def analyzer() -> SeatPatternAnalyzer:
    # registry_path 指向真实 seat_registry.yaml（15 席位档案）
    return SeatPatternAnalyzer(SeatPatternConfig())


def _rec(
    seat_name: str,
    net: float,
    buy_rank: int | None = None,
    sell_rank: int | None = None,
    provider_type: str = "broker",
    symbol: str = "000001",
    trade_date: str = "2026-08-18",
) -> SeatRecord:
    buy = max(net, 0.0) + 1_000_000.0
    sell = max(-net, 0.0) + 1_000_000.0
    return SeatRecord(
        symbol=symbol,
        trade_date=trade_date,
        seat_name=seat_name,
        buy_amount=buy,
        sell_amount=sell,
        net_amount=net,
        buy_rank=buy_rank,
        sell_rank=sell_rank,
        provider_seat_type=provider_type,
        reason="日涨幅偏离值达7%",
    )


# ---------- A1 席位身份识别 ----------


def test_identify_institution_exact_match(analyzer: SeatPatternAnalyzer) -> None:
    rec = _rec("机构专用", 50_000_000, buy_rank=1, provider_type="institution")
    profile = analyzer.identify_seat(rec, total_turnover=200_000_000)
    assert profile.matched_registry is True
    assert profile.seat_id == "SEAT-INST-001"
    assert profile.seat_type == "institution"
    assert profile.net_buy_ratio == pytest.approx(0.25)


def test_identify_youzi_alias_match(analyzer: SeatPatternAnalyzer) -> None:
    rec = _rec("章盟主席位", 20_000_000, buy_rank=1)
    profile = analyzer.identify_seat(rec, total_turnover=100_000_000)
    assert profile.matched_registry is True
    assert profile.seat_id == "SEAT-YOUZI-001"
    assert profile.seat_type == "youzi"
    assert profile.seat_style == "龙头连板"


def test_identify_fallback_provider_type(analyzer: SeatPatternAnalyzer) -> None:
    rec = _rec("某不知名营业部", 5_000_000, buy_rank=3, provider_type="connect")
    profile = analyzer.identify_seat(rec, total_turnover=100_000_000)
    assert profile.matched_registry is False
    assert profile.seat_type == "connect"
    assert profile.seat_id is None


def test_identify_case_insensitive_and_whitespace(analyzer: SeatPatternAnalyzer) -> None:
    rec = _rec("  方新侠 ", 10_000_000, buy_rank=2)
    profile = analyzer.identify_seat(rec, total_turnover=100_000_000)
    assert profile.matched_registry is True
    assert profile.seat_id == "SEAT-YOUZI-002"


# ---------- A2 席位联动 ----------


def test_linkage_institution_youzi_relay(analyzer: SeatPatternAnalyzer) -> None:
    records = [
        _rec("机构专用", 60_000_000, buy_rank=1, provider_type="institution"),
        _rec("章盟主", 30_000_000, buy_rank=2),
        _rec("某营业部A", -10_000_000, sell_rank=1),
    ]
    result = analyzer.analyze(records)
    assert result.linkage is not None
    assert result.linkage.linkage_tag == "institution_youzi_relay"
    assert result.linkage.institution_net == pytest.approx(60_000_000)
    assert result.linkage.youzi_net == pytest.approx(30_000_000)


def test_linkage_top2_concentration(analyzer: SeatPatternAnalyzer) -> None:
    records = [
        _rec("机构专用", 80_000_000, buy_rank=1, provider_type="institution"),
        _rec("章盟主", 15_000_000, buy_rank=2),
        _rec("某营业部B", 5_000_000, buy_rank=3),
    ]
    result = analyzer.analyze(records)
    assert result.linkage is not None
    # top2 = 95M / 100M
    assert result.linkage.top2_concentration == pytest.approx(0.95)


def test_linkage_retail_dominated(analyzer: SeatPatternAnalyzer) -> None:
    records = [
        _rec("拉萨金融城南环路", 30_000_000, buy_rank=1),
        _rec("拉萨东环路", 20_000_000, buy_rank=2),
        _rec("某营业部C", -5_000_000, sell_rank=1),
    ]
    result = analyzer.analyze(records)
    assert result.linkage is not None
    assert result.linkage.linkage_tag == "retail_dominated"
    assert result.linkage.retail_net == pytest.approx(50_000_000)


# ---------- A3 跟随信号合成 ----------


def test_follow_long_institution_plus_youzi(analyzer: SeatPatternAnalyzer) -> None:
    # 机构60M + 游资30M + 强净买入占比 + 接力结构 → ≥60 long
    records = [
        _rec("机构专用", 60_000_000, buy_rank=1, provider_type="institution"),
        _rec("章盟主", 30_000_000, buy_rank=2),
        _rec("某营业部D", -20_000_000, sell_rank=1),
    ]
    result = analyzer.analyze(records)
    sig = result.follow_signal
    # 50 + 15(机构) + 10(知名游资) + 10(净买入占比>10%) + 5(接力) = 90
    assert sig.follow_score == pytest.approx(90.0)
    assert sig.direction == FollowDirection.LONG
    assert any("机构净买入" in r for r in sig.reasons)


def test_follow_avoid_quant_grinder(analyzer: SeatPatternAnalyzer) -> None:
    # 量化主导 + 散户共现 → ≤40 avoid
    records = [
        _rec("华鑫上海", 40_000_000, buy_rank=1),
        _rec("拉萨金融城南环路", 30_000_000, buy_rank=2),
        _rec("某营业部E", -60_000_000, sell_rank=1),
    ]
    result = analyzer.analyze(records)
    sig = result.follow_signal
    # 50 - 20(量化主导 40/130=31%) - 10(绞肉机) = 20；散户 30/130=23% 未达 30% 阈值
    assert sig.follow_score == pytest.approx(20.0)
    assert sig.direction == FollowDirection.AVOID


def test_follow_neutral_balanced(analyzer: SeatPatternAnalyzer) -> None:
    # 无加减分触发 → 50 neutral
    records = [
        _rec("某营业部F", 10_000_000, buy_rank=1),
        _rec("某营业部G", -10_000_000, sell_rank=1),
    ]
    result = analyzer.analyze(records)
    sig = result.follow_signal
    assert sig.follow_score == pytest.approx(50.0)
    assert sig.direction == FollowDirection.NEUTRAL


def test_follow_top2_danger_penalty(analyzer: SeatPatternAnalyzer) -> None:
    # 独食结构：买一买二占比 >70%
    records = [
        _rec("机构专用", 90_000_000, buy_rank=1, provider_type="institution"),
        _rec("某营业部H", 5_000_000, buy_rank=2),
        _rec("某营业部I", 2_000_000, buy_rank=3),
    ]
    result = analyzer.analyze(records)
    sig = result.follow_signal
    # 50 + 15(机构) + 10(净占比>10%) - 10(独食) = 65
    assert sig.follow_score == pytest.approx(65.0)
    assert any("独食" in r for r in sig.reasons)


def test_follow_score_clamped(analyzer: SeatPatternAnalyzer) -> None:
    # 极端负分应截断到 0
    cfg = SeatPatternConfig()
    analyzer2 = SeatPatternAnalyzer(cfg)
    records = [
        _rec("华鑫上海", 50_000_000, buy_rank=1),
        _rec("华泰总部", 40_000_000, buy_rank=2),
        _rec("拉萨金融城南环路", 35_000_000, buy_rank=3),
        _rec("拉萨东环路", 30_000_000, buy_rank=4),
    ]
    result = analyzer2.analyze(records)
    assert 0.0 <= result.follow_signal.follow_score <= 100.0


# ---------- 降级与契约 ----------


def test_empty_records_degraded(analyzer: SeatPatternAnalyzer) -> None:
    result = analyzer.analyze([])
    assert result.degraded is True
    assert result.follow_signal.direction == FollowDirection.NEUTRAL
    assert result.linkage is None


def test_mixed_symbols_raises(analyzer: SeatPatternAnalyzer) -> None:
    records = [
        _rec("机构专用", 10_000_000, buy_rank=1, symbol="000001"),
        _rec("机构专用", 10_000_000, buy_rank=1, symbol="000002"),
    ]
    with pytest.raises(SeatPatternDataError):
        analyzer.analyze(records)


def test_mixed_dates_raises(analyzer: SeatPatternAnalyzer) -> None:
    records = [
        _rec("机构专用", 10_000_000, buy_rank=1, trade_date="2026-08-17"),
        _rec("机构专用", 10_000_000, buy_rank=1, trade_date="2026-08-18"),
    ]
    with pytest.raises(SeatPatternDataError):
        analyzer.analyze(records)


def test_missing_registry_degrades_gracefully(tmp_path) -> None:
    cfg = SeatPatternConfig(registry_path=str(tmp_path / "nonexistent.yaml"))
    analyzer3 = SeatPatternAnalyzer(cfg)
    records = [_rec("机构专用", 60_000_000, buy_rank=1, provider_type="institution")]
    result = analyzer3.analyze(records)
    # registry 缺失 → matched_registry=False 回退 provider 类型，流程不崩
    assert result.profiles[0].matched_registry is False
    assert result.profiles[0].seat_type == "institution"
    assert result.degraded is False


def test_zero_turnover_degraded(analyzer: SeatPatternAnalyzer) -> None:
    rec = SeatRecord(
        symbol="000001",
        trade_date="2026-08-18",
        seat_name="机构专用",
        buy_amount=0.0,
        sell_amount=0.0,
        net_amount=0.0,
        provider_seat_type="institution",
    )
    result = analyzer.analyze([rec])
    assert result.degraded is True
