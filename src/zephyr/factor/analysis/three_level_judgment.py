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
"""

D-FACTOR-ANA-07 三级判定——按 IC 均值将因子分为优秀/合格/淘汰。

判定规则（默认）：
- |IC均值| > 0.1 → 优秀
- |IC均值| > 0.05 → 合格
- 否则 → 淘汰

策略参数从 _config.yaml 读取（excellent_ic, pass_ic）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 因子评估指标 float
#   fields: ic 均值（ir/oos_rate 保留接口兼容未使用）
#   code: judge_factor 函数参数
# - id: I2
#   name: 判定阈值配置
#   fields: three_level_judgment.excellent_ic=0.1 / pass_ic=0.05
#   code: _config.yaml L8-10
# - id: I3
#   name: 批量评估结果 dict[str, EvaluationResult]
#   fields: factor_id → 评估结果（judge_batch 用）
#   code: results 函数参数
# 层: 算法
# - id: A1
#   name_zh: ① 单因子三级判定
#   name_en: judge_factor
#   intro: 按IC均值绝对值把因子分成优秀/合格/淘汰三档
#   desc: |IC|≥excellent_ic→优秀；|IC|≥pass_ic→合格；否则→淘汰（L53-59）
#   inputs: I1 I2
#   outputs: 等级字符串（优秀/合格/淘汰）
#   invariant: 纯函数无IO；判定仅基于IC均值绝对值
# - id: A2
#   name_zh: ② 批量三级判定
#   name_en: judge_batch
#   intro: 字典推导式逐因子调单因子判定，一次出一批等级
#   desc: 对 results 每项取 ic_mean/ir/oos_positive_rate 调 judge_factor（L62-71）
#   inputs: I3 A1
#   outputs: dict[factor_id → 等级]
# 层: 输出
# - id: O1
#   name_zh: 单因子等级 str
#   name_en: factor grade
#   intro: 优秀/合格/淘汰三档之一
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 批量等级映射 dict[str, str]
#   name_en: batch grade dict
#   intro: factor_id→等级的批量判定结果
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A2
# A1 --> A2
# A1 --> O1
# A2 --> O2
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
