# [BLUEPRINT] MOD-INT-LLM-SELFEVAL | docs/03_modules/_domain_intelligence/llm_self_evaluation/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-LLM-SELFEVAL | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.intelligence.test_llm_self_evaluation
# [TESTS] src/zephyr/intelligence/llm_self_evaluation.py
"""MOD-INT-LLM-SELFEVAL 单元测试：llm_self_evaluation LLM 自评估与交叉验证。

蓝图验收（B10-01883/CAND-AISA-013，A1 §29.37）：
LLM-as-Judge 三维评分（事实/逻辑/风险，judge 注入）+ CoT 反向自校验
（逐步重验标记不一致）+ 三模型独立分析投票（一致性度量）+ 低一致性
标争议降权或人工审核 + 输出硬标注 advisory 不可直接交易 + CoT 链写审计。
judge/模型/重验/审核/审计全注入内存替身，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.intelligence.llm_self_evaluation",
    reason="llm_self_evaluation not importable",
)

from zephyr.intelligence.llm_self_evaluation import (  # noqa: E402
    EvalDimension,
    EvalVerdict,
    LlmSelfEvalError,
    LlmSelfEvaluation,
)

_QUERY = "该标的是否存在政策催化？"
_COT = ["第一步：读取政策事件", "第二步：比对标的行业", "第三步：得出结论"]


def _judge(score: float = 0.9):
    return lambda q, dim: score


def _models(a: str = "看多", b: str = "看多", c: str = "看多") -> dict:
    return {
        "model-a": lambda q: a,
        "model-b": lambda q: b,
        "model-c": lambda q: c,
    }


def _rechecker(ok: bool = True):
    return lambda i, step: ok


def _eval(reviews: list | None = None, audits: list | None = None, **kw) -> LlmSelfEvaluation:
    return LlmSelfEvaluation(
        judge=kw.pop("judge", _judge()),
        models=kw.pop("models", _models()),
        cot_rechecker=kw.pop("cot_rechecker", _rechecker()),
        review_sink=(lambda v: reviews.append(v)) if reviews is not None else None,
        audit_sink=(lambda v: audits.append(v)) if audits is not None else None,
        **kw,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造（注入校验 Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_ok(self) -> None:
        _eval()

    def test_models_not_three_raises(self) -> None:
        with pytest.raises(LlmSelfEvalError):
            _eval(models={"m1": lambda q: "x", "m2": lambda q: "x"})
        with pytest.raises(LlmSelfEvalError):
            _eval(models={**_models(), "m4": lambda q: "x"})

    def test_uncallable_model_raises(self) -> None:
        with pytest.raises(LlmSelfEvalError):
            _eval(models={"a": lambda q: "x", "b": lambda q: "x", "c": "not-fn"})

    def test_bad_threshold_raises(self) -> None:
        with pytest.raises(LlmSelfEvalError):
            _eval(consistency_threshold=0.0)
        with pytest.raises(LlmSelfEvalError):
            _eval(consistency_threshold=1.5)

    def test_bad_dispute_weight_raises(self) -> None:
        with pytest.raises(LlmSelfEvalError):
            _eval(dispute_weight=1.0)


# ──────────────────────────────────────────────────────────────────────────────
# Judge 三维评分
# ──────────────────────────────────────────────────────────────────────────────


class TestJudgeScores:
    def test_three_dimensions_scored(self) -> None:
        seen: list[EvalDimension] = []
        engine = _eval(judge=lambda q, d: seen.append(d) or 0.8)
        verdict = engine.evaluate(_QUERY, _COT)
        assert set(seen) == set(EvalDimension)
        assert len(verdict.dimension_scores) == 3
        assert all(s == 0.8 for _, s in verdict.dimension_scores)

    def test_judge_score_out_of_range_raises(self) -> None:
        engine = _eval(judge=_judge(1.5))
        with pytest.raises(LlmSelfEvalError):
            engine.evaluate(_QUERY, _COT)

    def test_empty_query_raises(self) -> None:
        with pytest.raises(LlmSelfEvalError):
            _eval().evaluate("", _COT)


# ──────────────────────────────────────────────────────────────────────────────
# CoT 反向自校验
# ──────────────────────────────────────────────────────────────────────────────


class TestCotVerify:
    def test_steps_rechecked_each(self) -> None:
        checked: list[tuple[int, str]] = []
        engine = _eval(cot_rechecker=lambda i, s: checked.append((i, s)) or True)
        verdict = engine.evaluate(_QUERY, _COT)
        assert checked == [(0, _COT[0]), (1, _COT[1]), (2, _COT[2])]  # 逐步重验
        assert verdict.cot_consistent is True
        assert len(verdict.cot_checks) == 3

    def test_inconsistent_step_marked_and_disputed(self) -> None:
        reviews: list[EvalVerdict] = []
        engine = _eval(reviews, cot_rechecker=lambda i, s: i != 1)  # 第2步不一致
        verdict = engine.evaluate(_QUERY, _COT)
        assert verdict.cot_consistent is False
        assert [c.consistent for c in verdict.cot_checks] == [True, False, True]
        assert verdict.disputed is True
        assert len(reviews) == 1

    def test_empty_cot_raises(self) -> None:
        with pytest.raises(LlmSelfEvalError):
            _eval().evaluate(_QUERY, [])

    def test_empty_step_raises(self) -> None:
        with pytest.raises(LlmSelfEvalError):
            _eval().evaluate(_QUERY, ["ok", ""])


# ──────────────────────────────────────────────────────────────────────────────
# 三模型投票与一致性
# ──────────────────────────────────────────────────────────────────────────────


class TestVoting:
    def test_unanimous_not_disputed(self) -> None:
        verdict = _eval().evaluate(_QUERY, _COT)
        assert verdict.consistency == pytest.approx(1.0)
        assert verdict.majority_conclusion == "看多"
        assert verdict.disputed is False
        assert verdict.weight == 1.0
        assert verdict.requires_human_review is False

    def test_two_thirds_majority(self) -> None:
        verdict = _eval(models=_models("看多", "看多", "看空")).evaluate(_QUERY, _COT)
        assert verdict.consistency == pytest.approx(2.0 / 3.0)
        assert verdict.majority_conclusion == "看多"
        assert verdict.disputed is False  # 2/3 不低于默认阈值

    def test_all_split_disputed_downweight(self) -> None:
        reviews: list[EvalVerdict] = []
        verdict = _eval(reviews, models=_models("看多", "看空", "中性")).evaluate(_QUERY, _COT)
        assert verdict.consistency == pytest.approx(1.0 / 3.0)
        assert verdict.disputed is True
        assert verdict.weight == 0.5  # 争议降权
        assert verdict.requires_human_review is True
        assert len(reviews) == 1  # 入人工审核队列

    def test_majority_tie_break_deterministic(self) -> None:
        verdict = _eval(models=_models("b", "a", "c")).evaluate(_QUERY, _COT)
        assert verdict.majority_conclusion == "a"  # 并列按结论名序

    def test_empty_conclusion_raises(self) -> None:
        engine = _eval(models=_models("看多", "", "看多"))
        with pytest.raises(LlmSelfEvalError):
            engine.evaluate(_QUERY, _COT)


# ──────────────────────────────────────────────────────────────────────────────
# advisory 硬标注 + CoT 审计
# ──────────────────────────────────────────────────────────────────────────────


class TestAdvisoryAndAudit:
    def test_output_hard_labeled_advisory(self) -> None:
        verdict = _eval().evaluate(_QUERY, _COT)
        assert verdict.output_label == "advisory"
        assert verdict.tradeable is False

    def test_label_tamper_rejected(self) -> None:
        verdict = _eval().evaluate(_QUERY, _COT)
        import dataclasses

        with pytest.raises(LlmSelfEvalError):
            dataclasses.replace(verdict, output_label="executable")
        with pytest.raises(LlmSelfEvalError):
            dataclasses.replace(verdict, tradeable=True)

    def test_cot_chain_written_to_audit(self) -> None:
        audits: list[EvalVerdict] = []
        verdict = _eval(audits=audits).evaluate(_QUERY, _COT)
        assert audits == [verdict]
        assert [c.step_text for c in audits[0].cot_checks] == _COT  # CoT 链留痕
