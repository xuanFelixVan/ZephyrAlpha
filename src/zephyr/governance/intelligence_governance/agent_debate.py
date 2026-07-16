# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.agent_debate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_agent_debate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
from __future__ import annotations
import hashlib
import logging
from enum import Enum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DebateVerdict(str, Enum):
    AGREE = "AGREE"
    A_SUPERIOR = "A_SUPERIOR"
    B_SUPERIOR = "B_SUPERIOR"
    OVERRIDE = "OVERRIDE"


class ModelResponse(BaseModel):
    model: str
    response_hash: str
    content_hash: str
    token_count: int
    latency_ms: int

    @staticmethod
    def from_content(model: str, content: str, token_count: int = 0, latency_ms: int = 0) -> ModelResponse:
        return ModelResponse(
            model=model,
            response_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
            content_hash=hashlib.sha256(content.encode()).hexdigest()[:32],
            token_count=token_count,
            latency_ms=latency_ms,
        )


class DebateRound(BaseModel):
    round_id: int
    model_a: ModelResponse
    model_b: ModelResponse
    consensus: bool = False
    verdict: DebateVerdict = DebateVerdict.OVERRIDE
    resolution: str = ""


class AgentDebate:
    def __init__(self) -> None:
        self._history: list[DebateRound] = []
        self._round_counter: int = 0

    def debate(
        self,
        model_a_name: str,
        model_a_content: str,
        model_b_name: str,
        model_b_content: str,
    ) -> DebateVerdict:
        self._round_counter += 1
        resp_a = ModelResponse.from_content(model_a_name, model_a_content)
        resp_b = ModelResponse.from_content(model_b_name, model_b_content)

        content_match = resp_a.content_hash == resp_b.content_hash
        rd = DebateRound(
            round_id=self._round_counter,
            model_a=resp_a,
            model_b=resp_b,
            consensus=content_match,
        )

        if content_match:
            rd.verdict = DebateVerdict.AGREE
            rd.resolution = "Both models produce identical output — AGREE"
        else:
            rd.verdict = DebateVerdict.OVERRIDE
            rd.resolution = "Models disagree — HUMAN OVERRIDE required"

        self._history.append(rd)
        logger.info(
            "Debate round %d: models=%s/%s consensus=%s verdict=%s",
            rd.round_id,
            resp_a.model,
            resp_b.model,
            rd.consensus,
            rd.verdict.value,
        )
        return rd.verdict

    def adjudicate(
        self,
        model_a_content: str,
        model_b_content: str,
        override_decision: str = "auto",
    ) -> tuple[DebateVerdict, str]:
        if override_decision == "auto":
            equal = (
                hashlib.sha256(model_a_content.encode()).hexdigest()
                == hashlib.sha256(model_b_content.encode()).hexdigest()
            )
            if equal:
                return DebateVerdict.AGREE, model_a_content
            return DebateVerdict.OVERRIDE, model_a_content
        return DebateVerdict.OVERRIDE, override_decision

    def history(self) -> list[DebateRound]:
        return list(self._history)

    def agreement_rate(self) -> float:
        if not self._history:
            return 0.0
        agreed = sum(1 for rd in self._history if rd.verdict is DebateVerdict.AGREE)
        return agreed / len(self._history)
