# [BLUEPRINT] MOD-L02-016 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-GOV-04
# [MODULE] zephyr.factor.governance.six_step_flow
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.governance.lifecycle_state_machine; zephyr.factor.governance.abs001_gate; zephyr.factor.governance.grayscale_rollout
# [CONSUMERS] zephyr.factor.governance.engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 六步流程严格顺序推进; 每步有准入/准出门禁; 复用lifecycle_state_machine状态
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法推进->拒绝; 门禁未过->拒绝+detail
# [TESTS] tests/factor/test_six_step_flow.py
# [A_module] module_id=MOD-L02-016 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-GOV-04 六步流程编排——因子从研究到实盘的治理流程。

六步：研究 → 开发 → 回测验证 → 纸面交易 → 灰度放量 → 实盘上线

每步有准入门禁（进入条件）和准出门禁（推进条件）。准出门禁复用 ABS001。
状态流转复用 lifecycle_state_machine 的 StateMachine。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 因子ID str
#   fields: factor_id（submit/get_status/check_exit_gate/advance 参数）
#   code: six_step_flow.py L81/L94/L110/L136
# - id: I2
#   name: 因子评估结果 EvaluationResult
#   fields: ic_mean/ir/oos_positive_rate/is_overfitted（准出门禁检查用）
#   code: six_step_flow.py L110 参数 eval_result
# 层: 算法
# - id: A1
#   name_zh: ① 提交因子建档
#   name_en: SixStepFlow.submit_factor
#   intro: 给因子建一台专属状态机，初始状态 research
#   desc: 无记录→create_factor_fsm() 存入 _factors → 返回当前态（L81-92）
#   inputs: I1
#   outputs: 初始状态名 research
# - id: A2
#   name_zh: ② 准出门禁检查
#   name_en: SixStepFlow.check_exit_gate
#   intro: 研究/开发两步随便走，回测及之后必须过ABS001质量门禁
#   desc: current==RESEARCH/DEVELOPMENT→直通；backtest及之后→check_factor_quality(eval_result)（L110-134）
#   inputs: I1 I2
#   outputs: (passed, detail)
#   invariant: 六步严格顺序推进；每步有准入/准出门禁
# - id: A3
#   name_zh: ③ 步骤推进
#   name_en: SixStepFlow.advance
#   intro: 过了准出门禁就把状态机推到下一步，到实盘封顶
#   desc: 已到production→拒；check_exit_gate未过→保持；过→fsm.transition(next_step)（L136-160）
#   inputs: I1 I2 A2
#   outputs: (new_step, message)
# - id: A4
#   name_zh: ④ 流程状态查询
#   name_en: SixStepFlow.get_status
#   intro: 查因子现在六步里的哪一步、中文名叫啥、还能不能推
#   desc: fsm.current_state→FlowStatus(step_index=SIX_STEPS.index, step_name=STEP_NAMES映射, can_advance)（L94-108）
#   inputs: I1
#   outputs: FlowStatus 或 None
# 层: 输出
# - id: O1
#   name_zh: 六步流程状态 FlowStatus
#   name_en: flow status
#   intro: 当前步骤/中文名/步骤索引/可否推进四件套
#   downstream: 治理引擎 engine MOD-L02-017
# - id: O2
#   name_zh: 提交/推进结果 (step, str)
#   name_en: advance result
#   intro: 新步骤名加一句人话消息，卡门禁时说明原因
#   downstream: 治理引擎 engine MOD-L02-017
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# A2 --> A3
# I1 --> A4
# A1 --> O2
# A3 --> O2
# A4 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass

from zephyr.factor.core.evaluation.backtest import EvaluationResult
from zephyr.factor.governance.abs001_gate import check_factor_quality
from zephyr.factor.governance.lifecycle_state_machine import (
    BACKTEST,
    DEVELOPMENT,
    GRAYSCALE,
    PAPER,
    PRODUCTION,
    RESEARCH,
    create_factor_fsm,
)
from zephyr.shared.lifecycle.state_machine import InvalidTransitionError, StateMachine

# 六步流程定义
SIX_STEPS = [RESEARCH, DEVELOPMENT, BACKTEST, PAPER, GRAYSCALE, PRODUCTION]
STEP_NAMES = {
    RESEARCH: "研究",
    DEVELOPMENT: "开发",
    BACKTEST: "回测验证",
    PAPER: "纸面交易",
    GRAYSCALE: "灰度放量",
    PRODUCTION: "实盘上线",
}


@dataclass
class FlowStatus:
    """因子在六步流程中的状态。

    Attributes:
        factor_id: 因子ID
        current_step: 当前步骤（状态名）
        step_name: 当前步骤中文名
        step_index: 当前步骤索引（0-5）
        can_advance: 是否可推进到下一步
    """

    factor_id: str
    current_step: str
    step_name: str
    step_index: int
    can_advance: bool


class SixStepFlow:
    """六步流程编排器。

    每个因子持有自己的 StateMachine 实例，按六步顺序推进。
    推进到灰度/实盘阶段需要通过 ABS001 门禁。
    """

    def __init__(self) -> None:
        self._factors: dict[str, StateMachine[str]] = {}

    def submit_factor(self, factor_id: str) -> str:
        """提交因子进入流程（初始状态 research）。

        Args:
            factor_id: 因子ID

        Returns:
            初始状态名
        """
        if factor_id not in self._factors:
            self._factors[factor_id] = create_factor_fsm()
        return self._factors[factor_id].current_state

    def get_status(self, factor_id: str) -> FlowStatus | None:
        """获取因子流程状态。未提交返回 None。"""
        fsm = self._factors.get(factor_id)
        if fsm is None:
            return None
        current = fsm.current_state
        step_index = SIX_STEPS.index(current) if current in SIX_STEPS else -1
        can_advance = step_index < len(SIX_STEPS) - 1
        return FlowStatus(
            factor_id=factor_id,
            current_step=current,
            step_name=STEP_NAMES.get(current, current),
            step_index=step_index,
            can_advance=can_advance,
        )

    def check_exit_gate(self, factor_id: str, eval_result: EvaluationResult) -> tuple[bool, str]:
        """检查准出门禁——当前步骤是否可推进。

        回测验证（backtest）及之后的步骤需要通过 ABS001 门禁。
        研究/开发步骤无门禁要求（直接推进）。

        Args:
            factor_id: 因子ID
            eval_result: 因子评估结果

        Returns:
            (passed, detail)
        """
        fsm = self._factors.get(factor_id)
        if fsm is None:
            return False, "因子未提交流程"
        current = fsm.current_state
        # research → development: 无门禁
        if current == RESEARCH:
            return True, ""
        # development → backtest: 无门禁
        if current == DEVELOPMENT:
            return True, ""
        # backtest 及之后: 需要 ABS001 门禁
        return check_factor_quality(eval_result)

    def advance(self, factor_id: str, eval_result: EvaluationResult) -> tuple[str, str]:
        """推进因子到下一步。

        Args:
            factor_id: 因子ID
            eval_result: 因子评估结果（用于门禁检查）

        Returns:
            (new_step, message)
        """
        fsm = self._factors.get(factor_id)
        if fsm is None:
            return "", "因子未提交流程"
        current = fsm.current_state
        if current not in SIX_STEPS or SIX_STEPS.index(current) >= len(SIX_STEPS) - 1:
            return current, "已到实盘上线，无法继续推进"
        passed, detail = self.check_exit_gate(factor_id, eval_result)
        if not passed:
            return current, f"准出门禁未通过: {detail}"
        next_step = SIX_STEPS[SIX_STEPS.index(current) + 1]
        try:
            fsm.transition(next_step)
            return next_step, f"推进到: {STEP_NAMES.get(next_step, next_step)}"
        except InvalidTransitionError as e:
            return current, f"状态转换失败: {e}"

    def get_factor_fsm(self, factor_id: str) -> StateMachine[str] | None:
        """获取因子底层状态机（供 engine 使用）。"""
        return self._factors.get(factor_id)
