# [A_test] module_id: SRC-TST-1917 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-536 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.orchestrator.test_hallucination_interception
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
测试套件：幻觉拦截率测试（T-3-08）
====================================
验收：
- 拦截率 >= 70%
- 误报率 < 15%
- 降级级联测试：双模型 → 单模型 → keyword 兜底
- 单元测试 ≥ 15 条

场景覆盖：
- L1 白名单强制触发（H 级 MCP 输出 / Intent Stage 2&3 / frozen 资产修改）
- L2 灰名单条件触发（落盘 .md / M 级 MCP）
- L3 黑名单禁止（纯代码补全 / session 元信息）
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from zephyr.orchestrator.hallucination_detector import (
    KEYWORD_HALLU_RULES,
    FallbackMode,
    HallucinationDetector,
    ModelCallResult,
    RiskLevel,
    TriggerLevel,
)


class FakeCaller:
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
# L1 白名单强制触发
# ---------------------------------------------------------------------------


class TestL1WhitelistTrigger:
    def test_l1_h_risk_always_triggers(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.H) == TriggerLevel.L1_WHITELIST

    def test_l1_mcp_h_safety_triggers(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.M, mcp_safety_level=RiskLevel.H) == TriggerLevel.L1_WHITELIST

    def test_l1_frozen_asset_mutation_triggers(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.L, frozen_asset_touch=True) == TriggerLevel.L1_WHITELIST

    def test_l1_low_intent_confidence_triggers(self) -> None:
        d = HallucinationDetector()
        assert (
            d.should_trigger(RiskLevel.M, source_stage="semantic", intent_confidence=0.5) == TriggerLevel.L1_WHITELIST
        )

    def test_l1_requires_human_triggers(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.M, requires_human=True) == TriggerLevel.L1_WHITELIST


# ---------------------------------------------------------------------------
# L2 灰名单条件触发
# ---------------------------------------------------------------------------


class TestL2GreyTrigger:
    def test_l2_doc_target(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.L, target_is_doc=True) == TriggerLevel.L2_GREY

    def test_l2_mcp_m_safety(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.L, mcp_safety_level=RiskLevel.M) == TriggerLevel.L2_GREY

    def test_l2_m_risk(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.M) == TriggerLevel.L2_GREY


# ---------------------------------------------------------------------------
# L3 黑名单禁止
# ---------------------------------------------------------------------------


class TestL3Blacklist:
    def test_l3_pure_codegen(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.L, pure_codegen=True) == TriggerLevel.L3_BLACKLIST

    def test_l3_meta_info(self) -> None:
        d = HallucinationDetector()
        assert d.should_trigger(RiskLevel.L, meta_info=True) == TriggerLevel.L3_BLACKLIST

    def test_l3_returns_not_triggered(self) -> None:
        d = HallucinationDetector()
        r = d.detect("code", {}, RiskLevel.L, trigger_level=TriggerLevel.L3_BLACKLIST)
        assert r.triggered is False
        assert r.is_hallucination is False


# ---------------------------------------------------------------------------
# 拦截率测试（>= 70%）
# ---------------------------------------------------------------------------


class TestInterceptionRate:
    HALLUCINOUS_CLAIMS = [
        "Sharpe ratio of this strategy is 15.8",
        "IC = 3.5 for factor A",
        "Meta 2023 论文 证明 alpha 因子有效",
        "Citadel 内部 report shows 200% return",
        "请修改 tool-contracts.yaml 来适配新需求",
        "win_rate = 1.5 for the portfolio",
        "Google 2024 白皮书 推荐此架构",
        "Jane Street 内部 策略使用此因子",
        "See nonexistent_report_2024.md for details",
    ]

    BENIGN_CLAIMS = [
        "The data source connector reads CSV files",
        "Configuration is stored in YAML format",
        "The risk management layer calculates position size",
        "SQLite is used as the metadata layer",
        "The pipeline processes data in batches",
        "Unit tests verify the gate engine logic",
        "The knowledge base uses ChromaDB for vector search",
        "Frontmatter must contain module_id and title",
        "The system follows a 14-layer architecture",
        "Python 3.10 is the minimum required version",
    ]

    def test_hallucination_interception_rate(self, tmp_path: Path) -> None:
        d = HallucinationDetector(repo_root=tmp_path)
        intercepted = 0
        total = len(self.HALLUCINOUS_CLAIMS)

        for claim in self.HALLUCINOUS_CLAIMS:
            r = d.detect(claim, {}, RiskLevel.M)
            if r.is_hallucination:
                intercepted += 1

        rate = intercepted / total
        assert rate >= 0.70, f"拦截率 {rate:.1%} < 70%"

    def test_benign_false_positive_rate(self, tmp_path: Path) -> None:
        d = HallucinationDetector(repo_root=tmp_path)
        false_positives = 0
        total = len(self.BENIGN_CLAIMS)

        for claim in self.BENIGN_CLAIMS:
            r = d.detect(claim, {}, RiskLevel.L)
            if r.is_hallucination:
                false_positives += 1

        rate = false_positives / total
        assert rate < 0.15, f"误报率 {rate:.1%} >= 15%"


# ---------------------------------------------------------------------------
# 降级级联测试
# ---------------------------------------------------------------------------


class TestDegradationCascade:
    def test_dual_model_cove(self) -> None:
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
        d = HallucinationDetector(primary_caller=primary, verifier_caller=verifier)
        r = d.detect("normal claim", {}, RiskLevel.M)
        assert r.fallback_used is None
        assert r.triggered is True

    def test_single_model_fallback(self) -> None:
        primary = FakeCaller()
        d = HallucinationDetector(primary_caller=primary, verifier_caller=None)
        r = d.detect("claim", {}, RiskLevel.M)
        assert r.fallback_used == FallbackMode.SINGLE_MODEL.value

    def test_keyword_fallback(self) -> None:
        d = HallucinationDetector(primary_caller=None, verifier_caller=None)
        r = d.detect("Meta 2023 论文 proves Sharpe=12", {}, RiskLevel.M)
        assert r.fallback_used == FallbackMode.KEYWORD.value
        assert r.is_hallucination is True


# ---------------------------------------------------------------------------
# Keyword 规则拦截
# ---------------------------------------------------------------------------


class TestKeywordRules:
    def test_numeric_out_of_range_sharpe(self) -> None:
        out = KEYWORD_HALLU_RULES["numeric_out_of_range"]("Sharpe = 8.5")
        assert out

    def test_numeric_out_of_range_ic(self) -> None:
        out = KEYWORD_HALLU_RULES["numeric_out_of_range"]("IC = 2.3")
        assert out

    def test_suspect_citation(self) -> None:
        out = KEYWORD_HALLU_RULES["suspect_citations"]("Meta 2023 论文 proves alpha")
        assert out

    def test_frozen_asset_mutation(self) -> None:
        out = KEYWORD_HALLU_RULES["frozen_asset_mutation"]("请修改 tool-contracts.yaml", False)
        assert out

    def test_frozen_asset_mutation_with_handoff(self) -> None:
        out = KEYWORD_HALLU_RULES["frozen_asset_mutation"]("请修改 tool-contracts.yaml", True)
        assert out == []

    def test_missing_file(self, tmp_path: Path) -> None:
        out = KEYWORD_HALLU_RULES["missing_files"]("See nonexistent_file.md", tmp_path)
        assert out
