# [A_test] module_id: MOD-GOV_evaluation_backtest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_evaluation_backtest
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_evaluation_backtest.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D-FACTOR-03 因子评估回测运行器测试——backtest.py。

覆盖：
- load_history: 空标的 / mock ch_reader / SQL 注入转义
- evaluate_factor: 空历史 / 完整流程 / 未注册因子
- EvaluationResult: frozen dataclass
- _format_symbols / _tsv_to_dataframe 私有辅助
"""

from __future__ import annotations

from io import StringIO

import pandas as pd
import pytest

backtest = pytest.importorskip("zephyr.factor.core.evaluation.backtest")
factor_base = pytest.importorskip("zephyr.factor.factor_base")

EvaluationResult = backtest.EvaluationResult
load_history = backtest.load_history
evaluate_factor = backtest.evaluate_factor
_format_symbols = backtest.format_symbols
_tsv_to_dataframe = backtest.tsv_to_dataframe

FactorBase = factor_base.FactorBase
FactorMeta = factor_base.FactorMeta
FactorRegistry = factor_base.FactorRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    FactorRegistry.clear()
    yield
    FactorRegistry.clear()


def _make_tsv(n_days: int = 20, symbols: list[str] | None = None) -> str:
    """构造合成日K TSV（无表头，9列，制表符分隔）。

    不同标的采用不同基础价和增量，确保因子值在截面上非常数（避免 spearman 退化）。
    """
    if symbols is None:
        symbols = ["600519.SH", "000001.SZ"]
    # 每个标的不同的基础价和日增量，保证 pct_change 在截面上有区分度
    base_map = {"600519.SH": 100.0, "000001.SZ": 50.0, "A.SH": 80.0, "B.SH": 60.0}
    incr_map = {"600519.SH": 0.8, "000001.SZ": 0.3, "A.SH": 0.5, "B.SH": 0.2}
    rows = []
    for sym in symbols:
        base = base_map.get(sym, 100.0)
        incr = incr_map.get(sym, 0.5)
        for i in range(n_days):
            date = f"2026-01-{i + 1:02d}"
            close = base + i * incr
            row = "\t".join(
                [
                    date,
                    sym,
                    str(close - 0.3),
                    str(close + 0.3),
                    str(close - 0.6),
                    str(close),
                    str(1000 + i * 10),
                    str(100000 + i * 1000),
                    "1.0",
                ]
            )
            rows.append(row)
    return "\n".join(rows) + "\n"


class TestFormatSymbols:
    def test_basic(self):
        assert _format_symbols(["A", "B"]) == "'A','B'"

    def test_empty(self):
        assert _format_symbols([]) == ""

    def test_filters_none(self):
        assert _format_symbols(["A", "", None, "B"]) == "'A','B'"

    def test_escape_quote(self):
        result = _format_symbols(["A'B"])
        assert "\\'" in result


class TestTsvToDataframe:
    def test_empty(self):
        assert _tsv_to_dataframe("").empty
        assert _tsv_to_dataframe("   ").empty

    def test_single_row(self):
        tsv = "2026-01-01\tA.SH\t100.0\t101.0\t99.0\t100.5\t1000\t100000\t1.0\n"
        df = _tsv_to_dataframe(tsv)
        assert len(df) == 1
        assert df["symbol"].iloc[0] == "A.SH"
        assert df["close"].iloc[0] == 100.5

    def test_trade_date_parsed_as_datetime(self):
        tsv = "2026-01-01\tA.SH\t100.0\t101.0\t99.0\t100.5\t1000\t100000\t1.0\n"
        df = _tsv_to_dataframe(tsv)
        assert pd.api.types.is_datetime64_any_dtype(df["trade_date"])


class TestLoadHistory:
    def test_empty_symbols(self):
        assert load_history([], "2026-01-01", "2026-01-31").empty

    def test_mock_ch_reader(self, monkeypatch):
        tsv = _make_tsv(n_days=10)
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv)
        df = load_history(["600519.SH", "000001.SZ"], "2026-01-01", "2026-01-10")
        assert not df.empty
        assert df.index.names == ["symbol", "trade_date"]
        assert "close" in df.columns

    def test_empty_result(self, monkeypatch):
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: "")
        df = load_history(["A.SH"], "2026-01-01", "2026-01-10")
        assert df.empty


class TestEvaluationResult:
    def test_frozen(self):
        r = EvaluationResult("f1", 0.1, 0.05, 2.0, 0.7, False, 10)
        with pytest.raises(Exception):
            r.factor_id = "f2"  # type: ignore[misc]

    def test_fields(self):
        r = EvaluationResult("f1", 0.1, 0.05, 2.0, 0.7, False, 10)
        assert r.factor_id == "f1"
        assert r.ic_mean == 0.1
        assert r.ir == 2.0
        assert r.is_overfitted is False
        assert r.sample_size == 10


class TestEvaluateFactorEmpty:
    def test_empty_history(self, monkeypatch):
        @FactorRegistry.register
        class TestFactor(FactorBase):
            meta = FactorMeta(factor_id="test_empty", name="Test", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: "")
        result = evaluate_factor("test_empty", ["A.SH"], "2026-01-01", "2026-01-31")
        assert result.factor_id == "test_empty"
        assert result.ic_mean == 0.0
        assert result.sample_size == 0
        assert result.is_overfitted is True


class TestEvaluateFactorFullFlow:
    def test_end_to_end(self, monkeypatch):
        @FactorRegistry.register
        class Momentum1d(FactorBase):
            meta = FactorMeta(factor_id="mom_1d", name="1d Momentum", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"].pct_change(1)

        # 20 天 × 2 标的，构造有明显动量效应的数据
        tsv = _make_tsv(n_days=20, symbols=["600519.SH", "000001.SZ"])
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv)

        result = evaluate_factor(
            "mom_1d",
            ["600519.SH", "000001.SZ"],
            "2026-01-01",
            "2026-01-20",
            horizon=1,
        )
        assert result.factor_id == "mom_1d"
        assert result.sample_size > 0
        # 数据单调递增，pct_change 恒正，IC 应为正
        assert result.ic_mean > 0

    def test_unregistered_factor_raises(self, monkeypatch):
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: _make_tsv())
        with pytest.raises(KeyError):
            evaluate_factor("nonexistent", ["A.SH"], "2026-01-01", "2026-01-10")

    def test_horizon_drops_tail(self, monkeypatch):
        @FactorRegistry.register
        class FlatFactor(FactorBase):
            meta = FactorMeta(factor_id="flat", name="Flat", domain="technical")

            def compute(self, data, **kwargs):
                return pd.Series(1.0, index=data.index)

        tsv = _make_tsv(n_days=10, symbols=["A.SH", "B.SH"])
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv)
        result = evaluate_factor("flat", ["A.SH", "B.SH"], "2026-01-01", "2026-01-10", horizon=3)
        # horizon=3 应丢掉尾部 3 天，sample_size <= 7
        assert result.sample_size <= 7


class TestEvaluateFactorOosRatio:
    def test_custom_oos_ratio(self, monkeypatch):
        @FactorRegistry.register
        class MomFactor(FactorBase):
            meta = FactorMeta(factor_id="mom_test", name="Mom", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"].pct_change(1)

        tsv = _make_tsv(n_days=20, symbols=["600519.SH", "000001.SZ"])
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv)
        r1 = evaluate_factor("mom_test", ["600519.SH", "000001.SZ"], "2026-01-01", "2026-01-20", oos_ratio=0.3)
        r2 = evaluate_factor("mom_test", ["600519.SH", "000001.SZ"], "2026-01-01", "2026-01-20", oos_ratio=0.5)
        # 不同 OOS 比例不应崩
        assert isinstance(r1.oos_positive_rate, float)
        assert isinstance(r2.oos_positive_rate, float)
        assert 0.0 <= r1.oos_positive_rate <= 1.0


def _make_ex_dividend_tsv() -> str:
    """构造含除权日的单标的 TSV（tracker #197 回归场景）。

    10送10 除权：close 从 20 腰斩到 10，乘法口径复权因子从 1 上台阶到 2
    （QMT dr / 新浪 hfq 均为 adj_close = close × adj_factor 乘法口径，
    除权日因子上台阶），真实持有收益应为 0，而非 raw close 口径的 -50%。
    """
    rows = []
    closes = [20.0, 20.0, 20.0, 10.0, 10.0, 10.0]
    factors = [1.0, 1.0, 1.0, 2.0, 2.0, 2.0]
    for i, (close, factor) in enumerate(zip(closes, factors)):
        date = f"2026-01-{i + 1:02d}"
        rows.append(
            "\t".join(
                [
                    date,
                    "A.SH",
                    str(close - 0.3),
                    str(close + 0.3),
                    str(close - 0.6),
                    str(close),
                    "1000",
                    "100000",
                    str(factor),
                ]
            )
        )
    return "\n".join(rows) + "\n"


class TestForwardReturnsAdjusted:
    """tracker #197 回归：前向收益按复权价（close × adj_factor）计算。"""

    def _load(self, monkeypatch, tsv: str) -> pd.DataFrame:
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv)
        return load_history(["A.SH"], "2026-01-01", "2026-01-06")

    def test_ex_dividend_forward_return_near_zero(self, monkeypatch):
        """除权日 10送10：复权前向收益 ≈ 0，而非 raw close 口径的 -50%。"""
        history = self._load(monkeypatch, _make_ex_dividend_tsv())
        adj_panel = backtest._adjusted_close_panel(history)
        returns = backtest._compute_forward_returns(adj_panel, horizon=1)["A.SH"].dropna()
        # 除权日截面（01-03 → 01-04）：close 20→10 但因子 1→2，真实收益 0
        assert returns.loc[pd.Timestamp("2026-01-03")] == pytest.approx(0.0, abs=1e-12)
        # 平台期价格不变，收益亦为 0
        assert (returns.abs() < 1e-12).all()

    def test_raw_close_would_report_minus_50pct(self, monkeypatch):
        """对照组：未复权口径下同一除权日被计为 -50%（证明修复必要性）。"""
        history = self._load(monkeypatch, _make_ex_dividend_tsv())
        raw_panel = history["close"].unstack(level="symbol")
        raw_returns = backtest._compute_forward_returns(raw_panel, horizon=1)["A.SH"]
        assert raw_returns.loc[pd.Timestamp("2026-01-03")] == pytest.approx(-0.5)

    def test_adj_factor_null_and_zero_fallback_to_one(self, monkeypatch):
        """adj_factor 缺失(NULL)/0 → 回退 1.0，该行复权价退化为 raw close。"""
        rows = [
            "2026-01-01\tA.SH\t19.7\t20.3\t19.4\t20.0\t1000\t100000\t\\N",
            "2026-01-02\tA.SH\t21.7\t22.3\t21.4\t22.0\t1000\t100000\t0",
            "2026-01-03\tA.SH\t23.7\t24.3\t23.4\t24.0\t1000\t100000\t1.5",
        ]
        history = self._load(monkeypatch, "\n".join(rows) + "\n")
        adj_close = backtest._adjusted_close_panel(history)["A.SH"]
        # NULL → ×1.0（退化为不复权价）
        assert adj_close.loc[pd.Timestamp("2026-01-01")] == pytest.approx(20.0)
        # 0（无效因子，裁定#ARCH-ADJFACTOR-NULL-001）→ ×1.0
        assert adj_close.loc[pd.Timestamp("2026-01-02")] == pytest.approx(22.0)
        # 正常因子 ×1.5 生效
        assert adj_close.loc[pd.Timestamp("2026-01-03")] == pytest.approx(36.0)

    def test_evaluate_factor_end_to_end_with_ex_dividend(self, monkeypatch):
        """端到端：含除权日数据跑 evaluate_factor 不崩且产出有效截面。"""

        @FactorRegistry.register
        class CloseFactor(FactorBase):
            meta = FactorMeta(factor_id="close_f197", name="Close", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"].pct_change(1)

        tsv_a = _make_ex_dividend_tsv()
        # 第二标的：平稳上涨，保证截面 IC 可计算
        tsv_b = _make_tsv(n_days=6, symbols=["B.SH"])
        monkeypatch.setattr(backtest.ch_reader, "query", lambda sql, timeout=30: tsv_a + tsv_b)
        result = evaluate_factor(
            "close_f197",
            ["A.SH", "B.SH"],
            "2026-01-01",
            "2026-01-06",
            horizon=1,
        )
        assert result.factor_id == "close_f197"
        assert result.sample_size > 0
