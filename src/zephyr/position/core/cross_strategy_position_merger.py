# [BLUEPRINT] MOD-POS-005 | docs/03_modules/MOD-POS-005/
# [MODULE] zephyr.position.core.cross_strategy_position_merger
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D-PORTFOLIO(组合权重层) ; MOD-POS rebalance_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 组合权重=Σ子策略资金占比×账本权重(净额合并); 占比∈[0,1]且Σ≤1(余量=现金); 完全抵消标的不留占位; gross=Σ|w|/net=Σw; 合并只动权重不碰选股(三维解耦,宪章§3约束二统一框架派多子策略); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-POS-005/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidMergerInputError(ZA-POS-0022)
# [TESTS] tests/position/test_cross_strategy_position_merger.py
# [A_module] module_id=MOD-POS-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Cross Strategy Position Merger — 跨策略仓位合并器 (MOD-POS-005)

宪章 §3 约束二（统一框架派）的仓位层落点：一个策略包含多个子策略，各
子策略产出自己的目标权重簿（strategy book），本模块把它们按资金占比
合并为组合级净目标权重：

    weight(symbol) = Σ_s alloc_s · book_s.get(symbol, 0)

口径：
  - 净额合并（netting）：同标的多空意图相互抵消（A 股主方向多头，
    负权重仅作为通用口径支持，实际由上层约束）；
  - 完全抵消的标的不留 0 占位（避免下游把 0 权重误读为持仓意图）；
  - 资金占比和 <1 的余量记为现金（cash_fraction），>1 拒绝（Fail-Closed）；
  - 合并器只处理权重簿，不含任何选股/信号逻辑（三维解耦 how much 层）。

纪律：纯函数、无 IO；权重簿与资金占比由调用方注入。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidMergerInputError",
    "MergedPositionBook",
    "merge_strategy_books",
]

# 占比和的浮点容差
_ALLOC_SUM_TOL: Final = 1e-9
# 净额归零判定阈值（浮点残余）
_NET_ZERO_TOL: Final = 1e-12


class InvalidMergerInputError(ZephyrBaseError):
    """跨策略仓位合并输入非法（空簿/占比不齐/非有限值/占比超 1）。"""

    error_code = "ZA-POS-0022"


@dataclass(frozen=True)
class MergedPositionBook:
    """合并后组合级目标权重簿（frozen 不可变）。

    Attributes:
        weights: {symbol: 组合净目标权重}（净额非零标的）
        contributors: {symbol: 来源策略 id tuple}（按策略 id 排序）
        gross_exposure: 毛敞口 Σ|w|
        net_exposure: 净敞口 Σw（带符号）
        cash_fraction: 现金余量 = 1 − Σalloc（占比和<1 时）
        warnings: 合并预警（同标的多空抵消等）
    """

    weights: dict[str, float]
    contributors: dict[str, tuple[str, ...]]
    gross_exposure: float
    net_exposure: float
    cash_fraction: float
    warnings: tuple[str, ...] = field(default_factory=tuple)


def merge_strategy_books(
    books: Mapping[str, Mapping[str, float]],
    allocations: Mapping[str, float] | None = None,
) -> MergedPositionBook:
    """合并多个子策略目标权重簿为组合级净权重（纯函数）。

    Args:
        books: {strategy_id: {symbol: 目标权重}}（各簿相对自身账本归一）
        allocations: {strategy_id: 资金占比∈[0,1]}，缺省=等分 1/N；
            占比和须 ≤1（余量留现金）

    Returns:
        MergedPositionBook

    Raises:
        InvalidMergerInputError: 空簿/空账本/占比不齐/占比越界或和>1/权重非有限
    """
    if not books:
        raise InvalidMergerInputError("策略簿为空（须 ≥1 个子策略）")
    for sid, book in books.items():
        if not book:
            raise InvalidMergerInputError(f"策略 {sid} 账本为空（空仓意图须显式给 0 权重）")
        for sym, w in book.items():
            if not math.isfinite(w):
                raise InvalidMergerInputError(f"策略 {sid} 标的 {sym} 权重非有限值，got {w}")

    if allocations is None:
        share = 1.0 / len(books)
        alloc = {sid: share for sid in books}
    else:
        if set(allocations) != set(books):
            raise InvalidMergerInputError(
                f"资金占比策略集与簿不齐：allocations={sorted(allocations)} vs books={sorted(books)}"
            )
        for sid, a in allocations.items():
            if not math.isfinite(a) or a < 0.0 or a > 1.0:
                raise InvalidMergerInputError(f"策略 {sid} 资金占比非法（须 ∈[0,1]），got {a}")
        total_alloc = sum(allocations.values())
        if total_alloc > 1.0 + _ALLOC_SUM_TOL:
            raise InvalidMergerInputError(f"资金占比和 {total_alloc} > 1（超配拒绝）")
        alloc = dict(allocations)

    merged: dict[str, float] = {}
    contributors: dict[str, list[str]] = {}
    signed_by_symbol: dict[str, list[float]] = {}
    for sid in sorted(books):
        a = alloc[sid]
        for sym, w in books[sid].items():
            merged[sym] = merged.get(sym, 0.0) + a * w
            contributors.setdefault(sym, []).append(sid)
            signed_by_symbol.setdefault(sym, []).append(w)

    warnings: list[str] = []
    final: dict[str, float] = {}
    for sym in sorted(merged):
        net = merged[sym]
        signs = {1 if v > 0 else (-1 if v < 0 else 0) for v in signed_by_symbol[sym]}
        if 1 in signs and -1 in signs:
            warnings.append(f"标的 {sym} 多策略方向冲突，已净额抵消为 {net:.6f}")
        if abs(net) > _NET_ZERO_TOL:
            final[sym] = net

    gross = sum(abs(v) for v in final.values())
    net_total = sum(final.values())
    cash = max(0.0, 1.0 - sum(alloc.values()))

    return MergedPositionBook(
        weights=final,
        contributors={s: tuple(contributors[s]) for s in sorted(contributors)},
        gross_exposure=gross,
        net_exposure=net_total,
        cash_fraction=cash,
        warnings=tuple(warnings),
    )
