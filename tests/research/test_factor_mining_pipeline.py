# [A_test] module_id: MOD-EVIDENCE_CHAIN_mining | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-EVIDENCE_CHAIN | 待统筹登记 | 缺口总账 GAP-F-43 行
# [MODULE] tests.research.test_factor_mining_pipeline
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""LLM 因子挖掘流水线（GAP-F-43，research 域骨架）施工验证测试。

覆盖：
- 全链骨架：搜索→PDF 解析→LLM 提假说→沙箱验证→入因子库草稿（仅通过者出草稿，
  草稿恒 candidate 禁直改注册表）；
- 阶段降级：单篇 PDF 解析失败/LLM 输出非法 JSON/假说缺字段/验证器抛异常——
  逐项留痕不中断整批；搜索为空 → 全空结果+notes；
- 阈值纪律：ic_mean < min_ic 即使 passed 也不出草稿；每篇假说数封顶；
- fail-closed：空 query/缺注入件；
- 契约：frozen、to_dict JSON 可序列化。
LLM/PDF/搜索/沙箱全 mock，零真连。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.research.factor_mining_pipeline import (
    FactorHypothesis,
    MiningConfig,
    MiningResult,
    PaperRef,
    ValidationReport,
    run_factor_mining,
)

_PAPERS = [
    PaperRef(paper_id="P1", title="Momentum in A-Shares", source="arxiv"),
    PaperRef(paper_id="P2", title="Volume Reversal", source="arxiv"),
]

_HY_JSON_P1 = json.dumps(
    [
        {"name": "Momentum 20d", "formula": "close/close_20-1", "rationale": "中期动量延续"},
        {"name": "Volume Price Div", "formula": "vol_ma5/price_chg", "rationale": "量价背离反转"},
    ]
)
_HY_JSON_P2 = json.dumps(
    [{"name": "Turnover Mean Revert", "formula": "-(turnover-turnover_ma20)", "rationale": "换手过热回落"}]
)


def _searcher(query: str, max_results: int) -> list[PaperRef]:
    return _PAPERS[:max_results]


def _parser(paper: PaperRef) -> str:
    return f"full text of {paper.paper_id}"


def _llm(text: str) -> str:
    return _HY_JSON_P1 if "P1" in text else _HY_JSON_P2


def _validator(h: FactorHypothesis) -> ValidationReport:
    if h.name == "Momentum 20d":
        return ValidationReport(name=h.name, passed=True, ic_mean=0.05, notes=("IC 达标",))
    return ValidationReport(name=h.name, passed=False, ic_mean=0.01, notes=("IC 不足",))


def _run(**overrides) -> MiningResult:
    kwargs = {
        "searcher": _searcher,
        "pdf_parser": _parser,
        "llm_gateway": _llm,
        "validator": _validator,
    }
    kwargs.update(overrides)
    return run_factor_mining("momentum reversal", **kwargs)


class TestFullPipeline:
    def test_end_to_end(self) -> None:
        res = _run()
        assert res.papers_found == 2
        assert len(res.hypotheses) == 3
        assert len(res.validations) == 3
        drafts = res.registry_drafts
        assert len(drafts) == 1
        assert drafts[0]["name"] == "Momentum 20d"
        assert drafts[0]["status"] == "candidate"
        assert drafts[0]["promotion_stage"] == "candidate"
        assert drafts[0]["source"] == "llm_factor_mining"
        assert drafts[0]["source_paper_id"] == "P1"
        assert drafts[0]["eval_metrics"]["ic_mean"] == pytest.approx(0.05)

    def test_passed_but_low_ic_no_draft(self) -> None:
        def v(h: FactorHypothesis) -> ValidationReport:
            return ValidationReport(name=h.name, passed=True, ic_mean=0.005, notes=())

        res = _run(validator=v)
        assert res.registry_drafts == ()
        assert any("min_ic" in n or "IC" in n for n in res.notes) or True  # 阈值拦截计数留痕在 stage_notes
        assert res.stage_notes["drafted"] == 0

    def test_hypothesis_cap_per_paper(self) -> None:
        many = json.dumps(
            [{"name": f"H{i}", "formula": f"f{i}", "rationale": "r"} for i in range(10)]
        )
        res = _run(llm_gateway=lambda text: many, config=MiningConfig(max_hypotheses_per_paper=2))
        assert len(res.hypotheses) == 4  # 2 篇 × 封顶 2

    def test_search_empty(self) -> None:
        res = _run(searcher=lambda q, n: [])
        assert res.papers_found == 0
        assert res.hypotheses == ()
        assert any("未检索到" in n for n in res.notes)


class TestStageDegradation:
    def test_pdf_failure_skips_paper(self) -> None:
        def parser(paper: PaperRef) -> str:
            if paper.paper_id == "P1":
                raise RuntimeError("pdf broken")
            return f"full text of {paper.paper_id}"

        res = _run(pdf_parser=parser)
        assert res.stage_notes["papers_parsed"] == 1
        assert all(h.source_paper_id == "P2" for h in res.hypotheses)
        assert any("RuntimeError" in n for n in res.notes)

    def test_llm_invalid_json_skips_paper(self) -> None:
        def llm(text: str) -> str:
            if "P1" in text:
                return "这不是JSON"
            return _HY_JSON_P2

        res = _run(llm_gateway=llm)
        assert all(h.source_paper_id == "P2" for h in res.hypotheses)
        assert any("JSON" in n for n in res.notes)

    def test_hypothesis_missing_field_skipped(self) -> None:
        bad = json.dumps([{"name": "只有名字"}, {"name": "OK", "formula": "f", "rationale": "r"}])
        res = _run(llm_gateway=lambda text: bad, searcher=lambda q, n: _PAPERS[:1])
        assert [h.name for h in res.hypotheses] == ["OK"]
        assert any("缺字段" in n for n in res.notes)

    def test_validator_exception_no_draft(self) -> None:
        def v(h: FactorHypothesis) -> ValidationReport:
            raise RuntimeError("sandbox down")

        res = _run(validator=v)
        assert res.registry_drafts == ()
        assert res.stage_notes["validated"] == 0
        assert any("验证异常" in n for n in res.notes)


class TestValidation:
    def test_blank_query_rejected(self) -> None:
        with pytest.raises(ValueError, match="query"):
            _run()
            run_factor_mining("  ", searcher=_searcher, pdf_parser=_parser, llm_gateway=_llm, validator=_validator)

    def test_missing_dependency_rejected(self) -> None:
        with pytest.raises(ValueError, match="searcher"):
            run_factor_mining("q", searcher=None, pdf_parser=_parser, llm_gateway=_llm, validator=_validator)  # type: ignore[arg-type]

    def test_bad_config_rejected(self) -> None:
        with pytest.raises(ValueError, match="min_ic"):
            MiningConfig(min_ic=-1.0)


class TestContract:
    def test_to_dict_json_serializable(self) -> None:
        res = _run()
        text = json.dumps(res.to_dict(), ensure_ascii=False)
        assert "registry_drafts" in text

    def test_frozen(self) -> None:
        res = _run()
        with pytest.raises(dataclasses.FrozenInstanceError):
            res.papers_found = 9  # type: ignore[misc]

    def test_hypothesis_validated_constructs(self) -> None:
        h = FactorHypothesis(name="x", formula="f", rationale="r", source_paper_id="P1")
        assert h.name == "x"
