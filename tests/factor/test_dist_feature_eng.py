# [A_test] module_id: MOD-GOV_dist_feature_eng | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_dist_feature_eng
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_dist_feature_eng.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D_FACTOR core dist_feature_eng 测试——engine.py。

覆盖：
- DistEngConfig 默认值
- compute_factor_for_symbol 纯函数
- DistributedFeatureEngine.execute：单进程退化（max_workers=1）/ 跨标的 panel 组装
- 因子未注册处理
- 非 MultiIndex 输入抛 ValueError
- backpressure 集成
"""

from __future__ import annotations

import pandas as pd
import pytest

engine_mod = pytest.importorskip("zephyr.factor.core.dist_feature_eng.engine")
dag_mod = pytest.importorskip("zephyr.factor.core.factor_dag.dag")
factor_base = pytest.importorskip("zephyr.factor.factor_base")
bp_mod = pytest.importorskip("zephyr.factor.core.backpressure.limiter")

DistEngConfig = engine_mod.DistEngConfig
DistEngResult = engine_mod.DistEngResult
DistributedFeatureEngine = engine_mod.DistributedFeatureEngine
compute_factor_for_symbol = engine_mod.compute_factor_for_symbol

FactorDAG = dag_mod.FactorDAG
FactorNode = dag_mod.FactorNode
build_dag_from_registry = dag_mod.build_dag_from_registry

FactorBase = factor_base.FactorBase
FactorMeta = factor_base.FactorMeta
FactorRegistry = factor_base.FactorRegistry

BackpressureLimiter = bp_mod.BackpressureLimiter
BackpressureConfig = bp_mod.BackpressureConfig


@pytest.fixture(autouse=True)
def clear_registry():
    FactorRegistry.clear()
    yield
    FactorRegistry.clear()


def _register_factor(fid: str, deps: list[str] | None = None) -> None:
    """注册一个简单因子（返回 close 列）。"""

    class _Factor(FactorBase):
        meta = FactorMeta(factor_id=fid, name=fid, domain="test", dependencies=deps or [])

        def compute(self, data, **kwargs):
            return data["close"]

    FactorRegistry.register(_Factor)


def _make_multiindex_data(
    symbols: list[str] | None = None,
    n_days: int = 5,
) -> pd.DataFrame:
    """构造 MultiIndex (symbol, trade_date) 行情数据。"""
    if symbols is None:
        symbols = ["600519.SH", "000001.SZ"]
    rows = []
    for sym in symbols:
        for i in range(n_days):
            rows.append(
                {
                    "symbol": sym,
                    "trade_date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=i),
                    "open": 99.0 + i,
                    "high": 101.0 + i,
                    "low": 98.0 + i,
                    "close": 100.0 + i,
                    "volume": 1000 + i,
                }
            )
    df = pd.DataFrame(rows)
    df["symbol"] = df["symbol"].astype(str)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df.set_index(["symbol", "trade_date"]).sort_index()


class TestDistEngConfig:
    def test_defaults(self) -> None:
        cfg = DistEngConfig()
        assert cfg.max_workers == 4
        assert cfg.factor_timeout_s == 120.0


class TestComputeFactorForSymbol:
    def test_success(self) -> None:
        _register_factor("test_factor")
        data = pd.DataFrame(
            {"close": [100.0, 101.0, 102.0]},
            index=pd.date_range("2026-01-01", periods=3, freq="D"),
        )
        sym, fid, series, error = compute_factor_for_symbol("test_factor", "TEST", data)
        assert sym == "TEST"
        assert fid == "test_factor"
        assert error == ""
        assert series is not None
        assert len(series) == 3

    def test_unregistered_factor(self) -> None:
        data = pd.DataFrame(
            {"close": [100.0]},
            index=pd.date_range("2026-01-01", periods=1, freq="D"),
        )
        sym, fid, series, error = compute_factor_for_symbol("nope", "TEST", data)
        assert series is None
        assert "not registered" in error


class TestDistributedFeatureEngineSingleProcess:
    """max_workers=1 退化为串行（仍走 ProcessPoolExecutor）。"""

    def test_single_factor_single_symbol(self) -> None:
        _register_factor("f1")
        dag = build_dag_from_registry(["f1"], dag_id="t")
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1))
        data = _make_multiindex_data(symbols=["A.SH"])
        results = engine.execute(dag, data)
        assert "f1" in results
        assert isinstance(results["f1"], DistEngResult)
        assert not results["f1"].panel.empty
        assert results["f1"].failed_symbols == []

    def test_single_factor_multiple_symbols(self) -> None:
        _register_factor("f1")
        dag = build_dag_from_registry(["f1"], dag_id="t")
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1))
        data = _make_multiindex_data(symbols=["A.SH", "B.SH", "C.SH"])
        results = engine.execute(dag, data)
        assert "f1" in results
        panel = results["f1"].panel
        assert set(panel.columns) == {"A.SH", "B.SH", "C.SH"}
        assert len(panel) == 5  # 5 天

    def test_two_layer_dag(self) -> None:
        _register_factor("f1")
        _register_factor("f2", deps=["f1"])
        dag = build_dag_from_registry(["f1", "f2"], dag_id="t")
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1))
        data = _make_multiindex_data()
        results = engine.execute(dag, data)
        assert "f1" in results
        assert "f2" in results
        assert not results["f1"].panel.empty
        assert not results["f2"].panel.empty


class TestNonMultiIndexInput:
    def test_flat_index_raises(self) -> None:
        _register_factor("f1")
        dag = build_dag_from_registry(["f1"], dag_id="t")
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1))
        bad_data = pd.DataFrame({"close": [100.0]}, index=[0])
        with pytest.raises(ValueError, match="MultiIndex"):
            engine.execute(dag, bad_data)

    def test_wrong_multiindex_names_raises(self) -> None:
        _register_factor("f1")
        dag = build_dag_from_registry(["f1"], dag_id="t")
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1))
        # MultiIndex 但 names 不含 symbol/trade_date
        bad_data = pd.DataFrame(
            {"close": [100.0]},
            index=pd.MultiIndex.from_tuples([("a", 1)], names=["x", "y"]),
        )
        with pytest.raises(ValueError, match="symbol"):
            engine.execute(dag, bad_data)


class TestBackpressureIntegration:
    def test_paused_backpressure_skips_all_symbols(self) -> None:
        """backpressure PAUSED → 所有标的 acquire 失败 → panel 为空。"""
        _register_factor("f1")
        dag = build_dag_from_registry(["f1"], dag_id="t")
        bp = BackpressureLimiter(BackpressureConfig(max_inflight=1))
        bp.pause()
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1), backpressure=bp)
        data = _make_multiindex_data()
        results = engine.execute(dag, data)
        # 所有标的被拒绝 → panel 空
        assert results["f1"].panel.empty

    def test_normal_backpressure_executes(self) -> None:
        _register_factor("f1")
        dag = build_dag_from_registry(["f1"], dag_id="t")
        bp = BackpressureLimiter(BackpressureConfig(max_inflight=4))
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1), backpressure=bp)
        data = _make_multiindex_data()
        results = engine.execute(dag, data)
        assert not results["f1"].panel.empty


class TestUnregisteredFactorInEngine:
    def test_unregistered_factor_yields_empty_panel(self) -> None:
        """因子未注册 → 所有标的失败 → panel 空 + failed_symbols 含全部标的。"""
        # 手动构造 DAG 绕过 build_dag_from_registry 的注册检查
        dag = FactorDAG(dag_id="t")
        dag.add_node(FactorNode(factor_id="nonexistent"))
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1))
        data = _make_multiindex_data(symbols=["A.SH", "B.SH"])
        results = engine.execute(dag, data)
        assert results["nonexistent"].panel.empty
        assert sorted(results["nonexistent"].failed_symbols) == ["A.SH", "B.SH"]


class TestPanelAssembly:
    def test_panel_index_aligned(self) -> None:
        """panel 的 index 应对齐 trade_date。"""
        _register_factor("f1")
        dag = build_dag_from_registry(["f1"], dag_id="t")
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1))
        data = _make_multiindex_data(symbols=["A.SH", "B.SH"], n_days=3)
        results = engine.execute(dag, data)
        panel = results["f1"].panel
        assert len(panel) == 3
        assert set(panel.columns) == {"A.SH", "B.SH"}

    def test_duration_recorded(self) -> None:
        _register_factor("f1")
        dag = build_dag_from_registry(["f1"], dag_id="t")
        engine = DistributedFeatureEngine(DistEngConfig(max_workers=1))
        data = _make_multiindex_data()
        results = engine.execute(dag, data)
        assert results["f1"].duration_s >= 0.0
