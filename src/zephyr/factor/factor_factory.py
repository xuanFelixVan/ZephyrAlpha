# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.factor_factory
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.governance.lifecycle_state_machine(复用底层生命周期FSM); zephyr.shared.foundation.errors
# [CONSUMERS] 因子挖掘/治理编排调用方（运行时装配批接线）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 9阶段顺序推进(仅正向一步/监控→迭代/迭代→验证合法); 入库必经IC+因果+回测三重门禁且验证一次通过不回炉; 注册委托注入registry; 底层生命周期复用MOD-L02-013 FSM不重造; 每次submit/advance产审计
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未立项/未装mining_hook->FactorFactoryError; 门禁失败->StageGateVerdict.passed=False(不抛)
# [TESTS] tests/factor/test_factor_factory.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C-027 因子工厂（CAND-FAC-008 / B1-00143）。

9 阶段全生命周期工厂：候选立项(candidate) → 假设(hypothesis) → 生成(generation)
→ 验证(validation) → 入库(registration) → 监控(monitoring) → 迭代(iteration)
→ 废弃(deprecation) → 退役(retirement)。

查重裁定（不重复既有件）：
  - 底层 8 状态生命周期状态机复用 MOD-L02-013 lifecycle_state_machine
    （create_factor_fsm），本件只做 9 阶段工厂编排，不重造转换拓扑；
  - 因子注册表复用 factor_base.FactorRegistry 语义（registry 注入式，运行时
    装配批接真注册表）；
  - FactorMAD 多 Agent 投票挖掘属 CAND-FAC-020（P2 候选，未来件
    research/factor_vote_mining.py）——本件只留 mining_hook 扩展点，委托不实现；
  - IC/因果验证与 C-003 回测门禁为 validator/gate 注入点（复用 ic_ir_calc /
    回测域门禁语义），判定核心不复制其计算。

不变量：
  - 产出必经回测门禁与 IC/因果双重验证：REGISTRATION 前置条件
    validation_passed=True；三重验证仅在验证关执行一次。
  - 阶段顺序：仅正向一步推进；监控→迭代、迭代→验证（回炉重验）为合法边；
    退役为终态。
  - 每次 submit/advance 产不可变审计记录；audit_sink 异常不阻断。

依据: §功能域模块·D-FACTOR；construction_backlog_dig.tsv B1-00143。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol

from zephyr.factor.governance.lifecycle_state_machine import (
    BACKTEST,
    DEPRECATED,
    DEVELOPMENT,
    GRAYSCALE,
    PAPER,
    PRODUCTION,
    RETIRED,
    create_factor_fsm,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__ = [
    "FactorCandidate",
    "FactorFactory",
    "FactorFactoryError",
    "FactoryStage",
    "StageGateVerdict",
]


class FactorFactoryError(ZephyrBaseError):
    """工厂编排失败（错误码未登，纪律⑦留错误码对账批）。"""


class FactoryStage(str, Enum):
    """因子工厂 9 阶段。"""

    CANDIDATE = "candidate"
    HYPOTHESIS = "hypothesis"
    GENERATION = "generation"
    VALIDATION = "validation"
    REGISTRATION = "registration"
    MONITORING = "monitoring"
    ITERATION = "iteration"
    DEPRECATION = "deprecation"
    RETIREMENT = "retirement"


_STAGE_ORDER: tuple[FactoryStage, ...] = tuple(FactoryStage)

# 合法阶段边（显式枚举）：主链 candidate→…→monitoring→deprecation→retirement；
# iteration 为监控期的可选回炉边（回炉后可重验证或直接废弃）；retirement 终态。
_STAGE_EDGES: frozenset[tuple[FactoryStage, FactoryStage]] = frozenset(
    {
        (FactoryStage.CANDIDATE, FactoryStage.HYPOTHESIS),
        (FactoryStage.HYPOTHESIS, FactoryStage.GENERATION),
        (FactoryStage.GENERATION, FactoryStage.VALIDATION),
        (FactoryStage.VALIDATION, FactoryStage.REGISTRATION),
        (FactoryStage.REGISTRATION, FactoryStage.MONITORING),
        (FactoryStage.MONITORING, FactoryStage.ITERATION),
        (FactoryStage.MONITORING, FactoryStage.DEPRECATION),
        (FactoryStage.ITERATION, FactoryStage.VALIDATION),
        (FactoryStage.ITERATION, FactoryStage.DEPRECATION),
        (FactoryStage.DEPRECATION, FactoryStage.RETIREMENT),
    }
)

# 工厂阶段→底层生命周期 FSM 状态（首通正向驱动目标；复用 MOD-L02-013 不重造）
_LIFECYCLE_TARGET: dict[FactoryStage, str | None] = {
    FactoryStage.CANDIDATE: None,
    FactoryStage.HYPOTHESIS: None,
    FactoryStage.GENERATION: DEVELOPMENT,
    FactoryStage.VALIDATION: BACKTEST,
    FactoryStage.REGISTRATION: PAPER,
    FactoryStage.MONITORING: PRODUCTION,
    FactoryStage.ITERATION: None,  # 迭代不动底层（保持 production，工厂层独立标记）
    FactoryStage.DEPRECATION: DEPRECATED,
    FactoryStage.RETIREMENT: RETIRED,
}

# 底层 FSM 逐站推进路径（线性推进段）
_LIFECYCLE_FORWARD: dict[str, str] = {
    "research": DEVELOPMENT,
    DEVELOPMENT: BACKTEST,
    BACKTEST: PAPER,
    PAPER: GRAYSCALE,
    GRAYSCALE: PRODUCTION,
    PRODUCTION: DEPRECATED,
    DEPRECATED: RETIRED,
}


@dataclass(frozen=True)
class FactorCandidate:
    """因子候选立项单。

    Attributes:
        candidate_id: 候选唯一 ID。
        hypothesis: 因子假设（可证伪陈述）。
        expression: 因子表达式/生成描述。
        factor_id: 目标注册因子 ID。
        metadata: 溯源元数据。
    """

    candidate_id: str
    hypothesis: str
    expression: str
    factor_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StageGateVerdict:
    """阶段推进裁定。

    Attributes:
        candidate_id: 候选 ID。
        to_stage: 目标阶段。
        passed: 是否通过门禁。
        reason: 未通过理由（通过为空）。
    """

    candidate_id: str
    to_stage: FactoryStage
    passed: bool
    reason: str = ""


class _RegistryPort(Protocol):
    """因子注册表最小协议（FactorRegistry 语义子集，注入式）。"""

    def register_factor(self, factor_id: str, payload: dict) -> None: ...


@dataclass
class _Pipeline:
    candidate: FactorCandidate
    stage: FactoryStage
    fsm: Any
    validation_passed: bool = False
    lifecycle_driven_to: str = "research"


class FactorFactory:
    """因子工厂：9 阶段全生命周期编排。

    Args:
        registry: 因子注册表（注入式，register_factor 协议）。
        ic_validator: IC 验证委托 ``validator(candidate) -> bool``（缺省真，
            运行时装配批接 ic_ir_calc 链路）。
        causal_validator: 因果验证委托（同上）。
        backtest_gate: C-003 回测门禁委托（同上）。
        mining_hook: FactorMAD 挖掘扩展点 ``hook(prompt) -> list[FactorCandidate]``
            （CAND-FAC-020 未来件，委托不实现）。
        audit_sink: 审计持久化回调（可选，异常不阻断）。
        clock: 时钟注入（测试可控）。
    """

    def __init__(
        self,
        *,
        registry: _RegistryPort | None = None,
        ic_validator: Callable[[FactorCandidate], bool] | None = None,
        causal_validator: Callable[[FactorCandidate], bool] | None = None,
        backtest_gate: Callable[[FactorCandidate], bool] | None = None,
        mining_hook: Callable[[str], list[FactorCandidate]] | None = None,
        audit_sink: Callable[[dict], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._registry = registry
        self._ic_validator = ic_validator or (lambda c: True)
        self._causal_validator = causal_validator or (lambda c: True)
        self._backtest_gate = backtest_gate or (lambda c: True)
        self._mining_hook = mining_hook
        self._audit_sink = audit_sink
        self._clock = clock or (lambda: datetime.datetime.now(datetime.timezone.utc))
        self._pipelines: dict[str, _Pipeline] = {}

    # ------------------------------------------------------------------ 查询

    def stage_of(self, candidate_id: str) -> FactoryStage:
        """候选当前工厂阶段。"""
        return self._pipeline(candidate_id).stage

    def lifecycle_state_of(self, candidate_id: str) -> str:
        """候选底层生命周期 FSM 当前状态（MOD-L02-013 语义）。"""
        return str(self._pipeline(candidate_id).fsm.current_state)

    def pipeline_snapshot(self) -> Mapping[str, str]:
        """全部流水线阶段快照（只读）。"""
        return MappingProxyType({cid: p.stage.value for cid, p in self._pipelines.items()})

    def _pipeline(self, candidate_id: str) -> _Pipeline:
        try:
            return self._pipelines[candidate_id]
        except KeyError:
            raise FactorFactoryError(f"因子候选未立项: {candidate_id!r}") from None

    # ------------------------------------------------------------------ 立项/挖掘

    def submit(self, candidate: FactorCandidate) -> FactorCandidate:
        """候选立项：建立流水线（底层生命周期 FSM 从 research 起跑）。"""
        if candidate.candidate_id in self._pipelines:
            raise FactorFactoryError(f"因子候选重复立项: {candidate.candidate_id!r}")
        self._pipelines[candidate.candidate_id] = _Pipeline(
            candidate=candidate,
            stage=FactoryStage.CANDIDATE,
            fsm=create_factor_fsm(),
        )
        self._audit(candidate.candidate_id, "submit", FactoryStage.CANDIDATE, True, "")
        return candidate

    def mine(self, prompt: str) -> list[FactorCandidate]:
        """FactorMAD 挖掘扩展点：委托 mining_hook 产出候选并自动立项。"""
        if self._mining_hook is None:
            raise FactorFactoryError("mining_hook 未装配（FactorMAD 属 CAND-FAC-020 未来件）")
        mined = self._mining_hook(prompt)
        for candidate in mined:
            if candidate.candidate_id not in self._pipelines:
                self.submit(candidate)
        return list(mined)

    # ------------------------------------------------------------------ 推进

    def _legal_transition(self, current: FactoryStage, target: FactoryStage) -> bool:
        return (current, target) in _STAGE_EDGES

    def _run_validation_gates(self, candidate: FactorCandidate) -> str:
        """三重门禁：IC/因果/回测。返回失败理由（通过为空串）。"""
        if not self._ic_validator(candidate):
            return "IC 验证未通过"
        if not self._causal_validator(candidate):
            return "因果验证未通过"
        if not self._backtest_gate(candidate):
            return "回测门禁未通过（C-003）"
        return ""

    def _drive_lifecycle(self, pipe: _Pipeline, target: FactoryStage) -> None:
        """底层 FSM 首通正向驱动（复用 MOD-L02-013 合法转换，逐站推进）。"""
        goal = _LIFECYCLE_TARGET.get(target)
        if goal is None:
            return
        state = str(pipe.fsm.current_state)
        if state == goal:
            return
        while state != goal:
            nxt = _LIFECYCLE_FORWARD.get(state)
            if nxt is None:
                # 回炉场景（如迭代后重验）：底层已领先，不再驱动
                return
            pipe.fsm.transition(nxt)
            state = nxt
        pipe.lifecycle_driven_to = goal

    def advance(self, candidate_id: str, to_stage: FactoryStage) -> StageGateVerdict:
        """推进候选到目标阶段（门禁裁定 + 底层生命周期对齐 + 审计）。"""
        pipe = self._pipeline(candidate_id)

        if not self._legal_transition(pipe.stage, to_stage):
            reason = f"非法阶段跳转: {pipe.stage.value} -> {to_stage.value}（仅顺序推进/监控→迭代/迭代→验证）"
            verdict = StageGateVerdict(candidate_id, to_stage, False, reason)
            self._audit(candidate_id, "advance", to_stage, False, reason)
            return verdict

        if to_stage == FactoryStage.VALIDATION:
            reason = self._run_validation_gates(pipe.candidate)
            if reason:
                verdict = StageGateVerdict(candidate_id, to_stage, False, reason)
                self._audit(candidate_id, "advance", to_stage, False, reason)
                return verdict
            pipe.validation_passed = True

        if to_stage == FactoryStage.REGISTRATION:
            if not pipe.validation_passed:
                reason = "入库前置未满足：验证关未通过（必经 IC/因果/回测三重验证）"
                verdict = StageGateVerdict(candidate_id, to_stage, False, reason)
                self._audit(candidate_id, "advance", to_stage, False, reason)
                return verdict
            if self._registry is not None:
                self._registry.register_factor(
                    pipe.candidate.factor_id,
                    {
                        "candidate_id": candidate_id,
                        "hypothesis": pipe.candidate.hypothesis,
                        "expression": pipe.candidate.expression,
                        "registered_at": self._clock().isoformat(),
                    },
                )

        self._drive_lifecycle(pipe, to_stage)
        pipe.stage = to_stage
        verdict = StageGateVerdict(candidate_id, to_stage, True, "")
        self._audit(candidate_id, "advance", to_stage, True, "")
        return verdict

    # ------------------------------------------------------------------ 审计

    def _audit(
        self, candidate_id: str, action: str, to_stage: FactoryStage, passed: bool, reason: str
    ) -> None:
        if self._audit_sink is None:
            return
        record = {
            "candidate_id": candidate_id,
            "action": action,
            "to_stage": to_stage.value,
            "passed": passed,
            "reason": reason,
            "at": self._clock().isoformat(),
        }
        try:
            self._audit_sink(record)
        except Exception:  # noqa: BLE001 — sink 故障不阻断编排
            log.warning("factor_factory: audit_sink 异常", exc_info=True)
