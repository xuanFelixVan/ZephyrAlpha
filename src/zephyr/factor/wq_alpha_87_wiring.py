# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.wq_alpha_87_wiring
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas; zephyr.factor.factor_base; zephyr.factor.wq_alpha_87; zephyr.factor.core.evaluation.metrics
# [CONSUMERS] 装配批/考试链（wire_wq_alpha_87 后 evaluate_factor/compute_ic_ir_table/StrategyRunner 经 FactorRegistry 解析 wq_alpha_* 因子）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 截面型公式禁单标的退化计算（compute 显式抛错防静默错值）; 注册幂等（重入跳过本件已接线条目，撞他类即抛错）; IC 委托 metrics.compute_ic_series/compute_ir 与 ic_ir_calc 同语义 PIT
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] factor_id 被他类占用->Alpha87WiringError; history 缺列/缺 symbol 层->Alpha87WiringError; 未接线考试链查册->KeyError(FactorRegistry.get 原语义)
# [TESTS] tests/research/factor/test_wq_alpha_87_wiring.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
WQ87 核接线件——wq_alpha_87 双委托注入点的真实装配（master_backlog P2-6「接线日即插」）。

接线语义（仓内权威记载=核头部 CONSUMERS「因子注册表/feature_store（register_all/validate_ic
委托注入点）」+ gpu_survey_v1「接线待装配批；接线后=因子批考批量面」）：

  1. 注册册登记：`wire_wq_alpha_87()` 经 `WqAlpha87.register_all(register_hook)` 把 87 个
     公式逐个装配为 FactorBase 适配类入 `FactorRegistry`（factor_id=`wq_alpha_001`..
     `wq_alpha_101`，domain=`wq_alpha`），幂等可重入。
  2. 调用链挂载：考试链 `evaluate_factor`/`compute_ic_ir_table`（backtest.py/ic_ir_calc.py）
     按 factor_id 查册取类。截面型公式无法逐标的计算（单标的输入截面 rank 恒 1 退化），
     适配类声明 `compute_panel(history)` 整面板一次计算；`_compute_factor_panel` 侧加
     duck-type 分支优先走 panel 路径（无该方法因子走原逐标的路径，零影响）。
  3. IC 委托装配：`make_ic_ir_hook(return_panel, horizon)` 产 validate_ic 的真实 ic_hook，
     委托 metrics.compute_ic_series/compute_ir（ic_ir_calc 同语义，纯函数无 IO）。

用法（装配批/考试入口一次性）::

    from zephyr.factor.wq_alpha_87_wiring import wire_wq_alpha_87, make_ic_ir_hook

    wire_wq_alpha_87()                    # 幂等；重复调用返回 0
    compute_ic_ir_table(["wq_alpha_101"], symbols, start, end)   # 考试链直用

显式不做：import 期自动注册（全局注册表副作用，污染所有 zephyr.factor 消费方与
测试隔离）——接线动作=显式调用本件；incremental_compute 逐标的语义与截面公式冲突，
不做（默认回退 compute 即抛错，诚实失败）。

依据: docs/_working/matrix_campaign/master_backlog_v2.md P2-6；mining/wq_alpha_87_wiring_v1.md。

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/wq_alpha_87_wiring.yaml
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Final

import pandas as pd

from zephyr.factor.core.evaluation.metrics import compute_ic_series, compute_ir
from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry
from zephyr.factor.wq_alpha_87 import WQ_ALPHA_87_IDS, Alpha87Error, WqAlpha87
from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__: Final = [
    "Alpha87WiringError",
    "WQ87_DOMAIN",
    "history_to_panels",
    "make_ic_ir_hook",
    "wire_wq_alpha_87",
    "wired_factor_ids",
]

WQ87_DOMAIN: Final = "wq_alpha"
"""87 个适配因子在 FactorMeta.domain 的统一域标记（list_by_domain(WQ87_DOMAIN) 批考面）。"""

_WQ_INPUT_COLUMNS: Final = ("open", "high", "low", "close", "volume", "amount")
_WIRED_MARKER: Final = "_wq_alpha_87_alpha_id"

_LIB = WqAlpha87()  # 无状态门面，全件共享单实例


class Alpha87WiringError(ZephyrBaseError):
    """WQ87 接线件调用失败（册位冲突/history 形态违例）。"""


def history_to_panels(history: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """load_history 形态长表（MultiIndex(symbol, trade_date)）→ WQ87 输入面板 dict。

    Args:
        history: index=(symbol, trade_date) 升序长表，columns 至少含
            open/high/low/close/volume/amount（load_history 出口归一口径：
            volume=股/价格复权连续/amount=元）。

    Returns:
        dict[str, pd.DataFrame]：6 字段各一张 (date×symbol) 宽面板。

    Raises:
        Alpha87WiringError: 缺必需列或缺 symbol 索引层。
    """
    missing = [c for c in _WQ_INPUT_COLUMNS if c not in history.columns]
    if missing:
        raise Alpha87WiringError(
            f"history missing columns {missing} (need {_WQ_INPUT_COLUMNS}, load_history normalized shape)"
        )
    if "symbol" not in getattr(history.index, "names", ()):
        raise Alpha87WiringError("history index must be MultiIndex carrying level 'symbol'")
    return {c: history[c].unstack(level="symbol").sort_index() for c in _WQ_INPUT_COLUMNS}


def _build_factor_class(alpha_id: int) -> type[FactorBase]:
    """构造第 alpha_id 号公式的 FactorBase 适配类（panel 感知，compute 显式拒单标的）。"""
    factor_id = f"wq_alpha_{alpha_id:03d}"
    degraded = _LIB.is_degraded_formula(alpha_id)

    class WqAlpha87Factor(FactorBase):
        meta = FactorMeta(
            factor_id=factor_id,
            name=f"WorldQuant Alpha #{alpha_id:03d}",
            domain=WQ87_DOMAIN,
            description=(
                "WorldQuant 101 精选 87 集公式（WQ87 核委托，截面型 panel 因子，"
                + ("IndNeutralize 已降级为全市场截面 demean)" if degraded else "仅依赖 OHLCV/成交额免费数据)")
            ),
            tags=["wq87", "cross-sectional"] + (["ind-neutralize-degraded"] if degraded else []),
        )

        _wq_alpha_87_alpha_id = alpha_id

        def compute_panel(self, history: pd.DataFrame) -> pd.DataFrame:
            """考试链整面板入口：MultiIndex 长表 → WQ87 公式 → (date×symbol) panel。"""
            return _LIB.compute(alpha_id, history_to_panels(history))

        def compute(self, data: pd.DataFrame, **kwargs: Any) -> pd.Series:
            raise Alpha87Error(
                f"alpha#{alpha_id} is cross-sectional: single-symbol compute would degenerate"
                " (rank over 1 column) - use compute_panel(history) or the"
                " evaluate_factor/compute_ic_ir_table chain"
            )

    WqAlpha87Factor.__name__ = f"WqAlpha{alpha_id:03d}"
    WqAlpha87Factor.__qualname__ = WqAlpha87Factor.__name__
    WqAlpha87Factor.__doc__ = f"WQ87 adapter: WorldQuant Alpha #{alpha_id:03d} (panel factor)"
    return WqAlpha87Factor


def wire_wq_alpha_87() -> int:
    """87 个 WQ 公式逐个入 FactorRegistry（幂等，撞他类即抛错）。

    Returns:
        本次新注册数量（首次=87，重入=0）。

    Raises:
        Alpha87WiringError: 某 factor_id 已被非本件类占用（册位冲突，不静默顶替）。
    """

    registered = 0

    def _hook(factor_id: str, alpha_id: int) -> None:
        nonlocal registered
        existing = FactorRegistry.registry.get(factor_id)
        if existing is not None:
            if getattr(existing, _WIRED_MARKER, None) == alpha_id:
                return  # 幂等重入：本件已接线，跳过
            raise Alpha87WiringError(
                f"factor_id '{factor_id}' already registered by {existing.__name__}"
                " (wq_alpha_* namespace collision, refuse to overwrite)"
            )
        FactorRegistry.register(_build_factor_class(alpha_id))
        registered += 1
        log.debug("wq_alpha_87 wiring: registered %s", factor_id)

    _LIB.register_all(_hook)
    return registered


def wired_factor_ids() -> list[str]:
    """当前已接线的 wq_alpha_* factor_id 列表（升序，批考面取单入口）。"""
    return sorted(
        fid
        for fid, cls in FactorRegistry.registry.items()
        if fid.startswith("wq_alpha_") and hasattr(cls, _WIRED_MARKER)
    )


def make_ic_ir_hook(
    return_panel: pd.DataFrame,
    horizon: int = 5,
) -> Callable[[str, pd.DataFrame], dict[str, Any]]:
    """validate_ic 的真实 ic_hook 工厂：委托 metrics 纯函数（ic_ir_calc 同语义）。

    Args:
        return_panel: (date×symbol) 前向收益面板（PIT：已实现收益，评估链同口径）。
        horizon: 前向收益周期（仅日志语义，对齐靠 index）。

    Returns:
        ic_hook(factor_id, values) -> {factor_id, ic_mean, ic_std, ir, sample_size}；
        空截面全 0（ERROR_CONTRACT 同 ic_ir_calc 容错语义，不阻断批内其他因子）。
    """

    def _hook(factor_id: str, values: pd.DataFrame) -> dict[str, Any]:
        ic = compute_ic_series(values, return_panel, horizon)
        if ic.empty:
            return {"factor_id": factor_id, "ic_mean": 0.0, "ic_std": 0.0, "ir": 0.0, "sample_size": 0}
        return {
            "factor_id": factor_id,
            "ic_mean": float(ic.mean()),
            "ic_std": float(ic.std(ddof=1)) if len(ic) >= 2 else 0.0,
            "ir": float(compute_ir(ic)),
            "sample_size": int(len(ic)),
        }

    return _hook
