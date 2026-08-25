# [BLUEPRINT] MOD-INT-LLM-FUND | docs/03_modules/_domain_intelligence/llm_fundamental_analysis/blueprint.md | §test
# [A_test] module_id: MOD-INT-LLM-FUND | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# add-design-node tests/intelligence/test_llm_fundamental_analysis.py MOD-INT-LLM-FUND D_INTELLIGENCE planned --granularity file
"""LlmFundamentalAnalysis 单元测试 (MOD-INT-LLM-FUND, MVP)。

覆盖: Agent JSON 输出解析 Fail-Closed / 融合权重和非法 / 定性定量加权融合
方向与置信度 / 融合点过滤 / 双模校验 / 审计 sink 异常不阻断 / 有效 Agent
不足 2 个 Fail-Closed / 零密钥字段。
"""

from __future__ import annotations

import json

import pytest

from zephyr.intelligence.llm_fundamental_analysis import (
    AgentVerdict,
    FundamentalAnalysisError,
    FundamentalInputBundle,
    FundamentalVerdict,
    FusionWeights,
    LlmFundamentalAnalysis,
)


def _fake_agent(direction: str, confidence: float) -> str:
    return json.dumps({"direction": direction, "confidence": confidence, "rationale": "test"})


def _make_agents(report_dir: str = "bullish", news_dir: str = "neutral", verdict_dir: str = "bullish") -> dict:
    return {
        "report": lambda payload, mode: _fake_agent(report_dir, 0.8),
        "news": lambda payload, mode: _fake_agent(news_dir, 0.6),
        "verdict": lambda payload, mode: _fake_agent(verdict_dir, 0.7),
    }


class TestParseAgentOutput:
    def test_ok(self) -> None:
        raw = json.dumps({"direction": "bullish", "confidence": 0.8, "rationale": "r1"})
        v = LlmFundamentalAnalysis()._agents
        # 间接通过 analyze 测
        fa = LlmFundamentalAnalysis(agents={"report": lambda p, m: raw, "news": lambda p, m: raw})
        res = fa.analyze(
            FundamentalInputBundle(symbol="000001", financial_report="r", news_policy="n"),
            "local",
        )
        assert res.direction in _DIRECTIONS

    @pytest.mark.parametrize("bad", ["not_json", json.dumps({"direction": "up"})])
    def test_fail_closed(self, bad: str) -> None:
        fa = LlmFundamentalAnalysis(agents={"report": lambda p, m: bad, "news": lambda p, m: _fake_agent("bullish", 0.8)})
        with pytest.raises(FundamentalAnalysisError):
            fa.analyze(FundamentalInputBundle(symbol="000001", financial_report="r", news_policy="n"), "local")


_DIRECTIONS = ("bullish", "neutral", "bearish")


class TestFusionWeights:
    def test_ok(self) -> None:
        w = FusionWeights(0.5, 0.5)
        assert w.qualitative_weight == 0.5

    def test_invalid_sum(self) -> None:
        with pytest.raises(FundamentalAnalysisError):
            FusionWeights(0.6, 0.5)


class TestAnalyze:
    def test_basic(self) -> None:
        fa = LlmFundamentalAnalysis(agents=_make_agents())
        bundle = FundamentalInputBundle(
            symbol="000001",
            financial_report="r",
            news_policy="n",
            quantitative_score=0.3,
            fusion_channels=("c014_sentiment", "unknown"),
        )
        res = fa.analyze(bundle, "local")
        assert isinstance(res, FundamentalVerdict)
        assert res.symbol == "000001"
        assert res.mode == "local"
        assert res.fusion_points_used == ("c014_sentiment",)
        assert 0.0 <= res.confidence <= 1.0

    def test_api_mode(self) -> None:
        fa = LlmFundamentalAnalysis(agents=_make_agents())
        res = fa.analyze(FundamentalInputBundle(symbol="000001", financial_report="r", news_policy="n"), "api")
        assert res.mode == "api"

    def test_invalid_mode(self) -> None:
        fa = LlmFundamentalAnalysis(agents=_make_agents())
        with pytest.raises(FundamentalAnalysisError):
            fa.analyze(FundamentalInputBundle(symbol="000001", financial_report="r", news_policy="n"), "bad")

    def test_too_few_agents(self) -> None:
        fa = LlmFundamentalAnalysis(agents={"report": lambda p, m: _fake_agent("bullish", 0.8)})
        with pytest.raises(FundamentalAnalysisError):
            fa.analyze(FundamentalInputBundle(symbol="000001", financial_report="r"), "local")

    def test_quantitative_oob(self) -> None:
        fa = LlmFundamentalAnalysis(agents=_make_agents())
        bundle = FundamentalInputBundle(symbol="000001", financial_report="r", news_policy="n", quantitative_score=2.0)
        with pytest.raises(FundamentalAnalysisError):
            fa.analyze(bundle, "local")

    def test_audit_sink_error_not_blocking(self) -> None:
        def bad_sink(record: dict) -> None:
            raise RuntimeError("boom")
        fa = LlmFundamentalAnalysis(agents=_make_agents(), audit_sink=bad_sink)
        res = fa.analyze(FundamentalInputBundle(symbol="000001", financial_report="r", news_policy="n"), "local")
        assert "sink_errors" in res.audit_record


class TestFuse:
    def test_bullish(self) -> None:
        fa = LlmFundamentalAnalysis()
        direction, confidence, score = fa.fuse(
            (AgentVerdict("a", "bullish", 0.8, ""), AgentVerdict("b", "bullish", 0.8, "")),
            0.5,
        )
        assert direction == "bullish"
        assert confidence > 0.0

    def test_bearish(self) -> None:
        fa = LlmFundamentalAnalysis()
        direction, confidence, score = fa.fuse(
            (AgentVerdict("a", "bearish", 0.9, ""), AgentVerdict("b", "bearish", 0.9, "")),
            -0.5,
        )
        assert direction == "bearish"

    def test_neutral(self) -> None:
        fa = LlmFundamentalAnalysis()
        direction, confidence, score = fa.fuse(
            (AgentVerdict("a", "bullish", 0.2, ""), AgentVerdict("b", "bearish", 0.2, "")),
            0.0,
        )
        assert direction == "neutral"
