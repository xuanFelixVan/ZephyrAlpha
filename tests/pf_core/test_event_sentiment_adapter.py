# [A_test] module_id: MOD-GOV_event_sentiment_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md | §test
# [MODULE] tests.pf_core.test_event_sentiment_adapter
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/pf_core/test_event_sentiment_adapter.py
# [TTL] permanent
"""D_PORTFOLIO_CORE event_sentiment_adapter（runner 契约适配层）测试。

覆盖（纯逻辑零 DB，fake source 注入）：
- signal_window_date：交易日 T → 夜间窗 window_date=T-1（自然日，PIT 口径）
- sentiment_to_event_payload：情绪行 → eventdriven-sleeve 富负载契约
  （canonical symbol 去后缀 / class_ 默认 news / direction=+1 情绪带号 / symbol 不重复注入）
- build_event_weight_panel：逐日取窗 → 策略富负载 → 权重面板（零行 hold/exclude/top_n/权重和≤1）
- 面板 symbol 与 load_history 同源（纯数字代码，INV 同源）
- ClickHouseSentimentWindowSource 行解析与 symbol 白名单（不触 DB）
"""

from __future__ import annotations

import datetime

import pytest

pd = pytest.importorskip("pandas")

from zephyr.intelligence.event_score import SIGNAL_NOISE_THRESHOLD  # noqa: E402
from zephyr.pf_core.strategies.event_driven_sleeve_strategy import (  # noqa: E402
    EventDrivenSleeveStrategy,
)
from zephyr.pf_core.strategy_engine.event_sentiment_adapter import (  # noqa: E402
    DEFAULT_EVENT_CLASS,
    ClickHouseSentimentWindowSource,
    SentimentRow,
    build_event_weight_panel,
    sentiment_to_event_payload,
    signal_window_date,
)


def _row(symbol: str, idx: float, total: int = 3) -> SentimentRow:
    return SentimentRow(
        symbol=symbol,
        sentiment_index=idx,
        positive_count=total if idx > 0 else 0,
        negative_count=total if idx < 0 else 0,
        neutral_count=0,
        total_count=total,
    )


# ── signal_window_date ────────────────────────────────────────────────


def test_signal_window_date_prev_natural_day():
    assert signal_window_date(datetime.date(2026, 8, 18)) == datetime.date(2026, 8, 17)


def test_signal_window_date_monday_maps_to_sunday():
    # 2026-08-17 为周一：夜间窗 [周日18:00, 周一08:00) → window_date=周日
    assert signal_window_date(datetime.date(2026, 8, 17)) == datetime.date(2026, 8, 16)


def test_signal_window_date_accepts_timestamp():
    ts = pd.Timestamp("2026-08-18")
    assert signal_window_date(ts) == datetime.date(2026, 8, 17)


# ── sentiment_to_event_payload ────────────────────────────────────────


def test_payload_maps_fields_and_strips_suffix():
    payload = sentiment_to_event_payload([_row("600519.SH", 0.5)])
    assert list(payload.keys()) == ["600519"]
    ev = payload["600519"]["event"]
    assert ev["class_"] == DEFAULT_EVENT_CLASS
    assert ev["surprise_direction"] == 1.0
    assert ev["sentiment_score"] == pytest.approx(0.5)
    assert ev["decay_stage_factor"] == 1.0
    assert ev["extreme_reaction_modifier"] == 1.0
    assert "symbol" not in ev  # symbol 由策略侧注入，防 EventRecord 重复键


def test_payload_keeps_signed_sentiment():
    payload = sentiment_to_event_payload([_row("000001.SZ", -0.6)])
    assert payload["000001"]["event"]["sentiment_score"] == pytest.approx(-0.6)


def test_payload_symbol_without_suffix_passthrough():
    payload = sentiment_to_event_payload([_row("300750", 0.4)])
    assert "300750" in payload


def test_payload_empty_rows():
    assert sentiment_to_event_payload([]) == {}


# ── 与 EventDrivenSleeveStrategy 契约贯通 ─────────────────────────────


def test_payload_consumed_by_strategy_contract():
    strategy = EventDrivenSleeveStrategy()
    rows = [
        _row("600519.SH", 0.9),
        _row("000001.SZ", 0.3),
        _row("300750.SZ", -0.8),  # 负情绪 → 利空剔除（A股不能做空）
        _row("601211.SH", 0.1),  # 低于噪声阈 0.2 → 不动作
    ]
    payload = sentiment_to_event_payload(rows)
    weights = strategy.generate_target_weights(
        universe=["600519", "000001", "300750", "601211"],
        signals=payload,
        constraints={"top_n": 10, "max_single": 0.10},
    )
    assert set(weights.keys()) == {"600519", "000001"}
    assert weights["600519"] == pytest.approx(0.10)  # max_single 截顶
    assert weights["000001"] == pytest.approx(0.10)
    assert sum(weights.values()) <= 1.0 + 1e-12


def test_noise_threshold_boundary():
    strategy = EventDrivenSleeveStrategy()
    at = SIGNAL_NOISE_THRESHOLD
    payload = sentiment_to_event_payload([_row("600519.SH", at), _row("000001.SZ", at - 0.001)])
    weights = strategy.generate_target_weights(
        universe=["600519", "000001"], signals=payload, constraints={"top_n": 10, "max_single": 0.5}
    )
    assert "600519" in weights  # score==阈值 不触发 <|过滤
    assert "000001" not in weights


# ── build_event_weight_panel ──────────────────────────────────────────


class _FakeSource:
    """按 window_date 供给情绪行的假源（记录查询日期以验证 PIT 口径）。"""

    def __init__(self, by_window_date: dict[datetime.date, list[SentimentRow]]):
        self._data = by_window_date
        self.queried: list[datetime.date] = []

    def fetch(self, window_date: datetime.date, symbols=None) -> list[SentimentRow]:
        self.queried.append(window_date)
        return self._data.get(window_date, [])


def test_panel_pit_window_mapping_and_zero_row_hold():
    d1, d2, d3 = pd.Timestamp("2026-08-14"), pd.Timestamp("2026-08-17"), pd.Timestamp("2026-08-18")
    source = _FakeSource(
        {
            datetime.date(2026, 8, 13): [_row("600519.SH", 0.9)],  # d1 的窗
            # d2 的窗（08-16 周日）无行 → 当日全零行（引擎语义=hold 沿用持仓）
            datetime.date(2026, 8, 17): [_row("000001.SZ", 0.8)],  # d3 的窗
        }
    )
    panel = build_event_weight_panel(
        [d1, d2, d3],
        ["600519", "000001"],
        source=source,
        strategy=EventDrivenSleeveStrategy(),
        top_n=10,
        max_single=0.10,
    )
    # PIT：三日查询的 window_date 分别为 08-13/08-16/08-17
    assert source.queried == [
        datetime.date(2026, 8, 13),
        datetime.date(2026, 8, 16),
        datetime.date(2026, 8, 17),
    ]
    assert panel.loc[d1, "600519"] == pytest.approx(0.10)
    # d2 空窗 → 全零行（引擎 _normalize_day_signals 仅取>0 分量，零行=当日 hold）
    assert float(panel.loc[d2].sum()) == 0.0
    assert panel.loc[d3, "000001"] == pytest.approx(0.10)
    # d3 调仓后 600519 不再入选 → 权重归零（新组合覆盖）
    assert panel.loc[d3, "600519"] == pytest.approx(0.0)


def test_panel_exclude_filter():
    d1 = pd.Timestamp("2026-08-18")
    source = _FakeSource({datetime.date(2026, 8, 17): [_row("600519.SH", 0.9), _row("000001.SZ", 0.8)]})
    panel = build_event_weight_panel(
        [d1],
        ["600519", "000001"],
        source=source,
        strategy=EventDrivenSleeveStrategy(),
        exclude=lambda d: {"600519"},
    )
    assert panel.loc[d1, "600519"] == pytest.approx(0.0)
    assert panel.loc[d1, "000001"] == pytest.approx(0.10)


def test_panel_top_n_and_weight_cap():
    d1 = pd.Timestamp("2026-08-18")
    rows = [_row(f"60000{i}.SH", 0.9 - i * 0.01) for i in range(5)]
    source = _FakeSource({datetime.date(2026, 8, 17): rows})
    panel = build_event_weight_panel(
        [d1],
        [f"60000{i}" for i in range(5)],
        source=source,
        strategy=EventDrivenSleeveStrategy(),
        top_n=3,
        max_single=0.10,
    )
    picked = [c for c in panel.columns if panel.loc[d1, c] > 0]
    assert len(picked) == 3
    assert all(panel.loc[d1, c] <= 0.10 + 1e-12 for c in picked)
    assert float(panel.loc[d1].sum()) <= 1.0 + 1e-12


def test_panel_empty_source_all_zero():
    d1 = pd.Timestamp("2026-08-18")
    source = _FakeSource({})
    panel = build_event_weight_panel(
        [d1], ["600519"], source=source, strategy=EventDrivenSleeveStrategy()
    )
    assert float(panel.loc[d1].sum()) == 0.0


def test_panel_columns_plain_symbols():
    d1 = pd.Timestamp("2026-08-18")
    source = _FakeSource({datetime.date(2026, 8, 17): [_row("600519.SH", 0.9)]})
    panel = build_event_weight_panel(
        [d1], ["600519"], source=source, strategy=EventDrivenSleeveStrategy()
    )
    assert all("." not in c for c in panel.columns)


# ── PIT 防未来函数护栏（window_date ≤ T-1 才可消费）──────────────────


def _row_dated(symbol: str, idx: float, win: datetime.date) -> SentimentRow:
    return SentimentRow(symbol=symbol, sentiment_index=idx, total_count=3, window_date=win)


def test_pit_guard_t_minus_1_consumable():
    # T-1 窗口记录：可消费（口径边界——恰好等于 cutoff 放行）
    d1 = pd.Timestamp("2026-08-18")  # 周二 T
    source = _FakeSource({datetime.date(2026, 8, 17): [_row_dated("600519.SH", 0.9, datetime.date(2026, 8, 17))]})
    panel = build_event_weight_panel(
        [d1], ["600519"], source=source, strategy=EventDrivenSleeveStrategy()
    )
    assert panel.loc[d1, "600519"] == pytest.approx(0.10)


def test_pit_guard_t_day_record_not_consumable():
    # T 日记录（window_date=T）：防未来函数硬剔除——当日面板全零（hold）
    d1 = pd.Timestamp("2026-08-18")
    source = _FakeSource({datetime.date(2026, 8, 17): [_row_dated("600519.SH", 0.9, datetime.date(2026, 8, 18))]})
    panel = build_event_weight_panel(
        [d1], ["600519"], source=source, strategy=EventDrivenSleeveStrategy()
    )
    assert float(panel.loc[d1].sum()) == 0.0


def test_pit_guard_future_record_beyond_t_not_consumable():
    # T+1 及更远未来记录：同样硬剔除
    d1 = pd.Timestamp("2026-08-18")
    source = _FakeSource(
        {
            datetime.date(2026, 8, 17): [
                _row_dated("600519.SH", 0.9, datetime.date(2026, 8, 19)),  # T+1 → 剔除
                _row_dated("000001.SZ", 0.8, datetime.date(2026, 8, 17)),  # T-1 → 可消费
            ]
        }
    )
    panel = build_event_weight_panel(
        [d1], ["600519", "000001"], source=source, strategy=EventDrivenSleeveStrategy()
    )
    assert panel.loc[d1, "600519"] == pytest.approx(0.0)
    assert panel.loc[d1, "000001"] == pytest.approx(0.10)


def test_pit_guard_cross_weekend_t_minus_3_consumable():
    # 跨周末：周一 T 的 cutoff=周日（T-1 自然日）；周五（T-3）窗口记录 ≤ cutoff 可消费
    d1 = pd.Timestamp("2026-08-17")  # 周一
    source = _FakeSource(
        {
            datetime.date(2026, 8, 16): [
                _row_dated("600519.SH", 0.9, datetime.date(2026, 8, 14)),  # 周五（T-3）→ 可消费
                _row_dated("000001.SZ", 0.8, datetime.date(2026, 8, 16)),  # 周日（T-1）→ 可消费
            ]
        }
    )
    panel = build_event_weight_panel(
        [d1], ["600519", "000001"], source=source, strategy=EventDrivenSleeveStrategy()
    )
    assert panel.loc[d1, "600519"] == pytest.approx(0.10)
    assert panel.loc[d1, "000001"] == pytest.approx(0.10)


def test_pit_guard_logs_violation(caplog):
    # 违规剔除须留痕（warning 含剔除条数与 cutoff）
    d1 = pd.Timestamp("2026-08-18")
    source = _FakeSource({datetime.date(2026, 8, 17): [_row_dated("600519.SH", 0.9, datetime.date(2026, 8, 18))]})
    with caplog.at_level("WARNING", logger="zephyr.pf_core.strategy_engine.event_sentiment_adapter"):
        build_event_weight_panel([d1], ["600519"], source=source, strategy=EventDrivenSleeveStrategy())
    assert any("PIT" in rec.message and "1 条" in rec.message for rec in caplog.records)


def test_pit_guard_none_window_date_passthrough():
    # window_date=None（源未携带归属日）：放行兼容（fetch 点查询已按 T-1 取窗）
    d1 = pd.Timestamp("2026-08-18")
    source = _FakeSource({datetime.date(2026, 8, 17): [_row("600519.SH", 0.9)]})
    panel = build_event_weight_panel(
        [d1], ["600519"], source=source, strategy=EventDrivenSleeveStrategy()
    )
    assert panel.loc[d1, "600519"] == pytest.approx(0.10)


def test_ch_source_parse_row_with_window_date():
    row = ClickHouseSentimentWindowSource.parse_row(("600519.SH", 0.42, 3, 1, 0, 4, "2026-08-17"))
    assert row.window_date == datetime.date(2026, 8, 17)
    row_none = ClickHouseSentimentWindowSource.parse_row(("600519.SH", 0.42, 3, 1, 0, 4))
    assert row_none.window_date is None


# ── ClickHouseSentimentWindowSource（不触 DB：SQL 形态/行解析/白名单）──


def test_ch_source_rejects_invalid_window_date_type():
    src = ClickHouseSentimentWindowSource()
    with pytest.raises(ValueError):
        src.fetch("2026-08-17")  # type: ignore[arg-type]


def test_ch_source_parse_row_valid():
    row = ClickHouseSentimentWindowSource.parse_row(("600519.SH", 0.42, 3, 1, 0, 4))
    assert row.symbol == "600519.SH"
    assert row.sentiment_index == pytest.approx(0.42)
    assert row.total_count == 4


def test_ch_source_symbol_whitelist():
    assert ClickHouseSentimentWindowSource.valid_symbol("600519.SH")
    assert not ClickHouseSentimentWindowSource.valid_symbol("600519.SH'; DROP TABLE--")
