# [BLUEPRINT] MOD-INF-048 | docs/03_modules/MOD-INF-048/
# [MODULE] zephyr.orchestrator.voting_first_multi_agent
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] 无（纯标准库）
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 投票优先——裁定只来自票数聚合，无协调者暗箱改票；平票确定性裁决（字典序小者胜）；单 agent 失败容错不阻断；全部失败 fail-closed（winner=None）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VoteConfigError(ZA-TR-0022)——无注册 agent/空任务/非法权重/非法注册
# [TESTS] tests/orchestrator/test_voting_first_multi_agent.py
# [A_module] module_id=MOD-INF-048 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""投票优先多智能体编排（MOD-INF-048）。

多 agent 对同一任务独立提案，裁定**投票优先**：tally_votes 纯函数聚票
（可选权重），多数/相对多数者胜；平票确定性裁决（并列中字典序小者胜，
保证同输入同输出、可审计复现）。单 agent 异常容错（记 failed_agents 不阻断），
全部失败 fail-closed 返回 winner=None——由调用方走人工/降级通道。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Final

__all__: Final = [
    "VoteConfigError",
    "VoteOutcome",
    "VotingFirstMultiAgent",
    "VotingResult",
    "tally_votes",
]


class VoteConfigError(Exception):
    """ZA-TR-0022: 投票编排配置/入口非法。"""

    error_code = "ZA-TR-0022"


@dataclass(frozen=True)
class VoteOutcome:
    """聚票结果（纯函数输出）。"""

    winner: str | None
    tally: dict[str, float]
    tie_broken: bool = False


@dataclass(frozen=True)
class VotingResult:
    """一次编排结果。"""

    task: str
    winner: str | None
    proposals: dict[str, str]
    failed_agents: list[str] = field(default_factory=list)
    vote: VoteOutcome | None = None


def tally_votes(votes: dict[str, str], weights: dict[str, float] | None = None) -> VoteOutcome:
    """纯函数聚票：加权 plurality；平票时字典序小者确定性胜。"""
    tally: dict[str, float] = {}
    for voter, choice in votes.items():
        w = (weights or {}).get(voter, 1.0)
        w = float(w)
        if w < 0.0:
            raise VoteConfigError(f"权重不得为负: {w}")
        tally[choice] = tally.get(choice, 0.0) + w

    if not tally:
        return VoteOutcome(winner=None, tally={})

    max_votes = max(tally.values())
    leaders = sorted(k for k, v in tally.items() if v == max_votes)
    if len(leaders) == 1:
        return VoteOutcome(winner=leaders[0], tally=tally)
    return VoteOutcome(winner=leaders[0], tally=tally, tie_broken=True)


class VotingFirstMultiAgent:
    """投票优先多智能体编排器。"""

    def __init__(self) -> None:
        self._agents: dict[str, tuple[Callable[[str], str], float]] = {}

    def register_agent(self, name: str, fn: Callable[[str], str], *, weight: float = 1.0) -> None:
        """注册提案 agent（fn: task -> proposal）。非法注册 → ZA-TR-0022。"""
        if not name:
            raise VoteConfigError("agent 名不得为空")
        if not callable(fn):
            raise VoteConfigError(f"agent {name!r} 不可调用")
        w = float(weight)
        if w <= 0.0:
            raise VoteConfigError(f"权重必须为正: {weight}")
        self._agents[name] = (fn, w)

    def run(self, task: str) -> VotingResult:
        """收集提案并投票裁定。无 agent/空任务 → ZA-TR-0022；全灭 → winner=None。"""
        if not self._agents:
            raise VoteConfigError("未注册任何 agent")
        if not task or not task.strip():
            raise VoteConfigError("task 不得为空")

        proposals: dict[str, str] = {}
        failed: list[str] = []
        for name, (fn, _w) in self._agents.items():
            try:
                proposals[name] = str(fn(task))
            except Exception:  # noqa: BLE001 — 单 agent 失败容错，记名不阻断投票
                failed.append(name)

        weights = {name: w for name, (_f, w) in self._agents.items()}
        outcome = tally_votes(proposals, weights=weights)
        return VotingResult(
            task=task,
            winner=outcome.winner,
            proposals=proposals,
            failed_agents=failed,
            vote=outcome,
        )
