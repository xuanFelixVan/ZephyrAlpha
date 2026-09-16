# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t.intraday_t
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas
# [CONSUMERS] zephyr.strategy_factory.owner_band_t.engine; tests/strategy_factory/test_s_owner_001_engine.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 做T 额度=前收盘持仓（T+1 结构约束，当日新买股份不入额度）；纯决策函数无 I/O；15:00 强制平仓闭合当日回转
# [MODIFY-GUARD] 语义变更=考试冻结口径变更，冻结期禁改
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(非法参数)
# [TESTS] tests/strategy_factory/test_s_owner_001_engine.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""日内做T 臂——纯决策函数（编排见 engine）。

冻结口径（E4 冻结文档 §3）:
  * 开仓: 10:30 bar 收盘动量（bar0.close / 当日 open - 1）<= -0.5% 且当日已实现
    做T 亏损未触 0.5%×NAV 日亏停 且次数未满上限。
  * 平仓: 11:30/14:00/15:00 bar 收盘累计浮盈 >= +0.5% 即平；15:00 强制平。
  * 额度: 做T 仓位 <= 前收盘持仓（当日波段卖出扣减额度；当日波段买入不加持额度）。
"""

from __future__ import annotations

MOMENTUM_TRIGGER = -0.005  # 10:30 动量开仓阈（冻结）
PROFIT_TARGET = 0.005  # 浮盈平仓阈（冻结）
DAILY_T_LOSS_STOP = -0.005  # 当日已实现做T 亏损停（占 NAV，冻结）
LOT_SIZE = 100


def should_open_t(
    morning_ret: float,
    trips_used: int,
    max_trips: int,
    realized_t_today: float,
    nav_prev: float,
) -> bool:
    """10:30 bar 收盘判定是否开做T 仓。"""
    if trips_used >= max_trips:
        return False
    if morning_ret > MOMENTUM_TRIGGER:
        return False
    if nav_prev > 0 and realized_t_today <= DAILY_T_LOSS_STOP * nav_prev:
        return False  # 日亏停：当日停止做T
    return True


def should_close_t(entry_price: float, bar_close: float) -> bool:
    """浮盈达标平仓判定。"""
    if entry_price <= 0:
        raise ValueError("entry_price 必须为正")
    return bar_close >= entry_price * (1.0 + PROFIT_TARGET)


def round_lot(shares: float) -> int:
    """向下取整手（A 股 100 股/手）。"""
    if shares <= 0:
        return 0
    return int(shares // LOT_SIZE) * LOT_SIZE
