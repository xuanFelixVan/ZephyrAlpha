# [BLUEPRINT] MOD-PF-013 | docs/03_modules/_domain_portfolio_core/rl_portfolio_execution/blueprint.md
# [MODULE] zephyr.pf_core.rl_portfolio_execution
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] 无（编排核心纯内存；trainer/C-003回测门禁/风控校验/时钟全注入）
# [CONSUMERS] 运行时装配批（RL离线评估流水线装配 / Constrained RL trainer 绑定 / C-003 门禁接线）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三场景词表闭合(portfolio_optimization|optimal_execution|t0_trading); 风险预算硬上限钳制不可越(used>cap按比例缩放); 偏离AC轨迹超阈值熔断回落AC计划轨迹; 做T底仓不变(净变动=0且标的⊆底仓)+风控硬约束校验; C-003门禁不过不启用(异常按不过); RL仅离线评估语义标注不可摘除; 金额Decimal-only拒绝float; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_portfolio_core/rl_portfolio_execution/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RlPortfolioError(占位 ZA-PF-UNREGISTERED-RL-PORTFOLIO)——trainer/门禁缺失/场景错配/离线标注摘除/非Decimal/AC轨迹非法/步数错配/底仓变动/风控未过时抛
# [TESTS] tests/pf_core/test_rl_portfolio_execution.py
# [A_module] module_id=MOD-PF-013 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
RlPortfolioExecutionOrchestrator — RL 组合优化与执行（MOD-PF-013）。

B10-01835（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PF004-006，A1 §29.9）：
RL **三场景分立编排**——

① RL 组合优化：状态/动作/奖励 Schema（RlRequest/RlProposal/expected_reward）
   + Constrained RL（Lagrangian 思想）trainer 注入 + **风险预算硬上限钳制
   不可越**（used>cap → 动作按比例缩放至 cap）；
② RL 最优执行：增强 Almgren-Chriss——AC 计划轨迹注入，RL 动作步
   （step_0..step_{n-1} 累计成交比例）偏离 AC 轨迹超阈值 → **熔断**回落
   AC 计划轨迹（基线安全路径）；
③ RL 做T：**底仓不变校验**（每标的净变动=0 且标的⊆底仓）+ 风控硬约束
   校验器注入（未注入/未过 Fail-Closed）。

统一经 **C-003 回测门禁注入（不过不启用；门禁异常按不过）**；RL 提案强制
**仅离线评估语义标注**（offline_only=True 不可摘除）。本件只编排不训练，
不做在线实盘启用。

查重分工（蓝图 §0）：portfolio_optimizer=确定性组合优化（非 RL）；本件=
RL 提案的**约束编排与门禁层**，不实现 RL 算法本身。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: trainer 参数
#   fields: 参数 trainer（无注解）
#   code: rl_portfolio_execution.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: backtest_gate 参数
#   fields: 参数 backtest_gate（无注解）
#   code: rl_portfolio_execution.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: risk_budget_cap 参数
#   fields: 参数 risk_budget_cap（无注解）
#   code: rl_portfolio_execution.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: ac_deviation_threshold 参数
#   fields: 参数 ac_deviation_threshold（无注解）
#   code: rl_portfolio_execution.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RlPortfolioExecutionOrchestrator
#   name_en: RlPortfolioExecutionOrchestrator
#   intro: RL 三场景编排器（trainer/门禁/风控全注入，纯内存确定性）。
#   desc: RL 三场景编排器（trainer/门禁/风控全注入，纯内存确定性）。；公共方法（定义序）: run_portfolio_optimization, run_optimal_execution, run_t0…
#   inputs: trainer backtest_gate risk_budget_cap ac_deviation_threshold t0_risk_…
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: RlPortfolioExecutionOrchestrator
#   downstream: 运行时装配批（RL离线评估流水线装配 / Constrained RL trainer 绑定 / C-003 门禁接线）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "RlPortfolioError",
    "RlPortfolioExecutionOrchestrator",
    "RlProposal",
    "RlRequest",
    "RlRunResult",
    "RlRunStatus",
    "RlScenario",
]

_OFFLINE_NOTE: Final = "RL仅离线评估语义标注（不启用在线实盘）"
_CLAMP_NOTE: Final = "风险预算硬上限钳制：used>cap 动作按比例缩放至 cap"
_FUSE_NOTE: Final = "偏离AC轨迹超阈值熔断：停用RL动作，回落AC计划轨迹（基线安全路径）"


class RlPortfolioError(Exception):
    """RL 组合优化与执行编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-PF-UNREGISTERED-RL-PORTFOLIO。
    """


class RlScenario(str, Enum):
    """RL 三场景（词表闭合）。"""

    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    OPTIMAL_EXECUTION = "optimal_execution"
    T0_TRADING = "t0_trading"


class RlRunStatus(str, Enum):
    """编排运行状态。"""

    ENABLED = "enabled"  # 门禁通过，（钳制后）生效
    GATE_REJECTED = "gate_rejected"  # C-003 回测门禁不过 → 不启用
    FUSED_TO_AC = "fused_to_ac"  # 偏离AC轨迹超阈值熔断 → 回落AC计划轨迹


@dataclass(frozen=True)
class RlRequest:
    """RL 请求（状态 Schema + 场景注入件，frozen）。"""

    scenario: RlScenario
    state: Mapping[str, float]
    ac_trajectory: tuple[Decimal, ...] = ()
    base_positions: Mapping[str, Decimal] = field(default_factory=dict)


@dataclass(frozen=True)
class RlProposal:
    """RL 提案（动作/奖励 Schema，frozen）。offline_only 强制 True。"""

    scenario: RlScenario
    actions: Mapping[str, Decimal]
    risk_budget_used: Decimal
    expected_reward: float
    offline_only: bool = True


@dataclass(frozen=True)
class RlRunResult:
    """编排结果（frozen）。"""

    scenario: RlScenario
    status: RlRunStatus
    enabled: bool
    clamped: bool
    fused: bool
    effective_actions: Mapping[str, Decimal]
    risk_budget_used: Decimal
    notes: tuple[str, ...]
    run_at: datetime.datetime


def _require_decimal(name: str, value: object) -> Decimal:
    if not isinstance(value, Decimal):
        raise RlPortfolioError(f"{name} 须为 Decimal（Decimal-only，拒绝 float 隐式转换）: {type(value).__name__}")
    if not value.is_finite():
        raise RlPortfolioError(f"{name} 非有限: {value!r}")
    return value


def _validate_state(state: Mapping[str, float]) -> None:
    for key, value in state.items():
        if not key:
            raise RlPortfolioError("state 特征键为空")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise RlPortfolioError(f"state[{key!r}] 须为有限数值: {value!r}")


class RlPortfolioExecutionOrchestrator:
    """RL 三场景编排器（trainer/门禁/风控全注入，纯内存确定性）。"""

    def __init__(
        self,
        *,
        trainer: Callable[[RlRequest], RlProposal] | None,
        backtest_gate: Callable[[RlProposal], bool] | None,
        risk_budget_cap: Decimal,
        ac_deviation_threshold: Decimal,
        t0_risk_checker: Callable[[RlProposal], bool] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if trainer is None or not callable(trainer):
            raise RlPortfolioError("trainer 未注入（Constrained RL Lagrangian trainer 须注入）")
        if backtest_gate is None or not callable(backtest_gate):
            raise RlPortfolioError("C-003 回测门禁未注入（统一经门禁，不过不启用）")
        _require_decimal("risk_budget_cap", risk_budget_cap)
        if risk_budget_cap <= 0:
            raise RlPortfolioError(f"risk_budget_cap 须为正: {risk_budget_cap!r}")
        _require_decimal("ac_deviation_threshold", ac_deviation_threshold)
        if not (Decimal("0") <= ac_deviation_threshold <= Decimal("1")):
            raise RlPortfolioError(f"ac_deviation_threshold 须在[0,1]: {ac_deviation_threshold!r}")
        if t0_risk_checker is not None and not callable(t0_risk_checker):
            raise RlPortfolioError("t0_risk_checker 不可调用")
        self._trainer = trainer
        self._backtest_gate = backtest_gate
        self._risk_budget_cap = risk_budget_cap
        self._ac_deviation_threshold = ac_deviation_threshold
        self._t0_risk_checker = t0_risk_checker
        self._clock = clock or datetime.datetime.now

    # ── 内部：提案校验 / 门禁 ─────────────────────────────────────────────

    def _propose(self, request: RlRequest) -> RlProposal:
        proposal = self._trainer(request)
        if not isinstance(proposal, RlProposal):
            raise RlPortfolioError(f"trainer 须返回 RlProposal: {type(proposal).__name__}")
        if proposal.scenario is not request.scenario:
            raise RlPortfolioError(f"场景错配: 请求 {request.scenario.value}，提案 {proposal.scenario.value}")
        if proposal.offline_only is not True:
            raise RlPortfolioError("RL 仅离线评估语义标注被摘除（offline_only 须=True）")
        if not proposal.actions:
            raise RlPortfolioError("提案动作为空")
        for symbol, qty in proposal.actions.items():
            if not symbol:
                raise RlPortfolioError("动作标的为空")
            _require_decimal(f"actions[{symbol!r}]", qty)
        _require_decimal("risk_budget_used", proposal.risk_budget_used)
        if proposal.risk_budget_used < 0:
            raise RlPortfolioError(f"risk_budget_used 须非负: {proposal.risk_budget_used!r}")
        if (
            isinstance(proposal.expected_reward, bool)
            or not isinstance(proposal.expected_reward, (int, float))
            or not math.isfinite(proposal.expected_reward)
        ):
            raise RlPortfolioError(f"expected_reward 须为有限数值: {proposal.expected_reward!r}")
        return proposal

    def _gate(self, proposal: RlProposal) -> bool:
        try:
            return bool(self._backtest_gate(proposal))
        except Exception:  # noqa: BLE001 — 门禁异常按不过处理（Fail-Closed 不启用）
            _log.exception("C-003 回测门禁异常，按不过处理")
            return False

    def _gate_rejected(self, scenario: RlScenario) -> RlRunResult:
        return RlRunResult(
            scenario=scenario,
            status=RlRunStatus.GATE_REJECTED,
            enabled=False,
            clamped=False,
            fused=False,
            effective_actions={},
            risk_budget_used=Decimal("0"),
            notes=("C-003 回测门禁不过，不启用", _OFFLINE_NOTE),
            run_at=self._clock(),
        )

    # ── 场景①：RL 组合优化 ───────────────────────────────────────────────

    def run_portfolio_optimization(self, *, state: Mapping[str, float]) -> RlRunResult:
        """RL 组合优化：trainer 提案 → C-003 门禁 → 风险预算硬上限钳制。"""
        _validate_state(state)
        proposal = self._propose(RlRequest(scenario=RlScenario.PORTFOLIO_OPTIMIZATION, state=state))
        if not self._gate(proposal):
            return self._gate_rejected(RlScenario.PORTFOLIO_OPTIMIZATION)
        notes: list[str] = [_OFFLINE_NOTE]
        used = proposal.risk_budget_used
        clamped = False
        if used > self._risk_budget_cap:
            scale = self._risk_budget_cap / used
            effective = {s: proposal.actions[s] * scale for s in sorted(proposal.actions)}
            used = self._risk_budget_cap
            clamped = True
            notes.insert(0, _CLAMP_NOTE)
        else:
            effective = {s: proposal.actions[s] for s in sorted(proposal.actions)}
        return RlRunResult(
            scenario=RlScenario.PORTFOLIO_OPTIMIZATION,
            status=RlRunStatus.ENABLED,
            enabled=True,
            clamped=clamped,
            fused=False,
            effective_actions=effective,
            risk_budget_used=used,
            notes=tuple(notes),
            run_at=self._clock(),
        )

    # ── 场景②：RL 最优执行（增强 Almgren-Chriss）────────────────────────

    def run_optimal_execution(self, *, state: Mapping[str, float], ac_trajectory: Sequence[Decimal]) -> RlRunResult:
        """RL 最优执行：AC 计划轨迹注入，偏离超阈值熔断回落 AC。"""
        _validate_state(state)
        if not ac_trajectory:
            raise RlPortfolioError("ac_trajectory 为空（AC 计划轨迹须注入）")
        trajectory = tuple(_require_decimal(f"ac_trajectory[{i}]", v) for i, v in enumerate(ac_trajectory))
        prev = Decimal("0")
        for i, v in enumerate(trajectory):
            if not (Decimal("0") <= v <= Decimal("1")):
                raise RlPortfolioError(f"ac_trajectory[{i}] 须在[0,1]（累计成交比例）: {v!r}")
            if v < prev:
                raise RlPortfolioError(f"ac_trajectory[{i}] 非法递减（累计轨迹须单调不减）: {v!r}<{prev!r}")
            prev = v
        proposal = self._propose(
            RlRequest(
                scenario=RlScenario.OPTIMAL_EXECUTION,
                state=state,
                ac_trajectory=trajectory,
            )
        )
        expected_keys = [f"step_{i}" for i in range(len(trajectory))]
        if sorted(proposal.actions) != expected_keys:
            raise RlPortfolioError(
                f"动作步数须与 AC 轨迹对齐（键=step_0..step_{len(trajectory) - 1}）: {sorted(proposal.actions)}"
            )
        if not self._gate(proposal):
            return self._gate_rejected(RlScenario.OPTIMAL_EXECUTION)
        deviation = max(abs(proposal.actions[f"step_{i}"] - trajectory[i]) for i in range(len(trajectory)))
        if deviation > self._ac_deviation_threshold:
            effective = {f"step_{i}": trajectory[i] for i in range(len(trajectory))}
            return RlRunResult(
                scenario=RlScenario.OPTIMAL_EXECUTION,
                status=RlRunStatus.FUSED_TO_AC,
                enabled=True,
                clamped=False,
                fused=True,
                effective_actions=effective,
                risk_budget_used=proposal.risk_budget_used,
                notes=(_FUSE_NOTE, _OFFLINE_NOTE),
                run_at=self._clock(),
            )
        return RlRunResult(
            scenario=RlScenario.OPTIMAL_EXECUTION,
            status=RlRunStatus.ENABLED,
            enabled=True,
            clamped=False,
            fused=False,
            effective_actions={k: proposal.actions[k] for k in expected_keys},
            risk_budget_used=proposal.risk_budget_used,
            notes=(_OFFLINE_NOTE,),
            run_at=self._clock(),
        )

    # ── 场景③：RL 做T ────────────────────────────────────────────────────

    def run_t0(self, *, state: Mapping[str, float], base_positions: Mapping[str, Decimal]) -> RlRunResult:
        """RL 做T：底仓不变校验 + 风控硬约束校验 → C-003 门禁。"""
        _validate_state(state)
        if not base_positions:
            raise RlPortfolioError("base_positions 为空（做T底仓须注入）")
        for symbol, qty in base_positions.items():
            if not symbol:
                raise RlPortfolioError("底仓标的为空")
            _require_decimal(f"base_positions[{symbol!r}]", qty)
        if self._t0_risk_checker is None:
            raise RlPortfolioError("做T风控硬约束校验器未注入")
        proposal = self._propose(
            RlRequest(
                scenario=RlScenario.T0_TRADING,
                state=state,
                base_positions=dict(base_positions),
            )
        )
        for symbol, delta in proposal.actions.items():
            if symbol not in base_positions:
                raise RlPortfolioError(f"做T标的越出底仓: {symbol!r} 不在 base_positions")
            if delta != 0:
                raise RlPortfolioError(f"底仓不变校验失败: {symbol!r} 净变动 {delta!r} ≠ 0")
        try:
            risk_ok = bool(self._t0_risk_checker(proposal))
        except Exception as exc:  # noqa: BLE001 — 风控校验异常 Fail-Closed
            raise RlPortfolioError(f"风控硬约束校验异常: {exc}") from None
        if not risk_ok:
            raise RlPortfolioError("风控硬约束校验未过")
        if not self._gate(proposal):
            return self._gate_rejected(RlScenario.T0_TRADING)
        return RlRunResult(
            scenario=RlScenario.T0_TRADING,
            status=RlRunStatus.ENABLED,
            enabled=True,
            clamped=False,
            fused=False,
            effective_actions={s: proposal.actions[s] for s in sorted(proposal.actions)},
            risk_budget_used=proposal.risk_budget_used,
            notes=("底仓不变+风控硬约束校验通过", _OFFLINE_NOTE),
            run_at=self._clock(),
        )
