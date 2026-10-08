# [BLUEPRINT] MOD-SIG-159 | docs/03_modules/_domain_signal/source_line_capital_flow_direction_criterion/blueprint.md
# [MODULE] zephyr.signal_ashare.source_line.capital_flow_direction_criterion
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] TDM-E-L9-A06（源线·资金流，decision_question="主力/大单净流向能否预测短期方向？"；module_ref 挂载=总裁终裁批，本件先按源线判据口径落码）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数核零 IO（主力净流入/收盘序列由调用方注入，按日期升序）; conviction ∈ [-1,1] 单值输出; 输入非法 fail-closed（CapitalFlowInputError）; 单标的缺陷跳过记 notes 不整体 fail; 同输入必同输出（零墙钟零随机）; PIT=日度聚合盘后落定不修订（A06 节点 algo_note）; 与 moneyflow 落库/聚合面正交——本件输出源线级判据非数据管道
# [MODIFY-GUARD] 地图节点 TDM-E-L9-A06（本班禁改 trading_decision_map.yaml，module_ref 挂载待总裁终裁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 流水/收盘序列非法 → CapitalFlowInputError；单标的序列过短/零流动 → 跳过或 NONE 记 notes
# [TESTS] tests/signal_ashare/source_line/test_capital_flow_direction_criterion.py
# [TTL] permanent
"""CapitalFlowDirectionCriterion — A06 资金流源线判据转化器（MOD-SIG-159）。

# [ALGO_FLOW] external: docs/03_modules/_domain_signal/algo_flow/source_line/capital_flow_direction_criterion.yaml
TDM-E-L9-A06「源线·资金流」的 decision_question：
    主力/大单净流向能否预测短期方向？

本件把个股日度主力净流入序列族（DS-016，TUSHARE moneyflow 日度聚合，
CH 表由调用方读取注入）+ 同轴收盘序列转化为三段判据：

    1. 流向持续性（streak）：从末日起逐日计数连续同向（净流入>0 / 净流出<0）
       天数，零流断号；
    2. 方向信念度（conviction）：近 window 日净流累计 / 绝对流累计 ∈ [-1,1]，
       绝对值=同向一致度（对冲流互相抵消则趋 0）；
    3. 跟随判据（flow_tier）：conviction ≥+0.6 且 streak ≥3 → FOLLOW_IN
       （主力持续净流入、短期上行跟随预期）；conviction ≤-0.6 且 streak ≥3
       → FOLLOW_OUT；|conviction| ≥0.3 → WATCH；其余 NONE。
       双门设计防"单日脉冲流"误报（资金流日度噪声在案）。

价流背离注记（不改档，供消费方加权）：近 window 价格涨而 conviction
<-0.3 → 顶背离 note；价格跌而 conviction >+0.3 → 底背离 note。

与既有件的正交性：moneyflow 数据管道（采集/落库/聚合）与本件（序列 →
decision_question 判据）问句不同不并；sector_rotation（MOD-SIG-157）是
板块横截面判据，本件是个股流向判据，不并。

标准化：单标的序列过短（< window+1）跳过记 notes 不整体 fail；零流动
窗口 conviction=0 判 NONE 记 notes 不编方向；流入快照日度聚合盘后落定
不修订（A06 PIT 口径）。
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

#: 流向回看窗口（交易日，初拟与短线资金流惯性口径对齐待标定）
DEFAULT_WINDOW: Final = 10

#: 跟随判据阈值（初拟待标定）：信念度 + 持续天数双门
CONVICTION_FOLLOW_MIN: Final = 0.6
CONVICTION_WATCH_MIN: Final = 0.3
STREAK_FOLLOW_MIN: Final = 3

#: 价流背离判读阈（note 级，不改档）
DIVERGENCE_CONVICTION_MIN: Final = 0.3


class CapitalFlowInputError(ValueError):
    """输入非法（流水/收盘序列非法、标的族为空）——fail-closed。"""


class FlowTier:
    """资金流跟随性四档（值即输出标签）。"""

    FOLLOW_IN = "FOLLOW_IN"  # 持续净流入：短期上行跟随预期
    FOLLOW_OUT = "FOLLOW_OUT"  # 持续净流出：短期下行跟随预期
    WATCH = "WATCH"  # 中度同向但持续性未达标
    NONE = "NONE"


@dataclass(frozen=True)
class SymbolFlowCriterion:
    """单标的 A06 判据信号（JSON 可序列化经 to_dict）。"""

    symbol: str  # 标的标识（透传）
    n_days: int  # 有效交易日数
    conviction: float  # 近 window 净流/绝对流 ∈ [-1,1]
    streak: int  # 连续同向天数（>0 净流入 / <0 净流出）
    net_flow_window: float  # 近 window 净流累计（原单位透传）
    price_ret_window: float  # 近 window 收盘收益
    flow_tier: str  # FlowTier 四档
    divergence: str  # 背离注记："" / "TOP"(顶背离) / "BOTTOM"(底背离)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """全基本类型字典（json.dumps 直序列化）。"""
        return {
            "symbol": self.symbol,
            "n_days": self.n_days,
            "conviction": self.conviction,
            "streak": self.streak,
            "net_flow_window": self.net_flow_window,
            "price_ret_window": self.price_ret_window,
            "flow_tier": self.flow_tier,
            "divergence": self.divergence,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class CapitalFlowSnapshot:
    """全标的资金流判据快照（一次调用输出全标的）。"""

    window: int
    symbols: tuple[SymbolFlowCriterion, ...]  # 按 |conviction| 降序
    follow_in_symbols: tuple[str, ...]
    follow_out_symbols: tuple[str, ...]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """全基本类型字典（json.dumps 直序列化）。"""
        return {
            "window": self.window,
            "symbols": [s.to_dict() for s in self.symbols],
            "follow_in_symbols": list(self.follow_in_symbols),
            "follow_out_symbols": list(self.follow_out_symbols),
            "notes": list(self.notes),
        }


def classify_flow_tier(conviction: float, streak: int) -> str:
    """信念度 × 持续天数 → 跟随性四档（阈值初拟待标定）。

    streak 带符号（净流连续 +N / 净流连续 -N），判档取其长度 |streak|——
    方向语义由 conviction 符号承载，避免双处判号漂移。
    """
    if conviction >= CONVICTION_FOLLOW_MIN and abs(streak) >= STREAK_FOLLOW_MIN:
        return FlowTier.FOLLOW_IN
    if conviction <= -CONVICTION_FOLLOW_MIN and abs(streak) >= STREAK_FOLLOW_MIN:
        return FlowTier.FOLLOW_OUT
    if abs(conviction) >= CONVICTION_WATCH_MIN:
        return FlowTier.WATCH
    return FlowTier.NONE


def _validate_flows(flows: Sequence[float], min_len: int, what: str) -> list[float]:
    """净流入序列校验：长度、有限值（符号即方向，零=断号）。"""
    if len(flows) < min_len:
        raise CapitalFlowInputError(f"{what} 净流入序列过短: n={len(flows)} < {min_len}")
    out: list[float] = []
    for i, f in enumerate(flows):
        v = float(f)
        if not math.isfinite(v):
            raise CapitalFlowInputError(f"{what} 净流入非法: idx={i} value={f!r}")
        out.append(v)
    return out


def flow_streak(flows: Sequence[float]) -> int:
    """连续同向天数：从末日起逐日计数（>0 计入正流，<0 计入负流），零流断号。

    返回带符号天数：净流入连续 3 天 → +3；净流出连续 2 天 → -2；末日零流 → 0。
    """
    n = len(flows)
    if n == 0:
        return 0
    last = flows[-1]
    if last == 0.0:
        return 0
    sign = 1 if last > 0 else -1
    streak = 0
    for v in reversed(flows):
        if v == 0.0 or (v > 0) != (sign > 0):
            break
        streak += 1
    return sign * streak


def build_capital_flow_snapshot(
    flows_by_symbol: Mapping[str, Sequence[float]],
    closes_by_symbol: Mapping[str, Sequence[float]],
    *,
    window: int = DEFAULT_WINDOW,
) -> CapitalFlowSnapshot:
    """主入口：个股净流入/收盘序列族 → 全标的 A06 判据快照。

    Args:
        flows_by_symbol: 标的标识 → 日度主力净流入序列（升序，原单位透传；
            DS-016 CH 表由调用方读取注入，日度聚合盘后落定不修订）。
        closes_by_symbol: 标的标识 → 日收盘序列（与流水同交易日轴）。
        window: 流向回看窗口（默认 10 交易日）。

    Returns:
        CapitalFlowSnapshot（frozen，symbols 按 |conviction| 降序）。

    Raises:
        CapitalFlowInputError: 标的族为空/两表键不对齐。
    """
    if not flows_by_symbol:
        raise CapitalFlowInputError("标的族为空")
    missing = set(flows_by_symbol) - set(closes_by_symbol)
    if missing:
        raise CapitalFlowInputError(f"收盘表缺标的: {sorted(missing)}")

    notes: list[str] = []
    crits: list[SymbolFlowCriterion] = []
    for symbol, raw_flows in flows_by_symbol.items():
        try:
            flows = _validate_flows(raw_flows, window + 1, f"标的 {symbol}")
            raw_closes = closes_by_symbol[symbol]
            if len(raw_closes) < window + 1:
                raise CapitalFlowInputError(f"标的 {symbol} 收盘序列过短: n={len(raw_closes)} < {window + 1}")
            # 收盘序列就地校验（正+有限）——不抽独立 helper：与 sector_rotation_criterion
            # _validate_series 结构同构会吃 CloneGuard extract 级克隆硬拦（q-0009 实证）
            closes: list[float] = []
            for ci, c in enumerate(raw_closes):
                cv = float(c)
                if not math.isfinite(cv) or cv <= 0.0:
                    raise CapitalFlowInputError(f"标的 {symbol} 收盘价非法: idx={ci} value={c!r}")
                closes.append(cv)
            if len(flows) != len(closes):
                raise CapitalFlowInputError(f"标的 {symbol} 流水/收盘不等长: {len(flows)} != {len(closes)}")
        except CapitalFlowInputError as e:
            notes.append(f"跳过标的 {symbol}: {e}")
            continue
        win_f = flows[-window:]
        abs_sum = sum(abs(v) for v in win_f)
        net_sum = sum(win_f)
        conviction = net_sum / abs_sum if abs_sum > 0.0 else 0.0
        streak = flow_streak(flows)
        price_ret = closes[-1] / closes[-1 - window] - 1.0
        tier = classify_flow_tier(conviction, streak)
        divergence = ""
        sym_notes: list[str] = []
        if abs_sum == 0.0:
            sym_notes.append("窗内零流动，conviction 记 0 不编方向")
        if price_ret > 0.0 and conviction < -DIVERGENCE_CONVICTION_MIN:
            divergence = "TOP"
            sym_notes.append("顶背离：价格上行而主力净流出（note 级不改档）")
        elif price_ret < 0.0 and conviction > DIVERGENCE_CONVICTION_MIN:
            divergence = "BOTTOM"
            sym_notes.append("底背离：价格下行而主力净流入（note 级不改档）")
        crits.append(
            SymbolFlowCriterion(
                symbol=symbol,
                n_days=len(flows),
                conviction=conviction,
                streak=streak,
                net_flow_window=net_sum,
                price_ret_window=price_ret,
                flow_tier=tier,
                divergence=divergence,
                notes=sym_notes,
            )
        )
    if not crits:
        raise CapitalFlowInputError(f"全部标的序列非法，无可判标的: {'; '.join(notes)}")
    crits.sort(key=lambda c: -abs(c.conviction))
    follow_in = tuple(c.symbol for c in crits if c.flow_tier == FlowTier.FOLLOW_IN)
    follow_out = tuple(c.symbol for c in crits if c.flow_tier == FlowTier.FOLLOW_OUT)
    return CapitalFlowSnapshot(
        window=window,
        symbols=tuple(crits),
        follow_in_symbols=follow_in,
        follow_out_symbols=follow_out,
        notes=notes,
    )


def build_from_moneyflow_rows(
    rows: Sequence[Mapping],
    closes_by_symbol: Mapping[str, Sequence[float]],
    *,
    symbol_key: str = "symbol",
    flow_key: str = "net_main_amount",
    date_key: str = "trade_date",
    window: int = DEFAULT_WINDOW,
) -> CapitalFlowSnapshot:
    """DS 读入形态入口：moneyflow 行字典序列（symbol/trade_date/net_main_amount）→ 判据快照。

    标准化：按 (symbol, date) 分组升序重排；缺字段或值非法的行跳过计数；
    组内不足 window+1 行的标的跳过记 notes。
    """
    grouped: dict[str, list[tuple[object, float]]] = {}
    skipped = 0
    for raw in rows:
        try:
            symbol = str(raw[symbol_key])
            dt = raw[date_key]
            flow = float(raw[flow_key])
        except (KeyError, TypeError, ValueError):
            skipped += 1
            continue
        if not math.isfinite(flow):
            skipped += 1
            continue
        grouped.setdefault(symbol, []).append((dt, flow))
    serial: dict[str, list[float]] = {}
    for symbol, pairs in grouped.items():
        pairs.sort(key=lambda t: t[0])
        serial[symbol] = [f for _, f in pairs]
    snap = build_capital_flow_snapshot(serial, closes_by_symbol, window=window)
    extra: list[str] = []
    if skipped:
        extra.append(f"跳过缺陷 moneyflow 行 {skipped} 行（缺字段/非法值）")
    return CapitalFlowSnapshot(
        window=snap.window,
        symbols=snap.symbols,
        follow_in_symbols=snap.follow_in_symbols,
        follow_out_symbols=snap.follow_out_symbols,
        notes=snap.notes + extra,
    )


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 永久模块最小自检入口（判据冒烟），主体经 zephyr 导入消费（消费方=TDM-E-L9-A06 挂载待总裁终裁）
    import argparse

    _ap = argparse.ArgumentParser(description="A06 判据转化器自检（无副作用冒烟）")
    _ap.add_argument("--selfcheck", action="store_true", help="跑一次合成资金流判据冒烟")
    _args = _ap.parse_args()
    if _args.selfcheck:
        from zephyr.signal_ashare.source_line.capital_flow_direction_criterion import (
            build_capital_flow_snapshot,
        )

        _n = 11
        _flows = {"IN": [1.0e6 + 1.0e5 * i for i in range(_n)], "OUT": [-8.0e5 - 1.0e4 * i for i in range(_n)]}
        _closes = {k: [10.0 + 0.05 * i for i in range(_n)] for k in _flows}
        _s = build_capital_flow_snapshot(_flows, _closes)
        print(f"capital_flow_direction_criterion selfcheck: in={_s.follow_in_symbols} out={_s.follow_out_symbols}")
