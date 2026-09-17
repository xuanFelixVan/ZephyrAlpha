# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t.costs
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] decimal; zephyr.backtest.core.cost_model_calibration; zephyr.backtest.core.matching_logic
# [CONSUMERS] zephyr.strategy_factory.owner_band_t.engine; tests/strategy_factory/test_s_owner_001_costs.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 零费率字面量（佣金/地板=matching_logic 真源，滑点/冲击=cost_model_calibration 标定真源）；ETF 免印花税+免过户费（与股票费率结构差异如实体现）；流动性输入=PIT 修正的 t-1 日真实成交额（当日额收盘才可知）
# [MODIFY-GUARD] 禁在本件引入第二套费率字面量
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CostCalibrationError(非法输入,Fail-Closed)
# [TESTS] tests/strategy_factory/test_s_owner_001_costs.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""H2 真成本模型全套封装（策略卡 §三「成本：H2 真成本模型全套」落地）。

费腿:
  1. 佣金 = max(notional * COMMISSION_RATE, MIN_COMMISSION)   [matching_logic 真源]
  2. 滑点 = notional * resolve_slippage_bps(liquidity_input)  [标定分层]
  3. 冲击 = notional * impact_level_for_tier(tier).cost_ratio_at(participation)
  4. 做T 加成 = notional * T_EXTRA_COST_BPS（冻结 1.0bp/边）
  5. 印花税/过户费 = 0（ETF 法定豁免——如实体现与股票差异）
流动性输入: 上一交易日的 510300 真实日成交额（PIT 修正；冻结文档「当日成交额」
按标定件「40 日 ADV 单调近似」语义取 t-1 值，同一把尺子前移一日，出证报告披露）。
"""

from __future__ import annotations

from decimal import Decimal

from zephyr.backtest.core import cost_model_calibration as cc
from zephyr.backtest.core.matching_logic import COMMISSION_RATE, MIN_COMMISSION

T_EXTRA_COST_BPS = Decimal("1.0")  # 做T 额外成本（冻结，bp/边）


def total_cost_yuan(
    notional_yuan: float,
    liquidity_input_yuan: float | None,
    *,
    is_t_trade: bool = False,
) -> float:
    """单边成交全成本（元）=佣金+滑点+冲击(+做T 加成)。

    :param notional_yuan: 成交名义（元）
    :param liquidity_input_yuan: 流动性输入（t-1 日真实成交额；None 走 universal 档）
    :param is_t_trade: 做T 单（叠加冻结加成 bp）
    """
    if notional_yuan <= 0:
        return 0.0
    # 1) 佣金（真源 Decimal 费率；地板 5 元）
    commission = max(notional_yuan * float(COMMISSION_RATE), float(MIN_COMMISSION))
    # 2) 滑点腿（标定分层唯一入口）
    slip_bps = cc.resolve_slippage_bps(
        float(liquidity_input_yuan) if liquidity_input_yuan else None
    )
    slippage = notional_yuan * float(slip_bps) / 10000.0
    # 3) 冲击腿（尺寸相关；tier 越界 Fail-Closed 抛错）
    if liquidity_input_yuan and liquidity_input_yuan > 0:
        tier = cc.liquidity_tier(float(liquidity_input_yuan))
        level = cc.impact_level_for_tier(tier)
        participation = notional_yuan / float(liquidity_input_yuan)
        impact = notional_yuan * level.cost_ratio_at(participation)
    else:
        impact = 0.0
    # 4) 做T 加成
    t_extra = notional_yuan * float(T_EXTRA_COST_BPS) / 10000.0 if is_t_trade else 0.0
    return commission + slippage + impact + t_extra
