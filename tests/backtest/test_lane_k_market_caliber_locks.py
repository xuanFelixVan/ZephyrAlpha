# [A_test] module_id: MOD-GOV_lane_k_locks | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §test
# [MODULE] tests.backtest.test_lane_k_market_caliber_locks
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_lane_k_market_caliber_locks.py
# [TTL] task_bound
"""车道 K（task #21 / H1-P0）量纲 + 复权治本回归锁。

三侧同锁（缺一不可，否则修复可被静默回退）：
1. **入口侧**（`factor.core.evaluation.backtest.load_history`）：
   混存量纲逐行归一、后复权真值接通、告警非静默、A/B 复现开关 `normalize_units=False`；
2. **撮合侧**（`backtest.core.matching_engine`）：参与率上限按**股**计（P0-1 的
   病灶是 100× 过严），且引擎自身对量纲无感——只有入口守住 INV-UNIT-001 才对；
3. **绝对价侧**（P0-2 配套）：价格序列被复权乘子缩放后，涨跌停判定必须**缩放不变**
   （否则送转股被判为永久封板，所有卖单被拒——修一个 P0 造一个新 P0）。
"""

from __future__ import annotations

import logging
from decimal import Decimal

import pandas as pd
import pytest

from zephyr.backtest.core.matching_engine import (
    LimitInfo,
    LiquidityGuardConfig,
    MatchingConfig,
    MatchingEngine,
)
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.factor.core.evaluation import backtest as bt
from zephyr.shared.utils.market_units import REPORT_ATTR

D = Decimal

_DATE_FMT = "%Y-%m-%d"


def _hist_tsv(rows: list[tuple]) -> str:
    """9 列无表头 TSV（ch_reader 真实返回形态）：date sym o h l c vol amount adj。"""
    return "".join(
        "\t".join([d, sym, str(o), str(h), str(l), str(c), str(v), str(a), adj]) + "\n"
        for d, sym, o, h, l, c, v, a, adj in rows
    )


def _hfq_tsv(rows: list[tuple[str, str, float]]) -> str:
    """3 列无表头 TSV：date sym hfq_close。"""
    return "".join(f"{d}\t{s}\t{c}\n" for d, s, c in rows)


def _mixed_market() -> tuple[list[tuple], list[tuple[str, str, float]]]:
    """两标的 4 交易日：600519 主进料=手，000001 tushare=股；后复权=原价（无除权）。

    日量（真实股）：600519 1,000,000 股 / 000001 2,000,000 股；价格恒定 10 元。
    """
    dates = pd.bdate_range("2026-08-03", periods=4).strftime(_DATE_FMT).tolist()
    hist = []
    for d in dates:
        # 600519：volume 手（10000 手 = 1e6 股），amount = 10 × 1e6 = 1e7 元
        hist.append((d, "600519", 10.0, 10.2, 9.8, 10.0, 10000, 10_000_000.0, "1.0"))
        # 000001：volume 股（写入侧已 ×100），amount = 10 × 2e6 = 2e7 元
        hist.append((d, "000001", 10.0, 10.2, 9.8, 10.0, 2_000_000, 20_000_000.0, "1.0"))
    hfq = [(d, "600519", 10.0) for d in dates] + [(d, "000001", 10.0) for d in dates]
    return hist, hfq


def _patch_ch(monkeypatch, hist_rows, hfq_rows, *, calls=None):
    """按 SQL 分派的 ch_reader.query mock（后复权表名命中→3 列，否则→9 列）。"""

    def _query(sql, timeout=30):
        hfq_table = bt._TBL_KLINE_DAILY_HFQ
        if hfq_table in sql:
            if calls is not None:
                calls.append("hfq")
            return _hfq_tsv(hfq_rows)
        if calls is not None:
            calls.append("raw")
        return _hist_tsv(hist_rows)

    monkeypatch.setattr(bt.ch_reader, "query", _query)
    return _query


def _to_engine_data(history: pd.DataFrame) -> pd.DataFrame:
    """load_history 出口 → DefaultBacktestEngine 入参形态（同 StrategyRunner）。"""
    data = history.copy()
    if isinstance(data.index, pd.MultiIndex):
        data.index = data.index.rename({"trade_date": "date"})
    return data


class TestLoaderCaliberLock:
    """入口侧：load_history 出口口径 =「volume 股 / 价格复权连续 / amount 元」。"""

    def test_mixed_volume_units_normalized_per_row(self, monkeypatch):
        hist, hfq = _mixed_market()
        _patch_ch(monkeypatch, hist, hfq)
        out = bt.load_history(["600519.SH", "000001.SZ"], "2026-08-03", "2026-08-06")
        syms = out.index.get_level_values("symbol")
        # P0-1 核心：手腿 ×100、股腿不变——单一全局 ×100 会把股腿错 100 倍
        assert out.loc[syms == "600519", "volume"].unique().tolist() == [1_000_000.0]
        assert out.loc[syms == "000001", "volume"].unique().tolist() == [2_000_000.0]
        # 源表原值可追溯（真实价/原始量语义留痕，供涨跌停与审计用）
        assert out.loc[syms == "600519", "volume_lots"].unique().tolist() == [10000.0]
        report = out.attrs[REPORT_ATTR]
        assert report.volume.suspect is False
        assert report.volume.counts_by_multiplier == {1.0: 4, 100.0: 4}

    def test_amount_close_volume_invariant_after_normalize(self, monkeypatch):
        hist, hfq = _mixed_market()
        _patch_ch(monkeypatch, hist, hfq)
        out = bt.load_history(["600519.SH", "000001.SZ"], "2026-08-03", "2026-08-06")
        ratio = out["amount"] / (out["close"] * out["volume"])
        assert abs(float(ratio.median()) - 1.0) < 1e-6  # 归一后自洽绊线必须 ≈1

    def test_adjustment_source_wired_and_hfq_identity(self, monkeypatch):
        """P0-2：adj_factor 不再恒 1（接通 hfq 真值），close×adj_factor ≡ 后复权价。"""
        hist, hfq = _mixed_market()
        _patch_ch(monkeypatch, hist, hfq)
        out = bt.load_history(["600519.SH", "000001.SZ"], "2026-08-03", "2026-08-06")
        report = out.attrs[REPORT_ATTR]
        assert report.adjustment_enabled is True
        assert (out["close"] * out["adj_factor"]).tolist() == [10.0] * 8

    def test_ex_dividend_phantom_removed_end_to_end(self, monkeypatch):
        """现网口径：600519 中途 10送10（raw 20→10），复权后前向收益不再有 -50% 幻影。"""
        dates = pd.bdate_range("2026-08-03", periods=4).strftime(_DATE_FMT).tolist()
        hist = []
        for i, d in enumerate(dates):
            c = 20.0 if i < 2 else 10.0
            lots = 1000.0 if i < 2 else 2000.0  # 送转后股数翻倍（手口径）
            hist.append((d, "600519", c * 1.01, c * 1.02, c * 0.98, c, lots, 2_000_000.0, "1.0"))
        hfq = [(d, "600519", 20.0) for d in dates]  # 后复权恒 20（真实总收益 0）
        _patch_ch(monkeypatch, hist, hfq)
        out = bt.load_history(["600519.SH"], "2026-08-03", "2026-08-06")
        panel = bt._adjusted_close_panel(out)
        rets = bt._compute_forward_returns(panel, 1)["600519"].dropna()
        assert (rets.abs() < 1e-12).all(), f"除权幻影未消除: {rets.tolist()}"
        # 对照组：raw close 同日必判 -50%
        raw_panel = out["close_raw"].unstack(level="symbol")
        assert bt._compute_forward_returns(raw_panel, 1)["600519"].iloc[1] == pytest.approx(-0.5)

    def test_warns_loudly_when_adjustment_source_missing(self, monkeypatch, caplog):
        """无 hfq 行 → 必须 WARNING 点名"未复权/幻影未修"，不得静默按 raw 算。"""
        hist, _ = _mixed_market()
        _patch_ch(monkeypatch, hist, [])
        with caplog.at_level(logging.WARNING, logger="zephyr.factor.core.evaluation.backtest"):
            out = bt.load_history(["600519.SH"], "2026-08-03", "2026-08-06")
        assert out.attrs[REPORT_ATTR].adjustment_enabled is False
        assert any("未复权" in r.getMessage() for r in caplog.records), caplog.text

    def test_warns_when_volume_caliber_undecidable(self, monkeypatch, caplog):
        """量纲不可判定（amount 与两种量纲都不自洽）→ suspect + WARNING（不静默）。"""
        dates = pd.bdate_range("2026-08-03", periods=2).strftime(_DATE_FMT).tolist()
        hist = [(d, "600519", 10.0, 10.2, 9.8, 10.0, 1000, 5_000_000.0, "1.0") for d in dates]
        _patch_ch(monkeypatch, hist, [(d, "600519", 10.0) for d in dates])
        with caplog.at_level(logging.WARNING, logger="zephyr.factor.core.evaluation.backtest"):
            out = bt.load_history(["600519.SH"], "2026-08-03", "2026-08-04")
        assert out.attrs[REPORT_ATTR].volume.suspect is True
        assert any("量纲" in r.getMessage() for r in caplog.records), caplog.text

    def test_normalize_units_false_reproduces_legacy_caliber(self, monkeypatch):
        """A/B 开关：False 逐位复现修复前口径（volume 混存 + raw 价），供现网对照复验。"""
        hist, hfq = _mixed_market()
        _patch_ch(monkeypatch, hist, hfq)
        legacy = bt.load_history(
            ["600519.SH", "000001.SZ"], "2026-08-03", "2026-08-06", normalize_units=False
        )
        syms = legacy.index.get_level_values("symbol")
        assert legacy.loc[syms == "600519", "volume"].unique().tolist() == [10000]  # 手
        assert "close_raw" not in legacy.columns
        assert (legacy["adj_factor"] == 1.0).all()

    def test_hfq_tsv_parser_rejects_misshapen_rows(self):
        """严格字段数校验：9 列 raw 行/NULL/非正价一律丢弃（错位数据不当复权真值）。"""
        bad = _hist_tsv([("2026-08-03", "600519", 10.0, 10.2, 9.8, 10.0, 1, 1.0, "1.0")])
        good = "2026-08-03\t600519\t11.0\n2026-08-04\t600519\t\\N\n2026-08-05\t600519\t0\n"
        parsed = bt._parse_adjusted_close_tsv(bad + good)
        assert list(parsed.index.get_level_values("trade_date")) == [pd.Timestamp("2026-08-03")]
        assert parsed["close"].iloc[0] == 11.0
        assert bt._parse_adjusted_close_tsv("").empty
        assert bt._parse_adjusted_close_tsv(bad).empty


class TestMatchingEngineParticipationCaliber:
    """撮合侧：上限按"股"计；引擎对量纲无感，故入口必须归一（P0-1 病灶 100× 过严）。"""

    def _engine(self, **overrides):
        cfg = dict(
            initial_capital=D("1000000"),
            sanity_guard=False,
            enable_pit_universe_filter=False,
        )
        cfg.update(overrides)
        return DefaultBacktestEngine(
            config=BacktestConfig(**cfg), enable_stk_limit_provider=False
        )

    @staticmethod
    def _data(volumes, closes=(10.0, 10.0), symbol="600000"):
        dates = pd.bdate_range("2026-08-03", periods=len(closes))
        return pd.DataFrame(
            {
                "symbol": [symbol] * len(closes),
                "date": dates,
                "close": list(closes),
                "volume": volumes,
            }
        )

    @staticmethod
    def _signal(value=1.0, n=2, symbol="600000"):
        dates = pd.bdate_range("2026-08-03", periods=n)
        return pd.DataFrame({symbol: [value] + [None] * (n - 1)}, index=dates)

    def test_cap_binds_on_shares_not_lots(self):
        """日量 20 万股 → 上限 2 万股（10%）；同源数据若按"手"喂入只剩 200 股。"""
        eng_shares = self._engine()
        shares = eng_shares.run(
            data=self._data([1_000_000.0, 200_000.0]), signals=self._signal()
        )
        assert shares.trades_count == 1
        qty_shares = D(str(eng_shares.last_portfolio.trades_log[0]["quantity"]))
        assert qty_shares == D("20000")  # 20 万股 ×10%

        eng_lots = self._engine()
        lots = eng_lots.run(
            data=self._data([10_000.0, 2_000.0]), signals=self._signal()
        )
        qty_lots = D(str(eng_lots.last_portfolio.trades_log[0]["quantity"]))
        assert qty_lots == D("200")  # 2000 手 ×10% —— 真实参与率被压到 0.1%（P0-1 病灶）
        assert qty_shares / qty_lots == D("100")

    def test_loader_output_satisfies_engine_contract(self, monkeypatch):
        """入口归一后的面板喂引擎：真实参与率 >1%（H1-A 微缩版），且 ≤ 上限 10%。"""
        hist, hfq = _mixed_market()
        _patch_ch(monkeypatch, hist, hfq)
        normalized = _to_engine_data(
            bt.load_history(["600519.SH", "000001.SZ"], "2026-08-03", "2026-08-06")
        )
        legacy = _to_engine_data(
            bt.load_history(
                ["600519.SH", "000001.SZ"], "2026-08-03", "2026-08-06", normalize_units=False
            )
        )
        dates = pd.bdate_range("2026-08-03", periods=4)
        signals = pd.DataFrame(0.5, index=dates, columns=["600519", "000001"])
        signals.iloc[1:] = None

        def _participation_by_symbol(data, vol_ref=None):
            """真实参与率 = 成交量 / **真实股本量纲日量**，逐标的取最差。

            vol_ref 缺省用 data 自身；A/B 的 legacy 腿必须显式传归一后的面板，
            否则分母跟着分子一起被"手"缩小 100 倍，比值恒等于引擎上限 10%，
            P0-1 的 100× 低估就被这个自洽假象抹平了。

            逐标的而非合并：混存面板里 600519 是手量纲（病灶腿）、000001 本就是
            股量纲（健康腿），合并取 max 会让健康腿掩盖病灶腿被钉死的事实。
            """
            ref = data if vol_ref is None else vol_ref
            engine = self._engine()
            res = engine.run(data=data, signals=signals)
            worst: dict[str, Decimal] = {}
            for tr in engine.last_portfolio.trades_log:
                day_vol = ref.xs(tr["date"], level="date").loc[tr["symbol"], "volume"]
                ratio = D(str(tr["quantity"])) / D(str(day_vol))
                worst[tr["symbol"]] = max(worst.get(tr["symbol"], D("0")), ratio)
            return res.trades_count, worst

        n_new, r_new = _participation_by_symbol(normalized)
        n_old, r_old = _participation_by_symbol(legacy, vol_ref=normalized)
        assert n_new > 0 and n_old > 0
        for sym in ("600519", "000001"):
            assert D("0.01") < r_new[sym] <= D("0.10") + D("0.0001"), (
                f"归一后 {sym} 真实参与率不在合理带: {r_new[sym]}"
            )  # H1-A
        assert r_old["600519"] < D("0.0011"), (
            f"legacy 腿不再复现 0.1% 钉死，A/B 失效: {r_old['600519']}"
        )
        assert abs(r_old["000001"] - r_new["000001"]) / r_new["000001"] < D("0.02"), (
            f"归一误伤本已正确的股量纲标的: {r_old['000001']} vs {r_new['000001']}"
            "（容差 2% 只吃整手取整与另一腿资金占用的二阶差，不吃量纲）"
        )


class TestLimitBoundsScaleInvariance:
    """绝对价侧：复权缩放后涨跌停判定不变（P0-2 配套，防"修一处坏一处"）。"""

    @staticmethod
    def _engine():
        return MatchingEngine(config=MatchingConfig(), liquidity_config=None)

    @staticmethod
    def _row(up, down, pct=None):
        return LimitInfo(
            limit_up=D(up), limit_down=D(down),
            limit_pct=None if pct is None else D(pct),
            from_table=True,
        )

    def test_same_caliber_uses_table_absolute_prices(self):
        """引擎价与表价同纲（k=1）→ 直用表内精确价（#ARCH-DATA-020 链路 1 不变）。"""
        eng = self._engine()
        lm = {"600000": self._row("11.00", "9.00")}
        assert eng._limit_bounds("600000", None, D("10.00"), lm) == (D("11.00"), D("9.00"))
        assert eng._is_limit_up("600000", D("11.00"), D("10.00"), None, lm) is True
        assert eng._is_limit_down("600000", D("10.00"), D("10.00"), None, lm) is False

    def test_rescaled_series_does_not_freeze_sells(self):
        """k=0.5（送转复权空间）普通日：修复前 5.0 < 表跌停 9.0 → 误判永久封板。"""
        eng = self._engine()
        lm = {"600000": self._row("11.00", "9.00", "0.10")}
        bounds = eng._limit_bounds("600000", None, D("5.00"), lm)
        assert bounds == (D("5.50"), D("4.50"))  # 收益空间等价式
        assert eng._is_limit_down("600000", D("5.00"), D("5.00"), None, lm) is False
        assert eng._is_limit_up("600000", D("5.00"), D("5.00"), None, lm) is False

    def test_rescaled_series_still_detects_real_limit_down(self):
        """k=0.5 且当日真跌停（引擎价 4.5 = 9.0×0.5）→ 仍判封板（卖单拒成）。"""
        eng = self._engine()
        lm = {"600000": self._row("11.00", "9.00", "0.10")}
        assert eng._is_limit_down("600000", D("4.50"), D("5.00"), None, lm) is True

    def test_scaling_leaves_classification_unchanged(self):
        """缩放不变性总检验：同一批价格在 k 与 1 两套空间下判定逐位一致。"""
        eng = self._engine()
        lm = {"600000": self._row("11.00", "9.00", "0.10")}
        lm_half = {"600000": lm["600000"] if False else self._row("11.00", "9.00", "0.10")}
        for raw_price in ("8.90", "9.00", "9.80", "10.00", "10.90", "11.00", "11.20"):
            base_up = eng._is_limit_up("600000", D(raw_price), D("10.00"), None, lm)
            base_dn = eng._is_limit_down("600000", D(raw_price), D("10.00"), None, lm)
            scaled_up = eng._is_limit_up(
                "600000", D(raw_price) / D("2"), D("5.00"), None, lm_half
            )
            scaled_dn = eng._is_limit_down(
                "600000", D(raw_price) / D("2"), D("5.00"), None, lm_half
            )
            assert base_up == scaled_up, raw_price
            assert base_dn == scaled_dn, raw_price

    def test_row_without_pct_scales_table_prices(self):
        """表行无 limit_pct（异形板）→ 按 prev_close/参考价 缩放表价，不丢不对称性。"""
        eng = self._engine()
        lm = {"600000": self._row("12.00", "8.00")}  # 参考 midpoint=10，无 pct
        assert eng._limit_bounds("600000", None, D("5.00"), lm) == (D("6.00"), D("4.00"))

    def test_no_limit_row_keeps_rule_chain(self):
        """非表行（规则兜底）路径不受影响：仍按 prev_close×(1±pct) 重算。"""
        eng = self._engine()
        lm = {"600000": LimitInfo(limit_pct=D("0.10"), from_table=False)}
        assert eng._limit_bounds("600000", None, D("10.00"), lm) == (D("11.00"), D("9.00"))

    def test_null_row_means_no_clamp(self):
        """表行 limit_*=NULL（新股无涨跌幅限制）→ None（不封板）。"""
        eng = self._engine()
        lm = {"301999": LimitInfo(limit_up=None, limit_down=None, limit_pct=None, from_table=True)}
        assert eng._limit_bounds("301999", None, D("10.00"), lm) is None

    def test_impact_bypass_is_noisy_not_silent(self, caplog):
        """参与率越界（p>1，疑量纲违例）→ 显式 WARNING 点名 INV-UNIT-001 违例。"""
        eng = MatchingEngine(
            config=MatchingConfig(),
            liquidity_config=__import__(
                "zephyr.backtest.core.matching_engine", fromlist=["LiquidityGuardConfig"]
            ).LiquidityGuardConfig(max_participation_rate=D("2.0"), impact_enabled=True),
        )
        from zephyr.backtest.core.matching_logic import OrderBookSnapshot

        ob = OrderBookSnapshot(
            symbol="600000",
            ask_price=(D("10"),) * 5,
            bid_price=(D("10"),) * 5,
            ask_vol=(D("1000"),) * 5,
            bid_vol=(D("1000"),) * 5,
            last_price=D("10"),
            timestamp=None,
        )
        with caplog.at_level(logging.WARNING, logger="zephyr.backtest.core.matching_engine"):
            eng._apply_impact_to_books(
                [{"side": "BUY", "symbol": "600000", "quantity": D("5000")}],
                {"600000": ob},
                {"600000": D("1000")},
            )
        msgs = " ".join(r.getMessage() for r in caplog.records)
        assert "INV-UNIT-001" in msgs, msgs
