# [BLUEPRINT] MOD-SOWNER-002 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_regime_switcher.packages
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] pandas; typing
# [CONSUMERS] zephyr.strategy_factory.owner_regime_switcher.engine; zephyr.strategy_factory.owner_regime_switcher.exam
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 信号=代理包目标仓位序列（t 收盘判定，由引擎统一 shift 后 t+1 开盘成交，本件不做 shift）；包 A=510300 均线波段（close>MA20 满仓/否则 0）；包 B=篮子 20 日动量 top-1 满仓（仅 top-1 变更才换仓）；标的未上市/数据缺失=不可持有（NaN 防御）
# [MODIFY-GUARD] 考试冻结文档 §3——冻结后语义变更=第二真源作弊
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(窗口不足/空面板)
# [TESTS] tests/strategy_factory/test_s_owner_002_engine.py
# [A_module] module_id=MOD-SOWNER-002 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""代理包信号面（冻结 §3；两包均为简化代理，非可毕业策略）。

包 A（防御/ETF 波段代理）: 510300，close > MA20 → 目标 1.0；close < MA20 → 0。
包 B（进攻/动量代理）: 篮子 {510050,159915,510300,510500,512100}，20 日动量最大者
  目标 1.0，其余 0；数据缺失标的自动失去候选资格。
两包目标序列由同一引擎消费（同池对照：切换 on/off 只改"启用集合+上限"，不改信号）。
"""

from __future__ import annotations

from typing import Final

import pandas as pd

PACKAGE_A_SYMBOL = "510300"
PACKAGE_B_BASKET: tuple[str, ...] = ("510050", "159915", "510300", "510500", "512100")
MA_WINDOW_DEFAULT = 20
MOM_WINDOW_DEFAULT = 20

__all__: Final = [
    "PACKAGE_A_SYMBOL",
    "PACKAGE_B_BASKET",
    "package_a_targets",
    "package_b_targets",
]


def package_a_targets(daily_close: pd.Series, ma_window: int = MA_WINDOW_DEFAULT) -> pd.Series:
    """包 A 目标仓位（{0.0,1.0}；t 收盘判定）。

    :param daily_close: 510300 聚合日线收盘（升序；index=trade_date）。
    """
    close = pd.to_numeric(daily_close, errors="coerce").dropna()
    if len(close) < ma_window + 1:
        raise ValueError(f"包 A 数据不足 MA 窗口: {len(close)} < {ma_window + 1}")
    ma = close.rolling(ma_window).mean()
    target = (close > ma).astype(float)
    target[ma.isna()] = 0.0  # 预热段=0（不持有）
    return target.reindex(daily_close.index).fillna(0.0)


def package_b_targets(
    close_panel: pd.DataFrame,
    mom_window: int = MOM_WINDOW_DEFAULT,
) -> pd.DataFrame:
    """包 B 目标仓位（篮子 one-hot top-1；t 收盘判定）。

    :param close_panel: 列=篮子标的，index=交易日（升序）。缺失值=该标的当日无候选资格。
    """
    if close_panel.empty:
        raise ValueError("包 B 篮子面板为空")
    close = close_panel.apply(pd.to_numeric, errors="coerce")
    mom = close / close.shift(mom_window) - 1.0  # 数据不足/未上市=NaN=无候选资格
    target = pd.DataFrame(0.0, index=close.index, columns=close.columns)
    valid = mom.dropna(how="all")  # 全 NaN 行（窗口预热/全篮断供）=无 top-1，显式剔除
    if not valid.empty:
        top1 = valid.idxmax(axis=1)
        for dt, sym in top1.items():
            target.loc[dt, sym] = 1.0
    return target
