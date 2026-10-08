# [BLUEPRINT] MOD-SIG-157 | docs/03_modules/_domain_signal/source_line_sector_rotation_criterion/blueprint.md
# [MODULE] zephyr.signal_ashare.source_line.sector_rotation_criterion
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] TDM-E-L9-A03（源线·板块/概念指数，decision_question="板块轮动与强弱持续性能否领先个股？"；module_ref 挂载=总裁终裁批，本件先按源线判据口径落码）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数核零 IO（板块指数序列由调用方注入，按日期升序）; RS 分位 ∈ [0,1] 单值输出; 输入非法 fail-closed（SectorRotationInputError）; 单板块缺陷跳过记 notes 不整体 fail; 同输入必同输出（零墙钟零随机）; 与 sector_rotation_state（市场级5状态）正交——本件输出源线级板块判据非市场态
# [MODIFY-GUARD] 地图节点 TDM-E-L9-A03（本班禁改 trading_decision_map.yaml，module_ref 挂载待总裁终裁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 基准序列非法/板块为空 → SectorRotationInputError；单板块序列过短 → 跳过该板块记 notes
# [TESTS] tests/signal_ashare/source_line/test_sector_rotation_criterion.py
# [TTL] permanent
"""SectorRotationCriterion — A03 板块/概念指数源线判据转化器（MOD-SIG-157）。

TDM-E-L9-A03「源线·板块/概念指数」的 decision_question：
    板块轮动与强弱持续性能否领先个股？

本件把板块指数日收盘序列族（DS-117 概念板块 / DS-119 概念行业，CH 表
由调用方读取注入）转化为三段判据：

    1. 板块相对强度（rs_rank_pct）：板块 N 日收益在全板块横截面的分位
       ∈ [0,1]，1=最强；
    2. 领涨持续性（streak）：板块连续跑赢基准（市场基准日收益）天数；
    3. 领先性判据（lead_signal）：RS 分位 ≥0.8 且 streak ≥3 → 板块领先
       信号（成分股跟随预期，tier=LEAD）；分位 ≥0.6 → WATCH；其余 NONE。

与既有件的正交性：sector_rotation_state（MOD-SIG-026 系）输出市场级
5 状态快照（全板块加总），本件输出源线级逐板块判据（问句=能否领先
个股），消费面与口径不同，不并。

标准化：单板块序列过短（< window+1）跳过记 notes 不整体 fail；基准
序列非法 fail-closed。指数快照落定不修订（A03 PIT 口径）。


# [ALGO_FLOW] external: docs/03_modules/_domain_signal/algo_flow/source_line/sector_rotation_criterion.yaml
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

#: 相对强度回看窗口（N 日，初拟与 sector_momentum q20 对齐待标定）
DEFAULT_WINDOW: Final = 20

#: 领先性判据阈值（初拟待标定）：RS 分位 + 持续天数双门
RS_LEAD_MIN: Final = 0.8
RS_WATCH_MIN: Final = 0.6
STREAK_LEAD_MIN: Final = 3


class SectorRotationInputError(ValueError):
    """输入非法（基准序列非法/板块族为空）——fail-closed。"""


class LeadTier:
    """板块领先性三档（值即输出标签）。"""

    LEAD = "LEAD"  # 领先：RS 高位 + 持续跑赢 → 成分股跟随预期
    WATCH = "WATCH"  # 观察：RS 中高位，持续性未达标
    NONE = "NONE"


@dataclass(frozen=True)
class BoardRotationCriterion:
    """单板块 A03 判据信号（JSON 可序列化经 to_dict）。"""

    board: str  # 板块标识（透传）
    n_days: int  # 有效交易日数
    ret_n: float  # 板块 N 日收益
    rs_rank_pct: float  # N 日收益横截面分位 ∈ [0,1]
    streak: int  # 连续跑赢基准天数
    lead_tier: str  # LeadTier 三档
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """全基本类型字典（json.dumps 直序列化）。"""
        return {
            "board": self.board,
            "n_days": self.n_days,
            "ret_n": self.ret_n,
            "rs_rank_pct": self.rs_rank_pct,
            "streak": self.streak,
            "lead_tier": self.lead_tier,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class SectorRotationSnapshot:
    """全市场板块判据快照（一次调用输出全板块）。"""

    window: int
    boards: tuple[BoardRotationCriterion, ...]
    lead_boards: tuple[str, ...]  # lead_tier=LEAD 的板块清单（按 RS 分位降序）
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """全基本类型字典（json.dumps 直序列化）。"""
        return {
            "window": self.window,
            "boards": [b.to_dict() for b in self.boards],
            "lead_boards": list(self.lead_boards),
            "notes": list(self.notes),
        }


def classify_lead_tier(rs_rank_pct: float, streak: int) -> str:
    """RS 分位 × 持续天数 → 领先性三档（阈值初拟待标定）。"""
    if rs_rank_pct >= RS_LEAD_MIN and streak >= STREAK_LEAD_MIN:
        return LeadTier.LEAD
    if rs_rank_pct >= RS_WATCH_MIN:
        return LeadTier.WATCH
    return LeadTier.NONE


def _validate_series(closes: Sequence[float], min_len: int, what: str) -> list[float]:
    """收盘序列校验：长度、有限值。"""
    if len(closes) < min_len:
        raise SectorRotationInputError(f"{what} 序列过短: n={len(closes)} < {min_len}")
    out: list[float] = []
    for i, c in enumerate(closes):
        v = float(c)
        if not math.isfinite(v) or v <= 0.0:
            raise SectorRotationInputError(f"{what} 收盘价非法: idx={i} value={c!r}")
        out.append(v)
    return out


def streak_vs_benchmark(board_closes: Sequence[float], benchmark_closes: Sequence[float]) -> int:
    """连续跑赢基准天数：从末日起逐日比对（board 日收益 > 基准日收益计 1）。

    两序列等长对齐由调用方保证（同一交易日轴）；收益差并列（相等）不续 streak。
    """
    n = min(len(board_closes), len(benchmark_closes))
    streak = 0
    for i in range(n - 1, 0, -1):
        rb = board_closes[i] / board_closes[i - 1] - 1.0
        rm = benchmark_closes[i] / benchmark_closes[i - 1] - 1.0
        if rb > rm:
            streak += 1
        else:
            break
    return streak


def build_sector_rotation_snapshot(
    board_closes: Mapping[str, Sequence[float]],
    benchmark_closes: Sequence[float],
    *,
    window: int = DEFAULT_WINDOW,
) -> SectorRotationSnapshot:
    """主入口：板块收盘序列族 + 市场基准 → 全板块 A03 判据快照。

    Args:
        board_closes: 板块标识 → 日收盘序列（升序；DS-117/DS-119 CH 表由
            调用方读取注入，指数快照落定不修订）。
        benchmark_closes: 市场基准日收盘序列（与板块同交易日轴）。
        window: 相对强度回看窗口（默认 20 日）。

    Returns:
        SectorRotationSnapshot（frozen，boards 按 RS 分位降序）。

    Raises:
        SectorRotationInputError: 基准非法/板块族为空。
    """
    _validate_series(benchmark_closes, window + 1, "基准")
    if not board_closes:
        raise SectorRotationInputError("板块族为空")

    notes: list[str] = []
    valid: dict[str, list[float]] = {}
    for board, closes in board_closes.items():
        try:
            valid[board] = _validate_series(closes, window + 1, f"板块 {board}")
        except SectorRotationInputError as e:
            notes.append(f"跳过板块 {board}: {e}")
    if not valid:
        raise SectorRotationInputError("全部板块序列过短，无可判板块")

    rets = {b: c[-1] / c[-1 - window] - 1.0 for b, c in valid.items()}
    ranked = sorted(rets, key=lambda b: rets[b])
    n = len(ranked)
    crits: list[BoardRotationCriterion] = []
    for board in ranked:
        closes = valid[board]
        rs_rank = ranked.index(board) / (n - 1) if n > 1 else 0.0
        streak = streak_vs_benchmark(closes, benchmark_closes)
        crits.append(
            BoardRotationCriterion(
                board=board,
                n_days=len(closes),
                ret_n=rets[board],
                rs_rank_pct=rs_rank,
                streak=streak,
                lead_tier=classify_lead_tier(rs_rank, streak),
            )
        )
    crits.reverse()  # RS 分位降序（最强在前）
    lead = tuple(c.board for c in crits if c.lead_tier == LeadTier.LEAD)
    return SectorRotationSnapshot(window=window, boards=tuple(crits), lead_boards=lead, notes=notes)


def build_from_index_rows(
    rows: Sequence[Mapping],
    benchmark_closes: Sequence[float],
    *,
    board_key: str = "board",
    close_key: str = "close",
    date_key: str = "date",
    window: int = DEFAULT_WINDOW,
) -> SectorRotationSnapshot:
    """DS 读入形态入口：指数行情行字典序列（board/date/close）→ 判据快照。

    标准化：按 (board, date) 分组升序重排；缺 close/date 或值非法的行跳过
    记 notes；组内不足 window+1 行的板块跳过记 notes。
    """
    grouped: dict[str, list[tuple[object, float]]] = {}
    skipped = 0
    for raw in rows:
        try:
            board = str(raw[board_key])
            dt = raw[date_key]
            close = float(raw[close_key])
        except (KeyError, TypeError, ValueError):
            skipped += 1
            continue
        if not math.isfinite(close) or close <= 0.0:
            skipped += 1
            continue
        grouped.setdefault(board, []).append((dt, close))
    serial: dict[str, list[float]] = {}
    for board, pairs in grouped.items():
        pairs.sort(key=lambda t: t[0])
        serial[board] = [c for _, c in pairs]
    snap = build_sector_rotation_snapshot(serial, benchmark_closes, window=window)
    extra: list[str] = []
    if skipped:
        extra.append(f"跳过缺陷指数行 {skipped} 行（缺字段/非法值）")
    return SectorRotationSnapshot(
        window=snap.window,
        boards=snap.boards,
        lead_boards=snap.lead_boards,
        notes=snap.notes + extra,
    )


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 永久模块最小自检入口（判据冒烟），主体经 zephyr 导入消费（消费方=TDM-E-L9-A03 挂载待总裁终裁）
    import argparse

    _ap = argparse.ArgumentParser(description="A03 判据转化器自检（无副作用冒烟）")
    _ap.add_argument("--selfcheck", action="store_true", help="跑一次合成板块判据冒烟")
    _args = _ap.parse_args()
    if _args.selfcheck:
        from zephyr.signal_ashare.source_line.sector_rotation_criterion import (
            build_sector_rotation_snapshot,
        )

        _n = 25
        _bench = [3000.0 + 2.0 * i for i in range(_n)]
        _boards = {
            "STRONG": [1000.0 * (1.0 + 0.01) ** i for i in range(_n)],
            "WEAK": [1000.0 * (1.0 - 0.005) ** i for i in range(_n)],
        }
        _s = build_sector_rotation_snapshot(_boards, _bench)
        print(f"sector_rotation_criterion selfcheck: lead={_s.lead_boards}")
