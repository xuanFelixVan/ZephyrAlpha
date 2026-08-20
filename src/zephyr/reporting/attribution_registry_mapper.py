# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.reporting.attribution_registry_mapper
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors（仅错误基类；输入为 reporting.attribution 已落地函数的产出 dict）
# [CONSUMERS] 调用方（experiment_registry attribution_result 回填批——62 号未施工清单 #4；本模块仅提供映射，不批量执行回填）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] method 枚举唯一真源=62 号 §7.2（brinson/factor_based/none）; Shapley/求和不变量 FAIL 的产出拒绝映射（fail-closed）; 不写字段=None（registry 只登记有值字段）; 纯映射无副作用（不触碰注册表 YAML）
# [MODIFY-GUARD] 62_business_registry_construction.md §7.2
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributionMappingError(ZA-RPT-0032)
# [TESTS] tests/reporting/test_attribution_registry_mapper.py
# [A_module] module_id=MOD-RPT-MAPPER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: shapley_strategy_attribution 产出 dict（shapley_values/full_portfolio_return/invariant_status）
# I2: validate_strategy_pnl_invariant 产出 dict（strategy_contributions/diff/invariant_status）
# F1: map_shapley_to_attribution_result（invariant PASS → method=factor_based + factor_contributions=shapley_values）
# F2: map_invariant_to_attribution_result（method=factor_based + factor_contributions=contribution_ratio + alpha=未解释残差 diff）
# F3: validate_attribution_result（registry 写入前形状校验：method 枚举 + 数值字段 NaN/非数值拒）
# O1: attribution_result dict（62 号 §7.2 形状：method/allocation_effect/selection_effect/interaction_effect/factor_contributions/alpha）
# [/ALGO_FLOW]
"""D_REPORTING — 归因结果 → experiment_registry.attribution_result 字段映射（62 号未施工清单 #4）。

54 号归因执行体已落地（``reporting.attribution``：StrategyPnlAccountant /
validate_strategy_pnl_invariant / shapley_strategy_attribution）；本模块把其产出 dict
映射为 62 号 §7.2 登记的 ``attribution_result`` 字段形状::

    {method: brinson/factor_based/none, allocation_effect, selection_effect,
     interaction_effect, factor_contributions, alpha}

边界（62 号 §4.4）：归因执行逻辑归 54 号，本字段仅登记结果；本模块**只做映射 +
形状校验，不批量执行回填**（回填批待排期，注册表 YAML 不在本模块触碰）。

依据: 62_business_registry_construction §7.2（attribution_result schema）+ 54 号 §3.5/§3.12
Version: 0.1.0
"""

from __future__ import annotations

import logging
import math
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

#: method 枚举（62 号 §7.2 attribution_result schema 唯一真源）
ALLOWED_METHODS: Final[tuple[str, ...]] = ("brinson", "factor_based", "none")
#: 数值字段（shape 校验用）
_NUMERIC_FIELDS: Final[tuple[str, ...]] = (
    "allocation_effect",
    "selection_effect",
    "interaction_effect",
    "alpha",
)


class AttributionMappingError(ZephyrBaseError):
    """归因映射输入非法（method 越枚举 / 不变量 FAIL / 数值 NaN）。"""

    error_code = "ZA-RPT-0032"


def _check_number(name: str, value: float) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError) as exc:
        raise AttributionMappingError(f"{name} 非数值: {value!r}") from exc
    if math.isnan(f) or math.isinf(f):
        raise AttributionMappingError(f"{name} 非法数值: {f}")
    return f


def build_attribution_result(
    method: str,
    *,
    allocation_effect: float | None = None,
    selection_effect: float | None = None,
    interaction_effect: float | None = None,
    factor_contributions: dict[str, float] | None = None,
    alpha: float | None = None,
) -> dict:
    """构造 62 号 §7.2 attribution_result 字段形状（None 字段不写出）。

    Raises:
        AttributionMappingError: method 越枚举 / 数值 NaN / factor_contributions 非数值。
    """
    if method not in ALLOWED_METHODS:
        raise AttributionMappingError(f"method 越枚举: {method!r}（允许 {ALLOWED_METHODS}，62 号 §7.2）")
    out: dict = {"method": method}
    for name, value in (
        ("allocation_effect", allocation_effect),
        ("selection_effect", selection_effect),
        ("interaction_effect", interaction_effect),
        ("alpha", alpha),
    ):
        if value is not None:
            out[name] = _check_number(name, value)
    if factor_contributions is not None:
        out["factor_contributions"] = {
            str(k): _check_number(f"factor_contributions[{k!r}]", v) for k, v in factor_contributions.items()
        }
    return out


def map_shapley_to_attribution_result(shapley_result: dict) -> dict:
    """``shapley_strategy_attribution`` 产出 → attribution_result（54 号 §3.12 → 62 号 §7.2）。

    Shapley 效率公理已保证 Σ=组合总收益；invariant_status != PASS 拒绝映射（fail-closed）。
    method=factor_based；factor_contributions=各策略 Shapley 值。
    """
    if shapley_result.get("invariant_status") != "PASS":
        raise AttributionMappingError(
            "Shapley 求和不变量非 PASS，拒绝映射（fail-closed）",
            details={"invariant_status": shapley_result.get("invariant_status")},
        )
    values = shapley_result.get("shapley_values")
    if not isinstance(values, dict) or not values:
        raise AttributionMappingError("shapley_values 缺失或为空")
    return build_attribution_result("factor_based", factor_contributions=values)


def map_invariant_to_attribution_result(invariant_result: dict) -> dict:
    """``validate_strategy_pnl_invariant`` 产出 → attribution_result（54 号 §3.5 → 62 号 §7.2）。

    factor_contributions=各策略 contribution_ratio；alpha 承载**未解释残差** diff
    （firm_pnl − Σstrategy_pnl：成交漏算/费率错算/T+1 跨日错位/裁剪副作用的量化残差，
    非 Brinson 语义 alpha，登记供回填后审计）。invariant FAIL 仍映射（FAIL 本身即
    须登记的审计事实，残差 alpha 即差异定位线索）。
    """
    contributions = invariant_result.get("strategy_contributions")
    if not isinstance(contributions, dict) or not contributions:
        raise AttributionMappingError("strategy_contributions 缺失或为空")
    ratios = {sid: c.get("contribution_ratio") for sid, c in contributions.items()}
    return build_attribution_result(
        "factor_based",
        factor_contributions=ratios,
        alpha=invariant_result.get("diff", 0.0),
    )


def validate_attribution_result(obj: dict) -> list[str]:
    """attribution_result 形状校验（registry 写入前 gate；空列表=合规）。

    校验：method 必填且在枚举内；数值字段可解析且非 NaN/inf；
    factor_contributions 须为 {str: 数值}。
    """
    violations: list[str] = []
    if not isinstance(obj, dict):
        return [f"attribution_result 须为 dict: {type(obj).__name__}"]
    method = obj.get("method")
    if method not in ALLOWED_METHODS:
        violations.append(f"method 缺失或越枚举: {method!r}（允许 {ALLOWED_METHODS}）")
    for name in _NUMERIC_FIELDS:
        if name in obj:
            try:
                _check_number(name, obj[name])
            except AttributionMappingError as exc:
                violations.append(str(exc))
    fc = obj.get("factor_contributions")
    if fc is not None:
        if not isinstance(fc, dict):
            violations.append(f"factor_contributions 须为 dict: {type(fc).__name__}")
        else:
            for k, v in fc.items():
                try:
                    _check_number(f"factor_contributions[{k!r}]", v)
                except AttributionMappingError as exc:
                    violations.append(str(exc))
    return violations


__all__: Final = [
    "ALLOWED_METHODS",
    "AttributionMappingError",
    "build_attribution_result",
    "map_invariant_to_attribution_result",
    "map_shapley_to_attribution_result",
    "validate_attribution_result",
]
