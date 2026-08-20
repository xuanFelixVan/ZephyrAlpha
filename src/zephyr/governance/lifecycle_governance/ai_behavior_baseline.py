# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.ai_behavior_baseline
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.foundation.errors（仅错误基类；统计数据由调用方从 git_commit 会话日志/depgraph 变更记录提取）
# [CONSUMERS] 调用方（AI 会话行为审查；告警通道待 55 号定型承接，当前 interim=人工审查输出）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 基线须 ≥3 会话样本（小样本不判）; z-score 偏离 + 首次触碰未见模块 双规则; 纯统计无副作用; std=0 时偏离均值即异常
# [MODIFY-GUARD] 61_lifecycle_multi_ai.md §3.6 BM-RC-04-F
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BehaviorBaselineError(ZA-GV-0050)
# [TESTS] tests/governance/lifecycle/test_ai_behavior_baseline.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: SessionBehavior 序列（commits/duration_hours/三类文件数/modules_touched）
# F1: compute_baseline(commits_per_hour + 三类文件占比 的均值/总体标准差 + known_modules 并集)
# F2: detect_anomalies(z>|threshold| → commit_frequency/type_distribution；新模块 → first_touch_module)
# O1: BehaviorBaseline；list[BehaviorAnomaly]（空=正常）
# [/ALGO_FLOW]
"""D_GOVERNANCE — AI 会话行为基线 + 异常告警（61 号 §3.6 BM-RC-04-F，函数级 MVP）。

从 Git 提交历史/会话日志统计 AI 会话行为基线——操作频率（commits/小时）、操作类型
分布（文档 vs 代码 vs 注册表占比）、涉及模块分布；偏离基线（z-score 超阈）或首次触碰
从未涉及的模块即产出异常记录。轻量纯统计（<150 行核心），无独立监控服务；
告警通道待 55 号定型承接，当前 interim 载体=会话日志人工审查（§3.6 裁定）。

依据: 61_lifecycle_multi_ai §3.6（BM-RC-04-F Agent 行为基线 + 异常告警）
Version: 0.1.0
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from statistics import fmean, pstdev
from typing import Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

MIN_BASELINE_SESSIONS: Final[int] = 3
DEFAULT_Z_THRESHOLD: Final[float] = 3.0
_EPS: Final[float] = 1e-12


class BehaviorBaselineError(ZephyrBaseError):
    """行为基线输入非法（样本不足 / 数值非法）。"""

    error_code = "ZA-GV-0050"


@dataclass(frozen=True)
class SessionBehavior:
    """单 AI 会话行为快照（调用方从 git_commit 会话登记日志提取）。"""

    session_id: str
    commits: int
    duration_hours: float
    files_docs: int = 0
    files_code: int = 0
    files_registry: int = 0
    modules_touched: tuple[str, ...] = ()

    def commits_per_hour(self) -> float:
        return self.commits / self.duration_hours if self.duration_hours > _EPS else 0.0

    def type_ratios(self) -> tuple[float, float, float]:
        total = self.files_docs + self.files_code + self.files_registry
        if total <= 0:
            return (0.0, 0.0, 0.0)
        return (self.files_docs / total, self.files_code / total, self.files_registry / total)


@dataclass(frozen=True)
class BehaviorBaseline:
    """行为基线（均值 + 总体标准差 + 已知模块并集）。"""

    n_sessions: int
    cph_mean: float
    cph_std: float
    docs_ratio_mean: float
    docs_ratio_std: float
    code_ratio_mean: float
    code_ratio_std: float
    registry_ratio_mean: float
    registry_ratio_std: float
    known_modules: frozenset[str]


@dataclass(frozen=True)
class BehaviorAnomaly:
    """单条行为异常（z-score 偏离 / 首次触碰模块）。"""

    rule: str  # commit_frequency / type_distribution / first_touch_module
    metric: str
    detail: str
    value: float | None = None
    z_score: float | None = None


def _validate_sessions(sessions: Sequence[SessionBehavior]) -> None:
    for s in sessions:
        if s.commits < 0 or s.duration_hours < 0:
            raise BehaviorBaselineError(f"commits/duration_hours 须 >= 0: {s.session_id}")
        if min(s.files_docs, s.files_code, s.files_registry) < 0:
            raise BehaviorBaselineError(f"文件计数须 >= 0: {s.session_id}")


def compute_baseline(
    sessions: Sequence[SessionBehavior],
    *,
    min_sessions: int = MIN_BASELINE_SESSIONS,
) -> BehaviorBaseline:
    """从 ≥min_sessions 个历史会话统计行为基线（小样本不判，fail-closed）。"""
    if len(sessions) < min_sessions:
        raise BehaviorBaselineError(
            f"基线样本不足（须 >= {min_sessions}，实际 {len(sessions)}）——小样本不判"
        )
    _validate_sessions(sessions)
    cph = [s.commits_per_hour() for s in sessions]
    ratios = [s.type_ratios() for s in sessions]
    known = frozenset(m for s in sessions for m in s.modules_touched)
    cols = list(zip(*ratios))
    return BehaviorBaseline(
        n_sessions=len(sessions),
        cph_mean=fmean(cph),
        cph_std=pstdev(cph),
        docs_ratio_mean=fmean(cols[0]),
        docs_ratio_std=pstdev(cols[0]),
        code_ratio_mean=fmean(cols[1]),
        code_ratio_std=pstdev(cols[1]),
        registry_ratio_mean=fmean(cols[2]),
        registry_ratio_std=pstdev(cols[2]),
        known_modules=known,
    )


def _z(value: float, mean: float, std: float) -> float:
    """z-score；std≈0 时：等于均值 → 0，偏离均值 → ±inf（硬异常）。"""
    if std < _EPS:
        return 0.0 if abs(value - mean) < _EPS else math.copysign(math.inf, value - mean)
    return (value - mean) / std


def detect_anomalies(
    session: SessionBehavior,
    baseline: BehaviorBaseline,
    *,
    z_threshold: float = DEFAULT_Z_THRESHOLD,
) -> list[BehaviorAnomaly]:
    """对单会话做异常检测：z-score 偏离 + 首次触碰未见模块（空列表=正常）。"""
    _validate_sessions([session])
    if z_threshold <= 0:
        raise BehaviorBaselineError(f"z_threshold 须 > 0: {z_threshold}")
    anomalies: list[BehaviorAnomaly] = []

    z_cph = _z(session.commits_per_hour(), baseline.cph_mean, baseline.cph_std)
    if abs(z_cph) > z_threshold:
        anomalies.append(BehaviorAnomaly(
            rule="commit_frequency", metric="commits_per_hour",
            value=session.commits_per_hour(), z_score=z_cph,
            detail=f"commits/hour={session.commits_per_hour():.1f} 偏离基线 "
                   f"{baseline.cph_mean:.1f}±{baseline.cph_std:.1f}（z={z_cph:.1f}）",
        ))

    names = ("docs_ratio", "code_ratio", "registry_ratio")
    means = (baseline.docs_ratio_mean, baseline.code_ratio_mean, baseline.registry_ratio_mean)
    stds = (baseline.docs_ratio_std, baseline.code_ratio_std, baseline.registry_ratio_std)
    for name, value, mean, std in zip(names, session.type_ratios(), means, stds):
        z = _z(value, mean, std)
        if abs(z) > z_threshold:
            anomalies.append(BehaviorAnomaly(
                rule="type_distribution", metric=name, value=value, z_score=z,
                detail=f"{name}={value:.2f} 偏离基线 {mean:.2f}±{std:.2f}（z={z:.1f}）",
            ))

    for module in session.modules_touched:
        if module not in baseline.known_modules:
            anomalies.append(BehaviorAnomaly(
                rule="first_touch_module", metric=module,
                detail=f"首次触碰基线外模块: {module}（61 号 §3.6：首次涉及未见模块即告警）",
            ))
    if anomalies:
        logger.warning("AI 行为异常 %s: %d 条（%s）", session.session_id, len(anomalies),
                       ",".join(sorted({a.rule for a in anomalies})))
    return anomalies


__all__: Final = [
    "DEFAULT_Z_THRESHOLD",
    "MIN_BASELINE_SESSIONS",
    "BehaviorAnomaly",
    "BehaviorBaseline",
    "BehaviorBaselineError",
    "SessionBehavior",
    "compute_baseline",
    "detect_anomalies",
]
