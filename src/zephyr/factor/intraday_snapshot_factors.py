# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-04
# [MODULE] zephyr.factor.intraday_snapshot_factors
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.factor_base
# [CONSUMERS] zephyr.factor.core.intraday_factor_loop; zephyr.runtime.intraday_main
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 横截面因子——仅依赖当前 tick 快照(close/volume/amount)，无历史序列需求; 盘中3秒周期可重算; volume=0 时回退 close 避免除零
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 失败返回 NaN Series（DagExecutor 容错）; 输入缺列抛 KeyError（调用方保证列存在）
# [TESTS] tests/factor/test_intraday_snapshot_factors.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""盘中横截面因子——基于最新 tick 快照计算（无历史序列依赖）。

真源：
    - D-FACTOR 蓝图 §D-FACTOR-04 盘中增量路径
    - 数据架构.md §8.2 流式路径（miniQMT 3秒 Tick）
    - H1 蓝图 §9 集成点（D-FACTOR → H1）

背景（治本，2026-08-03 实地演练发现）：
    IntradayFactorLoop 原仅依赖历史时序因子（momentum/MA 等），
    盘中 3 秒 tick 快照 DataFrame 只有 close/volume/amount 列，
    无历史窗口无法计算时序因子 → FactorRegistry 在盘中为空 → 链路空转。
    本模块提供纯横截面因子，仅依赖当前快照即可计算，填补盘中因子缺口。

因子清单：
    - intraday_close: 最新成交价（横截面基准价，供信号/风控读取）
    - intraday_vwap: 累计成交均价 = amount / volume（volume>0 时；否则回退 close）

数据契约（CTR-001 NormalizedMarketData 派生）：
    输入 DataFrame 由 IntradayFactorLoop.read_ticks_to_dataframe 构造，
    index=symbol，columns 至少含 close/volume/amount（见 _TICK_FIELD_MAP）。
"""

from __future__ import annotations

import logging

import pandas as pd

from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry

logger = logging.getLogger(__name__)


@FactorRegistry.register
class IntradayClose(FactorBase):
    """盘中最新成交价（横截面）。"""

    meta = FactorMeta(
        factor_id="intraday_close",
        name="盘中最新价",
        domain="technical",
        version="1.0.0",
        description="横截面因子：返回最新 tick close 价。盘中 3 秒周期可重算，供信号/风控作为基准价读取。",
        tags=["intraday", "cross-sectional", "price"],
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        return data["close"]


@FactorRegistry.register
class IntradayVwap(FactorBase):
    """盘中累计成交均价（amount/volume 横截面）。"""

    meta = FactorMeta(
        factor_id="intraday_vwap",
        name="盘中累计均价",
        domain="technical",
        version="1.0.0",
        description="横截面因子：累计成交均价 = amount / volume。"
        "volume=0 时回退为 close（避免除零），代表当日零成交时的价格基准。",
        tags=["intraday", "cross-sectional", "vwap"],
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        close = data["close"]
        volume = data["volume"]
        amount = data["amount"]
        # 默认回退 close；volume>0 处用 amount/volume 覆盖
        # .copy() 避免 SettingWithCopyWarning；.loc[mask] 保证对齐安全
        vwap = close.copy()
        mask = volume > 0
        if mask.any():
            vwap.loc[mask] = amount.loc[mask] / volume.loc[mask]
        return vwap
