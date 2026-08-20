# [BLUEPRINT] MOD-L02-017 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-GOV-05
# [MODULE] zephyr.factor.governance.engine
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.governance.six_step_flow; zephyr.factor.governance.grayscale_rollout; zephyr.factor.governance.lifecycle_state_machine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 编排六步流程+灰度发布; 推进需通过ABS001门禁
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未提交因子->拒绝; 门禁未过->拒绝+detail
# [TESTS] tests/factor/test_governance_engine.py
# [A_module] module_id=MOD-L02-017 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-GOV-05 因子治理引擎——顶层编排六步流程+灰度发布。

组合 SixStepFlow + GrayscaleRollout + LifecycleStateMachine，
提供因子从提交到实盘的完整治理入口。

职责边界：
- submit_factor: 提交因子进入治理流程
- evaluate: 查询因子当前状态
- promote: 推进因子到下一步（自动检查门禁+灰度阶梯）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 因子ID str
#   fields: factor_id（submit/evaluate/promote 三入口共用参数）
#   code: engine.py L62/L74/L91
# - id: I2
#   name: 因子评估结果 EvaluationResult
#   fields: ic_mean/ir/oos_positive_rate/is_overfitted（promote 门禁检查用）
#   code: engine.py L91 参数 eval_result
# 层: 算法
# - id: A1
#   name_zh: ① 提交因子入治理
#   name_en: FactorGovernanceEngine.submit_factor
#   intro: 把新因子登记进六步流程，初始状态 research
#   desc: 委托 SixStepFlow.submit_factor 建因子FSM → 返回 "research"（L62-72）
#   inputs: I1
#   outputs: 初始状态名 research
# - id: A2
#   name_zh: ② 治理状态查询
#   name_en: FactorGovernanceEngine.evaluate
#   intro: 一次查出因子在六步流程和灰度阶梯上的综合状态
#   desc: flow.get_status + rollout.get_status → 合并成 FactorStatus（L74-89）
#   inputs: I1
#   outputs: FactorStatus（flow_status + grayscale_status）
# - id: A3
#   name_zh: ③ 推进编排
#   name_en: FactorGovernanceEngine.promote
#   intro: 推因子走下一步：灰度步就推灰度阶梯，灰度满100%自动推进实盘，进灰度时自动初始化10%
#   desc: 当前=grayscale→rollout.advance，ratio≥1.0且step_index<5→flow.advance进production；其他步→flow.advance，落到grayscale→rollout.init_factor（L106-124）
#   inputs: I1 I2
#   outputs: (current_state, message)
#   invariant: 编排六步流程+灰度发布；推进需通过ABS001门禁
# 层: 输出
# - id: O1
#   name_zh: 因子治理综合状态 FactorStatus
#   name_en: factor governance status
#   intro: 六步流程状态+灰度状态打包，一眼看清因子走到哪
#   downstream: 无下游/内部使用（顶层治理入口）
# - id: O2
#   name_zh: 提交/推进结果消息 (state, str)
#   name_en: promote result
#   intro: 当前状态加一句人话消息，说明推没推成、卡在哪条门禁
#   downstream: 无下游/内部使用（顶层治理入口）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I2 --> A3
# A2 --> O1
# A1 --> O2
# A3 --> O2
"""

from __future__ import annotations

from dataclasses import dataclass

from zephyr.factor.core.evaluation.backtest import EvaluationResult
from zephyr.factor.governance.grayscale_rollout import GrayscaleRollout, GrayscaleStatus
from zephyr.factor.governance.lifecycle_state_machine import GRAYSCALE, PRODUCTION
from zephyr.factor.governance.six_step_flow import FlowStatus, SixStepFlow


@dataclass
class FactorStatus:
    """因子治理综合状态。

    Attributes:
        factor_id: 因子ID
        flow_status: 六步流程状态
        grayscale_status: 灰度状态（仅 grayscale 阶段有值）
    """

    factor_id: str
    flow_status: FlowStatus | None
    grayscale_status: GrayscaleStatus | None


class FactorGovernanceEngine:
    """因子治理引擎——顶层编排。

    组合 SixStepFlow（六步流程）和 GrayscaleRollout（灰度发布），
    提供统一的因子治理入口。
    """

    def __init__(self) -> None:
        self._flow = SixStepFlow()
        self._rollout = GrayscaleRollout()

    def submit_factor(self, factor_id: str) -> str:
        """提交因子进入治理流程。

        Args:
            factor_id: 因子ID

        Returns:
            初始状态名（"research"）
        """
        self._flow.submit_factor(factor_id)
        return "research"

    def evaluate(self, factor_id: str) -> FactorStatus:
        """评估因子当前治理状态。

        Args:
            factor_id: 因子ID

        Returns:
            FactorStatus
        """
        flow_status = self._flow.get_status(factor_id)
        grayscale_status = self._rollout.get_status(factor_id)
        return FactorStatus(
            factor_id=factor_id,
            flow_status=flow_status,
            grayscale_status=grayscale_status,
        )

    def promote(self, factor_id: str, eval_result: EvaluationResult) -> tuple[str, str]:
        """推进因子到下一治理阶段。

        自动处理六步流程推进和灰度阶梯推进：
        - 到达 grayscale 步骤时自动初始化灰度
        - 在 grayscale 步骤中推进灰度阶梯
        - 灰度到 100% 后推进到 production

        Args:
            factor_id: 因子ID
            eval_result: 因子评估结果

        Returns:
            (current_state, message)
        """
        flow_status = self._flow.get_status(factor_id)
        if flow_status is None:
            return "", "因子未提交，请先调用 submit_factor"
        current = flow_status.current_step
        # 如果当前在 grayscale 步骤，推进灰度阶梯
        if current == GRAYSCALE:
            new_ratio, msg = self._rollout.advance(factor_id, eval_result)
            # 如果灰度到 100%，推进到 production
            if new_ratio >= 1.0 and flow_status.step_index < 5:
                new_step, step_msg = self._flow.advance(factor_id, eval_result)
                return new_step, f"{msg}; {step_msg}"
            return current, msg
        # 其他步骤：推进六步流程
        new_step, msg = self._flow.advance(factor_id, eval_result)
        # 如果推进到 grayscale，初始化灰度
        if new_step == GRAYSCALE:
            ratio = self._rollout.init_factor(factor_id)
            return new_step, f"{msg}; 初始化灰度比例 {ratio:.0%}"
        return new_step, msg
