# [BLUEPRINT] MOD-INT-LLM-FUND | docs/03_modules/_domain_intelligence/llm_fundamental_analysis/blueprint.md | §0-5
# [MODULE] zephyr.intelligence.llm_fundamental_analysis
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.foundation.errors(ZephyrBaseError)
# [CONSUMERS] 运行时装配批（report/news/verdict Agent callable 装配 / 四融合点输入 / audit_sink 接审计链）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定核心纯内存无IO; LLM输出须合法JSON四字段且值域合规否则 FundamentalAnalysisError fail-closed; 置信度恒∈[0,1]; 定量分恒∈[-1,1]; 权重和恒=1(容差1e-6); 仅信号输入无下单语义; 零密钥字段
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/llm_fundamental_analysis/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FundamentalAnalysisError(ZA-IT-0018)
# [TESTS] tests/intelligence/test_llm_fundamental_analysis.py
# [A_module] module_id=MOD-INT-LLM-FUND | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""LlmFundamentalAnalysis — LLM Agent 基本面分析（MOD-INT-LLM-FUND）。

B10-01840（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§29.11）：三 Agent
（财报质量/新闻政策/综合裁决）+ 定性定量加权融合 + 4 融合点留痕；
本地盘后+API 盘中双模；结论仅作信号输入不直接下单。

查重裁定：不复制 llm_market_interpreter（三路市场解读）、llm_premarket_analysis
（盘前复盘单点）、news_sentiment_analyzer（单路新闻情感）；新闻政策 Agent
可经注入 callable 复用既有解读产物，不复制其逻辑。
"""

from __future__ import annotations

import datetime
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_log = logging.getLogger(__name__)

__all__: Final = [
    "AgentVerdict",
    "FundamentalAnalysisError",
    "FundamentalInputBundle",
    "FundamentalVerdict",
    "FusionWeights",
    "LlmFundamentalAnalysis",
]

_MODES: Final = ("local", "api")
_DIRECTIONS: Final = ("bullish", "neutral", "bearish")
_FUSION_CHANNELS: Final = frozenset({"c014_sentiment", "c016_event", "funnel_l4", "c013_directive"})


class FundamentalAnalysisError(ZephyrBaseError):
    """LLM Agent 输出结构非法或融合参数越界（Fail-Closed）。"""

    error_code = "ZA-IT-0018"


@dataclass(frozen=True)
class AgentVerdict:
    """单 Agent 裁决。"""

    agent: str
    direction: str
    confidence: float
    rationale: str


@dataclass(frozen=True)
class FundamentalInputBundle:
    """基本面输入包。"""

    symbol: str
    financial_report: str = ""
    news_policy: str = ""
    quantitative_score: float = 0.0
    fusion_channels: tuple[str, ...] = ()
    as_of: datetime.datetime | None = None


@dataclass(frozen=True)
class FundamentalVerdict:
    """最终基本面裁决。"""

    symbol: str
    direction: str
    confidence: float
    fused_score: float
    agent_verdicts: tuple[AgentVerdict, ...]
    fusion_points_used: tuple[str, ...]
    mode: str
    audit_record: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FusionWeights:
    """融合权重（qualitative + quantitative = 1）。"""

    qualitative_weight: float = 0.6
    quantitative_weight: float = 0.4

    def __post_init__(self) -> None:
        total = self.qualitative_weight + self.quantitative_weight
        if abs(total - 1.0) > 1e-6:
            raise FundamentalAnalysisError(f"权重和须=1，实际={total}")


def _parse_agent_output(agent: str, raw: str) -> AgentVerdict:
    """解析 Agent JSON 输出并校验值域。"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FundamentalAnalysisError(f"{agent} 输出非 JSON: {exc}") from exc
    for key in ("direction", "confidence", "rationale"):
        if key not in data:
            raise FundamentalAnalysisError(f"{agent} 输出缺字段 {key}")
    direction = data["direction"]
    if direction not in _DIRECTIONS:
        raise FundamentalAnalysisError(f"{agent} direction 非法: {direction}")
    confidence = float(data["confidence"])
    if not (0.0 <= confidence <= 1.0):
        raise FundamentalAnalysisError(f"{agent} confidence 越界: {confidence}")
    return AgentVerdict(
        agent=agent,
        direction=direction,
        confidence=confidence,
        rationale=str(data.get("rationale", "")),
    )


def _fuse(verdicts: tuple[AgentVerdict, ...], quantitative: float, weights: FusionWeights) -> tuple[str, float, float]:
    """定性定量加权融合 → (direction, confidence, fused_score)。"""
    if not (-1.0 <= quantitative <= 1.0):
        raise FundamentalAnalysisError(f"定量分越界: {quantitative}")
    direction_scores = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}
    qual_score = 0.0
    for v in verdicts:
        qual_score += direction_scores.get(v.direction, 0.0) * v.confidence
    if verdicts:
        qual_score /= len(verdicts)
    fused = weights.qualitative_weight * qual_score + weights.quantitative_weight * quantitative
    if fused > 0.2:
        direction = "bullish"
    elif fused < -0.2:
        direction = "bearish"
    else:
        direction = "neutral"
    confidence = min(1.0, abs(fused))
    return direction, confidence, fused


class LlmFundamentalAnalysis:
    """基本面分析判定核心（纯内存，无 IO）。"""

    def __init__(
        self,
        weights: FusionWeights | None = None,
        agents: dict[str, Callable[[str, str], str]] | None = None,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._weights = weights or FusionWeights()
        self._agents = agents or {}
        self._audit_sink = audit_sink

    def analyze(self, bundle: FundamentalInputBundle, mode: str) -> FundamentalVerdict:
        """执行三 Agent 分析 + 融合。"""
        if mode not in _MODES:
            raise FundamentalAnalysisError(f"未知 mode: {mode}")
        verdicts: list[AgentVerdict] = []
        for role, agent_fn in self._agents.items():
            if role in ("report", "news", "verdict"):
                payload = bundle.financial_report if role == "report" else bundle.news_policy if role == "news" else ""
                try:
                    raw = agent_fn(payload, mode)
                except Exception as exc:
                    raise FundamentalAnalysisError(f"{role} Agent 调用异常: {exc}") from exc
                verdicts.append(_parse_agent_output(role, raw))
        if len(verdicts) < 2:
            raise FundamentalAnalysisError(f"有效 Agent 裁决不足 2 个: {len(verdicts)}")
        direction, confidence, fused = _fuse(tuple(verdicts), bundle.quantitative_score, self._weights)
        fusion_points_used = tuple(ch for ch in bundle.fusion_channels if ch in _FUSION_CHANNELS)
        audit: dict[str, Any] = {
            "symbol": bundle.symbol,
            "mode": mode,
            "agent_verdicts": [dataclasses.asdict(v) for v in verdicts],
            "direction": direction,
            "confidence": confidence,
            "fused_score": fused,
            "fusion_points_used": list(fusion_points_used),
            "as_of": bundle.as_of.isoformat() if bundle.as_of else None,
        }
        if self._audit_sink is not None:
            try:
                self._audit_sink(audit)
            except Exception as exc:
                audit.setdefault("sink_errors", []).append(str(exc))
        return FundamentalVerdict(
            symbol=bundle.symbol,
            direction=direction,
            confidence=confidence,
            fused_score=fused,
            agent_verdicts=tuple(verdicts),
            fusion_points_used=fusion_points_used,
            mode=mode,
            audit_record=audit,
        )

    def fuse(
        self,
        verdicts: tuple[AgentVerdict, ...],
        quantitative: float,
        weights: FusionWeights | None = None,
    ) -> tuple[str, float, float]:
        """外部可调融合（供测试/复用）。"""
        w = weights or self._weights
        return _fuse(verdicts, quantitative, w)


import dataclasses
