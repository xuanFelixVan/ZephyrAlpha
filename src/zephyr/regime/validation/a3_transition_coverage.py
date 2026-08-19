# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §0.5.7 A3 / §4.1 A3 / §5
# [MODULE] zephyr.regime.validation.a3_transition_coverage
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan A3 状态转移合理性
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯统计函数: 只消费既有 Viterbi 状态序列产物; 默认剔除自环(i→i)转移(态持续非spec转换路径); 覆盖率=落在spec路径集内的实际转移数/总转移数; 无态间转移=空集真(coverage=1.0); frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] A3CoverageError(ZA-REGIME-0031)
# [TESTS] tests/regime/validation/test_a3_transition_coverage.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: state_seq(全历史 Viterbi 解码状态序列, 既有 detector 产物, 任意可哈希标签)
# I2: allowed_paths(spec §4 定义的合法转移路径集 (from,to)) + coverage_threshold=0.80
# F1: 逐日相邻对提取(默认剔除自环) → 转移计数
# A1: compute_path_coverage(覆盖率统计 + 未覆盖路径 top 榜 + ≥80% 判定)
# O1: A3CoverageReport(total/covered/coverage/passed/top_uncovered)
# [/ALGO_FLOW]
"""D_REGIME — A3 状态转移路径覆盖正式统计（11 号 memo §0.5.7 A3 / §4.1 A3）。

纯统计函数：消费既有 Viterbi 解码状态序列（全历史或窗口段），统计实际
状态转移中落在 spec §4 定义路径集内的比例，按「spec 定义的转移路径覆盖
实际转移的 ≥80%」判定。

默认剔除自环转移（i→i 是态持续而非 spec 转换路径，计入会 trivially 抬高
覆盖率）；空集真约定：序列无任何态间转移时 coverage=1.0（无违规转移）。

依据: 11_regime_backtest_validation_plan §4.1 A3 / §5
Version: 0.1.0
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from typing import Any, Hashable, Iterable, Sequence

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class A3CoverageError(ZephyrBaseError):
    """ZA-REGIME-0031: A3 转移覆盖统计错误（输入非法）。"""

    error_code = "ZA-REGIME-0031"


@dataclass(frozen=True)
class A3UncoveredPath:
    """未覆盖转移路径——不可变。"""

    from_state: Hashable
    to_state: Hashable
    count: int  # 实际发生次数
    share: float  # 占全部转移比例


@dataclass(frozen=True)
class A3CoverageReport:
    """A3 转移路径覆盖报告——不可变。"""

    total_transitions: int  # 实际转移总数（剔除自环后）
    covered_transitions: int  # 落在 spec 路径集内的转移数
    coverage: float  # covered/total；total=0 时=1.0（空集真）
    n_distinct_paths: int  # 实际出现的不同转移路径数
    top_uncovered: tuple[A3UncoveredPath, ...]  # 未覆盖路径 top5（按次数降序）
    passed: bool  # coverage ≥ threshold（§4.1 A3=0.80）
    summary: str


def compute_path_coverage(
    state_seq: Sequence[Hashable],
    allowed_paths: Iterable[tuple[Hashable, Hashable]],
    coverage_threshold: float = 0.80,
    exclude_self: bool = True,
    top_n: int = 5,
) -> A3CoverageReport:
    """A3 主入口：实际转移的 spec 路径覆盖率统计。

    Args:
        state_seq: Viterbi 解码状态序列（任意可哈希标签，如 r1-r4/r10-r12）。
        allowed_paths: spec §4 定义的合法转移路径集 [(from, to), ...]。
        coverage_threshold: 覆盖门槛（§4.1 A3=0.80）。
        exclude_self: 是否剔除自环转移（默认 True，态持续非 spec 路径）。
        top_n: 未覆盖路径榜单长度。

    Raises:
        A3CoverageError: 序列长度<2 / allowed_paths 为空 / 门槛不在 (0,1]。
    """
    if len(state_seq) < 2:
        raise A3CoverageError(f"状态序列长度需 ≥2: {len(state_seq)}")
    allowed = set(allowed_paths)
    if not allowed:
        raise A3CoverageError("allowed_paths 不能为空")
    if not 0.0 < coverage_threshold <= 1.0:
        raise A3CoverageError(f"coverage_threshold 须在 (0,1]: {coverage_threshold}")
    if top_n < 1:
        raise A3CoverageError(f"top_n 需 ≥1: {top_n}")

    pairs: list[tuple[Hashable, Hashable]] = []
    for i in range(len(state_seq) - 1):
        a, b = state_seq[i], state_seq[i + 1]
        if exclude_self and a == b:
            continue
        pairs.append((a, b))

    total = len(pairs)
    if total == 0:
        # 空集真：无态间转移 → 无任何违反 spec 的转移
        summary = "A3 转移覆盖: 序列无态间转移（单态持续），coverage=1.0（空集真） → 通过"
        _logger.info("A3 完成: %s", summary)
        return A3CoverageReport(
            total_transitions=0,
            covered_transitions=0,
            coverage=1.0,
            n_distinct_paths=0,
            top_uncovered=(),
            passed=True,
            summary=summary,
        )

    counts: Counter[tuple[Hashable, Hashable]] = Counter(pairs)
    covered = sum(c for path, c in counts.items() if path in allowed)
    coverage = covered / total
    uncovered = sorted(
        (A3UncoveredPath(f, t, c, c / total) for (f, t), c in counts.items() if (f, t) not in allowed),
        key=lambda u: (-u.count, str(u.from_state), str(u.to_state)),
    )[:top_n]
    passed = coverage >= coverage_threshold
    summary = (
        f"A3 转移覆盖: {total} 次态间转移 / {len(counts)} 条路径, "
        f"spec 覆盖 {covered} 次 = {coverage:.2%} 门槛≥{coverage_threshold:.0%} → "
        f"{'通过' if passed else f'不通过（top未覆盖: {[(str(u.from_state), str(u.to_state), u.count) for u in uncovered]}）'}"
    )
    _logger.info("A3 完成: %s", summary)
    return A3CoverageReport(
        total_transitions=total,
        covered_transitions=covered,
        coverage=coverage,
        n_distinct_paths=len(counts),
        top_uncovered=tuple(uncovered),
        passed=passed,
        summary=summary,
    )


__all__ = [
    "A3CoverageError",
    "A3CoverageReport",
    "A3UncoveredPath",
    "compute_path_coverage",
]
