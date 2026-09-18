# [BLUEPRINT] MOD-SOWNER-002 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_regime_switcher.costs
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] typing; zephyr.backtest.core.cost_model_calibration; zephyr.backtest.core.matching_logic
# [CONSUMERS] zephyr.strategy_factory.owner_regime_switcher.engine; tests/strategy_factory/test_s_owner_002_engine.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 零费率字面量（佣金/地板=matching_logic 真源，滑点/冲击=cost_model_calibration 标定真源）；ETF 免印花税+免过户费；流动性输入=PIT 修正的 t-1 日真实成交额（当日额收盘才可知）；单边计费买卖同价（冻结 §4）
# [MODIFY-GUARD] 禁在本件引入第二套费率字面量
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CostCalibrationError(非法输入,Fail-Closed)
# [TESTS] tests/strategy_factory/test_s_owner_002_engine.py
# [A_module] module_id=MOD-SOWNER-002 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""成本真源封装（冻结 §4：两腿成本模型逐参数一致，切换腿多出的换手即切换成本）。

费腿（与 S-OWNER-001 costs 同一真源链，零新费率）:
  1. 佣金 = max(notional * COMMISSION_RATE, MIN_COMMISSION)   [matching_logic 真源]
  2. 滑点 = notional * resolve_slippage_bps(liquidity_input)  [标定分层]
  3. 冲击 = notional * impact_level_for_tier(tier).cost_ratio_at(participation)
  4. 印花税/过户费 = 0（ETF 法定豁免）
slippage_scale 参数仅供红蓝③「切换成本极端化」注入使用（×50），正式跑数恒为 1.0。
"""

from __future__ import annotations

from typing import Final

from zephyr.backtest.core import cost_model_calibration as cc
from zephyr.backtest.core.matching_logic import COMMISSION_RATE, MIN_COMMISSION

__all__: Final = ["total_cost_yuan"]


def total_cost_yuan(
    notional_yuan: float,
    liquidity_input_yuan: float | None,
    *,
    slippage_scale: float = 1.0,
) -> float:
    """单边成交全成本（元）=佣金+滑点(+冲击)。

    :param notional_yuan: 成交名义（元）
    :param liquidity_input_yuan: 流动性输入（t-1 日该标的真实成交额；None 走 universal 档）
    :param slippage_scale: 滑点放大器（红蓝对抗专用；正式考试=1.0）
    """
    if notional_yuan <= 0:
        return 0.0
    # 1) 佣金（真源 Decimal 费率；地板 5 元）
    commission = max(notional_yuan * float(COMMISSION_RATE), float(MIN_COMMISSION))
    # 2) 滑点腿（标定分层唯一入口；×scale 供红蓝极端化）
    slip_bps = cc.resolve_slippage_bps(
        float(liquidity_input_yuan) if liquidity_input_yuan else None
    )
    slippage = notional_yuan * float(slip_bps) * slippage_scale / 10000.0
    # 3) 冲击腿（尺寸相关；tier 越界 Fail-Closed 抛错）
    if liquidity_input_yuan and liquidity_input_yuan > 0:
        tier = cc.liquidity_tier(float(liquidity_input_yuan))
        level = cc.impact_level_for_tier(tier)
        participation = notional_yuan / float(liquidity_input_yuan)
        impact = notional_yuan * level.cost_ratio_at(participation)
    else:
        impact = 0.0
    return commission + slippage + impact
