# [BLUEPRINT] MOD-SIG-165 | docs/_working/infoaxis/15_intraday_workbook.md §2/§3/§5 | 一档盘口特征件
# [MODULE] zephyr.signal_intraday.orderflow_features
# [DOMAIN] D_SIGNAL_INTRADAY
# [DEPENDENCIES] 无（纯函数；tick 序列全注入——ch_tick_replay 列契约 8 字段一档口径）
# [CONSUMERS] t0_trading_pipeline 三策略之盘口失衡腿（MOD-SIG-090 生产接线留集成批=其头注
#   契约，本件=该腿的特征供给面）; D_EXEC_SIM 撮合（micro-price 公允价参考，二期）;
#   L3-11-2 盘中涨速异动交叉验证（后置）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯函数零 IO 零触网; 输入=tick 序列（timestamp,price,volume,amount,bid_price,
#   ask_price,bid_volume,ask_volume 一档——DS-195 列契约 ch_tick_replay.py:59，2-5 档填 0
#   现实下只用一档量); OFI=Cont-Kukanov-Stoikov 一档口径 Σ e_n（e=Δbid_vol·1{bid 不落}
#   -Δask_vol·1{ask 不涨}）零克隆无外部依赖; micro-price=Stoikov imbalance 加权
#   (bid*ask_vol+ask*bid_vol)/(bid_vol+ask_vol) 带零保护; 近零保护=分母<1e-9 → None 留痕
#   禁估算（PEAD 同口径纪律）; 特征带时窗（bar 聚合窗长注入）; 判据数值零自拟（窗长/阈值
#   由调用方或考卡冻结面给）
# [MODIFY-GUARD] tests/signal_intraday/test_orderflow_features.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空序列→空特征; 单点序列→OFI=None 首帧不可差分; 全模块禁抛（纯特征件）
# [TESTS] tests/signal_intraday/test_orderflow_features.py
# [TTL] permanent

"""一档盘口特征件（st-infoaxis-20261013 P2 做T首刀——15 号作业簿 §3 OFI/micro-price 借鉴落地）。

真源：docs/_working/infoaxis/15_intraday_workbook.md §3（Cont-Kukanov-Stoikov OFI 一档可算
——tick_data 仅一档现实下的先行特征面；预测力衰减秒-分钟级，消费须带时窗）。
# [ALGO_FLOW]
# 层: 输入 → 逐帧差分 → 窗聚合 → 特征组
# - OFI: 连续两帧 e_n 累加（窗内 Σ）＋归一（÷窗内均深度）
# - imbalance: (bid_vol-ask_vol)/(bid_vol+ask_vol) 末帧＋窗均
# - micro-price: 末帧公允价＋相对中间价偏移
# [/ALGO_FLOW]
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Final, Sequence

__all__: Final = ["Tick", "OrderflowFeatures", "compute_features"]

_EPS: Final = 1e-9


@dataclass(frozen=True)
class Tick:
    """一档 tick 帧（DS-195 列契约子集；2-5 档填 0 现实只用一档）。"""

    timestamp: str
    price: float
    bid_price: float
    ask_price: float
    bid_volume: float
    ask_volume: float
    volume: float = 0.0
    amount: float = 0.0


@dataclass(frozen=True)
class OrderflowFeatures:
    """窗聚合特征组（None=不可计算留痕，禁估算）。"""

    ofi_sum: float | None
    ofi_normalized: float | None
    imbalance_last: float | None
    imbalance_mean: float | None
    micro_price: float | None
    micro_price_offset_bps: float | None
    n_ticks: int


def _ofi_event(prev: Tick, cur: Tick) -> float | None:
    """单帧 OFI 贡献 e_n（CKS 一档）：bid 不落加 Δbid_vol，ask 不升减 Δask_vol。"""
    d_bid = cur.bid_volume - prev.bid_volume
    d_ask = cur.ask_volume - prev.ask_volume
    bid_stays = cur.bid_price >= prev.bid_price - _EPS
    ask_stays = cur.ask_price <= prev.ask_price + _EPS
    return (d_bid if bid_stays else 0.0) - (d_ask if ask_stays else 0.0)


def _micro_price(t: Tick) -> float | None:
    denom = t.bid_volume + t.ask_volume
    if denom < _EPS or t.bid_price <= 0 or t.ask_price <= 0:
        return None
    return (t.bid_price * t.ask_volume + t.ask_price * t.bid_volume) / denom


def compute_features(ticks: Sequence[Tick]) -> OrderflowFeatures:
    """窗内特征组（空/单帧→全 None 留痕）。"""
    n = len(ticks)
    if n == 0:
        return OrderflowFeatures(None, None, None, None, None, None, 0)
    if n == 1:
        t = ticks[0]
        return OrderflowFeatures(None, None, _imb(t), _imb(t), _micro_price(t), _offset_bps(t), 1)
    ofi = 0.0
    depths = []
    for prev, cur in itertools.pairwise(ticks):
        e = _ofi_event(prev, cur)
        if e is not None:
            ofi += e
        depths.append(prev.bid_volume + prev.ask_volume)
    depths.append(ticks[-1].bid_volume + ticks[-1].ask_volume)
    mean_depth = sum(depths) / len(depths) if depths else 0.0
    last = ticks[-1]
    mp = _micro_price(last)
    return OrderflowFeatures(
        ofi_sum=ofi,
        ofi_normalized=(ofi / mean_depth) if mean_depth > _EPS else None,
        imbalance_last=_imb(last),
        imbalance_mean=(sum(v for v in (_imb(t) for t in ticks) if v is not None) / n if n else None),
        micro_price=mp,
        micro_price_offset_bps=_offset_bps(last),
        n_ticks=n,
    )


def _imb(t: Tick) -> float | None:
    denom = t.bid_volume + t.ask_volume
    if denom < _EPS:
        return None
    return (t.bid_volume - t.ask_volume) / denom


def _offset_bps(t: Tick) -> float | None:
    mp = _micro_price(t)
    mid = (t.bid_price + t.ask_price) / 2 if t.bid_price > 0 and t.ask_price > 0 else None
    if mp is None or mid is None or mid < _EPS:
        return None
    return (mp - mid) / mid * 1e4
