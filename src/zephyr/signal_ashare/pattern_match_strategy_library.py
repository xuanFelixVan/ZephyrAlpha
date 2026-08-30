# [BLUEPRINT] MOD-SIG-105 | docs/03_modules/_domain_signal/pattern_match_strategy_library/blueprint.md
# [MODULE] zephyr.signal_ashare.pattern_match_strategy_library
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none（纯函数核，不 import zephyr 内部件）
# [CONSUMERS] （候选：执行策略选择器装配层）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] BUY/SELL 模式封闭集 7 项；DTW 距离≥0；双门控：案例数≥min_cases 且胜率≥0.50 且 IC≥0.03；缺 IC fail-closed（ic_missing）；门语义非异常
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01416 行 + 候选注册表 CAND-TESTB-022
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知 pattern_id/空序列/非有限值/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_pattern_match_strategy_library.py
# [A_module] module_id=MOD-SIG-105 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
量化模式匹配与执行策略库（MOD-SIG-105，B10-01416，模块44）。

买卖点模式特征向量库 + DTW 历史案例匹配 + 胜率>50% 与 IC>0.03 双门控。
与 unified_pattern_engine（MOD-SIG-091 图形识别库）分工：本件管模式→执行策略
映射门控，091 管图形识别。

依据: AUD-DRAFT-001 深挖批 B10-01416（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-105
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: pattern_match_strategy_library.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PatternMatchStrategyLibrary
#   name_en: PatternMatchStrategyLibrary
#   intro: 量化模式匹配与执行策略库。
#   desc: 量化模式匹配与执行策略库。；公共方法（定义序）: list_patterns, dtw_distance, match_cases, gate_pattern；源码 L163-L255
#   inputs: config
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: PatternMatchStrategyLibrary
#   downstream: （候选：执行策略选择器装配层）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "BUY_PATTERNS",
    "SELL_PATTERNS",
    "CaseMatch",
    "HistoricalCase",
    "PatternGateResult",
    "PatternMatchConfig",
    "PatternMatchStrategyLibrary",
    "PatternSpec",
]

# ------------------------------------------------------------------
# 封闭集
# ------------------------------------------------------------------
_BUY_DEFS: Final[tuple[tuple[str, str, tuple[str, ...]], ...]] = (
    ("counter_trend_dip", "buy", ("rsi14", "volume_ratio", "depth")),
    ("breakout_volume", "buy", ("price_level", "volume_mult", "resistance_dist")),
    ("pullback_entry", "buy", ("ma_distance", "retracement_pct", "volume")),
    ("auction_weak_to_strong", "buy", ("auction_open", "first_bar", "strength")),
)
_SELL_DEFS: Final[tuple[tuple[str, str, tuple[str, ...]], ...]] = (
    ("cvd_divergence_exit", "sell", ("cvd_slope", "price_slope", "vol")),
    ("atr_stop_execution", "sell", ("atr14", "entry_price", "current_price")),
    ("thesis_invalidation_exit", "sell", ("thesis_score", "news_age", "price_dev")),
)

BUY_PATTERNS: Final[tuple[str, ...]] = tuple(d[0] for d in _BUY_DEFS)
SELL_PATTERNS: Final[tuple[str, ...]] = tuple(d[0] for d in _SELL_DEFS)


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class PatternSpec:
    """模式规格（id/方向/特征维名/语义）。"""

    pattern_id: str
    side: str  # buy or sell
    feature_dims: tuple[str, ...]


@dataclass(frozen=True)
class HistoricalCase:
    """历史案例（鸭子类型注入）。"""

    case_id: str
    series: Sequence[float]
    pattern_id: str | None = None
    forward_return: float | None = None


@dataclass(frozen=True)
class PatternMatchConfig:
    """门控配置（构造即校验）。"""

    dtw_window: float = 0.25  # Sakoe-Chiba 带宽比例
    min_win_rate: float = 0.50
    min_ic: float = 0.03
    top_k: int = 5
    min_cases: int = 2

    def __post_init__(self):
        if not (0.0 < self.dtw_window <= 1.0):
            raise ValueError("dtw_window 必须在 (0,1] 内")
        if not (0.0 < self.min_win_rate <= 1.0):
            raise ValueError("min_win_rate 必须在 (0,1] 内")
        if not (0.0 <= self.min_ic <= 1.0):
            raise ValueError("min_ic 必须在 [0,1] 内")
        if self.top_k <= 0:
            raise ValueError("top_k 必须 >0")
        if self.min_cases < 1:
            raise ValueError("min_cases 必须 ≥1")


@dataclass(frozen=True)
class CaseMatch:
    """案例匹配结果。"""

    case_id: str
    distance: float


@dataclass(frozen=True)
class PatternGateResult:
    """双门控裁定。"""

    eligible: bool
    win_rate: float | None = None
    ic: float | None = None
    matched_cases: int = 0
    reason: str = ""


# ------------------------------------------------------------------
# 实现
# ------------------------------------------------------------------
class PatternMatchStrategyLibrary:
    """量化模式匹配与执行策略库。"""

    def __init__(self, config: PatternMatchConfig | None = None) -> None:
        self.config = config or PatternMatchConfig()
        self._registry: dict[str, PatternSpec] = {}
        for pid, side, dims in (*_BUY_DEFS, *_SELL_DEFS):
            self._registry[pid] = PatternSpec(pattern_id=pid, side=side, feature_dims=dims)

    def list_patterns(self, side: str | None = None) -> tuple[PatternSpec, ...]:
        if side is None:
            return tuple(self._registry.values())
        return tuple(s for s in self._registry.values() if s.side == side)

    def dtw_distance(self, a: Sequence[float], b: Sequence[float]) -> float:
        """Sakoe-Chiba 带约束 DTW；距离=累计成本/路径长开方。"""
        if not a or not b:
            raise ValueError("DTW 输入序列不可为空")
        for v in (*a, *b):
            if not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError("DTW 输入必须全为有限数值")
        n, m = len(a), len(b)
        w = max(1, int(self.config.dtw_window * max(n, m)))
        # 滚动窗口 DP（两列）
        prev = [float("inf")] * (m + 1)
        prev[0] = 0.0
        for i in range(1, n + 1):
            curr = [float("inf")] * (m + 1)
            j_start = max(1, i - w)
            j_end = min(m, i + w)
            for j in range(j_start, j_end + 1):
                cost = (a[i - 1] - b[j - 1]) ** 2
                curr[j] = cost + min(prev[j], curr[j - 1], prev[j - 1])
            prev = curr
        d = prev[m]
        path_len = (n + m) / 2.0
        return math.sqrt(d) / math.sqrt(max(1.0, path_len))

    def match_cases(
        self,
        query: Sequence[float],
        cases: Sequence[HistoricalCase],
        top_k: int | None = None,
        pattern_id: str | None = None,
    ) -> tuple[CaseMatch, ...]:
        """DTW 匹配并升序截取 top_k。"""
        tk = top_k if top_k is not None else self.config.top_k
        if tk <= 0:
            raise ValueError("top_k 必须 >0")
        results: list[tuple[str, float]] = []
        for c in cases:
            if pattern_id is not None and getattr(c, "pattern_id", None) != pattern_id:
                continue
            d = self.dtw_distance(query, c.series)
            results.append((c.case_id, d))
        results.sort(key=lambda x: x[1])
        return tuple(CaseMatch(case_id=rid, distance=dist) for rid, dist in results[:tk])

    def gate_pattern(
        self,
        pattern_id: str,
        cases: Sequence[HistoricalCase],
        *,
        ic_value: float | None = None,
    ) -> PatternGateResult:
        if pattern_id not in self._registry:
            raise ValueError(f"未知 pattern_id: {pattern_id}")
        matched = [c for c in cases if getattr(c, "pattern_id", None) == pattern_id]
        n = len(matched)
        if n < self.config.min_cases:
            return PatternGateResult(
                eligible=False, matched_cases=n, reason=f"cases={n}<min_cases={self.config.min_cases}"
            )
        wins = sum(1 for c in matched if (getattr(c, "forward_return", 0.0) or 0.0) > 0)
        win_rate = wins / n
        if win_rate < self.config.min_win_rate:
            return PatternGateResult(
                eligible=False,
                win_rate=win_rate,
                matched_cases=n,
                reason=f"win_rate={win_rate:.2f}<min_win_rate={self.config.min_win_rate}",
            )
        if ic_value is None:
            return PatternGateResult(eligible=False, win_rate=win_rate, matched_cases=n, reason="ic_missing")
        if ic_value < self.config.min_ic:
            return PatternGateResult(
                eligible=False,
                win_rate=win_rate,
                ic=ic_value,
                matched_cases=n,
                reason=f"ic={ic_value:.4f}<min_ic={self.config.min_ic}",
            )
        return PatternGateResult(eligible=True, win_rate=win_rate, ic=ic_value, matched_cases=n, reason="ok")
