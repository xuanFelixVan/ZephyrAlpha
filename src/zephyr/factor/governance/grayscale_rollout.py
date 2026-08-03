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
"""D-FACTOR-GOV-03 灰度发布——管理因子从 10% → 30% → 100% 的放量阶梯。

每个进入灰度阶段的因子从最小阶梯开始，通过 ABS001 门禁检查后可推进到下一阶梯。
达到 100% 后可推进到 production（实盘全量）。
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
