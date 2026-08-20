# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.retirement_workflow
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.foundation.errors（仅错误基类；执行端口全部依赖注入，本模块不 import 生产执行体）
# [CONSUMERS] 调用方（周/月退役评审编排；首个退役策略触发时由运营入口装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 评审制铁律=decision==RETIRE 且 human_approved=True 才执行退役动作，否则仅诊断+上报（55 号 §3.5 评审制与本模块对齐，本模块永不自动改策略状态）;决策矩阵唯一真源=61 号 §3.9 三选一;执行顺序固定=仓位减半→暂停新建仓→平掉存量→归档→ARCHIVED
# [MODIFY-GUARD] 61_lifecycle_multi_ai.md §3.9
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RetirementWorkflowError(ZA-GV-0048)
# [TESTS] tests/governance/lifecycle/test_retirement_workflow.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: strategy_id + RetirementPorts（get_decay_alerts/run_backtest/check_peers/get_regime_mismatch 四必备 + 执行六可选）
# I2: sustained_min_days=10（持续告警阈值）+ lookback_days=126（诊断回测窗口）+ human_approved（评审制人工闸门）+ knight（五骑士归因，可选）
# F1: Step1 触发——持续告警过滤（consecutive_days≥10）→ OBSERVING，未达标→MONITORING 返回
# F2: Step2 诊断——oos_sharpe/is_regime_wide/regime_mismatch 三元组（端口供给，本模块不重算）
# F3: Step3 决策——三选一矩阵（oos>0&mismatch→REOPTIMIZE；oos>-0.2&非全策略坏→PAUSE_CUT_SIZE；否则 RETIRE）
# F4: Step4 退役执行——仅 RETIRE+human_approved：scale(0.5)→disable_new_entries→flatten→archive→ARCHIVED
# F5: Step5 复盘——五骑士归因 classify_decay_knight + record_methodology 沉淀
# O1: RetirementWorkflowResult（state/sustained_alerts/diagnosis/decision/executed_actions/knight/escalation_required）
# [/ALGO_FLOW]
"""D_GOVERNANCE — 策略退役 5 步工作流编排（61 号 §3.9，函数级 MVP）。

判据执行体已由 55 号承载（``strategy_retirement_evaluator.StrategyRetirementEvaluator``
production），本模块是 §3.9 伪代码的**编排层**：触发 → 诊断 → 决策 → 退役执行 → 复盘，
五步全部通过注入端口（RetirementPorts）调用，本模块不 import 任何生产执行体——
装配权在调用方（首个退役策略触发时的运营入口）。

评审制铁律（与 55 号 §3.5 对齐）：``decision == RETIRE`` 且 ``human_approved=True``
才执行 Step 4 退役动作；未批准时仅诊断 + ``escalation_required=True`` 上报人工裁定，
本模块永不自动改策略状态。

依据: 61_lifecycle_multi_ai §3.9（退役流程 5 步施工伪代码 + 三选一决策矩阵 + 五骑士归因）
Version: 0.1.0
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

#: 持续告警阈值（61 号 §3.9：单一监控点连续告警 ≥10 个交易日，约 2 周，过滤单日噪声）
SUSTAINED_MIN_DAYS: Final[int] = 10
#: 诊断回测窗口（61 号 §3.9：最近 3-6 个月，126≈6 个月交易日）
DIAGNOSIS_LOOKBACK_DAYS: Final[int] = 126
#: 三选一矩阵 PAUSE_CUT_SIZE 下界（61 号 §3.9：oos_sharpe > -0.2 且非全策略坏 → 降仓观察）
PAUSE_SHARPE_FLOOR: Final[float] = -0.2


class RetirementWorkflowError(ZephyrBaseError):
    """退役工作流输入非法（strategy_id 空 / 阈值非法 / 诊断指标 NaN）。"""

    error_code = "ZA-GV-0048"


class RetirementDecision(str, Enum):
    """三选一决策矩阵（61 号 §3.9）。"""

    REOPTIMIZE = "REOPTIMIZE"
    PAUSE_CUT_SIZE = "PAUSE_CUT_SIZE"
    RETIRE = "RETIRE"


class DecayKnight(str, Enum):
    """五骑士退役归因分类（61 号 §3.3 第 5 条）。"""

    CROWDING = "crowding"
    REGIME_CHANGE = "regime_change"
    OVERFITTING = "overfitting"
    TECHNOLOGY_EVOLUTION = "technology_evolution"
    REGULATORY_CHANGE = "regulatory_change"


@dataclass(frozen=True)
class DecayAlert:
    """Decay Detection 单监控点告警（61 号 §3.9 Step 1 输入）。"""

    monitor_point: str
    consecutive_days: int


@dataclass(frozen=True)
class RetirementDiagnosis:
    """Step 2 诊断三元组（端口供给，本模块不重算）。"""

    oos_sharpe: float
    is_regime_wide: bool
    regime_mismatch: bool


@dataclass(frozen=True)
class RetirementPorts:
    """执行端口（依赖注入；四必备诊断端口 + 六可选执行端口）。

    必备：
        get_decay_alerts: (strategy_id) -> Sequence[DecayAlert]
        run_backtest: (strategy_id, lookback_days) -> oos_sharpe float
        check_peers: (strategy_id) -> 全策略同时坏 bool（True=regime 切换）
        get_regime_mismatch: (strategy_id) -> 设计 regime 与当前 regime 失配 bool
    可选（None=对应动作跳过并留痕）：
        scale_position / disable_new_entries / flatten_positions /
        archive / set_lifecycle_state / record_methodology
    """

    get_decay_alerts: Callable[[str], Sequence[DecayAlert]]
    run_backtest: Callable[[str, int], float]
    check_peers: Callable[[str], bool]
    get_regime_mismatch: Callable[[str], bool]
    scale_position: Callable[[str, float], None] | None = None
    disable_new_entries: Callable[[str], None] | None = None
    flatten_positions: Callable[[str], None] | None = None
    archive: Callable[[str], None] | None = None
    set_lifecycle_state: Callable[[str, str], None] | None = None
    record_methodology: Callable[[str, DecayKnight, dict], None] | None = None


@dataclass(frozen=True)
class RetirementWorkflowResult:
    """退役工作流产物。"""

    strategy_id: str
    state: str  # MONITORING（未触发）/ OBSERVING（已触发，已诊断决策）
    sustained_alerts: tuple[str, ...] = ()
    diagnosis: RetirementDiagnosis | None = None
    decision: RetirementDecision | None = None
    executed_actions: tuple[str, ...] = ()
    knight: DecayKnight | None = None
    human_approved: bool = False
    escalation_required: bool = False  # RETIRE 但未批准 → 待人工裁定
    skipped_ports: tuple[str, ...] = field(default_factory=tuple)


def decide_retirement(diagnosis: RetirementDiagnosis) -> RetirementDecision:
    """三选一决策矩阵（61 号 §3.9 Step 3，唯一真源）。"""
    if diagnosis.oos_sharpe > 0 and diagnosis.regime_mismatch:
        return RetirementDecision.REOPTIMIZE
    if diagnosis.oos_sharpe > PAUSE_SHARPE_FLOOR and not diagnosis.is_regime_wide:
        return RetirementDecision.PAUSE_CUT_SIZE
    return RetirementDecision.RETIRE


def classify_decay_knight(diagnosis: RetirementDiagnosis) -> DecayKnight:
    """五骑士归因 MVP 规则（61 号 §3.9 Step 5；完整归因须人工/因子证据，MVP 默认映射）。"""
    if diagnosis.regime_mismatch or diagnosis.is_regime_wide:
        return DecayKnight.REGIME_CHANGE
    return DecayKnight.OVERFITTING


def run_retirement_workflow(
    strategy_id: str,
    ports: RetirementPorts,
    *,
    sustained_min_days: int = SUSTAINED_MIN_DAYS,
    lookback_days: int = DIAGNOSIS_LOOKBACK_DAYS,
    human_approved: bool = False,
    knight: DecayKnight | None = None,
) -> RetirementWorkflowResult:
    """退役 5 步工作流编排（61 号 §3.9）。

    Args:
        strategy_id: 策略 ID。
        ports: 执行端口（四必备诊断 + 六可选执行）。
        sustained_min_days: 持续告警阈值（默认 10 交易日）。
        lookback_days: 诊断回测窗口（默认 126≈6 个月）。
        human_approved: 评审制人工闸门——False 时 RETIRE 不执行仅上报。
        knight: 五骑士归因（None=classify_decay_knight MVP 规则推断）。

    Returns:
        RetirementWorkflowResult（MONITORING=未触发；OBSERVING=已诊断决策）。

    Raises:
        RetirementWorkflowError: 输入非法 / 诊断指标 NaN。
    """
    if not strategy_id or not strategy_id.strip():
        raise RetirementWorkflowError("strategy_id 不能为空")
    if sustained_min_days < 1 or lookback_days < 1:
        raise RetirementWorkflowError(
            f"阈值须 >= 1: sustained_min_days={sustained_min_days} lookback_days={lookback_days}"
        )

    # Step 1: 触发——Decay Detection 任一监控点持续告警 → OBSERVING
    alerts = ports.get_decay_alerts(strategy_id)
    sustained = tuple(a.monitor_point for a in alerts if a.consecutive_days >= sustained_min_days)
    if not sustained:
        logger.info("退役工作流 %s: 无持续告警（阈值 %d 天），继续监控", strategy_id, sustained_min_days)
        return RetirementWorkflowResult(strategy_id=strategy_id, state="MONITORING")
    _invoke(ports.set_lifecycle_state, strategy_id, "OBSERVING")

    # Step 2: 诊断——最近 3-6 个月回测 + 同伴对比 + regime 失配
    oos_sharpe = float(ports.run_backtest(strategy_id, lookback_days))
    if math.isnan(oos_sharpe) or math.isinf(oos_sharpe):
        raise RetirementWorkflowError(f"诊断 oos_sharpe 非法: {oos_sharpe}")
    diagnosis = RetirementDiagnosis(
        oos_sharpe=oos_sharpe,
        is_regime_wide=bool(ports.check_peers(strategy_id)),
        regime_mismatch=bool(ports.get_regime_mismatch(strategy_id)),
    )

    # Step 3: 决策——三选一矩阵
    decision = decide_retirement(diagnosis)

    # Step 4: 退役执行——仅 RETIRE 且评审批准（评审制铁律）
    executed: list[str] = []
    skipped: list[str] = []
    if decision is RetirementDecision.RETIRE and human_approved:
        for name, fn, args in (
            ("scale_position_0.5", ports.scale_position, (strategy_id, 0.5)),
            ("disable_new_entries", ports.disable_new_entries, (strategy_id,)),
            ("flatten_positions", ports.flatten_positions, (strategy_id,)),
            ("archive", ports.archive, (strategy_id,)),
        ):
            if fn is None:
                skipped.append(name)
                continue
            fn(*args)
            executed.append(name)
        _invoke(ports.set_lifecycle_state, strategy_id, "ARCHIVED")
        if ports.set_lifecycle_state is not None:
            executed.append("set_state_archived")
    escalation = decision is RetirementDecision.RETIRE and not human_approved
    if escalation:
        logger.warning(
            "退役工作流 %s: 决策=RETIRE 但未经人工批准——不执行，上报评审裁定（评审制铁律）",
            strategy_id,
        )

    # Step 5: 复盘——五骑士归因沉淀
    final_knight = knight or classify_decay_knight(diagnosis)
    if ports.record_methodology is not None:
        ports.record_methodology(
            strategy_id,
            final_knight,
            {
                "oos_sharpe": diagnosis.oos_sharpe,
                "is_regime_wide": diagnosis.is_regime_wide,
                "regime_mismatch": diagnosis.regime_mismatch,
                "decision": decision.value,
                "human_approved": human_approved,
            },
        )
        executed.append("record_methodology")

    return RetirementWorkflowResult(
        strategy_id=strategy_id,
        state="OBSERVING",
        sustained_alerts=sustained,
        diagnosis=diagnosis,
        decision=decision,
        executed_actions=tuple(executed),
        knight=final_knight,
        human_approved=human_approved,
        escalation_required=escalation,
        skipped_ports=tuple(skipped),
    )


def _invoke(fn: Callable[[str, str], None] | None, strategy_id: str, state: str) -> None:
    """可选状态端口调用（None=跳过留痕，不抛）。"""
    if fn is not None:
        fn(strategy_id, state)


__all__: Final = [
    "DIAGNOSIS_LOOKBACK_DAYS",
    "PAUSE_SHARPE_FLOOR",
    "SUSTAINED_MIN_DAYS",
    "DecayAlert",
    "DecayKnight",
    "RetirementDecision",
    "RetirementDiagnosis",
    "RetirementPorts",
    "RetirementWorkflowError",
    "RetirementWorkflowResult",
    "classify_decay_knight",
    "decide_retirement",
    "run_retirement_workflow",
]
