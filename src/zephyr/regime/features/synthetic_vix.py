# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.9 Phase2c
# [MODULE] zephyr.regime.features.synthetic_vix
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] MOD-REGIME-002(OverlaySignalsConstructor消费vix_pct→S1 vix_panic/S2 vix)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] vix_pct∈[0,1]; 数据缺失返回空Series(调用方回退vol_pct); PIT由调用方shift(1)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_synthetic_vix.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.9 #MOD-REGIME-002 #Phase2c
"""
合成 VIX（CBOE 简化版，50ETF+300ETF 双标的均值）（MOD-REGIME-002 Phase 2c）。

利用 50ETF(510050)+300ETF(510300) 期权隐含波动率曲面，按 CBOE VIX 简化公式
计算中国版恐慌指数，替代 MVP 的 vol_pct（实现波动率分位）代理。

CBOE VIX 简化公式：
    1. 筛 ATM 附近（|delta-0.5|<0.15，call+put 平均）
    2. 取近月（DTE≤30）+ 次月（DTE>30）IV 均值
    3. 线性插值到 30 天：σ_30 = iv1 + (iv2-iv1)×(30-t1)/(t2-t1)
    4. VIX = σ_30 × 100（百分数）
    5. 双标的取均值 VIX = (VIX_50 + VIX_300) / 2
    6. vix_pct = VIX.rolling(250).rank(pct=True) → [0,1]（与 vol_pct 接口一致）

设计原则：
  - **接口兼容**：vix_pct ∈ [0,1]，与 vol_pct（实现波动率分位）同构，可无缝替换
    s1_vix_panic_score / s2_vix_score 的输入。
  - **降级友好**：某标的 IV 缺失 → 用单标的；两者都缺 → 返回空 Series（调用方
    回退 vol_pct，C1 不退化）。
  - **PIT 由调用方负责**：本模块纯计算，shift(1) 在 OverlaySignalsConstructor._precompute 统一做。

依据: 10_regime_detector_spec v1.3.1 §4.9 / Phase 2c 计划 §任务4
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: option_iv_df 参数
#   fields: 参数 option_iv_df，类型注解 pd.DataFrame | None
#   code: synthetic_vix.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: vix 参数
#   fields: 参数 vix，类型注解 pd.Series
#   code: synthetic_vix.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: window 参数
#   fields: 参数 window，类型注解 int
#   code: synthetic_vix.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: close 参数
#   fields: 参数 close，类型注解 pd.Series
#   code: synthetic_vix.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① compute_synthetic_vix
#   name_en: compute_synthetic_vix
#   intro: 合成 VIX → VIX 绝对值序列（百分数）。
#   desc: 合成 VIX → VIX 绝对值序列（百分数）。 Parameters ---------- option_iv_df : MultiIndex(trade_date, unde…；源码 L135-L174
#   inputs: option_iv_df
#   outputs: pd.Series
# - id: A2
#   name_zh: ② vix_pct_from_vix
#   name_en: vix_pct_from_vix
#   intro: VIX 历史分位 → [0,1]（与 vol_pct 接口一致，可无缝替换）。
#   desc: VIX 历史分位 → [0,1]（与 vol_pct 接口一致，可无缝替换）。 vix_pct = vix.rolling(window).rank(pct=True) 数据缺失…；源码 L177-L194
#   inputs: vix window
#   outputs: pd.Series
# - id: A3
#   name_zh: ③ synthetic_vix_pct
#   name_en: synthetic_vix_pct
#   intro: 后备合成 VIX 历史分位（downside semi-deviation percentile）∈ [0, 1]。
#   desc: 后备合成 VIX 历史分位（downside semi-deviation percentile）∈ [0, 1]。 期权 IV 曲面缺失时的 P0 后备路径：用**下行半偏差*…；源码 L197-L234
#   inputs: close hv_window pct_window
#   outputs: pd.Series
# 层: 输出
# - id: O1
#   name_zh: pd.Series
#   name_en: pd.Series
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-REGIME-002(OverlaySignalsConstructor消费vix_pct→S1 vix_panic/S2 vix)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["compute_synthetic_vix", "vix_pct_from_vix", "synthetic_vix_pct"]


def _interp_vix_for_date(group: pd.DataFrame) -> float:
    """对单日 ATM 期权数据做近月/次月 IV 线性插值到 30 天。

    Returns VIX 绝对值（小数，未乘 100）。
    """
    if group.empty:
        return np.nan
    near = group[group["dte"] <= 30].sort_values("dte")
    far = group[group["dte"] > 30].sort_values("dte")
    # 近月/次月 IV 均值
    iv_near = near["iv"].mean() if not near.empty else np.nan
    iv_far = far["iv"].mean() if not far.empty else np.nan
    # 只有一个到期日可用 → 直接用该 IV
    if np.isnan(iv_near) and np.isnan(iv_far):
        return np.nan
    if np.isnan(iv_near):
        return float(iv_far)
    if np.isnan(iv_far):
        return float(iv_near)
    t1 = near["dte"].max()  # 近月最大 DTE（最接近30天）
    t2 = far["dte"].min()  # 次月最小 DTE（最接近30天）
    if t2 == t1:
        return float(iv_near)
    # 线性插值到 30 天
    return float(iv_near + (iv_far - iv_near) * (30 - t1) / (t2 - t1))


def compute_synthetic_vix(option_iv_df: pd.DataFrame | None) -> pd.Series:
    """合成 VIX → VIX 绝对值序列（百分数）。

    Parameters
    ----------
    option_iv_df : MultiIndex(trade_date, underlying) DataFrame，含 strike/expiry/iv/
        option_type/delta/vega。None 或空 → 返回空 Series。

    Returns
    -------
    pd.Series(index=trade_date, name="vix")，值为 VIX 绝对值（百分数，如 20.5）。
    双标的（510050+510300）取均值；单标的缺失时用可用的那个。
    """
    if option_iv_df is None or option_iv_df.empty:
        return pd.Series(dtype=float, name="vix")
    df = option_iv_df.reset_index().copy()
    df["expiry"] = pd.to_datetime(df["expiry"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df["dte"] = (df["expiry"] - df["trade_date"]).dt.days
    # ATM 筛选：|delta-0.5|<0.15（call delta 接近 0.5 为 ATM）
    df["delta_abs"] = df["delta"].abs()
    atm = df[(df["delta_abs"] - 0.5).abs() < 0.15].copy()
    if atm.empty:
        return pd.Series(dtype=float, name="vix")
    # 按 underlying 分组计算 VIX
    vix_by_underlying: dict[str, pd.Series] = {}
    for underlying, group in atm.groupby("underlying"):
        vix = group.groupby("trade_date").apply(_interp_vix_for_date, include_groups=False)
        vix = vix.dropna()
        if not vix.empty:
            vix_by_underlying[underlying] = vix
    if not vix_by_underlying:
        return pd.Series(dtype=float, name="vix")
    # 双标的取均值（缺失时用单标的，dropna 后 concat）
    vix_list = list(vix_by_underlying.values())
    if len(vix_list) == 1:
        vix = vix_list[0] * 100  # 转百分数
    else:
        vix = pd.concat(vix_list, axis=1).mean(axis=1) * 100  # 双标的均值
    return vix.dropna().rename("vix")


def vix_pct_from_vix(vix: pd.Series, window: int = 250) -> pd.Series:
    """VIX 历史分位 → [0,1]（与 vol_pct 接口一致，可无缝替换）。

    vix_pct = vix.rolling(window).rank(pct=True)
    数据缺失（空 Series）返回空 Series（调用方按 vol_pct 降级）。

    Parameters
    ----------
    vix : compute_synthetic_vix 返回的 VIX 绝对值序列。
    window : 分位回看窗口（默认 250 日≈1年）。

    Returns
    -------
    pd.Series，值 ∈ [0,1]；空输入返回空 Series。
    """
    if vix is None or vix.empty:
        return pd.Series(dtype=float, name="vix_pct")
    return vix.rolling(window).rank(pct=True).rename("vix_pct")


def synthetic_vix_pct(
    close: pd.Series,
    hv_window: int = 20,
    pct_window: int = 250,
) -> pd.Series:
    """后备合成 VIX 历史分位（downside semi-deviation percentile）∈ [0, 1]。

    期权 IV 曲面缺失时的 P0 后备路径：用**下行半偏差**（只计负收益）的年化值
    在过去 250 日的滚动分位作为恐慌代理。与 realized_vol_pct（上下行均计）互补：

      - **bull 高波期**（急涨急跌但向上）：vol_pct 高，但下行占比小 → vix_pct 低
      - **危机期**（持续大跌）：下行主导 → vix_pct 飙升

    算法：
      1. 对数收益率 r = log(close / close.shift(1))
      2. 下行收益 r_down = min(r, 0)（正收益归 0，只保留负收益的"伤害"）
      3. 下行半方差 = mean(r_down^2) over hv_window
      4. 年化下行波动 = sqrt(下行半方差) × √252
      5. 过去 pct_window 日的滚动分位（pct=True）→ ∈ [0, 1]

    依据：downside deviation（Sortino 分母）是公认的下行风险度量；
    A 股期权数据常缺失，用此作 VIX 代用，危机特异性强于总波动率。

    Parameters
    ----------
    close : 收盘价序列（index=日期）。应为市场代理（如沪深300指数）。
    hv_window : 下行半偏差窗口（默认20日）。
    pct_window : 分位回看窗口（默认250日≈1年）。

    Returns
    -------
    pd.Series，index 同 close，值 ∈ [0, 1]；前 (hv_window+pct_window) 日为 NaN。
    """
    returns = np.log(close / close.shift(1))
    down_returns = returns.clip(upper=0.0)  # 正收益→0，只保留负收益
    downside_var = (down_returns**2).rolling(hv_window).mean()
    downside_vol = np.sqrt(downside_var) * np.sqrt(252)
    return downside_vol.rolling(pct_window).rank(pct=True)
