# [BLUEPRINT] MOD-FAC-004 | docs/03_modules/_domain_factor/factor_vote_mining/blueprint.md
# [MODULE] zephyr.research.factor_vote_mining
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无（协议核心纯内存；Agent propose/vote 回调、ic_validator/oos_validator/clock 全注入）
# [CONSUMERS] 运行时装配批（FactorMAD 多智能体因子挖掘批 / 因子库草稿治理串行合并）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 生成 Agent 数护栏 3-5 且 agent_id 唯一（越界 Fail-Closed）；候选须先过 IC 验证+样本外测试（注入验证器，异常 Fail-Closed）方入投票；多数投票严格过半（votes > n/2）入选；首轮无入选→升级辩论重提案，辩论轮次护栏 max_debate_rounds；每候选 IC/OOS 验证时延经注入时钟计量并标记 within_latency_budget（预算 <1 分钟/因子）；入选按 (-votes,-|ic|,expression) 确定性排序；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_factor/factor_vote_mining/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FactorVoteError(占位 ZA-FAC-UNREGISTERED-FACTOR-VOTE)——Agent 数越界/id 重复或空/验证器缺失/topic 空白/验证器异常或返回非法/注入时钟回读非法时抛
# [TESTS] tests/research/test_factor_vote_mining.py
# [A_module] module_id=MOD-FAC-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""FactorVoteMiner — FactorMAD 多智能体投票因子挖掘（MOD-FAC-004）。

B10-01845（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-020，A1 §29.14-3.5）：
FactorMAD——3-5 个生成 Agent 独立产出因子（Agent 回调全注入）+ **多数投票**
选优（票数>半入选）+ 性能不足**升级辩论**（辩论轮次护栏）+ 候选须过 IC 验证
+ 样本外测试（注入验证器）+ <1 分钟/因子**时延预算标记**。

查重分工（蓝图 §0）：gp_strategy_discovery=单机表达式树进化（无多 Agent）；
本件=多 Agent **提案-验证-投票-辩论**协议（Agent 产出/投票回调全注入，本件
不实现 Agent 本体，不重建注册表）。
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_LATENCY_BUDGET_S",
    "MAX_AGENTS",
    "MIN_AGENTS",
    "ElectedFactor",
    "FactorProposal",
    "FactorVoteError",
    "FactorVoteMiner",
    "VoteAgent",
    "VoteMiningResult",
]

#: 生成 Agent 数护栏（FactorMAD 设定 3-5）
MIN_AGENTS: Final = 3
MAX_AGENTS: Final = 5
#: 单因子验证时延预算（<1 分钟/因子）
DEFAULT_LATENCY_BUDGET_S: Final = 60.0

_MAX_DEBATE_CAP: Final = 5


class FactorVoteError(Exception):
    """FactorMAD 投票挖掘输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FAC-UNREGISTERED-FACTOR-VOTE。
    """


@dataclass(frozen=True)
class VoteAgent:
    """生成 Agent 回调组（frozen；propose/vote 全注入）。

    - propose: ``(topic, debate_round) -> 表达式序列``（独立产出因子）
    - vote: ``expression -> bool``（对候选是否赞成）
    """

    agent_id: str
    propose: Callable[[str, int], Sequence[str]]
    vote: Callable[[str], bool]


@dataclass(frozen=True)
class FactorProposal:
    """单 Agent 提案（frozen）。"""

    agent_id: str
    expression: str
    debate_round: int


@dataclass(frozen=True)
class ElectedFactor:
    """多数投票入选因子（frozen）。"""

    expression: str
    votes: int
    vote_share: float
    ic: float
    within_latency_budget: bool
    debate_round: int


@dataclass(frozen=True)
class VoteMiningResult:
    """FactorMAD 挖掘产出（frozen）。"""

    topic: str
    proposals: tuple[FactorProposal, ...]
    elected: tuple[ElectedFactor, ...]
    debate_rounds: int
    notes: tuple[str, ...]


class FactorVoteMiner:
    """FactorMAD 多智能体投票因子挖掘器（提案→IC/OOS 验证→多数投票→辩论护栏）。

    Args:
        agents: 3-5 个 VoteAgent（回调全注入，id 唯一）。
        ic_validator: 注入 IC 验证器，``expression -> float``（|ic|≥min_ic 为过）。
        oos_validator: 注入样本外验证器，``expression -> bool``。
        min_ic: IC 通过下限（∈ [0,1)）。
        max_debate_rounds: 升级辩论轮次护栏（0..5；首轮无入选才辩论）。
        latency_budget_s: 单因子验证时延预算（秒，默认 60）。
        clock: 注入时钟（``() -> float`` 秒；时延计量用）。
    """

    def __init__(
        self,
        *,
        agents: Sequence[VoteAgent],
        ic_validator: Callable[[str], float] | None,
        oos_validator: Callable[[str], bool] | None,
        min_ic: float = 0.02,
        max_debate_rounds: int = 2,
        latency_budget_s: float = DEFAULT_LATENCY_BUDGET_S,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if not agents or not (MIN_AGENTS <= len(agents) <= MAX_AGENTS):
            raise FactorVoteError(
                f"Agent 数越出护栏 [{MIN_AGENTS},{MAX_AGENTS}]: {len(agents) if agents else 0}"
            )
        ids = [a.agent_id for a in agents]
        if any(not isinstance(i, str) or not i.strip() for i in ids):
            raise FactorVoteError(f"agent_id 空白: {ids!r}")
        if len(set(ids)) != len(ids):
            raise FactorVoteError(f"agent_id 重复: {ids!r}")
        if ic_validator is None:
            raise FactorVoteError("ic_validator 未注入（IC 验证强制注入，Fail-Closed）")
        if oos_validator is None:
            raise FactorVoteError("oos_validator 未注入（样本外测试强制注入，Fail-Closed）")
        if not (0.0 <= float(min_ic) < 1.0):
            raise FactorVoteError(f"min_ic 非法（须 ∈ [0,1)）: {min_ic!r}")
        if isinstance(max_debate_rounds, bool) or not (0 <= int(max_debate_rounds) <= _MAX_DEBATE_CAP):
            raise FactorVoteError(
                f"max_debate_rounds 越出护栏 [0,{_MAX_DEBATE_CAP}]: {max_debate_rounds!r}"
            )
        if float(latency_budget_s) <= 0.0:
            raise FactorVoteError(f"latency_budget_s 非法（须 >0）: {latency_budget_s!r}")
        self._agents = tuple(agents)
        self._ic_validator = ic_validator
        self._oos_validator = oos_validator
        self._min_ic = float(min_ic)
        self._max_debate = int(max_debate_rounds)
        self._budget = float(latency_budget_s)
        self._clock = clock or time.monotonic

    # ── 注入件封装（异常/非法返回 Fail-Closed） ─────────────────────────────

    def _tick(self) -> float:
        t = float(self._clock())
        if t != t:  # NaN
            raise FactorVoteError("注入时钟返回 NaN（时延计量契约违反，Fail-Closed）")
        return t

    def _validate_candidate(self, expr: str) -> tuple[float, bool, bool]:
        """IC + 样本外验证 + 时延标记；验证器异常 Fail-Closed。"""
        t0 = self._tick()
        try:
            ic = self._ic_validator(expr)
        except FactorVoteError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise FactorVoteError(f"ic_validator 异常: {expr!r}（{type(exc).__name__}）") from exc
        if isinstance(ic, bool) or not isinstance(ic, (int, float)):
            raise FactorVoteError(f"ic_validator 返回非法: {ic!r}（expression={expr!r}）")
        try:
            oos_ok = bool(self._oos_validator(expr))
        except FactorVoteError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise FactorVoteError(f"oos_validator 异常: {expr!r}（{type(exc).__name__}）") from exc
        elapsed = self._tick() - t0
        return float(ic), oos_ok, elapsed <= self._budget

    # ── 主流程（提案→验证→投票→辩论护栏） ──────────────────────────────────

    def mine(self, topic: str) -> VoteMiningResult:
        """FactorMAD 挖掘主入口（多数投票严格过半入选，不足升级辩论）。"""
        if not isinstance(topic, str) or not topic.strip():
            raise FactorVoteError(f"topic 空白: {topic!r}")
        topic = topic.strip()
        n = len(self._agents)
        notes: list[str] = []
        proposals: list[FactorProposal] = []
        seen: set[str] = set()
        elected: list[ElectedFactor] = []
        round_used = 0

        for r in range(self._max_debate + 1):
            round_used = r
            fresh: list[str] = []
            for agent in self._agents:
                try:
                    exprs = agent.propose(topic, r)
                except FactorVoteError:
                    raise
                except Exception as exc:  # noqa: BLE001
                    raise FactorVoteError(
                        f"Agent {agent.agent_id} propose 异常（{type(exc).__name__}）"
                    ) from exc
                for expr in exprs or ():
                    if not isinstance(expr, str) or not expr.strip():
                        notes.append(f"Agent {agent.agent_id} 提案空白剔除（第 {r} 轮）")
                        continue
                    expr = expr.strip()
                    proposals.append(
                        FactorProposal(agent_id=agent.agent_id, expression=expr, debate_round=r)
                    )
                    if expr not in seen:
                        seen.add(expr)
                        fresh.append(expr)
            passing: list[tuple[str, float, bool]] = []
            for expr in fresh:
                ic, oos_ok, within = self._validate_candidate(expr)
                if abs(ic) < self._min_ic:
                    notes.append(f"IC 不足剔除: {expr}（|ic|={abs(ic):.4f}<{self._min_ic}）")
                    continue
                if not oos_ok:
                    notes.append(f"样本外未过剔除: {expr}")
                    continue
                passing.append((expr, ic, within))
            for expr, ic, within in passing:
                votes = sum(1 for agent in self._agents if bool(agent.vote(expr)))
                if votes > n / 2:  # 多数投票严格过半入选
                    elected.append(
                        ElectedFactor(
                            expression=expr,
                            votes=votes,
                            vote_share=round(votes / n, 6),
                            ic=ic,
                            within_latency_budget=within,
                            debate_round=r,
                        )
                    )
                else:
                    notes.append(f"票数未过半落选: {expr}（{votes}/{n}）")
            if elected:
                break
            if r < self._max_debate:
                notes.append(f"第 {r} 轮无入选，升级辩论（{r + 1}/{self._max_debate}）")
        elected.sort(key=lambda e: (-e.votes, -abs(e.ic), e.expression))
        _log.info("FactorMAD 挖掘: topic=%s 入选 %d（辩论 %d 轮）", topic, len(elected), round_used)
        return VoteMiningResult(
            topic=topic,
            proposals=tuple(proposals),
            elected=tuple(elected),
            debate_rounds=round_used,
            notes=tuple(notes),
        )
