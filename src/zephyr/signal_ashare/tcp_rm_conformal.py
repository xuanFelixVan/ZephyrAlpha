# [BLUEPRINT] MOD-SIG-128 | docs/03_modules/_domain_signal/tcp_rm_conformal/blueprint.md
# [MODULE] zephyr.signal_ashare.tcp_rm_conformal
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（在线校准核纯内存；clock 注入；CP-VaR 回测序列由调用方注入）
# [CONSUMERS] 运行时装配批（CP-VaR 回测 / 在线区间预测接密度预测下游）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 区间先出后更新（无未来函数）; Robbins-Monro 步长按 1/n 衰减（第n步=step0/n）; DDCI 双向调节（欠覆盖阈值外扩收窄覆盖缺口/过宽阈值内收放宽宽度）; margin 恒 ≥ min_margin 护栏; 覆盖率统计目标 vs 实际; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/tcp_rm_conformal/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TcpRmError(占位 ZA-SIG-UNREGISTERED-TCP-RM)——非法配置（覆盖率/步长/增益/容差/护栏越界）/point或actual非有限/回测序列空或长度不符时抛
# [TESTS] tests/signal_ashare/test_tcp_rm_conformal.py
# [A_module] module_id=MOD-SIG-128 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
TcpRmConformal — TCP-RM 时序保形预测增强器（MOD-SIG-128）。

B10-01854（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-050，A1 §29.16-5）：
**Robbins-Monro 在线校准**（分位数误差反馈 q ← q + (step0/n)·(τ − 1{score≤q})，
步长按 1/n 衰减更新分位数阈值，收敛到非一致得分序列的 τ 分位数）+
**DDCI 双反馈**（累计覆盖率低于目标→阈值外扩收窄覆盖缺口；高于目标→
阈值内收放宽过宽区间，双向，min_margin 护栏兜底）+ **CP-VaR 回测**（注入
回测序列流式过在线校准，统计下轨破位率 vs 目标）+ **覆盖率统计报告**
（目标 vs 实际）。

查重分工（蓝图 §0）：conformal_predictor（MOD-SIG-044）= rolling split-
conformal 离线基线（窗口经验分位数，无在线反馈）；adaptive_conformal_
tcp_rm_ddci（MOD-SIG-052）= 加权校准批式变体（整批残差加权分位数；本件=
Robbins-Monro 随机逼近逐样本流式在线更新 + DDCI 覆盖率双反馈 + CP-VaR
回测语义，路线不同零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: tcp_rm_conformal.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: tcp_rm_conformal.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TcpRmConformal
#   name_en: TcpRmConformal
#   intro: TCP-RM 时序保形预测增强器（Robbins-Monro + DDCI 双反馈）。
#   desc: TCP-RM 时序保形预测增强器（Robbins-Monro + DDCI 双反馈）。 在线语义：update(point, actual) 先用当前阈值出区间（无未来函数），再…；公共方法（定义序）: reset,…
#   inputs: config clock
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: TcpRmConformal
#   downstream: 运行时装配批（CP-VaR 回测 / 在线区间预测接密度预测下游）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "CoverageReport",
    "CpVarBacktestReport",
    "PredictionInterval",
    "TcpRmConformal",
    "TcpRmConfig",
    "TcpRmError",
]


class TcpRmError(Exception):
    """TCP-RM 时序保形输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-TCP-RM。
    """


@dataclass(frozen=True)
class TcpRmConfig:
    """TCP-RM 配置。

    Attributes:
        target_coverage: 目标覆盖率 τ ∈ (0,1)（如 0.90 → 双侧 90% 区间）
        step0: Robbins-Monro 初始步长 γ0（第 n 步实际步长 = step0/n，1/n 衰减）
        ddci_gain: DDCI 双反馈增益（≥0；0 = 关闭 DDCI 仅 RM）
        ddci_tolerance: DDCI 触发容差（|累计覆盖率−目标| 超过才调节）
        min_margin: 分位数阈值下限护栏（≥0，防区间坍缩）
    """

    target_coverage: float = 0.90
    step0: float = 0.1
    ddci_gain: float = 0.05
    ddci_tolerance: float = 0.0
    min_margin: float = 1e-6


@dataclass(frozen=True)
class PredictionInterval:
    """单步预测区间（先出区间后更新，无未来函数）。"""

    point: float
    lower: float
    upper: float
    margin: float  # 出区间时的分位数阈值（半宽）
    target_coverage: float
    n_step: int  # 出区间前已完成的在线步数
    at: datetime.datetime
    covered: bool | None  # update 路径=实际是否落入；predict 路径=None


@dataclass(frozen=True)
class CoverageReport:
    """覆盖率统计报告（目标 vs 实际）。"""

    n: int
    n_covered: int
    n_missed: int
    target_coverage: float
    empirical_coverage: float | None  # n=0 → None
    coverage_gap: float | None  # 实际−目标（n=0 → None）
    current_margin: float
    mean_margin: float | None  # 各步出区间阈值均值（n=0 → None）
    ddci_widen_count: int
    ddci_narrow_count: int


@dataclass(frozen=True)
class CpVarBacktestReport:
    """CP-VaR 回测报告（下轨=point−margin，破位=actual<lower，VaR 口径）。"""

    n: int
    n_breaches: int
    breach_indices: tuple[int, ...]
    breach_rate: float
    target_breach_rate: float  # 1 − target_coverage
    breach_gap: float  # 实际−目标
    ran_at: datetime.datetime


class TcpRmConformal:
    """TCP-RM 时序保形预测增强器（Robbins-Monro + DDCI 双反馈）。

    在线语义：update(point, actual) 先用当前阈值出区间（无未来函数），再按
    两路反馈更新分位数阈值 margin：
      - Robbins-Monro：margin += (step0/n)·(τ − 1{score≤margin})——未覆盖
        外扩 / 覆盖微内收，步长按 1/n 衰减，收敛到得分序列 τ 分位数；
      - DDCI 双反馈：累计覆盖率 < 目标−容差 → margin += gain·(目标−实际)
        （欠覆盖外扩，收窄覆盖缺口）；> 目标+容差 → margin −= gain·(实际
        −目标)（过宽内收，放宽宽度）；下限 min_margin 护栏。
    backtest_cp_var 自当前状态续跑（回测前可 reset() 保证确定性重播）。
    """

    def __init__(
        self,
        *,
        config: TcpRmConfig | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        cfg = config or TcpRmConfig()
        if not math.isfinite(cfg.target_coverage) or not 0.0 < cfg.target_coverage < 1.0:
            raise TcpRmError(f"target_coverage 越界: {cfg.target_coverage!r}（须∈(0,1)）")
        if not math.isfinite(cfg.step0) or cfg.step0 <= 0.0:
            raise TcpRmError(f"step0 非法: {cfg.step0!r}（须为正有限值）")
        if not math.isfinite(cfg.ddci_gain) or cfg.ddci_gain < 0.0:
            raise TcpRmError(f"ddci_gain 非法: {cfg.ddci_gain!r}（须≥0 有限值）")
        if not math.isfinite(cfg.ddci_tolerance) or not 0.0 <= cfg.ddci_tolerance < 1.0:
            raise TcpRmError(f"ddci_tolerance 非法: {cfg.ddci_tolerance!r}（须∈[0,1)）")
        if not math.isfinite(cfg.min_margin) or cfg.min_margin < 0.0:
            raise TcpRmError(f"min_margin 非法: {cfg.min_margin!r}（须≥0 有限值）")
        self._cfg = cfg
        self._clock = clock or datetime.datetime.now
        self.reset()

    def reset(self) -> None:
        """清空在线状态（确定性重播起点）。"""
        self._margin = self._cfg.min_margin
        self._n = 0
        self._n_covered = 0
        self._margin_used_sum = 0.0
        self._ddci_widen = 0
        self._ddci_narrow = 0

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _finite(value: float, name: str) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            raise TcpRmError(f"{name} 不可转 float: {value!r}") from None
        if not math.isfinite(v):
            raise TcpRmError(f"{name} 非有限值: {value!r}")
        return v

    def _interval(self, point: float, covered: bool | None) -> PredictionInterval:
        m = self._margin
        return PredictionInterval(
            point=point,
            lower=point - m,
            upper=point + m,
            margin=m,
            target_coverage=self._cfg.target_coverage,
            n_step=self._n,
            at=self._clock(),
            covered=covered,
        )

    # ── 在线校准 ──────────────────────────────────────────────────────────

    def update(self, point: float, actual: float) -> PredictionInterval:
        """在线一步：先出区间（无未来函数）→ RM 步长 1/n 衰减更新 → DDCI 双反馈。"""
        p = self._finite(point, "point")
        a = self._finite(actual, "actual")
        covered = abs(a - p) <= self._margin
        out = self._interval(p, covered)
        self._margin_used_sum += self._margin

        self._n += 1
        self._n_covered += 1 if covered else 0
        # Robbins-Monro：分位数误差反馈，步长按 1/n 衰减
        step = self._cfg.step0 / self._n
        indicator = 1.0 if covered else 0.0
        self._margin += step * (self._cfg.target_coverage - indicator)

        # DDCI 双反馈（累计覆盖率 目标 vs 实际，双向）
        if self._cfg.ddci_gain > 0.0:
            empirical = self._n_covered / self._n
            gap = self._cfg.target_coverage - empirical
            if gap > self._cfg.ddci_tolerance:
                # 欠覆盖 → 阈值外扩（收窄覆盖缺口）
                self._margin += self._cfg.ddci_gain * gap
                self._ddci_widen += 1
            elif -gap > self._cfg.ddci_tolerance:
                # 过宽（超覆盖）→ 阈值内收（放宽宽度）
                self._margin -= self._cfg.ddci_gain * (-gap)
                self._ddci_narrow += 1

        if self._margin < self._cfg.min_margin:
            self._margin = self._cfg.min_margin
        return out

    def predict_interval(self, point: float) -> PredictionInterval:
        """仅按当前阈值出区间（不更新状态）。"""
        p = self._finite(point, "point")
        return self._interval(p, None)

    @property
    def current_margin(self) -> float:
        """当前分位数阈值（区间半宽）。"""
        return self._margin

    # ── CP-VaR 回测（注入回测序列） ────────────────────────────────────────

    def backtest_cp_var(
        self,
        points: Iterable[float],
        actuals: Iterable[float],
    ) -> CpVarBacktestReport:
        """CP-VaR 回测：注入历史 (point, actual) 序列流式过在线校准，统计下轨破位。

        自当前状态续跑（不回零）；破位口径 = actual < 区间下轨（损失超 VaR）。
        """
        pts = [self._finite(x, f"points[{i}]") for i, x in enumerate(points)]
        acts = [self._finite(x, f"actuals[{i}]") for i, x in enumerate(actuals)]
        if len(pts) != len(acts):
            raise TcpRmError(f"回测序列长度不符: points={len(pts)} vs actuals={len(acts)}")
        if not pts:
            raise TcpRmError("回测序列为空")
        breaches: list[int] = []
        for i, (p, a) in enumerate(zip(pts, acts, strict=True)):
            iv = self.update(p, a)
            if a < iv.lower:
                breaches.append(i)
        n = len(pts)
        rate = len(breaches) / n
        target = 1.0 - self._cfg.target_coverage
        return CpVarBacktestReport(
            n=n,
            n_breaches=len(breaches),
            breach_indices=tuple(breaches),
            breach_rate=rate,
            target_breach_rate=target,
            breach_gap=rate - target,
            ran_at=self._clock(),
        )

    # ── 覆盖率统计报告（目标 vs 实际） ─────────────────────────────────────

    def coverage_report(self) -> CoverageReport:
        """覆盖率统计：目标 vs 实际 + 阈值轨迹 + DDCI 动作计数。"""
        n = self._n
        empirical = (self._n_covered / n) if n else None
        gap = (empirical - self._cfg.target_coverage) if empirical is not None else None
        mean_margin = (self._margin_used_sum / n) if n else None
        return CoverageReport(
            n=n,
            n_covered=self._n_covered,
            n_missed=n - self._n_covered,
            target_coverage=self._cfg.target_coverage,
            empirical_coverage=empirical,
            coverage_gap=gap,
            current_margin=self._margin,
            mean_margin=mean_margin,
            ddci_widen_count=self._ddci_widen,
            ddci_narrow_count=self._ddci_narrow,
        )
