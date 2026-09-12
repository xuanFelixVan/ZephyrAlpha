# [BLUEPRINT] MOD-SIG-127 | docs/03_modules/_domain_signal/causal_ml_engine/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-127 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_causal_ml_engine
# [TESTS] src/zephyr/signal_ashare/causal_ml_engine.py
"""MOD-SIG-127 单元测试：causal_ml_engine 因果ML引擎。

蓝图验收（B10-01858/CAND-TESTB-051，A1 §29.18；承接 TESTB-035/047 归并）：
DML/CausalForest/DoWhy证伪/PC-LiNGAM发现四通道全注入（未注入/异常/产出非法
一律降级标记不阻断）+ 盘前预计算因果图缓存（按数据指纹失效）+ 效应显著性
筛选（|效应|>阈值 且 p<0.05，严格不等号）。runner 全内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.causal_ml_engine",
    reason="causal_ml_engine not importable",
)

from zephyr.signal_ashare.causal_ml_engine import (  # noqa: E402
    CausalChannel,
    CausalEffect,
    CausalMlEngine,
    CausalMlError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_VARS = ("momentum", "value", "size")
_EDGES = (("momentum", "return"), ("value", "return"))


def _ok_runner(effect: float = 0.12, p_value: float = 0.01, n: int = 240):
    return lambda t, o, ctx: {"effect": effect, "p_value": p_value, "n_samples": n}


def _discovery_runner(edges=_EDGES):
    return lambda fp, variables, ctx: {"edges": edges}


def _engine(**kwargs) -> CausalMlEngine:
    kwargs.setdefault("clock", lambda: _T0)
    return CausalMlEngine(**kwargs)


def _full_engine() -> CausalMlEngine:
    return _engine(
        dml_runner=_ok_runner(0.12, 0.01),
        causal_forest_runner=_ok_runner(0.08, 0.03),
        dowhy_runner=_ok_runner(0.20, 0.001),
        discovery_runner=_discovery_runner(),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造期 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_effect_threshold_negative_raises(self) -> None:
        with pytest.raises(CausalMlError):
            _engine(effect_threshold=-0.1)

    def test_effect_threshold_nan_raises(self) -> None:
        with pytest.raises(CausalMlError):
            _engine(effect_threshold=float("nan"))

    def test_p_value_threshold_out_of_range_raises(self) -> None:
        for bad in (0.0, 1.0, -0.05, float("nan")):
            with pytest.raises(CausalMlError):
                _engine(p_value_threshold=bad)


# ──────────────────────────────────────────────────────────────────────────────
# 单通道效应估计（降级不阻断）
# ──────────────────────────────────────────────────────────────────────────────


class TestEstimateEffect:
    def test_dml_ok(self) -> None:
        eng = _engine(dml_runner=_ok_runner(0.12, 0.01, 240))
        eff = eng.estimate_effect(CausalChannel.DML, "momentum", "return")
        assert eff.downgraded is False
        assert eff.effect == pytest.approx(0.12)
        assert eff.p_value == pytest.approx(0.01)
        assert eff.n_samples == 240
        assert eff.channel is CausalChannel.DML

    def test_runner_not_injected_degraded(self) -> None:
        eng = _engine()
        for ch in (CausalChannel.DML, CausalChannel.CAUSAL_FOREST, CausalChannel.DOWHY_REFUTE):
            eff = eng.estimate_effect(ch, "momentum", "return")
            assert eff.downgraded is True
            assert eff.effect == 0.0
            assert eff.p_value == 1.0
            assert "未注入" in eff.note

    def test_runner_exception_degraded(self) -> None:
        def _boom(t, o, ctx):
            raise RuntimeError("econml 未安装")

        eng = _engine(dml_runner=_boom)
        eff = eng.estimate_effect(CausalChannel.DML, "momentum", "return")
        assert eff.downgraded is True
        assert "异常降级" in eff.note

    def test_runner_bad_payload_degraded(self) -> None:
        eng = _engine(dml_runner=lambda t, o, ctx: {"effect": 0.1})  # 缺 p_value
        assert eng.estimate_effect(CausalChannel.DML, "momentum", "return").downgraded is True
        eng2 = _engine(dml_runner=lambda t, o, ctx: {"effect": 0.1, "p_value": 1.5})  # p 越界
        assert eng2.estimate_effect(CausalChannel.DML, "momentum", "return").downgraded is True
        eng3 = _engine(dml_runner=lambda t, o, ctx: {"effect": float("nan"), "p_value": 0.01})
        assert eng3.estimate_effect(CausalChannel.DML, "momentum", "return").downgraded is True

    def test_dowhy_refuted_note(self) -> None:
        eng = _engine(dowhy_runner=lambda t, o, ctx: {"effect": 0.1, "p_value": 0.02, "refuted": True})
        eff = eng.estimate_effect(CausalChannel.DOWHY_REFUTE, "momentum", "return")
        assert eff.downgraded is False
        assert "证伪" in eff.note

    def test_context_passed_through(self) -> None:
        seen: list[dict] = []
        eng = _engine(dml_runner=lambda t, o, ctx: seen.append(dict(ctx)) or {"effect": 0.1, "p_value": 0.01})
        eng.estimate_effect(CausalChannel.DML, "momentum", "return", context={"n": 10})
        assert seen == [{"n": 10}]

    def test_unknown_channel_raises(self) -> None:
        eng = _engine()
        with pytest.raises(CausalMlError):
            eng.estimate_effect("dml", "momentum", "return")  # type: ignore[arg-type]
        with pytest.raises(CausalMlError):
            eng.estimate_effect(CausalChannel.DISCOVERY, "momentum", "return")  # 发现通道无效应估计

    def test_empty_names_raise(self) -> None:
        eng = _engine(dml_runner=_ok_runner())
        with pytest.raises(CausalMlError):
            eng.estimate_effect(CausalChannel.DML, "", "return")
        with pytest.raises(CausalMlError):
            eng.estimate_effect(CausalChannel.DML, "momentum", "  ")


# ──────────────────────────────────────────────────────────────────────────────
# 效应通道汇总
# ──────────────────────────────────────────────────────────────────────────────


class TestEstimateAll:
    def test_channel_order_and_significant(self) -> None:
        eng = _full_engine()
        rep = eng.estimate_all("momentum", "return")
        # 三效应通道按定义序（DISCOVERY 发现通道专属 precompute_causal_graph）
        assert [e.channel for e in rep.effects] == [
            CausalChannel.DML,
            CausalChannel.CAUSAL_FOREST,
            CausalChannel.DOWHY_REFUTE,
        ]
        assert rep.degraded_channels == ()
        # 显著性排序：|0.20| > |0.12| > |0.08|
        assert [s.channel for s in rep.significant] == [
            CausalChannel.DOWHY_REFUTE,
            CausalChannel.DML,
            CausalChannel.CAUSAL_FOREST,
        ]
        assert rep.ran_at == _T0

    def test_degraded_channels_listing(self) -> None:
        eng = _engine(dml_runner=_ok_runner(), discovery_runner=_discovery_runner())
        rep = eng.estimate_all("momentum", "return")
        assert rep.degraded_channels == (CausalChannel.CAUSAL_FOREST, CausalChannel.DOWHY_REFUTE)
        assert len(rep.effects) == 3  # 降级不阻断，三效应通道齐出

    def test_determinism(self) -> None:
        r1 = _full_engine().estimate_all("momentum", "return")
        r2 = _full_engine().estimate_all("momentum", "return")
        assert r1 == r2


# ──────────────────────────────────────────────────────────────────────────────
# 显著性筛选（|效应|>阈值 且 p<阈值，严格不等号）
# ──────────────────────────────────────────────────────────────────────────────


class TestFilterSignificant:
    def _eff(self, effect: float, p: float, downgraded: bool = False) -> CausalEffect:
        return CausalEffect(
            channel=CausalChannel.DML,
            treatment="momentum",
            outcome="return",
            effect=effect,
            p_value=p,
            n_samples=100,
            downgraded=downgraded,
        )

    def test_pass_and_fail(self) -> None:
        eng = _engine(effect_threshold=0.05, p_value_threshold=0.05)
        sig = eng.filter_significant(
            [
                self._eff(0.10, 0.01),  # 通过
                self._eff(0.03, 0.01),  # |效应|不足
                self._eff(0.10, 0.20),  # p 不足
            ]
        )
        assert len(sig) == 1
        assert sig[0].effect == pytest.approx(0.10)

    def test_boundary_excluded(self) -> None:
        eng = _engine(effect_threshold=0.05, p_value_threshold=0.05)
        sig = eng.filter_significant(
            [
                self._eff(0.05, 0.01),  # |效应|==阈值 → 排除（严格 >）
                self._eff(0.10, 0.05),  # p==阈值 → 排除（严格 <）
            ]
        )
        assert sig == ()

    def test_negative_effect_abs_pass(self) -> None:
        eng = _engine(effect_threshold=0.05)
        sig = eng.filter_significant([self._eff(-0.09, 0.02)])
        assert len(sig) == 1
        assert sig[0].effect == pytest.approx(-0.09)

    def test_downgraded_excluded(self) -> None:
        eng = _engine(effect_threshold=0.0)
        sig = eng.filter_significant([self._eff(0.5, 0.001, downgraded=True)])
        assert sig == ()


# ──────────────────────────────────────────────────────────────────────────────
# 盘前预计算因果图缓存（按数据指纹失效）
# ──────────────────────────────────────────────────────────────────────────────


class TestGraphCache:
    def test_precompute_and_hit(self) -> None:
        calls: list[str] = []

        def _runner(fp, variables, ctx):
            calls.append(fp)
            return {"edges": _EDGES}

        eng = _engine(discovery_runner=_runner)
        s1 = eng.precompute_causal_graph("fp-001", _VARS)
        s2 = eng.precompute_causal_graph("fp-001", _VARS)
        assert s1 is s2  # 命中直返同一快照
        assert calls == ["fp-001"]  # runner 仅调一次
        assert s1.edges == _EDGES
        assert s1.n_variables == 3
        assert s1.downgraded is False
        assert s1.computed_at == _T0

    def test_fingerprint_change_invalidates(self) -> None:
        eng = _engine(discovery_runner=_discovery_runner())
        s1 = eng.precompute_causal_graph("fp-001", _VARS)
        assert eng.cached_causal_graph("fp-001") is s1
        assert eng.cached_causal_graph("fp-002") is None  # 旧指纹视角失效
        s2 = eng.precompute_causal_graph("fp-002", _VARS)
        assert s2 is not s1
        assert eng.cached_causal_graph("fp-001") is None  # 数据变更后旧快照失效
        assert eng.cached_causal_graph("fp-002") is s2

    def test_discovery_not_injected_degraded(self) -> None:
        eng = _engine()
        snap = eng.precompute_causal_graph("fp-001", _VARS)
        assert snap.downgraded is True
        assert snap.edges == ()
        assert "未注入" in snap.note
        assert eng.cached_causal_graph("fp-001") is snap  # 降级快照同样入缓存

    def test_discovery_exception_degraded(self) -> None:
        def _boom(fp, variables, ctx):
            raise RuntimeError("lingam 崩溃")

        eng = _engine(discovery_runner=_boom)
        snap = eng.precompute_causal_graph("fp-001", _VARS)
        assert snap.downgraded is True
        assert snap.edges == ()
        assert "异常降级" in snap.note

    def test_edges_normalized(self) -> None:
        messy = [
            ("value", "return"),
            ("momentum", "return"),
            ("value", "return"),  # 重复
            ("size", "size"),  # 自环
            ("", "return"),  # 空白
            ("single",),  # 非法形态
        ]
        eng = _engine(discovery_runner=_discovery_runner(messy))
        snap = eng.precompute_causal_graph("fp-001", _VARS)
        assert snap.edges == (("momentum", "return"), ("value", "return"))  # 去重升序
        assert "自环" in snap.note
        assert "非法边" in snap.note

    def test_invalidate_cache(self) -> None:
        eng = _engine(discovery_runner=_discovery_runner())
        eng.precompute_causal_graph("fp-001", _VARS)
        eng.invalidate_graph_cache()
        assert eng.cached_causal_graph("fp-001") is None

    def test_bad_inputs_raise(self) -> None:
        eng = _engine(discovery_runner=_discovery_runner())
        with pytest.raises(CausalMlError):
            eng.precompute_causal_graph("", _VARS)  # 空指纹
        with pytest.raises(CausalMlError):
            eng.precompute_causal_graph("fp", [])  # 空变量集
        with pytest.raises(CausalMlError):
            eng.precompute_causal_graph("fp", ["momentum", " "])  # 空白变量
        with pytest.raises(CausalMlError):
            eng.cached_causal_graph("  ")
