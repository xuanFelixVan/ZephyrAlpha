# [BLUEPRINT] MOD-L02-014 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-GOV-02
# [MODULE] zephyr.factor.governance.abs001_gate
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest; zephyr.factor.governance
# [CONSUMERS] zephyr.factor.governance.six_step_flow; zephyr.factor.governance.engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 4条全过才放行; 阈值从_config.yaml读取不硬编码
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 评估结果为None->fail; 任一指标不达标->fail+detail说明
# [TESTS] tests/factor/test_abs001_gate.py
# [A_module] module_id=MOD-L02-014 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-FACTOR-GOV-02 ABS001 上线门禁——因子进入灰度前的质量检查。

检查4项指标，全部通过才允许因子从 paper → grayscale：
1. IC 均值 > min_ic（默认 0.03）
2. IR > min_ir（默认 0.5）
3. OOS 正率 > min_oos_rate（默认 0.5）
4. 未判定过拟合（is_overfitted == False）

参数从 governance/_config.yaml 读取。
"""
from __future__ import annotations

from zephyr.factor.core.evaluation.backtest import EvaluationResult
from zephyr.factor.governance import load_governance_config

GATE_ID = "ABS001"


def _get_thresholds() -> tuple[float, float, float]:
    """从配置读取门禁阈值 (min_ic, min_ir, min_oos_rate)。"""
    cfg = load_governance_config()
    g = cfg.get("abs001_gate", {})
    return (
        float(g.get("min_ic", 0.03)),
        float(g.get("min_ir", 0.5)),
        float(g.get("min_oos_rate", 0.5)),
    )


def check_factor_quality(result: EvaluationResult) -> tuple[bool, str]:
    """检查因子评估结果是否满足 ABS001 上线门禁。

    Args:
        result: evaluate_factor 返回的 EvaluationResult

    Returns:
        (passed, detail)：passed=True 时 detail 为空；
        passed=False 时 detail 说明哪项不达标。
    """
    min_ic, min_ir, min_oos = _get_thresholds()
    failures: list[str] = []

    if abs(result.ic_mean) < min_ic:
        failures.append(f"IC均值 {result.ic_mean:.4f} < {min_ic}")
    if result.ir < min_ir:
        failures.append(f"IR {result.ir:.4f} < {min_ir}")
    if result.oos_positive_rate < min_oos:
        failures.append(f"OOS正率 {result.oos_positive_rate:.2%} < {min_oos:.0%}")
    if result.is_overfitted:
        failures.append("判定过拟合")

    if failures:
        return False, f"ABS001 门禁未通过: {'; '.join(failures)}"
    return True, ""


def get_gate_spec() -> dict:
    """返回 ABS001 门禁的声明式描述（用于注册到治理引擎）。"""
    min_ic, min_ir, min_oos = _get_thresholds()
    return {
        "gate_id": GATE_ID,
        "description": "因子上线前质量门禁",
        "checks": [
            {"metric": "ic_mean", "op": ">=", "threshold": min_ic},
            {"metric": "ir", "op": ">=", "threshold": min_ir},
            {"metric": "oos_positive_rate", "op": ">=", "threshold": min_oos},
            {"metric": "is_overfitted", "op": "==", "threshold": False},
        ],
    }
