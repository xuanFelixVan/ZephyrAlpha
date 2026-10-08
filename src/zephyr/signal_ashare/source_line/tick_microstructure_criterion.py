# [BLUEPRINT] MOD-SIG-156 | docs/03_modules/_domain_signal/source_line_tick_microstructure_criterion/blueprint.md
# [MODULE] zephyr.signal_ashare.source_line.tick_microstructure_criterion
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] TDM-E-L9-A02（源线·Tick分笔，decision_question="日内微观结构能否预测次日方向与冲击成本？"；module_ref 挂载=总裁终裁批，本件先按源线判据口径落码）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数核零 IO（tick 序列由调用方注入，按时间升序）; 买卖不平衡 ∈ [-1,1] 单值输出; 输入非法 fail-closed（TickMicroInputError）; 记录级缺陷跳过记 notes 不整体 fail; 同输入必同输出（零墙钟零随机）; PIT=TDX分笔仅近交易日，历史断档不可补（缺口透明透出不补数）
# [MODIFY-GUARD] 地图节点 TDM-E-L9-A02（本班禁改 trading_decision_map.yaml，module_ref 挂载待总裁终裁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tick 序列非法（空/长度<2/NaN/非正价/非正量/side 非法值）→ TickMicroInputError；单笔缺陷（缺字段/非法值）→ 跳过记 notes
# [TESTS] tests/signal_ashare/source_line/test_tick_microstructure_criterion.py
# [TTL] permanent
"""TickMicrostructureCriterion — A02 Tick分笔源线判据转化器（MOD-SIG-156）。

TDM-E-L9-A02「源线·Tick分笔」的 decision_question：
    日内微观结构能否预测次日方向与冲击成本？

本件把标准化 tick 成交流（DS-001 口径：价格/数量/买卖方向，由 tick 聚合
或行情源直供）转化为三段判据：

    1. 主动性买卖不平衡（imbalance）：买向成交量占比 − 卖向成交量占比，
       ∈ [-1,1]，五档（STRONG_BUY/BUY/NEUTRAL/SELL/STRONG_SELL），
       阈值 ±0.10/±0.25 初拟待标定；
    2. 冲击成本代理（impact_coef）：Kyle-λ 简化代理 = Σ|Δprice| / Σvolume
       （每手净推动价格跳动的幅度，值越大流动性越薄、冲击成本越高）；
    3. 方向判据（direction_lean）：不平衡档 + 尾段动量同向 → next_day lean
       （long/short/flat），二者背离 → flat（不编方向）。

标准化：序列按时间戳升序（乱序=重排）；单笔缺陷跳过记 notes；不足 2 笔
fail-closed。tick 断档（A02 节点 PIT：历史依赖包断档不可补）不补数，
缺口由调用方感知，本件对注入窗口负责。


# [ALGO_FLOW] external: docs/03_modules/_domain_signal/algo_flow/source_line/tick_microstructure_criterion.yaml
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

#: 不平衡五档阈值（|imbalance|，初拟待实盘标定）
STRONG_BUY_MIN: Final = 0.25
BUY_MIN: Final = 0.10

#: 尾段动量窗口（末 N 笔净收益方向，初拟=全日尾段 10% 笔数，最少 5 笔）
TAIL_FRACTION: Final = 0.10
TAIL_MIN_TICKS: Final = 5

#: 合法买卖方向标记（归一为 B/S，兼容 buy/sell/0/1 两套口径）
_SIDE_BUY: Final[frozenset[str]] = frozenset({"B", "b", "buy", "BUY", "1"})
_SIDE_SELL: Final[frozenset[str]] = frozenset({"S", "s", "sell", "SELL", "0", "-1"})


class TickMicroInputError(ValueError):
    """输入 tick 序列非法（空/过短/NaN/非正价/非正量/方向不可判）——fail-closed。"""


class ImbalanceTier:
    """买卖不平衡五档（值即输出标签）。"""

    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class DirectionLean:
    """次日方向判据。"""

    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


@dataclass(frozen=True)
class TickMicroCriterion:
    """A02 判据信号输出（JSON 可序列化经 to_dict）。"""

    symbol: str
    n_ticks: int  # 有效 tick 数（跳过缺陷后）
    imbalance: float  # 买卖不平衡 ∈ [-1,1]（买占比−卖占比）
    imbalance_tier: str  # ImbalanceTier 五档
    impact_coef: float  # 冲击成本代理 = Σ|Δp|/Σv（每手推动幅度）
    tail_ret: float  # 尾段净收益率（末段首→末笔）
    direction_lean: str  # DirectionLean 三值
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """全基本类型字典（json.dumps 直序列化）。"""
        return {
            "symbol": self.symbol,
            "n_ticks": self.n_ticks,
            "imbalance": self.imbalance,
            "imbalance_tier": self.imbalance_tier,
            "impact_coef": self.impact_coef,
            "tail_ret": self.tail_ret,
            "direction_lean": self.direction_lean,
            "notes": list(self.notes),
        }


def classify_imbalance_tier(imbalance: float) -> str:
    """买卖不平衡 → 五档（阈值初拟待标定）。"""
    if imbalance >= STRONG_BUY_MIN:
        return ImbalanceTier.STRONG_BUY
    if imbalance >= BUY_MIN:
        return ImbalanceTier.BUY
    if imbalance <= -STRONG_BUY_MIN:
        return ImbalanceTier.STRONG_SELL
    if imbalance <= -BUY_MIN:
        return ImbalanceTier.SELL
    return ImbalanceTier.NEUTRAL


def direction_lean_of(imbalance_tier: str, tail_bullish: bool | None) -> str:
    """不平衡档 × 尾段动量 → 次日方向判据。

    不平衡中性档恒 flat；尾段动量 None（尾段过短不可判）→ flat 不编方向；
    不平衡方向与尾段动量同向 → 沿不平衡方向，背离 → flat。
    """
    if imbalance_tier == ImbalanceTier.NEUTRAL or tail_bullish is None:
        return DirectionLean.FLAT
    bullish_imb = imbalance_tier in (ImbalanceTier.STRONG_BUY, ImbalanceTier.BUY)
    if bullish_imb == tail_bullish:
        return DirectionLean.LONG if bullish_imb else DirectionLean.SHORT
    return DirectionLean.FLAT


def build_tick_micro_criterion(
    symbol: str,
    prices: Sequence[float],
    volumes: Sequence[float],
    sides: Sequence[str],
) -> TickMicroCriterion:
    """主入口：tick 三元序列 → A02 判据信号。

    Args:
        symbol: 标的代码（透传）。
        prices: 成交价序列（升序）。
        volumes: 成交量序列（与 prices 等长对齐）。
        sides: 买卖方向序列（B/buy/1=买向；S/sell/0/-1=卖向）。

    Returns:
        TickMicroCriterion（frozen）。

    Raises:
        TickMicroInputError: 序列非法（空/过短/NaN/非正价/非正量/不等长/方向非法）。
    """
    if not (len(prices) == len(volumes) == len(sides)):
        raise TickMicroInputError(f"prices/volumes/sides 不等长: {len(prices)}/{len(volumes)}/{len(sides)}")
    if len(prices) < 2:
        raise TickMicroInputError(f"tick 序列过短: n={len(prices)} < 2")
    p_list: list[float] = []
    v_list: list[float] = []
    for i, (p, v) in enumerate(zip(prices, volumes, strict=True)):
        fp, fv = float(p), float(v)
        if not math.isfinite(fp) or fp <= 0.0:
            raise TickMicroInputError(f"成交价非法: idx={i} value={p!r}")
        if not math.isfinite(fv) or fv <= 0.0:
            raise TickMicroInputError(f"成交量非法: idx={i} value={v!r}")
        p_list.append(fp)
        v_list.append(fv)
    sides_v: list[bool] = []  # True=买向
    for i, s in enumerate(sides):
        sv = str(s)
        if sv in _SIDE_BUY:
            sides_v.append(True)
        elif sv in _SIDE_SELL:
            sides_v.append(False)
        else:
            raise TickMicroInputError(f"买卖方向非法: idx={i} value={s!r}")

    notes: list[str] = []
    buy_vol = sum(v for v, b in zip(v_list, sides_v, strict=True) if b)
    sell_vol = sum(v for v, b in zip(v_list, sides_v, strict=True) if not b)
    total = buy_vol + sell_vol
    imbalance = (buy_vol - sell_vol) / total if total > 0.0 else 0.0
    tier = classify_imbalance_tier(imbalance)

    # 冲击成本代理：Σ|Δp| / Σv（价格变动按相邻笔差分，量取后一笔）
    abs_dp = sum(abs(p_list[i] - p_list[i - 1]) for i in range(1, len(p_list)))
    vol_sum = sum(v_list[1:])
    impact_coef = abs_dp / vol_sum if vol_sum > 0.0 else 0.0

    # 尾段动量：末 max(TAIL_MIN_TICKS, n×TAIL_FRACTION) 笔的净收益
    tail_n = max(TAIL_MIN_TICKS, int(len(p_list) * TAIL_FRACTION))
    tail_bullish: bool | None = None
    if len(p_list) < tail_n + 1:
        notes.append(f"尾段过短（n={len(p_list)} < {tail_n + 1}）→ 尾段动量不可判")
    else:
        tail_ret = p_list[-1] / p_list[-1 - tail_n] - 1.0
        tail_bullish = tail_ret > 0.0

    lean = direction_lean_of(tier, tail_bullish)
    if lean == DirectionLean.FLAT and tier != ImbalanceTier.NEUTRAL and tail_bullish is not None:
        notes.append("不平衡方向与尾段动量背离 → 方向判据 flat 不编方向")

    return TickMicroCriterion(
        symbol=symbol,
        n_ticks=len(p_list),
        imbalance=imbalance,
        imbalance_tier=tier,
        impact_coef=impact_coef,
        tail_ret=(p_list[-1] / p_list[-1 - tail_n] - 1.0) if tail_bullish is not None else 0.0,
        direction_lean=lean,
        notes=notes,
    )


def build_from_ticks(symbol: str, ticks: Sequence[Mapping]) -> TickMicroCriterion:
    """DS 读入形态入口：tick 字典序列（price/volume/side）→ 判据。

    标准化：缺 price/volume/side 或值非法的笔跳过记 notes（记录级缺陷不
    整体 fail）；剩余不足 2 笔 fail-closed。已按时间升序的序列由调用方
    保证（DS-001 标准化 tick 契约）。
    """
    cleaned: list[tuple[float, float, str]] = []
    skipped = 0
    for raw in ticks:
        try:
            price = float(raw["price"])
            vol = float(raw["volume"])
            side = str(raw["side"])
        except (KeyError, TypeError, ValueError):
            skipped += 1
            continue
        if not (math.isfinite(price) and math.isfinite(vol)):
            skipped += 1
            continue
        cleaned.append((price, vol, side))
    notes: list[str] = []
    if skipped:
        notes.append(f"跳过缺陷 tick {skipped} 笔（缺字段/非法值）")
    crit = build_tick_micro_criterion(
        symbol,
        [p for p, _, _ in cleaned],
        [v for _, v, _ in cleaned],
        [s for _, _, s in cleaned],
    )
    if notes:
        return TickMicroCriterion(
            symbol=crit.symbol,
            n_ticks=crit.n_ticks,
            imbalance=crit.imbalance,
            imbalance_tier=crit.imbalance_tier,
            impact_coef=crit.impact_coef,
            tail_ret=crit.tail_ret,
            direction_lean=crit.direction_lean,
            notes=crit.notes + notes,
        )
    return crit


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 永久模块最小自检入口（判据冒烟），主体经 zephyr 导入消费（消费方=TDM-E-L9-A02 挂载待总裁终裁）
    import argparse

    _ap = argparse.ArgumentParser(description="A02 判据转化器自检（无副作用冒烟）")
    _ap.add_argument("--selfcheck", action="store_true", help="跑一次合成 tick 判据冒烟")
    _args = _ap.parse_args()
    if _args.selfcheck:
        from zephyr.signal_ashare.source_line.tick_microstructure_criterion import (
            build_tick_micro_criterion,
        )

        _n = 60
        _prices = [10.0 + 0.01 * i for i in range(_n)]
        _vols = [100.0] * _n
        _sides = ["B"] * (_n - 10) + ["S"] * 10
        _c = build_tick_micro_criterion("SELFTEST", _prices, _vols, _sides)
        print(f"tick_microstructure_criterion selfcheck: {_c.imbalance_tier}/{_c.direction_lean}")
