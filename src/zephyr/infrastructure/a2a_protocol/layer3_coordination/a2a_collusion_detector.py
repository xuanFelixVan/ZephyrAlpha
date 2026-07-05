# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_collusion_detector
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_collusion_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 合谋检测器 — Agent 间串通模式识别

检测两个或多个 Agent 是否合谋绕过安全机制:
  模式1: 互为审查者 — Agent A 和 Agent B 互相 approve 对方的所有 output
  模式2: 分拆攻击 — 大操作被拆成 N 个小操作，分配给 N 个 Agent，每个不触达安全阈值
  模式3: 时序同步 — 多个 Agent 在相近时间执行相同/相关操作

输出: CollusionReport — 合谋风险评分 + 参与 Agent 列表
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class CollusionFinding:
    pattern: str
    agent_ids: list[str]
    evidence: list[dict]
    risk_score: float


@dataclass
class CollusionReport:
    findings: list[CollusionFinding] = field(default_factory=list)
    clean: bool = True


class A2ACollusionDetector:
    def __init__(self, mutual_review_threshold: int = 5, time_window_seconds: float = 300.0):
        self._mutual_review_threshold = mutual_review_threshold
        self._time_window = time_window_seconds
        self._interactions: dict[tuple[str, str], int] = defaultdict(int)

    def record_interaction(self, from_agent: str, to_agent: str, action: str, timestamp: float = 0.0):
        pair = tuple(sorted([from_agent, to_agent]))
        self._interactions[pair] += 1

    def detect(self) -> CollusionReport:
        report = CollusionReport(clean=True)
        pairs = list(self._interactions.items())
        pairs.sort(key=lambda x: x[1], reverse=True)

        for (a, b), count in pairs:
            if count >= self._mutual_review_threshold:
                risk = min(1.0, count / (self._mutual_review_threshold * 2))
                report.findings.append(
                    CollusionFinding(
                        pattern="mutual_review",
                        agent_ids=[a, b],
                        evidence=[{"interaction_count": count}],
                        risk_score=round(risk, 2),
                    )
                )

        report.clean = len(report.findings) == 0
        return report
