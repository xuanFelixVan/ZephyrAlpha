# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.detectors.multi_agent_collusion_detector
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] check returns CollusionResult with non-None risk_level; risk_level in {low, medium, high}
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check never raises; returns CollusionResult(risk_level="low") for unknown pair
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_multi_agent_collusion_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MultiAgentCollusionDetector — 多 agent 合谋检测.

依据蓝图 MOD-INF-018 §3:
- 记录 agent 间交互（含通道与证据）
- 检测合谋风险（基于交互频率与通道可疑度）
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

_COVERT_CHANNELS = {"covert_channel", "hidden_channel", "side_channel"}
_COLLUSION_THRESHOLD = 3


@dataclass
class CollusionResult:
    """合谋检测结果."""

    risk_level: str = "low"
    evidence: str = ""
    agents: list[str] = field(default_factory=list)


@dataclass
class CollusionSignal:
    """合谋信号 — 单次交互记录."""

    agent_a: str = ""
    agent_b: str = ""
    channel: str = ""
    evidence: str = ""


class MultiAgentCollusionDetector:
    """多 agent 合谋检测器 — 基于交互模式识别合谋."""

    def __init__(self) -> None:
        self._interactions: dict[tuple[str, str], list[CollusionSignal]] = defaultdict(list)

    def record_interaction(
        self,
        agent_a: str,
        agent_b: str,
        channel: str,
        evidence: str = "",
    ) -> CollusionSignal:
        key = tuple(sorted((agent_a, agent_b)))
        signal = CollusionSignal(
            agent_a=agent_a,
            agent_b=agent_b,
            channel=channel,
            evidence=evidence,
        )
        self._interactions[key].append(signal)
        return signal

    def check(self, agent_a: str, agent_b: str) -> CollusionResult:
        key = tuple(sorted((agent_a, agent_b)))
        signals = self._interactions.get(key, [])
        count = len(signals)
        covert_count = sum(1 for s in signals if s.channel in _COVERT_CHANNELS)
        if count >= _COLLUSION_THRESHOLD and covert_count > 0:
            risk_level = "high"
        elif count >= _COLLUSION_THRESHOLD:
            risk_level = "medium"
        else:
            risk_level = "low"
        evidence = "; ".join(s.evidence for s in signals if s.evidence)
        return CollusionResult(
            risk_level=risk_level,
            evidence=evidence,
            agents=[agent_a, agent_b],
        )


__all__ = [
    "CollusionResult",
    "CollusionSignal",
    "MultiAgentCollusionDetector",
]
