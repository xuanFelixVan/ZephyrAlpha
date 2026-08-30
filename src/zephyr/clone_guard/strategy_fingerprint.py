# [BLUEPRINT] 90_methodology_open_questions.md §20（v2.0.0 裁定 B-010）
# [MODULE] zephyr.clone_guard.strategy_fingerprint
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] numpy
# [CONSUMERS] echo-guard 退役策略相似度拦截（接线待排期，本批仅交付模块本体）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] DTW 管形状、Pearson 管方向，两者均超阈值才算相似；指纹库 append-only（退役策略只增不改）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空序列/重复 strategy_id→ValueError
# [TESTS] tests/clone_guard/test_strategy_fingerprint.py
# [A_module] module_id=MOD-CLONE_GUARD-SFP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



D_GOV_CODE_QUALITY — 退役策略指纹库（90 号 Phase2 项，#20 工程细节 B-010）

裁定真源：90_methodology_open_questions.md §20（v2.0.0）：
  三维指纹——AST 哈希（Tier1 精确复制）+ CodeSAGE 语义嵌入（Tier2，echo-guard
  已施工）+ DTW PnL 形态（Tier3，本模块补齐 Phase 2 缺口）；
  DTW 优于 Pearson：允许时间轴非线性对齐，捕获"形态相似但相位偏移"的新瓶旧酒；
  判定口径：DTW 管形状、Pearson 管方向，两者均超阈值才算相似。

注意：本模块为 90 号 Phase2 交付物，MATURITY=testing；echo-guard 拦截链路接线
挂起待 Owner（宪章 B-007 纪律）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: a 参数
#   fields: 参数 a，类型注解 np.ndarray | list[float] | tuple[float,…
#   code: strategy_fingerprint.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: b 参数
#   fields: 参数 b，类型注解 np.ndarray | list[float] | tuple[float,…
#   code: strategy_fingerprint.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① dtw_distance
#   name_en: dtw_distance
#   intro: DTW（Dynamic Time Warping）距离——PnL 形态比对（Tier3）。
#   desc: DTW（Dynamic Time Warping）距离——PnL 形态比对（Tier3）。 经典 O(n×m) DP：局部代价=绝对差，路径=min(上/左/左上) 累积。 允许…；源码 L88-L114
#   inputs: a b
#   outputs: float
# - id: A2
#   name_zh: ② StrategyFingerprintStore
#   name_en: StrategyFingerprintStore
#   intro: 退役策略指纹库（内存 MVP；持久化随 echo-guard 接线排期）。
#   desc: 退役策略指纹库（内存 MVP；持久化随 echo-guard 接线排期）。 相似判定（裁定口径）：DTW 距离 ≤ dtw_max（形状）且 Pearson ≥ pearson_…；公共方法（定义序）: add, fi…
#   inputs: dtw_max pearson_min
#   outputs: 返回值
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: echo-guard 退役策略相似度拦截（接线待排期，本批仅交付模块本体）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

_logger = logging.getLogger(__name__)

__all__ = [
    "StrategyFingerprint",
    "StrategyFingerprintStore",
    "dtw_distance",
]


def dtw_distance(
    a: np.ndarray | list[float] | tuple[float, ...], b: np.ndarray | list[float] | tuple[float, ...]
) -> float:
    """DTW（Dynamic Time Warping）距离——PnL 形态比对（Tier3）。

    经典 O(n×m) DP：局部代价=绝对差，路径=min(上/左/左上) 累积。
    允许时间轴非线性对齐（相位偏移的形态相似序列距离≈0）。

    Raises:
        ValueError: 任一序列为空
    """
    x = np.asarray(a, dtype=float).ravel()
    y = np.asarray(b, dtype=float).ravel()
    if x.size == 0 or y.size == 0:
        raise ValueError("DTW 输入序列不能为空")

    n, m = x.size, y.size
    # 滚动两行 DP（省内存；语义等价全矩阵）
    prev = np.full(m + 1, np.inf)
    prev[0] = 0.0
    for i in range(1, n + 1):
        curr = np.full(m + 1, np.inf)
        for j in range(1, m + 1):
            cost = abs(x[i - 1] - y[j - 1])
            curr[j] = cost + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return float(prev[m])


@dataclass(frozen=True)
class StrategyFingerprint:
    """退役策略三维指纹（90 号 §20 B-010）。"""

    strategy_id: str
    ast_hash: str  # Tier1 AST 哈希（精确复制）
    embedding: tuple[float, ...] | None  # Tier2 CodeSAGE 语义嵌入（可选）
    pnl_series: tuple[float, ...] | None  # Tier3 PnL 序列（DTW 形态比对；None=缺失降级）
    retired_at: str  # 退役日期（ISO）


class StrategyFingerprintStore:
    """退役策略指纹库（内存 MVP；持久化随 echo-guard 接线排期）。

    相似判定（裁定口径）：DTW 距离 ≤ dtw_max（形状）且 Pearson ≥ pearson_min
    （方向），两者同时满足才算相似。Pearson 要求等长——长度不等时截断至较短者
    （DTW 仍全序列对齐）。

    Args:
        dtw_max: DTW 形状阈值（默认 1.0，待实盘校准）
        pearson_min: Pearson 方向阈值（默认 0.9，待实盘校准）
    """

    def __init__(self, dtw_max: float = 1.0, pearson_min: float = 0.9) -> None:
        if dtw_max < 0:
            raise ValueError("dtw_max 不能为负")
        if not -1 <= pearson_min <= 1:
            raise ValueError("pearson_min 必须在 [-1,1]")
        self._dtw_max = dtw_max
        self._pearson_min = pearson_min
        self._store: dict[str, StrategyFingerprint] = {}

    def add(self, fingerprint: StrategyFingerprint) -> None:
        """登记退役策略指纹（append-only，重复 id 拒绝）。"""
        if fingerprint.strategy_id in self._store:
            raise ValueError(f"指纹已存在: {fingerprint.strategy_id}")
        self._store[fingerprint.strategy_id] = fingerprint
        _logger.info("Strategy fingerprint added: %s", fingerprint.strategy_id)

    def find_similar(self, pnl_series: tuple[float, ...]) -> list[StrategyFingerprint]:
        """按 PnL 形态检索相似退役策略（Tier3 比对）。"""
        if len(pnl_series) == 0:
            raise ValueError("查询 PnL 序列不能为空")
        matches: list[StrategyFingerprint] = []
        for fp in self._store.values():
            if fp.pnl_series is None:
                continue  # Tier3 数据缺失降级跳过
            dist = dtw_distance(np.asarray(fp.pnl_series), np.asarray(pnl_series))
            if dist > self._dtw_max:
                continue
            pearson = _pearson_min_window(fp.pnl_series, pnl_series)
            if pearson is not None and pearson < self._pearson_min:
                continue
            matches.append(fp)
        return matches

    def __len__(self) -> int:
        return len(self._store)


def _pearson_min_window(a: tuple[float, ...], b: tuple[float, ...]) -> float | None:
    """Pearson 相关（截断至较短序列；常数序列返回 None=不判方向）。"""
    k = min(len(a), len(b))
    if k < 2:
        return None
    x = np.asarray(a[:k], dtype=float)
    y = np.asarray(b[:k], dtype=float)
    if x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])
