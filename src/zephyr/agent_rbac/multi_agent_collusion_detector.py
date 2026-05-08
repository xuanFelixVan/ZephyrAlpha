"""
多Agent合谋检测器 — 跨会话隐式通信 + 博弈论建模

MOD-INF-018 §2.13  D-018-29
"""

import time
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional


@dataclass
class CollusionSignal:
    agent_a: str
    agent_b: str
    signal_type: str
    evidence: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class CollusionResult:
    collusion_detected: bool = False
    risk_level: str = "NONE"
    agents_involved: list[str] = field(default_factory=list)
    signal_count: int = 0
    evidence_chain: list[str] = field(default_factory=list)


class MultiAgentCollusionDetector:
    def __init__(self) -> None:
        self._signals: list[CollusionSignal] = []
        self._pair_activity: dict[tuple[str, str], list[float]] = defaultdict(list)
        self._threshold = 3
        self._time_window = 3600

    def record_interaction(
        self,
        agent_a: str,
        agent_b: str,
        signal_type: str,
        evidence: str = "",
    ) -> Optional[CollusionSignal]:
        signal = CollusionSignal(
            agent_a=agent_a,
            agent_b=agent_b,
            signal_type=signal_type,
            evidence=evidence,
        )
        self._signals.append(signal)
        pair_key = tuple(sorted([agent_a, agent_b]))
        self._pair_activity[pair_key].append(time.time())
        return signal

    def check(self, agent_a: str, agent_b: str) -> CollusionResult:
        pair_key = tuple(sorted([agent_a, agent_b]))
        timestamps = self._pair_activity.get(pair_key, [])
        cutoff = time.time() - self._time_window
        recent = [t for t in timestamps if t > cutoff]

        recent_signals = [
            s for s in self._signals
            if {s.agent_a, s.agent_b} == {agent_a, agent_b}
            and s.timestamp > cutoff
        ]

        if len(recent_signals) >= self._threshold:
            return CollusionResult(
                collusion_detected=True,
                risk_level="HIGH" if len(recent_signals) >= self._threshold * 2 else "MEDIUM",
                agents_involved=[agent_a, agent_b],
                signal_count=len(recent_signals),
                evidence_chain=[s.evidence for s in recent_signals if s.evidence],
            )

        return CollusionResult(
            collusion_detected=len(recent_signals) >= 2,
            risk_level="LOW" if len(recent_signals) >= 2 else "NONE",
            agents_involved=[agent_a, agent_b],
            signal_count=len(recent_signals),
        )

    def reset_pair(self, agent_a: str, agent_b: str) -> None:
        pair_key = tuple(sorted([agent_a, agent_b]))
        self._pair_activity.pop(pair_key, None)
        self._signals = [s for s in self._signals if {s.agent_a, s.agent_b} != {agent_a, agent_b}]
