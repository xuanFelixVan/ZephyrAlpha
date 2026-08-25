# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.wq_alpha_87
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas; numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 因子注册表/feature_store（register_all/validate_ic 委托注入点）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 87公式仅依赖OHLCV/成交额(vwap=amount/volume,returns=close.pct_change,cap=close*volume代理); IndNeutralize降级为全市场截面demean(DEGRADED_FORMULAS标注); rolling时序算子天然PIT无未来函数; 101剔除14个(EXCLUDED_IDS)理由留档
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知/排除编号->Alpha87Error; 缺必需字段->Alpha87Error
# [TESTS] tests/factor/test_wq_alpha_87.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""92 87-Alpha：WorldQuant 101 精选 87 公式库（CAND-FAC-010 / B1-00847，GATE-92-01）。

范围裁定：
  - WorldQuant 101 Alphas（Kakushadze & Tulchinsky 2015, arXiv:1511.04310）中
    剔除 14 个依赖行业分类（IndNeutralize）或市值（cap 无免费真源）数据的公式
    （EXCLUDED_IDS，对齐知名开源实现的 87 集口径），余 87 个逐个实现。
  - 剔除清单：{48, 56, 58, 59, 63, 67, 69, 70, 76, 80, 82, 90, 96, 100}。
  - 保留集中仍含 IndNeutralize 的 5 个（DEGRADED_FORMULAS={79, 87, 91, 93, 97}）
    降级为全市场截面 demean（IndNeutralize(x, cls) ≈ x - mean(x)，无行业数据
    下的最近似），is_degraded_formula() 显式标注，IC 验证自然反映失真。
  - 数据仅依赖 OHLCV/成交额免费数据：vwap=amount/volume 派生（可显式覆盖）、
    returns=close.pct_change()、cap=close*volume 代理（保留集中无 cap 公式，
    派生仅供扩展）。

PIT 合规（INV-004 对齐）：全部公式由 rolling/shift 时序算子与截面算子复合，
天然仅用截至当日的数据，无未来函数；tests 锚定截断前缀不变性。

IC/IR 验证：validate_ic 经 ic_hook 委托（复用 analysis/ic_ir_calc 语义，运行时
装配批接 compute_ic_ir_table/evaluate_factor）；入因子注册经 register_all 的
register_hook 委托（FactorRegistry/feature_store 接线留装配批）。

依据: §1.2 子模块；construction_backlog_dig.tsv B1-00847；GATE-92-01。
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__ = [
    "Alpha87Error",
    "DEGRADED_FORMULAS",
    "EXCLUDED_IDS",
    "WQ_ALPHA_87_IDS",
    "WqAlpha87",
    "ops",
]

# 101 中剔除的 14 个（IndNeutralize 行业数据或 cap 市值真源依赖，超出
# "仅 OHLCV/成交额免费数据"约束；对齐知名开源实现 87 集口径）
EXCLUDED_IDS: tuple[int, ...] = (48, 56, 58, 59, 63, 67, 69, 70, 76, 80, 82, 90, 96, 100)

WQ_ALPHA_87_IDS: tuple[int, ...] = tuple(i for i in range(1, 102) if i not in EXCLUDED_IDS)

# 保留集中含 IndNeutralize 的 5 个：降级为全市场截面 demean，显式标注
DEGRADED_FORMULAS: tuple[int, ...] = (79, 87, 91, 93, 97)

_REQUIRED_FIELDS = ("open", "high", "low", "close", "volume", "amount")


class Alpha87Error(ZephyrBaseError):
    """87-Alpha 库调用失败（错误码未登，纪律⑦留错误码对账批）。"""


# ---------------------------------------------------------------------------
# ts 算子集（panel：index=date, columns=symbol）
# ---------------------------------------------------------------------------


def _w(window: float) -> int:
    """论文浮点窗口取整（最小 1）。"""
    return max(1, int(round(window)))


class ops:  # noqa: N801 — 算子命名空间按业界惯例小写
    """WorldQuant 101 时序/截面算子集（全部 rolling/shift 实现，天然 PIT）。"""

    @staticmethod
    def rank(df: pd.DataFrame) -> pd.DataFrame:
        """截面百分位排名（axis=1）。"""
        return df.rank(axis=1, pct=True)

    @staticmethod
    def delay(df: pd.DataFrame, d: float) -> pd.DataFrame:
        return df.shift(_w(d))

    @staticmethod
    def delta(df: pd.DataFrame, d: float) -> pd.DataFrame:
        return df - df.shift(_w(d))

    @staticmethod
    def ts_sum(df: pd.DataFrame, d: float) -> pd.DataFrame:
        return df.rolling(_w(d), min_periods=_w(d)).sum()

    @staticmethod
    def ts_mean(df: pd.DataFrame, d: float) -> pd.DataFrame:
        return df.rolling(_w(d), min_periods=_w(d)).mean()

    @staticmethod
    def ts_min(df: pd.DataFrame, d: float) -> pd.DataFrame:
        return df.rolling(_w(d), min_periods=_w(d)).min()

    @staticmethod
    def ts_max(df: pd.DataFrame, d: float) -> pd.DataFrame:
        return df.rolling(_w(d), min_periods=_w(d)).max()

    @staticmethod
    def ts_argmax(df: pd.DataFrame, d: float) -> pd.DataFrame:
        w = _w(d)
        return df.rolling(w, min_periods=w).apply(
            lambda x: float(np.argmax(x)) + 1.0 if np.isfinite(x).all() else np.nan, raw=True
        )

    @staticmethod
    def ts_argmin(df: pd.DataFrame, d: float) -> pd.DataFrame:
        w = _w(d)
        return df.rolling(w, min_periods=w).apply(
            lambda x: float(np.argmin(x)) + 1.0 if np.isfinite(x).all() else np.nan, raw=True
        )

    @staticmethod
    def ts_rank(df: pd.DataFrame, d: float) -> pd.DataFrame:
        w = _w(d)
        return df.rolling(w, min_periods=w).apply(
            lambda x: (pd.Series(x).rank(pct=True).iloc[-1] if np.isfinite(x).all() else np.nan),
            raw=True,
        )

    @staticmethod
    def ts_product(df: pd.DataFrame, d: float) -> pd.DataFrame:
        w = _w(d)
        return df.rolling(w, min_periods=w).apply(
            lambda x: float(np.prod(x)) if np.isfinite(x).all() else np.nan, raw=True
        )

    @staticmethod
    def stddev(df: pd.DataFrame, d: float) -> pd.DataFrame:
        return df.rolling(_w(d), min_periods=_w(d)).std()

    @staticmethod
    def correlation(a: pd.DataFrame, b: pd.DataFrame, d: float) -> pd.DataFrame:
        w = _w(d)
        # 窗内零方差产生的 inf 归一为 NaN（下游 rolling 链以 isfinite 判定）
        return a.rolling(w, min_periods=w).corr(b).replace([np.inf, -np.inf], np.nan)

    @staticmethod
    def covariance(a: pd.DataFrame, b: pd.DataFrame, d: float) -> pd.DataFrame:
        w = _w(d)
        return a.rolling(w, min_periods=w).cov(b).replace([np.inf, -np.inf], np.nan)

    @staticmethod
    def decay_linear(df: pd.DataFrame, d: float) -> pd.DataFrame:
        w = _w(d)
        weights = np.arange(1, w + 1, dtype=float)
        weights /= weights.sum()
        return df.rolling(w, min_periods=w).apply(
            lambda x: float(np.dot(x, weights)) if np.isfinite(x).all() else np.nan, raw=True
        )

    @staticmethod
    def scale(df: pd.DataFrame, k: float = 1.0) -> pd.DataFrame:
        return df.mul(k).div(df.abs().sum(axis=1).replace(0.0, np.nan), axis=0)

    @staticmethod
    def sign(df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(np.sign)

    @staticmethod
    def signed_power(df: pd.DataFrame, p: Any) -> pd.DataFrame:
        return np.sign(df) * df.abs() ** p

    @staticmethod
    def adv(volume: pd.DataFrame, d: float) -> pd.DataFrame:
        """平均日成交量（adv{d}）。"""
        return volume.rolling(_w(d), min_periods=_w(d)).mean()

    @staticmethod
    def log(df: pd.DataFrame) -> pd.DataFrame:
        return np.log(df.where(df > 0))

    @staticmethod
    def ind_neutralize_proxy(df: pd.DataFrame) -> pd.DataFrame:
        """IndNeutralize 降级：全市场截面 demean（DEGRADED_FORMULAS 专用）。"""
        return df.sub(df.mean(axis=1), axis=0)


def _where(cond: pd.DataFrame, a: Any, b: Any) -> pd.DataFrame:
    if isinstance(a, pd.DataFrame):
        return a.where(cond, b)
    if isinstance(b, pd.DataFrame):
        return b.where(~cond, a)
    return pd.DataFrame(np.where(cond, a, b), index=cond.index, columns=cond.columns)


def _df_min(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    return a.where(a <= b, b)


def _df_max(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    return a.where(a >= b, b)


def _boolf(df: pd.DataFrame) -> pd.DataFrame:
    return df.astype(float)


# ---------------------------------------------------------------------------
# 87 个 Alpha 公式（d = prepare() 产出的数据 dict）
# ---------------------------------------------------------------------------


def _alpha_001(d):
    cond = d["returns"] < 0
    base = ops.stddev(d["returns"], 20).where(cond, d["close"])
    return ops.rank(ops.ts_argmax(ops.signed_power(base, 2.0), 5)) - 0.5


def _alpha_002(d):
    return -ops.correlation(ops.rank(ops.delta(ops.log(d["volume"]), 2)), ops.rank((d["close"] - d["open"]) / d["open"]), 6)


def _alpha_003(d):
    return -ops.correlation(ops.rank(d["open"]), ops.rank(d["volume"]), 10)


def _alpha_004(d):
    return -ops.ts_rank(ops.rank(d["low"]), 9)


def _alpha_005(d):
    return ops.rank(d["open"] - ops.ts_mean(d["vwap"], 10)) * (-abs(ops.rank(d["close"] - d["vwap"])))


def _alpha_006(d):
    return -ops.correlation(d["open"], d["volume"], 10)


def _alpha_007(d):
    neg_side = (-ops.ts_rank(abs(ops.delta(d["close"], 7)), 60)) * ops.sign(ops.delta(d["close"], 7))
    return _where(d["adv20"] < d["volume"], neg_side, -1.0)


def _alpha_008(d):
    s = ops.ts_sum(d["open"], 5) * ops.ts_sum(d["returns"], 5)
    return -ops.rank(s - ops.delay(s, 10))


def _alpha_009(d):
    dc = ops.delta(d["close"], 1)
    return _where(0 < ops.ts_min(dc, 5), dc, _where(ops.ts_max(dc, 5) < 0, dc, -dc))


def _alpha_010(d):
    dc = ops.delta(d["close"], 1)
    return ops.rank(_where(0 < ops.ts_min(dc, 4), dc, _where(ops.ts_max(dc, 4) < 0, dc, -dc)))


def _alpha_011(d):
    diff = d["vwap"] - d["close"]
    return (ops.rank(ops.ts_max(diff, 3)) + ops.rank(ops.ts_min(diff, 3))) * ops.rank(ops.delta(d["volume"], 3))


def _alpha_012(d):
    return ops.sign(ops.delta(d["volume"], 1)) * (-ops.delta(d["close"], 1))


def _alpha_013(d):
    return -ops.rank(ops.covariance(ops.rank(d["close"]), ops.rank(d["volume"]), 5))


def _alpha_014(d):
    return (-ops.rank(ops.delta(d["returns"], 3))) * ops.correlation(d["open"], d["volume"], 10)


def _alpha_015(d):
    return -ops.ts_sum(ops.rank(ops.correlation(ops.rank(d["high"]), ops.rank(d["volume"]), 3)), 3)


def _alpha_016(d):
    return -ops.rank(ops.covariance(ops.rank(d["high"]), ops.rank(d["volume"]), 5))


def _alpha_017(d):
    return ((-ops.rank(ops.ts_rank(d["close"], 10))) * ops.rank(ops.delta(ops.delta(d["close"], 1), 1))) * ops.rank(ops.ts_rank(d["volume"] / d["adv20"], 5))


def _alpha_018(d):
    return -ops.rank(ops.stddev(abs(d["close"] - d["open"]), 5) + (d["close"] - d["open"]) + ops.correlation(d["close"], d["open"], 10))


def _alpha_019(d):
    return (-ops.sign((d["close"] - ops.delay(d["close"], 7)) + ops.delta(d["close"], 7))) * (1 + ops.rank(1 + ops.ts_sum(d["returns"], 250)))


def _alpha_020(d):
    return ((-ops.rank(d["open"] - ops.delay(d["high"], 1))) * ops.rank(d["open"] - ops.delay(d["close"], 1))) * ops.rank(d["open"] - ops.delay(d["low"], 1))


def _alpha_021(d):
    m8, m2, sd8 = ops.ts_mean(d["close"], 8), ops.ts_mean(d["close"], 2), ops.stddev(d["close"], 8)
    return _where(m8 + sd8 < m2, -1.0, _where(m2 < m8 - sd8, 1.0, _where(d["volume"] / d["adv20"] >= 1, 1.0, -1.0)))


def _alpha_022(d):
    return (-ops.delta(ops.correlation(d["high"], d["volume"], 5), 5)) * ops.rank(ops.stddev(d["close"], 20))


def _alpha_023(d):
    return _where(ops.ts_mean(d["high"], 20) < d["high"], -ops.delta(d["high"], 2), 0.0)


def _alpha_024(d):
    cond = ops.delta(ops.ts_mean(d["close"], 100), 100) / ops.delay(d["close"], 100) <= 0.05
    return _where(cond, -(d["close"] - ops.ts_min(d["close"], 100)), -ops.delta(d["close"], 3))


def _alpha_025(d):
    return ops.rank((((-d["returns"]) * d["adv20"]) * d["vwap"]) * (d["high"] - d["close"]))


def _alpha_026(d):
    return -ops.ts_max(ops.correlation(ops.ts_rank(d["volume"], 5), ops.ts_rank(d["high"], 5), 5), 3)


def _alpha_027(d):
    cond = 0.5 < ops.rank(ops.ts_sum(ops.correlation(ops.rank(d["volume"]), ops.rank(d["vwap"]), 6), 2) / 2.0)
    return _where(cond, -1.0, 1.0)


def _alpha_028(d):
    return ops.scale(ops.correlation(d["adv20"], d["low"], 5) + ((d["high"] + d["low"]) / 2) - d["close"])


def _alpha_029(d):
    inner = ops.rank(ops.rank(ops.scale(ops.log(ops.ts_sum(ops.ts_min(ops.rank(ops.rank(-ops.rank(ops.delta(d["close"] - 1, 5)))), 2), 1)))))
    return ops.ts_min(inner, 5) + ops.ts_rank(ops.delay(-d["returns"], 6), 5)


def _alpha_030(d):
    signs = ops.sign(d["close"] - ops.delay(d["close"], 1)) + ops.sign(ops.delay(d["close"], 1) - ops.delay(d["close"], 2)) + ops.sign(ops.delay(d["close"], 2) - ops.delay(d["close"], 3))
    return ((1.0 - ops.rank(signs)) * ops.ts_sum(d["volume"], 5)) / ops.ts_sum(d["volume"], 20)


def _alpha_031(d):
    return (ops.rank(ops.rank(ops.rank(ops.decay_linear(-ops.rank(ops.rank(ops.delta(d["close"], 10))), 10)))) + ops.rank(-ops.delta(d["close"], 3))) + ops.sign(ops.scale(ops.correlation(d["adv20"], d["low"], 12)))


def _alpha_032(d):
    return ops.scale(ops.ts_mean(d["close"], 7) - d["close"]) + (20 * ops.scale(ops.correlation(d["vwap"], ops.delay(d["close"], 5), 230)))


def _alpha_033(d):
    return ops.rank(-(1 - (d["open"] / d["close"])))


def _alpha_034(d):
    return ops.rank((1 - ops.rank(ops.stddev(d["returns"], 2) / ops.stddev(d["returns"], 5))) + (1 - ops.rank(ops.delta(d["close"], 1))))


def _alpha_035(d):
    return (ops.ts_rank(d["volume"], 32) * (1 - ops.ts_rank((d["close"] + d["high"]) - d["low"], 16))) * (1 - ops.ts_rank(d["returns"], 32))


def _alpha_036(d):
    return (((((2.21 * ops.rank(ops.correlation(d["close"] - d["open"], ops.delay(d["volume"], 1), 15))) + (0.7 * ops.rank(d["open"] - d["close"]))) + (0.73 * ops.rank(ops.ts_rank(ops.delay(-d["returns"], 6), 5)))) + ops.rank(abs(ops.correlation(d["vwap"], d["adv20"], 6)))) + (0.6 * ops.rank((ops.ts_mean(d["close"], 200) - d["open"]) * (d["close"] - d["open"]))))


def _alpha_037(d):
    return ops.rank(ops.correlation(ops.delay(d["open"] - d["close"], 1), d["close"], 200)) + ops.rank(d["open"] - d["close"])


def _alpha_038(d):
    return (-ops.rank(ops.ts_rank(d["close"], 10))) * ops.rank(d["close"] / d["open"])


def _alpha_039(d):
    return ((-ops.rank(ops.delta(d["close"], 7) * (1 - ops.rank(ops.decay_linear(d["volume"] / d["adv20"], 9))))) * (1 + ops.rank(ops.ts_sum(d["returns"], 250))))


def _alpha_040(d):
    return (-ops.rank(ops.stddev(d["high"], 10))) * ops.correlation(d["high"], d["volume"], 10)


def _alpha_041(d):
    return (d["high"] * d["low"]) ** 0.5 - d["vwap"]


def _alpha_042(d):
    return ops.rank(d["vwap"] - d["close"]) / ops.rank(d["vwap"] + d["close"])


def _alpha_043(d):
    return ops.ts_rank(d["volume"] / d["adv20"], 20) * ops.ts_rank(-ops.delta(d["close"], 7), 8)


def _alpha_044(d):
    return -ops.correlation(d["high"], ops.rank(d["volume"]), 5)


def _alpha_045(d):
    return -(ops.rank(ops.ts_mean(ops.delay(d["close"], 5), 20)) * ops.correlation(d["close"], d["volume"], 2) * ops.rank(ops.correlation(ops.ts_sum(d["close"], 5), ops.ts_sum(d["close"], 20), 2)))


def _alpha_046(d):
    expr = ((ops.delay(d["close"], 20) - ops.delay(d["close"], 10)) / 10) - ((ops.delay(d["close"], 10) - d["close"]) / 10)
    return _where(0.25 < expr, -1.0, _where(expr < 0, 1.0, -(d["close"] - ops.delay(d["close"], 1))))


def _alpha_047(d):
    return (((ops.rank(1 / d["close"]) * d["volume"]) / d["adv20"]) * ((d["high"] * ops.rank(d["high"] - d["close"])) / ops.ts_mean(d["high"], 5))) - ops.rank(d["vwap"] - ops.delay(d["vwap"], 5))


def _alpha_049(d):
    expr = ((ops.delay(d["close"], 20) - ops.delay(d["close"], 10)) / 10) - ((ops.delay(d["close"], 10) - d["close"]) / 10)
    return _where(expr < -0.1, 1.0, -(d["close"] - ops.delay(d["close"], 1)))


def _alpha_050(d):
    return -ops.ts_max(ops.rank(ops.correlation(ops.rank(d["volume"]), ops.rank(d["vwap"]), 5)), 5)


def _alpha_051(d):
    expr = ((ops.delay(d["close"], 20) - ops.delay(d["close"], 10)) / 10) - ((ops.delay(d["close"], 10) - d["close"]) / 10)
    return _where(expr < -0.05, 1.0, -(d["close"] - ops.delay(d["close"], 1)))


def _alpha_052(d):
    return (((-ops.ts_min(d["low"], 5)) + ops.delay(ops.ts_min(d["low"], 5), 5)) * ops.rank((ops.ts_sum(d["returns"], 240) - ops.ts_sum(d["returns"], 20)) / 220)) * ops.ts_rank(d["volume"], 5)


def _alpha_053(d):
    return -ops.delta((((d["close"] - d["low"]) - (d["high"] - d["close"])) / (d["close"] - d["low"])), 9)


def _alpha_054(d):
    return (-((d["low"] - d["close"]) * (d["open"] ** 5))) / ((d["low"] - d["high"]) * (d["close"] ** 5))


def _alpha_055(d):
    return -ops.correlation(ops.rank((d["close"] - ops.ts_min(d["low"], 12)) / (ops.ts_max(d["high"], 12) - ops.ts_min(d["low"], 12))), ops.rank(d["volume"]), 6)


def _alpha_057(d):
    return -(d["close"] - d["vwap"]) / ops.decay_linear(ops.rank(ops.ts_argmax(d["close"], 30)), 2)


def _alpha_060(d):
    return -(2 * ops.scale(ops.rank((((d["close"] - d["low"]) - (d["high"] - d["close"])) / (d["high"] - d["low"])) * d["volume"])) - ops.scale(ops.rank(ops.ts_argmax(d["close"], 10))))


def _alpha_061(d):
    return _boolf(ops.rank(d["vwap"] - ops.ts_min(d["vwap"], 16.1219)) < ops.rank(ops.correlation(d["vwap"], d["adv180"], 17.9282)))


def _alpha_062(d):
    inner_cmp = _boolf((ops.rank(d["open"]) + ops.rank(d["open"])) < (ops.rank((d["high"] + d["low"]) / 2) + ops.rank(d["high"])))
    return _boolf(ops.rank(ops.correlation(d["vwap"], ops.ts_sum(d["adv20"], 22.4101), 9.91009)) < ops.rank(inner_cmp)) * -1


def _alpha_064(d):
    mix1 = (d["open"] * 0.178404) + (d["low"] * (1 - 0.178404))
    mix2 = (((d["high"] + d["low"]) / 2) * 0.178404) + (d["vwap"] * (1 - 0.178404))
    return _boolf(ops.rank(ops.correlation(ops.ts_sum(mix1, 12.7054), ops.ts_sum(d["adv120"], 12.7054), 16.6208)) < ops.rank(ops.delta(mix2, 3.69741))) * -1


def _alpha_065(d):
    mix = (d["open"] * 0.00817205) + (d["vwap"] * (1 - 0.00817205))
    return _boolf(ops.rank(ops.correlation(mix, ops.ts_sum(d["adv60"], 8.6911), 6.40374)) < ops.rank(d["open"] - ops.ts_min(d["open"], 14.2415))) * -1


def _alpha_066(d):
    leg1 = ops.rank(ops.decay_linear(ops.delta(d["vwap"], 3.51013), 7.23052))
    mix = ((d["low"] * 0.96633) + (d["low"] * (1 - 0.96633)))
    leg2 = ops.ts_rank(ops.decay_linear((mix - d["vwap"]) / (d["open"] - ((d["high"] + d["low"]) / 2)), 11.4157), 6.72611)
    return (leg1 + leg2) * -1


def _alpha_068(d):
    leg = ops.ts_rank(ops.correlation(ops.rank(d["high"]), ops.rank(d["adv15"]), 8.91644), 13.9333)
    mix = (d["close"] * 0.518371) + (d["low"] * (1 - 0.518371))
    return _boolf(leg < ops.rank(ops.delta(mix, 1.06157))) * -1


def _alpha_071(d):
    leg1 = ops.ts_rank(ops.decay_linear(ops.correlation(ops.ts_rank(d["close"], 3.43976), ops.ts_rank(d["adv180"], 12.0647), 18.0175), 4.20501), 15.6948)
    leg2 = ops.ts_rank(ops.decay_linear(ops.rank((d["low"] + d["open"]) - (d["vwap"] + d["vwap"])) ** 2, 16.4662), 4.4388)
    return _df_max(leg1, leg2)


def _alpha_072(d):
    num = ops.rank(ops.decay_linear(ops.correlation((d["high"] + d["low"]) / 2, d["adv40"], 8.93345), 10.1519))
    den = ops.rank(ops.correlation(ops.ts_rank((d["high"] + d["low"]) / 2, 3.72469), ops.ts_rank(d["volume"], 18.5188), 6.86671))
    return num / den


def _alpha_073(d):
    mix = (d["open"] * 0.147155) + (d["low"] * (1 - 0.147155))
    leg1 = ops.rank(ops.decay_linear(ops.delta(d["vwap"], 4.72775), 2.91864))
    leg2 = ops.ts_rank(ops.decay_linear(-(ops.delta(mix, 2.03608) / mix), 3.33829), 16.7411)
    return _df_max(leg1, leg2) * -1


def _alpha_074(d):
    leg1 = ops.rank(ops.correlation(d["close"], ops.ts_sum(d["adv30"], 37.4843), 15.1365))
    mix = (d["high"] * 0.0261661) + (d["vwap"] * (1 - 0.0261661))
    leg2 = ops.rank(ops.correlation(ops.rank(mix), ops.rank(d["volume"]), 11.4791))
    return _boolf(leg1 < leg2) * -1


def _alpha_075(d):
    return _boolf(ops.rank(ops.correlation(d["vwap"], d["volume"], 4.24304)) < ops.rank(ops.correlation(ops.rank(d["low"]), ops.rank(d["adv50"]), 12.4413)))


def _alpha_077(d):
    leg1 = ops.rank(ops.decay_linear((((d["high"] + d["low"]) / 2) + d["high"]) - (d["vwap"] + d["high"]), 20.0451))
    leg2 = ops.rank(ops.decay_linear(ops.correlation((d["high"] + d["low"]) / 2, d["adv40"], 3.1614), 5.64125))
    return _df_min(leg1, leg2)


def _alpha_078(d):
    mix = ((d["low"] * 0.352233) + (d["vwap"] * (1 - 0.352233))) * d["volume"]
    leg1 = ops.rank(ops.correlation(ops.ts_sum(mix, 19.7428), ops.ts_sum(d["adv40"], 19.7428), 6.83313))
    leg2 = ops.rank(ops.correlation(ops.rank(d["vwap"]), ops.rank(d["volume"]), 5.77492))
    return leg1 ** leg2


def _alpha_079(d):  # DEGRADED：IndNeutralize 降级全市场 demean
    mix = ops.ind_neutralize_proxy((d["close"] * 0.60733) + (d["open"] * (1 - 0.60733)))
    leg1 = ops.rank(ops.delta(mix, 1.23438))
    leg2 = ops.rank(ops.correlation(ops.ts_rank(d["vwap"], 3.60973), ops.ts_rank(d["adv150"], 9.18637), 14.6644))
    return _boolf(leg1 < leg2)


def _alpha_081(d):
    inner = ops.rank(ops.rank(ops.correlation(d["vwap"], ops.ts_sum(d["adv10"], 49.6054), 8.47743))) ** 4
    leg1 = ops.rank(ops.log(ops.ts_product(inner, 14.9655)))
    leg2 = ops.rank(ops.correlation(ops.rank(d["vwap"]), ops.rank(d["volume"]), 5.07914))
    return _boolf(leg1 < leg2) * -1


def _alpha_083(d):
    atr = (d["high"] - d["low"]) / ops.ts_mean(d["close"], 5)
    return (ops.rank(ops.delay(atr, 2)) * ops.rank(ops.rank(d["volume"]))) / (atr / (d["vwap"] - d["close"]))


def _alpha_084(d):
    return ops.signed_power(ops.ts_rank(d["vwap"] - ops.ts_max(d["vwap"], 15.3217), 20.7127), ops.delta(d["close"], 4.96796))


def _alpha_085(d):
    mix = (d["high"] * 0.876703) + (d["close"] * (1 - 0.876703))
    leg1 = ops.rank(ops.correlation(mix, d["adv30"], 9.61331))
    leg2 = ops.rank(ops.correlation(ops.ts_rank((d["high"] + d["low"]) / 2, 3.70596), ops.ts_rank(d["volume"], 10.1595), 7.11408))
    return leg1 ** leg2


def _alpha_086(d):
    leg1 = ops.ts_rank(ops.correlation(d["close"], ops.ts_sum(d["adv20"], 14.7444), 6.00049), 20.4195)
    leg2 = ops.rank((d["open"] + d["close"]) - (d["vwap"] + d["open"]))
    return _boolf(leg1 < leg2) * -1


def _alpha_087(d):  # DEGRADED：IndNeutralize 降级全市场 demean
    mix = (d["close"] * 0.369701) + (d["vwap"] * (1 - 0.369701))
    leg1 = ops.rank(ops.decay_linear(ops.delta(mix, 1.91233), 2.65461))
    leg2 = ops.ts_rank(ops.decay_linear(abs(ops.correlation(ops.ind_neutralize_proxy(d["adv81"]), d["close"], 13.4132)), 4.89768), 14.4535)
    return _df_max(leg1, leg2) * -1


def _alpha_088(d):
    leg1 = ops.rank(ops.decay_linear((ops.rank(d["open"]) + ops.rank(d["low"])) - (ops.rank(d["high"]) + ops.rank(d["close"])), 8.06882))
    leg2 = ops.ts_rank(ops.decay_linear(ops.correlation(ops.ts_rank(d["close"], 8.44728), ops.ts_rank(d["adv60"], 20.6966), 8.01266), 6.65053), 2.61957)
    return _df_min(leg1, leg2)


def _alpha_089(d):
    mix = (d["low"] * 0.967285) + (d["low"] * (1 - 0.967285))
    leg1 = ops.rank(ops.correlation(mix, d["adv10"], 6.94279))
    leg2 = ops.rank(ops.correlation(ops.ts_rank(d["vwap"], 5.41607), ops.ts_rank(d["volume"], 11.1839), 3.23082))
    return leg1 ** leg2


def _alpha_091(d):  # DEGRADED：IndNeutralize 降级全市场 demean
    leg1 = ops.ts_rank(ops.decay_linear(ops.decay_linear(ops.correlation(ops.ind_neutralize_proxy(d["close"]), d["volume"], 9.74928), 16.398), 3.90631), 15.225)
    mix = (d["high"] * 0.156179) + (d["low"] * (1 - 0.156179))
    leg2 = ops.ts_rank(ops.decay_linear(ops.correlation(ops.rank(mix), ops.rank(d["adv30"]), 4.40754), 6.00313), 11.8984)
    return (leg1 - leg2) * -1


def _alpha_092(d):
    cond = _boolf((((d["high"] + d["low"]) / 2) + d["close"]) < (d["low"] + d["open"]))
    leg1 = ops.ts_rank(ops.decay_linear(cond, 14.7221), 18.4617)
    leg2 = ops.ts_rank(ops.decay_linear(ops.correlation(ops.rank(d["low"]), ops.rank(d["adv30"]), 7.58555), 6.94024), 6.80584)
    return _df_min(leg1, leg2)


def _alpha_093(d):  # DEGRADED：IndNeutralize 降级全市场 demean
    leg1 = ops.ts_rank(ops.decay_linear(ops.correlation(ops.ind_neutralize_proxy(d["vwap"]), d["adv81"], 17.4193), 19.848), 7.54455)
    mix = (d["close"] * 0.524434) + (d["vwap"] * (1 - 0.524434))
    leg2 = ops.rank(ops.decay_linear(ops.delta(mix, 2.77377), 16.2664))
    return leg1 / leg2


def _alpha_094(d):
    leg1 = ops.rank(d["vwap"] - ops.ts_min(d["vwap"], 11.5783))
    leg2 = ops.ts_rank(ops.correlation(ops.ts_rank(d["vwap"], 19.6462), ops.ts_rank(d["adv60"], 4.02992), 18.0926), 2.70756)
    return (leg1 ** leg2) * -1


def _alpha_095(d):
    leg1 = ops.rank(d["open"] - ops.ts_min(d["open"], 12.4105))
    corr = ops.rank(ops.correlation(ops.ts_mean((d["high"] + d["low"]) / 2, 19.1351), ops.ts_mean(d["adv40"], 19.1351), 12.8742)) ** 5
    leg2 = ops.ts_rank(corr, 11.7584)
    return _boolf(leg1 < leg2)


def _alpha_097(d):  # DEGRADED：IndNeutralize 降级全市场 demean
    mix = ops.ind_neutralize_proxy((d["low"] * 0.721001) + (d["vwap"] * (1 - 0.721001)))
    leg1 = ops.rank(ops.decay_linear(ops.delta(mix, 3.3705), 20.4523))
    leg2 = ops.ts_rank(ops.decay_linear(ops.ts_rank(ops.correlation(ops.ts_rank(d["low"], 7.87871), ops.ts_rank(d["adv60"], 17.255), 4.97547), 18.5925), 15.7152), 6.71659)
    return leg1 - leg2


def _alpha_098(d):
    leg1 = ops.rank(ops.decay_linear(ops.correlation(d["vwap"], ops.ts_sum(d["adv5"], 26.4719), 4.58418), 7.18088))
    leg2 = ops.rank(ops.decay_linear(ops.ts_rank(ops.ts_argmin(ops.correlation(ops.rank(d["open"]), ops.rank(d["adv15"]), 20.8187), 8.62571), 6.95668), 8.07206))
    return leg1 - leg2


def _alpha_099(d):
    leg1 = ops.rank(ops.correlation(ops.ts_mean((d["high"] + d["low"]) / 2, 19.8975), ops.ts_mean(d["adv60"], 19.8975), 8.8136))
    leg2 = ops.rank(ops.correlation(d["low"], d["volume"], 6.28259))
    return _boolf(leg1 < leg2) * -1


def _alpha_101(d):
    return (d["close"] - d["open"]) / ((d["high"] - d["low"]) + 0.001)


_ALPHA_IMPL: dict[int, Callable[[Mapping[str, pd.DataFrame]], pd.DataFrame]] = {
    1: _alpha_001, 2: _alpha_002, 3: _alpha_003, 4: _alpha_004, 5: _alpha_005,
    6: _alpha_006, 7: _alpha_007, 8: _alpha_008, 9: _alpha_009, 10: _alpha_010,
    11: _alpha_011, 12: _alpha_012, 13: _alpha_013, 14: _alpha_014, 15: _alpha_015,
    16: _alpha_016, 17: _alpha_017, 18: _alpha_018, 19: _alpha_019, 20: _alpha_020,
    21: _alpha_021, 22: _alpha_022, 23: _alpha_023, 24: _alpha_024, 25: _alpha_025,
    26: _alpha_026, 27: _alpha_027, 28: _alpha_028, 29: _alpha_029, 30: _alpha_030,
    31: _alpha_031, 32: _alpha_032, 33: _alpha_033, 34: _alpha_034, 35: _alpha_035,
    36: _alpha_036, 37: _alpha_037, 38: _alpha_038, 39: _alpha_039, 40: _alpha_040,
    41: _alpha_041, 42: _alpha_042, 43: _alpha_043, 44: _alpha_044, 45: _alpha_045,
    46: _alpha_046, 47: _alpha_047, 49: _alpha_049, 50: _alpha_050, 51: _alpha_051,
    52: _alpha_052, 53: _alpha_053, 54: _alpha_054, 55: _alpha_055, 57: _alpha_057,
    60: _alpha_060, 61: _alpha_061, 62: _alpha_062, 64: _alpha_064, 65: _alpha_065,
    66: _alpha_066, 68: _alpha_068, 71: _alpha_071, 72: _alpha_072, 73: _alpha_073,
    74: _alpha_074, 75: _alpha_075, 77: _alpha_077, 78: _alpha_078, 79: _alpha_079,
    81: _alpha_081, 83: _alpha_083, 84: _alpha_084, 85: _alpha_085, 86: _alpha_086,
    87: _alpha_087, 88: _alpha_088, 89: _alpha_089, 91: _alpha_091, 92: _alpha_092,
    93: _alpha_093, 94: _alpha_094, 95: _alpha_095, 97: _alpha_097, 98: _alpha_098,
    99: _alpha_099, 101: _alpha_101,
}

assert len(_ALPHA_IMPL) == 87, f"87 公式集漂移: {len(_ALPHA_IMPL)}"
assert set(_ALPHA_IMPL) == set(WQ_ALPHA_87_IDS), "公式实现集与 WQ_ALPHA_87_IDS 不一致"


class WqAlpha87:
    """WorldQuant 101 精选 87 Alpha 公式库门面。

    用法::

        lib = WqAlpha87()
        values = lib.compute(101, {"open": df_o, "high": df_h, "low": df_l,
                                   "close": df_c, "volume": df_v, "amount": df_a})
        lib.register_all(register_hook)            # 入因子注册（装配批接 FactorRegistry）
        lib.validate_ic(101, data, ic_hook)        # 逐个 IC/IR 验证（接 ic_ir_calc）
    """

    def list_alphas(self) -> tuple[int, ...]:
        """87 个可用公式编号。"""
        return WQ_ALPHA_87_IDS

    def is_degraded_formula(self, alpha_id: int) -> bool:
        """是否为 IndNeutralize 降级公式（全市场 demean 近似）。"""
        return alpha_id in DEGRADED_FORMULAS

    def prepare(self, data: Mapping[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """数据准备：必需字段校验 + vwap/returns/cap/adv{d} 派生（仅 OHLCV/成交额）。"""
        missing = [f for f in _REQUIRED_FIELDS if f not in data]
        if missing:
            raise Alpha87Error(f"缺必需数据字段: {missing}（需 open/high/low/close/volume/amount）")
        out = dict(data)
        if "vwap" not in out:
            out["vwap"] = out["amount"] / out["volume"].replace(0.0, np.nan)
        if "returns" not in out:
            out["returns"] = out["close"].pct_change()
        if "cap" not in out:
            out["cap"] = out["close"] * out["volume"]  # 代理口径（保留集无 cap 公式，仅供扩展）
        for w in (5, 10, 15, 20, 30, 40, 50, 60, 81, 120, 150, 180):
            out[f"adv{w}"] = ops.adv(out["volume"], w)
        return out

    def compute(self, alpha_id: int, data: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
        """计算指定 Alpha 公式，输出 panel（index=date, columns=symbol）。"""
        impl = _ALPHA_IMPL.get(alpha_id)
        if impl is None:
            if alpha_id in EXCLUDED_IDS:
                raise Alpha87Error(
                    f"alpha#{alpha_id} 在 101 剔除集（IndNeutralize/cap 外部数据依赖，"
                    f"EXCLUDED_IDS 留档）；可用 87 集见 list_alphas()"
                )
            raise Alpha87Error(f"未知 alpha 编号: {alpha_id!r}（合法范围 1..101 剔除 14）")
        prepared = self.prepare(data)
        result = impl(prepared)
        if not isinstance(result, pd.DataFrame):
            result = pd.DataFrame(result, index=prepared["close"].index, columns=prepared["close"].columns)
        return result

    def register_all(self, register_hook: Callable[[str, int], Any]) -> int:
        """87 个公式逐个入因子注册（register_hook 委托 FactorRegistry/feature_store）。

        Returns:
            注册数量（87）。
        """
        if not callable(register_hook):
            raise Alpha87Error("register_hook 必须为可调用对象")
        for alpha_id in WQ_ALPHA_87_IDS:
            register_hook(f"wq_alpha_{alpha_id:03d}", alpha_id)
        return len(WQ_ALPHA_87_IDS)

    def validate_ic(
        self,
        alpha_id: int,
        data: Mapping[str, pd.DataFrame],
        ic_hook: Callable[[str, pd.DataFrame], Any],
    ) -> Any:
        """逐个 IC/IR 验证接入（ic_hook 委托，复用 analysis/ic_ir_calc 语义）。"""
        if not callable(ic_hook):
            raise Alpha87Error("ic_hook 未装配（运行时装配批接 ic_ir_calc/evaluate_factor）")
        values = self.compute(alpha_id, data)
        return ic_hook(f"wq_alpha_{alpha_id:03d}", values)
