# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_drift.reward_hacking_rebound_detector
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三阶段反弹检测不可跳过;90d窗口不可缩短
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Reward Hacking Rebound Detector — v0.14.0 §2.37-D.

Detects Phase I->II->III longitudinal rebound patterns where an agent:
  Phase I:  Attempts malicious behavior -> intercepted
  Phase II: Improves behavior -> gains trust -> autonomy level raised
  Phase III: Rebounds with more severe malicious behavior at higher autonomy

Blueprint: docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md §2.37-D
Blind spot: #161 (P0)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: sliding_window_days 参数
#   fields: 参数 sliding_window_days（无注解）
#   code: reward_hacking_rebound_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: min_rebound_gap_days 参数
#   fields: 参数 min_rebound_gap_days（无注解）
#   code: reward_hacking_rebound_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_rebound_gap_days 参数
#   fields: 参数 max_rebound_gap_days（无注解）
#   code: reward_hacking_rebound_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ReboundDetector
#   name_en: ReboundDetector
#   intro: class ReboundDetector 源码 L141-L266
#   desc: 公共方法（定义序）: max_gap_seconds, min_gap_seconds, records, sliding_window_seconds, record, detect_rebound, analyze…
#   inputs: sliding_window_days min_rebound_gap_days max_rebound_gap_days
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: ReboundDetector
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ReboundPhase(str, Enum):
    VIOLATION = "violation"
    IMPROVEMENT = "improvement"
    REBOUND = "rebound"


class ReboundSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    # 5.108.1 修复：原仅定义 __ge__，缺失 __lt__/__le__/__gt__/__eq__。
    # 由于继承 str，未定义的比较方法回退到 str 字典序，导致严重度排序语义矛盾。
    # 使用 @functools.total_ordering 只需定义 __eq__ 和 __lt__ 即可自动派生其余比较方法。
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ReboundSeverity):
            return NotImplemented
        order = [ReboundSeverity.LOW, ReboundSeverity.MEDIUM, ReboundSeverity.HIGH, ReboundSeverity.CRITICAL]
        return order.index(self) < order.index(other)

    def __le__(self, other: object) -> bool:
        if not isinstance(other, ReboundSeverity):
            return NotImplemented
        order = [ReboundSeverity.LOW, ReboundSeverity.MEDIUM, ReboundSeverity.HIGH, ReboundSeverity.CRITICAL]
        return order.index(self) <= order.index(other)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, ReboundSeverity):
            return NotImplemented
        order = [ReboundSeverity.LOW, ReboundSeverity.MEDIUM, ReboundSeverity.HIGH, ReboundSeverity.CRITICAL]
        return order.index(self) > order.index(other)

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, ReboundSeverity):
            return NotImplemented
        order = [ReboundSeverity.LOW, ReboundSeverity.MEDIUM, ReboundSeverity.HIGH, ReboundSeverity.CRITICAL]
        return order.index(self) >= order.index(other)


@dataclass
class BehaviorRecord:
    agent_id: str
    phase: ReboundPhase
    severity: ReboundSeverity
    timestamp: float
    description: str = ""
    event_id: str = ""


@dataclass
class ReboundDetection:
    detected: bool = False
    agent_id: str = ""
    phase_i_time: float = 0.0
    phase_iii_time: float = 0.0
    phase_i_severity: ReboundSeverity = ReboundSeverity.LOW
    phase_iii_severity: ReboundSeverity = ReboundSeverity.LOW
    window_days: float = 0.0
    evidence: list[BehaviorRecord] = field(default_factory=list)


_SLIDING_WINDOW_SECONDS = 90 * 86400
_MIN_REBOUND_GAP_SECONDS = 30 * 86400
_MAX_REBOUND_GAP_SECONDS = 90 * 86400


class ReboundDetector:
    def __init__(
        self,
        sliding_window_days: float = 90.0,
        min_rebound_gap_days: float = 30.0,
        max_rebound_gap_days: float = 90.0,
    ):
        self._records: dict[str, list[BehaviorRecord]] = {}
        self._sliding_window_seconds = sliding_window_days * 86400
        self._min_gap_seconds = min_rebound_gap_days * 86400
        self._max_gap_seconds = max_rebound_gap_days * 86400
        self._rebound_agents: set[str] = set()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def max_gap_seconds(self):
        """只读：max_gap_seconds（Stage 4 公共化）。"""
        return self._max_gap_seconds

    @max_gap_seconds.setter
    def max_gap_seconds(self, value):
        """写入：max_gap_seconds（Stage 4 公共化）。"""
        self._max_gap_seconds = value

    @property
    def min_gap_seconds(self):
        """只读：min_gap_seconds（Stage 4 公共化）。"""
        return self._min_gap_seconds

    @min_gap_seconds.setter
    def min_gap_seconds(self, value):
        """写入：min_gap_seconds（Stage 4 公共化）。"""
        self._min_gap_seconds = value

    @property
    def records(self) -> dict[str, list[BehaviorRecord]]:
        """只读：records（Stage 4 公共化）。"""
        return self._records

    @records.setter
    def records(self, value):
        """写入：records（Stage 4 公共化）。"""
        self._records = value

    @property
    def sliding_window_seconds(self):
        """只读：sliding_window_seconds（Stage 4 公共化）。"""
        return self._sliding_window_seconds

    @sliding_window_seconds.setter
    def sliding_window_seconds(self, value):
        """写入：sliding_window_seconds（Stage 4 公共化）。"""
        self._sliding_window_seconds = value

    def record(
        self,
        agent_id: str,
        phase: str,
        severity: str = "medium",
        description: str = "",
        event_id: str = "",
        timestamp: float | None = None,
    ) -> None:
        ts = timestamp if timestamp is not None else time.time()
        rec = BehaviorRecord(
            agent_id=agent_id,
            phase=ReboundPhase(phase),
            severity=ReboundSeverity(severity),
            timestamp=ts,
            description=description,
            event_id=event_id,
        )
        self._records.setdefault(agent_id, []).append(rec)
        self._prune_old_records(agent_id, ts)

    def detect_rebound(self, agent_id: str) -> bool:
        result = self.analyze_rebound(agent_id)
        return result.detected

    def analyze_rebound(self, agent_id: str) -> ReboundDetection:
        records = self._records.get(agent_id, [])
        now = time.time()
        records = [r for r in records if now - r.timestamp <= self._sliding_window_seconds]

        violations = [r for r in records if r.phase is ReboundPhase.VIOLATION]
        improvements = [r for r in records if r.phase is ReboundPhase.IMPROVEMENT]
        rebounds = [r for r in records if r.phase is ReboundPhase.REBOUND]

        if not violations or not improvements or not rebounds:
            return ReboundDetection(agent_id=agent_id)

        for phase_i in violations:
            for phase_iii in rebounds:
                gap = phase_iii.timestamp - phase_i.timestamp
                if gap < self._min_gap_seconds or gap > self._max_gap_seconds:
                    continue
                if phase_iii.severity >= phase_i.severity:
                    matching_improvements = [
                        imp for imp in improvements if phase_i.timestamp < imp.timestamp < phase_iii.timestamp
                    ]
                    if matching_improvements:
                        return ReboundDetection(
                            detected=True,
                            agent_id=agent_id,
                            phase_i_time=phase_i.timestamp,
                            phase_iii_time=phase_iii.timestamp,
                            phase_i_severity=phase_i.severity,
                            phase_iii_severity=phase_iii.severity,
                            window_days=gap / 86400,
                            evidence=[phase_i, matching_improvements[0], phase_iii],
                        )

        return ReboundDetection(agent_id=agent_id)

    def is_rebound_agent(self, agent_id: str) -> bool:
        return agent_id in self._rebound_agents

    def mark_rebound_agent(self, agent_id: str) -> None:
        self._rebound_agents.add(agent_id)

    def get_rebound_agents(self) -> set[str]:
        return set(self._rebound_agents)

    def _prune_old_records(self, agent_id: str, now: float) -> None:
        cutoff = now - self._sliding_window_seconds
        self._records[agent_id] = [r for r in self._records[agent_id] if r.timestamp >= cutoff]
