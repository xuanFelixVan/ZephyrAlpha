# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.9 Phase2c
# [MODULE] zephyr.regime.features.synthetic_vix
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; logging
# [CONSUMERS] MOD-REGIME-002(OverlaySignalsConstructor消费vix_pct→S1 vix_panic/S2 vix)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] vix_pct∈[0,1]; 数据缺失返回空Series(调用方回退vol_pct); PIT由调用方shift(1); fail-closed消费（SVX-1-P0）：iv<=0 的 DEFAULT 0 伪装值与 delta=NULL 的行不入 ATM 池，曲面有行而池空必发非静默 WARNING（禁静默零值）
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_synthetic_vix.py; tests/regime/test_synthetic_vix_iv_path.py; tests/data/implementations/test_option_iv_surface_delta_feed.py
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

# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/synthetic_vix.yaml
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

_logger = logging.getLogger(__name__)

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


def _atm_empty_warning(df: pd.DataFrame) -> None:
    """ATM 池空但曲面有行 → 出声（SVX-1-P0：这条静默降级曾让期权 IV 主路径死半年）。

    区分两种成因，第一类是**进料口事故**，第二类是正常市场结构：
      ① delta 恒 0 —— miniqmt 未声明 delta/vega 列，被 DDL DEFAULT 0 兜底，
         |0-0.5|=0.5 → 全库行被 ATM 筛子排除 → 主路径零产出、vix_pct 恒走后备；
      ② 当日确无平值档（delta 分布合理但离 0.5 远）。
    """
    dabs = df["delta"].abs()
    all_zero = bool((dabs == 0).all())
    _logger.warning(
        "期权 IV 曲面 %d 行全部被 ATM 筛子(|abs(delta)-0.5|<0.15) 排除，"
        "主路径零产出→调用方回退合成 VIX；|delta| 区间[%s, %s]%s",
        len(df),
        float(dabs.min()),
        float(dabs.max()),
        "（delta 恒 0：进料口未落 delta/vega，SVX-1-P0 事故签名，非市场结构）"
        if all_zero
        else "",
    )


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
    # SVX-1-P0 消费纪律（禁静默零值）：坏行不静默参与 ATM 均值
    #   iv<=0 = 进料口反解失败被 Decimal DEFAULT 0 兜出的假值（非"零波动"），
    #           混入均值会把 VIX 腰斩（plausible-but-wrong 比 None 更坏）。
    fake_zero_iv = df["iv"].notna() & (df["iv"] <= 0)
    if fake_zero_iv.any():
        _logger.warning(
            "期权 IV 曲面 %d/%d 行 iv<=0（进料口反解失败的 DEFAULT 0 伪装值）已排除，"
            "不参与 ATM 均值——若占比持续偏高，请查 miniqmt_provider._compute_iv_rows",
            int(fake_zero_iv.sum()),
            len(df),
        )
        df = df[~fake_zero_iv]
    if df.empty:
        return pd.Series(dtype=float, name="vix")
    null_delta = int(df["delta"].isna().sum())
    if null_delta:
        _logger.warning(
            "期权 IV 曲面 %d/%d 行 delta 为 NULL（进料口显式标注不可用），"
            "这些行不进入 ATM 池（fail-closed，不按 0 处理）",
            null_delta,
            len(df),
        )
    # ATM 筛选：|delta-0.5|<0.15（call delta 接近 0.5 为 ATM）
    df["delta_abs"] = df["delta"].abs()
    atm = df[(df["delta_abs"] - 0.5).abs() < 0.15].copy()
    if atm.empty:
        _atm_empty_warning(df)
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
