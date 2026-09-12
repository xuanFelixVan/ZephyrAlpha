# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.expectations
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas（纯函数核，无 IO）
# [CONSUMERS] （C2 起接 factor/analysis 分层回测与 multifactor_pit_backtest；登记 factor_registry=待办）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 全函数纯无 IO；禁止前视——输入必须已是 PIT 正确（一致预期消费 consensus_daily(DS-229)，其本身只聚合 publish_date<=trade_date）；除法分母零/NaN 一律产 NaN 不产 inf；不缓存不落盘
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入未对齐/空输入→返回 NaN 系列或空（不抛异常，因子评估层负责断言）
# [TESTS] tests/factor/test_expectations.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""expectations — 分析师一致预期因子族（消费端 C2 预备，2026-09-12）。

数据源：c3_fundamental.consensus_daily（DS-229，每股每日×预测目标日历年的一致预期矩阵，
PIT 正确）+ 行情收盘价。六个因子对应设计文档 §M2（docs/_working/2026-09-12-expectation-consumption-design.md），
公式出处=华泰金工系列（单因子测试之九/AI54/基本面量化之二）+ 经典文献，逐函数 docstring 注明。

设计约定：
- 全部纯函数：输入已是 PIT 正确的 Series/DataFrame，输出同型 Series（NaN=无有效值）。
- 单标的用法：index=交易日（升序）；面板用法：MultiIndex(symbol, trade_date)——
  涉及时序移位的函数自动按 symbol 分组（groupby level）。
- 除法分母为 0/NaN → 产 NaN（禁 inf）。
- 因子登记（factor_registry expectations 族）与 SOP-B ④⑤⑥ 评估=后续步骤（排队 P0 后）。
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

__all__ = [
    "exp01_consensus_ep",
    "exp02_revision_momentum",
    "exp03_revision_breadth",
    "exp04_anomaly_coverage",
    "exp05_dispersion",
    "exp06_rating_momentum",
]

# 评级分映射（与 build_consensus_daily.py 一致——单一真源在构建器，此处为只读镜像）
RATING_SCORE_MAP: dict[str, int] = {
    "买入": 7,
    "增持": 5,
    "中性": 3,
    "持有": 3,
    "减持": 2,
    "卖出": 1,
    "回避": 2,
}

# 分歧度下限（防除零：disp < floor 时按 floor 处理）
_DISP_FLOOR = 1e-6


def _safe_div(num: pd.Series, den: pd.Series | float) -> pd.Series:
    """安全除法：分母 0/NaN → NaN（禁 inf）。"""
    den_s = pd.Series(den, index=num.index) if not isinstance(den, pd.Series) else den
    out = num / den_s
    return out.where(den_s.abs() > 0)


def _shift_by_symbol(s: pd.Series, k: int) -> pd.Series:
    """按 symbol 分组的时序移位；单标的（非 MultiIndex）直接 shift。"""
    if isinstance(s.index, pd.MultiIndex) and "symbol" in (s.index.names or []):
        return s.groupby(level="symbol").shift(k)
    return s.shift(k)


# ----------------------------------------------------------------------------
# EXP-01 一致预期 EP（价值类）
# 依据：华泰《单因子测试之一致预期因子》——沪深300 内 RankIC 6.32%（最强一致预期因子）
# ----------------------------------------------------------------------------
def exp01_consensus_ep(eps_consensus_fy1: pd.Series, close: pd.Series) -> pd.Series:
    """一致预期 EP = 窗口一致预期 FY1 EPS / 收盘价。

    Args:
        eps_consensus_fy1: forecast_year=次年的 eps_consensus（PIT 快照）
        close: 同日收盘价（后复权口径与回测一致）

    Returns:
        EP 序列；eps<=0（亏损预期）保留原始负值（华泰口径不截断），close<=0/NaN → NaN。
    """
    ep = _safe_div(eps_consensus_fy1, close)
    return ep.where(eps_consensus_fy1.notna())


# ----------------------------------------------------------------------------
# EXP-02 盈利修正动量（动量类）
# 依据：华泰 AI54——一致预期数据的变化率（ts_return）是最高频因子构件；
#       改进法=除以分析师预测标准差（DEGREE，2020 后离散度抬升的校正）；
#       Gleason & Lee 2003——修正后价格漂移。
# ----------------------------------------------------------------------------
def exp02_revision_momentum(
    eps_consensus: pd.Series,
    eps_std: pd.Series,
    eps_mean: pd.Series,
    k: int = 20,
) -> pd.Series:
    """盈利修正动量 = k 期修正变化率 ÷ 分歧度。

    两步（可拆用）：
      raw = (eps_t - eps_{t-k}) / |eps_{t-k}|          —— 修正变化率（k 交易日）
      adjusted = raw / max(eps_std_t/|eps_mean_t|, floor) —— 分歧度归一（DEGREE 改进）

    Args:
        eps_consensus/eps_std/eps_mean: 同型对齐序列（forecast_year 固定，如 FY1）
        k: 回看交易日数（默认 20≈1 个月）

    Returns:
        修正动量序列；任一环节缺值 → NaN。正值=一致预期上修。
    """
    eps_prev = _shift_by_symbol(eps_consensus, k)
    raw = _safe_div(eps_consensus - eps_prev, eps_prev.abs())
    disp = _safe_div(eps_std, eps_mean.abs()).clip(lower=_DISP_FLOOR)
    return _safe_div(raw, disp)


# ----------------------------------------------------------------------------
# EXP-03 修正广度（Gleason-Lee 上调占比）
# 依据：华泰基本面量化之二——上调占比因子；Gleason & Lee 2003——修正创新性分类
# ----------------------------------------------------------------------------
def exp03_revision_breadth(
    report_eps: pd.DataFrame,
    consensus_daily: pd.Series,
    window_days: int = 63,
) -> pd.Series:
    """修正广度 = 窗口内"上调研报占比"（按发布日滚动的研报级分类）。

    分类（PIT）：单份研报的 EPS 预测 vs **发布时点可见的最新一致预期**
    （consensus_daily 中 publish_date <= report_date 的最近快照——发布日当天快照
    已含当日他报，按华泰同口径可参考）。eps_report > consensus_before → 上调。

    Args:
        report_eps: 研报级预测，columns=[publish_date, forecast_year, eps]
                    （每行=一份研报的一个预测槽位，与 research_report 展开一致）
        consensus_daily: 某一 forecast_year 的每日一致预期序列（index=trade_date）
        window_days: 滚动窗口自然日（默认 63≈一个季度）

    Returns:
        index=发布日（研报自然日网格）的上调占比序列（窗口内研报数=0 的日期为 NaN）。
    """
    df = report_eps.copy()
    df["publish_date"] = pd.to_datetime(df["publish_date"])
    cons = consensus_daily.copy()
    cons.index = pd.to_datetime(cons.index)
    cons = cons.sort_index()

    # as-of 对齐：每份研报取发布日 <= 的最近一致预期（merge_asof，PIT）
    df = df.sort_values("publish_date")
    merged = pd.merge_asof(
        df,
        cons.rename("consensus_before").reset_index().rename(columns={"index": "trade_date"}),
        left_on="publish_date",
        right_on="trade_date",
        direction="backward",
    )
    merged = merged[merged["eps"].notna() & merged["consensus_before"].notna() & (merged["consensus_before"] != 0)]
    if merged.empty:
        return pd.Series(dtype=float)
    # 上调判定：研报预测 > 发布时点可见一致预期（绝对值比较；负预期区间（亏损股）的
    # "改善"语义（-5 → -2）V1 不覆盖，留待 V2 加方向感知口径——留痕）
    merged["is_up"] = merged["eps"] > merged["consensus_before"]
    ser = merged.set_index("publish_date")["is_up"].astype(float)
    # 自然日滚动窗口（研报事件网格）
    breadth = ser.rolling(f"{window_days}D").mean()
    return breadth


# ----------------------------------------------------------------------------
# EXP-04 异常覆盖（关注度，横截面回归残差）
# 依据：Lee & So 2017（异常覆盖度预测收益）；华泰基本面量化之二——
#       研报数/作者数/机构数 对 [市值, 动量, 换手, 机构持仓] 回归取残差（RankIC 2.34%）
# ----------------------------------------------------------------------------
def exp04_anomaly_coverage(
    coverage: pd.Series,
    characteristics: pd.DataFrame,
    use_log_coverage: bool = True,
) -> pd.Series:
    """异常覆盖 = 覆盖度对风格特征横截面回归的残差（单截面版）。

    Args:
        coverage: 截面覆盖度（如过去 63 天研报数/机构数；单标的时序用法=按日重复调用）
        characteristics: 同 index 的特征列（约定列名 log_mv/mom_63/turnover_20，
                         缺列自动跳过；全缺则残差=去均值覆盖度）
        use_log_coverage: 对覆盖度取 log1p 再回归（华泰口径数量级压缩）

    Returns:
        残差序列（index 同 coverage；等价于剥离风格后的"异常关注"）。
    """
    y = coverage.astype(float)
    if use_log_coverage:
        y = y.map(lambda v: float("nan") if pd.isna(v) else math.log1p(max(float(v), 0.0)))
    cols = [c for c in ("log_mv", "mom_63", "turnover_20") if c in characteristics.columns]
    feats = characteristics.reindex(y.index)[cols].astype(float) if cols else pd.DataFrame(index=y.index)
    feats["const"] = 1.0
    data = pd.concat([y.rename("y"), feats], axis=1).dropna()
    if data.empty or len(data) <= feats.shape[1]:
        return pd.Series(float("nan"), index=y.index)
    x_mat = data[feats.columns].to_numpy()
    y_vec = data["y"].to_numpy()
    beta, *_ = np.linalg.lstsq(x_mat, y_vec, rcond=None)
    resid = y_vec - x_mat @ beta
    return pd.Series(resid, index=data.index).reindex(y.index)


# ----------------------------------------------------------------------------
# EXP-05 预测分歧度（情绪/不确定性类，预期负向）
# 依据：Diether, Malloy & Scherbina 2002——高分歧→未来收益偏低；华泰 AI54 DEGREE 调整分母
# ----------------------------------------------------------------------------
def exp05_dispersion(eps_std: pd.Series, eps_mean: pd.Series) -> pd.Series:
    """分歧度 = eps_std / |eps_mean|（变异系数口径）。

    注意方向：文献口径为**负向因子**（分歧越大未来收益越低），使用时按低多空或取负。
    """
    return _safe_div(eps_std, eps_mean.abs()).where(eps_mean.abs() > _DISP_FLOOR)


# ----------------------------------------------------------------------------
# EXP-06 评级动量（情绪类）
# 依据：华泰基本面量化之二——评级分 7/5/3/2/1/0 映射 + 3 个月均值；Jegadeesh et al. 2002
# ----------------------------------------------------------------------------
def exp06_rating_momentum(rating_score_mean: pd.Series, k: int = 60) -> pd.Series:
    """评级动量 = 评级分均值 k 交易日变化（正值=评级系统性上移）。

    原始评级均值本身是弱因子（卖方乐观偏置：买入+增持占 91%，见 DS-228 evidence），
    **变化量**剥掉横截面乐观水平，保留边际信息。
    """
    prev = _shift_by_symbol(rating_score_mean, k)
    return rating_score_mean - prev
