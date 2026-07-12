# [A_test] module_id: SRC-TST-2029 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-646 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_hallucination_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for hallucination_detector.py (T-3-07, ADR-0039)
==============================================================

覆盖范围（≥15 条）
------------------
1. HallucinationResult 契约校验（正常 / 非法字段）
2. 触发矩阵 should_trigger 的 L1 / L2 / L3 判定
3. CoVe 四步正常流程（双模型均可达，低 inconsistency）
4. CoVe 发现显著不一致 → is_hallucination=True
5. H 级 Mid-band 走 Step 4 Final Check
6. H 级确认幻觉 → requires_human=True
7. 单模型降级（仅一方可达） → fallback_used=single_model
8. 双模型均不可达 → keyword 兜底（命中 suspect_citation）
9. Keyword 规则：数值异常（Sharpe > 5）
10. Keyword 规则：missing file（引用不存在的 .md）
11. Keyword 规则：frozen 资产修改未经 Handoff
12. Budget 日度超限 L/M 级 → budget_skip
13. Budget 窗口跨日重置
14. L3 黑名单 → triggered=False
15. 审计回调被触发一次
16. Step 1 返回非法 JSON → 自动降级到 keyword 兜底
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from zephyr.orchestrator.hallucination_detector import (
    KEYWORD_HALLU_RULES,
    BudgetState,
    FallbackMode,
    HallucinationDetector,
    HallucinationResult,
    ModelCallResult,
    RiskLevel,
    TriggerLevel,
    build_detector_with_defaults,
)

# ---------------------------------------------------------------------------
# 辅助：可编排的 FakeCaller
# ---------------------------------------------------------------------------


class FakeCaller:
    """可编排的模型调用 mock。按 purpose 返回预设内容。"""

    def __init__(
        self,
        responses: dict[str, ModelCallResult] | None = None,
        default_cost: float = 0.005,
    ) -> None:
        self._responses = responses or {}
        self._default_cost = default_cost
        self.calls: list[tuple[str, str]] = []

    def __call__(self, prompt: str, *, purpose: str) -> ModelCallResult:
        self.calls.append((purpose, prompt[:80]))
        if purpose in self._responses:
            return self._responses[purpose]
        return ModelCallResult(content="{}", cost_usd=self._default_cost, latency_ms=120, success=True)


def _step1_payload(baseline: str, questions: list[str]) -> ModelCallResult:
    return ModelCallResult(
        content=json.dumps({"baseline_answer": baseline, "verify_questions": questions}),
        cost_usd=0.005,
        latency_ms=500,
        success=True,
    )


def _step2_payload(answers: list[dict[str, Any]]) -> ModelCallResult:
    return ModelCallResult(
        content=json.dumps(answers),
        cost_usd=0.003,
        latency_ms=400,
        success=True,
    )


# ---------------------------------------------------------------------------
# 1. HallucinationResult 契约
# ---------------------------------------------------------------------------


class TestHallucinationResultContract:
    def test_valid_minimal(self) -> None:
        r = HallucinationResult(
            claim="x",
            is_hallucination=False,
            confidence=0.9,
            risk_level="L",
            inconsistency_score=0.1,
        )
        assert r.claim == "x"
        assert r.risk_level == "L"
        assert r.triggered is True

    def test_confidence_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            HallucinationResult(
                claim="x",
                is_hallucination=False,
                confidence=1.5,
                risk_level="L",
                inconsistency_score=0.1,
            )

    def test_too_many_questions(self) -> None:
        with pytest.raises(ValidationError):
            HallucinationResult(
                claim="x",
                is_hallucination=False,
                confidence=0.8,
                risk_level="L",
                inconsistency_score=0.1,
                verify_questions=["q"] * 6,
            )


# ---------------------------------------------------------------------------
# 2. should_trigger 触发矩阵
# ---------------------------------------------------------------------------


class TestShouldTrigger:
    def setup_method(self) -> None:
        self.detector = HallucinationDetector()

    def test_l3_pure_codegen(self) -> None:
        assert self.detector.should_trigger(RiskLevel.L, pure_codegen=True) == TriggerLevel.L3_BLACKLIST

    def test_l1_high_risk(self) -> None:
        assert self.detector.should_trigger(RiskLevel.H) == TriggerLevel.L1_WHITELIST

    def test_l1_low_intent_confidence(self) -> None:
        assert (
            self.detector.should_trigger(RiskLevel.M, source_stage="semantic", intent_confidence=0.7)
            == TriggerLevel.L1_WHITELIST
        )

    def test_l2_doc_target(self) -> None:
        assert self.detector.should_trigger(RiskLevel.L, target_is_doc=True) == TriggerLevel.L2_GREY

    def test_l1_frozen_asset(self) -> None:
        assert self.detector.should_trigger(RiskLevel.L, frozen_asset_touch=True) == TriggerLevel.L1_WHITELIST


# ---------------------------------------------------------------------------
# 3. CoVe 正常流程（双模型可达，低 inconsistency）
# ---------------------------------------------------------------------------


def test_cove_happy_path_low_inconsistency() -> None:
    primary = FakeCaller(
        {
            "cove_step1_baseline_plan": _step1_payload(
                baseline="Sharpe is 1.2 for momentum strategy",
                questions=[
                    "What is the Sharpe ratio of momentum strategy?",
                    "What is the strategy name?",
                    "Is the Sharpe positive?",
                ],
            )
        }
    )
    verifier = FakeCaller(
        {
            "cove_step2_verify": _step2_payload(
                [
                    {
                        "question": "What is the Sharpe ratio of momentum strategy?",
                        "answer": "Sharpe is 1.2 for momentum strategy",
                        "confidence_self": 0.9,
                    },
                    {
                        "question": "What is the strategy name?",
                        "answer": "momentum strategy",
                        "confidence_self": 0.9,
                    },
                    {
                        "question": "Is the Sharpe positive?",
                        "answer": "yes positive Sharpe 1.2",
                        "confidence_self": 0.9,
                    },
                ]
            )
        }
    )
    detector = HallucinationDetector(primary_caller=primary, verifier_caller=verifier)
    r = detector.detect("Sharpe is 1.2 for momentum strategy", {}, RiskLevel.M)
    assert r.triggered is True
    assert r.is_hallucination is False
    assert r.fallback_used is None
    assert r.execution_model == "Sonnet 4.6"
    assert r.verifier_model == "GLM-5.1"
    assert r.cost_usd > 0
    assert len(r.verify_questions) >= 3


def test_cove_detects_hallucination_on_drift() -> None:
    primary = FakeCaller(
        {
            "cove_step1_baseline_plan": _step1_payload(
                baseline="因子 A 的 IC 是 0.08",
                questions=[
                    "因子 A 的 IC 具体数值是多少？",
                    "因子 A 的样本周期是什么？",
                    "该 IC 是否显著？",
                ],
            ),
            "cove_step4_final_check": ModelCallResult(
                content=json.dumps({"corrected": "因子 A 的 IC 未知", "confidence": 0.4}),
                cost_usd=0.004,
                latency_ms=300,
                success=True,
            ),
        }
    )
    verifier = FakeCaller(
        {
            "cove_step2_verify": _step2_payload(
                [
                    {"question": "因子 A 的 IC 具体数值是多少？", "answer": "不知道", "confidence_self": 0.3},
                    {
                        "question": "因子 A 的样本周期是什么？",
                        "answer": "完全不相关的东西 banana apple",
                        "confidence_self": 0.3,
                    },
                    {"question": "该 IC 是否显著？", "answer": "cucumber tomato", "confidence_self": 0.2},
                ]
            )
        }
    )
    detector = HallucinationDetector(primary_caller=primary, verifier_caller=verifier)
    r = detector.detect("因子 A 的 IC 是 0.08", {}, RiskLevel.H)
    assert r.is_hallucination is True
    assert r.requires_human is True
    assert r.risk_level == "H"


def test_cove_h_level_midband_final_check() -> None:
    """H 级若 inconsistency_score 在 (0.10, 0.40] 中间带 → requires_human 而非 Final Check 修正。"""
    primary = FakeCaller(
        {
            "cove_step1_baseline_plan": _step1_payload(
                baseline="答案 A",
                questions=["Q1", "Q2", "Q3", "Q4"],
            )
        }
    )
    verifier = FakeCaller(
        {
            "cove_step2_verify": _step2_payload(
                [
                    {"question": "Q1", "answer": "答案 A", "confidence_self": 0.8},
                    {"question": "Q2", "answer": "答案 A", "confidence_self": 0.8},
                    {"question": "Q3", "answer": "答案 A", "confidence_self": 0.8},
                    {"question": "Q4", "answer": "xyz 不相关完全", "confidence_self": 0.4},
                ]
            )
        }
    )
    detector = HallucinationDetector(primary_caller=primary, verifier_caller=verifier)
    r = detector.detect("答案 A", {}, RiskLevel.H)
    assert r.inconsistency_score > 0.10
    assert r.requires_human is True


# ---------------------------------------------------------------------------
# 4. 降级级联
# ---------------------------------------------------------------------------


def test_single_model_fallback_when_only_one_available() -> None:
    primary = FakeCaller()
    detector = HallucinationDetector(primary_caller=primary, verifier_caller=None)
    r = detector.detect("无害 claim", {}, RiskLevel.M)
    assert r.fallback_used == FallbackMode.SINGLE_MODEL.value
    assert r.confidence == 0.5
    assert r.triggered is True


def test_keyword_fallback_when_both_models_unavailable() -> None:
    detector = HallucinationDetector(primary_caller=None, verifier_caller=None)
    r = detector.detect(
        "Meta 2023 论文 证明 Sharpe=12.5 是因子 A 的真实值",
        {},
        RiskLevel.M,
    )
    assert r.fallback_used == FallbackMode.KEYWORD.value
    assert r.is_hallucination is True
    assert any("suspect_citation" in ev for ev in r.evidence)
    assert any("numeric_out_of_range" in ev for ev in r.evidence)


def test_step1_bad_json_falls_back_to_keyword() -> None:
    primary = FakeCaller(
        {
            "cove_step1_baseline_plan": ModelCallResult(
                content="not a json at all",
                cost_usd=0.005,
                latency_ms=200,
                success=True,
            )
        }
    )
    verifier = FakeCaller()
    detector = HallucinationDetector(primary_caller=primary, verifier_caller=verifier)
    r = detector.detect("claim with IC=2.5", {}, RiskLevel.M)
    assert r.fallback_used == FallbackMode.KEYWORD.value
    assert any("numeric_out_of_range" in ev for ev in r.evidence)


# ---------------------------------------------------------------------------
# 5. Keyword 规则
# ---------------------------------------------------------------------------


class TestKeywordRules:
    def test_numeric_out_of_range_sharpe(self) -> None:
        out = KEYWORD_HALLU_RULES["numeric_out_of_range"]("Sharpe = 8.5 is great")
        assert any("sharpe" in ev.lower() for ev in out)

    def test_numeric_out_of_range_ic(self) -> None:
        out = KEYWORD_HALLU_RULES["numeric_out_of_range"]("IC = 2.3 computed")
        assert out  # IC > 1 violates
        out_ok = KEYWORD_HALLU_RULES["numeric_out_of_range"]("IC = 0.08 computed")
        assert out_ok == []

    def test_missing_file(self, tmp_path: Path) -> None:
        (tmp_path / "real.md").write_text("x", encoding="utf-8")
        out_missing = KEYWORD_HALLU_RULES["missing_files"]("See docs/does_not_exist.md for detail", tmp_path)
        assert out_missing
        out_found = KEYWORD_HALLU_RULES["missing_files"]("See real.md", tmp_path)
        assert out_found == []

    def test_suspect_citation(self) -> None:
        out = KEYWORD_HALLU_RULES["suspect_citations"]("Citadel 内部 report shows alpha")
        assert out

    def test_frozen_asset_mutation_blocked(self) -> None:
        out_blocked = KEYWORD_HALLU_RULES["frozen_asset_mutation"]("请修改 tool-contracts.yaml 来适配", False)
        assert out_blocked
        out_ok = KEYWORD_HALLU_RULES["frozen_asset_mutation"]("请修改 tool-contracts.yaml 来适配", True)
        assert out_ok == []


# ---------------------------------------------------------------------------
# 6. Budget / 窗口重置
# ---------------------------------------------------------------------------


def test_budget_skip_l_m_when_daily_cap_exhausted() -> None:
    fixed_now = datetime(2026, 4, 24, 12, 0, tzinfo=UTC)
    detector = HallucinationDetector(
        primary_caller=FakeCaller(),
        verifier_caller=FakeCaller(),
        daily_budget_usd=0.01,
        now=lambda: fixed_now,
    )
    detector.budget_state.current_day = fixed_now.date().isoformat()
    detector.budget_state.current_month = fixed_now.strftime("%Y-%m")
    detector.budget_state.daily_spent_usd = 0.02
    r = detector.detect("normal claim", {}, RiskLevel.L)
    assert r.triggered is False
    assert r.fallback_used == FallbackMode.BUDGET_SKIP.value


def test_budget_h_level_ignores_daily_cap() -> None:
    primary = FakeCaller({"cove_step1_baseline_plan": _step1_payload("ok", ["Q1", "Q2", "Q3"])})
    verifier = FakeCaller(
        {
            "cove_step2_verify": _step2_payload(
                [
                    {"question": "Q1", "answer": "ok", "confidence_self": 0.9},
                    {"question": "Q2", "answer": "ok", "confidence_self": 0.9},
                    {"question": "Q3", "answer": "ok", "confidence_self": 0.9},
                ]
            )
        }
    )
    fixed_now = datetime(2026, 4, 24, 12, 0, tzinfo=UTC)
    detector = HallucinationDetector(
        primary_caller=primary,
        verifier_caller=verifier,
        daily_budget_usd=0.001,
        now=lambda: fixed_now,
    )
    detector.budget_state.current_day = fixed_now.date().isoformat()
    detector.budget_state.current_month = fixed_now.strftime("%Y-%m")
    detector.budget_state.daily_spent_usd = 10.0
    r = detector.detect("ok", {}, RiskLevel.H)
    assert r.triggered is True  # H 级强制执行


def test_budget_window_resets_across_day() -> None:
    times = [
        datetime(2026, 4, 24, 23, 59, tzinfo=UTC),
        datetime(2026, 4, 25, 0, 0, 1, tzinfo=UTC),
    ]

    def clock() -> datetime:
        return times[min(len(times) - 1, clock.idx)]  # type: ignore[attr-defined]

    clock.idx = 0  # type: ignore[attr-defined]
    detector = HallucinationDetector(primary_caller=None, verifier_caller=None, now=clock)
    detector.budget_state.reset_if_window_changed(times[0])
    detector.budget_state.record(0.5)
    assert detector.budget_state.daily_spent_usd == 0.5
    clock.idx = 1  # type: ignore[attr-defined]
    detector.budget_state.reset_if_window_changed(times[1])
    assert detector.budget_state.daily_spent_usd == 0.0


# ---------------------------------------------------------------------------
# 7. L3 黑名单 / 审计回调 / 工厂
# ---------------------------------------------------------------------------


def test_l3_blacklist_returns_not_triggered() -> None:
    detector = HallucinationDetector()
    r = detector.detect(
        "pure code skeleton",
        {},
        RiskLevel.L,
        trigger_level=TriggerLevel.L3_BLACKLIST,
    )
    assert r.triggered is False
    assert r.is_hallucination is False


def test_audit_logger_invoked_exactly_once() -> None:
    calls: list[HallucinationResult] = []

    def logger(result: HallucinationResult) -> None:
        calls.append(result)

    detector = HallucinationDetector(audit_logger=logger)
    detector.detect("无关 claim", {}, RiskLevel.L)
    assert len(calls) == 1
    assert calls[0].triggered is True


def test_claim_hash_stable() -> None:
    h1 = HallucinationDetector.claim_hash("abc")
    h2 = HallucinationDetector.claim_hash("abc")
    h3 = HallucinationDetector.claim_hash("abd")
    assert h1 == h2
    assert h1 != h3
    assert h1.startswith("claim#sha256:")


def test_build_detector_factory_has_default_budget() -> None:
    d = build_detector_with_defaults()
    assert isinstance(d.budget_state, BudgetState)
    assert d.budget_state.monthly_budget_usd == 15.0
    assert d.budget_state.daily_budget_usd == 0.75


def test_empty_claim_raises() -> None:
    detector = HallucinationDetector()
    with pytest.raises(ValueError):
        detector.detect("   ", {}, RiskLevel.L)
