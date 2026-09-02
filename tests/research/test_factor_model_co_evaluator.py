# [BLUEPRINT] MOD-FAC-005 | docs/03_modules/_domain_factor/factor_model_co_evaluator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FAC-005 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.research.test_factor_model_co_evaluator
# [TESTS] src/zephyr/research/factor_model_co_evaluator.py
"""MOD-FAC-005 单元测试：factor_model_co_evaluator 因子模型联合评估器。

蓝图验收（B10-01230/CAND-FAC-017，A1 v8.2）：
因子↔模型双向评估报告（贡献/利用度）+ 淘汰/迭代建议（低贡献淘汰清单 +
高潜力迭代方向）+ 报告版本化（单调递增、不可变、未知版本 Fail-Closed）。
双向评估器全注入内存替身，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.research.factor_model_co_evaluator",
    reason="factor_model_co_evaluator not importable",
)

from zephyr.research.factor_model_co_evaluator import (  # noqa: E402
    CoEvaluatorError,
    FactorModelCoEvaluator,
    FactorVerdict,
)

#: 贡献表 (factor, model) -> 贡献度
_CONTRIB = {
    ("f_dead", "m1"): 0.01,
    ("f_dead", "m2"): 0.01,  # mean 0.01 < 0.05 → eliminate
    ("f_mid", "m1"): 0.10,
    ("f_mid", "m2"): 0.10,  # mean 0.10 中贡献
    ("f_star", "m1"): 0.80,
    ("f_star", "m2"): 0.80,  # mean 0.80 高贡献 → keep
}

#: 利用度表 (model, factor) -> 利用度
_UTIL = {
    ("m1", "f_dead"): 0.10,
    ("m2", "f_dead"): 0.10,
    ("m1", "f_mid"): 0.90,
    ("m2", "f_mid"): 0.90,  # mean 0.90 ≥ 0.5 → iterate（中贡献高利用）
    ("m1", "f_star"): 0.60,
    ("m2", "f_star"): 0.40,  # mean 0.50
}


def _contrib(f: str, m: str) -> float:
    return _CONTRIB[(f, m)]


def _util(m: str, f: str) -> float:
    return _UTIL[(m, f)]


def _evaluator(**kw) -> FactorModelCoEvaluator:
    kw.setdefault("contribution_evaluator", _contrib)
    kw.setdefault("utilization_evaluator", _util)
    return FactorModelCoEvaluator(**kw)


_FACTORS = ["f_dead", "f_mid", "f_star"]
_MODELS = ["m1", "m2"]


# ──────────────────────────────────────────────────────────────────────────────
# 构造 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_missing_evaluators(self) -> None:
        with pytest.raises(CoEvaluatorError):
            FactorModelCoEvaluator(contribution_evaluator=None, utilization_evaluator=_util)
        with pytest.raises(CoEvaluatorError):
            FactorModelCoEvaluator(contribution_evaluator=_contrib, utilization_evaluator=None)

    def test_threshold_order_invalid(self) -> None:
        with pytest.raises(CoEvaluatorError):
            _evaluator(eliminate_threshold=0.5, high_contribution=0.2)  # 淘汰线≥高贡献线
        with pytest.raises(CoEvaluatorError):
            _evaluator(eliminate_threshold=-0.1)

    def test_high_utilization_range(self) -> None:
        with pytest.raises(CoEvaluatorError):
            _evaluator(high_utilization=1.5)


# ──────────────────────────────────────────────────────────────────────────────
# 双向评估 + 淘汰/迭代建议
# ──────────────────────────────────────────────────────────────────────────────


class TestEvaluate:
    def test_empty_ids_rejected(self) -> None:
        ev = _evaluator()
        with pytest.raises(CoEvaluatorError):
            ev.evaluate([], _MODELS)
        with pytest.raises(CoEvaluatorError):
            ev.evaluate(_FACTORS, [])

    def test_blank_and_duplicate_ids_rejected(self) -> None:
        ev = _evaluator()
        with pytest.raises(CoEvaluatorError):
            ev.evaluate(["f_dead", " "], _MODELS)
        with pytest.raises(CoEvaluatorError):
            ev.evaluate(["f_dead", "f_dead"], _MODELS)

    def test_bidirectional_scores(self) -> None:
        report = _evaluator().evaluate(_FACTORS, _MODELS)
        scores = {s.factor_id: s for s in report.factor_scores}
        assert scores["f_dead"].mean_contribution == pytest.approx(0.01)
        assert scores["f_mid"].mean_utilization == pytest.approx(0.90)
        m_scores = {s.model_id: s.mean_utilization for s in report.model_scores}
        assert m_scores["m1"] == pytest.approx(round((0.10 + 0.90 + 0.60) / 3, 6))
        assert m_scores["m2"] == pytest.approx(round((0.10 + 0.90 + 0.40) / 3, 6))

    def test_verdict_vocab(self) -> None:
        report = _evaluator().evaluate(_FACTORS, _MODELS)
        verdicts = {s.factor_id: s.verdict for s in report.factor_scores}
        assert verdicts["f_dead"] is FactorVerdict.ELIMINATE
        assert verdicts["f_mid"] is FactorVerdict.ITERATE
        assert verdicts["f_star"] is FactorVerdict.KEEP

    def test_elimination_and_iteration_lists(self) -> None:
        report = _evaluator().evaluate(_FACTORS, _MODELS)
        assert report.elimination_list == ("f_dead",)
        assert report.iteration_list == ("f_mid",)

    def test_mid_contrib_low_util_keeps(self) -> None:
        # 中贡献但利用度不足 → 不进迭代清单（keep）
        util_low = {k: (0.1 if k[1] == "f_mid" else v) for k, v in _UTIL.items()}
        ev = _evaluator(utilization_evaluator=lambda m, f: util_low[(m, f)])
        report = ev.evaluate(_FACTORS, _MODELS)
        verdicts = {s.factor_id: s.verdict for s in report.factor_scores}
        assert verdicts["f_mid"] is FactorVerdict.KEEP
        assert report.iteration_list == ()

    def test_evaluator_exception_fail_closed(self) -> None:
        def boom(f: str, m: str) -> float:
            raise RuntimeError("评估后端故障")

        with pytest.raises(CoEvaluatorError):
            _evaluator(contribution_evaluator=boom).evaluate(_FACTORS, _MODELS)

    def test_evaluator_bad_return_fail_closed(self) -> None:
        with pytest.raises(CoEvaluatorError):
            _evaluator(utilization_evaluator=lambda m, f: None).evaluate(_FACTORS, _MODELS)


# ──────────────────────────────────────────────────────────────────────────────
# 报告版本化
# ──────────────────────────────────────────────────────────────────────────────


class TestVersioning:
    def test_versions_monotonic(self) -> None:
        ev = _evaluator()
        r1 = ev.evaluate(_FACTORS, _MODELS)
        r2 = ev.evaluate(_FACTORS, _MODELS)
        assert (r1.version, r2.version) == (1, 2)
        assert ev.list_versions() == (1, 2)

    def test_get_report_and_latest(self) -> None:
        ev = _evaluator()
        r1 = ev.evaluate(_FACTORS, _MODELS)
        ev.evaluate(["f_dead"], ["m1"])
        assert ev.get_report(1) is r1
        assert ev.latest().version == 2

    def test_unknown_version_raises(self) -> None:
        ev = _evaluator()
        ev.evaluate(_FACTORS, _MODELS)
        with pytest.raises(CoEvaluatorError):
            ev.get_report(99)

    def test_latest_without_report_raises(self) -> None:
        with pytest.raises(CoEvaluatorError):
            _evaluator().latest()

    def test_report_immutable(self) -> None:
        report = _evaluator().evaluate(_FACTORS, _MODELS)
        with pytest.raises(Exception):
            report.version = 99  # type: ignore[misc]

    def test_full_determinism(self) -> None:
        def run() -> tuple:
            r = _evaluator().evaluate(_FACTORS, _MODELS)
            return (
                tuple((s.factor_id, s.mean_contribution, s.verdict.value) for s in r.factor_scores),
                r.elimination_list,
                r.iteration_list,
            )

        assert run() == run()  # 同输入必同输出
