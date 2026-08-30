# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | 19 号 §6
# [MODULE] zephyr.data.northbound_hold_analysis
# [DOMAIN] D_DATA
# [DEPENDENCIES] pandas
# [CONSUMERS] 外资行为分析（季报复盘；因子立项后供 25 号多因子消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Δ持股×当季VWAP 单公式; 缺VWAP标的剔除(宁缺毋错不虚构金额); 同季度/空季度比较拒绝
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 同季度或空季度->ValueError
# [TESTS] tests/zephyr/data/test_northbound_hold_analysis.py
# [A_module] module_id=MOD-DAT-northbound_hold_analysis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #19_northbound_hold_snapshot §6.3/§6.5
# [ALGO_FLOW]
# I1: snapshot 季度持仓快照(trade_date/ts_code/hold_share) + vwap 当季个股 VWAP Series
# F1: compute_quarter_position_changes(两季度持仓外连接 → Δ持股×VWAP；退出=负全仓/新进=全仓)
# F2: top_position_changes(delta_amount 降序取 top 加仓 / 升序取 top 减仓)
# F3: estimate_quarterly_net_inflow(Σ Δ持股×VWAP → 准北向季度净流入)
# O1: 变化明细 DataFrame / top_add+top_reduce dict / 净流入 float
# [/ALGO_FLOW]
"""
北向季度持仓快照分析层（19 号 memo §6.3/§6.5 MVP，数据断档后的准北向估算）。

港交所 2024-08-19 停发日频北向后，季度持仓快照是唯一的北向持仓真源
（northbound_hold_fetcher 落库 c1_market.northbound_hold_snapshot）。本模块落地
memo 审定的 MVP 两项（单公式 Δ持股数量 × 当季 VWAP，pandas 数十行）：

  - §6.3 个股增减持排名（流量信号）：主动增减仓金额 = Δ持股 × 当季 VWAP，
    取 top 加仓/top 减仓。主动增减仓才是外资真实意图（股价效应是被动浮盈）。
  - §6.5 季度净流入估算（总量）：Σ_all_stocks(Δ持股 × 当季VWAP)——现在唯一能
    算出的"准北向净流入"（季度颗粒度），可与国信季度估算交叉验证。

口径说明：
  - 当季 VWAP 由调用方注入（项目已有成交量加权均价数据）；缺 VWAP 标的剔除
    （宁缺毋错：虚构价格会污染净流入总量，剔除使估算保守偏小）。
  - 退出标的（当季无持仓记录）= 负全仓减仓；新进标的 = 全仓加仓。
  - 季度颗粒度样本量约束（memo §6.4 警示）：方向性参考，不做硬信号。

依据: 19_northbound_hold_snapshot v1.0.1 §6.3/§6.5

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: snapshot 参数
#   fields: 参数 snapshot，类型注解 pd.DataFrame
#   code: northbound_hold_analysis.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: prev_date 参数
#   fields: 参数 prev_date（无注解）
#   code: northbound_hold_analysis.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: curr_date 参数
#   fields: 参数 curr_date（无注解）
#   code: northbound_hold_analysis.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: vwap 参数
#   fields: 参数 vwap，类型注解 pd.Series
#   code: northbound_hold_analysis.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① compute_quarter_position_changes
#   name_en: compute_quarter_position_changes
#   intro: 两季度间个股主动增减仓金额（Δ持股 × 当季 VWAP）。
#   desc: 两季度间个股主动增减仓金额（Δ持股 × 当季 VWAP）。 Args: snapshot: 持仓快照（列 trade_date/ts_code/hold_share）。 prev…；源码 L123-L167
#   inputs: snapshot prev_date curr_date vwap
#   outputs: pd.DataFrame
# - id: A2
#   name_zh: ② top_position_changes
#   name_en: top_position_changes
#   intro: top 加仓/减仓排名（§6.3 流量信号；零变动标的不入榜）。
#   desc: top 加仓/减仓排名（§6.3 流量信号；零变动标的不入榜）。 Args: changes: compute_quarter_position_changes 输出。 top_…；源码 L170-L183
#   inputs: changes top_n
#   outputs: dict[str, pd.DataFrame]
# - id: A3
#   name_zh: ③ estimate_quarterly_net_inflow
#   name_en: estimate_quarterly_net_inflow
#   intro: 季度净流入估算（§6.5）：Σ Δ持股 × 当季 VWAP。
#   desc: 季度净流入估算（§6.5）：Σ Δ持股 × 当季 VWAP。 季度颗粒度的"准北向净流入"——可与国信季度估算（如 2026Q2 ~2193 亿） 交叉验证误差范围。缺 VWAP…；源码 L186-L198
#   inputs: snapshot prev_date curr_date vwap
#   outputs: float
# 层: 输出
# - id: O1
#   name_zh: pd.DataFrame
#   name_en: pd.DataFrame
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 外资行为分析（季报复盘；因子立项后供 25 号多因子消费）
# - id: O2
#   name_zh: dict[str, pd.DataFrame]
#   name_en: dict[str, pd.DataFrame]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 外资行为分析（季报复盘；因子立项后供 25 号多因子消费）
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

import logging

import pandas as pd

__all__ = [
    "compute_quarter_position_changes",
    "estimate_quarterly_net_inflow",
    "top_position_changes",
]

log = logging.getLogger(__name__)


def compute_quarter_position_changes(
    snapshot: pd.DataFrame,
    prev_date,
    curr_date,
    vwap: pd.Series,
) -> pd.DataFrame:
    """两季度间个股主动增减仓金额（Δ持股 × 当季 VWAP）。

    Args:
        snapshot: 持仓快照（列 trade_date/ts_code/hold_share）。
        prev_date / curr_date: 上季末 / 当季末日期（须不同且均有记录）。
        vwap: 当季个股 VWAP（index=ts_code）。

    Returns:
        pd.DataFrame：ts_code/hold_prev/hold_curr/delta_share/vwap/delta_amount，
        按 delta_amount 降序。缺 VWAP 标的剔除（log 计数）。
    """
    if pd.Timestamp(prev_date) == pd.Timestamp(curr_date):
        raise ValueError("prev_date 与 curr_date 须为不同季度")
    prev = snapshot[snapshot["trade_date"].astype(str) == str(prev_date)]
    curr = snapshot[snapshot["trade_date"].astype(str) == str(curr_date)]
    if prev.empty or curr.empty:
        raise ValueError(f"季度无记录: prev={len(prev)} 行, curr={len(curr)} 行")

    p = prev.set_index("ts_code")["hold_share"].rename("hold_prev")
    c = curr.set_index("ts_code")["hold_share"].rename("hold_curr")
    merged = pd.concat([p, c], axis=1).fillna(0.0)
    merged["delta_share"] = merged["hold_curr"] - merged["hold_prev"]

    vw = vwap.reindex(merged.index)
    missing = vw.isna()
    if missing.any():
        log.warning(
            "北向增减持 %s→%s: %d 只标的缺当季 VWAP 被剔除（宁缺毋错）: %s",
            prev_date,
            curr_date,
            int(missing.sum()),
            list(merged.index[missing][:5]),
        )
    merged = merged[~missing]
    merged["vwap"] = vw[~missing]
    merged["delta_amount"] = merged["delta_share"] * merged["vwap"]

    out = merged.reset_index().sort_values("delta_amount", ascending=False)
    return out.reset_index(drop=True)


def top_position_changes(changes: pd.DataFrame, top_n: int = 20) -> dict[str, pd.DataFrame]:
    """top 加仓/减仓排名（§6.3 流量信号；零变动标的不入榜）。

    Args:
        changes: compute_quarter_position_changes 输出。
        top_n: 每榜条数。

    Returns:
        {"top_add": 增仓 top_n（金额降序）, "top_reduce": 减仓 top_n（金额升序）}
    """
    adds = changes[changes["delta_amount"] > 0].head(top_n)
    reduces = changes[changes["delta_amount"] < 0].tail(top_n)
    reduces = reduces.sort_values("delta_amount", ascending=True).reset_index(drop=True)
    return {"top_add": adds.reset_index(drop=True), "top_reduce": reduces}


def estimate_quarterly_net_inflow(
    snapshot: pd.DataFrame,
    prev_date,
    curr_date,
    vwap: pd.Series,
) -> float:
    """季度净流入估算（§6.5）：Σ Δ持股 × 当季 VWAP。

    季度颗粒度的"准北向净流入"——可与国信季度估算（如 2026Q2 ~2193 亿）
    交叉验证误差范围。缺 VWAP 标的剔除使估算保守偏小（见模块口径说明）。
    """
    changes = compute_quarter_position_changes(snapshot, prev_date, curr_date, vwap)
    return float(changes["delta_amount"].sum())
