# [A_test] module_id: SRC-TST-1337 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_orchestrator_hallucination_detector
# [INVARIANTS] HallucinationDetector uses keyword fallback when no callers provided
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_orchestrator_hallucination_detector.py
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from zephyr.orchestrator.hallucination_detector import (
    BudgetState,
    FallbackMode,
    HallucinationDetector,
    HallucinationResult,
    ModelCallResult,
    RiskLevel,
    TriggerLevel,
    _contains_negation,
    _frozen_asset_mutation,
    _missing_files,
    _numeric_out_of_range,
    _suspect_citations,
    _token_overlap,
    build_detector_with_defaults,
)


class TestRiskLevel:
    def test_values(self):
        assert RiskLevel.L.value == "L"
        assert RiskLevel.M.value == "M"
        assert RiskLevel.H.value == "H"


class TestTriggerLevel:
    def test_values(self):
        assert TriggerLevel.L1_WHITELIST.value == "L1"
        assert TriggerLevel.L2_GREY.value == "L2"
        assert TriggerLevel.L3_BLACKLIST.value == "L3"


class TestFallbackMode:
    def test_values(self):
        assert FallbackMode.NONE.value == "none"
        assert FallbackMode.SINGLE_MODEL.value == "single_model"
        assert FallbackMode.KEYWORD.value == "keyword"
        assert FallbackMode.BUDGET_SKIP.value == "budget_skip"


class TestModelCallResult:
    def test_defaults(self):
        r = ModelCallResult()
        assert r.content == ""
        assert r.cost_usd == 0.0
        assert r.latency_ms == 0
        assert r.success is True
        assert r.error is None

    def test_custom_values(self):
        r = ModelCallResult(content="hello", cost_usd=0.01, latency_ms=100, success=False, error="timeout")
        assert r.content == "hello"
        assert r.cost_usd == 0.01
        assert r.success is False
        assert r.error == "timeout"


class TestHallucinationResult:
    def test_minimal_creation(self):
        r = HallucinationResult(
            claim="test claim", is_hallucination=False, confidence=0.9, risk_level="L", inconsistency_score=0.1
        )
        assert r.claim == "test claim"
        assert r.is_hallucination is False
        assert r.triggered is True

    def test_verify_questions_max_5(self):
        with pytest.raises(ValueError):
            HallucinationResult(
                claim="test",
                is_hallucination=False,
                confidence=0.9,
                risk_level="L",
                inconsistency_score=0.1,
                verify_questions=["q1", "q2", "q3", "q4", "q5", "q6"],
            )


class TestBudgetState:
    def test_default_budgets(self):
        b = BudgetState()
        assert b.monthly_budget_usd == 15.0
        assert b.daily_budget_usd == 0.75
        assert b.per_call_max_usd == 0.02

    def test_can_afford_under_budget(self):
        b = BudgetState()
        assert b.can_afford(RiskLevel.L) is True
        assert b.can_afford(RiskLevel.M) is True
        assert b.can_afford(RiskLevel.H) is True

    def test_can_afford_over_daily_budget(self):
        b = BudgetState(daily_spent_usd=1.0)
        assert b.can_afford(RiskLevel.L) is False
        assert b.can_afford(RiskLevel.M) is False
        assert b.can_afford(RiskLevel.H) is True

    def test_record_increments_spent(self):
        b = BudgetState()
        b.record(0.5)
        assert b.daily_spent_usd == 0.5
        assert b.monthly_spent_usd == 0.5

    def test_reset_if_window_changed_day(self):
        b = BudgetState(current_day="2026-01-01", daily_spent_usd=1.0)
        now = datetime(2026, 1, 2, tzinfo=UTC)
        b.reset_if_window_changed(now)
        assert b.daily_spent_usd == 0.0
        assert b.current_day == "2026-01-02"

    def test_reset_if_window_changed_month(self):
        b = BudgetState(current_month="2026-01", monthly_spent_usd=5.0)
        now = datetime(2026, 2, 1, tzinfo=UTC)
        b.reset_if_window_changed(now)
        assert b.monthly_spent_usd == 0.0
        assert b.current_month == "2026-02"


class TestKeywordRules:
    def test_numeric_out_of_range_ic(self):
        evidence = _numeric_out_of_range("IC = 1.5 is great")
        assert len(evidence) == 1
        assert "numeric_out_of_range" in evidence[0]

    def test_numeric_out_of_range_sharpe(self):
        evidence = _numeric_out_of_range("Sharpe = 6.0")
        assert len(evidence) == 1

    def test_numeric_out_of_range_normal(self):
        evidence = _numeric_out_of_range("IC = 0.3 is normal")
        assert len(evidence) == 0

    def test_missing_files_with_nonexistent(self, tmp_path):
        evidence = _missing_files("see docs/nonexistent.md for details", tmp_path)
        assert len(evidence) >= 1
        assert "missing_file" in evidence[0]

    def test_missing_files_none_root(self):
        evidence = _missing_files("see docs/test.md", None)
        assert evidence == []

    def test_suspect_citations_meta(self):
        evidence = _suspect_citations("Meta 2024 论文证明了这一点")
        assert len(evidence) >= 1

    def test_suspect_citations_clean(self):
        evidence = _suspect_citations("This is a normal claim")
        assert evidence == []

    def test_frozen_asset_mutation_without_handoff(self):
        evidence = _frozen_asset_mutation("修改 tool-contracts.yaml 中的配置", handoff_approved=False)
        assert len(evidence) >= 1

    def test_frozen_asset_mutation_with_handoff(self):
        evidence = _frozen_asset_mutation("修改 tool-contracts.yaml 中的配置", handoff_approved=True)
        assert evidence == []


class TestTokenOverlap:
    def test_identical_strings(self):
        assert _token_overlap("hello world", "hello world") == 1.0

    def test_no_overlap(self):
        assert _token_overlap("aaa bbb", "ccc ddd") == 0.0

    def test_partial_overlap(self):
        overlap = _token_overlap("hello world", "hello python")
        assert 0.0 < overlap < 1.0

    def test_empty_strings(self):
        assert _token_overlap("", "") == 1.0

    def test_one_empty(self):
        assert _token_overlap("hello", "") == 0.0


class TestContainsNegation:
    def test_english_negation(self):
        assert _contains_negation("this is not correct") is True

    def test_chinese_negation(self):
        assert _contains_negation("这是不对的") is True

    def test_no_negation(self):
        assert _contains_negation("this is correct") is False


class TestHallucinationDetectorShouldTrigger:
    def test_pure_codegen_blacklist(self):
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.L, pure_codegen=True) == TriggerLevel.L3_BLACKLIST

    def test_meta_info_blacklist(self):
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.L, meta_info=True) == TriggerLevel.L3_BLACKLIST

    def test_low_confidence_whitelist(self):
        d = HallucinationDetector()
        result = d.should_trigger(RiskLevel.L, source_stage="semantic", intent_confidence=0.5)
        assert result == TriggerLevel.L1_WHITELIST

    def test_high_confidence_no_whitelist(self):
        d = HallucinationDetector()
        result = d.should_trigger(RiskLevel.L, source_stage="semantic", intent_confidence=0.95)
        assert result == TriggerLevel.L2_GREY

    def test_mcp_safety_h_whitelist(self):
        d = HallucinationDetector()
        result = d.should_trigger(RiskLevel.L, mcp_safety_level=RiskLevel.H)
        assert result == TriggerLevel.L1_WHITELIST

    def test_requires_human_whitelist(self):
        d = HallucinationDetector()
        result = d.should_trigger(RiskLevel.L, requires_human=True)
        assert result == TriggerLevel.L1_WHITELIST

    def test_frozen_asset_whitelist(self):
        d = HallucinationDetector()
        result = d.should_trigger(RiskLevel.L, frozen_asset_touch=True)
        assert result == TriggerLevel.L1_WHITELIST

    def test_risk_h_whitelist(self):
        d = HallucinationDetector()
        result = d.should_trigger(RiskLevel.H)
        assert result == TriggerLevel.L1_WHITELIST

    def test_target_is_doc_grey(self):
        d = HallucinationDetector()
        result = d.should_trigger(RiskLevel.L, target_is_doc=True)
        assert result == TriggerLevel.L2_GREY


class TestHallucinationDetectorDetectKeywordFallback:
    def test_keyword_fallback_clean_claim(self):
        d = HallucinationDetector()
        result = d.detect("normal claim with no issues", risk_level=RiskLevel.L)
        assert result.triggered is True
        assert result.fallback_used == FallbackMode.KEYWORD.value
        assert result.is_hallucination is False

    def test_keyword_fallback_suspicious_claim(self):
        d = HallucinationDetector()
        result = d.detect("IC = 2.0 is the best indicator", risk_level=RiskLevel.M)
        assert result.is_hallucination is True
        assert result.fallback_used == FallbackMode.KEYWORD.value

    def test_empty_claim_raises(self):
        d = HallucinationDetector()
        with pytest.raises(ValueError):
            d.detect("", risk_level=RiskLevel.L)

    def test_whitespace_claim_raises(self):
        d = HallucinationDetector()
        with pytest.raises(ValueError):
            d.detect("   ", risk_level=RiskLevel.L)

    def test_l3_blacklist_skips(self):
        d = HallucinationDetector()
        result = d.detect("some claim", risk_level=RiskLevel.L, trigger_level=TriggerLevel.L3_BLACKLIST)
        assert result.triggered is False
        assert result.is_hallucination is False
        assert result.confidence == 1.0


class TestHallucinationDetectorDetectSingleModel:
    def test_single_model_primary_only(self):
        def mock_primary(prompt, *, purpose):
            return ModelCallResult(
                content=json.dumps(
                    {
                        "baseline_answer": "test answer",
                        "verify_questions": ["q1?", "q2?", "q3?"],
                    }
                ),
                cost_usd=0.001,
                success=True,
            )

        d = HallucinationDetector(primary_caller=mock_primary)
        result = d.detect("normal claim", risk_level=RiskLevel.L)
        assert result.fallback_used == FallbackMode.SINGLE_MODEL.value
        assert result.triggered is True


class TestHallucinationDetectorDetectFullCoVe:
    def test_full_cove_consistent(self):
        def mock_primary(prompt, *, purpose):
            return ModelCallResult(
                content=json.dumps(
                    {
                        "baseline_answer": "the sky is blue",
                        "verify_questions": ["what color is the sky?", "is the sky blue?", "does the sky appear blue?"],
                    }
                ),
                cost_usd=0.001,
                success=True,
            )

        def mock_verifier(prompt, *, purpose):
            return ModelCallResult(
                content=json.dumps(
                    [
                        {"question": "what color is the sky?", "answer": "blue", "confidence_self": 0.9},
                        {"question": "is the sky blue?", "answer": "yes it is blue", "confidence_self": 0.95},
                        {"question": "does the sky appear blue?", "answer": "the sky is blue", "confidence_self": 0.9},
                    ]
                ),
                cost_usd=0.001,
                success=True,
            )

        d = HallucinationDetector(primary_caller=mock_primary, verifier_caller=mock_verifier)
        result = d.detect("the sky is blue", risk_level=RiskLevel.L)
        assert result.triggered is True
        assert result.fallback_used is None
        assert len(result.verify_questions) == 3

    def test_full_cove_step1_failure_falls_back(self):
        def mock_primary(prompt, *, purpose):
            return ModelCallResult(success=False, error="API unreachable")

        d = HallucinationDetector(
            primary_caller=mock_primary,
            verifier_caller=lambda p, **kw: ModelCallResult(content="[]", cost_usd=0.001, success=True),
        )
        result = d.detect("some claim", risk_level=RiskLevel.L)
        assert result.fallback_used == FallbackMode.KEYWORD.value


class TestHallucinationDetectorBudgetSkip:
    def test_budget_skip_for_l_risk(self):
        d = HallucinationDetector()
        today = datetime.now(UTC).date().isoformat()
        d._budget.current_day = today
        d._budget.current_month = datetime.now(UTC).strftime("%Y-%m")
        d._budget.daily_spent_usd = 1.0
        result = d.detect("normal claim", risk_level=RiskLevel.L)
        assert result.fallback_used == FallbackMode.BUDGET_SKIP.value
        assert result.triggered is False

    def test_h_risk_forces_through_budget(self):
        d = HallucinationDetector()
        d._budget.daily_spent_usd = 1.0
        result = d.detect("normal claim", risk_level=RiskLevel.H)
        assert result.triggered is True


class TestHallucinationDetectorClaimHash:
    def test_claim_hash_deterministic(self):
        h1 = HallucinationDetector.claim_hash("test claim")
        h2 = HallucinationDetector.claim_hash("test claim")
        assert h1 == h2

    def test_claim_hash_different_claims(self):
        h1 = HallucinationDetector.claim_hash("claim a")
        h2 = HallucinationDetector.claim_hash("claim b")
        assert h1 != h2


class TestBuildDetectorWithDefaults:
    def test_creates_detector(self):
        d = build_detector_with_defaults()
        assert isinstance(d, HallucinationDetector)
