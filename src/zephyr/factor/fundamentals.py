# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.fundamentals
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas（纯函数核，无 IO）
# [CONSUMERS] （F2 起接 IC 评估/分层回测；factor_registry FCT-FQ/FCT-GR 族；与预期侧 expectations.py 互不侵入）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 全函数纯无 IO；输入契约=financial_derived(DS-230) statement 粒度面板
#              （MultiIndex(symbol, report_period) 升序，每键一行=PIT 可见最新版本）；
#              方向约定=值越大预期收益越高（对冲 Sloan/国盛原方向取负在函数内完成）；
#              跨期参照统一 _shift_report_by_symbol(k=4)（上年同期报告期）；
#              除法分母零/NaN→NaN 禁 inf；胜异/标准化属评估层职责，本模块输出原始值；
#              fq06 任一子项缺失→整体 NaN（F-Score 语义要求九项齐）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入未对齐/空输入→返回 NaN 系列或空（不抛异常，因子评估层负责断言）
# [TESTS] tests/factor/test_fundamentals.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""fundamentals — 财报事实侧因子族（消费端 F2，2026-09-14）。

数据源：c3_fundamental.financial_derived（DS-230，跨表对齐+单季+TTM+比率，statement 粒度，
PIT=三方公告日齐+哨兵守卫）。设计真源：docs/_working/2026-09-12-fundamental-consumption-design.md §M2；
首发顺序（裁定#230/D5）：FQ-01 应计 → GR-01 单季营收 → FQ-03 GPOA → FQ-06 F-Score；
D3 双登记：FQ-01 先出证，FQ-02 现金流实现率作对照（日度秩相关>=0.85 挂 variant_of）。

设计约定（与 expectations.py 同款）：
- 全部纯函数：输入已是 PIT 正确的 statement 面板，输出同型 Series（NaN=无有效值）。
- 面板用法：MultiIndex(symbol, report_period) 升序；涉及时序移位的函数自动按 symbol 分组。
- 除法分母为 0/NaN → 产 NaN（禁 inf）；方向统一"值越大预期收益越高"。
- 胜异（winsorize）/行业中性/标准化 = 评估层职责，本模块输出原始值。
"""

from __future__ import annotations

import pandas as pd

__all__ = [
    "fq01_accrual",
    "fq02_cash_conversion",
    "fq03_gpoa",
    "fq04_delta_roe_q",
    "gr01_rev_q_yoy",
    "gr02_np_q_qoq",
    "fq05_info_quality",
    "fq06_fscore",
]

_FSCORE_ITEMS = 9


def _safe_div(num: pd.Series, den: pd.Series | float) -> pd.Series:
    """安全除法：分母 0/NaN → NaN（禁 inf）。"""
    den_s = pd.Series(den, index=num.index) if not isinstance(den, pd.Series) else den
    out = num / den_s
    return out.where(den_s.abs() > 0)


def _shift_report_by_symbol(s: pd.Series, k: int = 4) -> pd.Series:
    """按 symbol 分组的报告期移位（k=4 即上年同期）；单标的（非 MultiIndex）直接 shift。

    契约：面板每 (symbol, report_period) 恰一行（PIT 可见最新版本）且按报告期升序，
    故 shift(4)=上年同季报告。
    """
    if isinstance(s.index, pd.MultiIndex) and "symbol" in (s.index.names or []):
        return s.groupby(level="symbol").shift(k)
    return s.shift(k)


def _rolling_mean_by_symbol(s: pd.Series, w: int) -> pd.Series:
    """按 symbol 分组滚动均值（报告期数）；min_periods=w//2 下限 4。"""

    def _roll(x: pd.Series) -> pd.Series:
        return x.rolling(w, min_periods=max(4, w // 2)).mean()

    if isinstance(s.index, pd.MultiIndex) and "symbol" in (s.index.names or []):
        return s.groupby(level="symbol", sort=False).apply(_roll).droplevel(0).reindex(s.index)
    return _roll(s)


def _rolling_std_by_symbol(s: pd.Series, w: int) -> pd.Series:
    """按 symbol 分组滚动标准差（报告期数）。"""

    def _roll(x: pd.Series) -> pd.Series:
        return x.rolling(w, min_periods=max(4, w // 2)).std()

    if isinstance(s.index, pd.MultiIndex) and "symbol" in (s.index.names or []):
        return s.groupby(level="symbol", sort=False).apply(_roll).droplevel(0).reindex(s.index)
    return _roll(s)


# ----------------------------------------------------------------------------
# FQ-01 应计（quality，D5 首发/D3 主）
# 依据：Sloan 1996 The Accounting Review——高应计=盈余持续性差=未来收益低（方向取负）；
#       A 股实证：公告期贡献 28% 年超额（应计异象综述），剔除亏损股更强
# ----------------------------------------------------------------------------
def fq01_accrual(accrual_ttm: pd.Series) -> pd.Series:
    """应计因子 = -应计(TTM)，应计=(净利−经营现金流)/总资产（DS-230 accrual_ttm 列）。

    方向：应计越高（利润里真金白银越少）未来收益越低 → 取负对齐"值越大越好"。
    """
    return -accrual_ttm


# ----------------------------------------------------------------------------
# FQ-02 现金流实现率（quality，D3 对照——与 FQ-01 秩相关>=0.85 挂 variant_of）
# 依据：券商量化专题（2026-04）改进应计：传统同期对比误判成长股，改用时间序列
#       利润→现金流转化效率 + 现金流残差波动率（专题 RankIC 2.61%→2.93%）
# ----------------------------------------------------------------------------
def fq02_cash_conversion(
    np_ttm: pd.Series,
    ocf_ttm: pd.Series,
    total_assets: pd.Series,
    window: int = 8,
) -> pd.Series:
    """现金流实现率 = 转化效率均值 − 应计残差波动率（滚动 window 个报告期）。

    两步（可拆用）：
      conv_t   = ocf_ttm / |np_ttm|                        —— 利润→现金转化效率
      vol_t    = std((np_ttm−ocf_ttm)/total_assets, w)     —— 应计残差波动率
      factor_t = mean(conv, w) − vol_t
    """
    conv = _safe_div(ocf_ttm, np_ttm.abs())
    conv_mean = _rolling_mean_by_symbol(conv, window)
    accrual_vol = _rolling_std_by_symbol(_safe_div(np_ttm - ocf_ttm, total_assets), window)
    out = conv_mean - accrual_vol
    return out


# ----------------------------------------------------------------------------
# FQ-03 GPOA（quality，D5 首发第三）
# 依据：Novy-Marx 2013 JFE《The Other Side of Value》——毛利率/总资产，
#       "价值另一面"，不受杠杆与税务扭曲
# ----------------------------------------------------------------------------
def fq03_gpoa(gpoa_ttm: pd.Series) -> pd.Series:  # noqa: clone-guard — 因子注册表 convention 每因子独立入口
    """GPOA = (营收−成本)/总资产（TTM，DS-230 gpoa_ttm 列），方向原样（值大=好）。"""
    return gpoa_ttm


# ----------------------------------------------------------------------------
# FQ-04 单季盈利变化 ΔROEq（quality）
# 依据：雪球 V4.x 单季拆解框架实证——roe_q 同比差；单季 ROE 由派生面板年化重建
# ----------------------------------------------------------------------------
def fq04_delta_roe_q(np_q: pd.Series, equity_incl_minority: pd.Series) -> pd.Series:
    """ΔROEq = 年化单季 ROE(t) − 年化单季 ROE(t 上年同期)，roe_q = np_q×4/净资产。"""
    roe_q = _safe_div(np_q * 4.0, equity_incl_minority)
    return roe_q - _shift_report_by_symbol(roe_q, 4)


# ----------------------------------------------------------------------------
# GR-01 单季营收成长（momentum——基本面动量；注册表无 growth 类，就近登记+条目注记）
# 依据：RevSUE 口径（营收比净利难操纵，雪球 V4.x）；DS-230 rev_q_yoy 列原样
# ----------------------------------------------------------------------------
def gr01_rev_q_yoy(rev_q_yoy: pd.Series) -> pd.Series:  # noqa: clone-guard — 同上
    """单季营收同比（(cur-base)/|base| 已在派生层完成）；小基数长尾由评估层胜异。"""
    return rev_q_yoy


# ----------------------------------------------------------------------------
# GR-02 盈利加速度（momentum）
# 依据：雪球 QoQ_Acc——单季净利环比变化率，盈利二阶导（DS-230 np_q_qoq 列原样）
# ----------------------------------------------------------------------------
def gr02_np_q_qoq(np_q_qoq: pd.Series) -> pd.Series:  # noqa: clone-guard — 同上
    """单季净利环比（盈利加速度）。"""
    return np_q_qoq


# ----------------------------------------------------------------------------
# FQ-05 信息质量代理（quality）
# 依据：国盛多因子系列 14《刻画财报信息质量》可得子集——应收/营收异常（自身历史 z）
#       + 实际税率波动；高质量=低异常低波动 → 取负对齐方向（附注级项无数据，做可得子集）
# ----------------------------------------------------------------------------
def fq05_info_quality(
    accounts_receivable: pd.Series,
    rev_ttm: pd.Series,
    eff_tax_rate_ttm: pd.Series,
    window: int = 12,
) -> pd.Series:
    """信息质量 = −|应收/营收 自身 z| − 税率波动（滚动 window 个报告期）。"""
    ar_ratio = _safe_div(accounts_receivable, rev_ttm)
    ar_mean = _rolling_mean_by_symbol(ar_ratio, window)
    ar_std = _rolling_std_by_symbol(ar_ratio, window)
    ar_z = (ar_ratio - ar_mean) / ar_std
    tax_vol = _rolling_std_by_symbol(eff_tax_rate_ttm, window)
    return -(ar_z.abs()) - tax_vol


# ----------------------------------------------------------------------------
# FQ-06 Piotroski F-Score（quality，D5 首发第四）
# 依据：Piotroski 2000 JAR——九项 0/1 计数（盈利 4+杠杆流动 3+运营效率 2）；
#       九项全部可由 DS-230 面板+上年同期重建（无增发项=总股本同比不增）
# ----------------------------------------------------------------------------
def fq06_fscore(
    np_ttm: pd.Series,
    ocf_ttm: pd.Series,
    total_assets: pd.Series,
    total_liabilities: pd.Series,
    total_current_assets: pd.Series,
    total_current_liabilities: pd.Series,
    total_shares: pd.Series,
    rev_ttm: pd.Series,
    gross_margin_q: pd.Series,
) -> pd.Series:
    """F-Score = 九项 0/1 求和；任一子项缺失 → NaN（九项齐才有分数，覆盖语义诚实）。

    九项（Piotroski 原序）：ROA>0；CFO>0；ΔROA>0；应计质量(CFO>ROA 即应计<0)；
    杠杆降；流动比率升；无增发（总股本同比不增）；毛利率升；周转率升。
    """
    roa = _safe_div(np_ttm, total_assets)
    roa_prev = _shift_report_by_symbol(roa, 4)
    accrual = _safe_div(np_ttm - ocf_ttm, total_assets)
    debt = _safe_div(total_liabilities, total_assets)
    debt_prev = _shift_report_by_symbol(debt, 4)
    cr = _safe_div(total_current_assets, total_current_liabilities)
    cr_prev = _shift_report_by_symbol(cr, 4)
    shares_prev = _shift_report_by_symbol(total_shares, 4)
    turnover = _safe_div(rev_ttm, total_assets)
    turnover_prev = _shift_report_by_symbol(turnover, 4)
    gm_prev = _shift_report_by_symbol(gross_margin_q, 4)

    items = [
        (roa > 0).astype("float").where(roa.notna()),
        (ocf_ttm > 0).astype("float").where(ocf_ttm.notna()),
        (roa > roa_prev).astype("float").where(roa.notna() & roa_prev.notna()),
        (accrual < 0).astype("float").where(accrual.notna()),
        (debt < debt_prev).astype("float").where(debt.notna() & debt_prev.notna()),
        (cr > cr_prev).astype("float").where(cr.notna() & cr_prev.notna()),
        (total_shares <= shares_prev).astype("float").where(total_shares.notna() & shares_prev.notna()),
        (gross_margin_q > gm_prev).astype("float").where(gross_margin_q.notna() & gm_prev.notna()),
        (turnover > turnover_prev).astype("float").where(turnover.notna() & turnover_prev.notna()),
    ]
    assert len(items) == _FSCORE_ITEMS
    frame = pd.concat(items, axis=1)
    # 九项齐才出分（严格语义：缺项≠0 分）；输出 0~9 浮点
    return frame.sum(axis=1).where(frame.notna().all(axis=1))


# ----------------------------------------------------------------------------
# FQ-01 衍生：应计负向剔除器（M5 negative_veto 弹药；生产接线待 SOP-C C5 解冻）
# 依据：⑥ 窄回测实证——应计 LS 价差 alpha 在空头腿（A股个人不可做空），
#       多头买入不可部署（IS 超额 Sharpe -0.179）；转为"剔除高应计"用法
# ----------------------------------------------------------------------------
def accrual_negative_screen(accrual_ttm: pd.Series, threshold: float = 0.0) -> pd.Series:
    """应计负向剔除器：应计(TTM) > threshold → True=建议剔除该标的。

    经典口径 threshold=0（应计为正=利润含非现金成分，Sloan 盈余质量差）；
    截面分位版（剔最高 20% 等）由消费方组合层实现（需截面上下文）。
    方向：True=剔除。accrual NaN → False（无证据不剔除，宁缺毋错）。
    """
    screen = (accrual_ttm > threshold).astype("float")
    return (screen == 1.0).where(accrual_ttm.notna(), other=False)
