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
"""

D-FACTOR-GOV-02 ABS001 上线门禁——因子进入灰度前的质量检查。

检查4项指标，全部通过才允许因子从 paper → grayscale：
1. IC 均值 > min_ic（默认 0.03）
2. IR > min_ir（默认 0.5）
3. OOS 正率 > min_oos_rate（默认 0.5）
4. 未判定过拟合（is_overfitted == False）

参数从 governance/_config.yaml 读取。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 因子评估结果 EvaluationResult
#   fields: ic_mean / ir / oos_positive_rate / is_overfitted 四项指标
#   code: abs001_gate.py L45 check_factor_quality 参数 result
# - id: I2
#   name: 门禁阈值配置 dict
#   fields: abs001_gate.min_ic=0.03 / min_ir=0.5 / min_oos_rate=0.5
#   code: governance/_config.yaml L5-8
# 层: 算法
# - id: A1
#   name_zh: ① 四项质量门禁检查
#   name_en: check_factor_quality
#   intro: IC均值、IR、OOS正率、过拟合标志四条全过才放行因子进灰度
#   desc: |ic_mean|<min_ic→fail；ir<min_ir→fail；oos_positive_rate<min_oos→fail；is_overfitted→fail；失败原因拼 detail（L55-69）
#   inputs: I1 I2
#   outputs: (passed: bool, detail: str)
#   invariant: 4条全过才放行；阈值从_config.yaml读取不硬编码
# - id: A2
#   name_zh: ② 门禁声明式描述生成
#   name_en: get_gate_spec
#   intro: 把四条检查规则打包成 dict，注册给治理引擎用
#   desc: 读阈值 → 拼 gate_id=ABS001 + checks 列表（metric/op/threshold）（L72-84）
#   inputs: I2
#   outputs: gate_spec dict（gate_id/description/checks）
# 层: 输出
# - id: O1
#   name_zh: 门禁判定结果 (bool, str)
#   name_en: gate check result
#   intro: passed=True放行；False时detail说明哪项不达标
#   downstream: 六步流程 six_step_flow MOD-L02-016；灰度发布 grayscale_rollout MOD-L02-015
# - id: O2
#   name_zh: 门禁规格 gate_spec dict
#   name_en: gate spec
#   intro: ABS001 门禁的声明式描述，供治理引擎注册
#   downstream: 治理引擎 engine MOD-L02-017
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# A1 --> O1
# A2 --> O2
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
