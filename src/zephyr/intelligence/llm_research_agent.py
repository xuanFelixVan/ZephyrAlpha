# [BLUEPRINT] MOD-INT-RESEARCH-AGENT | docs/03_modules/_domain_intelligence/llm_research_agent/blueprint.md
# [MODULE] zephyr.intelligence.llm_research_agent
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（协议核心纯内存；tools/planner/thinker/reflector/fact_checker/kb_writer/clock 全注入）
# [CONSUMERS] 运行时装配批（本地模型优先绑定规划/思考/反思回调 / 检索计算数据库工具白名单注册 / KB 写库与事实回查装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 工具白名单闭合(注册表外拒绝); ReAct 轮次护栏(max_rounds 超限 Fail-Closed); 关键数字/标的强制事实回查(未注入/未过 Fail-Closed); 仅辅助研究硬标注 advisory_only 恒真; KB 写库不阻断; 计划号/轮次确定性; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/llm_research_agent/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LlmResearchAgentError(占位 ZA-IT-UNREGISTERED-RESEARCH-AGENT)——空任务/非法工具表/白名单外工具/空计划/重复步骤/超轮次护栏/事实回查缺失或未过时抛
# [TESTS] tests/intelligence/test_llm_research_agent.py
# [A_module] module_id=MOD-INT-RESEARCH-AGENT | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""LlmResearchAgent — LLM 研究助手（MOD-INT-RESEARCH-AGENT）。

B6-08553（AUD-DRAFT-001-DIGEST P2 波 P2-W14，CAND-AISA-017，B6 D-RESEARCH-11）：
规划器（任务→步骤计划）+ 工具白名单（检索/计算/数据库工具注册表注入，白名单
外拒绝）+ ReAct 反思循环（思考-行动-观察-反思，轮次护栏）+ 记忆写 KB 回调 +
本地模型优先语义（规划/思考/反思回调由装配批优先绑定本地模型）+ 关键数字/标的
强制事实回查（注入 fact_checker，未注入 Fail-Closed）+ 仅辅助研究不直连交易硬
标注。W04 波漏处理，本波补施工。

查重分工（蓝图 §0）：llm_agent_router=LLM 路由选路（本件不做路由）；
episodic_memory_store=情景记忆存储（本件仅经 kb_writer 回调写记忆，不建存储）；
sentinel_hallucination_detector=幻觉检测（本件事实回查经注入回调，不实现检测）。
"""

from __future__ import annotations

import datetime
import logging
import re
from dataclasses import dataclass
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "FactCheckRecord",
    "LlmResearchAgent",
    "LlmResearchAgentError",
    "ReactRound",
    "ResearchPlan",
    "ResearchReport",
    "ResearchStep",
]

#: 仅辅助研究硬标注（不直连交易）
ADVISORY_DISCLAIMER: Final[str] = "仅辅助研究，不直连交易"

#: 关键标的（6 位 A 股代码）与关键数字（百分数）抽取词表
_SYMBOL_RE: Final = re.compile(r"(?<!\d)\d{6}(?!\d)")
_PERCENT_RE: Final = re.compile(r"\d+(?:\.\d+)?%")


class LlmResearchAgentError(Exception):
    """研究助手输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-IT-UNREGISTERED-RESEARCH-AGENT。
    """


@dataclass(frozen=True)
class ResearchStep:
    """研究步骤 Schema（规划器产出，frozen）。"""

    step_id: str
    action: str
    tool: str
    tool_input: str


@dataclass(frozen=True)
class ResearchPlan:
    """研究计划 Schema（任务→步骤计划，frozen）。"""

    plan_id: str
    task: str
    steps: tuple[ResearchStep, ...]
    created_at: datetime.datetime


@dataclass(frozen=True)
class ReactRound:
    """ReAct 单轮留痕（思考-行动-观察-反思，frozen）。"""

    round_no: int
    step_id: str
    thought: str
    action: str
    observation: str
    reflection: str


@dataclass(frozen=True)
class FactCheckRecord:
    """关键数字/标的事实回查留痕（frozen）。"""

    claim: str
    passed: bool
    checked_at: datetime.datetime


@dataclass(frozen=True)
class ResearchReport:
    """研究报告 Schema（仅辅助研究硬标注，frozen）。"""

    task: str
    plan_id: str
    rounds: tuple[ReactRound, ...]
    conclusion: str
    fact_checks: tuple[FactCheckRecord, ...]
    advisory_only: bool
    disclaimer: str
    created_at: datetime.datetime


class LlmResearchAgent:
    """LLM 研究助手（规划 + 白名单工具 + ReAct 循环 + 事实回查）。"""

    def __init__(
        self,
        *,
        tools: Mapping[str, Callable[[str], str]],
        planner: Callable[[str], Sequence[ResearchStep]],
        thinker: Callable[[ResearchStep], str] | None = None,
        reflector: Callable[[ResearchStep, str, str], str] | None = None,
        fact_checker: Callable[[str], bool] | None = None,
        kb_writer: Callable[[ResearchReport], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        max_rounds: int = 8,
    ) -> None:
        if not tools:
            raise LlmResearchAgentError("tools 为空（工具白名单注册表须注入）")
        for name, fn in tools.items():
            if not name:
                raise LlmResearchAgentError("工具名为空")
            if not callable(fn):
                raise LlmResearchAgentError(f"工具不可调用: {name!r}")
        if not callable(planner):
            raise LlmResearchAgentError("planner 未注入或不可调用")
        if isinstance(max_rounds, bool) or not isinstance(max_rounds, int) or max_rounds < 1:
            raise LlmResearchAgentError(f"非法 max_rounds: {max_rounds!r}（轮次护栏须为正整数）")
        self._tools: dict[str, Callable[[str], str]] = dict(tools)
        self._planner = planner
        # 本地模型优先语义：装配批应优先将 thinker/reflector 绑定本地模型
        self._thinker = thinker or (lambda step: f"思考：准备执行 {step.action}")
        self._reflector = reflector or (
            lambda step, thought, observation: (
                f"反思：步骤 {step.step_id} 完成，观察 {len(observation)} 字符"
            )
        )
        self._fact_checker = fact_checker
        self._kb_writer = kb_writer
        self._clock = clock or datetime.datetime.now
        self._max_rounds = max_rounds
        self._plan_seq = 0
        self._plans: dict[str, ResearchPlan] = {}
        self._reports: dict[str, ResearchReport] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_key_claims(text: str) -> tuple[str, ...]:
        """抽取关键数字/标的（确定性排序去重）。"""
        claims = set(_SYMBOL_RE.findall(text)) | set(_PERCENT_RE.findall(text))
        return tuple(sorted(claims))

    # ── 规划器 ───────────────────────────────────────────────────────────

    def plan(self, task: str) -> ResearchPlan:
        """规划：任务→步骤计划（空任务/空计划/白名单外工具/重复步骤 Fail-Closed）。"""
        if not isinstance(task, str) or not task.strip():
            raise LlmResearchAgentError("task 为空")
        try:
            steps = tuple(self._planner(task))
        except LlmResearchAgentError:
            raise
        except Exception as exc:  # noqa: BLE001 — 规划器异常按 Fail-Closed 包装
            raise LlmResearchAgentError(f"规划器异常: {exc!r}") from exc
        if not steps:
            raise LlmResearchAgentError("规划器产出空步骤计划")
        seen: set[str] = set()
        for step in steps:
            if not isinstance(step, ResearchStep):
                raise LlmResearchAgentError(f"非法步骤类型: {step!r}")
            if not step.step_id:
                raise LlmResearchAgentError("step_id 为空")
            if step.step_id in seen:
                raise LlmResearchAgentError(f"step_id 重复: {step.step_id!r}")
            seen.add(step.step_id)
            if step.tool not in self._tools:
                raise LlmResearchAgentError(
                    f"白名单外工具拒绝: {step.tool!r}（步骤 {step.step_id!r}）"
                )
        self._plan_seq += 1
        plan = ResearchPlan(
            plan_id=f"plan-{self._plan_seq:04d}",
            task=task,
            steps=steps,
            created_at=self._clock(),
        )
        self._plans[plan.plan_id] = plan
        return plan

    # ── 工具白名单 ────────────────────────────────────────────────────────

    def invoke_tool(self, name: str, payload: str) -> str:
        """工具调用：白名单外拒绝；工具异常按 Fail-Closed 包装。"""
        if not name:
            raise LlmResearchAgentError("工具名为空")
        if not isinstance(payload, str):
            raise LlmResearchAgentError(f"非法工具入参类型: {type(payload).__name__}")
        fn = self._tools.get(name)
        if fn is None:
            _log.warning("白名单外工具拒绝: %s", name)
            raise LlmResearchAgentError(f"白名单外工具拒绝: {name!r}")
        try:
            return str(fn(payload))
        except LlmResearchAgentError:
            raise
        except Exception as exc:  # noqa: BLE001 — 工具异常按 Fail-Closed 包装
            raise LlmResearchAgentError(f"工具 {name!r} 执行异常: {exc!r}") from exc

    # ── ReAct 反思循环 ────────────────────────────────────────────────────

    def run(self, task: str) -> ResearchReport:
        """执行研究：规划 → ReAct 循环（轮次护栏）→ 事实回查 → 写 KB → 报告。"""
        plan = self.plan(task)
        if len(plan.steps) > self._max_rounds:
            raise LlmResearchAgentError(
                f"轮次护栏触发: 计划 {len(plan.steps)} 步超 max_rounds={self._max_rounds}"
            )

        rounds: list[ReactRound] = []
        for round_no, step in enumerate(plan.steps, start=1):
            try:
                thought = str(self._thinker(step))
            except Exception as exc:  # noqa: BLE001 — 思考回调异常 Fail-Closed
                raise LlmResearchAgentError(f"思考回调异常: {exc!r}") from exc
            observation = self.invoke_tool(step.tool, step.tool_input)
            try:
                reflection = str(self._reflector(step, thought, observation))
            except Exception as exc:  # noqa: BLE001 — 反思回调异常 Fail-Closed
                raise LlmResearchAgentError(f"反思回调异常: {exc!r}") from exc
            rounds.append(ReactRound(
                round_no=round_no,
                step_id=step.step_id,
                thought=thought,
                action=step.action,
                observation=observation,
                reflection=reflection,
            ))

        conclusion = "；".join(r.observation for r in rounds)

        # 关键数字/标的强制事实回查（未注入 Fail-Closed，不旁路）
        claims = self._extract_key_claims(conclusion)
        fact_checks: list[FactCheckRecord] = []
        if claims:
            if self._fact_checker is None:
                raise LlmResearchAgentError(
                    "fact_checker 未注入（关键数字/标的强制事实回查，禁止旁路）: "
                    + ",".join(claims)
                )
            for claim in claims:
                try:
                    passed = bool(self._fact_checker(claim))
                except Exception as exc:  # noqa: BLE001 — 回查异常按未过处理
                    raise LlmResearchAgentError(f"事实回查异常: {claim!r}: {exc!r}") from exc
                fact_checks.append(FactCheckRecord(
                    claim=claim, passed=passed, checked_at=self._clock()
                ))
                if not passed:
                    raise LlmResearchAgentError(f"事实回查未过: {claim!r}")

        report = ResearchReport(
            task=task,
            plan_id=plan.plan_id,
            rounds=tuple(rounds),
            conclusion=conclusion,
            fact_checks=tuple(fact_checks),
            advisory_only=True,  # 仅辅助研究不直连交易硬标注
            disclaimer=ADVISORY_DISCLAIMER,
            created_at=self._clock(),
        )
        self._reports[plan.plan_id] = report

        if self._kb_writer is not None:
            try:
                self._kb_writer(report)
            except Exception:  # noqa: BLE001 — KB 写库不阻断（蓝图 §1）
                _log.exception("kb_writer 写库失败: %s", plan.plan_id)
        return report

    # ── 查询 ─────────────────────────────────────────────────────────────

    def plans(self) -> tuple[ResearchPlan, ...]:
        """计划台账（按 (created_at, plan_id) 确定性排序）。"""
        return tuple(sorted(self._plans.values(), key=lambda p: (p.created_at, p.plan_id)))

    def reports(self) -> tuple[ResearchReport, ...]:
        """报告台账（按 (created_at, plan_id) 确定性排序）。"""
        return tuple(sorted(self._reports.values(), key=lambda r: (r.created_at, r.plan_id)))
