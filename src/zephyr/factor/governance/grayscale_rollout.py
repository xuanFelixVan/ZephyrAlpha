# [BLUEPRINT] MOD-L02-015 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-GOV-03
# [MODULE] zephyr.factor.governance.grayscale_rollout
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.governance; zephyr.factor.governance.abs001_gate
# [CONSUMERS] zephyr.factor.governance.engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 灰度阶梯从_config.yaml读取; 推进需通过ABS001门禁
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 已到100%->无法推进; 门禁未过->拒绝推进
# [TESTS] tests/factor/test_grayscale_rollout.py
# [A_module] module_id=MOD-L02-015 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-GOV-03 灰度发布——管理因子从 10% → 30% → 100% 的放量阶梯。

每个进入灰度阶段的因子从最小阶梯开始，通过 ABS001 门禁检查后可推进到下一阶梯。
达到 100% 后可推进到 production（实盘全量）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 因子ID str
#   fields: factor_id（init/get_status/advance 参数）
#   code: grayscale_rollout.py L64/L76/L100
# - id: I2
#   name: 因子评估结果 EvaluationResult
#   fields: ic_mean/ir/oos_positive_rate/is_overfitted（advance 门禁检查用）
#   code: grayscale_rollout.py L100 参数 eval_result
# - id: I3
#   name: 灰度阶梯配置 list[float]
#   fields: grayscale_rollout.stages=[0.1, 0.3, 1.0]（10%→30%→100%）
#   code: governance/_config.yaml L10-11
# 层: 算法
# - id: A1
#   name_zh: ① 灰度初始化
#   name_en: GrayscaleRollout.init_factor
#   intro: 因子刚进灰度，先放到最低一档阶梯10%
#   desc: _factor_stages[factor_id]=0 → 返回 stages[0]（L64-74）
#   inputs: I1 I3
#   outputs: 初始灰度比例 0.1
# - id: A2
#   name_zh: ② 阶梯推进
#   name_en: GrayscaleRollout.advance
#   intro: 过ABS001门禁就升一档放量，到100%封顶；未初始化先按10%初始化
#   desc: 未初始化→init_factor；已到顶→保持；check_promotion(ABS001)未过→保持当前比例；过→stage_index+1（L100-123）
#   inputs: I1 I2 I3 A1
#   outputs: (new_ratio, message)
#   invariant: 灰度阶梯从_config.yaml读取；推进需通过ABS001门禁
# - id: A3
#   name_zh: ③ 灰度状态查询
#   name_en: GrayscaleRollout.get_status
#   intro: 查因子当前放到几成仓，还能不能继续推
#   desc: stage_index→GrayscaleStatus(current_ratio=stages[idx], can_advance=idx<len(stages)-1)（L76-87）
#   inputs: I1 I3
#   outputs: GrayscaleStatus 或 None
# 层: 输出
# - id: O1
#   name_zh: 灰度状态 GrayscaleStatus
#   name_en: grayscale status
#   intro: 当前比例/阶梯索引/可否推进三件套
#   downstream: 治理引擎 engine MOD-L02-017
# - id: O2
#   name_zh: 阶梯推进结果 (float, str)
#   name_en: advance result
#   intro: 新灰度比例加一句人话消息，说明推没推成
#   downstream: 治理引擎 engine MOD-L02-017
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I1 --> A2
# I2 --> A2
# I3 --> A2
# A1 --> A2
# I1 --> A3
# I3 --> A3
# A3 --> O1
# A2 --> O2
"""

from __future__ import annotations

from dataclasses import dataclass, field

from zephyr.factor.core.evaluation.backtest import EvaluationResult
from zephyr.factor.governance import load_governance_config
from zephyr.factor.governance.abs001_gate import check_factor_quality


def _get_stages() -> list[float]:
    """从配置读取灰度阶梯。"""
    cfg = load_governance_config()
    stages = cfg.get("grayscale_rollout", {}).get("stages", [0.1, 0.3, 1.0])
    return [float(s) for s in stages]


@dataclass
class GrayscaleStatus:
    """因子灰度状态。

    Attributes:
        factor_id: 因子ID
        current_ratio: 当前灰度比例（0~1）
        stage_index: 当前阶梯索引
        can_advance: 是否可推进到下一阶梯
    """

    factor_id: str
    current_ratio: float
    stage_index: int
    can_advance: bool


class GrayscaleRollout:
    """因子灰度发布管理器。

    管理多个因子的灰度状态，按阶梯推进。
    """

    def __init__(self) -> None:
        self._stages = _get_stages()
        self._factor_stages: dict[str, int] = {}  # factor_id → stage_index

    def init_factor(self, factor_id: str) -> float:
        """初始化因子灰度（进入第一阶梯）。

        Args:
            factor_id: 因子ID

        Returns:
            初始灰度比例
        """
        self._factor_stages[factor_id] = 0
        return self._stages[0]

    def get_status(self, factor_id: str) -> GrayscaleStatus | None:
        """获取因子灰度状态。未初始化返回 None。"""
        idx = self._factor_stages.get(factor_id)
        if idx is None:
            return None
        can_advance = idx < len(self._stages) - 1
        return GrayscaleStatus(
            factor_id=factor_id,
            current_ratio=self._stages[idx],
            stage_index=idx,
            can_advance=can_advance,
        )

    def check_promotion(self, eval_result: EvaluationResult) -> tuple[bool, str]:
        """检查因子是否可通过 ABS001 门禁推进到下一阶梯。

        Args:
            eval_result: 因子最新评估结果

        Returns:
            (can_promote, detail)
        """
        return check_factor_quality(eval_result)

    def advance(self, factor_id: str, eval_result: EvaluationResult) -> tuple[float, str]:
        """推进因子到下一灰度阶梯。

        需通过 ABS001 门禁才能推进。已到 100% 则返回当前比例。

        Args:
            factor_id: 因子ID
            eval_result: 因子最新评估结果

        Returns:
            (new_ratio, message)
        """
        idx = self._factor_stages.get(factor_id)
        if idx is None:
            ratio = self.init_factor(factor_id)
            return ratio, f"初始化灰度，比例 {ratio:.0%}"
        if idx >= len(self._stages) - 1:
            return self._stages[idx], "已到100%，无法继续推进"
        passed, detail = self.check_promotion(eval_result)
        if not passed:
            return self._stages[idx], f"门禁未通过，保持当前比例: {detail}"
        new_idx = idx + 1
        self._factor_stages[factor_id] = new_idx
        return self._stages[new_idx], f"推进到阶梯 {new_idx}，比例 {self._stages[new_idx]:.0%}"

    @property
    def stages(self) -> list[float]:
        """灰度阶梯列表。"""
        return list(self._stages)
