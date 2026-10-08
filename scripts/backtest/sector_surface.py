# [BLUEPRINT] MOD-BT-238 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sector_surface
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.translated._c4_engine（run_query/load_px/wide/_load_seal_masks 只读通道）; zephyr.data.table_registry; factory_grid_executor._industry_map（惰性导入，行业锚+词表清洗单一真源复用）
# [CONSUMERS] scripts.backtest.factory_grid_executor（X_sector 维 sector_ctx 批级装载，矩阵战役 W5）；TDM-E-L2-01 四路子分面板供给（MOD-SIG-142 上游）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 四路子分口径=TDM-E-L2-01-1~4 冻结真源（结构强度 0-10=0.4·clip(涨停比/8%,0,1)+0.3·梯队代理+0.3·趋势；活跃/动量/资金流=截面 rank 百分位 0-100；多周期权重 q3/q5/q20=0.2/0.3/0.5 进 prereg）；合分=等权 0.25×4（结构×10 归一 0-100）+market_adjustment clamp[0,100]（TDM-E-L2-01）；资金流缺席→三路等权重归一并标 degraded（TDM fallback 在册）；候选池=逐日 Top15%（保底 1）；传导乘数查表封闭 ≥9→1.15/≥6→1.05/<6→0.90 + 三级 gate（板块>6 ∧ 个股强度>5 ∧ 日成交>2e8 元）=TDM-E-L2-06 卡口径；零行循环（转置 groupby 族，同 _apply_industry_topk_overlay 先例）；数据只读（kline_daily_hfq/industry_class/stk_limit/money_flow 四在册表）；PIT=industry_class 现行快照（valid_to IS NULL，与引擎 industry_map 同源）
# [MODIFY-GUARD] 地图节点 TDM-E-L2-01/TDM-E-L2-06
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 窗口行情缺失/行业锚空→RuntimeError（fail-closed 禁静默全市场）；money_flow 缺席→degraded 降权（TDM fallback，非异常）
# [TESTS] tests/research/backtest/test_sector_surface_wiring.py
# [TTL] permanent
"""SectorSurface — 板块强度四路面板 + 回测引擎传导后处理供给（MOD-BT-238）。

规格卡真源（矩阵战役 m2_exit_sector，照卡施工禁自拟）：
    spec_l2_TDM-E-L2-01_strength.md §2/§4（四路子分+行业聚合宽表+X_sector 接法）
    spec_l2_TDM-E-L2-06_conduction.md §2/§4（三级 gate+查表乘数+A1/A2 后 Top-N 前插段）

四路子分（行业 k，日 t；0-100 归一后等权合成）：
    01-1 结构强度：涨停占比（>8% 满分段）+连板梯队代理（昨日涨停今日再涨停家数≥1）+
        板块指数趋势（MA20 上方），合 0-10（合成时 ×10 归一）。
    01-2 动量活跃度：板块成交额占全市场比+5 日环比，截面 rank 百分位（保符号，2026-09-18 修正）。
    01-3 多周期动量：IND_close 3/5/20 日动量 rank 加权 0.2/0.3/0.5。
    01-4 板块资金流：主力净流入 3 日累计+当日大单净额（超大单+大单），rank 百分位；
        money_flow 缺席→三路等权重归一 + degraded（TDM fallback）。
    总评 sector_score = clamp(0.25·Σ四路(结构×10) + adj, 0, 100)；候选池=逐日 Top15%。

引擎接法：run_batch 批级一次 build_sector_context → evaluate_recipe 在 combined 解析后、
Top-N 前调 _apply_sector_overlay（X_sector=strength_top15 行业池掩码 / conduction
先 gate 后 weight 查表乘数，只调分不重排名=TDM 层级隔离纪律）。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from zephyr.data.table_registry import get_registry as _get_table_registry

# 表名常量（T6 纪律：禁散落字面量，经 table_registry 真源反查；同 executor 模块级形态）
_SQL_MONEY_FLOW_WINDOW = (
    "SELECT trade_date, symbol_canonical, main_net_inflow, "
    "super_large_net_inflow, large_net_inflow FROM "
    + _get_table_registry().table("market_money_flow")
    + " WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}')"
)

#: 传导乘数查表（TDM-E-L2-06 冻结口径：10 分制十分位三档）
CONDUCTION_MULT_STRONG: float = 1.15  # ≥9 分 → +15%
CONDUCTION_MULT_MID: float = 1.05  # ≥6 分 → +5%
CONDUCTION_MULT_WEAK: float = 0.90  # <6 分 → -10%（平段）
#: 三级放行门槛（TDM-E-L2-06-1：先 gate 后 weight）
GATE_SECTOR_MIN: float = 6.0  # 板块强度（10 分制）>6
GATE_STOCK_MIN: float = 5.0  # 个股强度（合成因子截面百分位×10）>5
GATE_AMOUNT_MIN: float = 2e8  # 日成交额（元）>2 亿
#: 候选池截取（TDM-E-L2-01：前 15%）
POOL_RATIO: float = 0.15
#: 结构强度分档（涨停占比满分段阈值）
LIMIT_RATIO_FULL: float = 0.08
#: 多周期动量权重（prereg 冻结项）
MOM_WEIGHTS: tuple[float, float, float] = (0.2, 0.3, 0.5)  # q3/q5/q20
#: 活跃度环比窗口
ACTIVITY_DELTA_DAYS: int = 5


class SectorSurfaceError(RuntimeError):
    """面板构建失败（窗口缺数据/行业锚空）——fail-closed。"""


@dataclass(frozen=True)
class SectorPanel:
    """行业聚合宽表批级容器（一次构建多格点共享）。

    ind_close/ind_amount: date×industry（成员等权 close 均值 / 成员求和 amount）。
    sealed_up: date×symbol 布尔封板掩码（_c4_engine 原始价口径复用）。
    industry_map: symbol→industry（PIT 现行快照，引擎 industry_map 同源）。
    flow_3d/big_net: date×industry 资金流面（万元；缺席=None）。
    degraded_flags: 缺维如实标记（禁静默）。
    """

    ind_close: pd.DataFrame
    ind_amount: pd.DataFrame
    sealed_up: pd.DataFrame
    industry_map: dict[str, str]
    flow_3d: pd.DataFrame | None
    big_net: pd.DataFrame | None
    degraded_flags: tuple[str, ...]


def load_industry_map() -> dict[str, str]:
    """行业锚复用（factory_grid_executor._industry_map 单一真源，惰性导入防环）。"""
    from factory_grid_executor import _industry_map

    return _industry_map()


def build_sector_panel(start: str, end: str) -> SectorPanel:
    """行业聚合宽表批级一次构建（规格卡 L2-01 §2 主通道；数据面全只读）。

    warm 由调用方负责（动量 20 日预热需 start 前移 ≥20 交易日，同引擎 warm_start 口径）。

    Raises:
        SectorSurfaceError: 行情窗口空/行业锚空。
    """
    from _c4_engine import _load_seal_masks, load_px, wide

    px = load_px(start, end, fields=("close", "amount"))
    close_w = wide(px, "close")
    amount_w = wide(px, "amount")
    if close_w.empty:
        raise SectorSurfaceError(f"kline_daily_hfq 窗口空 [{start},{end}]——fail-closed")

    industry_map = load_industry_map()
    if not industry_map:
        raise SectorSurfaceError("industry_map 清洗后为空（industry_class 数据健康异常）")

    # 行业聚合：转置 groupby（零行循环，_apply_industry_topk_overlay 同款形态）
    ind_of = pd.Series({s: industry_map.get(s) for s in close_w.columns})
    known = list(ind_of.index[ind_of.notna()])
    if not known:
        raise SectorSurfaceError("窗口宇宙与行业锚零交集——fail-closed")
    ind_index = ind_of.loc[known].to_numpy()
    ind_close = close_w[known].T.groupby(ind_index).mean().T.sort_index()
    ind_amount = amount_w[known].T.groupby(ind_index).sum().T.sort_index()

    # 封板掩码（原始价口径，_c4_engine 单一真源复用：raw close × stk_limit limit_up）
    sealed_up, _sealed_dn = _load_seal_masks(close_w.index, close_w.columns)

    # 资金流面（money_flow 2021 起实测；缺席=degraded 三路重归一，TDM fallback）
    flow_3d: pd.DataFrame | None = None
    big_net: pd.DataFrame | None = None
    degraded: list[str] = []
    try:
        from _c4_engine import run_query

        rows = run_query(_SQL_MONEY_FLOW_WINDOW.format(start=start, end=end))
    except Exception as exc:  # noqa: BLE001  资金流缺席走 fallback 非 fail-closed（TDM 在册）
        rows = []
        degraded.append(f"money_flow_query_fail:{type(exc).__name__}")
    if rows:
        mf = pd.DataFrame(
            rows,
            columns=[
                "trade_date",
                "symbol",
                "main_net_inflow",
                "super_large",
                "large",
            ],
        )
        mf["trade_date"] = pd.to_datetime(mf["trade_date"])
        mf = mf.drop_duplicates(subset=["trade_date", "symbol"], keep="last")
        # CH Decimal 列强转 float（真数 smoke 20261008 实钓：Decimal 与 float 加法 TypeError）
        mf[["main_net_inflow", "super_large", "large"]] = mf[["main_net_inflow", "super_large", "large"]].astype(float)
        mf["industry"] = mf["symbol"].astype(str).str[:6].map(industry_map)
        mf = mf.dropna(subset=["industry"])
        mf["big_order"] = mf["super_large"] + mf["large"]
        # 同行业多票=重复 (date,industry) 键：成员求和聚合（板块流=Σ成员流，pivot_table 防重）
        piv_main = mf.pivot_table(
            index="trade_date", columns="industry", values="main_net_inflow", aggfunc="sum"
        ).sort_index()
        piv_big = mf.pivot_table(index="trade_date", columns="industry", values="big_order", aggfunc="sum").sort_index()
        flow_3d = piv_main.rolling(3, min_periods=1).sum()
        big_net = piv_big
    else:
        degraded.append("money_flow_absent")

    return SectorPanel(
        ind_close=ind_close,
        ind_amount=ind_amount,
        sealed_up=sealed_up,
        industry_map=industry_map,
        flow_3d=flow_3d,
        big_net=big_net,
        degraded_flags=tuple(degraded),
    )


def _rank_pct(df: pd.DataFrame) -> pd.DataFrame:
    """截面 rank 百分位 0-100（平均秩；NaN 保持 NaN=诚实缺供不入池）。"""
    return df.rank(axis=1, pct=True) * 100.0


def sector_strength(
    panel: SectorPanel, market_adjustment: float = 0.0
) -> tuple[pd.DataFrame, pd.DataFrame, tuple[str, ...]]:
    """四路子分合成板块强度（规格卡 L2-01 §2 计算式逐条对码）。

    Returns:
        (sector_score date×industry 0-100, pool_mask date×industry bool, degraded_flags)。

    Raises:
        SectorSurfaceError: 基础面板缺列。
    """
    degraded = list(panel.degraded_flags)
    ind_close = panel.ind_close
    industries = list(ind_close.columns)  # 行业列（ind_close/ind_amount 已按行业聚合）
    # ── 01-1 结构强度（0-10）─────────────────────────────────────────
    # 涨停占比：板块内封板家数/有效家数（掩码缺席=无封板，禁编造）
    sym_ind = pd.Series({s: panel.industry_map[s] for s in panel.sealed_up.columns if s in panel.industry_map})
    if sym_ind.empty:
        raise SectorSurfaceError("封板掩码宇宙与行业锚零交集——fail-closed")
    seal_known = panel.sealed_up[list(sym_ind.index)]
    ind_keys = sym_ind.to_numpy()
    limit_cnt = seal_known.T.groupby(ind_keys).sum().T
    limit_cnt = limit_cnt.reindex(columns=industries, fill_value=0)
    member_cnt = sym_ind.value_counts().reindex(industries, fill_value=0).replace(0, np.nan)
    limit_ratio = limit_cnt.div(member_cnt, axis=1).fillna(0.0)
    norm_ratio = (limit_ratio / LIMIT_RATIO_FULL).clip(upper=1.0)
    # 梯队代理：昨日涨停今日再涨停家数 ≥1（真连板梯队 tick 语义不可考，卡内代理档）
    two_board = (seal_known & seal_known.shift(1)).fillna(False).astype(bool)
    ladder_cnt = two_board.T.groupby(ind_keys).sum().T
    ladder_cnt = ladder_cnt.reindex(columns=industries, fill_value=0)
    ladder = (ladder_cnt >= 1).astype(float)
    # 趋势：MA20 上方
    ma20 = ind_close.rolling(20, min_periods=20).mean()
    trend = (ind_close > ma20).astype(float).where(~ma20.isna(), 0.0)
    struct_score = 10.0 * (0.4 * norm_ratio + 0.3 * ladder + 0.3 * trend)

    # ── 01-2 动量活跃度（0-100，保符号）──────────────────────────────
    turn_ratio = panel.ind_amount.div(panel.ind_amount.sum(axis=1), axis=0)
    activity = _rank_pct(turn_ratio + turn_ratio.diff(ACTIVITY_DELTA_DAYS))

    # ── 01-3 多周期动量（0-100，q3/q5/q20=0.2/0.3/0.5）───────────────
    moms = [ind_close.pct_change(n) for n in (3, 5, 20)]
    q_score = sum(w * _rank_pct(m) for w, m in zip(MOM_WEIGHTS, moms, strict=True))

    # ── 01-4 板块资金流（0-100；缺席→三路重归一 degraded）────────────
    adj = float(market_adjustment)
    if panel.flow_3d is not None and panel.big_net is not None:
        flow_raw = panel.flow_3d.reindex_like(ind_close).fillna(0.0) + panel.big_net.reindex_like(ind_close).fillna(0.0)
        flow_score = _rank_pct(flow_raw)
        composite = 0.25 * (struct_score * 10.0 + activity + q_score + flow_score) + adj
    else:
        degraded.append("flow_dim_absent_renormalized")
        composite = (struct_score * 10.0 + activity + q_score) / 3.0 + adj
    sector_score = composite.clip(lower=0.0, upper=100.0)

    # ── 候选池：逐日 Top15%（保底 1）─────────────────────────────────
    # 数学保证：任意含非 NaN 分的行，max ≥ 85 分位 → ge 恒至少 1 真（保底 1 内蕴）；
    # 全 NaN 行（当日无有效行业分）保持全 False=诚实缺供禁硬选。
    thresh = sector_score.quantile(1.0 - POOL_RATIO, axis=1)
    pool_mask = sector_score.ge(thresh, axis=0)
    return sector_score, pool_mask, tuple(degraded)


def build_sector_context(start: str, end: str, want_amount: bool = False) -> dict:
    """引擎批级装载入口：四路强度面板 → X_sector sector_ctx dict。

    Returns:
        {'sector_score': date×industry 0-100, 'pool_mask': date×industry bool,
         'amount': date×symbol 元（want_amount 时，conduction gate 用）,
         'degraded_flags': tuple}
    """
    panel = build_sector_panel(start, end)
    score, pool, degraded = sector_strength(panel)
    ctx: dict = {
        "sector_score": score,
        "pool_mask": pool,
        "degraded_flags": degraded,
    }
    if want_amount:
        from _c4_engine import load_px, wide

        px = load_px(start, end, fields=("amount",))
        ctx["amount"] = wide(px, "amount")
    return ctx


def conduction_multiplier(sector_score_10: pd.DataFrame) -> pd.DataFrame:
    """传导乘数查表（0-10 制十分位三档，TDM-E-L2-06 冻结口径，向量化）。"""
    arr = sector_score_10.to_numpy(dtype=float)
    mult = np.select(
        [arr >= 9.0, arr >= 6.0],
        [CONDUCTION_MULT_STRONG, CONDUCTION_MULT_MID],
        default=CONDUCTION_MULT_WEAK,
    )
    return pd.DataFrame(mult, index=sector_score_10.index, columns=sector_score_10.columns)
