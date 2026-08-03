# [BLUEPRINT] MOD-L02-008 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-07
# [MODULE] zephyr.factor.analysis.three_level_judgment
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数——无IO依赖; 判定基于IC均值绝对值
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->"淘汰"; 阈值从配置读取
# [TESTS] tests/factor/test_three_level_judgment.py
# [A_module] module_id=MOD-L02-008 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-FACTOR-ANA-07 三级判定——按 IC 均值将因子分为优秀/合格/淘汰。

判定规则（默认）：
- |IC均值| > 0.1 → 优秀
- |IC均值| > 0.05 → 合格
- 否则 → 淘汰

策略参数从 _config.yaml 读取（excellent_ic, pass_ic）。
"""
from __future__ import annotations

from zephyr.factor.analysis import load_analysis_config
from zephyr.factor.core.evaluation.backtest import EvaluationResult

_EXCELLENT = "优秀"
_PASS = "合格"
_REJECT = "淘汰"


def _get_thresholds() -> tuple[float, float]:
    """从配置读取判定阈值 (excellent_ic, pass_ic)。"""
    cfg = load_analysis_config()
    tj = cfg.get("three_level_judgment", {})
    return float(tj.get("excellent_ic", 0.1)), float(tj.get("pass_ic", 0.05))


def judge_factor(ic: float, ir: float = 0.0, oos_rate: float = 0.0) -> str:
    """按 IC 均值绝对值判定因子等级。

    Args:
        ic: IC 均值
        ir: IR（未使用，保留接口兼容）
        oos_rate: OOS 正率（未使用，保留接口兼容）

    Returns:
        "优秀" / "合格" / "淘汰"
    """
    excellent_ic, pass_ic = _get_thresholds()
    abs_ic = abs(ic)
    if abs_ic >= excellent_ic:
        return _EXCELLENT
    if abs_ic >= pass_ic:
        return _PASS
    return _REJECT


def judge_batch(results: dict[str, EvaluationResult]) -> dict[str, str]:
    """批量判定多因子等级。

    Args:
        results: factor_id → EvaluationResult

    Returns:
        factor_id → 等级字符串
    """
    return {fid: judge_factor(r.ic_mean, r.ir, r.oos_positive_rate) for fid, r in results.items()}
